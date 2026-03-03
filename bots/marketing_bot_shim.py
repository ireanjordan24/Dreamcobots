"""bots/marketing_bot_shim.py — importable shim for MarketingBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "marketing-bot", "marketing_bot.py")
_spec = importlib.util.spec_from_file_location("marketing_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["marketing_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
MarketingBot = _mod.MarketingBot
__all__ = ["MarketingBot"]
