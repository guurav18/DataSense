"""SQLAlchemy ORM models for DataSense AI."""

from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.database.connection import Base


class DatasetRecord(Base):
    """Stores metadata for uploaded datasets (CSV, Excel)."""

    __tablename__ = "datasets"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_name = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # csv, xlsx, xls
    file_size_bytes = Column(Integer, nullable=True)
    row_count = Column(Integer, nullable=True)
    column_count = Column(Integer, nullable=True)
    storage_path = Column(String(500), nullable=False)
    profile_summary = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    sessions = relationship("AnalysisSession", back_populates="dataset", cascade="all, delete-orphan")


class AnalysisSession(Base):
    """Stores interaction sessions, queries, and results produced by the agent."""

    __tablename__ = "analysis_sessions"

    id = Column(Integer, primary_key=True, index=True)
    dataset_id = Column(Integer, ForeignKey("datasets.id"), nullable=True)
    user_query = Column(Text, nullable=False)
    agent_plan = Column(JSON, nullable=True)
    generated_code = Column(Text, nullable=True)
    status = Column(String(50), default="pending")  # pending, completed, failed
    response_summary = Column(Text, nullable=True)
    chart_path = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    dataset = relationship("DatasetRecord", back_populates="sessions")
