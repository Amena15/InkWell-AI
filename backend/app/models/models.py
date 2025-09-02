from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy import String, Text, DateTime, ForeignKey, Boolean, Integer, JSON, Column, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column
from sqlalchemy.sql import func
import uuid

from app.database import Base

# Association table for document collaborators (using SQLAlchemy Core syntax)
document_collaborators = Table(
    'document_collaborators',
    Base.metadata,
    Column('document_id', String(36), ForeignKey('documents.id'), primary_key=True),
    Column('user_id', String(36), primary_key=True),
    Column('permission_level', String(20), server_default='viewer'),  # viewer, editor, admin
    Column('added_at', DateTime, server_default=func.now())
)

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[Optional[str]] = mapped_column(String(100))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    projects: Mapped[List["Project"]] = relationship("Project", back_populates="owner")
    documents: Mapped[List["Document"]] = relationship("Document", secondary=document_collaborators, back_populates="collaborators")
    comments: Mapped[List["DocumentComment"]] = relationship("DocumentComment", back_populates="author")

class Project(Base):
    __tablename__ = "projects"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    owner_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    
    # Relationships
    owner: Mapped["User"] = relationship("User", back_populates="projects")
    documents: Mapped[List["Document"]] = relationship("Document", back_populates="project")

# Document model has been moved to document_models.py

class AIIntegration(Base):
    __tablename__ = "ai_integrations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    provider: Mapped[str] = mapped_column(String(50), nullable=False)  # e.g., 'openai', 'anthropic'
    api_key: Mapped[str] = mapped_column(String(255), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., 'gpt-4', 'claude-2'
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), onupdate=func.now())

class Document(Base):
    __tablename__ = "documents"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
    created_by: Mapped[str] = mapped_column(String(36), nullable=False)  # User ID of the creator
    is_public: Mapped[bool] = mapped_column(Boolean, server_default='false')
    
    # Relationships
    versions: Mapped[List["DocumentVersion"]] = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    collaborators: Mapped[List["User"]] = relationship("User", secondary=document_collaborators, back_populates="documents")

class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    document_id: Mapped[str] = mapped_column(String(36), ForeignKey("documents.id"), nullable=False)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)  # User ID of the author
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # Commit message
    change_summary: Mapped[Optional[Dict[str, Any]]] = mapped_column(JSON, nullable=True)  # JSON with summary of changes
    
    # Relationships
    document: Mapped["Document"] = relationship("Document", back_populates="versions")
    comments: Mapped[List["DocumentComment"]] = relationship("DocumentComment", back_populates="version", cascade="all, delete-orphan")

class DocumentComment(Base):
    __tablename__ = "document_comments"
    
    id: Mapped[str] = mapped_column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    version_id: Mapped[str] = mapped_column(String(36), ForeignKey("document_versions.id"), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str] = mapped_column(String(36), nullable=False)  # User ID of the commenter
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    resolved: Mapped[bool] = mapped_column(Boolean, server_default='false')
    resolved_by: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)  # User ID who resolved the comment
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    parent_comment_id: Mapped[Optional[str]] = mapped_column(String(36), ForeignKey("document_comments.id"), nullable=True)  # For threaded comments
    comment_metadata: Mapped[Dict[str, Any]] = mapped_column(JSON, server_default='{}')  # Additional metadata like mentions, reactions, etc.
    
    # Relationships
    version: Mapped["DocumentVersion"] = relationship("DocumentVersion", back_populates="comments")
    parent_comment: Mapped[Optional["DocumentComment"]] = relationship("DocumentComment", remote_side=[id], back_populates="replies", foreign_keys=[parent_comment_id])
    replies: Mapped[List["DocumentComment"]] = relationship("DocumentComment", back_populates="parent_comment", cascade="all, delete-orphan")
