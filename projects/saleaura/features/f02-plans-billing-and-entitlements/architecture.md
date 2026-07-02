# Architecture

## Feature ID and Name

`F02 — Plans, Billing, and Entitlements`

## Architecture Mode

Delta architecture after QA-first baseline failure

## Inputs

* F02 CEO request ending `STATUS: CEO_REQUEST_CREATED`.
* F02 baseline QA report ending `STATUS: FAIL`.
* F02 delta PRD ending `STATUS: PRD_READY`.
* SaleAura V1 master architecture.
* Polar subscription lifecycle/idempotency guidance.
* Integrated F01 authenticated-owner and server-only admin boundaries.

## Design Goals

* Keep prices, quotas, and plan names immutable in application code.
* Treat Polar as lifecycle/payment authority, not plan-copy authority.
* Make checkout and portal owner-authenticated server operations.
* Make verified webhooks retry-safe and side effects idempotent.
* Resolve one effective access mode in the database.
* Enforce quota and retained-access rules at trusted write boundaries.
* Preserve existing owner data and future F03/F08 extensibility.
* Fail closed without converting transient errors into confirmed zero/retained states.

## Component Design

### Locked plans

`lib/config/plans.ts` remains the sole locked plan authority and gains:

* Safe plan catalog DTO construction.
* Expected paid price in cents.
* Strict plan-tier parsing.
* No dependency on mutable `products` rows for price/quota.

`lib/data/plans.ts` and `app/api/public/plans/route.ts` return only the safe catalog. Optional FX estimates may come from server-side FX rows but cannot replace locked USD values.

`lib/config/polar-products.ts` becomes strict:

* Parses `POLAR_PRODUCT_IDS`.
* Accepts only non-empty UUID IDs for `starter` and `growth`.
* Rejects missing, placeholder, free, duplicate, or malformed mappings.
* Provides reverse product-ID-to-tier lookup for verified webhooks.
* Never logs the access token.

### Billing errors

Add `lib/subscription/errors.ts`:

* Stable codes for unauthorized, invalid tier, checkout unavailable, product mismatch, portal unavailable, entitlement unavailable, and persistence failure.
* Public messages contain no Polar/Supabase detail.
* Route handlers use typed errors rather than matching exception strings.

### Polar product validation

Before checkout:

1. Resolve exact configured product ID.
2. Fetch the product through the official server SDK.
3. Require non-archived recurring monthly product.
4. Locate an active fixed USD recurring price equal to the locked cents value.
5. Reject mismatch with stable `CHECKOUT_UNAVAILABLE`.

This prevents an incorrect environment/DB ID from charging an unapproved price.

### Checkout

`createSubscriptionCheckout(planTier)`:

1. Loads authenticated user.
2. Loads only authoritative profile email.
3. Rejects free/current active same-plan checkout.
4. Validates configured Polar product.
5. Calls `POST /v1/checkouts` through SDK with:
   * `products`
   * `externalCustomerId: user.id`
   * `customerEmail`
   * exact `successUrl`
   * exact `returnUrl`
   * metadata `{ userId, planTier }`
6. Verifies returned URL is HTTPS on a Polar-owned checkout host.
7. Returns `{ checkoutUrl }`.

The success URL uses a non-authoritative marker such as `checkout=returned`; it never means activated.

### Customer portal

Add `app/api/subscription/portal/route.ts` and server helper:

1. Authenticate owner.
2. Create Polar customer session by `externalCustomerId: user.id`.
3. Use exact `/billing` return URL.
4. Validate returned portal URL is HTTPS and Polar-owned.
5. Return only `{ portalUrl }`.

### Billing overview

Replace browser table reads with `app/api/subscription/overview/route.ts`:

* Authenticates owner.
* Loads one entitlement row through service role.
* Loads at most 20 exact-owner payment rows with allowlisted columns.
* Returns stable `unavailable` response when either authoritative panel cannot load.

Billing UI:

* Uses locked plan catalog.
* Displays effective mode, lifecycle status, trial/period end, and quotas.
* Displays pending checkout-return copy.
* Refreshes overview after return but never grants access locally.
* Shows “Manage subscription” only when a Polar customer/subscription is present.
* Preserves retryable partial/unavailable states.

## Webhook Design

### Verified payload

Continue using `@polar-sh/nextjs` `Webhooks`, which validates Standard Webhooks headers/signature before `onPayload`.

Type payload as `ReturnType<typeof validateEvent>` from `@polar-sh/sdk/webhooks`; no `any`.

