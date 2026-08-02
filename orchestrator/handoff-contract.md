# Workflow Handoff Contract

## Purpose

This contract makes file-based handoffs routable without replacing the existing
human-readable reports. It applies to workflow artifacts created or materially
updated on or after 2026-08-02. Historical artifacts remain evidence and must
not be rewritten merely to meet this contract.

## Required Metadata

Every new or updated workflow artifact must contain one `## Handoff Metadata`
section near the start of the document with these exact fields:

```md
Handoff Contract: `v1`
Feature Key: `F16`
Change Package: `BASE` or `F16-CC005`
Attempt: `1`
Outcome: `PASS`
Disposition: `READY`
Next Route: `REVIEWER`
Requirement IDs: `CART-001`, `CART-002`
Evidence IDs: `E2E-033`, `E2E-034` or `NOT_APPLICABLE`
Input Revisions: `prd.md@<commit-or-checksum>`
```

`Feature Key` is the release-plan feature ID. `Change Package` is `BASE` for
the original feature scope or the immutable release-plan change-control key for
an approved delta. A child package does not independently unlock its parent.

`Outcome` must exactly equal the artifact's final `STATUS:` value without the
`STATUS:` prefix. The final `STATUS:` line remains the only terminal parser
signal; metadata supplies the reason and route.

## Canonical Artifact Statuses

| Artifact | Allowed final status |
| --- | --- |
| `ceo-request.md` | `CEO_REQUEST_RECORDED` |
| `prd.md` | `PRD_READY`, `NEEDS_CLARIFICATION` |
| `architecture.md` | `ARCHITECTURE_READY`, `BLOCKED` |
| `implementation-report.md` | `IMPLEMENTATION_COMPLETE`, `BLOCKED` |
| `qa-report.md` | `PASS`, `FAIL` |
| `review-report.md` | `APPROVED`, `CHANGES_REQUIRED` |
| `final-report.md` | `READY_FOR_CEO_REVIEW`, `BLOCKED` |

Older terminal values are legacy evidence. The Orchestrator maps them during
reconciliation, records the mapping in release state, and never silently treats
them as a canonical pass.

## Disposition and Routing

Use one of these dispositions:

* `READY` — all requirements and evidence for the stage are complete.
* `IMPLEMENTATION_DEFECT` — approved-scope defect; may route to Developer.
* `SCOPE_DECISION` — product or architecture decision is required; stop for CEO.
* `EXTERNAL_AUTH` — credentials, provider, test account, or approved access is missing.
* `INCOMPLETE_EVIDENCE` — required QA evidence has not run or is insufficient.
* `MIGRATION_SAFETY` — unsafe or unreconciled database change.
* `SECURITY` — unresolved authorization, data-handling, or public-access risk.
* `REPAIR_LIMIT` — normal repair allowance is exhausted.
* `STATE_INCONSISTENT` — sources cannot be reconciled.

For QA, `FAIL` does not by itself authorize a repair. Only `Outcome: FAIL` with
`Disposition: IMPLEMENTATION_DEFECT` can route to Developer. Every other
failing disposition routes to the matching stop state or CEO action without
consuming a repair cycle.

## QA Evidence Contract

Every QA attempt maps each scoped requirement to named evidence. For a
customer- or owner-visible change, evidence must include Playwright against the
authorized non-production environment:

* at least one happy path;
* relevant valid boundary or empty/retry path;
* relevant invalid, failed, cancelled, unauthorized, expired, replayed, or
  quota-limited path;
* affected security/ownership and regression paths; and
* desktop and mobile coverage whenever the changed journey is responsive.

Each matrix row records its requirement ID, Playwright test ID, fixture/owner,
result, evidence location, and whether QA executed it independently or reviewed
a valid recorded run. Unit, contract, integration, or database checks support
but never replace required Playwright evidence.

An unavailable test account, provider action, or environment is
`Outcome: FAIL` with `Disposition: EXTERNAL_AUTH` or
`INCOMPLETE_EVIDENCE`; it is never a pass. A provider-hosted action that cannot
be automated needs an explicit CEO-approved manual-smoke exception with the
manual evidence and the affected Playwright ID.

## Staging Fixture Safety

Before a mutating Playwright run, record the dedicated fixture/owner, allowed
records, expected mutation, pre-run counts/state, and cleanup procedure. Do not
run broad deletes, resets, or plan/profile changes against shared owner data.
After the run, verify cleanup with safe IDs/counts/state and retain failed-run
traces. Stop the affected path if a required fixture or isolated owner is
unavailable.

## Repair Exceptions

The normal repair budget remains two cycles. A CEO-approved exception must be
recorded in immutable release-plan change control before work starts and include
the package key, finding IDs, exact scope, revised budget, expiry, and required
fresh QA/Reviewer checks. Release state displays normal and exceptional budgets
separately, for example `2/2 + CC-004: 1/1`.

## Integration Evidence

Before a final report can claim integration, record the reviewed commit, the
integrated commit (or `NOT_INTEGRATED`), required check results, and applicable
migration version/checksum. `READY_TO_INTEGRATE` is not `INTEGRATED`.

## Validation

Run the read-only validator before a release-state transition:

```bash
python3 scripts/validate_workflow.py
python3 scripts/validate_workflow.py --strict
```

The default command reports legacy artifacts as warnings. `--strict` fails on
legacy values, malformed current-contract metadata, non-terminal statuses, and
unknown statuses. The validator does not modify artifacts or release state.
