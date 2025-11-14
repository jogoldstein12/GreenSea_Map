# Multi-City GIS Portfolio Analyzer - Implementation Roadmap

## Project Overview
Converting the Cleveland GIS mapping tool from a standalone Python script to a scalable, deployable Streamlit web application supporting multiple cities.

**Technology Stack:**
- **Framework:** Streamlit
- **Database:** PostgreSQL + PostGIS
- **Geospatial:** GeoPandas, Folium, Shapely
- **Data Processing:** Pandas, SQLAlchemy
- **Deployment:** Streamlit Cloud / Heroku

---

## Pre-Implementation Setup

### Environment Setup
- [x] Install Python 3.9+ (verify: `python --version`) ✅ **Python 3.13.1 installed**
- [x] Create project virtual environment ✅ **Created and activated (.venv)**
  ```bash
  python -m venv venv
  # Windows
  .\venv\Scripts\activate
  # Mac/Linux
  source venv/bin/activate
  ```
- [x] Install PostgreSQL 14+ with PostGIS extension ✅ **PostgreSQL 14.9 + PostGIS 3.3 via Docker**
- [x] Install Git (for version control and deployment)
- [ ] Create GitHub repository for project

### Development Tools
- [x] Install database management tool (pgAdmin, DBeaver, or TablePlus) ✅ **pgAdmin available via docker-compose**
- [x] Install code editor with Python support (VS Code recommended) ✅ **VS Code in use**
- [x] Setup `.gitignore` for Python projects ✅ **Comprehensive .gitignore created**

---

## Phase 1: Project Structure & Dependencies Setup
**Duration:** 1 day | **Priority:** Critical | **STATUS:** ✅ **COMPLETE**

### 1.1 Create Directory Structure
- [x] Create new project directory structure: ✅ **All folders created with __init__.py files**
```
multi_city_gis/
├── .streamlit/
│   └── config.toml              # Streamlit configuration
├── app/
│   ├── __init__.py
│   ├── main.py                  # Streamlit entry point
│   └── config.py                # Application configuration
├── database/
│   ├── __init__.py
│   ├── db_manager.py            # Database connection & queries
│   ├── models.py                # SQLAlchemy models
│   └── schema.sql               # Database schema (backup)
├── data_processing/
│   ├── __init__.py
│   ├── csv_processor.py         # CSV ingestion
│   ├── shapefile_processor.py   # Shapefile processing
│   ├── excel_processor.py       # Excel target owners
│   ├── normalizer.py            # Column normalization
│   └── analyzer.py              # Portfolio statistics
├── mapping/
│   ├── __init__.py
│   ├── map_generator.py         # Folium map creation
│   ├── layer_builder.py         # Layer generation
│   └── styles.py                # Map styling
├── ui/
│   ├── __init__.py
│   ├── pages/
│   │   ├── 1_🏠_Home.py         # City dashboard
│   │   ├── 2_🗺️_Map_Viewer.py   # Map interface
│   │   ├── 3_📤_Upload_Data.py  # Data upload
│   │   └── 4_⚙️_Settings.py     # Configuration
│   └── components/
│       ├── __init__.py
│       ├── sidebar.py           # Reusable sidebar
│       ├── stats_panel.py       # Statistics display
│       └── filters.py           # Filter components
├── utils/
│   ├── __init__.py
│   ├── validators.py            # Data validation
│   ├── helpers.py               # Utility functions
│   └── cache.py                 # Caching utilities
├── data/                        # Local data storage (gitignored)
│   └── uploads/
│       └── temp/
├── tests/
│   ├── __init__.py
│   ├── test_database.py
│   ├── test_processors.py
│   └── test_mapping.py
├── .env                         # Environment variables (gitignored)
├── .env.example                 # Template for .env
├── .gitignore
├── requirements.txt
├── README.md
└── docker-compose.yml           # Optional: for local PostgreSQL
```

### 1.2 Create requirements.txt
- [x] Create `requirements.txt` with dependencies: ✅ **Created with flexible versioning (>=)**
```txt
# Core Framework
streamlit==1.29.0
streamlit-folium==0.15.1

# Database
sqlalchemy==2.0.23
psycopg2-binary==2.9.9
geoalchemy2==0.14.2

# Geospatial
geopandas==0.14.1
folium==0.15.0
shapely==2.0.2
pyproj==3.6.1
Fiona==1.9.5

# Data Processing
pandas==2.1.4
openpyxl==3.1.2
xlrd==2.0.1

# Utilities
python-dotenv==1.0.0
colorama==0.4.6

# Visualization
matplotlib==3.8.2

# Development (optional)
pytest==7.4.3
black==23.12.1
flake8==6.1.0
```

