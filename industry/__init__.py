"""Industry-specific AI modules for Dreamcobots platform."""

from .construction import ConstructionAI
from .healthcare_ai import HealthcareAI
from .real_estate import RealEstateAI

__all__ = ["HealthcareAI", "RealEstateAI", "ConstructionAI"]
