# Orchestrator Workflow

## Role

The Orchestrator controls order, routing, file handoff, dependency locks, repair limits, state reconciliation, milestone gates, and final-report generation.

The Orchestrator is not an agent role. It does not create product requirements, design architecture, write product code, perform QA, or perform review.

## Required Release Files

A controlled release must have:

* `projects/<project-name>/<release-name>-release-plan.md`
* `projects/<project-name>/<release-name>-release-state.md`

The release plan is immutable after CEO approval except through its change-control section.

The release state is mutable and may be updated only by the Orchestrator.

No product feature may start until the release plan records CEO approval and release-state setup blockers for that feature are resolved.

All routing uses `orchestrator/handoff-contract.md`. Historical artifacts are
mapped during reconciliation and are never rewritten merely to use canonical
statuses.

## Feature Folder Modes

### Standard Implementation Folder

`projects/<project-name>/features/<feature-id>-<feature-name>/`

Contains:

* `ceo-request.md`
* `prd.md`
* `architecture.md`
* `implementation-report.md`
* `qa-report.md`
* `review-report.md`
* `final-report.md`

An approved delta retains the release-plan feature ID as its `Feature Key` and
uses the immutable change-control reference as its `Change Package`. A child
package may pass its own QA/review path, but the parent feature unlocks only
after its required package matrix, QA, review, and final-report evidence are
aggregated and reconciled.

### Existing-Code Verification Folder

Starts with:

* `ceo-request.md`
* `qa-report.md`

QA reads the master PRD, master architecture, release plan, shared memory, and scoped existing code.

If QA passes, add:

* `review-report.md`
* `final-report.md`

`prd.md`, `architecture.md`, and `implementation-report.md` remain absent and are recorded as `NOT_REQUIRED`.

If baseline QA fails, the same folder continues with:

* `prd.md`
* `architecture.md`
* `implementation-report.md`

Then QA updates `qa-report.md`, Reviewer creates or updates `review-report.md`, and the Orchestrator generates `final-report.md`.

Do not create empty placeholder artifacts.

## Workflow Entry Selection

The release plan assigns each feature an entry mode:

* `STANDARD`
* `QA_FIRST`

Use `QA_FIRST` when relevant implementation exists or partially exists.

Use `STANDARD` when the scoped capability does not exist.

The Orchestrator may confirm existence through a read-only file/code scan, but must not judge correctness. QA determines correctness.

## Standard Implementation Path

Valid transition:

`QUEUED`
→ `CEO_REQUEST_RECORDED`
→ `PRODUCT_MANAGER_RUNNING`
→ `PRD_READY`
→ `ARCHITECT_RUNNING`
→ `ARCHITECTURE_READY`
→ `DEVELOPER_RUNNING`
→ `IMPLEMENTATION_COMPLETE`
→ `QA_RUNNING`
→ `QA_PASS`
→ `REVIEWER_RUNNING`
→ `REVIEW_APPROVED`
→ `FINAL_REPORT_READY`

Stop states:

* `NEEDS_CLARIFICATION`
* `ARCHITECT_BLOCKED`
* `DEVELOPER_BLOCKED`
* `REPAIR_LIMIT_REACHED`
* `STATE_INCONSISTENT`
* `FINAL_REPORT_BLOCKED`

## Existing-Code Verification Path

Valid transition:

`QUEUED`
→ `CEO_REQUEST_RECORDED`
→ `EXISTING_QA_RUNNING`

If QA passes:

`EXISTING_QA_RUNNING`
→ `QA_PASS`
→ `EXISTING_REVIEW_RUNNING`
→ `REVIEW_APPROVED`
→ `FINAL_REPORT_READY`

The final report must record:

* Execution mode: `VERIFIED_EXISTING`
* Implementation: `NOT_REQUIRED`
* Product files changed: `None`

If baseline QA fails:

`EXISTING_QA_RUNNING`
→ `BASELINE_QA_FAIL`
→ `PRODUCT_MANAGER_RUNNING`
→ `PRD_READY`
→ `ARCHITECT_RUNNING`
→ `ARCHITECTURE_READY`
→ `DEVELOPER_RUNNING`
→ normal post-implementation QA and review

