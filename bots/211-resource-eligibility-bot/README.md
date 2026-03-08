# DreamCo Family Resource & Survival GPS — 211 Bot

A comprehensive, GPS-based community resource tool that aggregates data from **211**, **Feeding America**, **HUD**, **American Job Centers**, and more to help families find food pantries, shelters, job centers, legal aid, and other critical services.

---

## Features

### Core GPS Resource Finder
- Search community resources by GPS coordinate and category.
- Integrated data sources: 211, Feeding America, HUD, American Job Centers, OpenStreetMap, Google Maps API.
- Resource categories: Food, Shelter, Job Assistance, Legal Aid, Financial Literacy, Healthcare, Childcare, Transportation, Clothing, Mental Health.

### Building Intelligence Panels *(PRO / ENTERPRISE)*
Each resource on the map is enhanced with a detailed panel providing:
1. **Type of resource** — human-friendly category label.
2. **Eligibility requirements** — plain-English summary.
3. **Required documents** — checklist of what to bring.
4. **Optimal visit times** — recommended days/times to minimise waiting.
5. **Wait time estimate** — average wait in minutes.
6. **Success instructions** — step-by-step first-visit guide.
7. **Embedded video walkthrough** — YouTube / video URL.
8. **Real-time crowd level** — low / medium / high.
9. **Supply availability** — whether supplies are currently available.
10. **Neighbourhood safety score** — 0–10 (higher = safer).

### Advanced GPS Filtering *(PRO / ENTERPRISE)*
- **Open now** — only show resources currently accepting visitors.
- **Kid-friendly** — filter for child-friendly services.
- **Handicap-accessible** — ADA/wheelchair-accessible only.
- **Spanish-speaking** — Spanish-language services available.
- **Max distance** — limit results to within N kilometres.

### Route Planning *(PRO / ENTERPRISE)*
- Distance calculation (great-circle / Haversine).
- Estimated driving time and walking time.
- **Uber & Lyft cost estimates** based on distance.
- Google Maps deep-link for turn-by-turn directions.
- **Secure family-focused route planner** that avoids low-safety areas.

### Real-Time Crowd Reporting & Supply Alerts *(PRO / ENTERPRISE)*
- Community-submitted crowd level reports (low / medium / high).
- Supply availability status updates.

### Neighbourhood Safety Score *(PRO / ENTERPRISE)*
- Per-resource safety score (0–10) based on neighbourhood data.

### Resource Layers
| Layer | Categories |
|---|---|
| **Homeless Resources** | Warming centers, emergency shelters, transitional housing, tent-safe zones, free meals |
| **Job Resources** | Workforce development centers, resume workshops, job placement services, training programmes |
| **Financial Literacy** | Budgeting workshops, Roth IRA & ETF education, one-on-one financial coaching |
| **Safety Alerts** | Family GPS signals, panic buttons, arrival alerts |

### AI Resource Matching *(PRO / ENTERPRISE)*
Generates a **personalised resource plan** based on:
- Income level (`very_low` / `low` / `moderate` / `above_moderate`)
- Housing status (`housed` / `at_risk` / `homeless`)
- Household size
- Presence of children or members with disabilities
- Employment status
- Language preference

The plan includes prioritised resource recommendations and financial literacy tips.

### Family GPS & Safety Alerts *(PRO / ENTERPRISE)*
- Register family members with GPS coordinates.
- **Panic button** — dispatches an emergency alert with the member's location.
- **Arrival alerts** — notify family when a member reaches a destination safely.

### Monetisation *(ENTERPRISE)*
- **Sponsored listings** — nonprofits and businesses can feature their services.
- **Affiliate programmes** — register partner organisations.
- **Premium membership** — unlocked on PRO tier.

---

## Tier Comparison

| Feature | FREE | PRO ($29/mo) | ENTERPRISE ($199/mo) |
|---|:---:|:---:|:---:|
| Resource search | ✓ | ✓ | ✓ |
| GPS map | ✓ | ✓ | ✓ |
| Max results per query | 10 | 50 | Unlimited |
| Data sources | 211, OSM | + Feeding America, HUD, AJC, Google Maps | Same + custom feeds |
| Building Intelligence Panels | — | ✓ | ✓ |
| Advanced filtering | — | ✓ | ✓ |
| Route planning | — | ✓ | ✓ |
| Rideshare cost estimates | — | ✓ | ✓ |
| Crowd reporting | — | ✓ | ✓ |
| Supply alerts | — | ✓ | ✓ |
| Neighbourhood safety score | — | ✓ | ✓ |
| AI resource matching | — | ✓ | ✓ |
| Family GPS signals | — | ✓ | ✓ |
| Panic button | — | ✓ | ✓ |
| Arrival alerts | — | ✓ | ✓ |
| Analytics dashboard | — | ✓ | ✓ |
| Real-time data feeds | — | — | ✓ |
| Sponsored listings | — | — | ✓ |
| Affiliate programmes | — | — | ✓ |
| White-label | — | — | ✓ |
| Custom integrations | — | — | ✓ |
| Support | Community | Email 48 h SLA | Dedicated 24/7 |

