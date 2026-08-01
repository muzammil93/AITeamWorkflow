# Review Report

## Feature ID and Name

`F16-CONVERSATIONAL-PRODUCT-SELECTION` — Conversational Product Selection and
Cart Confirmation

## Review Mode

`CHANGED_CODE_AFTER_BOUNDED_QA_REPAIR`

## Frozen Product Checkpoint

`97eb41feff231d9bb8c1e38ec3b522aa84228ea3`

The product `HEAD` matched this checkpoint. Reviewer inspected the complete
feature delta from the parent of `e73fac4` through `97eb41f`, including
implementation commits `e73fac4` and `e7151ea` and the test-only repair
`97eb41f`. Reviewer did not modify product code, release state, or release
planning artifacts.

## Input References

* `ceo-request.md`
* `prd.md`, requirements `CPS-001` through `CPS-021`
* `architecture.md`
* `implementation-report.md`
* `qa-report.md`, ending `STATUS: PASS`

## Review Summary

The principal design is correct and within approved scope. Product-reference
and consent semantics are interpreted by the LLM through strict
`product_action.v1` output. No static product-reference phrase catalogue was
introduced. The model receives bounded conversation plus trusted numbered
product summaries and cannot return inventory IDs, offer tokens, prices,
stock, owner/session identity, or cart mutations. Trusted owner/session offer
resolution, current inventory revalidation, hashed one-time confirmation
secrets, preview-session authentication, customer-safe result composition, and
the `Hello` name safeguard are present.

The implementation cannot yet be approved because not every writer of the
shared `widget_sessions.cart_state` participates in the same compare-and-swap
boundary, and two required confirmation failures bypass the typed continuation
recovery flow. These are deterministic implementation issues even though the
executed QA journeys passed.

## Scope, Security, Privacy, and Maintainability

Scope compliance is otherwise `PASS`. No checkout, payment, order, reservation,
production, billing, deployment, migration, or unrelated search-ranking change
was introduced.

The reviewed identity and privacy boundaries are sound:

* Next and Flask derive owner/session authority from the active widget session.
* Browser display order is authorized only as ordered opaque session offer
  tokens; browser product facts are not trusted.
* Model output is semantic intent only and is schema-validated before any
  trusted state transition.
* Confirmation and continuation secrets are hashed at rest and compared using
  constant-time helpers.
* Public responses use customer-safe product facts and do not expose inventory
  IDs, session IDs, offer tokens, or confirmation hashes.
* Authenticated preview issues an owner-bound widget session and follows the
  same chat/cart path as the public widget.

The new state helpers are bounded to one display, one pending confirmation,
eight receipts, and capped offer/token/fact sizes. The split between semantic
interpretation, trusted state transitions, sole Next cart mutation, and
customer-safe composition is maintainable. The remaining problem is that this
split is not applied consistently to all read-modify-write paths over the same
JSON state.

## Independent Checks

Reviewer reran the complete affected deterministic gates at the frozen
checkpoint:

* Python affected suites — `PASS`, 29 tests.
* `pnpm vitest run tests/f16` — `PASS`, 6 files and 26 tests.
* `pnpm exec tsc --noEmit` — `PASS`.
* `git diff --check` — `PASS`.
* `git diff --cached --check` — `PASS`.

Reviewer also inspected the two expanded staging Playwright scenarios and the
QA staging lifecycle and shared-regression evidence. The evidence is sufficient
for visible-order semantics, multilingual interpretation, preview/public
parity, no pre-consent mutation, duplicate delivery of the same confirmation,
price/stock revalidation, cart opening/focus, rate/quota boundaries, isolation,
and the `Hello` regression. It does not exercise the conflicting shared-writer
interleaving in `F16-CPS-REV-001`, and deterministic inspection shows that
interleaving remains possible.

## Findings

### `F16-CPS-REV-001` — Shared cart-state writers can overwrite consumed or cleared selection state

Severity: `HIGH`
Requirements: `CPS-003`, `CPS-009`, `CPS-012`, `CPS-016`, `CPS-018`

`confirmSelectionAdd` correctly saves its cart mutation, consumed confirmation
receipt, and pending-state transition with an old-value compare-and-swap and
bounded retry. Flask display, pending, rejection, and continuation transitions
also use compare-and-swap.

