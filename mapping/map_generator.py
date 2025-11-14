"""
Map Generator Module
Creates interactive Folium maps with portfolio layers, statistics sidebar, and JavaScript controls
"""

import folium
import geopandas as gpd
import pandas as pd
from typing import Dict, List, Optional, Any
import logging
from folium import Element

from mapping.layer_builder import LayerBuilder
from mapping.styles import (
    ColorScheme,
    MapConfig,
    owner_to_slug,
    sanitize_for_html
)

# Setup logging
logger = logging.getLogger(__name__)


class MapGenerator:
    """
    Generates interactive Folium maps with portfolio visualization.
    
    Creates maps with base layers, per-owner layers, ZIP-based layers,
    a statistics sidebar, and JavaScript controls for layer toggling.
    """
    
    def __init__(
        self,
        city_config: Dict[str, Any],
        parcels_gdf: gpd.GeoDataFrame,
        target_owners: List[str],
        stats_per_owner: Dict[str, Dict],
        all_stats: Dict[str, Any]
    ):
        """
        Initialize the map generator.
        
        Args:
            city_config: Dictionary with city configuration
                - center_lat: Center latitude
                - center_lng: Center longitude
                - zoom_level: Default zoom level (default: 11)
                - display_name: City display name (optional)
            parcels_gdf: GeoDataFrame with parcels (must have 'owner_clean' column)
            target_owners: List of target owner names
            stats_per_owner: Dictionary mapping owner names to their statistics
            all_stats: Aggregate statistics for all target owners
        """
        self.city_config = city_config
        self.parcels_gdf = parcels_gdf
        self.target_owners = target_owners
        self.stats_per_owner = stats_per_owner
        self.all_stats = all_stats
        
        # Generate colors
        self.owner_colors = ColorScheme.generate_owner_colors(target_owners)
        
        # Initialize layer builder
        self.layer_builder = LayerBuilder(
            parcels_gdf,
            target_owners,
            self.owner_colors
        )
        
        logger.info(
            f"MapGenerator initialized for {city_config.get('display_name', 'Unknown City')}: "
            f"{len(parcels_gdf)} parcels, {len(target_owners)} target owners"
        )
    
    def generate_map(
        self,
        include_layer_control: bool = True,
        tile_layer: str = "light",
        use_clustering: bool = False,
        view_mode: str = "By Owner",
        include_zip_layers: bool = False
    ) -> folium.Map:
        """
        Generate the complete Folium map with all layers and controls.

        Args:
            include_layer_control: Whether to add Folium's layer control
            tile_layer: Base tile layer to use (light, dark, osm, satellite)
            use_clustering: Whether to use marker clustering (better for large datasets)
            view_mode: Initial view mode ("By Owner" or "By ZIP")
            include_zip_layers: Whether to build ZIP code layers (False by default for performance)

        Returns:
            Folium Map object
        """
        logger.info(f"Generating Folium map (clustering={use_clustering}, view_mode={view_mode}, include_zip_layers={include_zip_layers})")

        # Create base map
        m = self._create_base_map(tile_layer)

        # Build and add all layers
        # Note: ZIP layers are disabled by default as they can significantly slow down generation
        # when there are many ZIP codes (50-100+)
        layers = self.layer_builder.build_all_layers(
            include_popups=True,
            use_clustering=use_clustering,
            include_zips=include_zip_layers
        )
        
        # Add clustered layer if using clustering
        if "clustered" in layers:
            layers["clustered"].add_to(m)
            base_layer_name = None  # Clustering replaces base layer
        # Otherwise add base context layer
        elif "base" in layers:
            layers["base"].add_to(m)
            base_layer_name = layers["base"].get_name()
        else:
            base_layer_name = None
        
        # Add owner layers
        owner_layer_names = {}
        if "owners" in layers:
            for slug, layer in layers["owners"].items():
                layer.add_to(m)
                owner_layer_names[slug] = layer.get_name()
        
        # Add ZIP layers (but don't show by default)
        zip_layer_names = {}
        zip_codes = layers.get("zip_codes", [])
        if "zips" in layers:
            for zip_id, layer in layers["zips"].items():
                # Note: ZIP layers are NOT added to map yet; toggled via JavaScript
                zip_layer_names[zip_id] = layer.get_name()
        
        # Add layer control if requested
        if include_layer_control:
            folium.LayerControl(
                position=MapConfig.LAYER_CONTROL["position"],
                collapsed=MapConfig.LAYER_CONTROL["collapsed"]
            ).add_to(m)
        
        # Generate and inject sidebar HTML
        sidebar_html = self._generate_sidebar_html(zip_codes, view_mode)
        m.get_root().html.add_child(Element(sidebar_html))
        
        # Generate and inject JavaScript for layer toggling
        toggle_js = self._generate_toggle_javascript(
            m.get_name(),
            base_layer_name,
            owner_layer_names,
            zip_layer_names,
            zip_codes,
            view_mode
        )
        m.get_root().script.add_child(Element(toggle_js))
        
        logger.info("Map generation complete")
        return m
    
    def _create_base_map(self, tile_layer: str = "light") -> folium.Map:
        """
        Create the base Folium map.
        
        Args:
            tile_layer: Tile layer type
        
        Returns:
            Folium Map object
        """
        center_lat = float(self.city_config.get("center_lat", 41.4993))
        center_lng = float(self.city_config.get("center_lng", -81.6944))
        zoom = int(self.city_config.get("zoom_level", MapConfig.DEFAULT_ZOOM))
        
        tile_config = MapConfig.get_tile_config(tile_layer)
        
        m = folium.Map(
            location=[center_lat, center_lng],
            zoom_start=zoom,
            tiles=tile_config["tiles"]
        )
        
        logger.debug(f"Created base map at [{center_lat}, {center_lng}] zoom {zoom}")
        return m
    
    def _generate_sidebar_html(self, zip_codes: List[str], view_mode: str = "By Owner") -> str:
        """
        Generate HTML for the statistics sidebar.
        
        Args:
            zip_codes: List of ZIP codes in the data
            view_mode: Initial view mode ("By Owner" or "By ZIP")
        
        Returns:
            HTML string for sidebar
        """
        logger.debug(f"Generating sidebar HTML (view_mode={view_mode})")
        
        # Determine which mode should be checked initially
        owner_checked = 'checked' if view_mode == "By Owner" else ''
        zip_checked = 'checked' if view_mode == "By ZIP" else ''
        
        # Determine initial visibility of controls
        owner_display = 'block' if view_mode == "By Owner" else 'none'
        zip_display = 'block' if view_mode == "By ZIP" else 'none'
        
        # Generate owner options for datalist
        owner_options = "".join(
            f"<option value='{sanitize_for_html(owner)}'>"
            for owner in self.target_owners
        )
        
        # Generate owner select options
        owner_select_options = "".join(
            f"<option value='{owner_to_slug(owner)}'>{sanitize_for_html(owner)}</option>"
            for owner in self.target_owners
        )
        
        # Generate ZIP select options
        zip_select_options = "".join(
            f"<option value='zip_{zip_code}'>ZIP {zip_code}</option>"
            for zip_code in zip_codes
        )
        
        # Generate stat panels
        stat_panels = self._generate_all_stat_panels(zip_codes)
        
        # Build complete sidebar HTML
        sidebar = f"""
        <style>
        {self._get_sidebar_css()}
        </style>
        
        <div id="gs-sidebar">
          <h2>Portfolio Viewer</h2>
          <div class="gs-description">
            Select a target owner to see portfolio stats. Toggle map layers on the right to compare footprints.
          </div>
          
          <div class="gs-mode-toggle">
            <label>
              <input type="radio" name="gsMode" id="mode_owner" value="owner" {owner_checked} onchange="gsModeChanged()">
              By Portfolio
            </label>
            <label>
              <input type="radio" name="gsMode" id="mode_zip" value="zip" {zip_checked} onchange="gsModeChanged()">
              By ZIP
            </label>
          </div>
          
          <label for="ownerSearch" style="display:{owner_display};">Search portfolio:</label>
          <input id="ownerSearch" list="ownerSuggestions" type="text" 
                 placeholder="Type to search..." oninput="gsTypeOwner()" style="display:{owner_display};" />
          <datalist id="ownerSuggestions">
            {owner_options}
          </datalist>
          
          <label for="ownerSelect" style="display:{owner_display};">Select portfolio:</label>
          <select id="ownerSelect" onchange="gsShowOwner(); if (typeof gsToggleLayers==='function') {{ gsToggleLayers(); }}" style="display:{owner_display};">
            <option value="all">All Target Owners</option>
            {owner_select_options}
          </select>
          
          <label for="zipSelect" style="display:{zip_display};">Select ZIP:</label>
          <select id="zipSelect" onchange="gsShowZip(); if (typeof gsToggleLayers==='function') {{ gsToggleLayers(); }}" style="display:{zip_display};">
            <option value="all">All ZIPs</option>
            {zip_select_options}
          </select>
          
          <div id="gs-panels">
            {stat_panels}
          </div>
        </div>
        
        <script>
        {self._get_sidebar_javascript()}
        </script>
        """
        
        return sidebar
    
    def _generate_all_stat_panels(self, zip_codes: List[str]) -> str:
        """
        Generate HTML for all statistics panels (owners and ZIPs).
        
        Args:
            zip_codes: List of ZIP codes
        
        Returns:
            HTML string with all panels
        """
        # All target owners panel (default view)
        all_panel = self._generate_owner_panel(
            "All Target Owners",
            self.all_stats,
            panel_id="owner_all",
            visible=True
        )
        
        # Individual owner panels
        owner_panels = "".join(
            self._generate_owner_panel(
                owner, 
                self.stats_per_owner.get(owner, {
                    'count': 0,
                    'total_sales': 0,
                    'total_assess': 0,
                    'avg_sales': 0,
                    'avg_assess': 0,
                    'zip_table': None
                })
            )
            for owner in self.target_owners
        )
        
        # ZIP panels
        zip_panels = "".join(
            self._generate_zip_panel(zip_code)
            for zip_code in zip_codes
        ) if zip_codes else ""
        
        return all_panel + owner_panels + zip_panels
    
    def _generate_owner_panel(
        self,
        owner: str,
        stats: Dict[str, Any],
        panel_id: Optional[str] = None,
        visible: bool = False
    ) -> str:
        """
        Generate HTML for a single owner statistics panel.
        
        Args:
            owner: Owner name
            stats: Statistics dictionary for this owner
            panel_id: HTML ID for panel (auto-generated if None)
            visible: Whether panel should be visible by default
        
        Returns:
            HTML string
        """
        if panel_id is None:
            panel_id = owner_to_slug(owner)
        
        display_style = "block" if visible else "none"
        
        # Format numbers
        count = int(stats.get("count", 0))
        total_sales = self._format_money(stats.get("total_sales", 0))
        total_assess = self._format_money(stats.get("total_assess", 0))
        avg_sales = self._format_money(stats.get("avg_sales", 0))
        avg_assess = self._format_money(stats.get("avg_assess", 0))
        
        # Generate ZIP breakdown table
        zip_table_html = self._generate_zip_table(stats.get("zip_table"))
        
        return f"""
        <div class="stats owner" id="{panel_id}" style="display:{display_style};">
          <h3>{sanitize_for_html(owner)}</h3>
          <div class="stat-row">
            <span class="stat-label">Properties:</span>
            <span class="stat-value">{count}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Total Sales:</span>
            <span class="stat-value">{total_sales}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Total Assessed:</span>
            <span class="stat-value">{total_assess}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Avg Sales:</span>
            <span class="stat-value">{avg_sales}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Avg Assessed:</span>
            <span class="stat-value">{avg_assess}</span>
          </div>
          {zip_table_html}
        </div>
        """
    
    def _generate_zip_panel(self, zip_code: str) -> str:
        """
        Generate HTML for a single ZIP code statistics panel.
        
        Args:
            zip_code: ZIP code
        
        Returns:
            HTML string
        """
        # Calculate stats for this ZIP
        if "par_zip" not in self.parcels_gdf.columns:
            return ""
        
        try:
            # Convert to float first to handle Decimal types and values like "44119.0"
            # Then to int to remove decimals, then to string
            zip_df = self.parcels_gdf[
                self.parcels_gdf["par_zip"].astype(float).astype(int).astype(str) == str(zip_code)
            ].copy()
        except Exception:
            return ""
        
        if zip_df.empty:
            return ""
        
        count = len(zip_df)
        
        # Calculate totals
        sales_col = "sales_amount" if "sales_amount" in zip_df.columns else "sales_amou"
        if sales_col in zip_df.columns:
            total_sales = self._format_money(zip_df[sales_col].sum())
        else:
            total_sales = "N/A"
        
        if "certified_tax_total" in zip_df.columns:
            total_assess = self._format_money(zip_df["certified_tax_total"].sum())
        else:
            total_assess = "N/A"
        
        # Generate owner breakdown table
        owner_table_html = self._generate_zip_owner_table(zip_df, sales_col)
        
        return f"""
        <div class="stats zip" id="zip_{zip_code}" style="display:none;">
          <h3>ZIP {zip_code}</h3>
          <div class="stat-row">
            <span class="stat-label">Properties:</span>
            <span class="stat-value">{count}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Total Sales:</span>
            <span class="stat-value">{total_sales}</span>
          </div>
          <div class="stat-row">
            <span class="stat-label">Total Assessed:</span>
            <span class="stat-value">{total_assess}</span>
          </div>
          {owner_table_html}
        </div>
        """
    
    def _generate_zip_table(self, zip_df: Optional[pd.DataFrame]) -> str:
        """
        Generate HTML table showing ZIP code breakdown for an owner.
        
        Args:
            zip_df: DataFrame with ZIP breakdown data
        
        Returns:
            HTML string
        """
        if zip_df is None or zip_df.empty:
            return "<div style='margin-top:8px;'><em>No ZIP breakdown available.</em></div>"
        
        # Standardize column names
        df = zip_df.copy()
        
        # Handle various column name formats
        zip_col = None
        for col in ["par_zip", "ZIP", "zip"]:
            if col in df.columns:
                zip_col = col
                break
        
        if zip_col is None:
            return "<div style='margin-top:8px;'><em>No ZIP data available.</em></div>"
        
        # Format ZIP codes
        df["ZIP"] = df[zip_col].astype(str).str.zfill(5)
        
        # Format money columns
        for col in ["sales_total", "Sales Total"]:
            if col in df.columns:
                df[col] = df[col].apply(self._format_money)
        
        for col in ["assess_total", "Assessed Total"]:
            if col in df.columns:
                df[col] = df[col].apply(self._format_money)
        
        # Rename for display
        display_cols = []
        if "ZIP" in df.columns:
            display_cols.append("ZIP")
        if "properties" in df.columns:
            df["Count"] = df["properties"]
            display_cols.append("Count")
        if "sales_total" in df.columns:
            df["Sales"] = df["sales_total"]
            display_cols.append("Sales")
        if "assess_total" in df.columns:
            df["Assessed"] = df["assess_total"]
            display_cols.append("Assessed")
        
        if not display_cols:
            return "<div style='margin-top:8px;'><em>No data to display.</em></div>"
        
        # Generate table
        header_row = "".join(f"<th>{col}</th>" for col in display_cols)
        
        data_rows = ""
        for _, row in df.iterrows():
            data_rows += "<tr>" + "".join(
                f"<td>{row[col]}</td>" for col in display_cols
            ) + "</tr>"
        
        return f"""
        <div style='margin-top:8px;'><b>By ZIP</b></div>
        <table>
          <tr>{header_row}</tr>
          {data_rows}
        </table>
        """
    
    def _generate_zip_owner_table(self, zip_df: pd.DataFrame, sales_col: str) -> str:
        """
        Generate HTML table showing owner breakdown for a ZIP code.
        
        Args:
            zip_df: DataFrame with parcels in this ZIP
            sales_col: Name of sales amount column
        
        Returns:
            HTML string
        """
        if zip_df.empty:
            return "<div style='margin-top:8px;'><em>No portfolio activity in this ZIP.</em></div>"
        
        # Find a parcel ID column to count
        count_col = None
        for candidate in ['parcel_pin', 'parcelpin', 'parcel_id', 'pin', 'objectid']:
            if candidate in zip_df.columns:
                count_col = candidate
                break
        
        if count_col is None:
            # Fall back to counting rows
            return "<div style='margin-top:8px;'><em>Unable to generate owner breakdown.</em></div>"
        
        # Aggregate by owner - convert Decimal to float for aggregation
        agg_dict = {count_col: "count"}
        
        if sales_col in zip_df.columns:
            # Convert to float to handle Decimal types
            zip_df[sales_col] = zip_df[sales_col].astype(float)
            agg_dict[sales_col] = "sum"
        
        if "certified_tax_total" in zip_df.columns:
            # Convert to float to handle Decimal types
            zip_df["certified_tax_total"] = zip_df["certified_tax_total"].astype(float)
            agg_dict["certified_tax_total"] = "sum"
        
        owner_stats = (
            zip_df.groupby("owner_clean")
            .agg(agg_dict)
            .reset_index()
            .sort_values(count_col, ascending=False)
        )
        
        owner_stats.columns = ["Owner", "Count"] + list(owner_stats.columns[2:])
        
        # Format money columns
        if sales_col in zip_df.columns:
            owner_stats["Sales"] = owner_stats[sales_col].apply(self._format_money)
        
        if "certified_tax_total" in zip_df.columns:
            owner_stats["Assessed"] = owner_stats["certified_tax_total"].apply(self._format_money)
        
        # Select display columns
        display_cols = ["Owner", "Count"]
        if "Sales" in owner_stats.columns:
            display_cols.append("Sales")
        if "Assessed" in owner_stats.columns:
            display_cols.append("Assessed")
        
        # Generate table
        header_row = "".join(f"<th>{col}</th>" for col in display_cols)
        
        data_rows = ""
        for _, row in owner_stats.iterrows():
            data_rows += "<tr>" + "".join(
                f"<td>{sanitize_for_html(str(row[col]))}</td>" for col in display_cols
            ) + "</tr>"
        
        return f"""
        <div style='margin-top:8px;'><b>Portfolios in ZIP</b></div>
        <table>
          <tr>{header_row}</tr>
          {data_rows}
        </table>
        """
    
    def _format_money(self, value: Any) -> str:
        """
        Format a value as currency.
        
        Args:
            value: Numeric value
        
        Returns:
            Formatted string
        """
        try:
            return f"${float(value):,.0f}"
        except (ValueError, TypeError):
            return str(value) if value is not None else "N/A"
    
    def _get_sidebar_css(self) -> str:
        """
        Get CSS styles for the sidebar.
        
        Returns:
            CSS string
        """
        return """
        #gs-sidebar {
            position: fixed;
            top: 12px;
            left: 12px;
            width: 340px;
            max-height: 86vh;
            z-index: 9999;
            background: #fff;
            border: 1px solid #ddd;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            overflow: auto;
            padding: 12px;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }
        
        #gs-sidebar h2 {
            margin: 2px 0 10px 0;
            font-size: 18px;
            color: #333;
        }
        
        #gs-sidebar h3 {
            margin: 8px 0 6px 0;
            font-size: 15px;
            color: #444;
        }
        
        #gs-sidebar select,
        #gs-sidebar input[type="text"] {
            width: 100%;
            padding: 6px;
            margin: 4px 0 6px 0;
            border: 1px solid #ccc;
            border-radius: 4px;
            font-size: 13px;
            box-sizing: border-box;
        }
        
        #gs-sidebar label {
            font-size: 13px;
            color: #555;
            display: block;
            margin-top: 6px;
        }
        
        .gs-description {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
            line-height: 1.4;
        }
        
        .gs-mode-toggle {
            font-size: 12px;
            margin-bottom: 10px;
        }
        
        .gs-mode-toggle label {
            display: inline;
            margin-right: 10px;
            cursor: pointer;
        }
        
        .stats {
            font-size: 13px;
            margin-top: 12px;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 6px 0;
            border-bottom: 1px solid #f0f0f0;
        }
        
        .stat-label {
            font-weight: 500;
            color: #555;
        }
        
        .stat-value {
            color: #333;
            font-weight: 600;
        }
        
        .stats table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 6px;
            font-size: 12px;
        }
        
        .stats table th {
            text-align: left;
            border-bottom: 1px solid #ddd;
            padding: 4px 6px;
            font-weight: 600;
            color: #333;
            background: #f8f8f8;
        }
        
        .stats table td {
            border-bottom: 1px solid #f0f0f0;
            padding: 4px 6px;
            color: #555;
        }
        
        .stats table tr:last-child td {
            border-bottom: none;
        }
        """
    
    def _get_sidebar_javascript(self) -> str:
        """
        Get JavaScript for sidebar functionality.
        
        Returns:
            JavaScript string
        """
        return """
        function gsShowOwner() {
          var sel = document.getElementById("ownerSelect").value;
          var panels = document.querySelectorAll("#gs-panels .stats");
          panels.forEach(function(p) { p.style.display = "none"; });
          var el = document.getElementById(sel);
          if (el) el.style.display = "block";
          else document.getElementById("owner_all").style.display = "block";
        }
        
        function gsShowZip() {
          var sel = document.getElementById("zipSelect").value;
          var panels = document.querySelectorAll("#gs-panels .stats");
          panels.forEach(function(p) { p.style.display = "none"; });
          if (sel === 'all') {
            document.getElementById("owner_all").style.display = "block";
          } else {
            var el = document.getElementById(sel);
            if (el) el.style.display = "block";
            else document.getElementById("owner_all").style.display = "block";
          }
        }
        
        function gsModeChanged() {
          var isZip = document.getElementById('mode_zip').checked;
          var ownerSel = document.getElementById('ownerSelect');
          var ownerLbl = document.querySelector('label[for="ownerSelect"]');
          var ownerSearch = document.getElementById('ownerSearch');
          var ownerSearchLbl = document.querySelector('label[for="ownerSearch"]');
          var zipSel = document.getElementById('zipSelect');
          var zipLbl = document.querySelector('label[for="zipSelect"]');
          
          if (isZip) {
            ownerSel.style.display = 'none';
            if (ownerLbl) ownerLbl.style.display = 'none';
            if (ownerSearch) ownerSearch.style.display = 'none';
            if (ownerSearchLbl) ownerSearchLbl.style.display = 'none';
            zipSel.style.display = 'block';
            if (zipLbl) zipLbl.style.display = 'block';
            gsShowZip();
          } else {
            zipSel.style.display = 'none';
            if (zipLbl) zipLbl.style.display = 'none';
            ownerSel.style.display = 'block';
            if (ownerLbl) ownerLbl.style.display = 'block';
            if (ownerSearch) ownerSearch.style.display = 'block';
            if (ownerSearchLbl) ownerSearchLbl.style.display = 'block';
            gsShowOwner();
          }
          
          if (typeof gsToggleLayers === 'function') {
            gsToggleLayers();
          }
        }
        """
    
    def _generate_toggle_javascript(
        self,
        map_var: str,
        base_layer_name: Optional[str],
        owner_layer_names: Dict[str, str],
        zip_layer_names: Dict[str, str],
        zip_codes: List[str],
        view_mode: str = "By Owner"
    ) -> str:
        """
        Generate JavaScript for layer toggling.
        
        Args:
            map_var: Folium map variable name
            base_layer_name: Name of base context layer
            owner_layer_names: Dict mapping owner slugs to layer names
            zip_layer_names: Dict mapping ZIP IDs to layer names
            zip_codes: List of ZIP codes
            view_mode: Initial view mode ("By Owner" or "By ZIP")
        
        Returns:
            JavaScript string
        """
        # Build JavaScript object mappings
        owner_layers_js = ", ".join(
            f"'{slug}': '{name}'"
            for slug, name in owner_layer_names.items()
        )
        
        zip_layers_js = ", ".join(
            f"'{zip_id}': '{name}'"
            for zip_id, name in zip_layer_names.items()
        )
        
        owner_name_to_slug_js = ", ".join(
            f"'{owner.replace(chr(39), chr(92) + chr(39))}': '{owner_to_slug(owner)}'"
            for owner in self.target_owners
        )
        
        base_var = base_layer_name if base_layer_name else ""
        
        return f"""
        (function() {{
          var gsMapName = '{map_var}';
          var gsOwnerLayerNames = {{ {owner_layers_js} }};
          var gsZipLayerNames = {{ {zip_layers_js} }};
          var gsOwnerNameToSlug = {{ {owner_name_to_slug_js} }};
          var gsBaseContextName = '{base_var}';
          
          window.gsToggleLayers = function() {{
            var sel = document.getElementById('ownerSelect').value;
            var zselEl = document.getElementById('zipSelect');
            var zsel = zselEl ? zselEl.value : 'all';
            var modeEl = document.querySelector("input[name='gsMode']:checked");
            var mode = modeEl ? modeEl.value : 'owner';
            var map = window[gsMapName];
            
            if (!map) {{
              console.warn('Map not found:', gsMapName);
              return;
            }}
            
            // Toggle layers based on mode
            if (mode === 'owner') {{
              // Owner mode: show only selected owner layer (or all)
              Object.keys(gsOwnerLayerNames).forEach(function(key) {{
                var lname = gsOwnerLayerNames[key];
                var layer = window[lname];
                if (!layer) return;
                
                if (sel === 'all') {{
                  if (!map.hasLayer(layer)) map.addLayer(layer);
                }} else {{
                  if (key === sel) {{
                    if (!map.hasLayer(layer)) map.addLayer(layer);
                  }} else {{
                    if (map.hasLayer(layer)) map.removeLayer(layer);
                  }}
                }}
              }});
              
              // Hide any ZIP layers
              Object.keys(gsZipLayerNames).forEach(function(key) {{
                var lname = gsZipLayerNames[key];
                var layer = window[lname];
                if (layer && map.hasLayer(layer)) map.removeLayer(layer);
              }});
            }} else {{
              // ZIP mode: show only selected ZIP layer (or all)
              Object.keys(gsZipLayerNames).forEach(function(key) {{
                var lname = gsZipLayerNames[key];
                var layer = window[lname];
                if (!layer) return;
                
                if (zsel === 'all') {{
                  if (!map.hasLayer(layer)) map.addLayer(layer);
                }} else {{
                  if (key === zsel) {{
                    if (!map.hasLayer(layer)) map.addLayer(layer);
                  }} else {{
                    if (map.hasLayer(layer)) map.removeLayer(layer);
                  }}
                }}
              }});
              
              // Hide any owner layers
              Object.keys(gsOwnerLayerNames).forEach(function(key) {{
                var lname = gsOwnerLayerNames[key];
                var layer = window[lname];
                if (layer && map.hasLayer(layer)) map.removeLayer(layer);
              }});
            }}
            
            // Toggle base context layer
            var baseLayer = window[gsBaseContextName];
            if (typeof baseLayer !== 'undefined' && baseLayer) {{
              var showBase = (mode === 'owner' && sel === 'all') || (mode === 'zip' && zsel === 'all');
              if (showBase) {{
                if (!map.hasLayer(baseLayer)) map.addLayer(baseLayer);
              }} else {{
                if (map.hasLayer(baseLayer)) map.removeLayer(baseLayer);
              }}
            }}
          }};
          
          window.gsTypeOwner = function() {{
            var input = document.getElementById('ownerSearch');
            if (!input) return;
            
            var q = input.value.toLowerCase();
            var allNames = Object.keys(gsOwnerNameToSlug);
            var matches = allNames.filter(function(name) {{
              return q === '' || name.toLowerCase().indexOf(q) !== -1;
            }});
            
            // Update datalist suggestions
            var dl = document.getElementById('ownerSuggestions');
            if (dl) {{
              dl.innerHTML = matches.map(function(n) {{
                return '<option value="' + n + '">';
              }}).join('');
            }}
            
            // Update the portfolio dropdown to show only matches
            var sel = document.getElementById('ownerSelect');
            if (sel) {{
              sel.innerHTML = '<option value="all">All Target Owners</option>' + 
                matches.map(function(n) {{
                  return '<option value="' + gsOwnerNameToSlug[n] + '">' + n + '</option>';
                }}).join('');
            }}
            
            // Auto-select first match when typing
            if (sel) {{
              if (matches.length > 0) {{
                sel.value = gsOwnerNameToSlug[matches[0]];
              }} else {{
                sel.value = 'all';
              }}
            }}
            
            // Switch to owner mode
            var ownerMode = document.getElementById('mode_owner');
            if (ownerMode) ownerMode.checked = true;
            
            if (typeof gsToggleLayers === 'function') {{
              gsToggleLayers();
            }}
            
            if (typeof gsShowOwner === 'function') {{
              gsShowOwner();
            }}
          }};
          
          // Initialize on load with correct view mode
          if (typeof gsToggleLayers === 'function') {{
            setTimeout(function() {{
              // Set initial mode based on view_mode parameter
              var initialMode = '{view_mode}'.toLowerCase().includes('zip') ? 'zip' : 'owner';
              if (initialMode === 'zip') {{
                var zipModeRadio = document.getElementById('mode_zip');
                if (zipModeRadio) zipModeRadio.checked = true;
                gsModeChanged();
              }} else {{
                gsToggleLayers();
              }}
            }}, 100);
          }}
        }})();
        """


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def generate_map(
    city_config: Dict[str, Any],
    parcels_gdf: gpd.GeoDataFrame,
    target_owners: List[str],
    stats_per_owner: Dict[str, Dict],
    all_stats: Dict[str, Any],
    tile_layer: str = "light",
    use_clustering: bool = False,
    view_mode: str = "By Owner",
    include_zip_layers: bool = False
) -> folium.Map:
    """
    Convenience function to generate a map from city data.

    Args:
        city_config: Dictionary with city configuration (center_lat, center_lng, zoom_level)
        parcels_gdf: GeoDataFrame with parcels
        target_owners: List of target owner names
        stats_per_owner: Dictionary mapping owner names to their statistics
        all_stats: Aggregate statistics for all target owners
        tile_layer: Base tile layer (light, dark, osm, satellite)
        use_clustering: Whether to use marker clustering for better performance (default: False)
        view_mode: Initial view mode - "By Owner" or "By ZIP" (default: "By Owner")
        include_zip_layers: Whether to build ZIP code layers (False by default for performance)

    Returns:
        Folium Map object

    Example:
        >>> city_config = {"center_lat": 41.4993, "center_lng": -81.6944, "zoom_level": 11}
        >>> m = generate_map(city_config, gdf, owners, stats, all_stats, use_clustering=True)
        >>> m.save("output.html")
    """
    generator = MapGenerator(
        city_config,
        parcels_gdf,
        target_owners,
        stats_per_owner,
        all_stats
    )
    return generator.generate_map(
        tile_layer=tile_layer,
        use_clustering=use_clustering,
        view_mode=view_mode,
        include_zip_layers=include_zip_layers
    )

