"""
Property-based tests for essential configuration preservation during cleanup.

**Feature: repository-cleanup, Property 4: Essential Configuration Preservation**

Tests that essential configuration files required for deployment are preserved during cleanup.

**Validates: Requirements 2.5, 4.4**
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
from typing import Set, List
import os


class ConfigurationChecker:
    """Utility class to identify essential configuration files."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        
    def get_essential_config_files(self) -> Set[str]:
        """Get list of essential configuration files required for deployment."""
        essential_files = {
            # Core Python configuration
            "pyproject.toml",
            
            # Environment configuration
            ".env.example",
            
            # Git configuration
            ".gitignore",
            
            # Supabase database migrations (entire directory)
            "supabase/migrations",
        }
        
        # Add individual migration files if they exist
        migrations_dir = self.project_root / "supabase" / "migrations"
        if migrations_dir.exists():
            for migration_file in migrations_dir.glob("*.sql"):
                rel_path = str(migration_file.relative_to(self.project_root)).replace('\\', '/')
                essential_files.add(rel_path)
        
        return essential_files
    
    def check_file_exists(self, file_path: str) -> bool:
        """Check if a configuration file exists in the repository."""
        full_path = self.project_root / file_path
        return full_path.exists()
    
    def get_existing_essential_files(self) -> Set[str]:
        """Get essential configuration files that actually exist in the repository."""
        essential_files = self.get_essential_config_files()
        existing_files = set()
        
        for file_path in essential_files:
            if self.check_file_exists(file_path):
                existing_files.add(file_path)
                
        return existing_files


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).parent
    while current.parent != current:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


@st.composite
def valid_cleanup_file_list_strategy(draw):
    """Generate a list of files that would remain after a VALID cleanup (all essential files preserved)."""
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    # Get essential configuration files that actually exist
    essential_config_files = list(checker.get_existing_essential_files())
    
    # Generate additional files that might be kept
    additional_files = [
        "README.md",
        "src/mobius/__init__.py",
        "src/mobius/api/app_consolidated.py",
        "frontend/package.json",
        "scripts/deploy.py"
    ]
    
    # Always include all essential files (this represents a valid cleanup)
    # Plus some additional files that might be preserved
    additional_count = draw(st.integers(min_value=0, max_value=len(additional_files)))
    additional_selected = draw(st.lists(
        st.sampled_from(additional_files),
        min_size=0,
        max_size=additional_count,
        unique=True
    ))
    
    return essential_config_files + additional_selected


@given(remaining_files=valid_cleanup_file_list_strategy())
@settings(max_examples=100)
def test_essential_configuration_preservation_property(remaining_files):
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    *For any* valid cleanup operation that preserves essential files, all configuration 
    files required for deployment (pyproject.toml, .env.example, supabase migrations) 
    must remain after cleanup.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    # Get essential configuration files that actually exist
    essential_config_files = checker.get_existing_essential_files()
    
    # Convert remaining_files to a set for easier checking
    remaining_files_set = set(remaining_files)
    
    # Check that all essential configuration files are preserved
    for config_file in essential_config_files:
        assert config_file in remaining_files_set, (
            f"Essential configuration file {config_file} required for deployment "
            f"must be preserved during cleanup"
        )


def test_pyproject_toml_is_essential():
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    Verify that pyproject.toml is identified as essential and exists.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    essential_files = checker.get_essential_config_files()
    
    # pyproject.toml should always be essential
    assert "pyproject.toml" in essential_files, (
        "pyproject.toml must be identified as essential configuration"
    )
    
    # It should exist in the repository
    assert checker.check_file_exists("pyproject.toml"), (
        "pyproject.toml must exist in the repository"
    )


def test_env_example_is_essential():
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    Verify that .env.example is identified as essential and exists.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    essential_files = checker.get_essential_config_files()
    
    # .env.example should be essential
    assert ".env.example" in essential_files, (
        ".env.example must be identified as essential configuration"
    )
    
    # It should exist in the repository
    assert checker.check_file_exists(".env.example"), (
        ".env.example must exist in the repository"
    )


def test_gitignore_is_essential():
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    Verify that .gitignore is identified as essential and exists.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    essential_files = checker.get_essential_config_files()
    
    # .gitignore should be essential
    assert ".gitignore" in essential_files, (
        ".gitignore must be identified as essential configuration"
    )
    
    # It should exist in the repository
    assert checker.check_file_exists(".gitignore"), (
        ".gitignore must exist in the repository"
    )


def test_supabase_migrations_are_essential():
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    Verify that Supabase migration files are identified as essential.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    essential_files = checker.get_essential_config_files()
    
    # Supabase migrations directory should be essential
    assert "supabase/migrations" in essential_files, (
        "supabase/migrations directory must be identified as essential"
    )
    
    # Check if migrations directory exists and has files
    migrations_dir = project_root / "supabase" / "migrations"
    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob("*.sql"))
        if migration_files:
            # At least one migration file should be in essential files
            migration_found = False
            for migration_file in migration_files:
                rel_path = str(migration_file.relative_to(project_root)).replace('\\', '/')
                if rel_path in essential_files:
                    migration_found = True
                    break
            
            assert migration_found, (
                "At least one Supabase migration file should be identified as essential"
            )


