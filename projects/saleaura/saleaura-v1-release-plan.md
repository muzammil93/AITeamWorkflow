# SaleAura V1 Release Plan

## Control Metadata

Release ID: `SALEAURA-V1`

Plan version: `1.0`

Plan state: CEO approved

CEO approval date: 2026-07-01 (Asia/Karachi)

Master PRD:

`projects/saleaura/features/saleaura-v1-prd/prd.md`

Master architecture:

`projects/saleaura/features/saleaura-v1-prd/architecture.md`

This file defines immutable scope ownership, dependencies, entry modes, milestones, and gates. Progress belongs in `saleaura-v1-release-state.md`.

## Execution Rules

* Only one feature may be active.
* Dependencies must satisfy their integration gate before a dependent feature starts.
* `QA_FIRST` means existing behavior is validated before Developer involvement.
* Baseline QA failure routes to a delta PRD, delta architecture, and Developer.
* After implementation, at most two repair cycles are allowed.
* Every feature must pass QA and Reviewer before integration or verified-existing acceptance.
* Production database, billing, deployment, and legal-document changes require explicit CEO approval and are not authorized by this plan.

## Locked Exclusions

The following must not be introduced by any feature:

* Staff or team accounts.
* Customer accounts.
* Customer checkout, ordering, fulfilment, shipping, or store-product payment processing.
* Lead lifecycle stages or conversion pipeline.
* Self-service account deletion or owner data export.
* SaleAura Platform Operator/CEO dashboard.
* Customer-facing WhatsApp chat.
* Visible voice input or text-to-speech.
* Non-PC retail positioning.
* Office/integrated-graphics verified builds, peripherals, monitors, operating systems, multi-GPU, custom water loops, or advanced multi-storage/multi-RAM-kit optimization.
* Scheduled Google Sheets sync.
* More than one active spreadsheet/worksheet per owner.
* Owner-entered performance scores or runtime benchmark scraping.
* Legal-document content changes.
* Final hosting/deployment migration.

## Feature Dependency Plan

| ID | Feature | Entry | Dependencies | Risk | Milestone |
| --- | --- | --- | --- | --- | --- |
| F00 | Development Safety Baseline | STANDARD | None | Medium | M1 |
| F01 | Owner Identity and Onboarding | QA_FIRST | F00 | High | M1 |
| F02 | Plans, Billing, and Entitlements | QA_FIRST | F01 | Critical | M1 |
| F03 | Product Catalog and Manual Inventory | QA_FIRST | F02 | High | M2 |
| F04 | Category Compatibility and Build Eligibility | QA_FIRST | F03 | High | M2 |
| F05 | CPU/GPU Performance Reference Catalog | STANDARD | F03, F04 | High | M2 |
| F06 | Unified CSV Import Pipeline | QA_FIRST | F02, F03, F04, F05 | High | M2 |
| F07 | Google Sheets Connection and Manual Sync | QA_FIRST | F06 | High | M2 |
| F08 | Widget Platform and Anonymous Session Security | QA_FIRST | F01, F02, F03 | Critical | M3 |
| F09 | Conversation Core, Search, and Comparison | QA_FIRST | F04, F05, F07, F08 | High | M3 |
| F10 | Verified Build Generation | QA_FIRST | F09 | High | M3 |
| F11 | Build Modification | QA_FIRST | F10 | High | M3 |
| F12 | Lead Capture and Owner Notifications | QA_FIRST | F02, F08, F11 | Critical | M3 |
| F13 | Owner Dashboard | QA_FIRST | F02, F03, F08, F12 | High | M4 |
| F14 | Public Website and Product Positioning | QA_FIRST | F02, F09, F10, F11, F12, F13 | Medium | M4 |
| F15 | Integrated Production-Readiness Gate | QA_FIRST | F00, F01, F02, F03, F04, F05, F06, F07, F08, F09, F10, F11, F12, F13, F14 | Critical | M4 |

## Requirement Ownership

Each requirement has exactly one primary feature. Regression features may revalidate it but must not silently redefine it.

### F00 — Development Safety Baseline

