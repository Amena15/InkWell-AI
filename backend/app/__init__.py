"""
InkWell AI Backend Application
"""

__version__ = "0.1.0"

# Import core components to make them available at the package level
from .database import Base, get_db
from .core.config import settings

# Import models to ensure they are registered with SQLAlchemy
from .models import User, Project, Document, DocumentVersion, DocumentComment, document_collaborators

__all__ = [
    'Base',
    'get_db',
    'settings',
    'User',
    'Project',
    'Document',
    'DocumentVersion',
    'DocumentComment',
    'document_collaborators'
]
