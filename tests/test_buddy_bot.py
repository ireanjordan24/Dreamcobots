"""
Tests for BuddyAI/event_bus.py and BuddyAI/buddy_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from BuddyAI.event_bus import EventBus
from BuddyAI.buddy_bot import BuddyBot, BuddyBotError
from tiers import Tier
from bots.ai_chatbot.chatbot import Chatbot


# ---------------------------------------------------------------------------
# EventBus tests
# ---------------------------------------------------------------------------

class TestEventBus:
    def test_subscribe_and_publish(self):
        bus = EventBus()
        received = []
        bus.subscribe("test_event", lambda d: received.append(d))
        bus.publish("test_event", {"value": 42})
        assert received == [{"value": 42}]

    def test_publish_returns_handler_count(self):
        bus = EventBus()
        bus.subscribe("ev", lambda d: None)
        bus.subscribe("ev", lambda d: None)
        count = bus.publish("ev", {})
        assert count == 2

    def test_publish_with_no_subscribers_returns_zero(self):
        bus = EventBus()
        assert bus.publish("nonexistent") == 0

    def test_unsubscribe_removes_handler(self):
        bus = EventBus()
        calls = []
        handler = lambda d: calls.append(d)
        bus.subscribe("ev", handler)
        bus.unsubscribe("ev", handler)
        bus.publish("ev", "data")
        assert calls == []

    def test_unsubscribe_noop_if_not_registered(self):
        bus = EventBus()
        bus.unsubscribe("ev", lambda d: None)  # should not raise

    def test_duplicate_subscribe_registers_once(self):
        bus = EventBus()
        calls = []
        h = lambda d: calls.append(d)
        bus.subscribe("ev", h)
        bus.subscribe("ev", h)
        bus.publish("ev", 1)
        assert calls == [1]

    def test_clear_removes_event_handlers(self):
        bus = EventBus()
        calls = []
        bus.subscribe("ev", lambda d: calls.append(d))
        bus.clear("ev")
        bus.publish("ev", "x")
        assert calls == []

    def test_clear_all_removes_all_handlers(self):
        bus = EventBus()
        calls = []
        bus.subscribe("a", lambda d: calls.append(d))
        bus.subscribe("b", lambda d: calls.append(d))
        bus.clear_all()
        bus.publish("a", 1)
        bus.publish("b", 2)
        assert calls == []

    def test_list_events_returns_subscribed_events(self):
        bus = EventBus()
        bus.subscribe("alpha", lambda d: None)
        bus.subscribe("beta", lambda d: None)
        events = bus.list_events()
        assert "alpha" in events
        assert "beta" in events

    def test_list_events_excludes_cleared_events(self):
        bus = EventBus()
        bus.subscribe("alpha", lambda d: None)
        bus.clear("alpha")
        assert "alpha" not in bus.list_events()

    def test_multiple_subscribers_all_called(self):
        bus = EventBus()
        results = []
        bus.subscribe("ev", lambda d: results.append("a"))
        bus.subscribe("ev", lambda d: results.append("b"))
        bus.publish("ev", None)
        assert sorted(results) == ["a", "b"]

    def test_publish_none_data(self):
        bus = EventBus()
        received = []
        bus.subscribe("ev", lambda d: received.append(d))
        bus.publish("ev")
        assert received == [None]


# ---------------------------------------------------------------------------
# BuddyBot tests
# ---------------------------------------------------------------------------

class TestBuddyBot:
    def _make_bot(self, tier=Tier.FREE):
        return Chatbot(tier=tier)

    def test_register_bot(self):
        buddy = BuddyBot()
        bot = self._make_bot()
        buddy.register_bot("chat", bot)
        assert "chat" in buddy.list_bots()

    def test_list_bots_empty(self):
        buddy = BuddyBot()
        assert buddy.list_bots() == []

    def test_register_duplicate_raises(self):
        buddy = BuddyBot()
        bot = self._make_bot()
        buddy.register_bot("chat", bot)
        with pytest.raises(BuddyBotError, match="already registered"):
            buddy.register_bot("chat", self._make_bot())

    def test_register_non_protocol_raises(self):
        buddy = BuddyBot()
        with pytest.raises(BuddyBotError, match="SectorBotProtocol"):
            buddy.register_bot("bad", object())

    def test_unregister_bot(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        buddy.unregister_bot("chat")
        assert "chat" not in buddy.list_bots()

    def test_unregister_noop_if_not_registered(self):
        buddy = BuddyBot()
        buddy.unregister_bot("nonexistent")  # should not raise

    def test_chat_routes_to_correct_bot(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        result = buddy.chat("chat", "Hello!")
        assert isinstance(result, dict)
        assert "message" in result

    def test_chat_adds_bot_name_to_response(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        result = buddy.chat("chat", "Hello!")
        assert result["bot_name"] == "chat"

    def test_chat_adds_timestamp_to_response(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        result = buddy.chat("chat", "Hello!")
        assert "timestamp" in result
        assert isinstance(result["timestamp"], float)

    def test_chat_unknown_bot_raises(self):
        buddy = BuddyBot()
        with pytest.raises(BuddyBotError, match="No bot named"):
            buddy.chat("nonexistent", "Hello!")

    def test_chat_error_lists_available_bots(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        with pytest.raises(BuddyBotError, match="chat"):
            buddy.chat("missing", "Hello!")

    def test_get_history_all(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        buddy.chat("chat", "First message")
        history = buddy.get_history()
        assert len(history) == 2  # user + assistant

    def test_get_history_filtered_by_bot(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        buddy.register_bot("chat2", self._make_bot())
        buddy.chat("chat", "msg1")
        buddy.chat("chat2", "msg2")
        chat_history = buddy.get_history("chat")
        assert all(e["bot"] == "chat" for e in chat_history)

    def test_clear_history_all(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        buddy.chat("chat", "Hello")
        buddy.clear_history()
        assert buddy.get_history() == []

    def test_clear_history_specific_bot(self):
        buddy = BuddyBot()
        buddy.register_bot("a", self._make_bot())
        buddy.register_bot("b", self._make_bot())
        buddy.chat("a", "msg a")
        buddy.chat("b", "msg b")
        buddy.clear_history("a")
        assert buddy.get_history("a") == []
        assert len(buddy.get_history("b")) > 0

    def test_describe_bot_tier(self):
        buddy = BuddyBot()
        buddy.register_bot("chat", self._make_bot())
        result = buddy.describe_bot_tier("chat")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_describe_bot_tier_unknown_raises(self):
        buddy = BuddyBot()
        with pytest.raises(BuddyBotError, match="No bot named"):
            buddy.describe_bot_tier("unknown")

    def test_event_bus_fires_on_register(self):
        bus = EventBus()
        buddy = BuddyBot(event_bus=bus)
        events = []
        bus.subscribe("buddy.bot_registered", lambda d: events.append(d))
        buddy.register_bot("chat", self._make_bot())
        assert events == [{"name": "chat"}]

    def test_event_bus_fires_on_unregister(self):
        bus = EventBus()
        buddy = BuddyBot(event_bus=bus)
        buddy.register_bot("chat", self._make_bot())
        events = []
        bus.subscribe("buddy.bot_unregistered", lambda d: events.append(d))
        buddy.unregister_bot("chat")
        assert events == [{"name": "chat"}]

    def test_event_bus_fires_on_message(self):
        bus = EventBus()
        buddy = BuddyBot(event_bus=bus)
        buddy.register_bot("chat", self._make_bot())
        received = []
        responded = []
        bus.subscribe("buddy.message_received", lambda d: received.append(d))
        bus.subscribe("buddy.message_responded", lambda d: responded.append(d))
        buddy.chat("chat", "Hello!")
        assert len(received) == 1
        assert received[0]["bot"] == "chat"
        assert len(responded) == 1

    def test_shared_event_bus_accessible(self):
        bus = EventBus()
        buddy = BuddyBot(event_bus=bus)
        assert buddy.event_bus is bus

    def test_default_event_bus_created_if_none(self):
        buddy = BuddyBot()
        assert isinstance(buddy.event_bus, EventBus)