### 1.3 Environment Configuration
- [x] Create `.env.example` file template ✅ **Complete template created**
- [x] Create `.env` file for local development ✅ **Created with working database credentials**
```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=multi_city_gis
DB_USER=your_username
DB_PASSWORD=your_password

# Application Settings
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-change-in-production

# Data Upload Limits
MAX_FILE_SIZE_MB=500
ALLOWED_EXTENSIONS=csv,shp,shx,dbf,prj,cpg,xml,xlsx,xls
```

### 1.4 Streamlit Configuration
- [x] Create `.streamlit/config.toml`: ✅ **Created with theme, upload limits, server settings**
```toml
[theme]
primaryColor = "#2E86AB"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
maxUploadSize = 500
enableCORS = false
enableXsrfProtection = true

[browser]
gatherUsageStats = false
```

### 1.5 Git Setup
- [ ] Initialize Git repository
- [x] Create `.gitignore`: ✅ **Comprehensive ignore rules for Python, data, IDE files**
```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/
*.egg-info/

# Environment
.env
.env.local

# Data files
data/
*.csv
*.shp
*.shx
*.dbf
*.prj
*.cpg
*.xml
*.xlsx
!data/.gitkeep

# IDE
.vscode/
.idea/
*.swp
*.swo

# Streamlit
.streamlit/secrets.toml

# OS
.DS_Store
Thumbs.db

# Database
*.db
*.sqlite
```

**✅ Checkpoint:** Run `pip install -r requirements.txt` - should complete without errors
**STATUS:** ✅ **PASSED** - All packages installed successfully (streamlit 1.51.0, pandas 2.3.3, geopandas 1.1.1, etc.)

---

## Phase 2: Database Architecture
**Duration:** 1-2 days | **Priority:** Critical | **STATUS:** ✅ **COMPLETE**

### 2.1 PostgreSQL + PostGIS Setup
- [x] Install PostgreSQL locally or setup cloud instance ✅ **PostgreSQL 14.9 via Docker**
- [x] Enable PostGIS extension: ✅ **PostGIS 3.3 enabled**
```sql
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```
- [x] Create database: `multi_city_gis` ✅ **Database created and accessible**
- [x] Verify PostGIS: `SELECT PostGIS_version();` ✅ **Verified: PostGIS 3.3**

### 2.2 Database Schema Design
- [x] Create `database/schema.sql`: ✅ **Complete schema with all tables and indexes defined**
```sql
-- Cities Table
CREATE TABLE cities (
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

-- Configuration for each city
CREATE TABLE city_configs (
    config_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    valid_property_types JSONB,  -- Array of valid land use types
    column_mappings JSONB,        -- Map source columns to standard names
    data_sources JSONB,           -- File metadata
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Parcels Table (main geospatial data)
CREATE TABLE parcels (
    parcel_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    parcel_pin VARCHAR(50) NOT NULL,
    geometry GEOMETRY(Geometry, 4326),  -- WGS84
    
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

-- Spatial index for performance
CREATE INDEX idx_parcels_geometry ON parcels USING GIST(geometry);
CREATE INDEX idx_parcels_city ON parcels(city_id);
CREATE INDEX idx_parcels_owner_clean ON parcels(owner_clean);
CREATE INDEX idx_parcels_zip ON parcels(par_zip);

-- Target Owners Table
CREATE TABLE target_owners (
    target_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    owner_clean VARCHAR(300) NOT NULL,
    category VARCHAR(100),  -- e.g., "Portfolio Targets (10-100)"
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, owner_clean)
);

CREATE INDEX idx_target_owners_city ON target_owners(city_id);
CREATE INDEX idx_target_owners_clean ON target_owners(owner_clean);

-- Import History (track data uploads)
CREATE TABLE import_history (
    import_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    import_type VARCHAR(50),  -- 'parcels', 'targets', 'full'
    file_name VARCHAR(500),
    records_imported INTEGER,
    status VARCHAR(50),  -- 'success', 'failed', 'partial'
    error_log TEXT,
    imported_by VARCHAR(100),
    import_batch VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Statistics Cache (for performance)
CREATE TABLE stats_cache (
    cache_id SERIAL PRIMARY KEY,
    city_id INTEGER REFERENCES cities(city_id) ON DELETE CASCADE,
    cache_key VARCHAR(200) NOT NULL,
    cache_data JSONB,
    expires_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(city_id, cache_key)
);
```

