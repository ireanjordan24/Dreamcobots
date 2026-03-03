"""
bots/finance-bot/finance_bot.py

FinanceBot — budget analysis, investment returns, and financial planning.
"""

from __future__ import annotations

import math
import threading
import uuid
from datetime import datetime, timezone
from typing import Any

from bots.bot_base import BotBase

_INVESTMENT_OPTIONS: dict[str, list[dict[str, Any]]] = {
    "low": [
        {"name": "US Treasury Bonds", "expected_return": "3-5%", "risk": "Very Low"},
        {"name": "High-Yield Savings Account", "expected_return": "4-5%", "risk": "Very Low"},
        {"name": "CD Ladder", "expected_return": "4-5.5%", "risk": "Very Low"},
    ],
    "medium": [
        {"name": "S&P 500 Index Fund", "expected_return": "7-10%", "risk": "Medium"},
        {"name": "Dividend Growth ETF", "expected_return": "6-8%", "risk": "Medium"},
        {"name": "REIT Index Fund", "expected_return": "7-9%", "risk": "Medium"},
    ],
    "high": [
        {"name": "Individual Growth Stocks", "expected_return": "10-20%+", "risk": "High"},
        {"name": "Venture Capital Fund", "expected_return": "15-30%+", "risk": "Very High"},
        {"name": "Cryptocurrency Portfolio", "expected_return": "Variable", "risk": "Very High"},
    ],
}


class FinanceBot(BotBase):
    """
    Provides budgeting, investment calculations, and financial planning guidance.
    """

    def __init__(self, bot_id: str | None = None) -> None:
        super().__init__(
            bot_name="FinanceBot",
            bot_id=bot_id or str(uuid.uuid4()),
        )
        self._lock_extra: threading.RLock = threading.RLock()

    def run(self) -> None:
        self._set_running(True)
        self._start_time = datetime.now(timezone.utc)
        self.log_activity("FinanceBot started.")

    def stop(self) -> None:
        self._set_running(False)
        self.log_activity("FinanceBot stopped.")

    # ------------------------------------------------------------------
    # API
    # ------------------------------------------------------------------

    def analyze_budget(
        self, income: float, expenses: dict[str, float]
    ) -> dict[str, Any]:
        """
        Analyse income vs expenses and provide recommendations.

        Args:
            income: Monthly net income.
            expenses: Dict of expense category -> monthly amount.

        Returns:
            Budget analysis dict with savings rate, categories, and tips.
        """
        total_expenses = sum(expenses.values())
        surplus = income - total_expenses
        savings_rate = round((surplus / income * 100), 2) if income > 0 else 0.0
        expense_pct = {k: round(v / income * 100, 2) if income > 0 else 0 for k, v in expenses.items()}

        recommendations: list[str] = []
        if savings_rate < 10:
            recommendations.append("Aim to save at least 20% of income.")
        if expense_pct.get("housing", 0) > 30:
            recommendations.append("Housing costs exceed 30% of income — consider refinancing or downsizing.")
        if expense_pct.get("dining", 0) > 10:
            recommendations.append("Dining out is over 10% of income — meal prep can reduce costs.")
        if not recommendations:
            recommendations.append("Your budget looks healthy! Consider increasing investments.")

        self.log_activity("Budget analysed.")
        return {
            "income": income,
            "total_expenses": round(total_expenses, 2),
            "surplus": round(surplus, 2),
            "savings_rate_pct": savings_rate,
            "expense_breakdown_pct": expense_pct,
            "recommendations": recommendations,
        }

    def calculate_investment_returns(
        self, principal: float, rate: float, years: int
    ) -> float:
        """
        Calculate compound interest growth.

        Args:
            principal: Initial investment amount.
            rate: Annual interest rate as a decimal (e.g. 0.07 for 7%).
            years: Investment horizon in years.

        Returns:
            Future value rounded to 2 decimal places.
        """
        if years < 0:
            raise ValueError("years must be non-negative.")
        future_value = principal * math.pow(1 + rate, years)
        self.log_activity(f"Investment return calculated: ${future_value:.2f}.")
        return round(future_value, 2)

    def find_investment_opportunities(self, risk_level: str) -> list[dict[str, Any]]:
        """
        Return investment options for a given risk tolerance.

        Args:
            risk_level: ``"low"``, ``"medium"``, or ``"high"``.

        Returns:
            List of investment option dicts.
        """
        level = risk_level.lower().strip()
        options = _INVESTMENT_OPTIONS.get(level, _INVESTMENT_OPTIONS["medium"])
        self.log_activity(f"Investment opportunities retrieved for risk='{risk_level}'.")
        return list(options)

    def generate_financial_plan(self, goals: list[str]) -> dict[str, Any]:
        """
        Generate a personalised financial plan for a list of goals.

        Args:
            goals: List of financial goal strings.

        Returns:
            Structured financial plan dict.
        """
        strategies: list[dict[str, str]] = []
        for goal in goals:
            gl = goal.lower()
            if "retire" in gl:
                strategies.append({"goal": goal, "strategy": "Max 401(k) and IRA contributions; target 25x annual expenses."})
            elif "house" in gl or "home" in gl:
                strategies.append({"goal": goal, "strategy": "Save 20% down payment; maintain credit score above 720."})
            elif "emergency" in gl:
                strategies.append({"goal": goal, "strategy": "Build 6-month expense fund in a high-yield savings account."})
            elif "debt" in gl:
                strategies.append({"goal": goal, "strategy": "Use avalanche method: pay highest-interest debt first."})
            else:
                strategies.append({"goal": goal, "strategy": "Set a monthly savings target and automate transfers."})

        self.log_activity("Financial plan generated.")
        return {
            "goals": goals,
            "strategies": strategies,
            "general_advice": [
                "Follow the 50/30/20 rule: needs / wants / savings.",
                "Diversify investments across asset classes.",
                "Review your plan annually and after major life events.",
            ],
            "generated_at": datetime.now(timezone.utc).isoformat(),
        }
