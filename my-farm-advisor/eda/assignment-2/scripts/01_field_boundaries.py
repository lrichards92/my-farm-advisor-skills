#!/usr/bin/env python3
"""
Assignment 2: Field Boundaries EDA
2 statistical visualizations + 1 comparison
"""

from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

GROWERS = {
    "Illinois": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/boundary/field_boundaries.geojson"),
    "Iowa": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/boundary/field_boundaries.geojson"),
    "Nebraska": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/boundary/field_boundaries.geojson"),
}

COLORS = {"Illinois": "#2E86AB", "Iowa": "#A23B72", "Nebraska": "#F18F01"}

def load_data():
    records = []
    for grower, path in GROWERS.items():
        gdf = gpd.read_file(path)
        gdf["grower"] = grower
        records.append(gdf[["field_id", "area_acres", "grower"]])
    return pd.concat(records, ignore_index=True)

def viz1_acreage_histogram(df):
    """Statistical viz 1: Field acreage distribution by grower."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        subset = df[df["grower"] == grower]
        ax.hist(subset["area_acres"], bins=8, alpha=0.6, label=grower, 
                color=COLORS[grower], edgecolor="black")
    ax.set_xlabel("Field Area (acres)", fontsize=12)
    ax.set_ylabel("Count", fontsize=12)
    ax.set_title("Field Acreage Distribution by Grower", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "01_acreage_histogram.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def viz2_acreage_boxplot(df):
    """Statistical viz 2: Field acreage boxplot by grower."""
    fig, ax = plt.subplots(figsize=(8, 6))
    data = [df[df["grower"] == g]["area_acres"] for g in ["Illinois", "Iowa", "Nebraska"]]
    bp = ax.boxplot(data, patch_artist=True)
    ax.set_xticklabels(["Illinois", "Iowa", "Nebraska"])
    for patch, grower in zip(bp["boxes"], ["Illinois", "Iowa", "Nebraska"]):
        patch.set_facecolor(COLORS[grower])
        patch.set_alpha(0.7)
    ax.set_ylabel("Field Area (acres)", fontsize=12)
    ax.set_title("Field Acreage Distribution by Grower", fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "02_acreage_boxplot.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def comparison_size_by_grower(df):
    """Comparison: Mean/median field size comparison across growers."""
    summary = df.groupby("grower")["area_acres"].agg(["mean", "median", "std"]).round(1).reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    x = range(len(summary))
    width = 0.35
    bars1 = ax.bar([i - width/2 for i in x], summary["mean"], width, label="Mean", 
                   color=[COLORS[g] for g in summary["grower"]], alpha=0.8, edgecolor="black")
    bars2 = ax.bar([i + width/2 for i in x], summary["median"], width, label="Median", 
                   color=[COLORS[g] for g in summary["grower"]], alpha=0.5, edgecolor="black")
    ax.set_xticks(x)
    ax.set_xticklabels(summary["grower"])
    ax.set_ylabel("Field Area (acres)", fontsize=12)
    ax.set_title("Mean vs. Median Field Size by Grower", fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(axis="y", alpha=0.3)
    
    # Add value labels
    for bar in bars1:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    for bar in bars2:
        height = bar.get_height()
        ax.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                   xytext=(0, 3), textcoords="offset points", ha="center", fontsize=9)
    
    plt.tight_layout()
    out = OUTPUT_DIR / "03_size_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)
    
    summary.to_csv(OUTPUT_DIR / "field_size_summary.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'field_size_summary.csv'}")

def main():
    print("=" * 60)
    print("Field Boundaries EDA")
    print("=" * 60)
    df = load_data()
    print(f"Loaded {len(df)} fields")
    viz1_acreage_histogram(df)
    viz2_acreage_boxplot(df)
    comparison_size_by_grower(df)
    print("Done!")

if __name__ == "__main__":
    main()
