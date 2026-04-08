"""
Lead Generation Bot

Collects, scores, and manages leads with optional Stripe payment integration
for selling lead packages or charging for premium lead collection services.

Tier-aware:
  - FREE:       Collect up to 50 leads/month, no payment features.
  - PRO:        Collect up to 2 000 leads/month, sell lead packages via Stripe.
  - ENTERPRISE: Unlimited leads, full Stripe integration, webhook automation.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Optional

from bots.lead_gen_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_STRIPE_PAYMENTS,
    FEATURE_LEAD_PACKAGES,
    FEATURE_WEBHOOK_NOTIFICATIONS,
    FEATURE_LEAD_SCORING,
    FEATURE_CRM_EXPORT,
)
from bots.stripe_integration.stripe_client import StripeClient, StripeClientError
from framework import GlobalAISourcesFlow  # noqa: F401


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class LeadGenBotError(Exception):
    """Base exception for Lead Gen Bot errors."""


class LeadGenBotTierError(LeadGenBotError):
    """Raised when a feature requires a higher tier."""


class LeadGenBotLimitError(LeadGenBotError):
    """Raised when the monthly lead limit is exceeded."""


# ---------------------------------------------------------------------------
# Lead data model
# ---------------------------------------------------------------------------

@dataclass
class Lead:
    """Represents a collected lead."""

    lead_id: str = field(default_factory=lambda: f"lead_{uuid.uuid4().hex[:12]}")
    name: str = ""
    email: str = ""
    phone: str = ""
    company: str = ""
    industry: str = ""
    location: str = ""
    interest: str = ""
    source: str = "direct"
    score: float = 0.0
    collected_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    paid: bool = False
    payment_id: Optional[str] = None


# ---------------------------------------------------------------------------
# Lead packages for Stripe checkout
# ---------------------------------------------------------------------------

LEAD_PACKAGES = {
    "starter_pack": {
        "name": "Starter Lead Pack (25 leads)",
        "amount_cents": 4900,
        "currency": "usd",
        "lead_count": 25,
        "description": "25 verified leads from your target niche.",
    },
    "growth_pack": {
        "name": "Growth Lead Pack (100 leads)",
        "amount_cents": 14900,
        "currency": "usd",
        "lead_count": 100,
        "description": "100 scored and enriched leads with contact details.",
    },
    "enterprise_pack": {
        "name": "Enterprise Lead Pack (500 leads)",
        "amount_cents": 49900,
        "currency": "usd",
        "lead_count": 500,
        "description": "500 premium leads with full enrichment and CRM export.",
    },
}


# ---------------------------------------------------------------------------
# Main bot class
# ---------------------------------------------------------------------------

class LeadGenBot:
    """
    Tier-aware lead generation bot with Stripe payment integration.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    stripe_client : StripeClient | None
        Optional injected StripeClient (useful for testing).
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        stripe_client: Optional[StripeClient] = None,
    ) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self._stripe = stripe_client or StripeClient()
        self._leads: list[Lead] = []
        self._monthly_count: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            msg = f"Feature '{feature}' is not available on the {self.config.name} tier."
            if upgrade:
                msg += f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly:.0f}/mo)."
            raise LeadGenBotTierError(msg)

    def _check_monthly_limit(self) -> None:
        if not self.config.is_unlimited():
            assert self.config.max_leads_per_month is not None
            if self._monthly_count >= self.config.max_leads_per_month:
                raise LeadGenBotLimitError(
                    f"Monthly lead limit of {self.config.max_leads_per_month} reached on "
                    f"the {self.config.name} tier. Upgrade for more leads."
                )

    @staticmethod
    def _score_lead(lead: Lead) -> float:
        """Simple scoring heuristic based on data completeness."""
        score = 0.0
        if lead.name:
            score += 20
        if lead.email:
            score += 30
        if lead.phone:
            score += 20
        if lead.company:
            score += 15
        if lead.location:
            score += 10
        if lead.interest:
            score += 5
        return round(score, 1)

    # ------------------------------------------------------------------
    # Lead collection
    # ------------------------------------------------------------------

    def collect_lead(
        self,
        name: str,
        email: str,
        phone: str = "",
        company: str = "",
        industry: str = "",
        location: str = "",
        interest: str = "",
        source: str = "direct",
    ) -> Lead:
        """
        Collect a new lead and store it.

        Parameters
        ----------
        name : str
            Lead's full name.
        email : str
            Lead's email address.
        phone : str
            Optional phone number.
        company : str
            Optional company name.
        industry : str
            Optional industry.
        location : str
            Optional location.
        interest : str
            What the lead is interested in.
        source : str
            Where the lead came from (e.g. ``"website"``, ``"chatbot"``).

        Returns
        -------
        Lead
            The newly collected lead with a quality score.
        """
        self._check_monthly_limit()

        lead = Lead(
            name=name,
            email=email,
            phone=phone,
            company=company,
            industry=industry,
            location=location,
            interest=interest,
            source=source,
        )

        if self.config.has_feature(FEATURE_LEAD_SCORING):
            lead.score = self._score_lead(lead)

        self._leads.append(lead)
        self._monthly_count += 1
        return lead

    def get_leads(
        self,
        min_score: float = 0.0,
        industry: Optional[str] = None,
        paid_only: bool = False,
    ) -> list[Lead]:
        """
        Return collected leads, optionally filtered.

        Parameters
        ----------
        min_score : float
            Minimum quality score (0–100).
        industry : str | None
            Filter by industry.
        paid_only : bool
            Return only leads whose package has been paid for.

        Returns
        -------
        list[Lead]
        """
        results = self._leads
        if min_score > 0:
            results = [l for l in results if l.score >= min_score]
        if industry:
            results = [l for l in results if l.industry.lower() == industry.lower()]
        if paid_only:
            results = [l for l in results if l.paid]
        return results

    def get_lead_count(self) -> int:
        """Return total leads collected this month."""
        return self._monthly_count

    def reset_monthly_count(self) -> None:
        """Reset the monthly counter (call at the start of each billing period)."""
        self._monthly_count = 0

    # ------------------------------------------------------------------
    # Stripe — lead packages
    # ------------------------------------------------------------------

    def create_lead_package_checkout(
        self,
        package_key: str,
        customer_email: str,
        success_url: str,
        cancel_url: str,
    ) -> dict:
        """
        Create a Stripe Checkout Session for purchasing a lead package.

        Parameters
        ----------
        package_key : str
            One of ``"starter_pack"``, ``"growth_pack"``, ``"enterprise_pack"``.
        customer_email : str
            Buyer's email address.
        success_url : str
            Redirect URL on successful payment.
        cancel_url : str
            Redirect URL if the buyer cancels.

        Returns
        -------
        dict
            ``session_id``, ``checkout_url``, ``package``, ``amount_usd``.

        Raises
        ------
        LeadGenBotTierError
            If the PRO or ENTERPRISE tier is not active.
        """
        self._require_feature(FEATURE_STRIPE_PAYMENTS)
        self._require_feature(FEATURE_LEAD_PACKAGES)

        if package_key not in LEAD_PACKAGES:
            raise LeadGenBotError(
                f"Unknown package '{package_key}'. "
                f"Available: {list(LEAD_PACKAGES)}"
            )

        pkg = LEAD_PACKAGES[package_key]

        session = self._stripe.create_checkout_session(
            amount_cents=pkg["amount_cents"],
            currency=pkg["currency"],
            product_name=pkg["name"],
            success_url=success_url,
            cancel_url=cancel_url,
            customer_email=customer_email,
            metadata={"package_key": package_key, "bot": "lead_gen_bot"},
        )

        return {
            "session_id": session["id"],
            "checkout_url": session["url"],
            "package": pkg["name"],
            "lead_count": pkg["lead_count"],
            "amount_usd": pkg["amount_cents"] / 100,
            "currency": pkg["currency"],
        }

    def create_payment_link(
        self,
        package_key: str,
    ) -> dict:
        """
        Create a shareable Stripe Payment Link for a lead package.

        Returns
        -------
        dict
            ``link_id``, ``url``, ``package``, ``amount_usd``.
        """
        self._require_feature(FEATURE_STRIPE_PAYMENTS)

        if package_key not in LEAD_PACKAGES:
            raise LeadGenBotError(f"Unknown package '{package_key}'.")

        pkg = LEAD_PACKAGES[package_key]
        link = self._stripe.create_payment_link(
            amount_cents=pkg["amount_cents"],
            currency=pkg["currency"],
            product_name=pkg["name"],
            metadata={"bot": "lead_gen_bot", "package_key": package_key},
        )

        return {
            "link_id": link["id"],
            "url": link["url"],
            "package": pkg["name"],
            "lead_count": pkg["lead_count"],
            "amount_usd": pkg["amount_cents"] / 100,
        }

    def mark_lead_paid(self, lead_id: str, payment_id: str) -> bool:
        """
        Mark a lead as paid after a successful Stripe payment.

        Returns
        -------
        bool
            True if the lead was found and updated.
        """
        for lead in self._leads:
            if lead.lead_id == lead_id:
                lead.paid = True
                lead.payment_id = payment_id
                return True
        return False

    # ------------------------------------------------------------------
    # CRM export
    # ------------------------------------------------------------------

    def export_leads(self, format_type: str = "json") -> dict:
        """
        Export collected leads in the requested format.

        Parameters
        ----------
        format_type : str
            ``"json"`` or ``"csv"``.

        Returns
        -------
        dict
            ``format``, ``count``, ``leads``.
        """
        self._require_feature(FEATURE_CRM_EXPORT)

        leads_data = [
            {
                "lead_id": l.lead_id,
                "name": l.name,
                "email": l.email,
                "phone": l.phone,
                "company": l.company,
                "industry": l.industry,
                "location": l.location,
                "interest": l.interest,
                "source": l.source,
                "score": l.score,
                "collected_at": l.collected_at,
                "paid": l.paid,
            }
            for l in self._leads
        ]

        if format_type.lower() == "csv":
            if not leads_data:
                csv_content = "lead_id,name,email,phone,company,industry,location,interest,source,score,collected_at,paid\n"
            else:
                headers = list(leads_data[0].keys())
                rows = [",".join(str(v) for v in row.values()) for row in leads_data]
                csv_content = ",".join(headers) + "\n" + "\n".join(rows)
            return {"format": "csv", "count": len(leads_data), "content": csv_content}

        return {"format": "json", "count": len(leads_data), "leads": leads_data}

    # ------------------------------------------------------------------
    # Tier description
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Return a human-readable tier summary."""
        cfg = self.config
        limit = "Unlimited" if cfg.is_unlimited() else f"{cfg.max_leads_per_month:,}"
        lines = [
            f"Lead Gen Bot — {cfg.name} Tier",
            f"  Price       : ${cfg.price_usd_monthly:.2f}/month",
            f"  Leads/month : {limit}",
            f"  Support     : {cfg.support_level}",
            f"  Features    : {', '.join(cfg.features)}",
        ]
        upgrade = get_upgrade_path(self.tier)
        if upgrade:
            lines.append(
                f"  Upgrade to  : {upgrade.name} (${upgrade.price_usd_monthly:.0f}/mo)"
            )
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        BuddyAI-compatible chat interface.

        Parameters
        ----------
        message : str
            Incoming message text.

        Returns
        -------
        dict
            ``response``, ``bot_name``, ``tier``.
        """
        msg_lower = message.lower()

        if "tier" in msg_lower or "plan" in msg_lower:
            response = self.describe_tier()
        elif "package" in msg_lower or "buy" in msg_lower or "purchase" in msg_lower:
            pkg_list = "\n".join(
                f"  {k}: {v['name']} — ${v['amount_cents']/100:.0f} ({v['lead_count']} leads)"
                for k, v in LEAD_PACKAGES.items()
            )
            response = f"Available lead packages:\n{pkg_list}"
        elif "lead" in msg_lower and "count" in msg_lower:
            response = f"You have collected {self.get_lead_count()} leads this month."
        elif "collect" in msg_lower or "add" in msg_lower:
            response = (
                "To collect a lead, call collect_lead(name, email, ...) "
                "or use the chatbot form to submit lead details."
            )
        elif "export" in msg_lower:
            if self.config.has_feature(FEATURE_CRM_EXPORT):
                response = "Use export_leads('json') or export_leads('csv') to download your leads."
            else:
                response = "CRM export is available on Pro and Enterprise tiers."
        elif "stripe" in msg_lower or "payment" in msg_lower:
            if self.config.has_feature(FEATURE_STRIPE_PAYMENTS):
                response = (
                    "Stripe payments are active. Use create_lead_package_checkout() "
                    "or create_payment_link() to sell lead packages."
                )
            else:
                response = "Stripe payments are available on Pro and Enterprise tiers."
        else:
            response = (
                f"Hello from Lead Gen Bot ({self.config.name} tier)! "
                "I collect, score, and export leads. "
                "Ask me about packages, plans, or how to collect leads."
            )

        return {
            "response": response,
            "bot_name": "lead_gen_bot",
            "tier": self.tier.value,
        }
