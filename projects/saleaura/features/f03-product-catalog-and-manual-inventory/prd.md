# Product Requirements Document

## Feature Name

Product Catalog and Manual Inventory Delta

## Feature ID and Execution Mode

`F03` — `QA_FIRST` baseline failure followed by delta implementation

## CEO Request

Verify and complete the existing SaleAura V1 product catalog, inventory identity, source tracking, editable/read-only inventory behavior, customer-safe product exposure, and inventory-security implementation for requirements `INV-001` through `SEC-INV-001`.

Reference: `projects/saleaura/features/f03-product-catalog-and-manual-inventory/ceo-request.md`.

## Master Requirement References

* `INV-001` through `INV-008`
* `DTO-001`
* `SEC-INV-001`
* Master PRD sections “Inventory Sources and Source References”, “SKU and Product Identity”, and “Import and Sync Behavior”
* Master architecture inventory identity/source layer, owner inventory experience, DTO boundary, and raw-inventory hardening guidance

## Dependency References

* `F00 — Development Safety Baseline` is integrated.
* `F01 — Owner Identity and Onboarding` is integrated.
* `F02 — Plans, Billing, and Entitlements` is integrated at product commit `f8e48fb`.
* F03 must preserve the owner identity and quota/entitlement boundaries established by F01 and F02.

## Baseline QA Findings

* `F03-QA-001`: Product identity relies on mutable name/category/brand matching instead of owner-scoped SKU and aliases.
* `F03-QA-002`: Inventory rows lack per-product source metadata and cannot enforce Google-managed read-only behavior.
* `F03-QA-003`: Product lifecycle state is incomplete and owner/customer visibility rules are not centralized.
* `F03-QA-004`: Direct product-image upload is unauthenticated and not limited to editable products.
* `F03-QA-005`: Raw inventory is publicly readable and customer-facing paths expose unfiltered internal rows.
* `F03-QA-006`: F03 behavior lacks automated regression coverage.

## Clarifying Decisions

No CEO clarification is required for F03 behavior. The release plan, master PRD, and master architecture resolve the delta.

F03 owns the product-model and safe access boundary. It does not own:

* F04 compatibility normalization and verified build eligibility rules.
* F05 CPU/GPU performance catalogs.
* F06 unified CSV classification/reporting refinements beyond what F03 needs for identity safety.
* F07 Google Sheets connection UX and one-active-source lifecycle.

Where later features depend on F03 fields, F03 must create the durable product/source model now without implementing later feature behavior.

## Finalized Scope

### In Scope

* Add owner-scoped canonical SKU identity to inventory products.
* Backfill stable generated legacy SKUs for existing rows.
* Allow owner replacement of generated SKUs while preserving product identity through aliases.
* Track per-product source type as `manual`, `csv`, or `google_sheet`.
* Track enough per-product source reference data to support future safe imports/syncs.
* Track explicit product state for:
  * active
  * zero-stock
  * manually archived
  * mirror archived
* Support manual create/edit/archive/reactivate for editable products.
* Treat manual and CSV products as editable inside SaleAura.
* Treat Google-managed products as read-only inside SaleAura and show a clear owner-facing explanation.
* Support imported product URLs and imported image URLs.
* Restrict direct Cloudinary uploads to authenticated owners editing editable manual/CSV products.
* Return customer-safe product DTOs instead of raw inventory rows in customer-facing/search/build/widget paths.
* Hide zero-stock and archived products from customer-facing product results while preserving owner visibility.
* Remove unintended direct public raw inventory and embedding access.
* Keep existing owner inventory listing/upload flows working while upgrading them to the canonical product model.
* Add targeted TypeScript, Python, and executable SQL regression evidence for F03.

### Out of Scope

* F04 compatibility schema and canonical eligibility validation rules.
* F05 performance-score catalogs and verified CPU/GPU upgrade logic.
* F06 final unified CSV reporting/classification feature set beyond identity-safe matching.
* F07 one-active Google source connection UI, manual sync controls, and source-switch confirmation flow.
* Widget allow-domain/session redesign (F08).
* Dashboard redesign, analytics redesign, or lead-pipeline work.
* Shared staging, production, deployment, Google, or Cloudinary configuration mutation.

## Product Model Contract

Each inventory product must have:

* one stable inventory row UUID;
* one current owner-scoped SKU;
* zero or more historical owner-scoped SKU aliases;
* one source type:
  * `manual`
  * `csv`
  * `google_sheet`
