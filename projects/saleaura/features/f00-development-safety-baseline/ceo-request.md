# CEO Request

Begin `F00 — Development Safety Baseline` under the CEO-approved SaleAura V1 Release Plan version `1.0`.

## Authorized Scope

Deliver the six requirements assigned to F00:

* `BASE-001`: Preserve and checkpoint the pre-development working tree.
* `BASE-002`: Establish reproducible frontend, backend, and database check commands.
* `BASE-003`: Record existing TypeScript, lint, build, Python, and test results honestly.
* `BASE-004`: Establish isolated migration validation and shared-staging safety rules.
* `BASE-005`: Establish feature branch, commit, changed-file, and rollback evidence.
* `BASE-006`: Dry-run standard, QA-first pass/fail, bounded-repair, milestone, and reconciliation transitions without mutating production systems.

## Constraints

* Follow the `STANDARD` workflow assigned by the release plan.
* Do not change product behavior, production data, shared staging, billing, deployment, or legal documents.
* Preserve the clean product baseline at branch `1.0.0/1.0.0_BackednImplementation_v3`, commit `ff5a7ee`.
* Preserve the clean AI Team baseline on branch `main`, commit `6de9843`.
* Keep additions limited to development-safety commands, documentation, tests, and workflow evidence required by F00.
* Record failing or unavailable checks as evidence; do not weaken checks or claim production readiness.

## Requested Outcome

Create a repeatable, auditable safety foundation that later SaleAura feature work can use, verify it through QA and independent review, and unlock F01 only if every F00 requirement passes.

STATUS: CEO_REQUEST_CREATED
