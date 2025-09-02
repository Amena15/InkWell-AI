import json
import asyncio
import logging
import uuid
from typing import Dict, Set, List, Callable, Any, Optional, Union
from fastapi import WebSocket, WebSocketDisconnect
from collections import defaultdict
from datetime import datetime

logger = logging.getLogger(__name__)

class ConnectionManager:
    """
    Manages WebSocket connections for real-time document collaboration.
    Handles connection lifecycle, message routing, and broadcasting.
    """
    
    def __init__(self):
        # document_id -> { user_id -> WebSocket }
        self.active_connections: Dict[str, Dict[str, WebSocket]] = defaultdict(dict)
        # user_id -> Set[document_id]
        self.user_subscriptions: Dict[str, Set[str]] = defaultdict(set)
        # message_type -> handler
        self.handlers: Dict[str, Callable] = {}
        # Track user presence
        self.presence: Dict[str, Dict[str, Any]] = defaultdict(dict)

    async def connect(self, websocket: WebSocket, document_id: str, user_id: Optional[str] = None):
        """Register a new WebSocket connection for a user and document"""
        if not user_id:
            user_id = f"anonymous_{id(websocket)}"
            
        # Store the connection
        self.active_connections[document_id][user_id] = websocket
        self.user_subscriptions[user_id].add(document_id)
        
        # Update presence
        self.presence[document_id][user_id] = {
            'last_seen': datetime.utcnow().isoformat(),
            'status': 'online'
        }
        
        logger.info(f"User {user_id} connected to document {document_id}")
        return user_id

    async def disconnect(self, websocket: WebSocket, document_id: str, user_id: Optional[str] = None):
        """Remove a WebSocket connection"""
        if not user_id:
            # Find the user_id for this websocket
            for uid, ws in self.active_connections[document_id].items():
                if ws == websocket:
                    user_id = uid
                    break
            
            if not user_id:
                return
        
        # Remove the connection
        if document_id in self.active_connections and user_id in self.active_connections[document_id]:
            del self.active_connections[document_id][user_id]
            
        if user_id in self.user_subscriptions:
            self.user_subscriptions[user_id].discard(document_id)
            if not self.user_subscriptions[user_id]:
                del self.user_subscriptions[user_id]
        
        # Update presence
        if document_id in self.presence and user_id in self.presence[document_id]:
            del self.presence[document_id][user_id]
            
        logger.info(f"User {user_id} disconnected from document {document_id}")

    async def broadcast(
        self,
        document_id: str,
        message: Union[Dict[str, Any], str],
        exclude: Optional[Set[WebSocket]] = None,
        exclude_users: Optional[Set[str]] = None
    ) -> None:
        """Broadcast a message to all clients in a document"""
        if document_id not in self.active_connections:
            return

        exclude = exclude or set()
        exclude_users = exclude_users or set()
        
        if isinstance(message, dict):
            message = json.dumps(message)
            
        disconnected = []
        
        for user_id, connection in list(self.active_connections[document_id].items()):
            if connection in exclude or user_id in exclude_users:
                continue
                
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error sending to {user_id}: {e}")
                disconnected.append((user_id, connection))
        
        # Clean up disconnected clients
        for user_id, connection in disconnected:
            await self.disconnect(connection, document_id, user_id)

    async def handle_message(
        self, 
        websocket: WebSocket, 
        document_id: str, 
        user_id: str, 
        data: str
    ) -> None:
        """Process an incoming WebSocket message"""
        try:
            message = json.loads(data)
            message_type = message.get('type')
            
            if not message_type:
                await websocket.send_json({"error": "Message type is required"})
                return
                
            handler = self.handlers.get(message_type)
            if not handler:
                await websocket.send_json({"error": f"Unknown message type: {message_type}"})
                return
                
            # Update user's last seen time
            if document_id in self.presence and user_id in self.presence[document_id]:
                self.presence[document_id][user_id]['last_seen'] = datetime.utcnow().isoformat()
            
            # Process the message
            await handler(self, websocket, document_id, user_id, message)
            
        except json.JSONDecodeError:
            await websocket.send_json({"error": "Invalid JSON format"})
        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
            await websocket.send_json({"error": "Internal server error"})

    def register_handler(self, message_type: str) -> Callable:
        """Decorator to register a message handler"""
        def decorator(handler: Callable):
            self.handlers[message_type] = handler
            return handler
        return decorator
        
    def get_connected_users(self, document_id: str) -> List[Dict[str, Any]]:
        """Get list of users currently connected to a document"""
        if document_id not in self.presence:
            return []
            
        return [
            {"user_id": user_id, **data}
            for user_id, data in self.presence[document_id].items()
        ]

