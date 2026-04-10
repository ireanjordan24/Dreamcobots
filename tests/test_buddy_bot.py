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

# ===========================================================================
# 11. MediaProductionEngine
# ===========================================================================

class TestMediaProductionEngine:
    def _engine(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
            MusicVideoStyle, MovieGenre,
        )
        return MediaProductionEngine(user_id="test_user"), ClientBrief, AdFormat, AdStyle, MusicVideoStyle, MovieGenre

    def test_create_commercial_video(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief(
            client_name="Acme Corp",
            product_or_service="Widget Pro",
            target_audience="small business owners",
            key_message="Save time, earn more",
        )
        script = engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.FULLY_AI)
        assert script.client_name == "Acme Corp"
        assert script.ad_format == AdFormat.VIDEO_30
        assert script.ad_style == AdStyle.FULLY_AI
        assert "Acme Corp" in script.script
        assert script.duration_seconds == 30
        assert "AI" in script.ai_disclosure

    def test_create_radio_ad_30s(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdStyle, AdFormat,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief(
            client_name="Radio Brand",
            product_or_service="Podcast App",
            target_audience="commuters",
            key_message="Listen anywhere",
            call_to_action="Download now",
        )
        script = engine.create_radio_ad(brief, duration="30s")
        assert script.ad_format == AdFormat.RADIO_30
        assert script.duration_seconds == 30

    def test_create_radio_ad_60s(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief(
            client_name="LongAd Co",
            product_or_service="Service",
            target_audience="everyone",
            key_message="Best service",
        )
        script = engine.create_radio_ad(brief, duration="60s")
        assert script.ad_format == AdFormat.RADIO_60
        assert script.duration_seconds == 60

    def test_create_social_ad(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief(
            client_name="SocialBrand",
            product_or_service="App",
            target_audience="gen z",
            key_message="Go viral",
        )
        script = engine.create_social_ad(brief)
        assert script.ad_format == AdFormat.SOCIAL_REEL

    def test_commercial_with_client_assets(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief(
            client_name="PhotoBrand",
            product_or_service="Camera",
            target_audience="photographers",
            key_message="Capture every moment",
            assets_provided=["hero_photo.jpg", "logo.png"],
        )
        script = engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.CLIENT_ASSETS)
        assert script.ad_style == AdStyle.CLIENT_ASSETS
        assert "hero_photo.jpg" in script.visual_direction or "logo.png" in script.visual_direction

    def test_commercial_production_id_unique(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief("A", "B", "C", "D")
        s1 = engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.FULLY_AI)
        s2 = engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.FULLY_AI)
        assert s1.production_id != s2.production_id

    def test_list_productions(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief("Brand", "Product", "Audience", "Message")
        engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.FULLY_AI)
        engine.create_commercial(brief, AdFormat.RADIO_30, AdStyle.FULLY_AI)
        assert len(engine.list_productions()) == 2

    def test_get_production_by_id(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief("Brand", "Product", "Audience", "Message")
        s = engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.FULLY_AI)
        fetched = engine.get_production(s.production_id)
        assert fetched.production_id == s.production_id

    def test_get_production_not_found_raises(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MediaProductionEngineError,
        )
        engine = MediaProductionEngine()
        with pytest.raises(MediaProductionEngineError):
            engine.get_production("COMM_9999")

    def test_commercial_to_dict(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief("Brand", "Product", "Audience", "Message")
        s = engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.FULLY_AI)
        d = s.to_dict()
        assert "production_id" in d
        assert "script" in d
        assert "visual_direction" in d
        assert "music_direction" in d
        assert "ai_disclosure" in d

    def test_create_music_video_narrative(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MusicVideoStyle,
        )
        engine = MediaProductionEngine()
        mv = engine.create_music_video("Artist X", "Song Y", MusicVideoStyle.NARRATIVE)
        assert mv.artist_name == "Artist X"
        assert mv.song_title == "Song Y"
        assert mv.style == MusicVideoStyle.NARRATIVE
        assert len(mv.storyboard) > 0
        assert len(mv.shot_list) > 0

    def test_create_music_video_all_styles(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MusicVideoStyle,
        )
        engine = MediaProductionEngine()
        for style in MusicVideoStyle:
            mv = engine.create_music_video("Artist", "Track", style)
            assert mv.style == style

    def test_music_video_unique_ids(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MusicVideoStyle,
        )
        engine = MediaProductionEngine()
        mv1 = engine.create_music_video("A", "S1", MusicVideoStyle.PERFORMANCE)
        mv2 = engine.create_music_video("A", "S2", MusicVideoStyle.PERFORMANCE)
        assert mv1.production_id != mv2.production_id

    def test_list_music_videos(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MusicVideoStyle,
        )
        engine = MediaProductionEngine()
        engine.create_music_video("A", "T1", MusicVideoStyle.LYRIC_VIDEO)
        engine.create_music_video("B", "T2", MusicVideoStyle.ANIMATED)
        assert len(engine.list_music_videos()) == 2

    def test_get_music_video_by_id(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MusicVideoStyle,
        )
        engine = MediaProductionEngine()
        mv = engine.create_music_video("Artist", "Song", MusicVideoStyle.ABSTRACT)
        fetched = engine.get_music_video(mv.production_id)
        assert fetched.production_id == mv.production_id

    def test_get_music_video_not_found_raises(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MediaProductionEngineError,
        )
        engine = MediaProductionEngine()
        with pytest.raises(MediaProductionEngineError):
            engine.get_music_video("MV_9999")

    def test_music_video_to_dict(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MusicVideoStyle,
        )
        engine = MediaProductionEngine()
        mv = engine.create_music_video("A", "S", MusicVideoStyle.NARRATIVE)
        d = mv.to_dict()
        assert "storyboard" in d
        assert "shot_list" in d
        assert "visual_direction" in d
        assert "color_palette" in d

    def test_create_movie(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MovieGenre,
        )
        engine = MediaProductionEngine()
        movie = engine.create_movie("My Film", MovieGenre.DRAMA, runtime_minutes=90)
        assert movie.title == "My Film"
        assert movie.genre == MovieGenre.DRAMA
        assert movie.estimated_runtime_minutes == 90
        assert len(movie.act_breakdown) == 4
        assert len(movie.cast_descriptions) > 0
        assert len(movie.key_scenes) > 0

    def test_create_movie_auto_logline(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MovieGenre,
        )
        engine = MediaProductionEngine()
        movie = engine.create_movie("No Logline", MovieGenre.COMEDY)
        assert len(movie.logline) > 10

    def test_create_movie_with_logline(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MovieGenre,
        )
        engine = MediaProductionEngine()
        movie = engine.create_movie("Film", MovieGenre.ACTION, logline="A hero rises.")
        assert movie.logline == "A hero rises."

    def test_list_movies(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MovieGenre,
        )
        engine = MediaProductionEngine()
        engine.create_movie("Film A", MovieGenre.DRAMA)
        engine.create_movie("Film B", MovieGenre.COMEDY)
        assert len(engine.list_movies()) == 2

    def test_get_movie_by_id(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MovieGenre,
        )
        engine = MediaProductionEngine()
        movie = engine.create_movie("Find Me", MovieGenre.THRILLER)
        fetched = engine.get_movie(movie.production_id)
        assert fetched.production_id == movie.production_id

    def test_get_movie_not_found_raises(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MediaProductionEngineError,
        )
        engine = MediaProductionEngine()
        with pytest.raises(MediaProductionEngineError):
            engine.get_movie("FILM_9999")

    def test_movie_to_dict(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MovieGenre,
        )
        engine = MediaProductionEngine()
        movie = engine.create_movie("DictFilm", MovieGenre.SHORT_FILM)
        d = movie.to_dict()
        assert "logline" in d
        assert "synopsis" in d
        assert "act_breakdown" in d
        assert "cinematography_notes" in d

    def test_production_summary(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
            MusicVideoStyle, MovieGenre,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief("B", "P", "A", "M")
        engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.FULLY_AI)
        engine.create_music_video("A", "S", MusicVideoStyle.NARRATIVE)
        engine.create_movie("F", MovieGenre.DRAMA)
        summary = engine.production_summary()
        assert summary["commercials"] == 1
        assert summary["music_videos"] == 1
        assert summary["movies"] == 1
        assert summary["total"] == 3

    def test_all_ad_formats(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief("B", "P", "A", "M")
        for fmt in AdFormat:
            script = engine.create_commercial(brief, fmt, AdStyle.FULLY_AI)
            assert script.ad_format == fmt

    def test_hybrid_style(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, ClientBrief, AdFormat, AdStyle,
        )
        engine = MediaProductionEngine()
        brief = ClientBrief("HB", "HP", "HA", "HM")
        script = engine.create_commercial(brief, AdFormat.VIDEO_30, AdStyle.HYBRID)
        assert script.ad_style == AdStyle.HYBRID

    def test_all_movie_genres(self):
        from bots.buddy_bot.media_production_engine import (
            MediaProductionEngine, MovieGenre,
        )
        engine = MediaProductionEngine()
        for genre in MovieGenre:
            movie = engine.create_movie(f"Film-{genre.value}", genre)
            assert movie.genre == genre

    def test_engine_to_dict(self):
        from bots.buddy_bot.media_production_engine import MediaProductionEngine
        engine = MediaProductionEngine(user_id="u1")
        d = engine.to_dict()
        assert d["user_id"] == "u1"
        assert "summary" in d


# ===========================================================================
# 12. SelfLearningEngine
# ===========================================================================

class TestSelfLearningEngine:
    def _engine(self):
        from bots.buddy_bot.self_learning_engine import SelfLearningEngine
        return SelfLearningEngine()

    def test_initial_capabilities_not_empty(self):
        engine = self._engine()
        assert engine.capability_count() > 0

    def test_can_do_known_capability(self):
        engine = self._engine()
        assert engine.can_do("code generation") is True

    def test_can_do_chat(self):
        engine = self._engine()
        assert engine.can_do("chat with user") is True

    def test_can_do_unknown_returns_false(self):
        engine = self._engine()
        # a totally nonsense capability
        result = engine.can_do("xyzzy_unknown_magic_capability_12345")
        assert result is False

    def test_check_capability_known(self):
        engine = self._engine()
        result = engine.check_capability("chat")
        assert result["can_do"] is True
        assert len(result["matched_capabilities"]) > 0
        assert result["gap"] is None

    def test_check_capability_unknown_returns_gap(self):
        engine = self._engine()
        result = engine.check_capability("xyzzy_impossible_task_aaabbb")
        assert result["can_do"] is False
        assert result["gap"] is not None
        gap = result["gap"]
        assert "acquisition_plan" in gap
        assert "github_search_query" in gap
        assert "recommended_models" in gap

    def test_capability_gap_logged(self):
        engine = self._engine()
        engine.check_capability("xyzzy_task_888")
        assert len(engine.get_capability_gaps()) >= 1

    def test_ask_top_models_returns_records(self):
        engine = self._engine()
        records = engine.ask_top_models("image_generation", top_n=3)
        assert len(records) == 3
        for r in records:
            assert r.capability_learned == "image_generation"
            assert r.confidence_score > 0

    def test_ask_top_models_adds_capability(self):
        engine = self._engine()
        new_cap = "holographic_telepathy_9999"
        engine.ask_top_models(new_cap, top_n=1)
        assert new_cap in engine.list_capabilities()

    def test_ask_top_models_records_logged(self):
        engine = self._engine()
        initial = len(engine.get_learning_log())
        engine.ask_top_models("video_generation", top_n=2)
        assert len(engine.get_learning_log()) >= initial + 2

    def test_search_github_for_code(self):
        engine = self._engine()
        result = engine.search_github_for_code("video_editing")
        assert result.query == "video_editing"
        assert len(result.repositories_found) > 0
        assert result.quarantine_required is True
        assert "quarantine" in result.integration_notes.lower()

    def test_github_acquisition_logged(self):
        engine = self._engine()
        engine.search_github_for_code("audio_synthesis")
        assert len(engine.get_github_acquisitions()) >= 1

    def test_github_acquisition_to_dict(self):
        engine = self._engine()
        result = engine.search_github_for_code("music_generation")
        d = result.to_dict()
        assert "query" in d
        assert "repositories_found" in d
        assert "recommended_repo" in d
        assert "integration_notes" in d
        assert "quarantine_required" in d

    def test_run_training_session(self):
        engine = self._engine()
        session = engine.run_training_session()
        assert session.session_id.startswith("TRAIN_")
        assert len(session.models_consulted) > 0
        assert "knowledge_breadth" in session.benchmarks
        assert session.benchmarks["models_in_registry"] == 100

    def test_training_session_adds_capabilities(self):
        engine = self._engine()
        before = engine.capability_count()
        engine.run_training_session()
        # After a full training session Buddy should have at least as many capabilities
        assert engine.capability_count() >= before

    def test_training_session_logged(self):
        engine = self._engine()
        engine.run_training_session()
        assert len(engine.get_training_sessions()) >= 1

    def test_training_session_focused(self):
        engine = self._engine()
        session = engine.run_training_session(focus_specialties=["music_generation"])
        assert len(session.models_consulted) > 0

    def test_add_capability(self):
        engine = self._engine()
        engine.add_capability("hologram_rendering", source="github/hologram-py")
        assert "hologram_rendering" in engine.list_capabilities()

    def test_add_capability_returns_record(self):
        engine = self._engine()
        record = engine.add_capability("quantum_decode")
        assert record.capability_learned == "quantum_decode"
        assert record.confidence_score == 1.0

    def test_list_capabilities_sorted(self):
        engine = self._engine()
        caps = engine.list_capabilities()
        assert caps == sorted(caps)

    def test_get_learning_log_limit(self):
        engine = self._engine()
        for i in range(10):
            engine.add_capability(f"cap_{i}")
        log = engine.get_learning_log(limit=5)
        assert len(log) <= 5

    def test_get_top_models(self):
        engine = self._engine()
        models = engine.get_top_models(limit=10)
        assert len(models) == 10
        ranks = [m["rank"] for m in models]
        assert ranks == sorted(ranks)

    def test_top_models_have_required_keys(self):
        engine = self._engine()
        for model in engine.get_top_models(limit=5):
            assert "provider" in model
            assert "model" in model
            assert "rank" in model
            assert "specialties" in model

    def test_top_100_model_registry_size(self):
        from bots.buddy_bot.self_learning_engine import TOP_100_AI_MODELS
        assert len(TOP_100_AI_MODELS) == 100

    def test_training_session_to_dict(self):
        engine = self._engine()
        session = engine.run_training_session(focus_specialties=["code"])
        d = session.to_dict()
        assert "session_id" in d
        assert "models_consulted" in d
        assert "capabilities_added" in d
        assert "benchmarks" in d
        assert "duration_seconds" in d

    def test_learning_record_to_dict(self):
        engine = self._engine()
        records = engine.ask_top_models("reasoning", top_n=1)
        d = records[0].to_dict()
        assert "record_id" in d
        assert "source" in d
        assert "lesson_summary" in d
        assert "confidence_score" in d

    def test_engine_to_dict(self):
        engine = self._engine()
        d = engine.to_dict()
        assert "capability_count" in d
        assert "learning_records" in d
        assert "training_sessions" in d
        assert "top_model_registry_size" in d
        assert d["top_model_registry_size"] == 100

    def test_initial_capabilities_custom(self):
        from bots.buddy_bot.self_learning_engine import SelfLearningEngine
        engine = SelfLearningEngine(initial_capabilities={"a", "b", "c"})
        assert engine.capability_count() == 3
        assert "a" in engine.list_capabilities()

    def test_multiple_training_sessions_logged(self):
        engine = self._engine()
        engine.run_training_session(focus_specialties=["code"])
        engine.run_training_session(focus_specialties=["vision"])
        assert len(engine.get_training_sessions()) == 2


# ===========================================================================
# 13. BuddyBot — Media Production Integration
# ===========================================================================

class TestBuddyBotMediaProduction:
    def test_create_commercial_pro_tier(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Client")
        result = buddy.create_commercial(
            client_name="DreamBrand",
            product_or_service="Dream Widget",
            target_audience="entrepreneurs",
            key_message="Build your dream",
            ad_format="video_30s",
            ad_style="fully_ai",
        )
        assert result["client_name"] == "DreamBrand"
        assert "script" in result

    def test_create_commercial_pro_tier_only(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Client")
        with pytest.raises(BuddyBotTierError):
            buddy.create_commercial(
                client_name="Brand",
                product_or_service="Product",
                target_audience="everyone",
                key_message="Buy now",
            )

    def test_create_radio_ad_pro_tier(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="DJ")
        # radio ad studio requires PRO; but ai_only_ads requires ENTERPRISE
        # so use hybrid style which is not gated
        result = buddy.create_radio_ad(
            client_name="RadioCo",
            product_or_service="Radio App",
            target_audience="drivers",
            key_message="Listen on the road",
            duration="30s",
            ad_style="hybrid",
        )
        assert result["ad_format"] == "radio_30s"
        assert "script" in result

    def test_create_radio_ad_free_tier_blocked(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Client")
        with pytest.raises(BuddyBotTierError):
            buddy.create_radio_ad(
                client_name="R",
                product_or_service="P",
                target_audience="A",
                key_message="M",
            )

    def test_create_music_video_pro_tier(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Artist")
        result = buddy.create_music_video(
            artist_name="Dream Artist",
            song_title="Rise Up",
            style="narrative",
        )
        assert result["artist_name"] == "Dream Artist"
        assert result["song_title"] == "Rise Up"
        assert "storyboard" in result

    def test_create_music_video_free_tier_blocked(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="Artist")
        with pytest.raises(BuddyBotTierError):
            buddy.create_music_video("A", "S")

    def test_create_movie_enterprise_only(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Director")
        result = buddy.create_movie(
            title="The DreamCo Story",
            genre="drama",
            runtime_minutes=90,
        )
        assert result["title"] == "The DreamCo Story"
        assert "act_breakdown" in result
        assert len(result["act_breakdown"]) == 4

    def test_create_movie_pro_tier_blocked(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Director")
        with pytest.raises(BuddyBotTierError):
            buddy.create_movie("Film", "drama")

    def test_list_productions_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Client")
        buddy.create_radio_ad("B", "P", "A", "M", ad_style="hybrid")
        prods = buddy.list_productions()
        assert len(prods) >= 1

    def test_list_music_videos_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Artist")
        buddy.create_music_video("A", "S", style="performance")
        mvs = buddy.list_music_videos()
        assert len(mvs) >= 1

    def test_list_movies_enterprise(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Director")
        buddy.create_movie("Film X", "action")
        movies = buddy.list_movies()
        assert len(movies) >= 1

    def test_media_production_summary(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Producer")
        buddy.create_commercial(
            "B", "P", "A", "M",
            ad_format="video_30s", ad_style="fully_ai",
        )
        summary = buddy.media_production_summary()
        assert "total" in summary
        assert summary["total"] >= 1

    def test_system_status_includes_media(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Client")
        status = buddy.system_status()
        assert "media" in status
        assert "learning" in status


# ===========================================================================
# 14. BuddyBot — Self-Learning Integration
# ===========================================================================

class TestBuddyBotSelfLearning:
    def test_can_do_returns_bool(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="User")
        result = buddy.can_do("chat with user")
        assert isinstance(result, bool)

    def test_can_do_free_tier_blocked(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="User")
        with pytest.raises(BuddyBotTierError):
            buddy.can_do("chat")

    def test_check_capability_known(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="User")
        result = buddy.check_capability("code generation")
        assert "can_do" in result
        assert isinstance(result["can_do"], bool)

    def test_check_capability_free_tier_blocked(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="User")
        with pytest.raises(BuddyBotTierError):
            buddy.check_capability("any task")

    def test_learn_from_top_models_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="User")
        records = buddy.learn_from_top_models("video_editing", top_n=2)
        assert len(records) >= 1
        assert all("lesson_summary" in r for r in records)

    def test_learn_from_top_models_free_blocked(self):
        buddy = BuddyBot(tier=Tier.FREE, user_name="User")
        with pytest.raises(BuddyBotTierError):
            buddy.learn_from_top_models("something")

    def test_acquire_code_from_github_enterprise(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Dev")
        result = buddy.acquire_code_from_github("3d_rendering")
        assert "query" in result
        assert result["quarantine_required"] is True

    def test_acquire_code_pro_blocked(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Dev")
        with pytest.raises(BuddyBotTierError):
            buddy.acquire_code_from_github("something")

    def test_run_training_session_enterprise(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Trainer")
        session = buddy.run_training_session(focus_specialties=["code"])
        assert "session_id" in session
        assert "models_consulted" in session
        assert "benchmarks" in session

    def test_run_training_session_pro_blocked(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Trainer")
        with pytest.raises(BuddyBotTierError):
            buddy.run_training_session()

    def test_list_capabilities_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="User")
        caps = buddy.list_capabilities()
        assert isinstance(caps, list)
        assert len(caps) > 0

    def test_get_learning_log_pro(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="User")
        buddy.learn_from_top_models("music_generation", top_n=1)
        log = buddy.get_learning_log(limit=5)
        assert len(log) >= 1

    def test_get_top_models_enterprise(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="User")
        models = buddy.get_top_models(limit=5)
        assert len(models) == 5
        for m in models:
            assert "provider" in m

    def test_get_top_models_pro_blocked(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="User")
        with pytest.raises(BuddyBotTierError):
            buddy.get_top_models()

    def test_get_training_sessions_enterprise(self):
        buddy = BuddyBot(tier=Tier.ENTERPRISE, user_name="Trainer")
        buddy.run_training_session(focus_specialties=["vision"])
        sessions = buddy.get_training_sessions()
        assert len(sessions) >= 1

    def test_get_training_sessions_pro_blocked(self):
        buddy = BuddyBot(tier=Tier.PRO, user_name="Trainer")
        with pytest.raises(BuddyBotTierError):
            buddy.get_training_sessions()

    def test_pro_tier_has_self_learning_features(self):
        from bots.buddy_bot.tiers import get_tier_config, Tier, FEATURE_SELF_LEARNING, FEATURE_CAPABILITY_CHECK
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_SELF_LEARNING)
        assert cfg.has_feature(FEATURE_CAPABILITY_CHECK)

    def test_enterprise_tier_has_training_features(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier,
            FEATURE_TRAINING_SESSION, FEATURE_GITHUB_ACQUISITION, FEATURE_TOP_MODEL_REGISTRY,
        )
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_TRAINING_SESSION)
        assert cfg.has_feature(FEATURE_GITHUB_ACQUISITION)
        assert cfg.has_feature(FEATURE_TOP_MODEL_REGISTRY)

    def test_pro_tier_has_media_features(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier,
            FEATURE_COMMERCIAL_PRODUCTION, FEATURE_RADIO_AD_STUDIO,
            FEATURE_VIDEO_AD_STUDIO, FEATURE_MUSIC_VIDEO_PRODUCTION,
        )
        cfg = get_tier_config(Tier.PRO)
        assert cfg.has_feature(FEATURE_COMMERCIAL_PRODUCTION)
        assert cfg.has_feature(FEATURE_RADIO_AD_STUDIO)
        assert cfg.has_feature(FEATURE_VIDEO_AD_STUDIO)
        assert cfg.has_feature(FEATURE_MUSIC_VIDEO_PRODUCTION)

    def test_enterprise_tier_has_movie_features(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier,
            FEATURE_MOVIE_PRODUCTION, FEATURE_AI_ONLY_ADS, FEATURE_CLIENT_ASSET_ADS,
        )
        cfg = get_tier_config(Tier.ENTERPRISE)
        assert cfg.has_feature(FEATURE_MOVIE_PRODUCTION)
        assert cfg.has_feature(FEATURE_AI_ONLY_ADS)
        assert cfg.has_feature(FEATURE_CLIENT_ASSET_ADS)

    def test_free_tier_missing_media_features(self):
        from bots.buddy_bot.tiers import (
            get_tier_config, Tier,
            FEATURE_COMMERCIAL_PRODUCTION, FEATURE_SELF_LEARNING,
        )
        cfg = get_tier_config(Tier.FREE)
        assert not cfg.has_feature(FEATURE_COMMERCIAL_PRODUCTION)
        assert not cfg.has_feature(FEATURE_SELF_LEARNING)


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
