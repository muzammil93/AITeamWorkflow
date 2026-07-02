# Product Requirements Document

## Feature Name

Plans, Billing, and Entitlements Delta

## Feature ID and Execution Mode

`F02` — `QA_FIRST` baseline failure followed by delta implementation

## CEO Request

Verify and complete the existing SaleAura V1 plan, Polar billing, entitlement, quota, and payment-security implementation for requirements `PLAN-001` through `SEC-PAY-001`.

Reference: `projects/saleaura/features/f02-plans-billing-and-entitlements/ceo-request.md`.

## Master Requirement References

* `PLAN-001`, `PLAN-002`
* `BILLING-001`, `BILLING-002`, `BILLING-003`
* `ENTITLEMENT-001` through `ENTITLEMENT-004`
* `QUOTA-001`
* `SEC-PAY-001`
* Master PRD sections “Plans and Usage” and “Plans”
* Master architecture owner lifecycle, service-role, RLS, billing, and atomic quota guidance
* Polar subscription skill lifecycle and idempotency guidance

## Dependency References

* `F00 — Development Safety Baseline` is integrated.
* `F01 — Owner Identity and Onboarding` is integrated at product commit `b48d8bc`.
* The authenticated owner ID established by F01 is the only application customer identity accepted by F02.

## Baseline QA Findings

* `F02-QA-001`: Runtime Polar catalog does not match locked SaleAura plans.
* `F02-QA-002`: Checkout lacks stable external-customer reconciliation and safe errors.
* `F02-QA-003`: Webhook deduplication can lose retries; lifecycle/payment handling is incomplete.
* `F02-QA-004`: Checkout return and checkout events overstate or grant activation.
* `F02-QA-005`: Effective access mode is not resolved or displayed consistently.
* `F02-QA-006`: Widget and some new-activity paths bypass effective entitlement.
* `F02-QA-007`: Inventory quota is not atomic and can be bypassed.
* `F02-QA-008`: Payment/event grants and quota functions are not explicitly restricted.
* `F02-QA-009`: Consolidated subscription SQL is not executable.
* `F02-QA-010`: Required F02 behavior lacks regression evidence.

## Clarifying Decisions

No CEO clarification is required for application behavior. The master PRD, architecture, and Polar lifecycle guidance resolve the functional delta.

One external configuration fact remains:

* The configured Polar sandbox currently has a USD 20 “Standard” product and no Growth product.
* F02 implementation must not silently use that product.
* Code must fail checkout safely until exact USD 19 Starter and USD 49 Growth recurring product IDs are configured.
* Creating or modifying Polar products is an external billing-system mutation and remains outside this implementation unless separately authorized.

## Finalized Scope

### In Scope

* Make locked SaleAura plan prices/quotas the application source of truth.
* Display Free, Starter, and Growth consistently from a typed safe plan DTO.
* Show current plan, subscription status, effective access mode, trial/period end, quota usage, and owner payment history.
* Create Polar checkout only for authenticated owners and exact configured paid products.
* Include owner ID as both `external_customer_id` and deterministic metadata.
* Validate the configured Polar product’s recurring interval and fixed USD price before creating checkout.
* Use exact trusted application return URLs and stable public error codes.
* Add authenticated customer-portal session creation using the owner external customer ID.
* Verify Polar webhook signatures through the existing official adapter.
* Handle:
  * `subscription.created`
  * `subscription.updated`
  * `subscription.active`
  * `subscription.canceled`
  * `subscription.uncanceled`
  * `subscription.past_due`
  * `subscription.revoked`
  * `order.paid`
* Derive owner identity from Polar `customer.externalId` and deterministic metadata, rejecting conflicts.
* Derive plan tier from the configured Polar product ID rather than caller-controlled metadata.
* Make webhook effects retry-safe and record completion only after effects succeed.
* Record payment history only from `order.paid`, idempotently by Polar order ID.
* Resolve exactly one effective access mode:
  * `active`
  * `retained`
  * `unavailable`
