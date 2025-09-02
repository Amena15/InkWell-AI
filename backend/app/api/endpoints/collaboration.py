from fastapi import APIRouter, Depends, HTTPException, WebSocket, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from app.database import get_db
from app.models import Document, DocumentVersion, DocumentComment, User
from app.services.websocket_manager import websocket_manager
from app.core.security import get_current_user
from app.schemas.document_schemas import (
    DocumentCreate, DocumentVersionCreate, DocumentCommentCreate,
    DocumentResponse, DocumentVersionResponse, DocumentCommentResponse
)

router = APIRouter()

# WebSocket endpoint for real-time collaboration
@router.websocket("/ws/documents/{document_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    document_id: str,
    user_id: str = None,
    token: str = None,
    db: Session = Depends(get_db)
):
    """
    WebSocket endpoint for real-time document collaboration.
    
    Query Parameters:
        user_id: ID of the current user (optional, for anonymous users)
        token: Authentication token (for future use)
    """
    # Verify document exists
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # TODO: Add proper authentication and authorization
    # For now, we'll just log the connection attempt
    logger = logging.getLogger(__name__)
    
    try:
        # Connect the WebSocket
        user_id = await websocket_manager.connect(websocket, document_id, user_id)
        logger.info(f"User {user_id} connected to document {document_id}")
        
        # Notify other users in the same document
        await websocket_manager.broadcast(
            document_id=document_id,
            message={
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude={websocket}
        )
        
        # Send the current document state
        await websocket.send_json({
            "type": "document_state",
            "document_id": document_id,
            "content": document.content,
            "version": document.version,
            "last_modified": document.updated_at.isoformat() if document.updated_at else None,
            "connected_users": websocket_manager.get_connected_users(document_id)
        })
        
        # Process incoming messages
        while True:
            data = await websocket.receive_text()
            await websocket_manager.handle_message(websocket, document_id, user_id, data)
            
    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from document {document_id}")
    except Exception as e:
        logger.error(f"WebSocket error for user {user_id}: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"WebSocket error: {str(e)}"
            })
        except:
            pass
    finally:
        # Clean up the connection
        await websocket_manager.disconnect(websocket, document_id, user_id)
        
        # Notify other users that this user left
        try:
            await websocket_manager.broadcast(
                document_id=document_id,
                message={
                    "type": "user_left",
                    "user_id": user_id,
                    "timestamp": datetime.utcnow().isoformat()
                }
            )
        except Exception as e:
            logger.error(f"Error notifying about user departure: {str(e)}")

# Document endpoints
@router.post("/documents/", response_model=DocumentResponse)
def create_document(
    document: DocumentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_document = Document(
        **document.dict(exclude_unset=True),
        created_by=current_user.id
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/documents/{document_id}", response_model=DocumentResponse)
def get_document(
    document_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if not document.is_public and current_user.id not in [c.id for c in document.collaborators]:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    return document

# Version endpoints
@router.post("/documents/{document_id}/versions", response_model=DocumentVersionResponse)
def create_document_version(
    document_id: str,
    version: DocumentVersionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if user is a collaborator
    if current_user.id not in [c.id for c in document.collaborators]:
        raise HTTPException(status_code=403, detail="Not authorized to edit this document")
    
    # Get the next version number
    last_version = db.query(DocumentVersion)\
        .filter(DocumentVersion.document_id == document_id)\
        .order_by(DocumentVersion.version_number.desc())\
        .first()
    
    version_number = 1 if not last_version else last_version.version_number + 1
    
    db_version = DocumentVersion(
        **version.dict(exclude_unset=True),
        document_id=document_id,
        version_number=version_number,
        author_id=current_user.id
    )
    
    db.add(db_version)
    db.commit()
    db.refresh(db_version)
    
    # Notify all connected clients about the new version
    websocket_manager.broadcast(
        document_id,
        {
            "type": "new_version",
            "version_id": str(db_version.id),
            "version_number": version_number,
            "author_id": current_user.id,
            "timestamp": db_version.created_at.isoformat(),
            "message": version.message
        }
    )
    
    return db_version

@router.get("/documents/{document_id}/versions", response_model=List[DocumentVersionResponse])
def list_document_versions(
    document_id: str,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check permissions
    if not document.is_public and current_user.id not in [c.id for c in document.collaborators]:
        raise HTTPException(status_code=403, detail="Not authorized to access this document")
    
    versions = db.query(DocumentVersion)\
        .filter(DocumentVersion.document_id == document_id)\
        .order_by(DocumentVersion.version_number.desc())\
        .offset(skip)\
        .limit(limit)\
        .all()
    
    return versions

# Comment endpoints
@router.post("/versions/{version_id}/comments", response_model=DocumentCommentResponse)
def add_comment(
    version_id: str,
    comment: DocumentCommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    version = db.query(DocumentVersion)\
        .filter(DocumentVersion.id == version_id)\
        .first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Check if user has access to the document
    document = db.query(Document).filter(Document.id == version.document_id).first()
    if not document or (not document.is_public and current_user.id not in [c.id for c in document.collaborators]):
        raise HTTPException(status_code=403, detail="Not authorized to comment on this document")
    
    db_comment = DocumentComment(
        **comment.dict(exclude_unset=True),
        version_id=version_id,
        author_id=current_user.id
    )
    
    db.add(db_comment)
    db.commit()
    db.refresh(db_comment)
    
    # Notify about the new comment
    websocket_manager.broadcast(
        version.document_id,
        {
            "type": "new_comment",
            "comment_id": str(db_comment.id),
            "version_id": version_id,
            "author_id": current_user.id,
            "content": comment.content,
            "timestamp": db_comment.created_at.isoformat()
        }
    )
    
    return db_comment

@router.get("/versions/{version_id}/comments", response_model=List[DocumentCommentResponse])
def list_comments(
    version_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    version = db.query(DocumentVersion)\
        .filter(DocumentVersion.id == version_id)\
        .first()
    
    if not version:
        raise HTTPException(status_code=404, detail="Version not found")
    
    # Check if user has access to the document
    document = db.query(Document).filter(Document.id == version.document_id).first()
    if not document or (not document.is_public and current_user.id not in [c.id for c in document.collaborators]):
        raise HTTPException(status_code=403, detail="Not authorized to view comments on this document")
    
    comments = db.query(DocumentComment)\
        .filter(DocumentComment.version_id == version_id)\
        .filter(DocumentComment.parent_comment_id == None)\
        .all()
    
    return comments

# Collaboration endpoints
@router.post("/documents/{document_id}/collaborators/{user_id}")
def add_collaborator(
    document_id: str,
    user_id: str,
    permission: str = "editor",
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    document = db.query(Document).filter(Document.id == document_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Check if current user is the owner or has admin rights
    if document.created_by != current_user.id and \
       not any(c.id == current_user.id and c.permission_level == 'admin' 
              for c in document.collaborators):
        raise HTTPException(status_code=403, detail="Not authorized to manage collaborators")
    
    # Check if user exists
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Add or update collaborator
    # This is a simplified version - in a real app, you'd update the association table
    if user not in document.collaborators:
        document.collaborators.append(user)
    
    db.commit()
    
    return {"message": f"Added {user.username} as a collaborator"}
