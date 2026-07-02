# Implementation Report

## Feature ID and Name

`F02 — Plans, Billing, and Entitlements`

## Execution Mode

`INITIAL_IMPLEMENTATION` after QA-first baseline failure

## Requirement IDs

`PLAN-001`, `PLAN-002`, `BILLING-001`, `BILLING-002`, `BILLING-003`, `ENTITLEMENT-001`, `ENTITLEMENT-002`, `ENTITLEMENT-003`, `ENTITLEMENT-004`, `QUOTA-001`, `SEC-PAY-001`

## PRD and Architecture References

* F02 PRD — `STATUS: PRD_READY`
* F02 architecture — `STATUS: ARCHITECTURE_READY`
* Baseline QA report — `STATUS: FAIL`
* SaleAura V1 Release Plan v1.0
* Polar subscription lifecycle/idempotency guidance

## Attempt 1

### Repair Count

`0/2`

The QA-first baseline failure is not a repair attempt.

### Summary

Implemented the approved local F02 delta:

* Made the locked Free, Starter, and Growth catalog authoritative in application code.
* Removed mutable database plan rows as runtime price/quota authority.
* Added strict configured Polar product mapping and live product validation before checkout.
* Added authenticated checkout identity, deterministic metadata, exact success/return URLs, and stable public errors.
* Added authenticated Polar customer-portal session creation.
* Reworked webhook handling for retryable completion, all required subscription transitions, exact owner/product mapping, and `order.paid` payment history.
* Removed checkout-event access grants and activation claims from browser return state.
* Added canonical `active`, `retained`, and `unavailable` entitlement modes.
* Added owner billing overview with status, access mode, quota usage, and verified payment history.
* Added retained/inactive widget gating.
* Replaced Python table fallbacks with trusted entitlement/quota RPCs.
* Added transactional lead quota+insert and atomic inventory batch quota+upsert.
* Hardened payment/event/table/function ACLs through one additive migration.
* Reconciled the consolidated schema.
* Added 30 TypeScript F02 tests, six Python F02 tests, and executable PostgreSQL fixtures.

The configured Polar sandbox remains intentionally unchanged. Checkout now fails safely because the sandbox has an incorrect USD 20 Standard product and no Growth product.

### Product Files Changed

Application boundaries:

* `app/api/public/plans/route.ts`
* `app/api/subscription/checkout/route.ts`
* `app/api/subscription/entitlements/route.ts`
* `app/api/subscription/overview/route.ts`
* `app/api/subscription/portal/route.ts`
* `app/api/subscription/upload-preflight/route.ts`
* `app/api/widget/config/[user_id]/route.ts`
* `app/billing/BillingPageClient.tsx`
* `app/billing/page.tsx`
* `app/dashboard/page.tsx`
* `app/page.tsx`

Subscription modules:

* `lib/config/plans.ts`
* `lib/config/polar-products.ts`
* `lib/data/plans.ts`
* `lib/subscription/errors.ts`
* `lib/subscription/product.ts`
* `lib/subscription/server.ts`
* `lib/subscription/types.ts`
* `lib/subscription/webhook.ts`
* `lib/types/database.ts`

Backend:

* `backend/api.py`
* `backend/services/subscription_service.py`

Database:

* `supabase/migrations/20260702140000_f02_plans_billing_entitlements.sql`
* `supabase-schema.sql`
* `supabase/tests/f02_local_baseline.sql`
* `supabase/tests/f02_local_verify.sql`

Tests/configuration:

* `package.json`
* Seven files under `tests/f02/`
* `tests/test_f02_subscription_service.py`

### Checkout and Portal

Checkout now:

* requires an authenticated owner;
* accepts Starter/Growth only;
* requires distinct UUID product mappings for both paid tiers;
* reads the mapped product through the Polar server SDK;
* requires non-archived monthly recurring USD fixed price of exactly 1,900 or 4,900 cents;
* sends authenticated owner ID as `externalCustomerId` and metadata `userId`;
* sends authenticated profile email;
* uses exact application success and return URLs;
* validates returned HTTPS Polar URLs;
* returns stable masked failures.

Portal sessions use the authenticated owner external ID and return only a validated HTTPS Polar portal URL.

### Webhook Lifecycle

The official `@polar-sh/nextjs` adapter continues to verify signatures.

Verified payload processing now:

