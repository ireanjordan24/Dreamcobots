"""
Tests for bots/mining_bot/
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest
from bots.mining_bot.tiers import (
    Tier,
    MiningTierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_POOL_MINING,
    FEATURE_SOLO_MINING,
    FEATURE_MERGED_MINING,
    FEATURE_ADAPTIVE_STRATEGY,
    FEATURE_FRAUD_DETECTION,
    FEATURE_HONEYPOT_DETECTION,
    FEATURE_CONTRACT_VERIFICATION,
    FEATURE_MULTI_EXCHANGE,
    FEATURE_DEX_ROUTING,
    FEATURE_HARDWARE_WALLET,
    FEATURE_BACKTESTING,
    FEATURE_AI_OPTIMISATION,
    FEATURE_REINFORCEMENT_LEARNING,
    FEATURE_SMART_ALERTS,
)
from bots.mining_bot.strategy import (
    CoinProfile,
    StrategyType,
    StrategyEngine,
    AdaptiveStrategyEngine,
    MiningStrategyError,
    StrategyResult,
)
from bots.mining_bot.analytics import (
    MiningSession,
    ProfitabilityAnalytics,
    AnalyticsDepthError,
)
from bots.mining_bot.monitor import Alert, MiningMonitor, MonitoringDisabledError
from bots.mining_bot.fraud_detection import (
    FraudDetector,
    FraudCheckResult,
    FraudDetectionDisabledError,
)
from bots.mining_bot.exchange import (
    MultiExchangeRouter,
    ExchangeQuote,
    MultiExchangeDisabledError,
)
from bots.mining_bot.mining_bot import MiningBot, MiningBotTierError
from datetime import datetime, timezone


# ===========================================================================
# Helpers / fixtures
# ===========================================================================

def make_btc() -> CoinProfile:
    return CoinProfile(
        symbol="BTC",
        algorithm="SHA-256",
        network_difficulty=5e13,
        block_reward=3.125,
        coin_price_usd=65_000.0,
        network_hashrate=5e20,
        pool_fee_pct=1.0,
    )


def make_bch() -> CoinProfile:
    """BCH uses SHA-256 — compatible for merged mining with BTC."""
    return CoinProfile(
        symbol="BCH",
        algorithm="SHA-256",
        network_difficulty=1e12,
        block_reward=6.25,
        coin_price_usd=300.0,
        network_hashrate=2e19,
        pool_fee_pct=1.5,
    )


def make_ltc() -> CoinProfile:
    return CoinProfile(
        symbol="LTC",
        algorithm="Scrypt",
        network_difficulty=1e7,
        block_reward=6.25,
        coin_price_usd=90.0,
        network_hashrate=1e17,
        pool_fee_pct=1.0,
    )


def make_session(
    coin="BTC",
    strategy="pool_mining",
    revenue=10.0,
    cost=5.0,
    hashrate=100.0,
    energy=84.0,
) -> MiningSession:
    return MiningSession(
        coin=coin,
        strategy=strategy,
        duration_hours=24.0,
        hashrate_ths=hashrate,
        energy_kwh=energy,
        revenue_usd=revenue,
        electricity_cost_usd=cost,
    )


# ===========================================================================
# Tier tests
# ===========================================================================

class TestMiningTiers:
    def test_list_tiers_returns_three(self):
        assert len(list_tiers()) == 3

    def test_free_price_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 299.0

    def test_free_has_pool_mining(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_POOL_MINING)

    def test_free_lacks_solo_mining(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_SOLO_MINING)

    def test_pro_has_solo_and_merged(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_SOLO_MINING)
        assert cfg.has_feature(FEATURE_MERGED_MINING)

    def test_pro_has_fraud_detection(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_FRAUD_DETECTION)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in (
            FEATURE_AI_OPTIMISATION,
            FEATURE_REINFORCEMENT_LEARNING,
            FEATURE_DEX_ROUTING,
            FEATURE_HARDWARE_WALLET,
        ):
            assert cfg.has_feature(feat)

    def test_upgrade_free_to_pro(self):
        next_cfg = get_upgrade_path(Tier.FREE)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.PRO

    def test_upgrade_pro_to_enterprise(self):
        next_cfg = get_upgrade_path(Tier.PRO)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.ENTERPRISE

    def test_upgrade_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_free_monitored_coins(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.monitored_coins == 2

    def test_enterprise_unlimited_coins(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.monitored_coins == 0  # 0 = unlimited

    def test_all_tiers_have_analytics_depth(self):
        for cfg in list_tiers():
            assert cfg.analytics_depth in ("basic", "advanced", "full")


# ===========================================================================
# Strategy tests
# ===========================================================================

class TestStrategyEngine:
    def setup_method(self):
        self.engine = StrategyEngine(
            hashrate_ths=100.0,
            power_kw=3.5,
            electricity_rate=0.06,
            available_strategies=[StrategyType.POOL, StrategyType.SOLO, StrategyType.MERGED],
        )

    def test_invalid_hashrate_raises(self):
        with pytest.raises(ValueError):
            StrategyEngine(0, 3.5, 0.06, [StrategyType.POOL])

    def test_negative_power_raises(self):
        with pytest.raises(ValueError):
            StrategyEngine(100, -1, 0.06, [StrategyType.POOL])

    def test_evaluate_pool_returns_result(self):
        result = self.engine.evaluate_pool(make_btc())
        assert isinstance(result, StrategyResult)
        assert result.strategy == StrategyType.POOL
        assert result.coin == "BTC"

    def test_evaluate_solo_returns_result(self):
        result = self.engine.evaluate_solo(make_btc())
        assert result.strategy == StrategyType.SOLO

    def test_evaluate_merged_same_algo(self):
        result = self.engine.evaluate_merged(make_btc(), make_bch())
        assert result.strategy == StrategyType.MERGED
        assert "BTC" in result.coin
        assert "BCH" in result.coin

    def test_evaluate_merged_diff_algo_raises(self):
        with pytest.raises(MiningStrategyError):
            self.engine.evaluate_merged(make_btc(), make_ltc())

    def test_pool_not_available_raises(self):
        eng = StrategyEngine(100, 3.5, 0.06, [StrategyType.SOLO])
        with pytest.raises(MiningStrategyError):
            eng.evaluate_pool(make_btc())

    def test_compare_strategies_sorted_by_profit(self):
        results = self.engine.compare_strategies([make_btc(), make_bch()])
        profits = [r.net_profit_usd for r in results]
        assert profits == sorted(profits, reverse=True)

    def test_compare_strategies_returns_list(self):
        results = self.engine.compare_strategies([make_btc()])
        assert isinstance(results, list)
        assert len(results) > 0

    def test_pool_revenue_less_than_solo(self):
        pool = self.engine.evaluate_pool(make_btc())
        solo = self.engine.evaluate_solo(make_btc())
        # Solo has no pool fee, so revenue should be >= pool revenue
        assert solo.estimated_daily_revenue_usd >= pool.estimated_daily_revenue_usd

    def test_result_profitability_flag(self):
        result = self.engine.evaluate_pool(make_btc())
        # With these inputs the miner should be profitable
        assert isinstance(result.is_profitable, bool)

    def test_daily_energy_cost_calculation(self):
        cost = self.engine.daily_energy_cost()
        expected = 3.5 * 24 * 0.06
        assert abs(cost - expected) < 0.001


class TestAdaptiveStrategyEngine:
    def setup_method(self):
        self.engine = AdaptiveStrategyEngine(
            hashrate_ths=100.0,
            power_kw=3.5,
            electricity_rate=0.06,
            available_strategies=[StrategyType.POOL, StrategyType.SOLO, StrategyType.MERGED],
        )

    def test_best_strategy_returns_result(self):
        best = self.engine.best_strategy([make_btc()])
        assert best is not None
        assert isinstance(best, StrategyResult)

    def test_best_strategy_empty_coins_returns_none(self):
        best = self.engine.best_strategy([])
        assert best is None

    def test_recommend_returns_dict(self):
        rec = self.engine.recommend([make_btc()])
        assert "best" in rec
        assert "all_results" in rec
        assert "reasoning" in rec

    def test_recommend_reasoning_is_list(self):
        rec = self.engine.recommend([make_btc()])
        assert isinstance(rec["reasoning"], list)
        assert len(rec["reasoning"]) > 0

    def test_recommend_no_coins_reasoning(self):
        rec = self.engine.recommend([])
        assert any("No strategies" in r for r in rec["reasoning"])


# ===========================================================================
# Analytics tests
# ===========================================================================

class TestProfitabilityAnalytics:
    def test_basic_total_revenue(self):
        a = ProfitabilityAnalytics(depth="basic")
        a.record_session(make_session(revenue=10.0, cost=5.0))
        assert a.total_revenue_usd() == 10.0

    def test_basic_total_net_profit(self):
        a = ProfitabilityAnalytics(depth="basic")
        a.record_session(make_session(revenue=10.0, cost=5.0))
        assert a.total_net_profit_usd() == 5.0

    def test_basic_revenue_by_coin(self):
        a = ProfitabilityAnalytics(depth="basic")
        a.record_session(make_session(coin="BTC", revenue=10.0))
        a.record_session(make_session(coin="LTC", revenue=4.0))
        by_coin = a.revenue_by_coin()
        assert by_coin["BTC"] == 10.0
        assert by_coin["LTC"] == 4.0

    def test_basic_energy_requires_advanced(self):
        a = ProfitabilityAnalytics(depth="basic")
        with pytest.raises(AnalyticsDepthError):
            a.total_energy_kwh()

    def test_advanced_energy_kwh(self):
        a = ProfitabilityAnalytics(depth="advanced")
        a.record_session(make_session(energy=84.0))
        assert a.total_energy_kwh() == 84.0

    def test_advanced_average_hashrate(self):
        a = ProfitabilityAnalytics(depth="advanced")
        a.record_session(make_session(hashrate=100.0))
        a.record_session(make_session(hashrate=80.0))
        assert a.average_hashrate_ths() == 90.0

    def test_advanced_roi(self):
        a = ProfitabilityAnalytics(depth="advanced", hardware_cost_usd=0.0)
        a.record_session(make_session(revenue=10.0, cost=5.0))
        roi = a.roi_pct()
        assert roi == 100.0  # (10-5)/5 * 100

    def test_advanced_best_coin(self):
        a = ProfitabilityAnalytics(depth="advanced")
        a.record_session(make_session(coin="BTC", revenue=10.0))
        a.record_session(make_session(coin="LTC", revenue=3.0))
        assert a.best_performing_coin() == "BTC"

    def test_full_hashrate_trend(self):
        a = ProfitabilityAnalytics(depth="full")
        a.record_session(make_session(hashrate=100.0))
        a.record_session(make_session(hashrate=90.0))
        assert a.hashrate_trend() == [100.0, 90.0]

    def test_full_energy_efficiency(self):
        a = ProfitabilityAnalytics(depth="full")
        a.record_session(make_session(revenue=10.0, energy=100.0))
        assert a.energy_efficiency() == 0.1

    def test_full_profit_variance(self):
        a = ProfitabilityAnalytics(depth="full")
        a.record_session(make_session(revenue=10.0, cost=5.0))
        a.record_session(make_session(revenue=6.0, cost=3.0))
        v = a.profit_variance()
        assert v >= 0.0

    def test_summary_basic_keys(self):
        a = ProfitabilityAnalytics(depth="basic")
        summary = a.summary()
        for key in ("sessions", "total_revenue_usd", "total_net_profit_usd", "revenue_by_coin"):
            assert key in summary

    def test_summary_advanced_keys(self):
        a = ProfitabilityAnalytics(depth="advanced")
        summary = a.summary()
        assert "roi_pct" in summary
        assert "average_hashrate_ths" in summary

    def test_summary_full_keys(self):
        a = ProfitabilityAnalytics(depth="full")
        summary = a.summary()
        assert "hashrate_trend" in summary
        assert "energy_efficiency" in summary

    def test_session_count_increments(self):
        a = ProfitabilityAnalytics(depth="basic")
        assert a.session_count == 0
        a.record_session(make_session())
        assert a.session_count == 1

    def test_clear_resets_sessions(self):
        a = ProfitabilityAnalytics(depth="basic")
        a.record_session(make_session())
        a.clear()
        assert a.session_count == 0

    def test_invalid_depth_raises(self):
        with pytest.raises(ValueError):
            ProfitabilityAnalytics(depth="invalid")

    def test_session_roi_property(self):
        s = make_session(revenue=10.0, cost=5.0)
        assert s.roi_pct == 100.0

    def test_session_net_profit(self):
        s = make_session(revenue=10.0, cost=5.0)
        assert s.net_profit_usd == 5.0


# ===========================================================================
# Monitor tests
# ===========================================================================

class TestMiningMonitor:
    def test_alerts_disabled_raises(self):
        monitor = MiningMonitor(alerts_enabled=False)
        with pytest.raises(MonitoringDisabledError):
            monitor.record_hashrate(100.0, 3.5)

    def test_downtime_alert_on_zero_hashrate(self):
        monitor = MiningMonitor(alerts_enabled=True, expected_hashrate_ths=100.0)
        alerts = monitor.record_hashrate(0.0, 3.5)
        assert len(alerts) == 1
        assert alerts[0].category == "downtime"
        assert alerts[0].level == "critical"

    def test_no_alert_on_normal_hashrate(self):
        monitor = MiningMonitor(alerts_enabled=True, expected_hashrate_ths=100.0)
        alerts = monitor.record_hashrate(100.0, 3.5)
        assert len(alerts) == 0

    def test_sub_optimal_alert_on_low_hashrate(self):
        monitor = MiningMonitor(
            alerts_enabled=True,
            expected_hashrate_ths=100.0,
            hashrate_drop_pct=10.0,
        )
        alerts = monitor.record_hashrate(80.0, 3.5)  # 20% below expected
        categories = [a.category for a in alerts]
        assert "sub_optimal" in categories

    def test_unusual_activity_on_spike(self):
        monitor = MiningMonitor(
            alerts_enabled=True,
            expected_hashrate_ths=100.0,
            hashrate_spike_pct=20.0,
        )
        alerts = monitor.record_hashrate(130.0, 3.5)  # 30% above expected
        categories = [a.category for a in alerts]
        assert "unusual_activity" in categories

    def test_energy_alert_on_high_power(self):
        monitor = MiningMonitor(
            alerts_enabled=True,
            expected_hashrate_ths=100.0,
            max_power_kw=3.5,
        )
        alerts = monitor.record_hashrate(100.0, 10.0)  # 10 kW >> 3.5 kW
        categories = [a.category for a in alerts]
        assert "energy" in categories

    def test_check_downtime_no_reading(self):
        monitor = MiningMonitor(alerts_enabled=True)
        alert = monitor.check_downtime()
        assert alert is not None
        assert alert.category == "downtime"

    def test_all_alerts_accumulates(self):
        monitor = MiningMonitor(alerts_enabled=True, expected_hashrate_ths=100.0)
        monitor.record_hashrate(0.0, 3.5)
        monitor.record_hashrate(0.0, 3.5)
        assert len(monitor.all_alerts()) == 2

    def test_alerts_by_level(self):
        monitor = MiningMonitor(alerts_enabled=True, expected_hashrate_ths=100.0)
        monitor.record_hashrate(0.0, 3.5)
        criticals = monitor.alerts_by_level("critical")
        assert len(criticals) >= 1

    def test_alerts_by_category(self):
        monitor = MiningMonitor(alerts_enabled=True, expected_hashrate_ths=100.0)
        monitor.record_hashrate(0.0, 3.5)
        downtime = monitor.alerts_by_category("downtime")
        assert len(downtime) >= 1

    def test_clear_alerts(self):
        monitor = MiningMonitor(alerts_enabled=True, expected_hashrate_ths=100.0)
        monitor.record_hashrate(0.0, 3.5)
        monitor.clear_alerts()
        assert len(monitor.all_alerts()) == 0

    def test_alert_to_dict(self):
        alert = Alert(level="warning", category="test", message="hi")
        d = alert.to_dict()
        assert d["level"] == "warning"
        assert "timestamp" in d

    def test_handler_called_on_alert(self):
        received = []
        monitor = MiningMonitor(alerts_enabled=True, expected_hashrate_ths=100.0)
        monitor.register_handler(lambda a: received.append(a))
        monitor.record_hashrate(0.0, 3.5)
        assert len(received) == 1


# ===========================================================================
# Fraud Detection tests
# ===========================================================================

class TestFraudDetector:
    def test_disabled_raises_on_contract_check(self):
        fd = FraudDetector(enabled=False)
        with pytest.raises(FraudDetectionDisabledError):
            fd.check_contract("0xabc")

    def test_valid_contract_passes(self):
        fd = FraudDetector(enabled=True)
        result = fd.check_contract("0xabcdef1234567890abcdef1234567890abcd1234")
        assert result.passed
        assert result.risk_level == "none"

    def test_known_scam_contract_fails(self):
        fd = FraudDetector(enabled=True)
        result = fd.check_contract("0xdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef")
        assert not result.passed
        assert result.risk_level == "high"
        assert "known_scam_contract" in result.flags

    def test_invalid_address_format_fails(self):
        fd = FraudDetector(enabled=True)
        result = fd.check_contract("not_an_address")
        assert not result.passed
        assert "invalid_address_format" in result.flags

    def test_honeypot_pattern_detected(self):
        fd = FraudDetector(enabled=True)
        # Last 8 chars all the same
        result = fd.check_honeypot("0x" + "a" * 32 + "f" * 8)
        assert not result.passed
        assert "honeypot_address_pattern" in result.flags

    def test_clean_address_no_honeypot(self):
        fd = FraudDetector(enabled=True)
        result = fd.check_honeypot("0xabcdef1234567890abcdef1234567890abcd1234")
        assert result.passed

    def test_known_bad_pool_fails(self):
        fd = FraudDetector(enabled=True)
        result = fd.check_pool("https://fakeminingpool.com/stratum")
        assert not result.passed
        assert result.risk_level == "high"

    def test_clean_pool_passes(self):
        fd = FraudDetector(enabled=True)
        result = fd.check_pool("stratum+tcp://pool.example.com:3333")
        assert result.passed

    def test_run_all_checks_returns_list(self):
        fd = FraudDetector(enabled=True)
        results = fd.run_all_checks(
            contract_address="0xabcdef1234567890abcdef1234567890abcd5678",
            pool_url="stratum+tcp://pool.example.com:3333",
        )
        assert isinstance(results, list)
        assert len(results) == 3  # contract, honeypot, pool

    def test_custom_bad_domain(self):
        fd = FraudDetector(enabled=True, custom_bad_domains=["evilpool.xyz"])
        result = fd.check_pool("http://evilpool.xyz/")
        assert not result.passed

    def test_result_to_dict(self):
        fd = FraudDetector(enabled=True)
        result = fd.check_contract("0xabcdef1234567890abcdef1234567890abcd9876")
        d = result.to_dict()
        assert "passed" in d
        assert "risk_level" in d


# ===========================================================================
# Exchange tests
# ===========================================================================

class TestMultiExchangeRouter:
    def test_disabled_raises(self):
        router = MultiExchangeRouter(multi_exchange_enabled=False)
        with pytest.raises(MultiExchangeDisabledError):
            router.get_quotes("BTC", 1.0)

    def test_quotes_returned(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        quotes = router.get_quotes("BTC", 1.0)
        assert len(quotes) > 0
        assert all(isinstance(q, ExchangeQuote) for q in quotes)

    def test_dex_excluded_without_dex_routing(self):
        router = MultiExchangeRouter(
            multi_exchange_enabled=True, dex_routing_enabled=False
        )
        quotes = router.get_quotes("BTC", 1.0)
        assert all(not q.is_dex for q in quotes)

    def test_dex_included_with_dex_routing(self):
        router = MultiExchangeRouter(
            multi_exchange_enabled=True, dex_routing_enabled=True
        )
        quotes = router.get_quotes("BTC", 1.0)
        assert any(q.is_dex for q in quotes)

    def test_best_exchange_returns_highest_net(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        best = router.best_exchange("BTC", 1.0)
        all_quotes = router.get_quotes("BTC", 1.0)
        assert best.net_usd == max(q.net_usd for q in all_quotes)

    def test_compare_exchanges_has_required_keys(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        report = router.compare_exchanges("ETH", 1.0)
        for key in ("coin", "amount", "quotes", "best_exchange", "best_net_usd"):
            assert key in report

    def test_unknown_coin_returns_empty(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        quotes = router.get_quotes("UNKNOWN_COIN", 1.0)
        assert quotes == []

    def test_best_exchange_unknown_coin_none(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        assert router.best_exchange("UNKNOWN_COIN", 1.0) is None

    def test_net_usd_less_than_gross(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        quotes = router.get_quotes("BTC", 1.0)
        for q in quotes:
            assert q.net_usd < q.gross_usd

    def test_available_coins(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        coins = router.available_coins()
        assert "BTC" in coins
        assert "ETH" in coins

    def test_quote_to_dict(self):
        router = MultiExchangeRouter(multi_exchange_enabled=True)
        quote = router.get_quotes("BTC", 1.0)[0]
        d = quote.to_dict()
        assert "exchange" in d
        assert "net_usd" in d


# ===========================================================================
# MiningBot (integration) tests
# ===========================================================================

class TestMiningBotFree:
    def setup_method(self):
        self.bot = MiningBot(tier=Tier.FREE, hashrate_ths=50.0, power_kw=2.0, electricity_rate=0.05)

    def test_describe_tier_returns_string(self):
        result = self.bot.describe_tier()
        assert isinstance(result, str)
        assert "Free" in result

    def test_compare_tiers_returns_string(self):
        result = MiningBot.compare_tiers()
        assert isinstance(result, str)
        assert "Free" in result
        assert "Enterprise" in result

    def test_show_upgrade_path_free(self):
        result = self.bot.show_upgrade_path()
        assert "Pro" in result

    def test_free_compare_strategies_pool_only(self):
        results = self.bot.compare_strategies([make_btc()])
        strategies = [r.strategy for r in results]
        assert StrategyType.POOL in strategies
        assert StrategyType.SOLO not in strategies

    def test_free_recommend_strategy_raises(self):
        with pytest.raises(MiningBotTierError):
            self.bot.recommend_strategy([make_btc()])

    def test_free_record_session(self):
        self.bot.record_session(make_session())
        summary = self.bot.analytics_summary()
        assert summary["sessions"] == 1

    def test_free_check_contract_raises(self):
        with pytest.raises(FraudDetectionDisabledError):
            self.bot.check_contract("0x" + "a" * 40)

    def test_free_best_exchange_raises(self):
        with pytest.raises(MultiExchangeDisabledError):
            self.bot.best_exchange("BTC", 1.0)

    def test_free_record_hashrate_raises(self):
        with pytest.raises(MonitoringDisabledError):
            self.bot.record_hashrate(50.0, 2.0)

    def test_free_backtest_raises(self):
        with pytest.raises(MiningBotTierError):
            self.bot.backtest([make_session()])

    def test_free_ai_optimise_raises(self):
        with pytest.raises(MiningBotTierError):
            self.bot.ai_optimise([make_btc()])


class TestMiningBotPro:
    def setup_method(self):
        self.bot = MiningBot(
            tier=Tier.PRO,
            hashrate_ths=100.0,
            power_kw=3.5,
            electricity_rate=0.06,
        )

    def test_pro_recommend_strategy(self):
        rec = self.bot.recommend_strategy([make_btc()])
        assert "best" in rec
        assert "reasoning" in rec

    def test_pro_compare_strategies_all_types(self):
        results = self.bot.compare_strategies([make_btc(), make_bch()])
        strategy_types = {r.strategy for r in results}
        assert StrategyType.POOL in strategy_types
        assert StrategyType.SOLO in strategy_types
        assert StrategyType.MERGED in strategy_types

    def test_pro_fraud_check_contract(self):
        result = self.bot.check_contract("0xabcdef1234567890abcdef1234567890abcd1234")
        assert result.passed

    def test_pro_fraud_check_pool(self):
        result = self.bot.check_pool("stratum+tcp://legit.pool.com:3333")
        assert result.passed

    def test_pro_run_fraud_checks(self):
        results = self.bot.run_fraud_checks(
            contract_address="0xabcdef1234567890abcdef1234567890abcd5678",
            pool_url="http://pool.example.com",
        )
        assert len(results) == 3

    def test_pro_compare_exchanges(self):
        report = self.bot.compare_exchanges("BTC", 0.1)
        assert report["best_exchange"] is not None

    def test_pro_record_hashrate_alert(self):
        alerts = self.bot.record_hashrate(0.0, 3.5)
        assert len(alerts) > 0
        assert alerts[0].category == "downtime"

    def test_pro_backtest(self):
        sessions = [make_session(revenue=10.0, cost=5.0) for _ in range(5)]
        result = self.bot.backtest(sessions)
        assert result["sessions"] == 5

    def test_pro_analytics_summary_advanced(self):
        self.bot.record_session(make_session(revenue=10.0, cost=5.0, energy=84.0))
        summary = self.bot.analytics_summary()
        assert "roi_pct" in summary
        assert "total_energy_kwh" in summary

    def test_pro_all_alerts(self):
        self.bot.record_hashrate(0.0, 3.5)
        assert len(self.bot.all_alerts()) > 0

    def test_pro_ai_optimise_raises(self):
        with pytest.raises(MiningBotTierError):
            self.bot.ai_optimise([make_btc()])

    def test_pro_show_upgrade_path(self):
        result = self.bot.show_upgrade_path()
        assert "Enterprise" in result


class TestMiningBotEnterprise:
    def setup_method(self):
        self.bot = MiningBot(
            tier=Tier.ENTERPRISE,
            hashrate_ths=200.0,
            power_kw=7.0,
            electricity_rate=0.05,
            hardware_cost_usd=10_000.0,
        )

    def test_enterprise_ai_optimise(self):
        result = self.bot.ai_optimise([make_btc(), make_bch()])
        assert "recommendation" in result
        assert "scored_results" in result
        assert "reasoning" in result

    def test_enterprise_ai_optimise_recommendation_is_result_or_none(self):
        result = self.bot.ai_optimise([make_btc()])
        assert result["recommendation"] is None or isinstance(
            result["recommendation"], StrategyResult
        )

    def test_enterprise_reinforcement_learning(self):
        sessions = [
            make_session(strategy="pool_mining", revenue=10.0, cost=5.0),
            make_session(strategy="solo_mining", revenue=20.0, cost=8.0),
            make_session(strategy="pool_mining", revenue=12.0, cost=5.0),
        ]
        result = self.bot.reinforcement_learning_tune(sessions)
        assert "policy_weights" in result
        assert "improvement_pct" in result
        assert result["episodes"] == 3

    def test_enterprise_rl_empty_sessions(self):
        result = self.bot.reinforcement_learning_tune([])
        assert result["episodes"] == 0

    def test_enterprise_rl_weights_sum_to_one(self):
        sessions = [
            make_session(strategy="pool_mining", revenue=10.0, cost=4.0),
            make_session(strategy="solo_mining", revenue=12.0, cost=5.0),
        ]
        result = self.bot.reinforcement_learning_tune(sessions)
        weights = result["policy_weights"]
        if weights:
            total = sum(weights.values())
            assert abs(total - 1.0) < 1e-5

    def test_enterprise_dex_routing(self):
        report = self.bot.compare_exchanges("ETH", 1.0)
        quotes = report["quotes"]
        dex_quotes = [q for q in quotes if q.get("is_dex")]
        assert len(dex_quotes) > 0

    def test_enterprise_full_analytics(self):
        self.bot.record_session(make_session(revenue=10.0, cost=5.0, energy=84.0))
        summary = self.bot.analytics_summary()
        assert "hashrate_trend" in summary
        assert "energy_efficiency" in summary
        assert "profit_variance" in summary

    def test_enterprise_show_upgrade_is_top(self):
        result = self.bot.show_upgrade_path()
        assert "top-tier" in result

    def test_enterprise_honeypot_check(self):
        result = self.bot.check_honeypot("0xabcdef1234567890abcdef1234567890abcdef12")
        assert isinstance(result, FraudCheckResult)

    def test_enterprise_check_downtime_no_reading(self):
        alert = self.bot.check_downtime()
        assert alert is not None
        assert alert.category == "downtime"