* `BASE-001`: Preserve and checkpoint the pre-development working tree.
* `BASE-002`: Establish reproducible frontend, backend, and database check commands.
* `BASE-003`: Record existing TypeScript, lint, build, Python, and test results honestly.
* `BASE-004`: Establish isolated migration validation and shared-staging safety rules.
* `BASE-005`: Establish feature branch, commit, changed-file, and rollback evidence.
* `BASE-006`: Dry-run standard, QA-first pass/fail, bounded-repair, milestone, and reconciliation transitions without mutating production systems.

### F01 — Owner Identity and Onboarding

* `AUTH-001`: Support Google OAuth as the only V1 owner login provider.
* `AUTH-002`: Idempotently create or restore one owner profile per identity.
* `AUTH-003`: Route incomplete profiles to onboarding and complete profiles to dashboard.
* `AUTH-004`: Protect owner routes and handle expired/invalid sessions safely.
* `AUTH-005`: Provide secure logout.
* `AUTH-006`: Preserve safe OAuth redirect-host validation and provider error recovery.
* `PROFILE-001`: Validate and persist approved personal, business, and localization fields.
* `PROFILE-002`: Support later owner profile editing without duplicate records.
* `PROFILE-003`: Restrict profile reads/writes to the authenticated owner.
* `SEC-AUTH-001`: Restrict exposed auth/profile functions and grants to intended roles.

### F02 — Plans, Billing, and Entitlements

* `PLAN-001`: Preserve locked Free, Starter, and Growth prices and quotas.
* `PLAN-002`: Show current plan, usage, subscription state, and payment history.
* `BILLING-001`: Create checkout through trusted Polar server behavior.
* `BILLING-002`: Verify and deduplicate billing webhook processing.
* `BILLING-003`: Prevent unverified browser responses from granting access.
* `ENTITLEMENT-001`: Resolve active, retained-access, and unavailable modes consistently.
* `ENTITLEMENT-002`: Keep approved existing owner data accessible after expiry/cancellation.
* `ENTITLEMENT-003`: Disable widget and new metered activity after effective expiry/cancellation.
* `ENTITLEMENT-004`: Restore eligible activity after verified reactivation.
* `QUOTA-001`: Enforce inventory, lead, and AI quotas atomically and consistently.
* `SEC-PAY-001`: Remove unrestricted payment writes and protect billing event data/functions.

### F03 — Product Catalog and Manual Inventory

* `INV-001`: Use owner-scoped unique SKUs and stable legacy SKU backfill.
* `INV-002`: Preserve identity across SKU replacement through aliases.
* `INV-003`: Track manual, CSV, and Google Sheets source metadata.
* `INV-004`: Track active, manual-archive, mirror-archive, and zero-stock states.
* `INV-005`: Support manual create/edit/archive/reactivate for editable products.
* `INV-006`: Keep Google-managed products read-only in SaleAura.
* `INV-007`: Support imported URLs and Cloudinary uploads where editing is allowed.
* `INV-008`: Hide zero-stock/archived products from customers while retaining owner visibility.
* `DTO-001`: Return customer-safe product data instead of raw inventory rows.
* `SEC-INV-001`: Protect raw inventory and embeddings from unintended direct public access.

### F04 — Category Compatibility and Build Eligibility

* `COMP-001`: Validate eligibility by canonical component category.
* `COMP-002`: Define required normalized CPU, GPU, motherboard, RAM, storage, PSU, case, and cooling data.
* `COMP-003`: Return stable missing/invalid reason codes and owner guidance.
* `COMP-004`: Keep searchable and verified-build-eligible states distinct.
* `COMP-005`: Use deterministic compatibility rules rather than AI judgement.
* `COMP-006`: Treat unknown critical data as unverified, not compatible.
* `COMP-007`: Validate socket, family, RAM, storage, power, connector, clearance, format, and cooling rules.

### F05 — CPU/GPU Performance Reference Catalog

* `PERF-001`: Maintain versioned Supabase CPU/GPU reference catalogs.
* `PERF-002`: Use reviewed benchmark sources with traceable methodology and licensing notes.
* `PERF-003`: Cover common desktop consumer CPU/GPU models relevant to V1.
* `PERF-004`: Normalize canonical models and aliases deterministically.
* `PERF-005`: Verify exact matches while leaving ambiguous/unmatched products unverified.
* `PERF-006`: Keep scores system-managed and category-local.
* `PERF-007`: Use stable normalization and meaningful upgrade/downgrade thresholds.

### F06 — Unified CSV Import Pipeline

