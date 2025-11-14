"""
Test Suite for Map Generator Module
Tests the MapGenerator class and map generation functionality
"""

import pytest
import pandas as pd
import geopandas as gpd
import folium
from shapely.geometry import Polygon
from typing import Dict, List

from mapping.map_generator import MapGenerator, generate_map


# =============================================================================
# TEST FIXTURES
# =============================================================================

@pytest.fixture
def sample_parcels_gdf():
    """Create sample GeoDataFrame with parcels."""
    data = {
        "parcelpin": ["12345", "12346", "12347", "12348", "12349"],
        "owner_clean": ["SMITH", "JONES", "SMITH", "JONES", "BROWN"],
        "deeded_owner": ["Smith Properties", "Jones LLC", "Smith Co", "Jones Inc", "Brown Corp"],
        "address": ["123 Main St", "456 Oak Ave", "789 Pine St", "321 Elm St", "654 Maple Dr"],
        "par_zip": [44102, 44103, 44102, 44103, 44104],
        "tax_luc_description": ["1-FAMILY", "2-FAMILY", "1-FAMILY", "1-FAMILY", "2-FAMILY"],
        "sales_amount": [100000, 150000, 120000, 180000, 200000],
        "certified_tax_total": [80000, 120000, 95000, 140000, 160000],
        "geometry": [
            Polygon([(0, 0), (0, 0.001), (0.001, 0.001), (0.001, 0)]),
            Polygon([(0.001, 0), (0.001, 0.001), (0.002, 0.001), (0.002, 0)]),
            Polygon([(0.002, 0), (0.002, 0.001), (0.003, 0.001), (0.003, 0)]),
            Polygon([(0.003, 0), (0.003, 0.001), (0.004, 0.001), (0.004, 0)]),
            Polygon([(0.004, 0), (0.004, 0.001), (0.005, 0.001), (0.005, 0)]),
        ]
    }
    
    gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
    return gdf


@pytest.fixture
def target_owners():
    """Sample target owners list."""
    return ["SMITH", "JONES", "BROWN"]


@pytest.fixture
def stats_per_owner(sample_parcels_gdf):
    """Generate statistics per owner."""
    stats = {}
    
    for owner in ["SMITH", "JONES", "BROWN"]:
        subset = sample_parcels_gdf[sample_parcels_gdf["owner_clean"] == owner]
        
        zip_table = (
            subset.groupby("par_zip")
            .agg(
                properties=("parcelpin", "count"),
                sales_total=("sales_amount", "sum"),
                assess_total=("certified_tax_total", "sum")
            )
            .reset_index()
            .sort_values("properties", ascending=False)
        )
        
        stats[owner] = {
            "owner": owner,
            "count": len(subset),
            "total_sales": float(subset["sales_amount"].sum()),
            "total_assess": float(subset["certified_tax_total"].sum()),
            "avg_sales": float(subset["sales_amount"].mean()) if len(subset) > 0 else 0,
            "avg_assess": float(subset["certified_tax_total"].mean()) if len(subset) > 0 else 0,
            "zip_table": zip_table
        }
    
    return stats


@pytest.fixture
def all_stats(sample_parcels_gdf):
    """Generate aggregate statistics."""
    zip_table = (
        sample_parcels_gdf.groupby("par_zip")
        .agg(
            properties=("parcelpin", "count"),
            sales_total=("sales_amount", "sum"),
            assess_total=("certified_tax_total", "sum")
        )
        .reset_index()
        .sort_values("properties", ascending=False)
    )
    
    return {
        "owner": "ALL TARGET OWNERS",
        "count": len(sample_parcels_gdf),
        "total_sales": float(sample_parcels_gdf["sales_amount"].sum()),
        "total_assess": float(sample_parcels_gdf["certified_tax_total"].sum()),
        "avg_sales": float(sample_parcels_gdf["sales_amount"].mean()),
        "avg_assess": float(sample_parcels_gdf["certified_tax_total"].mean()),
        "zip_table": zip_table
    }


@pytest.fixture
def city_config():
    """Sample city configuration."""
    return {
        "city_name": "cleveland",
        "display_name": "Cleveland, OH",
        "center_lat": 41.4993,
        "center_lng": -81.6944,
        "zoom_level": 11
    }


