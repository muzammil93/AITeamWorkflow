# Architecture Document

## Feature Name

Backend-Driven Chat Processing Statuses

## Feature ID and Execution Mode

`F16-STATUS-PROPOSAL` — standard new-behavior proposal, approval-gated.

This architecture is a plan for CEO review. Product implementation must not
start until the CEO approves the PRD and this architecture and the Orchestrator
records the required release-plan change control.

## PRD Reference

`projects/saleaura/features/f16-chat-processing-statuses-proposal/prd.md`

The referenced PRD is ready for architecture and defines requirements
`CHAT-STATUS-001` through `CHAT-STATUS-012`.

## Master Architecture / Requirement References

* SaleAura V1 master architecture: preserve the incremental Next.js public API
  facade, synchronous Flask chat engine, F08 anonymous session boundary, F09
  structured response contract, and English/Urdu/Roman Urdu presentation.
* SaleAura V1 release plan: `CHAT-001`, `CHAT-002`, `CART-008`, `CART-010`, and
  `REL-005`.
* F08 architecture: the Next.js chat proxy remains responsible for deriving the
  trusted owner/session from the authenticated preview or signed widget
  session. A status stream must not create a second authorization path.
* F09 architecture: the backend remains authoritative for intent, active work,
  response language, and customer-safe response data.
* F10/F11 boundary: verified-build generation and build modification remain
  deterministic and unchanged; this feature may only report when those
  existing operations are actively executing.
* Existing F16 architecture and implementation: the Send-button spinner,
  product/build/cart/lead response behavior, and owner/session isolation remain
  unchanged.

## Baseline QA Findings

`NOT_APPLICABLE`

This is new customer-visible behavior. It is not a bounded repair of an
existing approved F16 requirement.

## Dependency Validation

The necessary implementation boundaries already exist:

* `components/chat/ChatWidget.tsx` owns the typing indicator, request loading
  state, response rendering, and the unchanged Send-button spinner.
* `app/api/chat/route.ts` authenticates the owner preview or validates the F08
  widget session before proxying one POST request.
* `backend/api.py` owns the synchronous Flask chat request lifecycle and already
  contains an SSE pattern for inventory-upload progress.
* `backend/engine.py` owns intent classification, inventory search, comparison,
  verified-build generation, and response composition.
* The project already uses browser `fetch`, Web Streams, Flask `Response`, and
  Python standard-library concurrency. No new runtime dependency is required.

F08, F09, F10, F11, and the existing F16 behavior are available as dependencies.
The proposal is not yet part of the immutable V1 release plan. That governance
gap does not block architecture planning, but it blocks Developer execution
until CEO approval and Orchestrator change control.

## Technical Summary

Use one content-negotiated Server-Sent Events response over the existing
authenticated `POST /api/chat` path.

The widget requests `text/event-stream`. The Next.js route performs exactly the
same F08 owner/session validation and rate limiting it performs today, forwards
the trusted request to Flask, and passes the upstream stream through without
buffering. Flask bridges its synchronous chat execution to a bounded in-process
event queue: the existing chat work runs in one worker, and the response
generator emits a status event immediately before each instrumented operation
and a single terminal result or error event afterward.

Non-streaming callers continue to receive the current JSON response from the
same route. Both adapters call one shared chat-execution path so streaming does
not fork search, quota, persistence, cart, lead, or error behavior.

The approved transport event contract is:

| Event | Required fields | Meaning |
| --- | --- | --- |
| `status` | `version`, `request_id`, `sequence`, `stage`, `language` | A fixed allowlisted stage is genuinely active for this request. |
| `result` | `version`, `request_id`, `payload` | The existing successful JSON chat payload, unchanged. |
| `error` | `version`, `request_id`, `error.code`, `error.message`, `error.retryable` | A safe terminal failure after streaming has begun. |

`stage` is an enum, never customer-authored text:

* `understanding_request`
* `searching_products`
* `comparing_products`
* `building_pc`
* `checking_build_changes`
* `preparing_response`

`language` is `en`, `ur`, or `roman_ur`. The frontend maps this stage/language
pair to the exact approved PRD wording. Unknown stages, unknown languages,
malformed events, and raw backend strings are never displayed.

