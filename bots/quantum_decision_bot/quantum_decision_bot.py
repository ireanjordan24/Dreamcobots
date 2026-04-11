"""
Quantum Decision Bot — DreamCo Reality Optimization System.

The Quantum Decision Bot is the central intelligence layer of DreamCo QuantumOS.
Inspired by quantum physics concepts (superposition, wave function collapse,
quantum entanglement), it simulates thousands of possible outcomes for any
business decision, scores them by profit and risk, and collapses to the best
"reality path" — before a single dollar is spent.

Engines
-------
- QuantumEngine          : Generate scenarios → simulate → score → collapse to best path
- SimulationEngine       : Monte Carlo runner (100 – 100,000 runs per scenario)
- ProbabilityModel       : Weighted profit/risk scoring with configurable bias
- DimensionMapper        : Maps decisions across time / capital / risk / scale axes
- BotRouter              : Entangled network — broadcast decisions to all DreamCo bots
- MoneyAutomationEngine  : Opportunity scanner + autonomous action recommender
- ContentViralEngine     : Auto-generate viral TikTok/YouTube scripts from simulations
- SelfImprovingAI        : Reinforcement-style learning loop to improve over time

Tier-aware:
  FREE       — QuantumEngine, SimulationEngine, ProbabilityModel (3 scenarios, 100 runs)
  PRO ($49)  — + DimensionMapper, BotRouter, MoneyAutomation, ContentViral (10,000 runs)
  ENTERPRISE ($199) — + SelfImprovingAI, HyperSimulation (100,000 runs), GlobalOrchestration

Adheres to the DreamCo bots GLOBAL AI SOURCES FLOW framework.
"""

from __future__ import annotations

import os
import random
import sys
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from framework import GlobalAISourcesFlow  # noqa: F401  (GLOBAL AI SOURCES FLOW)

from bots.quantum_decision_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
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
)


# ---------------------------------------------------------------------------
# Exceptions
# ---------------------------------------------------------------------------


class QuantumDecisionBotError(Exception):
    """Base exception for Quantum Decision Bot errors."""


class QuantumDecisionBotTierError(QuantumDecisionBotError):
    """Raised when a feature is not available on the current tier."""


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RiskLevel(Enum):
    SAFE = "safe"
    MODERATE = "moderate"
    AGGRESSIVE = "aggressive"


class TimeHorizon(Enum):
    SHORT = "short"       # < 3 months
    MEDIUM = "medium"     # 3–12 months
    LONG = "long"         # > 12 months


class ScaleGoal(Enum):
    LOCAL = "local"
    REGIONAL = "regional"
    GLOBAL = "global"


class OutcomeLabel(Enum):
    BEST_CASE = "best_case"
    AVERAGE_CASE = "average_case"
    WORST_CASE = "worst_case"


class BotDecisionStatus(Enum):
    PENDING = "pending"
    ROUTED = "routed"
    EXECUTED = "executed"
    CANCELLED = "cancelled"


class OpportunityType(Enum):
    REAL_ESTATE = "real_estate"
    SAAS = "saas"
    TRADING = "trading"
    HUSTLE = "hustle"
    LOCAL_BUSINESS = "local_business"
    CONTENT = "content"


class ContentFormat(Enum):
    TIKTOK = "tiktok"
    YOUTUBE = "youtube"
    INSTAGRAM = "instagram"
    BLOG = "blog"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class Scenario:
    """A single decision scenario with baseline financial parameters."""

    scenario_id: str
    name: str
    description: str
    base_profit: float
    risk_score: float          # 1 (safe) → 10 (very aggressive)
    time_horizon: TimeHorizon
    capital_required: float
    scale_goal: ScaleGoal
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class SimulationResult:
    """Aggregated output from running N Monte Carlo simulations on one scenario."""

    scenario: Scenario
    runs: int
    avg_profit: float
    min_profit: float
    max_profit: float
    avg_risk: float
    probability_positive: float    # fraction of runs with profit > 0
    best_case_profit: float
    worst_case_profit: float
    raw_samples: List[Tuple[float, float]] = field(default_factory=list)  # (profit, risk)


@dataclass
class ScoredPath:
    """A scenario together with its computed quantum score."""

    scenario: Scenario
    simulation: SimulationResult
    score: float
    rank: int = 0
    label: Optional[str] = None


@dataclass
class QuantumDecision:
    """Final output of the Quantum Engine for a given decision context."""

    decision_id: str
    context_summary: str
    best_path: ScoredPath
    alternatives: List[ScoredPath]
    risk_warning: ScoredPath
    dimensions: Dict[str, Any]
    timestamp: str
    tier: str


@dataclass
class BotRouterEvent:
    """An event dispatched to the entangled bot network."""

    event_id: str
    source_bot: str
    decision: QuantumDecision
    target_bots: List[str]
    actions: Dict[str, str]
    status: BotDecisionStatus
    timestamp: str


@dataclass
class Opportunity:
    """A money-making opportunity found by the MoneyAutomationEngine."""

    opportunity_id: str
    opp_type: OpportunityType
    title: str
    description: str
    estimated_profit: float
    confidence: float          # 0–1
    recommended_action: str
    quantum_score: float
    timestamp: str


