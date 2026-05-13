"""
DreamCo Lite — simplified DreamCo platform.

Exposes the two core bots used by the Lite UI:
  - MoneyBot  : lead generation + outreach message creation
  - DebugBot  : log/error analysis with plain-English explanations and fix suggestions
"""

from dreamco_lite.money_bot import MoneyBot
from dreamco_lite.debug_bot import DebugBot

__all__ = ["MoneyBot", "DebugBot"]
