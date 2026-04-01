"""
Tests for the DreamCo Global Wealth System

Covers:
  1. Tiers module
  2. WealthSystemBot — instantiation and tier guards
  3. Wealth Hub management (create, list, limits)
  4. Member management (add, KYC, limits)
  5. Deposits and withdrawals
  6. Asset allocation
  7. Dividend engine
  8. Governance (proposals, voting, closing)
  9. Bot ecosystem (activate, deactivate, run)
  10. DreamCoin
  11. Analytics and dashboard
  12. Pitch deck structure
  13. UI Screens — all 7 screens
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
AI_MODELS_DIR = os.path.join(REPO_ROOT, "bots", "ai-models-integration")
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest

from tiers import Tier
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
    FEATURE_ANALYTICS,
    FEATURE_ASSET_REBALANCING,
    FEATURE_KYC_VERIFICATION,
)
from bots.wealth_system_bot.wealth_system_bot import (
    WealthSystemBot,
    WealthSystemBotError,
    WealthSystemBotTierError,
    WealthSystemBotNotFoundError,
    WealthSystemBotValidationError,
    WealthHub,
    WealthMember,
    AssetAllocation,
    DividendRecord,
    GovernanceProposal,
    ProposalStatus,
    BotType,
    AssetTier,
    KYCStatus,
)


# ---------------------------------------------------------------------------
# 1. Tiers module
# ---------------------------------------------------------------------------

class TestTiersModule:
    def test_hub_limits_defined(self):
        assert HUB_LIMITS[Tier.FREE] == 1
        assert HUB_LIMITS[Tier.PRO] == 5
        assert HUB_LIMITS[Tier.ENTERPRISE] is None

    def test_member_limits_defined(self):
        assert MEMBER_LIMITS[Tier.FREE] == 10
        assert MEMBER_LIMITS[Tier.PRO] == 100
        assert MEMBER_LIMITS[Tier.ENTERPRISE] is None

    def test_features_escalate(self):
        free_feats = BOT_FEATURES[Tier.FREE.value]
        pro_feats = BOT_FEATURES[Tier.PRO.value]
        ent_feats = BOT_FEATURES[Tier.ENTERPRISE.value]
        assert FEATURE_WEALTH_HUB in free_feats
        assert FEATURE_GOVERNANCE_VOTING in pro_feats
        assert FEATURE_GOVERNANCE_VOTING not in free_feats
        assert FEATURE_DREAMCOIN in ent_feats
        assert FEATURE_DREAMCOIN not in pro_feats

    def test_get_bot_tier_info_free(self):
        info = get_bot_tier_info(Tier.FREE)
        assert info["tier"] == "free"
        assert info["max_hubs"] == 1
        assert isinstance(info["features"], list)

    def test_get_bot_tier_info_enterprise(self):
        info = get_bot_tier_info(Tier.ENTERPRISE)
        assert info["max_hubs"] is None
        assert info["max_members_per_hub"] is None


# ---------------------------------------------------------------------------
# 2. WealthSystemBot instantiation
# ---------------------------------------------------------------------------

class TestInstantiation:
    def test_default_is_free_tier(self):
        bot = WealthSystemBot()
        assert bot.tier == Tier.FREE

    def test_pro_tier(self):
        bot = WealthSystemBot(tier=Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_enterprise_tier(self):
        bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_config_loaded(self):
        bot = WealthSystemBot()
        assert bot.config is not None

    def test_owner_id(self):
        bot = WealthSystemBot(owner_id="dreamco_owner")
        assert bot.owner_id == "dreamco_owner"

    def test_initial_no_hubs(self):
        bot = WealthSystemBot()
        assert bot.list_hubs() == []


# ---------------------------------------------------------------------------
# 3. Wealth Hub management
# ---------------------------------------------------------------------------

class TestWealthHubManagement:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)

    def test_create_hub_returns_id(self):
        hub_id = self.bot.create_hub("Test Hub")
        assert isinstance(hub_id, str)
        assert len(hub_id) > 0

    def test_create_hub_stores_hub(self):
        hub_id = self.bot.create_hub("Family Pool")
        hubs = self.bot.list_hubs()
        assert len(hubs) == 1
        assert hubs[0]["hub_id"] == hub_id
        assert hubs[0]["name"] == "Family Pool"

    def test_create_hub_with_description(self):
        hub_id = self.bot.create_hub("My Hub", description="Test description")
        hub = self.bot.get_hub(hub_id)
        assert hub.description == "Test description"

    def test_empty_hub_name_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.create_hub("")

    def test_whitespace_hub_name_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.create_hub("   ")

    def test_get_nonexistent_hub_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.get_hub("nonexistent-id")

    def test_free_tier_hub_limit(self):
        bot = WealthSystemBot(tier=Tier.FREE)
        bot.create_hub("Hub 1")
        with pytest.raises(WealthSystemBotTierError):
            bot.create_hub("Hub 2")

    def test_pro_tier_allows_5_hubs(self):
        for i in range(5):
            self.bot.create_hub(f"Hub {i + 1}")
        assert len(self.bot.list_hubs()) == 5

    def test_pro_tier_hub_limit_enforced(self):
        for i in range(5):
            self.bot.create_hub(f"Hub {i + 1}")
        with pytest.raises(WealthSystemBotTierError):
            self.bot.create_hub("Hub 6")

    def test_enterprise_unlimited_hubs(self):
        bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        for i in range(10):
            bot.create_hub(f"Hub {i + 1}")
        assert len(bot.list_hubs()) == 10

    def test_list_hubs_returns_list(self):
        self.bot.create_hub("Hub A")
        self.bot.create_hub("Hub B")
        result = self.bot.list_hubs()
        assert len(result) == 2
        for item in result:
            assert "hub_id" in item
            assert "treasury_usd" in item


# ---------------------------------------------------------------------------
# 4. Member management
# ---------------------------------------------------------------------------

class TestMemberManagement:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub_id = self.bot.create_hub("Test Hub")

    def test_add_member_returns_wealth_member(self):
        member = self.bot.add_member(self.hub_id, "alice", "Alice")
        assert isinstance(member, WealthMember)
        assert member.user_id == "alice"

    def test_add_member_with_contribution(self):
        member = self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=1000.0)
        assert member.contribution_usd == 1000.0

    def test_add_member_updates_treasury(self):
        self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=1000.0)
        hub = self.bot.get_hub(self.hub_id)
        assert hub.treasury_usd == 1000.0

    def test_add_duplicate_member_raises(self):
        self.bot.add_member(self.hub_id, "alice", "Alice")
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.add_member(self.hub_id, "alice", "Alice Again")

    def test_negative_contribution_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=-100.0)

    def test_get_member(self):
        self.bot.add_member(self.hub_id, "bob", "Bob")
        member = self.bot.get_member(self.hub_id, "bob")
        assert member.name == "Bob"

    def test_get_nonexistent_member_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.get_member(self.hub_id, "nobody")

    def test_ownership_recalculated_on_add(self):
        self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=1000.0)
        self.bot.add_member(self.hub_id, "bob", "Bob", contribution_usd=1000.0)
        alice = self.bot.get_member(self.hub_id, "alice")
        bob = self.bot.get_member(self.hub_id, "bob")
        assert abs(alice.ownership_pct - 50.0) < 0.01
        assert abs(bob.ownership_pct - 50.0) < 0.01

    def test_verify_kyc(self):
        self.bot.add_member(self.hub_id, "alice", "Alice")
        status = self.bot.verify_kyc(self.hub_id, "alice")
        assert status == KYCStatus.VERIFIED

    def test_kyc_free_tier_starts_pending(self):
        bot = WealthSystemBot(tier=Tier.FREE)
        hub_id = bot.create_hub("Free Hub")
        member = bot.add_member(hub_id, "alice", "Alice")
        assert member.kyc_status == KYCStatus.PENDING


# ---------------------------------------------------------------------------
# 5. Deposits & withdrawals
# ---------------------------------------------------------------------------

class TestDepositsWithdrawals:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub_id = self.bot.create_hub("Test Hub")
        self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=1000.0)

    def test_deposit_increases_treasury(self):
        new_balance = self.bot.deposit(self.hub_id, "alice", 500.0)
        assert new_balance == 1500.0

    def test_deposit_zero_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.deposit(self.hub_id, "alice", 0.0)

    def test_deposit_negative_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.deposit(self.hub_id, "alice", -100.0)

    def test_withdraw_reduces_treasury(self):
        new_balance = self.bot.withdraw(self.hub_id, "alice", 500.0)
        assert new_balance == 500.0

    def test_withdraw_zero_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.withdraw(self.hub_id, "alice", 0.0)

    def test_withdraw_exceeds_share_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.withdraw(self.hub_id, "alice", 2000.0)

    def test_deposit_to_nonexistent_hub_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.deposit("bad-hub", "alice", 100.0)

    def test_allocation_updated_on_deposit(self):
        self.bot.deposit(self.hub_id, "alice", 1000.0)
        alloc = self.bot.get_allocation(self.hub_id)
        assert alloc["growth"]["usd"] == pytest.approx(800.0)


# ---------------------------------------------------------------------------
# 6. Asset allocation
# ---------------------------------------------------------------------------

class TestAssetAllocation:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        self.hub_id = self.bot.create_hub("Test Hub")
        self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=10_000.0)

    def test_get_allocation_returns_dict(self):
        alloc = self.bot.get_allocation(self.hub_id)
        assert "wealth_protection" in alloc
        assert "growth" in alloc
        assert "high_growth" in alloc

    def test_default_allocation_percentages(self):
        alloc = self.bot.get_allocation(self.hub_id)
        assert alloc["wealth_protection"]["pct"] == pytest.approx(40.0)
        assert alloc["growth"]["pct"] == pytest.approx(40.0)
        assert alloc["high_growth"]["pct"] == pytest.approx(20.0)

    def test_default_allocation_usd_values(self):
        alloc = self.bot.get_allocation(self.hub_id)
        assert alloc["wealth_protection"]["usd"] == pytest.approx(4_000.0)
        assert alloc["growth"]["usd"] == pytest.approx(4_000.0)
        assert alloc["high_growth"]["usd"] == pytest.approx(2_000.0)

    def test_set_allocation(self):
        alloc = self.bot.set_allocation(self.hub_id, 50.0, 30.0, 20.0)
        assert alloc["wealth_protection"]["pct"] == pytest.approx(50.0)
        assert alloc["growth"]["pct"] == pytest.approx(30.0)

    def test_set_allocation_invalid_sum_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.set_allocation(self.hub_id, 50.0, 30.0, 30.0)

    def test_set_allocation_requires_enterprise(self):
        bot = WealthSystemBot(tier=Tier.PRO)
        hub_id = bot.create_hub("Hub")
        with pytest.raises(WealthSystemBotTierError):
            bot.set_allocation(hub_id, 50.0, 30.0, 20.0)


# ---------------------------------------------------------------------------
# 7. Dividend engine
# ---------------------------------------------------------------------------

class TestDividendEngine:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub_id = self.bot.create_hub("Test Hub")
        self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=6000.0)
        self.bot.add_member(self.hub_id, "bob", "Bob", contribution_usd=4000.0)

    def test_run_dividend_cycle_returns_record(self):
        record = self.bot.run_dividend_cycle(self.hub_id)
        assert isinstance(record, DividendRecord)

    def test_dividend_total_positive(self):
        record = self.bot.run_dividend_cycle(self.hub_id)
        assert record.total_distributed_usd > 0

    def test_reinvestment_goes_into_treasury(self):
        hub = self.bot.get_hub(self.hub_id)
        initial = hub.treasury_usd
        record = self.bot.run_dividend_cycle(self.hub_id)
        assert hub.treasury_usd > initial
        assert record.reinvestment_usd > 0

    def test_distributions_sum_approximately_total(self):
        record = self.bot.run_dividend_cycle(self.hub_id)
        dist_sum = sum(record.distributions.values())
        assert abs(dist_sum - record.total_distributed_usd) < 0.10

    def test_member_dividends_proportional(self):
        record = self.bot.run_dividend_cycle(self.hub_id)
        alice_div = record.distributions.get("alice", 0)
        bob_div = record.distributions.get("bob", 0)
        assert alice_div > bob_div

    def test_dividend_recorded_in_hub_history(self):
        self.bot.run_dividend_cycle(self.hub_id)
        hub = self.bot.get_hub(self.hub_id)
        assert len(hub.dividend_history) == 1

    def test_empty_treasury_raises(self):
        bot = WealthSystemBot(tier=Tier.PRO)
        hub_id = bot.create_hub("Empty Hub")
        with pytest.raises(WealthSystemBotValidationError):
            bot.run_dividend_cycle(hub_id)

    def test_negative_return_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.run_dividend_cycle(self.hub_id, monthly_return_pct=-1.0)

    def test_dividend_requires_pro(self):
        bot = WealthSystemBot(tier=Tier.FREE)
        hub_id = bot.create_hub("Hub")
        with pytest.raises(WealthSystemBotTierError):
            bot.run_dividend_cycle(hub_id)


# ---------------------------------------------------------------------------
# 8. Governance
# ---------------------------------------------------------------------------

class TestGovernance:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub_id = self.bot.create_hub("Test Hub")
        self.bot.add_member(self.hub_id, "alice", "Alice")
        self.bot.add_member(self.hub_id, "bob", "Bob")
        self.bot.add_member(self.hub_id, "carol", "Carol")

    def test_create_proposal(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Invest in BTC")
        assert isinstance(proposal, GovernanceProposal)
        assert proposal.status == ProposalStatus.OPEN

    def test_create_proposal_empty_title_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.create_proposal(self.hub_id, "alice", "")

    def test_create_proposal_nonmember_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.create_proposal(self.hub_id, "nobody", "Test")

    def test_vote_approve(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        updated = self.bot.vote(self.hub_id, proposal.proposal_id, "bob", True)
        assert updated.votes_for == 1

    def test_vote_reject(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        updated = self.bot.vote(self.hub_id, proposal.proposal_id, "bob", False)
        assert updated.votes_against == 1

    def test_double_vote_raises(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        self.bot.vote(self.hub_id, proposal.proposal_id, "bob", True)
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.vote(self.hub_id, proposal.proposal_id, "bob", True)

    def test_vote_nonmember_raises(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.vote(self.hub_id, proposal.proposal_id, "nobody", True)

    def test_close_proposal_passed(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        self.bot.vote(self.hub_id, proposal.proposal_id, "alice", True)
        self.bot.vote(self.hub_id, proposal.proposal_id, "bob", True)
        self.bot.vote(self.hub_id, proposal.proposal_id, "carol", False)
        closed = self.bot.close_proposal(self.hub_id, proposal.proposal_id)
        assert closed.status == ProposalStatus.PASSED

    def test_close_proposal_rejected(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        self.bot.vote(self.hub_id, proposal.proposal_id, "alice", False)
        self.bot.vote(self.hub_id, proposal.proposal_id, "bob", False)
        closed = self.bot.close_proposal(self.hub_id, proposal.proposal_id)
        assert closed.status == ProposalStatus.REJECTED

    def test_close_already_closed_raises(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        self.bot.close_proposal(self.hub_id, proposal.proposal_id)
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.close_proposal(self.hub_id, proposal.proposal_id)

    def test_vote_closed_proposal_raises(self):
        proposal = self.bot.create_proposal(self.hub_id, "alice", "Test")
        self.bot.close_proposal(self.hub_id, proposal.proposal_id)
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.vote(self.hub_id, proposal.proposal_id, "bob", True)

    def test_governance_requires_pro(self):
        bot = WealthSystemBot(tier=Tier.FREE)
        hub_id = bot.create_hub("Hub")
        with pytest.raises(WealthSystemBotTierError):
            bot.create_proposal(hub_id, "alice", "Test")


# ---------------------------------------------------------------------------
# 9. Bot ecosystem
# ---------------------------------------------------------------------------

class TestBotEcosystem:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub_id = self.bot.create_hub("Test Hub")

    def test_activate_money_finder(self):
        result = self.bot.activate_bot(self.hub_id, BotType.MONEY_FINDER)
        assert result["status"] == "active"
        assert result["bot_type"] == "money_finder"

    def test_activate_referral_bot(self):
        result = self.bot.activate_bot(self.hub_id, BotType.REFERRAL)
        assert result["status"] == "active"

    def test_activate_arbitrage_requires_enterprise(self):
        with pytest.raises(WealthSystemBotTierError):
            self.bot.activate_bot(self.hub_id, BotType.ARBITRAGE)

    def test_enterprise_can_activate_arbitrage(self):
        bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        hub_id = bot.create_hub("Hub")
        result = bot.activate_bot(hub_id, BotType.ARBITRAGE)
        assert result["status"] == "active"

    def test_deactivate_bot(self):
        self.bot.activate_bot(self.hub_id, BotType.MONEY_FINDER)
        result = self.bot.deactivate_bot(self.hub_id, BotType.MONEY_FINDER)
        assert result["status"] == "inactive"

    def test_run_money_finder(self):
        self.bot.activate_bot(self.hub_id, BotType.MONEY_FINDER)
        result = self.bot.run_bot(self.hub_id, BotType.MONEY_FINDER)
        assert "opportunities" in result
        assert result["total_potential_usd"] > 0

    def test_run_referral_bot(self):
        self.bot.activate_bot(self.hub_id, BotType.REFERRAL)
        result = self.bot.run_bot(self.hub_id, BotType.REFERRAL)
        assert "opportunities" in result

    def test_run_real_estate_bot(self):
        self.bot.activate_bot(self.hub_id, BotType.REAL_ESTATE)
        result = self.bot.run_bot(self.hub_id, BotType.REAL_ESTATE)
        assert "deals" in result

    def test_run_trading_bot(self):
        self.bot.activate_bot(self.hub_id, BotType.TRADING)
        result = self.bot.run_bot(self.hub_id, BotType.TRADING)
        assert "signals" in result

    def test_run_inactive_bot_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.run_bot(self.hub_id, BotType.MONEY_FINDER)

    def test_active_bots_tracked_in_hub(self):
        self.bot.activate_bot(self.hub_id, BotType.MONEY_FINDER)
        self.bot.activate_bot(self.hub_id, BotType.REFERRAL)
        hub = self.bot.get_hub(self.hub_id)
        assert BotType.MONEY_FINDER in hub.active_bots
        assert BotType.REFERRAL in hub.active_bots


# ---------------------------------------------------------------------------
# 10. DreamCoin
# ---------------------------------------------------------------------------

class TestDreamCoin:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        self.hub_id = self.bot.create_hub("Test Hub")
        self.bot.add_member(self.hub_id, "alice", "Alice")

    def test_award_dreamcoin(self):
        balance = self.bot.award_dreamcoin(self.hub_id, "alice", 100.0)
        assert balance == 100.0

    def test_award_dreamcoin_accumulates(self):
        self.bot.award_dreamcoin(self.hub_id, "alice", 100.0)
        balance = self.bot.award_dreamcoin(self.hub_id, "alice", 50.0)
        assert balance == 150.0

    def test_zero_dreamcoin_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.award_dreamcoin(self.hub_id, "alice", 0.0)

    def test_supply_info(self):
        self.bot.award_dreamcoin(self.hub_id, "alice", 500.0)
        info = self.bot.dreamcoin_supply_info()
        assert info["total_supply"] == 1_000_000.0
        assert info["circulating"] == 500.0
        assert info["remaining"] == 999_500.0

    def test_dreamcoin_requires_enterprise(self):
        bot = WealthSystemBot(tier=Tier.PRO)
        hub_id = bot.create_hub("Hub")
        bot.add_member(hub_id, "alice", "Alice")
        with pytest.raises(WealthSystemBotTierError):
            bot.award_dreamcoin(hub_id, "alice", 100.0)

    def test_exhaust_supply_raises(self):
        self.bot.award_dreamcoin(self.hub_id, "alice", 999_999.0)
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.award_dreamcoin(self.hub_id, "alice", 2.0)


# ---------------------------------------------------------------------------
# 11. Analytics & dashboard
# ---------------------------------------------------------------------------

class TestAnalyticsDashboard:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub_id = self.bot.create_hub("Test Hub")
        self.bot.add_member(self.hub_id, "alice", "Alice", contribution_usd=5000.0)

    def test_hub_dashboard_returns_dict(self):
        result = self.bot.hub_dashboard(self.hub_id)
        assert isinstance(result, dict)

    def test_hub_dashboard_fields(self):
        result = self.bot.hub_dashboard(self.hub_id)
        for key in ("hub_id", "name", "treasury_usd", "member_count", "allocation"):
            assert key in result

    def test_hub_dashboard_treasury_value(self):
        result = self.bot.hub_dashboard(self.hub_id)
        assert result["treasury_usd"] == pytest.approx(5000.0)

    def test_member_portfolio_returns_dict(self):
        result = self.bot.member_portfolio(self.hub_id, "alice")
        assert isinstance(result, dict)
        assert result["user_id"] == "alice"

    def test_platform_analytics(self):
        self.bot.create_hub("Hub 2")
        result = self.bot.platform_analytics()
        assert result["total_hubs"] == 2
        assert result["total_members"] == 1

    def test_platform_analytics_requires_pro(self):
        bot = WealthSystemBot(tier=Tier.FREE)
        with pytest.raises(WealthSystemBotTierError):
            bot.platform_analytics()

    def test_upgrade_info_returns_dict(self):
        result = self.bot.upgrade_info()
        assert "current_tier" in result
        assert "upgrade_to" in result


# ---------------------------------------------------------------------------
# 12. Pitch deck structure
# ---------------------------------------------------------------------------

class TestPitchDeck:
    def setup_method(self):
        from docs.pitch_deck.pitch_deck import build_dreamco_pitch_deck, SlideType
        self.deck = build_dreamco_pitch_deck()
        self.SlideType = SlideType

    def test_deck_has_12_slides(self):
        assert self.deck.slide_count() == 12

    def test_deck_title(self):
        assert "DreamCo" in self.deck.title

    def test_slide_numbers_sequential(self):
        for i, slide in enumerate(self.deck.slides, start=1):
            assert slide.slide_number == i

    def test_all_slide_types_present(self):
        types = {s.slide_type for s in self.deck.slides}
        expected = {
            self.SlideType.VISION,
            self.SlideType.PROBLEM,
            self.SlideType.SOLUTION,
            self.SlideType.MARKET,
            self.SlideType.HOW_IT_WORKS,
            self.SlideType.PRODUCT,
            self.SlideType.TECHNOLOGY,
            self.SlideType.REVENUE,
            self.SlideType.GROWTH,
            self.SlideType.COMPLIANCE,
            self.SlideType.ASK,
            self.SlideType.CLOSING,
        }
        assert expected == types

    def test_each_slide_has_bullets(self):
        for slide in self.deck.slides:
            assert len(slide.bullets) > 0

    def test_each_slide_has_headline(self):
        for slide in self.deck.slides:
            assert len(slide.headline) > 0

    def test_render_returns_string(self):
        text = self.deck.render()
        assert isinstance(text, str)
        assert "DreamCo" in text

    def test_to_markdown_returns_string(self):
        md = self.deck.to_markdown()
        assert "# DreamCo" in md
        assert "## Slide 1:" in md

    def test_summary_dict(self):
        summary = self.deck.summary()
        assert summary["total_slides"] == 12
        assert summary["company"] == "DreamCo Technologies"

    def test_slide_to_dict(self):
        slide = self.deck.get_slide(1)
        d = slide.to_dict()
        assert d["slide_number"] == 1
        assert "bullets" in d

    def test_render_individual_slide(self):
        slide = self.deck.get_slide(1)
        text = slide.render()
        assert "Slide 1:" in text
        assert len(text) > 0

    def test_get_slide_none_for_bad_number(self):
        assert self.deck.get_slide(99) is None


# ---------------------------------------------------------------------------
# 13. UI Screens
# ---------------------------------------------------------------------------

class TestHomeDashboardScreen:
    def setup_method(self):
        from screens.home_dashboard import HomeDashboardScreen, HubCard, EarningsSummary
        self.HomeDashboardScreen = HomeDashboardScreen
        self.HubCard = HubCard
        self.EarningsSummary = EarningsSummary

    def test_instantiation(self):
        screen = self.HomeDashboardScreen(user_name="Alice", total_balance_usd=1000.0)
        assert screen.user_name == "Alice"

    def test_add_hub(self):
        screen = self.HomeDashboardScreen()
        screen.add_hub(self.HubCard("h1", "My Hub", 5000.0, 3, 2))
        assert screen.hub_count() == 1

    def test_render_returns_string(self):
        screen = self.HomeDashboardScreen(user_name="Alice")
        text = screen.render()
        assert isinstance(text, str)
        assert "DREAMCO" in text

    def test_to_dict_keys(self):
        screen = self.HomeDashboardScreen(user_name="Alice", total_balance_usd=500.0)
        d = screen.to_dict()
        for key in ("screen", "route", "user_name", "total_balance_usd", "wealth_hubs"):
            assert key in d

    def test_demo_class_method(self):
        screen = self.HomeDashboardScreen.demo()
        assert screen.hub_count() == 2
        assert screen.total_balance_usd > 0


class TestWealthHubScreen:
    def setup_method(self):
        from screens.wealth_hub_screen import WealthHubScreen, MemberRow, ProposalRow
        self.WealthHubScreen = WealthHubScreen
        self.MemberRow = MemberRow
        self.ProposalRow = ProposalRow

    def test_instantiation(self):
        screen = self.WealthHubScreen("h1", "Test Hub", treasury_usd=8500.0)
        assert screen.name == "Test Hub"

    def test_add_member(self):
        screen = self.WealthHubScreen("h1", "Hub")
        screen.add_member(self.MemberRow("alice", "Alice", 3000.0, 35.0, 420.0))
        assert screen.member_count() == 1

    def test_render_returns_string(self):
        screen = self.WealthHubScreen("h1", "Hub", treasury_usd=5000.0)
        text = screen.render()
        assert "WEALTH HUB" in text

    def test_demo_class_method(self):
        screen = self.WealthHubScreen.demo()
        assert screen.member_count() == 4

    def test_to_dict_keys(self):
        screen = self.WealthHubScreen("h1", "Hub")
        d = screen.to_dict()
        assert "treasury_usd" in d
        assert "members" in d


class TestBotControlCenterScreen:
    def setup_method(self):
        from screens.bot_control_center import BotControlCenterScreen, BotCard
        self.BotControlCenterScreen = BotControlCenterScreen
        self.BotCard = BotCard

    def test_instantiation(self):
        screen = self.BotControlCenterScreen("h1", "Test Hub")
        assert screen.hub_name == "Test Hub"

    def test_add_bot(self):
        screen = self.BotControlCenterScreen("h1", "Hub")
        screen.add_bot(self.BotCard("money_finder", "💰 Money Finder", "Desc"))
        assert screen.get_bot("money_finder") is not None

    def test_active_bots_empty_initially(self):
        screen = self.BotControlCenterScreen("h1", "Hub")
        assert screen.active_bots() == []

    def test_total_earnings(self):
        screen = self.BotControlCenterScreen("h1", "Hub")
        screen.add_bot(self.BotCard("b1", "Bot 1", "D", is_active=True, total_earnings_usd=100.0))
        screen.add_bot(self.BotCard("b2", "Bot 2", "D", is_active=True, total_earnings_usd=200.0))
        assert screen.total_earnings() == pytest.approx(300.0)

    def test_render_returns_string(self):
        screen = self.BotControlCenterScreen("h1", "Hub")
        text = screen.render()
        assert "BOT CONTROL CENTER" in text

    def test_demo_class_method(self):
        screen = self.BotControlCenterScreen.demo()
        assert len(screen._bots) == 5


class TestWalletScreen:
    def setup_method(self):
        from screens.wallet_screen import WalletScreen, Transaction, TransactionType
        self.WalletScreen = WalletScreen
        self.Transaction = Transaction
        self.TransactionType = TransactionType

    def test_instantiation(self):
        screen = self.WalletScreen("alice", "Alice", usd_balance=1000.0)
        assert screen.usd_balance == 1000.0

    def test_add_transaction(self):
        screen = self.WalletScreen("alice", "Alice")
        screen.add_transaction(self.Transaction(
            "tx1", self.TransactionType.DEPOSIT, amount_usd=500.0
        ))
        assert screen.transaction_count() == 1

    def test_total_deposited(self):
        screen = self.WalletScreen("alice", "Alice")
        screen.add_transaction(self.Transaction("t1", self.TransactionType.DEPOSIT, amount_usd=1000.0))
        screen.add_transaction(self.Transaction("t2", self.TransactionType.DEPOSIT, amount_usd=500.0))
        assert screen.total_deposited() == pytest.approx(1500.0)

    def test_total_dividends(self):
        screen = self.WalletScreen("alice", "Alice")
        screen.add_transaction(self.Transaction("t1", self.TransactionType.DIVIDEND, amount_usd=320.0))
        assert screen.total_dividends() == pytest.approx(320.0)

    def test_render_returns_string(self):
        screen = self.WalletScreen("alice", "Alice", usd_balance=2000.0)
        text = screen.render()
        assert "WALLET" in text

    def test_demo_class_method(self):
        screen = self.WalletScreen.demo()
        assert screen.transaction_count() == 5

    def test_to_dict_keys(self):
        screen = self.WalletScreen("alice", "Alice")
        d = screen.to_dict()
        assert "usd_balance" in d
        assert "transactions" in d


class TestGovernancePanelScreen:
    def setup_method(self):
        from screens.governance_panel import GovernancePanelScreen, ProposalDetail
        from datetime import datetime, timezone
        self.GovernancePanelScreen = GovernancePanelScreen
        self.ProposalDetail = ProposalDetail
        self.dt = datetime(2025, 1, 1, tzinfo=timezone.utc)

    def test_instantiation(self):
        screen = self.GovernancePanelScreen("h1", "Test Hub")
        assert screen.hub_name == "Test Hub"

    def test_add_proposal(self):
        screen = self.GovernancePanelScreen("h1", "Hub")
        screen.add_proposal(self.ProposalDetail(
            "p1", "Test", "Desc", "investment", "Alice", 2, 1, 4, "open",
            created_at=self.dt,
        ))
        assert len(screen.open_proposals()) == 1

    def test_closed_proposals_filtered(self):
        screen = self.GovernancePanelScreen("h1", "Hub")
        screen.add_proposal(self.ProposalDetail(
            "p1", "Open", "", "investment", "Alice", 2, 1, 4, "open", created_at=self.dt
        ))
        screen.add_proposal(self.ProposalDetail(
            "p2", "Passed", "", "payout", "Bob", 3, 0, 4, "passed", created_at=self.dt
        ))
        assert len(screen.open_proposals()) == 1
        assert len(screen.closed_proposals()) == 1

    def test_render_returns_string(self):
        screen = self.GovernancePanelScreen("h1", "Hub")
        text = screen.render()
        assert "GOVERNANCE PANEL" in text

    def test_participation_pct(self):
        p = self.ProposalDetail(
            "p1", "Test", "", "investment", "Alice", 2, 2, 4, "open", created_at=self.dt
        )
        assert p.participation_pct() == pytest.approx(100.0)

    def test_approval_pct(self):
        p = self.ProposalDetail(
            "p1", "Test", "", "investment", "Alice", 3, 1, 4, "open", created_at=self.dt
        )
        assert p.approval_pct() == pytest.approx(75.0)

    def test_demo_class_method(self):
        screen = self.GovernancePanelScreen.demo()
        assert len(screen.open_proposals()) == 2
        assert len(screen.closed_proposals()) == 2


class TestInvestmentDashboardScreen:
    def setup_method(self):
        from screens.investment_dashboard import InvestmentDashboardScreen, AssetHolding
        self.InvestmentDashboardScreen = InvestmentDashboardScreen
        self.AssetHolding = AssetHolding

    def test_instantiation(self):
        screen = self.InvestmentDashboardScreen("h1", "Hub", total_invested_usd=10000.0)
        assert screen.total_invested_usd == 10000.0

    def test_add_holding(self):
        screen = self.InvestmentDashboardScreen("h1", "Hub", total_invested_usd=1000.0)
        screen.add_holding(self.AssetHolding(
            "gold", "Gold", "Commodity", "wealth_protection",
            invested_usd=1000.0, current_value_usd=1100.0, quantity=0.5, unit_label="oz"
        ))
        assert len(screen._holdings) == 1

    def test_total_gain_loss(self):
        screen = self.InvestmentDashboardScreen("h1", "Hub", total_invested_usd=1000.0)
        screen.add_holding(self.AssetHolding(
            "gold", "Gold", "Commodity", "wealth_protection",
            invested_usd=1000.0, current_value_usd=1100.0
        ))
        assert screen.total_gain_loss() == pytest.approx(100.0)

    def test_portfolio_roi_pct(self):
        screen = self.InvestmentDashboardScreen("h1", "Hub", total_invested_usd=1000.0)
        screen.add_holding(self.AssetHolding(
            "gold", "Gold", "Commodity", "wealth_protection",
            invested_usd=1000.0, current_value_usd=1100.0
        ))
        assert screen.portfolio_roi_pct() == pytest.approx(10.0)

    def test_best_performer(self):
        screen = self.InvestmentDashboardScreen("h1", "Hub", total_invested_usd=2000.0)
        screen.add_holding(self.AssetHolding(
            "gold", "Gold", "Commodity", "wealth_protection",
            invested_usd=1000.0, current_value_usd=1200.0  # +20%
        ))
        screen.add_holding(self.AssetHolding(
            "btc", "Bitcoin", "Crypto", "high_growth",
            invested_usd=1000.0, current_value_usd=900.0  # -10%
        ))
        best = screen.best_performer()
        assert best.name == "Gold"

    def test_render_returns_string(self):
        screen = self.InvestmentDashboardScreen("h1", "Hub", total_invested_usd=8500.0)
        text = screen.render()
        assert "INVESTMENT DASHBOARD" in text

    def test_demo_class_method(self):
        screen = self.InvestmentDashboardScreen.demo()
        assert len(screen._holdings) == 7

    def test_holdings_by_tier(self):
        screen = self.InvestmentDashboardScreen.demo()
        protection = screen.holdings_by_tier("wealth_protection")
        assert len(protection) == 3


class TestReferralSystemScreen:
    def setup_method(self):
        from screens.referral_system import ReferralSystemScreen, ReferralProgram, TeamNode
        self.ReferralSystemScreen = ReferralSystemScreen
        self.ReferralProgram = ReferralProgram
        self.TeamNode = TeamNode

    def test_instantiation(self):
        screen = self.ReferralSystemScreen("alice", "Alice", "ALICE2025")
        assert screen.invite_code == "ALICE2025"

    def test_invite_link(self):
        screen = self.ReferralSystemScreen("alice", "Alice", "ALICE2025")
        assert "ALICE2025" in screen.invite_link

    def test_auto_invite_code(self):
        screen = self.ReferralSystemScreen("alice123", "Alice")
        assert "ALICE1" in screen.invite_code

    def test_add_program(self):
        screen = self.ReferralSystemScreen("alice", "Alice")
        screen.add_program(self.ReferralProgram("wisely", "Wisely", 25.0, 5, 125.0))
        assert len(screen._programs) == 1

    def test_total_earnings(self):
        screen = self.ReferralSystemScreen("alice", "Alice")
        screen.add_program(self.ReferralProgram("a", "A", 10.0, 5, 100.0))
        screen.add_program(self.ReferralProgram("b", "B", 20.0, 3, 200.0))
        assert screen.total_earnings() == pytest.approx(300.0)

    def test_add_team_member(self):
        screen = self.ReferralSystemScreen("alice", "Alice")
        screen.add_team_member(self.TeamNode("bob", "Bob", level=1))
        assert screen.direct_team_size() == 1

    def test_render_returns_string(self):
        screen = self.ReferralSystemScreen("alice", "Alice")
        text = screen.render()
        assert "REFERRAL SYSTEM" in text

    def test_demo_class_method(self):
        screen = self.ReferralSystemScreen.demo()
        assert len(screen._programs) == 4
        assert screen.direct_team_size() == 3

    def test_to_dict_keys(self):
        screen = self.ReferralSystemScreen("alice", "Alice")
        d = screen.to_dict()
        assert "invite_link" in d
        assert "programs" in d
        assert "leaderboard" in d
