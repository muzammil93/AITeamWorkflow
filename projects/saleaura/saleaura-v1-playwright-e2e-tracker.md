# SaleAura V1 Staging Playwright E2E Tracker

Use this document with `saleaura-v1-playwright-e2e-plan.md`. Update it during each run; do not rewrite history. Add new run records and findings rather than replacing old evidence.

## Status Values

* `NOT_RUN` - Not started.
* `IN_PROGRESS` - Running now.
* `PASS` - Passed with required evidence.
* `FAIL` - Failed; linked to a finding.
* `BLOCKED` - Cannot run because a prerequisite is missing.
* `PENDING_MANUAL_CONFIRMATION` - Automated portion passed; external receipt/confirmation remains.
* `RETEST_REQUIRED` - A code/configuration fix needs verification.
* `DEFERRED` - Intentionally excluded with approval.

## Active Run Summary

| Field | Value |
| --- | --- |
| Current run ID | `RUN-20260718-001` |
| Target | `STAGING ONLY` |
| Application version/commit | `183fef4` |
| Test plan version | `1.0` |
| Started | `2026-07-18 04:14 PKT` |
| Finished | `-` |
| Operator | `Codex` |
| Result | `IN_PROGRESS` |
| Critical open | `0` |
| High open | `0` |
| Evidence root | `SaleAura-WebApp/test-results/staging-e2e/` |

## Test Register

