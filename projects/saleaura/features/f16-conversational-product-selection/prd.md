# Product Requirements Document

## Feature Name

F16 Conversational Product Selection and Cart Confirmation

## Feature ID and Execution Mode

`F16-CONVERSATIONAL-PRODUCT-SELECTION` — Standard Implementation

## CEO Request

Allow a shopper to refer naturally to a product shown in the active chat
session, such as `the first one`, without SaleAura maintaining an exhaustive
catalogue of matching phrases. The LLM must interpret the conversation and
return a typed action. Trusted SaleAura logic must resolve that action against
the exact latest displayed product order, confirm the exact product with the
shopper, and add it exactly once to the existing private inquiry cart only
after explicit agreement. The cart then opens for the shopper.

The approved direction is LLM semantic understanding with deterministic
validation and execution. The LLM may not invent trusted product identity,
mutate the cart directly, or bypass confirmation.

## Master Requirement References

* SaleAura V1 PRD customer journey: anonymous session creation or safe
  resumption; grounded product discovery; explicitly consented lead submission
  with relevant context; and no checkout, ordering, payment, fulfilment, or
  stock reservation.
* SaleAura V1 PRD Product Positioning requirement 6: customer-facing chat
  supports English, Urdu, and Roman Urdu.
* SaleAura V1 PRD Chat Widget requirements 1–3 and 7–9: grounded search and
  comparison, non-fabricated inventory facts, truthful cards, and concise,
  helpful responses.
* SaleAura V1 PRD Widget Customization requirements 5 and 8: structured actions
  remain domain-authorized and authenticated preview cannot weaken public
  widget enforcement.
* SaleAura V1 PRD Security, Reliability, and Production Readiness requirements
  3, 6–9, 15, 17, and 18: customer-safe data, reliable sessions, preserved
  abuse/quota boundaries, safe failures, protected public widget APIs, staging
  database proof, and proportionate Playwright coverage.

## Dependency References

* `F08 / WIDGET-002`, `WIDGET-004`–`WIDGET-008`, and `SEC-CHAT-001` for
  authenticated preview, domain authorization, owner-bound anonymous sessions,
  bounded trusted session state, subscription checks, abuse controls, and
  protected persistence.
* `F09 / CHAT-001`–`CHAT-007` for multilingual model understanding, versioned
  structured actions, owner-inventory grounding, customer-safe response data,
  non-fabrication, and meaningful AI quota handling.
* `F16 Chat Widget Sales Flow / CART-002`–`CART-010` and `CART-012` for offered
  products, private cart actions, explicit purchase intent, safe failure
  states, mobile accessibility, bounded quantity, and the inquiry-not-checkout
  boundary.
* The direct CEO request at
  `features/f16-conversational-product-selection/ceo-request.md`.

## Baseline QA Findings

During visible owner-preview testing:

* The assistant named one product while the rendered product row used a
  different order.
* The shopper's `can i have the first one?` was not grounded to the first card
  visible to that shopper.
* The assistant did not confirm exact product identity and opened lead capture
  instead of adding a confirmed product to the cart.
* `Hello` was incorrectly inferred as the shopper's full name.

These observations define the approved behavior delta; formal QA findings will
be owned by QA after implementation.

## Clarifying Questions

No open clarification blocks implementation. In this feature, `add to cart`
means the existing private, non-reserving F16 inquiry cart. It does not create
an order or complete a purchase.

## Finalized Scope

### In Scope

* LLM interpretation of natural product references and confirmation or
  rejection across English, Urdu, and Roman Urdu through a versioned,
  allowlisted structured-action contract.
* Trusted session context for the latest product row in the exact order
  currently displayed to the shopper, including sort changes.
* Deterministic resolution of a model-proposed position/reference to an
  owner- and session-scoped offered product.
* A product-specific pending-confirmation state and assistant confirmation that
  identifies the exact product before any cart mutation.
* Revalidation of owner, session, offer expiry, product availability, stock,
  price, currency, and bounded quantity after agreement and before add.
