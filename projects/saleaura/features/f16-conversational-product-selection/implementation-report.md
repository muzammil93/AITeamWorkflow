# Implementation Report

## Feature ID and Name

`F16-CPS` — Conversational Product Selection and Confirmed Cart Mutation

## Execution Mode

`INITIAL_IMPLEMENTATION`

## Requirement IDs

`CPS-001` through `CPS-021`

## PRD and Architecture References

* `projects/saleaura/features/f16-conversational-product-selection/ceo-request.md`
* `projects/saleaura/features/f16-conversational-product-selection/prd.md`
* `projects/saleaura/features/f16-conversational-product-selection/architecture.md`

## Attempt 1

### Repair Count

`0/2`

### Summary

Implemented semantic conversational product selection without a static phrase
catalogue. The LLM receives the trusted current display and pending-selection
context and returns a typed product action. Deterministic server code then
validates that action against the exact browser-reported display revision,
creates a bounded pending confirmation, and performs cart mutation only after
the shopper explicitly confirms.

The server-owned confirmation is tied to the owner-bound widget session,
display revision, offer, expected product facts, and expiry. The confirmed cart
endpoint revalidates product visibility, stock, price, currency, quantity, and
the one-time confirmation secret immediately before mutation. The browser opens
and focuses the cart only after receiving a trusted `added` result.

### Files Changed

Product source:

* `app/api/chat/route.ts`
* `app/api/widget/cart/route.ts`
* `app/api/widget/preview-session/route.ts`
* `backend/api.py`
* `backend/engine.py`
* `backend/product_selection.py`
* `backend/prompts/04_response_format.txt`
* `backend/prompts/05_guardrails.txt`
* `backend/schema.py`
* `components/chat/ChatWidget.tsx`
* `lib/widget/cart.ts`
* `lib/widget/security.ts`

Product tests:

* `tests/e2e/conversational-product-selection.spec.ts`
* `tests/f16/cart-state.test.ts`
* `tests/f16/chat-request-id.test.ts`
* `tests/f16/product-selection.test.ts`
* `tests/test_f16_product_selection.py`

Pre-existing/generated changes in `backend/**/__pycache__/*.pyc` and
`tests/e2e/qa-storage-state.json` remain uncommitted and were excluded from the
feature checkpoint.

### Code Changes

* Added a required, versioned `product_action.v1` structured-output contract for
  semantic `select`, `confirm`, `reject`, `clarify`, and `no_action` decisions.
  No saved English, Urdu, or Roman Urdu phrase list is used to infer intent.
* Added exact displayed-product snapshots, monotonically increasing display
  revisions, bounded selection state, stale/conflicting update rejection, and
  deterministic ordinal resolution against the current displayed order.
* Added server-owned pending confirmations with hashed one-time secrets,
  expiry, offer/product facts, quantity, and display linkage.
* Added strict `confirm_add` validation, current inventory/price/currency
  revalidation, compare-and-swap session mutation, idempotent receipts, and
  safe `price_changed`/`unavailable` outcomes.
* Added an authenticated owner-preview widget-session bootstrap so local
  inventory testing follows the same protected web-widget path as embedded
  shoppers.
* Removed direct owner-cookie fallback from the chat proxy and required a valid
  widget session for this browser path.
* Preserved the existing explicit Add button and Send-button spinner.
* Prevented a bare greeting such as `Hello` from being misclassified as a lead
  name unless the conversation is already awaiting the name.

### Database / Migration Changes

`NOT_REQUIRED`

Selection state is stored inside the existing bounded widget-session cart state.
No migration, production data write, or deployment was performed.

### Migration Checksum and Recovery

`NOT_APPLICABLE`

Recovery is a code rollback of product commits
`e73fac431c10eaee5bdae09479b05a143cbd77e3` and
`e7151ea23c648778eb5ec12bc5a19f82c4651744`; no schema or data repair is
required.

### Tests and Checks

* `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest tests.test_f16_product_selection tests.test_f16_processing_status tests.test_f16_lead_notifications tests.test_f12_lead_consent tests.test_f09_customer_response tests.test_f09_language_contract tests.test_f09_quota_timing`
  * Passed initially: 26 tests; passed after the narrow repair: 27 tests.
* `export PATH="/Users/muzammilmunir/Library/Application Support/Herd/config/nvm/versions/node/v22.13.1/bin:$PATH"; pnpm vitest run tests/f16`
  * Passed: 6 files, 25 tests.
* `export PATH="/Users/muzammilmunir/Library/Application Support/Herd/config/nvm/versions/node/v22.13.1/bin:$PATH"; pnpm exec tsc --noEmit`
  * Passed.
* `git diff --cached --check`
  * Passed before commit.
* Focused authorized staging Playwright:
  * Reached real inventory search, exact rendered product order, semantic
    selection, and confirmation UI while proving no pre-confirmation cart
    mutation.
  * Exposed invalid JSON serialization in the Python cart-state
    compare-and-swap filter; fixed by canonical JSON serialization.
  * The last completed browser run then exposed a structured-output fallback:
    an empty parsed product action could inherit `no_action`, so explicit
    agreement did not produce `cart_action`.
  * The schema was repaired so both `contract` and `action` are required, and
    all local contract/regression tests pass after that repair.
  * Final single rerun against committed `e73fac4`:
    `E2E_BASE_URL=http://127.0.0.1:5001 pnpm exec playwright test
    tests/e2e/conversational-product-selection.spec.ts --project=chromium
    --workers=1 --reporter=list` (with the existing authorized staging
    environment and `qa-storage-state.json`).
  * Failed: 1/1 after 38.3 seconds at
    `tests/e2e/conversational-product-selection.spec.ts:113`.
    The explicit agreement request returned HTTP 200, but
    `confirmationPayload.cart_action?.type` was `undefined` instead of
    `confirm_add`. The backend recorded three successful `POST /api/chat`
    responses; the scenario stopped before cart mutation.
  * A bounded Developer repair removed `no_action` from the structured
    pending-confirmation decision and clarified that the action is a semantic
    label rather than a model-owned mutation.
  * The one permitted repair rerun still failed: 1/1 after 39.5 seconds at the
    same line with `cart_action?.type` undefined. The captured response remained
    `lead_capture`, while a read-only staging check proved the exact session
    still held the current display and unexpired pending confirmation.
  * This narrowed the remaining defect to the typed-action boundary:
    `PendingProductAction` still inherited optional position/candidate fields,
    so Pydantic could accept a cross-field-invalid shape that the deterministic
    validator then discarded. The local follow-up makes pending decisions a
    closed `confirm | reject | clarify` object with no position, token, or
    product fields. The exact captured message/state regression, 27 Python
    tests, 25 F16 Vitest tests, and TypeScript compilation passed.
  * Final authorized verification:
    `E2E_BASE_URL=http://127.0.0.1:5001 pnpm exec playwright test
    tests/e2e/conversational-product-selection.spec.ts --project=chromium
    --workers=1 --reporter=list` (with the existing authorized staging
    environment and `qa-storage-state.json`).
  * Passed: 1/1 in 1.3 minutes. The scenario completed exact rendered-order
    selection, trusted product confirmation, no pre-confirmation mutation,
    one-time confirmed add, cart open/focus, replay idempotency, forged-token
    rejection, Roman Urdu selection/rejection, greeting isolation,
    cross-session rejection, and protected owner preview.

