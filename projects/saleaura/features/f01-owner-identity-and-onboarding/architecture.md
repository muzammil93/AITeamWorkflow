# Architecture Document

## Feature Name

Owner Identity and Onboarding Delta

## Feature ID and Execution Mode

`F01` — QA-first baseline failure followed by delta implementation

## PRD Reference

`projects/saleaura/features/f01-owner-identity-and-onboarding/prd.md`, ending `STATUS: PRD_READY`.

## Master Architecture / Requirement References

* SaleAura V1 master architecture:
  * Owner authentication and onboarding data flow
  * Authentication and Profile frontend changes
  * Migration Strategy
  * Owner Operations authorization
  * Security and Testing Guidance
* Release Plan requirements `AUTH-001` through `SEC-AUTH-001`

## Baseline QA Findings

`F01-QA-001` through `F01-QA-007`.

## Dependency Validation

F00 is integrated at `162e947`; its safety commands and migration rules apply. F01 is the only active feature. No F01 product branch exists yet.

## Technical Summary

Harden the existing implementation in place; do not replace Supabase Auth or rebuild the owner UI.

Use five explicit boundaries:

1. `lib/auth/redirect.ts`
   * Pure exact-origin parsing and selection.
   * Fixed production origins plus `AUTH_REDIRECT_TRUSTED_ORIGINS`.
   * Local HTTP permitted only for `localhost`/`127.0.0.1`.
   * Non-local origins require HTTPS and no unapproved forwarded port.
2. `lib/auth/routing.ts`
   * Pure owner-route decision logic for unauthenticated, incomplete, and complete states.
   * Middleware performs authenticated profile-completion lookup and applies the pure decision.
3. `lib/profile/validation.ts`
   * Shared server-safe input type, normalization, validation, and field-safe errors.
   * Uses existing localization datasets for country-linked consistency.
4. `lib/profile/image.ts`
   * Pure image data-URL MIME/base64/decoded-size validation.
5. Trusted server persistence:
   * Cookie-authenticated Supabase client establishes the current user.
   * A server-only admin client writes the exact authenticated profile ID after validation.
   * Browser roles lose generic profile `INSERT`, `UPDATE`, and `DELETE` grants through an additive migration.

The callback uses the authenticated session plus server-only admin client for idempotent missing-profile insertion. It never resets an existing profile. Profile editing calls a server action with explicit editable fields; it does not write Supabase directly from the browser.

## Frontend Changes

### Auth page

* Keep the current Google-only button and presentation.
* Parse only stable callback error codes.
* Map codes to safe actionable messages in a pure helper.
* Never display arbitrary query text.
* Replace `any` error handling with `unknown`.

### Profile page

* Keep the existing form/layout and localization datasets.
* Load owner profile through authenticated server action or a server-provided initial contract; avoid generic browser writes.
* Submit an explicit `OwnerProfileInput` to `saveOwnerProfile`.
* Show field-safe validation errors and preserve entered values.
* Derive country-linked values in UI for convenience, while server validation remains authoritative.
* Disable arbitrary currency/symbol/phone-code combinations or normalize them to the selected country.
* On successful first completion or later save, route to `/dashboard`.
* Remove unused state/types and F01-targeted lint errors.

### Logout

Retain the Sidebar logout behavior. Extract or test a small result contract only if required; do not redesign navigation.

## Backend Changes

### OAuth callback

`app/auth/callback/route.ts`:

1. Compute a safe origin before every redirect.
2. Map missing code, exchange failure, missing user/session, profile read failure, and profile creation failure to stable public codes.
3. Log detailed errors server-side without tokens or full personal data.
4. Read the owner profile with the authenticated server client.
5. If missing, insert through the server-only admin client:
   * `id` from `user.id`
   * `email` from authenticated identity
   * normalized name from trusted user metadata
   * `profile_completed = false`
   * `upsert(..., { onConflict: 'id', ignoreDuplicates: true })`
6. Reread through the authenticated client; stop with safe recovery if unresolved.
7. Redirect complete owners to `/dashboard`, incomplete owners to `/profile`.

Do not pass a service-role client or key to browser code.

### Server-only Supabase admin helper

Add `lib/supabase/admin.ts` with `server-only`, service-role environment selection, disabled session persistence/refresh, and no user-supplied configuration.

### Middleware

* Preserve API bypass; API routes must enforce their own auth.
* Match owner paths on segment boundaries.
* Call `getUser`.
* Unauthenticated owner paths redirect to `/auth?error=session_required`.
* For authenticated owner/auth entry requests, select only `profile_completed`.
* Missing/error profiles fail closed to `/profile` or safe auth recovery without looping.
* Incomplete owners:
  * may access `/profile`;
  * are redirected from `/dashboard`, `/inventory`, `/billing`, and `/chat-widget` to `/profile`.
