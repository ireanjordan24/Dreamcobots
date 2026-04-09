"""
Stack & Profit Bot — AI-powered deal stacking and profit optimization.

Modules
-------
1. DealBot          — Price-drop deal finder across major retail stores.
2. PennyBot         — Penny-deal hunter for resale arbitrage (PRO+).
3. ReceiptBot       — Cashback orchestrator (CoinOut / Ibotta / Fetch Rewards).
4. FlipBot          — Local flip-opportunity finder (PRO+).
5. CouponBot        — Coupon stacker with optimal ordering.
6. ProfitEngine     — AI cost/profit calculation engine.
7. RankingAI        — Opportunity scoring and ranking.
8. AlertEngine      — Real-time deal alert dispatcher.

All capabilities are gated by tier (FREE / PRO / ENTERPRISE).
"""

from __future__ import annotations

import sys
import os
import json
import uuid
from dataclasses import dataclass, field
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))
from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from bots.stack_and_profit_bot.tiers import BOT_FEATURES, get_bot_tier_info  # noqa: F401

# ---------------------------------------------------------------------------
# Tier ordering for comparisons
# ---------------------------------------------------------------------------
_TIER_ORDER = {Tier.FREE: 0, Tier.PRO: 1, Tier.ENTERPRISE: 2}


# ---------------------------------------------------------------------------
# Exception
# ---------------------------------------------------------------------------

class StackAndProfitBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Deal dataclass
# ---------------------------------------------------------------------------

@dataclass
class Deal:
    deal_id: str
    title: str
    store: str
    original_price: float
    sale_price: float
    category: str
    coupon_code: Optional[str] = None
    cashback_pct: float = 0.0

    def to_dict(self) -> dict:
        return {
            "deal_id": self.deal_id,
            "title": self.title,
            "store": self.store,
            "original_price": self.original_price,
            "sale_price": self.sale_price,
            "coupon_code": self.coupon_code,
            "cashback_pct": self.cashback_pct,
            "category": self.category,
        }


# ---------------------------------------------------------------------------
# Deterministic mock data helpers
# ---------------------------------------------------------------------------

_MOCK_DEALS = [
    Deal("DEAL-M01", "Sony WH-1000XM5 Headphones", "Amazon", 399.99, 249.99, "electronics", "SAVE50", 8.0),
    Deal("DEAL-M02", "Instant Pot Duo 7-in-1", "Walmart", 99.99, 59.99, "appliances", None, 5.0),
    Deal("DEAL-M03", "Nike Air Max 270", "Target", 150.00, 89.99, "clothing", "NIKE10", 3.0),
    Deal("DEAL-M04", "Keurig K-Elite Coffee Maker", "Best Buy", 189.99, 99.99, "appliances", "COFFEE20", 6.0),
    Deal("DEAL-M05", "Lego Star Wars Millennium Falcon", "Amazon", 849.99, 549.99, "toys", None, 4.0),
    Deal("DEAL-M06", "Apple AirPods Pro (2nd Gen)", "Best Buy", 249.99, 179.99, "electronics", None, 5.0),
    Deal("DEAL-M07", "Dyson V15 Detect Vacuum", "Target", 749.99, 499.99, "appliances", "DYSON50", 7.0),
    Deal("DEAL-M08", "Milwaukee M18 Drill Set", "Home Depot", 349.99, 199.99, "tools", None, 3.0),
    Deal("DEAL-M09", "Pampers Diapers Size 3 (200ct)", "Walmart", 54.99, 34.99, "groceries", None, 10.0),
    Deal("DEAL-M10", "PlayStation 5 Slim Console", "Walmart", 449.99, 399.99, "gaming", None, 2.0),
]


# ---------------------------------------------------------------------------
# 1. DealBot
# ---------------------------------------------------------------------------

