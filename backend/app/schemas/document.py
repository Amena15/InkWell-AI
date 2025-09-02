from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field

class DocumentType(str, Enum):
    SRS = "srs"
    SDS = "sds"
    CODE = "code"
    OTHER = "other"

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    content: Optional[str] = None
    document_type: DocumentType = DocumentType.OTHER
    metadata_: Optional[Dict[str, Any]] = Field(default_factory=dict, alias="metadata")

class DocumentCreate(DocumentBase):
    project_id: int

class DocumentUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=3, max_length=200)
    content: Optional[str] = None
    document_type: Optional[DocumentType] = None
    metadata_: Optional[Dict[str, Any]] = Field(None, alias="metadata")

class DocumentInDBBase(DocumentBase):
    id: int
    project_id: int
    author_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True
        allow_population_by_field_name = True

class Document(DocumentInDBBase):
    pass

class DocumentWithProject(DocumentInDBBase):
    project: 'Project'

# Forward reference for Project to avoid circular imports
from .project import Project
DocumentWithProject.update_forward_refs()
