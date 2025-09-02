import os
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.config import settings
from app.api.api_v1.api import api_router
from app.core.exception_handlers import http_exception_handler, validation_exception_handler

def get_application() -> FastAPI:
    # Create FastAPI app
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="InkWell AI - AI-powered documentation platform",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc"
    )

    # Set up CORS
    if settings.BACKEND_CORS_ORIGINS:
        from fastapi.middleware.cors import CORSMiddleware
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    # Add middleware
    app.add_middleware(GZipMiddleware, minimum_size=1000)

    # Add exception handlers
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)

    # Include API router
    app.include_router(api_router, prefix=settings.API_V1_STR)

    # Mount static files
    os.makedirs("static", exist_ok=True)
    app.mount("/static", StaticFiles(directory="static"), name="static")

    # Health check endpoint
    @app.get("/health")
    async def health_check():
        return {"status": "ok"}

    return app

# Create FastAPI application
app = get_application()

# Run the app with uvicorn when executed directly
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
