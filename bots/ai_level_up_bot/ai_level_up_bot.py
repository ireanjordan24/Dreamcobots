"""
AI Level-Up Bot — Main Entry Point

Composes all five sub-modules into a single unified bot:

1. ai_companies_database  — Global AI tools registry (500–1 000 entries)
2. token_marketplace      — Tokenised billing with 25 % DreamCo markup
3. ai_course_engine       — 10-level DreamCo AI University
4. ai_skill_tree          — Gamified skill and XP progression
5. ai_agents_generator    — Custom AI agent builder

Architecture
------------
    DreamCoBots
    │
    ├── buddybot
    │
    ├── ai_level_up_bot          ← this module
    │     ├── ai_companies_database
    │     ├── ai_course_engine
    │     ├── token_marketplace
    │     ├── ai_skill_tree
    │     └── ai_agents_generator
    │
    ├── trade_titan_bot
    └── hustle_bots

Usage
-----
    from bots.ai_level_up_bot import AILevelUpBot, Tier

    bot = AILevelUpBot(user_id="user_001", tier=Tier.PRO)
    bot.purchase_tokens(50.0)
    bot.complete_module(1, "What is Artificial Intelligence?")
    print(bot.skill_tree_summary())
"""

from __future__ import annotations

from bots.ai_level_up_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_AI_COMPANIES_DATABASE,
    FEATURE_TOKEN_MARKETPLACE,
    FEATURE_COURSE_ENGINE,
    FEATURE_SKILL_TREE,
    FEATURE_AGENTS_GENERATOR,
)
from bots.ai_level_up_bot.ai_companies_database import (
    AICompanyDatabase,
    AITool,
    AICategory,
    PricingModel,
)
from bots.ai_level_up_bot.token_marketplace import (
    TokenMarketplace,
    ServiceType,
    InsufficientTokensError,
    list_all_pricing,
)
from bots.ai_level_up_bot.ai_course_engine import (
    AICourseEngine,
    CourseLevel,
    AICourseEngineError,
)
from bots.ai_level_up_bot.ai_skill_tree import (
    AISkillTree,
    SkillNode,
    SkillTreeError,
)
from bots.ai_level_up_bot.ai_agents_generator import (
    AIAgentsGenerator,
    CustomAgent,
    AgentPurpose,
    AgentsGeneratorError,
    AgentLimitExceededError,
)


class AILevelUpBotError(Exception):
    """General error raised by AILevelUpBot."""


