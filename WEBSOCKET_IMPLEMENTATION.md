# WebSocket Implementation for Real-Time Communication (Task 3.1)

## Overview

This document describes the comprehensive WebSocket implementation for the surgery scheduling system, providing real-time communication capabilities including schedule updates, optimization progress streaming, conflict notifications, and user presence tracking.

## Architecture

### Core Components

1. **WebSocket Manager** (`websocket_manager.py`)
   - Central hub for managing WebSocket connections
   - Handles connection lifecycle, message broadcasting, and user presence
   - Provides connection pooling and cleanup mechanisms

2. **WebSocket Models** (`api/models.py`)
   - Pydantic models for structured WebSocket messages
   - Type-safe message definitions for different event types
   - Comprehensive message validation and serialization

3. **WebSocket Router** (`api/routers/websockets.py`)
   - FastAPI router with WebSocket endpoints
   - Authentication and authorization for WebSocket connections
   - REST API endpoints for WebSocket management

4. **Progress Callback** (`websocket_progress_callback.py`)
   - Real-time optimization progress streaming
   - Integration with optimization engines
   - Performance metrics and status updates

## Features

### 1. Connection Management

- **Authenticated Connections**: JWT-based authentication for WebSocket connections
- **User Tracking**: Track active users and their connection status
- **Role-Based Access**: Support for role-based message targeting
- **Connection Pooling**: Efficient management of multiple connections per user
- **Heartbeat Monitoring**: Automatic detection and cleanup of stale connections

### 2. Message Broadcasting

- **Targeted Broadcasting**: Send messages to specific users or roles
- **Broadcast Patterns**: Support for unicast, multicast, and broadcast messaging
- **Message History**: Maintain message history for debugging and replay
- **Delivery Confirmation**: Optional message acknowledgment system

### 3. Real-Time Notifications

#### Schedule Updates
```python
await websocket_manager.broadcast_schedule_update(
    user_id=1,
    action="create",
    surgery_id=123,
    room_id=1,
    schedule_date="2024-01-15",
    changes={"start_time": "09:00"},
    affected_surgeries=[124, 125]
)
```

#### Optimization Progress
```python
await websocket_manager.broadcast_optimization_progress(
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
```

#### Conflict Notifications
```python
await websocket_manager.broadcast_conflict_notification(
    conflict_id="conflict-123",
    conflict_type="room_overlap",
    severity="critical",
    description="Room scheduling conflict detected",
    affected_surgeries=[123, 124],
    suggested_actions=["Reschedule one surgery"]
)
```

#### Emergency Alerts
```python
await websocket_manager.broadcast_emergency_alert(
    user_id=1,
    emergency_id="emergency-456",
    emergency_type="trauma",
    priority="immediate",
    description="Emergency trauma surgery required",
    surgery_id=789,
    patient_name="John Doe",
    surgery_type="Emergency Surgery"
)
```

### 4. User Presence Tracking

- **Real-Time Presence**: Track user online/offline status
- **Activity Monitoring**: Monitor user activity and current page
- **Presence Broadcasting**: Notify other users of presence changes
- **Session Management**: Handle multiple sessions per user

### 5. System Notifications

- **Targeted Notifications**: Send notifications to specific users or roles
- **Severity Levels**: Support for different notification severities
- **Action Items**: Include actionable items in notifications
- **Expiration**: Support for time-based notification expiration

## API Endpoints

### WebSocket Connection
```
WS /api/ws/ws?token=<jwt_token>
```

### REST Endpoints

- `POST /api/ws/broadcast` - Broadcast message to connected clients
- `GET /api/ws/connections` - Get active WebSocket connections
- `GET /api/ws/connections/user/{user_id}` - Get connections for specific user
- `GET /api/ws/users/active` - Get list of active users
- `GET /api/ws/statistics` - Get WebSocket statistics
- `POST /api/ws/cleanup` - Manually cleanup stale connections
- `POST /api/ws/notify/system` - Send system notification

## Message Types

### 1. Schedule Update Messages
```json
{
  "type": "schedule_update",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": 1,
  "data": {
    "action": "create",
    "surgery_id": 123,
    "room_id": 1,
    "schedule_date": "2024-01-15",
    "changes": {"start_time": "09:00"},
    "affected_surgeries": [124, 125]
  }
}
```

### 2. Optimization Progress Messages
```json
{
  "type": "optimization_progress",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": 1,
  "data": {
    "optimization_id": "opt-123",
    "progress_percentage": 50.0,
    "current_iteration": 50,
    "total_iterations": 100,
    "current_score": 85.5,
    "best_score": 90.2,
    "time_elapsed": 30.0,
    "status": "running"
  }
}
```

