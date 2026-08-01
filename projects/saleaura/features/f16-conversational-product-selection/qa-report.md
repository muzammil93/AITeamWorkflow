# QA Report

## Feature ID and Name

`F16-CONVERSATIONAL-PRODUCT-SELECTION` — Conversational Product Selection and
Cart Confirmation

## QA Attempt

`INITIAL_QA`

## Frozen Product Checkpoint

`e7151ea23c648778eb5ec12bc5a19f82c4651744`

The product `HEAD` matched this checkpoint before QA began. QA did not modify
product code. The only product working-tree changes were the Developer-disclosed
generated `backend/**/__pycache__/*.pyc` files and
`tests/e2e/qa-storage-state.json`.

## Scope and Source Artifacts

QA read and tested against:

* `ceo-request.md`
* `prd.md`, requirements `CPS-001` through `CPS-021`
* `architecture.md`
* `implementation-report.md`

The required boundary is LLM semantic interpretation plus deterministic,
session-owned validation and execution. Static product-reference phrase
matching is prohibited.

## Automated and Static Gates

### Python affected suites

Command:

`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest tests.test_f16_product_selection tests.test_f16_processing_status tests.test_f16_lead_notifications tests.test_f12_lead_consent tests.test_f09_customer_response tests.test_f09_language_contract tests.test_f09_quota_timing`

Result: `PASS` — 27 tests.

This covered the typed product-action contract, exact default/sorted state
resolution, stale/conflicting display rejection, pending confirmation and
secret boundaries, no static phrase matcher in the selection helper, the
captured semantic confirmation regression, processing statuses, lead behavior,
language contracts, quota timing, and the `Hello` name safeguard.

### TypeScript / Vitest

Command:

`pnpm vitest run tests/f16`

Result: `PASS` — 6 files, 25 tests.

This covered cart-state normalization, bounded selection/receipt state,
confirmation hashing, strict `confirm_add` input, browser-authored fact
rejection, processing-status and SSE contracts, product price display, existing
cart-sales-flow behavior, and chat trace IDs.

### Compilation and diff safety

* `pnpm exec tsc --noEmit` — `PASS`
* `git diff --check` — `PASS`
* `git diff --cached --check` — `PASS`

## Authorized Non-Production Supabase Evidence

Supabase staging MCP was used against the authorized non-production project.
The staging schema contains the real `inventory`, `chat_messages`,
`widget_sessions`, `profiles`, `leads`, and related tables with RLS enabled.
Recent API evidence showed the feature using real owner-bound widget sessions,
inventory reads, chat persistence, entitlement/quota RPCs, and cart-state
compare-and-swap writes.

A dedicated temporary lifecycle fixture exercised the real Next cart API and
staging database:

* Two concurrent deliveries of one confirmation both returned the persisted
  `added` outcome while the stored cart quantity remained exactly `1`.
* A price change returned `price_changed`, added zero lines, persisted the new
  trusted price, and removed the prior execution secret so fresh consent is
  required.
* Stock changed to zero returned `unavailable` and added zero lines.
* Expired and stale confirmations returned `409` and added nothing.
* An ended session returned `401`.

The temporary inventory and widget-session rows were deleted in cleanup.
Follow-up MCP verification returned zero matching fixture inventory rows and
zero matching fixture session rows.

No migration, production mutation, billing action, or deployment occurred.

## Playwright Evidence

Command:

`E2E_BASE_URL=http://localhost:5001 pnpm exec playwright test tests/e2e/conversational-product-selection.spec.ts --project=chromium --workers=1 --reporter=list`

Result: `PASS` — 1 test in 1.5 minutes against authorized staging.

The passing scenario proved:

* real customer-widget bootstrap and owner/domain authorization;
* an exact sorted visible row and natural first-card reference;
* trusted product-name/key confirmation;
* zero cart mutation before consent;
* semantic agreement producing typed `confirm_add`;
* one confirmed cart line, automatic cart opening, and keyboard focus;
* replay idempotency and forged-confirmation rejection;
* a reordered row with Roman Urdu selection/rejection;
* no lead-form diversion for the selection flow or `Hello`;
* cross-session rejection; and
* protected owner-preview session issuance and cart access.

Playwright also attached successfully to the already-open visible Chrome CDP
session on port `9224` and observed the authenticated staging inventory preview,
product cards, and active chat input. A later interactive rerun could not
proceed because that visible owner session expired: the first chat call returned
`401`, and refresh redirected the visible tab to `/auth`. This is recorded as
an authentication-state limitation, not a product finding, because the
authorized saved-state staging Playwright journey completed successfully.

The initial unprivileged Playwright attempt failed only because the sandbox
prohibited the test's temporary localhost embed server (`listen EPERM`).
The authorized rerun above passed and is the QA result.

## Requirement Assessment

### Proven

The combined unit, contract, staging integration, code-boundary inspection, and
passing Playwright evidence substantively prove:

* `CPS-001`, `CPS-002`, and `CPS-004` — model-backed typed semantics with no
  static product-reference phrase catalogue and no model-owned identity or
  mutation authority.
* `CPS-006`, `CPS-008`, `CPS-010`, `CPS-012`, `CPS-013`, `CPS-016`,
  `CPS-018`, and `CPS-019` — trusted pending confirmation, consent boundary,
  current-fact revalidation, exactly-once mutation, cart opening, session
  isolation, forged-action rejection, and greeting/name isolation.
* The exercised parts of `CPS-003`, `CPS-005`, `CPS-009`, `CPS-011`,
  `CPS-014`, `CPS-017`, and `CPS-020`, including sorted visible order,
  rejection, price/stock safety, protected preview bootstrap, Roman Urdu, and
  desktop focus.

