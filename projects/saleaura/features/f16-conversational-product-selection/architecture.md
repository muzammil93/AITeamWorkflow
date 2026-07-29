# Architecture Document

## Feature Name

F16 Conversational Product Selection and Cart Confirmation

## Feature ID and Execution Mode

`F16-CONVERSATIONAL-PRODUCT-SELECTION` — Standard Implementation

## PRD Reference

`features/f16-conversational-product-selection/prd.md`, `CPS-001`–`CPS-021`.

## Master Architecture / Requirement References

Preserve the existing F08 protected widget-session, allowed-domain, authenticated preview, subscription, rate-limit, and abuse boundaries; F09 bounded multilingual chat, structured output, quota, grounded and safe responses; and F16 private inquiry cart and offered-product safeguards. This remains inquiry, not checkout, ordering, payment, or inventory reservation.

## Baseline QA Findings

The visible card order and assistant prose could diverge; `first one` was not resolved against the visible first card; exact confirmation was skipped; preview opened lead capture; and `Hello` was accepted as a name. This design addresses those behaviors without changing search ranking or general lead scope.

## Dependency Validation

* The owner-bound `widget_sessions` row and existing JSON `cart_state` remain authoritative for offers, cart, and bounded selection state.
* The Flask chat service remains model-facing. The existing Next cart endpoint remains the sole cart-mutation authority.
* Reuse existing opaque offer tokens, session authentication, customer-safe inventory serialization, quota, and abuse controls.
* No DB migration is required because the state fits the existing `cart_state` JSON.

## Technical Summary

1. On each user chat send, the widget snapshots the exact rendered card order as opaque offer tokens with a monotonically increasing display revision.
2. Flask authenticates the session, validates all tokens against that session's unexpired `cart_state.offers`, rejects stale revisions, and stores bounded `current_display`.
3. Flask gives the LLM a bounded conversation window and trusted visible-product summaries derived server-side in accepted display order. Browser-authored product facts are never model or execution authority.
4. The LLM returns only schema-validated `product_action.v1`: `select`, `confirm`, `reject`, `clarify`, or `no_action`. No static phrase, regex, or translated phrase catalogue interprets product intent.
5. Flask resolves `select` against the stored row, creates one pending confirmation, and asks the LLM to compose from only the trusted resolved fact envelope. No cart mutation occurs.
6. A valid semantic `confirm` makes Flask issue a one-time confirmation ID and return typed `cart_action`; it emits no success claim.
7. The widget calls Next `confirm_add`. Next revalidates and atomically mutates cart plus consumes the ID, or records a non-success outcome.
8. The widget sends one non-user-visible tool-result continuation to Flask. Flask resolves the server receipt and the LLM emits the final truthful response. Only after `added` does the widget refresh and open the cart.

The complete valid-session transcript remains shopper-visible and resumable in existing storage. Model input stays within F09 caps and may use a bounded window/summary. Summaries never authorize display order, product identity, pending state, price, stock, execution, or cart.

## Trusted Session State

Extend cart-state normalization to preserve:

```text
selection_state: {
  version: 1,
  current_display?: {
    revision, render_id, ordered_offer_tokens, accepted_at, expires_at
  },
  pending_confirmation?: {
    pending_id, display_revision, offer_token, quantity,
    expected: { name, sku_or_key_spec, price, currency },
    created_at, expires_at,
    execution?: { confirmation_hash, issued_at }
  },
  consumptions: [{
    confirmation_hash, continuation_hash, outcome, trusted_result,
    consumed_at, continued_at?
  }]
}
```

* Store one display, one pending confirmation, and at most eight newest unexpired consumption receipts.
* Limit display tokens to the existing card-response maximum and never above 24. Reject duplicates, unknown/empty tokens, invalid revisions, unsafe strings, malformed prices, oversized state, and unknown schema versions.
* Preserve valid legacy offers/cart plus valid display, pending, and consumption fields. Legacy state defaults to empty `selection_state.version = 1`.
* Display expiry cannot exceed session or earliest offer expiry; pending expiry cannot exceed session, display, offer, or configured confirmation expiry. Clearing display clears tied pending state.
* Hash random 256-bit confirmation and continuation secrets. Expected facts and receipts are safe snapshots for comparisons/messages, not current inventory authority.

## Model Contract

The model sees numbered trusted summaries, not owner IDs, inventory IDs, opaque offer tokens, hidden fields, or mutation tools:

```json
{
  "contract": "product_action.v1",
  "action": "select|confirm|reject|clarify|no_action",
  "position": 1,
  "candidate_positions": [1, 2]
}
```

`position` is required only for `select`; bounded `candidate_positions` is allowed only for `clarify`; extra fields fail schema validation. Unsupported version/action, malformed output, out-of-range position, low confidence, or ambiguity adds nothing and produces a safe clarification/retry.

