#!/usr/bin/env python3
"""
Interactive setup script for Modal deployment.

This script helps you:
1. Install Modal CLI
2. Authenticate with Modal
3. Create Modal secrets
4. Verify configuration
"""

import subprocess
import sys
import os
from typing import Optional


class Colors:
    """ANSI color codes."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(message: str):
    """Print formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{message}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 60}{Colors.ENDC}\n")


def print_success(message: str):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {message}{Colors.ENDC}")


def print_error(message: str):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {message}{Colors.ENDC}")


def print_info(message: str):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {message}{Colors.ENDC}")


def print_warning(message: str):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {message}{Colors.ENDC}")


def run_command(command: list, check: bool = True) -> subprocess.CompletedProcess:
    """Run shell command."""
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


def check_modal_installed() -> bool:
    """Check if Modal CLI is installed."""
    try:
        result = run_command(["modal", "--version"], check=False)
        return result.returncode == 0
    except FileNotFoundError:
        return False


def install_modal():
    """Install Modal CLI."""
    print_info("Installing Modal CLI...")
    
    try:
        run_command([sys.executable, "-m", "pip", "install", "modal"])
        print_success("Modal CLI installed successfully")
        return True
    except Exception as e:
        print_error(f"Failed to install Modal CLI: {e}")
        return False


def authenticate_modal():
    """Authenticate with Modal."""
    print_info("Authenticating with Modal...")
    print_info("This will open a browser window. Follow the prompts to authenticate.")
    
    input("\nPress Enter to continue...")
    
    try:
        result = run_command(["modal", "token", "new"])
        print_success("Modal authentication successful")
        return True
    except Exception as e:
        print_error(f"Failed to authenticate: {e}")
        return False


def get_env_var(name: str, prompt: str, required: bool = True) -> Optional[str]:
    """Get environment variable with user prompt."""
    # Check if already set
    value = os.getenv(name)
    if value:
        print_info(f"{name} already set in environment")
        use_existing = input(f"Use existing value? (Y/n): ").strip().lower()
        if use_existing != 'n':
            return value
    
    # Prompt user
    while True:
        value = input(f"{prompt}: ").strip()
        
        if value:
            return value
        elif not required:
            return None
        else:
            print_warning("This field is required")


def create_modal_secrets():
    """Create Modal secrets interactively."""
    print_info("Creating Modal secrets...")
    print_info("You'll need the following API keys:")
    print("  - Fal.ai API key (get from https://fal.ai)")
    print("  - Google Gemini API key (get from https://aistudio.google.com)")
    print("  - Supabase URL (from your Supabase project)")
    print("  - Supabase anon key (from your Supabase project)")
    
    input("\nPress Enter when ready...")
    
    # Collect secrets
    fal_key = get_env_var("FAL_KEY", "Enter Fal.ai API key")
    gemini_key = get_env_var("GEMINI_API_KEY", "Enter Google Gemini API key")
    supabase_url = get_env_var("SUPABASE_URL", "Enter Supabase URL")
    supabase_key = get_env_var("SUPABASE_KEY", "Enter Supabase anon key")
    
    # Validate Supabase URL
    if supabase_url and "pooler.supabase.com" not in supabase_url and ":6543" not in supabase_url:
        print_warning("\n⚠️  Your Supabase URL doesn't appear to be a pooler URL")
        print_warning("For serverless deployments, you should use the pooler URL (port 6543)")
        print_info("Get it from: Supabase Dashboard → Settings → Database → Connection Pooling")
        
        use_anyway = input("\nContinue anyway? (y/N): ").strip().lower()
        if use_anyway != 'y':
            print_info("Please update SUPABASE_URL and try again")
            return False
    
    # Create secret
    print_info("\nCreating Modal secret 'mobius-secrets'...")
    
    try:
        command = [
            "modal", "secret", "create", "mobius-secrets",
            f"FAL_KEY={fal_key}",
            f"GEMINI_API_KEY={gemini_key}",
            f"SUPABASE_URL={supabase_url}",
            f"SUPABASE_KEY={supabase_key}",
        ]
        
        run_command(command)
        print_success("Modal secrets created successfully")
        return True
        
    except Exception as e:
        print_error(f"Failed to create secrets: {e}")
        print_info("\nYou can create secrets manually with:")
        print(f"modal secret create mobius-secrets \\")
        print(f"  FAL_KEY=your_key \\")
        print(f"  GEMINI_API_KEY=your_key \\")
        print(f"  SUPABASE_URL=your_url \\")
        print(f"  SUPABASE_KEY=your_key")
        return False


def verify_setup():
    """Verify Modal setup."""
    print_info("Verifying Modal setup...")
    
    # Check authentication
    try:
        result = run_command(["modal", "token", "list"], check=False)
        if result.returncode != 0:
            print_error("Modal authentication failed")
            return False
        print_success("Modal authentication verified")
    except Exception as e:
        print_error(f"Failed to verify authentication: {e}")
        return False
    
    # Check secrets
    try:
        result = run_command(["modal", "secret", "list"], check=False)
        if "mobius-secrets" in result.stdout:
            print_success("Modal secrets verified")
        else:
            print_warning("Modal secret 'mobius-secrets' not found")
            return False
    except Exception as e:
        print_error(f"Failed to verify secrets: {e}")
        return False
    
    return True


def main():
    """Main setup workflow."""
    print_header("Mobius Modal Setup")
    
    # Step 1: Check/Install Modal CLI
    print_header("Step 1: Modal CLI Installation")
    
    if check_modal_installed():
        print_success("Modal CLI is already installed")
    else:
        print_info("Modal CLI is not installed")
        install = input("Install Modal CLI now? (Y/n): ").strip().lower()
        
        if install != 'n':
            if not install_modal():
                print_error("Setup failed")
                sys.exit(1)
        else:
            print_info("Please install Modal CLI manually: pip install modal")
            sys.exit(0)
    
    # Step 2: Authenticate
    print_header("Step 2: Modal Authentication")
    
    try:
        result = run_command(["modal", "token", "list"], check=False)
        if result.returncode == 0:
            print_success("Already authenticated with Modal")
        else:
            if not authenticate_modal():
                print_error("Setup failed")
                sys.exit(1)
    except Exception:
        if not authenticate_modal():
            print_error("Setup failed")
            sys.exit(1)
    
    # Step 3: Create secrets
    print_header("Step 3: Modal Secrets")
    
    try:
        result = run_command(["modal", "secret", "list"], check=False)
        if "mobius-secrets" in result.stdout:
            print_success("Modal secret 'mobius-secrets' already exists")
            
            recreate = input("Recreate secrets? (y/N): ").strip().lower()
            if recreate == 'y':
                if not create_modal_secrets():
                    print_error("Setup failed")
                    sys.exit(1)
        else:
            if not create_modal_secrets():
                print_error("Setup failed")
                sys.exit(1)
    except Exception as e:
        print_error(f"Failed to check secrets: {e}")
        sys.exit(1)
    
    # Step 4: Verify
    print_header("Step 4: Verification")
    
    if not verify_setup():
        print_error("Setup verification failed")
        sys.exit(1)
    
    # Success
    print_header("Setup Complete")
    print_success("Modal is configured and ready for deployment")
    
    print_info("\nNext steps:")
    print("  1. Set up Supabase production project")
    print("  2. Run database migrations")
    print("  3. Deploy to Modal: python scripts/deploy.py")
    
    print(f"\n{Colors.OKGREEN}🚀 Ready to deploy!{Colors.ENDC}\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\n\nSetup cancelled by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {e}")
        sys.exit(1)
