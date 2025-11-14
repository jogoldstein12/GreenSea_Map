# Multi-City GIS Portfolio Analyzer

## 🏘️ Project Overview

A web-based geospatial analysis tool for real estate portfolio analysis across multiple cities. Originally built as a Python script for Cleveland, OH, this application has been redesigned as a scalable Streamlit webapp capable of handling multiple cities with dynamic data upload and interactive mapping capabilities.

### **Purpose**
Analyze and visualize real estate portfolios for target property owners across different cities, providing interactive maps, statistical breakdowns, and portfolio comparisons to support investment decision-making.

---

## 📊 Current Status

**🔴 Migration Phase**: Converting from standalone script to web application

### Original Application (v1.0)
- ✅ Single Python script (`ClevelandMap.py`)
- ✅ Generates static HTML maps with Folium
- ✅ Hardcoded paths for Cleveland data only
- ✅ Requires manual execution per city
- ✅ Excel-based target owner lists
- ✅ Rich interactive features (owner filtering, ZIP analysis)

### Target Application (v2.0)
- 🔄 Multi-page Streamlit web application
- 🔄 PostgreSQL + PostGIS database backend
- 🔄 Dynamic data upload interface
- 🔄 Support for unlimited cities
- 🔄 Web-deployable (Streamlit Cloud/Heroku)
- 🔄 City-agnostic map generation

**📅 Implementation Timeline:** 14-19 days (see `IMPLEMENTATION_ROADMAP.md`)

---

## 🎯 Key Features

### Current Features (from v1.0)
- **Interactive Maps**: Folium-based maps with layer toggling
- **Portfolio Analysis**: Statistics per owner (property count, total sales, assessments)
- **ZIP Code Breakdown**: Geographic distribution analysis
- **Owner Search**: Real-time search and filtering
- **Multiple Views**: By portfolio owner or by ZIP code
- **Property Filtering**: Filter by land use types (1-family, 2-family lots)
- **Custom Popups**: Detailed property information on click
- **Target Owner Lists**: Excel-based investor tracking

### Planned Features (v2.0)
- **Multi-City Support**: Add/manage multiple cities from UI
- **Data Upload Interface**: Drag-and-drop CSV, Shapefiles, Excel
- **Database Backend**: PostgreSQL for scalable data storage
- **Dynamic Configuration**: Per-city settings without code changes
- **Export Options**: PDF reports, Excel exports, map downloads
- **City Comparison**: Compare portfolios across cities
- **User Authentication**: Role-based access control (optional)
- **API Endpoints**: REST API for data access (future)

---

## 🗂️ Project Structure

### Current Structure (v1.0)
```
ClevelandGIS/
├── ClevelandMap.py                 # Main script (633 lines)
├── ClevelandOwners.py              # Ownership analysis (separate)
├── DetroitOwners.py                # Detroit analysis prep
├── Input Data/
│   ├── Combined_Parcels_-_Cleveland_Only.csv
│   ├── ClevelandSHP/               # Shapefiles
│   └── Detroit_GIS_Data.csv
├── Output Files/
│   ├── cleveland_ownership_analysis.xlsx
│   └── cleveland_top5_map.html     # Generated map
├── IMPLEMENTATION_ROADMAP.md       # Migration plan
└── README.md                       # This file
```

### Target Structure (v2.0)
```
multi_city_gis/
├── app/
│   ├── main.py                     # Streamlit entry point
│   └── config.py                   # App configuration
├── database/
│   ├── db_manager.py               # Database operations
│   ├── models.py                   # SQLAlchemy models
│   └── schema.sql                  # Database schema
├── data_processing/
│   ├── csv_processor.py            # CSV ingestion
│   ├── shapefile_processor.py      # Shapefile handling
│   ├── excel_processor.py          # Excel target lists
│   ├── normalizer.py               # Column normalization
│   └── analyzer.py                 # Statistics calculations
├── mapping/
│   ├── map_generator.py            # Folium map creation
│   ├── layer_builder.py            # Layer generation
│   └── styles.py                   # Map styling
├── ui/
│   ├── pages/
│   │   ├── 1_🏠_Home.py            # City dashboard
│   │   ├── 2_🗺️_Map_Viewer.py      # Interactive map
│   │   ├── 3_📤_Upload_Data.py     # Data management
│   │   └── 4_⚙️_Settings.py        # Configuration
│   └── components/
│       ├── sidebar.py              # Reusable UI components
│       ├── stats_panel.py
│       └── filters.py
├── utils/
│   ├── validators.py               # Data validation
│   ├── helpers.py                  # Utility functions
│   └── cache.py                    # Caching layer
├── data/                           # Local data storage (gitignored)
├── tests/                          # Unit tests
├── .env                            # Environment variables (gitignored)
├── .env.example                    # Environment template
├── requirements.txt                # Python dependencies
├── README.md                       # This file
└── IMPLEMENTATION_ROADMAP.md       # Detailed implementation plan
```

