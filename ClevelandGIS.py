import os
import pandas as pd
import geopandas as gpd
import folium
import matplotlib.cm as cm
import matplotlib.colors as colors

# -------------------------------
# CONFIG
# -------------------------------
INPUT_FILE = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\Combined_Parcels_-_Cleveland_Only.csv"
SHP_FILE   = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\ClevelandSHP\Combined_Parcels_-_Cleveland_Only.shp"

OUTPUT_EXCEL = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\cleveland_ownership_analysis.xlsx"
OUTPUT_MAP   = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\cleveland_top5_map.html"

VALID_TYPES = ["1-FAMILY PLATTED LOT", "2-FAMILY PLATTED LOT"]

# -------------------------------
# Helpers
# -------------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Lowercase columns and align key fields across CSV/SHP truncations."""
    df.columns = df.columns.str.lower()

    # Owner column candidates
    for col in ["deeded_owner", "deeded_own", "deed_owner", "ownername", "mail_name"]:
        if col in df.columns:
            df = df.rename(columns={col: "deeded_owner"})
            break

    # Land-use description candidates
    for col in ["tax_luc_description", "tax_luc_de", "tax_luc", "ext_luc_de"]:
        if col in df.columns:
            df = df.rename(columns={col: "tax_luc_description"})
            break

    return df

def clean_owner(name) -> str:
    if pd.isna(name):
        return "UNKNOWN"
    name = str(name).upper().strip()
    for suf in [" LLC", " L.L.C", " INC", " LP", " CO", " CORP", " CORPORATION", " TRUST", ",", "."]:
        name = name.replace(suf, "")
    return name.strip()

def safe_for_map(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Convert datetime to string for Folium; return a copy safe for JSON export."""
    gdf2 = gdf.copy()
    for col in gdf2.columns:
        if pd.api.types.is_datetime64_any_dtype(gdf2[col]):
            gdf2[col] = gdf2[col].astype(str)
    return gdf2

# -------------------------------
# STEP 1: Load CSV + summarize
# -------------------------------
csv_df = pd.read_csv(INPUT_FILE, low_memory=False)
csv_df = normalize_columns(csv_df)
print(f"Loaded {len(csv_df)} parcels from CSV")

csv_df = csv_df[csv_df["tax_luc_description"].isin(VALID_TYPES)].copy()
print(f"Filtered dataset: {len(csv_df)} parcels classified as 1-Family or 2-Family")

csv_df["owner_clean"] = csv_df["deeded_owner"].apply(clean_owner)

owner_summary = (
    csv_df.groupby("owner_clean")
    .size()
    .reset_index(name="parcel_count")
    .sort_values("parcel_count", ascending=False)
)
top5 = owner_summary.head(5)
print("Top 5 Owners:\n", top5)

# Excel export (skip if exists)
if not os.path.exists(OUTPUT_EXCEL):
    with pd.ExcelWriter(OUTPUT_EXCEL) as writer:
        owner_summary.to_excel(writer, sheet_name="Ownership Summary", index=False)
        csv_df.to_excel(writer, sheet_name="Raw Data", index=False)
    print(f"✅ Exported summaries: {OUTPUT_EXCEL}")
else:
    print(f"⚡ Skipped Excel export (already exists): {OUTPUT_EXCEL}")

# -------------------------------
# STEP 2: Load SHP, align + prep for map
# -------------------------------
gdf = gpd.read_file(SHP_FILE)
gdf = normalize_columns(gdf)
gdf = gdf[gdf["tax_luc_description"].isin(VALID_TYPES)].copy()
gdf["owner_clean"] = gdf["deeded_owner"].apply(clean_owner)

# Convert datetimes
gdf = safe_for_map(gdf)

# We’ll keep key fields for popup
fields_for_popup = ["parcel_id", "par_addr_a", "owner_clean", "tax_luc_description","sales_amou"]

# Subset to top 5 owners
gdf_top5 = gdf[gdf["owner_clean"].isin(top5["owner_clean"])].copy()

# -------------------------------
# STEP 3: Folium map
# -------------------------------
m = folium.Map(location=[41.4993, -81.6944], zoom_start=11, tiles="cartodbpositron")

# Base layer: all eligible parcels (light grey)
folium.GeoJson(
    gdf,
    name="All Parcels",
    style_function=lambda x: {"color": "grey", "weight": 0.3, "fillOpacity": 0.05},
    tooltip=folium.GeoJsonTooltip(fields=["parcel_id", "par_addr_a","sales_amou"], aliases=["Parcel ID:", "Address:","Sale Price:"], localize=True),
).add_to(m)

# Distinct colors for Top 5
cmap = cm.get_cmap("Set1", 5)
owner_list = top5["owner_clean"].tolist()
owner_colors = {owner: colors.rgb2hex(cmap(i)) for i, owner in enumerate(owner_list)}
owner_counts = top5.set_index("owner_clean")["parcel_count"].to_dict()

# Individual owner layers
for owner in owner_list:
    color  = owner_colors[owner]
    subset = gdf_top5[gdf_top5["owner_clean"] == owner]

    folium.GeoJson(
        subset,
        name=f"{owner} ({owner_counts.get(owner, 0)})",
        style_function=lambda x, c=color: {"color": c, "weight": 1, "fillOpacity": 0.6},
        tooltip=folium.GeoJsonTooltip(
            fields=fields_for_popup,
            aliases=["Parcel ID:", "Address:", "Owner:", "Land Use:"],
            localize=True
        ),
        popup=folium.GeoJsonPopup(
            fields=fields_for_popup,
            aliases=["Parcel ID:", "Address:", "Owner:", "Land Use:"],
            localize=True,
            labels=True
        )
    ).add_to(m)

folium.LayerControl(collapsed=False).add_to(m)

# Save
m.save(OUTPUT_MAP)
print(f"✅ Exported interactive map with popups: {OUTPUT_MAP}")
