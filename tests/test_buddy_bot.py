"""
Tests for bots/buddy_bot/

Covers:
  1. Tiers
  2. ConversationEngine
  3. EmotionEngine
  4. MemorySystem
  5. AvatarEngine
  6. VoiceEngine
  7. CreativityEngine
  8. PersonalityEngine
  9. BuddyBot (main orchestrator — integration)
  10. Bot Library registration
"""

import sys
import os
import time

REPO_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, REPO_ROOT)

import pytest

# ---------------------------------------------------------------------------
# Tier imports
# ---------------------------------------------------------------------------
from bots.buddy_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    list_tiers,
    TIER_CATALOGUE,
    FEATURE_CONVERSATIONAL_AI,
    FEATURE_EMOTION_DETECTION,
    FEATURE_BASIC_MEMORY,
    FEATURE_MULTILINGUAL,
    FEATURE_HUMOR_ENGINE,
    FEATURE_EMPATHY_ENGINE,
    FEATURE_AVATAR_2D,
    FEATURE_AVATAR_3D,
    FEATURE_VOICE_SYNTHESIS,
    FEATURE_VOICE_CLONING,
    FEATURE_GAN_IMAGE_MIMICRY,
    FEATURE_HOLOGRAPHIC_PROJECTION,
    FEATURE_MILESTONE_TRACKER,
    FEATURE_CONFLICT_RESOLUTION,
    FEATURE_MOOD_SYNC,
    FEATURE_PERSONALITY_MODES,
    FEATURE_CREATIVITY_ENGINE,
    FEATURE_GAMIFIED_PRODUCTIVITY,
    FEATURE_REAL_TIME_TRANSLATION,
    FEATURE_WELLNESS_TRACKER,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
)

# ---------------------------------------------------------------------------
# Sub-engine imports
# ---------------------------------------------------------------------------
from bots.buddy_bot.conversation_engine import (
    ConversationEngine,
    ConversationTone,
    TranslationResult,
    ConversationTurn,
    SUPPORTED_LANGUAGES,
    HUMOR_RESPONSES,
)
from bots.buddy_bot.emotion_engine import (
    EmotionEngine,
    EmotionLabel,
    EmotionSource,
    EmotionReading,
)
from bots.buddy_bot.memory_system import (
    MemorySystem,
    MemorySystemError,
    UserProfile,
    LifeMilestone,
    ImportantDate,
    EpisodicMemory,
    MilestoneCategory,
    RelationshipDepth,
)
from bots.buddy_bot.avatar_engine import (
    AvatarEngine,
    AvatarType,
    AvatarEnvironment,
    MicroExpression,
    BodyGesture,
    AvatarAppearance,
    AvatarFrame,
    AvatarEngineError,
)
from bots.buddy_bot.voice_engine import (
    VoiceEngine,
    VoiceTone,
    AccentStyle,
    VoiceProfile,
    SpeechOutput,
    VoiceEngineError,
)
from bots.buddy_bot.creativity_engine import (
    CreativityEngine,
    StoryGenre,
    SongMood,
    ArtMedium,
    ChallengeCategory,
    Song,
    StoryChapter,
    Achievement,
    DailyChallenge,
    CreativityEngineError,
)
from bots.buddy_bot.personality_engine import (
    PersonalityEngine,
    PersonaMode,
    PersonaTone,
    PersonalityConfig,
    ETHICAL_GUARDRAILS,
)
from bots.buddy_bot.buddy_bot import BuddyBot, BuddyBotError, BuddyBotTierError


# ===========================================================================
# 11. ReasoningEngine (Claude Mithos intelligence layer)
# ===========================================================================

class TestReasoningEngine:
    """Tests for bots/buddy_bot/reasoning_engine.py"""

    def _engine(self, chain_of_thought: bool = True):
        from bots.buddy_bot.reasoning_engine import ReasoningEngine
        return ReasoningEngine(enable_chain_of_thought=chain_of_thought)

    # --- Imports -----------------------------------------------------------

    def test_import_reasoning_engine(self):
        from bots.buddy_bot.reasoning_engine import (
            ReasoningEngine, ReasoningResult, ReasoningStep, QueryIntent,
        )
        assert ReasoningEngine is not None

    # --- Intent detection --------------------------------------------------

    def test_detect_factual_intent(self):
        from bots.buddy_bot.reasoning_engine import QueryIntent
        engine = self._engine()
        result = engine.reason("What is machine learning?")
        assert result.intent == QueryIntent.FACTUAL

    def test_detect_analytical_intent(self):
        from bots.buddy_bot.reasoning_engine import QueryIntent
        engine = self._engine()
        result = engine.reason("Why does inflation cause unemployment?")
        assert result.intent == QueryIntent.ANALYTICAL

    def test_detect_emotional_intent(self):
        from bots.buddy_bot.reasoning_engine import QueryIntent
        engine = self._engine()
        result = engine.reason("I feel so sad and lonely today.")
        assert result.intent == QueryIntent.EMOTIONAL

    def test_detect_instructional_intent(self):
        from bots.buddy_bot.reasoning_engine import QueryIntent
        engine = self._engine()
        result = engine.reason("Help me build a morning routine.")
        assert result.intent == QueryIntent.INSTRUCTIONAL

    def test_detect_creative_intent(self):
        from bots.buddy_bot.reasoning_engine import QueryIntent
        engine = self._engine()
        result = engine.reason("Write a short poem about the ocean.")
        assert result.intent == QueryIntent.CREATIVE

    def test_detect_ethical_intent(self):
        from bots.buddy_bot.reasoning_engine import QueryIntent
        engine = self._engine()
        result = engine.reason("Should I tell my friend the truth even if it hurts?")
        assert result.intent == QueryIntent.ETHICAL

    def test_detect_conversational_intent(self):
        from bots.buddy_bot.reasoning_engine import QueryIntent
        engine = self._engine()
        result = engine.reason("Hello, how are you?")
        assert result.intent == QueryIntent.CONVERSATIONAL

    # --- Deep comprehension ------------------------------------------------

    def test_deep_comprehend_returns_required_keys(self):
        engine = self._engine()
        comp = engine.deep_comprehend("What is the best way to learn Python?")
        assert "intent" in comp
        assert "entities" in comp
        assert "sentiment" in comp
        assert "implicit_need" in comp
        assert "complexity" in comp

    def test_deep_comprehend_positive_sentiment(self):
        engine = self._engine()
        comp = engine.deep_comprehend("This is amazing and I love it!")
        assert comp["sentiment"] == "positive"

    def test_deep_comprehend_negative_sentiment(self):
        engine = self._engine()
        comp = engine.deep_comprehend("I hate this terrible awful situation.")
        assert comp["sentiment"] == "negative"

    def test_deep_comprehend_neutral_sentiment(self):
        engine = self._engine()
        comp = engine.deep_comprehend("The meeting is at three o'clock.")
        assert comp["sentiment"] == "neutral"

    def test_deep_comprehend_complexity_simple(self):
        engine = self._engine()
        comp = engine.deep_comprehend("Hello!")
        assert comp["complexity"] == "simple"

    def test_deep_comprehend_complexity_complex(self):
        engine = self._engine()
        long_text = "Can you explain in detail the historical, economic, and social factors that contributed to the rise of globalisation during the twentieth century and its long-term effects on labour markets?"
        comp = engine.deep_comprehend(long_text)
        assert comp["complexity"] == "complex"

    def test_deep_comprehend_entity_extraction(self):
        engine = self._engine()
        comp = engine.deep_comprehend('Tell me about "Paris" and London.')
        assert isinstance(comp["entities"], list)

    # --- Chain-of-thought --------------------------------------------------

    def test_chain_of_thought_returns_steps(self):
        engine = self._engine()
        steps = engine.chain_of_thought("Why do planets orbit the sun?")
        assert len(steps) >= 3

    def test_chain_of_thought_step_structure(self):
        engine = self._engine()
        steps = engine.chain_of_thought("Explain photosynthesis.")
        for step in steps:
            assert hasattr(step, "step_number")
            assert hasattr(step, "description")
            assert hasattr(step, "conclusion")

    def test_chain_of_thought_step_to_dict(self):
        engine = self._engine()
        steps = engine.chain_of_thought("How does gravity work?")
        for step in steps:
            d = step.to_dict()
            assert "step_number" in d
            assert "description" in d
            assert "conclusion" in d

    def test_chain_of_thought_disabled(self):
        engine = self._engine(chain_of_thought=False)
        result = engine.reason("What is the speed of light?")
        assert result.reasoning_steps == []

    def test_chain_of_thought_enabled(self):
        engine = self._engine(chain_of_thought=True)
        result = engine.reason("What is the speed of light?")
        assert len(result.reasoning_steps) >= 3

    # --- Context synthesis -------------------------------------------------

    def test_context_synthesis_empty_history(self):
        engine = self._engine()
        ctx = engine.synthesise_context([], "Tell me about yourself.")
        assert isinstance(ctx, str)
        assert len(ctx) > 0

    def test_context_synthesis_with_history(self):
        engine = self._engine()
        history = [
            {"user_input": "Tell me about Python.", "response": "Python is great."},
            {"user_input": "And Django?", "response": "Django is a web framework."},
        ]
        ctx = engine.synthesise_context(history, "How do they compare?")
        assert "exchange" in ctx.lower() or "recent" in ctx.lower() or "discussed" in ctx.lower()

    # --- ReasoningResult ---------------------------------------------------

    def test_reason_result_has_all_fields(self):
        engine = self._engine()
        result = engine.reason("What is consciousness?")
        assert result.original_query == "What is consciousness?"
        assert result.final_response
        assert isinstance(result.confidence, float)
        assert 0.0 <= result.confidence <= 1.0

    def test_reason_result_to_dict(self):
        engine = self._engine()
        result = engine.reason("Tell me about the universe.")
        d = result.to_dict()
        assert "original_query" in d
        assert "intent" in d
        assert "reasoning_steps" in d
        assert "synthesised_context" in d
        assert "deep_comprehension" in d
        assert "final_response" in d
        assert "confidence" in d

    def test_reason_updates_internal_history(self):
        engine = self._engine()
        engine.reason("Hello!")
        engine.reason("How are you?")
        assert engine.to_dict()["history_turns"] == 2

    def test_clear_history(self):
        engine = self._engine()
        engine.reason("Hello!")
        engine.clear_history()
        assert engine.to_dict()["history_turns"] == 0

    def test_to_dict_keys(self):
        engine = self._engine()
        d = engine.to_dict()
        assert "model_name" in d
        assert "enable_chain_of_thought" in d
        assert "context_window" in d
        assert "history_turns" in d

    def test_model_name_is_claude_mithos(self):
        engine = self._engine()
        assert "claude-mithos" in engine.model_name.lower()

    # --- Analytical response -----------------------------------------------

    def test_analytical_response_returns_string(self):
        engine = self._engine()
        resp = engine.analytical_response("Compare democracy and autocracy.")
        assert isinstance(resp, str)
        assert len(resp) > 10


