"""
WebSocket Manager for Task 3.1.

This module provides comprehensive WebSocket management including:
- Connection management and authentication
- Real-time message broadcasting
- User presence tracking
- Schedule change notifications
- Optimization progress streaming
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Any
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from api.models import (
    WebSocketMessageType, WebSocketMessage, ScheduleUpdateMessage,
    OptimizationProgressMessage, ConflictNotificationMessage,
    UserPresenceMessage, EmergencyAlertMessage, SystemNotificationMessage,
    WebSocketConnectionInfo, WebSocketBroadcastRequest
)
from models import User

logger = logging.getLogger(__name__)


class WebSocketConnection:
    """Represents a single WebSocket connection."""

    def __init__(
        self,
        websocket: WebSocket,
        connection_id: str,
        user_id: int,
        username: str,
        role: Optional[str] = None
    ):
        self.websocket = websocket
        self.connection_id = connection_id
        self.user_id = user_id
        self.username = username
        self.role = role
        self.connected_at = datetime.now()
        self.last_heartbeat = datetime.now()
        self.last_activity = datetime.now()
        self.current_page: Optional[str] = None
        self.active_schedule_date: Optional[str] = None
        self.is_active = True

    async def send_message(self, message: Dict[str, Any]) -> bool:
        """Send a message to this connection."""
        try:
            await self.websocket.send_text(json.dumps(message, default=str))
            return True
        except Exception as e:
            logger.error(f"Error sending message to connection {self.connection_id}: {e}")
            return False

    def update_heartbeat(self):
        """Update the last heartbeat timestamp."""
        self.last_heartbeat = datetime.now()
        self.last_activity = datetime.now()

    def update_activity(self, page: Optional[str] = None, schedule_date: Optional[str] = None):
        """Update user activity information."""
        self.last_activity = datetime.now()
        if page is not None:
            self.current_page = page
        if schedule_date is not None:
            self.active_schedule_date = schedule_date

    def to_dict(self) -> Dict[str, Any]:
        """Convert connection info to dictionary."""
        return {
            "connection_id": self.connection_id,
            "user_id": self.user_id,
            "username": self.username,
            "role": self.role,
            "connected_at": self.connected_at,
            "last_heartbeat": self.last_heartbeat,
            "last_activity": self.last_activity,
            "current_page": self.current_page,
            "active_schedule_date": self.active_schedule_date,
            "is_active": self.is_active
        }


class WebSocketManager:
    """Manages WebSocket connections and message broadcasting."""

    def __init__(self):
        # Connection management
        self.connections: Dict[str, WebSocketConnection] = {}
        self.user_connections: Dict[int, Set[str]] = {}  # user_id -> set of connection_ids
        self.role_connections: Dict[str, Set[str]] = {}  # role -> set of connection_ids

        # Message queues and history
        self.message_history: List[Dict[str, Any]] = []
        self.max_history_size = 1000

        # Heartbeat management
        self.heartbeat_interval = 30  # seconds
        self.connection_timeout = 120  # seconds

        # Statistics
        self.total_connections = 0
        self.total_messages_sent = 0

        logger.info("WebSocket manager initialized")

    async def connect(
        self,
        websocket: WebSocket,
        user_id: int,
        username: str,
        role: Optional[str] = None
    ) -> str:
        """Accept a new WebSocket connection."""
        await websocket.accept()

        connection_id = str(uuid.uuid4())
        connection = WebSocketConnection(websocket, connection_id, user_id, username, role)

        # Store connection
        self.connections[connection_id] = connection

        # Update user connections mapping
        if user_id not in self.user_connections:
            self.user_connections[user_id] = set()
        self.user_connections[user_id].add(connection_id)

        # Update role connections mapping
        if role:
            if role not in self.role_connections:
                self.role_connections[role] = set()
            self.role_connections[role].add(connection_id)

        self.total_connections += 1

        logger.info(f"WebSocket connection established: {connection_id} for user {username} ({user_id})")

        # Send welcome message
        welcome_message = {
            "type": WebSocketMessageType.SYSTEM_NOTIFICATION,
            "timestamp": datetime.now(),
            "data": {
                "title": "Connected",
                "message": "WebSocket connection established successfully",
                "severity": "success"
            },
            "message_id": str(uuid.uuid4())
        }
        await connection.send_message(welcome_message)

        # Broadcast user presence
        await self.broadcast_user_presence(user_id, "join", connection_id)

        return connection_id

    async def disconnect(self, connection_id: str):
        """Handle WebSocket disconnection."""
        if connection_id not in self.connections:
            return

        connection = self.connections[connection_id]
        user_id = connection.user_id
        role = connection.role

        # Remove from connections
        del self.connections[connection_id]

        # Update user connections mapping
        if user_id in self.user_connections:
            self.user_connections[user_id].discard(connection_id)
            if not self.user_connections[user_id]:
                del self.user_connections[user_id]

        # Update role connections mapping
        if role and role in self.role_connections:
            self.role_connections[role].discard(connection_id)
            if not self.role_connections[role]:
                del self.role_connections[role]

        logger.info(f"WebSocket connection closed: {connection_id} for user {connection.username}")

        # Broadcast user presence
        await self.broadcast_user_presence(user_id, "leave", connection_id)

    async def send_to_connection(self, connection_id: str, message: Dict[str, Any]) -> bool:
        """Send a message to a specific connection."""
        if connection_id not in self.connections:
            return False

        connection = self.connections[connection_id]
        success = await connection.send_message(message)

        if success:
            self.total_messages_sent += 1
            self._add_to_history(message)

        return success

    async def send_to_user(self, user_id: int, message: Dict[str, Any]) -> int:
        """Send a message to all connections of a specific user."""
        if user_id not in self.user_connections:
            return 0

        sent_count = 0
        for connection_id in self.user_connections[user_id].copy():
            if await self.send_to_connection(connection_id, message):
                sent_count += 1

        return sent_count

    async def send_to_role(self, role: str, message: Dict[str, Any]) -> int:
        """Send a message to all connections of a specific role."""
        if role not in self.role_connections:
            return 0

        sent_count = 0
        for connection_id in self.role_connections[role].copy():
            if await self.send_to_connection(connection_id, message):
                sent_count += 1

        return sent_count

    async def broadcast_to_all(self, message: Dict[str, Any]) -> int:
        """Broadcast a message to all connected clients."""
        sent_count = 0
        for connection_id in list(self.connections.keys()):
            if await self.send_to_connection(connection_id, message):
                sent_count += 1

        return sent_count

    async def broadcast_message(self, request: WebSocketBroadcastRequest) -> Dict[str, Any]:
        """Broadcast a message based on targeting criteria."""
        message = {
            "type": request.message_type,
            "timestamp": datetime.now(),
            "data": request.message_data,
            "message_id": str(uuid.uuid4()),
            "sender_user_id": request.sender_user_id
        }

        sent_count = 0
        target_connections = set()

        # Determine target connections
        if request.target_users:
            # Send to specific users
            for user_id in request.target_users:
                if user_id in self.user_connections:
                    target_connections.update(self.user_connections[user_id])
        elif request.target_roles:
            # Send to specific roles
            for role in request.target_roles:
                if role in self.role_connections:
                    target_connections.update(self.role_connections[role])
        else:
            # Send to all connections
            target_connections = set(self.connections.keys())

        # Exclude specific users if requested
        if request.exclude_users:
            for user_id in request.exclude_users:
                if user_id in self.user_connections:
                    target_connections -= self.user_connections[user_id]

        # Send messages
        for connection_id in target_connections:
            if await self.send_to_connection(connection_id, message):
                sent_count += 1

        return {
            "message_id": message["message_id"],
            "sent_count": sent_count,
            "target_count": len(target_connections),
            "timestamp": message["timestamp"]
        }

    async def broadcast_schedule_update(
        self,
        user_id: int,
        action: str,
        surgery_id: Optional[int] = None,
        room_id: Optional[int] = None,
        schedule_date: Optional[str] = None,
        changes: Optional[Dict[str, Any]] = None,
        affected_surgeries: Optional[List[int]] = None
    ):
        """Broadcast a schedule update to all connected clients."""
        message = ScheduleUpdateMessage(
            user_id=user_id,
            action=action,
            surgery_id=surgery_id,
            room_id=room_id,
            schedule_date=schedule_date,
            changes=changes or {},
            affected_surgeries=affected_surgeries or []
        )

        broadcast_request = WebSocketBroadcastRequest(
            message_type=WebSocketMessageType.SCHEDULE_UPDATE,
            message_data=message.model_dump(),
            sender_user_id=user_id
        )

        return await self.broadcast_message(broadcast_request)

    async def broadcast_optimization_progress(
        self,
        user_id: int,
        optimization_id: str,
        progress_percentage: float,
        current_iteration: int,
        total_iterations: int,
        current_score: Optional[float] = None,
        best_score: Optional[float] = None,
        time_elapsed: float = 0,
        estimated_time_remaining: Optional[float] = None,
        status: str = "running",
        phase: Optional[str] = None
    ):
        """Broadcast optimization progress to all connected clients."""
        message = OptimizationProgressMessage(
            user_id=user_id,
            optimization_id=optimization_id,
            progress_percentage=progress_percentage,
            current_iteration=current_iteration,
            total_iterations=total_iterations,
            current_score=current_score,
            best_score=best_score,
            time_elapsed=time_elapsed,
            estimated_time_remaining=estimated_time_remaining,
            status=status,
            phase=phase
        )

        broadcast_request = WebSocketBroadcastRequest(
            message_type=WebSocketMessageType.OPTIMIZATION_PROGRESS,
            message_data=message.model_dump(),
            sender_user_id=user_id
        )

        return await self.broadcast_message(broadcast_request)

    async def broadcast_conflict_notification(
        self,
        conflict_id: str,
        conflict_type: str,
        severity: str,
        description: str,
        affected_surgeries: Optional[List[int]] = None,
        affected_rooms: Optional[List[int]] = None,
        affected_surgeons: Optional[List[int]] = None,
        affected_equipment: Optional[List[int]] = None,
        suggested_actions: Optional[List[str]] = None,
        auto_resolution_available: bool = False,
        user_id: Optional[int] = None
    ):
        """Broadcast a conflict notification to all connected clients."""
        message = ConflictNotificationMessage(
            user_id=user_id,
            conflict_id=conflict_id,
            conflict_type=conflict_type,
            severity=severity,
            description=description,
            affected_surgeries=affected_surgeries or [],
            affected_rooms=affected_rooms or [],
            affected_surgeons=affected_surgeons or [],
            affected_equipment=affected_equipment or [],
            suggested_actions=suggested_actions or [],
            auto_resolution_available=auto_resolution_available
        )

        broadcast_request = WebSocketBroadcastRequest(
            message_type=WebSocketMessageType.CONFLICT_NOTIFICATION,
            message_data=message.model_dump(),
            sender_user_id=user_id
        )

        return await self.broadcast_message(broadcast_request)

    async def broadcast_user_presence(
        self,
        user_id: int,
        action: str,
        connection_id: str,
        current_page: Optional[str] = None,
        active_schedule_date: Optional[str] = None
    ):
        """Broadcast user presence information to all connected clients."""
        connection = self.connections.get(connection_id)
        if not connection:
            return

        message = UserPresenceMessage(
            user_id=user_id,
            action=action,
            username=connection.username,
            role=connection.role,
            current_page=current_page or connection.current_page,
            active_schedule_date=active_schedule_date or connection.active_schedule_date,
            connection_id=connection_id
        )

        broadcast_request = WebSocketBroadcastRequest(
            message_type=WebSocketMessageType.USER_PRESENCE,
            message_data=message.model_dump(),
            exclude_users=[user_id]  # Don't send to the user themselves
        )

        return await self.broadcast_message(broadcast_request)

    async def broadcast_emergency_alert(
        self,
        user_id: int,
        emergency_id: str,
        emergency_type: str,
        priority: str,
        description: str,
        surgery_id: int,
        patient_name: str,
        surgery_type: str,
        estimated_duration: int,
        requested_time: Optional[datetime] = None,
        assigned_room: Optional[int] = None,
        assigned_surgeon: Optional[int] = None,
        conflicts_detected: bool = False,
        affected_surgeries: Optional[List[int]] = None
    ):
        """Broadcast an emergency alert to all connected clients."""
        message = EmergencyAlertMessage(
            user_id=user_id,
            emergency_id=emergency_id,
            emergency_type=emergency_type,
            priority=priority,
            description=description,
            surgery_id=surgery_id,
            patient_name=patient_name,
            surgery_type=surgery_type,
            estimated_duration=estimated_duration,
            requested_time=requested_time,
            assigned_room=assigned_room,
            assigned_surgeon=assigned_surgeon,
            conflicts_detected=conflicts_detected,
            affected_surgeries=affected_surgeries or []
        )

        broadcast_request = WebSocketBroadcastRequest(
            message_type=WebSocketMessageType.EMERGENCY_ALERT,
            message_data=message.model_dump(),
            sender_user_id=user_id
        )

        return await self.broadcast_message(broadcast_request)

    async def broadcast_system_notification(
        self,
        notification_type: str,
        title: str,
        message: str,
        severity: str = "info",
        target_users: Optional[List[int]] = None,
        target_roles: Optional[List[str]] = None,
        action_required: bool = False,
        action_url: Optional[str] = None,
        action_label: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ):
        """Broadcast a system notification to targeted users."""
        notification = SystemNotificationMessage(
            notification_type=notification_type,
            title=title,
            message=message,
            severity=severity,
            target_users=target_users,
            target_roles=target_roles,
            action_required=action_required,
            action_url=action_url,
            action_label=action_label,
            expires_at=expires_at
        )

        broadcast_request = WebSocketBroadcastRequest(
            message_type=WebSocketMessageType.SYSTEM_NOTIFICATION,
            message_data=notification.model_dump(),
            target_users=target_users,
            target_roles=target_roles
        )

        return await self.broadcast_message(broadcast_request)

    async def handle_heartbeat(self, connection_id: str, data: Optional[Dict[str, Any]] = None):
        """Handle heartbeat from a connection."""
        if connection_id not in self.connections:
            return False

        connection = self.connections[connection_id]
        connection.update_heartbeat()

        # Update activity information if provided
        if data:
            connection.update_activity(
                page=data.get("current_page"),
                schedule_date=data.get("active_schedule_date")
            )

        # Send heartbeat response
        heartbeat_response = {
            "type": WebSocketMessageType.HEARTBEAT,
            "timestamp": datetime.now(),
            "data": {
                "status": "alive",
                "server_time": datetime.now()
            },
            "message_id": str(uuid.uuid4())
        }

        return await self.send_to_connection(connection_id, heartbeat_response)

    async def cleanup_stale_connections(self):
        """Remove connections that haven't sent heartbeat recently."""
        current_time = datetime.now()
        stale_connections = []

        for connection_id, connection in self.connections.items():
            time_since_heartbeat = (current_time - connection.last_heartbeat).total_seconds()
            if time_since_heartbeat > self.connection_timeout:
                stale_connections.append(connection_id)

        for connection_id in stale_connections:
            logger.warning(f"Removing stale connection: {connection_id}")
            await self.disconnect(connection_id)

        return len(stale_connections)

    def get_connection_info(self, connection_id: str) -> Optional[WebSocketConnectionInfo]:
        """Get information about a specific connection."""
        if connection_id not in self.connections:
            return None

        connection = self.connections[connection_id]
        return WebSocketConnectionInfo(**connection.to_dict())

    def get_all_connections(self) -> List[WebSocketConnectionInfo]:
        """Get information about all active connections."""
        return [
            WebSocketConnectionInfo(**conn.to_dict())
            for conn in self.connections.values()
        ]

    def get_user_connections(self, user_id: int) -> List[WebSocketConnectionInfo]:
        """Get all connections for a specific user."""
        if user_id not in self.user_connections:
            return []

        return [
            WebSocketConnectionInfo(**self.connections[conn_id].to_dict())
            for conn_id in self.user_connections[user_id]
            if conn_id in self.connections
        ]

    def get_active_users(self) -> List[Dict[str, Any]]:
        """Get list of currently active users."""
        active_users = {}

        for connection in self.connections.values():
            user_id = connection.user_id
            if user_id not in active_users:
                active_users[user_id] = {
                    "user_id": user_id,
                    "username": connection.username,
                    "role": connection.role,
                    "connection_count": 0,
                    "last_activity": connection.last_activity,
                    "current_page": connection.current_page,
                    "active_schedule_date": connection.active_schedule_date
                }

            active_users[user_id]["connection_count"] += 1

            # Update with most recent activity
            if connection.last_activity > active_users[user_id]["last_activity"]:
                active_users[user_id]["last_activity"] = connection.last_activity
                active_users[user_id]["current_page"] = connection.current_page
                active_users[user_id]["active_schedule_date"] = connection.active_schedule_date

        return list(active_users.values())

    def get_statistics(self) -> Dict[str, Any]:
        """Get WebSocket manager statistics."""
        return {
            "active_connections": len(self.connections),
            "total_connections": self.total_connections,
            "total_messages_sent": self.total_messages_sent,
            "active_users": len(self.user_connections),
            "active_roles": list(self.role_connections.keys()),
            "message_history_size": len(self.message_history),
            "uptime_seconds": time.time() - getattr(self, '_start_time', time.time())
        }

    def _add_to_history(self, message: Dict[str, Any]):
        """Add message to history with size limit."""
        self.message_history.append({
            **message,
            "sent_at": datetime.now()
        })

        # Maintain history size limit
        if len(self.message_history) > self.max_history_size:
            self.message_history = self.message_history[-self.max_history_size:]


# Global WebSocket manager instance
websocket_manager = WebSocketManager()