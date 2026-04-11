"""
Tests for bots/quantum_decision_bot/quantum_decision_bot.py

Covers:
  1.  Tiers & feature flags
  2.  SimulationEngine
  3.  ProbabilityModel
  4.  DimensionMapper
  5.  QuantumEngine (decide / scenario generation)
  6.  BotRouter (entangled network)
  7.  MoneyAutomationEngine
  8.  ContentViralEngine
  9.  SelfImprovingAI
  10. QuantumDecisionBot (FREE tier)
  11. QuantumDecisionBot (PRO tier)
  12. QuantumDecisionBot (ENTERPRISE tier)
  13. Tier restrictions
  14. process() command interface
  15. Bot library registration
"""

from __future__ import annotations

import os
import sys

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.quantum_decision_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    get_bot_tier_info,
    FEATURE_QUANTUM_ENGINE,
    FEATURE_SIMULATION_ENGINE,
    FEATURE_PROBABILITY_MODEL,
    FEATURE_DIMENSION_MAPPER,
    FEATURE_BOT_ROUTER,
    FEATURE_MONEY_AUTOMATION,
    FEATURE_CONTENT_VIRAL_ENGINE,
    FEATURE_SELF_IMPROVING_AI,
    FEATURE_HYPER_SIMULATION,
    FEATURE_GLOBAL_ORCHESTRATION,
    FEATURE_WHITE_LABEL,
    FEATURE_STRIPE_BILLING,
    FEATURE_REFERRAL_SYSTEM,
)
from bots.quantum_decision_bot.quantum_decision_bot import (
    QuantumDecisionBot,
    QuantumDecisionBotError,
    QuantumDecisionBotTierError,
    RiskLevel,
    TimeHorizon,
    ScaleGoal,
    OutcomeLabel,
    BotDecisionStatus,
    OpportunityType,
    ContentFormat,
    Scenario,
    SimulationResult,
    ScoredPath,
    QuantumDecision,
    BotRouterEvent,
    Opportunity,
    ContentScript,
    LearningRecord,
    SimulationEngine,
    ProbabilityModel,
    DimensionMapper,
    QuantumEngine,
    BotRouter,
    MoneyAutomationEngine,
    ContentViralEngine,
    SelfImprovingAI,
)


# ===========================================================================
# Helpers
# ===========================================================================


def _make_bot(tier: Tier = Tier.FREE) -> QuantumDecisionBot:
    return QuantumDecisionBot(tier=tier)


def _simple_context(summary: str = "Test decision") -> dict:
    return {"summary": summary}


def _custom_context(summary: str = "Custom") -> dict:
    return {
        "summary": summary,
        "scenarios": [
            {"name": "plan_a", "base_profit": 10000.0, "risk_score": 3.0},
            {"name": "plan_b", "base_profit": 25000.0, "risk_score": 7.0},
        ],
        "budget": 15000,
        "risk_level": "moderate",
        "time_horizon": "medium",
        "scale_goal": "regional",
    }


# ===========================================================================
# 1. Tiers & feature flags
# ===========================================================================


