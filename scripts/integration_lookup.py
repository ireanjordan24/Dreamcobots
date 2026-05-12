import requests
import json
import sys

API_URL = "https://api.example-integration-platform.com/v1/search"
API_KEY = "YOUR_API_KEY"

def fetch_integration_opportunities(query):
    params = {"query": query, "api_key": API_KEY}
    response = requests.get(API_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return {}

def save_integration_results(query, data):
    with open("data/integration_lookup.json", "r+") as file:
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