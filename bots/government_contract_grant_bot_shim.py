"""
bots/government_contract_grant_bot_shim.py

Re-exports GovernmentContractGrantBot from the hyphenated sub-directory so
that it can be imported as a normal Python module.
"""

import importlib.util
import os
import sys

_BOT_PATH = os.path.join(
    os.path.dirname(__file__),
    "government-contract-grant-bot",
    "government_contract_grant_bot.py",
)

_spec = importlib.util.spec_from_file_location(
    "government_contract_grant_bot", _BOT_PATH
)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["government_contract_grant_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]

GovernmentContractGrantBot = _mod.GovernmentContractGrantBot

__all__ = ["GovernmentContractGrantBot"]