class DealBot:
    """Finds price-drop deals across major retail stores."""

    _STORE_DEALS: dict[str, list[Deal]] = {
        "Amazon": [
            Deal("DB-AMZ-01", "Sony WH-1000XM5 Headphones", "Amazon", 399.99, 249.99, "electronics", "SAVE50", 8.0),
            Deal("DB-AMZ-02", "Kindle Paperwhite 16GB", "Amazon", 159.99, 109.99, "electronics", None, 4.0),
            Deal("DB-AMZ-03", "Lego Star Wars Millennium Falcon", "Amazon", 849.99, 549.99, "toys", None, 4.0),
            Deal("DB-AMZ-04", "Ninja AF101 Air Fryer", "Amazon", 129.99, 79.99, "appliances", "NINJA20", 6.0),
            Deal("DB-AMZ-05", "Colgate Whitening Toothpaste 6pk", "Amazon", 18.99, 11.99, "beauty", None, 5.0),
        ],
        "Walmart": [
            Deal("DB-WMT-01", "Instant Pot Duo 7-in-1", "Walmart", 99.99, 59.99, "appliances", None, 5.0),
            Deal("DB-WMT-02", "Pampers Diapers Size 3 200ct", "Walmart", 54.99, 34.99, "groceries", None, 10.0),
            Deal("DB-WMT-03", "PlayStation 5 Slim Console", "Walmart", 449.99, 399.99, "gaming", None, 2.0),
            Deal("DB-WMT-04", "Ozark Trail 20qt Cooler", "Walmart", 39.99, 22.99, "sports", None, 3.0),
        ],
        "Target": [
            Deal("DB-TGT-01", "Nike Air Max 270", "Target", 150.00, 89.99, "clothing", "NIKE10", 3.0),
            Deal("DB-TGT-02", "Dyson V15 Detect Vacuum", "Target", 749.99, 499.99, "appliances", "DYSON50", 7.0),
            Deal("DB-TGT-03", "Neutrogena Hydro Boost Moisturizer", "Target", 29.99, 17.99, "beauty", None, 4.0),
        ],
        "Dollar General": [
            Deal("DB-DG-01", "Tide Pods 81ct", "Dollar General", 22.99, 14.99, "groceries", None, 8.0),
            Deal("DB-DG-02", "Bounty Paper Towels 8-pack", "Dollar General", 19.99, 12.99, "home", None, 6.0),
        ],
        "eBay": [
            Deal("DB-EBY-01", "Vintage Levi's 501 Jeans (32x30)", "eBay", 89.99, 45.00, "clothing", None, 0.0),
            Deal("DB-EBY-02", "Nintendo Switch V2", "eBay", 299.99, 199.99, "gaming", None, 0.0),
        ],
        "Walgreens": [
            Deal("DB-WLG-01", "Ensure Plus Nutrition Shake 24pk", "Walgreens", 44.99, 27.99, "groceries", None, 9.0),
            Deal("DB-WLG-02", "Revlon ColorStay Foundation", "Walgreens", 19.99, 11.99, "beauty", "BEAUTY30", 5.0),
        ],
        "Best Buy": [
            Deal("DB-BBY-01", "Keurig K-Elite Coffee Maker", "Best Buy", 189.99, 99.99, "appliances", "COFFEE20", 6.0),
            Deal("DB-BBY-02", "Apple AirPods Pro 2nd Gen", "Best Buy", 249.99, 179.99, "electronics", None, 5.0),
            Deal("DB-BBY-03", "Samsung 65in 4K QLED TV", "Best Buy", 1299.99, 799.99, "electronics", "TV200", 4.0),
        ],
        "Home Depot": [
            Deal("DB-HD-01", "Milwaukee M18 Drill Set", "Home Depot", 349.99, 199.99, "tools", None, 3.0),
            Deal("DB-HD-02", "Ryobi 18V ONE+ Circular Saw", "Home Depot", 89.99, 59.99, "tools", None, 2.0),
            Deal("DB-HD-03", "DEWALT 20V MAX Combo Kit", "Home Depot", 299.99, 199.99, "tools", "DEWALT20", 3.0),
        ],
    }

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._daily_limit = 5 if tier == Tier.FREE else (50 if tier == Tier.PRO else None)
        self._deals_found_today = 0

    def find_deals(self, store: str = None, category: str = None) -> list[Deal]:
        """Return mock deals filtered by store and/or category."""
        all_deals: list[Deal] = []
        if store:
            all_deals = self._STORE_DEALS.get(store, [])
        else:
            for deals in self._STORE_DEALS.values():
                all_deals.extend(deals)

        if category:
            all_deals = [d for d in all_deals if d.category == category]

        # Apply daily limit
        if self._daily_limit is not None:
            remaining = self._daily_limit - self._deals_found_today
            if remaining <= 0:
                return []
            all_deals = all_deals[:remaining]

        self._deals_found_today += len(all_deals)
        return all_deals

    def get_affiliate_commission(self, deal: Deal) -> float:
        """Return 5-15% of sale_price as affiliate commission (deterministic)."""
        pct_map = {
            "electronics": 0.08,
            "appliances": 0.07,
            "clothing": 0.10,
            "toys": 0.06,
            "groceries": 0.05,
            "beauty": 0.12,
            "tools": 0.06,
            "gaming": 0.05,
            "sports": 0.09,
            "home": 0.08,
        }
        pct = pct_map.get(deal.category, 0.07)
        return round(deal.sale_price * pct, 2)


