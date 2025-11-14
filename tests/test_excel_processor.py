"""
Test script for data_processing/excel_processor.py
Tests Excel loading, owner extraction, and validation
"""

import sys
from pathlib import Path
import tempfile
import pandas as pd
import time
import gc

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from data_processing.excel_processor import ExcelProcessor, process_owner_list_file


def safe_delete_file(file_path, max_attempts=3):
    """Safely delete a file with retry logic for Windows file locking"""
    for attempt in range(max_attempts):
        try:
            gc.collect()  # Force garbage collection
            time.sleep(0.1)  # Small delay
            Path(file_path).unlink()
            return
        except PermissionError:
            if attempt < max_attempts - 1:
                time.sleep(0.2)
            else:
                print(f"  ⚠️  Warning: Could not delete temp file (file in use)")
                return


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def create_sample_excel():
    """Create a temporary Excel file with sample owner data"""
    # Sample data mimicking Cleveland owner list format
    data = {
        'Owner': [
            'Smith Properties, LLC.',
            'Jones Investments Inc',
            'Brown Holdings Co.',
            'Wilson Real Estate Corp',
            'Smith Properties, LLC.',  # Duplicate
            'Davis Properties, Ltd.',
            '',  # Empty value (use empty string instead of None)
        ]
    }
    
    df = pd.DataFrame(data)
    
    # Create temporary Excel file
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.xlsx',
        delete=False
    )
    temp_file.close()
    
    # Write to Excel using ExcelWriter to ensure proper closing
    with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Target Owners', index=False)
    
    return temp_file.name, df


def create_multisheet_excel():
    """Create an Excel file with multiple sheets"""
    owners_df = pd.DataFrame({
        'owner_name': ['Company A LLC', 'Company B Inc', 'Company C Corp']
    })
    
    properties_df = pd.DataFrame({
        'address': ['123 Main St', '456 Oak Ave'],
        'value': [250000, 180000]
    })
    
    temp_file = tempfile.NamedTemporaryFile(
        mode='w',
        suffix='.xlsx',
        delete=False
    )
    temp_file.close()
    
    # Write multiple sheets
    with pd.ExcelWriter(temp_file.name, engine='openpyxl') as writer:
        owners_df.to_excel(writer, sheet_name='Owners', index=False)
        properties_df.to_excel(writer, sheet_name='Properties', index=False)
    
    return temp_file.name


def test_excel_loading():
    """Test basic Excel loading"""
    print_section("TEST 1: Excel Loading")
    
    excel_file, original_df = create_sample_excel()
    
    try:
        processor = ExcelProcessor()
        
        print(f"Loading Excel from: {excel_file}")
        df = processor.load_excel(excel_file, sheet_name='Target Owners')
        
        print(f"\nLoaded {len(df)} rows, {len(df.columns)} columns")
        print(f"Columns: {df.columns.tolist()}")
        print(f"\nSample data:")
        print(df.head(3))
        
        # Note: pandas drops empty rows when writing Excel, so expect 6 rows not 7
        expected_rows = 6
        if len(df) == expected_rows:
            print(f"\n✅ PASS: Loaded {expected_rows} rows (empty rows filtered by pandas)")
            return True
        else:
            print(f"\n❌ FAIL: Expected {expected_rows} rows, got {len(df)}")
            return False
            
    finally:
        safe_delete_file(excel_file)


def test_list_sheets():
    """Test listing sheets in Excel file"""
    print_section("TEST 2: List Sheets")
    
    excel_file = create_multisheet_excel()
    
    try:
        processor = ExcelProcessor()
        
        sheets = processor.list_sheets(excel_file)
        
        print(f"Found {len(sheets)} sheets:")
        for sheet in sheets:
            print(f"  - {sheet}")
        
        expected_sheets = ['Owners', 'Properties']
        if all(s in sheets for s in expected_sheets):
            print("\n✅ PASS: All sheets found")
            return True
        else:
            print("\n❌ FAIL: Expected sheets not found")
            return False
            
    finally:
        safe_delete_file(excel_file)


def test_find_owner_column():
    """Test auto-detection of owner column"""
    print_section("TEST 3: Find Owner Column")
    
    excel_file, _ = create_sample_excel()
    
    try:
        processor = ExcelProcessor()
        df = processor.load_excel(excel_file, sheet_name='Target Owners')
        df = processor.normalize_columns(df)
        
        print(f"Columns in Excel: {df.columns.tolist()}")
        
        owner_col = processor.find_owner_column(df)
        
        print(f"Detected owner column: '{owner_col}'")
        
        if owner_col is not None:
            print("\n✅ PASS: Owner column detected")
            return True
        else:
            print("\n❌ FAIL: Could not detect owner column")
            return False
            
    finally:
        safe_delete_file(excel_file)


