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

STATUS: FAIL
