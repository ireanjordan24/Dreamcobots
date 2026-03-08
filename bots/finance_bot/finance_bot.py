"""
Dreamcobots Finance Bot — tier-aware budget tracking and financial management.

Usage
-----
    from finance_bot import FinanceBot
    from tiers import Tier

    bot = FinanceBot(tier=Tier.FREE)
    result = bot.log_expense("food", 25.50, "Lunch")
    print(result)
"""
# Adheres to the GLOBAL AI SOURCES FLOW framework — see framework/global_ai_sources_flow.py


import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ai-models-integration'))

from tiers import Tier, get_tier_config, get_upgrade_path

import importlib.util as _ilu
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_spec = _ilu.spec_from_file_location("_finance_tiers", os.path.join(_THIS_DIR, "tiers.py"))
_finance_tiers = _ilu.module_from_spec(_spec)
_spec.loader.exec_module(_finance_tiers)
FINANCE_FEATURES = _finance_tiers.FINANCE_FEATURES
get_finance_tier_info = _finance_tiers.get_finance_tier_info


class FinanceBotTierError(Exception):
    """Raised when a feature is not available on the current tier."""


class FinanceBotRequestLimitError(Exception):
    """Raised when the monthly request quota has been exhausted."""


class FinanceBot:
    """
    Tier-aware financial tracking and management bot.

    Parameters
    ----------
    tier : Tier
        Subscription tier controlling feature availability and request limits.
    """

    def __init__(self, tier: Tier = Tier.FREE):
        self.tier = tier
        self.config = get_tier_config(tier)
        self._request_count: int = 0
        self._expenses: list[dict] = []
        self._income: list[dict] = []

    # ------------------------------------------------------------------
    # Core API
    # ------------------------------------------------------------------

    def log_expense(self, category: str, amount: float, description: str = "") -> dict:
        """
        Log an expense.

        Parameters
        ----------
        category : str
            Expense category (e.g., "food", "transport").
        amount : float
            Amount spent.
        description : str
            Optional description.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        entry = {
            "expense_id": f"EXP-{len(self._expenses) + 1:04d}",
            "category": category,
            "amount": amount,
            "description": description,
        }
        self._expenses.append(entry)
        return {
            "expense": entry,
            "total_expenses": sum(e["amount"] for e in self._expenses),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def log_income(self, source: str, amount: float) -> dict:
        """
        Log an income entry.

        Parameters
        ----------
        source : str
            Income source (e.g., "salary", "freelance").
        amount : float
            Amount received.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        entry = {
            "income_id": f"INC-{len(self._income) + 1:04d}",
            "source": source,
            "amount": amount,
        }
        self._income.append(entry)
        return {
            "income": entry,
            "total_income": sum(i["amount"] for i in self._income),
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def get_budget_summary(self) -> dict:
        """
        Return total income, expenses, and balance.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        self._request_count += 1
        total_income = sum(i["amount"] for i in self._income)
        total_expenses = sum(e["amount"] for e in self._expenses)
        balance = total_income - total_expenses
        by_category: dict[str, float] = {}
        for exp in self._expenses:
            by_category[exp["category"]] = by_category.get(exp["category"], 0) + exp["amount"]
        return {
            "total_income": round(total_income, 2),
            "total_expenses": round(total_expenses, 2),
            "balance": round(balance, 2),
            "expenses_by_category": {k: round(v, 2) for k, v in by_category.items()},
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def forecast_cashflow(self, months: int = 3) -> dict:
        """
        Forecast cash flow for upcoming months.  Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        months : int
            Number of months to forecast.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if self.tier == Tier.FREE:
            raise FinanceBotTierError(
                "Cash flow forecasting requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        avg_income = (sum(i["amount"] for i in self._income) / len(self._income)
                      if self._income else 0.0)
        avg_expense = (sum(e["amount"] for e in self._expenses) / len(self._expenses)
                       if self._expenses else 0.0)
        forecasts = [
            {
                "month": i + 1,
                "projected_income": round(avg_income, 2),
                "projected_expenses": round(avg_expense, 2),
                "projected_balance": round(avg_income - avg_expense, 2),
            }
            for i in range(months)
        ]
        return {
            "forecast_months": months,
            "forecasts": forecasts,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    def estimate_taxes(self, income: float, deductions: float = 0.0) -> dict:
        """
        Estimate tax liability.  Requires PRO or ENTERPRISE tier.

        Parameters
        ----------
        income : float
            Gross annual income.
        deductions : float
            Total deductible amount.

        Returns
        -------
        dict
        """
        self._check_request_limit()
        if self.tier == Tier.FREE:
            raise FinanceBotTierError(
                "Tax estimation requires PRO or ENTERPRISE tier."
            )
        self._request_count += 1
        taxable_income = max(income - deductions, 0.0)
        # Simplified mock tax bracket
        if taxable_income <= 10_000:
            rate = 0.10
        elif taxable_income <= 40_000:
            rate = 0.22
        elif taxable_income <= 85_000:
            rate = 0.24
        else:
            rate = 0.32
        estimated_tax = round(taxable_income * rate, 2)
        return {
            "gross_income": income,
            "deductions": deductions,
            "taxable_income": round(taxable_income, 2),
            "effective_rate_pct": rate * 100,
            "estimated_tax": estimated_tax,
            "tier": self.tier.value,
            "requests_used": self._request_count,
            "requests_remaining": self._requests_remaining(),
        }

    # ------------------------------------------------------------------
    # Tier information
    # ------------------------------------------------------------------

    def describe_tier(self) -> str:
        """Print and return a description of the current tier."""
        info = get_finance_tier_info(self.tier)
        limit = (
            "Unlimited"
            if info["requests_per_month"] is None
            else f"{info['requests_per_month']:,}"
        )
        lines = [
            f"=== {info['name']} Finance Bot Tier ===",
            f"Price   : ${info['price_usd_monthly']:.2f}/month",
            f"Requests: {limit}/month",
            f"Support : {info['support_level']}",
            "",
            "Features:",
        ]
        for feat in info["finance_features"]:
            lines.append(f"  ✓ {feat}")
        output = "\n".join(lines)
        print(output)
        return output

    def show_upgrade_path(self) -> str:
        """Print details about the next available tier upgrade."""
        next_cfg = get_upgrade_path(self.tier)
        if next_cfg is None:
            msg = f"You are already on the top-tier plan ({self.config.name})."
            print(msg)
            return msg
        current_feats = set(FINANCE_FEATURES[self.tier.value])
        new_feats = [f for f in FINANCE_FEATURES[next_cfg.tier.value] if f not in current_feats]
        lines = [
            f"=== Upgrade: {self.config.name} → {next_cfg.name} ===",
            f"New price: ${next_cfg.price_usd_monthly:.2f}/month",
            "",
            "New features:",
        ]
        for feat in new_feats:
            lines.append(f"  + {feat}")
        lines.append(
            f"\nTo upgrade, set tier=Tier.{next_cfg.tier.name} when "
            "constructing FinanceBot or contact support."
        )
        output = "\n".join(lines)
        print(output)
        return output

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _check_request_limit(self) -> None:
        limit = self.config.requests_per_month
        if limit is not None and self._request_count >= limit:
            raise FinanceBotRequestLimitError(
                f"Monthly request limit of {limit:,} reached on the "
                f"{self.config.name} tier. Please upgrade to continue."
            )

    def _requests_remaining(self) -> str:
        limit = self.config.requests_per_month
        if limit is None:
            return "unlimited"
        return str(max(limit - self._request_count, 0))


if __name__ == "__main__":
    bot = FinanceBot(tier=Tier.FREE)
    bot.describe_tier()
    bot.log_income("salary", 3000.0)
    bot.log_expense("food", 400.0, "Groceries")
    print(bot.get_budget_summary())
