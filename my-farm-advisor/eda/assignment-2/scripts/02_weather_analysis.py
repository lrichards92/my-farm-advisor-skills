#!/usr/bin/env python3
"""
Assignment 2: Weather EDA
Generates 2 statistical visualizations + 1 PCA comparison for weather category.
Growing season = April-September.
"""

from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

GROWERS = {
    "Illinois": {
        "weather": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois_weather_2021_2025.csv"),
        "fields_dir": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/fields"),
        "color": "#2E86AB",
        "rep_field": "osm-1499460308"  # representative field
    },
    "Iowa": {
        "weather": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa_weather_2021_2025.csv"),
        "fields_dir": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/fields"),
        "color": "#A23B72",
        "rep_field": "osm-1360326432"
    },
    "Nebraska": {
        "weather": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska_weather_2021_2025.csv"),
        "fields_dir": Path("/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/fields"),
        "color": "#F18F01",
        "rep_field": "osm-554107589"
    }
}

def load_growing_season_weather():
    """Load weather data and filter to growing season (Apr-Sep)."""
    all_data = []
    for grower, info in GROWERS.items():
        df = pd.read_csv(info["weather"], parse_dates=["date"])
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year
        df["grower"] = grower
        # Filter growing season
        gs = df[(df["month"] >= 4) & (df["month"] <= 9)].copy()
        all_data.append(gs)
    return pd.concat(all_data, ignore_index=True)

def plot_growing_season_temperature(df):
    """Viz 1: Mean growing season temperature profile (one rep field per grower, 5-yr avg)."""
    fig, ax = plt.subplots(figsize=(12, 6))
    
    for grower, info in GROWERS.items():
        rep = df[(df["grower"] == grower) & (df["field_id"] == info["rep_field"])]
        monthly = rep.groupby("month")["T2M"].mean().reset_index()
        months = ["Apr", "May", "Jun", "Jul", "Aug", "Sep"]
        ax.plot(monthly["month"], monthly["T2M"], marker="o", linewidth=2.5, 
                label=grower, color=info["color"], markersize=8)
    
    ax.set_xticks([4, 5, 6, 7, 8, 9])
    ax.set_xticklabels(months)
    ax.set_xlabel("Month", fontsize=12)
    ax.set_ylabel("Mean Temperature (°C)", fontsize=12)
    ax.set_title("Growing Season Temperature Profile (5-Year Average)\nOne Representative Field per Grower", 
                 fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "04_growing_season_temperature.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def plot_growing_season_precipitation(df):
    """Viz 2: Growing season total precipitation by grower with interannual variability."""
    # Sum precipitation per field per year for growing season
    yearly_precip = df.groupby(["grower", "field_id", "year"])["PRECTOTCORR"].sum().reset_index()
    grower_summary = yearly_precip.groupby("grower").agg(
        mean_precip=("PRECTOTCORR", "mean"),
        std_precip=("PRECTOTCORR", "std")
    ).reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 6))
    colors = [GROWERS[g]["color"] for g in grower_summary["grower"]]
    bars = ax.bar(grower_summary["grower"], grower_summary["mean_precip"], 
                  yerr=grower_summary["std_precip"], capsize=5, color=colors, 
                  alpha=0.8, edgecolor="black")
    ax.set_ylabel("Growing Season Precipitation (mm)", fontsize=12)
    ax.set_title("Growing Season Total Precipitation by Grower\n(April-September, 2021-2025)", 
                 fontsize=14, fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "05_growing_season_precipitation.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def plot_weather_pca(df):
    """Comparison: PCA of growing season weather variables."""
    # Calculate growing season averages per field per year
    gs_yearly = df.groupby(["grower", "field_id", "year"]).agg(
        T2M_mean=("T2M", "mean"),
        PRECTOTCORR_sum=("PRECTOTCORR", "sum"),
        ALLSKY_SFC_SW_DWN_mean=("ALLSKY_SFC_SW_DWN", "mean")
    ).reset_index()
    
    # Then average across years per field
    field_avg = gs_yearly.groupby(["grower", "field_id"]).agg(
        T2M=("T2M_mean", "mean"),
        PRECTOTCORR=("PRECTOTCORR_sum", "mean"),
        ALLSKY_SFC_SW_DWN=("ALLSKY_SFC_SW_DWN_mean", "mean")
    ).reset_index()
    
    # Standardize and run PCA
    features = ["T2M", "PRECTOTCORR", "ALLSKY_SFC_SW_DWN"]
    X = field_avg[features].values
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    pca = PCA(n_components=2)
    pcs = pca.fit_transform(X_scaled)
    field_avg["PC1"] = pcs[:, 0]
    field_avg["PC2"] = pcs[:, 1]
    
    # Plot
    fig, ax = plt.subplots(figsize=(10, 8))
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        subset = field_avg[field_avg["grower"] == grower]
        ax.scatter(subset["PC1"], subset["PC2"], label=grower, 
                   color=GROWERS[grower]["color"], s=120, alpha=0.7, edgecolors="black")
    
    # Add loadings arrows
    loadings = pca.components_.T * np.sqrt(pca.explained_variance_)
    for i, feature in enumerate(features):
        ax.arrow(0, 0, loadings[i, 0]*2, loadings[i, 1]*2, 
                 color="red", width=0.005, head_width=0.1)
        ax.text(loadings[i, 0]*2.3, loadings[i, 1]*2.3, feature, 
                color="red", fontsize=10, fontweight="bold")
    
    ax.set_xlabel(f"PC1 ({pca.explained_variance_ratio_[0]*100:.1f}% variance)", fontsize=12)
    ax.set_ylabel(f"PC2 ({pca.explained_variance_ratio_[1]*100:.1f}% variance)", fontsize=12)
    ax.set_title("PCA of Growing Season Climate Variables\nPer Field (2021-2025 Average)", 
                 fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.axhline(y=0, color="k", linestyle="--", alpha=0.3)
    ax.axvline(x=0, color="k", linestyle="--", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "06_weather_pca.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)
    
    # Save PCA summary
    pca_summary = pd.DataFrame({
        "Component": ["PC1", "PC2"],
        "Explained_Variance_Ratio": pca.explained_variance_ratio_,
        "Cumulative_Variance": np.cumsum(pca.explained_variance_ratio_)
    })
    pca_summary.to_csv(OUTPUT_DIR / "pca_summary.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'pca_summary.csv'}")
    
    return field_avg

def main():
    print("=" * 60)
    print("Weather EDA (Growing Season: Apr-Sep)")
    print("=" * 60)
    df = load_growing_season_weather()
    print(f"Loaded {len(df):,} growing season records")
    plot_growing_season_temperature(df)
    plot_growing_season_precipitation(df)
    plot_weather_pca(df)
    print("\nWeather analysis complete!")

if __name__ == "__main__":
    main()
