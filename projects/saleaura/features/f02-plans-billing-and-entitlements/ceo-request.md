# CEO Request

Begin `F02 — Plans, Billing, and Entitlements` under SaleAura V1 Release Plan version `1.0`.

## Execution Mode

`QA_FIRST`

Validate the existing plan display, Polar checkout/webhook lifecycle, payment history, entitlement resolution, retained-access behavior, quota enforcement, and billing database-security implementation before authorizing code changes.

If existing behavior passes, route it through existing-code review without Developer involvement. If baseline QA fails, create a delta PRD and architecture limited to the verified gaps, then implement, retest, and review them through the bounded-repair workflow.

## Authorized Requirements

* `PLAN-001`: Preserve locked Free, Starter, and Growth prices and quotas.
* `PLAN-002`: Show current plan, usage, subscription state, and payment history.
* `BILLING-001`: Create checkout through trusted Polar server behavior.
* `BILLING-002`: Verify and deduplicate billing webhook processing.
* `BILLING-003`: Prevent unverified browser responses from granting access.
* `ENTITLEMENT-001`: Resolve active, retained-access, and unavailable modes consistently.
* `ENTITLEMENT-002`: Keep approved existing owner data accessible after expiry/cancellation.
* `ENTITLEMENT-003`: Disable widget and new metered activity after effective expiry/cancellation.
* `ENTITLEMENT-004`: Restore eligible activity after verified reactivation.
* `QUOTA-001`: Enforce inventory, lead, and AI quotas atomically and consistently.
* `SEC-PAY-001`: Remove unrestricted payment writes and protect billing event data/functions.

## Constraints

* Preserve Polar as the V1 paid subscription provider.
* Use `order.paid` as the authoritative payment-success event.
* Do not grant access from checkout-return parameters or unverified browser state.
* Do not revoke retained access merely because cancellation was scheduled before the paid period ends.
* Preserve approved owner access to existing data while disabling new metered activity after effective expiry.
* Do not add annual billing, coupons, taxes, team billing, manual invoices, refunds automation, or multiple currencies.
* Do not change F03+ catalog, widget, chat, lead, dashboard, legal, or deployment scope except where F02 must expose a reusable entitlement/quota boundary for dependent work.
* Do not mutate Polar dashboard configuration, shared staging, production, billing accounts, or deployment systems without explicit authorization.
* Use additive migrations only when baseline QA proves F02 database/security gaps and validate them through the F00 safety gate.
* Preserve integrated F00/F01 at product commit `b48d8bc`.

## Requested Outcome

Deliver evidence-backed F02 verification or the smallest approved delta needed to make plans, billing, entitlements, quotas, and payment security ready for dependent feature work and the M1 milestone gate.

STATUS: CEO_REQUEST_CREATED