`select` resolves only against `current_display`. `confirm` requires matching unexpired pending state and no outstanding consumed execution. `reject` clears pending. A new resolved selection replaces pending and is never agreement to the old item. `clarify` and `no_action` never mutate cart authority.

Confirmation and tool-result composition receive an exclusive trusted fact envelope. The LLM localizes natural English, Urdu, or Roman Urdu text but cannot introduce facts outside it. Existing safe-response checks apply; invalid output falls back to concise server composition from the same facts.

## Frontend Changes

* Increase a session-local revision whenever the rendered product row/order changes. At chat-send time submit exact ordered opaque offer tokens, `render_id`, and revision.
* Keep only a server-acknowledged revision eligible for action; ignore older acknowledgements. Do not submit product IDs, owner, name, price, currency, or stock as authority.
* Exhaustively handle `cart_action`. For `confirm_add`, call Next once and append no speculative success.
* Send the returned continuation ID once as an internal tool-result chat event; never render/store it as a user message.
* Append Flask's final assistant response. On `added`, refresh returned cart, then open the accessible cart and announce/move focus. On other outcomes keep it closed and show the recovery response.
* Authenticated owner preview first obtains an owner-bound widget-session token through the protected preview bootstrap, then uses the identical widget chat/cart path. Owner cookies alone cannot replace widget-session authorization, and preview cannot divert selection to lead UI.

## Backend Changes

### Flask chat/session

* Add strict validators for display, product-action, cart-action, and tool-result contracts.
* Accept display only after widget-session/owner and offer validation. Apply atomic/CAS revision rules: higher replaces; same is idempotent only with identical `render_id` and order; lower/conflicting returns `stale_display`.
* Resolve indexed summaries from session offers and current customer-safe serializers. Never trust client/model identity or facts.
* Persist pending before confirmation text. Confirmation text must include trusted name, SKU/equivalent key specification, relevant quantity, and price/currency.
* On valid semantic confirmation, generate/hash a one-time confirmation ID, persist it, and return `cart_action` with no assistant success.
* On internal continuation, authenticate the same session, resolve receipt by continuation hash, ignore client-authored facts/outcome, mark it continued atomically, and compose from stored trusted result. Replay returns the persisted assistant turn or safe idempotent response without a second tool continuation.
* Gate naked-name extraction on explicit server-owned lead phase `awaiting_name` created by a visible name prompt. Outside that phase, bare chat never populates name. A greeting classification, including regression input `Hello`, is never a name even in that phase. Explicit validated form input is unchanged.

### Next cart endpoint

Add `confirm_add` to the existing action allowlist. Input is only the one-time confirmation ID plus existing session credential; browser product, owner, quantity, price, currency, and stock values are rejected.

Next loads the same owner-bound session/pending action, verifies the secret hash, and revalidates session, offer, pending and display expiry; display revision; offer ownership; product active/customer-visible state; current positive stock; current price/currency; and bounded positive quantity. It performs add/increment under existing F16 rules and ID consumption in one conditional `widget_sessions.cart_state` update.

Use compare-and-swap on the existing session row/version. On CAS loss, reload, revalidate inventory and pending state, and retry a small bound. A matching consumed ID returns stored result/cart idempotently and never increments twice. A different concurrent action resolves against reloaded state. Inventory is not reserved/decremented.

On price/currency change, consume this execution without adding, refresh pending trusted facts, and record `price_changed`; the tool-result response requests new explicit confirmation before Flask issues a new ID. Expired, inactive, hidden, unavailable, or out-of-stock outcomes clear/invalidate pending and add nothing.

## API Changes

User chat request extension:

```json
{
  "message": "the first one",
  "display_context": {
    "version": "display_context.v1",
    "revision": 7,
    "render_id": "opaque",
    "offer_tokens": ["opaque-a", "opaque-b"]
  }
}
```

Semantic-confirmation Flask response:

```json
{
  "version": "chat_response.v1",
  "assistant_message": null,
  "cart_action": {
    "type": "confirm_add",
    "confirmation_id": "one-time-opaque"
  }
}
```

Next cart request:

```json
{"action":"confirm_add","confirmation_id":"one-time-opaque"}
```

Next response:

```json
{
  "cart": {"customer_safe_existing_cart_shape": true},
  "tool_result": {
    "version": "cart_tool_result.v1",
    "continuation_id": "one-time-opaque",
    "outcome": "added|price_changed|unavailable|expired|conflict",
    "open_cart": true
  }
}
```

`open_cart` is true only for stored `added`. The result is customer-safe, but Flask still resolves facts from server state.

Internal continuation:

