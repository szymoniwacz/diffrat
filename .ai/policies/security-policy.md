# Security Policy

## Purpose

Set minimum security expectations for AI-assisted work in this repository.

## Rules

### Secret handling

- Never commit secrets, tokens, passwords, or private keys.
- Use environment variables or project-approved secret stores.
- Redact secrets from logs and all review artifacts, including review handoffs and PR descriptions.

### Production data

- Production data is prohibited by default in development, tests, and examples.
- Exceptional use requires explicit human approval and compliance with the project's privacy and security requirements.
- Minimize or anonymize any approved data; prefer fixtures or synthetic data.
- Never commit production data.

### Unsafe logging

- Do not log credentials, session tokens, PII, or full request payloads with sensitive fields.
- Call out new logging in security-sensitive areas for human review.

### Auth and security caution

- Treat changes to authentication, authorization, encryption, secrets handling,
  and input validation as high risk.
- Require explicit human approval before `implementation-ready` when the work
  changes security or privacy posture, authentication or authorization model,
  secret access, trust boundaries, encryption strategy, or externally visible
  security behaviour.
- Implementing an already approved security design may proceed without a new
  approval.
- Require human review before merge for security-sensitive changes.
- Prefer least privilege for permissions and API scopes.

### Dependency and supply chain

- Follow `.ai/policies/dependency-policy.md` for new packages.
- Note security-relevant dependency changes in the review handoff or PR description.

## Enforcement

High-risk changes must be flagged in review using `.ai/review/diff-risk-checklist.md`.

## Related documents

- `.ai/quality/quality-gates.md` (security gates)
- `.ai/policies/no-blind-coding.md`
- `.ai/policies/autonomy-and-authorization.md`
- `.ai/policies/dangerous-actions.md`