### 2.3 SQLAlchemy Models
- [x] Create `database/models.py`: ✅ **All models created (City, CityConfig, Parcel, TargetOwner, ImportHistory, StatsCache)**
```python
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Decimal, ForeignKey, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.declarative import declarative_base
from geoalchemy2 import Geometry
from datetime import datetime

Base = declarative_base()

class City(Base):
    __tablename__ = 'cities'
    
    city_id = Column(Integer, primary_key=True)
    city_name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(200), nullable=False)
    state = Column(String(50))
    center_lat = Column(Decimal(10, 8), nullable=False)
    center_lng = Column(Decimal(11, 8), nullable=False)
    zoom_level = Column(Integer, default=11)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class CityConfig(Base):
    __tablename__ = 'city_configs'
    
    config_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'))
    valid_property_types = Column(JSONB)
    column_mappings = Column(JSONB)
    data_sources = Column(JSONB)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Parcel(Base):
    __tablename__ = 'parcels'
    
    parcel_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'))
    parcel_pin = Column(String(50), nullable=False)
    geometry = Column(Geometry('GEOMETRY', srid=4326))
    
    address = Column(String(300))
    par_zip = Column(String(10))
    
    deeded_owner = Column(String(300))
    owner_clean = Column(String(300))
    
    tax_luc_description = Column(String(200))
    
    sales_amount = Column(Decimal(15, 2))
    certified_tax_total = Column(Decimal(15, 2))
    
    source_file = Column(String(500))
    import_batch = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)

class TargetOwner(Base):
    __tablename__ = 'target_owners'
    
    target_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'))
    owner_clean = Column(String(300), nullable=False)
    category = Column(String(100))
    notes = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class ImportHistory(Base):
    __tablename__ = 'import_history'
    
    import_id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.city_id', ondelete='CASCADE'))
    import_type = Column(String(50))
    file_name = Column(String(500))
    records_imported = Column(Integer)
    status = Column(String(50))
    error_log = Column(Text)
    imported_by = Column(String(100))
    import_batch = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
```

### 2.4 Database Manager
- [x] Create `database/db_manager.py`: ✅ **Complete with connection pooling, session management, PostGIS detection**
```python
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from contextlib import contextmanager
import os
from dotenv import load_dotenv
from typing import Optional

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.db_url = self._build_db_url()
        self.engine = None
        self.SessionLocal = None
    
    def _build_db_url(self) -> str:
        """Build database URL from environment variables"""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        database = os.getenv('DB_NAME', 'multi_city_gis')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', '')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{database}"
    
    def initialize(self):
        """Initialize database connection and create tables"""
        from database.models import Base
        
        self.engine = create_engine(self.db_url, echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)
        
        # Create all tables
        Base.metadata.create_all(self.engine)
    
    @contextmanager
    def get_session(self) -> Session:
        """Context manager for database sessions"""
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
        """Test database connection"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return True
        except Exception as e:
            print(f"Database connection failed: {e}")
            return False
    
    def get_postgis_version(self) -> Optional[str]:
        """Get PostGIS version"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(text("SELECT PostGIS_version();"))
                return result.scalar()
        except Exception:
            return None

# Singleton instance
db_manager = DatabaseManager()
```

**✅ Checkpoint:** 
- [x] Run schema.sql in PostgreSQL (or let SQLAlchemy auto-create on first run) ✅ **Tables auto-created by app**
- [x] Test database connection with Python script ✅ **Connection verified via setup_verification.py**
- [x] Verify tables created successfully ✅ **All tables created: cities, city_configs, parcels, target_owners, import_history, stats_cache**

---

## Phase 3: Data Processing Migration
**Duration:** 2-3 days | **Priority:** Critical | **STATUS:** ✅ **COMPLETE**

### 3.1 Column Normalizer
- [x] Create `data_processing/normalizer.py`: ✅ **220 lines, 5/5 tests passing**
  - ✅ Port `normalize_columns()` function from ClevelandMap.py
  - ✅ Make it configurable (accept column mappings as parameter)
  - ✅ Port `clean_owner()` function with improved suffix handling
  - ✅ Add validation for required columns
  - ✅ Create comprehensive test suite (`test_normalizer.py`)

### 3.2 CSV Processor
- [x] Create `data_processing/csv_processor.py`: ✅ **360 lines, 6/6 tests passing**
  - ✅ CSV file validation (size, format)
  - ✅ Parse and normalize columns (uses normalizer)
  - ✅ Handle large files (chunked reading support)
  - ✅ Data type coercion (numeric fields, handles invalid values)
  - ✅ Generate `owner_clean` field
  - ✅ Property type filtering
  - ✅ Data summaries and statistics
  - ✅ Create comprehensive test suite (`test_csv_processor.py`)

