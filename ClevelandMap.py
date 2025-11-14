import os
import re
import pandas as pd
import geopandas as gpd
import folium
import matplotlib.cm as cm
import matplotlib.colors as colors

# =========================================
# CONFIG (paths reflect your new structure)
# =========================================
CSV_FILE    = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\Input Data\Combined_Parcels_-_Cleveland_Only.csv"
SHP_FILE    = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\Input Data\ClevelandSHP\Combined_Parcels_-_Cleveland_Only.shp"
EXCEL_FILE  = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\Output Files\cleveland_ownership_analysis.xlsx"
OUTPUT_MAP  = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\Output Files\cleveland_top5_map.html"

VALID_TYPES = ["1-FAMILY PLATTED LOT", "2-FAMILY PLATTED LOT"]
TARGET_SHEET = "Portfolio Targets (10-100)"   # tab that contains your target owners

# ======================
# Helpers / Normalizers
# ======================
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    # Owner column normalization
    for col in ["deeded_owner", "deeded_own", "deed_owner", "ownername", "mail_name"]:
        if col in df.columns:
            df = df.rename(columns={col: "deeded_owner"})
            break
    # Land-use description normalization
    for col in ["tax_luc_description", "tax_luc_de", "tax_luc", "ext_luc_de"]:
        if col in df.columns:
            df = df.rename(columns={col: "tax_luc_description"})
            break
    return df

# --- Clean owner names ---
def clean_owner(name):
    if pd.isna(name):
        return "UNKNOWN"
    return (
        str(name)
        .upper()
        .replace(".", "")
        .replace(",", "")
        .replace(" LLC", "")
        .replace(" INC", "")
        .replace(" CO", "")
        .strip()
    )


def sanitize_for_geojson(gdf: gpd.GeoDataFrame) -> gpd.GeoDataFrame:
    """Folium/GeoJSON choke on Timestamps and some objects. Convert (but never touch geometry)."""
    gdf2 = gdf.copy()
    for col in gdf2.columns:
        if col == "geometry":
            continue
        if pd.api.types.is_datetime64_any_dtype(gdf2[col]):
            gdf2[col] = gdf2[col].astype(str)
        else:
            # leave numerics as-is; cast objects to string
            if gdf2[col].dtype == "object":
                gdf2[col] = gdf2[col].astype(str)
    return gdf2

def fmt_money(x: float) -> str:
    try:
        return f"${x:,.0f}"
    except Exception:
        return str(x)

# Create a safe slug for owner names to use in HTML ids and JS keys
def owner_slug(owner_name: str) -> str:
    base = re.sub(r"[^A-Za-z0-9_]+", "_", str(owner_name))
    return ("owner_" + base).strip("_")

# ======================
# Load core datasets
# ======================
# CSV (rich attributes)
csv_df = pd.read_csv(CSV_FILE, low_memory=False)
csv_df = normalize_columns(csv_df)
csv_df = csv_df[csv_df["tax_luc_description"].isin(VALID_TYPES)].copy()

# Clean owner
csv_df["owner_clean"] = csv_df["deeded_owner"].apply(clean_owner)

# Coerce numeric fields for stats
for col in ["sales_amount", "sales_amou", "certified_tax_total"]:
    if col in csv_df.columns:
        csv_df[col] = pd.to_numeric(csv_df[col], errors="coerce").fillna(0)

# Shapefile (geometry)
gdf = gpd.read_file(SHP_FILE)
gdf = normalize_columns(gdf)
gdf = gdf[gdf["tax_luc_description"].isin(VALID_TYPES)].copy()
gdf["owner_clean"] = gdf["deeded_owner"].apply(clean_owner)

# Ensure geometry is WGS84 for Folium
try:
    gdf = gdf.to_crs(epsg=4326)
except Exception:
    pass

# Merge geometry + CSV attributes on parcelpin
if "parcelpin" not in csv_df.columns or "parcelpin" not in gdf.columns:
    raise KeyError("parcelpin must exist in both CSV and SHP for merging.")

merged = gdf[["parcelpin", "geometry", "deeded_owner"]].merge(
    csv_df.drop(columns=["geometry"], errors="ignore"),
    on="parcelpin",
    how="left",
    suffixes=("_shp", "_csv")
)

