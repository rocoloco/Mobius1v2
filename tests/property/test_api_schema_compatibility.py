"""
Property-Based Test: API Schema Compatibility

**Feature: gemini-3-dual-architecture, Property 14: API Schema Compatibility**
**Validates: Requirements 7.1**

This test verifies that all API endpoints maintain identical request and response
schemas before and after the Gemini 3 refactoring. This ensures backward
compatibility for existing API clients.

Property: For any API endpoint, the request and response schemas should match
the pre-refactoring schemas exactly, ensuring zero breaking changes.
"""

import pytest
from hypothesis import given, strategies as st, settings
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, timezone
from typing import Dict, Any

from mobius.api.schemas import (
    GenerateRequest,
    GenerateResponse,
    IngestBrandResponse,
    BrandListResponse,
    BrandDetailResponse,
    UpdateBrandRequest,
    JobStatusResponse,
    TemplateResponse,
    TemplateListResponse,
    FeedbackResponse,
    FeedbackStatsResponse,
    HealthCheckResponse,
)


# Strategies for generating valid API request data

brand_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pd"), min_codepoint=45, max_codepoint=122),
    min_size=8,
    max_size=36
).filter(lambda x: len(x.strip()) > 0 and not x.startswith('-') and not x.endswith('-'))

organization_id_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Pd"), min_codepoint=45, max_codepoint=122),
    min_size=8,
    max_size=36
).filter(lambda x: len(x.strip()) > 0 and not x.startswith('-') and not x.endswith('-'))

prompt_strategy = st.text(min_size=10, max_size=500).filter(lambda x: len(x.strip()) > 0)

brand_name_strategy = st.text(
    alphabet=st.characters(whitelist_categories=("Lu", "Ll", "Nd", "Zs"), min_codepoint=32, max_codepoint=122),
    min_size=2,
    max_size=100
).filter(lambda x: len(x.strip()) > 0)


