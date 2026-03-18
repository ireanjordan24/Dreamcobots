# GLOBAL AI SOURCES FLOW
"""Drug Discovery Pipeline AI - computational drug discovery screening tool."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from framework import GlobalAISourcesFlow  # noqa: F401
try:
    from tiers import TIERS
except ImportError:
    from healthcare_tools.drug_discovery_pipeline_ai.tiers import TIERS


PROPERTY_THRESHOLDS = {
    "molecular_weight": (100, 500),
    "logp": (-0.5, 5.0),
    "h_bond_donors": (0, 5),
    "h_bond_acceptors": (0, 10),
    "rotatable_bonds": (0, 10),
    "tpsa": (0, 140),
}

ADMET_RULES = {
    "oral_bioavailability": lambda mw, logp: mw <= 500 and -0.5 <= logp <= 5.0,
    "blood_brain_barrier": lambda mw, tpsa: mw < 450 and tpsa < 90,
    "renal_clearance_risk": lambda mw: mw > 400,
}


class DrugDiscoveryPipelineAI:
    """Computational drug discovery pipeline: screening, ADMET, and lead optimization."""

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])

    def screen_compound(self, compound: dict) -> dict:
        """
        Apply Lipinski Rule-of-Five screening to a compound.
        compound keys: name, molecular_weight, logp, h_bond_donors, h_bond_acceptors.
        """
        violations = []
        mw = compound.get("molecular_weight", 0)
        logp = compound.get("logp", 0)
        hbd = compound.get("h_bond_donors", 0)
        hba = compound.get("h_bond_acceptors", 0)

        if mw > 500:
            violations.append("molecular_weight > 500 Da")
        if logp > 5:
            violations.append("logP > 5")
        if hbd > 5:
            violations.append("H-bond donors > 5")
        if hba > 10:
            violations.append("H-bond acceptors > 10")

        passed = len(violations) <= 1
        return {
            "compound": compound.get("name", "Unknown"),
            "rule_of_five_passed": passed,
            "violations": violations,
            "drug_like": passed,
            "tier": self.tier,
        }

    def predict_admet(self, compound: dict) -> dict:
        """Predict ADMET properties (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("ADMET prediction requires Pro tier or higher.")
        mw = compound.get("molecular_weight", 0)
        logp = compound.get("logp", 0)
        tpsa = compound.get("tpsa", 0)
        return {
            "compound": compound.get("name", "Unknown"),
            "oral_bioavailability": ADMET_RULES["oral_bioavailability"](mw, logp),
            "blood_brain_barrier_penetration": ADMET_RULES["blood_brain_barrier"](mw, tpsa),
            "renal_clearance_risk": ADMET_RULES["renal_clearance_risk"](mw),
            "solubility_estimate": "low" if logp > 4 else "moderate" if logp > 2 else "high",
            "disclaimer": "Computational prediction only. Requires wet-lab validation.",
        }

    def score_target_docking(self, compound: dict, target: str) -> dict:
        """Return a mock docking score for a compound-target pair (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Target docking requires Pro tier or higher.")
        mw = compound.get("molecular_weight", 300)
        logp = compound.get("logp", 2.0)
        score = round(-1 * (mw / 100 + logp * 0.5 + 3.0), 2)
        return {
            "compound": compound.get("name", "Unknown"),
            "target": target,
            "docking_score_kcal_mol": score,
            "interpretation": "favorable" if score <= -6 else "moderate" if score <= -4 else "weak",
            "disclaimer": "Simulated score. Real docking requires molecular simulation software.",
        }

    def suggest_lead_optimization(self, screen_result: dict) -> list:
        """Provide lead optimization suggestions based on screening result (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Lead optimization requires Pro tier or higher.")
        suggestions = []
        if not screen_result.get("drug_like"):
            suggestions.append("Reduce molecular weight below 500 Da by removing bulky substituents.")
            suggestions.append("Adjust logP to the 1-3 range for better bioavailability.")
        else:
            suggestions.append("Compound is drug-like. Consider bioisosteric replacements to improve potency.")
            suggestions.append("Evaluate metabolic stability via CYP enzyme profiling.")
        return suggestions