### 3.3 Shapefile Processor
- [x] Create `data_processing/shapefile_processor.py`: ✅ **513 lines, 8/8 tests passing**
  - ✅ Shapefile validation (check all required files present)
  - ✅ Read with GeoPandas
  - ✅ Normalize columns (integrated with normalizer)
  - ✅ Convert to WGS84 (EPSG:4326) for web mapping
  - ✅ Geometry validation and repair
  - ✅ Handle ZIP archives of shapefiles
  - ✅ CRS detection and transformation
  - ✅ Create comprehensive test suite (`test_shapefile_processor.py`)

### 3.4 Excel Processor
- [x] Create `data_processing/excel_processor.py`: ✅ **465 lines, 8/8 tests passing**
  - ✅ Read target owner lists from Excel (.xlsx, .xls, .xlsm)
  - ✅ Support multiple sheets (list, load individual or all)
  - ✅ Normalize owner names (uses clean_owner function)
  - ✅ Auto-detect owner columns
  - ✅ Remove duplicates and empty values
  - ✅ File information and validation
  - ✅ Windows file locking handling
  - ✅ Create comprehensive test suite (`test_excel_processor.py`)

### 3.5 Portfolio Analyzer
- [x] Create `data_processing/analyzer.py`: ✅ **458 lines, 7/7 tests passing**
  - ✅ Port `owner_stats()` function with improvements
  - ✅ Port `aggregate_stats()` function
  - ✅ Add ZIP breakdown calculations
  - ✅ Filter to target owners
  - ✅ Generate stats for multiple owners in batch
  - ✅ Handle empty data gracefully
  - ✅ Export analysis to Excel
  - ✅ Summary table generation
  - ✅ Create comprehensive test suite (`test_analyzer.py`)

**Key Functions Migrated:**
```python
# Successfully ported from ClevelandMap.py:
✅ owner_stats(df: pd.DataFrame, owner: str) -> dict
✅ aggregate_stats(df: pd.DataFrame) -> dict
✅ clean_owner(name) -> str
✅ normalize_columns(df: pd.DataFrame) -> pd.DataFrame
```

**✅ Checkpoint - ALL TESTS PASSING:** 
- [x] Test CSV processing with Cleveland-style data ✅ **6/6 tests pass**
- [x] Test shapefile processing with geometry validation ✅ **8/8 tests pass**
- [x] Test Excel owner list extraction ✅ **8/8 tests pass**
- [x] Verify owner statistics calculations ✅ **7/7 tests pass**
- [x] Test data normalization pipeline ✅ **5/5 tests pass**

**📊 Phase 3 Summary:**
- **5 production modules created**: 2,016 lines of code
- **5 comprehensive test suites**: 1,200+ lines of tests
- **34/34 tests passing**: 100% success rate
- **All Cleveland data operations supported**: Ready for integration

---

## Phase 4: Map Generation (City-Agnostic)
**Duration:** 2 days | **Priority:** High | **STATUS:** ✅ **COMPLETE**

### 4.1 Map Styles Configuration
- [x] Create `mapping/styles.py`: ✅ **610 lines, 6/6 tests passing**
  - ✅ Color schemes for owner layers (matplotlib colormaps)
  - ✅ Base layer styles (context, owner, ZIP)
  - ✅ Popup/tooltip templates with field aliases
  - ✅ Layer control configurations
  - ✅ HTML/CSS templates for sidebar
  - ✅ Utility functions (sanitization, slugification)
  - ✅ Create comprehensive test suite (`test_styles.py` - 6/6 tests passing)

### 4.2 Layer Builder
- [x] Create `mapping/layer_builder.py`: ✅ **530 lines, 9/9 tests passing**
  - ✅ Build base context layer (all target owners)
  - ✅ Build per-owner layers with colors
  - ✅ Build ZIP-based layers with owner coloring
  - ✅ Generate popups and tooltips dynamically
  - ✅ Handle empty datasets gracefully
  - ✅ Integration with styles module
  - ✅ Comprehensive test suite (`test_layer_builder.py` - 9/9 tests passing)

### 4.3 Map Generator
- [x] Create `mapping/map_generator.py`: ✅ **850+ lines, 17/17 tests passing**
  - ✅ Port core Folium map creation logic
  - ✅ Accept city coordinates and zoom as parameters
  - ✅ Generate map from database queries (not CSV files)
  - ✅ Embed JavaScript for layer toggling
  - ✅ Generate sidebar HTML dynamically
  - ✅ Return Folium map object
  - ✅ Create comprehensive test suite (`test_map_generator.py` - 17/17 tests passing)

