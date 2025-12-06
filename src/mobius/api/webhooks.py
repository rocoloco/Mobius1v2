"""
Webhook delivery with exponential backoff retry logic.

Implements reliable webhook delivery for async job completion notifications.
"""

import httpx
import asyncio
from typing import Dict, Any, Optional
import structlog
from mobius.config import settings

logger = structlog.get_logger()


async def deliver_webhook(
    url: str,
    payload: Dict[str, Any],
    job_id: str,
    attempt: int = 1,
    max_attempts: Optional[int] = None,
) -> bool:
    """
    Deliver webhook with exponential backoff retry logic.
    
    Implements the following retry strategy:
    - Attempt 1: Immediate
    - Attempt 2: Wait 2 seconds
    - Attempt 3: Wait 4 seconds
    - Attempt 4: Wait 8 seconds
    - Attempt 5: Wait 16 seconds
    
    Args:
        url: Webhook URL to POST to
        payload: JSON payload to send
        job_id: Job ID for logging
        attempt: Current attempt number (1-indexed)
        max_attempts: Maximum number of attempts (defaults to settings.webhook_retry_max)
        
    Returns:
        True if webhook delivered successfully, False if all retries exhausted
        
    Raises:
        No exceptions - all errors are caught and logged
    """
    if max_attempts is None:
        max_attempts = settings.webhook_retry_max
    
    # Calculate backoff time (exponential: 2^attempt seconds)
    # Attempt 1: 2^1 = 2s, Attempt 2: 2^2 = 4s, etc.
    backoff_seconds = 2 ** attempt if attempt > 1 else 0
    
    logger.info(
        "webhook_delivery_attempt",
        job_id=job_id,
        url=url,
        attempt=attempt,
        max_attempts=max_attempts,
        backoff_seconds=backoff_seconds,
    )
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(url, json=payload)
            response.raise_for_status()
            
            logger.info(
                "webhook_delivered",
                job_id=job_id,
                url=url,
                attempt=attempt,
                status_code=response.status_code,
            )
            return True
            
    except httpx.HTTPStatusError as e:
        logger.warning(
            "webhook_http_error",
            job_id=job_id,
            url=url,
            attempt=attempt,
            status_code=e.response.status_code,
            error=str(e),
        )
    except httpx.RequestError as e:
        logger.warning(
            "webhook_request_error",
            job_id=job_id,
            url=url,
            attempt=attempt,
            error=str(e),
        )
    except Exception as e:
        logger.error(
            "webhook_unexpected_error",
            job_id=job_id,
            url=url,
            attempt=attempt,
            error=str(e),
        )
    
    # If we haven't returned yet, the delivery failed
    if attempt < max_attempts:
        # Wait before retrying
        if backoff_seconds > 0:
            logger.info(
                "webhook_retry_backoff",
                job_id=job_id,
                url=url,
                attempt=attempt,
                next_attempt=attempt + 1,
                backoff_seconds=backoff_seconds,
            )
            await asyncio.sleep(backoff_seconds)
        
        # Retry
        return await deliver_webhook(
            url=url,
            payload=payload,
            job_id=job_id,
            attempt=attempt + 1,
            max_attempts=max_attempts,
        )
    
    # All retries exhausted
    logger.error(
        "webhook_exhausted",
        job_id=job_id,
        url=url,
        total_attempts=attempt,
        max_attempts=max_attempts,
    )
    return False


async def notify_job_completion(
    job_id: str,
    webhook_url: str,
    status: str,
    result: Dict[str, Any],
) -> bool:
    """
    Notify webhook of job completion.
    
    Constructs the webhook payload and delivers it with retry logic.
    Updates the job's webhook_attempts counter in the database.
    
    Args:
        job_id: Job ID
        webhook_url: Webhook URL to notify
        status: Job status (completed, failed, cancelled)
        result: Job result data
        
    Returns:
        True if webhook delivered successfully, False otherwise
    """
    from mobius.storage.jobs import JobStorage
    
    payload = {
        "job_id": job_id,
        "status": status,
        "result": result,
        "timestamp": asyncio.get_event_loop().time(),
    }
    
    logger.info(
        "webhook_notification_start",
        job_id=job_id,
        webhook_url=webhook_url,
        status=status,
    )
    
    # Deliver webhook with retry logic
    success = await deliver_webhook(
        url=webhook_url,
        payload=payload,
        job_id=job_id,
    )
    
    # Update webhook_attempts in database
    try:
        job_storage = JobStorage()
        job = await job_storage.get_job(job_id)
        if job:
            await job_storage.update_job(
                job_id=job_id,
                updates={"webhook_attempts": job.webhook_attempts + 1},
            )
    except Exception as e:
        logger.error(
            "webhook_attempts_update_failed",
            job_id=job_id,
            error=str(e),
        )
    
    return success
