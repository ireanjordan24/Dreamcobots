"""Working example demonstrating the ReferralBot."""
import sys
import os
import importlib.util

_ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, _ROOT)

_mod = importlib.util.spec_from_file_location(
    "referral_bot",
    os.path.join(_ROOT, "bots", "referral-bot", "referral_bot.py")
)
_m = importlib.util.module_from_spec(_mod)
_mod.loader.exec_module(_m)
ReferralBot = _m.ReferralBot


def main():
    """Demonstrate the ReferralBot features."""
    print("=" * 50)
    print("  DreamCobots ReferralBot Example")
    print("  50% Revenue Share Program")
    print("=" * 50)

    bot = ReferralBot()
    bot.start()
    print(f"\nBot Status: {bot._status}")

    print("\n[1] Registering referrers...")
    alice = bot.add_referrer("alice001", "Alice Johnson")
    bob = bot.add_referrer("bob002", "Bob Smith")
    print(f"  ✓ {alice['name']} registered: {alice['link']}")
    print(f"  ✓ {bob['name']} registered: {bob['link']}")

    print("\n[2] Tracking referrals...")
    for i in range(5):
        ref = bot.track_referral("alice001", f"new_user_{i:03d}")
        print(f"  ✓ Referral tracked: alice001 -> new_user_{i:03d}")

    bot.track_referral("bob002", "new_user_100")

    print("\n[3] Calculating earnings...")
    earnings = bot.calculate_earnings("alice001")
    print(f"  Alice's referrals: {earnings['total_referrals']}")
    print(f"  Pending earnings: ${earnings['pending_earnings']}")
    print(f"  Commission rate: {earnings['commission_rate']}")

    print("\n[4] Leaderboard:")
    leaderboard = bot.get_leaderboard()
    for entry in leaderboard[:3]:
        print(f"  #{entry['rank']} {entry['name']}: {entry['referral_count']} referrals | Tier: {entry['tier']}")

    print("\n[5] Overall stats:")
    stats = bot.get_referral_stats()
    print(f"  Total referrers: {stats['total_referrers']}")
    print(f"  Total referrals: {stats['total_referrals']}")
    print(f"  Program: {stats['program_name']}")

    bot.stop()
    print(f"\n✅ Bot stopped. Final status: {bot._status}")
    print("=" * 50)


if __name__ == "__main__":
    main()
