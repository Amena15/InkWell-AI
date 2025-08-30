from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import os
from ..services.openai_service import OpenAIService, DocumentGenerationRequest

router = APIRouter()

# Initialize OpenAI service
openai_service = OpenAIService(api_key=os.getenv("OPENAI_API_KEY"))

# Temporary storage (replace with database in production)
documents_db = {}

# Request models
class CodeSnippet(BaseModel):
    language: str
    code: str
    file_path: str

class GenerateDocumentRequest(BaseModel):
    project_id: str
    project_description: str
    code_snippets: List[CodeSnippet]
    document_type: Literal["srs", "sds"]
    additional_context: Optional[str] = None

class DocumentBase(BaseModel):
    title: str
    content: str
    doc_type: str  # 'srs' or 'sds'
    project_id: str
    metadata: Optional[dict] = None

class Document(DocumentBase):
    id: str
    created_at: datetime
    updated_at: datetime

@router.post("/", response_model=Document)
async def create_document(document: DocumentBase):
    """Create a new document"""
    doc_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    new_doc = Document(
        id=doc_id,
        **document.dict(),
        created_at=now,
        updated_at=now
    )
    
    documents_db[doc_id] = new_doc
    return new_doc

@router.get("/{doc_id}", response_model=Document)
async def get_document(doc_id: str):
    """Get a document by ID"""
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    return documents_db[doc_id]

@router.put("/{doc_id}", response_model=Document)
async def update_document(doc_id: str, document: DocumentBase):
    """Update a document"""
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    
    updated_doc = Document(
        id=doc_id,
        **document.dict(),
        created_at=documents_db[doc_id].created_at,
        updated_at=datetime.utcnow()
    )
    
    documents_db[doc_id] = updated_doc
    return updated_doc

@router.get("/project/{project_id}", response_model=List[Document])
async def get_project_documents(project_id: str, doc_type: Optional[str] = None):
    """Get all documents for a project, optionally filtered by type"""
    docs = [doc for doc in documents_db.values() if doc.project_id == project_id]
    if doc_type:
        docs = [doc for doc in docs if doc.doc_type == doc_type]
    return docs

@router.delete("/{doc_id}", status_code=204)
async def delete_document(doc_id: str):
    """Delete a document by ID"""
    if doc_id not in documents_db:
        raise HTTPException(status_code=404, detail="Document not found")
    del documents_db[doc_id]
    return None

@router.post("/generate", status_code=status.HTTP_201_CREATED)
async def generate_document(request: GenerateDocumentRequest):
    """
    Generate a document (SRS or SDS) based on project description and code snippets.
    """
    try:
        # Convert the request to the format expected by OpenAIService
        doc_request = DocumentGenerationRequest(
            project_description=request.project_description,
            code_snippets=[snippet.dict() for snippet in request.code_snippets],
            document_type=request.document_type,
            additional_context=request.additional_context
        )
        
        # Generate the document content
        content = await openai_service.generate_document(doc_request)
        
        # Create a new document with the generated content
        doc_data = {
            "title": f"{request.document_type.upper()} - {request.project_id}",
            "content": content,
            "doc_type": request.document_type,
            "project_id": request.project_id,
            "metadata": {
                "generated_by": "openai",
                "model": openai_service.model
            }
        }
        
        # Save the document
        doc = DocumentBase(**doc_data)
        created_doc = await create_document(doc)
        
        return {
            "message": "Document generated successfully",
            "document": created_doc.dict()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating document: {str(e)}"
        )

@router.post("/import/markdown")
async def import_markdown(file: UploadFile = File(...), project_id: str = Form(...), doc_type: str = Form(...)):
    """Import document from markdown file"""
    if not file.filename.endswith('.md'):
        raise HTTPException(status_code=400, detail="Only .md files are supported")
    
    content = await file.read()
    
    doc = DocumentBase(
        title=file.filename.replace('.md', ''),
        content=content.decode('utf-8'),
        doc_type=doc_type,
        project_id=project_id
    )
    
    return await create_document(doc)
