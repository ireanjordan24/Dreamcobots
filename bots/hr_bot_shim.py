"""bots/hr_bot_shim.py — importable shim for HrBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "hr-bot", "hr_bot.py")
_spec = importlib.util.spec_from_file_location("hr_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["hr_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
HrBot = _mod.HrBot
__all__ = ["HrBot"]
