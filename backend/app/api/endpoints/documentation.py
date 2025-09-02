from fastapi import APIRouter, UploadFile, File, HTTPException, Body
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import tempfile
import os
from pathlib import Path
from app.services.document_service import DocumentService
from app.services.grammar_service import GrammarService
from app.core.config import settings

router = APIRouter()
document_service = DocumentService()
grammar_service = GrammarService()

@router.post("/document/upload")
async def upload_document(file: UploadFile = File(...)):
    """
    Upload and process a document for documentation generation.
    """
    try:
        # Save the uploaded file temporarily
        file_extension = Path(file.filename).suffix.lower()
        if file_extension not in document_service.supported_formats:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file format. Supported formats: {', '.join(document_service.supported_formats)}"
            )

        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        try:
            # Process the document
            result = await document_service.process_document(temp_file_path)
            return JSONResponse(content={"status": "success", "data": result})
        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/document/analyze")
async def analyze_code(code: str, language: str = "python"):
    """
    Analyze and document a code snippet.
    """
    try:
        # For code snippets, we'll create a temporary file with the appropriate extension
        extension_map = {
            "python": ".py",
            "javascript": ".js",
            "typescript": ".ts",
            "html": ".html",
            "css": ".css"
        }
        
        extension = extension_map.get(language.lower(), ".txt")
        
        with tempfile.NamedTemporaryFile(suffix=extension, delete=False) as temp_file:
            temp_file.write(code.encode('utf-8'))
            temp_file_path = temp_file.name

        try:
            result = await document_service.process_document(temp_file_path)
            return {"status": "success", "data": result}
        finally:
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
                
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/documentation/check-grammar")
async def check_grammar(
    text: str = Body(..., embed=True, description="Text to check for grammar and style issues")
) -> Dict[str, Any]:
    """
    Check grammar and style issues in the provided text.
    
    Returns a list of issues with suggestions for improvement.
    """
    try:
        if not text or not text.strip():
            return {
                "status": "success",
                "issues": [],
                "issue_count": 0,
                "message": "No text provided for grammar check"
            }
            
        issues = grammar_service.check_grammar(text)
        return {
            "status": "success",
            "issues": issues,
            "issue_count": len(issues)
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check grammar: {str(e)}"
        )
