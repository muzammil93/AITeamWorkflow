# QA Report

## Feature ID and Name

`F02 — Plans, Billing, and Entitlements`

## Entry Mode

`QA_FIRST`

## Requirement IDs

`PLAN-001`, `PLAN-002`, `BILLING-001`, `BILLING-002`, `BILLING-003`, `ENTITLEMENT-001`, `ENTITLEMENT-002`, `ENTITLEMENT-003`, `ENTITLEMENT-004`, `QUOTA-001`, `SEC-PAY-001`

## Attempt 1

### Environment

* QA mode: `EXISTING_CODE_BASELINE`
* Product checkpoint: `b48d8bc`
* Product branch: `1.0.0/1.0.0_BackednImplementation_v3`
* Node.js `22.13.1`, pnpm `10.11.1`
* Polar: configured sandbox, read-only product listing
* Shared Supabase metadata: not rechecked because connector OAuth authorization is required
* Shared staging/production: not mutated

### QA Summary

FAIL.

The repository contains a useful partial subscription foundation: the locked plan constants are correct, checkout is server-created for an authenticated owner, the Polar route verifies webhook signatures through `@polar-sh/nextjs`, cancellation can retain access until period end, and lead/AI paths attempt atomic quota consumption.

The implementation is not F02-ready. The configured Polar sandbox does not match the locked product model, payment history is synthesized from subscription state instead of `order.paid`, event deduplication can permanently discard retries, lifecycle coverage is incomplete, checkout-return UI claims activation without authoritative confirmation, access-mode logic is duplicated/incomplete, widget and inventory creation can bypass entitlement/quota enforcement, payment/function privileges are not explicitly restricted, subscription SQL lacks a canonical migration history/final-state gate, and no F02 regression tests exist.

The QA-first baseline failure does not consume a repair cycle.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Evidence |
| --- | --- | --- |
| `PLAN-001` | FAIL | In-code constants and SQL seed use the locked values, but runtime plan/checkout data trusts mutable DB/Polar products. The configured sandbox has a recurring USD 20 “Standard” product with different quotas and no Growth product. |
| `PLAN-002` | FAIL | Billing shows plan cards, usage, and payment rows, but does not clearly render subscription/effective access state or unavailable/retained mode. |
| `BILLING-001` | FAIL | Checkout is authenticated and server-created, but omits stable `external_customer_id`, exposes raw/internal errors, and cannot create the locked Growth checkout from current configuration. |
| `BILLING-002` | FAIL | Signature verification exists, but event rows are inserted before business effects, retry failures become false duplicates, lifecycle events are incomplete, and `order.paid` is ignored. |
| `BILLING-003` | FAIL | Browser query `?success=true` displays “Subscription activated”; `checkout.*` webhook success directly grants plan access instead of waiting for authoritative subscription lifecycle. |
| `ENTITLEMENT-001` | FAIL | Resolver exposes booleans rather than one effective `active` / `retained` / `unavailable` mode; fallback logic is duplicated and `past_due` remains active without a bounded effective period. |
| `ENTITLEMENT-002` | PASS | Owner authentication remains valid and existing profile/billing/inventory/lead surfaces are not globally blocked after entitlement expiry. |
| `ENTITLEMENT-003` | FAIL | AI and lead paths attempt gating, but public widget configuration remains available without entitlement validation and direct/new inventory paths can bypass the preflight. |
| `ENTITLEMENT-004` | FAIL | `created`/`updated` may reactivate, but explicit `active`, `uncanceled`, `past_due`, and `revoked` transitions are not handled. |
| `QUOTA-001` | FAIL | Lead/AI counter updates are conditional, but inventory “reservation” only computes remaining slots and creates no atomic reservation; direct table mutation can bypass quota enforcement. |
| `SEC-PAY-001` | FAIL | RLS policies exist, but payment/event table grants and quota/entitlement function execution are not explicitly restricted; billing event payloads are stored wholesale. |

### Test Cases and Actual Results

