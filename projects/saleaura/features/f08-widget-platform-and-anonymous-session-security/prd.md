# Product Requirements Document — F08 Widget Platform and Anonymous Session Security

## Scope

Create a secure public widget platform without exposing owner IDs, trusting browser page URLs, or granting direct anonymous database writes.

## Requirements

* `WIDGET-001` — Persist owner branding and exact approved hostnames.
* `WIDGET-002` — Provide owner-authenticated preview and a non-secret installation snippet.
* `WIDGET-003` — Match only normalized exact hostnames; prohibit wildcards and suffix matches.
* `WIDGET-004` — Validate the request `Origin` during bootstrap.
* `WIDGET-005` — Issue a signed short-lived bootstrap credential, then exchange it for a durable anonymous session.
* `WIDGET-006` — Bind the session to one shop and keep session secrets server-side.
* `WIDGET-007` — Persist only bounded structured history/current build state for that session.
* `WIDGET-008` — Apply active subscription checks and layered abuse controls before chat work.
* `WIDGET-009` — Remove voice input and text-to-speech controls from public widget UI.
* `SEC-CHAT-001` — Remove unrestricted chat/session writes and protect records by service/owner boundaries.

## Out of Scope

Third-party CAPTCHA, scheduled background moderation, voice/TTS functionality, and F09 conversation/recommendation changes.

STATUS: PRD_READY
