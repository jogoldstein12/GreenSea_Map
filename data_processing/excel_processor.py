"""
Excel Processing Module
Handles Excel file loading, validation, and target owner list processing
"""

import pandas as pd
from pathlib import Path
from typing import Optional, List, Dict, Tuple, Union
import logging

from data_processing.normalizer import clean_owner
from utils.validators import validate_file_size

# Setup logging
logger = logging.getLogger(__name__)


class ExcelProcessor:
    """
    Processes Excel files containing target owner lists and other data.
    
    Handles validation, sheet management, owner cleaning, and preparation
    for database operations.
    """
    
    def __init__(
        self,
        max_file_size_mb: int = 100,
        default_sheet: Union[str, int] = 0
    ):
        """
        Initialize Excel processor.
        
        Args:
            max_file_size_mb: Maximum file size in MB
            default_sheet: Default sheet name or index to load
        """
        self.max_file_size_mb = max_file_size_mb
        self.default_sheet = default_sheet
        
        # Common column name variations for owner data
        self.owner_column_candidates = [
            "owner_clean",
            "owner",
            "owner_name",
            "deeded_owner",
            "ownername",
            "company",
            "company_name",
            "entity_name"
        ]
    
    def validate_file(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate Excel file before processing.
        
        Args:
            file_path: Path to Excel file
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(file_path)
        
        # Check file exists
        if not path.exists():
            return False, f"File not found: {file_path}"
        
        # Check file extension
        if path.suffix.lower() not in ['.xlsx', '.xls', '.xlsm']:
            return False, f"Not an Excel file: {file_path}"
        
        # Check file size
        file_size = path.stat().st_size
        is_valid, error = validate_file_size(file_size, self.max_file_size_mb)
        if not is_valid:
            return False, error
        
        return True, None
    
    def list_sheets(self, file_path: str) -> List[str]:
        """
        List all sheet names in the Excel file.
        
        Args:
            file_path: Path to Excel file
        
        Returns:
            List of sheet names
        
        Raises:
            ValueError: If file is invalid
        """
        logger.info(f"Listing sheets in: {file_path}")
        
        # Validate file first
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            raise ValueError(f"Excel validation failed: {error}")
        
        try:
            excel_file = pd.ExcelFile(file_path)
            sheets = excel_file.sheet_names
            logger.info(f"Found {len(sheets)} sheets: {sheets}")
            return sheets
            
        except Exception as e:
            raise ValueError(f"Error reading Excel file: {str(e)}")
    
    def load_excel(
        self,
        file_path: str,
        sheet_name: Optional[Union[str, int]] = None,
        header: int = 0,
        **kwargs
    ) -> pd.DataFrame:
        """
        Load Excel file into DataFrame.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index (default: uses default_sheet)
            header: Row number to use as column names (default: 0)
            **kwargs: Additional arguments to pass to pd.read_excel
        
        Returns:
            DataFrame with Excel contents
        
        Raises:
            ValueError: If validation fails
        """
        sheet_name = sheet_name if sheet_name is not None else self.default_sheet
        
        logger.info(f"Loading Excel file: {file_path}, sheet: {sheet_name}")
        
        # Validate file first
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            raise ValueError(f"Excel validation failed: {error}")
        
        try:
            df = pd.read_excel(
                file_path,
                sheet_name=sheet_name,
                header=header,
                **kwargs
            )
            
            logger.info(f"Loaded {len(df)} rows, {len(df.columns)} columns")
            logger.info(f"Columns: {df.columns.tolist()}")
            
            return df
            
        except Exception as e:
            raise ValueError(f"Error loading Excel: {str(e)}")
    
    def normalize_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normalize column names to lowercase.
        
        Args:
            df: Raw DataFrame
        
        Returns:
            DataFrame with normalized columns
        """
        df = df.copy()
        df.columns = df.columns.str.lower().str.strip()
        logger.debug(f"Normalized columns: {df.columns.tolist()}")
        return df
    
    def find_owner_column(
        self,
        df: pd.DataFrame,
        custom_candidates: Optional[List[str]] = None
    ) -> Optional[str]:
        """
        Find the owner column from common name variations.
        
        Args:
            df: DataFrame to search
            custom_candidates: Optional list of custom column names to try
        
        Returns:
            Name of the owner column, or None if not found
        """
        candidates = custom_candidates or self.owner_column_candidates
        
        # Try exact matches first
        for candidate in candidates:
            if candidate in df.columns:
                logger.info(f"Found owner column: '{candidate}'")
                return candidate
        
        # Try partial matches
        for candidate in candidates:
            for col in df.columns:
                if candidate in col.lower():
                    logger.info(f"Found owner column via partial match: '{col}'")
                    return col
        
        logger.warning("Could not find owner column")
        return None
    
    def extract_owners(
        self,
        df: pd.DataFrame,
        owner_column: Optional[str] = None,
        clean: bool = True,
        remove_duplicates: bool = True,
        remove_empty: bool = True
    ) -> List[str]:
        """
        Extract owner names from DataFrame.
        
        Args:
            df: DataFrame containing owner data
            owner_column: Name of owner column (auto-detected if None)
            clean: Whether to clean/normalize owner names
            remove_duplicates: Whether to remove duplicate owners
            remove_empty: Whether to remove empty/null values
        
        Returns:
            List of owner names
        
        Raises:
            ValueError: If owner column not found
        """
        # Auto-detect owner column if not specified
        if owner_column is None:
            owner_column = self.find_owner_column(df)
        
        if owner_column is None:
            raise ValueError(
                f"Could not find owner column. Tried: {self.owner_column_candidates}"
            )
        
        if owner_column not in df.columns:
            raise ValueError(f"Column '{owner_column}' not found in DataFrame")
        
        logger.info(f"Extracting owners from column: '{owner_column}'")
        
        # Extract series
        owners = df[owner_column]
        
        # Remove empty values
        if remove_empty:
            initial_count = len(owners)
            owners = owners.dropna()
            removed = initial_count - len(owners)
            if removed > 0:
                logger.info(f"Removed {removed} null/empty values")
        
        # Clean owner names
        if clean:
            owners = owners.map(clean_owner)
            logger.info("Applied owner name cleaning")
        
        # Remove duplicates
        if remove_duplicates:
            initial_count = len(owners)
            owners = owners.drop_duplicates()
            removed = initial_count - len(owners)
            if removed > 0:
                logger.info(f"Removed {removed} duplicate owners")
        
        # Convert to list
        owner_list = owners.tolist()
        
        logger.info(f"Extracted {len(owner_list)} unique owners")
        
        return owner_list
    
    def process_owner_list(
        self,
        file_path: str,
        sheet_name: Optional[Union[str, int]] = None,
        owner_column: Optional[str] = None,
        **kwargs
    ) -> List[str]:
        """
        Complete pipeline to load and process owner list from Excel.
        
        Args:
            file_path: Path to Excel file
            sheet_name: Sheet name or index
            owner_column: Name of owner column (auto-detected if None)
            **kwargs: Additional arguments for load_excel
        
        Returns:
            List of cleaned, unique owner names
        
        Raises:
            ValueError: If validation fails at any step
        
        Example:
            >>> processor = ExcelProcessor()
            >>> owners = processor.process_owner_list('target_owners.xlsx')
            >>> print(f"Loaded {len(owners)} target owners")
        """
        logger.info(f"Starting owner list processing for: {file_path}")
        
        # 1. Load Excel file
        df = self.load_excel(file_path, sheet_name, **kwargs)
        logger.info(f"Step 1/3: Loaded {len(df)} rows")
        
        # 2. Normalize columns
        df = self.normalize_columns(df)
        logger.info(f"Step 2/3: Normalized column names")
        
        # 3. Extract owners
        owners = self.extract_owners(df, owner_column)
        logger.info(f"Step 3/3: Extracted {len(owners)} owners")
        
        if not owners:
            raise ValueError("No owners found in Excel file")
        
        logger.info(f"Owner list processing complete: {len(owners)} owners ready")
        
        return owners
    
    def load_multiple_sheets(
        self,
        file_path: str,
        sheet_names: Optional[List[Union[str, int]]] = None,
        **kwargs
    ) -> Dict[str, pd.DataFrame]:
        """
        Load multiple sheets from an Excel file.
        
        Args:
            file_path: Path to Excel file
            sheet_names: List of sheet names/indices (None = all sheets)
            **kwargs: Additional arguments for pd.read_excel
        
        Returns:
            Dictionary mapping sheet names to DataFrames
        
        Example:
            >>> processor = ExcelProcessor()
            >>> sheets = processor.load_multiple_sheets('data.xlsx')
            >>> for name, df in sheets.items():
            ...     print(f"{name}: {len(df)} rows")
        """
        logger.info(f"Loading multiple sheets from: {file_path}")
        
        # Validate file first
        is_valid, error = self.validate_file(file_path)
        if not is_valid:
            raise ValueError(f"Excel validation failed: {error}")
        
        try:
            # Load all sheets or specified sheets
            if sheet_names is None:
                # Load all sheets
                dfs = pd.read_excel(file_path, sheet_name=None, **kwargs)
            else:
                # Load specific sheets
                dfs = {}
                for sheet in sheet_names:
                    dfs[sheet] = pd.read_excel(
                        file_path,
                        sheet_name=sheet,
                        **kwargs
                    )
            
            logger.info(f"Loaded {len(dfs)} sheets")
            for name, df in dfs.items():
                logger.info(f"  {name}: {len(df)} rows, {len(df.columns)} columns")
            
            return dfs
            
        except Exception as e:
            raise ValueError(f"Error loading multiple sheets: {str(e)}")
    
    def save_to_excel(
        self,
        df: pd.DataFrame,
        file_path: str,
        sheet_name: str = "Sheet1",
        index: bool = False,
        **kwargs
    ) -> None:
        """
        Save DataFrame to Excel file.
        
        Args:
            df: DataFrame to save
            file_path: Output file path
            sheet_name: Name for the sheet
            index: Whether to write row indices
            **kwargs: Additional arguments for to_excel
        
        Raises:
            ValueError: If save fails
        """
        logger.info(f"Saving DataFrame to Excel: {file_path}")
        
        try:
            df.to_excel(
                file_path,
                sheet_name=sheet_name,
                index=index,
                **kwargs
            )
            
            logger.info(f"Saved {len(df)} rows to {file_path}")
            
        except Exception as e:
            raise ValueError(f"Error saving to Excel: {str(e)}")
    
    def get_file_info(self, file_path: str) -> Dict:
        """
        Get information about an Excel file.
        
        Args:
            file_path: Path to Excel file
        
        Returns:
            Dictionary with file information
        """
        path = Path(file_path)
        
        info = {
            "file_path": str(path.absolute()),
            "file_name": path.name,
            "file_size_mb": path.stat().st_size / 1024 / 1024,
            "extension": path.suffix,
        }
        
        try:
            sheets = self.list_sheets(file_path)
            info["sheet_count"] = len(sheets)
            info["sheet_names"] = sheets
        except Exception as e:
            info["sheet_count"] = None
            info["sheet_names"] = None
            info["error"] = str(e)
        
        return info


def process_owner_list_file(
    file_path: str,
    sheet_name: Optional[Union[str, int]] = None,
    owner_column: Optional[str] = None
) -> List[str]:
    """
    Convenience function to process an owner list file in one call.
    
    Args:
        file_path: Path to Excel file
        sheet_name: Sheet name or index
        owner_column: Name of owner column (auto-detected if None)
    
    Returns:
        List of cleaned, unique owner names
    
    Example:
        >>> owners = process_owner_list_file('targets.xlsx', sheet_name='Owners')
        >>> print(f"Loaded {len(owners)} target owners")
    """
    processor = ExcelProcessor()
    return processor.process_owner_list(file_path, sheet_name, owner_column)