### Transport Options Considered

1. **Final JSON metadata** is not viable. Metadata arrives only after work has
   completed and therefore cannot describe a genuinely active stage.
2. **Frontend timers, message inference, or predetermined rotation** are
   prohibited by the PRD and would remain misleading.
3. **Polling a request-status endpoint** would require a request-job registry,
   a second authenticated request, race handling, cleanup, and either
   process-local state that fails across workers or new durable storage. It is
   larger and less reliable than the selected design.
4. **WebSockets** require a new connection lifecycle and likely deployment
   infrastructure for a one-request server-to-client flow. They are
   disproportionate.
5. **NDJSON over fetch** could work, but the repository already has Flask SSE
   streaming patterns, and named SSE events make status/result/error framing
   explicit without adding a protocol dependency.
6. **Content-negotiated SSE over the existing POST** is selected. `fetch` can
   read an SSE response to a POST, it keeps authorization and request payload in
   one request, requires no database or external service, and preserves JSON
   consumers.

This design must be stopped rather than replaced with simulated statuses if the
local and authorized staging proxy path cannot deliver a status frame before
the terminal frame without a deployment rewrite.

## Frontend Changes

### Request and Status State

In `components/chat/ChatWidget.tsx`:

* Keep `isLoading` and the existing Send-button rendering exactly as they are.
* Add ephemeral status state separate from `messages`.
* Generate one request ID before each chat request and store it as the active
  request. The existing trace ID may serve as this ID.
* Send `Accept: text/event-stream` and parse complete SSE frames from
  `response.body`. Retain JSON parsing as a compatibility fallback when the
  response content type is JSON.
* Apply a `status` event only when:
  * its version, request ID, sequence, stage, and language are valid;
  * its request ID equals the active request;
  * the request is still loading and non-terminal; and
  * its sequence is newer than the last accepted sequence.
* Ignore duplicate stage/language values without changing rendered live-region
  content, even if a newer sequence arrives.
* Accept exactly one matching terminal `result` or `error`. Ignore all later
  frames.
* Clear the status in the same active-request-scoped cleanup that clears
  loading on success, failure, abort, request replacement, navigation, or
  unmount. Cleanup from an older request must not clear a newer request.
* Use an `AbortController` for the active fetch lifecycle. This adds no customer
  cancel control; it only makes existing navigation/unmount/replacement cleanup
  explicit.

Keep the parser and approved status-copy table in one small typed helper, such
as `components/chat/processing-status.ts`, so the runtime allowlist and
multilingual mapping can be unit tested without rendering the full widget.

### Typing Indicator Presentation

Change only the hardcoded rotating-text portion of `TypingIndicator`:

* Remove the interval, step state, and hardcoded rotation.
* Always retain the current assistant visual and three animated dots while
  `isLoading` is true.
* Before a valid backend event, show no visible phrase.
* After a valid event, show only the latest mapped phrase.
* Use `role="status"`, `aria-live="polite"`, and `aria-atomic="true"` for the
  changing phrase. Do not move focus.
* The dots are decorative to assistive technology. A screen-reader-only
  “Assistant is responding” label may describe the dots-only initial state; it
  must not be visible or claim a specific processing operation.
* Use `dir="rtl"` for `ur` and `dir="ltr"` for `en` and `roman_ur`.
* Allow wrapping within the existing bubble width; do not add horizontal
  scrolling or change the overall widget/card layout.

The two existing desktop/embedded render branches must receive the same status
state so behavior cannot diverge.

## Backend Changes

### Shared Chat Execution

In `backend/api.py`, keep one business-logic path and expose two response
adapters:

* The current JSON adapter executes synchronously and returns the current status
  codes and payload shape.
* The streaming adapter uses a bounded standard-library queue and one
  request-scoped worker to run the same execution. The status reporter enqueues
  allowlisted events; the response generator yields them as SSE frames and then
  yields one terminal result/error frame.

