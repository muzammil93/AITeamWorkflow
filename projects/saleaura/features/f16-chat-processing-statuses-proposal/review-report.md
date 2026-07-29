# Review Report

## Feature ID and Name

`F16-STATUS-PROPOSAL` — Backend-Driven Chat Processing Statuses

## Review Mode

`CHANGED_CODE`

## Requirement IDs

`CHAT-STATUS-001` through `CHAT-STATUS-012`

## Input References

* `projects/saleaura/features/f16-chat-processing-statuses-proposal/ceo-request.md`
* `projects/saleaura/features/f16-chat-processing-statuses-proposal/prd.md`
  ending `STATUS: PRD_READY`
* `projects/saleaura/features/f16-chat-processing-statuses-proposal/architecture.md`
  ending `STATUS: ARCHITECTURE_READY`
* `projects/saleaura/features/f16-chat-processing-statuses-proposal/implementation-report.md`
  Attempts 1 and 2, ending `STATUS: IMPLEMENTATION_COMPLETE`
* `projects/saleaura/features/f16-chat-processing-statuses-proposal/qa-report.md`
  Attempts 1 and 2, ending `STATUS: PASS`
* Release-plan change control `CC-002`
* Release-state transitions `T-075` through `T-084`
* `memory/project.md`
* `memory/tech-stack.md`
* `memory/coding-standards.md`
* Initial product commit
  `624bdf5e70f0df88ab3d6d63320b861a05fd6fc6`
* Repair product commit
  `0e204f50216cb3197e08e623b50163040a4da27c`
* Every file changed by those commits and directly related chat, response,
  session, quota, persistence, cart, lead, build, parser, and test code

## Attempt 1

### Review Summary

The approved status vocabulary, genuine backend instrumentation, content-
negotiated JSON/SSE adapters, request-local concurrency repair, frontend stale-
request checks, accessible loader presentation, and unchanged Send-button
spinner are materially aligned with the approved PRD and architecture.

The repair for `F16-STATUS-PROPOSAL-QA-001` is correct. Reporter, intent, and
response-language state now belongs to `ChatRequestContext`, not the cached
owner engine. Independent deterministic tests confirm concurrent requests keep
their reporters, sequences, terminal payloads, intents, and languages separate
without introducing a per-owner lock or head-of-line blocking.

Review nevertheless found one High compatibility defect and one Medium event-
validation defect. The High defect causes an otherwise valid terminal product,
build, comparison, or lead response larger than 16 KiB to be silently discarded
by the frontend SSE parser. The widget then reports a generic failure even
though the backend completed successfully. This violates the architecture's
unchanged terminal-payload contract and blocks approval.

### Scope Compliance

The two product commits stay within the approved source and focused test
boundaries. They introduce no database migration, dependency, package,
external service, deployment, billing, legal, or production mutation. No
timer-based status rotation, polling, WebSocket, persistence, analytics, or
new customer cancellation control was added.

The Send-button spinner JSX remains
`<Loader2 className="w-4 h-4 animate-spin" />` in both widget render branches.
The feature changes only the typing indicator text path and request transport
needed for genuine statuses.

The product working tree contains only the previously disclosed generated
Python bytecode and `tests/e2e/qa-storage-state.json` modifications. Neither
product commit includes them. The changed-file scope is otherwise clean.

### Architecture Compliance

Compliant areas:

* The existing authenticated `POST /api/chat` route remains the only public
  chat path.
* Next.js performs the existing owner-preview or signed-widget-session
  authorization and widget rate limit before proxying.
* Trusted owner and session IDs continue to be server-derived.
* JSON callers retain the existing adapter and payload/status behavior.
* SSE uses a bounded request-owned queue and one worker around the same
  `_execute_chat_request` business path.
* Statuses are emitted only at real search, comparison, build, modification,
  and response-preparation boundaries.
* The six stages and three languages are allowlisted; frontend copy is fixed
  and localized rather than backend free text.
* Disconnect suppresses later status delivery without unsafe thread
  termination or business-operation rollback.