* optional source-reference fields sufficient for later safe re-import/sync matching;
* one current owner-facing state:
  * `active`
  * `manual_archive`
  * `mirror_archive`
* stock quantity, where `stock = 0` is still owner-visible but customer-hidden.

Customer-facing visibility requires:

* active state;
* stock greater than zero.

Google-managed read-only means:

* no SaleAura edit of product content fields;
* no SaleAura SKU change;
* no SaleAura archive/reactivate action;
* no SaleAura Cloudinary image replacement;
* owner sees an explanation directing them to edit the sheet and sync later.

## Functional Requirements

### Identity and SKU

1. Every product has a unique owner-scoped SKU.
2. Existing rows without SKUs receive stable generated legacy SKUs derived from immutable row identity.
3. Generated legacy SKUs may be replaced by the owner with a unique custom SKU.
4. Replacing a SKU preserves the same inventory row and records the old SKU as an alias.
5. Import/update matching must prioritize:
   * current SKU
   * SKU alias
   * safe source reference
   * only then any tightly bounded legacy fallback needed for pre-F03 data migration
6. Loose name/category matching alone must not remain the durable identity authority.

### Source metadata

1. Each product stores its source type.
2. CSV/manual rows remain editable in SaleAura.
3. Google-managed rows are read-only in SaleAura.
4. Source reference fields must preserve enough information for future row-safe re-import/sync behavior.
5. Existing rows are backfilled to a safe default source type without losing data.

### Product state and owner workflow

1. Editable products support manual create.
2. Editable products support edit.
3. Editable products support manual archive.
4. Editable products support manual reactivate.
5. Google-managed products reject these SaleAura mutations with a stable read-only error.
6. Owner inventory UI clearly shows:
   * SKU
   * source badge
   * state badge
   * zero-stock visibility
   * read-only explanation where applicable

### Images and URLs

1. Imported `product_url` and `image_url` remain supported.
2. Editable products support authenticated Cloudinary upload.
3. Google-managed products do not support SaleAura-side image replacement.
4. Upload errors are safe and stable.

### Customer-safe DTOs and visibility

1. Customer-facing product/search/build surfaces must not return raw inventory rows.
2. A customer-safe DTO exposes only the fields needed for recommendation/build/chat rendering.
3. Zero-stock and archived products are hidden from customer DTO queries.
4. Owner inventory views continue to show zero-stock and archived products with state context.

## Security Requirements

* Authenticated owner inventory operations derive the owner ID from the server session; client-supplied owner IDs are not authoritative.
* Raw `inventory` and `inventory_embeddings` are not directly publicly readable.
* Public/customer-facing reads go through server DTO endpoints only.
* Product-image upload requires an authenticated owner and an editable target product.
* Browser input cannot choose another owner’s product row, source type, performance data, or inventory alias ownership.
* Internal SKU-alias and product-state mutation boundaries are restricted to intended trusted roles.

## Acceptance Criteria

1. `INV-001` passes when each owner product has a unique SKU and pre-existing rows receive stable generated legacy SKUs.
2. `INV-002` passes when SKU replacement preserves row identity and the old SKU remains matchable as an alias.
3. `INV-003` passes when each product row stores source metadata sufficient for future safe source updates.
4. `INV-004` passes when active/manual-archive/mirror-archive/zero-stock states are represented and surfaced consistently.
5. `INV-005` passes when editable products support manual create/edit/archive/reactivate through trusted owner flows.
6. `INV-006` passes when Google-managed products are read-only in SaleAura and show a clear owner-facing explanation.
7. `INV-007` passes when imported URLs remain supported and Cloudinary upload is allowed only for editable owner products.
8. `INV-008` passes when zero-stock/archived products remain owner-visible but disappear from customer-facing surfaces.
9. `DTO-001` passes when customer/search/build/widget consumers use an allowlisted product DTO instead of raw inventory rows.
10. `SEC-INV-001` passes when raw inventory and embeddings are no longer unintentionally directly public and owner operations derive ownership safely.
11. F03-targeted typecheck, tests, build, and local schema evidence are recorded honestly.

## Risks and External Actions

* Existing inventory data must be backfilled carefully so later F06/F07 imports do not misclassify products.
* F03 should create source-reference fields broad enough for later Google Sheets row identity without prematurely implementing F07 flows.
* Live Supabase metadata/staging validation may still need separate reauthorization or rollout approval later.

## Status

STATUS: PRD_READY
