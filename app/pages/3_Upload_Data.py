"""
Upload Data Page - Market Data Import Wizard
5-step process for adding new markets to the system
"""

import streamlit as st
import sys
from pathlib import Path
import time
import logging
from typing import Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Import database and import manager
from database.db_manager import db_manager
from data_import.import_manager import ImportManager

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="Upload Data",
    page_icon="📤",
    layout="wide"
)

# Load custom CSS
def load_css():
    """Load custom CSS for glassmorphism theme"""
    css_file = project_root / "ui" / "styles" / "glass_theme.css"
    
    if css_file.exists():
        with open(css_file) as f:
            css_content = f.read()
            st.markdown(f"<style>{css_content}</style>", unsafe_allow_html=True)
    else:
        st.warning(f"⚠️ CSS file not found: {css_file}")

load_css()

# Set current page for navigation
st.session_state.current_page = "Upload Data"

# Import and render navigation
try:
    from ui.components.navigation import render_navigation
    render_navigation()
except Exception as e:
    st.error(f"Navigation error: {str(e)}")

# ====================================
# Helper Functions
# ====================================

def validate_uploaded_files(uploaded_files: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate uploaded files before import.
    
    Args:
        uploaded_files: Dictionary of uploaded files
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check all required files are present
    required_files = ['csv', 'shp', 'excel']
    for file_key in required_files:
        if file_key not in uploaded_files or uploaded_files[file_key] is None:
            return False, f"Missing required file: {file_key}"
    
    # Validate file extensions
    csv_file = uploaded_files['csv']
    if not csv_file.name.endswith('.csv'):
        return False, f"CSV file must have .csv extension (got: {csv_file.name})"
    
    shapefile_zip = uploaded_files['shp']
    if not shapefile_zip.name.endswith('.zip'):
        return False, f"Shapefile must be a .zip archive (got: {shapefile_zip.name})"
    
    excel_file = uploaded_files['excel']
    if not (excel_file.name.endswith('.xlsx') or excel_file.name.endswith('.xls')):
        return False, f"Excel file must be .xlsx or .xls (got: {excel_file.name})"
    
    return True, ""

def validate_csv_columns(csv_file) -> tuple[bool, str, list]:
    """
    Validate CSV file and extract column names.
    
    Args:
        csv_file: Uploaded CSV file
        
    Returns:
        Tuple of (is_valid, error_message, column_list)
    """
    try:
        import pandas as pd
        import io
        
        # Read first few rows to get columns
        csv_file.seek(0)  # Reset file pointer
        content = csv_file.read()
        csv_file.seek(0)  # Reset again
        
        df = pd.read_csv(io.BytesIO(content), nrows=5)
        
        if df.empty:
            return False, "CSV file is empty", []
        
        columns = df.columns.tolist()
        
        if len(columns) < 3:
            return False, f"CSV must have at least 3 columns (found {len(columns)})", columns
        
        return True, "", columns
        
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}", []

