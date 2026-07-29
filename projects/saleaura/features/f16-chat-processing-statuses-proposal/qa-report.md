# QA Report

## Feature ID and Name

`F16-STATUS-PROPOSAL` — Backend-Driven Chat Processing Statuses

## QA Mode

`POST_IMPLEMENTATION`

## Requirement IDs

`CHAT-STATUS-001` through `CHAT-STATUS-012`

## Input References

* `projects/saleaura/features/f16-chat-processing-statuses-proposal/ceo-request.md`
* `projects/saleaura/features/f16-chat-processing-statuses-proposal/prd.md`
  ending `PRD_READY`
* `projects/saleaura/features/f16-chat-processing-statuses-proposal/architecture.md`
  ending `ARCHITECTURE_READY`
* `projects/saleaura/features/f16-chat-processing-statuses-proposal/implementation-report.md`
  ending `IMPLEMENTATION_COMPLETE`
* `projects/saleaura/saleaura-v1-release-plan.md`, including approved change
  control `CC-002`
* `projects/saleaura/saleaura-v1-release-state.md`, including transitions
  `T-075` through `T-078`
* `memory/project.md`
* `memory/tech-stack.md`
* `memory/coding-standards.md`
* `templates/qa-report-template.md`
* Frozen product commit
  `624bdf5e70f0df88ab3d6d63320b861a05fd6fc6`

## Attempt 1

### Environment

* Date: 2026-07-29 through 2026-07-30 (Asia/Karachi).
* Product repository:
  `/Users/muzammilmunir/Documents/Developer/Agentic-teams/SaleAura-WebApp`
* Product HEAD: `624bdf5e70f0df88ab3d6d63320b861a05fd6fc6`.
* Branch shown by Git:
  `feature/f03-product-catalog-manual-inventory`.
* Frontend: existing single Next.js development server at
  `http://localhost:5001`.
* Backend: Flask restarted from frozen HEAD and served at
  `http://127.0.0.1:8001` with `.env.staging`.
* Browser: Chromium/Playwright plus the CEO-authorized refreshed staging owner
  state from `tests/e2e/qa-storage-state.json`.
* Data provider: authorized non-production Supabase staging only.
* Dedicated staging fixtures used the existing QA owner and were deleted by the
  E2E cleanup helpers. Follow-up SQL found zero feature QA inventory rows and
  zero temporary `127.0.0.1` allowed-host rows.
* Production, deployment, billing, migrations, and schema mutation were
  prohibited and not used.
* Pre-existing modified generated `backend/**/__pycache__/*.pyc` files and
  `tests/e2e/qa-storage-state.json` were preserved uncommitted.

### QA Summary

The fixed status vocabulary, SSE contract, dots-only initial state,
multilingual rendering, accessibility attributes, success/failure/abort
cleanup, JSON compatibility, no-persistence behavior, responsive presentation,
unchanged Send spinner, and affected F08–F12/F16 regressions passed the
executable checks listed below.

QA found one High request-isolation defect. `get_or_create_engine` shares one
mutable `UnifiedIntentService` instance for concurrent requests from the same
owner, while `process_message` stores the request reporter and response
language on that shared instance. A deterministic two-request test caused
request A's real search stages to be published through request B's reporter.
Request B would therefore accept and display a status for work it did not
execute, while request A receives no status. This violates the central
truthfulness and same-request requirement and prevents a QA pass.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Evidence | Command or Procedure |
| --- | --- | --- | --- |
| `CHAT-STATUS-001` | PASS | The assistant avatar/dots and Send spinner appeared during real and controlled requests. Source regression confirms the existing `<Loader2 className="w-4 h-4 animate-spin" />` JSX remains. | F16 Vitest suite; focused and multilingual staging Playwright; controlled dots-only mobile harness. |
| `CHAT-STATUS-002` | PASS | Before a delayed no-status response, three animated dots were visible, `processing-status` had count zero, and only the screen-reader label existed. | Controlled mobile Playwright no-status request. |
| `CHAT-STATUS-003` | FAIL | Genuine staging paths emitted the right stage normally, but a deterministic concurrent same-owner test rerouted request A's search stages through request B's reporter. See `F16-STATUS-PROPOSAL-QA-001`. | Real staging SSE matrix plus the two-thread Python concurrency reproduction. |
| `CHAT-STATUS-004` | PASS | No timer, random choice, message inference, predetermined rotation, or minimum duration remains. `Analyzing request`, `Searching inventory`, and `window.setInterval` are absent; visible transitions matched received SSE frames. | F16 Vitest source regression, code inspection, real SSE/DOM mutation evidence. |
| `CHAT-STATUS-005` | PASS | General chat completed with zero status events. Search, compare, and build requests emitted ordered sequences 1 and 2; the UI followed them without delay. Duplicate newer events did not re-announce. | Authenticated staging Playwright request matrix; F16 Python/Vitest tests. |
| `CHAT-STATUS-006` | PASS | English and Roman Urdu used `ltr`; Urdu used `rtl`. Exact approved search and preparation copy rendered in all three languages. | Desktop multilingual and mobile Urdu Playwright DOM mutation checks; 18-combination Vitest mapping. |
| `CHAT-STATUS-007` | PASS | Rendered text had `role=status`, `aria-live=polite`, and `aria-atomic=true`; status nodes were not focusable and active focus did not change between observed stages. Duplicate stage/language pairs produced one callback. | Desktop Playwright accessibility capture; F16 Vitest duplicate-event assertion. |
| `CHAT-STATUS-008` | PASS | Successful results removed the status/typing loader and left the assistant product/message/build result visible. | Focused staging Playwright, desktop/mobile multilingual checks, embedded build/modify flow. |
| `CHAT-STATUS-009` | PASS | A forced 500 cleared the loader/status, re-enabled input, and rendered the existing safe retry message. The only console error was the deliberately forced 500 resource log; unexpected console errors and page errors were zero. | Controlled mobile Playwright failure harness; backend safe-error unit test. |
| `CHAT-STATUS-010` | PASS | Close/abort followed by a new real staging request cleared the old loader; the current request completed, no old result appeared, and no status remained. Wrong-request and late frames were rejected in contract tests. | Real mobile close/reopen staging Playwright; controlled malformed/wrong-request checks; F16 Vitest. |
| `CHAT-STATUS-011` | PASS | Status state is separate from messages. Supabase staging contained zero chat-message rows equal to any of the 18 approved status phrases after QA traffic. Reload has no status source to rehydrate. | Supabase MCP read-only SQL plus source inspection. |
| `CHAT-STATUS-012` | PASS | Statuses were readable at 1440×1100 and 390×844. Captured status `scrollWidth` never exceeded `clientWidth`; terminal loader count was zero. | Desktop English/Urdu/Roman Urdu and mobile Urdu staging Playwright. |

