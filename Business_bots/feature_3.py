"""
Feature 3: Business bot for invoicing.
Functionality: Generates and sends invoices to clients.
Use Cases: Freelancers needing to bill their clients.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from datetime import date, timedelta
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class InvoicingBot(BotBase):
    """Generates, sends, and tracks invoices."""

    DEFAULT_PAYMENT_TERMS_DAYS = 30

    def __init__(self) -> None:
        super().__init__("InvoicingBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._invoices: list = []

    def generate_invoice(self, client: str, line_items: list, currency: str = "USD") -> dict:
        """Create an invoice from a list of line items."""
        subtotal = sum(item["qty"] * item["unit_price"] for item in line_items)
        tax = round(subtotal * 0.08, 2)
        total = round(subtotal + tax, 2)
        invoice = {
            "invoice_id": f"INV-{str(uuid.uuid4())[:8].upper()}",
            "client": client,
            "line_items": line_items,
            "subtotal": round(subtotal, 2),
            "tax": tax,
            "total": total,
            "currency": currency,
            "issue_date": date.today().isoformat(),
            "due_date": (date.today() + timedelta(days=self.DEFAULT_PAYMENT_TERMS_DAYS)).isoformat(),
            "status": "draft",
        }
        self._invoices.append(invoice)
        return invoice

    def send_invoice(self, invoice_id: str) -> dict:
        """Mark an invoice as sent."""
        for inv in self._invoices:
            if inv["invoice_id"] == invoice_id:
                inv["status"] = "sent"
                return {"status": "ok", "invoice_id": invoice_id}
        return {"status": "error", "message": "Invoice not found"}

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "generate_invoice":
            inv = self.generate_invoice(task.get("client", ""), task.get("line_items", []))
            return {"status": "ok", "invoice_id": inv["invoice_id"], "total": inv["total"]}
        return super()._run_task(task)


if __name__ == "__main__":
    bot = InvoicingBot()
    bot.start()
    items = [{"description": "Bot development", "qty": 10, "unit_price": 150}]
    inv = bot.generate_invoice("Acme Corp", items)
    print(inv)
    bot.stop()