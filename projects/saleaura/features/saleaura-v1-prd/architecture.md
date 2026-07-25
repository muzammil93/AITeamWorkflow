# Architecture Document

## Feature Name

SaleAura V1 Production-Ready Product Architecture

## PRD Reference

`projects/saleaura/features/saleaura-v1-prd/prd.md`

The referenced PRD ends with `STATUS: PRD_READY` and was revised on 2026-07-01 from the CEO’s locked decisions and the completed code/live-Supabase audits.

This architecture is ready for CEO review. Developer execution remains paused until the CEO explicitly resumes it.

### Delivery Governance Addendum

The SaleAura V1 release plan decomposes this master architecture into dependency-locked feature workflows. This changes delivery packaging, not product scope or target behavior.

Each feature:

* Owns only its assigned master requirements.
* Produces its own implementation, QA, review, and final-report evidence when applicable.
* Uses a feature-scoped additive migration when its database changes are ready.
* Must not rewrite a migration already applied to shared staging or production.
* Must satisfy its dependency and milestone gates before the next dependent feature begins.

The release plan and feature artifacts must preserve all requirements in this master architecture; decomposition must not be used to omit cross-feature security or integration behavior.

## Technical Summary

SaleAura V1 will harden and extend the existing hybrid Next.js, Flask, and Supabase application. This is an incremental architecture, not a rewrite.

The existing boundaries remain:

* Next.js owns the website, authenticated owner experience, embedded widget UI, and public/server API façade.
* Flask owns inventory ingestion, AI intent handling, deterministic compatibility, build generation and modification, lead capture, and external notification calls.
* Supabase PostgreSQL is the durable source of truth for owners, inventory, sources, imports, performance references, chat state, leads, plans, and quotas.
* OpenAI may classify intent, extract user preferences, and compose grounded language, but it must not decide hard compatibility, stock, quotas, product identity, or whether a CPU/GPU change is a verified upgrade.

### Current Implementation Baseline

The current implementation already contains partial support for:

* Google OAuth, profile creation/onboarding, protected owner routes, and logout.
* Owner profile editing and localization fields.
* Dashboard statistics, recent leads, lead analytics, and owner navigation.
* CSV and first-worksheet Google Sheets import.
* Inventory embeddings and structured inventory search.
* Product search, comparison, build request, and lead-capture intents.
* A seven-component tower build generator.
* A `BuildModifier` service that is not wired into the active chat route.
* Rule-based compatibility that mixes structured fields with product-name inference.
* Widget product, comparison, build, and lead cards.
* Widget branding customization, preview, installation snippet generation, and a public configuration endpoint.
* DB-driven subscription entitlements and quota RPCs.
* Owner email and WhatsApp lead notifications.

The current implementation is not sufficient for the approved V1 because:

* Inventory has no SKU, per-product source identity, archive state, Google Sheets ownership rule, or category-wise eligibility state.
* Existing imports match mainly by normalized name/category/brand and cannot safely implement the approved identity rules.
* Compatibility data is incomplete and several validations infer facts from product names.
* Build generation omits cooling and can return an over-budget build without prior budget approval.
* `build_modify` is recognized by intent classification but is not routed by the active engine.
* Existing “upgrade” selection is price-based rather than verified performance-based.
* The browser creates a new chat session on mount, while important state is stored in Flask memory; current builds and pending modifications do not reliably survive reloads or restarts.
* The widget lacks a modification-preview card and a complete structured action contract.
* Customer-facing data is not separated from full inventory rows at a strong API boundary.
* Owner inventory/import routes trust client-supplied owner IDs in multiple paths.
* Authentication/profile/dashboard behavior is spread across client components, server actions, middleware, and routes without one production-validated end-to-end contract.
* Dashboard panels can fail without a typed partial-failure contract.
* Widget installation has no persisted allowed-domain model or server-enforced host authorization.
* The embed script trusts URL attribution values and the public configuration route returns fallback configuration when loading fails; neither can authorize an embedding website.
* Trial/cancellation restrictions are not enforced consistently across widget bootstrap, chat, lead, AI, and inventory-creation boundaries.
* Live staging currently has `public.leads` RLS disabled. Live policies also expose full inventory and embeddings for public reads and allow overly permissive inserts/updates on other sensitive tables.
* TypeScript and ESLint errors are ignored during Next.js builds, and no automated test suite is present.

### Target Architecture

The V1 implementation will introduce six coordinated domain layers:

1. **Owner lifecycle and entitlement layer**
   * One Google-authenticated owner identity per SaleAura profile.
   * Validated onboarding/profile updates and deliberate protected-route behavior.
   * Owner-scoped dashboard and widget-management APIs.
   * One effective-access decision shared by widget, chat, lead, AI, and inventory-creation boundaries.
   * Retained owner-data access after trial expiry/cancellation with new metered activity disabled.

2. **Inventory identity and source layer**
   * Owner-scoped unique SKUs.
   * Stable legacy SKU backfill.
   * SKU aliases so an owner can replace a SKU without breaking identity.
   * Manual, CSV, and Google Sheets provenance.
   * One active Google spreadsheet/worksheet connection per owner.
   * Explicit active/manual-archive/mirror-archive behavior.

3. **Compatibility and performance layer**
   * Category-specific validated compatibility specifications.
   * Cached category eligibility plus machine-readable ineligibility reasons.
   * A versioned Supabase CPU/GPU performance reference catalog.
   * Deterministic normalization and matching with traceable source metadata.

4. **Verified build layer**
   * Deterministic eight-category GPU tower builds, with cooling conditional on verified CPU included-cooler data.
   * Inventory, stock, visibility, eligibility, budget, and compatibility validation at selection time.
   * Genuine CPU/GPU upgrade and downgrade logic based on verified scores.

5. **Durable build-modification layer**
   * Current build and pending proposal stored in Supabase-backed chat-session state.
   * Preview-before-apply semantics.
   * Explicit dependent changes.
   * Revalidation and optimistic version checks at confirmation.

6. **Security and production-readiness layer**
   * Authenticated owner APIs that derive ownership from Supabase Auth.
   * Owner-managed exact-host widget allowlist.
   * Allowed-host validation during widget bootstrap and a short-lived signed bootstrap credential exchanged for durable anonymous-session authorization.
   * Public APIs that return explicit customer-safe DTOs only.
   * Service-role-only writes for anonymous customer activity.
   * Correct RLS, grants, quota accounting, rate limiting, stable errors, type checks, and targeted automated tests.

### Primary Data Flow

#### Owner authentication and onboarding

1. The owner starts Google OAuth from `/auth`.
2. The callback exchanges the authorization code through the server Supabase client and validates the redirect host.
3. SaleAura loads the authenticated user and idempotently creates the owner profile if it does not exist.
4. An incomplete profile is routed to `/profile`; a complete profile is routed to `/dashboard`.
5. Profile reads and writes use the authenticated user ID, validate supported fields, and rely on owner-scoped RLS as defence in depth.
6. Protected owner routes redirect expired or unauthenticated sessions without exposing provider or token details.

#### Owner dashboard and retained-access mode

1. Protected dashboard routes derive the owner ID from the Supabase server session.
2. Independent owner-scoped queries load lead usage, chat sessions, inventory state, plan/subscription status, recent leads, and lead analytics.
3. The response distinguishes successful zero values from unavailable panels.
4. A shared entitlement resolver determines `active`, `retained_access`, or `unavailable`.
5. In `retained_access`, profile, billing, inventory, and existing leads remain accessible; widget bootstrap and new metered activity are rejected with a stable reactivation response.

#### Widget customization and authorized bootstrap

1. The authenticated owner saves customization and exact allowed hostnames through owner-scoped APIs.
2. The installation snippet contains only the public SaleAura script URL and public owner identifier.
3. When `embed.js` runs on a host page, it requests widget bootstrap. Browser-provided origin/referrer context is validated against the owner’s normalized allowlist; a host value supplied in the body or query is never authoritative.
4. An authorized, active owner receives customer-safe customization plus a short-lived signed bootstrap credential bound to the owner and normalized host.
5. The iframe exchanges that credential for a durable anonymous session credential. Later iframe-origin requests are authorized through that session because their network origin is SaleAura, not the embedding website.
6. Unauthorized, missing-origin, expired-subscription, or invalid bootstrap requests do not render fallback owner configuration or allow chat/lead actions.

#### Inventory import or manual creation

