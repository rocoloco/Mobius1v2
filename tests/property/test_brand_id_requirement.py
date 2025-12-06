"""
Property-based tests for brand ID requirement in generation requests.

**Feature: mobius-phase-2-refactor, Property 6: Brand ID is required for generation**
**Validates: Requirements 4.2**
"""

import pytest
from hypothesis import given, settings, strategies as st
from pydantic import ValidationError as PydanticValidationError
from mobius.api.schemas import GenerateRequest


@settings(max_examples=100)
@given(
    prompt=st.text(min_size=1, max_size=500),
    async_mode=st.booleans(),
)
def test_brand_id_required_for_generation(prompt: str, async_mode: bool):
    """
    Property: Brand ID is required for generation.

    For any generation request, if the brand_id parameter is missing,
    the system should raise a validation error.

    This ensures that all generation requests are properly associated
    with a brand for compliance checking.
    """
    # Attempt to create a GenerateRequest without brand_id
    with pytest.raises(PydanticValidationError) as exc_info:
        GenerateRequest(
            prompt=prompt,
            async_mode=async_mode,
            # brand_id intentionally omitted
        )

    # Verify that the error is about the missing brand_id field
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("brand_id",) and error["type"] == "missing"
        for error in errors
    ), "Validation error should indicate missing brand_id"


@settings(max_examples=100)
@given(
    brand_id=st.one_of(
        st.none(),
        st.just(""),
        st.text(max_size=0),
    ),
    prompt=st.text(min_size=1, max_size=500),
)
def test_brand_id_cannot_be_empty(brand_id, prompt: str):
    """
    Property: Brand ID cannot be empty or None.

    For any generation request with an empty or None brand_id,
    the system should raise a validation error.
    """
    with pytest.raises(PydanticValidationError) as exc_info:
        GenerateRequest(
            brand_id=brand_id,
            prompt=prompt,
        )

    # Verify validation error
    errors = exc_info.value.errors()
    assert any(
        error["loc"] == ("brand_id",)
        for error in errors
    ), "Validation error should be about brand_id"


@settings(max_examples=100)
@given(
    brand_id=st.text(min_size=1, max_size=100),
    prompt=st.text(min_size=1, max_size=500),
    async_mode=st.booleans(),
    template_id=st.one_of(st.none(), st.text(min_size=1, max_size=100)),
    webhook_url=st.one_of(st.none(), st.just("https://example.com/webhook")),
    idempotency_key=st.one_of(st.none(), st.text(min_size=1, max_size=64)),
)
def test_valid_brand_id_accepted(
    brand_id: str,
    prompt: str,
    async_mode: bool,
    template_id,
    webhook_url,
    idempotency_key,
):
    """
    Property: Valid brand IDs are accepted.

    For any generation request with a non-empty brand_id,
    the request should be successfully validated.
    """
    # This should not raise an error
    request = GenerateRequest(
        brand_id=brand_id,
        prompt=prompt,
        async_mode=async_mode,
        template_id=template_id,
        webhook_url=webhook_url,
        idempotency_key=idempotency_key,
    )

    # Verify the brand_id is preserved
    assert request.brand_id == brand_id
    assert request.prompt == prompt
    assert request.async_mode == async_mode


@settings(max_examples=100)
@given(
    brand_id=st.text(min_size=1, max_size=100),
    prompt=st.text(min_size=1, max_size=500),
)
def test_brand_id_preserved_in_request(brand_id: str, prompt: str):
    """
    Property: Brand ID is preserved in the request object.

    For any valid generation request, the brand_id should be
    exactly as provided in the input.
    """
    request = GenerateRequest(
        brand_id=brand_id,
        prompt=prompt,
    )

    # Brand ID should be preserved exactly
    assert request.brand_id == brand_id
    assert isinstance(request.brand_id, str)
    assert len(request.brand_id) > 0
