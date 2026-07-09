Feature: F05 — CPU/GPU Performance Reference Catalog

Objective:
Implement the SaleAura V1 CPU/GPU performance reference catalog feature that was already approved in the release plan and master V1 PRD.

Locked scope:
- Maintain a Supabase-backed CPU/GPU performance reference catalog.
- Cover common desktop consumer CPU/GPU models relevant to V1.
- Match imported/manual CPU/GPU inventory products deterministically when possible.
- Persist verified category-local performance scores only on confident matches.
- Leave unmatched products searchable but unverified.
- Keep scores system-managed; owners cannot manually author arbitrary performance scores.

Out of scope:
- F06 unified CSV orchestration.
- F09 comparison UX and conversation wording.
- F10 full verified build explanation UX.

Dependencies:
- F03 complete enough to persist inventory rows and specs.
- F04 complete enough to provide durable compatibility eligibility and category normalization inputs.

STATUS: CEO_REQUEST_CREATED
