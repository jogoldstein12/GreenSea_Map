"""
CSV Processing Module
Handles CSV file loading, validation, and preparation for database import
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Tuple
import logging

from data_processing.normalizer import (
    normalize_parcel_data,
    validate_required_columns,
    PARCEL_REQUIRED_COLUMNS
)
from utils.validators import validate_csv_file, validate_file_size

# Setup logging
logger = logging.getLogger(__name__)


class CSVProcessor:
    """
    Processes CSV files containing parcel data.
    
    Handles validation, normalization, filtering, and type conversion
    to prepare data for database insertion.
    """
    
    def __init__(
        self,
        valid_property_types: Optional[List[str]] = None,
        max_file_size_mb: int = 500
    ):
        """
        Initialize CSV processor.
        
        Args:
            valid_property_types: List of valid land use types to keep
            max_file_size_mb: Maximum file size in MB
        """
        self.valid_property_types = valid_property_types or [
            "1-FAMILY PLATTED LOT",
            "2-FAMILY PLATTED LOT"
        ]
        self.max_file_size_mb = max_file_size_mb
        self.numeric_columns = [
            "sales_amount",
            "sales_amou",
            "certified_tax_total",
            "tax_total"
        ]
    
    def validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate CSV file before processing.
        
        Args:
            file_path: Path to CSV file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check file exists
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # Check file size
        file_size = path.stat().st_size
        is_valid, error = validate_file_size(file_size, self.max_file_size_mb)
        if not is_valid:
            return False, error
        
        # Validate CSV format and structure
        is_valid, error = validate_csv_file(str(file_path))
        if not is_valid:
            return False, error
        
        return True, None
    
    def load_csv(
        self,
        file_path: str,
        chunksize: Optional[int] = None,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load CSV file into DataFrame.
        
        Args:
            file_path: Path to CSV file
            chunksize: If specified, load in chunks (for large files)
            **kwargs: Additional arguments to pass to pd.read_csv
        
        Returns:
            DataFrame with CSV contents
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is invalid
        """
        logger.info(f"Loading CSV file: {file_path}")
        
        # Validate file first
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            raise ValueError(f"CSV validation failed: {error}")
        
        try:
            # Load CSV with memory optimization
            df = pd.read_csv(
                file_path,
                low_memory=False,  # Avoid mixed type inference
                chunksize=chunksize,
                **kwargs
            )
            
            # If using chunks, concatenate them
            if chunksize:
                logger.info(f"Loading in chunks of {chunksize} rows")
                chunks = []
                for i, chunk in enumerate(df):
                    chunks.append(chunk)
                    logger.debug(f"Loaded chunk {i+1} with {len(chunk)} rows")
                df = pd.concat(chunks, ignore_index=True)
            
            logger.info(f"Loaded {len(df)} rows from CSV")
            return df
            
        except pd.errors.EmptyDataError:
            raise ValueError("CSV file is empty")
        except pd.errors.ParserError as e:
            raise ValueError(f"CSV parsing error: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error loading CSV: {str(e)}")
    
    def normalize_data(
        self,
        df: pd.DataFrame,
        column_mappings: Optional[Dict[str, List[str]]] = None
    ) -> pd.DataFrame:
        """
        Normalize column names and clean owner data.
        
        Args:
            df: Raw DataFrame
            column_mappings: Optional custom column mappings
        
        Returns:
            Normalized DataFrame
        """
        logger.info("Normalizing CSV data")
        return normalize_parcel_data(df, column_mappings, clean_owners=True)
    
    def filter_by_property_type(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Filter DataFrame to only include valid property types.
        
        Args:
            df: DataFrame with normalized columns
        
        Returns:
            Filtered DataFrame
        
        Raises:
            KeyError: If tax_luc_description column not found
        """
        if "tax_luc_description" not in df.columns:
            logger.warning(
                "Column 'tax_luc_description' not found. "
                "Skipping property type filtering."
            )
            return df
        
        initial_count = len(df)
        df_filtered = df[df["tax_luc_description"].isin(self.valid_property_types)].copy()
        filtered_count = len(df_filtered)
        
        logger.info(
            f"Filtered by property type: {initial_count} → {filtered_count} rows "
            f"({filtered_count/initial_count*100:.1f}% kept)"
        )
        
        return df_filtered
    
    def coerce_numeric_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Convert numeric columns to proper numeric types.
        
        Handles columns that should be numeric but may have been read as strings.
        Invalid values are converted to 0.
        
        Args:
            df: DataFrame with columns to convert
        
        Returns:
            DataFrame with numeric columns properly typed
        """
        df = df.copy()
        
        for col in self.numeric_columns:
            if col in df.columns:
                original_type = df[col].dtype
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                logger.debug(f"Converted column '{col}' from {original_type} to numeric")
        
        return df
    
    def validate_processed_data(self, df: pd.DataFrame) -> Tuple[bool, Optional[str]]:
        """
        Validate that processed data has required columns.
        
        Args:
            df: Processed DataFrame
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        return validate_required_columns(df, PARCEL_REQUIRED_COLUMNS, "Processed CSV")
    
    def process_csv(
        self,
        file_path: str,
        filter_property_types: bool = True,
        column_mappings: Optional[Dict[str, List[str]]] = None,
        chunksize: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Complete CSV processing pipeline.
        
        Loads, normalizes, filters, and prepares CSV data for database import.
        
        Args:
            file_path: Path to CSV file
            filter_property_types: Whether to filter by valid property types
            column_mappings: Optional custom column mappings
            chunksize: Optional chunk size for large files
        
        Returns:
            Processed DataFrame ready for database import
        
        Raises:
            ValueError: If validation fails at any step
        
        Example:
            >>> processor = CSVProcessor()
            >>> df = processor.process_csv('parcels.csv')
            >>> # df is now ready for database insertion
        """
        logger.info(f"Starting CSV processing pipeline for: {file_path}")
        
        # 1. Load CSV
        df = self.load_csv(file_path, chunksize=chunksize)
        logger.info(f"Step 1/5: Loaded {len(df)} rows")
        
        # 2. Normalize columns and clean owners
        df = self.normalize_data(df, column_mappings)
        logger.info(f"Step 2/5: Normalized columns and cleaned owner names")
        
        # 3. Filter by property type
        if filter_property_types:
            df = self.filter_by_property_type(df)
            logger.info(f"Step 3/5: Filtered to {len(df)} valid properties")
        else:
            logger.info(f"Step 3/5: Skipped property type filtering")
        
        # 4. Convert numeric columns
        df = self.coerce_numeric_columns(df)
        logger.info(f"Step 4/5: Converted numeric columns")
        
        # 5. Validate final data
        is_valid, error = self.validate_processed_data(df)
        if not is_valid:
            raise ValueError(f"Data validation failed: {error}")
        logger.info(f"Step 5/5: Validation passed")
        
        logger.info(
            f"CSV processing complete: {len(df)} rows, "
            f"{len(df.columns)} columns ready for import"
        )
        
        return df
    
    def get_data_summary(self, df: pd.DataFrame) -> Dict:
        """
        Generate summary statistics for processed data.
        
        Args:
            df: Processed DataFrame
        
        Returns:
            Dictionary with summary statistics
        """
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "columns": df.columns.tolist(),
            "unique_owners": df["owner_clean"].nunique() if "owner_clean" in df.columns else 0,
            "memory_usage_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
        }
        
        # Add property type breakdown if available
        if "tax_luc_description" in df.columns:
            summary["property_types"] = df["tax_luc_description"].value_counts().to_dict()
        
        # Add ZIP code breakdown if available
        if "par_zip" in df.columns:
            summary["zip_codes"] = df["par_zip"].value_counts().head(10).to_dict()
        
        # Add numeric summaries if available
        if "sales_amount" in df.columns:
            summary["total_sales_amount"] = float(df["sales_amount"].sum())
            summary["avg_sales_amount"] = float(df["sales_amount"].mean())
        
        return summary


def process_csv_file(
    file_path: str,
    valid_property_types: Optional[List[str]] = None,
    **kwargs
) -> pd.DataFrame:
    """
    Convenience function to process a CSV file in one call.
    
    Args:
        file_path: Path to CSV file
        valid_property_types: List of valid property types
        **kwargs: Additional arguments for CSVProcessor
    
    Returns:
        Processed DataFrame
    
    Example:
        >>> df = process_csv_file('cleveland_parcels.csv')
        >>> print(f"Loaded {len(df)} parcels")
    """
    processor = CSVProcessor(valid_property_types=valid_property_types)
    return processor.process_csv(file_path, **kwargs)

