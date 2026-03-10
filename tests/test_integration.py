"""
Integration tests for the DreamCobot ↔ BuddyBot collaboration framework.

These tests verify:
- AuthModule: registration, token verification, permission checks
- EventBus: subscribe/publish/unsubscribe, error handling
- BuddyBot: bot registration, knowledge base, task queue, event dispatch
- DreamCobot: full integration with BuddyBot (lifecycle, messaging, tasks,
              knowledge sharing, authentication)
"""

import pytest

from BuddyAI.auth import AuthModule, AuthError
from BuddyAI.event_bus import EventBus, EventBusError
from BuddyAI.buddy_bot import BuddyBot, BuddyBotError
from bots.dreamcobot.dreamcobot import DreamCobot, DreamCobotError


# ---------------------------------------------------------------------------
# AuthModule tests
# ---------------------------------------------------------------------------

class TestAuthModule:
    def setup_method(self):
        self.auth = AuthModule()

    def test_register_and_verify(self):
        token = self.auth.register_bot("bot1")
        assert self.auth.verify_token("bot1", token) is True

    def test_verify_wrong_token_raises(self):
        self.auth.register_bot("bot2")
        with pytest.raises(AuthError):
            self.auth.verify_token("bot2", "wrong_token")

    def test_verify_unknown_bot_raises(self):
        with pytest.raises(AuthError):
            self.auth.verify_token("ghost", "any_token")

    def test_register_empty_id_raises(self):
        with pytest.raises(ValueError):
            self.auth.register_bot("")

    def test_permission_granted(self):
        self.auth.register_bot("bot3", permissions=["task:run"])
        self.auth.require_permission("bot3", "task:run")  # should not raise

    def test_permission_denied_raises(self):
        self.auth.register_bot("bot4", permissions=["knowledge:read"])
        with pytest.raises(AuthError):
            self.auth.require_permission("bot4", "task:run")

    def test_has_permission_true(self):
        self.auth.register_bot("bot5", permissions=["event:publish"])
        assert self.auth.has_permission("bot5", "event:publish") is True

    def test_has_permission_false(self):
        self.auth.register_bot("bot6")
        assert self.auth.has_permission("bot6", "task:run") is False

    def test_has_permission_unknown_bot(self):
        assert self.auth.has_permission("ghost", "task:run") is False

    def test_unregister_removes_bot(self):
        self.auth.register_bot("bot7")
        self.auth.unregister_bot("bot7")
        with pytest.raises(AuthError):
            self.auth.verify_token("bot7", "any")

    def test_tokens_are_unique(self):
        t1 = self.auth.register_bot("botA")
        auth2 = AuthModule()
        t2 = auth2.register_bot("botA")
        assert t1 != t2


# ---------------------------------------------------------------------------
# EventBus tests
# ---------------------------------------------------------------------------

class TestEventBus:
    def setup_method(self):
        self.bus = EventBus()

    def test_subscribe_and_publish(self):
        results = []
        self.bus.subscribe("ping", lambda p: results.append(p))
        count = self.bus.publish("ping", "hello")
        assert count == 1
        assert results == ["hello"]

    def test_publish_no_handlers_returns_zero(self):
        assert self.bus.publish("empty.event") == 0

    def test_multiple_handlers(self):
        calls = []
        self.bus.subscribe("evt", lambda p: calls.append("h1"))
        self.bus.subscribe("evt", lambda p: calls.append("h2"))
        self.bus.publish("evt", None)
        assert calls == ["h1", "h2"]

    def test_unsubscribe(self):
        calls = []
        handler = lambda p: calls.append(p)
        self.bus.subscribe("evt2", handler)
        self.bus.unsubscribe("evt2", handler)
        self.bus.publish("evt2", "x")
        assert calls == []

    def test_unsubscribe_nonexistent_is_noop(self):
        with pytest.raises(EventBusError):
            self.bus.unsubscribe("never.subscribed", lambda p: None)

    def test_non_callable_raises(self):
        with pytest.raises(EventBusError):
            self.bus.subscribe("evt3", "not_callable")

    def test_error_handler_called_on_exception(self):
        errors = []

        def bad_handler(p):
            raise RuntimeError("boom")

        self.bus = EventBus(error_handler=lambda ev, h, exc: errors.append(exc))
        self.bus.subscribe("fail", bad_handler)
        self.bus.publish("fail", None)
        assert len(errors) == 1
        assert isinstance(errors[0], RuntimeError)

    def test_exception_propagates_without_error_handler(self):
        def bad(p):
            raise ValueError("oops")

        self.bus.subscribe("fail2", bad)
        with pytest.raises(ValueError):
            self.bus.publish("fail2", None)

    def test_events_list(self):
        self.bus.subscribe("z.event", lambda p: None)
        self.bus.subscribe("a.event", lambda p: None)
        assert self.bus.events() == ["a.event", "z.event"]

    def test_handler_count(self):
        self.bus.subscribe("counted", lambda p: None)
        self.bus.subscribe("counted", lambda p: None)
        assert self.bus.handler_count("counted") == 2
        assert self.bus.handler_count("absent") == 0


