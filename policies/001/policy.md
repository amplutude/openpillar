# Data Classification Standard

## 1. Purpose

This policy establishes a mandatory framework for classifying all organisational data assets according to their sensitivity, business value, and regulatory obligations. Consistent classification ensures that data is handled, protected, and shared in a manner proportionate to the risk it represents.

## 2. Scope

This policy applies to all employees, contractors, third-party vendors, and systems that create, store, process, or transmit data on behalf of the organisation.

## 3. Classification Tiers

All data must be assigned one of the following four classification tiers at the point of creation or ingestion:

| Tier | Label | Description | Examples |
|------|-------|-------------|---------|
| 1 | **Public** | Information approved for unrestricted external release. No harm if disclosed. | Marketing materials, press releases, published documentation |
| 2 | **Internal** | Information intended for general internal use. Limited harm if disclosed externally. | Internal procedures, project plans, general HR communications |
| 3 | **Confidential** | Sensitive business or personal information. Significant harm if disclosed. | Financial reports, customer PII, employee records, contracts |
| 4 | **Restricted** | Highly sensitive information. Severe or irreversible harm if disclosed. | Authentication credentials, cryptographic keys, regulated health data, M&A data |

## 4. Labelling Requirements

- All documents, files, and datasets must carry a visible classification label in the header or file metadata.
- Electronic files must have classification embedded in document properties or file naming convention (e.g., `[CONFIDENTIAL]_report.pdf`).
- Emails containing Confidential or Restricted information must include the classification tier in the subject line.
- Systems processing Restricted data must enforce access controls commensurate with the tier.

## 5. Handling Requirements

| Tier | Storage | Transmission | Access Control | Retention |
|------|---------|--------------|----------------|-----------|
| Public | Any approved system | Plain or encrypted | No restriction | Per retention schedule |
| Internal | Approved internal systems | Encrypted in transit | Authenticated employees | Per retention schedule |
| Confidential | Encrypted at rest | TLS 1.2+ | Role-based, need-to-know | Per retention schedule |
| Restricted | Encrypted at rest, isolated environments | End-to-end encrypted | Strict need-to-know, MFA required | Per retention schedule, legal hold aware |

## 6. Responsibilities

- **Data Owners** — Responsible for assigning and reviewing the classification of data assets within their domain.
- **Data Custodians** — Responsible for applying technical controls consistent with the assigned classification.
- **All Staff** — Responsible for handling data in accordance with its classification label and this policy.
- **Data Governance Team** — Responsible for maintaining this policy and providing guidance on classification disputes.

## 7. Reclassification

Data classification must be reviewed whenever the data's context, sensitivity, or regulatory status changes. Downgrade of Restricted data requires written approval from the Data Owner and the Chief Information Security Officer.

## 8. Exceptions

Requests for exceptions to this policy must be submitted to the Data Governance Team with documented business justification and compensating controls. Exceptions are valid for a maximum of 12 months and must be reviewed on renewal.

## 9. References

- ISO/IEC 27001:2022 Annex A Control 5.12 — Classification of Information
- NIST SP 800-53 Rev 5 — RA-2 Security Categorization
- GDPR Article 32 — Security of Processing
- Internal: Data Handling Procedures Guide v2.1