The extraction must be mechanical and limited to the current chat route. Do not
move or refactor unrelated inventory, cart, lead, quota, persistence, or
notification logic. The worker receives already-parsed request data and must
preserve trace context and safe logging. No event may contain message text,
session tokens, owner IDs, inventory rows, or exception details.

The queue is bounded because there are at most six approved stage changes.
Client disconnect sets a cancellation flag, stops further status publication,
and allows any already-running bounded external call to finish safely. The
implementation must not attempt unsafe thread termination.

### Genuine Instrumentation Points

Pass an optional typed status reporter from `backend/api.py` into
`UnifiedIntentService.process_message` and the existing handlers. A no-op
reporter preserves existing tests and non-streaming behavior.

Emit only at these actual boundaries:

* `searching_products`: immediately before the product-search inventory query.
* `comparing_products`: immediately before comparison inventory retrieval and
  comparison preparation.
* `building_pc`: immediately before the existing F10 generator begins candidate
  selection and deterministic validation.
* `checking_build_changes`: immediately before the existing F11 modifier begins
  proposal preparation, revalidation, or confirmation work.
* `preparing_response`: after the relevant domain operation finishes and
  immediately before grounded response composition or customer-safe response
  assembly.
* `understanding_request`: only if the backend has already established the
  current request language and is still actively classifying/extracting the
  request. The present one-shot intent parse may therefore show dots only
  during initial understanding. It must not emit this stage after
  classification merely to make it visible.

No handler may emit a stage it does not execute. A general component question
must not emit search, comparison, build, or modification stages. Very short
stages may pass too quickly to be perceived; neither backend nor frontend holds
them open.

### Response Language

Add an optional allowlisted `response_language` field to the structured
`IntentResponse` contract in `backend/schema.py` and its prompt schema in
`backend/prompts/04_response_format.txt`. Values are `en`, `ur`, or
`roman_ur`.

The value describes the language in which the backend is preparing the current
response. It does not translate inventory facts or alter F09 response behavior.
If the model omits it, returns an unsupported value, or language is otherwise
uncertain, the backend omits visible status events until a valid language is
available. It must not default an uncertain Roman Urdu request to an English
visible status.

The reporter deduplicates unchanged stage/language pairs and assigns monotonic
sequence numbers. It reports stages only after F08 session, entitlement, quota,
and basic request validation have allowed processing.

## Database Changes

None.

Statuses remain request-local and ephemeral. Do not add Supabase columns,
tables, migrations, chat-history records, analytics, audit records, or session
state for this feature.

## API Changes

`POST /api/chat` keeps its URL, request body, authentication, and JSON behavior.
The response varies only by the request `Accept` header:

* Default/current accept behavior: the existing JSON response and HTTP status.
* `Accept: text/event-stream`: SSE frames ending in one `result` or `error`.

The Next.js proxy must:

* complete the current owner-preview or widget-session authorization before
  proxying;
* preserve the current trusted `user_id`, trusted `session_id`, trace ID, rate
  limiting, and request payload;
* forward the streaming accept header;
* stream the Flask body without calling `response.json()` or accumulating the
  full body;
* set `Content-Type: text/event-stream`, `Cache-Control: no-cache, no-transform`,
  and a supported no-buffering header for the local/staging proxy;
* cancel the upstream reader when the downstream request is aborted; and
* keep JSON error passthrough for errors returned before a stream is created.

The terminal `result.payload` must be byte-for-byte equivalent in meaning and
shape to the current successful JSON body so the widget uses its existing
message/card/cart/lead rendering path. Status events are not final-response
metadata.

## Authentication / Authorization Impact

No authorization model changes.

The existing Next.js route validates the F08 widget token or authenticated owner
preview before any Flask request. The trusted session and owner remain
server-derived. A client-provided request ID is correlation data only and
grants no access.

Every event belongs to that authorized POST and contains only a stage enum,
language enum, sequence, version, and request ID. There is no independently
queryable status endpoint and no cross-request status store.

## Security Considerations

* Validate event fields on both backend emission and frontend consumption.
* Never render backend-provided free text as a status.
* Bound the SSE frame size, queue size, stage count, request duration, and
  existing message size/rate limits.
