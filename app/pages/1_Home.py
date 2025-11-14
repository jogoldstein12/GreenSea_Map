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
st.session_state.current_page = "Home"

# Import and render navigation
try:
    from ui.components.navigation import render_navigation
    render_navigation()
except Exception as e:
    st.error(f"Navigation error: {str(e)}")

# ====================================
# Header Section
# ====================================

st.markdown("<h1>Portfolio Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 1.125rem; color: var(--text-muted); margin-bottom: 2rem;'>"
    "Real estate investment analysis across multiple markets"
    "</p>", 
    unsafe_allow_html=True
)

# Info Alert
st.info(
    "**Welcome!** Select a market below to view interactive portfolio maps, "
    "or upload new market data to expand your analysis."
)

# ====================================
# Quick Stats Section
# ====================================

# Fetch aggregate stats from database
try:
    with db_manager.get_session() as session:
        total_cities = session.query(City).filter(City.is_active == True).count()
        total_parcels = session.query(Parcel).count()
        total_targets = session.query(TargetOwner).filter(TargetOwner.is_active == True).count()
        
        # Calculate total portfolio value
        total_value = session.query(func.sum(Parcel.sales_amount)).scalar() or 0

    # Quick Stats Grid
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{total_cities}</div>
            <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Active Markets</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{total_parcels:,}</div>
            <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Total Properties</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{total_targets}</div>
            <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Target Investors</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        # Format portfolio value
        if total_value >= 1_000_000_000:
            value_display = f"${total_value / 1_000_000_000:.1f}B"
        elif total_value >= 1_000_000:
            value_display = f"${total_value / 1_000_000:.1f}M"
        elif total_value >= 1_000:
            value_display = f"${total_value / 1_000:.1f}K"
        else:
            value_display = f"${total_value:.0f}"
            
        st.markdown(f"""
        <div class="glass-card" style="text-align: center;">
            <div style="font-size: 2.25rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{value_display}</div>
            <div style="font-size: 0.6875rem; color: var(--text-disabled); text-transform: uppercase; letter-spacing: 0.1em; margin-top: 0.5rem; font-weight: 600;">Portfolio Value</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

except Exception as e:
    st.error(f"Error loading statistics: {str(e)}")
    if st.session_state.get('debug_mode', False):
        st.exception(e)

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
    st.switch_page("pages/3_Upload_Data.py")

# ====================================
# Markets Grid Section
# ====================================

st.markdown("<h2 style='font-size: 1.75rem; font-weight: 700; color: var(--text-primary); margin: 3rem 0 1.75rem 0;'>Your Markets</h2>", unsafe_allow_html=True)

# Fetch all active cities
try:
    with db_manager.get_session() as session:
        cities_query = session.query(City).filter(City.is_active == True).all()
        # Convert to dictionaries to avoid session detachment issues
        cities = [
            {
                'city_id': city.city_id,
                'city_name': city.city_name,
                'display_name': city.display_name,
                'state': city.state
            }
            for city in cities_query
        ]

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
                        city_parcels = session.query(Parcel).filter(Parcel.city_id == city['city_id']).count()
                        city_targets = session.query(TargetOwner).filter(
                            TargetOwner.city_id == city['city_id'],
                            TargetOwner.is_active == True
                        ).count()
                        city_value = session.query(func.sum(Parcel.sales_amount)).filter(
                            Parcel.city_id == city['city_id']
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
                                <h3 style="font-size: 1.75rem; color: #f4f4f5; margin-bottom: 0.5rem; font-weight: 600; text-transform: none; letter-spacing: normal;">{city['display_name'].split(',')[0]}</h3>
                                <p style="color: #71717a; font-size: 0.875rem; margin-bottom: 1rem;">{city['display_name']}</p>
                                <span style="display: inline-block; padding: 0.375rem 0.875rem; border-radius: 1.25rem; font-size: 0.75rem; font-weight: 600; background: rgba(16, 185, 129, 0.2); color: #6ee7b7; border: 1px solid rgba(16, 185, 129, 0.3);">Active</span>
                            </div>
                        </div>
                        <div style="display: flex; justify-content: space-between; margin-top: 1.5rem; padding-top: 1.5rem; border-top: 1px solid rgba(255, 255, 255, 0.08);">
                            <div style="text-align: center;">
                                <div style="font-size: 1.625rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{city_parcels:,}</div>
                                <div style="font-size: 0.6875rem; color: #71717a; text-transform: uppercase; margin-top: 0.375rem; letter-spacing: 0.05em; font-weight: 600;">Properties</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.625rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{city_targets}</div>
                                <div style="font-size: 0.6875rem; color: #71717a; text-transform: uppercase; margin-top: 0.375rem; letter-spacing: 0.05em; font-weight: 600;">Investors</div>
                            </div>
                            <div style="text-align: center;">
                                <div style="font-size: 1.625rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{value_str}</div>
                                <div style="font-size: 0.6875rem; color: #71717a; text-transform: uppercase; margin-top: 0.375rem; letter-spacing: 0.05em; font-weight: 600;">Value</div>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # View Analysis button
                    if st.button(f"View Analysis →", key=f"view_{city['city_id']}", type="primary", use_container_width=True):
                        st.session_state.selected_city_id = city['city_id']
                        st.switch_page("pages/2_Map_Viewer.py")

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
                st.switch_page("pages/3_Upload_Data.py")

    else:
        # No cities yet - show onboarding (Empty State)
        st.markdown("""
        <div style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 4rem; margin-bottom: 1.5rem; opacity: 0.3;">📊</div>
            <h2 style="color: var(--text-primary); margin-bottom: 1rem;">No Markets Added Yet</h2>
            <p style="color: var(--text-muted); margin-bottom: 2rem;">Get started by uploading your first market's data</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("📤 Upload First Market", type="primary"):
            st.switch_page("pages/3_Upload_Data.py")

except Exception as e:
    st.error(f"Error loading markets: {str(e)}")
    if st.session_state.get('debug_mode', False):
        st.exception(e)

