"""
Example: Generate a Sample Map
Demonstrates the map generator with synthetic data
"""

import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mapping.map_generator import generate_map


def create_sample_data():
    """Create sample parcel data for demonstration."""
    import random
    random.seed(42)  # For reproducible results
    
    print("Creating sample parcel data...")
    
    # Create sample parcels scattered across Cleveland
    parcels = []
    owner_names = ["SMITH PROPERTIES", "JONES LLC", "BROWN INVESTMENTS", "DAVIS HOLDINGS", "WILSON REALTY"]
    zip_codes = [44102, 44103, 44104, 44105]
    
    # Cleveland area boundaries (approximate)
    # Longitude: -81.85 to -81.50 (west to east)
    # Latitude: 41.40 to 41.60 (south to north)
    
    parcel_id = 1
    for i in range(100):  # Create 100 parcels
        # Randomly distribute across Cleveland
        # Add some clustering by ZIP code for realism
        zip_index = i % len(zip_codes)
        zip_code = zip_codes[zip_index]
        
        # Create clusters for each ZIP
        if zip_index == 0:  # 44102 - west side
            lng_base = -81.75 + random.uniform(-0.08, 0.08)
            lat_base = 41.47 + random.uniform(-0.05, 0.05)
        elif zip_index == 1:  # 44103 - north-central
            lng_base = -81.65 + random.uniform(-0.08, 0.08)
            lat_base = 41.52 + random.uniform(-0.05, 0.05)
        elif zip_index == 2:  # 44104 - east side
            lng_base = -81.58 + random.uniform(-0.08, 0.08)
            lat_base = 41.48 + random.uniform(-0.05, 0.05)
        else:  # 44105 - southeast
            lng_base = -81.62 + random.uniform(-0.08, 0.08)
            lat_base = 41.44 + random.uniform(-0.05, 0.05)
        
        # Create a small parcel polygon (typical lot size ~0.0005 degrees)
        parcel_size = 0.0003  # About 100 feet
        polygon = Polygon([
            (lng_base, lat_base),
            (lng_base + parcel_size, lat_base),
            (lng_base + parcel_size, lat_base + parcel_size),
            (lng_base, lat_base + parcel_size)
        ])
        
        # Assign owner (distribute evenly)
        owner = owner_names[parcel_id % len(owner_names)]
        
        parcels.append({
            "parcelpin": f"PIN-{parcel_id:05d}",
            "owner_clean": owner,
            "deeded_owner": owner,
            "address": f"{parcel_id * 100} Sample St",
            "par_zip": zip_code,
            "tax_luc_description": "1-FAMILY" if parcel_id % 2 == 0 else "2-FAMILY",
            "sales_amount": 100000 + (parcel_id * 5000),
            "certified_tax_total": 80000 + (parcel_id * 4000),
            "geometry": polygon
        })
        
        parcel_id += 1
    
    # Create GeoDataFrame
    gdf = gpd.GeoDataFrame(parcels, geometry="geometry", crs="EPSG:4326")
    print(f"Created {len(gdf)} sample parcels scattered across Cleveland")
    return gdf


def calculate_stats(gdf, target_owners):
    """Calculate statistics for sample data."""
    print("Calculating portfolio statistics...")
    
    stats_per_owner = {}
    
    for owner in target_owners:
        subset = gdf[gdf["owner_clean"] == owner]
        
        # ZIP breakdown
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
        
        stats_per_owner[owner] = {
            "owner": owner,
            "count": len(subset),
            "total_sales": float(subset["sales_amount"].sum()),
            "total_assess": float(subset["certified_tax_total"].sum()),
            "avg_sales": float(subset["sales_amount"].mean()) if len(subset) > 0 else 0,
            "avg_assess": float(subset["certified_tax_total"].mean()) if len(subset) > 0 else 0,
            "zip_table": zip_table
        }
    
    # Aggregate stats
    zip_table_all = (
        gdf.groupby("par_zip")
        .agg(
            properties=("parcelpin", "count"),
            sales_total=("sales_amount", "sum"),
            assess_total=("certified_tax_total", "sum")
        )
        .reset_index()
        .sort_values("properties", ascending=False)
    )
    
    all_stats = {
        "owner": "ALL TARGET OWNERS",
        "count": len(gdf),
        "total_sales": float(gdf["sales_amount"].sum()),
        "total_assess": float(gdf["certified_tax_total"].sum()),
        "avg_sales": float(gdf["sales_amount"].mean()),
        "avg_assess": float(gdf["certified_tax_total"].mean()),
        "zip_table": zip_table_all
    }
    
    print(f"Calculated stats for {len(target_owners)} owners")
    return stats_per_owner, all_stats


def main():
    """Generate a sample map."""
    print("=" * 60)
    print("Sample Map Generator")
    print("=" * 60)
    
    # Create sample data
    gdf = create_sample_data()
    
    # Define target owners
    target_owners = [
        "SMITH PROPERTIES",
        "JONES LLC",
        "BROWN INVESTMENTS",
        "DAVIS HOLDINGS",
        "WILSON REALTY"
    ]
    
    # Calculate statistics
    stats_per_owner, all_stats = calculate_stats(gdf, target_owners)
    
    # Configure city (Cleveland coordinates)
    city_config = {
        "city_name": "cleveland",
        "display_name": "Cleveland, OH (Sample Data)",
        "center_lat": 41.4993,
        "center_lng": -81.6944,
        "zoom_level": 12
    }
    
    print("\nGenerating interactive map...")
    
    # Generate map without the layer control box (we use the sidebar instead)
    from mapping.map_generator import MapGenerator
    
    generator = MapGenerator(
        city_config,
        gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    
    # Generate map without Folium's default layer control box
    m = generator.generate_map(
        include_layer_control=False,  # Remove the box in upper right
        tile_layer="light"
    )
    
    # Save to file
    output_file = "sample_portfolio_map.html"
    m.save(output_file)
    
    print(f"\n✅ Map generated successfully!")
    print(f"📁 Saved to: {output_file}")
    print(f"\n📊 Map Statistics:")
    print(f"   - Total Parcels: {len(gdf)}")
    print(f"   - Target Owners: {len(target_owners)}")
    print(f"   - ZIP Codes: {len(gdf['par_zip'].unique())}")
    print(f"   - Total Value: ${all_stats['total_sales']:,.0f}")
    print(f"\n🌐 Open the HTML file in your browser to view the interactive map!")
    print("=" * 60)


if __name__ == "__main__":
    main()

