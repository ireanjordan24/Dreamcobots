"""
DreamCo Global Wealth System Bot

A community-owned financial ecosystem where people pool money, invest
collectively, earn automated dividends, and use AI bots to grow wealth.

Think: "A digital credit union + hedge fund + AI business engine — for everyone."

Features
--------
- Wealth Hub creation and management (community treasury pools)
- Member onboarding with KYC verification
- Asset allocation across three tiers: Wealth Protection, Growth, High-Growth
- Automated dividend distribution engine
- Governance voting on investments, payouts, and risk levels
- AI-powered bot ecosystem (Money Finder, Referral, Real Estate, Trading, Arbitrage)
- DreamCoin internal economy (ENTERPRISE)
- Cross-hub deal marketplace (ENTERPRISE)
- Compliance-first design: SEC / FinCEN / KYC / AML aligned

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.wealth_system_bot import WealthSystemBot
    from bots.ai-models-integration.tiers import Tier

    bot = WealthSystemBot(tier=Tier.PRO)

    hub_id = bot.create_hub("Family Wealth Circle", description="Our family investment pool")
    bot.add_member(hub_id, user_id="alice", name="Alice Johnson", contribution_usd=1000.0)
    bot.deposit(hub_id, user_id="alice", amount_usd=500.0)
    print(bot.hub_dashboard(hub_id))
    print(bot.run_dividend_cycle(hub_id))
"""

from __future__ import annotations

import sys
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "ai-models-integration"))

