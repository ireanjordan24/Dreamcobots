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


def _is_bot_local_shadow(mod_name: str, mod) -> bool:
    """Return True if *mod* was loaded from inside a ``bots/`` subdirectory.

    These modules use short, generic names (``bot``, ``tiers``, ``database``,
    ``config``, etc.) that can collide across different bot directories.
    Evicting them before each test ensures that each test file gets fresh
    imports from the correct bot directory, preventing cross-test pollution.
    """
    f = getattr(mod, "__file__", None)
    if not f:
        return False
    norm = f.replace("\\", "/")
    return "/bots/" in norm and norm.endswith(".py")


def _purge_bot_local_namespace_shadows():
    """Remove bot-local top-level modules from ``sys.modules``.

    Called before each test's snapshot is taken so the snapshot reflects a
    clean state.  Already-initialised module objects (and any names imported
    from them at module level in test files) remain valid in memory; removing
    the cache entry only prevents stale modules from being returned on the
    next ``import`` statement.
    """
    for name in list(sys.modules.keys()):
        if "." in name:
            continue
        mod = sys.modules.get(name)
        if mod is not None and _is_bot_local_shadow(name, mod):
            del sys.modules[name]


@pytest.fixture(autouse=True)
def _isolate_sys_modules():
    """Snapshot and restore sys.modules and sys.path between tests.

    This prevents sys.modules cache pollution where a test file that inserts
    a bot directory into sys.path (e.g. bots/211-resource-eligibility-bot)
    causes its local tiers.py to be cached as sys.modules['tiers'], breaking
    downstream tests that expect a different tiers module.
    """
    # Purge bot-local modules that shadow repo-level packages (e.g. config)
    # before taking the snapshot so the snapshot is clean.
    _purge_bot_local_namespace_shadows()

    modules_snapshot = dict(sys.modules)
    path_snapshot = list(sys.path)
    yield
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif sys.modules[key] is not modules_snapshot[key]:
            sys.modules[key] = modules_snapshot[key]
    sys.path[:] = path_snapshot
