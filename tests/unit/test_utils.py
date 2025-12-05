"""
Unit tests for API utilities.

Tests request ID generation and context management.
"""

import pytest
from mobius.api.utils import generate_request_id, get_request_id, set_request_id
from mobius.constants import REQUEST_ID_PREFIX


def test_generate_request_id_format():
    """Test that generated request IDs have the correct format."""
    request_id = generate_request_id()

    # Should start with prefix
    assert request_id.startswith(REQUEST_ID_PREFIX)

    # Should have correct length (prefix + 12 hex chars)
    expected_length = len(REQUEST_ID_PREFIX) + 12
    assert len(request_id) == expected_length

    # Suffix should be hexadecimal
    suffix = request_id[len(REQUEST_ID_PREFIX) :]
    assert all(c in "0123456789abcdef" for c in suffix)


def test_generate_request_id_uniqueness():
    """Test that multiple generated request IDs are unique."""
    ids = [generate_request_id() for _ in range(100)]

    # All IDs should be unique
    assert len(ids) == len(set(ids))


def test_request_id_context_management():
    """Test that request ID context management works correctly."""
    # Initially should be empty
    assert get_request_id() == ""

    # Set a request ID
    test_id = "req_test123456"
    set_request_id(test_id)

    # Should retrieve the same ID
    assert get_request_id() == test_id

    # Set a different ID
    new_id = "req_new789012"
    set_request_id(new_id)

    # Should retrieve the new ID
    assert get_request_id() == new_id


def test_request_id_context_isolation():
    """Test that request ID context is properly isolated."""
    # Set initial ID
    id1 = generate_request_id()
    set_request_id(id1)
    assert get_request_id() == id1

    # Generate and set new ID
    id2 = generate_request_id()
    set_request_id(id2)

    # Should have the new ID, not the old one
    assert get_request_id() == id2
    assert get_request_id() != id1
