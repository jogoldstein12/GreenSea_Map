"""
Map Styling Configuration
Defines colors, styles, templates, and configurations for Folium maps
"""

import matplotlib.colors as mcolors
from typing import Dict, List, Optional, Tuple
import logging

# Setup logging
logger = logging.getLogger(__name__)


# =============================================================================
# COLOR SCHEMES
# =============================================================================

class ColorScheme:
    """
    Manages color schemes for map layers using matplotlib colormaps.
    """
    
    DEFAULT_COLORMAP = "Set1"  # Matplotlib colormap for owner colors
    
    @staticmethod
    def generate_owner_colors(
        owners: List[str],
        colormap: str = DEFAULT_COLORMAP
    ) -> Dict[str, str]:
        """
        Generate unique colors for each owner using matplotlib colormap.
        
        Args:
            owners: List of owner names
            colormap: Name of matplotlib colormap (default: 'Set1')
        
        Returns:
            Dictionary mapping owner names to hex colors
        
        Example:
            >>> colors = ColorScheme.generate_owner_colors(['SMITH', 'JONES'])
            >>> colors
            {'SMITH': '#e41a1c', 'JONES': '#377eb8'}
        """
        num_colors = max(5, len(owners))
        
        try:
            # Try new matplotlib 3.6+ API
            from matplotlib import colormaps as mpl_cmaps
            cmap = mpl_cmaps.get_cmap(colormap).resampled(num_colors)
        except Exception:
            # Fallback for older matplotlib versions
            try:
                from matplotlib import cm
                cmap = cm.get_cmap(colormap, num_colors)
            except Exception as e:
                logger.error(f"Failed to get colormap: {e}")
                # Fallback to basic colors
                return ColorScheme._fallback_colors(owners)
        
        owner_colors = {
            owner: mcolors.rgb2hex(cmap(i % cmap.N))
            for i, owner in enumerate(owners)
        }
        
        logger.debug(f"Generated {len(owner_colors)} unique colors")
        return owner_colors
    
    @staticmethod
    def _fallback_colors(owners: List[str]) -> Dict[str, str]:
        """
        Fallback color scheme if matplotlib colormap fails.
        """
        basic_colors = [
            "#e41a1c", "#377eb8", "#4daf4a", "#984ea3", "#ff7f00",
            "#ffff33", "#a65628", "#f781bf", "#999999", "#66c2a5"
        ]
        return {
            owner: basic_colors[i % len(basic_colors)]
            for i, owner in enumerate(owners)
        }


# =============================================================================
# LAYER STYLES
# =============================================================================

class LayerStyles:
    """
    Defines style functions for different map layers.
    """
    
    # Base context layer style (all parcels in light grey)
    BASE_CONTEXT = {
        "color": "grey",
        "weight": 0.4,
        "fillOpacity": 0.08,
        "fillColor": "grey"
    }
    
    # Default parcel style
    DEFAULT_PARCEL = {
        "color": "#3388ff",
        "weight": 1,
        "fillOpacity": 0.55
    }
    
    # Highlighted/selected parcel style
    HIGHLIGHTED_PARCEL = {
        "color": "#ffff00",
        "weight": 2,
        "fillOpacity": 0.7
    }
    
    @staticmethod
    def get_base_style() -> Dict:
        """
        Get style for base context layer.
        
        Returns:
            Style dictionary for GeoJSON
        """
        return LayerStyles.BASE_CONTEXT.copy()
    
    @staticmethod
    def get_owner_style(color: str, opacity: float = 0.55) -> Dict:
        """
        Get style for owner-specific layer.
        
        Args:
            color: Hex color for the owner
            opacity: Fill opacity (0-1)
        
        Returns:
            Style dictionary for GeoJSON
        """
        return {
            "color": color,
            "weight": 1,
            "fillOpacity": opacity,
            "fillColor": color
        }
    
    @staticmethod
    def get_zip_style(color: str, opacity: float = 0.55) -> Dict:
        """
        Get style for ZIP code layer with owner coloring.
        
        Args:
            color: Hex color (usually from feature properties)
            opacity: Fill opacity (0-1)
        
        Returns:
            Style dictionary for GeoJSON
        """
        return {
            "color": color,
            "weight": 1,
            "fillOpacity": opacity,
            "fillColor": color
        }


# =============================================================================
# POPUP & TOOLTIP CONFIGURATION
# =============================================================================