# Ensure owner_clean exists
if "owner_clean" not in merged.columns:
    if "deeded_owner" in merged.columns:
        merged["owner_clean"] = merged["deeded_owner"].apply(clean_owner)
    else:
        raise KeyError("Neither owner_clean nor deeded_owner found in merged dataset.")


# ======================
# Load target owners (Excel only has owner names)
# ======================
targets_df = pd.read_excel(EXCEL_FILE, sheet_name=TARGET_SHEET)
targets_df.columns = targets_df.columns.str.lower()

# Extract the owner column
target_owner_col = None
for cand in ["owner_clean", "owner", "owner_name", "deeded_owner"]:
    if cand in targets_df.columns:
        target_owner_col = cand
        break
if target_owner_col is None:
    raise KeyError(f"Could not find an owner column in '{TARGET_SHEET}'.")

target_owners = (
    targets_df[target_owner_col]
    .dropna()
    .map(clean_owner)   # normalize
    .drop_duplicates()
    .tolist()
)

if not target_owners:
    raise ValueError(f"No target owners found in '{TARGET_SHEET}'.")

print(f"Loaded {len(target_owners)} target owners from Excel.")

# ======================
# Filter CSV to target owners BEFORE merge
# ======================
csv_targets = csv_df[csv_df["owner_clean"].isin(target_owners)].copy()

# Now merge only those parcels with SHP
merged_targets = gdf[["parcelpin", "geometry", "deeded_owner"]].merge(
    csv_targets.drop(columns=["geometry"], errors="ignore"),
    on="parcelpin",
    how="inner"   # only keep parcels in CSV that belong to targets
)

# Sanitize for folium
merged_targets = sanitize_for_geojson(merged_targets)


# ======================
# Portfolio stats (for sidebar)
# ======================
def owner_stats(df: pd.DataFrame, owner: str) -> dict:
    sub = df[df["owner_clean"] == owner]
    count = len(sub)
    sales_col = "sales_amount" if "sales_amount" in sub.columns else ("sales_amou" if "sales_amou" in sub.columns else None)
    total_sales = sub[sales_col].sum() if sales_col else 0
    total_assess = sub["certified_tax_total"].sum() if "certified_tax_total" in sub.columns else 0
    avg_sales = (total_sales / count) if count else 0
    avg_assess = (total_assess / count) if count else 0

    # Zip breakdown
    zipcol = "par_zip" if "par_zip" in sub.columns else None
    if zipcol:
        zip_tbl = (
            sub.groupby(zipcol)
            .agg(
                properties=("parcelpin", "count"),
                sales_total=(sales_col, "sum") if sales_col else ("parcelpin", "count"),
                assess_total=("certified_tax_total", "sum") if "certified_tax_total" in sub.columns else ("parcelpin", "count"),
            )
            .reset_index()
            .sort_values("properties", ascending=False)
        )
    else:
        zip_tbl = pd.DataFrame(columns=["par_zip", "properties", "sales_total", "assess_total"])

    return {
        "owner": owner,
        "count": int(count),
        "total_sales": float(total_sales),
        "total_assess": float(total_assess),
        "avg_sales": float(avg_sales),
        "avg_assess": float(avg_assess),
        "zip_table": zip_tbl
    }

# Stats per owner
stats_per_owner = {o: owner_stats(merged_targets, o) for o in target_owners}

# Aggregate stats (All Target Owners)
def aggregate_stats(df: pd.DataFrame) -> dict:
    count = len(df)
    sales_col = "sales_amount" if "sales_amount" in df.columns else ("sales_amou" if "sales_amou" in df.columns else None)
    total_sales = df[sales_col].sum() if sales_col else 0
    total_assess = df["certified_tax_total"].sum() if "certified_tax_total" in df.columns else 0
    avg_sales = (total_sales / count) if count else 0
    avg_assess = (total_assess / count) if count else 0
    zipcol = "par_zip" if "par_zip" in df.columns else None
    if zipcol:
        zip_tbl = (
            df.groupby(zipcol)
            .agg(
                properties=("parcelpin", "count"),
                sales_total=(sales_col, "sum") if sales_col else ("parcelpin", "count"),
                assess_total=("certified_tax_total", "sum") if "certified_tax_total" in df.columns else ("parcelpin", "count"),
            )
            .reset_index()
            .sort_values("properties", ascending=False)
        )
    else:
        zip_tbl = pd.DataFrame(columns=["par_zip", "properties", "sales_total", "assess_total"])
    return {
        "owner": "ALL TARGET OWNERS",
        "count": int(count),
        "total_sales": float(total_sales),
        "total_assess": float(total_assess),
        "avg_sales": float(avg_sales),
        "avg_assess": float(avg_assess),
        "zip_table": zip_tbl
    }

