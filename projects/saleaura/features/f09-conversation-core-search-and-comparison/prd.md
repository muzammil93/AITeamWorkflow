# Product Requirements Document — F09 Conversation Core, Search, and Comparison

## Scope

Make the F08-secured widget return safe, structured multilingual search and comparison responses without fabricating inventory information or consuming quota for deterministic/non-model work.

## Requirements

* `CHAT-001` — Detect/respond appropriately in English, Urdu, and Roman Urdu.
* `CHAT-002` — Use a versioned structured intent/action/response contract.
* `CHAT-003` — Search only the session's owner inventory where products are active, in stock, customer-visible, and safe for the requested response.
* `CHAT-004` — Compare only supplied inventory facts; render unavailable fields as unavailable.
* `CHAT-005` — Return allowlisted customer-safe product, comparison, and clarification payloads.
* `CHAT-006` — Never invent catalog facts or compatibility claims.
* `CHAT-007` — Consume AI quota only after a request is determined to require a successful model-backed action.

STATUS: PRD_READY
