# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Referral Bot

import json
import os
from datetime import datetime


class ReferralBot:
    """
    Tracks user referrals, computes earnings for referrers, and integrates
    with the Hustle Bot to trigger motivational campaigns for underperformers.
    """

    DEFAULT_COMMISSION_RATE = 0.10  # 10% of referred user's revenue

    def __init__(self, config=None):
        self.config = config or {}
        self.commission_rate = self.config.get("commission_rate", self.DEFAULT_COMMISSION_RATE)
        # { referrer_id: { "referrals": [...], "total_earnings": float } }
        self._referrers = {}
        # { user_id: { "revenue": float, "referrer_id": str | None } }
        self._users = {}

    # ------------------------------------------------------------------
    # User & referral management
    # ------------------------------------------------------------------

    def register_user(self, user_id, referrer_id=None):
        """Register a new user, optionally linked to a referrer."""
        if user_id in self._users:
            print(f"User '{user_id}' is already registered.")
            return
        self._users[user_id] = {"revenue": 0.0, "referrer_id": referrer_id}
        print(f"User '{user_id}' registered (referred by: {referrer_id or 'none'}).")

        if referrer_id:
            if referrer_id not in self._referrers:
                self._referrers[referrer_id] = {"referrals": [], "total_earnings": 0.0}
            self._referrers[referrer_id]["referrals"].append(user_id)

    def generate_invite_link(self, referrer_id):
        """Generate a simulated invite link for the given referrer."""
        link = f"https://dreamcobots.io/invite?ref={referrer_id}"
        print(f"Invite link for '{referrer_id}': {link}")
        return link

    # ------------------------------------------------------------------
    # Revenue & earnings
    # ------------------------------------------------------------------

    def record_revenue(self, user_id, amount):
        """Record revenue for a user and update the referrer's earnings."""
        if user_id not in self._users:
            print(f"Unknown user '{user_id}'. Please register first.")
            return
        if amount <= 0:
            print("Revenue amount must be positive.")
            return

        self._users[user_id]["revenue"] += amount
        referrer_id = self._users[user_id]["referrer_id"]
        if referrer_id and referrer_id in self._referrers:
            commission = amount * self.commission_rate
            self._referrers[referrer_id]["total_earnings"] += commission
            print(
                f"Revenue ${amount:.2f} recorded for '{user_id}'. "
                f"'{referrer_id}' earns ${commission:.2f} commission."
            )
        else:
            print(f"Revenue ${amount:.2f} recorded for '{user_id}' (no referrer).")

    def get_referrer_dashboard(self, referrer_id):
        """Return dashboard data for a referrer."""
        if referrer_id not in self._referrers:
            return {"error": f"Referrer '{referrer_id}' not found."}
        data = self._referrers[referrer_id]
        referral_details = [
            {
                "user_id": uid,
                "revenue": self._users[uid]["revenue"],
                "commission_earned": self._users[uid]["revenue"] * self.commission_rate,
            }
            for uid in data["referrals"]
            if uid in self._users
        ]
        dashboard = {
            "referrer_id": referrer_id,
            "total_referrals": len(data["referrals"]),
            "total_earnings": round(data["total_earnings"], 2),
            "referrals": referral_details,
        }
        return dashboard

    # ------------------------------------------------------------------
    # Bot-to-bot: trigger Hustle Bot for underperformers
    # ------------------------------------------------------------------

    def identify_underperformers(self, referrer_id, revenue_threshold=100.0):
        """Return referrals whose revenue is below the given threshold."""
        if referrer_id not in self._referrers:
            return []
        underperformers = [
            uid
            for uid in self._referrers[referrer_id]["referrals"]
            if self._users.get(uid, {}).get("revenue", 0) < revenue_threshold
        ]
        return underperformers

    def notify_hustle_bot(self, hustle_bot, referrer_id, revenue_threshold=100.0):
        """
        Identify underperforming referrals and ask the Hustle Bot to run
        a motivational campaign for each of them.
        """
        underperformers = self.identify_underperformers(referrer_id, revenue_threshold)
        if not underperformers:
            print(f"No underperformers found for referrer '{referrer_id}'.")
            return
        print(
            f"Notifying Hustle Bot about {len(underperformers)} "
            f"underperformer(s) for referrer '{referrer_id}'."
        )
        for uid in underperformers:
            hustle_bot.run_motivational_campaign(uid)

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self):
        """Demo run showing core referral bot capabilities."""
        print("=== Referral Bot Demo ===")
        self.register_user("Alex")
        self.generate_invite_link("Alex")
        for friend in ["Casey", "Jordan", "Taylor"]:
            self.register_user(friend, referrer_id="Alex")
        self.record_revenue("Casey", 300)
        self.record_revenue("Jordan", 500)
        self.record_revenue("Taylor", 50)

        dashboard = self.get_referrer_dashboard("Alex")
        print("\n--- Alex's Referral Dashboard ---")
        print(json.dumps(dashboard, indent=2))
        return dashboard


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    bot = ReferralBot(config=config.get("referral_bot", {}))
    bot.run()
