# User Data Selling Guide

## Overview

DataForge allows users to voluntarily contribute their data to AI/ML training datasets
and earn revenue when that data is purchased. Participation is entirely opt-in and can
be revoked at any time.

---

## How Users Can Participate

1. **Sign up** for a DataForge user account via the platform portal.
2. **Review** the data types you are willing to share (see *Data Types* below).
3. **Grant consent** for each data category you wish to monetise.
4. **Connect** any relevant accounts or data sources (optional; manual upload also supported).
5. **Monitor** your earnings dashboard in real time.

---

## Consent Process

All data sharing requires **explicit, informed, and revocable consent**:

| Step | Detail |
|------|--------|
| 1. Disclosure | Plain-language description of what data is collected and how it is used |
| 2. Granular opt-in | Separate consent checkbox for each data category |
| 3. Consent record | Timestamp, IP address, and consent text version stored immutably |
| 4. Revocation | One-click opt-out in account settings; takes effect within 24 hours |
| 5. Deletion | On revocation, your data is removed from all future datasets within 30 days |

**You will never be penalised for withdrawing consent.** Withdrawal does not affect
earnings already paid.

---

## Earnings Structure

Revenue is shared between the user (data contributor) and DreamCobots (platform) as
follows:

| Dataset Tier | User Share | Platform Share |
|--------------|-----------|----------------|
| Standard (open licence) | 60 % | 40 % |
| Premium (restricted licence) | 70 % | 30 % |
| Enterprise (custom licence) | 75 % | 25 % |

### Payment Schedule
- Earnings are calculated monthly.
- Payouts are issued on the 15th of each month via Stripe, PayPal, or crypto wallet.
- Minimum payout threshold: **$10 USD** (or equivalent).

### Earnings Calculation
```
Your earnings = (total dataset sales revenue × your data contribution %) × your tier share
```

Example: A premium dataset sells for $5,000. Your data contributes 2% of the dataset.
Your earnings = $5,000 × 0.02 × 0.70 = **$70.00**

---

## Data Types Supported

| Category | Examples | Notes |
|----------|----------|-------|
| Behavioural | Click streams, app usage patterns | Anonymised before sale |
| Textual | Product reviews, survey responses | PII stripped automatically |
| Audio | Voice samples (opted-in only) | HIPAA check applied |
| Image | Photos you upload and label | Facial data requires extra consent |
| Financial (aggregated) | Spending categories (no account numbers) | CCPA sale_opt_out respected |
| Location (coarse) | City/region level only | Precise GPS never collected |
| Item/Product | Purchase history, wish lists | Linked to consent at source |

### Data Never Collected Without Extra Consent
- Government-issued IDs
- Precise biometric data (fingerprints, retina scans)
- Medical records (PHI) — requires HIPAA authorization
- Children's data (users must be 18+)

---

## Frequently Asked Questions

**Q: Can I see exactly which datasets my data appeared in?**
A: Yes. Your account portal shows a full audit trail of every dataset containing your data.

**Q: What if a buyer misuses my data?**
A: All buyers must agree to our Data Use Agreement. Violations are reported to the
   relevant regulatory authority and the buyer is permanently banned.

**Q: Is my data identifiable?**
A: All datasets undergo anonymisation and aggregation before sale. Re-identification
   is contractually prohibited for all buyers.

**Q: How do I request deletion of all my data?**
A: Submit a deletion request from your account settings. We will process it within
   30 days (GDPR) or 45 days (CCPA).
