"""Working example demonstrating the HustleBot."""
import sys
import os
import importlib.util

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _ROOT)

_mod = importlib.util.spec_from_file_location(
    "hustle_bot",
    os.path.join(_ROOT, "bots", "hustle-bot", "hustle_bot.py")
)
_m = importlib.util.module_from_spec(_mod)
_mod.loader.exec_module(_m)
HustleBot = _m.HustleBot


def main():
    """Demonstrate the HustleBot features."""
    print("=" * 55)
    print("  DreamCobots HustleBot Example")
    print("  Revenue Goal Tracking & Optimization")
    print("=" * 55)

    bot = HustleBot()
    bot.start()
    print(f"\nBot: {bot.name} | Status: {bot._status}")

    print("\n[1] Setting revenue goals...")
    g1 = bot.set_goal("Hit $5K in freelance revenue", 5000.0)
    g2 = bot.set_goal("Launch digital product to $10K MRR", 10000.0)
    print(f"  ✓ Goal set: {g1['goal']} (target: ${g1['target_revenue']:,.0f})")
    print(f"  ✓ Goal set: {g2['goal']} (target: ${g2['target_revenue']:,.0f})")

    print("\n[2] Adding some revenue...")
    bot.add_revenue(1250.00)
    bot.add_revenue(875.50)
    print(f"  Current total revenue: ${bot.revenue:,.2f}")

    print("\n[3] Tracking progress...")
    progress = bot.track_progress()
    print(f"  Active goals: {progress['active_goals']}")
    for p in progress["progress"]:
        print(f"  '{p['goal']}': {p['percent_complete']}% complete (${p['remaining']:,.0f} remaining)")

    print("\n[4] Suggested tasks for today:")
    tasks = bot.suggest_tasks()
    for task in tasks[:3]:
        print(f"  • [{task['priority'].upper()}] {task['task']}")
        print(f"    Estimated value: {task['estimated_value']} | Time: {task['time_required']}")

    print("\n[5] Logging milestones...")
    m = bot.log_milestone("First $1,000 in revenue achieved!")
    print(f"  ✓ Milestone #{m['id']}: {m['milestone']}")

    print("\n[6] Revenue optimization...")
    optimizations = bot.optimize_revenue_streams()
    for tip in optimizations["optimization_tips"][:2]:
        print(f"  • {tip['stream']}: {tip['tip']} (+{tip['potential_increase']})")

    print("\n[7] Daily Summary:")
    summary = bot.generate_daily_summary()
    print(f"  Date: {summary['date']}")
    print(f"  Total revenue: ${summary['total_revenue']:,.2f}")
    print(f"  Active goals: {summary['active_goals']}")
    print(f"  Message: {summary['motivational_message']}")

    bot.stop()
    print(f"\n✅ HustleBot stopped. Revenue tracked: ${bot.revenue:,.2f}")
    print("=" * 55)


if __name__ == "__main__":
    main()