**Core Logic Successfully Ported:**
```python
# From ClevelandMap.py lines 247-443 (map building)
# Successfully made city-agnostic with parameters:
def generate_map(
    city_config: dict,
    parcels_gdf: gpd.GeoDataFrame,
    target_owners: list,
    stats_per_owner: dict,
    all_stats: dict
) -> folium.Map
```

### 4.4 JavaScript Integration
- [x] Port layer toggle JavaScript (lines 384-442) ✅ **Integrated into map_generator.py**
- [x] Make it work with Streamlit's iframe rendering ✅ **Compatible with Folium/Streamlit**
- [x] Test layer visibility controls ✅ **Tested in test suite**

**✅ Checkpoint PASSED:** 
- ✅ Generate a map programmatically from Cleveland data
- ✅ Verify all layers render correctly
- ✅ Test sidebar interactions
- ✅ All 17 tests passing

---

## Phase 5: Streamlit UI Development
**Duration:** 3-4 days | **Priority:** High

### 5.1 Main Application Entry Point
- [x] Create `app/main.py`: ✅ **Complete Streamlit app with database initialization, navigation, system status**
```python
import streamlit as st
from database.db_manager import db_manager

st.set_page_config(
    page_title="Multi-City GIS Portfolio Analyzer",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
if 'db_initialized' not in st.session_state:
    db_manager.initialize()
    st.session_state.db_initialized = True

# Main page content
st.title("🏘️ Multi-City GIS Portfolio Analyzer")
st.markdown("Select a city from the sidebar or upload new data to get started.")

# Add navigation instructions
with st.expander("📖 Getting Started"):
    st.markdown("""
    1. **View Cities**: Navigate to the Home page to see all available cities
    2. **Explore Maps**: Use the Map Viewer to interact with property data
    3. **Upload Data**: Add new cities via the Upload Data page
    4. **Configure**: Adjust settings in the Settings page
    """)
```

### 5.2 Home Page (City Dashboard)
- [ ] Create `ui/pages/1_🏠_Home.py`:
  - Display grid of available cities
  - Show quick stats per city (property count, target owners, etc.)
  - "View Map" button for each city
  - "Add New City" prominent call-to-action
  - Search/filter cities

### 5.3 Map Viewer Page
- [ ] Create `ui/pages/2_🗺️_Map_Viewer.py`:
  - City selector dropdown (top of page)
  - Load parcels and targets for selected city
  - Generate map using `map_generator.py`
  - Embed Folium map using `streamlit-folium`
  - Custom sidebar with portfolio search
  - Owner/ZIP toggle
  - Stats panels
  - Export buttons (download map HTML, export data to Excel)

**Key Layout:**
```python
import streamlit as st
from streamlit_folium import st_folium

col1, col2 = st.columns([1, 3])

with col1:
    # Sidebar content
    st.selectbox("Select Portfolio", options=owners)
    # Stats display
    
with col2:
    # Map display
    st_folium(map_object, width=1200, height=800)
```

### 5.4 Data Upload Page
- [ ] Create `ui/pages/3_📤_Upload_Data.py`:
  
**Step 1: City Information**
  - City name input
  - Display name
  - State selector
  - Center coordinates (lat/lng) - with map preview
  - Zoom level slider

**Step 2: File Upload**
  - CSV file uploader (parcel data)
  - Shapefile uploader (accept .zip of all shapefiles)
  - Excel file uploader (target owners)
  - File validation and preview

**Step 3: Column Mapping**
  - Auto-detect columns
  - Map to standard fields (dropdown for each required field)
  - Preview mapping results

**Step 4: Property Type Configuration**
  - Select valid property types (multi-select from detected values)

**Step 5: Import**
  - Progress bar for import
  - Summary of records imported
  - Error handling and reporting

### 5.5 Settings Page
- [ ] Create `ui/pages/4_⚙️_Settings.py`:
  - Edit city configurations
  - Manage target owner lists
  - Update column mappings
  - Re-import data
  - Delete cities (with confirmation)
  - View import history
  - Database statistics

### 5.6 Reusable Components
- [ ] Create `ui/components/sidebar.py`:
  - Portfolio search component
  - Owner/ZIP toggle component
  - Stats display component

- [ ] Create `ui/components/stats_panel.py`:
  - Format stats nicely
  - Generate ZIP breakdown tables
  - Handle missing data gracefully

- [ ] Create `ui/components/filters.py`:
  - Owner filter component
  - ZIP filter component
  - Property type filter