Baseline QA findings are required inputs to the delta PRD and architecture. They do not authorize scope beyond the master PRD, master architecture, and release plan.

## Bounded Repair Path

After an implementation attempt:

### QA Failure

If QA returns `STATUS: FAIL` with `Disposition: IMPLEMENTATION_DEFECT` because
the implementation does not satisfy approved requirements:

1. Record stable finding IDs.
2. Increment repair count.
3. If repair count is at most two, route to Developer.
4. Developer updates code and appends a new implementation attempt.
5. QA reruns all affected requirements and previously passing critical paths.
6. If QA passes, continue to Reviewer.

Do not consume a repair cycle or route to Developer when QA failure has another
disposition, such as ambiguous scope, missing CEO authorization, unavailable
required external access, incomplete evidence, destructive-data uncertainty, or
another mandatory stop condition. Set the matching stop state instead.

### Reviewer Changes

If Reviewer returns `STATUS: CHANGES_REQUIRED`:

1. Record stable finding IDs.
2. Increment repair count.
3. If repair count is at most two, route to Developer.
4. Developer repairs only approved findings.
5. QA reruns affected requirements.
6. Reviewer reviews again.

Route to Developer only when the required changes are implementation fixes within approved scope. Product clarification, architecture conflict requiring redesign, accepted-risk decisions, legal/deployment questions, and mandatory stop conditions require the appropriate human or upstream stage instead.

### Repair Exhaustion

When a third repair would be required:

* Set `REPAIR_LIMIT_REACHED`.
* Stop.
* Record unresolved finding IDs and required CEO action.

A CEO-approved exception is valid only when release-plan change control records
the package key, finding IDs, exact scope, revised budget, expiry, and fresh
QA/Reviewer evidence. Record its use separately from the normal `2/2` budget.

Baseline QA failure before the first implementation does not count as a repair.

## Agent Inputs and Ownership

Every agent reads `orchestrator/handoff-contract.md` and emits the required
handoff metadata in its owned artifact. The Orchestrator rejects a new or
materially updated artifact whose final status, outcome, disposition, route, or
input/evidence references cannot be reconciled.

### Product Manager

Inputs:

* `ceo-request.md`
* Master PRD and architecture references from the release plan
* Baseline `qa-report.md` when entering from existing-code failure
* Shared memory
* PRD template

Output:

* `prd.md`

Allowed statuses:

* `STATUS: NEEDS_CLARIFICATION`
* `STATUS: PRD_READY`

### Architect

Inputs:

* `prd.md`
* Master architecture reference
* Baseline QA findings when applicable
* Release plan
* Shared memory
* Architecture template

Output:

* `architecture.md`

Allowed statuses:

* `STATUS: ARCHITECTURE_READY`
* `STATUS: BLOCKED`

### Developer

Inputs:

* `prd.md`
* `architecture.md`
* Release plan/state
* Current QA/Reviewer findings when repairing
* Shared memory
* Implementation template

Output:

* Product changes
* `implementation-report.md`

Allowed statuses:

* `STATUS: IMPLEMENTATION_COMPLETE`
* `STATUS: BLOCKED`

### QA

Modes:

* `EXISTING_CODE`
* `POST_IMPLEMENTATION`

Output:

* `qa-report.md`

Allowed statuses:

* `STATUS: PASS`
* `STATUS: FAIL`

QA never modifies product code.

QA `PASS` requires the mapped Playwright happy path, relevant boundary,
bad/recovery, security/ownership, and regression evidence for the exact
reviewed commit. Desktop and mobile evidence is required for responsive work.
An unavailable environment or fixture is `FAIL` with a blocking disposition,
not a custom terminal QA status.

### Reviewer

Modes:

* `EXISTING_CODE`
* `CHANGED_CODE`

Output:

* `review-report.md`

Allowed statuses:

* `STATUS: APPROVED`
* `STATUS: CHANGES_REQUIRED`

Reviewer never modifies product code.

## Attempt Preservation Rule

An agent updating an existing report must preserve prior attempt sections.

Historical sections use:

* `Attempt Result: PASS`
* `Attempt Result: FAIL`
* `Attempt Result: APPROVED`
* `Attempt Result: CHANGES_REQUIRED`

Only one `STATUS:` line is allowed, and it must be the final line of the file.

