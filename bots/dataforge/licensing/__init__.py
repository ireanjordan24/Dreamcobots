"""
bots/dataforge/licensing/__init__.py

Exports the licensing, consent, and anonymization classes.
"""

from bots.dataforge.licensing.license_generator import LicenseGenerator
from bots.dataforge.licensing.consent_manager import ConsentManager
from bots.dataforge.licensing.anonymizer import DataAnonymizer

__all__ = [
    "LicenseGenerator",
    "ConsentManager",
    "DataAnonymizer",
]
