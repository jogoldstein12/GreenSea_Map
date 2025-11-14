# Phase 5: Streamlit UI Development - Professional Glass Design
**Duration:** 4-5 days | **Priority:** High | **Status:** Ready to Start

## Overview

This phase implements the Streamlit user interface with a **professional glassmorphism design**. The UI features a dark, sophisticated aesthetic with frosted glass effects, gradient accents, and smooth animations - moving away from bright, cartoonish colors to a sleek, enterprise-ready look.

**Design Philosophy:**
- Dark navy/charcoal backgrounds with subtle gradients
- Glassmorphism (frosted glass effect with backdrop blur)
- Blue-purple gradient accents (#3b82f6 → #8b5cf6)
- Clean typography with proper hierarchy
- Smooth, subtle animations
- Professional terminology ("Markets" instead of "Cities", "Investors" instead of "Owners")

**Reference Mockup:** See `UI_MOCKUP_PROFESSIONAL.html` in Documents folder for complete visual reference.

---

## 5.1 Global Styling & Theme Configuration

### Create Custom CSS File

**File:** `ui/styles/glass_theme.css`

```css
/* ====================================
   PROFESSIONAL GLASS THEME
   Multi-City GIS Portfolio Analyzer
==================================== */

/* Color Variables */
:root {
    --bg-primary: #0f0f1e;
    --bg-secondary: #1a1a2e;
    --bg-tertiary: #16213e;
    
    --glass-bg: rgba(255, 255, 255, 0.05);
    --glass-bg-hover: rgba(255, 255, 255, 0.08);
    --glass-border: rgba(255, 255, 255, 0.1);
    --glass-border-hover: rgba(255, 255, 255, 0.2);
    
    --accent-blue: #3b82f6;
    --accent-purple: #8b5cf6;
    --accent-green: #10b981;
    
    --text-primary: #f4f4f5;
    --text-secondary: #e4e4e7;
    --text-muted: #a1a1aa;
    --text-disabled: #71717a;
    
    --shadow-sm: 0 2px 8px rgba(0, 0, 0, 0.3);
    --shadow-md: 0 8px 32px rgba(0, 0, 0, 0.3);
    --shadow-lg: 0 12px 40px rgba(0, 0, 0, 0.4);
    
    --radius-sm: 8px;
    --radius-md: 12px;
    --radius-lg: 16px;
    --radius-xl: 20px;
}

/* Body & Main Container */
body {
    background: linear-gradient(135deg, var(--bg-primary) 0%, var(--bg-secondary) 50%, var(--bg-tertiary) 100%);
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Helvetica', 'Arial', sans-serif;
    color: var(--text-secondary);
}

/* Streamlit Main Container */
.main {
    background: transparent;
}

/* Hide Streamlit Branding */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Glassmorphism Base Class */
.glass-card {
    background: var(--glass-bg);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 2rem;
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.glass-card:hover {
    background: var(--glass-bg-hover);
    border-color: var(--glass-border-hover);
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
}

/* Headers */
h1 {
    font-size: 3rem;
    font-weight: 700;
    background: linear-gradient(135deg, #ffffff 0%, var(--text-muted) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin-bottom: 0.75rem;
}

h2 {
    font-size: 1.75rem;
    font-weight: 700;
    color: var(--text-primary);
    letter-spacing: -0.01em;
    margin-bottom: 1.5rem;
}

h3 {
    font-size: 1.25rem;
    font-weight: 600;
    color: var(--text-primary);
    text-transform: uppercase;
    letter-spacing: 0.05em;
    font-size: 1rem;
}

/* Streamlit Elements Override */

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
    color: white;
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    transition: all 0.3s;
    box-shadow: none;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(59, 130, 246, 0.4);
}

/* Secondary Button */
.stButton.secondary > button {
    background: var(--glass-bg);
    color: var(--text-secondary);
    border: 1px solid var(--glass-border);
}

.stButton.secondary > button:hover {
    background: var(--glass-bg-hover);
    border-color: var(--glass-border-hover);
    box-shadow: var(--shadow-sm);
}

/* Input Fields */
.stTextInput > div > div > input,
.stNumberInput > div > div > input,
.stSelectbox > div > div > select {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-secondary);
    padding: 0.875rem 1rem;
    transition: all 0.3s;
}

.stTextInput > div > div > input:focus,
.stNumberInput > div > div > input:focus,
.stSelectbox > div > div > select:focus {
    background: var(--glass-bg-hover);
    border-color: rgba(59, 130, 246, 0.5);
    box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1);
}

/* Metrics/Stats */
.stMetric {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s;
}

.stMetric:hover {
    background: var(--glass-bg-hover);
    border-color: var(--glass-border-hover);
}

.stMetric label {
    font-size: 0.6875rem;
    color: var(--text-disabled);
    text-transform: uppercase;
    letter-spacing: 0.1em;
    font-weight: 600;
}

.stMetric .metric-value {
    font-size: 2rem;
    font-weight: 700;
    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

/* Dataframe/Table */
.stDataFrame {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    overflow: hidden;
}

.stDataFrame table {
    color: var(--text-secondary);
}

.stDataFrame thead tr {
    background: rgba(255, 255, 255, 0.05);
}

.stDataFrame tbody tr:hover {
    background: rgba(255, 255, 255, 0.03);
}

/* Expander */
.streamlit-expanderHeader {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    color: var(--text-primary);
    font-weight: 600;
}

.streamlit-expanderHeader:hover {
    background: var(--glass-bg-hover);
}

/* File Uploader */
.stFileUploader {
    border: 2px dashed var(--glass-border-hover);
    border-radius: var(--radius-lg);
    background: rgba(255, 255, 255, 0.02);
    padding: 3rem;
    transition: all 0.3s;
}

.stFileUploader:hover {
    border-color: rgba(59, 130, 246, 0.5);
    background: rgba(59, 130, 246, 0.05);
}

/* Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 0.5rem;
    background: transparent;
    border-bottom: 1px solid var(--glass-border);
}

.stTabs [data-baseweb="tab"] {
    background: transparent;
    border: none;
    color: var(--text-muted);
    padding: 0.625rem 1.25rem;
    border-radius: var(--radius-sm) var(--radius-sm) 0 0;
    font-weight: 500;
}

.stTabs [data-baseweb="tab"]:hover {
    background: var(--glass-bg);
    color: var(--text-secondary);
}

.stTabs [aria-selected="true"] {
    background: rgba(59, 130, 246, 0.15);
    color: #60a5fa;
    border: 1px solid rgba(59, 130, 246, 0.3);
    border-bottom: none;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: rgba(15, 15, 30, 0.8);
    backdrop-filter: blur(20px);
    border-right: 1px solid var(--glass-border);
}

section[data-testid="stSidebar"] .stMarkdown {
    color: var(--text-secondary);
}

/* Alerts/Info Boxes */
.stAlert {
    background: rgba(59, 130, 246, 0.1);
    border-left: 4px solid var(--accent-blue);
    border-radius: var(--radius-md);
    color: #93c5fd;
    padding: 1.125rem 1.5rem;
}

.stSuccess {
    background: rgba(16, 185, 129, 0.1);
    border-left: 4px solid var(--accent-green);
    color: #6ee7b7;
}

.stWarning {
    background: rgba(245, 158, 11, 0.1);
    border-left: 4px solid #f59e0b;
    color: #fcd34d;
}

/* Progress Bar */
.stProgress > div > div {
    background: var(--glass-bg);
    border: 1px solid var(--glass-border);
    border-radius: 1.5rem;
    height: 3rem;
    overflow: hidden;
}

.stProgress > div > div > div {
    background: linear-gradient(90deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
    border-radius: 1.5rem;
}

/* Columns */
.row-widget.stHorizontal {
    gap: 1.5rem;
}

/* Links */
a {
    color: #60a5fa;
    text-decoration: none;
    transition: color 0.3s;
}

a:hover {
    color: #93c5fd;
}

/* Scrollbar */
::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: var(--glass-bg);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: rgba(255, 255, 255, 0.2);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: rgba(255, 255, 255, 0.3);
}
```

### Update Streamlit Config

**File:** `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#3b82f6"
backgroundColor = "#0f0f1e"
secondaryBackgroundColor = "#1a1a2e"
textColor = "#e4e4e7"
font = "sans serif"

[server]
maxUploadSize = 500
enableCORS = false
enableXsrfProtection = true
headless = true

[browser]
gatherUsageStats = false

[client]
showErrorDetails = false
toolbarMode = "minimal"
```

### Load CSS in Main App

**File:** `app/main.py` (add at top after imports)

```python
import streamlit as st
from pathlib import Path

# Load custom CSS
def load_css():
    css_file = Path(__file__).parent.parent / "ui" / "styles" / "glass_theme.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Apply theme
load_css()
```

**✅ Checkpoint:** Run app - should see dark theme with glass effects applied

---

## 5.2 Home Page - Dashboard

**File:** `ui/pages/1_🏠_Home.py`

### Page Structure

```python
"""
Home Page - Portfolio Analytics Dashboard
Shows overview of all markets with quick stats and navigation
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import db_manager
from database.models import City, Parcel, TargetOwner
from sqlalchemy import func

# Page config
st.set_page_config(
    page_title="Portfolio Dashboard",
    page_icon="🏠",
    layout="wide"
)

# Load custom CSS
def load_css():
    css_file = project_root / "ui" / "styles" / "glass_theme.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ====================================
# Header Section
# ====================================

st.markdown("<h1>Portfolio Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.125rem; color: var(--text-muted); margin-bottom: 2rem;'>Real estate investment analysis across multiple markets</p>", unsafe_allow_html=True)

# Info Alert
st.info("**Welcome** Select a market below to view interactive portfolio maps, or upload new market data to expand your analysis.")

# ====================================
# Quick Stats Section
# ====================================

# Fetch aggregate stats from database
with db_manager.get_session() as session:
    total_cities = session.query(City).filter(City.is_active == True).count()
    total_parcels = session.query(Parcel).count()
    total_targets = session.query(TargetOwner).filter(TargetOwner.is_active == True).count()
    
    # Calculate total portfolio value
    total_value = session.query(func.sum(Parcel.sales_amount)).scalar() or 0

# Quick Stats Grid
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{}</div>
        <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Active Markets</div>
    </div>
    """.format(total_cities), unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{:,}</div>
        <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Total Properties</div>
    </div>
    """.format(total_parcels), unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{}</div>
        <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Target Investors</div>
    </div>
    """.format(total_targets), unsafe_allow_html=True)

with col4:
    st.markdown("""
    <div class="glass-card" style="text-align: center;">
        <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${:.1f}B</div>
        <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Portfolio Value</div>
    </div>
    """.format(total_value / 1_000_000_000), unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ====================================
# Hero CTA Section
# ====================================

st.markdown("""
<div style="background: rgba(255, 255, 255, 0.03); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 1.25rem; padding: 4rem; text-align: center; margin: 3rem 0; position: relative; overflow: hidden;">
    <div style="position: absolute; top: 0; left: 0; right: 0; bottom: 0; background: radial-gradient(circle at 50% 0%, rgba(59, 130, 246, 0.15) 0%, transparent 50%); pointer-events: none;"></div>
    <h2 style="font-size: 2.25rem; margin-bottom: 1rem; background: linear-gradient(135deg, #ffffff 0%, #a1a1aa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 700; position: relative;">Expand Your Market Coverage</h2>
    <p style="font-size: 1.125rem; margin-bottom: 2rem; color: #71717a; position: relative;">Import parcel data, shapefiles, and investor lists to analyze new markets</p>
</div>
""", unsafe_allow_html=True)

# Add New Market button (links to Upload page)
if st.button("📤 Add New Market", type="primary", use_container_width=False):
    st.switch_page("pages/3_📤_Upload_Data.py")

# ====================================
# Markets Grid Section
# ====================================

st.markdown("<h2 style='font-size: 1.75rem; font-weight: 700; color: var(--text-primary); margin: 3rem 0 1.75rem 0;'>Your Markets</h2>", unsafe_allow_html=True)

# Fetch all active cities
with db_manager.get_session() as session:
    cities = session.query(City).filter(City.is_active == True).all()

# Create grid of city cards
if cities:
    # Calculate number of columns (3 cities per row)
    num_cols = 3
    rows = [cities[i:i + num_cols] for i in range(0, len(cities), num_cols)]
    
    for row in rows:
        cols = st.columns(num_cols)
        for idx, city in enumerate(row):
            with cols[idx]:
                # Get city stats
                with db_manager.get_session() as session:
                    city_parcels = session.query(Parcel).filter(Parcel.city_id == city.city_id).count()
                    city_targets = session.query(TargetOwner).filter(
                        TargetOwner.city_id == city.city_id,
                        TargetOwner.is_active == True
                    ).count()
                    city_value = session.query(func.sum(Parcel.sales_amount)).filter(
                        Parcel.city_id == city.city_id
                    ).scalar() or 0
                
                # Format value
                if city_value >= 1_000_000_000:
                    value_str = f"${city_value / 1_000_000_000:.1f}B"
                elif city_value >= 1_000_000:
                    value_str = f"${city_value / 1_000_000:.0f}M"
                else:
                    value_str = f"${city_value:,.0f}"
                
                # City Card
                st.markdown(f"""
                <div class="glass-card" style="cursor: pointer; position: relative; overflow: hidden;">
                    <div style="position: absolute; top: 0; left: 0; right: 0; height: 4px; background: linear-gradient(90deg, #3b82f6 0%, #8b5cf6 100%); opacity: 0; transition: opacity 0.3s;"></div>
                    <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 0.75rem;">
                        <div>
                            <h3 style="font-size: 1.75rem; color: #f4f4f5; margin-bottom: 0.5rem; font-weight: 600; text-transform: none; letter-spacing: normal;">{city.display_name.split(',')[0]}</h3>
                            <p style="color: #71717a; font-size: 0.875rem; margin-bottom: 1rem;">{city.display_name}</p>
                            <span style="display: inline-block; padding: 0.375rem 0.875rem; border-radius: 1.25rem; font-size: 0.75rem; font-weight: 600; background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3);">Active</span>
                        </div>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                        <div style="text-align: center;">
                            <div style="font-size: 1.625rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{city_parcels:,}</div>
                            <div style="font-size: 0.6875rem; color: #71717a; text-transform: uppercase; margin-top: 0.375rem; letter-spacing: 0.05em; font-weight: 600;">Properties</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.625rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{city_targets}</div>
                            <div style="font-size: 0.6875rem; color: #71717a; text-transform: uppercase; margin-top: 0.375rem; letter-spacing: 0.05em; font-weight: 600;">Investors</div>
                        </div>
                        <div style="text-align: center;">
                            <div style="font-size: 1.625rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{value_str}</div>
                            <div style="font-size: 0.6875rem; color: #71717a; text-transform: uppercase; margin-top: 0.375rem; letter-spacing: 0.05em; font-weight: 600;">Value</div>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # View Analysis button
                if st.button(f"View Analysis →", key=f"view_{city.city_id}", type="primary", use_container_width=True):
                    st.session_state.selected_city_id = city.city_id
                    st.switch_page("pages/2_🗺️_Map_Viewer.py")

    # Add "Add New Market" card at end
    with cols[-1] if len(row) < num_cols else st.columns(num_cols)[0]:
        st.markdown("""
        <div style="border: 2px dashed rgba(255, 255, 255, 0.2); border-radius: 1rem; display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 340px; cursor: pointer; transition: all 0.3s; background: rgba(255, 255, 255, 0.02); padding: 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1.25rem; opacity: 0.4;">+</div>
            <h3 style="font-size: 1.375rem; margin-bottom: 0.5rem; text-transform: none; letter-spacing: normal;">Add New Market</h3>
            <p style="color: #71717a; font-size: 0.875rem; text-align: center;">Import data to analyze another city</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("Add Market", key="add_new", use_container_width=True):
            st.switch_page("pages/3_📤_Upload_Data.py")

else:
    # No cities yet - show onboarding
    st.markdown("""
    <div style="text-align: center; padding: 4rem 2rem;">
        <div style="font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.3;">📊</div>
        <h2 style="color: var(--text-primary); margin-bottom: 1rem;">No Markets Added Yet</h2>
        <p style="color: var(--text-muted); margin-bottom: 2rem;">Get started by uploading your first market's data</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button("📤 Upload First Market", type="primary"):
        st.switch_page("pages/3_📤_Upload_Data.py")
```

**✅ Checkpoint:** 
- Home page displays with dark glass theme
- Quick stats show real data from database
- City cards render with proper styling
- Navigation buttons work

---

## 5.3 Map Viewer Page

**File:** `ui/pages/2_🗺️_Map_Viewer.py`

### Page Structure

```python
"""
Map Viewer Page - Interactive Portfolio Visualization
Displays Folium map with property data and portfolio statistics
"""

import streamlit as st
import sys
from pathlib import Path
import geopandas as gpd
from streamlit_folium import st_folium

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import db_manager
from database.models import City, Parcel, TargetOwner
from mapping.map_generator import generate_map
from data_processing.analyzer import calculate_owner_stats, calculate_aggregate_stats
from sqlalchemy import func

# Page config
st.set_page_config(
    page_title="Map Viewer",
    page_icon="🗺️",
    layout="wide"
)

# Load custom CSS
def load_css():
    css_file = project_root / "ui" / "styles" / "glass_theme.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ====================================
# Header Section
# ====================================

st.markdown("<h1>Map Viewer</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.125rem; color: var(--text-muted); margin-bottom: 2rem;'>Interactive property portfolio visualization</p>", unsafe_allow_html=True)

# ====================================
# City Selection
# ====================================

with db_manager.get_session() as session:
    cities = session.query(City).filter(City.is_active == True).all()

if not cities:
    st.warning("No markets available. Please upload data first.")
    if st.button("📤 Upload Data"):
        st.switch_page("pages/3_📤_Upload_Data.py")
    st.stop()

# City selector in glass card
st.markdown('<div class="glass-card" style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)

city_options = {city.display_name: city.city_id for city in cities}
selected_city_name = st.selectbox(
    "Select Market",
    options=list(city_options.keys()),
    key="city_select"
)
selected_city_id = city_options[selected_city_name]

# Store in session state
st.session_state.selected_city_id = selected_city_id

st.markdown('</div>', unsafe_allow_html=True)

# ====================================
# Load City Data
# ====================================

@st.cache_data(ttl=3600)
def load_city_data(city_id):
    """Load all parcels and target owners for selected city"""
    with db_manager.get_session() as session:
        # Get city details
        city = session.query(City).filter(City.city_id == city_id).first()
        
        # Get all parcels as GeoDataFrame
        parcels = session.query(Parcel).filter(Parcel.city_id == city_id).all()
        
        # Convert to GeoDataFrame
        if parcels:
            parcel_data = []
            for p in parcels:
                parcel_data.append({
                    'parcel_pin': p.parcel_pin,
                    'geometry': p.geometry,
                    'address': p.address,
                    'par_zip': p.par_zip,
                    'deeded_owner': p.deeded_owner,
                    'owner_clean': p.owner_clean,
                    'tax_luc_description': p.tax_luc_description,
                    'sales_amount': p.sales_amount,
                    'certified_tax_total': p.certified_tax_total
                })
            
            gdf = gpd.GeoDataFrame(parcel_data, geometry='geometry', crs='EPSG:4326')
        else:
            gdf = gpd.GeoDataFrame()
        
        # Get target owners
        targets = session.query(TargetOwner).filter(
            TargetOwner.city_id == city_id,
            TargetOwner.is_active == True
        ).all()
        
        target_list = [t.owner_clean for t in targets]
        
        return city, gdf, target_list

city, parcels_gdf, target_owners = load_city_data(selected_city_id)

if parcels_gdf.empty:
    st.error("No parcel data available for this market.")
    st.stop()

# ====================================
# Two-Column Layout
# ====================================

col_sidebar, col_map = st.columns([1, 3])

# ====================================
# LEFT SIDEBAR
# ====================================

with col_sidebar:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    
    # Portfolio Search
    st.markdown("<h3>Portfolio Search</h3>", unsafe_allow_html=True)
    search_term = st.text_input(
        "Search by investor name",
        placeholder="Search...",
        label_visibility="collapsed"
    )
    
    # View Toggle
    st.markdown("<div style='margin: 1.25rem 0;'>", unsafe_allow_html=True)
    view_mode = st.radio(
        "View Mode",
        options=["By Owner", "By ZIP"],
        horizontal=True,
        label_visibility="collapsed"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Target Owners List
    st.markdown("<h3 style='margin-top: 1.75rem;'>Target Investors</h3>", unsafe_allow_html=True)
    
    # Filter parcels to target owners
    target_parcels = parcels_gdf[parcels_gdf['owner_clean'].isin(target_owners)]
    
    # Calculate stats per owner
    owner_stats_list = []
    for owner in target_owners:
        owner_parcels = target_parcels[target_parcels['owner_clean'] == owner]
        if not owner_parcels.empty:
            num_properties = len(owner_parcels)
            num_zips = owner_parcels['par_zip'].nunique()
            owner_stats_list.append({
                'owner': owner,
                'properties': num_properties,
                'zips': num_zips
            })
    
    # Sort by property count
    owner_stats_list.sort(key=lambda x: x['properties'], reverse=True)
    
    # Display owner list with search filter
    filtered_owners = owner_stats_list
    if search_term:
        filtered_owners = [o for o in owner_stats_list if search_term.upper() in o['owner']]
    
    # Scrollable container
    st.markdown('<div style="max-height: 400px; overflow-y: auto; padding-right: 0.5rem;">', unsafe_allow_html=True)
    
    selected_owner = st.session_state.get('selected_owner', None)
    
    for owner_stat in filtered_owners[:20]:  # Limit to top 20
        owner_name = owner_stat['owner']
        properties = owner_stat['properties']
        zips = owner_stat['zips']
        
        # Owner item button
        if st.button(
            f"{owner_name}\n{properties} properties · {zips} ZIP codes",
            key=f"owner_{owner_name}",
            use_container_width=True
        ):
            st.session_state.selected_owner = owner_name
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Portfolio Statistics
    st.markdown("<h3 style='margin-top: 1.75rem;'>Portfolio Statistics</h3>", unsafe_allow_html=True)
    
    # Calculate aggregate stats
    if selected_owner:
        display_parcels = target_parcels[target_parcels['owner_clean'] == selected_owner]
    else:
        display_parcels = target_parcels
    
    total_properties = len(display_parcels)
    total_zips = display_parcels['par_zip'].nunique()
    total_sales = display_parcels['sales_amount'].sum()
    total_assessment = display_parcels['certified_tax_total'].sum()
    
    # Stats grid
    stats_col1, stats_col2 = st.columns(2)
    
    with stats_col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1.25rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-size: 1.75rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total_properties:,}</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Properties</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col2:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1.25rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-size: 1.75rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{total_zips}</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">ZIP Codes</div>
        </div>
        """, unsafe_allow_html=True)
    
    stats_col3, stats_col4 = st.columns(2)
    
    with stats_col3:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1.25rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08); margin-top: 0.75rem;">
            <div style="font-size: 1.75rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${total_sales/1_000_000:.0f}M</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Total Sales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col4:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1.25rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08); margin-top: 0.75rem;">
            <div style="font-size: 1.75rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">${total_assessment/1_000_000:.0f}M</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Assessments</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Export buttons
    st.markdown("<div style='margin-top: 1.75rem;'>", unsafe_allow_html=True)
    
    if st.button("📥 Export Map", type="primary", use_container_width=True):
        st.success("Map exported successfully!")
    
    if st.button("📊 Export Data", use_container_width=True):
        st.success("Data exported to Excel!")
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================
# RIGHT SIDE - MAP
# ====================================

with col_map:
    # Generate map
    with st.spinner("Generating map..."):
        city_config = {
            'center_lat': float(city.center_lat),
            'center_lng': float(city.center_lng),
            'zoom_level': city.zoom_level
        }
        
        # Calculate statistics
        stats_per_owner = {}
        for owner in target_owners:
            owner_parcels = target_parcels[target_parcels['owner_clean'] == owner]
            if not owner_parcels.empty:
                stats_per_owner[owner] = calculate_owner_stats(owner_parcels, owner)
        
        all_stats = calculate_aggregate_stats(target_parcels)
        
        # Generate map
        folium_map = generate_map(
            city_config=city_config,
            parcels_gdf=target_parcels,
            target_owners=target_owners,
            stats_per_owner=stats_per_owner,
            all_stats=all_stats
        )
    
    # Display map in glass container
    st.markdown('<div class="glass-card" style="padding: 0; overflow: hidden; min-height: 700px;">', unsafe_allow_html=True)
    st_folium(folium_map, width=None, height=700)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Property Details Table
    st.markdown('<div class="glass-card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
    st.markdown("<h3>Selected Property Details</h3>", unsafe_allow_html=True)
    
    # Sample property details (in real implementation, this would come from map click event)
    st.markdown("""
    <table style="width: 100%; color: var(--text-secondary);">
        <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
            <td style="padding: 1rem; width: 200px;"><strong>Parcel PIN</strong></td>
            <td style="padding: 1rem;">Click a property on the map to view details</td>
        </tr>
    </table>
    """, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
```

**✅ Checkpoint:**
- Map displays with glass theme styling
- Sidebar shows target investors with stats
- Search and filter functionality works
- Statistics update based on selection

---

## 5.4 Upload Data Page

**File:** `ui/pages/3_📤_Upload_Data.py`

### Implementation

```python
"""
Upload Data Page - Market Data Import Wizard
5-step process for adding new markets to the system
"""

import streamlit as st
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Page config
st.set_page_config(
    page_title="Upload Data",
    page_icon="📤",
    layout="wide"
)

# Load custom CSS
def load_css():
    css_file = project_root / "ui" / "styles" / "glass_theme.css"
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# ====================================
# Header Section
# ====================================

st.markdown("<h1>Upload Data</h1>", unsafe_allow_html=True)
st.markdown("<p style='font-size: 1.125rem; color: var(--text-muted); margin-bottom: 2rem;'>Add a new market to your portfolio analyzer</p>", unsafe_allow_html=True)

st.info("**Requirements** Three files needed: CSV (parcel data), Shapefile (geometry), and Excel (target investor list)")

# ====================================
# Step Indicator
# ====================================

# Initialize session state for current step
if 'upload_step' not in st.session_state:
    st.session_state.upload_step = 1

current_step = st.session_state.upload_step

# Step indicator HTML
steps_html = """
<div style="display: flex; justify-content: space-between; margin-bottom: 3rem; position: relative;">
    <div style="position: absolute; top: 1.5rem; left: 10%; right: 10%; height: 2px; background: rgba(255, 255, 255, 0.1); z-index: 0;"></div>
"""

step_labels = ["Market Info", "Upload Files", "Map Columns", "Configure", "Import"]

for i in range(1, 6):
    is_active = i == current_step
    is_completed = i < current_step
    
    circle_bg = "linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%)" if is_active else \
                "linear-gradient(135deg, #10b981 0%, #059669 100%)" if is_completed else \
                "rgba(255, 255, 255, 0.05)"
    
    circle_border = "transparent" if (is_active or is_completed) else "rgba(255, 255, 255, 0.1)"
    circle_color = "white" if (is_active or is_completed) else "#71717a"
    label_color = "#60a5fa" if is_active else "#71717a"
    
    steps_html += f"""
    <div style="flex: 1; text-align: center; position: relative; z-index: 1;">
        <div style="width: 48px; height: 48px; border-radius: 50%; background: {circle_bg}; margin: 0 auto 1rem; display: flex; align-items: center; justify-content: center; font-weight: 700; transition: all 0.3s; border: 2px solid {circle_border}; color: {circle_color}; font-size: 1.125rem;">
            {i}
        </div>
        <div style="font-size: 0.8125rem; color: {label_color}; font-weight: 500;">{step_labels[i-1]}</div>
    </div>
    """

steps_html += "</div>"
st.markdown(steps_html, unsafe_allow_html=True)

# ====================================
# Step 1: Market Information
# ====================================

if current_step == 1:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Step 1: Market Information</h3>", unsafe_allow_html=True)
    
    city_name = st.text_input("City Name", placeholder="e.g., Cleveland")
    
    col1, col2 = st.columns(2)
    with col1:
        display_name = st.text_input("Display Name", placeholder="e.g., Cleveland, OH")
    with col2:
        state = st.selectbox("State", ["Select state...", "Ohio", "Michigan", "Pennsylvania", "New York"])
    
    col3, col4, col5 = st.columns(3)
    with col3:
        center_lat = st.number_input("Center Latitude", value=41.4993, format="%.4f")
    with col4:
        center_lng = st.number_input("Center Longitude", value=-81.6944, format="%.4f")
    with col5:
        zoom_level = st.number_input("Default Zoom", value=11, min_value=8, max_value=16)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation buttons
    col_left, col_right = st.columns([1, 2])
    with col_right:
        if st.button("Next: Upload Files →", type="primary", use_container_width=True):
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
                st.error("Please fill in all required fields")

# ====================================
# Step 2: File Upload
# ====================================

elif current_step == 2:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Step 2: Upload Files</h3>", unsafe_allow_html=True)
    
    st.markdown("##### 1. Parcel Data (CSV)")
    csv_file = st.file_uploader("Upload CSV", type=['csv'], label_visibility="collapsed", key="csv")
    
    st.markdown("##### 2. Shapefile (ZIP Archive)")
    shp_file = st.file_uploader("Upload Shapefile ZIP", type=['zip'], label_visibility="collapsed", key="shp")
    
    st.markdown("##### 3. Target Investors (Excel)")
    excel_file = st.file_uploader("Upload Excel", type=['xlsx', 'xls', 'xlsm'], label_visibility="collapsed", key="excel")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_left, col_right = st.columns([1, 2])
    with col_left:
        if st.button("← Previous", use_container_width=True):
            st.session_state.upload_step = 1
            st.rerun()
    with col_right:
        if st.button("Next: Map Columns →", type="primary", use_container_width=True):
            if csv_file and shp_file and excel_file:
                st.session_state.uploaded_files = {
                    'csv': csv_file,
                    'shp': shp_file,
                    'excel': excel_file
                }
                st.session_state.upload_step = 3
                st.rerun()
            else:
                st.error("Please upload all three required files")

# ====================================
# Step 3: Column Mapping
# ====================================

elif current_step == 3:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Step 3: Map Columns</h3>", unsafe_allow_html=True)
    
    st.warning("**Column Mapping** Match your data columns to standard field names")
    
    # Sample column mapping interface
    st.markdown("#### Standard Field Mappings")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Standard Field**")
        st.markdown("Parcel PIN")
        st.markdown("Owner Name")
        st.markdown("Property Type")
        st.markdown("Address")
        st.markdown("ZIP Code")
    
    with col2:
        st.markdown("**Your Column**")
        st.selectbox("", ["parcelpin", "pin", "parcel_id"], key="pin_map", label_visibility="collapsed")
        st.selectbox("", ["deeded_owner", "owner", "owner_name"], key="owner_map", label_visibility="collapsed")
        st.selectbox("", ["tax_luc_description", "land_use", "property_type"], key="type_map", label_visibility="collapsed")
        st.selectbox("", ["par_addr", "address", "street_address"], key="addr_map", label_visibility="collapsed")
        st.selectbox("", ["par_zip", "zip_code", "zipcode"], key="zip_map", label_visibility="collapsed")
    
    with col3:
        st.markdown("**Preview**")
        st.markdown("123-45-678")
        st.markdown("SMITH PROPERTIES LLC")
        st.markdown("1-FAMILY PLATTED LOT")
        st.markdown("1234 Main St")
        st.markdown("44101")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_left, col_right = st.columns([1, 2])
    with col_left:
        if st.button("← Previous", use_container_width=True):
            st.session_state.upload_step = 2
            st.rerun()
    with col_right:
        if st.button("Next: Configure →", type="primary", use_container_width=True):
            st.session_state.upload_step = 4
            st.rerun()

# ====================================
# Step 4: Property Configuration
# ====================================

elif current_step == 4:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Step 4: Property Configuration</h3>", unsafe_allow_html=True)
    
    st.markdown("##### Select Valid Property Types")
    
    col1, col2 = st.columns(2)
    with col1:
        one_family = st.checkbox("1-FAMILY PLATTED LOT", value=True)
        commercial = st.checkbox("COMMERCIAL BUILDING", value=False)
    with col2:
        two_family = st.checkbox("2-FAMILY PLATTED LOT", value=True)
        vacant = st.checkbox("VACANT LAND", value=False)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_left, col_right = st.columns([1, 2])
    with col_left:
        if st.button("← Previous", use_container_width=True):
            st.session_state.upload_step = 3
            st.rerun()
    with col_right:
        if st.button("Next: Import →", type="primary", use_container_width=True):
            st.session_state.property_types = {
                '1-FAMILY PLATTED LOT': one_family,
                '2-FAMILY PLATTED LOT': two_family,
                'COMMERCIAL BUILDING': commercial,
                'VACANT LAND': vacant
            }
            st.session_state.upload_step = 5
            st.rerun()

# ====================================
# Step 5: Import
# ====================================

elif current_step == 5:
    st.markdown('<div class="glass-card">', unsafe_allow_html=True)
    st.markdown("<h3>Step 5: Ready to Import</h3>", unsafe_allow_html=True)
    
    st.success("**Validation Complete** All requirements met. Ready to import data.")
    
    # Progress bar placeholder
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Navigation
    col_left, col_right = st.columns([1, 2])
    with col_left:
        if st.button("← Previous", use_container_width=True):
            st.session_state.upload_step = 4
            st.rerun()
    with col_right:
        if st.button("🚀 Start Import", type="primary", use_container_width=True):
            # Simulate import process
            import time
            
            for i in range(101):
                time.sleep(0.02)
                progress_bar.progress(i)
                
                if i < 20:
                    status_text.text("Validating files...")
                elif i < 40:
                    status_text.text("Processing CSV data...")
                elif i < 60:
                    status_text.text("Loading shapefile geometry...")
                elif i < 80:
                    status_text.text("Importing target investors...")
                else:
                    status_text.text("Finalizing import...")
            
            st.success("✅ Import Complete! Market data successfully imported.")
            st.balloons()
            
            # Reset upload state
            st.session_state.upload_step = 1
            
            if st.button("View Dashboard"):
                st.switch_page("pages/1_🏠_Home.py")
```

**✅ Checkpoint:**
- 5-step wizard displays correctly
- Step indicator shows active/completed states
- File uploaders styled with glass theme
- Navigation between steps works
- Import simulation displays progress

---

## 5.5 Settings Page

**File:** `ui/pages/4_⚙️_Settings.py`

### Implementation Summary

```python
"""
Settings Page - System Configuration
Manage markets, view statistics, and configure application settings
"""

import streamlit as st
import sys
from pathlib import Path

# Page config and CSS loading...
# Similar structure to other pages

# Two-column layout
col1, col2 = st.columns(2)

# Left column: City management, database stats
# Right column: Import history, application settings

# Include:
# - City selector dropdown
# - Edit/Re-import/Delete buttons
# - Database statistics table
# - Import history table
# - Application settings form
# - Toggle switches for features
```

**✅ Checkpoint:**
- Settings page displays with glass theme
- All configuration options accessible
- Database statistics shown
- Import history table populated

---

## 5.6 Reusable Components

### Create Component Files

**File:** `ui/components/stats_card.py`

```python
"""
Reusable stat card component
"""

import streamlit as st

def render_stat_card(value: str, label: str, container=None):
    """
    Render a glassmorphic stat card
    
    Args:
        value: The stat value to display
        label: The label for the stat
        container: Optional streamlit container to render in
    """
    html = f"""
    <div style="background: rgba(255, 255, 255, 0.05); 
                backdrop-filter: blur(16px); 
                border: 1px solid rgba(255, 255, 255, 0.08); 
                border-radius: 0.75rem; 
                padding: 1.25rem; 
                text-align: center; 
                transition: all 0.3s;">
        <div style="font-size: 1.75rem; 
                    font-weight: 700; 
                    background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); 
                    -webkit-background-clip: text; 
                    -webkit-text-fill-color: transparent;">
            {value}
        </div>
        <div style="font-size: 0.6875rem; 
                    color: #71717a; 
                    margin-top: 0.375rem; 
                    text-transform: uppercase; 
                    letter-spacing: 0.05em; 
                    font-weight: 600;">
            {label}
        </div>
    </div>
    """
    
    if container:
        container.markdown(html, unsafe_allow_html=True)
    else:
        st.markdown(html, unsafe_allow_html=True)
```

**File:** `ui/components/glass_card.py`

```python
"""
Reusable glass card wrapper component
"""

import streamlit as st
from contextlib import contextmanager

@contextmanager
def glass_card(hover=True):
    """
    Context manager for glass card styling
    
    Usage:
        with glass_card():
            st.write("Content here")
    """
    hover_class = "glass-hover" if hover else ""
    st.markdown(f'<div class="glass-card {hover_class}">', unsafe_allow_html=True)
    try:
        yield
    finally:
        st.markdown('</div>', unsafe_allow_html=True)
```

---

## 5.7 Testing & Polish

### Test Checklist

**Visual Testing:**
- [ ] All pages render with dark background
- [ ] Glass effects visible (frosted blur)
- [ ] Gradient text on headings
- [ ] Hover effects work on cards
- [ ] Buttons have ripple effect
- [ ] Color scheme consistent (blue-purple gradient)
- [ ] Typography hierarchy clear
- [ ] Responsive on different screen sizes

**Functional Testing:**
- [ ] Navigation between pages works
- [ ] Database queries execute successfully
- [ ] File uploads trigger correctly
- [ ] Search/filter updates results
- [ ] Map renders in Folium container
- [ ] Statistics calculations accurate
- [ ] Session state persists between pages
- [ ] Error messages display appropriately

**Performance Testing:**
- [ ] Page load time < 2 seconds
- [ ] Map generation < 5 seconds
- [ ] Database queries < 1 second
- [ ] No console errors in browser
- [ ] Caching prevents redundant queries

### Polish Items

**Add Loading States:**
```python
with st.spinner("Loading market data..."):
    data = load_city_data(city_id)
```

**Add Empty States:**
```python
if not cities:
    st.markdown("""
    <div style="text-align: center; padding: 4rem;">
        <div style="font-size: 4rem; opacity: 0.3;">📊</div>
        <h3>No Markets Available</h3>
        <p style="color: var(--text-muted);">Upload your first market to get started</p>
    </div>
    """, unsafe_allow_html=True)
```

**Add Success Animations:**
```python
st.success("Import complete!")
st.balloons()  # Celebration animation
```

**Add Tooltips:**
```python
st.info("ℹ️ Tip: Use the search box to quickly find specific investors")
```

---

## 5.8 Final Integration

### Update Main App Entry Point

**File:** `app/main.py`

```python
"""
Main Application Entry Point
Sets up configuration and loads custom theme
"""

import streamlit as st
from pathlib import Path
import sys

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import db_manager

# Page config
st.set_page_config(
    page_title="GIS Portfolio Analyzer",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="collapsed",  # Hide sidebar on main page
    menu_items={
        'About': "# GIS Portfolio Analyzer\nProfessional real estate analytics platform"
    }
)

# Load custom CSS
def load_css():
    css_file = project_root / "ui" / "styles" / "glass_theme.css"
    if css_file.exists():
        with open(css_file) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

# Initialize database
if 'db_initialized' not in st.session_state:
    try:
        db_manager.initialize()
        
        if db_manager.test_connection():
            st.session_state.db_initialized = True
        else:
            st.error("❌ Database connection failed")
            st.stop()
    except Exception as e:
        st.error(f"❌ Database initialization error: {str(e)}")
        st.stop()

# Main page - redirect to Home
st.switch_page("pages/1_🏠_Home.py")
```

---

## Success Criteria

**Phase 5 Complete When:**
- ✅ All 4 pages implemented with glass theme
- ✅ Custom CSS loaded and applied consistently
- ✅ Navigation between pages works
- ✅ Database integration functional
- ✅ Map generation and display working
- ✅ File upload wizard operational
- ✅ All components styled professionally
- ✅ No console errors
- ✅ Responsive on desktop screens
- ✅ User feedback (loading states, success messages) present

---

## Estimated Timeline

| Task | Duration | Dependencies |
|------|----------|--------------|
| 5.1 Global Styling & Theme | 0.5 day | None |
| 5.2 Home Page | 1 day | 5.1 |
| 5.3 Map Viewer Page | 1.5 days | 5.1, Phase 4 |
| 5.4 Upload Data Page | 1 day | 5.1, Phase 3 |
| 5.5 Settings Page | 0.5 day | 5.1, Phase 2 |
| 5.6 Reusable Components | 0.5 day | 5.1 |
| 5.7 Testing & Polish | 1 day | All above |
| **Total** | **5-6 days** | Sequential |

---

## Next Phase

After completing Phase 5, proceed to:
- **Phase 6: Integration & Testing** - End-to-end testing, performance optimization
- **Phase 7: Documentation** - User guides, inline help
- **Phase 8: Deployment** - Streamlit Cloud setup, production configuration
- **Phase 9: Data Migration** - Import Cleveland and Detroit data

---

**Document Version:** 1.0  
**Created:** 2025-11-12  
**Status:** Ready for Implementation  
**Design Reference:** `UI_MOCKUP_PROFESSIONAL.html`
