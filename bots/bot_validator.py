"""
Bot Validator — Code quality gating using ranked PR insights.

Scans a code snippet (or file) for patterns that have historically caused
issues (as recorded in ranked_insights.json) and returns a score with
warnings.

Usage
-----
    python bots/bot_validator.py [<path_to_file>]
    echo "some code" | python bots/bot_validator.py -
"""

from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

KNOWLEDGE_FILE = os.path.join(
    os.path.dirname(__file__), "..", "knowledge", "ranked_insights.json"
)

_PASSING_THRESHOLD = 60


def load_insights() -> list[dict]:
    """Load ranked insights, returning empty list on failure."""
    try:
        with open(KNOWLEDGE_FILE, "r") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []


def validate_code(code: str) -> dict:
    """Validate *code* against known bad patterns from the insight store.

    Parameters
    ----------
    code : str
        The source code (or any text) to validate.

    Returns
    -------
    dict
        Keys: score (int 0-100), warnings (list[str]), status ("pass"|"review").
    """
    insights = load_insights()
    warnings: list[str] = []
    score = 100
    code_lower = code.lower()

    for item in insights:
        confidence = item.get("confidence", 0)
        if item.get("type") != "bug_fix":
            continue
        title = item.get("title", "").lower()
        if title and title in code_lower:
            penalty = 15 if confidence >= 3 else 10
            warnings.append(f"Pattern risk ({confidence}✶): {item.get('title', '')}")
            score = max(0, score - penalty)

    return {
        "score": score,
        "warnings": warnings,
        "status": "pass" if score > _PASSING_THRESHOLD else "review",
    }


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    context = context or {}
    code = context.get("code", "")
    if not code:
        code = context.get("file", "")
        if code and os.path.isfile(code):
            try:
                with open(code) as fh:
                    code = fh.read()
            except OSError:
                code = ""
    return validate_code(code)


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "-":
        code = sys.stdin.read()
    elif len(sys.argv) > 1:
        path = sys.argv[1]
        try:
            with open(path) as fh:
                code = fh.read()
        except OSError as exc:
            print(f"Error reading {path}: {exc}", file=sys.stderr)
            sys.exit(1)
    else:
        code = "fix ci workflow"

    result = validate_code(code)
    print(json.dumps(result, indent=2))
    if result["status"] != "pass":
        sys.exit(1)
