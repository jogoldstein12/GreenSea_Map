"""
Test script for mapping/layer_builder.py
Tests layer creation, popup generation, and data handling
"""

import sys
from pathlib import Path
import geopandas as gpd
import pandas as pd
from shapely.geometry import Polygon
import folium

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from mapping.layer_builder import LayerBuilder, build_layers_from_data
from mapping.styles import ColorScheme


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def create_sample_geodataframe():
    """Create sample GeoDataFrame with geometry and attributes"""
    # Create sample polygons
    geometries = [
        Polygon([(0, 0), (0, 1), (1, 1), (1, 0)]),
        Polygon([(1, 0), (1, 1), (2, 1), (2, 0)]),
        Polygon([(2, 0), (2, 1), (3, 1), (3, 0)]),
        Polygon([(3, 0), (3, 1), (4, 1), (4, 0)]),
        Polygon([(0, 1), (0, 2), (1, 2), (1, 1)]),
    ]
    
    # Sample data
    data = {
        'parcelpin': ['123-456', '123-457', '123-458', '123-459', '123-460'],
        'owner_clean': ['SMITH PROPERTIES', 'SMITH PROPERTIES', 'JONES INVESTMENTS', 
                        'BROWN HOLDINGS', 'JONES INVESTMENTS'],
        'par_addr': ['123 Main St', '456 Main St', '789 Oak Ave', '321 Elm St', '654 Maple Ln'],
        'sales_amount': [250000, 180000, 275000, 400000, 190000],
        'par_zip': ['44102', '44102', '44103', '44102', '44103']
    }
    
    gdf = gpd.GeoDataFrame(data, geometry=geometries, crs="EPSG:4326")
    return gdf


