from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class DocumentType(str, Enum):
    SRS = "srs"
    SDS = "sds"
    CODE = "code"
    OTHER = "other"

class AIDocumentGenerateRequest(BaseModel):
    """Request model for generating a document."""
    document_type: DocumentType
    project_id: int
    code_snippets: List[str] = Field(..., description="List of code snippets to analyze")
    project_description: Optional[str] = Field(None, description="Description of the project")
    additional_context: Optional[Dict[str, Any]] = Field(
        None, description="Additional context for document generation"
    )

class AIDocumentAnalysis(BaseModel):
    """Model for document analysis results."""
    word_count: int
    section_count: int
    coverage_score: float = Field(..., ge=0, le=100, description="Coverage score (0-100)")
    missing_sections: List[str] = Field(..., description="List of missing sections")
    issues_found: int = Field(..., description="Number of issues found")
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class AIDocumentSuggestion(BaseModel):
    """Model for document improvement suggestions."""
    type: str
    severity: str  # 'low', 'medium', 'high'
    message: str
    suggestion: str
    start_pos: Optional[int] = None
    end_pos: Optional[int] = None

class AIDocumentResponse(BaseModel):
    """Response model for document generation."""
    document: str = Field(..., description="Generated document content")
    analysis: AIDocumentAnalysis = Field(..., description="Analysis of the generated document")
    suggestions: List[AIDocumentSuggestion] = Field(..., description="List of improvement suggestions")

class AICodeAnalysisRequest(BaseModel):
    """Request model for code analysis."""
    code: str = Field(..., description="Source code to analyze")
    documentation: str = Field(..., description="Documentation to analyze")
    language: Optional[str] = Field(None, description="Programming language of the code")

class AICodeAnalysisResponse(BaseModel):
    """Response model for code analysis."""
    consistency_score: float = Field(..., ge=0, le=1, description="Consistency score (0-1)")
    elements_analyzed: int = Field(..., description="Number of code elements analyzed")
    issues_found: int = Field(..., description="Number of issues found")
    issues: List[Dict[str, Any]] = Field(..., description="List of issues found")

class AIProvider(str, Enum):
    """Supported AI providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    COHERE = "cohere"

class AIModelConfig(BaseModel):
    """Configuration for an AI model."""
    provider: AIProvider
    model_name: str
    temperature: float = 0.7
    max_tokens: int = 2000
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0

class AIIntegrationCreate(BaseModel):
    """Model for creating a new AI integration."""
    provider: AIProvider
    api_key: str
    model_name: str
    is_active: bool = True

class AIIntegrationUpdate(BaseModel):
    """Model for updating an AI integration."""
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    is_active: Optional[bool] = None

class AIIntegrationResponse(BaseModel):
    """Response model for AI integration."""
    id: int
    provider: str
    model_name: str
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AIDocumentTypeTemplate(BaseModel):
    """Template for a document type."""
    name: str
    description: str
    sections: List[Dict[str, str]] = Field(..., description="List of sections with name and description")
    example: Optional[str] = Field(None, description="Example of the document type")