### Security Notes

* The model may interpret language and references but cannot mutate the cart or
  choose authoritative price, currency, stock, owner, session, or offer facts.
* All displayed-order resolution uses a trusted server-accepted snapshot of the
  exact product IDs rendered by the browser for the active owner-bound session.
* Confirmation secrets are one-time, expiry-bounded, stored only as hashes, and
  compared in constant time.
* Cart mutation revalidates session binding, confirmation state, product
  visibility, stock, current price/currency, and bounded quantity.
* Compare-and-swap state transitions and bounded receipts prevent replay,
  duplicate delivery, and concurrent double-add.
* Invalid, stale, forged, cross-session, expired, ambiguous, or mismatched
  actions add nothing and return a safe next step.

### Finding Resolutions

`NOT_APPLICABLE`

This is the initial approved implementation.

### Git Checkpoint

Product commit:

`e73fac431c10eaee5bdae09479b05a143cbd77e3`

Commit message:

`feat(chat): confirm conversational product selections`

Narrow repair commit:

`e7151ea23c648778eb5ec12bc5a19f82c4651744`

Repair commit message:

`fix(chat): constrain pending product decisions`

### Assumptions

* The complete bounded session chat remains the conversational memory supplied
  to the LLM; no separate phrase dictionary is needed.
* Product reference interpretation is probabilistic, but every state transition
  and cart side effect remains deterministic and fail-closed.
* The existing cart represents an inquiry/sales flow and does not decrement
  inventory.

### Known Limitations

* Existing generated bytecode and browser storage-state changes remain outside
  the product commit.
* Independent QA still owns the broader approved matrix beyond the focused
  Developer scenario.

### Blockers

None for Developer handoff.

Attempt Result: Initial implementation and bounded confirmation repair completed;
ready for independent QA.

## Attempt 2

### Repair Count

`1/2`

### Finding

`F16-CPS-QA-001` — mandatory conversational-selection coverage matrix was
incomplete.

### Resolution

`FIXED_PENDING_VERIFICATION`

Added focused test coverage only; no product behavior changed.

* Expanded the staging customer scenario to prove default visible order,
  deliberate assistant-prose/card-order mismatch, reject/no-mutation,
  idempotent replay, forged and cross-session confirmation rejection,
  no-pending agreement, a different-product request while confirmation is
  pending, ambiguity, stale display context, and session cleanup.
* Added an owner-preview/mobile scenario for protected preview parity, pure Urdu
  search and relative selection, English confirmation after the Urdu turn,
  close/reopen transcript persistence, keyboard submit, cart focus and viewport
  bounds, customer-visible rate limiting, and real entitlement quota
  exhaustion/restoration.
* Added deterministic Python coverage for no pending confirmation,
  different-product clarification, malformed structured model output, and
  trusted customer-safe `price_changed`, `unavailable`, and `expired` fallback
  messages.
* Added a Vitest assertion that the bounded 429 chat response never reaches the
  model backend.
* Added explicit cleanup for temporary widget sessions and snapshot/restore
  support for the dedicated staging QA account's AI-usage counter.

### Verification

* `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest tests.test_f16_product_selection`
  * Passed: 8 tests.
* `pnpm vitest run tests/f16`
  * Passed: 6 files, 26 tests.
* `pnpm exec tsc --noEmit`
  * Passed.
* `git diff --check`
  * Passed.
* Authorized staging Playwright:
  * The expanded primary scenario passed 1/1 in 3.3 minutes and covered the
    visible-order/context/session checks above.
  * Recovery exploration reached and visibly passed both `price_changed` and
    `unavailable` safe UI continuations with a closed, unchanged cart.
  * Later independent searches were nondeterministic: one returned unrelated
    prose without product cards, and the final bounded rerun interpreted a
    relative selection as cart-review advice without issuing a confirmation.
    These runs failed closed and did not mutate the cart.
  * The unverified full-UI expiry/concurrent paths were not committed as a
    flaky gating scenario. Their state/secret/idempotency boundaries remain
    covered by deterministic Python/Vitest tests, and their customer-safe
    recovery copy is covered at the backend response boundary.
  * The new combined preview/mobile/language/rate/quota scenario compiles but
    was not independently completed after the recovery rerun consumed the
    bounded staging window.
* Shared search/cart/lead/build Playwright regressions were not rerun in this
  bounded repair window; existing F16 regression suites passed.

### Product Checkpoint

Commit:

`97eb41feff231d9bb8c1e38ec3b522aa84228ea3`

Commit message:

`test(f16): expand conversational selection QA coverage`

Generated/runtime files in `backend/**/__pycache__/*.pyc` and
`tests/e2e/qa-storage-state.json` remain uncommitted and excluded.

### Remaining Independent QA

Independent QA should rerun the new preview/mobile scenario and exercise
expiry/concurrent customer-visible recovery plus the shared
search/cart/lead/build regression set. The application failed closed during
model nondeterminism observed in this repair.

## Attempt 3

### Repair Count

`2/2`

### Reviewer Findings

* `F16-CPS-REV-001` — `FIXED_PENDING_VERIFICATION`
* `F16-CPS-REV-002` — `FIXED_PENDING_VERIFICATION`

### Summary

Made all product writers of `widget_sessions.cart_state` participate in one
service-role-only atomic boundary. Ordinary cart mutations now reload and
reapply after a compare-and-swap loss, and Flask offer, submitted-cart,
display, pending, rejection, and continuation transitions use the same RPC.
No blind product-code `cart_state` update remains.

Expired confirmation authority and terminal compare-and-swap exhaustion now
atomically merge one bounded `cart_tool_result.v1` receipt into the latest
session state. Next returns HTTP 200 with the typed result, the widget invokes
the existing internal continuation, and Flask composes a localized,
customer-safe retry/reselection message from trusted product facts and the
typed `select_product_again` next step. The model still cannot choose products,
prices, stock, authority, or mutations.

### Files Changed

Product:

* `app/api/widget/cart/route.ts`
* `backend/api.py`
* `backend/engine.py`
* `supabase/migrations/20260730143000_f16_widget_cart_state_atomicity.sql`

Focused tests/support:

* `tests/e2e/conversational-product-selection.spec.ts`
* `tests/e2e/support/staging-inventory.ts`
* `tests/f16/cart-concurrency.test.ts`
* `tests/f16/migration-cart-sales-flow.test.ts`
* `tests/f16/product-selection.test.ts`
* `tests/test_f16_product_selection.py`

### Atomicity and Recovery Details

* Added `compare_and_swap_widget_cart_state`, which updates only when owner,
  session, and the complete expected JSONB state match.
* Added `record_widget_cart_terminal_result`, which locks the latest session
  row, deduplicates by confirmation hash, retains only eight receipts, clears
  only the matching pending authority, and preserves any newer concurrent
  display/pending selection.
* Revoked both functions from `PUBLIC`, `anon`, and `authenticated`; granted
  execution only to `service_role`.
* Next `add`, `add_build`, `remove`, `quantity`, and `clear` now perform bounded
  reload/reapply/CAS. `get` is read-only.
* Flask offer registration precomputes opaque offer tokens, merges them into
  each freshly loaded state, and removes unpersisted tokens from the response
  if bounded CAS exhausts.
* Flask submitted-cart marking reloads and reapplies its marker through CAS.
  History and build state remain separate-column updates and cannot overwrite
  cart state.
* Replayed terminal results return the already persisted outcome, preserving
  exactly-once behavior when an identical confirmation wins concurrently.

### Migration

Local migration:

`20260730143000_f16_widget_cart_state_atomicity.sql`

SHA-256:

`57bbac77efc21332d8a3734c7d471d5ffb2e62a2ee92aaf635fbb5c62cf3ea66`

Applied to the verified staging project through the staging Supabase MCP:

* Migration name: `f16_widget_cart_state_atomicity`
* Staging migration version: `20260730093327`
* Permission verification: `service_role=true`, `authenticated=false`,
  `anon=false` for both functions.
* Post-migration security/performance advisors reported only pre-existing
  project notices; neither new function produced an advisor finding.

Recovery is to deploy the product commit and migration together. A rollback
must first return all application writers to the former implementation, then
drop `public.record_widget_cart_terminal_result(...)` and
`public.compare_and_swap_widget_cart_state(...)`. The migration does not
rewrite existing cart data.

### Deterministic Verification

* Affected Python suites:
  * Passed: 31 tests.
* `pnpm vitest run tests/f16`:
  * Passed: 7 files, 30 tests.
* `pnpm exec tsc --noEmit`:
  * Passed.
* `git diff --check` and pre-commit `git diff --cached --check`:
  * Passed.
* New deterministic cases prove:
  * an ordinary add loses CAS to a confirmation, reloads, and preserves both
    cart effects and the consumed receipt without restoring pending authority;
  * offer registration loses CAS to a rejection/result, reloads, preserves the
    cleared pending state and receipt, and registers only persisted tokens;
  * an expired confirmation persists and returns a typed `expired` result;
  * three confirmation CAS losses produce one atomic typed `conflict` result;
  * an expired receipt reaches the Flask localized continuation and persists
    the assistant recovery message.
* Exhaustive product-code search found no direct `cart_state` update outside
  the shared RPC boundary.

### Staging Playwright

* Primary conversational selection scenario:
  * Passed 1/1 in 2.7 minutes after the staging migration and backend restart.
  * Covered displayed-order selection, confirmation, confirmed CAS add, cart
    open/focus, replay idempotency, forged/cross-session rejection, and preview
    session protection.
* Deterministic expired-recovery widget scenario:
  * Passed 1/1 in 10.5 seconds.
  * Exercised real Next terminal receipt persistence, real Flask continuation,
    visible safe recovery copy, and a closed/empty cart.
* Shared ordinary-cart scenario:
  * Two synthetic offers were registered and added through the new CAS RPC and
    both cart lines rendered.
  * The scenario then stopped because the model did not find the unrelated
    third synthetic Monitor fixture. No cart-state or RPC failure occurred.
* Cleanup verification:
  * Zero temporary `QA F16 %` inventory rows.
  * Zero localhost allowed-host rows.

### Git Checkpoint

Product commit:

`c94257db198ef1cf9b4a5b16d504f775f46da52d`

Commit message:

`fix(f16): make cart state transitions atomic`

Generated/runtime files in `backend/**/__pycache__/*.pyc` and
`tests/e2e/qa-storage-state.json` remain uncommitted and excluded.

### Blockers

None for independent QA and Reviewer re-evaluation.

## Status

STATUS: IMPLEMENTATION_COMPLETE

## CEO-Authorized Repair Cycle 3/3 — CC-004

### Findings

* `F16-CPS-QA-003` — `FIXED_PENDING_VERIFICATION`
* `F16-CPS-QA-004` — `FIXED_PENDING_VERIFICATION`

### Implementation

The web-widget router now derives one trusted product state mode
(`visible_row`, `pending_confirmation`, or `no_actionable_context`) and always
runs a dedicated LLM semantic decision before lead/general routing. The strict
`product_action.v2` result is accepted only when its state, action, reason,
position, and candidate positions form an allowlisted combination. Malformed,
unsupported, state-mismatched, or internally conflicting outputs fail closed
to a typed clarification. Only valid `no_action/not_product_action` releases
the turn to the existing intent router.

This remains LLM semantic understanding rather than a saved phrase catalogue.
Trusted code resolves the LLM's position against the browser-authored visible
row and remains the only cart authority. An unanchored reference clarifies;
consent without pending authority receives a grounded no-pending response;
reject names the captured trusted product while clearing only pending state;
and a different-product request clears the old pending selection, preserves
the visible row, and asks which visible alternative the customer wants.

Customer-facing monetary claims are now checked against trusted product DTOs
and the owner currency. Foreign symbols/codes and conflicting amounts discard
the complete draft. Composition gets at most one grounded regeneration; a
second failure returns deterministic prose that omits price and directs the
customer to authoritative product cards. The former blind symbol replacement
was removed. Multi-product prose omits monetary claims when product-to-price
association cannot be proven.

### Files Changed

Product:

* `backend/api.py`
* `backend/engine.py`
* `backend/product_prose.py`
* `backend/product_selection.py`
* `backend/schema.py`

Tests/config:

* `playwright.staging.config.ts`
* `tests/e2e/conversational-product-selection.spec.ts`
* `tests/test_f16_product_prose.py`
* `tests/test_f16_product_selection.py`

No frontend component, Next cart route, database, migration, search ranking,
lead contract, or release document was changed.

### Regression Evidence

* Focused Python F16 selection/prose/status/notification suites:
  * Passed: 29 tests.
* Full Vitest:
  * Passed: 43 files, 153 tests.
* `pnpm exec tsc --noEmit`:
  * Passed.