# ---------------------------------------------------------------------------
# 2. PennyBot
# ---------------------------------------------------------------------------

class PennyBot:
    """Finds penny deals for resale arbitrage. PRO/ENTERPRISE only."""

    _PENNY_ITEMS = [
        {"item_id": "PNY-01", "title": "Scotch Magic Tape Roll", "store": "Dollar General", "price": 0.01, "resale_value": 2.50, "category": "home"},
        {"item_id": "PNY-02", "title": "Composition Notebook Wide Ruled", "store": "Walmart", "price": 0.01, "resale_value": 3.00, "category": "education"},
        {"item_id": "PNY-03", "title": "Crayola Crayons 24ct", "store": "Target", "price": 0.01, "resale_value": 4.50, "category": "toys"},
        {"item_id": "PNY-04", "title": "Band-Aid Variety Pack 30ct", "store": "Walgreens", "price": 0.01, "resale_value": 5.00, "category": "health"},
        {"item_id": "PNY-05", "title": "Sharpie Fine Point Marker Set", "store": "Dollar General", "price": 0.01, "resale_value": 6.00, "category": "office"},
        {"item_id": "PNY-06", "title": "Post-it Notes 3x3 100ct", "store": "Walmart", "price": 0.50, "resale_value": 4.00, "category": "office"},
        {"item_id": "PNY-07", "title": "Energizer AA Batteries 4pk", "store": "Dollar General", "price": 0.99, "resale_value": 5.99, "category": "home"},
        {"item_id": "PNY-08", "title": "Coloring Book Adults Mandala", "store": "Target", "price": 0.01, "resale_value": 8.00, "category": "toys"},
        {"item_id": "PNY-09", "title": "Hand Sanitizer Purell 8oz", "store": "Walgreens", "price": 0.01, "resale_value": 3.50, "category": "health"},
        {"item_id": "PNY-10", "title": "Scotch-Brite Scrub Sponge 6pk", "store": "Walmart", "price": 0.01, "resale_value": 4.99, "category": "home"},
    ]

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier

    def _check_tier(self) -> None:
        if _TIER_ORDER[self.tier] < _TIER_ORDER[Tier.PRO]:
            raise StackAndProfitBotTierError(
                "PennyBot requires PRO or ENTERPRISE tier."
            )

    def find_penny_deals(self, store: str = None) -> list[dict]:
        """Return penny deal items ($0.01–$1.00) with resale value. PRO+ only."""
        self._check_tier()
        items = self._PENNY_ITEMS
        if store:
            items = [i for i in items if i["store"] == store]
        result = []
        for item in items:
            entry = dict(item)
            entry["profit"] = round(entry["resale_value"] - entry["price"], 2)
            result.append(entry)
        return result

    def estimate_resale_profit(self, item: dict) -> float:
        """Return estimated profit for a penny deal item."""
        self._check_tier()
        return round(item.get("resale_value", 0.0) - item.get("price", 0.0), 2)


# ---------------------------------------------------------------------------
# 3. ReceiptBot
# ---------------------------------------------------------------------------

