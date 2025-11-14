-- ====================================
-- Multi-City GIS Portfolio Analyzer
-- Database Schema
-- ====================================
-- PostgreSQL + PostGIS
-- Run this file to manually create the database schema

-- Enable PostGIS extension
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS postgis_topology;

-- ====================================
-- Cities Table
-- ====================================
CREATE TABLE IF NOT EXISTS cities (
    city_id SERIAL PRIMARY KEY,
    city_name VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(200) NOT NULL,
    state VARCHAR(50),
    center_lat DECIMAL(10, 8) NOT NULL,
    center_lng DECIMAL(11, 8) NOT NULL,
    zoom_level INTEGER DEFAULT 11,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_cities_name ON cities(city_name);
CREATE INDEX idx_cities_active ON cities(is_active);

-- ====================================
-- City Configurations Table
-- ====================================
CREATE TABLE IF NOT EXISTS city_configs (
    config_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    valid_property_types JSONB,
    column_mappings JSONB,
    data_sources JSONB,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_city_configs_city ON city_configs(city_id);

-- ====================================
-- Parcels Table (Main Geospatial Data)
-- ====================================
CREATE TABLE IF NOT EXISTS parcels (
    parcel_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    parcel_pin VARCHAR(50) NOT NULL,
    geometry GEOMETRY(Geometry, 4326),
    
    -- Address fields
    address VARCHAR(300),
    par_zip VARCHAR(10),
    
    -- Owner information
    deeded_owner VARCHAR(300),
    owner_clean VARCHAR(300),
    
    -- Property details
    tax_luc_description VARCHAR(200),
    
    -- Financial data
    sales_amount DECIMAL(15, 2),
    certified_tax_total DECIMAL(15, 2),
    
    -- Metadata
    source_file VARCHAR(500),
    import_batch VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    UNIQUE(city_id, parcel_pin)
);

-- Spatial index for performance (critical!)
CREATE INDEX idx_parcels_geometry ON parcels USING GIST(geometry);
CREATE INDEX idx_parcels_city ON parcels(city_id);
CREATE INDEX idx_parcels_owner_clean ON parcels(owner_clean);
CREATE INDEX idx_parcels_zip ON parcels(par_zip);
CREATE INDEX idx_parcels_pin ON parcels(parcel_pin);

-- ====================================
-- Target Owners Table
-- ====================================
CREATE TABLE IF NOT EXISTS target_owners (
    target_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    owner_clean VARCHAR(300) NOT NULL,
    category VARCHAR(100),
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, owner_clean)
);

CREATE INDEX idx_target_owners_city ON target_owners(city_id);
CREATE INDEX idx_target_owners_clean ON target_owners(owner_clean);
CREATE INDEX idx_target_owners_active ON target_owners(is_active);

-- ====================================
-- Import History Table
-- ====================================
CREATE TABLE IF NOT EXISTS import_history (
    import_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    import_type VARCHAR(50),
    file_name VARCHAR(500),
    records_imported INTEGER,
    status VARCHAR(50),
    error_log TEXT,
    imported_by VARCHAR(100),
    import_batch VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_import_history_city ON import_history(city_id);
CREATE INDEX idx_import_history_status ON import_history(status);
CREATE INDEX idx_import_history_batch ON import_history(import_batch);

-- ====================================
-- Statistics Cache Table
-- ====================================
CREATE TABLE IF NOT EXISTS stats_cache (
    cache_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    cache_key VARCHAR(200) NOT NULL,
    cache_data JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, cache_key)
);

CREATE INDEX idx_stats_cache_city ON stats_cache(city_id);
CREATE INDEX idx_stats_cache_key ON stats_cache(cache_key);
CREATE INDEX idx_stats_cache_expires ON stats_cache(expires_at);

-- ====================================
-- Verification Queries
-- ====================================
-- Check PostGIS version
SELECT PostGIS_version();

-- List all tables
SELECT tablename FROM pg_tables WHERE schemaname = 'public';

-- Verify spatial indexes
SELECT 
    schemaname,
    tablename,
    indexname,
    indexdef
FROM pg_indexes
WHERE schemaname = 'public'
ORDER BY tablename, indexname;

