"""
Settings Page - Application Configuration
Manage cities, view database statistics, and import history
"""

import streamlit as st
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import db_manager
from database.models import City, Parcel, TargetOwner, ImportHistory
from sqlalchemy import func, desc

# Page config
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
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
st.session_state.current_page = "Settings"

# Import and render navigation
try:
    from ui.components.navigation import render_navigation
    render_navigation()
except Exception as e:
    st.error(f"Navigation error: {str(e)}")

# ====================================
# Header Section
# ====================================

st.markdown("<h1>Settings</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 1.125rem; color: var(--text-muted); margin-bottom: 2rem;'>"
    "Manage cities, view database statistics, and monitor import history"
    "</p>",
    unsafe_allow_html=True
)

# ====================================
# Two-Column Layout
# ====================================

col_left, col_right = st.columns([1, 1])

# ====================================
# LEFT COLUMN: City Management
# ====================================

with col_left:
    # ====================================
    # City Management Section
    # ====================================

    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1rem;'>City Management</h3>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    # Get all cities from database
    try:
        with db_manager.get_session() as session:
            cities_query = session.query(City).all()
            # Convert to dictionaries to avoid session detachment issues
            cities = [{
                'city_id': city.city_id,
                'city_name': city.city_name,
                'display_name': city.display_name,
                'state': city.state,
                'center_lat': city.center_lat,
                'center_lng': city.center_lng,
                'zoom_level': city.zoom_level
            } for city in cities_query]

        if cities:
            # City selector dropdown
            city_names = [f"{city['display_name']} ({city['city_name']})" for city in cities]
            selected_city_idx = st.selectbox(
                "Select City",
                range(len(cities)),
                format_func=lambda i: city_names[i],
                key="settings_city_selector"
            )

            selected_city = cities[selected_city_idx]

            # Display city information
            st.markdown(f"""
            <div style="background: rgba(255, 255, 255, 0.03); padding: 1rem; border-radius: 0.5rem; margin: 1rem 0; border: 1px solid rgba(255, 255, 255, 0.08);">
                <div style="font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem;">City Information</div>
                <div style="font-size: 0.875rem; margin-bottom: 0.25rem;"><strong>Name:</strong> {selected_city['city_name']}</div>
                <div style="font-size: 0.875rem; margin-bottom: 0.25rem;"><strong>Display Name:</strong> {selected_city['display_name']}</div>
                <div style="font-size: 0.875rem; margin-bottom: 0.25rem;"><strong>State:</strong> {selected_city['state']}</div>
                <div style="font-size: 0.875rem; margin-bottom: 0.25rem;"><strong>Coordinates:</strong> {selected_city['center_lat']}, {selected_city['center_lng']}</div>
                <div style="font-size: 0.875rem;"><strong>Zoom Level:</strong> {selected_city['zoom_level']}</div>
            </div>
            """, unsafe_allow_html=True)

            # Action buttons
            st.markdown("<div style='margin-top: 1.5rem;'>", unsafe_allow_html=True)

            col1, col2 = st.columns(2)

            with col1:
                if st.button("🔄 Re-import Data", use_container_width=True, key="reimport_btn"):
                    st.info("Re-import functionality coming soon!")

            with col2:
                if st.button("🗑️ Delete City", use_container_width=True, type="secondary", key="delete_btn"):
                    # Confirmation dialog
                    if 'confirm_delete' not in st.session_state:
                        st.session_state.confirm_delete = False

                    if not st.session_state.confirm_delete:
                        st.session_state.confirm_delete = True
                        st.warning(f"⚠️ Are you sure you want to delete {selected_city['display_name']}? This will remove all associated parcels and target owners.")
                        st.rerun()

            # Delete confirmation
            if st.session_state.get('confirm_delete', False):
                st.markdown(
                    "<div style='background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 0.5rem; padding: 1rem; margin-top: 1rem;'>",
                    unsafe_allow_html=True
                )
                st.markdown(
                    f"<p style='font-size: 0.875rem; margin-bottom: 0.75rem;'>⚠️ Confirm deletion of <strong>{selected_city['display_name']}</strong>?</p>",
                    unsafe_allow_html=True
                )

                col_confirm1, col_confirm2 = st.columns(2)

                with col_confirm1:
                    if st.button("✅ Yes, Delete", use_container_width=True, type="primary", key="confirm_delete_btn"):
                        try:
                            # Delete city and all associated data
                            with db_manager.get_session() as delete_session:
                                delete_session.query(Parcel).filter(Parcel.city_id == selected_city['city_id']).delete()
                                delete_session.query(TargetOwner).filter(TargetOwner.city_id == selected_city['city_id']).delete()
                                delete_session.query(ImportHistory).filter(ImportHistory.city_id == selected_city['city_id']).delete()
                                city_to_delete = delete_session.query(City).filter(City.city_id == selected_city['city_id']).first()
                                if city_to_delete:
                                    delete_session.delete(city_to_delete)

                            st.success(f"✅ Successfully deleted {selected_city['display_name']} and all associated data")
                            st.session_state.confirm_delete = False
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ Error deleting city: {str(e)}")

                with col_confirm2:
                    if st.button("❌ Cancel", use_container_width=True, key="cancel_delete_btn"):
                        st.session_state.confirm_delete = False
                        st.rerun()

                st.markdown("</div>", unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.info("📊 No cities found. Upload data to get started.")

    except Exception as e:
        st.error(f"❌ Error loading cities: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

    # ====================================
    # Database Statistics Section
    # ====================================

    st.markdown("<h3 style='font-size: 1.25rem; margin-top: 2rem; margin-bottom: 1rem;'>Database Statistics</h3>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    # Query database statistics
    try:
        with db_manager.get_session() as session:
            cities_count = session.query(func.count(City.city_id)).scalar()
            parcels_count = session.query(func.count(Parcel.parcel_id)).scalar()
            targets_count = session.query(func.count(TargetOwner.target_id)).scalar()
            imports_count = session.query(func.count(ImportHistory.import_id)).scalar()

        # Display statistics in table format
        st.markdown("""
        <div style="background: rgba(255, 255, 255, 0.03); border-radius: 0.5rem; overflow: hidden; border: 1px solid rgba(255, 255, 255, 0.08);">
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="background: rgba(255, 255, 255, 0.05);">
                        <th style="padding: 0.75rem; text-align: left; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">Table</th>
                        <th style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">Records</th>
                    </tr>
                </thead>
                <tbody>
                    <tr>
                        <td style="padding: 0.75rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">Cities</td>
                        <td style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">{:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.75rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">Parcels</td>
                        <td style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">{:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.75rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">Target Owners</td>
                        <td style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">{:,}</td>
                    </tr>
                    <tr>
                        <td style="padding: 0.75rem; font-size: 0.875rem;">Import Records</td>
                        <td style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600;">{:,}</td>
                    </tr>
                </tbody>
            </table>
        </div>
        """.format(cities_count, parcels_count, targets_count, imports_count), unsafe_allow_html=True)

    except Exception as e:
        st.error(f"❌ Error loading database statistics: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ====================================
# RIGHT COLUMN: Import History
# ====================================

with col_right:
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1rem;'>Import History</h3>", unsafe_allow_html=True)

    st.markdown('<div class="glass-card">', unsafe_allow_html=True)

    # Query import history
    try:
        with db_manager.get_session() as session:
            # Get recent imports (last 20)
            import_records = (
                session.query(ImportHistory, City.display_name)
                .join(City, ImportHistory.city_id == City.city_id)
                .order_by(desc(ImportHistory.created_at))
                .limit(20)
                .all()
            )
            
            # Convert to dictionaries BEFORE session closes (avoid "not bound to a Session" error)
            imports = [{
                'import_date': record[0].created_at.strftime("%Y-%m-%d %H:%M"),
                'city_name': record[1],
                'status': record[0].status or 'pending',
                'parcels_count': record[0].records_imported or 0,  # Use records_imported instead
                'target_owners_count': 0  # Placeholder - not tracked yet
            } for record in import_records]

        if imports:
            # Display import history in table format
            st.markdown(
                "<div style='max-height: 600px; overflow-y: auto; background: rgba(255, 255, 255, 0.03); border-radius: 0.5rem; border: 1px solid rgba(255, 255, 255, 0.08);'>",
                unsafe_allow_html=True
            )

            st.markdown("""
            <table style="width: 100%; border-collapse: collapse;">
                <thead style="position: sticky; top: 0; background: rgba(15, 15, 30, 0.95); z-index: 1;">
                    <tr style="background: rgba(255, 255, 255, 0.05);">
                        <th style="padding: 0.75rem; text-align: left; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">Date</th>
                        <th style="padding: 0.75rem; text-align: left; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">City</th>
                        <th style="padding: 0.75rem; text-align: left; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">Status</th>
                        <th style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">Parcels</th>
                        <th style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1);">Owners</th>
                    </tr>
                </thead>
                <tbody>
            """, unsafe_allow_html=True)

            for import_record in imports:
                # Extract data from dictionary
                date_str = import_record['import_date']
                city_name = import_record['city_name']
                status = import_record['status']
                parcels_count = import_record['parcels_count']
                target_owners_count = import_record['target_owners_count']

                # Status badge color
                if status == "success":
                    status_color = "#10b981"  # green
                    status_text = "✓ Success"
                elif status == "failed":
                    status_color = "#ef4444"  # red
                    status_text = "✗ Failed"
                else:
                    status_color = "#f59e0b"  # orange
                    status_text = "⚠ Partial"

                st.markdown(f"""
                <tr>
                    <td style="padding: 0.75rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">{date_str}</td>
                    <td style="padding: 0.75rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">{city_name}</td>
                    <td style="padding: 0.75rem; font-size: 0.875rem; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">
                        <span style="background: {status_color}20; color: {status_color}; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.75rem; font-weight: 600;">
                            {status_text}
                        </span>
                    </td>
                    <td style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">{parcels_count:,}</td>
                    <td style="padding: 0.75rem; text-align: right; font-size: 0.875rem; font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.05);">{target_owners_count:,}</td>
                </tr>
                """, unsafe_allow_html=True)

            st.markdown("""
                </tbody>
            </table>
            """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

        else:
            st.info("📊 No import history found. Upload data to get started.")

    except Exception as e:
        st.error(f"❌ Error loading import history: {str(e)}")

    st.markdown('</div>', unsafe_allow_html=True)

# ====================================
# Footer
# ====================================

st.markdown("<div style='margin-top: 3rem; padding-top: 2rem; border-top: 1px solid rgba(255, 255, 255, 0.1);'>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 0.875rem; color: var(--text-muted); text-align: center;'>"
    "Green Sea Map - Portfolio Analytics Platform"
    "</p>",
    unsafe_allow_html=True
)
st.markdown("</div>", unsafe_allow_html=True)