* Complete owners visiting `/auth` redirect to `/dashboard`.
* Complete owners may access `/profile` for editing.

### Profile server actions

Replace `Partial<Profile>` persistence with:

* `getOwnerProfile()`
* `saveOwnerProfile(input: OwnerProfileInput)`
* Existing `signOut()` may remain but must return/handle safe failure if used.

`saveOwnerProfile`:

1. Authenticates with cookie client.
2. Validates/normalizes through the shared validator.
3. Uses admin client to update the exact authenticated `id` with only approved fields and `profile_completed: true`.
4. Keeps authenticated email authoritative; it is never accepted from input.
5. Treats zero updated rows as a safe persistence failure.
6. Creates default widget customization idempotently only after first valid completion, using `upsert`/conflict-safe behavior. This is preservation of existing behavior, not widget feature expansion.
7. Returns structured field/global errors without raw Supabase text.

### Profile image route

`app/api/upload-image/route.ts`:

1. Authenticate with server Supabase client before parsing/uploading.
2. Apply a conservative JSON/body bound where available.
3. Validate exact JPEG/PNG/GIF data URL and decoded payload at most 5 MB.
4. Upload with a deterministic owner-scoped folder/public identifier strategy that does not expose the owner UUID in responses/logs unnecessarily.
5. Return only stable 400/401/413/500 codes/messages and the resulting HTTPS URL.
6. Use `unknown` exception handling and mask third-party details.

## Database Changes

Create one additive migration under `supabase/migrations/` with a UTC timestamp and F01 name.

The migration must:

* Recreate `public.handle_new_user()` with:
  * `SECURITY DEFINER`
  * `SET search_path = ''`
  * fully qualified objects
  * conflict-safe insert by auth user ID
* `REVOKE ALL ON FUNCTION public.handle_new_user() FROM PUBLIC, anon, authenticated`.
* Preserve trigger ownership/execution behavior.
* Enable RLS on `public.profiles`.
* Recreate owner SELECT policy using `(select auth.uid()) = id`.
* Remove generic authenticated/browser profile insert/update/delete grants:
  * revoke `INSERT`, `UPDATE`, `DELETE` from `anon` and `authenticated`;
  * grant only required `SELECT` to `authenticated`;
  * service role and object owner remain able to perform trusted writes.
* Drop obsolete profile insert/update policies once generic browser mutation grants are removed, retaining deliberate SELECT isolation.
* Preserve existing rows and subscription columns.

Do not alter billing values, other tables, auth identities, or production/staging.

Update `supabase-schema.sql` after isolated migration validation so consolidated SQL matches the intended F01 state.

## API Changes

### Server action contract

Input:

```ts
type OwnerProfileInput = {
  fullName: string
  shopName: string
  phoneNumber: string
  whatsappNumber: string
  country: string
  city: string
  currency: string
  currencySymbol: string
  timezone: string
  phoneCountryCode: string
  address: string
  profilePictureUrl?: string | null
}
```

Result:

```ts
type ProfileActionResult =
  | { ok: true; profileCompleted: true }
  | { ok: false; code: 'UNAUTHENTICATED' | 'VALIDATION_FAILED' | 'PERSISTENCE_FAILED'; fieldErrors?: Partial<Record<keyof OwnerProfileInput, string>>; message: string }
```

No arbitrary database fields cross this boundary.

### Upload response

Success: `{ url: string }`.

Failure: `{ error: { code: string; message: string } }` with stable public values.

## Authentication / Authorization Impact

* Identity remains Supabase Google OAuth.
* Middleware uses authenticated user plus owner profile completion.
* Profile reads remain RLS owner-scoped.
* Trusted server writes use service role only after cookie-session authentication and exact owner ID derivation.
* Generic browser profile writes are revoked.
* Trigger-only function execution is removed from public API roles.
* Image upload requires authenticated session.

## Security Considerations

* Import `server-only` in the admin helper.
* Never log service keys, OAuth codes, tokens, raw provider errors, or full contact data.
* Exact origins, not suffix matching, authorize redirects.
* Reject non-local HTTP and unapproved ports.
* Normalize/trim all profile strings.
* Enforce bounded lengths to limit database/UI abuse.
* Do not trust client completion/email/owner fields.
* Validate base64 before allocating/uploading and reject decoded data over 5 MB.
* Service-role writes always use the current authenticated `user.id`; never accept an owner ID argument.
* Migration revokes must be locally validated to avoid breaking trigger/profile flows.