| Test ID | Persona | Desktop | Mobile | Status | Run ID | Evidence | Finding ID / notes |
| --- | --- | --- | --- | --- | --- | --- | --- |
| E2E-000 | System | Required | - | PASS | RUN-20260718-001 | `SaleAura-WebApp/test-results/staging-e2e/preflight-E2E-000-saved-st-f40f7-n-reaches-the-fresh-profile-desktop-chromium/video.webm` | Fresh owner session reached `/profile`; console/server error attachments empty |
| E2E-001 | Visitor | Required | Required | PASS (desktop, mobile) | RUN-20260718-001 / RUN-20260719-E2E001M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-001-mobile-20260719-001/public-site-E2E-001-visito-00e5f-ite-and-reach-public-routes-mobile-chromium/video.webm` | Public home, pricing, Google sign-in entry, and legal routes passed on desktop and mobile. |
| E2E-002 | OWNER-FREE | Required | Required | PASS (desktop); PASS (mobile visitor subset) | RUN-20260718-001 / RUN-20260719-E2E002M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-002-003-mobile-visitor-20260719-001/auth-E2E-002-Google-sign-i-150d3-fe-protected-route-recovery-mobile-chromium/video.webm` | Mobile Google-only entry, protected-route recovery, and missing-callback handling passed. Incomplete-owner mobile routing remains pending a dedicated QA identity. |
| E2E-003 | OWNER-FREE | Required | - | PASS (desktop); PASS (mobile visitor subset) | RUN-20260718-001 / RUN-20260719-E2E003M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-002-003-mobile-visitor-20260719-001/routing-E2E-003-protected--7b116-gn-in-from-every-owner-page-mobile-chromium/video.webm` | Mobile visitors were returned safely from every protected owner route. Incomplete-owner mobile routing remains pending a dedicated QA identity. |
| E2E-004 | OWNER-FREE | Required | Required | PASS (desktop) | RUN-20260718-001 | `SaleAura-WebApp/test-results/staging-e2e/profile-E2E-004-Owner-comp-f60ae-profile-opens-the-dashboard-desktop-chromium/video.webm` | Missing details were explained; complete Pakistan/Karachi shop profile saved and opened dashboard; mobile remains scheduled in E2E-032 |
| E2E-005 | OWNER-FREE | Required | - | PASS | RUN-20260718-001 | `SaleAura-WebApp/test-results/staging-e2e/profile-E2E-005-Owner-edit-f05c2--logout-locks-the-workspace-desktop-chromium/video.webm` | Valid logo image uploaded; invalid phone was refused; address persisted after refresh; logout returned to sign-in and protected dashboard was blocked |
| E2E-006 | OWNER-FREE | Required | Required | PASS (desktop) | RUN-20260718-001 | `SaleAura-WebApp/test-results/staging-e2e/free-plan-E2E-006-Free-own-bc7f7-SV-is-stopped-before-saving-desktop-chromium/video.webm` | Billing showed Free Trial with a 100-product limit; the 500-row CSV preview showed 100 allowed and 400 over limit before any save; mobile remains scheduled in E2E-032 |
| E2E-007 | OWNER-PAID | Required | - | PASS (Pakistan); BLOCKED (U.S. hCaptcha) | RUN-20260718-F002FIX-010 / RUN-20260718-F003FIX-US-020 | `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-us-retest-20260718-020/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/video.webm` | Pakistan completed checkout, return, webhook, Starter access, and billing history. A clean U.S. run reaches Polar hosted checkout but Stripe's invisible hCaptcha never completes, so Polar emits no `/confirm`. |
| E2E-008 | OWNER-PAID | Required | - | PASS | RUN-20260719-E2E008-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-008-billing-recovery-20260719-001/billing-recovery-E2E-008-a-471f6--only-their-customer-portal-desktop-chromium/video.webm` | Active Starter access remained intact; a second paid checkout returned `ALREADY_SUBSCRIBED`; Manage subscription opened the Polar customer portal without a state change. |
| E2E-009 | OWNER-PAID | Required | - | PASS (free-plan import subset) | RUN-20260719-INVENTORY-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/inventory-full-20260719-002/inventory-Inventory-page-—-53765-e-final-user-visible-result-chromium/video.webm` | Valid CSV import passed and the supplied 500-row catalog showed the correct 100/400 free-plan limit. The paid 500-row save remains pending a new manual Starter sandbox checkout. |
| E2E-010 | OWNER-PAID | Required | - | PASS (mixed-row subset) | RUN-20260719-INVENTORY-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/inventory-full-20260719-002/inventory-Inventory-page-—-68a96-es-and-keeps-valid-CSV-rows-chromium/video.webm` | Mixed valid/error rows saved correctly and the failed-row report was downloadable. |
| E2E-011 | OWNER-PAID | Required | - | PASS (SKU-update subset) | RUN-20260719-INVENTORY-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/inventory-full-20260719-002/inventory-Inventory-page-—-056dc--new-inventory-slots-remain-chromium/video.webm` | Existing SKU update succeeded with no available new inventory slots and did not create a duplicate. |
| E2E-012 | OWNER-PAID | Required | - | NOT_RUN | - | - | - |
| E2E-013 | OWNER-PAID | Required | - | PASS (manual lifecycle subset) | RUN-20260719-INVENTORY-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/inventory-full-20260719-002/inventory-Inventory-page-—-17350-ssages-for-a-manual-product-chromium/video.webm` | Invalid/valid create, edit, archive, reactivate, duplicate handling, filter/sort/pagination, and manual quota enforcement passed. Image/link and zero-stock customer visibility remain pending. |
| E2E-014 | OWNER-PAID | Required | Required | PASS (desktop, mobile) | RUN-20260719-E2E014-001 / RUN-20260719-E2E014M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-014-015-mobile-20260719-002/widget-setup-E2E-014-owner-fc98a-a-temporary-widget-hostname-mobile-chromium/video.webm` | Desktop and mobile rejected malformed hosts, accepted a temporary exact host, showed the install code, and removed the temporary host. |
| E2E-015 | CUSTOMER-SEARCH | Required | Required | PASS (desktop, mobile) | RUN-20260719-E2E015-001 / RUN-20260719-E2E015M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-014-015-mobile-20260719-002/embedded-widget-E2E-015-ap-f8535-ns-and-refreshes-the-widget-mobile-chromium/video.webm` | Desktop and mobile external test-shops loaded the script, opened, closed, reopened, and refreshed the widget. Temporary `127.0.0.1` approval was removed. |
| E2E-016 | CUSTOMER-SEARCH | Required | Required | PASS (desktop, mobile) | RUN-20260719-E2E016-002 / RUN-20260719-E2E016M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-016-customer-search-20260719-007/customer-search-E2E-016-cu-80c49-e-in-stock-catalog-products-desktop-chromium/video.webm`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-016-customer-search-mobile-20260719-003/customer-search-E2E-016-cu-80c49-e-in-stock-catalog-products-mobile-chromium/video.webm` | Real approved external hosts returned the QA active/in-stock CPU and excluded the zero-stock GPU on desktop and mobile. |
| E2E-017 | CUSTOMER-SEARCH | Required | Required | PASS (desktop, mobile) | RUN-20260719-E2E017-001 / RUN-20260719-E2E017M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-017-customer-comparison-20260719-001/customer-comparison-E2E-01-f9ccc-s-and-labels-missing-values-desktop-chromium/video.webm`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-017-customer-comparison-mobile-20260719-001/customer-comparison-E2E-01-f9ccc-s-and-labels-missing-values-mobile-chromium/video.webm` | Real catalog CPU comparison rendered customer-safe facts and labeled the absent socket as `Not available` on desktop and mobile. |
| E2E-018 | CUSTOMER-LANG | Required | Required | PASS (desktop, mobile) | RUN-20260719-E2E018-001 / RUN-20260719-E2E018M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-018-customer-language-20260719-001/customer-language-E2E-018--2047c-y-grounded-in-catalog-facts-desktop-chromium/video.webm`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-018-customer-language-mobile-20260719-001/customer-language-E2E-018--2047c-y-grounded-in-catalog-facts-mobile-chromium/video.webm` | English comparison, Urdu search, and Roman Urdu search remained grounded in the two active QA catalog products on desktop and mobile. |
| E2E-019 | CUSTOMER-BUILD | Required | Required | PASS (desktop, mobile) | RUN-20260719-E2E019-001 / RUN-20260719-E2E019M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-019-full-catalog-builds-desktop-20260719-005/customer-build-E2E-019-com-06bd7--for-each-supported-purpose-desktop-chromium/video.webm`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-019-full-catalog-builds-mobile-20260719-001/customer-build-E2E-019-com-06bd7--for-each-supported-purpose-mobile-chromium/video.webm` | Imported complete CSV: gaming, editing, office, and general-use requests each returned a complete, compatible, under-budget eight-component build. Temporary `127.0.0.1` approval was removed. |
| E2E-020 | CUSTOMER-BUILD | Required | Required | PASS (desktop, mobile) | RUN-20260719-E2E020-001 / RUN-20260719-E2E020M-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-020-unsafe-builds-desktop-20260719-002/customer-build-E2E-020-uns-571b1--instead-of-a-partial-build-desktop-chromium/video.webm`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-020-unsafe-builds-mobile-20260719-002/customer-build-E2E-020-uns-571b1--instead-of-a-partial-build-mobile-chromium/video.webm` | Too-low budget and controlled missing-Cooling states returned actionable no-build guidance without partial cards. The test restored all 20 Cooling products and removed its temporary host. |
| E2E-021 | CUSTOMER-BUILD | Required | Required | NOT_RUN | - | - | - |
| E2E-022 | CUSTOMER-BUILD | Required | - | NOT_RUN | - | - | - |
| E2E-023 | CUSTOMER-LEAD | Required | Required | NOT_RUN | - | - | - |
| E2E-024 | CUSTOMER-LEAD | Required | - | NOT_RUN | - | - | - |
| E2E-025 | CUSTOMER-LEAD | Required | - | NOT_RUN | - | - | Manual receipt required |
| E2E-026 | CUSTOMER-LEAD | Required | - | NOT_RUN | - | - | - |
| E2E-027 | OWNER-PAID | Required | Required | NOT_RUN | - | - | - |
| E2E-028 | OWNER-RETAINED | Required | - | NOT_RUN | - | - | - |
| E2E-029 | OWNER-RETAINED | Required | - | NOT_RUN | - | - | - |
| E2E-030 | OWNER-OTHER | Required | - | NOT_RUN | - | - | - |
| E2E-031 | Customer/system | Required | - | PASS (unapproved-origin subset) | RUN-20260719-E2E031-001 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-031-unapproved-widget-host-20260719-002/embedded-widget-E2E-031-an-6633a--render-the-widget-launcher-desktop-chromium/video.webm` | An unapproved external origin received `403` from bootstrap and rendered no widget launcher. Fake/expired sessions and rate-limit recovery remain pending catalog-backed coverage. |
| E2E-032 | All selected | - | Required | NOT_RUN | - | - | - |

## Run Log

Add one entry per run. Never overwrite an earlier row.

| Run ID | Date/time (Asia/Karachi) | Scope | Browser/device | App commit | Result | Passed | Failed | Blocked | Evidence root | Notes |
| --- | --- | --- | --- | --- | --- | ---: | ---: | ---: | --- | --- |
| RUN-20260718-001 | 2026-07-18 04:14 PKT | E2E-000 to E2E-007 | Desktop Chrome | 183fef4 | FAIL | 10 | 1 | 0 | `SaleAura-WebApp/test-results/staging-e2e/` | E2E-000 to E2E-006 passed with video. E2E-007 entered the hosted Polar sandbox checkout, filled the visible Pakistan billing form, and pressed Subscribe now; the checkout remained open and no order confirmation reached Polar. |
| RUN-20260718-F003FIX-US-020 | 2026-07-18 21:34 PKT | E2E-007 U.S. clean-customer comparison | Desktop Chrome, visible | local changes | BLOCKED | 0 | 0 | 1 | `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-us-retest-20260718-020/` | The dedicated QA profile, its payment rows, and its Polar sandbox customer were cleared first. Checkout creation returned 200; U.S. card/address data was accepted. Trace shows Stripe started an invisible hCaptcha after Subscribe now; it did not complete and Polar sent no `/confirm`. Temporary endpoint `2ab91ef9-433e-4f26-b1d7-cd47fed315b8` and tunnel were removed. |
| RUN-20260719-F002MANUAL-001 | 2026-07-19 03:12 PKT | Completed manual Starter checkout reconciliation | Desktop Chrome, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-002-manual-checkout-reconcile-20260719-002/` | Polar already showed the user’s active Starter subscription and paid order, but there was no webhook delivery because its endpoint was disabled. Visiting `/billing?checkout=returned` verified the current signed-in user against Polar and displayed active Starter access plus the paid invoice. |
| RUN-20260719-F002MANUAL-002 | 2026-07-19 03:23 PKT | Returned-checkout reconciliation reliability | Desktop Chrome, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-002-manual-checkout-reconcile-20260719-004/` | The return page retried provider-authoritative reconciliation before dropping `checkout=returned`; no QA reset, Polar customer deletion, checkout, or webhook endpoint was used. The visible E2E-007 recovery check showed active Starter access and billing history. |
| RUN-20260719-E2E008-001 | 2026-07-19 03:34 PKT | E2E-008 checkout and billing recovery | Desktop Chrome, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-008-billing-recovery-20260719-001/` | Active Starter owner kept access; a request for a second paid checkout returned `409 ALREADY_SUBSCRIBED`; the owner-scoped Manage subscription control opened the Polar sandbox customer portal. No subscription cancellation or test-data reset occurred. |
| RUN-20260719-E2E014-001 | 2026-07-19 03:56 PKT | E2E-014 widget owner setup | Desktop Chrome, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-014-widget-setup-20260719-003/` | The app rejected a hostname with protocol and path, accepted an exact temporary `qa-widget-*.example.test` hostname, exposed the installation script, then removed the temporary hostname. The test also clears only leftover hosts in that reserved test namespace. |
| RUN-20260719-E2E015-001 | 2026-07-19 05:06 PKT | E2E-015 external embedded widget | Desktop Chrome, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-015-embedded-widget-20260719-004/` | A separate temporary local test-shop origin received the approved-host bootstrap token, loaded the iframe, opened, closed, reopened, and refreshed the widget. Its temporary allowed host was removed in cleanup. |
| RUN-20260719-E2E014M-001 / RUN-20260719-E2E015M-001 | 2026-07-19 05:25 PKT | E2E-014 and E2E-015 mobile regression | iPhone 13 viewport, Chromium, visible | local changes | PASS | 2 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-014-015-mobile-20260719-002/` | Mobile widget setup and the approved external iframe flow both passed. Temporary widget hosts were removed after each test. |
| RUN-20260719-E2E001M-001 | 2026-07-19 05:26 PKT | E2E-001 mobile public-site regression | iPhone 13 viewport, Chromium, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-001-mobile-20260719-001/` | Public home, pricing, Google sign-in entry, and the legal routes remained usable at the mobile viewport. |
| RUN-20260719-E2E002M-001 / RUN-20260719-E2E003M-001 | 2026-07-19 05:44 PKT | E2E-002 and E2E-003 mobile visitor regression | iPhone 13 viewport, Chromium, visible | local changes | PASS | 3 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-002-003-mobile-visitor-20260719-001/` | Google-only sign-in, missing-callback recovery, and visitor redirects from protected pages passed. No owner profile or inventory data was modified. |
| RUN-20260719-E2E031-001 | 2026-07-19 05:47 PKT | E2E-031 unapproved widget origin | Desktop Chrome, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-031-unapproved-widget-host-20260719-002/` | A separate unapproved local host requested the real embed script. Bootstrap returned `403` and the launcher was not rendered; no session, message, or owner data was created. |
| RUN-20260719-QARESET-001 | 2026-07-19 05:49 PKT | Current-account QA reset | Staging sandbox | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/playwright-report/staging-e2e/` | With explicit user authorization, deleted only the current QA account's Polar sandbox customer and SaleAura payment rows, then reset its billing profile to Free Trial. No production provider or database was used. |
| RUN-20260719-INVENTORY-001 | 2026-07-19 06:03 PKT | Inventory browser QA: E2E-009 to E2E-013 subsets | Desktop Chrome, visible | local changes | PASS | 12 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/inventory-full-20260719-002/` | All 12 serial inventory checks passed: valid/mixed imports, quota boundaries, failed-row downloads, SKU update, preflight failure recovery, manual CRUD, duplicate SKU, table controls, Sheets error handling, and manual quota enforcement. The account ends with QA-seeded catalog data and a Free Trial entitlement. |
| RUN-20260719-E2E016-001 | 2026-07-19 06:26 PKT | E2E-016 customer catalog search | Desktop Chrome, visible | local changes | PASS | 1 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-016-customer-search-20260719-006/` | The real external iframe waited for its signed session, returned the active in-stock QA CPU, and returned no product card for the zero-stock QA GPU. The temporary `127.0.0.1` host was removed in cleanup. |
| RUN-20260719-E2E016-002 / RUN-20260719-E2E016M-001 | 2026-07-19 06:29 PKT | E2E-016 final desktop and mobile customer catalog search | Desktop Chrome and iPhone 13 viewport, visible | local changes | PASS | 2 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-016-customer-search-20260719-007/`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-016-customer-search-mobile-20260719-003/` | Both final recordings used the same repaired backend: active/in-stock CPU returned, zero-stock GPU excluded, and temporary host removed after every run. |
| RUN-20260719-E2E017-001 / RUN-20260719-E2E017M-001 | 2026-07-19 06:31 PKT | E2E-017 customer comparison | Desktop Chrome and iPhone 13 viewport, visible | local changes | PASS | 2 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-017-customer-comparison-20260719-001/`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-017-customer-comparison-mobile-20260719-001/` | A real approved external host compared two active catalog CPUs. The UI displayed catalog facts and the intentionally absent socket as `Not available`; temporary host cleanup passed. |
| RUN-20260719-E2E018-001 / RUN-20260719-E2E018M-001 | 2026-07-19 06:36 PKT | E2E-018 multilingual customer grounding | Desktop Chrome and iPhone 13 viewport, visible | local changes | PASS | 2 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-018-customer-language-20260719-001/`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-018-customer-language-mobile-20260719-001/` | One real external widget session completed an English comparison, Urdu product search, and Roman Urdu product search. Each structured result contained only the seeded active catalog products; temporary host cleanup passed. |
| RUN-20260719-E2E019-001 / RUN-20260719-E2E019M-001 | 2026-07-19 07:14 PKT | E2E-019 full-catalog customer builds | Desktop Chrome and iPhone 13 viewport, visible | local changes | PASS | 2 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-019-full-catalog-builds-desktop-20260719-005/`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-019-full-catalog-builds-mobile-20260719-001/` | The app imported the supplied 500-row CSV through Inventory. Gaming, editing, office, and general-use requests each returned a complete eight-component verified build within PKR 900,000. Final database check: 500 total, 500 active/in stock; temporary widget host cleanup passed. |
| RUN-20260719-E2E020-001 / RUN-20260719-E2E020M-001 | 2026-07-19 14:40 PKT | E2E-020 safe no-build outcomes | Desktop Chrome and iPhone 13 viewport, visible | local changes | PASS | 2 | 0 | 0 | `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-020-unsafe-builds-desktop-20260719-002/`; `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-020-unsafe-builds-mobile-20260719-002/` | A PKR 1,000 request returned actionable no-build guidance. After temporarily disabling Cooling, the widget identified Cooling as missing and returned no partial build. Cleanup restored all 20 Cooling products and removed the temporary host. |
| - | - | - | - | - | NOT_RUN | 0 | 0 | 0 | - | - |

## Finding Register

Create a finding immediately when a test fails, a result is misleading, an assertion cannot be trusted, or a manual notification does not arrive.

| Finding ID | Status | Severity | First seen | Feature | Test ID | Short title | Owner | Fix branch/commit | Re-test ID | Evidence |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| FINDING-001 | VERIFIED | High | 2026-07-18 04:48 PKT | F02 Billing | E2E-007 | Sandbox checkout return address points to another local app | Codex | local staging configuration | E2E-007 | RUN-20260718-F002FIX-010 returned to `http://localhost:5001/billing?checkout=returned` and completed E2E-007 |
| FINDING-002 | VERIFIED | Critical | 2026-07-18 05:04 PKT | F02 Billing | E2E-007 | Polar sandbox webhook is disabled | Software team | staging schema repair | E2E-007 | RUN-20260718-F002FIX-010: real Polar webhook deliveries returned 200; profile became active Starter and billing history received the paid order |
| FINDING-003 | WONT_FIX_APPROVED | Critical | 2026-07-18 05:41 PKT | F02 Billing | E2E-007 | Sandbox checkout remains open after Subscribe now | Codex | local staging E2E harness | Manual staging smoke test | Pakistan is proven by RUN-20260718-F002FIX-010. Clean U.S. run RUN-20260718-F003FIX-US-020 shows Polar/Stripe hCaptcha blocks automated confirmation before `/confirm`. Manual sandbox checkout and returned-checkout reconciliation are verified; user approved excluding provider confirmation from automation. |
| FINDING-004 | VERIFIED | High | 2026-07-19 04:58 PKT | F08 Widget | E2E-015 | Approved external widget host could not obtain a session | Codex | local changes | E2E-015 | RUN-20260719-E2E015-001 proves the separate approved host loads, opens, closes, reopens, and refreshes the real iframe. |
| FINDING-005 | VERIFIED | High | 2026-07-19 06:12 PKT | F08 Widget | E2E-016 | Embedded chat rejected its own approved host session | Codex | local changes | E2E-016 | RUN-20260719-E2E016-002 / RUN-20260719-E2E016M-001 prove a signed session can send a real external customer search and return only active, in-stock products on desktop and mobile. |
| FINDING-006 | VERIFIED | High | 2026-07-19 07:08 PKT | F04/F10 Customer builds | E2E-019 | Complete catalog build request could stop before generating a build | Codex | local changes | E2E-019 | RUN-20260719-E2E019-001 / RUN-20260719-E2E019M-001 prove full catalog builds for gaming, editing, office, and general use on desktop and mobile. |
| FINDING-007 | VERIFIED | Medium | 2026-07-19 14:37 PKT | F10 Customer builds | E2E-020 | No-build outcome did not explain the next action | Codex | local changes | E2E-020 | RUN-20260719-E2E020-001 / RUN-20260719-E2E020M-001 prove the actionable low-budget and missing-category responses on desktop and mobile. |

