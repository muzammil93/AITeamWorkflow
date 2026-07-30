# Architecture Document

## Feature Name

F16 Conversational Product Selection and Cart Confirmation

## Feature ID and Execution Mode

`F16-CONVERSATIONAL-PRODUCT-SELECTION` — Standard Implementation

## PRD Reference

`features/f16-conversational-product-selection/prd.md`, `CPS-001`–`CPS-026`, including CEO-authorized exceptional repair cycle `3/3` under `CC-004`.

## Master Architecture / Requirement References

Preserve the existing F08 protected widget-session, allowed-domain, authenticated preview, subscription, rate-limit, and abuse boundaries; F09 bounded multilingual chat, structured output, quota, grounded and safe responses; and F16 private inquiry cart and offered-product safeguards. This remains inquiry, not checkout, ordering, payment, or inventory reservation.

## Baseline QA Findings

The original visible-order, confirmation, preview, and `Hello` defects remain covered. The QA 10-conversation audit additionally left `F16-CPS-QA-003` and `F16-CPS-QA-004` open: first-run natural references could divert to lead capture, ambiguous/no-pending/different-product/reject turns could be ungrounded, and discovery prose could contradict trusted PKR cards with foreign currency symbols. `CC-004` authorizes only the smallest repair of those two High findings.

## Dependency Validation

* The owner-bound `widget_sessions` row and existing JSON `cart_state` remain authoritative for offers, cart, and bounded selection state.
* The Flask chat service remains model-facing. The existing Next cart endpoint remains the sole cart-mutation authority.
* Reuse existing opaque offer tokens, session authentication, customer-safe inventory serialization, quota, and abuse controls.
* `CC-004` adds no cart-state shape, mutation, RPC, or DB migration. Preserve the already implemented CAS/terminal-receipt design unchanged.

## Technical Summary

1. On each user chat send, the widget snapshots the exact rendered card order as opaque offer tokens with a monotonically increasing display revision.
2. Flask authenticates the session, validates all tokens against that session's unexpired `cart_state.offers`, rejects stale revisions, and stores bounded `current_display`.
3. Flask gives the LLM a bounded conversation window and trusted visible-product summaries derived server-side in accepted display order. Browser-authored product facts are never model or execution authority.
4. Before lead/general routing, Flask derives a trusted state mode and invokes the authoritative `product_action.v2` classifier. It returns only `select`, `confirm`, `reject`, `clarify`, or `no_action` plus a typed reason. No static phrase, regex, or translated phrase catalogue interprets product intent.
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

## State-Mode Model Contract

Flask derives, supplies, and later verifies exactly one state mode from trusted session state: `visible_row`, `pending_confirmation`, or `no_actionable_context`. The model cannot choose or change it. The model sees bounded chat plus numbered trusted summaries/current pending facts, not owner IDs, inventory IDs, offer tokens, hidden fields, or mutation tools.

```json
{
  "contract": "product_action.v2",
  "state_mode": "visible_row|pending_confirmation|no_actionable_context",
  "action": "select|confirm|reject|clarify|no_action",
  "reason": "resolved_reference|ambiguous_reference|uncertain_reference|confirmed|rejected|different_product_requested|no_pending_confirmation|not_product_action",
  "position": 1,
  "candidate_positions": [1, 2]
}
```

`position` is required only for `select`; bounded `candidate_positions` is allowed only for `clarify`; extra fields and incompatible state/action/reason combinations fail validation. Server-generated failure reasons additionally include `malformed_output`, `unsupported_contract`, and `state_mismatch`.

The classifier is authoritative before any lead/general model path whenever it produces a product action or a fail-closed product reason. Only a valid `no_action` + `not_product_action` result may release the turn to existing general/lead routing. The prompt must distinguish product inquiry from explicit buying-intent lead capture, but must do so semantically rather than with saved phrases.

State allowlists are mandatory:

