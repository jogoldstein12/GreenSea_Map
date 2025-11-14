# Map Generation Examples

This directory contains example scripts demonstrating the map generation capabilities.

## Files

### `generate_sample_map.py`
Demonstrates the complete map generation workflow with synthetic data.

**Features demonstrated:**
- Creating sample parcel GeoDataFrame
- Calculating portfolio statistics
- Generating interactive Folium map
- Sidebar with statistics
- Layer toggling (owner/ZIP modes)
- Exporting to HTML

**Usage:**
```bash
# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Run the example
python examples/generate_sample_map.py
```

**Output:**
- Creates `sample_portfolio_map.html` in the project root
- 100 sample parcels
- 5 target owners
- 4 ZIP codes
- Interactive map with sidebar

**What you'll see:**
1. Interactive map centered on Cleveland
2. Sidebar with portfolio search and statistics
3. Toggle between "By Portfolio" and "By ZIP" views
4. Click parcels to see popup information
5. Search functionality to filter portfolios
6. Detailed statistics per owner and ZIP code

## Adding Your Own Examples

Create new example scripts following this pattern:

```python
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mapping.map_generator import generate_map

# Your code here
```

## Next Steps

After running the sample:
1. Open `sample_portfolio_map.html` in your browser
2. Explore the interactive features
3. Try switching between owner and ZIP modes
4. Use the search to filter portfolios
5. Click on parcels to see details

## Integration with Real Data

To use with real Cleveland data:

```python
from data_processing.shapefile_processor import ShapefileProcessor
from data_processing.analyzer import PortfolioAnalyzer
from mapping.map_generator import generate_map

# Load real data
processor = ShapefileProcessor("path/to/cleveland/parcels.shp")
gdf = processor.read_and_normalize()

# Analyze
analyzer = PortfolioAnalyzer(gdf, target_owners)
stats_per_owner = analyzer.get_stats_per_owner()
all_stats = analyzer.get_aggregate_stats()

# Generate map
city_config = {
    'center_lat': 41.4993,
    'center_lng': -81.6944,
    'zoom_level': 11,
    'display_name': 'Cleveland, OH'
}

m = generate_map(city_config, gdf, target_owners, stats_per_owner, all_stats)
m.save('cleveland_real_map.html')
```

## Documentation

For detailed documentation, see:
- `../mapping/map_generator.py` - Main map generation module
- `../mapping/layer_builder.py` - Layer building utilities
- `../mapping/styles.py` - Style configurations
- `../Documents/PHASE4_COMPLETE.md` - Complete Phase 4 documentation