class ReceiptBot:
    """Cashback from receipts via CoinOut / Ibotta / Fetch Rewards."""

    _CASHBACK_APPS = {
        "CoinOut": 0.02,
        "Ibotta": 0.05,
        "Fetch Rewards": 0.03,
    }

    _FREE_DAILY_LIMIT = 3

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._uploads_today = 0

    def upload_receipt(self, store: str, amount: float) -> dict:
        """Return cashback opportunities for a receipt. FREE limited to 3/day."""
        if self.tier == Tier.FREE and self._uploads_today >= self._FREE_DAILY_LIMIT:
            raise StackAndProfitBotTierError(
                "FREE tier allows only 3 receipt uploads per day. Upgrade to PRO for unlimited."
            )

        self._uploads_today += 1

        if self.tier == Tier.FREE:
            apps = {"CoinOut": round(amount * self._CASHBACK_APPS["CoinOut"], 2)}
        else:
            apps = {app: round(amount * pct, 2) for app, pct in self._CASHBACK_APPS.items()}

        total = round(sum(apps.values()), 2)
        return {
            "store": store,
            "purchase_amount": amount,
            "cashback_by_app": apps,
            "total_cashback": total,
            "tier": self.tier.value,
        }

    def calculate_total_cashback(self, receipts: list[dict]) -> float:
        """Sum total_cashback across a list of receipt results."""
        return round(sum(r.get("total_cashback", 0.0) for r in receipts), 2)


# ---------------------------------------------------------------------------
# 4. FlipBot
# ---------------------------------------------------------------------------

class FlipBot:
    """Finds local flip opportunities. PRO/ENTERPRISE only."""

    _FLIP_ITEMS = [
        {"flip_id": "FLP-01", "title": "iPhone 12 (cracked screen)", "source": "Facebook Marketplace", "buy_price": 80.0, "sell_price": 220.0, "category": "electronics"},
        {"flip_id": "FLP-02", "title": "Vintage Leather Couch", "source": "Facebook Marketplace", "buy_price": 50.0, "sell_price": 200.0, "category": "home"},
        {"flip_id": "FLP-03", "title": "Nintendo Switch (broken joystick)", "source": "eBay", "buy_price": 60.0, "sell_price": 175.0, "category": "gaming"},
        {"flip_id": "FLP-04", "title": "Stanley Tool Box 26in", "source": "Facebook Marketplace", "buy_price": 40.0, "sell_price": 120.0, "category": "tools"},
        {"flip_id": "FLP-05", "title": "Roomba i3 Robot Vacuum", "source": "eBay", "buy_price": 75.0, "sell_price": 180.0, "category": "appliances"},
        {"flip_id": "FLP-06", "title": "Air Jordan 1 Retro High OG", "source": "Facebook Marketplace", "buy_price": 100.0, "sell_price": 280.0, "category": "clothing"},
        {"flip_id": "FLP-07", "title": "Dewalt 18V Drill (no charger)", "source": "Facebook Marketplace", "buy_price": 25.0, "sell_price": 80.0, "category": "tools"},
        {"flip_id": "FLP-08", "title": "KitchenAid Stand Mixer 5qt", "source": "Facebook Marketplace", "buy_price": 90.0, "sell_price": 220.0, "category": "appliances"},
        {"flip_id": "FLP-09", "title": "Vintage Levi's 501 Jeans (32x30)", "source": "eBay", "buy_price": 15.0, "sell_price": 65.0, "category": "clothing"},
        {"flip_id": "FLP-10", "title": "Peloton Bike (Generation 1)", "source": "Facebook Marketplace", "buy_price": 300.0, "sell_price": 700.0, "category": "sports"},
    ]

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier

    def _check_tier(self) -> None:
        if _TIER_ORDER[self.tier] < _TIER_ORDER[Tier.PRO]:
            raise StackAndProfitBotTierError(
                "FlipBot requires PRO or ENTERPRISE tier."
            )

    def find_flips(self, location: str = "local", budget: float = 500.0) -> list[dict]:
        """Return flip opportunities within budget. PRO+ only."""
        self._check_tier()
        result = []
        for item in self._FLIP_ITEMS:
            if item["buy_price"] <= budget:
                entry = dict(item)
                entry["profit"] = round(entry["sell_price"] - entry["buy_price"], 2)
                entry["profit_pct"] = round((entry["profit"] / entry["buy_price"]) * 100, 1)
                entry["location"] = location
                result.append(entry)
        return result

    def rank_flips(self, flips: list[dict]) -> list[dict]:
        """Sort flips by profit_pct descending."""
        self._check_tier()
        return sorted(flips, key=lambda f: f.get("profit_pct", 0.0), reverse=True)


# ---------------------------------------------------------------------------
# 5. CouponBot
# ---------------------------------------------------------------------------