1. The authenticated owner submits a manual product, CSV preview, or Google Sheet sync request through a Next.js API route.
2. The Next.js route validates the Supabase session and derives the owner ID. A client-supplied `user_id` is never authoritative.
3. Flask parses the source into one canonical inventory-input model.
4. The input model distinguishes a missing column from an explicitly blank cell.
5. SKU/source identity is resolved before quota classification:
   * Current SKU match.
   * Historical SKU alias match.
   * Safe source-row match where applicable.
   * Otherwise a new product.
6. New-row quota is reserved atomically. Existing-row updates continue even when no new slots remain.
7. Valid rows are persisted, compatibility specifications are validated by category, eligibility reasons are calculated, and CPU/GPU catalog matching is attempted.
8. Embeddings are refreshed only when searchable semantic fields changed.
9. The import result reports inserted, updated, unchanged, archived, reactivated, and failed rows.
10. Mirror-mode archiving occurs only after a complete successful source read and row-validation pass; it must not run after a partial source failure.

#### Customer chat and verified build

1. The widget sends a message with an opaque durable session credential and public shop identifier.
2. The public API applies per-IP/session/owner abuse controls and loads the owner’s active entitlement.
3. AI classification extracts intent, language, and soft preferences.
4. Product and build services query only active, in-stock customer-visible inventory. Verified builds additionally require category eligibility.
5. Deterministic code validates component compatibility and budget.
6. A customer-safe structured response is returned to the widget.
7. If a build is generated, its immutable snapshot becomes the current session build and its version is incremented.

#### Build modification

1. AI classification extracts a modification request against the latest current build.
2. The modifier resolves candidates using inventory data, verified performance where required, and deterministic compatibility.
3. If dependencies are needed, the service calculates the smallest complete compatible change set.
4. The proposal is stored separately from the current build.
5. The widget renders the proposal, old/new components, dependent changes, price delta, new total, stock, compatibility, and budget impact.
6. Confirm, alternatives, and cancel are structured actions; they do not depend on the LLM interpreting button text.
7. Confirmation reloads every affected inventory row, verifies session/build version, stock, active state, eligibility, compatibility, and budget approval.
8. Only a successful confirmation replaces the current build. Stock is not reserved.

## Frontend Changes

### Authentication and Profile

Retain the current Google-only authentication direction in `app/auth/page.tsx` and the server callback in `app/auth/callback/route.ts`.

Required hardening:

* Keep provider errors safe and actionable.
* Preserve forwarded-host validation and reject untrusted callback hosts.
* Make fallback profile creation idempotent and owner-scoped.
* Route incomplete profiles to onboarding and complete profiles to the dashboard.
* Redirect authenticated owners away from redundant authentication where appropriate.
* Preserve secure logout through the shared owner navigation.

Update `app/profile/page.tsx` and `lib/actions/profile.ts` so one validated contract covers first-time completion and later editing.

The profile form must:

* Validate full name, shop name, phone, WhatsApp, country, city, currency, currency symbol, timezone, phone country code, address, and optional image.
* Keep country-dependent choices consistent.
* Derive the owner ID from the server session.
* Avoid passing arbitrary `Partial<Profile>` data directly to persistence.
* Return field-safe errors and distinct loading/success states.
* Create default widget customization idempotently without making profile success depend on a duplicate customization insert.

No email/password provider, staff invitation, account deletion, or data-export flow is added.

### Owner Dashboard

Keep the existing dashboard and navigation; do not create a replacement dashboard.

Harden:

* `app/dashboard/page.tsx`
* `app/api/dashboard/stats/route.ts`
* `app/api/dashboard/recent-leads/route.ts`
* `app/api/dashboard/leads-analytics/route.ts`
* `components/AppSidebar.tsx`
* `components/DashboardLayout.tsx`

Define shared typed response contracts for stats, recent leads, and chart points. Every API route must authenticate, derive the owner ID from the server session, and return a stable panel result.

The page must distinguish:

* A valid zero.
* Loading.
* Empty data.
* A failed individual panel.
* A fully unavailable dashboard.

Keep current V1 information architecture: monthly leads/limit, chats/conversations, inventory, plan/subscription status, recent leads, and lead activity over time. Do not add lead stages, conversion pipeline, data export, or operator metrics.

### Widget Setup and Customization

Update `app/chat-widget/page.tsx` and the owner customization API.

The owner screen must retain:

* Header title/subtitle.
* Primary colour.
* Welcome message.
* Bot name and image.
* Live preview.
* Copyable installation snippet.

Add exact-host allowed-domain management with normalization, validation, duplicate prevention, removal confirmation, and a clear empty state. V1 does not support wildcard domains; each hostname/subdomain must be added explicitly.

The preview must use an authenticated, short-lived preview-authorization path. It must not require weakening the public allowed-domain check or adding SaleAura’s own hostname to every owner’s customer allowlist.

Update `public/embed.js` so configuration failure does not silently create a generic active widget. It must request authorized bootstrap first, pass the returned short-lived credential to the iframe, and render nothing except a safe console diagnostic when authorization fails.

### Owner Inventory Experience

Update `app/inventory/page.tsx` and extract focused components where the page would otherwise become harder to maintain.

The inventory screen must provide:

* Manual product creation.
* Edit and archive actions for manual and CSV products.
* Read-only controls for Google Sheets products.
* A visible source badge: Manual, CSV, or Google Sheets.
* SKU display and validation.
* A generated-legacy-SKU indicator where applicable.
* Active, zero-stock, manually archived, and mirror-archived states.
* Build eligibility status and category-specific reasons.
* CPU/GPU performance match status: verified match, unmatched, or review required.
* Google Sheets connection details, selected worksheet, mirror-mode setting, last-sync status, and a manual Sync action.
* A clear message on Google Sheets rows: the product and its image must be edited in the connected sheet, then synced.
* Failed-row download containing SKU/source row and field-specific validation errors.

Manual and CSV product forms must use category-specific fields. Selecting a category changes the compatibility fields shown and validated. The form must not present one universal “compatible” checkbox.

The UI may preserve the current preview/progress experience, but the preview table must add SKU, source, and validation result information.

Explicit blank-cell behavior must be explained in import guidance:

* A present blank cell clears the existing optional value.
* Blank numeric price or stock clears to `0` because these fields remain non-null.
* Blank name, category, or SKU is invalid for a new V1 row.
* An omitted optional column does not alter the existing value.

### Google Sheets Connection UI

V1 supports one active spreadsheet and one worksheet/tab per owner.

The connection UI must:

* Accept and validate a Google Sheet URL.
* Load available worksheets and require the owner to select one worksheet.
* Persist the spreadsheet ID and immutable worksheet GID, not only the display title.
* Allow mirror mode to be explicitly enabled or disabled.
* Explain that Google-sourced products are read-only in SaleAura.
* Explain that image URLs for Google-sourced products must be changed in the sheet.
* Show the last successful sync time and last result summary.
* Require an explicit manual Sync action; no scheduled/background sync is introduced.

Changing the active spreadsheet/worksheet requires confirmation because it changes the source identity boundary. It must not silently archive the previous source’s products.

### Chat Widget

Update the shared response types in `components/chat/ChatWidget.tsx` and the Pydantic response models together.

The widget must:

* Persist the opaque session credential in `sessionStorage`, keyed by shop owner, so reload reuses the current conversation while a new browser session remains anonymous.
* Rehydrate structured history and the current build from the server.
* Render product, comparison, build, modification-preview, clarification, and lead-capture payloads from explicit DTOs.
* Never render raw database rows.
* Send button actions as structured payloads.
* Render English and Roman Urdu left-to-right and Urdu right-to-left at the message/card boundary.
* Keep mobile embedded layouts usable without horizontal page overflow.
* Hide voice recorder, speech-to-text, and audio playback controls for V1.

### Build Card

Extend `components/chat/cards/BuildCard.tsx` so every component can include:

* Inventory ID and SKU for internal action references.
* Customer-safe name, category, price, stock state, image, product URL, and concise specs.
* Cooling as a visible category when a separate cooler is required.
* A verified-build indicator only when every required category passes deterministic validation.

The “I want this build” button must send a structured `start_lead_capture` action containing the current build version. It must not rely on a generic text message. The lead form will be linked to the server-held finalized build snapshot.

### Build Modification Preview Card

