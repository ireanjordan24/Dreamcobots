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

# Generic module names that are used by multiple, unrelated bot packages.
# They get cached in sys.modules at *collection* time by whichever test module
# is collected first (e.g. test_211_bot.py imports `bot` at module level from
# bots/211-resource-eligibility-bot/).  Without resetting them, later tests
# that expect a *different* `bot` (e.g. test_saas_selling_bot.py) pick up the
# stale cached entry and fail with ImportError / AttributeError.
#
# Note: `database` is intentionally excluded so that the saas-selling-bot
# test suite's module-level ``import database as db`` reference stays valid.
# The ``fresh_db`` fixture patches ``db.DB_PATH`` on that cached module object;
# if we cleared and re-imported ``database``, the fixture would patch a stale
# object and Flask routes would connect to the wrong file.
_GENERIC_MODULE_NAMES = frozenset({"bot", "tiers", "nlp", "app"})


@pytest.fixture(scope="session", autouse=True)
def _reset_generic_module_cache():
    """Remove generic bot-package modules cached during collection.

    Some test files import modules like ``bot``, ``tiers``, or ``database``
    at module level so their symbols are available in the test namespace.
    This is fine for *those* tests, but the cached entry persists into the
    per-test ``_isolate_sys_modules`` snapshot baseline, causing unrelated
    test files that need the *same generic name* from a *different path* to
    receive the wrong module.

    Clearing the cache here (once, before the first test runs) ensures each
    test suite imports these modules fresh from whichever ``sys.path`` is
    active at that point.  The module-level symbol bindings in the test files
    that imported early (e.g. ``ResourceBot`` in test_211_bot.py) are
    unaffected because they were bound at collection time and do not depend on
    ``sys.modules`` staying populated.
    """
    for name in list(_GENERIC_MODULE_NAMES):
        sys.modules.pop(name, None)
    yield


@pytest.fixture(autouse=True)
def _isolate_sys_modules():
    """Snapshot and restore sys.modules and sys.path between tests.

    This prevents sys.modules cache pollution where a test file that inserts
    a bot directory into sys.path (e.g. bots/211-resource-eligibility-bot)
    causes its local tiers.py to be cached as sys.modules['tiers'], breaking
    downstream tests that expect a different tiers module.
    """
    modules_snapshot = dict(sys.modules)
    path_snapshot = list(sys.path)
    yield
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif sys.modules[key] is not modules_snapshot[key]:
            sys.modules[key] = modules_snapshot[key]
    sys.path[:] = path_snapshot
