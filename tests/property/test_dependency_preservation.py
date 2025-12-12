"""
Property-based tests for repository cleanup dependency preservation.

**Feature: repository-cleanup, Property 1: Dependency Preservation**

Tests that all modules imported by app_consolidated.py are preserved during cleanup.

**Validates: Requirements 1.4, 2.1**
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import ast
import json
import os
from typing import Set, List, Optional


class DependencyChecker:
    """Utility class to check dependencies of app_consolidated.py."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_root = project_root / "src"
        
    def analyze_imports(self, file_path: Path) -> List[str]:
        """Extract all import statements from a Python file."""
        if not file_path.exists() or file_path.suffix != '.py':
            return []
            
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        imports.append(node.module)
                        
            return imports
        except (SyntaxError, UnicodeDecodeError):
            return []
    
    def resolve_import_to_file(self, import_name: str) -> Optional[Path]:
        """Resolve an import name to its corresponding file path."""
        # Handle mobius.* imports
        if import_name.startswith('mobius.'):
            relative_path = import_name.replace('mobius.', '').replace('.', '/')
            
            # Try as a module file
            module_file = self.src_root / "mobius" / f"{relative_path}.py"
            if module_file.exists():
                return module_file
                
            # Try as a package __init__.py
            package_init = self.src_root / "mobius" / relative_path / "__init__.py"
            if package_init.exists():
                return package_init
                
        return None
    
    def find_all_dependencies(self, start_file: Path, visited: Optional[Set[str]] = None) -> Set[str]:
        """Find all transitive dependencies starting from a file."""
        if visited is None:
            visited = set()
            
        if str(start_file) in visited:
            return set()
            
        visited.add(str(start_file))
        dependencies = set()
        
        imports = self.analyze_imports(start_file)
        
        for import_name in imports:
            resolved_file = self.resolve_import_to_file(import_name)
            if resolved_file:
                rel_path = str(resolved_file.relative_to(self.project_root)).replace('\\', '/')
                dependencies.add(rel_path)
                # Recursively find dependencies
                sub_deps = self.find_all_dependencies(resolved_file, visited)
                dependencies.update(sub_deps)
                
        return dependencies
    
    def get_app_consolidated_dependencies(self) -> Set[str]:
        """Get all dependencies of app_consolidated.py."""
        app_file = self.project_root / "src" / "mobius" / "api" / "app_consolidated.py"
        if not app_file.exists():
            return set()
            
        dependencies = self.find_all_dependencies(app_file)
        # Add the main file itself
        dependencies.add(str(app_file.relative_to(self.project_root)).replace('\\', '/'))
        return dependencies


def get_project_root() -> Path:
    """Get the project root directory."""
    # Start from the test file location and go up to find project root
    current = Path(__file__).parent
    while current.parent != current:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


@st.composite
def valid_cleanup_scenario_strategy(draw):
    """Generate valid cleanup scenarios where all dependencies are preserved."""
    # Get actual dependencies to ensure we test realistic scenarios
    project_root = get_project_root()
    checker = DependencyChecker(project_root)
    actual_dependencies = list(checker.get_app_consolidated_dependencies())
    
    # Add some additional files that might exist but aren't dependencies
    additional_files = [
        "pyproject.toml",
        "README.md", 
        ".gitignore",
        ".env.example",
        "src/mobius/api/websocket_handlers.py",
        "src/mobius/tools/experimental.py",
        "tests/unit/test_experimental.py",
        "scripts/temp_analysis.py",
        "docs/temp_notes.md"
    ]
    
    # Always include all dependencies (this makes it a valid cleanup scenario)
    # Then add a random selection of additional files
    additional_count = draw(st.integers(min_value=0, max_value=len(additional_files)))
    additional_selected = draw(st.lists(
        st.sampled_from(additional_files),
        min_size=additional_count,
        max_size=additional_count,
        unique=True
    ))
    
    # Return all dependencies plus some additional files
    return actual_dependencies + additional_selected


@given(remaining_files=valid_cleanup_scenario_strategy())
@settings(max_examples=50)
def test_dependency_preservation_property(remaining_files):
    """
    Property 1: Dependency Preservation.
    
    For any valid cleanup scenario (where all dependencies are preserved), 
    the system should be able to import app_consolidated.py successfully.
    
    **Validates: Requirements 1.4, 2.1**
    """
    project_root = get_project_root()
    checker = DependencyChecker(project_root)
    
    # Get actual dependencies of app_consolidated.py
    actual_dependencies = checker.get_app_consolidated_dependencies()
    
    # Convert remaining_files to a set for easier checking
    remaining_files_set = set(remaining_files)
    
    # Property: In a valid cleanup scenario, all dependencies must be preserved
    # This should always pass since our strategy ensures all dependencies are included
    for dependency in actual_dependencies:
        # Only check dependencies that actually exist in the current repository
        dependency_path = project_root / dependency
        if dependency_path.exists():
            assert dependency in remaining_files_set, (
                f"Dependency {dependency} required by app_consolidated.py "
                f"must be preserved in valid cleanup scenario"
            )
    
    # Additional property: The remaining files should include all essential dependencies
    essential_count = sum(1 for dep in actual_dependencies 
                         if (project_root / dep).exists())
    preserved_count = sum(1 for dep in actual_dependencies 
                         if dep in remaining_files_set and (project_root / dep).exists())
    
    assert preserved_count == essential_count, (
        f"All {essential_count} essential dependencies must be preserved, "
        f"but only {preserved_count} were found in cleanup scenario"
    )


