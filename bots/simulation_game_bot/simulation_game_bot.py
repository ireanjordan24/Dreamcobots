"""
Simulation Game Bot — Buddy creates and runs simulation games for any audience.

Buddy can generate simulation games for:
  • Teachers / students  — learning simulations (ecosystems, history, chemistry).
  • Business people      — market simulations, startup strategy games, trading.
  • Parents / children   — fun life-skill games (cooking, budgeting, pet care).
  • Developers           — traffic simulations, AI agent arenas.
  • Anyone               — custom scenarios generated from a natural-language prompt.

Architecture
------------
  GameScenario     — defines rules, win conditions, and initial state.
  GameSession      — active play state (player actions → state transitions).
  SimulationGameBot— Buddy's game designer, session manager, and referee.
"""
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.

from __future__ import annotations

import random
import time
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------


class GameCategory(str, Enum):
    EDUCATION = "education"
    BUSINESS = "business"
    PERSONAL = "personal"
    TECHNOLOGY = "technology"
    ENTERTAINMENT = "entertainment"
    HEALTH = "health"
    CUSTOM = "custom"


class GameStatus(str, Enum):
    LOBBY = "lobby"
    RUNNING = "running"
    PAUSED = "paused"
    FINISHED = "finished"


class ActionResult(str, Enum):
    SUCCESS = "success"
    FAILURE = "failure"
    NEUTRAL = "neutral"
    GAME_OVER = "game_over"
    WIN = "win"


# ---------------------------------------------------------------------------
# Built-in scenario templates
# ---------------------------------------------------------------------------

