"""bots/legal_bot_shim.py — importable shim for LegalBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "legal-bot", "legal_bot.py")
_spec = importlib.util.spec_from_file_location("legal_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["legal_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
LegalBot = _mod.LegalBot
__all__ = ["LegalBot"]
