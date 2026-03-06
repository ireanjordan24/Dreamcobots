"""
bots/ecommerce-bot/ecommerce_bot.py

EcommerceBot — product search, competition analysis, listing generation, and profit calculation.
"""

from __future__ import annotations

import random
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_PLATFORM_FEES: dict[str, float] = {
    "amazon": 0.15,
    "ebay": 0.13,
    "etsy": 0.065,
    "shopify": 0.02,
    "walmart": 0.15,
}


class EcommerceBot(BotBase):
    """
    E-commerce assistant for product research, competition analysis, and profitability.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="EcommerceBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("EcommerceBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("EcommerceBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def search_products(self, query: str, platform: str) -> list[dict[str, Any]]:
        """
        Simulate product search results on *platform*.

        Args:
            query: Search query.
            platform: Marketplace platform name.

        Returns:
            List of product result dicts.
        """
        fee_rate = _PLATFORM_FEES.get(platform.lower(), 0.15)
        products = []
        for i in range(1, 6):
            price = round(random.uniform(5.0, 200.0), 2)
            products.append({
                "rank": i,
                "title": f"{query.title()} — Model {chr(64 + i)}",
                "price": price,
                "rating": round(random.uniform(3.5, 5.0), 1),
                "reviews": random.randint(10, 5000),
                "platform": platform,
                "platform_fee_pct": fee_rate * 100,
                "asin": uuid.uuid4().hex[:10].upper(),
            })
        self.log_activity(f"Product search: query='{query}', platform='{platform}'.")
        return products

    def analyze_competition(self, niche: str) -> dict[str, Any]:
        """
        Analyse the competitive landscape for *niche*.

        Args:
            niche: Product niche or category.

        Returns:
            Competition analysis dict.
        """
        competition_score = random.randint(1, 10)
        self.log_activity(f"Competition analysed for niche='{niche}'.")
        return {
            "niche": niche,
            "competition_score": competition_score,
            "competition_level": (
                "Low" if competition_score <= 3
                else "Medium" if competition_score <= 6
                else "High"
            ),
            "top_sellers": random.randint(50, 500),
            "avg_price": round(random.uniform(10.0, 150.0), 2),
            "avg_reviews": random.randint(100, 2000),
            "market_opportunity": "Good" if competition_score < 5 else "Moderate" if competition_score < 8 else "Saturated",
            "keywords": [f"{niche} buy", f"best {niche}", f"{niche} cheap", f"{niche} review"],
        }

    def generate_product_listing(self, product: dict[str, Any]) -> dict[str, Any]:
        """
        Generate an optimised product listing from *product* details.

        Args:
            product: Dict with ``name``, ``features`` (list), ``price``,
                     ``category``.

        Returns:
            Optimised listing dict ready for marketplace submission.
        """
        name = product.get("name", "Product")
        features = product.get("features", [])
        price = product.get("price", 0.0)
        category = product.get("category", "General")

        bullet_points = [f"✓ {f}" for f in features[:5]] if features else ["✓ High quality", "✓ Fast shipping"]
        self.log_activity(f"Product listing generated for '{name}'.")
        return {
            "title": f"{name} — Premium Quality | {category}",
            "bullet_points": bullet_points,
            "description": (
                f"Introducing the {name}, the ultimate solution for your {category.lower()} needs. "
                f"{'Features include: ' + ', '.join(features) + '.' if features else ''} "
                f"Order now and experience the difference!"
            ),
            "search_terms": [name.lower(), category.lower(), f"buy {name.lower()}", f"best {category.lower()}"],
            "suggested_price": price,
            "category": category,
        }

    def calculate_profit_margin(
        self, cost: float, price: float, fees: float
    ) -> float:
        """
        Calculate net profit margin.

        Args:
            cost: Product cost (COGS).
            price: Selling price.
            fees: Total platform / shipping fees.

        Returns:
            Net profit margin as a percentage (0-100).
        """
        if price <= 0:
            raise ValueError("price must be positive.")
        net_profit = price - cost - fees
        margin = round(net_profit / price * 100, 2)
        self.log_activity(f"Profit margin: {margin}%.")
        return margin
