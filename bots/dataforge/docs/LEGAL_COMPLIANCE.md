# DataForge Legal Compliance Documentation

> **Important:** This document describes the compliance framework implemented in
> DataForge. It is not legal advice. Always consult a qualified attorney before
> processing personal data in production.

---

## GDPR Compliance

### Scope
The General Data Protection Regulation (EU) 2016/679 applies to the processing of
personal data of individuals located in the European Economic Area (EEA).

### Key Principles Implemented

| Principle | Implementation |
|-----------|---------------|
| Lawfulness / Consent | `consent_given` field required for personal data |
| Purpose Limitation | `purpose_of_processing` field required |
| Data Minimisation | Only fields required for the stated purpose are collected |
| Accuracy | Data validation at ingest; stale records purged per retention policy |
| Storage Limitation | See *Data Retention Policies* below |
| Integrity & Confidentiality | Data encrypted at rest (AES-256) and in transit (TLS 1.3) |
| Accountability | Full audit logs stored for 7 years |

### User Rights Support
- **Right to access:** users can request a copy of all stored data via the user portal.
- **Right to erasure ("right to be forgotten"):** delete requests are processed within 30 days.
- **Right to portability:** data exported in JSON or CSV on request.
- **Right to object:** users can opt out of any processing purpose at any time.

### Data Protection Officer (DPO)
A DPO must be designated before processing EEA personal data at scale.
Contact: `dpo@dreamcobots.example.com`

---

## CCPA Compliance

### Scope
The California Consumer Privacy Act (CCPA) / CPRA applies to for-profit businesses
that collect personal information of California residents meeting certain thresholds.

### Key Implementations

| Requirement | Implementation |
|-------------|---------------|
| Notice at collection | `ccpa_notice_provided` flag checked at ingest |
| Right to know | API endpoint to retrieve all data collected about a consumer |
| Right to delete | Deletion pipeline with 45-day processing window |
| Right to opt-out of sale | `sale_opt_out` flag honoured before any dataset publication |
| Non-discrimination | No service degradation for users who exercise rights |

### Do Not Sell / Do Not Share
DataForge will not include records with `sale_opt_out: true` in any published dataset.

---

## HIPAA Compliance

### Scope
The Health Insurance Portability and Accountability Act applies to covered entities
and business associates handling Protected Health Information (PHI).

### Safeguards Implemented

| Safeguard | Detail |
|-----------|--------|
| Administrative | Role-based access control; workforce training required |
| Physical | Cloud infrastructure with SOC 2 Type II certification required |
| Technical | Encryption at rest and in transit; audit logs; automatic log-off |

### PHI Fields
The following field names trigger HIPAA checks in the compliance manager:
`medical_record`, `health`, `diagnosis`, `prescription`, `ssn`

Any dataset containing these fields requires `hipaa_authorization: true` and must be
processed only under a signed Business Associate Agreement (BAA).

---

## Data Retention Policies

| Data Category | Retention Period | Disposal Method |
|---------------|-----------------|-----------------|
| Raw bot activity logs | 90 days | Secure deletion |
| Anonymised/aggregated datasets | Indefinite | N/A |
| Personal data (GDPR/CCPA) | Duration of consent + 30 days | Cryptographic erasure |
| Financial transaction records | 7 years | Secure archival then deletion |
| Audit and compliance logs | 7 years | Secure archival |
| PHI (HIPAA) | As required by law (min 6 years) | Secure deletion per BAA |

### Automated Retention Enforcement
The `ComplianceManager` tags each record with an `expires_at` timestamp based on the
applicable policy. A scheduled job runs nightly to purge expired records.

---

## Incident Response

1. Detect breach via automated anomaly detection or manual report.
2. Contain: revoke compromised credentials, isolate affected services.
3. Assess: determine scope, affected records, and applicable regulations.
4. Notify: GDPR requires notification to supervisory authority within **72 hours**;
   affected data subjects notified without undue delay.
5. Remediate and document: patch, update policies, retrain staff.
6. Post-incident review within 14 days.