* Playwright discovery:
  * The staging configuration lists all four F16 scenarios, including the new
    opt-in `E2E_F16_TEN_CHAT_AUDIT=1` ten-clean-session first-attempt audit.
  * The audit attaches an immutable JSON result for every first attempt and
    covers default/sorted ordinals, different-product handling, ambiguity,
    consent without pending authority, named rejection, repeated natural
    ordinal recovery paths, foreign currency substitution, Urdu selection,
    language switching, and visible context preservation.
* Single-process `unittest discover` is not a clean aggregate runner in this
  repository: the pre-existing F06 upload test replaces `backend.engine` in
  `sys.modules`, causing later import/object errors. Clean-process focused
  suites pass with no assertion failures.

### Staging Browser Blocker

The current shell does not contain any of the dedicated staging QA variables
required by the test safety gate, the stored browser state has no SaleAura
Supabase origin/session, and the prior signed-in CDP Chrome session is no
longer running. The implementation therefore does not claim a completed
cycle-3 staging browser audit. The harness is ready, but independent QA must
provide or restore the dedicated staging QA identity and run:

`E2E_F16_TEN_CHAT_AUDIT=1 pnpm exec playwright test --config=playwright.staging.config.ts conversational-product-selection`

Generated/runtime `backend/**/__pycache__/*.pyc` and
`tests/e2e/qa-storage-state.json` remain excluded from the product commit.

### Product Checkpoint

Commit:

`1a4cc22bc81a6e20c3256f995e9023e326c58aff`

Commit message:

`fix(f16): ground conversational product actions`

STATUS: FIXED_PENDING_VERIFICATION

## Cycle-3 Developer Staging Verification

### Environment Evidence

The first runner invocation against the user's existing port-5001 frontend
never opened Conversation 1. `POST /api/widget/bootstrap` returned HTTP 503
`Widget is temporarily unavailable` because that user-run frontend did not
have `WIDGET_BOOTSTRAP_SECRET`. The runner timed out at its 35-minute limit.
No discovery request, product-action request, or model response occurred, so
this was environmental evidence rather than a conversational retry.

An isolated current-source frontend was then started on port 5002 with the
staging configuration. Before the actual audit:

* owner installation: HTTP 200;
* temporary `127.0.0.1` allowed-host add: HTTP 200;
* widget bootstrap: HTTP 200;
* preflight host cleanup: HTTP 204.

The saved owner session was scoped to `localhost`, so the valid audit base URL
was `http://localhost:5002`. The embedded test host remained the
spec-generated `127.0.0.1` origin.

### First Actual Conversation — Failed

The opt-in ten-clean-session audit launched successfully with one worker and
no retry. It stopped on the first assertion after 50.9 seconds.

Conversation 1 discovery passed:

* User: `Show me the RAM products available in this shop.`
* Assistant: `I found these matching products: TeamGroup DDR5 RAM RAM-5096B,
  TeamGroup DDR5 RAM RAM-5469O, Kingston DDR5 RAM RAM-9224L, TeamGroup DDR4
  RAM RAM-1298L, G.Skill DDR4 RAM RAM-6517Y. Please use the product cards for
  prices.`
* Ten structured/cards products were returned, all in `PKR`.
* The prose contained no monetary claim and no foreign currency symbol.
* Visible first card: `TeamGroup DDR5 RAM RAM-5096B`.

The first natural ordinal failed:

* User: `Can I get the first one?`
* Assistant: `Please clarify which visible product you mean. I have not added
  anything.`
* Typed intent remained `product_selection`; it did not divert to lead capture
  and did not claim a cart mutation.
* Expected: a trusted confirmation naming `TeamGroup DDR5 RAM RAM-5096B`.

The request carried a valid `display_context.v1` revision with the exact ten
visible offer tokens, so the ordinal had sufficient browser authority. This is
a genuine remaining `F16-CPS-QA-003` semantic-resolution failure, not an
environmental or card-order failure. Conversations 2–10 did not run because
the serial audit correctly stopped on the first preserved failure.

Trace evidence:

* Playwright result: `/private/tmp/f16-cycle3-actual-results/.last-run.json`
  (`status=failed`);
* trace:
  `/private/tmp/f16-cycle3-actual-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`;
* discovery trace ID: `5f3de4ca-ms7lf5is-kwmvlz2r`;
* ordinal trace ID: `5f3de4ca-ms7lfra1-ru4uvfom`.

### Cleanup

Read-only service-role verification after the failed run found:

* captured audit widget sessions remaining: `0`;
* temporary `127.0.0.1` allowed-host rows remaining: `0`;
* temporary `QA F16 %` inventory rows remaining: `0`.

The user's port-5001 frontend was not changed. Generated bytecode and the
authorized browser storage state remain outside the product commit.

### Verification Disposition

* `F16-CPS-QA-003` — `OPEN` (`FAILED_VERIFICATION`)
* `F16-CPS-QA-004` — `FIXED_PENDING_VERIFICATION`

QA-004 passed the one completed discovery response, but the full ten-session
currency audit did not complete. No additional product change or product
commit was made after commit
`1a4cc22bc81a6e20c3256f995e9023e326c58aff`.

STATUS: FAIL

### Post-Attempt-7 Replacement Diagnostic

One observability-only clean session reproduced the exact Attempt-7 sequence
without changing semantic behavior:

* discovery;
* first visible product selection;
* `Actually I want a different product from this row.`

Visible result:

`Please clarify which visible product you mean. I have not added anything.`

Safe trace ID:

`e1d81e1f-ms7o43tg-jia5j9qn`

Both primary and adjudication produced the same correct semantic decision:

* expected/parsed state: `pending_confirmation`;
* action: `clarify`;
* reason: `different_product_requested`;
* position present: `true`;
* candidate positions present: `true`;
* validation: `rejected`;
* failure: `action_reason_or_cross_field_mismatch`.

Therefore the remaining failure is not LLM misunderstanding. Correct
replacement semantics were rejected because the global structured schema also
populated positional metadata that is non-authoritative for this pending-state
replacement decision. Trusted fail-closed behavior then returned generic
clarification. The isolated test's awaited session/host cleanup passed, the
temporary harness was removed, and normal backend logging was restored.

## Cycle-3 Replacement Normalization and Attempt 8

### Precise Replacement Metadata Correction

For the exact tuple
`pending_confirmation/clarify/different_product_requested`, trusted validation
now drops model-emitted position and candidate metadata. No replacement has
been chosen at that point; the trusted current display remains the only
authority.

The correction does not loosen visible selection, ambiguous or uncertain
clarification, state/action/reason pairs, or mutation authority. Captured
regressions prove:

* the exact observed primary/adjudication shape normalizes to
  `different_product_requested`;
* malformed ambiguity candidates remain invalid;
* clearing pending replacement authority preserves the visible display and
  cart items.

Commit:

`038c078`

Commit message:

`fix(f16): normalize pending replacement metadata`

Verification:

* focused Python suites: `42` tests passed;
* full Vitest: `43` files, `153` tests passed;
* TypeScript and diff checks: passed.

