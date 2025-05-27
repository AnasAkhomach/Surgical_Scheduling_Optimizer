"""
Tests for WebSocket Implementation (Task 3.1).

This module tests the WebSocket functionality including:
- Connection management and authentication
- Message broadcasting
- User presence tracking
- Real-time notifications
- Progress streaming
"""

import pytest
import asyncio
import json
import time
import uuid
from datetime import datetime, timedelta
from unittest.mock import Mock, AsyncMock, patch
from fastapi.testclient import TestClient
from fastapi import WebSocket

from websocket_manager import WebSocketManager, WebSocketConnection, websocket_manager
from websocket_progress_callback import WebSocketProgressCallback
from api.models import (
    WebSocketMessageType, WebSocketBroadcastRequest, ScheduleUpdateMessage,
    OptimizationProgressMessage, ConflictNotificationMessage, UserPresenceMessage
)


class TestWebSocketConnection:
    """Test cases for WebSocketConnection class."""

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        websocket = Mock(spec=WebSocket)
        websocket.send_text = AsyncMock()
        return websocket

    @pytest.fixture
    def websocket_connection(self, mock_websocket):
        """Create a WebSocketConnection instance."""
        return WebSocketConnection(
            websocket=mock_websocket,
            connection_id="test-connection-123",
            user_id=1,
            username="testuser",
            role="admin"
        )

    def test_connection_initialization(self, websocket_connection):
        """Test WebSocket connection initialization."""
        assert websocket_connection.connection_id == "test-connection-123"
        assert websocket_connection.user_id == 1
        assert websocket_connection.username == "testuser"
        assert websocket_connection.role == "admin"
        assert websocket_connection.is_active is True
        assert isinstance(websocket_connection.connected_at, datetime)

    @pytest.mark.asyncio
    async def test_send_message_success(self, websocket_connection):
        """Test successful message sending."""
        message = {"type": "test", "data": {"message": "hello"}}

        result = await websocket_connection.send_message(message)

        assert result is True
        websocket_connection.websocket.send_text.assert_called_once()
        call_args = websocket_connection.websocket.send_text.call_args[0][0]
        sent_message = json.loads(call_args)
        assert sent_message["type"] == "test"
        assert sent_message["data"]["message"] == "hello"

    @pytest.mark.asyncio
    async def test_send_message_failure(self, websocket_connection):
        """Test message sending failure."""
        websocket_connection.websocket.send_text.side_effect = Exception("Connection lost")

        message = {"type": "test", "data": {"message": "hello"}}
        result = await websocket_connection.send_message(message)

        assert result is False

    def test_update_heartbeat(self, websocket_connection):
        """Test heartbeat update."""
        original_heartbeat = websocket_connection.last_heartbeat
        original_activity = websocket_connection.last_activity

        websocket_connection.update_heartbeat()

        assert websocket_connection.last_heartbeat > original_heartbeat
        assert websocket_connection.last_activity > original_activity

    def test_update_activity(self, websocket_connection):
        """Test activity update."""
        websocket_connection.update_activity(
            page="/schedule",
            schedule_date="2024-01-15"
        )

        assert websocket_connection.current_page == "/schedule"
        assert websocket_connection.active_schedule_date == "2024-01-15"

    def test_to_dict(self, websocket_connection):
        """Test connection info serialization."""
        info_dict = websocket_connection.to_dict()

        assert info_dict["connection_id"] == "test-connection-123"
        assert info_dict["user_id"] == 1
        assert info_dict["username"] == "testuser"
        assert info_dict["role"] == "admin"
        assert info_dict["is_active"] is True