Finding statuses: `OPEN`, `READY_FOR_FIX`, `FIX_IN_PROGRESS`, `READY_FOR_RETEST`, `VERIFIED`, `WONT_FIX_APPROVED`, `DUPLICATE`.

### FINDING-001 - Sandbox checkout return address points to another local app

Status: VERIFIED
Severity: High
Feature: F02 Billing
Affected test: E2E-007
First seen: 2026-07-18 04:48 Asia/Karachi
Run ID: RUN-20260718-001
Browser/device: Desktop Chrome
Test account/persona: OWNER-FREE becoming OWNER-PAID

What the user tried:
1. A completed SaleAura owner is ready to choose the Starter plan in the sandbox.
2. Before creating a chargeable sandbox checkout, the test checked the configured origin used to build Polar success and return URLs.

Expected result:
After checkout, the owner returns to the SaleAura staging billing page, where verified subscription processing can be observed.

Actual result:
The configured application origin resolves to `localhost:5000`, while this SaleAura app is running at `localhost:5001`; port 5000 belongs to a different local app. `createSubscriptionCheckout` uses that configured origin for both Polar return URLs.

Impact:
An owner can complete sandbox checkout but be returned to the wrong app instead of SaleAura billing. The paid-plan confirmation, webhook/entitlement check, and all dependent paid journeys cannot be trusted.

