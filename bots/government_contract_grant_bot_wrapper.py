"""
bots/government_contract_grant_bot_wrapper.py

Thin wrapper that builds the default set of bots for the orchestrator.
"""

from typing import Any

from bots.bot_base import BotBase
from bots.government_contract_grant_bot_shim import GovernmentContractGrantBot


def build_default_bots(config: dict[str, Any]) -> list[BotBase]:
    """
    Instantiate and return the default set of DreamCobots bots.

    Args:
        config: Top-level project configuration dict.

    Returns:
        A list of :class:`~bots.bot_base.BotBase` instances ready to be
        registered with the orchestrator.
    """
    query: str = config.get("gov_search_query", "technology services")
    poll_interval: int = int(config.get("gov_poll_interval_seconds", 300))

    gov_bot = GovernmentContractGrantBot(
        bot_id="gov-contract-grant-bot-001",
        search_query=query,
        poll_interval_seconds=poll_interval,
    )
    return [gov_bot]
