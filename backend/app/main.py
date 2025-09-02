from fastapi import FastAPI, Depends, HTTPException, status, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.websockets import WebSocketDisconnect
from typing import List, Dict, Optional, Any
import json
import asyncio
import uuid
from datetime import datetime
import logging
import os
from dotenv import load_dotenv
from pathlib import Path

# Import database and models
from app.database import engine, get_db
from app.models import Base, init_db

# Import WebSocket manager
from app.services.websocket_manager import ConnectionManager

# Import API routers
from app.api import api_router
from app.api.endpoints import documentation as documents_router

# Initialize WebSocket manager
websocket_manager = ConnectionManager()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
env_path = Path('.') / '.env'
load_dotenv(dotenv_path=env_path)

# Initialize WebSocket manager
websocket_manager = ConnectionManager()

# Configure allowed origins for CORS
origins = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
]

app = FastAPI(
    title="InkWell AI",
    description="AI-powered documentation tool for generating and maintaining technical documentation.",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_tags=[
        {
            "name": "Documents",
            "description": "Document generation and management",
        },
        {
            "name": "Templates",
            "description": "Documentation templates management",
        },
        {
            "name": "Collaboration",
            "description": "Real-time document collaboration",
        },
    ],
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["Content-Range", "X-Total-Count"],
)

# Include API routers
app.include_router(api_router, prefix="/api/v1")
app.include_router(documents_router.router, prefix="/api/v1/documents", tags=["Documents"])

# Health check endpoint
@app.get("/api/health", response_model=dict, tags=["Health"])
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Status and version information including database connection status
    """
    from sqlalchemy import text
    from app.database import AsyncSessionLocal
    import os
    import sys
    from datetime import datetime
    
    db_status = "disconnected"
    db_version = "unknown"
    
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT sqlite_version()"))
            db_version = result.scalar()
            db_status = "connected"
    except Exception as e:
        print(f"Database connection error: {e}", file=sys.stderr)
    
    response = {
        "status": "ok" if db_status == "connected" else "error",
        "version": "1.0.0",
        "database": {
            "status": db_status,
            "version": str(db_version) if db_version else "unknown",
            "type": "sqlite"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENV", "development"),
        "websockets": {
            "active_connections": len(websocket_manager.active_connections)
        }
    }
    
    # Log the response for debugging
    print(f"Health check response: {response}", file=sys.stderr)
    return response

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    logger.info("Initializing database...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Middleware to log all incoming requests"""
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    logger.info(f"Response status: {response.status_code}")
    return response

@app.get("/api/health")
async def health_check():
    """
    Health check endpoint
    
    Returns:
        dict: Status and version information including database connection status
    """
    from app.database import get_db
    from sqlalchemy import text
    
    # Test database connection
    db_connected = False
    db_version = "unknown"
    
    try:
        async with get_db() as db:
            # Test database connection with a simple query
            result = await db.execute(text("SELECT 1"))
            db_connected = result.scalar() == 1
            
            # Try to get database version
            try:
                if 'sqlite' in str(engine.url):
                    version = await db.execute(text("SELECT sqlite_version()"))
                else:
                    version = await db.execute(text("SELECT version()"))
                db_version = version.scalar()
            except Exception as e:
                logger.warning(f"Could not get database version: {e}")
                
    except Exception as e:
        logger.error(f"Database connection error: {e}")
    
    return {
        "status": "ok" if db_connected else "error",
        "version": "1.0.0",
        "database": {
            "status": "connected" if db_connected else "disconnected",
            "version": db_version,
            "type": str(engine.url).split('+')[0] if hasattr(engine, 'url') else "unknown"
        },
        "timestamp": datetime.utcnow().isoformat(),
        "environment": os.getenv("ENVIRONMENT", "development"),
        "websockets": {
            "active_connections": len(websocket_manager.active_connections)
        }
    }

# WebSocket endpoint for real-time collaboration
@app.websocket("/ws/{document_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    document_id: str, 
    user_id: str = None,
    token: str = None
):
    """
    WebSocket endpoint for real-time document collaboration
    
    Args:
        websocket: The WebSocket connection
        document_id: ID of the document being collaborated on
        user_id: Optional user ID for the connecting user
        token: Optional authentication token
    """
    # Accept the WebSocket connection
    await websocket.accept()
    
    # Validate user and document access
    try:
        # TODO: Implement proper authentication and authorization
        # For now, we'll just log the connection attempt
        logger.info(f"New WebSocket connection for document {document_id} from user {user_id or 'anonymous'}")
        
        # Register the connection with the manager
        await websocket_manager.connect(websocket, document_id, user_id)
        
        # Notify other users in the same document
        await websocket_manager.broadcast(
            document_id,
            {
                "type": "user_joined",
                "user_id": user_id,
                "timestamp": datetime.utcnow().isoformat()
            },
            exclude=[websocket]
        )
        
        # Send initial document state
        # TODO: Fetch and send the current document state
        await websocket.send_json({
            "type": "init",
            "document_id": document_id,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        # Process incoming messages
        while True:
            # Keep the connection alive
            data = await websocket.receive_text()
            # Process incoming messages
            await websocket_manager.handle_message(websocket, document_id, user_id, data)
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}")
    finally:
        await websocket_manager.disconnect(websocket, document_id, user_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
