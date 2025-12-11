"""
Unit tests for WebSocket integration in real-time monitoring.

Tests the WebSocket manager, connection handling, and message broadcasting
functionality for brand compliance monitoring.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from mobius.api.websocket_handlers import (
    WebSocketConnectionManager,
    broadcast_compliance_scores,
    broadcast_reasoning_log,
    broadcast_status_change,
)


class TestWebSocketConnectionManager:
    """Test WebSocket connection management functionality."""

    @pytest.fixture
    def manager(self):
        """Create a fresh WebSocket connection manager for each test."""
        return WebSocketConnectionManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket connection."""
        websocket = Mock()
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        return websocket

    @pytest.mark.asyncio
    async def test_connect_websocket(self, manager, mock_websocket):
        """Test WebSocket connection establishment."""
        job_id = "test-job-123"
        
        await manager.connect(mock_websocket, job_id)
        
        # Verify connection was accepted
        mock_websocket.accept.assert_called_once()
        
        # Verify connection was added to job group
        assert job_id in manager.job_connections
        assert mock_websocket in manager.job_connections[job_id]
        assert manager.connection_jobs[mock_websocket] == job_id
        
        # Verify connection count
        assert manager.get_job_connection_count(job_id) == 1
        assert manager.get_total_connections() == 1

    @pytest.mark.asyncio
    async def test_disconnect_websocket(self, manager, mock_websocket):
        """Test WebSocket disconnection and cleanup."""
        job_id = "test-job-123"
        
        # First connect
        await manager.connect(mock_websocket, job_id)
        assert manager.get_job_connection_count(job_id) == 1
        
        # Then disconnect
        manager.disconnect(mock_websocket)
        
        # Verify cleanup
        assert manager.get_job_connection_count(job_id) == 0
        assert mock_websocket not in manager.connection_jobs
        assert job_id not in manager.job_connections

    @pytest.mark.asyncio
    async def test_send_to_job(self, manager, mock_websocket):
        """Test broadcasting message to all connections for a job."""
        job_id = "test-job-123"
        message = {
            "type": "test_message",
            "jobId": job_id,
            "payload": {"test": "data"}
        }
        
        # Connect websocket
        await manager.connect(mock_websocket, job_id)
        
        # Send message to job
        await manager.send_to_job(job_id, message)
        
        # Verify message was sent
        mock_websocket.send_text.assert_called_once()
        sent_data = mock_websocket.send_text.call_args[0][0]
        assert json.loads(sent_data) == message

    @pytest.mark.asyncio
    async def test_multiple_connections_same_job(self, manager):
        """Test multiple WebSocket connections for the same job."""
        job_id = "test-job-123"
        
        # Create multiple mock websockets
        ws1 = Mock()
        ws1.accept = AsyncMock()
        ws1.send_text = AsyncMock()
        
        ws2 = Mock()
        ws2.accept = AsyncMock()
        ws2.send_text = AsyncMock()
        
        # Connect both
        await manager.connect(ws1, job_id)
        await manager.connect(ws2, job_id)
        
        # Verify both are tracked
        assert manager.get_job_connection_count(job_id) == 2
        assert manager.get_total_connections() == 2
        
        # Send message to job
        message = {"type": "test", "jobId": job_id, "payload": {}}
        await manager.send_to_job(job_id, message)
        
        # Verify both received the message
        ws1.send_text.assert_called_once()
        ws2.send_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_send_to_nonexistent_job(self, manager):
        """Test sending message to job with no connections."""
        job_id = "nonexistent-job"
        message = {"type": "test", "jobId": job_id, "payload": {}}
        
        # Should not raise exception
        await manager.send_to_job(job_id, message)
        
        # No connections should exist
        assert manager.get_job_connection_count(job_id) == 0


