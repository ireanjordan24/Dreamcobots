"""
AI Agents Generator — Custom AI Agent Builder

Allows users to define, configure, and manage custom AI agents by specifying
a purpose (e.g. Marketing, Real Estate) and selecting relevant tools from
the global AI companies database (GPT, Midjourney, ElevenLabs, etc.).

Example agent types
-------------------
- Marketing Agent  : GPT + DALL-E + ElevenLabs
- Real Estate Agent: GPT + Perplexity AI + custom data
- Coding Agent     : GitHub Copilot + Replit + DeepMind AlphaCode
- Content Agent    : GPT + Midjourney + Synthesia

Usage
-----
    from bots.ai_level_up_bot.ai_agents_generator import AIAgentsGenerator

    generator = AIAgentsGenerator(user_id="user_001", max_agents=5)
    agent = generator.create_agent(
        name="My Marketing Bot",
        purpose="Marketing",
        tools=["OpenAI", "Midjourney", "ElevenLabs"],
    )
    print(agent.agent_id, agent.purpose)
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class AgentPurpose(Enum):
    """Pre-defined agent purpose categories."""

    MARKETING = "Marketing"
    REAL_ESTATE = "Real Estate"
    CODING = "Coding"
    CONTENT_CREATION = "Content Creation"
    CUSTOMER_SUPPORT = "Customer Support"
    RESEARCH = "Research"
    EDUCATION = "Education"
    FINANCE = "Finance"
    HEALTH = "Health"
    LEGAL = "Legal"
    E_COMMERCE = "E-Commerce"
    SOCIAL_MEDIA = "Social Media"
    CUSTOM = "Custom"


class AgentStatus(Enum):
    """Lifecycle status of a custom AI agent."""

    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


# ---------------------------------------------------------------------------
# Pre-defined tool templates per purpose
# ---------------------------------------------------------------------------

# Suggested default tool sets keyed by AgentPurpose value.
PURPOSE_TOOL_TEMPLATES: dict[str, list[str]] = {
    AgentPurpose.MARKETING.value: ["OpenAI", "Midjourney", "ElevenLabs", "Runway"],
    AgentPurpose.REAL_ESTATE.value: ["OpenAI", "Perplexity AI", "DALL-E"],
    AgentPurpose.CODING.value: ["GitHub Copilot", "Replit Ghostwriter", "DeepMind AlphaCode", "OpenAI"],
    AgentPurpose.CONTENT_CREATION.value: ["OpenAI", "Midjourney", "Synthesia", "Suno AI"],
    AgentPurpose.CUSTOMER_SUPPORT.value: ["OpenAI", "Anthropic Claude", "ElevenLabs"],
    AgentPurpose.RESEARCH.value: ["Perplexity AI", "Elicit", "OpenAI", "Anthropic Claude"],
    AgentPurpose.EDUCATION.value: ["OpenAI", "Anthropic Claude", "Perplexity AI", "ElevenLabs"],
    AgentPurpose.FINANCE.value: ["OpenAI", "Perplexity AI", "Anthropic Claude"],
    AgentPurpose.HEALTH.value: ["OpenAI", "Anthropic Claude", "Perplexity AI"],
    AgentPurpose.LEGAL.value: ["OpenAI", "Anthropic Claude", "Elicit"],
    AgentPurpose.E_COMMERCE.value: ["OpenAI", "Midjourney", "DALL-E", "Alibaba Tongyi Qianwen"],
    AgentPurpose.SOCIAL_MEDIA.value: ["OpenAI", "Midjourney", "Suno AI", "Pika Labs"],
    AgentPurpose.CUSTOM.value: [],
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class CustomAgent:
    """
    A user-defined custom AI agent.

    Attributes
    ----------
    agent_id : str
        Unique identifier.
    user_id : str
        Owner of this agent.
    name : str
        Display name.
    purpose : str
        The agent's primary purpose (AgentPurpose value or custom string).
    tools : list[str]
        AI tool names selected for this agent.
    system_prompt : str
        The system-level prompt defining the agent's behaviour.
    status : AgentStatus
        Current lifecycle status.
    tasks_run : int
        Number of tasks this agent has executed.
    created_at : str
        ISO 8601 creation timestamp.
    updated_at : str
        ISO 8601 last-updated timestamp.
    metadata : dict
        Arbitrary key-value metadata.
    """

    agent_id: str
    user_id: str
    name: str
    purpose: str
    tools: list[str]
    system_prompt: str = ""
    status: AgentStatus = AgentStatus.DRAFT
    tasks_run: int = 0
    created_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    updated_at: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
    metadata: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Serialise the agent to a plain dictionary."""
        return {
            "agent_id": self.agent_id,
            "user_id": self.user_id,
            "name": self.name,
            "purpose": self.purpose,
            "tools": self.tools,
            "system_prompt": self.system_prompt,
            "status": self.status.value,
            "tasks_run": self.tasks_run,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "metadata": self.metadata,
        }


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class AgentsGeneratorError(Exception):
    """General error raised by AIAgentsGenerator."""


