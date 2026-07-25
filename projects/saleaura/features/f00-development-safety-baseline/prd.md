# Product Requirements Document

## Feature Name

Development Safety Baseline

## Feature ID and Execution Mode

`F00` — `STANDARD`

## CEO Request

Begin the first SaleAura V1 release feature and establish the reproducible, auditable development-safety foundation required before product hardening starts.

Reference: `projects/saleaura/features/f00-development-safety-baseline/ceo-request.md`.

## Master Requirement References

* SaleAura V1 Release Plan v1.0: `BASE-001` through `BASE-006`.
* Master PRD production-readiness requirements for honest validation, type safety, testing, and no deployment migration.
* Master architecture testing guidance, additive-migration safety, delivery governance, and baseline/contract-freeze implementation slice.

## Dependency References

F00 has no feature dependencies. Release setup blockers `B-001`, `B-002`, and `B-003` are resolved. The reconciled baselines are:

* Product repository: branch `1.0.0/1.0.0_BackednImplementation_v3`, commit `ff5a7ee`.
* AI Team repository: branch `main`, commit `6de9843` before F00 activation.

## Baseline QA Findings

`NOT_APPLICABLE` — F00 uses the standard implementation path.

## Clarifying Questions

No clarification required.

## Finalized Scope

### In Scope

* Preserve an auditable record of both pre-development repository baselines.
* Provide one documented canonical command for each of:
  * TypeScript type checking.
  * Frontend linting.
  * Production frontend build.
  * Python source compilation.
  * Python automated test discovery.
  * Complete repository baseline execution.
* Make the commands use repository-pinned dependencies and avoid network or production mutations after dependencies are installed.
* Execute the baseline commands and record their actual success, failure, or unavailability without suppressing errors.
* Document the authorized staging-Supabase-MCP migration/test validation sequence and explicit rules for production.
* Define required evidence for feature branches, base/head commits, changed files, checks, migration checksums, recovery, and unrelated-work preservation.
* Exercise the file-based workflow state model with non-mutating dry-run scenarios for:
  * Standard success.
  * QA-first existing-code success.
  * QA-first baseline failure and delta implementation.
  * QA repair.
  * Reviewer repair.
  * Repair-limit exhaustion.
  * Milestone gate.
  * State reconciliation failure.
* Add focused automated tests for safety helpers if executable helper logic is introduced.

### Out of Scope

* Fixing historical TypeScript, lint, build, Python, or product-test failures discovered by the baseline.
* Removing Next.js ignored-error configuration before the application passes the relevant checks.
* Implementing any F01–F15 product behavior.
* Creating or applying a SaleAura V1 database migration.
* Applying a product migration or mutating shared staging as part of F00; F00 documents the authorized staging-MCP sequence for later feature work.
* Any production database, billing, deployment, or legal-document change.
* Adding or operating Playwright as part of F00 itself; later implemented or repaired product features must use the approved Playwright plan. CI provider, new AI agent, dashboard, background job, or external integration work remains out of scope.
* Rewriting existing product setup documentation unrelated to the safety baseline.

## Assumptions

* `pnpm-lock.yaml` is the authoritative frontend dependency lock.
* Python 3.11 remains the supported target even if local validation runs on a newer compatible interpreter and records that fact.
* The repository may have no product unit tests yet; zero discovered tests must be reported honestly and must not be described as test coverage.
* Database validation may remain documented and unexecuted during F00 because no migration is owned by F00.
* A small repository-native command runner or script is acceptable when it directly provides the required reproducibility and does not add a runtime dependency.
* Dry-run transition validation operates on in-memory fixtures or temporary files and must not edit the live release state.

## User Stories

* As a developer, I want one reliable set of commands so I can validate every later feature consistently.
* As QA, I want check results with exit codes and environment facts so I can distinguish passing evidence from missing evidence.
* As a reviewer, I want branch, commit, changed-file, migration, and recovery records so I can audit feature boundaries.
* As the CEO, I want database-backed readiness proof to use the authorized staging Supabase MCP project and dedicated test data, while production remains protected.
* As the Orchestrator, I want workflow transitions dry-run against the locked state model so invalid routing is caught before product features depend on it.

## Functional Requirements

### `BASE-001` — Pre-development baseline

