# Architecture — F10 Verified Build Generation

1. Restrict candidate queries to owner-scoped `is_active`, positive-stock, build-eligible inventory; CPU and GPU candidates additionally require verified positive reference scores.
2. Keep the existing bounded beam search, but validate every completed candidate with `CompatibilityValidator.validate_build` before selection.
3. Select only an under-budget complete build. If none exists, return a customer-safe `budget_too_low` or inventory/compatibility explanation instead of an over-budget recommendation.
4. Convert all eight components—including Cooling—into allowlisted `ProductItem` cards.
5. On success, write a canonical immutable `verified_build_snapshots` record containing sanitized component identity/pricing, request context, validation status, and schema version. If persistence fails, do not claim a verified build was created.
6. Protect snapshots with owner RLS. The service-role backend creates them; no public raw snapshot endpoint is introduced in F10.

STATUS: ARCHITECTURE_READY
