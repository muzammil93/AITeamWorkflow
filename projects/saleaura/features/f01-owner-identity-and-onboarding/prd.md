# Product Requirements Document

## Feature Name

Owner Identity and Onboarding Delta

## Feature ID and Execution Mode

`F01` — `QA_FIRST` baseline failure followed by delta implementation

## CEO Request

Verify and complete the existing SaleAura V1 owner identity and onboarding implementation for requirements `AUTH-001` through `SEC-AUTH-001`.

Reference: `projects/saleaura/features/f01-owner-identity-and-onboarding/ceo-request.md`.

## Master Requirement References

* `AUTH-001` through `AUTH-006`
* `PROFILE-001` through `PROFILE-003`
* `SEC-AUTH-001`
* Master PRD sections “Owner Authentication and Session,” “Owner Profile and Onboarding,” and “Authentication and Profile” acceptance criteria
* Master architecture “Authentication and Profile,” owner authorization, migration, and testing guidance

## Dependency References

`F00 — Development Safety Baseline` is complete and integrated at product commit `162e947`. Its check, migration, Git, and evidence rules apply.

## Baseline QA Findings

* `F01-QA-001`: Incomplete owners can bypass onboarding.
* `F01-QA-002`: OAuth callback exposes provider errors and does not fail safely on profile persistence errors.
* `F01-QA-003`: Forwarded redirect validation does not fully constrain origin.
* `F01-QA-004`: Browser-controlled profile update can mark invalid data complete.
* `F01-QA-005`: Profile image upload is unauthenticated and under-validated.
* `F01-QA-006`: Auth/profile function and table grants are not explicitly restricted.
* `F01-QA-007`: Required auth/profile behavior lacks automated regression evidence.

## Clarifying Questions

No clarification required. The master PRD and architecture resolve the product behavior needed for this delta.

## Finalized Scope

### In Scope

* Preserve Google OAuth as the only V1 owner sign-in method.
* Provide stable, safe OAuth cancellation/failure recovery without exposing provider, token, database, or internal errors.
* Use exact trusted callback origins and require HTTPS outside explicitly local development.
* Idempotently ensure exactly one owner profile exists for the authenticated Google identity.
* Route incomplete authenticated owners to profile onboarding and complete owners to the dashboard.
* Protect approved owner routes from unauthenticated access and handle expired/invalid sessions safely.
* Preserve secure logout and return to `/auth`.
* Use one server-validated profile contract for first completion and later editing.
* Support the approved fields: full name, business name, authenticated email, phone, WhatsApp, country, city, currency, currency symbol, timezone, phone country code, business address, and optional image.
* Validate required strings, phone values, image data, and country-linked localization consistency before completion.
* Derive owner identity and `profile_completed` on trusted server/database boundaries.
* Keep profile reads/writes owner-scoped and prevent browser callers from persisting arbitrary profile/subscription fields.
* Protect profile-image upload with authentication, image MIME/type, and 5 MB maximum validation.
* Restrict trigger-only/auth-profile database functions and grants to intended roles through an additive migration.
* Add targeted automated tests for the baseline findings and critical F01 paths.

### Out of Scope

* Email/password or any identity provider other than Google.
* Staff/team accounts, invitations, roles, or multiple owners per business.
* Customer accounts.
* Account deletion or owner-data export.
* Billing, plan, entitlement, quota, dashboard-data, inventory, widget-domain, chat, lead, or notification behavior.
* Changing legal content.
* Production deployment or migration.
* Applying a migration to shared staging without successful isolated validation and explicit authorization.
* A broad browser end-to-end framework.

## Assumptions

* Supabase Auth remains the identity provider/session authority.
* The authenticated Google email is authoritative and not owner-editable.
* The existing localization country, city, currency, symbol, timezone, and phone-code datasets remain the approved V1 choices.
* Required text fields are trimmed; whitespace-only values are invalid.
* Phone and WhatsApp values must be plausible bounded phone strings but F01 does not introduce SMS/WhatsApp verification.
* The existing UI statement permitting JPG, PNG, or GIF up to 5 MB is preserved.
* Successful first-time onboarding routes to `/dashboard`; later editing also returns the owner to a protected owner surface without creating a new profile.
* Detailed errors remain in masked server logs; users receive stable recovery messages.
* The additive database migration may be created during implementation but must not be applied to shared staging or production under this request.

## User Stories

* As a new owner, I want Google sign-in to create one SaleAura profile and route me to required onboarding.
* As a returning owner, I want a complete profile to take me directly to my dashboard.
* As an incomplete owner, I want every protected navigation path to return me to onboarding until required data is valid.
* As an owner, I want provider failures to give me a safe retry path without exposing internal details.
* As an owner, I want profile data validated consistently so localization and contact details are trustworthy.
* As an owner, I want to edit the same profile later without duplicates.
* As an owner, I want optional image upload limited to my authenticated session and approved image bounds.
* As the platform owner, I want auth/profile database functions and grants inaccessible to unintended API roles.

