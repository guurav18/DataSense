"""Main entrypoint for DataSense AI FastAPI Backend."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any

from app.config import settings
from app.api.routes import router as api_router

# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous Data Analysis Agent API powered by LangGraph, Pandas, and Matplotlib",
    version="0.1.0",
    debug=settings.DEBUG,
)

# Configure Cross-Origin Resource Sharing (CORS) for Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router)


@app.get("/")
def read_root() -> Dict[str, Any]:
    """Root endpoint welcoming users and providing basic API metadata."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "description": "Autonomous Data Analysis Agent backend is running successfully.",
        "version": "0.1.0",
        "docs_url": "/docs",
        "health_check": "/health",
        "status_url": "/api/v1/status",
    }


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify backend service readiness.

    Does not require external database or LLM connectivity to report healthy status.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database_configured": bool(settings.DATABASE_URL and "localhost:5432" not in settings.DATABASE_URL),
        "llm_configured": bool(settings.LLM_API_KEY and "your_" not in settings.LLM_API_KEY),
    }