### Acceptance Criteria

| Acceptance criterion | Result | Actual result |
| --- | --- | --- |
| Dots only before the first genuine stage | PASS | Delayed no-status response showed avatar and three dots with no visible phrase. |
| Genuine English, Urdu, and Roman Urdu inventory-search copy | PASS | Real staging search emitted and rendered the exact approved text and direction for all three languages. |
| General requests never claim inventory search | PASS | Real `qa-general` request emitted zero statuses and returned a terminal message result. |
| Comparison, build, and modification show only their applicable stage | PASS | Real staging produced `comparing_products`, `building_pc`, and `checking_build_changes` respectively. The embedded build/modify UI observed `Building your PC` then `Checking build changes`. |
| Multiple genuine stages follow backend reports without fake timing | PASS | Search, comparison, and build streams emitted monotonic stage 1 then `preparing_response` stage 2; DOM mutation order matched the stream. |
| A no-customer-status request can complete | PASS | Controlled dots-only request and real general chat both completed normally without status text. |
| Completion clears loader and does not persist status | PASS | Loader count was zero after every terminal result; Supabase status-message count was zero. |
| Backend/network failure clears loader and preserves safe retry | PASS | Forced 500 produced the existing safe retry message with enabled input and no remaining status. |
| Abort/cancellation clears stale state | PASS | Real close/reopen test completed the new request without rendering the aborted request result or status. |
| Polite live status, stable focus, no repeated unchanged announcement | PASS | Live-region attributes passed; focus remained on `BODY` across status mutations; duplicate stage/language was deduplicated. |
| LTR/RTL and no desktop/mobile horizontal overflow | PASS | Exact direction and `scrollWidth <= clientWidth` passed at desktop and mobile sizes. |
| Existing Send spinner and chat/search/comparison/build/modification/cart/lead behavior | PASS | Send spinner remained visible during load; targeted unit suites, seeded E2E search/comparison/language, embedded build/modify, and cart E2E passed. |
| Every visible status is truthful and belongs to the same active request | FAIL | Concurrent requests using the cached engine can publish one request's stages under the other request's reporter/request ID. |

### Test Cases and Actual Results

#### Static, Python, TypeScript, and Contract Checks

1. Product freeze and workspace:

   ```text
   git rev-parse HEAD
   git status --short
   git show --stat --oneline 624bdf5
   git diff-tree --no-commit-id --name-status -r 624bdf5
   ```

   Actual: HEAD matched the frozen commit. Only the five explicitly preserved
   generated/storage-state files were modified. The feature commit changed 18
   approved source/test files and no migration, package, deployment, legal, or
   Send-component file.

2. Backend and dependency regressions:

   ```text
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest \
     tests.test_f16_processing_status \
     tests.test_f09_customer_response \
     tests.test_f09_language_contract \
     tests.test_f09_quota_timing \
     tests.test_f10_verified_build_generation \
     tests.test_f11_build_modifier_safety \
     tests.test_f12_lead_consent \
     tests.test_f16_lead_notifications \
     tests.test_engine_search_fallback \
     tests.test_engine_build_clarification
   ```

   Actual: 27/27 passed.

3. Frontend and dependency regressions:

   ```text
   pnpm vitest run tests/f08 tests/f09 tests/f10 tests/f11 tests/f12 tests/f16
   ```

   Actual: 11 files and 27/27 tests passed.

4. Type and diff checks:

   ```text
   pnpm exec tsc --noEmit
   git diff --check
   git diff --quiet -- <all 18 frozen feature files>
   ```

   Actual: all passed; frozen feature files had no uncommitted delta.

5. JSON compatibility:

   Authenticated Playwright request to the unchanged route with
   `Accept: application/json`.

   Actual: HTTP 200, `application/json`, keys
   `model,response,session_id,structured,success,trace_id`, structured type
   `message`, and matching trace ID.

6. Backend SSE contract:

   F16 Python tests exercised validation, deduplication, monotonic sequence,
   cancellation suppression, status-before-result framing, JSON payload parity,
   and one safe terminal server error.

   Actual: passed.

