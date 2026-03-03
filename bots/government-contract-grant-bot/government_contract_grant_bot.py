"""Government Contract & Grant Bot - finds and applies for federal opportunities."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from core.base_bot import BaseBot


class GovernmentContractGrantBot(BaseBot):
    """AI bot for discovering and applying for government contracts and grants."""

    def __init__(self):
        """Initialize the Government Contract & Grant Bot."""
        super().__init__(
            name="government-contract-grant-bot",
            description="Finds and applies for federal contracts, SBIR/STTR grants, and government funding opportunities.",
            version="2.0.0",
        )
        self.priority = "high"
        self._applied_contracts = []
        self._applied_grants = []

    def run(self):
        """Run the government contract and grant bot main workflow."""
        self.start()
        opportunities = self.search_opportunities(["technology", "AI", "small business"])
        self.log(f"Found {len(opportunities)} opportunities")
        return opportunities

    def search_opportunities(self, keywords: list) -> list:
        """Search for government contract and grant opportunities matching keywords."""
        keyword_str = ", ".join(keywords) if keywords else "general"
        opportunities = [
            {
                "id": "SAM-2024-001",
                "type": "contract",
                "title": f"AI Solutions for Federal Agency Operations ({keyword_str})",
                "agency": "Department of Defense",
                "value": "$2,500,000",
                "deadline": "2024-12-31",
                "naics_code": "541511",
                "set_aside": "Small Business",
                "status": "open",
                "link": "https://sam.gov/opp/SAM-2024-001",
            },
            {
                "id": "SBIR-2024-Phase2-042",
                "type": "grant",
                "title": f"SBIR Phase II: Advanced Technology Development ({keyword_str})",
                "agency": "National Science Foundation",
                "value": "$750,000",
                "deadline": "2024-11-15",
                "program": "SBIR Phase II",
                "status": "open",
                "link": "https://www.sbir.gov/node/2024-042",
            },
            {
                "id": "STTR-2024-T1-018",
                "type": "grant",
                "title": "STTR Topic: Cybersecurity Innovation for Critical Infrastructure",
                "agency": "Department of Homeland Security",
                "value": "$1,000,000",
                "deadline": "2025-01-20",
                "program": "STTR Phase I",
                "status": "open",
                "link": "https://www.sbir.gov/sttr/2024-T1-018",
            },
            {
                "id": "GRANT-HHS-2024-055",
                "type": "grant",
                "title": "Healthcare Technology Modernization Grant",
                "agency": "Department of Health and Human Services",
                "value": "$500,000",
                "deadline": "2024-10-30",
                "program": "HHS Tech Modernization",
                "status": "open",
                "link": "https://grants.gov/HHS-2024-055",
            },
            {
                "id": "BPA-DOE-2024-012",
                "type": "contract",
                "title": "Blanket Purchase Agreement: Clean Energy Analytics Platform",
                "agency": "Department of Energy",
                "value": "$5,000,000",
                "deadline": "2025-02-28",
                "naics_code": "541512",
                "set_aside": "8(a) Program",
                "status": "open",
                "link": "https://sam.gov/opp/BPA-DOE-2024-012",
            },
        ]
        self.log(f"Searched opportunities with keywords: {keyword_str}")
        return opportunities

    def apply_for_contract(self, contract_id: str) -> dict:
        """Simulate the process of applying for a government contract."""
        self._applied_contracts.append(contract_id)
        self.add_revenue(149.00)
        result = {
            "contract_id": contract_id,
            "status": "application_submitted",
            "submission_date": "2024-10-01",
            "documents_prepared": [
                "SF-1449 Standard Form",
                "Technical Proposal",
                "Price/Cost Volume",
                "Past Performance Narrative",
                "SAM.gov Registration Verification",
            ],
            "estimated_review_time": "30-45 business days",
            "message": f"Application for contract {contract_id} submitted successfully.",
        }
        self.log(f"Applied for contract: {contract_id}")
        return result

    def apply_for_grant(self, grant_id: str) -> dict:
        """Simulate the process of applying for a government grant."""
        self._applied_grants.append(grant_id)
        self.add_revenue(99.00)
        result = {
            "grant_id": grant_id,
            "status": "application_submitted",
            "submission_date": "2024-10-01",
            "documents_prepared": [
                "SF-424 Application for Federal Assistance",
                "Project Narrative",
                "Budget Justification",
                "Key Personnel CVs",
                "Organizational Chart",
                "Data Management Plan",
            ],
            "grants_gov_tracking": f"GRANTS-{grant_id}-2024",
            "estimated_review_time": "60-90 days",
            "message": f"Grant application {grant_id} submitted via Grants.gov.",
        }
        self.log(f"Applied for grant: {grant_id}")
        return result

    def get_funding_recommendations(self) -> dict:
        """Return funding recommendations based on bot profile and business type."""
        recommendations = {
            "top_programs": [
                {
                    "program": "SBIR Phase I",
                    "agency": "Multiple Agencies",
                    "award_amount": "$275,000",
                    "success_rate": "15-25%",
                    "best_for": "Early-stage technology companies",
                    "tip": "Focus on clear commercialization potential",
                },
                {
                    "program": "8(a) Business Development",
                    "agency": "SBA",
                    "award_amount": "Up to $22M (sole source)",
                    "success_rate": "Eligible companies get contracts",
                    "best_for": "Socially and economically disadvantaged business owners",
                    "tip": "Apply early; certification takes 90+ days",
                },
                {
                    "program": "HUBZone Certification",
                    "agency": "SBA",
                    "award_amount": "10% price evaluation preference",
                    "success_rate": "Varies by opportunity",
                    "best_for": "Businesses in historically underutilized zones",
                    "tip": "Check your location eligibility at maps.certify.sba.gov",
                },
                {
                    "program": "WOSB Federal Contract Program",
                    "agency": "SBA",
                    "award_amount": "Set-aside contracts",
                    "success_rate": "Growing opportunity set",
                    "best_for": "Women-owned small businesses",
                    "tip": "Self-certify on SAM.gov or use a third-party certifier",
                },
            ],
            "action_steps": [
                "Register on SAM.gov (required for all federal contracting)",
                "Get a DUNS/UEI number from SAM.gov",
                "Identify your NAICS codes",
                "Complete your capability statement (one-page)",
                "Attend agency small business outreach events",
            ],
            "resources": [
                "https://sam.gov",
                "https://grants.gov",
                "https://sbir.gov",
                "https://www.sba.gov/federal-contracting",
            ],
        }
        self.log("Generated funding recommendations")
        return recommendations

    def get_status(self) -> dict:
        """Return detailed status including applied contracts and grants."""
        base = super().get_status()
        base.update({
            "applied_contracts": len(self._applied_contracts),
            "applied_grants": len(self._applied_grants),
        })
        return base


if __name__ == "__main__":
    bot = GovernmentContractGrantBot()
    bot.run()
