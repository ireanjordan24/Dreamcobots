"""
Feature 2: Fiverr bot for order management.
Functionality: Tracks and manages incoming orders from clients.
Use Cases: Sellers needing to stay organized.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import uuid
from core.bot_base import AutonomyLevel, BotBase, ScalingLevel


class OrderManagementBot(BotBase):
    """Tracks and manages Fiverr orders."""

    def __init__(self) -> None:
        super().__init__("OrderManagementBot", AutonomyLevel.SEMI_AUTONOMOUS, ScalingLevel.MODERATE)
        self._orders: dict = {}

    def receive_order(self, client: str, service: str, amount: float, requirements: str) -> dict:
        """Record a new incoming order."""
        order_id = str(uuid.uuid4())
        self._orders[order_id] = {
            "order_id": order_id, "client": client, "service": service,
            "amount": amount, "requirements": requirements, "status": "in_progress",
        }
        return {"status": "ok", "order_id": order_id}

    def complete_order(self, order_id: str) -> dict:
        """Mark an order as complete."""
        order = self._orders.get(order_id)
        if not order:
            return {"status": "error", "message": "Order not found"}
        order["status"] = "delivered"
        return {"status": "ok", "order_id": order_id, "new_status": "delivered"}

    def get_orders(self, status: str = None) -> list:
        """Return all (or status-filtered) orders."""
        orders = list(self._orders.values())
        if status:
            orders = [o for o in orders if o["status"] == status]
        return orders

    def _run_task(self, task: dict) -> dict:
        if task.get("type") == "receive_order":
            return self.receive_order(
                task.get("client", ""), task.get("service", ""),
                task.get("amount", 0), task.get("requirements", ""),
            )
        return super()._run_task(task)


if __name__ == "__main__":
    bot = OrderManagementBot()
    bot.start()
    order = bot.receive_order("John Doe", "AI Bot", 300, "Build a Telegram bot")
    print(bot.complete_order(order["order_id"]))
    bot.stop()