* The concurrency repair preserves cached-engine reuse and parallel work while
  removing newly introduced request-derived shared state.

Noncompliant areas:

* The frontend applies the same 16 KiB logical-frame limit to small control
  frames and to the existing terminal chat payload. This breaks the approved
  requirement that streamed `result.payload` preserve the existing JSON
  response in meaning and shape.
* The backend copies a client-provided `trace_id` into the SSE request ID,
  terminal/status frames, response header, and logs without a bounded
  validation/normalization step, contrary to the architecture's requirement
  to validate event fields and bound frames.

### Code Quality

The request-local `ChatRequestContext`, typed status allowlists, small frontend
parser helper, and single shared chat execution path are clear and focused.
Terminal events are singular, status sequence handling is monotonic, unknown
or stale frontend frames are ignored, and cleanup from an old request cannot
clear a newer request.

The 16 KiB parser rule is not event-aware: `extractSseFrames` silently skips
every oversized complete frame. That behavior is especially unsafe for a
terminal result because the caller cannot distinguish an intentionally rejected
control frame from a successfully completed chat payload that was discarded.

### Security Review

Authentication, widget-session ownership, rate limiting, quota timing, safe
terminal error handling, and server-only credentials remain intact. Status
events contain no message, contact, inventory, owner/session, prompt, provider,
or exception data. Fixed stage/language mappings prevent rendering backend free
text.

The repaired engine no longer permits reporter/language/intent leakage between
concurrent same-owner requests.

`trace_id` remains client-controlled and is newly reused as an SSE protocol
field and Flask response header without length or character validation.
Although it grants no authorization, this allows an authenticated preview or
valid widget session to create unbounded correlation fields and malformed or
oversized protocol/header values. This requires bounded normalization and
contract coverage.

### Performance Review

The repair correctly avoids serializing a cached owner engine, so one shopper
does not wait behind another. The queue size is eight and current genuine paths
emit at most a small number of status frames plus one terminal frame. Client
disconnect stops later status publication while allowing the already-running
bounded business call to finish, as approved.

No new database query, polling loop, durable status store, or frontend timer
was introduced. The worker-per-stream design is the explicitly approved bridge
for the synchronous Flask path.

The unbounded client correlation field is a small avoidable memory/header/log
risk. The terminal-payload finding is a correctness issue rather than a reason
to remove streaming or buffer the whole response in Next.js.

### Maintainability Review

The stage vocabulary is duplicated across Python and TypeScript but is small,
explicit, and contract-tested. The implementation keeps localization in one
frontend table and reporter validation in one backend helper.

The parser needs separate, named limits and behavior for control versus
terminal frames, with a shared documented contract. A single undocumented
`MAX_FRAME_LENGTH` cannot safely represent both tiny status events and the
pre-existing structured chat response.

### Test Evidence Review

QA provides strong staging evidence for genuine pre-terminal status delivery,
multilingual direction, accessibility, desktop/mobile layout, failure and
abort cleanup, no persistence, JSON compatibility, Send-spinner preservation,
search/comparison/build/modification/cart regressions, and the repaired
concurrent-request path. Supabase staging cleanup and no-status persistence
evidence are sufficient for the scoped database boundary.

Independent Reviewer checks:

* `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest -v
  tests.test_f16_processing_status tests.test_engine_build_clarification`
  completed with 7/7 discovered tests passing.
* The full QA backend command completed with 29/29 discovered tests passing.
* Seven function-style search/build-clarification checks, which `unittest`
  does not auto-discover, were invoked directly and all passed.
* `pnpm vitest run tests/f16/processing-status.test.ts` passed 6/6.
* `pnpm exec tsc --noEmit` and `git diff --check` passed.
* An attempted `pnpm exec vite-node` reproduction could not run because
  `vite-node` is not installed; no dependency was added.
* A Node 22 type-stripping reproduction executed the production
  `consumeChatEventStream` helper with a valid 17,000-character terminal
  response. Actual result:
  `The chat response ended before a result was received.`