# Singleton instance
websocket_manager = ConnectionManager()

# Register message handlers
def register_handlers():
    @websocket_manager.register_handler("cursor_update")
    async def handle_cursor_update(
        manager: ConnectionManager,
        websocket: WebSocket,
        document_id: str,
        user_id: str,
        message: dict
    ):
        """Handle cursor position updates from clients"""
        await manager.broadcast(
            document_id=document_id,
            message={
                "type": "cursor_update",
                "user_id": user_id,
                "position": message.get("position"),
                "user_info": message.get("user_info", {}),
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude={websocket}
        )

    @websocket_manager.register_handler("content_update")
    async def handle_content_update(
        manager: ConnectionManager,
        websocket: WebSocket,
        document_id: str,
        user_id: str,
        message: dict
    ):
        """Handle document content updates from clients"""
        changes = message.get("changes", [])
        version = message.get("version")
        
        if not changes or version is None:
            await websocket.send_json({
                "type": "error",
                "message": "Missing required fields: changes and version are required"
            })
            return
        
        # Here you would typically validate and save the changes to your database
        # For now, we'll just broadcast them to other clients
        
        await manager.broadcast(
            document_id=document_id,
            message={
                "type": "content_update",
                "user_id": user_id,
                "changes": changes,
                "version": version,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude={websocket}
        )
        
        # Acknowledge the update
        await websocket.send_json({
            "type": "content_update_ack",
            "version": version,
            "timestamp": datetime.utcnow().isoformat()
        })

    @websocket_manager.register_handler("comment")
    async def handle_comment(
        manager: ConnectionManager,
        websocket: WebSocket,
        document_id: str,
        user_id: str,
        message: dict
    ):
        """Handle document comments from clients"""
        comment = message.get("comment")
        comment_range = message.get("range")
        
        if not comment or not comment_range:
            await websocket.send_json({
                "type": "error",
                "message": "Missing required fields: comment and range are required"
            })
            return
        
        # Create a new comment with server-generated ID and timestamp
        comment_id = f"comment_{uuid.uuid4().hex}"
        timestamp = datetime.utcnow().isoformat()
        
        # Here you would typically save the comment to your database
        
        # Broadcast the comment to all clients, including the sender
        await manager.broadcast(
            document_id=document_id,
            message={
                "type": "comment",
                "id": comment_id,
                "user_id": user_id,
                "comment": comment,
                "range": comment_range,
                "timestamp": timestamp,
                "status": "active"
            }
        )
        
    @websocket_manager.register_handler("presence_update")
    async def handle_presence_update(
        manager: ConnectionManager,
        websocket: WebSocket,
        document_id: str,
        user_id: str,
        message: dict
    ):
        """Handle user presence updates (typing status, etc.)"""
        status = message.get("status", {})
        
        # Update presence information
        if document_id in manager.presence and user_id in manager.presence[document_id]:
            manager.presence[document_id][user_id].update(status)
            manager.presence[document_id][user_id]["last_seen"] = datetime.utcnow().isoformat()
        
        # Broadcast the update to other clients
        await manager.broadcast(
            document_id=document_id,
            message={
                "type": "presence_update",
                "user_id": user_id,
                "status": status,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude={websocket}
        )
        
    @websocket_manager.register_handler("get_presence")
    async def handle_get_presence(
        manager: ConnectionManager,
        websocket: WebSocket,
        document_id: str,
        user_id: str,
        message: dict
    ):
        """Send current presence information for a document"""
        await websocket.send_json({
            "type": "presence_info",
            "users": manager.get_connected_users(document_id),
            "timestamp": datetime.utcnow().isoformat()
        })

# Initialize handlers
register_handlers()
