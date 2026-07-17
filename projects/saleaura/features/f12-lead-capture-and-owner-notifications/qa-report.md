# QA Baseline Report — F12 Lead Capture and Owner Notifications

* `F12-QA-001` — Sharing contact data implicitly grants consent; V1 requires explicit consent (`LEAD-001`).
* `F12-QA-002` — Duplicate handling depends on process-memory session state rather than a durable idempotency key (`LEAD-002`).
* `F12-QA-003` — Saved leads do not attach finalized product/build context (`LEAD-003`).
* `F12-QA-004` — Existing persistence-before-notification and notification-failure behavior are correct, but need regression coverage (`LEAD-004`–`LEAD-006`).

Attempt Result: FAIL

## Verification Attempt — 2026-07-17

* Explicit-consent and F12 migration regressions pass in the focused suite.
* TypeScript typecheck and Python syntax checks pass.
* Staging migration `20260717130000_f12_lead_idempotency_context.sql` applied; `idempotency_key` and `context_json` columns verified.

Attempt Result: PASS

STATUS: PASS