### Not fully proven by the frozen automated/Playwright suite

The committed test evidence does not cover the complete required matrix:

* The single F16 Playwright scenario sorts before selection; it does not
  explicitly assert selection from the default visible order or construct the
  required assistant-prose/card-order mismatch.
* Ambiguous selection, agreement without pending state, a different product
  request while pending, malformed model output, and a stale display response
  are not exercised as customer-visible staging Playwright outcomes.
* Price-change, out-of-stock, offer-expiry, session-expiry, and concurrent
  delivery were proven at the real staging API/state boundary, but their final
  localized assistant recovery and closed-cart UI outcomes are not exercised
  in Playwright.
* The preview check proves protected session issuance and cart access, but not
  the complete preview selection → confirmation → add → cart-open journey.
* Pure Urdu product selection, in-session language switching, transcript
  resumption, mobile layout/accessibility, rate-limit/quota recovery, and
  search/cart/lead/build regressions are not all present in this feature's
  committed Playwright coverage.

## Findings

### `F16-CPS-QA-001` — Required customer-visible coverage matrix is incomplete

Severity: `HIGH`
Requirements: `CPS-003`, `CPS-005`, `CPS-007`, `CPS-009`, `CPS-011`,
`CPS-014`, `CPS-015`, `CPS-017`, `CPS-020`, `CPS-021`

The PRD and architecture require automated and staging Playwright evidence for
normal, boundary, ambiguous, declined, malformed, unauthorized, expired,
price/stock changed, duplicate, concurrent, quota/rate-limited,
session-lifecycle, multilingual, mobile/accessibility, and preview/public
parity behavior. The frozen commit contains one passing F16 Playwright scenario,
but it does not exercise the complete matrix listed above.

The independent staging API probes reduce implementation risk and found no
cart-integrity failure, but they do not replace the required customer-visible
Playwright assertions or committed regression coverage. Therefore `CPS-021`
cannot be certified, and the related partially covered requirements remain
release-blocking evidence gaps.

Expected resolution: add the smallest focused automated and staging Playwright
cases needed to close the listed gaps, using dedicated staging data and cleanup.
Do not change product behavior unless a new test exposes a functional defect.

## Regression and Safety Summary

No stable runtime defect was observed in the paths actually exercised. The
selection flow, deterministic execution boundary, idempotency, price/stock
safety, isolation, and existing focused regressions passed. The failure verdict
is based on missing mandatory acceptance evidence, not on the sandbox-only
localhost failure or the expired visible-Chrome login.

## Attempt 1 Verdict

Attempt Result: Core implementation checks and the focused authorized staging
journey passed, but mandatory `CPS-021` coverage is incomplete at the frozen
checkpoint. Route to Developer for bounded repair of test coverage, then rerun
QA.

## Attempt 2

### Execution Mode

`BOUNDED_REPAIR_QA`

### Frozen Product Checkpoint

`97eb41feff231d9bb8c1e38ec3b522aa84228ea3`

The product `HEAD` matched this checkpoint. The repair delta from
`e7151ea23c648778eb5ec12bc5a19f82c4651744` changed only:

* `tests/e2e/conversational-product-selection.spec.ts`
* `tests/e2e/support/staging-inventory.ts`
* `tests/f16/chat-request-id.test.ts`
* `tests/test_f16_product_selection.py`

The delta added 342 lines and removed 13 lines. It changed test coverage and
test support only; product behavior was unchanged. QA did not modify product
code. The product working tree retained only the previously disclosed generated
Python bytecode and browser storage-state changes.

### Deterministic Gates

The complete affected Python command from Attempt 1 was rerun.

Result: `PASS` — 29 tests.

The two added tests independently proved:

* agreement without pending state produces no confirmation;
* a different-product turn against pending state clarifies rather than
  confirming the old product;
* malformed structured model output fails closed to clarification; and
* price-changed, unavailable, and expired recovery fallbacks use only trusted,
  customer-safe facts and provide a safe next step.

Additional results:

* `pnpm vitest run tests/f16` — `PASS`, 6 files and 26 tests.
* `pnpm exec tsc --noEmit` — `PASS`.
* `git diff --check` — `PASS`.
* `git diff --cached --check` — `PASS`.

The added Vitest case proved that a bounded 429 response is returned without
calling the model backend.

### Expanded F16 Staging Playwright

Command:

`pnpm exec playwright test tests/e2e/conversational-product-selection.spec.ts --project=chromium --workers=1 --reporter=list`

Result: `PASS` — 2/2 tests in 4.1 minutes.

Scenario 1 passed in 2.7 minutes and independently proved:

* selection against the exact default visible order;
* a deliberate assistant-prose/card-order mismatch followed by selection of
  the actual first visible card;
* trusted name/key confirmation and zero pre-consent mutation;
* confirmed add, final acknowledgement, cart refresh/open/focus, and quantity
  one;
* replay idempotency, forged confirmation rejection, and cross-session
  rejection;
* Roman Urdu selection/rejection;
* agreement without pending state adds nothing;
* a different-product request while pending adds nothing;
* cancellation, ambiguity, and stale display context add nothing;
* `Hello` does not open or prefill lead capture; and
* protected preview session/cart access.

Scenario 2 passed in 1.4 minutes and independently proved:

* the complete authenticated owner-preview selection → confirmation → add →
  cart-open/focus journey;
* public customer-widget parity at a 390×844 mobile viewport;
* pure Urdu search and relative product selection;
* an English confirmation after the Urdu turn without changing trusted product
  identity;
