"""
Setup Verification Script
Checks if all required components are properly installed and configured
"""

import sys
import os
from pathlib import Path

# Colors for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_error(text):
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_info(text):
    print(f"  {text}")


def check_python_version():
    """Check Python version"""
    print_header("Checking Python Version")
    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"
    
    if version.major >= 3 and version.minor >= 9:
        print_success(f"Python {version_str} (✓ Requirement: 3.9+)")
        return True
    else:
        print_error(f"Python {version_str} (✗ Requirement: 3.9+)")
        return False


def check_packages():
    """Check required Python packages"""
    print_header("Checking Python Packages")
    
    required_packages = [
        ('streamlit', '1.29.0'),
        ('pandas', '2.0.0'),
        ('geopandas', '0.14.0'),
        ('sqlalchemy', '2.0.0'),
        ('folium', '0.15.0'),
        ('psycopg2', '2.9.0'),
    ]
    
    all_ok = True
    for package_name, min_version in required_packages:
        try:
            if package_name == 'psycopg2':
                import psycopg2
                version = psycopg2.__version__
            else:
                module = __import__(package_name)
                version = getattr(module, '__version__', 'unknown')
            
            print_success(f"{package_name} {version}")
        except ImportError:
            print_error(f"{package_name} NOT INSTALLED")
            all_ok = False
    
    return all_ok


def check_directory_structure():
    """Check if project directory structure exists"""
    print_header("Checking Directory Structure")
    
    required_dirs = [
        'app',
        'database',
        'data_processing',
        'mapping',
        'ui',
        'ui/components',
        'utils',
        'tests',
        'data/uploads/temp',
        '.streamlit'
    ]
    
    all_ok = True
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"{dir_path}/")
        else:
            print_error(f"{dir_path}/ MISSING")
            all_ok = False
    
    return all_ok


def check_config_files():
    """Check if configuration files exist"""
    print_header("Checking Configuration Files")
    
    required_files = [
        'requirements.txt',
        '.streamlit/config.toml',
        '.gitignore',
        'README.md',
        'IMPLEMENTATION_ROADMAP.md',
    ]
    
    optional_files = [
        '.env',
        'docker-compose.yml'
    ]
    
    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print_success(f"{file_path}")
        else:
            print_error(f"{file_path} MISSING")
            all_ok = False
    
    for file_path in optional_files:
        if Path(file_path).exists():
            print_success(f"{file_path} (optional)")
        else:
            print_warning(f"{file_path} NOT FOUND (optional)")
    
    return all_ok


def check_database_connection():
    """Check database connection"""
    print_header("Checking Database Connection")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        import psycopg2
        
        # Get connection details from environment
        db_host = os.getenv('DB_HOST', 'localhost')
        db_port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'multi_city_gis')
        db_user = os.getenv('DB_USER', 'postgres')
        db_password = os.getenv('DB_PASSWORD', '')
        
        print_info(f"Attempting connection to: {db_host}:{db_port}/{db_name}")
        
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor()
        
        # Check PostgreSQL version
        cursor.execute("SELECT version();")
        pg_version = cursor.fetchone()[0]
        print_success(f"PostgreSQL: {pg_version.split(',')[0]}")
        
        # Check PostGIS
        try:
            cursor.execute("SELECT PostGIS_version();")
            postgis_version = cursor.fetchone()[0]
            print_success(f"PostGIS: {postgis_version}")
        except:
            print_warning("PostGIS extension not found or not enabled")
        
        cursor.close()
        conn.close()
        
        return True
        
    except Exception as e:
        print_error(f"Database connection failed: {str(e)}")
        print_info("\nTo set up PostgreSQL with Docker:")
        print_info("  docker-compose up -d postgres")
        print_info("\nOr install PostgreSQL + PostGIS locally")
        return False


def check_environment_variables():
    """Check environment variables"""
    print_header("Checking Environment Variables")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    required_vars = [
        'DB_HOST',
        'DB_PORT',
        'DB_NAME',
        'DB_USER',
    ]
    
    optional_vars = [
        'DB_PASSWORD',
        'SECRET_KEY',
        'MAX_FILE_SIZE_MB',
    ]
    
    all_ok = True
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password if present
            display_value = '***' if 'PASSWORD' in var or 'KEY' in var else value
            print_success(f"{var}={display_value}")
        else:
            print_error(f"{var} NOT SET")
            all_ok = False
    
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            display_value = '***' if 'PASSWORD' in var or 'KEY' in var else value
            print_success(f"{var}={display_value} (optional)")
        else:
            print_warning(f"{var} NOT SET (optional)")
    
    if not all_ok:
        print_info("\nCreate a .env file based on .env.example")
    
    return all_ok


def main():
    """Run all verification checks"""
    print(f"\n{Colors.BOLD}Multi-City GIS Portfolio Analyzer{Colors.END}")
    print(f"{Colors.BOLD}Setup Verification Script{Colors.END}\n")
    
    checks = [
        ("Python Version", check_python_version),
        ("Python Packages", check_packages),
        ("Directory Structure", check_directory_structure),
        ("Configuration Files", check_config_files),
        ("Environment Variables", check_environment_variables),
        ("Database Connection", check_database_connection),
    ]
    
    results = []
    for check_name, check_func in checks:
        try:
            result = check_func()
            results.append((check_name, result))
        except Exception as e:
            print_error(f"Error during {check_name}: {str(e)}")
            results.append((check_name, False))
    
    # Summary
    print_header("Verification Summary")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for check_name, result in results:
        if result:
            print_success(f"{check_name}")
        else:
            print_error(f"{check_name}")
    
    print(f"\n{Colors.BOLD}Result: {passed}/{total} checks passed{Colors.END}\n")
    
    if passed == total:
        print(f"{Colors.GREEN}{Colors.BOLD}✓ All checks passed! You're ready to start development.{Colors.END}\n")
        print("Next steps:")
        print("  1. Start the database: docker-compose up -d postgres")
        print("  2. Run the application: streamlit run app/main.py")
        return 0
    else:
        print(f"{Colors.RED}{Colors.BOLD}✗ Some checks failed. Please fix the issues above.{Colors.END}\n")
        print("Common fixes:")
        print("  • Install packages: pip install -r requirements.txt")
        print("  • Create .env file: cp .env.example .env")
        print("  • Start database: docker-compose up -d postgres")
        return 1


if __name__ == "__main__":
    sys.exit(main())