* `CSV-001`: Parse imports into one canonical product-input contract.
* `CSV-002`: Distinguish missing columns from explicitly blank cells.
* `CSV-003`: Resolve current SKU, alias, and safe source identity before insert classification.
* `CSV-004`: Update existing rows even when new-row quota is exhausted.
* `CSV-005`: Insert only permitted new rows and report quota skips.
* `CSV-006`: Validate categories and match CPU/GPU references during ingestion.
* `CSV-007`: Report inserted, updated, unchanged, failed, archived, and reactivated rows.
* `CSV-008`: Refresh embeddings only when searchable content changes.

### F07 — Google Sheets Connection and Manual Sync

* `SHEET-001`: Support one active spreadsheet and worksheet per owner.
* `SHEET-002`: Persist spreadsheet ID and worksheet GID identity.
* `SHEET-003`: Use explicit manual sync only.
* `SHEET-004`: Keep Google-managed values and images read-only in SaleAura.
* `SHEET-005`: Apply mirror archiving only after a complete safe source read.
* `SHEET-006`: Reactivate mirror-archived products when they return.
* `SHEET-007`: Preserve manual archive precedence.
* `SHEET-008`: Require confirmation for source changes and avoid silent previous-source archiving.

### F08 — Widget Platform and Anonymous Session Security

* `WIDGET-001`: Support approved branding customization and owner-scoped persistence.
* `WIDGET-002`: Provide authenticated preview and a non-secret installation snippet.
* `WIDGET-003`: Maintain exact allowed hostnames without wildcard or suffix confusion.
* `WIDGET-004`: Validate embedding origin during bootstrap rather than trusting page URL input.
* `WIDGET-005`: Exchange a signed short-lived bootstrap credential for a durable anonymous session.
* `WIDGET-006`: Bind sessions to one shop and protect session secrets.
* `WIDGET-007`: Rehydrate bounded structured history and current build state.
* `WIDGET-008`: Apply subscription availability and layered abuse controls.
* `WIDGET-009`: Hide voice recording and text-to-speech controls.
* `SEC-CHAT-001`: Remove unrestricted chat writes and protect chat/session data.

### F09 — Conversation Core, Search, and Comparison

* `CHAT-001`: Support English, Urdu, and Roman Urdu response behavior.
* `CHAT-002`: Use structured intent, action, and response contracts.
* `CHAT-003`: Search only the correct owner’s active, in-stock customer-visible products.
* `CHAT-004`: Compare inventory products without inventing missing specifications.
* `CHAT-005`: Return customer-safe product, comparison, and clarification payloads.
* `CHAT-006`: Never fabricate products, prices, stock, images, links, specifications, or compatibility.
* `CHAT-007`: Consume AI quota only for meaningful model-backed requests.

### F10 — Verified Build Generation

* `BUILD-001`: Generate GPU-based tower builds for approved V1 purposes.
* `BUILD-002`: Include CPU, discrete GPU, motherboard, RAM kit, primary storage, PSU, case, and valid cooling.
* `BUILD-003`: Use only active, in-stock, customer-visible, eligible products.
* `BUILD-004`: Validate complete compatibility deterministically.
* `BUILD-005`: Respect budget unless the customer explicitly changes it.
* `BUILD-006`: Use verified CPU/GPU scores only where performance ranking is required.
* `BUILD-007`: Return clear no-build reasons and customer-safe build cards.
* `BUILD-008`: Persist a durable canonical build snapshot and version.

### F11 — Build Modification

* `MODIFY-001`: Route `build_modify` against the current build.
* `MODIFY-002`: Support exact swap, cheaper alternative, verified upgrade/downgrade, brand, and budget changes.
* `MODIFY-003`: Prevent removal of required components.
* `MODIFY-004`: Calculate and display the smallest complete dependent-change set.
* `MODIFY-005`: Preserve the active build until explicit confirmation.
* `MODIFY-006`: Show old/new components, price delta, total, stock, compatibility, budget, and performance.
* `MODIFY-007`: Support confirm, alternatives, cancel, stale proposal, and sequential changes.
* `MODIFY-008`: Revalidate price, stock, eligibility, compatibility, version, and performance before apply.

### F12 — Lead Capture and Owner Notifications