Add a focused card, likely `components/chat/cards/BuildModificationCard.tsx`, and export it through the existing cards index.

It must show:

* Requested change.
* Old and replacement component.
* Each dependent old/replacement component.
* Per-component price delta.
* Total price delta and new build total.
* In-stock/revalidated state.
* Compatibility result and any blocking reason.
* Original budget, new total, and over/under-budget result.
* Verified performance delta for CPU/GPU when available.
* Confirm, See alternatives, and Cancel actions.

Confirm must be disabled when the proposal is expired or marked invalid. Server confirmation remains authoritative even when the button is enabled.

### Lead Capture

The lead form must:

* Require a full name.
* Require at least one contact method.
* Require an explicit consent checkbox.
* Not infer consent merely because contact details were entered.
* Preserve the linked current build version while the form is open.
* Show a safe retry state when saving fails.

The owner dashboard may display the attached build summary using the existing lead surfaces. No new dashboard is introduced.

### Plans and Positioning

Existing marketing, billing, and entitlement displays must use the locked plan values:

* Free: 30-day trial, 100 inventory items, 25 leads/month, 500 AI responses/month.
* Starter: USD 19/month, 500 inventory items, 150 leads/month, 2,000 AI responses/month.
* Growth: USD 49/month, unlimited inventory items, 600 leads/month, 8,000 AI responses/month.

Customer and owner copy must describe SaleAura as a PC component and custom PC building product, not a generic retail assistant.

Billing and owner navigation must clearly represent three effective access modes:

* Active trial/subscription.
* Retained access after trial expiry/effective cancellation.
* Temporary unavailable/error state.

In retained access, existing profile, billing, inventory, and lead surfaces remain reachable. Controls that create new metered activity must explain that reactivation is required. A verified Polar webhook or refreshed server entitlement—not a checkout-return query parameter—restores active access.

Existing terms, privacy, and refund links may remain visible, but their routes and content must not be modified in V1.

## Backend Changes

### Owner Lifecycle and Entitlement Services

Owner authentication remains in Next.js/Supabase rather than Flask.

Create or consolidate server-side helpers for:

* Loading the authenticated owner or returning a stable unauthorized response.
* Validating and updating permitted profile fields.
* Loading dashboard panel data with owner scoping.
* Resolving one effective access mode from trial dates, subscription status, subscription end date, and verified Polar state.
* Enforcing active access for widget bootstrap, model-backed chat, new leads, and new inventory items.
* Preserving retained access to approved existing owner data.

Do not scatter different subscription-status checks across routes. Flask receives trusted owner/access context from the Next.js boundary where needed and still validates quota operations through atomic database functions.

### Widget Bootstrap and Domain Authorization

Add a server-owned widget bootstrap service.

Normalization rules:

* Store lowercase ASCII hostnames only.
* Strip scheme, path, query, fragment, trailing dot, and default port during owner input normalization.
* Reject credentials, IP/private-network hosts in production, malformed internationalized domains, public-suffix-only values, wildcards, and lookalike suffix matching.
* Require explicit rows for subdomains.
* Permit development hosts only in non-production environments.

Authorization rules:

* Read the browser-provided `Origin`; use a validated referrer only where browser behavior requires a documented fallback.
* Reject public bootstrap when neither trustworthy header is available.
* Never authorize from `host_page_url`, `host_referrer`, request JSON, or a query parameter.
* Require the owner’s effective access mode to be active.
* Return only customer-safe customization.
* Sign a short-lived bootstrap credential containing owner ID, normalized host, issue/expiry time, and a nonce.
* Exchange the bootstrap credential once for the durable anonymous session ID/secret used by chat, history, actions, and leads.
* Add a dynamic `Content-Security-Policy: frame-ancestors` response for the widget page using approved hosts as defence in depth.

Attribution URL values may still be recorded after URL validation, but they are untrusted analytics fields and never authorization evidence.

### Domain Models

Extend `backend/schema.py` with explicit models for:

* Canonical inventory input.
* Category-specific compatibility specifications.
* Build eligibility result.
* Performance reference match.
* Durable build snapshot.
* Build modification request.
* Build modification proposal.
* Structured chat action.
* Customer-safe product/build DTOs.
* Response language: `en`, `ur`, or `ur_roman`.

The TypeScript widget contracts and Pydantic models must represent the same fields and status values.

### Inventory Import Service

Move import identity, normalization, row validation, and persistence planning out of the oversized Flask route into focused services, while retaining the existing Flask endpoint adapters.

Recommended responsibilities:

* `inventory_import_service.py`
  * Parse canonical rows.
  * Resolve SKU/source identity.
  * Classify insert/update/unchanged/failure.
  * Enforce partial-import quotas.
  * Apply mirror archive/reactivation after a safe full sync.
  * Produce progress and failed-row results.
* `inventory_eligibility_service.py`
  * Validate category-specific required data.
  * Return `build_eligible`, reason codes, and rules version.
* `performance_reference_service.py`
  * Normalize CPU/GPU model names.
  * Resolve canonical and alias matches.
  * Assign system-managed score/match metadata.

The existing semantic embedding path may remain for product discovery. It is not the source of identity, compatibility, or performance truth.

### SKU and Identity Rules

Identity resolution must use this order:

1. Exact owner-scoped current normalized SKU.
2. Exact owner-scoped historical SKU alias.
3. Exact source record reference for the same active source, with corroborating product identity fields.
4. No match: classify as a new product.

Loose name/category/brand matching may assist a one-time legacy backfill review, but it must not silently overwrite a V1 record.

Rules:

* New manual, CSV, and Google Sheets products require SKU.
* Existing rows are backfilled with `LEGACY-<stable value derived from inventory UUID>`.
* SKU comparison is trimmed and case-insensitive.
* A SKU update retains the same inventory UUID.
* The old SKU becomes an alias and cannot be reused by another product for that owner.
* Duplicate or ambiguous rows fail individually and appear in the failed-row report.

For Google Sheets, persist spreadsheet ID, worksheet GID, and source row position/reference. SKU or alias remains the primary match. A row-position fallback is allowed only when previous identifying fields corroborate the same product; otherwise the row must fail safely instead of overwriting another item.

### Blank and Missing Values

The parser must stop using truthy `or` chains that make a blank value indistinguishable from an absent value or numeric zero.

Canonical parsing rules:

* Header absent: preserve the existing field during update.
* Header present with blank cell: clear the field.
* Optional text/URL/spec blank: persist `NULL`.
* Price/stock blank: persist `0`.
* Required name/category/SKU blank: reject the row.
* Invalid number, URL, enum, connector count, or dimension: reject that field/row with a stable reason code; do not guess.

### Category-Wise Eligibility

`CompatibilityValidator` must use structured, normalized specifications for verified decisions. Name inference may be retained only as a non-verified hint for searchable legacy products.

Each category validator returns:

* Canonical category.
* Eligibility boolean.
* Missing fields.
* Invalid fields.
* Machine-readable reason codes.
* Human-readable owner guidance.
* Rules version.

Minimum V1 data:

* CPU: socket, family/generation where required, included-cooler status, and cooling/power requirement.
* GPU: length in millimetres, recommended PSU wattage, required connector counts/types, VRAM, and verified performance match.
* Motherboard: socket, supported CPU family/generation where required, chipset, RAM type, form factor, and storage interfaces.
* RAM: RAM type, capacity, module count/kit, and speed.
* Storage: SSD/HDD type, interface, form factor where relevant, and capacity.
* PSU: wattage, form factor, efficiency where displayed, and connector counts/types.
* Case: supported motherboard form factors, supported PSU form factors, maximum GPU length, air-cooler height, and supported radiator sizes.
* Cooling: air/AIO/stock type, supported sockets, cooler height or radiator size, and verified cooling suitability.

The cached inventory eligibility result is an indexable summary, not the compatibility rule itself. The category validator and normalized specs remain authoritative.

### Deterministic Compatibility Engine

The compatibility engine must validate at least:

* CPU socket/family against motherboard socket/chipset support.
* Motherboard RAM type against RAM type.
* Motherboard storage interface against storage interface/form factor.
* GPU recommended wattage against PSU wattage.
* GPU required power connectors against PSU connector availability.
* GPU length against case clearance.
* Motherboard form factor against case support.
* PSU form factor against case support.
* Cooler socket against CPU socket.
* Air-cooler height against case clearance.
* AIO radiator size against case radiator support.
* Cooling suitability against the selected CPU’s verified requirement.

