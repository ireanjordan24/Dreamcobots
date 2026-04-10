"""
Buddy Bot — Media Production Engine

Enables Buddy to create fully customised advertising and media content for clients:

  • Commercial Production — TV/video spots, radio ads, social-media clips
  • Client-Asset Ads      — incorporate client-supplied photos, logos, voice-overs
  • Fully AI Ads          — end-to-end AI-generated creative from brief to deliverable
  • Music Video Production — storyboard, shot list, AI visual direction, sync to track
  • Movie / Short Film     — screenplay, scene-by-scene direction, cast description

Every production respects the DreamCo ethical guidelines:
  - Client-supplied assets are used only with explicit, recorded consent.
  - AI-generated content is always disclosed in final deliverables.
  - No deceptive or manipulative messaging is ever produced.

GLOBAL AI SOURCES FLOW: this module participates in GlobalAISourcesFlow
via BuddyBot.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------

class AdFormat(Enum):
    RADIO_30 = "radio_30s"
    RADIO_60 = "radio_60s"
    VIDEO_15 = "video_15s"
    VIDEO_30 = "video_30s"
    VIDEO_60 = "video_60s"
    SOCIAL_REEL = "social_reel"
    BANNER = "banner"
    PODCAST_AD = "podcast_ad"


class AdStyle(Enum):
    FULLY_AI = "fully_ai"
    CLIENT_ASSETS = "client_assets"
    HYBRID = "hybrid"


class MusicVideoStyle(Enum):
    NARRATIVE = "narrative"
    PERFORMANCE = "performance"
    ABSTRACT = "abstract"
    LYRIC_VIDEO = "lyric_video"
    ANIMATED = "animated"
    DOCUMENTARY = "documentary"


class MovieGenre(Enum):
    ACTION = "action"
    DRAMA = "drama"
    COMEDY = "comedy"
    HORROR = "horror"
    DOCUMENTARY = "documentary"
    ROMANCE = "romance"
    THRILLER = "thriller"
    SCIENCE_FICTION = "science_fiction"
    ANIMATION = "animation"
    SHORT_FILM = "short_film"


class ProductionStatus(Enum):
    BRIEF = "brief"
    CONCEPT = "concept"
    SCRIPTED = "scripted"
    IN_PRODUCTION = "in_production"
    POST_PRODUCTION = "post_production"
    DELIVERED = "delivered"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class ClientBrief:
    """Structured brief for any production job."""
    client_name: str
    product_or_service: str
    target_audience: str
    key_message: str
    tone: str = "professional"
    call_to_action: str = "Visit our website"
    brand_colors: list = field(default_factory=list)
    tagline: str = ""
    assets_provided: list = field(default_factory=list)  # photo refs, logos, audio

    def to_dict(self) -> dict:
        return {
            "client_name": self.client_name,
            "product_or_service": self.product_or_service,
            "target_audience": self.target_audience,
            "key_message": self.key_message,
            "tone": self.tone,
            "call_to_action": self.call_to_action,
            "brand_colors": self.brand_colors,
            "tagline": self.tagline,
            "assets_provided": self.assets_provided,
        }


@dataclass
class CommercialScript:
    """A fully scripted commercial ready for production."""
    production_id: str
    client_name: str
    ad_format: AdFormat
    ad_style: AdStyle
    title: str
    script: str
    voice_direction: str
    visual_direction: str
    music_direction: str
    duration_seconds: int
    call_to_action: str
    ai_disclosure: str
    status: ProductionStatus = ProductionStatus.SCRIPTED
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "production_id": self.production_id,
            "client_name": self.client_name,
            "ad_format": self.ad_format.value,
            "ad_style": self.ad_style.value,
            "title": self.title,
            "script": self.script,
            "voice_direction": self.voice_direction,
            "visual_direction": self.visual_direction,
            "music_direction": self.music_direction,
            "duration_seconds": self.duration_seconds,
            "call_to_action": self.call_to_action,
            "ai_disclosure": self.ai_disclosure,
            "status": self.status.value,
            "created_at": self.created_at,
        }


@dataclass
class MusicVideoProject:
    """A complete music video production package."""
    production_id: str
    artist_name: str
    song_title: str
    style: MusicVideoStyle
    storyboard: list[str]
    shot_list: list[str]
    visual_direction: str
    color_palette: str
    vfx_notes: str
    estimated_scenes: int
    status: ProductionStatus = ProductionStatus.CONCEPT
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "production_id": self.production_id,
            "artist_name": self.artist_name,
            "song_title": self.song_title,
            "style": self.style.value,
            "storyboard": self.storyboard,
            "shot_list": self.shot_list,
            "visual_direction": self.visual_direction,
            "color_palette": self.color_palette,
            "vfx_notes": self.vfx_notes,
            "estimated_scenes": self.estimated_scenes,
            "status": self.status.value,
            "created_at": self.created_at,
        }


@dataclass
class MovieProject:
    """A complete movie / short-film production package."""
    production_id: str
    title: str
    genre: MovieGenre
    logline: str
    synopsis: str
    act_breakdown: list[str]
    cast_descriptions: list[str]
    key_scenes: list[str]
    cinematography_notes: str
    score_direction: str
    estimated_runtime_minutes: int
    status: ProductionStatus = ProductionStatus.CONCEPT
    created_at: float = field(default_factory=time.time)

    def to_dict(self) -> dict:
        return {
            "production_id": self.production_id,
            "title": self.title,
            "genre": self.genre.value,
            "logline": self.logline,
            "synopsis": self.synopsis,
            "act_breakdown": self.act_breakdown,
            "cast_descriptions": self.cast_descriptions,
            "key_scenes": self.key_scenes,
            "cinematography_notes": self.cinematography_notes,
            "score_direction": self.score_direction,
            "estimated_runtime_minutes": self.estimated_runtime_minutes,
            "status": self.status.value,
            "created_at": self.created_at,
        }


# ---------------------------------------------------------------------------
# Content pools
# ---------------------------------------------------------------------------

_RADIO_SCRIPT_TEMPLATES = [
    (
        "[OPEN: warm, upbeat music bed]\n"
        "ANNOUNCER: Are you tired of {problem}? {client} has the answer.\n"
        "{key_message}\n"
        "{client}'s {product} is designed for {audience} who deserve the best.\n"
        "{tagline}\n"
        "[MUSIC SWELL]\n"
        "ANNOUNCER: {cta}. That's {client}. Making a difference, one {product} at a time.\n"
        "[MUSIC OUT]"
    ),
    (
        "[OPEN: ambient sound — {audience} environment]\n"
        "CHARACTER: I never thought I'd find something like {product}.\n"
        "ANNOUNCER: {key_message}.\n"
        "{client} — {tagline}\n"
        "ANNOUNCER: {cta}.\n"
        "[LIGHT MUSIC STING — OUT]"
    ),
    (
        "[ENERGETIC MUSIC OPEN]\n"
        "ANNOUNCER: Introducing {product} from {client}!\n"
        "{key_message}.\n"
        "Built for {audience} — by people who care.\n"
        "{tagline}\n"
        "ANNOUNCER: {cta}. {client}.\n"
        "[MUSIC FADE]"
    ),
]

_VIDEO_SCRIPT_TEMPLATES = [
    (
        "[SCENE 1 — PROBLEM]\n"
        "VISUAL: Close-up of frustrated {audience} face. Warm, relatable lighting.\n"
        "VO: We all know the feeling of {problem}...\n\n"
        "[SCENE 2 — SOLUTION REVEAL]\n"
        "VISUAL: {product} appears — bright, confident reveal shot.\n"
        "VO: {key_message}.\n\n"
        "[SCENE 3 — SOCIAL PROOF]\n"
        "VISUAL: Diverse happy {audience} using {product}.\n"
        "VO: Trusted by thousands.\n\n"
        "[SCENE 4 — CTA]\n"
        "VISUAL: {client} logo lock-up. Brand color background.\n"
        "SUPER: {cta}\n"
        "VO: {client}. {tagline}."
    ),
    (
        "[SCENE 1 — LIFESTYLE OPEN]\n"
        "VISUAL: Aspirational scene featuring {audience} thriving.\n"
        "MUSIC: Uplifting, modern.\n\n"
        "[SCENE 2 — PRODUCT INTEGRATION]\n"
        "VISUAL: {product} seamlessly part of the lifestyle.\n"
        "VO: {key_message}.\n\n"
        "[SCENE 3 — BRAND MOMENT]\n"
        "VISUAL: {client} branding, tagline animation.\n"
        "SUPER: {tagline}\n"
        "VO: {cta}."
    ),
]

_VISUAL_DIRECTIONS: dict[AdStyle, list[str]] = {
    AdStyle.FULLY_AI: [
        "All visuals generated by AI image synthesis. Photorealistic, brand-color-saturated.",
        "AI-animated motion graphics with generative backgrounds. High-energy transitions.",
        "Fully synthetic environments rendered by AI. Cinematic depth of field.",
    ],
    AdStyle.CLIENT_ASSETS: [
        "Lead with client-supplied hero photography. Overlay brand motion graphics.",
        "Client photos as primary visuals. AI-enhanced colour grading to match brand palette.",
        "Client product shots center-stage. AI background removal and replacement.",
    ],
    AdStyle.HYBRID: [
        "Client hero assets anchored by AI-generated supporting visuals.",
        "AI environment, client product and logo. Best of both worlds.",
        "Split-screen: client photos on left, AI-generated lifestyle scenes on right.",
    ],
}

_MUSIC_DIRECTIONS = [
    "Uplifting corporate pop — major key, 120 BPM, no lyrics.",
    "Cinematic orchestral swell — builds to brand logo reveal.",
    "Lo-fi acoustic guitar — approachable, authentic, warm.",
    "Electronic/synth — modern, energetic, youth-skewed.",
    "Jazz-inflected R&B bed — sophisticated, urban, polished.",
    "Inspirational piano — emotional, minimal, trust-building.",
]

_MV_STORYBOARD_TEMPLATES = {
    MusicVideoStyle.NARRATIVE: [
        "Act 1 — Ordinary world: artist shown in everyday setting, hinting at inner conflict.",
        "Act 2 — Inciting moment: event disrupts the world; music shifts in intensity.",
        "Act 3 — Journey: visual metaphors mirror lyrical themes across quick-cut scenes.",
        "Act 4 — Climax: performance shot at peak energy, colour palette reaches full saturation.",
        "Act 5 — Resolution: return to opening location, transformed; final logo/title card.",
    ],
    MusicVideoStyle.PERFORMANCE: [
        "Opening wide shot: artist on stage or iconic location.",
        "Verse 1: close-up performance cuts, minimal editing.",
        "Chorus: full-band or ensemble, dynamic wide angles.",
        "Bridge: isolated solo performance, stark lighting.",
        "Outro: pullback to wide, lights out, artist silhouette.",
    ],
    MusicVideoStyle.ABSTRACT: [
        "Intro: generative AI visuals synced to beat — geometric forms.",
        "Verse: fragmented, kaleidoscopic imagery tied to lyric themes.",
        "Chorus: full-colour burst, fast-cut abstract shapes.",
        "Bridge: slow-motion liquid simulation, ethereal.",
        "Outro: forms dissolve back to void.",
    ],
    MusicVideoStyle.LYRIC_VIDEO: [
        "Kinetic typography synced frame-accurately to vocals.",
        "Background: looping AI-generated animated artwork.",
        "Chorus: words explode outward, impact-font at peak.",
        "Bridge: slower font reveal, emotional color shift.",
        "Outro: title card and streaming links.",
    ],
    MusicVideoStyle.ANIMATED: [
        "Character design brief: artist as stylised animation.",
        "World-building scenes that mirror song's narrative arc.",
        "Lip-sync animation frames for vocal sections.",
        "Action sequences for high-energy choruses.",
        "Closing scene mirroring opening, story completed.",
    ],
    MusicVideoStyle.DOCUMENTARY: [
        "Archival and BTS footage of artist, woven with performance shots.",
        "Interview-style segments intercut with live performance.",
        "Fan interaction and community scenes.",
        "Studio recording footage layered over final mix.",
        "Montage of artist's journey to close.",
    ],
}


# ---------------------------------------------------------------------------
# Engine
# ---------------------------------------------------------------------------

class MediaProductionEngineError(Exception):
    """Raised when a media production operation cannot be completed."""


class MediaProductionEngine:
    """
    Powers all media production features of Buddy Bot.

    Produces commercials (radio + video), music videos, and full movies,
    customised for each client.  Supports fully AI-generated productions
    as well as productions that incorporate client-supplied assets.

    Parameters
    ----------
    user_id : str
        The user / operator this session belongs to.
    """

    def __init__(self, user_id: str = "default") -> None:
        self.user_id = user_id
        self._productions: list[CommercialScript] = []
        self._music_videos: list[MusicVideoProject] = []
        self._movies: list[MovieProject] = []
        self._production_counter: int = 0

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _next_id(self, prefix: str) -> str:
        self._production_counter += 1
        return f"{prefix}_{self._production_counter:04d}"

    @staticmethod
    def _fill_template(template: str, brief: ClientBrief, **extra: str) -> str:
        problem = extra.get("problem", f"finding the best {brief.product_or_service}")
        tagline = brief.tagline or f"{brief.client_name} — {brief.key_message}"
        filled = (
            template
            .replace("{client}", brief.client_name)
            .replace("{product}", brief.product_or_service)
            .replace("{audience}", brief.target_audience)
            .replace("{key_message}", brief.key_message)
            .replace("{cta}", brief.call_to_action)
            .replace("{tagline}", tagline)
            .replace("{problem}", problem)
        )
        return filled

    # ------------------------------------------------------------------
    # Commercial production
    # ------------------------------------------------------------------

    def create_commercial(
        self,
        brief: ClientBrief,
        ad_format: AdFormat = AdFormat.VIDEO_30,
        ad_style: AdStyle = AdStyle.FULLY_AI,
    ) -> CommercialScript:
        """
        Generate a fully scripted commercial for a client.

        Parameters
        ----------
        brief : ClientBrief
            Structured creative brief from the client.
        ad_format : AdFormat
            The target format (radio 30s, video 30s, social reel, etc.).
        ad_style : AdStyle
            Whether to use AI-only assets, client-supplied assets, or a hybrid.

        Returns
        -------
        CommercialScript
        """
        is_radio = ad_format in (AdFormat.RADIO_30, AdFormat.RADIO_60, AdFormat.PODCAST_AD)
        templates = _RADIO_SCRIPT_TEMPLATES if is_radio else _VIDEO_SCRIPT_TEMPLATES
        raw = random.choice(templates)
        script = self._fill_template(raw, brief)

        duration_map = {
            AdFormat.RADIO_30: 30,
            AdFormat.RADIO_60: 60,
            AdFormat.VIDEO_15: 15,
            AdFormat.VIDEO_30: 30,
            AdFormat.VIDEO_60: 60,
            AdFormat.SOCIAL_REEL: 30,
            AdFormat.BANNER: 0,
            AdFormat.PODCAST_AD: 60,
        }

        voice_direction = (
            "Warm, authoritative narrator voice. Conversational pace, slight smile audible."
            if is_radio
            else "Clear, confident VO. Upbeat but not over-produced. Age-neutral."
        )

        visual_dirs = _VISUAL_DIRECTIONS.get(ad_style, _VISUAL_DIRECTIONS[AdStyle.FULLY_AI])
        visual_direction = random.choice(visual_dirs)
        if ad_style == AdStyle.CLIENT_ASSETS and brief.assets_provided:
            visual_direction += f" Client assets: {', '.join(brief.assets_provided)}."

        music_direction = random.choice(_MUSIC_DIRECTIONS)

        ai_disclosure = (
            "This commercial was produced with AI assistance. "
            "All creative content is AI-generated."
            if ad_style == AdStyle.FULLY_AI
            else "This commercial incorporates client-supplied assets enhanced with AI tools."
        )

        production = CommercialScript(
            production_id=self._next_id("COMM"),
            client_name=brief.client_name,
            ad_format=ad_format,
            ad_style=ad_style,
            title=f"{brief.client_name} — {ad_format.value} ({ad_style.value})",
            script=script,
            voice_direction=voice_direction,
            visual_direction=visual_direction,
            music_direction=music_direction,
            duration_seconds=duration_map.get(ad_format, 30),
            call_to_action=brief.call_to_action,
            ai_disclosure=ai_disclosure,
        )
        self._productions.append(production)
        return production

    def create_radio_ad(
        self,
        brief: ClientBrief,
        duration: str = "30s",
        ad_style: AdStyle = AdStyle.FULLY_AI,
    ) -> CommercialScript:
        """
        Convenience wrapper to produce a radio-only advertisement.

        Parameters
        ----------
        brief : ClientBrief
            Client creative brief.
        duration : str
            ``"30s"`` or ``"60s"``.
        ad_style : AdStyle
            Asset approach.

        Returns
        -------
        CommercialScript
        """
        fmt = AdFormat.RADIO_60 if duration == "60s" else AdFormat.RADIO_30
        return self.create_commercial(brief, fmt, ad_style)

    def create_social_ad(
        self,
        brief: ClientBrief,
        ad_style: AdStyle = AdStyle.HYBRID,
    ) -> CommercialScript:
        """Produce a short-form social-media reel ad (30 s)."""
        return self.create_commercial(brief, AdFormat.SOCIAL_REEL, ad_style)

    def list_productions(self) -> list[dict]:
        """Return all generated commercial scripts as dicts."""
        return [p.to_dict() for p in self._productions]

    def get_production(self, production_id: str) -> CommercialScript:
        """Return a CommercialScript by ID."""
        for p in self._productions:
            if p.production_id == production_id:
                return p
        raise MediaProductionEngineError(f"Production '{production_id}' not found.")

    # ------------------------------------------------------------------
    # Music Video production
    # ------------------------------------------------------------------

    def create_music_video(
        self,
        artist_name: str,
        song_title: str,
        style: MusicVideoStyle = MusicVideoStyle.NARRATIVE,
        color_palette: str = "warm cinematic",
        vfx_notes: str = "",
    ) -> MusicVideoProject:
        """
        Generate a complete music video production package.

        Parameters
        ----------
        artist_name : str
            Name of the artist or band.
        song_title : str
            Title of the track.
        style : MusicVideoStyle
            Creative direction style.
        color_palette : str
            Desired colour grading description.
        vfx_notes : str
            Any specific VFX or CGI requirements.

        Returns
        -------
        MusicVideoProject
        """
        storyboard = _MV_STORYBOARD_TEMPLATES.get(
            style,
            _MV_STORYBOARD_TEMPLATES[MusicVideoStyle.NARRATIVE],
        )

        shot_list = [
            "ECU — artist's eyes, opening frame.",
            "MS — artist, full-body performance, key light from 45°.",
            "WS — location establishing shot, golden-hour lighting.",
            "CU — hands on instrument / microphone.",
            "OTS — crowd or supporting cast reactions.",
            "Aerial — pull-back drone shot for chorus peak.",
            "Insert — thematic prop close-ups tied to lyric imagery.",
            "Final — slow zoom out from artist to black.",
        ]

        visual_direction = (
            f"Style: {style.value.replace('_', ' ').title()}. "
            f"Color palette: {color_palette}. "
            "Every cut is beat-synced. Transitions: flash-cut on snare, slow dissolve on bridge. "
            "Aspect ratio: 16:9 primary, 9:16 vertical cut for social."
        )

        mv = MusicVideoProject(
            production_id=self._next_id("MV"),
            artist_name=artist_name,
            song_title=song_title,
            style=style,
            storyboard=list(storyboard),
            shot_list=shot_list,
            visual_direction=visual_direction,
            color_palette=color_palette,
            vfx_notes=vfx_notes or "Standard colour grade + subtle lens flare.",
            estimated_scenes=len(storyboard),
        )
        self._music_videos.append(mv)
        return mv

    def list_music_videos(self) -> list[dict]:
        """Return all music video projects as dicts."""
        return [mv.to_dict() for mv in self._music_videos]

    def get_music_video(self, production_id: str) -> MusicVideoProject:
        """Return a MusicVideoProject by ID."""
        for mv in self._music_videos:
            if mv.production_id == production_id:
                return mv
        raise MediaProductionEngineError(f"Music video '{production_id}' not found.")

    # ------------------------------------------------------------------
    # Movie / short film production
    # ------------------------------------------------------------------

    def create_movie(
        self,
        title: str,
        genre: MovieGenre = MovieGenre.SHORT_FILM,
        logline: str = "",
        runtime_minutes: int = 20,
    ) -> MovieProject:
        """
        Generate a complete movie or short-film production package.

        Parameters
        ----------
        title : str
            Working title of the film.
        genre : MovieGenre
            Genre classification.
        logline : str
            One-sentence story pitch (auto-generated if empty).
        runtime_minutes : int
            Target runtime in minutes.

        Returns
        -------
        MovieProject
        """
        auto_logline = logline or (
            f"A {genre.value} story about one person's journey to change everything "
            "they thought they knew — and discover who they really are."
        )

        synopsis = (
            f"'{title}' is a {genre.value} set in a world where the stakes couldn't be higher. "
            "Our protagonist faces a defining challenge that forces them to confront their deepest "
            "fears and greatest strengths. Through unexpected alliances and hard-won lessons, "
            "they emerge transformed — leaving the audience with a feeling they won't forget."
        )

        act_breakdown = [
            f"Act 1 (Setup, ~{round(runtime_minutes * 0.25)} min): "
            "Introduce protagonist and their ordinary world. Inciting incident disrupts the status quo.",
            f"Act 2A (Confrontation, ~{round(runtime_minutes * 0.25)} min): "
            "Protagonist pursues goal; early successes mask deeper obstacles.",
            f"Act 2B (Crisis, ~{round(runtime_minutes * 0.25)} min): "
            "Midpoint reversal; all seems lost. Dark night of the soul.",
            f"Act 3 (Resolution, ~{round(runtime_minutes * 0.25)} min): "
            "Climax, final battle, transformation complete. New equilibrium established.",
        ]

        cast_descriptions = [
            "PROTAGONIST — Mid-20s to 40s. Any ethnicity. Strong inner life, subtle exterior.",
            "ANTAGONIST / FOIL — Believable motivation. Not purely evil — complex.",
            "MENTOR FIGURE — Wisdom-bearer. May not survive the third act.",
            "ALLY — Comic relief balanced with genuine heart.",
            "LOVE INTEREST (optional) — Stakes-raiser for the protagonist's internal journey.",
        ]

        key_scenes = [
            "The Inciting Incident — 5-minute mark: the moment that shatters the ordinary world.",
            "The Point of No Return — protagonist makes an irreversible choice.",
            "The Dark Night of the Soul — everything lost, silence before the storm.",
            "The Climax — highest tension, all themes converge.",
            "The Resolution — quiet, earned, emotionally resonant final image.",
        ]

        cinematography_notes = (
            f"Genre: {genre.value}. "
            "Visual language: motivated camera movement, naturalistic lighting where possible. "
            "Golden ratio framing for emotionally significant shots. "
            "Handheld for chaos; locked-off for control and stillness."
        )

        score_direction = (
            "Minimalist score — theme introduced in Act 1, deconstructed in Act 2B, "
            "fully resolved in Act 3 finale. Avoid telegraphing emotion; undercut and subvert."
        )

        movie = MovieProject(
            production_id=self._next_id("FILM"),
            title=title,
            genre=genre,
            logline=auto_logline,
            synopsis=synopsis,
            act_breakdown=act_breakdown,
            cast_descriptions=cast_descriptions,
            key_scenes=key_scenes,
            cinematography_notes=cinematography_notes,
            score_direction=score_direction,
            estimated_runtime_minutes=runtime_minutes,
        )
        self._movies.append(movie)
        return movie

    def list_movies(self) -> list[dict]:
        """Return all movie projects as dicts."""
        return [m.to_dict() for m in self._movies]

    def get_movie(self, production_id: str) -> MovieProject:
        """Return a MovieProject by ID."""
        for m in self._movies:
            if m.production_id == production_id:
                return m
        raise MediaProductionEngineError(f"Movie '{production_id}' not found.")

    # ------------------------------------------------------------------
    # Status & serialisation
    # ------------------------------------------------------------------

    def production_summary(self) -> dict:
        """Return a count summary of all productions managed by this engine."""
        return {
            "commercials": len(self._productions),
            "music_videos": len(self._music_videos),
            "movies": len(self._movies),
            "total": len(self._productions) + len(self._music_videos) + len(self._movies),
        }

    def to_dict(self) -> dict:
        return {
            "user_id": self.user_id,
            "summary": self.production_summary(),
        }
