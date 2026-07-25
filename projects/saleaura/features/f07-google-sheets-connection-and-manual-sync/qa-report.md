# QA Baseline Report — F07 Google Sheets Connection and Manual Sync

## Existing-Code Audit — 2026-07-16

The existing Sheets path is an ad hoc preview/import flow. It extracts a spreadsheet ID from the URL, always opens worksheet index `0`, and delegates save behavior to the generic inventory importer.

## Findings

* `F07-QA-001` — No owner-scoped persisted connection exists; `SHEET-001` and `SHEET-002` fail.
* `F07-QA-002` — The worksheet identity is implicit (`get_worksheet(0)`), so a worksheet GID cannot be selected or persisted; `SHEET-002` fails.
* `F07-QA-003` — The browser passes `user_id` to the proxy/backend and the backend uses it for database work; authoritative server-side owner derivation is missing.
* `F07-QA-004` — Preview/save is an upload action, not a saved-connection manual-sync contract; `SHEET-003` fails.
* `F07-QA-005` — There is no source-switch confirmation or prior-source protection; `SHEET-008` fails.
* `F07-QA-006` — There is no connection-specific complete-read marker to prove mirror archiving is safe; `SHEET-005` through `SHEET-007` are not established.

## Result

The existing code supplies useful parsing and generic source metadata but does not satisfy F07's connection/sync contract. A bounded F07 delta is required.

Attempt Result: FAIL

Attempt Result: FAIL

## CEO-Approved Live-Test Deferral — 2026-07-17

The CEO authorized deferring the shareable-Google-Sheet staging validation. Automated verification, the staging schema migration, and code review are complete; live Google read/connect/manual-sync, source-missing archive, and reactivation scenarios remain explicitly unverified.

Risk: external Google credentials, sharing permissions, and real worksheet lifecycle behavior may still expose integration defects. This is not a QA pass and must be completed before F09 or production readiness relies on Google Sheets data.

Attempt Result: DEFERRED_BY_CEO

STATUS: QA_DEFERRED_CEO_WAIVER

## Follow-up Repair QA Handoff — 2026-07-22

The approved follow-up implementation has replaced the earlier failing behavior. This entry preserves the historical baseline and does not claim a browser pass.

### Authorized staging database evidence

* Verified the connected MCP project is the documented staging project: `https://ktyehpormzdtvoznynka.supabase.co`.
* Preflight found 500 Google-managed inventory rows, zero blank SKUs, and zero duplicate stable-identity groups.
* Applied `20260722165610_f07_google_sheet_safe_sync_and_delete` successfully.
* Verified partial unique index `inventory_google_sheet_source_row_identity_idx` on `(user_id, source_reference, source_row_key)` for Google-managed rows.
* No production Supabase project or Polar environment was accessed.

### Browser QA state

The required F07 Playwright journey was not run. The staging configuration intentionally has no `E2E_QA_USER_ID` and no controlled `E2E_GOOGLE_SHEET_URL`; a QA run must not repurpose an existing customer or Google source. Provide a dedicated Starter-entitled staging owner and a service-account-shared Sheet fixture with unique stable IDs, then execute `F07-INV-001` through `F07-INV-010` in order on desktop and the required mobile regression.

Attempt Result: BLOCKED_PENDING_DEDICATED_STAGING_BROWSER_FIXTURE

STATUS: QA_BLOCKED_PREREQUISITES

## Authenticated Browser Attempt — 2026-07-22

An owner signed in to the local SaleAura app connected to staging, then Chrome Playwright navigated to `/inventory` and opened Google Sheets mode. Inventory rendered successfully and browser console capture contained no `warn`, `error`, or `pageerror` entries.

The supplied Sheet URL could not be previewed because the local Flask backend returned:

`GOOGLE_SHEETS_CREDENTIALS not found in environment`

Diagnosis: the running backend loads `.env`, where `GOOGLE_SHEETS_CREDENTIALS` is empty. `.env.staging` contains a non-empty value but was not sourced when the backend was started. The error occurred before the connection `PUT`, so the existing connected worksheet and all Google-managed inventory remain unchanged.

Required repair before continuing browser QA: restart the local backend with the authorized staging environment loaded, without exposing the credential value; then re-run the preview and capture its Playwright evidence.

Attempt Result: BLOCKED_LOCAL_STAGING_GOOGLE_CREDENTIAL_CONFIGURATION

STATUS: QA_BLOCKED_LOCAL_ENVIRONMENT

## Authenticated Browser Re-test — F07-INV-001 — 2026-07-22

The local application service was restarted with the authorized staging configuration and project virtual environment. It used the authorized staging Supabase project; no local, mock, or alternate database was used.