* `visible_row`: uniquely grounded intent may `select`; unanchored, multi-candidate, or uncertain intent must `clarify`; valid `no_action/not_product_action` alone may fall through.
* `pending_confirmation`: agreement may `confirm`; decline/cancel must `reject/rejected`; a request for another item must `clarify/different_product_requested`; uncertainty must `clarify`. It cannot become lead capture or confirm the old item.
* `no_actionable_context`: `select` and `confirm` are invalid. Apparent agreement/request without authority becomes `clarify/no_pending_confirmation`; only unrelated intent may be `no_action/not_product_action`.

Malformed, unsupported, state-inconsistent, low-confidence, or uncertain outcomes never expose model prose. Flask maps the typed reason to a concise server-owned localized fallback grounded only in current display/pending facts. No fallback may mention internal schema terms such as `candidate_positions` or invent products/topics.

For `reject`, Flask captures trusted pending facts, clears only pending authority, preserves `current_display`, and says the named item was not added. For `different_product_requested`, it prevents old confirmation, clears/replaces pending as appropriate, preserves the visible row, and asks which current alternative is intended. These transitions add nothing and keep the row available on the next turn.

## Product Prose Grounding

Every product-bearing response—discovery, comparison, confirmation, rejection, recovery, price change, unavailable, and successful add—must carry the trusted product DTO/fact envelope used for validation. Before persistence or delivery, Flask validates each prose monetary claim against canonical owner currency and exact trusted amounts for the products in that response.

Currency codes/symbols/aliases come from canonical currency metadata, not semantic phrase matching. An amount is compared in canonical decimal/minor units; no conversion, rounding substitution, or foreign marker is accepted. Non-price specifications such as capacity or speed are not treated as monetary claims.

On mismatch or unverifiable product money prose, discard the entire candidate response. Regenerate at most once using only trusted DTO facts, validate again, then use a deterministic localized safe fallback that either formats exact trusted amount/currency server-side or omits the price claim. Never repair by blind symbol replacement, and never change structured cards, identity, pending/cart state, or owner currency.

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
* Derive state mode before model invocation; run `product_action.v2` before lead/general routing and require an explicit validated `no_action/not_product_action` release token before fallthrough.
* Accept display only after widget-session/owner and offer validation. Apply atomic/CAS revision rules: higher replaces; same is idempotent only with identical `render_id` and order; lower/conflicting returns `stale_display`.
* Resolve indexed summaries from session offers and current customer-safe serializers. Never trust client/model identity or facts.
* Convert invalid/uncertain/state-impossible semantic outputs to typed server reasons and state-grounded localized fallbacks. Preserve display across reject/different-product handling and retain pending facts long enough to name what was not added.
* Apply amount/currency validation to every product-bearing prose response before transcript persistence or client delivery; foreign or conflicting money claims use bounded regeneration then deterministic safe fallback.
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

Typed safe outcomes include `invalid_contract`, `malformed_output`, `unsupported_contract`, `state_mismatch`, `ambiguous_selection`, `uncertain_reference`, `different_product_requested`, `no_pending_confirmation`, `stale_display`, `pending_expired`, `offer_expired`, `price_changed`, `unavailable`, `prose_fact_mismatch`, `unauthorized`, `rate_limited`, `quota_exhausted`, `conflict`, and `internal_error`. None claims an add. Semantic failures return only the state-grounded fallback; monetary mismatch never reaches the transcript/client. Cart behavior remains unchanged.

Revision rules prevent late chat from restoring old order. Atomic consumption prevents double send, refresh, retry, two tabs, duplicate model confirmation, or continuation from adding twice. Persist the trusted result before responding so network retries recover it.

## Testing Guidance