---

## Installation

```bash
# From the repository root
pip install -r requirements.txt
```

No external dependencies are required to run the core bot.  Optional API
integrations (Google Maps, 211 live feeds, Feeding America API) require the
respective API keys set as environment variables.

---

## Quick Start

```python
from bot import ResourceBot, ResourceFilter, UserProfile, Tier

# --- FREE tier: basic resource search ---
bot = ResourceBot(tier=Tier.FREE)
results = bot.search_resources(lat=40.7128, lon=-74.0060)
for r in results:
    print(r.name, r.category, r.address)

# --- PRO tier: advanced features ---
pro_bot = ResourceBot(tier=Tier.PRO)

# Advanced filtering
filt = ResourceFilter(kid_friendly=True, handicap_accessible=True, max_distance_km=5.0)
results = pro_bot.search_resources(lat=40.7128, lon=-74.0060, filters=filt)

# Building Intelligence Panel
panel = pro_bot.get_building_intel_panel("r001")
print(panel.type_label, panel.wait_time_label, panel.safety_score)

# Route planning with Uber/Lyft estimates
route = pro_bot.get_route_info(40.7000, -74.0000, "r001")
print(f"{route.distance_km} km — Uber ~${route.uber_estimate_usd}")

# AI resource matching
profile = UserProfile(income_level="very_low", housing_status="homeless",
                      household_size=3, has_children=True)
plan = pro_bot.generate_resource_plan(profile=profile, lat=40.7128, lon=-74.0060)
print(plan.summary)
for tip in plan.financial_literacy_tips:
    print(" •", tip)

# Family GPS
pro_bot.register_family_member("Alice", lat=40.7128, lon=-74.0060)
alert = pro_bot.send_panic_alert("Alice")
print(alert.message)
```

---

## Running the CLI Demo

```bash
cd bots/211-resource-eligibility-bot
python bot.py
```

---

## Running the Tests

```bash
# From the repository root
python -m pytest tests/test_211_bot.py -v
```

---

## Technical Architecture

```
bots/211-resource-eligibility-bot/
├── __init__.py          # Package exports
├── bot.py               # Main ResourceBot class + data models
├── tiers.py             # Tier configuration (FREE / PRO / ENTERPRISE)
└── README.md            # This file

tests/
└── test_211_bot.py      # Comprehensive test suite (48+ tests)
```

### Key Design Decisions
- **No external runtime dependencies** — the bot works out-of-the-box with only the Python standard library.  Real API integrations (Google Maps, 211 live feed, etc.) are designed as drop-in replacements for the stub data layer.
- **Tier-aware access control** — every premium feature is gated behind `_require_feature()`, raising `ResourceBotTierError` on unauthorised access.
- **Haversine distance** — accurate great-circle distances are used for sorting and filtering.
- **Stub database** — a representative set of 6 sample resources covers all major categories and data sources, enabling full offline testing.

---

## Data Sources & Integration Points

| Source | Integration Method | Tier |
|---|---|---|
| **211.org** | REST API (requires API key) | FREE |
| **OpenStreetMap** | Overpass API (free, rate-limited) | FREE |
| **Feeding America** | Partner API (requires agreement) | PRO |
| **HUD (Housing)** | public.hud.gov REST API | PRO |
| **American Job Centers** | CareerOneStop API | PRO |
| **Google Maps** | Maps JavaScript API / Directions API | PRO |

---

## Environment Variables (for live API integration)

| Variable | Description |
|---|---|
| `GOOGLE_MAPS_API_KEY` | Google Maps Platform API key |
| `FEEDING_AMERICA_API_KEY` | Feeding America partner API key |
| `HUD_API_KEY` | HUD public data API key |
| `CAREERONESTOP_USER_ID` | CareerOneStop API user ID |
| `CAREERONESTOP_TOKEN` | CareerOneStop API token |

---

## License

Part of the Dreamcobots project.  See the repository root `LICENSE` for details.
