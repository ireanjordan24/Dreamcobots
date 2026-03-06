"""
Pytest configuration and shared fixtures for the Dreamcobots test suite.
Conversational data is pre-loaded once per session to optimize runtime.
"""
import json
import os

import pytest

_CONVERSATIONAL_DATA_PATH = os.path.join(
    os.path.dirname(__file__), "fixtures", "conversational_data.json"
)


@pytest.fixture(scope="session")
def conversational_data():
    """Pre-load frequently used conversational data for all bot tests."""
    with open(_CONVERSATIONAL_DATA_PATH) as fh:
        data = json.load(fh)
    return data
