import os
import pandas as pd

# -------------------------------
# CONFIG
# -------------------------------
INPUT_FILE = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\Combined_Parcels_-_Cleveland_Only.csv"
OUTPUT_EXCEL = r"C:\Users\jogol\Desktop\GS_Reports\ClevelandGIS\cleveland_ownership_analysis.xlsx"

VALID_TYPES = ["1-FAMILY PLATTED LOT", "2-FAMILY PLATTED LOT"]

# -------------------------------
# Helpers
# -------------------------------
def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    for col in ["deeded_owner", "deeded_own", "deed_owner", "ownername", "mail_name"]:
        if col in df.columns:
            df = df.rename(columns={col: "deeded_owner"})
            break
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

# -------------------------------
# Step 1: Load + Clean
# -------------------------------
csv_df = pd.read_csv(INPUT_FILE, low_memory=False)
csv_df = normalize_columns(csv_df)
print(f"Loaded {len(csv_df)} parcels from CSV")

csv_df = csv_df[csv_df["tax_luc_description"].isin(VALID_TYPES)].copy()
print(f"Filtered dataset: {len(csv_df)} parcels classified as 1-Family or 2-Family")

csv_df["owner_clean"] = csv_df["deeded_owner"].apply(clean_owner)

# Ownership summary
owner_summary = (
    csv_df.groupby("owner_clean")
    .size()
    .reset_index(name="parcel_count")
    .sort_values("parcel_count", ascending=False)
)

top5 = owner_summary.head(5)
print("Top 5 Owners:\n", top5)

# -------------------------------
# Step 2: Export
# -------------------------------
if not os.path.exists(OUTPUT_EXCEL):
    with pd.ExcelWriter(OUTPUT_EXCEL) as writer:
        owner_summary.to_excel(writer, sheet_name="Ownership Summary", index=False)
        csv_df.to_excel(writer, sheet_name="Raw Data", index=False)
    print(f"✅ Exported summaries: {OUTPUT_EXCEL}")
else:
    print(f"⚡ Skipped Excel export (already exists): {OUTPUT_EXCEL}")
