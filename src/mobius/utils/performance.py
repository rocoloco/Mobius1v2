"""
Performance monitoring utilities for tracking optimization improvements.

Provides decorators and context managers for measuring execution time
and tracking performance metrics across the generation workflow.
"""

import time
import structlog
from functools import wraps
from contextlib import contextmanager
from typing import Dict, Any, Optional
from collections import defaultdict

logger = structlog.get_logger()

# Global performance metrics storage
_performance_metrics: Dict[str, list] = defaultdict(list)


@contextmanager
def timer(operation_name: str, job_id: Optional[str] = None, **context):
    """
    Context manager for timing operations.
    
    Usage:
        with timer("logo_processing", job_id="123"):
            # ... operation code ...
    """
    start_time = time.time()
    try:
        yield
    finally:
        duration_ms = int((time.time() - start_time) * 1000)
        
        # Log the timing
        logger.info(
            "performance_timing",
            operation=operation_name,
            duration_ms=duration_ms,
            job_id=job_id,
            **context
        )
        
        # Store metric for analysis
        _performance_metrics[operation_name].append({
            "duration_ms": duration_ms,
            "timestamp": time.time(),
            "job_id": job_id,
            **context
        })


def performance_monitor(operation_name: Optional[str] = None):
    """
    Decorator for monitoring function performance.
    
    Usage:
        @performance_monitor("generate_node")
        async def generate_node(state):
            # ... function code ...
    """
    def decorator(func):
        op_name = operation_name or f"{func.__module__}.{func.__name__}"
        
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Extract job_id from state if available
            job_id = None
            if args and isinstance(args[0], dict) and "job_id" in args[0]:
                job_id = args[0]["job_id"]
            
            with timer(op_name, job_id=job_id):
                return await func(*args, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Extract job_id from state if available
            job_id = None
            if args and isinstance(args[0], dict) and "job_id" in args[0]:
                job_id = args[0]["job_id"]
            
            with timer(op_name, job_id=job_id):
                return func(*args, **kwargs)
        
        # Return appropriate wrapper based on function type
        if hasattr(func, '__code__') and func.__code__.co_flags & 0x80:  # CO_COROUTINE
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator


def get_performance_summary(operation_name: Optional[str] = None, 
                          last_n_minutes: int = 60) -> Dict[str, Any]:
    """
    Get performance summary for operations.
    
    Args:
        operation_name: Specific operation to analyze (None for all)
        last_n_minutes: Only include metrics from last N minutes
        
    Returns:
        Dictionary with performance statistics
    """
    cutoff_time = time.time() - (last_n_minutes * 60)
    
    if operation_name:
        operations = {operation_name: _performance_metrics[operation_name]}
    else:
        operations = dict(_performance_metrics)
    
    summary = {}
    
    for op_name, metrics in operations.items():
        # Filter by time window
        recent_metrics = [
            m for m in metrics 
            if m["timestamp"] >= cutoff_time
        ]
        
        if not recent_metrics:
            continue
        
        durations = [m["duration_ms"] for m in recent_metrics]
        
        summary[op_name] = {
            "count": len(durations),
            "avg_ms": sum(durations) / len(durations),
            "min_ms": min(durations),
            "max_ms": max(durations),
            "total_ms": sum(durations),
            "p50_ms": sorted(durations)[len(durations) // 2],
            "p95_ms": sorted(durations)[int(len(durations) * 0.95)] if len(durations) > 1 else durations[0],
        }
    
    return summary


def log_performance_summary(operation_name: Optional[str] = None):
    """Log performance summary to structured logs."""
    summary = get_performance_summary(operation_name)
    
    if summary:
        logger.info(
            "performance_summary",
            operations=summary,
            total_operations=sum(s["count"] for s in summary.values())
        )
    else:
        logger.info("performance_summary", message="No recent performance data")


def clear_performance_metrics(operation_name: Optional[str] = None):
    """Clear performance metrics (useful for testing)."""
    if operation_name:
        _performance_metrics[operation_name].clear()
    else:
        _performance_metrics.clear()