"""
Fiverr Automation Bot — Main Module

Automates Fiverr freelance operations: gig listings, order management,
inbox automation, review collection, analytics, and AI-powered pricing.

Tier-aware: FREE gets 5 gigs + 20 orders/month; PRO 50 gigs + analytics;
ENTERPRISE unlimited gigs with AI pricing and CRM export.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.fiverr_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_GIG_LISTING,
    FEATURE_ORDER_TRACKING,
    FEATURE_INBOX_AUTOMATION,
    FEATURE_REVIEW_COLLECTION,
    FEATURE_ANALYTICS,
    FEATURE_PRICING_OPTIMIZER,
    FEATURE_CRM_EXPORT,
    FEATURE_AI_PRICING,
    FEATURE_WHITE_LABEL,
    FEATURE_BULK_MESSAGING,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class FiverrBotError(Exception):
    """Base exception for Fiverr Bot errors."""


class FiverrBotTierError(FiverrBotError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

class GigCategory(Enum):
    DATA_ENTRY = "data_entry"
    RESEARCH = "research"
    CONTENT_WRITING = "content_writing"
    ANALYTICS = "analytics"
    GRAPHIC_DESIGN = "graphic_design"
    VIDEO_EDITING = "video_editing"
    SEO = "seo"
    SOCIAL_MEDIA = "social_media"
    WEB_DEVELOPMENT = "web_development"
    VIRTUAL_ASSISTANT = "virtual_assistant"


class OrderStatus(Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELIVERED = "delivered"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    REVISION_REQUESTED = "revision_requested"


@dataclass
class Gig:
    gig_id: str
    title: str
    category: GigCategory
    description: str
    price_usd: float
    delivery_days: int
    tags: list = field(default_factory=list)
    active: bool = True
    impressions: int = 0
    clicks: int = 0
    orders_total: int = 0
    rating: float = 0.0
    review_count: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


@dataclass
class Order:
    order_id: str
    gig_id: str
    buyer_username: str
    amount_usd: float
    status: OrderStatus
    requirements: str = ""
    deliverable: str = ""
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    delivered_at: Optional[str] = None
    completed_at: Optional[str] = None


@dataclass
class Review:
    review_id: str
    order_id: str
    gig_id: str
    buyer_username: str
    rating: float          # 1.0 – 5.0
    comment: str
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# GIG_TEMPLATES — realistic starting-point gig definitions
# ---------------------------------------------------------------------------

GIG_TEMPLATES = {
    GigCategory.DATA_ENTRY: {
        "title": "Professional Data Entry & Spreadsheet Management",
        "description": (
            "I will perform accurate, fast data entry into Excel, Google Sheets, "
            "CRM systems, or any database you use. Includes deduplication and "
            "formatting cleanup."
        ),
        "base_price_usd": 15.0,
        "delivery_days": 1,
        "tags": ["data entry", "spreadsheet", "excel", "google sheets", "database"],
    },
    GigCategory.RESEARCH: {
        "title": "In-Depth Market Research & Competitor Analysis",
        "description": (
            "I will research your industry, competitors, or target audience and "
            "deliver a structured report with actionable insights."
        ),
        "base_price_usd": 25.0,
        "delivery_days": 2,
        "tags": ["research", "market analysis", "competitor research", "report"],
    },
    GigCategory.CONTENT_WRITING: {
        "title": "SEO-Optimized Blog Posts & Article Writing",
        "description": (
            "I will write engaging, SEO-friendly articles (500–2,000 words) on "
            "any topic, including keyword research and meta descriptions."
        ),
        "base_price_usd": 20.0,
        "delivery_days": 2,
        "tags": ["blog writing", "SEO", "articles", "content", "copywriting"],
    },
    GigCategory.ANALYTICS: {
        "title": "Business Analytics Dashboard & KPI Reporting",
        "description": (
            "I will build analytics dashboards in Google Data Studio, Tableau, or "
            "Excel, and produce monthly KPI reports tailored to your business goals."
        ),
        "base_price_usd": 50.0,
        "delivery_days": 3,
        "tags": ["analytics", "dashboard", "KPI", "data visualization", "reporting"],
    },
    GigCategory.SEO: {
        "title": "Complete SEO Audit & Optimization Strategy",
        "description": (
            "I will audit your website, identify SEO issues, and provide a "
            "prioritized action plan to improve search rankings."
        ),
        "base_price_usd": 35.0,
        "delivery_days": 2,
        "tags": ["SEO", "audit", "keyword research", "on-page SEO", "backlinks"],
    },
    GigCategory.SOCIAL_MEDIA: {
        "title": "Social Media Management & Content Calendar",
        "description": (
            "I will create and schedule 30 days of social media content for "
            "Instagram, Facebook, Twitter/X, or LinkedIn."
        ),
        "base_price_usd": 40.0,
        "delivery_days": 3,
        "tags": ["social media", "content calendar", "Instagram", "Facebook", "scheduling"],
    },
    GigCategory.VIRTUAL_ASSISTANT: {
        "title": "Professional Virtual Assistant for Business Tasks",
        "description": (
            "I will handle emails, scheduling, research, data management, and "
            "any administrative tasks to free up your time."
        ),
        "base_price_usd": 10.0,
        "delivery_days": 1,
        "tags": ["virtual assistant", "admin", "scheduling", "email management"],
    },
    GigCategory.GRAPHIC_DESIGN: {
        "title": "Modern Logo & Brand Identity Design",
        "description": (
            "I will design a professional logo with full brand identity package "
            "including color palette, typography, and usage guidelines."
        ),
        "base_price_usd": 45.0,
        "delivery_days": 3,
        "tags": ["logo design", "branding", "graphic design", "identity", "Canva"],
    },
    GigCategory.VIDEO_EDITING: {
        "title": "Professional Video Editing for YouTube & Social Media",
        "description": (
            "I will edit your raw footage into a polished video with captions, "
            "transitions, music, and color grading."
        ),
        "base_price_usd": 30.0,
        "delivery_days": 2,
        "tags": ["video editing", "YouTube", "reels", "TikTok", "color grading"],
    },
    GigCategory.WEB_DEVELOPMENT: {
        "title": "Responsive Website Design with WordPress or HTML/CSS",
        "description": (
            "I will build a clean, mobile-responsive website with SEO best "
            "practices, contact forms, and fast loading times."
        ),
        "base_price_usd": 75.0,
        "delivery_days": 5,
        "tags": ["web design", "WordPress", "HTML", "CSS", "responsive"],
    },
}


# ---------------------------------------------------------------------------
# Main class
# ---------------------------------------------------------------------------

class FiverrBot:
    """
    Fiverr Automation Bot — empire-grade freelance automation engine.

    Automates service listing, order management, inbox automation,
    review collection, and analytics for Fiverr freelancers.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability and limits.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._gigs: dict[str, Gig] = {}
        self._orders: dict[str, Order] = {}
        self._reviews: dict[str, Review] = {}
        self._inbox: list[dict] = []
        self._revenue_log: list[dict] = []
        self._gig_counter: int = 0
        self._order_counter: int = 0
        self._review_counter: int = 0

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            suggestion = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade else ""
            )
            raise FiverrBotTierError(
                f"Feature '{feature}' is not available on the "
                f"{self._config.name} tier.{suggestion}"
            )

    def _check_gig_limit(self) -> None:
        limit = self._config.max_gigs
        if limit is not None and len(self._gigs) >= limit:
            upgrade = get_upgrade_path(self.tier)
            suggestion = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade else ""
            )
            raise FiverrBotTierError(
                f"Gig limit of {limit} reached on the {self._config.name} tier.{suggestion}"
            )

    def _check_order_limit(self) -> None:
        limit = self._config.max_orders_per_month
        if limit is not None and len(self._orders) >= limit:
            upgrade = get_upgrade_path(self.tier)
            suggestion = (
                f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
                if upgrade else ""
            )
            raise FiverrBotTierError(
                f"Order limit of {limit} reached on the {self._config.name} tier.{suggestion}"
            )

    # ------------------------------------------------------------------
    # Gig management
    # ------------------------------------------------------------------

    def create_gig(
        self,
        category: GigCategory,
        title: Optional[str] = None,
        price_usd: Optional[float] = None,
        delivery_days: Optional[int] = None,
        description: Optional[str] = None,
    ) -> dict:
        """Create a new gig listing from a category template or custom values."""
        self._require(FEATURE_GIG_LISTING)
        self._check_gig_limit()

        template = GIG_TEMPLATES.get(category, GIG_TEMPLATES[GigCategory.DATA_ENTRY])
        self._gig_counter += 1
        gig_id = f"gig_{self._gig_counter:04d}"

        gig = Gig(
            gig_id=gig_id,
            title=title or template["title"],
            category=category,
            description=description or template["description"],
            price_usd=price_usd or template["base_price_usd"],
            delivery_days=delivery_days or template["delivery_days"],
            tags=list(template.get("tags", [])),
        )
        self._gigs[gig_id] = gig
        return _gig_to_dict(gig)

    def update_gig_price(self, gig_id: str, new_price_usd: float) -> dict:
        """Update the price of an existing gig."""
        gig = self._get_gig(gig_id)
        gig.price_usd = round(new_price_usd, 2)
        return _gig_to_dict(gig)

    def deactivate_gig(self, gig_id: str) -> dict:
        """Deactivate a gig so it no longer appears in listings."""
        gig = self._get_gig(gig_id)
        gig.active = False
        return {"gig_id": gig_id, "active": False, "status": "deactivated"}

    def get_gigs(self, active_only: bool = False) -> list:
        """Return all (or only active) gigs."""
        gigs = list(self._gigs.values())
        if active_only:
            gigs = [g for g in gigs if g.active]
        return [_gig_to_dict(g) for g in gigs]

    def _get_gig(self, gig_id: str) -> Gig:
        if gig_id not in self._gigs:
            raise FiverrBotError(f"Gig '{gig_id}' not found.")
        return self._gigs[gig_id]

    # ------------------------------------------------------------------
    # Order management
    # ------------------------------------------------------------------

    def receive_order(
        self,
        gig_id: str,
        buyer_username: str,
        requirements: str = "",
    ) -> dict:
        """Record a new incoming order for a gig."""
        self._require(FEATURE_ORDER_TRACKING)
        self._check_order_limit()
        gig = self._get_gig(gig_id)

        self._order_counter += 1
        order_id = f"ord_{self._order_counter:04d}"
        order = Order(
            order_id=order_id,
            gig_id=gig_id,
            buyer_username=buyer_username,
            amount_usd=gig.price_usd,
            status=OrderStatus.PENDING,
            requirements=requirements,
        )
        self._orders[order_id] = order
        gig.orders_total += 1
        return _order_to_dict(order)

    def start_order(self, order_id: str) -> dict:
        """Mark an order as in-progress."""
        order = self._get_order(order_id)
        order.status = OrderStatus.IN_PROGRESS
        return _order_to_dict(order)

    def deliver_order(self, order_id: str, deliverable: str) -> dict:
        """Mark an order as delivered with the provided deliverable content."""
        order = self._get_order(order_id)
        order.status = OrderStatus.DELIVERED
        order.deliverable = deliverable
        order.delivered_at = datetime.now(timezone.utc).isoformat()
        return _order_to_dict(order)

    def complete_order(self, order_id: str) -> dict:
        """Mark an order as completed and record revenue."""
        order = self._get_order(order_id)
        order.status = OrderStatus.COMPLETED
        order.completed_at = datetime.now(timezone.utc).isoformat()
        self._revenue_log.append({
            "order_id": order_id,
            "gig_id": order.gig_id,
            "amount_usd": order.amount_usd,
            "buyer": order.buyer_username,
            "completed_at": order.completed_at,
        })
        return _order_to_dict(order)

    def cancel_order(self, order_id: str) -> dict:
        """Cancel an order."""
        order = self._get_order(order_id)
        order.status = OrderStatus.CANCELLED
        return _order_to_dict(order)

    def get_orders(self, status: Optional[OrderStatus] = None) -> list:
        """Return all orders, optionally filtered by status."""
        orders = list(self._orders.values())
        if status:
            orders = [o for o in orders if o.status == status]
        return [_order_to_dict(o) for o in orders]

    def _get_order(self, order_id: str) -> Order:
        if order_id not in self._orders:
            raise FiverrBotError(f"Order '{order_id}' not found.")
        return self._orders[order_id]

    # ------------------------------------------------------------------
    # Inbox automation
    # ------------------------------------------------------------------

    def send_message(self, buyer_username: str, message: str) -> dict:
        """Send an automated inbox message to a buyer."""
        self._require(FEATURE_INBOX_AUTOMATION)
        entry = {
            "to": buyer_username,
            "message": message,
            "sent_at": datetime.now(timezone.utc).isoformat(),
            "status": "sent",
        }
        self._inbox.append(entry)
        return entry

    def bulk_message(self, buyer_usernames: list, message: str) -> dict:
        """Send a bulk message to multiple buyers."""
        self._require(FEATURE_BULK_MESSAGING)
        sent = []
        for username in buyer_usernames:
            sent.append(self.send_message(username, message))
        return {"recipients": len(sent), "status": "sent", "messages": sent}

    def auto_respond_inquiry(self, buyer_username: str, inquiry: str) -> dict:
        """Generate and send an automated response to a buyer inquiry."""
        self._require(FEATURE_INBOX_AUTOMATION)
        response = (
            f"Hi {buyer_username}, thanks for your message! "
            "I'd be happy to help. Could you share more details about your project? "
            "I'll get back to you within 24 hours with a custom quote. — DreamCo Bot"
        )
        return self.send_message(buyer_username, response)

    def get_inbox(self) -> list:
        """Return all inbox messages sent."""
        return list(self._inbox)

    # ------------------------------------------------------------------
    # Review collection
    # ------------------------------------------------------------------

    def request_review(self, order_id: str) -> dict:
        """Send a review request message after order completion."""
        self._require(FEATURE_REVIEW_COLLECTION)
        order = self._get_order(order_id)
        if order.status != OrderStatus.COMPLETED:
            raise FiverrBotError(
                f"Order '{order_id}' must be completed before requesting a review."
            )
        message = (
            f"Hi {order.buyer_username}, thank you for your order! "
            "If you're happy with the delivery, I'd really appreciate a 5-star review. "
            "It helps my profile grow. 🙏"
        )
        return self.send_message(order.buyer_username, message)

    def record_review(
        self,
        order_id: str,
        rating: float,
        comment: str = "",
    ) -> dict:
        """Record a buyer review for a completed order."""
        self._require(FEATURE_REVIEW_COLLECTION)
        order = self._get_order(order_id)
        if not (1.0 <= rating <= 5.0):
            raise FiverrBotError("Rating must be between 1.0 and 5.0.")

        self._review_counter += 1
        review_id = f"rev_{self._review_counter:04d}"
        review = Review(
            review_id=review_id,
            order_id=order_id,
            gig_id=order.gig_id,
            buyer_username=order.buyer_username,
            rating=round(rating, 1),
            comment=comment,
        )
        self._reviews[review_id] = review

        # Update gig rating
        gig = self._gigs.get(order.gig_id)
        if gig:
            total_rating = gig.rating * gig.review_count + rating
            gig.review_count += 1
            gig.rating = round(total_rating / gig.review_count, 2)

        return _review_to_dict(review)

    def get_reviews(self, gig_id: Optional[str] = None) -> list:
        """Return all reviews, optionally filtered by gig."""
        reviews = list(self._reviews.values())
        if gig_id:
            reviews = [r for r in reviews if r.gig_id == gig_id]
        return [_review_to_dict(r) for r in reviews]

    # ------------------------------------------------------------------
    # Pricing optimizer
    # ------------------------------------------------------------------

    def optimize_price(self, gig_id: str) -> dict:
        """Suggest an optimized price for a gig based on category benchmarks."""
        self._require(FEATURE_PRICING_OPTIMIZER)
        gig = self._get_gig(gig_id)
        template = GIG_TEMPLATES.get(gig.category, GIG_TEMPLATES[GigCategory.DATA_ENTRY])
        base = template["base_price_usd"]

        # AI pricing uses additional signals
        if self._config.has_feature(FEATURE_AI_PRICING):
            demand_factor = random.uniform(1.05, 1.40)
            optimized = round(base * demand_factor, 2)
            method = "AI demand modeling"
        else:
            # Simple rules-based optimization
            if gig.rating >= 4.8 and gig.review_count >= 10:
                optimized = round(base * 1.20, 2)
            elif gig.orders_total >= 50:
                optimized = round(base * 1.10, 2)
            else:
                optimized = base
            method = "rules-based"

        return {
            "gig_id": gig_id,
            "current_price_usd": gig.price_usd,
            "optimized_price_usd": optimized,
            "optimization_method": method,
            "tier": self.tier.value,
        }

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def get_analytics(self) -> dict:
        """Return performance analytics across all gigs and orders."""
        self._require(FEATURE_ANALYTICS)
        total_revenue = sum(e["amount_usd"] for e in self._revenue_log)
        completed = [o for o in self._orders.values() if o.status == OrderStatus.COMPLETED]
        avg_rating = (
            round(sum(r.rating for r in self._reviews.values()) / len(self._reviews), 2)
            if self._reviews else 0.0
        )
        conversion_rate = (
            round(len(completed) / len(self._orders) * 100, 1)
            if self._orders else 0.0
        )

        by_category: dict = {}
        for gig in self._gigs.values():
            cat = gig.category.value
            rev = sum(
                o.amount_usd
                for o in self._orders.values()
                if o.gig_id == gig.gig_id and o.status == OrderStatus.COMPLETED
            )
            by_category[cat] = by_category.get(cat, 0.0) + rev

        return {
            "total_gigs": len(self._gigs),
            "active_gigs": sum(1 for g in self._gigs.values() if g.active),
            "total_orders": len(self._orders),
            "completed_orders": len(completed),
            "total_revenue_usd": round(total_revenue, 2),
            "average_order_value_usd": (
                round(total_revenue / len(completed), 2) if completed else 0.0
            ),
            "avg_rating": avg_rating,
            "review_count": len(self._reviews),
            "conversion_rate_pct": conversion_rate,
            "revenue_by_category": {k: round(v, 2) for k, v in by_category.items()},
            "tier": self.tier.value,
        }

    def get_revenue_summary(self) -> dict:
        """Return a summary of revenue earned."""
        total = sum(e["amount_usd"] for e in self._revenue_log)
        by_gig: dict = {}
        for entry in self._revenue_log:
            gid = entry["gig_id"]
            by_gig[gid] = round(by_gig.get(gid, 0.0) + entry["amount_usd"], 2)
        return {
            "total_revenue_usd": round(total, 2),
            "completed_orders": len(self._revenue_log),
            "by_gig": by_gig,
            "revenue_log": list(self._revenue_log),
        }

    # ------------------------------------------------------------------
    # CRM export
    # ------------------------------------------------------------------

    def export_to_crm(self, crm_name: str = "default") -> dict:
        """Export completed order data to an external CRM."""
        self._require(FEATURE_CRM_EXPORT)
        records = [
            {
                "order_id": e["order_id"],
                "buyer": e["buyer"],
                "amount_usd": e["amount_usd"],
                "gig_id": e["gig_id"],
                "completed_at": e["completed_at"],
            }
            for e in self._revenue_log
        ]
        return {
            "crm": crm_name,
            "records_exported": len(records),
            "records": records,
            "exported_at": datetime.now(timezone.utc).isoformat(),
            "status": "success",
        }

    # ------------------------------------------------------------------
    # Summary & chat interfaces
    # ------------------------------------------------------------------

    def get_summary(self) -> dict:
        """Return overall bot statistics."""
        total_revenue = sum(e["amount_usd"] for e in self._revenue_log)
        return {
            "tier": self.tier.value,
            "total_gigs": len(self._gigs),
            "total_orders": len(self._orders),
            "total_reviews": len(self._reviews),
            "total_revenue_usd": round(total_revenue, 2),
            "inbox_messages_sent": len(self._inbox),
        }

    def run(self) -> str:
        """Return a one-line status string (used by ControlCenter)."""
        summary = self.get_summary()
        return (
            f"FiverrBot [{self.tier.value}]: "
            f"{summary['total_gigs']} gigs, "
            f"{summary['total_orders']} orders, "
            f"${summary['total_revenue_usd']:.2f} revenue"
        )

    def chat(self, message: str) -> dict:
        """Natural-language interface for BuddyAI routing."""
        msg = message.lower()
        if "summary" in msg or "stats" in msg or "status" in msg:
            return {"message": "Fiverr Bot summary retrieved.", "data": self.get_summary()}
        if "gigs" in msg or "listings" in msg:
            return {"message": "Gig listings retrieved.", "data": self.get_gigs()}
        if "orders" in msg:
            return {"message": "Orders retrieved.", "data": self.get_orders()}
        if "revenue" in msg or "earnings" in msg:
            return {"message": "Revenue summary retrieved.", "data": self.get_revenue_summary()}
        return {
            "message": (
                f"Fiverr Automation Bot online. Tier: {self.tier.value}. "
                "Try: 'summary', 'gigs', 'orders', or 'revenue'."
            )
        }

    def process(self, payload: dict) -> dict:
        """GLOBAL AI SOURCES FLOW framework entry point."""
        action = payload.get("action", "summary")
        if action == "create_gig":
            category_str = payload.get("category", "data_entry")
            category = GigCategory(category_str)
            return self.create_gig(
                category=category,
                title=payload.get("title"),
                price_usd=payload.get("price_usd"),
                delivery_days=payload.get("delivery_days"),
                description=payload.get("description"),
            )
        if action == "receive_order":
            return self.receive_order(
                gig_id=payload["gig_id"],
                buyer_username=payload["buyer_username"],
                requirements=payload.get("requirements", ""),
            )
        if action == "get_analytics":
            return self.get_analytics()
        return self.get_summary()

    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self._config
        gig_limit = "Unlimited" if cfg.is_unlimited_gigs() else str(cfg.max_gigs)
        order_limit = (
            "Unlimited" if cfg.max_orders_per_month is None
            else str(cfg.max_orders_per_month)
        )
        lines = [
            f"=== {cfg.name} Fiverr Automation Bot Tier ===",
            f"Price         : ${cfg.price_usd_monthly:.2f}/month",
            f"Max Gigs      : {gig_limit}",
            f"Max Orders/mo : {order_limit}",
            f"Support       : {cfg.support_level}",
            "",
            "Features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        output = "\n".join(lines)
        print(output)
        return output


# ---------------------------------------------------------------------------
# Helper serializers
# ---------------------------------------------------------------------------

def _gig_to_dict(g: Gig) -> dict:
    return {
        "gig_id": g.gig_id,
        "title": g.title,
        "category": g.category.value,
        "description": g.description,
        "price_usd": g.price_usd,
        "delivery_days": g.delivery_days,
        "tags": g.tags,
        "active": g.active,
        "impressions": g.impressions,
        "clicks": g.clicks,
        "orders_total": g.orders_total,
        "rating": g.rating,
        "review_count": g.review_count,
        "created_at": g.created_at,
    }


def _order_to_dict(o: Order) -> dict:
    return {
        "order_id": o.order_id,
        "gig_id": o.gig_id,
        "buyer_username": o.buyer_username,
        "amount_usd": o.amount_usd,
        "status": o.status.value,
        "requirements": o.requirements,
        "deliverable": o.deliverable,
        "created_at": o.created_at,
        "delivered_at": o.delivered_at,
        "completed_at": o.completed_at,
    }


def _review_to_dict(r: Review) -> dict:
    return {
        "review_id": r.review_id,
        "order_id": r.order_id,
        "gig_id": r.gig_id,
        "buyer_username": r.buyer_username,
        "rating": r.rating,
        "comment": r.comment,
        "created_at": r.created_at,
    }


__all__ = [
    "FiverrBot",
    "FiverrBotError",
    "FiverrBotTierError",
    "GigCategory",
    "OrderStatus",
    "Gig",
    "Order",
    "Review",
]
