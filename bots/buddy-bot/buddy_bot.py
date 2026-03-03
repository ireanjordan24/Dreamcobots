"""Buddy Bot - Central AI assistant that orchestrates all DreamCobots bots."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from datetime import datetime
from core.base_bot import BaseBot


class BuddyBot(BaseBot):
    """Central AI assistant and orchestrator for the DreamCobots ecosystem."""

    def __init__(self):
        """Initialize the BuddyBot."""
        super().__init__(
            name="buddy-bot",
            description="Central AI assistant that routes requests, delegates tasks, and coordinates all bots.",
            version="2.0.0",
        )
        self.priority = "critical"
        self._delegated_bots = {}
        self._client_memory = {}
        self._weekly_log = []

    def run(self):
        """Run the buddy bot main workflow."""
        self.start()
        return self.get_capabilities()

    def process_request(self, request: str, client_id: str = "default") -> dict:
        """Process a request, route it to the appropriate bot, and return results."""
        request_lower = request.lower()
        routing_map = {
            "contract": "government-contract-grant-bot",
            "grant": "government-contract-grant-bot",
            "hustle": "hustle-bot",
            "revenue": "hustle-bot",
            "referral": "referral-bot",
            "business plan": "entrepreneur-bot",
            "startup": "entrepreneur-bot",
            "medical": "medical-bot",
            "health": "medical-bot",
            "legal": "legal-bot",
            "contract review": "legal-bot",
            "budget": "finance-bot",
            "investment": "finance-bot",
            "real estate": "real-estate-bot",
            "property": "real-estate-bot",
            "ecommerce": "ecommerce-bot",
            "product listing": "ecommerce-bot",
            "marketing": "marketing-bot",
            "seo": "marketing-bot",
            "education": "education-bot",
            "learn": "education-bot",
            "security": "cybersecurity-bot",
            "cyber": "cybersecurity-bot",
            "hr": "hr-bot",
            "employee": "hr-bot",
            "funeral": "farewell-bot",
            "memorial": "farewell-bot",
        }
        matched_bot = None
        for keyword, bot_name in routing_map.items():
            if keyword in request_lower:
                matched_bot = bot_name
                break

        self.remember(client_id, "last_request", request)

        response = {
            "request": request,
            "client_id": client_id,
            "routed_to": matched_bot or "buddy-bot",
            "timestamp": datetime.utcnow().isoformat(),
            "suggestions": self.get_capabilities()["top_capabilities"][:3],
            "message": (
                f"I've routed your request to {matched_bot}."
                if matched_bot
                else "I'm handling your request directly. How can I help you further?"
            ),
        }
        self.log(f"Processed request for {client_id}: {request[:80]}")
        return response

    def delegate_to_bot(self, bot_name: str, task: str) -> dict:
        """Delegate a specific task to a named bot."""
        self._delegated_bots[bot_name] = self._delegated_bots.get(bot_name, 0) + 1
        self.log(f"Delegated task to {bot_name}: {task[:60]}")
        return {
            "delegated_to": bot_name,
            "task": task,
            "status": "dispatched",
            "timestamp": datetime.utcnow().isoformat(),
        }

    def merge_results(self, results: list) -> dict:
        """Merge and summarize results from multiple bots."""
        merged = {
            "total_results": len(results),
            "sources": [],
            "combined_data": [],
            "summary": f"Merged {len(results)} result sets from DreamCobots bots.",
            "timestamp": datetime.utcnow().isoformat(),
        }
        for result in results:
            if isinstance(result, dict):
                source = result.get("bot", result.get("source", "unknown"))
                merged["sources"].append(source)
                merged["combined_data"].append(result)
        return merged

    def remember(self, client_id: str, key: str, value):
        """Store a preference or data point for a specific client."""
        if client_id not in self._client_memory:
            self._client_memory[client_id] = {}
        self._client_memory[client_id][key] = {
            "value": value,
            "stored_at": datetime.utcnow().isoformat(),
        }

    def recall(self, client_id: str, key: str):
        """Retrieve a stored preference for a specific client."""
        client_data = self._client_memory.get(client_id, {})
        entry = client_data.get(key)
        if entry:
            return entry.get("value")
        return None

    def get_capabilities(self) -> dict:
        """List all available capabilities across the DreamCobots ecosystem."""
        return {
            "platform": "DreamCobots",
            "version": "2.0.0",
            "total_bots": 15,
            "top_capabilities": [
                "Government contract and grant discovery",
                "Revenue goal setting and hustle optimization",
                "50% referral commission tracking",
                "Business plan generation",
                "Medical information with HIPAA compliance",
                "Legal document drafting",
                "Financial planning and analysis",
                "Real estate investment analysis",
                "E-commerce listing optimization",
                "Marketing campaigns and SEO",
                "Personalized learning plans",
                "Cybersecurity audits",
                "HR and hiring automation",
                "Funeral and memorial planning",
            ],
            "revenue_model": "50% revenue share with clients",
        }

    def weekly_suggestions(self) -> list:
        """Return a list of weekly improvement suggestions for the platform."""
        suggestions = [
            "Activate 3 additional bots to maximize revenue potential this week",
            "Review your referral program - top referrers need recognition",
            "Check for new government contract opportunities (SAM.gov updates weekly)",
            "Update your compliance packages - regulations change quarterly",
            "Run a stress test to ensure all bots are performing optimally",
            "Analyze last week's revenue streams and double down on top performers",
            "Onboard 2 new clients with the 50% revenue share pitch",
        ]
        entry = {"week": datetime.utcnow().isocalendar()[1], "suggestions": suggestions}
        self._weekly_log.append(entry)
        return suggestions
