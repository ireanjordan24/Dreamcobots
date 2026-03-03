# BuddyAI — Autonomous Financial System

This directory contains the central AI code to manage and communicate with all bots,
plus a complete **autonomous financial system** that lets Buddy process payments,
distribute earnings, issue cards, and surface real-time metrics to clients.

---

## Directory Structure

```
BuddyAI/
├── financial/          # Core financial engine
│   ├── models.py       # Data models (Account, Transaction, Card, Earning)
│   ├── transactions.py # Transfer & payment processing
│   ├── earnings.py     # 50/50 earnings distribution
│   └── cards.py        # Card issuance & payment processing
├── dashboard/          # Client dashboard
│   ├── metrics.py      # Profitability, compute usage, task metrics
│   ├── stress_test.py  # System stress-testing
│   └── dashboard.py    # Unified ClientDashboard
└── tests/
    ├── test_financial.py
    └── test_dashboard.py
```

---

## Quick Start

```python
from BuddyAI.financial import Account, TransactionProcessor, EarningsDistributor, CardProcessor
from BuddyAI.dashboard import ClientDashboard

# 1. Create accounts
buddy_account = Account(owner_id="buddy", owner_name="Buddy", is_autonomous=True)
client_account = Account(owner_id="client-1", owner_name="Alice")

# 2. Process a transfer
processor = TransactionProcessor()
processor.register_account(buddy_account)
processor.register_account(client_account)
client_account.deposit(1000.0)
txn = processor.transfer(client_account.account_id, buddy_account.account_id, 50.0)
print(txn.status)   # TransactionStatus.COMPLETED

# 3. Distribute earnings (50/50 split)
distributor = EarningsDistributor(buddy_account=buddy_account)
earning, buddy_txn, client_txn = distributor.distribute(
    client_account=client_account,
    gross_amount=200.0,
    source="autonomous_task",
)
# buddy_account.balance += 100.0, client_account.balance += 100.0

# 4. Issue a card and process a card payment
card_processor = CardProcessor()
card = card_processor.issue_card(client_account, cardholder_name="Alice", spending_limit=500.0)
charge_txn = card_processor.charge_card(
    card.card_id, client_account, buddy_account, amount=25.0
)

# 5. View the dashboard
dashboard = ClientDashboard(
    client_id="client-1",
    client_name="Alice",
    account=client_account,
)
dashboard.metrics.record_task("t1", "web_scrape", duration_seconds=3.2)
dashboard.metrics.record_compute_snapshot(cpu_percent=42.5, memory_percent=58.0)
dashboard.metrics.record_earning(100.0)
dashboard.print_summary()
data = dashboard.render()   # JSON-ready dict for any frontend
```

---

## Financial System

### Transaction Processing (`transactions.py`)

The `TransactionProcessor` is the core engine. It supports:

| Method | Description |
|---|---|
| `register_account(account)` | Enrol a new account |
| `transfer(sender_id, recipient_id, amount)` | Move funds between accounts |
| `process_payment(payer_id, payee_id, amount)` | Record a service payment |
| `refund(transaction_id)` | Reverse a completed transaction |
| `get_account_transactions(account_id)` | Full history for an account |

### Earnings Distribution (`earnings.py`)

`EarningsDistributor` enforces the **50/50 split** in all modes:

- **Autonomous mode** — Buddy keeps 50 %; client receives 50 %.
- **Compute-share mode** — client earns 50 % of compute-derived profits; Buddy retains 50 %.

```python
# Autonomous mode
earning, _, _ = distributor.distribute(client_account, gross_amount=400.0)

# Compute-share mode
earning, _, _ = distributor.distribute_compute_share(client_account, compute_profit=300.0)
```

### Card Payments (`cards.py`)

Clients can sign up for a virtual or physical card:

```python
card = card_processor.issue_card(
    account=client_account,
    cardholder_name="Alice",
    card_type="virtual",   # or "physical"
    spending_limit=1000.0,
)
card_processor.charge_card(card.card_id, payer_account, payee_account, amount=99.99)
card_processor.suspend_card(card.card_id)
card_processor.cancel_card(card.card_id)
```

**Security notes:**
- Full card PANs are never stored; only the last four digits are retained.
- Card IDs are UUIDs; no sequential or guessable identifiers are used.
- Spending limits are enforced on every charge attempt.

---

## Client Dashboard

### Metrics (`metrics.py`)

```python
metrics = MetricsCollector(client_id="alice-001")
metrics.record_task("t1", "fetch_data", duration_seconds=2.1)
metrics.record_compute_snapshot(cpu_percent=55.0, memory_percent=70.0)
metrics.record_earning(amount=50.0)
print(metrics.summary())
```

### Stress Testing (`stress_test.py`)

```python
runner = StressTestRunner()
result = runner.run(
    target=my_callable,
    test_name="payment_processing",
    iterations=1000,
)
print(result.ops_per_second, result.success_rate)
```

### Dashboard (`dashboard.py`)

`ClientDashboard` aggregates everything into one render call:

```python
data = dashboard.render()
# Returns a JSON-serialisable dict with:
#   profitability / earnings_timeline
#   compute_usage / snapshots
#   tasks / records
#   stress_tests
#   visualizations (cpu_over_time, memory_over_time, earnings_over_time)
```

The `visualizations` section produces `{x, y}` series compatible with
Chart.js, Plotly, Recharts, or any other charting library.

---

## Running Tests

```bash
cd Dreamcobots
pip install pytest
python -m pytest BuddyAI/tests/ -v
```

All 66 tests should pass.

---

## Security & Compliance Considerations

- Card PANs are never stored in plaintext.
- All monetary values are `float` rounded to 2 decimal places to prevent
  floating-point accumulation errors in accounting contexts.
  For production use, replace `float` with Python's `decimal.Decimal`.
- Input validation is enforced throughout (negative amounts, zero transfers,
  invalid card types, etc.).
- For production deployment, integrate with a regulated payment processor
  (e.g. Stripe, Marqeta) and apply PCI-DSS controls before handling real card data.

---

## Integration Guidelines for Buddy's Financial Operations

1. **Bootstrap accounts** — create a `buddy_account` (`is_autonomous=True`) at
   system start and persist its `account_id`.
2. **Register client accounts** — call `processor.register_account()` when a
   new client signs up.
3. **Hook earnings events** — after each completed autonomous task, call
   `distributor.distribute()` with the gross revenue; both accounts are
   credited automatically.
4. **Issue cards on sign-up** — clients opting into the financial system
   receive a virtual card via `card_processor.issue_card()`.
5. **Expose the dashboard** — serialise `dashboard.render()` and serve it
   to the client's frontend (REST endpoint, WebSocket push, etc.).
6. **Run stress tests periodically** — schedule `stress_runner.run()` against
   critical paths (payment processing, distribution) to catch regressions.