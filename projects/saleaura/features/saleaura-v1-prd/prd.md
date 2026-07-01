# Product Requirements Document

## Feature Name

SaleAura V1 Production-Ready Product Requirements

## CEO Request

Create a PRD for SaleAura V1 that documents both the current product state and the target production-ready product.

SaleAura V1 is a public paid launch product for custom PC builders and PC component businesses. The PRD must preserve the locked decisions from CEO discussion, including inventory rules, category-wise PC compatibility eligibility, `build_modify`, the CPU/GPU performance reference catalog, multilingual widget support, fixed subscription plans, and deferred items.

This PRD is limited to product requirements. It does not implement code, database migrations, architecture, workflow automation, or deployment changes.

## Clarifying Questions

No clarification required.

## Finalized Scope

### In Scope

* Document the current SaleAura product state at a product-requirements level.
* Define target SaleAura V1 behavior for public paid launch.
* Keep SaleAura focused on PC component stores and custom PC builders.
* Support one owner account per business for V1.
* Support anonymous customer conversations through the embedded chat widget.
* Define the complete owner journey from marketing page through Google sign-up/sign-in, onboarding, profile editing, dashboard, inventory, widget setup, billing, logout, and subscription restriction/recovery.
* Define the dashboard’s required information, loading, empty, and error behavior.
* Define widget branding, preview, installation, and allowed-domain management.
* Support English, Urdu, and Roman Urdu customer conversations.
* Preserve the confirmed Free, Starter, and Growth plans.
* Hide deferred voice input and text-to-speech features from V1 customer-facing usage.
* Preserve existing owner email and WhatsApp lead notification behavior.
* Define inventory source, source reference, SKU, import, edit, image, stock, archive, and partial-import behavior.
* Define Google Sheets V1 behavior with one active connected spreadsheet and worksheet/tab per owner.
* Define PC-specific category-wise compatibility verification and build eligibility.
* Define a SaleAura-maintained CPU/GPU performance reference catalog requirement.
* Define verified GPU-based tower build generation requirements.
* Define `build_modify` requirements, including preview, confirmation, dependent changes, budget handling, stock, and compatibility validation.
* Define chat widget requirements for product search, comparison, build generation, build modification, and lead capture.
* Include production-readiness requirements for security, tests, type safety, reliability, documentation alignment, and data quality.

### Out of Scope

* Customer-facing WhatsApp chat changes.
* Public-launch deployment architecture and migration away from legacy Replit setup.
* Staff/team accounts.
* Customer accounts.
* Customer checkout, ordering, payment for store products, fulfilment, shipping, and order tracking.
* Lead lifecycle stages such as contacted, converted, and lost.
* Self-service account deletion.
* Self-service owner data export.
* A SaleAura Platform Operator or CEO administration dashboard.
* A separate website-implementer stakeholder journey.
* Non-PC retail categories.
* Voice input and text-to-speech in V1 customer-facing usage.
* Office/integrated-graphics-only verified PC builds.
* Peripherals, monitors, operating systems, multi-GPU builds, custom water loops, and advanced multi-storage or multi-RAM-kit optimization.
* New pricing tiers or quota values.
* New AI agents, dashboards, RAG, semantic search architecture changes, autonomous background jobs, or unrelated external integrations.
* Changes to privacy policy, terms and conditions, refund policy, or other legal-document content.
* Code implementation, database schema design, API contracts, or detailed technical architecture.

## Assumptions

* The existing `SaleAura-WebApp/` codebase contains partial implementations for onboarding, inventory, widget chat, build generation, lead capture, billing, and notifications, but these are not production-ready.
* Supabase remains the runtime source of truth for inventory, profiles, leads, plans, usage, and chat-related records.
* Product inventory can originate from manual entry, CSV import, or Google Sheets import/sync.
* SaleAura can maintain its own curated CPU/GPU performance reference catalog for V1, focused on common desktop consumer parts relevant to PC builders.
* A product may be searchable in inventory even if it is not eligible for verified build generation or verified upgrade/downgrade logic.
* Existing legal pages remain unchanged during V1; legal suitability for public launch requires separate CEO/legal review.
* Supabase, Polar, and application logs are sufficient for V1 platform operations; no operator-facing product dashboard is required.
* The Architect will later decide exact database schema, API contracts, validation flow, and migration approach based on this PRD.
* The CEO will review and approve the PRD before architecture and development begin.