* Captured-model unit regressions must replay every audit failure: default and sorted natural ordinal returned as `lead_capture`; preview relative selection/consent returned as general message; unanchored `that one` guessed position one; no-pending consent mentioned `candidate positions`; different-product lost the visible row; rejection recommended an unrelated prose-first product; and discovery substituted `₱` or `₦` for PKR.
* Contract tests must cover all state/action/reason allowlist combinations, mismatched echoed state, malformed/old version, low confidence, and routing precedence. Assert product/fail-closed results never invoke lead/general handling and only valid `no_action/not_product_action` does.
* State transition tests must prove reject names the trusted pending product, clears pending, preserves display, and adds nothing; different-product prevents confirmation, preserves display, and asks for an alternative; no-pending consent is grounded; ambiguity never defaults to position one.
* Prose-validator tests must cover correct/foreign codes, symbols, and aliases; conflicting amounts; multiple product DTOs; capacity/speed numbers; English, Urdu, and Roman Urdu; first validation failure followed by valid regeneration; second failure deterministic fallback; and no invalid text persisted or returned.
* Rerun all existing deterministic, contract, authorized non-production Supabase, full F16 desktop/mobile/preview Playwright, lifecycle, cart concurrency/idempotency, multilingual/resume/accessibility, rate/quota, search/cart/lead/build, and cleanup checks. `CC-004` must not regress the verified cart/DB boundary.
* QA must execute ten distinct clean staging sessions matching the prior audit categories: default ordinal; sorted ordinal plus rejection; different product while pending; ambiguous reference; consent without pending; explicit reject; expired confirmation; price change; unavailable with discovery pricing; and name plus Urdu/Roman Urdu/language switch/resume.
* Acceptance is first-run only: preserve every original attempt; a rerun cannot replace a failure. Across all ten, require zero visible/sorted-reference errors, ambiguity guesses, pending/no-pending errors, different-product/reject context loss, product-action lead/general diversion, ungrounded fallback/internal terms, or amount/currency contradictions. Recovery carts remain closed; successful confirmation adds once and opens cart.
* Use dedicated staging data with exact cleanup. Local/mock DB is not readiness proof; production is prohibited.

## Migration Validation and Recovery

`NOT_APPLICABLE` for `CC-004` — retain the existing cart-state normalization, CAS functions, terminal receipts, migration history, and grants unchanged. This repair adds no schema/migration/data repair and rollback affects only classifier/routing/prose-validation behavior.

## Git / Change Boundaries

For exceptional repair `3/3`, Developer changes are limited to the existing Flask product-action prompt/schema/parser, state-aware chat/lead/general router, grounded product-response composer/validator, and directly corresponding captured-model, contract, integration, and Playwright tests/fixtures. Exact paths belong in `implementation-report.md`. Do not change frontend display/cart contracts, Next cart mutation, cart-state normalization, CAS/RPC functions, DB/migrations/grants, search ranking, lead contract, checkout, billing, subscription, deployment, production, or release artifacts.

## Risks

* Model interpretation is probabilistic; explicit product confirmation and deterministic resolution fail closed.
* A classifier can still be confidently wrong; state-specific prompts, strict routing precedence, captured failures, and first-run audit acceptance are required rather than relying on bounded reruns.
* Prose validation can mistake technical numbers for money; validate only currency-marked/structured monetary claims against response DTOs and fall back safely on uncertainty.
* Browser/server order can race; accepted monotonic revisions reject stale work.
* Price/stock can change; Next checks immediately before session mutation, and inquiry cart reserves nothing.
* Responses can be lost/retried; bounded persisted receipts preserve idempotency.

## Out of Scope / Not Implemented

No static product-intent phrase catalogue, cart/DB redesign, new migration, production/deployment change, payment, checkout, order, reservation, stock decrement, ranking change, cross-session memory, lead redesign, unrelated prose rewrite, or external integration.

## Implementation Guidance

Implement `product_action.v2` and universal product-prose validation at the existing Flask boundary. Keep session/display/pending/cart execution and APIs unchanged. Fail closed before persistence/routing on unknown state/version/action/reason or ungrounded money prose. Product semantics remain LLM-based; trusted code supplies mode, validates authority/facts, and chooses fallbacks. Cart opens only after stored `added`.

## Status

STATUS: ARCHITECTURE_READY
