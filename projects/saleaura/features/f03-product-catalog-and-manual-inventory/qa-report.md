# QA Report

## Feature ID and Name

`F03 — Product Catalog and Manual Inventory`

## QA Mode

`EXISTING_CODE`

## Requirement IDs

`INV-001`, `INV-002`, `INV-003`, `INV-004`, `INV-005`, `INV-006`, `INV-007`, `INV-008`, `DTO-001`, `SEC-INV-001`

## Input References

* `projects/saleaura/features/f03-product-catalog-and-manual-inventory/ceo-request.md`
* Master SaleAura V1 PRD ending `STATUS: PRD_READY`
* Master SaleAura V1 architecture ending `STATUS: ARCHITECTURE_READY`
* SaleAura V1 Release Plan v1.0
* Existing product code at integrated F02 head `f8e48fb`
* Checked-in consolidated schema and integrated F02 inventory/quota boundaries

## Attempt 1

### Environment

* Date: 2026-07-03 (Asia/Karachi).
* Product branch: `feature/f03-product-catalog-manual-inventory`.
* Product baseline: release-branch head `f8e48fb`.
* Node.js: `22.13.1`; pnpm: `10.11.1`.
* Python: `3.13.7`.
* TypeScript compiler: passed.
* Existing automated suite: 15 Vitest files / 63 tests pass; 15 Python tests pass.
* F03-targeted automated coverage: none discovered.
* Production/staging mutation: none.
* Live Supabase metadata recheck: not performed; baseline uses checked-in schema and product code only.

### QA Summary

FAIL.

The existing implementation already provides a substantial inventory-upload foundation: CSV and Google Sheets preview/save flows exist, uploads are quota-aware, inventory rows can be updated, embeddings are refreshed efficiently, and owner inventory is visible in the dashboard.

It is not F03-ready. The current product model has no SKU or alias identity, no per-product source metadata, no product archive/mirror/manual lifecycle state, no Google-managed read-only enforcement, no first-class manual create/archive/reactivate workflow, no customer-safe product DTO boundary, and no protection against broad raw inventory exposure. The current identity logic still deduplicates imports by loose name/category/brand matching, and the raw inventory surface is intentionally public at the schema level.

This is a QA-first baseline failure and consumes no repair cycle.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Evidence |
| --- | --- | --- |
| `INV-001` | FAIL | Inventory schema has no `sku` field, and import identity is derived from normalized `name|category|brand` plus loose `name|category` matching. |
| `INV-002` | FAIL | There is no alias table/field or SKU-replacement preservation model; product identity changes cannot be tracked independently of mutable display fields. |
| `INV-003` | FAIL | Source tracking exists only on `inventory_import_jobs`; inventory rows themselves do not store manual/CSV/Google Sheets provenance or source row reference. |
| `INV-004` | FAIL | Inventory rows have only `stock`; no active/manual-archive/mirror-archive/zero-stock lifecycle state is stored. |
| `INV-005` | FAIL | The owner UI supports upload and listing, and the backend supports `PUT` update, but there is no first-class manual create/archive/reactivate workflow. |
| `INV-006` | FAIL | Google Sheets rows are not distinguishable per product and therefore cannot be enforced as read-only inside SaleAura; the generic update path allows any owner row update. |
| `INV-007` | FAIL | Imported URLs are supported, but direct product-image upload is unauthenticated and not restricted to editable products. |
| `INV-008` | FAIL | Some search/build queries filter `stock > 0`, but there is no canonical hidden-from-customer rule for zero-stock/archived states while retaining owner visibility. |
| `DTO-001` | FAIL | Customer-facing and internal search paths return raw `inventory` rows with `select('*')` rather than a purpose-built customer-safe product DTO. |
| `SEC-INV-001` | FAIL | Checked-in RLS explicitly grants public `SELECT` on `inventory`, and the Next inventory proxy/backend GET path expose raw owner inventory by `user_id`. |

### Test Cases and Actual Results

1. Existing frontend/backend regression suites:
   * `pnpm exec vitest run tests/f02 tests/f01`: PASS — 15 files / 63 tests.
   * `python3 -m unittest discover -s tests -p 'test_*.py'`: PASS — 15 tests.
   * `pnpm exec tsc --noEmit`: PASS.

2. F03-targeted test discovery:
   * Procedure: search `tests/` for F03 inventory/product identity coverage.
   * Result: FAIL — no F03-targeted automated tests discovered.

3. Owner inventory read boundary:
   * Procedure: inspect `app/api/inventory/[user_id]/route.ts` and backend `GET /api/inventory/<user_id>`.
   * Result: FAIL — route accepts arbitrary `user_id`; no owner-session verification occurs at that boundary.

4. Product identity and deduplication:
   * Procedure: inspect `_normalize_item_for_persistence`, `_build_identity_key`, `_build_loose_identity_key`, and `_build_existing_inventory_maps`.
   * Result: FAIL — identity is based on mutable name/category/brand fields, with a loose name+category fallback.

5. Source tracking:
   * Procedure: inspect `inventory` schema, `inventory_import_jobs` schema, and save pipeline.
   * Result: FAIL — import job provenance exists, but inventory rows themselves do not store source type or source references.

6. Product lifecycle state:
   * Procedure: inspect `inventory` schema, owner page, and backend inventory routes.
   * Result: FAIL — no archive/manual/mirror status model exists; only `stock` is persisted.

7. Editable vs read-only behavior:
   * Procedure: inspect owner inventory UI and backend update route.
   * Result: FAIL — Google Sheets products cannot be identified per row, and no read-only guard exists.

