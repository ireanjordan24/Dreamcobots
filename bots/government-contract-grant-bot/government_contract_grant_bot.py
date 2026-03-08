# Government Contract & Grant Bot
#
# Adheres to the Dreamcobots GLOBAL AI SOURCES FLOW framework.
# See framework/global_ai_sources_flow.py for the full pipeline specification.

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from framework import GlobalAISourcesFlow


class GovernmentContractGrantBot:
    """Bot that discovers and processes government contracts and grants.

    The bot is wired into the GLOBAL AI SOURCES FLOW pipeline so that all
    data sourcing, learning, testing, analytics, evolution, deployment,
    market intelligence, and governance stages are executed in order.
    """

    def __init__(self):
        self.flow = GlobalAISourcesFlow(bot_name="GovernmentContractGrantBot")

    def start(self):
        print("Government Contract & Grant Bot is starting...")

    def process_contracts(self):
        print("Processing contracts...")

    def process_grants(self):
        print("Processing grants...")

    def run(self):
        self.start()
        self.process_contracts()
        self.process_grants()
        result = self.flow.run_pipeline(
            raw_data={"domain": "government_contracts_and_grants"},
            learning_method="supervised",
        )
        print(f"Pipeline complete: {result['pipeline_complete']}")
        return result


# If this module is run directly, start the bot
if __name__ == '__main__':
    bot = GovernmentContractGrantBot()
    bot.run()