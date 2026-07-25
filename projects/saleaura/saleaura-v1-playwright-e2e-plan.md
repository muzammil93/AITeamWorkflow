# SaleAura V1 Staging Playwright End-to-End Test Plan

## Control Metadata

Plan ID: `SALEAURA-E2E-STAGING-001`

Version: `1.2`

Status: `APPROVED_FOR_IMPLEMENTATION_AND_QA - F07_INVENTORY_REPAIR_PENDING`

Environment: Staging application, staging Supabase, and Polar sandbox only.

Production: Explicitly out of scope until separately authorized.

Scope: F01-F14, including the approved F07 Google Sheets inventory follow-up.

Purpose: Validate the complete experience of a PC-component shop owner and that shop's customers. The browser suite must prove the visible result, the correct owner-scoped result in staging data where appropriate, and safe recovery when something fails.

## Operating Rules

* Test only dedicated staging accounts and dedicated test customer data. Never use a real customer account or production service.
* A browser test represents one real user journey. It must begin from a known state, state the persona, and clean up only the data it created.
* Keep browser work in the order in this document. Later journeys consume the account, inventory, widget, chat, and lead data created by earlier journeys.
* Use real staging integrations for the normal owner, Polar-sandbox payment, widget, chat, lead, and notification paths. Use a controlled staging failure only for a failure path that cannot safely be induced with a real provider.
* Database-backed test proof uses the connected authorized staging Supabase project through MCP and dedicated test data. Flask, local, mock, and sandbox databases do not count as database readiness evidence.
* Each feature run includes normal journeys, valid boundary cases, relevant invalid/failure/cancelled/unauthorized/quota cases, and regression cases for affected shared behavior.
* Do not put passwords, session tokens, service keys, private email addresses, phone numbers, payment details, or raw provider responses in videos, traces, reports, or source control.
* Google login is a one-time manual checkpoint. The tester signs in to the dedicated Google account when prompted; Playwright stores only the resulting test-session state outside the repository.
* F07 Sheet changes are made through the dedicated Google Sheet in Playwright, then verified through SaleAura in Playwright. The F07 suite does not use direct database calls as test proof.
* Google-managed products are changed or removed in Google Sheets and then synced. Direct Edit, Archive, Delete, and bulk Delete are limited to Manual and CSV products.
* Payment testing uses Polar sandbox and its approved test payment method. It must never charge a real card.
* Email and WhatsApp delivery have two evidence levels: automated staging request/result evidence, then manual receipt confirmation from the designated test inbox and phone.

## Personas and Test Data

| ID | Persona | Starting state | Purpose |
| --- | --- | --- | --- |
| `OWNER-FREE` | Newly completed owner on Free | Empty catalog, active free access | Onboarding, free limits, profile, protected routes |
| `OWNER-PAID` | Newly completed owner on Starter | Empty catalog, active paid access | Paid checkout, 500-row catalog, widget, dashboard |
| `OWNER-SHEET` | Completed owner on Starter | Dedicated 500-product Google Sheet with stable product IDs | Google Sheet connect, sync, quota, removal, and source guidance |
| `OWNER-RETAINED` | Previously paid owner after sandbox cancellation/expiry | Existing catalog, chats, and leads | Retained access and reactivation |
| `OWNER-OTHER` | Separate completed shop owner | Separate catalog and widget | Owner/data isolation |
| `CUSTOMER-SEARCH` | Anonymous shopper | New browser/session | Search, no-result, product cards, comparison |
| `CUSTOMER-BUILD` | Anonymous shopper | New browser/session | Build creation and modification |
| `CUSTOMER-LEAD` | Anonymous shopper | New browser/session | Lead capture and notifications |
| `CUSTOMER-LANG` | Anonymous shopper | New browser/session | English, Urdu, Roman Urdu |

Required seed catalog for `OWNER-PAID`:

* Import the approved 500-row data for catalog/search coverage.
* Import the F04-reviewed data in a clean test cycle for verified build coverage.
* Maintain a written fixture map of known active/in-stock, out-of-stock, archived, eligible, ineligible, CPU, GPU, and comparison products. Chat expectations must use this map, never guessed catalog facts.
* `OWNER-OTHER` receives unique product names and SKUs so every cross-shop denial is unambiguous.

## Evidence Required for Every Test

Every Playwright test must produce and retain:

