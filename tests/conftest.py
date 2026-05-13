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

# Repository sub-trees whose modules use short generic names (tiers, bot,
# database, config …) that can collide when different test files add their
# tool/bot directory to sys.path.  Any module whose __file__ lives inside
# one of these sub-trees is evicted from sys.modules before each test.
_REPO_ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
_TOOL_SUBDIRS: tuple = (
    "/bots/",
    "/automation-tools/",
    "/education-tools/",
    "/healthcare-tools/",
    "/analytics-elites/",
    "/real-estate-tools/",
    "/compliance-tools/",
    "/App_bots/",
    "/Business_bots/",
    "/Marketing_bots/",
    "/Fiverr_bots/",
    "/Occupational_bots/",
    "/Real_Estate_bots/",
    "/Side_Hustle_bots/",
    "/Government_Contract_bots/",
)


def _is_tool_local_module(mod) -> bool:
    """Return True if *mod* was loaded from a per-tool/bot sub-directory."""
    f = getattr(mod, "__file__", None)
    if not f:
        return False
    norm = f.replace("\\", "/")
    return any(sub in norm for sub in _TOOL_SUBDIRS) and norm.endswith(".py")


def _is_tool_local_path(p: str) -> bool:
    """Return True if *p* is a sys.path entry that points inside a tool/bot sub-tree."""
    norm = p.replace("\\", "/")
    return any(sub.strip("/") in norm for sub in _TOOL_SUBDIRS)


def _purge_tool_local_namespace_shadows():
    """Remove top-level tool/bot modules from ``sys.modules`` AND tool-local
    directories from ``sys.path`` that would shadow each other or repo-level
    packages when tests run in sequence.

    Called before each test's snapshot is taken so the snapshot reflects a
    clean state.
    """
    for name in list(sys.modules.keys()):
        if "." in name:
            continue
        mod = sys.modules.get(name)
        if mod is not None and _is_tool_local_module(mod):
            del sys.modules[name]

    # Also remove tool-local sys.path entries so the snapshot does not bake
    # them in for all subsequent tests.
    sys.path[:] = [p for p in sys.path if not _is_tool_local_path(p)]


@pytest.fixture(autouse=True)
def _isolate_sys_modules():
    """Snapshot and restore sys.modules and sys.path between tests.

    This prevents sys.modules cache pollution where a test file that inserts
    a tool/bot directory into sys.path causes its local modules (tiers.py,
    database.py, config.py, …) to be cached under short names that break
    downstream tests expecting a different module of the same name.
    """
    # Evict tool-local modules before taking the snapshot.
    _purge_tool_local_namespace_shadows()

    modules_snapshot = dict(sys.modules)
    path_snapshot = list(sys.path)
    yield
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif sys.modules[key] is not modules_snapshot[key]:
            sys.modules[key] = modules_snapshot[key]
    sys.path[:] = path_snapshot
