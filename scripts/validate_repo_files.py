#!/usr/bin/env python3
"""
validate_repo_files.py
======================
Checks that every path listed in ``repo-required-files.yml`` exists.
Exits with status 0 if all files/dirs are present, or 1 (with a clear list
of missing paths) if any are absent.

Usage
-----
    python scripts/validate_repo_files.py
    python scripts/validate_repo_files.py --manifest repo-required-files.yml --root .

Wire this into CI as the first substantive step so failures are immediately
actionable rather than surfacing as cryptic import errors later.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

try:
    import yaml  # type: ignore[import]
    _YAML_AVAILABLE = True
except ImportError:
    _YAML_AVAILABLE = False

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "repo-required-files.yml"


def _load_manifest(manifest_path: Path) -> dict:
    """Load YAML manifest; fall back to a minimal line-based parser if PyYAML is absent."""
    text = manifest_path.read_text(encoding="utf-8")
    if _YAML_AVAILABLE:
        return yaml.safe_load(text) or {}

    # Minimal fallback: parse YAML list items manually (no PyYAML dependency required in CI)
    result: dict = {"required_files": [], "required_dirs": []}
    current_key: str | None = None
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line in ("required_files:", "required_dirs:"):
            current_key = line.rstrip(":")
        elif line.startswith("- ") and current_key:
            result[current_key].append(line[2:].strip())
    return result


def validate(manifest_path: Path, root: Path) -> list[str]:
    """Return a list of missing paths (relative to *root*)."""
    data = _load_manifest(manifest_path)
    missing: list[str] = []

    for rel in data.get("required_files", []):
        if not (root / rel).is_file():
            missing.append(rel)

    for rel in data.get("required_dirs", []):
        if not (root / rel).is_dir():
            missing.append(rel + "/")

    return missing


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help="Path to the required-files YAML manifest (default: repo-required-files.yml)",
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=REPO_ROOT,
        help="Repository root to check paths against (default: repo root)",
    )
    args = parser.parse_args(argv)

    print(f"Validating required files against: {args.manifest}")
    missing = validate(args.manifest, args.root)

    if missing:
        print(f"\n❌ {len(missing)} required path(s) are MISSING:\n")
        for path in missing:
            print(f"   MISSING: {path}")
        print(
            "\nFix: add the missing files/directories listed above, or update"
            " repo-required-files.yml if the path was intentionally removed.\n"
        )
        return 1

    print(f"✅ All required files and directories are present.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
