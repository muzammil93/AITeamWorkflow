# Product Requirements Document — F10 Verified Build Generation

## Scope

Return only complete, customer-safe, deterministic GPU-based tower builds for gaming, editing, office, and general usage.

## Requirements

* `BUILD-001` — Generate only GPU-based tower builds for approved V1 purposes.
* `BUILD-002` — Every returned build contains CPU, discrete GPU, motherboard, RAM, primary storage, PSU, case, and valid cooling.
* `BUILD-003` — Select only active, in-stock, build-eligible inventory. `is_active` is the V1 customer-visible state.
* `BUILD-004` — Run full deterministic validation on the final selected component map; unknown critical compatibility data fails closed.
* `BUILD-005` — Return no build when no complete verified build fits the requested budget. Explain that the customer must explicitly increase the budget.
* `BUILD-006` — Require verified positive CPU/GPU performance scores for performance-ranked build selection.
* `BUILD-007` — Return allowlisted customer-safe build cards and clear no-build messages; never expose raw inventory identifiers or internal diagnostics.
* `BUILD-008` — Persist each returned build as an immutable owner-scoped canonical snapshot at version `f10.v1`.

STATUS: PRD_READY