## User Stories

* As a PC business owner, I want to sign up or sign in with Google so I can securely access my business workspace.
* As a PC business owner, I want to onboard my business so I can configure SaleAura for my store.
* As a PC business owner, I want to edit my personal, business, localization, and profile-image information so my workspace and customer experience stay accurate.
* As a PC business owner, I want a reliable dashboard showing leads, conversations, inventory, plan, and usage so I can understand current business activity.
* As a PC business owner, I want to upload inventory through CSV or Google Sheets so SaleAura can recommend products I actually sell.
* As a PC business owner, I want every product to have a stable SKU so future imports update the right product instead of creating duplicates.
* As a PC business owner, I want Google Sheets products to stay read-only in SaleAura so my sheet remains the source for those imported fields.
* As a PC business owner, I want imported products to show whether they are eligible for verified PC builds so I know what data needs correction.
* As a PC business owner, I want CPU/GPU products to be matched to SaleAura performance references so upgrade/downgrade suggestions are genuine.
* As a PC business owner, I want to customize and preview my widget, restrict it to approved domains, and copy its installation snippet so it represents my store safely.
* As a PC business owner, I want to understand my plan, quotas, payment history, and access state so I know when to upgrade or reactivate.
* As a customer, I want to search the store’s real inventory so I can find available PC components with accurate price and stock information.
* As a customer, I want to compare PC components so I can decide between relevant options.
* As a customer, I want SaleAura to generate a compatible GPU-based tower build from the store’s inventory.
* As a customer, I want to modify a generated build by asking for cheaper options, upgrades, brand changes, or budget changes.
* As a customer, I want to preview and confirm build changes before SaleAura updates my selected build.
* As a customer, I want SaleAura to explain compatibility issues clearly instead of silently recommending incompatible parts.
* As a customer, I want to submit my lead details with consent when I am interested in a product or build.
* As a business owner, I want captured leads to appear in my dashboard and trigger existing owner notifications.

## Functional Requirements

### Current Product Baseline

1. The current codebase contains substantial implementations for Google authentication, profile onboarding/editing, protected owner pages, dashboard analytics, inventory upload, widget customization, public chat, product comparison, build generation, build modification, lead capture, owner notifications, plan display, Polar billing, and Supabase persistence.
2. Existing implementation does not prove production readiness; V1 must close the audited security, authorization, data-quality, reliability, compatibility, session, UI-contract, and testing gaps.
3. Production behavior must follow this PRD even when the current implementation differs.

### Stakeholders and End-to-End Journeys

1. SaleAura V1 has two product stakeholders:
   * The authenticated PC business owner.
   * The anonymous shopper using that owner’s widget.
2. The owner journey must support:
   * Marketing page to Google sign-up/sign-in.
   * First-time profile completion and returning-owner routing.
   * Profile editing.
   * Protected dashboard usage.
   * Inventory onboarding and ongoing management.
   * Widget customization, preview, domain authorization, and installation.
   * Lead and conversation visibility.
   * Plan, quota, payment, trial, cancellation, and reactivation visibility.
   * Secure logout.
3. The shopper journey must support:
   * Opening the widget on an owner-approved website.
   * Anonymous session creation or safe resumption.
   * Product discovery, comparison, component guidance, verified builds, and build modification.
   * Explicitly consented lead submission with relevant product/build context.
4. The V1 product journey ends at a qualified lead. SaleAura does not complete the shopper’s purchase or order.

### Product Positioning and Launch Scope

1. SaleAura V1 must be positioned specifically for custom PC builders and PC component businesses.
2. SaleAura V1 must not present itself as a general retail AI assistant.
3. SaleAura V1 must support public paid launch readiness at the product-quality level, excluding deployment architecture that is intentionally parked for later discussion.
4. SaleAura V1 must support one authenticated owner account per business.
5. SaleAura V1 must keep customers anonymous and must not require customer accounts.
6. SaleAura V1 customer-facing chat must support English, Urdu, and Roman Urdu.