Evidence:
- Code: `SaleAura-WebApp/lib/subscription/server.ts:212` and `SaleAura-WebApp/lib/subscription/server.ts:213`
- Safe staging configuration check: `NEXT_PUBLIC_APP_URL` host is `localhost:5000` (value redacted)
- Existing recorded prerequisite: `SaleAura-WebApp/test-results/staging-e2e/free-plan-E2E-006-Free-own-bc7f7-SV-is-stopped-before-saving-desktop-chromium/video.webm`

Fix request:
Configure the staging SaleAura application origin to the actual SaleAura staging host, then restart the staging app and verify both Polar success and return URLs use that same host.

Re-test scope:
E2E-006, E2E-007, E2E-008, then the paid inventory, widget, and customer journeys in their original order.

### FINDING-002 - Polar sandbox webhook is disabled

Status: VERIFIED
Severity: Critical
Feature: F02 Billing
Affected test: E2E-007
First seen: 2026-07-18 05:04 Asia/Karachi
Run ID: RUN-20260718-001
Browser/device: Desktop Chrome
Test account/persona: OWNER-FREE becoming OWNER-PAID

What the user tried:
1. The local checkout return address was corrected and the SaleAura staging app restarted.
2. Before charging the sandbox card, the test checked whether Polar can send the verified subscription events that grant access.

