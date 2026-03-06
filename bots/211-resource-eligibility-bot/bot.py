"""
211 Resource Eligibility Bot
Helps users find local social services and check eligibility for assistance programs.
"""

import os


RESOURCE_DATA = {
    "food": [
        {
            "name": "Community Food Bank",
            "category": "food",
            "description": "Free groceries and meals for income-qualifying families.",
            "phone": "1-800-555-0101",
            "website": "https://example-foodbank.org",
            "eligibility": {"max_income_percent_fpl": 185},
        },
        {
            "name": "SNAP Benefits (Food Stamps)",
            "category": "food",
            "description": "Federal nutrition assistance program.",
            "phone": "1-800-221-5689",
            "website": "https://www.fns.usda.gov/snap",
            "eligibility": {"max_income_percent_fpl": 130},
        },
    ],
    "housing": [
        {
            "name": "Emergency Rental Assistance",
            "category": "housing",
            "description": "One-time rent or utility payment to prevent eviction.",
            "phone": "1-800-555-0202",
            "website": "https://example-housing.org",
            "eligibility": {"max_income_percent_fpl": 80},
        },
        {
            "name": "Section 8 Housing Voucher",
            "category": "housing",
            "description": "Federal housing choice voucher program.",
            "phone": "1-800-955-2232",
            "website": "https://www.hud.gov",
            "eligibility": {"max_income_percent_fpl": 50},
        },
    ],
    "health": [
        {
            "name": "Medicaid",
            "category": "health",
            "description": "Free or low-cost health coverage for eligible adults and children.",
            "phone": "1-800-318-2596",
            "website": "https://www.medicaid.gov",
            "eligibility": {"max_income_percent_fpl": 138},
        },
        {
            "name": "Community Health Clinic",
            "category": "health",
            "description": "Low-cost medical, dental, and mental health services.",
            "phone": "1-800-555-0303",
            "website": "https://example-clinic.org",
            "eligibility": {"max_income_percent_fpl": 200},
        },
    ],
    "utility": [
        {
            "name": "LIHEAP Energy Assistance",
            "category": "utility",
            "description": "Help with heating and cooling energy costs.",
            "phone": "1-866-674-6327",
            "website": "https://www.acf.hhs.gov/ocs/programs/liheap",
            "eligibility": {"max_income_percent_fpl": 150},
        },
    ],
    "childcare": [
        {
            "name": "Child Care Subsidy Program",
            "category": "childcare",
            "description": "Subsidized childcare for working low-income families.",
            "phone": "1-800-555-0404",
            "website": "https://example-childcare.org",
            "eligibility": {"max_income_percent_fpl": 85},
        },
    ],
}

# Federal Poverty Level (FPL) 2024 guidelines (annual income) by family size
FPL_2024 = {
    1: 15060,
    2: 20440,
    3: 25820,
    4: 31200,
    5: 36580,
    6: 41960,
    7: 47340,
    8: 52720,
}