* Do not include prompts, user messages, contact details, owner/session IDs,
  inventory data, secrets, stack traces, or provider errors in status events.
* Preserve current server-only Supabase/OpenAI credentials and F08
  owner/session isolation.
* Disable intermediary caching and response transformation for the stream.
* Treat disconnect as cancellation of delivery, not authorization to roll back
  or partially repeat a quota, lead, cart, or persistence operation.
* Do not automatically retry the POST stream because chat processing and lead
  submission may have non-idempotent effects.

## Error Handling

* Before streaming starts, preserve the existing safe JSON HTTP errors from the
  Next.js authorization boundary.
* After streaming starts, emit one safe terminal `error` frame and close the
  stream. Raw Flask, Supabase, OpenAI, or network errors remain server logs only.
* A malformed frame, unknown stage/language, invalid sequence, wrong request ID,
  duplicate terminal event, or late frame is ignored and never shown as text.
* An unexpectedly closed stream without a terminal frame follows the widget's
  existing generic retryable error path.
* Success clears status before or atomically with rendering the assistant
  response.
* Failure clears status before rendering the existing safe failure message.
* Abort, navigation, unmount, or replacement clears the active request's
  loader/status. A late event from that request cannot update the next request.
* Server-side cancellation checks occur between bounded operations. An
  in-flight OpenAI/Supabase call may complete, but no later status is delivered
  to a disconnected client and no unsafe thread cancellation is attempted.

## Testing Guidance

### Python Unit and Contract Coverage

Add focused tests using the existing Python test approach:

* Each engine handler emits only its genuine stage immediately before the
  corresponding operation.
* General chat/no-status requests never emit inventory-search status.
* Search, comparison, build, and modification paths emit the relevant stage and
  transition to response preparation only when that preparation executes.
* Unknown/absent response language suppresses the visible status event.
* Events are deduplicated and sequences are monotonic.
* The SSE adapter emits valid status frames followed by exactly one terminal
  result or safe error.
* The JSON adapter retains existing status codes and payloads.
* The terminal streamed result matches the JSON contract for the same
  deterministic fixture.
* Disconnect/cancellation prevents later status publication without duplicating
  persistence or quota work.

Mocks are appropriate for focused OpenAI/Supabase unit boundaries, but they are
not staging readiness evidence.

### TypeScript Unit and Contract Coverage

Using the existing Vitest setup, cover:

* fragmented and multi-frame SSE parsing;
* allowlisted stage/language localization for all eighteen approved
  stage/language combinations;
* malformed, unknown, duplicate, out-of-order, wrong-request, post-terminal,
  and stale-event rejection;
* dots-only presentation before the first status;
* unchanged status not triggering a repeated live-region announcement;
* completion, JSON fallback, error, unexpected close, abort, unmount, and
  replacement cleanup;
* Urdu RTL and English/Roman Urdu LTR direction;
* wrapped desktop/mobile-safe presentation; and
* an explicit regression assertion that the existing Send-button spinner,
  disabled state, and loading trigger are unchanged.

Run the existing F08, F09, F10/F11, F12, and F16 targeted regressions affected
by the shared chat route.

### Staging Playwright Coverage

Against the authorized non-production Supabase owner and dedicated inventory:

* Install a DOM `MutationObserver` before sending so genuine short-lived status
  text can be recorded without introducing a minimum display delay.
* Verify an actual English inventory search reports and renders `Searching
  products`, then clears it when the real product response appears.
* Verify Urdu and Roman Urdu inventory searches render the exact approved text
  and direction.
* Verify a general non-search request never records an inventory-search status.
* Verify genuine comparison, build, and build-modification requests record only
  their applicable stages when those operations execute.
* Verify terminal success, forced safe failure, request abort/navigation, and a
  controlled late/stale frame clear or preserve the correct request state.
* Verify unknown/malformed frames are not visible, focus does not move, the
  live region is polite, and unchanged text is not re-announced.
* Repeat the focused presentation checks at the existing desktop and mobile
  widget widths.
* Assert the Send-button spinner still appears during loading and is unchanged.
* Fail on uncaught `pageerror` and unexpected `console.error`.

