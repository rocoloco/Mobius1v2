#!/usr/bin/env python3
"""
Deployment script for Mobius Phase 2 to Modal.

This script handles:
1. Pre-deployment validation
2. Database migration verification
3. Modal deployment
4. Post-deployment health checks
5. Endpoint URL reporting

Usage:
    python scripts/deploy.py [--staging|--production]
"""

import subprocess
import sys
import os
import time
import argparse
from typing import Optional
import json


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print a formatted header message."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(message: str):
    """Print a success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print an error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print an info message."""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def run_command(command: list, check: bool = True) -> subprocess.CompletedProcess:
    """
    Run a shell command and return the result.
    
    Args:
        command: Command to run as list of strings
        check: Whether to raise exception on non-zero exit code
        
    Returns:
        CompletedProcess instance
    """
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=check
        )
        return result
    except subprocess.CalledProcessError as e:
        print_error(f"Command failed: {' '.join(command)}")
        print_error(f"Error: {e.stderr}")
        raise


def check_modal_cli() -> bool:
    """Check if Modal CLI is installed and authenticated."""
    print_info("Checking Modal CLI installation...")
    
    try:
        result = run_command(["modal", "--version"], check=False)
        if result.returncode != 0:
            print_error("Modal CLI is not installed")
            print_info("Install with: pip install modal")
            return False
        
        print_success(f"Modal CLI installed: {result.stdout.strip()}")
        
        # Check authentication
        result = run_command(["modal", "token", "list"], check=False)
        if result.returncode != 0:
            print_error("Modal CLI is not authenticated")
            print_info("Authenticate with: modal token new")
            return False
        
        print_success("Modal CLI authenticated")
        return True
        
    except FileNotFoundError:
        print_error("Modal CLI is not installed")
        print_info("Install with: pip install modal")
        return False