* close/reopen transcript persistence;
* keyboard submission, focus, and viewport-bounded cart accessibility;
* visible, recoverable rate limiting; and
* real entitlement quota exhaustion, customer-safe disabling, and restoration.

### Deterministic Lifecycle Evidence

Attempt 1's real staging lifecycle probes remain applicable because the repair
changed no product behavior. Those probes independently proved:

* concurrent duplicate confirmation produces one stored cart quantity;
* price change adds nothing, refreshes trusted pending facts, and requires new
  consent;
* out-of-stock adds nothing;
* expired and stale confirmation add nothing;
* ended session is unauthorized; and
* all dedicated lifecycle fixtures were removed.

Together with the Attempt 2 deterministic recovery-copy tests and the passing
browser fail-closed scenarios, this is proportionate evidence for the
expiry/concurrency branches. QA does not require the probabilistic model to
emit one exact wording or action on every exploratory turn; it does require
schema validation, no unsafe mutation, and a recoverable result. Those
boundaries passed.

### Shared Staging Playwright Regressions

A proportionate shared set covered status/SSE, search, cart, lead, and build:

* `chat-processing-status.spec.ts` genuine search status/mobile clearing —
  `PASS` in 14.4 seconds.
* `customer-build.spec.ts` `E2E-019` complete-catalog customer-safe builds —
  `PASS` in 50.2 seconds.
* `customer-search.spec.ts` `E2E-016` active/in-stock grounded search —
  `PASS` in 24.4 seconds.
* `customer-cart.spec.ts` `E2E-033` session-bound cart, quantity, removal,
  invalid/forged/cross-session/expired offers, and cancelled lead — initial
  run reached all earlier cart assertions but one repeated exact-name LLM
  search returned clarification instead of a fresh offer. It failed closed
  with no unsafe mutation. The single bounded rerun `PASS`ed in 51.1 seconds.
* `customer-cart.spec.ts` `E2E-035` independent build cart, consented lead,
  cart update, version history, and owner dashboard visibility — `PASS` in
  56.9 seconds.

The one preserved first-run failure is model nondeterminism, not a stable cart
or selection defect: the same product had already been found and safely added
earlier in the journey, the failing repeated search returned no forged offer,
and the bounded rerun passed.

### Staging Cleanup and Restoration

Post-run MCP inspection found four duplicate owner-preview sessions from the
expanded F16 browser run that were not removed by token-based cleanup. QA
removed only those exact timestamped rows.

The proportionate pre-existing shared regressions left nine short-lived widget
sessions and one dedicated `QA F16 Cart` lead. Their inventory fixtures had
already been removed. QA removed the exact shared-test-window session and lead
rows.

Final MCP verification returned:

* recent test widget sessions: `0`;
* recent `QA F16 Cart` leads: `0`;
* recent `QA F16` inventory fixtures: `0`; and
* entitlement access: active, with 283 of 2,000 monthly AI responses used and
  1,717 remaining.

No production, migration, billing, payment, or deployment action occurred.

## Attempt 2 Finding Verification

### `F16-CPS-QA-001` — `VERIFIED`

The repaired committed suite now supplies the previously missing
customer-visible evidence for default order, deliberate prose/card mismatch,
no-pending/different-product/ambiguity/stale behavior, full preview parity,
pure Urdu and language switching, transcript resumption, mobile/accessibility,
rate/quota recovery, and the shared status/search/cart/lead/build regressions.

Price, stock, expiry, concurrency, replay, cross-session, and session-expiry
integrity are covered proportionately across real staging API/state probes,
deterministic schema/state tests, safe recovery-copy tests, and passing visible
browser outcomes. All observed model variability failed closed.

Finding State: `VERIFIED`

### `F16-CPS-QA-002` — Preview test cleanup misses duplicate bootstrap sessions

Severity: `LOW`  
Requirements: test hygiene supporting `CPS-021`

The repaired F16 scenarios attempt token-based widget-session cleanup, but
development-mode preview bootstrap created additional owner-preview sessions
whose tokens were not captured. Four rows remained after the passing run.
QA removed the exact rows and verified zero remaining test fixtures.

This is a non-blocking test-hygiene observation: widget sessions are bounded and
expiring, no product/customer data leaked, no authorization boundary failed,
and cleanup was completed. Future test maintenance should capture every preview
bootstrap response or delete sessions using a dedicated test-run marker.

Finding State: `OBSERVATION`

## Attempt 2 Requirement Assessment

`CPS-001` through `CPS-021` are now supported by proportionate deterministic,
authorized staging, and customer-visible browser evidence. The LLM interprets
natural language without a static product-reference phrase catalogue; trusted
code alone resolves session offers and mutates the cart after explicit consent.
Normal, multilingual, ambiguous, declined, stale, malformed, unavailable,
price/stock changed, duplicate, concurrent, unauthorized, quota/rate-limited,
session lifecycle, preview/public parity, mobile/accessibility, transcript,
lead, search, cart, status, and build boundaries are covered without requiring
probabilistic wording to be identical on every run.

## Final QA Verdict

Attempt Result: The coverage repair is independently verified at
`97eb41feff231d9bb8c1e38ec3b522aa84228ea3`. All deterministic gates, both
expanded F16 staging scenarios, and the proportionate shared browser regression
set pass, with the preserved model-variable search turn failing closed before a
successful bounded rerun. `F16-CPS-QA-001` is verified. The cleanup observation
is non-blocking and all QA fixtures were removed.

## Attempt 3

### Execution Mode and Frozen Checkpoint

`REVIEW_FINDING_QA`

