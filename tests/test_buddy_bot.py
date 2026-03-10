"""
Tests for BuddyAI/event_bus.py and BuddyAI/buddy_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from BuddyAI.event_bus import EventBus, EventBusError
from BuddyAI.buddy_bot import BuddyBot, BuddyBotError


# -----------------------------------------------------------------------
# EventBus tests
# -----------------------------------------------------------------------

class TestEventBus:
    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe("test.event", lambda p: received.append(p))
        count = bus.publish("test.event", "hello")
        assert count == 1
        assert received == ["hello"]

    def test_multiple_subscribers(self):
        bus = EventBus()
        results = []
        bus.subscribe("evt", lambda p: results.append(("h1", p)))
        bus.subscribe("evt", lambda p: results.append(("h2", p)))
        count = bus.publish("evt", 42)
        assert count == 2
        assert len(results) == 2

    def test_publish_no_subscribers_returns_zero(self):
        bus = EventBus()
        count = bus.publish("unknown.event", None)
        assert count == 0

    def test_unsubscribe_stops_delivery(self):
        bus = EventBus()
        received = []

        def handler(p):
            received.append(p)

        bus.subscribe("evt", handler)
        bus.publish("evt", "first")
        bus.unsubscribe("evt", handler)
        bus.publish("evt", "second")
        assert received == ["first"]

    def test_unsubscribe_nonexistent_raises(self):
        bus = EventBus()
        # unsubscribing a non-existent event is a no-op (does not raise)
        bus.unsubscribe("no.such.event", lambda p: None)

    def test_event_log_populated(self):
        bus = EventBus()
        bus.publish("my.event", {"key": "value"})
        log = bus.get_event_log()
        assert len(log) == 1
        assert log[0]["event_type"] == "my.event"
        assert log[0]["payload"] == {"key": "value"}

    def test_get_event_log_returns_copy(self):
        bus = EventBus()
        bus.publish("evt", None)
        log = bus.get_event_log()
        log.append({"injected": True})
        assert len(bus.get_event_log()) == 1

    def test_clear_log(self):
        bus = EventBus()
        bus.publish("evt", None)
        bus.clear_log()
        assert bus.get_event_log() == []

    def test_list_event_types_empty(self):
        bus = EventBus()
        assert bus.list_event_types() == []

    def test_list_event_types_populated(self):
        bus = EventBus()
        bus.subscribe("alpha", lambda p: None)
        bus.subscribe("beta", lambda p: None)
        types = bus.list_event_types()
        assert "alpha" in types
        assert "beta" in types

    def test_publish_payload_none(self):
        bus = EventBus()
        received = []
        bus.subscribe("null.evt", lambda p: received.append(p))
        bus.publish("null.evt")
        assert received == [None]


# -----------------------------------------------------------------------
# BuddyBot tests
# -----------------------------------------------------------------------

class _MockBot:
    """Minimal mock bot with a process() method."""
    def __init__(self, response="mock response"):
        self._response = response
        self._calls = []

    def process(self, message: str, **kwargs) -> dict:
        self._calls.append(message)
        return {"message": self._response, "input": message}


class _BotWithoutProcess:
    """Bot that does not implement process()."""
    pass


class TestBuddyBot:
    def test_default_tier_is_free(self):
        hub = BuddyBot()
        assert hub.tier == Tier.FREE

    def test_register_bot(self):
        hub = BuddyBot()
        hub.register_bot("chat", _MockBot())
        assert "chat" in hub.list_bots()

    def test_register_duplicate_raises(self):
        hub = BuddyBot()
        hub.register_bot("chat", _MockBot())
        with pytest.raises(BuddyBotError):
            hub.register_bot("chat", _MockBot())

    def test_unregister_bot(self):
        hub = BuddyBot()
        hub.register_bot("chat", _MockBot())
        hub.unregister_bot("chat")
        assert "chat" not in hub.list_bots()

    def test_unregister_nonexistent_raises(self):
        hub = BuddyBot()
        with pytest.raises(BuddyBotError):
            hub.unregister_bot("no.such.bot")

    def test_get_bot(self):
        hub = BuddyBot()
        mock = _MockBot()
        hub.register_bot("my_bot", mock)
        assert hub.get_bot("my_bot") is mock

    def test_get_bot_not_found_raises(self):
        hub = BuddyBot()
        with pytest.raises(BuddyBotError):
            hub.get_bot("missing")

    def test_list_bots_sorted(self):
        hub = BuddyBot()
        hub.register_bot("zebra", _MockBot())
        hub.register_bot("apple", _MockBot())
        assert hub.list_bots() == ["apple", "zebra"]

    def test_list_bots_empty(self):
        hub = BuddyBot()
        assert hub.list_bots() == []

    def test_route_message(self):
        hub = BuddyBot()
        hub.register_bot("echo", _MockBot("pong"))
        result = hub.route_message("echo", "ping")
        assert isinstance(result, dict)
        assert result["message"] == "pong"

    def test_route_message_unknown_bot_raises(self):
        hub = BuddyBot()
        with pytest.raises(BuddyBotError):
            hub.route_message("ghost", "hello")

    def test_route_message_no_process_raises(self):
        hub = BuddyBot()
        hub.register_bot("no_proc", _BotWithoutProcess())
        with pytest.raises(BuddyBotError):
            hub.route_message("no_proc", "hello")

    def test_route_publishes_event(self):
        hub = BuddyBot()
        hub.register_bot("bot", _MockBot())
        events = []
        hub.event_bus.subscribe("message.routed", lambda p: events.append(p))
        hub.route_message("bot", "test msg")
        assert len(events) == 1
        assert events[0]["bot_name"] == "bot"

    def test_event_bus_property_returns_event_bus(self):
        hub = BuddyBot()
        assert isinstance(hub.event_bus, EventBus)

    def test_describe_tier_returns_string(self):
        hub = BuddyBot(Tier.FREE)
        output = hub.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_describe_tier_pro(self):
        hub = BuddyBot(Tier.PRO)
        output = hub.describe_tier()
        assert "Pro" in output
        assert "$49.00" in output

    def test_show_upgrade_path_from_free(self):
        hub = BuddyBot(Tier.FREE)
        output = hub.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise_no_upgrade(self):
        hub = BuddyBot(Tier.ENTERPRISE)
        output = hub.show_upgrade_path()
        assert "top-tier" in output

    def test_register_event_fires_on_register(self):
        hub = BuddyBot()
        events = []
        hub.event_bus.subscribe("bot.registered", lambda p: events.append(p))
        hub.register_bot("bot1", _MockBot())
        assert len(events) == 1
        assert events[0]["name"] == "bot1"

    def test_unregister_event_fires_on_unregister(self):
        hub = BuddyBot()
        events = []
        hub.event_bus.subscribe("bot.unregistered", lambda p: events.append(p))
        hub.register_bot("bot2", _MockBot())
        hub.unregister_bot("bot2")
        assert len(events) == 1
        assert events[0]["name"] == "bot2"