* Preserve scheduled-cancellation access until the paid period ends.
* Bound active paid access by verified period dates so stale state fails closed.
* Preserve existing owner data in retained mode.
* Block widget/public activity, new leads, new AI responses, and new inventory rows in retained mode.
* Keep existing inventory-row updates allowed when new-row quota is exhausted or access is retained.
* Enforce lead, AI, and inventory quotas through service-role-only database functions.
* Make inventory batch quota checking and upsert atomic under an owner lock.
* Make lead quota consumption and lead insertion one database transaction.
* Remove direct browser inventory insertion while preserving intended owner reads/updates pending F03.
* Restrict payments, webhook events, products, FX rows, and internal billing/quota functions to intended roles.
* Store only minimal billing event audit metadata, not complete provider payloads.
* Create one canonical additive F02 migration and reconcile `supabase-schema.sql`.
* Add TypeScript, Python, and executable PostgreSQL regression evidence.

### Out of Scope

* Annual billing.
* Coupons, discounts, taxes, seat/team billing, multiple businesses, or manual invoices.
* Automated refunds or refund-policy changes.
* Customer purchase checkout, fulfilment, shipping, or commerce payments.
* Account deletion or export.
* F03 SKU/source/archive/manual inventory features.
* F08 allowed-domain, signed widget bootstrap, and anonymous-session redesign.
* F12 lead form/build-snapshot redesign.
* Legal content changes.
* Production or shared-staging migration.
* Creating/updating Polar products without separate authorization.

## Locked Plan Contract

| Tier | Price | Billing | Inventory | Leads / month | AI responses / month |
| --- | ---: | --- | ---: | ---: | ---: |
| Free | USD 0 | 30-day trial | 100 | 25 | 500 |
| Starter | USD 19 | Monthly | 500 | 150 | 2,000 |
| Growth | USD 49 | Monthly | Unlimited | 600 | 8,000 |

No database row, URL parameter, webhook metadata value, or mutable Polar product description may override this contract.

## Effective Access Contract

### `active`

* Free owner is inside the 30-day trial; or
* Paid owner has a verified supported plan, lifecycle status `active`, `trialing`, or `past_due`, and a future verified period end; or
* Paid owner has scheduled cancellation and a future effective end.

New metered activity is eligible, subject to quota.

### `retained`

* Free trial has expired; or
* Paid subscription has reached effective cancellation/revocation/end; or
* Paid lifecycle state is non-active and no future paid access remains.

Owner authentication and reads of existing approved profile, billing, inventory, and lead data remain available. New widget/public activity, leads, AI responses, and inventory inserts are disabled.

### `unavailable`

* Required owner/billing data cannot be loaded or validated.
* Plan tier is unsupported or lifecycle state is contradictory.
* Entitlement resolver/database call fails.

New metered activity fails closed. UI shows a retry state rather than presenting retained/active as confirmed.

## Functional Requirements

### Plan display

1. UI and public plan API return the locked three-plan catalog.
2. Mutable database rows may provide neither price nor quota authority.
3. Localized amounts, if shown, are estimates derived from protected FX data; checkout remains USD.
4. Billing shows current tier, lifecycle status, effective mode, relevant end date, and all three quota usages.
5. Payment history is owner-scoped and contains only verified `order.paid` records.

### Checkout and portal

1. Only an authenticated owner can create checkout or portal sessions.
2. Free tier is rejected as non-checkout.
3. Paid tier must map to one configured non-placeholder product ID.
4. Polar product verification must confirm:
   * public/non-archived recurring product;
   * monthly recurrence;
   * one fixed USD price matching 1,900 or 4,900 cents.
5. Checkout sends product ID, authenticated email, `externalCustomerId = user.id`, safe success/return URLs, and `{ userId, planTier }`.
6. Checkout response contains only the HTTPS checkout URL.
7. Errors use stable public codes/messages.
8. Portal sessions use the authenticated owner’s external ID and return only a safe HTTPS URL.

### Webhook processing

