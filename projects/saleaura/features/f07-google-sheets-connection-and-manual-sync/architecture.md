# Architecture — F07 Google Sheets Connection and Manual Sync

## Design

1. Add an owner-unique `google_sheet_connections` record containing spreadsheet ID, worksheet GID/title, canonical URL, and sync timestamps/status.
2. Replace the browser-controlled backend call with authenticated Next.js connection and sync routes. The server derives the owner from Supabase session and passes only trusted owner context to the backend reader/importer.
3. Parse Google URLs strictly, including optional `gid`; read the selected worksheet by GID rather than index. A read is complete only after headers and all records are obtained without error.
4. Creating the first connection is immediate. A different spreadsheet/GID returns a `SOURCE_CHANGE_CONFIRMATION_REQUIRED` response unless `confirm_replace: true` is sent.
5. Manual sync reads the saved connection, tags each row with stable source identity and row key, then uses the canonical inventory lifecycle path. Only a complete read may supply the source snapshot used for mirror archive; manual archives retain precedence.
6. The existing F03 item routes remain the enforcement point for Google-managed read-only behavior.

## Validation

* Unit tests for URL/GID parsing, source-change protection, and source identity.
* Route tests proving owner derivation and rejection of caller-supplied owner IDs.
* Migration contract tests for single active connection.
* E2E coverage for connect, confirmation, explicit sync result, and safe error state.

STATUS: ARCHITECTURE_READY
