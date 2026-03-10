# BuddyAI – Central AI connector for all Dreamcobots category bots
# Connects OOH Major Occupational Group bots, Mobile App Category bots,
# and Business Category / Industry Classification bots to the Buddy system.

import sys, os

# Ensure all bot directories are on the path
_BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
for _d in ('Occupational_bots', 'App_bots', 'Business_bots',
           os.path.join('bots', 'government-contract-grant-bot')):
    _p = os.path.join(_BASE, _d)
    if _p not in sys.path:
        sys.path.insert(0, _p)

# ── Government Contract & Grant Bot ──────────────────────────────────────
from government_contract_grant_bot import GovernmentContractGrantBot

# ── OOH Occupational Group bots ──────────────────────────────────────────
from administrative_support_bot import AdministrativeSupportBot
from architecture_engineering_bot import ArchitectureEngineeringBot
from arts_media_bot import ArtsMediaBot
from building_maintenance_bot import BuildingMaintenanceBot
from business_financial_bot import BusinessFinancialBot
from community_service_bot import CommunityServiceBot
from computer_math_bot import ComputerMathBot
from construction_extraction_bot import ConstructionExtractionBot
from education_library_bot import EducationLibraryBot
from farming_fishing_forestry_bot import FarmingFishingForestryBot
from food_service_bot import FoodServiceBot
from healthcare_practitioner_bot import HealthcarePractitionerBot
from healthcare_support_bot import HealthcareSupportBot
from installation_maintenance_bot import InstallationMaintenanceBot
from legal_bot import LegalBot
from management_bot import ManagementBot
from military_bot import MilitaryBot
from personal_care_bot import PersonalCareBot
from production_bot import ProductionBot
from protective_service_bot import ProtectiveServiceBot
from sales_bot import SalesBot
from science_bot import ScienceBot
from transportation_bot import TransportationBot

# ── Mobile App Category bots ─────────────────────────────────────────────
from books_app_bot import BooksAppBot
from business_app_bot import BusinessAppBot
from education_app_bot import EducationAppBot
from entertainment_app_bot import EntertainmentAppBot
from finance_app_bot import FinanceAppBot
from food_drink_app_bot import FoodDrinkAppBot
from games_app_bot import GamesAppBot
from health_fitness_app_bot import HealthFitnessAppBot
from kids_family_app_bot import KidsFamilyAppBot
from lifestyle_app_bot import LifestyleAppBot
from medical_app_bot import MedicalAppBot
from music_app_bot import MusicAppBot
from navigation_app_bot import NavigationAppBot
from news_app_bot import NewsAppBot
from photo_video_app_bot import PhotoVideoAppBot
from productivity_app_bot import ProductivityAppBot
from reference_app_bot import ReferenceAppBot
from shopping_app_bot import ShoppingAppBot
from social_networking_app_bot import SocialNetworkingAppBot
from sports_app_bot import SportsAppBot
from travel_app_bot import TravelAppBot
from utilities_app_bot import UtilitiesAppBot
from weather_app_bot import WeatherAppBot

# ── Business Category / Industry Classification bots ─────────────────────
from accommodation_food_bot import AccommodationFoodBot
from administrative_support_industry_bot import AdministrativeSupportIndustryBot
from agriculture_bot import AgricultureBot
from arts_entertainment_bot import ArtsEntertainmentBot
from construction_bot import ConstructionBot
from educational_services_bot import EducationalServicesBot
from finance_insurance_bot import FinanceInsuranceBot
from health_care_bot import HealthCareBot
from information_bot import InformationBot
from management_companies_bot import ManagementCompaniesBot
from manufacturing_bot import ManufacturingBot
from mining_bot import MiningBot
from other_services_bot import OtherServicesBot
from professional_services_bot import ProfessionalServicesBot
from public_administration_bot import PublicAdministrationBot
from real_estate_leasing_bot import RealEstateLeasingBot
from retail_trade_bot import RetailTradeBot
from transportation_warehousing_bot import TransportationWarehousingBot
from utilities_bot import UtilitiesBot
from wholesale_trade_bot import WholesaleTradeBot


