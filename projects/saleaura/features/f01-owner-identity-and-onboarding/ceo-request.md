# CEO Request

Begin `F01 — Owner Identity and Onboarding` under SaleAura V1 Release Plan version `1.0`.

## Execution Mode

`QA_FIRST`

Validate the existing Google OAuth, owner profile, onboarding, protected-route, logout, and auth/profile database-security implementation before authorizing code changes.

If existing behavior passes, route it through existing-code review without Developer involvement. If baseline QA fails, create a delta PRD and architecture limited to the verified gaps, then implement, retest, and review them through the bounded-repair workflow.

## Authorized Requirements

* `AUTH-001`: Support Google OAuth as the only V1 owner login provider.
* `AUTH-002`: Idempotently create or restore one owner profile per identity.
* `AUTH-003`: Route incomplete profiles to onboarding and complete profiles to dashboard.
* `AUTH-004`: Protect owner routes and handle expired/invalid sessions safely.
* `AUTH-005`: Provide secure logout.
* `AUTH-006`: Preserve safe OAuth redirect-host validation and provider error recovery.
* `PROFILE-001`: Validate and persist approved personal, business, and localization fields.
* `PROFILE-002`: Support later owner profile editing without duplicate records.
* `PROFILE-003`: Restrict profile reads/writes to the authenticated owner.
* `SEC-AUTH-001`: Restrict exposed auth/profile functions and grants to intended roles.

## Constraints

* Preserve Google as the only owner identity provider.
* Do not add email/password login, staff/team accounts, customer accounts, account deletion, or data export.
* Do not change billing, entitlements, inventory, dashboard behavior, widget behavior, legal content, deployment, or unrelated product scope.
* Do not mutate shared staging, production, billing, or deployment systems.
* Use a new additive migration only if baseline QA proves F01 database/security gaps and the migration is validated through the F00 safety gate.
* Preserve integrated F00 at product commit `162e947`.

## Requested Outcome

Deliver evidence-backed F01 verification or the smallest approved delta needed to make owner identity and onboarding ready for dependent feature work.

STATUS: CEO_REQUEST_CREATED