Using the supplied Google Sheet and the authenticated staging owner in visible Chrome:

* Google Sheets preview completed successfully.
* The owner cancelled the preview without saving inventory.
* The exact canonical selected-sheet URL remained in the editable field after cancellation.
* The connected worksheet remained visible and the later CTA was `Sync & Preview`.
* Chrome captured no `warn`, `error`, or `pageerror` entries.

During this test, QA found and repaired the saved-URL regression: the connection `PUT` response omitted `sheet_url`, while preview cancellation cleared the input. The route now returns the canonical selected-sheet URL and cancellation restores the connected URL. Focused Vitest coverage (4 assertions) and TypeScript validation passed before the browser re-test.

This is a pass for `F07-INV-001` only. The 500-row save, quota, removal/re-add, identity-reorder, invalid-state, replacement, delete, isolation, and mobile journeys remain required.

Attempt Result: PARTIAL_PASS_F07_INV_001

STATUS: QA_PARTIAL_STAGING_PASS

## Completion Follow-up — 2026-07-23

QA continued in visible authenticated Chrome through Playwright CDP against the authorized staging Supabase project and the supplied editable Google Sheet. A same-workbook backup worksheet (`QA-F07-BACKUP-20260722183135`, GID `872238534`) remains available; the selected production-like worksheet and inventory were restored after every temporary fixture.

### Newly completed desktop journeys

* Accepted source replacement now passes: QA accepted the clear replacement confirmation for the backup worksheet, cancelled its preview without syncing inventory, then accepted replacement back to the original selected worksheet and cancelled its preview. Each reload showed the expected canonical saved URL; no inventory rows were synced during either switch.
* Middle-row removal now passes: a labelled SKU was inserted at source row 250 and saved, then that exact middle source row was removed. The complete visible sync reported `0 added, 1 updated, 498 unchanged, 1 deleted, 0 new products skipped`; MCP confirmed the SKU was absent. The Sheet and inventory were restored to 499 Google-managed rows.
* Invalid-source handling now has positive browser evidence: a temporary missing-SKU row was rejected before save with `Row 249 is missing a unique SKU or Product ID. Add one before syncing.` A nonexistent worksheet GID failed with `id 999999999 not found`; reloading proved that it did not replace the original saved selected-sheet URL. The earlier duplicate-SKU and preview-cancel evidence remains valid. An inaccessible external Sheet still needs a separately unshared staging fixture.
* Manual/CSV owner actions now pass: visible UI created and permanently deleted labelled Manual and CSV products. The Manual flow proved individual delete, cancellation, selected-row delete, Select All, and bulk delete. Both product types displayed the permanent-delete warning. Google-managed row selection, Edit, Archive, and Delete were disabled with Sheet-specific guidance. MCP confirmed all temporary fixtures were absent afterward.
* The valid 501-row quota regression now passes. At 500/500, one existing SKU changed and one valid new SKU exceeded capacity. The dialog stated that existing updates were allowed and one new row was over limit. The permitted save updated the existing SKU, did not create the new SKU, and preserved source-removal safety. QA found and repaired a message defect that had described the quota skip as an invalid row. The final visible result was `0 added, 2 updated, 498 unchanged, 0 deleted, 1 new products skipped (no Sheet removals were applied).` The saved last-result text is now quota-specific. A final complete sync removed the labelled existing fixture and restored 499 source and staging rows.

### Mobile and isolation limits

At a 390×844 viewport, the F07 URL field, `Sync & Preview` control, and mode selector were individually visible and operable. QA found the inventory table was widening the shared dashboard flex container to 1328px. A scoped `min-w-0` repair in the dashboard inset/main restored the intended card-level horizontal table scrolling; a visible re-test measured both document and body width at exactly 390px. The mobile portion now passes. Cross-owner isolation remains blocked: no second authorized staging owner session was supplied, and QA did not create or repurpose one.

### Current staging baseline and verification

* Staging MCP final check: 499 Google-managed rows and zero `QA-F07-*` inventory rows.
* Selected source: original worksheet GID `1332864850`; no temporary QA rows remain. The backup worksheet is retained for audit/recovery only.
* Focused checks after the quota-message repair: `pnpm vitest run tests/f07` — 2 files / 9 tests passed; `pnpm exec tsc --noEmit` passed; `git diff --check` passed.

Attempt Result: PARTIAL_PASS_REMAINING_DESKTOP_QA

STATUS: QA_PARTIAL_STAGING_PASS

## Editable Fixture Lifecycle Run — 2026-07-22

After the staging service account received Editor access, QA created in-workbook backup worksheet `QA-F07-BACKUP-20260722183135` with the original 499 data rows. All temporary Sheet and inventory changes below were restored at the end of the run.