### Owner Authentication and Session

1. The V1 owner authentication method is Google OAuth through the existing SaleAura sign-up/sign-in entry point.
2. First-time Google authentication must create or restore exactly one SaleAura owner profile for the authenticated identity.
3. An owner whose required profile is incomplete must be routed to profile onboarding.
4. An owner whose required profile is complete must be routed to the protected dashboard.
5. Returning authenticated owners must not be forced through onboarding again unless required profile data becomes incomplete.
6. Unauthenticated users attempting to access owner pages must be redirected to authentication.
7. Authentication cancellation, provider errors, invalid callbacks, and expired sessions must show safe recovery behavior without exposing tokens or internal errors.
8. Logout must terminate the SaleAura session and return the user to a public/authentication surface.
9. V1 must not introduce email/password login, additional identity providers, staff invitations, or team membership.

### Owner Profile and Onboarding

1. First-time onboarding and later profile editing must use the same persisted owner profile.
2. Profile behavior must support:
   * Full name.
   * Shop/business name.
   * Email from the authenticated identity.
   * Phone number and country code.
   * WhatsApp number.
   * Country and city.
   * Currency and currency symbol.
   * Timezone.
   * Business address.
   * Optional profile/business image.
3. Required fields must be validated before onboarding is marked complete.
4. Country-dependent city, currency, timezone, and phone values must remain internally consistent.
5. Saving must provide clear success, validation, loading, and recoverable error states.
6. Owners must be able to return and edit supported profile fields without creating a duplicate profile.
7. Profile changes must not grant access to another owner’s records or expose owner data publicly.

### Owner Dashboard

1. The dashboard must be authenticated and owner-scoped.
2. It must show accurate, clearly labelled information for:
   * Current monthly leads and plan limit.
   * Chat/conversation activity.
   * Inventory totals and relevant stock state.
   * Current plan/subscription status.
   * Recent leads.
   * Lead activity over time using the existing analytics scope.
3. Dashboard numbers must come from protected server-side owner-scoped queries and must not trust a client-supplied owner ID.
4. Dashboard navigation must provide access to profile, inventory, chat widget, billing, and logout.
5. The dashboard must provide usable loading, empty, partial-failure, and error states.
6. A failure in one dashboard panel must not silently present fabricated zero values as confirmed business data.
7. Lead stages, conversion tracking, pipeline management, and an operator dashboard are not part of V1.

### Plans and Usage

1. SaleAura V1 must preserve these plans:
   * Free: 30-day trial, 100 inventory items, 25 leads/month, 500 AI responses/month.
   * Starter: $19/month, 500 inventory items, 150 leads/month, 2,000 AI responses/month.
   * Growth: $49/month, unlimited inventory items, 600 leads/month, 8,000 AI responses/month.
2. Plan limits must apply to inventory item creation, monthly leads, and monthly AI responses.
3. Existing inventory updates must be allowed even when new item insertion is limited by plan quota.
4. The product must avoid promising unsupported plan behavior or unapproved price changes.
5. Billing must show the owner’s current plan, quota usage, available plans, subscription state, and existing payment history.
6. Paid checkout must use the existing Polar subscription direction and must not grant paid access from an unverified browser response.
7. After trial expiry or the effective end of a cancelled subscription:
   * The owner retains access to profile, billing, inventory, and existing lead data.
   * The embedded widget and new metered activity are disabled.
   * Existing business data is not automatically deleted.
   * Successful reactivation restores eligible V1 activity without requiring inventory re-creation.
8. V1 does not provide self-service account deletion or owner data export.

### Inventory Sources and Source References

1. SaleAura must track the source of each inventory product: manual, CSV, or Google Sheets.
2. SaleAura must track enough source reference information to safely update imported products on future imports/syncs.
3. Source references must help prevent duplicate products when the same source row is imported again.
4. Google Sheets products must be read-only inside SaleAura for V1.
5. CSV-imported and manually created products must be editable inside SaleAura.
6. When editing is disabled for Google Sheets products, SaleAura must show a clear owner-facing explanation.

