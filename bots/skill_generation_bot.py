"""
Skill Generation Bot — Dynamically generates new bot skill templates.

Analyzes existing bot patterns, identifies missing capability gaps, and
scaffolds new bot modules using a template engine so the bot factory never
has to start from scratch.

Usage
-----
    python bots/skill_generation_bot.py [<skill_name>]
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_BOTS_DIR = os.path.join(_ROOT, "bots")
_DOCS_DIR = os.path.join(_ROOT, "docs", "bots")

_SKILL_TEMPLATE = '''\
"""
{skill_name_title} — Auto-generated skill module.

TODO: Implement the core skill logic below.
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def run(context: dict | None = None) -> dict:
    """Execute the {skill_name} skill.

    Parameters
    ----------
    context : dict | None
        Optional runtime context passed by the execution controller.

    Returns
    -------
    dict
        Keys: status, output, skill_name.
    """
    context = context or {{}}
    return {{
        "skill_name": "{skill_name}",
        "status": "ok",
        "output": "Skill ran successfully (stub — implement me).",
        "context": context,
    }}


if __name__ == "__main__":
    print(run())
'''

_DOC_TEMPLATE = """\
# {skill_name_title}

## Overview
Auto-generated skill module. Implements the `{skill_name}` capability.

## What It Does
- TODO: describe the skill's primary function

## Features
- Accepts a `context` dict for runtime parameters
- Returns structured `status` / `output` response

## Benefits
- Rapid prototyping of new capabilities
- Consistent interface with the rest of the bot ecosystem

## Example Use Case
```python
from bots.{skill_name} import run
result = run({{"key": "value"}})
print(result)
```

## Future Enhancements
- Replace stub logic with real implementation
- Add unit tests in `tests/test_{skill_name}.py`
"""


def list_existing_skills() -> list[str]:
    """Return names of existing bot script files."""
    try:
        return [
            f[:-3]
            for f in os.listdir(_BOTS_DIR)
            if f.endswith(".py") and not f.startswith("_")
        ]
    except OSError:
        return []


def generate_skill(skill_name: str) -> dict:
    """Scaffold a new skill file and its documentation page.

    Parameters
    ----------
    skill_name : str
        Snake-case name for the new skill (e.g. ``weather_bot``).

    Returns
    -------
    dict
        Keys: skill_path, doc_path, status.
    """
    skill_name = skill_name.lower().replace(" ", "_").replace("-", "_")
    skill_name_title = skill_name.replace("_", " ").title()

    skill_path = os.path.join(_BOTS_DIR, f"{skill_name}.py")
    doc_path = os.path.join(_DOCS_DIR, f"{skill_name}.md")

    results: dict = {"skill_name": skill_name, "skill_path": skill_path, "doc_path": doc_path}

    if os.path.exists(skill_path):
        results["status"] = "already_exists"
        results["message"] = f"Skill {skill_name} already exists — skipping."
        return results

    # Create skill file
    code = _SKILL_TEMPLATE.format(skill_name=skill_name, skill_name_title=skill_name_title)
    with open(skill_path, "w") as fh:
        fh.write(code)

    # Create doc file
    os.makedirs(_DOCS_DIR, exist_ok=True)
    doc = _DOC_TEMPLATE.format(skill_name=skill_name, skill_name_title=skill_name_title)
    with open(doc_path, "w") as fh:
        fh.write(doc)

    results["status"] = "created"
    return results


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    if "skill_name" in context:
        return generate_skill(context["skill_name"])
    skills = list_existing_skills()
    return {"existing_skills": skills, "count": len(skills), "status": "ok"}


if __name__ == "__main__":
    if len(sys.argv) > 1:
        skill_name = sys.argv[1]
    else:
        print("Existing skills:", list_existing_skills())
        sys.exit(0)

    result = generate_skill(skill_name)
    print(json.dumps(result, indent=2))