8. Direct image upload boundary:
   * Procedure: inspect `app/api/upload-product-image/route.ts`.
   * Result: FAIL — no authentication, no owner binding, and no editable-product gate are enforced.

9. Customer-safe product exposure:
   * Procedure: inspect `inventory_service.py`, build-generator queries, and backend raw inventory reads.
   * Result: FAIL — raw rows are returned with `select('*')`, not a customer-safe DTO.

10. Raw inventory security:
   * Procedure: inspect checked-in RLS policies and the inventory proxy/backend GET path.
   * Result: FAIL — schema defines `CREATE POLICY "Inventory Public View" ON inventory FOR SELECT USING (true)`, and route-level access is broad.

### Findings

#### `F03-QA-001`

* Requirement ID: `INV-001`, `INV-002`
* Severity: Critical
* State: `OPEN`
* Title: Product identity relies on mutable name/category/brand matching instead of owner-scoped SKU and aliases
* Evidence: `_build_identity_key`, `_build_loose_identity_key`, `_normalize_item_for_persistence`, and `inventory` schema.
* Expected: Every owner product has a unique SKU, legacy rows receive stable generated SKUs, and SKU replacement preserves identity through aliases/reference data.
* Actual: No SKU or alias model exists. Imports deduplicate by normalized name/category/brand and sometimes by name/category alone.
* Suggested fix direction: Add a canonical per-product identity layer with owner-scoped SKU uniqueness, stable generated legacy SKUs, and alias preservation for later imports/edits.

#### `F03-QA-002`

* Requirement ID: `INV-003`, `INV-006`
* Severity: Critical
* State: `OPEN`
* Title: Inventory rows lack per-product source metadata and cannot enforce Google-managed read-only behavior
* Evidence: `inventory` schema, `inventory_import_jobs`, save pipeline, and update endpoint.
* Expected: Each product row stores source type and enough source reference metadata to support future sync safety and read-only Google Sheets enforcement.
* Actual: Only import jobs store `source_type` and `source_reference`. Product rows themselves are source-agnostic and all rows are editable through the same update path.
* Suggested fix direction: Persist per-row source ownership/reference data and enforce read-only behavior plus clear owner messaging for Google-managed products.

#### `F03-QA-003`

* Requirement ID: `INV-004`, `INV-005`, `INV-008`
* Severity: High
* State: `OPEN`
* Title: Product lifecycle state is incomplete and owner/customer visibility rules are not centralized
* Evidence: `inventory` schema, `app/inventory/page.tsx`, and inventory/build query paths.
* Expected: Products track active/manual-archive/mirror-archive/zero-stock state; owners can create/edit/archive/reactivate editable products; customer-facing outputs hide zero-stock and archived rows.
* Actual: Rows only store `stock`; there is no archive/reactivate state model or manual product lifecycle UI, and customer filtering is inconsistent across paths.
* Suggested fix direction: Add explicit product-state fields and route both owner and customer product access through one authoritative visibility contract.

#### `F03-QA-004`

* Requirement ID: `INV-007`
* Severity: High
* State: `OPEN`
* Title: Direct product-image upload is unauthenticated and not limited to editable products
* Evidence: `app/api/upload-product-image/route.ts`.
* Expected: Imported URLs remain supported, and direct Cloudinary uploads are allowed only for authenticated owners editing manual/CSV products.
* Actual: The route accepts any request with `file` JSON and uploads it without session, owner, or editable-product checks.
* Suggested fix direction: Add authenticated owner checks, validated file bounds, and editable-product/source gating before upload.

#### `F03-QA-005`

* Requirement ID: `DTO-001`, `SEC-INV-001`
* Severity: Critical
* State: `OPEN`
* Title: Raw inventory is publicly readable and customer-facing paths expose unfiltered internal rows
* Evidence: `supabase-schema.sql` inventory public-view policy, `GET /api/inventory/<user_id>`, `app/api/inventory/[user_id]/route.ts`, `inventory_service.py`, and other `select('*')` inventory queries.
* Expected: Raw inventory/embeddings are protected from unintended public access, and customer-facing consumers receive a minimal customer-safe product DTO.
* Actual: The schema explicitly allows public inventory `SELECT`, the proxy/backend inventory read paths are broad, and product consumers read raw inventory rows directly.
* Suggested fix direction: Remove unintended public raw access, introduce explicit owner/customer DTO boundaries, and narrow inventory reads to the minimum contract each surface needs.

#### `F03-QA-006`

* Requirement ID: All F03 requirements
* Severity: High
* State: `OPEN`
* Title: F03 behavior lacks automated regression coverage
* Evidence: test discovery across `tests/`.
* Expected: Targeted tests cover SKU generation, alias preservation, source/read-only behavior, archive/reactivate state, customer DTO shaping, and inventory security boundaries.
* Actual: No F03-targeted tests were found.
* Suggested fix direction: Add focused TypeScript, Python, and executable SQL tests alongside the F03 delta.

### Security and Ownership Checks

FAIL.

F02 correctly revoked direct browser inventory `INSERT`, but F03 still exposes raw inventory too broadly for V1. The schema’s public inventory read policy and the unauthenticated product-image upload route both conflict with the approved product-catalog security model.

### Scope Compliance

The baseline audit stayed within F03. No F04 compatibility logic, F05 reference catalogs, F06/F07 source-connection feature expansion, staging mutation, production mutation, or external configuration change was performed.

### Coverage Limitations

* No live Supabase metadata query or shared-environment audit was performed in this baseline pass.
* No real Google Sheets connection or Cloudinary upload execution was performed.
* No browser E2E owner workflow was exercised.
* These limits do not change the deterministic code/schema failures above.

Attempt Result: FAIL

## Status

STATUS: FAIL