### SKU and Product Identity

1. Every product must have a unique SKU within the owner’s inventory.
2. Existing products without SKUs must receive stable generated legacy SKUs.
3. Owners may replace generated legacy SKUs with unique custom SKUs.
4. SKU changes must preserve the same product record and must not break product history or future matching.
5. Product identity and deduplication must not rely only on loose name/category/brand matching.

### Import and Sync Behavior

1. CSV import must remain supported.
2. Google Sheets import/sync must remain supported.
3. Google Sheets V1 must support one active connected spreadsheet and one active worksheet/tab per owner.
4. Google Sheets sync must be manual for V1.
5. When an imported cell is blank, SaleAura must clear the existing corresponding value.
6. Missing products must be archived only when explicit mirror mode is enabled.
7. Products auto-archived by mirror-mode sync must reactivate if they return to the sheet.
8. Products manually archived by the owner must remain manually archived even if they return to a sheet.
9. Partial-import behavior must remain: update existing products, insert only permitted new products, and provide a failed-row report.
10. Zero-stock products must remain visible in the owner dashboard.
11. Zero-stock products must be hidden from customer-facing product recommendations and verified builds.
12. Product images must support imported URLs.
13. Products editable inside SaleAura must support direct Cloudinary image upload.
14. Google Sheets product image changes must be managed through the sheet for V1.

### Category-Wise Compatibility Verification and Build Eligibility

1. Compatibility verification must be category-wise, not a single generic product flag.
2. Each PC component category must define its own required data for verified build eligibility.
3. Products missing required verified data may remain searchable but must not be used in verified PC builds.
4. Products missing required verified data must not be used for verified `build_modify` changes that depend on that missing data.
5. SaleAura must clearly distinguish searchable inventory from build-eligible inventory.
6. Owner-facing inventory UI must show when a product is not eligible for verified builds and why.

Required V1 build categories:

* CPU
* GPU
* Motherboard
* RAM
* Storage
* PSU
* Case
* Cooling, when the selected CPU does not have a verified included cooler

Category-specific verification must cover at least:

* CPU: socket/platform compatibility, supported generation/family where needed, included-cooler status, and power/cooling relevance.
* GPU: physical length, recommended PSU wattage, required power connectors, VRAM, and verified performance score.
* Motherboard: CPU socket/platform support, chipset/generation support where needed, RAM type, form factor, and storage interface support.
* RAM: RAM type, capacity, kit information where needed, and speed where relevant.
* Storage: storage type, storage interface, form factor where relevant, and capacity.
* PSU: wattage, PSU form factor, efficiency where displayed, and connector availability.
* Case: supported motherboard form factors, supported PSU formats, max GPU length, CPU cooler clearance, and radiator support where relevant.
* Cooling: cooler type, supported CPU sockets, physical clearance or radiator format, and cooling suitability.

### CPU/GPU Performance Reference Catalog

1. SaleAura V1 must maintain a CPU/GPU performance reference catalog in Supabase.
2. The catalog must cover common desktop consumer CPUs and GPUs relevant to custom PC builders.
3. The catalog does not need to cover every historical, laptop, server, workstation, OEM-only, or obscure component for V1.
4. Imported CPU/GPU products must be normalized and matched against the reference catalog when possible.
5. A confidently matched CPU/GPU product must receive a verified SaleAura performance score.
6. An unmatched CPU/GPU product must keep a blank or unverified performance score.
7. Unmatched CPU/GPU products may remain searchable.
8. Unmatched CPU/GPU products must not be used for verified upgrade/downgrade decisions.
9. Owners must not manually enter arbitrary performance scores for V1.
10. SaleAura performance scores must be traceable to curated, trusted benchmark-based references.
11. SaleAura must not rely on AI-only guessing to assign verified performance scores.
12. Higher performance scores must consistently represent better category-specific performance.

### Verified Build Generation

1. SaleAura V1 must generate verified GPU-based tower PC builds for gaming, editing/content creation, and general performance use cases.
2. A verified V1 build must include:
   * CPU
   * Discrete GPU
   * Motherboard
   * One RAM kit
   * One primary SSD/storage item
   * PSU
   * Case
   * Valid CPU cooling solution