* Idempotent, exactly-once cart execution followed by opening the existing cart.
* Safe ambiguity, decline, cancellation, stale response, expiry, price-change,
  unavailable-product, and malformed-action behavior.
* Equivalent selection and cart behavior in authenticated owner preview and
  the public customer widget.
* Protection against treating a greeting such as `Hello` as a person's name.
* Complete shopper-visible chat continuity for the active session, kept
  distinct from bounded model input and bounded trusted action state.
* Automated, contract, staging Supabase, desktop/mobile, and visible Playwright
  verification proportionate to the behavior and security boundaries.

### Out of Scope

* An exhaustive static dictionary, regular-expression catalogue, or translated
  phrase list for interpreting product references or consent.
* Search relevance/ranking changes, broader product-card ordering changes, or
  rewriting unrelated assistant product claims.
* Checkout, customer payment, order creation, fulfilment, shipping, invoicing,
  or inventory reservation/decrement.
* Changes to lead qualification, lead quotas, owner notifications, billing,
  subscriptions, production data, deployment, or external providers.
* Customer accounts, durable cross-session shopper identity, or carrying
  product-selection state into a different/expired session.
* Unrelated currency-display and product-description truncation fixes.

## Assumptions

* The existing F16 private inquiry cart and offered-product security boundary
  remain the destination for a confirmed selection.
* The browser can report the exact currently displayed offer order through a
  trusted, session-validated contract; browser-supplied product identity,
  price, owner, and stock remain untrusted.
* The full active-session transcript can remain visible to the shopper without
  sending an unbounded transcript to the model on every turn.
* The model may receive a bounded, relevant conversation window and trusted
  structured context or summary. The latest displayed row and any pending
  confirmation must be supplied explicitly and must never be reconstructed by
  model guesswork from a truncated transcript.
* Existing session expiry, subscription, rate-limit, and AI quota policies
  remain authoritative.
* Price and stock can change between product display, confirmation, and cart
  execution.

## User Stories

* As a shopper, I want to say `the first one`, `the Crucial one`, or an
  equivalent natural expression so I can select what I can actually see
  without learning special commands.
* As a shopper, I want SaleAura to repeat the exact product before adding it so
  I can catch a misunderstanding.
* As a shopper, I want my agreement to add only the confirmed product once and
  open the cart so I can review it.
* As a multilingual shopper, I want the same natural selection, clarification,
  confirmation, and cancellation behavior in English, Urdu, and Roman Urdu.
* As a shopper, I want earlier chat to remain visible throughout my active
  session while SaleAura safely remembers the current displayed products and
  pending action.
* As a business owner, I want preview to exercise the same customer selection
  path so it accurately represents the installed widget.
* As a business owner, I want SaleAura to reject forged, expired, stale, or
  cross-session product actions so another shopper or store cannot affect my
  cart.

## Functional Requirements

* `CPS-001` — SaleAura must use the LLM to interpret natural product references,
  selection intent, confirmation, rejection, and clarification need from the
  relevant active-session conversation and trusted structured product context.
  Product-reference understanding must not depend on an exhaustive static
  catalogue of phrases in any supported language.
* `CPS-002` — Model-backed selection behavior must use a versioned, typed,
  allowlisted structured-action contract. Supported outcomes must distinguish
  at least selection, confirmation, rejection/cancellation, clarification, and
  no product action. Malformed, unsupported, or schema-invalid output must not
  mutate trusted state and must recover with a safe customer response.
* `CPS-003` — Every rendered product row must have a session-owned display
  version and an ordered set of opaque offered-product references. The trusted
  session context must represent the exact order currently visible to the
  shopper after approved sorting or reordering. A late/stale response must not
  overwrite a newer visible-row version.
* `CPS-004` — The model may identify a visible position or an unambiguous
  reference within the supplied structured context, but it may not supply an
  arbitrary trusted inventory ID, owner ID, price, stock value, or cart
  mutation. Trusted server logic must resolve the action only against valid
  offers owned by the active owner-bound session and display version.
