# Architecture — F08 Widget Platform and Anonymous Session Security

1. Add owner-scoped allowed-host records and server-only widget-session records. Revoke anonymous direct writes to chat/session tables.
2. Owner configuration APIs derive identity from Supabase session. Public bootstrap accepts only shop public ID plus browser `Origin`, validates the normalized exact hostname, checks entitlements, and signs a five-minute bootstrap JWT with a server secret.
3. Session exchange verifies the bootstrap JWT once, creates/returns an opaque random session token, stores only its hash, and binds it to one shop with expiry and bounded history state.
4. Chat verifies the opaque session token server-side and derives the shop from the session; browser `user_id` is ignored/rejected.
5. Apply per-origin bootstrap and per-session message limits; public response shape remains non-secret.
6. Widget uses bootstrap then session exchange before chat, has an owner-only preview path, and exposes no voice/TTS controls.

## Validation

Migration/RLS contracts, hostname normalization tests, bootstrap/session route tests, chat rejection tests, and browser E2E origin/session cases.

STATUS: ARCHITECTURE_READY