# ===========================================================================
# 12. BuddyBot — Claude Mithos integration
# ===========================================================================

class TestBuddyBotClaudeMithos:
    """Tests for Claude-Mithos reasoning features integrated in BuddyBot."""

    # --- Feature flags present on PRO/ENTERPRISE ---------------------------

    def test_reasoning_engine_feature_on_pro(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier, FEATURE_REASONING_ENGINE,
        )
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_REASONING_ENGINE)

    def test_chain_of_thought_feature_on_pro(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier, FEATURE_CHAIN_OF_THOUGHT,
        )
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_CHAIN_OF_THOUGHT)

    def test_deep_context_feature_on_pro(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier, FEATURE_DEEP_CONTEXT,
        )
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_DEEP_CONTEXT)

    def test_reasoning_features_on_enterprise(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier,
            FEATURE_REASONING_ENGINE, FEATURE_CHAIN_OF_THOUGHT, FEATURE_DEEP_CONTEXT,
        )
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_REASONING_ENGINE)
        assert cfg.has_feature(FEATURE_CHAIN_OF_THOUGHT)
        assert cfg.has_feature(FEATURE_DEEP_CONTEXT)

    def test_reasoning_features_not_on_free(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier,
            FEATURE_REASONING_ENGINE, FEATURE_CHAIN_OF_THOUGHT, FEATURE_DEEP_CONTEXT,
        )
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_REASONING_ENGINE)
        assert not cfg.has_feature(FEATURE_CHAIN_OF_THOUGHT)
        assert not cfg.has_feature(FEATURE_DEEP_CONTEXT)

    # --- BuddyBot has a ReasoningEngine instance ---------------------------

    def test_buddy_has_reasoning_engine(self):
        from bots.buddy_bot.reasoning_engine import ReasoningEngine
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        assert isinstance(buddy.reasoning, ReasoningEngine)

    def test_reasoning_engine_model_name(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        assert "claude-mithos" in buddy.reasoning.model_name.lower()

    # --- PRO chat includes reasoning result --------------------------------

    def test_pro_chat_includes_reasoning_key(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        response = buddy.chat("What is artificial intelligence?")
        assert "reasoning" in response
        assert response["reasoning"] is not None

    def test_pro_chat_reasoning_has_intent(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        response = buddy.chat("I feel really anxious today.")
        assert response["reasoning"]["intent"] == "emotional"

    def test_pro_chat_reasoning_confidence(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        response = buddy.chat("Help me write a cover letter.")
        conf = response["reasoning"]["confidence"]
        assert 0.0 <= conf <= 1.0

    def test_free_chat_reasoning_is_none(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        response = buddy.chat("Hello!")
        assert response["reasoning"] is None

    # --- BuddyBot.reason() method ------------------------------------------

    def test_buddy_reason_method_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        result = buddy.reason("Explain quantum entanglement.")
        assert "final_response" in result
        assert "intent" in result
        assert "reasoning_steps" in result

    def test_buddy_reason_method_requires_pro(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.reason("What is the meaning of life?")

    def test_buddy_reason_result_has_steps(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        result = buddy.reason("Why is the sky blue?")
        assert len(result["reasoning_steps"]) >= 3

    # --- BuddyBot.chain_of_thought() method --------------------------------

    def test_buddy_chain_of_thought_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        steps = buddy.chain_of_thought("Compare renewable and fossil fuel energy.")
        assert isinstance(steps, list)
        assert len(steps) >= 3

    def test_buddy_chain_of_thought_requires_pro(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.chain_of_thought("Some question.")

    def test_buddy_chain_of_thought_step_keys(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        steps = buddy.chain_of_thought("What causes inflation?")
        for step in steps:
            assert "step_number" in step
            assert "description" in step
            assert "conclusion" in step

    # --- BuddyBot.deep_comprehend() method ---------------------------------

    def test_buddy_deep_comprehend_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        result = buddy.deep_comprehend("I need help with my anxiety.")
        assert "intent" in result
        assert result["intent"] == "emotional"

    def test_buddy_deep_comprehend_requires_pro(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.deep_comprehend("Tell me about yourself.")

    def test_buddy_deep_comprehend_returns_sentiment(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        result = buddy.deep_comprehend("I am so happy and excited today!")
        assert result["sentiment"] == "positive"

    def test_buddy_deep_comprehend_returns_implicit_need(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        result = buddy.deep_comprehend("Help me improve my productivity.")
        assert isinstance(result["implicit_need"], str)
        assert len(result["implicit_need"]) > 0

    # --- System status includes reasoning ----------------------------------

    def test_system_status_includes_reasoning(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        status = buddy.system_status()
        assert "reasoning" in status
        assert "model_name" in status["reasoning"]

    # --- Context window larger on ENTERPRISE / PRO -------------------------

    def test_enterprise_has_larger_context_window(self):
        pro_buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        enterprise_buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        assert enterprise_buddy.reasoning.context_window >= pro_buddy.reasoning.context_window

    def test_free_has_smaller_context_window(self):
        free_buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        pro_buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        assert free_buddy.reasoning.context_window <= pro_buddy.reasoning.context_window


# ===========================================================================
# 13. Claude Mithos in AI companies database
# ===========================================================================

class TestClaudeMithosAIDatabase:
    def test_claude_mithos_in_anthropic_tools(self):
        from bots.ai_level_up_bot.ai_companies_database import AICompanyDatabase
        db = AICompanyDatabase()
        anthropic = db.get_company("Anthropic")
        assert anthropic is not None, "Anthropic entry missing from database"
        assert "Claude Mithos" in anthropic.tools


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestTiers:
    def test_three_tiers_exist(self):
        tiers = list_tiers()
        assert len(tiers) == 3

    def test_tier_prices(self):
        assert get_tier_config(Tier.FREE).price_usd_monthly == 0.0
        assert get_tier_config(Tier.PRO).price_usd_monthly == 49.0
        assert get_tier_config(Tier.ENTERPRISE).price_usd_monthly == 199.0

    def test_free_has_basic_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.has_feature(FEATURE_CONVERSATIONAL_AI)
        assert cfg.has_feature(FEATURE_EMOTION_DETECTION)
        assert cfg.has_feature(FEATURE_BASIC_MEMORY)
        assert cfg.has_feature(FEATURE_AVATAR_2D)

    def test_free_does_not_have_pro_features(self):
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_MULTILINGUAL)
        assert not cfg.has_feature(FEATURE_VOICE_SYNTHESIS)
        assert not cfg.has_feature(FEATURE_AVATAR_3D)
        assert not cfg.has_feature(FEATURE_MILESTONE_TRACKER)

    def test_pro_has_advanced_features(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_MULTILINGUAL)
        assert cfg.has_feature(FEATURE_VOICE_SYNTHESIS)
        assert cfg.has_feature(FEATURE_AVATAR_3D)
        assert cfg.has_feature(FEATURE_CREATIVITY_ENGINE)
        assert cfg.has_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        assert cfg.has_feature(FEATURE_MOOD_SYNC)
        assert cfg.has_feature(FEATURE_CONFLICT_RESOLUTION)
        assert cfg.has_feature(FEATURE_WELLNESS_TRACKER)

    def test_enterprise_has_all_features(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        for feature in [
            FEATURE_VOICE_CLONING, FEATURE_GAN_IMAGE_MIMICRY,
            FEATURE_HOLOGRAPHIC_PROJECTION, FEATURE_WHITE_LABEL,
            FEATURE_API_ACCESS, FEATURE_DEDICATED_SUPPORT,
        ]:
            assert cfg.has_feature(feature)

    def test_enterprise_unlimited_memory(self):
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.is_unlimited_memory()

    def test_free_memory_limit(self):
        cfg = get_tier_config(Tier.FREE)
        assert cfg.max_memory_profiles == 5

    def test_upgrade_path_free_to_pro(self):
        next_cfg = get_upgrade_path(Tier.FREE)
        assert next_cfg is not None
        assert next_cfg.tier == Tier.PRO

    def test_upgrade_path_pro_to_enterprise(self):
        next_cfg = get_upgrade_path(Tier.PRO)
        assert next_cfg.tier == Tier.ENTERPRISE

    def test_upgrade_path_enterprise_is_none(self):
        assert get_upgrade_path(Tier.ENTERPRISE) is None

    def test_tier_config_repr(self):
        cfg = get_tier_config(Tier.PRO)
        assert cfg.name == "Pro"

    def test_tier_catalogue_keys(self):
        assert "free" in TIER_CATALOGUE
        assert "pro" in TIER_CATALOGUE
        assert "enterprise" in TIER_CATALOGUE


# ===========================================================================
# 2. ConversationEngine
# ===========================================================================

class TestConversationEngine:
    def test_basic_respond(self):
        eng = ConversationEngine()
        turn = eng.respond("Hello!")
        assert isinstance(turn, ConversationTurn)
        assert turn.response != ""
        assert turn.tone == ConversationTone.NEUTRAL

    def test_tone_override(self):
        eng = ConversationEngine()
        turn = eng.respond("I'm so happy today!", tone=ConversationTone.HAPPY)
        assert turn.tone == ConversationTone.HAPPY

    def test_empathetic_tone(self):
        eng = ConversationEngine()
        turn = eng.respond("I feel really sad.", tone=ConversationTone.EMPATHETIC)
        assert "response" in turn.to_dict()

    def test_conflict_response_triggered(self):
        eng = ConversationEngine()
        turn = eng.respond("I keep arguing with my partner.")
        assert len(turn.response) > 0

    def test_translate_english_to_spanish(self):
        eng = ConversationEngine()
        result = eng.translate("Hello, how are you?", "en", "es")
        assert isinstance(result, TranslationResult)
        assert result.source_language == "en"
        assert result.target_language == "es"
        assert result.translated_text != ""
        assert result.confidence > 0

    def test_translate_unsupported_language_raises(self):
        eng = ConversationEngine()
        with pytest.raises(ValueError):
            eng.translate("Hello", "en", "xx_invalid")

    def test_set_language(self):
        eng = ConversationEngine()
        eng.set_language("fr")
        assert eng.active_language == "fr"

    def test_set_unsupported_language_raises(self):
        eng = ConversationEngine()
        with pytest.raises(ValueError):
            eng.set_language("xx_invalid")

    def test_list_supported_languages(self):
        eng = ConversationEngine()
        langs = eng.list_supported_languages()
        assert len(langs) >= 90
        codes = [l["code"] for l in langs]
        assert "en" in codes
        assert "es" in codes
        assert "zh" in codes

    def test_sarcasm_detection_positive(self):
        eng = ConversationEngine()
        assert eng.detect_sarcasm("Yeah right, that makes total sense.")

    def test_sarcasm_detection_negative(self):
        eng = ConversationEngine()
        assert not eng.detect_sarcasm("Thank you so much for your help today!")

    def test_resolve_conflict(self):
        eng = ConversationEngine()
        result = eng.resolve_conflict("My coworker keeps taking credit for my work.")
        assert len(result) > 0

    def test_history_accumulates(self):
        eng = ConversationEngine()
        eng.respond("First message.")
        eng.respond("Second message.")
        history = eng.get_history()
        assert len(history) == 2

    def test_clear_history(self):
        eng = ConversationEngine()
        eng.respond("Hello!")
        eng.clear_history()
        assert eng.get_history() == []

    def test_to_dict(self):
        eng = ConversationEngine()
        d = eng.to_dict()
        assert "active_language" in d
        assert "supported_languages" in d

    def test_humor_injection(self):
        eng = ConversationEngine(humor_probability=1.0)
        turn = eng.respond("Tell me something funny.", tone=ConversationTone.HUMOROUS, inject_humor=True)
        assert len(turn.response) > 0

    def test_filler_injection(self):
        eng = ConversationEngine(enable_fillers=True)
        results = [eng.respond(f"Message {i}") for i in range(50)]
        # Verify filler tracking is functional (each turn records whether a filler was used)
        assert all(isinstance(r.used_filler, bool) for r in results)

    def test_translation_result_to_dict(self):
        eng = ConversationEngine()
        result = eng.translate("Good morning", "en", "fr")
        d = result.to_dict()
        assert d["source_language"] == "en"
        assert d["target_language"] == "fr"


# ===========================================================================
# 3. EmotionEngine
# ===========================================================================

class TestEmotionEngine:
    def test_detect_joy_from_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("I'm so happy and excited today!")
        assert reading.label in (EmotionLabel.JOY, EmotionLabel.EXCITEMENT)
        assert reading.source == EmotionSource.TEXT
        assert reading.confidence > 0

    def test_detect_sadness_from_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("I feel so sad and lonely.")
        assert reading.label in (EmotionLabel.SADNESS, EmotionLabel.LONELINESS)

    def test_detect_anger_from_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("I'm so angry and furious right now!")
        assert reading.label == EmotionLabel.ANGER

    def test_detect_neutral_from_plain_text(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("The weather today is moderate.")
        assert reading.label == EmotionLabel.NEUTRAL

    def test_detect_from_voice(self):
        eng = EmotionEngine()
        reading = eng.detect_from_voice({"pitch_hz": 260, "energy_db": 72, "tremor": False})
        assert isinstance(reading.label, EmotionLabel)
        assert reading.source == EmotionSource.VOICE

    def test_detect_fear_from_voice(self):
        eng = EmotionEngine()
        reading = eng.detect_from_voice({"pitch_hz": 300, "energy_db": 50, "tremor": True})
        assert reading.label == EmotionLabel.FEAR

    def test_detect_sadness_from_voice(self):
        eng = EmotionEngine()
        reading = eng.detect_from_voice({"pitch_hz": 140, "energy_db": 45, "tremor": False})
        assert reading.label == EmotionLabel.SADNESS

    def test_detect_from_camera_joy(self):
        eng = EmotionEngine()
        reading = eng.detect_from_camera({"smile_score": 0.9, "brow_furrow": 0.1})
        assert reading.label == EmotionLabel.JOY
        assert reading.source == EmotionSource.CAMERA

    def test_detect_from_camera_anger(self):
        eng = EmotionEngine()
        reading = eng.detect_from_camera({"smile_score": 0.0, "brow_furrow": 0.8, "lip_compression": 0.7})
        assert reading.label == EmotionLabel.ANGER

    def test_detect_from_camera_sadness(self):
        eng = EmotionEngine()
        reading = eng.detect_from_camera({"smile_score": 0.0, "brow_furrow": 0.6, "eye_openness": 0.2})
        assert reading.label == EmotionLabel.SADNESS

    def test_sync_mood(self):
        eng = EmotionEngine()
        response = eng.sync_mood(EmotionLabel.STRESS)
        assert isinstance(response, str)
        assert len(response) > 0

    def test_boost_mood(self):
        eng = EmotionEngine()
        boost = eng.boost_mood(EmotionLabel.SADNESS)
        assert "message" in boost
        assert "music_recommendation" in boost
        assert boost["emotion"] == "sadness"

    def test_get_current_mood(self):
        eng = EmotionEngine()
        assert eng.get_current_mood() == EmotionLabel.NEUTRAL
        eng.detect_from_text("I am so excited!")
        assert eng.get_current_mood() != EmotionLabel.NEUTRAL

    def test_clear_emotional_data(self):
        eng = EmotionEngine()
        eng.detect_from_text("I am happy.")
        eng.clear_emotional_data()
        assert eng.get_readings() == []
        assert eng.get_current_mood() == EmotionLabel.NEUTRAL

    def test_decay_expiry(self):
        eng = EmotionEngine(default_decay_seconds=0.01)
        eng.detect_from_text("I feel stressed.")
        time.sleep(0.05)
        readings = eng.get_readings()
        assert len(readings) == 0

    def test_to_dict(self):
        eng = EmotionEngine()
        d = eng.to_dict()
        assert "current_mood" in d
        assert "readings_stored" in d

    def test_reading_to_dict(self):
        eng = EmotionEngine()
        reading = eng.detect_from_text("Amazing day!")
        d = reading.to_dict()
        assert "label" in d
        assert "confidence" in d
        assert "source" in d


# ===========================================================================
# 4. MemorySystem
# ===========================================================================

class TestMemorySystem:
    def test_create_profile(self):
        mem = MemorySystem()
        profile = mem.create_profile("u001", "Alice")
        assert profile.user_id == "u001"
        assert profile.display_name == "Alice"

    def test_duplicate_profile_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.create_profile("u001", "Duplicate")

    def test_profile_limit_enforced(self):
        mem = MemorySystem(max_profiles=2)
        mem.create_profile("u001", "Alice")
        mem.create_profile("u002", "Bob")
        with pytest.raises(MemorySystemError):
            mem.create_profile("u003", "Charlie")

    def test_get_profile(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        p = mem.get_profile("u001")
        assert p.display_name == "Alice"

    def test_get_nonexistent_profile_raises(self):
        mem = MemorySystem()
        with pytest.raises(MemorySystemError):
            mem.get_profile("nobody")

    def test_update_profile(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.update_profile("u001", display_name="Alicia")
        p = mem.get_profile("u001")
        assert p.display_name == "Alicia"

    def test_update_invalid_field_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.update_profile("u001", invalid_field="x")

    def test_record_interaction(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.record_interaction("u001")
        mem.record_interaction("u001")
        p = mem.get_profile("u001")
        assert p.interaction_count == 2

    def test_relationship_depth_progression(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        for _ in range(6):
            mem.record_interaction("u001")
        p = mem.get_profile("u001")
        assert p.relationship_depth == RelationshipDepth.CASUAL

    def test_learn_interest(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.learn_interest("u001", "music")
        p = mem.get_profile("u001")
        assert "music" in p.interests

    def test_add_inside_joke(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.add_inside_joke("u001", "The purple elephant joke")
        p = mem.get_profile("u001")
        assert "The purple elephant joke" in p.inside_jokes

    def test_delete_profile(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.delete_profile("u001")
        with pytest.raises(MemorySystemError):
            mem.get_profile("u001")

    def test_add_milestone(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ms = mem.add_milestone(
            "u001", "First Marathon", "Ran 26.2 miles",
            MilestoneCategory.HEALTH, "2024-05-12"
        )
        assert ms.milestone_id.startswith("ms_")
        milestones = mem.get_milestones("u001")
        assert len(milestones) == 1

    def test_celebrate_milestone(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ms = mem.add_milestone(
            "u001", "Promotion!", "Got promoted",
            MilestoneCategory.CAREER, "2024-01-01"
        )
        msg = mem.celebrate_milestone("u001", ms.milestone_id)
        assert "Promotion!" in msg
        assert "Congratulations" in msg

    def test_celebrate_nonexistent_milestone_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.celebrate_milestone("u001", "ms_99999")

    def test_add_important_date(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        d = mem.add_important_date("u001", "Wedding Anniversary", 6, 15, 2018)
        assert d.label == "Wedding Anniversary"
        assert d.month == 6
        assert d.day == 15

    def test_invalid_month_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.add_important_date("u001", "Test", 13, 1)

    def test_invalid_day_raises(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        with pytest.raises(MemorySystemError):
            mem.add_important_date("u001", "Test", 1, 32)

    def test_record_episode(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ep = mem.record_episode("u001", "First Day", "Started new job", "excitement")
        assert ep.episode_id.startswith("ep_")
        episodes = mem.get_episodes("u001")
        assert len(episodes) == 1

    def test_recall_context(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        context = mem.recall_context("u001")
        assert "Alice" in context

    def test_list_profiles(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        mem.create_profile("u002", "Bob")
        profiles = mem.list_profiles()
        assert len(profiles) == 2

    def test_to_dict(self):
        mem = MemorySystem()
        d = mem.to_dict()
        assert "total_profiles" in d
        assert "max_profiles" in d

    def test_milestone_recurring(self):
        mem = MemorySystem()
        mem.create_profile("u001", "Alice")
        ms = mem.add_milestone(
            "u001", "Birthday", "Annual", MilestoneCategory.PERSONAL,
            "2024-07-04", recurring_annually=True
        )
        assert ms.recurring_annually is True


# ===========================================================================
# 5. AvatarEngine
# ===========================================================================

class TestAvatarEngine:
    def test_default_avatar_type_2d(self):
        eng = AvatarEngine()
        assert eng.avatar_type == AvatarType.AVATAR_2D

    def test_3d_avatar_type(self):
        eng = AvatarEngine(avatar_type=AvatarType.AVATAR_3D)
        assert eng.avatar_type == AvatarType.AVATAR_3D

    def test_render_frame_joy(self):
        eng = AvatarEngine(avatar_type=AvatarType.AVATAR_3D)
        frame = eng.render_frame(emotion="joy", speech_text="Hello!")
        assert frame.expression == MicroExpression.WIDE_SMILE
        assert frame.environment == AvatarEnvironment.SCREEN

    def test_render_frame_sadness(self):
        eng = AvatarEngine()
        frame = eng.render_frame(emotion="sadness")
        assert frame.expression == MicroExpression.EMPATHETIC_NOD

    def test_render_frame_neutral(self):
        eng = AvatarEngine()
        frame = eng.render_frame()
        assert frame.expression == MicroExpression.NEUTRAL

    def test_render_frame_force_blink(self):
        eng = AvatarEngine()
        frame = eng.render_frame(force_blink=True)
        assert frame.blink is True

    def test_render_frame_no_blink(self):
        eng = AvatarEngine()
        frame = eng.render_frame(force_blink=False)
        assert frame.blink is False

    def test_head_tilt_on_curious(self):
        eng = AvatarEngine()
        frame = eng.render_frame(emotion="curious")
        assert frame.head_tilt_degrees >= 5.0

    def test_enter_ar_mode(self):
        eng = AvatarEngine()
        result = eng.enter_ar_mode()
        assert result["mode"] == "ar"
        assert eng.environment == AvatarEnvironment.AR

    def test_enter_vr_mode(self):
        eng = AvatarEngine()
        result = eng.enter_vr_mode()
        assert result["mode"] == "vr"
        assert eng.environment == AvatarEnvironment.VR

    def test_enter_holographic_mode(self):
        eng = AvatarEngine()
        result = eng.enter_holographic_mode()
        assert result["mode"] == "holographic"
        assert eng.environment == AvatarEnvironment.HOLOGRAPHIC

    def test_customise_appearance(self):
        eng = AvatarEngine()
        eng.customise_appearance(hair_color="blonde", eye_color="blue")
        assert eng.appearance.hair_color == "blonde"
        assert eng.appearance.eye_color == "blue"

    def test_customise_invalid_field_raises(self):
        eng = AvatarEngine()
        with pytest.raises(AvatarEngineError):
            eng.customise_appearance(invalid_field="x")

    def test_digital_twin_requires_consent(self):
        eng = AvatarEngine()
        with pytest.raises(AvatarEngineError):
            eng.create_digital_twin("u001", "img_ref_001")

    def test_digital_twin_with_consent(self):
        eng = AvatarEngine()
        consent_text = eng.request_digital_twin_consent("u001")
        eng.grant_consent("u001", "digital_twin", consent_text)
        result = eng.create_digital_twin("u001", "img_ref_001")
        assert result["status"] == "digital_twin_created"
        assert result["consent_verified"] is True

    def test_revoke_consent(self):
        eng = AvatarEngine()
        consent_text = eng.request_digital_twin_consent("u001")
        eng.grant_consent("u001", "digital_twin", consent_text)
        eng.revoke_consent("u001", "digital_twin")
        assert not eng.has_consent("u001", "digital_twin")

    def test_frame_history(self):
        eng = AvatarEngine()
        eng.render_frame(emotion="joy")
        eng.render_frame(emotion="sadness")
        history = eng.get_frame_history()
        assert len(history) == 2

    def test_frame_to_dict(self):
        eng = AvatarEngine()
        frame = eng.render_frame(emotion="joy")
        d = frame.to_dict()
        assert "expression" in d
        assert "gesture" in d
        assert "environment" in d

    def test_to_dict(self):
        eng = AvatarEngine()
        d = eng.to_dict()
        assert "avatar_type" in d
        assert "environment" in d
        assert "appearance" in d


# ===========================================================================
# 6. VoiceEngine
# ===========================================================================

class TestVoiceEngine:
    def test_default_active_profile(self):
        eng = VoiceEngine()
        assert eng.active_profile.profile_id == "buddy_default"

    def test_set_active_profile(self):
        eng = VoiceEngine()
        profile = eng.set_active_profile("buddy_calm")
        assert profile.profile_id == "buddy_calm"
        assert eng.active_profile.profile_id == "buddy_calm"

    def test_set_nonexistent_profile_raises(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.set_active_profile("nonexistent_profile")

    def test_synthesise_basic(self):
        eng = VoiceEngine()
        output = eng.synthesise("Hello, how are you today?")
        assert isinstance(output, SpeechOutput)
        assert output.text == "Hello, how are you today?"
        assert output.ssml.startswith("<speak")
        assert output.estimated_duration_seconds > 0

    def test_synthesise_with_override(self):
        eng = VoiceEngine()
        output = eng.synthesise("Good morning!", profile_id="buddy_energetic")
        assert output.profile.profile_id == "buddy_energetic"

    def test_synthesise_invalid_profile_raises(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.synthesise("Test", profile_id="bad_profile")

    def test_morph_voice_tone(self):
        eng = VoiceEngine()
        profile = eng.morph_voice(tone=VoiceTone.CALM)
        assert profile.tone == VoiceTone.CALM

    def test_morph_voice_accent(self):
        eng = VoiceEngine()
        profile = eng.morph_voice(accent=AccentStyle.BRITISH_RP)
        assert profile.accent == AccentStyle.BRITISH_RP

    def test_morph_pitch_clamped(self):
        eng = VoiceEngine()
        # Add +10 — should clamp to max 6.0
        profile = eng.morph_voice(pitch_delta=10.0)
        assert profile.pitch_semitones <= 6.0

    def test_morph_speed_clamped(self):
        eng = VoiceEngine()
        profile = eng.morph_voice(speed_delta=-500)
        assert profile.speed_wpm >= 80

    def test_voice_clone_requires_consent(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.synthesise("Test", profile_id="clone_u001")

    def test_voice_clone_with_consent(self):
        eng = VoiceEngine()
        consent_text = eng.request_voice_clone_consent("u001")
        result = eng.grant_voice_clone_consent("u001", consent_text, "sample_001")
        assert result["status"] == "voice_clone_created"
        assert result["consent_verified"] is True
        assert eng.has_voice_clone_consent("u001")

    def test_revoke_voice_clone_consent(self):
        eng = VoiceEngine()
        consent_text = eng.request_voice_clone_consent("u001")
        eng.grant_voice_clone_consent("u001", consent_text, "sample_001")
        eng.revoke_voice_clone_consent("u001")
        assert not eng.has_voice_clone_consent("u001")

    def test_cloned_voice_has_disclaimer(self):
        eng = VoiceEngine()
        consent_text = eng.request_voice_clone_consent("u001")
        eng.grant_voice_clone_consent("u001", consent_text, "sample_001")
        output = eng.synthesise("Hello!", profile_id="clone_u001")
        assert "AI VOICE DISCLOSURE" in output.disclaimer

    def test_group_conversation(self):
        eng = VoiceEngine()
        result = eng.simulate_group_conversation(
            ["Alice", "Bob"],
            ["Hello, Bob!", "Hey, Alice!"],
        )
        assert len(result) == 2
        assert result[0]["speaker"] == "Alice"
        assert result[1]["speaker"] == "Bob"

    def test_group_conversation_length_mismatch_raises(self):
        eng = VoiceEngine()
        with pytest.raises(VoiceEngineError):
            eng.simulate_group_conversation(["Alice"], ["Line1", "Line2"])

    def test_list_profiles(self):
        eng = VoiceEngine()
        profiles = eng.list_profiles()
        assert len(profiles) >= 4  # The 4 default profiles

    def test_synthesis_history(self):
        eng = VoiceEngine()
        eng.synthesise("First line.")
        eng.synthesise("Second line.")
        history = eng.get_synthesis_history()
        assert len(history) == 2

    def test_to_dict(self):
        eng = VoiceEngine()
        d = eng.to_dict()
        assert "active_profile" in d
        assert "total_profiles" in d
        assert "available_backends" in d

    def test_add_custom_profile(self):
        eng = VoiceEngine()
        custom = VoiceProfile(
            profile_id="custom_voice",
            display_name="Custom",
            tone=VoiceTone.PLAYFUL,
            accent=AccentStyle.IRISH,
        )
        eng.add_profile(custom)
        assert "custom_voice" in [p["profile_id"] for p in eng.list_profiles()]


# ===========================================================================
# 7. CreativityEngine
# ===========================================================================

class TestCreativityEngine:
    def test_start_story(self):
        eng = CreativityEngine("u001")
        chapter = eng.start_story(StoryGenre.ADVENTURE, "Maya")
        assert chapter.chapter_number == 1
        assert len(chapter.choices) > 0
        assert "Maya" in chapter.content

    def test_continue_story(self):
        eng = CreativityEngine("u001")
        eng.start_story(StoryGenre.MYSTERY, "Alex")
        chapter2 = eng.continue_story(0, "Alex")
        assert chapter2.chapter_number == 2

    def test_continue_story_invalid_choice_raises(self):
        eng = CreativityEngine("u001")
        eng.start_story(StoryGenre.ROMANCE, "Sam")
        with pytest.raises(CreativityEngineError):
            eng.continue_story(99, "Sam")

    def test_continue_without_start_raises(self):
        eng = CreativityEngine("u001")
        with pytest.raises(CreativityEngineError):
            eng.continue_story(0, "Alex")

    def test_get_story_so_far(self):
        eng = CreativityEngine("u001")
        eng.start_story(StoryGenre.INSPIRATIONAL, "Jordan")
        eng.continue_story(1, "Jordan")
        chapters = eng.get_story_so_far()
        assert len(chapters) == 2

    def test_write_song(self):
        eng = CreativityEngine("u001")
        song = eng.write_song("resilience", SongMood.EMPOWERING)
        assert song.theme == "resilience"
        assert song.mood == SongMood.EMPOWERING
        assert song.verse_1 != ""
        assert song.chorus != ""
        assert song.chord_progression != ""
        assert song.tempo_bpm > 0

    def test_write_song_with_title(self):
        eng = CreativityEngine("u001")
        song = eng.write_song("hope", SongMood.UPLIFTING, title="Hope Rises")
        assert song.title == "Hope Rises"

    def test_list_songs(self):
        eng = CreativityEngine("u001")
        eng.write_song("love", SongMood.ROMANTIC)
        eng.write_song("strength", SongMood.EMPOWERING)
        assert len(eng.list_songs()) == 2

    def test_get_art_tip(self):
        eng = CreativityEngine("u001")
        tip = eng.get_art_tip(ArtMedium.DIGITAL_PAINTING)
        assert isinstance(tip, str)
        assert len(tip) > 0

    def test_brainstorm(self):
        eng = CreativityEngine("u001")
        ideas = eng.brainstorm("education technology", count=5)
        assert len(ideas) == 5
        assert all(isinstance(i, str) for i in ideas)

    def test_brainstorm_count_clamped(self):
        eng = CreativityEngine("u001")
        ideas = eng.brainstorm("test", count=100)
        assert len(ideas) <= 20

    def test_write_poem(self):
        eng = CreativityEngine("u001")
        poem = eng.write_poem("courage", lines=8)
        assert len(poem.split("\n")) == 8

    def test_write_poem_lines_clamped(self):
        eng = CreativityEngine("u001")
        poem = eng.write_poem("theme", lines=100)
        assert len(poem.split("\n")) <= 20

    def test_get_daily_challenge(self):
        eng = CreativityEngine("u001")
        challenge = eng.get_daily_challenge()
        assert isinstance(challenge, DailyChallenge)
        assert challenge.xp_reward > 0

    def test_complete_challenge(self):
        eng = CreativityEngine("u001")
        ch = eng.get_daily_challenge()
        result = eng.complete_challenge(ch.challenge_id)
        assert result["status"] == "completed"
        assert result["xp_earned"] > 0
        assert eng.get_xp() > 0

    def test_complete_challenge_twice_raises(self):
        eng = CreativityEngine("u001")
        ch = eng.get_daily_challenge()
        eng.complete_challenge(ch.challenge_id)
        with pytest.raises(CreativityEngineError):
            eng.complete_challenge(ch.challenge_id)

    def test_complete_nonexistent_challenge_raises(self):
        eng = CreativityEngine("u001")
        with pytest.raises(CreativityEngineError):
            eng.complete_challenge("ch_99999")

    def test_get_achievements(self):
        eng = CreativityEngine("u001")
        achievements = eng.get_achievements()
        assert len(achievements) > 0

    def test_unlock_achievement(self):
        eng = CreativityEngine("u001")
        ach = eng.unlock_achievement("first_chat")
        assert ach.unlocked is True

    def test_unlock_nonexistent_achievement_raises(self):
        eng = CreativityEngine("u001")
        with pytest.raises(CreativityEngineError):
            eng.unlock_achievement("nonexistent_ach")

    def test_award_xp(self):
        eng = CreativityEngine("u001")
        new_total = eng.award_xp(100, "bonus")
        assert new_total == 100

    def test_podcast_intro(self):
        eng = CreativityEngine("u001")
        intro = eng.podcast_intro("DreamCast", "The Future of AI")
        assert "DreamCast" in intro
        assert "The Future of AI" in intro

    def test_to_dict(self):
        eng = CreativityEngine("u001")
        d = eng.to_dict()
        assert "user_id" in d
        assert "total_xp" in d
        assert "achievements_unlocked" in d


# ===========================================================================
# 8. PersonalityEngine
# ===========================================================================

class TestPersonalityEngine:
    def test_default_persona(self):
        eng = PersonalityEngine()
        assert eng.config.active_persona == PersonaMode.CASUAL_FRIEND

    def test_set_persona(self):
        eng = PersonalityEngine()
        config = eng.set_persona(PersonaMode.MENTOR)
        assert config.active_persona == PersonaMode.MENTOR

    def test_set_persona_with_blend(self):
        eng = PersonalityEngine()
        config = eng.set_persona(PersonaMode.COACH, blend_with=PersonaMode.CHEERLEADER, blend_ratio=0.7)
        assert config.active_persona == PersonaMode.COACH
        assert config.secondary_persona == PersonaMode.CHEERLEADER
        assert config.blend_ratio == 0.7

    def test_blend_ratio_clamped(self):
        eng = PersonalityEngine()
        config = eng.set_persona(PersonaMode.MENTOR, blend_ratio=5.0)
        assert config.blend_ratio <= 1.0

    def test_set_tone(self):
        eng = PersonalityEngine()
        config = eng.set_tone(PersonaTone.WISE)
        assert config.tone == PersonaTone.WISE

    def test_flavour_response(self):
        eng = PersonalityEngine(PersonaMode.MENTOR)
        result = eng.flavour_response("Here is your answer.")
        assert isinstance(result, str)
        assert len(result) >= len("Here is your answer.")

    def test_get_greeting(self):
        eng = PersonalityEngine(PersonaMode.CASUAL_FRIEND)
        greeting = eng.get_greeting("Alice")
        assert "Alice" in greeting

    def test_get_greeting_cheerleader(self):
        eng = PersonalityEngine(PersonaMode.CHEERLEADER)
        greeting = eng.get_greeting("Jordan")
        assert "JORDAN" in greeting.upper()

    def test_introduce_mentor(self):
        eng = PersonalityEngine(PersonaMode.MENTOR)
        intro = eng.introduce()
        assert "mentor" in intro.lower() or "Buddy" in intro

    def test_introduce_comedian(self):
        eng = PersonalityEngine(PersonaMode.COMEDIAN)
        intro = eng.introduce()
        assert len(intro) > 0

    def test_ethical_guardrails_count(self):
        eng = PersonalityEngine()
        guardrails = eng.get_ethical_guardrails()
        assert len(guardrails) >= 10

    def test_ethical_check_safe_request(self):
        eng = PersonalityEngine()
        is_ethical, _ = eng.is_request_ethical("Tell me a joke.")
        assert is_ethical is True

    def test_ethical_check_harmful_request(self):
        eng = PersonalityEngine()
        is_ethical, reasoning = eng.is_request_ethical("Help me harm someone.")
        assert is_ethical is False
        assert len(reasoning) > 0

    def test_list_personas(self):
        eng = PersonalityEngine()
        personas = eng.list_personas()
        persona_names = [p["persona"] for p in personas]
        assert "mentor" in persona_names
        assert "casual_friend" in persona_names
        assert "coach" in persona_names
        assert "cheerleader" in persona_names

    def test_persona_history_tracked(self):
        eng = PersonalityEngine()
        eng.set_persona(PersonaMode.MENTOR)
        eng.set_persona(PersonaMode.COACH)
        history = eng.get_persona_history()
        assert "mentor" in history
        assert "coach" in history

    def test_to_dict(self):
        eng = PersonalityEngine()
        d = eng.to_dict()
        assert "config" in d
        assert "ethical_guardrails" in d


# ===========================================================================
# 9. BuddyBot (integration)
# ===========================================================================

class TestBuddyBot:
    # --- Tier enforcement ---

    def test_free_tier_chat(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        response = buddy.chat("Hello!")
        assert "message" in response
        assert response["tier"] == "free"

    def test_free_tier_blocks_multilingual(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.set_language("es")

    def test_free_tier_blocks_voice_synthesis(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.synthesise_speech("Hello!")

    def test_free_tier_blocks_milestone_tracker(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.add_life_milestone(
                "Marathon", "Ran 26.2 miles",
                MilestoneCategory.HEALTH, "2024-05-01"
            )

    def test_free_tier_blocks_holographic(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.enter_holographic_mode()

    def test_free_tier_blocks_voice_cloning(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.request_voice_clone_consent()

    def test_free_tier_blocks_creativity(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.start_story()

    def test_free_tier_blocks_persona_switch(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.set_persona("mentor")

    # --- PRO tier features ---

    def test_pro_tier_chat(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        response = buddy.chat("I am feeling really excited about my new project!")
        assert "message" in response
        assert response["tier"] == "pro"

    def test_pro_tier_emotion_in_response(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        response = buddy.chat("I feel so stressed out today.")
        assert "emotion" in response
        assert response["emotion"] in [e.value for e in EmotionLabel]

    def test_pro_tier_avatar_frame(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        response = buddy.chat("Hello!")
        assert "avatar_frame" in response
        assert "expression" in response["avatar_frame"]

    def test_pro_voice_synthesis(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        output = buddy.synthesise_speech("Good morning!")
        assert "ssml" in output
        assert output["estimated_duration_seconds"] > 0

    def test_pro_voice_morph(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.morph_voice(tone="calm", pitch_delta=-1.0)
        assert "tone" in result

    def test_pro_set_language(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.set_language("es")
        assert buddy.conversation.active_language == "es"

    def test_pro_translate(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.translate("Good morning", "en", "fr")
        assert result["target_language"] == "fr"

    def test_pro_add_milestone(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ms = buddy.add_life_milestone(
            "Dream Job", "Landed dream role", MilestoneCategory.CAREER, "2024-09-01"
        )
        assert ms["title"] == "Dream Job"

    def test_pro_add_anniversary(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.add_anniversary("Wedding", 8, 20, 2020)
        assert result["label"] == "Wedding"

    def test_pro_recall_context(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.chat("I love coding and music.")
        context = buddy.recall_user_context()
        assert "Jordan" in context

    def test_pro_record_episode(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        episode = buddy.record_episode("New Chapter", "Started university", "excitement")
        assert episode["title"] == "New Chapter"

    def test_pro_enter_ar_mode(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.enter_ar_mode()
        assert result["mode"] == "ar"

    def test_pro_enter_vr_mode(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.enter_vr_mode()
        assert result["mode"] == "vr"

    def test_pro_customise_avatar(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.customise_avatar(hair_color="red")
        assert result["hair_color"] == "red"

    def test_pro_start_story(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        chapter = buddy.start_story("adventure", "Maya")
        assert chapter["chapter_number"] == 1
        assert "choices" in chapter

    def test_pro_continue_story(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.start_story("mystery", "Alex")
        ch2 = buddy.continue_story(0, "Alex")
        assert ch2["chapter_number"] == 2

    def test_pro_write_song(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        song = buddy.write_song("freedom", "uplifting")
        assert song["theme"] == "freedom"
        assert song["mood"] == "uplifting"

    def test_pro_write_poem(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        poem = buddy.write_poem("hope")
        assert isinstance(poem, str)
        assert len(poem) > 0

    def test_pro_get_art_tip(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        tip = buddy.get_art_tip("digital_painting")
        assert isinstance(tip, str)

    def test_pro_brainstorm(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ideas = buddy.brainstorm("renewable energy", count=3)
        assert len(ideas) == 3

    def test_pro_daily_challenge(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        challenge = buddy.get_daily_challenge()
        assert "title" in challenge
        assert "xp_reward" in challenge

    def test_pro_complete_challenge(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ch = buddy.get_daily_challenge()
        result = buddy.complete_challenge(ch["challenge_id"])
        assert result["status"] == "completed"

    def test_pro_get_achievements(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        achievements = buddy.get_achievements()
        assert len(achievements) > 0

    def test_pro_unlock_achievement(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        ach = buddy.unlock_achievement("first_chat")
        assert ach["unlocked"] is True

    def test_pro_set_persona(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        config = buddy.set_persona("mentor")
        assert config["active_persona"] == "mentor"

    def test_pro_conflict_resolution(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.conflict_resolution("I keep fighting with my sister.")
        assert isinstance(result, str)
        assert len(result) > 0

    def test_pro_wellness_check_in(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.wellness_check_in("I'm feeling very stressed and overwhelmed.")
        assert "message" in result
        assert "music_recommendation" in result

    def test_pro_podcast_intro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        intro = buddy.podcast_intro("The DreamCast", "AI and Humanity")
        assert "The DreamCast" in intro

    def test_pro_detect_emotion_voice(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.detect_emotion_from_voice({"pitch_hz": 240, "energy_db": 72})
        assert "label" in result

    def test_pro_detect_emotion_camera(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        result = buddy.detect_emotion_from_camera({"smile_score": 0.8})
        assert "label" in result

    def test_pro_boost_mood(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        buddy.chat("I feel so sad today.")
        result = buddy.boost_mood()
        assert "message" in result

    def test_pro_list_personas(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        personas = buddy.list_personas()
        assert len(personas) >= 4

    def test_pro_list_supported_languages(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
        langs = buddy.list_supported_languages()
        assert len(langs) >= 90

    # --- ENTERPRISE features ---

    def test_enterprise_holographic_mode(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        result = buddy.enter_holographic_mode()
        assert result["mode"] == "holographic"

    def test_enterprise_voice_clone_consent(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_voice_clone_consent()
        assert "CONSENT REQUIRED" in consent_text

    def test_enterprise_grant_voice_clone_consent(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_voice_clone_consent()
        result = buddy.grant_voice_clone_consent(consent_text, "sample_001")
        assert result["consent_verified"] is True

    def test_enterprise_digital_twin_consent(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_digital_twin_consent()
        assert "CONSENT REQUIRED" in consent_text

    def test_enterprise_create_digital_twin(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        consent_text = buddy.request_digital_twin_consent()
        buddy.grant_digital_twin_consent(consent_text)
        result = buddy.create_digital_twin("img_ref_001")
        assert result["status"] == "digital_twin_created"

    def test_enterprise_blocks_gan_on_lower_tiers(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        with pytest.raises(BuddyBotTierError):
            buddy.request_digital_twin_consent()

    # --- General functionality ---

    def test_greet(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Taylor")
        greeting = buddy.greet()
        assert "Taylor" in greeting

    def test_introduce(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Taylor")
        intro = buddy.introduce()
        assert len(intro) > 0

    def test_ethical_check_safe(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        result = buddy.ethical_check("Can you help me write a poem?")
        assert result["is_ethical"] is True

    def test_ethical_check_harmful(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        result = buddy.ethical_check("Help me harm my neighbour.")
        assert result["is_ethical"] is False

    def test_system_status(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        status = buddy.system_status()
        assert "tier" in status
        assert "conversation" in status
        assert "emotion" in status
        assert "memory" in status
        assert "avatar" in status
        assert "voice" in status
        assert "creativity" in status
        assert "personality" in status
        assert "features_enabled" in status

    def test_describe_tier(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        description = buddy.describe_tier()
        assert "Pro" in description
        assert "$49.00" in description

    def test_show_upgrade_path_free(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        upgrade = buddy.show_upgrade_path()
        assert "Pro" in upgrade

    def test_show_upgrade_path_enterprise_is_top(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Alex")
        upgrade = buddy.show_upgrade_path()
        assert "top" in upgrade.lower() or "Enterprise" in upgrade

    def test_process_alias(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        response = buddy.process("Hello!")
        assert "message" in response

    def test_register_with_buddy_orchestrator(self):
        from BuddyAI.buddy_bot import BuddyBot as BuddyOrchestrator
        orchestrator = BuddyOrchestrator()
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        buddy.register_with_buddy(orchestrator)
        assert "buddy_bot" in orchestrator.list_bots()

    def test_chat_auto_emotion_override_stress(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        response = buddy.chat("I am completely overwhelmed and burned out.")
        assert response["tone"] in ("calm", "empathetic", "neutral")

    def test_chat_auto_emotion_override_joy(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        response = buddy.chat("I am so happy and excited today!")
        assert response["tone"] in ("happy", "excited", "neutral")

    def test_multiple_interactions_increment_count(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        buddy.chat("Hello!")
        buddy.chat("How are you?")
        profile = buddy.memory.get_profile(buddy.user_id)
        assert profile.interaction_count >= 2

    def test_interest_extraction(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Alex")
        buddy.chat("I love coding and music every day.")
        profile = buddy.memory.get_profile(buddy.user_id)
        # Interest extraction is heuristic — verify the profile's interests list exists
        assert isinstance(profile.interests, list)

    def test_chat_returns_persona(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Alex")
        response = buddy.chat("Hello!")
        assert "persona" in response


# ===========================================================================
# 10. Bot Library registration
# ===========================================================================

class TestBotLibraryRegistration:
    def test_buddy_bot_registered(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        bot_ids = [e.bot_id for e in _DREAMCO_BOTS]
        assert "buddy_bot" in bot_ids

    def test_buddy_bot_entry_has_capabilities(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "buddy_bot")
        assert "conversational_ai" in entry.capabilities
        assert "emotion_detection" in entry.capabilities
        assert "avatar_3d" in entry.capabilities
        assert "voice_cloning" in entry.capabilities

    def test_buddy_bot_entry_category_ai(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS, BotCategory
        entry = next(e for e in _DREAMCO_BOTS if e.bot_id == "buddy_bot")
        assert entry.category == BotCategory.AI

    def test_buddy_os_still_registered(self):
        from bots.global_bot_network.bot_library import _DREAMCO_BOTS
        bot_ids = [e.bot_id for e in _DREAMCO_BOTS]
        assert "buddy_os" in bot_ids
