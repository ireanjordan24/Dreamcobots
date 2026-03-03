# Feature 3: Business bot for invoicing.
# Functionality: Generates and sends invoices to clients.
# Use Cases: Freelancers needing to bill their clients.

import sys
import os
import time
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from framework import BaseBot
from framework.monetization import PricingPlan, PricingModel


class InvoicingBot(BaseBot):
    """
    Business bot that automates invoice generation and client billing.

    Generates itemised invoices, tracks payment status, and sells
    freelance-billing datasets to fintech and accounting companies.
    """

    def __init__(self):
        super().__init__(
            name="Invoicing Bot",
            domain="finance",
            category="business",
        )
        self._invoice_counter = 1000

    def _setup_datasets(self):
        self.datasets.create_dataset(
            name="Freelance Billing Patterns Dataset",
            description="Anonymised invoice data from 20,000 freelancers including rates and payment times.",
            domain="finance",
            size_mb=45.0,
            price_usd=89.00,
            license="Proprietary",
            tags=["invoicing", "freelance", "billing", "fintech"],
            ethical_review_passed=True,
        )

    def _setup_plans(self):
        super()._setup_plans()
        self.monetization.add_plan(PricingPlan(
            plan_id="invoicing_pro",
            name="Invoicing Pro",
            model=PricingModel.SUBSCRIPTION,
            price_usd=14.99,
            description="Unlimited invoice generation with auto-reminders.",
            features=["Unlimited invoices", "Payment reminders", "PDF export", "Client portal"],
        ))

    def _generate_invoice_number(self) -> str:
        number = f"INV-{self._invoice_counter}"
        self._invoice_counter += 1
        return number

    def _build_response(self, nlp_result, user_id):
        intent = nlp_result["intent"]
        prefix = self._emotion_prefix()
        numbers = nlp_result.get("entities", {}).get("numbers", [])

        if intent == "invoice":
            inv_num = self._generate_invoice_number()
            amount = f"${numbers[0]}" if numbers else "the agreed amount"
            response = (
                f"{prefix}I'll generate invoice **{inv_num}** for {amount}. "
                "Please confirm: client name, service description, and due date."
            )
        elif intent == "pricing_inquiry":
            response = (
                f"{prefix}Our invoicing plans start free. "
                "The Pro plan is $14.99/month for unlimited invoices with auto-reminders."
            )
        elif intent == "dataset_purchase":
            response = (
                f"{prefix}I offer freelance billing pattern datasets for fintech research."
                + self._dataset_offer()
            )
        elif intent == "greeting":
            response = (
                f"{prefix}Hi! I'm {self.name}. I'll handle your invoicing so you can "
                "focus on your work. Ready to create an invoice?"
            )
        elif intent == "help":
            response = (
                "I can: 🧾 Generate invoices  |  📧 Send payment reminders  |  "
                "💳 Track payment status  |  💾 Sell billing datasets."
            )
        else:
            response = (
                f"{prefix}Tell me the client name, service, and amount and I'll "
                "create a professional invoice right away."
            )
        return response


if __name__ == "__main__":
    bot = InvoicingBot()
    print(bot.chat("Hello! I need to invoice a client for $1500."))
    print(bot.chat("The client is Acme Corp, for web design services."))
    print(bot.status())