# QA Baseline Report — F10 Verified Build Generation

## Existing-Code Findings — 2026-07-17

* `F10-QA-001` — The tower candidate query filters eligibility and stock but not `is_active`; archived/customer-hidden products can be selected (`BUILD-003`).
* `F10-QA-002` — Unverified CPU/GPU records can receive a fallback quality score and influence performance selection (`BUILD-006`).
* `F10-QA-003` — The generator returns the closest compatible build over the stated budget without a new explicit customer budget (`BUILD-005`).
* `F10-QA-004` — The generated card omits Cooling even though the underlying generator requires it; customers cannot see the complete verified component set (`BUILD-002`, `BUILD-007`).
* `F10-QA-005` — No canonical build record/version is persisted for an accepted generated build (`BUILD-008`).

Attempt Result: FAIL

## Verification Attempt — 2026-07-17

Evidence:

* Focused Python regression tests passed for complete under-budget snapshots, no over-budget return, customer-safe build cards, and candidate-query constraints.
* Focused TypeScript migration tests passed for the canonical snapshot table and owner RLS contract.
* TypeScript typecheck passed under the project-pinned Node 22.13.1 runtime.
* Staging migration `20260717110000_f10_verified_build_snapshots.sql` was applied and inspected: the table exists with RLS enabled and exactly two owner policies.
* Read-only staging inventory audit confirms it currently has only CPU/GPU records and no verified CPU/GPU performance matches. A full live build is therefore expected to return a truthful no-build result; staging test data was not changed to fabricate a pass.

Result: The F10 requirements are covered by deterministic unit/migration evidence. A representative eight-category staging catalog remains a release-validation dataset need, not an implementation defect.

Attempt Result: PASS

STATUS: PASS
