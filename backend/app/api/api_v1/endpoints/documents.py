from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_active_user

router = APIRouter()

@router.post("/", response_model=schemas.Document)
def create_document(
    document_in: schemas.DocumentCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Create a new document."""
    # Verify project exists and user has access
    db_project = (
        db.query(models.Project)
        .filter(
            models.Project.id == document_in.project_id,
            models.Project.owner_id == current_user.id
        )
        .first()
    )
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    # Create new document
    document_data = document_in.dict()
    document_data.pop("metadata", None)  # Handle metadata separately
    
    db_document = models.Document(
        **document_data,
        author_id=current_user.id,
        metadata_=document_in.metadata_ if hasattr(document_in, 'metadata_') else {}
    )
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.get("/{document_id}", response_model=schemas.DocumentWithProject)
def read_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get a specific document by ID."""
    db_document = (
        db.query(models.Document)
        .join(models.Project, models.Project.id == models.Document.project_id)
        .filter(
            models.Document.id == document_id,
            models.Project.owner_id == current_user.id
        )
        .first()
    )
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    return db_document

@router.get("/project/{project_id}", response_model=List[schemas.Document])
def read_project_documents(
    project_id: int,
    document_type: schemas.DocumentType = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Get all documents for a specific project."""
    # Verify project exists and user has access
    db_project = (
        db.query(models.Project)
        .filter(
            models.Project.id == project_id,
            models.Project.owner_id == current_user.id
        )
        .first()
    )
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    query = db.query(models.Document).filter(
        models.Document.project_id == project_id
    )
    
    if document_type:
        query = query.filter(models.Document.document_type == document_type)
    
    return query.offset(skip).limit(limit).all()

@router.put("/{document_id}", response_model=schemas.Document)
def update_document(
    document_id: int,
    document_in: schemas.DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Update a document."""
    db_document = (
        db.query(models.Document)
        .join(models.Project, models.Project.id == models.Document.project_id)
        .filter(
            models.Document.id == document_id,
            models.Project.owner_id == current_user.id
        )
        .first()
    )
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    update_data = document_in.dict(exclude_unset=True)
    
    # Handle metadata update
    if 'metadata_' in update_data:
        if db_document.metadata_ is None:
            db_document.metadata_ = {}
        db_document.metadata_.update(update_data.pop('metadata_', {}) or {})
    
    for field, value in update_data.items():
        setattr(db_document, field, value)
    
    db.add(db_document)
    db.commit()
    db.refresh(db_document)
    return db_document

@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """Delete a document."""
    db_document = (
        db.query(models.Document)
        .join(models.Project, models.Project.id == models.Document.project_id)
        .filter(
            models.Document.id == document_id,
            models.Project.owner_id == current_user.id
        )
        .first()
    )
    if db_document is None:
        raise HTTPException(status_code=404, detail="Document not found")
    
    db.delete(db_document)
    db.commit()
    return None
