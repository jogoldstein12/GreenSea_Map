# CLAUDE.md - AI Assistant Guide for Green Sea Map Project

**Last Updated:** 2025-11-14
**Project Version:** 2.0 (in development)
**Project Name:** Multi-City GIS Portfolio Analyzer (formerly "Green Sea Map")

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Architecture & Technology Stack](#architecture--technology-stack)
3. [Codebase Structure](#codebase-structure)
4. [Database Schema](#database-schema)
5. [Key Modules & Components](#key-modules--components)
6. [Development Workflow](#development-workflow)
7. [Coding Conventions](#coding-conventions)
8. [Common Tasks](#common-tasks)
9. [Current State & Progress](#current-state--progress)
10. [Testing Strategy](#testing-strategy)
11. [Important Context](#important-context)
12. [Do's and Don'ts](#dos-and-donts)

---

## Project Overview

### Purpose

The Multi-City GIS Portfolio Analyzer is a web-based geospatial analysis tool for real estate portfolio analysis across multiple cities. It enables users to:

- Visualize property ownership portfolios on interactive maps
- Analyze investment patterns by owner and ZIP code
- Upload and manage data for multiple cities
- Generate statistical reports on property holdings
- Identify and track target investors across markets

### Project History

- **v1.0 (Original):** Single Python script (`ClevelandMap.py`) that generated static HTML maps for Cleveland, OH only
- **v2.0 (Current):** Complete redesign as a scalable Streamlit web application with PostgreSQL backend, supporting unlimited cities with dynamic data upload

### Business Context

This tool is used for real estate investment analysis to:
- Identify portfolio owners with 10-100 properties (sweet spot for wholesaling)
- Analyze geographic concentration of holdings
- Track sales activity and property values
- Support investment decision-making

---

## Architecture & Technology Stack

### Core Technologies

| Category | Technology | Version | Purpose |
|----------|-----------|---------|---------|
| **Language** | Python | 3.9+ | Primary language |
| **Web Framework** | Streamlit | 1.29+ | Web UI |
| **Database** | PostgreSQL | 14+ | Relational data |
| **Spatial Extension** | PostGIS | 3.3+ | Geospatial queries |
| **ORM** | SQLAlchemy | 2.0+ | Database abstraction |
| **Geospatial** | GeoPandas | 0.14+ | Spatial data manipulation |
| **Mapping** | Folium | 0.15+ | Interactive maps |
| **Data Processing** | Pandas | 2.1+ | Tabular data |

### Architecture Pattern

**Multi-tier Architecture:**
```
┌─────────────────────────────────────┐
│   Streamlit UI (ui/pages/)          │
├─────────────────────────────────────┤
│   Business Logic (mapping/,         │
│   data_processing/, data_import/)   │
├─────────────────────────────────────┤
│   Data Access (database/)           │
├─────────────────────────────────────┤
│   PostgreSQL + PostGIS              │
└─────────────────────────────────────┘
```

**Key Principles:**
- Separation of concerns (UI, logic, data)
- Database-first design
- Configuration over code
- Reusable processors and generators

---

## Codebase Structure

### Directory Tree

```
GreenSea_Map/
├── app/                          # Streamlit application entry
│   ├── main.py                   # App entry point, DB init, routing
│   ├── config.py                 # App configuration (from .env)
│   └── pages/
│       ├── 1_Home.py             # Portfolio dashboard
│       ├── 2_Map_Viewer.py       # Interactive map viewer
│       └── 3_Upload_Data.py      # Data upload wizard
│
├── database/                     # Database layer
│   ├── models.py                 # SQLAlchemy models (6 tables)
│   ├── db_manager.py             # Connection pooling, sessions
│   └── schema.sql                # SQL schema (backup/reference)
│
├── data_processing/              # Core data transformation
│   ├── normalizer.py             # Column normalization, owner cleaning
│   ├── csv_processor.py          # CSV parsing and validation
│   ├── shapefile_processor.py    # Shapefile handling, CRS conversion
│   ├── excel_processor.py        # Excel target owner lists
│   └── analyzer.py               # Portfolio statistics calculation
│
├── data_import/                  # Import orchestration
│   └── import_manager.py         # Coordinates import workflow
│
├── mapping/                      # Map generation
│   ├── styles.py                 # Color schemes, popup templates
│   ├── layer_builder.py          # Folium layer creation
│   └── map_generator.py          # Complete map assembly
│
├── ui/                           # UI components and styling
│   ├── components/
│   │   └── navigation.py         # Shared navigation component
│   └── styles/
│       └── glass_theme.css       # Dark glassmorphism theme
│
├── utils/                        # Helper utilities
│   ├── validators.py             # Data validation functions
│   └── helpers.py                # Formatting, sanitization
│
├── tests/                        # Test suites
│   ├── test_*.py                 # Unit tests (66 tests total)
│   └── setup_verification.py     # Database connectivity test
│
├── Documents/                    # Project documentation
│   ├── README.md                 # Main project documentation
│   ├── IMPLEMENTATION_ROADMAP.md # Phase-by-phase plan
│   ├── PHASE5_TODO_CHECKLIST.md  # Current phase checklist
│   └── SETUP_INSTRUCTIONS.md     # Development setup guide
│
├── examples/                     # Example scripts
│   └── generate_sample_map.py    # Sample map generation
│
├── .env                          # Environment variables (gitignored)
├── .env.example                  # Environment template
├── requirements.txt              # Python dependencies
├── docker-compose.yml            # Local PostgreSQL + PostGIS
└── CLAUDE.md                     # This file
```

### Module Responsibilities

| Module | Lines | Tests | Purpose |
|--------|-------|-------|---------|
| `data_processing/normalizer.py` | 220 | 5/5 ✅ | Column name standardization, owner name cleaning |
| `data_processing/csv_processor.py` | 360 | 6/6 ✅ | CSV validation, parsing, filtering |
| `data_processing/shapefile_processor.py` | 513 | 8/8 ✅ | Shapefile handling, geometry validation, CRS conversion |
| `data_processing/excel_processor.py` | 465 | 8/8 ✅ | Excel target owner extraction |
| `data_processing/analyzer.py` | 458 | 7/7 ✅ | Portfolio statistics (per-owner, aggregate, ZIP) |
| `mapping/styles.py` | 610 | 6/6 ✅ | Color generation, popup templates, HTML/CSS |
| `mapping/layer_builder.py` | 530 | 9/9 ✅ | Folium layer creation (owner, ZIP, context) |
| `mapping/map_generator.py` | 850 | 17/17 ✅ | Complete map assembly with JS controls |
| `data_import/import_manager.py` | 487 | Manual | Orchestrates complete import workflow |
| `database/db_manager.py` | 160 | Manual | Connection pooling, session management |
| `database/models.py` | 131 | Manual | 6 SQLAlchemy models |

**Total Production Code:** ~12,000+ lines
**Total Test Code:** ~3,000+ lines
**Test Coverage:** 66/66 passing (100%)

---

## Database Schema

### Tables Overview

```sql
cities              -- City metadata and map settings
city_configs        -- Per-city configuration (JSONB)
parcels             -- Main parcel data with geometries
target_owners       -- Lists of investors to analyze
import_history      -- Audit trail of uploads
stats_cache         -- Performance optimization cache
```

### Key Tables Detail

#### `cities`
Stores city information and map display settings.
```sql
city_id             SERIAL PRIMARY KEY
city_name           VARCHAR(100) UNIQUE     -- e.g., "cleveland"
display_name        VARCHAR(200)            -- e.g., "Cleveland, OH"
state               VARCHAR(50)
center_lat          DECIMAL(10, 8)          -- Map center
center_lng          DECIMAL(11, 8)
zoom_level          INTEGER DEFAULT 11
is_active           BOOLEAN DEFAULT TRUE
created_at, updated_at TIMESTAMP
```

#### `parcels`
Main geospatial table with property data.
```sql
parcel_id           SERIAL PRIMARY KEY
city_id             INTEGER FK → cities
parcel_pin          VARCHAR(50)             -- Unique parcel identifier
geometry            GEOMETRY(4326)          -- PostGIS geometry (WGS84)
address             VARCHAR(300)
par_zip             VARCHAR(10)
deeded_owner        VARCHAR(300)            -- Raw owner name
owner_clean         VARCHAR(300)            -- Normalized owner name
tax_luc_description VARCHAR(200)            -- Land use type
sales_amount        DECIMAL(15, 2)
certified_tax_total DECIMAL(15, 2)
source_file, import_batch, created_at

UNIQUE(city_id, parcel_pin)
INDEX on geometry (GIST), city_id, owner_clean, par_zip
```

#### `city_configs`
Flexible configuration using JSONB.
```sql
config_id           SERIAL PRIMARY KEY
city_id             INTEGER FK → cities
valid_property_types JSONB                  -- ["1-FAMILY PLATTED LOT", ...]
column_mappings     JSONB                   -- {"owner": "deeded_owner", ...}
data_sources        JSONB                   -- File metadata
updated_at          TIMESTAMP
```

#### `target_owners`
Investors to track and analyze.
```sql
target_id           SERIAL PRIMARY KEY
city_id             INTEGER FK → cities
owner_clean         VARCHAR(300)            -- Matches parcels.owner_clean
category            VARCHAR(100)            -- e.g., "Portfolio Targets (10-100)"
notes               TEXT
is_active           BOOLEAN DEFAULT TRUE
created_at          TIMESTAMP

UNIQUE(city_id, owner_clean)
```

### Critical Relationships

- All tables cascade delete when city is deleted (`ON DELETE CASCADE`)
- `parcels.owner_clean` matches `target_owners.owner_clean` (case-sensitive)
- Spatial queries use `parcels.geometry` with PostGIS functions
- JSONB fields allow flexible, schema-less config storage

---

## Key Modules & Components

### Data Processing Pipeline

#### 1. `normalizer.py`
**Functions:**
- `normalize_columns(df, column_mappings)` - Maps various column names to standard schema
- `clean_owner(name)` - Standardizes owner names (uppercase, remove punctuation, legal suffixes)

**Example:**
```python
from data_processing.normalizer import clean_owner

clean_owner("Smith Properties, LLC.")  # Returns: "SMITH PROPERTIES"
```

**Column Mapping Logic:**
```python
{
    "deeded_owner": ["deeded_owner", "deeded_own", "deed_owner", "ownername"],
    "parcelpin": ["parcelpin", "parcel_pin", "parcel_id", "pin"],
    # ... handles many variations
}
```

#### 2. `csv_processor.py`
**Class:** `CSVProcessor`

**Key Methods:**
- `load_csv(file_path)` - Load and validate CSV
- `normalize_columns()` - Apply column normalization
- `filter_property_types(types)` - Keep only valid property types
- `generate_owner_clean()` - Create normalized owner field
- `get_summary()` - Return data statistics

**Usage Pattern:**
```python
processor = CSVProcessor(csv_path)
processor.normalize_columns(mappings)
processor.filter_property_types(["1-FAMILY PLATTED LOT"])
df = processor.get_dataframe()
```

#### 3. `shapefile_processor.py`
**Class:** `ShapefileProcessor`

**Key Methods:**
- `load_shapefile(path_or_zip)` - Load from .shp or .zip
- `normalize_columns()` - Apply column normalization
- `convert_to_wgs84()` - Transform to EPSG:4326
- `validate_geometries()` - Check and repair invalid geometries
- `get_geodataframe()` - Return GeoDataFrame

**CRS Handling:**
- Auto-detects source CRS from .prj file
- Converts all to WGS84 (EPSG:4326) for web mapping
- Handles missing CRS with fallback to common projections

#### 4. `analyzer.py`
**Functions:**
- `owner_stats(df, owner_name)` - Calculate stats for one owner
- `aggregate_stats(df)` - Calculate stats for all target owners
- `zip_breakdown(df, owner_name)` - Geographic distribution
- `export_to_excel(stats, filepath)` - Export analysis

**Statistics Calculated:**
```python
{
    'property_count': int,
    'total_sales': float,
    'total_assessed': float,
    'avg_sales': float,
    'avg_assessed': float,
    'zip_codes': int,
    'zip_breakdown': {zip_code: count}
}
```

### Map Generation

#### 5. `map_generator.py`
**Class:** `MapGenerator`

**Initialization:**
```python
generator = MapGenerator(
    city_config={
        'center_lat': 41.5,
        'center_lng': -81.7,
        'zoom_level': 11,
        'display_name': 'Cleveland, OH'
    },
    parcels_gdf=gdf,
    target_owners=['OWNER A', 'OWNER B'],
    stats_per_owner={...},
    all_stats={...}
)
```

**Map Generation:**
```python
folium_map = generator.generate_map(
    include_layer_control=True,
    tile_layer="light",
    use_clustering=False,
    view_mode="By Owner"
)
```

**Features:**
- Base context layer (all target owner parcels)
- Per-owner colored layers
- ZIP-based grouping layers
- Interactive sidebar with JavaScript controls
- Layer toggle dropdown
- Custom popups with property details

#### 6. `layer_builder.py`
**Class:** `LayerBuilder`

**Responsibilities:**
- Creates Folium feature groups for each owner
- Generates popups and tooltips
- Handles empty datasets gracefully
- Applies color schemes consistently

### Data Import

#### 7. `import_manager.py`
**Class:** `ImportManager`

**Complete Import Workflow:**
```python
manager = ImportManager(
    city_name='cleveland',
    display_name='Cleveland, OH',
    state='Ohio',
    center_lat=41.5,
    center_lng=-81.7,
    csv_file=csv_path,
    shapefile_zip=shp_zip,
    excel_file=excel_path,
    column_mappings={...},
    valid_property_types=[...]
)

result = manager.execute_import()
# Returns: {
#     'success': bool,
#     'city_id': int,
#     'parcels_imported': int,
#     'targets_imported': int,
#     'errors': []
# }
```

**Transaction Handling:**
- All-or-nothing import (rollback on failure)
- Temp file cleanup
- Error logging to database
- Progress tracking

---

## Development Workflow

### Phase-Based Development

The project follows a **10-phase roadmap** (see `Documents/IMPLEMENTATION_ROADMAP.md`):

| Phase | Status | Description |
|-------|--------|-------------|
| 1 | ✅ Complete | Project structure & dependencies |
| 2 | ✅ Complete | Database architecture |
| 3 | ✅ Complete | Data processing migration |
| 4 | ✅ Complete | Map generation |
| 5 | 🔄 In Progress (72%) | Streamlit UI development |
| 6 | ⏳ Pending | Integration & testing |
| 7 | ⏳ Pending | Documentation & polish |
| 8 | ⏳ Pending | Deployment preparation |
| 9 | ⏳ Pending | Data migration (Cleveland/Detroit) |
| 10 | ⏳ Pending | Advanced features (optional) |

### Current Phase: Phase 5 - UI Development

**Completed:**
- ✅ Global glassmorphism theme (CSS)
- ✅ Home page (portfolio dashboard)
- ✅ Map Viewer page
- ✅ Upload Data wizard (5-step form)
- ✅ Data import backend integration

**In Progress:**
- Settings page (medium priority)
- Reusable UI components (low priority)
- Testing & polish

### Git Workflow

**Branching:**
- Main branch: `main` (or `master`)
- Feature branch: `claude/claude-md-mhz8vnk8xwkn13d8-01NawNDESKG7jxy4AEU1d7dz`

**Commit Guidelines:**
- Descriptive messages focused on "why" not "what"
- Reference phase/task if applicable
- Test before committing

**Important:** Always work on the designated Claude branch, not main.

---

## Coding Conventions

### Python Style

**PEP 8 Compliance:**
- 4 spaces for indentation (not tabs)
- Max line length: 100 characters (flexible)
- Imports: stdlib → third-party → local

**Type Hints:**
```python
def normalize_columns(
    df: pd.DataFrame,
    column_mappings: Optional[Dict[str, List[str]]] = None
) -> pd.DataFrame:
    """Docstring here"""
    pass
```

**Docstrings:**
All public functions require docstrings:
```python
"""
Brief description.

Longer explanation if needed.

Args:
    param1: Description
    param2: Description

Returns:
    Description of return value

Example:
    >>> normalize_columns(df)
    <DataFrame>
"""
```

### Database Patterns

**Session Management:**
Always use context manager:
```python
with db_manager.get_session() as session:
    cities = session.query(City).all()
    # Automatic commit/rollback
```

**Don't:**
```python
session = db_manager.SessionLocal()  # ❌ Manual management
cities = session.query(City).all()
session.close()  # ❌ Easy to forget
```

**Spatial Queries:**
```python
from geoalchemy2 import functions as geo_func

parcels = session.query(Parcel).filter(
    geo_func.ST_Within(Parcel.geometry, boundary_geom)
).all()
```

### Streamlit Patterns

**Caching:**
Use for expensive operations:
```python
@st.cache_data(ttl=3600)
def load_city_parcels(city_id: int) -> gpd.GeoDataFrame:
    """Load parcels for a city (cached for 1 hour)"""
    # Database query here
```

**Session State:**
```python
if 'selected_city_id' not in st.session_state:
    st.session_state.selected_city_id = None

st.session_state.selected_city_id = 1
```

**Page Navigation:**
```python
if st.button("View Map"):
    st.switch_page("pages/2_Map_Viewer.py")
```

### File Handling

**Temporary Files:**
```python
import tempfile
from pathlib import Path

temp_dir = Path("data/uploads/temp")
temp_file = temp_dir / f"{uuid.uuid4()}.csv"

# Always clean up
try:
    # Use file
    pass
finally:
    if temp_file.exists():
        temp_file.unlink()
```

---

## Common Tasks

### Task 1: Add Support for a New Column Variation

**Location:** `data_processing/normalizer.py`

```python
# In normalize_columns() function, update column_mappings:
column_mappings = {
    "deeded_owner": [
        "deeded_owner",
        "deeded_own",
        "new_variation_here"  # Add here
    ],
    # ...
}
```

### Task 2: Add a New Property Type Filter

**Location:** Upload wizard or `city_configs` table

```python
# In database (JSONB):
valid_property_types = [
    "1-FAMILY PLATTED LOT",
    "2-FAMILY PLATTED LOT",
    "CONDOMINIUM"  # New type
]
```

### Task 3: Change Map Tile Layer

**Location:** `mapping/map_generator.py`

```python
def _create_base_map(self, tile_layer: str = "light"):
    tiles = {
        "light": "cartodbpositron",
        "dark": "cartodbdark_matter",
        "osm": "OpenStreetMap",
        "satellite": "Esri WorldImagery",
        "custom": "https://..."  # Add custom
    }
```

### Task 4: Modify Owner Name Cleaning Logic

**Location:** `data_processing/normalizer.py`

```python
def clean_owner(name) -> str:
    # Add new suffixes to remove:
    suffixes_to_remove = [
        " LLC", " INC", " CO", " LP",
        " NEW_SUFFIX_HERE"  # Add here
    ]
```

### Task 5: Add a New Statistic to Portfolio Analysis

**Location:** `data_processing/analyzer.py`

```python
def owner_stats(df: pd.DataFrame, owner: str) -> dict:
    stats = {
        'property_count': len(owner_df),
        # ... existing stats
        'new_stat': calculate_new_stat(owner_df)  # Add here
    }
    return stats
```

### Task 6: Query All Cities from Database

```python
from database.db_manager import db_manager
from database.models import City

with db_manager.get_session() as session:
    cities = session.query(City).filter(City.is_active == True).all()
    for city in cities:
        print(f"{city.display_name}: {city.city_id}")
```

### Task 7: Run All Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_normalizer.py -v

# Run with coverage
pytest tests/ --cov=data_processing --cov-report=html
```

### Task 8: Generate a Map Programmatically

```python
from database.db_manager import db_manager
from data_processing.analyzer import aggregate_stats
from mapping.map_generator import MapGenerator
import geopandas as gpd

# Load data
with db_manager.get_session() as session:
    parcels_df = gpd.read_postgis(
        "SELECT * FROM parcels WHERE city_id = 1",
        session.connection(),
        geom_col='geometry'
    )

# Calculate stats
target_owners = ['OWNER A', 'OWNER B']
stats = aggregate_stats(parcels_df, target_owners)

# Generate map
generator = MapGenerator(
    city_config={'center_lat': 41.5, 'center_lng': -81.7, 'zoom_level': 11},
    parcels_gdf=parcels_df,
    target_owners=target_owners,
    stats_per_owner=stats['per_owner'],
    all_stats=stats['aggregate']
)
map_obj = generator.generate_map()
map_obj.save('output.html')
```

---

## Current State & Progress

### What's Working

✅ **Database Layer**
- PostgreSQL + PostGIS running via Docker
- All 6 tables created and indexed
- Connection pooling and session management
- Models tested and verified

✅ **Data Processing (Phase 3)**
- All 5 processors implemented and tested
- 34/34 tests passing
- Handles CSV, Shapefiles, Excel files
- Column normalization robust
- Owner name cleaning works

✅ **Map Generation (Phase 4)**
- Map generator creates Folium maps
- Layer builder creates owner/ZIP layers
- Styling module handles colors and popups
- JavaScript controls integrated
- 32/32 tests passing

✅ **Streamlit UI (Phase 5 - 72% complete)**
- Home page: Portfolio dashboard with stats
- Map Viewer: Interactive map display
- Upload Data: 5-step wizard fully functional
- Data import backend: Actually imports to database
- Glassmorphism theme applied

### What's Not Working / Missing

⚠️ **Phase 5 Remaining (28%)**
- Settings page (not critical for MVP)
- Reusable UI components (nice to have)
- Comprehensive testing suite
- Final integration testing

⏳ **Phase 6-10 (Not Started)**
- End-to-end testing with real data
- Performance optimization
- Deployment configuration
- Cleveland/Detroit data migration
- Advanced features (PDF export, comparisons, auth)

### Known Issues

1. **No real data imported yet** - Database is empty until first upload
2. **Settings page incomplete** - Can't edit city configs via UI yet
3. **No authentication** - App is open to anyone (REQUIRE_AUTH=False)
4. **Export functionality stubbed** - Export buttons exist but don't work

### Recent Changes

**2025-11-13:**
- ✅ Completed data import backend integration
- ✅ Upload wizard now actually imports data
- ✅ Import manager handles complete workflow
- ✅ Transaction rollback on errors

**2025-11-12:**
- ✅ Completed Phase 4 (Map Generation)
- ✅ All 32 mapping tests passing
- ✅ Created Home page and Map Viewer UI

---

## Testing Strategy

### Test Organization

```
tests/
├── test_normalizer.py          # 5 tests
├── test_csv_processor.py       # 6 tests
├── test_shapefile_processor.py # 8 tests
├── test_excel_processor.py     # 8 tests
├── test_analyzer.py            # 7 tests
├── test_styles.py              # 6 tests
├── test_layer_builder.py       # 9 tests
├── test_map_generator.py       # 17 tests
└── setup_verification.py       # Database connectivity check
```

### Running Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/test_normalizer.py -v

# With coverage
pytest tests/ --cov=data_processing --cov=mapping

# Database verification
python tests/setup_verification.py
```

### Test Data

Tests use **in-memory test data**, not real files:
```python
test_df = pd.DataFrame({
    'DEEDED_OWN': ['Smith Properties, LLC'],
    'TAX_LUC_DE': ['1-FAMILY PLATTED LOT'],
    'PARCELPIN': ['123-45-678']
})
```

### Manual Testing Checklist

When making changes, test:
- [ ] Database connection still works
- [ ] CSV processing with sample file
- [ ] Map generates without errors
- [ ] Streamlit pages load
- [ ] Navigation between pages works
- [ ] Session state persists

---

## Important Context

### The v1.0 to v2.0 Migration

**Original Script:** `ClevelandMap.py` (633 lines)
- Single-city only (Cleveland hardcoded)
- Manual file path configuration
- Generates static HTML output
- Rich features but not scalable

**New Application:** Multi-city Streamlit app
- Database-driven (PostgreSQL + PostGIS)
- Web-based upload interface
- Dynamic map generation
- Supports unlimited cities

**Migration Philosophy:**
> "Preserve all existing functionality from v1.0, but make it city-agnostic and database-driven."

**Key Functions Preserved:**
1. `normalize_columns()` - Now in `normalizer.py:10`
2. `clean_owner()` - Now in `normalizer.py:62`
3. `owner_stats()` - Now in `analyzer.py:172`
4. Map generation logic - Now in `map_generator.py:76`

### Data Sources

**Parcel Data:**
- Source: County auditor offices (public records)
- Format: CSV files with parcel attributes
- Key fields: parcel_pin, owner, address, land use, sales, assessments

**Spatial Data:**
- Source: County GIS departments (public records)
- Format: Shapefiles (.shp, .shx, .dbf, .prj)
- Projection: Usually State Plane or NAD83 (converted to WGS84)

**Target Owners:**
- Source: Manually curated Excel lists
- Criteria: Portfolio owners with 10-100 properties
- Purpose: Focus analysis on investment-grade portfolios

### Why This Architecture?

**Database-First:**
- Enables multi-user access
- Supports concurrent analysis
- Historical data tracking
- Easy querying and filtering

**Streamlit:**
- Rapid UI development
- Python-native (no JS required)
- Built-in components
- Easy deployment

**PostGIS:**
- Industry standard for spatial data
- Powerful spatial queries
- Excellent performance with indexes
- Wide tool support

---

## Do's and Don'ts

### ✅ DO

**Code Organization:**
- ✅ Separate UI, logic, and data layers
- ✅ Use type hints for function parameters
- ✅ Write docstrings for all public functions
- ✅ Keep functions focused and small (<50 lines ideal)

**Database:**
- ✅ Use context managers for sessions
- ✅ Always handle connection errors
- ✅ Use spatial indexes for geometry queries
- ✅ Store flexible config in JSONB

**Streamlit:**
- ✅ Cache expensive operations (`@st.cache_data`)
- ✅ Use session state for cross-page data
- ✅ Load CSS on every page
- ✅ Handle empty states gracefully

**Testing:**
- ✅ Run tests before committing
- ✅ Test edge cases (empty data, invalid input)
- ✅ Use fixtures for test data
- ✅ Keep tests isolated (no shared state)

**Data Processing:**
- ✅ Validate data before processing
- ✅ Handle missing/null values
- ✅ Log errors with context
- ✅ Clean up temporary files

### ❌ DON'T

**Anti-Patterns:**
- ❌ Hardcode file paths (use config)
- ❌ Hardcode city names (use database)
- ❌ Mix SQL and business logic
- ❌ Leave database sessions open

**Performance:**
- ❌ Load entire datasets into memory unnecessarily
- ❌ Run same query multiple times (cache it)
- ❌ Generate maps on every Streamlit rerun
- ❌ Skip spatial indexes

**Security:**
- ❌ Commit .env files to git
- ❌ Use string interpolation for SQL (SQL injection risk)
- ❌ Trust user input without validation
- ❌ Expose database credentials in code

**UI/UX:**
- ❌ Let Streamlit rerun expensive operations
- ❌ Show technical errors to users
- ❌ Forget loading indicators
- ❌ Ignore empty states

**Testing:**
- ❌ Skip tests because "it works on my machine"
- ❌ Test against production database
- ❌ Write tests that depend on external files
- ❌ Ignore failing tests

---

## Configuration Reference

### Environment Variables (.env)

```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=multi_city_gis
DB_USER=postgres
DB_PASSWORD=postgres

# App
APP_NAME=Multi-City GIS Portfolio Analyzer
APP_ENV=development
DEBUG=True
SECRET_KEY=dev-secret-key

# Uploads
MAX_FILE_SIZE_MB=500
ALLOWED_EXTENSIONS=csv,shp,shx,dbf,prj,cpg,xml,xlsx,xls
UPLOAD_DIR=data/uploads/temp

# Maps
DEFAULT_ZOOM=11
DEFAULT_MAP_TILES=cartodbpositron

# Performance
CACHE_TTL=3600
MAX_PARCELS_WARNING=50000
GEOMETRY_SIMPLIFY_TOLERANCE=0.0001

# Security
ENABLE_DATA_UPLOAD=True
ENABLE_DATA_DELETE=True
REQUIRE_AUTH=False
```

### Streamlit Config (.streamlit/config.toml)

```toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#0a0a1e"
secondaryBackgroundColor = "#1a1a2e"
textColor = "#e4e4e7"

[server]
maxUploadSize = 500
enableCORS = false

[browser]
gatherUsageStats = false
```

---

## Quick Reference Card

### File Locations

| Task | File |
|------|------|
| Add column variation | `data_processing/normalizer.py:42` |
| Modify owner cleaning | `data_processing/normalizer.py:62` |
| Change map colors | `mapping/styles.py:20` |
| Update database models | `database/models.py` |
| Configure app | `app/config.py` |
| Add UI page | `app/pages/N_Name.py` |

### Key Commands

```bash
# Start app
streamlit run app/main.py

# Run tests
pytest tests/ -v

# Start database
docker-compose up -d postgres

# Stop database
docker-compose down

# Database shell
docker exec -it multi_city_gis_db psql -U postgres -d multi_city_gis

# Check database
python tests/setup_verification.py
```

### Common Queries

```python
# Get all cities
with db_manager.get_session() as session:
    cities = session.query(City).all()

# Get parcels for a city
parcels = session.query(Parcel).filter(
    Parcel.city_id == 1
).all()

# Get target owners
targets = session.query(TargetOwner).filter(
    TargetOwner.city_id == 1,
    TargetOwner.is_active == True
).all()

# Count parcels by owner
from sqlalchemy import func
owner_counts = session.query(
    Parcel.owner_clean,
    func.count(Parcel.parcel_id)
).group_by(Parcel.owner_clean).all()
```

---

## Getting Help

### Documentation

| Resource | Location | Purpose |
|----------|----------|---------|
| Project Overview | `Documents/README.md` | High-level project info |
| Implementation Plan | `Documents/IMPLEMENTATION_ROADMAP.md` | Phase-by-phase plan |
| Setup Guide | `Documents/SETUP_INSTRUCTIONS.md` | Development environment |
| Current Phase | `Documents/PHASE5_TODO_CHECKLIST.md` | Task breakdown |
| This Guide | `CLAUDE.md` | AI assistant reference |

### Original Reference

The original v1.0 script is preserved in project root:
- `ClevelandMap.py` - Original working implementation
- `ClevelandOwners.py` - Ownership analysis
- `DetroitOwners.py` - Detroit preparation

**Use these for reference when:**
- Unclear how a feature should work
- Need to verify calculations
- Understanding business logic
- Comparing output

### Debugging Tips

**Database Issues:**
```bash
# Check connection
python tests/setup_verification.py

# Check tables
docker exec -it multi_city_gis_db psql -U postgres -d multi_city_gis -c "\dt"

# Check PostGIS
docker exec -it multi_city_gis_db psql -U postgres -d multi_city_gis -c "SELECT PostGIS_version();"
```

**Streamlit Issues:**
```bash
# Clear cache
streamlit cache clear

# Run in debug mode
streamlit run app/main.py --logger.level=debug

# Check browser console for JavaScript errors
```

**Import Issues:**
```python
import sys
print(sys.path)  # Verify project root is in path
```

---

## Contributing Guidelines

### Before Making Changes

1. **Read relevant documentation** in `Documents/`
2. **Check current phase status** in roadmap
3. **Run existing tests** to ensure nothing is broken
4. **Review similar code** for patterns

### Making Changes

1. **Create focused commits** - one logical change per commit
2. **Write descriptive commit messages** - explain why, not what
3. **Update tests** if modifying tested code
4. **Run tests** before committing
5. **Update documentation** if changing interfaces

### Testing Changes

1. **Unit tests:** Run affected test files
2. **Integration:** Test UI pages if applicable
3. **Database:** Verify schema changes don't break queries
4. **Visual:** Check Streamlit UI renders correctly

### Code Review Checklist

- [ ] Code follows project conventions
- [ ] All tests pass
- [ ] No hardcoded values (use config)
- [ ] Database sessions properly managed
- [ ] Errors handled gracefully
- [ ] Documentation updated
- [ ] No debug print statements
- [ ] Type hints added
- [ ] Docstrings updated

---

## Appendix: Technology Deep Dives

### PostGIS Spatial Operations

**Common Operations:**
```sql
-- Find parcels within a polygon
SELECT * FROM parcels
WHERE ST_Within(geometry, ST_GeomFromText('POLYGON(...)'));

-- Calculate parcel area
SELECT parcel_pin, ST_Area(geometry::geography) / 4047 as acres
FROM parcels;

-- Find nearby parcels
SELECT * FROM parcels
WHERE ST_DWithin(
    geometry::geography,
    ST_GeomFromText('POINT(-81.7 41.5)', 4326)::geography,
    1000  -- 1000 meters
);
```

### Folium Map Customization

**Adding Custom JavaScript:**
```python
from folium import Element

js_code = """
<script>
// Custom functionality
</script>
"""
map_obj.get_root().html.add_child(Element(js_code))
```

**Custom Tile Layers:**
```python
folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    attr='OpenStreetMap',
    name='Custom Layer',
    overlay=False,
    control=True
).add_to(map_obj)
```

### Streamlit Advanced Patterns

**Session State Management:**
```python
# Initialize with defaults
if 'wizard_step' not in st.session_state:
    st.session_state.wizard_step = 1
    st.session_state.uploaded_files = {}

# Update state
st.session_state.wizard_step += 1

# Reset state
for key in list(st.session_state.keys()):
    del st.session_state[key]
```

**Custom Components:**
```python
import streamlit.components.v1 as components

html_content = """
<div class="custom-component">
    <!-- HTML here -->
</div>
"""
components.html(html_content, height=400)
```

---

## Conclusion

This guide provides comprehensive context for AI assistants working on the Green Sea Map / Multi-City GIS Portfolio Analyzer project.

**Key Takeaways:**

1. **This is a real estate investment analysis tool** being migrated from script to web app
2. **Phase 5 (UI) is 72% complete**, Phase 6-10 are upcoming
3. **All data processing and mapping modules are tested and working**
4. **Follow the established patterns** for database, Streamlit, and testing
5. **Consult the roadmap** for phase-specific guidance
6. **Test thoroughly** - we have 66 tests for a reason

**When in doubt:**
- Check `Documents/IMPLEMENTATION_ROADMAP.md` for detailed implementation steps
- Review original `ClevelandMap.py` for business logic reference
- Run `python tests/setup_verification.py` to verify environment
- Follow established code patterns in existing modules

**Happy coding!** 🚀

---

**Document Metadata:**
- **Version:** 1.0
- **Created:** 2025-11-14
- **Author:** Claude (AI Assistant)
- **Purpose:** Comprehensive codebase guide for AI assistants
- **Maintenance:** Update when major changes occur to project structure or conventions