```json
{
  "event": {
    "type": "tool_result",
    "version": "cart_tool_result.v1",
    "continuation_id": "one-time-opaque"
  }
}
```

No user message is created. Existing envelopes may keep their names, but these versions, types, allowlists, and semantics are required.

## Authentication / Authorization Impact

Every display, chat, confirmation, cart, and continuation call requires the same active owner-bound widget-session credential. Public calls keep allowed-domain enforcement; preview issuance also requires the authenticated matching owner. Never log secrets/tokens, place them in URLs, expose them to the model, or accept them cross-owner/session. Existing subscription, quota, rate-limit, and abuse policy applies equally to public and preview.

## Security Considerations

* Browser order is only a presentation claim; authorize each token against session offers. Model output is only untrusted intent.
* Use generic unauthorized/not-found errors and constant-time secret-hash comparison where practical.
* Prompt injection cannot extend schemas, expose opaque/hidden data, or invoke Next. Customer-safe serializers remain mandatory.
* Pending is bound to owner/session/display revision/offer/facts/quantity/expiry; execution is one-time and tied to that pending state.
* Preserve CSRF/origin/domain protections, secure cookies/transport, request limits, safe logs, and AI/tool timeouts.

## Error Handling

Typed safe outcomes include `invalid_contract`, `stale_display`, `ambiguous_selection`, `no_pending_confirmation`, `pending_expired`, `offer_expired`, `price_changed`, `unavailable`, `unauthorized`, `rate_limited`, `quota_exhausted`, `conflict`, and `internal_error`. None claims an add. Malformed model output, timeout, auth failure, stale request, or exhausted CAS preserves cart. Price change requires reconfirmation; unavailable/expired clears pending.

Revision rules prevent late chat from restoring old order. Atomic consumption prevents double send, refresh, retry, two tabs, duplicate model confirmation, or continuation from adding twice. Persist the trusted result before responding so network retries recover it.

## Testing Guidance

* Unit/schema: five actions; English/Urdu/Roman Urdu semantic fixtures without phrase matching; malformed/extra fields; bounds; normalization; pending transitions; receipt pruning; and `Hello`/name gate.
* Contract: exact order and sort revision; same-revision idempotency; stale/conflicting display; ambiguous/out-of-range selection; trusted confirmation facts; no premature success; typed `confirm_add`; and internal continuation.
* Authorized non-production Supabase integration: owner/session/offer isolation; preview token issuance; expiry; active/visible stock/price revalidation; price/stock change; CAS conflict; duplicate exactly-once; safe stored receipt; legacy JSON normalization; and no migration.
* Desktop/mobile visible Playwright: mismatched prose/card order selects visible first; sorting changes first; exact confirmation; accept adds once, final LLM acknowledgement, refresh/open/focus; decline/cancel/different request adds nothing; ambiguity/failures recover; preview matches public; transcript resumes; three language modes; keyboard/assistive announcements; and `Hello` never opens/prefills lead capture.
* Negative tests: forged, cross-owner/session, expired, replayed, malformed, rate/quota limited, ended session, price/stock changed, spoofed tool result, model/Next failure, and concurrent duplicates.
* Use dedicated staging data. Local/mock DB is not readiness proof; production is prohibited.

## Migration Validation and Recovery

`NOT_APPLICABLE` — normalization must round-trip legacy cart data and safely omit/prune invalid new state. Rollback stops new reads/writes while leaving unknown JSON harmless; it must not delete carts/conversations. No production migration or data repair.

## Git / Change Boundaries

Developer changes are limited to existing Flask chat/widget-session and cart-state normalization code; existing widget/owner-preview chat UI; existing Next widget cart route; and directly corresponding unit, contract, integration, and Playwright tests/fixtures. Exact paths belong in `implementation-report.md`. Do not change search ranking, unrelated assistant claims, lead workflow beyond the name gate, inventory management, checkout, billing, subscription, migrations, deployment, or release artifacts.

## Risks

* Model interpretation is probabilistic; explicit product confirmation and deterministic resolution fail closed.
* Browser/server order can race; accepted monotonic revisions reject stale work.
* Price/stock can change; Next checks immediately before session mutation, and inquiry cart reserves nothing.
* Responses can be lost/retried; bounded persisted receipts preserve idempotency.

## Out of Scope / Not Implemented

No static product-intent phrase catalogue, DB migration, production/deployment change, payment, checkout, order, reservation, stock decrement, ranking change, cross-session memory, lead redesign, or external integration.

## Implementation Guidance

Implement the smallest versioned additions around existing authentication, serializers, offer validation, cart mutation, and transcript persistence. Share/mirror schemas across browser, Flask, and Next. Fail closed on every unknown version/action/state. Client facts, model output, and response prose never become authority; cart opens only after stored `added`.

## Status

STATUS: ARCHITECTURE_READY
