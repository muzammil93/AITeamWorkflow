# Product Requirements Document — F07 Google Sheets Connection and Manual Sync

## Scope

Replace the ad hoc Google Sheets upload path with one authenticated, owner-scoped connection and an explicit manual-sync workflow.

## Requirements

* `SHEET-001` — An owner may have exactly one active Google Sheets connection, selecting one spreadsheet and worksheet.
* `SHEET-002` — Persist spreadsheet ID, worksheet GID, worksheet title, and the canonical source reference.
* `SHEET-003` — Do not schedule sync. The owner explicitly triggers preview/sync from the saved connection.
* `SHEET-004` — Products created by the connection are `google_sheet` products and remain read-only in SaleAura.
* `SHEET-005` — Mirror archive is permitted only after a complete successful worksheet read and only within that connection's source identity.
* `SHEET-006` — A returned source row reactivates a prior mirror-archived product.
* `SHEET-007` — A manually archived product never reactivates from sync.
* `SHEET-008` — Replacing an existing source requires an explicit confirmation; without it, no connection or inventory source is changed.

## Acceptance

* Connection, preview, sync, and replacement APIs derive ownership from the authenticated server session, never a caller-supplied owner ID.
* Invalid, inaccessible, or partial reads leave the previous connection and inventory lifecycle untouched.
* The Inventory page tells the owner the connected worksheet and whether a source replacement needs confirmation.

## Out of Scope

* Google OAuth for the owner, scheduled/background sync, multiple active sources, Google Sheet writes, and changes to CSV import behavior.

STATUS: PRD_READY