class TestWebSocketBroadcasting:
    """Test WebSocket message broadcasting functions."""

    @pytest.mark.asyncio
    @patch('mobius.api.websocket_handlers.connection_manager')
    async def test_broadcast_compliance_scores(self, mock_manager):
        """Test broadcasting compliance scores."""
        job_id = "test-job-123"
        scores = {
            "categories": {
                "typography": {"score": 85},
                "voice": {"score": 90},
                "color": {"score": 75},
                "logo": {"score": 95}
            }
        }
        
        mock_manager.send_to_job = AsyncMock()
        
        await broadcast_compliance_scores(job_id, scores)
        
        # Verify message was sent with correct format
        mock_manager.send_to_job.assert_called_once()
        call_args = mock_manager.send_to_job.call_args
        
        assert call_args[0][0] == job_id  # First arg is job_id
        message = call_args[0][1]  # Second arg is message
        
        assert message["type"] == "compliance_score"
        assert message["jobId"] == job_id
        assert "timestamp" in message
        
        payload = message["payload"]
        assert payload["typography"] == 0.85  # Converted to 0-1 scale
        assert payload["voice"] == 0.90
        assert payload["color"] == 0.75
        assert payload["logo"] == 0.95

    @pytest.mark.asyncio
    @patch('mobius.api.websocket_handlers.connection_manager')
    async def test_broadcast_reasoning_log(self, mock_manager):
        """Test broadcasting reasoning log entries."""
        job_id = "test-job-123"
        log_entry = {
            "step": "Generation",
            "message": "Starting image generation",
            "level": "info"
        }
        
        mock_manager.send_to_job = AsyncMock()
        
        await broadcast_reasoning_log(job_id, log_entry)
        
        # Verify message was sent with correct format
        mock_manager.send_to_job.assert_called_once()
        call_args = mock_manager.send_to_job.call_args
        
        assert call_args[0][0] == job_id
        message = call_args[0][1]
        
        assert message["type"] == "reasoning_log"
        assert message["jobId"] == job_id
        assert "timestamp" in message
        
        payload = message["payload"]
        assert payload["step"] == "Generation"
        assert payload["message"] == "Starting image generation"
        assert payload["level"] == "info"
        assert "id" in payload
        assert "timestamp" in payload

    @pytest.mark.asyncio
    @patch('mobius.api.websocket_handlers.connection_manager')
    async def test_broadcast_status_change(self, mock_manager):
        """Test broadcasting status changes."""
        job_id = "test-job-123"
        status = "processing"
        progress = 50.0
        current_step = "Generating image"
        
        mock_manager.send_to_job = AsyncMock()
        
        await broadcast_status_change(job_id, status, progress, current_step)
        
        # Verify message was sent with correct format
        mock_manager.send_to_job.assert_called_once()
        call_args = mock_manager.send_to_job.call_args
        
        assert call_args[0][0] == job_id
        message = call_args[0][1]
        
        assert message["type"] == "status_change"
        assert message["jobId"] == job_id
        assert "timestamp" in message
        
        payload = message["payload"]
        assert payload["jobId"] == job_id
        assert payload["status"] == status
        assert payload["progress"] == progress
        assert payload["currentStep"] == current_step


class TestWebSocketMessageValidation:
    """Test WebSocket message validation and error handling."""

    @pytest.fixture
    def manager(self):
        return WebSocketConnectionManager()

    @pytest.mark.asyncio
    async def test_connection_failure_cleanup(self, manager):
        """Test cleanup when WebSocket connection fails."""
        job_id = "test-job-123"
        
        # Mock websocket that fails to send
        failing_ws = Mock()
        failing_ws.accept = AsyncMock()
        failing_ws.send_text = AsyncMock(side_effect=Exception("Connection failed"))
        
        # Connect websocket
        await manager.connect(failing_ws, job_id)
        assert manager.get_job_connection_count(job_id) == 1
        
        # Try to send message (should handle failure gracefully)
        message = {"type": "test", "jobId": job_id, "payload": {}}
        await manager.send_to_job(job_id, message)
        
        # Verify failed connection was cleaned up
        assert manager.get_job_connection_count(job_id) == 0

    def test_empty_manager_state(self):
        """Test manager with no connections."""
        manager = WebSocketConnectionManager()
        
        assert manager.get_total_connections() == 0
        assert manager.get_job_connection_count("any-job") == 0
        assert len(manager.job_connections) == 0
        assert len(manager.connection_jobs) == 0