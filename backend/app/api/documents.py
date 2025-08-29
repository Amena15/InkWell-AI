from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from typing import List, Dict, Optional
from pydantic import BaseModel
import logging

from ..services.openai_service import OpenAIService, DocumentGenerationRequest, document_type

router = APIRouter()
logger = logging.getLogger(__name__)

class DocumentRequest(BaseModel):
    project_id: str
    project_description: str
    code_snippets: List[Dict[str, str]]
    document_type: document_type
    additional_context: Optional[str] = None

@router.post("/generate")
async def generate_document(request: DocumentRequest):
    """
    Generate SRS or SDS document based on project information and code snippets.
    
    - **project_id**: Unique identifier for the project
    - **project_description**: Detailed description of the project
    - **code_snippets**: List of code snippets with language and optional file path
    - **document_type**: Type of document to generate ('srs' or 'sds')
    - **additional_context**: Any additional context or requirements
    """
    try:
        # Initialize OpenAI service
        openai_service = OpenAIService()
        
        # Prepare the document generation request
        doc_request = DocumentGenerationRequest(
            project_description=request.project_description,
            code_snippets=request.code_snippets,
            document_type=request.document_type,
            additional_context=request.additional_context
        )
        
        # Generate the document
        document = await openai_service.generate_document(doc_request)
        
        # In a real application, you would save this to a database
        # For now, we'll just return it in the response
        
        return {
            "status": "success",
            "document_type": request.document_type,
            "content": document,
            "project_id": request.project_id
        }
        
    except Exception as e:
        logger.error(f"Error generating document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate document: {str(e)}"
        )

# Add the router to the FastAPI app in main.py
# from fastapi import FastAPI
# from .api.documents import router as documents_router
# app = FastAPI()
# app.include_router(documents_router, prefix="/api/documents", tags=["documents"])
