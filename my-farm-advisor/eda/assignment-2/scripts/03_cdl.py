#!/usr/bin/env python3
"""
Assignment 2: CDL/Cropland EDA
2 statistical visualizations + 1 comparison
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import geopandas as gpd

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {"Illinois": "#2E86AB", "Iowa": "#A23B72", "Nebraska": "#F18F01"}
CROP_COLORS = {"Corn": "#FFD700", "Soybeans": "#228B22", "Grass/Pasture": "#8B4513", "Forest": "#006400"}

CDL_FILES = {
    "Illinois": {
        2025: "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois_2025_cdl.csv",
    },
    "Iowa": {
        2025: "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa_2025_cdl.csv",
    },
    "Nebraska": {
        2025: "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska_2025_cdl.csv",
    },
}

BOUNDARY_FILES = {
    "Illinois": "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/boundary/field_boundaries.geojson",
    "Iowa": "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/boundary/field_boundaries.geojson",
    "Nebraska": "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/boundary/field_boundaries.geojson",
}

def load_cdl_2025():
    records = []
    for grower, paths in CDL_FILES.items():
        df = pd.read_csv(paths[2025])
        df["grower"] = grower
        records.append(df)
    return pd.concat(records, ignore_index=True)

def viz1_crop_counts_2025(cdl_df):
    """Statistical viz 1: CDL crop class counts across growers (2025)."""
    dominant = cdl_df.loc[cdl_df.groupby(["grower", "field_id"])["pct"].idxmax()]
    crop_counts = dominant.groupby(["grower", "crop_name"]).size().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    crop_counts.plot(kind="bar", stacked=True, ax=ax,
                     color={k: v for k, v in CROP_COLORS.items() if k in crop_counts.columns},
                     edgecolor="black")
    ax.set_xlabel("Grower", fontsize=12)
    ax.set_ylabel("Number of Fields", fontsize=12)
    ax.set_title("2025 CDL Crop Type Distribution by Grower\n(Dominant Crop per Field)", 
                 fontsize=14, fontweight="bold")
    ax.legend(title="Crop", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    out = OUTPUT_DIR / "07_crop_counts_2025.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def viz2_crop_trend():
    """Statistical viz 2: Corn percentage over time by grower (2021-2025)."""
    corn_pct = []
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        for year in [2021, 2022, 2023, 2024, 2025]:
            if grower == "Illinois":
                base = "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois"
            elif grower == "Iowa":
                base = "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa"
            else:
                base = "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska"
            
            path = f"{base}_{year}_cdl.csv"
            df = pd.read_csv(path)
            dominant = df.loc[df.groupby("field_id")["pct"].idxmax()]
            corn_count = (dominant["crop_name"] == "Corn").sum()
            total = len(dominant)
            corn_pct.append({
                "grower": grower,
                "year": year,
                "corn_pct": (corn_count / total) * 100
            })
    
    trend = pd.DataFrame(corn_pct)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        subset = trend[trend["grower"] == grower]
        ax.plot(subset["year"], subset["corn_pct"], marker="o", linewidth=2.5,
                label=grower, color=COLORS[grower], markersize=8)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Corn Fields (%)", fontsize=12)
    ax.set_title("Corn Dominance Trend by Grower (2021-2025)", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_ylim(0, 100)
    ax.set_xticks([2021, 2022, 2023, 2024, 2025])
    plt.tight_layout()
    out = OUTPUT_DIR / "08_corn_trend.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def comparison_size_vs_corn(cdl_df):
    """Comparison: Field size vs. CDL corn percentage (2025)."""
    # Get 2025 corn percentage per field
    corn_rows = cdl_df[cdl_df["crop_name"] == "Corn"][["grower", "field_id", "pct"]].copy()
    corn_rows.columns = ["grower", "field_id", "corn_pct"]
    
    # Get field sizes
    sizes = []
    for grower, path in BOUNDARY_FILES.items():
        gdf = gpd.read_file(path)
        for _, row in gdf.iterrows():
            sizes.append({"grower": grower, "field_id": row["field_id"], "area_acres": row["area_acres"]})
    size_df = pd.DataFrame(sizes)
    
    # Merge
    merged = corn_rows.merge(size_df, on=["grower", "field_id"])
    
    fig, ax = plt.subplots(figsize=(10, 7))
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        subset = merged[merged["grower"] == grower]
        ax.scatter(subset["area_acres"], subset["corn_pct"], 
                   label=grower, color=COLORS[grower], s=100, alpha=0.7, edgecolors="black")
    
    # Add regression line for all data
    if len(merged) > 2:
        slope, intercept, r_value, p_value, std_err = stats.linregress(merged["area_acres"], merged["corn_pct"])
        x_line = np.linspace(merged["area_acres"].min(), merged["area_acres"].max(), 100)
        ax.plot(x_line, slope * x_line + intercept, 'r--', alpha=0.6, 
                label=f'All growers (R={r_value:.2f})')
    
    ax.set_xlabel("Field Size (acres)", fontsize=12)
    ax.set_ylabel("CDL Corn Percentage (%)", fontsize=12)
    ax.set_title("Field Size vs. Corn Percentage (2025)\nCorrelation Analysis", 
                 fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "09_size_vs_corn.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)
    
    # Save correlation stats
    stats_df = pd.DataFrame({
        "metric": ["slope", "intercept", "r_value", "p_value", "std_err"],
        "value": [slope, intercept, r_value, p_value, std_err]
    })
    stats_df.to_csv(OUTPUT_DIR / "size_corn_correlation.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'size_corn_correlation.csv'}")

def main():
    print("=" * 60)
    print("CDL/Cropland EDA")
    print("=" * 60)
    cdl = load_cdl_2025()
    print(f"Loaded 2025 CDL data: {len(cdl)} records")
    viz1_crop_counts_2025(cdl)
    viz2_crop_trend()
    comparison_size_vs_corn(cdl)
    print("Done!")

if __name__ == "__main__":
    main()
