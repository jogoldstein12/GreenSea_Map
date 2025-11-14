"""
Multi-City GIS Portfolio Analyzer
Main Streamlit Application Entry Point
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config import config
from database.db_manager import db_manager


# ====================================
# Page Configuration
# ====================================
st.set_page_config(
    page_title=config.APP_NAME,
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': None,
        'Report a bug': None,
        'About': f"# {config.APP_NAME}\nVersion {config.APP_VERSION}\n\nReal estate portfolio analysis across multiple cities."
    }
)


# ====================================
# CSS Loading
# ====================================
def load_css():
    """Load custom CSS for glassmorphism theme"""
    css_file = project_root / "ui" / "styles" / "glass_theme.css"
    
    if css_file.exists():
        with open(css_file) as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found: {css_file}")


# Load CSS immediately after page config
load_css()


# ====================================
# Session State Initialization
# ====================================
def init_session_state():
    """Initialize session state variables"""
    if 'db_initialized' not in st.session_state:
        st.session_state.db_initialized = False
    
    if 'selected_city' not in st.session_state:
        st.session_state.selected_city = None
    
    if 'user_authenticated' not in st.session_state:
        st.session_state.user_authenticated = not config.REQUIRE_AUTH


# ====================================
# Database Initialization
# ====================================
def init_database():
    """Initialize database connection"""
    if not st.session_state.db_initialized:
        try:
            with st.spinner("Connecting to database..."):
                db_manager.initialize()
                
                # Test connection
                if db_manager.test_connection():
                    st.session_state.db_initialized = True
                    
                    # Check PostGIS
                    postgis_version = db_manager.get_postgis_version()
                    if postgis_version:
                        if config.DEBUG:
                            st.success(f"✅ Database connected (PostGIS {postgis_version})")
                    else:
                        st.warning("⚠️ PostGIS extension not detected. Spatial queries may not work.")
                else:
                    st.error("❌ Database connection failed. Please check your configuration.")
                    st.stop()
        except Exception as e:
            st.error(f"❌ Database initialization error: {str(e)}")
            if config.DEBUG:
                st.exception(e)
            st.stop()


# ====================================
# Main Application
# ====================================
def main():
    """Main application entry point - redirects to Home page"""
    
    # Initialize session state
    init_session_state()
    
    # Initialize database
    init_database()
    
    # Redirect to Home page
    st.switch_page("pages/1_Home.py")


if __name__ == "__main__":
    main()

