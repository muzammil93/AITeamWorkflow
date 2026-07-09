# Product Requirements Document

## Feature Name

Category Compatibility and Build Eligibility Delta

## Feature ID and Execution Mode

`F04` — `QA_FIRST` baseline failure followed by delta implementation

## CEO Request

Verify and complete the existing SaleAura V1 category-wise compatibility validation and verified build-eligibility behavior for requirements `COMP-001` through `COMP-007`.

Reference: `projects/saleaura/saleaura-v1-release-plan.md`.

## Master Requirement References

* `COMP-001` through `COMP-007`
* Master PRD sections “Category-Wise Compatibility Verification and Build Eligibility”, “Compatibility Eligibility”, and verified-build prerequisites
* Master architecture compatibility/performance layer, cached eligibility state, deterministic compatibility engine, and owner-facing reason guidance

## Dependency References

* `F00 — Development Safety Baseline` is integrated.
* `F01 — Owner Identity and Onboarding` is integrated.
* `F02 — Plans, Billing, and Entitlements` is integrated.
* `F03 — Product Catalog and Manual Inventory` is the upstream product-model dependency and has established normalized product/source/state fields in staging and current product code.
* F04 must prepare durable compatibility eligibility for F05 performance matching, F09 conversation behavior, and F10 verified build generation without implementing those later feature scopes.

## Baseline QA Findings

* `F04-QA-001`: Searchable inventory is not separated from verified build-eligible inventory.
* `F04-QA-002`: Eligibility-required normalized data is incomplete and not formalized.
* `F04-QA-003`: Compatibility outputs are too coarse for stable owner remediation.
* `F04-QA-004`: Unknown critical compatibility data is treated as allowed instead of unverified.
* `F04-QA-005`: Deterministic rule coverage is materially narrower than the F04 requirement set.
* `F04-QA-006`: Cooling is recognized by the conversation layer but excluded from verified build composition.

## Clarifying Decisions

No CEO clarification is required for F04 behavior. The release plan, master PRD, and master architecture already resolve the intended product behavior.

F04 owns:

* category-wise eligibility requirements;
* owner-facing build-eligibility reasons;
* deterministic compatibility validation inputs and rules;
* searchable-vs-eligible separation;
* cached product eligibility state.

F04 does not own:

* F05 CPU/GPU performance reference catalog matching;
* F09 full conversation/search/comparison response design;
* F10 final verified build generation UX/persistence;
* F11 build modification logic;
* source import workflow redesign beyond what is necessary to compute eligibility safely.

## Finalized Scope

### In Scope

* Define canonical compatibility categories for verified build eligibility:
  * CPU
  * GPU
  * Motherboard
  * RAM
  * Storage
  * PSU
  * Case
  * Cooling
* Define required normalized data for each canonical category.
* Persist per-product build-eligibility state and machine-readable ineligibility reasons.
* Keep searchable inventory and build-eligible inventory distinct.
* Treat missing or invalid critical compatibility data as unverified/ineligible rather than compatible.
* Use deterministic compatibility rules only for verified decisions.
* Expand rule coverage to include:
  * socket/platform
  * family/generation where required
  * RAM type
  * storage interface/form factor where required
  * PSU wattage and connector requirements
  * motherboard/case form-factor fit
  * GPU/case clearance
  * cooling socket and physical-fit requirements
  * CPU cooling sufficiency based on known included-cooler data or separate cooling product
* Provide stable owner-facing reason codes and safe guidance for missing/invalid/incompatible products.
* Ensure verified-build candidate selection consumes only active, in-stock, customer-visible, build-eligible products.
* Preserve non-eligible products as searchable where appropriate.
* Add focused regression coverage for eligibility calculation and deterministic compatibility rules.

### Out of Scope

* CPU/GPU performance ranking or verified upgrade/downgrade scoring logic (F05).
* Final customer-facing build-generation orchestration, snapshot persistence, or UX contracts (F10).
* Build modification/change-set behavior (F11).
* Office/integrated-graphics verified builds.
* Multi-GPU, custom water loops, advanced multi-storage optimization, or advanced multi-RAM-kit optimization.
* Reworking all existing inventory import UX beyond the eligibility data it must now persist/report.
* Shared staging or production data migration without separate authorization.

## Eligibility Contract

SaleAura must distinguish three concepts:

1. searchable product
2. customer-visible product
3. verified build-eligible product

A product may be searchable and customer-visible while still not being eligible for verified builds.

A verified build-eligible product must satisfy all of the following:

* active
* in stock
* customer-visible
* mapped to one canonical compatibility category
* contains the category-required normalized compatibility data
* has no blocking invalid-data reason
* has passed deterministic eligibility evaluation for the current rules version

## Category Requirements

### Canonical category mapping

