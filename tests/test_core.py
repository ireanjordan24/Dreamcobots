"""
tests/test_core.py

Tests for core module: watchdog, resource_monitor, orchestrator, config_loader.
"""

import json
import os
import tempfile
import threading
import time
import unittest

from bots.bot_base import BotBase
from core.orchestrator import BotOrchestrator
from core.config_loader import ConfigLoader
from core.watchdog import Watchdog
from core.resource_monitor import ResourceMonitor
from core.base_bot import BaseBotCore


# ---------------------------------------------------------------------------
# Minimal concrete BotBase for orchestrator tests
# ---------------------------------------------------------------------------

class _TestBot(BotBase):
    def __init__(self, bot_id: str = "test-001") -> None:
        super().__init__(bot_name="TestBot", bot_id=bot_id)
        self._stop_event = threading.Event()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = __import__("datetime").datetime.now(
            __import__("datetime").timezone.utc
        )
        self._stop_event.wait(timeout=0.1)
        self._set_running(False)

    def stop(self) -> None:
        self._set_running(False)
        self._stop_event.set()


# ---------------------------------------------------------------------------
# Minimal concrete BaseBotCore for watchdog tests
# ---------------------------------------------------------------------------

class _CoreTestBot(BaseBotCore):
    def __init__(self, name: str = "CoreTestBot") -> None:
        super().__init__(name=name)

    def initialize(self) -> None:
        pass

    def start(self) -> None:
        pass

    def stop(self) -> None:
        pass


# ---------------------------------------------------------------------------
# Orchestrator tests
# ---------------------------------------------------------------------------

class TestBotOrchestrator(unittest.TestCase):
    def setUp(self) -> None:
        self.orch = BotOrchestrator()
        self.bot = _TestBot("orch-test-001")

    def test_register_bot(self) -> None:
        self.orch.register_bot(self.bot)
        statuses = self.orch.get_all_statuses()
        self.assertIn("orch-test-001", statuses["bots"])

    def test_double_register_is_noop(self) -> None:
        self.orch.register_bot(self.bot)
        self.orch.register_bot(self.bot)  # should not raise
        statuses = self.orch.get_all_statuses()
        self.assertEqual(1, sum(1 for k in statuses["bots"] if k == "orch-test-001"))

    def test_unregister_bot(self) -> None:
        self.orch.register_bot(self.bot)
        self.orch.unregister_bot("orch-test-001")
        statuses = self.orch.get_all_statuses()
        self.assertNotIn("orch-test-001", statuses["bots"])

    def test_start_unknown_raises(self) -> None:
        with self.assertRaises(KeyError):
            self.orch.start_bot("nonexistent")

    def test_start_and_stop_bot(self) -> None:
        self.orch.register_bot(self.bot)
        self.orch.start_bot("orch-test-001")
        self.orch.stop_bot("orch-test-001")

    def test_start_all_stop_all(self) -> None:
        bot2 = _TestBot("orch-test-002")
        self.orch.register_bot(self.bot)
        self.orch.register_bot(bot2)
        self.orch.start_all()
        self.orch.stop_all()

    def test_send_message(self) -> None:
        self.orch.register_bot(self.bot)
        self.orch.send_message("orchestrator", "orch-test-001", "ping", {"data": 1})
        msgs = self.orch.receive_messages("orch-test-001")
        self.assertEqual(1, len(msgs))
        self.assertEqual("ping", msgs[0]["topic"])

    def test_send_to_unknown_raises(self) -> None:
        with self.assertRaises(KeyError):
            self.orch.send_message("a", "unknown-recipient", "topic")

    def test_receive_empty(self) -> None:
        self.orch.register_bot(self.bot)
        msgs = self.orch.receive_messages("orch-test-001")
        self.assertEqual([], msgs)

    def test_collect_all_data(self) -> None:
        self.orch.register_bot(self.bot)
        data = self.orch.collect_all_data()
        self.assertIn("bots", data)
        self.assertIn("orch-test-001", data["bots"])

    def test_get_message_history(self) -> None:
        self.orch.register_bot(self.bot)
        self.orch.send_message("orchestrator", "orch-test-001", "test")
        history = self.orch.get_message_history()
        self.assertGreater(len(history), 0)

    def test_router_start_stop(self) -> None:
        self.orch.start_router()
        self.assertTrue(self.orch._router_thread.is_alive())
        self.orch.stop_router()


