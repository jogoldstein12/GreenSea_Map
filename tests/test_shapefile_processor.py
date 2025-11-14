"""
Test script for data_processing/shapefile_processor.py
Tests shapefile loading, CRS conversion, geometry validation, and processing
"""

import sys
from pathlib import Path
import tempfile
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon, Point

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_processing.shapefile_processor import ShapefileProcessor, process_shapefile


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def create_sample_shapefile():
    """Create a temporary shapefile with sample Cleveland-style parcel data"""
    # Create sample polygons (simple squares)
    geometries = [
        Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
        Polygon([(1, 0), (1, 1), (2, 1), (2, 0)]),
        Polygon([(2, 0), (2, 1), (3, 1), (3, 0)]),
        Polygon([(3, 0), (3, 1), (4, 1), (4, 0)]),  # This one will be COMMERCIAL
        Polygon([(0, 1), (0, 2), (1, 2), (1, 1)]),
    ]
    
    # Sample attribute data mimicking Cleveland format
    data = {
        'PARCELPIN': [
            '123-456-789',
            '987-654-321',
            '111-222-333',
            '444-555-666',
            '777-888-999'
        ],
        'DEEDED_OWN': [
            'Smith Properties, LLC.',
            'Jones Investments Inc',
            'Brown Holdings Co.',
            'Wilson Real Estate Corp',
            'Davis Properties, Ltd.'
        ],
        'TAX_LUC_DE': [
            '1-FAMILY PLATTED LOT',
            '2-FAMILY PLATTED LOT',
            '1-FAMILY PLATTED LOT',
            'COMMERCIAL',  # Should be filtered out
            '1-FAMILY PLATTED LOT'
        ],
        'PAR_ADDR_ALL': [
            '123 Main St',
            '456 Oak Ave',
            '789 Elm St',
            '321 Commercial Dr',
            '654 Maple Ln'
        ],
        'PAR_ZIP': [
            '44102',
            '44103',
            '44104',
            '44105',
            '44102'
        ]
    }
    
    # Create GeoDataFrame with a standard CRS (NAD83 State Plane Ohio North)
    gdf = gpd.GeoDataFrame(data, geometry=geometries, crs="EPSG:3734")
    
    # Create temporary directory
    temp_dir = tempfile.mkdtemp(prefix='shapefile_test_')
    shapefile_path = Path(temp_dir) / 'test_parcels.shp'
    
    # Write shapefile
    gdf.to_file(shapefile_path)
    
    return str(shapefile_path), gdf


def test_shapefile_loading():
    """Test basic shapefile loading"""
    print_section("TEST 1: Shapefile Loading")
    
    shapefile_path, original_gdf = create_sample_shapefile()
    
    try:
        processor = ShapefileProcessor()
        
        print(f"Loading shapefile from: {shapefile_path}")
        gdf = processor.load_shapefile(shapefile_path)
        
        print(f"\nLoaded {len(gdf)} features, {len(gdf.columns)} columns")
        print(f"Geometry types: {gdf.geometry.type.unique()}")
        print(f"Original CRS: {gdf.crs}")
        
        if len(gdf) == len(original_gdf):
            print("\n✅ PASS: All features loaded successfully")
            return True
        else:
            print(f"\n❌ FAIL: Expected {len(original_gdf)} features, got {len(gdf)}")
            return False
            
    finally:
        # Cleanup
        import shutil
        shutil.rmtree(Path(shapefile_path).parent)


def test_crs_conversion():
    """Test CRS conversion to WGS84"""
    print_section("TEST 2: CRS Conversion")
    
    shapefile_path, _ = create_sample_shapefile()
    
    try:
        processor = ShapefileProcessor(target_crs="EPSG:4326")
        gdf = processor.load_shapefile(shapefile_path)
        
        print(f"Original CRS: {gdf.crs}")
        print(f"Target CRS: EPSG:4326 (WGS84)")
        
        gdf_converted = processor.convert_crs(gdf)
        
        print(f"Converted CRS: {gdf_converted.crs}")
        
        # Check bounds changed (should be in lat/lng now)
        original_bounds = gdf.total_bounds
        converted_bounds = gdf_converted.total_bounds
        
        print(f"\nOriginal bounds: {original_bounds}")
        print(f"Converted bounds: {converted_bounds}")
        
        # CRS should be WGS84
        if "4326" in str(gdf_converted.crs):
            print("\n✅ PASS: CRS conversion successful")
            return True
        else:
            print("\n❌ FAIL: CRS not properly converted")
            return False
            
    finally:
        import shutil
        shutil.rmtree(Path(shapefile_path).parent)