* A video for both pass and fail, named with run ID, test ID, browser, and viewport.
* Start/end screenshots or a final full-page screenshot.
* Browser-console errors and failed network requests as attachments.
* Playwright trace for a failed or retried test.
* Test input summary with secrets and personal data redacted.
* Where a server-side result is essential, a minimal safe verification record: record ID/count/status only, never raw private payloads.
* For every F07 case, separate recordings show the source Sheet change and the corresponding SaleAura owner result. Both recordings use the same run ID and test ID.

Video exception: the manual Google credential-entry screen is excluded from recording. Recording begins again immediately after the provider returns to SaleAura. This protects the dedicated account while preserving evidence of SaleAura's callback result.

## Test Environments and Devices

| Project | Purpose | Required journeys |
| --- | --- | --- |
| Desktop Chrome | Primary owner and customer validation | All tests |
| Mobile Chrome viewport | Responsive customer and owner behavior | E2E-001, E2E-002, E2E-004, E2E-006 to E2E-011 |

All tests run serially within a persona/data group. Independent groups may run separately only when they do not share an account, host, quota, inventory, or provider event.

## Required Execution Sequence

### Phase 0 - Run Preflight

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `E2E-000` | Staging readiness | Correct staging target, required test accounts, clean data, active sandbox products, approved widget test hostname, app health | All preconditions are present; otherwise record `BLOCKED` and stop the affected path |
| `E2E-001` | Public visitor | Home, pricing, legal routes, sign-in entry, supported positioning, desktop/mobile layout, broken links | Pages load, claims match V1, routes work, layout remains usable |

### Phase 1 - Owner Identity, Profile, and Free Plan

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `E2E-002` | Google sign-in and callback | Start Google sign-in, manual login checkpoint, return path, cancellation/error recovery | One owner session is created/restored; safe error/retry state for cancellation/failure |
| `E2E-003` | Protected routes | Visitor opens dashboard, inventory, billing, widget pages; incomplete owner repeats the attempt | Visitor reaches sign-in; incomplete owner reaches profile; no redirect loop |
| `E2E-004` | Complete profile | Required contact/localization values, invalid country/city/phone/timezone, optional image, refresh persistence | Only valid values complete profile; one profile exists; errors are clear and safe |
| `E2E-005` | Edit profile and logout | Edit valid fields/image, reject invalid edit, refresh, logout, revisit protected route | Same profile updates; logout clears access; protected route returns to sign-in |
| `E2E-006` | Free plan and quota explanation | Dashboard/billing plan details and 500-row CSV preview | Free plan and current usage are accurate; owner sees 100-row limit before unintended save |

### Phase 2 - Sandbox Subscription and Paid Catalog

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `E2E-007` | Starter sandbox checkout | Paid-plan choice, sandbox checkout, return, verified webhook update, billing history | Correct Starter plan/limits appear only after verified provider processing |
| `E2E-008` | Checkout and billing recovery | Cancel checkout, provider/unavailable message, portal access | Owner receives clear recovery; no false access grant; portal is owner-scoped |
| `E2E-009` | Valid 500-row import | `ProductListing - 500.csv` preview, import, final summary, visible inventory | Expected rows save within paid limit and final counts/statuses are correct |
| `E2E-010` | CSV failure and recovery | `ProductListing - Failure Cases.csv`, mixed valid/error rows, failed-row download | Valid rows save, errors explain affected rows, downloadable report matches visible result |
| `E2E-011` | CSV duplicate/update behavior | `ProductListing - Duplicate Update Cases.csv` | Existing SKU/alias rows update without duplicates; changed values appear correctly |
| `E2E-012` | Reviewed build catalog | Clean import of `ProductListing - 500.f04-reviewed.csv` | Eligible/ineligible state and required component coverage are available for build paths |
| `E2E-013` | Manual inventory lifecycle | Create invalid/valid product, edit, upload image/link, archive, reactivate, zero stock, search/filter/sort/page | Owner sees accurate state/reasons; customer visibility follows active/in-stock rules |

### Phase 2A - Google Sheet Inventory Sync

