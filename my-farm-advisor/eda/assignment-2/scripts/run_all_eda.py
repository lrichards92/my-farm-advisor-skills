#!/usr/bin/env python3
"""
Assignment 2: Master EDA runner
Executes all EDA scripts and generates outputs.
"""

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).parent
OUTPUTS_DIR = SCRIPTS_DIR.parent / "outputs"
OUTPUTS_DIR.mkdir(exist_ok=True)

scripts = [
    "01_field_boundaries.py",
    "02_weather.py",
    "03_cdl.py",
    "04_geospatial_map.py",
]

print("=" * 70)
print("ASSIGNMENT 2: FIELD-LEVEL EDA")
print("=" * 70)
print(f"Output directory: {OUTPUTS_DIR}")
print()

for script in scripts:
    script_path = SCRIPTS_DIR / script
    print(f"\n{'='*70}")
    print(f"Running: {script}")
    print(f"{'='*70}")
    result = subprocess.run([sys.executable, str(script_path)], capture_output=False)
    if result.returncode != 0:
        print(f"WARNING: {script} exited with code {result.returncode}")
    else:
        print(f"✅ {script} completed successfully")

print(f"\n{'='*70}")
print("ALL EDA SCRIPTS COMPLETE")
print(f"{'='*70}")
print(f"\nGenerated outputs in: {OUTPUTS_DIR}")
for f in sorted(OUTPUTS_DIR.glob("*.png")):
    print(f"  📊 {f.name}")
for f in sorted(OUTPUTS_DIR.glob("*.csv")):
    print(f"  📄 {f.name}")
