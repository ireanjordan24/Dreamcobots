"""Tests for TaskEngine."""

import pytest
from BuddyAI.task_engine import TaskEngine, UnknownIntentError


@pytest.fixture
def engine():
    e = TaskEngine()
    e.register_capability("greet", lambda p: {"success": True, "message": "Hello!"})
    e.register_capability(
        "echo", lambda p: {"success": True, "message": p.get("text", "")}
    )
    return e


def test_execute_known_intent(engine):
    result = engine.execute("greet", {})
    assert result["success"] is True
    assert result["message"] == "Hello!"


def test_execute_unknown_intent_raises(engine):
    with pytest.raises(UnknownIntentError):
        engine.execute("nonexistent", {})


def test_list_capabilities(engine):
    caps = engine.list_capabilities()
    assert "greet" in caps
    assert "echo" in caps


def test_register_capability(engine):
    engine.register_capability("new_cap", lambda p: {"done": True})
    result = engine.execute("new_cap", {})
    assert result["done"] is True


def test_unregister_capability(engine):
    engine.register_capability("temp", lambda p: {})
    removed = engine.unregister_capability("temp")
    assert removed is True
    with pytest.raises(UnknownIntentError):
        engine.execute("temp", {})


def test_unregister_nonexistent(engine):
    assert engine.unregister_capability("ghost") is False


def test_process_text_known(engine):
    result = engine.process_text("help")
    # 'help' intent is not registered in this minimal engine
    # so we should get an informative failure
    assert "message" in result


def test_process_text_empty(engine):
    result = engine.process_text("")
    assert result["success"] is False


def test_process_text_with_registered_intent():
    e = TaskEngine()
    e.register_capability("add_todo", lambda p: {"success": True, "message": "added"})
    result = e.process_text("Add todo write tests")
    assert result["success"] is True


def test_handler_exception_returns_error(engine):
    engine.register_capability("explode", lambda p: (_ for _ in ()).throw(RuntimeError("boom")))
    result = engine.execute("explode", {})
    assert result["success"] is False
    assert "boom" in result["error"]
