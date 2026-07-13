#!/usr/bin/env python3
"""
Assignment 2: Weather EDA
2 statistical visualizations + 1 comparison (growing season: Apr-Sep)
"""

from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

COLORS = {"Illinois": "#2E86AB", "Iowa": "#A23B72", "Nebraska": "#F18F01"}

WEATHER_FILES = {
    "Illinois": "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/il-grower/farms/il-grower-illinois/derived/tables/il_grower_illinois_weather_2021_2025.csv",
    "Iowa": "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/iowa-grower/farms/iowa-grower-iowa/derived/tables/iowa_grower_iowa_weather_2021_2025.csv",
    "Nebraska": "/home/coder/my-farm-advisor-runtime/data-pipeline/growers/ne-grower/farms/ne-grower-nebraska/derived/tables/ne_grower_nebraska_weather_2021_2025.csv",
}

REP_FIELDS = {
    "Illinois": "osm-1499460308",
    "Iowa": "osm-1360326432",
    "Nebraska": "osm-554107589",
}

def load_growing_season():
    all_data = []
    for grower, path in WEATHER_FILES.items():
        df = pd.read_csv(path, parse_dates=["date"])
        df["month"] = df["date"].dt.month
        df["year"] = df["date"].dt.year
        df["grower"] = grower
        gs = df[(df["month"] >= 4) & (df["month"] <= 9)].copy()
        all_data.append(gs)
    return pd.concat(all_data, ignore_index=True)

def viz1_precip_by_year(df):
    """Statistical viz 1: Annual growing season precipitation for rep fields."""
    fig, ax = plt.subplots(figsize=(10, 6))
    for grower in ["Illinois", "Iowa", "Nebraska"]:
        rep = df[(df["grower"] == grower) & (df["field_id"] == REP_FIELDS[grower])]
        yearly = rep.groupby("year")["PRECTOTCORR"].sum().reset_index()
        ax.plot(yearly["year"], yearly["PRECTOTCORR"], marker="o", linewidth=2.5,
                label=grower, color=COLORS[grower], markersize=8)
    ax.set_xlabel("Year", fontsize=12)
    ax.set_ylabel("Growing Season Precipitation (mm, Apr-Sep)", fontsize=12)
    ax.set_title("Annual Growing Season Precipitation\nOne Representative Field per Grower", 
                 fontsize=14, fontweight="bold")
    ax.legend()
    ax.grid(alpha=0.3)
    ax.set_xticks([2021, 2022, 2023, 2024, 2025])
    plt.tight_layout()
    out = OUTPUT_DIR / "04_precip_by_year.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def viz2_temp_by_field(df):
    """Statistical viz 2: Growing season temperature for all Illinois fields."""
    il = df[df["grower"] == "Illinois"]
    field_temps = il.groupby("field_id")["T2M"].mean().reset_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(field_temps)), field_temps["T2M"], color=COLORS["Illinois"], alpha=0.7, edgecolor="black")
    ax.set_yticks(range(len(field_temps)))
    ax.set_yticklabels([f"Field {i+1}" for i in range(len(field_temps))], fontsize=9)
    ax.set_xlabel("Mean Growing Season Temperature (°C, Apr-Sep)", fontsize=12)
    ax.set_title("Growing Season Temperature: All 10 Illinois Fields\n(2021-2025 Average)", 
                 fontsize=14, fontweight="bold")
    ax.grid(axis="x", alpha=0.3)
    plt.tight_layout()
    out = OUTPUT_DIR / "05_il_temp_by_field.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)

def comparison_grower_weather(df):
    """Comparison: Weather summaries between IL, IA, and NE."""
    summary = df.groupby(["grower", "year"]).agg(
        temp_mean=("T2M", "mean"),
        precip_total=("PRECTOTCORR", "sum")
    ).reset_index()
    
    # Average across years
    avg = summary.groupby("grower").agg(
        temp_mean=("temp_mean", "mean"),
        precip_total=("precip_total", "mean")
    ).reset_index()
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Temperature
    bars1 = ax1.bar(avg["grower"], avg["temp_mean"], 
                    color=[COLORS[g] for g in avg["grower"]], alpha=0.8, edgecolor="black")
    ax1.set_ylabel("Mean Temperature (°C, Apr-Sep)", fontsize=12)
    ax1.set_title("Growing Season Temperature by Grower", fontsize=13, fontweight="bold")
    ax1.grid(axis="y", alpha=0.3)
    for bar in bars1:
        height = bar.get_height()
        ax1.annotate(f'{height:.1f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10)
    
    # Precipitation
    bars2 = ax2.bar(avg["grower"], avg["precip_total"], 
                    color=[COLORS[g] for g in avg["grower"]], alpha=0.8, edgecolor="black")
    ax2.set_ylabel("Total Precipitation (mm, Apr-Sep)", fontsize=12)
    ax2.set_title("Growing Season Precipitation by Grower", fontsize=13, fontweight="bold")
    ax2.grid(axis="y", alpha=0.3)
    for bar in bars2:
        height = bar.get_height()
        ax2.annotate(f'{height:.0f}', xy=(bar.get_x() + bar.get_width()/2, height),
                    xytext=(0, 3), textcoords="offset points", ha="center", fontsize=10)
    
    plt.tight_layout()
    out = OUTPUT_DIR / "06_grower_weather_comparison.png"
    fig.savefig(out, dpi=150, bbox_inches="tight")
    print(f"Saved: {out}")
    plt.close(fig)
    
    avg.to_csv(OUTPUT_DIR / "weather_summary.csv", index=False)
    print(f"Saved: {OUTPUT_DIR / 'weather_summary.csv'}")

def main():
    print("=" * 60)
    print("Weather EDA")
    print("=" * 60)
    df = load_growing_season()
    print(f"Loaded {len(df):,} growing season records")
    viz1_precip_by_year(df)
    viz2_temp_by_field(df)
    comparison_grower_weather(df)
    print("Done!")

if __name__ == "__main__":
    main()