# ---------------------------------------------------------------------------
# BuddyBot tests
# ---------------------------------------------------------------------------

class TestBuddyBot:
    def setup_method(self):
        self.buddy = BuddyBot("TestHub")

    def test_register_bot_returns_token(self):
        token = self.buddy.register_bot("mybot")
        assert isinstance(token, str) and len(token) > 0

    def test_duplicate_register_raises(self):
        self.buddy.register_bot("dup")
        with pytest.raises(BuddyBotError):
            self.buddy.register_bot("dup")

    def test_connected_bots(self):
        self.buddy.register_bot("b1")
        self.buddy.register_bot("b2")
        bots = self.buddy.connected_bots()
        assert "b1" in bots
        assert "b2" in bots

    def test_authenticate_success(self):
        token = self.buddy.register_bot("auth_bot")
        assert self.buddy.authenticate("auth_bot", token) is True

    def test_authenticate_wrong_token_raises(self):
        self.buddy.register_bot("auth_bot2")
        with pytest.raises(AuthError):
            self.buddy.authenticate("auth_bot2", "bad")

    def test_unregister_removes_bot(self):
        self.buddy.register_bot("gone")
        self.buddy.unregister_bot("gone")
        assert "gone" not in self.buddy.connected_bots()

    def test_knowledge_base_set_get(self):
        self.buddy.set_knowledge("greeting", "hello")
        assert self.buddy.get_knowledge("greeting") == "hello"

    def test_knowledge_base_default(self):
        assert self.buddy.get_knowledge("missing", "default") == "default"

    def test_knowledge_base_delete(self):
        self.buddy.set_knowledge("temp", 1)
        self.buddy.delete_knowledge("temp")
        assert self.buddy.get_knowledge("temp") is None

    def test_knowledge_keys(self):
        self.buddy.set_knowledge("z", 1)
        self.buddy.set_knowledge("a", 2)
        assert self.buddy.knowledge_keys() == ["a", "z"]

    def test_task_queue_push_pop(self):
        task = {"type": "onboard", "user_id": 1}
        self.buddy.push_task(task)
        assert self.buddy.pending_tasks() == 1
        popped = self.buddy.pop_task()
        assert popped == task
        assert self.buddy.pending_tasks() == 0

    def test_pop_empty_queue_returns_none(self):
        assert self.buddy.pop_task() is None

    def test_push_non_dict_raises(self):
        with pytest.raises(BuddyBotError):
            self.buddy.push_task("not a dict")

    def test_task_queue_fifo(self):
        self.buddy.push_task({"id": 1})
        self.buddy.push_task({"id": 2})
        assert self.buddy.pop_task() == {"id": 1}
        assert self.buddy.pop_task() == {"id": 2}

    def test_event_subscription_and_publish(self):
        received = []
        self.buddy.subscribe_event("greet", lambda p: received.append(p))
        self.buddy.publish_event("greet", "world")
        assert received == ["world"]

    def test_publish_event_returns_handler_count(self):
        self.buddy.subscribe_event("multi", lambda p: None)
        self.buddy.subscribe_event("multi", lambda p: None)
        assert self.buddy.publish_event("multi") == 2


