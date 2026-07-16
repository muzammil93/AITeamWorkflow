# QA Report — F05 CPU/GPU Performance Reference Catalog

## Scope

Existing-code verification of the versioned CPU/GPU reference catalog, deterministic matching, and safe unverified fallback defined by F05.

## Evidence — 2026-07-16

* `pnpm test`: 93/93 pass, including `tests/f05/performance-reference.test.ts` and `tests/f05/migration-performance-reference.test.ts`.
* `venv/bin/python -m unittest tests.test_f05_performance_reference ...`: 19/19 inventory tests pass, including the F05 Python reference tests.
* `pnpm exec tsc --noEmit`: pass.

## Result

The focused tests cover reference-row schema, exact/alias matching, and the safe behavior that leaves generic or partial labels unverified. No F05 regression was observed.

Attempt Result: PASS

STATUS: PASS