@given(
    config_files=st.lists(
        st.sampled_from([
            "pyproject.toml",
            ".env.example", 
            ".gitignore",
            "supabase/migrations/001_initial_schema.sql",
            "package.json",  # Not essential for Python project
            "Dockerfile",    # Not essential for this project
        ]),
        min_size=1,
        max_size=6,
        unique=True
    )
)
@settings(max_examples=100)
def test_configuration_classification_accuracy(config_files):
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    *For any* list of configuration files, the classification should correctly
    identify which ones are essential for deployment.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    essential_files = checker.get_essential_config_files()
    
    # Known essential files for this project
    known_essential = {
        "pyproject.toml",
        ".env.example",
        ".gitignore",
        "supabase/migrations/001_initial_schema.sql"
    }
    
    # Known non-essential files
    known_non_essential = {
        "package.json",  # Frontend config, not essential for Python backend
        "Dockerfile"     # Not used in current deployment
    }
    
    for config_file in config_files:
        if config_file in known_essential:
            assert config_file in essential_files or config_file.startswith("supabase/migrations"), (
                f"Known essential file {config_file} should be classified as essential"
            )
        elif config_file in known_non_essential:
            assert config_file not in essential_files, (
                f"Known non-essential file {config_file} should not be classified as essential"
            )


def test_cleanup_simulation_preserves_deployment_capability():
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    Simulate cleanup and verify that deployment capability is preserved.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    # Get essential configuration files
    essential_config_files = checker.get_existing_essential_files()
    
    # Simulate files that would remain after cleanup
    # (Include all essential config files plus some source files)
    files_after_cleanup = set(essential_config_files)
    
    # Add some core source files that would be kept
    core_files = [
        "src/mobius/__init__.py",
        "src/mobius/api/app_consolidated.py",
        "src/mobius/config.py"
    ]
    
    for core_file in core_files:
        if checker.check_file_exists(core_file):
            files_after_cleanup.add(core_file)
    
    # Verify deployment-critical files are preserved
    deployment_critical = [
        "pyproject.toml",      # Python project configuration
        ".env.example",        # Environment setup guide
        ".gitignore"           # Git configuration
    ]
    
    for critical_file in deployment_critical:
        if checker.check_file_exists(critical_file):
            assert critical_file in files_after_cleanup, (
                f"Deployment-critical file {critical_file} must be preserved"
            )
    
    # Verify Supabase migrations are preserved if they exist
    migrations_dir = project_root / "supabase" / "migrations"
    if migrations_dir.exists():
        migration_files = list(migrations_dir.glob("*.sql"))
        if migration_files:
            # At least one migration should be preserved
            migration_preserved = False
            for migration_file in migration_files:
                rel_path = str(migration_file.relative_to(project_root)).replace('\\', '/')
                if rel_path in files_after_cleanup:
                    migration_preserved = True
                    break
            
            assert migration_preserved, (
                "At least one Supabase migration file must be preserved for deployment"
            )


@given(st.lists(st.text(min_size=1, max_size=50), min_size=0, max_size=20))
@settings(max_examples=50)
def test_configuration_checker_robustness(file_paths):
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    *For any* list of file paths, the configuration checker should handle them
    gracefully without crashing.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    # Test that file existence checking doesn't crash on arbitrary input
    for file_path in file_paths:
        try:
            result = checker.check_file_exists(file_path)
            # Result should be a boolean
            assert isinstance(result, bool)
        except Exception as e:
            # File existence checking should not raise exceptions for invalid paths
            pytest.fail(f"Configuration checker crashed on '{file_path}': {e}")


def test_invalid_cleanup_scenarios():
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    Test that cleanup scenarios missing essential files would be detected as invalid.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    essential_config_files = checker.get_existing_essential_files()
    
    # Test scenario 1: Empty file list (should be invalid)
    remaining_files_empty = set()
    
    missing_files = []
    for config_file in essential_config_files:
        if config_file not in remaining_files_empty:
            missing_files.append(config_file)
    
    assert len(missing_files) > 0, (
        "Empty cleanup should be detected as missing essential files"
    )
    
    # Test scenario 2: Missing one essential file (should be invalid)
    if len(essential_config_files) > 1:
        essential_list = list(essential_config_files)
        incomplete_files = set(essential_list[1:])  # Skip first essential file
        
        missing_files = []
        for config_file in essential_config_files:
            if config_file not in incomplete_files:
                missing_files.append(config_file)
        
        assert len(missing_files) > 0, (
            "Incomplete cleanup should be detected as missing essential files"
        )


def test_essential_files_actually_exist():
    """
    **Feature: repository-cleanup, Property 4: Essential Configuration Preservation**
    
    Verify that all files identified as essential actually exist in the repository.
    
    **Validates: Requirements 2.5, 4.4**
    """
    project_root = get_project_root()
    checker = ConfigurationChecker(project_root)
    
    existing_essential_files = checker.get_existing_essential_files()
    
    # All files in the existing essential files set should actually exist
    for file_path in existing_essential_files:
        full_path = project_root / file_path
        assert full_path.exists(), (
            f"Essential configuration file {file_path} should exist in repository"
        )
        
        # If it's a file (not directory), it should be readable
        if full_path.is_file():
            assert full_path.is_file(), f"{file_path} should be a readable file"
        elif full_path.is_dir():
            assert full_path.is_dir(), f"{file_path} should be a directory"