class AgentLimitExceededError(AgentsGeneratorError):
    """Raised when the user's agent creation cap is reached."""


class AgentNotFoundError(AgentsGeneratorError):
    """Raised when an agent with the given ID is not found."""


# ---------------------------------------------------------------------------
# AI Agents Generator
# ---------------------------------------------------------------------------

class AIAgentsGenerator:
    """
    Framework for creating and managing custom AI agents.

    Parameters
    ----------
    user_id : str
        Unique identifier of the owning user.
    max_agents : int | None
        Maximum number of agents this user may create.  ``None`` = unlimited.

    Methods
    -------
    create_agent(name, purpose, tools, system_prompt, metadata)
        Create and register a new custom agent.
    get_agent(agent_id)
        Retrieve an agent by its ID.
    list_agents(status)
        List agents, optionally filtered by status.
    update_agent(agent_id, **kwargs)
        Update mutable fields of an existing agent.
    activate_agent(agent_id)
        Transition an agent to ACTIVE status.
    pause_agent(agent_id)
        Pause a running agent.
    archive_agent(agent_id)
        Archive an agent (cannot be reactivated).
    run_task(agent_id, task_description)
        Simulate running a task through an agent.
    get_purpose_template(purpose)
        Return the default tool list for a given purpose.
    """

    def __init__(
        self,
        user_id: str,
        max_agents: Optional[int] = 5,
    ) -> None:
        self.user_id = user_id
        self.max_agents = max_agents
        self._agents: dict[str, CustomAgent] = {}

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def create_agent(
        self,
        name: str,
        purpose: str,
        tools: Optional[list[str]] = None,
        system_prompt: str = "",
        metadata: Optional[dict] = None,
    ) -> CustomAgent:
        """
        Create a new custom AI agent.

        Parameters
        ----------
        name : str
            Display name for the agent.
        purpose : str
            Purpose category (use AgentPurpose values or any custom string).
        tools : list[str] | None
            AI tool names to include.  If None, defaults to the purpose template.
        system_prompt : str
            Instructions that define the agent's behaviour.
        metadata : dict | None
            Additional key-value data.

        Returns
        -------
        CustomAgent
            The newly created agent.

        Raises
        ------
        AgentLimitExceededError
            If the user has reached their maximum allowed agent count.
        """
        active_count = sum(
            1 for a in self._agents.values()
            if a.status != AgentStatus.ARCHIVED
        )
        if self.max_agents is not None and active_count >= self.max_agents:
            raise AgentLimitExceededError(
                f"Agent limit reached ({self.max_agents}). "
                "Archive an existing agent or upgrade your subscription."
            )

        if tools is None:
            tools = self.get_purpose_template(purpose)

        if not system_prompt:
            system_prompt = self._default_system_prompt(name, purpose, tools)

        agent = CustomAgent(
            agent_id=str(uuid.uuid4()),
            user_id=self.user_id,
            name=name,
            purpose=purpose,
            tools=list(tools),
            system_prompt=system_prompt,
            metadata=metadata or {},
        )
        self._agents[agent.agent_id] = agent
        return agent

    def get_agent(self, agent_id: str) -> CustomAgent:
        """
        Return the agent with *agent_id*.

        Raises
        ------
        AgentNotFoundError
            If no matching agent is found.
        """
        if agent_id not in self._agents:
            raise AgentNotFoundError(f"Agent '{agent_id}' not found.")
        return self._agents[agent_id]

    def list_agents(
        self,
        status: Optional[AgentStatus] = None,
    ) -> list[CustomAgent]:
        """Return all agents, optionally filtered by *status*."""
        agents = list(self._agents.values())
        if status is not None:
            agents = [a for a in agents if a.status == status]
        return agents

    def update_agent(self, agent_id: str, **kwargs) -> CustomAgent:
        """
        Update mutable fields of an existing agent.

        Updatable fields: ``name``, ``tools``, ``system_prompt``, ``metadata``.

        Returns
        -------
        CustomAgent
            The updated agent.
        """
        agent = self.get_agent(agent_id)
        allowed = {"name", "tools", "system_prompt", "metadata"}
        for key, value in kwargs.items():
            if key not in allowed:
                raise AgentsGeneratorError(f"Field '{key}' cannot be updated.")
            setattr(agent, key, value)
        agent.updated_at = datetime.now(timezone.utc).isoformat()
        return agent

    # ------------------------------------------------------------------
    # Status transitions
    # ------------------------------------------------------------------

    def activate_agent(self, agent_id: str) -> dict:
        """Transition *agent_id* from DRAFT/PAUSED to ACTIVE."""
        agent = self.get_agent(agent_id)
        if agent.status == AgentStatus.ARCHIVED:
            raise AgentsGeneratorError("Archived agents cannot be reactivated.")
        agent.status = AgentStatus.ACTIVE
        agent.updated_at = datetime.now(timezone.utc).isoformat()
        return {"agent_id": agent_id, "status": agent.status.value}

    def pause_agent(self, agent_id: str) -> dict:
        """Pause an ACTIVE agent."""
        agent = self.get_agent(agent_id)
        if agent.status != AgentStatus.ACTIVE:
            raise AgentsGeneratorError(
                f"Only ACTIVE agents can be paused (current: {agent.status.value})."
            )
        agent.status = AgentStatus.PAUSED
        agent.updated_at = datetime.now(timezone.utc).isoformat()
        return {"agent_id": agent_id, "status": agent.status.value}

    def archive_agent(self, agent_id: str) -> dict:
        """Archive an agent.  This action cannot be reversed."""
        agent = self.get_agent(agent_id)
        agent.status = AgentStatus.ARCHIVED
        agent.updated_at = datetime.now(timezone.utc).isoformat()
        return {"agent_id": agent_id, "status": agent.status.value}

    # ------------------------------------------------------------------
    # Task simulation
    # ------------------------------------------------------------------

    def run_task(self, agent_id: str, task_description: str) -> dict:
        """
        Simulate running *task_description* through the given agent.

        The agent must be in ACTIVE status.

        Returns
        -------
        dict
            Task execution summary.
        """
        agent = self.get_agent(agent_id)
        if agent.status != AgentStatus.ACTIVE:
            raise AgentsGeneratorError(
                f"Agent '{agent.name}' must be ACTIVE to run tasks "
                f"(current status: {agent.status.value})."
            )
        agent.tasks_run += 1
        agent.updated_at = datetime.now(timezone.utc).isoformat()
        return {
            "agent_id": agent_id,
            "agent_name": agent.name,
            "task": task_description,
            "tools_used": agent.tools,
            "tasks_run_total": agent.tasks_run,
            "status": "completed",
        }

    # ------------------------------------------------------------------
    # Templates & helpers
    # ------------------------------------------------------------------

    def get_purpose_template(self, purpose: str) -> list[str]:
        """
        Return the default tool list for *purpose*.

        Falls back to an empty list for unknown purposes.
        """
        return list(PURPOSE_TOOL_TEMPLATES.get(purpose, []))

    def list_purposes(self) -> list[str]:
        """Return all pre-defined agent purpose values."""
        return [p.value for p in AgentPurpose]

    def agent_count(self) -> int:
        """Return the number of non-archived agents."""
        return sum(1 for a in self._agents.values() if a.status != AgentStatus.ARCHIVED)

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _default_system_prompt(
        self,
        name: str,
        purpose: str,
        tools: list[str],
    ) -> str:
        """Generate a sensible default system prompt for the agent."""
        tool_list = ", ".join(tools) if tools else "general AI tools"
        return (
            f"You are {name}, a specialised AI agent focused on {purpose}. "
            f"You have access to the following tools: {tool_list}. "
            "Complete tasks efficiently, accurately, and ethically."
        )
