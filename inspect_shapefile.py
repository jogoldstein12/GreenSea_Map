"""
Quick script to inspect shapefile column names and sample data
"""

import sys
from pathlib import Path
import geopandas as gpd

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def inspect_shapefile(shapefile_path: str):
    """
    Display column names and sample data from a shapefile.
    
    Args:
        shapefile_path: Path to the .shp file
    """
    print(f"\n{'='*80}")
    print(f"INSPECTING SHAPEFILE: {shapefile_path}")
    print(f"{'='*80}\n")
    
    # Read shapefile
    gdf = gpd.read_file(shapefile_path)
    
    # Show basic info
    print(f"📊 BASIC INFO:")
    print(f"   Total records: {len(gdf):,}")
    print(f"   Total columns: {len(gdf.columns)}")
    print(f"   CRS: {gdf.crs}")
    
    # Show column names
    print(f"\n📝 COLUMN NAMES ({len(gdf.columns)} total):")
    print(f"   {'-'*76}")
    for idx, col in enumerate(gdf.columns, 1):
        col_type = str(gdf[col].dtype)
        null_count = gdf[col].isnull().sum()
        print(f"   {idx:2d}. {col:30s} | Type: {col_type:12s} | Nulls: {null_count:,}")
    
    # Show sample data for key columns
    print(f"\n🔍 SAMPLE DATA (first 5 records):")
    print(f"   {'-'*76}")
    
    # Look for owner-related columns
    owner_cols = [col for col in gdf.columns if 'own' in col.lower() or 'deed' in col.lower()]
    if owner_cols:
        print(f"\n   📌 OWNER-RELATED COLUMNS:")
        for col in owner_cols:
            print(f"\n   {col}:")
            samples = gdf[col].head(5).tolist()
            for i, val in enumerate(samples, 1):
                print(f"      {i}. {val}")
    
    # Show all columns in first record
    print(f"\n   📌 FIRST RECORD (all columns):")
    first_record = gdf.iloc[0]
    for col in gdf.columns:
        if col != 'geometry':  # Skip geometry for readability
            print(f"      {col:30s}: {first_record[col]}")
    
    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    # Default to Cleveland shapefile
    shapefile_path = "Input Data/ClevelandSHP/Combined_Parcels_-_Cleveland_Only.shp"
    
    # Allow custom path as argument
    if len(sys.argv) > 1:
        shapefile_path = sys.argv[1]
    
    try:
        inspect_shapefile(shapefile_path)
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