* creates a deterministic SHA-256 event key from type, resource, and verified timestamp;
* skips completed duplicates;
* records completion only after business effects;
* records failed attempts without suppressing Polar retry;
* keeps profile/payment effects idempotent;
* resolves owner from `customer.externalId` plus matching metadata;
* resolves tier only from configured product ID;
* handles created, updated, active, canceled, uncanceled, past_due, and revoked;
* retains scheduled cancellation until future period end;
* preserves plan/data identity after revocation;
* ignores checkout events for access;
* records payments only from `order.paid`, unique by `polar_order_id`;
* stores minimal event audit metadata and no new full payload.

### Entitlement and Quota Changes

`get_user_entitlements` now returns:

* `active`, `retained`, or `unavailable`;
* stable access reason;
* verified lifecycle/end fields;
* locked quotas;
* usage and remaining values;
* Polar customer/subscription linkage.

Paid active-like states require a future verified period end. Scheduled cancellation remains active until that end. Expired trials and effective cancellation/revocation become retained.

Quota boundaries:

* AI consumption locks the owner and increments conditionally.
* Lead quota consumption and lead insertion occur in one transaction.
* Inventory batch writes lock the owner, count genuinely new IDs, preserve existing-row updates, and enforce the locked limit atomically.
* Direct browser inventory and lead inserts are revoked.
* Python direct-table entitlement/counter fallbacks were removed.

### Database / Migration

Migration:

`supabase/migrations/20260702140000_f02_plans_billing_entitlements.sql`

SHA-256:

`76763892d3478fa557525295ae5fe0217da34b7393b7cd5828d28829d2604fcc`

Database state:

`LOCAL_VALIDATED`

Validated repeatedly on fresh PostgreSQL `16.14` databases:

* migration applies cleanly;
* migration reapplication is idempotent;
* locked plan display rows overwrite incorrect price/quota copies while preserving existing Polar IDs on conflict;
* active/retained/unavailable modes pass;
* scheduled cancellation retains access;
* revocation retains data;
* unknown plans fail closed;
* lead/AI quotas stop at limits;
* failed lead insertion rolls back counter consumption;
* inventory accepts the final slot and atomically rejects overrun;
* retained owners can update existing inventory but cannot add rows;
* duplicate Polar order IDs fail;
* legacy profiles/payments/event payloads are preserved;
* owner payment RLS works;
* anon/authenticated payment/event writes fail with `42501`;
* internal function execution is denied to browser roles and allowed to service role;
* reconciled consolidated F02 function SQL parses successfully.

No migration was applied to shared staging or production.

### Tests and Checks

| Command / procedure | Result |
| --- | --- |
| `pnpm exec tsc --noEmit` | PASS |
| `pnpm exec vitest run` | PASS — 15 files / 62 tests |
| F02 tests | PASS — 30 TypeScript tests |
| Targeted changed-file ESLint | PASS — 0 errors, 3 existing image warnings |
| `pnpm run build` | PASS — 33 routes/pages; existing warnings and skipped embedded gates remain |
| Python syntax check | PASS — 18 files |
| Python unit discovery | PASS — 15 tests, including 6 F02 tests |
| Workflow dry-run | PASS — 12 checks |
| Fresh local migration/ACL/quota verification | PASS |
| Migration repeat application | PASS |
| Consolidated F02 function parse | PASS |
| `git diff --check` | PASS |

### Finding Resolutions

* `F02-QA-001`: `APPLICATION_FIXED_EXTERNAL_BLOCKED`
  * Locked catalog and product verification prevent incorrect charges. Exact sandbox Starter/Growth products still require separate external authorization/configuration.
* `F02-QA-002`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-003`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-004`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-005`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-006`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-007`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-008`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-009`: `FIXED_PENDING_VERIFICATION`
* `F02-QA-010`: `FIXED_PENDING_VERIFICATION`

### Git Checkpoint

* Product base: `b48d8bc`
* Product branch: `feature/f02-plans-billing-entitlements`
* Feature checkpoint: `9e0dac6`
* Working tree after checkpoint: clean
* Remote push: not performed

Safe reversal:

* Revert checkpoint `9e0dac6` rather than resetting.
* If the migration is later applied to a shared database, use reviewed additive forward fixes rather than editing migration history.

### External Action Required

The code must not be configured to the existing USD 20 Standard product.

Before a live sandbox checkout can pass:

1. Create or correct exact monthly USD 19 Starter and USD 49 Growth Polar sandbox products.
2. Configure their IDs in `POLAR_PRODUCT_IDS`.
3. Run an authorized sandbox checkout, `order.paid`, lifecycle, cancellation/uncancel/revoke, and portal test.

No Polar product/customer/order/subscription mutation was performed.

Attempt Result: IMPLEMENTED

## Status

STATUS: IMPLEMENTATION_COMPLETE