7. Frontend SSE parser:

   F16 Vitest exercised fragmented/multi-frame parsing, all 18 copy mappings,
   malformed/unknown/wrong-request/duplicate/out-of-order rejection, safe error,
   abrupt close, dots-only source, and the unchanged spinner.

   Actual: passed.

#### Mandatory Staging Playwright

1. First focused attempt using the previously stale saved state:

   ```text
   pnpm exec playwright test --config=playwright.staging.config.ts \
     tests/e2e/chat-processing-status.spec.ts
   ```

   Actual: environment authentication blocked at Google sign-in because the
   saved Supabase refresh token had rotated. This was not treated as product
   evidence or a product finding.

2. After the Orchestrator refreshed the authorized Chrome state:

   ```text
   E2E_BASE_URL=http://localhost:5001 \
   E2E_STORAGE_STATE=tests/e2e/qa-storage-state.json \
   pnpm exec playwright test --config=playwright.staging.config.ts \
     tests/e2e/chat-processing-status.spec.ts
   ```

   Actual: 1/1 passed in 15.1 seconds. Real staging emitted
   `Searching products` and `Preparing response` before the product result;
   mobile UI, status cleanup, spinner, `pageerror`, and `console.error`
   assertions passed.

3. Dedicated staging fixtures:

   ```text
   pnpm exec playwright test --config=playwright.staging.config.ts \
     tests/e2e/customer-search.spec.ts \
     tests/e2e/customer-comparison.spec.ts \
     tests/e2e/customer-language.spec.ts
   ```

   Actual: 3/3 passed in 1.2 minutes. Temporary inventory and allowed host were
   cleaned.

4. Proportionate cart regression:

   ```text
   pnpm exec playwright test --config=playwright.staging.config.ts \
     tests/e2e/customer-cart.spec.ts --grep E2E-033
   ```

   Actual: 1/1 passed in 57.6 seconds. Session-bound offers, quantity, remove,
   buy-intent validation, cancellation, forged/replayed/expired offers, and
   cleanup passed.

5. Authenticated real-stage request matrix:

   Playwright sent general, Urdu search, Roman Urdu search, comparison, and
   build requests through `POST /api/chat` with `Accept: text/event-stream`.

   Actual:

   * General: zero statuses, terminal message result.
   * Urdu: `searching_products(1)` then `preparing_response(2)`, both `ur`.
   * Roman Urdu: the same ordered stages, both `roman_ur`.
   * Comparison: `comparing_products(1)` then
     `preparing_response(2)`, terminal comparison.
   * Build: `building_pc(1)` then `preparing_response(2)`, terminal builds.
   * Every frame and terminal event carried the matching request ID.

6. Real embedded build/modification:

   An ephemeral localhost host embedded the real staging widget, generated a
   build, then requested a cheaper GPU. The allowed-host row was removed in
   `finally`.

   Actual: build observed `Building your PC` and `Preparing response`;
   modification observed `Checking build changes`; both returned HTTP 200 SSE,
   spinner cleared, terminal loader count was zero, and page/console errors
   were zero.

7. Desktop and mobile presentation:

   Inline Playwright DOM observers recorded genuine fast status mutations.

   Actual:

   * 1440×1100: exact English/Urdu/Roman Urdu copy, `ltr/rtl/ltr`,
     `role=status`, polite/atomic live region, no overflow, spinner present,
     terminal cleanup, zero page/console errors.
   * 390×844 Urdu: exact RTL search/preparation copy, no overflow, spinner
     present, terminal cleanup, zero page/console errors.

8. Controlled failure and malformed events:

   A mobile Playwright route harness delayed the first response, forced a 500,
   then supplied malformed JSON, wrong-request, unknown-stage, out-of-order,
   and duplicate status frames before a valid terminal result.

   Actual: dots-only state passed; failure cleanup and safe retry passed; raw
   invalid values never rendered; terminal cleanup passed; page errors were
   zero. The expected forced-500 resource log was recorded, and unexpected
   console errors were zero.

9. Abort and late cleanup:

   A real staging search was closed while loading, the widget reopened, and a
   new general request was sent after widget configuration was ready.

   Actual: the new request completed, old and new user messages remained, no
   aborted search result/status appeared, input was enabled, status count was
   zero, and page/console errors were zero.

   An earlier harness attempt sent before the saved greeting/configuration had
   initialized and was discarded because greeting initialization replaced the
   harness messages. The isolated retest waited for configuration and passed.

#### Supabase Staging Evidence

Read-only Supabase MCP SQL found:

* `0` `chat_messages` rows equal to any of the 18 approved status phrases after
  QA traffic.
* `0` leftover search/comparison/language/F16 fixture inventory rows.
* `0` leftover `127.0.0.1` QA allowed-host rows.

No status table, column, migration, or production mutation was introduced.

#### Deterministic Concurrency Reproduction

An inline Python two-thread harness used one cached-equivalent
`UnifiedIntentService`. It held request A in intent parsing, started request B
so B replaced the shared reporter, then released A into its real search
handler.

Expected:

```text
events_a = [("searching_products", "en"), ("preparing_response", "en")]
events_b = []
```

Actual:

```text
events_a = []
events_b = [("searching_products", "en"), ("preparing_response", "en")]
threads_alive = [False, False]
errors = []
```

