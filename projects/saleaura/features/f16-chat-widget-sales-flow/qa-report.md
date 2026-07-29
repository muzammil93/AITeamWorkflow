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

Attempt Result: FAIL

STATUS: BASELINE_FAIL
