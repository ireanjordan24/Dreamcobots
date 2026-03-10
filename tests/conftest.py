"""Pytest configuration and shared fixtures."""
import json
import os
import sys

# Ensure the repo root is on the Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


import pytest


@pytest.fixture
def conversational_data():
    """Load shared conversational test data from fixtures."""
    fixtures_path = os.path.join(os.path.dirname(__file__), "fixtures", "conversational_data.json")
    with open(fixtures_path, encoding="utf-8") as f:
        return json.load(f)