The assertion failed with `request A lost/misrouted its statuses`. The failure
was deterministic and directly follows the production cache/request path:
`backend/api.py` returns one cached engine for the same owner, while
`backend/engine.py` stores `_status_reporter` and `last_response_language` on
that shared engine.

### Findings

#### F16-STATUS-PROPOSAL-QA-001

* Requirement ID: `CHAT-STATUS-003`
* Severity: High
* State: `OPEN`
* Title: Concurrent same-owner requests can display another request's
  processing stage
* Reproduction steps:
  1. Obtain the same cached `UnifiedIntentService` used for one owner.
  2. Start request A with reporter A and hold it during intent parsing.
  3. Start request B with reporter B and hold it after `process_message`
     replaces the engine's `_status_reporter`.
  4. Release request A into product search.
  5. Inspect both reporter event lists.
* Expected result: Request A's genuine search/preparation stages publish only
  through reporter A. Request B receives no stage for work it did not execute.
* Actual result: Reporter A receives no event. Reporter B receives request A's
  `searching_products` and `preparing_response` stages. Because reporter B
  stamps its own request ID, request B's frontend accepts the misleading stages
  as current.
* Evidence:
  * `backend/api.py:301-316` reuses one cached engine for a matching
    owner/locale.
  * `backend/engine.py:48-50` stores request-derived intent, language, and
    reporter on the engine.
  * `backend/engine.py:89-91` replaces those fields at request start.
  * `backend/engine.py:239-244` clears/reads the same shared reporter.
  * Deterministic harness actual result shown above.
* Suggested fix direction: make reporter, response language, and intent
  request-local throughout processing, or otherwise serialize use of each
  cached mutable engine. Add a deterministic concurrent-request regression
  proving that each queue receives only its own statuses and terminal result.

### Edge Cases

Passed:

* Zero-status successful request.
* Rapid genuine multi-stage request.
* Missing/unsupported response language suppression.
* Fragmented and multi-frame SSE.
* Malformed JSON and oversized/abrupt stream handling.
* Unknown stage/language.
* Wrong request ID.
* Duplicate, out-of-order, and post-terminal frames.
* Safe JSON and streamed failure.
* Close/abort followed by a new request.
* English, Urdu, and Roman Urdu copy/direction.
* Desktop and mobile overflow.
* Search with active/in-stock versus excluded products.
* Comparison with missing catalog facts.
* Build and build-modification status boundaries.
* Cart quantity, remove, cancel, forged/replayed/expired offer boundaries.

Failed:

* Two concurrent requests sharing the same cached owner engine.

### Security and Ownership Checks

* The existing authenticated owner-preview/widget-session authorization path
  remained before the Next.js proxy.
* Embedded staging validation used an allowed hostname and removed it after the
  test.
* Event payloads observed only protocol version, request ID, sequence, fixed
  stage, and fixed language.
* No credentials, messages, inventory rows, owner/session IDs, provider
  details, or exception text appeared in status frames.
* JSON clients remained authenticated and compatible.
* No database/RLS change was introduced.
* The open concurrency finding crosses request/session truth within one owner.
  Although the stage enum itself is not sensitive, it is a High integrity and
  request-isolation failure because the receiving shopper can see work that
  belongs to another active shopper request.
* Production was not accessed or mutated.

### Scope Compliance

* The implementation stayed within the approved source/test boundaries.
* The Send-button spinner JSX and behavior were preserved.
* No timer rotation, simulated progress, polling, WebSocket, persistence,
  database migration, new dependency, external service, deployment, legal
  change, or production mutation was added.
* QA modified no product code, release state, PRD, architecture,
  implementation report, reviewer artifact, or final report.
* Only this QA-owned report was created.

### Coverage Limitations

* Production was intentionally not tested.
* `understanding_request` is permitted to be omitted by the architecture and
  was not emitted by the current one-shot classifier; its exact 18-entry copy
  mapping and direction were covered by Vitest.
* The concurrency defect was reproduced deterministically at the real engine
  request seam rather than by attempting to synchronize two nondeterministic
  external model calls in browsers. The test uses the same shared instance
  fields and handler methods as production.
* Full release E2E and F15 remain outside this QA assignment.

Attempt Result: FAIL — one High open finding violates truthful same-request status delivery.

## Attempt 2

### Environment

* Date: 2026-07-30 (Asia/Karachi).
* QA mode: `POST_IMPLEMENTATION` bounded-repair verification, repair cycle
  `1/2`.
* Frozen product repair commit:
  `0e204f50216cb3197e08e623b50163040a4da27c`.
* Repair files: `backend/api.py`, `backend/engine.py`,
  `tests/test_f16_processing_status.py`, and
  `tests/test_engine_build_clarification.py`.
* The Flask backend on `127.0.0.1:8001` was stopped and restarted from the
  frozen repair HEAD before browser checks.
* The existing frontend remained at `http://localhost:5001`.
* Staging Playwright used the refreshed authorized
  `tests/e2e/qa-storage-state.json`.
* Authorized non-production Supabase staging and dedicated QA fixtures only;
  production remained prohibited.
* The pre-existing generated bytecode and refreshed storage-state changes
  remained uncommitted and were not overwritten.

### QA Summary

The repair removes request-derived reporter, intent, and language fields from
the shared cached engine and carries them in a new request-owned
`ChatRequestContext`.