class PopupConfig:
    """
    Manages popup and tooltip field configurations.
    """
    
    # Candidate fields to display (in priority order)
    CANDIDATE_FIELDS = [
        "parcelpin",
        "parcel_id",
        "objectid",
        "par_addr",
        "par_addr_a",
        "par_addr_all",
        "address",
        "owner_clean",
        "deeded_owner",
        "tax_luc_description",
        "sales_amount",
        "sales_amou",
        "certified_tax_total",
        "par_zip"
    ]
    
    # Field aliases for display (user-friendly names)
    FIELD_ALIASES = {
        "parcelpin": "Parcel PIN",
        "parcel_id": "Parcel ID",
        "objectid": "Object ID",
        "par_addr": "Address",
        "par_addr_a": "Alt Address",
        "par_addr_all": "Full Address",
        "address": "Address",
        "owner_clean": "Owner",
        "deeded_owner": "Deeded Owner",
        "tax_luc_description": "Land Use",
        "sales_amount": "Sale Price",
        "sales_amou": "Sale Price",
        "certified_tax_total": "Tax Assessment",
        "par_zip": "ZIP Code"
    }
    
    @staticmethod
    def get_available_fields(
        columns: List[str],
        preferred_fields: Optional[List[str]] = None
    ) -> List[str]:
        """
        Get list of available fields from DataFrame columns.
        
        Args:
            columns: List of column names in the DataFrame
            preferred_fields: Optional list of preferred fields (default: CANDIDATE_FIELDS)
        
        Returns:
            List of fields that exist in both candidate list and columns
        """
        if preferred_fields is None:
            preferred_fields = PopupConfig.CANDIDATE_FIELDS
        
        available = [f for f in preferred_fields if f in columns]
        logger.debug(f"Available popup fields: {available}")
        return available
    
    @staticmethod
    def get_aliases(fields: List[str]) -> List[str]:
        """
        Get display aliases for a list of fields.
        
        Args:
            fields: List of field names
        
        Returns:
            List of display aliases (defaults to field name if not in map)
        """
        return [
            PopupConfig.FIELD_ALIASES.get(f, f.replace("_", " ").title())
            for f in fields
        ]
    
    @staticmethod
    def format_value(field: str, value: any) -> str:
        """
        Format a field value for display in popup/tooltip.
        
        Args:
            field: Field name
            value: Field value
        
        Returns:
            Formatted string for display
        """
        if value is None or value == "":
            return "N/A"
        
        # Format currency fields
        if field in ["sales_amount", "sales_amou", "certified_tax_total"]:
            try:
                return f"${float(value):,.0f}"
            except (ValueError, TypeError):
                return str(value)
        
        return str(value)


# =============================================================================
# HTML TEMPLATES
# =============================================================================

