# BuddyAI - Central AI hub for managing and communicating with all Dreamcobots bots.

import json
import time


class BuddyAI:
    """Central AI hub that orchestrates all Dreamcobots bots and services."""

    def __init__(self, config_path=None):
        self.bots = {}
        self.running = False
        self.start_time = None
        self.analytics_data = {
            "commands_executed": 0,
            "messages_broadcast": 0,
            "devices_registered": 0,
        }
        if config_path:
            self._load_config(config_path)

    def _load_config(self, config_path):
        try:
            with open(config_path, "r") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}

    def register_bot(self, bot_id, bot_instance):
        """Register a bot with BuddyAI."""
        self.bots[bot_id] = {"instance": bot_instance, "status": "registered"}
        print(f"Bot '{bot_id}' registered with BuddyAI.")

    def get_status(self):
        """Return the current status of BuddyAI and all bots."""
        return {
            "running": self.running,
            "uptime_seconds": time.time() - self.start_time if self.start_time else 0,
            "bots": {bid: info["status"] for bid, info in self.bots.items()},
            "analytics": self.analytics_data,
        }
