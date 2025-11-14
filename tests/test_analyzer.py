"""
Test script for data_processing/analyzer.py
Tests portfolio analysis, owner statistics, and aggregations
"""

import sys
from pathlib import Path
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_processing.analyzer import PortfolioAnalyzer, analyze_target_owners


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def create_sample_data():
    """Create sample property data for testing"""
    data = {
        'parcelpin': [
            '123-456', '123-457', '123-458', '123-459', '123-460',
            '123-461', '123-462', '123-463', '123-464', '123-465'
        ],
        'owner_clean': [
            'SMITH PROPERTIES', 'SMITH PROPERTIES', 'SMITH PROPERTIES',
            'JONES INVESTMENTS', 'JONES INVESTMENTS',
            'BROWN HOLDINGS', 'BROWN HOLDINGS',
            'WILSON REAL ESTATE',
            'OTHER OWNER', 'OTHER OWNER'  # Not in target list
        ],
        'sales_amount': [
            250000, 180000, 320000,
            275000, 190000,
            400000, 350000,
            220000,
            150000, 160000
        ],
        'certified_tax_total': [
            3500, 2800, 4200,
            3800, 2600,
            5200, 4500,
            3100,
            2200, 2400
        ],
        'par_zip': [
            '44102', '44102', '44103',
            '44103', '44104',
            '44102', '44103',
            '44104',
            '44102', '44103'
        ],
        'address': [
            '123 Main St', '456 Main St', '789 Oak Ave',
            '321 Elm St', '654 Maple Ln',
            '111 Pine St', '222 Cedar Ave',
            '333 Birch Dr',
            '444 Spruce Rd', '555 Willow Way'
        ]
    }
    
    df = pd.DataFrame(data)
    target_owners = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'BROWN HOLDINGS', 'WILSON REAL ESTATE']
    
    return df, target_owners