* `pnpm exec tsc --noEmit`: PASS.
* `pnpm exec vitest run`: PASS — existing F01 suite only, 8 files / 32 tests.
* F02-targeted ESLint: FAIL — 12 errors, primarily explicit `any`, plus one unused catch variable.
* F02 automated tests discovered: none.
* Canonical F02 migration discovery: FAIL — subscription SQL exists as root-level standalone files rather than one ordered file under `supabase/migrations/`.
* Read-only Polar sandbox product listing:
  * Product `adbd4b92-1362-48fd-ba26-2f173409d9af`: “Standard”, recurring monthly, USD 20, description “Unlimited Inventory Items / 30 leads/month”.
  * Product “Free Forever”: zero-price recurring product with 25 inventory / 3 leads description.
  * No locked USD 19 Starter product.
  * No locked USD 49 Growth product.
* `.env` and `.env.production` both set `POLAR_PRODUCT_IDS={}`; the database seed’s Starter ID points to the mismatched sandbox Standard product and Growth remains a placeholder.

### Findings

#### `F02-QA-001`

* Requirement ID: `PLAN-001`, `BILLING-001`
* Severity: Critical
* State: `OPEN`
* Title: Runtime Polar catalog does not match locked SaleAura plans
* Evidence: Read-only Polar sandbox listing; `lib/config/plans.ts`; `supabase-migration-subscription-modular.sql`; `POLAR_PRODUCT_IDS` configuration.
* Expected: Free trial 100/25/500, Starter USD 19 with 500/150/2000, and Growth USD 49 with unlimited/600/8000 map to real recurring products.
* Actual: Sandbox exposes a USD 20 Standard product with different limits and no Growth product.
* Suggested fix direction: Enforce locked application plan metadata and configure exact sandbox product IDs before checkout acceptance. Polar dashboard mutation requires separate authorization.

#### `F02-QA-002`

* Requirement ID: `BILLING-001`
* Severity: High
* State: `OPEN`
* Title: Checkout contract lacks stable customer reconciliation and safe errors
* Evidence: `app/api/subscription/checkout/route.ts`; `lib/subscription/server.ts`.
* Expected: Authenticated server checkout sends product, `external_customer_id`, email, safe success/return URLs, deterministic metadata, and stable public failures.
* Actual: `external_customer_id` is absent, errors are classified from and returned as raw exception messages, and product mapping can use mismatched DB data.
* Suggested fix direction: Add a typed checkout boundary, exact configured product mapping, stable errors, and external owner identity.

#### `F02-QA-003`

* Requirement ID: `BILLING-002`, `ENTITLEMENT-004`
* Severity: Critical
* State: `OPEN`
* Title: Webhook deduplication can lose retries and lifecycle/payment events are incomplete
* Evidence: `markWebhookSeen`, `processPolarWebhookPayload`, and `upsertPaymentForSubscription` in `lib/subscription/server.ts`.
* Expected: Verified events are claimed/processed transactionally or with recoverable state; duplicates skip only completed work; all approved subscription transitions and `order.paid` are handled.
* Actual: The event is inserted before effects. Any later failure leaves it permanently duplicate. Only created/updated/canceled and checkout events are handled; payment rows are fabricated from subscription state.
* Suggested fix direction: Persist processing status/attempt/error, process retry-safely, cover the explicit lifecycle, and record payments only from idempotent `order.paid`.

#### `F02-QA-004`

* Requirement ID: `BILLING-003`
* Severity: High
* State: `OPEN`
* Title: Checkout return and checkout events overstate or grant activation
* Evidence: `app/billing/BillingPageClient.tsx`; checkout-event branch in `processPolarWebhookPayload`.
* Expected: Return parameters show only pending verification; verified subscription state determines access.
* Actual: `?success=true` displays “Subscription activated”, and a succeeded checkout webhook directly writes an active paid plan.
* Suggested fix direction: Use pending copy, refresh server entitlements, and remove checkout-event access grants.

#### `F02-QA-005`

