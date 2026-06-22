#!/usr/bin/env python3
# pyright: reportMissingImports=false, reportAttributeAccessIssue=false, reportGeneralTypeIssues=false
"""CLI entrypoint to generate a grower-level interactive web map."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

_LOCAL_LIB = Path(__file__).resolve().parents[1] / "lib"
sys.path.insert(0, str(_LOCAL_LIB))

from runtime_paths import resolve_runtime_paths  # noqa: E402

_RUNTIME_PATHS = resolve_runtime_paths()
_REPO = _RUNTIME_PATHS.runtime_base
_SCRIPTS = _RUNTIME_PATHS.runtime_scripts
_LIB = _RUNTIME_PATHS.runtime_scripts / "lib"
sys.path.insert(0, str(_SCRIPTS))
sys.path.insert(0, str(_LIB))

from reporting_bootstrap import ensure_skill_path  # noqa: E402


_GROWER_WEB_MAP_SKILL = ensure_skill_path("grower-web-map")

from grower_web_map import generate_grower_web_map  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate an interactive web map for a grower."
    )
    parser.add_argument(
        "--grower-slug",
        required=True,
        help="Canonical grower slug (e.g. iowa-grower).",
    )
    parser.add_argument(
        "--output-dir",
        default="",
        help="Optional override for the output directory. Defaults to growers/<slug>/derived/dashboards/.",
    )
    args = parser.parse_args()

    data_root = _REPO
    output_dir = Path(args.output_dir) if args.output_dir else None

    try:
        out_path = generate_grower_web_map(
            grower_slug=args.grower_slug,
            data_root=data_root,
            output_dir=output_dir,
        )
        print(f"✓ Created: {out_path}")
        print(f"Open this file in any web browser.")
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