---

## 🛠️ Technology Stack

### Core Technologies
- **Python 3.9+**: Primary programming language
- **Streamlit 1.29+**: Web application framework
- **PostgreSQL 14+**: Relational database
- **PostGIS**: Spatial database extension

### Geospatial Libraries
- **GeoPandas**: Spatial data manipulation
- **Folium**: Interactive map generation
- **Shapely**: Geometric operations
- **Fiona**: Shapefile I/O
- **PyProj**: Coordinate reference system transformations

### Data Processing
- **Pandas**: Tabular data manipulation
- **SQLAlchemy**: Database ORM
- **OpenPyXL**: Excel file handling

### Deployment
- **Streamlit Cloud**: Recommended hosting (free tier available)
- **Heroku**: Alternative hosting
- **Docker**: Containerization for self-hosting

---

## 📚 Data Architecture

### Input Data Requirements

#### 1. **Parcel Data (CSV)**
Required columns (after normalization):
- `parcelpin` - Unique parcel identifier
- `deeded_owner` - Property owner name
- `tax_luc_description` - Land use classification
- `par_addr` / `par_addr_all` - Property address
- `par_zip` - ZIP code
- `sales_amount` / `sales_amou` - Last sale price
- `certified_tax_total` - Tax assessment value

#### 2. **Spatial Data (Shapefile)**
Required files in shapefile bundle:
- `.shp` - Geometry data
- `.shx` - Shape index
- `.dbf` - Attribute data
- `.prj` - Projection/CRS information
- `.cpg` - Character encoding (optional)
- `.xml` - Metadata (optional)

**Important**: Shapefile must contain same `parcelpin` for merging with CSV.

#### 3. **Target Owners (Excel)**
Format:
- One or more sheets (e.g., "Portfolio Targets (10-100)")
- Owner name column (various names supported: `owner_clean`, `owner`, `deeded_owner`)
- Optional: category, notes columns

### Database Schema (v2.0)

#### **cities** table
Stores city configurations and metadata.
```sql
city_id, city_name, display_name, state, center_lat, center_lng, zoom_level, is_active
```

#### **parcels** table
Main geospatial data with property information.
```sql
parcel_id, city_id, parcel_pin, geometry (PostGIS), address, par_zip,
deeded_owner, owner_clean, tax_luc_description, sales_amount, certified_tax_total
```

#### **target_owners** table
Lists of property owners to analyze.
```sql
target_id, city_id, owner_clean, category, notes, is_active
```

#### **city_configs** table
Per-city configuration (property types, column mappings).
```sql
config_id, city_id, valid_property_types (JSON), column_mappings (JSON)
```

#### **import_history** table
Audit trail of data uploads.
```sql
import_id, city_id, import_type, file_name, records_imported, status, error_log
```

---

## 🔧 Configuration

### Environment Variables (.env)

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=5432
DB_NAME=multi_city_gis
DB_USER=postgres
DB_PASSWORD=your_secure_password

# Application Settings
APP_ENV=development
DEBUG=True
SECRET_KEY=your-secret-key-here