One isolated replacement proof passed:

* Assistant: `I have not added TeamGroup DDR5 RAM RAM-5096B. Which other
  visible product would you like?`
* cart unchanged: `true`;
* visible row remained rendered: `true`;
* safe trace: `f60b233a-ms7ob7sw-uaz1h6sr`;
* primary and adjudication:
  `pending_confirmation/clarify/different_product_requested`;
* position/candidates present: `true/true`;
* ignored non-authoritative fields: `true`;
* validation: `accepted`.

Cleanup passed and the temporary proof harness was removed.

### Attempt 8 — Fresh Visible Selection Failure

Attempt 8 ran once from Conversation 1 and stopped at its first genuine
failure.

Conversations 1–2 passed, including default ordinal, sorted ordinal, and exact
named rejection. Conversation 3 discovery returned ten grounded `PKR`
products, but:

* User: `I want the first visible product.`
* Assistant: `Please clarify which visible product you mean. I have not added
  anything.`
* no trusted pending confirmation was created.

The replacement turn did not run.

Evidence:

`/private/tmp/f16-cycle3-attempt8-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`

Failed-turn trace:

`dce03ecf-ms7oerg5-71v5bmo4`

Cleanup verification:

* captured sessions: `3`;
* captured sessions remaining: `0`;
* temporary host rows remaining: `0`;
* temporary inventory remaining: `0`.

No rerun was made.

One observability-only isolated diagnostic then ran the exact discovery plus
`I want the first visible product.` flow once. It did not reproduce the
failure:

* visible response grounded TeamGroup DDR5 RAM `RAM-5096B`;
* pending confirmation existed;
* safe trace: `483b6638-ms7ohsuj-xnsr4lut`;
* primary: `visible_row/select/resolved_reference`;
* position present: `true`;
* candidates present: `false`;
* validation: `accepted`;
* no adjudication was needed.

Therefore there is no evidence that the isolated select was rejected due to
candidate metadata. Attempt 8 remains a nondeterministic full-audit classifier
failure whose historical primary/adjudication shape is unavailable because
detailed tracing was intentionally disabled for the full audit.

STATUS: FAIL

## Cycle-3 Continuation — Attempts 2–7

### Attempt-2 Representation Reclassification

Product and architecture review reclassified Attempt 2's split canonical name
(`Kingston DDR4 RAM (SKU: RAM-7878U)`) as an audit representation mismatch,
not a product-identity defect. The trusted selected offer, SKU, price, currency,
quantity, pending token, and unchanged cart were all correct.

The test-only correction accepts only either the boundary-exact canonical name
or the boundary-exact base name followed by the exact trusted SKU. It also
checks the trusted pending offer token, quantity, price, currency, and
pre-consent cart state. It does not use fuzzy matching.

Commit:

`be2c68b85027bd11da5c8ca81ca81aeae4066984`

Commit message:

`test(f16): verify equivalent trusted confirmation identity`

### Attempt 3 — Genuine Pending Rejection Failure

The corrected representation harness passed Conversation 1 and the sorted
Conversation-2 confirmation. The following clear rejection failed:

* User: `No, do not add it.`
* Assistant: `Please clarify which visible product you mean. I have not added
  anything.`
* Expected: rejection naming the trusted pending Kingston product.

Evidence:

`/private/tmp/f16-cycle3-attempt3-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`

No retry was run. Cleanup removed both captured sessions, all temporary host
rows, and all temporary inventory.

The narrow correction added one constrained semantic pending-state
adjudication for clear consent, rejection, replacement request, or genuine
ambiguity. It performs no phrase matching and accepts only validated
state/action/reason combinations.

Commit:

`90c91f7670e629fbc6c99f5bbf5c61fe4c6d2926`

Commit message:

`fix(f16): adjudicate uncertain pending decisions`

Verification at that checkpoint:

* focused Python suites: `33` tests passed;
* full Vitest: `43` files, `153` tests passed;
* TypeScript and diff checks: passed.

### Attempt 4 — Genuine Clean-Session Routing Failure

Conversations 1–2 passed, including the sorted selection and named rejection.
Conversation 3's fresh discovery was incorrectly blocked:

* User: `Show me the RAM products available in this shop.`
* Assistant: `There is no product waiting for confirmation. Please choose a
  visible product by name or position first.`
* Typed intent: `product_selection`;
* structured products: none.

This was a genuine `no_actionable_context` routing defect: ordinary discovery
should release to normal product search, while ungrounded consent/reference
must remain grounded clarification.

Evidence:

`/private/tmp/f16-cycle3-attempt4-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`

Relevant trace IDs:

* Conversation-1 discovery: `cab486f3-ms7m6mv8-ouabw1te`;
* Conversation-1 ordinal: `cab486f3-ms7m6yrx-ytooeoec`;
* Conversation-2 discovery: `83f46780-ms7m79bk-lygauf5q`;
* Conversation-2 sorted ordinal: `83f46780-ms7m7iom-uht462qu`;
* Conversation-2 reject: `83f46780-ms7m7qrd-bkmqf43q`;
* Conversation-3 failed discovery: `097fe4f4-ms7m80vq-gh44fr18`.

Cleanup found zero remaining captured sessions, temporary host rows, or
temporary inventory. No retry was run.

The correction gives an invalid/blocking no-authority result exactly one
constrained semantic adjudication. Ordinary discovery/general questions may
return validated `no_action/not_product_action`; ungrounded consent/reference
remains `clarify/no_pending_confirmation`. It contains no phrase catalogue.

Commit:

`53f7ceea2b4f74cd6ea3a9d2c7bc54b95ca0e8af`

Commit message:

`fix(f16): adjudicate no-authority routing`

Verification:

* focused Python suites: `35` tests passed;
* full Vitest: `43` files, `153` tests passed;
* TypeScript and diff checks: passed.

### Attempt 5 — Genuine Pending Replacement Failure

The clean-session routing correction worked. Conversation 1 passed.
Conversation 2 passed its sorted confirmation and named rejection.
Conversation 3 failed after a grounded pending selection:

* User: `Actually I want a different product from this row.`
* Assistant: `Please clarify which visible product you mean. I have not added
  anything.`
* Expected: grounded copy asking which other visible product was intended.

Evidence:

`/private/tmp/f16-cycle3-attempt5-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`

Relevant failed-turn trace ID:

`beb4886f-ms7mfaxp-do11tc5j`

Cleanup removed all three captured sessions and left zero temporary host or
inventory rows. No retry was run.

The pending semantic contract was tightened to distinguish a plain decline
from abandoning the pending item while continuing with another visible
option. English, Urdu, and Roman Urdu semantic fixtures were added only as
tests; runtime code still performs no phrase matching.

Commit:

`517563b0c5421fe56a3512b02aa1345b8369a78d`