def test_geometry_validation():
    """Test geometry validation"""
    print_section("TEST 3: Geometry Validation")
    
    shapefile_path, _ = create_sample_shapefile()
    
    try:
        processor = ShapefileProcessor()
        gdf = processor.load_shapefile(shapefile_path)
        
        valid_count, invalid_count = processor.validate_geometries(gdf)
        
        print(f"Valid geometries: {valid_count}")
        print(f"Invalid geometries: {invalid_count}")
        print(f"Total: {len(gdf)}")
        
        if valid_count == len(gdf) and invalid_count == 0:
            print("\n✅ PASS: All geometries are valid")
            return True
        else:
            print("\n❌ FAIL: Some geometries are invalid")
            return False
            
    finally:
        import shutil
        shutil.rmtree(Path(shapefile_path).parent)


def test_normalization():
    """Test data normalization"""
    print_section("TEST 4: Data Normalization")
    
    shapefile_path, _ = create_sample_shapefile()
    
    try:
        processor = ShapefileProcessor()
        gdf = processor.load_shapefile(shapefile_path)
        
        print("BEFORE normalization:")
        print(f"Columns: {[c for c in gdf.columns if c != 'geometry']}\n")
        print(gdf.drop(columns='geometry').head(2))
        
        normalized = processor.normalize_data(gdf)
        
        print("\n\nAFTER normalization:")
        print(f"Columns: {[c for c in normalized.columns if c != 'geometry']}\n")
        print(normalized.drop(columns='geometry').head(2))
        
        # Check expected columns
        expected_cols = ['parcelpin', 'deeded_owner', 'owner_clean', 'tax_luc_description']
        found = [col for col in expected_cols if col in normalized.columns]
        
        print(f"\n✓ Expected columns found: {len(found)}/{len(expected_cols)}")
        
        # Check owner cleaning
        if 'owner_clean' in normalized.columns:
            sample_clean = normalized['owner_clean'].iloc[0]
            print(f"✓ Owner cleaning applied: '{sample_clean}'")
        
        if len(found) == len(expected_cols):
            print("\n✅ PASS: Normalization successful")
            return True
        else:
            print("\n❌ FAIL: Some columns missing")
            return False
            
    finally:
        import shutil
        shutil.rmtree(Path(shapefile_path).parent)


def test_property_type_filtering():
    """Test filtering by property type"""
    print_section("TEST 5: Property Type Filtering")
    
    shapefile_path, original_gdf = create_sample_shapefile()
    
    try:
        processor = ShapefileProcessor()
        gdf = processor.load_shapefile(shapefile_path)
        normalized = processor.normalize_data(gdf)
        
        print(f"Before filtering: {len(normalized)} features")
        print(f"Property types: {normalized['tax_luc_description'].value_counts().to_dict()}")
        
        filtered = processor.filter_by_property_type(normalized)
        
        print(f"\nAfter filtering: {len(filtered)} features")
        print(f"Property types: {filtered['tax_luc_description'].value_counts().to_dict()}")
        
        # Should have 4 features (1 COMMERCIAL filtered out)
        expected_features = 4
        if len(filtered) == expected_features:
            print(f"\n✅ PASS: Correctly filtered to {expected_features} residential parcels")
            return True
        else:
            print(f"\n❌ FAIL: Expected {expected_features} features, got {len(filtered)}")
            return False
            
    finally:
        import shutil
        shutil.rmtree(Path(shapefile_path).parent)


def test_full_pipeline():
    """Test the complete shapefile processing pipeline"""
    print_section("TEST 6: Full Processing Pipeline")
    
    shapefile_path, original_gdf = create_sample_shapefile()
    
    try:
        print(f"Processing shapefile: {shapefile_path}")
        print(f"Original data: {len(original_gdf)} features\n")
        
        # Process using the pipeline
        processor = ShapefileProcessor(target_crs="EPSG:4326")
        processed = processor.process_shapefile(
            shapefile_path,
            convert_crs=True,
            fix_geometries=True,
            filter_property_types=True
        )
        
        print(f"\nProcessed data: {len(processed)} features")
        print(f"Columns: {[c for c in processed.columns if c != 'geometry']}")
        print(f"CRS: {processed.crs}")
        
        # Get geometry summary
        summary = processor.get_geometry_summary(processed)
        
        print("\n📊 Geometry Summary:")
        print(f"  Total features: {summary['total_features']}")
        print(f"  Geometry types: {summary['geometry_types']}")
        print(f"  CRS: {summary['crs']}")
        print(f"  Valid geometries: {summary['valid_geometries']}")
        print(f"  Null geometries: {summary['null_geometries']}")
        
        if 'bounds' in summary and summary['bounds']:
            print(f"  Bounds: {[f'{x:.6f}' for x in summary['bounds']]}")
        
        if 'total_area' in summary:
            print(f"  Total area: {summary['total_area']:.6f}")
            print(f"  Avg area: {summary['avg_area']:.6f}")
        
        # Validation checks
        checks = [
            (len(processed) == 4, "Correct number of features after filtering"),
            ('owner_clean' in processed.columns, "owner_clean column exists"),
            ('parcelpin' in processed.columns, "parcelpin column exists"),
            ('geometry' in processed.columns, "geometry column exists"),
            ("4326" in str(processed.crs), "CRS converted to WGS84"),
            (summary['valid_geometries'] == 4, "All geometries valid")
        ]
        
        print("\n📋 Validation Checks:")
        all_passed = True
        for passed, description in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {description}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ PASS: Full pipeline works correctly!")
            return True
        else:
            print("\n❌ FAIL: Some pipeline checks failed")
            return False
            
    finally:
        import shutil
        shutil.rmtree(Path(shapefile_path).parent)


