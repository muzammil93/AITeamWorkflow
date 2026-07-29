# Architecture — F16 Chat Widget Sales Flow

## Design

1. Reuse the F08 signed bootstrap and anonymous `widget_sessions` boundary. Cart state is owner- and session-bound; the browser never supplies a trusted owner ID.
2. Extend the F09 customer response contract with an opaque, short-lived offer/action token for each returned product. The token resolves server-side to the session owner and offered inventory row; raw inventory IDs, prices, and owner fields remain absent from public payloads. The safe response also carries the owner-profile currency required for truthful card/cart display.
3. Add a trusted cart command boundary in the Next.js server layer. Add/remove/view/update-quantity commands validate the anonymous session and opaque offer token, derive the owner/session from the server, and store only a bounded cart snapshot. Client price, product ID, owner, context, and arbitrary quantity are discarded or bounded server-side.
4. At add time, only products that were offered from active, positive-stock owner inventory are eligible. Cart changes do not reserve/decrement stock. Lead submission intentionally records the final trusted cart snapshot without a new stock revalidation, per CEO decision.
5. Render the saved `welcome_message` through the same public widget configuration used by the owner preview. Replace the incorrect missing-stock fallback with a truthful offered-product presentation that does not leak exact stock unless separately approved.
6. On explicit build-card selection, resolve the protected current F10/F11 snapshot server-side and expand its component rows into ordinary individual cart lines. Cart data retains only internal origin metadata needed to mark rows already included in the latest build; it never displays a build bundle or compatibility claim. A later build modification does not mutate the cart; the customer chooses any add/remove/change action explicitly.
7. Add explicit ProductCard Add to cart, quantity, cart-summary/remove, and `I want to buy` controls. The purchase-intent control is disabled/hidden for an empty cart and opens the existing F12 form only for the current cart version.
8. Extend F12 lead context with a server-created cart snapshot: product display data, quantity, offered price/currency, line totals, cart version, and timestamp. A later confirmed `Update my request` appends a request version to the existing lead, preserves history, sends an updated notification, and does not consume another lead quota.
9. Add a protected lead-request-version persistence model if existing lead context cannot preserve immutable history. Owner notification builders receive formatted cart lines. F13 renders a lead-details dialog using trusted owner-scoped lead/version data.
10. Bound cart line count, quantity, display fields, request versions, and snapshot size. Cart state is cleared only through explicit customer removal/clear behavior or existing session expiry; it is never shared across sessions or owners.

## Data and Migration Decision

Implementation may add a staging migration only if the protected widget-session record cannot safely retain bounded cart state or the existing lead schema cannot safely retain immutable request-version history. Any migration must be additive, owner/session-scoped, protected by RLS/service boundaries, and validated against the authorized staging Supabase project. Production application is prohibited.

## Validation Plan

* Unit/contract: opaque-token validation, owner/session binding, forgery/replay rejection, bounded cart/quantity behavior, trusted build-snapshot expansion, explicit cart/build separation, no stock write/reservation, request-version/lead idempotency/context, notification cart formatting, Dashboard owner boundary, and greeting/product-card/currency truthfulness.
* Playwright staging: `E2E-033` cart-to-lead flow, `E2E-034` cart/session safety, and `E2E-035` build-to-cart/modification/lead-update flow, plus F08–F13 regressions and `E2E-032` mobile coverage. Final F16 QA cannot pass without recorded Playwright evidence for every F16 requirement.
* Test data: dedicated staging owner, active/in-stock CPU, keyboard, and monitor/LCD rows, plus separate owner/expired-session fixtures. No production database, local database, Flask substitute, or payment-provider action is evidence.

STATUS: ARCHITECTURE_READY
