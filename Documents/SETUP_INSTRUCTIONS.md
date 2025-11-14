# Setup Instructions
Multi-City GIS Portfolio Analyzer - Development Environment Setup

## Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.9 or higher** - [Download Python](https://www.python.org/downloads/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **Docker Desktop** (optional, for local PostgreSQL) - [Download Docker](https://www.docker.com/products/docker-desktop/)

## Step-by-Step Setup

### 1. Verify Python Installation

Open PowerShell and check your Python version:

```powershell
python --version
```

Should show Python 3.9 or higher. If not, install Python from the link above.

### 2. Create Virtual Environment

Navigate to the project directory and create a virtual environment:

```powershell
cd C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\activate

# Your prompt should now show (venv) at the beginning
```

### 3. Install Python Dependencies

With the virtual environment activated:

```powershell
# Upgrade pip first
python -m pip install --upgrade pip

# Install all dependencies
pip install -r requirements.txt
```

This may take 5-10 minutes as it installs all geospatial libraries.

**Note:** If you encounter errors installing `geopandas` or `fiona`:
- Windows users may need to install GDAL binaries first
- Download from: https://www.lfd.uci.edu/~gohlke/pythonlibs/
- Or use: `pip install pipwin` then `pipwin install gdal fiona`

### 4. Setup Environment Variables

Create your local `.env` file:

```powershell
# Copy the example file
copy .env.example .env

# Edit .env with your preferred text editor
notepad .env
```

Update the following settings in `.env`:
- `DB_PASSWORD` - Set a secure password for PostgreSQL
- `SECRET_KEY` - Change to a random string for production

For development, the default values in `.env.example` work fine.

### 5. Setup PostgreSQL Database

You have two options:

#### Option A: Using Docker (Recommended for Development)

1. Install Docker Desktop from the link above
2. Start Docker Desktop
3. Run PostgreSQL with PostGIS:

```powershell
# Start database
docker-compose up -d postgres

# Verify it's running
docker-compose ps

# View logs (optional)
docker-compose logs postgres
```

Database will be available at:
- Host: `localhost`
- Port: `5432`
- Database: `multi_city_gis`
- User: `postgres`
- Password: `postgres`

#### Option B: Install PostgreSQL Locally

1. Download PostgreSQL 14+ from: https://www.postgresql.org/download/windows/
2. During installation, note your password
3. Install PostGIS extension:
   - Use StackBuilder (included with PostgreSQL installer)
   - Or download from: https://postgis.net/install/

4. Create database:

```sql
-- Connect to PostgreSQL with psql or pgAdmin
CREATE DATABASE multi_city_gis;

-- Connect to the new database
\c multi_city_gis

-- Enable PostGIS
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;
```

5. Update `.env` with your PostgreSQL credentials

### 6. Verify Setup

Run the verification script:

```powershell
# Make sure virtual environment is activated
python setup_verification.py
```

This will check:
- ✓ Python version
- ✓ Installed packages
- ✓ Directory structure
- ✓ Configuration files
- ✓ Environment variables
- ✓ Database connection

All checks should pass (green ✓). If any fail, follow the error messages to fix them.

### 7. Initialize Database Schema

The database tables will be created automatically when you first run the application, but you can also create them manually:

```powershell
# Using the SQL file directly with psql
psql -U postgres -h localhost -d multi_city_gis -f database/schema.sql

# Or let SQLAlchemy create them when the app starts
```

### 8. Run the Application

Start the Streamlit application:

```powershell
# Make sure you're in the project directory with venv activated
streamlit run app/main.py
```

The application should open in your browser at: `http://localhost:8501`

## Troubleshooting

### Virtual Environment Issues

**Problem:** `.\venv\Scripts\activate` doesn't work
**Solution:** Enable script execution in PowerShell:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### Package Installation Errors

**Problem:** `pip install` fails for geospatial packages
**Solutions:**
1. Try installing GDAL first:
   ```powershell
   pip install pipwin
   pipwin install gdal
   pipwin install fiona
   pip install geopandas
   ```

2. Or use conda instead of pip:
   ```powershell
   conda install -c conda-forge geopandas
   ```

### Database Connection Fails

**Problem:** "Database connection failed"
**Solutions:**

