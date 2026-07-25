# Product Requirements Document - F07 Google Sheets Connection and Manual Sync

## Feature Name

F07 Google Sheets Connection and Manual Sync - Inventory Follow-up

## Feature ID and Execution Mode

`F07` - bounded repair after live inventory testing.

## Master Requirement References

`SHEET-001` to `SHEET-008`, `INV-001` to `INV-008`, and the approved SaleAura V1 release plan.

## Dependency References

* F02 plan limits and upload quota rules.
* F03 product ownership, source labels, editable-product rules, and inventory lifecycle.
* F06 import preview, validation, and failed-row reporting.

## CEO Request

The Inventory page must make Google Sheets easy to understand and safe for a real shop owner. A Google Sheet is the source of truth for Google-managed products: the owner changes or removes products in the Sheet, then manually syncs SaleAura. A removed Sheet product must be permanently removed from SaleAura inventory after a complete successful sync.

The page must clearly show the connected Sheet, allow an owner to sync without pasting the URL again, allow updates at a full quota, block only genuinely new products that exceed the quota, explain Google-managed read-only actions, and add Delete and bulk Delete for Manual and CSV products. Product-listing tables must hide source, status, and eligibility columns; use consistent two-line product-name and description treatment in preview and saved inventory; and explain every disabled Google-managed action with the Sheet-and-sync next step.

## Clarifying Questions

No clarification required. The CEO confirmed that Google-managed products are removed in Google Sheets and then synced; SaleAura does not offer direct Delete or bulk Delete for those rows.

## Finalized Scope

### In Scope

* One owner-scoped active Google Sheets connection and explicit manual preview/sync.
* A saved, editable connected-Sheet URL and worksheet name on the Inventory page.
* `Connect & Preview` before the first connection and `Sync & Preview` after a connection exists.
* A stable unique product identity from a Sheet `SKU` or `Product ID`. A product name is editable data, not its identity. Row position must never be treated as a stable identity.
* Full-quota behavior that allows existing Sheet products to update and blocks only new products above the plan limit.
* A clear quota result that separately states products to add, update, leave unchanged, delete, and skip.
* Permanent removal of a Google-managed SaleAura product when its stable identity is no longer present in a complete, successful sync of the connected Sheet.
* Protection from accidental removal: a failed, inaccessible, incomplete, invalid, or cancelled Sheet read must not remove existing products.
* Clear source guidance on every Google-managed row: change it in Google Sheets, then sync. The disabled Edit, Archive, and Delete actions must explain this rule.
* Delete and bulk Delete for Manual and CSV products only, including row selection, Select All, clear counts, cancellation, confirmation, and a clear permanent-deletion warning.
* Inventory-table presentation: hide Source, Status, Eligibility, and the separate Link column; give Product Name and Description 320px shared columns; show Product Name with the Brand text size and a two-line clamp, using the product URL as its link when present; show Description with a two-line clamp and a `See more` dialog only when the full text overflows two lines; use visibly distinct alternating row backgrounds; and keep Preview and Your Products product columns aligned. In Your Products only, the selection checkbox is vertically centred within the Product Name cell and turns the complete selected row blue; Preview has neither selection nor actions.
* Owner and source isolation: an owner can act only on their own inventory and their own connected Sheet.
* Recorded staging QA through Playwright only, on desktop and mobile.

### Out of Scope

* Google OAuth, scheduled/background sync, multiple active Sheets, writes back to Google Sheets, and production testing.
* Direct SaleAura Delete, bulk Delete, Edit, or Archive for Google-managed products.
* Recovering a Google-managed product after it has been removed from the Sheet and permanently deleted from SaleAura.
* Changes to CSV import rules except regression protection for shared quota and product-identity behavior.

## Assumptions

* The dedicated staging Sheet contains a unique, non-empty `SKU` or `Product ID` for each product. If it does not, the owner receives a clear message before a destructive sync can occur.
* `Sync & Preview` keeps the owner in control: they review the changes before saving them.
* A full quota never prevents an update to an existing product.
* A Manual or CSV product deletion is permanent and requires an explicit owner confirmation.

## User Stories

