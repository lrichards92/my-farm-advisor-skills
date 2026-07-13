#!/usr/bin/env python3
"""
Assignment 2: Geospatial Map
Static map of all 30 fields colored by 2025 CDL crop type.
"""

from pathlib import Path
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

GROWERS = {
    "Illinois": {
        "boundary": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/boundary/field_boundaries.geojson"),
        "cdl": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois_2025_cdl.csv"),
    },
    "Iowa": {
        "boundary": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/boundary/field_boundaries.geojson"),
        "cdl": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa_2025_cdl.csv"),
    },
    "Nebraska": {
        "boundary": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/boundary/field_boundaries.geojson"),
        "cdl": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska_2025_cdl.csv"),
    }
}

def load_all_with_crops():
    all_fields = []
    for grower, info in GROWERS.items():
        gdf = gpd.read_file(info["boundary"])
        gdf["grower"] = grower
        cdl = pd.read_csv(info["cdl"])
        dominant = cdl.loc[cdl.groupby("field_id")["pct"].idxmax()]
        crop_map = dict(zip(dominant["field_id"], dominant["crop_name"]))
        gdf["dominant_crop"] = gdf["field_id"].map(crop_map)
        all_fields.append(gdf)
    return pd.concat(all_fields, ignore_index=True)

def plot_map(combined):
    fig, ax = plt.subplots(figsize=(16, 10))
    
    crop_colors = {
        "Corn": "#FFD700",
        "Soybeans": "#228B22",
        "Grass/Pasture": "#8B4513",
        "Forest": "#006400",
    }
    
    for crop, color in crop_colors.items():
        subset = combined[combined["dominant_crop"] == crop]
        if len(subset) > 0:
            subset.plot(ax=ax, color=color, edgecolor="black", linewidth=0.8, 
                       alpha=0.7, label=crop)
    
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        subset = combined[combined["grower"] == grower]
        if len(subset) > 0:
            centroid = subset.geometry.union_all().centroid
            ax.annotate(grower, (centroid.x, centroid.y), 
                       fontsize=14, fontweight="bold", 
                       bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))
    
    ax.set_xlabel("Longitude", fontsize=12)
    ax.set_ylabel("Latitude", fontsize=12)
    ax.set_title("Field Boundaries by 2025 CDL Crop Type\nIllinois (10), Iowa (10), Nebraska (10)", 
                 fontsize=16, fontweight="bold")
    
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=color, edgecolor="black", label=crop) 
                      for crop, color in crop_colors.items()]
    ax.legend(handles=legend_elements, loc="lower right", title="CDL Crop")
    
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "10_geospatial_map.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def main():
    print("=" * 60)
    print("Geospatial Map")
    print("=" * 60)
    combined = load_all_with_crops()
    print(f"Loaded {len(combined)} fields")
    print(f"Crops: {combined['dominant_crop'].value_counts().to_dict()}")
    plot_map(combined)
    print("Done!")

if __name__ == "__main__":
    main()
