"""
WebSocket handlers for real-time brand compliance monitoring.

Provides WebSocket endpoints for streaming compliance scores, reasoning logs,
color analysis, and constraint updates during brand audit processes.
"""

import json
import asyncio
import structlog
from typing import Dict, Set, Optional
from datetime import datetime
from fastapi import WebSocket, WebSocketDisconnect
from mobius.api.utils import generate_request_id

logger = structlog.get_logger()

# Global connection manager for WebSocket connections
class WebSocketConnectionManager:
    """
    Manages WebSocket connections for real-time monitoring.
    
    Features:
    - Job-based connection grouping
    - Message broadcasting to job subscribers
    - Connection lifecycle management
    - Automatic cleanup on disconnect
    """
    
    def __init__(self):
        # Dictionary mapping job_id to set of WebSocket connections
        self.job_connections: Dict[str, Set[WebSocket]] = {}
        # Dictionary mapping WebSocket to job_id for cleanup
        self.connection_jobs: Dict[WebSocket, str] = {}
        
    async def connect(self, websocket: WebSocket, job_id: str):
        """Accept WebSocket connection and add to job group."""
        await websocket.accept()
        
        # Add to job group
        if job_id not in self.job_connections:
            self.job_connections[job_id] = set()
        
        self.job_connections[job_id].add(websocket)
        self.connection_jobs[websocket] = job_id
        
        logger.info(
            "websocket_connected",
            job_id=job_id,
            connection_count=len(self.job_connections[job_id])
        )
        
        # Send connection confirmation
        await self.send_to_connection(websocket, {
            "type": "connection_confirmed",
            "jobId": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "message": "WebSocket connected successfully",
                "connection_count": len(self.job_connections[job_id])
            }
        })
    
    def disconnect(self, websocket: WebSocket):
        """Remove WebSocket connection and cleanup."""
        job_id = self.connection_jobs.get(websocket)
        
        if job_id and job_id in self.job_connections:
            self.job_connections[job_id].discard(websocket)
            
            # Clean up empty job groups
            if not self.job_connections[job_id]:
                del self.job_connections[job_id]
                
        if websocket in self.connection_jobs:
            del self.connection_jobs[websocket]
            
        logger.info(
            "websocket_disconnected",
            job_id=job_id,
            remaining_connections=len(self.job_connections.get(job_id, []))
        )
    
    async def send_to_job(self, job_id: str, message: dict):
        """Send message to all connections subscribed to a job."""
        if job_id not in self.job_connections:
            logger.debug("no_connections_for_job", job_id=job_id)
            return
        
        # Create a copy of connections to avoid modification during iteration
        connections = list(self.job_connections[job_id])
        disconnected = []
        
        for websocket in connections:
            try:
                await self.send_to_connection(websocket, message)
            except Exception as e:
                logger.warning(
                    "websocket_send_failed",
                    job_id=job_id,
                    error=str(e)
                )
                disconnected.append(websocket)
        
        # Clean up failed connections
        for websocket in disconnected:
            self.disconnect(websocket)
    
    async def send_to_connection(self, websocket: WebSocket, message: dict):
        """Send message to a specific WebSocket connection."""
        try:
            await websocket.send_text(json.dumps(message))
        except Exception as e:
            logger.error("websocket_message_send_failed", error=str(e))
            raise
    
    def get_job_connection_count(self, job_id: str) -> int:
        """Get number of active connections for a job."""
        return len(self.job_connections.get(job_id, []))
    
    def get_total_connections(self) -> int:
        """Get total number of active connections."""
        return sum(len(connections) for connections in self.job_connections.values())

# Global connection manager instance
connection_manager = WebSocketConnectionManager()

