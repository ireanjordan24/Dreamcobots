# Feature 2: Fiverr bot for order management.
# Functionality: Tracks and manages incoming orders from clients.
# Use Cases: Sellers needing to stay organized.
#
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
# See framework/global_ai_sources_flow.py for the full pipeline specification.
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from framework import GlobalAISourcesFlow


class FiverrOrderManager:
    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="FiverrOrderManager")
        self._orders = {}

    def create_order(self, client_name, service_title, price_usd, deadline_days):
        order_id = f"order_{len(self._orders)+1}"
        order = {"order_id": order_id, "client_name": client_name, "service_title": service_title, "price_usd": price_usd, "deadline_days": deadline_days, "status": "pending"}
        self._orders[order_id] = order
        return order

    def update_status(self, order_id, status):
        if order_id in self._orders:
            self._orders[order_id]["status"] = status
            return True
        return False

    def get_orders(self, status=None):
        orders = list(self._orders.values())
        if status:
            return [o for o in orders if o["status"] == status]
        return orders

    def run(self):
        return self.flow.run_pipeline(raw_data={"bot": "FiverrOrderManager", "orders": len(self._orders)}, learning_method="supervised")
