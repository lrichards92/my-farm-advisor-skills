"""Grower Web Map subskill — generate interactive HTML maps for farm growers."""

from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any


# Farm palette — enough for a handful of farms per grower.
_FARM_COLORS = [
    "#2E7D32",  # green
    "#1565C0",  # blue
    "#C62828",  # red
    "#F9A825",  # yellow
    "#6A1B9A",  # purple
    "#00695C",  # teal
    "#D84315",  # orange
    "#455A64",  # blue-grey
]


def _farm_color(index: int) -> str:
    return _FARM_COLORS[index % len(_FARM_COLORS)]


def _geojson_bounds(features: list[dict[str, Any]]) -> tuple[float, float, float, float] | None:
    """Compute [west, south, east, north] from all polygon coordinates."""
    lons: list[float] = []
    lats: list[float] = []
    for feature in features:
        geom = feature.get("geometry")
        if not geom:
            continue
        coords = geom.get("coordinates")
        if not coords:
            continue
        # Handle Polygon (list of rings) and fallback for MultiPolygon (list of polygons)
        if geom.get("type") == "Polygon":
            rings = coords
        elif geom.get("type") == "MultiPolygon":
            # Flatten: each polygon is list of rings
            rings = []
            for poly in coords:
                rings.extend(poly)
        else:
            continue
        for ring in rings:
            for pt in ring:
                if isinstance(pt, (list, tuple)) and len(pt) >= 2:
                    lons.append(float(pt[0]))
                    lats.append(float(pt[1]))
    if not lons:
        return None
    return min(lons), min(lats), max(lons), max(lats)


def _centroid(bounds: tuple[float, float, float, float]) -> tuple[float, float]:
    return (bounds[1] + bounds[3]) / 2.0, (bounds[0] + bounds[2]) / 2.0