The current tests use small terminal payloads and therefore do not cover the
allowed large-response boundary. QA's passing result is not sufficient to
override the deterministic contract failure.

### Database / Migration Review

`NOT_APPLICABLE`

No schema, migration, RLS, RPC, database type, persistence, or production data
change is present. Status state remains ephemeral. QA's read-only staging
evidence found no status phrases persisted as chat messages and no leftover
feature fixtures.

### Required Changes

#### F16-STATUS-PROPOSAL-REV-001

* Requirement ID: `CHAT-STATUS-008`
* Category: Correctness / API compatibility
* Severity: High
* State: `OPEN`
* Reason: The frontend must render every valid successful terminal response
  preserved by the existing JSON contract. It currently discards a complete
  SSE frame over 16 KiB and converts the successful chat into a generic
  failure.
* Evidence:
  * `components/chat/processing-status.ts:75` defines one 16 KiB limit for all
    frames.
  * `components/chat/processing-status.ts:103-105` silently skips an oversized
    complete frame.
  * `components/chat/processing-status.ts:205-206` rejects a fragmented frame
    after 32 KiB.
  * `backend/services/customer_response.py:30-36` permits each product to
    include a 2,048-character image URL, notes, specs, and an offer token, and
    search may return ten products. A valid existing payload can therefore
    exceed 16 KiB without violating the customer-safe response contract.
  * Independent production-helper reproduction with a 17,000-character valid
    terminal payload ended with
    `The chat response ended before a result was received.`
* Suggested fix direction: Keep strict small limits for `status` and `error`
  control frames, but define and enforce a separate bounded terminal-result
  limit compatible with the existing maximum chat response contract. Do not
  silently skip a terminal result. Add frontend and backend contract tests for
  a valid result above 16 KiB, a genuinely over-limit result, fragmented
  delivery, and JSON/SSE payload parity.

#### F16-STATUS-PROPOSAL-REV-002

* Requirement ID: `CHAT-STATUS-003`, `CHAT-STATUS-010`
* Category: Security / event-contract validation
* Severity: Medium
* State: `OPEN`
* Reason: SSE protocol fields must be bounded and validated on backend
  emission. A caller-provided `trace_id` is currently accepted without length
  or character validation and reused as `request_id` in frames, a response
  header, thread correlation, and logs.
* Evidence:
  * `app/api/chat/route.ts:59-62` accepts any non-empty string `trace_id`.
  * `backend/api.py:3829-3831` converts that value directly to the stream
    request ID.
  * `backend/api.py:3840`, `3852`, `3866`, `3876`, `3880`, and `3919` reuse it
    in reporter events, terminal events, logs, and `X-Chat-Trace-Id`.
  * `ProcessingStatusReporter` validates stage and language but not the
    request ID supplied at construction.
* Suggested fix direction: Normalize or replace client correlation IDs at the
  trusted Next.js boundary using a documented safe character set and maximum
  length, enforce the same bound before Flask SSE emission, and add tests for
  empty, oversized, and control-character IDs. Preserve request matching and
  do not treat correlation data as authorization.

### Human Action Required

No new CEO product, architecture, database, deployment, billing, or production
decision is required. The Orchestrator should route the two findings to
Developer under bounded repair, then to QA and Reviewer again. Production
deployment remains separately approval-gated.

Attempt Result: CHANGES_REQUIRED — one High terminal-response compatibility
defect and one Medium event-validation defect remain open.

## Attempt 2

### Review Summary

The final bounded repair at frozen product commit
`ec168ac8518a6da7c30f079bb943d6367e6afb84` resolves both stable Reviewer
findings without reopening the previously verified concurrency defect.

`F16-STATUS-PROPOSAL-REV-001` is verified. Status/error control frames retain
the strict 16 KiB limit, terminal result frames have a separate 256 KiB
envelope, valid fragmented results above 16 KiB are consumed, and a true
terminal overflow becomes one explicit customer-safe error instead of being
silently discarded.

