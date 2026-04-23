"""
Adaptive Learning Bot — Continuously updates bot behavior based on outcomes.

Monitors the knowledge base for high-confidence insights and adjusts
internal thresholds (confidence floors, penalty weights) so all bots in
the ecosystem improve over time without manual intervention.

Usage
-----
    python bots/adaptive_learning_bot.py
"""

from __future__ import annotations

import json
import os
import sys
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RANKED_FILE = os.path.join(_ROOT, "knowledge", "ranked_insights.json")
CONFIG_FILE = os.path.join(_ROOT, "knowledge", "adaptive_config.json")

_DEFAULTS: dict = {
    "min_confidence": 2,
    "validator_penalty_high": 15,
    "validator_penalty_medium": 10,
    "debug_min_confidence": 2,
    "buddy_min_confidence": 3,
    "last_updated": "",
}


def _load_ranked() -> list[dict]:
    try:
        with open(RANKED_FILE) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return []


def _load_config() -> dict:
    try:
        with open(CONFIG_FILE) as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return dict(_DEFAULTS)


def _save_config(cfg: dict) -> None:
    os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
    with open(CONFIG_FILE, "w") as fh:
        json.dump(cfg, fh, indent=2)


def adapt(insights: list[dict], config: dict) -> dict:
    """Adjust configuration thresholds based on insight quality.

    Strategy:
    - If there are many high-confidence insights, raise thresholds to be
      more selective (reduce false positives).
    - If the knowledge base is sparse, lower thresholds to catch more.

    Parameters
    ----------
    insights : list[dict]
        Ranked insights from the knowledge store.
    config : dict
        Current adaptive configuration.

    Returns
    -------
    dict
        Updated configuration dictionary.
    """
    total = len(insights)
    high_conf = sum(1 for i in insights if i.get("confidence", 0) >= 4)

    new_cfg = dict(config)

    if total == 0:
        # Empty knowledge base — use permissive defaults
        new_cfg["min_confidence"] = 1
        new_cfg["debug_min_confidence"] = 1
    elif high_conf / max(total, 1) > 0.5:
        # Rich, trustworthy dataset — be selective
        new_cfg["min_confidence"] = min(4, config["min_confidence"] + 1)
        new_cfg["debug_min_confidence"] = min(4, config["debug_min_confidence"] + 1)
        new_cfg["validator_penalty_high"] = min(25, config["validator_penalty_high"] + 2)
    else:
        # Limited high-confidence data — relax thresholds
        new_cfg["min_confidence"] = max(1, config["min_confidence"] - 1)
        new_cfg["debug_min_confidence"] = max(1, config["debug_min_confidence"] - 1)

    new_cfg["last_updated"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    return new_cfg


def run(context: dict | None = None) -> dict:
    """Entry point for the Task Execution Controller."""
    insights = _load_ranked()
    config = _load_config()
    updated = adapt(insights, config)
    _save_config(updated)
    return updated


if __name__ == "__main__":
    insights = _load_ranked()
    config = _load_config()
    updated = adapt(insights, config)
    _save_config(updated)
    print(json.dumps(updated, indent=2))
    print(
        f"\n🧠 Adaptive config updated: min_confidence={updated['min_confidence']}, "
        f"debug_min={updated['debug_min_confidence']}"
    )
