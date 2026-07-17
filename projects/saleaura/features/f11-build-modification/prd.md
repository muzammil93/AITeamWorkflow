# Product Requirements Document — F11 Build Modification

## Scope

Modify only the current F10 verified build from its protected session snapshot. Propose a complete, verified alternative first; apply it only after explicit confirmation.

## Requirements

* Route `build_modify` against the current protected session build snapshot.
* Support exact compatible swaps, cheaper alternatives, verified CPU/GPU upgrades or downgrades, and explicit brand/budget changes.
* Never remove a required F10 component or return a partial build.
* Calculate the smallest complete dependent-change set and validate it with the full deterministic validator.
* Keep the active snapshot until confirm; support alternatives, cancel, stale proposal, and sequential changes.
* Show customer-safe old/new component, price delta, total, stock/compatibility/budget/performance facts.
* On confirm, revalidate active stock, eligibility, compatibility, snapshot version, and CPU/GPU performance before creating the next canonical snapshot.

STATUS: PRD_READY