class CouponBot:
    """Stacks coupons for maximum savings."""

    _STORE_COUPONS: dict[str, list[dict]] = {
        "Amazon": [
            {"code": "SAVE50", "discount_amount": 50.0, "discount_type": "fixed", "source": "Amazon Promo", "min_purchase": 200.0},
            {"code": "PRIME10", "discount_amount": 10.0, "discount_type": "pct", "source": "Prime Exclusive", "min_purchase": 0.0},
            {"code": "DEAL15", "discount_amount": 15.0, "discount_type": "pct", "source": "Lightning Deal", "min_purchase": 50.0},
        ],
        "Walmart": [
            {"code": "WMART5", "discount_amount": 5.0, "discount_type": "fixed", "source": "Walmart.com", "min_purchase": 25.0},
            {"code": "PICKUP10", "discount_amount": 10.0, "discount_type": "pct", "source": "Pickup Discount", "min_purchase": 30.0},
        ],
        "Target": [
            {"code": "CIRCLE15", "discount_amount": 15.0, "discount_type": "pct", "source": "Target Circle", "min_purchase": 0.0},
            {"code": "REDCARD5", "discount_amount": 5.0, "discount_type": "pct", "source": "RedCard", "min_purchase": 0.0},
            {"code": "APP10", "discount_amount": 10.0, "discount_type": "fixed", "source": "Target App", "min_purchase": 40.0},
        ],
        "Best Buy": [
            {"code": "COFFEE20", "discount_amount": 20.0, "discount_type": "fixed", "source": "Best Buy Promo", "min_purchase": 80.0},
            {"code": "BESTPLUS5", "discount_amount": 5.0, "discount_type": "pct", "source": "Best Buy Plus", "min_purchase": 0.0},
        ],
        "Home Depot": [
            {"code": "DEWALT20", "discount_amount": 20.0, "discount_type": "fixed", "source": "Home Depot Pro", "min_purchase": 100.0},
            {"code": "SPRING10", "discount_amount": 10.0, "discount_type": "pct", "source": "Seasonal Sale", "min_purchase": 50.0},
        ],
        "Walgreens": [
            {"code": "BEAUTY30", "discount_amount": 30.0, "discount_type": "pct", "source": "myWalgreens", "min_purchase": 0.0},
            {"code": "WELLNESS5", "discount_amount": 5.0, "discount_type": "fixed", "source": "Walgreens App", "min_purchase": 20.0},
        ],
        "Dollar General": [
            {"code": "DG5OFF", "discount_amount": 5.0, "discount_type": "fixed", "source": "DG App", "min_purchase": 25.0},
            {"code": "DGDIGITAL20", "discount_amount": 20.0, "discount_type": "pct", "source": "Digital Coupon", "min_purchase": 10.0},
        ],
    }

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._max_stack = 1 if tier == Tier.FREE else 5

    def find_coupons(self, store: str, product: str = None) -> list[dict]:
        """Return available coupons for a store."""
        coupons = self._STORE_COUPONS.get(store, [])
        if product:
            keyword = product.lower()
            coupons = [c for c in coupons if keyword in c.get("source", "").lower() or keyword in c.get("code", "").lower()]
        return list(coupons)

    def stack_coupons(self, coupons: list[dict], original_price: float) -> dict:
        """Apply coupons in optimal order. FREE: 1 coupon; PRO+: up to 5."""
        # Sort coupons: fixed first (higher absolute value), then pct
        def coupon_value(c: dict) -> float:
            if c["discount_type"] == "fixed":
                return c["discount_amount"]
            return original_price * c["discount_amount"] / 100.0

        sorted_coupons = sorted(coupons, key=coupon_value, reverse=True)
        applicable = [c for c in sorted_coupons if original_price >= c.get("min_purchase", 0.0)]
        applicable = applicable[: self._max_stack]

        current_price = original_price
        applied = []
        for coupon in applicable:
            if current_price < coupon.get("min_purchase", 0.0):
                continue
            if coupon["discount_type"] == "fixed":
                discount = min(coupon["discount_amount"], current_price)
            else:
                discount = round(current_price * coupon["discount_amount"] / 100.0, 2)
            current_price = round(max(current_price - discount, 0.0), 2)
            applied.append(coupon)

        total_saved = round(original_price - current_price, 2)
        return {
            "original_price": original_price,
            "final_price": current_price,
            "total_saved": total_saved,
            "applied_coupons": applied,
            "tier": self.tier.value,
        }