Actual staging stream frames plus DOM mutation evidence prove the
backend-to-visible path. Controlled route responses may supplement malformed,
stale, and abrupt-close frontend cases but do not replace the real staging
search/comparison/build evidence.

Required implementation checks remain proportionate: targeted Python tests,
targeted Vitest suites, `pnpm exec tsc --noEmit`, `git diff --check`, and the
focused staging Playwright spec. No new test framework is required.

## Migration Validation and Recovery

`NOT_APPLICABLE`

No database or migration change is permitted. Recovery is a code rollback to
the prior JSON-only proxy and dots-only typing indicator. Because the terminal
JSON payload and persistence behavior remain unchanged, rollback requires no
data repair.

## Git / Change Boundaries

Expected product-code boundaries:

* `SaleAura-WebApp/components/chat/ChatWidget.tsx`
* `SaleAura-WebApp/components/chat/processing-status.ts` (small typed helper)
* `SaleAura-WebApp/app/api/chat/route.ts`
* `SaleAura-WebApp/backend/api.py`
* `SaleAura-WebApp/backend/engine.py`
* `SaleAura-WebApp/backend/schema.py`
* `SaleAura-WebApp/backend/prompts/04_response_format.txt`
* Focused tests under `SaleAura-WebApp/tests/f16/`,
  `SaleAura-WebApp/tests/e2e/`, and the existing Python test directory.

Do not change the Send-button component, cart/lead/product/build contracts,
database files, migrations, package manifests, lockfiles, deployment files,
legal content, release plan/state, or unrelated loaders. Preserve existing
generated bytecode and browser storage-state changes without committing or
rewriting them.

## Risks

* **Proxy buffering:** a server or intermediary may buffer frames. Local and
  staging verification must prove the first status arrives before the terminal
  result. Do not compensate with timers or fake rotation.
* **Synchronous execution:** streaming requires a small worker/queue bridge.
  Keep it request-scoped, bounded, and shared with the JSON execution path to
  avoid behavior drift.
* **Language uncertainty:** the current intent contract does not expose response
  language. The optional enum must be validated; uncertainty yields dots-only
  loading rather than incorrect English or script.
* **Rapid stages:** genuine stages may be too short to perceive. Mutation
  evidence can verify them, but production must not impose display delays.
* **Refactor regression:** mechanically extracting the chat execution path can
  affect quota, persistence, cart, lead, F10, and F11 branches. Targeted
  regression coverage is mandatory.
* **Disconnect semantics:** browser abort cannot safely terminate an already
  executing provider call. Delivery stops and cleanup remains bounded, while
  existing idempotency and persistence semantics stay authoritative.

## Out of Scope / Not Implemented

* Any Send-button spinner change.
* Timer/random/predetermined status rotation, frontend message inference,
  percentage progress, elapsed time, estimates, or minimum display duration.
* A visible generic fallback phrase before the first valid status.
* New customer cancellation controls.
* Status persistence, history, Supabase schema, analytics, owner customization,
  or audit logging.
* Search, comparison, build, modification, cart, lead, quota, entitlement,
  inventory, prompt-response meaning, or AI model changes beyond exposing the
  response-language enum needed for presentation.
* WebSockets, polling infrastructure, background job systems, external
  services, new packages, deployment changes, or production mutation.
* Changes to any loader outside the chat typing indicator.

## Implementation Guidance

1. First extract one test-covered shared Flask chat execution function without
   changing its JSON output.
2. Add the validated response-language enum and optional status reporter.
3. Instrument only the approved real-operation boundaries.
4. Add the bounded SSE adapter and confirm non-stream JSON parity.
5. Update the existing Next.js POST proxy to pass through negotiated streams
   after the current authorization checks.
6. Add the typed frontend parser/request scoping and replace only the typing
   indicator's rotating text.
7. Run focused unit/contract regressions before staging Playwright.
8. Stop and return to the Architect/CEO if true pre-terminal delivery requires
   a deployment change, new durable status store, new external service, or
   material rewrite of the chat engine.

Developer execution remains paused until explicit CEO approval and Orchestrator
change control.

## Status

STATUS: ARCHITECTURE_READY
