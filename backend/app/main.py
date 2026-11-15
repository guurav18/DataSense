"""Main entrypoint for DataSense AI FastAPI Backend."""

from contextlib import asynccontextmanager
from typing import Dict, Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.routes import router as api_router
from app.database.connection import init_db, check_db_connection, is_using_sqlite


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager initializing database tables on application launch."""
    init_db()
    yield


# Initialize FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Autonomous Data Analysis Agent API powered by LangGraph, Pandas, and Matplotlib",
    version="1.0.0",
    debug=settings.DEBUG,
    lifespan=lifespan,
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
        "version": "1.0.0",
        "docs_url": "/docs",
        "health_check": "/health",
        "status_url": "/api/v1/status",
    }


@app.get("/health")
def health_check() -> Dict[str, Any]:
    """Health check endpoint to verify backend service readiness."""
    db_ok = check_db_connection()
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "database_configured": db_ok,
        "database_type": "sqlite" if is_using_sqlite() else "postgresql",
        "llm_configured": bool(settings.LLM_API_KEY and "your_" not in settings.LLM_API_KEY),
    }