### Event identity and completion

Compute event key as SHA-256 over:

`type + verified timestamp + resource ID`

Algorithm:

1. Query minimal event row by key.
2. If `status = processed`, return duplicate success.
3. Apply idempotent business effect.
4. Upsert minimal event audit row as `processed` with type, resource ID, occurred/processed timestamps, and attempt count.
5. On failure, upsert `failed` with a stable internal error code and increment attempts, then throw so Polar retries.

No complete webhook payload is stored.

Concurrent duplicate effects remain safe:

* Profile lifecycle writes are deterministic exact-owner updates.
* Payments use unique `polar_order_id`.
* Event audit uses unique event key.

### Owner and plan mapping

Owner ID resolution:

* Primary: `data.customer.externalId`.
* Secondary compatibility: `data.metadata.userId`.
* If both exist, they must match.
* Value must be a UUID.

Plan resolution:

* Use `data.productId` or order product ID.
* Reverse-map through configured Starter/Growth Polar IDs.
* Metadata plan tier may be checked for consistency but never grants authority.

Unknown/conflicting mapping fails retryably and does not update access.

### Subscription transitions

For created, updated, active, uncanceled, and past_due:

* Store Polar customer/subscription IDs.
* Store mapped paid plan.
* Store normalized lifecycle status.
* Store verified current period end / effective end.
* Store `cancel_at_period_end`.

For canceled:

* If future effective end exists, keep status `canceled`, plan, and future end.
* Resolver remains active until end.

For revoked:

* Store `revoked`.
* Store effective ended timestamp (or verified event timestamp).
* Keep paid plan label and all business data.
* Resolver returns retained.

Checkout events never change plan/access.

### Payments

Only `order.paid` writes `payments`.

Upsert by unique `polar_order_id`:

* owner ID from verified external identity;
* Polar subscription ID;
* total amount divided from cents;
* lowercase/uppercase normalized currency;
* `succeeded`;
* mapped tier;
* subscription period dates when present;
* invoice number;
* paid/order created timestamp.

## Entitlement Architecture

### Database resolver

Canonical function:

`public.get_user_entitlements(p_user_id uuid)`

Service-role only. It:

* Resets monthly counters if due.
* Loads the owner.
* Applies locked tier limits with SQL `CASE`, not mutable products.
* Counts current inventory.
* Computes paid/trial timing.
* Returns:
  * `access_mode`
  * `access_reason`
  * lifecycle fields
  * active booleans for compatibility
  * locked quota limits/usage/remaining
  * relevant reset/end timestamps
* Returns `unavailable` for unsupported/contradictory state rather than silently falling back to free.

Paid active-like states require a future `subscription_end_date`. Scheduled cancellation is active until that end. Expired/revoked/canceled-without-future-end is retained.

### TypeScript

`UserEntitlements` includes:

* `access_mode: "active" | "retained" | "unavailable"`
* `access_reason`
* `subscription_end_date`
* existing quota fields

All F02 TypeScript gates use this row.

### Python

`backend/services/subscription_service.py` consumes the same RPC contract.

Remove duplicated table-based entitlement fallback. RPC failure becomes `unavailable` and blocks metered activity.

## Quota Architecture

### Lead

Add service-role function:

`public.create_lead_with_quota(p_user_id uuid, p_lead jsonb) returns uuid`

Within one transaction:

1. Lock owner profile.
2. Resolve active access and locked lead limit.
3. Reject retained/unavailable/exhausted.
4. Increment monthly lead usage conditionally.
5. Insert an allowlisted lead row.
6. Return lead ID.

Any insertion failure rolls back counter consumption.

Backend `save_lead` calls this RPC rather than separate consume/insert.

### AI

`consume_ai_response`:

* service-role only;
* locks owner;
* resolves active access under the same transaction;
* conditionally increments below locked limit;
* returns false on retained/unavailable/exhausted.

Python removes direct-table fallback counter updates.

### Inventory

Preflight uses:

`preview_inventory_slots(p_user_id, requested)`

This is advisory and does not reserve.

Actual writes use:

`apply_inventory_batch_with_quota(p_user_id uuid, p_items jsonb) returns jsonb`

Within one transaction:

1. Lock owner profile.
2. Parse an allowlisted current inventory-row shape.
3. Require every incoming `user_id` to equal `p_user_id`.
4. Reject cross-owner conflicting IDs.
5. Count genuinely new IDs.
6. Permit existing-ID updates regardless of exhausted new-item quota.
7. Require active access for any new IDs.
8. Enforce locked inventory limit against current count plus new IDs.
9. Upsert the batch and return saved rows.