Commit message:

`fix(f16): distinguish pending replacement intent`

Verification:

* focused Python suites: `36` tests passed;
* full Vitest: `43` files, `153` tests passed;
* TypeScript and diff checks: passed.

### Attempt 6 — Rejection Regression and Missing Historical Observability

Attempt 6 stopped in Conversation 2:

* User: `No, do not add it.`
* Assistant: `Please clarify which visible product you mean. I have not added
  anything.`
* Expected pending product: `Kingston DDR4 RAM RAM-7878U`.

Evidence:

`/private/tmp/f16-cycle3-attempt6-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`

Failed-turn trace ID:

`72cf8621-ms7mmb9a-sz7ekugg`

Cleanup removed both captured sessions and left zero temporary host or
inventory rows. No retry was run.

The browser trace proved only the final pending `product_selection` generic
clarification. `DEBUG_CHAT_FLOW` had been disabled, and historical primary and
adjudication shapes were not recoverable. No speculative semantic correction
was made.

Safe structured diagnostics were added separately. They log only expected and
parsed state/action/reason, position/candidate presence booleans, validation
outcome, bounded failure category, and safe error type. They never log customer
text, product facts, tokens, IDs, secrets, or the raw model payload.

Commit:

`cf103d1`

Commit message:

`chore(f16): trace product action validation`

Verification:

* focused Python suites: `38` tests passed;
* full Vitest: `43` files, `153` tests passed;
* TypeScript and diff checks: passed.

### Isolated Diagnostic — Exact Root Cause

One isolated clean flow reproduced the rejection failure under safe tracing:

* discovery → sorted first selection → `No, do not add it.`;
* visible response remained generic clarification.

Trace ID:

`472f9899-ms7mx810-vnoyjpu3`

Safe primary diagnostic:

* expected/parsed state: `pending_confirmation`;
* action/reason: `reject/rejected`;
* position present: `true`;
* candidate positions present: `true`;
* validation: `rejected`;
* failure: `action_reason_or_cross_field_mismatch`.

Safe adjudication diagnostic:

* expected/parsed state: `pending_confirmation`;
* action/reason: `reject/rejected`;
* position present: `true`;
* candidate positions present: `false`;
* validation: `rejected`;
* same cross-field failure.

Both LLM calls understood the rejection correctly. The global structured
schema populated positional fields that have no authority for a pending
reject, and strict cross-field validation rejected both otherwise-correct
decisions. The general intent parser independently returned
`lead_capture` with confidence `1.0`, but its legacy product action was not
authoritative and was overwritten by the dedicated v2 result.

### Root-Cause Validator Correction

After an exact state/action/reason pair passes, trusted validation now drops
model-emitted position/candidate fields only for state-bound
`confirm`, `reject`, and `no_action`. Those actions use trusted pending/current
state and cannot select or redirect product identity.

`select` still requires a valid one-based position and rejects candidate
metadata. `clarify` still rejects position and validates any candidate list.
Wrong state, action, reason, contract, or extra keys remain invalid. Normalized
accepted output omits ignored positional fields. Safe diagnostics expose only
`ignored_non_authoritative_fields=true/false`.

Commit:

`689fc00`

Commit message:

`fix(f16): normalize non-select action metadata`

Verification:

* focused Python suites: `40` tests passed;
* full Vitest: `43` files, `153` tests passed;
* TypeScript and diff checks: passed.

One isolated post-fix proof passed:

* selected product: `Kingston DDR4 RAM RAM-7878U`;
* User: `No, do not add it.`
* Assistant: `No problem—I have not added Kingston DDR4 RAM RAM-7878U. What
  would you like to see instead?`
* safe trace ID: `be0f7919-ms7ni6vc-5c6uncy3`;
* primary: `pending_confirmation/reject/rejected`;
* position present: `true`;
* ignored non-authoritative fields: `true`;
* validation: `accepted`;
* no adjudication was required.

The isolated test's awaited session/host cleanup passed.

### Attempt 7 — Rejection Fixed, Replacement Still Open

Attempt 7 launched once from Conversation 1 and stopped at the first genuine
failure after 2.1 minutes.

Conversation 1 passed:

* discovery returned ten `PKR` products;
* `Can I get the first one?` produced a grounded confirmation for TeamGroup
  DDR5 RAM `RAM-5096B`, quantity 1, `71,901 PKR`.

Conversation 2 passed:

* price-ascending first card: `Kingston DDR4 RAM RAM-7878U`;
* grounded confirmation: quantity 1, `10,864 PKR`;
* clear rejection named the exact trusted product and said it was not added.

Conversation 3 discovery and first-card confirmation passed. The replacement
turn failed:

* User: `Actually I want a different product from this row.`
* Assistant: `Please clarify which visible product you mean. I have not added
  anything.`
* Expected: grounded `Which other visible product...` response.

Evidence:

`/private/tmp/f16-cycle3-attempt7-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`

Relevant trace IDs:

* Conversation-1 discovery: `65b131d0-ms7nk4qo-k5mkqvlk`;
* Conversation-1 ordinal: `65b131d0-ms7nkdvn-vcknnjil`;
* Conversation-2 discovery: `a60d6b7f-ms7nkxdk-cdhe7p80`;
* Conversation-2 sorted ordinal: `a60d6b7f-ms7nl9g6-ob4zjn9j`;
* Conversation-2 reject: `a60d6b7f-ms7nlijx-73wcetgf`;
* Conversation-3 discovery: `89a34199-ms7nlu1u-842v9wvu`;
* Conversation-3 ordinal: `89a34199-ms7nm3m9-5kksjo8a`;
* Conversation-3 failed replacement: `89a34199-ms7nmcom-8rx6f076`.

Cleanup verification:

* captured sessions: `3`;
* captured sessions remaining: `0`;
* temporary host rows remaining: `0`;
* temporary inventory remaining: `0`.

No retry was run. Conversations 4–10 did not execute.

### Current Cycle-3 Disposition

The currency/card-grounding checks passed every completed discovery and
confirmation. The clean-session discovery, ordinal selection, and rejection
paths now pass. The full audit remains red because pending replacement intent
still produces generic clarification.

* `F16-CPS-QA-003` — `OPEN` (`FAILED_REPLACEMENT_VERIFICATION`)
* `F16-CPS-QA-004` — `FIXED_PENDING_FULL_AUDIT`

STATUS: FAIL

## Cycle-3 Narrow Ordinal Correction and Post-Change Audit

### Preserved Attempt 1

The preceding failed audit remains authoritative evidence:

* product head: `1a4cc22bc81a6e20c3256f995e9023e326c58aff`;
* Conversation 1 clear ordinal returned typed clarification instead of
  selecting visible position 1;
* result: `FAIL`;
* no retry was used to relabel that first output.

### Narrow Correction