Frozen product checkpoint:
`c94257db198ef1cf9b4a5b16d504f775f46da52d`

`HEAD` matched the checkpoint before testing. The repair delta from
`97eb41feff231d9bb8c1e38ec3b522aa84228ea3` changed the cart route, backend
selection writers, engine recovery guidance, one migration, and focused
tests/support. QA changed no product code and made no commit. The product
working tree retained only the disclosed generated Python bytecode and
`tests/e2e/qa-storage-state.json`.

### Deterministic and Static Gates

* Affected Python command — `PASS`, 31/31 tests.
* `pnpm vitest run tests/f16` — `PASS`, 7 files and 30/30 tests.
* `pnpm exec tsc --noEmit` — `PASS`.
* `git diff --check` — `PASS`.
* Local migration SHA-256 —
  `57bbac77efc21332d8a3734c7d471d5ffb2e62a2ee92aaf635fbb5c62cf3ea66`,
  matching the implementation report.

The new deterministic concurrency cases force an ordinary cart add to lose
its first compare-and-swap after a confirmation wins, reload the winner, and
preserve both cart lines plus the confirmation receipt without resurrecting
pending state. They also prove that expiry and three exhausted confirmation
CAS attempts create one persisted typed `expired` or `conflict` continuation.

Code-boundary inspection found all F16 cart-state writers using bounded CAS
loops: ordinary Next cart add/remove/quantity/clear, offer registration,
display acceptance, pending/reject/continuation state, and the Flask submitted
marker. No blind F16 `cart_state` update remains.

### Staging Migration and Permission Verification

Staging MCP lists migration
`20260730093327_f16_widget_cart_state_atomicity`.

The deployed definitions independently verified:

* `compare_and_swap_widget_cart_state` scopes the update by session, owner, and
  exact expected JSON state;
* `record_widget_cart_terminal_result` locks the row, deduplicates the
  confirmation receipt, bounds receipts, clears only the matching pending
  authority, and preserves a newer pending/display state;
* both functions are `SECURITY DEFINER` with `search_path=''`;
* `service_role` has execute permission; `authenticated`, `anon`, and
  `PUBLIC` do not.

The staging function-definition SHA-256 values were
`6f0b79ca98770086927e9dc0462540de360827bb1b7f6ce4f72e6a29cd24a82c`
for CAS and
`188f4fa7c0d8f35e356e1988765b0d89abea57a3f70dc6ff63c9c9d7746e6651`
for terminal receipt persistence. Supabase advisors reported no new warning
against either function; the returned security/performance notices concerned
pre-existing objects.

### F16 and Shared Browser Evidence

The full F16 staging Playwright file produced:

* primary customer selection/confirm/add/open-cart — `PASS`;
* expired typed localized recovery/cart closed — `PASS`;
* owner-preview parity — first run `FAIL` because the assistant answered both
  the relative selection and later consent with a generic cart-review sentence,
  so no cart opened.

The one allowed bounded rerun of only owner preview `PASS`ed in 1.4 minutes.
The first failure remains evidence of model variability and is not discarded.

Proportionate shared staging results:

* genuine processing status/mobile clearing — `PASS`;
* build `E2E-019` — `PASS`;
* search `E2E-016` — `PASS`;
* lead/cart independence `E2E-035` — `PASS` when run separately after serial
  skip;
* cart `E2E-033` — `FAIL` on its first product lookup because the model
  returned structured `message` rather than `products`. The failure occurred
  before cart mutation. No rerun was used.

The deterministic cart boundary is stable, but the two first-run browser
failures motivated the required assistant-response audit below.

## 10-Conversation Assistant Response Audit

Ten distinct customer-widget sessions were run against authorized staging.
Each conversation started with clean session context. The order below is the
actual visible card order captured from the DOM; prose and typed outcome are
reported separately. First-run failures count even when a later explicit turn
allowed recovery testing.

### Conversation 1 — Normal discovery and default ordinal

Visible order:
`TeamGroup RAM-7731L`, `Crucial RAM-4178L`, `TeamGroup RAM-5096B`,
`TeamGroup RAM-5469O`, `Kingston RAM-9224L`, `TeamGroup RAM-1298L`,
`G.Skill RAM-6517Y`, `Corsair RAM-3254B`, `Crucial RAM-5193G`,
`Kingston RAM-7878U`.

* User: `Show me the RAM products available in this shop.`
* Assistant: `Here are the available RAM products in the shop:` followed by
  accurate names, capacities, speeds, and PKR prices for the first five.
* User: `Can I get the first one?`
* Assistant: `Excellent! I'd be happy to help you place an order. Please share
  your contact details and I'll connect you with our sales team.`

Discovery grounding and card facts were correct. The ordinal was wrongly
classified as `lead_capture`; no product was named and no confirmation was
created.

Severity: `HIGH`  
Violated principle: session-context continuity and named-product confirmation.  
Expected: `To confirm, you want TeamGroup DDR5 RAM RAM-7731L (RAM-7731L)
for PKR 94,335. Should I add it to your cart?`

### Conversation 2 — Sorted ordinal and prose/card mismatch

Discovery prose first was `TeamGroup RAM-7731L`. After client price-ascending
sort, visible order began `Kingston RAM-7878U`, `Crucial RAM-5193G`,
`G.Skill RAM-6517Y`, `Crucial RAM-4178L`; therefore the visible first card was
unambiguously Kingston.

* User: `I want the first product visible in the row now.`
* Assistant: the same contact-details/lead-capture sentence as Conversation 1.
* User: `No, do not add it.`
* Assistant: `I found the TeamGroup DDR5 RAM RAM-7731L ... priced at
  \u20a894,335 ... an excellent choice.`

