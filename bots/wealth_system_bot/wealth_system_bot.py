"""
DreamCo Global Wealth System Bot — Main Module

Manages Wealth Hubs, treasury operations, governance voting, automated
income/asset/commerce/finance bots, dividend distribution, KYC compliance,
DreamCoin staking, and advanced analytics.

Tier-aware: FREE can join hubs and vote; PRO can create hubs (up to 3) and
run Income + Asset bots; ENTERPRISE unlocks all bots, unlimited hubs,
DreamCoin staking, and advanced analytics.

Adheres to the DreamCo bots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import sys
import os
import uuid
import random
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.wealth_system_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    FEATURE_CREATE_HUB,
    FEATURE_VIEW_TREASURY,
    FEATURE_INCOME_BOTS,
    FEATURE_ASSET_BOTS,
    FEATURE_COMMERCE_BOTS,
    FEATURE_FINANCE_BOTS,
    FEATURE_DIVIDEND_TRACKING,
    FEATURE_ASSET_ALLOCATION,
    FEATURE_DREAMCOIN_STAKING,
    FEATURE_ADVANCED_ANALYTICS,
    FEATURE_FULL_GOVERNANCE,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class WealthSystemBotError(Exception):
    """Base exception for Wealth System Bot errors."""


class WealthSystemBotTierError(WealthSystemBotError):
    """Raised when a feature is not available on the current tier."""


class WealthSystemBotNotFoundError(WealthSystemBotError):
    """Raised when a requested resource is not found."""


class WealthSystemBotValidationError(WealthSystemBotError):
    """Raised for invalid input (e.g. allocations that don't sum to 100)."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class BotType(Enum):
    INCOME = "income"
    ASSET = "asset"
    COMMERCE = "commerce"
    FINANCE = "finance"


class IncomeBot(Enum):
    REFERRAL = "referral"
    AFFILIATE = "affiliate"
    LEAD_GENERATION = "lead_generation"


class AssetBot(Enum):
    REAL_ESTATE_DEALS = "real_estate_deals"
    FORECLOSURE = "foreclosure"
    SECTION_8_RENTAL = "section_8_rental"


class CommerceBot(Enum):
    AMAZON_ARBITRAGE = "amazon_arbitrage"
    SHOPIFY_ARBITRAGE = "shopify_arbitrage"
    DROPSHIPPING = "dropshipping"


class FinanceBot(Enum):
    STOCK_TRADING = "stock_trading"
    CRYPTO_INVESTMENT = "crypto_investment"
    GRANT_FINDER = "grant_finder"


class AssetTier(Enum):
    STABILITY = "stability"    # gold / silver / treasury
    GROWTH = "growth"          # stocks / ETFs / real estate
    HIGH_GROWTH = "high_growth"  # crypto / startups / AI


class GovernanceVoteType(Enum):
    INVESTMENT = "investment"
    PAYOUT_SCHEDULE = "payout_schedule"
    RISK_LEVEL = "risk_level"
    BOT_ACTIVATION = "bot_activation"


class PayoutMode(Enum):
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    COMPOUNDING = "compounding"


class ComplianceStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Member:
    member_id: str
    name: str
    email: str
    contribution_usd: float
    ownership_pct: float = 0.0
    reputation_score: float = 100.0
    join_date: str = field(default_factory=_now_iso)
    dreamcoin_balance: float = 0.0
    kyc_status: ComplianceStatus = ComplianceStatus.PENDING


@dataclass
class WealthHub:
    hub_id: str
    name: str
    owner_id: str
    members: dict = field(default_factory=dict)       # member_id -> Member
    treasury_usd: float = 0.0
    asset_allocation: dict = field(
        default_factory=lambda: {"stability": 34, "growth": 33, "high_growth": 33}
    )
    active_bots: dict = field(default_factory=dict)   # "bot_type:sub_type" -> BotEarnings
    governance_votes: dict = field(default_factory=dict)  # vote_id -> GovernanceVote
    payout_mode: PayoutMode = PayoutMode.MONTHLY
    dividends_paid_usd: float = 0.0
    created_at: str = field(default_factory=_now_iso)


@dataclass
class GovernanceVote:
    vote_id: str
    hub_id: str
    vote_type: GovernanceVoteType
    proposal: str
    options: list
    votes_cast: dict = field(default_factory=dict)    # member_id -> option
    is_resolved: bool = False
    result: Optional[str] = None


@dataclass
class BotEarnings:
    bot_type: BotType
    sub_type: str
    earnings_usd: float = 0.0
    runs: int = 0
    last_run_at: Optional[str] = None


@dataclass
class ComplianceRecord:
    record_id: str
    member_id: str
    check_type: str
    status: ComplianceStatus = ComplianceStatus.PENDING
    notes: str = ""
    checked_at: str = field(default_factory=_now_iso)


@dataclass
class DividendPayout:
    payout_id: str
    hub_id: str
    member_id: str
    amount_usd: float
    payout_date: str = field(default_factory=_now_iso)
    mode: PayoutMode = PayoutMode.MONTHLY


# ---------------------------------------------------------------------------
# Helpers — bot type → required feature + valid sub-types
# ---------------------------------------------------------------------------

_BOT_FEATURE = {
    BotType.INCOME: FEATURE_INCOME_BOTS,
    BotType.ASSET: FEATURE_ASSET_BOTS,
    BotType.COMMERCE: FEATURE_COMMERCE_BOTS,
    BotType.FINANCE: FEATURE_FINANCE_BOTS,
}

_BOT_SUB_TYPES: dict[BotType, type] = {
    BotType.INCOME: IncomeBot,
    BotType.ASSET: AssetBot,
    BotType.COMMERCE: CommerceBot,
    BotType.FINANCE: FinanceBot,
}


MIN_BOT_EARNINGS_USD: float = 10.0
MAX_BOT_EARNINGS_USD: float = 500.0


def _bot_key(bot_type: BotType, sub_type: str) -> str:
    return f"{bot_type.value}:{sub_type}"


# ---------------------------------------------------------------------------
# Main Bot Class
# ---------------------------------------------------------------------------

class WealthSystemBot:
    """
    DreamCo Global Wealth System Bot.

    Manages collective Wealth Hubs where members pool capital, activate
    automated bots, govern decisions, and distribute dividends —
    powered by the GLOBAL AI SOURCES FLOW framework.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier: Tier = tier
        self._config: TierConfig = get_tier_config(tier)
        self._hubs: dict[str, WealthHub] = {}
        self._compliance_records: dict[str, ComplianceRecord] = {}  # record_id -> record
        self._dreamcoin_staking: dict[str, float] = {}              # member_id -> staked

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            raise WealthSystemBotTierError(
                f"Feature '{feature}' requires a higher tier than '{self.tier.value}'."
            )

    def _get_hub(self, hub_id: str) -> WealthHub:
        if hub_id not in self._hubs:
            raise WealthSystemBotNotFoundError(f"Wealth Hub '{hub_id}' not found.")
        return self._hubs[hub_id]

    def _get_member(self, hub: WealthHub, member_id: str) -> Member:
        if member_id not in hub.members:
            raise WealthSystemBotNotFoundError(
                f"Member '{member_id}' not found in hub '{hub.hub_id}'."
            )
        return hub.members[member_id]

    def _recalc_ownership(self, hub: WealthHub) -> None:
        """Recompute ownership_pct for every member based on contribution_usd."""
        total = sum(m.contribution_usd for m in hub.members.values())
        for member in hub.members.values():
            member.ownership_pct = (
                round(member.contribution_usd / total * 100, 6) if total > 0 else 0.0
            )

    # ------------------------------------------------------------------
    # Wealth Hub Management
    # ------------------------------------------------------------------

    def create_hub(
        self,
        owner_id: str,
        name: str,
        payout_mode: PayoutMode = PayoutMode.MONTHLY,
    ) -> WealthHub:
        """Create a new Wealth Hub (PRO+)."""
        self._require_feature(FEATURE_CREATE_HUB)
        max_hubs = self._config.max_hubs
        if max_hubs is not None:
            owner_hubs = [h for h in self._hubs.values() if h.owner_id == owner_id]
            if len(owner_hubs) >= max_hubs:
                raise WealthSystemBotTierError(
                    f"Hub limit reached ({max_hubs}). Upgrade to ENTERPRISE for unlimited hubs."
                )
        hub = WealthHub(
            hub_id=str(uuid.uuid4()),
            name=name,
            owner_id=owner_id,
            payout_mode=payout_mode,
        )
        self._hubs[hub.hub_id] = hub
        return hub

    def get_hub(self, hub_id: str) -> WealthHub:
        return self._get_hub(hub_id)

    def list_hubs(self, owner_id: Optional[str] = None) -> list[WealthHub]:
        hubs = list(self._hubs.values())
        if owner_id is not None:
            hubs = [h for h in hubs if h.owner_id == owner_id]
        return hubs

    def add_member(
        self,
        hub_id: str,
        member_id: str,
        name: str,
        email: str,
        contribution_usd: float,
    ) -> Member:
        """Add a member to a Wealth Hub and recalculate ownership."""
        hub = self._get_hub(hub_id)
        if member_id in hub.members:
            raise WealthSystemBotValidationError(
                f"Member '{member_id}' already exists in hub '{hub_id}'."
            )
        if contribution_usd < 0:
            raise WealthSystemBotValidationError("contribution_usd must be non-negative.")
        member = Member(
            member_id=member_id,
            name=name,
            email=email,
            contribution_usd=contribution_usd,
        )
        hub.members[member_id] = member
        hub.treasury_usd += contribution_usd
        self._recalc_ownership(hub)
        return member

    def get_member(self, hub_id: str, member_id: str) -> Member:
        hub = self._get_hub(hub_id)
        return self._get_member(hub, member_id)

    # ------------------------------------------------------------------
    # Treasury Management
    # ------------------------------------------------------------------

    def deposit(self, hub_id: str, member_id: str, amount_usd: float) -> dict:
        """Deposit funds; update treasury and recalculate all ownership percentages."""
        if amount_usd <= 0:
            raise WealthSystemBotValidationError("Deposit amount must be positive.")
        hub = self._get_hub(hub_id)
        member = self._get_member(hub, member_id)
        member.contribution_usd += amount_usd
        hub.treasury_usd += amount_usd
        self._recalc_ownership(hub)
        return {
            "hub_id": hub_id,
            "member_id": member_id,
            "deposited_usd": amount_usd,
            "treasury_usd": hub.treasury_usd,
            "ownership_pct": member.ownership_pct,
        }

    def get_treasury_snapshot(self, hub_id: str) -> dict:
        """Return treasury balance, per-member ownership, and asset breakdown (FREE+)."""
        self._require_feature(FEATURE_VIEW_TREASURY)
        hub = self._get_hub(hub_id)
        members_info = {
            mid: {
                "name": m.name,
                "contribution_usd": m.contribution_usd,
                "ownership_pct": m.ownership_pct,
            }
            for mid, m in hub.members.items()
        }
        return {
            "hub_id": hub_id,
            "treasury_usd": hub.treasury_usd,
            "members": members_info,
            "asset_breakdown": self.get_asset_breakdown(hub_id),
            "payout_mode": hub.payout_mode.value,
            "dividends_paid_usd": hub.dividends_paid_usd,
        }

    def allocate_assets(
        self,
        hub_id: str,
        stability_pct: float,
        growth_pct: float,
        high_growth_pct: float,
    ) -> dict:
        """Set asset allocation percentages; must sum to 100 (PRO+)."""
        self._require_feature(FEATURE_ASSET_ALLOCATION)
        total = stability_pct + growth_pct + high_growth_pct
        if abs(total - 100) > 0.001:
            raise WealthSystemBotValidationError(
                f"Allocation percentages must sum to 100 (got {total})."
            )
        hub = self._get_hub(hub_id)
        hub.asset_allocation = {
            "stability": stability_pct,
            "growth": growth_pct,
            "high_growth": high_growth_pct,
        }
        return {"hub_id": hub_id, "asset_allocation": hub.asset_allocation}

    def distribute_dividends(self, hub_id: str, profit_usd: float) -> list[DividendPayout]:
        """Distribute profit proportionally to ownership_pct (PRO+)."""
        self._require_feature(FEATURE_DIVIDEND_TRACKING)
        if profit_usd <= 0:
            raise WealthSystemBotValidationError("profit_usd must be positive.")
        hub = self._get_hub(hub_id)
        payouts: list[DividendPayout] = []
        for member in hub.members.values():
            amount = round(profit_usd * member.ownership_pct / 100, 4)
            payout = DividendPayout(
                payout_id=str(uuid.uuid4()),
                hub_id=hub_id,
                member_id=member.member_id,
                amount_usd=amount,
                mode=hub.payout_mode,
            )
            payouts.append(payout)
        hub.dividends_paid_usd += profit_usd
        return payouts

    # ------------------------------------------------------------------
    # Governance / Voting
    # ------------------------------------------------------------------

    def create_vote(
        self,
        hub_id: str,
        proposer_id: str,
        vote_type: GovernanceVoteType,
        proposal: str,
        options: list,
    ) -> GovernanceVote:
        """Create a governance vote in a hub."""
        hub = self._get_hub(hub_id)
        if proposer_id not in hub.members:
            raise WealthSystemBotNotFoundError(
                f"Proposer '{proposer_id}' is not a member of hub '{hub_id}'."
            )
        if not options:
            raise WealthSystemBotValidationError("Vote must have at least one option.")
        vote = GovernanceVote(
            vote_id=str(uuid.uuid4()),
            hub_id=hub_id,
            vote_type=vote_type,
            proposal=proposal,
            options=options,
        )
        hub.governance_votes[vote.vote_id] = vote
        return vote

    def cast_vote(
        self,
        hub_id: str,
        vote_id: str,
        member_id: str,
        option: str,
    ) -> GovernanceVote:
        """Cast a vote; each member may vote once per proposal."""
        hub = self._get_hub(hub_id)
        self._get_member(hub, member_id)
        if vote_id not in hub.governance_votes:
            raise WealthSystemBotNotFoundError(f"Vote '{vote_id}' not found.")
        vote = hub.governance_votes[vote_id]
        if vote.is_resolved:
            raise WealthSystemBotValidationError("Cannot cast a vote on a resolved proposal.")
        if option not in vote.options:
            raise WealthSystemBotValidationError(
                f"Option '{option}' is not valid. Choose from {vote.options}."
            )
        if member_id in vote.votes_cast:
            raise WealthSystemBotValidationError(
                f"Member '{member_id}' has already voted on this proposal."
            )
        vote.votes_cast[member_id] = option
        return vote

    def resolve_vote(self, hub_id: str, vote_id: str) -> GovernanceVote:
        """Tally votes (weighted by ownership for ENTERPRISE) and set result."""
        hub = self._get_hub(hub_id)
        if vote_id not in hub.governance_votes:
            raise WealthSystemBotNotFoundError(f"Vote '{vote_id}' not found.")
        vote = hub.governance_votes[vote_id]
        if vote.is_resolved:
            return vote

        tally: dict[str, float] = {opt: 0.0 for opt in vote.options}
        weighted = self._config.has_feature(FEATURE_FULL_GOVERNANCE)

        for member_id, option in vote.votes_cast.items():
            weight = (
                hub.members[member_id].ownership_pct
                if weighted and member_id in hub.members
                else 1.0
            )
            tally[option] = tally.get(option, 0.0) + weight

        if tally:
            vote.result = max(tally, key=lambda k: tally[k])
        vote.is_resolved = True
        return vote

    def list_votes(
        self,
        hub_id: str,
        resolved_only: bool = False,
    ) -> list[GovernanceVote]:
        hub = self._get_hub(hub_id)
        votes = list(hub.governance_votes.values())
        if resolved_only:
            votes = [v for v in votes if v.is_resolved]
        return votes

    # ------------------------------------------------------------------
    # Bot Framework
    # ------------------------------------------------------------------

    def _validate_sub_type(self, bot_type: BotType, sub_type: str) -> None:
        valid_enum = _BOT_SUB_TYPES[bot_type]
        valid_values = {e.value for e in valid_enum}
        if sub_type not in valid_values:
            raise WealthSystemBotValidationError(
                f"'{sub_type}' is not a valid sub_type for {bot_type.value}. "
                f"Valid options: {sorted(valid_values)}"
            )

    def activate_bot(
        self,
        hub_id: str,
        bot_type: BotType,
        sub_type: str,
    ) -> BotEarnings:
        """Activate a bot in a hub (Income/Asset: PRO+; Commerce/Finance: ENTERPRISE)."""
        required_feature = _BOT_FEATURE[bot_type]
        self._require_feature(required_feature)
        self._validate_sub_type(bot_type, sub_type)
        hub = self._get_hub(hub_id)
        key = _bot_key(bot_type, sub_type)
        if key not in hub.active_bots:
            hub.active_bots[key] = BotEarnings(
                bot_type=bot_type,
                sub_type=sub_type,
            )
        return hub.active_bots[key]

    def run_bot(
        self,
        hub_id: str,
        bot_type: BotType,
        sub_type: str,
    ) -> BotEarnings:
        """Simulate a bot run; earnings (10–500 USD) are added to treasury."""
        hub = self._get_hub(hub_id)
        key = _bot_key(bot_type, sub_type)
        if key not in hub.active_bots:
            raise WealthSystemBotNotFoundError(
                f"Bot '{key}' is not activated in hub '{hub_id}'. Activate it first."
            )
        earnings_obj = hub.active_bots[key]
        earned = round(random.uniform(MIN_BOT_EARNINGS_USD, MAX_BOT_EARNINGS_USD), 2)
        earnings_obj.earnings_usd += earned
        earnings_obj.runs += 1
        earnings_obj.last_run_at = _now_iso()
        hub.treasury_usd += earned
        return earnings_obj

    def get_bot_earnings(self, hub_id: str) -> list[BotEarnings]:
        hub = self._get_hub(hub_id)
        return list(hub.active_bots.values())

    # ------------------------------------------------------------------
    # Asset Allocation
    # ------------------------------------------------------------------

    def get_asset_breakdown(self, hub_id: str) -> dict:
        """Return {stability, growth, high_growth} USD amounts from treasury."""
        hub = self._get_hub(hub_id)
        alloc = hub.asset_allocation
        return {
            "stability": round(hub.treasury_usd * alloc.get("stability", 0) / 100, 4),
            "growth": round(hub.treasury_usd * alloc.get("growth", 0) / 100, 4),
            "high_growth": round(hub.treasury_usd * alloc.get("high_growth", 0) / 100, 4),
        }

    # ------------------------------------------------------------------
    # Compliance / KYC
    # ------------------------------------------------------------------

    def submit_kyc(
        self,
        hub_id: str,
        member_id: str,
        document_type: str,
    ) -> ComplianceRecord:
        """Create a PENDING KYC compliance record for a member."""
        hub = self._get_hub(hub_id)
        self._get_member(hub, member_id)
        record = ComplianceRecord(
            record_id=str(uuid.uuid4()),
            member_id=member_id,
            check_type=document_type,
            status=ComplianceStatus.PENDING,
        )
        self._compliance_records[record.record_id] = record
        return record

    def review_kyc(
        self,
        record_id: str,
        approved: bool,
        notes: str = "",
    ) -> ComplianceRecord:
        """Approve or reject a KYC compliance record."""
        if record_id not in self._compliance_records:
            raise WealthSystemBotNotFoundError(f"Compliance record '{record_id}' not found.")
        record = self._compliance_records[record_id]
        record.status = ComplianceStatus.APPROVED if approved else ComplianceStatus.REJECTED
        record.notes = notes
        record.checked_at = _now_iso()
        return record

    def get_compliance_records(self, member_id: str) -> list[ComplianceRecord]:
        return [r for r in self._compliance_records.values() if r.member_id == member_id]

    def is_kyc_approved(self, member_id: str) -> bool:
        records = self.get_compliance_records(member_id)
        return any(r.status == ComplianceStatus.APPROVED for r in records)

    # ------------------------------------------------------------------
    # DreamCoin (ENTERPRISE)
    # ------------------------------------------------------------------

    def stake_dreamcoin(
        self,
        hub_id: str,
        member_id: str,
        amount: float,
    ) -> dict:
        """Stake DreamCoin for a member (ENTERPRISE only)."""
        self._require_feature(FEATURE_DREAMCOIN_STAKING)
        if amount <= 0:
            raise WealthSystemBotValidationError("Stake amount must be positive.")
        hub = self._get_hub(hub_id)
        member = self._get_member(hub, member_id)
        if member.dreamcoin_balance < amount:
            raise WealthSystemBotValidationError(
                f"Insufficient DreamCoin balance ({member.dreamcoin_balance}) to stake {amount}."
            )
        member.dreamcoin_balance -= amount
        self._dreamcoin_staking[member_id] = (
            self._dreamcoin_staking.get(member_id, 0.0) + amount
        )
        return {
            "member_id": member_id,
            "staked": amount,
            "total_staked": self._dreamcoin_staking[member_id],
            "remaining_balance": member.dreamcoin_balance,
        }

    def get_dreamcoin_balance(self, member_id: str) -> float:
        """Return the DreamCoin wallet balance for any member across all hubs."""
        for hub in self._hubs.values():
            if member_id in hub.members:
                return hub.members[member_id].dreamcoin_balance
        return 0.0

    # ------------------------------------------------------------------
    # Analytics (ENTERPRISE)
    # ------------------------------------------------------------------

    def get_hub_analytics(self, hub_id: str) -> dict:
        """Return aggregated analytics for a hub (ENTERPRISE only)."""
        self._require_feature(FEATURE_ADVANCED_ANALYTICS)
        hub = self._get_hub(hub_id)
        bot_earnings_total = sum(
            be.earnings_usd for be in hub.active_bots.values()
        )
        return {
            "hub_id": hub_id,
            "total_members": len(hub.members),
            "treasury_usd": hub.treasury_usd,
            "dividends_paid_usd": hub.dividends_paid_usd,
            "bot_earnings_total_usd": round(bot_earnings_total, 4),
            "vote_count": len(hub.governance_votes),
            "active_bot_count": len(hub.active_bots),
        }

    # ------------------------------------------------------------------
    # Chat interface
    # ------------------------------------------------------------------

    def chat(self, hub_id: str, user_id: str, message: str) -> str:
        """Simple keyword-based chat dispatcher."""
        msg = message.lower()
        if "treasury" in msg or "balance" in msg:
            try:
                snap = self.get_treasury_snapshot(hub_id)
                return (
                    f"Treasury: ${snap['treasury_usd']:.2f} | "
                    f"Members: {len(snap['members'])}"
                )
            except WealthSystemBotTierError as exc:
                return str(exc)
        if "deposit" in msg:
            return "Use deposit(hub_id, member_id, amount_usd) to add funds to the treasury."
        if "dividend" in msg or "payout" in msg:
            return "Use distribute_dividends(hub_id, profit_usd) to issue payouts proportionally."
        if "vote" in msg or "governance" in msg:
            return "Use create_vote / cast_vote / resolve_vote to manage hub governance."
        if "bot" in msg or "income" in msg or "asset" in msg:
            return "Use activate_bot(hub_id, bot_type, sub_type) then run_bot(...) to earn income."
        if "kyc" in msg or "compliance" in msg:
            return "Use submit_kyc(hub_id, member_id, doc_type) to start KYC verification."
        if "dreamcoin" in msg or "stake" in msg:
            return "Use stake_dreamcoin(hub_id, member_id, amount) to stake DreamCoin (ENTERPRISE)."
        if "analytic" in msg:
            return "Use get_hub_analytics(hub_id) for full analytics (ENTERPRISE)."
        hub = self._hubs.get(hub_id)
        hub_name = hub.name if hub else "this hub"
        return (
            f"Welcome to the DreamCo Global Wealth System! "
            f"You are viewing '{hub_name}' on the {self.tier.value} tier. "
            "Ask about treasury, deposits, dividends, voting, bots, KYC, or DreamCoin."
        )

    # ------------------------------------------------------------------
    # run() helper
    # ------------------------------------------------------------------

    def run(self) -> None:  # pragma: no cover
        """Entry-point for standalone execution."""
        print(f"DreamCo Global Wealth System Bot running on tier: {self.tier.value}")
        flow = GlobalAISourcesFlow()
        flow.run()