all_stats = aggregate_stats(merged_targets)

# ======================
# Build Map
# ======================
m = folium.Map(location=[41.4993, -81.6944], zoom_start=11, tiles="cartodbpositron")

# Base layer: all target-owner parcels (light grey)
base_context_layer = folium.GeoJson(
    merged_targets,
    name="All Target Owners (context)",
    style_function=lambda x: {"color": "grey", "weight": 0.4, "fillOpacity": 0.08},
)
base_context_layer.add_to(m)

# Colors per owner (prefer new Matplotlib colormap API; fallback for older)
num_colors = max(5, len(target_owners))
try:
    from matplotlib import colormaps as mpl_cmaps  # 3.6+
    cmap = mpl_cmaps.get_cmap("Set1").resampled(num_colors)
except Exception:
    # Deprecated in 3.7+, but kept for backward compatibility
    cmap = cm.get_cmap("Set1", num_colors)
owner_colors = {owner: colors.rgb2hex(cmap(i % cmap.N)) for i, owner in enumerate(target_owners)}

# Popup/tooltip fields (choose only columns that actually exist after merge)
candidate_fields = [
    "parcelpin", "parcel_id", "objectid",
    "par_addr", "par_addr_a", "par_addr_all",
    "owner_clean", "tax_luc_description",
    "sales_amou", "sales_amount"
]
popup_fields = [f for f in candidate_fields if f in merged_targets.columns]
print("Using popup fields:", popup_fields)

# Safety check to see your columns once:
print("merged_targets columns:", merged_targets.columns.tolist())

# Common aliases mapping for popups/tooltips
alias_map = {
            "parcelpin": "Parcel PIN:",
            "parcel_id": "Parcel ID:",
            "objectid": "Object ID:",
            "par_addr": "Address:",
            "par_addr_a": "Alt Address:",
            "par_addr_all": "Address (Full):",
            "owner_clean": "Owner:",
            "tax_luc_description": "Land Use:",
            "sales_amou": "Sale Price:",
            "sales_amount": "Sale Price:",
        }
aliases_common = [alias_map.get(f, f + ":") for f in popup_fields]

# Per-owner layers
owner_layer_vars = {}
def owner_to_slug(o: str) -> str:
    return owner_slug(o)

for owner in target_owners:
    color = owner_colors[owner]
    subset = merged_targets[merged_targets["owner_clean"] == owner].copy()
    print(f"Owner {owner}: subset rows={len(subset)}")

    # Skip tooltip/popup rendering if there are no features for this owner
    if subset.empty:
        group = folium.FeatureGroup(name=f"{owner} (0)")
        group.add_to(m)
        owner_layer_vars[owner_to_slug(owner)] = group.get_name()
        continue

    # Only keep fields that truly exist for THIS subset
    available_fields = [c for c in popup_fields if c in subset.columns]

    # If nothing is available, add the layer without popups/tooltip (prevents crash)
    if not available_fields:
        print(f"⚠️ Skipping popups for {owner}, no available fields.")
        gj = folium.GeoJson(
            subset,
            name=f"{owner} ({len(subset)})",
            style_function=lambda x, c=color: {"color": c, "weight": 1, "fillOpacity": 0.55},
        )
        gj.add_to(m)
        owner_layer_vars[owner_to_slug(owner)] = gj.get_name()
    else:
        # Keep only the available fields + geometry so Folium serializes them as properties
        subset = subset[available_fields + ["geometry"]]

        # Build aliases to match the exact number/order of available_fields
        aliases = [alias_map.get(f, f + ":") for f in available_fields]

        gj = folium.GeoJson(
            subset,
            name=f"{owner} ({len(subset)})",
            style_function=lambda x, c=color: {"color": c, "weight": 1, "fillOpacity": 0.55},
            tooltip=folium.GeoJsonTooltip(fields=available_fields, aliases=aliases, localize=True),
            popup=folium.GeoJsonPopup(fields=available_fields, aliases=aliases, localize=True, labels=True),
        )
        gj.add_to(m)
        owner_layer_vars[owner_to_slug(owner)] = gj.get_name()