Unknown required data is a failed verified check, not an implicit pass.

Compatibility results must use stable reason codes such as:

* `CPU_SOCKET_MISMATCH`
* `CPU_FAMILY_UNVERIFIED`
* `RAM_TYPE_MISMATCH`
* `STORAGE_INTERFACE_UNSUPPORTED`
* `PSU_WATTAGE_INSUFFICIENT`
* `PSU_CONNECTOR_INSUFFICIENT`
* `GPU_CASE_CLEARANCE_FAILED`
* `MOTHERBOARD_CASE_FORMAT_UNSUPPORTED`
* `PSU_CASE_FORMAT_UNSUPPORTED`
* `COOLER_SOCKET_MISMATCH`
* `COOLER_CLEARANCE_FAILED`
* `RADIATOR_FORMAT_UNSUPPORTED`
* `COOLING_CAPACITY_UNVERIFIED`

### Performance Reference Catalog

Implement a curated, versioned catalog in Supabase. Do not fetch benchmark data at customer request time and do not let owners enter scores.

Catalog rules:

* CPU and GPU scores are category-local and must never be compared across categories.
* Each published catalog version records its benchmark basis, normalization method, publication date, source URLs, and licensing/review notes.
* A V1 seed dataset covers common desktop consumer CPUs and discrete GPUs relevant to active PC-builder inventory.
* Laptop, server, workstation, OEM-only, obscure, and historical-completeness goals remain out of scope.
* Canonical models and aliases are normalized deterministically by removing vendor noise, board-partner prefixes, punctuation differences, and safe suffix variations without collapsing distinct models.
* Exact normalized canonical/alias matches may be automatically verified.
* Ambiguous/fuzzy matches remain `review_required`; AI may not promote them to verified.
* Inventory stores the matched reference ID, catalog version, system-managed score snapshot, match method, confidence, and timestamp.

Score computation must be reproducible:

* Select a reviewed primary benchmark basis per category/catalog version.
* Store the raw benchmark value and its source.
* Apply the catalog version’s fixed normalization factor to create a positive integer SaleAura score.
* Do not renormalize old scores merely because a faster future component is added.
* A higher score always means higher performance within that category/version.

A verified CPU/GPU upgrade requires:

* Both products matched to compatible published catalog versions.
* Replacement score greater than the current score by at least the catalog version’s configured minimum meaningful delta.
* The full resulting build remains compatible, in stock, active, and build-eligible.

A downgrade requires the inverse score relationship and explicit customer intent. If either score is unverified, the product may be offered as an exact/brand/price alternative but must not be labelled a verified upgrade or downgrade.

### Verified Build Generator

Refactor the active tower-build path around a single canonical build model.

Required categories:

* CPU
* Discrete GPU
* Motherboard
* One RAM kit
* One primary SSD/storage product
* PSU
* Case
* Cooling, unless the CPU has a verified included cooler suitable for that CPU

Candidate queries must require:

* Correct owner.
* Active product.
* Stock greater than zero.
* Build eligibility true for the product category.
* Valid price.

Selection order may remain purpose-aware, but hard rules take priority over preference/quality scoring. The generator must:

1. Filter eligible candidate pools.
2. Apply owner inventory, stock, category, and brand constraints.
3. Construct only complete compatible builds.
4. Enforce the requested budget.
5. Rank valid builds by approved purpose weighting and verified CPU/GPU scores.
6. Return a clear no-build reason when no valid build exists.

For an initial request, do not return an over-budget build as though it were acceptable. Return the closest required budget or missing-data explanation and ask the customer to explicitly change the budget.

### Build Modification Service

Replace the current immediate `new_build` behavior with proposal-based behavior.

Supported requests:

* Exact component swap.
* Cheaper alternative.
* Verified CPU/GPU upgrade.
* Explicit downgrade.
* Brand preference.
* Total budget change.

Required categories cannot be removed. The current public `remove_component` behavior must not be reachable for required V1 build categories.

Dependent-change search must find the smallest compatible change set. Typical dependency paths include:

* CPU may require motherboard, RAM, and cooling changes.
* Motherboard may require CPU, RAM, case, storage, and cooling changes.
* GPU may require PSU and case changes.
* PSU may require case compatibility.
* Cooler may require case or radiator compatibility.

The proposal must include:

* Unique proposal ID and expiry.
* Base build ID/version.
* Requested change.
* Primary replacement.
* Dependent replacements.
* Original and proposed component snapshots.
* Price delta and proposed total.
* Stock result.
* Compatibility result/reasons.
* Budget result and whether an explicit budget change is required.
* Performance comparison and verification metadata where relevant.

The session’s current build is unchanged until confirmation.

Confirmation must:

1. Load the pending proposal by session and proposal ID.
2. Check that the proposal targets the current build version.
3. Reload all referenced inventory rows.
4. Recheck active state, stock, eligibility, prices, and performance references.
5. Re-run full compatibility.
6. Require explicit budget approval when the confirmed proposal changes/exceeds the prior budget.
7. Atomically replace the current build, increment its version, and clear the proposal.

If any value changed, return `PROPOSAL_STALE` with a refreshed preview or alternatives. Do not partially apply a dependent set.

### Durable Chat Session

Replace authoritative Flask-memory build state with a Supabase-backed session record. An in-memory cache may remain as a performance optimization only.

Persist:

* Opaque session ID and hashed session secret.
* Shop owner ID.
* Accumulated non-sensitive intent slots.
* Current build snapshot and build version.
* Pending modification proposal.
* Lead-saved flag.
* Last activity and expiry.

Persist structured assistant payloads in chat history so reload can reconstruct cards. Limit retained/replayed history to a safe bounded window.

Session rules:

* A session credential is scoped to one shop owner.
* A session cannot be loaded by ID alone; the secret must match.
* Expired sessions fail safely and begin a new anonymous session.
* Contact details remain in the lead flow and must not be copied into general session logs/state unnecessarily.
* The browser may discard its session credential; no customer account is created.

### Intent, Language, and Response Composition

Update prompt definitions and `IntentResponse` to:

* Route `build_modify`.
* Extract modification category/action/target/brand/budget.
* Detect explicit confirm, alternatives, and cancel only for free-text fallback; card actions remain structured.
* Exclude office/integrated-graphics verified builds.
* Include Cooling in verified tower requirements.
* Return the response language: English, Urdu, or Roman Urdu.

All fixed error/success messages used in critical build, modification, quota, and lead paths must have reviewed translations. OpenAI may compose concise grounded wording in the detected language, but structured values and hard decisions come from deterministic services.

### Product Search and Comparison

Preserve the existing hybrid structured/semantic search, with these mandatory filters:

* Correct owner.
* Active.
* Stock greater than zero for customer recommendations.
* Customer-safe projection only.

Searchable products need not be build-eligible. Comparison must clearly mark missing/unverified specs and must not infer absent data.

### Leads and Notifications

Lead creation remains a server-side service-role operation.

Requirements:

* Validate full name, at least one contact method, and explicit consent.
* Consume the lead quota atomically with lead creation or compensate safely if the insert fails.
* Attach the finalized build snapshot/version when lead capture came from “I want this build.”
* Persist the lead before notification calls.
* Preserve current email and WhatsApp owner notification behavior.
* Notification errors are logged safely and never roll back the valid lead.
* Prevent duplicate lead creation for repeated submission of the same lead-form/session idempotency key.

### Plans, Quotas, and Rate Limits

The active `products` row remains the plan source of truth, with current config values only as a safe fallback.

Quota behavior:

* Inventory quota counts non-deleted owner inventory records consistently; archived records must not be exploitable to bypass the plan unless a future product decision explicitly changes this rule.
* Updates to existing inventory are allowed at the item limit.
* Lead and AI usage use atomic database functions.
* Structured button actions and deterministic server operations do not consume an AI response when no model call occurs.
* AI quota is consumed only for a meaningful model-backed request; failed pre-validation and blocked subscription requests do not consume it.

Replace the owner-only in-memory public-chat limiter with a layered key:

* Shop owner.
* Hashed client network identifier from the trusted proxy boundary.
* Anonymous session.

Use a bounded Supabase-backed time bucket or atomic RPC so one anonymous visitor cannot exhaust access for every customer of the owner. Store no raw IP address.

The shared entitlement resolver must enforce:

* `active`: current trial or verified active paid entitlement; V1 activity proceeds subject to quotas.
* `retained_access`: expired trial or effectively ended/cancelled entitlement; existing approved owner data remains accessible, but public bootstrap and new metered activity are blocked.
* `unavailable`: entitlement state cannot be established safely; fail closed for new metered/public activity and keep billing recovery available.

Cancellation scheduled for period end remains active until the verified effective end. Existing data is never automatically deleted under V1.

## Database Changes

### Migration Strategy

Create an ordered sequence of feature-scoped additive SaleAura V1 migrations. Do not rewrite previously applied migrations.

Each applicable migration must:

* Be safe on both the current checked-in schema and live staging schema.
* Use `IF EXISTS`/`IF NOT EXISTS` where practical.
* Backfill before applying `NOT NULL` or unique constraints.
* Preserve existing UUIDs, inventory, leads, imports, messages, and billing records.
* Add indexes only for defined queries.
* Update `supabase-schema.sql` as the consolidated reference after the applicable additive migration is validated.
* Update `lib/types/database.ts` with the resulting contracts.

### Inventory Columns

Add to `inventory`:

* `sku TEXT`
* `source_type TEXT NOT NULL DEFAULT 'manual'` with allowed values `manual`, `csv`, `google_sheet`
* `source_id UUID NULL`
* `source_reference TEXT NULL`
* `source_row_key TEXT NULL`
* `is_active BOOLEAN NOT NULL DEFAULT true`
* `archive_reason TEXT NULL` with allowed values `manual`, `source_missing`
* `archived_at TIMESTAMPTZ NULL`
* `compatibility_specs JSONB NOT NULL DEFAULT '{}'`
* `compatibility_schema_version TEXT NULL`
* `build_eligible BOOLEAN NOT NULL DEFAULT false`
* `build_ineligibility_reasons JSONB NOT NULL DEFAULT '[]'`
* `eligibility_rules_version TEXT NULL`
* `performance_reference_id UUID NULL`
* `performance_score INTEGER NULL`
* `performance_score_verified BOOLEAN NOT NULL DEFAULT false`
* `performance_catalog_version TEXT NULL`
* `performance_match_method TEXT NULL`
* `performance_match_confidence NUMERIC NULL`
* `performance_matched_at TIMESTAMPTZ NULL`

Backfill every existing SKU with a deterministic value derived from the immutable inventory UUID, then add a case-insensitive unique owner/SKU index.

Add indexes for:

* Owner, active state, category, stock, and build eligibility.
* Owner and source.
* Performance reference.
* Source row lookup.

`performance_score` is system managed. Owner-authenticated direct update policies must not allow clients to assign it through an unrestricted browser update.

### Inventory Sources

Add `inventory_sources`:

* `id UUID PRIMARY KEY`
* `user_id UUID NOT NULL REFERENCES auth.users`
* `source_type TEXT NOT NULL`
* `spreadsheet_id TEXT`
* `worksheet_gid TEXT`
* `worksheet_title TEXT`
* `source_url TEXT`
* `mirror_mode BOOLEAN NOT NULL DEFAULT false`
* `is_active BOOLEAN NOT NULL DEFAULT true`
* `last_sync_started_at TIMESTAMPTZ`
* `last_sync_completed_at TIMESTAMPTZ`
* `last_sync_status TEXT`
* `last_sync_summary JSONB`
* Timestamps

Create a partial unique index allowing only one active `google_sheet` source per owner.

RLS permits an authenticated owner to select/manage only their own source row. Sync execution still occurs server-side.

### Widget Allowed Domains

Add `widget_allowed_domains`:

* `id UUID PRIMARY KEY`
* `user_id UUID NOT NULL REFERENCES auth.users`
* `hostname TEXT NOT NULL`
* `normalized_hostname TEXT NOT NULL`
* `created_at TIMESTAMPTZ`
* `updated_at TIMESTAMPTZ`

Enforce unique `(user_id, normalized_hostname)`. Do not store schemes, paths, query strings, wildcard patterns, or secrets.

RLS permits authenticated owners to select, insert, and delete only their own rows. Anonymous/authenticated direct public reads are not required; widget bootstrap reads through the server boundary.

If a one-time bootstrap nonce is persisted rather than cryptographically self-contained, store only its hash, owner/host binding, expiry, and consumed timestamp. Do not store bearer credentials in plaintext.

### SKU Aliases

Add `inventory_sku_aliases`:

* `id UUID PRIMARY KEY`
* `user_id UUID NOT NULL`
* `inventory_id UUID NOT NULL REFERENCES inventory ON DELETE CASCADE`
* `sku TEXT NOT NULL`
* `normalized_sku TEXT NOT NULL`
* `created_at TIMESTAMPTZ`

Enforce unique `(user_id, normalized_sku)`. SKU update logic must check both current SKUs and aliases in one transaction.

### Performance Catalog

Add `performance_catalog_versions`:

* Category and version key.
* Status: draft or published.
* Benchmark name.
* Benchmark/source description and URLs.
* Fixed normalization method/factor.
* Minimum meaningful upgrade delta.
* As-of date and publication timestamp.
* Licensing/review notes.

Add `component_performance_references`:

* UUID primary key.
* Category: CPU or GPU.
* Manufacturer.
* Canonical model.
* Normalized model.
* Raw benchmark score.
* SaleAura performance score.
* Catalog version foreign key.
* Source URL and source-as-of date.
* Active/verified state.
* Timestamps.

Add `component_performance_aliases`:

* Reference foreign key.
* Category.
* Alias.
* Normalized alias.
* Unique category/normalized-alias constraint.

Seed a reviewed V1 catalog through a versioned migration/data migration. Catalog tables are service-managed; owners and anonymous clients cannot insert/update scores.

### Durable Chat State

Add `chat_sessions`:

* `id UUID PRIMARY KEY`
* `shop_owner_id UUID NOT NULL`
* `session_secret_hash TEXT NOT NULL`
* `accumulated_slots JSONB NOT NULL DEFAULT '{}'`
* `current_build JSONB`
* `current_build_version INTEGER NOT NULL DEFAULT 0`
* `pending_modification JSONB`
* `lead_saved BOOLEAN NOT NULL DEFAULT false`
* `last_activity_at TIMESTAMPTZ`
* `expires_at TIMESTAMPTZ`
* Timestamps

Add owner/session and expiry indexes.

Add `structured_payload JSONB` and optional `session_sequence INTEGER` to `chat_messages` so cards can be rehydrated in order.

Chat sessions and anonymous chat writes must have no direct anon/authenticated table access. Flask uses the server-side service role after validating the opaque session credential.

### Leads

Add:

* `build_snapshot JSONB NULL`
* `lead_form_key TEXT NULL`

Add a uniqueness/idempotency constraint scoped to shop/session/form key where a form key is present.

Enable RLS on `public.leads`. Add owner-scoped authenticated select/update policies as required by the current dashboard. Do not add a public insert policy; the backend service role creates validated leads.

### Public Chat Rate Limit

If no deployment-provided shared limiter exists at implementation time, add `chat_rate_limit_buckets` with:

* Hashed composite key.
* Owner ID.
* Window start.
* Request count.
* Expiry.

Expose only an atomic service-role function. Perform bounded opportunistic cleanup during requests; do not add an autonomous background job.

### Constraints and RLS Hardening

The migration must also:

* Replace broad public inventory SELECT with owner-only direct table access; public customer reads go through server DTO endpoints.
* Remove public SELECT from inventory embeddings.
* Remove unrestricted public insert on `chat_messages`.
* Remove unrestricted public insert/update policies on `payments`; verified server webhook code uses service role.
* Restrict grants on sensitive tables even when RLS is enabled.
* Review exposed `SECURITY DEFINER` functions, revoke unintended anon/authenticated execution, and set a safe fixed `search_path`.
* Keep intentionally public active-plan and widget-configuration reads limited to safe columns/endpoints.

The live staging findings are launch blockers. At minimum, `leads` RLS and sensitive-table policies must be corrected before any public paid launch.

## API Changes

### API Boundary Rules

* Authenticated owner routes derive owner identity from the Supabase server session.
* Public routes accept a public shop identifier but never accept it as authorization for owner operations.
* Flask privileged routes accept requests only from the trusted Next.js server boundary or an equivalent server-to-server credential.
* Request bodies are validated with Zod at Next.js boundaries and Pydantic in Flask.
* Customer responses use allowlisted DTOs.

