"""bots/cybersecurity_bot_shim.py — importable shim for CybersecurityBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "cybersecurity-bot", "cybersecurity_bot.py")
_spec = importlib.util.spec_from_file_location("cybersecurity_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["cybersecurity_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
CybersecurityBot = _mod.CybersecurityBot
__all__ = ["CybersecurityBot"]