# =============================================================================
# TEST MAPGENERATOR INITIALIZATION
# =============================================================================

def test_mapgenerator_initialization(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test MapGenerator initializes correctly."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    assert generator.city_config == city_config
    assert len(generator.parcels_gdf) == len(sample_parcels_gdf)
    assert generator.target_owners == target_owners
    assert len(generator.owner_colors) == len(target_owners)
    assert generator.layer_builder is not None


def test_mapgenerator_with_empty_geodataframe(
    city_config,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test MapGenerator handles empty GeoDataFrame."""
    empty_gdf = gpd.GeoDataFrame(columns=["owner_clean", "geometry"], crs="EPSG:4326")
    
    generator = MapGenerator(
        city_config,
        empty_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    assert len(generator.parcels_gdf) == 0
    assert generator.layer_builder is not None


# =============================================================================
# TEST MAP GENERATION
# =============================================================================

def test_generate_basic_map(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test basic map generation."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    m = generator.generate_map()
    
    # Verify it's a Folium map
    assert isinstance(m, folium.Map)
    
    # Verify map is centered correctly
    assert m.location == [41.4993, -81.6944]
    
    # Map should have content
    html = m._repr_html_()
    assert html is not None
    assert len(html) > 0


def test_generate_map_with_different_tile_layers(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test map generation with different tile layers."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    # Test different tile layers
    for tile_type in ["light", "dark", "osm"]:
        m = generator.generate_map(tile_layer=tile_type)
        assert isinstance(m, folium.Map)


def test_generate_map_without_layer_control(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test map generation without layer control."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    m = generator.generate_map(include_layer_control=False)
    assert isinstance(m, folium.Map)


# =============================================================================
# TEST SIDEBAR GENERATION
# =============================================================================

def test_sidebar_html_generation(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test sidebar HTML generation."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    zip_codes = ["44102", "44103", "44104"]
    sidebar_html = generator._generate_sidebar_html(zip_codes)
    
    # Verify sidebar contains key elements
    assert "gs-sidebar" in sidebar_html
    assert "Portfolio Viewer" in sidebar_html
    assert "ownerSelect" in sidebar_html
    assert "zipSelect" in sidebar_html
    
    # Verify all owners are in the sidebar
    for owner in target_owners:
        assert owner in sidebar_html


def test_owner_panel_generation(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test individual owner panel generation."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    panel_html = generator._generate_owner_panel("SMITH", stats_per_owner["SMITH"])
    
    # Verify panel contains stats
    assert "SMITH" in panel_html
    assert "Properties:" in panel_html
    assert "Total Sales:" in panel_html
    assert "Total Assessed:" in panel_html


def test_zip_panel_generation(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test ZIP code panel generation."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    panel_html = generator._generate_zip_panel("44102")
    
    # Verify panel contains ZIP info
    assert "44102" in panel_html
    assert "Properties:" in panel_html


# =============================================================================
# TEST JAVASCRIPT GENERATION
# =============================================================================

def test_toggle_javascript_generation(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test layer toggle JavaScript generation."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    owner_layer_names = {"owner_smith": "layer_1", "owner_jones": "layer_2"}
    zip_layer_names = {"zip_44102": "layer_3", "zip_44103": "layer_4"}
    
    js = generator._generate_toggle_javascript(
        "map_123",
        "base_layer",
        owner_layer_names,
        zip_layer_names,
        ["44102", "44103"]
    )
    
    # Verify JavaScript contains key functions
    assert "gsToggleLayers" in js
    assert "gsTypeOwner" in js
    assert "gsOwnerLayerNames" in js
    assert "gsZipLayerNames" in js


# =============================================================================
# TEST UTILITY FUNCTIONS
# =============================================================================

def test_format_money(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test money formatting."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    # Test various inputs
    assert generator._format_money(100000) == "$100,000"
    assert generator._format_money(1234.56) == "$1,235"
    assert generator._format_money(0) == "$0"
    assert generator._format_money(None) == "N/A"
    assert generator._format_money("invalid") == "invalid"


def test_generate_zip_table(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test ZIP breakdown table generation."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    zip_df = stats_per_owner["SMITH"]["zip_table"]
    table_html = generator._generate_zip_table(zip_df)
    
    # Verify table contains expected elements
    assert "<table>" in table_html or "No ZIP breakdown" in table_html
    
    # Test with empty DataFrame
    empty_df = pd.DataFrame()
    table_html = generator._generate_zip_table(empty_df)
    assert "No ZIP breakdown" in table_html


def test_generate_zip_owner_table(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test ZIP owner breakdown table generation."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    zip_subset = sample_parcels_gdf[sample_parcels_gdf["par_zip"] == 44102]
    table_html = generator._generate_zip_owner_table(zip_subset, "sales_amount")
    
    # Verify table contains expected elements
    assert "<table>" in table_html or "No portfolio activity" in table_html


# =============================================================================
# TEST CONVENIENCE FUNCTION
# =============================================================================

def test_convenience_generate_map_function(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test the convenience generate_map() function."""
    m = generate_map(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    assert isinstance(m, folium.Map)
    assert m.location == [41.4993, -81.6944]


def test_convenience_function_with_tile_layer(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test convenience function with custom tile layer."""
    m = generate_map(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats,
        tile_layer="dark"
    )
    
    assert isinstance(m, folium.Map)


# =============================================================================
# TEST EDGE CASES
# =============================================================================

def test_map_with_no_zip_codes(
    city_config,
    target_owners,
    stats_per_owner,
    all_stats
):
    """Test map generation when parcels have no ZIP codes."""
    # Create GeoDataFrame without par_zip column
    data = {
        "parcelpin": ["12345", "12346"],
        "owner_clean": ["SMITH", "JONES"],
        "geometry": [
            Polygon([(0, 0), (0, 0.001), (0.001, 0.001), (0.001, 0)]),
            Polygon([(0.001, 0), (0.001, 0.001), (0.002, 0.001), (0.002, 0)]),
        ]
    }
    gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
    
    generator = MapGenerator(
        city_config,
        gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    m = generator.generate_map()
    assert isinstance(m, folium.Map)


def test_map_with_single_owner(city_config):
    """Test map generation with only one owner."""
    data = {
        "parcelpin": ["12345", "12346"],
        "owner_clean": ["SMITH", "SMITH"],
        "par_zip": [44102, 44102],
        "sales_amount": [100000, 150000],
        "certified_tax_total": [80000, 120000],
        "geometry": [
            Polygon([(0, 0), (0, 0.001), (0.001, 0.001), (0.001, 0)]),
            Polygon([(0.001, 0), (0.001, 0.001), (0.002, 0.001), (0.002, 0)]),
        ]
    }
    gdf = gpd.GeoDataFrame(data, geometry="geometry", crs="EPSG:4326")
    
    target_owners = ["SMITH"]
    
    zip_table = (
        gdf.groupby("par_zip")
        .agg(
            properties=("parcelpin", "count"),
            sales_total=("sales_amount", "sum"),
            assess_total=("certified_tax_total", "sum")
        )
        .reset_index()
    )
    
    stats = {
        "SMITH": {
            "owner": "SMITH",
            "count": 2,
            "total_sales": 250000.0,
            "total_assess": 200000.0,
            "avg_sales": 125000.0,
            "avg_assess": 100000.0,
            "zip_table": zip_table
        }
    }
    
    all_stats = {
        "owner": "ALL TARGET OWNERS",
        "count": 2,
        "total_sales": 250000.0,
        "total_assess": 200000.0,
        "avg_sales": 125000.0,
        "avg_assess": 100000.0,
        "zip_table": zip_table
    }
    
    generator = MapGenerator(city_config, gdf, target_owners, stats, all_stats)
    m = generator.generate_map()
    
    assert isinstance(m, folium.Map)


def test_map_saves_to_html(
    city_config,
    sample_parcels_gdf,
    target_owners,
    stats_per_owner,
    all_stats,
    tmp_path
):
    """Test that generated map can be saved to HTML file."""
    generator = MapGenerator(
        city_config,
        sample_parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    m = generator.generate_map()
    
    # Save to temporary file
    output_file = tmp_path / "test_map.html"
    m.save(str(output_file))
    
    # Verify file was created and has content
    assert output_file.exists()
    content = output_file.read_text()
    assert len(content) > 1000  # Should have substantial content
    assert "Portfolio Viewer" in content
    assert "folium" in content.lower()


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v"])

