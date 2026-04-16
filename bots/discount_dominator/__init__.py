"""
Discount Dominator package.

Exposes the primary public API for settings 401–600 and the three
interoperability domain modules.
"""

from .analytics import AdvancedAnalytics
from .behavioral_settings import BehavioralSettings
from .car_flipping_bot import CarFlippingBot
from .discount_dominator import DiscountDominator
from .enterprise_features import EnterpriseFeatures
from .in_store_controls import InStoreTacticalControls
from .online_optimization import OnlinePlatformOptimization
from .real_estate_optimizer import RealEstateOptimizer
from .retail_intelligence import RetailIntelligenceNetwork
from .settings import (
    ALL_GROUPS,
    DISCOUNT_DOMINATOR_SETTINGS,
    GROUP_ANALYTICS,
    GROUP_BEHAVIORAL,
    GROUP_ENTERPRISE,
    GROUP_INSTORE,
    GROUP_ONLINE,
    SETTINGS_BY_GROUP,
    Setting,
    apply_settings,
    as_dict,
    get_group_settings,
    get_setting,
    reset_all,
)

__all__ = [
    # Settings
    "Setting",
    "DISCOUNT_DOMINATOR_SETTINGS",
    "SETTINGS_BY_GROUP",
    "ALL_GROUPS",
    "GROUP_ANALYTICS",
    "GROUP_INSTORE",
    "GROUP_ONLINE",
    "GROUP_ENTERPRISE",
    "GROUP_BEHAVIORAL",
    "get_setting",
    "apply_settings",
    "get_group_settings",
    "reset_all",
    "as_dict",
    # Module facades
    "AdvancedAnalytics",
    "InStoreTacticalControls",
    "OnlinePlatformOptimization",
    "EnterpriseFeatures",
    "BehavioralSettings",
    # Domain interoperability
    "RealEstateOptimizer",
    "CarFlippingBot",
    "RetailIntelligenceNetwork",
    # Main bot
    "DiscountDominator",
]
