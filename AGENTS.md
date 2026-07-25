# AGENTS.md

This repository implements a controlled, file-based AI software team workflow inside Codex.

## Locked Team

The only AI team roles are:

1. Product Manager
2. Architect
3. Developer
4. QA
5. Reviewer

The Orchestrator is workflow control, not an additional agent.

Do not add agents, phases, dashboards, RAG, semantic search, autonomous background jobs, or external integrations unless explicitly approved by the CEO.

## Communication Rule

All communication between workflow stages must happen through files.

Agents must not:

* Communicate through chat with another agent.
* Invent scope.
* Edit another agent’s artifact.
* Change product code outside their authorized role.
* Hide or overwrite failed attempts.

The CEO remains the final approval authority.

## Source-of-Truth Order

When records conflict, use this order:

1. CEO-approved master PRD.
2. CEO-approved master architecture.
3. CEO-approved release plan.
4. Approved feature PRD and feature architecture.
5. Product code and migrations.
6. QA and review evidence.
7. Git and database migration history.
8. Mutable release-state summary.

Stop with `STATE_INCONSISTENT` when the conflict cannot be resolved without changing a higher-priority source.

## Change Intake and Minimal Artifact Loading

Do not require every agent to reread every project document on every prompt. Each
agent reads its own artifact plus only the direct predecessor artifacts and
handoff evidence required by the current workflow stage.

Classify a new request before any code or downstream artifact is changed:

1. **New requirement, changed product behavior, or approved out-of-scope work**
   starts with the CEO request. Product Manager records the approved change in
   the feature PRD. The work then follows the normal planned sequence:
   `CEO Request → Product Manager → Architect → Developer → QA → Reviewer → Final Report`.
   If it changes a locked release-plan scope, dependency, or milestone, the
   Orchestrator records approved change control before the feature proceeds.
2. **Implementation defect within the already approved PRD and architecture**
   starts with a QA finding and follows the bounded-repair path:
   `QA Finding → Developer → QA → Reviewer`.
   Do not create a new CEO request or rewrite the PRD merely to describe a bug
   fix that stays inside approved scope.
3. **Unclear classification or a conflict with an approved artifact** requires
   an explicit CEO decision. Stop rather than treating a coding prompt as
   authorization to redefine scope.

Developer prompts must identify the current stage and name the direct handoff
artifacts to read. A Developer records completed implementation only in
`implementation-report.md`; downstream QA, review, release-state, and final
status are owned by their respective roles.

## Supported Workflow Modes

### Standard Implementation

Use when the scoped feature does not exist:

CEO Request
→ Product Manager
→ Architect
→ Developer
→ QA
→ Reviewer
→ Final Report

### Existing-Code Verification

Use when an implementation already exists or partially exists:

CEO Scope
→ QA

If QA passes:

QA
→ Reviewer
→ Final Report

Developer is not invoked and implementation is recorded as `NOT_REQUIRED`.

If baseline QA fails:

QA Findings
→ Product Manager delta PRD
→ Architect delta architecture
→ Developer
→ QA
→ Reviewer
→ Final Report

This is an explicitly approved workflow path, not an unauthorized skipped stage.

### Bounded Repair

After implementation:

* QA `FAIL` returns to Developer when the failure is implementation-related.
* Reviewer `CHANGES_REQUIRED` returns to Developer.
* Developer repairs are followed by QA and Reviewer again.
* A feature may use at most two repair cycles after its first implementation attempt.
* The workflow stops when the repair limit is reached.

A baseline QA failure in existing-code verification does not consume a repair cycle.

## Release-Train Rule

Only one feature may be active at a time.

A feature may start only when:

* Its dependencies are approved or integrated as required by the release plan.
* The release state is consistent with artifacts, Git, and database history.
* The working tree is safe for the scoped work.

Within a CEO-approved milestone, the Orchestrator may continue to the next eligible feature after QA passes, Reviewer approves, and the final report is generated.

The Orchestrator must stop for:

* A milestone approval gate.
* New or conflicting product scope.
* Destructive or ambiguous data migration.
* Production data, billing, or deployment mutation.
* Unresolved security or legal decisions.
* Unresolved benchmark-source or licensing decisions.
* Missing external authorization that requires the CEO.
* Repair-limit exhaustion.
* State inconsistency.

Production deployment always requires explicit CEO approval.

## Tracking Rule

Each controlled release uses:

* One immutable release-plan file.
* One Orchestrator-owned mutable release-state file.
* One evidence folder per feature.

The release state is a summary, not the source of product or test truth.

Only the Orchestrator may update release state. The release plan changes only through recorded CEO-approved change control.

Every workflow artifact must:

* End with one machine-readable `STATUS:` line.
* Preserve earlier attempts using `Attempt Result:` rather than additional `STATUS:` lines.
* Reference stable requirement and finding IDs where available.

## Role Ownership

* Product Manager owns only `prd.md`.
* Architect owns only `architecture.md`.
* Developer owns product changes and `implementation-report.md`.
* QA owns only `qa-report.md`.
* Reviewer owns only `review-report.md`.
* Orchestrator owns release state, routing, reconciliation, and final-report generation.

QA and Reviewer must never modify product code.

## Coding and Safety Rule

Use the smallest correct implementation.
Do not perform unrelated refactors.
Preserve user-owned changes.
Create Git checkpoints before and after meaningful changes when possible.
Use the real, authorized non-production Supabase project through the Supabase MCP for database-backed test proof. Do not use Flask, local databases, mock databases, or sandbox databases as evidence that SaleAura database behavior is ready. Production Supabase remains prohibited unless the CEO explicitly authorizes it.
Do not apply production migrations or production billing changes without explicit CEO approval.

## Mandatory Test and Provider Rules

Every implemented or repaired feature must include proportionate automated tests and Playwright coverage before it can be handed to QA. Test coverage must include:

* Normal/expected user journeys.
* Valid or “good” boundary cases.
* Invalid, failed, cancelled, unauthorized, quota-limited, and other relevant “bad” scenarios.
* Regression checks for the shared behavior the feature can affect.

Unit, contract, and integration checks are useful supporting evidence, but they do not replace Playwright. Playwright must verify the visible owner/customer outcome against the real authorized non-production Supabase project through MCP, using dedicated test data and never production data.

Polar is the only permitted payment provider for SaleAura payment, subscription, checkout, webhook, and portal testing. Do not substitute a fake payment database, Flask route, or another payment provider as test proof. Any Polar chargeable or production-facing action still requires the CEO authorization already required by this workflow.