# Each template is a dict with keys:
#   title, description, category, initial_state, actions, win_condition_desc
_SCENARIO_TEMPLATES: Dict[str, Dict[str, Any]] = {
    "startup_simulator": {
        "title": "DreamCo Startup Simulator",
        "description": "Build your startup from $10,000 seed money to $1M valuation.",
        "category": GameCategory.BUSINESS,
        "initial_state": {"cash": 10_000, "valuation": 0, "team_size": 1, "customers": 0, "turn": 0},
        "actions": {
            "hire": {"description": "Hire a developer (-$5,000, +team_size)", "cost": 5_000, "effect": {"team_size": 1}},
            "market": {"description": "Run a marketing campaign (-$2,000, +customers)", "cost": 2_000, "effect": {"customers": 20}},
            "build": {"description": "Build a feature (requires 2+ team, +valuation)", "cost": 0, "effect": {"valuation": 50_000}},
            "raise_funds": {"description": "Pitch investors (+$50,000)", "cost": 0, "effect": {"cash": 50_000}},
        },
        "win_condition": lambda s: s.get("valuation", 0) >= 1_000_000,
        "win_condition_desc": "Reach a valuation of $1,000,000",
    },
    "ecosystem_sim": {
        "title": "Forest Ecosystem Simulator",
        "description": "Balance predators, prey, and vegetation to sustain a healthy forest.",
        "category": GameCategory.EDUCATION,
        "initial_state": {"wolves": 5, "rabbits": 50, "grass": 200, "turn": 0},
        "actions": {
            "add_wolf": {"description": "Introduce a wolf (+wolves, -rabbits)", "cost": 0, "effect": {"wolves": 1, "rabbits": -5}},
            "add_rabbit": {"description": "Introduce a rabbit (+rabbits)", "cost": 0, "effect": {"rabbits": 5}},
            "plant_grass": {"description": "Plant grass (+grass)", "cost": 0, "effect": {"grass": 30}},
            "remove_wolf": {"description": "Remove a predator (-wolves)", "cost": 0, "effect": {"wolves": -1}},
        },
        "win_condition": lambda s: s.get("wolves", 0) > 0 and s.get("rabbits", 0) > 0 and s.get("grass", 0) > 0 and s.get("turn", 0) >= 10,
        "win_condition_desc": "Maintain a balanced ecosystem for 10 turns",
    },
    "budget_hero": {
        "title": "Budget Hero",
        "description": "Manage a monthly household budget and build $10,000 in savings.",
        "category": GameCategory.PERSONAL,
        "initial_state": {"cash": 3_000, "savings": 0, "happiness": 70, "debt": 2_000, "turn": 0},
        "actions": {
            "save": {"description": "Transfer $500 to savings (-cash, +savings)", "cost": 0, "effect": {"cash": -500, "savings": 500}},
            "pay_debt": {"description": "Pay $200 debt (-cash, -debt)", "cost": 0, "effect": {"cash": -200, "debt": -200}},
            "splurge": {"description": "Treat yourself (+happiness, -cash)", "cost": 0, "effect": {"cash": -300, "happiness": 10}},
            "side_hustle": {"description": "Do a side gig (+cash)", "cost": 0, "effect": {"cash": 800}},
        },
        "win_condition": lambda s: s.get("savings", 0) >= 10_000,
        "win_condition_desc": "Accumulate $10,000 in savings",
    },
    "trading_floor": {
        "title": "DreamCo Trading Floor",
        "description": "Day-trade simulated stocks and turn $5,000 into $25,000.",
        "category": GameCategory.BUSINESS,
        "initial_state": {"cash": 5_000, "portfolio_value": 0, "trades": 0, "turn": 0},
        "actions": {
            "buy_growth": {"description": "Buy growth stocks (high risk/reward)", "cost": 0, "effect": {}},
            "buy_stable": {"description": "Buy stable ETFs (low risk/reward)", "cost": 0, "effect": {}},
            "sell_all": {"description": "Liquidate portfolio", "cost": 0, "effect": {}},
            "research": {"description": "Spend a turn researching (+insight)", "cost": 0, "effect": {}},
        },
        "win_condition": lambda s: s.get("cash", 0) + s.get("portfolio_value", 0) >= 25_000,
        "win_condition_desc": "Grow total wealth to $25,000",
    },
    "ai_arena": {
        "title": "AI Agent Arena",
        "description": "Code and compete AI agents in a strategy tournament.",
        "category": GameCategory.TECHNOLOGY,
        "initial_state": {"agent_score": 0, "rounds_won": 0, "energy": 100, "turn": 0},
        "actions": {
            "attack": {"description": "Send an offensive agent (-energy, +score)", "cost": 0, "effect": {"energy": -10, "agent_score": 15}},
            "defend": {"description": "Reinforce defences (+energy, -small_score)", "cost": 0, "effect": {"energy": 20, "agent_score": 5}},
            "upgrade": {"description": "Upgrade agent intelligence (+score)", "cost": 0, "effect": {"agent_score": 25, "energy": -20}},
            "rest": {"description": "Recover energy", "cost": 0, "effect": {"energy": 30}},
        },
        "win_condition": lambda s: s.get("agent_score", 0) >= 200,
        "win_condition_desc": "Achieve an agent score of 200",
    },
}


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------


@dataclass
class GameScenario:
    """Blueprint for a simulation game."""

    scenario_id: str
    title: str
    description: str
    category: GameCategory
    initial_state: Dict[str, Any]
    actions: Dict[str, Dict[str, Any]]
    win_condition_desc: str
    # Callable[state_dict → bool]  (not serialisable, kept in-memory only)
    win_condition: Any = field(default=None, repr=False)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "scenario_id": self.scenario_id,
            "title": self.title,
            "description": self.description,
            "category": self.category.value,
            "win_condition": self.win_condition_desc,
            "actions": {
                k: {"description": v.get("description", "")}
                for k, v in self.actions.items()
            },
        }


@dataclass
class TurnEvent:
    """A single event that occurred on a game turn."""

    turn: int
    action: str
    result: ActionResult
    state_delta: Dict[str, Any]
    message: str


@dataclass
class GameSession:
    """An active game play session."""

    game_id: str
    scenario_id: str
    player_id: str
    state: Dict[str, Any]
    status: GameStatus = GameStatus.RUNNING
    history: List[TurnEvent] = field(default_factory=list)
    started_at: float = field(default_factory=time.time)
    finished_at: Optional[float] = None

    @property
    def turn(self) -> int:
        return self.state.get("turn", 0)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "game_id": self.game_id,
            "scenario_id": self.scenario_id,
            "player_id": self.player_id,
            "status": self.status.value,
            "turn": self.turn,
            "state": self.state,
            "history_length": len(self.history),
        }


