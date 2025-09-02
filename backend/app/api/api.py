from fastapi import APIRouter
from app.api.endpoints import documentation

api_router = APIRouter()

# Include documentation endpoints
api_router.include_router(
    documentation.router,
    prefix="/documentation",
    tags=["documentation"]
)

# Add more API routers here as needed
# api_router.include_router(users.router, prefix="/users", tags=["users"])
