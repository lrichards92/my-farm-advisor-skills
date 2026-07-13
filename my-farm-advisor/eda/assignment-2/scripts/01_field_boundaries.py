#!/usr/bin/env python3
"""
Assignment 2: Field Boundaries EDA
Generates 2 statistical visualizations + 1 comparison for field boundary category.
"""

from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

# Output directory
OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# Data paths
GROWERS = {
    "Illinois": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/boundary/field_boundaries.geojson"),
    "Iowa": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/boundary/field_boundaries.geojson"),
    "Nebraska": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/boundary/field_boundaries.geojson"),
}

def load_all_fields():
    records = []
    for grower, path in GROWERS.items():
        gdf = gpd.read_file(path)
        gdf["grower"] = grower
        # Calculate shape complexity (perimeter / sqrt(area))
        gdf_proj = gdf.to_crs("EPSG:5070")
        gdf["perimeter_m"] = gdf_proj.geometry.length
        gdf["area_m2"] = gdf_proj.geometry.area
        gdf["shape_complexity"] = gdf["perimeter_m"] / np.sqrt(gdf["area_m2"])
        records.append(gdf)
    return pd.concat(records, ignore_index=True)

def plot_acreage_distribution(df):
    """Viz 1: Overlapping histograms of field acreage by grower."""
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = {"Illinois": "#2E86AB", "Iowa": "#A23B72", "Nebraska": "#F18F01"}
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        subset = df[df["grower"] == grower]
        ax.hist(subset["area_acres"], bins=8, alpha=0.6, label=grower, color=colors[grower], edgecolor="black")
    ax.set_xlabel("Field Area (acres)", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Field Acreage Distribution by Grower", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "01_acreage_distribution.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def plot_shape_complexity(df):
    """Viz 2: Boxplot of shape complexity by grower."""
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = {"Illinois": "#2E86AB", "Iowa": "#A23B72", "Nebraska": "#F18F01"}
    sns.boxplot(data=df, x="grower", y="shape_complexity", palette=colors, ax=ax)
    ax.set_xlabel("Grower", fontsize=12)
    ax.set_ylabel("Shape Complexity (perimeter / sqrt(area))", fontsize=12)
    ax.set_title("Field Shape Complexity by Grower", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "02_shape_complexity.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def plot_size_vs_regularity(df):
    """Comparison: Field size vs. shape regularity scatter."""
    fig, ax = plt.subplots(figsize=(10, 7))
    colors = {"Illinois": "#2E86AB", "Iowa": "#A23B72", "Nebraska": "#F18F01"}
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        subset = df[df["grower"] == grower]
        ax.scatter(subset["area_acres"], subset["shape_complexity"], 
                   label=grower, color=colors[grower], s=100, alpha=0.7, edgecolors="black")
    ax.set_xlabel("Field Area (acres)", fontsize=12)
    ax.set_ylabel("Shape Complexity (perimeter / sqrt(area))", fontsize=12)
    ax.set_title("Field Size vs. Shape Regularity", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "03_size_vs_regularity.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)
    
    # Also save a summary table
    summary = df.groupby("grower").agg({
        "area_acres": ["count", "mean", "std", "min", "max"],
        "shape_complexity": ["mean", "std"]
    }).round(2)
    summary_path = OUTPUT_DIR / "boundary_summary.csv"
    summary.to_csv(summary_path)
    print(f"Saved: {summary_path}")

def main():
    print("=" * 60)
    print("Field Boundaries EDA")
    print("=" * 60)
    df = load_all_fields()
    print(f"Loaded {len(df)} fields from 3 growers")
    plot_acreage_distribution(df)
    plot_shape_complexity(df)
    plot_size_vs_regularity(df)
    print("\nField boundaries analysis complete!")

if __name__ == "__main__":
    main()
