"""
Tests for bots/wealth_system_bot/wealth_system_bot.py

Covers:
  1. Tiers
  2. Wealth Hub Management
  3. Treasury Management
  4. Governance / Voting
  5. Bot Framework
  6. Asset Allocation
  7. Compliance / KYC
  8. DreamCoin Staking
  9. Analytics
  10. Chat Interface
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.wealth_system_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_JOIN_HUB,
    FEATURE_VIEW_TREASURY,
    FEATURE_BASIC_VOTING,
    FEATURE_CREATE_HUB,
    FEATURE_INCOME_BOTS,
    FEATURE_ASSET_BOTS,
    FEATURE_DIVIDEND_TRACKING,
    FEATURE_ASSET_ALLOCATION,
    FEATURE_COMMERCE_BOTS,
    FEATURE_FINANCE_BOTS,
    FEATURE_DREAMCOIN_STAKING,
    FEATURE_ADVANCED_ANALYTICS,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
)
from bots.wealth_system_bot.wealth_system_bot import (
    WealthSystemBot,
    WealthSystemBotError,
    WealthSystemBotTierError,
    WealthSystemBotNotFoundError,
    WealthSystemBotValidationError,
    BotType,
    IncomeBot,
    AssetBot,
    CommerceBot,
    FinanceBot,
    AssetTier,
    GovernanceVoteType,
    PayoutMode,
    ComplianceStatus,
    Member,
    WealthHub,
    GovernanceVote,
    BotEarnings,
    ComplianceRecord,
    DividendPayout,
)


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        assert len(list_tiers()) == 3

    def test_free_price_zero(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0

    def test_pro_price(self):
        assert get_tier_config(Tier.PRO).price_usd_monthly == 29.0

    def test_enterprise_price(self):
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 99.0

    def test_free_has_join_hub(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_JOIN_HUB)

    def test_free_has_view_treasury(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_VIEW_TREASURY)

    def test_free_has_basic_voting(self):
        assert get_tier_config(Tier.FREE).has_feature(FEATURE_BASIC_VOTING)

    def test_free_lacks_create_hub(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_CREATE_HUB)

    def test_free_lacks_income_bots(self):
        assert not get_tier_config(Tier.FREE).has_feature(FEATURE_INCOME_BOTS)

    def test_pro_has_create_hub(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_CREATE_HUB)

    def test_pro_has_income_bots(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_INCOME_BOTS)

    def test_pro_has_asset_bots(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_ASSET_BOTS)

    def test_pro_has_dividend_tracking(self):
        assert get_tier_config(Tier.PRO).has_feature(FEATURE_DIVIDEND_TRACKING)

    def test_pro_lacks_commerce_bots(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_COMMERCE_BOTS)

    def test_pro_lacks_dreamcoin_staking(self):
        assert not get_tier_config(Tier.PRO).has_feature(FEATURE_DREAMCOIN_STAKING)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in (
            FEATURE_COMMERCE_BOTS, FEATURE_FINANCE_BOTS,
            FEATURE_DREAMCOIN_STAKING, FEATURE_ADVANCED_ANALYTICS,
            FEATURE_WHITE_LABEL, FEATURE_STRIPE_BILLING,
        ):
            assert cfg.has_feature(feat), f"Expected feature: {feat}"

    def test_enterprise_unlimited_hubs(self):
        assert get_tier_config(Tier.ENTERPRISE).is_unlimited_hubs()

    def test_pro_max_hubs_is_three(self):
        assert get_tier_config(Tier.PRO).max_hubs == 3

    def test_free_max_hubs_is_zero(self):
        assert get_tier_config(Tier.FREE).max_hubs == 0

    def test_upgrade_path_free_to_pro(self):
        next_tier = get_upgrade_path(Tier.FREE)
        assert next_tier.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        next_tier = get_upgrade_path(Tier.PRO)
        assert next_tier.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None


# ===========================================================================
# 2. Wealth Hub Management
# ===========================================================================

class TestWealthHubManagement:
    def setup_method(self):
        self.pro_bot = WealthSystemBot(tier=Tier.PRO)
        self.free_bot = WealthSystemBot(tier=Tier.FREE)
        self.ent_bot = WealthSystemBot(tier=Tier.ENTERPRISE)

    def _make_hub(self, bot=None, owner="owner1", name="Test Hub"):
        bot = bot or self.pro_bot
        return bot.create_hub(owner, name)

    def test_create_hub_returns_wealth_hub(self):
        hub = self._make_hub()
        assert isinstance(hub, WealthHub)

    def test_create_hub_sets_name(self):
        hub = self._make_hub(name="Alpha Hub")
        assert hub.name == "Alpha Hub"

    def test_create_hub_sets_owner(self):
        hub = self._make_hub(owner="alice")
        assert hub.owner_id == "alice"

    def test_create_hub_has_id(self):
        hub = self._make_hub()
        assert hub.hub_id

    def test_free_tier_cannot_create_hub(self):
        with pytest.raises(WealthSystemBotTierError):
            self.free_bot.create_hub("owner1", "My Hub")

    def test_pro_hub_limit_three(self):
        for i in range(3):
            self._make_hub(name=f"Hub {i}")
        with pytest.raises(WealthSystemBotTierError):
            self._make_hub(name="Hub 4")

    def test_enterprise_can_exceed_three_hubs(self):
        for i in range(5):
            self._make_hub(bot=self.ent_bot, name=f"Hub {i}")
        assert len(self.ent_bot.list_hubs()) == 5

    def test_get_hub_returns_correct_hub(self):
        hub = self._make_hub()
        fetched = self.pro_bot.get_hub(hub.hub_id)
        assert fetched.hub_id == hub.hub_id

    def test_get_hub_missing_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.pro_bot.get_hub("nonexistent")

    def test_list_hubs_all(self):
        self._make_hub(name="A")
        self._make_hub(name="B")
        assert len(self.pro_bot.list_hubs()) == 2

    def test_list_hubs_filter_by_owner(self):
        self.pro_bot.create_hub("alice", "Alice Hub")
        self.pro_bot.create_hub("bob", "Bob Hub")
        alice_hubs = self.pro_bot.list_hubs(owner_id="alice")
        assert len(alice_hubs) == 1
        assert alice_hubs[0].owner_id == "alice"

    def test_add_member_returns_member(self):
        hub = self._make_hub()
        m = self.pro_bot.add_member(hub.hub_id, "m1", "Alice", "a@b.com", 1000)
        assert isinstance(m, Member)

    def test_add_member_updates_treasury(self):
        hub = self._make_hub()
        self.pro_bot.add_member(hub.hub_id, "m1", "Alice", "a@b.com", 500)
        assert hub.treasury_usd == 500

    def test_add_duplicate_member_raises(self):
        hub = self._make_hub()
        self.pro_bot.add_member(hub.hub_id, "m1", "Alice", "a@b.com", 100)
        with pytest.raises(WealthSystemBotValidationError):
            self.pro_bot.add_member(hub.hub_id, "m1", "Alice", "a@b.com", 100)

    def test_add_member_negative_contribution_raises(self):
        hub = self._make_hub()
        with pytest.raises(WealthSystemBotValidationError):
            self.pro_bot.add_member(hub.hub_id, "m1", "Alice", "a@b.com", -50)

    def test_get_member_returns_member(self):
        hub = self._make_hub()
        self.pro_bot.add_member(hub.hub_id, "m1", "Alice", "a@b.com", 100)
        m = self.pro_bot.get_member(hub.hub_id, "m1")
        assert m.member_id == "m1"

    def test_get_member_missing_raises(self):
        hub = self._make_hub()
        with pytest.raises(WealthSystemBotNotFoundError):
            self.pro_bot.get_member(hub.hub_id, "ghost")

    def test_payout_mode_default_monthly(self):
        hub = self._make_hub()
        assert hub.payout_mode == PayoutMode.MONTHLY

    def test_payout_mode_custom(self):
        hub = self.pro_bot.create_hub("owner", "Hub", payout_mode=PayoutMode.WEEKLY)
        assert hub.payout_mode == PayoutMode.WEEKLY


# ===========================================================================
# 3. Treasury Management
# ===========================================================================

class TestTreasuryManagement:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub = self.bot.create_hub("owner1", "Wealth Hub")
        self.bot.add_member(self.hub.hub_id, "m1", "Alice", "a@ex.com", 1000)
        self.bot.add_member(self.hub.hub_id, "m2", "Bob", "b@ex.com", 1000)

    def test_ownership_pct_equal_two_members(self):
        m1 = self.bot.get_member(self.hub.hub_id, "m1")
        m2 = self.bot.get_member(self.hub.hub_id, "m2")
        assert abs(m1.ownership_pct - 50.0) < 0.01
        assert abs(m2.ownership_pct - 50.0) < 0.01

    def test_deposit_updates_treasury(self):
        result = self.bot.deposit(self.hub.hub_id, "m1", 500)
        assert result["treasury_usd"] == 2500

    def test_deposit_recalculates_ownership(self):
        self.bot.deposit(self.hub.hub_id, "m1", 1000)
        m1 = self.bot.get_member(self.hub.hub_id, "m1")
        # m1 has 2000, m2 has 1000 → m1 = 66.67%
        assert abs(m1.ownership_pct - 66.666667) < 0.01

    def test_deposit_zero_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.deposit(self.hub.hub_id, "m1", 0)

    def test_deposit_negative_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.deposit(self.hub.hub_id, "m1", -100)

    def test_deposit_missing_member_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.deposit(self.hub.hub_id, "ghost", 100)

    def test_get_treasury_snapshot_returns_dict(self):
        snap = self.bot.get_treasury_snapshot(self.hub.hub_id)
        assert isinstance(snap, dict)

    def test_treasury_snapshot_has_required_keys(self):
        snap = self.bot.get_treasury_snapshot(self.hub.hub_id)
        for key in ("treasury_usd", "members", "asset_breakdown", "payout_mode"):
            assert key in snap

    def test_treasury_snapshot_correct_balance(self):
        snap = self.bot.get_treasury_snapshot(self.hub.hub_id)
        assert snap["treasury_usd"] == 2000

    def test_treasury_snapshot_free_tier(self):
        free_bot = WealthSystemBot(tier=Tier.FREE)
        # FREE can view treasury but cannot create hub; use pro_bot's hub via different instance
        # We just test that FREE tier has the feature
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_VIEW_TREASURY)

    def test_allocate_assets_updates_hub(self):
        result = self.bot.allocate_assets(self.hub.hub_id, 50, 30, 20)
        assert result["asset_allocation"]["stability"] == 50

    def test_allocate_assets_invalid_sum_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.allocate_assets(self.hub.hub_id, 50, 30, 30)

    def test_allocate_assets_free_tier_blocked(self):
        free_bot = WealthSystemBot(tier=Tier.FREE)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.allocate_assets(self.hub.hub_id, 50, 30, 20)

    def test_distribute_dividends_returns_payouts(self):
        payouts = self.bot.distribute_dividends(self.hub.hub_id, 1000)
        assert len(payouts) == 2

    def test_distribute_dividends_proportional(self):
        payouts = self.bot.distribute_dividends(self.hub.hub_id, 1000)
        amounts = {p.member_id: p.amount_usd for p in payouts}
        assert abs(amounts["m1"] - 500.0) < 0.1
        assert abs(amounts["m2"] - 500.0) < 0.1

    def test_distribute_dividends_updates_hub_total(self):
        self.bot.distribute_dividends(self.hub.hub_id, 500)
        assert self.hub.dividends_paid_usd == 500

    def test_distribute_dividends_zero_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.distribute_dividends(self.hub.hub_id, 0)

    def test_distribute_dividends_free_tier_blocked(self):
        free_bot = WealthSystemBot(tier=Tier.FREE)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.distribute_dividends(self.hub.hub_id, 100)


# ===========================================================================
# 4. Governance / Voting
# ===========================================================================

class TestGovernance:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub = self.bot.create_hub("owner1", "Gov Hub")
        self.bot.add_member(self.hub.hub_id, "m1", "Alice", "a@ex.com", 600)
        self.bot.add_member(self.hub.hub_id, "m2", "Bob", "b@ex.com", 400)
        self.hid = self.hub.hub_id

    def _create_vote(self):
        return self.bot.create_vote(
            self.hid, "m1", GovernanceVoteType.INVESTMENT,
            "Invest in real estate?", ["yes", "no"],
        )

    def test_create_vote_returns_governance_vote(self):
        vote = self._create_vote()
        assert isinstance(vote, GovernanceVote)

    def test_create_vote_has_id(self):
        vote = self._create_vote()
        assert vote.vote_id

    def test_create_vote_non_member_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.create_vote(
                self.hid, "ghost", GovernanceVoteType.INVESTMENT, "X", ["yes"]
            )

    def test_create_vote_empty_options_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.create_vote(self.hid, "m1", GovernanceVoteType.INVESTMENT, "X", [])

    def test_cast_vote_records_choice(self):
        vote = self._create_vote()
        updated = self.bot.cast_vote(self.hid, vote.vote_id, "m1", "yes")
        assert updated.votes_cast["m1"] == "yes"

    def test_cast_vote_invalid_option_raises(self):
        vote = self._create_vote()
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.cast_vote(self.hid, vote.vote_id, "m1", "maybe")

    def test_cast_vote_duplicate_raises(self):
        vote = self._create_vote()
        self.bot.cast_vote(self.hid, vote.vote_id, "m1", "yes")
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.cast_vote(self.hid, vote.vote_id, "m1", "no")

    def test_cast_vote_missing_vote_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.cast_vote(self.hid, "fake_vote", "m1", "yes")

    def test_cast_vote_on_resolved_raises(self):
        vote = self._create_vote()
        self.bot.cast_vote(self.hid, vote.vote_id, "m1", "yes")
        self.bot.resolve_vote(self.hid, vote.vote_id)
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.cast_vote(self.hid, vote.vote_id, "m2", "no")

    def test_resolve_vote_sets_result(self):
        vote = self._create_vote()
        self.bot.cast_vote(self.hid, vote.vote_id, "m1", "yes")
        self.bot.cast_vote(self.hid, vote.vote_id, "m2", "no")
        resolved = self.bot.resolve_vote(self.hid, vote.vote_id)
        assert resolved.result in ("yes", "no")
        assert resolved.is_resolved

    def test_resolve_vote_majority_wins(self):
        bot = WealthSystemBot(tier=Tier.PRO)
        hub = bot.create_hub("o", "Hub")
        bot.add_member(hub.hub_id, "a", "A", "a@a.com", 100)
        bot.add_member(hub.hub_id, "b", "B", "b@b.com", 100)
        bot.add_member(hub.hub_id, "c", "C", "c@c.com", 100)
        vote = bot.create_vote(hub.hub_id, "a", GovernanceVoteType.RISK_LEVEL, "P", ["x", "y"])
        bot.cast_vote(hub.hub_id, vote.vote_id, "a", "x")
        bot.cast_vote(hub.hub_id, vote.vote_id, "b", "x")
        bot.cast_vote(hub.hub_id, vote.vote_id, "c", "y")
        resolved = bot.resolve_vote(hub.hub_id, vote.vote_id)
        assert resolved.result == "x"

    def test_resolve_missing_vote_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.resolve_vote(self.hid, "bad_id")

    def test_resolve_already_resolved_returns_same(self):
        vote = self._create_vote()
        self.bot.cast_vote(self.hid, vote.vote_id, "m1", "yes")
        r1 = self.bot.resolve_vote(self.hid, vote.vote_id)
        r2 = self.bot.resolve_vote(self.hid, vote.vote_id)
        assert r1.vote_id == r2.vote_id

    def test_list_votes_returns_all(self):
        self._create_vote()
        self._create_vote()
        assert len(self.bot.list_votes(self.hid)) == 2

    def test_list_votes_resolved_only(self):
        vote = self._create_vote()
        self._create_vote()
        self.bot.cast_vote(self.hid, vote.vote_id, "m1", "yes")
        self.bot.resolve_vote(self.hid, vote.vote_id)
        resolved = self.bot.list_votes(self.hid, resolved_only=True)
        assert len(resolved) == 1
        assert resolved[0].is_resolved


# ===========================================================================
# 5. Bot Framework
# ===========================================================================

class TestBotFramework:
    def setup_method(self):
        self.pro_bot = WealthSystemBot(tier=Tier.PRO)
        self.ent_bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        self.free_bot = WealthSystemBot(tier=Tier.FREE)
        self.hub = self.pro_bot.create_hub("owner1", "Bot Hub")
        self.hid = self.hub.hub_id
        self.ent_hub = self.ent_bot.create_hub("owner2", "Ent Hub")
        self.ehid = self.ent_hub.hub_id

    def test_activate_income_bot_pro(self):
        be = self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        assert isinstance(be, BotEarnings)

    def test_activate_asset_bot_pro(self):
        be = self.pro_bot.activate_bot(self.hid, BotType.ASSET, AssetBot.FORECLOSURE.value)
        assert be.bot_type == BotType.ASSET

    def test_activate_commerce_bot_enterprise(self):
        be = self.ent_bot.activate_bot(self.ehid, BotType.COMMERCE, CommerceBot.DROPSHIPPING.value)
        assert be.sub_type == CommerceBot.DROPSHIPPING.value

    def test_activate_finance_bot_enterprise(self):
        be = self.ent_bot.activate_bot(self.ehid, BotType.FINANCE, FinanceBot.GRANT_FINDER.value)
        assert be.bot_type == BotType.FINANCE

    def test_pro_cannot_activate_commerce_bot(self):
        with pytest.raises(WealthSystemBotTierError):
            self.pro_bot.activate_bot(self.hid, BotType.COMMERCE, CommerceBot.DROPSHIPPING.value)

    def test_pro_cannot_activate_finance_bot(self):
        with pytest.raises(WealthSystemBotTierError):
            self.pro_bot.activate_bot(self.hid, BotType.FINANCE, FinanceBot.STOCK_TRADING.value)

    def test_free_cannot_activate_any_bot(self):
        with pytest.raises(WealthSystemBotTierError):
            self.free_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)

    def test_invalid_sub_type_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.pro_bot.activate_bot(self.hid, BotType.INCOME, "magic_bot")

    def test_run_bot_returns_bot_earnings(self):
        self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.AFFILIATE.value)
        be = self.pro_bot.run_bot(self.hid, BotType.INCOME, IncomeBot.AFFILIATE.value)
        assert isinstance(be, BotEarnings)

    def test_run_bot_increments_runs(self):
        self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.LEAD_GENERATION.value)
        self.pro_bot.run_bot(self.hid, BotType.INCOME, IncomeBot.LEAD_GENERATION.value)
        self.pro_bot.run_bot(self.hid, BotType.INCOME, IncomeBot.LEAD_GENERATION.value)
        be = self.pro_bot.get_bot_earnings(self.hid)
        assert be[0].runs == 2

    def test_run_bot_adds_to_treasury(self):
        before = self.hub.treasury_usd
        self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        self.pro_bot.run_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        assert self.hub.treasury_usd > before

    def test_run_bot_earnings_in_range(self):
        self.pro_bot.activate_bot(self.hid, BotType.ASSET, AssetBot.REAL_ESTATE_DEALS.value)
        be = self.pro_bot.run_bot(self.hid, BotType.ASSET, AssetBot.REAL_ESTATE_DEALS.value)
        assert be.earnings_usd >= 10

    def test_run_bot_sets_last_run_at(self):
        self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        be = self.pro_bot.run_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        assert be.last_run_at is not None

    def test_run_unactivated_bot_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.pro_bot.run_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)

    def test_get_bot_earnings_returns_list(self):
        self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        self.pro_bot.activate_bot(self.hid, BotType.ASSET, AssetBot.SECTION_8_RENTAL.value)
        earnings = self.pro_bot.get_bot_earnings(self.hid)
        assert len(earnings) == 2

    def test_activate_same_bot_twice_returns_same(self):
        be1 = self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        be2 = self.pro_bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        assert be1 is be2


# ===========================================================================
# 6. Asset Allocation
# ===========================================================================

class TestAssetAllocation:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub = self.bot.create_hub("owner1", "Alloc Hub")
        self.bot.add_member(self.hub.hub_id, "m1", "Alice", "a@ex.com", 10000)
        self.hid = self.hub.hub_id

    def test_get_asset_breakdown_returns_dict(self):
        bd = self.bot.get_asset_breakdown(self.hid)
        assert isinstance(bd, dict)

    def test_get_asset_breakdown_has_three_buckets(self):
        bd = self.bot.get_asset_breakdown(self.hid)
        for key in ("stability", "growth", "high_growth"):
            assert key in bd

    def test_asset_breakdown_sums_to_treasury(self):
        bd = self.bot.get_asset_breakdown(self.hid)
        total = sum(bd.values())
        assert abs(total - self.hub.treasury_usd) < 1.0

    def test_allocate_changes_breakdown(self):
        self.bot.allocate_assets(self.hid, 80, 10, 10)
        bd = self.bot.get_asset_breakdown(self.hid)
        assert bd["stability"] == 8000.0

    def test_allocation_sum_not_100_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.bot.allocate_assets(self.hid, 40, 40, 40)

    def test_allocation_sum_exactly_100_ok(self):
        result = self.bot.allocate_assets(self.hid, 33, 33, 34)
        assert result["asset_allocation"]["high_growth"] == 34

    def test_asset_tier_enum_values(self):
        assert AssetTier.STABILITY.value == "stability"
        assert AssetTier.GROWTH.value == "growth"
        assert AssetTier.HIGH_GROWTH.value == "high_growth"


# ===========================================================================
# 7. Compliance / KYC
# ===========================================================================

class TestCompliance:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub = self.bot.create_hub("owner1", "KYC Hub")
        self.bot.add_member(self.hub.hub_id, "m1", "Alice", "a@ex.com", 500)
        self.hid = self.hub.hub_id

    def test_submit_kyc_returns_compliance_record(self):
        rec = self.bot.submit_kyc(self.hid, "m1", "passport")
        assert isinstance(rec, ComplianceRecord)

    def test_submit_kyc_status_pending(self):
        rec = self.bot.submit_kyc(self.hid, "m1", "drivers_license")
        assert rec.status == ComplianceStatus.PENDING

    def test_submit_kyc_missing_member_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.submit_kyc(self.hid, "ghost", "passport")

    def test_review_kyc_approve(self):
        rec = self.bot.submit_kyc(self.hid, "m1", "passport")
        updated = self.bot.review_kyc(rec.record_id, approved=True, notes="Verified")
        assert updated.status == ComplianceStatus.APPROVED
        assert updated.notes == "Verified"

    def test_review_kyc_reject(self):
        rec = self.bot.submit_kyc(self.hid, "m1", "passport")
        updated = self.bot.review_kyc(rec.record_id, approved=False, notes="Blurry image")
        assert updated.status == ComplianceStatus.REJECTED

    def test_review_kyc_missing_record_raises(self):
        with pytest.raises(WealthSystemBotNotFoundError):
            self.bot.review_kyc("nonexistent_id", approved=True)

    def test_get_compliance_records_returns_list(self):
        self.bot.submit_kyc(self.hid, "m1", "passport")
        self.bot.submit_kyc(self.hid, "m1", "utility_bill")
        records = self.bot.get_compliance_records("m1")
        assert len(records) == 2

    def test_get_compliance_records_empty_for_unknown(self):
        records = self.bot.get_compliance_records("nobody")
        assert records == []

    def test_is_kyc_approved_false_before_review(self):
        self.bot.submit_kyc(self.hid, "m1", "passport")
        assert not self.bot.is_kyc_approved("m1")

    def test_is_kyc_approved_true_after_approve(self):
        rec = self.bot.submit_kyc(self.hid, "m1", "passport")
        self.bot.review_kyc(rec.record_id, approved=True)
        assert self.bot.is_kyc_approved("m1")

    def test_is_kyc_approved_false_after_reject(self):
        rec = self.bot.submit_kyc(self.hid, "m1", "passport")
        self.bot.review_kyc(rec.record_id, approved=False)
        assert not self.bot.is_kyc_approved("m1")


# ===========================================================================
# 8. DreamCoin Staking
# ===========================================================================

class TestDreamCoin:
    def setup_method(self):
        self.ent_bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        self.hub = self.ent_bot.create_hub("owner1", "DreamCoin Hub")
        self.ent_bot.add_member(self.hub.hub_id, "m1", "Alice", "a@ex.com", 1000)
        m = self.ent_bot.get_member(self.hub.hub_id, "m1")
        m.dreamcoin_balance = 500.0
        self.hid = self.hub.hub_id

    def test_stake_dreamcoin_returns_dict(self):
        result = self.ent_bot.stake_dreamcoin(self.hid, "m1", 100)
        assert isinstance(result, dict)

    def test_stake_dreamcoin_deducts_balance(self):
        self.ent_bot.stake_dreamcoin(self.hid, "m1", 200)
        assert self.ent_bot.get_dreamcoin_balance("m1") == 300.0

    def test_stake_dreamcoin_records_staked(self):
        result = self.ent_bot.stake_dreamcoin(self.hid, "m1", 100)
        assert result["staked"] == 100
        assert result["total_staked"] == 100

    def test_stake_dreamcoin_cumulative(self):
        self.ent_bot.stake_dreamcoin(self.hid, "m1", 100)
        result = self.ent_bot.stake_dreamcoin(self.hid, "m1", 50)
        assert result["total_staked"] == 150

    def test_stake_zero_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.ent_bot.stake_dreamcoin(self.hid, "m1", 0)

    def test_stake_exceeds_balance_raises(self):
        with pytest.raises(WealthSystemBotValidationError):
            self.ent_bot.stake_dreamcoin(self.hid, "m1", 1000)

    def test_stake_dreamcoin_pro_tier_blocked(self):
        pro_bot = WealthSystemBot(tier=Tier.PRO)
        with pytest.raises(WealthSystemBotTierError):
            pro_bot.stake_dreamcoin(self.hid, "m1", 10)

    def test_stake_dreamcoin_free_tier_blocked(self):
        free_bot = WealthSystemBot(tier=Tier.FREE)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.stake_dreamcoin(self.hid, "m1", 10)

    def test_get_dreamcoin_balance_returns_float(self):
        bal = self.ent_bot.get_dreamcoin_balance("m1")
        assert isinstance(bal, float)

    def test_get_dreamcoin_balance_unknown_member_returns_zero(self):
        bal = self.ent_bot.get_dreamcoin_balance("nobody")
        assert bal == 0.0


# ===========================================================================
# 9. Analytics
# ===========================================================================

class TestAnalytics:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.ENTERPRISE)
        self.hub = self.bot.create_hub("owner1", "Analytics Hub")
        self.bot.add_member(self.hub.hub_id, "m1", "Alice", "a@ex.com", 1000)
        self.hid = self.hub.hub_id

    def test_get_hub_analytics_returns_dict(self):
        result = self.bot.get_hub_analytics(self.hid)
        assert isinstance(result, dict)

    def test_analytics_has_required_keys(self):
        result = self.bot.get_hub_analytics(self.hid)
        for key in (
            "hub_id", "total_members", "treasury_usd",
            "dividends_paid_usd", "bot_earnings_total_usd", "vote_count",
        ):
            assert key in result

    def test_analytics_reflects_member_count(self):
        result = self.bot.get_hub_analytics(self.hid)
        assert result["total_members"] == 1

    def test_analytics_reflects_treasury(self):
        result = self.bot.get_hub_analytics(self.hid)
        assert result["treasury_usd"] == 1000

    def test_analytics_reflects_bot_earnings(self):
        self.bot.activate_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        self.bot.run_bot(self.hid, BotType.INCOME, IncomeBot.REFERRAL.value)
        result = self.bot.get_hub_analytics(self.hid)
        assert result["bot_earnings_total_usd"] > 0

    def test_analytics_free_tier_blocked(self):
        free_bot = WealthSystemBot(tier=Tier.FREE)
        with pytest.raises(WealthSystemBotTierError):
            free_bot.get_hub_analytics(self.hid)

    def test_analytics_pro_tier_blocked(self):
        pro_bot = WealthSystemBot(tier=Tier.PRO)
        with pytest.raises(WealthSystemBotTierError):
            pro_bot.get_hub_analytics(self.hid)

    def test_analytics_reflects_vote_count(self):
        self.bot.create_vote(
            self.hid, "m1", GovernanceVoteType.INVESTMENT, "Proposal", ["yes", "no"]
        )
        result = self.bot.get_hub_analytics(self.hid)
        assert result["vote_count"] == 1


# ===========================================================================
# 10. Chat Interface
# ===========================================================================

class TestChat:
    def setup_method(self):
        self.bot = WealthSystemBot(tier=Tier.PRO)
        self.hub = self.bot.create_hub("owner1", "Chat Hub")
        self.bot.add_member(self.hub.hub_id, "m1", "Alice", "a@ex.com", 1000)
        self.hid = self.hub.hub_id

    def test_chat_treasury(self):
        result = self.bot.chat(self.hid, "m1", "What is my treasury balance?")
        assert "Treasury" in result or "treasury" in result.lower()

    def test_chat_deposit(self):
        result = self.bot.chat(self.hid, "m1", "how do I deposit funds?")
        assert "deposit" in result.lower()

    def test_chat_dividend(self):
        result = self.bot.chat(self.hid, "m1", "tell me about dividends")
        assert "dividend" in result.lower() or "payout" in result.lower()

    def test_chat_vote(self):
        result = self.bot.chat(self.hid, "m1", "I want to vote on something")
        assert "vote" in result.lower() or "governance" in result.lower()

    def test_chat_bot(self):
        result = self.bot.chat(self.hid, "m1", "activate income bot")
        assert "bot" in result.lower() or "income" in result.lower()

    def test_chat_kyc(self):
        result = self.bot.chat(self.hid, "m1", "kyc verification needed")
        assert "kyc" in result.lower() or "compliance" in result.lower()

    def test_chat_dreamcoin(self):
        result = self.bot.chat(self.hid, "m1", "dreamcoin staking")
        assert "dreamcoin" in result.lower() or "stake" in result.lower()

    def test_chat_analytics(self):
        result = self.bot.chat(self.hid, "m1", "show me analytics")
        assert "analytic" in result.lower()

    def test_chat_unknown_message(self):
        result = self.bot.chat(self.hid, "m1", "random unrelated message")
        assert "DreamCo" in result or "Wealth" in result

    def test_chat_returns_string(self):
        result = self.bot.chat(self.hid, "m1", "hello world")
        assert isinstance(result, str)

    def test_chat_balance_keyword(self):
        result = self.bot.chat(self.hid, "m1", "check my balance")
        assert isinstance(result, str) and len(result) > 0
