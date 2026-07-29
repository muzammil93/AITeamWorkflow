# Product Requirements Document — F16 Chat Widget Sales Flow

## Scope

Complete the public ChatWidget's sales journey: truthful greeting and product presentation, verified-build and modification conversation, private individual-product cart, final-cart review/removal, and consented lead capture after explicit purchase intent.

## Dependencies

* F02 for atomic lead quota enforcement.
* F03 for owner-scoped, active/in-stock inventory and safe product DTO boundaries.
* F08 for anonymous widget sessions and host security.
* F09 for grounded conversation/search responses.
* F10 for protected verified-build snapshots and deterministic complete-build generation.
* F11 for protected current-build modification and confirmation.
* F12 for idempotent consented leads and owner notification behavior.
* F13 for displaying complete lead details to the owner.

## In Scope

* Display the saved owner greeting in the live widget.
* Correct customer product-card availability presentation without exposing raw inventory fields.
* Add offered products to a private customer cart with an editable positive integer quantity. The default is the quantity confidently requested in chat, otherwise one.
* Keep verified builds as one recommendation card in chat. On an explicit customer selection, expand the trusted current build snapshot into individual component cart lines; do not store or display a verified-build bundle in cart.
* Keep build modification in chat and require explicit confirmation under F11. A new or modified build never changes cart contents automatically.
* Mark a cart row that is also included in the latest build as `Already included in your build`; do not block the customer from intentionally keeping it.
* Show a final cart with remove controls and a clear empty state; the shopper may continue asking/searching after any cart change.
* Do not show contact collection merely because a product was added. Show it only after explicit buying intent against a non-empty final cart.
* Create one owner-scoped, idempotent lead that stores a trusted final-cart snapshot, full name, one contact method, and explicit consent before notification. Later confirmed cart changes create a version of that same customer request, not a duplicate lead.
* Preserve current F12 notification behavior: a notification failure cannot erase a saved lead.
* Send the owner the customer contact details and complete cart items/quantities in initial and updated lead notifications; show the same complete data in a Dashboard lead-details dialog.
* Test the visible desktop and mobile flow against the authorized staging Supabase project through MCP using dedicated data.

## Out of Scope

* Checkout, customer payment, order creation, fulfilment, shipping, invoices, or stock reservation/decrement.
* Lead-time stock revalidation. The lead is an inquiry snapshot rather than a promise of availability.
* Live internet research, benchmark scraping, product citations, or a new external data provider.
* Customer accounts, customer WhatsApp chat, and any production mutation.

## Requirements

* `CART-001` — The live widget uses the owner-saved greeting; preview and public widget content must not diverge.
* `CART-002` — An offered product card must make no false availability claim. Search remains limited to the current owner’s active, positive-stock inventory at offer time.
* `CART-003` — Each offered product has an accessible Add to cart action. The cart displays product name, category, offered price/currency, image where available, editable quantity, line total, and a remove action.
* `CART-004` — The browser cannot choose another owner’s product, set price, substitute an inventory ID, or manufacture a cart line. Cart state is private to the authenticated owner-bound anonymous widget session.
* `CART-005` — Adding/removing/cart viewing is non-reserving: it does not mutate inventory stock or create an order. A stock change after an offer does not block the approved lead-inquiry submission.
* `CART-006` — A non-empty final cart is shown before contact collection. Only an explicit customer buying-intent action from that cart opens lead capture.
* `CART-007` — `I want to buy` is the explicit buying-intent CTA for a non-empty final cart. Lead creation requires full name, at least one contact method, and explicit consent. It saves the final cart snapshot idempotently before owner email/WhatsApp notifications, then confirms that a representative will contact the customer.
* `CART-008` — The flow has clear states for unavailable widget/session, invalid/replayed cart action, cart-save failure, empty cart, cancelled lead, validation failure, duplicate lead, and notification failure.
* `CART-009` — Product search, comparison, existing lead capture, owner/session isolation, quotas, and F12 notification preservation retain regression coverage.
* `CART-010` — Desktop and mobile layouts keep cart controls, item names, prices, remove actions, final-cart intent action, and lead form reachable and readable.
* `CART-011` — A confirmed F10/F11 build remains a chat recommendation. Selecting it expands only its trusted current component snapshot into individual cart rows. A modified build never automatically replaces or duplicates prior cart rows; the customer makes each cart change explicitly.
* `CART-012` — Cart quantity defaults to the confidently parsed requested quantity, otherwise one. It is a bounded positive integer the customer can edit; totals and lead context reflect the final quantity.
* `CART-013` — A successful lead leaves the customer able to continue shopping. Cart changes are visibly unsent until `Update my request` is explicitly confirmed; that confirmation records a new request version on the same lead and sends an updated owner notification without consuming a second lead quota.
* `CART-014` — Owner email/WhatsApp notification and the Dashboard lead-details dialog show customer contact details, every final cart item, quantity, price/currency, totals, source/consent facts, and request-version history.

## Acceptance Criteria

* A saved greeting appears unchanged in the public embedded widget after refresh.
* A product returned by chat displays a truthful offer state and can be added once to the session’s cart without exposing raw inventory identity.
* The shopper can add a CPU, keyboard, and monitor/LCD from the same owner catalog, edit quantities, remove one, and see exact remaining quantities, line totals, and final-cart total.
* A selected verified build expands its trusted components into individual cart products. A customer can add/remove any individual component; cart never represents that set as a verified build.
* Adding/removing products makes no stock reservation, inventory write, customer order, or payment action.
* The lead form remains unavailable until a non-empty cart’s explicit buying-intent control is used.
* Missing name/contact/consent prevents a lead; valid `I want to buy` submission creates one owner-scoped lead with final cart context and does not duplicate it on retry. A later explicitly confirmed cart change records an updated request version on that same lead.
* A saved lead remains saved if owner notification fails.
* Initial and updated owner notifications, and the owner Dashboard lead dialog, show the full final cart with quantities and currency.
* Cross-session, cross-owner, expired/replayed, or browser-forged cart actions fail safely without exposing another owner’s product data.
* Required automated, contract, and recorded staging Playwright coverage passes on desktop and mobile, including normal, boundary, invalid, cancelled, unauthorized, quota-limited, and failure cases.

## Open Decisions

No open product decision blocks this planned scope. Quantity is customer-editable and is not a stock reservation or a promise of availability.

STATUS: PRD_READY
