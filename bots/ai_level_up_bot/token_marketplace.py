"""
Token Marketplace — DreamCo Billing Engine

Implements the tokenised usage billing system with a configurable markup
(default 25 %).  Handles token purchases, balance management, usage tracking,
and billing reports.

Pricing structure
-----------------
| Service            | Base cost   | DreamCo price (25 % markup) |
|--------------------|-------------|------------------------------|
| GPT model tokens   | $1.00       | $1.25                        |
| Image generation   | $0.10       | $0.125                       |
| Voice generation   | $0.20       | $0.25                        |

Usage
-----
    from bots.ai_level_up_bot.token_marketplace import TokenMarketplace

    marketplace = TokenMarketplace(user_id="user_001")
    marketplace.purchase_tokens(50.0)
    result = marketplace.use_service("gpt", units=3)
    print(result)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Optional


# ---------------------------------------------------------------------------
# Enumerations & pricing constants
# ---------------------------------------------------------------------------

class ServiceType(Enum):
    """AI service types available in the token marketplace."""

    GPT = "gpt"
    IMAGE_GENERATION = "image_generation"
    VOICE_GENERATION = "voice_generation"


# Base costs per unit (in USD) before DreamCo markup.
_BASE_COSTS: dict[ServiceType, float] = {
    ServiceType.GPT: 1.0,
    ServiceType.IMAGE_GENERATION: 0.10,
    ServiceType.VOICE_GENERATION: 0.20,
}

# Default DreamCo markup applied on top of every base cost.
DEFAULT_MARKUP = 0.25  # 25 %

# Pre-defined token bundle sizes (USD spend → bonus multiplier).
TOKEN_BUNDLES: list[dict] = [
    {"label": "Starter Bundle",   "usd": 10.0,  "bonus_pct": 0.0},
    {"label": "Growth Bundle",    "usd": 50.0,  "bonus_pct": 5.0},
    {"label": "Pro Bundle",       "usd": 100.0, "bonus_pct": 10.0},
    {"label": "Enterprise Bundle","usd": 500.0, "bonus_pct": 20.0},
]


# ---------------------------------------------------------------------------
# Data models
# ---------------------------------------------------------------------------

@dataclass
class ServicePricing:
    """
    Pricing details for a single service type.

    Attributes
    ----------
    service : ServiceType
        The AI service this pricing applies to.
    base_cost_usd : float
        Raw cost per unit charged by the upstream provider.
    markup : float
        Decimal markup rate (e.g. 0.25 for 25 %).
    dreamco_price_usd : float
        Final price per unit charged to the user.
    """

    service: ServiceType
    base_cost_usd: float
    markup: float
    dreamco_price_usd: float

    @property
    def profit_per_unit(self) -> float:
        """Return DreamCo's profit per unit for this service."""
        return round(self.dreamco_price_usd - self.base_cost_usd, 6)


@dataclass
class TokenTransaction:
    """
    Record of a single token marketplace transaction.

    Attributes
    ----------
    transaction_id : str
        Unique identifier.
    user_id : str
        Owner of the transaction.
    transaction_type : str
        One of 'purchase' or 'usage'.
    service : ServiceType | None
        Service consumed (None for purchase transactions).
    units : float
        Number of tokens/units involved.
    amount_usd : float
        USD value of the transaction.
    profit_usd : float
        DreamCo profit on this transaction (0 for purchases).
    timestamp : str
        ISO 8601 timestamp of the transaction.
    """

    transaction_id: str
    user_id: str
    transaction_type: str
    service: Optional[ServiceType]
    units: float
    amount_usd: float
    profit_usd: float
    timestamp: str = field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


# ---------------------------------------------------------------------------
# Errors
# ---------------------------------------------------------------------------

class InsufficientTokensError(Exception):
    """Raised when a user has insufficient token balance for an operation."""


class TokenMarketplaceError(Exception):
    """General token marketplace error."""


# ---------------------------------------------------------------------------
# Pricing helpers
# ---------------------------------------------------------------------------

def get_service_pricing(
    service: ServiceType,
    markup: float = DEFAULT_MARKUP,
) -> ServicePricing:
    """
    Return a ServicePricing object for *service* at the given *markup*.

    Parameters
    ----------
    service : ServiceType
        The service to price.
    markup : float
        Decimal markup rate (default: 0.25).
    """
    base = _BASE_COSTS[service]
    dreamco_price = round(base * (1 + markup), 6)
    return ServicePricing(
        service=service,
        base_cost_usd=base,
        markup=markup,
        dreamco_price_usd=dreamco_price,
    )


def list_all_pricing(markup: float = DEFAULT_MARKUP) -> list[ServicePricing]:
    """Return pricing details for all service types."""
    return [get_service_pricing(s, markup) for s in ServiceType]


# ---------------------------------------------------------------------------
# Token Marketplace
# ---------------------------------------------------------------------------

