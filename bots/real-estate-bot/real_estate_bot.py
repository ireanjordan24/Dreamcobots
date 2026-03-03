"""
bots/real-estate-bot/real_estate_bot.py

RealEstateBot — property search, analysis, mortgage calculation, and market trends.
"""

from __future__ import annotations

import math
import random
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase


class RealEstateBot(BotBase):
    """
    Assists with real estate research, mortgage calculations, and market analysis.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="RealEstateBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("RealEstateBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("RealEstateBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def search_properties(
        self, location: str, budget: float
    ) -> list[dict[str, Any]]:
        """
        Simulate property search results.

        Args:
            location: City or zip code.
            budget: Maximum purchase price.

        Returns:
            List of property listing dicts.
        """
        listings = []
        base_price = budget * random.uniform(0.75, 0.98)
        for i in range(1, 4):
            price = round(base_price * random.uniform(0.9, 1.0) / i, -3)
            listings.append({
                "id": f"PROP-{uuid.uuid4().hex[:8].upper()}",
                "address": f"{100 * i} Main St, {location}",
                "price": price,
                "bedrooms": random.randint(2, 5),
                "bathrooms": random.randint(1, 3),
                "sqft": random.randint(900, 3500),
                "year_built": random.randint(1980, 2023),
                "listing_type": random.choice(["For Sale", "New Construction"]),
            })
        self.log_activity(f"Property search: location='{location}', budget=${budget}.")
        return listings

    def analyze_property(self, address: str) -> dict[str, Any]:
        """
        Produce a simulated property analysis.

        Args:
            address: Property address string.

        Returns:
            Dict with estimated value, cap rate, rent estimate, and scores.
        """
        estimated_value = random.randint(200_000, 800_000)
        monthly_rent = round(estimated_value * 0.007, 0)
        annual_noi = monthly_rent * 12 * 0.65  # assume 35% expenses
        cap_rate = round(annual_noi / estimated_value * 100, 2)

        self.log_activity(f"Property analysed: '{address}'.")
        return {
            "address": address,
            "estimated_value": estimated_value,
            "estimated_monthly_rent": monthly_rent,
            "annual_noi": round(annual_noi, 2),
            "cap_rate_pct": cap_rate,
            "walk_score": random.randint(40, 99),
            "school_rating": f"{random.randint(5, 10)}/10",
            "flood_zone": random.choice(["None", "Zone X", "Zone AE"]),
            "days_on_market": random.randint(5, 90),
        }

    def calculate_mortgage(
        self,
        price: float,
        down_payment: float,
        rate: float,
        years: int,
    ) -> dict[str, Any]:
        """
        Calculate mortgage payment details.

        Args:
            price: Property purchase price.
            down_payment: Down payment amount.
            rate: Annual interest rate as a decimal (e.g. 0.065 for 6.5%).
            years: Loan term in years.

        Returns:
            Dict with monthly payment, total payment, total interest, and LTV.
        """
        if price <= 0 or years <= 0:
            raise ValueError("price and years must be positive.")
        loan_amount = price - down_payment
        if loan_amount <= 0:
            return {
                "loan_amount": 0.0, "monthly_payment": 0.0,
                "total_payment": 0.0, "total_interest": 0.0, "ltv_pct": 0.0,
            }
        monthly_rate = rate / 12
        n = years * 12
        if monthly_rate == 0:
            monthly_payment = loan_amount / n
        else:
            monthly_payment = loan_amount * (monthly_rate * math.pow(1 + monthly_rate, n)) / (math.pow(1 + monthly_rate, n) - 1)

        total_payment = monthly_payment * n
        total_interest = total_payment - loan_amount
        ltv = round(loan_amount / price * 100, 2)

        self.log_activity(f"Mortgage calculated: price=${price}, rate={rate*100:.2f}%, {years}yr.")
        return {
            "loan_amount": round(loan_amount, 2),
            "monthly_payment": round(monthly_payment, 2),
            "total_payment": round(total_payment, 2),
            "total_interest": round(total_interest, 2),
            "ltv_pct": ltv,
            "down_payment": round(down_payment, 2),
        }

    def get_market_trends(self, location: str) -> dict[str, Any]:
        """
        Return simulated real estate market trend data for *location*.

        Args:
            location: City or region.

        Returns:
            Market trends dict with median price, YoY change, and inventory.
        """
        median_price = random.randint(250_000, 900_000)
        yoy_change = round(random.uniform(-5.0, 15.0), 1)
        self.log_activity(f"Market trends retrieved for '{location}'.")
        return {
            "location": location,
            "median_home_price": median_price,
            "yoy_price_change_pct": yoy_change,
            "months_of_supply": round(random.uniform(1.0, 6.0), 1),
            "avg_days_on_market": random.randint(15, 90),
            "market_type": "Seller's Market" if yoy_change > 5 else ("Buyer's Market" if yoy_change < 0 else "Balanced"),
            "foreclosure_rate": f"{random.uniform(0.1, 2.0):.2f}%",
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }
