#!/usr/bin/env python3
"""
Assignment 2: Generate HTML Report
One-time artifact summarizing EDA outputs.
Follows Step 8 requirements exactly.
"""

from pathlib import Path
import base64

OUTPUT_DIR = Path(__file__).parents[1] / "outputs"
REPORT_PATH = OUTPUT_DIR / "assignment_2_eda_report.html"

def encode_image(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

def generate_report():
    images = {
        "01": OUTPUT_DIR / "01_acreage_histogram.png",
        "02": OUTPUT_DIR / "02_acreage_boxplot.png",
        "03": OUTPUT_DIR / "03_size_comparison.png",
        "04": OUTPUT_DIR / "04_precip_by_year.png",
        "05": OUTPUT_DIR / "05_il_temp_by_field.png",
        "06": OUTPUT_DIR / "06_grower_weather_comparison.png",
        "07": OUTPUT_DIR / "07_crop_counts_2025.png",
        "08": OUTPUT_DIR / "08_corn_trend.png",
        "09": OUTPUT_DIR / "09_size_vs_corn.png",
        "10": OUTPUT_DIR / "10_geospatial_map.png",
    }
    
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
        and <strong>Nebraska</strong> (York County). Each grower has 10 fields with 5 years (2021-2025) of 
        daily weather and annual CDL crop classifications.</p>
        <ul>
            <li><strong>Total fields:</strong> 30</li>
            <li><strong>Total area:</strong> 2,162 acres</li>
            <li><strong>Weather records:</strong> 54,780 daily observations</li>
            <li><strong>CDL years:</strong> 2021-2025</li>
        </ul>
    </div>
    
    <h2>1. Dataset Scope and Data Layers</h2>
    <table>
        <tr><th>Grower</th><th>Location</th><th>Fields</th><th>Total Area</th><th>Context</th></tr>
        <tr><td>Illinois</td><td>Iroquois County, IL</td><td>10</td><td>700.0 ac</td><td>Corn Belt, no irrigation</td></tr>
        <tr><td>Iowa</td><td>Kossuth County, IA</td><td>10</td><td>1,020.3 ac</td><td>Corn Belt, rain-fed</td></tr>
        <tr><td>Nebraska</td><td>York County, NE</td><td>10</td><td>441.7 ac</td><td>Platte Valley, center-pivot irrigation common</td></tr>
    </table>
    
    <h3>Data Layers Used</h3>
    <ul>
        <li><strong>Field boundaries:</strong> GeoJSON polygons from OpenStreetMap (EPSG:4326)</li>
        <li><strong>Weather:</strong> NASA POWER daily data (T2M, T2M_MAX, T2M_MIN, PRECTOTCORR, ALLSKY_SFC_SW_DWN, RH2M, WS10M)</li>
        <li><strong>CDL:</strong> USDA Cropland Data Layer annual crop classifications (2021-2025)</li>
    </ul>
    
    <div class="limitation">
        <strong>Soil analysis:</strong> Not required for this assignment and not included in the EDA focus.
    </div>
    
    <h2>2. Comparison Levels</h2>
    <p>This EDA compares data at three levels where the data supports it:</p>
    <table>
        <tr><th>Level</th><th>What Was Compared</th><th>Outputs</th></tr>
        <tr><td><strong>Within-field</strong></td><td>Weather across multiple years for the same representative field</td><td>Figures 4, 5</td></tr>
        <tr><td><strong>Across fields (within grower)</strong></td><td>Field acreage, temperature variation across all 10 Illinois fields</td><td>Figures 1, 2, 5</td></tr>
        <tr><td><strong>Across growers</strong></td><td>Field size, precipitation, temperature, and crop patterns between IL, IA, and NE</td><td>Figures 3, 6, 7, 8, 9, 10</td></tr>
    </table>
    
    <h2>3. Field Boundaries Analysis</h2>
    <p><em>Category: Field Boundaries | Level: Across fields and across growers</em></p>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['01']}" alt="Acreage Histogram">
        <div class="caption"><strong>Figure 1 (Statistical Visualization):</strong> Field acreage distribution by grower. Iowa shows the largest fields, Nebraska the smallest.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['02']}" alt="Acreage Boxplot">
        <div class="caption"><strong>Figure 2 (Statistical Visualization):</strong> Boxplot of field acreage by grower, showing median, quartiles, and outliers. Iowa median is ~110 acres, Illinois ~45 acres, Nebraska ~40 acres.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['03']}" alt="Size Comparison">
        <div class="caption"><strong>Figure 3 (Comparison Analysis):</strong> Mean vs. median field size comparison across growers. Iowa has both the highest mean and median, indicating consistently large fields.</div>
    </div>
    
    <h3>What the comparison shows:</h3>
    <p>Iowa has the largest average field size (102.0 acres) while Nebraska has the smallest (44.2 acres). 
    The difference is substantial and likely reflects historical land division patterns and mechanization levels.</p>
    
    <h2>4. Weather Analysis (Growing Season: April-September)</h2>
    <p><em>Category: Weather | Level: Within-field, across fields, and across growers</em></p>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['04']}" alt="Precipitation by Year">
        <div class="caption"><strong>Figure 4 (Statistical Visualization):</strong> Annual growing season precipitation for one representative field per grower (2021-2025). Shows interannual variability.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['05']}" alt="IL Temperature by Field">
        <div class="caption"><strong>Figure 5 (Statistical Visualization):</strong> Mean growing season temperature for all 10 Illinois fields. Shows minimal variation within the same climate grid.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['06']}" alt="Weather Comparison">
        <div class="caption"><strong>Figure 6 (Comparison Analysis):</strong> Growing season temperature and precipitation comparison across all three growers. Nebraska is warmest, Iowa is wettest.</div>
    </div>
    
    <h3>What the comparison shows:</h3>
    <p>Across-grower comparison reveals clear climate gradients: Iowa receives the most growing season precipitation (~500mm), while Nebraska is the warmest. Illinois falls between the two. The within-field time series (Figure 4) shows 2022 was the driest year across all three states.</p>
    
    <h2>5. CDL/Cropland Data Layer Analysis</h2>
    <p><em>Category: CDL/Cropland | Level: Across growers and field-year</em></p>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['07']}" alt="Crop Counts">
        <div class="caption"><strong>Figure 7 (Statistical Visualization):</strong> 2025 CDL crop type distribution by grower. Corn dominates all three regions.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['08']}" alt="Corn Trend">
        <div class="caption"><strong>Figure 8 (Statistical Visualization):</strong> Corn dominance trend by grower (2021-2025). Nebraska shows the most stable corn percentage.</div>
    </div>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['09']}" alt="Size vs Corn">
        <div class="caption"><strong>Figure 9 (Correlation Analysis):</strong> Field size vs. CDL corn percentage (2025). The regression line shows a weak negative correlation (R = -0.15), indicating larger fields are slightly less likely to be 100% corn.</div>
    </div>
    
    <h3>What the comparison shows:</h3>
    <p>Corn is the dominant crop across all three growers (60% of fields in 2025). The correlation between field size and corn percentage is weakly negative (R = -0.15), suggesting that field size is not a strong predictor of crop choice. The trend analysis shows Iowa had the highest corn percentage in 2022 (80%), while Nebraska maintained 60-70% consistently.</p>
    
    <h2>6. Geospatial Map</h2>
    <p><em>Level: Across growers</em></p>
    
    <div class="viz">
        <img src="data:image/png;base64,{encoded['10']}" alt="Geospatial Map">
        <div class="caption"><strong>Figure 10 (Geospatial Map):</strong> All 30 fields colored by 2025 CDL crop type. Fields are clustered within each county as expected for real farm operations. Corn (gold) dominates, with soybeans (green) concentrated in Iowa and Nebraska.</div>
    </div>
    
    <h3>What the map shows:</h3>
    <p>The map visualizes the spatial distribution of the three growers. Illinois and Iowa fields are in the eastern Corn Belt, while Nebraska fields are further west in the Platte River Valley. The color coding confirms corn dominance across all regions, with soybean fields interspersed.</p>
    
    <h2>7. Limitations and Assumptions</h2>
    <div class="limitation">
        <ul>
            <li><strong>Weather data:</strong> NASA POWER provides grid-cell averages, not exact field-level measurements. Fields within ~10 km share the same weather grid.</li>
            <li><strong>Field clustering:</strong> OSM farmland polygons in each county are geographically clustered, which is realistic but limits spatial independence.</li>
            <li><strong>Center-pivot irrigation:</strong> Identified by geographic proxy (York County, NE) rather than direct observation. CDL does not flag irrigation method.</li>
            <li><strong>CDL accuracy:</strong> Field-level classifications are based on pixel-majority voting and may misclassify small fields or mixed parcels.</li>
            <li><strong>Soil analysis:</strong> Not required for this assignment and not included.</li>
        </ul>
    </div>
    
    <h2>8. Conclusion</h2>
    <p>This EDA reveals meaningful patterns across the three-grower dataset. <strong>Field boundaries</strong> show Iowa's larger average field sizes (102 acres vs. 44-70 acres). <strong>Weather</strong> confirms regional climate gradients, with Iowa being the wettest and Nebraska the warmest. <strong>CDL data</strong> shows corn-soy rotation dominance with corn percentages ranging from 50-80% across growers and years. The weak correlation between field size and crop type suggests that management decisions are driven more by economics and rotation strategy than by field geometry.</p>
    
    <hr>
    <p><em>Report generated by Assignment 2 EDA subskill | my-farm-advisor/eda/assignment-2/ | All outputs based on real OSM field boundaries with NASA POWER weather and USDA CDL crop data (2021-2025).</em></p>
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
    print("Done!")

if __name__ == "__main__":
    main()