**✅ Checkpoint:** 
- Navigate through all pages without errors
- Upload Cleveland data through UI
- Generate map from uploaded data
- Verify functionality matches original script

---

## Phase 6: Integration & Testing
**Duration:** 2 days | **Priority:** Medium

### 6.1 End-to-End Testing
- [ ] Test complete workflow: Upload Cleveland → View Map → Verify Stats
- [ ] Test with Detroit data (second city)
- [ ] Test with invalid data (error handling)
- [ ] Test edge cases (empty datasets, missing columns)

### 6.2 Performance Optimization
- [ ] Add caching for database queries:
```python
@st.cache_data(ttl=3600)
def load_city_parcels(city_id):
    # Query database
    pass
```
- [ ] Optimize map generation (lazy loading)
- [ ] Add loading spinners for slow operations
- [ ] Implement pagination for large datasets

### 6.3 Error Handling
- [ ] Add try-except blocks around critical operations
- [ ] User-friendly error messages
- [ ] Logging for debugging
- [ ] Validation feedback

### 6.4 Create Utility Functions
- [x] Create `utils/validators.py`: ✅ **Complete with file, data, geometry, coordinate validation**
  - File validation functions
  - Data validation functions
  - Geometry validation

- [x] Create `utils/helpers.py`: ✅ **Complete with formatting, sanitization, parsing utilities**
  - Money formatting
  - Date formatting
  - String sanitization
  - Coordinate validation

- [ ] Create `utils/cache.py`:
  - Cache management
  - Cache invalidation helpers

**✅ Checkpoint:** 
- All tests pass
- No console errors
- Smooth user experience

---

## Phase 7: Documentation & Polish
**Duration:** 1 day | **Priority:** Medium

### 7.1 User Documentation
- [x] Create comprehensive `README.md` with: ✅ **744 lines including LLM context section**
  - Project description
  - Installation instructions
  - Usage guide
  - Configuration options
  - LLM assistant guidance

- [x] Create `SETUP_INSTRUCTIONS.md`: ✅ **Complete setup guide with troubleshooting**
  - Step-by-step setup
  - Troubleshooting section
  - Development workflow

- [x] Create `IMPLEMENTATION_ROADMAP.md`: ✅ **This file - 1,143 lines**
  - Detailed phase breakdown
  - Code examples
  - Checkboxes for tracking

- [ ] Add inline help text in UI
- [ ] Create video walkthrough (optional)

### 7.2 Code Documentation
- [ ] Add docstrings to all functions
- [ ] Add type hints
- [ ] Add comments for complex logic
- [ ] Create API documentation (if building REST API)

### 7.3 UI Polish
- [ ] Consistent styling across pages
- [ ] Add icons and visual improvements
- [ ] Loading states for all async operations
- [ ] Success/error notifications
- [ ] Responsive design checks

**✅ Checkpoint:** 
- Documentation complete and accurate
- Code is readable and well-commented
- UI is polished and professional

---

## Phase 8: Deployment Preparation
**Duration:** 1-2 days | **Priority:** High

### 8.1 Production Configuration
- [ ] Create production `.env` template
- [ ] Setup secrets management for Streamlit Cloud
- [ ] Configure database connection pooling
- [ ] Set appropriate cache TTL values
- [ ] Configure upload size limits

### 8.2 Database Migration
- [ ] Export schema as migration script
- [ ] Create seed data scripts (optional)
- [ ] Setup automated backups

### 8.3 Security Checklist
- [ ] Remove hardcoded credentials
- [ ] Validate all user inputs
- [ ] Sanitize file uploads
- [ ] Add rate limiting (if needed)
- [ ] HTTPS enforcement (handled by hosting)

### 8.4 Deployment Options Setup

**Option 1: Streamlit Cloud (Recommended)**
- [ ] Push code to GitHub repository
- [ ] Connect Streamlit Cloud to GitHub
- [ ] Configure secrets in Streamlit Cloud dashboard
- [ ] Setup PostgreSQL on cloud (ElephantSQL, Heroku Postgres, or Supabase)
- [ ] Deploy and test

**Option 2: Heroku**
- [ ] Create `Procfile`:
```
web: streamlit run app/main.py --server.port=$PORT
```
- [ ] Create `runtime.txt`:
```
python-3.11.6
```
- [ ] Add Heroku Postgres add-on
- [ ] Deploy via Heroku CLI or GitHub integration

