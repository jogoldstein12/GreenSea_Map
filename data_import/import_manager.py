"""
Import Manager Module
Orchestrates the data import process for new cities
"""

import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional, Tuple, Any, List
from datetime import datetime
import logging

import pandas as pd
import geopandas as gpd
from sqlalchemy.orm import Session

from database.db_manager import db_manager
from database.models import City, CityConfig, Parcel, TargetOwner, ImportHistory
from data_processing.csv_processor import CSVProcessor
from data_processing.shapefile_processor import ShapefileProcessor
from data_processing.excel_processor import ExcelProcessor
from data_processing.normalizer import clean_owner

# Setup logging
logger = logging.getLogger(__name__)


class ImportManager:
    """
    Manages the complete data import process for a new city.
    
    Orchestrates CSV processing, shapefile processing, Excel processing,
    database transactions, and error handling.
    """
    
    def __init__(self):
        """Initialize the import manager."""
        self.import_batch = self._generate_batch_id()
        self.temp_dir = None
        self.temp_files = []
        
    def _generate_batch_id(self) -> str:
        """
        Generate a unique import batch ID.
        
        Returns:
            Unique batch identifier (timestamp + UUID)
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_id = str(uuid.uuid4())[:8]
        return f"{timestamp}_{unique_id}"
    
    def _convert_column_mappings(self, ui_mappings: Dict[str, str]) -> Dict[str, List[str]]:
        """
        Convert column mappings from UI format to processor format.
        
        UI format: {'pin': 'PARCEL_PIN', 'owner': 'DEEDED_OWN', ...}
        Processor format: {'parcelpin': ['PARCEL_PIN', 'parcelpin', 'PARCELPIN'], 'deeded_owner': ['DEEDED_OWN', 'deeded_owner', 'deeded_own'], ...}
        
        Includes multiple possible column name variations to handle differences between
        CSV and shapefile column names (e.g., truncated names, case variations).
        
        Args:
            ui_mappings: Column mappings from the upload wizard
            
        Returns:
            Column mappings in processor format with multiple possible source columns
        """
        # Map UI field names to processor field names + common variations
        # Format: ui_field -> (standard_field, [list of possible source column variations])
        field_variations = {
            'pin': ('parcelpin', [
                'parcelpin', 'PARCELPIN', 'parcel_pin', 'PARCEL_PIN',
                'pin', 'PIN', 'parcel_id', 'PARCEL_ID', 'parcel_number'
            ]),
            'owner': ('deeded_owner', [
                'deeded_owner', 'DEEDED_OWNER', 'deeded_own', 'DEEDED_OWN',
                'deed_owner', 'DEED_OWNER', 'owner', 'OWNER',
                'owner_name', 'OWNER_NAME', 'ownername', 'OWNERNAME',
                'mail_name', 'MAIL_NAME'
            ]),
            'type': ('tax_luc_description', [
                'tax_luc_description', 'TAX_LUC_DESCRIPTION',
                'tax_luc_de', 'TAX_LUC_DE',
                'tax_luc', 'TAX_LUC',
                'ext_luc_de', 'EXT_LUC_DE',
                'land_use', 'LAND_USE',
                'property_type', 'PROPERTY_TYPE'
            ]),
            'address': ('par_addr', [
                'par_addr', 'PAR_ADDR',
                'par_addr_a', 'PAR_ADDR_A',
                'address', 'ADDRESS',
                'street_address', 'STREET_ADDRESS',
                'property_address', 'PROPERTY_ADDRESS'
            ]),
            'zip': ('par_zip', [
                'par_zip', 'PAR_ZIP',
                'zip_code', 'ZIP_CODE',
                'zipcode', 'ZIPCODE',
                'postal_code', 'POSTAL_CODE',
                'zip', 'ZIP'
            ]),
            'sales': ('sales_amount', [
                'sales_amount', 'SALES_AMOUNT',
                'sales_amou', 'SALES_AMOU',  # Truncated version
                'sale_price', 'SALE_PRICE',
                'last_sale', 'LAST_SALE',
                'sales', 'SALES'
            ]),
            'tax': ('certified_tax_total', [
                'certified_tax_total', 'CERTIFIED_TAX_TOTAL',
                'certified_', 'CERTIFIED_',  # Truncated version
                'tax_total', 'TAX_TOTAL',
                'assessed_value', 'ASSESSED_VALUE',
                'tax_value', 'TAX_VALUE'
            ])
        }
        
        processor_mappings = {}
        for ui_field, user_column in ui_mappings.items():
            if ui_field in field_variations:
                standard_field, common_variations = field_variations[ui_field]
                
                # Put user's selected column first, then add common variations
                # (avoiding duplicates)
                column_list = [user_column]
                for variation in common_variations:
                    if variation.lower() != user_column.lower():
                        column_list.append(variation)
                
                processor_mappings[standard_field] = column_list
                logger.debug(
                    f"Mapped user column '{user_column}' to standard field '{standard_field}' "
                    f"with {len(column_list)-1} fallback variations"
                )
        
        return processor_mappings
    
    def _create_temp_directory(self) -> Path:
        """
        Create a temporary directory for file processing.
        
        Returns:
            Path to temporary directory
        """
        if self.temp_dir is None:
            self.temp_dir = Path(tempfile.mkdtemp(prefix="import_"))
        return self.temp_dir
    
    def _save_uploaded_file(self, uploaded_file, suffix: str = "") -> Path:
        """
        Save an uploaded Streamlit file to temporary storage.
        
        Args:
            uploaded_file: Streamlit UploadedFile object
            suffix: Optional file suffix/extension
            
        Returns:
            Path to saved temporary file
        """
        temp_dir = self._create_temp_directory()
        
        # Generate unique filename
        filename = f"{uuid.uuid4().hex}_{uploaded_file.name}"
        temp_path = temp_dir / filename
        
        # Write file
        with open(temp_path, 'wb') as f:
            f.write(uploaded_file.getbuffer())
        
        self.temp_files.append(temp_path)
        logger.info(f"Saved uploaded file: {temp_path}")
        
        return temp_path
    
    def _cleanup_temp_files(self):
        """
        Clean up all temporary files and directories.
        """
        for temp_file in self.temp_files:
            try:
                if temp_file.exists():
                    temp_file.unlink()
                    logger.debug(f"Deleted temp file: {temp_file}")
            except Exception as e:
                logger.warning(f"Could not delete temp file {temp_file}: {e}")
        
        if self.temp_dir and self.temp_dir.exists():
            try:
                self.temp_dir.rmdir()
                logger.debug(f"Deleted temp directory: {self.temp_dir}")
            except Exception as e:
                logger.warning(f"Could not delete temp directory {self.temp_dir}: {e}")
        
        self.temp_files = []
        self.temp_dir = None
    
    def import_city_data(
        self,
        city_info: Dict[str, Any],
        uploaded_files: Dict[str, Any],
        column_mappings: Dict[str, str],
        property_types: Dict[str, bool],
        session: Optional[Session] = None
    ) -> Tuple[bool, str, Dict[str, int]]:
        """
        Import complete city data including parcels and target owners.
        
        This is the main entry point for the import process. It coordinates
        all import operations and manages the database transaction.
        
        Args:
            city_info: Dictionary with city details (name, coordinates, etc.)
            uploaded_files: Dictionary with CSV, shapefile, and Excel files
            column_mappings: Dictionary mapping source columns to standard names
            property_types: Dictionary of property types to include (type: bool)
            session: Optional database session (creates new if not provided)
            
        Returns:
            Tuple of (success: bool, message: str, counts: dict)
            - success: True if import succeeded
            - message: Success or error message
            - counts: Dictionary with record counts (parcels, owners, etc.)
        """
        counts = {
            'parcels': 0,
            'target_owners': 0,
            'city_created': False
        }
        
        city_id = None
        use_external_session = session is not None
        
        try:
            # Create session if not provided
            if session is None:
                session = db_manager.SessionLocal()
            
            logger.info(f"Starting import for city: {city_info.get('city_name')}")
            logger.info(f"Import batch ID: {self.import_batch}")
            
            # Step 1: Create city record
            city_id = self._create_city(session, city_info)
            counts['city_created'] = True
            logger.info(f"Created city with ID: {city_id}")
            
            # Step 2: Create city configuration
            self._create_city_config(
                session, 
                city_id, 
                column_mappings, 
                property_types,
                uploaded_files
            )
            logger.info(f"Created city configuration")
            
            # Step 3: Import parcels (CSV + Shapefile merge)
            parcel_count = self._import_parcels(
                session,
                city_id,
                uploaded_files['csv'],
                uploaded_files['shp'],
                column_mappings,
                property_types
            )
            counts['parcels'] = parcel_count
            logger.info(f"Imported {parcel_count} parcels")
            
            # Step 4: Import target owners
            owner_count = self._import_target_owners(
                session,
                city_id,
                uploaded_files['excel']
            )
            counts['target_owners'] = owner_count
            logger.info(f"Imported {owner_count} target owners")
            
            # Step 5: Log import history
            self._log_import_history(
                session,
                city_id,
                'full',
                uploaded_files,
                counts,
                'success',
                None
            )
            
            # Commit transaction if we created the session
            if not use_external_session:
                session.commit()
                logger.info("Import transaction committed successfully")
            
            # Clean up temp files
            self._cleanup_temp_files()
            
            success_message = (
                f"✅ Import complete! "
                f"City '{city_info.get('display_name')}' added with "
                f"{counts['parcels']:,} parcels and "
                f"{counts['target_owners']} target investors."
            )
            
            return True, success_message, counts
            
        except Exception as e:
            # Rollback on error
            if not use_external_session and session:
                session.rollback()
                logger.error(f"Import failed, transaction rolled back: {e}")
            
            # Log failed import
            if city_id:
                try:
                    self._log_import_history(
                        session,
                        city_id,
                        'full',
                        uploaded_files,
                        counts,
                        'failed',
                        str(e)
                    )
                    if not use_external_session:
                        session.commit()
                except Exception as log_error:
                    logger.error(f"Could not log import failure: {log_error}")
            
            # Clean up temp files
            self._cleanup_temp_files()
            
            error_message = f"❌ Import failed: {str(e)}"
            logger.exception("Import error details:")
            
            return False, error_message, counts
            
        finally:
            # Close session if we created it
            if not use_external_session and session:
                session.close()
    
    def _create_city(self, session: Session, city_info: Dict[str, Any]) -> int:
        """
        Create a new city record in the database.
        
        Args:
            session: Database session
            city_info: Dictionary with city details
            
        Returns:
            Created city ID
            
        Raises:
            ValueError: If city name already exists
        """
        # Check if city already exists
        existing_city = session.query(City).filter(
            City.city_name == city_info['city_name']
        ).first()
        
        if existing_city:
            raise ValueError(
                f"City '{city_info['city_name']}' already exists. "
                "Please use a different name or delete the existing city first."
            )
        
        # Create new city
        city = City(
            city_name=city_info['city_name'],
            display_name=city_info['display_name'],
            state=city_info.get('state'),
            center_lat=city_info['center_lat'],
            center_lng=city_info['center_lng'],
            zoom_level=city_info.get('zoom_level', 11),
            is_active=True
        )
        
        session.add(city)
        session.flush()  # Get city_id without committing
        
        return city.city_id
    
    def _create_city_config(
        self,
        session: Session,
        city_id: int,
        column_mappings: Dict[str, str],
        property_types: Dict[str, bool],
        uploaded_files: Dict[str, Any]
    ):
        """
        Create city configuration record.
        
        Args:
            session: Database session
            city_id: ID of the city
            column_mappings: Column mapping dictionary
            property_types: Property types dictionary
            uploaded_files: Uploaded files dictionary
        """
        # Filter to only selected property types
        valid_types = [k for k, v in property_types.items() if v]
        
        # Prepare file metadata
        file_metadata = {
            'csv': {
                'name': uploaded_files['csv'].name,
                'size': uploaded_files['csv'].size
            },
            'shapefile': {
                'name': uploaded_files['shp'].name,
                'size': uploaded_files['shp'].size
            },
            'excel': {
                'name': uploaded_files['excel'].name,
                'size': uploaded_files['excel'].size
            },
            'upload_date': datetime.now().isoformat()
        }
        
        # Create config
        config = CityConfig(
            city_id=city_id,
            valid_property_types=valid_types,
            column_mappings=column_mappings,
            data_sources=file_metadata
        )
        
        session.add(config)
        session.flush()
    
    def _import_parcels(
        self,
        session: Session,
        city_id: int,
        csv_file,
        shapefile_zip,
        column_mappings: Dict[str, str],
        property_types: Dict[str, bool]
    ) -> int:
        """
        Import parcel data from CSV and shapefile.
        
        Processes CSV and shapefile, merges them on parcel_pin,
        applies column mappings and property type filters, then
        bulk inserts into the database.
        
        Args:
            session: Database session
            city_id: ID of the city
            csv_file: Uploaded CSV file
            shapefile_zip: Uploaded shapefile ZIP
            column_mappings: Column mappings
            property_types: Property types to include
            
        Returns:
            Number of parcels imported
            
        Raises:
            ValueError: If files cannot be processed or merged
        """
        logger.info("Starting parcel import...")
        
        # Save uploaded files to temp storage
        csv_path = self._save_uploaded_file(csv_file, suffix='.csv')
        shp_zip_path = self._save_uploaded_file(shapefile_zip, suffix='.zip')
        
        # Filter to only selected property types
        valid_types = [k for k, v in property_types.items() if v]
        
        if not valid_types:
            raise ValueError("No property types selected. Please select at least one property type.")
        
        # Convert column mappings from UI format to processor format
        # UI format: {'pin': 'PARCEL_PIN', 'owner': 'DEEDED_OWN', ...}
        # Processor format: {'parcelpin': ['PARCEL_PIN'], 'deeded_owner': ['DEEDED_OWN'], ...}
        processor_mappings = self._convert_column_mappings(column_mappings)
        
        # Process CSV - complete pipeline
        logger.info(f"Processing CSV: {csv_path}")
        csv_processor = CSVProcessor(valid_property_types=valid_types)
        csv_df = csv_processor.process_csv(
            file_path=str(csv_path),
            filter_property_types=True,
            column_mappings=processor_mappings
        )
        
        logger.info(f"Processed {len(csv_df):,} records from CSV")
        
        # Process Shapefile - complete pipeline (handles ZIP extraction)
        logger.info(f"Processing shapefile: {shp_zip_path}")
        shp_processor = ShapefileProcessor(
            target_crs='EPSG:4326',
            valid_property_types=valid_types
        )
        shp_gdf = shp_processor.process_shapefile(
            shapefile_path=str(shp_zip_path),
            convert_crs=True,
            fix_geometries=True,
            filter_property_types=True,
            column_mappings=processor_mappings
        )
        
        logger.info(f"Processed {len(shp_gdf):,} geometries from shapefile")
        
        # Both processors have already normalized columns to standard names
        # Standard column name is 'parcelpin' (not 'parcel_pin')
        pin_column = 'parcelpin'
        
        # Verify pin column exists in both datasets
        if pin_column not in csv_df.columns:
            raise ValueError(
                f"Parcel PIN column '{pin_column}' not found in CSV after processing. "
                f"Available columns: {', '.join(csv_df.columns)}"
            )
        
        if pin_column not in shp_gdf.columns:
            raise ValueError(
                f"Parcel PIN column '{pin_column}' not found in shapefile after processing. "
                f"Available columns: {', '.join(shp_gdf.columns)}"
            )
        
        # Merge CSV data with shapefile geometries on parcelpin
        logger.info(f"Merging data on column: {pin_column}")
        merged_gdf = shp_gdf.merge(
            csv_df,
            on=pin_column,
            how='inner',
            suffixes=('_shp', '_csv')
        )
        
        if merged_gdf.empty:
            raise ValueError(
                f"No matching records found when merging CSV and shapefile on '{pin_column}'. "
                "Please verify that parcel PINs match between files."
            )
        
        logger.info(f"Merged dataset contains {len(merged_gdf):,} parcels")
        
        # Handle suffix conflicts from merge (_shp and _csv columns)
        # Prefer CSV data where both exist, as it usually has better quality
        conflicted_columns = ['deeded_owner', 'owner_clean', 'sales_amount', 'certified_tax_total', 'par_zip', 'address', 'tax_luc_description']
        for col in conflicted_columns:
            csv_col = f'{col}_csv'
            shp_col = f'{col}_shp'
            
            if csv_col in merged_gdf.columns and shp_col in merged_gdf.columns:
                # Coalesce: use CSV value if not null, otherwise use shapefile value
                merged_gdf[col] = merged_gdf[csv_col].fillna(merged_gdf[shp_col])
                # Drop the suffixed columns
                merged_gdf = merged_gdf.drop(columns=[csv_col, shp_col])
                logger.info(f"Merged conflicted column: {col} (preferred CSV data)")
            elif csv_col in merged_gdf.columns:
                # Only CSV version exists, rename it
                merged_gdf[col] = merged_gdf[csv_col]
                merged_gdf = merged_gdf.drop(columns=[csv_col])
                logger.info(f"Used CSV column: {col}")
            elif shp_col in merged_gdf.columns:
                # Only shapefile version exists, rename it
                merged_gdf[col] = merged_gdf[shp_col]
                merged_gdf = merged_gdf.drop(columns=[shp_col])
                logger.info(f"Used shapefile column: {col}")
        
        # Processors have already normalized columns, but we need to rename for database
        # The processors use lowercase names, database expects specific names
        column_rename = {
            'parcelpin': 'parcel_pin',
            'par_addr': 'address',
            'par_zip': 'par_zip',  # Already correct
            'deeded_owner': 'deeded_owner',  # Already correct
            'owner_clean': 'owner_clean',  # Already correct
            'tax_luc_description': 'tax_luc_description',  # Already correct
            'sales_amou': 'sales_amount',  # Truncated in some datasets
            'sales_amount': 'sales_amount',  # Already correct
            'certified_tax_total': 'certified_tax_total'  # Already correct
        }
        
        # Only rename columns that exist
        rename_map = {k: v for k, v in column_rename.items() if k in merged_gdf.columns}
        if rename_map:
            merged_gdf = merged_gdf.rename(columns=rename_map)
            logger.info(f"Renamed columns for database: {rename_map}")
        
        # Ensure required columns exist
        required_columns = ['parcel_pin', 'geometry']
        missing_columns = [col for col in required_columns if col not in merged_gdf.columns]
        if missing_columns:
            raise ValueError(f"Missing required columns after processing: {missing_columns}")
        
        # Create owner_clean column if it doesn't exist
        if 'owner_clean' not in merged_gdf.columns and 'deeded_owner' in merged_gdf.columns:
            logger.info("Creating owner_clean from deeded_owner...")
            merged_gdf['owner_clean'] = merged_gdf['deeded_owner'].apply(clean_owner)
            logger.info(f"Created owner_clean for {merged_gdf['owner_clean'].notna().sum():,} parcels")
        
        # Prepare parcel records for bulk insert
        parcel_records = []
        for _, row in merged_gdf.iterrows():
            parcel_dict = {
                'city_id': city_id,
                'parcel_pin': row.get('parcel_pin'),
                'geometry': row['geometry'].wkt if hasattr(row['geometry'], 'wkt') else str(row['geometry']),
                'address': row.get('address'),
                'par_zip': str(row.get('par_zip')) if pd.notna(row.get('par_zip')) else None,
                'deeded_owner': row.get('deeded_owner'),
                'owner_clean': row.get('owner_clean'),
                'tax_luc_description': row.get('tax_luc_description'),
                'sales_amount': float(row.get('sales_amount')) if pd.notna(row.get('sales_amount')) else None,
                'certified_tax_total': float(row.get('certified_tax_total')) if pd.notna(row.get('certified_tax_total')) else None,
                'source_file': csv_file.name,
                'import_batch': self.import_batch
            }
            
            parcel_records.append(Parcel(**parcel_dict))
        
        # Bulk insert in batches of 1000
        logger.info(f"Inserting {len(parcel_records):,} parcels in batches of 1000...")
        batch_size = 1000
        total_inserted = 0
        
        for i in range(0, len(parcel_records), batch_size):
            batch = parcel_records[i:i + batch_size]
            session.bulk_save_objects(batch)
            session.flush()
            total_inserted += len(batch)
            logger.info(f"Inserted batch {i//batch_size + 1}: {total_inserted:,}/{len(parcel_records):,} parcels")
        
        logger.info(f"Successfully imported {total_inserted:,} parcels")
        return total_inserted
    
    def _import_target_owners(
        self,
        session: Session,
        city_id: int,
        excel_file
    ) -> int:
        """
        Import target owners from Excel file.
        
        Processes Excel file, cleans owner names, and creates
        TargetOwner records in the database.
        
        Args:
            session: Database session
            city_id: ID of the city
            excel_file: Uploaded Excel file
            
        Returns:
            Number of target owners imported
            
        Raises:
            ValueError: If Excel file cannot be processed
        """
        logger.info("Starting target owners import...")
        
        # Save uploaded file to temp storage
        excel_path = self._save_uploaded_file(excel_file, suffix='.xlsx')
        
        # Process Excel file
        logger.info(f"Processing Excel file: {excel_path}")
        excel_processor = ExcelProcessor()
        
        # Load Excel file
        df = excel_processor.load_excel(str(excel_path))
        
        if df is None or df.empty:
            logger.warning("Excel file is empty or could not be loaded")
            return 0
        
        # Extract owner names
        owner_list = excel_processor.extract_owners(df)
        
        if not owner_list:
            logger.warning("No owner names found in Excel file")
            return 0
        
        logger.info(f"Found {len(owner_list)} potential target owners")
        
        # Get existing target owners for this city (to handle duplicates)
        existing_owners = session.query(TargetOwner.owner_clean).filter(
            TargetOwner.city_id == city_id
        ).all()
        existing_owner_set = {owner[0] for owner in existing_owners}
        
        logger.info(f"Found {len(existing_owner_set)} existing target owners for this city")
        
        # Create TargetOwner records
        new_owners = []
        skipped_count = 0
        
        for owner_name in owner_list:
            # Owner names are already cleaned by ExcelProcessor
            owner_clean = owner_name
            
            # Skip duplicates
            if owner_clean in existing_owner_set:
                logger.debug(f"Skipping duplicate owner: {owner_clean}")
                skipped_count += 1
                continue
            
            # Create new target owner record
            target_owner = TargetOwner(
                city_id=city_id,
                owner_clean=owner_clean,
                is_active=True
            )
            
            new_owners.append(target_owner)
            existing_owner_set.add(owner_clean)  # Prevent duplicates within this import
        
        # Bulk insert new owners
        if new_owners:
            session.bulk_save_objects(new_owners)
            session.flush()
            logger.info(f"Inserted {len(new_owners)} new target owners")
        
        if skipped_count > 0:
            logger.info(f"Skipped {skipped_count} duplicate owners")
        
        total_imported = len(new_owners)
        logger.info(f"Successfully imported {total_imported} target owners")
        
        return total_imported
    
    def _log_import_history(
        self,
        session: Session,
        city_id: int,
        import_type: str,
        uploaded_files: Dict[str, Any],
        counts: Dict[str, int],
        status: str,
        error_log: Optional[str]
    ):
        """
        Log import history to database.
        
        Args:
            session: Database session
            city_id: ID of the city
            import_type: Type of import ('full', 'parcels', 'targets')
            uploaded_files: Dictionary of uploaded files
            counts: Dictionary of record counts
            status: Import status ('success', 'failed', 'partial')
            error_log: Error message if failed
        """
        file_names = ", ".join([
            f"{k}: {v.name}" for k, v in uploaded_files.items()
        ])
        
        history = ImportHistory(
            city_id=city_id,
            import_type=import_type,
            file_name=file_names,
            records_imported=counts.get('parcels', 0) + counts.get('target_owners', 0),
            status=status,
            error_log=error_log,
            imported_by='streamlit_user',  # TODO: Add user authentication
            import_batch=self.import_batch
        )
        
        session.add(history)
        session.flush()

