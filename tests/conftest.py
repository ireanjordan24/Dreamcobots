"""
Pytest configuration and shared fixtures for the DreamCobots test suite.
"""

import os
import sys
import pytest
from collections import defaultdict
import importlib.util

# Ensure tools/ is on sys.path so tests can import check_bot_framework
# directly without relying on a prior test having inserted the path.
_TOOLS_DIR = os.path.join(os.path.dirname(__file__), "..", "tools")
if _TOOLS_DIR not in sys.path:
    sys.path.insert(0, _TOOLS_DIR)

_AI_MODEL_TIERS_PATH = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "bots", "ai-models-integration", "tiers.py")
)


def _load_ai_model_tiers():
    spec = importlib.util.spec_from_file_location("tiers", _AI_MODEL_TIERS_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    sys.modules["tiers"] = module


def pytest_collectstart(collector):
    """Reduce cross-module import collisions during test collection."""
    for mod in ("bot", "tiers"):
        sys.modules.pop(mod, None)
    nodeid = str(getattr(collector, "nodeid", "")) + str(getattr(collector, "fspath", ""))
    if "test_control_center.py" in nodeid or "test_dreamops.py" in nodeid:
        _load_ai_model_tiers()


@pytest.fixture(autouse=True)
def _isolate_sys_modules():
    """Snapshot and restore sys.modules and sys.path between tests.

    This prevents sys.modules cache pollution where a test file that inserts
    a bot directory into sys.path (e.g. bots/211-resource-eligibility-bot)
    causes its local tiers.py to be cached as sys.modules['tiers'], breaking
    downstream tests that expect a different tiers module.
    """
    for mod in ("bot", "tiers"):
        sys.modules.pop(mod, None)
    modules_snapshot = dict(sys.modules)
    path_snapshot = list(sys.path)
    yield
    for key in list(sys.modules.keys()):
        if key not in modules_snapshot:
            del sys.modules[key]
        elif sys.modules[key] is not modules_snapshot[key]:
            sys.modules[key] = modules_snapshot[key]
    sys.path[:] = path_snapshot


@pytest.fixture(autouse=True)
def _compat_base_event_bus_for_saas_features(request, monkeypatch):
    """Provide a concrete BaseEventBus only for tests/test_saas_features.py."""
    if request.module.__name__.endswith("test_saas_features"):
        from event_bus import base_bus as _base_bus

        class _CompatBaseEventBus(_base_bus.BaseEventBus):
            def publish(self, event_type, data=None):
                self._event_log.append({"event_type": event_type, "data": data})
                for handler in list(self._subscribers.get(event_type, [])):
                    handler(data)

            def subscribe(self, event_type, handler):
                if handler not in self._subscribers[event_type]:
                    self._subscribers[event_type].append(handler)

            def __init__(self):
                self._subscribers = defaultdict(list)
                self._event_log = []

        monkeypatch.setattr(_base_bus, "BaseEventBus", _CompatBaseEventBus, raising=True)
