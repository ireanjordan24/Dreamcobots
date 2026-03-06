"""bots/finance_bot_shim.py — importable shim for FinanceBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "finance-bot", "finance_bot.py")
_spec = importlib.util.spec_from_file_location("finance_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["finance_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
FinanceBot = _mod.FinanceBot
__all__ = ["FinanceBot"]