* `CPS-005` — Ordinal or relative references such as a first, second, or last
  item must resolve against the latest exact row displayed to that shopper.
  They must not resolve against model prose, database search order, an earlier
  unspecific row, or a server order that differs from the browser display. If
  the current visible order cannot be proven, SaleAura must ask for
  clarification and add nothing.
* `CPS-006` — When the model's proposed selection resolves uniquely, SaleAura
  must create a bounded, server-owned pending confirmation tied to the active
  session, display version, offer, expected product facts, and expiry. The
  assistant must ask the shopper to confirm the trusted product name, SKU or
  equivalent distinguishing key specification, quantity when relevant, and
  current price/currency. No product may be added at this stage.
* `CPS-007` — When a reference can reasonably identify multiple products, no
  current displayed product, or a stale/expired offer, SaleAura must add
  nothing and ask a concise question that exposes only customer-safe facts
  sufficient to disambiguate or repeat the search.
* `CPS-008` — Agreement or rejection must be interpreted semantically by the
  LLM in the conversation language and returned as a typed action. A
  confirmation action is valid only when an unexpired pending confirmation
  exists in the same owner-bound session. An unrelated affirmation without
  pending state, or agreement attached to a different product, must not add
  anything.
* `CPS-009` — A valid rejection or cancellation must clear the applicable
  pending confirmation, preserve the cart, and let the shopper continue the
  conversation. A new product request or selection while confirmation is
  pending must never be treated as agreement to the old product; SaleAura must
  safely replace, cancel, or explicitly clarify the pending selection.
* `CPS-010` — After valid agreement and immediately before cart mutation,
  trusted code must revalidate session and owner binding, action/display
  version, offer authenticity and expiry, active/customer-visible product
  state, positive stock, current price/currency, and bounded positive quantity.
  Browser fields and model prose are not authoritative for these values.
* `CPS-011` — If price changes after the confirmation prompt, SaleAura must add
  nothing, show the new customer-safe price, and require a new explicit
  confirmation. If the product is expired, inactive, unavailable, or out of
  stock, SaleAura must add nothing, clear or invalidate the pending action, and
  explain the safe next step without promising availability.
* `CPS-012` — A successful confirmed action must be consumed atomically and
  idempotently so retry, double send, duplicate model output, refresh, or
  concurrent delivery cannot add or increment the product more than once.
  A later intentional change requires a new explicit shopper action. The
  resulting line and quantity must follow existing F16 cart rules.
* `CPS-013` — After a successful add, the assistant must identify what was
  added using trusted customer-safe facts, the widget must refresh the private
  cart, and the cart must open for shopper review. Lead capture must not open
  merely because conversational selection succeeded; the existing explicit
  non-empty-cart buying-intent step remains required.
* `CPS-014` — The authenticated owner preview and public customer widget must
  use the same structured selection, pending-confirmation, validation,
  cart-mutation, and cart-opening contract. Preview authorization may differ as
  already approved by F08, but preview must not substitute a lead form or
  bypass customer-flow safeguards.
* `CPS-015` — The complete chat transcript available to the shopper must remain
  visible and resumable for the valid active session according to existing
  session behavior. Model input must remain bounded and may use a relevant
  window plus trusted structured context/summary. Truncation or summarization
  must not change displayed order, selected offer identity, confirmation state,
  or cart state.
* `CPS-016` — When the widget session ends, expires, is invalidated, or cannot
  be safely resumed, its visible product-order context, pending confirmation,
  and offer authority must not be usable by a new session. Late responses or
  actions from the old session must fail safely. Existing authorized retention
  of owner-visible conversation records is unchanged and does not authorize
  cross-session customer actions.
* `CPS-017` — Product-selection behavior and recovery messages must preserve
  English, Urdu, and Roman Urdu conversation. A language change within an
  active session must not change the trusted selected product or allow
  confirmation to bypass pending state.
* `CPS-018` — Product selection must preserve F08/F09 allowed-domain, preview
  authentication, owner/session isolation, subscription, rate-limit, quota,
  safe-response, and customer-safe data boundaries. Prompt injection or model
  output must not expose or authorize raw identifiers, secrets, hidden
  inventory fields, other sessions, or other owners.