Visible-row product action now gets exactly one constrained LLM semantic
adjudication when the primary `product_action.v2` result is `clarify` or fails
state/cross-field validation. The adjudicator sees the same trusted numbered
row and conversation. It distinguishes semantically resolvable ordinal/named
references from genuinely unanchored deixis.

Trusted code still performs no phrase matching, regex intent inference, or
position guessing. It accepts `select` only when the second result passes the
existing state/action/reason/position allowlist; otherwise it retains grounded
clarification.

Captured regressions prove:

* primary uncertain → adjudicated clear ordinal selects position 1;
* primary ambiguous → `I want that one.` remains clarify after adjudication;
* conflicting primary plus state-mismatched secondary fails closed to clarify;
* no more than one adjudication is attempted.

Verification:

* focused Python suites: `31` tests passed;
* full Vitest: `43` files, `153` tests passed;
* `pnpm exec tsc --noEmit`: passed;
* `git diff --check` and staged diff check: passed.

Correction commit:

`7faaccc4ef15b591fa5285ed63b6f4cf2a35a7fc`

Commit message:

`fix(f16): adjudicate uncertain visible references`

### Post-Change Attempt 2

Attempt 2 ran from Conversation 1 with a freshly restarted corrected backend.
It is a separately labeled post-change run, not a retry used to overwrite
Attempt 1.

Conversation 1 passed:

* discovery returned ten structured/card products, all `PKR`;
* discovery prose contained product specifications but no price/currency
  claim, therefore no foreign currency contradiction;
* visible first card: `TeamGroup DDR5 RAM RAM-5096B`;
* User: `Can I get the first one?`
* Assistant: `You have selected the TeamGroup DDR5 RAM RAM-5096B, quantity 1,
  for 71,901 PKR. Do you confirm this selection? Yes/No?`
* exact visible product, price, currency, and confirmation purpose matched.

Conversation 2 discovery also returned ten `PKR` products with no monetary
claim in prose. After price-ascending client sort:

* visible first card: `Kingston DDR4 RAM RAM-7878U`;
* User: `I want the first product visible in the row now.`
* Assistant: `Please confirm your selection of 1 Kingston DDR4 RAM (SKU:
  RAM-7878U) for 10,864 PKR. Do you want to proceed with this purchase? Yes or
  no?`

The semantic product, browser-authored position, SKU, price, and currency were
all correct. However, the response did not contain the exact full card name as
one trusted string (`Kingston DDR4 RAM RAM-7878U`); it split the final SKU into
parenthetical copy. The committed audit intentionally requires the exact card
name and stopped on this first failure after 1.1 minutes. The rejection turn
and Conversations 3–10 did not run. The assertion was not relaxed and the
audit was not rerun.

Attempt-2 evidence:

* Playwright result:
  `/private/tmp/f16-cycle3-postchange-results/.last-run.json`
  (`status=failed`);
* trace:
  `/private/tmp/f16-cycle3-postchange-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`;
* Conversation 1 discovery: `5367c4ea-ms7lns4m-lrj9yhci`;
* Conversation 1 ordinal: `5367c4ea-ms7loa05-y33auy1a`;
* Conversation 2 discovery: `c9e3ecc1-ms7loiw0-hp7qsun4`;
* Conversation 2 sorted ordinal: `c9e3ecc1-ms7lorvn-t9rvciij`.

Post-change cleanup verification:

* captured widget sessions: `2`;
* captured widget sessions remaining: `0`;
* temporary `127.0.0.1` allowed-host rows remaining: `0`;
* temporary `QA F16 %` inventory rows remaining: `0`.

### Final Cycle-3 Disposition

The original natural-ordinal semantic failure is corrected in the completed
post-change conversations. The full ten-session audit is still not green
because exact confirmation-name rendering failed in Conversation 2.

* `F16-CPS-QA-003` — `OPEN` (`PARTIAL_POST_CHANGE_PASS`)
* `F16-CPS-QA-004` — `FIXED_PENDING_VERIFICATION`

No third audit was run and no confirmation-copy correction was made after
Attempt 2.

STATUS: FAIL

## Cycle-3 Sampling Stability and Attempt 9

### Narrow Sampling Correction

The two dedicated `product_action.v2` structured semantic calls now explicitly
use `temperature=0`: the primary product-action parse and the single
constrained adjudication parse.

No phrase catalog, regex intent matcher, prompt change, validator change, or
general-response sampling change was made. Product identity and cart mutation
remain trusted-code decisions after the LLM returns a typed semantic action.

Mock regressions assert that both semantic calls use `temperature=0` while
retaining `ProductActionV2` as the response schema. Existing captured
selection, rejection, different-product, and no-authority regressions remain
in the suite.

Commit:

`5b15185`

Commit message:

`fix(f16): stabilize semantic product decisions`

Verification:

* focused Python F16 suites: `42` tests passed;
* full Vitest: `43` files, `153` tests passed;
* `pnpm exec tsc --noEmit`: passed;
* `git diff --check`: passed.

### Bounded Stability Diagnostic

A non-acceptance diagnostic exercised six independent clean widget sessions:
two repetitions for each previously flaky semantic turn. The corrected
diagnostic passed in 3.0 minutes with consistent validated outcomes:

* visible ordinal: `2/2` →
  `visible_row/select/resolved_reference`;
* clear pending rejection: `2/2` →
  `pending_confirmation/reject/rejected`;
* pending different-product request: `2/2` →
  `pending_confirmation/clarify/different_product_requested`.

The first diagnostic artifact was preserved separately. It stopped on a
temporary harness representation assertion because valid prose rendered the
same product as base name plus parenthetical SKU instead of the concatenated
canonical card name. Only that temporary equivalence assertion was corrected;
product code was not changed.

Diagnostic evidence:

* results:
  `/private/tmp/f16-temperature-zero-stability-attempt2-results/stability-results.json`;
* passing trace:
  `/private/tmp/f16-temperature-zero-stability-attempt2-results/f16-stability-diagnostic-t-02e3d-action-stability-diagnostic-desktop-chromium/trace.zip`;
* preserved harness-only first artifact:
  `/private/tmp/f16-temperature-zero-stability-harness-attempt1/`.

The diagnostic's targeted session deletion completed without error and the
temporary `127.0.0.1` host row was absent afterward.

### Attempt 9 — Genuine Unanchored-Deixis Failure

Attempt 9 ran once from Conversation 1 on localhost port `5002` against backend
commit `5b15185`, with normal logging. First responses were preserved and the
audit stopped at the first genuine failure after 1.9 minutes. It was not
rerun.

Conversations 1–3 passed:

* clear visible ordinal selection grounded TeamGroup DDR5 RAM `RAM-5096B`,
  quantity 1, `71,901 PKR`;
* the sorted ordinal grounded Kingston DDR4 RAM `RAM-7878U`, and clear
  rejection left the cart empty;
