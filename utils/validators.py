"""
Data Validators
Functions to validate user inputs and data files
"""

import os
from pathlib import Path
from typing import Optional, Tuple, List
import pandas as pd


def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Check if file has allowed extension
    
    Args:
        filename: File name
        allowed_extensions: List of allowed extensions (without dot)
    
    Returns:
        bool: True if valid, False otherwise
    """
    if not filename:
        return False
    
    ext = Path(filename).suffix.lower().lstrip('.')
    return ext in [e.lower() for e in allowed_extensions]


def validate_file_size(file_size: int, max_size_mb: int = 500) -> Tuple[bool, Optional[str]]:
    """
    Check if file size is within limits
    
    Args:
        file_size: File size in bytes
        max_size_mb: Maximum size in MB
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    max_bytes = max_size_mb * 1024 * 1024
    
    if file_size > max_bytes:
        return False, f"File size ({file_size / 1024 / 1024:.1f} MB) exceeds maximum allowed ({max_size_mb} MB)"
    
    return True, None


def validate_csv_file(file_path: str, required_columns: Optional[List[str]] = None) -> Tuple[bool, Optional[str]]:
    """
    Validate CSV file format and required columns
    
    Args:
        file_path: Path to CSV file
        required_columns: List of required column names (optional)
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        # Try to read first few rows
        df = pd.read_csv(file_path, nrows=5)
        
        if df.empty:
            return False, "CSV file is empty"
        
        # Check required columns
        if required_columns:
            missing_cols = [col for col in required_columns if col not in df.columns]
            if missing_cols:
                return False, f"Missing required columns: {', '.join(missing_cols)}"
        
        return True, None
        
    except pd.errors.EmptyDataError:
        return False, "CSV file is empty"
    except pd.errors.ParserError as e:
        return False, f"CSV parsing error: {str(e)}"
    except Exception as e:
        return False, f"Error reading CSV: {str(e)}"


def validate_shapefile_bundle(file_paths: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Validate that all required shapefile components are present
    
    Args:
        file_paths: List of file paths in the shapefile bundle
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    required_extensions = {'.shp', '.shx', '.dbf'}
    recommended_extensions = {'.prj'}
    
    # Get all extensions present
    extensions = {Path(f).suffix.lower() for f in file_paths}
    
    # Check required files
    missing_required = required_extensions - extensions
    if missing_required:
        return False, f"Missing required shapefile components: {', '.join(missing_required)}"
    
    # Warn about missing recommended files
    missing_recommended = recommended_extensions - extensions
    if missing_recommended:
        # This is just a warning, still valid
        pass
    
    return True, None


def validate_coordinates(lat: float, lng: float) -> Tuple[bool, Optional[str]]:
    """
    Validate latitude and longitude coordinates
    
    Args:
        lat: Latitude
        lng: Longitude
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        lat = float(lat)
        lng = float(lng)
        
        if not (-90 <= lat <= 90):
            return False, f"Latitude {lat} is out of range (-90 to 90)"
        
        if not (-180 <= lng <= 180):
            return False, f"Longitude {lng} is out of range (-180 to 180)"
        
        return True, None
        
    except (TypeError, ValueError):
        return False, "Coordinates must be numeric values"


def validate_city_name(name: str) -> Tuple[bool, Optional[str]]:
    """
    Validate city name
    
    Args:
        name: City name
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if not name or not name.strip():
        return False, "City name cannot be empty"
    
    if len(name) > 100:
        return False, "City name too long (max 100 characters)"
    
    # Check for invalid characters
    if not all(c.isalnum() or c.isspace() or c in '-_' for c in name):
        return False, "City name contains invalid characters"
    
    return True, None


def validate_zoom_level(zoom: int) -> Tuple[bool, Optional[str]]:
    """
    Validate map zoom level
    
    Args:
        zoom: Zoom level
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    try:
        zoom = int(zoom)
        if not (1 <= zoom <= 20):
            return False, "Zoom level must be between 1 and 20"
        return True, None
    except (TypeError, ValueError):
        return False, "Zoom level must be an integer"


def validate_dataframe_not_empty(df: pd.DataFrame, df_name: str = "DataFrame") -> Tuple[bool, Optional[str]]:
    """
    Check if DataFrame is not empty
    
    Args:
        df: Pandas DataFrame
        df_name: Name for error messages
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if df is None:
        return False, f"{df_name} is None"
    
    if df.empty:
        return False, f"{df_name} is empty"
    
    return True, None


def validate_parcel_pin_column(df: pd.DataFrame, column_name: str = 'parcelpin') -> Tuple[bool, Optional[str]]:
    """
    Validate parcel PIN column exists and has values
    
    Args:
        df: Pandas DataFrame
        column_name: Name of parcel PIN column
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if column_name not in df.columns:
        return False, f"Column '{column_name}' not found in data"
    
    if df[column_name].isna().all():
        return False, f"Column '{column_name}' has no values"
    
    # Check for duplicates
    duplicate_count = df[column_name].duplicated().sum()
    if duplicate_count > 0:
        return False, f"Found {duplicate_count} duplicate parcel PINs"
    
    return True, None