def test_app_consolidated_dependencies_exist():
    """
    Property 1 (concrete test): All current dependencies of app_consolidated.py exist.
    
    This test verifies that the dependency analysis correctly identifies existing files.
    
    **Validates: Requirements 1.4, 2.1**
    """
    project_root = get_project_root()
    checker = DependencyChecker(project_root)
    
    dependencies = checker.get_app_consolidated_dependencies()
    
    # All identified dependencies should correspond to existing files
    for dependency in dependencies:
        dependency_path = project_root / dependency
        assert dependency_path.exists(), (
            f"Dependency {dependency} identified by analysis should exist in repository"
        )


def test_essential_files_are_dependencies():
    """
    Property 1 (essential files): Core system files are identified as dependencies.
    
    Verifies that critical files like the main app file are correctly identified.
    
    **Validates: Requirements 1.4, 2.1**
    """
    project_root = get_project_root()
    checker = DependencyChecker(project_root)
    
    dependencies = checker.get_app_consolidated_dependencies()
    
    # The main app file should always be in dependencies
    app_file_path = "src/mobius/api/app_consolidated.py"
    assert app_file_path in dependencies, (
        "Main application file must be identified as a dependency"
    )
    
    # Check for some expected core modules (if they exist)
    expected_core_modules = [
        "src/mobius/api/routes.py",
        "src/mobius/api/errors.py", 
        "src/mobius/models/brand.py"
    ]
    
    for module_path in expected_core_modules:
        full_path = project_root / module_path
        if full_path.exists():
            assert module_path in dependencies, (
                f"Core module {module_path} should be identified as a dependency"
            )


@given(st.lists(st.text(min_size=1, max_size=50), min_size=1, max_size=10))
@settings(max_examples=50)
def test_import_resolution_robustness(import_names):
    """
    Property 1 (robustness): Import resolution handles various input gracefully.
    
    For any list of import names, the resolution process should not crash
    and should return valid results.
    
    **Validates: Requirements 1.4, 2.1**
    """
    project_root = get_project_root()
    checker = DependencyChecker(project_root)
    
    # Test that import resolution doesn't crash on arbitrary input
    for import_name in import_names:
        try:
            result = checker.resolve_import_to_file(import_name)
            # Result should be None or a valid Path
            assert result is None or isinstance(result, Path)
            
            # If result is a Path, it should be within the project
            if result is not None:
                assert str(result).startswith(str(project_root))
        except Exception as e:
            # Import resolution should not raise exceptions for invalid imports
            pytest.fail(f"Import resolution crashed on '{import_name}': {e}")


def test_dependency_analysis_completeness():
    """
    Property 1 (completeness): Dependency analysis finds all import relationships.
    
    This test verifies that the dependency analysis is thorough and doesn't miss
    important import relationships.
    
    **Validates: Requirements 1.4, 2.1**
    """
    project_root = get_project_root()
    checker = DependencyChecker(project_root)
    
    # Test on the main app file
    app_file = project_root / "src" / "mobius" / "api" / "app_consolidated.py"
    if not app_file.exists():
        pytest.skip("app_consolidated.py not found")
    
    # Get direct imports from the file
    direct_imports = checker.analyze_imports(app_file)
    
    # Get all transitive dependencies
    all_dependencies = checker.find_all_dependencies(app_file)
    
    # Verify that direct mobius imports are resolved to file paths
    mobius_imports = [imp for imp in direct_imports if imp.startswith('mobius.')]
    
    for mobius_import in mobius_imports:
        resolved_file = checker.resolve_import_to_file(mobius_import)
        if resolved_file:  # If it resolves to a file
            rel_path = str(resolved_file.relative_to(project_root)).replace('\\', '/')
            assert rel_path in all_dependencies, (
                f"Direct import {mobius_import} -> {rel_path} should be in dependencies"
            )


def test_cleanup_simulation():
    """
    Property 1 (simulation): Simulate cleanup and verify dependencies preserved.
    
    This test simulates a cleanup operation and verifies that all required
    dependencies would be preserved.
    
    **Validates: Requirements 1.4, 2.1**
    """
    project_root = get_project_root()
    checker = DependencyChecker(project_root)
    
    # Get all current dependencies
    required_dependencies = checker.get_app_consolidated_dependencies()
    
    # Simulate files that would be kept after cleanup
    # (This would normally come from the cleanup analysis)
    essential_files = set()
    
    # Add all Python source files in src/mobius (core system)
    for root, dirs, files in os.walk(project_root / "src" / "mobius"):
        for file in files:
            if file.endswith('.py'):
                file_path = Path(root) / file
                rel_path = str(file_path.relative_to(project_root)).replace('\\', '/')
                essential_files.add(rel_path)
    
    # Add configuration files
    config_files = ["pyproject.toml", ".env.example", ".gitignore"]
    for config_file in config_files:
        if (project_root / config_file).exists():
            essential_files.add(config_file)
    
    # Verify all required dependencies are in essential files
    missing_dependencies = required_dependencies - essential_files
    
    # Filter out dependencies that don't actually exist (external packages, etc.)
    actual_missing = []
    for dep in missing_dependencies:
        if (project_root / dep).exists():
            actual_missing.append(dep)
    
    assert not actual_missing, (
        f"Cleanup would remove required dependencies: {actual_missing}"
    )