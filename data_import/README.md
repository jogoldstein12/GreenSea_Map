# Data Import Module

This module handles the complete data import process for adding new cities to the GIS Portfolio Analyzer.

## ImportManager

The `ImportManager` class orchestrates the entire import workflow:

1. **City Creation** - Creates city record in database
2. **Configuration** - Stores column mappings and property types
3. **Parcel Import** - Processes CSV + Shapefile and merges data
4. **Target Owners Import** - Processes Excel file with investor names
5. **History Logging** - Tracks import operations
6. **Transaction Management** - Ensures all-or-nothing imports
7. **Temp File Management** - Cleans up temporary files

## Usage

```python
from data_import import ImportManager

# Initialize manager
manager = ImportManager()

# Import city data
success, message, counts = manager.import_city_data(
    city_info={
        'city_name': 'Cleveland',
        'display_name': 'Cleveland, OH',
        'state': 'Ohio',
        'center_lat': 41.4993,
        'center_lng': -81.6944,
        'zoom_level': 11
    },
    uploaded_files={
        'csv': csv_file,
        'shp': shapefile_zip,
        'excel': excel_file
    },
    column_mappings={
        'pin': 'parcelpin',
        'owner': 'deeded_owner',
        # ...
    },
    property_types={
        '1-FAMILY PLATTED LOT': True,
        '2-FAMILY PLATTED LOT': True,
        # ...
    }
)

if success:
    print(f"Imported {counts['parcels']} parcels and {counts['target_owners']} owners")
else:
    print(f"Import failed: {message}")
```

## Features

- **Unique Batch IDs** - Each import gets a unique identifier for tracking
- **Temp File Management** - Automatically saves and cleans up uploaded files
- **Transaction Safety** - Rolls back database changes on any error
- **Detailed Logging** - Comprehensive logging for debugging
- **Error Handling** - Clear error messages for users
- **Import History** - All imports logged to database

## Implementation Status

- ✅ **Task 22:** Import Manager orchestration (complete)
- ⏳ **Task 23:** City creation logic (complete)
- ⏳ **Task 24:** City configuration creation (complete)
- 🔄 **Task 25:** Parcel data import (placeholder)
- 🔄 **Task 26:** Target owners import (placeholder)
- ✅ **Task 27:** Import history logging (complete)
- ✅ **Task 28:** Transaction management (complete)
- 🔄 **Task 29:** Streamlit integration (pending)
- 🔄 **Task 30:** Validation (pending)
- ✅ **Task 31:** Temp file management (complete)

## Methods

### `import_city_data()`
Main entry point for importing a complete city dataset.

### `_create_city()`
Creates the city record in the database.

### `_create_city_config()`
Stores city configuration (mappings, property types, etc.).

### `_import_parcels()` (Placeholder)
Will process and import parcel data from CSV + Shapefile.

### `_import_target_owners()` (Placeholder)
Will process and import target owners from Excel.

### `_log_import_history()`
Records import operation in the database.

## Error Handling

The ImportManager handles errors gracefully:
- Database transaction rollback on failure
- Cleanup of temporary files
- Detailed error logging
- User-friendly error messages
- Import history logging even for failures