### 3. Conflict Notification Messages
```json
{
  "type": "conflict_notification",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "conflict_id": "conflict-123",
    "conflict_type": "room_overlap",
    "severity": "critical",
    "description": "Room scheduling conflict detected",
    "affected_surgeries": [123, 124],
    "suggested_actions": ["Reschedule one surgery"]
  }
}
```

### 4. User Presence Messages
```json
{
  "type": "user_presence",
  "timestamp": "2024-01-15T10:30:00Z",
  "data": {
    "user_id": 1,
    "action": "join",
    "username": "john_doe",
    "role": "admin",
    "current_page": "/schedule",
    "connection_id": "conn-123"
  }
}
```

### 5. Emergency Alert Messages
```json
{
  "type": "emergency_alert",
  "timestamp": "2024-01-15T10:30:00Z",
  "user_id": 1,
  "data": {
    "emergency_id": "emergency-456",
    "emergency_type": "trauma",
    "priority": "immediate",
    "description": "Emergency trauma surgery required",
    "surgery_id": 789,
    "patient_name": "John Doe",
    "surgery_type": "Emergency Surgery"
  }
}
```

## Client-Side Integration

### JavaScript WebSocket Client Example

```javascript
class SurgerySchedulerWebSocket {
    constructor(token) {
        this.token = token;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        const wsUrl = `ws://localhost:8000/api/ws/ws?token=${this.token}`;
        this.ws = new WebSocket(wsUrl);

        this.ws.onopen = () => {
            console.log('WebSocket connected');
            this.reconnectAttempts = 0;
            this.startHeartbeat();
        };

        this.ws.onmessage = (event) => {
            const message = JSON.parse(event.data);
            this.handleMessage(message);
        };

        this.ws.onclose = () => {
            console.log('WebSocket disconnected');
            this.reconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleMessage(message) {
        switch (message.type) {
            case 'schedule_update':
                this.handleScheduleUpdate(message.data);
                break;
            case 'optimization_progress':
                this.handleOptimizationProgress(message.data);
                break;
            case 'conflict_notification':
                this.handleConflictNotification(message.data);
                break;
            case 'user_presence':
                this.handleUserPresence(message.data);
                break;
            case 'emergency_alert':
                this.handleEmergencyAlert(message.data);
                break;
            case 'system_notification':
                this.handleSystemNotification(message.data);
                break;
        }
    }

    sendHeartbeat() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'heartbeat',
                data: {
                    current_page: window.location.pathname,
                    active_schedule_date: this.getCurrentScheduleDate()
                }
            }));
        }
    }

    startHeartbeat() {
        setInterval(() => this.sendHeartbeat(), 30000); // Every 30 seconds
    }
}
```

## Performance Considerations

### Connection Management
- **Connection Pooling**: Efficient management of multiple connections
- **Memory Usage**: Optimized data structures for connection tracking
- **Cleanup**: Automatic cleanup of stale connections

### Message Broadcasting
- **Batch Processing**: Efficient message broadcasting to multiple recipients
- **Message Queuing**: Queue messages for offline users
- **Rate Limiting**: Prevent message flooding

### Scalability
- **Horizontal Scaling**: Support for multiple server instances
- **Load Balancing**: Distribute WebSocket connections across servers
- **State Management**: Shared state management for multi-instance deployments

## Security

### Authentication
- **JWT Tokens**: Secure authentication using JWT tokens
- **Token Validation**: Validate tokens on connection and periodically
- **Role-Based Access**: Restrict message access based on user roles

### Authorization
- **Message Filtering**: Filter messages based on user permissions
- **Data Sanitization**: Sanitize message content before broadcasting
- **Rate Limiting**: Prevent abuse through rate limiting

## Testing

The implementation includes comprehensive tests covering:

- **Unit Tests**: Individual component testing
- **Integration Tests**: End-to-end WebSocket communication
- **Performance Tests**: Load testing and performance validation
- **Security Tests**: Authentication and authorization testing

Run tests with:
```bash
python test_websocket_simple.py
python -m pytest test_websocket_implementation.py -v
```

## Deployment

### Environment Variables
```env
WEBSOCKET_HEARTBEAT_INTERVAL=30
WEBSOCKET_CONNECTION_TIMEOUT=120
WEBSOCKET_MAX_CONNECTIONS=1000
WEBSOCKET_MESSAGE_HISTORY_SIZE=1000
```

### Production Considerations
- **Load Balancing**: Use sticky sessions for WebSocket connections
- **Monitoring**: Monitor connection counts and message throughput
- **Logging**: Comprehensive logging for debugging and monitoring
- **Error Handling**: Robust error handling and recovery mechanisms

## Future Enhancements

1. **Message Persistence**: Store messages for offline users
2. **Advanced Filtering**: More sophisticated message filtering
3. **Analytics**: Real-time analytics and monitoring dashboard
4. **Mobile Support**: Enhanced mobile WebSocket support
5. **Clustering**: Support for WebSocket clustering and federation