3. A CPU cooling solution may be satisfied by:
   * A verified CPU included cooler, or
   * A compatible cooler inventory item.
4. Verified builds must use only active, in-stock, customer-visible, build-eligible products.
5. Verified builds must not silently include products with unknown critical compatibility data.
6. Verified builds must validate compatibility deterministically rather than relying on AI judgment.
7. Verified builds must stay within the customer’s stated budget unless the customer explicitly approves a budget change.
8. Verified builds must show clear total price and component breakdown.
9. SaleAura must clearly explain when it cannot generate a verified build due to missing data, stock, budget, or compatibility limitations.

### Build Modification

1. `build_modify` is required for V1.
2. `build_modify` must operate on the latest generated or confirmed build in the active customer session.
3. `build_modify` must support:
   * Exact component swaps when requested.
   * Cheaper alternatives.
   * Genuine upgrades.
   * Downgrades when explicitly requested.
   * Brand preference changes.
   * Total budget changes.
4. `build_modify` must not remove required V1 build components.
5. If a requested change requires dependent changes, SaleAura must show those dependent changes explicitly.
6. Dependent changes must require customer confirmation before the active build is updated.
7. The original build must remain unchanged until the customer confirms the modification.
8. Each modification preview must show:
   * Original component.
   * Replacement component.
   * Dependent changes, if any.
   * Price difference.
   * New total price.
   * Stock status.
   * Compatibility result.
   * Budget impact.
9. SaleAura must provide customer actions for confirming changes, seeing alternatives, or cancelling.
10. Sequential modifications must be supported within the same active session.
11. `build_modify` must not reserve inventory stock.
12. If stock changes or data becomes stale, SaleAura must revalidate before confirmation.
13. “Upgrade” and “downgrade” decisions for CPU/GPU must use verified performance scores.
14. If verified performance data is missing, SaleAura must not claim that a CPU/GPU replacement is a verified upgrade or downgrade.

### Chat Widget

1. The embedded chat widget must support product search grounded in the owner’s inventory.
2. The widget must support product comparison grounded in the owner’s inventory.
3. The widget must support component information answers without fabricating product availability, prices, stock, or compatibility.
4. The widget must support verified build request flows.
5. The widget must support `build_modify` preview and confirmation flows.
6. Build and modification cards must be clear on mobile embedded views.
7. Product and build cards must show accurate customer-safe stock, price, product image, and product link information when available.
8. The “I want this build” flow must open lead capture and attach the finalized build details.
9. Chat responses must remain concise, helpful, and honest when inventory data is incomplete.
10. Voice input and text-to-speech must be hidden from V1 customer-facing usage.

### Widget Customization, Installation, and Domain Authorization

1. An authenticated owner must be able to configure:
   * Header title.
   * Header subtitle.
   * Primary colour.
   * Welcome message.
   * Bot/assistant name.
   * Bot/assistant image.
2. The owner must see a usable preview before installation.
3. SaleAura must provide an owner-specific installation snippet that does not expose secrets.
4. The owner must be able to maintain an allowed-domain list for the embedded widget.
5. Embedded widget configuration, chat, history, structured actions, and lead submission must be rejected safely when the requesting website is not allowed for that owner.
6. Domain authorization must be enforced by SaleAura services; hiding the widget in browser code alone is insufficient.
7. Domain matching must normalize ordinary URL/host formatting and must not accept arbitrary lookalike domains.
8. Authenticated SaleAura preview/testing must remain possible without weakening production domain enforcement.
9. Customization changes must affect only the authenticated owner’s widget.
10. Widget loading, saving, preview, copy, empty, and error states must be clear and accessible on desktop and mobile.

### Lead Capture and Notifications

1. Lead capture must require customer name, at least one contact method, and consent.
2. Lead capture must preserve quota enforcement.
3. Captured leads must appear in the owner dashboard.
4. Existing owner email and WhatsApp lead notification behavior must remain unchanged.
5. Notification failure must not undo an already saved valid lead.
6. Customer-facing WhatsApp chat changes are not part of this PRD.

### Security, Reliability, and Production Readiness