def test_filter_to_targets():
    """Test filtering data to target owners"""
    print_section("TEST 1: Filter to Target Owners")
    
    df, target_owners = create_sample_data()
    analyzer = PortfolioAnalyzer()
    
    print(f"Original data: {len(df)} properties")
    print(f"Target owners ({len(target_owners)}): {target_owners}")
    
    filtered = analyzer.filter_to_targets(df, target_owners)
    
    print(f"\nFiltered data: {len(filtered)} properties")
    print(f"Owners in filtered data: {filtered['owner_clean'].unique().tolist()}")
    
    # Should have 8 properties (10 total - 2 OTHER OWNER = 8)
    expected_count = 8
    
    checks = [
        (len(filtered) == expected_count, f"Expected {expected_count} properties, got {len(filtered)}"),
        ('OTHER OWNER' not in filtered['owner_clean'].values, "OTHER OWNER excluded"),
        (all(filtered['owner_clean'].isin(target_owners)), "All owners are in target list")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Filtering successful")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_owner_stats():
    """Test individual owner statistics calculation"""
    print_section("TEST 2: Owner Statistics")
    
    df, target_owners = create_sample_data()
    analyzer = PortfolioAnalyzer()
    
    # Test stats for SMITH PROPERTIES
    owner = 'SMITH PROPERTIES'
    stats = analyzer.calculate_owner_stats(df, owner)
    
    print(f"Statistics for: {owner}\n")
    print(f"  Properties: {stats['count']}")
    print(f"  Total Sales: ${stats['total_sales']:,.0f}")
    print(f"  Avg Sales: ${stats['avg_sales']:,.0f}")
    print(f"  Total Assessment: ${stats['total_assess']:,.0f}")
    print(f"  Avg Assessment: ${stats['avg_assess']:,.0f}")
    
    if not stats['zip_table'].empty:
        print(f"\n  ZIP Code Breakdown:")
        print(stats['zip_table'].to_string(index=False))
    
    # SMITH PROPERTIES should have 3 properties
    expected_count = 3
    expected_total_sales = 250000 + 180000 + 320000  # 750000
    
    checks = [
        (stats['count'] == expected_count, f"Expected {expected_count} properties"),
        (stats['total_sales'] == expected_total_sales, f"Expected ${expected_total_sales:,} total sales"),
        (stats['avg_sales'] == expected_total_sales / expected_count, "Correct average sales"),
        (not stats['zip_table'].empty, "ZIP table generated"),
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Owner stats calculated correctly")
        return True
    else:
        print("\n❌ FAIL: Some calculations incorrect")
        return False


def test_all_owner_stats():
    """Test statistics for all target owners"""
    print_section("TEST 3: All Owner Statistics")
    
    df, target_owners = create_sample_data()
    analyzer = PortfolioAnalyzer()
    
    all_stats = analyzer.calculate_all_owner_stats(df, target_owners)
    
    print(f"Calculated stats for {len(all_stats)} owners:\n")
    
    for owner, stats in all_stats.items():
        print(f"  {owner}:")
        print(f"    Properties: {stats['count']}")
        print(f"    Total Sales: ${stats['total_sales']:,.0f}")
        print(f"    Avg Sales: ${stats['avg_sales']:,.0f}\n")
    
    total_properties = sum(s['count'] for s in all_stats.values())
    print(f"Total properties across all owners: {total_properties}")
    
    checks = [
        (len(all_stats) == len(target_owners), "Stats for all target owners"),
        (all_stats['SMITH PROPERTIES']['count'] == 3, "SMITH PROPERTIES: 3 properties"),
        (all_stats['JONES INVESTMENTS']['count'] == 2, "JONES INVESTMENTS: 2 properties"),
        (all_stats['BROWN HOLDINGS']['count'] == 2, "BROWN HOLDINGS: 2 properties"),
        (all_stats['WILSON REAL ESTATE']['count'] == 1, "WILSON REAL ESTATE: 1 property"),
        (total_properties == 8, "Total count correct")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: All owner stats calculated correctly")
        return True
    else:
        print("\n❌ FAIL: Some calculations incorrect")
        return False


def test_aggregate_stats():
    """Test aggregate statistics calculation"""
    print_section("TEST 4: Aggregate Statistics")
    
    df, target_owners = create_sample_data()
    analyzer = PortfolioAnalyzer()
    
    # Filter to targets first
    filtered = analyzer.filter_to_targets(df, target_owners)
    
    # Calculate aggregate stats
    agg_stats = analyzer.calculate_aggregate_stats(filtered)
    
    print("Aggregate Statistics:\n")
    print(f"  Total Properties: {agg_stats['count']}")
    print(f"  Unique Owners: {agg_stats['unique_owners']}")
    print(f"  Total Sales: ${agg_stats['total_sales']:,.0f}")
    print(f"  Avg Sales: ${agg_stats['avg_sales']:,.0f}")
    print(f"  Total Assessment: ${agg_stats['total_assess']:,.0f}")
    print(f"  Avg Assessment: ${agg_stats['avg_assess']:,.0f}")
    
    if not agg_stats['zip_table'].empty:
        print(f"\n  ZIP Code Breakdown:")
        print(agg_stats['zip_table'].to_string(index=False))
    
    # Calculate expected values
    expected_count = 8
    expected_owners = 4
    # Sales: 250k + 180k + 320k + 275k + 190k + 400k + 350k + 220k = 2,185,000
    expected_total_sales = 2185000
    
    checks = [
        (agg_stats['count'] == expected_count, f"Expected {expected_count} properties"),
        (agg_stats['unique_owners'] == expected_owners, f"Expected {expected_owners} unique owners"),
        (agg_stats['total_sales'] == expected_total_sales, f"Expected ${expected_total_sales:,} total sales"),
        (not agg_stats['zip_table'].empty, "ZIP breakdown generated")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Aggregate stats calculated correctly")
        return True
    else:
        print("\n❌ FAIL: Some calculations incorrect")
        return False


def test_full_analysis():
    """Test complete portfolio analysis pipeline"""
    print_section("TEST 5: Full Portfolio Analysis")
    
    df, target_owners = create_sample_data()
    analyzer = PortfolioAnalyzer()
    
    print(f"Running portfolio analysis...")
    print(f"  Input: {len(df)} properties")
    print(f"  Targets: {len(target_owners)} owners\n")
    
    results = analyzer.analyze_portfolio(df, target_owners)
    
    print("Analysis Results:\n")
    print(f"  Target owner count: {results['target_owner_count']}")
    print(f"  Properties found: {results['properties_found']}")
    print(f"  Unique owners: {results['aggregate']['unique_owners']}")
    print(f"  Total sales value: ${results['aggregate']['total_sales']:,.0f}")
    
    print(f"\n  Per-Owner Breakdown:")
    for owner, stats in results['owner_stats'].items():
        print(f"    {owner}: {stats['count']} properties, ${stats['total_sales']:,.0f}")
    
    # Generate summary table
    summary = analyzer.get_summary_table(results['owner_stats'])
    print(f"\n  Summary Table ({len(summary)} rows):")
    print(summary.to_string(index=False))
    
    checks = [
        (results['target_owner_count'] == 4, "Correct target owner count"),
        (results['properties_found'] == 8, "Correct properties found"),
        (len(results['owner_stats']) == 4, "Stats for all owners"),
        (results['aggregate']['count'] == 8, "Aggregate count correct"),
        (not summary.empty, "Summary table generated"),
        (len(summary) == 4, "Summary has all owners")
    ]
    
    print("\n📋 Validation Checks:")
    all_passed = True
    for passed, description in checks:
        status = "✓" if passed else "✗"
        print(f"  {status} {description}")
        if not passed:
            all_passed = False
    
    if all_passed:
        print("\n✅ PASS: Full analysis pipeline works correctly!")
        return True
    else:
        print("\n❌ FAIL: Some checks failed")
        return False


def test_convenience_function():
    """Test the convenience function"""
    print_section("TEST 6: Convenience Function")
    
    df, target_owners = create_sample_data()
    
    print(f"Using analyze_target_owners() convenience function\n")
    
    results = analyze_target_owners(df, target_owners)
    
    print(f"Results:")
    print(f"  Properties found: {results['properties_found']}")
    print(f"  Total sales: ${results['aggregate']['total_sales']:,.0f}")
    
    if results['properties_found'] == 8 and results['target_owner_count'] == 4:
        print("\n✅ PASS: Convenience function works")
        return True
    else:
        print("\n❌ FAIL: Unexpected results")
        return False


def test_empty_data():
    """Test handling of empty data"""
    print_section("TEST 7: Empty Data Handling")
    
    df = pd.DataFrame(columns=['parcelpin', 'owner_clean', 'sales_amount', 'certified_tax_total', 'par_zip'])
    target_owners = ['SMITH PROPERTIES']
    
    analyzer = PortfolioAnalyzer()
    
    print("Testing with empty DataFrame...")
    
    try:
        filtered = analyzer.filter_to_targets(df, target_owners)
        print(f"  Filtered: {len(filtered)} properties")
        
        agg_stats = analyzer.calculate_aggregate_stats(filtered)
        print(f"  Aggregate count: {agg_stats['count']}")
        print(f"  Unique owners: {agg_stats['unique_owners']}")
        
        # Test analyze_portfolio with empty data
        results = analyzer.analyze_portfolio(df, target_owners)
        print(f"  Portfolio properties found: {results['properties_found']}")
        
        checks = [
            (agg_stats['count'] == 0, "Aggregate count is 0"),
            (len(filtered) == 0, "Filtered data is empty"),
            (results['properties_found'] == 0, "No properties found in full analysis"),
            (agg_stats['total_sales'] == 0.0, "Total sales is 0"),
            (agg_stats['total_assess'] == 0.0, "Total assessment is 0")
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
            print("\n❌ FAIL: Unexpected behavior with empty data")
            return False
            
    except Exception as e:
        print(f"\n❌ FAIL: Error with empty data: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  PORTFOLIO ANALYZER TEST SUITE")
    print("="*60)
    
    tests = [
        ("Filter to Target Owners", test_filter_to_targets),
        ("Owner Statistics", test_owner_stats),
        ("All Owner Statistics", test_all_owner_stats),
        ("Aggregate Statistics", test_aggregate_stats),
        ("Full Portfolio Analysis", test_full_analysis),
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
        print("🎉 ALL TESTS PASSED! Portfolio Analyzer is working correctly.\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

