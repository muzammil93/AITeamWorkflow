# Coding Standards Memory

This file stores coding rules that the Developer and Reviewer must follow.

## General Rules

* Use the smallest correct implementation.
* Do not perform unrelated refactors.
* Do not add features outside the approved PRD.
* Do not change architecture unless explicitly approved.
* Keep code readable and maintainable.
* Prefer clear naming over clever abstractions.
* Add tests when behavior changes.
* Update documentation when needed.
* Preserve existing user changes and the dirty working tree; never revert unrelated files.
* Treat executable code and current configuration as authoritative when documentation is stale.
* Do not edit generated files, `.next/`, virtual environments, caches, compiled files, or dependency output.
* Do not change lockfiles or dependency manifests unless the approved feature requires a dependency change.

## Repository Boundaries

* AI Team workflow files live in `ai-team/`.
* Product code lives in `SaleAura-WebApp/`.
* Feature artifacts must identify every product file changed.
* Keep frontend, Flask backend, SQL migrations, prompts, and shared types synchronized when a contract changes.
* Legal pages and legal-document source content are locked for V1 and must not be modified.
* Deployment files and hosting configuration are outside V1 product implementation unless the CEO separately approves deployment work.

## TypeScript and React Rules

* Follow the Next.js App Router structure under `app/`.
* Use Server Components by default and add `"use client"` only when browser APIs, state, effects, or event handlers require it.
* Keep TypeScript strict and prefer explicit types at API, database, billing, and component boundaries.
* Avoid introducing `any`; if an external payload forces it, validate and normalize the value immediately.
* Use `@/*` imports for project modules.
* Use PascalCase for React components and types, camelCase for variables and functions, and existing route/file naming conventions.
* Reuse existing shadcn/ui and shared layout components before creating new UI primitives.
* Keep authenticated owner pages separate from public widget/customer surfaces.
* Preserve loading, error, empty, mobile, and accessibility behavior when changing UI.
* Do not rely on `ignoreBuildErrors` or `ignoreDuringBuilds`; relevant TypeScript and lint issues must still be addressed.

## Python Rules

* Target Python 3.11 and follow existing PEP 8-style naming: snake_case functions/variables and PascalCase classes.
* Add type hints to new or changed public functions and service boundaries.
* Keep Flask route handlers thin when logic belongs in `backend/services/`.
* Use Pydantic models for structured AI and frontend response contracts.
* Preserve structured logging through the existing debug logger and mask identifiers or personal data.
* Return stable, user-safe errors; keep detailed exceptions in server logs without exposing secrets.
* Keep long-running or network operations bounded with timeouts, batching, pagination, or existing streaming patterns.

## API and Security Rules

* Authenticate protected Next.js API routes with the server Supabase client.
* Validate ownership; never trust a client-supplied `user_id` for an owner-only operation.
* Keep Supabase service-role keys and all other secrets server-side only.
* Use environment helpers instead of duplicating staging/production credential selection.
* Validate all request payloads, file types, external URLs, and third-party responses.
* Preserve safe OAuth redirect-host validation.
* Verify webhook signatures and preserve idempotent webhook handling.
* Do not log credentials, tokens, full contact details, or sensitive customer data.
* Lead capture must require a name, at least one contact method, consent, and successful quota consumption.
* Public endpoints must return only data intentionally approved for public use.
* Do not expose raw inventory rows, embeddings, payment records, webhook events, owner profiles, or lead records through public APIs.
* Public widget requests must verify the configured allowed domain and apply bounded abuse controls.
* Anonymous session identifiers are not authorization; use an opaque secret or equivalent server-verifiable credential.

## Database and Migration Rules

* Use Supabase/PostgreSQL and preserve RLS boundaries.
* Prefer atomic database RPC functions for quota checks and consumption.
* Keep migrations minimal, explicit, idempotent where practical, and safe for already-deployed data.
* Do not rewrite an applied migration unless explicitly approved; add a new migration for new changes.
* Keep `supabase-schema.sql`, migration files, and `lib/types/database.ts` aligned.
* Add indexes only for demonstrated query patterns.
* Preserve pgvector dimension and embedding model compatibility.
* Never expose service-role access to browser code.
* `public.leads` must not remain accessible with RLS disabled.
* Do not use unrestricted `WITH CHECK (true)` policies for backend-only chat or payment writes.
* Restrict RPC execution to the roles that genuinely require it, especially `SECURITY DEFINER` functions.
* Treat applied migrations and the live Supabase schema as audited state; resolve drift with a new reviewed migration.

## SaleAura V1 Product Rules

* Keep the product limited to PC components and custom PC builders.
* Support one owner account per business and anonymous shoppers.
* Keep voice input and text-to-speech hidden.
* Keep customer-facing WhatsApp chat out of scope.
* Keep lead stages, self-service account deletion, owner data export, and the CEO/operator dashboard out of V1.
* Preserve owner access to profile, billing, inventory, and existing leads after trial expiry/cancellation; disable the widget and new metered activity until access is restored.
* Do not implement customer checkout, ordering, fulfilment, shipping, or customer accounts.

## AI and Chat Rules

