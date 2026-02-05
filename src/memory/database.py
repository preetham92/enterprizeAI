"""
Database models and initialization for PostgreSQL memory layer.
"""
from datetime import datetime
from typing import Optional
from uuid import uuid4
from sqlalchemy import (
    Column, String, Float, DateTime, Text, ARRAY, JSON,
    create_engine, Index
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config.settings import settings
from src.utils.logging import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class MemoryEntryModel(Base):
    """
    PostgreSQL model for memory entries.
    Stores historical insights and learnings.
    """
    __tablename__ = "memory_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(String(100), nullable=False, index=True)
    entity_name = Column(String(500), nullable=False, index=True)
    insight_type = Column(String(100), nullable=False, index=True)
    content = Column(JSON, nullable=False)
    confidence_score = Column(Float, nullable=False, index=True)
    source_agent = Column(String(100), nullable=False)
    tags = Column(ARRAY(String), default=list)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_entity_type_name', 'entity_type', 'entity_name'),
        Index('idx_insight_confidence', 'insight_type', 'confidence_score'),
        Index('idx_created_at', 'created_at'),
    )


class EntityScoreModel(Base):
    """
    Optional table for tracking entity-level aggregated scores.
    """
    __tablename__ = "entity_scores"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    entity_type = Column(String(100), nullable=False)
    entity_name = Column(String(500), nullable=False)
    score_type = Column(String(100), nullable=False)
    score_value = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_entity_score_type', 'entity_type', 'entity_name', 'score_type', unique=True),
    )


class MemorySourceModel(Base):
    """
    Optional table for tracking sources of memory entries.
    """
    __tablename__ = "memory_sources"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    memory_entry_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    source_type = Column(String(50), nullable=False)  # 'url', 'document', 'agent'
    source_reference = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class DatabaseManager:
    """Manages database connections and sessions."""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
    
    def initialize(self) -> None:
        """Initialize database connection and create tables."""
        try:
            logger.info("Initializing database connection", url=settings.database_url.split('@')[-1])
            
            self.engine = create_engine(
                settings.database_url,
                pool_size=settings.db_pool_size,
                max_overflow=settings.db_max_overflow,
                pool_timeout=settings.db_pool_timeout,
                pool_pre_ping=True,
                echo=settings.environment == "development"
            )
            
            # Create all tables
            Base.metadata.create_all(bind=self.engine)
            
            # Create session factory
            self.SessionLocal = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )
            
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.error("Failed to initialize database", error=str(e))
            raise
    
    def get_session(self):
        """Get a database session."""
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        return self.SessionLocal()
    
    def close(self) -> None:
        """Close database connections."""
        if self.engine:
            self.engine.dispose()
            logger.info("Database connections closed")


# Global database manager instance
db_manager = DatabaseManager()