* `CPS-019` — A greeting or conversational word such as `Hello` must never be
  inferred as the shopper's full name. A name may be captured only from an
  explicit form entry or an unambiguous answer while SaleAura is actively and
  visibly requesting the shopper's name; product selection must not open or
  prefill lead capture.
* `CPS-020` — Confirmation, clarification, error, and cart-open outcomes must
  be usable on desktop and mobile and accessible by keyboard and assistive
  technology. The confirmed product identity and price must be available as
  text; opening the cart must provide a clear announced/focus outcome without
  hiding the continuation of chat.
* `CPS-021` — Automated, contract, integration, and Playwright coverage must
  include normal, boundary, ambiguous, declined, cancelled, malformed,
  unauthorized, expired, price-changed, stock-changed, duplicate, concurrent,
  quota/rate-limited, session-expired, and cross-owner/session behavior.
  Database-backed readiness evidence must use the authorized non-production
  Supabase project and dedicated test data; production mutation is prohibited.

## Acceptance Criteria

* With a visible row whose first card is Product A while assistant prose names
  Product B, a natural reference meaning `the first one` produces a structured
  selection for visible position one and asks the shopper to confirm Product A
  by trusted name, SKU/key specification, quantity where relevant, and current
  price. Product B is not silently selected.
* Changing the visible row from default ordering to low-to-high or high-to-low
  changes the meaning of a positional reference to match the exact newly
  displayed order. A stale response cannot restore the prior order.
* Natural English, Urdu, and Roman Urdu references are understood through model
  semantics without a maintained exhaustive phrase catalogue. The same typed
  action contract and trusted validation boundary applies to every language.
* An unambiguous named or positional reference creates pending confirmation and
  does not mutate the cart. An ambiguous, missing, stale, or expired reference
  asks for clarification and does not mutate the cart.
* A semantically clear agreement to an active product-specific confirmation
  causes trusted revalidation, one idempotent add, a truthful acknowledgement,
  cart refresh, and automatic cart opening. Duplicate delivery or retry does
  not add or increment the item again.
* A decline, cancellation, unrelated affirmation, agreement without pending
  state, or request for a different product adds nothing and leaves the shopper
  in a clear recoverable state.
* A price change requires a new confirmation showing the changed price.
  Expired, inactive, unavailable, out-of-stock, forged, cross-owner, or
  cross-session offers are not added and reveal no unsafe data.
* Product selection never directly opens lead capture. The existing final-cart
  review and explicit buying-intent requirements remain intact, and no stock
  reservation, order, payment, or fulfilment behavior is introduced.
* Owner preview follows the same visible selection, confirmation, add, and
  cart-open journey as the public widget, on desktop and mobile.
* The active-session transcript remains visible across supported safe resumption
  while bounded model context still resolves the current displayed row and
  pending confirmation correctly. Expired-session state cannot act in a new
  session.
* Sending `Hello` as a greeting never populates a full-name field, creates a
  lead, or opens lead capture.
* Required unit/contract/integration checks and recorded staging Playwright
  journeys pass for the normal flow and every applicable negative, concurrency,
  accessibility, isolation, rate/quota, and lifecycle case listed in
  `CPS-021`.

## Risks / Open Questions

* Model interpretation is probabilistic. The required product-specific
  confirmation and deterministic server resolution are the product safeguards;
  lowering confidence must result in clarification rather than a guessed add.
* Browser-visible order and server-trusted offer order can race when sorting or
  new results arrive. Architecture must define versioning/acknowledgement so
  only the row actually visible at send time can be selected.
* Sending an unbounded transcript to the model would create cost, latency,
  privacy, and context-window risk. Architecture must preserve full
  shopper-visible session continuity while bounding model context without
  allowing summaries to become authority for product identity.
* No CEO decision is currently required. Architecture must choose the smallest
  secure persistence and structured-action design compatible with existing
  F08/F09/F16 boundaries.

## Status

STATUS: PRD_READY