1. Record the product repository path, branch, baseline commit, and clean/dirty state before F00 product changes.
2. Record the AI Team repository path, branch, activation commit, and clean/dirty state.
3. Preserve unrelated work; no destructive reset, checkout, or cleanup may be used.

### `BASE-002` — Reproducible checks

1. Expose named, documented commands for frontend types, lint, build, Python compile, Python tests, workflow transition dry-run, and the aggregate baseline.
2. Commands must return a non-zero exit status when their underlying check fails.
3. Commands must not install dependencies implicitly, use production credentials, mutate databases, or hide output needed to diagnose failure.
4. Python compilation must exclude generated caches and virtual environments.
5. Python test discovery must use the standard-library test runner unless a later approved feature changes the test architecture.

### `BASE-003` — Honest current results

1. Run each applicable baseline command in the actual F00 environment.
2. Record command, runtime/tool version where relevant, exit result, and concise actual outcome.
3. Dependency absence, no discovered tests, configuration deprecation, or pre-existing failures must be reported explicitly.
4. An aggregate failure caused by known baseline debt is evidence and does not by itself require expanding F00 into product repair.

### `BASE-004` — Migration isolation and shared safety

1. Document an authorized staging-Supabase-MCP validation flow for future additive migrations and database-backed feature tests, using dedicated test data and verified environment identity.
2. Require checksum capture and schema/security verification for migrations.
3. Forbid rewriting an applied migration.
4. Forbid staging migration application until MCP environment verification, review, backup/recovery planning, and explicit feature authorization are recorded.
5. Forbid production migration application without explicit CEO authorization.
6. State that rollback is not assumed safe; prefer a reviewed forward fix when data may have changed.

### `BASE-005` — Git and recovery evidence

1. Require expected base branch/commit, feature branch, pre-existing changes, changed-file list, checkpoint/head commit, and diff verification.
2. Require a migration checksum and recovery plan when a feature owns database changes.
3. Require exact restore/revert guidance based on recorded commits while prohibiting destructive commands that could discard user work.
4. Require evidence to distinguish AI Team artifact commits from product commits.

### `BASE-006` — Workflow dry-run

1. Validate only transitions defined by the locked Orchestrator state model.
2. Verify the eight in-scope scenarios without changing the live release-state file or external systems.
3. Reject invalid transitions and multiple simultaneously active features.
4. Verify a dependency cannot start before its prerequisite gate.
5. Produce deterministic automated output suitable for later regression use.

## Acceptance Criteria

1. `BASE-001` passes when both repository baselines and their clean/dirty states are recorded before product changes, and QA confirms no unrelated work was discarded.
2. `BASE-002` passes when all seven named check categories are documented, runnable from a fresh repository with installed locked dependencies, and preserve underlying non-zero exits.
3. `BASE-003` passes when the implementation report contains actual F00 results for TypeScript, lint, build, Python compile, Python tests, and workflow tests, including failures or unavailable checks.
4. `BASE-004` passes when the safety documentation defines authorized staging-MCP validation, checksum, RLS/security inspection, staging authorization, production prohibition, and forward-fix/recovery rules without applying a migration.
5. `BASE-005` passes when QA can reconstruct the F00 base, branch/checkpoint, changed files, validation evidence, and safe reversal boundary from recorded evidence.
6. `BASE-006` passes when an automated test command exercises all eight scenarios, rejects invalid routing, and leaves the live release state byte-for-byte unchanged.
7. No product behavior, database, shared staging, production, billing, deployment, or legal content is changed.

## Risks / Open Questions

* The current frontend lockfile exists but `node_modules` may be absent, making frontend results initially unavailable until the locked dependencies are installed. This must be recorded, not papered over.
* The current `next lint` command may be incompatible with or deprecated by the installed framework toolchain; a failing result should guide a minimal canonical lint command rather than suppress linting.
* Existing frontend debt may make typecheck or build fail. Repair belongs to the owning later feature unless the failure is caused by F00’s own safety implementation.
* The connected staging Supabase MCP may be unavailable. Because F00 owns no migration, documentation and dry-run safety checks are acceptable; the first migration-owning feature must execute the authorized staging-MCP flow when access is available.

## Status

STATUS: PRD_READY