Expected result:
An enabled Polar sandbox webhook sends subscription and paid-order events to a reachable SaleAura staging endpoint.

Actual result:
The only configured Polar sandbox webhook endpoint was disabled. Its configured path also differed from the current app webhook route (`/api/subscription/webhooks/polar`). The existing public staging host returned `404` for both that path and its older configured path.

Impact:
A customer may complete payment but remain on the free plan because SaleAura never receives the provider event. This blocks all paid-plan testing and would prevent a paid customer from getting access.

Evidence:
- Safe provider check: one sandbox webhook endpoint is configured but `enabled` is false
- Provider events configured: subscription lifecycle and checkout events; `order.paid` is not included
- Current application handler: `SaleAura-WebApp/app/api/subscription/webhooks/polar/route.ts`
- Public staging route check: both candidate webhook paths return `404`

Temporary test attempt:
A temporary public tunnel reached the local staging server. The existing Polar sandbox endpoint was enabled and pointed at its exact `/api/subscription/webhooks/polar` path, with the required subscription and `order.paid` events. The configured signing secret matched the staging app. FINDING-003 prevented any payment event from being created, so the temporary endpoint was disabled after the test. A permanent reachable staging endpoint remains required.

Latest evidence after FINDING-003 repair:
- Run: `RUN-20260718-F003FIX-007` at 2026-07-18 06:28 PKT
- Recording: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-retest-20260718-007/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/video.webm`
- Trace: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-retest-20260718-007/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/trace.zip`
- Polar checkout `88c9d51c-b1fd-49b2-8fd8-6a9eca901c35` succeeded and returned to SaleAura.
- Polar subscription `4ae7538e-c3ac-4bf8-9e18-f5394aad533c` is active; order `f598f665-d5b5-45d0-b316-80afb9776c8f` is paid.
- SaleAura staging profile `b2396c93-de50-407c-93cd-289fd06f608f` still has `plan_tier = free`, no `polar_customer_id`, no `polar_subscription_id`, and no payment rows. This confirms the remaining blocker is webhook delivery, not hosted checkout confirmation.

Re-test scope:
E2E-007 through E2E-008 before any paid inventory, widget, or customer tests continue.

Latest repair update:
- Root cause: staging schema drift. `billing_webhook_events` lacked the audit columns used by the handler, causing `42703` on `status`; the older `payments_polar_order_id_unique` partial index could not satisfy the `onConflict: "polar_order_id"` upsert target, causing `42P10` on `order.paid`.
- Changed files: `SaleAura-WebApp/supabase/migrations/20260718113000_f02_billing_webhook_event_audit_columns.sql` (applied to staging as `20260718113943`), `SaleAura-WebApp/supabase/migrations/20260718120000_f02_payment_order_id_upsert_index.sql` (queued source migration), and `SaleAura-WebApp/lib/subscription/server.ts` (safe compatibility fallback for the older partial-index schema).
- Verification: `RUN-20260718-F002FIX-010` passed the full visible Pakistan E2E-007 recording. Polar confirmed the checkout, SaleAura returned to `/billing?checkout=returned`, the temporary reachable webhook returned `200`, and the QA profile was `starter` / `active` with paid billing rows.
- The temporary sandbox webhook endpoints, ngrok tunnel, local server, and temporary signing secret were removed after validation. No provider webhook remains pointed at a local tunnel.

### FINDING-003 - Sandbox checkout remains open after Subscribe now

Status: WONT_FIX_APPROVED
Severity: Critical
Feature: F02 Billing
Affected test: E2E-007
First seen: 2026-07-18 05:41 Asia/Karachi
Run ID: RUN-20260718-001
Browser/device: Desktop Chrome, visible browser
Test account/persona: OWNER-FREE becoming OWNER-PAID

What the user tried:
1. A completed SaleAura owner with a Pakistan shop opened Billing and selected Starter.
2. The recorded sandbox checkout showed the Starter amount and the secure card form.
3. The test entered the sandbox card, a future expiry, security code, owner name, and a billing country, then pressed the visible Subscribe now button.

Expected result:
The sandbox creates the Starter subscription, redirects the owner back to SaleAura billing, and triggers the enabled webhook.

Actual result:
The checkout stayed open for more than 90 seconds after Subscribe now. The provider did not send an order confirmation request and its safe status check still reported the checkout as `open`, with no subscription or customer created.

Impact:
Owners cannot complete the paid-plan journey in staging. The same result occurred with Pakistan and U.S. billing countries in a visible browser. SaleAura does not receive a payment event, so paid access, billing history, and every dependent owner/customer journey must remain paused.

Evidence:
- Video: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-pakistan-checkout-visible-browser/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/video.webm`
- Screenshot: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-pakistan-checkout-visible-browser/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/test-failed-1.png`
- Trace: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-pakistan-checkout-visible-browser/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/trace.zip`
- Comparison video: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-us-billing-comparison/video.webm`
- Comparison screenshot: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-us-billing-comparison/test-failed-1.png`
- Comparison trace: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-us-billing-comparison/trace.zip`
- Safe provider check: status `open`; no subscription and no customer on the latest checkout

Suspected area (optional, not a diagnosis):
Polar sandbox checkout confirmation. The same result occurred with Pakistan and U.S. billing countries in a visible browser, so it is not limited to a country choice or hidden test-browser mode.

Root cause:
The reusable staging owner email already had an active Polar sandbox Starter subscription under an older SaleAura metadata user id, so new checkouts for the current owner showed Polar's duplicate active-subscription warning and never reached confirmation. After isolating the sandbox billing email, the test then exposed a second timing issue: billing-country selection sends a Polar checkout `PATCH`, and pressing Subscribe before that update completes returns `409 CheckoutLocked`. The repaired E2E harness now uses a deliverable Gmail plus-address for each staging run and waits for the Polar checkout `PATCH` before waiting for the `/confirm` request.