Nothing unsafe was added, but the assistant ignored the browser-authored order,
then treated rejection as a fresh recommendation for the prose-first product
and appended another product card.

Severity: `HIGH`  
Violated principle: browser order is authoritative; rejection must not trigger
an unrelated selection.  
Expected: name `Kingston DDR4 RAM RAM-7878U` and ask confirmation; on rejection,
state that Kingston was not added.

### Conversation 3 — Different product while pending

After grounded discovery:

* User: `I want the first visible product.`
* Assistant: `Please confirm your selection of the TeamGroup DDR5 RAM
  (SKU: RAM-7731L) for 1 unit at a price of 94,335 PKR. Do you want to proceed
  with this purchase? Yes or No?`
* User: `Actually I want a different product from this row.`
* Assistant: `It seems that nothing was added to your cart. Please feel free
  to select the product again if you'd like!`

The first confirmation was correct and grounded. The second response safely
avoided adding the old product, but discarded useful visible-row context and
did not ask which alternative the user meant.

Severity: `MEDIUM`  
Violated principle: maintain context while clearing/replacing pending intent.  
Expected: `Nothing was added. Which visible product would you like instead
(for example, the second or third card)?`

### Conversation 4 — Ambiguous reference

With the same ten cards visible:

* User: `I want that one.`
* Assistant: `Please confirm your selection of the TeamGroup DDR5 RAM
  (SKU: RAM-7731L) for 1 unit at a price of 94,335 PKR. Do you want to proceed
  with this purchase? Yes/No?`

The assistant silently interpreted an unanchored `that one` as position 1.

Severity: `HIGH`  
Violated principle: ambiguous references must fail closed to clarification.  
Expected: `Which visible product do you mean? You can say its name or position.`

### Conversation 5 — Consent without pending selection

No cards or pending authority existed.

* User: `Yes, add it to my cart.`
* Assistant: `I'm here to help! Could you please clarify what specific
  information or assistance you need regarding candidate positions?`

The cart stayed empty, but `candidate positions` is unrelated hallucinated
context.

Severity: `HIGH`  
Violated principle: no-pending consent must be grounded and helpful.  
Expected: `There is no product awaiting confirmation. Please search for or
select a product first.`

### Conversation 6 — Explicit reject/cancel

The assistant correctly named `TeamGroup DDR5 RAM RAM-7731L`, SKU, quantity,
and PKR 94,335 when asked for the first product.

* User: `No, cancel this selection.`
* Assistant: `It seems that nothing was added to your cart. Please feel free
  to select the product again if you need assistance!`

The result was safe and correct. Wording was indirect and omitted the product
name, but the pending selection was cleared and the cart remained empty.

Severity: `LOW`  
Expected improvement: `No problem—TeamGroup DDR5 RAM RAM-7731L was not added.`

### Conversation 7 — Expired confirmation

The first natural `Can I get the first one?` attempt was misclassified as lead
capture and is retained as another instance of Conversation 1's high-severity
failure. An explicit position-1 request then correctly created a trusted
confirmation for TeamGroup `RAM-7731L`.

After consent, the staged authority was expired before execution.

* User: `Yes, add that exact product.`
* Assistant: `It looks like the TeamGroup DDR5 RAM (SKU: RAM-7731L) is no
  longer available. Nothing was added to your cart. Please select the product
  again.`
* Typed result: `expired`; `open_cart=false`; cart items `[]`.

Recovery result: `PASS`. It named the product, made no false add claim, and
gave a safe next step.

### Conversation 8 — Price changed after confirmation

The assistant correctly confirmed TeamGroup `RAM-7731L` at PKR 94,335.
Inventory was then changed to PKR 94,472 before execution.

* User: `Yes, add that exact product.`
* Assistant: `The price for the TeamGroup DDR5 RAM (SKU: RAM-7731L) has changed
  to 94,472 PKR. Would you like to confirm this selection? Yes or No?`
* Typed result: `price_changed`; `open_cart=false`; cart items `[]`.

Recovery result: `PASS`. New consent is required. The old product card remained
visible at PKR 94,335, so a future UI improvement should refresh or mark it
stale, but the trusted response and cart behavior were correct.

### Conversation 9 — Product unavailable

Discovery cards and structured products used `PKR`/`Rs`, but assistant prose
rendered prices with Philippine peso `₱`.

The assistant then correctly confirmed visible-first `Crucial DDR4 RAM
RAM-4178L` at PKR 28,325. Stock was set to zero before execution.

* User: `Yes, add that exact product.`
* Assistant: `The product "Crucial DDR4 RAM RAM-4178L" is currently
  unavailable, so nothing was added to your cart. Please select the product
  again or choose an alternative.`
* Typed result: `unavailable`; `open_cart=false`; cart items `[]`.

Unavailable recovery: `PASS`.  
Currency prose/card mismatch severity: `HIGH`.  
Violated principle: customer prose must use the trusted owner currency and
agree with structured cards.  
Expected: use `PKR` or `Rs`, never `₱`.

### Conversation 10 — Name, Urdu, Roman Urdu, language switch, resume

* User: `Hello, my name is Ahmed. Please show me RAM products.`
* Assistant addressed `Ahmed` correctly and returned grounded products, but
  used Nigerian naira `₦` in prose while every structured product/card was
  `PKR`/`Rs`.
