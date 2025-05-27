"""
WebSocket Router for Task 3.1.

This module provides WebSocket endpoints for real-time communication including:
- WebSocket connection management with authentication
- Real-time message broadcasting
- User presence tracking
- Schedule change notifications
- Optimization progress streaming
"""

import json
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from db_config import get_db
from api.auth import get_current_active_user, SECRET_KEY, ALGORITHM
from api.models import (
    WebSocketBroadcastRequest, WebSocketConnectionInfo, WebSocketMessageType,
    User
)
from models import User as UserModel
from websocket_manager import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()


async def get_user_from_token(token: str, db: Session) -> Optional[UserModel]:
    """Extract user from JWT token for WebSocket authentication."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
        
        user = db.query(UserModel).filter(UserModel.username == username).first()
        return user
    except JWTError:
        return None


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(..., description="JWT authentication token"),
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time communication.
    
    Requires JWT authentication via query parameter.
    Handles connection management, message routing, and heartbeat.
    """
    # Authenticate user
    user = await get_user_from_token(token, db)
    if not user or not user.is_active:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Establish connection
    connection_id = await websocket_manager.connect(
        websocket, user.user_id, user.username, user.role
    )
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                await handle_websocket_message(connection_id, message, user.user_id, db)
            except json.JSONDecodeError:
                logger.error(f"Invalid JSON received from connection {connection_id}")
                await websocket_manager.send_to_connection(connection_id, {
                    "type": WebSocketMessageType.ERROR,
                    "data": {"error": "Invalid JSON format"},
                    "timestamp": "now"
                })
            except Exception as e:
                logger.error(f"Error handling message from connection {connection_id}: {e}")
                await websocket_manager.send_to_connection(connection_id, {
                    "type": WebSocketMessageType.ERROR,
                    "data": {"error": "Message processing failed"},
                    "timestamp": "now"
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected: {connection_id}")
    except Exception as e:
        logger.error(f"WebSocket error for connection {connection_id}: {e}")
    finally:
        await websocket_manager.disconnect(connection_id)


async def handle_websocket_message(
    connection_id: str, 
    message: Dict[str, Any], 
    user_id: int, 
    db: Session
):
    """Handle incoming WebSocket messages from clients."""
    message_type = message.get("type")
    data = message.get("data", {})
    
    if message_type == "heartbeat":
        # Handle heartbeat
        await websocket_manager.handle_heartbeat(connection_id, data)
    
    elif message_type == "user_activity":
        # Update user activity
        connection = websocket_manager.connections.get(connection_id)
        if connection:
            connection.update_activity(
                page=data.get("current_page"),
                schedule_date=data.get("active_schedule_date")
            )
            
            # Broadcast presence update
            await websocket_manager.broadcast_user_presence(
                user_id, "active", connection_id,
                current_page=data.get("current_page"),
                active_schedule_date=data.get("active_schedule_date")
            )
    
    elif message_type == "subscribe":
        # Handle subscription to specific events/channels
        # This could be extended for more granular subscriptions
        logger.info(f"User {user_id} subscribed to: {data.get('channels', [])}")
    
    elif message_type == "ping":
        # Simple ping-pong for connection testing
        await websocket_manager.send_to_connection(connection_id, {
            "type": "pong",
            "data": {"timestamp": data.get("timestamp")},
            "timestamp": "now"
        })
    
    else:
        logger.warning(f"Unknown message type '{message_type}' from connection {connection_id}")


@router.post("/broadcast")
async def broadcast_message(
    request: WebSocketBroadcastRequest,
    current_user: User = Depends(get_current_active_user)
):
    """
    Broadcast a message to connected WebSocket clients.
    
    Allows administrators to send targeted messages to specific users or roles.
    """
    try:
        # Set sender information
        request.sender_user_id = current_user.user_id
        
        # Broadcast the message
        result = await websocket_manager.broadcast_message(request)
        
        logger.info(f"Message broadcast by user {current_user.username}: {result['sent_count']} recipients")
        
        return {
            "success": True,
            "message": "Message broadcast successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to broadcast message: {str(e)}"
        )


@router.get("/connections")
async def get_active_connections(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get information about active WebSocket connections.
    
    Returns details about all active connections for monitoring purposes.
    """
    try:
        connections = websocket_manager.get_all_connections()
        
        return {
            "success": True,
            "connections": connections,
            "total_connections": len(connections)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving connections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve connections: {str(e)}"
        )


@router.get("/connections/user/{user_id}")
async def get_user_connections(
    user_id: int,
    current_user: User = Depends(get_current_active_user)
):
    """
    Get WebSocket connections for a specific user.
    
    Returns all active connections for the specified user.
    """
    try:
        connections = websocket_manager.get_user_connections(user_id)
        
        return {
            "success": True,
            "user_id": user_id,
            "connections": connections,
            "connection_count": len(connections)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving user connections: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve user connections: {str(e)}"
        )


@router.get("/users/active")
async def get_active_users(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get list of currently active users.
    
    Returns information about users who have active WebSocket connections.
    """
    try:
        active_users = websocket_manager.get_active_users()
        
        return {
            "success": True,
            "active_users": active_users,
            "total_active_users": len(active_users)
        }
        
    except Exception as e:
        logger.error(f"Error retrieving active users: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve active users: {str(e)}"
        )


@router.get("/statistics")
async def get_websocket_statistics(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get WebSocket manager statistics.
    
    Returns comprehensive statistics about WebSocket usage and performance.
    """
    try:
        stats = websocket_manager.get_statistics()
        
        return {
            "success": True,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error retrieving statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.post("/cleanup")
async def cleanup_stale_connections(
    current_user: User = Depends(get_current_active_user)
):
    """
    Manually trigger cleanup of stale WebSocket connections.
    
    Removes connections that haven't sent heartbeat recently.
    """
    try:
        removed_count = await websocket_manager.cleanup_stale_connections()
        
        return {
            "success": True,
            "message": f"Cleanup completed: {removed_count} stale connections removed",
            "removed_connections": removed_count
        }
        
    except Exception as e:
        logger.error(f"Error during cleanup: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to cleanup connections: {str(e)}"
        )


@router.post("/notify/system")
async def send_system_notification(
    notification_type: str,
    title: str,
    message: str,
    severity: str = "info",
    target_users: Optional[str] = Query(None, description="Comma-separated user IDs"),
    target_roles: Optional[str] = Query(None, description="Comma-separated roles"),
    current_user: User = Depends(get_current_active_user)
):
    """
    Send a system notification to targeted users.
    
    Broadcasts system notifications to specific users or roles.
    """
    try:
        # Parse target lists
        target_user_ids = None
        if target_users:
            target_user_ids = [int(uid.strip()) for uid in target_users.split(",")]
        
        target_role_list = None
        if target_roles:
            target_role_list = [role.strip() for role in target_roles.split(",")]
        
        # Broadcast notification
        result = await websocket_manager.broadcast_system_notification(
            notification_type=notification_type,
            title=title,
            message=message,
            severity=severity,
            target_users=target_user_ids,
            target_roles=target_role_list
        )
        
        logger.info(f"System notification sent by {current_user.username}: {result['sent_count']} recipients")
        
        return {
            "success": True,
            "message": "System notification sent successfully",
            "result": result
        }
        
    except Exception as e:
        logger.error(f"Error sending system notification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send system notification: {str(e)}"
        )
