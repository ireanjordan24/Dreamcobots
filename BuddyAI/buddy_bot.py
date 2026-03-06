"""
buddy_bot.py – BuddyBot Main Orchestrator.

Wires all residual-income modules together and exposes a clean API for:
* Running the full income-tracking & reporting cycle
* Generating content on demand
* Performing market analysis
* Running the ML optimization engine

Usage (CLI)::

    python -m BuddyAI.buddy_bot --run-all

Usage (Python)::

    from BuddyAI.buddy_bot import BuddyBot
    bot = BuddyBot()
    bot.run_full_cycle()
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Any

from .config import ensure_output_dirs, load_config
from .content_automation import ContentAutomation
from .dashboard import Dashboard
from .event_bus import EventBus
from .income_tracker import IncomeTracker
from .market_analysis import MarketAnalysis
from .ml_optimizer import IncomePredictor, OptimizationEngine

logger = logging.getLogger(__name__)


def _setup_logging(level: str = "INFO") -> None:
    logging.basicConfig(
        level=getattr(logging, level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


class BuddyBot:
    """
    Central orchestrator for Dreamco's residual income automation system.

    All sub-modules communicate through the shared ``EventBus`` so they
    remain independently testable and replaceable.
    """

    def __init__(self, cfg: dict | None = None) -> None:
        self.cfg = cfg if cfg is not None else load_config()
        _setup_logging(self.cfg.get("log_level", "INFO"))
        ensure_output_dirs(self.cfg)

        self.bus = EventBus()
        self.income_tracker = IncomeTracker(self.cfg, self.bus)
        self.dashboard = Dashboard(self.cfg, self.bus)
        self.content_automation = ContentAutomation(self.cfg, self.bus)
        self.market_analysis = MarketAnalysis(self.cfg, self.bus)
        self.predictor = IncomePredictor(self.cfg)
        self.optimizer = OptimizationEngine(self.cfg, self.bus)

        logger.info(
            "%s initialised with %d income adapters.",
            self.cfg.get("buddy_bot_name", "BuddyBot"),
            len(self.income_tracker.adapters),
        )

    # ------------------------------------------------------------------
    # High-level workflows
    # ------------------------------------------------------------------

    def run_full_cycle(self) -> dict[str, Any]:
        """
        Execute the complete residual-income management cycle:

        1. Collect income data from all sources
        2. Generate the dashboard summary
        3. Train the ML predictor and forecast each stream
        4. Run market analysis
        5. Suggest new income streams
        6. Generate a batch of content
        7. Optimise the top opportunity

        Returns a dict with all results for programmatic consumption.
        """
        results: dict[str, Any] = {}

        print(f"\n{'#' * 60}")
        print(f"#  {self.cfg.get('buddy_bot_name', 'BuddyBot')} — Full Residual Income Cycle")
        print(f"{'#' * 60}\n")

        # ── Step 1: Income collection ──────────────────────────────────
        print("► Step 1/7  Collecting income data…")
        records = self.income_tracker.collect_all()
        summary = self.income_tracker.summarize(records)
        results["income_summary"] = summary

        # ── Step 2: Dashboard ─────────────────────────────────────────
        print("► Step 2/7  Rendering dashboard…")
        report_text = self.dashboard.render(records, summary, save=True)
        results["dashboard_report"] = report_text

        # ── Step 3: ML prediction ──────────────────────────────────────
        print("► Step 3/7  Training ML predictor & forecasting…")
        self.predictor.train(records)
        sources = [r.source for r in records]
        predictions = self.predictor.predict_all(sources, steps_ahead=30)
        results["predictions"] = [p.to_dict() for p in predictions]
        print("\n  Revenue Forecasts (30 days):")
        for p in predictions:
            print(
                f"    {p.source:<14} → ${p.predicted_revenue:>8,.2f}  "
                f"(×{p.growth_factor:.2f}, conf {p.confidence:.0%})"
            )

        # ── Step 4: Market analysis ───────────────────────────────────
        print("\n► Step 4/7  Running market analysis…")
        market_report = self.market_analysis.run_analysis()
        self.market_analysis.print_report(market_report)
        results["market_report"] = market_report.to_dict()

        # ── Step 5: New stream suggestions ────────────────────────────
        print("► Step 5/7  Suggesting new income streams…")
        suggestions = self.market_analysis.suggest_new_streams(market_report, top_k=3)
        results["stream_suggestions"] = suggestions
        for i, s in enumerate(suggestions, 1):
            print(
                f"    {i}. {s['topic']}  [{s['category']}]  "
                f"score={s['opportunity_score']:.1f}  "
                f"paths: {', '.join(s['monetization_paths'])}"
            )

        # ── Step 6: Content generation ────────────────────────────────
        print("\n► Step 6/7  Generating content batch…")
        top_niche = (
            market_report.top_trends[0].category
            if market_report.top_trends
            else None
        )
        blog_post = self.content_automation.generate_blog_post(niche=top_niche)
        ebook = self.content_automation.generate_ebook(niche=top_niche)
        saas_ideas = self.content_automation.suggest_saas_ideas(count=3)
        video = self.content_automation.generate_video_outline(niche=top_niche)
        results["content"] = {
            "blog_post": blog_post.to_dict(),
            "ebook": ebook.to_dict(),
            "saas_ideas": [i.to_dict() for i in saas_ideas],
            "video_outline": video.to_dict(),
        }
        print(f"    Blog post  : {blog_post.title}")
        print(f"    E-book     : {ebook.title}")
        print(f"    SaaS ideas : {', '.join(i.name for i in saas_ideas)}")
        print(f"    Video      : {video.title}")

        # ── Step 7: Optimization ──────────────────────────────────────
        print("\n► Step 7/7  Running optimization engine…")
        top_idea = (
            suggestions[0]["topic"] if suggestions else "AI Blog Network"
        )
        opt_result = self.optimizer.optimize(top_idea)
        scale_plan = self.optimizer.scale(opt_result)
        results["optimization"] = {
            "result": opt_result.to_dict(),
            "scale_plan": scale_plan,
        }
        print(f"    Idea       : {opt_result.idea}")
        print(f"    Score      : {opt_result.best_score:.4f} ({opt_result.status})")
        print(f"    Improvement: +{opt_result.improvement_pct:.1f}%")
        if scale_plan.get("next_steps"):
            print("    Next steps:")
            for step in scale_plan["next_steps"]:
                print(f"      • {step}")

        print(f"\n{'#' * 60}")
        print("#  Cycle complete.")
        print(f"{'#' * 60}\n")

        self.bus.publish("buddybot.cycle_complete", results)
        return results

    # ------------------------------------------------------------------
    # Individual module access (convenience wrappers)
    # ------------------------------------------------------------------

    def collect_income(self) -> dict:
        """Collect & summarise income; return the summary dict."""
        records = self.income_tracker.collect_all()
        return self.income_tracker.summarize(records)

    def generate_content(
        self, niche: str | None = None, content_type: str = "all"
    ) -> dict:
        """Generate content for a given niche and return results."""
        out: dict[str, Any] = {}
        if content_type in ("all", "blog"):
            out["blog_post"] = self.content_automation.generate_blog_post(niche).to_dict()
        if content_type in ("all", "ebook"):
            out["ebook"] = self.content_automation.generate_ebook(niche).to_dict()
        if content_type in ("all", "saas"):
            out["saas_ideas"] = [
                i.to_dict() for i in self.content_automation.suggest_saas_ideas()
            ]
        if content_type in ("all", "video"):
            out["video_outline"] = self.content_automation.generate_video_outline(niche).to_dict()
        return out

    def analyse_market(self) -> dict:
        """Run a market analysis and return the report dict."""
        report = self.market_analysis.run_analysis()
        self.market_analysis.print_report(report)
        return report.to_dict()

    def optimise(self, idea: str) -> dict:
        """Run the optimization engine for *idea* and return the scale plan."""
        result = self.optimizer.optimize(idea)
        return self.optimizer.scale(result)


# ── CLI entry point ────────────────────────────────────────────────────────


def _cli() -> None:
    parser = argparse.ArgumentParser(
        description="BuddyBot – Dreamco Residual Income Automation"
    )
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("run", help="Run the full automation cycle")
    sub.add_parser("income", help="Collect and display income data")
    sub.add_parser("market", help="Run market analysis")

    content_p = sub.add_parser("content", help="Generate content")
    content_p.add_argument("--niche", default=None, help="Content niche")
    content_p.add_argument(
        "--type",
        default="all",
        choices=["all", "blog", "ebook", "saas", "video"],
    )

    opt_p = sub.add_parser("optimise", help="Optimise an income idea")
    opt_p.add_argument("idea", help="Name of the idea to optimise")

    args = parser.parse_args()
    bot = BuddyBot()

    if args.command == "run" or args.command is None:
        bot.run_full_cycle()
    elif args.command == "income":
        summary = bot.collect_income()
        bot.dashboard.print_summary(summary)
    elif args.command == "market":
        bot.analyse_market()
    elif args.command == "content":
        bot.generate_content(niche=getattr(args, "niche", None),
                             content_type=getattr(args, "type", "all"))
    elif args.command == "optimise":
        plan = bot.optimise(args.idea)
        print(plan)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    _cli()
