# QA Baseline Report — F13 Owner Dashboard

* `F13-QA-001` — Dashboard lead analytics multiply actual leads by ten and label them as potential leads, which fabricates owner data (`DASH-002`).
* Owner dashboard API routes authenticate and filter by the current owner; dashboard UI already distinguishes loading, empty, and error states.

Attempt Result: FAIL

## Verification Attempt — 2026-07-17

* Owner-scope audit confirms authenticated server routes filter leads, inventory, and chats by the current owner.
* F13 regression locks the UI to unscaled `leads` data and rejects the former fabricated identifiers.

Attempt Result: PASS

STATUS: PASS