def test_initialization():
    """Test LayerBuilder initialization"""
    print_section("TEST 1: Initialization")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'BROWN HOLDINGS']
    
    builder = LayerBuilder(gdf, target_owners)
    
    print(f"Initialized LayerBuilder:")
    print(f"  Total parcels: {len(builder.gdf)}")
    print(f"  Target owners: {len(builder.target_owners)}")
    print(f"  Owner colors generated: {len(builder.owner_colors)}")
    print(f"  Popup fields: {builder.popup_fields}")
    
    checks = [
        (len(builder.gdf) == 5, "GeoDataFrame has 5 parcels"),
        (len(builder.target_owners) == 3, "3 target owners"),
        (len(builder.owner_colors) == 3, "Colors generated for all owners"),
        (len(builder.popup_fields) > 0, "Popup fields detected"),
        ('parcelpin' in builder.popup_fields, "Parcelpin in popup fields")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Initialization successful")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_base_layer():
    """Test base context layer creation"""
    print_section("TEST 2: Base Context Layer")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS']
    
    builder = LayerBuilder(gdf, target_owners)
    base_layer = builder.build_base_layer()
    
    print(f"Base layer created:")
    print(f"  Type: {type(base_layer).__name__}")
    print(f"  Has name attribute: {hasattr(base_layer, '_name')}")
    
    # Check it's a valid Folium object
    is_valid = isinstance(base_layer, (folium.GeoJson, folium.FeatureGroup))
    
    checks = [
        (is_valid, "Layer is valid Folium object"),
        (base_layer is not None, "Layer created successfully")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Base layer creation successful")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_owner_layer():
    """Test single owner layer creation"""
    print_section("TEST 3: Single Owner Layer")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'BROWN HOLDINGS']
    
    builder = LayerBuilder(gdf, target_owners)
    
    # Test layer with parcels
    layer, slug = builder.build_owner_layer('SMITH PROPERTIES')
    
    print(f"Owner layer for SMITH PROPERTIES:")
    print(f"  Type: {type(layer).__name__}")
    print(f"  Slug: {slug}")
    print(f"  Has name: {hasattr(layer, '_name')}")
    
    # Test layer with no parcels
    empty_layer, empty_slug = builder.build_owner_layer('NONEXISTENT OWNER')
    
    print(f"\nEmpty owner layer:")
    print(f"  Type: {type(empty_layer).__name__}")
    print(f"  Slug: {empty_slug}")
    
    checks = [
        (isinstance(layer, folium.GeoJson), "Layer is GeoJson"),
        (slug == 'owner_smith_properties', "Correct slug generated"),
        (isinstance(empty_layer, folium.FeatureGroup), "Empty layer is FeatureGroup"),
        (layer is not None, "Layer created"),
        (empty_layer is not None, "Empty layer created")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Owner layer creation successful")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_all_owner_layers():
    """Test creating all owner layers"""
    print_section("TEST 4: All Owner Layers")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'BROWN HOLDINGS']
    
    builder = LayerBuilder(gdf, target_owners)
    layers = builder.build_all_owner_layers()
    
    print(f"Created {len(layers)} owner layers:")
    for slug, layer in layers.items():
        print(f"  {slug}: {type(layer).__name__}")
    
    checks = [
        (len(layers) == 3, "Created 3 layers"),
        ('owner_smith_properties' in layers, "SMITH PROPERTIES layer exists"),
        ('owner_jones_investments' in layers, "JONES INVESTMENTS layer exists"),
        ('owner_brown_holdings' in layers, "BROWN HOLDINGS layer exists"),
        (all(isinstance(l, (folium.GeoJson, folium.FeatureGroup)) for l in layers.values()), "All valid Folium objects")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: All owner layers created successfully")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_zip_layer():
    """Test ZIP code layer creation"""
    print_section("TEST 5: ZIP Code Layer")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'BROWN HOLDINGS']
    
    builder = LayerBuilder(gdf, target_owners)
    
    # Test ZIP layer with parcels
    layer, layer_id = builder.build_zip_layer('44102')
    
    print(f"ZIP layer for 44102:")
    print(f"  Type: {type(layer).__name__}")
    print(f"  Layer ID: {layer_id}")
    
    # Test ZIP layer with no parcels
    empty_layer, empty_id = builder.build_zip_layer('99999')
    
    print(f"\nEmpty ZIP layer (99999):")
    print(f"  Layer: {empty_layer}")
    print(f"  Layer ID: {empty_id}")
    
    checks = [
        (layer is not None, "Layer created for valid ZIP"),
        (isinstance(layer, folium.GeoJson), "Layer is GeoJson"),
        (layer_id == 'zip_44102', "Correct layer ID"),
        (empty_layer is None, "No layer for nonexistent ZIP"),
        (empty_id == 'zip_99999', "Correct empty layer ID")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: ZIP layer creation successful")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_all_zip_layers():
    """Test creating all ZIP layers"""
    print_section("TEST 6: All ZIP Layers")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS']
    
    builder = LayerBuilder(gdf, target_owners)
    zip_layers = builder.build_all_zip_layers()
    
    print(f"Created {len(zip_layers)} ZIP layers:")
    for layer_id, layer in zip_layers.items():
        print(f"  {layer_id}: {type(layer).__name__}")
    
    zip_codes = builder.get_zip_codes()
    print(f"\nZIP codes in data: {zip_codes}")
    
    checks = [
        (len(zip_layers) == 2, "Created 2 ZIP layers"),
        ('zip_44102' in zip_layers, "ZIP 44102 layer exists"),
        ('zip_44103' in zip_layers, "ZIP 44103 layer exists"),
        (len(zip_codes) == 2, "Detected 2 ZIP codes"),
        (all(isinstance(l, folium.GeoJson) for l in zip_layers.values()), "All valid GeoJson objects")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: All ZIP layers created successfully")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_complete_pipeline():
    """Test building all layers at once"""
    print_section("TEST 7: Complete Pipeline")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'BROWN HOLDINGS']
    
    builder = LayerBuilder(gdf, target_owners)
    result = builder.build_all_layers()
    
    print("Built all layers:")
    print(f"  Base layer: {type(result.get('base')).__name__ if result.get('base') else 'None'}")
    print(f"  Owner layers: {len(result.get('owners', {}))}")
    print(f"  ZIP layers: {len(result.get('zips', {}))}")
    print(f"  Owner colors: {len(result.get('owner_colors', {}))}")
    print(f"  ZIP codes: {result.get('zip_codes', [])}")
    
    checks = [
        ('base' in result, "Base layer included"),
        ('owners' in result, "Owner layers included"),
        ('zips' in result, "ZIP layers included"),
        ('owner_colors' in result, "Owner colors included"),
        ('zip_codes' in result, "ZIP codes included"),
        (len(result['owners']) == 3, "3 owner layers created"),
        (len(result['zips']) == 2, "2 ZIP layers created"),
        (isinstance(result['base'], (folium.GeoJson, folium.FeatureGroup)), "Valid base layer")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Complete pipeline working")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_convenience_function():
    """Test convenience function"""
    print_section("TEST 8: Convenience Function")
    
    gdf = create_sample_geodataframe()
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS']
    
    print("Using build_layers_from_data() convenience function")
    
    result = build_layers_from_data(gdf, target_owners)
    
    print(f"\nResults:")
    print(f"  Owner layers: {len(result.get('owners', {}))}")
    print(f"  ZIP layers: {len(result.get('zips', {}))}")
    
    checks = [
        ('base' in result, "Has base layer"),
        ('owners' in result, "Has owner layers"),
        ('zips' in result, "Has ZIP layers"),
        (len(result['owners']) == 2, "Correct number of owner layers"),
        (len(result['zips']) == 2, "Correct number of ZIP layers")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Convenience function working")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_empty_data():
    """Test handling of empty GeoDataFrame"""
    print_section("TEST 9: Empty Data Handling")
    
    # Create empty GeoDataFrame
    gdf = gpd.GeoDataFrame(columns=['parcelpin', 'owner_clean', 'geometry'], crs="EPSG:4326")
    target_owners = ['SMITH PROPERTIES']
    
    print("Testing with empty GeoDataFrame")
    
    try:
        builder = LayerBuilder(gdf, target_owners)
        
        base = builder.build_base_layer()
        owners = builder.build_all_owner_layers()
        zips = builder.build_all_zip_layers()
        
        print(f"\nEmpty data handling:")
        print(f"  Base layer: {type(base).__name__}")
        print(f"  Owner layers: {len(owners)}")
        print(f"  ZIP layers: {len(zips)}")
        
        checks = [
            (base is not None, "Base layer created (empty)"),
            (len(owners) == 1, "Owner layer created"),
            (len(zips) == 0, "No ZIP layers for empty data"),
            (isinstance(base, folium.FeatureGroup), "Base is FeatureGroup for empty data")
        ]
        
        print("\n📋 Validation Checks:")
        all_passed = True
        for passed, description in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {description}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ PASS: Empty data handled gracefully")
            return True
        else:
            print("\n❌ FAIL: Some checks failed")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL: Error with empty data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  LAYER BUILDER TEST SUITE")
    print("="*60)
    
    tests = [
        ("Initialization", test_initialization),
        ("Base Context Layer", test_base_layer),
        ("Single Owner Layer", test_owner_layer),
        ("All Owner Layers", test_all_owner_layers),
        ("ZIP Code Layer", test_zip_layer),
        ("All ZIP Layers", test_all_zip_layers),
        ("Complete Pipeline", test_complete_pipeline),
        ("Convenience Function", test_convenience_function),
        ("Empty Data Handling", test_empty_data)
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
        print("🎉 ALL TESTS PASSED! Layer Builder is working correctly.\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

