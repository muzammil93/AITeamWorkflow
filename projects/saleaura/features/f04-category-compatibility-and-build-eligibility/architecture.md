# Architecture

## Feature ID and Name

`F04 — Category Compatibility and Build Eligibility`

## Architecture Mode

Delta architecture after QA-first baseline failure

## Inputs

* F04 baseline QA report ending `STATUS: FAIL`
* F04 delta PRD ending `STATUS: PRD_READY`
* SaleAura V1 master architecture
* Existing compatibility/build-generation services in `SaleAura-WebApp/`
* Current staging Supabase schema with F03 inventory normalization fields present

## Design Goals

* Preserve the existing deterministic compatibility foundation while making it strict enough for verified eligibility.
* Separate searchable inventory from verified build-eligible inventory.
* Make missing critical compatibility data fail closed.
* Add category-specific required-data validation and stable reason codes.
* Keep the eligibility model durable so later F05, F09, and F10 features can consume it without redefining compatibility authority.

## Component Design

### Canonical compatibility category layer

Introduce one canonical compatibility category contract for build-relevant products:

* CPU
* GPU
* Motherboard
* RAM
* Storage
* PSU
* Case
* Cooling

Normalization may accept synonyms from imports/UI, but persisted eligibility must use one canonical category value.

Products that cannot be safely normalized to one canonical category remain searchable only and receive an ineligibility reason such as:

* `category_unknown`
* `category_unsupported_for_verified_builds`

### Eligibility state on inventory

Persist a cached eligibility summary on `inventory` so later services do not recompute everything ad hoc on every customer request.

Recommended additive fields:

* `build_eligible BOOLEAN NOT NULL DEFAULT false`
* `build_ineligibility_reasons JSONB NOT NULL DEFAULT '[]'`
* `eligibility_rules_version TEXT NULL`

Optional extension if needed during implementation:

* `canonical_compatibility_category TEXT NULL`

Rules:

1. `build_eligible = true` only when the product passes category-required data validation and deterministic eligibility checks for the active rules version.
2. `build_ineligibility_reasons` contains stable machine-readable owner diagnostics.
3. Searchable visibility is not derived from `build_eligible`.
4. Eligibility caching is a summary; deterministic validators remain authoritative.

### Eligibility evaluation service

Create a focused service such as `inventory_eligibility_service.py` or equivalent extracted helper.

Responsibilities:

1. Normalize one product row into its canonical compatibility category.
2. Validate required normalized fields for that category.
3. Return:
   * `canonical_category`
   * `build_eligible`
   * `reason_codes`
   * `rules_version`
4. Distinguish:
   * missing required field
   * invalid field format/value
   * unsupported category
   * rule-blocked incompatibility prerequisite

This service owns per-product eligibility, not full multi-part build validation.

### Deterministic compatibility validator hardening

Refactor `CompatibilityValidator` so verified decisions use structured normalized data first.

Current acceptable direction:

* keep existing helper methods where useful;
* remove pass-through compatibility for unknown critical values in verified mode;
* keep legacy name inference only as a non-verified fallback hint where needed.

Required hardening:

1. CPU ↔ motherboard socket mismatch remains a hard failure.
2. Missing CPU socket or motherboard socket becomes ineligible/unverified, not allowed.
3. PSU ↔ GPU wattage mismatch remains a hard failure.
4. Missing PSU wattage or unresolved GPU power requirement becomes unverified for verified eligibility/build use.
5. GPU ↔ case clearance mismatch remains a hard failure.
6. Missing GPU length or case clearance becomes unverified where the rule is required for verified use.
7. Cooling socket/physical-fit rules become first-class checks.
8. Motherboard/case and PSU/case format-fit rules become first-class checks.
9. Storage-interface compatibility becomes first-class where normalized data exists.
10. CPU family/generation support is enforced only where the normalized rule data exists; otherwise it remains unverified rather than guessed.

### Required-data validator by category

Implement category-local required-field validators.

Suggested minimum rules:

* CPU:
  * require socket
  * require known included-cooler status or allow later cooling-required reason
* GPU:
  * require resolvable power requirement and physical length where applicable
* Motherboard:
  * require socket, chipset, RAM type, form factor
* RAM:
  * require RAM type and capacity
* Storage:
  * require storage type/capacity and interface/form factor where relevant
* PSU:
  * require wattage and connector data where known relevant
* Case:
  * require supported form factors and physical clearance fields relevant to verified fitting
* Cooling:
  * require supported sockets and physical/radiator sizing data relevant to its type

The validator returns reason codes such as:

