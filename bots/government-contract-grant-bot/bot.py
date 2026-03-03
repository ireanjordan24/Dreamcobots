"""Entry point for the government-contract-grant-bot."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from government_contract_grant_bot import GovernmentContractGrantBot

if __name__ == "__main__":
    bot = GovernmentContractGrantBot()
    bot.run()
