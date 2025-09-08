"""
Database Connection Management
Copyright (c) 2025 - Signature: 8598

Professional database connection management with connection pooling,
transaction handling, and error recovery.
"""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import QueuePool
from sqlalchemy.exc import SQLAlchemyError, DisconnectionError
from contextlib import contextmanager
from typing import Generator, Optional
import logging
import time
from threading import Lock

from ..config import config
from .models import Base

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Professional database connection manager.
    Signature: 8598
    """
    
    _instance: Optional['DatabaseManager'] = None
    _lock = Lock()
    
    def __new__(cls) -> 'DatabaseManager':
        """Singleton pattern for database manager."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize database manager."""
        if hasattr(self, '_initialized'):
            return
        
        self._initialized = True
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
    
    def _setup_engine(self) -> None:
        """Setup database engine with connection pooling."""
        try:
            # Create engine with connection pooling
            self.engine = create_engine(
                config.get_database_url(),
                echo=config.database.echo,
                poolclass=QueuePool,
                pool_size=config.database.pool_size,
                max_overflow=config.database.max_overflow,
                pool_timeout=config.database.pool_timeout,
                pool_recycle=config.database.pool_recycle,
                pool_pre_ping=True,  # Verify connections before use
                connect_args={
                    "check_same_thread": False  # For SQLite compatibility
                } if "sqlite" in config.get_database_url() else {}
            )
            
            # Create session factory
            self.SessionLocal = scoped_session(
                sessionmaker(
                    bind=self.engine,
                    autocommit=False,
                    autoflush=False
                )
            )
            
            # Add connection event listeners
            self._setup_event_listeners()
            
            logger.info(f"Database engine initialized successfully - Signature: 8598")
            
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise
    
    def _setup_event_listeners(self) -> None:
        """Setup database event listeners for monitoring."""
        
        @event.listens_for(self.engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            """Set SQLite pragmas for better performance."""
            if "sqlite" in config.get_database_url():
                cursor = dbapi_connection.cursor()
                cursor.execute("PRAGMA foreign_keys=ON")
                cursor.execute("PRAGMA journal_mode=WAL")
                cursor.execute("PRAGMA synchronous=NORMAL")
                cursor.execute("PRAGMA cache_size=10000")
                cursor.execute("PRAGMA temp_store=MEMORY")
                cursor.close()
        
        @event.listens_for(self.engine, "checkout")
        def receive_checkout(dbapi_connection, connection_record, connection_proxy):
            """Log connection checkout."""
            logger.debug("Database connection checked out")
        
        @event.listens_for(self.engine, "checkin")
        def receive_checkin(dbapi_connection, connection_record):
            """Log connection checkin."""
            logger.debug("Database connection checked in")
    
    def create_tables(self) -> None:
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("Database tables created successfully - Signature: 8598")
        except Exception as e:
            logger.error(f"Failed to create database tables: {e}")
            raise
    
    def drop_tables(self) -> None:
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("Database tables dropped successfully - Signature: 8598")
        except Exception as e:
            logger.error(f"Failed to drop database tables: {e}")
            raise
    
    @contextmanager
    def get_session(self) -> Generator:
        """
        Get database session with automatic cleanup.
        Usage:
            with db_manager.get_session() as session:
                # Use session here
                pass
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()
    
    def get_session(self) -> 'Session':
        """Get database session (manual management)."""
        return self.SessionLocal()
    
    def close_session(self, session) -> None:
        """Close database session."""
        if session:
            session.close()
    
    def health_check(self) -> bool:
        """
        Check database connection health.
        Returns True if healthy, False otherwise.
        """
        try:
            with self.get_session() as session:
                session.execute(text("SELECT 1"))
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False
    
    def get_connection_info(self) -> dict:
        """Get database connection information."""
        return {
            "url": config.get_database_url(),
            "pool_size": config.database.pool_size,
            "max_overflow": config.database.max_overflow,
            "pool_timeout": config.database.pool_timeout,
            "pool_recycle": config.database.pool_recycle,
            "signature": "8598"
        }
    
    def close(self) -> None:
        """Close all database connections."""
        try:
            if self.engine:
                self.engine.dispose()
            logger.info("Database connections closed - Signature: 8598")
        except Exception as e:
            logger.error(f"Error closing database connections: {e}")


# Global database manager instance
db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    """Get the global database manager instance."""
    return db_manager


def init_database() -> None:
    """Initialize database with tables."""
    try:
        # In development with SQLite, drop and recreate to ensure schema matches models
        db_url = config.get_database_url()
        if "sqlite" in db_url:
            db_manager.drop_tables()
        db_manager.create_tables()
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise


def get_session():
    """Get database session."""
    return db_manager.get_session()


@contextmanager
def get_db_session():
    """Get database session with context manager."""
    with db_manager.get_session() as session:
        yield session
