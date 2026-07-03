# CEO Request

Begin `F03 — Product Catalog and Manual Inventory` under SaleAura V1 Release Plan version `1.0`.

## Execution Mode

`QA_FIRST`

Validate the existing inventory model, owner inventory UI, product identity rules, source tracking, editable-versus-read-only behavior, customer-facing product exposure, and raw inventory security before authorizing code changes.

If existing behavior passes, route it through existing-code review without Developer involvement. If baseline QA fails, create a delta PRD and architecture limited to the verified gaps, then implement, retest, and review them through the bounded-repair workflow.

## Authorized Requirements

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

## Constraints

* Preserve the integrated F00, F01, and F02 behavior at release-branch head `f8e48fb`.
* Preserve F02 quota and entitlement boundaries while extending inventory behavior.
* Track per-product source as `manual`, `csv`, or `google_sheets`.
* Treat Google Sheets products as read-only inside SaleAura for V1 and show a clear owner-facing explanation.
* Keep CSV-imported and manual products editable inside SaleAura.
* Support owner-scoped unique SKU identity and stable generated legacy SKUs for pre-existing rows without SKUs.
* Preserve product identity across SKU replacement and future import matching through aliases/reference data rather than loose name matching.
* Hide zero-stock and archived products from customer-facing outputs while retaining owner visibility.
* Do not implement F04 compatibility logic, F05 performance catalogs, F06 unified CSV pipeline, F07 Google Sheets connection flow, F08 widget/session changes, or deployment work except where F03 must expose safe reusable product DTO boundaries.
* Do not mutate shared staging, production, deployment systems, or external Google/Cloudinary configuration without explicit authorization.
* Use additive migrations only when baseline QA proves F03 database/security gaps and validate them through the F00 safety gate.

## Requested Outcome

Deliver evidence-backed F03 verification or the smallest approved delta needed to make SaleAura’s product catalog identity, source tracking, editable inventory workflow, customer-safe product exposure, and inventory security ready for dependent M2 features.

STATUS: CEO_REQUEST_CREATED
