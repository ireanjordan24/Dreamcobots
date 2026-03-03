"""bots/medical_bot_shim.py — importable shim for MedicalBot."""
import importlib.util, os, sys
_path = os.path.join(os.path.dirname(__file__), "medical-bot", "medical_bot.py")
_spec = importlib.util.spec_from_file_location("medical_bot", _path)
_mod = importlib.util.module_from_spec(_spec)  # type: ignore[arg-type]
sys.modules["medical_bot"] = _mod
_spec.loader.exec_module(_mod)  # type: ignore[union-attr]
MedicalBot = _mod.MedicalBot
__all__ = ["MedicalBot"]