# ----------------------
# ZIP-based layers
# ----------------------
zip_layer_vars = {}
zip_codes = []
if "par_zip" in merged_targets.columns:
    # Normalize ZIP codes to string without decimals
    zip_codes = (
        merged_targets["par_zip"].dropna().astype("Int64").astype(str).drop_duplicates().sort_values().tolist()
    )

    # Ensure owner_color property for styling within ZIP layers
    merged_targets["owner_color"] = merged_targets["owner_clean"].map(owner_colors)

    for z in zip_codes:
        zsubset = merged_targets[merged_targets["par_zip"].astype("Int64").astype(str) == z].copy()
        if zsubset.empty:
            continue
        # Keep only popup fields + styling + geometry
        keep_cols = [c for c in popup_fields if c in zsubset.columns]
        zsubset = zsubset[keep_cols + ["owner_color", "geometry"]]

        gj = folium.GeoJson(
            zsubset,
            name=f"ZIP {z} ({len(zsubset)})",
            style_function=lambda feature: {
                "color": feature["properties"].get("owner_color", "#666"),
                "weight": 1,
                "fillOpacity": 0.55,
            },
            tooltip=folium.GeoJsonTooltip(fields=keep_cols, aliases=[alias_map.get(f, f + ":") for f in keep_cols], localize=True),
            popup=folium.GeoJsonPopup(fields=keep_cols, aliases=[alias_map.get(f, f + ":") for f in keep_cols], localize=True, labels=True),
        )
        # Do not add ZIP layers by default; they will be toggled on demand
        zip_layer_vars[f"zip_{z}"] = gj.get_name()

# Inject JS to toggle owner layers based on dropdown selection
map_var = m.get_name()
base_var = base_context_layer.get_name()
layers_entries = ", ".join(["'" + k + "': '" + v + "'" for k, v in owner_layer_vars.items()])
layers_entries_zip = ", ".join(["'" + k + "': '" + v + "'" for k, v in zip_layer_vars.items()])
owner_name_to_slug = ", ".join(["'" + o.replace("'", "\\'") + "': '" + owner_to_slug(o) + "'" for o in target_owners])
toggle_js = (
    "(function() {\n" +
    "  var gsMapName = '" + map_var + "';\n" +
    "  var gsOwnerLayerNames = { " + layers_entries + " };\n" +
    "  var gsZipLayerNames = { " + layers_entries_zip + " };\n" +
    "  var gsOwnerNameToSlug = { " + owner_name_to_slug + " };\n" +
    "  var gsBaseContextName = '" + base_var + "';\n" +
    "  window.gsToggleLayers = function() {\n" +
    "    var sel = document.getElementById('ownerSelect').value;\n" +
    "    var zselEl = document.getElementById('zipSelect');\n" +
    "    var zsel = zselEl ? zselEl.value : 'all';\n" +
    "    var modeEl = document.querySelector(\"input[name='gsMode']:checked\");\n" +
    "    var mode = modeEl ? modeEl.value : 'owner';\n" +
    "    var map = window[gsMapName];\n" +
    "    if (!map) { return; }\n" +
    "    // Toggle layers based on mode\n" +
    "    if (mode === 'owner') {\n" +
    "      // Owner mode: show only selected owner layer (or all)\n" +
    "      Object.keys(gsOwnerLayerNames).forEach(function(key) {\n" +
    "        var lname = gsOwnerLayerNames[key];\n" +
    "        var layer = window[lname]; if (!layer) { return; }\n" +
    "        if (sel === 'all') { if (!map.hasLayer(layer)) map.addLayer(layer); }\n" +
    "        else { if (key === sel) { if (!map.hasLayer(layer)) map.addLayer(layer); } else { if (map.hasLayer(layer)) map.removeLayer(layer); } }\n" +
    "      });\n" +
    "      // Hide any ZIP layers\n" +
    "      Object.keys(gsZipLayerNames).forEach(function(key){ var lname=gsZipLayerNames[key]; var layer=window[lname]; if(layer && map.hasLayer(layer)) map.removeLayer(layer); });\n" +
    "    } else {\n" +
    "      // ZIP mode: show only selected ZIP layer (or all)\n" +
    "      Object.keys(gsZipLayerNames).forEach(function(key){\n" +
    "        var lname=gsZipLayerNames[key]; var layer=window[lname]; if(!layer){return;}\n" +
    "        if (zsel === 'all') { if (!map.hasLayer(layer)) map.addLayer(layer); }\n" +
    "        else { if (key === zsel) { if (!map.hasLayer(layer)) map.addLayer(layer); } else { if (map.hasLayer(layer)) map.removeLayer(layer); } }\n" +
    "      });\n" +
    "      // Hide any owner layers\n" +
    "      Object.keys(gsOwnerLayerNames).forEach(function(key){ var lname=gsOwnerLayerNames[key]; var layer=window[lname]; if(layer && map.hasLayer(layer)) map.removeLayer(layer); });\n" +
    "    }\n" +
    "    var baseLayer = window[gsBaseContextName];\n" +
    "    if (typeof baseLayer !== 'undefined') {\n" +
    "      var showBase = (mode === 'owner' && sel === 'all') || (mode === 'zip' && zsel === 'all');\n" +
    "      if (showBase) { if (!map.hasLayer(baseLayer)) map.addLayer(baseLayer); } else { if (map.hasLayer(baseLayer)) map.removeLayer(baseLayer); }\n" +
    "    }\n" +
    "  };\n" +
    "  window.gsTypeOwner = function() {\n" +
    "    var input = document.getElementById('ownerSearch'); if (!input) return;\n" +
    "    var q = input.value.toLowerCase();\n" +
    "    var allNames = Object.keys(gsOwnerNameToSlug);\n" +
    "    var matches = allNames.filter(function(name){ return q === '' || name.toLowerCase().indexOf(q) !== -1; });\n" +
    "    // Update datalist suggestions\n" +
    "    var dl = document.getElementById('ownerSuggestions'); if (dl) { dl.innerHTML = matches.map(function(n){ return `\\u003Coption value='${n}'\\u003E`; }).join(''); }\n" +
    "    // Update the portfolio dropdown to show only matches\n" +
    "    var sel = document.getElementById('ownerSelect'); if (sel) { sel.innerHTML = `\\u003Coption value='all'\\u003EAll Target Owners\\u003C/option\\u003E` + matches.map(function(n){ return `\\u003Coption value='${gsOwnerNameToSlug[n]}'\\u003E${n}\\u003C/option\\u003E`; }).join(''); }\n" +
    "    // Auto-select first match when typing\n" +
    "    if (sel) { if (matches.length > 0) sel.value = gsOwnerNameToSlug[matches[0]]; else sel.value = 'all'; }\n" +
    "    var ownerMode = document.getElementById('mode_owner'); if (ownerMode) ownerMode.checked = true;\n" +
    "    if (typeof gsToggleLayers==='function') { gsToggleLayers(); }\n" +
    "    if (typeof gsShowOwner==='function') { gsShowOwner(); }\n" +
    "  };\n" +
    "})();\n"
)
m.get_root().script.add_child(folium.Element(toggle_js))