Finding IDs remain stable across attempts.

## Final Report

The Orchestrator generates `final-report.md` only after Reviewer returns `STATUS: APPROVED`.

The report must distinguish:

* Execution mode: `VERIFIED_EXISTING` or `IMPLEMENTED`
* Implementation requirement: `NOT_REQUIRED` or `COMPLETED`
* Code state
* Database state
* Staging state
* Production state
* QA attempts
* Review attempts
* Changed files
* Migration evidence
* Remaining non-blocking risks
* Dependency unlock and milestone outcome
* CEO or milestone action required
* Reviewed commit and integrated commit (or `NOT_INTEGRATED`)
* Required Playwright IDs, outcomes, and approved manual-smoke exceptions

Allowed statuses:

* `STATUS: READY_FOR_CEO_REVIEW`
* `STATUS: BLOCKED`

## Release-Train Continuation

After a feature final report:

1. Reconcile release state.
2. Mark code/database states from evidence.
3. Unlock dependents only when the release plan’s gate is satisfied.
4. If the feature is not a milestone boundary and no stop condition exists, continue to the next eligible feature.
5. At a milestone boundary, set `MILESTONE_READY_FOR_CEO_REVIEW` and stop.

No release-train continuation may apply production migrations, production billing changes, deployment changes, or legal-document changes.

## Integrated Gate Rule

The final integrated production-readiness feature is a validation gate, not a catch-all implementation feature.

When integrated QA finds a defect:

1. Assign the finding to the primary owning feature from the release plan.
2. Reopen that feature in repair mode when its approved scope already covers the defect.
3. Run Developer, affected QA, Reviewer, and final-report updates for the owning feature.
4. Rerun the integrated gate afterward.

Create implementation work inside the integrated-gate feature only when the defect is genuinely integration-only and an approved delta PRD/architecture explicitly assigns it there.

## State Reconciliation

Before and after every transition, verify:

* Artifact exists when required for the active mode.
* Artifact ends with an allowed final status.
* Release state matches the artifact status.
* Feature dependencies satisfy the release plan.
* Only one feature is active.
* Recorded Git branch/base/head are consistent when Git is used.
* Working tree contains no unexplained cross-feature changes.
* Recorded migration checksum matches the migration file.
* Recorded staging migration matches database history when database access is available.
* Handoff-contract metadata is valid for every new or updated artifact.
* Child change-package evidence is complete before a parent feature unlocks.

If a required check fails:

* Set `STATE_INCONSISTENT`.
* Record the exact mismatch.
* Stop without guessing or modifying agent artifacts.

Run `python3 scripts/validate_workflow.py` before recording the transition. The
default report identifies legacy artifacts; new or updated handoffs must pass
the contract checks. Use `--strict` only when the selected release has been
fully migrated from legacy artifact values.

Every successful release-state change must append an immutable transition-log entry with timestamp, actor, previous/new state, evidence, and reason.

## Finding and Blocker Rules

Finding IDs use:

* `<feature-id>-QA-<number>`
* `<feature-id>-REV-<number>`

Allowed finding states:

* `OPEN`
* `FIXED_PENDING_VERIFICATION`
* `VERIFIED`
* `ACCEPTED_RISK`
* `BLOCKED`

Only the CEO may approve `ACCEPTED_RISK` for a release-blocking finding.

Blockers must record:

* Blocker ID
* Feature ID
* Reason
* Required decision or external action
* Owner
* Date
* Resolution reference

## Mandatory Stop Conditions

Stop for:

* New or conflicting product scope.
* Destructive or ambiguous data migration.
* Production database, billing, or deployment mutation.
* Benchmark-source or licensing uncertainty.
* Security behavior requiring unapproved public access.
* Legal-document changes.
* Missing CEO-controlled credentials or authorization.
* Repair-limit exhaustion.
* State inconsistency.

## Orchestrator Restrictions

The Orchestrator must not:

* Edit PRD, architecture, implementation, QA, or review content.
* Change finding outcomes.
* Mark a check as passed without evidence.
* Treat release state as proof of correctness.
* Run two active features concurrently.
* Auto-approve a milestone or production release.

## Status

STATUS: ORCHESTRATOR_WORKFLOW_DEFINED
