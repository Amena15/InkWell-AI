from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
import tempfile
import os

from app import models, schemas
from app.database import get_db
from app.core.security import get_current_active_user
from app.services.ai_service import AIService

router = APIRouter()
ai_service = AIService()

class DocumentType(str):
    SRS = "srs"
    SDS = "sds"
    OTHER = "other"

@router.post("/generate-document")
async def generate_document(
    document_type: str,
    project_id: int,
    code_files: List[UploadFile] = File(...),
    project_description: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Generate a document (SRS/SDS) based on provided code files and project description.
    
    Args:
        document_type: Type of document to generate ('srs' or 'sds')
        project_id: ID of the project this document belongs to
        code_files: List of code files to analyze
        project_description: Optional project description
        
    Returns:
        Generated document with analysis and suggestions
    """
    try:
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
        
        # Read code from uploaded files
        code_snippets = []
        for file in code_files:
            if file.filename.endswith(('.py', '.js', '.ts', '.java', '.c', '.cpp', '.go', '.rs')):
                content = await file.read()
                code_snippets.append(f"File: {file.filename}\n```\n{content.decode()}\n```")
        
        if not code_snippets:
            raise HTTPException(
                status_code=400,
                detail="No valid code files provided. Supported formats: .py, .js, .ts, .java, .c, .cpp, .go, .rs"
            )
        
        # Get existing project documents for context
        existing_docs = db.query(models.Document).filter(
            models.Document.project_id == project_id
        ).all()
        
        existing_docs_content = [
            f"{doc.title} ({doc.document_type}):\n{doc.content}"
            for doc in existing_docs
        ]
        
        # Generate document using AI service
        result = await ai_service.generate_document(
            document_type=document_type,
            code_snippets=code_snippets,
            project_description=project_description or "",
            existing_docs=existing_docs_content
        )
        
        # Save the generated document
        db_document = models.Document(
            title=f"{document_type.upper()} - {db_project.name}",
            content=result["document"],
            document_type=document_type,
            project_id=project_id,
            author_id=current_user.id,
            metadata_={
                "generated": True,
                "analysis": result.get("analysis", {}),
                "suggestions": result.get("suggestions", [])
            }
        )
        
        db.add(db_document)
        db.commit()
        db.refresh(db_document)
        
        return {
            "document": db_document,
            "analysis": result.get("analysis", {}),
            "suggestions": result.get("suggestions", [])
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate document: {str(e)}"
        )
    finally:
        # Clean up any temporary files
        for file in code_files:
            if hasattr(file.file, 'name') and os.path.exists(file.file.name):
                try:
                    os.unlink(file.file.name)
                except:
                    pass

@router.post("/analyze-code-docs")
async def analyze_code_documentation(
    code: str,
    documentation: str,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Analyze the consistency between code and its documentation.
    
    Args:
        code: Source code to analyze
        documentation: Documentation text to check against
        
    Returns:
        Analysis results with consistency metrics and issues
    """
    try:
        analysis = ai_service.analyze_code_documentation_consistency(code, documentation)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze code documentation: {str(e)}"
        )

@router.post("/analyze-document-quality")
async def analyze_document_quality(
    document: str,
    doc_type: str,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Analyze the quality of a document.
    
    Args:
        document: The document text to analyze
        doc_type: Type of document ('srs' or 'sds')
        
    Returns:
        Quality analysis with metrics and suggestions
    """
    try:
        analysis = ai_service.analyze_document_quality(document, doc_type)
        return analysis
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze document quality: {str(e)}"
        )

@router.post("/suggest-improvements")
async def suggest_improvements(
    document: str,
    doc_type: str,
    current_user: models.User = Depends(get_current_active_user)
):
    """
    Suggest improvements for a document.
    
    Args:
        document: The document text to improve
        doc_type: Type of document ('srs' or 'sds')
        
    Returns:
        List of suggested improvements
    """
    try:
        # First analyze the document
        analysis = ai_service.analyze_document_quality(document, doc_type)
        
        # Then generate suggestions based on the analysis
        suggestions = []
        
        # Check coverage
        if analysis.get('coverage_score', 0) < 50:
            suggestions.append({
                'type': 'coverage',
                'severity': 'high',
                'message': 'Document has low coverage of required sections.',
                'suggestion': 'Consider adding more sections to cover all aspects of the document type.'
            })
        
        # Check for missing sections
        if analysis.get('missing_sections'):
            suggestions.append({
                'type': 'structure',
                'severity': 'medium',
                'message': f"Missing recommended sections: {', '.join(analysis['missing_sections'])}",
                'suggestion': 'Add these sections to improve document completeness.'
            })
        
        # Check document length
        if analysis.get('word_count', 0) < 200:
            suggestions.append({
                'type': 'content',
                'severity': 'low',
                'message': 'Document is quite short.',
                'suggestion': 'Consider adding more detailed explanations and examples.'
            })
        
        return {
            'suggestions': suggestions,
            'analysis': analysis
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate suggestions: {str(e)}"
        )
