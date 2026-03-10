"""
Dreamcobots Government Contract & Grant Bot — tier-aware contract and grant management.

Usage
-----
    from government_contract_grant_bot import GovernmentContractGrantBot
    from tiers import Tier

    bot = GovernmentContractGrantBot(tier=Tier.FREE)
    result = bot.search_contracts("IT services")
    print(result)
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from tiers import Tier, get_tier_config, get_upgrade_path
from framework import GlobalAISourcesFlow

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_govbot_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_govbot_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_govbot_tiers)
GOVBOT_FEATURES = _govbot_tiers.GOVBOT_FEATURES
get_govbot_tier_info = _govbot_tiers.get_govbot_tier_info


class GovBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class GovBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class GovernmentContractGrantBot:
    """
    Tier-aware Government Contract & Grant Bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability and request limits.
    """

    def __init__(self, tier: Tier = Tier.FREE, config=None):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self.flow = GlobalAISourcesFlow(bot_name="GovernmentContractGrantBot")
        # Results store for backward compatibility
        self.results = {
            "contracts_found": [],
            "grants_found": [],
            "summary": "",
        }

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def search_contracts(self, query: str = "", keywords: list | None = None, filters: dict | None = None) -> dict:
        """Search government contracts matching the given query or keywords."""
        self._check_request_limit()
        if filters and self.tier == Tier.FREE:
            raise GovBotTierError(
                "Advanced contract search with filters requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        mock_results = [
            {
                "contract_id": f"GOV-{i:04d}",
                "title": f"Mock contract matching '{query or 'general'}' #{i}",
                "agency": "Department of Mock Affairs",
                "value_usd": (i + 1) * 100_000,
                "deadline": "2025-12-31",
                "keywords": keywords or ["general"],
            }
            for i in range(1, 4 if self.tier == Tier.FREE else 11)
        ]
        if keywords:
            mock_results = [r for r in mock_results if any(k in r["keywords"] for k in keywords)]
        self.results["contracts_found"] = mock_results
        return {
            "query": query,
            "filters": filters,
            "results": mock_results,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def search_grants(self, query: str = "", keywords: list | None = None, filters: dict | None = None) -> dict:
        """Search government grants matching the given query or keywords."""
        self._check_request_limit()
        self._request_count += 1
        mock_results = [
            {
                "grant_id": f"GRANT-{i:04d}",
                "title": f"Mock grant matching '{query or 'general'}' #{i}",
                "agency": "Department of Innovation",
                "amount_usd": (i + 1) * 50_000,
                "deadline": "2025-12-31",
                "keywords": keywords or ["innovation"],
            }
            for i in range(1, 4 if self.tier == Tier.FREE else 11)
        ]
        if keywords:
            mock_results = [r for r in mock_results if any(k in r["keywords"] for k in keywords)]
        self.results["grants_found"] = mock_results
        return {
            "query": query,
            "filters": filters,
            "results": mock_results,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def _score_opportunity(self, value: int) -> int:
        """Score an opportunity (1-10) based on its value."""
        if value >= 1_000_000:
            return 10
        elif value >= 500_000:
            return 8
        elif value >= 150_000:
            return 6
        elif value >= 50_000:
            return 4
        else:
            return 2

    def process_contracts(self) -> None:
        """Score and enrich contracts in results."""
        print("Processing contracts...")
        for contract in self.results["contracts_found"]:
            contract["score"] = self._score_opportunity(contract.get("value_usd", 50000))

    def process_grants(self) -> None:
        """Score and enrich grants in results."""
        print("Processing grants...")
        for grant in self.results["grants_found"]:
            grant["score"] = self._score_opportunity(grant.get("amount_usd", 25000))

    def generate_report(self) -> dict:
        """Generate a summary report of contracts and grants found."""
        import datetime
        contracts = self.results["contracts_found"]
        grants = self.results["grants_found"]
        summary = f"Contracts found: {len(contracts)}, Grants found: {len(grants)}"
        self.results["summary"] = summary
        report = {
            "summary": summary,
            "contracts": contracts,
            "grants": grants,
            "generated_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        return report

    def check_grant_eligibility(self, org_profile: dict) -> dict:
        """Check whether an organization profile is eligible for grants."""
        self._check_request_limit()
        self._request_count += 1
        eligible_grants = [
            {
                "grant_id": "GR-001",
                "title": "Small Business Innovation Grant",
                "amount_usd": 50_000,
                "eligibility": "Eligible based on profile",
            }
        ]
        if self.tier in (Tier.PRO, Tier.ENTERPRISE):
            eligible_grants.append({
                "grant_id": "GR-002",
                "title": "Technology Modernization Grant",
                "amount_usd": 250_000,
                "eligibility": "Eligible — advanced matching",
            })
        if self.tier == Tier.ENTERPRISE:
            eligible_grants.append({
                "grant_id": "GR-003",
                "title": "Enterprise Compliance Grant",
                "amount_usd": 1_000_000,
                "eligibility": "Custom matched by specialist",
            })
        return {
            "org_profile": org_profile,
            "eligible_grants": eligible_grants,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def draft_grant_application(self, grant_id: str, org_profile: dict) -> dict:
        """Draft a grant application. Requires PRO or ENTERPRISE tier."""
        self._check_request_limit()
        if self.tier == Tier.FREE:
            raise GovBotTierError(
                "Grant application drafting is not available on the FREE tier. "
                "Upgrade to PRO or ENTERPRISE."
            )
        self._request_count += 1
        return {
            "grant_id": grant_id,
            "draft": f"[Mock draft application for grant {grant_id}]",
            "org_name": org_profile.get("name", "Unknown Organization"),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def track_compliance(self, contract_id: str) -> dict:
        """Track compliance status for a contract. Requires ENTERPRISE tier."""
        self._check_request_limit()
        if self.tier != Tier.ENTERPRISE:
            raise GovBotTierError(
                "Compliance tracking is only available on the ENTERPRISE tier."
            )
        self._request_count += 1
        return {
            "contract_id": contract_id,
            "compliance_status": "compliant",
            "last_checked": "2025-01-01",
            "issues": [],
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_govbot_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Government Contract & Grant Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["govbot_features"]:
            lines.append(f"  \u2713 {feat}")
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
        current_feats = set(GOVBOT_FEATURES[self.tier.value])
        new_feats = [
            f for f in GOVBOT_FEATURES[next_cfg.tier.value]
            if f not in current_feats
        ]
        lines = [
            f"=== Upgrade: {self.config.name} \u2192 {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing GovernmentContractGrantBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    def run(self) -> dict:
        """Run the full GlobalAISourcesFlow pipeline and return report."""
        self.search_contracts()
        self.search_grants()
        self.process_contracts()
        self.process_grants()
        report = self.generate_report()
        # Also run the framework pipeline
        pipeline_result = self.flow.run_pipeline()
        report["pipeline_complete"] = pipeline_result.get("pipeline_complete", True)
        report["pipeline_result"] = pipeline_result
        return report

    def start(self):
        """Start the Government Contract & Grant Bot."""
        print("Government Contract & Grant Bot is starting...")

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise GovBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = GovernmentContractGrantBot(tier=Tier.FREE)
    bot.describe_tier()
    result = bot.search_contracts("IT services")
    print(result)
