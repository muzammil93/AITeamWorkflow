# Orchestrator State Model

## Purpose

This file defines valid workflow, code, database, release, stop, and reconciliation states.

Project-specific mutable state belongs in the project release-state file. This file is a state-model definition, not a live feature tracker.

## Global Mode

Mode: Usage

Capabilities:

* Standard implementation
* Existing-code QA-first verification
* Delta implementation after baseline QA failure
* Two bounded repair cycles
* Dependency-locked release trains
* Milestone approval gates
* State reconciliation

## Workflow States

### Release Setup

* `SETUP_REQUIRED`
* `RELEASE_PLAN_READY`
* `RELEASE_PLAN_CEO_APPROVED`

### Queue and Dependency

* `QUEUED`
* `BLOCKED_DEPENDENCY`
* `CEO_REQUEST_CREATED`

### Existing-Code Verification

* `EXISTING_QA_RUNNING`
* `BASELINE_QA_FAIL`
* `EXISTING_REVIEW_RUNNING`

### Standard and Delta Delivery

* `PRODUCT_MANAGER_RUNNING`
* `PRD_READY`
* `ARCHITECT_RUNNING`
* `ARCHITECTURE_READY`
* `DEVELOPER_RUNNING`
* `IMPLEMENTATION_COMPLETE`
* `QA_RUNNING`
* `QA_PASS`
* `QA_FAIL`
* `REVIEWER_RUNNING`
* `REVIEW_APPROVED`
* `REVIEW_CHANGES_REQUIRED`
* `FINAL_REPORT_READY`

### Release

* `READY_FOR_NEXT_FEATURE`
* `MILESTONE_READY_FOR_CEO_REVIEW`
* `MILESTONE_CEO_APPROVED`
* `RELEASE_READY_FOR_CEO_REVIEW`
* `RELEASE_CEO_APPROVED`

## Code States

* `NOT_STARTED`
* `EXISTING_UNVERIFIED`
* `VERIFIED_EXISTING`
* `FEATURE_BRANCH`
* `READY_TO_INTEGRATE`
* `INTEGRATED`

Code state does not imply deployment.

## Database States

* `NOT_REQUIRED`
* `PLANNED`
* `LOCAL_VALIDATED`
* `STAGING_APPLIED`
* `STAGING_VERIFIED`
* `PRODUCTION_NOT_APPLIED`
* `PRODUCTION_APPLIED`

`PRODUCTION_APPLIED` requires recorded CEO authorization.

## Finding States

* `OPEN`
* `FIXED_PENDING_VERIFICATION`
* `VERIFIED`
* `ACCEPTED_RISK`
* `BLOCKED`

## Stop States

* `NEEDS_CLARIFICATION`
* `ARCHITECT_BLOCKED`
* `DEVELOPER_BLOCKED`
* `REPAIR_LIMIT_REACHED`
* `STATE_INCONSISTENT`
* `MIGRATION_BLOCKED`
* `SECURITY_BLOCKED`
* `EXTERNAL_AUTH_REQUIRED`
* `CEO_DECISION_REQUIRED`
* `FINAL_REPORT_BLOCKED`

## Standard Transition

`QUEUED`
→ `CEO_REQUEST_CREATED`
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

## Existing-Code Pass Transition

`QUEUED`
→ `CEO_REQUEST_CREATED`
→ `EXISTING_QA_RUNNING`
→ `QA_PASS`
→ `EXISTING_REVIEW_RUNNING`
→ `REVIEW_APPROVED`
→ `FINAL_REPORT_READY`

Code state becomes `VERIFIED_EXISTING`.
Database state reflects verified existing state or `NOT_REQUIRED`.

## Existing-Code Failure Transition

`EXISTING_QA_RUNNING`
→ `BASELINE_QA_FAIL`
→ `PRODUCT_MANAGER_RUNNING`
→ `PRD_READY`
→ `ARCHITECT_RUNNING`
→ `ARCHITECTURE_READY`
→ `DEVELOPER_RUNNING`
→ `IMPLEMENTATION_COMPLETE`
→ `QA_RUNNING`

Baseline QA failure does not consume a repair cycle.

## Repair Transitions

Repair transitions apply only to implementation defects within approved scope. Ambiguous requirements, CEO-controlled authorization, destructive-data uncertainty, security/product decisions, legal/deployment questions, and external-access blockers transition to the corresponding stop state without incrementing repair count.

### QA Repair

`QA_FAIL`
→ `DEVELOPER_RUNNING`
→ `IMPLEMENTATION_COMPLETE`
→ `QA_RUNNING`

### Review Repair

`REVIEW_CHANGES_REQUIRED`
→ `DEVELOPER_RUNNING`
→ `IMPLEMENTATION_COMPLETE`
→ `QA_RUNNING`
→ `QA_PASS`
→ `REVIEWER_RUNNING`

Maximum repair count: 2.

When another repair is required after count 2:

→ `REPAIR_LIMIT_REACHED`

## Final Report Transition

After `REVIEW_APPROVED`:

→ `FINAL_REPORT_READY`

Then:

* `READY_FOR_NEXT_FEATURE` when milestone continuation is allowed.
* `MILESTONE_READY_FOR_CEO_REVIEW` at milestone boundary.
* `RELEASE_READY_FOR_CEO_REVIEW` after the final release gate.

## Reconciliation Rule

Before and after each transition, compare:

* Release-plan dependency and entry mode
* Project release state
* Required artifact presence
* Artifact final status
* Repair count
* Git state when applicable
* Migration file checksum and recorded database history when applicable

Any unexplained mismatch transitions to:

`STATE_INCONSISTENT`

No automatic recovery is allowed from state inconsistency.

## Transition Log Rule

Every project release-state change must append a transition entry containing:

* Transition ID
* Timestamp and timezone
* Actor
* Previous state
* New state
* Artifact/evidence references
* Reason

Do not rewrite or delete earlier transition entries.

## Single-Writer Rule

Only the Orchestrator updates project release state.

Agents update only their owned artifact. Product code is modified only by Developer in an authorized implementation or repair stage.

## Current Global State

No product feature is active in this state-model file.

Project-specific current state:

`projects/<project-name>/<release-name>-release-state.md`

## Status

STATUS: ORCHESTRATOR_STATE_DEFINED
