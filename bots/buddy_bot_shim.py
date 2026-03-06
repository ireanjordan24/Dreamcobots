"""bots/buddy_bot_shim.py — importable shim for BuddyBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "buddy-bot", "buddy_bot.py")
_spec = importlib.util.spec_from_file_location("buddy_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["buddy_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
BuddyBot = _mod.BuddyBot
__all__ = ["BuddyBot"]