The exact deterministic interleaving that failed Attempt 1 now passes: request
A alone receives its two genuine search statuses with request A's ID, request B
receives no false status, both contexts retain their own intent/language, and
both terminal responses remain local. A second concurrent Flask stream-queue
test and a real simultaneous staging search/general pair also passed.

All affected backend contracts, JSON/SSE compatibility, TypeScript/Vitest
regressions, focused genuine staging status UI, unchanged Send spinner,
search, comparison, build, modification, and cart checks passed.
`F16-STATUS-PROPOSAL-QA-001` is verified.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Attempt 2 evidence |
| --- | --- | --- |
| `CHAT-STATUS-001` | PASS | Focused real staging Playwright again observed the existing Send spinner and typing indicator during load. |
| `CHAT-STATUS-002` | PASS | Frontend code was unchanged by the repair; the dots-only F16 Vitest regression passed. |
| `CHAT-STATUS-003` | PASS | Exact two-thread cached-engine reproduction, concurrent stream-queue test, and simultaneous live staging streams all kept events and terminal data request-local. |
| `CHAT-STATUS-004` | PASS | No frontend status-generation change occurred; F16 Vitest still rejects fake/timer rotation. |
| `CHAT-STATUS-005` | PASS | Live concurrent search retained monotonic `searching_products` then `preparing_response`; concurrent general chat emitted zero stages. |
| `CHAT-STATUS-006` | PASS | Request A retained `product_search/en`; request B retained `general_chat/roman_ur` under forced interleaving. Existing 18-copy/direction Vitest passed. |
| `CHAT-STATUS-007` | PASS | Frontend accessibility and deduplication implementation was unchanged; the affected F16 Vitest suite passed. |
| `CHAT-STATUS-008` | PASS | Focused search and embedded build/modify checks cleared the loader at the terminal result. |
| `CHAT-STATUS-009` | PASS | Safe streamed-error/abrupt-close contracts remained passing in backend and Vitest suites. |
| `CHAT-STATUS-010` | PASS | Concurrent request IDs, reporters, queues, terminal payloads, intent, and language remained isolated; neither stream contained the other request ID. |
| `CHAT-STATUS-011` | PASS | Repair introduced no database/persistence change; statuses remain request-local only. |
| `CHAT-STATUS-012` | PASS | Focused staging Playwright passed at the existing mobile viewport with no page or console errors. |

### Test Cases and Actual Results

1. Frozen repair and scope inspection:

   ```text
   git rev-parse HEAD
   git status --short
   git show --stat --oneline 0e204f5
   git diff-tree --no-commit-id --name-status -r 0e204f5
   ```

   Actual: HEAD matched the full repair commit. Four approved files changed:
   two backend source files and two focused Python tests. Only the preserved
   generated bytecode/storage-state files were uncommitted. No frontend,
   database, dependency, deployment, or production file changed.

2. Exact deterministic finding reproduction:

   An independent inline Python harness reused one
   `UnifiedIntentService`, held request A in parsing, started and held request B,
   released A, then released B.

   Actual:

   ```text
   events_a = [
     ("request-a", "searching_products", "en"),
     ("request-a", "preparing_response", "en")
   ]
   events_b = []
   context_a = ("product_search", "en")
   context_b = ("general_chat", "roman_ur")
   responses = ("Done", "Salam")
   errors = []
   threads_alive = [False, False]
   ```

   All independent assertions passed. This is the same interleaving that
   produced `events_a=[]` and placed A's stages in `events_b` during Attempt 1.

3. Focused reporter and terminal-queue isolation:

   ```text
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest -v \
     tests.test_f16_processing_status.ProcessingStatusReporterTests.test_cached_engine_keeps_concurrent_request_status_and_intent_local \
     tests.test_f16_processing_status.StreamingAdapterTests.test_concurrent_stream_queues_keep_status_and_terminal_payloads_local
   ```

   Actual: 2/2 passed. Request A's queue contained only A's statuses and result;
   request B's queue contained only B's result and no false status; neither
   body contained the other request ID or response.

4. Affected backend contract/regression suite:

   ```text
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest \
     tests.test_f16_processing_status \
     tests.test_f09_customer_response \
     tests.test_f09_language_contract \
     tests.test_f09_quota_timing \
     tests.test_f10_verified_build_generation \
     tests.test_f11_build_modifier_safety \
     tests.test_f12_lead_consent \
     tests.test_f16_lead_notifications \
     tests.test_engine_search_fallback \
     tests.test_engine_build_clarification
   ```

   Actual: 29/29 passed, including JSON/stream result parity, safe streamed
   error, status sequencing, search/build clarification, quota, build,
   modification, lead, and notification-preservation behavior.

5. Frontend/static regressions:

   ```text
   pnpm vitest run tests/f08 tests/f09 tests/f10 tests/f11 tests/f12 tests/f16
   pnpm exec tsc --noEmit
   git diff --check
   git diff --quiet -- backend/api.py backend/engine.py \
     tests/test_f16_processing_status.py \
     tests/test_engine_build_clarification.py
   ```

   Actual: 11 Vitest files and 27/27 tests passed; TypeScript, diff checks, and
   frozen repair-file checks passed.

6. Mandatory focused staging Playwright:

   ```text
   E2E_BASE_URL=http://localhost:5001 \
   E2E_STORAGE_STATE=tests/e2e/qa-storage-state.json \
   pnpm exec playwright test --config=playwright.staging.config.ts \
     tests/e2e/chat-processing-status.spec.ts
   ```

   Actual: 1/1 passed in 15.1 seconds against the restarted repaired backend.
   Genuine `Searching products` and `Preparing response` preceded the product
   result; the unchanged Send spinner appeared; terminal cleanup passed; page
   and console errors were zero.