`F16-STATUS-PROPOSAL-REV-002` is verified. Next.js and Flask use the same
`^[A-Za-z0-9_-]{1,64}$` correlation-ID contract. Invalid IDs are replaced before
proxying, request tracing, logging, headers, reporter construction, worker
correlation, and SSE emission; valid IDs remain stable for frontend matching.

The final repair introduces no blocking correctness, security, performance, or
maintainability issue. All scoped requirements are ready for final-report
generation.

### Scope Compliance

The repair commit changes exactly seven approved files:

* `app/api/chat/route.ts`
* `backend/api.py`
* `backend/processing_status.py`
* `components/chat/processing-status.ts`
* `tests/f16/chat-request-id.test.ts`
* `tests/f16/processing-status.test.ts`
* `tests/test_f16_processing_status.py`

No database, migration, package, dependency, deployment, billing, provider,
legal, prompt, persistence, business-rule, or production file changed. The
repair does not add UI text, timer rotation, polling, WebSockets, retries, or
new cancellation behavior.

The Send-button component and `ChatWidget.tsx` are not part of the final repair
commit. The previously reviewed
`<Loader2 className="w-4 h-4 animate-spin" />` behavior remains unchanged and
passed focused staging Playwright.

The seven repair files have no uncommitted delta. The only product working-tree
changes are the previously disclosed generated Python bytecode and authorized
Playwright storage state, which remain excluded from the product commits.

### Architecture Compliance

The final implementation now satisfies the approved transport contract:

* The existing authenticated and rate-limited Next.js `POST /api/chat` path
  remains authoritative.
* JSON callers preserve their response behavior.
* SSE status/error control events are capped at 16 KiB.
* SSE terminal results are independently capped at 256 KiB.
* Frontend and backend limits are UTF-8 byte based.
* Valid above-16-KiB terminal results preserve JSON/SSE payload parity.
* A true terminal overflow closes with one safe bounded error frame and no raw
  payload disclosure.
* Correlation IDs are bounded identically at all trusted emission boundaries.
* Reporter, intent, language, queue, and terminal payload remain request-local.
* No per-owner serialization or additional authorization/status path exists.

The architecture's authentication, session, rate-limit, quota, persistence,
cart, lead, search, comparison, build, modification, abort, and no-automatic-
retry constraints remain preserved.

### Code Quality

The two frame classes have explicit named constants and event-aware validation.
Oversized frames no longer disappear silently. Backend serialization converts
only a too-large terminal event into the fixed safe error contract; ordinary
server failures retain their existing safe error path.

The Next.js and Python normalizers are small, readable, and equivalent. The
reporter normalizes again defensively while preserving already-valid IDs.
Request matching therefore remains deterministic across proxy header, status,
error, result, and terminal payload.

The repair keeps the shared execution path and the request-owned
`ChatRequestContext`; no duplicate business path or mutable cached-engine
request state was added.

### Security Review

`F16-STATUS-PROPOSAL-REV-002` is `VERIFIED`.

Empty, 65-character, and control-character IDs are replaced. Valid IDs of the
approved character set remain unchanged. Flask applies normalization before
`start_request_trace`, application logs, response headers, reporter frames, and
worker correlation. Next.js normalizes before forwarding and validates returned
correlation headers.

SSE status/error events still contain only protocol version, bounded request
ID, sequence, allowlisted stage, allowlisted language, or fixed safe error
fields. Oversized terminal content is neither emitted in an event nor included
in the size-error log. No credentials, user messages, contacts, owner/session
IDs, inventory rows, prompts, provider details, or exception text were added to
status events.

Existing owner-preview authentication, signed widget-session validation,
trusted owner/session derivation, widget abuse limit, quota checks, and
customer-safe DTO boundaries are unchanged.

### Performance Review

Control and terminal buffers are finite. The frontend permits one 256 KiB
terminal envelope plus the bounded approved control-event allowance. The
backend queue remains size eight, and the final repair adds no polling,
database work, external call, durable status store, retry, or per-owner lock.