### Owner Profile and Dashboard APIs

Profile reads/updates may remain server actions or become route handlers, but must share:

* Server-session authentication.
* An allowlisted input schema.
* Owner-scoped persistence.
* Stable validation and conflict errors.

Dashboard routes retain their current paths and return typed owner-scoped payloads. Use `Promise.allSettled` or equivalent deliberate panel handling so a single failed query is represented as unavailable rather than converted silently to a real zero.

### Owner Widget APIs

Keep authenticated customization reads/updates under `/api/widget/customization`, but validate and allowlist fields rather than forwarding arbitrary objects.

Add authenticated allowed-domain capabilities:

* List the owner’s normalized hosts.
* Add one validated exact hostname.
* Delete one owner-scoped hostname.
* Request a short-lived authenticated preview credential.

The owner APIs never return bootstrap signing material or anonymous session secrets.

### Owner Inventory APIs

Preserve current paths where practical to minimize churn, but change their authorization contract.

Required capabilities:

* Authenticated list inventory, including source/archive/eligibility status.
* Authenticated manual create.
* Authenticated edit by inventory ID.
* Authenticated manual archive/reactivate.
* Authenticated CSV preview and commit.
* Authenticated Google connection create/update.
* Authenticated worksheet discovery.
* Authenticated Google preview and manual sync.
* Authenticated product image upload for editable manual/CSV products only.

The API must reject SaleAura edits, SKU changes, archive changes, and Cloudinary image changes for Google-managed products with a stable `SOURCE_MANAGED_READ_ONLY` error and explanatory message.

### Import Result Contract

Return:

* Import job ID.
* Source ID/reference.
* Total rows.
* Inserted.
* Updated.
* Unchanged.
* Auto-archived.
* Reactivated.
* Failed.
* New rows skipped by quota.
* Failed rows with row number, SKU, field, reason code, and safe message.
* Timing/progress fields already used by the UI.

### Public Widget Bootstrap API

Replace the current unauthenticated configuration-only flow with a bootstrap boundary, such as `/api/widget/bootstrap/[user_id]`.

The response for an authorized active widget includes:

* Customer-safe customization.
* Public shop identifier.
* Short-lived signed bootstrap credential.
* Credential expiry.
* Widget URL.

The endpoint must validate browser-provided origin/referrer context against `widget_allowed_domains`, apply a bootstrap rate limit, and reject unauthorized or retained-access stores. It must not return generic fallback customization on failure.

The iframe/session-start endpoint exchanges the bootstrap credential once for the durable anonymous session credential. Chat, history, structured actions, and lead submission require that session credential.

### Public Chat API

Regular request:

```json
{
  "message": "Upgrade the GPU",
  "shop_id": "public-owner-uuid",
  "session_id": "opaque-uuid",
  "session_secret": "opaque-secret",
  "app_type": "web_widget",
  "attribution": {}
}
```

Structured action request:

```json
{
  "shop_id": "public-owner-uuid",
  "session_id": "opaque-uuid",
  "session_secret": "opaque-secret",
  "action": {
    "type": "confirm_build_modification",
    "proposal_id": "uuid",
    "build_version": 3,
    "approve_budget_change": false
  }
}
```

Actions include:

* `confirm_build_modification`
* `show_build_modification_alternatives`
* `cancel_build_modification`
* `start_lead_capture`
* `submit_lead`

Structured actions bypass intent classification unless free text is actually required.

### Customer-Safe Product DTO

Allow only:

* Inventory ID as an opaque action reference.
* SKU where useful to the customer.
* Name.
* Category.
* Brand.
* Price/currency.
* In-stock state or safe stock quantity if approved by existing behavior.
* Image URL.
* Product URL.
* Display-safe specifications.
* Verified compatibility/performance labels only where supported.

Never return owner ID, source internals, embedding content/vector, eligibility diagnostics intended for owners, or service metadata.

### Modification Response Contract

Add a response type such as `build_modification_preview` containing:

* Proposal ID and expiry.
* Base build version.
* Requested change.
* Primary and dependent changes.
* Old/new customer-safe components.
* Price delta/new total.
* Budget state.
* Stock state.
* Compatibility status/reasons safe for customers.
* Performance delta/verification where applicable.
* Allowed actions.

### Error Contract

Every API error must include:

* Stable machine-readable code.
* Safe user-facing message.
* Retryable boolean.
* Trace/reference ID where useful.

Do not expose raw Supabase, OpenAI, Google, SMTP, WhatsApp, Cloudinary, or Polar errors.

## Authentication / Authorization Impact

### Owner Operations

Owner pages remain protected by Supabase Auth and current middleware.

Every owner API must:

1. Load the server-side Supabase session.
2. Reject unauthenticated requests.
3. Derive `owner_id` from `auth.uid()`.
4. Verify the target profile/dashboard/customization/domain/inventory/source/import/lead/payment record belongs to that owner.
5. Ignore or reject a conflicting client-supplied owner ID.

One owner account per business remains unchanged. No staff roles or team authorization model is added.

Trial expiry or effective cancellation does not invalidate owner authentication. Authorization combines identity with the requested capability: retained-data reads remain available, while new metered/public activity requires an active entitlement.

### Anonymous Customers

Customers remain anonymous.

The public shop ID selects the inventory namespace but grants no owner privilege. Public widget bootstrap additionally requires an approved embedding host and active owner entitlement. A high-entropy session ID plus secret, created from a valid short-lived bootstrap credential, authorizes only that anonymous session’s conversation/build state. It does not authorize table access or reveal other sessions.

### Service Role

Service-role credentials remain server-side and are used only for:

* Validated anonymous chat/session writes.
* Lead insertion after consent/quota validation.
* Performance catalog maintenance/matching.
* Import processing after authenticated owner verification.
* Trusted billing webhook writes.

The browser must never receive the service-role key.

## Security Considerations

### Confirmed Live Staging Finding

`public.leads` currently has RLS disabled in live staging. This exposes sensitive lead/contact data to Supabase API roles and is a critical launch blocker. The implementation must enable RLS and add deliberate owner policies in the same migration so access is not accidentally blocked or left open.

### Additional Live Policy Findings

The live policy review also found:

* Full inventory has a public SELECT policy.
* Inventory embeddings have a public SELECT policy.
* Chat messages allow unrestricted public insert.
* Payment insert/update policies are unrestricted.
* Some `SECURITY DEFINER` functions are executable by public roles or have mutable search paths.

The Developer must review and correct these boundaries as part of the PRD’s production-readiness work. The objective is not to hide intentionally public product information; it is to expose only a controlled customer-safe projection through server APIs.

### Public Endpoint Abuse

* Apply request-size and message-length limits.
* Rate limit by owner plus anonymous client/session, not owner alone.
* Validate session/shop binding.
* Validate URLs and reject unsafe schemes.
* Limit import file size, row count, and accepted content type.
* Bound Google/OpenAI/Cloudinary/notification calls with timeouts.
* Keep CORS restricted at the Flask boundary; the hosted Next.js widget/API façade is the public web boundary.
* Mask IDs and contact details in logs.

### Widget Domain Authorization

The existing `host_page_url` and `host_referrer` query values are attribution only and must not authorize widget use because any caller can forge them.

The embedding host is verified at bootstrap from browser request context, then bound cryptographically to the one-time bootstrap credential and resulting anonymous session. Use exact normalized hostname matching; `example.com` must not match `example.com.attacker.test`, and an approved parent does not automatically approve every subdomain.

Bootstrap credentials must be short-lived, audience/purpose scoped, signed with a server-only secret, and protected against replay during session exchange. Durable session secrets are hashed at rest.

### Data Integrity

* Quota checks and consumption are atomic.
* SKU changes and aliases are transactional.
* Mirror archive runs only after a safe complete sync.
* Modification confirmation uses optimistic build versioning.
* Lead submission is idempotent.
* Performance scores are service-managed and traceable.
* Compatibility never treats missing critical data as compatible.

### Secrets

All Supabase, OpenAI, Google, Cloudinary, Polar, ElevenLabs, SMTP, and WhatsApp credentials remain environment variables. No credential or full third-party payload is stored in feature artifacts, logs, or client responses.

### Legal Documentation Boundary

Do not modify `app/privacy-policy`, `app/terms-and-conditions`, `app/refund-policy`, their Markdown/content sources, or other legal-document content during V1. Existing links may remain unchanged.

