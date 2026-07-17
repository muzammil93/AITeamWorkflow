# Architecture — F12 Lead Capture and Owner Notifications

Use a server-generated owner/session/form idempotency key, explicit consent in the submitted form, and a database-backed lead context JSON field. Persist through the quota RPC first, then issue best-effort owner notifications. No customer WhatsApp messaging is added.

STATUS: ARCHITECTURE_READY
