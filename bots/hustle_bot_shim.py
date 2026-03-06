"""
bots/hustle_bot_shim.py — importable shim for HustleBot.
"""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "hustle-bot", "hustle_bot.py")
_spec = importlib.util.spec_from_file_location("hustle_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["hustle_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
HustleBot = _mod.HustleBot
__all__ = ["HustleBot"]
