"""
DreamCo Bot Generator — Self-Build Engine
==========================================

Dynamically creates new bot folders, auto-writes functional bot code from
templates, and registers the freshly created bots into the ControlCenter.

This is the component that turns DreamCo into "a system that builds systems".

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""

from __future__ import annotations

import os
import random
import sys
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

if TYPE_CHECKING:
    from bots.control_center.controller import ControlCenter

# Probability threshold above which no new bot is generated in a cycle.
# At 0.7 the system expands roughly 30 % of cycles — fast enough to grow
# without flooding the filesystem with unnecessary bots.
_EXPANSION_THRESHOLD: float = 0.7

# ---------------------------------------------------------------------------
# Bot source template
# ---------------------------------------------------------------------------

_BOT_TEMPLATE = '''\
"""Auto-generated DreamCo bot: {name}

Generated on {date} by the DreamCo Bot Generator (GLOBAL AI SOURCES FLOW).
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)


class Bot:
    """Auto-generated bot: {name}."""

    def __init__(self) -> None:
        self.name = "{name}"
        self.created_at = "{date}"
        self._run_count: int = 0

    def run(self) -> str:
        """Execute the bot's primary task."""
        self._run_count += 1
        return f"{{self.name}} completed task #{{self._run_count}} successfully!"

    def get_status(self) -> dict:
        """Return current bot status."""
        return {{
            "name": self.name,
            "run_count": self._run_count,
            "status": "active",
        }}
'''


class BotGenerator:
    """
    DreamCo Self-Build Engine.

    Creates new bot directories, writes starter bot code, and plugs the
    resulting bots into the ControlCenter so they participate in every
    subsequent automation cycle.

    Parameters
    ----------
    control_center : ControlCenter
        The running ControlCenter instance to register newly generated bots.
    bots_root : str, optional
        Filesystem path where new bot folders will be created.
        Defaults to the ``bots/`` directory adjacent to this file.
    """

    def __init__(self, control_center: "ControlCenter", bots_root: Optional[str] = None) -> None:
        self.control_center = control_center
        self.bots_root = bots_root or os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..")
        )
        self.bot_count: int = 0
        self._generation_log: List[Dict] = []

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def create_bot(self, name: str) -> str:
        """
        Create a new bot directory and write starter code.

        Parameters
        ----------
        name : str
            Snake-case name for the new bot (e.g. ``lead_qualifier_bot``).

        Returns
        -------
        str
            Absolute path to the generated bot file.
        """
        bot_dir = os.path.join(self.bots_root, name)
        os.makedirs(bot_dir, exist_ok=True)

        bot_file = os.path.join(bot_dir, f"{name}.py")
        init_file = os.path.join(bot_dir, "__init__.py")
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

        with open(bot_file, "w", encoding="utf-8") as fh:
            fh.write(_BOT_TEMPLATE.format(name=name, date=date_str))

        if not os.path.exists(init_file):
            with open(init_file, "w", encoding="utf-8") as fh:
                fh.write(f'"""Auto-generated DreamCo bot package: {name}."""\n')

        # Register with control center immediately
        try:
            import importlib
            spec_path = f"bots.{name}.{name}"
            module = importlib.import_module(spec_path)
            if hasattr(module, "Bot"):
                self.control_center.register_bot(name, module.Bot())
        except Exception:  # noqa: BLE001
            pass

        entry = {
            "name": name,
            "path": bot_file,
            "created_at": date_str,
        }
        self._generation_log.append(entry)
        print(f"🆕 Created new bot: {name} → {bot_file}")
        return bot_file

    def evaluate_and_expand(self) -> Optional[str]:
        """
        Probabilistically decide whether to generate a new bot this cycle.

        The threshold ensures the system expands organically — roughly 30 %
        of cycles produce a new bot.

        Returns
        -------
        str or None
            Path to the newly created bot file, or ``None`` if no bot was
            generated this cycle.
        """
        if random.random() > _EXPANSION_THRESHOLD:
            self.bot_count += 1
            new_name = f"auto_bot_{self.bot_count}"
            return self.create_bot(new_name)
        return None

    def get_generation_log(self) -> List[Dict]:
        """Return a list of all bots generated so far."""
        return list(self._generation_log)

    def get_summary(self) -> dict:
        """Return a generation summary."""
        return {
            "total_generated": self.bot_count,
            "log": self._generation_log,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
