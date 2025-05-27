"""
Simple test script for WebSocket implementation.
"""

import asyncio
import json
from unittest.mock import Mock, AsyncMock

def test_websocket_manager_basic():
    """Test basic WebSocket manager functionality."""
    try:
        from websocket_manager import WebSocketManager, WebSocketConnection
        
        # Test WebSocketConnection creation
        mock_websocket = Mock()
        mock_websocket.send_text = AsyncMock()
        
        connection = WebSocketConnection(
            websocket=mock_websocket,
            connection_id="test-123",
            user_id=1,
            username="testuser",
            role="admin"
        )
        
        assert connection.connection_id == "test-123"
        assert connection.user_id == 1
        assert connection.username == "testuser"
        assert connection.role == "admin"
        print("✓ WebSocketConnection creation test passed")
        
        # Test WebSocketManager creation
        manager = WebSocketManager()
        assert len(manager.connections) == 0
        assert len(manager.user_connections) == 0
        assert len(manager.role_connections) == 0
        print("✓ WebSocketManager creation test passed")
        
        # Test connection info serialization
        info_dict = connection.to_dict()
        assert info_dict["connection_id"] == "test-123"
        assert info_dict["user_id"] == 1
        print("✓ Connection serialization test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ WebSocket manager test failed: {e}")
        return False


def test_websocket_models():
    """Test WebSocket models."""
    try:
        from api.models import (
            WebSocketMessageType, WebSocketMessage, ScheduleUpdateMessage,
            OptimizationProgressMessage, ConflictNotificationMessage
        )
        
        # Test message type enum
        assert WebSocketMessageType.SCHEDULE_UPDATE == "schedule_update"
        assert WebSocketMessageType.OPTIMIZATION_PROGRESS == "optimization_progress"
        print("✓ WebSocket message types test passed")
        
        # Test schedule update message
        schedule_msg = ScheduleUpdateMessage(
            user_id=1,
            action="create",
            surgery_id=123,
            room_id=1,
            changes={"start_time": "09:00"}
        )
        
        assert schedule_msg.user_id == 1
        assert schedule_msg.action == "create"
        assert schedule_msg.surgery_id == 123
        print("✓ ScheduleUpdateMessage test passed")
        
        # Test optimization progress message
        progress_msg = OptimizationProgressMessage(
            user_id=1,
            optimization_id="opt-123",
            progress_percentage=50.0,
            current_iteration=50,
            total_iterations=100,
            time_elapsed=30.0,
            status="running"
        )
        
        assert progress_msg.optimization_id == "opt-123"
        assert progress_msg.progress_percentage == 50.0
        assert progress_msg.current_iteration == 50
        print("✓ OptimizationProgressMessage test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ WebSocket models test failed: {e}")
        return False


def test_websocket_progress_callback():
    """Test WebSocket progress callback."""
    try:
        from websocket_progress_callback import WebSocketProgressCallback
        
        callback = WebSocketProgressCallback(
            optimization_id="opt-123",
            user_id=1,
            total_iterations=100,
            update_interval=10
        )
        
        assert callback.optimization_id == "opt-123"
        assert callback.user_id == 1
        assert callback.total_iterations == 100
        assert callback.current_phase == "initialization"
        print("✓ WebSocketProgressCallback creation test passed")
        
        # Test progress summary
        summary = callback.get_progress_summary()
        assert summary["optimization_id"] == "opt-123"
        assert summary["user_id"] == 1
        print("✓ Progress summary test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ WebSocket progress callback test failed: {e}")
        return False


async def test_websocket_async_operations():
    """Test async WebSocket operations."""
    try:
        from websocket_manager import WebSocketManager
        
        manager = WebSocketManager()
        
        # Create mock websocket
        mock_websocket = Mock()
        mock_websocket.accept = AsyncMock()
        mock_websocket.send_text = AsyncMock()
        
        # Test connection
        connection_id = await manager.connect(
            websocket=mock_websocket,
            user_id=1,
            username="testuser",
            role="admin"
        )
        
        assert connection_id in manager.connections
        assert 1 in manager.user_connections
        assert "admin" in manager.role_connections
        print("✓ Async connection test passed")
        
        # Test message sending
        message = {"type": "test", "data": {"message": "hello"}}
        sent_count = await manager.send_to_user(1, message)
        assert sent_count == 1
        print("✓ Async message sending test passed")
        
        # Test disconnection
        await manager.disconnect(connection_id)
        assert connection_id not in manager.connections
        print("✓ Async disconnection test passed")
        
        return True
        
    except Exception as e:
        print(f"✗ Async WebSocket operations test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Running WebSocket implementation tests...\n")
    
    tests = [
        ("WebSocket Manager Basic", test_websocket_manager_basic),
        ("WebSocket Models", test_websocket_models),
        ("WebSocket Progress Callback", test_websocket_progress_callback),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED\n")
        else:
            print(f"✗ {test_name} FAILED\n")
    
    # Run async test
    print("Running Async WebSocket Operations...")
    try:
        result = asyncio.run(test_websocket_async_operations())
        if result:
            passed += 1
            print("✓ Async WebSocket Operations PASSED\n")
        else:
            print("✗ Async WebSocket Operations FAILED\n")
        total += 1
    except Exception as e:
        print(f"✗ Async WebSocket Operations FAILED: {e}\n")
        total += 1
    
    print(f"Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! WebSocket implementation is working correctly.")
        return True
    else:
        print("❌ Some tests failed. Please check the implementation.")
        return False


if __name__ == "__main__":
    main()