* `missing_socket`
* `missing_chipset`
* `missing_ram_type`
* `missing_storage_interface`
* `missing_psu_wattage`
* `missing_gpu_length`
* `missing_case_gpu_clearance`
* `missing_cooling_socket_support`
* `invalid_dimension_format`

### Searchable vs eligible query boundaries

Current build candidate fetches query directly from `inventory` by owner, category, stock, and price.

Replace/extend this boundary so:

* generic search/comparison may use customer-visible inventory;
* verified-build candidate pools require:
  * exact owner
  * `is_active = true`
  * `stock > 0`
  * `build_eligible = true`
  * canonical category match

This separation must exist in both the incremental build generator path and any legacy strict/relaxed build-generator path still retained during transition.

### Strict verified mode vs legacy relaxed mode

Current code mixes:

* strict validation
* relaxed validation
* partial build fallbacks

F04 architecture requirement:

1. Verified build eligibility must use strict verified mode only.
2. Relaxed/partial logic may remain for transitional or non-verified recommendation flows only if clearly segregated.
3. No customer-facing verified-build claim may come from relaxed or unknown-data-passing logic.

If keeping legacy generators during transition:

* mark their outputs as non-verified when strict eligibility is not guaranteed;
* prevent them from being treated as verified builds by later F10 behavior.

### Cooling model

Cooling must become part of build composition and eligibility contracts.

Required behavior:

1. Engine/category normalization continues to recognize cooling.
2. Eligibility cache supports cooling products.
3. Verified build composition can satisfy cooling by either:
   * trusted included stock cooler data on the CPU; or
   * separate eligible cooling inventory.
4. If neither is proven, the build is not verified.

F04 only needs to establish the compatibility/eligibility contract and data model; F10 can own the final build UX/persistence.

### Owner-facing diagnostics

Owner inventory surfaces need stable reason data without exposing internal-only implementation detail to customers.

Recommended contract:

* `build_eligible: boolean`
* `build_ineligibility_reasons: string[]`
* optional derived safe messages on the server

Owner examples:

* “Missing CPU socket”
* “Motherboard form factor not provided”
* “Cooling socket support missing”
* “GPU power requirement cannot be verified”

Customer-facing surfaces should receive only safe high-level compatibility blockers where required later.

## Database / Migration Design

Create one additive F04 migration that:

1. adds cached eligibility fields to `inventory`;
2. optionally adds canonical compatibility category if needed beyond current `category`;
3. backfills current rows to deterministic default eligibility state;
4. computes `build_eligible = false` where required data is absent;
5. adds indexes for owner/category/active/stock/eligibility queries;
6. updates generated types and consolidated schema.

Backfill rules:

* no product row is deleted;
* missing critical normalized data defaults to ineligible, not eligible;
* existing searchable behavior is preserved where product visibility rules still allow it.

## API and Service Boundaries

### Flask / backend services

Own:

* canonical category normalization for verified eligibility;
* per-product eligibility evaluation;
* strict deterministic compatibility validation;
* verified-build candidate filtering;
* machine-readable reason-code generation.

### Next.js

Own:

* owner-facing inventory eligibility display;
* safe owner DTO exposure for eligibility state;
* customer-safe DTO shaping that excludes owner-only diagnostics unless explicitly required later.

### Supabase

Own:

* durable cached eligibility state;
* query/index support for verified-build candidate pools;
* additive persistence of reason codes and rules version.

## Test Strategy

Add focused F04 regression evidence across:

1. TypeScript tests for owner-facing eligibility DTO/contracts.
2. Python tests for:
   * category normalization
   * required-field validation
   * strict unknown-data rejection
   * deterministic compatibility rules
3. Executable database/schema validation for new eligibility fields and indexes.

Priority cases:

* CPU without socket → ineligible
* motherboard without socket/chipset → ineligible
* PSU without wattage for verified use → ineligible
* GPU without known length where case-fit rule is required → ineligible
* case without clearance data where fit must be proven → ineligible
* cooling without socket support → ineligible
* valid structured CPU+motherboard+RAM+PSU+GPU+case path → eligible
* searchable but ineligible product remains excluded from verified candidate pool

## Risks and Migration Notes

* Existing inventory may drop out of verified eligibility after hardening because current inference is permissive.
* That is expected and correct if owner-facing reasons are clear.
* The implementation should avoid silently breaking generic searchability while tightening verified-build correctness.
* F05/F10 must consume the same eligibility authority rather than duplicating rule logic.

## Status

STATUS: ARCHITECTURE_READY
