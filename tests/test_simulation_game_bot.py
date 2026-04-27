"""
Tests for bots/simulation_game_bot/simulation_game_bot.py

Covers:
  1. Built-in scenario loading
  2. Custom scenario creation
  3. Scenario-from-prompt generation
  4. Game session start
  5. Turn-based action processing
  6. Win detection
  7. Game-over detection
  8. Leaderboard
  9. Dashboard and capabilities
  10. Error paths
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

from bots.simulation_game_bot.simulation_game_bot import (
    SimulationGameBot,
    GameCategory,
    GameStatus,
    ActionResult,
    GameSession,
    GameScenario,
    _SCENARIO_TEMPLATES,
)


# ---------------------------------------------------------------------------
# Built-in scenarios
# ---------------------------------------------------------------------------


class TestBuiltinScenarios:
    def setup_method(self):
        self.bot = SimulationGameBot(seed=42)

    def test_builtin_scenarios_loaded(self):
        scenarios = self.bot.list_scenarios()
        assert len(scenarios) == len(_SCENARIO_TEMPLATES)

    def test_scenario_keys(self):
        scenarios = self.bot.list_scenarios()
        for s in scenarios:
            for key in ("scenario_id", "title", "description", "category", "win_condition", "actions"):
                assert key in s

    def test_list_scenarios_by_category(self):
        biz = self.bot.list_scenarios(category=GameCategory.BUSINESS)
        assert all(s["category"] == "business" for s in biz)

    def test_get_scenario_returns_object(self):
        sc = self.bot.get_scenario("startup_simulator")
        assert sc is not None
        assert sc.title == "DreamCo Startup Simulator"

    def test_get_nonexistent_scenario_returns_none(self):
        assert self.bot.get_scenario("ghost") is None


# ---------------------------------------------------------------------------
# Custom scenario creation
# ---------------------------------------------------------------------------


class TestCustomScenario:
    def setup_method(self):
        self.bot = SimulationGameBot(seed=42)

    def test_create_custom_scenario(self):
        sc = self.bot.create_custom_scenario(
            title="My Game",
            description="A test game",
            category=GameCategory.CUSTOM,
            initial_state={"score": 0, "turn": 0},
            actions={"score_point": {"description": "Score a point", "cost": 0, "effect": {"score": 10}}},
            win_condition_desc="Score 100 points",
        )
        assert sc.scenario_id in self.bot._scenarios
        assert sc.title == "My Game"

    def test_custom_scenario_appears_in_list(self):
        before = len(self.bot.list_scenarios())
        self.bot.create_custom_scenario("X", "desc", GameCategory.CUSTOM)
        assert len(self.bot.list_scenarios()) == before + 1

    def test_generate_from_prompt_startup(self):
        sc = self.bot.generate_scenario_from_prompt("I want a startup business challenge")
        assert sc is not None
        # Title will contain "Buddy-Generated:" prefix with the prompt
        assert "Buddy-Generated" in sc.title

    def test_generate_from_prompt_ecosystem(self):
        sc = self.bot.generate_scenario_from_prompt("an ecosystem with nature and animals")
        assert sc is not None

    def test_generate_from_prompt_custom_category(self):
        sc = self.bot.generate_scenario_from_prompt("anything", category=GameCategory.EDUCATION)
        assert sc.category == GameCategory.EDUCATION


# ---------------------------------------------------------------------------
# Game session and actions
# ---------------------------------------------------------------------------


class TestGameSession:
    def setup_method(self):
        self.bot = SimulationGameBot(seed=0)

    def test_start_game_returns_session(self):
        session = self.bot.start_game("startup_simulator", "player1")
        assert isinstance(session, GameSession)
        assert session.player_id == "player1"
        assert session.status == GameStatus.RUNNING

    def test_start_game_invalid_scenario(self):
        with pytest.raises(KeyError):
            self.bot.start_game("nonexistent", "player1")

    def test_take_action_valid(self):
        session = self.bot.start_game("ecosystem_sim", "alice")
        result = self.bot.take_action(session.game_id, "add_rabbit")
        assert result["result"] in [a.value for a in ActionResult]
        assert "state" in result

    def test_take_action_invalid(self):
        session = self.bot.start_game("ecosystem_sim", "bob")
        result = self.bot.take_action(session.game_id, "fly_to_moon")
        assert "error" in result

    def test_take_action_increments_turn(self):
        session = self.bot.start_game("budget_hero", "charlie")
        initial_turn = session.turn
        self.bot.take_action(session.game_id, "save")
        assert session.turn == initial_turn + 1

    def test_take_action_adds_to_history(self):
        session = self.bot.start_game("ai_arena", "delta")
        self.bot.take_action(session.game_id, "attack")
        assert len(session.history) == 1

    def test_take_action_on_finished_game_returns_error(self):
        session = self.bot.start_game("budget_hero", "echo")
        session.status = GameStatus.FINISHED
        result = self.bot.take_action(session.game_id, "save")
        assert "error" in result

    def test_take_action_missing_session(self):
        with pytest.raises(KeyError):
            self.bot.take_action("ghost_game", "save")


# ---------------------------------------------------------------------------
# Win condition
# ---------------------------------------------------------------------------


class TestWinCondition:
    def setup_method(self):
        self.bot = SimulationGameBot(seed=1)

    def test_win_budget_hero(self):
        """Force a win by directly setting state past the goal."""
        session = self.bot.start_game("budget_hero", "winner")
        # Inject winning state
        session.state["savings"] = 9_999
        result = self.bot.take_action(session.game_id, "save")
        # After this action savings becomes >=10000 → WIN
        assert result["result"] == ActionResult.WIN.value
        assert session.status == GameStatus.FINISHED

    def test_ecosystem_win_requires_10_turns(self):
        session = self.bot.start_game("ecosystem_sim", "eco_player")
        # Force state to have all three species > 0 but only 9 turns done
        session.state = {"wolves": 3, "rabbits": 10, "grass": 50, "turn": 9}
        # 10th turn should win
        result = self.bot.take_action(session.game_id, "plant_grass")
        assert result["result"] == ActionResult.WIN.value


# ---------------------------------------------------------------------------
# Leaderboard
# ---------------------------------------------------------------------------


class TestLeaderboard:
    def setup_method(self):
        self.bot = SimulationGameBot(seed=2)

    def test_leaderboard_empty_when_no_finished_games(self):
        board = self.bot.get_leaderboard("startup_simulator")
        assert isinstance(board, list)

    def test_leaderboard_appears_after_finish(self):
        session = self.bot.start_game("ai_arena", "ranker")
        session.status = GameStatus.FINISHED
        board = self.bot.get_leaderboard("ai_arena")
        assert len(board) >= 1
        assert board[0]["player_id"] == "ranker"

    def test_leaderboard_max_10(self):
        for i in range(15):
            s = self.bot.start_game("ai_arena", f"p{i}")
            s.state["agent_score"] = i * 10
            s.status = GameStatus.FINISHED
        board = self.bot.get_leaderboard("ai_arena")
        assert len(board) <= 10


# ---------------------------------------------------------------------------
# Dashboard and capabilities
# ---------------------------------------------------------------------------


class TestDashboard:
    def setup_method(self):
        self.bot = SimulationGameBot()

    def test_dashboard_keys(self):
        dash = self.bot.dashboard()
        for key in ("total_scenarios", "total_sessions", "active_sessions", "finished_sessions"):
            assert key in dash

    def test_get_capabilities_keys(self):
        caps = self.bot.get_capabilities()
        assert caps["bot_id"] == "simulation_game_bot"
        assert "categories" in caps
        assert len(caps["features"]) > 0

    def test_capabilities_builtin_count(self):
        caps = self.bot.get_capabilities()
        assert caps["builtin_scenarios"] == len(_SCENARIO_TEMPLATES)
