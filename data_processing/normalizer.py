"""
Data Normalization Module
Handles column normalization and data cleaning for parcel datasets
"""

import pandas as pd
from typing import Optional, Dict, List


def normalize_columns(
    df: pd.DataFrame, 
    column_mappings: Optional[Dict[str, List[str]]] = None
) -> pd.DataFrame:
    """
    Normalize column names in a DataFrame to standard schema.
    
    Converts column names to lowercase and maps common variations
    to standard field names used throughout the application.
    
    Args:
        df: Input DataFrame with raw column names
        column_mappings: Optional dict mapping standard names to list of possible variations.
                        If None, uses default mappings.
    
    Returns:
        DataFrame with normalized column names
    
    Example:
        >>> df = pd.DataFrame({'DEEDED_OWN': ['Smith'], 'TAX_LUC_DE': ['Residential']})
        >>> normalized = normalize_columns(df)
        >>> 'deeded_owner' in normalized.columns
        True
    """
    # Make a copy to avoid modifying original
    df = df.copy()
    
    # Convert all column names to lowercase
    df.columns = df.columns.str.lower()
    
    # Default column mappings if none provided
    if column_mappings is None:
        column_mappings = {
            "deeded_owner": ["deeded_owner", "deeded_own", "deed_owner", "ownername", "mail_name"],
            "tax_luc_description": ["tax_luc_description", "tax_luc_de", "tax_luc", "ext_luc_de"],
            "parcelpin": ["parcelpin", "parcel_pin", "parcel_id", "pin"],
            "par_addr": ["par_addr", "par_addr_all", "par_addr_a", "address", "site_address"],
            "par_zip": ["par_zip", "zip", "zipcode", "zip_code"],
            "sales_amount": ["sales_amount", "sales_amou", "sale_price", "saleprice"],
            "certified_tax_total": ["certified_tax_total", "tax_total", "assessed_value"]
        }
    
    # Apply mappings - find first matching column and rename it
    for standard_name, variations in column_mappings.items():
        for variation in variations:
            if variation in df.columns:
                df = df.rename(columns={variation: standard_name})
                break  # Only rename the first match
    
    return df


def clean_owner(name) -> str:
    """
    Clean and standardize owner names for consistent matching.
    
    Normalizes owner names by:
    - Converting to uppercase
    - Removing punctuation (periods, commas)
    - Removing common legal suffixes (LLC, INC, CO)
    - Trimming whitespace
    
    Args:
        name: Raw owner name (string or any type)
    
    Returns:
        Cleaned, standardized owner name string
    
    Example:
        >>> clean_owner("Smith Properties, LLC.")
        'SMITH PROPERTIES'
        >>> clean_owner(None)
        'UNKNOWN'
    """
    # Handle null/missing values
    if pd.isna(name):
        return "UNKNOWN"
    
    # Convert to string and uppercase
    cleaned = str(name).upper().strip()
    
    # Handle empty strings
    if not cleaned:
        return "UNKNOWN"
    
    # Remove punctuation
    cleaned = cleaned.replace(".", "")
    cleaned = cleaned.replace(",", "")
    
    # Remove common legal entity suffixes
    # Order matters! Longer suffixes first to avoid partial matches
    suffixes = [" CORP", " PLLC", " LLC", " INC", " LTD", " LP", " CO"]
    for suffix in suffixes:
        cleaned = cleaned.replace(suffix, "")
    
    # Remove extra whitespace
    cleaned = " ".join(cleaned.split())
    
    return cleaned.strip()


def validate_required_columns(
    df: pd.DataFrame, 
    required_columns: List[str],
    df_name: str = "DataFrame"
) -> tuple[bool, Optional[str]]:
    """
    Validate that DataFrame contains all required columns.
    
    Args:
        df: DataFrame to validate
        required_columns: List of column names that must be present
        df_name: Name of DataFrame for error messages
    
    Returns:
        Tuple of (is_valid, error_message)
        - (True, None) if all required columns present
        - (False, error_message) if any columns missing
    
    Example:
        >>> df = pd.DataFrame({'name': ['A'], 'value': [1]})
        >>> is_valid, msg = validate_required_columns(df, ['name', 'value'])
        >>> is_valid
        True
    """
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        error_msg = (
            f"{df_name} is missing required columns: {', '.join(missing_columns)}. "
            f"Available columns: {', '.join(df.columns.tolist())}"
        )
        return False, error_msg
    
    return True, None


def apply_owner_cleaning(df: pd.DataFrame, owner_column: str = "deeded_owner") -> pd.DataFrame:
    """
    Apply owner name cleaning to a DataFrame column.
    
    Creates a new 'owner_clean' column with standardized owner names.
    
    Args:
        df: DataFrame containing owner names
        owner_column: Name of column containing raw owner names
    
    Returns:
        DataFrame with new 'owner_clean' column added
    
    Raises:
        KeyError: If owner_column doesn't exist in DataFrame
    
    Example:
        >>> df = pd.DataFrame({'deeded_owner': ['Smith LLC', 'Jones, Inc.']})
        >>> result = apply_owner_cleaning(df)
        >>> result['owner_clean'].tolist()
        ['SMITH', 'JONES']
    """
    if owner_column not in df.columns:
        raise KeyError(f"Column '{owner_column}' not found in DataFrame")
    
    df = df.copy()
    df["owner_clean"] = df[owner_column].apply(clean_owner)
    
    return df


def normalize_parcel_data(
    df: pd.DataFrame,
    column_mappings: Optional[Dict[str, List[str]]] = None,
    clean_owners: bool = True
) -> pd.DataFrame:
    """
    Complete normalization pipeline for parcel data.
    
    Combines column normalization and owner cleaning into one step.
    
    Args:
        df: Raw parcel DataFrame
        column_mappings: Optional custom column mappings
        clean_owners: Whether to create cleaned owner names
    
    Returns:
        Fully normalized DataFrame
    
    Example:
        >>> raw_df = pd.DataFrame({
        ...     'DEEDED_OWN': ['Smith, LLC'],
        ...     'TAX_LUC_DE': ['Residential']
        ... })
        >>> normalized = normalize_parcel_data(raw_df)
        >>> 'owner_clean' in normalized.columns
        True
    """
    # Normalize column names
    df = normalize_columns(df, column_mappings)
    
    # Clean owner names if requested and column exists
    if clean_owners and "deeded_owner" in df.columns:
        df = apply_owner_cleaning(df, "deeded_owner")
    
    return df


# Standard column requirements for different data types
PARCEL_REQUIRED_COLUMNS = ["parcelpin", "deeded_owner"]
TARGET_OWNER_REQUIRED_COLUMNS = ["owner_clean"]
MERGED_REQUIRED_COLUMNS = ["parcelpin", "deeded_owner", "geometry"]

