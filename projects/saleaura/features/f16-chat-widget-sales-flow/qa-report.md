# QA Baseline Report — F16 Chat Widget Sales Flow

## Existing-Code Audit — 2026-07-26

The existing public widget securely starts an anonymous owner-bound session, searches only active in-stock owner inventory, renders product/build/lead cards, and persists consented leads. It does not implement a product cart or final-cart lead workflow.

## Findings

* `F16-QA-001` — The owner-configured `welcome_message` is saved and shown in the owner preview, but the live widget renders a hard-coded welcome screen. `CART-001` fails; this is a regression against F08 branding behavior.
* `F16-QA-002` — Customer-safe product responses omit `stock`, while the card defaults missing stock to zero and visibly labels offered products `Out`. Retrieval correctly filters to active, positive-stock owner inventory, but the visible sales state is misleading. `CART-002` fails; F09 truthfulness is affected.
* `F16-QA-003` — Product cards have no effective Add to cart action. Their selection callback is unused and no customer-safe product identity can be retained for a trusted cart line. `CART-003`, `CART-004`, and `CART-012` fail.
* `F16-QA-004` — There is no cart session state, cart API, cart summary, remove action, or empty/recovery state. `CART-003` through `CART-006` fail.
* `F16-QA-005` — Lead capture can persist consented contact details and an existing build snapshot, but not final selected product/cart context, request versions, cart-item notification content, or a dashboard lead-details dialog. It may open from general purchase language rather than final-cart intent. `CART-006`, `CART-007`, `CART-013`, and `CART-014` fail.
* `F16-QA-006` — Existing staging Playwright coverage proves widget startup, owner-scoped in-stock search, comparison, and multilingual response behavior, but has no cart-to-lead normal, invalid, cancellation, isolation, or mobile journey. `CART-008` fails.
* `F16-QA-007` — The visible **I want this build** button has no connected action. A build is not expanded into trusted individual cart lines, and cart rows cannot identify a product already included in the latest build. `CART-009` and `CART-010` fail.
* `F16-QA-008` — Current build modification changes the protected chat build only after confirmation, but has no explicit cart-aware choice when earlier build components already exist in the cart. `CART-011` fails.

## Deferred Findings Outside F16

* `F16-DEF-001` — F10 documents say low budgets produce no build, while current code/test evidence can describe a closest over-budget build. This F10 documentation/behavior conflict must be resolved during the F16 F10 regression review before the feature receives final approval.
* `F16-DEF-003` — No live web product-data retrieval, source policy, citation display, or cache exists. The CEO deferred that integration.

## Result

The current widget is not production-ready for the approved cart-to-lead sales journey. A focused F16 delta is required. No test, code, database, provider, or production mutation occurred during this audit.

Attempt Result: BASELINE_FAIL

## Post-Implementation QA Attempt 1 — 2026-07-29

### Scope

Verified the implemented F16 cart-to-lead flow against the authorized staging
Supabase project through the local staging-connected application on desktop and
mobile. Supporting contract/unit checks were rerun for F08–F13 behavior affected
by the change.

### Passed Browser Evidence

* Desktop `customer-cart.spec.ts` — `E2E-033`, `E2E-034`, and `E2E-035`: 3/3
  passed in 2.0 minutes.
* Mobile `customer-cart.spec.ts` — `E2E-033`, `E2E-034`, and `E2E-035`: 3/3
  passed in 2.0 minutes.
* Desktop and mobile `E2E-036` passed: an exhausted lead quota produces a
  visible failure and no lead, then the dedicated owner's original counter is
  restored.
* The runs covered three-item CPU/keyboard/monitor cart creation, exact totals,
  quantity increase, removal, validation errors, cancellation without a lead,
  forged/replayed/expired offers, expired widget sessions, build expansion,
  build/cart separation, consented lead persistence, and same-lead request
  version updates.
* Adjacent desktop regressions passed:
  * `E2E-016` active/in-stock search: 1/1.
  * `E2E-017` catalog comparison: 1/1.
  * `E2E-018` English, Urdu, and Roman Urdu grounding: 1/1.
  * `E2E-019` complete supported-purpose builds: 1/1.
  * `E2E-020` budget/compatibility edge cases: 1/1.
* `E2E-021` long-chat soak was skipped because `E2E_LONG_CHAT=1` was not
  enabled; it is not required for the focused F16 attempt.

### Passed Supporting Evidence

* Seven Python unit tests passed for consent normalization, quota rejection,
  notification-failure preservation, notification cart formatting, and exact
  catalog-name search.
* Three focused search fallback checks passed, including safe generic-category
  relaxation and preservation of explicit GPU filtering.
* 21 Vitest checks passed across F08, F09, F10, F12, F13, and F16.
* Python syntax passed for 40 files.
* `pnpm exec tsc --noEmit` and `git diff --check` passed.
* Supabase read-back after cleanup confirmed the dedicated owner is restored to
  `starter`, with inventory limit/used `500/500`, 500 active in-stock products,
  and 500 inventory embeddings.

### Findings Verified

* `F16-QA-001` through `F16-QA-004`, `F16-QA-007`, and `F16-QA-008` are
  verified by desktop/mobile browser evidence.
* `F16-QA-005` is partially verified: cart lead persistence, request versions,
  notification-failure preservation, notification formatting, and the complete
  Dashboard details pass. Desktop and mobile `E2E-035` visibly verify email,
  source, consent, current cart quantities/totals, and request versions 1 and 2.
  Provider content receipt remains open.
* `F16-QA-006` is partially verified: focused desktop/mobile coverage is now
  present, including forced cart-save failure and quota exhaustion, but the
  PRD-required cross-owner browser branch remains open.

### Preserved Failed Attempt and Recovery

The first adjacent F09 regression command used legacy test setup that cleared
the dedicated 500-row staging inventory and changed the profile to the free
tier. QA stopped the run, restored the profile to active `starter`, re-imported
the supplied 500-row CSV through the normal application flow, and verified 500
active rows plus 500 embeddings through Supabase MCP. The affected search,
comparison, and language tests were repaired to use uniquely named temporary
rows with targeted cleanup; their reruns passed and left the catalog at exactly
500 rows.

The restore browser assertion itself timed out because it expected the obsolete
message `Successfully saved 500 rows`; the application correctly displayed
`Sync result: 500 added...`. The assertion now accepts the current success copy.
Database count, category, and embedding read-back prove that the restore
completed.

### Open QA Evidence / Blockers

* True cross-owner cart isolation cannot be executed because staging currently
  has only one authorized owner profile. A second authorized staging owner is
  required.
* Live email delivery succeeded during the cart lead runs. Live WhatsApp calls
  returned `401 Authentication Error`; the saved lead remained intact as
  required, but successful WhatsApp notification content is not verified.
* Supabase advisors still report pre-existing security and performance warnings,
  including permissive policies/GraphQL grants and RLS initialization-plan
  findings. They are not introduced by F16, but must be reconciled by the
  integrated readiness gate.
* The source/staging F16 migration version provenance difference remains open.

Attempt Result: QA_PARTIAL_PASS

STATUS: QA_IN_PROGRESS
