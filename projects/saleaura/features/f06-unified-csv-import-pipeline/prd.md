Feature: F06 — Unified CSV Import Pipeline

Goal:
Make CSV ingestion deterministic, quota-aware, identity-safe, and operationally transparent for SaleAura V1.

Requirements:
1. Every CSV row must be normalized into one canonical product-input contract.
2. The parser must distinguish:
   - column missing from the file
   - column present but blank in the row
3. SKU values must be parsed and passed through so identity resolution can use current SKU and alias history.
4. Existing rows must still update when a file also contains over-quota new rows.
5. Only allowed new rows may insert; skipped rows must be reported explicitly.
6. Ingestion must run category normalization, eligibility evaluation, and CPU/GPU performance matching.
7. Import results must report inserted, updated, unchanged, failed, archived, and reactivated rows.
8. Source-managed missing rows for the same import source must mirror-archive safely, while manual archives preserve precedence.
9. Embeddings must refresh only when searchable content actually changes.

Acceptance:
- Parser preserves missing-vs-blank metadata.
- SKU enters the canonical import contract.
- Source-missing reactivation works even when row content is otherwise unchanged.
- Same-source missing rows can be mirror-archived and counted.
- Existing F03/F04/F05 regression checks remain green.

STATUS: PRD_READY