* User: `مجھے پہلی نظر آنے والی پروڈکٹ چاہیے۔`
* Assistant: `کیا آپ "TeamGroup DDR5 RAM RAM-5096B" کی 1 یونٹ کی خریداری
  71,901 PKR میں تصدیق کرنا چاہتے ہیں؟ ہاں یا نہیں میں جواب دیں۔`
* Close/reopen restored the prior transcript and exact Urdu turn.
* User: `Nahi, is selection ko cancel kar dein. Ab English mein jawab dein.`
* Assistant: `It seems that nothing was added to your cart. Please feel free
  to select the product again.`

Name context, Urdu selection, product identity, transcript resume, Roman Urdu
cancel, and requested English switch all passed. The prose currency
hallucination is `HIGH` severity and violates factual/card alignment. Expected:
all discovery prose must retain `PKR`/`Rs`.

### Audit Summary

Cart safety remained fail-closed in all ten conversations, and trusted recovery
for expired, price-changed, and unavailable products was correct. However,
first-run assistant behavior is not release-stable:

* natural ordinal selection was diverted to lead capture in Conversations 1,
  2, and the first Conversation 7 attempt;
* an ambiguous reference silently selected position 1;
* a no-pending consent hallucinated `candidate positions`;
* a different-product request lost useful visible context; and
* two discovery responses contradicted PKR cards with `₱` or `₦`.

These are customer-visible semantic/factual failures, not harmless wording
variation.

## Attempt 3 Findings

### `F16-CPS-REV-001` — Shared cart-state writers can overwrite consumed or cleared selection state

Finding State: `VERIFIED`

The repair makes shared writers CAS-based, deterministic interleavings preserve
both effects, receipts and cleared pending state, and deployed staging grants
are service-role-only. No lost cart effect or resurrected pending/display state
was observed.

### `F16-CPS-REV-002` — Expiry and exhausted-CAS paths bypass typed localized recovery

Finding State: `VERIFIED`

Expired and exhausted-CAS paths persist a bounded typed terminal receipt. Unit,
staging migration, and real continuation evidence prove replayable
`expired`/`conflict` outcomes, localized safe next steps, no cart opening, and
no item addition.

### `F16-CPS-QA-003` — Natural reference and pending-intent interpretation is not reliable

Severity: `HIGH`  
Requirements: `CPS-001`, `CPS-003`, `CPS-005`, `CPS-007`, `CPS-009`,
`CPS-018`, `CPS-021`

Across independent first-run conversations, clear default/sorted ordinal
requests were repeatedly diverted to lead capture, an ambiguous reference
silently selected position 1, and no-pending consent produced unrelated
hallucinated context. Owner-preview also failed its first run for the same
semantic layer before passing the bounded rerun.

Expected resolution: strengthen the LLM product-action contract/prompt and
validation so visible-product references produce typed `select`, genuinely
ambiguous references produce typed clarification, and no-pending consent cannot
fall through to unrelated general/lead text. Add deterministic captured-model
regressions for the exact failing outputs; do not add a static phrase catalogue.

Finding State: `OPEN`

### `F16-CPS-QA-004` — Assistant prose can contradict trusted card currency

Severity: `HIGH`  
Requirements: `CPS-004`, `CPS-005`, `CPS-017`, `CPS-021`

Two real discovery conversations rendered `₱` and `₦` while structured
products and visible cards correctly carried `PKR`/`Rs`. Product names and
numeric prices were grounded, but the wrong currency symbol materially changes
customer meaning.

Expected resolution: ensure customer prose is composed or post-validated
against trusted owner currency, and add model-output regression cases for
foreign-symbol substitution.

Finding State: `OPEN`

### `F16-CPS-QA-002` — Preview test cleanup misses duplicate bootstrap sessions

Finding State: `OBSERVATION — STILL PRESENT`

Current browser runs again left duplicate owner-preview and shared-test
sessions. QA deleted 18 exact QA session IDs and the one exact E2E-035 lead.
This remains non-blocking test hygiene, but the committed cleanup helper still
does not capture every development-mode preview bootstrap.

### Cleanup and Restoration

The ten-conversation harness deleted its token-hashed sessions in `finally` and
was removed from the product tree after use. MCP then removed only the 18 exact
identified QA sessions and exact lead
`f177703b-e64d-4088-9425-26b715e22031`.

Final verification:

* exact identified sessions remaining: `0`;
* exact identified lead remaining: `0`;
* QA localhost/127.0.0.1 hosts remaining: `0`;
* QA F16/Search/AUTO inventory fixtures remaining: `0`;
* touched `RAM-7731L`: PKR 94,335, stock 100, active;
* touched `RAM-4178L`: PKR 28,325, stock 100, active.

No migration, deployment, production, billing, payment, or subscription
mutation occurred.

## Attempt 3 Verdict

The two Reviewer repair findings are independently verified and the
deterministic cart-execution boundary is safe. Release QA nevertheless fails
because the required ten-conversation audit exposed repeatable first-run
customer-visible semantic and currency-grounding defects.

The feature has reached its recorded bounded repair limit (`2/2`). The
Orchestrator must not silently dispatch a third repair. It should record the
release as not ready and escalate `F16-CPS-QA-003` and `F16-CPS-QA-004` for an
explicitly authorized new repair cycle/scope decision. If a new cycle is
authorized, rerun the full F16 browser matrix and ten-conversation audit.

Attempt Result: FAIL

## Attempt 4 — Independent Cycle-3 QA

### Scope and checkpoint

QA independently evaluated product checkpoint `39edc8a fix(f16): verify
semantic product references` using the direct F16 PRD, architecture, and
Developer handoff. QA did not modify product code or any non-QA artifact.

Supabase MCP connectivity was confirmed before the run. The audit used the
authorized non-production staging project through the isolated services:

