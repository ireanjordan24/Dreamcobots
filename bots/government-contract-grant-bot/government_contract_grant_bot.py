# Government Contract & Grant Bot

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from bots.discount_dominator import (
    DiscountDominator,
    GROUP_ANALYTICS,
    GROUP_ENTERPRISE,
)


class GovernmentContractGrantBot:
    """Government Contract & Grant Bot with Discount Dominator integration.

    Leverages Discount Dominator settings 401–600 to enhance analytics,
    compliance monitoring, and enterprise-grade features for government
    contract and grant operations.
    """

    def __init__(self, dd_overrides=None):
        self._dd = DiscountDominator(overrides=dd_overrides)

    @property
    def discount_dominator(self):
        """Access the embedded Discount Dominator instance."""
        return self._dd

    def start(self):
        print("Government Contract & Grant Bot is starting...")
        print(
            f"  Discount Dominator active — "
            f"{self._dd.SETTINGS_COUNT} settings (401–600) loaded."
        )

    def process_contracts(self):
        print("Processing contracts...")
        if self._dd.enterprise.compliance_monitoring:
            print("  Compliance monitoring: active")
        if self._dd.enterprise.audit_trail_retention_years:
            print(
                f"  Audit trail retention: "
                f"{self._dd.enterprise.audit_trail_retention_years} years"
            )

    def process_grants(self):
        print("Processing grants...")
        if self._dd.analytics.realtime_enabled:
            print("  Real-time analytics: active")
        if self._dd.analytics.analytics_api_enabled:
            print("  Analytics API: enabled")

    def run(self):
        self.start()
        self.process_contracts()
        self.process_grants()


# If this module is run directly, start the bot
if __name__ == '__main__':
    bot = GovernmentContractGrantBot()
    bot.run()
