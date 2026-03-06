"""bots/entrepreneur_bot_shim.py — importable shim for EntrepreneurBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "entrepreneur-bot", "entrepreneur_bot.py")
_spec = importlib.util.spec_from_file_location("entrepreneur_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["entrepreneur_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
EntrepreneurBot = _mod.EntrepreneurBot
__all__ = ["EntrepreneurBot"]