* Requirement ID: `PLAN-002`, `ENTITLEMENT-001`, `ENTITLEMENT-002`
* Severity: High
* State: `OPEN`
* Title: Effective access mode is not resolved or displayed consistently
* Evidence: SQL `get_user_entitlements`, TypeScript entitlement type, Python fallback resolver, and billing UI.
* Expected: One authoritative `active`, `retained`, or `unavailable` mode with bounded lifecycle semantics and clear owner-facing state.
* Actual: Multiple implementations derive booleans differently, treat `past_due` as active without an effective bound, and the UI does not expose retained/unavailable mode.
* Suggested fix direction: Centralize the resolver contract and make fallbacks fail closed as unavailable.

#### `F02-QA-006`

* Requirement ID: `ENTITLEMENT-003`
* Severity: Critical
* State: `OPEN`
* Title: Expired owners can retain widget bootstrap/config and bypass some new-activity gates
* Evidence: `app/api/widget/config/[user_id]/route.ts`; inventory direct table policies and owner UI paths.
* Expected: Existing owner data remains readable, but widget/public activity and new metered writes are disabled after effective expiry.
* Actual: Widget config uses service role without entitlement validation, and inventory writes are not universally routed through an authoritative quota boundary.
* Suggested fix direction: Add a reusable active-access guard to F02-owned boundaries and expose it for dependent widget/catalog work without implementing F03/F08 scope.

#### `F02-QA-007`

* Requirement ID: `QUOTA-001`
* Severity: Critical
* State: `OPEN`
* Title: Inventory quota is not atomically reserved and quota enforcement is bypassable
* Evidence: `reserve_inventory_slots` SQL, backend fallback, current inventory RLS/browser mutation.
* Expected: Concurrent new-item creation cannot exceed quota; existing-row updates remain allowed.
* Actual: Reservation only counts rows and returns an allowance. Concurrent callers can receive the same capacity, and direct inserts bypass the function.
* Suggested fix direction: Introduce a transactional service-role quota/write boundary or durable reservation model and lock down bypass paths in the owning feature sequence.

#### `F02-QA-008`

* Requirement ID: `SEC-PAY-001`
* Severity: Critical
* State: `OPEN`
* Title: Payment/event grants and entitlement/quota functions are not explicitly restricted
* Evidence: `supabase-schema.sql` and subscription SQL files contain policies but no complete table/function revoke/grant contract.
* Expected: Only verified server billing paths write payments/events; owner payment reads are isolated; internal mutation functions are unavailable to unintended API roles.
* Actual: Intended access depends on ambient default grants and RLS; functions default to public execution; raw provider payloads are persisted.
* Suggested fix direction: Add an additive ACL/RLS/function-hardening migration and validate it in an isolated database.

#### `F02-QA-009`

* Requirement ID: `SEC-PAY-001`
* Severity: High
* State: `OPEN`
* Title: Subscription SQL lacks a canonical migration history and reproducible F02 final state
* Evidence: `supabase-migration-subscription-modular.sql`, cleanup/hotfix/drift files, and `supabase-schema.sql`.
* Expected: One ordered additive F02 migration and reconciled consolidated schema reproduce the intended state.
* Actual: Existing subscription SQL files are outside the canonical migration directory, overlap each other, and have unclear application history.
* Suggested fix direction: Create one canonical additive F02 migration, validate it from representative baseline fixtures, and reconcile the consolidated schema.

#### `F02-QA-010`

* Requirement ID: All F02 requirements
* Severity: High
* State: `OPEN`
* Title: Billing lifecycle, entitlement, quota, and security behavior lacks regression tests
* Evidence: Test discovery finds only F01 tests.
* Expected: Targeted tests cover checkout mapping, stable failures, webhook verification/duplicates/retries, all lifecycle transitions, `order.paid`, access modes, quota races, and ACL/RLS behavior.
* Actual: No F02 automated tests exist; targeted billing lint reports 12 errors.
* Suggested fix direction: Add focused TypeScript, Python, and executable PostgreSQL tests and integrate them into existing commands.