## Functional Requirements

### Authentication

1. The sign-in UI exposes Google only.
2. Every callback exit uses a trusted exact origin.
3. Non-local callback origins use HTTPS and approved ports only.
4. Missing code, provider cancellation, exchange failure, invalid session, and profile persistence failure map to stable public recovery codes/messages.
5. Internal error messages, tokens, and contact data are never returned or placed in URLs.
6. Profile creation/restoration is idempotent for concurrent and returning callbacks.

### Routing and sessions

1. Unauthenticated owner-route requests redirect to `/auth`.
2. Incomplete owners may access `/profile` and logout/recovery behavior but are redirected away from dashboard, inventory, billing, and widget-management owner pages.
3. Complete owners visiting `/auth` or `/profile` remain able to edit the profile, while authentication entry routes to `/dashboard`.
4. Invalid/expired sessions fail safely without redirect loops.
5. Logout clears the Supabase session and returns to `/auth`; failure remains visible and retryable.

### Profile contract

1. Reads and mutations derive owner identity from the authenticated session.
2. The browser submits only approved editable fields; email, owner ID, subscription, plan, usage, and completion flags are not accepted as editable input.
3. Required strings are trimmed, bounded, and non-empty.
4. Country must exist in the approved dataset.
5. City must belong to the selected country.
6. Currency, currency symbol, and phone country code must match the selected country.
7. Timezone must belong to the selected country.
8. Phone and WhatsApp values use a bounded allowed-character/length contract.
9. `profile_completed` is derived after successful trusted validation and is false whenever required stored data is invalid.
10. First completion and later editing update the same profile primary key.
11. Default widget customization creation remains idempotent and cannot turn an otherwise successful profile save into duplicate data.

### Image upload

1. Only an authenticated owner may use the profile-image endpoint.
2. Input must be a base64 data URL for JPEG, PNG, or GIF.
3. Decoded payload must not exceed 5 MB.
4. Empty, malformed, non-image, unsupported, and oversized payloads return stable safe errors.
5. External service details remain server-side.

### Database security

1. Use an additive migration; do not rewrite applied SQL.
2. Trigger-only functions use a fixed safe search path and are not executable by `PUBLIC`, `anon`, or `authenticated`.
3. Authenticated browser roles cannot use generic table mutation to bypass the validated profile path.
4. The intended authenticated profile mutation function, if used, validates `auth.uid()` and exact input fields.
5. Owner read isolation remains enforced by RLS.
6. Migration checksum, affected objects, grants, recovery/forward-fix, and local validation evidence are recorded.

### Tests

Targeted automated tests cover:

* Google-only initiation.
* Stable callback error mapping.
* Exact safe-origin handling.
* Profile creation success, duplicate/concurrent behavior, and persistence failure.
* Incomplete/complete/unauthenticated/expired routing.
* Valid and invalid localization/profile inputs.
* Owner identity/field allowlisting.
* Profile image auth/type/size/error behavior.
* Logout success/failure contract where testable.
* Migration/grant assertions without shared-environment mutation.

## Acceptance Criteria

1. `AUTH-001` passes when Google is the only exposed/configured owner sign-in flow.
2. `AUTH-002` passes when tests prove repeated/concurrent callback paths resolve one owner profile and unresolved persistence fails safely.
3. `AUTH-003` passes when incomplete and complete owner routing is enforced on callback and protected navigation.
4. `AUTH-004` passes when unauthenticated and invalid/expired sessions route safely to `/auth` without loops or internal disclosure.
5. `AUTH-005` passes when logout invalidates the session and returns to `/auth`, with a safe failure state.
6. `AUTH-006` passes when callback origins are exactly allowlisted, non-local HTTP/arbitrary ports are rejected, and only stable public errors reach the browser.
7. `PROFILE-001` passes when all approved fields and country-linked values are validated on a trusted boundary and invalid data cannot mark completion.
8. `PROFILE-002` passes when initial completion and later edits update the same owner profile without duplicates.
9. `PROFILE-003` passes when cross-owner access, unauthenticated upload, and arbitrary field mutation tests are denied.
10. `SEC-AUTH-001` passes when the additive migration and executable evidence show intended RLS/grants/function ACLs in an isolated environment.
11. F01-targeted typecheck, tests, lint, and build evidence are recorded honestly.
12. No shared-staging, production, billing, deployment, or legal mutation occurs.

## Risks / Open Questions

* Live Supabase metadata recheck currently requires connector OAuth reauthorization.
* The disposable local Supabase stack was absent during baseline QA. `SEC-AUTH-001` cannot pass until the migration can be validated in isolation.
* Restricting generic profile mutation grants must preserve service-role billing updates and auth-trigger profile creation.
* Existing historical lint debt is broad; this delta fixes F01-targeted lint issues only.
* Real Google provider interaction may remain a manual staging check if an authorized test identity is unavailable; deterministic boundary tests are still required.

## Status

STATUS: PRD_READY