* Ground product answers in the selected owner's inventory.
* Never fabricate products, stock, prices, specifications, compatibility, or availability.
* Preserve the Pydantic structured-output contract between the OpenAI engine and frontend cards.
* Use deterministic code—not LLM judgment—for hard PC compatibility and quota rules.
* Keep prompt files modular and ordered by their numeric prefixes.
* A prompt or model change requires regression checks across intent classification, slot extraction, multilingual input, product search, comparisons, build requests, and lead capture.
* Do not silently generalize the current PC-specialized AI engine to other product categories without CEO-approved product scope and architecture.
* Preserve the neutral unavailable message when subscription or AI quota access is blocked.
* Use explicit structured actions for build confirmation, alternatives, cancellation, and lead capture; do not rely on interpreting button-label text.
* Keep authoritative session/build/proposal state durable; process memory may only be a cache.
* Support English, Urdu, and Roman Urdu without translating or changing factual inventory data.

## Inventory and PC Compatibility Rules

* Use owner-scoped SKU and approved source references for product identity; never overwrite inventory based only on fuzzy name matching.
* Distinguish a missing import column from an explicitly blank cell.
* Preserve manual archive state separately from mirror-sync archive state.
* Google Sheets products are read-only in SaleAura; manual and CSV products remain editable.
* Zero-stock or archived products must not appear in customer recommendations or verified builds.
* Category-specific normalized data and deterministic code are authoritative for verified compatibility.
* Unknown critical compatibility data must fail verified eligibility rather than pass silently.
* Owners must not enter verified CPU/GPU performance scores.
* CPU/GPU upgrade and downgrade claims require curated, versioned, source-traceable performance references.
* Build modifications must remain proposals until fresh stock, price, budget, performance, and compatibility checks pass on confirmation.

## Billing and Integration Rules

* Use only the canonical `/api/subscription/*` endpoints.
* Keep plans and entitlements DB-driven, with existing config fallbacks.
* Preserve webhook deduplication and cancel-at-period-end behavior.
* Do not grant paid access from an unverified client response.
* Keep inventory, lead, and AI-response quota operations consistent across TypeScript, Python, and SQL.
* External requests must use timeouts and must fail safely without corrupting core records.
* Email and WhatsApp notification failure must not undo an already-saved lead.
* Keep Cloudinary, Google Sheets, ElevenLabs, SMTP, WhatsApp, OpenAI, Polar, and Supabase credentials in environment variables.

## Testing and Verification Rules

* The current repository has no automated test suite; do not claim tests passed when none ran.
* Add targeted tests when behavior changes and an existing test approach is available.
* Do not introduce a new test framework without approved architecture.
* For frontend changes, validate the affected route, responsive states, loading/error states, and relevant build/type checks.
* For backend changes, validate success, invalid input, missing configuration, permission, quota, and external-service failure paths.
* For database changes, validate migration safety, RLS, RPC behavior, and staging/production compatibility.
* For AI changes, use representative deterministic scenarios and record expected versus actual structured outputs.
* Document every command and manual check performed, including failures or checks that could not run.

## Developer Rules

* Read the approved PRD before coding.
* Read the approved architecture before coding.
* Modify only the files required for the approved feature.
* List all changed files in the implementation report.
* Document assumptions clearly.
* Inspect existing patterns and relevant setup documentation before editing.
* Preserve public API and database contracts unless the architecture explicitly changes them.
* If the implementation conflicts with the approved architecture or current repository state, stop with `STATUS: BLOCKED`.

## QA Rules

* Validate only against approved requirement IDs, the applicable PRD/acceptance criteria, architecture, and release-plan scope.
* Do not invent new requirements.
* Report bugs with clear reproduction steps.
* Confirm that claimed tests and checks actually ran.
* Check authentication, ownership, RLS, quotas, and public/private boundaries when relevant.
* Treat regressions hidden by ignored TypeScript or ESLint build settings as real defects.
* In existing-code verification mode, validate scoped existing behavior without requiring an implementation report.
* Preserve prior attempts and stable finding IDs.

## Reviewer Rules

* In changed-code mode, review changed files and directly related logic only.
* In existing-code verification mode, review only the scoped existing code required by assigned requirement IDs.
* Check scope compliance, security, performance, maintainability, and test coverage.
* Do not create new product requirements.
* Verify cross-stack contract changes across Next.js, Flask, Supabase SQL, shared types, and prompts.
* Verify secrets and sensitive data remain server-side and out of logs.
* Confirm production and staging environment behavior remain intentional.
* Preserve prior attempts and stable finding IDs.

## Workflow Evidence Rules

* Every workflow report ends with exactly one machine-readable `STATUS:` line.
* Historical attempts use `Attempt Result:` and must not add extra `STATUS:` lines.
* Product Manager, Architect, Developer, QA, and Reviewer edit only their owned artifact.
* Only the Orchestrator updates project release state.
* Release state summarizes evidence and must never replace PRD, code, QA, review, Git, or migration truth.
* Stop on unexplained artifact, Git, working-tree, migration, or release-state mismatch.

## Status

STATUS: CODING_STANDARDS_UPDATED
