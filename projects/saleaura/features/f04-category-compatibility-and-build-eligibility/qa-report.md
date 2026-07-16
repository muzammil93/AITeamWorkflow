# QA Report

## Feature ID and Name

`F04 — Category Compatibility and Build Eligibility`

## QA Mode

`EXISTING_CODE`

## Requirement IDs

`COMP-001`, `COMP-002`, `COMP-003`, `COMP-004`, `COMP-005`, `COMP-006`, `COMP-007`

## Input References

* `projects/saleaura/saleaura-v1-release-plan.md`
* `projects/saleaura/saleaura-v1-release-state.md`
* Existing product code in `SaleAura-WebApp/` compatibility/build-generation paths
* Connected staging Supabase metadata and migration ledger

## Attempt 1

### Environment

* Date: 2026-07-04 (Asia/Karachi).
* Product branch: `feature/f03-product-catalog-manual-inventory`.
* Product working tree: dirty with in-progress F03 changes; F04 baseline audit intentionally did not mutate product code.
* Node.js: `22.13.1`; pnpm: `10.11.1`.
* Python: `3.13.7`.
* Shared staging Supabase: connected through MCP; F03 migrations are present.
* Staging inventory table shape confirms F03 catalog fields such as `socket`, `chipset`, `ram_type`, `storage_capacity`, `wattage`, `form_factor`, `gpu_length`, `max_gpu_clearance`, and `cooler_height`.
* Staging table row counts are currently `0`, so this baseline is code-and-schema driven rather than data-driven.
* Production mutation: none.
* Staging mutation: none.

### QA Summary

FAIL.

The current system already contains meaningful deterministic compatibility logic. It has a dedicated `CompatibilityValidator`, an incremental build generator, a strict/relaxed/partial legacy build generator, normalized inventory fields for several hardware attributes, and machine-readable failure outputs such as `reason_code` and `missing_categories`. This is strong starting material.

It is not F04-ready. Build eligibility is not modeled as a first-class verified state, unknown critical attributes are frequently treated as allowed instead of unverified, cooling is recognized by the conversation layer but excluded from the build-eligibility contract, and the implemented rules cover only a subset of the required deterministic checks. The current code also mixes strict and relaxed compatibility modes in ways that blur the boundary between searchable inventory and verified build-safe inventory.

This is a QA-first baseline failure and consumes no repair cycle.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Evidence |
| --- | --- | --- |
| `COMP-001` | FAIL | Build generators require exact category strings in fixed orders such as `CPU`, `GPU`, `Motherboard`, `RAM`, `Storage`, `PSU`, `Case`, but there is no explicit canonical eligibility gate that classifies every inventory row as eligible vs merely searchable. |
| `COMP-002` | FAIL | Staging inventory has many normalized columns, but there is no explicit required-data contract for eligibility and cooling is absent from build generator required categories. |
| `COMP-003` | FAIL | The code returns some stable machine codes like `missing_inventory`, `budget_too_low`, and `compatibility_no_match`, but it does not return stable owner-facing missing/invalid reason codes for unknown critical compatibility data or per-component remediation guidance. |
| `COMP-004` | FAIL | Searchability and verified-build-eligibility are conflated: build candidate queries pull directly from active stock inventory without a separate eligibility state. |
| `COMP-005` | PASS | Existing compatibility/build validation is deterministic and rule-based; comments and code paths explicitly avoid AI judgement for compatibility enforcement. |
| `COMP-006` | FAIL | Multiple compatibility checks return allow/true when critical data is missing or unparseable, which treats unknown as potentially compatible instead of unverified. |
| `COMP-007` | FAIL | Implemented checks cover socket, RAM type, storage minimums, PSU wattage, and GPU clearance, but not the full required rule set for family, connectors, format, storage interface, and cooling compatibility. |

### Test Cases and Actual Results