# ======================
# Sidebar (static HTML)
# ======================
def zip_table_html(zip_df: pd.DataFrame) -> str:
    if zip_df.empty:
        return "<em>No ZIP breakdown available.</em>"
    # Try to standardize column names
    cols = [c for c in zip_df.columns]
    # rename for display if present
    rename_map = {}
    if "par_zip" in cols: rename_map["par_zip"] = "ZIP"
    if "properties" in cols: rename_map["properties"] = "Count"
    if "sales_total" in cols: rename_map["sales_total"] = "Sales Total"
    if "assess_total" in cols: rename_map["assess_total"] = "Assessed Total"
    disp = zip_df.rename(columns=rename_map).copy()
    # format ZIP codes to be 5 digits
    disp["ZIP"] = disp["ZIP"].astype(str).str.zfill(5)
    # format money
    if "Sales Total" in disp.columns:
        disp["Sales Total"] = disp["Sales Total"].map(fmt_money)
    if "Assessed Total" in disp.columns:
        disp["Assessed Total"] = disp["Assessed Total"].map(fmt_money)
    return (
        "<table style='width:100%; border-collapse:collapse;'>"
        "<tr>" + "".join(f"<th style='text-align:left; border-bottom:1px solid #ddd; padding:4px 6px'>{c}</th>" for c in disp.columns) + "</tr>" +
        "".join(
            "<tr>" + "".join(
                f"<td style='border-bottom:1px solid #f0f0f0; padding:4px 6px'>{row[c]}</td>" for c in disp.columns
            ) + "</tr>"
            for _, row in disp.iterrows()
        ) +
        "</table>"
    )