class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_free_tier_price_is_zero(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.price_usd_monthly == 0.0

    def test_pro_tier_price(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.price_usd_monthly == 49.0

    def test_enterprise_tier_price(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.price_usd_monthly == 199.0

    def test_free_has_core_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_QUANTUM_ENGINE)
        assert cfg.has_feature(FEATURE_SIMULATION_ENGINE)
        assert cfg.has_feature(FEATURE_PROBABILITY_MODEL)

    def test_free_does_not_have_pro_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_BOT_ROUTER)
        assert not cfg.has_feature(FEATURE_MONEY_AUTOMATION)
        assert not cfg.has_feature(FEATURE_SELF_IMPROVING_AI)

    def test_pro_has_dimension_mapper_and_router(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_DIMENSION_MAPPER)
        assert cfg.has_feature(FEATURE_BOT_ROUTER)
        assert cfg.has_feature(FEATURE_MONEY_AUTOMATION)
        assert cfg.has_feature(FEATURE_CONTENT_VIRAL_ENGINE)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feat in [
            FEATURE_SELF_IMPROVING_AI,
            FEATURE_HYPER_SIMULATION,
            FEATURE_GLOBAL_ORCHESTRATION,
            FEATURE_WHITE_LABEL,
        ]:
            assert cfg.has_feature(feat)

    def test_free_scenario_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_scenarios == 3

    def test_pro_scenario_limit_is_unlimited(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.max_scenarios is None

    def test_free_simulation_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_simulations == 100

    def test_enterprise_simulation_limit(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.max_simulations == 100_000

    def test_upgrade_path_free_to_pro(self):
        upgrade = get_upgrade_path(Tier.FREE)
        assert upgrade is not None
        assert upgrade.tier == Tier.PRO

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_get_bot_tier_info_returns_dict(self):
        info = get_bot_tier_info()
        assert "free" in info
        assert "pro" in info
        assert "enterprise" in info


# ===========================================================================
# 2. SimulationEngine
# ===========================================================================


class TestSimulationEngine:
    def _make_scenario(self) -> Scenario:
        import uuid
        return Scenario(
            scenario_id=str(uuid.uuid4()),
            name="test_scenario",
            description="Test",
            base_profit=10000.0,
            risk_score=5.0,
            time_horizon=TimeHorizon.MEDIUM,
            capital_required=8000.0,
            scale_goal=ScaleGoal.LOCAL,
        )

    def test_run_returns_simulation_result(self):
        engine = SimulationEngine()
        scenario = self._make_scenario()
        result = engine.run(scenario, runs=50)
        assert isinstance(result, SimulationResult)

    def test_run_count_matches(self):
        engine = SimulationEngine()
        scenario = self._make_scenario()
        result = engine.run(scenario, runs=200)
        assert result.runs == 200

    def test_avg_profit_is_numeric(self):
        engine = SimulationEngine()
        result = engine.run(self._make_scenario(), runs=100)
        assert isinstance(result.avg_profit, float)

    def test_probability_positive_between_0_and_1(self):
        engine = SimulationEngine()
        result = engine.run(self._make_scenario(), runs=100)
        assert 0.0 <= result.probability_positive <= 1.0

    def test_best_case_gte_worst_case(self):
        engine = SimulationEngine()
        result = engine.run(self._make_scenario(), runs=500)
        assert result.best_case_profit >= result.worst_case_profit

    def test_max_profit_gte_min_profit(self):
        engine = SimulationEngine()
        result = engine.run(self._make_scenario(), runs=100)
        assert result.max_profit >= result.min_profit

    def test_raw_samples_length(self):
        engine = SimulationEngine()
        result = engine.run(self._make_scenario(), runs=50)
        assert len(result.raw_samples) == 50

    def test_positive_base_profit_yields_positive_avg(self):
        engine = SimulationEngine()
        import uuid
        scenario = Scenario(
            scenario_id=str(uuid.uuid4()),
            name="high_profit",
            description="",
            base_profit=1_000_000.0,
            risk_score=1.0,
            time_horizon=TimeHorizon.SHORT,
            capital_required=0.0,
            scale_goal=ScaleGoal.GLOBAL,
        )
        result = engine.run(scenario, runs=200)
        assert result.avg_profit > 0


# ===========================================================================
# 3. ProbabilityModel
# ===========================================================================


class TestProbabilityModel:
    def _make_result(self, avg_profit=10000.0, avg_risk=3.0, prob=0.8) -> SimulationResult:
        import uuid
        scenario = Scenario(
            scenario_id=str(uuid.uuid4()),
            name="mock",
            description="",
            base_profit=avg_profit,
            risk_score=avg_risk,
            time_horizon=TimeHorizon.MEDIUM,
            capital_required=0.0,
            scale_goal=ScaleGoal.LOCAL,
        )
        return SimulationResult(
            scenario=scenario,
            runs=100,
            avg_profit=avg_profit,
            min_profit=0.0,
            max_profit=avg_profit * 1.5,
            avg_risk=avg_risk,
            probability_positive=prob,
            best_case_profit=avg_profit * 1.3,
            worst_case_profit=avg_profit * 0.5,
        )

    def test_score_returns_float(self):
        model = ProbabilityModel()
        result = self._make_result()
        assert isinstance(model.score(result), float)

    def test_higher_profit_yields_higher_score(self):
        model = ProbabilityModel()
        low = self._make_result(avg_profit=1000.0)
        high = self._make_result(avg_profit=50000.0)
        assert model.score(high) > model.score(low)

    def test_higher_risk_yields_lower_score(self):
        model = ProbabilityModel(risk_weight=1.0)
        low_risk = self._make_result(avg_risk=1.0)
        high_risk = self._make_result(avg_risk=9.0)
        assert model.score(low_risk) > model.score(high_risk)

    def test_apply_adjustment_changes_score(self):
        model = ProbabilityModel()
        result = self._make_result()
        before = model.score(result)
        model.apply_adjustment("mock", 500.0)
        after = model.score(result)
        assert after > before

    def test_get_adjustment_default_zero(self):
        model = ProbabilityModel()
        assert model.get_adjustment("unknown") == 0.0

    def test_negative_adjustment_lowers_score(self):
        model = ProbabilityModel()
        result = self._make_result()
        before = model.score(result)
        model.apply_adjustment("mock", -100.0)
        after = model.score(result)
        assert after < before


# ===========================================================================
# 4. DimensionMapper
# ===========================================================================


class TestDimensionMapper:
    def test_map_returns_dict(self):
        mapper = DimensionMapper()
        result = mapper.map(TimeHorizon.MEDIUM, 10000.0, RiskLevel.MODERATE, ScaleGoal.LOCAL)
        assert isinstance(result, dict)

    def test_map_contains_expected_keys(self):
        mapper = DimensionMapper()
        result = mapper.map(TimeHorizon.LONG, 20000.0, RiskLevel.SAFE, ScaleGoal.GLOBAL)
        for key in ["time_horizon", "budget", "risk_level", "scale_goal",
                    "composite_multiplier", "recommended_max_capital"]:
            assert key in result

    def test_global_scale_increases_recommended_capital(self):
        mapper = DimensionMapper()
        local = mapper.map(TimeHorizon.MEDIUM, 10000.0, RiskLevel.MODERATE, ScaleGoal.LOCAL)
        global_ = mapper.map(TimeHorizon.MEDIUM, 10000.0, RiskLevel.MODERATE, ScaleGoal.GLOBAL)
        assert global_["recommended_max_capital"] > local["recommended_max_capital"]

    def test_long_horizon_multiplier_higher_than_short(self):
        mapper = DimensionMapper()
        short = mapper.map(TimeHorizon.SHORT, 10000.0, RiskLevel.MODERATE, ScaleGoal.LOCAL)
        long_ = mapper.map(TimeHorizon.LONG, 10000.0, RiskLevel.MODERATE, ScaleGoal.LOCAL)
        assert long_["time_multiplier"] > short["time_multiplier"]

    def test_risk_range_values(self):
        mapper = DimensionMapper()
        safe = mapper.map(TimeHorizon.SHORT, 5000.0, RiskLevel.SAFE, ScaleGoal.LOCAL)
        aggressive = mapper.map(TimeHorizon.SHORT, 5000.0, RiskLevel.AGGRESSIVE, ScaleGoal.LOCAL)
        assert safe["risk_range"][1] < aggressive["risk_range"][0]

    def test_budget_reflected_in_output(self):
        mapper = DimensionMapper()
        result = mapper.map(TimeHorizon.MEDIUM, 50000.0, RiskLevel.MODERATE, ScaleGoal.LOCAL)
        assert result["budget"] == 50000.0


# ===========================================================================
# 5. QuantumEngine
# ===========================================================================


class TestQuantumEngine:
    def _make_engine(self) -> QuantumEngine:
        sim = SimulationEngine()
        prob = ProbabilityModel()
        dim = DimensionMapper()
        return QuantumEngine(sim, prob, dim)

    def test_decide_returns_quantum_decision(self):
        engine = self._make_engine()
        result = engine.decide({}, runs=50)
        assert isinstance(result, QuantumDecision)

    def test_best_path_has_highest_score(self):
        engine = self._make_engine()
        result = engine.decide({}, runs=50)
        all_scores = [result.best_path.score] + [a.score for a in result.alternatives]
        assert result.best_path.score == max(all_scores)

    def test_three_default_scenarios(self):
        engine = self._make_engine()
        result = engine.decide({}, runs=50)
        total = 1 + len(result.alternatives)
        assert total == 3

    def test_custom_scenarios_are_used(self):
        engine = self._make_engine()
        ctx = {
            "scenarios": [
                {"name": "alpha", "base_profit": 5000.0, "risk_score": 2.0},
                {"name": "beta", "base_profit": 20000.0, "risk_score": 6.0},
            ]
        }
        result = engine.decide(ctx, runs=50)
        names = {result.best_path.scenario.name} | {a.scenario.name for a in result.alternatives}
        assert "alpha" in names or "beta" in names

    def test_decision_has_timestamp(self):
        engine = self._make_engine()
        result = engine.decide({}, runs=20)
        assert result.timestamp

    def test_decision_has_id(self):
        engine = self._make_engine()
        result = engine.decide({}, runs=20)
        assert result.decision_id

    def test_dimensions_populated_when_mapper_provided(self):
        engine = self._make_engine()
        ctx = {"budget": 10000, "risk_level": "moderate"}
        result = engine.decide(ctx, runs=50)
        assert isinstance(result.dimensions, dict)
        assert len(result.dimensions) > 0

    def test_risk_warning_has_lowest_or_equal_score(self):
        engine = self._make_engine()
        result = engine.decide({}, runs=50)
        all_scores = [result.best_path.score] + [a.score for a in result.alternatives]
        assert result.risk_warning.score <= max(all_scores)

    def test_string_enum_values_in_context_accepted(self):
        engine = self._make_engine()
        ctx = {"time_horizon": "short", "scale_goal": "global"}
        result = engine.decide(ctx, runs=30)
        assert isinstance(result, QuantumDecision)


# ===========================================================================
# 6. BotRouter
# ===========================================================================


class TestBotRouter:
    def _make_decision(self) -> QuantumDecision:
        engine = QuantumEngine(SimulationEngine(), ProbabilityModel(), DimensionMapper())
        return engine.decide({}, runs=30)

    def test_route_returns_event(self):
        router = BotRouter()
        decision = self._make_decision()
        event = router.route(decision)
        assert isinstance(event, BotRouterEvent)

    def test_event_status_is_routed(self):
        router = BotRouter()
        event = router.route(self._make_decision())
        assert event.status == BotDecisionStatus.ROUTED

    def test_event_targets_default_network(self):
        router = BotRouter()
        event = router.route(self._make_decision())
        assert len(event.target_bots) > 0

    def test_actions_dict_populated(self):
        router = BotRouter()
        event = router.route(self._make_decision())
        assert isinstance(event.actions, dict)
        assert len(event.actions) > 0

    def test_event_log_grows(self):
        router = BotRouter()
        router.route(self._make_decision())
        router.route(self._make_decision())
        assert len(router.get_event_log()) == 2

    def test_add_bot_to_network(self):
        router = BotRouter()
        router.add_bot("new_custom_bot")
        assert "new_custom_bot" in router.network

    def test_remove_bot_from_network(self):
        router = BotRouter()
        router.add_bot("temp_bot")
        router.remove_bot("temp_bot")
        assert "temp_bot" not in router.network

    def test_custom_network(self):
        router = BotRouter(network=["bot_a", "bot_b"])
        assert router.network == ["bot_a", "bot_b"]

    def test_each_bot_gets_an_action(self):
        network = ["real_estate_bot", "crypto_bot", "deal_bot"]
        router = BotRouter(network=network)
        event = router.route(self._make_decision())
        for bot in network:
            assert bot in event.actions


# ===========================================================================
# 7. MoneyAutomationEngine
# ===========================================================================


class TestMoneyAutomationEngine:
    def test_scan_returns_list(self):
        engine = MoneyAutomationEngine(SimulationEngine(), ProbabilityModel())
        results = engine.scan(runs=50)
        assert isinstance(results, list)

    def test_scan_returns_all_opportunity_templates(self):
        engine = MoneyAutomationEngine(SimulationEngine(), ProbabilityModel())
        results = engine.scan(runs=50)
        assert len(results) == len(MoneyAutomationEngine.OPPORTUNITY_TEMPLATES)

    def test_opportunities_are_sorted_by_score(self):
        engine = MoneyAutomationEngine(SimulationEngine(), ProbabilityModel())
        results = engine.scan(runs=50)
        scores = [o.quantum_score for o in results]
        assert scores == sorted(scores, reverse=True)

    def test_opportunity_has_action(self):
        engine = MoneyAutomationEngine(SimulationEngine(), ProbabilityModel())
        results = engine.scan(runs=50)
        for opp in results:
            assert opp.recommended_action

    def test_opportunity_confidence_between_0_and_1(self):
        engine = MoneyAutomationEngine(SimulationEngine(), ProbabilityModel())
        results = engine.scan(runs=100)
        for opp in results:
            assert 0.0 <= opp.confidence <= 1.0

    def test_get_top_opportunities(self):
        engine = MoneyAutomationEngine(SimulationEngine(), ProbabilityModel())
        engine.scan(runs=50)
        top = engine.get_top_opportunities(n=2)
        assert len(top) == 2

    def test_all_opportunity_types_covered(self):
        engine = MoneyAutomationEngine(SimulationEngine(), ProbabilityModel())
        results = engine.scan(runs=50)
        types = {o.opp_type for o in results}
        assert len(types) > 3


# ===========================================================================
# 8. ContentViralEngine
# ===========================================================================


class TestContentViralEngine:
    def _make_decision(self) -> QuantumDecision:
        engine = QuantumEngine(SimulationEngine(), ProbabilityModel(), DimensionMapper())
        return engine.decide({}, runs=50)

    def test_generate_returns_content_script(self):
        viral = ContentViralEngine()
        decision = self._make_decision()
        script = viral.generate(decision, fmt=ContentFormat.TIKTOK)
        assert isinstance(script, ContentScript)

    def test_tiktok_hook_not_empty(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.TIKTOK)
        assert script.hook

    def test_youtube_hook_not_empty(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.YOUTUBE)
        assert script.hook

    def test_instagram_format(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.INSTAGRAM)
        assert script.format == ContentFormat.INSTAGRAM

    def test_blog_format(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.BLOG)
        assert script.format == ContentFormat.BLOG

    def test_script_body_contains_profit(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.TIKTOK)
        assert "$" in script.body

    def test_cta_not_empty(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.TIKTOK)
        assert script.cta

    def test_title_not_empty(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.TIKTOK)
        assert script.title

    def test_script_id_is_uuid(self):
        viral = ContentViralEngine()
        script = viral.generate(self._make_decision(), fmt=ContentFormat.TIKTOK)
        assert len(script.script_id) == 36  # UUID4 format


# ===========================================================================
# 9. SelfImprovingAI
# ===========================================================================


class TestSelfImprovingAI:
    def _make_decision(self) -> QuantumDecision:
        engine = QuantumEngine(SimulationEngine(), ProbabilityModel(), DimensionMapper())
        return engine.decide({}, runs=50)

    def test_record_outcome_returns_learning_record(self):
        model = ProbabilityModel()
        ai = SelfImprovingAI(model)
        decision = self._make_decision()
        record = ai.record_outcome(decision, actual_profit=15000.0)
        assert isinstance(record, LearningRecord)

    def test_records_accumulate(self):
        model = ProbabilityModel()
        ai = SelfImprovingAI(model)
        decision = self._make_decision()
        ai.record_outcome(decision, 10000.0)
        ai.record_outcome(decision, 5000.0)
        assert len(ai.get_records()) == 2

    def test_accuracy_zero_with_no_records(self):
        ai = SelfImprovingAI(ProbabilityModel())
        assert ai.accuracy() == 0.0

    def test_accuracy_between_0_and_1(self):
        model = ProbabilityModel()
        ai = SelfImprovingAI(model)
        decision = self._make_decision()
        for profit in [1000, 5000, 50000, 100000]:
            ai.record_outcome(decision, float(profit))
        assert 0.0 <= ai.accuracy() <= 1.0

    def test_correct_outcome_reinforces_model(self):
        model = ProbabilityModel()
        ai = SelfImprovingAI(model)
        decision = self._make_decision()
        scenario_name = decision.best_path.scenario.name
        before = model.get_adjustment(scenario_name)
        # Record a very profitable outcome to guarantee reinforcement
        ai.record_outcome(decision, actual_profit=decision.best_path.simulation.avg_profit * 2)
        after = model.get_adjustment(scenario_name)
        assert after > before

    def test_summary_has_accuracy(self):
        model = ProbabilityModel()
        ai = SelfImprovingAI(model)
        summary = ai.summary()
        assert "accuracy" in summary

    def test_summary_total_records(self):
        model = ProbabilityModel()
        ai = SelfImprovingAI(model)
        decision = self._make_decision()
        ai.record_outcome(decision, 10000.0)
        assert ai.summary()["total_records"] == 1


# ===========================================================================
# 10. QuantumDecisionBot — FREE tier
# ===========================================================================


class TestQuantumDecisionBotFree:
    def test_instantiation(self):
        bot = _make_bot(Tier.FREE)
        assert bot.tier == Tier.FREE

    def test_decide_returns_quantum_decision(self):
        bot = _make_bot(Tier.FREE)
        result = bot.decide(_simple_context())
        assert isinstance(result, QuantumDecision)

    def test_decision_log_grows(self):
        bot = _make_bot(Tier.FREE)
        bot.decide(_simple_context())
        bot.decide(_simple_context())
        assert len(bot.get_decision_log()) == 2

    def test_best_path_score_is_highest(self):
        bot = _make_bot(Tier.FREE)
        result = bot.decide(_simple_context())
        all_scores = [result.best_path.score] + [a.score for a in result.alternatives]
        assert result.best_path.score == max(all_scores)

    def test_free_tier_caps_scenarios(self):
        bot = _make_bot(Tier.FREE)
        ctx = {
            "scenarios": [
                {"name": f"s{i}", "base_profit": float(i * 1000), "risk_score": float(i)}
                for i in range(1, 7)
            ]
        }
        result = bot.decide(ctx)
        total = 1 + len(result.alternatives)
        assert total <= 3

    def test_get_tier_info(self):
        bot = _make_bot(Tier.FREE)
        info = bot.get_tier_info()
        assert info["tier"] == "Free"
        assert info["price_usd_monthly"] == 0.0
        assert info["upgrade"] is not None

    def test_process_decide_command(self):
        bot = _make_bot(Tier.FREE)
        result = bot.process("decide", _simple_context())
        assert result["command"] == "decide"
        assert "best_path" in result
        assert "avg_profit" in result

    def test_process_status_command(self):
        bot = _make_bot(Tier.FREE)
        result = bot.process("status")
        assert result["command"] == "status"
        assert result["bot"] == "QuantumDecisionBot"

    def test_process_unknown_command(self):
        bot = _make_bot(Tier.FREE)
        result = bot.process("invalid_cmd")
        assert "error" in result

    def test_free_simulation_runs_capped(self):
        bot = _make_bot(Tier.FREE)
        result = bot.decide(_simple_context())
        assert result.best_path.simulation.runs == 100


# ===========================================================================
# 11. QuantumDecisionBot — PRO tier
# ===========================================================================


class TestQuantumDecisionBotPro:
    def test_instantiation(self):
        bot = _make_bot(Tier.PRO)
        assert bot.tier == Tier.PRO

    def test_decide_works(self):
        bot = _make_bot(Tier.PRO)
        result = bot.decide(_custom_context())
        assert isinstance(result, QuantumDecision)

    def test_broadcast_decision_returns_event(self):
        bot = _make_bot(Tier.PRO)
        decision = bot.decide(_simple_context())
        event = bot.broadcast_decision(decision)
        assert isinstance(event, BotRouterEvent)
        assert event.status == BotDecisionStatus.ROUTED

    def test_router_event_log(self):
        bot = _make_bot(Tier.PRO)
        decision = bot.decide(_simple_context())
        bot.broadcast_decision(decision)
        log = bot.get_router_event_log()
        assert len(log) == 1

    def test_get_bot_network(self):
        bot = _make_bot(Tier.PRO)
        network = bot.get_bot_network()
        assert isinstance(network, list)
        assert len(network) > 0

    def test_add_bot_to_network(self):
        bot = _make_bot(Tier.PRO)
        bot.add_bot_to_network("trade_titan_bot")
        assert "trade_titan_bot" in bot.get_bot_network()

    def test_remove_bot_from_network(self):
        bot = _make_bot(Tier.PRO)
        bot.add_bot_to_network("temp_bot")
        bot.remove_bot_from_network("temp_bot")
        assert "temp_bot" not in bot.get_bot_network()

    def test_scan_opportunities(self):
        bot = _make_bot(Tier.PRO)
        opps = bot.scan_opportunities(runs=50)
        assert isinstance(opps, list)
        assert len(opps) > 0

    def test_top_opportunities(self):
        bot = _make_bot(Tier.PRO)
        bot.scan_opportunities(runs=50)
        top = bot.get_top_opportunities(n=2)
        assert len(top) == 2

    def test_generate_tiktok_content(self):
        bot = _make_bot(Tier.PRO)
        decision = bot.decide(_simple_context())
        script = bot.generate_content(decision, fmt=ContentFormat.TIKTOK)
        assert isinstance(script, ContentScript)
        assert script.format == ContentFormat.TIKTOK

    def test_generate_youtube_content(self):
        bot = _make_bot(Tier.PRO)
        decision = bot.decide(_simple_context())
        script = bot.generate_content(decision, fmt=ContentFormat.YOUTUBE)
        assert script.format == ContentFormat.YOUTUBE

    def test_map_dimensions_pro(self):
        bot = _make_bot(Tier.PRO)
        dims = bot.map_dimensions(TimeHorizon.MEDIUM, 20000.0, RiskLevel.MODERATE, ScaleGoal.REGIONAL)
        assert "composite_multiplier" in dims

    def test_dimensions_in_decision_when_pro(self):
        bot = _make_bot(Tier.PRO)
        result = bot.decide({"budget": 10000, "risk_level": "safe"})
        assert result.dimensions

    def test_process_scan_command(self):
        bot = _make_bot(Tier.PRO)
        result = bot.process("scan", {"runs": 50})
        assert result["command"] == "scan"
        assert "top_3" in result

    def test_process_content_command(self):
        bot = _make_bot(Tier.PRO)
        bot.decide(_simple_context())
        result = bot.process("content", {"format": "tiktok"})
        assert result["command"] == "content"
        assert "hook" in result

    def test_process_map_command(self):
        bot = _make_bot(Tier.PRO)
        result = bot.process("map", {
            "time_horizon": "medium",
            "budget": 15000,
            "risk_level": "moderate",
            "scale_goal": "regional",
        })
        assert result["command"] == "map"
        assert "composite_multiplier" in result

    def test_pro_simulation_runs(self):
        bot = _make_bot(Tier.PRO)
        result = bot.decide(_simple_context())
        assert result.best_path.simulation.runs == 10_000

    def test_pro_unlimited_scenarios(self):
        bot = _make_bot(Tier.PRO)
        ctx = {
            "scenarios": [
                {"name": f"s{i}", "base_profit": float(i * 5000), "risk_score": float(i % 9 + 1)}
                for i in range(1, 8)
            ]
        }
        result = bot.decide(ctx)
        total = 1 + len(result.alternatives)
        assert total == 7


# ===========================================================================
# 12. QuantumDecisionBot — ENTERPRISE tier
# ===========================================================================


class TestQuantumDecisionBotEnterprise:
    def test_instantiation(self):
        bot = _make_bot(Tier.ENTERPRISE)
        assert bot.tier == Tier.ENTERPRISE

    def test_record_outcome(self):
        bot = _make_bot(Tier.ENTERPRISE)
        decision = bot.decide(_simple_context())
        record = bot.record_outcome(decision, actual_profit=20000.0)
        assert isinstance(record, LearningRecord)

    def test_learning_records_accumulate(self):
        bot = _make_bot(Tier.ENTERPRISE)
        decision = bot.decide(_simple_context())
        bot.record_outcome(decision, 10000.0)
        bot.record_outcome(decision, 5000.0)
        assert len(bot.get_learning_records()) == 2

    def test_get_learning_summary(self):
        bot = _make_bot(Tier.ENTERPRISE)
        decision = bot.decide(_simple_context())
        bot.record_outcome(decision, 15000.0)
        summary = bot.get_learning_summary()
        assert "accuracy" in summary
        assert "total_records" in summary

    def test_accuracy_between_0_and_1(self):
        bot = _make_bot(Tier.ENTERPRISE)
        decision = bot.decide(_simple_context())
        for profit in [1000.0, 50000.0, 30000.0]:
            bot.record_outcome(decision, profit)
        summary = bot.get_learning_summary()
        assert 0.0 <= summary["accuracy"] <= 1.0

    def test_process_learn_command(self):
        bot = _make_bot(Tier.ENTERPRISE)
        bot.decide(_simple_context())
        result = bot.process("learn", {"actual_profit": 25000.0})
        assert result["command"] == "learn"
        assert "was_correct" in result

    def test_enterprise_simulation_runs(self):
        bot = _make_bot(Tier.ENTERPRISE)
        result = bot.decide(_simple_context())
        assert result.best_path.simulation.runs == 100_000

    def test_enterprise_has_all_engines(self):
        bot = _make_bot(Tier.ENTERPRISE)
        assert bot._learning_ai is not None
        assert bot._bot_router is not None
        assert bot._money_engine is not None
        assert bot._content_engine is not None

    def test_learning_improves_model_over_time(self):
        bot = _make_bot(Tier.ENTERPRISE)
        decision = bot.decide(_simple_context())
        scenario_name = decision.best_path.scenario.name
        before = bot._probability_model.get_adjustment(scenario_name)
        # Force a successful outcome
        bot.record_outcome(decision, actual_profit=decision.best_path.simulation.avg_profit * 5)
        after = bot._probability_model.get_adjustment(scenario_name)
        assert after > before


# ===========================================================================
# 13. Tier restrictions
# ===========================================================================


class TestTierRestrictions:
    def test_free_cannot_broadcast_decision(self):
        bot = _make_bot(Tier.FREE)
        decision = bot.decide(_simple_context())
        with pytest.raises(QuantumDecisionBotTierError):
            bot.broadcast_decision(decision)

    def test_free_cannot_scan_opportunities(self):
        bot = _make_bot(Tier.FREE)
        with pytest.raises(QuantumDecisionBotTierError):
            bot.scan_opportunities()

    def test_free_cannot_generate_content(self):
        bot = _make_bot(Tier.FREE)
        decision = bot.decide(_simple_context())
        with pytest.raises(QuantumDecisionBotTierError):
            bot.generate_content(decision)

    def test_free_cannot_map_dimensions(self):
        bot = _make_bot(Tier.FREE)
        with pytest.raises(QuantumDecisionBotTierError):
            bot.map_dimensions(TimeHorizon.MEDIUM, 10000.0, RiskLevel.MODERATE, ScaleGoal.LOCAL)

    def test_free_cannot_record_outcome(self):
        bot = _make_bot(Tier.FREE)
        decision = bot.decide(_simple_context())
        with pytest.raises(QuantumDecisionBotTierError):
            bot.record_outcome(decision, 10000.0)

    def test_pro_cannot_record_outcome(self):
        bot = _make_bot(Tier.PRO)
        decision = bot.decide(_simple_context())
        with pytest.raises(QuantumDecisionBotTierError):
            bot.record_outcome(decision, 10000.0)

    def test_pro_cannot_get_learning_summary(self):
        bot = _make_bot(Tier.PRO)
        with pytest.raises(QuantumDecisionBotTierError):
            bot.get_learning_summary()

    def test_tier_error_message_mentions_upgrade(self):
        bot = _make_bot(Tier.FREE)
        with pytest.raises(QuantumDecisionBotTierError) as exc_info:
            bot.scan_opportunities()
        assert "upgrade" in str(exc_info.value).lower() or "Upgrade" in str(exc_info.value)

    def test_process_scan_on_free_raises(self):
        bot = _make_bot(Tier.FREE)
        with pytest.raises(QuantumDecisionBotTierError):
            bot.process("scan", {"runs": 50})

    def test_process_learn_on_pro_raises(self):
        bot = _make_bot(Tier.PRO)
        bot.decide(_simple_context())
        with pytest.raises(QuantumDecisionBotTierError):
            bot.process("learn", {"actual_profit": 5000.0})


# ===========================================================================
# 14. process() command interface
# ===========================================================================


class TestProcessInterface:
    def test_decide_via_process(self):
        bot = _make_bot(Tier.FREE)
        result = bot.process("decide", {"summary": "Test via process"})
        assert result["command"] == "decide"
        assert "decision_id" in result

    def test_status_shows_decision_count(self):
        bot = _make_bot(Tier.FREE)
        bot.decide(_simple_context())
        bot.decide(_simple_context())
        result = bot.process("status")
        assert result["decisions_made"] == 2

    def test_content_without_prior_decision_returns_error(self):
        bot = _make_bot(Tier.PRO)
        result = bot.process("content", {"format": "youtube"})
        assert "error" in result

    def test_learn_without_prior_decision_returns_error(self):
        bot = _make_bot(Tier.ENTERPRISE)
        result = bot.process("learn", {"actual_profit": 0.0})
        assert "error" in result

    def test_process_map_returns_dimensions(self):
        bot = _make_bot(Tier.PRO)
        result = bot.process("map", {
            "time_horizon": "long",
            "budget": 50000,
            "risk_level": "aggressive",
            "scale_goal": "global",
        })
        assert result["scale_goal"] == "global"

    def test_process_content_uses_last_decision(self):
        bot = _make_bot(Tier.PRO)
        bot.process("decide", {"summary": "First decision"})
        bot.process("decide", {"summary": "Second decision"})
        result = bot.process("content", {"format": "instagram"})
        assert result["command"] == "content"
        assert "hook" in result


# ===========================================================================
# 15. Bot library registration
# ===========================================================================


class TestBotLibraryRegistration:
    def test_quantum_bot_registered(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        ids = [e.bot_id for e in _DREAMCO_BOTS]
        assert "quantum_decision_bot" in ids

    def test_quantum_bot_category_is_ai(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS, BotCategory
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "quantum_decision_bot")
        assert entry.category == BotCategory.AI

    def test_quantum_bot_has_key_capabilities(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "quantum_decision_bot")
        for cap in ["quantum_decision_engine", "monte_carlo_simulation", "entangled_bot_routing"]:
            assert cap in entry.capabilities

    def test_quantum_bot_class_name(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "quantum_decision_bot")
        assert entry.class_name == "QuantumDecisionBot"

    def test_quantum_bot_module_path(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "quantum_decision_bot")
        assert "quantum_decision_bot" in entry.module_path