def validate_shapefile_zip(zip_file) -> tuple[bool, str]:
    """
    Validate shapefile ZIP contains required components.
    
    Args:
        zip_file: Uploaded ZIP file
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        import zipfile
        import io
        
        zip_file.seek(0)  # Reset file pointer
        content = zip_file.read()
        zip_file.seek(0)  # Reset again
        
        with zipfile.ZipFile(io.BytesIO(content)) as z:
            files = z.namelist()
            
            # Check for required shapefile components
            has_shp = any(f.endswith('.shp') for f in files)
            has_shx = any(f.endswith('.shx') for f in files)
            has_dbf = any(f.endswith('.dbf') for f in files)
            
            if not has_shp:
                return False, "Shapefile ZIP must contain a .shp file"
            if not has_shx:
                return False, "Shapefile ZIP must contain a .shx file"
            if not has_dbf:
                return False, "Shapefile ZIP must contain a .dbf file"
            
            # Check for projection file (warning, not error)
            has_prj = any(f.endswith('.prj') for f in files)
            if not has_prj:
                logger.warning("Shapefile ZIP does not contain a .prj file (projection). EPSG:4326 will be assumed.")
            
            return True, ""
        
    except zipfile.BadZipFile:
        return False, "Invalid ZIP file format"
    except Exception as e:
        return False, f"Error reading shapefile ZIP: {str(e)}"

def perform_import(
    city_info: Dict[str, Any],
    uploaded_files: Dict[str, Any],
    column_mappings: Dict[str, str],
    property_types: Dict[str, bool],
    progress_callback=None,
    status_callback=None
) -> tuple[bool, str, Dict[str, int]]:
    """
    Perform the actual data import using ImportManager.
    
    Args:
        city_info: City configuration
        uploaded_files: Uploaded files
        column_mappings: Column mappings
        property_types: Property types
        progress_callback: Optional callback for progress updates
        status_callback: Optional callback for status messages
        
    Returns:
        Tuple of (success, message, counts)
    """
    try:
        # Update status
        if status_callback:
            status_callback("🔍 Validating files...")
        
        # Validate files
        is_valid, error_msg = validate_uploaded_files(uploaded_files)
        if not is_valid:
            return False, error_msg, {}
        
        if progress_callback:
            progress_callback(10)
        
        # Initialize ImportManager
        if status_callback:
            status_callback("🚀 Initializing import manager...")
        
        import_manager = ImportManager()
        
        if progress_callback:
            progress_callback(20)
        
        # Prepare import data
        import_data = {
            'city_name': city_info.get('city_name'),
            'display_name': city_info.get('display_name'),
            'state': city_info.get('state'),
            'center_lat': float(city_info.get('center_lat', 0)),
            'center_lng': float(city_info.get('center_lng', 0)),
            'zoom_level': int(city_info.get('zoom_level', 11)),
            'is_active': True
        }
        
        # Update status
        if status_callback:
            status_callback("📊 Importing city and configuration...")
        
        if progress_callback:
            progress_callback(30)
        
        # Perform import
        success, message, counts = import_manager.import_city_data(
            city_info=import_data,
            uploaded_files=uploaded_files,
            column_mappings=column_mappings,
            property_types=property_types
        )
        
        if not success:
            return False, message, counts
        
        # Update progress through the process
        if status_callback:
            status_callback(f"✅ Successfully imported {counts.get('parcels', 0):,} parcels")
        
        if progress_callback:
            progress_callback(80)
        
        if status_callback:
            status_callback(f"✅ Successfully imported {counts.get('target_owners', 0):,} target investors")
        
        if progress_callback:
            progress_callback(90)
        
        # Final status
        if status_callback:
            status_callback("✨ Finalizing import...")
        
        if progress_callback:
            progress_callback(100)
        
        return True, message, counts
        
    except Exception as e:
        logger.error(f"Import failed: {str(e)}", exc_info=True)
        error_message = f"Import failed: {str(e)}"
        return False, error_message, {}

# ====================================
# Header Section
# ====================================

st.markdown("<h1>Upload Data</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 1.125rem; color: var(--text-muted); margin-bottom: 2rem;'>"
    "Add a new market to your portfolio analyzer"
    "</p>", 
    unsafe_allow_html=True
)

st.info("**Requirements:** Three files needed: CSV (parcel data), Shapefile (geometry), and Excel (target investor list)")

# ====================================
# Step Indicator
# ====================================

# Initialize session state for current step
if 'upload_step' not in st.session_state:
    st.session_state.upload_step = 1

current_step = st.session_state.upload_step

# Step indicator using columns for better compatibility
st.markdown('<div style="margin-bottom: 2rem;">', unsafe_allow_html=True)

step_labels = ["Market Info", "Upload Files", "Map Columns", "Configure", "Import"]
step_cols = st.columns(5)

for i, col in enumerate(step_cols, 1):
    is_active = i == current_step
    is_completed = i < current_step
    
    with col:
        if is_active:
            circle_style = "background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%); color: white; border: 2px solid transparent;"
            label_color = "#60a5fa"
        elif is_completed:
            circle_style = "background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; border: 2px solid transparent;"
            label_color = "#71717a"
        else:
            circle_style = "background: rgba(255, 255, 255, 0.05); color: #71717a; border: 2px solid rgba(255, 255, 255, 0.1);"
            label_color = "#71717a"
        
        st.markdown(f"""
        <div style="text-align: center;">
            <div style="width: 48px; height: 48px; border-radius: 50%; {circle_style} margin: 0 auto 0.75rem; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 1.125rem;">
                {i}
            </div>
            <div style="font-size: 0.8125rem; color: {label_color}; font-weight: 500;">{step_labels[i-1]}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# ====================================
# Step 1: Market Information
# ====================================