# ---------------------------------------------------------------------------
# SimulationGameBot
# ---------------------------------------------------------------------------


class SimulationGameBot:
    """
    Buddy's game designer and referee for simulation games.

    Creates scenarios from natural-language prompts or from the built-in
    template catalogue, then manages all active game sessions.

    Parameters
    ----------
    seed : Optional[int]   Random seed for reproducible games (useful in tests).
    """

    bot_id = "simulation_game_bot"
    name = "Simulation Game Bot"
    category = "gaming"

    def __init__(self, seed: Optional[int] = None) -> None:
        self._rng = random.Random(seed)
        self._scenarios: Dict[str, GameScenario] = {}
        self._sessions: Dict[str, GameSession] = {}
        self._load_builtin_scenarios()

    # ------------------------------------------------------------------
    # Scenario management
    # ------------------------------------------------------------------

    def list_scenarios(self, category: Optional[GameCategory] = None) -> List[Dict[str, Any]]:
        """Return all available game scenarios."""
        scenarios = list(self._scenarios.values())
        if category:
            scenarios = [s for s in scenarios if s.category == category]
        return [s.to_dict() for s in scenarios]

    def get_scenario(self, scenario_id: str) -> Optional[GameScenario]:
        return self._scenarios.get(scenario_id)

    def create_custom_scenario(
        self,
        title: str,
        description: str,
        category: GameCategory = GameCategory.CUSTOM,
        initial_state: Optional[Dict[str, Any]] = None,
        actions: Optional[Dict[str, Dict[str, Any]]] = None,
        win_condition_desc: str = "Complete all objectives",
    ) -> GameScenario:
        """
        Create a custom game scenario (Buddy's 'vibe game design' feature).

        In a production system Buddy would use an LLM to generate the scenario
        from a natural-language prompt; here we build it from explicit params.
        """
        scenario = GameScenario(
            scenario_id=str(uuid.uuid4()),
            title=title,
            description=description,
            category=category,
            initial_state=initial_state or {"score": 0, "turn": 0},
            actions=actions or {
                "action_1": {"description": "Take action 1", "cost": 0, "effect": {"score": 10}},
                "action_2": {"description": "Take action 2", "cost": 0, "effect": {"score": 5}},
            },
            win_condition_desc=win_condition_desc,
            win_condition=lambda s: s.get("score", 0) >= 100,
        )
        self._scenarios[scenario.scenario_id] = scenario
        return scenario

    def generate_scenario_from_prompt(self, prompt: str, category: GameCategory = GameCategory.CUSTOM) -> GameScenario:
        """
        Generate a game scenario inspired by a natural-language prompt.

        (Buddy would call an LLM here in production; this implementation
        returns a structured scenario based on keyword detection.)
        """
        prompt_lower = prompt.lower()
        title = f"Buddy-Generated: {prompt[:50]}"
        if "business" in prompt_lower or "startup" in prompt_lower:
            base = "startup_simulator"
        elif "ecosystem" in prompt_lower or "nature" in prompt_lower:
            base = "ecosystem_sim"
        elif "budget" in prompt_lower or "money" in prompt_lower:
            base = "budget_hero"
        elif "trade" in prompt_lower or "stock" in prompt_lower:
            base = "trading_floor"
        else:
            base = "ai_arena"

        template = _SCENARIO_TEMPLATES[base]
        scenario = GameScenario(
            scenario_id=str(uuid.uuid4()),
            title=title,
            description=prompt,
            category=category,
            initial_state=dict(template["initial_state"]),
            actions=dict(template["actions"]),
            win_condition_desc=template["win_condition_desc"],
            win_condition=template["win_condition"],
        )
        self._scenarios[scenario.scenario_id] = scenario
        return scenario

    # ------------------------------------------------------------------
    # Session management
    # ------------------------------------------------------------------

    def start_game(self, scenario_id: str, player_id: str) -> GameSession:
        """Create a new game session for the given player and scenario."""
        scenario = self._scenarios.get(scenario_id)
        if scenario is None:
            raise KeyError(f"Scenario '{scenario_id}' not found.")
        session = GameSession(
            game_id=str(uuid.uuid4()),
            scenario_id=scenario_id,
            player_id=player_id,
            state=dict(scenario.initial_state),
        )
        self._sessions[session.game_id] = session
        return session

    def take_action(self, game_id: str, action: str) -> Dict[str, Any]:
        """
        Apply a player action to the game state and return the updated snapshot.

        Handles the startup_simulator and trading_floor with special logic;
        all other scenarios use the generic effect-dict approach.
        """
        session = self._require_session(game_id)
        scenario = self._scenarios[session.scenario_id]

        if session.status != GameStatus.RUNNING:
            return {"game_id": game_id, "error": "Game is not running.", "status": session.status.value}

        if action not in scenario.actions:
            return {
                "game_id": game_id,
                "error": f"Invalid action '{action}'. Choose from: {list(scenario.actions.keys())}",
            }

        # Apply action effects
        action_def = scenario.actions[action]
        effect = dict(action_def.get("effect", {}))
        cost = action_def.get("cost", 0)

        # Special handling for cash-costing actions
        if cost > 0:
            if session.state.get("cash", 0) < cost:
                event = TurnEvent(
                    turn=session.turn,
                    action=action,
                    result=ActionResult.FAILURE,
                    state_delta={},
                    message=f"Not enough cash to {action}. Need ${cost:,}.",
                )
                session.history.append(event)
                return {"game_id": game_id, "result": ActionResult.FAILURE.value, "message": event.message, "state": session.state}
            effect["cash"] = effect.get("cash", 0) - cost

        # Trading floor special logic
        if session.scenario_id in self._scenarios and session.scenario_id == "trading_floor":
            effect = self._trading_effect(action, session.state)

        # Apply effects
        delta: Dict[str, Any] = {}
        for k, v in effect.items():
            if k in session.state and isinstance(session.state[k], (int, float)):
                session.state[k] = round(session.state[k] + v, 2)
                delta[k] = v
            elif k not in session.state:
                session.state[k] = v
                delta[k] = v

        # Prevent negatives where sensible
        for k in ("cash", "rabbits", "wolves", "grass", "energy", "savings"):
            if k in session.state:
                session.state[k] = max(0, session.state[k])

        session.state["turn"] = session.state.get("turn", 0) + 1

        # Ecosystem natural tick
        if "ecosystem" in scenario.title.lower():
            self._ecosystem_tick(session.state)

        # Check win condition
        result = ActionResult.SUCCESS
        message = f"Turn {session.turn}: {action_def.get('description', action)}"

        if scenario.win_condition and scenario.win_condition(session.state):
            session.status = GameStatus.FINISHED
            session.finished_at = time.time()
            result = ActionResult.WIN
            message = f"🎉 Congratulations! You achieved: {scenario.win_condition_desc}"

        # Check game-over conditions
        elif self._is_game_over(session):
            session.status = GameStatus.FINISHED
            session.finished_at = time.time()
            result = ActionResult.GAME_OVER
            message = "Game over! Resources exhausted."

        event = TurnEvent(
            turn=session.turn,
            action=action,
            result=result,
            state_delta=delta,
            message=message,
        )
        session.history.append(event)

        return {
            "game_id": game_id,
            "turn": session.turn,
            "action": action,
            "result": result.value,
            "message": message,
            "state": session.state,
            "status": session.status.value,
        }

    def get_session(self, game_id: str) -> Optional[GameSession]:
        return self._sessions.get(game_id)

    def get_leaderboard(self, scenario_id: str) -> List[Dict[str, Any]]:
        """Return top scores for a scenario."""
        finished = [
            s for s in self._sessions.values()
            if s.scenario_id == scenario_id and s.status == GameStatus.FINISHED
        ]
        # Score = sum of positive numeric state values at end of game
        scored = []
        for s in finished:
            score = sum(v for v in s.state.values() if isinstance(v, (int, float)) and v > 0)
            scored.append({"player_id": s.player_id, "score": round(score, 2), "turns": s.turn})
        return sorted(scored, key=lambda x: x["score"], reverse=True)[:10]

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def dashboard(self) -> Dict[str, Any]:
        active = sum(1 for s in self._sessions.values() if s.status == GameStatus.RUNNING)
        finished = sum(1 for s in self._sessions.values() if s.status == GameStatus.FINISHED)
        return {
            "total_scenarios": len(self._scenarios),
            "total_sessions": len(self._sessions),
            "active_sessions": active,
            "finished_sessions": finished,
        }

    def get_capabilities(self) -> Dict[str, Any]:
        return {
            "bot_id": self.bot_id,
            "name": self.name,
            "category": self.category,
            "builtin_scenarios": len(_SCENARIO_TEMPLATES),
            "categories": [c.value for c in GameCategory],
            "features": [
                "5 built-in simulation scenarios (startup, ecosystem, budget, trading, AI arena)",
                "Custom scenario creation from natural-language prompts",
                "Turn-based game engine with state machine",
                "Leaderboards per scenario",
                "Suitable for teachers, parents, business users, developers",
                "Multi-session support",
            ],
        }

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _is_game_over(self, session: GameSession) -> bool:
        """Return True if the game state represents a terminal failure."""
        state = session.state
        sid = session.scenario_id

        if sid == "ecosystem_sim":
            return (
                state.get("wolves", 1) <= 0
                or state.get("rabbits", 1) <= 0
                or state.get("grass", 1) <= 0
            )
        if sid == "budget_hero":
            return state.get("cash", 1) <= 0 and state.get("savings", 1) <= 0
        if sid == "trading_floor":
            return state.get("cash", 1) <= 0 and state.get("portfolio_value", 0) <= 0
        if sid == "startup_simulator":
            return state.get("cash", 0) < 0
        return False

    def _load_builtin_scenarios(self) -> None:
        for key, template in _SCENARIO_TEMPLATES.items():
            scenario = GameScenario(
                scenario_id=key,
                title=template["title"],
                description=template["description"],
                category=template["category"],
                initial_state=dict(template["initial_state"]),
                actions=dict(template["actions"]),
                win_condition_desc=template["win_condition_desc"],
                win_condition=template["win_condition"],
            )
            self._scenarios[key] = scenario

    def _require_session(self, game_id: str) -> GameSession:
        session = self._sessions.get(game_id)
        if session is None:
            raise KeyError(f"Game session '{game_id}' not found.")
        return session

    def _trading_effect(self, action: str, state: Dict[str, Any]) -> Dict[str, Any]:
        """Stochastic trading outcomes for the trading floor scenario."""
        cash = state.get("cash", 0)
        portfolio = state.get("portfolio_value", 0)
        effect: Dict[str, Any] = {}
        if action == "buy_growth":
            change = self._rng.uniform(-0.15, 0.25)
            invest = min(cash * 0.3, cash)
            gain = round(invest * change, 2)
            effect = {"cash": -invest, "portfolio_value": invest + gain, "trades": 1}
        elif action == "buy_stable":
            change = self._rng.uniform(-0.03, 0.08)
            invest = min(cash * 0.2, cash)
            gain = round(invest * change, 2)
            effect = {"cash": -invest, "portfolio_value": invest + gain, "trades": 1}
        elif action == "sell_all":
            effect = {"cash": portfolio, "portfolio_value": -portfolio, "trades": 1}
        elif action == "research":
            # Small bonus on next trade (simplified: small cash gain)
            effect = {"cash": self._rng.uniform(100, 300)}
        return effect

    def _ecosystem_tick(self, state: Dict[str, Any]) -> None:
        """Natural population dynamics for the ecosystem simulator."""
        wolves = state.get("wolves", 0)
        rabbits = state.get("rabbits", 0)
        grass = state.get("grass", 0)

        # Grass grows slowly
        state["grass"] = max(0, grass + self._rng.randint(5, 15) - wolves * 2)
        # Rabbits eat grass and reproduce
        state["rabbits"] = max(0, rabbits + self._rng.randint(2, 8) - wolves * 3)
        # Wolves decline if rabbits are scarce
        if rabbits < 5:
            state["wolves"] = max(0, wolves - 1)