class Buddy:
    """Central AI that manages and routes messages to all category bots.

    Usage::

        buddy = Buddy()
        buddy.start_all()
        buddy.route('ManagementBot', 'run')
    """

    def __init__(self):
        self.bots = {}
        self._register_all()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def _register_all(self):
        """Instantiate and register every bot, connecting each back to Buddy."""
        all_bot_instances = [
            GovernmentContractGrantBot(),
        AdministrativeSupportBot(),
        ArchitectureEngineeringBot(),
        ArtsMediaBot(),
        BuildingMaintenanceBot(),
        BusinessFinancialBot(),
        CommunityServiceBot(),
        ComputerMathBot(),
        ConstructionExtractionBot(),
        EducationLibraryBot(),
        FarmingFishingForestryBot(),
        FoodServiceBot(),
        HealthcarePractitionerBot(),
        HealthcareSupportBot(),
        InstallationMaintenanceBot(),
        LegalBot(),
        ManagementBot(),
        MilitaryBot(),
        PersonalCareBot(),
        ProductionBot(),
        ProtectiveServiceBot(),
        SalesBot(),
        ScienceBot(),
        TransportationBot(),
        BooksAppBot(),
        BusinessAppBot(),
        EducationAppBot(),
        EntertainmentAppBot(),
        FinanceAppBot(),
        FoodDrinkAppBot(),
        GamesAppBot(),
        HealthFitnessAppBot(),
        KidsFamilyAppBot(),
        LifestyleAppBot(),
        MedicalAppBot(),
        MusicAppBot(),
        NavigationAppBot(),
        NewsAppBot(),
        PhotoVideoAppBot(),
        ProductivityAppBot(),
        ReferenceAppBot(),
        ShoppingAppBot(),
        SocialNetworkingAppBot(),
        SportsAppBot(),
        TravelAppBot(),
        UtilitiesAppBot(),
        WeatherAppBot(),
        AccommodationFoodBot(),
        AdministrativeSupportIndustryBot(),
        AgricultureBot(),
        ArtsEntertainmentBot(),
        ConstructionBot(),
        EducationalServicesBot(),
        FinanceInsuranceBot(),
        HealthCareBot(),
        InformationBot(),
        ManagementCompaniesBot(),
        ManufacturingBot(),
        MiningBot(),
        OtherServicesBot(),
        ProfessionalServicesBot(),
        PublicAdministrationBot(),
        RealEstateLeasingBot(),
        RetailTradeBot(),
        TransportationWarehousingBot(),
        UtilitiesBot(),
        WholesaleTradeBot(),
        ]
        for bot in all_bot_instances:
            bot.connect_to_buddy(self)
            self.bots[bot.name] = bot

    def register(self, bot):
        """Manually register an additional bot instance."""
        bot.connect_to_buddy(self)
        self.bots[bot.name] = bot

    # ------------------------------------------------------------------
    # Communication
    # ------------------------------------------------------------------

    def receive(self, bot_name: str, message: str):
        """Receive a message from a bot and log it."""
        print(f'[Buddy] Received from {bot_name}: {message}')
        return message

    def route(self, bot_name: str, method: str, *args, **kwargs):
        """Call a named method on a registered bot."""
        bot = self.bots.get(bot_name)
        if bot is None:
            raise KeyError(f'Bot not found: {bot_name}')
        fn = getattr(bot, method, None)
        if fn is None:
            raise AttributeError(f'{bot_name} has no method: {method}')
        return fn(*args, **kwargs)

    def broadcast(self, method: str, *args, **kwargs):
        """Call the same method on every registered bot."""
        return {name: getattr(bot, method)(*args, **kwargs)
                for name, bot in self.bots.items()
                if hasattr(bot, method)}

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start_all(self):
        """Start every registered bot."""
        for bot in self.bots.values():
            bot.start()

    def run_all(self):
        """Run every registered bot."""
        for bot in self.bots.values():
            bot.run()

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_bots(self):
        """Return the names of all registered bots."""
        return list(self.bots.keys())

    def capabilities_report(self):
        """Print a capabilities summary for every registered bot."""
        for bot in self.bots.values():
            try:
                summary = bot.capabilities_summary()
            except AttributeError:
                summary = {'bot': bot.name, 'note': 'no capabilities_summary method'}
            print(summary)


if __name__ == '__main__':
    buddy = Buddy()
    print(f'Buddy managing {len(buddy.list_bots())} bots:')
    buddy.capabilities_report()