def test_extract_owners():
    """Test owner extraction and cleaning"""
    print_section("TEST 4: Extract Owners")
    
    excel_file, original_df = create_sample_excel()
    
    try:
        processor = ExcelProcessor()
        df = processor.load_excel(excel_file, sheet_name='Target Owners')
        df = processor.normalize_columns(df)
        
        print(f"Original data ({len(df)} rows):")
        print(df)
        
        owners = processor.extract_owners(
            df,
            clean=True,
            remove_duplicates=True,
            remove_empty=True
        )
        
        print(f"\nExtracted owners ({len(owners)}):")
        for i, owner in enumerate(owners, 1):
            print(f"  {i}. {owner}")
        
        # Should have 5 unique owners (7 rows - 1 duplicate - 1 null = 5)
        expected_count = 5
        
        # Check that owners are cleaned (no "LLC", "INC", etc.)
        sample_owner = owners[0]
        is_cleaned = "LLC" not in sample_owner and "INC" not in sample_owner
        
        checks = [
            (len(owners) == expected_count, f"Expected {expected_count} owners, got {len(owners)}"),
            (is_cleaned, "Owner names are cleaned"),
            (len(owners) == len(set(owners)), "No duplicates in list")
        ]
        
        print("\n📋 Validation Checks:")
        all_passed = True
        for passed, description in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {description}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ PASS: Owner extraction successful")
            return True
        else:
            print("\n❌ FAIL: Some checks failed")
            return False
            
    finally:
        safe_delete_file(excel_file)


def test_full_pipeline():
    """Test the complete owner list processing pipeline"""
    print_section("TEST 5: Full Processing Pipeline")
    
    excel_file, original_df = create_sample_excel()
    
    try:
        print(f"Processing Excel: {excel_file}")
        print(f"Original data: {len(original_df)} rows\n")
        
        processor = ExcelProcessor()
        owners = processor.process_owner_list(
            excel_file,
            sheet_name='Target Owners'
        )
        
        print(f"Processed owner list: {len(owners)} unique owners")
        print(f"\nOwners:")
        for i, owner in enumerate(owners, 1):
            print(f"  {i}. {owner}")
        
        # Validation checks
        checks = [
            (len(owners) == 5, "Correct number of owners"),
            (len(owners) == len(set(owners)), "No duplicates"),
            (all(isinstance(o, str) for o in owners), "All owners are strings"),
            (all(o.strip() == o for o in owners), "No leading/trailing whitespace")
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
        safe_delete_file(excel_file)


def test_convenience_function():
    """Test the convenience function"""
    print_section("TEST 6: Convenience Function")
    
    excel_file, _ = create_sample_excel()
    
    try:
        print(f"Using process_owner_list_file() convenience function\n")
        
        owners = process_owner_list_file(
            excel_file,
            sheet_name='Target Owners'
        )
        
        print(f"Loaded {len(owners)} owners:")
        for i, owner in enumerate(owners, 1):
            print(f"  {i}. {owner}")
        
        if len(owners) == 5 and isinstance(owners, list):
            print("\n✅ PASS: Convenience function works")
            return True
        else:
            print("\n❌ FAIL: Unexpected results")
            return False
            
    finally:
        safe_delete_file(excel_file)


def test_multiple_sheets():
    """Test loading multiple sheets"""
    print_section("TEST 7: Load Multiple Sheets")
    
    excel_file = create_multisheet_excel()
    
    try:
        processor = ExcelProcessor()
        
        sheets = processor.load_multiple_sheets(excel_file)
        
        print(f"Loaded {len(sheets)} sheets:")
        for name, df in sheets.items():
            print(f"  {name}: {len(df)} rows, {len(df.columns)} columns")
        
        if len(sheets) == 2 and 'Owners' in sheets and 'Properties' in sheets:
            print("\n✅ PASS: Multiple sheets loaded")
            return True
        else:
            print("\n❌ FAIL: Expected sheets not loaded")
            return False
            
    finally:
        safe_delete_file(excel_file)


def test_file_info():
    """Test getting file information"""
    print_section("TEST 8: File Information")
    
    excel_file, _ = create_sample_excel()
    
    try:
        processor = ExcelProcessor()
        
        info = processor.get_file_info(excel_file)
        
        print("📊 File Information:")
        print(f"  File name: {info['file_name']}")
        print(f"  File size: {info['file_size_mb']:.4f} MB")
        print(f"  Extension: {info['extension']}")
        print(f"  Sheet count: {info['sheet_count']}")
        print(f"  Sheets: {info['sheet_names']}")
        
        checks = [
            (info['extension'] == '.xlsx', "Correct extension"),
            (info['sheet_count'] == 1, "Correct sheet count"),
            ('Target Owners' in info['sheet_names'], "Sheet name found")
        ]
        
        print("\n📋 Validation Checks:")
        all_passed = True
        for passed, description in checks:
            status = "✓" if passed else "✗"
            print(f"  {status} {description}")
            if not passed:
                all_passed = False
        
        if all_passed:
            print("\n✅ PASS: File info correct")
            return True
        else:
            print("\n❌ FAIL: Some info incorrect")
            return False
            
    finally:
        safe_delete_file(excel_file)


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  EXCEL PROCESSOR TEST SUITE")
    print("="*60)
    
    tests = [
        ("Excel Loading", test_excel_loading),
        ("List Sheets", test_list_sheets),
        ("Find Owner Column", test_find_owner_column),
        ("Extract Owners", test_extract_owners),
        ("Full Pipeline", test_full_pipeline),
        ("Convenience Function", test_convenience_function),
        ("Multiple Sheets", test_multiple_sheets),
        ("File Information", test_file_info)
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
        print("🎉 ALL TESTS PASSED! Excel Processor is working correctly.\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