However, ordinary cart actions (`add`, `add_build`, `remove`, `quantity`, and
`clear`) still load `cart_state`, mutate it, and perform an unconditional update
scoped only by session and owner. Product-offer registration performs the same
unconditional read-modify-write, and the existing submitted-cart marker is
another writer of this shared JSON value.

A stable conflicting interleaving is therefore possible:

1. An ordinary cart action reads state containing a pending confirmation.
2. A confirmation, rejection, newer display, or continuation commits through
   compare-and-swap.
3. The ordinary action writes its older full JSON snapshot without an old-state
   predicate.

The later blind write can remove a newly persisted consumption receipt/cart
result or restore a pending/display state that trusted code already consumed,
rejected, or replaced. The same risk exists when offer registration races a
cart mutation. This violates the architecture rule that a different concurrent
action must reload and revalidate rather than overwrite the winner, and it can
make a successful add disappear, restore rejected authority, or invalidate
exactly-once recovery.

Required change: route every mutation of `widget_sessions.cart_state` that can
overlap this flow through one shared atomic compare-and-swap/RPC boundary with
bounded reload and reapplication of the requested action. Add deterministic
coverage for confirmation versus at least one ordinary cart mutation and for a
selection/rejection transition versus offer/cart mutation. Preserve both
non-conflicting effects and prove that consumed or cleared selection authority
cannot be resurrected.

Finding State: `OPEN`

### `F16-CPS-REV-002` — Expiry and exhausted-CAS paths bypass typed localized recovery

Severity: `MEDIUM`
Requirements: `CPS-002`, `CPS-011`, `CPS-013`, `CPS-017`, `CPS-021`

The approved architecture requires Next to persist a trusted receipt and return
`cart_tool_result.v1` for `expired` and `conflict`, after which Flask composes
the truthful customer response from trusted facts. The implementation does
this for `added`, `price_changed`, and `unavailable`, but an expired
pending/display/offer returns an HTTP `409` directly. Exhausting the
confirmation compare-and-swap retries also returns an HTTP `409` directly.

The widget consequently skips the internal continuation and renders the raw
English route error. The deterministic fallback-copy unit tests do not connect
that copy to these actual Next branches. Thus expiry/conflict recovery is not
localized through the LLM, does not provide the specified trusted safe-next-step
message, and does not persist the receipt needed for reliable retry recovery.

Required change: make expired and terminal conflict branches fail closed
through the versioned trusted tool-result/receipt contract, or provide an
equivalent architecture-approved typed continuation that clears/invalidates
authority, preserves the cart, localizes the safe next step, and remains
idempotent. Add a customer-visible or deterministic cross-layer test proving
the Next outcome reaches Flask continuation and the widget keeps the cart
closed.

Finding State: `OPEN`

## QA Finding Assessment

### `F16-CPS-QA-001`

`VERIFIED`.

The repaired suite materially closes the original customer-visible evidence
gap. Reviewer accepts QA's combined deterministic, real staging, and Playwright
evidence for the matrix it records. The open Reviewer findings concern
interleavings and cross-layer failure routing not covered by that matrix.

### `F16-CPS-QA-002`

`ACCEPTED_NON_BLOCKING`.

The four duplicate preview bootstrap sessions were bounded, expiring,
owner-scoped test rows; no authorization boundary failed and QA removed the
exact fixtures and verified cleanup. This is a low-severity test-maintenance
observation, not a release blocker. Future test maintenance should capture all
preview bootstrap tokens or use a dedicated test-run marker, but it does not
require product behavior changes for this gate.

## Required Changes

Resolve `F16-CPS-REV-001` and `F16-CPS-REV-002`, rerun the affected
deterministic suites and authorized staging/Playwright checks proportionate to
the repairs, then return through QA before Reviewer re-evaluation under the
bounded-repair workflow.

Attempt Result: CHANGES_REQUIRED

STATUS: CHANGES_REQUIRED

## Attempt 2 — Independent Cycle-3 Final Review

### Scope and Checkpoint

