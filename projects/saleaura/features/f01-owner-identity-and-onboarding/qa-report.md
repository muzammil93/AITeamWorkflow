# QA Report

## Feature ID and Name

`F01 — Owner Identity and Onboarding`

## QA Mode

`EXISTING_CODE`

## Requirement IDs

`AUTH-001`, `AUTH-002`, `AUTH-003`, `AUTH-004`, `AUTH-005`, `AUTH-006`, `PROFILE-001`, `PROFILE-002`, `PROFILE-003`, `SEC-AUTH-001`

## Input References

* `projects/saleaura/features/f01-owner-identity-and-onboarding/ceo-request.md`
* Master SaleAura V1 PRD ending `STATUS: PRD_READY`
* Master SaleAura V1 architecture ending `STATUS: ARCHITECTURE_READY`
* SaleAura V1 Release Plan v1.0
* Shared project, tech-stack, and coding-standards memory
* Existing product code at integrated F00 head `162e947`
* Checked-in consolidated schema and prior read-only live-staging audit memory

## Attempt 1

### Environment

* Date: 2026-07-02 (Asia/Karachi).
* Product branch: `1.0.0/1.0.0_BackednImplementation_v3`.
* Product commit: `162e947`.
* Node.js: `22.13.1`; pnpm: `10.11.1`.
* TypeScript compiler: passed.
* Existing F01-targeted ESLint run: 10 errors and 4 warnings.
* Live Supabase read-only recheck: unavailable because the Supabase MCP requires OAuth reauthorization.
* Production/staging mutation: none.
* Real Google OAuth/browser execution: not performed; no authorized test identity or interactive provider session was available.

### QA Summary

FAIL.

The existing implementation provides Google-only OAuth initiation, a callback, protected-route middleware, owner-scoped profile queries, profile editing UI, and logout. It does not satisfy the complete approved F01 contract.

Baseline failure is driven by unsafe/incomplete onboarding routing, raw provider-error disclosure, browser-controlled profile completion, missing server-side localization/field validation, an unauthenticated profile-image upload endpoint, and unverified/overexposed auth-function grants. Required automated auth/profile evidence is also absent.

This is a QA-first baseline failure and consumes no repair cycle.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Evidence | Command or Procedure |
| --- | --- | --- | --- |
| `AUTH-001` | PASS | `/auth` invokes only `signInWithOAuth({ provider: 'google' })`; no email/password or other provider UI exists. | Static inspection of `app/auth/page.tsx` and auth-related routes. |
| `AUTH-002` | FAIL | Trigger and callback fallback are duplicate creation paths. The fallback handles unique violation, but profile read/create errors still route to `/profile` even when no profile exists. No executable concurrency/retry tests prove exactly-one restoration. | Inspect callback lines 96–148 and `handle_new_user`; attempt live metadata recheck; search for tests. |
| `AUTH-003` | FAIL | Callback routes by `profile_completed`, but middleware redirects every authenticated `/auth` visit to `/dashboard` and allows incomplete owners to access all protected routes directly. | Inspect `lib/supabase/middleware.ts`; compare master routing requirements. |
| `AUTH-004` | FAIL | Middleware refreshes/validates sessions, but unauthenticated protected routes redirect to `/` instead of the auth/recovery surface, and profile completion is not enforced for owner routes. No expired-session tests exist. | Static middleware inspection and test search. |
| `AUTH-005` | PASS | Sidebar logout calls Supabase sign-out, retries once, redirects to `/auth`, refreshes routing, and shows a safe failure toast. | Inspect `components/AppSidebar.tsx` lines 69–98. |
| `AUTH-006` | FAIL | Callback places `exchangeError.message` in the browser query and AuthPage renders it. Error redirects use raw `requestUrl.origin`; forwarded protocol may downgrade to HTTP and trusted hostname matching retains arbitrary forwarded ports. | Inspect callback lines 44–84 and AuthPage error rendering. |
| `PROFILE-001` | FAIL | Completion checks only JavaScript truthiness. Whitespace and malformed phones pass; country/currency/symbol/phone-code combinations can be inconsistent; browser writes directly to `profiles`; no server-side allowlist/schema validates the approved fields. | Inspect profile load/save and localization selects; inspect unused `lib/actions/profile.ts`. |
| `PROFILE-002` | PASS | Existing UI updates the authenticated identity’s existing primary-key row and does not create a second profile during editing. | Inspect profile update query `.eq('id', user.id)` and profile primary key. |
| `PROFILE-003` | FAIL | Table reads/updates are owner-filtered and checked-in RLS is owner-scoped, but the profile image endpoint is unauthenticated and the generic server action accepts arbitrary `Partial<Profile>` fields. Live grants could not be reverified. | Inspect profile page, `lib/actions/profile.ts`, `app/api/upload-image/route.ts`, schema policies, and live-tool auth failure. |
| `SEC-AUTH-001` | FAIL | `handle_new_user` is `SECURITY DEFINER`; checked-in SQL has no explicit revoke from `PUBLIC`, `anon`, or `authenticated`. Prior live audit recorded public executability. Profile grants/function metadata could not be rechecked because MCP OAuth expired. | Schema/grant search and attempted read-only Supabase SQL metadata query. |

