"""
Test script for data_processing/normalizer.py
Tests column normalization and owner cleaning functions
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from data_processing.normalizer import (
    normalize_columns,
    clean_owner,
    validate_required_columns,
    apply_owner_cleaning,
    normalize_parcel_data,
    PARCEL_REQUIRED_COLUMNS
)


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")


def test_normalize_columns():
    """Test column normalization with various column name formats"""
    print_section("TEST 1: Column Normalization")
    
    # Create sample data with various column name formats
    # (simulating Cleveland data structure)
    test_data = pd.DataFrame({
        'PARCELPIN': ['123-456-789', '987-654-321'],
        'DEEDED_OWN': ['Smith Properties, LLC.', 'Jones Investments Inc'],
        'TAX_LUC_DE': ['1-FAMILY PLATTED LOT', '2-FAMILY PLATTED LOT'],
        'PAR_ADDR_ALL': ['123 Main St', '456 Oak Ave'],
        'SALES_AMOU': [250000, 180000],
        'CERTIFIED_TAX_TOTAL': [3500, 2800],
        'PAR_ZIP': ['44102', '44103']
    })
    
    print("BEFORE normalization:")
    print(f"Columns: {test_data.columns.tolist()}\n")
    print(test_data.head())
    
    # Normalize
    normalized = normalize_columns(test_data)
    
    print("\n\nAFTER normalization:")
    print(f"Columns: {normalized.columns.tolist()}\n")
    print(normalized.head())
    
    # Verify expected columns exist
    expected = ['parcelpin', 'deeded_owner', 'tax_luc_description', 'par_addr', 'sales_amount']
    found = [col for col in expected if col in normalized.columns]
    
    print(f"\n✓ Expected columns found: {len(found)}/{len(expected)}")
    print(f"  Found: {found}")
    
    if len(found) == len(expected):
        print("  ✅ PASS: All expected columns normalized correctly")
        return True
    else:
        print("  ❌ FAIL: Some columns missing")
        return False


def test_clean_owner():
    """Test owner name cleaning with various formats"""
    print_section("TEST 2: Owner Name Cleaning")
    
    # Test cases with expected results
    test_cases = [
        ("Smith Properties, LLC.", "SMITH PROPERTIES"),
        ("JONES INVESTMENTS INC", "JONES INVESTMENTS"),
        ("Brown & Associates Co.", "BROWN & ASSOCIATES"),
        ("Wilson Real Estate Corp", "WILSON REAL ESTATE"),
        ("Davis Holdings, Ltd.", "DAVIS HOLDINGS"),
        (None, "UNKNOWN"),
        ("", ""),
        ("multiple   spaces", "MULTIPLE SPACES"),
    ]
    
    print("Testing owner name cleaning:\n")
    
    all_passed = True
    for input_name, expected in test_cases:
        result = clean_owner(input_name)
        passed = result == expected
        status = "✓" if passed else "✗"
        
        print(f"{status} Input:    '{input_name}'")
        print(f"  Expected: '{expected}'")
        print(f"  Got:      '{result}'")
        
        if not passed:
            all_passed = False
            print(f"  ❌ MISMATCH!")
        print()
    
    if all_passed:
        print("✅ PASS: All owner names cleaned correctly")
        return True
    else:
        print("❌ FAIL: Some owner names not cleaned properly")
        return False


def test_validate_required_columns():
    """Test column validation function"""
    print_section("TEST 3: Column Validation")
    
    # Test with all required columns present
    valid_df = pd.DataFrame({
        'parcelpin': ['123'],
        'deeded_owner': ['Smith']
    })
    
    is_valid, error_msg = validate_required_columns(valid_df, PARCEL_REQUIRED_COLUMNS)
    
    print("Test 3a: Valid DataFrame")
    print(f"  Columns: {valid_df.columns.tolist()}")
    print(f"  Required: {PARCEL_REQUIRED_COLUMNS}")
    print(f"  Result: is_valid={is_valid}, error_msg={error_msg}")
    
    if is_valid:
        print("  ✅ PASS: Valid DataFrame accepted\n")
        test_3a = True
    else:
        print("  ❌ FAIL: Valid DataFrame rejected\n")
        test_3a = False
    
    # Test with missing columns
    invalid_df = pd.DataFrame({
        'parcelpin': ['123'],
        # Missing deeded_owner
    })
    
    is_valid, error_msg = validate_required_columns(invalid_df, PARCEL_REQUIRED_COLUMNS)
    
    print("Test 3b: Invalid DataFrame (missing columns)")
    print(f"  Columns: {invalid_df.columns.tolist()}")
    print(f"  Required: {PARCEL_REQUIRED_COLUMNS}")
    print(f"  Result: is_valid={is_valid}")
    print(f"  Error: {error_msg}")
    
    if not is_valid and error_msg:
        print("  ✅ PASS: Invalid DataFrame correctly rejected\n")
        test_3b = True
    else:
        print("  ❌ FAIL: Invalid DataFrame not detected\n")
        test_3b = False
    
    return test_3a and test_3b


def test_apply_owner_cleaning():
    """Test applying owner cleaning to entire DataFrame"""
    print_section("TEST 4: Apply Owner Cleaning to DataFrame")
    
    # Create sample data
    df = pd.DataFrame({
        'parcelpin': ['123', '456', '789'],
        'deeded_owner': [
            'Smith Properties, LLC.',
            'Jones Investments Inc',
            'Wilson Real Estate Co.'
        ]
    })
    
    print("BEFORE applying owner cleaning:")
    print(df)
    
    # Apply cleaning
    result = apply_owner_cleaning(df)
    
    print("\n\nAFTER applying owner cleaning:")
    print(result)
    
    # Check that owner_clean column was created
    if 'owner_clean' in result.columns:
        print("\n✓ 'owner_clean' column created")
        
        # Check that cleaning worked
        expected_cleaned = ['SMITH PROPERTIES', 'JONES INVESTMENTS', 'WILSON REAL ESTATE']
        actual_cleaned = result['owner_clean'].tolist()
        
        print(f"\nExpected: {expected_cleaned}")
        print(f"Got:      {actual_cleaned}")
        
        if actual_cleaned == expected_cleaned:
            print("\n✅ PASS: Owner cleaning applied correctly")
            return True
        else:
            print("\n❌ FAIL: Cleaning results don't match expected")
            return False
    else:
        print("\n❌ FAIL: 'owner_clean' column not created")
        return False


def test_full_pipeline():
    """Test the complete normalization pipeline"""
    print_section("TEST 5: Full Normalization Pipeline")
    
    # Create data that simulates Cleveland raw data structure
    raw_data = pd.DataFrame({
        'PARCELPIN': ['123-456-789', '987-654-321', '111-222-333'],
        'DEEDED_OWN': [
            'Cleveland Properties, LLC.',
            'Ohio Real Estate Inc',
            'Lake Investments Co.'
        ],
        'TAX_LUC_DE': [
            '1-FAMILY PLATTED LOT',
            '2-FAMILY PLATTED LOT',
            '1-FAMILY PLATTED LOT'
        ],
        'PAR_ADDR_A': ['123 Main St', '456 Oak Ave', '789 Elm St'],
        'SALES_AMOU': [250000, 180000, 320000],
        'CERTIFIED_TAX_TOTAL': [3500, 2800, 4200],
        'PAR_ZIP': ['44102', '44103', '44104']
    })
    
    print("RAW DATA (simulating Cleveland format):")
    print(f"Columns: {raw_data.columns.tolist()}\n")
    print(raw_data)
    
    # Apply full pipeline
    normalized = normalize_parcel_data(raw_data, clean_owners=True)
    
    print("\n\nNORMALIZED DATA (ready for database):")
    print(f"Columns: {normalized.columns.tolist()}\n")
    print(normalized)
    
    # Verify all transformations
    checks = [
        ('parcelpin' in normalized.columns, "parcelpin column exists"),
        ('deeded_owner' in normalized.columns, "deeded_owner column exists"),
        ('owner_clean' in normalized.columns, "owner_clean column created"),
        ('tax_luc_description' in normalized.columns, "tax_luc_description normalized"),
        (normalized['owner_clean'].iloc[0] == 'CLEVELAND PROPERTIES', "Owner names cleaned correctly"),
        (all(normalized.columns == normalized.columns.str.lower()), "All columns lowercase")
    ]
    
    print("\n\nValidation Checks:")
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


def run_all_tests():
    """Run all tests and report results"""
    print("\n" + "="*60)
    print("  NORMALIZER TEST SUITE")
    print("="*60)
    
    tests = [
        ("Column Normalization", test_normalize_columns),
        ("Owner Name Cleaning", test_clean_owner),
        ("Column Validation", test_validate_required_columns),
        ("Apply Owner Cleaning", test_apply_owner_cleaning),
        ("Full Pipeline", test_full_pipeline)
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
        print("🎉 ALL TESTS PASSED! Normalizer is working correctly.\n")
        return True
    else:
        print(f"⚠️  {total - passed} test(s) failed. Review errors above.\n")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

