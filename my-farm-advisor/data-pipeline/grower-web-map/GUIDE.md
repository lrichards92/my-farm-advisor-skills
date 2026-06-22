---
name: grower-web-map
description: Generate lightweight, interactive HTML web maps for individual growers. Reads per-farm field boundary GeoJSON files and produces a single self-contained Leaflet.js map with click-to-view popups, a zoomable field list sidebar, and auto-fit bounds. Suitable for sharing via email or hosting on any static server.
version: "1.0.0"
author: Boreal Bytes
tags: [web-map, visualization, leaflet, geospatial, grower, interactive]
---

# Workflow: grower-web-map

## Description

Create a single self-contained HTML map for a grower. The map shows all field polygons across all of the grower's farms on a generic OpenStreetMap basemap.

**Key Features:**

- **Self-contained**: Single HTML file with embedded GeoJSON data
- **Field list sidebar**: Click any field name to zoom directly to it
- **Click-to-view popups**: Click a polygon to see grower, farm, field name, area, and county
- **Distinct farm colors**: Each farm gets its own fill color for easy visual separation
- **Auto-fit bounds**: The map automatically zooms to fit all fields on load
- **Lightweight**: No imagery, rasters, or external data bundles are embedded

## When to Use This Workflow

- **Sharing grower overviews**: Send a complete interactive map to collaborators or stakeholders
- **Field work planning**: Quick reference map for tablets or phones
- **Dashboards**: Include in grower-level reporting dashboards

## Prerequisites

To generate maps with data:

```bash
# No extra dependencies — the generator uses only the Python standard library.
# The output HTML requires only a modern web browser (Chrome, Firefox, Safari, Edge).
```

## API

```python
from pathlib import Path
from grower_web_map import generate_grower_web_map

output_path = generate_grower_web_map(
    grower_slug="iowa-grower",
    data_root=Path("/path/to/my-farm-advisor-runtime/data-pipeline"),
)
print(f"Map written to: {output_path}")
```

## CLI

```bash
export DATA_PIPELINE_DATA_ROOT=/path/to/my-farm-advisor-runtime
python src/scripts/reporting/generate_grower_web_map.py \
  --grower-slug iowa-grower
```

## Output

A single ``<grower-slug>_grower_web_map.html`` file (typically <100 KB for a few fields) that:

- Opens in any modern web browser
- Requires no installation or server
- Can be emailed as an attachment
- Can be hosted on any static web server

## Output Path

```
growers/<grower-slug>/derived/dashboards/<grower-slug>_grower_web_map.html
```

## Styling Notes

- Farm colors cycle through a built-in palette (green, blue, red, yellow, purple, teal, orange, blue-grey).
- Stroke color is consistently dark green (`#1B5E20`) with 90% opacity.
- Fill opacity is 35% so underlying basemap details remain visible.

## Resources

- [Leaflet Documentation](https://leafletjs.com/)
- [OpenStreetMap](https://www.openstreetmap.org/)
