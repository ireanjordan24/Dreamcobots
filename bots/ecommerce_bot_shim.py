"""bots/ecommerce_bot_shim.py — importable shim for EcommerceBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "ecommerce-bot", "ecommerce_bot.py")
_spec = importlib.util.spec_from_file_location("ecommerce_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["ecommerce_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
EcommerceBot = _mod.EcommerceBot
__all__ = ["EcommerceBot"]