class TestWebSocketManager:
    """Test cases for WebSocketManager class."""

    @pytest.fixture
    def manager(self):
        """Create a fresh WebSocketManager instance."""
        return WebSocketManager()

    @pytest.fixture
    def mock_websocket(self):
        """Create a mock WebSocket."""
        websocket = Mock(spec=WebSocket)
        websocket.accept = AsyncMock()
        websocket.send_text = AsyncMock()
        return websocket

    @pytest.mark.asyncio
    async def test_connect_user(self, manager, mock_websocket):
        """Test user connection."""
        connection_id = await manager.connect(
            websocket=mock_websocket,
            user_id=1,
            username="testuser",
            role="admin"
        )

        assert connection_id in manager.connections
        assert 1 in manager.user_connections
        assert "admin" in manager.role_connections
        assert manager.total_connections == 1

        # Verify welcome message was sent
        mock_websocket.send_text.assert_called()

    @pytest.mark.asyncio
    async def test_disconnect_user(self, manager, mock_websocket):
        """Test user disconnection."""
        # First connect
        connection_id = await manager.connect(
            websocket=mock_websocket,
            user_id=1,
            username="testuser",
            role="admin"
        )

        # Then disconnect
        await manager.disconnect(connection_id)

        assert connection_id not in manager.connections
        assert 1 not in manager.user_connections
        assert "admin" not in manager.role_connections

    @pytest.mark.asyncio
    async def test_send_to_user(self, manager, mock_websocket):
        """Test sending message to specific user."""
        # Connect user
        connection_id = await manager.connect(
            websocket=mock_websocket,
            user_id=1,
            username="testuser"
        )

        # Send message
        message = {"type": "test", "data": {"message": "hello"}}
        sent_count = await manager.send_to_user(1, message)

        assert sent_count == 1
        assert manager.total_messages_sent > 0

    @pytest.mark.asyncio
    async def test_send_to_role(self, manager, mock_websocket):
        """Test sending message to specific role."""
        # Connect users with same role
        await manager.connect(mock_websocket, 1, "user1", "admin")
        await manager.connect(mock_websocket, 2, "user2", "admin")

        # Send message to role
        message = {"type": "test", "data": {"message": "hello"}}
        sent_count = await manager.send_to_role("admin", message)

        assert sent_count == 2

    @pytest.mark.asyncio
    async def test_broadcast_to_all(self, manager, mock_websocket):
        """Test broadcasting to all connected users."""
        # Connect multiple users
        await manager.connect(mock_websocket, 1, "user1", "admin")
        await manager.connect(mock_websocket, 2, "user2", "user")

        # Broadcast message
        message = {"type": "test", "data": {"message": "hello"}}
        sent_count = await manager.broadcast_to_all(message)

        assert sent_count == 2

    @pytest.mark.asyncio
    async def test_broadcast_schedule_update(self, manager, mock_websocket):
        """Test broadcasting schedule update."""
        # Connect user
        await manager.connect(mock_websocket, 1, "testuser")

        # Broadcast schedule update
        result = await manager.broadcast_schedule_update(
            user_id=1,
            action="create",
            surgery_id=123,
            room_id=1,
            schedule_date="2024-01-15",
            changes={"start_time": "09:00"},
            affected_surgeries=[124, 125]
        )

        assert result["sent_count"] == 1
        assert "message_id" in result

    @pytest.mark.asyncio
    async def test_broadcast_optimization_progress(self, manager, mock_websocket):
        """Test broadcasting optimization progress."""
        # Connect user
        await manager.connect(mock_websocket, 1, "testuser")

        # Broadcast progress
        result = await manager.broadcast_optimization_progress(
            user_id=1,
            optimization_id="opt-123",
            progress_percentage=50.0,
            current_iteration=50,
            total_iterations=100,
            current_score=85.5,
            best_score=90.2,
            time_elapsed=30.0,
            status="running"
        )

        assert result["sent_count"] == 1

    @pytest.mark.asyncio
    async def test_broadcast_conflict_notification(self, manager, mock_websocket):
        """Test broadcasting conflict notification."""
        # Connect user
        await manager.connect(mock_websocket, 1, "testuser")

        # Broadcast conflict
        result = await manager.broadcast_conflict_notification(
            conflict_id="conflict-123",
            conflict_type="room_overlap",
            severity="critical",
            description="Room scheduling conflict detected",
            affected_surgeries=[123, 124],
            affected_rooms=[1],
            suggested_actions=["Reschedule one surgery", "Use alternative room"]
        )

        assert result["sent_count"] == 1

    @pytest.mark.asyncio
    async def test_handle_heartbeat(self, manager, mock_websocket):
        """Test heartbeat handling."""
        # Connect user
        connection_id = await manager.connect(mock_websocket, 1, "testuser")

        # Send heartbeat
        heartbeat_data = {
            "current_page": "/schedule",
            "active_schedule_date": "2024-01-15"
        }
        result = await manager.handle_heartbeat(connection_id, heartbeat_data)

        assert result is True

        # Check that activity was updated
        connection = manager.connections[connection_id]
        assert connection.current_page == "/schedule"
        assert connection.active_schedule_date == "2024-01-15"

    @pytest.mark.asyncio
    async def test_cleanup_stale_connections(self, manager, mock_websocket):
        """Test cleanup of stale connections."""
        # Connect user
        connection_id = await manager.connect(mock_websocket, 1, "testuser")

        # Manually set old heartbeat time
        connection = manager.connections[connection_id]
        connection.last_heartbeat = datetime.now() - timedelta(minutes=5)

        # Set short timeout for testing
        manager.connection_timeout = 60  # 1 minute

        # Run cleanup
        removed_count = await manager.cleanup_stale_connections()

        assert removed_count == 1
        assert connection_id not in manager.connections

    def test_get_active_users(self, manager):
        """Test getting active users list."""
        # This is a synchronous test since we're not testing WebSocket operations
        # We'll manually add connections to test the logic

        # Create mock connections
        conn1 = Mock()
        conn1.user_id = 1
        conn1.username = "user1"
        conn1.role = "admin"
        conn1.last_activity = datetime.now()
        conn1.current_page = "/schedule"
        conn1.active_schedule_date = "2024-01-15"

        conn2 = Mock()
        conn2.user_id = 2
        conn2.username = "user2"
        conn2.role = "user"
        conn2.last_activity = datetime.now()
        conn2.current_page = "/dashboard"
        conn2.active_schedule_date = None

        manager.connections = {"conn1": conn1, "conn2": conn2}

        active_users = manager.get_active_users()

        assert len(active_users) == 2
        assert any(user["username"] == "user1" for user in active_users)
        assert any(user["username"] == "user2" for user in active_users)

    def test_get_statistics(self, manager):
        """Test getting WebSocket statistics."""
        # Add some mock data
        manager.total_connections = 10
        manager.total_messages_sent = 100
        manager.connections = {"conn1": Mock(), "conn2": Mock()}
        manager.user_connections = {1: {"conn1"}, 2: {"conn2"}}
        manager.role_connections = {"admin": {"conn1"}, "user": {"conn2"}}

        stats = manager.get_statistics()

        assert stats["active_connections"] == 2
        assert stats["total_connections"] == 10
        assert stats["total_messages_sent"] == 100
        assert stats["active_users"] == 2
        assert "admin" in stats["active_roles"]
        assert "user" in stats["active_roles"]