Concurrent imports serialize on the owner lock, preventing quota overshoot.

Revoke direct anon/authenticated inventory INSERT. Existing owner SELECT/UPDATE behavior remains until F03 replaces broader inventory policies.

## Widget Gate

`app/api/widget/config/[user_id]/route.ts`:

* Uses the canonical entitlement row before returning customization/defaults.
* Returns a stable inactive/unavailable response when mode is not active.
* Does not implement F08 domain/session redesign.
* Returns only allowlisted customization fields.

This closes the F02 subscription gate while leaving embedding-host authorization to F08.

## Database Migration

Create:

`supabase/migrations/<UTC>_f02_plans_billing_entitlements.sql`

Additive/data-preserving changes:

* Profiles:
  * `polar_subscription_id`
  * lifecycle constraints/indexes where safe
* Payments:
  * `polar_order_id`
  * `invoice_number`
  * unique order constraint/index
* Billing webhook events:
  * processing status
  * resource ID
  * occurred/processed timestamps
  * attempts
  * last stable error code
  * stop storing new payloads; preserve old payload column/data unless safe nulling is explicitly chosen
* Recreate entitlement/quota/write functions with:
  * fixed empty search path;
  * fully qualified objects;
  * service-role-only execution.
* Recreate payment owner SELECT policy.
* Explicit table grants/revokes for payments/events/products/FX/inventory.
* Upsert locked product display rows without treating Polar IDs as application plan authority.

No existing payment/profile/inventory/lead row is deleted.

## ACL Contract

| Object | anon | authenticated | service_role |
| --- | --- | --- | --- |
| payments | none | owner RLS SELECT | read/write |
| billing_webhook_events | none | none | read/write |
| products | active SELECT | active SELECT | read/write |
| fx_rates | SELECT | SELECT | read/write |
| inventory INSERT | denied | denied | allowed through trusted boundary |
| internal entitlement/quota/write functions | denied | denied | execute |

## Testing Strategy

### TypeScript

* Locked plan DTO and product mapping.
* Checkout:
  * unauthenticated;
  * invalid/free tier;
  * missing/mismatched product;
  * exact external ID/metadata/URLs;
  * safe errors.
* Portal authentication and safe URL.
* Webhooks:
  * completed duplicate;
  * failed retry;
  * each subscription lifecycle;
  * scheduled cancellation;
  * revocation;
  * active/uncanceled reactivation;
  * conflicting owner;
  * unknown product;
  * `order.paid` idempotency;
  * checkout events ignored for access.
* Billing return copy never claims activation.
* Widget entitlement gate.

### Python

* RPC result-shape extraction.
* Entitlement unavailable failure.
* Lead/AI/inventory trusted RPC usage with no direct fallback.
* Stable blocked response behavior.

### PostgreSQL

Representative baseline fixtures prove:

* Migration applies cleanly and preserves rows.
* Locked plan resolver values.
* Active trial, expired trial, active paid, scheduled cancellation, revoked, past_due bounds, and invalid/unavailable modes.
* Lead/AI limits cannot overrun.
* Lead insert rolls back counter on error.
* Concurrent/serialized inventory batches cannot exceed the limit.
* Existing inventory update remains allowed at limit/retained mode.
* Owner payment SELECT isolation.
* anon/authenticated payment/event writes denied.
* internal function execution denied to anon/authenticated and succeeds for service role.
* unique Polar order prevents duplicate payment rows.

### Required checks

* `pnpm exec tsc --noEmit`
* `pnpm exec vitest run`
* F02-targeted ESLint
* `pnpm run build`
* Python syntax and targeted tests
* F00 workflow tests
* fresh local PostgreSQL migration/ACL/RLS tests
* migration checksum

## Deployment and External Gates

* No shared-staging or production migration in this task.
* No real charge or subscription creation in this task.
* Polar sandbox products remain an external configuration blocker until separately authorized/corrected.
* After exact products exist, configure product IDs, run read-only product validation, then perform an authorized sandbox checkout/webhook/portal test before claiming shared readiness.

## Recovery

* Before shared application, revise the unapplied migration normally.
* After shared application, use additive forward fixes; never edit applied migration history.
* Webhook retries are safe because effects are idempotent and completion is recorded after effects.
* Preserve later F03/F08/F12 data and schema when extending these boundaries.

## Status

STATUS: ARCHITECTURE_READY