1. Staging schema and migration recheck:
   * Procedure: inspect Supabase staging migration ledger and public table summaries.
   * Result: PASS — F03 migrations are present in staging and the `inventory` table includes compatibility-related columns such as `socket`, `chipset`, `ram_type`, `storage_capacity`, `wattage`, `form_factor`, `gpu_length`, `max_gpu_clearance`, and `cooler_height`.

2. Deterministic compatibility enforcement audit:
   * Procedure: inspect `backend/services/compatibility_validator.py`, `backend/services/incremental_build_generator.py`, and `backend/services/build_generator.py`.
   * Result: PASS — compatibility enforcement is rule-based and local to application code; no LLM compatibility judgement is used.

3. Canonical-category eligibility boundary:
   * Procedure: inspect category normalization and build-generator category requirements.
   * Result: FAIL — the engine normalizes categories including `cooling`, but build eligibility paths still hardcode only `CPU`, `GPU`, `Motherboard`, `RAM`, `Storage`, `PSU`, and `Case`.

4. Unknown-critical-data handling:
   * Procedure: inspect compatibility helper functions for missing socket, PSU, GPU length, and case clearance behavior.
   * Result: FAIL — missing socket, wattage/model, and clearance values generally return allow/true, so unknown data is not downgraded to unverified.

5. Searchable vs verified-eligible distinction:
   * Procedure: inspect build candidate fetch queries and output contracts.
   * Result: FAIL — build candidate queries read directly from `inventory` by `user_id`, `category`, `stock > 0`, and price, with no separate persisted eligibility state or precomputed verification boundary.

6. Stable compatibility failure reason audit:
   * Procedure: inspect `reason_code`, `reason`, and `missing_categories` outputs across build-generation paths and engine formatting.
   * Result: FAIL — outputs are useful but too coarse for F04; they do not distinguish unknown critical fields, incompatible normalized metadata, or owner remediation steps by category.

7. Required-rule coverage audit:
   * Procedure: compare implemented rules against `COMP-007` in the release plan.
   * Result: FAIL — no complete deterministic checks were found for CPU family compatibility, PSU/GPU connector requirements, motherboard/case form-factor fit, cooling socket/height/radiator compatibility, or storage-interface compatibility.

### Findings

#### `F04-QA-001`

* Requirement ID: `COMP-001`, `COMP-004`
* Severity: Critical
* State: `OPEN`
* Title: Searchable inventory is not separated from verified build-eligible inventory
* Evidence: `backend/services/incremental_build_generator.py` queries candidates directly from `inventory` using owner, category, stock, and price filters; no eligibility flag or verification state is required before build use.
* Expected: Inventory rows can remain searchable/customer-visible while build generation only consumes rows explicitly verified as build-eligible for their canonical category.
* Actual: The same inventory pool feeds both discoverability and compatibility-sensitive build generation.
* Suggested fix direction: Introduce a canonical eligibility contract and persisted verification state so build generation can fail closed without hiding otherwise searchable inventory.

#### `F04-QA-002`

* Requirement ID: `COMP-002`
* Severity: Critical
* State: `OPEN`
* Title: Eligibility-required normalized data is incomplete and not formalized
* Evidence: staging `inventory` columns include several normalized fields, but build generator required categories exclude cooling and there is no first-class required-field matrix by canonical category.
* Expected: Each canonical category has an explicit required-data contract for build eligibility, including cooling, with stable missing-data handling.
* Actual: Normalized fields exist opportunistically, but the code does not define which are mandatory for eligibility vs optional for search.
* Suggested fix direction: Define a category-by-category normalized eligibility schema and enforce it consistently on reads and writes.

#### `F04-QA-003`

* Requirement ID: `COMP-003`
* Severity: High
* State: `OPEN`
* Title: Compatibility outputs are too coarse for stable owner remediation
* Evidence: build paths return broad result codes such as `missing_inventory`, `budget_too_low`, and `compatibility_no_match`; engine responses summarize customer-facing failure but do not preserve detailed owner guidance.
* Expected: Stable reason codes distinguish missing normalized data, invalid normalized data, and hard compatibility mismatches, with actionable owner guidance.
* Actual: Failure reporting is present but too aggregated for F04’s eligibility and repair workflow.
* Suggested fix direction: Add category-local missing/invalid/incompatible reason codes and map them to owner guidance without exposing raw internals to customers.

