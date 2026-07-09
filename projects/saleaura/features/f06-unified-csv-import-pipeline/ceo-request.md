Feature: F06 — Unified CSV Import Pipeline

Objective:
Implement the approved unified CSV import pipeline for SaleAura V1 on top of the existing inventory, eligibility, and performance infrastructure.

Locked scope:
- Parse CSV rows into one canonical product-input contract.
- Distinguish missing columns from explicitly blank cells.
- Resolve SKU / alias / safe source identity before insert classification.
- Update existing rows even when new-row quota is exhausted.
- Insert only allowed new rows and report quota skips.
- Validate categories and match CPU/GPU references during ingestion.
- Report inserted, updated, unchanged, failed, archived, and reactivated rows.
- Refresh embeddings only when searchable content changes.

Out of scope:
- F07 Google Sheets connection semantics beyond shared parser behavior.
- F09 conversation behavior.

STATUS: CEO_REQUEST_CREATED