def _build_html(
    grower_name: str,
    grower_slug: str,
    features: list[dict[str, Any]],
    farm_field_counts: dict[str, int],
    bounds: tuple[float, float, float, float],
) -> str:
    """Build a self-contained Leaflet HTML string."""
    west, south, east, north = bounds
    center_lat, center_lon = _centroid(bounds)

    # Farm index lookup for consistent coloring.
    farm_names = list(farm_field_counts.keys())
    farm_index = {name: i for i, name in enumerate(farm_names)}

    # Augment features with color index.
    for feature in features:
        farm_name = feature["properties"].get("farm", "Unknown")
        feature["properties"]["_farm_color"] = _farm_color(farm_index.get(farm_name, 0))
        feature["properties"]["_farm_index"] = farm_index.get(farm_name, 0)

    geojson_str = json.dumps({"type": "FeatureCollection", "features": features}, indent=2)

    # Sidebar items grouped by farm.
    sidebar_items: list[str] = []
    for farm_name in farm_names:
        color = _farm_color(farm_index[farm_name])
        sidebar_items.append(f"""
        <div class="farm-group">
          <div class="farm-header" style="border-left: 4px solid {color};">
            <span class="farm-color-dot" style="background:{color}"></span>
            <span class="farm-name">{farm_name}</span>
            <span class="farm-count">({farm_field_counts[farm_name]} fields)</span>
          </div>
          <ul class="field-list">
        """)
        for i, feature in enumerate(features):
            if feature["properties"].get("farm") == farm_name:
                field_id = feature["properties"].get("field_id", "Unknown")
                area = feature["properties"].get("area_acres")
                area_str = f"{area:.1f} ac" if isinstance(area, (int, float)) else ""
                label = field_id
                if area_str:
                    label += f" <span class='area'>{area_str}</span>"
                sidebar_items.append(f"""
            <li onclick="zoomToFeature({i})">
              {label}
            </li>
                """)
        sidebar_items.append("          </ul>\n        </div>")

    sidebar_html = "\n".join(sidebar_items)

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>Grower Web Map — {grower_name}</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"
        integrity="sha256-p4NxAoJBhIIN+hmNHrzRCf9tD/miZyoHS5obTRR9BMY=" crossorigin="" />
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"
          integrity="sha256-20nQCchB9co0qIjJZRGuk2/Z9VM+kNiyxNV1lvTlZBo=" crossorigin=""></script>
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    html, body {{ height: 100%; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    #map {{ position: absolute; top: 0; left: 0; right: 0; bottom: 0; z-index: 1; }}
    #sidebar {{
      position: absolute; top: 10px; left: 10px; bottom: 10px; width: 280px;
      background: rgba(255,255,255,0.95); border-radius: 8px;
      box-shadow: 0 2px 12px rgba(0,0,0,0.15); z-index: 1000;
      display: flex; flex-direction: column; overflow: hidden;
    }}
    #sidebar-header {{
      padding: 16px; border-bottom: 1px solid #e0e0e0;
      background: #f8f9fa; flex-shrink: 0;
    }}
    #sidebar-header h1 {{ font-size: 1.1rem; color: #1B5E20; margin-bottom: 4px; }}
    #sidebar-header .meta {{ font-size: 0.8rem; color: #666; }}
    #field-list {{ flex: 1; overflow-y: auto; padding: 8px 0; }}
    .farm-group {{ margin-bottom: 8px; }}
    .farm-header {{
      display: flex; align-items: center; padding: 8px 16px;
      font-weight: 600; font-size: 0.9rem; color: #333; border-left: 4px solid transparent;
      background: #fafafa;
    }}
    .farm-color-dot {{ width: 10px; height: 10px; border-radius: 50%; margin-right: 8px; }}
    .farm-count {{ margin-left: auto; font-weight: 400; color: #888; font-size: 0.8rem; }}
    .field-list {{ list-style: none; }}
    .field-list li {{
      padding: 6px 24px; font-size: 0.85rem; color: #444; cursor: pointer;
      transition: background 0.15s; display: flex; justify-content: space-between;
    }}
    .field-list li:hover {{ background: #e8f5e9; }}
    .field-list li .area {{ color: #888; font-size: 0.8rem; }}
    .leaflet-popup-content {{ font-size: 0.9rem; line-height: 1.5; }}
    .leaflet-popup-content b {{ color: #1B5E20; }}
    @media (max-width: 640px) {{
      #sidebar {{ width: 220px; }}
    }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div id="sidebar">
    <div id="sidebar-header">
      <h1>{grower_name}</h1>
      <div class="meta">{len(features)} field(s) across {len(farm_names)} farm(s)</div>
    </div>
    <div id="field-list">
{sidebar_html}
    </div>
  </div>

  <script>
    var geojsonData = {geojson_str};

    var map = L.map('map').setView([{center_lat}, {center_lon}], 10);

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{{z}}/{{y}}/{{x}}', {{
      maxZoom: 19,
      attribution: 'Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
    }}).addTo(map);

    var layerGroup = L.featureGroup();
    var featureLayers = [];

    L.geoJSON(geojsonData, {{
      style: function(feature) {{
        return {{
          color: '#FFFFFF',
          weight: 2.5,
          opacity: 1.0,
          fillColor: 'transparent',
          fillOpacity: 0
        }};
      }},
      onEachFeature: function(feature, layer) {{
        var props = feature.properties;
        var popupHtml = '<b>Grower:</b> ' + (props.grower || 'Unknown') + '<br>' +
                        '<b>Farm:</b> ' + (props.farm || 'Unknown') + '<br>' +
                        '<b>Field:</b> ' + (props.field_id || 'Unknown') + '<br>' +
                        '<b>Area:</b> ' + (props.area_acres ? props.area_acres.toFixed(1) + ' acres' : 'N/A') + '<br>' +
                        '<b>County:</b> ' + (props.county_name || 'N/A');
        layer.bindPopup(popupHtml);
        featureLayers.push(layer);
        layerGroup.addLayer(layer);
      }}
    }}).addTo(map);

    layerGroup.addTo(map);
    map.fitBounds(layerGroup.getBounds(), {{ padding: [40, 40] }});

    function zoomToFeature(index) {{
      var layer = featureLayers[index];
      if (layer) {{
        if (typeof layer.getBounds === 'function') {{
          map.fitBounds(layer.getBounds(), {{ padding: [60, 60], maxZoom: 16 }});
        }} else if (typeof layer.getLatLng === 'function') {{
          map.setView(layer.getLatLng(), 16);
        }}
        layer.openPopup();
      }}
    }}
  </script>
</body>
</html>"""
    return html


def generate_grower_web_map(
    grower_slug: str,
    data_root: Path,
    output_dir: Path | None = None,
) -> Path:
    """
    Generate an interactive Leaflet HTML map for the given grower.

    Parameters
    ----------
    grower_slug
        Canonical grower slug (e.g. ``iowa-grower``).
    data_root
        Absolute path to the pipeline data root
        (``${DATA_PIPELINE_DATA_ROOT}/data-pipeline``).
    output_dir
        Optional override for the output directory.  Defaults to
        ``growers/<slug>/derived/dashboards/``.

    Returns
    -------
    Path
        The written HTML file path.
    """
    grower_dir = data_root / "growers" / grower_slug
    if not grower_dir.exists():
        raise FileNotFoundError(f"Grower directory not found: {grower_dir}")

    # Read grower metadata.
    grower_json = grower_dir / "grower.json"
    grower_name = grower_slug
    if grower_json.exists():
        try:
            grower_data = json.loads(grower_json.read_text(encoding="utf-8"))
            grower_name = grower_data.get("display_name") or grower_slug
        except (OSError, json.JSONDecodeError):
            pass

    # Discover farms.
    farms_dir = grower_dir / "farms"
    if not farms_dir.exists():
        raise FileNotFoundError(f"No farms directory for grower: {farms_dir}")

    all_features: list[dict[str, Any]] = []
    farm_field_counts: dict[str, int] = {}

    for farm_path in sorted(farms_dir.iterdir()):
        if not farm_path.is_dir():
            continue

        farm_json = farm_path / "farm.json"
        farm_name = farm_path.name
        if farm_json.exists():
            try:
                farm_data = json.loads(farm_json.read_text(encoding="utf-8"))
                farm_name = farm_data.get("display_name") or farm_data.get("farm_slug") or farm_path.name
            except (OSError, json.JSONDecodeError):
                pass

        boundary_file = farm_path / "boundary" / "field_boundaries.geojson"
        if not boundary_file.exists():
            continue

        try:
            fc = json.loads(boundary_file.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue

        features = fc.get("features", [])
        farm_field_counts[farm_name] = len(features)

        for feature in features:
            props = feature.setdefault("properties", {})
            props["grower"] = grower_name
            props["grower_slug"] = grower_slug
            props["farm"] = farm_name
            props.setdefault("farm_slug", farm_path.name)
            all_features.append(feature)

    if not all_features:
        raise ValueError(f"No field boundaries found for grower '{grower_slug}'.")

    bounds = _geojson_bounds(all_features)
    if bounds is None:
        raise ValueError(f"Could not compute bounds for grower '{grower_slug}'.")

    html = _build_html(grower_name, grower_slug, all_features, farm_field_counts, bounds)

    out_dir = output_dir or (grower_dir / "derived" / "dashboards")
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{grower_slug}_grower_web_map.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
