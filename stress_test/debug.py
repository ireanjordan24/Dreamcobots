"""
stress_test/debug.py

Debug utilities for DreamCobots: diagnostics, import checks, health checks,
and system information printing.
"""

import importlib
import platform
import sys
from typing import Any


def debug_bot(bot_instance: Any) -> dict:
    """
    Run diagnostics on *bot_instance* and return a summary dict.

    Args:
        bot_instance: Any DreamCobots bot object.

    Returns:
        dict with keys: bot_id, bot_name, status, has_run, has_stop,
        activity_count, error_count.
    """
    status: dict[str, Any] = {}
    if hasattr(bot_instance, "get_status"):
        status = bot_instance.get_status()

    return {
        "bot_id": getattr(bot_instance, "bot_id", "unknown"),
        "bot_name": getattr(bot_instance, "bot_name", "unknown"),
        "status": status,
        "has_run": callable(getattr(bot_instance, "run", None)),
        "has_stop": callable(getattr(bot_instance, "stop", None)),
        "activity_count": len(getattr(bot_instance, "_activity_log", [])),
        "error_count": len(getattr(bot_instance, "_error_log", [])),
    }


def check_imports() -> dict:
    """
    Verify that all core DreamCobots modules can be imported.

    Returns:
        dict mapping module name -> True (success) or error message (str).
    """
    modules = [
        "core.orchestrator",
        "core.resource_monitor",
        "core.watchdog",
        "core.config_loader",
        "bots.bot_base",
        "bots.dataforge.dataforge_bot",
        "bots.dataforge.compliance",
        "bots.dataforge.marketplace",
        "bots.dataforge.user_marketplace",
        "bots.dataforge.sales_channels",
    ]

    results: dict[str, Any] = {}
    for mod in modules:
        try:
            importlib.import_module(mod)
            results[mod] = True
        except Exception as exc:  # pragma: no cover
            results[mod] = str(exc)
    return results


def run_health_checks() -> dict:
    """
    Run health checks on all major DreamCobots components.

    Returns:
        dict mapping component name -> "ok" or error message.
    """
    health: dict[str, str] = {}

    # Orchestrator
    try:
        from core.orchestrator import BotOrchestrator
        orch = BotOrchestrator()
        orch.get_all_statuses()
        health["orchestrator"] = "ok"
    except Exception as exc:  # pragma: no cover
        health["orchestrator"] = str(exc)

    # Resource monitor
    try:
        from core.resource_monitor import ResourceMonitor
        rm = ResourceMonitor(sample_interval_seconds=1)
        health["resource_monitor"] = "ok"
        del rm
    except Exception as exc:  # pragma: no cover
        health["resource_monitor"] = str(exc)

    # Compliance manager
    try:
        from bots.dataforge.compliance import ComplianceManager
        cm = ComplianceManager()
        cm.validate_gdpr_compliance({"consent_given": True, "purpose_of_processing": "test"})
        health["compliance_manager"] = "ok"
    except Exception as exc:  # pragma: no cover
        health["compliance_manager"] = str(exc)

    return health


def print_system_info() -> None:
    """Print Python version, platform, and available memory to stdout."""
    print(f"Python version : {sys.version}")
    print(f"Platform       : {platform.platform()}")
    print(f"Architecture   : {platform.machine()}")
    try:
        import psutil  # type: ignore[import-untyped]
        mem = psutil.virtual_memory()
        print(f"Total memory   : {mem.total / (1024 ** 3):.2f} GB")
        print(f"Available mem  : {mem.available / (1024 ** 3):.2f} GB")
        print(f"Memory usage   : {mem.percent:.1f}%")
    except ImportError:  # pragma: no cover
        print("Memory info    : psutil not available")
