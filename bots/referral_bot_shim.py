"""bots/referral_bot_shim.py — importable shim for ReferralBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "referral-bot", "referral_bot.py")
_spec = importlib.util.spec_from_file_location("referral_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["referral_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
ReferralBot = _mod.ReferralBot
__all__ = ["ReferralBot"]
