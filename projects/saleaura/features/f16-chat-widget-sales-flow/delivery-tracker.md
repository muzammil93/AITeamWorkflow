# F16 Delivery Tracker — Chat Widget Sales Flow

## Control

This is the feature-level delivery tracker. It complements, and does not replace, the authoritative release state and staging Playwright tracker.

Current stage: `IMPLEMENTATION_COMPLETE — STAGING_QA_IN_PROGRESS`

Feature rule: every F16 workstream requires focused automated coverage and recorded staging Playwright evidence on desktop and mobile before QA can mark it passed. Unit/contract checks support, but never replace, Playwright.

## Workflow Gate

| Stage | Owner | Status | Required handoff |
| --- | --- | --- | --- |
| CEO request | CEO | COMPLETE | `ceo-request.md` |
| Existing-code QA baseline | QA | COMPLETE — FAIL | `qa-report.md` findings `F16-QA-001`–`F16-QA-008` |
| Product requirements | Product Manager | COMPLETE | `prd.md` requirements `CART-001`–`CART-014` |
| Architecture | Architect | COMPLETE | `architecture.md` |
| Implementation | Developer | COMPLETE | `implementation-report.md`, focused tests, migration evidence |
| Feature QA | QA | IN_PROGRESS — PARTIAL DESKTOP/MOBILE PASS | recorded real-staging Playwright desktop/mobile evidence |
| Review | Reviewer | NOT_STARTED | `review-report.md` |
| Final report | Orchestrator | NOT_STARTED | final status only after QA PASS and review APPROVED |

## Delivery Matrix

| Workstream | Requirements / findings | Implementation | Automated tests | Playwright desktop | Playwright mobile | QA | Review | Final gate |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Live greeting and truthful product-card currency/availability | CART-001, CART-002; F16-QA-001, F16-QA-002 | COMPLETE | PASS | PARTIAL PASS | PARTIAL PASS | IN PROGRESS | PENDING | PASS required |
| Product offer actions and secure cart state | CART-003–005; F16-QA-003, F16-QA-004 | COMPLETE | PASS | PARTIAL PASS — session/forgery/expiry | PARTIAL PASS — session/forgery/expiry | IN PROGRESS | PENDING | PASS required |
| Editable quantities and cart totals | CART-003, CART-012 | COMPLETE | PASS | PARTIAL PASS | PARTIAL PASS | IN PROGRESS | PENDING | PASS required |
| Build generation to individual cart products | CART-011; F16-QA-007 | COMPLETE | PASS | PASS | PASS | IN PROGRESS | PENDING | PASS required |
| Build modification and explicit cart separation | CART-011; F16-QA-008 | COMPLETE | PASS | PASS | PASS | IN PROGRESS | PENDING | PASS required |
| Final-cart buying intent and initial lead | CART-006–008; F16-QA-005 | COMPLETE | PASS | PARTIAL PASS | PARTIAL PASS | IN PROGRESS | PENDING | PASS required |
| Post-lead request versions and updated notification | CART-013 | COMPLETE | PASS | PASS — persistence | PASS — persistence | IN PROGRESS | PENDING | PASS required |
| Owner notification cart content and Dashboard lead details | CART-014; F16-QA-005 | COMPLETE | PASS | REQUIRED | REQUIRED | PENDING | PENDING | PASS required |
| Security, entitlement, owner/session, and regression coverage | CART-004, CART-008–010 | COMPLETE | PASS | PARTIAL PASS | PARTIAL PASS | IN PROGRESS | PENDING | PASS required |

## Required Playwright Completion Record

* `E2E-033` — Product cart, quantities, final-cart `I want to buy`, validation, and initial lead.
* `E2E-034` — Invalid quantity, forged/replayed/expired action, owner/session isolation, cancellation, save failure, duplicate, and notification-failure preservation.
* `E2E-035` — Verified-build component expansion, build-modification/cart separation, already-in-build notice, post-lead update request, owner notification, and Dashboard details.
* `E2E-032` — Responsive regression covering the F16 customer journey.

All runs use the authorized staging Supabase project through MCP and dedicated test data. No local/Flask/mock database, sandbox database, production database, or payment-provider action is valid evidence.

## Explicit Exclusions

No customer checkout, payment collection, order, stock reservation/decrement, lead-time stock revalidation, fulfilment, shipping, customer account, or live internet product-research work is allowed in F16.

STATUS: DELIVERY_TRACKER_READY
