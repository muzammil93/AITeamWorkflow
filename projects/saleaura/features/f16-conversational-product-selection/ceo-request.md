# CEO Request — Conversational Product Selection and Cart Confirmation

## Context

During visible owner-preview testing, the customer asked for `32gb ram ddr5`.
The assistant named one product while rendering a differently ordered product
row. When the customer then said `can i have the first one?`, the assistant did
not ground `first one` to the first card the customer could see, did not confirm
the exact product, and opened a lead form instead of adding a confirmed product
to the cart.

SaleAura already maintains a conversation for each active session. The
conversation should remain the customer-facing memory for that session, while
structured session context preserves the exact displayed products and their
order for safe actions.

## Requested Outcome

Implement conversational product selection in which the LLM understands
natural references from the complete session conversation and the latest
displayed product context. The LLM must respond naturally; SaleAura must not
depend on a static catalogue of saved phrases.

For a reference such as `the first one`, the LLM should produce a structured
selection action against the latest visible product row. Trusted server logic
must resolve that action to the session-owned product, and the assistant must
confirm the exact product name and key facts. Only after the customer agrees
should the product be revalidated, added to the cart, and the cart opened.

## Approved Product Principle

Use an LLM-understanding plus deterministic-execution boundary:

* The LLM receives the relevant session conversation and ordered, structured
  product context.
* The LLM returns a typed action such as selecting product position one or
  confirming the pending selection.
* Trusted code validates the action against owner/session-scoped offers and
  current inventory.
* The LLM never invents or directly mutates product IDs, offers, or cart state.
* No exhaustive static phrase list is used to understand customer references.

The CEO explicitly approved this direction and requested implementation in the
active Codex thread on 2026-07-30.

## Required Customer Flow

1. The customer sees an ordered product row.
2. The customer refers naturally to one of those products.
3. The LLM identifies the intended reference through structured output.
4. SaleAura resolves it against the exact current displayed order.
5. The assistant confirms the product name, SKU/key specification, and current
   price.
6. The customer agrees or declines.
7. On agreement, SaleAura revalidates the offer, adds it exactly once, and
   opens the cart.
8. On decline, ambiguity, expiry, price change, or unavailable inventory,
   SaleAura does not add the item and explains the next safe action.

## Constraints

* Do not implement reference understanding as a static phrase catalogue.
* Do not let the LLM directly choose arbitrary inventory IDs or mutate carts.
* Do not add an item before explicit customer confirmation.
* Preserve session, owner, offer-token, inventory, price, stock, expiry,
  idempotency, rate-limit, quota, and safe-response boundaries.
* Preserve English, Urdu, and Roman Urdu conversation behavior.
* Keep complete user-visible session chat separate from bounded model context
  and trusted structured action state.
* Make owner preview faithfully exercise the customer-widget selection/cart
  flow rather than opening a preview-only lead form.
* A greeting such as `Hello` must not be inferred as a customer full name.
* Do not change production, billing, deployment, or unrelated product
  behavior.

## Exceptional Repair Authorization

After QA completed a dedicated 10-conversation staging audit, two High findings
remained open:

* `F16-CPS-QA-003` — natural visible-product references could divert to lead
  capture, guess an ambiguous card, or produce ungrounded no-pending recovery.
* `F16-CPS-QA-004` — product-bearing assistant prose could contradict trusted
  PKR cards with a foreign currency symbol.

The controlled repair allowance had reached `2/2`. On 2026-07-30
(Asia/Karachi), the CEO explicitly responded `Yes approved from my side`,
authorizing one exceptional third F16 repair cycle and approving prose currency
grounding as part of this F16 delta. The exceptional cycle must preserve the
LLM-first semantic design, must not add a static phrase catalogue, and must
return through fresh QA, a new 10-conversation first-run audit, and Reviewer.

## Workflow Classification

This is a new customer-visible F16 behavior delta, not an implementation defect
fully covered by the previously approved F16 scope. It follows the standard
controlled sequence:

`CEO Request → Product Manager → Architect → Developer → QA → Reviewer → Final Report`

STATUS: CEO_REQUEST_RECORDED
