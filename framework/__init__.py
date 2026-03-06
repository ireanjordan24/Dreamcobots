"""
framework/__init__.py

Public API for the DreamCobots framework module.
"""

from framework.base_bot import BaseBot
from framework.nlp_engine import NLPEngine
from framework.adaptive_learning import AdaptiveLearning
from framework.dataset_manager import DatasetManager
from framework.monetization import MonetizationEngine

__all__ = [
    "BaseBot",
    "NLPEngine",
    "AdaptiveLearning",
    "DatasetManager",
    "MonetizationEngine",
]
