# Local Instructions

## Purpose

This subskill generates lightweight, self-contained interactive HTML maps for individual growers. It reads per-farm field boundary GeoJSON files, combines them, and produces a single Leaflet.js web map with click-to-view popups and a zoomable field list sidebar.

## Safe edit scope

Edits should stay in this folder and its children. Do not change parent `SKILL.md`, sibling workflows, or root policy from a subskill task unless explicitly requested.

## Read nearby docs first

Read `GUIDE.md` first for the workflow and API reference. Read `../../AGENTS.md` for root-level asset and validation policy.

## Local validation

Run `./scripts/validate.sh` from the repository root after structural changes.

## Runtime contract

The core function `generate_grower_web_map(grower_slug, data_root, output_dir=None)` writes its output to:

```
growers/<grower-slug>/derived/dashboards/<grower-slug>_grower_web_map.html
```

It relies on the canonical data-tree shape created by the pipeline:
- `growers/<slug>/grower.json`
- `growers/<slug>/farms/<farm-slug>/farm.json`
- `growers/<slug>/farms/<farm-slug>/boundary/field_boundaries.geojson`

## Local-delta-only reminder

This nested AGENTS.md only records instructions that differ from the parent or root files. Do not duplicate root-wide vendor, asset, or validation policy here except this pointer to `../../../AGENTS.md`.
