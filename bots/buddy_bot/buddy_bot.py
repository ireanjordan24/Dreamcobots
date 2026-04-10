"""
Buddy Bot — DreamCo's Most Human-Like AI Companion

The most human-like AI the world has ever seen.  BuddyBot orchestrates all
sub-engines to deliver a cohesive, emotionally intelligent, creative, and
deeply personalised companion experience.

Sub-systems
-----------
  • ConversationEngine    — natural speech, multilingual, humor, conflict resolution
  • EmotionEngine         — emotion detection (text/voice/camera), mood sync, boost
  • MemorySystem          — user profiles, milestones, important dates, episodic memory
  • AvatarEngine          — 3D avatars, micro-expressions, AR/VR, holographic
  • VoiceEngine           — voice synthesis, morphing, cloning (consent-gated)
  • CreativityEngine      — storytelling, songwriting, art mentorship, gamified productivity
  • PersonalityEngine     — dynamic personas (mentor, friend, coach, cheerleader, …)

Tier access
-----------
  FREE:       Core chat, emotion detection, 5 memory profiles, 2D avatar, basic personas.
  PRO:        Full emotion suite, multilingual, voice synthesis, 3D avatar, AR/VR,
              100 memory profiles, all personas, creativity engine, gamified productivity.
  ENTERPRISE: Unlimited memory, voice cloning, GAN image mimicry, holographic projection,
              social media manager, white-label, API access, dedicated support.

Ethical principles
------------------
  Buddy never manipulates, demeans, or harms.  Every mimicry feature (voice cloning,
  digital twin) is gated behind explicit, recorded user consent.  AI-generated content
  is always disclosed.

Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
See framework/global_ai_sources_flow.py for the full pipeline specification.

Usage
-----
    from bots.buddy_bot import BuddyBot, Tier

    buddy = BuddyBot(tier=Tier.PRO, user_name="Jordan")
    response = buddy.chat("I'm feeling anxious about my presentation tomorrow.")
    print(response["message"])
"""

from __future__ import annotations

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from bots.buddy_bot.tiers import (
    Tier,
    TierConfig,
    get_tier_config,
    get_upgrade_path,
    FEATURE_CONVERSATIONAL_AI,
    FEATURE_EMOTION_DETECTION,
    FEATURE_BASIC_MEMORY,
    FEATURE_MULTILINGUAL,
    FEATURE_HUMOR_ENGINE,
    FEATURE_EMPATHY_ENGINE,
    FEATURE_VOICE_SYNTHESIS,
    FEATURE_AVATAR_2D,
    FEATURE_AVATAR_3D,
    FEATURE_MICRO_EXPRESSIONS,
    FEATURE_AR_VR_PRESENCE,
    FEATURE_ADVANCED_MEMORY,
    FEATURE_MILESTONE_TRACKER,
    FEATURE_CONFLICT_RESOLUTION,
    FEATURE_MOOD_SYNC,
    FEATURE_PERSONALITY_MODES,
    FEATURE_CREATIVITY_ENGINE,
    FEATURE_GAMIFIED_PRODUCTIVITY,
    FEATURE_VOICE_CLONING,
    FEATURE_GAN_IMAGE_MIMICRY,
    FEATURE_HOLOGRAPHIC_PROJECTION,
    FEATURE_REAL_TIME_TRANSLATION,
    FEATURE_WELLNESS_TRACKER,
    FEATURE_SOCIAL_MEDIA_MANAGER,
    FEATURE_WHITE_LABEL,
    FEATURE_API_ACCESS,
    FEATURE_DEDICATED_SUPPORT,
    # Media Production
    FEATURE_COMMERCIAL_PRODUCTION,
    FEATURE_RADIO_AD_STUDIO,
    FEATURE_VIDEO_AD_STUDIO,
    FEATURE_MUSIC_VIDEO_PRODUCTION,
    FEATURE_MOVIE_PRODUCTION,
    FEATURE_AI_ONLY_ADS,
    FEATURE_CLIENT_ASSET_ADS,
    # Self-Learning
    FEATURE_SELF_LEARNING,
    FEATURE_CAPABILITY_CHECK,
    FEATURE_TRAINING_SESSION,
    FEATURE_GITHUB_ACQUISITION,
    FEATURE_TOP_MODEL_REGISTRY,
)
from bots.buddy_bot.conversation_engine import (
    ConversationEngine,
    ConversationTone,
    SUPPORTED_LANGUAGES,
)
from bots.buddy_bot.emotion_engine import (
    EmotionEngine,
    EmotionLabel,
    EmotionSource,
)
from bots.buddy_bot.memory_system import (
    MemorySystem,
    MemorySystemError,
    MilestoneCategory,
    UserProfile,
)
from bots.buddy_bot.avatar_engine import (
    AvatarEngine,
    AvatarType,
    AvatarEnvironment,
    MicroExpression,
    AvatarEngineError,
)
from bots.buddy_bot.voice_engine import (
    VoiceEngine,
    VoiceTone,
    AccentStyle,
    VoiceEngineError,
)
from bots.buddy_bot.creativity_engine import (
    CreativityEngine,
    StoryGenre,
    SongMood,
    ArtMedium,
    CreativityEngineError,
)
from bots.buddy_bot.personality_engine import (
    PersonalityEngine,
    PersonaMode,
    PersonaTone,
)
from bots.buddy_bot.media_production_engine import (
    MediaProductionEngine,
    MediaProductionEngineError,
    ClientBrief,
    AdFormat,
    AdStyle,
    MusicVideoStyle,
    MovieGenre,
    CommercialScript,
    MusicVideoProject,
    MovieProject,
)
from bots.buddy_bot.self_learning_engine import (
    SelfLearningEngine,
    SelfLearningEngineError,
    LearningRecord,
    TrainingSession,
    GitHubAcquisitionResult,
    TOP_100_AI_MODELS,
)