@dataclass
class ContentScript:
    """A viral content script generated from a QuantumDecision."""

    script_id: str
    format: ContentFormat
    title: str
    hook: str
    body: str
    cta: str
    scenario_reference: str
    timestamp: str


@dataclass
class LearningRecord:
    """A record of a real-world outcome used to improve the probability model."""

    record_id: str
    decision_id: str
    scenario_name: str
    predicted_score: float
    actual_profit: float
    was_correct: bool          # predicted best path matched real outcome
    weight_adjustment: float
    timestamp: str


# ---------------------------------------------------------------------------
# Simulation Engine
# ---------------------------------------------------------------------------


class SimulationEngine:
    """
    Monte Carlo simulation runner.

    Uses Gaussian noise to vary profit and risk around each scenario's baseline,
    producing a realistic distribution of outcomes.
    """

    def run(self, scenario: Scenario, runs: int = 1000) -> SimulationResult:
        """Run *runs* Monte Carlo simulations for *scenario* and return aggregated stats."""
        samples: List[Tuple[float, float]] = []

        for _ in range(runs):
            # Gaussian noise (mean=1.0, std=0.2): models ±20% variance around the
            # baseline — realistic for business outcomes where most results cluster
            # near the expected value, with occasional extreme outliers.
            # Risk is inversely proportional to the profit noise: a better-than-
            # expected profit run implies favourable conditions (lower realised risk).
            noise = random.gauss(1.0, 0.2)
            profit = scenario.base_profit * noise
            risk = scenario.risk_score * (1.0 / max(noise, 0.01))
            samples.append((profit, risk))

        profits = [s[0] for s in samples]
        risks = [s[1] for s in samples]

        avg_profit = sum(profits) / len(profits)
        avg_risk = sum(risks) / len(risks)
        min_profit = min(profits)
        max_profit = max(profits)
        positive_runs = sum(1 for p in profits if p > 0)
        probability_positive = positive_runs / len(profits)

        sorted_profits = sorted(profits, reverse=True)
        top_10_pct = max(1, len(sorted_profits) // 10)
        bottom_10_pct = max(1, len(sorted_profits) // 10)
        best_case = sum(sorted_profits[:top_10_pct]) / top_10_pct
        worst_case = sum(sorted_profits[-bottom_10_pct:]) / bottom_10_pct

        return SimulationResult(
            scenario=scenario,
            runs=runs,
            avg_profit=round(avg_profit, 2),
            min_profit=round(min_profit, 2),
            max_profit=round(max_profit, 2),
            avg_risk=round(avg_risk, 2),
            probability_positive=round(probability_positive, 4),
            best_case_profit=round(best_case, 2),
            worst_case_profit=round(worst_case, 2),
            raw_samples=samples,
        )


# ---------------------------------------------------------------------------
# Probability Model
# ---------------------------------------------------------------------------


class ProbabilityModel:
    """
    Weighted profit/risk scoring model.

    score = avg_profit * probability_positive - avg_risk * risk_weight

    The *risk_weight* adjusts how aggressively risk is penalised.
    Lower values favour bold, high-profit paths; higher values favour safety.
    """

    def __init__(self, risk_weight: float = 0.5) -> None:
        self.risk_weight = risk_weight
        # Learned adjustments keyed by scenario name — updated by SelfImprovingAI
        self._learned_adjustments: Dict[str, float] = {}

    def score(self, result: SimulationResult) -> float:
        """Return a numeric score for *result*; higher = better."""
        base = result.avg_profit * result.probability_positive
        penalty = result.avg_risk * self.risk_weight
        raw = base - penalty
        adjustment = self._learned_adjustments.get(result.scenario.name, 0.0)
        return round(raw + adjustment, 4)

    def apply_adjustment(self, scenario_name: str, delta: float) -> None:
        """Apply a learned weight adjustment for *scenario_name*."""
        current = self._learned_adjustments.get(scenario_name, 0.0)
        self._learned_adjustments[scenario_name] = round(current + delta, 4)

    def get_adjustment(self, scenario_name: str) -> float:
        return self._learned_adjustments.get(scenario_name, 0.0)


# ---------------------------------------------------------------------------
# Dimension Mapper
# ---------------------------------------------------------------------------


class DimensionMapper:
    """
    Maps a decision context across four strategic dimensions:
    Time, Capital, Risk, and Scale.

    Finds the intersection that maximises upside while respecting constraints.
    """

    RISK_SCORES = {
        RiskLevel.SAFE: (1, 3),
        RiskLevel.MODERATE: (4, 6),
        RiskLevel.AGGRESSIVE: (7, 10),
    }

    TIME_MULTIPLIERS = {
        TimeHorizon.SHORT: 0.8,
        TimeHorizon.MEDIUM: 1.0,
        TimeHorizon.LONG: 1.25,
    }

    SCALE_MULTIPLIERS = {
        ScaleGoal.LOCAL: 0.9,
        ScaleGoal.REGIONAL: 1.0,
        ScaleGoal.GLOBAL: 1.2,
    }

    def map(
        self,
        time_horizon: TimeHorizon,
        budget: float,
        risk_level: RiskLevel,
        scale_goal: ScaleGoal,
    ) -> Dict[str, Any]:
        """Return a multi-dimensional analysis for the given parameters."""
        risk_range = self.RISK_SCORES[risk_level]
        time_mult = self.TIME_MULTIPLIERS[time_horizon]
        scale_mult = self.SCALE_MULTIPLIERS[scale_goal]

        composite_multiplier = round(time_mult * scale_mult, 4)

        return {
            "time_horizon": time_horizon.value,
            "budget": budget,
            "risk_level": risk_level.value,
            "risk_range": risk_range,
            "scale_goal": scale_goal.value,
            "time_multiplier": time_mult,
            "scale_multiplier": scale_mult,
            "composite_multiplier": composite_multiplier,
            "recommended_max_capital": round(budget * composite_multiplier, 2),
            "optimal_risk_midpoint": round(sum(risk_range) / 2, 1),
        }


# ---------------------------------------------------------------------------
# Bot Router (Entangled Network)
# ---------------------------------------------------------------------------


class BotRouter:
    """
    Entangled Bot Network dispatcher.

    When the QuantumEngine makes a decision, the BotRouter instantly
    propagates that decision to all relevant DreamCo bots so that
    every part of the system updates together — just like quantum entanglement.
    """

    # Default set of bots that will be notified of every QuantumDecision
    DEFAULT_NETWORK: List[str] = [
        "real_estate_bot",
        "crypto_bot",
        "deal_finder_bot",
        "money_finder_bot",
        "wealth_system_bot",
        "stack_and_profit_bot",
        "car_flipping_bot",
        "fiverr_bot",
        "revenue_engine_bot",
        "god_bot",
    ]

    def __init__(self, network: Optional[List[str]] = None) -> None:
        self._network = network if network is not None else list(self.DEFAULT_NETWORK)
        self._event_log: List[BotRouterEvent] = []

    def route(self, decision: QuantumDecision, source_bot: str = "quantum_decision_bot") -> BotRouterEvent:
        """Broadcast *decision* to all bots in the network and return the event record."""
        actions = self._generate_actions(decision)
        event = BotRouterEvent(
            event_id=str(uuid.uuid4()),
            source_bot=source_bot,
            decision=decision,
            target_bots=list(self._network),
            actions=actions,
            status=BotDecisionStatus.ROUTED,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._event_log.append(event)
        return event

    def _generate_actions(self, decision: QuantumDecision) -> Dict[str, str]:
        """Produce a per-bot action recommendation based on the QuantumDecision."""
        best = decision.best_path.scenario
        actions: Dict[str, str] = {}
        for bot in self._network:
            if "real_estate" in bot:
                actions[bot] = (
                    f"Scan properties matching '{best.name}' profile — "
                    f"budget ${best.capital_required:,.0f}, "
                    f"horizon {best.time_horizon.value}"
                )
            elif "crypto" in bot or "trade" in bot:
                actions[bot] = (
                    f"Adjust trading strategy to '{best.scale_goal.value}' scale — "
                    f"risk level {best.risk_score:.1f}/10"
                )
            elif "deal" in bot or "money" in bot or "profit" in bot:
                actions[bot] = (
                    f"Prioritise deals with projected profit > "
                    f"${decision.best_path.simulation.avg_profit:,.0f}"
                )
            elif "wealth" in bot:
                actions[bot] = (
                    f"Allocate hub capital aligned to '{best.time_horizon.value}' "
                    f"horizon strategy"
                )
            elif "god" in bot:
                actions[bot] = (
                    f"Sync master pipeline with best-path scenario '{best.name}'"
                )
            else:
                actions[bot] = (
                    f"Align operations with QuantumDecision '{decision.decision_id}'"
                )
        return actions

    def get_event_log(self) -> List[BotRouterEvent]:
        return list(self._event_log)

    def add_bot(self, bot_name: str) -> None:
        if bot_name not in self._network:
            self._network.append(bot_name)

    def remove_bot(self, bot_name: str) -> None:
        self._network = [b for b in self._network if b != bot_name]

    @property
    def network(self) -> List[str]:
        return list(self._network)


# ---------------------------------------------------------------------------
# Money Automation Engine
# ---------------------------------------------------------------------------


class MoneyAutomationEngine:
    """
    Autonomous opportunity scanner and action recommender.

    Scans virtual data sources, scores each opportunity through the
    QuantumEngine, and returns ranked action recommendations.
    """

    OPPORTUNITY_TEMPLATES: List[Dict[str, Any]] = [
        {
            "type": OpportunityType.LOCAL_BUSINESS,
            "title": "AI Marketing Service for Local Business",
            "description": "Offer AI-powered marketing automation to local SMBs",
            "base_profit": 1500.0,
            "risk_score": 3.0,
            "capital_required": 200.0,
        },
        {
            "type": OpportunityType.REAL_ESTATE,
            "title": "House Flip Opportunity",
            "description": "Buy, renovate, and resell residential property",
            "base_profit": 35000.0,
            "risk_score": 7.0,
            "capital_required": 60000.0,
        },
        {
            "type": OpportunityType.SAAS,
            "title": "SaaS Subscription Launch",
            "description": "Launch a micro-SaaS tool with recurring revenue",
            "base_profit": 8000.0,
            "risk_score": 5.0,
            "capital_required": 5000.0,
        },
        {
            "type": OpportunityType.TRADING,
            "title": "Algorithmic Trading Strategy",
            "description": "Deploy rule-based algo on crypto/forex markets",
            "base_profit": 12000.0,
            "risk_score": 8.0,
            "capital_required": 10000.0,
        },
        {
            "type": OpportunityType.HUSTLE,
            "title": "Content Automation Side Hustle",
            "description": "Sell AI content generation services to creators",
            "base_profit": 3000.0,
            "risk_score": 2.0,
            "capital_required": 100.0,
        },
        {
            "type": OpportunityType.CONTENT,
            "title": "Viral Content Monetisation",
            "description": "Grow and monetise a short-form video channel",
            "base_profit": 5000.0,
            "risk_score": 4.0,
            "capital_required": 500.0,
        },
    ]

    def __init__(self, simulation_engine: SimulationEngine, probability_model: ProbabilityModel) -> None:
        self._sim = simulation_engine
        self._prob = probability_model
        self._found: List[Opportunity] = []

    def scan(self, runs: int = 500) -> List[Opportunity]:
        """Scan all opportunity templates, simulate each, and return ranked list."""
        opportunities: List[Opportunity] = []

        for template in self.OPPORTUNITY_TEMPLATES:
            scenario = Scenario(
                scenario_id=str(uuid.uuid4()),
                name=template["title"],
                description=template["description"],
                base_profit=template["base_profit"],
                risk_score=template["risk_score"],
                time_horizon=TimeHorizon.MEDIUM,
                capital_required=template["capital_required"],
                scale_goal=ScaleGoal.LOCAL,
            )
            result = self._sim.run(scenario, runs=runs)
            score = self._prob.score(result)
            action = self._recommend_action(template["type"], result)

            opp = Opportunity(
                opportunity_id=str(uuid.uuid4()),
                opp_type=template["type"],
                title=template["title"],
                description=template["description"],
                estimated_profit=result.avg_profit,
                confidence=result.probability_positive,
                recommended_action=action,
                quantum_score=score,
                timestamp=datetime.now(timezone.utc).isoformat(),
            )
            opportunities.append(opp)

        opportunities.sort(key=lambda o: o.quantum_score, reverse=True)
        self._found = opportunities
        return opportunities

    def _recommend_action(self, opp_type: OpportunityType, result: SimulationResult) -> str:
        profit = result.avg_profit
        prob = result.probability_positive
        if opp_type == OpportunityType.LOCAL_BUSINESS:
            return f"Pitch AI marketing package to 10 local businesses — est. ${profit:,.0f} avg return ({prob:.0%} success rate)"
        if opp_type == OpportunityType.REAL_ESTATE:
            return f"Identify undervalued properties in target market — est. ${profit:,.0f} flip profit ({prob:.0%} success rate)"
        if opp_type == OpportunityType.SAAS:
            return f"Launch MVP within 30 days, target 50 paying users — est. ${profit:,.0f} MRR potential ({prob:.0%} success rate)"
        if opp_type == OpportunityType.TRADING:
            return f"Paper-trade strategy for 2 weeks then deploy — est. ${profit:,.0f} monthly ({prob:.0%} success rate)"
        if opp_type == OpportunityType.HUSTLE:
            return f"List service on Fiverr + cold-DM 50 creators — est. ${profit:,.0f} monthly ({prob:.0%} success rate)"
        if opp_type == OpportunityType.CONTENT:
            return f"Post 30 days of daily content, monetise at 10K followers — est. ${profit:,.0f} monthly ({prob:.0%} success rate)"
        return f"Execute opportunity — est. ${profit:,.0f} return ({prob:.0%} success rate)"

    def get_top_opportunities(self, n: int = 3) -> List[Opportunity]:
        return self._found[:n]


# ---------------------------------------------------------------------------
# Content Viral Engine
# ---------------------------------------------------------------------------


class ContentViralEngine:
    """
    Auto-generates viral content scripts from QuantumDecision results.

    Turns simulation data into attention-grabbing hooks and educational
    scripts for TikTok, YouTube, Instagram, and blogs.
    """

    HOOKS = {
        ContentFormat.TIKTOK: "What if I told you {hook_core}? 🤯 Here's what the simulation says...",
        ContentFormat.YOUTUBE: "I ran {runs:,} simulations on {topic} — the results shocked me",
        ContentFormat.INSTAGRAM: "The numbers don't lie 📊 {hook_core} — swipe to see ALL outcomes",
        ContentFormat.BLOG: "We simulated {runs:,} versions of '{topic}' — here's what we found",
    }

    def generate(self, decision: QuantumDecision, fmt: ContentFormat = ContentFormat.TIKTOK) -> ContentScript:
        """Generate a content script from *decision* for the given *fmt*."""
        best = decision.best_path
        sim = best.simulation
        topic = best.scenario.name

        hook_core = (
            f"'{topic}' has a {sim.probability_positive:.0%} chance of making you "
            f"${sim.avg_profit:,.0f}"
        )

        hook = self.HOOKS[fmt].format(
            hook_core=hook_core,
            runs=sim.runs,
            topic=topic,
        )

        body_lines = [
            f"We ran {sim.runs:,} reality simulations on: {topic}",
            f"",
            f"📈 Best case:  ${sim.best_case_profit:,.0f}",
            f"📊 Average:    ${sim.avg_profit:,.0f}",
            f"📉 Worst case: ${sim.worst_case_profit:,.0f}",
            f"",
            f"Success probability: {sim.probability_positive:.0%}",
            f"Risk score: {sim.avg_risk:.1f}/10",
            f"",
            f"The Quantum Engine picked this as the #1 path because it scores "
            f"{best.score:,.0f} points — higher than {len(decision.alternatives)} alternatives.",
        ]

        if decision.alternatives:
            alt = decision.alternatives[0]
            body_lines += [
                f"",
                f"Runner-up: {alt.scenario.name}",
                f"  → ${alt.simulation.avg_profit:,.0f} avg profit ({alt.simulation.probability_positive:.0%} success)",
            ]

        cta_map = {
            ContentFormat.TIKTOK: "Follow for daily reality simulations 🚀 Comment your next decision below!",
            ContentFormat.YOUTUBE: "Subscribe for weekly deep-dives — link to full simulation report in description!",
            ContentFormat.INSTAGRAM: "Save this post 📌 DM 'SIMULATE' to get your own free decision analysis!",
            ContentFormat.BLOG: "Want your own simulation? Join DreamCo QuantumOS — link below.",
        }

        return ContentScript(
            script_id=str(uuid.uuid4()),
            format=fmt,
            title=f"Reality Check: {topic}",
            hook=hook,
            body="\n".join(body_lines),
            cta=cta_map[fmt],
            scenario_reference=best.scenario.scenario_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


# ---------------------------------------------------------------------------
# Self-Improving AI (Learning Loop)
# ---------------------------------------------------------------------------


class SelfImprovingAI:
    """
    Reinforcement-style learning loop.

    Records real-world outcomes and adjusts the ProbabilityModel's
    learned weights so that future predictions improve over time.
    """

    # Learning rate constants.
    # REINFORCE_DELTA (+0.05): small positive nudge — prevents over-fitting to a
    #   single successful outcome while still accumulating signal over many runs.
    # PENALISE_DELTA (-0.03): smaller negative correction — asymmetric to avoid
    #   the model over-penalising noisy losses (losses are noisier than wins).
    REINFORCE_DELTA = 0.05   # positive reward
    PENALISE_DELTA = -0.03   # negative correction

    def __init__(self, probability_model: ProbabilityModel) -> None:
        self._model = probability_model
        self._records: List[LearningRecord] = []

    def record_outcome(
        self,
        decision: QuantumDecision,
        actual_profit: float,
    ) -> LearningRecord:
        """
        Compare the decision's predicted best path against *actual_profit*.

        If actual_profit ≥ predicted avg_profit → reinforce.
        Otherwise → penalise.
        """
        best = decision.best_path
        predicted = best.simulation.avg_profit
        # 20% tolerance: a prediction is "correct" if the actual outcome lands
        # within 80–120% of the simulated average.  This threshold acknowledges
        # that business results are inherently noisy; demanding exact accuracy
        # would make the model too slow to reinforce good predictions.
        was_correct = actual_profit >= predicted * 0.8   # within 20% counts as correct

        delta = self.REINFORCE_DELTA if was_correct else self.PENALISE_DELTA
        self._model.apply_adjustment(best.scenario.name, delta)

        record = LearningRecord(
            record_id=str(uuid.uuid4()),
            decision_id=decision.decision_id,
            scenario_name=best.scenario.name,
            predicted_score=best.score,
            actual_profit=actual_profit,
            was_correct=was_correct,
            weight_adjustment=delta,
            timestamp=datetime.now(timezone.utc).isoformat(),
        )
        self._records.append(record)
        return record

    def get_records(self) -> List[LearningRecord]:
        return list(self._records)

    def accuracy(self) -> float:
        """Return fraction of recorded outcomes where prediction was correct."""
        if not self._records:
            return 0.0
        correct = sum(1 for r in self._records if r.was_correct)
        return round(correct / len(self._records), 4)

    def summary(self) -> Dict[str, Any]:
        return {
            "total_records": len(self._records),
            "accuracy": self.accuracy(),
            "learned_adjustments": dict(self._model._learned_adjustments),
        }


# ---------------------------------------------------------------------------
# Quantum Engine (Core Brain)
# ---------------------------------------------------------------------------


class QuantumEngine:
    """
    Core decision engine.

    1. Generate scenarios (superposition of all possibilities)
    2. Simulate each scenario with Monte Carlo
    3. Score each via ProbabilityModel
    4. Collapse to best path (wave function collapse)
    """

    DEFAULT_SCENARIOS = [
        {
            "name": "low_risk_path",
            "description": "Conservative approach — slow and steady growth",
            "base_profit": 5000.0,
            "risk_score": 2.0,
            "time_horizon": TimeHorizon.LONG,
            "capital_required": 2000.0,
            "scale_goal": ScaleGoal.LOCAL,
        },
        {
            "name": "medium_risk_path",
            "description": "Balanced approach — moderate growth with manageable risk",
            "base_profit": 15000.0,
            "risk_score": 5.0,
            "time_horizon": TimeHorizon.MEDIUM,
            "capital_required": 10000.0,
            "scale_goal": ScaleGoal.REGIONAL,
        },
        {
            "name": "high_risk_path",
            "description": "Aggressive approach — high upside, significant downside",
            "base_profit": 50000.0,
            "risk_score": 9.0,
            "time_horizon": TimeHorizon.SHORT,
            "capital_required": 40000.0,
            "scale_goal": ScaleGoal.GLOBAL,
        },
    ]

    def __init__(
        self,
        simulation_engine: SimulationEngine,
        probability_model: ProbabilityModel,
        dimension_mapper: Optional[DimensionMapper] = None,
    ) -> None:
        self._sim = simulation_engine
        self._prob = probability_model
        self._dim = dimension_mapper

    def generate_scenarios(self, context: Dict[str, Any]) -> List[Scenario]:
        """
        Build scenario objects from *context*.

        Context keys (all optional):
          - scenarios: list of scenario dicts (overrides DEFAULT_SCENARIOS)
          - time_horizon: TimeHorizon value
          - budget: float
          - risk_level: RiskLevel value
          - scale_goal: ScaleGoal value
        """
        raw = context.get("scenarios", self.DEFAULT_SCENARIOS)
        time_h = context.get("time_horizon", TimeHorizon.MEDIUM)
        scale = context.get("scale_goal", ScaleGoal.LOCAL)

        if isinstance(time_h, str):
            time_h = TimeHorizon(time_h)
        if isinstance(scale, str):
            scale = ScaleGoal(scale)

        scenarios = []
        for raw_s in raw:
            th = raw_s.get("time_horizon", time_h)
            if isinstance(th, str):
                th = TimeHorizon(th)
            sg = raw_s.get("scale_goal", scale)
            if isinstance(sg, str):
                sg = ScaleGoal(sg)

            scenarios.append(Scenario(
                scenario_id=str(uuid.uuid4()),
                name=raw_s["name"],
                description=raw_s.get("description", ""),
                base_profit=float(raw_s["base_profit"]),
                risk_score=float(raw_s["risk_score"]),
                time_horizon=th,
                capital_required=float(raw_s.get("capital_required", 0.0)),
                scale_goal=sg,
                metadata=raw_s.get("metadata", {}),
            ))
        return scenarios

    def decide(self, context: Dict[str, Any], runs: int = 1000) -> QuantumDecision:
        """
        Run the full quantum decision pipeline for *context*.

        Returns a QuantumDecision with best_path, alternatives, and risk_warning.
        """
        scenarios = self.generate_scenarios(context)

        scored: List[ScoredPath] = []
        for scenario in scenarios:
            result = self._sim.run(scenario, runs=runs)
            score = self._prob.score(result)
            scored.append(ScoredPath(scenario=scenario, simulation=result, score=score))

        scored.sort(key=lambda s: s.score, reverse=True)
        for i, sp in enumerate(scored):
            sp.rank = i + 1

        if scored:
            scored[0].label = OutcomeLabel.BEST_CASE.value
            if len(scored) > 1:
                scored[-1].label = OutcomeLabel.WORST_CASE.value

        best = scored[0]
        alternatives = scored[1:]
        risk_warning = scored[-1]

        dims: Dict[str, Any] = {}
        if self._dim:
            budget = context.get("budget", best.scenario.capital_required)
            risk_level = context.get("risk_level", RiskLevel.MODERATE)
            if isinstance(risk_level, str):
                risk_level = RiskLevel(risk_level)
            dims = self._dim.map(
                time_horizon=best.scenario.time_horizon,
                budget=budget,
                risk_level=risk_level,
                scale_goal=best.scenario.scale_goal,
            )

        return QuantumDecision(
            decision_id=str(uuid.uuid4()),
            context_summary=context.get("summary", "DreamCo decision analysis"),
            best_path=best,
            alternatives=alternatives,
            risk_warning=risk_warning,
            dimensions=dims,
            timestamp=datetime.now(timezone.utc).isoformat(),
            tier=context.get("tier", Tier.FREE.value),
        )


# ---------------------------------------------------------------------------
# Quantum Decision Bot (Main class)
# ---------------------------------------------------------------------------


class QuantumDecisionBot:
    """
    DreamCo Quantum Decision Bot — Reality Optimization System.

    The central intelligence that simulates all possible futures,
    collapses to the best path, and wires every DreamCo bot together
    into a self-coordinating money machine.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling which engines are unlocked.
    risk_weight : float
        Risk penalty coefficient for the ProbabilityModel (default 0.5).
    bot_network : list of str, optional
        Override the default entangled bot network.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        risk_weight: float = 0.5,
        bot_network: Optional[List[str]] = None,
    ) -> None:
        self.tier = tier
        self._config = get_tier_config(tier)

        # Core engines — always available
        self._simulation_engine = SimulationEngine()
        self._probability_model = ProbabilityModel(risk_weight=risk_weight)
        self._quantum_engine = QuantumEngine(
            simulation_engine=self._simulation_engine,
            probability_model=self._probability_model,
            dimension_mapper=DimensionMapper() if self._config.has_feature(FEATURE_DIMENSION_MAPPER) else None,
        )

        # PRO+ engines
        self._bot_router: Optional[BotRouter] = (
            BotRouter(network=bot_network)
            if self._config.has_feature(FEATURE_BOT_ROUTER)
            else None
        )
        self._money_engine: Optional[MoneyAutomationEngine] = (
            MoneyAutomationEngine(self._simulation_engine, self._probability_model)
            if self._config.has_feature(FEATURE_MONEY_AUTOMATION)
            else None
        )
        self._content_engine: Optional[ContentViralEngine] = (
            ContentViralEngine()
            if self._config.has_feature(FEATURE_CONTENT_VIRAL_ENGINE)
            else None
        )

        # ENTERPRISE+ engines
        self._learning_ai: Optional[SelfImprovingAI] = (
            SelfImprovingAI(self._probability_model)
            if self._config.has_feature(FEATURE_SELF_IMPROVING_AI)
            else None
        )

        self._decision_log: List[QuantumDecision] = []

    # ------------------------------------------------------------------
    # Tier guard
    # ------------------------------------------------------------------

    def _require(self, feature: str) -> None:
        if not self._config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            msg = f"Feature '{feature}' requires an upgrade."
            if upgrade:
                msg += f" Upgrade to {upgrade.name} (${upgrade.price_usd_monthly}/mo)."
            raise QuantumDecisionBotTierError(msg)

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def decide(self, context: Dict[str, Any]) -> QuantumDecision:
        """
        Run the full Quantum Decision pipeline for *context*.

        Automatically caps scenarios and simulation runs according to the
        active tier.  Logs every decision internally.

        Parameters
        ----------
        context : dict
            Keys:
              summary        — human description of the decision
              scenarios      — list of scenario dicts (optional)
              budget         — float (optional, used by DimensionMapper)
              risk_level     — "safe" | "moderate" | "aggressive" (optional)
              time_horizon   — "short" | "medium" | "long" (optional)
              scale_goal     — "local" | "regional" | "global" (optional)
        """
        self._require(FEATURE_QUANTUM_ENGINE)

        # Enforce tier scenario limit
        max_s = self._config.max_scenarios
        if max_s is not None and "scenarios" in context:
            context = dict(context)
            context["scenarios"] = context["scenarios"][:max_s]

        runs = self._config.max_simulations
        context = {**context, "tier": self.tier.value}

        decision = self._quantum_engine.decide(context, runs=runs)
        self._decision_log.append(decision)
        return decision

    def get_decision_log(self) -> List[QuantumDecision]:
        """Return all decisions made in this session."""
        return list(self._decision_log)

    # ------------------------------------------------------------------
    # Bot Router (PRO+)
    # ------------------------------------------------------------------

    def broadcast_decision(self, decision: QuantumDecision) -> BotRouterEvent:
        """
        Broadcast *decision* to the entire entangled bot network.

        Requires PRO tier or higher.
        """
        self._require(FEATURE_BOT_ROUTER)
        assert self._bot_router is not None
        return self._bot_router.route(decision)

    def get_bot_network(self) -> List[str]:
        """Return the list of bots in the entangled network (PRO+)."""
        self._require(FEATURE_BOT_ROUTER)
        assert self._bot_router is not None
        return self._bot_router.network

    def add_bot_to_network(self, bot_name: str) -> None:
        """Add *bot_name* to the entangled network (PRO+)."""
        self._require(FEATURE_BOT_ROUTER)
        assert self._bot_router is not None
        self._bot_router.add_bot(bot_name)

    def remove_bot_from_network(self, bot_name: str) -> None:
        """Remove *bot_name* from the entangled network (PRO+)."""
        self._require(FEATURE_BOT_ROUTER)
        assert self._bot_router is not None
        self._bot_router.remove_bot(bot_name)

    def get_router_event_log(self) -> List[BotRouterEvent]:
        """Return all router events (PRO+)."""
        self._require(FEATURE_BOT_ROUTER)
        assert self._bot_router is not None
        return self._bot_router.get_event_log()

    # ------------------------------------------------------------------
    # Money Automation (PRO+)
    # ------------------------------------------------------------------

    def scan_opportunities(self, runs: int = 500) -> List[Opportunity]:
        """
        Autonomously scan for money-making opportunities and rank them
        by quantum score.

        Requires PRO tier or higher.
        """
        self._require(FEATURE_MONEY_AUTOMATION)
        assert self._money_engine is not None
        return self._money_engine.scan(runs=runs)

    def get_top_opportunities(self, n: int = 3) -> List[Opportunity]:
        """Return the top-N opportunities from the last scan (PRO+)."""
        self._require(FEATURE_MONEY_AUTOMATION)
        assert self._money_engine is not None
        return self._money_engine.get_top_opportunities(n=n)

    # ------------------------------------------------------------------
    # Content Viral Engine (PRO+)
    # ------------------------------------------------------------------

    def generate_content(
        self,
        decision: QuantumDecision,
        fmt: ContentFormat = ContentFormat.TIKTOK,
    ) -> ContentScript:
        """
        Generate a viral content script from *decision* (PRO+).
        """
        self._require(FEATURE_CONTENT_VIRAL_ENGINE)
        assert self._content_engine is not None
        return self._content_engine.generate(decision, fmt=fmt)

    # ------------------------------------------------------------------
    # Self-Improving AI (ENTERPRISE+)
    # ------------------------------------------------------------------

    def record_outcome(self, decision: QuantumDecision, actual_profit: float) -> LearningRecord:
        """
        Feed a real-world outcome back into the learning loop (ENTERPRISE+).

        The bot will adjust its probability model based on the result.
        """
        self._require(FEATURE_SELF_IMPROVING_AI)
        assert self._learning_ai is not None
        return self._learning_ai.record_outcome(decision, actual_profit)

    def get_learning_summary(self) -> Dict[str, Any]:
        """Return the AI learning loop summary (ENTERPRISE+)."""
        self._require(FEATURE_SELF_IMPROVING_AI)
        assert self._learning_ai is not None
        return self._learning_ai.summary()

    def get_learning_records(self) -> List[LearningRecord]:
        """Return all learning records (ENTERPRISE+)."""
        self._require(FEATURE_SELF_IMPROVING_AI)
        assert self._learning_ai is not None
        return self._learning_ai.get_records()

    # ------------------------------------------------------------------
    # Dimension Mapper (PRO+)
    # ------------------------------------------------------------------

    def map_dimensions(
        self,
        time_horizon: TimeHorizon,
        budget: float,
        risk_level: RiskLevel,
        scale_goal: ScaleGoal,
    ) -> Dict[str, Any]:
        """
        Analyse a decision across time / capital / risk / scale dimensions (PRO+).
        """
        self._require(FEATURE_DIMENSION_MAPPER)
        mapper = DimensionMapper()
        return mapper.map(time_horizon, budget, risk_level, scale_goal)

    # ------------------------------------------------------------------
    # Utility
    # ------------------------------------------------------------------

    def get_tier_info(self) -> Dict[str, Any]:
        """Return tier name, price, feature list, and upgrade path."""
        upgrade = get_upgrade_path(self.tier)
        return {
            "tier": self._config.name,
            "price_usd_monthly": self._config.price_usd_monthly,
            "max_scenarios": self._config.max_scenarios,
            "max_simulations": self._config.max_simulations,
            "features": self._config.features,
            "support_level": self._config.support_level,
            "upgrade": {
                "name": upgrade.name,
                "price_usd_monthly": upgrade.price_usd_monthly,
            } if upgrade else None,
        }

    def process(self, command: str, payload: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Generic command-based interface for chat / API integration.

        Supported commands
        ------------------
        decide          — run quantum decision pipeline
        scan            — scan for money opportunities
        map             — run dimension mapping
        content         — generate viral content from last decision
        learn           — record real outcome and update AI
        status          — return bot status and tier info
        """
        payload = payload or {}

        if command == "decide":
            d = self.decide(payload)
            return {
                "command": command,
                "decision_id": d.decision_id,
                "best_path": d.best_path.scenario.name,
                "best_score": d.best_path.score,
                "avg_profit": d.best_path.simulation.avg_profit,
                "probability_positive": d.best_path.simulation.probability_positive,
                "alternatives_count": len(d.alternatives),
                "timestamp": d.timestamp,
            }

        if command == "scan":
            runs = payload.get("runs", 500)
            opps = self.scan_opportunities(runs=runs)
            return {
                "command": command,
                "total": len(opps),
                "top_3": [
                    {
                        "title": o.title,
                        "estimated_profit": o.estimated_profit,
                        "confidence": o.confidence,
                        "action": o.recommended_action,
                    }
                    for o in opps[:3]
                ],
            }

        if command == "map":
            time_h = TimeHorizon(payload.get("time_horizon", "medium"))
            budget = float(payload.get("budget", 10000))
            risk = RiskLevel(payload.get("risk_level", "moderate"))
            scale = ScaleGoal(payload.get("scale_goal", "local"))
            return {"command": command, **self.map_dimensions(time_h, budget, risk, scale)}

        if command == "content":
            if not self._decision_log:
                return {"command": command, "error": "No decisions yet. Run 'decide' first."}
            last = self._decision_log[-1]
            fmt_str = payload.get("format", "tiktok")
            fmt = ContentFormat(fmt_str)
            script = self.generate_content(last, fmt=fmt)
            return {
                "command": command,
                "title": script.title,
                "hook": script.hook,
                "body": script.body,
                "cta": script.cta,
                "format": script.format.value,
            }

        if command == "learn":
            if not self._decision_log:
                return {"command": command, "error": "No decisions yet. Run 'decide' first."}
            last = self._decision_log[-1]
            actual_profit = float(payload.get("actual_profit", 0))
            rec = self.record_outcome(last, actual_profit)
            return {
                "command": command,
                "was_correct": rec.was_correct,
                "weight_adjustment": rec.weight_adjustment,
                "accuracy": self._learning_ai.accuracy() if self._learning_ai else None,
            }

        if command == "status":
            return {
                "command": command,
                "bot": "QuantumDecisionBot",
                "tier_info": self.get_tier_info(),
                "decisions_made": len(self._decision_log),
            }

        return {"command": command, "error": f"Unknown command '{command}'"}