* backend `http://127.0.0.1:8001`;
* frontend `http://localhost:5002`; and
* dedicated QA owner/session state supplied by the staging configuration.

The CEO's services on ports `8000` and `5001` were not touched. No production,
migration, billing, payment, or deployment action occurred.

### First-run audit protocol

The first command accidentally selected the repository's default local
Playwright profile rather than `playwright.staging.config.ts`. Its widget iframe
was blank and it failed before an assistant conversation could be evaluated.
That non-acceptance environment error is preserved at:

`/private/tmp/saleaura-f16-e2e.PtrkQ6/test-results/inventory-e2e/.last-run.json`

It is not used as staging product evidence and was not rerun under that
profile. QA then ran the correctly configured staging audit once, with no
retries:

```text
E2E_INVENTORY=1 E2E_TARGET=staging
E2E_QA_USER_ID=7a2cb1fb-475b-4f4d-af58-7e1497e01cb2
E2E_STORAGE_STATE=tests/e2e/qa-storage-state.json
E2E_BASE_URL=http://localhost:5002 E2E_F16_TEN_CHAT_AUDIT=1
pnpm exec playwright test --config=playwright.staging.config.ts \
  tests/e2e/conversational-product-selection.spec.ts \
  --project=desktop-chromium --workers=1 --reporter=list \
  --grep 'CPS cycle-3 audit'
```

Result: `PASS` — 1 test, all ten clean first-run conversations completed.
No Playwright retry was enabled or used. The result file is:

`/private/tmp/f16-independent-qa-audit/.last-run.json`

The ten first-run conversation recordings are retained under:

`/private/tmp/f16-independent-qa-audit/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/`

### Assistant-response and behavioural assessment

The audit evaluated the assistant's content as well as API/cart state. All
expected customer-facing outcomes were present on the first valid staging run:

| Conversation | Expected assistant behaviour | Observed first-run result |
| --- | --- | --- |
| 1 | Default visible ordinal names the first card, SKU, quantity, and PKR before consent | PASS — `Can I get the first one?` produced a named TeamGroup confirmation for quantity 1 and `71,901 PKR`; cart stayed unchanged. |
| 2 | Sorted visible ordinal follows browser order; rejection retains product context | PASS — confirmation named sorted first `Kingston DDR4 RAM RAM-7878U`, quantity 1, `10,864 PKR`; rejection response included that product. |
| 3 | Different-product request never confirms the previous pending item | PASS — assistant asked which other visible product was intended and retained the row. |
| 4 | Unanchored `that one` fails closed | PASS — `Please clarify which visible product you mean. I have not added anything.`; cart remained empty. |
| 5 | Consent without pending selection is grounded and helpful | PASS — `There is no product waiting for confirmation. Please choose a visible product by name or position first.` No internal `candidate positions` wording. |
| 6 | Explicit cancellation names the declined product and adds nothing | PASS — assistant said the named TeamGroup product was not added; cart remained empty. |
| 7–8 | Fresh visible-row selection remains product/card/currency grounded | PASS — each confirmation carried the exact visible product, quantity 1, PKR price, and no pre-consent cart mutation. |
| 9 | Discovery prose and cards agree on PKR | PASS — at least three PKR product cards and no foreign-currency marker in prose. |
| 10 | Name context plus Urdu selection and Roman-Urdu cancellation preserves product/language context | PASS — Urdu confirmation named the visible TeamGroup product, quantity, and PKR price; the later cancellation response retained the product name and switched to English. |

Visible recording review confirms the central quality fixes are customer-safe
and intelligible: no lead-form diversion for a product reference, no guessed
selection for unanchored deixis, no schema/internal wording, and no `₱`/`₦`
currency contradiction. Confirmation copy is concise enough to be usable and
contains the necessary distinguishing product key, quantity, and trusted PKR
price. The non-selection clarifications are direct and do not imply a cart
mutation.

### Prior findings re-evaluation

* `F16-CPS-QA-003` — `CLOSED_BY_ATTEMPT_4`: all relevant first-run audit
  categories passed, including default/sorted ordinals, ambiguous deixis,
  pending replacement, no-pending agreement, explicit rejection, and
  Urdu/Roman Urdu session context.
* `F16-CPS-QA-004` — `CLOSED_BY_ATTEMPT_4`: discovery and confirmation prose
  matched the trusted PKR card currency in the fresh audit; no foreign marker
  reached the shopper.
* `F16-CPS-QA-002` remains a non-blocking test-hygiene observation. This QA
  run used the test's `finally` cleanup and did not observe a functional
  selection/cart defect.

### Attempt 4 verdict

The correctly configured, one-shot authorized staging audit is green and
provides fresh customer-visible evidence for the exceptional cycle-3 repair.
The earlier failed attempts remain recorded above and were not overwritten.
Route the checkpoint to independent Reviewer evaluation.

STATUS: PASS

## Attempt 5 — CC-005 Routing-Boundary QA

### Scope and checkpoint

QA evaluated the CEO-authorized final routing-boundary repair at product
checkpoint `22b84fa fix(f16): gate generic routing after product actions`.
QA did not modify product code, release/review/implementation artifacts, or
rerun the one-shot staging audit.

### Focused deterministic routing evidence

Current code makes the general router reachable only through a validated
`product_action.v2` result with `action=no_action` and
`reason=not_product_action`. The focused test coverage at
`tests/test_f16_product_selection.py:1610` proves that the generic router is
not called for select, ambiguous, uncertain, confirm, reject,
different-product, or no-pending product outcomes; a valid explicit
non-product result is routed to the generic handler; and malformed no-action
data cannot release it.