def zip_owner_table_html(zdf: pd.DataFrame) -> str:
    if zdf.empty:
        return "<em>No portfolio activity in this ZIP.</em>"
    disp = zdf.copy()
    disp = disp.rename(columns={"owner_clean": "Owner", "properties": "Count", "sales_total": "Sales Total", "assess_total": "Assessed Total"})
    if "Sales Total" in disp.columns:
        disp["Sales Total"] = disp["Sales Total"].map(fmt_money)
    if "Assessed Total" in disp.columns:
        disp["Assessed Total"] = disp["Assessed Total"].map(fmt_money)
    return (
        "<table style='width:100%; border-collapse:collapse; margin-top:6px'>"
        "<tr>" + "".join(f"<th style='text-align:left; border-bottom:1px solid #ddd; padding:4px 6px'>{c}</th>" for c in ["Owner","Count","Sales Total","Assessed Total"]) + "</tr>" +
        "".join(
            f"<tr><td style='border-bottom:1px solid #f0f0f0; padding:4px 6px'>{row['Owner']}</td><td style='border-bottom:1px solid #f0f0f0; padding:4px 6px'>{row['Count']}</td><td style='border-bottom:1px solid #f0f0f0; padding:4px 6px'>{row['Sales Total']}</td><td style='border-bottom:1px solid #f0f0f0; padding:4px 6px'>{row['Assessed Total']}</td></tr>"
            for _, row in disp.iterrows()
        ) +
        "</table>"
    )

def zip_panel_html(zip_code: str, df: pd.DataFrame) -> str:
    sub = df[df.get("par_zip").astype("Int64").astype(str) == zip_code]
    count = len(sub)
    sales_col = "sales_amount" if "sales_amount" in sub.columns else ("sales_amou" if "sales_amou" in sub.columns else None)
    total_sales = sub[sales_col].sum() if sales_col else 0
    total_assess = sub["certified_tax_total"].sum() if "certified_tax_total" in sub.columns else 0
    owners_tbl = (
        sub.groupby("owner_clean")
        .agg(properties=("parcelpin","count"), sales_total=(sales_col,"sum") if sales_col else ("parcelpin","count"), assess_total=("certified_tax_total","sum") if "certified_tax_total" in sub.columns else ("parcelpin","count"))
        .reset_index().sort_values("properties", ascending=False)
    )
    return f"""
    <div class="stats zip" id="zip_{zip_code}" style="display:none;">
      <h3 style="margin:8px 0 6px 0;">ZIP {zip_code}</h3>
      <div><b>Properties:</b> {int(count)}</div>
      <div><b>Total Sales:</b> {fmt_money(float(total_sales))}</div>
      <div><b>Total Assessed:</b> {fmt_money(float(total_assess))}</div>
      <div style="margin-top:8px;"><b>Portfolios in ZIP</b></div>
      <div>{zip_owner_table_html(owners_tbl)}</div>
    </div>
    """

def owner_panel_html(o: str, st: dict) -> str:
    return f"""
    <div class="stats owner" id="owner_{o.replace(' ', '_').replace('&','')}">
      <h3 style="margin:8px 0 6px 0;">{o}</h3>
      <div><b>Properties:</b> {st['count']}</div>
      <div><b>Total Sales:</b> {fmt_money(st['total_sales'])}</div>
      <div><b>Total Assessed:</b> {fmt_money(st['total_assess'])}</div>
      <div><b>Avg Sales:</b> {fmt_money(st['avg_sales'])}</div>
      <div><b>Avg Assessed:</b> {fmt_money(st['avg_assess'])}</div>
      <div style="margin-top:8px;"><b>By ZIP</b></div>
      <div>{zip_table_html(st['zip_table'])}</div>
    </div>
    """

# Build all owner panels
owner_panels = "\n".join(owner_panel_html(o, stats_per_owner[o]) for o in target_owners)
owner_panels = owner_panels.replace("owner_", "owner_")

# Build ALL panel
all_panel = owner_panel_html("All Target Owners", all_stats).replace("owner_All_Target_Owners", "owner_all")

zip_panels = "\n".join(zip_panel_html(z, merged_targets) for z in zip_codes) if zip_codes else ""

