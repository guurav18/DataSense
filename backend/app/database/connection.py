"""Database connection setup using SQLAlchemy."""

from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings

# Base class for declarative ORM models
Base = declarative_base()

# Lazy / safe engine configuration
# pool_pre_ping ensures connections are verified before use
_engine = None
_session_factory = None


def get_engine():
    """Returns the SQLAlchemy engine singleton, creating it if necessary."""
    global _engine
    if _engine is None:
        _engine = create_engine(
            settings.DATABASE_URL,
            pool_pre_ping=True,
            echo=settings.DEBUG,
        )
    return _engine


def get_session_factory():
    """Returns the sessionmaker singleton."""
    global _session_factory
    if _session_factory is None:
        _session_factory = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=get_engine(),
        )
    return _session_factory


def get_db() -> Generator[Session, None, None]:
    """FastAPI dependency yielding a database session."""
    factory = get_session_factory()
    db = factory()
    try:
        yield db
    finally:
        db.close()


def check_db_connection() -> bool:
    """Verifies whether PostgreSQL is reachable without crashing the app."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            return True
    except Exception:
        return False