### Security and Ownership Checks

FAIL.

Webhook signature verification is a positive control. It is insufficient while payment/event grants are implicit, internal functions are broadly executable, checkout/lifecycle effects are not authoritative enough, and quota/write bypasses remain.

### Scope Compliance

The existing code does not introduce annual billing, coupons, taxes, team billing, refunds automation, or unsupported currencies. The repair can remain within F02 by creating reusable entitlement/quota boundaries while deferring F03/F08 feature behavior.

### Coverage Limitations

* Supabase live metadata/advisors could not be read because connector OAuth authorization is required.
* No checkout, payment, customer, or subscription was created in Polar.
* The Polar product check was read-only.
* No authorized paid test transaction or real webhook delivery was available.
* These limitations do not erase the deterministic code, schema, and sandbox-catalog failures.

Attempt Result: FAIL

## Attempt 2

### Environment

* QA mode: `POST_IMPLEMENTATION`
* Product checkpoint: `9e0dac6`
* Database state: independently reproducible local migration evidence available
* Polar sandbox: read-only catalog remains unchanged

### QA Summary

FAIL.

The implementation closes the baseline application/database findings or fails safely around the external Polar catalog. One additional billing-integrity defect remains at checkpoint `9e0dac6`: an owner with any active paid subscription is blocked only from checking out the same tier. They can create checkout for the other paid tier, risking two simultaneous recurring subscriptions instead of managing the existing subscription through the customer portal.

This post-implementation code failure consumes repair cycle `1/2`.

The unchanged Polar catalog remains a separate external blocker and does not consume a repair cycle.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Evidence |
| --- | --- | --- |
| `PLAN-001` | BLOCKED_EXTERNAL | Locked application catalog and exact Polar product validation pass; sandbox still lacks exact Starter/Growth products. |
| `PLAN-002` | PASS | Billing overview shows locked plans, lifecycle/effective mode, quotas, and verified payment history. |
| `BILLING-001` | FAIL | New checkout contract is trusted, but an already-active paid owner can start another tier checkout. |
| `BILLING-002` | PASS | Required lifecycle, retry, duplicate, owner/product mapping, and `order.paid` tests pass. |
| `BILLING-003` | PASS | Browser return is pending-only and checkout events do not grant access. |
| `ENTITLEMENT-001` | PASS | Canonical active/retained/unavailable database resolver passes executable tests. |
| `ENTITLEMENT-002` | PASS | Retained existing data and inventory update evidence passes. |
| `ENTITLEMENT-003` | PASS | Widget/new lead/AI/inventory gates pass locally. |
| `ENTITLEMENT-004` | PASS | Active/uncanceled lifecycle restores eligibility through verified state. |
| `QUOTA-001` | PASS | Transactional lead/inventory and locked AI quota evidence passes. |
| `SEC-PAY-001` | PASS | Local ACL/RLS/function execution and unique payment evidence passes. |

### Finding Verification

Baseline findings:

* `F02-QA-001`: `APPLICATION_VERIFIED_EXTERNAL_BLOCKED`
* `F02-QA-002` through `F02-QA-010`: `VERIFIED`

New finding:

#### `F02-QA-011`

* Requirement ID: `BILLING-001`
* Severity: Critical
* State: `OPEN`
* Title: Active paid owner can start a second paid subscription checkout
* Reproduction:
  1. Resolve an owner as active Starter.
  2. Request Growth checkout.
  3. Observe the same-plan-only guard permits checkout creation.
* Expected: Any active paid subscription uses customer portal management; no second recurring checkout is created.
* Actual: Only active same-tier checkout is blocked.
* Evidence: `createSubscriptionCheckout` at product checkpoint `9e0dac6`.
* Suggested fix direction: Centralize an active-paid predicate, block checkout for either paid tier, hide alternate-tier checkout controls, and add regression coverage.

Attempt Result: FAIL

## Status

STATUS: FAIL