## Error Handling

Stable auth query codes:

* `missing_code`
* `oauth_failed`
* `session_failed`
* `profile_unavailable`
* `session_required`

AuthPage maps these to fixed messages and discards unknown values.

Profile action returns stable structured errors. Upload returns stable HTTP/error codes. Detailed failures remain masked in server logs.

## Testing Guidance

Add Vitest as the minimal approved TypeScript unit-test runner; React Testing Library is not required if behavior is factored into pure helpers.

Create targeted tests for:

* Redirect origin parsing/allowlist/protocol/port/fallback.
* Public error-code mapping and unknown-code handling.
* Owner route decisions for every auth/completion/path state.
* Profile normalization, required/whitespace/length/phone/country/city/currency/symbol/timezone/phone-code validation.
* Image MIME/base64/size validation.
* Static migration assertions for RLS, revokes, fixed search path, and absence of unrelated table changes.

Where route/service mocking stays small, test callback/profile action/upload orchestration. Otherwise QA supplements pure tests with direct handler/manual procedures and records the limitation.

Required checks:

* `pnpm exec vitest run`
* `pnpm exec tsc --noEmit`
* Targeted ESLint for changed F01 files
* `pnpm build`
* Python/F00 regression checks
* Isolated migration application and SQL ACL/RLS verification

## Migration Validation and Recovery

Before shared staging:

1. Record base `162e947`, migration path, SHA-256, and affected objects.
2. Use a disposable local Supabase workdir/project only.
3. Reconstruct current `profiles` table, policies, trigger, and relevant roles from the checked-in/current audited baseline.
4. Apply the additive F01 migration.
5. Verify:
   * existing profile rows/columns preserved;
   * trigger inserts exactly one row and survives duplicates;
   * `handle_new_user` ACL excludes `PUBLIC`, `anon`, `authenticated`;
   * authenticated SELECT returns own row only;
   * authenticated/anon direct INSERT/UPDATE/DELETE fail;
   * trusted service-role exact-owner update succeeds;
   * unrelated profile subscription fields remain unchanged.
6. Capture schema diff and `supabase db lint --local --fail-on warning`.
7. Do not use `--linked` or remote DB URLs.

Recovery:

* No destructive down migration is assumed.
* If revokes break an intended path locally, revise the unapplied feature migration before approval.
* After any future shared application, use a reviewed additive forward fix to restore only required grants/functions.

## Git / Change Boundaries

Create product branch `feature/f01-owner-identity-onboarding` from integrated F00 head `162e947`.

Expected existing files:

* `app/auth/page.tsx`
* `app/auth/callback/route.ts`
* `app/profile/page.tsx`
* `app/api/upload-image/route.ts`
* `components/AppSidebar.tsx` only if logout lint/test work requires it
* `lib/actions/profile.ts`
* `lib/supabase/middleware.ts`
* `lib/types/database.ts` only if the profile contract changes
* `supabase-schema.sql`
* `package.json`
* `pnpm-lock.yaml`

Expected new files:

* `lib/auth/errors.ts`
* `lib/auth/redirect.ts`
* `lib/auth/routing.ts`
* `lib/profile/validation.ts`
* `lib/profile/image.ts`
* `lib/supabase/admin.ts`
* Focused `tests/f01/*.test.ts`
* One additive `supabase/migrations/*_f01_owner_identity_onboarding.sql`

No backend Python, billing, inventory, dashboard-data, widget-domain, legal, or deployment file changes.

## Risks

* Service-role environment selection must remain server-only and correct for staging/production.
* Revoking generic profile mutation may reveal an undocumented browser write; repository search and local tests must confirm scope.
* Live grants may drift from checked-in SQL; staging remains blocked until reauthentication and explicit authorization.
* Local Docker/Supabase availability may block required migration validation.
* Callback route tests may require careful dependency injection to avoid network calls.

## Out of Scope / Not Implemented

All PRD exclusions, especially other providers, team accounts, billing/entitlement changes, dashboard data, inventory, widget security, production deployment, and legal changes.

## Implementation Guidance

1. Reconfirm clean repositories and create the feature branch.
2. Add pure helpers/tests first.
3. Harden callback and middleware using those helpers.
4. Replace profile browser mutation with validated server action/admin persistence.
5. Protect image upload.
6. Add and locally validate the migration.
7. Update consolidated schema only after validation.
8. Run focused/full checks and record all results.
9. Stop with `STATUS: BLOCKED` if the local migration cannot be executed or if live drift requires a destructive/ambiguous decision.

## Status

STATUS: ARCHITECTURE_READY
