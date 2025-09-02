# Import Base from database to ensure all models are registered
from app.database import Base

# Import all models from models.py
from .models import (
    User,
    Project,
    AIIntegration,
    Document,
    DocumentVersion,
    DocumentComment,
    document_collaborators
)

# Export all models and database utilities
__all__ = [
    'User',
    'Project',
    'AIIntegration',
    'Document',
    'DocumentVersion',
    'DocumentComment',
    'document_collaborators',
    'Base',
    'init_db'
]

# Import all models to ensure they are registered with SQLAlchemy
# This is necessary for Alembic to detect all models
from . import models
# any database operations are performed
async def init_db():
    """Initialize the database by creating all tables."""
    from app.database import engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Don't call init_db() here - let the application handle when to initialize the database
