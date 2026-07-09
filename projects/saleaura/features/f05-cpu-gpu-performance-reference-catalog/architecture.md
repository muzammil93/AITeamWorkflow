Feature: F05 — CPU/GPU Performance Reference Catalog

Technical design:
1. Add a shared `performance_references` Supabase table with:
   - category (`CPU` / `GPU`)
   - stable reference key
   - canonical name
   - vendor
   - normalized performance score
   - alias list
   - source/methodology/licensing notes
   - catalog version
   - active flag

2. Extend inventory rows with additive performance fields:
   - `performance_score`
   - `performance_score_verified`
   - `performance_reference_category`
   - `performance_reference_key`
   - `performance_canonical_name`
   - `performance_catalog_version`
   - `performance_match_status`

3. Use deterministic matching in both write paths:
   - Next.js owner inventory create/update routes
   - Python inventory normalization/update/import paths

4. Matching strategy:
   - normalize inventory candidate text from name/chipset/description
   - check exact alias/model containment deterministically
   - prefer the longest unique alias hit
   - if no unique best match exists, persist `unmatched`

5. Keep scores system-managed:
   - no owner-editable verified score input
   - persisted performance metadata is derived only from the curated catalog

6. Immediate integration points:
   - CPU/GPU upgrade/downgrade logic may require verified scores
   - build ranking may use verified CPU/GPU performance preference while keeping compatibility authority unchanged

7. Safety:
   - unmatched CPU/GPU rows remain searchable and ordinary inventory-visible
   - only verified matches may drive genuine performance comparisons
   - non-CPU/GPU categories remain outside the F05 scoring authority

Validation:
- migration contract test
- TS matcher tests
- Python matcher tests
- regression check against existing F03/F04 tests

STATUS: ARCHITECTURE_READY