sidebar_html = f"""
<div id="gs-sidebar" style="
    position: fixed; top: 12px; left: 12px; width: 340px; max-height: 86vh;
    z-index: 9999; background: #fff; border: 1px solid #ddd; border-radius: 8px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.08); overflow: auto; padding: 12px;">
  <h2 style="margin: 2px 0 10px 0; font-size: 18px;">Portfolio Viewer</h2>
  <div style="font-size: 12px; color:#666; margin-bottom:8px;">
    Select a target owner to see portfolio stats. Toggle map layers on the right to compare footprints.
  </div>
  <div style="font-size: 12px; margin-bottom:6px;">
    <label><input type="radio" name="gsMode" id="mode_owner" value="owner" checked onchange="gsModeChanged()"> By Portfolio</label>
    <label style="margin-left:10px;"><input type="radio" name="gsMode" id="mode_zip" value="zip" onchange="gsModeChanged()"> By ZIP</label>
  </div>
  <label for="ownerSearch" style="font-size:13px;">Search portfolio:</label>
  <input id="ownerSearch" list="ownerSuggestions" type="text" placeholder="Type to search..." oninput="gsTypeOwner()" style="width:100%; margin:4px 0 6px 0; padding:6px;" />
  <datalist id="ownerSuggestions">
    {"".join(f"<option value='{o}'>" for o in target_owners)}
  </datalist>
  <label for="ownerSelect" style="font-size:13px;">Select portfolio:</label>
  <select id="ownerSelect" onchange="gsShowOwner(); if (typeof gsToggleLayers==='function') {{ gsToggleLayers(); }}" style="width:100%; margin:6px 0 10px 0; padding:6px;">
    <option value="all">All Target Owners</option>
    {"".join(f"<option value='{owner_to_slug(o)}'>{o}</option>" for o in target_owners)}
  </select>

  <label for="zipSelect" style="font-size:13px; display:none;">Select ZIP:</label>
  <select id="zipSelect" onchange="gsShowZip(); if (typeof gsToggleLayers==='function') {{ gsToggleLayers(); }}" style="display:none; width:100%; margin:6px 0 10px 0; padding:6px;">
    <option value="all">All ZIPs</option>
    {"".join(f"<option value='zip_{z}'>ZIP {z}</option>" for z in zip_codes)}
  </select>

  <div id="gs-panels">
    <div class="stats" id="owner_all" style="display:block;">
      {all_panel}
    </div>
    {owner_panels}
    {zip_panels}
  </div>
</div>

<script>
function gsShowOwner() {{
  var sel = document.getElementById("ownerSelect").value;
  var panels = document.querySelectorAll("#gs-panels .stats");
  panels.forEach(function(p) {{ p.style.display = "none"; }});
  var el = document.getElementById(sel);
  if (el) el.style.display = "block";
  else document.getElementById("owner_all").style.display = "block";
}}

function gsShowZip() {{
  var sel = document.getElementById("zipSelect").value; // e.g., zip_44102 or 'all'
  var panels = document.querySelectorAll("#gs-panels .stats");
  panels.forEach(function(p) {{ p.style.display = "none"; }});
  if (sel === 'all') {{
    document.getElementById("owner_all").style.display = "block";
  }} else {{
    var el = document.getElementById(sel);
    if (el) el.style.display = "block"; else document.getElementById("owner_all").style.display = "block";
  }}
}}

function gsModeChanged() {{
  var isZip = document.getElementById('mode_zip').checked;
  var ownerSel = document.getElementById('ownerSelect');
  var ownerLbl = document.querySelector('label[for="ownerSelect"]');
  var zipSel = document.getElementById('zipSelect');
  var zipLbl = document.querySelector('label[for="zipSelect"]');
  if (isZip) {{
    ownerSel.style.display = 'none'; if (ownerLbl) ownerLbl.style.display = 'none';
    zipSel.style.display = 'block'; if (zipLbl) zipLbl.style.display = 'block';
    gsShowZip();
  }} else {{
    zipSel.style.display = 'none'; if (zipLbl) zipLbl.style.display = 'none';
    ownerSel.style.display = 'block'; if (ownerLbl) ownerLbl.style.display = 'block';
    gsShowOwner();
  }}
  if (typeof gsToggleLayers==='function') {{ gsToggleLayers(); }}
}}
</script>
"""

# Inject sidebar into the map
m.get_root().html.add_child(folium.Element(sidebar_html))

# ======================
# Save
# ======================
m.save(OUTPUT_MAP)
print(f"✅ Exported portfolio map with sidebar: {OUTPUT_MAP}")