# ---------------------------------------------------------------------------
# Config loader tests
# ---------------------------------------------------------------------------

class TestConfigLoader(unittest.TestCase):
    def test_load_valid_json(self) -> None:
        cfg = {"name": "test", "version": 1}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(cfg, f)
            path = f.name
        try:
            loader = ConfigLoader()
            loaded = loader.load(path)
            self.assertEqual("test", loaded["name"])
        finally:
            os.unlink(path)

    def test_get_with_default(self) -> None:
        cfg = {"a": 1}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(cfg, f)
            path = f.name
        try:
            loader = ConfigLoader()
            loaded = loader.load(path)
            self.assertEqual(42, loader.get(loaded, "b", 42))
            self.assertEqual(1, loader.get(loaded, "a"))
        finally:
            os.unlink(path)

    def test_missing_file_raises(self) -> None:
        loader = ConfigLoader()
        with self.assertRaises((FileNotFoundError, Exception)):
            loader.load("/nonexistent/path/config.json")

    def test_load_from_dict(self) -> None:
        loader = ConfigLoader()
        loaded = loader.load_from_dict({"x": 42})
        self.assertEqual(42, loaded["x"])

    def test_env_override(self) -> None:
        cfg = {"key": "original"}
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            json.dump(cfg, f)
            path = f.name
        try:
            os.environ["DREAMCOBOTS_KEY"] = "overridden"
            loader = ConfigLoader()
            loaded = loader.load(path)
            self.assertIsNotNone(loaded)
        finally:
            os.unlink(path)
            os.environ.pop("DREAMCOBOTS_KEY", None)


# ---------------------------------------------------------------------------
# Watchdog tests
# ---------------------------------------------------------------------------

class TestWatchdog(unittest.TestCase):
    def test_init(self) -> None:
        wd = Watchdog(check_interval_seconds=1, max_restarts=3)
        self.assertEqual(1, wd.check_interval_seconds)
        self.assertEqual(3, wd.max_restarts)

    def test_register_and_unregister(self) -> None:
        wd = Watchdog(check_interval_seconds=1)
        bot = _CoreTestBot("wd-test-bot")
        wd.register_bot("wd-001", bot)
        wd.unregister_bot("wd-001")

    def test_start_stop(self) -> None:
        wd = Watchdog(check_interval_seconds=1)
        wd.start()
        time.sleep(0.1)
        wd.stop()

    def test_get_health_report(self) -> None:
        wd = Watchdog(check_interval_seconds=1)
        report = wd.get_bot_health_report()
        self.assertIsInstance(report, dict)


# ---------------------------------------------------------------------------
# Resource monitor tests
# ---------------------------------------------------------------------------

class TestResourceMonitor(unittest.TestCase):
    def test_sample(self) -> None:
        rm = ResourceMonitor()
        snap = rm.sample()
        self.assertIn("cpu", snap)
        self.assertIn("memory", snap)

    def test_start_stop(self) -> None:
        rm = ResourceMonitor(sample_interval_seconds=1)
        rm.start()
        time.sleep(0.2)
        rm.stop()

    def test_get_latest_snapshot(self) -> None:
        rm = ResourceMonitor(sample_interval_seconds=1)
        rm.start()
        time.sleep(1.5)
        latest = rm.get_latest_snapshot()
        self.assertIsNotNone(latest)
        rm.stop()

    def test_generate_report(self) -> None:
        rm = ResourceMonitor(sample_interval_seconds=1)
        report = rm.generate_report()
        self.assertIsInstance(report, dict)

    def test_register_alert_callback(self) -> None:
        alerts: list = []
        rm = ResourceMonitor(
            sample_interval_seconds=1,
            cpu_threshold=0.0,  # triggers on any CPU usage
        )
        rm.register_alert_callback(lambda resource, value, threshold: alerts.append(resource))
        rm.start()
        time.sleep(1.5)
        rm.stop()
        # Alerts may or may not fire — just ensure no crash


if __name__ == "__main__":
    unittest.main()