from framework import GlobalAISourcesFlow


class BuddyBotError(Exception):
    """Raised when a Buddy Bot operation cannot be completed."""


class BuddyBotTierError(BuddyBotError):
    """Raised when a feature is not available on the current tier."""


class BuddyBot:
    """
    DreamCo's most human-like AI companion.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature access.
    user_name : str
        Primary user's display name (used to initialise a default profile).
    user_id : str
        Unique user identifier.
    initial_persona : PersonaMode
        Starting persona mode.
    active_language : str
        ISO 639-1 language code for the primary conversation language.
    """

    def __init__(
        self,
        tier: Tier = Tier.FREE,
        user_name: str = "Friend",
        user_id: str = "default_user",
        initial_persona: PersonaMode = PersonaMode.CASUAL_FRIEND,
        active_language: str = "en",
    ) -> None:
        self.tier = tier
        self.config: TierConfig = get_tier_config(tier)
        self.user_id = user_id

        # GLOBAL AI SOURCES FLOW
        self.flow = GlobalAISourcesFlow(bot_name="BuddyBot")

        # --- Sub-engines ---
        self.conversation = ConversationEngine(
            active_language=active_language,
        )
        self.emotion = EmotionEngine()
        self.memory = MemorySystem(max_profiles=self.config.max_memory_profiles)
        self.avatar = AvatarEngine(
            avatar_type=(
                AvatarType.AVATAR_3D
                if self.config.has_feature(FEATURE_AVATAR_3D)
                else AvatarType.AVATAR_2D
            ),
        )
        self.voice = VoiceEngine()
        self.creativity = CreativityEngine(user_id=user_id)
        self.personality = PersonalityEngine(initial_persona=initial_persona)
        self.media = MediaProductionEngine(user_id=user_id)
        self.learning = SelfLearningEngine()

        # Bootstrap memory profile for the primary user
        try:
            self.memory.create_profile(
                user_id=user_id,
                display_name=user_name,
                preferred_language=active_language,
            )
        except MemorySystemError:
            pass  # Profile may already exist in long-running sessions

    # ------------------------------------------------------------------
    # Tier enforcement
    # ------------------------------------------------------------------

    def _require_feature(self, feature: str) -> None:
        """Raise BuddyBotTierError if *feature* is not available on the current tier."""
        if not self.config.has_feature(feature):
            raise BuddyBotTierError(
                f"Feature '{feature}' is not available on the {self.config.name} tier. "
                f"Upgrade to unlock this capability."
            )

    # ------------------------------------------------------------------
    # Primary chat interface
    # ------------------------------------------------------------------

    def chat(self, message: str, tone: str = "neutral") -> dict:
        """
        The primary conversational interface for Buddy Bot.

        Buddy automatically:
        1. Detects emotion in the user's message.
        2. Selects an appropriate conversational tone.
        3. Generates a natural, human-like response.
        4. Renders an avatar frame matching the response emotion.
        5. Records the interaction in memory.
        6. Applies personality flavouring.

        Parameters
        ----------
        message : str
            The user's message.
        tone : str
            Optional tone override (e.g. ``"empathetic"``, ``"humorous"``).

        Returns
        -------
        dict with keys: ``message``, ``emotion``, ``tone``, ``avatar_frame``,
        ``persona``, ``tier``, ``language``.
        """
        self._require_feature(FEATURE_CONVERSATIONAL_AI)

        # 1. Emotion detection
        emotion_reading = self.emotion.detect_from_text(message)
        detected_emotion = emotion_reading.label

        # 2. Resolve tone
        tone_map: dict[str, ConversationTone] = {
            "neutral": ConversationTone.NEUTRAL,
            "happy": ConversationTone.HAPPY,
            "empathetic": ConversationTone.EMPATHETIC,
            "humorous": ConversationTone.HUMOROUS,
            "calm": ConversationTone.CALM,
            "excited": ConversationTone.EXCITED,
            "serious": ConversationTone.SERIOUS,
            "encouraging": ConversationTone.ENCOURAGING,
        }
        resolved_tone = tone_map.get(tone.lower(), ConversationTone.NEUTRAL)

        # Auto-override tone based on detected emotion for empathetic responses
        if self.config.has_feature(FEATURE_EMPATHY_ENGINE):
            emotion_tone_map: dict[EmotionLabel, ConversationTone] = {
                EmotionLabel.SADNESS: ConversationTone.EMPATHETIC,
                EmotionLabel.ANGER: ConversationTone.CALM,
                EmotionLabel.FEAR: ConversationTone.EMPATHETIC,
                EmotionLabel.STRESS: ConversationTone.CALM,
                EmotionLabel.ANXIETY: ConversationTone.EMPATHETIC,
                EmotionLabel.LONELINESS: ConversationTone.EMPATHETIC,
                EmotionLabel.JOY: ConversationTone.HAPPY,
                EmotionLabel.EXCITEMENT: ConversationTone.EXCITED,
                EmotionLabel.GRATITUDE: ConversationTone.HAPPY,
            }
            if resolved_tone == ConversationTone.NEUTRAL and detected_emotion in emotion_tone_map:
                resolved_tone = emotion_tone_map[detected_emotion]

        # 3. Generate conversational response
        turn = self.conversation.respond(message, tone=resolved_tone)
        base_response = turn.response

        # 4. Mood sync (PRO+)
        mood_response = ""
        if self.config.has_feature(FEATURE_MOOD_SYNC):
            mood_response = self.emotion.sync_mood(detected_emotion)
            if mood_response and mood_response not in base_response:
                base_response = f"{mood_response}\n\n{base_response}"

        # 5. Personality flavouring
        final_response = self.personality.flavour_response(base_response)

        # 6. Avatar frame
        avatar_frame = self.avatar.render_frame(
            emotion=detected_emotion.value,
            speech_text=final_response[:100],
        )

        # 7. Memory: record interaction
        try:
            self.memory.record_interaction(self.user_id)
            # Dynamically learn topics mentioned
            if self.config.has_feature(FEATURE_ADVANCED_MEMORY):
                self._extract_interests(message)
        except MemorySystemError:
            pass

        return {
            "message": final_response,
            "emotion": detected_emotion.value,
            "tone": resolved_tone.value,
            "avatar_frame": avatar_frame.to_dict(),
            "persona": self.personality.config.active_persona.value,
            "tier": self.tier.value,
            "language": self.conversation.active_language,
        }

    def process(self, message: str, **kwargs) -> dict:
        """Alias for chat() — BuddyAI process() compatibility."""
        return self.chat(message, **kwargs)

    # ------------------------------------------------------------------
    # Greeting & introduction
    # ------------------------------------------------------------------

    def greet(self) -> str:
        """Return a persona-appropriate greeting for the primary user."""
        try:
            profile = self.memory.get_profile(self.user_id)
            name = profile.display_name
        except MemorySystemError:
            name = "Friend"
        return self.personality.get_greeting(name)

    def introduce(self) -> str:
        """Return Buddy's full self-introduction."""
        return self.personality.introduce()

    # ------------------------------------------------------------------
    # Emotion features
    # ------------------------------------------------------------------

    def detect_emotion_from_voice(self, voice_descriptors: dict) -> dict:
        """
        Detect emotion from voice feature descriptors.

        Parameters
        ----------
        voice_descriptors : dict
            Keys: ``pitch_hz``, ``tempo_wpm``, ``energy_db``, ``tremor``,
            ``pause_ratio``.

        Returns
        -------
        dict
        """
        self._require_feature(FEATURE_EMOTION_DETECTION)
        reading = self.emotion.detect_from_voice(voice_descriptors)
        return reading.to_dict()

    def detect_emotion_from_camera(self, facial_signals: dict) -> dict:
        """
        Detect emotion from facial expression signals.

        Parameters
        ----------
        facial_signals : dict
            Keys: ``smile_score``, ``brow_furrow``, ``eye_openness``,
            ``lip_compression``, ``head_tilt``.

        Returns
        -------
        dict
        """
        self._require_feature(FEATURE_EMOTION_DETECTION)
        reading = self.emotion.detect_from_camera(facial_signals)
        return reading.to_dict()

    def boost_mood(self) -> dict:
        """Return a mood boost package for the user's current emotional state."""
        self._require_feature(FEATURE_MOOD_SYNC)
        current = self.emotion.get_current_mood()
        return self.emotion.boost_mood(current)

    # ------------------------------------------------------------------
    # Memory features
    # ------------------------------------------------------------------

    def add_life_milestone(
        self,
        title: str,
        description: str,
        category: MilestoneCategory,
        date_achieved: str,
        recurring_annually: bool = False,
    ) -> dict:
        """
        Add a life milestone for the primary user.

        Requires PRO+ (FEATURE_MILESTONE_TRACKER).
        """
        self._require_feature(FEATURE_MILESTONE_TRACKER)
        milestone = self.memory.add_milestone(
            user_id=self.user_id,
            title=title,
            description=description,
            category=category,
            date_achieved=date_achieved,
            recurring_annually=recurring_annually,
        )
        return milestone.to_dict()

    def add_anniversary(
        self,
        label: str,
        month: int,
        day: int,
        year_started: int = None,
    ) -> dict:
        """
        Add an important recurring anniversary or date.

        Requires PRO+ (FEATURE_MILESTONE_TRACKER).
        """
        self._require_feature(FEATURE_MILESTONE_TRACKER)
        date_obj = self.memory.add_important_date(
            user_id=self.user_id,
            label=label,
            month=month,
            day=day,
            year_started=year_started,
        )
        return date_obj.to_dict()

    def recall_user_context(self) -> str:
        """Return a natural-language summary of what Buddy knows about the user."""
        self._require_feature(FEATURE_BASIC_MEMORY)
        try:
            return self.memory.recall_context(self.user_id)
        except MemorySystemError as exc:
            return str(exc)

    def record_episode(self, title: str, summary: str, emotion: str = "neutral") -> dict:
        """Record a significant life episode in Buddy's memory."""
        self._require_feature(FEATURE_ADVANCED_MEMORY)
        episode = self.memory.record_episode(
            user_id=self.user_id,
            title=title,
            summary=summary,
            emotion_at_time=emotion,
        )
        return episode.to_dict()

    def _extract_interests(self, text: str) -> None:
        """Heuristically extract topics of interest from user text."""
        interest_keywords = {
            "music", "coding", "programming", "art", "travel", "food", "fitness",
            "sports", "reading", "writing", "film", "gaming", "fashion", "business",
            "investing", "meditation", "yoga", "cooking", "photography", "science",
            "history", "philosophy", "nature", "technology",
        }
        for word in text.lower().split():
            clean = word.strip(".,!?;:\"'")
            if clean in interest_keywords:
                try:
                    self.memory.learn_interest(self.user_id, clean)
                except MemorySystemError:
                    pass

    # ------------------------------------------------------------------
    # Avatar features
    # ------------------------------------------------------------------

    def enter_ar_mode(self) -> dict:
        """Switch Buddy's avatar to Augmented Reality mode (PRO+)."""
        self._require_feature(FEATURE_AR_VR_PRESENCE)
        return self.avatar.enter_ar_mode()

    def enter_vr_mode(self) -> dict:
        """Switch Buddy's avatar to full VR presence (PRO+)."""
        self._require_feature(FEATURE_AR_VR_PRESENCE)
        return self.avatar.enter_vr_mode()

    def enter_holographic_mode(self) -> dict:
        """Activate holographic projection (ENTERPRISE)."""
        self._require_feature(FEATURE_HOLOGRAPHIC_PROJECTION)
        return self.avatar.enter_holographic_mode()

    def customise_avatar(self, **kwargs) -> dict:
        """Customise Buddy's visual appearance."""
        result = self.avatar.customise_appearance(**kwargs)
        return result.to_dict()

    def request_digital_twin_consent(self) -> str:
        """Generate the consent request for Digital Twin / GAN mimicry."""
        self._require_feature(FEATURE_GAN_IMAGE_MIMICRY)
        return self.avatar.request_digital_twin_consent(self.user_id)

    def grant_digital_twin_consent(self, consent_text: str) -> dict:
        """Record Digital Twin consent and confirm activation."""
        self._require_feature(FEATURE_GAN_IMAGE_MIMICRY)
        record = self.avatar.grant_consent(self.user_id, "digital_twin", consent_text)
        return record.to_dict()

    def create_digital_twin(self, image_data_reference: str) -> dict:
        """Create a GAN-powered digital twin (ENTERPRISE, consent required)."""
        self._require_feature(FEATURE_GAN_IMAGE_MIMICRY)
        return self.avatar.create_digital_twin(self.user_id, image_data_reference)

    # ------------------------------------------------------------------
    # Voice features
    # ------------------------------------------------------------------

    def synthesise_speech(self, text: str, profile_id: str = None) -> dict:
        """Synthesise text to speech using Buddy's voice engine (PRO+)."""
        self._require_feature(FEATURE_VOICE_SYNTHESIS)
        output = self.voice.synthesise(text, profile_id=profile_id)
        return output.to_dict()

    def morph_voice(
        self,
        tone: str = None,
        accent: str = None,
        pitch_delta: float = 0.0,
        speed_delta: int = 0,
    ) -> dict:
        """Adjust Buddy's voice in real time (PRO+)."""
        self._require_feature(FEATURE_VOICE_SYNTHESIS)
        tone_enum = VoiceTone(tone) if tone else None
        accent_enum = AccentStyle(accent) if accent else None
        profile = self.voice.morph_voice(
            tone=tone_enum,
            accent=accent_enum,
            pitch_delta=pitch_delta,
            speed_delta=speed_delta,
        )
        return profile.to_dict()

    def request_voice_clone_consent(self) -> str:
        """Generate the voice cloning consent request text (ENTERPRISE)."""
        self._require_feature(FEATURE_VOICE_CLONING)
        return self.voice.request_voice_clone_consent(self.user_id)

    def grant_voice_clone_consent(
        self,
        consent_text: str,
        voice_sample_reference: str,
    ) -> dict:
        """Record voice cloning consent and create the cloned voice profile (ENTERPRISE)."""
        self._require_feature(FEATURE_VOICE_CLONING)
        return self.voice.grant_voice_clone_consent(
            self.user_id,
            consent_text,
            voice_sample_reference,
        )

    # ------------------------------------------------------------------
    # Multilingual / translation
    # ------------------------------------------------------------------

    def translate(self, text: str, source_lang: str, target_lang: str) -> dict:
        """Translate *text* between two languages (PRO+)."""
        self._require_feature(FEATURE_REAL_TIME_TRANSLATION)
        result = self.conversation.translate(text, source_lang, target_lang)
        return result.to_dict()

    def set_language(self, lang_code: str) -> None:
        """Switch the active conversation language (PRO+)."""
        self._require_feature(FEATURE_MULTILINGUAL)
        self.conversation.set_language(lang_code)

    def list_supported_languages(self) -> list[dict]:
        """Return all supported languages."""
        self._require_feature(FEATURE_MULTILINGUAL)
        return self.conversation.list_supported_languages()

    # ------------------------------------------------------------------
    # Creativity features
    # ------------------------------------------------------------------

    def start_story(
        self,
        genre: str = "inspirational",
        protagonist_name: str = "Alex",
    ) -> dict:
        """Begin an interactive story (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        genre_enum = StoryGenre(genre)
        chapter = self.creativity.start_story(genre_enum, protagonist_name)
        self.creativity.award_xp(10, "story_started")
        return chapter.to_dict()

    def continue_story(self, choice_index: int, protagonist_name: str = "Alex") -> dict:
        """Advance the active story (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        chapter = self.creativity.continue_story(choice_index, protagonist_name)
        self.creativity.award_xp(5, "story_advanced")
        return chapter.to_dict()

    def write_song(
        self,
        theme: str,
        mood: str = "uplifting",
        title: str = None,
    ) -> dict:
        """Generate an original song (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        mood_enum = SongMood(mood)
        song = self.creativity.write_song(theme, mood_enum, title)
        self.creativity.award_xp(20, "song_written")
        return song.to_dict()

    def get_art_tip(self, medium: str = "digital_painting") -> str:
        """Return an art mentorship tip for *medium* (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        medium_enum = ArtMedium(medium)
        return self.creativity.get_art_tip(medium_enum)

    def brainstorm(self, topic: str, count: int = 5) -> list[str]:
        """Generate creative brainstorming ideas around *topic* (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        return self.creativity.brainstorm(topic, count)

    def write_poem(self, theme: str, lines: int = 8) -> str:
        """Generate an original poem (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        return self.creativity.write_poem(theme, lines)

    def get_daily_challenge(self) -> dict:
        """Issue today's gamified productivity challenge (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        challenge = self.creativity.get_daily_challenge()
        return challenge.to_dict()

    def complete_challenge(self, challenge_id: str) -> dict:
        """Mark a challenge as completed and award XP (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        return self.creativity.complete_challenge(challenge_id)

    def get_achievements(self) -> list[dict]:
        """Return all achievements (locked and unlocked) (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        return self.creativity.get_achievements()

    def unlock_achievement(self, achievement_id: str) -> dict:
        """Unlock an achievement by ID (PRO+)."""
        self._require_feature(FEATURE_GAMIFIED_PRODUCTIVITY)
        ach = self.creativity.unlock_achievement(achievement_id)
        return ach.to_dict()

    def podcast_intro(self, show_title: str, episode_topic: str) -> str:
        """Generate a podcast intro with Buddy as co-host (PRO+)."""
        self._require_feature(FEATURE_CREATIVITY_ENGINE)
        return self.creativity.podcast_intro(show_title, episode_topic)

    # ------------------------------------------------------------------
    # Personality
    # ------------------------------------------------------------------

    def set_persona(self, persona: str, blend_with: str = None, blend_ratio: float = 1.0) -> dict:
        """Switch Buddy's active persona mode (PRO+)."""
        self._require_feature(FEATURE_PERSONALITY_MODES)
        persona_enum = PersonaMode(persona)
        blend_enum = PersonaMode(blend_with) if blend_with else None
        config = self.personality.set_persona(persona_enum, blend_enum, blend_ratio)
        return config.to_dict()

    def list_personas(self) -> list[dict]:
        """Return all available persona modes."""
        return self.personality.list_personas()

    def conflict_resolution(self, situation: str) -> str:
        """Provide AI-powered conflict resolution guidance (PRO+)."""
        self._require_feature(FEATURE_CONFLICT_RESOLUTION)
        return self.conversation.resolve_conflict(situation)

    def ethical_check(self, request: str) -> dict:
        """Check if a request is within Buddy's ethical boundaries."""
        is_ethical, reasoning = self.personality.is_request_ethical(request)
        return {"is_ethical": is_ethical, "reasoning": reasoning}

    # ------------------------------------------------------------------
    # Wellness
    # ------------------------------------------------------------------

    def wellness_check_in(self, how_are_you: str) -> dict:
        """
        Conduct a wellness check-in based on the user's self-report.

        Parameters
        ----------
        how_are_you : str
            The user's free-text response to "How are you?"

        Returns
        -------
        dict with ``message``, ``music_recommendation``, ``emotion``.
        """
        self._require_feature(FEATURE_WELLNESS_TRACKER)
        reading = self.emotion.detect_from_text(how_are_you)
        boost = self.emotion.boost_mood(reading.label)
        return boost

    # ------------------------------------------------------------------
    # System status
    # ------------------------------------------------------------------

    def system_status(self) -> dict:
        """Return a comprehensive status snapshot of Buddy Bot."""
        try:
            profile = self.memory.get_profile(self.user_id)
            user_dict = profile.to_dict()
        except MemorySystemError:
            user_dict = {"user_id": self.user_id}

        return {
            "tier": self.tier.value,
            "tier_name": self.config.name,
            "user": user_dict,
            "conversation": self.conversation.to_dict(),
            "emotion": self.emotion.to_dict(),
            "memory": self.memory.to_dict(),
            "avatar": self.avatar.to_dict(),
            "voice": self.voice.to_dict(),
            "creativity": self.creativity.to_dict(),
            "personality": self.personality.to_dict(),
            "media": self.media.to_dict(),
            "learning": self.learning.to_dict(),
            "features_enabled": self.config.features,
        }

    # ------------------------------------------------------------------
    # Media Production — Commercials
    # ------------------------------------------------------------------

    def create_commercial(
        self,
        client_name: str,
        product_or_service: str,
        target_audience: str,
        key_message: str,
        ad_format: str = "video_30s",
        ad_style: str = "fully_ai",
        tagline: str = "",
        call_to_action: str = "Visit our website",
        client_assets: list = None,
        tone: str = "professional",
    ) -> dict:
        """
        Produce a fully scripted commercial for a client (PRO+).

        Buddy generates every element of the ad — script, voice direction,
        visual direction, and music direction.  The ad can be fully AI-generated
        or built around client-supplied photos and assets.

        Parameters
        ----------
        client_name : str
            Name of the client / brand.
        product_or_service : str
            What is being advertised.
        target_audience : str
            Who the ad is aimed at.
        key_message : str
            The single most important thing the ad must communicate.
        ad_format : str
            One of: ``"radio_30s"``, ``"radio_60s"``, ``"video_15s"``,
            ``"video_30s"``, ``"video_60s"``, ``"social_reel"``,
            ``"podcast_ad"``, ``"banner"``.
        ad_style : str
            One of: ``"fully_ai"``, ``"client_assets"``, ``"hybrid"``.
        tagline : str
            Brand tagline (auto-generated if empty).
        call_to_action : str
            Final CTA line for the ad.
        client_assets : list | None
            References to client-supplied photos, logos, or audio files.
        tone : str
            Creative tone (e.g. ``"professional"``, ``"fun"``, ``"inspirational"``).

        Returns
        -------
        dict  — CommercialScript serialised to dict.
        """
        self._require_feature(FEATURE_COMMERCIAL_PRODUCTION)

        brief = ClientBrief(
            client_name=client_name,
            product_or_service=product_or_service,
            target_audience=target_audience,
            key_message=key_message,
            tone=tone,
            call_to_action=call_to_action,
            tagline=tagline,
            assets_provided=client_assets or [],
        )

        fmt = AdFormat(ad_format)
        style = AdStyle(ad_style)

        # Style-specific tier checks
        if style == AdStyle.CLIENT_ASSETS:
            self._require_feature(FEATURE_CLIENT_ASSET_ADS)
        if style == AdStyle.FULLY_AI:
            self._require_feature(FEATURE_AI_ONLY_ADS)

        script = self.media.create_commercial(brief, fmt, style)
        self.creativity.award_xp(30, "commercial_produced")
        return script.to_dict()

    def create_radio_ad(
        self,
        client_name: str,
        product_or_service: str,
        target_audience: str,
        key_message: str,
        duration: str = "30s",
        ad_style: str = "fully_ai",
        tagline: str = "",
        call_to_action: str = "Call us today",
        client_assets: list = None,
    ) -> dict:
        """
        Produce a radio advertisement for a client (PRO+).

        Parameters
        ----------
        client_name : str
            Client / brand name.
        product_or_service : str
            Advertised offering.
        target_audience : str
            Intended audience.
        key_message : str
            Core message of the ad.
        duration : str
            ``"30s"`` or ``"60s"``.
        ad_style : str
            ``"fully_ai"``, ``"client_assets"``, or ``"hybrid"``.
        tagline : str
            Brand tagline.
        call_to_action : str
            Closing CTA.
        client_assets : list | None
            Client-supplied audio or asset references.

        Returns
        -------
        dict — CommercialScript serialised to dict.
        """
        self._require_feature(FEATURE_RADIO_AD_STUDIO)
        brief = ClientBrief(
            client_name=client_name,
            product_or_service=product_or_service,
            target_audience=target_audience,
            key_message=key_message,
            call_to_action=call_to_action,
            tagline=tagline,
            assets_provided=client_assets or [],
        )
        style = AdStyle(ad_style)
        script = self.media.create_radio_ad(brief, duration, style)
        self.creativity.award_xp(25, "radio_ad_produced")
        return script.to_dict()

    def list_productions(self) -> list:
        """Return all produced commercials (PRO+)."""
        self._require_feature(FEATURE_COMMERCIAL_PRODUCTION)
        return self.media.list_productions()

    # ------------------------------------------------------------------
    # Media Production — Music Videos
    # ------------------------------------------------------------------

    def create_music_video(
        self,
        artist_name: str,
        song_title: str,
        style: str = "narrative",
        color_palette: str = "warm cinematic",
        vfx_notes: str = "",
    ) -> dict:
        """
        Generate a complete music video production package (PRO+).

        Buddy produces a storyboard, shot list, visual direction brief,
        and VFX notes for the artist's track.

        Parameters
        ----------
        artist_name : str
            Name of the artist or band.
        song_title : str
            Song being visualised.
        style : str
            One of: ``"narrative"``, ``"performance"``, ``"abstract"``,
            ``"lyric_video"``, ``"animated"``, ``"documentary"``.
        color_palette : str
            Colour-grading direction (e.g. ``"warm cinematic"``).
        vfx_notes : str
            Any VFX or CGI requirements.

        Returns
        -------
        dict — MusicVideoProject serialised to dict.
        """
        self._require_feature(FEATURE_MUSIC_VIDEO_PRODUCTION)
        style_enum = MusicVideoStyle(style)
        mv = self.media.create_music_video(artist_name, song_title, style_enum, color_palette, vfx_notes)
        self.creativity.award_xp(40, "music_video_produced")
        return mv.to_dict()

    def list_music_videos(self) -> list:
        """Return all music video projects (PRO+)."""
        self._require_feature(FEATURE_MUSIC_VIDEO_PRODUCTION)
        return self.media.list_music_videos()

    # ------------------------------------------------------------------
    # Media Production — Movies
    # ------------------------------------------------------------------

    def create_movie(
        self,
        title: str,
        genre: str = "short_film",
        logline: str = "",
        runtime_minutes: int = 20,
    ) -> dict:
        """
        Generate a complete movie / short-film production package (ENTERPRISE).

        Buddy produces a logline, synopsis, act breakdown, cast descriptions,
        key scenes, cinematography notes, and score direction.

        Parameters
        ----------
        title : str
            Working title of the film.
        genre : str
            One of: ``"action"``, ``"drama"``, ``"comedy"``, ``"horror"``,
            ``"documentary"``, ``"romance"``, ``"thriller"``,
            ``"science_fiction"``, ``"animation"``, ``"short_film"``.
        logline : str
            One-sentence pitch (auto-generated if empty).
        runtime_minutes : int
            Target runtime in minutes.

        Returns
        -------
        dict — MovieProject serialised to dict.
        """
        self._require_feature(FEATURE_MOVIE_PRODUCTION)
        genre_enum = MovieGenre(genre)
        movie = self.media.create_movie(title, genre_enum, logline, runtime_minutes)
        self.creativity.award_xp(100, "movie_produced")
        return movie.to_dict()

    def list_movies(self) -> list:
        """Return all movie projects (ENTERPRISE)."""
        self._require_feature(FEATURE_MOVIE_PRODUCTION)
        return self.media.list_movies()

    def media_production_summary(self) -> dict:
        """Return a summary of all media productions (PRO+)."""
        self._require_feature(FEATURE_COMMERCIAL_PRODUCTION)
        return self.media.production_summary()

    # ------------------------------------------------------------------
    # Self-Learning — Capability checking
    # ------------------------------------------------------------------

    def can_do(self, task_description: str) -> bool:
        """
        Return True if Buddy currently has a capability matching the task (PRO+).

        Parameters
        ----------
        task_description : str
            Natural-language description of what the client wants.
        """
        self._require_feature(FEATURE_CAPABILITY_CHECK)
        return self.learning.can_do(task_description)

    def check_capability(self, task_description: str) -> dict:
        """
        Perform a full capability gap analysis for a task description (PRO+).

        If Buddy cannot do the task, it automatically:
        1. Identifies the missing capabilities.
        2. Recommends the top AI models that can help.
        3. Provides a GitHub acquisition plan.

        Parameters
        ----------
        task_description : str
            What the client wants Buddy to do.

        Returns
        -------
        dict with keys: ``can_do``, ``matched_capabilities``, ``gap``.
        """
        self._require_feature(FEATURE_CAPABILITY_CHECK)
        return self.learning.check_capability(task_description)

    # ------------------------------------------------------------------
    # Self-Learning — Learning from top AI models
    # ------------------------------------------------------------------

    def learn_from_top_models(
        self,
        capability: str,
        top_n: int = 5,
    ) -> list:
        """
        Ask the top-N AI models most relevant to *capability* to teach Buddy (PRO+).

        Buddy consults the global top-100 model registry, identifies the best
        models for the requested skill, simulates querying them for guidance,
        records the lessons, and adds the capability to its registry.

        Parameters
        ----------
        capability : str
            The skill or topic for Buddy to learn.
        top_n : int
            How many models to consult (1–10).

        Returns
        -------
        list[dict] — Learning records for each model consulted.
        """
        self._require_feature(FEATURE_SELF_LEARNING)
        records = self.learning.ask_top_models(capability, top_n)
        return [r.to_dict() for r in records]

    # ------------------------------------------------------------------
    # Self-Learning — GitHub code acquisition
    # ------------------------------------------------------------------

    def acquire_code_from_github(self, capability: str) -> dict:
        """
        Search GitHub for code that would give Buddy a new capability (ENTERPRISE).

        All discovered repositories are quarantined for human review before
        being merged into the DreamCo codebase.

        Parameters
        ----------
        capability : str
            The capability to search GitHub for.

        Returns
        -------
        dict — GitHubAcquisitionResult serialised to dict.
        """
        self._require_feature(FEATURE_GITHUB_ACQUISITION)
        result = self.learning.search_github_for_code(capability)
        return result.to_dict()

    # ------------------------------------------------------------------
    # Self-Learning — Training sessions
    # ------------------------------------------------------------------

    def run_training_session(
        self,
        focus_specialties: list = None,
    ) -> dict:
        """
        Run one complete self-training session against all 100 top AI models (ENTERPRISE).

        Buddy cycles through the entire top-100 model registry, identifies any
        capabilities those models have that Buddy does not yet possess, and
        records a learning outcome for each new capability acquired.

        Parameters
        ----------
        focus_specialties : list[str] | None
            If provided, only models with those specialties are consulted.
            Omit to train against all 100 models.

        Returns
        -------
        dict — TrainingSession serialised to dict.
        """
        self._require_feature(FEATURE_TRAINING_SESSION)
        session = self.learning.run_training_session(focus_specialties)
        return session.to_dict()

    def list_capabilities(self) -> list:
        """Return all of Buddy's currently known capabilities (PRO+)."""
        self._require_feature(FEATURE_SELF_LEARNING)
        return self.learning.list_capabilities()

    def get_learning_log(self, limit: int = 50) -> list:
        """Return the most recent learning records (PRO+)."""
        self._require_feature(FEATURE_SELF_LEARNING)
        return self.learning.get_learning_log(limit)

    def get_top_models(self, limit: int = 10) -> list:
        """Return the top AI models from the global registry (ENTERPRISE)."""
        self._require_feature(FEATURE_TOP_MODEL_REGISTRY)
        return self.learning.get_top_models(limit)

    def get_training_sessions(self) -> list:
        """Return all completed training session records (ENTERPRISE)."""
        self._require_feature(FEATURE_TRAINING_SESSION)
        return self.learning.get_training_sessions()



    def describe_tier(self) -> str:
        """Return a human-readable tier description."""
        cfg = self.config
        lines = [
            f"=== Buddy Bot — {cfg.name} Tier ===",
            f"Price      : ${cfg.price_usd_monthly:.2f}/month",
            f"Memory     : {'Unlimited' if cfg.is_unlimited_memory() else str(cfg.max_memory_profiles)} profiles",
            f"Languages  : {cfg.max_languages}+",
            f"Personas   : {'Unlimited' if cfg.max_personas is None else str(cfg.max_personas)}",
            f"Support    : {cfg.support_level}",
            "",
            "Features:",
        ]
        for feat in cfg.features:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        return "\n".join(lines)

    def show_upgrade_path(self) -> str:
        """Return information about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            return f"You're already on the top Buddy Bot tier: {self.config.name}."
        current_features = set(self.config.features)
        new_features = [f for f in next_cfg.features if f not in current_features]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features unlocked:",
        ]
        for f in new_features:
            lines.append(f"  + {f.replace('_', ' ').title()}")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # BuddyAI / BuddyOS integration
    # ------------------------------------------------------------------

    def register_with_buddy(self, buddy_bot_instance: object) -> None:
        """Register this BuddyBot instance with a BuddyAI orchestrator."""
        buddy_bot_instance.register_bot("buddy_bot", self)