Repair:
- Added `SaleAura-WebApp/tests/e2e/support/staging-billing.ts` to reset only the dedicated staging QA profile's billing-facing fields to free trial and assign a unique deliverable Polar sandbox email. It does not create subscriptions, payments, or paid access.
- Updated `SaleAura-WebApp/tests/e2e/paid-plan.spec.ts` to call the staging billing prep, wait for Polar's checkout update `PATCH`, and assert the explicit `/confirm` request.

Repair evidence:
- Run: `RUN-20260718-F003FIX-007` at 2026-07-18 06:28 PKT
- Recording: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-retest-20260718-007/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/video.webm`
- Screenshot: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-retest-20260718-007/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/test-failed-1.png`
- Trace: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-retest-20260718-007/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/trace.zip`
- Polar checkout `88c9d51c-b1fd-49b2-8fd8-6a9eca901c35`: `succeeded`, success URL `http://localhost:5001/billing?checkout=returned`.
- Polar customer `6133f1af-a73b-4f14-9f58-630e5253eac2`: `external_id = b2396c93-de50-407c-93cd-289fd06f608f`.
- Polar subscription `4ae7538e-c3ac-4bf8-9e18-f5394aad533c`: `active`.
- Polar order `f598f665-d5b5-45d0-b316-80afb9776c8f`: `paid`.
- E2E-007 now fails only after return while polling SaleAura for active Starter access, matching FINDING-002.

Latest repair update:
- Pakistan proof: `RUN-20260718-F002FIX-010` passed the full visible E2E-007 flow. Recording: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-002-retest-20260718-010/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/video.webm`.
- The E2E harness now isolates each run with a deliverable Gmail plus-address, waits for Polar checkout updates, waits for card-form readiness, waits for client-side billing data after return, and uses complete U.S. address details including state.
- Remaining U.S. evidence: `RUN-20260718-F003FIX-US-015`, recording and trace under `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-us-retest-20260718-015/`. Polar left the valid U.S. checkout open and did not emit `/confirm`, even after the country and state `PATCH` requests completed. No U.S. subscription or paid access was created by that failed attempt.

Latest investigation, repair, and evidence:
- Root cause of the remaining automated U.S. block: the clean `RUN-20260718-F003FIX-US-020` trace shows Stripe creating an invisible hCaptcha challenge after Subscribe now. The challenge does not complete in the Playwright browser, so Polar does not send `POST /v1/checkouts/client/.../confirm`; the checkout remains open. This is a provider anti-bot challenge, not a country-specific address error or SaleAura webhook failure. CAPTCHA completion must be performed by a human and is not bypassed by this test.
- Reset repair: `SaleAura-WebApp/tests/e2e/support/staging-billing.ts` now requires `E2E_POLAR_RESET_SANDBOX=1`, deletes only the dedicated QA user's Polar **sandbox** customer by external ID (which revokes its sandbox subscriptions), deletes only that user's `payments` rows, and resets only that profile to free trial. It never creates paid access or touches production/shared customers.
- Payment idempotency repair: `SaleAura-WebApp/supabase/migrations/20260718120000_f02_payment_order_id_upsert_index.sql` was applied to staging after a duplicate preflight; `payments_polar_order_id_unique` is now a non-partial unique index. `SaleAura-WebApp/lib/subscription/server.ts` retains a safe `42P10` compatibility fallback and treats the expected concurrent duplicate-key insert as already recorded. `tests/f02/webhook.test.ts` adds concurrent order delivery coverage.
- Test-launch repair: quoted `POLAR_PRODUCT_IDS` in `SaleAura-WebApp/.env` and `SaleAura-WebApp/.env.staging` preserves the JSON mapping when the documented `zsh` staging command sources those files; without quotes checkout creation returned `503` because no Starter product could be resolved.
- Authentication resilience: `SaleAura-WebApp/tests/e2e/paid-plan.spec.ts` returns to Billing after the normal Google sign-in redirect when a recorded QA session has expired.
- Verification: `pnpm exec tsc --noEmit` passed; `pnpm exec vitest run tests/f02/webhook.test.ts tests/f02/migration-security.test.ts` passed 17 tests. The temporary Polar sandbox endpoint and ngrok tunnel were deleted after the blocked run. No provider webhook points at a local tunnel.
- Evidence: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-003-us-retest-20260718-020/paid-plan-E2E-007-Owner-up-a636a-owner-active-Starter-access-desktop-chromium/{video.webm,test-failed-1.png,trace.zip}`.

