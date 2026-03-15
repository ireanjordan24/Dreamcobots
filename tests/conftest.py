"""
Shared pytest configuration and fixtures for the DreamCobots test suite.

Ensures the repository root and tools/ directory are importable, and
provides test isolation by snapshotting and restoring sys.modules and
sys.path between tests to prevent cross-test module-cache pollution.
"""

import sys
import os
import pytest

# ---------------------------------------------------------------------------
# Session-level path setup
# ---------------------------------------------------------------------------
_REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
_TOOLS_DIR = os.path.join(_REPO_ROOT, "tools")

for _p in (_REPO_ROOT, _TOOLS_DIR):
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(autouse=True)
def _isolate_sys_modules():
    """
    Snapshot sys.modules and sys.path before each test, then restore them
    afterwards.  This prevents stale or wrong-path module objects from leaking
    between test files (e.g. the 'tiers' or 'bot' modules imported from
    different bots' sub-directories).
    """
    modules_snapshot = dict(sys.modules)
    path_snapshot = list(sys.path)

    yield

    # Remove any modules added during the test that are not in the snapshot
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif key in sys.modules and sys.modules[key] is not modules_snapshot[key]:
            # Restore the original module object if it was replaced
            sys.modules[key] = modules_snapshot[key]

    sys.path[:] = path_snapshot