async def websocket_monitoring_endpoint(websocket: WebSocket, job_id: str):
    """
    WebSocket endpoint for real-time monitoring of a specific job.
    
    URL: /ws/monitoring/{job_id}
    
    Handles:
    - Connection establishment and authentication
    - Message routing for compliance updates
    - Heartbeat/ping-pong for connection health
    - Graceful disconnection and cleanup
    
    Args:
        websocket: FastAPI WebSocket connection
        job_id: Job ID to monitor
    """
    request_id = generate_request_id()
    
    logger.info(
        "websocket_connection_attempt",
        request_id=request_id,
        job_id=job_id
    )
    
    try:
        # Accept connection and add to manager
        await connection_manager.connect(websocket, job_id)
        
        # Send initial job status if available
        await send_initial_job_status(websocket, job_id)
        
        # Handle incoming messages (mainly heartbeat)
        while True:
            try:
                # Wait for message with timeout
                message = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0  # 30 second timeout
                )
                
                # Parse and handle message
                try:
                    data = json.loads(message)
                    await handle_websocket_message(websocket, job_id, data)
                except json.JSONDecodeError:
                    logger.warning(
                        "invalid_websocket_message",
                        job_id=job_id,
                        message=message
                    )
                    await connection_manager.send_to_connection(websocket, {
                        "type": "error",
                        "jobId": job_id,
                        "timestamp": datetime.utcnow().isoformat(),
                        "payload": {
                            "message": "Invalid JSON message format"
                        }
                    })
                    
            except asyncio.TimeoutError:
                # Send ping to check connection health
                await connection_manager.send_to_connection(websocket, {
                    "type": "ping",
                    "jobId": job_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "payload": {}
                })
                
    except WebSocketDisconnect:
        logger.info("websocket_client_disconnected", job_id=job_id)
    except Exception as e:
        logger.error(
            "websocket_connection_error",
            job_id=job_id,
            error=str(e)
        )
    finally:
        # Clean up connection
        connection_manager.disconnect(websocket)

async def handle_websocket_message(websocket: WebSocket, job_id: str, data: dict):
    """
    Handle incoming WebSocket messages from client.
    
    Supports:
    - ping/pong for heartbeat
    - subscription management
    - Client-side error reporting
    
    Args:
        websocket: WebSocket connection
        job_id: Job ID being monitored
        data: Parsed JSON message from client
    """
    message_type = data.get("type")
    
    if message_type == "ping":
        # Respond to ping with pong
        await connection_manager.send_to_connection(websocket, {
            "type": "pong",
            "jobId": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {}
        })
        
    elif message_type == "subscribe":
        # Handle subscription requests (future enhancement)
        logger.info("websocket_subscribe_request", job_id=job_id, data=data)
        
    elif message_type == "unsubscribe":
        # Handle unsubscription requests (future enhancement)
        logger.info("websocket_unsubscribe_request", job_id=job_id, data=data)
        
    else:
        logger.warning("unknown_websocket_message_type", job_id=job_id, type=message_type)

async def send_initial_job_status(websocket: WebSocket, job_id: str):
    """
    Send initial job status when client connects.
    
    Provides current state of the job including:
    - Current status and progress
    - Latest compliance scores
    - Recent reasoning logs
    - Current constraint violations
    
    Args:
        websocket: WebSocket connection
        job_id: Job ID to get status for
    """
    try:
        from mobius.storage.jobs import JobStorage
        
        job_storage = JobStorage()
        job = await job_storage.get_job(job_id)
        
        if not job:
            await connection_manager.send_to_connection(websocket, {
                "type": "error",
                "jobId": job_id,
                "timestamp": datetime.utcnow().isoformat(),
                "payload": {
                    "message": f"Job {job_id} not found"
                }
            })
            return
        
        # Send current job status
        await connection_manager.send_to_connection(websocket, {
            "type": "status_change",
            "jobId": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "jobId": job_id,
                "status": job.status,
                "progress": job.progress,
                "currentStep": job.state.get("current_step", "Initializing") if job.state else "Initializing"
            }
        })
        
        # Send latest compliance scores if available
        if job.state and job.state.get("compliance_scores"):
            latest_scores = job.state["compliance_scores"][-1]
            if latest_scores:
                await connection_manager.send_to_connection(websocket, {
                    "type": "compliance_score",
                    "jobId": job_id,
                    "timestamp": datetime.utcnow().isoformat(),
                    "payload": {
                        "typography": latest_scores.get("categories", {}).get("typography", {}).get("score", 0) / 100,
                        "voice": latest_scores.get("categories", {}).get("voice", {}).get("score", 0) / 100,
                        "color": latest_scores.get("categories", {}).get("color", {}).get("score", 0) / 100,
                        "logo": latest_scores.get("categories", {}).get("logo", {}).get("score", 0) / 100,
                    }
                })
        
        logger.info("initial_job_status_sent", job_id=job_id, status=job.status)
        
    except Exception as e:
        logger.error("send_initial_status_failed", job_id=job_id, error=str(e))
        await connection_manager.send_to_connection(websocket, {
            "type": "error",
            "jobId": job_id,
            "timestamp": datetime.utcnow().isoformat(),
            "payload": {
                "message": f"Failed to load job status: {str(e)}"
            }
        })

