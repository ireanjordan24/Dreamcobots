#!/usr/bin/env python3
"""
Dependency Intelligence Gate for Dreamcobots.

Ensures every declared dependency has strategic requirements that align to
category-dominance goals for both current and future dependencies.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = ROOT / ".github" / "dependency_intelligence_requirements.json"

PACKAGE_MANIFESTS = [
    ROOT / "package.json",
    ROOT / "DreamCo" / "package.json",
    ROOT / "dreamco" / "package.json",
    ROOT / "dreamco-control-tower" / "package.json",
    ROOT / "dreamco-control-tower" / "frontend" / "package.json",
    ROOT / "dreamco-control-tower" / "backend" / "package.json",
    ROOT / "stripe" / "node" / "package.json",
]

REQUIREMENTS_MANIFESTS = sorted(
    p
    for p in ROOT.glob("**/requirements*.txt")
    if "node_modules" not in str(p) and ".venv" not in str(p)
)

REQ_NAME_RE = re.compile(r"^\s*([A-Za-z0-9_.-]+)")

REQUIRED_FIELDS = ("value_hypothesis", "strategic_requirements", "target_categories", "kpis")


def parse_package_json(path: Path) -> set[str]:
    if not path.is_file():
        return set()
    data = json.loads(path.read_text(encoding="utf-8"))
    deps = set((data.get("dependencies") or {}).keys())
    deps.update((data.get("devDependencies") or {}).keys())
    return {d.strip() for d in deps if d.strip()}


def parse_requirements(path: Path) -> set[str]:
    deps: set[str] = set()
    if not path.is_file():
        return deps
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or line.startswith("-r ") or line.startswith("--"):
            continue
        match = REQ_NAME_RE.match(line)
        if match:
            deps.add(match.group(1))
    return deps


def collect_declared_dependencies() -> dict[str, set[str]]:
    dependency_to_manifests: dict[str, set[str]] = {}
    for manifest in PACKAGE_MANIFESTS:
        rel = str(manifest.relative_to(ROOT))
        for dep in parse_package_json(manifest):
            dependency_to_manifests.setdefault(dep, set()).add(rel)

    for manifest in REQUIREMENTS_MANIFESTS:
        rel = str(manifest.relative_to(ROOT))
        for dep in parse_requirements(manifest):
            dependency_to_manifests.setdefault(dep, set()).add(rel)

    return dependency_to_manifests


def validate_entry(dep: str, entry: dict, allowed_categories: set[str]) -> list[str]:
    errors: list[str] = []
    for field in REQUIRED_FIELDS:
        if field not in entry:
            errors.append(f"{dep}: missing required field '{field}'")

    if not isinstance(entry.get("value_hypothesis"), str) or not entry["value_hypothesis"].strip():
        errors.append(f"{dep}: value_hypothesis must be a non-empty string")

    strategic_requirements = entry.get("strategic_requirements")
    if not isinstance(strategic_requirements, list) or not strategic_requirements:
        errors.append(f"{dep}: strategic_requirements must be a non-empty list")
    elif not all(isinstance(item, str) and item.strip() for item in strategic_requirements):
        errors.append(f"{dep}: strategic_requirements entries must be non-empty strings")

    target_categories = entry.get("target_categories")
    if not isinstance(target_categories, list) or not target_categories:
        errors.append(f"{dep}: target_categories must be a non-empty list")
    else:
        invalid = [c for c in target_categories if c not in allowed_categories]
        if invalid:
            errors.append(f"{dep}: invalid target_categories {invalid}; allowed={sorted(allowed_categories)}")

    kpis = entry.get("kpis")
    if not isinstance(kpis, list) or not kpis:
        errors.append(f"{dep}: kpis must be a non-empty list")
    elif not all(isinstance(item, str) and item.strip() for item in kpis):
        errors.append(f"{dep}: kpis entries must be non-empty strings")

    return errors


def main() -> int:
    if not CATALOG_PATH.is_file():
        print(f"Dependency intelligence check failed: catalog file missing: {CATALOG_PATH}")
        return 1

    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    allowed_categories = set(catalog.get("allowed_categories") or [])
    entries = catalog.get("dependencies") or {}
    if not isinstance(entries, dict):
        print("Dependency intelligence check failed: 'dependencies' must be an object")
        return 1

    declared = collect_declared_dependencies()
    declared_names = set(declared.keys())
    catalog_names = set(entries.keys())

    missing = sorted(declared_names - catalog_names)
    stale = sorted(catalog_names - declared_names)

    errors: list[str] = []
    for dep in sorted(declared_names & catalog_names):
        errors.extend(validate_entry(dep, entries[dep], allowed_categories))

    print("Dependency intelligence check summary")
    print(f"- Declared dependencies: {len(declared_names)}")
    print(f"- Catalog entries: {len(catalog_names)}")
    print(f"- Missing catalog coverage: {len(missing)}")
    print(f"- Stale catalog entries: {len(stale)}")

    if missing:
        print("\nMissing dependency intelligence entries:")
        for dep in missing:
            manifests = ", ".join(sorted(declared[dep]))
            print(f"- {dep} (declared in: {manifests})")
        errors.append("Missing dependency intelligence entries detected.")

    if stale:
        print("\nStale dependency intelligence entries (not currently declared):")
        for dep in stale:
            print(f"- {dep}")

    if errors:
        print("\nDependency intelligence check result: FAIL")
        for err in errors:
            print(f"- {err}")
        return 1

    print("\nDependency intelligence check result: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
