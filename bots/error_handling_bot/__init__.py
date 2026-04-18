"""
DreamCo Error Handling Bot Package.

Exports the main ErrorHandlingBot class and its supporting types.
"""

from .error_handling_bot import (
    ErrorCategory,
    ErrorRecord,
    FixSuggestion,
    ErrorHandlingBot,
)

__all__ = [
    "ErrorCategory",
    "ErrorRecord",
    "FixSuggestion",
    "ErrorHandlingBot",
]
