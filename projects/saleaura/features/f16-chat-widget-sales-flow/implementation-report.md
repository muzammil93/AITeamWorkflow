# Implementation Report — F16 Chat Widget Sales Flow

## Feature ID and Name

`F16 — Chat Widget Sales Flow`

## Execution Mode

`INITIAL_IMPLEMENTATION`

## Requirement IDs

`CART-001` through `CART-014`

## PRD and Architecture References

* `prd.md` — approved cart-to-lead inquiry scope.
* `architecture.md` — owner/session-bound cart and trusted server-side snapshots.
* `qa-report.md` — baseline findings `F16-QA-001` through `F16-QA-008`.

## Attempt 1

### Repair Count

`0/2`

### Summary

Implemented the F16 cart-to-lead inquiry flow. Product actions now use short-lived, server-stored offer tokens; cart actions derive owner and session from the signed anonymous widget session. The browser cannot set product identity, owner, price, or an unbounded quantity.

The live widget now renders the saved greeting, presents offered products without inventing stock counts, supports cart review and editable quantities, and creates/updates an existing lead only through the final-cart actions. Cart changes neither reserve/decrement stock nor create a checkout/order/payment action.

### Files Changed

* Product commits `672fca6` and `58b5135` in `SaleAura-WebApp/`.
* `app/api/widget/cart/route.ts`
* `lib/widget/cart.ts`
* `components/chat/ChatWidget.tsx`
* `components/chat/cards/CartPanel.tsx`
* `components/chat/cards/ProductCard.tsx`
* `backend/api.py`, `backend/engine.py`, `backend/schema.py`, and `backend/services/customer_response.py`
* `app/dashboard/page.tsx`
* F16 migration and focused test files.

### Code Changes

* Added opaque owner/session-bound product offers and a bounded, server-owned cart state.
* Added add, quantity, remove, clear, and protected latest-build expansion commands.
* Added greeting rendering, truthful availability language, owner currency, cart UI, final-cart intent, and unsent-cart update state.
* Added cart snapshots/request versions to lead context; initial and updated notifications include cart lines; Dashboard exposes lead details.
* Kept build cards as chat recommendations and expands a selected trusted build only into individual cart rows. Later build changes never mutate the cart automatically.

### Database / Migration Changes

`20260726120000_f16_cart_sales_flow.sql` adds only `widget_sessions.cart_state jsonb` with an object constraint.

Read-only staging inspection on 2026-07-26 confirms that `widget_sessions.cart_state` exists with the expected JSON-object constraint and RLS remains enabled. The staging migration history records the same named F16 migration as version `20260726015509`, while the product repository contains version `20260726120000`. The schema matches, but the migration-version provenance must be reconciled by the Orchestrator before final release evidence is claimed.

### Tests and Checks

Passed:

* `pnpm vitest run tests/f16 tests/f08 tests/f09` — 15 tests passed.
* `pnpm vitest run tests/f03/leads-rls.test.ts tests/f12/migration-lead-idempotency.test.ts tests/f13/dashboard-analytics.test.ts` — 4 tests passed.
* `pnpm exec tsc --noEmit` — passed.
* `python3 scripts/check_python_syntax.py` — 38 files passed.
* `git diff --check` — passed before each product commit.

Known unrelated baseline failure:

* `venv/bin/python -m unittest tests/test_f12_lead_consent.py` has one failure. `_normalize_lead_form_submission` emits `consent_given: false` when consent was not supplied, although the pre-existing test expects the key to be absent. The implementation is identical before and after the F16 commits; this is not an F16 repair and is routed for F12/F15 reconciliation.

Required before QA handoff:

* Execute and record `E2E-033`, `E2E-034`, `E2E-035`, and the F16 portion of `E2E-032` against authorized dedicated staging data on desktop and mobile.
* Refresh the dedicated Playwright owner storage state. The 2026-07-26 `E2E-000` preflight reached the local staging-connected application but redirected to `/auth`; the saved `tests/e2e/qa-storage-state.json` session has expired. No owner or customer data was mutated by this preflight attempt.

### Security Notes

* Raw inventory IDs are removed from public responses and cart responses.
* Expired/replayed offer actions and invalid/expired widget sessions are rejected.
* Cart price, currency, product data, build components, and lead context are generated server-side.
* Cart state is owner/session-scoped and capped to 24 lines with quantities 1–99.
* No inventory stock, payment, order, or fulfilment mutation is included.