1. Every build-relevant product must resolve to one canonical category.
2. Category aliases may be normalized for input convenience, but verified eligibility must store/use one canonical category.
3. Products that cannot be mapped safely to a canonical category may remain searchable but are not build-eligible.

### Required normalized data by category

The minimum required normalized data must be explicit and machine-checkable.

1. CPU:
   * brand
   * socket
   * family/generation where required by compatibility rules
   * included-cooler status when known
2. GPU:
   * brand
   * wattage/power requirement or resolvable supported model mapping
   * physical length when relevant
   * required power connector data when relevant
3. Motherboard:
   * socket
   * chipset
   * RAM type
   * supported form factor
   * storage interface support where relevant
4. RAM:
   * RAM type
   * capacity
5. Storage:
   * storage type
   * storage interface where relevant
   * form factor where relevant
   * capacity
6. PSU:
   * wattage
   * form factor where relevant
   * connector availability where relevant
7. Case:
   * supported motherboard form factors
   * supported PSU form factors where relevant
   * max GPU length
   * CPU cooler clearance and/or radiator support where relevant
8. Cooling:
   * cooling type
   * supported CPU sockets
   * cooler height or radiator format where relevant

## Functional Requirements

### Searchable vs verified-eligible inventory

1. Search/build candidate selection for verified builds must not use all searchable inventory rows blindly.
2. Verified-build candidate selection must use only build-eligible rows.
3. Non-eligible products may remain searchable and customer-visible when they are otherwise valid products.
4. Owner inventory views must clearly show the difference between searchable and verified build-eligible state.

### Unknown and invalid data handling

1. Missing critical compatibility data must not be treated as compatible.
2. Invalid or unparseable critical compatibility data must not be guessed.
3. Unknown critical compatibility state results in ineligible/unverified status with stable reasons.
4. Name inference may help searchability or owner hints, but not verified eligibility authority.

### Deterministic compatibility rules

1. Verified compatibility decisions must be deterministic and rule-based.
2. AI may not decide hard compatibility or build eligibility.
3. Deterministic rules must cover:
   * CPU ↔ motherboard socket/platform
   * CPU family/generation ↔ motherboard support where required
   * RAM type ↔ CPU/motherboard platform
   * storage interface/form factor ↔ motherboard support where required
   * PSU wattage ↔ GPU minimum requirement
   * PSU connector capability ↔ GPU requirement where known
   * motherboard form factor ↔ case support
   * PSU form factor ↔ case support where relevant
   * GPU length ↔ case clearance
   * CPU cooling ↔ socket support
   * air cooler height or radiator format ↔ case support
4. If a rule cannot be safely evaluated because required critical data is missing, the product/build is not verified as eligible.

### Owner-facing reason model

1. Every ineligible product must have stable machine-readable reason codes.
2. Reason codes must distinguish:
   * missing required field
   * invalid normalized field
   * unsupported category mapping
   * incompatible deterministic rule
3. Owner-facing guidance must explain what needs correction without exposing raw internal-only details.
4. Customer-facing surfaces may expose only safe compatibility blockers where appropriate.

### Cooling in verified builds

1. Cooling is part of the verified build-eligibility model.
2. A verified build must have a valid CPU cooling solution.
3. CPU cooling may be satisfied either by:
   * a verified included stock cooler when that fact is known and allowed; or
   * a separate eligible cooling product.
4. If cooling sufficiency cannot be proven, the build is not verified.

## Security Requirements

* Verified eligibility must fail closed for missing critical data.
* Customer-facing product/build queries must not expose owner-only eligibility diagnostics.
* Owner-facing eligibility reasons must be derived from trusted server-side evaluation, not client guesses.
* No AI or browser input may override deterministic compatibility/eligibility results.

## Acceptance Criteria

1. `COMP-001` passes when verified eligibility is computed by canonical category rather than a generic pass-through flag.
2. `COMP-002` passes when each canonical category has explicit required normalized data and cooling is included in the contract.
3. `COMP-003` passes when stable reason codes and owner guidance exist for missing, invalid, and incompatible products.
4. `COMP-004` passes when searchable inventory and verified build-eligible inventory are distinct and used differently.
5. `COMP-005` passes when verified compatibility decisions remain deterministic and AI-free.
6. `COMP-006` passes when missing critical compatibility data yields unverified/ineligible status rather than compatibility.
7. `COMP-007` passes when deterministic validation covers socket, family, RAM, storage, power, connector, clearance, format, and cooling rules required for V1.
8. F04-targeted typecheck, tests, and database/schema evidence are recorded honestly.

## Risks and External Actions

* Existing inventory rows may remain searchable but ineligible until owners provide normalized compatibility data.
* CPU/GPU name-only inference cannot remain the authority for verified decisions; some current products may lose verified eligibility until normalized.
* F04 should keep the persisted eligibility model additive so F05/F10 can consume it without redefining the rules.

## Status

STATUS: PRD_READY
