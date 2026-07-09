Feature: F05 — CPU/GPU Performance Reference Catalog

Goal:
Provide a deterministic, traceable CPU/GPU performance authority for SaleAura V1 so upgrade, downgrade, ranking, and later comparison decisions can rely on verified category-local scores instead of price or AI guesswork.

Requirements:
1. Maintain a Supabase-backed reference catalog for CPU and GPU models.
2. Store canonical model, aliases, performance score, version, and traceable source/methodology notes.
3. Cover common V1 desktop consumer CPUs and GPUs; do not require exhaustive historical/server/mobile coverage.
4. Match inventory products deterministically using canonical/alias normalization only.
5. Persist verified scores only when the match is confident and category-local.
6. Mark ambiguous or unmatched CPU/GPU products as unverified rather than guessing.
7. Keep unmatched products searchable and inventory-visible when otherwise valid.
8. Do not allow owners to set or override arbitrary verified performance scores.
9. Make later upgrade/downgrade logic depend on verified scores for CPU/GPU categories.

Acceptance:
- Inventory rows can persist verified CPU/GPU performance metadata.
- Reference catalog exists in Supabase with versioned rows and trace metadata.
- Exact/alias matches verify correctly for common models.
- Generic or partial labels remain unverified.
- CPU/GPU ranking logic can prefer verified higher-performance parts without affecting non-CPU/GPU categories.

Out of scope:
- CSV pipeline sequencing/reporting (F06).
- Chat/widget comparison UX (F09).
- Final verified-build explanation flows (F10).

STATUS: PRD_READY
