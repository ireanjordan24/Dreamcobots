"""
Dreamcobots Framework.

Exports the GLOBAL AI SOURCES FLOW pipeline and the modular bot framework
components (NLP, adaptive learning, dataset management, monetisation).
"""

# Global AI Sources Flow pipeline (original framework)
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

# Modular framework components (from PR #15)
from .base_bot import BaseBot
from .nlp_engine import NLPEngine
from .adaptive_learning import AdaptiveLearning
from .dataset_manager import DatasetManager
from .monetization import MonetizationManager

__all__ = [
    # Global AI Sources Flow
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
    # Modular framework components
    "BaseBot",
    "NLPEngine",
    "AdaptiveLearning",
    "DatasetManager",
    "MonetizationManager",
]