This architecture does not certify legal sufficiency for public launch. Any required legal review is a separate CEO responsibility and must not be disguised as product implementation.

## Error Handling

### Authentication, Profile, and Dashboard

* OAuth cancellation/provider errors return the owner to a safe authentication state.
* Profile validation returns field-safe messages without leaking Supabase details.
* Session expiry redirects protected pages and returns `401` from APIs.
* Dashboard panel failures are represented explicitly; they are not converted silently into real zero counts.

### Widget Bootstrap and Entitlements

* Unauthorized host returns `WIDGET_DOMAIN_NOT_ALLOWED`.
* Missing trustworthy origin context returns `WIDGET_ORIGIN_UNVERIFIED`.
* Expired/used bootstrap credential returns `WIDGET_BOOTSTRAP_EXPIRED`.
* Expired trial/effective cancellation returns `SUBSCRIPTION_REACTIVATION_REQUIRED`.
* Unsafe entitlement uncertainty returns `ENTITLEMENT_UNAVAILABLE` and fails closed for new public/metered activity.
* These failures must not reveal whether unrelated owner data exists or return fallback customization.

### Inventory

* Invalid rows fail independently without aborting valid rows.
* A complete infrastructure failure marks the import job failed and does not claim success.
* Quota-limited new rows are reported; valid existing-row updates still apply.
* Mirror archive is skipped on source read, parse, or validation incompleteness.
* Ambiguous identity fails safely rather than overwriting.
* Google permission/worksheet errors preserve existing inventory.

### Performance Matching

* Unmatched CPU/GPU remains searchable.
* Ambiguous matches become review-required.
* No verified score or upgrade claim is produced without a published match.
* Catalog unavailability blocks verified CPU/GPU upgrade decisions but does not break ordinary search.

### Builds

* Missing category inventory returns exact missing/ineligible categories.
* Unknown compatibility data returns an unverified-data reason.
* No compatible within-budget result returns a clear budget/inventory explanation.
* A stale proposal is not applied; the customer receives a refreshed preview or alternatives.
* Any dependent-change failure rejects the whole proposal.

### Leads and Notifications

* Invalid/absent consent prevents save.
* Quota exhaustion returns a stable lead-limit message.
* Lead save failure permits retry with the form data still present client-side.
* Notification failure is logged and does not delete/rollback a saved lead.

### External Services

Use bounded retries only for safe idempotent operations. Avoid automatic retries for non-idempotent lead, billing, or inventory writes unless protected by an idempotency key.

## Testing Guidance

The approved architecture requires layered automated coverage and real staging proof. Unit and contract tests provide fast regression feedback; Playwright and the authorized staging Supabase MCP provide the database-backed readiness evidence.

### Python

Use Python’s standard `unittest` and Flask test client for unit-level behavior initially to avoid a new runtime dependency. Flask test-client results are not database-backed readiness proof.

Cover:

* Entitlement resolution for active, retained-access, and unavailable states.
* SKU normalization, alias resolution, legacy backfill, and duplicates.
* Blank-versus-missing import semantics.
* Partial quota imports.
* Mirror archive/reactivation and manual archive precedence.
* Every category eligibility validator.
* Every compatibility pair listed in this architecture.
* Performance canonical/alias/unmatched/ambiguous matching.
* Upgrade/downgrade score rules.
* Complete build generation with included and separate cooling.
* No over-budget initial build without approval.
* Modification preview, dependent changes, cancel, confirm, stale proposal, and sequential changes.
* Lead validation, consent, idempotency, quota, and notification failure.
* AI quota behavior for model-backed versus structured actions.
* Customer-safe DTO projection.

Mocks may be used at unit boundaries for OpenAI, Supabase, Google Sheets, Cloudinary, SMTP, WhatsApp, and Polar. They are not readiness evidence for persistence, authorization, migration, or payment behavior.

### Required Staging and Browser Evidence

Every implemented or repaired feature must include Playwright coverage for its normal journey, valid boundary conditions, relevant invalid/failure/cancelled/unauthorized/quota states, and affected shared-behavior regressions.

Use the connected, authorized non-production Supabase staging project through MCP for database-backed verification, with dedicated test data and safe record-level evidence. Do not use Flask, local, mock, or sandbox databases as proof that SaleAura persistence is ready. Production Supabase remains out of scope until explicitly authorized.

Polar is the only payment provider. Non-production checkout, subscription, webhook, and portal verification uses Polar sandbox and approved test payment methods; no real payment charge is permitted.

### TypeScript/React

Introduce Vitest and React Testing Library as minimal development-only dependencies if component behavior cannot be adequately validated with existing tools. This is specifically approved for:

* Google OAuth callback routing and profile-completion decisions using mocked Supabase boundaries.
* Profile validation and owner-scoped update behavior.
* Dashboard valid-zero, empty, partial-failure, and unauthenticated states.
* Widget customization and exact-host domain management.
* Embed bootstrap success, unauthorized host, absent origin, expired credential, and expired subscription.
* Build modification preview rendering.
* Confirm/alternatives/cancel payloads.
* Google-source read-only inventory controls.
* Eligibility/source/archive indicators.
* Explicit consent validation.
* Session rehydration behavior.
* Voice controls remaining hidden.
* Urdu direction and mobile card states.

Playwright is the required end-to-end framework for feature readiness. Do not introduce an additional end-to-end framework unless the Developer is blocked from validating an acceptance criterion and receives approval.

### Database

Validate on staging:

* Migration on the current live schema.
* Owner profile, customization, and allowed-domain RLS isolation.
* Inventory SKU backfill and uniqueness.
* Source and alias constraints.
* Performance catalog referential integrity.
* Owner RLS isolation.
* Anonymous denial for leads, embeddings, payments, chat state, and raw inventory.
* Service-role success for intended server operations.
* Atomic quota functions.
* Advisor output after migration, with critical findings resolved or explicitly documented.

### Required Commands and Checks

At minimum:

* Python compile check for changed modules.
* Python unit tests.
* `pnpm exec tsc --noEmit`.
* ESLint using a script compatible with the installed Next.js version.
* `pnpm build`.
* Targeted manual Google sign-in/onboarding/profile/dashboard/billing checks.
* Targeted manual embedded-widget checks on an approved host, rejected host, mobile width, and desktop width.

Remove `ignoreBuildErrors` and `ignoreDuringBuilds` only after the application passes the corresponding checks. Do not claim the build is production-ready while errors remain hidden.

## Risks

### Scope and Sequencing

This PRD is a full V1 hardening program, not a small isolated feature. Implementing database, import, build, chat, security, and UI changes in one unreviewed patch would be high risk. The release plan turns the ordered implementation slices below into feature workflows, each with its own required evidence.

### Existing Dirty Worktree

The product repository already contains user-owned deletions, a modified `supabase-schema.sql`, and untracked Supabase files. The Developer must inspect and preserve those changes. No reset, checkout, or unrelated cleanup is allowed.

### Database Drift

Checked-in SQL and live staging policies differ in names/details. The additive migration must be tested against live staging metadata and must not assume the consolidated schema file is exact.

### Catalog Coverage and Licensing

A useful common-desktop CPU/GPU catalog is substantial. Blind scraping, copied datasets, or undocumented benchmark use creates legal and quality risk. Each seed row/version needs traceable reviewed sources, and unmatched inventory must remain honestly unverified.

### Legacy Inventory Quality

Existing text fields may not contain enough structured information to become build-eligible. Backfill may classify many products as searchable but ineligible until owners correct them. The UI and import report must make this visible rather than guessing.

### Compatibility Complexity

Hardware compatibility contains edge cases beyond V1. The engine must implement only the approved tower scope and return “unverified” outside those rules rather than implying universal hardware expertise.

### Session and Privacy

Durable anonymous sessions improve reliability but introduce retention and session-hijacking concerns. Store a hashed secret, bound retention, minimal state, and no unnecessary contact data.

### Widget Domain Enforcement

The current iframe changes the apparent origin of chat requests to SaleAura, so checking the chat request’s `Origin` alone cannot prove the embedding website. Domain validation must happen before iframe creation and be carried through a signed bootstrap/session exchange. A client-supplied page URL is not a safe substitute.

### Type/Lint Debt

Enabling real TypeScript and lint enforcement may reveal unrelated historical errors. Fix issues required to make the V1 paths and production build trustworthy, but do not perform unrelated refactors. Report any genuinely blocking pre-existing debt.