class ResourceEligibilityBot:
    """
    211 Resource Eligibility Bot — helps users find local social services
    and determine which assistance programs they qualify for.
    """

    def __init__(self, config=None):
        """
        Initialize the bot with an optional configuration dictionary.

        Args:
            config (dict, optional): Configuration overrides. Supports keys:
                - 'default_location' (str): Default city/state for searches.
                - 'max_results' (int): Maximum resources to return per query.
        """
        self.config = config or {}
        self.default_location = self.config.get("default_location", "your area")
        self.max_results = self.config.get("max_results", 10)
        print("[211 Bot] Initialized. Ready to help find resources.")

    def check_eligibility(self, user_profile):
        """
        Check which programs the user may qualify for based on their profile.

        Args:
            user_profile (dict): Must include:
                - 'annual_income' (float): Household annual income in USD.
                - 'family_size' (int): Number of people in the household.
                - 'location' (str): City and state (e.g., 'Austin, TX').

        Returns:
            dict: {
                'eligible_programs': list of program dicts,
                'income_percent_fpl': float,
                'summary': str
            }
        """
        income = float(user_profile.get("annual_income", 0))
        family_size = int(user_profile.get("family_size", 1))
        location = user_profile.get("location", self.default_location)

        fpl_base = FPL_2024.get(min(family_size, 8), FPL_2024[8])
        income_percent_fpl = (income / fpl_base) * 100 if fpl_base else 0

        eligible_programs = []
        for category, resources in RESOURCE_DATA.items():
            for resource in resources:
                threshold = resource.get("eligibility", {}).get("max_income_percent_fpl", 999)
                if income_percent_fpl <= threshold:
                    eligible_programs.append({**resource, "location": location})

        summary = (
            f"Based on an annual income of ${income:,.0f} for a family of {family_size} "
            f"in {location}, you are at {income_percent_fpl:.1f}% of the Federal Poverty Level. "
            f"You may qualify for {len(eligible_programs)} program(s)."
        )

        return {
            "eligible_programs": eligible_programs,
            "income_percent_fpl": round(income_percent_fpl, 1),
            "summary": summary,
        }

    def find_resources(self, location, category=None):
        """
        Find available resources by location and optional category.

        Args:
            location (str): City and state to search in.
            category (str, optional): Filter by category. One of:
                food, housing, health, utility, childcare.
                If None, all categories are returned.

        Returns:
            list[dict]: List of resource dictionaries.
        """
        categories = self.get_resource_categories()

        if category and category.lower() not in categories:
            print(f"[211 Bot] Unknown category '{category}'. Valid: {categories}")
            return []

        results = []
        search_categories = [category.lower()] if category else categories
        for cat in search_categories:
            for resource in RESOURCE_DATA.get(cat, []):
                results.append({**resource, "location": location})
                if len(results) >= self.max_results:
                    break

        print(f"[211 Bot] Found {len(results)} resource(s) in '{location}'.")
        return results

    def get_resource_categories(self):
        """
        Return the list of available resource categories.

        Returns:
            list[str]: Category names.
        """
        return list(RESOURCE_DATA.keys())

    def format_resource_list(self, resources):
        """
        Format a list of resources as a human-readable string.

        Args:
            resources (list[dict]): Resource dicts as returned by find_resources().

        Returns:
            str: Formatted multi-line string.
        """
        if not resources:
            return "No resources found."

        lines = []
        for i, r in enumerate(resources, 1):
            lines.append(
                f"{i}. [{r['category'].upper()}] {r['name']}\n"
                f"   {r['description']}\n"
                f"   Phone : {r.get('phone', 'N/A')}\n"
                f"   Website: {r.get('website', 'N/A')}\n"
            )
        return "\n".join(lines)

    def run(self):
        """
        Interactive CLI loop for the 211 Resource Eligibility Bot.
        Guides the user through eligibility checking and resource searching.
        """
        print("\n" + "=" * 60)
        print("  211 Resource & Eligibility Bot — DreamCobots")
        print("=" * 60)
        print("Type 'quit' at any prompt to exit.\n")

        while True:
            print("\nOptions:")
            print("  1) Check my eligibility for programs")
            print("  2) Find resources in my area")
            print("  3) List resource categories")
            print("  4) Quit")
            choice = input("\nSelect an option (1-4): ").strip()

            if choice == "1":
                try:
                    income = input("  Annual household income (USD): ").strip()
                    if income.lower() == "quit":
                        break
                    family_size = input("  Family / household size: ").strip()
                    if family_size.lower() == "quit":
                        break
                    location = input("  Your city and state (e.g. Austin, TX): ").strip()
                    if location.lower() == "quit":
                        break

                    result = self.check_eligibility(
                        {"annual_income": float(income), "family_size": int(family_size), "location": location}
                    )
                    print(f"\n{result['summary']}")
                    print(self.format_resource_list(result["eligible_programs"]))
                except ValueError:
                    print("[211 Bot] Invalid input. Please enter numeric values for income and family size.")

            elif choice == "2":
                location = input("  Enter your city and state: ").strip()
                if location.lower() == "quit":
                    break
                cat = input(f"  Category (or press Enter for all) [{', '.join(self.get_resource_categories())}]: ").strip()
                resources = self.find_resources(location, category=cat if cat else None)
                print(self.format_resource_list(resources))

            elif choice == "3":
                cats = self.get_resource_categories()
                print(f"\nAvailable categories: {', '.join(cats)}")

            elif choice == "4" or choice.lower() == "quit":
                print("[211 Bot] Goodbye! Dial 2-1-1 anytime for live local help.")
                break
            else:
                print("[211 Bot] Invalid option. Please choose 1–4.")


if __name__ == "__main__":
    bot = ResourceEligibilityBot()
    bot.run()
