"""
Database Manager
Handles PostgreSQL + PostGIS connections and operations
"""

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
from typing import Optional
import os
from dotenv import load_dotenv

load_dotenv()


class DatabaseManager:
    """
    Manages database connections and sessions
    Provides context managers for safe database operations
    """
    
    def __init__(self):
        self.db_url: Optional[str] = None
        self.engine = None
        self.SessionLocal = None
    
    def _build_db_url(self) -> str:
        """
        Build database URL from environment variables
        
        Returns:
            str: Database connection string
        """
        # Check for full DATABASE_URL first (for cloud deployments)
        db_url = os.getenv('DATABASE_URL')
        if db_url:
            # Fix for Heroku postgres:// to postgresql://
            if db_url.startswith('postgres://'):
                db_url = db_url.replace('postgres://', 'postgresql://', 1)
            return db_url
        
        # Build from individual components
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'multi_city_gis')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def initialize(self):
        """
        Initialize database connection and create tables
        Should be called once at application startup
        """
        from database.models import Base
        
        self.db_url = self._build_db_url()
        
        # Create engine with connection pooling
        self.engine = create_engine(
            self.db_url,
            echo=False,  # Set to True for SQL debugging
            pool_size=5,
            max_overflow=10,
            pool_pre_ping=True  # Verify connections before using
        )
        
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False
        )
        
        # Create all tables
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """
        Context manager for database sessions
        Automatically handles commit/rollback
        
        Usage:
            with db_manager.get_session() as session:
                # Your database operations here
                pass
        
        Yields:
            Session: SQLAlchemy session
        """
        if self.SessionLocal is None:
            raise RuntimeError("Database not initialized. Call initialize() first.")
        
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def test_connection(self) -> bool:
        """
        Test database connection
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            if self.engine is None:
                return False
            
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def get_postgis_version(self) -> Optional[str]:
        """
        Get PostGIS version if installed
        
        Returns:
            str: PostGIS version string or None if not available
        """
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT PostGIS_version();"))
                return result.scalar()
        except Exception:
            return None
    
    def execute_query(self, query: str, params: dict = None):
        """
        Execute a raw SQL query
        
        Args:
            query: SQL query string
            params: Query parameters (optional)
        
        Returns:
            Query result
        """
        with self.get_session() as session:
            return session.execute(text(query), params or {})
    
    def close(self):
        """Close database connections"""
        if self.engine:
            self.engine.dispose()


# Create singleton instance
db_manager = DatabaseManager()