#### `F04-QA-004`

* Requirement ID: `COMP-006`
* Severity: Critical
* State: `OPEN`
* Title: Unknown critical compatibility data is treated as allowed instead of unverified
* Evidence: `_check_cpu_mobo_compat` returns true when socket data cannot be determined; PSU/GPU and case/GPU checks also return true when required values are missing or unparseable.
* Expected: Missing critical compatibility attributes prevent verified eligibility until the row is normalized enough to prove safety.
* Actual: The code frequently treats “cannot determine” as pass-through compatibility.
* Suggested fix direction: Fail closed for eligibility, preserve searchable state separately, and surface deterministic missing-data reason codes.

#### `F04-QA-005`

* Requirement ID: `COMP-007`
* Severity: Critical
* State: `OPEN`
* Title: Deterministic rule coverage is materially narrower than the F04 requirement set
* Evidence: `compatibility_validator.py` currently validates CPU/motherboard socket, RAM/socket, purpose minimums, PSU/GPU wattage, and GPU/case clearance. No complete validation layer was found for CPU family, motherboard/case form factor, PSU connector sufficiency, cooling compatibility, or storage-interface rules.
* Expected: Deterministic validation covers socket, family, RAM, storage, power, connector, clearance, format, and cooling rules.
* Actual: Only a subset is implemented, leaving major verified-build checks undefined.
* Suggested fix direction: Expand the validator into a complete hard-rule engine and keep relaxed/search-only behavior out of verified eligibility.

#### `F04-QA-006`

* Requirement ID: `COMP-001`, `COMP-002`, `COMP-007`
* Severity: High
* State: `OPEN`
* Title: Cooling is recognized by the conversation layer but excluded from verified build composition
* Evidence: `backend/engine.py` normalizes `cooling` and exposes cooling spec keys, while build generator category orders and required categories omit cooling entirely.
* Expected: Cooling participates in the canonical category and eligibility model wherever required by the V1 verified-build contract.
* Actual: Cooling exists as searchable/spec-aware inventory data but is outside the current build-eligibility contract.
* Suggested fix direction: Decide and codify when cooling is required, how it is normalized, and which deterministic compatibility checks gate its eligibility.

### Security and Ownership Checks

FAIL.

There is no evidence that F04 adds an unsafe new public boundary yet, but the current build pipeline is too permissive for a verified-eligibility feature because missing critical specs silently pass compatibility checks. For F04, “fail closed for verified eligibility” is a correctness and trust requirement.

### Scope Compliance

This audit stayed within F04. It did not implement F05 performance scoring, F09 conversation behavior, or F10 final verified-build persistence. It also did not mutate staging or production data.

### Coverage Limitations

* Staging currently has zero inventory rows, so no live row-level compatibility fixtures were exercised there yet.
* This baseline did not create or modify any staging data because the goal was to establish the pre-implementation QA status first.
* No browser E2E flow was exercised in this pass.
* These limits do not change the deterministic code-contract failures above.

Attempt Result: FAIL

## Status

Attempt Result: FAIL

## Verification Attempt — 2026-07-16

Scope: existing-code verification of the persisted eligibility model and deterministic compatibility behavior.

Evidence:

* `pnpm test`: 93/93 pass, including six F04 eligibility tests and three migration-contract tests.
* `venv/bin/python -m unittest ...`: 19/19 pass, including the F04 Python eligibility suite.
* `pnpm exec tsc --noEmit`: pass.
* Inventory E2E coverage includes eligibility search, sorting, and pagination against staging inventory.

Result: The previous baseline findings F04-QA-001 through F04-QA-006 are not reproduced by the current deterministic rule, migration, and UI regression coverage. No new F04 finding was observed.

Attempt Result: PASS

## Status

STATUS: PASS
