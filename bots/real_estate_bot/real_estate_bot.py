# GLOBAL AI SOURCES FLOW
"""Real Estate Bot — tier-aware real estate deal finder and ROI analyzer."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
from tiers import Tier, get_tier_config, get_upgrade_path
from bots.real_estate_bot.tiers import BOT_FEATURES, get_bot_tier_info
from framework import GlobalAISourcesFlow  # noqa: F401


class RealEstateBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class RealEstateBot:
    """Tier-aware real estate deal finder and ROI analyzer."""

    LOCATION_LIMITS = {Tier.FREE: 1, Tier.PRO: 10, Tier.ENTERPRISE: None}

    PROPERTY_DATABASE = {
        "austin": [
            {"address": "1204 Oak Blvd, Austin TX", "price": 320000, "beds": 3, "baths": 2, "sqft": 1450, "type": "single_family", "monthly_rent": 2400, "year_built": 1998},
            {"address": "5601 Riverside Dr #203, Austin TX", "price": 185000, "beds": 2, "baths": 1, "sqft": 875, "type": "condo", "monthly_rent": 1600, "year_built": 2005},
            {"address": "820 S Congress Ave, Austin TX", "price": 450000, "beds": 4, "baths": 3, "sqft": 2100, "type": "single_family", "monthly_rent": 3200, "year_built": 2001},
            {"address": "311 W 7th St #402, Austin TX", "price": 275000, "beds": 1, "baths": 1, "sqft": 720, "type": "condo", "monthly_rent": 2000, "year_built": 2010},
            {"address": "4422 Burnet Rd, Austin TX", "price": 380000, "beds": 3, "baths": 2, "sqft": 1600, "type": "townhouse", "monthly_rent": 2800, "year_built": 2003},
        ],
        "phoenix": [
            {"address": "3901 E Indian School Rd, Phoenix AZ", "price": 285000, "beds": 3, "baths": 2, "sqft": 1550, "type": "single_family", "monthly_rent": 2100, "year_built": 1995},
            {"address": "1820 N 44th St #110, Phoenix AZ", "price": 165000, "beds": 2, "baths": 2, "sqft": 1000, "type": "condo", "monthly_rent": 1450, "year_built": 2002},
            {"address": "6120 N 7th Ave, Phoenix AZ", "price": 220000, "beds": 3, "baths": 2, "sqft": 1350, "type": "single_family", "monthly_rent": 1800, "year_built": 1988},
            {"address": "2401 W Camelback Rd, Phoenix AZ", "price": 340000, "beds": 4, "baths": 2, "sqft": 1900, "type": "single_family", "monthly_rent": 2500, "year_built": 2000},
            {"address": "910 E Osborn Rd #301, Phoenix AZ", "price": 195000, "beds": 2, "baths": 1, "sqft": 880, "type": "condo", "monthly_rent": 1600, "year_built": 2008},
        ],
        "nashville": [
            {"address": "2204 Belmont Blvd, Nashville TN", "price": 415000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "monthly_rent": 2900, "year_built": 1997},
            {"address": "500 Church St #1205, Nashville TN", "price": 310000, "beds": 2, "baths": 2, "sqft": 1100, "type": "condo", "monthly_rent": 2400, "year_built": 2012},
            {"address": "1122 Gallatin Ave, Nashville TN", "price": 295000, "beds": 3, "baths": 1, "sqft": 1400, "type": "single_family", "monthly_rent": 2200, "year_built": 1962},
            {"address": "4401 Murphy Rd, Nashville TN", "price": 375000, "beds": 4, "baths": 3, "sqft": 2000, "type": "townhouse", "monthly_rent": 2700, "year_built": 2004},
        ],
        "denver": [
            {"address": "1502 Larimer St #4C, Denver CO", "price": 265000, "beds": 1, "baths": 1, "sqft": 750, "type": "condo", "monthly_rent": 2000, "year_built": 2007},
            {"address": "3822 W 38th Ave, Denver CO", "price": 445000, "beds": 3, "baths": 2, "sqft": 1650, "type": "single_family", "monthly_rent": 3100, "year_built": 1955},
            {"address": "7001 E Colfax Ave, Denver CO", "price": 325000, "beds": 3, "baths": 2, "sqft": 1500, "type": "single_family", "monthly_rent": 2500, "year_built": 1974},
        ],
        "tampa": [
            {"address": "4810 W Kennedy Blvd, Tampa FL", "price": 310000, "beds": 3, "baths": 2, "sqft": 1550, "type": "single_family", "monthly_rent": 2300, "year_built": 1993},
            {"address": "111 N 12th St #2205, Tampa FL", "price": 220000, "beds": 2, "baths": 2, "sqft": 1050, "type": "condo", "monthly_rent": 1900, "year_built": 2006},
            {"address": "2901 W Cypress St, Tampa FL", "price": 275000, "beds": 3, "baths": 2, "sqft": 1350, "type": "single_family", "monthly_rent": 2100, "year_built": 1985},
        ],
        "charlotte": [
            {"address": "2215 Park Rd, Charlotte NC", "price": 295000, "beds": 3, "baths": 2, "sqft": 1480, "type": "single_family", "monthly_rent": 2100, "year_built": 1996},
            {"address": "500 W 5th St #1804, Charlotte NC", "price": 245000, "beds": 1, "baths": 1, "sqft": 820, "type": "condo", "monthly_rent": 1800, "year_built": 2014},
        ],
        "atlanta": [
            {"address": "1350 Spring St NW, Atlanta GA", "price": 380000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "monthly_rent": 2600, "year_built": 2001},
            {"address": "805 Peachtree St NE #14, Atlanta GA", "price": 290000, "beds": 2, "baths": 2, "sqft": 1200, "type": "condo", "monthly_rent": 2200, "year_built": 2009},
        ],
        "dallas": [
            {"address": "4421 Lemmon Ave, Dallas TX", "price": 350000, "beds": 3, "baths": 2, "sqft": 1600, "type": "single_family", "monthly_rent": 2500, "year_built": 1999},
            {"address": "2922 Elm St #301, Dallas TX", "price": 210000, "beds": 1, "baths": 1, "sqft": 780, "type": "condo", "monthly_rent": 1700, "year_built": 2011},
        ],
        "houston": [
            {"address": "3901 Richmond Ave, Houston TX", "price": 290000, "beds": 3, "baths": 2, "sqft": 1500, "type": "single_family", "monthly_rent": 2000, "year_built": 1994},
            {"address": "2400 Mid Ln #401, Houston TX", "price": 175000, "beds": 2, "baths": 2, "sqft": 950, "type": "condo", "monthly_rent": 1500, "year_built": 2003},
        ],
        "las_vegas": [
            {"address": "8901 W Charleston Blvd, Las Vegas NV", "price": 320000, "beds": 3, "baths": 2, "sqft": 1700, "type": "single_family", "monthly_rent": 2200, "year_built": 2002},
            {"address": "4455 Paradise Rd #506, Las Vegas NV", "price": 185000, "beds": 2, "baths": 2, "sqft": 1000, "type": "condo", "monthly_rent": 1550, "year_built": 2007},
        ],
    }

    MARKET_TRENDS = {
        "austin": {"avg_price_change_pct": 6.2, "inventory_months": 2.1, "days_on_market": 18, "price_per_sqft": 285},
        "phoenix": {"avg_price_change_pct": 4.8, "inventory_months": 2.8, "days_on_market": 22, "price_per_sqft": 210},
        "nashville": {"avg_price_change_pct": 5.5, "inventory_months": 1.9, "days_on_market": 15, "price_per_sqft": 260},
        "denver": {"avg_price_change_pct": 3.2, "inventory_months": 3.1, "days_on_market": 28, "price_per_sqft": 295},
        "tampa": {"avg_price_change_pct": 7.1, "inventory_months": 2.5, "days_on_market": 20, "price_per_sqft": 230},
        "charlotte": {"avg_price_change_pct": 5.9, "inventory_months": 2.2, "days_on_market": 17, "price_per_sqft": 218},
        "atlanta": {"avg_price_change_pct": 4.4, "inventory_months": 2.7, "days_on_market": 24, "price_per_sqft": 225},
        "dallas": {"avg_price_change_pct": 3.8, "inventory_months": 3.0, "days_on_market": 26, "price_per_sqft": 215},
        "houston": {"avg_price_change_pct": 3.1, "inventory_months": 3.4, "days_on_market": 30, "price_per_sqft": 190},
        "las_vegas": {"avg_price_change_pct": 4.9, "inventory_months": 2.6, "days_on_market": 21, "price_per_sqft": 220},
    }

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._searched_locations: list = []

    def _check_location_limit(self, location: str) -> None:
        limit = self.LOCATION_LIMITS[self.tier]
        loc_lower = location.lower().replace(" ", "_")
        if limit is not None and len(self._searched_locations) >= limit and loc_lower not in self._searched_locations:
            raise RealEstateBotTierError(
                f"Location limit of {limit} reached on {self.config.name} tier. Upgrade to search more locations."
            )
        if loc_lower not in self._searched_locations:
            self._searched_locations.append(loc_lower)

    def search_deals(self, location: str, budget: float) -> list:
        """Return properties under budget in location."""
        self._check_location_limit(location)
        loc_key = location.lower().replace(" ", "_")
        properties = self.PROPERTY_DATABASE.get(loc_key, self.PROPERTY_DATABASE["austin"])
        results = [p for p in properties if p["price"] <= budget]
        for p in results:
            p["roi_estimate"] = round(self.estimate_roi(p), 2)
        return results

    def evaluate_property(self, address: str) -> dict:
        """Return valuation, cap rate, and cash flow analysis."""
        prop = None
        for props in self.PROPERTY_DATABASE.values():
            for p in props:
                if address.lower() in p["address"].lower():
                    prop = p
                    break
            if prop:
                break
        if not prop:
            prop = list(self.PROPERTY_DATABASE["austin"])[0]

        annual_rent = prop["monthly_rent"] * 12
        operating_expenses = annual_rent * 0.35
        noi = annual_rent - operating_expenses
        cap_rate = round(noi / prop["price"] * 100, 2)
        monthly_cashflow = round((noi / 12) - (prop["price"] * 0.008), 2)

        result = {
            "address": prop["address"],
            "price": prop["price"],
            "beds": prop["beds"],
            "baths": prop["baths"],
            "sqft": prop["sqft"],
            "type": prop["type"],
            "monthly_rent": prop["monthly_rent"],
            "annual_rent": annual_rent,
            "cap_rate_pct": cap_rate,
            "monthly_cashflow_usd": monthly_cashflow,
            "noi_usd": round(noi, 2),
            "roi_estimate_pct": round(self.estimate_roi(prop), 2),
            "tier": self.tier.value,
        }
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            result["rental_comps"] = [{"address": "Comparable nearby", "rent": prop["monthly_rent"] + 100}]
            result["cash_flow_analysis"] = {
                "gross_rent": annual_rent,
                "vacancy_loss": round(annual_rent * 0.05, 2),
                "operating_expenses": round(operating_expenses, 2),
                "noi": round(noi, 2),
            }
        if self.tier == Tier.ENTERPRISE:
            result["ai_valuation"] = round(prop["price"] * 1.05, 0)
            result["predictive_appreciation_3yr_pct"] = 12.5
        return result

    def estimate_roi(self, property_dict: dict) -> float:
        """Return estimated annual ROI percentage."""
        annual_rent = property_dict["monthly_rent"] * 12
        operating_expenses = annual_rent * 0.35
        noi = annual_rent - operating_expenses
        return round(noi / property_dict["price"] * 100, 2)

    def get_market_trends(self, location: str) -> dict:
        """Return price trends, inventory, and days-on-market."""
        if self.tier == Tier.FREE:
            raise RealEstateBotTierError("Market trends require PRO or ENTERPRISE tier.")
        loc_key = location.lower().replace(" ", "_")
        trends = self.MARKET_TRENDS.get(loc_key, self.MARKET_TRENDS["austin"])
        result = {
            "location": location,
            "avg_price_change_pct_yoy": trends["avg_price_change_pct"],
            "inventory_months_supply": trends["inventory_months"],
            "avg_days_on_market": trends["days_on_market"],
            "price_per_sqft": trends["price_per_sqft"],
            "market_type": "Seller's" if trends["inventory_months"] < 3 else "Buyer's",
            "tier": self.tier.value,
        }
        if self.tier == Tier.ENTERPRISE:
            result["predictive_analytics"] = {
                "6mo_price_forecast_pct": round(trends["avg_price_change_pct"] / 2, 1),
                "investment_score": min(100, int(trends["avg_price_change_pct"] * 12)),
            }
        return result

    def describe_tier(self) -> str:
        info = get_bot_tier_info(self.tier)
        lines = [
            f"=== {info['name']} Real Estate Bot Tier ===",
            f"Price: ${info['price_usd_monthly']:.2f}/month",
            f"Support: {info['support_level']}",
            "Features:",
        ]
        for f in info["features"]:
            lines.append(f"  \u2713 {f}")
        output = "\n".join(lines)
        print(output)
        return output
