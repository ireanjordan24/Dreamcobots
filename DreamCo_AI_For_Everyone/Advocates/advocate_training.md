# DreamCo Advocate Training Guide

## Training Overview
This guide prepares advocates to teach, support, and accelerate AI adoption within DreamCo.

---

## Module 1 — DreamCo Architecture (30 min)
- Review `README.md` — repo structure and GLOBAL AI SOURCES FLOW
- Walk through `framework/global_ai_sources_flow.py`
- Understand bot categories in `bots/global_bot_network/bot_library.py`
- Run `python tools/check_bot_framework.py`

## Module 2 — Bot Operations (45 min)
- Run each major bot category (finance, real estate, lead gen, etc.)
- Trigger workflows via GitHub Actions manually
- Interpret bot output and logs
- Practice with BuddyOrchestrator

## Module 3 — Teaching Techniques (30 min)
- Use the [Beginner Path](../Learning/beginner_path.md) as your curriculum
- Common questions and answers:
  - "What if the bot fails?" → Check `data/integration_log.json`
  - "How do I get more features?" → Upgrade tier in the bot init
  - "Can I make my own bot?" → Yes! See [Advanced Path](../Learning/advanced_path.md)

## Module 4 — Policy & Security (20 min)
- Review all 5 policy documents in `DreamCo_AI_For_Everyone/Policies/`
- Know what data can/cannot be entered into AI tools
- Know the incident response process

## Module 5 — Running a Workshop
### Template Agenda (60 min)
| Time | Activity |
|------|----------|
| 0:00 | Intro — What is DreamCo? |
| 0:10 | Demo — Run a live bot in GitHub Actions |
| 0:20 | Hands-on — Each attendee runs their first bot |
| 0:40 | Q&A — Address questions and blockers |
| 0:50 | Next steps — Learning paths, community, policies |
| 1:00 | Close |

### Materials Needed
- Repository access for all attendees
- Screen sharing for demo
- Link to [Beginner Path](../Learning/beginner_path.md)
- GitHub Discussions link for follow-up

---

## Certification
Advocates who complete all 5 modules receive the Core Advocate designation.
Submit your completion via GitHub Issue with label `advocate-certification`.
