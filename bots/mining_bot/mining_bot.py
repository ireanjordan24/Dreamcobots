"""
Dreamcobots Mining Bot — optimised, adaptive cryptocurrency mining.

This bot ties together all mining sub-modules into a single, tier-aware
interface:

  * AdaptiveStrategyEngine  — picks the most profitable mining strategy
  * ProfitabilityAnalytics  — tracks hash rate, energy, ROI
  * MiningMonitor           — alerts for downtime and anomalies
  * FraudDetector           — honeypot and contract verification
  * MultiExchangeRouter     — best-rate coin conversion across exchanges

Usage (quick-start)
-------------------
    from bots.mining_bot.mining_bot import MiningBot
    from bots.mining_bot.tiers import Tier

    bot = MiningBot(tier=Tier.PRO)
    bot.describe_tier()

    from bots.mining_bot.strategy import CoinProfile
    btc = CoinProfile("BTC", "SHA-256", 5e13, 3.125, 65000.0, 5e20, 1.0)
    rec = bot.recommend_strategy([btc])
    print(rec)
"""

from __future__ import annotations

from typing import Dict, List, Optional

from bots.mining_bot.tiers import (
    Tier,
    MiningTierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    FEATURE_ADAPTIVE_STRATEGY,
    FEATURE_SOLO_MINING,
    FEATURE_MERGED_MINING,
    FEATURE_POOL_MINING,
    FEATURE_FRAUD_DETECTION,
    FEATURE_HONEYPOT_DETECTION,
    FEATURE_CONTRACT_VERIFICATION,
    FEATURE_MULTI_EXCHANGE,
    FEATURE_DEX_ROUTING,
    FEATURE_HARDWARE_WALLET,
    FEATURE_BACKTESTING,
    FEATURE_REINFORCEMENT_LEARNING,
    FEATURE_AI_OPTIMISATION,
    FEATURE_SMART_ALERTS,
)
from bots.mining_bot.strategy import (
    AdaptiveStrategyEngine,
    CoinProfile,
    StrategyResult,
    StrategyType,
)
from bots.mining_bot.analytics import MiningSession, ProfitabilityAnalytics
from bots.mining_bot.monitor import Alert, MiningMonitor
from bots.mining_bot.fraud_detection import FraudCheckResult, FraudDetector
from bots.mining_bot.exchange import ExchangeQuote, MultiExchangeRouter


class MiningBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class MiningBot:
    """
    Tier-aware Mining Bot for the Dreamcobots platform.

    Parameters
    ----------
    tier : Tier
        Subscription tier (FREE / PRO / ENTERPRISE).
    hashrate_ths : float
        Miner hash rate in TH/s (default: 100).
    power_kw : float
        Miner power draw in kW (default: 3.5).
    electricity_rate : float
        Electricity cost in USD/kWh (default: 0.06).
    hardware_cost_usd : float
        Total hardware investment for ROI calculation (default: 0).
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        hashrate_ths: float = 100.0,
        power_kw: float = 3.5,
        electricity_rate: float = 0.06,
        hardware_cost_usd: float = 0.0,
    ):
        self.tier = tier
        self.config: MiningTierConfig = get_tier_config(tier)

        # --- Strategy engine -------------------------------------------
        available_strategies = []
        if self.config.has_feature(FEATURE_POOL_MINING):
            available_strategies.append(StrategyType.POOL)
        if self.config.has_feature(FEATURE_SOLO_MINING):
            available_strategies.append(StrategyType.SOLO)
        if self.config.has_feature(FEATURE_MERGED_MINING):
            available_strategies.append(StrategyType.MERGED)

        self._strategy_engine = AdaptiveStrategyEngine(
            hashrate_ths=hashrate_ths,
            power_kw=power_kw,
            electricity_rate=electricity_rate,
            available_strategies=available_strategies,
        )

        # --- Analytics -------------------------------------------------
        self._analytics = ProfitabilityAnalytics(
            depth=self.config.analytics_depth,
            hardware_cost_usd=hardware_cost_usd,
        )

        # --- Monitor ---------------------------------------------------
        self._monitor = MiningMonitor(
            alerts_enabled=self.config.alerts,
            expected_hashrate_ths=hashrate_ths,
            max_power_kw=power_kw * 1.1,
        )

        # --- Fraud detector --------------------------------------------
        self._fraud_detector = FraudDetector(
            enabled=self.config.fraud_detection,
        )

        # --- Exchange router -------------------------------------------
        self._exchange_router = MultiExchangeRouter(
            multi_exchange_enabled=self.config.multi_exchange,
            dex_routing_enabled=self.config.has_feature(FEATURE_DEX_ROUTING),
        )

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a human-readable description of the current tier."""
        cfg = self.config
        coins = "Unlimited" if cfg.monitored_coins == 0 else str(cfg.monitored_coins)
        strats = "Unlimited" if cfg.max_strategies == 0 else str(cfg.max_strategies)
        lines = [
            f"=== {cfg.name} Mining Tier ===",
            f"Price           : ${cfg.price_usd_monthly:.2f}/month",
            f"Monitored coins : {coins}",
            f"Max strategies  : {strats}",
            f"Analytics depth : {cfg.analytics_depth}",
            f"Support         : {cfg.support_level}",
            "",
            "Enabled features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg

        current_features = set(self.config.features)
        new_features = [f for f in next_cfg.features if f not in current_features]

        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features unlocked:",
        ]
        for feat in new_features:
            lines.append(f"  + {feat.replace('_', ' ').title()}")
        output = "\n".join(lines)
        print(output)
        return output

    @staticmethod
    def compare_tiers() -> str:
        """Print a comparison table of all tiers."""
        lines = ["=== Mining Bot Tier Comparison ===", ""]
        for cfg in list_tiers():
            coins = "Unlimited" if cfg.monitored_coins == 0 else str(cfg.monitored_coins)
            lines.append(
                f"{cfg.name:12s} ${cfg.price_usd_monthly:>7.2f}/mo  "
                f"Coins: {coins:9s}  "
                f"Analytics: {cfg.analytics_depth}"
            )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Strategy
    # ------------------------------------------------------------------

    def recommend_strategy(self, coins: List[CoinProfile]) -> Dict:
        """
        Adaptively recommend the best mining strategy across supplied coins.

        Requires FEATURE_ADAPTIVE_STRATEGY (PRO or ENTERPRISE).
        """
        if not self.config.has_feature(FEATURE_ADAPTIVE_STRATEGY):
            raise MiningBotTierError(
                "Adaptive strategy requires PRO or ENTERPRISE tier."
            )
        return self._strategy_engine.recommend(coins)

    def compare_strategies(self, coins: List[CoinProfile]) -> List[StrategyResult]:
        """Compare all available strategies across *coins*."""
        return self._strategy_engine.compare_strategies(coins)

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------

    def record_session(self, session: MiningSession) -> None:
        """Record a completed mining session into analytics."""
        self._analytics.record_session(session)

    def analytics_summary(self) -> Dict:
        """Return a profitability analytics summary for all recorded sessions."""
        return self._analytics.summary()

    def backtest(
        self,
        sessions: List[MiningSession],
    ) -> Dict:
        """
        Backtest mining performance over a historical list of sessions.

        Requires PRO or ENTERPRISE (FEATURE_BACKTESTING).
        """
        if not self.config.has_feature(FEATURE_BACKTESTING):
            raise MiningBotTierError("Backtesting requires PRO or ENTERPRISE tier.")

        from bots.mining_bot.analytics import ProfitabilityAnalytics

        bt = ProfitabilityAnalytics(
            depth=self.config.analytics_depth,
            hardware_cost_usd=self._analytics.hardware_cost_usd,
        )
        for s in sessions:
            bt.record_session(s)
        return bt.summary()

    # ------------------------------------------------------------------
    # Monitoring
    # ------------------------------------------------------------------

    def record_hashrate(self, hashrate_ths: float, power_kw: float) -> List[Alert]:
        """Record a live hash-rate reading and return any triggered alerts."""
        return self._monitor.record_hashrate(hashrate_ths, power_kw)

    def check_downtime(self) -> Optional[Alert]:
        """Check whether the miner appears to be offline."""
        return self._monitor.check_downtime()

    def all_alerts(self) -> List[Alert]:
        """Return all monitoring alerts emitted so far."""
        return self._monitor.all_alerts()

    # ------------------------------------------------------------------
    # Fraud detection
    # ------------------------------------------------------------------

    def check_contract(self, address: str) -> FraudCheckResult:
        """Verify a smart-contract address for scam indicators."""
        return self._fraud_detector.check_contract(address)

    def check_honeypot(self, address: str) -> FraudCheckResult:
        """Check whether an address exhibits honeypot characteristics."""
        return self._fraud_detector.check_honeypot(address)

    def check_pool(self, pool_url: str) -> FraudCheckResult:
        """Check whether a pool URL is associated with a known scam."""
        return self._fraud_detector.check_pool(pool_url)

    def run_fraud_checks(
        self,
        contract_address: Optional[str] = None,
        pool_url: Optional[str] = None,
    ) -> List[FraudCheckResult]:
        """Run all applicable fraud checks."""
        return self._fraud_detector.run_all_checks(
            contract_address=contract_address,
            pool_url=pool_url,
        )

    # ------------------------------------------------------------------
    # Exchange routing
    # ------------------------------------------------------------------

    def best_exchange(self, coin: str, amount: float) -> Optional[ExchangeQuote]:
        """Return the exchange offering the best net yield for *amount* of *coin*."""
        return self._exchange_router.best_exchange(coin, amount)

    def compare_exchanges(self, coin: str, amount: float) -> Dict:
        """Return a full exchange-comparison report."""
        return self._exchange_router.compare_exchanges(coin, amount)

    # ------------------------------------------------------------------
    # AI / RL optimisation (ENTERPRISE only)
    # ------------------------------------------------------------------

    def ai_optimise(self, coins: List[CoinProfile]) -> Dict:
        """
        Apply AI-driven optimisation to select the best strategy and
        energy settings.

        Requires ENTERPRISE tier (FEATURE_AI_OPTIMISATION).

        This implementation uses a lightweight reinforcement-learning
        inspired heuristic: it scores each strategy result by a composite
        of profitability and energy efficiency, then returns a ranked list.
        """
        if not self.config.has_feature(FEATURE_AI_OPTIMISATION):
            raise MiningBotTierError(
                "AI optimisation requires ENTERPRISE tier."
            )

        results = self._strategy_engine.compare_strategies(coins)
        daily_cost = self._strategy_engine.daily_energy_cost()

        scored = []
        for r in results:
            # Composite score: weight profit heavily, penalise energy waste
            if r.estimated_daily_revenue_usd > 0:
                energy_efficiency = r.net_profit_usd / max(daily_cost, 0.001)
            else:
                energy_efficiency = -1.0
            score = r.net_profit_usd * 0.7 + energy_efficiency * 0.3
            scored.append({"result": r, "ai_score": round(score, 6)})

        scored.sort(key=lambda x: x["ai_score"], reverse=True)

        recommendation = None
        reasoning = []
        if scored:
            best = scored[0]
            recommendation = best["result"]
            reasoning.append(
                f"AI recommends '{recommendation.strategy.value}' on "
                f"{recommendation.coin} with score {best['ai_score']:.4f}."
            )
            if not recommendation.is_profitable:
                reasoning.append(
                    "No strategy is currently profitable — consider halting "
                    "operations or reducing power consumption."
                )

        return {
            "recommendation": recommendation,
            "scored_results": scored,
            "reasoning": reasoning,
        }

    def reinforcement_learning_tune(
        self, historical_sessions: List[MiningSession]
    ) -> Dict:
        """
        Simulate a reinforcement-learning pass over historical sessions to
        derive improved strategy weights.

        Requires ENTERPRISE tier (FEATURE_REINFORCEMENT_LEARNING).

        Returns a dict containing derived policy weights and a performance
        improvement estimate.
        """
        if not self.config.has_feature(FEATURE_REINFORCEMENT_LEARNING):
            raise MiningBotTierError(
                "Reinforcement learning requires ENTERPRISE tier."
            )

        if not historical_sessions:
            return {"policy_weights": {}, "improvement_pct": 0.0, "episodes": 0}

        # Simulate a Q-learning update: compute per-strategy average rewards
        strategy_rewards: Dict[str, List[float]] = {}
        for session in historical_sessions:
            rewards = strategy_rewards.setdefault(session.strategy, [])
            rewards.append(session.net_profit_usd)

        import statistics

        policy_weights: Dict[str, float] = {}
        for strat, rewards in strategy_rewards.items():
            mean_reward = statistics.mean(rewards)
            policy_weights[strat] = round(max(mean_reward, 0.0), 6)

        # Normalise weights to sum to 1
        total = sum(policy_weights.values())
        if total > 0:
            policy_weights = {
                k: round(v / total, 6) for k, v in policy_weights.items()
            }

        # Estimate improvement as % gain over uniform policy
        n_strategies = max(len(policy_weights), 1)
        uniform_reward = (
            sum(
                statistics.mean(r)
                for r in strategy_rewards.values()
            )
            / n_strategies
        )
        best_weighted_reward = max(
            statistics.mean(strategy_rewards[s]) * policy_weights.get(s, 0)
            for s in strategy_rewards
        ) if strategy_rewards else 0.0

        improvement_pct = (
            (best_weighted_reward - uniform_reward) / abs(uniform_reward) * 100
            if uniform_reward != 0
            else 0.0
        )

        return {
            "policy_weights": policy_weights,
            "improvement_pct": round(improvement_pct, 4),
            "episodes": len(historical_sessions),
        }


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("Dreamcobots — Mining Bot\n")
    MiningBot.compare_tiers()
    print()

    for tier in Tier:
        bot = MiningBot(tier=tier)
        bot.describe_tier()
        bot.show_upgrade_path()
        print()