### Deployment Decision Deferred

The architecture improves application-level security and durability but does not select the final hosting topology or perform Replit migration. Final public-launch deployment review remains a separate CEO decision.

### Legal Review Deferred

Legal-document content is locked for V1. Product implementation cannot establish that the existing legal text is sufficient for public paid launch; the CEO must handle that review separately without expanding this implementation scope.

## Out of Scope / Not Implemented

* Customer-facing WhatsApp chat.
* Final production hosting architecture or Replit migration/removal.
* Staff/team accounts.
* Customer accounts.
* Customer checkout, orders, fulfilment, shipping, or customer purchase payments.
* Lead stages or conversion pipeline.
* Self-service account deletion or owner data export.
* SaleAura Platform Operator/CEO dashboard.
* Non-PC retail categories.
* Visible voice input or text-to-speech.
* Office/integrated-graphics verified builds.
* Monitors, peripherals, operating systems, multi-GPU, custom water loops, multi-storage optimization, or multi-RAM-kit optimization.
* Scheduled Google Sheets sync.
* More than one active Google spreadsheet/worksheet per owner.
* Owner-entered performance scores.
* Runtime benchmark scraping.
* Exhaustive historical/laptop/server/workstation/OEM CPU/GPU coverage.
* A replacement owner dashboard; the existing dashboard is hardened in place.
* Changes to legal-document routes or content.
* New pricing tiers.
* RAG or a new semantic-search architecture.
* Autonomous background jobs.
* Unrelated external integrations.

## Implementation Guidance

### Ordered Implementation Slices

1. **Baseline and contract freeze**
   * Record current build/type/lint/Python compile results.
   * Confirm dirty worktree ownership.
   * Add shared canonical domain/status contracts.

2. **Additive database and security migration**
   * Add inventory identity/source/eligibility/performance fields.
   * Add source, alias, catalog, allowed-domain, session, and rate-limit tables.
   * Backfill SKUs.
   * Add lead build/idempotency fields.
   * Correct RLS/grants/functions.
   * Validate live staging before application code depends on new fields.

3. **Owner lifecycle, dashboard, widget setup, and entitlement**
   * Harden Google callback, profile validation, protected owner APIs, and logout.
   * Add typed dashboard partial-failure behavior.
   * Add widget customization validation and exact-host management.
   * Implement signed bootstrap/preview authorization and active/retained/unavailable entitlement handling.

4. **Inventory domain services**
   * Implement canonical parsing, SKU resolution, blank semantics, partial quota behavior, and source provenance.
   * Implement Google connection/worksheet selection, manual sync, mirror archive, and reactivation.
   * Preserve the existing SSE progress contract while extending result counts.

5. **Eligibility and performance**
   * Add category validators and owner-facing reason codes.
   * Seed the reviewed performance catalog.
   * Add deterministic normalizer/matcher.
   * Backfill existing inventory to verified/unverified states without guessing.

6. **Owner inventory API and UI**
   * Enforce server-side authentication/ownership.
   * Add manual create/edit/archive.
   * Enforce Google read-only behavior.
   * Add source, SKU, archive, eligibility, and performance states.

7. **Verified build generation**
   * Replace name-inference authority with structured rules.
   * Add cooling.
   * Enforce active/stock/eligibility/budget.
   * Return customer-safe canonical build snapshots.

8. **Durable chat and `build_modify`**
   * Add session credential/rehydration.
   * Route modification intent.
   * Add proposal, dependency, confirmation, alternatives, cancellation, and sequential changes.
   * Add the widget preview card and structured actions.

9. **Lead, quota, language, and public safety hardening**
   * Attach build snapshots.
   * Require explicit consent.
   * Preserve owner notifications.
   * Correct AI quota timing and public rate limiting.
   * Add reviewed English/Urdu/Roman Urdu behavior.
   * Hide voice controls.

10. **Verification and production-quality gate**
   * Run automated and staging checks.
   * Resolve relevant type/lint/build issues.
   * Confirm RLS and customer-safe projections.
   * Update current implementation documentation without making deployment decisions.

### Likely Existing Files to Change

* `SaleAura-WebApp/backend/api.py`
* `SaleAura-WebApp/backend/schema.py`
* `SaleAura-WebApp/backend/engine.py`
* `SaleAura-WebApp/backend/session_manager.py`
* `SaleAura-WebApp/backend/services/inventory_service.py`
* `SaleAura-WebApp/backend/services/incremental_build_generator.py`
* `SaleAura-WebApp/backend/services/build_modifier.py`
* `SaleAura-WebApp/backend/services/compatibility_validator.py`
* `SaleAura-WebApp/backend/services/subscription_service.py`
* `SaleAura-WebApp/backend/prompts/02_intent_definitions.txt`
* `SaleAura-WebApp/backend/prompts/03_slot_extraction.txt`
* `SaleAura-WebApp/backend/prompts/04_response_format.txt`
* `SaleAura-WebApp/backend/prompts/05_guardrails.txt`
* `SaleAura-WebApp/backend/prompts/rules/compatibility_rules.json`
* `SaleAura-WebApp/app/auth/page.tsx`
* `SaleAura-WebApp/app/auth/callback/route.ts`
* `SaleAura-WebApp/app/profile/page.tsx`
* `SaleAura-WebApp/app/dashboard/page.tsx`
* `SaleAura-WebApp/app/chat-widget/page.tsx`
* `SaleAura-WebApp/app/inventory/page.tsx`
* `SaleAura-WebApp/app/api/dashboard/stats/route.ts`
* `SaleAura-WebApp/app/api/dashboard/recent-leads/route.ts`
* `SaleAura-WebApp/app/api/dashboard/leads-analytics/route.ts`
* `SaleAura-WebApp/app/api/widget/customization/route.ts`
* `SaleAura-WebApp/app/api/widget/config/[user_id]/route.ts` or a safer bootstrap replacement
* `SaleAura-WebApp/app/api/chat/route.ts`
* `SaleAura-WebApp/app/api/parse-csv/route.ts`
* `SaleAura-WebApp/app/api/upload-google-sheet/route.ts`
* `SaleAura-WebApp/app/api/upload-product-image/route.ts`
* `SaleAura-WebApp/app/api/inventory/[user_id]/route.ts` or a safer authenticated replacement
* `SaleAura-WebApp/components/chat/ChatWidget.tsx`
* `SaleAura-WebApp/components/chat/cards/BuildCard.tsx`
* `SaleAura-WebApp/components/chat/cards/LeadCaptureCard.tsx`
* `SaleAura-WebApp/components/chat/cards/index.ts`
* `SaleAura-WebApp/components/AppSidebar.tsx`
* `SaleAura-WebApp/components/DashboardLayout.tsx`
* `SaleAura-WebApp/lib/actions/profile.ts`
* `SaleAura-WebApp/lib/subscription/server.ts`
* `SaleAura-WebApp/lib/types/database.ts`
* `SaleAura-WebApp/public/embed.js`
* `SaleAura-WebApp/supabase-schema.sql`
* `SaleAura-WebApp/next.config.mjs`
* `SaleAura-WebApp/package.json` and `pnpm-lock.yaml` only if the approved frontend test dependencies are added

### Likely New Product Files

Keep additions focused:

* Feature-scoped additive SaleAura V1 SQL migrations, created only when their owning feature requires database changes.
* Focused backend services for import/eligibility/performance/session responsibilities where extracting from `api.py` reduces risk.
* Focused owner widget allowed-domain/bootstrap route or helper files.
* One build-modification preview card.
* Targeted backend and frontend test files.

Do not create extra agents, workflow files, dashboards, unrelated scripts, or deployment tooling.

Do not modify privacy, terms, refund, or other legal-document files.

### Developer Stop Conditions

Return `STATUS: BLOCKED` instead of inventing behavior if:

* Live schema makes the additive migration unsafe without a CEO-approved data decision.
* A trusted/licensable V1 benchmark source cannot be established.
* Existing inventory cannot be backfilled without destructive ambiguity.
* The approved plan values conflict with verified active billing products in a way that could charge customers incorrectly.
* A required compatibility rule cannot be made deterministic from approved data.
* Implementation requires selecting the deferred production deployment architecture.
* A required V1 behavior cannot be implemented without changing locked legal-document content.

## Status

STATUS: ARCHITECTURE_READY
