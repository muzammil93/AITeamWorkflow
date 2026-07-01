# Tech Stack Memory

This file records SaleAura’s audited implementation stack and the approved V1 technical direction.

## Application Shape

SaleAura is a hybrid TypeScript/Python SaaS application:

* Next.js handles the website, protected owner application, server rendering, API routes, Supabase sessions, billing, and backend proxies.
* Flask handles AI chat, inventory ingestion, embeddings, build generation/modification, compatibility validation, lead capture, notifications, and the currently implemented voice endpoint.
* Supabase PostgreSQL provides authentication, application data, RLS, RPC functions, and vector storage.

## Frontend

* Next.js `15.2.4` with App Router and React `19`.
* TypeScript `5` with `strict: true`, `noEmit: true`, and `@/*` aliases.
* Tailwind CSS `3.4`, PostCSS, shadcn/ui, and Radix UI.
* Lucide React, Recharts, Sonner, `next-themes`, React Hook Form, and Zod.
* Current owner surfaces: Google authentication, dashboard, profile, inventory, billing, and widget customization.
* Current customer surfaces: embedded/fullscreen chat, product, comparison, build, clarification, and lead-capture cards.
* Voice recorder and audio components exist in the current code but must be hidden for V1.

## Backend

* Python `3.11` target.
* Flask `3.1` with Flask-CORS.
* Main service entry point: `backend/api.py`, currently listening on port `8000`.
* Next.js API routes proxy selected chat, upload, inventory, and text-to-speech requests through `BACKEND_URL`.
* Pydantic models define AI intent and structured response contracts.
* Current services cover inventory search, subscriptions, build generation/modification, and deterministic compatibility validation.
* CSV ingestion uses pandas.
* Google Sheets ingestion uses gspread and Google service-account credentials.
* Existing upload progress uses Server-Sent Events.

## Supabase — Live Audited State

The live staging project currently contains:

* `profiles`
* `inventory`
* `inventory_embeddings`
* `chat_messages`
* `leads`
* `chat_widget_customization`
* `payments`
* `products`
* `inventory_import_jobs`
* `billing_webhook_events`
* `fx_rates`

Current extensions include `pgvector` and `pg_trgm` in the public schema. Ten migrations are registered, ending with `db_drift_reconciliation_subscription_followup`. No Supabase Edge Functions are deployed.

Important live findings:

* `public.leads` has RLS disabled.
* `chat_messages` has an unrestricted public insert policy.
* `payments` has unrestricted public insert and update policies.
* Raw `inventory` and `inventory_embeddings` have public-select policies.
* `count_unique_chat_sessions` and `handle_new_user` are publicly executable `SECURITY DEFINER` functions.
* Multiple RLS policies repeatedly evaluate `auth.uid()` per row and need safe performance cleanup.
* The current live inventory schema does not yet provide the complete V1 SKU, source ownership, archive, compatibility, performance-reference, domain-allowlist, or durable-session model.

These findings must be addressed through approved migrations. Do not apply direct production/staging changes outside the workflow.

## Authentication and Owner Boundaries

* Supabase Auth currently uses Google OAuth.
* `@supabase/ssr` manages browser, server, and middleware sessions.
* Middleware protects `/dashboard`, `/profile`, `/inventory`, `/billing`, and `/chat-widget`.
* OAuth callback logic validates redirect hosts, creates a missing profile, and routes incomplete profiles to `/profile`.
* V1 supports one owner account per business.
* Protected routes and server APIs must authenticate the owner and enforce ownership server-side.
* Anonymous widget sessions must remain separate from authenticated owner sessions.

## AI and Recommendation Stack

* OpenAI SDK.
* Current configuration uses `gpt-4o-mini` for structured intent classification and response composition.
* Current embeddings use `text-embedding-3-small` with 768 dimensions.
* Prompt files live under `backend/prompts/`.
* Structured outputs use Pydantic.
* Existing compatibility code uses Python and JSON rules, but V1 requires normalized category-specific data and deterministic verification.
* Existing build state is partly process memory; V1 requires durable anonymous session/build state in Supabase.
* Semantic search may continue for discovery, but it must not decide identity, stock, compatibility, performance, authorization, or quota truth.

## V1 Data and Service Direction

The approved architecture must cover:

* Owner-scoped SKU identity and aliases.
* Manual, CSV, and Google Sheets source metadata.
* One manually synchronized spreadsheet/worksheet connection per owner.
* Manual and mirror archive states.
* Category-specific compatibility specifications and eligibility reasons.
* Curated, versioned CPU/GPU performance references and deterministic aliases.
* Durable anonymous widget sessions and build snapshots.
* Proposal-based build modification.
* Owner-configured widget allowed domains.
* Customer-safe DTOs rather than raw database records.
* Explicit lead consent and protected lead access.

## Billing and Entitlements

* Polar.sh uses `@polar-sh/sdk` and `@polar-sh/nextjs`.
* Canonical endpoints are under `/api/subscription/*`.
* Plans are stored in `products`, with application fallbacks.
* Webhook events are deduplicated through `billing_webhook_events`.
* Quotas cover inventory items, monthly leads, and monthly AI responses.
* V1 post-trial/cancellation behavior keeps owner access to profile, billing, inventory, and existing leads while disabling the widget and new metered activity until access is restored.

## External Services

* OpenAI for chat and embeddings.
* Supabase for PostgreSQL, Auth, RLS, RPC, and pgvector.
* Polar.sh for subscriptions.
* Cloudinary for profile and editable product images.
* Google Sheets API for manual inventory synchronization.
* Gmail SMTP for primary owner lead notifications.
* WhatsApp Cloud API for secondary owner lead notifications.
* ElevenLabs and browser speech APIs exist but are deferred and hidden in V1.

Customer-facing WhatsApp chat and new integrations are out of scope.

## Deployment

Final public-launch hosting, production topology, and legacy deployment removal are deferred until the product is otherwise production-ready.

V1 product work must:

* Avoid adding new hosting-specific dependencies.
* Keep secrets in environment variables.
* Preserve deliberate staging/production Supabase and Polar separation.
* Avoid changing deployment files unless the CEO approves the later deployment phase.

## Testing

* No automated frontend or backend test suite is currently present in the audited working tree.
* `package.json` provides `dev`, `build`, `start`, and `lint`.
* Next.js currently ignores ESLint and TypeScript build errors; V1 must not treat this as correctness.
* A full TypeScript/build check could not be completed during audit because dependencies were not installed.
* Python source syntax parsing passed during the read-only audit.
* V1 requires targeted automated and manual validation for authentication, ownership, profile, dashboard, inventory, widget, compatibility, builds, build modification, leads, billing, quotas, and security boundaries.

## Repository Notes

* JavaScript dependencies are locked with pnpm.
* Python dependencies exist in `requirements.txt` and `pyproject.toml`; keep them synchronized when an approved dependency change is required.
* Do not edit `.next/`, virtual environments, caches, compiled files, or generated dependency output.
* Legal pages and legal-document source content are locked and must not be modified during V1.

## Status

STATUS: TECH_STACK_MEMORY_UPDATED
