"""
Test script for data_processing/csv_processor.py
Tests CSV loading, processing, and validation
"""

import sys
from pathlib import Path
import tempfile
import pandas as pd

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_processing.csv_processor import CSVProcessor, process_csv_file


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def create_sample_csv():
    """Create a temporary CSV file with sample Cleveland-style data"""
    # Sample data mimicking Cleveland format
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
        'SALES_AMOU': [
            '250000',
            '180000',
            '320000',
            'N/A',  # Should convert to 0
            '275000'
        ],
        'CERTIFIED_TAX_TOTAL': [
            3500,
            2800,
            4200,
            5000,
            3800
        ],
        'PAR_ZIP': [
            '44102',
            '44103',
            '44104',
            '44105',
            '44102'
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary CSV file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.csv',
        delete=False,
        newline=''
    )
    df.to_csv(temp_file.name, index=False)
    temp_file.close()
    
    return temp_file.name, df


def test_csv_loading():
    """Test basic CSV loading"""
    print_section("TEST 1: CSV Loading")
    
    csv_file, original_df = create_sample_csv()
    
    try:
        processor = CSVProcessor()
        
        print(f"Loading CSV from: {csv_file}")
        df = processor.load_csv(csv_file)
        
        print(f"\nLoaded {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {df.columns.tolist()}")
        
        if len(df) == len(original_df):
            print("\n✅ PASS: All rows loaded successfully")
            return True
        else:
            print(f"\n❌ FAIL: Expected {len(original_df)} rows, got {len(df)}")
            return False
            
    finally:
        # Cleanup
        Path(csv_file).unlink()


def test_normalization():
    """Test data normalization"""
    print_section("TEST 2: Data Normalization")
    
    csv_file, _ = create_sample_csv()
    
    try:
        processor = CSVProcessor()
        df = processor.load_csv(csv_file)
        
        print("BEFORE normalization:")
        print(f"Columns: {df.columns.tolist()}\n")
        print(df.head(2))
        
        normalized = processor.normalize_data(df)
        
        print("\n\nAFTER normalization:")
        print(f"Columns: {normalized.columns.tolist()}\n")
        print(normalized.head(2))
        
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
        Path(csv_file).unlink()


def test_property_type_filtering():
    """Test filtering by property type"""
    print_section("TEST 3: Property Type Filtering")
    
    csv_file, original_df = create_sample_csv()
    
    try:
        processor = CSVProcessor()
        df = processor.load_csv(csv_file)
        normalized = processor.normalize_data(df)
        
        print(f"Before filtering: {len(normalized)} rows")
        print(f"Property types: {normalized['tax_luc_description'].value_counts().to_dict()}")
        
        filtered = processor.filter_by_property_type(normalized)
        
        print(f"\nAfter filtering: {len(filtered)} rows")
        print(f"Property types: {filtered['tax_luc_description'].value_counts().to_dict()}")
        
        # Should have 4 rows (1 COMMERCIAL filtered out)
        expected_rows = 4
        if len(filtered) == expected_rows:
            print(f"\n✅ PASS: Correctly filtered to {expected_rows} residential properties")
            return True
        else:
            print(f"\n❌ FAIL: Expected {expected_rows} rows, got {len(filtered)}")
            return False
            
    finally:
        Path(csv_file).unlink()


def test_numeric_conversion():
    """Test numeric column conversion"""
    print_section("TEST 4: Numeric Column Conversion")
    
    csv_file, _ = create_sample_csv()
    
    try:
        processor = CSVProcessor()
        df = processor.load_csv(csv_file)
        normalized = processor.normalize_data(df)
        
        print("BEFORE numeric conversion:")
        print(f"sales_amount dtype: {normalized['sales_amount'].dtype}")
        print(f"Sample values: {normalized['sales_amount'].head().tolist()}\n")
        
        converted = processor.coerce_numeric_columns(normalized)
        
        print("AFTER numeric conversion:")
        print(f"sales_amount dtype: {converted['sales_amount'].dtype}")
        print(f"Sample values: {converted['sales_amount'].head().tolist()}")
        
        # Check that N/A was converted to 0
        if converted['sales_amount'].iloc[3] == 0:
            print("\n✓ Invalid value ('N/A') correctly converted to 0")
        
        # Check dtype is numeric
        if pd.api.types.is_numeric_dtype(converted['sales_amount']):
            print("\n✅ PASS: Numeric conversion successful")
            return True
        else:
            print("\n❌ FAIL: Column not properly converted to numeric")
            return False
            
    finally:
        Path(csv_file).unlink()


def test_full_pipeline():
    """Test the complete CSV processing pipeline"""
    print_section("TEST 5: Full Processing Pipeline")
    
    csv_file, original_df = create_sample_csv()
    
    try:
        print(f"Processing CSV: {csv_file}")
        print(f"Original data: {len(original_df)} rows\n")
        
        # Process using the pipeline
        processor = CSVProcessor()
        processed = processor.process_csv(
            csv_file,
            filter_property_types=True
        )
        
        print(f"\nProcessed data: {len(processed)} rows")
        print(f"Columns: {processed.columns.tolist()}")
        
        # Get summary
        summary = processor.get_data_summary(processed)
        
        print("\n📊 Data Summary:")
        print(f"  Total rows: {summary['total_rows']}")
        print(f"  Total columns: {summary['total_columns']}")
        print(f"  Unique owners: {summary['unique_owners']}")
        print(f"  Memory usage: {summary['memory_usage_mb']:.2f} MB")
        
        if 'property_types' in summary:
            print(f"  Property types: {summary['property_types']}")
        
        if 'total_sales_amount' in summary:
            print(f"  Total sales: ${summary['total_sales_amount']:,.0f}")
            print(f"  Avg sales: ${summary['avg_sales_amount']:,.0f}")
        
        # Validation checks
        checks = [
            (len(processed) == 4, "Correct number of rows after filtering"),
            ('owner_clean' in processed.columns, "owner_clean column exists"),
            ('parcelpin' in processed.columns, "parcelpin column exists"),
            (pd.api.types.is_numeric_dtype(processed['sales_amount']), "sales_amount is numeric"),
            (summary['unique_owners'] == 4, "Correct number of unique owners")
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
        Path(csv_file).unlink()


def test_convenience_function():
    """Test the convenience function"""
    print_section("TEST 6: Convenience Function")
    
    csv_file, _ = create_sample_csv()
    
    try:
        print(f"Using process_csv_file() convenience function\n")
        
        # Process using convenience function
        df = process_csv_file(csv_file)
        
        print(f"Processed {len(df)} rows")
        print(f"Columns: {df.columns.tolist()}")
        
        if len(df) == 4 and 'owner_clean' in df.columns:
            print("\n✅ PASS: Convenience function works")
            return True
        else:
            print("\n❌ FAIL: Unexpected results")
            return False
            
    finally:
        Path(csv_file).unlink()


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  CSV PROCESSOR TEST SUITE")
    print("="*60)
    
    tests = [
        ("CSV Loading", test_csv_loading),
        ("Data Normalization", test_normalization),
        ("Property Type Filtering", test_property_type_filtering),
        ("Numeric Conversion", test_numeric_conversion),
        ("Full Pipeline", test_full_pipeline),
        ("Convenience Function", test_convenience_function)
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
        print("🎉 ALL TESTS PASSED! CSV Processor is working correctly.\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

