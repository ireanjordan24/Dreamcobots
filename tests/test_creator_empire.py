"""
Tests for bots/creator_empire/ — CreatorEmpire bot.

Covers all seven sub-modules:
  1. tiers.py               — Tier configuration
  2. talent_onboarding.py  — Talent Onboarding Engine
  3. streamer_module.py    — Streamer Module
  4. artist_module.py      — Rapper/Artist Module
  5. athlete_module.py     — Athlete Module
  6. event_planner.py      — Event Planner Engine
  7. legal_protection.py   — Legal & Protection Layer
  8. monetization_dashboard.py — Monetization Dashboard
  9. creator_empire.py     — Main orchestrator
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, os.path.join(AI_MODELS_DIR, 'models'))
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier

# Sub-module imports
from bots.creator_empire.tiers import (
    get_creator_tier_info,
    CREATOR_FEATURES,
    CREATOR_EXTRAS,
    FEATURE_TALENT_ONBOARDING,
    FEATURE_STREAMER_MODULE,
    FEATURE_LEGAL_PROTECTION,
    FEATURE_MONETIZATION_DASHBOARD,
)
from bots.creator_empire.talent_onboarding import (
    TalentOnboardingEngine, OnboardingError, BrandKit, MediaAsset,
)
from bots.creator_empire.streamer_module import (
    StreamerModule, StreamerModuleError, OVERLAY_LIBRARY,
)
from bots.creator_empire.artist_module import (
    ArtistModule, ArtistModuleError, DISTRIBUTION_PLATFORMS,
)
from bots.creator_empire.athlete_module import (
    AthleteModule, AthleteModuleError,
)
from bots.creator_empire.event_planner import (
    EventPlannerEngine, EventPlannerError,
)
from bots.creator_empire.legal_protection import (
    LegalProtectionLayer, LegalProtectionError,
)
from bots.creator_empire.monetization_dashboard import (
    MonetizationDashboard, MonetizationError, SERVICE_PLANS,
)
from bots.creator_empire.creator_empire import CreatorEmpire, CreatorEmpireError


# ===========================================================================
# 1. Tiers
# ===========================================================================

class TestCreatorTiers:
    def test_free_tier_info_keys(self):
        info = get_creator_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "platform_features", "creator_features", "creator_extras", "support_level"):
            assert key in info

    def test_free_price_is_zero(self):
        info = get_creator_tier_info(Tier.FREE)
        assert info["price_usd_monthly"] == 0.0

    def test_pro_price(self):
        info = get_creator_tier_info(Tier.PRO)
        assert info["price_usd_monthly"] == 49.0

    def test_enterprise_unlimited_requests(self):
        info = get_creator_tier_info(Tier.ENTERPRISE)
        assert info["requests_per_month"] is None

    def test_free_includes_core_modules(self):
        info = get_creator_tier_info(Tier.FREE)
        assert FEATURE_TALENT_ONBOARDING in info["creator_features"]
        assert FEATURE_STREAMER_MODULE in info["creator_features"]

    def test_pro_includes_legal_and_monetization(self):
        info = get_creator_tier_info(Tier.PRO)
        assert FEATURE_LEGAL_PROTECTION in info["creator_features"]
        assert FEATURE_MONETIZATION_DASHBOARD in info["creator_features"]

    def test_enterprise_has_more_features_than_pro(self):
        pro = get_creator_tier_info(Tier.PRO)
        ent = get_creator_tier_info(Tier.ENTERPRISE)
        assert len(ent["creator_features"]) > len(pro["creator_features"])

    def test_creator_extras_populated_all_tiers(self):
        for tier in Tier:
            extras = CREATOR_EXTRAS[tier.value]
            assert isinstance(extras, list)
            assert len(extras) > 0

    def test_all_tiers_have_creator_features(self):
        for tier in Tier:
            assert isinstance(CREATOR_FEATURES[tier.value], list)
            assert len(CREATOR_FEATURES[tier.value]) > 0


# ===========================================================================
# 2. Talent Onboarding Engine
# ===========================================================================

class TestTalentOnboarding:
    def _engine(self, tier=Tier.FREE):
        return TalentOnboardingEngine(tier=tier)

    def test_onboard_talent_returns_profile(self):
        eng = self._engine()
        p = eng.onboard_talent("t1", "Alice", "streamer", "alice@test.com")
        assert p.talent_id == "t1"
        assert p.name == "Alice"

    def test_profile_in_list(self):
        eng = self._engine()
        eng.onboard_talent("t1", "Alice", "streamer", "alice@test.com")
        profiles = eng.list_profiles()
        assert len(profiles) == 1
        assert profiles[0]["talent_id"] == "t1"

    def test_free_tier_limit_3(self):
        eng = self._engine(Tier.FREE)
        for i in range(3):
            eng.onboard_talent(f"t{i}", f"Name{i}", "general", f"e{i}@test.com")
        with pytest.raises(OnboardingError, match="limit"):
            eng.onboard_talent("t4", "Extra", "general", "x@test.com")

    def test_pro_tier_unlimited(self):
        eng = self._engine(Tier.PRO)
        for i in range(10):
            eng.onboard_talent(f"t{i}", f"Name{i}", "general", f"e{i}@test.com")
        assert len(eng.list_profiles()) == 10

    def test_duplicate_id_raises(self):
        eng = self._engine()
        eng.onboard_talent("t1", "Alice", "streamer", "alice@test.com")
        with pytest.raises(OnboardingError, match="already exists"):
            eng.onboard_talent("t1", "Alice2", "general", "b@test.com")

    def test_get_profile(self):
        eng = self._engine()
        eng.onboard_talent("t1", "Alice", "streamer", "alice@test.com")
        p = eng.get_profile("t1")
        assert p.talent_id == "t1"

    def test_get_profile_not_found(self):
        eng = self._engine()
        with pytest.raises(OnboardingError, match="not found"):
            eng.get_profile("missing")

    def test_remove_profile(self):
        eng = self._engine()
        eng.onboard_talent("t1", "Alice", "streamer", "alice@test.com")
        eng.remove_profile("t1")
        assert len(eng.list_profiles()) == 0

    def test_generate_ai_brand_kit_free(self):
        eng = self._engine(Tier.FREE)
        eng.onboard_talent("t1", "Streamer", "streamer", "s@test.com")
        kit = eng.generate_ai_brand_kit("t1")
        assert isinstance(kit, BrandKit)
        assert kit.tagline != ""

    def test_generate_ai_brand_kit_pro_enhanced(self):
        eng = self._engine(Tier.PRO)
        eng.onboard_talent("t1", "Rapper", "rapper", "r@test.com")
        kit = eng.generate_ai_brand_kit("t1")
        assert "[AI-Enhanced]" in kit.tagline

    def test_add_media_asset(self):
        eng = self._engine()
        eng.onboard_talent("t1", "Alice", "general", "a@test.com")
        asset = eng.add_media_asset("t1", "headshot", "https://example.com/pic.jpg")
        assert isinstance(asset, MediaAsset)
        p = eng.get_profile("t1")
        assert len(p.media_assets) == 1

    def test_summary(self):
        eng = self._engine(Tier.PRO)
        eng.onboard_talent("t1", "Alice", "general", "a@test.com")
        s = eng.summary()
        assert s["profiles_created"] == 1
        assert s["profile_limit"] == "unlimited"

    def test_to_dict_structure(self):
        eng = self._engine()
        eng.onboard_talent("t1", "Alice", "streamer", "a@test.com",
                           social_handles={"twitch": "alicestreams"})
        p = eng.get_profile("t1")
        d = p.to_dict()
        assert "brand_kit" in d
        assert "social_handles" in d
        assert d["social_handles"]["twitch"] == "alicestreams"


# ===========================================================================
# 3. Streamer Module
# ===========================================================================

class TestStreamerModule:
    def _mod(self, tier=Tier.FREE):
        return StreamerModule(tier=tier)

    def test_launch_twitch_account(self):
        mod = self._mod()
        acc = mod.launch_account("t1", "twitch", "StreamKing")
        assert acc.platform == "twitch"
        assert "twitch.tv" in acc.channel_url
        assert acc.setup_complete is True

    def test_launch_youtube_account(self):
        mod = self._mod()
        acc = mod.launch_account("t1", "youtube", "StreamKing")
        assert acc.platform == "youtube"
        assert acc.channel_url.startswith("https://youtube.com/@")

    def test_unsupported_platform_raises(self):
        mod = self._mod()
        with pytest.raises(StreamerModuleError, match="not supported"):
            mod.launch_account("t1", "tiktok", "king")

    def test_free_overlays_available(self):
        mod = self._mod(Tier.FREE)
        overlays = mod.list_available_overlays()
        assert len(overlays) > 0
        for o in overlays:
            assert o["tier_required"] == "free"

    def test_pro_overlays_more_than_free(self):
        free_mod = self._mod(Tier.FREE)
        pro_mod = self._mod(Tier.PRO)
        assert len(pro_mod.list_available_overlays()) > len(free_mod.list_available_overlays())

    def test_assign_free_overlay(self):
        mod = self._mod(Tier.FREE)
        mod.launch_account("t1", "twitch", "StreamKing")
        acc = mod.assign_overlay("t1", "twitch", "Neon Gamer")
        assert acc.overlay is not None
        assert acc.overlay.name == "Neon Gamer"

    def test_assign_pro_overlay_on_free_raises(self):
        mod = self._mod(Tier.FREE)
        mod.launch_account("t1", "twitch", "StreamKing")
        with pytest.raises(StreamerModuleError, match="requires"):
            mod.assign_overlay("t1", "twitch", "Hip-Hop Stage")

    def test_assign_pro_overlay_on_pro(self):
        mod = self._mod(Tier.PRO)
        mod.launch_account("t1", "twitch", "StreamKing")
        acc = mod.assign_overlay("t1", "twitch", "Hip-Hop Stage")
        assert acc.overlay.name == "Hip-Hop Stage"

    def test_ai_overlay_free_raises(self):
        mod = self._mod(Tier.FREE)
        mod.launch_account("t1", "twitch", "King")
        with pytest.raises(StreamerModuleError, match="Pro tier"):
            mod.generate_ai_overlay("t1", "twitch", "gaming")

    def test_ai_overlay_pro(self):
        mod = self._mod(Tier.PRO)
        mod.launch_account("t1", "twitch", "King")
        overlay = mod.generate_ai_overlay("t1", "twitch", "gaming")
        assert "[AI Generated]" in overlay.name

    def test_get_accounts(self):
        mod = self._mod()
        mod.launch_account("t1", "twitch", "King")
        mod.launch_account("t1", "youtube", "King")
        accounts = mod.get_accounts("t1")
        assert len(accounts) == 2

    def test_summary(self):
        mod = self._mod(Tier.PRO)
        mod.launch_account("t1", "twitch", "King")
        s = mod.summary()
        assert s["total_accounts"] == 1
        assert s["available_overlay_count"] > 0

    def test_overlay_not_found_raises(self):
        mod = self._mod(Tier.FREE)
        mod.launch_account("t1", "twitch", "King")
        with pytest.raises(StreamerModuleError, match="not found"):
            mod.assign_overlay("t1", "twitch", "NonExistentOverlay")

    def test_no_account_before_overlay_raises(self):
        mod = self._mod(Tier.FREE)
        with pytest.raises(StreamerModuleError, match="No twitch account"):
            mod.assign_overlay("t1", "twitch", "Neon Gamer")


# ===========================================================================
# 4. Artist Module
# ===========================================================================

class TestArtistModule:
    def _mod(self, tier=Tier.FREE):
        return ArtistModule(tier=tier)

    def test_create_release(self):
        mod = self._mod()
        r = mod.create_release("r1", "t1", "My Track", "trap")
        assert r.release_id == "r1"
        assert r.status == "pending"

    def test_free_max_3_platforms(self):
        mod = self._mod(Tier.FREE)
        with pytest.raises(ArtistModuleError, match="maximum of 3"):
            mod.create_release("r1", "t1", "Track", "trap",
                               platforms=DISTRIBUTION_PLATFORMS)

    def test_pro_all_platforms(self):
        mod = self._mod(Tier.PRO)
        r = mod.create_release("r1", "t1", "Track", "trap",
                               platforms=DISTRIBUTION_PLATFORMS)
        assert len(r.platforms) == len(DISTRIBUTION_PLATFORMS)

    def test_duplicate_release_raises(self):
        mod = self._mod()
        mod.create_release("r1", "t1", "Track", "trap")
        with pytest.raises(ArtistModuleError, match="already exists"):
            mod.create_release("r1", "t1", "Track2", "drill")

    def test_distribute_release(self):
        mod = self._mod()
        mod.create_release("r1", "t1", "Track", "trap")
        r = mod.distribute_release("r1")
        assert r.status == "distributed"

    def test_ai_beat_match_free_raises(self):
        mod = self._mod(Tier.FREE)
        mod.create_release("r1", "t1", "Track", "trap")
        with pytest.raises(ArtistModuleError, match="Pro tier"):
            mod.ai_beat_match("r1", 140, "C")

    def test_ai_beat_match_pro(self):
        mod = self._mod(Tier.PRO)
        mod.create_release("r1", "t1", "Track", "trap")
        bm = mod.ai_beat_match("r1", 140, "C")
        assert bm.bpm == 140
        assert len(bm.suggested_beats) > 0

    def test_royalty_split_free_raises(self):
        mod = self._mod(Tier.FREE)
        mod.create_release("r1", "t1", "Track", "trap")
        with pytest.raises(ArtistModuleError, match="Pro tier"):
            mod.set_royalty_split("r1", 60, 20, 10, 10)

    def test_royalty_split_validation(self):
        mod = self._mod(Tier.PRO)
        mod.create_release("r1", "t1", "Track", "trap")
        with pytest.raises(ArtistModuleError, match="sum to 100"):
            mod.set_royalty_split("r1", 50, 20, 10, 10)  # only 90%

    def test_royalty_split_valid(self):
        mod = self._mod(Tier.PRO)
        mod.create_release("r1", "t1", "Track", "trap")
        split = mod.set_royalty_split("r1", 60, 20, 10, 10)
        assert split.artist_pct == 60

    def test_royalty_earnings(self):
        mod = self._mod(Tier.PRO)
        mod.create_release("r1", "t1", "Track", "trap")
        mod.set_royalty_split("r1", 70, 15, 10, 5)
        earnings = mod.calculate_royalty_earnings("r1", 1000.0)
        assert earnings["artist"] == 700.0
        assert earnings["producer"] == 150.0

    def test_royalty_earnings_no_split_raises(self):
        mod = self._mod(Tier.PRO)
        mod.create_release("r1", "t1", "Track", "trap")
        with pytest.raises(ArtistModuleError, match="No royalty split"):
            mod.calculate_royalty_earnings("r1", 500.0)

    def test_list_releases(self):
        mod = self._mod(Tier.PRO)
        mod.create_release("r1", "t1", "Track1", "trap")
        mod.create_release("r2", "t2", "Track2", "drill")
        assert len(mod.list_releases()) == 2
        assert len(mod.list_releases(talent_id="t1")) == 1

    def test_summary(self):
        mod = self._mod(Tier.PRO)
        mod.create_release("r1", "t1", "Track", "trap")
        mod.distribute_release("r1")
        s = mod.summary()
        assert s["total_releases"] == 1
        assert s["distributed"] == 1


# ===========================================================================
# 5. Athlete Module
# ===========================================================================

class TestAthleteModule:
    def _mod(self, tier=Tier.FREE):
        return AthleteModule(tier=tier)

    def test_create_highlight_reel(self):
        mod = self._mod()
        reel = mod.create_highlight_reel("rl1", "t1", "Best Plays")
        assert reel.reel_id == "rl1"
        assert reel.status == "draft"

    def test_add_clip(self):
        mod = self._mod()
        mod.create_highlight_reel("rl1", "t1", "Plays")
        clip = mod.add_clip("rl1", "c1", 10.0, 20.0, "Dunk")
        assert clip.clip_id == "c1"
        assert clip.duration() == 10.0

    def test_add_clip_invalid_timestamps(self):
        mod = self._mod()
        mod.create_highlight_reel("rl1", "t1", "Plays")
        with pytest.raises(AthleteModuleError, match="greater than"):
            mod.add_clip("rl1", "c1", 20.0, 10.0)

    def test_ai_detect_free_raises(self):
        mod = self._mod(Tier.FREE)
        mod.create_highlight_reel("rl1", "t1", "Plays")
        with pytest.raises(AthleteModuleError, match="Pro tier"):
            mod.ai_detect_highlights("rl1")

    def test_ai_detect_pro(self):
        mod = self._mod(Tier.PRO)
        mod.create_highlight_reel("rl1", "t1", "Plays")
        mod.add_clip("rl1", "c1", 0, 10, "Play 1")
        mod.add_clip("rl1", "c2", 10, 25, "Play 2")
        reel = mod.ai_detect_highlights("rl1")
        assert reel.status == "compiled"
        # Clips should be scored
        for clip in reel.clips:
            assert clip.score >= 0

    def test_export_reel(self):
        mod = self._mod()
        mod.create_highlight_reel("rl1", "t1", "Plays")
        result = mod.export_reel("rl1")
        assert result["status"] == "exported"
        assert result["export_url"].startswith("https://creatorempire.io/reels/")

    def test_create_recruitment_profile(self):
        mod = self._mod()
        p = mod.create_recruitment_profile(
            "t1", "basketball", "Point Guard", 2025, 3.8,
            stats={"ppg": 22.5}, awards=["All-State"],
            contact_email="t1@school.edu"
        )
        assert p.sport == "basketball"
        assert p.gpa == 3.8

    def test_get_recruitment_profile(self):
        mod = self._mod()
        mod.create_recruitment_profile("t1", "basketball", "PG", 2025, 3.8)
        d = mod.get_recruitment_profile("t1")
        assert d["sport"] == "basketball"

    def test_nil_tips(self):
        mod = self._mod()
        tips = mod.get_nil_tips("basketball")
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_nil_tips_default_sport(self):
        mod = self._mod()
        tips = mod.get_nil_tips("curling")
        assert isinstance(tips, list)
        assert len(tips) > 0

    def test_nil_deal_free_raises(self):
        mod = self._mod(Tier.FREE)
        with pytest.raises(AthleteModuleError, match="Pro tier"):
            mod.create_nil_deal("d1", "t1", "endorsement", "Nike", 5000)

    def test_nil_deal_pro(self):
        mod = self._mod(Tier.PRO)
        deal = mod.create_nil_deal("d1", "t1", "endorsement", "Nike", 5000.0)
        assert deal.brand == "Nike"
        assert deal.status == "prospect"

    def test_nil_deal_status_update(self):
        mod = self._mod(Tier.PRO)
        mod.create_nil_deal("d1", "t1", "endorsement", "Nike", 5000.0)
        deal = mod.update_nil_deal_status("d1", "signed")
        assert deal.status == "signed"

    def test_nil_deal_invalid_status(self):
        mod = self._mod(Tier.PRO)
        mod.create_nil_deal("d1", "t1", "endorsement", "Nike", 5000.0)
        with pytest.raises(AthleteModuleError, match="Invalid status"):
            mod.update_nil_deal_status("d1", "in_review")

    def test_summary(self):
        mod = self._mod(Tier.PRO)
        mod.create_highlight_reel("rl1", "t1", "Plays")
        mod.create_recruitment_profile("t1", "football", "QB", 2024, 3.5)
        mod.create_nil_deal("d1", "t1", "endorsement", "Adidas", 2000)
        s = mod.summary()
        assert s["highlight_reels"] == 1
        assert s["recruitment_profiles"] == 1
        assert s["nil_deals"] == 1

    def test_attach_reel_to_recruitment(self):
        mod = self._mod()
        mod.create_highlight_reel("rl1", "t1", "Plays")
        mod.export_reel("rl1")
        mod.create_recruitment_profile("t1", "basketball", "PG", 2025, 3.8)
        p = mod.attach_reel_to_recruitment("t1", "rl1")
        assert "rl1" in p.highlight_reel_url


# ===========================================================================
# 6. Event Planner Engine
# ===========================================================================

class TestEventPlanner:
    def _eng(self, tier=Tier.FREE):
        return EventPlannerEngine(tier=tier)

    def test_create_event(self):
        eng = self._eng()
        e = eng.create_event("ev1", "t1", "concert", "My Show", "NYC", 500)
        assert e.event_id == "ev1"
        assert e.status == "planning"

    def test_free_event_limit(self):
        eng = self._eng(Tier.FREE)
        eng.create_event("ev1", "t1", "concert", "Show1", "NYC", 100)
        eng.create_event("ev2", "t1", "concert", "Show2", "LA", 200)
        with pytest.raises(EventPlannerError, match="maximum of 2"):
            eng.create_event("ev3", "t1", "concert", "Show3", "Chicago", 300)

    def test_pro_unlimited_events(self):
        eng = self._eng(Tier.PRO)
        for i in range(5):
            eng.create_event(f"ev{i}", "t1", "concert", f"Show{i}", "NYC", 100)
        assert eng.summary()["total_events"] == 5

    def test_duplicate_event_raises(self):
        eng = self._eng()
        eng.create_event("ev1", "t1", "concert", "Show", "NYC", 100)
        with pytest.raises(EventPlannerError, match="already exists"):
            eng.create_event("ev1", "t1", "concert", "Show2", "LA", 200)

    def test_research_venues_by_city(self):
        eng = self._eng()
        results = eng.research_venues("New York")
        assert len(results) > 0
        for v in results:
            assert "New York" in v["city"] or v["city"] == "Virtual"

    def test_research_venues_min_capacity(self):
        eng = self._eng()
        results = eng.research_venues("New York", min_capacity=10000)
        for v in results:
            assert v["capacity"] >= 10000

    def test_research_venues_max_budget(self):
        eng = self._eng()
        results = eng.research_venues("New York", max_budget_usd=10000)
        for v in results:
            assert v["estimated_cost_usd"] <= 10000

    def test_assign_venue(self):
        eng = self._eng()
        eng.create_event("ev1", "t1", "concert", "Show", "New York", 500)
        eng.assign_venue("ev1", "The Marquee")
        e = eng.get_event("ev1")
        assert e["venue"]["name"] == "The Marquee"

    def test_create_budget(self):
        eng = self._eng()
        eng.create_event("ev1", "t1", "concert", "Show", "NYC", 500)
        budget = eng.create_budget(
            "ev1",
            venue_cost=5000,
            production_cost=2000,
            marketing_cost=1000,
            staffing_cost=500,
            catering_cost=300,
            talent_fees=1000,
        )
        assert budget.total() > budget.subtotal()  # contingency added
        assert budget.subtotal() == 9800.0

    def test_generate_contract_free_raises(self):
        eng = self._eng(Tier.FREE)
        eng.create_event("ev1", "t1", "concert", "Show", "NYC", 100)
        with pytest.raises(EventPlannerError, match="Pro tier"):
            eng.generate_contract("ev1")

    def test_generate_contract_pro(self):
        eng = self._eng(Tier.PRO)
        eng.create_event("ev1", "t1", "concert", "My Show", "NYC", 300)
        contract = eng.generate_contract("ev1")
        assert "My Show" in contract
        assert "CreatorEmpire" in contract

    def test_update_event_status(self):
        eng = self._eng()
        eng.create_event("ev1", "t1", "concert", "Show", "NYC", 100)
        eng.update_event_status("ev1", "confirmed")
        e = eng.get_event("ev1")
        assert e["status"] == "confirmed"

    def test_invalid_status_raises(self):
        eng = self._eng()
        eng.create_event("ev1", "t1", "concert", "Show", "NYC", 100)
        with pytest.raises(EventPlannerError, match="Invalid status"):
            eng.update_event_status("ev1", "in_progress")

    def test_summary(self):
        eng = self._eng(Tier.PRO)
        eng.create_event("ev1", "t1", "concert", "Show", "NYC", 100)
        s = eng.summary()
        assert s["total_events"] == 1
        assert s["event_limit"] == "unlimited"


# ===========================================================================
# 7. Legal & Protection Layer
# ===========================================================================

class TestLegalProtection:
    def _layer(self, tier=Tier.FREE):
        return LegalProtectionLayer(tier=tier)

    def test_scan_red_flags_all_tiers(self):
        layer = self._layer(Tier.FREE)
        result = layer.scan_for_red_flags("This contract grants rights in perpetuity.")
        assert len(result) >= 1
        assert result[0]["keyword"] == "in perpetuity"

    def test_scan_no_flags(self):
        layer = self._layer(Tier.FREE)
        result = layer.scan_for_red_flags("Standard services agreement with mutual consent.")
        assert result == []

    def test_analyze_contract_free_raises(self):
        layer = self._layer(Tier.FREE)
        with pytest.raises(LegalProtectionError, match="Pro tier"):
            layer.analyze_contract("c1", "Some contract text.")

    def test_analyze_contract_pro(self):
        layer = self._layer(Tier.PRO)
        text = "This agreement grants irrevocable rights in perpetuity."
        analysis = layer.analyze_contract("c1", text)
        assert analysis.contract_id == "c1"
        assert len(analysis.red_flags) >= 2

    def test_overall_risk_high(self):
        layer = self._layer(Tier.PRO)
        text = "Grants irrevocable rights in perpetuity as work for hire with non-compete."
        analysis = layer.analyze_contract("c1", text)
        assert analysis.overall_risk in ("medium", "high")

    def test_overall_risk_low_clean_contract(self):
        layer = self._layer(Tier.PRO)
        text = "Services agreement. Payment within 30 days. Standard terms apply."
        analysis = layer.analyze_contract("c1", text)
        assert analysis.overall_risk == "low"
        assert len(analysis.recommendations) > 0

    def test_get_analysis_not_found_raises(self):
        layer = self._layer(Tier.PRO)
        with pytest.raises(LegalProtectionError, match="No analysis"):
            layer.get_analysis("missing_id")

    def test_streaming_royalties_free_raises(self):
        layer = self._layer(Tier.FREE)
        with pytest.raises(LegalProtectionError, match="Pro tier"):
            layer.calculate_streaming_royalties({"spotify": 100000})

    def test_streaming_royalties_pro(self):
        layer = self._layer(Tier.PRO)
        result = layer.calculate_streaming_royalties(
            {"spotify": 1_000_000, "apple_music": 500_000},
            artist_share_pct=80.0,
        )
        assert result["total_gross_usd"] > 0
        assert result["artist_net_usd"] < result["total_gross_usd"]

    def test_streaming_royalties_full_share(self):
        layer = self._layer(Tier.PRO)
        result = layer.calculate_streaming_royalties({"spotify": 1000}, 100.0)
        assert result["artist_net_usd"] == result["total_gross_usd"]

    def test_nil_value_not_enterprise_raises(self):
        layer = self._layer(Tier.PRO)
        with pytest.raises(LegalProtectionError, match="Enterprise"):
            layer.estimate_nil_value(100_000, 5.0, "basketball")

    def test_nil_value_enterprise(self):
        layer = self._layer(Tier.ENTERPRISE)
        result = layer.estimate_nil_value(500_000, 4.0, "basketball")
        assert result["estimated_nil_value_per_post_usd"] > 0

    def test_summary(self):
        layer = self._layer(Tier.PRO)
        layer.analyze_contract("c1", "Test contract text.")
        s = layer.summary()
        assert s["contracts_analyzed"] == 1


# ===========================================================================
# 8. Monetization Dashboard
# ===========================================================================

class TestMonetizationDashboard:
    def _dash(self, tier=Tier.FREE):
        return MonetizationDashboard(tier=tier)

    def test_register_talent(self):
        dash = self._dash()
        account = dash.register_talent("t1", "starter")
        assert account.talent_id == "t1"
        assert account.service_plan_id == "starter"

    def test_duplicate_registration_raises(self):
        dash = self._dash()
        dash.register_talent("t1")
        with pytest.raises(MonetizationError, match="already registered"):
            dash.register_talent("t1")

    def test_invalid_plan_raises(self):
        dash = self._dash()
        with pytest.raises(MonetizationError, match="not found"):
            dash.register_talent("t1", "diamond")

    def test_pro_plan_requires_pro_tier(self):
        dash = self._dash(Tier.FREE)
        with pytest.raises(MonetizationError, match="Pro platform tier"):
            dash.register_talent("t1", "pro")

    def test_connect_payment_processor(self):
        dash = self._dash(Tier.PRO)
        dash.register_talent("t1", "pro")
        result = dash.connect_payment_processor("t1", "stripe")
        assert result["status"] == "connected"

    def test_unsupported_processor_raises(self):
        dash = self._dash()
        dash.register_talent("t1", "starter")
        with pytest.raises(MonetizationError, match="not supported"):
            dash.connect_payment_processor("t1", "bitcoin")

    def test_duplicate_processor_raises(self):
        dash = self._dash(Tier.PRO)
        dash.register_talent("t1", "pro")
        dash.connect_payment_processor("t1", "stripe")
        with pytest.raises(MonetizationError, match="already connected"):
            dash.connect_payment_processor("t1", "stripe")

    def test_log_revenue(self):
        dash = self._dash()
        dash.register_talent("t1", "starter")
        entry = dash.log_revenue("t1", "e1", "streaming_royalties", 1000.0)
        assert entry.gross_amount_usd == 1000.0
        assert entry.net_amount() < 1000.0  # fee deducted

    def test_revenue_report(self):
        dash = self._dash(Tier.PRO)
        dash.register_talent("t1", "creator")
        dash.log_revenue("t1", "e1", "streaming_royalties", 500.0)
        dash.log_revenue("t1", "e2", "sponsorship", 1000.0)
        report = dash.get_revenue_report("t1")
        assert report["entry_count"] == 2
        assert report["total_gross_usd"] == 1500.0

    def test_list_service_plans(self):
        plans = MonetizationDashboard.list_service_plans()
        assert len(plans) == len(SERVICE_PLANS)
        for p in plans:
            assert "plan_id" in p
            assert "monthly_fee_usd" in p

    def test_upgrade_plan(self):
        dash = self._dash(Tier.PRO)
        dash.register_talent("t1", "starter")
        account = dash.upgrade_plan("t1", "creator")
        assert account.service_plan_id == "creator"

    def test_summary(self):
        dash = self._dash(Tier.PRO)
        dash.register_talent("t1", "creator")
        dash.log_revenue("t1", "e1", "event", 2000.0)
        s = dash.summary()
        assert s["registered_talents"] == 1
        assert s["total_gross_revenue_usd"] == 2000.0


# ===========================================================================
# 9. CreatorEmpire Orchestrator
# ===========================================================================

class TestCreatorEmpire:
    def test_init_free(self):
        empire = CreatorEmpire(tier=Tier.FREE)
        assert empire.tier == Tier.FREE

    def test_all_modules_present(self):
        empire = CreatorEmpire(tier=Tier.PRO)
        assert hasattr(empire, "onboarding")
        assert hasattr(empire, "streamer")
        assert hasattr(empire, "artist")
        assert hasattr(empire, "athlete")
        assert hasattr(empire, "event_planner")
        assert hasattr(empire, "legal")
        assert hasattr(empire, "monetization")

    def test_all_modules_share_tier(self):
        empire = CreatorEmpire(tier=Tier.PRO)
        assert empire.onboarding.tier == Tier.PRO
        assert empire.streamer.tier == Tier.PRO
        assert empire.artist.tier == Tier.PRO
        assert empire.athlete.tier == Tier.PRO
        assert empire.event_planner.tier == Tier.PRO
        assert empire.legal.tier == Tier.PRO
        assert empire.monetization.tier == Tier.PRO

    def test_describe_tier_returns_string(self):
        empire = CreatorEmpire(tier=Tier.FREE)
        desc = empire.describe_tier()
        assert isinstance(desc, str)
        assert "CreatorEmpire" in desc
        assert "Free" in desc

    def test_show_upgrade_path_from_free(self):
        empire = CreatorEmpire(tier=Tier.FREE)
        msg = empire.show_upgrade_path()
        assert "Pro" in msg

    def test_show_upgrade_path_from_enterprise(self):
        empire = CreatorEmpire(tier=Tier.ENTERPRISE)
        msg = empire.show_upgrade_path()
        assert "top-tier" in msg

    def test_platform_summary_keys(self):
        empire = CreatorEmpire(tier=Tier.PRO)
        s = empire.platform_summary()
        for key in ("tier", "onboarding", "streamer", "artist", "athlete",
                    "event_planner", "legal", "monetization"):
            assert key in s

    def test_quick_onboard_streamer(self):
        empire = CreatorEmpire(tier=Tier.PRO)
        result = empire.quick_onboard(
            "t1", "StreamKing", "streamer", "sk@test.com",
            platform="twitch", channel_name="StreamKingLive"
        )
        assert "profile" in result
        assert "brand_kit" in result
        assert "streamer_account" in result
        assert result["streamer_account"]["platform"] == "twitch"

    def test_quick_onboard_non_streamer(self):
        empire = CreatorEmpire(tier=Tier.PRO)
        result = empire.quick_onboard("t1", "DJ Mike", "rapper", "dj@test.com")
        assert "profile" in result
        assert "brand_kit" in result
        assert "streamer_account" not in result

    def test_quick_onboard_default_channel_name(self):
        empire = CreatorEmpire(tier=Tier.PRO)
        result = empire.quick_onboard(
            "t1", "Stream King", "streamer", "sk@test.com"
        )
        # channel name should default to name without spaces
        assert result["streamer_account"]["channel_name"] == "StreamKing"

    def test_cross_module_workflow(self):
        """Full end-to-end: onboard → stream → event → legal → monetize."""
        empire = CreatorEmpire(tier=Tier.PRO)

        # Onboard
        empire.onboarding.onboard_talent("t1", "Artist X", "streamer", "ax@test.com")
        empire.onboarding.generate_ai_brand_kit("t1")

        # Stream
        empire.streamer.launch_account("t1", "twitch", "ArtistXLive")

        # Artist release
        empire.artist.create_release("r1", "t1", "My Song", "trap")
        empire.artist.set_royalty_split("r1", 60, 20, 10, 10)

        # Event
        empire.event_planner.create_event("ev1", "t1", "concert", "Release Show", "LA", 200)
        empire.event_planner.generate_contract("ev1")

        # Monetize
        empire.monetization.register_talent("t1", "creator")
        empire.monetization.log_revenue("t1", "e1", "streaming", 500.0)

        summary = empire.platform_summary()
        assert summary["onboarding"]["profiles_created"] == 1
        assert summary["streamer"]["total_accounts"] == 1
        assert summary["artist"]["total_releases"] == 1
        assert summary["event_planner"]["total_events"] == 1
        assert summary["monetization"]["registered_talents"] == 1