7. Critical dedicated-fixture customer regressions:

   ```text
   pnpm exec playwright test --config=playwright.staging.config.ts \
     tests/e2e/customer-search.spec.ts \
     tests/e2e/customer-comparison.spec.ts \
     tests/e2e/customer-cart.spec.ts \
     --grep 'E2E-016|E2E-017|E2E-033'
   ```

   Actual: 3/3 passed in 1.4 minutes:

   * Search returned only active/in-stock owner inventory and rendered its
     genuine statuses.
   * Comparison retained exact owner-catalog products and missing-fact labels.
   * Cart retained session-bound offers, quantity/remove behavior, buy-intent
     validation, cancellation, and forged/replayed/expired-offer rejection.

8. Real embedded staging build and modification:

   A temporary allowed localhost embedded the real widget, generated a gaming
   build, and requested a cheaper GPU. Cleanup removed the allowed host in
   `finally`.

   Actual:

   * Build: HTTP 200 SSE; unchanged spinner; `Building your PC` then
     `Preparing response`.
   * Modification: HTTP 200 SSE; unchanged spinner;
     `Checking build changes`.
   * Terminal loader count zero; page and console errors zero.

9. Live authenticated JSON compatibility:

   Playwright sent `Accept: application/json` through the existing authenticated
   `POST /api/chat`.

   Actual: HTTP 200 `application/json`; unchanged keys
   `model,response,session_id,structured,success,trace_id`; structured type
   `message`; trace ID matched.

10. Real simultaneous staging streams:

    Playwright issued an English product search and general greeting
    concurrently for the same owner.

    Actual:

    ```text
    request A:
      searching_products/en with request A ID
      preparing_response/en with request A ID
      result with request A ID
    request B:
      no status
      result with request B ID
    ```

    Both returned HTTP 200. No stream contained the other request ID.

11. Cleanup:

    Read-only Supabase MCP SQL found zero feature QA inventory rows and zero
    temporary `127.0.0.1` allowed-host rows after the run.

### Findings

#### F16-STATUS-PROPOSAL-QA-001

* Requirement ID: `CHAT-STATUS-003`
* Severity: High
* State: `VERIFIED`
* Title: Concurrent same-owner requests can display another request's
  processing stage
* Attempt 1 actual result: Request A received no statuses; request B received
  request A's search/preparation stages through the shared cached-engine field.
* Repair verification: The same forced interleaving now delivers both request A
  statuses only to reporter A, no false status to reporter B, and keeps both
  request contexts and terminal responses local. Concurrent Flask queue tests
  and simultaneous live staging streams independently confirm the isolation.
* Resolution evidence: repair commit
  `0e204f50216cb3197e08e623b50163040a4da27c`,
  the exact reproduction output, 2/2 focused concurrency tests, 29/29 backend
  regressions, and live concurrent staging evidence above.

No open Critical, High, Medium, or Low finding remains in this feature QA.

### Edge Cases

Passed:

* Same cached engine, two concurrently interleaved request contexts.
* Status-producing search concurrent with zero-status general chat.
* Distinct intent and response language under forced overlap.
* Separate reporter sequences and request IDs.
* Separate bounded stream queues and terminal payloads.
* JSON and SSE adapters.
* Safe streamed failure and abrupt close.
* Search, comparison, build, modification, and cart regressions.
* Real mobile loader, status, spinner, terminal cleanup, and browser-error
  checks.

### Security and Ownership Checks

* The existing Next.js owner-preview/widget-session authentication remained
  unchanged.
* Reporter, parsed intent, and response language are request-owned and are no
  longer stored on the cached engine.
* Each observed status and terminal event carried only its own request ID.
* No cross-request status, terminal response, intent, or language appeared in
  deterministic, queue-level, or live staging evidence.
* No secrets, raw user content, provider errors, inventory data, or
  owner/session IDs were added to status events.
* No database/RLS, external-provider, deployment, billing, or production
  mutation occurred.

### Scope Compliance

The repair is limited to the approved finding and four files. It adds no
serialization, new service, dependency, schema, migration, frontend behavior,
timer, persistence, or out-of-scope feature. The Send-button spinner is
unchanged. QA modified only this report.

### Coverage Limitations

* Production was intentionally not tested.
* True provider calls cannot be deterministically paused at a chosen instruction
  boundary, so the exact forced interleaving was verified at the real cached
  engine seam and concurrent Flask queue seam. A real simultaneous staging pair
  supplemented that deterministic evidence.
* Full F15/release E2E remains outside this feature repair verification.

Attempt Result: PASS — the stable High finding is verified and all scoped requirements pass.

## Attempt 3

### Environment

* Date: 2026-07-30 (Asia/Karachi).
* QA disposition: final `POST_IMPLEMENTATION` repair verification, repair
  count `2/2`.
* Frozen product commit:
  `ec168ac8518a6da7c30f079bb943d6367e6afb84`.
* The Flask staging backend was stopped and restarted from that exact commit at
  `http://127.0.0.1:8001` using `.env.staging`.
* The existing Next.js staging frontend remained at
  `http://localhost:5001`.
