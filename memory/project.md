# Project Memory

This file stores high-level project context for the AI Team workflow.

## Project Name

SaleAura

Repository: `SaleAura-WebApp/`

## Product End Goal

SaleAura is a subscription SaaS product for PC component retailers, custom PC builders, PC-focused e-commerce businesses, and system integrators.

Its end goal is to let a business owner connect real inventory and deploy a branded, inventory-grounded AI sales assistant that helps anonymous shoppers discover components, compare options, generate verified compatible GPU-based tower PC builds, safely modify those builds, and submit consented sales leads.

SaleAura V1 ends at qualified lead generation. Checkout, order processing, payment collection for customer purchases, fulfilment, shipping, and customer accounts are not part of V1.

SaleAura must not present itself as a general retail assistant during V1.

## V1 Stakeholders

### PC Business Owner

The authenticated paying user who:

* Signs up or signs in with Google.
* Completes and edits a localized business profile.
* Manages manual, CSV, and Google Sheets inventory.
* Reviews category-wise build eligibility and CPU/GPU performance matching.
* Customizes, previews, installs, and domain-restricts the chat widget.
* Monitors dashboard activity, conversations, leads, inventory usage, plan usage, and billing.
* Receives the existing email and WhatsApp lead notifications.

V1 supports one owner account per business. Staff and team accounts are deferred.

### Anonymous Shopper

The customer who uses an embedded widget without creating an account. The shopper can:

* Search and compare in-stock PC components.
* Ask PC component questions.
* Request a verified GPU-based tower PC build.
* Preview and confirm safe build modifications.
* Continue a bounded anonymous session across page reloads.
* Submit name, at least one contact method, and explicit consent as a lead.

The widget supports English, Urdu, and Roman Urdu. Customer-facing WhatsApp chat is deferred.

## Owner Journey

1. The owner lands on SaleAura and signs up or signs in through Google OAuth.
2. SaleAura creates or restores the owner profile and routes incomplete profiles to onboarding.
3. The owner completes required personal, business, location, currency, timezone, phone, and WhatsApp details.
4. The owner reaches a protected dashboard showing accurate leads, conversations, inventory, plan, and usage information.
5. The owner creates products manually, imports CSV inventory, or connects one Google spreadsheet and one worksheet for manual sync.
6. SaleAura assigns stable owner-scoped SKUs, tracks product source, validates category-specific specifications, and matches eligible CPUs/GPUs to curated performance references.
7. The owner corrects invalid or incomplete inventory and can see why a product is searchable, customer-visible, or verified-build eligible.
8. The owner customizes widget branding, configures allowed domains, previews the widget, and copies the installation snippet.
9. Anonymous shoppers use the widget; valid leads and conversations become visible to the owner.
10. The owner reviews current plan, quota usage, payment history, and available upgrades through Polar billing.
11. After trial expiry or subscription cancellation, profile, billing, inventory, and existing leads remain accessible, while the widget and new metered activity are disabled until subscription access is restored.

## Shopper Journey

1. The shopper opens the widget on an owner-approved domain.
2. SaleAura creates or resumes an anonymous session scoped to that store.
3. The shopper searches, compares, asks technical questions, or requests a PC build in English, Urdu, or Roman Urdu.
4. SaleAura uses only active, in-stock, customer-visible inventory and never fabricates prices, stock, specifications, products, links, or compatibility.
5. Verified builds include CPU, discrete GPU, motherboard, one RAM kit, one primary storage product, PSU, case, and valid CPU cooling.
6. A requested modification is presented as a preview. The current build changes only after explicit confirmation and fresh stock, price, compatibility, performance, and budget validation.
7. When purchase intent is established, the shopper may submit a consented lead.
8. SaleAura saves the lead and relevant finalized build or product context, then triggers the existing owner notification behavior.

## Locked V1 Plans

* Free: 30-day trial, 100 inventory items, 25 leads/month, 500 AI responses/month.
* Starter: USD 19/month, 500 inventory items, 150 leads/month, 2,000 AI responses/month.
* Growth: USD 49/month, unlimited inventory items, 600 leads/month, 8,000 AI responses/month.

## Locked V1 Product Rules

* Supabase inventory is the runtime source of truth.
* Every product has a unique owner-scoped SKU.
* Existing products receive stable generated legacy SKUs that owners may replace.
* CSV/manual products are editable in SaleAura.
* Google Sheets products are read-only in SaleAura and clearly explain that edits, including image URL changes, belong in the sheet.
* V1 supports one active spreadsheet and worksheet per owner with explicit manual sync.
* Blank imported cells clear existing values; omitted optional columns preserve existing values.
* Missing sheet products are archived only in explicit mirror mode.
* Mirror-archived products reactivate when they return; manually archived products do not.
* Zero-stock products remain visible to owners but are hidden from shoppers.
* Partial imports update existing products, insert permitted new products, and report failed rows.
* Compatibility and verified-build eligibility are category-wise.
* CPU/GPU upgrade and downgrade claims require curated, versioned SaleAura performance references.
* `build_modify` uses preview, dependent-change disclosure, deterministic validation, and explicit confirmation.
* Voice input and text-to-speech remain hidden in V1.
* Widget use is restricted through an owner-configured allowed-domain list.
* Legal documents and legal-document content must not be modified during V1.

## Deferred Beyond V1

The following are deferred to V1.5 or a separately approved phase:

* Staff/team accounts.
* Customer accounts.
* Lead lifecycle stages such as contacted, converted, and lost.
* Self-service account deletion.
* Self-service owner data export.
* Customer-facing WhatsApp chat.
* SaleAura Platform Operator/CEO dashboard.
* Voice input and text-to-speech.
* Non-PC retail categories.
* Office/integrated-graphics verified builds, peripherals, monitors, operating systems, multi-GPU builds, custom water loops, and advanced multi-storage or multi-RAM-kit optimization.

Final public-launch hosting and legacy deployment removal are separate decisions to be handled just before deployment. V1 product implementation must not introduce new hosting dependencies.

## Current Implementation Assessment

The existing product contains substantial implementations for Google authentication, profile onboarding/editing, protected owner pages, dashboard analytics, inventory upload, widget customization, public chat, product cards, comparisons, build generation, build modification, lead capture, notifications, plans, Polar billing, and Supabase persistence.

It is not production-ready. The completed static code and live Supabase audits found gaps in:

* Owner API authorization and ownership checks.
* `public.leads` RLS, which is currently disabled.
* Overly permissive chat-message and payment write policies.
* Public raw inventory and embedding access.
* Allowed-domain enforcement.
* Explicit lead consent.
* Durable anonymous sessions and structured action routing.
* Customer-safe product DTO completeness.
* Category-wise compatibility data and verification.
* Complete cooling-aware build generation.
* Proposal-based `build_modify`.
* CPU/GPU performance references.
* Inventory source/SKU/archive/sync metadata.
* Automated tests, strict type/build enforcement, and current implementation documentation.

These findings are requirements for V1 hardening, not authorization to implement outside an approved PRD and architecture.

## Repository Rules

* AI Team workflow artifacts live under `ai-team/`.
* Production application code lives under `SaleAura-WebApp/`.
* Preserve user-owned uncommitted work.
* Never edit generated output, virtual environments, caches, or compiled files.
* Prefer executable code and the live Supabase schema when stale documentation conflicts with implementation.
* Do not modify legal documentation during V1.
* Do not perform deployment migration until the CEO explicitly approves that separate work.

## Communication and Approval

All AI Team communication must happen through files.

The CEO remains the final approval authority.

## Status

STATUS: PROJECT_MEMORY_UPDATED
