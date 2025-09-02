# Initialize the API router and include all endpoints
from fastapi import APIRouter
from .endpoints import documentation, collaboration

api_router = APIRouter()
api_router.include_router(documentation.router, prefix="/documentation", tags=["Documentation"])
api_router.include_router(collaboration.router, prefix="/collaboration", tags=["Collaboration"])