* Browser evidence used Playwright/Chromium and the authorized owner state in
  `tests/e2e/qa-storage-state.json`.
* Only non-production Supabase staging was used. Production, deployment,
  billing, migrations, and schema mutation remained prohibited.
* The existing generated Python bytecode changes and refreshed Playwright
  storage state were preserved uncommitted.

### QA Summary

The final repair passes. QA independently verified both Reviewer findings and
reran the stable QA concurrency finding:

* `F16-STATUS-PROPOSAL-REV-001` — `VERIFIED`: the production frontend helper
  consumes a valid fragmented UTF-8 terminal result above 16 KiB, rejects a
  true result-frame overflow with an explicit result-size error, retains the
  strict 16 KiB status/error control limit, and matches the backend's JSON/SSE
  terminal payload behavior.
* `F16-STATUS-PROPOSAL-REV-002` — `VERIFIED`: empty, oversized, and
  control-character trace IDs are replaced with safe 1–64 character IDs at the
  Next.js and Flask/reporter boundaries; valid IDs are preserved; request logs,
  JSON responses, SSE headers, frames, and worker context use the trusted ID.
* `F16-STATUS-PROPOSAL-QA-001` — remains `VERIFIED`: the exact cached-engine
  and concurrent stream-queue reproductions keep reporters, status stages,
  request IDs, intent/language, and terminal results request-local.

All affected backend, frontend, type, compile, diff, JSON/SSE, focused staging,
product-card, and verified-build checks passed. The initial dots-only behavior
and the existing Send-button spinner remain unchanged.

### Requirement / Acceptance Matrix

| Requirement ID | Result | Attempt 3 evidence |
| --- | --- | --- |
| `CHAT-STATUS-001` | PASS | Focused staging Playwright observed the existing Send-button spinner during the live request; the source assertion still matches the unchanged `Loader2` spinner. |
| `CHAT-STATUS-002` | PASS | F16 frontend regression confirms dots-only loading remains before the first genuine status. |
| `CHAT-STATUS-003` | PASS | Trace IDs are trusted-boundary normalized, valid IDs are preserved, and both concurrency reproductions remain isolated. |
| `CHAT-STATUS-004` | PASS | No timer, random rotation, or guessed frontend status was introduced; the existing source regression passed. |
| `CHAT-STATUS-005` | PASS | Focused staging emitted genuine `Searching products` then `Preparing response`; backend sequencing/deduplication tests passed. |
| `CHAT-STATUS-006` | PASS | All 18 approved stage/language mappings and LTR/RTL directions passed unchanged. |
| `CHAT-STATUS-007` | PASS | Existing live-region and deduplication behavior passed the affected F16 suite. |
| `CHAT-STATUS-008` | PASS | A fragmented 21,090-byte UTF-8 result frame completed through the production helper; a 20,000-character backend result retained JSON/SSE parity; real over-limit results fail explicitly and safely. |
| `CHAT-STATUS-009` | PASS | Server failure and over-limit result paths emit one bounded safe terminal error; frontend error/abrupt-close checks passed. |
| `CHAT-STATUS-010` | PASS | Unsafe trace IDs did not reach live response frames or direct request logs; stream header/frame IDs matched; concurrent queues remained request-local. |
| `CHAT-STATUS-011` | PASS | Repair introduced no persistence or database change; statuses remain transient. |
| `CHAT-STATUS-012` | PASS | Focused mobile staging test completed with loader cleanup and no page/console assertion failure. |

### Test Cases and Actual Results

1. Frozen repair and scope:

   ```text
   git rev-parse HEAD
   git status --short
   git show --check --stat --oneline HEAD
   ```

   Actual: HEAD matched `ec168ac8518a6da7c30f079bb943d6367e6afb84`.
   The repair contains seven approved source/test files and no database,
   dependency, deployment, billing, or Send-button change. The seven repair
   files had no uncommitted delta.

2. Independent production-helper frame-limit reproduction:

   Node 22 imported
   `components/chat/processing-status.ts` directly and passed a multibyte
   terminal result as nine deliberately fragmented chunks.

   Actual:

   ```text
   fragmented UTF-8 frame bytes: 21090
   terminal response characters: 12000
   result overflow: "The chat result exceeded the supported stream size."
   control overflow: "The chat response stream contained an oversized control frame."
   ```

   The fragmented result resolved with the exact payload. The result overflow
   and control overflow rejected explicitly; neither was silently discarded.

3. Focused backend and frontend repair contracts:

   ```text
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest -v \
     tests.test_f16_processing_status

   pnpm vitest run \
     tests/f16/processing-status.test.ts \
     tests/f16/chat-request-id.test.ts
   ```

   Actual: backend 10/10 passed; frontend 13/13 passed. Evidence includes
   20,000-character JSON/SSE parity, one safe `CHAT_RESPONSE_TOO_LARGE`
   terminal error, strict control-frame rejection, fragmented frontend
   delivery, and safe trace-ID replacement/preservation.

4. Exact stable concurrency finding:

   ```text
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest -v \
     tests.test_f16_processing_status.ProcessingStatusReporterTests.test_cached_engine_keeps_concurrent_request_status_and_intent_local \
     tests.test_f16_processing_status.StreamingAdapterTests.test_concurrent_stream_queues_keep_status_and_terminal_payloads_local
   ```

   Actual: 2/2 passed. Request A alone received A's two genuine statuses and A's
   terminal payload; request B received no false status and only B's terminal
   payload. No request ID, response, intent, or language crossed contexts.

