# QA Baseline Report — F09 Conversation Core, Search, and Comparison

## Existing-Code Findings — 2026-07-17

* `F09-QA-001` — Chat has an implicit engine response shape, but no strict public structured intent/action/response contract (`CHAT-002`, `CHAT-005` fail).
* `F09-QA-002` — AI quota is consumed before the request is classified as meaningful/model-backed (`CHAT-007` fails).
* `F09-QA-003` — Conversation history/state uses process memory rather than the F08 protected bounded session record (`CHAT-002`, `CHAT-005` fail at the session boundary).
* `F09-QA-004` — Customer-visible inventory filtering is present in the inventory service, but its response DTO/comparison boundary is not formally enforced end-to-end (`CHAT-003` through `CHAT-006` fail).
* `F09-QA-005` — English behavior exists; Urdu and Roman Urdu response behavior is not a verified deterministic contract (`CHAT-001` fails).

Attempt Result: FAIL

Attempt Result: FAIL

## Verification Attempt — 2026-07-17

Evidence:

* F09 Python tests pass for quota timing, protected bounded widget history, multilingual contract, and customer-safe response filtering.
* F09 TypeScript comparison test passes, verifying missing specifications are shown as unavailable rather than fabricated.
* Existing customer inventory query remains owner-scoped, active-only, and in-stock-only.

Result: The F09 response contract, quota timing, bounded session behavior, and comparison safety requirements are covered by deterministic regression evidence. No open F09 finding remains.

Attempt Result: PASS

STATUS: PASS
