"""
Feature 3: Real estate bot for market analysis.
Functionality: Analyzes market trends and provides insights.
Use Cases: Investors making data-driven decisions.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from industry.real_estate import RealEstateAI
from core.bot_base import AutonomyLevel, ScalingLevel


class MarketAnalysisBot(RealEstateAI):
    """Analyses real estate market trends and produces investor insights."""

    def __init__(self) -> None:
        super().__init__(AutonomyLevel.FULLY_AUTONOMOUS, ScalingLevel.AGGRESSIVE)
        self.name = "MarketAnalysisBot"

    def investor_brief(self, city: str) -> str:
        """Generate a plain-text investor market brief for *city*."""
        trends = self.analyze_market_trends(city)
        if trends.get("trend") == "no data":
            return f"No market data available for {city}."

        lines = [
            f"=== Market Brief: {city} ===",
            f"Data points : {trends['data_points']}",
            f"Average price: ${trends['avg_price']:,.2f}",
            f"Price range  : ${trends['min_price']:,.2f} – ${trends['max_price']:,.2f}",
            f"Total volume : {trends['total_volume']} transactions",
            f"Trend        : {trends['trend'].upper()}",
        ]
        return "\n".join(lines)

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "investor_brief":
            brief = self.investor_brief(task.get("city", ""))
            return {"status": "ok", "brief": brief}
        return super()._run_task(task)


if __name__ == "__main__":
    bot = MarketAnalysisBot()
    bot.start()
    bot.record_market_data("Austin", 420000, 150, "2026-01")
    bot.record_market_data("Austin", 435000, 162, "2026-02")
    bot.record_market_data("Austin", 450000, 175, "2026-03")
    print(bot.investor_brief("Austin"))
    bot.stop()