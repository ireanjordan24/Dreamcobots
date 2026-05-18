import json
import os
import sys
from pathlib import Path

import requests

API_URL = os.getenv("INTEGRATION_LOOKUP_API_URL", "https://api.example-integration-platform.com/v1/search")
API_KEY = os.getenv("INTEGRATION_LOOKUP_API_KEY", "YOUR_API_KEY")
OUTPUT_PATH = Path("data/integration_lookup.json")

def fetch_integration_opportunities(query):
    if API_KEY == "YOUR_API_KEY":
        print("Integration lookup API key is not configured; skipping remote lookup.")
        return {}

    params = {"query": query, "api_key": API_KEY}
    try:
        response = requests.get(API_URL, params=params, timeout=15)
    except requests.RequestException as exc:
        print(f"Integration lookup request failed: {exc}")
        return {}

    if response.status_code == 200:
        return response.json()

    print(f"Error: {response.status_code} - {response.text}")
    return {}

def save_integration_results(query, data):
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.touch(exist_ok=True)
    with OUTPUT_PATH.open("r+", encoding="utf-8") as file:
        try:
            existing_data = json.load(file)
        except json.JSONDecodeError:
            existing_data = {}

        existing_data[query] = data

        file.seek(0)
        json.dump(existing_data, file, indent=4)
        file.truncate()

if __name__ == "__main__":
    query = sys.argv[1]
    print(f"Fetching integration opportunities for: {query}")
    results = fetch_integration_opportunities(query)
    if results:
        save_integration_results(query, results)
        print(f"Integration opportunities saved for {query}")
    else:
        print("No results found.")