# ---------------------------------------------------------------------------
# DreamCobot integration tests
# ---------------------------------------------------------------------------

class TestDreamCobot:
    def setup_method(self):
        self.buddy = BuddyBot("IntegrationHub")
        self.dream = DreamCobot(self.buddy, bot_id="dreamcobot-test")

    def teardown_method(self):
        if self.dream.is_running:
            self.dream.stop()

    def test_start_registers_with_buddy(self):
        self.dream.start()
        assert "dreamcobot-test" in self.buddy.connected_bots()

    def test_start_sets_running(self):
        self.dream.start()
        assert self.dream.is_running is True

    def test_stop_unregisters(self):
        self.dream.start()
        self.dream.stop()
        assert "dreamcobot-test" not in self.buddy.connected_bots()
        assert self.dream.is_running is False

    def test_start_twice_is_safe(self):
        self.dream.start()
        self.dream.start()  # second call is a no-op

    def test_stop_when_not_started_is_safe(self):
        self.dream.stop()  # should not raise

    def test_requires_running_before_actions(self):
        with pytest.raises(DreamCobotError):
            self.dream.handle_user_message("hello")

    def test_handle_user_message(self):
        self.dream.start()
        response = self.dream.handle_user_message("Hi!")
        assert "dreamcobot-test" in response
        assert "Hi!" in response

    def test_handle_user_message_publishes_event(self):
        self.dream.start()
        events = []
        self.buddy.subscribe_event("user.message", lambda p: events.append(p))
        self.dream.handle_user_message("Test message")
        assert len(events) == 1
        assert events[0]["text"] == "Test message"

    def test_assign_task(self):
        self.dream.start()
        self.dream.assign_task({"type": "goal", "user": "Alice"})
        assert self.buddy.pending_tasks() == 1

    def test_process_next_task(self):
        self.dream.start()
        task = {"type": "onboard", "user_id": 5}
        self.buddy.push_task(task)
        result = self.dream.process_next_task()
        assert result == task

    def test_process_empty_queue_returns_none(self):
        self.dream.start()
        assert self.dream.process_next_task() is None

    def test_store_and_retrieve_knowledge(self):
        self.dream.start()
        self.dream.store_knowledge("user_pref", "dark_mode")
        assert self.dream.retrieve_knowledge("user_pref") == "dark_mode"

    def test_retrieve_missing_knowledge_default(self):
        self.dream.start()
        assert self.dream.retrieve_knowledge("nope", "fallback") == "fallback"

    def test_knowledge_shared_with_buddy(self):
        self.dream.start()
        self.dream.store_knowledge("shared_key", 42)
        assert self.buddy.get_knowledge("shared_key") == 42

    def test_verify_identity(self):
        self.dream.start()
        assert self.dream.verify_identity() is True

    def test_invalid_buddy_raises(self):
        with pytest.raises(DreamCobotError):
            DreamCobot("not_a_buddy_bot")

    def test_create_and_start_factory(self):
        buddy2 = BuddyBot()
        bot = DreamCobot.create_and_start(buddy2, bot_id="factory-bot")
        try:
            assert bot.is_running is True
            assert "factory-bot" in buddy2.connected_bots()
        finally:
            bot.stop()

    def test_duplicate_bot_id_raises(self):
        self.dream.start()
        dream2 = DreamCobot(self.buddy, bot_id="dreamcobot-test")
        with pytest.raises(DreamCobotError):
            dream2.start()

    def test_event_on_user_joined(self, capsys):
        self.dream.start()
        self.buddy.publish_event("user.joined", {"user_id": 99})
        captured = capsys.readouterr()
        assert "99" in captured.out

    def test_multi_bot_collaboration(self):
        """Two DreamCobot instances share tasks via BuddyBot."""
        buddy = BuddyBot("MultiHub")
        bot_a = DreamCobot.create_and_start(buddy, bot_id="bot-a")
        bot_b = DreamCobot.create_and_start(buddy, bot_id="bot-b")
        try:
            bot_a.assign_task({"type": "report", "owner": "bot-a"})
            task = bot_b.process_next_task()
            assert task == {"type": "report", "owner": "bot-a"}
        finally:
            bot_a.stop()
            bot_b.stop()
