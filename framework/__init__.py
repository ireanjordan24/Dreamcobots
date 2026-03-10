"""
Dreamcobots GLOBAL AI SOURCES FLOW Framework.

Import the main pipeline class from this package:

    from framework import GlobalAISourcesFlow

Also exports the bot framework classes:

    from framework import BaseBot, DatasetManager
"""

from .global_ai_sources_flow import (
    GlobalAISourcesFlow,
    DataIngestionLayer,
    LearningMethodClassifier,
    SandboxTestLab,
    PerformanceAnalytics,
    HybridEvolutionEngine,
    DeploymentEngine,
    ProfitMarketIntelligence,
    GovernanceSecurityLayer,
    FrameworkViolationError,
    FRAMEWORK_VERSION,
    REQUIRED_STAGES,
)
from .base_bot import BaseBot
from .dataset_manager import DatasetManager
from .nlp_engine import NLPEngine
from .adaptive_learning import AdaptiveLearning
from .monetization import MonetizationManager

__all__ = [
    "GlobalAISourcesFlow",
    "DataIngestionLayer",
    "LearningMethodClassifier",
    "SandboxTestLab",
    "PerformanceAnalytics",
    "HybridEvolutionEngine",
    "DeploymentEngine",
    "ProfitMarketIntelligence",
    "GovernanceSecurityLayer",
    "FrameworkViolationError",
    "FRAMEWORK_VERSION",
    "REQUIRED_STAGES",
    "BaseBot",
    "DatasetManager",
    "NLPEngine",
    "AdaptiveLearning",
    "MonetizationManager",
]
