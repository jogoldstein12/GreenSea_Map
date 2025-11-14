"""
Shapefile Processing Module
Handles shapefile loading, validation, CRS conversion, and geometry processing
"""

import geopandas as gpd
from pathlib import Path
from typing import Optional, List, Tuple, Dict
import logging
from zipfile import ZipFile, is_zipfile

from data_processing.normalizer import normalize_parcel_data, validate_required_columns
from utils.validators import validate_shapefile_bundle

# Setup logging
logger = logging.getLogger(__name__)

# Required shapefile components
REQUIRED_SHAPEFILE_EXTENSIONS = {'.shp', '.shx', '.dbf'}
RECOMMENDED_SHAPEFILE_EXTENSIONS = {'.prj'}
ALL_SHAPEFILE_EXTENSIONS = {'.shp', '.shx', '.dbf', '.prj', '.cpg', '.xml', '.sbn', '.sbx'}


class ShapefileProcessor:
    """
    Processes shapefiles containing parcel geometries.
    
    Handles validation, CRS conversion, normalization, and preparation
    for database insertion with PostGIS.
    """
    
    def __init__(
        self,
        target_crs: str = "EPSG:4326",  # WGS84 for web mapping
        valid_property_types: Optional[List[str]] = None
    ):
        """
        Initialize shapefile processor.
        
        Args:
            target_crs: Target coordinate reference system (default: WGS84)
            valid_property_types: List of valid land use types to keep
        """
        self.target_crs = target_crs
        self.valid_property_types = valid_property_types or [
            "1-FAMILY PLATTED LOT",
            "2-FAMILY PLATTED LOT"
        ]
    
    def validate_shapefile(self, shapefile_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate that all required shapefile components are present.
        
        Args:
            shapefile_path: Path to .shp file or directory containing shapefile
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        path = Path(shapefile_path)
        
        # If it's a directory, look for .shp files
        if path.is_dir():
            shp_files = list(path.glob("*.shp"))
            if not shp_files:
                return False, f"No .shp files found in directory: {shapefile_path}"
            path = shp_files[0]  # Use first .shp file
        
        # Check if path exists and is a .shp file
        if not path.exists():
            return False, f"Shapefile not found: {shapefile_path}"
        
        if path.suffix.lower() != '.shp':
            return False, f"Not a shapefile (.shp): {shapefile_path}"
        
        # Get all related files
        base_path = path.with_suffix('')
        related_files = []
        
        for ext in ALL_SHAPEFILE_EXTENSIONS:
            file_path = base_path.with_suffix(ext)
            if file_path.exists():
                related_files.append(str(file_path))
        
        # Validate bundle
        return validate_shapefile_bundle(related_files)
    
    def extract_shapefile_from_zip(
        self,
        zip_path: str,
        extract_dir: Optional[str] = None
    ) -> str:
        """
        Extract shapefile from a ZIP archive.
        
        Args:
            zip_path: Path to ZIP file
            extract_dir: Directory to extract to (default: temp directory)
        
        Returns:
            Path to extracted .shp file
        
        Raises:
            ValueError: If ZIP is invalid or contains no shapefile
        """
        if not is_zipfile(zip_path):
            raise ValueError(f"Not a valid ZIP file: {zip_path}")
        
        # Create extraction directory
        if extract_dir is None:
            import tempfile
            extract_dir = tempfile.mkdtemp(prefix='shapefile_')
        else:
            Path(extract_dir).mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Extracting shapefile from {zip_path} to {extract_dir}")
        
        # Extract all files
        with ZipFile(zip_path, 'r') as zip_file:
            zip_file.extractall(extract_dir)
        
        # Find .shp file
        shp_files = list(Path(extract_dir).glob("**/*.shp"))
        
        if not shp_files:
            raise ValueError(f"No .shp file found in ZIP: {zip_path}")
        
        logger.info(f"Found shapefile: {shp_files[0]}")
        return str(shp_files[0])
    
    def load_shapefile(self, shapefile_path: str) -> gpd.GeoDataFrame:
        """
        Load shapefile into GeoDataFrame.
        
        Args:
            shapefile_path: Path to .shp file
        
        Returns:
            GeoDataFrame with shapefile contents
        
        Raises:
            ValueError: If validation fails
            FileNotFoundError: If file doesn't exist
        """
        logger.info(f"Loading shapefile: {shapefile_path}")
        
        # Validate shapefile
        is_valid, error = self.validate_shapefile(shapefile_path)
        if not is_valid:
            raise ValueError(f"Shapefile validation failed: {error}")
        
        try:
            # Load with geopandas
            gdf = gpd.read_file(shapefile_path)
            
            logger.info(
                f"Loaded {len(gdf)} features with {len(gdf.columns)} attributes"
            )
            logger.info(f"Geometry type: {gdf.geometry.type.unique()}")
            logger.info(f"Original CRS: {gdf.crs}")
            
            return gdf
            
        except Exception as e:
            raise ValueError(f"Error loading shapefile: {str(e)}")
    
    def check_crs(self, gdf: gpd.GeoDataFrame) -> Optional[str]:
        """
        Check and return the current CRS of the GeoDataFrame.
        
        Args:
            gdf: GeoDataFrame to check
        
        Returns:
            CRS string or None if not set
        """
        if gdf.crs is None:
            logger.warning("GeoDataFrame has no CRS set")
            return None
        return str(gdf.crs)
    
    def convert_crs(
        self,
        gdf: gpd.GeoDataFrame,
        target_crs: Optional[str] = None
    ) -> gpd.GeoDataFrame:
        """
        Convert GeoDataFrame to target coordinate reference system.
        
        Args:
            gdf: Input GeoDataFrame
            target_crs: Target CRS (default: uses instance target_crs)
        
        Returns:
            GeoDataFrame with converted CRS
        """
        target_crs = target_crs or self.target_crs
        
        # Check current CRS
        current_crs = self.check_crs(gdf)
        
        if current_crs is None:
            logger.warning(
                f"No CRS set, assuming {target_crs}. "
                "Set CRS explicitly if this is incorrect."
            )
            gdf = gdf.set_crs(target_crs)
            return gdf
        
        # Convert if different
        if str(gdf.crs).upper() != target_crs.upper():
            logger.info(f"Converting CRS: {current_crs} → {target_crs}")
            try:
                gdf = gdf.to_crs(target_crs)
                logger.info("CRS conversion successful")
            except Exception as e:
                logger.error(f"CRS conversion failed: {str(e)}")
                raise ValueError(f"Failed to convert CRS: {str(e)}")
        else:
            logger.info(f"CRS already {target_crs}, no conversion needed")
        
        return gdf
    
    def validate_geometries(self, gdf: gpd.GeoDataFrame) -> Tuple[int, int]:
        """
        Validate geometries and report issues.
        
        Args:
            gdf: GeoDataFrame to validate
        
        Returns:
            Tuple of (valid_count, invalid_count)
        """
        total = len(gdf)
        
        # Check for null geometries
        null_geoms = gdf.geometry.isna().sum()
        
        # Check for invalid geometries
        invalid_geoms = (~gdf.geometry.is_valid).sum()
        
        valid_count = total - null_geoms - invalid_geoms
        invalid_count = null_geoms + invalid_geoms
        
        if null_geoms > 0:
            logger.warning(f"Found {null_geoms} null geometries")
        
        if invalid_geoms > 0:
            logger.warning(f"Found {invalid_geoms} invalid geometries")
        
        logger.info(
            f"Geometry validation: {valid_count}/{total} valid "
            f"({valid_count/total*100:.1f}%)"
        )
        
        return valid_count, invalid_count
    
    def fix_invalid_geometries(
        self,
        gdf: gpd.GeoDataFrame,
        buffer_distance: float = 0
    ) -> gpd.GeoDataFrame:
        """
        Attempt to fix invalid geometries using buffer(0) technique.
        
        Args:
            gdf: GeoDataFrame with potentially invalid geometries
            buffer_distance: Buffer distance for fixing (default: 0)
        
        Returns:
            GeoDataFrame with fixed geometries
        """
        gdf = gdf.copy()
        
        # Find invalid geometries
        invalid_mask = ~gdf.geometry.is_valid
        invalid_count = invalid_mask.sum()
        
        if invalid_count == 0:
            logger.info("No invalid geometries to fix")
            return gdf
        
        logger.info(f"Attempting to fix {invalid_count} invalid geometries")
        
        # Apply buffer(0) to fix
        gdf.loc[invalid_mask, 'geometry'] = (
            gdf.loc[invalid_mask, 'geometry'].buffer(buffer_distance)
        )
        
        # Check if fixed
        still_invalid = (~gdf.geometry.is_valid).sum()
        fixed = invalid_count - still_invalid
        
        logger.info(f"Fixed {fixed}/{invalid_count} invalid geometries")
        
        if still_invalid > 0:
            logger.warning(f"{still_invalid} geometries still invalid after fix attempt")
        
        return gdf
    
    def normalize_data(
        self,
        gdf: gpd.GeoDataFrame,
        column_mappings: Optional[Dict[str, List[str]]] = None
    ) -> gpd.GeoDataFrame:
        """
        Normalize column names and clean owner data.
        
        Args:
            gdf: Raw GeoDataFrame
            column_mappings: Optional custom column mappings
        
        Returns:
            Normalized GeoDataFrame
        """
        logger.info("Normalizing shapefile data")
        return normalize_parcel_data(gdf, column_mappings, clean_owners=True)
    
    def filter_by_property_type(self, gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
        """
        Filter GeoDataFrame to only include valid property types.
        
        Args:
            gdf: GeoDataFrame with normalized columns
        
        Returns:
            Filtered GeoDataFrame
        """
        if "tax_luc_description" not in gdf.columns:
            logger.warning(
                "Column 'tax_luc_description' not found. "
                "Skipping property type filtering."
            )
            return gdf
        
        initial_count = len(gdf)
        gdf_filtered = gdf[gdf["tax_luc_description"].isin(self.valid_property_types)].copy()
        filtered_count = len(gdf_filtered)
        
        logger.info(
            f"Filtered by property type: {initial_count} → {filtered_count} features "
            f"({filtered_count/initial_count*100:.1f}% kept)"
        )
        
        return gdf_filtered
    
    def process_shapefile(
        self,
        shapefile_path: str,
        convert_crs: bool = True,
        fix_geometries: bool = True,
        filter_property_types: bool = True,
        column_mappings: Optional[Dict[str, List[str]]] = None
    ) -> gpd.GeoDataFrame:
        """
        Complete shapefile processing pipeline.
        
        Loads, validates, converts, normalizes, and prepares shapefile data.
        
        Args:
            shapefile_path: Path to .shp file or .zip file
            convert_crs: Whether to convert to target CRS
            fix_geometries: Whether to attempt fixing invalid geometries
            filter_property_types: Whether to filter by valid property types
            column_mappings: Optional custom column mappings
        
        Returns:
            Processed GeoDataFrame ready for database import
        
        Raises:
            ValueError: If validation fails at any step
        
        Example:
            >>> processor = ShapefileProcessor()
            >>> gdf = processor.process_shapefile('parcels.shp')
            >>> # gdf is now ready for database insertion
        """
        logger.info(f"Starting shapefile processing pipeline for: {shapefile_path}")
        
        # Handle ZIP files
        if shapefile_path.lower().endswith('.zip'):
            logger.info("Detected ZIP file, extracting...")
            shapefile_path = self.extract_shapefile_from_zip(shapefile_path)
        
        # 1. Load shapefile
        gdf = self.load_shapefile(shapefile_path)
        logger.info(f"Step 1/6: Loaded {len(gdf)} features")
        
        # 2. Validate and fix geometries
        valid_count, invalid_count = self.validate_geometries(gdf)
        logger.info(f"Step 2/6: {valid_count} valid, {invalid_count} invalid geometries")
        
        if fix_geometries and invalid_count > 0:
            gdf = self.fix_invalid_geometries(gdf)
        
        # 3. Convert CRS
        if convert_crs:
            gdf = self.convert_crs(gdf)
            logger.info(f"Step 3/6: Converted to {self.target_crs}")
        else:
            logger.info(f"Step 3/6: Skipped CRS conversion")
        
        # 4. Normalize columns and clean owners
        gdf = self.normalize_data(gdf, column_mappings)
        logger.info(f"Step 4/6: Normalized columns and cleaned owner names")
        
        # 5. Filter by property type
        if filter_property_types:
            gdf = self.filter_by_property_type(gdf)
            logger.info(f"Step 5/6: Filtered to {len(gdf)} valid properties")
        else:
            logger.info(f"Step 5/6: Skipped property type filtering")
        
        # 6. Final validation
        is_valid, error = validate_required_columns(
            gdf,
            ['parcelpin', 'deeded_owner'],
            "Processed Shapefile"
        )
        if not is_valid:
            raise ValueError(f"Data validation failed: {error}")
        logger.info(f"Step 6/6: Validation passed")
        
        logger.info(
            f"Shapefile processing complete: {len(gdf)} features, "
            f"{len(gdf.columns)} columns ready for import"
        )
        
        return gdf
    
    def get_geometry_summary(self, gdf: gpd.GeoDataFrame) -> Dict:
        """
        Generate summary statistics for geometry data.
        
        Args:
            gdf: Processed GeoDataFrame
        
        Returns:
            Dictionary with geometry statistics
        """
        summary = {
            "total_features": len(gdf),
            "geometry_types": gdf.geometry.type.value_counts().to_dict(),
            "crs": str(gdf.crs) if gdf.crs else None,
            "bounds": gdf.total_bounds.tolist() if len(gdf) > 0 else None,
            "valid_geometries": gdf.geometry.is_valid.sum(),
            "null_geometries": gdf.geometry.isna().sum(),
        }
        
        # Add area statistics for polygons
        if any(gdf.geometry.type.isin(['Polygon', 'MultiPolygon'])):
            summary["total_area"] = float(gdf.geometry.area.sum())
            summary["avg_area"] = float(gdf.geometry.area.mean())
        
        return summary


def process_shapefile(
    shapefile_path: str,
    target_crs: str = "EPSG:4326",
    **kwargs
) -> gpd.GeoDataFrame:
    """
    Convenience function to process a shapefile in one call.
    
    Args:
        shapefile_path: Path to .shp file or .zip file
        target_crs: Target coordinate reference system
        **kwargs: Additional arguments for ShapefileProcessor
    
    Returns:
        Processed GeoDataFrame
    
    Example:
        >>> gdf = process_shapefile('cleveland_parcels.shp')
        >>> print(f"Loaded {len(gdf)} parcels")
    """
    processor = ShapefileProcessor(target_crs=target_crs)
    return processor.process_shapefile(shapefile_path, **kwargs)