### Test Cases and Actual Results

1. TypeScript baseline:
   * Command: `make check-types`.
   * Result: PASS.

2. Targeted lint:
   * Command: `pnpm exec eslint app/auth/page.tsx app/auth/callback/route.ts app/profile/page.tsx app/api/upload-image/route.ts lib/actions/profile.ts lib/supabase/middleware.ts components/AppSidebar.tsx`.
   * Result: FAIL with 10 errors and 4 warnings.
   * Relevant issues include `any`, unused profile state/type, suppressed effect dependency, and middleware unused callback options.

3. Google-only provider:
   * Procedure: search auth initiation and UI for provider/email-password flows.
   * Result: PASS; only Google is exposed.

4. New-owner callback:
   * Procedure: inspect profile lookup, fallback insert, duplicate path, and terminal redirect.
   * Result: FAIL; non-duplicate lookup/insert failure still proceeds to onboarding instead of safe recovery.

5. Incomplete-owner route:
   * Procedure: trace authenticated `/auth` and direct `/dashboard` behavior through middleware.
   * Result: FAIL; both can reach dashboard without checking `profile_completed`.

6. Provider cancellation/error:
   * Procedure: inspect callback query handling and browser display.
   * Result: FAIL; raw Supabase exchange message is surfaced to the user.

7. Redirect-host safety:
   * Procedure: inspect `x-forwarded-host` and `x-forwarded-proto` normalization.
   * Result: FAIL; hostname trust does not constrain forwarded port and accepts HTTP protocol for non-local trusted hosts.

8. Profile completion:
   * Procedure: submit-path inspection with whitespace/mismatched localization values.
   * Result: FAIL; any non-empty strings mark completion, and country-linked values are not validated on the server.

9. Profile image boundary:
   * Procedure: inspect API authentication, payload validation, size/type checks, and errors.
   * Result: FAIL; endpoint has no session check, accepts arbitrary upload input, does not enforce the UI’s stated 5 MB image constraint, and returns third-party error messages.

10. Owner isolation:
   * Procedure: inspect `.eq('id', user.id)`, RLS policies, server action input type, and upload route.
   * Result: partial only; row queries are owner-scoped, but the broader profile mutation surface is not safely bounded.

11. Function grants:
   * Procedure: search checked-in SQL and query live metadata.
   * Result: FAIL; no revoke is checked in, prior audit found exposure, and live recheck was blocked by expired MCP OAuth.

12. Automated tests:
   * Procedure: inspect test discovery and run F00 suite.
   * Result: no F01 auth/profile behavior tests exist; current tests cover only the F00 safety harness.

### Findings

#### `F01-QA-001`

* Requirement ID: `AUTH-003`, `AUTH-004`
* Severity: High
* State: `OPEN`
* Title: Incomplete owners can bypass onboarding
* Reproduction steps:
  1. Authenticate an owner whose `profiles.profile_completed` is false.
  2. Visit `/auth` or request `/dashboard` directly.
  3. Observe middleware routing.
* Expected result: Incomplete owners are routed to `/profile`; complete owners may access the dashboard.
* Actual result: Authenticated `/auth` always redirects to `/dashboard`, and protected routes check only user presence.
* Evidence: `lib/supabase/middleware.ts`.
* Suggested fix direction: Centralize server-side profile-completion routing in middleware/helper logic and test incomplete, complete, unauthenticated, and expired sessions.

#### `F01-QA-002`

* Requirement ID: `AUTH-002`, `AUTH-006`
* Severity: High
* State: `OPEN`
* Title: OAuth callback exposes provider errors and does not fail safely on profile persistence errors
* Reproduction steps:
  1. Call the callback without a valid code or force an exchange/profile query failure.
  2. Inspect redirect query and AuthPage output.
* Expected result: A stable safe error code/message is displayed; internal provider/database details remain server-side; failed profile persistence does not proceed as success.
* Actual result: `exchangeError.message` is sent to the browser, and profile read/insert failures can still redirect to `/profile`.
* Evidence: `app/auth/callback/route.ts` and `app/auth/page.tsx`.
* Suggested fix direction: Use stable public error codes, keep detailed errors in masked server logs, and stop on unresolved profile persistence.

#### `F01-QA-003`

* Requirement ID: `AUTH-006`
* Severity: High
* State: `OPEN`
* Title: Forwarded redirect validation does not fully constrain origin
* Reproduction steps:
  1. Provide a trusted hostname in `x-forwarded-host` with an arbitrary port.
  2. Provide `x-forwarded-proto: http` for a non-local trusted host.
  3. Inspect the callback redirect origin.