# ---------------------------------------------------------------------------
# 6. ProfitEngine
# ---------------------------------------------------------------------------

class ProfitEngine:
    """Calculates net profit for deals accounting for cashback and coupons."""

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier

    def calculate_profit(self, deal: Deal) -> dict:
        """Return comprehensive profit breakdown for a deal."""
        savings = round(deal.original_price - deal.sale_price, 2)
        savings_pct = round((savings / deal.original_price) * 100, 1) if deal.original_price else 0.0
        cashback = round(deal.sale_price * deal.cashback_pct / 100.0, 2)
        net_profit = round(savings + cashback, 2)
        roi_pct = round((net_profit / deal.original_price) * 100, 1) if deal.original_price else 0.0
        final_cost = round(deal.sale_price - cashback, 2)
        return {
            "deal_id": deal.deal_id,
            "title": deal.title,
            "finalCost": final_cost,
            "savings": savings,
            "savings_pct": savings_pct,
            "cashback": cashback,
            "net_profit": net_profit,
            "roi_pct": roi_pct,
        }

    def batch_calculate(self, deals: list[Deal]) -> list[dict]:
        """Calculate profit for multiple deals."""
        return [self.calculate_profit(d) for d in deals]


# ---------------------------------------------------------------------------
# 7. RankingAI
# ---------------------------------------------------------------------------

class RankingAI:
    """Scores and ranks deals by profit potential."""

    _STORE_REPUTATION: dict[str, float] = {
        "Amazon": 1.0,
        "Walmart": 0.95,
        "Target": 0.93,
        "Best Buy": 0.90,
        "Home Depot": 0.88,
        "Walgreens": 0.85,
        "Dollar General": 0.80,
        "eBay": 0.75,
        "Facebook Marketplace": 0.65,
    }

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier

    def score_deal(self, deal: Deal) -> float:
        """Return 0-100 score based on savings_pct, cashback_pct, store reputation."""
        if deal.original_price <= 0:
            return 0.0
        savings_pct = ((deal.original_price - deal.sale_price) / deal.original_price) * 100.0
        reputation = self._STORE_REPUTATION.get(deal.store, 0.70)
        # Weighted: 50% savings, 30% cashback, 20% reputation
        score = (savings_pct * 0.50) + (deal.cashback_pct * 3.0 * 0.30) + (reputation * 20.0 * 0.20)
        return round(min(score, 100.0), 2)

    def rank_deals(self, deals: list[Deal]) -> list[Deal]:
        """Return deals sorted by score descending."""
        return sorted(deals, key=lambda d: self.score_deal(d), reverse=True)

    def get_top_deals(self, deals: list[Deal], n: int = 5) -> list[Deal]:
        """Return top N deals by score."""
        return self.rank_deals(deals)[:n]


# ---------------------------------------------------------------------------
# 8. AlertEngine
# ---------------------------------------------------------------------------

class AlertEngine:
    """Generates alerts for high-profit deals."""

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._profit_engine = ProfitEngine(tier)

    def should_alert(self, deal: Deal, min_profit: float = 15.0) -> bool:
        """Return True if deal's net_profit meets or exceeds min_profit threshold."""
        result = self._profit_engine.calculate_profit(deal)
        return result["net_profit"] >= min_profit

    def get_alerts(self, deals: list[Deal], min_profit: float = 15.0) -> list[dict]:
        """Return alert dicts for deals that meet the profit threshold."""
        alerts = []
        for deal in deals:
            result = self._profit_engine.calculate_profit(deal)
            if result["net_profit"] >= min_profit:
                net_profit = result["net_profit"]
                if net_profit >= 100.0:
                    urgency = "HIGH"
                elif net_profit >= 40.0:
                    urgency = "MEDIUM"
                else:
                    urgency = "LOW"
                alerts.append({
                    "deal_id": deal.deal_id,
                    "title": deal.title,
                    "store": deal.store,
                    "net_profit": net_profit,
                    "savings_pct": result["savings_pct"],
                    "urgency": urgency,
                    "deal": deal.to_dict(),
                })
        return alerts


# ---------------------------------------------------------------------------
# Main StackAndProfitBot
# ---------------------------------------------------------------------------