The request-local concurrency repair remains verified, so a concurrent request
does not receive another request's status or wait behind it. Disconnect
semantics remain delivery cancellation only; already-running bounded business
work is not unsafely terminated.

No blocking head-of-line or resource-growth issue remains within the approved
stream design.

### Maintainability Review

The documented 16 KiB and 256 KiB constants make the protocol distinction
clear on both stacks. Focused tests protect fragmented delivery, valid large
results, true overflow, JSON/SSE parity, safe overflow error, and exact request-
ID behavior.

The fixed vocabulary and language mappings are unchanged. The repair does not
broaden the status system or couple it to business-specific response rendering.

### Test Evidence Review

QA Attempt 3 is sufficient and internally consistent. It froze the exact repair
commit, restarted the staging backend from that commit, verified both Reviewer
findings, reran the stable concurrency finding, and covered focused live
status/UI behavior, product-card rendering, verified builds, cleanup, type/
compile checks, and the unchanged Send spinner.

Independent Reviewer checks:

* `PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest -v
  tests.test_f16_processing_status` passed 10/10.
* The two deterministic request-local concurrency tests passed within that
  suite.
* `pnpm vitest run tests/f16/processing-status.test.ts
  tests/f16/chat-request-id.test.ts` passed 13/13.
* `pnpm exec tsc --noEmit` and `git diff --check` passed.
* A Node 22 production-helper reproduction delivered a 24,104-byte fragmented
  Urdu terminal result and returned all 12,000 response characters exactly.
* The same production-helper reproduction rejected a true result overflow with
  `The chat result exceeded the supported stream size.`
* The same reproduction rejected an oversized control event with
  `The chat response stream contained an oversized control frame.`
* Product HEAD equals the frozen commit, and all seven repair files are free of
  uncommitted changes.

Backend tests additionally prove a 20,000-character JSON/SSE terminal payload
match and one safe `CHAT_RESPONSE_TOO_LARGE` event for a genuine backend
overflow. Next.js tests exercise invalid and valid IDs through the actual route;
Flask tests exercise replacement before headers and result frames. Code
inspection confirms the regex and 64-character maximum are identical in both
stacks.

### Database / Migration Review

`NOT_APPLICABLE`

The final repair adds no schema, migration, RLS, RPC, database type, persistence,
analytics, billing, provider, deployment, or production mutation. Statuses
remain request-local and ephemeral. QA cleanup found no remaining feature
fixtures.

### Required Changes

#### F16-STATUS-PROPOSAL-REV-001

* Requirement ID: `CHAT-STATUS-008`
* Category: Correctness / API compatibility
* Severity: High
* State: `VERIFIED`
* Resolution: Event-aware limits now preserve valid terminal responses above
  16 KiB, explicitly reject true overflows, emit one safe backend size error,
  and retain JSON/SSE parity.
* Evidence: frozen commit `ec168ac`, frontend fragmented/overflow tests,
  backend parity/size-error tests, QA Attempt 3, and the independent 24,104-byte
  production-helper reproduction.

#### F16-STATUS-PROPOSAL-REV-002

* Requirement ID: `CHAT-STATUS-003`, `CHAT-STATUS-010`
* Category: Security / event-contract validation
* Severity: Medium
* State: `VERIFIED`
* Resolution: Next.js, Flask, and `ProcessingStatusReporter` now preserve only
  IDs matching `^[A-Za-z0-9_-]{1,64}$` and replace all other values before
  trusted protocol/log/header use.
* Evidence: frozen commit `ec168ac`, Next.js route tests, Flask/reporter tests,
  live QA proxy/log checks, and direct cross-stack code inspection.

No open Reviewer or QA finding remains.

### Human Action Required

None for feature correctness or integration. No new CEO clarification,
database action, billing action, deployment action, or production mutation is
required. The Orchestrator may generate the final report and continue the
approved release workflow. Production deployment remains separately
approval-gated.

Attempt Result: APPROVED — both stable Reviewer findings and the prior QA
concurrency finding are verified at the final frozen commit; no blocking issue
remains.

## Status

STATUS: APPROVED