# Upload Limits
MAX_FILE_SIZE_MB=500
ALLOWED_EXTENSIONS=csv,shp,shx,dbf,prj,cpg,xml,xlsx,xls
```

### City Configuration (v2.0)

Each city can have custom configuration stored in `city_configs` table:

```json
{
  "valid_property_types": [
    "1-FAMILY PLATTED LOT",
    "2-FAMILY PLATTED LOT"
  ],
  "column_mappings": {
    "owner": "deeded_owner",
    "luc": "tax_luc_description",
    "address": "par_addr"
  },
  "filter_rules": {
    "exclude_government": true,
    "exclude_non_profit": true
  }
}
```

---

## 🚀 Usage Guide

### Current Usage (v1.0 - Script)

1. **Prepare Data Files**:
   - Place CSV, shapefile, and Excel in designated folders
   - Update paths in `ClevelandMap.py` lines 12-15

2. **Configure Settings**:
   - Set valid property types (line 17)
   - Set target Excel sheet name (line 18)

3. **Run Script**:
   ```bash
   python ClevelandMap.py
   ```

4. **View Output**:
   - Open `Output Files/cleveland_top5_map.html` in browser

### Future Usage (v2.0 - Web App)

1. **Access Application**: Navigate to deployed URL

2. **View Cities**: Home page shows all available cities

3. **Explore Map**:
   - Select city from Map Viewer page
   - Use search to find specific owners
   - Toggle between owner and ZIP views
   - Click parcels for detailed info

4. **Upload New City**:
   - Go to Upload Data page
   - Enter city information
   - Upload CSV, shapefile (as .zip), and Excel
   - Map columns to standard fields
   - Import and view

5. **Export Data**:
   - Download map as HTML
   - Export statistics to Excel
   - Generate PDF reports (planned)

---

## 🔑 Key Concepts

### Owner Normalization
Owner names are cleaned and standardized:
- Convert to uppercase
- Remove punctuation (periods, commas)
- Remove legal suffixes (LLC, INC, CO)
- Trim whitespace

Example: `Smith Properties, LLC.` → `SMITH PROPERTIES`

This ensures consistent matching across datasets.

### Property Type Filtering
Analysis focuses on residential investment properties:
- `1-FAMILY PLATTED LOT` - Single-family homes
- `2-FAMILY PLATTED LOT` - Duplexes

Other property types (commercial, vacant land, etc.) are excluded unless configured otherwise.

### Target Owners
Investors identified for analysis, typically:
- Portfolio size: 10-100 properties
- Active in target market
- Investment-focused (not occupant-owners)

### Portfolio Statistics
Key metrics calculated per owner:
- **Property Count**: Number of parcels owned
- **Total Sales**: Sum of last sale prices
- **Total Assessed**: Sum of tax assessments
- **Average Sales**: Mean sale price per property
- **Average Assessed**: Mean assessment per property
- **ZIP Breakdown**: Distribution across ZIP codes

---

## 🎨 Map Features

### Layer Types

1. **Base Context Layer** (Grey)
   - Shows all target owner properties
   - Low opacity for context
   - Always visible in "All Owners" view

2. **Owner Layers** (Colored)
   - Each owner gets unique color
   - Toggleable via dropdown
   - Can view individually or all at once

3. **ZIP Layers** (Mixed Colors)
   - Groups properties by ZIP code
   - Maintains owner colors within ZIP
   - Alternative view mode

### Interactive Elements

- **Tooltips**: Hover to see basic info (address, owner)
- **Popups**: Click for detailed property info (sale price, assessment, PIN)
- **Layer Control**: Toggle layers on/off via Folium control
- **Search**: Real-time owner name search with autocomplete
- **Filters**: Switch between Owner and ZIP views

### Map Controls
- Pan: Click and drag
- Zoom: Mouse wheel or +/- buttons
- Reset: Double-click to recenter
- Fullscreen: Available in layer control

---

## 📊 Statistical Analysis

### Owner-Level Stats
For each target owner, calculate:
- Property count by city
- Geographic distribution (ZIP codes)
- Financial totals (sales, assessments)
- Average property values
- Portfolio concentration metrics

### ZIP-Level Stats
For each ZIP code, show:
- Total properties in portfolio
- Which owners are active
- Total sales volume
- Assessment values
- Comparative metrics

### City-Level Stats
Aggregate across all target owners:
- Total properties under analysis
- Market coverage percentage
- Top ZIP codes
- Portfolio diversity metrics

---

## 🔍 Data Processing Pipeline

### Current Pipeline (v1.0)
1. **Load CSV**: Read parcel attributes
2. **Load Shapefile**: Read geometries
3. **Normalize**: Standardize column names
4. **Filter**: Keep only valid property types
5. **Clean**: Normalize owner names
6. **Load Targets**: Read Excel owner list
7. **Merge**: Join CSV + Shapefile on parcelpin
8. **Filter**: Keep only target owner parcels
9. **Calculate**: Compute statistics
10. **Generate**: Build Folium map with layers
11. **Export**: Save HTML file

### Future Pipeline (v2.0)
1. **Upload**: Web interface accepts files
2. **Validate**: Check file formats and required columns
3. **Transform**: Normalize columns, clean data
4. **Load**: Insert into PostgreSQL database
5. **Index**: Create spatial indexes
6. **Cache**: Store computed statistics
7. **Query**: Fetch data for selected city
8. **Generate**: Create map dynamically
9. **Display**: Render in Streamlit
10. **Export**: Download on demand

---

## 🧪 Testing Strategy

### Data Validation
- ✅ Required columns present
- ✅ Parcelpin uniqueness
- ✅ Geometry validity
- ✅ CRS compatibility (must be convertible to WGS84)
- ✅ Numeric fields are actually numeric

### Functional Testing
- ✅ Map renders correctly
- ✅ All owners appear in dropdown
- ✅ Layer toggling works
- ✅ Statistics match expected values
- ✅ Search returns correct results
- ✅ Export functions work

### Performance Testing
- ✅ Load time for 10k parcels < 5 seconds
- ✅ Map generation < 10 seconds
- ✅ Database queries < 1 second
- ✅ UI remains responsive during operations

---

## 🚨 Common Issues & Solutions

### Issue: Column Not Found
**Problem**: Required column missing after merge  
**Cause**: Column names don't match between CSV and shapefile  
**Solution**: Check `normalize_columns()` function, add mapping for your column names

### Issue: Geometry Invalid
**Problem**: Some parcels don't render on map  
**Cause**: Invalid geometries in shapefile  
**Solution**: Use `gdf.geometry.is_valid` to identify, then `gdf.geometry.buffer(0)` to fix

### Issue: Slow Map Rendering
**Problem**: Map takes >30 seconds to load  
**Cause**: Too many parcels (>50k) or complex geometries  
**Solutions**:
- Simplify geometries: `gdf.geometry.simplify(tolerance=0.0001)`
- Use clustering for dense areas
- Implement lazy loading of layers
- Consider vector tiles for very large datasets

### Issue: Owner Names Don't Match
**Problem**: Same owner appears multiple times with different names  
**Cause**: Inconsistent naming in source data  
**Solution**: Enhance `clean_owner()` function with more normalization rules or create manual mapping table

### Issue: Memory Error During Import
**Problem**: Script crashes on large CSV files  
**Cause**: Loading entire file into memory  
**Solution**: Use chunked reading: `pd.read_csv(file, chunksize=10000)`

---

## 📈 Performance Optimization

### Database Level
- Create indexes on frequently queried columns (owner_clean, par_zip, city_id)
- Use spatial indexes (GIST) for geometry columns
- Implement connection pooling
- Cache statistics in `stats_cache` table

### Application Level
- Use Streamlit caching (`@st.cache_data`, `@st.cache_resource`)
- Lazy load map layers (only generate when selected)
- Paginate large result sets
- Compress geometries for network transfer

### Map Optimization
- Simplify geometries at lower zoom levels
- Use marker clustering for point data
- Limit popup fields to essential info only
- Precompute layer bounds for quick zoom

---

## 🔐 Security Considerations

### Data Privacy
- Owner information is public record (from county auditor)
- No personal information (SSN, bank accounts, etc.)
- Sales data is public information
- Consider access controls if adding proprietary analysis

### Application Security
- Validate all file uploads (type, size, content)
- Sanitize user inputs to prevent SQL injection
- Use parameterized queries (SQLAlchemy ORM)
- Don't expose database credentials in code
- Use environment variables for secrets

### Deployment Security
- Use HTTPS (handled by Streamlit Cloud/Heroku)
- Set secure session cookies
- Implement rate limiting if public-facing
- Regular security updates for dependencies

---

## 📦 Deployment Options

### Option 1: Streamlit Cloud (Recommended)
**Pros:**
- Free tier available
- Automatic HTTPS
- GitHub integration
- Zero DevOps overhead

**Cons:**
- 1GB RAM limit (free tier)
- Need external database
- Limited customization

**Best For:** Internal tools, proof-of-concept, small teams

### Option 2: Heroku
**Pros:**
- Easy setup
- PostgreSQL add-on included
- Scalable
- Good documentation

**Cons:**
- Paid plans ($7-25/month)
- Sleeping on free tier
- Platform-specific config

**Best For:** Production apps, external users, need reliability

### Option 3: Self-Hosted (Docker)
**Pros:**
- Full control
- No vendor lock-in
- Can run on-premises
- Cheapest for high usage

**Cons:**
- Requires DevOps knowledge
- You manage updates/backups
- Setup complexity

**Best For:** Enterprise deployments, specific compliance needs

---

## 🤖 LLM Assistant Context

**For AI Assistants working on this project:**

### Project Intent
This is a real estate portfolio analysis tool being migrated from a standalone Python script to a multi-city web application. The original script (`ClevelandMap.py`) works well but isn't scalable. We're building v2.0 with Streamlit + PostgreSQL.

### Key Constraints
- Must preserve all existing functionality from v1.0
- Must support multiple cities without code changes
- Data upload should be user-friendly (no coding required)
- Performance target: <5 seconds for 50k parcels
- Must work on Streamlit Cloud free tier (with external DB)

### Code Style Preferences
- Type hints for function parameters
- Docstrings for all public functions
- Error handling with user-friendly messages
- Logging for debugging (not print statements)
- Separate concerns (processing, mapping, UI)

### Critical Functions to Preserve
From `ClevelandMap.py`:
- `normalize_columns()` - Lines 23-35
- `clean_owner()` - Lines 38-50
- `owner_stats()` - Lines 172-205
- Map generation logic - Lines 247-443
- Sidebar HTML generation - Lines 544-626

### Testing Expectations
- Test with Cleveland data (known good dataset)
- Verify statistics match original output
- Check map layers render identically
- Validate with Detroit data (second city)

### Database Design Philosophy
- Normalize data (3NF) but denormalize for performance where needed
- Use JSONB for flexible configs (valid_property_types, column_mappings)
- Spatial indexes are critical for performance
- Track imports for auditing and rollback

### Migration Strategy
Follow `IMPLEMENTATION_ROADMAP.md` phases sequentially. Each phase has checkpoints - don't proceed until checkpoints pass. Cleveland data migration is in Phase 9, after core functionality is built.

### When Stuck
1. Check `IMPLEMENTATION_ROADMAP.md` for detailed steps
2. Review original `ClevelandMap.py` for reference implementation
3. Test with small dataset first (filter to single ZIP code)
4. Use SQL EXPLAIN ANALYZE for slow queries
5. Check Streamlit docs for component usage

---

## 📞 Support & Resources

### Documentation
- **Implementation Roadmap**: `IMPLEMENTATION_ROADMAP.md` - Step-by-step guide
- **This README**: Project overview and reference
- **Original Script**: `ClevelandMap.py` - Working reference implementation

### External Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [GeoPandas User Guide](https://geopandas.org/)
- [Folium Documentation](https://python-visualization.github.io/folium/)
- [PostGIS Documentation](https://postgis.net/documentation/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)

### Data Sources
- Cleveland Parcels: Cuyahoga County Auditor
- Detroit Parcels: City of Detroit Open Data Portal
- Property data is public record (county auditor websites)

---

## 🗺️ Roadmap

### ✅ Completed
- [x] Original Cleveland script (v1.0)
- [x] Implementation roadmap created
- [x] Architecture designed
- [x] Database schema defined

### 🔄 In Progress
- [ ] Phase 1: Project setup
- [ ] Phase 2: Database implementation
- [ ] Phase 3: Data processing migration

### 📅 Planned (v2.0 - MVP)
- [ ] Multi-city support
- [ ] Web-based data upload
- [ ] Streamlit UI
- [ ] Deployment to Streamlit Cloud
- [ ] Cleveland + Detroit data migrated

### 🔮 Future Enhancements (v2.1+)
- [ ] PDF report generation
- [ ] City comparison dashboard
- [ ] Historical data tracking
- [ ] User authentication
- [ ] REST API for data access
- [ ] Mobile-responsive design improvements
- [ ] Email notifications for data updates
- [ ] CRM integration (Salesforce, HubSpot)
- [ ] Predictive analytics (ownership trends)

---

## 📄 License & Usage

**Internal Tool**: This application is designed for internal real estate investment analysis.

**Data Sources**: All parcel and ownership data is sourced from public records (county auditor websites). Users are responsible for complying with terms of use from data providers.

**No Warranty**: This tool is provided as-is for analysis purposes. Always verify critical information against original sources before making investment decisions.

---

## 🤝 Contributing

Since this is currently a single-developer project in migration phase, contribution guidelines will be established once v2.0 is stable.

**Migration Help Appreciated:**
- Testing with data from additional cities
- Performance optimization suggestions
- Bug reports and fixes
- Documentation improvements

---

## 📝 Version History

### v1.0 (Current)
- Single-city Python script
- Static HTML output
- Cleveland data only
- Manual execution required

### v2.0 (In Development)
- Multi-city Streamlit web app
- PostgreSQL database backend
- Dynamic data upload
- Web-deployable
- **Target Release:** ~3 weeks from project start

---

## 📧 Contact

**Project Owner**: Joe (jogol)  
**Project Path**: `C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\`  
**Development Start**: November 2025

---

**Last Updated**: 2025-11-12  
**Document Version**: 1.0  
**Status**: 🔴 Migration Phase