* As a shop owner, I can see which Google Sheet is connected and sync it again without guessing whether to paste the URL.
* As a shop owner at my plan limit, I can update an existing Sheet product without being incorrectly told to upgrade.
* As a shop owner, I can add a new product only when my plan has room for it.
* As a shop owner, when I remove a product from my Google Sheet and complete a sync, that product is removed from SaleAura too.
* As a shop owner, I understand why Google-managed rows cannot be edited, archived, or deleted in SaleAura and what to do instead.
* As a shop owner, I can permanently delete one or many Manual or CSV products after a clear confirmation.

## Functional Requirements

* `SHEET-001` - An owner may have exactly one active Google Sheets connection, selecting one spreadsheet and worksheet.
* `SHEET-002` - The connection keeps the selected worksheet identity and enough information to show the connected worksheet URL and name back to the owner.
* `SHEET-003` - There is no scheduled sync. The owner explicitly uses `Connect & Preview` for a first connection and `Sync & Preview` for later changes.
* `SHEET-004` - Products created from the connection are marked as Google-managed and are read-only in SaleAura.
* `SHEET-005` - A complete successful sync permanently removes only Google-managed products that belong to that connection and whose stable Sheet identity is absent. It never removes a product because a read failed or was incomplete.
* `SHEET-006` - Re-adding a previously removed Sheet product creates it again only when the owner saves the reviewed sync and the plan allows the new product.
* `SHEET-007` - A Manual or CSV product keeps its own lifecycle and is never deleted because of a Google Sheet sync.
* `SHEET-008` - Replacing an existing source requires explicit owner confirmation; without it, no connection or inventory source changes.
* `SHEET-009` - Sheet preview and final save use the same stable product identity. Product-name edits, row deletion, and row reordering must not turn an existing product into a false new product or change another product.
* `SHEET-010` - The quota experience distinguishes new products from updates. At zero remaining slots, updates remain savable; new products are clearly skipped or require an upgrade.
* `SHEET-011` - The page shows simple, accurate before-save and after-save counts for added, updated, unchanged, deleted, and skipped products.
* `INV-DELETE-001` - Manual and CSV rows support individual Delete and bulk Delete using selected rows and Select All. Confirmation names the number of products and states that deletion is permanent.
* `INV-DELETE-002` - Google-managed rows cannot be selected for direct deletion. The row and bulk controls explain that removal happens in Google Sheets followed by sync.
* `INV-UI-001` - Preview and saved-product tables expose the same product columns in the same order, excluding Source, Status, Eligibility, and the separate Link column from the visible listing. Product Name is the product URL link when one is available.
* `INV-UI-002` - Product Name uses the same text size as Brand and is clamped to two lines. Description is clamped to two lines and exposes `See more` only when its full text exceeds the clamp; the control opens the complete description in a dialog.
* `INV-UI-003` - Every disabled Google-managed Edit, Archive, and Delete action has a tooltip telling the owner to change, update, or delete the product in Google Sheets and sync it from SaleAura.

## Acceptance Criteria

* After a first successful connection, refresh shows the selected Sheet URL, worksheet name, and `Sync & Preview` without requiring the owner to paste the URL again.
* Changing only a product name in a 500/500 connected Sheet is previewed and saved as one update, not one new product; no upgrade prompt blocks it.
* At 500/500, a sync with one update and one new product allows the update to continue and clearly reports the skipped new product.
* Removing a Sheet product and completing a successful sync removes that exact product from the owner inventory. Removing or reordering a Sheet row does not alter another product.
* A failed, inaccessible, incomplete, invalid, or cancelled sync leaves the previous inventory unchanged.
* A Google-managed row visibly tells the owner to edit or remove it in the Sheet and then sync; Manual and CSV rows retain their appropriate inventory actions.
* Manual and CSV single and bulk Delete work only for the signed-in owner, require confirmation, and update the visible inventory result immediately after success.
* Preview and saved-product listings hide Source, Status, and Eligibility, align their visible product columns, clamp Product Name and Description to two lines, and show the full description only through `See more` when needed.
* Disabled Google-managed Edit, Archive, and Delete controls each provide the approved Google Sheets update/delete-and-sync tooltip.
* Every listed outcome is proven through recorded Playwright staging tests on desktop and mobile. No production service is used.

## Risks / Open Questions

* A Sheet without a unique stable product value cannot safely support rename, delete, and reorder behavior. The page must stop before a destructive sync and clearly direct the owner to provide `SKU` or `Product ID`.
* Permanent deletion is irreversible. The confirmation and Google-managed source guidance must make that consequence clear before the owner acts.

## Status

STATUS: PRD_READY
