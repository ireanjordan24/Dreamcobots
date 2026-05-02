"""
Pytest configuration and shared fixtures for the DreamCobots test suite.
"""

import os
import sys
import pytest

# Ensure tools/ is on sys.path so tests can import check_bot_framework
# directly without relying on a prior test having inserted the path.
_TOOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

# ---------------------------------------------------------------------------
# Modules that are known to collide between test files (same name, different
# path).  Any module in this set is proactively cleared before each test that
# belongs to a file that needs a "fresh" import of that module.
# ---------------------------------------------------------------------------
_SAAS_BOT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "bots", "saas-selling-bot")
)
_ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


@pytest.fixture(autouse=True)
def _isolate_sys_modules(request):
    """Snapshot and restore sys.modules and sys.path between tests.

    This prevents sys.modules cache pollution where a test file that inserts
    a bot directory into sys.path (e.g. bots/211-resource-eligibility-bot)
    causes its local tiers.py to be cached as sys.modules['tiers'], breaking
    downstream tests that expect a different tiers module.

    Additionally, for tests that rely on specific modules (e.g. the saas-
    selling-bot's ``bot`` module or the root ``config`` package), we clear
    the stale cached copy before taking the snapshot so the correct module
    is loaded on demand.
    """
    testfile = str(request.node.fspath.basename)

    # ------------------------------------------------------------------
    # Pre-snapshot clean-up: remove known collision modules so the
    # correct version is imported when the test actually runs.
    # ------------------------------------------------------------------

    # The saas-selling-bot test file needs its own ``bot`` module,
    # not the one cached from bots/211-resource-eligibility-bot.
    if testfile in ("test_saas_selling_bot.py",):
        sys.modules.pop("bot", None)
        # Ensure saas-selling-bot dir is first on sys.path for this test
        if _SAAS_BOT_DIR not in sys.path:
            sys.path.insert(0, _SAAS_BOT_DIR)
        elif sys.path[0] != _SAAS_BOT_DIR:
            sys.path.remove(_SAAS_BOT_DIR)
            sys.path.insert(0, _SAAS_BOT_DIR)

    # The root ``config/`` package must not be shadowed by the 211-bot's
    # flat config.py module for test files that use config.settings.
    if testfile in ("test_core_system.py",):
        cached_config = sys.modules.get("config")
        if cached_config is not None and not hasattr(cached_config, "settings"):
            sys.modules.pop("config", None)
        # Ensure repo root is FIRST on sys.path so the config/ package takes
        # precedence over any bot directory that contains a flat config.py.
        if _ROOT_DIR in sys.path:
            sys.path.remove(_ROOT_DIR)
        sys.path.insert(0, _ROOT_DIR)

    modules_snapshot = dict(sys.modules)
    path_snapshot = list(sys.path)
    yield
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif sys.modules[key] is not modules_snapshot[key]:
            sys.modules[key] = modules_snapshot[key]
    sys.path[:] = path_snapshot
