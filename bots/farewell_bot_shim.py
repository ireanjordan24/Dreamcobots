"""bots/farewell_bot_shim.py — importable shim for FarewellBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "farewell-bot", "farewell_bot.py")
_spec = importlib.util.spec_from_file_location("farewell_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["farewell_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
FarewellBot = _mod.FarewellBot
__all__ = ["FarewellBot"]
