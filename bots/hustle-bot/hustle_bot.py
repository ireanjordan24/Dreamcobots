# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py
# Hustle Bot

import json
import os
from datetime import datetime


MOTIVATIONAL_RESOURCES = [
    "Getting Started with Dreamcobots – Tutorial Series",
    "Top 10 Revenue Streams for Cobot Operators",
    "Community Success Stories: From Zero to $1k/Month",
    "How to Automate Your Workflow in 7 Days",
    "Building Your Personal Brand in the Dreamcobots Ecosystem",
]


class HustleBot:
    """
    Helps users set revenue goals, tracks milestones, delivers daily progress
    summaries, and runs motivational campaigns for underperformers.
    """

    def __init__(self, config=None):
        self.config = config or {}
        # { user_id: { "goal": float, "current_revenue": float, "tasks": [...] } }
        self._users = {}

    # ------------------------------------------------------------------
    # Goal & task management
    # ------------------------------------------------------------------

    def configure_goal(self, user_id, revenue_goal):
        """Set or update a user's revenue goal."""
        if revenue_goal <= 0:
            raise ValueError("Revenue goal must be positive.")
        if user_id not in self._users:
            self._users[user_id] = {
                "goal": revenue_goal,
                "current_revenue": 0.0,
                "tasks": [],
                "milestones": [],
                "campaigns_received": [],
            }
        else:
            self._users[user_id]["goal"] = revenue_goal
        print(f"Goal for '{user_id}' set to ${revenue_goal:.2f}.")

    def add_task(self, user_id, task_description):
        """Add a suggested task to the user's task list."""
        if user_id not in self._users:
            print(f"User '{user_id}' not configured. Call configure_goal first.")
            return
        self._users[user_id]["tasks"].append(
            {"description": task_description, "completed": False, "added_at": datetime.now().isoformat()}
        )
        print(f"Task added for '{user_id}': {task_description}")

    def complete_task(self, user_id, task_index):
        """Mark a task as completed."""
        if user_id not in self._users:
            print(f"Unknown user '{user_id}'.")
            return
        tasks = self._users[user_id]["tasks"]
        if task_index < 0 or task_index >= len(tasks):
            print(f"Invalid task index {task_index}.")
            return
        tasks[task_index]["completed"] = True
        print(f"Task {task_index} marked as completed for '{user_id}'.")

    # ------------------------------------------------------------------
    # Revenue tracking & milestones
    # ------------------------------------------------------------------

    def record_revenue(self, user_id, amount):
        """Record revenue for a user and check milestone achievements."""
        if user_id not in self._users:
            print(f"Unknown user '{user_id}'. Please configure a goal first.")
            return
        if amount <= 0:
            print("Revenue amount must be positive.")
            return
        self._users[user_id]["current_revenue"] += amount
        current = self._users[user_id]["current_revenue"]
        goal = self._users[user_id]["goal"]
        progress_pct = (current / goal) * 100
        print(f"Revenue for '{user_id}': ${current:.2f} / ${goal:.2f} ({progress_pct:.1f}%)")
        self._check_milestones(user_id)

    def _check_milestones(self, user_id):
        """Detect and log milestone crossings (25%, 50%, 75%, 100%)."""
        user = self._users[user_id]
        progress_pct = (user["current_revenue"] / user["goal"]) * 100
        for threshold in [25, 50, 75, 100]:
            label = f"{threshold}%"
            if progress_pct >= threshold and label not in user["milestones"]:
                user["milestones"].append(label)
                print(f"🎉 Milestone reached for '{user_id}': {label} of goal achieved!")

    # ------------------------------------------------------------------
    # Summaries & analytics
    # ------------------------------------------------------------------

    def get_daily_summary(self, user_id):
        """Return a daily progress summary for a user."""
        if user_id not in self._users:
            return {"error": f"User '{user_id}' not found."}
        user = self._users[user_id]
        completed_tasks = [t for t in user["tasks"] if t["completed"]]
        pending_tasks = [t for t in user["tasks"] if not t["completed"]]
        summary = {
            "user_id": user_id,
            "goal": user["goal"],
            "current_revenue": round(user["current_revenue"], 2),
            "progress_pct": round((user["current_revenue"] / user["goal"]) * 100, 1) if user["goal"] else 0,
            "milestones": user["milestones"],
            "completed_tasks": len(completed_tasks),
            "pending_tasks": len(pending_tasks),
        }
        return summary

    def suggest_tasks(self, user_id):
        """Suggest tasks based on current progress."""
        if user_id not in self._users:
            print(f"Unknown user '{user_id}'.")
            return []
        user = self._users[user_id]
        progress_pct = (user["current_revenue"] / user["goal"]) * 100 if user["goal"] else 0
        suggestions = []
        if progress_pct < 25:
            suggestions = [
                "Complete your profile and onboarding checklist",
                "Share your first referral link",
                "Join the community forum and introduce yourself",
            ]
        elif progress_pct < 50:
            suggestions = [
                "Reach out to 5 new potential referrals this week",
                "Attend a live Dreamcobots webinar",
            ]
        elif progress_pct < 75:
            suggestions = [
                "Optimize your referral outreach message",
                "Explore advanced automation features",
            ]
        else:
            suggestions = [
                "Scale your outreach to new communities",
                "Mentor a new user in the ecosystem",
            ]
        for s in suggestions:
            self.add_task(user_id, s)
        return suggestions

    def identify_untapped_markets(self):
        """Use analytics to surface potential growth markets."""
        markets = [
            {"name": "Small Business Owners", "potential_score": 9.2},
            {"name": "Freelance Developers", "potential_score": 8.7},
            {"name": "Community Managers", "potential_score": 7.5},
            {"name": "Content Creators", "potential_score": 8.0},
        ]
        print("=== Untapped Market Analysis ===")
        for m in sorted(markets, key=lambda x: x["potential_score"], reverse=True):
            print(f"  {m['name']}: score {m['potential_score']}/10")
        return markets

    # ------------------------------------------------------------------
    # Motivational campaigns (called by Referral Bot)
    # ------------------------------------------------------------------

    def run_motivational_campaign(self, user_id):
        """Deliver tailored motivational resources to a user."""
        if user_id not in self._users:
            # Register the user with a default goal so campaigns still work
            self.configure_goal(user_id, revenue_goal=500.0)
        resource = MOTIVATIONAL_RESOURCES[len(self._users[user_id]["campaigns_received"]) % len(MOTIVATIONAL_RESOURCES)]
        self._users[user_id]["campaigns_received"].append(resource)
        print(f"📣 Motivational campaign sent to '{user_id}': {resource}")
        return resource

    # ------------------------------------------------------------------
    # Run
    # ------------------------------------------------------------------

    def run(self):
        """Demo run showing core Hustle Bot capabilities."""
        print("=== Hustle Bot Demo ===")
        self.configure_goal("Jordan", revenue_goal=1000.0)
        self.suggest_tasks("Jordan")
        self.record_revenue("Jordan", 150)
        self.record_revenue("Jordan", 400)
        summary = self.get_daily_summary("Jordan")
        print("\n--- Jordan's Daily Summary ---")
        print(json.dumps(summary, indent=2))
        print()
        self.identify_untapped_markets()
        return summary


if __name__ == "__main__":
    config_path = os.path.join(os.path.dirname(__file__), "..", "config.json")
    config = {}
    if os.path.exists(config_path):
        with open(config_path) as f:
            config = json.load(f)
    bot = HustleBot(config=config.get("hustle_bot", {}))
    bot.run()