class TestWebSocketProgressCallback:
    """Test cases for WebSocketProgressCallback class."""

    @pytest.fixture
    def progress_callback(self):
        """Create a WebSocketProgressCallback instance."""
        return WebSocketProgressCallback(
            optimization_id="opt-123",
            user_id=1,
            total_iterations=100,
            update_interval=10
        )

    def test_initialization(self, progress_callback):
        """Test progress callback initialization."""
        assert progress_callback.optimization_id == "opt-123"
        assert progress_callback.user_id == 1
        assert progress_callback.total_iterations == 100
        assert progress_callback.update_interval == 10
        assert progress_callback.current_phase == "initialization"

    @pytest.mark.asyncio
    async def test_on_iteration_complete(self, progress_callback):
        """Test iteration completion handling."""
        with patch.object(websocket_manager, 'broadcast_optimization_progress') as mock_broadcast:
            mock_broadcast.return_value = {"sent_count": 1}

            # Test update on interval
            await progress_callback.on_iteration_complete(
                iteration=10,
                current_score=85.5,
                best_score=90.2
            )

            mock_broadcast.assert_called_once()
            call_args = mock_broadcast.call_args[1]
            assert call_args["optimization_id"] == "opt-123"
            assert call_args["current_iteration"] == 10
            assert call_args["progress_percentage"] == 10.0

    @pytest.mark.asyncio
    async def test_on_phase_change(self, progress_callback):
        """Test phase change handling."""
        with patch.object(websocket_manager, 'broadcast_optimization_progress') as mock_broadcast:
            mock_broadcast.return_value = {"sent_count": 1}

            await progress_callback.on_phase_change(
                phase="diversification",
                current_score=85.5,
                best_score=90.2
            )

            assert progress_callback.current_phase == "diversification"
            mock_broadcast.assert_called_once()

    @pytest.mark.asyncio
    async def test_on_optimization_complete(self, progress_callback):
        """Test optimization completion handling."""
        with patch.object(websocket_manager, 'broadcast_optimization_progress') as mock_progress:
            with patch.object(websocket_manager, 'broadcast_system_notification') as mock_notification:
                mock_progress.return_value = {"sent_count": 1}
                mock_notification.return_value = {"sent_count": 1}

                await progress_callback.on_optimization_complete(
                    final_score=92.5,
                    total_iterations=100
                )

                assert progress_callback.current_phase == "completed"
                mock_progress.assert_called_once()
                mock_notification.assert_called_once()

                # Check notification content
                notification_args = mock_notification.call_args[1]
                assert notification_args["title"] == "Optimization Complete"
                assert "92.5" in notification_args["message"]

    def test_get_progress_summary(self, progress_callback):
        """Test progress summary generation."""
        # Add some mock data
        progress_callback.last_update_iteration = 50
        progress_callback.iterations_per_second = 2.5
        progress_callback.best_score_history = [
            {"iteration": 10, "score": 85.0, "timestamp": time.time()},
            {"iteration": 20, "score": 87.5, "timestamp": time.time()}
        ]

        summary = progress_callback.get_progress_summary()

        assert summary["optimization_id"] == "opt-123"
        assert summary["user_id"] == 1
        assert summary["last_iteration"] == 50
        assert summary["iterations_per_second"] == 2.5
        assert len(summary["best_score_history"]) == 2


if __name__ == "__main__":
    # Run the tests
    pytest.main([__file__, "-v"])
