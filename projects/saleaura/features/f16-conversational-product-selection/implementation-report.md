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
