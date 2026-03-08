"""
Tests for bots/finance_bot/tiers.py and bots/finance_bot/finance_bot.py
"""

import sys
import os

REPO_ROOT = os.path.join(os.path.dirname(__file__), '..')
AI_MODELS_DIR = os.path.join(REPO_ROOT, 'bots', 'ai-models-integration')
BOT_DIR = os.path.join(REPO_ROOT, 'bots', 'finance_bot')
sys.path.insert(0, AI_MODELS_DIR)
sys.path.insert(0, REPO_ROOT)

import pytest
from tiers import Tier
from bots.finance_bot.finance_bot import FinanceBot, FinanceBotTierError, FinanceBotRequestLimitError


# -----------------------------------------------------------------------
# Tier info tests
# -----------------------------------------------------------------------

class TestFinanceBotTierInfo:
    def _load_tiers(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "_fin_tiers", os.path.join(BOT_DIR, "tiers.py")
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod

    def test_tier_info_keys(self):
        mod = self._load_tiers()
        info = mod.get_finance_tier_info(Tier.FREE)
        for key in ("tier", "name", "price_usd_monthly", "requests_per_month",
                    "finance_features", "support_level"):
            assert key in info

    def test_free_price_zero(self):
        mod = self._load_tiers()
        assert mod.get_finance_tier_info(Tier.FREE)["price_usd_monthly"] == 0.0

    def test_enterprise_unlimited(self):
        mod = self._load_tiers()
        assert mod.get_finance_tier_info(Tier.ENTERPRISE)["requests_per_month"] is None

    def test_all_tiers_have_features(self):
        mod = self._load_tiers()
        for tier in Tier:
            assert len(mod.get_finance_tier_info(tier)["finance_features"]) > 0


# -----------------------------------------------------------------------
# FinanceBot tests
# -----------------------------------------------------------------------

class TestFinanceBot:
    def test_default_tier_free(self):
        bot = FinanceBot()
        assert bot.tier == Tier.FREE

    def test_log_expense_returns_dict(self):
        bot = FinanceBot()
        result = bot.log_expense("food", 25.50, "Lunch")
        assert isinstance(result, dict)

    def test_log_expense_keys(self):
        bot = FinanceBot()
        result = bot.log_expense("transport", 10.0)
        for key in ("expense", "total_expenses", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_log_expense_increments_count(self):
        bot = FinanceBot()
        bot.log_expense("food", 10.0)
        bot.log_expense("transport", 5.0)
        assert bot._request_count == 2

    def test_log_income_returns_dict(self):
        bot = FinanceBot()
        result = bot.log_income("salary", 3000.0)
        assert isinstance(result, dict)

    def test_log_income_keys(self):
        bot = FinanceBot()
        result = bot.log_income("freelance", 500.0)
        for key in ("income", "total_income", "tier", "requests_used", "requests_remaining"):
            assert key in result

    def test_get_budget_summary_returns_dict(self):
        bot = FinanceBot()
        bot.log_income("salary", 3000.0)
        bot.log_expense("food", 400.0)
        result = bot.get_budget_summary()
        assert isinstance(result, dict)

    def test_budget_summary_keys(self):
        bot = FinanceBot()
        result = bot.get_budget_summary()
        for key in ("total_income", "total_expenses", "balance",
                    "expenses_by_category", "tier"):
            assert key in result

    def test_budget_summary_balance_correct(self):
        bot = FinanceBot()
        bot.log_income("salary", 1000.0)
        bot.log_expense("rent", 600.0)
        summary = bot.get_budget_summary()
        assert summary["balance"] == pytest.approx(400.0)

    def test_budget_expenses_by_category(self):
        bot = FinanceBot()
        bot.log_expense("food", 100.0)
        bot.log_expense("food", 50.0)
        bot.log_expense("transport", 30.0)
        summary = bot.get_budget_summary()
        assert summary["expenses_by_category"]["food"] == pytest.approx(150.0)

    def test_forecast_cashflow_free_raises(self):
        bot = FinanceBot(tier=Tier.FREE)
        with pytest.raises(FinanceBotTierError):
            bot.forecast_cashflow(3)

    def test_forecast_cashflow_pro_ok(self):
        bot = FinanceBot(tier=Tier.PRO)
        result = bot.forecast_cashflow(3)
        assert isinstance(result, dict)
        assert len(result["forecasts"]) == 3

    def test_forecast_cashflow_keys(self):
        bot = FinanceBot(tier=Tier.PRO)
        result = bot.forecast_cashflow(2)
        for key in ("forecast_months", "forecasts", "tier"):
            assert key in result
        for month in result["forecasts"]:
            for k in ("month", "projected_income", "projected_expenses", "projected_balance"):
                assert k in month

    def test_estimate_taxes_free_raises(self):
        bot = FinanceBot(tier=Tier.FREE)
        with pytest.raises(FinanceBotTierError):
            bot.estimate_taxes(50_000.0)

    def test_estimate_taxes_pro_ok(self):
        bot = FinanceBot(tier=Tier.PRO)
        result = bot.estimate_taxes(50_000.0, deductions=5_000.0)
        assert isinstance(result, dict)
        assert "estimated_tax" in result

    def test_estimate_taxes_keys(self):
        bot = FinanceBot(tier=Tier.PRO)
        result = bot.estimate_taxes(40_000.0)
        for key in ("gross_income", "deductions", "taxable_income",
                    "effective_rate_pct", "estimated_tax", "tier"):
            assert key in result

    def test_estimate_taxes_no_negative_taxable(self):
        bot = FinanceBot(tier=Tier.PRO)
        result = bot.estimate_taxes(1000.0, deductions=5000.0)
        assert result["taxable_income"] == 0.0
        assert result["estimated_tax"] == 0.0

    def test_request_limit_raises(self):
        bot = FinanceBot(tier=Tier.FREE)
        bot._request_count = bot.config.requests_per_month
        with pytest.raises(FinanceBotRequestLimitError):
            bot.log_expense("food", 10.0)

    def test_enterprise_no_request_limit(self):
        bot = FinanceBot(tier=Tier.ENTERPRISE)
        bot._request_count = 999_999
        result = bot.log_income("salary", 1000.0)
        assert result["requests_remaining"] == "unlimited"

    def test_describe_tier_returns_string(self):
        bot = FinanceBot()
        output = bot.describe_tier()
        assert isinstance(output, str)
        assert "Free" in output

    def test_show_upgrade_path_from_free(self):
        bot = FinanceBot()
        output = bot.show_upgrade_path()
        assert "Pro" in output

    def test_show_upgrade_path_enterprise(self):
        bot = FinanceBot(tier=Tier.ENTERPRISE)
        output = bot.show_upgrade_path()
        assert "top-tier" in output