1. SaleAura V1 must address known security gaps before public paid launch.
2. The known staging issue where `public.leads` has RLS disabled must be fixed during development.
3. Public customer endpoints must expose only customer-safe data.
4. Owner-only operations must require authenticated owner access and ownership validation.
5. Service-role access must remain server-side only.
6. Chat/session behavior must be reliable across page reloads and server restarts where required for V1 user journeys.
7. Rate limiting and quota consumption must not allow obvious abuse or unintended owner-wide denial of service.
8. AI response quota consumption must align with meaningful AI usage.
9. Build, inventory, and lead flows must fail safely with clear user-facing messages.
10. Type safety and lint/build issues hidden by current configuration must not be treated as acceptable production behavior.
11. Documentation must be aligned with current OpenAI-based implementation and approved deployment decisions when those decisions are made.
12. Tests or targeted validation must cover inventory import, product matching, compatibility eligibility, build generation, build modification, lead capture, quotas, and security-sensitive access.
13. The live-audit findings must be resolved before public paid launch, including:
   * RLS disabled on `public.leads`.
   * Unrestricted write policies on chat messages and payments.
   * Unintended public access to raw inventory and embedding data.
   * Over-broad execution rights on exposed database functions.
14. Protected dashboard, profile, inventory, customization, billing, and related APIs must authenticate and scope every operation to the owner.
15. Public widget APIs must use customer-safe response fields, allowed-domain enforcement, anonymous-session authorization, rate limiting, and subscription availability checks.
16. Privacy policy, terms and conditions, refund policy, and other legal-document content must remain unchanged during V1 implementation.

## Acceptance Criteria

### Product Scope

* SaleAura V1 is clearly positioned for PC component businesses and custom PC builders only.
* No V1 user-facing flow markets SaleAura as a generic retail assistant.
* Owner accounts are single-owner only.
* Customer accounts are not introduced.
* English, Urdu, and Roman Urdu are supported in customer-facing chat behavior.
* Voice input and text-to-speech are hidden from V1 customer-facing usage.
* The V1 flow ends at qualified lead capture; no customer commerce or fulfilment workflow is introduced.

### Authentication and Profile

* Google sign-up/sign-in supports new and returning owners with safe success, failure, and logout behavior.
* New owners receive one profile and are routed to required onboarding.
* Complete returning owners are routed to the protected dashboard.
* Owner routes reject or redirect unauthenticated access.
* Owners can complete and later edit all supported profile and localization fields.
* Invalid or incomplete required profile data cannot mark onboarding complete.
* Profile reads and writes are restricted to the authenticated owner.

### Dashboard

* Dashboard statistics, recent leads, and lead analytics are authenticated and owner-scoped.
* Lead, chat/conversation, inventory, plan, and usage values are accurately labelled.
* Dashboard loading, empty, partial-failure, and error states do not misrepresent unavailable data.
* Dashboard navigation reaches the approved owner surfaces and supports secure logout.

### Plans

* Free, Starter, and Growth plans match the CEO-confirmed limits and prices.
* Inventory, lead, and AI response quotas are enforced consistently.
* Existing product updates are not blocked solely because new product creation quota is exhausted.
* After trial expiry or effective cancellation, retained owner data remains accessible while the widget and new metered activity are disabled.
* Reactivation restores eligible activity without deleting or rebuilding retained inventory.

### Inventory

* Every product has a unique owner-scoped SKU.
* Existing products without SKUs receive stable generated legacy SKUs.
* Manual, CSV, and Google Sheets products clearly track their source.
* Imported products retain enough source reference data to support future updates without duplicate creation.
* Google Sheets products are read-only in SaleAura and show an explanatory owner-facing message.
* CSV/manual products remain editable in SaleAura.
* Blank imported cells clear corresponding existing values.
* Mirror-mode missing products are archived only when mirror mode is explicitly enabled.
* Auto-archived sheet products reactivate when they return to the sheet.
* Manually archived products do not automatically reactivate from sheet sync.
* Zero-stock products are visible to owners but hidden from customer recommendations and verified builds.
* Partial imports update existing products, insert permitted new products, and report failed rows.