1. **If using Docker:**
   ```powershell
   # Check if container is running
   docker-compose ps
   
   # If not running, start it
   docker-compose up -d postgres
   
   # Check logs for errors
   docker-compose logs postgres
   ```

2. **Check .env settings:**
   - Verify `DB_HOST=localhost`
   - Verify `DB_PORT=5432`
   - Verify `DB_NAME=multi_city_gis`
   - Verify `DB_PASSWORD` matches your PostgreSQL password

3. **Test connection manually:**
   ```powershell
   # Using psql
   psql -U postgres -h localhost -d multi_city_gis
   
   # Or using Python
   python -c "import psycopg2; psycopg2.connect('dbname=multi_city_gis user=postgres host=localhost')"
   ```

### PostGIS Not Found

**Problem:** "PostGIS extension not detected"
**Solution:**
```sql
-- Connect to your database and run:
CREATE EXTENSION postgis;
CREATE EXTENSION postgis_topology;

-- Verify installation:
SELECT PostGIS_version();
```

### Port Already in Use

**Problem:** Port 5432 or 8501 already in use
**Solutions:**

1. **For PostgreSQL (port 5432):**
   - Stop other PostgreSQL instances
   - Or change port in docker-compose.yml and .env

2. **For Streamlit (port 8501):**
   ```powershell
   # Use a different port
   streamlit run app/main.py --server.port 8502
   ```

### Import Errors

**Problem:** `ModuleNotFoundError` when running the app
**Solutions:**

1. Ensure virtual environment is activated:
   ```powershell
   # You should see (venv) in your prompt
   .\venv\Scripts\activate
   ```

2. Reinstall requirements:
   ```powershell
   pip install -r requirements.txt --force-reinstall
   ```

3. Check Python path:
   ```powershell
   python -c "import sys; print(sys.executable)"
   # Should point to your venv folder
   ```

## Optional: pgAdmin Setup

To use pgAdmin for database management:

```powershell
# Start PostgreSQL with pgAdmin
docker-compose --profile with-pgadmin up -d

# Access pgAdmin at http://localhost:5050
# Login: admin@admin.com
# Password: admin
```

Add server in pgAdmin:
- Name: Local GIS DB
- Host: postgres (or localhost if not using Docker)
- Port: 5432
- Database: multi_city_gis
- Username: postgres
- Password: postgres

## Next Steps

Once setup is complete:

1. ✅ **Explore the Application**
   - Navigate through the pages
   - Familiarize yourself with the UI structure

2. ✅ **Review the Roadmap**
   - Read `IMPLEMENTATION_ROADMAP.md`
   - Understand the development phases

3. ✅ **Start Development**
   - Begin with Phase 2: Database Architecture
   - Follow the roadmap step-by-step

4. ✅ **Migrate Cleveland Data**
   - This will be covered in Phase 9
   - Keep existing `ClevelandMap.py` as reference

## Development Workflow

Daily workflow when working on the project:

```powershell
# 1. Navigate to project directory
cd C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS

# 2. Activate virtual environment
.\venv\Scripts\activate

# 3. Start database (if not already running)
docker-compose up -d postgres

# 4. Run the application
streamlit run app/main.py

# 5. When done, deactivate virtual environment
deactivate
```

## Useful Commands

```powershell
# Check what's running
docker-compose ps

# View database logs
docker-compose logs -f postgres

# Stop database
docker-compose down

# Stop database and delete data (⚠️ WARNING: deletes all data!)
docker-compose down -v

# Run verification script
python setup_verification.py

# Install new package
pip install package-name
pip freeze > requirements.txt  # Update requirements

# Run tests (when available)
pytest tests/

# Format code (if using black)
black app/ database/ utils/
```

## Getting Help

If you encounter issues:

1. Check this troubleshooting section
2. Review `README.md` for project documentation
3. Check `IMPLEMENTATION_ROADMAP.md` for phase-specific details
4. Search for error messages online
5. Check Streamlit docs: https://docs.streamlit.io/
6. Check PostGIS docs: https://postgis.net/documentation/

## Success!

If `setup_verification.py` passes all checks and you can access the application at `http://localhost:8501`, you're all set!

Welcome to the Multi-City GIS Portfolio Analyzer development! 🎉