Reviewer independently evaluated the CEO-authorized `CC-004` delta at product
checkpoint `39edc8a9d5cc769423c3a8bcd2544bbad9ed8de4`
(`fix(f16): verify semantic product references`) and QA commit `0257110`.
The product checkout matches that checkpoint; its only uncommitted changes are
generated Python bytecode and the confidential Playwright storage state. This
review did not modify product code, QA evidence, implementation evidence, or
release-state/plan artifacts.

### Evidence Reviewed

* QA's correctly configured, one-shot staging audit passed all ten clean
  first-run conversations and preserved the earlier failed attempts.
* The direct `39edc8a` delta is narrowly scoped to product-reference
  verification, strict validation, a final display-revision recheck, and its
  tests (`633` additions, `7` removals across five F16 files). `git diff
  --check 39edc8a^ 39edc8a` passed.
* Reviewer reran `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest
  tests.test_f16_product_selection`: `PASS` (30 tests).

### Accepted Cycle-3 Design Work

The reference verifier is properly bounded and fail-closed. It runs only for a
validated `visible_row/select` candidate, sees numbered customer-safe name/key
summaries rather than inventory IDs, offer tokens, price, or stock, has a
12-second timeout and temperature zero, and accepts only the same trusted
display revision and same position. Ambiguous, invalid, mismatched, stale, and
provider-failure results become `uncertain_reference` without pending state or
cart mutation. The captured regressions cover the ambiguity veto, clear
default/sorted ordinal selection in English, Urdu, and Roman Urdu, schema and
position mismatch, timeout/provider failure, stale revision, and non-select
calls.

The earlier cart authority boundaries remain sound: cart mutation is still at
the trusted Next endpoint, confirmation is server-owned and one-time, and the
new Flask code only creates pending state after the verified trusted revision.
The product-prose validator rejects foreign currency markers and untrusted
amounts before delivery, with bounded regeneration and trusted fallback. QA's
fresh staging evidence supports the intended customer-visible recovery,
currency, and locale behaviour.

### Finding

#### `F16-CPS-REV-003` — Product actions still execute the general/lead router before their trusted result is applied

Severity: `HIGH`
Requirements: `CPS-002`, `CPS-018`, `CPS-024`, `CPS-026`

`backend/api.py` correctly calls `interpret_product_action(...)` first, but it
then unconditionally calls `engine.process_message(...)` before examining that
trusted result. For a validated select, confirm, reject, or fail-closed
clarification, `process_message` can still invoke the generic structured intent
model and execute its general/search/lead route; only afterwards does the API
replace the response with the product-action result. The generic lead handler
currently returns text rather than writing a lead, so the reviewed path does
not establish an unauthorized cart or lead mutation. Nevertheless, this is not
the architecture's required routing boundary: only a validated
`no_action/not_product_action` may release a turn to general/lead routing.

This can emit the wrong processing path before the final product response,
consume an unnecessary second model call, and permits future generic route side
effects to run on a turn that must be product-only. The ten-chat audit proves
the final visible reply was safe; it does not prove that the prohibited router
was skipped.

Required change: gate `engine.process_message(...)` so it is called only after
the dedicated product action validates as `no_action/not_product_action`. For
every other valid product action or fail-closed product result, compose/persist
only the trusted product response. Add deterministic coverage that spies on the
generic router and proves it is not called for select, confirm, reject,
different-product, no-pending, ambiguous, or malformed/uncertain product
turns, while ordinary search/general turns still reach it. Rerun the affected
staging/Playwright matrix and return through QA.

Finding State: `OPEN`

### Prior Finding Assessment

`F16-CPS-REV-001` and `F16-CPS-REV-002` are accepted as resolved by their
documented atomic-state and typed-terminal-recovery repairs. QA findings
`F16-CPS-QA-003` and `F16-CPS-QA-004` are accepted as closed by the independent
one-shot ten-conversation staging audit. `F16-CPS-QA-002` remains a
non-blocking test-cleanup observation.

## Required Changes

Resolve `F16-CPS-REV-003` through the bounded workflow. Because `CC-004`
already consumed exceptional repair `3/3`, the Orchestrator must obtain any
further CEO authorization required by the release plan before dispatching a
new product repair.

Attempt Result: CHANGES_REQUIRED

STATUS: CHANGES_REQUIRED
