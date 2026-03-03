"""bots/education_bot_shim.py — importable shim for EducationBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "education-bot", "education_bot.py")
_spec = importlib.util.spec_from_file_location("education_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["education_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
EducationBot = _mod.EducationBot
__all__ = ["EducationBot"]
