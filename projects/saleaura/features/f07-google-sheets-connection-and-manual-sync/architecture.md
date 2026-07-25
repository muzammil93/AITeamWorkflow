# Architecture — F07 Google Sheets Connection and Manual Sync

## Design

1. Add an owner-unique `google_sheet_connections` record containing spreadsheet ID, worksheet GID/title, canonical URL, and sync timestamps/status.
2. Replace the browser-controlled backend call with authenticated Next.js connection and sync routes. The server derives the owner from Supabase session and passes only trusted owner context to the backend reader/importer.
3. Parse Google URLs strictly, including optional `gid`; read the selected worksheet by GID rather than index. A read is complete only after headers and all records are obtained without error.
4. Creating the first connection is immediate. A different spreadsheet/GID returns a `SOURCE_CHANGE_CONFIRMATION_REQUIRED` response unless `confirm_replace: true` is sent.
5. Manual sync reads the saved connection, tags each row with a stable Sheet `SKU` or `Product ID`, and uses that same identity for preview and final save. Product name and row position are mutable data and must never be used as a fallback identity.
6. Only a complete successful Sheet read and save may provide a source snapshot for removal. After all source rows validate, inventory persistence succeeds, and required embedding work succeeds, Google-managed rows for that connection whose stable identity is absent are permanently deleted. Failed, inaccessible, incomplete, invalid, cancelled, or quota-incomplete syncs must not remove existing Google-managed inventory.
7. Capacity classification matches stable Sheet identity: existing Google-managed rows remain eligible for update at capacity; only genuinely new Sheet rows over the entitlement limit are skipped and reported.
8. Google-managed rows remain read-only in SaleAura with guidance to edit or remove the product in the Sheet and then sync. Manual and CSV rows retain their separate, owner-scoped permanent-delete lifecycle.
9. The existing F03 item routes remain the enforcement point for Google-managed read-only behavior and owner/source isolation.
10. The Inventory preview and saved-product listings share one visible-column contract: Source, Status, Eligibility, and the separate Link column are omitted; Product Name uses the product URL as its link when available; 320px Product Name/Description columns use two-line clamping; Description measures overflow after render to conditionally expose a dialog-based `See more`; alternating rows use visible contrast; and all disabled Google-managed actions use the same accessible tooltip copy directing the owner to Google Sheets and a manual sync. Your Products combines its vertically centred checkbox with Product Name and applies a full-row selected state; Preview intentionally has no selection or actions.

## Validation

* Unit tests for URL/GID parsing, source-change protection, and stable SKU/Product-ID identity.
* Route tests proving owner derivation and rejection of caller-supplied owner IDs.
* Migration contract tests for single active connection.
* Playwright staging coverage for normal connect/sync, valid capacity updates, safe invalid/inaccessible/cancelled states, permanent source removal after a complete sync, Manual/CSV deletion, owner isolation, and mobile regression.

## Follow-up Lifecycle Decision — 2026-07-22

The approved F07 follow-up PRD and CEO-confirmed operating rule replace the inherited `mirror archive`/reactivation interpretation for this feature only. The required terminal behavior is permanent deletion of a removed Google-managed product after a complete successful sync. This delta does not change Manual or CSV product lifecycle rules.

STATUS: ARCHITECTURE_READY
