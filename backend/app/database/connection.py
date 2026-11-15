"""Database connection setup using SQLAlchemy with PostgreSQL and SQLite fallback."""

from typing import Generator
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from app.config import settings, BASE_DIR

# Base class for declarative ORM models
Base = declarative_base()

_engine = None
_session_factory = None
_is_sqlite = False


def _create_engine_with_fallback():
    """Attempts to connect to settings.DATABASE_URL. If unreachable and PostgreSQL, falls back to SQLite."""
    global _is_sqlite
    db_url = settings.DATABASE_URL

    if db_url.startswith("sqlite"):
        _is_sqlite = True
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            echo=False,
        )

    # Attempt PostgreSQL connection
    try:
        engine = create_engine(
            db_url,
            pool_pre_ping=True,
            echo=False,
        )
        with engine.connect() as conn:
            pass
        _is_sqlite = False
        return engine
    except Exception:
        # Graceful fallback to local SQLite database file
        sqlite_path = BASE_DIR / "datasense.db"
        fallback_url = f"sqlite:///{sqlite_path}"
        _is_sqlite = True
        return create_engine(
            fallback_url,
            connect_args={"check_same_thread": False},
            echo=False,
        )


def get_engine():
    """Returns the SQLAlchemy engine singleton, creating it with fallback if necessary."""
    global _engine
    if _engine is None:
        _engine = _create_engine_with_fallback()
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
    """Verifies whether database is reachable without crashing the app."""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            return True
    except Exception:
        return False


def is_using_sqlite() -> bool:
    """Returns True if the engine is running on SQLite fallback."""
    global _is_sqlite
    get_engine()
    return _is_sqlite


def init_db():
    """Initializes tables in the active database engine."""
    from app.database import models  # Ensure all models are registered
    engine = get_engine()
    Base.metadata.create_all(bind=engine)