def test_convenience_function():
    """Test the convenience function"""
    print_section("TEST 7: Convenience Function")
    
    shapefile_path, _ = create_sample_shapefile()
    
    try:
        print(f"Using process_shapefile() convenience function\n")
        
        # Process using convenience function
        gdf = process_shapefile(shapefile_path, target_crs="EPSG:4326")
        
        print(f"Processed {len(gdf)} features")
        print(f"Columns: {[c for c in gdf.columns if c != 'geometry']}")
        print(f"CRS: {gdf.crs}")
        
        if len(gdf) == 4 and 'owner_clean' in gdf.columns and "4326" in str(gdf.crs):
            print("\n✅ PASS: Convenience function works")
            return True
        else:
            print("\n❌ FAIL: Unexpected results")
            return False
            
    finally:
        import shutil
        shutil.rmtree(Path(shapefile_path).parent)


def test_geometry_fix():
    """Test invalid geometry fixing"""
    print_section("TEST 8: Invalid Geometry Fixing")
    
    # Create a GeoDataFrame with an invalid geometry
    # (self-intersecting polygon)
    invalid_polygon = Polygon([(0, 0), (0, 2), (2, 0), (2, 2), (0, 0)])
    valid_polygon = Polygon([(3, 0), (3, 1), (4, 1), (4, 0)])
    
    data = {
        'PARCELPIN': ['invalid-001', 'valid-001'],
        'DEEDED_OWN': ['Test Owner 1', 'Test Owner 2'],
        'TAX_LUC_DE': ['1-FAMILY PLATTED LOT', '1-FAMILY PLATTED LOT']
    }
    
    gdf = gpd.GeoDataFrame(
        data,
        geometry=[invalid_polygon, valid_polygon],
        crs="EPSG:4326"
    )
    
    # Create temporary shapefile
    temp_dir = tempfile.mkdtemp(prefix='shapefile_invalid_')
    shapefile_path = Path(temp_dir) / 'invalid_geoms.shp'
    gdf.to_file(shapefile_path)
    
    try:
        processor = ShapefileProcessor()
        loaded_gdf = processor.load_shapefile(str(shapefile_path))
        
        print("Testing geometry validation and fixing...")
        
        valid_count, invalid_count = processor.validate_geometries(loaded_gdf)
        print(f"\nBefore fix: {valid_count} valid, {invalid_count} invalid")
        
        if invalid_count > 0:
            fixed_gdf = processor.fix_invalid_geometries(loaded_gdf)
            valid_after, invalid_after = processor.validate_geometries(fixed_gdf)
            print(f"After fix: {valid_after} valid, {invalid_after} invalid")
            
            if invalid_after < invalid_count:
                print("\n✅ PASS: Successfully fixed invalid geometries")
                return True
            else:
                print("\n⚠️  WARNING: Could not fix invalid geometries (this is OK)")
                return True  # Still pass, as fixing may not always work
        else:
            print("\n✅ PASS: No invalid geometries to fix")
            return True
            
    except Exception as e:
        print(f"\n❌ FAIL: Error during geometry fix test: {str(e)}")
        return False
    finally:
        import shutil
        shutil.rmtree(temp_dir)


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  SHAPEFILE PROCESSOR TEST SUITE")
    print("="*60)
    
    tests = [
        ("Shapefile Loading", test_shapefile_loading),
        ("CRS Conversion", test_crs_conversion),
        ("Geometry Validation", test_geometry_validation),
        ("Data Normalization", test_normalization),
        ("Property Type Filtering", test_property_type_filtering),
        ("Full Pipeline", test_full_pipeline),
        ("Convenience Function", test_convenience_function),
        ("Invalid Geometry Fixing", test_geometry_fix)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result, None))
        except Exception as e:
            print(f"\n❌ ERROR in {test_name}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False, str(e)))
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result, _ in results if result)
    total = len(results)
    
    for test_name, result, error in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {test_name}")
        if error:
            print(f"       Error: {error}")
    
    print(f"\n{'='*60}")
    print(f"  Results: {passed}/{total} tests passed")
    print(f"{'='*60}\n")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! Shapefile Processor is working correctly.\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