Google-managed products are always edited or removed in the connected Google Sheet. The owner returns to SaleAura, uses `Sync & Preview`, reviews the planned result, and then saves it. Tests run in the listed order because each later case relies on the correctly synced catalog from the earlier case.

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `F07-INV-001` | First connection and saved source | First URL entry, selected worksheet, preview, cancel, refresh, saved URL, worksheet name, and first-sync CTA | The owner sees the saved connected Sheet and `Sync & Preview`; no URL must be pasted again |
| `F07-INV-002` | Initial 500-product Sheet save | Preview and save the dedicated 500-product Sheet | Exactly 500 source products are visible and the result clearly reports the saved counts |
| `F07-INV-003` | Update at full quota | Rename one known product at 500/500, then sync and save | The row is an update, not a new product; no quota block appears |
| `F07-INV-004` | Update plus new row at full quota | Change one known product and add one new product at 500/500 | The update is saved, only the new row is skipped, and the quota message is clear |
| `F07-INV-005` | Source removal and re-add | Remove a middle and a final Sheet row in separate syncs, then re-add one | The exact removed product disappears after each completed sync; other products remain correct; a re-added product follows the normal new-row quota rule |
| `F07-INV-006` | Reorder and identity safety | Reorder rows and change safe fields on known products | Row order does not swap, duplicate, or change product identity |
| `F07-INV-007` | Invalid and interrupted source states | Missing/duplicate stable ID, invalid row, inaccessible Sheet, wrong worksheet, cancelled preview, failed read | The owner gets a clear recovery message and existing inventory is unchanged |
| `F07-INV-008` | Source replacement | Paste a different worksheet and accept or cancel the replacement confirmation | Nothing changes until confirmed; the selected result is accurately shown afterward |
| `F07-INV-009` | Inventory actions and guidance | Google-managed row help; Manual/CSV single Delete, selected-row Delete, Select All, bulk Delete, cancel, confirm, search, filter, pagination | Google rows explain the Sheet rule; eligible owner rows delete only after clear confirmation |
| `F07-INV-010` | Isolation and responsive regression | Repeat the core connect, full-quota update, removal, and action-guidance cases as another owner and on mobile | No cross-owner access; all controls, alerts, and text remain usable on mobile |

### Phase 3 - Widget Installation and Customer Search

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `E2E-014` | Widget owner setup | Add/remove approved host, reject malformed host, copy install snippet, save customization, preview | Exact host rule is enforced; saved branding persists and preview reflects it |
| `E2E-015` | Real embedded widget start | Load widget from approved staging test-shop page, open/close/reopen, refresh page | Widget starts a private session and retains bounded conversation state; no voice/TTS control is visible |
| `E2E-016` | Product search | Natural shopper requests for known product, unknown product, out-of-stock/archived product, follow-up | Only the correct shop's visible inventory appears; unavailable items are not presented as purchasable |
| `E2E-017` | Product comparison | Compare known products, include an unknown/missing property, ask a follow-up | Comparison uses only catalog facts and labels missing information as unavailable |
| `E2E-018` | Multilingual chat | Repeat realistic product/search/comparison prompts in English, Urdu, Roman Urdu | Intent and safe catalog grounding are preserved in all supported languages |

### Phase 4 - Customer Build and Modification

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `E2E-019` | Verified build request | Gaming, editing, office, general-use request with realistic budgets | Each build is complete, in stock, eligible, compatible, customer-safe, and within budget |
| `E2E-020` | No-build/unsafe-data outcome | Too-low budget, missing category, ineligible/unknown compatibility condition | Widget does not invent a partial or unsafe build; it clearly explains the next customer action |
| `E2E-021` | Build changes | Cheaper request, CPU/GPU upgrade/downgrade, brand/budget request, alternatives, cancel | Current build remains unchanged until explicit confirm; proposal shows complete customer-safe differences |
| `E2E-022` | Build confirmation/revalidation | Confirm proposed change after controlled stock/state change, then make a sequential change | Confirmation rechecks stock/compatibility/version; stale proposal is safely rejected; next snapshot is correct |

### Phase 5 - Leads, Notifications, and Owner Dashboard

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `E2E-023` | Lead validation | Product/build lead form with missing name, no contact, no consent, valid phone/email/WhatsApp | Clear validation; no incomplete lead is saved |
| `E2E-024` | Lead save and duplicate control | Submit valid product lead and valid build lead; repeat same request | One correctly scoped lead per intent is saved with product/build context and quota count is correct |
| `E2E-025` | Notification success | Trigger valid lead notification | Staging response reports success; owner dashboard records lead; tester confirms delivery to designated email/WhatsApp |
| `E2E-026` | Notification failure preservation | Controlled staging notification-provider failure after a valid lead save | Lead remains saved and owner sees a safe result; failure does not duplicate or erase the lead |
| `E2E-027` | Owner dashboard | Sign in as owner after customer activity; inspect counts, recent leads, plan/usage, empty/loading/error states | Dashboard reflects actual owner-scoped data with no fabricated/scaled metrics |

### Phase 6 - Entitlements, Security, Isolation, and Responsive Regression

