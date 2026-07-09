Feature: F06 — Unified CSV Import Pipeline

Technical design:
1. Introduce a shared tabular-row parser that maps alias column names into the canonical inventory contract.
2. The parser must emit import metadata for:
   - missing fields
   - blank fields
   - source column used per canonical field
3. Feed parsed `sku` into the existing normalized persistence path so SKU/alias identity logic can work.
4. Preserve current two-phase upload behavior:
   - plan identity/update/insert decisions first
   - apply quota only to inserts
5. Track source row keys for the current import snapshot and mirror-archive same-source rows missing from the new file when manual archive precedence does not apply.
6. Force reactivation updates for rows currently marked `source_missing`, even when product fields are otherwise unchanged.
7. Reuse existing eligibility and performance-matching logic inside persistence normalization.
8. Keep embedding refresh hash-based and content-driven only.

Validation:
- focused parser unit tests
- existing F03/F04/F05 regression suites
- no schema migration required for this implementation slice

STATUS: ARCHITECTURE_READY
