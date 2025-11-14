"""
SQLAlchemy Database Models
Defines the database schema for the application
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Numeric, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from datetime import datetime

Base = declarative_base()


class City(Base):
    """Cities table - stores information about each city"""
    __tablename__ = 'cities'
    
    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(100), unique=True, nullable=False, index=True)
    display_name = Column(String(200), nullable=False)
    state = Column(String(50))
    center_lat = Column(Numeric(10, 8), nullable=False)
    center_lng = Column(Numeric(11, 8), nullable=False)
    zoom_level = Column(Integer, default=11)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<City(id={self.city_id}, name='{self.city_name}')>"


class CityConfig(Base):
    """City configuration table - stores city-specific settings"""
    __tablename__ = 'city_configs'
    
    config_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'), nullable=False)
    valid_property_types = Column(JSONB)  # Array of valid land use types
    column_mappings = Column(JSONB)       # Map source columns to standard names
    data_sources = Column(JSONB)          # File metadata
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f"<CityConfig(id={self.config_id}, city_id={self.city_id})>"


class Parcel(Base):
    """Parcels table - main geospatial data"""
    __tablename__ = 'parcels'
    
    parcel_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'), nullable=False, index=True)
    parcel_pin = Column(String(50), nullable=False)
    geometry = Column(Geometry('GEOMETRY', srid=4326))  # WGS84
    
    # Address fields
    address = Column(String(300))
    par_zip = Column(String(10), index=True)
    
    # Owner information
    deeded_owner = Column(String(300))
    owner_clean = Column(String(300), index=True)
    
    # Property details
    tax_luc_description = Column(String(200))
    
    # Financial data
    sales_amount = Column(Numeric(15, 2))
    certified_tax_total = Column(Numeric(15, 2))
    
    # Metadata
    source_file = Column(String(500))
    import_batch = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Parcel(id={self.parcel_id}, pin='{self.parcel_pin}', city_id={self.city_id})>"


class TargetOwner(Base):
    """Target owners table - lists of property owners to analyze"""
    __tablename__ = 'target_owners'
    
    target_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'), nullable=False, index=True)
    owner_clean = Column(String(300), nullable=False, index=True)
    category = Column(String(100))  # e.g., "Portfolio Targets (10-100)"
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<TargetOwner(id={self.target_id}, owner='{self.owner_clean}', city_id={self.city_id})>"


class ImportHistory(Base):
    """Import history table - tracks data uploads"""
    __tablename__ = 'import_history'
    
    import_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'), nullable=False)
    import_type = Column(String(50))  # 'parcels', 'targets', 'full'
    file_name = Column(String(500))
    records_imported = Column(Integer)
    status = Column(String(50))  # 'success', 'failed', 'partial'
    error_log = Column(Text)
    imported_by = Column(String(100))
    import_batch = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<ImportHistory(id={self.import_id}, type='{self.import_type}', status='{self.status}')>"


class StatsCache(Base):
    """Statistics cache table - for performance optimization"""
    __tablename__ = 'stats_cache'
    
    cache_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'), nullable=False)
    cache_key = Column(String(200), nullable=False)
    cache_data = Column(JSONB)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<StatsCache(id={self.cache_id}, key='{self.cache_key}')>"

