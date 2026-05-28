# C-0001 — Data Classification Policy

## Purpose

This control establishes a mandatory framework for classifying all organisational data assets according to their sensitivity, regulatory obligations, and business value. Consistent classification is the foundation for appropriate handling, protection, and sharing of data.

## Scope

This control applies to all data created, received, stored, processed, or transmitted by the organisation, including data held by third parties on the organisation's behalf.

## Classification Tiers

| Tier | Label | Description |
|------|-------|-------------|
| 1 | **Public** | Information intended for public release. No restrictions on access or distribution. |
| 2 | **Internal** | Information for internal use only. Not for external distribution without authorisation. |
| 3 | **Confidential** | Sensitive business information. Access restricted to authorised personnel on a need-to-know basis. |
| 4 | **Restricted** | Highly sensitive information (e.g. PII, financial records, trade secrets). Strict access controls and encryption required. |

## Requirements

1. All data assets **must** be assigned a classification label at the time of creation or ingestion.
2. Classification labels **must** be applied as metadata tags in all storage systems (S3 object tags, database column metadata, document properties).
3. Data owners are responsible for maintaining correct classifications and reviewing them at least annually.
4. Downgrading a classification tier requires documented approval from the Data Governance Team.
5. Automated tools **must** scan for unclassified data quarterly and remediate within 30 days.

## Responsibilities

| Role | Responsibility |
|------|---------------|
| Data Owner | Assign and maintain classification; approve reclassification. |
| Data Steward | Enforce classification standards in systems and processes. |
| IT/Engineering | Implement technical controls to enforce classification-based access. |
| All Staff | Apply correct labels and handle data according to its tier. |

## Exceptions

Exceptions must be submitted to the Data Governance Team with a business justification and mitigating controls. Approved exceptions are logged and reviewed annually.

## References

- ISO 27001:2022 — A.5.12 Classification of Information
- NIST SP 800-53 Rev 5 — RA-2 Security Categorisation
- Internal: Data Handling Procedures v2.1