# Message broadcasting functions for workflow integration

async def broadcast_compliance_scores(job_id: str, scores: dict):
    """
    Broadcast compliance scores to all connections monitoring a job.
    
    Args:
        job_id: Job ID to broadcast to
        scores: Compliance scores dictionary with category scores
    """
    message = {
        "type": "compliance_score",
        "jobId": job_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": {
            "typography": scores.get("categories", {}).get("typography", {}).get("score", 0) / 100,
            "voice": scores.get("categories", {}).get("voice", {}).get("score", 0) / 100,
            "color": scores.get("categories", {}).get("color", {}).get("score", 0) / 100,
            "logo": scores.get("categories", {}).get("logo", {}).get("score", 0) / 100,
        }
    }
    
    await connection_manager.send_to_job(job_id, message)
    logger.debug("compliance_scores_broadcasted", job_id=job_id)

async def broadcast_reasoning_log(job_id: str, log_entry: dict):
    """
    Broadcast reasoning log entry to all connections monitoring a job.
    
    Args:
        job_id: Job ID to broadcast to
        log_entry: Reasoning log entry with step, message, and level
    """
    message = {
        "type": "reasoning_log",
        "jobId": job_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": {
            "id": f"{job_id}_{datetime.utcnow().timestamp()}",
            "timestamp": datetime.utcnow().isoformat(),
            "step": log_entry.get("step", "Unknown"),
            "message": log_entry.get("message", ""),
            "level": log_entry.get("level", "info")
        }
    }
    
    await connection_manager.send_to_job(job_id, message)
    logger.debug("reasoning_log_broadcasted", job_id=job_id, step=log_entry.get("step"))

async def broadcast_color_analysis(job_id: str, color_data: list):
    """
    Broadcast color analysis results to all connections monitoring a job.
    
    Args:
        job_id: Job ID to broadcast to
        color_data: List of color analysis data with hex, name, percentage, usage
    """
    message = {
        "type": "color_analysis",
        "jobId": job_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": color_data
    }
    
    await connection_manager.send_to_job(job_id, message)
    logger.debug("color_analysis_broadcasted", job_id=job_id, color_count=len(color_data))

async def broadcast_constraint_update(job_id: str, constraints: list):
    """
    Broadcast constraint status updates to all connections monitoring a job.
    
    Args:
        job_id: Job ID to broadcast to
        constraints: List of constraint status objects
    """
    message = {
        "type": "constraint_update",
        "jobId": job_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": constraints
    }
    
    await connection_manager.send_to_job(job_id, message)
    logger.debug("constraint_update_broadcasted", job_id=job_id, constraint_count=len(constraints))

async def broadcast_status_change(job_id: str, status: str, progress: float, current_step: str):
    """
    Broadcast job status change to all connections monitoring a job.
    
    Args:
        job_id: Job ID to broadcast to
        status: New job status
        progress: Current progress (0-100)
        current_step: Description of current step
    """
    message = {
        "type": "status_change",
        "jobId": job_id,
        "timestamp": datetime.utcnow().isoformat(),
        "payload": {
            "jobId": job_id,
            "status": status,
            "progress": progress,
            "currentStep": current_step
        }
    }
    
    await connection_manager.send_to_job(job_id, message)
    logger.debug("status_change_broadcasted", job_id=job_id, status=status, progress=progress)

# Utility functions for workflow integration

def get_connection_manager() -> WebSocketConnectionManager:
    """Get the global WebSocket connection manager instance."""
    return connection_manager

def get_job_connection_count(job_id: str) -> int:
    """Get number of active WebSocket connections for a job."""
    return connection_manager.get_job_connection_count(job_id)

def get_total_connection_count() -> int:
    """Get total number of active WebSocket connections."""
    return connection_manager.get_total_connections()