class AILevelUpBot:
    """
    DreamCo AI Level-Up Bot.

    A unified interface over the AI companies database, token marketplace,
    course engine, skill tree, and AI agents generator.

    Parameters
    ----------
    user_id : str
        Unique identifier for the user driving this bot session.
    tier : Tier
        Subscription tier controlling feature access and limits.
        Defaults to FREE.

    Attributes
    ----------
    bot_name : str
        Display name of this bot.
    version : str
        Current version string.
    """

    bot_name: str = "AI Level Up Bot"
    version: str = "1.0"

    def __init__(
        self,
        user_id: str = "guest",
        tier: Tier = Tier.FREE,
    ) -> None:
        self.user_id = user_id
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)

        # ── Sub-modules ────────────────────────────────────────────────────
        self.database = AICompanyDatabase()
        self.marketplace = TokenMarketplace(user_id=user_id, markup=self.config.token_markup)
        self.course_engine = AICourseEngine()
        self.skill_tree = AISkillTree(user_id=user_id)
        self.agents_generator = AIAgentsGenerator(
            user_id=user_id,
            max_agents=self.config.max_agents,
        )

    # ------------------------------------------------------------------
    # Bot lifecycle
    # ------------------------------------------------------------------

    def run(self) -> None:
        """Print a startup message confirming the bot is online."""
        print(f"{self.bot_name} v{self.version} Online — User: {self.user_id} | Tier: {self.config.name}")

    # ------------------------------------------------------------------
    # AI Companies Database delegation
    # ------------------------------------------------------------------

    def teach_ai_tool(self, tool_name: str) -> dict:
        """
        Look up an AI tool and return its learning summary.

        Parameters
        ----------
        tool_name : str
            Name of the tool (case-insensitive).

        Returns
        -------
        dict
            Tool name, capabilities, and base pricing.
        """
        self._require_feature(FEATURE_AI_COMPANIES_DATABASE)
        tool = self.database.get_tool(tool_name)
        return {
            "tool": tool.name,
            "capabilities": tool.capabilities,
            "pricing": tool.token_cost_usd,
            "pricing_model": tool.pricing_model.value,
            "region": tool.region,
            "description": tool.description,
        }

    def search_tools(self, query: str) -> list[dict]:
        """Search the global AI tools database and return matching tools."""
        self._require_feature(FEATURE_AI_COMPANIES_DATABASE)
        return [t.to_dict() for t in self.database.search(query)]

    def tools_by_category(self, category: AICategory) -> list[dict]:
        """Return all tools in the given category."""
        self._require_feature(FEATURE_AI_COMPANIES_DATABASE)
        return [t.to_dict() for t in self.database.filter_by_category(category)]

    # ------------------------------------------------------------------
    # Token Marketplace delegation
    # ------------------------------------------------------------------

    def purchase_tokens(self, amount_usd: float) -> dict:
        """Purchase *amount_usd* worth of tokens (with bundle bonuses applied)."""
        self._require_feature(FEATURE_TOKEN_MARKETPLACE)
        return self.marketplace.purchase_tokens(amount_usd)

    def use_service(self, service: str, units: float = 1.0) -> dict:
        """Consume tokens for *units* of *service* (gpt / image_generation / voice_generation)."""
        self._require_feature(FEATURE_TOKEN_MARKETPLACE)
        return self.marketplace.use_service(service, units)

    def token_balance(self) -> float:
        """Return the current token balance in USD."""
        return self.marketplace.balance_usd

    def billing_summary(self) -> dict:
        """Return a high-level billing report."""
        self._require_feature(FEATURE_TOKEN_MARKETPLACE)
        return self.marketplace.billing_summary()

    def pricing_overview(self) -> list[dict]:
        """Return the DreamCo pricing for all services (with markup applied)."""
        return [
            {
                "service": p.service.value,
                "base_cost_usd": p.base_cost_usd,
                "markup_pct": round(p.markup * 100, 1),
                "dreamco_price_usd": p.dreamco_price_usd,
                "profit_per_unit_usd": p.profit_per_unit,
            }
            for p in list_all_pricing(self.config.token_markup)
        ]

    # ------------------------------------------------------------------
    # Course Engine delegation
    # ------------------------------------------------------------------

    def get_course_level(self, level_number: int) -> dict:
        """Return details for the given course level (1–10)."""
        self._require_feature(FEATURE_COURSE_ENGINE)
        level = self.course_engine.get_level(level_number)
        return {
            "level_number": level.level_number,
            "title": level.title,
            "description": level.description,
            "certificate_name": level.certificate_name,
            "total_xp": level.total_xp,
            "total_duration_minutes": level.total_duration_minutes,
            "modules": [
                {
                    "title": m.title,
                    "description": m.description,
                    "teaching_mode": m.teaching_mode.value,
                    "duration_minutes": m.duration_minutes,
                    "xp_reward": m.xp_reward,
                }
                for m in level.modules
            ],
        }

    def complete_module(self, level_number: int, module_title: str) -> dict:
        """
        Mark a course module as completed and award XP to the skill tree.

        Returns a combined result including course completion and XP awarded.
        """
        self._require_feature(FEATURE_COURSE_ENGINE)

        if not self.course_engine.is_level_unlocked(
            self.user_id, level_number, self.config.max_course_level
        ):
            raise AILevelUpBotError(
                f"Level {level_number} is not unlocked for your subscription tier "
                f"({self.config.name}). Upgrade to access higher levels."
            )

        course_result = self.course_engine.complete_module(
            self.user_id, level_number, module_title
        )

        # Award XP to the skill tree
        xp_gained = course_result.get("xp_awarded", 0)
        skill_result = {}
        if xp_gained > 0 and self.config.has_feature(FEATURE_SKILL_TREE):
            skill_result = self.skill_tree.award_xp(xp_gained)

        return {**course_result, "skill_tree": skill_result}

    def course_progress(self) -> dict:
        """Return the user's progress across all 10 course levels."""
        self._require_feature(FEATURE_COURSE_ENGINE)
        return self.course_engine.get_user_progress(self.user_id)

    # ------------------------------------------------------------------
    # Skill Tree delegation
    # ------------------------------------------------------------------

    def award_xp(self, amount: int) -> dict:
        """Directly award *amount* XP to the user's skill tree."""
        self._require_feature(FEATURE_SKILL_TREE)
        return self.skill_tree.award_xp(amount)

    def unlock_skill(self, skill_id: str) -> dict:
        """Unlock the skill identified by *skill_id*."""
        self._require_feature(FEATURE_SKILL_TREE)
        return self.skill_tree.unlock_skill(skill_id)

    def skill_tree_summary(self) -> dict:
        """Return a summary of the user's gamification progress."""
        self._require_feature(FEATURE_SKILL_TREE)
        return self.skill_tree.skill_tree_summary()

    # ------------------------------------------------------------------
    # Agents Generator delegation
    # ------------------------------------------------------------------

    def create_agent(
        self,
        name: str,
        purpose: str,
        tools: list[str] | None = None,
        system_prompt: str = "",
    ) -> dict:
        """
        Create a new custom AI agent.

        Parameters
        ----------
        name : str
            Display name for the agent.
        purpose : str
            Agent purpose (e.g. 'Marketing', 'Real Estate').
        tools : list[str] | None
            Tool names to include; defaults to purpose template.
        system_prompt : str
            Custom system prompt for the agent.

        Returns
        -------
        dict
            Serialised agent dictionary.
        """
        self._require_feature(FEATURE_AGENTS_GENERATOR)
        agent = self.agents_generator.create_agent(
            name=name, purpose=purpose, tools=tools, system_prompt=system_prompt
        )
        return agent.to_dict()

    def list_agents(self) -> list[dict]:
        """Return all non-archived agents for this user."""
        self._require_feature(FEATURE_AGENTS_GENERATOR)
        return [a.to_dict() for a in self.agents_generator.list_agents()]

    def activate_agent(self, agent_id: str) -> dict:
        """Activate a DRAFT or PAUSED agent."""
        self._require_feature(FEATURE_AGENTS_GENERATOR)
        return self.agents_generator.activate_agent(agent_id)

    def run_agent_task(self, agent_id: str, task: str) -> dict:
        """Run a task through an ACTIVE agent."""
        self._require_feature(FEATURE_AGENTS_GENERATOR)
        return self.agents_generator.run_task(agent_id, task)

    # ------------------------------------------------------------------
    # Tier & upgrade info
    # ------------------------------------------------------------------

    def tier_info(self) -> dict:
        """Return the current tier configuration."""
        return {
            "tier": self.tier.value,
            "name": self.config.name,
            "price_usd_monthly": self.config.price_usd_monthly,
            "max_course_level": self.config.max_course_level,
            "max_agents": self.config.max_agents,
            "features": self.config.features,
            "support_level": self.config.support_level,
        }

    def upgrade_info(self) -> dict | None:
        """Return the next tier info, or None if already on ENTERPRISE."""
        next_config = get_upgrade_path(self.tier)
        if next_config is None:
            return None
        return {
            "tier": next_config.tier.value,
            "name": next_config.name,
            "price_usd_monthly": next_config.price_usd_monthly,
            "max_course_level": next_config.max_course_level,
            "max_agents": next_config.max_agents,
        }

    # ------------------------------------------------------------------
    # BuddyAI-compatible chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str) -> dict:
        """
        Handle a plain-text *message* and return a structured response.

        Supports: tier info, tool lookup, pricing overview, course listing,
        skill tree status, agent listing.
        """
        msg = message.lower().strip()

        if "upgrade" in msg:
            info = self.upgrade_info()
            if info:
                return self._response(
                    f"Upgrade to {info['name']} for ${info['price_usd_monthly']}/mo "
                    f"to unlock up to Level {info['max_course_level']} and "
                    f"{info['max_agents'] or 'unlimited'} agents."
                )
            return self._response("You're already on the top-tier plan. Keep building! 🚀")

        if "tier" in msg or "plan" in msg or "subscription" in msg:
            return self._response(
                f"You are on the {self.config.name} plan "
                f"(${self.config.price_usd_monthly}/mo). "
                f"Course levels unlocked: 1–{self.config.max_course_level}."
            )

        if "balance" in msg:
            return self._response(f"Token balance: ${self.marketplace.balance_usd:.4f}")

        if "pricing" in msg or "token" in msg:
            prices = self.pricing_overview()
            lines = [f"  • {p['service']}: ${p['dreamco_price_usd']} (base ${p['base_cost_usd']})" for p in prices]
            return self._response("DreamCo Token Pricing:\n" + "\n".join(lines))

        if "course" in msg or "level" in msg:
            levels = self.course_engine.list_levels()
            lines = [f"  Level {lv.level_number}: {lv.title}" for lv in levels]
            return self._response("DreamCo AI University Levels:\n" + "\n".join(lines))

        if "skill" in msg or "xp" in msg:
            summary = self.skill_tree_summary()
            return self._response(
                f"Skill Tree: Level {summary['level']} | XP {summary['xp']} | "
                f"Skills {summary['skills_unlocked']}/{summary['total_skills']} | "
                f"Token Discount {summary['token_discount_pct']}%"
            )

        if "agent" in msg:
            agents = self.list_agents()
            if agents:
                names = ", ".join(a["name"] for a in agents)
                return self._response(f"Your agents: {names}")
            return self._response("No agents yet. Create one with create_agent()!")

        if "balance" in msg:
            return self._response(f"Token balance: ${self.marketplace.balance_usd:.4f}")

        return self._response(
            f"Welcome to {self.bot_name}! I can help with: "
            "AI tools, token pricing, course levels, skill tree, and AI agents. "
            "What would you like to explore?"
        )

    # ------------------------------------------------------------------
    # Internal
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        """Raise AILevelUpBotError if *feature* is not available on the current tier."""
        if not self.config.has_feature(feature):
            upgrade = get_upgrade_path(self.tier)
            hint = (
                f" Upgrade to {upgrade.name} to unlock this feature."
                if upgrade else ""
            )
            raise AILevelUpBotError(
                f"Feature '{feature}' is not available on the {self.config.name} tier.{hint}"
            )

    @staticmethod
    def _response(message: str) -> dict:
        """Wrap *message* in a standard BuddyAI-compatible response dict."""
        return {"bot": "AI Level Up Bot", "message": message}
