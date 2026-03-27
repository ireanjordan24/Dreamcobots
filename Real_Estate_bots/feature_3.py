"""
Feature 3: Real estate market analysis.

Analyzes market trends, price indices, and investment signals across
major metro areas. Provides actionable insights for investors and agents.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))


class MarketAnalyzer:
    """Analyzes real estate market trends and surfaces investment signals."""

    MARKET_DATA = {
        "austin": {
            "avg_price_change_pct_yoy": 6.2, "inventory_months": 2.1,
            "days_on_market": 18, "price_per_sqft": 285,
            "avg_home_price": 485000, "rent_growth_pct_yoy": 4.5,
            "vacancy_rate_pct": 4.2, "population_growth_pct": 2.8,
        },
        "phoenix": {
            "avg_price_change_pct_yoy": 4.8, "inventory_months": 2.8,
            "days_on_market": 22, "price_per_sqft": 210,
            "avg_home_price": 375000, "rent_growth_pct_yoy": 3.8,
            "vacancy_rate_pct": 5.1, "population_growth_pct": 2.1,
        },
        "nashville": {
            "avg_price_change_pct_yoy": 5.5, "inventory_months": 1.9,
            "days_on_market": 15, "price_per_sqft": 260,
            "avg_home_price": 430000, "rent_growth_pct_yoy": 4.2,
            "vacancy_rate_pct": 3.9, "population_growth_pct": 2.5,
        },
        "denver": {
            "avg_price_change_pct_yoy": 3.2, "inventory_months": 3.1,
            "days_on_market": 28, "price_per_sqft": 295,
            "avg_home_price": 560000, "rent_growth_pct_yoy": 2.9,
            "vacancy_rate_pct": 5.8, "population_growth_pct": 1.4,
        },
        "tampa": {
            "avg_price_change_pct_yoy": 7.1, "inventory_months": 2.5,
            "days_on_market": 20, "price_per_sqft": 230,
            "avg_home_price": 410000, "rent_growth_pct_yoy": 5.1,
            "vacancy_rate_pct": 4.6, "population_growth_pct": 3.1,
        },
        "charlotte": {
            "avg_price_change_pct_yoy": 5.9, "inventory_months": 2.2,
            "days_on_market": 17, "price_per_sqft": 218,
            "avg_home_price": 380000, "rent_growth_pct_yoy": 4.0,
            "vacancy_rate_pct": 4.4, "population_growth_pct": 2.6,
        },
        "atlanta": {
            "avg_price_change_pct_yoy": 4.4, "inventory_months": 2.7,
            "days_on_market": 24, "price_per_sqft": 225,
            "avg_home_price": 405000, "rent_growth_pct_yoy": 3.6,
            "vacancy_rate_pct": 5.0, "population_growth_pct": 1.9,
        },
        "dallas": {
            "avg_price_change_pct_yoy": 3.8, "inventory_months": 3.0,
            "days_on_market": 26, "price_per_sqft": 215,
            "avg_home_price": 390000, "rent_growth_pct_yoy": 3.0,
            "vacancy_rate_pct": 5.3, "population_growth_pct": 1.7,
        },
        "houston": {
            "avg_price_change_pct_yoy": 3.1, "inventory_months": 3.4,
            "days_on_market": 30, "price_per_sqft": 190,
            "avg_home_price": 340000, "rent_growth_pct_yoy": 2.8,
            "vacancy_rate_pct": 6.0, "population_growth_pct": 1.5,
        },
        "las_vegas": {
            "avg_price_change_pct_yoy": 4.9, "inventory_months": 2.6,
            "days_on_market": 21, "price_per_sqft": 220,
            "avg_home_price": 415000, "rent_growth_pct_yoy": 3.5,
            "vacancy_rate_pct": 5.5, "population_growth_pct": 1.8,
        },
    }

    def _market_type(self, inventory_months: float) -> str:
        if inventory_months < 2.5:
            return "Strong Seller's Market"
        if inventory_months < 4.0:
            return "Seller's Market"
        if inventory_months < 6.0:
            return "Balanced Market"
        return "Buyer's Market"

    def _investment_score(self, data: dict) -> int:
        """Score 0-100: combines appreciation, rent growth, population growth, vacancy."""
        score = 0
        score += min(30, int(data["avg_price_change_pct_yoy"] * 4))
        score += min(25, int(data["rent_growth_pct_yoy"] * 5))
        score += min(25, int(data["population_growth_pct"] * 8))
        vacancy = data["vacancy_rate_pct"]
        score += 20 if vacancy < 4 else (15 if vacancy < 5 else (10 if vacancy < 6 else 5))
        return min(100, score)

    def get_market_report(self, market: str) -> dict:
        """Return comprehensive market report for a metro area."""
        key = market.lower().replace(" ", "_")
        data = self.MARKET_DATA.get(key)
        if data is None:
            return {"market": market, "data_available": False}

        return {
            "market": market,
            "data_available": True,
            "avg_home_price_usd": data["avg_home_price"],
            "price_change_pct_yoy": data["avg_price_change_pct_yoy"],
            "price_per_sqft_usd": data["price_per_sqft"],
            "avg_days_on_market": data["days_on_market"],
            "inventory_months_supply": data["inventory_months"],
            "market_type": self._market_type(data["inventory_months"]),
            "rent_growth_pct_yoy": data["rent_growth_pct_yoy"],
            "vacancy_rate_pct": data["vacancy_rate_pct"],
            "population_growth_pct": data["population_growth_pct"],
            "investment_score": self._investment_score(data),
        }

    def rank_markets(self, top_n: int = 5) -> list:
        """Return markets ranked by investment score (best first)."""
        ranked = [
            {"market": k, **{"investment_score": self._investment_score(v)},
             "price_change_pct": v["avg_price_change_pct_yoy"],
             "avg_home_price_usd": v["avg_home_price"]}
            for k, v in self.MARKET_DATA.items()
        ]
        return sorted(ranked, key=lambda x: x["investment_score"], reverse=True)[:top_n]

    def compare_markets(self, markets: list) -> list:
        """Return side-by-side comparison of multiple markets."""
        return [self.get_market_report(m) for m in markets]

    def get_price_trend_signal(self, market: str) -> str:
        """Return BUY / HOLD / SELL signal based on market conditions."""
        key = market.lower().replace(" ", "_")
        data = self.MARKET_DATA.get(key)
        if data is None:
            return "INSUFFICIENT_DATA"

        score = self._investment_score(data)
        if score >= 70:
            return "STRONG BUY"
        if score >= 50:
            return "BUY"
        if score >= 35:
            return "HOLD"
        return "SELL"