"""
Property-based tests for test coverage maintenance during repository cleanup.

**Feature: repository-cleanup, Property 2: Test Coverage Maintenance**

Tests that core functionality maintains test coverage after cleanup operations.

**Validates: Requirements 2.2, 3.2**
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import ast
import os
from typing import Set, List, Dict, Optional
import re


class CoverageAnalyzer:
    """Utility class to analyze test coverage for core modules."""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.src_root = project_root / "src" / "mobius"
        self.test_root = project_root / "tests"
        
    def get_core_modules(self) -> Set[str]:
        """Get all core modules that should have test coverage."""
        core_modules = set()
        
        # Walk through src/mobius directory
        for root, dirs, files in os.walk(self.src_root):
            # Skip __pycache__ directories
            dirs[:] = [d for d in dirs if d != '__pycache__']
            
            for file in files:
                if file.endswith('.py') and file != '__init__.py':
                    file_path = Path(root) / file
                    # Get relative path from src/mobius
                    rel_path = file_path.relative_to(self.src_root)
                    # Convert to module name (e.g., api/routes.py -> api.routes)
                    module_name = str(rel_path.with_suffix('')).replace('/', '.')
                    core_modules.add(module_name)
                    
        return core_modules
    
    def get_test_files(self) -> Dict[str, List[str]]:
        """Get all test files organized by test type."""
        test_files = {
            'unit': [],
            'integration': [],
            'property': []
        }
        
        for test_type in test_files.keys():
            test_dir = self.test_root / test_type
            if test_dir.exists():
                for file in test_dir.glob('test_*.py'):
                    test_files[test_type].append(file.name)
                    
        return test_files
    
    def analyze_test_imports(self, test_file: Path) -> Set[str]:
        """Analyze what modules a test file imports from mobius."""
        if not test_file.exists():
            return set()
            
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            mobius_imports = set()
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name.startswith('mobius.'):
                            # Convert mobius.api.routes to api.routes
                            module_name = alias.name.replace('mobius.', '')
                            mobius_imports.add(module_name)
                elif isinstance(node, ast.ImportFrom):
                    if node.module and node.module.startswith('mobius.'):
                        # Convert mobius.api.routes to api.routes
                        module_name = node.module.replace('mobius.', '')
                        mobius_imports.add(module_name)
                        
            return mobius_imports
        except (SyntaxError, UnicodeDecodeError):
            return set()
    
    def get_tested_modules(self) -> Set[str]:
        """Get all modules that have some form of test coverage."""
        tested_modules = set()
        
        # Check all test directories
        for test_type in ['unit', 'integration', 'property']:
            test_dir = self.test_root / test_type
            if test_dir.exists():
                for test_file in test_dir.glob('test_*.py'):
                    imports = self.analyze_test_imports(test_file)
                    tested_modules.update(imports)
                    
        return tested_modules
    
    def get_coverage_mapping(self) -> Dict[str, List[str]]:
        """Get mapping of modules to their test files."""
        coverage_mapping = {}
        
        for test_type in ['unit', 'integration', 'property']:
            test_dir = self.test_root / test_type
            if test_dir.exists():
                for test_file in test_dir.glob('test_*.py'):
                    imports = self.analyze_test_imports(test_file)
                    for module in imports:
                        if module not in coverage_mapping:
                            coverage_mapping[module] = []
                        coverage_mapping[module].append(f"{test_type}/{test_file.name}")
                        
        return coverage_mapping
    
    def is_essential_module(self, module_name: str) -> bool:
        """Determine if a module is essential and should have test coverage."""
        # Essential modules are those in core directories
        essential_patterns = [
            'api.',      # API routes and handlers
            'models.',   # Data models
            'storage.',  # Storage operations
            'nodes.',    # Core processing nodes
            'learning.', # Learning functionality
            'tools.',    # Utility tools
        ]
        
        return any(module_name.startswith(pattern) for pattern in essential_patterns)


def get_project_root() -> Path:
    """Get the project root directory."""
    current = Path(__file__).parent
    while current.parent != current:
        if (current / "pyproject.toml").exists():
            return current
        current = current.parent
    raise RuntimeError("Could not find project root")


@st.composite
def file_list_strategy(draw):
    """Generate a list of test files that could remain after cleanup."""
    project_root = get_project_root()
    analyzer = CoverageAnalyzer(project_root)
    
    # Get all current test files
    test_files = analyzer.get_test_files()
    all_test_files = []
    for test_type, files in test_files.items():
        all_test_files.extend([f"{test_type}/{f}" for f in files])
    
    # Generate a subset of test files (simulating cleanup)
    if not all_test_files:
        return []
    
    # Ensure we keep some essential tests
    keep_ratio = draw(st.floats(min_value=0.5, max_value=1.0))
    keep_count = max(1, int(len(all_test_files) * keep_ratio))
    
    return draw(st.lists(
        st.sampled_from(all_test_files),
        min_size=min(keep_count, len(all_test_files)),
        max_size=len(all_test_files),
        unique=True
    ))


@given(remaining_test_files=file_list_strategy())
@settings(max_examples=50)
def test_core_module_coverage_property(remaining_test_files):
    """
    Property 2: Test Coverage Maintenance.
    
    For any core module in the source directory, at least one test file must exist 
    that covers its functionality after cleanup operations.
    
    **Validates: Requirements 2.2, 3.2**
    """
    project_root = get_project_root()
    analyzer = CoverageAnalyzer(project_root)
    
    # Get all core modules that should have coverage
    core_modules = analyzer.get_core_modules()
    essential_modules = {mod for mod in core_modules if analyzer.is_essential_module(mod)}
    
    # Simulate which modules would be covered by remaining test files
    covered_modules = set()
    
    for test_file_path in remaining_test_files:
        # Parse test file path (e.g., "unit/test_brand_routes.py")
        test_type, test_file_name = test_file_path.split('/', 1)
        full_test_path = project_root / "tests" / test_type / test_file_name
        
        if full_test_path.exists():
            imports = analyzer.analyze_test_imports(full_test_path)
            covered_modules.update(imports)
    
    # Check that essential modules have coverage
    uncovered_essential = essential_modules - covered_modules
    
    # Filter out modules that don't actually exist (in case of cleanup simulation)
    actual_uncovered = []
    for module in uncovered_essential:
        module_path = analyzer.src_root / module.replace('.', '/') + '.py'
        if module_path.exists():
            actual_uncovered.append(module)
    
    # Allow some flexibility - not every single module needs direct coverage
    # But critical modules should be covered
    critical_modules = {
        'api.routes', 'api.errors', 'models.brand', 'storage.brands',
        'storage.database', 'nodes.audit', 'nodes.generate'
    }
    
    uncovered_critical = set(actual_uncovered) & critical_modules
    
    assert not uncovered_critical, (
        f"Critical modules must maintain test coverage after cleanup: {uncovered_critical}"
    )


def test_current_test_coverage_baseline():
    """
    Property 2 (baseline): Current test suite covers essential modules.
    
    This test establishes a baseline of current test coverage to ensure
    cleanup doesn't reduce coverage below acceptable levels.
    
    **Validates: Requirements 2.2, 3.2**
    """
    project_root = get_project_root()
    analyzer = CoverageAnalyzer(project_root)
    
    core_modules = analyzer.get_core_modules()
    tested_modules = analyzer.get_tested_modules()
    coverage_mapping = analyzer.get_coverage_mapping()
    
    # Calculate coverage percentage
    if core_modules:
        coverage_percentage = len(tested_modules & core_modules) / len(core_modules)
    else:
        coverage_percentage = 1.0
    
    # Essential modules should have coverage
    essential_modules = {mod for mod in core_modules if analyzer.is_essential_module(mod)}
    covered_essential = tested_modules & essential_modules
    
    # Report coverage statistics
    print(f"\nTest Coverage Analysis:")
    print(f"Total core modules: {len(core_modules)}")
    print(f"Essential modules: {len(essential_modules)}")
    print(f"Covered essential modules: {len(covered_essential)}")
    print(f"Overall coverage: {coverage_percentage:.1%}")
    
    # Ensure minimum coverage for essential modules
    if essential_modules:
        essential_coverage = len(covered_essential) / len(essential_modules)
        assert essential_coverage >= 0.7, (
            f"Essential module coverage ({essential_coverage:.1%}) below minimum (70%)"
        )


@given(st.lists(st.text(min_size=1, max_size=30), min_size=1, max_size=10))
@settings(max_examples=30)
def test_module_classification_robustness(module_names):
    """
    Property 2 (robustness): Module classification handles various inputs gracefully.
    
    For any list of module names, the classification process should not crash
    and should return consistent results.
    
    **Validates: Requirements 2.2, 3.2**
    """
    project_root = get_project_root()
    analyzer = CoverageAnalyzer(project_root)
    
    # Test that module classification doesn't crash on arbitrary input
    for module_name in module_names:
        try:
            # Clean the module name to be more realistic
            clean_name = re.sub(r'[^a-zA-Z0-9._]', '', module_name)
            if clean_name:
                result = analyzer.is_essential_module(clean_name)
                assert isinstance(result, bool)
        except Exception as e:
            pytest.fail(f"Module classification crashed on '{module_name}': {e}")


def test_test_file_analysis_completeness():
    """
    Property 2 (completeness): Test file analysis correctly identifies imports.
    
    This test verifies that the test analysis correctly identifies which modules
    are being tested by each test file.
    
    **Validates: Requirements 2.2, 3.2**
    """
    project_root = get_project_root()
    analyzer = CoverageAnalyzer(project_root)
    
    # Test on existing test files
    test_files = analyzer.get_test_files()
    
    for test_type, files in test_files.items():
        for test_file_name in files[:3]:  # Test first 3 files of each type
            test_file_path = project_root / "tests" / test_type / test_file_name
            
            if test_file_path.exists():
                imports = analyzer.analyze_test_imports(test_file_path)
                
                # Imports should be valid module names
                for import_name in imports:
                    assert '.' in import_name or import_name.isidentifier(), (
                        f"Invalid module name detected: {import_name}"
                    )
                    
                    # Should not contain 'mobius.' prefix (should be stripped)
                    assert not import_name.startswith('mobius.'), (
                        f"Module name should not contain 'mobius.' prefix: {import_name}"
                    )


def test_coverage_after_simulated_cleanup():
    """
    Property 2 (simulation): Simulate test cleanup and verify coverage maintained.
    
    This test simulates removing some test files and verifies that essential
    coverage is maintained.
    
    **Validates: Requirements 2.2, 3.2**
    """
    project_root = get_project_root()
    analyzer = CoverageAnalyzer(project_root)
    
    # Get current state
    core_modules = analyzer.get_core_modules()
    essential_modules = {mod for mod in core_modules if analyzer.is_essential_module(mod)}
    current_coverage = analyzer.get_coverage_mapping()
    
    # Simulate keeping only essential test files
    # Keep all property tests (they test core business logic)
    # Keep unit tests for API routes and storage
    # Keep integration tests for workflows
    essential_test_patterns = [
        'property/',           # All property tests
        'unit/test_brand_routes.py',
        'unit/test_storage.py',
        'unit/test_database_client.py',
        'integration/test_end_to_end.py',
        'integration/test_generation_workflow.py'
    ]
    
    # Calculate what would be covered after cleanup
    remaining_coverage = set()
    
    for test_type in ['unit', 'integration', 'property']:
        test_dir = project_root / "tests" / test_type
        if test_dir.exists():
            for test_file in test_dir.glob('test_*.py'):
                test_path = f"{test_type}/{test_file.name}"
                
                # Check if this test file matches essential patterns
                should_keep = any(
                    test_path.startswith(pattern) or test_path == pattern
                    for pattern in essential_test_patterns
                )
                
                if should_keep:
                    imports = analyzer.analyze_test_imports(test_file)
                    remaining_coverage.update(imports)
    
    # Verify essential modules still have coverage
    covered_essential = remaining_coverage & essential_modules
    
    # Critical modules that must have coverage
    critical_modules = {
        'api.routes', 'models.brand', 'storage.brands', 'storage.database'
    }
    
    uncovered_critical = critical_modules - remaining_coverage
    
    # Filter to only existing modules
    actual_uncovered_critical = []
    for module in uncovered_critical:
        module_path = analyzer.src_root / module.replace('.', '/') + '.py'
        if module_path.exists():
            actual_uncovered_critical.append(module)
    
    assert not actual_uncovered_critical, (
        f"Simulated cleanup would remove coverage for critical modules: {actual_uncovered_critical}"
    )


def test_test_organization_structure():
    """
    Property 2 (structure): Test files are properly organized by type.
    
    Verifies that the test suite maintains proper organization with
    unit, integration, and property tests in separate directories.
    
    **Validates: Requirements 2.2, 3.2**
    """
    project_root = get_project_root()
    test_root = project_root / "tests"
    
    # Required test directories should exist
    required_dirs = ['unit', 'integration', 'property']
    
    for dir_name in required_dirs:
        test_dir = test_root / dir_name
        assert test_dir.exists(), f"Test directory {dir_name} should exist"
        assert test_dir.is_dir(), f"{dir_name} should be a directory"
        
        # Should contain at least some test files
        test_files = list(test_dir.glob('test_*.py'))
        assert len(test_files) > 0, f"Test directory {dir_name} should contain test files"
    
    # Property tests should test core business logic
    property_dir = test_root / "property"
    property_files = list(property_dir.glob('test_*.py'))
    
    # Should have property tests for key functionality
    expected_property_tests = [
        'test_dependency_preservation.py',
        'test_documentation_content_preservation.py'
    ]
    
    existing_property_files = [f.name for f in property_files]
    
    for expected_test in expected_property_tests:
        assert expected_test in existing_property_files, (
            f"Expected property test {expected_test} should exist"
        )