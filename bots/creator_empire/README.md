# CreatorEmpire

**Talent Agency + Event Planner + Distribution + Sports Representation + Streaming Launchpad Bot**

CreatorEmpire is a comprehensive DreamCo platform bot that manages every facet of a creator's career — from onboarding and brand building to music distribution, event planning, legal protection, and monetization.

---

## Modules

| Module | File | Description |
|--------|------|-------------|
| Tiers | `tiers.py` | FREE / PRO / ENTERPRISE feature access control |
| Talent Onboarding | `talent_onboarding.py` | Personal brand kits, media assets, talent profiles |
| Streamer Module | `streamer_module.py` | Twitch/YouTube account launch, AI overlay templates |
| Artist Module | `artist_module.py` | Music distribution, AI beat matching, royalty splits |
| Athlete Module | `athlete_module.py` | Highlight reels, recruitment profiles, NIL deals |
| Event Planner | `event_planner.py` | Venue research, budget planning, contract templates |
| Legal & Protection | `legal_protection.py` | Contract analysis, red-flag scanning, royalty calc |
| Monetization Dashboard | `monetization_dashboard.py` | Revenue tracking, service plans, payment processors |
| **CreatorEmpire** | `creator_empire.py` | Main orchestrator — ties all modules together |

---

## Quick Start

```python
from bots.creator_empire.creator_empire import CreatorEmpire
from bots.creator_empire.tiers import Tier

# Initialize the platform
empire = CreatorEmpire(tier=Tier.PRO)

# Describe the current tier
empire.describe_tier()

# Onboard a streamer in one call
result = empire.quick_onboard(
    talent_id="t001",
    name="StreamKing",
    category="streamer",
    email="sk@example.com",
    platform="twitch",
    channel_name="StreamKingLive",
)
print(result["brand_kit"]["tagline"])
print(result["streamer_account"]["channel_url"])
```

---

## Tier Comparison

| Feature | FREE | PRO ($49/mo) | ENTERPRISE ($299/mo) |
|---------|------|-------------|----------------------|
| Talent profiles | Up to 3 | Unlimited | Unlimited |
| Streaming accounts | ✓ (Twitch, YouTube) | ✓ + AI overlays | ✓ + AI overlays |
| Music distribution | 3 platforms | All platforms | All platforms |
| AI beat matching | ✗ | ✓ | ✓ |
| Royalty splits | ✗ | ✓ | ✓ |
| Highlight reels | ✓ (manual) | ✓ + AI detection | ✓ + AI detection |
| NIL deal tracking | ✗ | ✓ | ✓ |
| Events per month | 2 | Unlimited | Unlimited |
| Contract generator | ✗ | ✓ | ✓ |
| Legal analysis | ✗ | ✓ | ✓ |
| NIL value estimator | ✗ | ✗ | ✓ |
| Revenue tracking | ✓ (Starter plan) | ✓ | ✓ |
| Outreach automation | ✗ | ✗ | ✓ |
| White-label | ✗ | ✗ | ✓ |
| Support | Community | Email (48h SLA) | Dedicated 24/7 |

---

## Module Examples

### Talent Onboarding

```python
from bots.creator_empire.talent_onboarding import TalentOnboardingEngine
from bots.creator_empire.tiers import Tier

eng = TalentOnboardingEngine(tier=Tier.PRO)
profile = eng.onboard_talent(
    talent_id="t001",
    name="MC Blaze",
    category="rapper",
    email="blaze@example.com",
    social_handles={"instagram": "@mcblaze", "twitter": "@mcblaze"},
)
kit = eng.generate_ai_brand_kit("t001")
print(kit.tagline)   # "[AI-Enhanced] From the underground to the top."

eng.add_media_asset("t001", "headshot", "https://cdn.example.com/headshot.jpg")
```

### Streamer Module

```python
from bots.creator_empire.streamer_module import StreamerModule
from bots.creator_empire.tiers import Tier

mod = StreamerModule(tier=Tier.PRO)
account = mod.launch_account("t001", "twitch", "MCBlazeStream")
print(account.channel_url)  # https://twitch.tv/MCBlazeStream

# Assign an overlay
mod.assign_overlay("t001", "twitch", "Hip-Hop Stage")

# Or generate a custom AI overlay
overlay = mod.generate_ai_overlay("t001", "twitch", "music")
print(overlay.name)
```

### Artist Module

```python
from bots.creator_empire.artist_module import ArtistModule
from bots.creator_empire.tiers import Tier

mod = ArtistModule(tier=Tier.PRO)
release = mod.create_release("r001", "t001", "Street Dreams", "trap")
mod.set_royalty_split("r001", artist_pct=60, producer_pct=20, label_pct=10, distributor_pct=10)
mod.ai_beat_match("r001", bpm=140, key="C")
mod.distribute_release("r001")

earnings = mod.calculate_royalty_earnings("r001", total_revenue=5000.0)
print(earnings["artist"])   # 3000.0
```

