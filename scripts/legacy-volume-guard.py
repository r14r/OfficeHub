#!/usr/bin/env python3
"""Block unsafe upgrades when old host-mounted app data has not been reviewed.

This preflight does not copy, modify, or delete host data or Docker volumes.
"""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parent.parent
MAPPING = ROOT / "scripts" / "legacy-volume-map.json"
LEGACY_DATA_ROOT = ROOT.parent / "data"
ACK_ENV = "OFFICEHUB_LEGACY_DATA_ACK"


def legacy_entries(profile: str | None = None) -> list[dict]:
    all_entries = json.loads(MAPPING.read_text(encoding="utf-8"))["entries"]
    return [item for item in all_entries if profile is None or item["profile"] == profile]


def populated_paths(entries: list[dict], data_root: Path) -> list[tuple[dict, Path]]:
    """Fail closed if a legacy directory is a symlink or cannot be inspected."""
    populated = []
    for entry in entries:
        path = data_root / entry["legacy"]
        try:
            if path.is_symlink() or path.is_file() or (
                path.is_dir() and any(path.iterdir())
            ):
                populated.append((entry, path))
        except OSError:
            populated.append((entry, path))
    return populated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--all", action="store_true")
    target.add_argument("--profile")
    args = parser.parse_args()
    entries = legacy_entries(None if args.all else args.profile)
    existing = populated_paths(entries, LEGACY_DATA_ROOT)
    if not existing:
        print("Legacy data check: no populated previous app directories")
        return 0

    print("Old host bind-mount data found:", file=sys.stderr)
    for entry, path in existing:
        dest = entry.get("volume") or entry.get("target")
        print(f"  {path} -> {dest}", file=sys.stderr)
    print(
        "\nSTOP: New named volumes are empty until migrated. "
        "Back up and move existing data before starting. "
        "See docs/application-volume-migration.md.",
        file=sys.stderr,
    )
    if os.environ.get(ACK_ENV) == "1":
        print(f"{ACK_ENV}=1: migration warning explicitly acknowledged.", file=sys.stderr)
        return 0
    print(
        f"After verifying backup/migration, set {ACK_ENV}=1 for the start command.",
        file=sys.stderr,
    )
    return 3


if __name__ == "__main__":
    raise SystemExit(main())
