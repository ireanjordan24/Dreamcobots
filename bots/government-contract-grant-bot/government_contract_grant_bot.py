# Government Contract & Grant Bot

import json
import os
from datetime import datetime


class GovernmentContractGrantBot:
    def __init__(self, config=None):
        self.config = config or {}
        self.contracts = []
        self.grants = []
        self.results = {"contracts_found": [], "grants_found": [], "errors": []}

    def start(self):
        print("Government Contract & Grant Bot is starting...")
        print(f"Initialized at {datetime.now().isoformat()}")

    def search_contracts(self, keywords=None):
        """Search for government contracts matching given keywords."""
        keywords = keywords or self.config.get("contract_keywords", ["technology", "robotics", "automation"])
        print(f"Searching contracts with keywords: {keywords}")
        # Simulate contract discovery
        mock_contracts = [
            {
                "id": "CONT-2024-001",
                "title": "Collaborative Robotics Integration for Federal Facilities",
                "agency": "Department of Labor",
                "value": 500000,
                "deadline": "2025-06-30",
                "status": "open",
                "keywords": ["robotics", "automation"],
            },
            {
                "id": "CONT-2024-002",
                "title": "AI-Assisted Manufacturing Technology Procurement",
                "agency": "Department of Defense",
                "value": 1200000,
                "deadline": "2025-09-15",
                "status": "open",
                "keywords": ["technology", "automation"],
            },
        ]
        matched = [c for c in mock_contracts if any(kw in c["keywords"] for kw in keywords)]
        self.results["contracts_found"].extend(matched)
        print(f"Found {len(matched)} matching contracts.")
        return matched

    def search_grants(self, keywords=None):
        """Search for government grants matching given keywords."""
        keywords = keywords or self.config.get("grant_keywords", ["innovation", "robotics", "small business"])
        print(f"Searching grants with keywords: {keywords}")
        # Simulate grant discovery
        mock_grants = [
            {
                "id": "GRANT-2024-101",
                "title": "Small Business Innovation Research (SBIR) – Robotics",
                "agency": "National Science Foundation",
                "amount": 150000,
                "deadline": "2025-05-01",
                "status": "open",
                "keywords": ["robotics", "innovation", "small business"],
            },
            {
                "id": "GRANT-2024-102",
                "title": "Advanced Manufacturing Technology Grant",
                "agency": "Department of Energy",
                "amount": 250000,
                "deadline": "2025-07-31",
                "status": "open",
                "keywords": ["innovation", "robotics"],
            },
        ]
        matched = [g for g in mock_grants if any(kw in g["keywords"] for kw in keywords)]
        self.results["grants_found"].extend(matched)
        print(f"Found {len(matched)} matching grants.")
        return matched

    def process_contracts(self):
        """Process and score discovered contracts."""
        print("Processing contracts...")
        for contract in self.results["contracts_found"]:
            contract["score"] = self._score_opportunity(contract.get("value", 0))
            print(f"  [{contract['id']}] {contract['title']} — Score: {contract['score']}/10")

    def process_grants(self):
        """Process and score discovered grants."""
        print("Processing grants...")
        for grant in self.results["grants_found"]:
            grant["score"] = self._score_opportunity(grant.get("amount", 0))
            print(f"  [{grant['id']}] {grant['title']} — Score: {grant['score']}/10")

    def _score_opportunity(self, value):
        """Score an opportunity from 1–10 based on its monetary value."""
        if value >= 1_000_000:
            return 10
        elif value >= 500_000:
            return 8
        elif value >= 100_000:
            return 6
        elif value >= 50_000:
            return 4
        return 2

    def generate_report(self):
        """Generate a summary report of found opportunities."""
        total_contracts = len(self.results["contracts_found"])
        total_grants = len(self.results["grants_found"])
        total_value = sum(c.get("value", 0) for c in self.results["contracts_found"])
        total_grants_value = sum(g.get("amount", 0) for g in self.results["grants_found"])

        report = {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "contracts_found": total_contracts,
                "grants_found": total_grants,
                "total_contract_value": total_value,
                "total_grant_amount": total_grants_value,
            },
            "contracts": self.results["contracts_found"],
            "grants": self.results["grants_found"],
        }
        print("\n=== Government Contract & Grant Bot Report ===")
        print(json.dumps(report["summary"], indent=2))
        return report

    def run(self):
        self.start()
        self.search_contracts()
        self.search_grants()
        self.process_contracts()
        self.process_grants()
        return self.generate_report()


# If this module is run directly, start the bot
if __name__ == '__main__':
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    bot = GovernmentContractGrantBot(config=config.get("government_contract_grant_bot", {}))
    bot.run()