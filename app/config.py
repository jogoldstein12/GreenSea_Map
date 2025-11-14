"""
Application Configuration
Loads environment variables and provides app-wide settings
"""

import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Optional

# Load environment variables
load_dotenv()


class Config:
    """Application configuration class"""
    
    # Application Info
    APP_NAME: str = os.getenv("APP_NAME", "Multi-City GIS Portfolio Analyzer")
    APP_VERSION: str = "2.0.0"
    APP_ENV: str = os.getenv("APP_ENV", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key")
    
    # Database Configuration
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: int = int(os.getenv("DB_PORT", "5432"))
    DB_NAME: str = os.getenv("DB_NAME", "multi_city_gis")
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "")
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    # File Upload Configuration
    MAX_FILE_SIZE_MB: int = int(os.getenv("MAX_FILE_SIZE_MB", "500"))
    ALLOWED_EXTENSIONS: list = os.getenv(
        "ALLOWED_EXTENSIONS", 
        "csv,shp,shx,dbf,prj,cpg,xml,xlsx,xls"
    ).split(",")
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "data/uploads/temp")
    
    # Map Configuration
    DEFAULT_ZOOM: int = int(os.getenv("DEFAULT_ZOOM", "11"))
    DEFAULT_MAP_TILES: str = os.getenv("DEFAULT_MAP_TILES", "cartodbpositron")
    
    # Performance Settings
    CACHE_TTL: int = int(os.getenv("CACHE_TTL", "3600"))
    MAX_PARCELS_WARNING: int = int(os.getenv("MAX_PARCELS_WARNING", "50000"))
    GEOMETRY_SIMPLIFY_TOLERANCE: float = float(
        os.getenv("GEOMETRY_SIMPLIFY_TOLERANCE", "0.0001")
    )
    
    # Security Settings
    ENABLE_DATA_UPLOAD: bool = os.getenv("ENABLE_DATA_UPLOAD", "True").lower() == "true"
    ENABLE_DATA_DELETE: bool = os.getenv("ENABLE_DATA_DELETE", "True").lower() == "true"
    REQUIRE_AUTH: bool = os.getenv("REQUIRE_AUTH", "False").lower() == "true"
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/app.log")
    
    @classmethod
    def get_database_url(cls) -> str:
        """
        Build database connection URL
        
        Returns:
            str: Database connection string
        """
        if cls.DATABASE_URL:
            return cls.DATABASE_URL
        
        return (
            f"postgresql://{cls.DB_USER}:{cls.DB_PASSWORD}"
            f"@{cls.DB_HOST}:{cls.DB_PORT}/{cls.DB_NAME}"
        )
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist"""
        directories = [
            cls.UPLOAD_DIR,
            "logs",
            "data/uploads",
            "data/uploads/temp"
        ]
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def is_development(cls) -> bool:
        """Check if running in development mode"""
        return cls.APP_ENV == "development"
    
    @classmethod
    def is_production(cls) -> bool:
        """Check if running in production mode"""
        return cls.APP_ENV == "production"


# Create singleton instance
config = Config()

# Ensure directories exist
config.ensure_directories()

