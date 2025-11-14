"""
Layer Builder Module
Builds Folium map layers from GeoDataFrame data
"""

import folium
from folium import plugins
import geopandas as gpd
import pandas as pd
from typing import List, Dict, Optional, Tuple
import logging

from mapping.styles import (
    ColorScheme,
    LayerStyles,
    PopupConfig,
    owner_to_slug
)

# Setup logging
logger = logging.getLogger(__name__)


class LayerBuilder:
    """
    Builds Folium map layers from geospatial data.
    
    Creates base context layers, per-owner layers, and ZIP-based layers
    with popups, tooltips, and styling.
    """
    
    def __init__(
        self,
        gdf: gpd.GeoDataFrame,
        target_owners: List[str],
        owner_colors: Optional[Dict[str, str]] = None
    ):
        """
        Initialize the layer builder.
        
        Args:
            gdf: GeoDataFrame with parcels (must have 'owner_clean' column)
            target_owners: List of target owner names
            owner_colors: Optional pre-generated color mapping (will generate if None)
        """
        self.gdf = gdf.copy()
        self.target_owners = target_owners
        
        # Generate colors if not provided
        if owner_colors is None:
            self.owner_colors = ColorScheme.generate_owner_colors(target_owners)
        else:
            self.owner_colors = owner_colors
        
        # Detect actual column names in the GeoDataFrame
        self._detect_column_names()
        
        # Get available popup fields
        self.popup_fields = PopupConfig.get_available_fields(gdf.columns.tolist())
        self.popup_aliases = PopupConfig.get_aliases(self.popup_fields)
        
        logger.info(
            f"LayerBuilder initialized: {len(gdf)} parcels, "
            f"{len(target_owners)} owners, {len(self.popup_fields)} popup fields"
        )
    
    def _detect_column_names(self):
        """
        Detect and standardize column names to handle variations.
        Sets instance variables for commonly used columns.
        """
        cols = self.gdf.columns.tolist()
        
        # Parcel PIN column
        self.parcel_pin_col = None
        for candidate in ['parcel_pin', 'parcelpin', 'parcel_id', 'pin', 'objectid']:
            if candidate in cols:
                self.parcel_pin_col = candidate
                break
        
        # ZIP code column
        self.zip_col = None
        for candidate in ['par_zip', 'zip', 'zip_code', 'zipcode']:
            if candidate in cols:
                self.zip_col = candidate
                break
        
        # Sales amount column
        self.sales_col = None
        for candidate in ['sales_amount', 'sales_amou', 'sale_price', 'sales']:
            if candidate in cols:
                self.sales_col = candidate
                break
        
        # Tax assessment column
        self.assess_col = None
        for candidate in ['certified_tax_total', 'tax_total', 'assessed_value', 'assessment']:
            if candidate in cols:
                self.assess_col = candidate
                break
        
        # Owner column
        self.owner_col = 'owner_clean' if 'owner_clean' in cols else None
        
        logger.debug(
            f"Column detection: parcel_pin={self.parcel_pin_col}, "
            f"zip={self.zip_col}, sales={self.sales_col}, "
            f"assess={self.assess_col}, owner={self.owner_col}"
        )
        
        # Validate required columns
        if self.owner_col is None:
            logger.error("Required column 'owner_clean' not found in GeoDataFrame")
            raise ValueError("GeoDataFrame must have 'owner_clean' column")
    
    def build_base_layer(self, name: str = "All Target Owners (context)") -> folium.GeoJson:
        """
        Build base context layer showing all target owner parcels in light grey.
        
        Args:
            name: Name for the layer
        
        Returns:
            Folium GeoJson layer
        """
        logger.info(f"Building base context layer with {len(self.gdf)} features")
        
        if self.gdf.empty:
            logger.warning("GeoDataFrame is empty, creating empty layer")
            return folium.FeatureGroup(name=f"{name} (0)")
        
        base_style = LayerStyles.get_base_style()
        
        layer = folium.GeoJson(
            self.gdf,
            name=name,
            style_function=lambda x: base_style,
            show=True  # Base layer shown by default
        )
        
        logger.debug(f"Base layer created: {name}")
        return layer
    
    def build_clustered_layer(
        self, 
        name: str = "All Parcels",
        include_popups: bool = True
    ) -> plugins.MarkerCluster:
        """
        Build a marker cluster layer showing all parcels with clustering for performance.
        Clusters are automatically created based on zoom level.
        
        Args:
            name: Name for the layer
            include_popups: Whether to include popups on markers
        
        Returns:
            Folium MarkerCluster layer
        """
        logger.info(f"Building clustered marker layer with {len(self.gdf)} features")
        
        if self.gdf.empty:
            logger.warning("GeoDataFrame is empty, creating empty cluster")
            return plugins.MarkerCluster(name=name)
        
        # Create marker cluster
        marker_cluster = plugins.MarkerCluster(
            name=name,
            overlay=True,
            control=True,
            show=True
        )
        
        # Check which popup fields are available
        available_fields = [f for f in self.popup_fields if f in self.gdf.columns]
        
        # Add markers to cluster
        for idx, row in self.gdf.iterrows():
            # Get geometry centroid for marker location
            if row.geometry is None:
                continue
                
            centroid = row.geometry.centroid
            lat, lon = centroid.y, centroid.x
            
            # Build popup HTML if fields available
            popup = None
            if available_fields and include_popups:
                # Build simple HTML popup
                popup_lines = []
                for field in available_fields:
                    if pd.notna(row.get(field)):
                        label = PopupConfig.FIELD_ALIASES.get(field, field.title())
                        value = row.get(field)
                        
                        # Convert Decimal to float for JSON serialization
                        if hasattr(value, '__float__'):
                            value = float(value)
                        
                        # Format numbers nicely
                        if isinstance(value, (int, float)):
                            if field in [self.sales_col, self.assess_col]:
                                value = f"${value:,.0f}"
                            elif isinstance(value, float):
                                value = f"{value:,.2f}"
                        
                        popup_lines.append(f"<b>{label}:</b> {value}")
                
                if popup_lines:
                    popup_html = "<br>".join(popup_lines)
                    popup = folium.Popup(popup_html, max_width=300)
            
            # Get owner color if available
            owner = row.get(self.owner_col, 'Unknown')
            color = self.owner_colors.get(owner, '#666666')
            
            # Create marker
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                popup=popup,
                color=color,
                fill=True,
                fillColor=color,
                fillOpacity=0.6,
                weight=2
            ).add_to(marker_cluster)
        
        logger.debug(f"Clustered layer created: {name} with {len(self.gdf)} markers")
        return marker_cluster
    
    def build_owner_layer(
        self,
        owner: str,
        include_popups: bool = True
    ) -> Tuple[folium.GeoJson, str]:
        """
        Build layer for a single owner.
        
        Args:
            owner: Owner name
            include_popups: Whether to include popups and tooltips
        
        Returns:
            Tuple of (Folium layer, layer slug/ID)
        """
        color = self.owner_colors.get(owner, "#666666")
        owner_slug = owner_to_slug(owner)
        
        # Filter to this owner
        subset = self.gdf[self.gdf[self.owner_col] == owner].copy()
        layer_name = f"{owner} ({len(subset)})"
        
        logger.debug(f"Building owner layer: {owner} - {len(subset)} parcels")
        
        # Handle empty subset
        if subset.empty:
            logger.debug(f"No parcels for {owner}, creating empty layer")
            layer = folium.FeatureGroup(name=layer_name, show=False)
            return layer, owner_slug
        
        # Get style for this owner
        style = LayerStyles.get_owner_style(color)
        
        # Check which popup fields are available in this subset
        available_fields = [f for f in self.popup_fields if f in subset.columns]
        
        # Build layer without popups if no fields available or disabled
        if not available_fields or not include_popups:
            logger.debug(f"Creating layer for {owner} without popups")
            layer = folium.GeoJson(
                subset,
                name=layer_name,
                style_function=lambda x, s=style: s,
                show=False  # Owner layers hidden by default
            )
            return layer, owner_slug
        
        # Keep only available fields + geometry for GeoJSON serialization
        subset_clean = subset[available_fields + ["geometry"]].copy()
        
        # Get aliases for available fields
        aliases = [PopupConfig.FIELD_ALIASES.get(f, f.title()) for f in available_fields]
        
        # Build layer with popups and tooltips
        layer = folium.GeoJson(
            subset_clean,
            name=layer_name,
            style_function=lambda x, s=style: s,
            tooltip=folium.GeoJsonTooltip(
                fields=available_fields,
                aliases=aliases,
                localize=True
            ),
            popup=folium.GeoJsonPopup(
                fields=available_fields,
                aliases=aliases,
                localize=True,
                labels=True
            ),
            show=False  # Owner layers hidden by default
        )
        
        logger.debug(f"Created owner layer with popups: {owner}")
        return layer, owner_slug
    
    def build_all_owner_layers(
        self,
        include_popups: bool = True
    ) -> Dict[str, folium.GeoJson]:
        """
        Build layers for all target owners.
        
        Args:
            include_popups: Whether to include popups and tooltips
        
        Returns:
            Dictionary mapping owner slugs to Folium layers
        """
        logger.info(f"Building layers for {len(self.target_owners)} owners")
        
        layers = {}
        for owner in self.target_owners:
            layer, slug = self.build_owner_layer(owner, include_popups)
            layers[slug] = layer
        
        logger.info(f"Created {len(layers)} owner layers")
        return layers
    
    def build_zip_layer(
        self,
        zip_code: str,
        include_popups: bool = True
    ) -> Tuple[Optional[folium.GeoJson], str]:
        """
        Build layer for a single ZIP code.
        
        Properties within the ZIP are colored by their owner.
        
        Args:
            zip_code: ZIP code
            include_popups: Whether to include popups and tooltips
        
        Returns:
            Tuple of (Folium layer or None if empty, layer ID)
        """
        layer_id = f"zip_{zip_code}"
        
        # Check if ZIP column exists
        if self.zip_col is None:
            logger.warning("ZIP column not found, cannot build ZIP layer")
            return None, layer_id
        
        # Filter to this ZIP (handle various data types)
        try:
            # Convert to float first to handle Decimal types and values like "44119.0"
            # Then to int to remove decimals, then to string for comparison
            gdf_zips = self.gdf[self.zip_col].dropna().astype(float).astype(int).astype(str)
            mask = gdf_zips == str(zip_code)
            subset = self.gdf[mask].copy()
        except Exception as e:
            logger.error(f"Error filtering ZIP {zip_code}: {e}")
            return None, layer_id
        
        layer_name = f"ZIP {zip_code} ({len(subset)})"
        
        logger.debug(f"Building ZIP layer: {zip_code} - {len(subset)} parcels")
        
        # Handle empty subset
        if subset.empty:
            logger.debug(f"No parcels in ZIP {zip_code}")
            return None, layer_id
        
        # Add owner_color column for styling
        subset["owner_color"] = subset[self.owner_col].map(self.owner_colors)
        subset["owner_color"] = subset["owner_color"].fillna("#666666")
        
        # Get available fields
        available_fields = [f for f in self.popup_fields if f in subset.columns]
        
        # Build layer without popups if no fields or disabled
        if not available_fields or not include_popups:
            logger.debug(f"Creating ZIP layer {zip_code} without popups")
            
            # Keep geometry and owner_color
            subset_clean = subset[["owner_color", "geometry"]].copy()
            
            layer = folium.GeoJson(
                subset_clean,
                name=layer_name,
                style_function=lambda feature: {
                    "color": feature["properties"].get("owner_color", "#666666"),
                    "weight": 1,
                    "fillOpacity": 0.55
                },
                show=False  # ZIP layers hidden by default
            )
            return layer, layer_id
        
        # Keep available fields + owner_color + geometry
        subset_clean = subset[available_fields + ["owner_color", "geometry"]].copy()
        
        # Get aliases
        aliases = [PopupConfig.FIELD_ALIASES.get(f, f.title()) for f in available_fields]
        
        # Build layer with popups
        layer = folium.GeoJson(
            subset_clean,
            name=layer_name,
            style_function=lambda feature: {
                "color": feature["properties"].get("owner_color", "#666666"),
                "weight": 1,
                "fillOpacity": 0.55
            },
            tooltip=folium.GeoJsonTooltip(
                fields=available_fields,
                aliases=aliases,
                localize=True
            ),
            popup=folium.GeoJsonPopup(
                fields=available_fields,
                aliases=aliases,
                localize=True,
                labels=True
            ),
            show=False  # ZIP layers hidden by default
        )
        
        logger.debug(f"Created ZIP layer with popups: {zip_code}")
        return layer, layer_id
    
    def build_all_zip_layers(
        self,
        include_popups: bool = True
    ) -> Dict[str, folium.GeoJson]:
        """
        Build layers for all ZIP codes in the data.
        
        Args:
            include_popups: Whether to include popups and tooltips
        
        Returns:
            Dictionary mapping ZIP layer IDs to Folium layers
        """
        # Check if ZIP column exists
        if self.zip_col is None:
            logger.warning("ZIP column not found, no ZIP layers built")
            return {}
        
        # Get unique ZIP codes
        try:
            # Convert to float first to handle Decimal types and values like "44119.0"
            # Then to int to remove decimals, then to string
            zip_codes = (
                self.gdf[self.zip_col]
                .dropna()
                .astype(float)
                .astype(int)
                .astype(str)
                .drop_duplicates()
                .sort_values()
                .tolist()
            )
        except Exception as e:
            logger.error(f"Error extracting ZIP codes: {e}")
            return {}
        
        logger.info(f"Building layers for {len(zip_codes)} ZIP codes")
        
        layers = {}
        for zip_code in zip_codes:
            layer, layer_id = self.build_zip_layer(zip_code, include_popups)
            if layer is not None:
                layers[layer_id] = layer
        
        logger.info(f"Created {len(layers)} ZIP layers")
        return layers
    
    def get_zip_codes(self) -> List[str]:
        """
        Get list of ZIP codes in the data.
        
        Returns:
            Sorted list of ZIP codes
        """
        if self.zip_col is None:
            return []
        
        try:
            # Convert to float first to handle Decimal types and values like "44119.0"
            # Then to int to remove decimals, then to string
            return (
                self.gdf[self.zip_col]
                .dropna()
                .astype(float)
                .astype(int)
                .astype(str)
                .drop_duplicates()
                .sort_values()
                .tolist()
            )
        except Exception:
            return []
    
    def build_all_layers(
        self,
        include_base: bool = True,
        include_owners: bool = True,
        include_zips: bool = True,
        include_popups: bool = True,
        use_clustering: bool = False
    ) -> Dict[str, any]:
        """
        Build all map layers.
        
        Args:
            include_base: Whether to include base context layer
            include_owners: Whether to include per-owner layers
            include_zips: Whether to include ZIP-based layers
            include_popups: Whether to include popups and tooltips
            use_clustering: Whether to use marker clustering for all parcels (better performance)
        
        Returns:
            Dictionary with keys:
                - 'base': Base context layer (if included)
                - 'clustered': Clustered marker layer (if use_clustering=True)
                - 'owners': Dict of owner layers (if included)
                - 'zips': Dict of ZIP layers (if included)
                - 'owner_colors': Color mapping
                - 'zip_codes': List of ZIP codes
        """
        logger.info("Building all map layers")
        
        result = {
            "owner_colors": self.owner_colors,
            "zip_codes": self.get_zip_codes()
        }
        
        if use_clustering:
            result["clustered"] = self.build_clustered_layer(include_popups=include_popups)
        elif include_base:
            result["base"] = self.build_base_layer()
        
        if include_owners:
            result["owners"] = self.build_all_owner_layers(include_popups)
        
        if include_zips:
            result["zips"] = self.build_all_zip_layers(include_popups)
        
        logger.info(
            f"Layer building complete: "
            f"base={include_base}, "
            f"owners={len(result.get('owners', {}))}, "
            f"zips={len(result.get('zips', {}))}"
        )
        
        return result


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def build_layers_from_data(
    gdf: gpd.GeoDataFrame,
    target_owners: List[str],
    include_popups: bool = True
) -> Dict[str, any]:
    """
    Convenience function to build all layers from GeoDataFrame.
    
    Args:
        gdf: GeoDataFrame with parcel data
        target_owners: List of target owner names
        include_popups: Whether to include popups and tooltips
    
    Returns:
        Dictionary with all layers and metadata
    
    Example:
        >>> layers = build_layers_from_data(gdf, ['SMITH', 'JONES'])
        >>> base_layer = layers['base']
        >>> owner_layers = layers['owners']
    """
    builder = LayerBuilder(gdf, target_owners)
    return builder.build_all_layers(include_popups=include_popups)