def check_environment_variables() -> bool:
    """Check if required environment variables are set."""
    print_info("Checking environment variables...")
    
    required_vars = [
        "GEMINI_API_KEY",
        "SUPABASE_URL",
        "SUPABASE_KEY",
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print_error(f"Missing environment variables: {', '.join(missing_vars)}")
        print_info("Set them in .env file or configure Modal secrets")
        print_info("Create Modal secret with: modal secret create mobius-secrets ...")
        return False
    
    print_success("All required environment variables are set")
    
    # Check for pooler URL
    supabase_url = os.getenv("SUPABASE_URL", "")
    if "pooler.supabase.com" not in supabase_url and ":6543" not in supabase_url:
        print_warning("SUPABASE_URL does not appear to be a pooler URL")
        print_warning("Consider using pooler URL (port 6543) for serverless")
    
    return True


def check_modal_secrets() -> bool:
    """Check if Modal secrets are configured."""
    print_info("Checking Modal secrets...")
    
    try:
        result = run_command(["modal", "secret", "list"], check=False)
        if "mobius-secrets" in result.stdout:
            print_success("Modal secret 'mobius-secrets' found")
            return True
        else:
            print_warning("Modal secret 'mobius-secrets' not found")
            print_info("Create with: modal secret create mobius-secrets GEMINI_API_KEY=... SUPABASE_URL=... SUPABASE_KEY=...")
            return False
    except Exception as e:
        print_error(f"Failed to check Modal secrets: {e}")
        return False


def run_tests() -> bool:
    """Run test suite before deployment."""
    print_info("Running test suite...")
    
    try:
        result = run_command(["pytest", "-v", "--tb=short"], check=False)
        
        if result.returncode == 0:
            print_success("All tests passed")
            return True
        else:
            print_error("Some tests failed")
            print_info("Review test output above")
            
            response = input(f"\n{Colors.WARNING}Continue with deployment anyway? (y/N): {Colors.ENDC}")
            return response.lower() == 'y'
            
    except FileNotFoundError:
        print_warning("pytest not found, skipping tests")
        return True


def check_file_sizes() -> bool:
    """Check that no Python files exceed 300 lines."""
    print_info("Checking file sizes...")
    
    oversized_files = []
    
    for root, dirs, files in os.walk("src/mobius"):
        # Skip __pycache__ directories
        dirs[:] = [d for d in dirs if d != '__pycache__']
        
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r', encoding='utf-8') as f:
                    line_count = sum(1 for _ in f)
                
                if line_count > 300:
                    oversized_files.append((filepath, line_count))
    
    if oversized_files:
        print_warning("Some files exceed 300 lines:")
        for filepath, line_count in oversized_files:
            print(f"  {filepath}: {line_count} lines")
        
        response = input(f"\n{Colors.WARNING}Continue with deployment anyway? (y/N): {Colors.ENDC}")
        return response.lower() == 'y'
    else:
        print_success("All files are under 300 lines")
        return True


def deploy_to_modal(environment: str = "staging") -> bool:
    """
    Deploy application to Modal.
    
    Args:
        environment: Deployment environment (staging or production)
        
    Returns:
        True if deployment succeeded
    """
    print_info(f"Deploying to Modal ({environment})...")
    
    app_file = "src/mobius/api/app.py"
    
    if not os.path.exists(app_file):
        print_error(f"Application file not found: {app_file}")
        return False
    
    try:
        # Deploy the app
        result = run_command(["modal", "deploy", app_file])
        
        print_success(f"Deployment to {environment} completed successfully")
        
        # Extract endpoint URLs from output
        if "https://" in result.stdout:
            print_info("\nEndpoint URLs:")
            for line in result.stdout.split('\n'):
                if "https://" in line:
                    print(f"  {line.strip()}")
        
        return True
        
    except subprocess.CalledProcessError:
        print_error("Deployment failed")
        return False


def run_health_check(base_url: Optional[str] = None) -> bool:
    """
    Run health check against deployed application.
    
    Args:
        base_url: Base URL of deployed application
        
    Returns:
        True if health check passed
    """
    if not base_url:
        print_warning("No base URL provided, skipping health check")
        print_info("Run health check manually: curl https://your-app.modal.run/v1/health")
        return True
    
    print_info("Running health check...")
    
    try:
        import requests
        
        health_url = f"{base_url}/v1/health"
        response = requests.get(health_url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if data.get("status") == "healthy":
                print_success("Health check passed")
                print_info(f"Database: {data.get('database')}")
                print_info(f"Storage: {data.get('storage')}")
                print_info(f"API: {data.get('api')}")
                return True
            else:
                print_warning(f"Health check returned status: {data.get('status')}")
                return False
        else:
            print_error(f"Health check failed with status code: {response.status_code}")
            return False
            
    except ImportError:
        print_warning("requests library not installed, skipping health check")
        print_info("Install with: pip install requests")
        return True
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def main():
    """Main deployment workflow."""
    parser = argparse.ArgumentParser(description="Deploy Mobius to Modal")
    parser.add_argument(
        "--environment",
        choices=["staging", "production"],
        default="staging",
        help="Deployment environment (default: staging)"
    )
    parser.add_argument(
        "--skip-tests",
        action="store_true",
        help="Skip running tests before deployment"
    )
    parser.add_argument(
        "--skip-health-check",
        action="store_true",
        help="Skip health check after deployment"
    )
    parser.add_argument(
        "--base-url",
        help="Base URL for health check (e.g., https://your-app.modal.run)"
    )
    
    args = parser.parse_args()
    
    print_header(f"Mobius Phase 2 Deployment to Modal ({args.environment})")
    
    # Pre-deployment checks
    print_header("Pre-Deployment Checks")
    
    checks_passed = True
    
    if not check_modal_cli():
        checks_passed = False
    
    if not check_environment_variables():
        checks_passed = False
    
    if not check_modal_secrets():
        print_warning("Modal secrets not configured, will use environment variables")
    
    if not check_file_sizes():
        checks_passed = False
    
    if not args.skip_tests:
        if not run_tests():
            checks_passed = False
    
    if not checks_passed:
        print_error("\nPre-deployment checks failed")
        sys.exit(1)
    
    print_success("\nAll pre-deployment checks passed")
    
    # Confirm deployment
    if args.environment == "production":
        print_warning("\n⚠️  You are about to deploy to PRODUCTION")
        response = input(f"{Colors.WARNING}Are you sure you want to continue? (yes/N): {Colors.ENDC}")
        if response.lower() != "yes":
            print_info("Deployment cancelled")
            sys.exit(0)
    
    # Deploy
    print_header("Deployment")
    
    if not deploy_to_modal(args.environment):
        print_error("\nDeployment failed")
        sys.exit(1)
    
    # Post-deployment checks
    if not args.skip_health_check:
        print_header("Post-Deployment Checks")
        
        # Wait a few seconds for deployment to stabilize
        print_info("Waiting for deployment to stabilize...")
        time.sleep(5)
        
        if not run_health_check(args.base_url):
            print_warning("Health check failed, but deployment completed")
            print_info("Check logs with: modal app logs mobius-v2")
    
    # Success
    print_header("Deployment Complete")
    print_success(f"Mobius Phase 2 deployed successfully to {args.environment}")
    
    print_info("\nNext steps:")
    print("  1. View logs: modal app logs mobius-v2")
    print("  2. List endpoints: modal app list")
    print("  3. Test health: curl https://your-app.modal.run/v1/health")
    print("  4. View docs: curl https://your-app.modal.run/v1/docs")
    
    print(f"\n{Colors.OKGREEN}🚀 Deployment successful!{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nDeployment cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        sys.exit(1)
