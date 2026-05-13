"""
Tests for bots/vibe_coding_bot/vibe_coding_bot.py

Covers:
  1. Session lifecycle (create, get, close, list)
  2. Code editing
  3. Code execution (inline and via session)
  4. Collaboration (join, leave, cursor, chat)
  5. Buddy AI assistance (complete, review, explain)
  6. Package management
  7. Deployment
  8. Dashboard and capabilities
  9. Error paths
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.vibe_coding_bot.vibe_coding_bot import (
    VibeCodingBot,
    VibeCodingSession,
    CodeExecution,
    ExecutionStatus,
    SessionStatus,
    DeployTarget,
    _execute_code,
)


# ---------------------------------------------------------------------------
# _execute_code helper
# ---------------------------------------------------------------------------


class TestExecuteCode:
    def test_unsupported_language_simulated(self):
        result = _execute_code("cobol", "DISPLAY 'HELLO'.")
        assert result.status == ExecutionStatus.SIMULATED
        assert "simulated" in result.stdout.lower()

    def test_python_hello_world_or_simulated(self):
        result = _execute_code("python", "print('hello')")
        assert result.status in (ExecutionStatus.SUCCESS, ExecutionStatus.SIMULATED)
        assert isinstance(result.stdout, str)

    def test_execution_has_id(self):
        result = _execute_code("python", "x = 1")
        assert result.execution_id
        assert len(result.execution_id) > 0

    def test_duration_non_negative(self):
        result = _execute_code("python", "pass")
        assert result.duration_seconds >= 0

    def test_syntax_error_returns_error_or_simulated(self):
        result = _execute_code("python", "def broken(")
        assert result.status in (ExecutionStatus.ERROR, ExecutionStatus.SIMULATED)


# ---------------------------------------------------------------------------
# VibeCodingBot — Session lifecycle
# ---------------------------------------------------------------------------


class TestSessionLifecycle:
    def setup_method(self):
        self.bot = VibeCodingBot()

    def test_create_session_returns_session(self):
        session = self.bot.create_session(owner_id="user1", language="python", title="My Session")
        assert isinstance(session, VibeCodingSession)
        assert session.owner_id == "user1"
        assert session.language == "python"

    def test_create_session_stored(self):
        session = self.bot.create_session(owner_id="user2")
        assert self.bot.get_session(session.session_id) is session

    def test_create_session_invalid_language(self):
        with pytest.raises(ValueError, match="not supported"):
            self.bot.create_session(owner_id="user3", language="brainfuck")

    def test_get_session_nonexistent_returns_none(self):
        assert self.bot.get_session("nonexistent") is None

    def test_close_session_returns_true(self):
        session = self.bot.create_session(owner_id="u")
        assert self.bot.close_session(session.session_id) is True

    def test_close_session_removes_from_store(self):
        session = self.bot.create_session(owner_id="u")
        sid = session.session_id
        self.bot.close_session(sid)
        assert self.bot.get_session(sid) is None

    def test_close_nonexistent_returns_false(self):
        assert self.bot.close_session("ghost") is False

    def test_list_sessions_returns_list(self):
        self.bot.create_session(owner_id="list_user")
        sessions = self.bot.list_sessions()
        assert isinstance(sessions, list)
        assert len(sessions) >= 1

    def test_list_sessions_filter_by_owner(self):
        self.bot.create_session(owner_id="alice")
        self.bot.create_session(owner_id="bob")
        alice_sessions = self.bot.list_sessions(owner_id="alice")
        assert all(s["owner_id"] == "alice" for s in alice_sessions)

    def test_max_sessions_enforced(self):
        bot = VibeCodingBot(max_sessions=2)
        bot.create_session(owner_id="u1")
        bot.create_session(owner_id="u2")
        with pytest.raises(RuntimeError, match="Maximum concurrent sessions"):
            bot.create_session(owner_id="u3")


# ---------------------------------------------------------------------------
# Code editing and execution
# ---------------------------------------------------------------------------


class TestCodeExecution:
    def setup_method(self):
        self.bot = VibeCodingBot()
        self.session = self.bot.create_session(owner_id="dev", language="python")

    def test_update_code(self):
        result = self.bot.update_code(self.session.session_id, "print('hi')")
        assert result["status"] == "updated"

    def test_run_code_returns_code_execution(self):
        self.bot.update_code(self.session.session_id, "x = 42")
        execution = self.bot.run_code(self.session.session_id)
        assert isinstance(execution, CodeExecution)
        assert execution.language == "python"

    def test_run_code_adds_to_history(self):
        before = len(self.session.execution_history)
        self.bot.run_code(self.session.session_id, code="pass")
        assert len(self.session.execution_history) == before + 1

    def test_run_code_with_explicit_language(self):
        execution = self.bot.run_code(self.session.session_id, code="console.log(1)", language="javascript")
        assert execution.language == "javascript"

    def test_run_code_inline_no_session(self):
        execution = self.bot.run_code_inline("print(2+2)", language="python")
        assert execution.status in (ExecutionStatus.SUCCESS, ExecutionStatus.SIMULATED)

    def test_run_code_missing_session_raises(self):
        with pytest.raises(KeyError):
            self.bot.run_code("ghost_session")


# ---------------------------------------------------------------------------
# Collaboration
# ---------------------------------------------------------------------------


class TestCollaboration:
    def setup_method(self):
        self.bot = VibeCodingBot()
        self.session = self.bot.create_session(owner_id="owner")

    def test_join_session(self):
        result = self.bot.join_session(self.session.session_id, "user1", "Alice")
        assert result["user_id"] == "user1"
        assert len(result["collaborators"]) >= 1

    def test_join_session_twice_no_duplicate(self):
        self.bot.join_session(self.session.session_id, "user1", "Alice")
        self.bot.join_session(self.session.session_id, "user1", "Alice")
        assert len(self.session.collaborators) == 1

    def test_leave_session(self):
        self.bot.join_session(self.session.session_id, "user1", "Alice")
        result = self.bot.leave_session(self.session.session_id, "user1")
        assert result["status"] == "left"
        assert len(self.session.collaborators) == 0

    def test_move_cursor(self):
        self.bot.join_session(self.session.session_id, "user1", "Alice")
        result = self.bot.move_cursor(self.session.session_id, "user1", line=5, column=12)
        assert result["line"] == 5
        assert result["column"] == 12

    def test_send_chat(self):
        result = self.bot.send_chat(self.session.session_id, "user1", "Hello world!")
        assert result["message"] == "Hello world!"
        assert len(self.session.chat_history) == 1


# ---------------------------------------------------------------------------
# Buddy AI assistance
# ---------------------------------------------------------------------------


class TestBuddyAssistance:
    def setup_method(self):
        self.bot = VibeCodingBot()
        self.session = self.bot.create_session(owner_id="dev", language="python")
        self.bot.update_code(self.session.session_id, "def greet(name):\n    pass")

    def test_buddy_complete_returns_suggestion(self):
        result = self.bot.buddy_complete(self.session.session_id, "complete the greeting function")
        assert "suggestion" in result
        assert isinstance(result["suggestion"], str)

    def test_buddy_review_returns_score(self):
        result = self.bot.buddy_review(self.session.session_id)
        assert "score" in result
        assert "suggestions" in result

    def test_buddy_explain_returns_explanation(self):
        result = self.bot.buddy_explain(self.session.session_id)
        assert "explanation" in result
        assert result["lines"] > 0


# ---------------------------------------------------------------------------
# Package management and deployment
# ---------------------------------------------------------------------------


class TestPackagesAndDeploy:
    def setup_method(self):
        self.bot = VibeCodingBot()
        self.session = self.bot.create_session(owner_id="dev")

    def test_install_package(self):
        result = self.bot.install_package(self.session.session_id, "numpy")
        assert result["package"] == "numpy"
        assert result["status"] == "installed"
        assert "numpy" in self.session.packages_installed

    def test_install_package_idempotent(self):
        self.bot.install_package(self.session.session_id, "pandas")
        self.bot.install_package(self.session.session_id, "pandas")
        assert self.session.packages_installed.count("pandas") == 1

    def test_deploy_returns_url(self):
        result = self.bot.deploy(self.session.session_id, target=DeployTarget.DOCKER)
        assert "url" in result
        assert result["status"] == "deployed"
        assert result["target"] == "docker"

    def test_deploy_vercel(self):
        result = self.bot.deploy(self.session.session_id, target=DeployTarget.VERCEL)
        assert "vercel" in result["url"]


# ---------------------------------------------------------------------------
# Dashboard and capabilities
# ---------------------------------------------------------------------------


class TestDashboard:
    def setup_method(self):
        self.bot = VibeCodingBot()

    def test_dashboard_keys(self):
        dash = self.bot.dashboard()
        for key in ("active_sessions", "total_sessions", "total_executions", "supported_languages"):
            assert key in dash

    def test_get_capabilities_keys(self):
        caps = self.bot.get_capabilities()
        assert caps["bot_id"] == "vibe_coding_bot"
        assert "supported_languages" in caps
        assert len(caps["features"]) > 0

    def test_supported_languages_non_empty(self):
        assert len(self.bot.SUPPORTED_LANGUAGES) > 5
