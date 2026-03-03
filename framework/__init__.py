"""
DreamCObots Framework
=====================
Modular, scalable bot framework supporting occupational bots, app bots,
business bots, and side-hustle bots with NLP, emotional intelligence,
adaptive learning, dataset management, and built-in monetization.
"""

from .base_bot import BaseBot
from .nlp_engine import NLPEngine
from .adaptive_learning import AdaptiveLearning
from .dataset_manager import DatasetManager
from .monetization import MonetizationManager

__all__ = [
    "BaseBot",
    "NLPEngine",
    "AdaptiveLearning",
    "DatasetManager",
    "MonetizationManager",
]
