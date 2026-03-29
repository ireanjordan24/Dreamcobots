"""
CreatorEmpire — Talent Agency + Event Planner + Distribution +
Sports Representation + Streaming Launchpad Bot.

Part of the DreamCo bot ecosystem (inherits structural conventions from
BotBase / DreamCo platform).

Usage
-----
    from creator_empire import CreatorEmpire
    from tiers import Tier

    empire = CreatorEmpire(tier=Tier.PRO)

    # Onboard a new streamer
    profile = empire.onboarding.onboard_talent(
        talent_id="t001", name="StreamKing", category="streamer", email="sk@example.com"
    )
    empire.onboarding.generate_ai_brand_kit("t001")

    # Launch a Twitch channel
    account = empire.streamer.launch_account("t001", "twitch", "StreamKingLive")

    # Plan an event
    event = empire.event_planner.create_event(
        "ev001", "t001", "concert", "StreamKing Live Show", "New York", 500
    )

    # Describe the current tier
    empire.describe_tier()
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path
from bots.creator_empire.tiers import (
    get_creator_tier_info,
    CREATOR_FEATURES,
    CREATOR_EXTRAS,
    FEATURE_TALENT_ONBOARDING,
    FEATURE_STREAMER_MODULE,
    FEATURE_ARTIST_MODULE,
    FEATURE_ATHLETE_MODULE,
    FEATURE_EVENT_PLANNER,
    FEATURE_LEGAL_PROTECTION,
    FEATURE_MONETIZATION_DASHBOARD,
)
from bots.creator_empire.talent_onboarding import TalentOnboardingEngine, OnboardingError
from bots.creator_empire.streamer_module import StreamerModule, StreamerModuleError
from bots.creator_empire.artist_module import ArtistModule, ArtistModuleError
from bots.creator_empire.athlete_module import AthleteModule, AthleteModuleError
from bots.creator_empire.event_planner import EventPlannerEngine, EventPlannerError
from bots.creator_empire.legal_protection import LegalProtectionLayer, LegalProtectionError
from bots.creator_empire.monetization_dashboard import MonetizationDashboard, MonetizationError


class CreatorEmpireError(Exception):
    """Top-level error for the CreatorEmpire bot."""


class CreatorEmpire:
    """
    CreatorEmpire — unified talent management and monetization platform.

    Orchestrates seven sub-modules under a single tier-aware interface:

    Attributes
    ----------
    onboarding : TalentOnboardingEngine
        Manage talent profiles and brand kits.
    streamer : StreamerModule
        Launch and manage streaming accounts with AI overlays.
    artist : ArtistModule
        Handle music releases, beat matching, and royalty splits.
    athlete : AthleteModule
        Manage highlight reels, recruitment profiles, and NIL deals.
    event_planner : EventPlannerEngine
        Plan events, research venues, and generate contracts.
    legal : LegalProtectionLayer
        Analyze contracts and calculate royalties.
    monetization : MonetizationDashboard
        Track revenue and manage payment processors.

    Parameters
    ----------
    tier : Tier
        Subscription tier that controls feature access across all modules.
    """

    def __init__(self, tier: Tier = Tier.FREE) -> None:
        self.tier = tier
        self.config = get_tier_config(tier)

        # Instantiate all sub-modules with the same tier
        self.onboarding = TalentOnboardingEngine(tier=tier)
        self.streamer = StreamerModule(tier=tier)
        self.artist = ArtistModule(tier=tier)
        self.athlete = AthleteModule(tier=tier)
        self.event_planner = EventPlannerEngine(tier=tier)
        self.legal = LegalProtectionLayer(tier=tier)
        self.monetization = MonetizationDashboard(tier=tier)

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current CreatorEmpire tier."""
        info = get_creator_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== CreatorEmpire — {info['name']} Tier ===",
            f"Price    : ${info['price_usd_monthly']:.2f}/month",
            f"Requests : {limit}/month",
            f"Support  : {info['support_level']}",
            "",
            "Enabled modules:",
        ]
        for feat in info["creator_features"]:
            lines.append(f"  ✓ {feat.replace('_', ' ').title()}")
        lines.append("")
        lines.append("Creator extras:")
        for extra in info["creator_extras"]:
            lines.append(f"  • {extra}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg

        current_extras = set(CREATOR_FEATURES[self.tier.value])
        new_features = [
            f for f in CREATOR_FEATURES[next_cfg.tier.value]
            if f not in current_extras
        ]

        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features unlocked:",
        ]
        for feat in new_features:
            lines.append(f"  + {feat.replace('_', ' ').title()}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing CreatorEmpire or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Platform-wide summary
    # ------------------------------------------------------------------

    def platform_summary(self) -> dict:
        """Return a high-level summary of the entire platform state."""
        return {
            "tier": self.tier.value,
            "onboarding": self.onboarding.summary(),
            "streamer": self.streamer.summary(),
            "artist": self.artist.summary(),
            "athlete": self.athlete.summary(),
            "event_planner": self.event_planner.summary(),
            "legal": self.legal.summary(),
            "monetization": self.monetization.summary(),
        }

    # ------------------------------------------------------------------
    # Convenience: full talent onboarding workflow
    # ------------------------------------------------------------------

    def quick_onboard(
        self,
        talent_id: str,
        name: str,
        category: str,
        email: str,
        platform: str = "twitch",
        channel_name: str = "",
    ) -> dict:
        """
        Convenience method that onboards a talent, generates a brand kit,
        and optionally launches a streaming account in one call.

        Parameters
        ----------
        talent_id : str
        name : str
        category : str
            "streamer", "rapper", "athlete", or "general".
        email : str
        platform : str
            Streaming platform ("twitch" or "youtube"). Used only for streamers.
        channel_name : str
            Channel name. Defaults to `name` if empty.

        Returns
        -------
        dict with keys: ``profile``, ``brand_kit``, ``streamer_account`` (if streamer).
        """
        profile = self.onboarding.onboard_talent(
            talent_id=talent_id,
            name=name,
            category=category,
            email=email,
        )
        brand_kit = self.onboarding.generate_ai_brand_kit(talent_id)

        result: dict = {
            "profile": profile.to_dict(),
            "brand_kit": {
                "primary_color": brand_kit.primary_color,
                "secondary_color": brand_kit.secondary_color,
                "font": brand_kit.font,
                "tagline": brand_kit.tagline,
                "bio": brand_kit.bio,
            },
        }

        if category.lower() == "streamer":
            ch_name = channel_name or name.replace(" ", "")
            account = self.streamer.launch_account(talent_id, platform, ch_name)
            result["streamer_account"] = account.to_dict()

        return result


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    print("CreatorEmpire — DreamCo Talent & Event Platform\n")

    for tier in Tier:
        empire = CreatorEmpire(tier=tier)
        empire.describe_tier()
        empire.show_upgrade_path()
        print()