Manual-completion recovery:
- A user completed the real Polar sandbox Starter checkout manually on 2026-07-19. Polar reported subscription `4a1db16c-29dc-46e7-8bb2-8678c5119789` as active and order `d946596e-2839-4ef3-a6ec-0d1125e712e1` as paid, but SaleAura remained free because the only sandbox endpoint was disabled and had no delivery records to redeliver.
- Repair: `SaleAura-WebApp/app/api/subscription/reconcile/route.ts`, `SaleAura-WebApp/lib/subscription/server.ts`, and `SaleAura-WebApp/app/billing/BillingPageClient.tsx` now reconcile only an authenticated user who returns with `?checkout=returned`. The server confirms an active configured Polar subscription for that user’s external ID and confirms its paid order before reusing the normal webhook store to write entitlement and payment history. It cannot grant access without those Polar records and does not create a checkout, subscription, or payment itself.
- Verification: `RUN-20260719-F002MANUAL-001` passed the visible `E2E-007 recovery` check. Staging profile is `starter` / `active` with the actual Polar customer and subscription IDs, and the billing history contains the $19 `LOGICODE360-SANDBOX-0011` order. Evidence: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-002-manual-checkout-reconcile-20260719-002/paid-plan-E2E-007-recovery-36288-verified-Polar-subscription-desktop-chromium/video.webm`.
- Reliability hardening: the return page now retries verified Polar reconciliation for six seconds before removing `checkout=returned`, so an immediately returning paid owner is not shown as free merely because Polar has not exposed the subscription/order yet. The E2E auth recovery waits for the auth page to finish clearing its session error before starting Google OAuth. `RUN-20260719-F002MANUAL-002` passed visibly with active Starter access and billing history: `SaleAura-WebApp/test-results/staging-e2e-evidence/finding-002-manual-checkout-reconcile-20260719-004/paid-plan-E2E-007-recovery-36288-verified-Polar-subscription-desktop-chromium/video.webm`.
- Cleanup: temporary endpoint `98ea2ae2-5907-4ad2-948f-7fa3cf0b5588` and its ngrok tunnel were deleted immediately after verification. Automated U.S. confirmation remains blocked by provider hCaptcha, so a complete unattended U.S. E2E-007 recording is intentionally not required.
- Approval: on 2026-07-19, the product owner approved excluding the provider-hosted final confirmation from automation. This is not a SaleAura code defect: hCaptcha runs inside Stripe/Polar before `/confirm`. Keep automated coverage for SaleAura checkout creation and the provider-authoritative returned-checkout reconciliation; perform the final sandbox card confirmation as a manual staging smoke test. No CAPTCHA bypass or direct access grant is permitted.

Fix request:
Do not automate provider-hosted payment confirmation. Perform a manual Starter sandbox smoke payment when needed, then verify return to SaleAura, provider-authoritative reconciliation, Starter access, and billing history.

Re-test scope:
Automated: checkout-session creation and returned-checkout reconciliation. Manual: the final hosted card confirmation, followed by the same Starter access and billing-history checks.

### FINDING-004 - Approved external widget host could not obtain a session

Status: VERIFIED
Severity: High
Feature: F08 Widget
Affected test: E2E-015
First seen: 2026-07-19 04:58 Asia/Karachi
Run ID: RUN-20260719-E2E015-001
Browser/device: Desktop Chrome, visible browser
Test account/persona: OWNER-PAID / CUSTOMER-SEARCH

Root cause:
`public/embed.js` loaded the widget iframe from the SaleAura app origin, and the iframe itself requested `/api/widget/bootstrap`. The request therefore carried the app origin instead of the customer's approved host origin. The bootstrap endpoint did not provide cross-origin CORS handling, so a real external host could not obtain a signed bootstrap token and the widget launcher never rendered.

Repair:
- `public/embed.js` now requests the bootstrap token from the host page, then sends it to the trusted SaleAura iframe only after the iframe signals readiness.
- `components/chat/ChatWidget.tsx` receives that signed token from its parent and creates the widget session from it; it no longer tries to bootstrap from the iframe origin.
- `app/api/widget/bootstrap/route.ts` now handles CORS preflight and returns the allowed request origin only after its normal exact-host allowlist validation.
- `app/api/widget/config/[user_id]/route.ts` exposes public widget configuration with CORS for the external embed.
- Added focused F08 regression tests and a recorded real cross-origin `E2E-015` test. The E2E test starts a temporary local test-shop origin and removes its temporary `127.0.0.1` approval in cleanup.

Verification:
- `pnpm exec tsc --noEmit` passed.
- `pnpm exec vitest run tests/f08` passed: 4 files, 7 tests.
- `RUN-20260719-E2E015-001` passed visibly. Evidence: `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-015-embedded-widget-20260719-004/embedded-widget-E2E-015-ap-f8535-ns-and-refreshes-the-widget-desktop-chromium/video.webm`.

### FINDING-005 - Embedded chat rejected its own approved host session

Status: VERIFIED
Severity: High
Feature: F08 Widget
Affected test: E2E-016
First seen: 2026-07-19 06:12 Asia/Karachi
Run ID: RUN-20260719-E2E016-001
Browser/device: Desktop Chrome, visible browser
Test account/persona: CUSTOMER-SEARCH

Root cause:
After the approved host created the iframe, its chat request originated from the SaleAura iframe origin. `app/api/chat/route.ts` incorrectly compared that iframe request origin with the external hostname recorded in the signed widget session, so valid embedded messages could be rejected even though bootstrap had already bound the session to the approved host.

Repair:
- `app/api/chat/route.ts` now validates the short-lived, hash-matched widget session and expiry without comparing it to the iframe's SaleAura origin. The signed bootstrap remains the origin-binding control.
- `components/chat/ChatWidget.tsx` keeps both the message field and Send control disabled until its signed widget session is ready, so an early customer message cannot be silently refused during bootstrap.
- `backend/engine.py` retries a no-match product search without only the model-inferred brand, while preserving the customer's words, category, and stated price ceiling. This prevents an inconsistent extracted brand from hiding an exact catalog match without surfacing unrelated categories.
- `tests/e2e/customer-search.spec.ts` records the real external customer flow: seed only the dedicated QA catalog, search for an active in-stock product, and prove that a zero-stock product is excluded.
- `tests/test_engine_search_fallback.py` covers the narrowed retrieval fallback with plain Python assertions.
- `tests/f08/embed-bootstrap-flow.test.ts` covers the origin-validation regression.

Verification:
- `pnpm exec tsc --noEmit` passed.
- `pnpm exec vitest run tests/f08` passed: 4 files, 8 tests.
- `RUN-20260719-E2E016-002` and `RUN-20260719-E2E016M-001` passed visibly on desktop and mobile. Evidence: `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-016-customer-search-20260719-007/customer-search-E2E-016-cu-80c49-e-in-stock-catalog-products-desktop-chromium/video.webm` and `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-016-customer-search-mobile-20260719-003/customer-search-E2E-016-cu-80c49-e-in-stock-catalog-products-mobile-chromium/video.webm`.
- The first E2E-016 attempt also revealed a stale local Python backend process that returned no products despite the active seeded row. Restarting that staging-only process against the same staging database resolved the mismatch; direct current-code retrieval and the final browser recording both returned the seeded CPU.

### FINDING-006 - Complete catalog build request could stop before generating a build

Status: VERIFIED
Severity: High
Feature: F04/F10 Customer builds
Affected test: E2E-019
First seen: 2026-07-19 07:08 Asia/Karachi
Run ID: RUN-20260719-E2E019-001
Browser/device: Desktop Chrome, visible browser
Test account/persona: OWNER-PAID / CUSTOMER-BUILD

What the user tried:
1. The owner imported the supplied `ProductListing - 500.csv` through the Inventory page while on Starter.
2. An external customer opened the approved embedded widget and asked for a gaming PC within PKR 900,000.

Expected result:
The widget should generate a complete, compatible, in-stock build using the supplied catalog. CPU/GPU brand preferences are optional, so their absence must not stop a budgeted build request.

Actual result:
The supplied data initially had build-readiness gaps: RAM capacity appeared only in descriptions, eight AIO cooler rows lacked a required internal cooler-height value, and four synthetic CPU/GPU rows had no verified performance reference. After those catalog/validator repairs, the first real widget request still returned the plain message `Do you have any preferences for CPU or GPU brand?` because the LLM marked optional preferences as required clarification. No build card was returned.

Impact:
Customers with a clear budget and purpose could be blocked before receiving a build recommendation. This prevents the primary build-generation workflow despite a complete paid catalog.

Repair:
- Repaired the supplied CSV without changing its 500-row total or category coverage: populated the missing AIO cooler-height values and replaced the four synthetic CPU/GPU names with products already present in SaleAura's verified performance reference catalog.
- `backend/services/compatibility_validator.py` now reads RAM capacity from the imported description when it is not present in the name.
- `backend/engine.py` now routes any budgeted build request to the safe default build generator even when the LLM asks only for optional brand preferences.
- Added `tests/test_f04_inventory_eligibility.py` coverage for RAM capacity in descriptions and `tests/test_engine_build_clarification.py` coverage for the optional-brand clarification regression.
- Added the recorded `tests/e2e/customer-build.spec.ts` E2E-019 flow and registered it in both staging Playwright configurations. It preserves the imported catalog and removes its temporary approved widget host in cleanup.

Verification:
- The complete CSV was imported through the real Inventory UI: `SaleAura-WebApp/test-results/staging-e2e-evidence/full-build-catalog-import-20260719-005/`.
- Focused Python checks passed: `PYTHONPATH=. venv/bin/python tests/test_engine_build_clarification.py`, `tests/test_engine_search_fallback.py`, and `tests/test_f04_inventory_eligibility.py`.
- `RUN-20260719-E2E019-001` passed visibly on desktop and `RUN-20260719-E2E019M-001` passed visibly on the iPhone 13 viewport. Each run requested gaming, editing, office, and general-use builds. Every returned build had CPU, GPU, Motherboard, RAM, Storage, PSU, Case, and Cooling; was within PKR 900,000; and was marked fully compatible.
- Final staging check: 500 total inventory products, all 500 active and in stock; category counts are CPU 70, GPU 80, Motherboard 80, RAM 80, Storage 80, PSU 50, Case 40, and Cooling 20. No temporary widget host remained.

Evidence:
- Desktop video: `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-019-full-catalog-builds-desktop-20260719-005/customer-build-E2E-019-com-06bd7--for-each-supported-purpose-desktop-chromium/video.webm`.
- Mobile video: `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-019-full-catalog-builds-mobile-20260719-001/customer-build-E2E-019-com-06bd7--for-each-supported-purpose-mobile-chromium/video.webm`.

### FINDING-007 - No-build outcome did not explain the next action

Status: VERIFIED
Severity: Medium
Feature: F10 Customer builds
Affected test: E2E-020
First seen: 2026-07-19 14:37 Asia/Karachi
Run ID: RUN-20260719-E2E020-001
Browser/device: Desktop Chrome, visible browser
Test account/persona: CUSTOMER-BUILD

Root cause:
When the verified build generator returned `no_compatible_full_build`, `backend/engine.py` passed through the generic inventory message. It correctly withheld a partial build, but it did not tell the customer to increase the budget or change purpose.

Repair and verification:
- `backend/engine.py` now maps that safe no-build code to clear next-step guidance.
- `tests/test_engine_build_clarification.py` covers the message; the focused Python test passed.
- E2E-020 passed visibly on desktop and mobile with a PKR 1,000 budget and a controlled missing-Cooling state. Both responses returned no build cards; the test restored the full 500-row catalog and removed its temporary host.
- Evidence: `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-020-unsafe-builds-desktop-20260719-002/customer-build-E2E-020-uns-571b1--instead-of-a-partial-build-desktop-chromium/video.webm` and `SaleAura-WebApp/test-results/staging-e2e-evidence/e2e-020-unsafe-builds-mobile-20260719-002/customer-build-E2E-020-uns-571b1--instead-of-a-partial-build-mobile-chromium/video.webm`.

## Developer Handoff Template

Copy this block for each new finding. Keep it factual and reproducible.

```md
### FINDING-XXX - [short factual title]