class StackAndProfitBot:
    """
    AI-powered deal stacking and profit optimization bot.

    Orchestrates DealBot, PennyBot, ReceiptBot, FlipBot, CouponBot,
    ProfitEngine, RankingAI, and AlertEngine.
    """

    def __init__(self, tier: Tier = Tier.FREE, user_id: str = None) -> None:
        self._tier = tier
        self._config = get_tier_config(tier)
        self._user_id = user_id or str(uuid.uuid4())

        # Sub-bots
        self.deal_bot = DealBot(tier)
        self.penny_bot = PennyBot(tier)
        self.receipt_bot = ReceiptBot(tier)
        self.flip_bot = FlipBot(tier)
        self.coupon_bot = CouponBot(tier)

        # AI Engines
        self.profit_engine = ProfitEngine(tier)
        self.ranking_ai = RankingAI(tier)
        self.alert_engine = AlertEngine(tier)

    @property
    def tier(self) -> Tier:
        return self._tier

    @property
    def config(self):
        return self._config

    @property
    def user_id(self) -> str:
        return self._user_id

    def _require_tier(self, feature_name: str, min_tier: Tier) -> None:
        """Raise StackAndProfitBotTierError if current tier is below min_tier."""
        if _TIER_ORDER[self._tier] < _TIER_ORDER[min_tier]:
            raise StackAndProfitBotTierError(
                f"Feature '{feature_name}' requires {min_tier.value} tier or higher. "
                f"Current tier: {self._tier.value}."
            )

    def run_all_bots(self, min_profit: float = 15.0) -> dict:
        """
        Run all available bots for the current tier and return aggregated results.
        """
        deals = self.deal_bot.find_deals()
        ranked_deals = self.ranking_ai.rank_deals(deals)
        alerts = self.alert_engine.get_alerts(ranked_deals, min_profit=min_profit)

        coupon_results = []
        for deal in ranked_deals[:5]:
            coupons = self.coupon_bot.find_coupons(deal.store)
            if coupons:
                result = self.coupon_bot.stack_coupons(coupons, deal.sale_price)
                coupon_results.append({"deal_id": deal.deal_id, "coupon_result": result})

        penny_deals: list[dict] = []
        flips: list[dict] = []

        if _TIER_ORDER[self._tier] >= _TIER_ORDER[Tier.PRO]:
            penny_deals = self.penny_bot.find_penny_deals()
            raw_flips = self.flip_bot.find_flips()
            flips = self.flip_bot.rank_flips(raw_flips)

        profit_calcs = self.profit_engine.batch_calculate(ranked_deals)
        estimated_daily_profit = round(sum(p["net_profit"] for p in profit_calcs), 2)

        return {
            "deals": [d.to_dict() for d in ranked_deals],
            "penny_deals": penny_deals,
            "flips": flips,
            "alerts": alerts,
            "coupon_results": coupon_results,
            "total_opportunities": len(ranked_deals) + len(penny_deals) + len(flips),
            "estimated_daily_profit": estimated_daily_profit,
        }

    def rank_deals(self, deals: list[Deal]) -> list[Deal]:
        """Proxy to RankingAI.rank_deals."""
        return self.ranking_ai.rank_deals(deals)

    def get_alerts(self, deals: list[Deal], min_profit: float = 15.0) -> list[dict]:
        """Proxy to AlertEngine.get_alerts."""
        return self.alert_engine.get_alerts(deals, min_profit=min_profit)

    def calculate_profit(self, deal: Deal) -> dict:
        """Proxy to ProfitEngine.calculate_profit."""
        return self.profit_engine.calculate_profit(deal)

    def get_tier_info(self) -> dict:
        """Return current tier info."""
        return get_bot_tier_info(self._tier)

    def load_preloaded_deals(self) -> list[Deal]:
        """Load deals from data/first_50_deals.json if it exists."""
        data_path = os.path.join(
            os.path.dirname(__file__), "..", "..", "data", "first_50_deals.json"
        )
        if not os.path.exists(data_path):
            return []
        with open(data_path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        deals = []
        for item in raw:
            deals.append(Deal(
                deal_id=item.get("deal_id", ""),
                title=item.get("title", ""),
                store=item.get("store", ""),
                original_price=float(item.get("original_price", 0.0)),
                sale_price=float(item.get("sale_price", 0.0)),
                category=item.get("category", ""),
                coupon_code=item.get("coupon_code"),
                cashback_pct=float(item.get("cashback_pct", 0.0)),
            ))
        return deals
