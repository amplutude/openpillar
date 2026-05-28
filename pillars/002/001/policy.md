# C-0004 / C-0005 — Identity & Authentication Controls

## Purpose

This control mandates strong authentication for all organisational systems and governs the lifecycle of privileged access to reduce the risk of unauthorised access and credential compromise.

## Scope

All users, service accounts, and automated processes accessing organisational systems, infrastructure, and data.

## C-0004 — Multi-Factor Authentication (MFA) Requirement

### Requirements

1. MFA **must** be enforced for all human user accounts accessing:
   - Cloud management consoles (AWS, GCP, Azure)
   - Identity provider (IdP) and SSO systems
   - Code repositories and CI/CD pipelines
   - Administrative interfaces for production systems
   - Remote access (VPN, bastion hosts)
2. Acceptable MFA factors: TOTP authenticator apps, hardware security keys (FIDO2/WebAuthn). SMS OTP is **not** acceptable for privileged or sensitive systems.
3. MFA bypass or recovery codes **must** be stored in an approved secrets manager, not email or personal storage.
4. Accounts without MFA enrollment **must** be suspended within 48 hours of provisioning deadline expiry.

### Monitoring

- Failed MFA attempts exceeding 5 in 10 minutes trigger an automatic account lock and security alert.
- MFA enrollment coverage is reported weekly to the CISO.

## C-0005 — Privileged Access Management (PAM)

### Requirements

1. Privileged access (admin, root, superuser) **must** be granted on a just-in-time (JIT) basis with a maximum session duration of 8 hours.
2. All privileged sessions **must** be recorded and logs retained for 12 months.
3. Standing privileged access is prohibited unless a documented exception is approved by the CISO.
4. Service accounts **must** use short-lived credentials (e.g. IAM roles with STS, Workload Identity Federation) — long-lived API keys are prohibited for new integrations.
5. Privileged access reviews **must** be conducted quarterly; unused access removed within 5 business days of review completion.

### Break-Glass Procedures

Emergency break-glass accounts exist for each critical system. Their use triggers an immediate alert to the Security team and a mandatory post-use review within 24 hours.

## References

- NIST SP 800-63B — Digital Identity Guidelines
- ISO 27001:2022 — A.8.2 Privileged Access Rights
- CIS Controls v8 — Control 6: Access Control Management