Command:

`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest tests.test_f16_product_selection`

Result: `PASS` — 33 tests, including the three focused routing-boundary tests.

### Retained one-shot staging evidence

The retained isolated audit at
`/private/tmp/f16-qa-final-22b84fa-corrected` is not a passing acceptance
run. Its preserved `.last-run.json` records `status: failed`. Its Playwright
trace records that widget bootstrap returned HTTP `503` before the widget
could load; the test then ended while waiting for its first bootstrap response.
No chat conversation, assistant reply, product selection, cart action, or
customer-visible router outcome was evaluated in that run.

This is an environment/bootstrap failure, not evidence of a routing defect in
the `22b84fa` code. It nevertheless cannot certify the required real staging
customer outcome or replace the one-shot audit. The earlier `39edc8a` audit
remains historical evidence only because CC-005 changes the request-routing
boundary under test.

### Finding

#### `F16-CPS-QA-005` — CC-005 staging acceptance run did not reach the widget

Severity: `HIGH`
Requirements: `CPS-002`, `CPS-018`, `CPS-021`

The retained one-shot CC-005 staging run failed at widget bootstrap with HTTP
`503`, before a conversation could be exercised. Automated unit coverage
supports the routing gate, but it does not prove that the real staging
bootstrap/chat path applies that gate correctly. A correctly configured
fresh staging run is required, preserving its first output and avoiding a
retry of this failed run.

Finding State: `OPEN`

### Attempt 5 verdict

The routing-boundary unit tests pass. The retained one-shot staging audit
failed before product behavior was exercised, so QA cannot certify CC-005 for
release. Preserve this environmental acceptance failure and route the
checkpoint to a fresh, correctly configured staging QA run before Reviewer
re-evaluation.

Attempt Result: FAIL — staging acceptance evidence unavailable after bootstrap
HTTP `503`.

## Attempt 6 — CC-005 Valid Isolated Staging Acceptance

### Scope and environment

QA evaluated the CEO-authorized CC-005 routing-boundary repair at product
checkpoint `22b84fa fix(f16): gate generic routing after product actions`.
The isolated services were confirmed healthy immediately before the valid run:
backend `http://127.0.0.1:8001/health` returned `200`, and frontend
`http://localhost:5002` responded successfully. The CEO-owned services on
ports `8000` and `5001` were not touched. QA used the saved dedicated staging
owner state and the authorized non-production Supabase configuration.

Attempt 5 remains an environmental, non-acceptance record: its HTTP `503`
occurred before widget bootstrap and before any conversation. It is not
relabelled as a passing run.

### Focused routing boundary

Command:

`PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest tests.test_f16_product_selection.ProductActionRoutingBoundaryTests`

Result: `PASS` — 3/3 tests. The generic router was not called for select,
ambiguous, uncertain, confirm, reject, different-product, or no-pending
product outcomes. It ran only for the validated explicit
`no_action/not_product_action` outcome; malformed no-action data did not
release it.

### One-shot staging ten-conversation audit

The first invocation selected an unsupported Node 18.2 runtime and exited
before Playwright launched; it opened no browser or widget and sent no chat
turn. QA then selected the project's Node 22.13.1 runtime and ran the one
actual audit once, with Playwright retries disabled:

```text
E2E_INVENTORY=1 E2E_TARGET=staging
E2E_QA_USER_ID=7a2cb1fb-475b-4f4d-af58-7e1497e01cb2
E2E_STORAGE_STATE=tests/e2e/qa-storage-state.json
E2E_BASE_URL=http://localhost:5002 E2E_F16_TEN_CHAT_AUDIT=1
pnpm exec playwright test --config=playwright.staging.config.ts \
  tests/e2e/conversational-product-selection.spec.ts \
  --project=desktop-chromium --workers=1 --reporter=list \
  --grep 'CPS cycle-3 audit'
```

Result: `PASS` — one test, all ten clean first-run conversations. The result
metadata is `/private/tmp/saleaura-f16-cc005.7Z3mKL/test-results/staging-e2e/.last-run.json`
(`status: passed`, no failed tests). The retained browser recordings comprise
the ten clean sessions under the matching `conversational-product-sel-*`
result directory.

### First-response review

QA reviewed the audit's first-response content assertions and retained browser
recordings. The expected customer-facing result passed for every conversation:

* default and sorted visible ordinals named the trusted card product, included
  quantity one and the PKR price before consent, and left the cart unchanged;
* a different-product turn requested a new visible choice rather than
  confirming the prior pending item;
* unanchored `that one` clarified without adding anything, and no-pending
  agreement said no product was waiting without internal candidate wording;
* cancellation named the declined product and added nothing;
* fresh repeated selections remained card/PKR grounded;
* discovery prose and cards used PKR with no foreign-currency marker; and
* Urdu ordinal selection remained grounded, while the Roman-Urdu cancellation
  retained the selected name and honoured the switch back to English.

This valid run reached real widget bootstrap and chat, unlike Attempt 5. The
test's `finally` cleanup completed because the test passed; no migration,
production, billing, payment, subscription, or deployment action occurred.

### CC-005 finding resolution

`F16-CPS-QA-005` — `CLOSED_BY_ATTEMPT_6`. Real staging customer-visible
evidence now confirms the routing boundary alongside the focused gate tests.

### Attempt 6 verdict

CC-005 passes independent QA. Preserve all earlier failed and invalid attempts
as historical evidence; route this checkpoint to independent Reviewer
re-evaluation.

Attempt Result: PASS

STATUS: PASS