* `LEAD-001`: Require name, at least one contact method, and explicit consent.
* `LEAD-002`: Enforce lead quota and idempotent submission.
* `LEAD-003`: Attach finalized product/build context where relevant.
* `LEAD-004`: Persist the lead before notifications.
* `LEAD-005`: Preserve existing owner email and WhatsApp notifications.
* `LEAD-006`: Do not undo a valid saved lead when notification fails.
* `LEAD-007`: Keep customer-facing WhatsApp chat out of V1.
* `SEC-LEAD-001`: Enable deliberate lead RLS and owner-scoped access.

### F13 — Owner Dashboard

* `DASH-001`: Authenticate and owner-scope every dashboard query.
* `DASH-002`: Show leads, chats/conversations, inventory, plan, and usage accurately.
* `DASH-003`: Show recent leads and existing lead analytics.
* `DASH-004`: Distinguish valid zero, empty, loading, partial failure, and unavailable states.
* `DASH-005`: Provide approved navigation and secure logout.
* `DASH-006`: Exclude lead pipeline/stages and operator dashboard.

### F14 — Public Website and Product Positioning

* `WEB-001`: Position SaleAura only for PC component businesses and custom PC builders.
* `WEB-002`: Present accurate approved capabilities and plan values.
* `WEB-003`: Remove stale Gemini/general-retail/unsupported-language or voice claims.
* `WEB-004`: Preserve correct authentication and pricing journeys.
* `WEB-005`: Leave legal routes and legal-document content unchanged.
* `WEB-006`: Do not introduce customer checkout, ordering, fulfilment, or shipping.

### F15 — Integrated Production-Readiness Gate

* `REL-001`: Validate the complete owner journey.
* `REL-002`: Validate the complete anonymous shopper journey.
* `REL-003`: Validate cross-feature authentication, ownership, RLS, quota, and entitlement boundaries.
* `REL-004`: Validate inventory-to-widget search, comparison, build, modification, and lead flow.
* `REL-005`: Validate English, Urdu, Roman Urdu, mobile, loading, empty, and failure behavior.
* `REL-006`: Pass required TypeScript, lint, build, Python, database, and targeted automated checks.
* `REL-007`: Resolve or explicitly block on critical Supabase security advisor findings.
* `REL-008`: Confirm rollback readiness and clean approved feature scope.
* `REL-009`: Confirm no legal-document, deployment, or production mutation occurred.

F15 is a validation gate, not a backlog for unfinished work. Findings must be routed to their primary feature owner. F15 implementation is permitted only for a genuinely integration-only defect covered by an approved delta PRD and architecture.

## Feature Gate

A feature unlocks dependents only when:

* Every assigned requirement passes QA.
* QA ends `STATUS: PASS`.
* Reviewer ends `STATUS: APPROVED`.
* Required tests/checks actually ran or a documented stop condition is raised.
* Relevant RLS positive/negative checks pass.
* Migration evidence matches local/staging state when applicable.
* No Critical or High finding remains open.
* The working tree and Git evidence contain only explained scope.
* Final report is generated.

## Milestones

| ID | Name | Features | Gate |
| --- | --- | --- | --- |
| M1 | Platform Foundation | F00–F02 | CEO review |
| M2 | Catalog and Inventory | F03–F07 | CEO review |
| M3 | Customer Intelligence | F08–F12 | CEO review |
| M4 | Owner and Launch Readiness | F13–F15 | Final CEO review |

## Environment and Promotion Rules

* Product changes start from a recorded clean or explicitly checkpointed base.
* Migrations are validated locally or in an isolated environment before shared staging.
* Shared staging changes require migration evidence and recovery guidance.
* Production database, billing, and deployment changes are not authorized.
* Production state remains `PRODUCTION_NOT_APPLIED` until separately approved.

## Mandatory Stops

Stop for:

* New/conflicting scope.
* Destructive or ambiguous migration.
* Benchmark-source/licensing uncertainty.
* Billing-product conflict.
* Unapproved public access.
* Legal-document or deployment change.
* CEO-controlled external authorization.
* Repair-limit exhaustion.
* State inconsistency.

## Change Control

No changes recorded.

Future changes must include:

* Change ID
* Request
* Reason
* Affected requirements/features
* Dependency/milestone impact
* CEO decision and date

## Status

STATUS: RELEASE_PLAN_CEO_APPROVED