**Option 3: Docker (Self-hosted)**
- [x] Create `docker-compose.yml` for local development: ✅ **Created with PostgreSQL + PostGIS + optional pgAdmin**
- [ ] Create `Dockerfile` for production deployment:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    postgresql-client \
    gdal-bin \
    libgdal-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app/main.py", "--server.address=0.0.0.0"]
```


**✅ Checkpoint:** 
- Application deployed successfully
- Can access from public URL
- Database connected
- All features working in production

---

## Phase 9: Migration of Existing Data
**Duration:** 1 day | **Priority:** High

### 9.1 Cleveland Data Migration Script
- [ ] Create `scripts/migrate_cleveland.py`:
  - Load existing Cleveland CSV, SHP, and Excel files
  - Create Cleveland city record
  - Create city config with current settings
  - Import all parcels
  - Import target owners
  - Verify import success

### 9.2 Verification
- [ ] Compare original HTML output with new app output
- [ ] Verify parcel counts match
- [ ] Verify statistics match
- [ ] Verify map layers render identically

### 9.3 Detroit Data Preparation
- [ ] Review Detroit data structure
- [ ] Create Detroit city config
- [ ] Import Detroit data through UI or script
- [ ] Test Detroit map generation

**✅ Checkpoint:** 
- Cleveland data fully migrated and functional
- Detroit data loaded successfully
- Both cities accessible from dashboard

---

## Phase 10: Advanced Features (Optional)
**Duration:** 2-3 days | **Priority:** Low

### 10.1 Export Enhancements
- [ ] PDF report generation
- [ ] Excel export with formatting
- [ ] Export filtered datasets
- [ ] Export map as image

### 10.2 Comparison Tools
- [ ] Side-by-side city comparison
- [ ] Owner portfolio across multiple cities
- [ ] Statistical comparisons

### 10.3 Authentication (if needed)
- [ ] Add Streamlit authentication
- [ ] User roles (viewer, editor, admin)
- [ ] Audit logging

### 10.4 Scheduled Data Updates
- [ ] Setup automated data refresh scripts
- [ ] Email notifications for data updates
- [ ] Data change tracking

**✅ Checkpoint:** 
- Advanced features working as expected
- No negative impact on core functionality

---

## Post-Deployment Checklist

### Monitoring & Maintenance
- [ ] Setup application monitoring (Uptime Robot, Pingdom, etc.)
- [ ] Configure error tracking (Sentry, etc.)
- [ ] Setup database backup schedule
- [ ] Create runbook for common issues
- [ ] Plan for regular dependency updates

### User Onboarding
- [ ] Create user guide
- [ ] Record demo video
- [ ] Setup support channel (if needed)
- [ ] Gather initial user feedback

---

## Success Metrics

### Technical Metrics
- [ ] Page load time < 3 seconds
- [ ] Map renders in < 5 seconds for datasets with 50k+ parcels
- [ ] Database queries < 1 second (with proper indexing)
- [ ] 99%+ uptime

### Functional Metrics
- [ ] All original features working
- [ ] Can add new city in < 10 minutes
- [ ] Users can navigate without documentation
- [ ] Zero data loss during imports

---

## Troubleshooting Guide

### Common Issues

**Database Connection Failed**
- Check `.env` file credentials
- Verify PostgreSQL is running
- Test connection with `psql` command
- Check firewall rules

**Large File Upload Fails**
- Increase `maxUploadSize` in `.streamlit/config.toml`
- Check server memory limits
- Consider chunked upload for files > 500MB

**Map Rendering Slow**
- Add spatial indexes to database
- Implement geometry simplification
- Use clustering for dense areas
- Cache map components

**Import Errors**
- Validate all required shapefile components present
- Check column mappings
- Verify CRS is set correctly
- Review error logs in import_history table

---

## Timeline Summary

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Setup | 1 day | None |
| Phase 2: Database | 1-2 days | Phase 1 |
| Phase 3: Data Processing | 2-3 days | Phase 2 |
| Phase 4: Map Generation | 2 days | Phase 3 |
| Phase 5: UI Development | 3-4 days | Phase 2-4 |
| Phase 6: Testing | 2 days | Phase 5 |
| Phase 7: Documentation | 1 day | Phase 6 |
| Phase 8: Deployment | 1-2 days | Phase 7 |
| Phase 9: Data Migration | 1 day | Phase 8 |
| **Total (Critical Path)** | **14-19 days** | Sequential |

---

## Resource Requirements

### Development
- Python 3.9+
- PostgreSQL 14+ with PostGIS
- 8GB+ RAM (for processing large datasets)
- 50GB+ disk space (for shapefiles and database)

### Production (Streamlit Cloud Free Tier)
- 1GB RAM (limited to smaller datasets)
- Shared CPU
- External PostgreSQL required

### Production (Heroku/Self-hosted)
- 2-4GB RAM recommended
- 2 CPU cores
- 20GB+ disk space
- PostgreSQL database (separate or included)

---

## Next Steps

After completing this roadmap:
1. ✅ Review plan with stakeholders **DONE**
2. ✅ Setup development environment (Phase 1) **DONE - All packages installed, database running**
3. ✅ Complete Phase 2 (Database setup) **DONE - All tables created, app running successfully**
4. 🔄 Begin Phase 3 (Data Processing Migration) **READY TO START**
   - Port normalize_columns() function from ClevelandMap.py
   - Port clean_owner() function
   - Create CSV, Shapefile, and Excel processors
   - Port statistics calculation functions
5. ⏭️ Continue through Phase 4-5 (Map Generation & UI)
6. 🎯 Deploy MVP with Cleveland + Detroit
7. 📊 Gather feedback and iterate

## Current Status Summary (Updated: 2025-11-12)

### ✅ Completed
- **Pre-Implementation Setup**: Python 3.13.1, Virtual env, PostgreSQL 14.9, PostGIS 3.3 ✅
- **Phase 1: Project Structure**: All directories, config files, requirements.txt, .gitignore ✅ **COMPLETE**
- **Phase 2: Database Architecture**: Database running, schema implemented, all tables created, connection verified ✅ **COMPLETE**
- **Phase 3: Data Processing Migration**: All 5 modules created, 34/34 tests passing ✅ **COMPLETE**
- **Documentation**: README.md, SETUP_INSTRUCTIONS.md, IMPLEMENTATION_ROADMAP.md ✅
- **Utilities**: helpers.py and validators.py created ✅
- **Application Core**: app/config.py and app/main.py running successfully ✅
- **Environment Configuration**: .env file created with working credentials ✅

### 🎉 Application Status
- **✅ App Running**: Successfully launched at http://localhost:8501
- **✅ Database Connected**: All 6 tables created and accessible
- **✅ All Checks Passing**: setup_verification.py shows 6/6 checks passed
- **✅ PostGIS Working**: Spatial capabilities confirmed
- **✅ Data Processing Ready**: All 5 processors tested and working (34/34 tests pass)

### 🎊 Phase 3 Complete! - Data Processing
- ✅ `data_processing/normalizer.py` - 220 lines, 5/5 tests ✅
- ✅ `data_processing/csv_processor.py` - 360 lines, 6/6 tests ✅
- ✅ `data_processing/shapefile_processor.py` - 513 lines, 8/8 tests ✅
- ✅ `data_processing/excel_processor.py` - 465 lines, 8/8 tests ✅
- ✅ `data_processing/analyzer.py` - 458 lines, 7/7 tests ✅

### 🎉 Phase 4 Complete! - Map Generation
- ✅ `mapping/styles.py` - 610 lines, 6/6 tests ✅
- ✅ `mapping/layer_builder.py` - 530 lines, 9/9 tests ✅
- ✅ `mapping/map_generator.py` - 850 lines, 17/17 tests ✅

### ✅ Phase 4 Complete! - Map Generation
- ✅ `mapping/styles.py` (610 lines, 6/6 tests) - color schemes, popup templates
- ✅ `mapping/layer_builder.py` (530 lines, 9/9 tests) - layer generation
- ✅ `mapping/map_generator.py` (850 lines, 17/17 tests) - Folium map creation
- ✅ JavaScript layer toggle functionality integrated
- ✅ Ready for Streamlit rendering integration

### 📊 Progress Metrics
- **Phases Completed**: 4 of 10 (40%) ⬆️
- **Setup Complete**: 100% ✅
- **Database Infrastructure**: 100% ✅
- **Application Foundation**: 100% ✅
- **Data Processing**: 100% ✅
- **Map Generation**: 100% ✅
- **Production Code Files**: 35+ files
- **Lines Written**: ~12,000+ (code + tests + documentation)
- **Test Coverage**: 66/66 tests passing (100%) ✅
- **Ready for**: UI development and Streamlit integration

---

## Notes & Considerations

- **Data Security**: If handling sensitive data, consider encryption at rest
- **Scalability**: Current design handles ~100k parcels/city comfortably
- **Customization**: All city-specific logic is configurable, not hardcoded
- **Backup**: Implement regular database backups before production use
- **Cost**: Streamlit Cloud free tier suitable for internal use; paid plans for external users

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-12  
**Author:** AI Assistant  
**Project:** Multi-City GIS Portfolio Analyzer

