"""
main.py

DreamCobots main entry point.

Initialises all bots, starts the orchestrator, and provides a simple CLI
interface for interacting with the running system.  Handles SIGINT/SIGTERM
for graceful shutdown.
"""

import argparse
import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime, timezone
from typing import Any


# ---------------------------------------------------------------------------
# Logging setup
# ---------------------------------------------------------------------------

def _configure_root_logger(level: str = "INFO") -> None:
    logging.basicConfig(
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
        level=getattr(logging, level.upper(), logging.INFO),
        stream=sys.stdout,
    )


logger = logging.getLogger("DreamCobots.Main")


# ---------------------------------------------------------------------------
# Graceful shutdown helper
# ---------------------------------------------------------------------------

_shutdown_event: threading.Event = threading.Event()


def _handle_signal(signum: int, frame: Any) -> None:
    """Handle SIGINT / SIGTERM by setting the shutdown event."""
    logger.info("Signal %d received. Initiating graceful shutdown…", signum)
    _shutdown_event.set()


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------

def cmd_run(args: argparse.Namespace) -> None:
    """Start the orchestrator and all registered bots."""
    from core.orchestrator import BotOrchestrator
    from core.resource_monitor import ResourceMonitor
    from core.watchdog import Watchdog
    from core.config_loader import ConfigLoader
    from bots.government_contract_grant_bot_wrapper import build_default_bots

    _configure_root_logger(args.log_level)

    # Load project-wide config
    config_path = args.config or os.path.join(
        os.path.dirname(__file__), "bots", "config.json"
    )
    loader = ConfigLoader()
    try:
        config = loader.load(config_path)
    except Exception as exc:
        logger.warning("Could not load config from %s: %s. Using defaults.", config_path, exc)
        config = {}

    logger.info("DreamCobots starting up. Config keys: %s", list(config.keys()))

    # Build components
    orchestrator = BotOrchestrator()
    resource_monitor = ResourceMonitor(sample_interval_seconds=args.monitor_interval)
    watchdog = Watchdog(check_interval_seconds=args.watchdog_interval)

    # Register a default alert handler
    def _alert_handler(alert: dict[str, Any]) -> None:
        logger.warning("Resource alert: %s", alert)

    resource_monitor.register_alert_callback(_alert_handler)

    # Build and register bots
    bots = build_default_bots(config)
    for bot in bots:
        orchestrator.register_bot(bot)

    # Install signal handlers
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)

    # Start everything
    resource_monitor.start()
    orchestrator.start_router()
    orchestrator.start_all()

    logger.info(
        "DreamCobots running. %d bot(s) active. Press Ctrl-C to stop.",
        len(bots),
    )

    # Block until shutdown signal
    _shutdown_event.wait()

    logger.info("Shutting down…")
    orchestrator.stop_all()
    resource_monitor.stop()
    watchdog.stop()

    # Dump final collected data if requested
    if args.dump_data:
        data = orchestrator.collect_all_data()
        output_path = args.dump_data
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(data, fh, indent=2, default=str)
        logger.info("Structured data written to %s", output_path)

    logger.info("DreamCobots stopped cleanly.")


def cmd_status(args: argparse.Namespace) -> None:
    """Print current status of all bots (requires a running orchestrator API)."""
    _configure_root_logger(args.log_level)
    from core.orchestrator import BotOrchestrator
    from bots.government_contract_grant_bot_wrapper import build_default_bots

    orchestrator = BotOrchestrator()
    bots = build_default_bots({})
    for bot in bots:
        orchestrator.register_bot(bot)

    statuses = orchestrator.get_all_statuses()
    print(json.dumps(statuses, indent=2, default=str))


def cmd_collect(args: argparse.Namespace) -> None:
    """Run bots for one cycle and dump collected data to stdout or a file."""
    _configure_root_logger(args.log_level)
    from core.orchestrator import BotOrchestrator
    from bots.government_contract_grant_bot_wrapper import build_default_bots

    orchestrator = BotOrchestrator()
    bots = build_default_bots({})
    for bot in bots:
        orchestrator.register_bot(bot)
        # Run one cycle directly (no thread) so data is populated synchronously
        try:
            bot.process_contracts()  # type: ignore[attr-defined]
            bot.process_grants()     # type: ignore[attr-defined]
        except AttributeError:
            pass

    data = orchestrator.collect_all_data()
    output = json.dumps(data, indent=2, default=str)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(output)
        logger.info("Data written to %s", args.output)
    else:
        print(output)


# ---------------------------------------------------------------------------
# Argument parser
# ---------------------------------------------------------------------------

def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="dreamcobots",
        description="DreamCobots – Autonomous Bot Platform",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # run
    run_parser = subparsers.add_parser("run", help="Start the orchestrator and all bots.")
    run_parser.add_argument(
        "--config", default=None, help="Path to config.json (default: bots/config.json)"
    )
    run_parser.add_argument(
        "--monitor-interval",
        type=int,
        default=30,
        help="Resource monitor sample interval in seconds (default: 30)",
    )
    run_parser.add_argument(
        "--watchdog-interval",
        type=int,
        default=60,
        help="Watchdog check interval in seconds (default: 60)",
    )
    run_parser.add_argument(
        "--dump-data",
        default=None,
        metavar="FILE",
        help="Write collected bot data to FILE on shutdown.",
    )
    run_parser.set_defaults(func=cmd_run)

    # status
    status_parser = subparsers.add_parser("status", help="Print bot status.")
    status_parser.set_defaults(func=cmd_status)

    # collect
    collect_parser = subparsers.add_parser(
        "collect", help="Run one data-collection cycle and print results."
    )
    collect_parser.add_argument(
        "--output", default=None, metavar="FILE", help="Write output to FILE instead of stdout."
    )
    collect_parser.set_defaults(func=cmd_collect)

    return parser


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main(argv: list[str] | None = None) -> int:
    """
    Main entry point for the DreamCobots CLI.

    Args:
        argv: Command-line arguments (defaults to ``sys.argv[1:]``).

    Returns:
        Exit code (0 for success, non-zero for error).
    """
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
        return 0
    except KeyboardInterrupt:
        return 0
    except Exception as exc:
        logging.getLogger("DreamCobots.Main").exception("Fatal error: %s", exc)
        return 1


if __name__ == "__main__":
    sys.exit(main())
