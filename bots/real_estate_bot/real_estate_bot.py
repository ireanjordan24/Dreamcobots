"""
Real Estate Bot — tier-aware property search and transaction assistant.

Usage
-----
    from bots.real_estate_bot.real_estate_bot import RealEstateBot
    from bots.ai_chatbot.tiers import Tier

    bot = RealEstateBot(tier=Tier.PRO)
    response = bot.chat("Find 3-bedroom homes under $400,000 in Austin, TX")
    print(response["message"])
"""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py


import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.real_estate_bot.tiers import (
    RE_EXTRA_FEATURES,
    RE_TOOLS,
    get_re_tier_info,
)


class RealEstateTierError(Exception):
    """Raised when a real-estate tool is not available on the current tier."""


class RealEstateRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class RealEstateBot:
    """
    Tier-aware real estate assistant.

    Supported tools (by tier):
      FREE       -- property search, basic market overview, neighborhood info
      PRO        -- investment analysis, rental yield calculator, comps report
      ENTERPRISE -- MLS integration, portfolio management, deal pipeline CRM

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling tool access.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._history: list[dict] = []

    # ------------------------------------------------------------------
    # Core chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, tool: str | None = None) -> dict:
        """
        Process a real-estate query and return a structured response.

        Parameters
        ----------
        message : str
            User's natural-language property or market question.
        tool : str | None
            Optional tool to invoke directly.

        Returns
        -------
        dict with keys: ``message``, ``tool``, ``tier``,
        ``requests_used``, ``requests_remaining``.
        """
        self._check_request_limit()
        active_tool = tool or self._default_tool(message)
        self._check_tool_access(active_tool)

        self._request_count += 1
        response_text = (
            f"[RealEstateBot/{active_tool}] Processed: {message!r}"
        )
        self._history.append({"role": "user", "content": message})
        self._history.append({"role": "assistant", "content": response_text})

        return {
            "message": response_text,
            "tool": active_tool,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def search_properties(self, criteria: dict) -> dict:
        """
        Search properties based on structured criteria.

        Parameters
        ----------
        criteria : dict
            Keys may include: ``location``, ``min_price``, ``max_price``,
            ``bedrooms``, ``property_type``.

        Returns
        -------
        dict with keys: ``status``, ``results``, ``tier``.
        """
        self._check_request_limit()
        self._check_tool_access("property_search")
        self._request_count += 1

        return {
            "status": "success",
            "results": f"[Mock] Properties matching: {criteria}",
            "tier": self.tier.value,
        }

    def list_tools(self) -> list[str]:
        """Return the real-estate tools available on the current tier."""
        return list(RE_TOOLS.get(self.tier.value, []))

    def get_history(self) -> list[dict]:
        """Return a copy of the conversation history."""
        return list(self._history)

    def clear_history(self) -> None:
        """Clear conversation history."""
        self._history = []

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current real-estate tier."""
        info = get_re_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Real Estate Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Real estate features:",
        ]
        for feat in info["re_features"]:
            lines.append(f"  ✓ {feat}")
        lines.append("")
        lines.append("Available tools:")
        for t in info["tools"]:
            lines.append(f"  • {t}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_tier = get_upgrade_path(self.tier)
        if next_tier is None:
            msg = f"You are already on the highest tier ({self.config.name})."
        else:
            msg = (
                f"Upgrade to {next_tier.name} for "
                f"${next_tier.price_usd_monthly:.2f}/month to unlock "
                f"investment analysis and MLS integration."
            )
        print(msg)
        return msg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_tool(self, message: str) -> str:
        available = RE_TOOLS.get(self.tier.value, ["property_search"])
        lower = message.lower()
        if "search" in lower or "find" in lower or "list" in lower:
            return "property_search"
        if "invest" in lower or "yield" in lower or "roi" in lower:
            return "investment_analyzer"
        if "rent" in lower:
            return "rental_yield_calculator"
        if "market" in lower or "trend" in lower:
            return "market_overview"
        if "comp" in lower or "comparable" in lower:
            return "comps_report"
        return available[0] if available else "property_search"

    def _check_tool_access(self, tool: str) -> None:
        allowed = RE_TOOLS.get(self.tier.value, [])
        if tool not in allowed:
            raise RealEstateTierError(
                f"Tool '{tool}' is not available on the "
                f"{self.config.name} tier. Upgrade to access it."
            )

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise RealEstateRequestLimitError(
                f"Monthly request limit of {limit} reached on the "
                f"{self.config.name} tier."
            )

    def _requests_remaining(self) -> int | None:
        limit = self.config.requests_per_month
        if limit is None:
            return None
        return max(0, limit - self._request_count)