if current_step == 1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1.5rem;'>Step 1: Market Information</h3>", unsafe_allow_html=True)
    
    # Get existing values from session state if available
    existing_info = st.session_state.get('city_info', {})
    
    city_name = st.text_input(
        "City Name", 
        placeholder="e.g., Cleveland",
        value=existing_info.get('city_name', ''),
        key="city_name_input"
    )
    
    col1, col2 = st.columns(2)
    with col1:
        display_name = st.text_input(
            "Display Name", 
            placeholder="e.g., Cleveland, OH",
            value=existing_info.get('display_name', ''),
            key="display_name_input"
        )
    with col2:
        state_options = ["Select state...", "Ohio", "Michigan", "Pennsylvania", "New York", "Indiana", "Kentucky", "West Virginia"]
        state_default = state_options[0]
        if 'state' in existing_info and existing_info['state'] in state_options:
            state_default = existing_info['state']
        
        state = st.selectbox(
            "State", 
            state_options,
            index=state_options.index(state_default),
            key="state_input"
        )
    
    st.markdown("<p style='font-size: 0.875rem; color: var(--text-muted); margin-top: 1.5rem; margin-bottom: 0.5rem;'>Map Center Coordinates</p>", unsafe_allow_html=True)
    col3, col4, col5 = st.columns(3)
    with col3:
        center_lat = st.number_input(
            "Center Latitude", 
            value=existing_info.get('center_lat', 41.4993), 
            format="%.4f",
            key="lat_input"
        )
    with col4:
        center_lng = st.number_input(
            "Center Longitude", 
            value=existing_info.get('center_lng', -81.6944), 
            format="%.4f",
            key="lng_input"
        )
    with col5:
        zoom_level = st.number_input(
            "Default Zoom", 
            value=existing_info.get('zoom_level', 11), 
            min_value=8, 
            max_value=16,
            key="zoom_input"
        )
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation buttons
    col_left, col_right = st.columns([1, 2])
    with col_right:
        if st.button("Next: Upload Files →", type="primary", use_container_width=True, key="step1_next"):
            if city_name and display_name and state != "Select state...":
                # Store in session state
                st.session_state.city_info = {
                    'city_name': city_name,
                    'display_name': display_name,
                    'state': state,
                    'center_lat': center_lat,
                    'center_lng': center_lng,
                    'zoom_level': zoom_level
                }
                st.session_state.upload_step = 2
                st.rerun()
            else:
                st.error("⚠️ Please fill in all required fields")

# ====================================
# Step 2: File Upload
# ====================================

