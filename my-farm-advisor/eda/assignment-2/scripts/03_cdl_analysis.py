#!/usr/bin/env python3
"""
Assignment 2: CDL/Cropland Data Layer EDA
Generates 2 statistical visualizations + 1 comparison for CDL category.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

GROWERS = {
    "Illinois": {
        "cdl": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois_2025_cdl.csv"),
        "rotation": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois_crop_rotation.csv"),
        "color": "#2E86AB"
    },
    "Iowa": {
        "cdl": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa_2025_cdl.csv"),
        "rotation": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa_crop_rotation.csv"),
        "color": "#A23B72"
    },
    "Nebraska": {
        "cdl": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska_2025_cdl.csv"),
        "rotation": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska_crop_rotation.csv"),
        "color": "#F18F01"
    }
}

def load_cdl_data():
    """Load 2025 CDL data for all growers."""
    records = []
    for grower, info in GROWERS.items():
        df = pd.read_csv(info["cdl"])
        df["grower"] = grower
        records.append(df)
    return pd.concat(records, ignore_index=True)

def load_rotation_data():
    """Load crop rotation data for diversity analysis."""
    records = []
    for grower, info in GROWERS.items():
        df = pd.read_csv(info["rotation"])
        df["grower"] = grower
        records.append(df)
    return pd.concat(records, ignore_index=True)

def plot_crop_distribution(cdl_df):
    """Viz 1: Stacked bar chart of crop types by grower (2025)."""
    # Get dominant crop per field
    dominant = cdl_df.loc[cdl_df.groupby(["grower", "field_id"])["pct"].idxmax()]
    crop_counts = dominant.groupby(["grower", "crop_name"]).size().unstack(fill_value=0)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    crop_counts.plot(kind="bar", stacked=True, ax=ax, 
                     color={"Corn": "#FFD700", "Soybeans": "#228B22", 
                            "Grass/Pasture": "#8B4513", "Forest": "#006400"},
                     edgecolor="black")
    ax.set_xlabel("Grower", fontsize=12)
    ax.set_ylabel("Number of Fields", fontsize=12)
    ax.set_title("2025 CDL Crop Type Distribution by Grower\n(Dominant Crop per Field)", 
                 fontsize=14, fontweight="bold")
    ax.legend(title="Crop", bbox_to_anchor=(1.05, 1), loc="upper left")
    ax.set_xticklabels(ax.get_xticklabels(), rotation=0)
    plt.tight_layout()
    out = OUTPUT_DIR / "07_crop_distribution_2025.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def plot_rotation_diversity(rotation_df):
    """Viz 2: Shannon diversity index per field (violin plot by grower)."""
    # The rotation CSV already has crop_diversity (Shannon index) calculated
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {"Illinois": "#2E86AB", "Iowa": "#A23B72", "Nebraska": "#F18F01"}
    sns.violinplot(data=rotation_df, x="grower", y="crop_diversity", palette=colors, ax=ax)
    ax.set_xlabel("Grower", fontsize=12)
    ax.set_ylabel("Shannon Diversity Index", fontsize=12)
    ax.set_title("Crop Rotation Diversity by Field (2021-2025)\nHigher = More Diverse Rotation", 
                 fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "08_rotation_diversity.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)
    
    return rotation_df[["grower", "field_id", "crop_diversity"]]

def plot_crop_vs_precipitation():
    """Comparison: Growing season precipitation for Corn vs. Soybean fields."""
    # Load weather data
    weather_data = []
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        if grower == "Illinois":
            w = pd.read_csv("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois_weather_2021_2025.csv", parse_dates=["date"])
        elif grower == "Iowa":
            w = pd.read_csv("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa_weather_2021_2025.csv", parse_dates=["date"])
        else:
            w = pd.read_csv("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska_weather_2021_2025.csv", parse_dates=["date"])
        w["month"] = w["date"].dt.month
        w["grower"] = grower
        weather_data.append(w)
    
    weather = pd.concat(weather_data, ignore_index=True)
    gs_weather = weather[(weather["month"] >= 4) & (weather["month"] <= 9)]
    
    # Get dominant crop per field for 2025
    cdl = load_cdl_data()
    dominant = cdl.loc[cdl.groupby(["grower", "field_id"])["pct"].idxmax()]
    
    # Calculate growing season precipitation per field
    field_precip = gs_weather.groupby(["grower", "field_id"])["PRECTOTCORR"].sum().reset_index()
    
    # Merge with crop type
    merged = field_precip.merge(dominant[["grower", "field_id", "crop_name"]], on=["grower", "field_id"])
    
    # Filter to Corn and Soybeans only
    crop_comparison = merged[merged["crop_name"].isin(["Corn", "Soybeans"])]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.boxplot(data=crop_comparison, x="crop_name", y="PRECTOTCORR", 
                palette={"Corn": "#FFD700", "Soybeans": "#228B22"}, ax=ax)
    ax.set_xlabel("Dominant Crop Type (2025)", fontsize=12)
    ax.set_ylabel("Growing Season Precipitation (mm, Apr-Sep)", fontsize=12)
    ax.set_title("Growing Season Precipitation: Corn vs. Soybean Fields\n(All Growers, 2021-2025 Average)", 
                 fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "09_crop_vs_precipitation.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)
    
    # Save summary table
    summary = crop_comparison.groupby("crop_name")["PRECTOTCORR"].agg(["count", "mean", "std", "min", "max"]).round(2)
    summary.to_csv(OUTPUT_DIR / "crop_precipitation_summary.csv")
    print(f"Saved: {OUTPUT_DIR / 'crop_precipitation_summary.csv'}")

def main():
    print("=" * 60)
    print("CDL/Cropland EDA")
    print("=" * 60)
    cdl = load_cdl_data()
    rotation = load_rotation_data()
    print(f"Loaded CDL data: {len(cdl)} records")
    print(f"Loaded rotation data: {len(rotation)} records")
    plot_crop_distribution(cdl)
    plot_rotation_diversity(rotation)
    plot_crop_vs_precipitation()
    print("\nCDL analysis complete!")

if __name__ == "__main__":
    main()
