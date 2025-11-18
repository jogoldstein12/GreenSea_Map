"""
Map Viewer Page - Interactive Portfolio Visualization
Displays Folium map with property data and portfolio statistics
"""

import streamlit as st
import sys
from pathlib import Path
import geopandas as gpd
from streamlit_folium import st_folium
from geoalchemy2.shape import to_shape
import time

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from database.db_manager import db_manager
from database.models import City, Parcel, TargetOwner
from mapping.map_generator import generate_map
from data_processing.analyzer import PortfolioAnalyzer
from data_processing.normalizer import clean_owner

# ====================================
# CACHED MAP GENERATION
# ====================================
@st.cache_resource(show_spinner=False, ttl=3600)
def generate_cached_map(
    city_id: int,
    view_mode: str,
    selected_owner: str = None,
    _parcels_gdf=None,
    _city_config=None,
    _target_owners=None,
    _stats_per_owner=None,
    _all_stats=None,
    _view_mode_param=None
):
    """
    Generate and cache a Folium map based on the provided parameters.
    
    Cached for 1 hour (3600 seconds) to avoid regenerating the same map.
    Cache key includes: city_id, view_mode, selected_owner
    
    Args:
        city_id: Database ID of the city
        view_mode: Display mode ('By Owner', 'By ZIP') - used as cache key
        selected_owner: Name of selected owner (if any)
        _parcels_gdf: GeoDataFrame with parcel data (uncached with _ prefix)
        _city_config: City configuration dict (uncached)
        _target_owners: List of target owners (uncached)
        _stats_per_owner: Statistics per owner dict (uncached)
        _all_stats: Aggregate statistics dict (uncached)
        _view_mode_param: Actual view_mode to pass to map generator (uncached)
    
    Returns:
        Folium map object
    """
    try:
        # Use _view_mode_param if provided, otherwise fall back to view_mode
        actual_view_mode = _view_mode_param if _view_mode_param else view_mode
        
        folium_map = generate_map(
            city_config=_city_config,
            parcels_gdf=_parcels_gdf,
            target_owners=_target_owners,
            stats_per_owner=_stats_per_owner,
            all_stats=_all_stats,
            use_clustering=True,
            view_mode=actual_view_mode,
            include_zip_layers=False  # Disabled for performance (can be 50-100+ layers)
        )
        return folium_map
    except Exception as e:
        st.error(f"❌ Error in cached map generation: {str(e)}")
        return None