### Athlete Module

```python
from bots.creator_empire.athlete_module import AthleteModule
from bots.creator_empire.tiers import Tier

mod = AthleteModule(tier=Tier.PRO)
reel = mod.create_highlight_reel("rl001", "t001", "Season Highlights")
mod.add_clip("rl001", "c1", 0, 12, "Game-winning dunk")
mod.add_clip("rl001", "c2", 15, 30, "Alley-oop")
mod.ai_detect_highlights("rl001")
mod.export_reel("rl001")

mod.create_recruitment_profile(
    "t001", "basketball", "Point Guard", 2025, 3.9,
    stats={"ppg": 24.1, "apg": 8.3}, awards=["All-State MVP"]
)
mod.attach_reel_to_recruitment("t001", "rl001")

deal = mod.create_nil_deal("d001", "t001", "endorsement", "Nike", 15000.0)
```

### Event Planner

```python
from bots.creator_empire.event_planner import EventPlannerEngine
from bots.creator_empire.tiers import Tier

eng = EventPlannerEngine(tier=Tier.PRO)
event = eng.create_event("ev001", "t001", "concert", "Street Dreams Release", "New York", 500)

venues = eng.research_venues("New York", min_capacity=300, max_budget_usd=20000)
eng.assign_venue("ev001", "The Marquee")
eng.create_budget("ev001", venue_cost=5000, production_cost=2000, marketing_cost=1000,
                  staffing_cost=500, catering_cost=300, talent_fees=1000)
contract = eng.generate_contract("ev001")
print(contract[:200])
```

### Legal & Protection

```python
from bots.creator_empire.legal_protection import LegalProtectionLayer
from bots.creator_empire.tiers import Tier

layer = LegalProtectionLayer(tier=Tier.PRO)

# Quick scan (all tiers)
flags = layer.scan_for_red_flags("This deal grants irrevocable rights in perpetuity.")
for f in flags:
    print(f"{f['severity'].upper()}: {f['keyword']} — {f['explanation']}")

# Full analysis
analysis = layer.analyze_contract("c001", open("my_contract.txt").read())
print(f"Risk: {analysis.overall_risk}")
for rec in analysis.recommendations:
    print(f"  → {rec}")

# Streaming royalties
result = layer.calculate_streaming_royalties(
    {"spotify": 2_000_000, "apple_music": 800_000},
    artist_share_pct=70.0,
)
print(f"Artist net: ${result['artist_net_usd']}")
```

### Monetization Dashboard

```python
from bots.creator_empire.monetization_dashboard import MonetizationDashboard
from bots.creator_empire.tiers import Tier

dash = MonetizationDashboard(tier=Tier.PRO)
dash.register_talent("t001", service_plan_id="creator")
dash.connect_payment_processor("t001", "stripe")
dash.connect_payment_processor("t001", "paypal")

dash.log_revenue("t001", "e001", "streaming_royalties", 2500.0)
dash.log_revenue("t001", "e002", "sponsorship", 5000.0)

report = dash.get_revenue_report("t001")
print(f"Net revenue: ${report['total_net_usd']}")
```

---

## Directory Structure

```
bots/creator_empire/
├── __init__.py
├── tiers.py                  # FREE / PRO / ENTERPRISE tier config
├── talent_onboarding.py      # Talent Onboarding Engine
├── streamer_module.py        # Streamer Module (Twitch, YouTube, overlays)
├── artist_module.py          # Rapper/Artist Module
├── athlete_module.py         # Athlete Module (highlights, NIL)
├── event_planner.py          # Event Planner Engine
├── legal_protection.py       # Legal & Protection Layer
├── monetization_dashboard.py # Monetization Dashboard
└── creator_empire.py         # Main orchestrator
```

---

## Running Tests

```bash
cd Dreamcobots
pip install -r requirements.txt
python -m pytest tests/test_creator_empire.py -v
```

All 116 tests cover every module and tier combination.

---

## Technical Architecture

- **Backend**: Python (FastAPI-ready modules, PostgreSQL-compatible data models)
- **Payment Systems**: Stripe & PayPal integration hooks in `MonetizationDashboard`
- **AI Components**: Brand kit generation, AI beat matching, clip detection, overlay generation
- **Tier System**: Inherits FREE / PRO / ENTERPRISE structure from DreamCo `bots/ai-models-integration/tiers.py`
- **Ecosystem**: Structural conventions follow DreamCo BotBase / ai_chatbot patterns
