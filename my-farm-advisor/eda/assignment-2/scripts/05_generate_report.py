#!/usr/bin/env python3
"""
Assignment 2: Generate HTML Report
One-time artifact summarizing EDA outputs.
"""

from pathlib import Path
import base64

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
REPORT_PATH = OUTPUT_DIR / "assignment_2_eda_report.html"

def encode_image(path):
    """Base64 encode an image for inline HTML."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def generate_report():
    images = {
        "01_acreage": OUTPUT_DIR / "01_acreage_distribution.png",
        "02_shape": OUTPUT_DIR / "02_shape_complexity.png",
        "03_size_reg": OUTPUT_DIR / "03_size_vs_regularity.png",
        "04_temp": OUTPUT_DIR / "04_growing_season_temperature.png",
        "05_precip": OUTPUT_DIR / "05_growing_season_precipitation.png",
        "06_pca": OUTPUT_DIR / "06_weather_pca.png",
        "07_crops": OUTPUT_DIR / "07_crop_distribution_2025.png",
        "08_diversity": OUTPUT_DIR / "08_rotation_diversity.png",
        "09_crop_precip": OUTPUT_DIR / "09_crop_vs_precipitation.png",
        "10_map": OUTPUT_DIR / "10_geospatial_map.png",
        "10_map_by": OUTPUT_DIR / "10_geospatial_map_by_grower.png",
    }
    
    # Base64 encode all images
    encoded = {k: encode_image(v) for k, v in images.items()}
    
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Assignment 2: Field-Level EDA Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; 
               max-width: 1000px; margin: 0 auto; padding: 20px; line-height: 1.6; color: #333; }}
        h1 {{ color: #1B5E20; border-bottom: 3px solid #4CAF50; padding-bottom: 10px; }}
        h2 {{ color: #2E7D32; margin-top: 30px; border-bottom: 2px solid #81C784; padding-bottom: 5px; }}
        h3 {{ color: #388E3C; }}
        .summary {{ background: #E8F5E9; padding: 15px; border-radius: 8px; margin: 20px 0; }}
        .viz {{ margin: 20px 0; text-align: center; }}
        .viz img {{ max-width: 100%; height: auto; border: 1px solid #ddd; border-radius: 4px; }}
        .caption {{ font-size: 0.9em; color: #666; margin-top: 5px; font-style: italic; }}
        table {{ border-collapse: collapse; width: 100%; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background: #4CAF50; color: white; }}
        tr:nth-child(even) {{ background: #f2f2f2; }}
        .limitation {{ background: #FFF3E0; padding: 10px; border-left: 4px solid #FF9800; margin: 15px 0; }}
    </style>
</head>
<body>
    <h1>Assignment 2: Field-Level EDA and Spatial Comparison</h1>
    <p><strong>Course:</strong> Agricultural Data Systems | <strong>Branch:</strong> assignment-2</p>
    
    <div class="summary">
        <h2>Executive Summary</h2>
        <p>This report presents exploratory data analysis of field boundaries, weather, and CDL/cropland data 
        across three growers: <strong>Illinois</strong> (Iroquois County), <strong>Iowa</strong> (Kossuth County), 
        and <strong>Nebraska</strong> (York County). Each grower has 10 fields with 5 years (2021–2025) of 
        daily weather and annual CDL crop classifications.</p>
        <ul>
            <li><strong>Total fields:</strong> 30</li>
            <li><strong>Total area:</strong> 2,162 acres</li>
            <li><strong>Weather records:</strong> 54,780 daily observations</li>
            <li><strong>CDL years:</strong> 2021–2025</li>
        </ul>
    </div>
    
    <h2>1. Dataset Scope</h2>
    <table>
        <tr><th>Grower</th><th>Location</th><th>Fields</th><th>Total Area</th><th>Avg Size</th><th>Context</th></tr>
        <tr><td>Illinois</td><td>Iroquois County, IL</td><td>10</td><td>700.0 ac</td><td>70.0 ac</td><td>Corn Belt, no irrigation</td></tr>
        <tr><td>Iowa</td><td>Kossuth County, IA</td><td>10</td><td>1,020.3 ac</td><td>102.0 ac</td><td>Corn Belt, rain-fed</td></tr>
        <tr><td>Nebraska</td><td>York County, NE</td><td>10</td><td>441.7 ac</td><td>44.2 ac</td><td>Platte Valley, center-pivot irrigation common</td></tr>
    </table>
    
    <div class="limitation">
        <strong>Nebraska Context:</strong> York County was chosen for its corn/soy production dominance and 
        extensive center-pivot irrigation infrastructure in the Platte River Valley. CDL confirms 8 of 10 
        fields are corn or soybean (2025).
    </div>
    
    <h2>2. Field Boundaries Analysis</h2>
    <p>Comparison of field sizes and shapes across the three growers.</p>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['01_acreage']}" alt="Acreage Distribution">
        <div class="caption">Figure 1: Field acreage distribution by grower. Iowa shows larger average field sizes.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['02_shape']}" alt="Shape Complexity">
        <div class="caption">Figure 2: Field shape complexity (perimeter / sqrt(area)). Higher values indicate more irregular shapes.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['03_size_reg']}" alt="Size vs Regularity">
        <div class="caption">Figure 3: Field size vs. shape regularity. Nebraska fields tend to be smaller and more regular.</div>
    </div>
    
    <h3>Key Finding:</h3>
    <p>Iowa has the largest fields (avg 102 acres) while Nebraska has the smallest (avg 44 acres). 
    Field shape complexity does not strongly correlate with size, suggesting all growers manage 
    both regular and irregular field geometries.</p>
    
    <h2>3. Weather Analysis (Growing Season: April–September)</h2>
    <p>Climate comparison using 5-year growing season averages. Principal Component Analysis (PCA) 
    reveals whether the three growers separate in climate space.</p>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['04_temp']}" alt="Temperature Profile">
        <div class="caption">Figure 4: Mean growing season temperature by month (5-year average). Nebraska shows slightly warmer mid-summer temperatures.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['05_precip']}" alt="Precipitation">
        <div class="caption">Figure 5: Total growing season precipitation by grower with interannual variability. Iowa receives the most rainfall.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['06_pca']}" alt="PCA">
        <div class="caption">Figure 6: PCA of growing season climate variables (temperature, precipitation, solar radiation). PC1 captures 62% of variance, primarily driven by precipitation and temperature gradients.</div>
    </div>
    
    <h3>Key Finding:</h3>
    <p>The PCA shows partial separation between growers. Iowa and Illinois overlap in climate space, 
    while Nebraska fields tend toward higher PC1 values (warmer, drier). This aligns with Nebraska's 
    more continental climate and need for center-pivot irrigation.</p>
    
    <h2>4. CDL/Cropland Data Layer Analysis</h2>
    <p>Crop type distributions and rotation patterns from the USDA Cropland Data Layer (2021–2025).</p>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['07_crops']}" alt="Crop Distribution">
        <div class="caption">Figure 7: 2025 CDL crop type distribution by grower. Corn dominates across all three states.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['08_diversity']}" alt="Rotation Diversity">
        <div class="caption">Figure 8: Crop rotation diversity (Shannon index) by field. Most fields show low diversity (corn-soy rotation).</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['09_crop_precip']}" alt="Crop vs Precipitation">
        <div class="caption">Figure 9: Growing season precipitation for Corn vs. Soybean fields. No significant difference in rainfall between crops.</div>
    </div>
    
    <h3>Key Finding:</h3>
    <p>Corn is the dominant crop (60% of all fields in 2025). Most fields practice simple corn-soy 
    rotation (Shannon diversity ~0.6–0.7). Precipitation does not significantly differ between 
    corn and soybean fields, suggesting crop choice is driven by other factors (markets, soil, rotation benefits).</p>
    
    <h2>5. Geospatial Context</h2>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['10_map']}" alt="Geospatial Map">
        <div class="caption">Figure 10: All 30 fields colored by 2025 CDL crop type. Fields are clustered within each county as expected for real farm operations.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['10_map_by']}" alt="Map by Grower">
        <div class="caption">Figure 11: Fields separated by grower with individual state contexts.</div>
    </div>
    
    <h2>6. Comparison Levels Summary</h2>
    <table>
        <tr><th>Level</th><th>What Was Compared</th><th>Key Insight</th></tr>
        <tr><td>Within-field</td><td>Weather across 5 years for representative fields</td><td>Interannual temperature variability is low; precipitation varies more</td></tr>
        <tr><td>Across-fields (within grower)</td><td>Field sizes, shapes, crop types</td><td>Size varies 10x within each farm; all farms grow both corn and soy</td></tr>
        <tr><td>Across-growers</td><td>Climate, field size, crop distribution</td><td>Nebraska is warmer/drier with smaller fields; Iowa is wettest with largest fields</td></tr>
    </table>
    
    <h2>7. Limitations and Assumptions</h2>
    <div class="limitation">
        <ul>
            <li><strong>Weather data:</strong> NASA POWER provides grid-cell averages, not exact field-level measurements. Fields within 10 km share the same weather grid.</li>
            <li><strong>Field clustering:</strong> OSM farmland polygons in each county are geographically clustered, which is realistic but limits spatial independence.</li>
            <li><strong>Center-pivot irrigation:</strong> Identified by geographic proxy (York County, NE) rather than direct observation. CDL does not flag irrigation method.</li>
            <li><strong>Soil analysis:</strong> Not required for this assignment and not included in EDA.</li>
            <li><strong>CDL accuracy:</strong> Field-level CDL classifications are based on pixel-majority voting and may misclassify small fields.</li>
        </ul>
    </div>
    
    <h2>8. Conclusion</h2>
    <p>The three-grower dataset successfully captures regional variation in the US Corn Belt. 
    <strong>Field boundaries</strong> reveal Iowa's larger field sizes and Nebraska's smaller, more regular parcels. 
    <strong>Weather analysis</strong> confirms climate gradients from east (Illinois/Iowa, wetter) to west 
    (Nebraska, drier). <strong>CDL data</strong> shows corn-soy rotation dominance with limited diversity. 
    The PCA demonstrates that climate alone partially separates the regions, but crop management 
    decisions (rotation, field size) also reflect economic and infrastructure factors beyond weather.</p>
    
    <hr>
    <p><em>Report generated by Assignment 2 EDA subskill | my-farm-advisor/eda/assignment-2/</em></p>
</body>
</html>"""
    
    REPORT_PATH.write_text(html, encoding="utf-8")
    print(f"Report saved to: {REPORT_PATH}")
    print(f"Size: {REPORT_PATH.stat().st_size / 1024:.1f} KB")

def main():
    print("=" * 60)
    print("Generating HTML Report")
    print("=" * 60)
    generate_report()
    print("\nReport generation complete!")

if __name__ == "__main__":
    main()
