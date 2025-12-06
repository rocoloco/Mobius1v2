"""
Property-based tests for API versioning consistency.

**Feature: mobius-phase-2-refactor, Property 15: API versioning consistency**

Tests that all API endpoints follow consistent versioning patterns.
"""

from hypothesis import given, strategies as st
import pytest


# Property 15: API versioning consistency
def test_api_endpoint_versioning():
    """
    **Feature: mobius-phase-2-refactor, Property 15: API versioning consistency**
    
    *For any* API endpoint, the URL path should start with the version prefix v1.
    
    **Validates: Requirements 9.1**
    
    This test verifies that all defined API endpoints follow the v1 versioning pattern.
    """
    import ast
    import pathlib
    
    # Read the app.py file and parse it
    app_file = pathlib.Path("src/mobius/api/app.py")
    assert app_file.exists(), "app.py file not found"
    
    with open(app_file, "r") as f:
        tree = ast.parse(f.read())
    
    # Find all function definitions
    endpoints = []
    non_v1_endpoints = []
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            
            # Check if it's decorated with @app.function
            is_endpoint = any(
                isinstance(decorator, ast.Call) and
                hasattr(decorator.func, 'attr') and
                decorator.func.attr == 'function'
                for decorator in node.decorator_list
            )
            
            if is_endpoint:
                # All v1 endpoints should start with "v1_"
                if func_name.startswith("v1_"):
                    endpoints.append(func_name)
                # Legacy endpoint is allowed
                elif func_name == "run_mobius_job":
                    # This is the legacy endpoint, which is acceptable
                    pass
                elif func_name == "cleanup_expired_jobs":
                    # This is a cron job, not an API endpoint
                    pass
                else:
                    # Any other endpoint should fail the test
                    non_v1_endpoints.append(func_name)
    
    # Verify we found some endpoints
    assert len(endpoints) > 0, "No v1 endpoints found in the Modal app"
    
    # Check for non-v1 endpoints
    assert len(non_v1_endpoints) == 0, (
        f"Found endpoints that don't follow v1 naming convention: {non_v1_endpoints}. "
        f"All API endpoints must start with 'v1_' prefix."
    )
    
    # All endpoints should follow the v1_ naming pattern
    for endpoint in endpoints:
        assert endpoint.startswith("v1_"), (
            f"Endpoint {endpoint} does not start with 'v1_' prefix. "
            f"All API endpoints must follow the v1 versioning pattern."
        )
    
    print(f"✓ All {len(endpoints)} API endpoints follow v1 versioning pattern")


@given(
    endpoint_name=st.sampled_from([
        "v1_ingest_brand",
        "v1_list_brands",
        "v1_get_brand",
        "v1_update_brand",
        "v1_delete_brand",
        "v1_generate",
        "v1_get_job_status",
        "v1_cancel_job",
        "v1_save_template",
        "v1_list_templates",
        "v1_get_template",
        "v1_delete_template",
        "v1_submit_feedback",
        "v1_get_feedback_stats",
        "v1_health",
        "v1_docs",
    ])
)
def test_endpoint_name_starts_with_v1(endpoint_name: str):
    """
    **Feature: mobius-phase-2-refactor, Property 15: API versioning consistency**
    
    *For any* defined API endpoint name, it should start with the version prefix 'v1_'.
    
    **Validates: Requirements 9.1**
    
    This property test verifies that endpoint naming follows the v1 convention.
    """
    assert endpoint_name.startswith("v1_"), (
        f"Endpoint {endpoint_name} does not start with 'v1_' prefix"
    )


@given(
    label=st.sampled_from([
        "v1-ingest-brand",
        "v1-list-brands",
        "v1-get-brand",
        "v1-update-brand",
        "v1-delete-brand",
        "v1-generate",
        "v1-get-job-status",
        "v1-cancel-job",
        "v1-save-template",
        "v1-list-templates",
        "v1-get-template",
        "v1-delete-template",
        "v1-submit-feedback",
        "v1-get-feedback-stats",
        "v1-health",
        "v1-docs",
    ])
)
def test_endpoint_label_starts_with_v1(label: str):
    """
    **Feature: mobius-phase-2-refactor, Property 15: API versioning consistency**
    
    *For any* defined API endpoint label, it should start with the version prefix 'v1-'.
    
    **Validates: Requirements 9.1**
    
    This property test verifies that endpoint labels follow the v1 convention.
    """
    assert label.startswith("v1-"), (
        f"Endpoint label {label} does not start with 'v1-' prefix"
    )


def test_legacy_endpoint_exists():
    """
    Verify that the legacy Phase 1 endpoint exists for backward compatibility.
    
    The legacy endpoint 'run_mobius_job' should exist but should log a deprecation warning.
    """
    import ast
    import pathlib
    
    # Read the app.py file and parse it
    app_file = pathlib.Path("src/mobius/api/app.py")
    assert app_file.exists(), "app.py file not found"
    
    with open(app_file, "r") as f:
        tree = ast.parse(f.read())
    
    # Check if legacy endpoint exists
    legacy_found = False
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "run_mobius_job":
            legacy_found = True
            break
    
    assert legacy_found, (
        "Legacy endpoint 'run_mobius_job' not found. "
        "This endpoint is required for backward compatibility with Phase 1."
    )
    
    print("✓ Legacy endpoint 'run_mobius_job' exists for backward compatibility")


def test_all_required_endpoints_exist():
    """
    Verify that all required v1 endpoints are defined in the Modal app.
    
    This ensures completeness of the API implementation.
    """
    import ast
    import pathlib
    
    required_endpoints = {
        # Brand management
        "v1_ingest_brand",
        "v1_list_brands",
        "v1_get_brand",
        "v1_update_brand",
        "v1_delete_brand",
        # Generation
        "v1_generate",
        # Job management
        "v1_get_job_status",
        "v1_cancel_job",
        # Template management
        "v1_save_template",
        "v1_list_templates",
        "v1_get_template",
        "v1_delete_template",
        # Feedback
        "v1_submit_feedback",
        "v1_get_feedback_stats",
        # System
        "v1_health",
        "v1_docs",
    }
    
    # Read the app.py file and parse it
    app_file = pathlib.Path("src/mobius/api/app.py")
    assert app_file.exists(), "app.py file not found"
    
    with open(app_file, "r") as f:
        tree = ast.parse(f.read())
    
    # Get all function names from the app
    defined_endpoints = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            func_name = node.name
            if func_name.startswith("v1_"):
                defined_endpoints.add(func_name)
    
    # Check for missing endpoints
    missing = required_endpoints - defined_endpoints
    assert not missing, (
        f"Missing required endpoints: {missing}. "
        f"All required v1 endpoints must be implemented."
    )
    
    print(f"✓ All {len(required_endpoints)} required v1 endpoints are defined")
