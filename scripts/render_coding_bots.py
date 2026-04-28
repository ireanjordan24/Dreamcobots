#!/usr/bin/env python3
"""
render_coding_bots.py
=====================
Reads ``coding-bots.json`` (repo root) and updates the ``## 🤖 Coding Systems``
section in ``README.md`` between the markers::

    <!-- CODING-BOTS:START -->
    <!-- CODING-BOTS:END -->

Usage
-----
    python scripts/render_coding_bots.py
    python scripts/render_coding_bots.py --registry path/to/coding-bots.json --readme README.md

To add a new coding system/bot:
    1. Edit ``coding-bots.json`` — add an entry to the ``coding_bots`` array.
    2. Run ``python scripts/render_coding_bots.py`` to regenerate README.md.
    3. Commit both files.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
DEFAULT_REGISTRY = REPO_ROOT / "coding-bots.json"
DEFAULT_README = REPO_ROOT / "README.md"

START_MARKER = "<!-- CODING-BOTS:START -->"
END_MARKER = "<!-- CODING-BOTS:END -->"


def load_registry(registry_path: Path) -> list[dict]:
    with registry_path.open(encoding="utf-8") as fh:
        data = json.load(fh)
    return data["coding_bots"]


def render_table(bots: list[dict]) -> str:
    lines: list[str] = [
        "| System | Description | Tags |",
        "|--------|-------------|------|",
    ]
    for bot in bots:
        name = bot["name"]
        url = bot.get("url", "")
        desc = bot.get("description", "")
        tags = ", ".join(f"`{t}`" for t in bot.get("tags", []))
        name_cell = f"[{name}]({url})" if url else name
        lines.append(f"| {name_cell} | {desc} | {tags} |")
    return "\n".join(lines)


def update_readme(readme_path: Path, bots: list[dict], *, dry_run: bool = False) -> bool:
    """
    Replace content between markers in *readme_path*.

    Returns True if the file was changed, False if it was already up-to-date.
    """
    original = readme_path.read_text(encoding="utf-8")

    pattern = re.compile(
        re.escape(START_MARKER) + r".*?" + re.escape(END_MARKER),
        re.DOTALL,
    )

    table = render_table(bots)
    replacement = f"{START_MARKER}\n{table}\n{END_MARKER}"

    if not pattern.search(original):
        print(f"ERROR: markers not found in {readme_path}", file=sys.stderr)
        print(f"  Add the following lines to {readme_path}:")
        print(f"  {START_MARKER}")
        print(f"  {END_MARKER}")
        sys.exit(1)

    updated = pattern.sub(replacement, original)
    if updated == original:
        print("README.md is already up-to-date.")
        return False

    if not dry_run:
        readme_path.write_text(updated, encoding="utf-8")
        print(f"README.md updated with {len(bots)} coding bots.")
    else:
        print("[dry-run] Would write the following replacement:")
        print(replacement)
    return True


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY, help="Path to coding-bots.json")
    parser.add_argument("--readme", type=Path, default=DEFAULT_README, help="Path to README.md")
    parser.add_argument("--dry-run", action="store_true", help="Print the replacement without writing")
    args = parser.parse_args(argv)

    bots = load_registry(args.registry)
    update_readme(args.readme, bots, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
