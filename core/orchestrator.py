"""Buddy Orchestrator - routes requests and manages all DreamCobots bots."""
import re
from datetime import datetime


ROUTING_KEYWORDS = {
    "government-contract-grant-bot": [
        "contract", "grant", "government", "federal", "sam.gov", "rfp", "bid", "solicitation",
        "sbir", "sttr", "funding opportunity"
    ],
    "hustle-bot": [
        "hustle", "revenue", "income", "side hustle", "freelance", "gig", "goal", "milestone",
        "earning", "money", "profit"
    ],
    "referral-bot": [
        "referral", "refer", "affiliate", "commission", "leaderboard", "referrer", "share link"
    ],
    "buddy-bot": [
        "help", "what can you do", "capabilities", "overview", "assistant", "general", "support"
    ],
    "entrepreneur-bot": [
        "startup", "business plan", "business idea", "pitch", "investor", "entrepreneur",
        "venture", "LLC", "incorporate", "founder"
    ],
    "medical-bot": [
        "medical", "health", "symptoms", "doctor", "clinical", "HIPAA", "patient",
        "drug", "hospital", "diagnosis"
    ],
    "legal-bot": [
        "legal", "contract", "attorney", "lawsuit", "compliance", "court", "regulation",
        "document", "agreement", "law"
    ],
    "finance-bot": [
        "finance", "budget", "investment", "portfolio", "tax", "loan", "crypto",
        "ROI", "cash flow", "balance sheet"
    ],
    "real-estate-bot": [
        "real estate", "property", "house", "rental", "mortgage", "cap rate", "flip",
        "investment property", "neighborhood", "appraisal"
    ],
    "ecommerce-bot": [
        "ecommerce", "shopify", "amazon", "listing", "product", "inventory", "shipping",
        "store", "marketplace", "dropship"
    ],
    "marketing-bot": [
        "marketing", "SEO", "social media", "campaign", "brand", "content", "ad",
        "email marketing", "analytics", "keywords"
    ],
    "education-bot": [
        "education", "learn", "study", "quiz", "course", "certification", "skill",
        "training", "curriculum", "student"
    ],
    "cybersecurity-bot": [
        "security", "hacker", "vulnerability", "password", "GDPR", "CCPA", "firewall",
        "phishing", "breach", "cyber"
    ],
    "hr-bot": [
        "HR", "hire", "employee", "onboarding", "resume", "interview", "salary",
        "job description", "performance review", "workforce"
    ],
    "farewell-bot": [
        "funeral", "obituary", "memorial", "grief", "burial", "cremation", "death",
        "bereavement", "service planning", "farewell"
    ],
}


class Orchestrator:
    """Central orchestrator that routes requests to appropriate bots."""

    def __init__(self):
        """Initialize the orchestrator with empty bot registry and client memory."""
        self._bots = {}
        self._client_memory = {}
        self._event_log = []

    def register_bot(self, name: str, bot):
        """Register a bot with the orchestrator."""
        self._bots[name] = bot
        self._log_event(f"Bot registered: {name}")

    def deregister_bot(self, name: str):
        """Remove a bot from the orchestrator."""
        self._bots.pop(name, None)
        self._log_event(f"Bot deregistered: {name}")

    def route_request(self, request_text: str) -> dict:
        """Route a text request to the most appropriate registered bot."""
        text_lower = request_text.lower()
        best_bot = None
        best_score = 0

        for bot_name, keywords in ROUTING_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw.lower() in text_lower)
            if score > best_score:
                best_score = score
                best_bot = bot_name

        if best_bot and best_bot in self._bots:
            self._log_event(f"Routed request to {best_bot} (score={best_score})")
            return {
                "routed_to": best_bot,
                "score": best_score,
                "bot_status": self._bots[best_bot].get_status(),
                "message": f"Request routed to {best_bot}",
            }
        return {
            "routed_to": "buddy-bot",
            "score": 0,
            "message": "No specific bot matched; routing to BuddyBot",
        }

    def dispatch(self, bot_name: str, task: dict) -> dict:
        """Send a task to a specific registered bot."""
        bot = self._bots.get(bot_name)
        if bot is None:
            return {"error": f"Bot '{bot_name}' not found"}

        action = task.get("action", "get_status")
        params = task.get("params", {})
        method = getattr(bot, action, None)

        if callable(method):
            try:
                result = method(**params) if params else method()
                self._log_event(f"Dispatched '{action}' to {bot_name}")
                return {"bot": bot_name, "action": action, "result": result}
            except Exception as e:
                return {"bot": bot_name, "action": action, "error": str(e)}
        return {"error": f"Action '{action}' not found on {bot_name}"}

    def get_all_statuses(self) -> dict:
        """Return status dictionaries for all registered bots."""
        return {name: bot.get_status() for name, bot in self._bots.items()}

    def learn_preference(self, client_id: str, preference: dict):
        """Store a client preference for future recommendations."""
        if client_id not in self._client_memory:
            self._client_memory[client_id] = {"preferences": [], "history": []}
        self._client_memory[client_id]["preferences"].append({
            "timestamp": datetime.utcnow().isoformat(),
            "preference": preference,
        })

    def get_recommendation(self, client_id: str) -> dict:
        """Return personalized bot recommendations for a client."""
        memory = self._client_memory.get(client_id, {})
        preferences = memory.get("preferences", [])
        active_bots = [name for name, bot in self._bots.items()
                       if getattr(bot, "_status", "stopped") == "running"]
        return {
            "client_id": client_id,
            "recommended_bots": active_bots[:5],
            "preference_count": len(preferences),
            "message": "Based on your history, these bots can help you today.",
        }

    def _log_event(self, message: str):
        """Log an orchestrator event."""
        self._event_log.append({
            "timestamp": datetime.utcnow().isoformat(),
            "message": message,
        })
        if len(self._event_log) > 500:
            self._event_log = self._event_log[-500:]

    def get_event_log(self) -> list:
        """Return the orchestrator event log."""
        return list(self._event_log)
