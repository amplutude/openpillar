# Data Retention & Disposal

## 1. Purpose

This policy defines mandatory retention schedules and secure disposal requirements for all categories of organisational data. It ensures the organisation meets legal, regulatory, and contractual obligations while minimising risk associated with retaining data beyond its useful life.

## 2. Scope

This policy applies to all data assets — electronic and physical — created, received, or maintained by the organisation, including data held by third-party processors on the organisation's behalf.

## 3. Retention Schedules

Data must be retained for the minimum periods specified below. Data must be securely disposed of promptly upon expiry unless subject to a legal hold.

| Data Category | Retention Period | Basis |
|---------------|-----------------|-------|
| Financial records (invoices, ledgers, tax) | 7 years from financial year end | Statutory / tax legislation |
| Human resources records | 7 years post-employment | Employment law |
| Customer PII | Duration of relationship + 2 years | Contractual / GDPR |
| Audit and access logs | 12 months | Security / ISO 27001 |
| Contracts and agreements | 7 years post-expiry | Legal |
| Information security incident records | 3 years | Regulatory |
| Marketing consent records | Until consent withdrawn + 3 years | GDPR |
| Backup media | Aligned to primary data schedule | Operational |

Retention clocks start from the date of the last activity or transaction associated with the record unless otherwise specified.

## 4. Legal Hold Procedure

When litigation, regulatory investigation, or formal audit is reasonably anticipated:

1. The Legal or Compliance team issues a **Legal Hold Notice** identifying the affected data categories, custodians, and date range.
2. All automated deletion processes for the affected data are suspended immediately.
3. Custodians must acknowledge receipt of the Legal Hold Notice within 24 hours.
4. The hold remains in effect until formally released in writing by Legal or Compliance.
5. Data subject to a legal hold may not be deleted, altered, or migrated without prior written approval.

## 5. Secure Disposal Methods

Disposal method must be proportionate to the data classification:

| Classification | Acceptable Disposal Methods |
|---------------|----------------------------|
| Public / Internal | Standard deletion, overwrite, or recycling of physical media |
| Confidential | Cryptographic erasure (crypto-shredding) per NIST SP 800-88, or secure cross-cut shredding for physical |
| Restricted | Cryptographic erasure with key destruction, or physical destruction (degaussing + shredding) verified by authorised personnel |

**Cryptographic erasure** is the preferred method for cloud-hosted and encrypted storage. The encryption key must be irrecoverably destroyed and destruction must be logged.

**Physical media** must be disposed of via approved secure destruction vendors who provide a Certificate of Destruction.

## 6. Disposal Certificate Requirement

A Disposal Certificate must be obtained and retained for a minimum of 3 years for:

- All Confidential and Restricted data disposals.
- Any disposal involving physical media.
- Third-party-managed disposals.

Disposal Certificates must record: asset identifier, data category, disposal method, date, and name of responsible party or vendor.

## 7. Third-Party Obligations

Contracts with data processors must include retention and disposal terms consistent with this policy. Upon contract termination, processors must confirm secure disposal of all organisational data within 30 days, providing a Disposal Certificate where required.

## 8. Responsibilities

- **Data Owners** — Approve and initiate disposal of data within their domain.
- **IT / Data Custodians** — Execute disposal and obtain Disposal Certificates.
- **Legal / Compliance** — Issue and release Legal Holds; maintain the Legal Hold register.
- **Data Governance Team** — Maintain retention schedules and audit compliance annually.

## 9. References

- NIST SP 800-88 Rev 1 — Guidelines for Media Sanitisation
- ISO/IEC 27001:2022 Annex A Control 8.10 — Deletion of Information
- GDPR Article 5(1)(e) — Storage Limitation
- Internal: Data Classification Standard (POL-001)
