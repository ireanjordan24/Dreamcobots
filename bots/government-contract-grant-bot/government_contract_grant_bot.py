"""
Government Contract & Grant Bot — tier-aware assistant for finding and applying
for government contracts and grant funding opportunities.

Usage
-----
    from bots.government-contract-grant-bot.government_contract_grant_bot import (
        GovernmentContractGrantBot,
    )
    from bots.ai_chatbot.tiers import Tier

    bot = GovernmentContractGrantBot(tier=Tier.PRO)
    response = bot.chat("Find SBIR grants for AI startups")
    print(response["message"])
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path


# ------------------------------------------------------------------
# Tier configuration
# ------------------------------------------------------------------

GCG_EXTRA_FEATURES: dict[str, list[str]] = {
    Tier.FREE.value: [
        "SAM.gov opportunity search",
        "Grant database browse (federal)",
        "Eligibility pre-check",
        "Basic proposal outline",
    ],
    Tier.PRO.value: [
        "SBIR/STTR grant finder",
        "Contract bid tracker (FPDS-NG data)",
        "Proposal & RFP writer",
        "Compliance checklist (FAR/DFARS)",
        "Deadline alert notifications",
        "Win-rate analytics",
    ],
    Tier.ENTERPRISE.value: [
        "Multi-agency contract pipeline",
        "Teaming partner finder",
        "Set-aside & sole-source optimization",
        "Audit-ready proposal packages",
        "Dedicated government contracts specialist",
        "White-label client portal",
    ],
}

GCG_TOOLS: dict[str, list[str]] = {
    Tier.FREE.value: [
        "opportunity_search",
        "grant_browse",
        "eligibility_checker",
    ],
    Tier.PRO.value: [
        "opportunity_search",
        "grant_browse",
        "eligibility_checker",
        "sbir_grant_finder",
        "contract_bid_tracker",
        "proposal_writer",
        "compliance_checklist",
    ],
    Tier.ENTERPRISE.value: [
        "opportunity_search",
        "grant_browse",
        "eligibility_checker",
        "sbir_grant_finder",
        "contract_bid_tracker",
        "proposal_writer",
        "compliance_checklist",
        "teaming_partner_finder",
        "set_aside_optimizer",
        "audit_package_generator",
        "contract_pipeline_manager",
    ],
}


def get_gcg_tier_info(tier: Tier) -> dict:
    """Return Government Contract & Grant Bot tier information as a dict."""
    cfg = get_tier_config(tier)
    return {
        "tier": tier.value,
        "name": cfg.name,
        "price_usd_monthly": cfg.price_usd_monthly,
        "requests_per_month": cfg.requests_per_month,
        "platform_features": cfg.features,
        "gcg_features": GCG_EXTRA_FEATURES[tier.value],
        "tools": GCG_TOOLS[tier.value],
        "support_level": cfg.support_level,
    }


# ------------------------------------------------------------------
# Bot exceptions
# ------------------------------------------------------------------

class GCGTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class GCGRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


# ------------------------------------------------------------------
# Main bot class
# ------------------------------------------------------------------

class GovernmentContractGrantBot:
    """
    Tier-aware government contract and grant assistant.

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
    # Legacy interface (preserved for backwards compatibility)
    # ------------------------------------------------------------------

    def start(self) -> None:
        print(f"Government Contract & Grant Bot is starting (tier={self.tier.value})...")

    def process_contracts(self) -> None:
        print("Processing contracts...")

    def process_grants(self) -> None:
        print("Processing grants...")

    def run(self) -> None:
        self.start()
        self.process_contracts()
        self.process_grants()

    # ------------------------------------------------------------------
    # Core chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, tool: str | None = None) -> dict:
        """
        Process a government contracting or grant query.

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
            f"[GovContractGrantBot/{active_tool}] Processed: {message!r}"
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

    def search_opportunities(self, keywords: str, agency: str | None = None) -> dict:
        """
        Search government contracting/grant opportunities.

        Returns
        -------
        dict with keys: ``status``, ``opportunities``, ``tier``.
        """
        self._check_request_limit()
        self._check_tool_access("opportunity_search")
        self._request_count += 1

        return {
            "status": "success",
            "opportunities": (
                f"[Mock] Opportunities for '{keywords}' "
                f"from agency '{agency or 'all'}'"
            ),
            "tier": self.tier.value,
        }

    def list_tools(self) -> list[str]:
        """Return the tools available on the current tier."""
        return list(GCG_TOOLS.get(self.tier.value, []))

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
        """Print and return a description of the current tier."""
        info = get_gcg_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Government Contract & Grant Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["gcg_features"]:
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
                f"SBIR/STTR finders and proposal writers."
            )
        print(msg)
        return msg

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _default_tool(self, message: str) -> str:
        available = GCG_TOOLS.get(self.tier.value, ["opportunity_search"])
        lower = message.lower()
        if "sbir" in lower or "sttr" in lower:
            return "sbir_grant_finder"
        if "grant" in lower:
            return "grant_browse"
        if "contract" in lower or "bid" in lower:
            return "contract_bid_tracker"
        if "proposal" in lower or "rfp" in lower:
            return "proposal_writer"
        if "eligib" in lower:
            return "eligibility_checker"
        return available[0] if available else "opportunity_search"

    def _check_tool_access(self, tool: str) -> None:
        allowed = GCG_TOOLS.get(self.tier.value, [])
        if tool not in allowed:
            raise GCGTierError(
                f"Tool '{tool}' is not available on the "
                f"{self.config.name} tier. Upgrade to access it."
            )

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise GCGRequestLimitError(
                f"Monthly request limit of {limit} reached on the "
                f"{self.config.name} tier."
            )

    def _requests_remaining(self) -> int | None:
        limit = self.config.requests_per_month
        if limit is None:
            return None
        return max(0, limit - self._request_count)


# If this module is run directly, start the bot
if __name__ == '__main__':
    bot = GovernmentContractGrantBot()
    bot.run()
