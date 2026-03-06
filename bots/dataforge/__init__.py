"""
bots/dataforge/__init__.py

DataForge AI Bot module for DreamCobots.

Exports the four primary public interfaces:
  - DataForgeBot       – main orchestration bot
  - ComplianceManager  – GDPR / CCPA / HIPAA validation
  - UserMarketplace    – data-selling cooperative
  - SalesChannelManager – multi-channel dataset publishing
"""

from bots.dataforge.dataforge_bot import DataForgeBot
from bots.dataforge.compliance import ComplianceManager
from bots.dataforge.user_marketplace import UserMarketplace
from bots.dataforge.sales_channels import SalesChannelManager

__all__ = [
    "DataForgeBot",
    "ComplianceManager",
    "UserMarketplace",
    "SalesChannelManager",
]