| Test ID | Journey | Checks | Pass condition |
| --- | --- | --- | --- |
| `E2E-028` | Retained access | Cancel/expire `OWNER-RETAINED` in sandbox; open owner pages and public widget | Existing approved data remains viewable; widget/new metered actions are blocked clearly |
| `E2E-029` | Reactivation | Reactivate sandbox subscription | Eligible activity returns without losing inventory, leads, chats, or existing data |
| `E2E-030` | Shop isolation | `OWNER-OTHER` and separate customer contexts attempt cross-shop URLs, widget interactions, inventory/chat/lead/billing access | No cross-owner data is visible or mutable |
| `E2E-031` | Widget/session abuse recovery | Unapproved origin, malformed host, fake/expired session, repeated messages, refresh/retry | Requests fail safely; approved widget remains usable; no secrets or owner IDs appear |
| `E2E-032` | Mobile regression | Repeat the highest-value profile, billing, CSV preview, widget, search, comparison, build, modification, lead, dashboard flows | No overlap, clipped text, unreachable controls, or broken responsive conversation flow |

## Feature Coverage Map

| Feature | Covered by |
| --- | --- |
| F01 Authentication and onboarding | E2E-002 to E2E-005 |
| F02 Billing, entitlements, quotas | E2E-006 to E2E-008, E2E-024, E2E-028 to E2E-029 |
| F03 Product catalog | E2E-009 to E2E-013, E2E-016 |
| F04 Compatibility | E2E-012 to E2E-013, E2E-019 to E2E-022 |
| F05 Performance reference | E2E-019, E2E-021 to E2E-022 |
| F06 CSV pipeline | E2E-006, E2E-009 to E2E-012 |
| F07 Google Sheets | F07-INV-001 to F07-INV-010 |
| F08 Widget platform/security | E2E-014 to E2E-015, E2E-028, E2E-031 |
| F09 Search/comparison | E2E-016 to E2E-018 |
| F10 Build generation | E2E-019 to E2E-020 |
| F11 Build modification | E2E-021 to E2E-022 |
| F12 Leads/notifications | E2E-023 to E2E-026 |
| F13 Dashboard | E2E-027, E2E-030, E2E-032 |
| F14 Public site | E2E-001 |

## Run Levels and Gates

| Run | Tests | Trigger | Release rule |
| --- | --- | --- | --- |
| Smoke | E2E-000, 001, 004, 009, F07-INV-001, F07-INV-003 to F07-INV-005, 014 to 016, 023 to 025, 027 | Every meaningful staging change | All pass; no Critical/High open finding |
| Full desktop | E2E-000 to E2E-031 and F07-INV-001 to F07-INV-009 | Feature-complete staging candidate | All in-scope tests pass or have an approved documented blocker |
| Full mobile | E2E-001, 002, 004, 006, 014 to 027, 032, and F07-INV-010 | Same candidate after desktop pass | All selected tests pass; no responsive Critical/High finding |
| Re-test | Affected tests plus prerequisite/consumer tests | Developer marks a bug fixed | Fix test passes, regression set passes, original finding is closed with evidence |

## Defect Severity and Stop Rules

| Severity | Meaning | Action |
| --- | --- | --- |
| Critical | Data exposure/loss, payment error, cross-shop access, unsafe widget session, broken sign-in, complete journey unavailable | Stop affected run; do not release |
| High | Core owner/customer journey cannot finish, wrong plan/quota, wrong inventory/build/lead result, notification loss | Block release until fixed and re-tested |
| Medium | Important behavior has a workaround or limited scenario impact | Record, assign, and re-test before release decision |
| Low | Cosmetic, wording, or minor usability issue with no incorrect outcome | Record and schedule; still re-test if changed |

Stop immediately for a production target, real payment charge, non-test account, exposed secret/private data, destructive data operation outside a dedicated test tenant, or a suspected cross-shop/privacy breach.

## Notification Manual Checkpoint

For `E2E-025`, Playwright records the safe application-side result. The designated tester then confirms:

* Email received: `Yes`, `No`, or `Not yet`.
* WhatsApp received: `Yes`, `No`, or `Not yet`.
* Receipt time and message correctness, with personal contact information redacted.

`E2E-025` remains `PENDING_MANUAL_CONFIRMATION` until both requested delivery confirmations are recorded in the tracker.

## Completion Criteria

The staging plan is complete only when every in-scope test has a final status, every failed/retried test has linked evidence, no Critical/High finding remains open, manual notification confirmations are recorded, and the tracker contains the final run summary.
