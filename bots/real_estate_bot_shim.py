"""bots/real_estate_bot_shim.py — importable shim for RealEstateBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "real-estate-bot", "real_estate_bot.py")
_spec = importlib.util.spec_from_file_location("real_estate_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["real_estate_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
RealEstateBot = _mod.RealEstateBot
__all__ = ["RealEstateBot"]