@given(
    brand_id=brand_id_strategy,
    prompt=prompt_strategy,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_generate_request_schema_compatibility(brand_id, prompt):
    """
    Property 14.1: Generate Request Schema Compatibility
    
    For any generation request, the GenerateRequest schema should:
    1. Accept all required fields (brand_id, prompt)
    2. Accept all optional fields (template_id, webhook_url, async_mode, idempotency_key)
    3. Validate field types correctly
    4. Maintain the same field names and structure as pre-refactoring
    
    This ensures existing clients can continue using the same request format.
    """
    # Test with minimal required fields
    minimal_request = GenerateRequest(
        brand_id=brand_id,
        prompt=prompt
    )
    
    assert minimal_request.brand_id == brand_id
    assert minimal_request.prompt == prompt
    assert minimal_request.async_mode == False  # Default value
    assert minimal_request.template_id is None  # Default value
    assert minimal_request.webhook_url is None  # Default value
    assert minimal_request.idempotency_key is None  # Default value
    
    # Test with all optional fields
    full_request = GenerateRequest(
        brand_id=brand_id,
        prompt=prompt,
        template_id="template-123",
        webhook_url="https://example.com/webhook",
        async_mode=True,
        idempotency_key="client-key-456"
    )
    
    assert full_request.brand_id == brand_id
    assert full_request.prompt == prompt
    assert full_request.template_id == "template-123"
    assert full_request.webhook_url == "https://example.com/webhook"
    assert full_request.async_mode == True
    assert full_request.idempotency_key == "client-key-456"
    
    # Verify the schema can be serialized (for API transmission)
    request_dict = full_request.model_dump()
    assert isinstance(request_dict, dict)
    assert "brand_id" in request_dict
    assert "prompt" in request_dict
    assert "template_id" in request_dict
    assert "webhook_url" in request_dict
    assert "async_mode" in request_dict
    assert "idempotency_key" in request_dict


@given(
    job_id=brand_id_strategy,
    status=st.sampled_from(["pending", "processing", "completed", "failed", "cancelled"]),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_generate_response_schema_compatibility(job_id, status):
    """
    Property 14.2: Generate Response Schema Compatibility
    
    For any generation response, the GenerateResponse schema should:
    1. Include all required fields (job_id, status, message, request_id)
    2. Include optional fields (image_url, compliance_score)
    3. Maintain the same field names and types as pre-refactoring
    
    This ensures existing clients can parse responses without changes.
    """
    # Test with minimal required fields
    minimal_response = GenerateResponse(
        job_id=job_id,
        status=status,
        message="Job created successfully",
        request_id="req_abc123"
    )
    
    assert minimal_response.job_id == job_id
    assert minimal_response.status == status
    assert minimal_response.message == "Job created successfully"
    assert minimal_response.request_id == "req_abc123"
    assert minimal_response.image_url is None
    assert minimal_response.compliance_score is None
    
    # Test with all fields
    full_response = GenerateResponse(
        job_id=job_id,
        status=status,
        message="Job completed",
        request_id="req_def456",
        image_url="https://example.com/image.png",
        compliance_score=85.5
    )
    
    assert full_response.job_id == job_id
    assert full_response.status == status
    assert full_response.image_url == "https://example.com/image.png"
    assert full_response.compliance_score == 85.5
    
    # Verify serialization
    response_dict = full_response.model_dump()
    assert isinstance(response_dict, dict)
    assert "job_id" in response_dict
    assert "status" in response_dict
    assert "message" in response_dict
    assert "request_id" in response_dict
    assert "image_url" in response_dict
    assert "compliance_score" in response_dict


@given(
    brand_id=brand_id_strategy,
    organization_id=organization_id_strategy,
    brand_name=brand_name_strategy,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_ingest_brand_response_schema_compatibility(brand_id, organization_id, brand_name):
    """
    Property 14.3: Ingest Brand Response Schema Compatibility
    
    For any brand ingestion response, the IngestBrandResponse schema should:
    1. Include all required fields (brand_id, status, pdf_url, request_id)
    2. Include needs_review list
    3. Maintain the same structure as pre-refactoring
    
    This ensures brand ingestion API remains compatible.
    """
    response = IngestBrandResponse(
        brand_id=brand_id,
        status="created",
        pdf_url=f"https://cdn.example.com/{brand_id}/guidelines.pdf",
        needs_review=["No logo provided"],
        request_id="req_xyz789"
    )
    
    assert response.brand_id == brand_id
    assert response.status == "created"
    assert response.pdf_url.startswith("https://")
    assert isinstance(response.needs_review, list)
    assert response.request_id == "req_xyz789"
    
    # Verify serialization
    response_dict = response.model_dump()
    assert "brand_id" in response_dict
    assert "status" in response_dict
    assert "pdf_url" in response_dict
    assert "needs_review" in response_dict
    assert "request_id" in response_dict


@given(
    brand_id=brand_id_strategy,
    organization_id=organization_id_strategy,
    brand_name=brand_name_strategy,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_brand_detail_response_schema_compatibility(brand_id, organization_id, brand_name):
    """
    Property 14.4: Brand Detail Response Schema Compatibility
    
    For any brand detail response, the BrandDetailResponse schema should:
    1. Include all required fields
    2. Include guidelines as a dictionary
    3. Maintain the same structure as pre-refactoring
    
    This ensures brand retrieval API remains compatible.
    """
    now = datetime.now(timezone.utc)
    
    response = BrandDetailResponse(
        brand_id=brand_id,
        organization_id=organization_id,
        name=brand_name,
        guidelines={
            "colors": [],
            "typography": {"fonts": []},
            "logos": [],
            "voice": None,
            "rules": []
        },
        pdf_url=f"https://cdn.example.com/{brand_id}/guidelines.pdf",
        logo_thumbnail_url=f"https://cdn.example.com/{brand_id}/logo.png",
        needs_review=[],
        learning_active=False,
        feedback_count=0,
        created_at=now,
        updated_at=now,
        request_id="req_abc123"
    )
    
    assert response.brand_id == brand_id
    assert response.organization_id == organization_id
    assert response.name == brand_name
    assert isinstance(response.guidelines, dict)
    assert "colors" in response.guidelines
    assert "typography" in response.guidelines
    assert isinstance(response.needs_review, list)
    assert isinstance(response.learning_active, bool)
    assert isinstance(response.feedback_count, int)
    assert isinstance(response.created_at, datetime)
    assert isinstance(response.updated_at, datetime)
    
    # Verify serialization
    response_dict = response.model_dump()
    assert "brand_id" in response_dict
    assert "organization_id" in response_dict
    assert "name" in response_dict
    assert "guidelines" in response_dict
    assert "pdf_url" in response_dict
    assert "logo_thumbnail_url" in response_dict
    assert "needs_review" in response_dict
    assert "learning_active" in response_dict
    assert "feedback_count" in response_dict
    assert "created_at" in response_dict
    assert "updated_at" in response_dict
    assert "request_id" in response_dict


@given(
    job_id=brand_id_strategy,
    status=st.sampled_from(["pending", "processing", "completed", "failed", "cancelled"]),
    progress=st.floats(min_value=0.0, max_value=100.0, allow_nan=False, allow_infinity=False),
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_job_status_response_schema_compatibility(job_id, status, progress):
    """
    Property 14.5: Job Status Response Schema Compatibility
    
    For any job status response, the JobStatusResponse schema should:
    1. Include all required fields
    2. Include optional fields (current_image_url, compliance_score, error)
    3. Maintain the same structure as pre-refactoring
    
    This ensures job status API remains compatible.
    """
    now = datetime.now(timezone.utc)
    
    # Test with minimal fields
    minimal_response = JobStatusResponse(
        job_id=job_id,
        status=status,
        progress=progress,
        current_image_url=None,
        compliance_score=None,
        error=None,
        created_at=now,
        updated_at=now,
        request_id="req_abc123"
    )
    
    assert minimal_response.job_id == job_id
    assert minimal_response.status == status
    assert minimal_response.progress == progress
    assert minimal_response.current_image_url is None
    assert minimal_response.compliance_score is None
    assert minimal_response.error is None
    
    # Test with all fields
    full_response = JobStatusResponse(
        job_id=job_id,
        status=status,
        progress=progress,
        current_image_url="https://example.com/image.png",
        compliance_score=85.5,
        error="Generation failed",
        created_at=now,
        updated_at=now,
        request_id="req_def456"
    )
    
    assert full_response.current_image_url == "https://example.com/image.png"
    assert full_response.compliance_score == 85.5
    assert full_response.error == "Generation failed"
    
    # Verify serialization
    response_dict = full_response.model_dump()
    assert "job_id" in response_dict
    assert "status" in response_dict
    assert "progress" in response_dict
    assert "current_image_url" in response_dict
    assert "compliance_score" in response_dict
    assert "error" in response_dict
    assert "created_at" in response_dict
    assert "updated_at" in response_dict
    assert "request_id" in response_dict


@given(
    template_id=brand_id_strategy,
    brand_id=brand_id_strategy,
    template_name=brand_name_strategy,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_template_response_schema_compatibility(template_id, brand_id, template_name):
    """
    Property 14.6: Template Response Schema Compatibility
    
    For any template response, the TemplateResponse schema should:
    1. Include all required fields
    2. Include generation_params as a dictionary
    3. Maintain the same structure as pre-refactoring
    
    This ensures template API remains compatible.
    """
    now = datetime.now(timezone.utc)
    
    response = TemplateResponse(
        template_id=template_id,
        brand_id=brand_id,
        name=template_name,
        description="A professional template",
        generation_params={"temperature": 0.7, "aspect_ratio": "16:9"},
        thumbnail_url=f"https://cdn.example.com/{template_id}/thumb.png",
        created_at=now,
        request_id="req_abc123"
    )
    
    assert response.template_id == template_id
    assert response.brand_id == brand_id
    assert response.name == template_name
    assert isinstance(response.generation_params, dict)
    assert "temperature" in response.generation_params
    assert isinstance(response.created_at, datetime)
    
    # Verify serialization
    response_dict = response.model_dump()
    assert "template_id" in response_dict
    assert "brand_id" in response_dict
    assert "name" in response_dict
    assert "description" in response_dict
    assert "generation_params" in response_dict
    assert "thumbnail_url" in response_dict
    assert "created_at" in response_dict
    assert "request_id" in response_dict


@given(
    brand_id=brand_id_strategy,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_feedback_response_schema_compatibility(brand_id):
    """
    Property 14.7: Feedback Response Schema Compatibility
    
    For any feedback response, the FeedbackResponse schema should:
    1. Include all required fields
    2. Maintain the same structure as pre-refactoring
    
    This ensures feedback API remains compatible.
    """
    response = FeedbackResponse(
        feedback_id="feedback-123",
        brand_id=brand_id,
        total_feedback_count=42,
        learning_active=True,
        request_id="req_abc123"
    )
    
    assert response.feedback_id == "feedback-123"
    assert response.brand_id == brand_id
    assert response.total_feedback_count == 42
    assert response.learning_active == True
    
    # Verify serialization
    response_dict = response.model_dump()
    assert "feedback_id" in response_dict
    assert "brand_id" in response_dict
    assert "total_feedback_count" in response_dict
    assert "learning_active" in response_dict
    assert "request_id" in response_dict


@pytest.mark.asyncio
async def test_health_check_response_schema_compatibility():
    """
    Property 14.8: Health Check Response Schema Compatibility
    
    For any health check response, the HealthCheckResponse schema should:
    1. Include all required fields
    2. Maintain the same structure as pre-refactoring
    
    This ensures health check API remains compatible.
    """
    now = datetime.now(timezone.utc)
    
    response = HealthCheckResponse(
        status="healthy",
        database="healthy",
        storage="healthy",
        api="healthy",
        timestamp=now,
        request_id="req_abc123"
    )
    
    assert response.status == "healthy"
    assert response.database == "healthy"
    assert response.storage == "healthy"
    assert response.api == "healthy"
    assert isinstance(response.timestamp, datetime)
    
    # Verify serialization
    response_dict = response.model_dump()
    assert "status" in response_dict
    assert "database" in response_dict
    assert "storage" in response_dict
    assert "api" in response_dict
    assert "timestamp" in response_dict
    assert "request_id" in response_dict


@given(
    brand_name=brand_name_strategy,
)
@settings(max_examples=100, deadline=None)
@pytest.mark.asyncio
async def test_update_brand_request_schema_compatibility(brand_name):
    """
    Property 14.9: Update Brand Request Schema Compatibility
    
    For any brand update request, the UpdateBrandRequest schema should:
    1. Accept optional fields (name, logo_thumbnail_url)
    2. Allow partial updates (only some fields provided)
    3. Maintain the same structure as pre-refactoring
    
    This ensures brand update API remains compatible.
    """
    # Test with only name
    name_only = UpdateBrandRequest(name=brand_name)
    assert name_only.name == brand_name
    assert name_only.logo_thumbnail_url is None
    
    # Test with only logo
    logo_only = UpdateBrandRequest(logo_thumbnail_url="https://example.com/logo.png")
    assert logo_only.name is None
    assert logo_only.logo_thumbnail_url == "https://example.com/logo.png"
    
    # Test with both fields
    both_fields = UpdateBrandRequest(
        name=brand_name,
        logo_thumbnail_url="https://example.com/logo.png"
    )
    assert both_fields.name == brand_name
    assert both_fields.logo_thumbnail_url == "https://example.com/logo.png"
    
    # Test with no fields (empty update)
    empty_update = UpdateBrandRequest()
    assert empty_update.name is None
    assert empty_update.logo_thumbnail_url is None
    
    # Verify serialization with exclude_none
    update_dict = both_fields.model_dump(exclude_none=True)
    assert "name" in update_dict
    assert "logo_thumbnail_url" in update_dict
    
    empty_dict = empty_update.model_dump(exclude_none=True)
    assert len(empty_dict) == 0  # No fields should be present


@pytest.mark.asyncio
async def test_all_response_schemas_include_request_id():
    """
    Property 14.10: All Response Schemas Include request_id
    
    For any API response schema, it should include a request_id field.
    This is a critical field for distributed tracing and debugging.
    
    This ensures all responses can be traced back to their originating request.
    """
    now = datetime.now(timezone.utc)
    
    # Test all response schemas
    schemas_to_test = [
        GenerateResponse(
            job_id="job-123",
            status="pending",
            message="Job created",
            request_id="req_1"
        ),
        IngestBrandResponse(
            brand_id="brand-123",
            status="created",
            pdf_url="https://example.com/pdf",
            request_id="req_2"
        ),
        BrandDetailResponse(
            brand_id="brand-123",
            organization_id="org-123",
            name="Test Brand",
            guidelines={},
            pdf_url="https://example.com/pdf",
            logo_thumbnail_url=None,
            needs_review=[],
            learning_active=False,
            feedback_count=0,
            created_at=now,
            updated_at=now,
            request_id="req_3"
        ),
        JobStatusResponse(
            job_id="job-123",
            status="pending",
            progress=0.0,
            current_image_url=None,
            compliance_score=None,
            error=None,
            created_at=now,
            updated_at=now,
            request_id="req_4"
        ),
        TemplateResponse(
            template_id="template-123",
            brand_id="brand-123",
            name="Template",
            description="Description",
            generation_params={},
            thumbnail_url="https://example.com/thumb",
            created_at=now,
            request_id="req_5"
        ),
        FeedbackResponse(
            feedback_id="feedback-123",
            brand_id="brand-123",
            total_feedback_count=10,
            learning_active=True,
            request_id="req_6"
        ),
        HealthCheckResponse(
            status="healthy",
            database="healthy",
            storage="healthy",
            api="healthy",
            timestamp=now,
            request_id="req_7"
        ),
    ]
    
    for schema in schemas_to_test:
        # Verify request_id field exists
        assert hasattr(schema, 'request_id'), \
            f"{schema.__class__.__name__} must have request_id field"
        
        # Verify request_id is a string
        assert isinstance(schema.request_id, str), \
            f"{schema.__class__.__name__}.request_id must be a string"
        
        # Verify request_id is present in serialized form
        schema_dict = schema.model_dump()
        assert "request_id" in schema_dict, \
            f"{schema.__class__.__name__} serialization must include request_id"
        
        # Verify request_id is not empty
        assert len(schema.request_id) > 0, \
            f"{schema.__class__.__name__}.request_id must not be empty"
