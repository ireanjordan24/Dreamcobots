# GLOBAL AI SOURCES FLOW
"""Predictive Engagement Tool - score and predict customer engagement and churn risk."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
from framework import GlobalAISourcesFlow  # noqa: F401
try:
    from tiers import TIERS
except ImportError:
    from analytics_elites.predictive_engagement_tool.tiers import TIERS


class PredictiveEngagementTool:
    """Score customer engagement and predict churn risk using behavioral signals."""

    SEGMENT_THRESHOLDS = {"champion": 80, "loyal": 60, "at_risk": 40, "dormant": 20}

    def __init__(self, tier: str = "free"):
        self.tier = tier
        self.tier_config = TIERS.get(tier, TIERS["free"])

    def score_engagement(self, customer: dict) -> dict:
        """
        Calculate an engagement score (0-100) from behavioral signals.

        customer keys: recency_days, frequency_30d, avg_session_minutes,
                       email_open_rate (0-1), support_tickets_90d
        """
        recency = customer.get("recency_days", 90)
        frequency = customer.get("frequency_30d", 0)
        session_min = customer.get("avg_session_minutes", 0)
        email_open = customer.get("email_open_rate", 0.0)
        tickets = customer.get("support_tickets_90d", 0)

        recency_score = max(0, 100 - recency * 1.5)
        frequency_score = min(100, frequency * 10)
        session_score = min(100, session_min * 5)
        email_score = email_open * 100
        ticket_penalty = min(30, tickets * 10)

        raw = (recency_score * 0.3 + frequency_score * 0.25 +
               session_score * 0.2 + email_score * 0.25) - ticket_penalty
        score = round(max(0, min(100, raw)), 1)

        segment = "dormant"
        for seg, threshold in self.SEGMENT_THRESHOLDS.items():
            if score >= threshold:
                segment = seg
                break

        return {
            "customer_id": customer.get("customer_id", "unknown"),
            "engagement_score": score,
            "segment": segment,
            "tier": self.tier,
        }

    def predict_churn(self, customer: dict) -> dict:
        """Predict churn probability (Pro+ only)."""
        if self.tier == "free":
            raise PermissionError("Churn prediction requires Pro tier or higher.")
        score_result = self.score_engagement(customer)
        score = score_result["engagement_score"]
        recency = customer.get("recency_days", 90)

        churn_prob = round(max(0, min(1, (100 - score) / 100 * 0.7 + (recency / 365) * 0.3)), 3)
        risk_level = "high" if churn_prob > 0.6 else "medium" if churn_prob > 0.3 else "low"

        return {
            "customer_id": customer.get("customer_id", "unknown"),
            "churn_probability": churn_prob,
            "risk_level": risk_level,
            "engagement_score": score,
            "recommended_action": self._recommend_action(risk_level),
        }

    def _recommend_action(self, risk_level: str) -> str:
        actions = {
            "high": "Send win-back campaign with personalized discount immediately.",
            "medium": "Trigger re-engagement email sequence with product highlights.",
            "low": "Maintain regular nurture cadence; monitor for signal changes.",
        }
        return actions.get(risk_level, "Monitor engagement signals.")

    def batch_score(self, customers: list) -> list:
        """Score engagement for a list of customers."""
        return [self.score_engagement(c) for c in customers]
