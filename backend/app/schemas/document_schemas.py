from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from uuid import UUID

# Enums
class PermissionLevel(str, Enum):
    VIEWER = "viewer"
    EDITOR = "editor"
    ADMIN = "admin"

# Base schemas
class DocumentBase(BaseModel):
    title: str
    description: Optional[str] = None
    is_public: bool = False

class DocumentVersionBase(BaseModel):
    content: str
    message: Optional[str] = None
    change_summary: Optional[Dict[str, Any]] = None

class DocumentCommentBase(BaseModel):
    content: str
    range: Optional[Dict[str, Any]] = None
    parent_comment_id: Optional[UUID] = None
    metadata: Optional[Dict[str, Any]] = {}

# Create schemas
class DocumentCreate(DocumentBase):
    pass

class DocumentVersionCreate(DocumentVersionBase):
    pass

class DocumentCommentCreate(DocumentCommentBase):
    pass

# Update schemas
class DocumentUpdate(DocumentBase):
    title: Optional[str] = None
    description: Optional[str] = None
    is_public: Optional[bool] = None

class DocumentVersionUpdate(DocumentVersionBase):
    content: Optional[str] = None
    message: Optional[str] = None

class DocumentCommentUpdate(DocumentCommentBase):
    content: Optional[str] = None
    resolved: Optional[bool] = None

# Response schemas
class UserResponse(BaseModel):
    id: UUID
    username: str
    email: str

    class Config:
        from_attributes = True

class DocumentResponse(DocumentBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    created_by: UUID
    versions_count: Optional[int] = None
    
    class Config:
        from_attributes = True

class DocumentVersionResponse(DocumentVersionBase):
    id: UUID
    document_id: UUID
    version_number: int
    author_id: UUID
    created_at: datetime
    comment_count: Optional[int] = 0
    
    class Config:
        from_attributes = True

class DocumentCommentResponse(DocumentCommentBase):
    id: UUID
    version_id: UUID
    author_id: UUID
    created_at: datetime
    resolved: bool = False
    resolved_by: Optional[UUID] = None
    resolved_at: Optional[datetime] = None
    replies: List['DocumentCommentResponse'] = []
    
    class Config:
        from_attributes = True

# Update forward reference for nested comments
DocumentCommentResponse.model_rebuild()

# WebSocket message schemas
class WebSocketMessage(BaseModel):
    type: str
    client_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class CursorUpdateMessage(WebSocketMessage):
    type: str = "cursor_update"
    position: Dict[str, int]
    user: Dict[str, Any]

class ContentUpdateMessage(WebSocketMessage):
    type: str = "content_update"
    changes: Dict[str, Any]
    version: int

class CommentMessage(WebSocketMessage):
    type: str = "comment"
    comment: Dict[str, Any]
    range: Optional[Dict[str, Any]] = None

class NewVersionMessage(WebSocketMessage):
    type: str = "new_version"
    version_id: UUID
    version_number: int
    author_id: UUID
    message: Optional[str] = None

class NewCommentMessage(WebSocketMessage):
    type: str = "new_comment"
    comment_id: UUID
    version_id: UUID
    author_id: UUID
    content: str

# Permission schemas
class DocumentPermission(BaseModel):
    user_id: UUID
    permission_level: PermissionLevel
    document_id: UUID

class UpdatePermission(BaseModel):
    permission_level: PermissionLevel
