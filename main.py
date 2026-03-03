"""
DreamCobots - Master Entry Point
Starts the orchestrator and dashboard for the full bot ecosystem.
"""
import sys
import os
import threading
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from colorama import init as colorama_init, Fore, Style

colorama_init(autoreset=True)


def print_banner():
    """Print the DreamCobots ASCII banner."""
    banner = f"""
{Fore.CYAN}
  ____                          ____       _           _
 |  _ \\ _ __ ___  __ _ _ __ __|  _ \\ ___ | |__   ___ | |_ ___
 | | | | '__/ _ \\/ _` | '_ ` _ \\ |_) / _ \\| '_ \\ / _ \\| __/ __|
 | |_| | | |  __/ (_| | | | | | |  _ < (_) | |_) | (_) | |_\\__ \\
 |____/|_|  \\___|\\__,_|_| |_| |_|_| \\_\\___/|_.__/ \\___/ \\__|___/

{Fore.YELLOW}           AI-Powered Business Bot Ecosystem  v2.0.0
{Fore.GREEN}        50% Revenue Share | 15 Specialized Bots | Live Dashboard
{Style.RESET_ALL}
"""
    print(banner)


def register_all_bots(orchestrator):
    """Register all available bots with the orchestrator."""
    import importlib.util

    bot_modules = [
        ("government-contract-grant-bot", "government_contract_grant_bot.py", "GovernmentContractGrantBot"),
        ("hustle-bot", "hustle_bot.py", "HustleBot"),
        ("referral-bot", "referral_bot.py", "ReferralBot"),
        ("buddy-bot", "buddy_bot.py", "BuddyBot"),
        ("entrepreneur-bot", "entrepreneur_bot.py", "EntrepreneurBot"),
        ("medical-bot", "medical_bot.py", "MedicalBot"),
        ("legal-bot", "legal_bot.py", "LegalBot"),
        ("finance-bot", "finance_bot.py", "FinanceBot"),
        ("real-estate-bot", "real_estate_bot.py", "RealEstateBot"),
        ("ecommerce-bot", "ecommerce_bot.py", "EcommerceBot"),
        ("marketing-bot", "marketing_bot.py", "MarketingBot"),
        ("education-bot", "education_bot.py", "EducationBot"),
        ("cybersecurity-bot", "cybersecurity_bot.py", "CybersecurityBot"),
        ("hr-bot", "hr_bot.py", "HRBot"),
        ("farewell-bot", "farewell_bot.py", "FarewellBot"),
    ]

    root = os.path.dirname(os.path.abspath(__file__))
    for bot_dir, module_file, class_name in bot_modules:
        try:
            path = os.path.join(root, "bots", bot_dir, module_file)
            spec = importlib.util.spec_from_file_location(bot_dir.replace("-", "_"), path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            bot_class = getattr(module, class_name)
            bot_instance = bot_class()
            orchestrator.register_bot(bot_dir, bot_instance)
            print(f"{Fore.GREEN}  ✓ Registered: {bot_dir}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}  ✗ Failed to register {bot_dir}: {e}{Style.RESET_ALL}")


def start_dashboard(orchestrator):
    """Start the Flask dashboard in a background thread."""
    try:
        from dashboard.app import create_app
        app = create_app(orchestrator)

        def run_flask():
            """Run Flask server."""
            app.run(host="0.0.0.0", port=8080, debug=False, use_reloader=False)

        dashboard_thread = threading.Thread(target=run_flask, daemon=True)
        dashboard_thread.start()
        print(f"{Fore.CYAN}  ✓ Dashboard running at http://0.0.0.0:8080{Style.RESET_ALL}")
        return dashboard_thread
    except Exception as e:
        print(f"{Fore.RED}  ✗ Dashboard failed to start: {e}{Style.RESET_ALL}")
        return None


def main():
    """Main entry point for DreamCobots platform."""
    print_banner()

    print(f"{Fore.YELLOW}[1/4] Loading configuration...{Style.RESET_ALL}")
    from core.config_loader import config
    print(f"  Platform: {config.get('platform', 'DreamCobots')}")
    print(f"  Version: {config.get('version', '2.0.0')}")

    print(f"\n{Fore.YELLOW}[2/4] Initializing orchestrator...{Style.RESET_ALL}")
    from core.orchestrator import Orchestrator
    orchestrator = Orchestrator()

    print(f"\n{Fore.YELLOW}[3/4] Registering bots...{Style.RESET_ALL}")
    register_all_bots(orchestrator)

    print(f"\n{Fore.YELLOW}[4/4] Starting dashboard...{Style.RESET_ALL}")
    start_dashboard(orchestrator)

    print(f"\n{Fore.GREEN}{'='*60}")
    print(f"  DreamCobots Platform is LIVE!")
    print(f"  Dashboard: http://0.0.0.0:8080")
    print(f"  Bots registered: {len(orchestrator.get_all_statuses())}")
    print(f"{'='*60}{Style.RESET_ALL}\n")

    try:
        while True:
            time.sleep(60)
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Shutting down DreamCobots...{Style.RESET_ALL}")
        sys.exit(0)


if __name__ == "__main__":
    main()