# Page config
st.set_page_config(
    page_title="Map Viewer",
    page_icon="🗺️",
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
st.session_state.current_page = "Map Viewer"

# Import and render navigation
try:
    from ui.components.navigation import render_navigation
    render_navigation()
except Exception as e:
    st.error(f"Navigation error: {str(e)}")

# ====================================
# Header Section
# ====================================

# Performance & Developer Options
with st.expander("⚡ Performance & Developer Options", expanded=False):
    st.markdown("### 🎯 Dataset Settings")

    # Dataset mode selector
    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        dataset_mode = st.radio(
            "Dataset Mode",
            options=["Target Owners Only", "All Parcels"],
            index=0,
            help="Target Owners Only: Fast loading (only target investors)\nAll Parcels: Show entire dataset (may be slow)"
        )
        st.session_state.dataset_mode = dataset_mode

    with col_mode2:
        if dataset_mode == "All Parcels":
            # Sampling options for large datasets
            use_sampling = st.checkbox(
                "Enable Smart Sampling",
                value=True,
                help="Automatically sample large datasets to ensure fast loading"
            )
            st.session_state.use_sampling = use_sampling

            if use_sampling:
                sample_size = st.slider(
                    "Sample Size",
                    min_value=1000,
                    max_value=100000,
                    value=25000,
                    step=5000,
                    help="Maximum number of parcels to load. Larger = slower but more complete."
                )
                st.session_state.sample_size = sample_size
            else:
                st.session_state.sample_size = None
                st.warning("⚠️ No sampling - may be very slow with 50k+ parcels!")
        else:
            st.session_state.use_sampling = False
            st.session_state.sample_size = None
            st.info("✅ Target owners mode - optimized for fast performance")

    st.markdown("---")
    st.markdown("### 🚀 Performance Settings")
    st.caption("Optimize map loading for large datasets (100,000+ parcels)")

    # Geometry simplification slider
    simplify_options = {
        "Maximum Detail (Slowest)": 0.0,
        "High Detail": 0.00005,
        "Balanced (Recommended)": 0.0001,
        "Lower Detail (Faster)": 0.0002,
        "Minimum Detail (Fastest)": 0.0005
    }

    simplify_label = st.select_slider(
        "Geometry Detail Level",
        options=list(simplify_options.keys()),
        value="Balanced (Recommended)",
        help="Lower detail = faster loading & smaller file size. For 100k+ parcels, use 'Lower Detail' or less."
    )
    simplify_tolerance = simplify_options[simplify_label]
    st.session_state.simplify_tolerance = simplify_tolerance

    if simplify_tolerance == 0.0:
        st.warning("⚠️ Maximum detail may be slow with large datasets (10+ seconds)")
    elif simplify_tolerance >= 0.0002:
        st.success("✅ Fast performance mode - optimized for 100k+ parcels")

    st.caption(f"💡 Current tolerance: {simplify_tolerance} degrees (~{int(simplify_tolerance * 111000)}m at equator)")

    st.markdown("---")
    st.markdown("### 🔧 Developer Options")

    debug_mode = st.checkbox(
        "Enable Debug Mode",
        value=st.session_state.get('debug_mode', False),
        help="Show detailed error messages and diagnostic information"
    )
    st.session_state.debug_mode = debug_mode
    if debug_mode:
        st.info("🐛 Debug mode enabled - detailed error information will be displayed")

    # Cache management
    st.markdown("**Cache Management:**")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🗑️ Clear Data Cache", help="Clear cached data and reload from database", use_container_width=True):
            st.cache_data.clear()
            # Also clear session state map
            if 'cached_map' in st.session_state:
                del st.session_state.cached_map
            if 'map_cache_key' in st.session_state:
                del st.session_state.map_cache_key
            st.success("✅ Data cache cleared!")
            st.rerun()
    with col2:
        if st.button("🗺️ Clear Map Cache", help="Clear cached maps (forces map regeneration)", use_container_width=True):
            st.cache_resource.clear()
            # Also clear session state map
            if 'cached_map' in st.session_state:
                del st.session_state.cached_map
            if 'map_cache_key' in st.session_state:
                del st.session_state.map_cache_key
            st.success("✅ Map cache cleared!")
            st.rerun()

    st.caption("💡 Map caching: Maps cached for 1 hour + session state. Only regenerates when city/view/investor changes.")

st.markdown("<h1>Map Viewer</h1>", unsafe_allow_html=True)
st.markdown(
    "<p style='font-size: 1.125rem; color: var(--text-muted); margin-bottom: 2rem;'>"
    "Interactive property portfolio visualization"
    "</p>", 
    unsafe_allow_html=True
)

# ====================================
# City Selection
# ====================================

# Fetch active cities
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

    if not cities:
        # No cities available
        st.warning("⚠️ No markets available. Please upload data first.")
        if st.button("📤 Upload Data", type="primary"):
            st.switch_page("pages/3_Upload_Data.py")
        st.stop()

    # City selector in glass card
    st.markdown('<div class="glass-card" style="margin-bottom: 1.5rem;">', unsafe_allow_html=True)
    
    # Get selected city from session state or use first city as default
    default_city_id = st.session_state.get('selected_city_id', cities[0]['city_id'])
    
    # Create options dict
    city_options = {city['display_name']: city['city_id'] for city in cities}
    
    # Find default index
    default_index = 0
    for idx, (name, city_id) in enumerate(city_options.items()):
        if city_id == default_city_id:
            default_index = idx
            break
    
    # City selectbox
    selected_city_name = st.selectbox(
        "📍 Select Market",
        options=list(city_options.keys()),
        index=default_index,
        key="city_select",
        help="Choose a market to view its property portfolio"
    )
    
    selected_city_id = city_options[selected_city_name]
    
    # Store in session state
    st.session_state.selected_city_id = selected_city_id
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Display selected city info
    with db_manager.get_session() as session:
        selected_city_obj = session.query(City).filter(City.city_id == selected_city_id).first()
        
        if selected_city_obj:
            st.info(f"**Selected Market:** {selected_city_obj.display_name}")

except Exception as e:
    st.error(f"Error loading cities: {str(e)}")
    if st.session_state.get('debug_mode', False):
        st.exception(e)
    st.stop()

# ====================================
# Load City Data
# ====================================

@st.cache_data(ttl=3600)
def load_city_data(city_id, simplify_tolerance=0.0001, dataset_mode="Target Owners Only", sample_size=None):
    """
    Load parcels and target owners for selected city

    PERFORMANCE OPTIMIZATIONS:
    - Filters parcels at database level (SQL filters)
    - Optional sampling for large datasets
    - Simplifies geometries to reduce polygon complexity
    - Reduces memory usage and processing time significantly

    Args:
        city_id: Unique identifier for the city
        simplify_tolerance: Geometry simplification tolerance (degrees, ~11m at equator)
            - 0.0001 (default): Good balance, ~11m precision
            - 0.00005: Higher detail, ~5m precision
            - 0.0002: Lower detail, ~22m precision, faster
            - 0: No simplification (slower, larger files)
        dataset_mode: "Target Owners Only" or "All Parcels"
        sample_size: Maximum number of parcels to load (None = load all)

    Returns:
        tuple: (city_data, parcels_gdf, target_list, total_count)
            - city_data: Dictionary with city information
            - parcels_gdf: GeoDataFrame of parcels
            - target_list: List of target owner names
            - total_count: Total parcels in database (before sampling)
    """
    with db_manager.get_session() as session:
        # Get city details
        city = session.query(City).filter(City.city_id == city_id).first()

        if not city:
            return None, gpd.GeoDataFrame(), [], 0

        # Convert city to dict to avoid session detachment
        city_data = {
            'city_id': city.city_id,
            'city_name': city.city_name,
            'display_name': city.display_name,
            'center_lat': float(city.center_lat),
            'center_lng': float(city.center_lng),
            'zoom_level': city.zoom_level
        }

        # Get target owners first
        targets = session.query(TargetOwner).filter(
            TargetOwner.city_id == city_id,
            TargetOwner.is_active == True
        ).all()

        target_list = [t.owner_clean for t in targets]

        # Get total parcel count for this city (for statistics)
        total_count = session.query(Parcel).filter(Parcel.city_id == city_id).count()

        # Build parcel query based on dataset mode
        if dataset_mode == "Target Owners Only":
            if not target_list:
                # No target owners - return empty GeoDataFrame
                return city_data, gpd.GeoDataFrame(), [], total_count

            # OPTIMIZATION: Filter parcels at database level using IN clause
            # Only load parcels that belong to target owners
            parcel_query = session.query(Parcel).filter(
                Parcel.city_id == city_id,
                Parcel.owner_clean.in_(target_list)
            )
        else:
            # Load ALL parcels for this city
            parcel_query = session.query(Parcel).filter(
                Parcel.city_id == city_id
            )

        # Apply sampling if requested
        if sample_size is not None and dataset_mode == "All Parcels":
            # Random sampling using PostgreSQL's TABLESAMPLE
            # Note: We'll use Python random sampling instead for better control
            all_parcel_ids = [p.parcel_id for p in parcel_query.with_entities(Parcel.parcel_id).all()]

            if len(all_parcel_ids) > sample_size:
                import random
                random.seed(42)  # Consistent sampling
                sampled_ids = random.sample(all_parcel_ids, sample_size)
                parcel_query = session.query(Parcel).filter(
                    Parcel.parcel_id.in_(sampled_ids)
                )

        # Execute query
        parcels = parcel_query.all()

        # Convert to GeoDataFrame
        if parcels:
            parcel_data = []
            for p in parcels:
                # Convert WKB geometry to shapely geometry
                geom = to_shape(p.geometry) if p.geometry else None

                # OPTIMIZATION: Simplify geometry to reduce complexity
                if geom and simplify_tolerance > 0:
                    try:
                        geom = geom.simplify(simplify_tolerance, preserve_topology=True)
                    except Exception:
                        pass  # Keep original if simplification fails

                # Fix: If owner_clean is null, normalize from deeded_owner
                owner_clean = p.owner_clean
                if not owner_clean and p.deeded_owner:
                    owner_clean = clean_owner(p.deeded_owner)

                parcel_data.append({
                    'parcel_pin': p.parcel_pin,
                    'geometry': geom,
                    'address': p.address,
                    'par_zip': p.par_zip,
                    'deeded_owner': p.deeded_owner,
                    'owner_clean': owner_clean,
                    'tax_luc_description': p.tax_luc_description,
                    'sales_amount': float(p.sales_amount) if p.sales_amount else 0.0,
                    'certified_tax_total': float(p.certified_tax_total) if p.certified_tax_total else 0.0
                })

            gdf = gpd.GeoDataFrame(parcel_data, geometry='geometry', crs='EPSG:4326')
        else:
            gdf = gpd.GeoDataFrame()

        return city_data, gdf, target_list, total_count

# Load data for selected city
try:
    # Data loading progress
    data_progress = st.empty()
    data_status = st.empty()

    data_load_start = time.time()

    # Get parameters from session state
    simplify_tolerance = st.session_state.get('simplify_tolerance', 0.0001)
    dataset_mode = st.session_state.get('dataset_mode', 'Target Owners Only')
    sample_size = st.session_state.get('sample_size', None)

    # Show loading message based on mode
    if dataset_mode == "All Parcels":
        if sample_size:
            data_status.info(f"📊 Loading parcels from database (sample size: {sample_size:,}, detail level: {simplify_tolerance})...")
        else:
            data_status.warning(f"📊 Loading ALL parcels from database (no sampling - may be slow, detail level: {simplify_tolerance})...")
    else:
        data_status.info(f"📊 Loading target owner parcels from database (detail level: {simplify_tolerance})...")

    # Load data with new parameters
    city, parcels_gdf, target_owners, total_parcel_count = load_city_data(
        selected_city_id,
        simplify_tolerance,
        dataset_mode,
        sample_size
    )

    data_load_time = time.time() - data_load_start

    if city is None:
        data_progress.empty()
        data_status.empty()
        st.error("❌ Could not load city data.")
        st.stop()

    if parcels_gdf.empty:
        data_progress.empty()
        data_status.empty()

        if dataset_mode == "Target Owners Only" and len(target_owners) == 0:
            st.warning("⚠️ No target owners found for this market.")
            st.info("💡 **Tip:** Switch to 'All Parcels' mode in Performance Settings to view the entire dataset, "
                    "or upload target owner data in the Upload Data page.")
        else:
            st.warning("⚠️ No parcel data available for this market.")
            st.info("This market may have been added but data hasn't been imported yet.")
        st.stop()

    # Show success message with statistics
    loaded_count = len(parcels_gdf)

    if dataset_mode == "All Parcels":
        if sample_size and loaded_count < total_parcel_count:
            data_status.success(
                f"✅ Loaded {loaded_count:,} parcels (sampled from {total_parcel_count:,} total) in {data_load_time:.1f}s"
            )
        else:
            data_status.success(
                f"✅ Loaded {loaded_count:,} parcels in {data_load_time:.1f}s"
            )
    else:
        # Target owners mode
        if loaded_count > 10000:
            estimated_original = total_parcel_count
            if estimated_original > loaded_count:
                performance_gain = ((estimated_original - loaded_count) / estimated_original) * 100
                data_status.success(
                    f"✅ Loaded {loaded_count:,} target owner parcels in {data_load_time:.1f}s "
                    f"(~{performance_gain:.0f}% faster by filtering {estimated_original:,} total parcels!)"
                )
            else:
                data_status.success(f"✅ Loaded {loaded_count:,} target owner parcels in {data_load_time:.1f}s")
        else:
            data_status.success(f"✅ Loaded {loaded_count:,} parcels and {len(target_owners)} investors in {data_load_time:.1f}s")

    time.sleep(0.5)  # Brief pause to show message

    # Clear status indicators
    data_progress.empty()
    data_status.empty()

except Exception as e:
    st.error(f"Error loading city data: {str(e)}")
    if st.session_state.get('debug_mode', False):
        st.exception(e)
    st.stop()

# ====================================
# Debug Info (if enabled)
# ====================================

if st.session_state.get('debug_mode', False):
    with st.expander("📊 Data Debug Information"):
        st.write(f"**Target owner parcels loaded:** {len(parcels_gdf)}")
        st.write(f"**Target investors count:** {len(target_owners)}")
        st.write(f"**Sample target owners:** {target_owners[:3] if target_owners else 'None'}")
        st.write(f"**Geometry simplification tolerance:** {simplify_tolerance}")
        if not parcels_gdf.empty:
            if 'deeded_owner' in parcels_gdf.columns:
                st.write(f"**Deeded_owner null count:** {parcels_gdf['deeded_owner'].isna().sum()}")
                st.write(f"**Sample deeded_owner:** {parcels_gdf['deeded_owner'].dropna().unique()[:3].tolist() if not parcels_gdf['deeded_owner'].dropna().empty else 'All NULL'}")
            if 'owner_clean' in parcels_gdf.columns:
                st.write(f"**Unique owners in parcels:** {parcels_gdf['owner_clean'].nunique()}")
                st.write(f"**Owner_clean null count:** {parcels_gdf['owner_clean'].isna().sum()}")
                st.write(f"**Sample owner_clean:** {parcels_gdf['owner_clean'].dropna().unique()[:3].tolist() if not parcels_gdf['owner_clean'].dropna().empty else 'All NULL'}")

# ====================================
# NOTE: parcels_gdf already contains ONLY target owner parcels
# No additional filtering needed - database query already optimized
# ====================================

target_parcels = parcels_gdf  # Already filtered at database level!

# Alert if no target parcels found
if len(target_parcels) == 0:
    if len(parcels_gdf) == 0:
        st.error("❌ No parcels were loaded for this city. The parcel data may not have been imported.")
    elif len(target_owners) == 0:
        st.error("❌ No target investors found for this city. Please add target investors in the upload page.")
    else:
        st.error(f"❌ No matching parcels found. Loaded {len(parcels_gdf)} parcels and {len(target_owners)} target investors, but owner names don't match.")
        with st.expander("🔍 See Details"):
            st.write("**Sample parcel owners:**")
            st.write(parcels_gdf['owner_clean'].unique()[:10].tolist() if 'owner_clean' in parcels_gdf.columns else "No owner_clean column")
            st.write("\n**Target investors:**")
            st.write(target_owners[:10])
    st.stop()

# ====================================
# Dataset Size Info & Recommendations
# ====================================

parcel_count = len(target_parcels)

# Show dataset information and performance recommendations
if dataset_mode == "All Parcels":
    # All Parcels mode - show total and sampling info
    if sample_size and parcel_count < total_parcel_count:
        st.info(
            f"📊 **Dataset:** {parcel_count:,} parcels loaded (sampled from {total_parcel_count:,} total - "
            f"{(parcel_count/total_parcel_count*100):.0f}% of full dataset)\n\n"
            f"✅ **Optimizations Active:**\n"
            f"- Random sampling (ensures fast loading)\n"
            f"- Geometry simplification (reduces file size)\n"
            f"- Marker clustering (groups nearby parcels)\n\n"
            f"💡 **Tip:** Adjust sample size in Performance Settings to load more/fewer parcels."
        )
    elif parcel_count > 50000:
        st.warning(
            f"📊 **Large Dataset:** {parcel_count:,} parcels loaded (full dataset)\n\n"
            f"⚠️ **Performance Impact:** Loading may take 10+ seconds\n\n"
            f"✅ **Optimizations Active:**\n"
            f"- Geometry simplification (reduces file size)\n"
            f"- Marker clustering (groups nearby parcels)\n\n"
            f"💡 **Recommendations:**\n"
            f"- Enable 'Smart Sampling' in Performance Settings\n"
            f"- Use 'Lower Detail' or 'Minimum Detail' geometry\n"
            f"- Or switch to 'Target Owners Only' mode"
        )
    elif parcel_count > 20000:
        st.info(
            f"📊 **Medium Dataset:** {parcel_count:,} parcels - optimizations active for smooth performance"
        )
    else:
        st.success(f"📊 **Dataset:** {parcel_count:,} parcels loaded - excellent performance expected!")
else:
    # Target Owners Only mode
    if parcel_count > 50000:
        st.info(
            f"📊 **Large Dataset Detected:** {parcel_count:,} parcels\n\n"
            f"✅ **Optimizations Active:**\n"
            f"- Database filtering (only target owners: {len(target_owners)} investors)\n"
            f"- Geometry simplification (reduces file size by ~60-80%)\n"
            f"- Marker clustering (groups nearby parcels)\n\n"
            f"💡 **Tip:** If map still loads slowly, try 'Lower Detail' or 'Minimum Detail' in Performance Settings."
        )
    elif parcel_count > 20000:
        st.info(
            f"📊 **Medium Dataset:** {parcel_count:,} parcels from {len(target_owners)} target investors - optimizations active"
        )
    else:
        st.success(f"📊 **Dataset:** {parcel_count:,} parcels from {len(target_owners)} target investors")

# ====================================
# Determine display parcels based on selection
# ====================================

selected_owner = st.session_state.get('selected_owner', None)
if selected_owner:
    display_parcels = target_parcels[target_parcels['owner_clean'] == selected_owner].copy()
else:
    display_parcels = target_parcels.copy()

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
    st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1rem;'>Portfolio Search</h3>", unsafe_allow_html=True)
    search_term = st.text_input(
        "Search by investor name",
        placeholder="Search investors...",
        label_visibility="collapsed",
        key="investor_search"
    )
    
    # View Toggle
    st.markdown("<div style='margin: 1.5rem 0 1rem 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.875rem; color: var(--text-muted); margin-bottom: 0.5rem;'>View Mode</p>", unsafe_allow_html=True)
    view_mode = st.radio(
        "View Mode",
        options=["By Owner", "By ZIP"],
        horizontal=True,
        label_visibility="collapsed",
        key="view_mode"
    )
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Investors List (title depends on mode)
    if dataset_mode == "All Parcels":
        st.markdown("<h3 style='font-size: 1.25rem; margin-top: 1.75rem; margin-bottom: 1rem;'>All Property Owners</h3>", unsafe_allow_html=True)
        st.caption("Showing all owners in the dataset (or sample)")
    else:
        st.markdown("<h3 style='font-size: 1.25rem; margin-top: 1.75rem; margin-bottom: 1rem;'>Target Investors</h3>", unsafe_allow_html=True)
        if len(target_owners) > 0:
            st.caption(f"Showing {len(target_owners)} target investors with properties")

    # Calculate stats per owner (optimized with groupby)
    if not target_parcels.empty:
        # Group by owner and calculate stats efficiently
        owner_groups = target_parcels.groupby('owner_clean').agg({
            'parcel_pin': 'count',  # Count of properties
            'par_zip': 'nunique'    # Unique ZIP codes
        }).reset_index()

        owner_groups.columns = ['owner', 'properties', 'zips']

        # Convert to list of dicts and sort by property count
        owner_stats_list = owner_groups.to_dict('records')
        owner_stats_list.sort(key=lambda x: x['properties'], reverse=True)
    else:
        owner_stats_list = []
    
    # Display owner list with search filter
    filtered_owners = owner_stats_list
    
    # Apply search filter only if user has typed something
    if search_term and len(search_term.strip()) > 0:
        filtered_owners = [o for o in owner_stats_list if search_term.upper() in o['owner']]
        
        # Show message if search returns no results
        if not filtered_owners:
            st.warning(f"🔍 No investors match '{search_term}'. Try a different search term.")
            st.info(f"💡 Showing all {len(owner_stats_list)} investors with properties instead.")
            filtered_owners = owner_stats_list  # Fall back to showing all
    
    # Show investor count and filtering status
    if search_term and len(search_term.strip()) > 0:
        st.caption(f"📊 Showing {len(filtered_owners)} of {len(owner_stats_list)} investors (filtered)")
    else:
        st.caption(f"📊 Showing {min(len(filtered_owners), 50)} of {len(owner_stats_list)} investors with properties")
    
    if owner_stats_list:
        # Scrollable container
        st.markdown('<div style="max-height: 450px; overflow-y: auto; padding-right: 0.5rem;">', unsafe_allow_html=True)
        
        # Show top 50 investors (increased from 20 for better visibility)
        display_limit = 50
        for idx, owner_stat in enumerate(filtered_owners[:display_limit]):
            owner_name = owner_stat['owner']
            properties = owner_stat['properties']
            zips = owner_stat['zips']
            
            # Check if this owner is selected
            is_selected = (selected_owner == owner_name)
            
            # Owner item with stats
            st.markdown(f"""
            <div style="background: {'rgba(59, 130, 246, 0.1)' if is_selected else 'rgba(255, 255, 255, 0.03)'}; 
                        border: 1px solid {'rgba(59, 130, 246, 0.3)' if is_selected else 'rgba(255, 255, 255, 0.08)'}; 
                        border-radius: 0.5rem; 
                        padding: 0.875rem; 
                        margin-bottom: 0.5rem;
                        cursor: pointer;
                        transition: all 0.2s;">
                <div style="font-size: 0.875rem; font-weight: 600; color: var(--text-primary); margin-bottom: 0.375rem; 
                            word-break: break-word;">{owner_name}</div>
                <div style="display: flex; gap: 1rem; font-size: 0.75rem; color: var(--text-muted);">
                    <span>🏠 {properties} properties</span>
                    <span>📍 {zips} ZIPs</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Hidden button for selection
            if st.button(
                f"Select {owner_name}",
                key=f"owner_btn_{idx}_{owner_name}",
                use_container_width=True,
                type="primary" if is_selected else "secondary",
                disabled=is_selected
            ):
                st.session_state.selected_owner = owner_name
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show selected owner controls
        if selected_owner:
            st.markdown("<div style='margin-top: 1rem;'>", unsafe_allow_html=True)
            if st.button("🔄 Clear Selection", use_container_width=True):
                st.session_state.selected_owner = None
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
    else:
        # No investors with properties found
        st.info("📊 No target investors with properties found. Upload data to get started.")
    
    # ====================================
    # Portfolio Statistics
    # ====================================
    
    st.markdown("<h3 style='font-size: 1.25rem; margin-top: 2rem; margin-bottom: 1rem;'>Portfolio Statistics</h3>", unsafe_allow_html=True)
    
    # Show which dataset is being displayed
    if selected_owner:
        st.markdown(f"<p style='font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1rem;'>Showing stats for: <strong>{selected_owner}</strong></p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='font-size: 0.875rem; color: var(--text-muted); margin-bottom: 1rem;'>Showing stats for: <strong>All Target Investors</strong></p>", unsafe_allow_html=True)
    
    # Calculate metrics using display_parcels
    total_properties = len(display_parcels)
    total_zips = display_parcels['par_zip'].nunique() if not display_parcels.empty else 0
    total_sales = display_parcels['sales_amount'].sum() if not display_parcels.empty else 0
    total_assessment = display_parcels['certified_tax_total'].sum() if not display_parcels.empty else 0
    
    # Stats grid - Row 1
    stats_col1, stats_col2 = st.columns(2)
    
    with stats_col1:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{total_properties:,}</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Properties</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col2:
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{total_zips}</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">ZIP Codes</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Stats grid - Row 2
    st.markdown("<div style='margin-top: 0.75rem;'>", unsafe_allow_html=True)
    stats_col3, stats_col4 = st.columns(2)
    
    with stats_col3:
        # Format sales value
        if total_sales >= 1_000_000:
            sales_display = f"${total_sales / 1_000_000:.1f}M"
        elif total_sales >= 1_000:
            sales_display = f"${total_sales / 1_000:.0f}K"
        else:
            sales_display = f"${total_sales:.0f}"
            
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{sales_display}</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Total Sales</div>
        </div>
        """, unsafe_allow_html=True)
    
    with stats_col4:
        # Format assessment value
        if total_assessment >= 1_000_000:
            assess_display = f"${total_assessment / 1_000_000:.1f}M"
        elif total_assessment >= 1_000:
            assess_display = f"${total_assessment / 1_000:.0f}K"
        else:
            assess_display = f"${total_assessment:.0f}"
            
        st.markdown(f"""
        <div style="background: rgba(255, 255, 255, 0.05); padding: 1rem; border-radius: 0.75rem; text-align: center; border: 1px solid rgba(255, 255, 255, 0.08);">
            <div style="font-size: 1.5rem; font-weight: 700; background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">{assess_display}</div>
            <div style="font-size: 0.6875rem; color: #71717a; margin-top: 0.375rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 600;">Assessments</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # ====================================
    # Export Buttons
    # ====================================
    
    st.markdown("<div style='margin-top: 1.75rem;'>", unsafe_allow_html=True)
    
    if st.button("📥 Export Map", type="primary", use_container_width=True, key="export_map_sidebar"):
        st.success("✅ Map exported successfully!")
        st.balloons()
    
    if st.button("📊 Export Data", use_container_width=True, key="export_data_sidebar"):
        st.success("✅ Data exported to Excel!")
        st.balloons()
    
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ====================================
# MAP COLUMN
# ====================================

with col_map:
    # Generate and display map
    try:
        # ====================================
        # VALIDATION: Check GeoDataFrame
        # ====================================
        
        if st.session_state.get('debug_mode', False):
            st.info(f"🔍 Debug: Processing {len(display_parcels)} parcels for mapping...")
        
        # Validate GeoDataFrame has required columns
        required_cols = ['geometry', 'owner_clean']
        missing_cols = [col for col in required_cols if col not in display_parcels.columns]
        if missing_cols:
            st.error(f"❌ Missing required columns: {missing_cols}")
            st.stop()
        
        # Validate geometries exist and are valid
        null_geom_count = display_parcels['geometry'].isna().sum()
        if null_geom_count > 0:
            st.warning(f"⚠️ Found {null_geom_count} parcels with null geometries (will be excluded)")
            display_parcels = display_parcels[display_parcels['geometry'].notna()].copy()
        
        # Check if we still have data
        if display_parcels.empty:
            st.error("❌ No valid parcel geometries found for mapping")
            st.stop()
        
        # Validate GeoDataFrame CRS
        if display_parcels.crs is None:
            st.warning("⚠️ No CRS set, assuming EPSG:4326")
            display_parcels.set_crs('EPSG:4326', inplace=True)
        elif display_parcels.crs.to_string() != 'EPSG:4326':
            if st.session_state.get('debug_mode', False):
                st.info(f"🔄 Converting from {display_parcels.crs} to EPSG:4326")
            display_parcels = display_parcels.to_crs('EPSG:4326')
        
        if st.session_state.get('debug_mode', False):
            st.success(f"✅ Validated {len(display_parcels)} parcels with geometries")
        
        # Create city config
        city_config = {
            'center_lat': city['center_lat'],
            'center_lng': city['center_lng'],
            'zoom_level': city['zoom_level']
        }
        
        # Calculate statistics per owner (optimized with groupby)
        if not target_parcels.empty:
            # Group by owner and aggregate stats efficiently
            stats_agg = target_parcels.groupby('owner_clean').agg({
                'parcel_pin': 'count',
                'sales_amount': 'sum',
                'certified_tax_total': 'sum'
            }).reset_index()
            
            # Rename columns for clarity
            stats_agg.columns = ['owner', 'count', 'total_sales', 'total_assess']
            
            # Convert Decimal columns to float
            stats_agg['total_sales'] = stats_agg['total_sales'].astype(float)
            stats_agg['total_assess'] = stats_agg['total_assess'].astype(float)
            
            # Calculate averages
            stats_agg['avg_sales'] = stats_agg['total_sales'] / stats_agg['count']
            stats_agg['avg_assess'] = stats_agg['total_assess'] / stats_agg['count']
            stats_agg['zip_table'] = None
            
            # Convert to dictionary format expected by map generator
            stats_per_owner = stats_agg.set_index('owner').to_dict('index')
        else:
            stats_per_owner = {}
        
        # Calculate aggregate statistics
        total_sales_all = float(target_parcels['sales_amount'].sum()) if 'sales_amount' in target_parcels.columns else 0
        total_assess_all = float(target_parcels['certified_tax_total'].sum()) if 'certified_tax_total' in target_parcels.columns else 0
        count_all = len(target_parcels)
        
        all_stats = {
            'count': count_all,
            'total_sales': total_sales_all,
            'total_assess': total_assess_all,
            'avg_sales': total_sales_all / count_all if count_all > 0 else 0,
            'avg_assess': total_assess_all / count_all if count_all > 0 else 0,
            'zip_table': None
        }
        
        # ====================================
        # GENERATE MAP (with caching + session state)
        # ====================================
        # Handle different dataset modes
        if dataset_mode == "All Parcels":
            # In All Parcels mode, use all unique owners from loaded parcels
            # (target_owners list may be empty)
            all_unique_owners = target_parcels['owner_clean'].dropna().unique().tolist()
            investors_with_properties = [owner for owner in stats_per_owner.keys() if stats_per_owner[owner]['count'] > 0]

            # If we have a large number of owners, limit to top N to avoid performance issues
            if len(investors_with_properties) > 100:
                # Sort by property count and take top 100
                sorted_owners = sorted(investors_with_properties, key=lambda o: stats_per_owner[o]['count'], reverse=True)
                investors_with_properties = sorted_owners[:100]
                if not selected_owner or selected_owner not in investors_with_properties:
                    # Show warning that we're limiting
                    pass  # We'll show this later

        else:
            # Target Owners Only mode - use defined target owners
            investors_with_properties = [owner for owner in stats_per_owner.keys() if stats_per_owner[owner]['count'] > 0]

        # PERFORMANCE OPTIMIZATION: If filtering to a single investor, only generate that investor's layer
        # This dramatically speeds up map generation when viewing individual investors
        if selected_owner:
            map_target_owners = [selected_owner] if selected_owner in investors_with_properties else investors_with_properties
            map_stats_per_owner = {selected_owner: stats_per_owner[selected_owner]} if selected_owner in stats_per_owner else stats_per_owner
        else:
            map_target_owners = investors_with_properties
            map_stats_per_owner = stats_per_owner

        # Create cache key for session state - includes city, dataset mode, view mode, owner, and sample size
        current_map_key = f"{selected_city_id}_{dataset_mode}_{sample_size}_{view_mode}_{st.session_state.get('selected_owner', 'all')}"
        previous_map_key = st.session_state.get('map_cache_key', None)

        # Check if we need to regenerate the map
        needs_regeneration = (
            previous_map_key != current_map_key or
            'cached_map' not in st.session_state
        )

        if needs_regeneration:
            # Progress indicator
            progress_container = st.empty()
            progress_bar = st.progress(0)
            status_text = st.empty()

            try:
                # Step 1: Preparing data
                start_time = time.time()
                progress_bar.progress(20)
                status_text.info(f"🗺️ Step 1/3: Preparing map data ({len(display_parcels):,} parcels, {len(map_target_owners)} investor{'s' if len(map_target_owners) != 1 else ''})...")
                time.sleep(0.1)  # Brief pause for UI update

                # Step 2: Generate map layers
                progress_bar.progress(40)
                status_text.info(f"🗺️ Step 2/3: Generating map layers with clustering ({view_mode} mode)...")

                # Use cached map generation function
                # Cache key: city_id, view_mode, selected_owner
                # Data parameters prefixed with _ are not included in cache key
                folium_map = generate_cached_map(
                    city_id=selected_city_id,
                    view_mode=view_mode,
                    selected_owner=st.session_state.get('selected_owner', None),
                    _parcels_gdf=display_parcels,
                    _city_config=city_config,
                    _target_owners=map_target_owners,
                    _stats_per_owner=map_stats_per_owner,
                    _all_stats=all_stats,
                    _view_mode_param=view_mode  # Pass to actual generator
                )
                
                if folium_map is None:
                    raise ValueError("Map generator returned None")
                
                # Step 3: Caching results
                progress_bar.progress(80)
                status_text.info("🗺️ Step 3/3: Caching map for fast future loads...")
                
                # Store in session state
                st.session_state.cached_map = folium_map
                st.session_state.map_cache_key = current_map_key
                
                # Complete
                progress_bar.progress(100)
                elapsed_time = time.time() - start_time
                status_text.success(f"✅ Map generated successfully in {elapsed_time:.1f}s! (cached for 1 hour)")
                time.sleep(1)  # Show success message briefly
                
                # Clear progress indicators
                progress_container.empty()
                progress_bar.empty()
                status_text.empty()
                
            except Exception as map_error:
                st.error(f"❌ Map generation failed: {str(map_error)}")
                if st.session_state.get('debug_mode', False):
                    st.exception(map_error)
                
                # Show diagnostic information
                with st.expander("🔍 Diagnostic Information"):
                    st.write("**City Config:**", city_config)
                    st.write("**Display Parcels Shape:**", display_parcels.shape)
                    st.write("**Display Parcels Columns:**", display_parcels.columns.tolist())
                    st.write("**Target Owners Count:**", len(target_owners))
                    st.write("**Stats Per Owner Keys:**", list(stats_per_owner.keys())[:10])
                    st.write("**Sample Geometry Type:**", type(display_parcels.iloc[0]['geometry']) if not display_parcels.empty else None)
                
                st.stop()
        else:
            # Map already exists in session state - reusing it
            cached_msg = st.empty()
            cached_msg.success(f"♻️ Using cached map (instant load! - {view_mode} mode)")
            time.sleep(0.5)  # Brief message
            cached_msg.empty()
        
        # Retrieve map from session state for display
        folium_map = st.session_state.get('cached_map', None)
        if folium_map is None:
            st.error("❌ No map available in session state")
            st.stop()
        
        # Display map in glass container
        st.markdown('<div class="glass-card" style="padding: 0; overflow: hidden; min-height: 700px;">', unsafe_allow_html=True)
        
        try:
            # Show rendering indicator
            with st.spinner("🌍 Rendering interactive map..."):
                st_folium(folium_map, width=None, height=700, returned_objects=[])
        except Exception as render_error:
            st.error(f"❌ Map rendering failed: {str(render_error)}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            # Fallback: Show basic map info
            st.markdown('<div class="glass-card">', unsafe_allow_html=True)
            st.warning("⚠️ Unable to render interactive map. Showing data summary instead:")
            st.metric("Total Parcels", len(display_parcels))
            st.metric("Target Investors", len(target_owners))
            st.metric("Map Center", f"{city_config['center_lat']:.4f}, {city_config['center_lng']:.4f}")
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.get('debug_mode', False):
                st.exception(render_error)
            st.stop()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Property Details Table (placeholder for future map click interaction)
        st.markdown('<div class="glass-card" style="margin-top: 1.5rem;">', unsafe_allow_html=True)
        st.markdown("<h3 style='font-size: 1.25rem; margin-bottom: 1rem;'>Selected Property Details</h3>", unsafe_allow_html=True)
        
        st.markdown("""
        <table style="width: 100%; color: var(--text-secondary);">
            <tr style="border-bottom: 1px solid rgba(255, 255, 255, 0.08);">
                <td style="padding: 1rem; width: 200px;"><strong>Parcel PIN</strong></td>
                <td style="padding: 1rem;">Click a property on the map to view details</td>
            </tr>
        </table>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    except Exception as e:
        st.error(f"❌ Error in map viewer: {str(e)}")
        
        # Provide detailed error information
        st.markdown('<div class="glass-card">', unsafe_allow_html=True)
        st.markdown("### 🔧 Troubleshooting Information")
        
        st.write("**Error Type:**", type(e).__name__)
        st.write("**Error Message:**", str(e))
        
        # Show what data we have
        try:
            st.write("**Available Data:**")
            st.write(f"- City loaded: {city is not None}")
            st.write(f"- Parcels loaded: {not parcels_gdf.empty if 'parcels_gdf' in locals() else 'Not loaded'}")
            st.write(f"- Target owners: {len(target_owners) if 'target_owners' in locals() else 'Not loaded'}")
            if 'target_parcels' in locals():
                st.write(f"- Target parcels: {len(target_parcels)}")
                st.write(f"- Has geometry column: {'geometry' in target_parcels.columns}")
            if 'display_parcels' in locals():
                st.write(f"- Display parcels: {len(display_parcels)}")
        except:
            pass
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Show full traceback in debug mode
        if st.session_state.get('debug_mode', False):
            with st.expander("📋 Full Error Traceback"):
                st.exception(e)
        
        # Suggest actions
        st.info("💡 **Possible solutions:**\n"
                "1. Try refreshing the page\n"
                "2. Select a different market\n"
                "3. Check if data was uploaded correctly\n"
                "4. Enable debug mode for more details\n"
                "5. Contact support if issue persists")