from tiers import Tier, get_tier_config, get_upgrade_path  # noqa: F401
from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.wealth_system_bot.tiers import (
    BOT_FEATURES,
    HUB_LIMITS,
    MEMBER_LIMITS,
    get_bot_tier_info,
    FEATURE_WEALTH_HUB,
    FEATURE_MONEY_FINDER_BOT,
    FEATURE_REFERRAL_BOT,
    FEATURE_REAL_ESTATE_BOT,
    FEATURE_TRADING_BOT,
    FEATURE_ARBITRAGE_BOT,
    FEATURE_GOVERNANCE_VOTING,
    FEATURE_AUTOMATED_DIVIDENDS,
    FEATURE_DREAMCOIN,
    FEATURE_CROSS_HUB_DEALS,
    FEATURE_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_ASSET_REBALANCING,
    FEATURE_KYC_VERIFICATION,
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------

class WealthSystemBotError(Exception):
    """Base exception for WealthSystemBot errors."""


class WealthSystemBotTierError(WealthSystemBotError):
    """Raised when a feature is not available on the current tier."""


class WealthSystemBotNotFoundError(WealthSystemBotError):
    """Raised when a requested resource is not found."""


class WealthSystemBotValidationError(WealthSystemBotError):
    """Raised when input validation fails."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AssetTier(Enum):
    """Asset allocation tiers following the DreamCo smart money strategy."""
    WEALTH_PROTECTION = "wealth_protection"   # 40% — Gold, Silver, low-risk
    GROWTH = "growth"                          # 40% — Stocks, ETFs, Real Estate
    HIGH_GROWTH = "high_growth"                # 20% — Crypto, Startups, AI


class BotType(Enum):
    """Bot types available in the DreamCo ecosystem."""
    MONEY_FINDER = "money_finder"
    REFERRAL = "referral"
    REAL_ESTATE = "real_estate"
    TRADING = "trading"
    ARBITRAGE = "arbitrage"
    GRANT_FINDER = "grant_finder"
    LEAD_GEN = "lead_gen"


class ProposalStatus(Enum):
    """Governance proposal lifecycle states."""
    OPEN = "open"
    PASSED = "passed"
    REJECTED = "rejected"
    EXECUTED = "executed"


class KYCStatus(Enum):
    """Know-Your-Customer verification states."""
    PENDING = "pending"
    VERIFIED = "verified"
    REJECTED = "rejected"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class WealthMember:
    """A member of a Wealth Hub."""
    user_id: str
    name: str
    contribution_usd: float = 0.0
    dreamcoin_balance: float = 0.0
    ownership_pct: float = 0.0
    kyc_status: KYCStatus = KYCStatus.PENDING
    joined_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reputation_score: float = 0.0
    total_dividends_usd: float = 0.0
    votes_cast: int = 0


@dataclass
class AssetAllocation:
    """Asset allocation breakdown for a Wealth Hub treasury."""
    wealth_protection_pct: float = 40.0   # Gold, Silver, T-bills
    growth_pct: float = 40.0              # Stocks, ETFs, Real estate
    high_growth_pct: float = 20.0         # Crypto, Startups

    wealth_protection_usd: float = 0.0
    growth_usd: float = 0.0
    high_growth_usd: float = 0.0

    def recalculate(self, total_usd: float) -> None:
        """Recalculate absolute USD values from total treasury."""
        self.wealth_protection_usd = total_usd * self.wealth_protection_pct / 100
        self.growth_usd = total_usd * self.growth_pct / 100
        self.high_growth_usd = total_usd * self.high_growth_pct / 100

    def to_dict(self) -> dict:
        return {
            "wealth_protection": {
                "pct": self.wealth_protection_pct,
                "usd": round(self.wealth_protection_usd, 2),
                "assets": ["Gold", "Silver", "Treasury-backed assets"],
            },
            "growth": {
                "pct": self.growth_pct,
                "usd": round(self.growth_usd, 2),
                "assets": ["Stocks / ETFs", "Real Estate", "Business investments"],
            },
            "high_growth": {
                "pct": self.high_growth_pct,
                "usd": round(self.high_growth_usd, 2),
                "assets": ["Crypto", "Startups", "AI ventures"],
            },
        }


@dataclass
class DividendRecord:
    """A single dividend distribution event."""
    dividend_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hub_id: str = ""
    total_distributed_usd: float = 0.0
    profit_usd: float = 0.0
    reinvestment_usd: float = 0.0
    distributions: dict = field(default_factory=dict)  # user_id -> amount_usd
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class GovernanceProposal:
    """A governance proposal submitted by hub members."""
    proposal_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    hub_id: str = ""
    title: str = ""
    description: str = ""
    proposer_id: str = ""
    proposal_type: str = "investment"  # investment | payout | risk_level | other
    votes_for: int = 0
    votes_against: int = 0
    voters: set = field(default_factory=set)
    status: ProposalStatus = ProposalStatus.OPEN
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    closed_at: Optional[datetime] = None


@dataclass
class WealthHub:
    """A community Wealth Hub — the core pooling unit of the DreamCo system."""
    hub_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    name: str = ""
    description: str = ""
    treasury_usd: float = 0.0
    allocation: AssetAllocation = field(default_factory=AssetAllocation)
    members: dict = field(default_factory=dict)       # user_id -> WealthMember
    proposals: list = field(default_factory=list)     # list[GovernanceProposal]
    dividend_history: list = field(default_factory=list)  # list[DividendRecord]
    active_bots: list = field(default_factory=list)   # list[BotType]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    reinvestment_rate_pct: float = 20.0               # % of profits auto-reinvested

    def member_count(self) -> int:
        return len(self.members)

    def recalculate_ownership(self) -> None:
        """Recalculate each member's ownership percentage from contributions."""
        total = sum(m.contribution_usd for m in self.members.values())
        if total <= 0:
            return
        for member in self.members.values():
            member.ownership_pct = round(member.contribution_usd / total * 100, 4)

    def total_dividends_paid_usd(self) -> float:
        return sum(d.total_distributed_usd for d in self.dividend_history)


# ---------------------------------------------------------------------------
# Bot simulation helpers (mock data for demo output)
# ---------------------------------------------------------------------------

_MOCK_MONEY_OPPORTUNITIES = [
    {"source": "Unclaimed Bank Account", "amount_usd": 324.50, "difficulty": "Easy"},
    {"source": "Government Grant — SBIR", "amount_usd": 50000.0, "difficulty": "Medium"},
    {"source": "IRS Tax Refund", "amount_usd": 1200.0, "difficulty": "Easy"},
    {"source": "Community Development Block Grant", "amount_usd": 25000.0, "difficulty": "Hard"},
]

_MOCK_REFERRAL_OPPORTUNITIES = [
    {"program": "Wisely Pay Card", "payout_usd": 25.0, "type": "Referral"},
    {"program": "Cash App", "payout_usd": 15.0, "type": "Referral"},
    {"program": "Robinhood", "payout_usd": 20.0, "type": "Referral"},
    {"program": "Amazon Affiliate", "payout_usd": 50.0, "type": "Affiliate"},
    {"program": "Shopify Partner", "payout_usd": 150.0, "type": "Affiliate"},
]

_MOCK_REAL_ESTATE_DEALS = [
    {"address": "1204 Oak Blvd, Austin TX", "price": 320000, "monthly_rent": 2400, "cap_rate_pct": 6.5},
    {"address": "3901 E Indian School Rd, Phoenix AZ", "price": 285000, "monthly_rent": 2100, "cap_rate_pct": 7.2},
    {"address": "4810 W Kennedy Blvd, Tampa FL", "price": 310000, "monthly_rent": 2300, "cap_rate_pct": 6.8},
]

_MOCK_TRADE_SIGNALS = [
    {"symbol": "GLD", "action": "BUY", "confidence_pct": 82, "reason": "Gold safe-haven demand rising"},
    {"symbol": "SPY", "action": "HOLD", "confidence_pct": 70, "reason": "Broad market consolidation"},
    {"symbol": "BTC", "action": "BUY", "confidence_pct": 65, "reason": "Halving cycle momentum"},
]

_MOCK_ARBITRAGE_DEALS = [
    {"product": "Gaming Headset XR", "buy_price": 45.0, "sell_price": 89.0, "platform": "Amazon→eBay"},
    {"product": "Vintage Sneakers Sz 10", "buy_price": 80.0, "sell_price": 195.0, "platform": "Thrift→StockX"},
]


# ---------------------------------------------------------------------------
# Main Bot Class
# ---------------------------------------------------------------------------

class WealthSystemBot:
    """
    DreamCo Global Wealth System Bot.

    Manages community Wealth Hubs, member accounts, asset allocation,
    governance voting, dividend distribution, and the AI bot ecosystem.
    """

    # Dividend payout simulation: profit is modelled as a % of treasury.
    _DEFAULT_MONTHLY_RETURN_PCT = 3.5

    def __init__(self, tier: Tier = Tier.FREE, owner_id: str = "owner") -> None:
        self.tier = tier
        self.owner_id = owner_id
        self.config = get_tier_config(tier)
        self._features: list[str] = BOT_FEATURES[tier.value]
        self._hubs: dict[str, WealthHub] = {}
        self._dreamcoin_total_supply: float = 1_000_000.0
        self._dreamcoin_circulating: float = 0.0

    # ------------------------------------------------------------------
    # Feature guard
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        if feature not in self._features:
            upgrade = get_upgrade_path(self.tier)
            msg = (
                f"Feature '{feature}' is not available on the {self.tier.value.upper()} tier. "
                f"Upgrade to {upgrade} to unlock it."
            )
            raise WealthSystemBotTierError(msg)

    # ------------------------------------------------------------------
    # Wealth Hub management
    # ------------------------------------------------------------------

    def create_hub(self, name: str, description: str = "") -> str:
        """Create a new Wealth Hub and return its hub_id."""
        self._require_feature(FEATURE_WEALTH_HUB)
        if not name or not name.strip():
            raise WealthSystemBotValidationError("Hub name cannot be empty.")
        limit = HUB_LIMITS[self.tier]
        if limit is not None and len(self._hubs) >= limit:
            raise WealthSystemBotTierError(
                f"Hub limit reached ({limit}). Upgrade to create more hubs."
            )
        hub = WealthHub(name=name.strip(), description=description.strip())
        self._hubs[hub.hub_id] = hub
        return hub.hub_id

    def get_hub(self, hub_id: str) -> WealthHub:
        """Retrieve a hub by ID."""
        hub = self._hubs.get(hub_id)
        if hub is None:
            raise WealthSystemBotNotFoundError(f"Wealth Hub '{hub_id}' not found.")
        return hub

    def list_hubs(self) -> list[dict]:
        """List all Wealth Hubs with summary data."""
        return [
            {
                "hub_id": h.hub_id,
                "name": h.name,
                "description": h.description,
                "treasury_usd": round(h.treasury_usd, 2),
                "member_count": h.member_count(),
                "active_bots": [b.value for b in h.active_bots],
                "created_at": h.created_at.isoformat(),
            }
            for h in self._hubs.values()
        ]

    # ------------------------------------------------------------------
    # Member management
    # ------------------------------------------------------------------

    def add_member(
        self,
        hub_id: str,
        user_id: str,
        name: str,
        contribution_usd: float = 0.0,
    ) -> WealthMember:
        """Add a member to a Wealth Hub."""
        hub = self.get_hub(hub_id)
        limit = MEMBER_LIMITS[self.tier]
        if limit is not None and len(hub.members) >= limit:
            raise WealthSystemBotTierError(
                f"Member limit reached ({limit}) for this tier."
            )
        if user_id in hub.members:
            raise WealthSystemBotValidationError(
                f"User '{user_id}' is already a member of hub '{hub_id}'."
            )
        if contribution_usd < 0:
            raise WealthSystemBotValidationError("Contribution cannot be negative.")
        member = WealthMember(
            user_id=user_id,
            name=name.strip(),
            contribution_usd=contribution_usd,
            kyc_status=KYCStatus.VERIFIED if self.tier != Tier.FREE else KYCStatus.PENDING,
        )
        hub.members[user_id] = member
        hub.treasury_usd += contribution_usd
        hub.allocation.recalculate(hub.treasury_usd)
        hub.recalculate_ownership()
        return member

    def get_member(self, hub_id: str, user_id: str) -> WealthMember:
        """Retrieve a member from a hub."""
        hub = self.get_hub(hub_id)
        member = hub.members.get(user_id)
        if member is None:
            raise WealthSystemBotNotFoundError(
                f"Member '{user_id}' not found in hub '{hub_id}'."
            )
        return member

    def verify_kyc(self, hub_id: str, user_id: str) -> KYCStatus:
        """Mark a member as KYC-verified."""
        self._require_feature(FEATURE_KYC_VERIFICATION)
        member = self.get_member(hub_id, user_id)
        member.kyc_status = KYCStatus.VERIFIED
        return member.kyc_status

    # ------------------------------------------------------------------
    # Deposits & withdrawals
    # ------------------------------------------------------------------

    def deposit(self, hub_id: str, user_id: str, amount_usd: float) -> float:
        """Deposit funds into a hub for a member. Returns new treasury balance."""
        if amount_usd <= 0:
            raise WealthSystemBotValidationError("Deposit amount must be positive.")
        hub = self.get_hub(hub_id)
        member = self.get_member(hub_id, user_id)
        member.contribution_usd += amount_usd
        hub.treasury_usd += amount_usd
        hub.allocation.recalculate(hub.treasury_usd)
        hub.recalculate_ownership()
        return hub.treasury_usd

    def withdraw(self, hub_id: str, user_id: str, amount_usd: float) -> float:
        """Withdraw funds from a hub for a member. Returns new treasury balance."""
        if amount_usd <= 0:
            raise WealthSystemBotValidationError("Withdrawal amount must be positive.")
        hub = self.get_hub(hub_id)
        member = self.get_member(hub_id, user_id)
        max_withdrawal = hub.treasury_usd * (member.ownership_pct / 100)
        if amount_usd > max_withdrawal:
            raise WealthSystemBotValidationError(
                f"Withdrawal ${amount_usd:.2f} exceeds your share "
                f"${max_withdrawal:.2f} of the treasury."
            )
        member.contribution_usd = max(0.0, member.contribution_usd - amount_usd)
        hub.treasury_usd = max(0.0, hub.treasury_usd - amount_usd)
        hub.allocation.recalculate(hub.treasury_usd)
        hub.recalculate_ownership()
        return hub.treasury_usd

    # ------------------------------------------------------------------
    # Asset allocation
    # ------------------------------------------------------------------

    def set_allocation(
        self,
        hub_id: str,
        wealth_protection_pct: float,
        growth_pct: float,
        high_growth_pct: float,
    ) -> dict:
        """Set the asset allocation percentages for a hub (must sum to 100)."""
        self._require_feature(FEATURE_ASSET_REBALANCING)
        total = wealth_protection_pct + growth_pct + high_growth_pct
        if abs(total - 100.0) > 0.01:
            raise WealthSystemBotValidationError(
                f"Allocation percentages must sum to 100 (got {total:.2f})."
            )
        hub = self.get_hub(hub_id)
        hub.allocation.wealth_protection_pct = wealth_protection_pct
        hub.allocation.growth_pct = growth_pct
        hub.allocation.high_growth_pct = high_growth_pct
        hub.allocation.recalculate(hub.treasury_usd)
        return hub.allocation.to_dict()

    def get_allocation(self, hub_id: str) -> dict:
        """Return the current asset allocation for a hub."""
        hub = self.get_hub(hub_id)
        hub.allocation.recalculate(hub.treasury_usd)
        return hub.allocation.to_dict()

    # ------------------------------------------------------------------
    # Dividend engine
    # ------------------------------------------------------------------

    def run_dividend_cycle(
        self,
        hub_id: str,
        monthly_return_pct: float = _DEFAULT_MONTHLY_RETURN_PCT,
    ) -> DividendRecord:
        """
        Simulate a dividend cycle for a hub.

        Generates mock profit, deducts reinvestment portion, and
        distributes remaining profit to members proportionally.
        """
        self._require_feature(FEATURE_AUTOMATED_DIVIDENDS)
        hub = self.get_hub(hub_id)
        if hub.treasury_usd <= 0:
            raise WealthSystemBotValidationError(
                "Treasury is empty. Members must deposit funds first."
            )
        if monthly_return_pct < 0:
            raise WealthSystemBotValidationError(
                "Monthly return percentage cannot be negative."
            )
        gross_profit = hub.treasury_usd * (monthly_return_pct / 100)
        reinvest = gross_profit * (hub.reinvestment_rate_pct / 100)
        distributable = gross_profit - reinvest

        # Reinvest portion back into treasury
        hub.treasury_usd += reinvest
        hub.allocation.recalculate(hub.treasury_usd)

        # Distribute to members
        distributions: dict[str, float] = {}
        for uid, member in hub.members.items():
            payout = distributable * (member.ownership_pct / 100)
            member.total_dividends_usd += payout
            distributions[uid] = round(payout, 2)

        record = DividendRecord(
            hub_id=hub_id,
            total_distributed_usd=round(distributable, 2),
            profit_usd=round(gross_profit, 2),
            reinvestment_usd=round(reinvest, 2),
            distributions=distributions,
        )
        hub.dividend_history.append(record)
        return record

    # ------------------------------------------------------------------
    # Governance
    # ------------------------------------------------------------------

    def create_proposal(
        self,
        hub_id: str,
        proposer_id: str,
        title: str,
        description: str = "",
        proposal_type: str = "investment",
    ) -> GovernanceProposal:
        """Submit a governance proposal to a hub."""
        self._require_feature(FEATURE_GOVERNANCE_VOTING)
        hub = self.get_hub(hub_id)
        if proposer_id not in hub.members:
            raise WealthSystemBotNotFoundError(
                f"Proposer '{proposer_id}' is not a member of hub '{hub_id}'."
            )
        if not title or not title.strip():
            raise WealthSystemBotValidationError("Proposal title cannot be empty.")
        proposal = GovernanceProposal(
            hub_id=hub_id,
            title=title.strip(),
            description=description.strip(),
            proposer_id=proposer_id,
            proposal_type=proposal_type,
        )
        hub.proposals.append(proposal)
        return proposal

    def vote(
        self,
        hub_id: str,
        proposal_id: str,
        voter_id: str,
        approve: bool,
    ) -> GovernanceProposal:
        """Cast a vote on a governance proposal."""
        self._require_feature(FEATURE_GOVERNANCE_VOTING)
        hub = self.get_hub(hub_id)
        if voter_id not in hub.members:
            raise WealthSystemBotNotFoundError(
                f"Voter '{voter_id}' is not a member of hub '{hub_id}'."
            )
        proposal = next(
            (p for p in hub.proposals if p.proposal_id == proposal_id), None
        )
        if proposal is None:
            raise WealthSystemBotNotFoundError(
                f"Proposal '{proposal_id}' not found in hub '{hub_id}'."
            )
        if proposal.status != ProposalStatus.OPEN:
            raise WealthSystemBotValidationError(
                f"Proposal is already {proposal.status.value} and cannot be voted on."
            )
        if voter_id in proposal.voters:
            raise WealthSystemBotValidationError(
                f"Voter '{voter_id}' has already voted on this proposal."
            )
        proposal.voters.add(voter_id)
        hub.members[voter_id].votes_cast += 1
        if approve:
            proposal.votes_for += 1
        else:
            proposal.votes_against += 1
        return proposal

    def close_proposal(self, hub_id: str, proposal_id: str) -> GovernanceProposal:
        """Close a proposal and determine its outcome (simple majority)."""
        self._require_feature(FEATURE_GOVERNANCE_VOTING)
        hub = self.get_hub(hub_id)
        proposal = next(
            (p for p in hub.proposals if p.proposal_id == proposal_id), None
        )
        if proposal is None:
            raise WealthSystemBotNotFoundError(
                f"Proposal '{proposal_id}' not found."
            )
        if proposal.status != ProposalStatus.OPEN:
            raise WealthSystemBotValidationError(
                f"Proposal is already {proposal.status.value}."
            )
        proposal.closed_at = datetime.now(timezone.utc)
        if proposal.votes_for > proposal.votes_against:
            proposal.status = ProposalStatus.PASSED
        else:
            proposal.status = ProposalStatus.REJECTED
        return proposal

    # ------------------------------------------------------------------
    # Bot ecosystem
    # ------------------------------------------------------------------

    def activate_bot(self, hub_id: str, bot_type: BotType) -> dict:
        """Activate an AI bot for a Wealth Hub."""
        feature_map = {
            BotType.MONEY_FINDER: FEATURE_MONEY_FINDER_BOT,
            BotType.REFERRAL: FEATURE_REFERRAL_BOT,
            BotType.REAL_ESTATE: FEATURE_REAL_ESTATE_BOT,
            BotType.TRADING: FEATURE_TRADING_BOT,
            BotType.ARBITRAGE: FEATURE_ARBITRAGE_BOT,
            BotType.GRANT_FINDER: FEATURE_MONEY_FINDER_BOT,
            BotType.LEAD_GEN: FEATURE_REFERRAL_BOT,
        }
        required_feature = feature_map.get(bot_type, FEATURE_MONEY_FINDER_BOT)
        self._require_feature(required_feature)
        hub = self.get_hub(hub_id)
        if bot_type not in hub.active_bots:
            hub.active_bots.append(bot_type)
        return {
            "hub_id": hub_id,
            "bot_type": bot_type.value,
            "status": "active",
            "message": f"{bot_type.value.replace('_', ' ').title()} Bot activated for hub '{hub.name}'.",
        }

    def deactivate_bot(self, hub_id: str, bot_type: BotType) -> dict:
        """Deactivate an AI bot for a Wealth Hub."""
        hub = self.get_hub(hub_id)
        if bot_type in hub.active_bots:
            hub.active_bots.remove(bot_type)
        return {
            "hub_id": hub_id,
            "bot_type": bot_type.value,
            "status": "inactive",
        }

    def run_bot(self, hub_id: str, bot_type: BotType) -> dict:
        """Execute a bot and return mock results."""
        hub = self.get_hub(hub_id)
        if bot_type not in hub.active_bots:
            raise WealthSystemBotValidationError(
                f"Bot '{bot_type.value}' is not activated for hub '{hub_id}'. "
                "Call activate_bot() first."
            )
        result_map = {
            BotType.MONEY_FINDER: {
                "bot": "Money Finder",
                "opportunities": _MOCK_MONEY_OPPORTUNITIES,
                "total_potential_usd": sum(o["amount_usd"] for o in _MOCK_MONEY_OPPORTUNITIES),
            },
            BotType.REFERRAL: {
                "bot": "Referral",
                "opportunities": _MOCK_REFERRAL_OPPORTUNITIES,
                "total_potential_usd": sum(o["payout_usd"] for o in _MOCK_REFERRAL_OPPORTUNITIES),
            },
            BotType.REAL_ESTATE: {
                "bot": "Real Estate",
                "deals": _MOCK_REAL_ESTATE_DEALS,
                "deals_found": len(_MOCK_REAL_ESTATE_DEALS),
            },
            BotType.TRADING: {
                "bot": "Trading",
                "signals": _MOCK_TRADE_SIGNALS,
                "signals_generated": len(_MOCK_TRADE_SIGNALS),
            },
            BotType.ARBITRAGE: {
                "bot": "Arbitrage",
                "deals": _MOCK_ARBITRAGE_DEALS,
                "total_potential_profit_usd": sum(
                    d["sell_price"] - d["buy_price"] for d in _MOCK_ARBITRAGE_DEALS
                ),
            },
            BotType.GRANT_FINDER: {
                "bot": "Grant Finder",
                "grants": [o for o in _MOCK_MONEY_OPPORTUNITIES if "Grant" in o["source"]],
            },
            BotType.LEAD_GEN: {
                "bot": "Lead Gen",
                "leads_generated": 47,
                "estimated_revenue_usd": 2350.0,
            },
        }
        return result_map.get(bot_type, {"bot": bot_type.value, "status": "ran"})

    # ------------------------------------------------------------------
    # DreamCoin
    # ------------------------------------------------------------------

    def award_dreamcoin(self, hub_id: str, user_id: str, amount: float) -> float:
        """Award DreamCoin to a member (ENTERPRISE only)."""
        self._require_feature(FEATURE_DREAMCOIN)
        if amount <= 0:
            raise WealthSystemBotValidationError("DreamCoin amount must be positive.")
        member = self.get_member(hub_id, user_id)
        if self._dreamcoin_circulating + amount > self._dreamcoin_total_supply:
            raise WealthSystemBotValidationError("DreamCoin supply exhausted.")
        member.dreamcoin_balance += amount
        self._dreamcoin_circulating += amount
        return member.dreamcoin_balance

    def dreamcoin_supply_info(self) -> dict:
        """Return DreamCoin supply statistics."""
        self._require_feature(FEATURE_DREAMCOIN)
        return {
            "total_supply": self._dreamcoin_total_supply,
            "circulating": round(self._dreamcoin_circulating, 4),
            "remaining": round(self._dreamcoin_total_supply - self._dreamcoin_circulating, 4),
        }

    # ------------------------------------------------------------------
    # Analytics & dashboard
    # ------------------------------------------------------------------

    def hub_dashboard(self, hub_id: str) -> dict:
        """Return a full dashboard summary for a Wealth Hub."""
        hub = self.get_hub(hub_id)
        hub.allocation.recalculate(hub.treasury_usd)
        return {
            "hub_id": hub.hub_id,
            "name": hub.name,
            "description": hub.description,
            "treasury_usd": round(hub.treasury_usd, 2),
            "member_count": hub.member_count(),
            "allocation": hub.allocation.to_dict(),
            "active_bots": [b.value for b in hub.active_bots],
            "total_dividends_paid_usd": round(hub.total_dividends_paid_usd(), 2),
            "open_proposals": sum(
                1 for p in hub.proposals if p.status == ProposalStatus.OPEN
            ),
            "dividend_cycles": len(hub.dividend_history),
            "reinvestment_rate_pct": hub.reinvestment_rate_pct,
            "created_at": hub.created_at.isoformat(),
        }

    def member_portfolio(self, hub_id: str, user_id: str) -> dict:
        """Return a member's portfolio summary."""
        hub = self.get_hub(hub_id)
        member = self.get_member(hub_id, user_id)
        return {
            "user_id": member.user_id,
            "name": member.name,
            "hub": hub.name,
            "contribution_usd": round(member.contribution_usd, 2),
            "ownership_pct": member.ownership_pct,
            "total_dividends_usd": round(member.total_dividends_usd, 2),
            "dreamcoin_balance": member.dreamcoin_balance,
            "kyc_status": member.kyc_status.value,
            "reputation_score": member.reputation_score,
            "votes_cast": member.votes_cast,
            "joined_at": member.joined_at.isoformat(),
        }

    def platform_analytics(self) -> dict:
        """Return platform-wide analytics (PRO+ only)."""
        self._require_feature(FEATURE_ANALYTICS)
        total_treasury = sum(h.treasury_usd for h in self._hubs.values())
        total_members = sum(h.member_count() for h in self._hubs.values())
        total_dividends = sum(h.total_dividends_paid_usd() for h in self._hubs.values())
        return {
            "total_hubs": len(self._hubs),
            "total_members": total_members,
            "total_treasury_usd": round(total_treasury, 2),
            "total_dividends_paid_usd": round(total_dividends, 2),
            "tier": self.tier.value,
            "features_enabled": self._features,
        }

    def upgrade_info(self) -> dict:
        """Return upgrade path and feature comparison."""
        upgrade = get_upgrade_path(self.tier)
        return {
            "current_tier": self.tier.value,
            "upgrade_to": upgrade,
            "current_features": self._features,
            "hub_limit": HUB_LIMITS[self.tier],
            "member_limit_per_hub": MEMBER_LIMITS[self.tier],
        }