### Finding Resolutions

Implementation addresses `F16-QA-001` through `F16-QA-008`; verification remains QA-owned and is pending required staging evidence.

### Git Checkpoint

* `672fca6 feat(widget): add cart-to-lead sales flow`
* `58b5135 fix(widget): complete cart lead safeguards`

Generated Python bytecode changes are intentionally uncommitted.

### Assumptions

* The existing F08 signed widget session and F12 lead persistence boundaries remain authoritative.
* A product quantity is considered confidently parsed only when the customer message contains an explicit bounded count such as `2x` or `3 units`; otherwise it defaults to one.

### Known Limitations

* No production migration, deployment, billing, checkout, or provider action was performed.
* The isolated local staging-connected backend/frontend now run on ports 8001/5002. A fresh in-app-browser owner session verified the saved greeting in the public embedded widget on 2026-07-26; the temporary `localhost` allowed-host entry was removed immediately afterward. The browser's current iframe input control cannot deliver a customer message through automation, and its owner session cannot be exported as the Playwright storage state. The required E2E records remain pending a refreshed `qa-storage-state.json` or an equivalent approved Playwright session.

### Blockers

* Reconcile the F16 staging migration version mismatch before treating migration evidence as release-ready.
* Provide a runnable authorized staging browser/service environment to execute the mandatory E2E evidence.

Attempt Result: IMPLEMENTATION_COMPLETE_STAGING_QA_PENDING

## Attempt 2 — Staging Browser Verification

### Repair Count

`1/2`

### Summary

The CEO completed Google sign-in in a separate visible Chrome profile opened at
`http://localhost:5001/auth`. Playwright captured that authenticated context to
`tests/e2e/qa-storage-state.json`, and `E2E-000` staging preflight passed.

Commit `8c6c9e3` adds non-destructive F16 staging Playwright coverage and fixes
two defects found during the run:

* Large build carts could grow beyond the widget viewport and make the composer
  and lead actions unreachable. The cart is now height-bounded and scrollable.
* The post-lead cart refresh could race with a shopper's next quantity update
  and overwrite the newer UI state. Lead/update refreshes are now serialized
  while cart actions remain disabled.

The staging lead path also exposed a pre-existing database function reference to
`public.uuid_generate_v4()`. Migration
`20260729170000_fix_lead_uuid_generator.sql` replaces it with
`gen_random_uuid()` while preserving quota, consent, idempotency, and
owner-scoping behavior. Supabase MCP applied it to staging as migration version
`20260729115510`.

### Recorded Evidence

Passed on the final code:

* Desktop `customer-cart.spec.ts` — 2/2 passed in 1.2 minutes.
* Mobile `customer-cart.spec.ts` — 2/2 passed in 1.4 minutes.
* `E2E-033` evidence: valid offered-product add, quantity update, invalid
  quantity rejection, forged offer rejection, cross-session replay rejection,
  and expired offer rejection.
* `E2E-035` evidence: trusted eight-component build expansion, later-build/cart
  separation, consented lead persistence, quantity change, and same-lead
  request-version update.
* Supabase MCP read-back found six isolated `qa-f16-cart-*` staging leads and six
  request-version updates from the focused and final verification runs.
* `pnpm vitest run tests/f12/migration-lead-idempotency.test.ts tests/f16` —
  8/8 passed.
* `pnpm exec tsc --noEmit` and `git diff --check` — passed.

### Remaining QA Scope

The recorded tests materially advance `E2E-033`, `E2E-034`, `E2E-035`, and
mobile `E2E-032`, but do not yet satisfy every acceptance branch. Remaining
evidence includes:

* CPU + keyboard + monitor/LCD multi-item/remove/exact-total coverage using
  dedicated staging fixtures; the current 500-row build catalog has no keyboard
  or monitor category.
* Cross-owner isolation with a second authorized staging owner.
* Cancelled lead, duplicate submission, quota-limited, forced cart-save failure,
  and notification-failure preservation.
* Automated owner notification-content and Dashboard lead-details assertions.
* Broader F08–F13 regression runs and independent QA/reviewer sign-off.
* Reconciliation of the existing F16 migration filename/version provenance
  difference (`20260726120000` in source versus `20260726015509` in staging).

Attempt Result: IMPLEMENTATION_COMPLETE_STAGING_QA_PARTIAL

## Status

STATUS: IMPLEMENTATION_REPORT_READY
