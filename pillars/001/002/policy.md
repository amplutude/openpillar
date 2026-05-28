# C-0002 / C-0003 — Data Retention & Secure Disposal

## Purpose

This control defines the minimum retention periods for data categories and mandates secure, verifiable disposal upon expiry or at end-of-need.

## Scope

All data assets held in systems operated by or on behalf of the organisation, regardless of storage medium.

## Retention Schedule

| Data Category | Minimum Retention | Maximum Retention | Regulatory Basis |
|--------------|-------------------|-------------------|-----------------|
| Financial records | 7 years | 10 years | Corporations Act |
| Employee records | Duration of employment + 7 years | — | Fair Work Act |
| Customer PII | Duration of relationship + 2 years | 5 years | Privacy Act |
| Audit & access logs | 12 months | 3 years | ISO 27001 |
| Marketing data | Until consent withdrawn | — | Spam Act / GDPR |
| Backup snapshots | 30 days (daily), 12 months (monthly) | — | Business continuity |

## C-0002 — Retention Requirements

1. Each system **must** have a documented data retention configuration aligned to the schedule above.
2. Automated retention policies **must** be enforced at the storage layer (S3 lifecycle rules, database TTLs).
3. Data owners **must** review retention configurations annually.
4. Retention holds (e.g. for legal proceedings) override scheduled deletion and must be tracked in the legal hold register.

## C-0003 — Secure Disposal Requirements

1. Data deletion **must** render the data unrecoverable, using cryptographic erasure or verified overwrite.
2. Physical media disposal **must** follow NIST 800-88 guidelines (clear, purge, or destroy based on sensitivity tier).
3. Disposal **must** be logged and a certificate of destruction retained for 2 years.
4. Third-party processors **must** provide a written confirmation of deletion within 30 days of contract termination.

## References

- NIST SP 800-88 — Guidelines for Media Sanitisation
- ISO 27001:2022 — A.8.10 Information Deletion
- AS/NZS ISO 15489 — Records Management