5. Affected backend regression suite:

   ```text
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m unittest \
     tests.test_f16_processing_status \
     tests.test_f09_customer_response \
     tests.test_f09_language_contract \
     tests.test_f09_quota_timing \
     tests.test_f10_verified_build_generation \
     tests.test_f11_build_modifier_safety \
     tests.test_f12_lead_consent \
     tests.test_f16_lead_notifications \
     tests.test_engine_search_fallback \
     tests.test_engine_build_clarification
   ```

   Actual: 32/32 passed.

6. Frontend and static regressions:

   ```text
   pnpm vitest run tests/f08 tests/f09 tests/f10 tests/f11 tests/f12 tests/f16
   pnpm exec tsc --noEmit
   PYTHONDONTWRITEBYTECODE=1 venv/bin/python -m py_compile \
     backend/api.py backend/processing_status.py
   git diff --check
   ```

   Actual: 12 Vitest files and 34/34 tests passed. TypeScript, Python compile,
   whitespace, and frozen-file checks passed.

7. Live JSON and trace-ID boundary compatibility:

   Authenticated Playwright sent one JSON request with a valid bounded ID and
   one SSE validation request with a control-character ID through the real
   Next.js proxy and restarted Flask backend.

   Actual:

   ```text
   JSON: HTTP 200 application/json; valid trace preserved in header and body
   SSE: HTTP 200 text/event-stream; unsafe trace replaced
   SSE header ID == terminal frame request_id
   unsafe client text absent from the stream
   ```

   A separate direct Flask harness captured `start_request_trace`,
   `chat.request.received`, and the validation response. All used the same
   normalized ID, and the unsafe value was absent from captured logs.

8. Mandatory focused staging Playwright:

   ```text
   pnpm exec playwright test \
     tests/e2e/chat-processing-status.spec.ts --reporter=line
   ```

   Actual: 1/1 passed in 18.9 seconds against the restarted repair backend.
   Genuine search and preparation statuses preceded the terminal product
   result; the existing Send spinner appeared; mobile cleanup and browser-error
   assertions passed.

9. Product-card and verified-build regressions:

   ```text
   pnpm exec playwright test \
     tests/e2e/customer-search.spec.ts \
     tests/e2e/customer-build.spec.ts \
     --grep 'E2E-016|E2E-019' --workers=1
   ```

   Actual: 2/2 passed in 1.5 minutes.

   * Search returned only active/in-stock owner inventory, rendered the seeded
     RAM product card with exact `16 GB`, retained ISO currency, showed genuine
     statuses, and cleared the loader.
   * Gaming, editing, office, and general-use requests each produced a complete
     customer-safe verified build with all eight categories, positive prices,
     no missing category, and no budget overrun.

10. Cleanup:

    A read-only staging Supabase REST check found zero remaining
    `QA-SEARCH-RAM-*` or `QA-SEARCH-ARCHIVED-GPU-*` inventory fixtures. The E2E
    `finally` blocks also successfully removed the temporary allowed host.

### Findings

#### F16-STATUS-PROPOSAL-QA-001

* Requirement ID: `CHAT-STATUS-003`
* Severity: High
* State: `VERIFIED`
* Attempt 3 evidence: both focused concurrency tests passed at the final frozen
  repair commit; product and build staging regressions remained green.

#### F16-STATUS-PROPOSAL-REV-001

* Requirement ID: `CHAT-STATUS-008`
* Original severity: High
* QA verification state: `VERIFIED`
* Evidence: independent fragmented 21,090-byte UTF-8 production-helper
  reproduction, explicit true over-limit rejection, strict control-frame
  rejection, backend JSON/SSE parity, and safe over-limit terminal error.

#### F16-STATUS-PROPOSAL-REV-002

* Requirement IDs: `CHAT-STATUS-003`, `CHAT-STATUS-010`
* Original severity: Medium
* QA verification state: `VERIFIED`
* Evidence: focused Next.js/Flask tests, authenticated live proxy checks, and
  captured Flask trace-start/log/response evidence.

No open QA finding or independently unverified Reviewer finding remains.

### Security and Ownership Checks

* Client-provided trace IDs are untrusted until normalized to
  `^[A-Za-z0-9_-]{1,64}$`.
* Valid bounded IDs remain stable for correlation.
* Invalid IDs are replaced before backend request tracing, application logs,
  response headers, status/error/result frames, reporter state, and worker
  thread names.
* Result and control frames are UTF-8 byte bounded, with explicit safe failure
  behavior.
* Request-local concurrency isolation remains verified.
* No secret, raw provider error, cross-owner data, database/RLS, external
  provider, deployment, billing, or production mutation was introduced.

### Scope Compliance

The final repair is limited to the two Reviewer findings and their focused
tests. It does not change the approved status vocabulary, add guessed UI text,
touch the Send-button spinner, add persistence, alter schema, or add a
dependency. QA modified only this report.

### Coverage Limitations

* Production was intentionally not tested.
* The focused build regression exercised all four supported purposes but did
  not rerun the entire release E2E suite.
* The Reviewer report remains a separate role-owned artifact; this QA attempt
  records independent repair verification and does not edit the Reviewer's
  historical finding states or final line.

Attempt Result: PASS — both Reviewer repairs and the stable QA concurrency
finding are verified at the final frozen commit; all scoped checks pass.

## Status

STATUS: PASS
