# Government Contract & Grant Bot
# Functionality: Searches, filters, and notifies users of government contracts and grants.
# Use Cases: Small businesses, nonprofits, and contractors seeking government funding opportunities.

import json
import os


CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")


def load_config(path=CONFIG_PATH):
    """Load bot configuration from config.json."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"Configuration file not found: {path}")
    with open(path, "r") as f:
        return json.load(f)


class GovernmentContractGrantBot:
    def __init__(self, config=None):
        """Initialize the bot, loading configuration from file if not provided."""
        if config is None:
            config = load_config()
        self.api_key = config.get("api_key", "")
        self.search_keywords = config.get("search_keywords", [])
        self.naics_codes = config.get("naics_codes", [])
        self.max_results = config.get("max_results", 10)
        self.notify_email = config.get("notify_email", "")
        self.sources = config.get("sources", ["SAM.gov", "Grants.gov"])
        self.results = {"contracts": [], "grants": []}

    def start(self):
        """Start the bot and display configuration summary."""
        print("Government Contract & Grant Bot is starting...")
        print(f"  Sources:  {', '.join(self.sources)}")
        print(f"  Keywords: {', '.join(self.search_keywords) if self.search_keywords else 'None'}")
        print(f"  NAICS codes: {', '.join(self.naics_codes) if self.naics_codes else 'None'}")
        print(f"  Max results per source: {self.max_results}")

    def search_contracts(self):
        """Search for government contracts matching configured keywords and NAICS codes."""
        print("\nSearching for government contracts...")
        # In production, replace this stub with a real API call to SAM.gov or a similar source.
        # Example endpoint: https://api.sam.gov/opportunities/v2/search
        contracts = []
        for keyword in self.search_keywords:
            entry = {
                "source": "SAM.gov",
                "title": f"Contract opportunity for: {keyword}",
                "naics": self.naics_codes[0] if self.naics_codes else "N/A",
                "deadline": "2026-06-01",
                "url": "https://sam.gov/search/",
            }
            contracts.append(entry)
        self.results["contracts"] = contracts
        print(f"  Found {len(contracts)} contract opportunity(ies).")
        return contracts

    def search_grants(self):
        """Search for government grants matching configured keywords."""
        print("\nSearching for government grants...")
        # In production, replace this stub with a real API call to Grants.gov or a similar source.
        # Example endpoint: https://www.grants.gov/web/grants/search-grants.html
        grants = []
        for keyword in self.search_keywords:
            entry = {
                "source": "Grants.gov",
                "title": f"Grant opportunity for: {keyword}",
                "agency": "Department of Commerce",
                "deadline": "2026-07-15",
                "url": "https://www.grants.gov/search-grants",
            }
            grants.append(entry)
        self.results["grants"] = grants
        print(f"  Found {len(grants)} grant opportunity(ies).")
        return grants

    def filter_results(self, results, naics_codes=None):
        """Filter results by NAICS codes (if provided)."""
        codes = naics_codes or self.naics_codes
        if not codes:
            return results
        filtered = [r for r in results if r.get("naics") in codes]
        print(f"  Filtered to {len(filtered)} result(s) matching NAICS codes: {', '.join(codes)}")
        return filtered

    def display_results(self):
        """Print a formatted summary of all search results."""
        print("\n--- Contract Opportunities ---")
        if self.results["contracts"]:
            for i, c in enumerate(self.results["contracts"], 1):
                print(f"  {i}. [{c['source']}] {c['title']}")
                print(f"     NAICS: {c['naics']} | Deadline: {c['deadline']}")
                print(f"     URL: {c['url']}")
        else:
            print("  No contract opportunities found.")

        print("\n--- Grant Opportunities ---")
        if self.results["grants"]:
            for i, g in enumerate(self.results["grants"], 1):
                print(f"  {i}. [{g['source']}] {g['title']}")
                print(f"     Agency: {g['agency']} | Deadline: {g['deadline']}")
                print(f"     URL: {g['url']}")
        else:
            print("  No grant opportunities found.")

    def notify(self):
        """Send a notification summary to the configured email address."""
        if not self.notify_email:
            print("\nNo notification email configured. Skipping notification.")
            return
        total = len(self.results["contracts"]) + len(self.results["grants"])
        print(f"\nNotification: Sending summary of {total} opportunity(ies) to {self.notify_email}...")
        # In production, integrate with an email service (e.g., SendGrid, SMTP) here.
        print("  Notification sent (stub).")

    def process_contracts(self):
        """Search and display contracts."""
        contracts = self.search_contracts()
        self.results["contracts"] = contracts

    def process_grants(self):
        """Search and display grants."""
        grants = self.search_grants()
        self.results["grants"] = grants

    def run(self):
        """Run the full bot pipeline: start, search, display, and notify."""
        self.start()
        self.process_contracts()
        self.process_grants()
        self.display_results()
        self.notify()
        print("\nGovernment Contract & Grant Bot finished.")


# If this module is run directly, start the bot
if __name__ == '__main__':
    bot = GovernmentContractGrantBot()
    bot.run()
