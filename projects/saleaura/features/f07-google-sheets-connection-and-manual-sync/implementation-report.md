# Implementation Report — F07 Google Sheets Connection and Manual Sync

## Feature and Workflow Position

`F07 — Google Sheets Connection and Manual Sync`

Execution mode: `BOUNDED_REPAIR_AFTER_QA_FIRST_BASELINE_FAILURE`

Required sequence completed by the Software team:

`CEO request → QA baseline failure → approved F07 follow-up PRD → approved F07 architecture → Developer implementation → QA handoff`

This report is the Developer-owned record. It does not mark the feature QA-verified, Reviewer-approved, integrated, or production-ready.

## Controlling Requirements and Reconciliation

The implementation follows the approved F07 follow-up PRD and the CEO-confirmed operating rules supplied with this repair. The operational result is:

| Concern | Implemented behavior |
| --- | --- |
| Sheet identity | A non-empty, unique Sheet `SKU` or `Product ID` is required. Product name and row position are never used as Sheet identity. |
| Sync safety | Preview and final save use the same stable identity. Missing or duplicate IDs, invalid rows, inaccessible/wrong sheets, failures, and cancellations do not remove existing Google-managed inventory. |
| Source removal | A Google-managed row absent from a complete, successful source snapshot is permanently deleted only after all Sheet rows have been parsed, validated, saved, and embedded. |
| Quota | Existing matched rows update at capacity. Only genuinely new rows over the plan limit are skipped, and the owner receives separate add/update/unchanged/delete/skip counts. |
| Owner actions | Google-managed rows are read-only with Sheet-and-sync guidance. Manual and CSV rows support owner-scoped single and selected-row permanent deletion with confirmation. |

The F07 architecture follow-up decision dated 2026-07-22 now aligns the architecture with this implementation: the inherited `mirror archive`/reactivation behavior does not apply to Google-managed F07 source removal. A removed Google-managed product is permanently deleted only after a complete successful sync.

## Scope Delivered

* Saved one-per-owner connection state including spreadsheet ID, worksheet GID/title, canonical selected-sheet URL, and sync result metadata.
* First-time `Connect & Preview` and later `Sync & Preview` behavior, with the saved URL repopulated in the editable field.
* Source-replacement confirmation before a different spreadsheet/worksheet connection is persisted.
* Strict Google Sheet `SKU`/`Product ID` parsing, duplicate/missing-ID rejection, and connection-scoped matching.
* Complete-sync-only permanent deletion of removed Google-managed inventory, after successful persistence and embedding work.
* Full-capacity update handling and explicit partial-save messaging for skipped new rows.
* Read-only Google row guidance for Edit, Archive, Delete, row selection, and bulk actions.
* Single and bulk permanent deletion for Manual and CSV inventory only, including authenticated owner checks and confirmations.

## QA-Driven Bounded Repair — 2026-07-22

Authenticated staging browser QA found that a cancelled Sheet preview left the connected worksheet label and `Sync & Preview` CTA visible but cleared the editable saved URL. The repair returns the canonical selected-sheet URL from the connection `PUT` response and restores that URL whenever preview state is cancelled. QA also found that same-source preview reset `last_sync_status` to `never`; the connection route now preserves the last result unless the owner creates or confirms a replacement connection. Focused regression assertions, TypeScript checks, and live browser re-tests passed.

## QA-Driven Quota Result Repair — 2026-07-23

A valid 501-row staging journey proved the stable-SKU update and quota decision were correct, but exposed an inaccurate result sentence: a quota-skipped new product was also labelled as an invalid row. `app/inventory/page.tsx` now subtracts quota skips from validation failures before composing the result. `backend/api.py` now persists a quota-specific partial-sync result explaining that source removals were not applied. The visible re-test confirmed the existing update saved, only the new row was skipped, and the final result and saved last-result were specific.

## Inventory Listing Presentation Refinement — 2026-07-25