Verified in visible Chrome, with every persisted result checked through the authorized staging Supabase MCP:

* A QA-prefixed row brought the source to exactly 500 products. Complete sync reported one addition; MCP confirmed 500 Google-managed rows and successful status.
* At 500/500, changing the existing QA product name saved as an update with zero additions and zero skipped rows. MCP confirmed the stable-SKU row retained its identity and received the new name.
* A 501-row update-plus-new attempt opened the specific quota dialog: existing updates could continue while the new row was skipped. The selected update persisted and the new SKU was absent from staging. The run also reported one invalid source row and marked the connection failed, so the exact all-valid 501-row scenario remains a retest requirement.
* Removing the final QA row, then completing sync, reported exactly one deletion. MCP confirmed the SKU was absent and the source count was 499. Re-adding the same SKU to the 499-row source then reported one addition and restored 500 rows.
* Moving the QA row from row 501 to row 3 produced no insert/delete. MCP confirmed exactly one Google-managed inventory row with `source_row_key = QA-F07-SKU-001`.
* A duplicate-SKU source preview failed clearly with `Row 501 duplicates SKU/Product ID QA-F07-SKU-001`. MCP confirmed the existing 500 rows and the stable SKU were unchanged. No save control appeared.
* Previewing the backup worksheet displayed the source-replacement confirmation. Dismissing it and reloading retained the original selected-sheet URL. No inventory sync was saved.

Final restoration evidence: the original Sheet has 499 data rows and no `QA-F07-*` rows. A final complete sync returned staging to 499 Google-managed rows, zero QA inventory rows, `last_sync_status = succeeded`, and no sync error.

Remaining QA coverage:

* Re-run a fully valid 501-row update-plus-new fixture without the unexpected invalid-row report.
* Remove a middle source row and cover accepted replacement confirmation, not cancellation only.
* Complete Manual/CSV single, selected, Select All, bulk, cancel, Google-guidance, second-owner isolation, and mobile checks with reliable evidence.

Attempt Result: PARTIAL_PASS_EDITABLE_FIXTURE_LIFECYCLE

STATUS: QA_PARTIAL_STAGING_PASS

## Fixture Edit and Owner-Action Follow-up — 2026-07-22

The supplied Sheet has 499 data rows and the staging service account can read it, but Google rejected a backup-worksheet creation attempt with `403 The caller does not have permission`. The signed-in browser account shows editable Sheet controls; however, without a service-account-editable dedicated copy, QA cannot safely automate source row removal, re-addition, reordering, duplicate/missing-ID states, or a second source replacement while preserving the original fixture.

QA also started the Manual-product deletion journey using one QA-prefixed staging row. The browser automation transport did not return a trustworthy completion callback, so this is not accepted as owner-action evidence. The exact residual QA row was removed through Supabase MCP cleanup and MCP verified zero rows remain. That cleanup does not replace the required owner-UI Manual/CSV single and bulk deletion proof.

Required fixture action: create a disposable copy of the source Sheet, share it with the authorized staging service account as an Editor, and provide its selected-worksheet URL. This preserves the original Sheet while allowing the remaining normal, boundary, and bad-state F07 journeys to be completed and restored deterministically.

Attempt Result: BLOCKED_EDITABLE_DISPOSABLE_SHEET_AND_RELIABLE_OWNER_UI_EVIDENCE

STATUS: QA_PARTIAL_STAGING_PASS

## Sync Safety and Last-Result Re-test — 2026-07-22

The authenticated staging owner completed one full Google Sheet save. The visible result was `0 added, 1 updated, 498 unchanged, 1 deleted, 0 new products skipped`; Chrome captured no warnings/errors.

Supabase MCP then confirmed the selected connection has `last_sync_status = succeeded`, no sync error, and 499 Google-managed rows for the saved source. This is direct staging-database evidence that the completed source snapshot permitted the reported permanent removal.

QA then found and repaired a second same-source preview regression: the connection route reset `last_sync_status` to `never` on every preview. The route now resets lifecycle state only for a first connection or confirmed source replacement. A live preview/cancel re-test retained the successful timestamp, canonical URL, worksheet label, and `Sync & Preview` CTA with no browser warnings/errors.

The supplied source snapshot currently contains 499 products, so this run does not satisfy the exact dedicated 500-product fixture criterion for `F07-INV-002`; it also does not cover the separately required middle/final removal and re-add sequence of `F07-INV-005`.

Attempt Result: PARTIAL_PASS_SYNC_SAFETY_AND_LAST_RESULT

STATUS: QA_PARTIAL_STAGING_PASS
