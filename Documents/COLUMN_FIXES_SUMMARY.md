# Column Name Fixes - Summary

## Overview
Fixed column name inconsistencies throughout the mapping module to handle variations in parcel data schemas across different cities/sources.

## Changes Made

### 1. **layer_builder.py** - Added Dynamic Column Detection

#### New Method: `_detect_column_names()`
Added intelligent column detection that searches for common variations of column names:

```python
# Parcel PIN column
Searches: 'parcel_pin', 'parcelpin', 'parcel_id', 'pin', 'objectid'

# ZIP code column  
Searches: 'par_zip', 'zip', 'zip_code', 'zipcode'

# Sales amount column
Searches: 'sales_amount', 'sales_amou', 'sale_price', 'sales'

# Tax assessment column
Searches: 'certified_tax_total', 'tax_total', 'assessed_value', 'assessment'

# Owner column (required)
Must have: 'owner_clean'
```

#### Benefits:
- **Automatic adaptation** to different data schemas
- **Better error messages** when required columns are missing
- **Logging** of detected column names for debugging
- **Validation** that required columns exist

#### Updated Methods:
All methods now use instance variables instead of hardcoded column names:
- `self.parcel_pin_col` instead of `"parcel_pin"` or `"parcelpin"`
- `self.zip_col` instead of `"par_zip"`
- `self.sales_col` instead of `"sales_amount"` or `"sales_amou"`
- `self.assess_col` instead of `"certified_tax_total"`
- `self.owner_col` instead of `"owner_clean"`

### 2. **map_generator.py** - Fixed Aggregation Issues

#### Fixed `_generate_zip_owner_table()` method:

**Before:**
```python
agg_dict = {"parcelpin": "count"}  # Hardcoded - would fail if column doesn't exist
```

**After:**
```python
# Dynamically find the parcel ID column
count_col = None
for candidate in ['parcel_pin', 'parcelpin', 'parcel_id', 'pin', 'objectid']:
    if candidate in zip_df.columns:
        count_col = candidate
        break

agg_dict = {count_col: "count"}  # Use detected column
```

#### Added Decimal Type Handling:
```python
# Convert Decimal to float before aggregation (prevents JSON serialization errors)
if sales_col in zip_df.columns:
    zip_df[sales_col] = zip_df[sales_col].astype(float)
    agg_dict[sales_col] = "sum"
```

### 3. **Error Handling Improvements**

#### Better Fallbacks:
- If no parcel ID column found, shows friendly error message instead of crashing
- Graceful handling when optional columns (ZIP, sales, assessment) are missing
- Validates required `owner_clean` column exists on initialization

#### Enhanced Logging:
```python
logger.debug(
    f"Column detection: parcel_pin={self.parcel_pin_col}, "
    f"zip={self.zip_col}, sales={self.sales_col}, "
    f"assess={self.assess_col}, owner={self.owner_col}"
)
```

## Testing Recommendations

### Test with different data schemas:

1. **Standard Cleveland Data:**
   - Has: `parcel_pin`, `par_zip`, `sales_amount`, `certified_tax_total`
   - Should work without issues

2. **Alternative Schema 1:**
   - Has: `parcelpin`, `zip`, `sales_amou`, `tax_total`
   - Should auto-detect and work

3. **Minimal Schema:**
   - Has: `objectid`, `owner_clean`, `geometry`
   - Should work but show "N/A" for missing financial data

4. **Missing Required Column:**
   - Missing: `owner_clean`
   - Should raise clear ValueError on initialization

## Breaking Changes

None - all changes are backward compatible. Code that worked before will continue to work.

## Future Improvements

Consider adding:
1. Configuration file for custom column mappings per city
2. More detailed validation of column data types
3. Automatic column name normalization on data load
4. Unit tests for column detection logic

## Files Modified

1. `/mapping/layer_builder.py` - Added `_detect_column_names()` method and updated all column references
2. `/mapping/map_generator.py` - Fixed `_generate_zip_owner_table()` to use dynamic column detection and handle Decimal types

## Related Issues Fixed

- ✅ KeyError when parcel data uses `parcelpin` instead of `parcel_pin`
- ✅ KeyError when grouping by non-existent column in ZIP owner tables
- ✅ JSON serialization errors from Decimal types in aggregation
- ✅ Missing graceful fallbacks when optional columns absent
- ✅ Inconsistent column name handling across methods