Status: OPEN
Severity: Critical | High | Medium | Low
Feature: FXX
Affected test: E2E-XXX
First seen: YYYY-MM-DD HH:MM Asia/Karachi
Run ID: RUN-XXX
Browser/device: Desktop Chrome | Mobile Chrome
Test account/persona: OWNER-FREE | OWNER-PAID | OWNER-RETAINED | OWNER-OTHER | CUSTOMER-XXX

What the user tried:
1. [starting page and known state]
2. [exact visible action]
3. [next exact visible action]

Expected result:
[What a real owner/customer should see or be able to complete.]

Actual result:
[What happened, including visible wording and whether data was saved/changed.]

Impact:
[Who is blocked or harmed, and why the severity is appropriate.]

Evidence:
- Video: [relative artifact path]
- Screenshot: [relative artifact path]
- Trace: [relative artifact path, if applicable]
- Browser/network log: [relative artifact path]
- Safe staging record/check: [redacted ID, count, or status only]

Suspected area (optional, not a diagnosis):
[Route/page/component/API name if the evidence points to one.]

Fix request:
[The observable behavior that must work after the fix.]

Re-test scope:
[Original E2E test plus directly affected prerequisite/consumer tests.]
```

## Re-test Log

Use after the software team marks a finding ready. A finding is not closed merely because a developer says it is fixed.

| Finding ID | Fix reference | Re-test date | Tests run | Result | Evidence | Closure decision |
| --- | --- | --- | --- | --- | --- | --- |
| - | - | - | - | - | - | - |

Re-test rule:

1. Reset only the dedicated affected test data.
2. Re-run the original failing test from its real starting point.
3. Re-run its upstream prerequisite and downstream customer/owner consumer tests listed in the finding.
4. Save a new video and logs; never replace the original failure evidence.
5. Mark `VERIFIED` only when the expected result and regression checks pass.

## Manual Notification Confirmation Log

| Run ID | Lead/test ID | Email received | WhatsApp received | Confirmed at | Message/context correct | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| - | E2E-025 | PENDING | PENDING | - | - | - |

## End-of-Run Summary Template

```md
### RUN-XXX Summary

Target: Staging only
Application version/commit: [value]
Plan version: 1.0
Browsers: [Desktop Chrome / Mobile Chrome]
Scope: [test IDs]

Result: PASS | FAIL | BLOCKED | PENDING_MANUAL_CONFIRMATION

Counts:
- Passed: [n]
- Failed: [n]
- Blocked: [n]
- Re-test required: [n]
- Pending manual notification confirmation: [n]

Open findings:
- [FINDING-XXX - severity - title]

Evidence root: [relative artifact directory]

Decision:
[State whether the next suite may run, whether developer work is required, or why the run is blocked.]
```
