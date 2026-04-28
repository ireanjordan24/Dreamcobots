"""
run_elite_scrapers.py — CLI runner for the Elite Scraper Bot system.

Invoked by the ``elite-scraper.yml`` GitHub Actions workflow.  Accepts an
optional ``--bots`` argument to run scrapers for a subset of bots; defaults
to all registered bot profiles.

Usage
-----
    python bots/elite_scraper/run_elite_scrapers.py
    python bots/elite_scraper/run_elite_scrapers.py --bots lead_gen_bot buddy_bot
    python bots/elite_scraper/run_elite_scrapers.py --bots all
"""

from __future__ import annotations

import argparse
import logging
import os
import sys

# Ensure repo root is on the path regardless of CWD
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if _REPO_ROOT not in sys.path:
    sys.path.insert(0, _REPO_ROOT)

from bots.elite_scraper import BOT_PROFILES, EliteScraper  # noqa: E402

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S",
)
_LOG = logging.getLogger("elite_scraper.runner")


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Elite Scraper Bots for all or selected DreamCo bots.")
    parser.add_argument(
        "--bots",
        nargs="*",
        default=["all"],
        help="Bot names to scrape (space-separated), or 'all' for every registered bot.",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum results per query per bot (default: 10).",
    )
    return parser.parse_args()


def main() -> int:
    args = _parse_args()

    # Determine which bots to run
    all_bots = [k for k in BOT_PROFILES if k != "_default"]
    if args.bots == ["all"] or "all" in args.bots:
        target_bots = all_bots
    else:
        target_bots = [b for b in args.bots if b in BOT_PROFILES]
        unknown = [b for b in args.bots if b not in BOT_PROFILES]
        if unknown:
            _LOG.warning("Unknown bot names (skipped): %s", unknown)

    if not target_bots:
        _LOG.error("No valid bots to scrape.  Exiting.")
        return 1

    _LOG.info("Running Elite Scrapers for %d bot(s): %s", len(target_bots), target_bots)

    github_token = os.environ.get("GITHUB_TOKEN")
    total_findings = 0
    failed: list[str] = []

    for bot_name in target_bots:
        try:
            scraper = EliteScraper.for_bot(
                bot_name,
                github_token=github_token,
                max_results_per_query=args.max_results,
            )
            result = scraper.run()
            print(result.summary())
            total_findings += result.total_findings()
        except Exception as exc:
            _LOG.error("Elite Scraper failed for %s: %s", bot_name, exc)
            failed.append(bot_name)

    print("\n" + "=" * 60)
    print(f"Elite Scraper run complete.")
    print(f"  Bots processed : {len(target_bots) - len(failed)} / {len(target_bots)}")
    print(f"  Total findings : {total_findings}")
    if failed:
        print(f"  Failed bots    : {failed}")
    print("=" * 60)

    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