1. Signature failure remains `403` through the official Polar adapter.
2. Event key uses the verified payload type, timestamp, and resource ID.
3. Completed duplicate delivery returns success without new effects.
4. Failed or interrupted processing remains retryable.
5. Subscription owner and plan mappings reject absent/conflicting/unknown values.
6. Lifecycle updates are idempotent exact-owner writes.
7. Scheduled cancellation keeps its plan and future period end.
8. Revocation/effective cancellation keeps retained data and records inactive lifecycle; it does not delete/downgrade business data.
9. Reactivation/uncancel updates lifecycle and restores active eligibility when the verified period is future.
10. Only `order.paid` inserts/updates payment history.
11. Payment amount comes from the verified order total in cents and order currency.
12. Event audit storage excludes full payload/customer/contact data.

### Entitlement and quotas

1. One database resolver returns mode and quota state.
2. TypeScript and Python consume the same resolver rather than reimplementing lifecycle rules.
3. Failure to resolve returns `unavailable` and blocks metered actions.
4. Lead and AI counters cannot exceed locked limits under concurrency.
5. Lead insertion and lead counter consumption share one database transaction.
6. Inventory batch upsert locks the owner, counts genuinely new IDs, allows existing-ID updates, and rejects over-limit inserts atomically.
7. Direct anon/authenticated inventory insertion is denied.
8. Widget configuration fails closed when owner mode is not active.
9. Verified reactivation restores eligible metered activity without recreating inventory.

## Security Requirements

* Service-role keys remain server-side.
* Browser input cannot set customer ID, plan, subscription status, entitlement mode, payment amount, event ID, or quota counters.
* Provider product ID determines paid plan mapping.
* Raw Polar, Supabase, and backend errors are not returned.
* `payments`:
  * authenticated owner SELECT through RLS;
  * no anon access;
  * no authenticated writes.
* `billing_webhook_events`:
  * service-role only;
  * no browser reads/writes.
* Internal entitlement/quota/write functions:
  * revoked from `PUBLIC`, `anon`, and `authenticated`;
  * granted only to `service_role`.
* Public plans expose only safe catalog fields.
* Webhook audit rows store no full payload.

## Acceptance Criteria

1. `PLAN-001` passes when every application surface uses exactly the locked contract and checkout refuses mismatched/missing Polar products.
2. `PLAN-002` passes when billing displays current plan, lifecycle/effective mode, usage, available plans, and verified payment history with unavailable states.
3. `BILLING-001` passes when authenticated checkout includes external customer ID, deterministic metadata, exact URLs/product verification, and stable errors.
4. `BILLING-002` passes when duplicate/completed events skip, failed events retry, all required lifecycle events apply, and `order.paid` alone records payments.
5. `BILLING-003` passes when checkout return is pending-only and no browser/checkout event grants access.
6. `ENTITLEMENT-001` passes when one resolver consistently returns `active`, `retained`, or `unavailable`.
7. `ENTITLEMENT-002` passes when retained owners can read approved existing data.
8. `ENTITLEMENT-003` passes when retained/unavailable owners cannot use widget or create new metered rows/activity.
9. `ENTITLEMENT-004` passes when verified active/uncanceled state restores eligible activity.
10. `QUOTA-001` passes executable concurrent/edge tests for locked inventory, lead, and AI limits while existing inventory updates remain possible.
11. `SEC-PAY-001` passes isolated ACL/RLS/function tests for owner reads and browser denial.
12. F02-targeted typecheck, lint, unit tests, Python tests, build, and migration evidence are recorded honestly.
13. No Polar write, shared-staging, production, billing-account, legal, or deployment mutation occurs without explicit authorization.

## Risks and External Actions

* Exact Starter/Growth products must be created or corrected in Polar sandbox before live checkout can pass. This is currently an external blocker, not permission to mutate Polar.
* Real payment/webhook/customer-portal validation requires an authorized sandbox transaction.
* The live Supabase connector requires OAuth reauthorization; local representative database validation is mandatory meanwhile.
* F03 and F08 will extend the reusable inventory/widget boundaries without weakening F02 gates.

## Status

STATUS: PRD_READY