### Compatibility Eligibility

* Build eligibility is evaluated by product category.
* Products missing category-required compatibility data are not used in verified builds.
* Products missing category-required compatibility data remain searchable where appropriate.
* Owners can see why a product is not build-eligible.
* Verified builds use only active, in-stock, customer-visible, build-eligible products.

### Performance Reference Catalog

* SaleAura has a Supabase-backed CPU/GPU performance reference catalog for V1.
* Common desktop consumer CPUs and GPUs relevant to custom PC builders are covered for V1.
* Uploaded CPU/GPU products are normalized and matched to reference rows where possible.
* Matched CPU/GPU products receive verified performance scores.
* Unmatched CPU/GPU products remain searchable but are not used for verified upgrade/downgrade claims.
* Owners cannot manually enter arbitrary performance scores for V1.
* Upgrade/downgrade logic uses verified scores where required.

### Build Generation

* SaleAura can generate verified GPU-based tower builds for approved V1 purposes.
* Every verified build includes CPU, GPU, motherboard, RAM, primary storage, PSU, case, and valid CPU cooling.
* CPU included-cooler status is considered when deciding whether a separate cooler is required.
* Builds are validated for compatibility using deterministic rules.
* Builds stay within budget unless the customer explicitly changes the budget.
* SaleAura explains clearly when it cannot generate a verified build.

### Build Modification

* Customers can modify the latest active build in-session.
* Requested swaps, cheaper options, upgrades, downgrades, brand preferences, and budget changes are supported.
* Required build components cannot be removed.
* Dependent changes are shown before confirmation.
* The active build is not changed until the customer confirms.
* The modification preview shows old component, replacement, dependent changes, price difference, new total, stock, compatibility result, and budget impact.
* Sequential modifications work in the same session.
* Stock and compatibility are revalidated before confirmation.
* Missing verified performance data prevents verified CPU/GPU upgrade/downgrade claims.

### Chat Widget and Leads

* Product, comparison, build, modification, and lead-capture cards use customer-safe inventory data.
* Product and build cards do not fabricate stock, price, images, links, specifications, or compatibility.
* “I want this build” opens lead capture and attaches finalized build details.
* Valid leads require name, contact method, and consent.
* Owner email and WhatsApp lead notification behavior remains unchanged.
* Customer-facing WhatsApp chat changes are not introduced by this PRD.
* Owners can save approved widget branding fields and see a representative preview.
* Owners can copy a non-secret installation snippet.
* Owners can maintain allowed domains.
* Widget configuration, chat, actions, history, and lead submission fail safely on an unauthorized domain.

### Production Readiness

* The known `public.leads` RLS-disabled issue is addressed before public paid launch.
* Owner-only data is protected by authentication and ownership validation.
* Public endpoints expose only intentionally public customer-safe data.
* Implementation includes appropriate targeted tests or documented validation for the PRD requirements.
* No deployment migration is implemented under this PRD unless separately approved later.
* Unrestricted chat/payment writes, unintended raw inventory/embedding exposure, and over-broad database function grants are addressed.
* Legal-document content remains unchanged during V1 implementation.

## Risks / Open Questions

* Benchmark/reference data licensing must be handled carefully. V1 should use a curated SaleAura reference catalog based on trusted sources rather than blind scraping or copied third-party datasets.
* Initial CPU/GPU catalog coverage must be large enough for common desktop PC-builder inventory but should not attempt to cover every historical, laptop, server, workstation, OEM-only, or obscure model before V1 launch.
* Existing inventory may require backfill, normalization, and owner review before products become build-eligible.
* Some current code paths already partially implement build, import, chat, billing, and lead behavior, but production readiness depends on architecture and development hardening.
* Customer-facing WhatsApp chat is intentionally parked and should be revisited separately.
* Public-launch deployment architecture is intentionally parked and should be revisited after product functionality is production-ready.
* Legal documents are locked for V1. Their suitability for public paid launch remains a separate CEO/legal responsibility and cannot be inferred from product implementation.
* Lead stages, self-service account deletion, owner data export, and an operator dashboard are intentionally deferred to V1.5.

## Status

STATUS: PRD_READY