The CEO-approved F07 UI refinement changes presentation only. `app/inventory/page.tsx` now hides Source, Status, Eligibility, and the separate Link column; aligns Preview and Your Products product columns as Product Name, Brand, Category, SKU, price/stock, technical specifications, Image, and Description; and makes Product Name the product URL link when available. Both Product Name and Description use 320px shared columns; Product Name remains a two-line, Brand-sized label, while Description uses a measured two-line clamp with a dialog-based `See more` control only after overflow. Both listings use clearly contrasting alternate rows and hover feedback. In Your Products, the selection checkbox is vertically centered within the Product Name cell and a selected row receives a full-row blue state; Preview deliberately has neither selection nor actions. Disabled Google-managed Edit, Archive, and Delete actions share the approved tooltip directing the owner to change, update, or delete the product in Google Sheets and then sync from SaleAura. No inventory data, Sheet connection, sync, or permission behavior changed.

Focused F07 Vitest coverage and TypeScript checks passed. Authenticated browser re-test remains a QA handoff item because the browser available to this implementation session is signed out; no account or test data was created to bypass that boundary.

## Product Files Changed

Application routes and UI:

* `app/inventory/page.tsx`
* `components/DashboardLayout.tsx`
* `app/api/upload-google-sheet/route.ts`
* `app/api/inventory/google-sheet/connection/route.ts`
* `app/api/inventory/items/route.ts`
* `app/api/inventory/items/[inventory_id]/route.ts`

Backend and import contract:

* `backend/api.py`
* `backend/services/import_parser.py`

Database:

* `supabase/migrations/20260722110000_f07_google_sheet_safe_sync_and_delete.sql`

Focused coverage:

* `tests/f07/migration-google-sheet-connections.test.ts`
* `tests/test_f06_import_parser.py`

## Migration and Shared-Environment State

The new migration converts prior Google-managed source row keys to their stored SKU where present, then adds a partial unique index on `(user_id, source_reference, source_row_key)` for Google-managed inventory.

Migration state: `APPLIED_TO_AUTHORIZED_STAGING_ON_2026-07-22`; not applied to production.

The authorized staging Supabase MCP project was identified as `https://ktyehpormzdtvoznynka.supabase.co`. Before application, its 500 Google-managed rows had no blank SKUs and no duplicate `(owner, source, SKU)` identity groups. Migration `20260722165610_f07_google_sheet_safe_sync_and_delete` then applied successfully, and the partial unique index was verified. No production Supabase, Polar, or other external provider data was changed.

## Local Verification

| Check | Result |
| --- | --- |
| `pnpm exec tsc --noEmit` | PASS |
| `pnpm vitest run` | PASS — 36 files / 117 tests |
| `python3 -m unittest tests.test_f06_import_parser tests.test_f06_import_lifecycle` | PASS — 8 tests |
| `python3 scripts/check_python_syntax.py` | PASS — 38 files |
| `pnpm build` | PASS — existing Supabase Edge Runtime and Node deprecation warnings remain |
| `git diff --check` | PASS |

## QA Handoff

The implementation report does not determine QA disposition. The QA report and E2E tracker now record completed staging browser coverage for `F07-INV-001` through `F07-INV-006`, `F07-INV-008`, and `F07-INV-009`, plus partial invalid-source/mobile coverage. Remaining QA is limited to an inaccessible-source fixture and cross-owner/mobile-layout completion under `F07-INV-007` and `F07-INV-010`.

To finish the remaining browser QA, the QA owner needs:

1. A separate staging Sheet that is intentionally not shared with the configured service account, to prove inaccessible-source failure without changing the saved connection.
2. A second authorized staging owner session for owner-isolation checks.

Expected QA focus: inaccessible-source preservation and owner isolation. See the QA report and E2E tracker for the authoritative current status.

Attempt Result: IMPLEMENTED_PENDING_QA_RETEST

STATUS: IMPLEMENTATION_READY_FOR_QA
