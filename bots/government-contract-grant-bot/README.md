# Government Contract & Grant Bot

The Government Contract & Grant Bot searches government databases (SAM.gov, Grants.gov) for contract and grant opportunities that match your configured keywords and NAICS codes. It filters results and optionally sends a notification email with a summary of new opportunities.

---

## Features

- **Contract search** – Queries SAM.gov (or equivalent) for open contract opportunities.
- **Grant search** – Queries Grants.gov (or equivalent) for open grant opportunities.
- **NAICS code filtering** – Narrows results to industry codes you care about.
- **Email notification** – Sends a summary of discovered opportunities to a configured email address.

---

## Setup

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone https://github.com/ireanjordan24/Dreamcobots.git
   cd Dreamcobots
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot** – Edit `bots/government-contract-grant-bot/config.json`:
   ```json
   {
     "api_key": "YOUR_API_KEY_HERE",
     "search_keywords": ["IT services", "cybersecurity", "consulting"],
     "naics_codes": ["541512", "541519", "541611"],
     "max_results": 10,
     "notify_email": "your-email@example.com",
     "sources": ["SAM.gov", "Grants.gov"]
   }
   ```

   | Field             | Description                                                                 |
   |-------------------|-----------------------------------------------------------------------------|
   | `api_key`         | Your API key for SAM.gov or another contract/grant data provider.           |
   | `search_keywords` | List of keywords to search for in contract and grant titles/descriptions.   |
   | `naics_codes`     | NAICS industry codes used to filter results to relevant sectors.            |
   | `max_results`     | Maximum number of results to return per source.                             |
   | `notify_email`    | Email address to receive opportunity summaries. Leave empty to skip.        |
   | `sources`         | List of data sources to query (e.g., `"SAM.gov"`, `"Grants.gov"`).         |

---

## Usage

Navigate to the bot directory and run the script:

```bash
cd bots/government-contract-grant-bot
python government_contract_grant_bot.py
```

### Example output

```
Government Contract & Grant Bot is starting...
  Sources:  SAM.gov, Grants.gov
  Keywords: IT services, cybersecurity, consulting
  NAICS codes: 541512, 541519, 541611
  Max results per source: 10

Searching for government contracts...
  Found 3 contract opportunity(ies).

Searching for government grants...
  Found 3 grant opportunity(ies).

--- Contract Opportunities ---
  1. [SAM.gov] Contract opportunity for: IT services
     NAICS: 541512 | Deadline: 2026-06-01
     URL: https://sam.gov/search/
  ...

--- Grant Opportunities ---
  1. [Grants.gov] Grant opportunity for: IT services
     Agency: Department of Commerce | Deadline: 2026-07-15
     URL: https://www.grants.gov/search-grants
  ...

Notification: Sending summary of 6 opportunity(ies) to your-email@example.com...
  Notification sent (stub).

Government Contract & Grant Bot finished.
```

---

## Integrating a Real API

The bot currently uses stub implementations. To connect to a live data source:

- **SAM.gov**: Register for a free API key at <https://sam.gov/> and replace the stub in `search_contracts()` with a call to:
  `GET https://api.sam.gov/opportunities/v2/search?api_key=<KEY>&q=<keyword>`
- **Grants.gov**: Use the Grants.gov Search API at <https://www.grants.gov/> and replace the stub in `search_grants()`.
- **Email notifications**: Integrate an email provider (SendGrid, SMTP) inside the `notify()` method.

---

## Project Structure

```
bots/government-contract-grant-bot/
├── government_contract_grant_bot.py   # Main bot logic
├── config.json                        # Configuration file (API keys, keywords, etc.)
└── README.md                          # This file
```
