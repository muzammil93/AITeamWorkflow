# Architecture — F09 Conversation Core, Search, and Comparison

1. Define a server-owned response schema and customer product DTO allowlist.
2. Classify deterministic greeting/clarification/search/comparison paths before quota consumption; charge only a successful model-backed path.
3. Load/update bounded session state through the F08 `widget_sessions` record for public widgets; retain an authenticated owner-preview adapter.
4. Search from the owner-scoped customer inventory DTO only. Comparison derives rows from those DTOs and labels missing fields instead of guessing.
5. Add language preference detection for English, Urdu script, and Roman Urdu, with safe fallback clarification.
6. Validate every public response before it leaves the API boundary.

STATUS: ARCHITECTURE_READY
