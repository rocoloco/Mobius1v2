"""
Property-based tests for request ID generation.

**Feature: mobius-phase-2-refactor, Property 16 (partial): Request ID uniqueness**
**Validates: Requirements 9.5**
"""

import pytest
from hypothesis import given, settings, strategies as st
from mobius.api.utils import generate_request_id
from mobius.constants import REQUEST_ID_PREFIX


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=1000))
def test_request_id_uniqueness(num_ids: int):
    """
    Property: Request ID uniqueness.

    For any number of request IDs generated, all IDs should be unique.
    This ensures distributed tracing works correctly without ID collisions.
    """
    # Generate multiple request IDs
    request_ids = [generate_request_id() for _ in range(num_ids)]

    # All IDs should be unique
    assert len(request_ids) == len(set(request_ids)), "Request IDs must be unique"


def test_request_id_format():
    """
    Test that request IDs follow the expected format.

    Request IDs should:
    - Start with the REQUEST_ID_PREFIX
    - Have a 12-character hexadecimal suffix
    - Be a valid string
    """
    request_id = generate_request_id()

    # Check prefix
    assert request_id.startswith(REQUEST_ID_PREFIX), f"Request ID should start with {REQUEST_ID_PREFIX}"

    # Check length (prefix + 12 hex chars)
    expected_length = len(REQUEST_ID_PREFIX) + 12
    assert len(request_id) == expected_length, f"Request ID should be {expected_length} characters"

    # Check that suffix is hexadecimal
    suffix = request_id[len(REQUEST_ID_PREFIX):]
    assert all(c in "0123456789abcdef" for c in suffix), "Request ID suffix should be hexadecimal"


@settings(max_examples=100)
@given(st.integers(min_value=1, max_value=100))
def test_request_id_concurrent_uniqueness(batch_size: int):
    """
    Property: Request IDs remain unique even when generated in batches.

    For any batch size, generating multiple request IDs should produce
    unique values without collisions.
    """
    # Generate multiple batches
    all_ids = []
    for _ in range(10):  # 10 batches
        batch = [generate_request_id() for _ in range(batch_size)]
        all_ids.extend(batch)

    # All IDs across all batches should be unique
    assert len(all_ids) == len(set(all_ids)), "Request IDs must be unique across batches"
