#!/usr/bin/env python3
"""
Pre-deployment verification script.

Checks that everything is ready for deployment:
- Tests passing
- Environment configured
- Modal setup complete
- Supabase ready
"""

import subprocess
import sys
import os
from typing import List, Tuple


class Colors:
    HEADER = '\033[95m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_check(name: str, passed: bool, details: str = ""):
    status = f"{Colors.OKGREEN}✓ PASS{Colors.ENDC}" if passed else f"{Colors.FAIL}✗ FAIL{Colors.ENDC}"
    print(f"{status} - {name}")
    if details:
        print(f"       {details}")


def run_command(command: List[str]) -> Tuple[bool, str]:
    """Run command and return (success, output)."""
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False
        )
        return result.returncode == 0, result.stdout + result.stderr
    except FileNotFoundError:
        return False, "Command not found"


def check_python_version() -> bool:
    """Check Python version >= 3.11."""
    version = sys.version_info
    return version.major == 3 and version.minor >= 11


def check_dependencies() -> bool:
    """Check required packages are installed."""
    required = [
        "modal",
        "langgraph",
        "pydantic",
        "supabase",
        "google.generativeai",
        "pdfplumber",
        "httpx",
        "structlog",
        "tenacity",
        "hypothesis",
        "pytest",
    ]
    
    missing = []
    for package in required:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"       Missing: {', '.join(missing)}")
        return False
    return True


def check_modal_cli() -> bool:
    """Check Modal CLI installed and authenticated."""
    success, _ = run_command(["modal", "--version"])
    if not success:
        print("       Modal CLI not installed")
        return False
    
    success, _ = run_command(["modal", "token", "list"])
    if not success:
        print("       Modal not authenticated")
        return False
    
    return True


def check_modal_secrets() -> bool:
    """Check Modal secrets configured."""
    success, output = run_command(["modal", "secret", "list"])
    if not success:
        return False
    
    if "mobius-secrets" not in output:
        print("       Secret 'mobius-secrets' not found")
        return False
    
    return True


def check_env_vars() -> bool:
    """Check required environment variables."""
    required = ["FAL_KEY", "GEMINI_API_KEY", "SUPABASE_URL", "SUPABASE_KEY"]
    missing = [var for var in required if not os.getenv(var)]
    
    if missing:
        print(f"       Missing: {', '.join(missing)}")
        print("       (OK if using Modal secrets)")
        return True  # Not critical if using Modal secrets
    
    return True


def check_supabase_url() -> bool:
    """Check Supabase URL is pooler URL."""
    url = os.getenv("SUPABASE_URL", "")
    if not url:
        print("       SUPABASE_URL not set")
        return False
    
    if "pooler.supabase.com" not in url and ":6543" not in url:
        print("       Warning: Not using pooler URL (port 6543)")
        print("       Recommended for serverless deployments")
        return True  # Warning, not failure
    
    return True


def check_tests() -> bool:
    """Check tests pass."""
    print("       Running tests (this may take a minute)...")
    success, output = run_command(["pytest", "-v", "--tb=short", "-x"])
    
    if not success:
        print("       Some tests failed")
        # Show last few lines of output
        lines = output.split('\n')
        for line in lines[-10:]:
            if line.strip():
                print(f"       {line}")
        return False
    
    return True


def check_file_structure() -> bool:
    """Check required files exist."""
    required_files = [
        "src/mobius/api/app.py",
        "src/mobius/config.py",
        "pyproject.toml",
        "supabase/migrations/001_initial_schema.sql",
        "supabase/migrations/002_add_templates.sql",
        "supabase/migrations/003_add_feedback.sql",
        "supabase/migrations/004_learning_privacy.sql",
    ]
    
    missing = [f for f in required_files if not os.path.exists(f)]
    
    if missing:
        print(f"       Missing files:")
        for f in missing:
            print(f"         - {f}")
        return False
    
    return True


def check_file_sizes() -> bool:
    """Check no files exceed 300 lines."""
    oversized = []
    
    for root, dirs, files in os.walk("src/mobius"):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                if line_count > 300:
                    oversized.append((filepath, line_count))
    
    if oversized:
        print("       Files exceeding 300 lines:")
        for filepath, count in oversized:
            print(f"         - {filepath}: {count} lines")
        return False
    
    return True


def main():
    """Run all checks."""
    print_header("Mobius Pre-Deployment Verification")
    
    checks = [
        ("Python Version (>= 3.11)", check_python_version),
        ("Required Dependencies", check_dependencies),
        ("File Structure", check_file_structure),
        ("File Size Limits", check_file_sizes),
        ("Modal CLI", check_modal_cli),
        ("Modal Secrets", check_modal_secrets),
        ("Environment Variables", check_env_vars),
        ("Supabase URL", check_supabase_url),
        ("Test Suite", check_tests),
    ]
    
    results = []
    
    for name, check_func in checks:
        try:
            passed = check_func()
            results.append((name, passed))
            print_check(name, passed)
        except Exception as e:
            results.append((name, False))
            print_check(name, False, f"Error: {e}")
    
    # Summary
    print_header("Summary")
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    print(f"Checks passed: {passed_count}/{total_count}")
    
    if passed_count == total_count:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ All checks passed! Ready to deploy.{Colors.ENDC}\n")
        print("Deploy with: python scripts/deploy.py")
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Some checks failed. Please fix issues before deploying.{Colors.ENDC}\n")
        
        failed = [name for name, passed in results if not passed]
        print("Failed checks:")
        for name in failed:
            print(f"  - {name}")
        
        print("\nRefer to:")
        print("  - docs/DEPLOYMENT-GUIDE.md for setup instructions")
        print("  - docs/DEPLOYMENT-CHECKLIST.md for checklist")
        
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Verification cancelled{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        sys.exit(1)