* Expected result: Redirects use an exact approved origin/protocol/port policy.
* Actual result: Trust compares hostname only, then returns the forwarded host including port and accepts either HTTP or HTTPS.
* Evidence: callback lines 44–67.
* Suggested fix direction: Build an exact allowed-origin set, require HTTPS for non-local hosts, and use the same safe origin for every callback exit.

#### `F01-QA-004`

* Requirement ID: `PROFILE-001`, `PROFILE-003`
* Severity: High
* State: `OPEN`
* Title: Browser-controlled profile update can mark invalid data complete
* Reproduction steps:
  1. Supply whitespace or arbitrary non-empty strings for required fields.
  2. Mix country, currency, symbol, phone code, city, and timezone values.
  3. Submit or call the Supabase update directly with `profile_completed: true`.
* Expected result: A server-owned allowlisted contract validates and normalizes all approved fields and derives completion.
* Actual result: Client truthiness derives completion; the browser directly writes the row; the generic server action accepts arbitrary `Partial<Profile>`.
* Evidence: `app/profile/page.tsx` and `lib/actions/profile.ts`.
* Suggested fix direction: Use a shared typed validator and authenticated server action/RPC with explicit fields, country-linked consistency checks, and server-derived completion.

#### `F01-QA-005`

* Requirement ID: `PROFILE-001`, `PROFILE-003`
* Severity: High
* State: `OPEN`
* Title: Profile image upload is unauthenticated and under-validated
* Reproduction steps:
  1. POST JSON with a `file` value to `/api/upload-image` without an authenticated owner session.
  2. Use a non-image or oversized data URL.
* Expected result: Only an authenticated owner may upload a bounded approved image; errors are stable and safe.
* Actual result: No authentication is checked, file type/size is not enforced, and caught third-party errors are returned.
* Evidence: `app/api/upload-image/route.ts`.
* Suggested fix direction: Authenticate server-side, validate a bounded image data URL/MIME/size, and return stable errors.

#### `F01-QA-006`

* Requirement ID: `SEC-AUTH-001`, `PROFILE-003`
* Severity: High
* State: `OPEN`
* Title: Auth/profile function and table grants are not explicitly restricted
* Reproduction steps:
  1. Inspect `public.handle_new_user` function ACL and profile table grants.
  2. Compare checked-in SQL for explicit revokes.
* Expected result: Trigger-only functions are not executable by public API roles, and profile mutation exposure is limited to the intended validated path.
* Actual result: Checked-in SQL contains no revoke for the `SECURITY DEFINER` trigger function; prior live audit recorded public executability.
* Evidence: `supabase-schema.sql`; shared tech-stack memory; live metadata recheck failed with OAuth authorization required.
* Suggested fix direction: Add an additive migration with explicit function/search-path/grant hardening and validate it in the disposable local environment before staging.

#### `F01-QA-007`

* Requirement ID: All F01 requirements
* Severity: Medium
* State: `OPEN`
* Title: Required auth/profile behavior lacks automated regression evidence
* Reproduction steps:
  1. Run current test discovery.
  2. Search for callback, middleware, profile validator/action, upload, and logout tests.
* Expected result: Targeted tests cover success, provider error, incomplete/complete routing, invalid session, idempotent profile creation, owner isolation, validation, upload rejection, and logout.
* Actual result: Only F00 safety-harness tests exist.
* Evidence: `tests/` and F00 baseline commands.
* Suggested fix direction: Add targeted standard-library or framework-native tests per approved architecture without introducing a broad E2E framework.

### Edge Cases

Failed or unverified:

* Missing callback code.
* Provider exchange failure/cancellation.
* Profile lookup failure.
* Concurrent/missing profile creation.
* Incomplete authenticated owner revisiting `/auth`.
* Incomplete owner directly requesting protected pages.
* Expired/invalid session on owner routes.
* Whitespace-only required fields.
* Country/localization mismatches.
* Oversized/non-image profile uploads.
* Direct browser manipulation of completion/profile fields.
* Public execution grants on trigger functions.

### Security and Ownership Checks

FAIL.

Owner row filters and checked-in RLS are positive controls, but they are insufficient while completion is browser-controlled, profile upload is unauthenticated, and function/grant restrictions are absent or unverified.

### Scope Compliance

Existing implementation does not introduce prohibited providers, staff/team accounts, customer accounts, deletion, or export. The required delta can remain within F01.

### Coverage Limitations

* Live Supabase metadata could not be rechecked because connector OAuth authorization is required.
* No authorized Google test identity/browser provider session was available.
* No disposable local Supabase stack is running.
* These limitations prevent a pass; they do not erase the code-inspection failures above.

Attempt Result: FAIL

## Status

STATUS: FAIL
