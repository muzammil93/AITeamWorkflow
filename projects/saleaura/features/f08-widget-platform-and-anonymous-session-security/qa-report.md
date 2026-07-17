# QA Baseline Report — F08 Widget Platform and Anonymous Session Security

## Existing-Code Findings — 2026-07-17

* `F08-QA-001` — Widget routes expose an owner ID in the URL and no exact allowed-host validation exists (`WIDGET-003`, `WIDGET-004` fail).
* `F08-QA-002` — `/api/chat` forwards browser-controlled `user_id` and `session_id`; there is no signed bootstrap credential or durable anonymous-session exchange (`WIDGET-005`, `WIDGET-006` fail).
* `F08-QA-003` — Anonymous session history/build state has no bounded, protected persistence (`WIDGET-007` fails).
* `F08-QA-004` — The chat-message database policy permits public inserts and no layered widget abuse boundary is established (`WIDGET-008`, `SEC-CHAT-001` fail).
* `F08-QA-005` — Voice recorder/audio components remain in the widget code path; public-widget removal has not been proved (`WIDGET-009` fails).

Attempt Result: FAIL

Attempt Result: FAIL

## Verification Attempt — 2026-07-17

Evidence:

* 103 automated TypeScript/Vitest tests and TypeScript typecheck passed during F08 implementation.
* Staging migration `f08_widget_session_security` applied successfully; `widget_allowed_hosts` and `widget_sessions` exist with RLS enabled.
* CEO reported successful Playwright validation in the dedicated QA thread after configuring the widget bootstrap secret and allowed localhost host.

Result: The secure bootstrap/session flow, origin enforcement, owner host management, and public widget chat path passed the accepted staging QA run. No open F08 finding remains.

Attempt Result: PASS

STATUS: PASS