elif current_step == 2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1.5rem;'>Step 2: Upload Files</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 0.9375rem; font-weight: 600; color: var(--text-primary); margin-top: 1.5rem; margin-bottom: 0.5rem;'>1. Parcel Data (CSV)</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.8125rem; color: var(--text-muted); margin-bottom: 0.75rem;'>CSV file containing property records with parcel details</p>", unsafe_allow_html=True)
    csv_file = st.file_uploader(
        "Upload CSV", 
        type=['csv'], 
        label_visibility="collapsed", 
        key="csv_uploader"
    )
    
    st.markdown("<p style='font-size: 0.9375rem; font-weight: 600; color: var(--text-primary); margin-top: 1.5rem; margin-bottom: 0.5rem;'>2. Shapefile (ZIP Archive)</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.8125rem; color: var(--text-muted); margin-bottom: 0.75rem;'>Compressed ZIP containing .shp, .shx, .dbf, and .prj files</p>", unsafe_allow_html=True)
    shp_file = st.file_uploader(
        "Upload Shapefile ZIP", 
        type=['zip'], 
        label_visibility="collapsed", 
        key="shp_uploader"
    )
    
    st.markdown("<p style='font-size: 0.9375rem; font-weight: 600; color: var(--text-primary); margin-top: 1.5rem; margin-bottom: 0.5rem;'>3. Target Investors (Excel)</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.8125rem; color: var(--text-muted); margin-bottom: 0.75rem;'>Excel spreadsheet with target investor names</p>", unsafe_allow_html=True)
    excel_file = st.file_uploader(
        "Upload Excel", 
        type=['xlsx', 'xls', 'xlsm'], 
        label_visibility="collapsed", 
        key="excel_uploader"
    )
    
    # Show upload status
    if csv_file or shp_file or excel_file:
        st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
        files_status = []
        if csv_file:
            files_status.append(f"✅ CSV: {csv_file.name} ({csv_file.size / 1024:.1f} KB)")
        if shp_file:
            files_status.append(f"✅ Shapefile: {shp_file.name} ({shp_file.size / 1024:.1f} KB)")
        if excel_file:
            files_status.append(f"✅ Excel: {excel_file.name} ({excel_file.size / 1024:.1f} KB)")
        
        for status in files_status:
            st.markdown(f"<p style='font-size: 0.875rem; color: #10b981; margin: 0.25rem 0;'>{status}</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_left, col_right = st.columns([1, 2])
    with col_left:
        if st.button("← Previous", use_container_width=True, key="step2_prev"):
            st.session_state.upload_step = 1
            st.rerun()
    with col_right:
        if st.button("Next: Map Columns →", type="primary", use_container_width=True, key="step2_next"):
            if csv_file and shp_file and excel_file:
                # Validate files before proceeding
                validation_passed = True
                error_messages = []
                
                # Validate CSV
                csv_valid, csv_error, csv_columns = validate_csv_columns(csv_file)
                if not csv_valid:
                    validation_passed = False
                    error_messages.append(f"CSV validation failed: {csv_error}")
                else:
                    # Store columns for Step 3
                    st.session_state.csv_columns = csv_columns
                
                # Validate shapefile ZIP
                shp_valid, shp_error = validate_shapefile_zip(shp_file)
                if not shp_valid:
                    validation_passed = False
                    error_messages.append(f"Shapefile validation failed: {shp_error}")
                
                if validation_passed:
                    st.session_state.uploaded_files = {
                        'csv': csv_file,
                        'shp': shp_file,
                        'excel': excel_file
                    }
                    st.session_state.upload_step = 3
                    st.rerun()
                else:
                    for error_msg in error_messages:
                        st.error(f"⚠️ {error_msg}")
            else:
                st.error("⚠️ Please upload all three required files")

# ====================================
# Step 3: Column Mapping
# ====================================

elif current_step == 3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1.5rem;'>Step 3: Map Columns</h3>", unsafe_allow_html=True)
    
    st.warning("**Column Mapping:** Match your data columns to standard field names")
    
    # Sample column mapping interface
    st.markdown("<h4 style='font-size: 1rem; margin-top: 1.5rem; margin-bottom: 1rem;'>Standard Field Mappings</h4>", unsafe_allow_html=True)
    
    # Get CSV columns from session state
    csv_columns = st.session_state.get('csv_columns', [])
    
    if not csv_columns:
        st.error("⚠️ No CSV columns found. Please go back to Step 2 and re-upload your files.")
        st.markdown('</div>', unsafe_allow_html=True)
        if st.button("← Back to Step 2", use_container_width=True):
            st.session_state.upload_step = 2
            st.rerun()
    else:
        st.info(f"📊 Found {len(csv_columns)} columns in your CSV file")
        
        # Get existing mappings from session state if available
        existing_mappings = st.session_state.get('column_mappings', {})
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<p style='font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem;'>Standard Field</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);'>Parcel PIN</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);'>Owner Name</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);'>Property Type</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);'>Address</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);'>ZIP Code</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08);'>Sales Amount</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0;'>Tax Total</p>", unsafe_allow_html=True)
        
        with col2:
            st.markdown("<p style='font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem;'>Your Column</p>", unsafe_allow_html=True)
            
            # Use actual CSV columns for all dropdowns
            pin_map = st.selectbox("", csv_columns, key="pin_map", label_visibility="collapsed",
                                   index=csv_columns.index(existing_mappings.get('pin')) if existing_mappings.get('pin') in csv_columns else 0)
            
            owner_map = st.selectbox("", csv_columns, key="owner_map", label_visibility="collapsed",
                                     index=csv_columns.index(existing_mappings.get('owner')) if existing_mappings.get('owner') in csv_columns else 0)
            
            type_map = st.selectbox("", csv_columns, key="type_map", label_visibility="collapsed",
                                    index=csv_columns.index(existing_mappings.get('type')) if existing_mappings.get('type') in csv_columns else 0)
            
            addr_map = st.selectbox("", csv_columns, key="addr_map", label_visibility="collapsed",
                                    index=csv_columns.index(existing_mappings.get('address')) if existing_mappings.get('address') in csv_columns else 0)
            
            zip_map = st.selectbox("", csv_columns, key="zip_map", label_visibility="collapsed",
                                   index=csv_columns.index(existing_mappings.get('zip')) if existing_mappings.get('zip') in csv_columns else 0)
            
            sales_map = st.selectbox("", csv_columns, key="sales_map", label_visibility="collapsed",
                                     index=csv_columns.index(existing_mappings.get('sales')) if existing_mappings.get('sales') in csv_columns else 0)
            
            tax_map = st.selectbox("", csv_columns, key="tax_map", label_visibility="collapsed",
                                   index=csv_columns.index(existing_mappings.get('tax')) if existing_mappings.get('tax') in csv_columns else 0)
        
        with col3:
            st.markdown("<p style='font-weight: 600; color: var(--text-primary); margin-bottom: 0.75rem;'>Preview</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 0.875rem;'>123-45-678</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 0.875rem;'>SMITH PROPERTIES LLC</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 0.875rem;'>1-FAMILY PLATTED LOT</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 0.875rem;'>1234 Main St</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 0.875rem;'>44101</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; border-bottom: 1px solid rgba(255, 255, 255, 0.08); font-family: monospace; font-size: 0.875rem;'>$185,000</p>", unsafe_allow_html=True)
            st.markdown("<p style='padding: 0.75rem 0; font-family: monospace; font-size: 0.875rem;'>$4,250</p>", unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Navigation
        col_left, col_right = st.columns([1, 2])
        with col_left:
            if st.button("← Previous", use_container_width=True, key="step3_prev"):
                st.session_state.upload_step = 2
                st.rerun()
        with col_right:
            if st.button("Next: Configure →", type="primary", use_container_width=True, key="step3_next"):
                # Store mappings in session state
                st.session_state.column_mappings = {
                    'pin': pin_map,
                    'owner': owner_map,
                    'type': type_map,
                    'address': addr_map,
                    'zip': zip_map,
                    'sales': sales_map,
                    'tax': tax_map
                }
                st.session_state.upload_step = 4
                st.rerun()

# ====================================
# Step 4: Property Configuration
# ====================================

elif current_step == 4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1.5rem;'>Step 4: Property Configuration</h3>", unsafe_allow_html=True)
    
    st.markdown("<p style='font-size: 0.9375rem; font-weight: 600; color: var(--text-primary); margin-bottom: 1rem;'>Select Valid Property Types</p>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1.5rem;'>Choose which property types should be included in the analysis</p>", unsafe_allow_html=True)
    
    # Get existing selections from session state if available
    existing_types = st.session_state.get('property_types', {})
    
    col1, col2 = st.columns(2)
    with col1:
        one_family = st.checkbox(
            "1-FAMILY PLATTED LOT", 
            value=existing_types.get('1-FAMILY PLATTED LOT', True),
            key="prop_1family"
        )
        two_family = st.checkbox(
            "2-FAMILY PLATTED LOT", 
            value=existing_types.get('2-FAMILY PLATTED LOT', True),
            key="prop_2family"
        )
        three_family = st.checkbox(
            "3-FAMILY PLATTED LOT", 
            value=existing_types.get('3-FAMILY PLATTED LOT', False),
            key="prop_3family"
        )
    with col2:
        commercial = st.checkbox(
            "COMMERCIAL BUILDING", 
            value=existing_types.get('COMMERCIAL BUILDING', False),
            key="prop_commercial"
        )
        vacant = st.checkbox(
            "VACANT LAND", 
            value=existing_types.get('VACANT LAND', False),
            key="prop_vacant"
        )
        condo = st.checkbox(
            "CONDOMINIUM UNIT", 
            value=existing_types.get('CONDOMINIUM UNIT', False),
            key="prop_condo"
        )
    
    # Count selected types
    selected_count = sum([one_family, two_family, three_family, commercial, vacant, condo])
    
    if selected_count > 0:
        st.success(f"✅ {selected_count} property type(s) selected")
    else:
        st.warning("⚠️ Please select at least one property type")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_left, col_right = st.columns([1, 2])
    with col_left:
        if st.button("← Previous", use_container_width=True, key="step4_prev"):
            st.session_state.upload_step = 3
            st.rerun()
    with col_right:
        if st.button("Next: Import →", type="primary", use_container_width=True, key="step4_next", disabled=(selected_count == 0)):
            st.session_state.property_types = {
                '1-FAMILY PLATTED LOT': one_family,
                '2-FAMILY PLATTED LOT': two_family,
                '3-FAMILY PLATTED LOT': three_family,
                'COMMERCIAL BUILDING': commercial,
                'VACANT LAND': vacant,
                'CONDOMINIUM UNIT': condo
            }
            st.session_state.upload_step = 5
            st.rerun()

# ====================================
# Step 5: Import Process
# ====================================

elif current_step == 5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1.5rem;'>Step 5: Ready to Import</h3>", unsafe_allow_html=True)
    
    st.success("**Validation Complete:** All requirements met. Ready to import data.")
    
    # Show summary of configuration
    st.markdown("<h4 style='font-size: 1rem; margin-top: 1.5rem; margin-bottom: 1rem;'>Import Summary</h4>", unsafe_allow_html=True)
    
    city_info = st.session_state.get('city_info', {})
    property_types = st.session_state.get('property_types', {})
    selected_types = [k for k, v in property_types.items() if v]
    
    st.markdown(f"""
    <div style="background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 0.5rem; border: 1px solid rgba(255, 255, 255, 0.08);">
        <p style="margin: 0.5rem 0;"><strong>Market:</strong> {city_info.get('display_name', 'N/A')}</p>
        <p style="margin: 0.5rem 0;"><strong>Location:</strong> {city_info.get('state', 'N/A')}</p>
        <p style="margin: 0.5rem 0;"><strong>Property Types:</strong> {len(selected_types)} selected</p>
        <p style="margin: 0.5rem 0;"><strong>Files:</strong> 3 uploaded</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize import state if not exists
    if 'import_started' not in st.session_state:
        st.session_state.import_started = False
    
    if 'import_result' not in st.session_state:
        st.session_state.import_result = None
    
    # Progress bar and status (only show if import started)
    if st.session_state.import_started:
        progress_bar = st.progress(0)
        status_text = st.empty()
        result_container = st.empty()
        
        # Perform actual import
        uploaded_files = st.session_state.get('uploaded_files', {})
        city_info = st.session_state.get('city_info', {})
        column_mappings = st.session_state.get('column_mappings', {})
        property_types = st.session_state.get('property_types', {})
        
        # Progress and status callbacks
        def update_progress(value):
            progress_bar.progress(value)
        
        def update_status(message):
            status_text.text(message)
        
        # Perform import
        success, message, counts = perform_import(
            city_info=city_info,
            uploaded_files=uploaded_files,
            column_mappings=column_mappings,
            property_types=property_types,
            progress_callback=update_progress,
            status_callback=update_status
        )
        
        # Store result
        st.session_state.import_result = {
            'success': success,
            'message': message,
            'counts': counts
        }
        
        # Display result
        if success:
            parcels = counts.get('parcels', 0)
            owners = counts.get('target_owners', 0)
            
            result_container.success(
                f"✅ **Import Complete!**\n\n"
                f"Successfully imported:\n"
                f"- {parcels:,} parcels\n"
                f"- {owners:,} target investors\n\n"
                f"{message}"
            )
            st.balloons()
        else:
            result_container.error(
                f"❌ **Import Failed**\n\n"
                f"{message}\n\n"
                f"Please check your files and try again."
            )
        
        # Reset import state
        st.session_state.import_started = False
        
        # Show completion actions (only if import was successful)
        if success:
            st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            col_view, col_new = st.columns(2)
            
            with col_view:
                if st.button("📊 View Dashboard", type="primary", use_container_width=True, key="view_dashboard"):
                    # Reset wizard state
                    st.session_state.upload_step = 1
                    st.session_state.city_info = {}
                    st.session_state.uploaded_files = {}
                    st.session_state.column_mappings = {}
                    st.session_state.property_types = {}
                    st.session_state.import_result = None
                    st.switch_page("pages/1_Home.py")
            
            with col_new:
                if st.button("➕ Add Another Market", use_container_width=True, key="add_another"):
                    # Reset wizard state
                    st.session_state.upload_step = 1
                    st.session_state.city_info = {}
                    st.session_state.uploaded_files = {}
                    st.session_state.column_mappings = {}
                    st.session_state.property_types = {}
                    st.session_state.import_result = None
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            # Show retry button if import failed
            st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col2:
                if st.button("🔄 Return to Step 1", type="primary", use_container_width=True, key="retry_import"):
                    # Reset wizard state to start over
                    st.session_state.upload_step = 1
                    st.session_state.city_info = {}
                    st.session_state.uploaded_files = {}
                    st.session_state.column_mappings = {}
                    st.session_state.property_types = {}
                    st.session_state.import_result = None
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation (only show if import not started)
    if not st.session_state.import_started:
        col_left, col_right = st.columns([1, 2])
        with col_left:
            if st.button("← Previous", use_container_width=True, key="step5_prev"):
                st.session_state.upload_step = 4
                st.rerun()
        with col_right:
            if st.button("🚀 Start Import", type="primary", use_container_width=True, key="start_import"):
                st.session_state.import_started = True
                st.rerun()