class TokenMarketplace:
    """
    Per-user token balance and usage tracker.

    Parameters
    ----------
    user_id : str
        Unique identifier for the user.
    markup : float
        DreamCo markup rate applied to all services (default: 0.25).
    initial_balance : float
        Starting USD token balance (default: 0.0).

    Attributes
    ----------
    balance_usd : float
        Current unspent token balance in USD.
    total_purchased_usd : float
        Cumulative USD value of all token purchases.
    total_spent_usd : float
        Cumulative USD spent on AI services.
    total_profit_usd : float
        Total DreamCo profit generated by this user's usage.
    transactions : list[TokenTransaction]
        Full transaction history.
    """

    def __init__(
        self,
        user_id: str,
        markup: float = DEFAULT_MARKUP,
        initial_balance: float = 0.0,
    ) -> None:
        self.user_id = user_id
        self.markup = markup
        self.balance_usd: float = initial_balance
        self.total_purchased_usd: float = 0.0
        self.total_spent_usd: float = 0.0
        self.total_profit_usd: float = 0.0
        self.transactions: list[TokenTransaction] = []
        self._tx_counter: int = 0

    # ------------------------------------------------------------------
    # Purchasing
    # ------------------------------------------------------------------

    def purchase_tokens(self, amount_usd: float) -> dict:
        """
        Add *amount_usd* worth of tokens to the user's balance.

        Applies any applicable bundle bonus before crediting.

        Parameters
        ----------
        amount_usd : float
            Amount of USD to spend on tokens.

        Returns
        -------
        dict
            Summary of the purchase including bonus tokens credited.
        """
        if amount_usd <= 0:
            raise TokenMarketplaceError("Purchase amount must be positive.")

        bonus_pct = self._get_bundle_bonus(amount_usd)
        total_credit = round(amount_usd * (1 + bonus_pct / 100), 4)

        self.balance_usd = round(self.balance_usd + total_credit, 4)
        self.total_purchased_usd = round(self.total_purchased_usd + amount_usd, 4)

        tx = self._record_transaction(
            transaction_type="purchase",
            service=None,
            units=total_credit,
            amount_usd=amount_usd,
            profit_usd=0.0,
        )

        return {
            "transaction_id": tx.transaction_id,
            "amount_paid_usd": amount_usd,
            "bonus_pct": bonus_pct,
            "tokens_credited_usd": total_credit,
            "new_balance_usd": self.balance_usd,
        }

    # ------------------------------------------------------------------
    # Usage
    # ------------------------------------------------------------------

    def use_service(
        self,
        service: str | ServiceType,
        units: float = 1.0,
    ) -> dict:
        """
        Consume tokens for *units* of an AI *service*.

        Parameters
        ----------
        service : str | ServiceType
            Service identifier (e.g. "gpt", ServiceType.IMAGE_GENERATION).
        units : float
            Number of units to consume (default: 1).

        Returns
        -------
        dict
            Usage summary including cost and remaining balance.

        Raises
        ------
        InsufficientTokensError
            If the user's balance is too low.
        TokenMarketplaceError
            If *service* is not recognised.
        """
        svc = self._resolve_service(service)
        pricing = get_service_pricing(svc, self.markup)
        total_cost = round(pricing.dreamco_price_usd * units, 6)
        total_profit = round(pricing.profit_per_unit * units, 6)

        if self.balance_usd < total_cost:
            raise InsufficientTokensError(
                f"Insufficient tokens: need ${total_cost:.4f}, "
                f"have ${self.balance_usd:.4f}."
            )

        self.balance_usd = round(self.balance_usd - total_cost, 6)
        self.total_spent_usd = round(self.total_spent_usd + total_cost, 6)
        self.total_profit_usd = round(self.total_profit_usd + total_profit, 6)

        tx = self._record_transaction(
            transaction_type="usage",
            service=svc,
            units=units,
            amount_usd=total_cost,
            profit_usd=total_profit,
        )

        return {
            "transaction_id": tx.transaction_id,
            "service": svc.value,
            "units": units,
            "cost_usd": total_cost,
            "dreamco_profit_usd": total_profit,
            "remaining_balance_usd": self.balance_usd,
        }

    # ------------------------------------------------------------------
    # Reporting
    # ------------------------------------------------------------------

    def billing_summary(self) -> dict:
        """Return a high-level billing summary for this user."""
        return {
            "user_id": self.user_id,
            "balance_usd": self.balance_usd,
            "total_purchased_usd": self.total_purchased_usd,
            "total_spent_usd": self.total_spent_usd,
            "total_profit_usd": self.total_profit_usd,
            "transaction_count": len(self.transactions),
        }

    def get_transactions(
        self,
        transaction_type: Optional[str] = None,
    ) -> list[TokenTransaction]:
        """
        Return transactions, optionally filtered by *transaction_type*.

        Parameters
        ----------
        transaction_type : str | None
            'purchase', 'usage', or None for all.
        """
        if transaction_type is None:
            return list(self.transactions)
        return [t for t in self.transactions if t.transaction_type == transaction_type]

    def is_low_balance(self, threshold_usd: float = 5.0) -> bool:
        """Return True if the balance is below *threshold_usd*."""
        return self.balance_usd < threshold_usd

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _get_bundle_bonus(self, amount_usd: float) -> float:
        """Return the bonus percentage for purchasing *amount_usd* worth of tokens."""
        bonus = 0.0
        for bundle in sorted(TOKEN_BUNDLES, key=lambda b: b["usd"], reverse=True):
            if amount_usd >= bundle["usd"]:
                bonus = bundle["bonus_pct"]
                break
        return bonus

    def _resolve_service(self, service: str | ServiceType) -> ServiceType:
        """Normalise *service* to a ServiceType enum value."""
        if isinstance(service, ServiceType):
            return service
        try:
            return ServiceType(service.lower())
        except ValueError:
            raise TokenMarketplaceError(
                f"Unknown service: '{service}'. "
                f"Valid services: {[s.value for s in ServiceType]}"
            )

    def _record_transaction(
        self,
        transaction_type: str,
        service: Optional[ServiceType],
        units: float,
        amount_usd: float,
        profit_usd: float,
    ) -> TokenTransaction:
        """Create and store a transaction record."""
        self._tx_counter += 1
        tx = TokenTransaction(
            transaction_id=f"tx_{self.user_id}_{self._tx_counter:04d}",
            user_id=self.user_id,
            transaction_type=transaction_type,
            service=service,
            units=units,
            amount_usd=amount_usd,
            profit_usd=profit_usd,
        )
        self.transactions.append(tx)
        return tx
