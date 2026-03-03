"""
bots/medical-bot/medical_bot.py

MedicalBot — health information assistant.

DISCLAIMER: This bot provides general health information only.
It is NOT a substitute for professional medical advice, diagnosis, or treatment.
Always consult a qualified healthcare provider for medical concerns.
"""

from __future__ import annotations

import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_DISCLAIMER = (
    "⚠️ MEDICAL DISCLAIMER: This information is for general educational purposes only "
    "and does NOT constitute medical advice. Always consult a qualified healthcare "
    "professional before making any health-related decisions."
)

_CONDITIONS_DB: dict[str, dict[str, Any]] = {
    "diabetes": {
        "description": "A metabolic disease causing high blood sugar levels.",
        "symptoms": ["increased thirst", "frequent urination", "fatigue", "blurred vision"],
        "treatments": ["insulin therapy", "oral medications", "diet management", "exercise"],
        "icd10": "E11",
    },
    "hypertension": {
        "description": "Persistently elevated blood pressure in the arteries.",
        "symptoms": ["headaches", "shortness of breath", "nosebleeds"],
        "treatments": ["ACE inhibitors", "beta-blockers", "lifestyle changes"],
        "icd10": "I10",
    },
    "asthma": {
        "description": "Chronic lung disease that inflames and narrows airways.",
        "symptoms": ["wheezing", "shortness of breath", "chest tightness", "coughing"],
        "treatments": ["bronchodilators", "inhaled corticosteroids", "avoiding triggers"],
        "icd10": "J45",
    },
    "depression": {
        "description": "A mood disorder causing persistent sadness and loss of interest.",
        "symptoms": ["persistent sadness", "loss of interest", "fatigue", "sleep problems"],
        "treatments": ["antidepressants", "psychotherapy", "lifestyle changes"],
        "icd10": "F32",
    },
}

_MEDICATIONS_DB: dict[str, dict[str, Any]] = {
    "metformin": {
        "class": "Biguanide",
        "uses": "Type 2 diabetes management",
        "common_side_effects": ["nausea", "diarrhoea", "stomach upset"],
        "contraindications": ["severe kidney disease", "liver disease"],
    },
    "lisinopril": {
        "class": "ACE Inhibitor",
        "uses": "Hypertension and heart failure",
        "common_side_effects": ["dry cough", "dizziness", "hyperkalaemia"],
        "contraindications": ["pregnancy", "angioedema history"],
    },
    "atorvastatin": {
        "class": "Statin",
        "uses": "High cholesterol and cardiovascular risk reduction",
        "common_side_effects": ["muscle pain", "liver enzyme elevation"],
        "contraindications": ["pregnancy", "liver disease"],
    },
}


class MedicalBot(BotBase):
    """
    Health information bot. All responses include mandatory medical disclaimers.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="MedicalBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("MedicalBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("MedicalBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def search_condition(self, condition: str) -> dict[str, Any]:
        """
        Return general information about a medical condition.

        Args:
            condition: Condition name (e.g. ``"diabetes"``).

        Returns:
            Dict with condition details and mandatory disclaimer.
        """
        key = condition.lower().strip()
        info = _CONDITIONS_DB.get(key, {
            "description": f"No specific data available for '{condition}'.",
            "symptoms": [],
            "treatments": ["Consult a healthcare provider"],
            "icd10": "N/A",
        })
        self.log_activity(f"Condition searched: '{condition}'.")
        return {**info, "condition": condition, "disclaimer": _DISCLAIMER}

    def get_medication_info(self, medication: str) -> dict[str, Any]:
        """
        Return general information about a medication.

        Args:
            medication: Medication name.

        Returns:
            Dict with medication details and mandatory disclaimer.
        """
        key = medication.lower().strip()
        info = _MEDICATIONS_DB.get(key, {
            "class": "Unknown",
            "uses": f"No data available for '{medication}'.",
            "common_side_effects": [],
            "contraindications": ["Consult a pharmacist or physician"],
        })
        self.log_activity(f"Medication info requested: '{medication}'.")
        return {**info, "medication": medication, "disclaimer": _DISCLAIMER}

    def find_providers(self, location: str, specialty: str) -> list[dict[str, Any]]:
        """
        Simulate finding healthcare providers near *location* with *specialty*.

        Args:
            location: City or ZIP code.
            specialty: Medical specialty (e.g. ``"cardiologist"``).

        Returns:
            List of provider dicts with disclaimer.
        """
        providers = [
            {
                "name": f"Dr. A. Smith — {specialty.title()}",
                "address": f"123 Health Ave, {location}",
                "phone": "(555) 100-0001",
                "accepting_patients": True,
                "disclaimer": _DISCLAIMER,
            },
            {
                "name": f"Dr. B. Jones — {specialty.title()}",
                "address": f"456 Wellness Blvd, {location}",
                "phone": "(555) 100-0002",
                "accepting_patients": True,
                "disclaimer": _DISCLAIMER,
            },
            {
                "name": f"{location} Medical Center — {specialty.title()} Dept",
                "address": f"789 Hospital Rd, {location}",
                "phone": "(555) 100-0003",
                "accepting_patients": True,
                "disclaimer": _DISCLAIMER,
            },
        ]
        self.log_activity(f"Provider search: location='{location}', specialty='{specialty}'.")
        return providers

    def generate_health_report(self, vitals: dict[str, Any]) -> dict[str, Any]:
        """
        Generate a basic health assessment from vital signs.

        Args:
            vitals: Dict with optional keys ``blood_pressure``, ``heart_rate``,
                    ``temperature``, ``bmi``.

        Returns:
            Health report dict with observations and disclaimer.
        """
        observations: list[str] = []
        bp = vitals.get("blood_pressure", "")
        hr = vitals.get("heart_rate", 0)
        temp = vitals.get("temperature", 98.6)
        bmi = vitals.get("bmi", 22.0)

        if bp and "/" in str(bp):
            sys_bp, dia_bp = (int(x) for x in str(bp).split("/"))
            if sys_bp >= 130 or dia_bp >= 80:
                observations.append("Blood pressure is elevated — monitor closely.")
            else:
                observations.append("Blood pressure is within normal range.")

        if hr:
            if 60 <= int(hr) <= 100:
                observations.append("Heart rate is normal (60–100 bpm).")
            else:
                observations.append(f"Heart rate ({hr} bpm) is outside normal range.")

        if float(temp) > 100.4:
            observations.append(f"Temperature ({temp}°F) indicates possible fever.")
        else:
            observations.append("Temperature is normal.")

        bmi_f = float(bmi)
        if bmi_f < 18.5:
            bmi_status = "Underweight"
        elif bmi_f < 25:
            bmi_status = "Normal weight"
        elif bmi_f < 30:
            bmi_status = "Overweight"
        else:
            bmi_status = "Obese"
        observations.append(f"BMI {bmi_f:.1f} — {bmi_status}.")

        self.log_activity("Health report generated.")
        return {
            "vitals": vitals,
            "observations": observations,
            "risk_level": "Low" if len([o for o in observations if "elevated" in o or "outside" in o or "fever" in o]) == 0 else "Moderate",
            "recommendations": ["Schedule a check-up with your GP", "Maintain a balanced diet and regular exercise"],
            "disclaimer": _DISCLAIMER,
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
