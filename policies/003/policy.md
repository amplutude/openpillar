# Multi-Factor Authentication Requirement

## 1. Purpose

This policy mandates the use of multi-factor authentication (MFA) for all access to privileged systems and sensitive organisational resources. MFA significantly reduces the risk of account compromise resulting from credential theft, phishing, or brute-force attacks.

## 2. Scope

This policy applies to all employees, contractors, and third-party personnel who access organisational systems. It covers all environments — production, staging, development, and corporate.

## 3. Mandatory MFA Systems

MFA is required without exception for the following system categories:

| System Category | Examples | MFA Required |
|-----------------|---------|--------------|
| Cloud management consoles | AWS Console, Azure Portal, GCP Console | Yes — all users |
| Single Sign-On (SSO) | Okta, Azure AD, Google Workspace | Yes — all users |
| VPN / remote access | Corporate VPN, jump hosts, bastion servers | Yes — all users |
| Source code repositories | GitHub, GitLab, Bitbucket | Yes — all users |
| Privileged access workstations | Admin consoles, database direct access | Yes — all privileged users |
| CI/CD pipelines (human authentication) | Jenkins, GitHub Actions manual triggers | Yes — all users |
| Email (corporate) | Microsoft 365, Google Workspace | Yes — all users |

## 4. Approved Authentication Factors

The second factor must be one of the following approved methods. Factors are listed in order of preference:

1. **Hardware security key** (FIDO2/WebAuthn) — e.g., YubiKey, Google Titan Key. Required for privileged access.
2. **Time-based One-Time Password (TOTP)** — e.g., Authy, Google Authenticator, 1Password TOTP. Acceptable for standard access.
3. **Push notification** — e.g., Okta Verify, Duo Push. Acceptable for standard access with number matching enabled.

> **SMS one-time passcodes are NOT acceptable** as a second factor for any privileged access or Restricted system access. SMS may be used only as a fallback for Internal-tier systems with a documented risk acceptance from the CISO.

## 5. Enrollment Requirements

- All new employees must enrol MFA within **24 hours** of account creation.
- All existing accounts not yet enrolled must complete MFA enrolment within the deadline communicated by Security Engineering.
- Each user must register a minimum of **two** approved second factors (primary + backup) to prevent lockout.
- Hardware keys must be registered by users with privileged access roles within **14 days** of role assignment.

## 6. Enforcement

- Identity Provider (IdP) policies must enforce MFA at login. Bypasses are not permitted without a formal exemption.
- Accounts that have not enrolled MFA within the required period will be **suspended automatically** after a **48-hour** grace period following formal notification.
- Service accounts and non-human identities must use certificate-based or IAM role-based authentication; MFA via interactive challenge is not applicable but equivalent controls must be applied.

## 7. Monitoring and Alerting

Security Engineering must configure alerting for:

- MFA bypass attempts or repeated authentication failures.
- Logins from new or unknown devices or geographies.
- Bulk MFA de-enrolment events.
- Service account authentication anomalies.

Alerts must be reviewed within the SLA defined in the Incident Response Plan.

## 8. Exemption Process

Requests for MFA exemptions must be:

1. Submitted in writing to Security Engineering with documented business justification and proposed compensating controls.
2. Reviewed and approved by the CISO or delegate.
3. Time-limited (maximum 30 days) and logged in the exemption register.
4. Reviewed at renewal; no exemption may be renewed more than twice without a formal risk acceptance signed by an Executive sponsor.

## 9. References

- NIST SP 800-63B — Digital Identity Guidelines: Authentication and Lifecycle Management (AAL2/AAL3)
- CIS Controls v8 — Control 6: Access Control Management
- ISO/IEC 27001:2022 Annex A Control 8.5 — Secure Authentication
- Internal: Identity & Access Management Standard
- Internal: Data Classification Standard (POL-001)