class HTMLTemplates:
    """
    HTML and CSS templates for map components.
    """
    
    @staticmethod
    def get_sidebar_css() -> str:
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
        }
        
        #gs-sidebar label {
            font-size: 13px;
            color: #555;
        }
        
        .gs-description {
            font-size: 12px;
            color: #666;
            margin-bottom: 8px;
        }
        
        .gs-mode-toggle {
            font-size: 12px;
            margin-bottom: 6px;
        }
        
        .gs-mode-toggle label {
            margin-right: 10px;
        }
        
        .stats {
            font-size: 13px;
        }
        
        .stats table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 6px;
        }
        
        .stats table th {
            text-align: left;
            border-bottom: 1px solid #ddd;
            padding: 4px 6px;
            font-weight: 600;
            color: #333;
        }
        
        .stats table td {
            border-bottom: 1px solid #f0f0f0;
            padding: 4px 6px;
            color: #555;
        }
        
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 4px 0;
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
        """
    
    @staticmethod
    def get_stats_table_html(
        rows: List[Tuple],
        headers: List[str],
        title: Optional[str] = None
    ) -> str:
        """
        Generate HTML for a statistics table.
        
        Args:
            rows: List of tuples containing row data
            headers: List of column headers
            title: Optional table title
        
        Returns:
            HTML string
        """
        title_html = f"<div style='margin-top:8px;'><b>{title}</b></div>" if title else ""
        
        header_row = "".join(
            f"<th style='text-align:left; border-bottom:1px solid #ddd; padding:4px 6px'>{h}</th>"
            for h in headers
        )
        
        data_rows = ""
        for row in rows:
            data_rows += "<tr>" + "".join(
                f"<td style='border-bottom:1px solid #f0f0f0; padding:4px 6px'>{cell}</td>"
                for cell in row
            ) + "</tr>"
        
        return f"""
        {title_html}
        <table style='width:100%; border-collapse:collapse; margin-top:6px'>
            <tr>{header_row}</tr>
            {data_rows}
        </table>
        """
    
    @staticmethod
    def get_sidebar_template() -> str:
        """
        Get HTML template for the sidebar.
        
        Returns:
            HTML template string with placeholders
        """
        return """
        <div id="gs-sidebar">
          <h2>Portfolio Viewer</h2>
          <div class="gs-description">
            Select a target owner to see portfolio stats. Toggle map layers on the right to compare footprints.
          </div>
          <div class="gs-mode-toggle">
            <label>
              <input type="radio" name="gsMode" id="mode_owner" value="owner" checked onchange="gsModeChanged()">
              By Portfolio
            </label>
            <label>
              <input type="radio" name="gsMode" id="mode_zip" value="zip" onchange="gsModeChanged()">
              By ZIP
            </label>
          </div>
          
          <label for="ownerSearch">Search portfolio:</label>
          <input id="ownerSearch" list="ownerSuggestions" type="text" 
                 placeholder="Type to search..." oninput="gsTypeOwner()" />
          <datalist id="ownerSuggestions">
            {owner_options}
          </datalist>
          
          <label for="ownerSelect">Select portfolio:</label>
          <select id="ownerSelect" onchange="gsShowOwner(); if (typeof gsToggleLayers==='function') {{ gsToggleLayers(); }}">
            <option value="all">All Target Owners</option>
            {owner_select_options}
          </select>
          
          <label for="zipSelect" style="display:none;">Select ZIP:</label>
          <select id="zipSelect" onchange="gsShowZip(); if (typeof gsToggleLayers==='function') {{ gsToggleLayers(); }}" style="display:none;">
            <option value="all">All ZIPs</option>
            {zip_select_options}
          </select>
          
          <div id="gs-panels">
            {stat_panels}
          </div>
        </div>
        """


# =============================================================================
# MAP CONFIGURATION
# =============================================================================

class MapConfig:
    """
    Default map configuration settings.
    """
    
    # Default tile layers
    TILE_LAYERS = {
        "light": {
            "name": "CartoDB Positron",
            "tiles": "cartodbpositron",
            "attr": "© OpenStreetMap contributors © CARTO"
        },
        "dark": {
            "name": "CartoDB Dark Matter",
            "tiles": "cartodbdark_matter",
            "attr": "© OpenStreetMap contributors © CARTO"
        },
        "osm": {
            "name": "OpenStreetMap",
            "tiles": "OpenStreetMap",
            "attr": "© OpenStreetMap contributors"
        },
        "satellite": {
            "name": "Esri Satellite",
            "tiles": "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            "attr": "© Esri"
        }
    }
    
    # Default map settings
    DEFAULT_ZOOM = 11
    DEFAULT_TILE = "light"
    
    # Layer control settings
    LAYER_CONTROL = {
        "position": "topright",
        "collapsed": False,
        "autoZIndex": True
    }
    
    @staticmethod
    def get_tile_config(tile_type: str = DEFAULT_TILE) -> Dict:
        """
        Get tile layer configuration.
        
        Args:
            tile_type: Type of tile layer (light, dark, osm, satellite)
        
        Returns:
            Dictionary with tile configuration
        """
        return MapConfig.TILE_LAYERS.get(
            tile_type,
            MapConfig.TILE_LAYERS[MapConfig.DEFAULT_TILE]
        )


# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def sanitize_for_html(text: str) -> str:
    """
    Sanitize text for safe HTML display.
    
    Args:
        text: Input text
    
    Returns:
        Sanitized text
    """
    if not text:
        return ""
    
    replacements = {
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
        '"': "&quot;",
        "'": "&#x27;"
    }
    
    for old, new in replacements.items():
        text = str(text).replace(old, new)
    
    return text


def owner_to_slug(owner_name: str) -> str:
    """
    Convert owner name to a valid HTML ID/slug.
    
    Args:
        owner_name: Owner name
    
    Returns:
        Slugified version safe for HTML IDs
    
    Example:
        >>> owner_to_slug("SMITH PROPERTIES")
        'owner_smith_properties'
    """
    slug = owner_name.lower()
    slug = "".join(c if c.isalnum() else "_" for c in slug)
    # Collapse multiple consecutive underscores
    while "__" in slug:
        slug = slug.replace("__", "_")
    # Remove leading/trailing underscores
    slug = slug.strip("_")
    return f"owner_{slug}"


# =============================================================================
# EXPORT CONVENIENCE OBJECTS
# =============================================================================

# Create singleton instances for easy import
color_scheme = ColorScheme()
layer_styles = LayerStyles()
popup_config = PopupConfig()
html_templates = HTMLTemplates()
map_config = MapConfig()