* pending different-product intent returned:
  `I have not added TeamGroup DDR5 RAM RAM-5096B. Which other visible product
  would you like?`

Conversation 4 failed:

* User: `I want that one.`
* Assistant: `You have selected the TeamGroup DDR5 RAM (SKU: RAM-5096B) with a
  quantity of 1 for 71,901 PKR. Do you confirm this selection? Yes/No?`
* Expected: clarification because the deictic reference is unanchored and the
  visible row contains multiple possible products.

This is a genuine grounding failure: the system guessed visible position 1
instead of asking which product the user meant. Conversations 5–10 did not
execute.

Attempt-9 evidence:

* first-response audit:
  `/private/tmp/f16-cycle3-attempt9-results/attempt9-first-responses.json`;
* trace:
  `/private/tmp/f16-cycle3-attempt9-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/trace.zip`;
* screenshot and videos:
  `/private/tmp/f16-cycle3-attempt9-results/conversational-product-sel-bc84c-ay-state--and-card-grounded-desktop-chromium/`.

Exact cleanup verification:

* captured Attempt-9 session tokens: `4`;
* captured token rows remaining: `0`;
* temporary `127.0.0.1` host rows remaining: `0`;
* temporary `QA-AUTO-%` inventory rows remaining: `0`.

### Current Disposition

The temperature-zero correction is committed and its focused stability
diagnostic passed. The full ten-conversation acceptance audit remains red
because unanchored deixis can still be resolved to a product without a unique
conversational anchor.

* `F16-CPS-QA-003` — `OPEN` (`FAILED_UNANCHORED_DEIXIS_VERIFICATION`)
* `F16-CPS-QA-004` — `FIXED_PENDING_FULL_AUDIT`

STATUS: FAIL

### Attempt-9 Ambiguous-Reference Diagnostic

One observability-only clean session reproduced the exact failed flow on
commit `5b15185` without code changes:

1. discovery returned ten visible products;
2. User: `I want that one.`

Safe trace ID:

`eefc86eb-ms7p9lyq-7lyqsaxy`

The primary was not a valid select:

* expected state: `visible_row`;
* parsed state/action/reason:
  `pending_confirmation/confirm/confirmed`;
* position present: `true`;
* candidates present: `false`;
* validation: `rejected`;
* failure: `state_mismatch`.

The single adjudication then returned:

* `visible_row/select/resolved_reference`;
* position present: `true`;
* candidates present: `false`;
* validation: `accepted`.

Visible response:

`You have selected the TeamGroup DDR5 RAM RAM-5096B, quantity: 1, for 71,901
PKR. Do you confirm this selection? Yes or No?`

The trusted pending state existed for that exact product and the cart remained
empty. This isolates the failure to an accepted adjudication that guessed a
position for unanchored deixis, not a primary valid-select path.

Evidence:

* extracted result:
  `/private/tmp/f16-attempt9-ambiguous-observability-results/observability-result.json`;
* trace:
  `/private/tmp/f16-attempt9-ambiguous-observability-results/f16-ambiguous-observabilit-9c4a1-ous-reference-observability-desktop-chromium/trace.zip`.

Cleanup verification:

* captured session token: `1`;
* captured token rows remaining: `0`;
* temporary `127.0.0.1` host rows remaining: `0`.

The temporary diagnostic harness was removed and the backend was restored to
normal logging. Attempt 9 remains preserved and was not rerun.

STATUS: FAIL

## Cycle-3 Product-Reference Verification — Passing Staging Audit

### Current Product Checkpoint

`39edc8a fix(f16): verify semantic product references`

This narrow final cycle-3 change adds a bounded LLM reference verifier after a
validated visible-row selection candidate. The verifier may only confirm that
the candidate resolves to the same current trusted displayed position; any
ambiguity, mismatch, invalid result, timeout, stale display, or provider
failure fails closed to `uncertain_reference`. It does not introduce phrase
matching, product authority in the model, cart mutation, or a second retry.

### Verification

* Focused Python F16 suites: passed, `35/35` tests.
* `pnpm exec tsc --noEmit`: passed.
* `git diff --check`: passed.
* Authorized staging Playwright ten-conversation audit: passed once, `1/1`.
  The decoded result was `total=1`, `expected=1`, `unexpected=0`.
  Report: `/private/tmp/saleaura-f16-e2e.PtrkQ6/playwright-report/staging-e2e/index.html`.

All ten clean-session first-run conversations were asserted. Coverage includes
the ambiguity veto and Urdu ordinal paths, alongside the existing visible/sorted
reference, pending confirmation, rejection/replacement, no-authority,
recovery, currency-grounding, language-switch, and session-context cases.
Earlier failed attempts remain preserved above; this passing run is a new
separately recorded result, not a relabeling or overwrite of any first output.

### Handoff

Developer implementation is complete at the checkpoint above. Independent QA
and Reviewer still own their required fresh evaluation and final disposition.

STATUS: IMPLEMENTATION_COMPLETE

## CEO-Authorized Final Routing-Boundary Repair — CC-005

### Finding Addressed

`F16-CPS-REV-003` — product-action handling invoked the generic/general/lead
router before applying its trusted result.

### Implementation

The web-widget request path now validates the dedicated `product_action.v2`
outcome before choosing whether the legacy generic router may run. The generic
router is called only for the explicit validated
`no_action/not_product_action` outcome. A select, confirm, reject, ambiguous,
uncertain, different-product, no-pending, or malformed result stays on the
trusted product path; malformed output first becomes the existing fail-closed
clarification. No product action can invoke the general or lead router before
its trusted result is composed and persisted.

The change does not alter the LLM contract, product-reference semantics, cart
authority, lead workflow, search behavior, schema, migration, or customer UI.
For product-only turns, the existing session language is retained for trusted
response composition when available.

### Files Changed

Product:

* `backend/api.py`

Tests:

* `tests/test_f16_product_selection.py`

### Regression Evidence

* Focused generic-routing boundary tests: passed, `3/3`.
  * Spies prove the generic router is not invoked for select, ambiguous,
    uncertain, confirm, reject, different-product, and no-pending outcomes.
  * The only validated explicit `no_action/not_product_action` outcome invokes
    the generic router.
  * A malformed no-action outcome cannot release it.
* Full focused F16 product-selection module: passed, `32/32`.
* Focused F16 selection, prose, and processing-status modules: passed,
  `48/48`.
* `pnpm exec tsc --noEmit`: passed.
* `git diff --check`: passed.

### Product Checkpoint

`22b84fa fix(f16): gate generic routing after product actions`

### Handoff

The CEO-authorized CC-005 implementation is complete. Fresh targeted QA and
Reviewer evaluation are required for `F16-CPS-REV-003`; this report does not
claim release approval.

STATUS: IMPLEMENTATION_COMPLETE
