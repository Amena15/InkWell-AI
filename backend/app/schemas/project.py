from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ProjectBase(BaseModel):
    name: str = Field(..., min_length=3, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

class ProjectCreate(ProjectBase):
    pass

class ProjectUpdate(ProjectBase):
    name: Optional[str] = Field(None, min_length=3, max_length=100)

class ProjectInDBBase(ProjectBase):
    id: int
    owner_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class Project(ProjectInDBBase):
    pass

class ProjectWithDocuments(ProjectInDBBase):
    documents: List['Document'] = []

# Forward reference for Document to avoid circular imports
from .document import Document
ProjectWithDocuments.update_forward_refs()
