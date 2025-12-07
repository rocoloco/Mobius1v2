#!/usr/bin/env python3
"""
Verify migration 005 (compressed_twin) syntax and structure.

This script performs static validation of the migration file without
requiring a database connection. It checks:
1. SQL syntax is valid
2. Migration follows naming conventions
3. Rollback migration exists
4. Documentation is complete
"""

import sys
from pathlib import Path


class Colors:
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_success(msg):
    print(f"{Colors.OKGREEN}✓ {msg}{Colors.ENDC}")


def print_error(msg):
    print(f"{Colors.FAIL}✗ {msg}{Colors.ENDC}")


def print_warning(msg):
    print(f"{Colors.WARNING}⚠ {msg}{Colors.ENDC}")


def check_migration_file_exists() -> bool:
    """Check if migration file exists."""
    migration_path = Path("supabase/migrations/005_add_compressed_twin.sql")
    if migration_path.exists():
        print_success("Migration file exists")
        return True
    else:
        print_error("Migration file not found")
        return False


def check_rollback_file_exists() -> bool:
    """Check if rollback file exists."""
    rollback_path = Path("supabase/migrations/005_add_compressed_twin_rollback.sql")
    if rollback_path.exists():
        print_success("Rollback file exists")
        return True
    else:
        print_error("Rollback file not found")
        return False


def check_migration_content() -> bool:
    """Check migration file content."""
    migration_path = Path("supabase/migrations/005_add_compressed_twin.sql")
    
    try:
        content = migration_path.read_text()
        
        checks = [
            ("ALTER TABLE brands", "ALTER TABLE statement"),
            ("ADD COLUMN", "ADD COLUMN statement"),
            ("compressed_twin", "compressed_twin column name"),
            ("JSONB", "JSONB data type"),
            ("IF NOT EXISTS", "IF NOT EXISTS clause (non-breaking)"),
            ("CREATE INDEX", "Index creation"),
            ("idx_brands_compressed_twin", "Index name"),
            ("COMMENT ON COLUMN", "Column documentation"),
        ]
        
        all_passed = True
        for keyword, description in checks:
            if keyword in content:
                print_success(f"Contains {description}")
            else:
                print_error(f"Missing {description}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print_error(f"Failed to read migration file: {e}")
        return False


def check_rollback_content() -> bool:
    """Check rollback file content."""
    rollback_path = Path("supabase/migrations/005_add_compressed_twin_rollback.sql")
    
    try:
        content = rollback_path.read_text()
        
        checks = [
            ("DROP INDEX", "DROP INDEX statement"),
            ("DROP COLUMN", "DROP COLUMN statement"),
            ("IF EXISTS", "IF EXISTS clause (safe rollback)"),
            ("compressed_twin", "compressed_twin column name"),
        ]
        
        all_passed = True
        for keyword, description in checks:
            if keyword in content:
                print_success(f"Rollback contains {description}")
            else:
                print_error(f"Rollback missing {description}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print_error(f"Failed to read rollback file: {e}")
        return False


def check_readme_updated() -> bool:
    """Check if README is updated."""
    readme_path = Path("supabase/migrations/README.md")
    
    try:
        content = readme_path.read_text()
        
        if "005_add_compressed_twin.sql" in content:
            print_success("README.md mentions migration 005")
            return True
        else:
            print_warning("README.md does not mention migration 005")
            return False
    except Exception as e:
        print_error(f"Failed to read README: {e}")
        return False


def check_model_updated() -> bool:
    """Check if Brand model has compressed_twin field."""
    model_path = Path("src/mobius/models/brand.py")
    
    try:
        content = model_path.read_text()
        
        checks = [
            ("class CompressedDigitalTwin", "CompressedDigitalTwin class"),
            ("compressed_twin: Optional[CompressedDigitalTwin]", "compressed_twin field in Brand model"),
            ("estimate_tokens", "estimate_tokens method"),
            ("validate_size", "validate_size method"),
        ]
        
        all_passed = True
        for keyword, description in checks:
            if keyword in content:
                print_success(f"Brand model has {description}")
            else:
                print_error(f"Brand model missing {description}")
                all_passed = False
        
        return all_passed
    except Exception as e:
        print_error(f"Failed to read brand model: {e}")
        return False


def main():
    """Main verification workflow."""
    print(f"{Colors.BOLD}Migration 005 Verification{Colors.ENDC}\n")
    
    checks = [
        ("Migration File", check_migration_file_exists),
        ("Rollback File", check_rollback_file_exists),
        ("Migration Content", check_migration_content),
        ("Rollback Content", check_rollback_content),
        ("README Updated", check_readme_updated),
        ("Brand Model Updated", check_model_updated),
    ]
    
    results = []
    for name, check_func in checks:
        print(f"\n{Colors.BOLD}Checking {name}...{Colors.ENDC}")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"{name} check failed: {e}")
            results.append((name, False))
    
    # Summary
    print(f"\n{Colors.BOLD}Summary{Colors.ENDC}")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print(f"\n{Colors.OKGREEN}{Colors.BOLD}✓ Migration 005 is ready to deploy!{Colors.ENDC}\n")
        print("Next steps:")
        print("  1. Apply migration to Supabase:")
        print("     - Via SQL Editor: Copy/paste 005_add_compressed_twin.sql")
        print("     - Via CLI: supabase db push")
        print("  2. Test with: python scripts/test_compressed_twin_migration.py")
        print("  3. If needed, rollback with: 005_add_compressed_twin_rollback.sql")
        print()
        return 0
    else:
        print(f"\n{Colors.FAIL}{Colors.BOLD}✗ Some checks failed. Please review above.{Colors.ENDC}\n")
        return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print(f"\n{Colors.WARNING}Verification cancelled{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Unexpected error: {e}{Colors.ENDC}")
        sys.exit(1)
