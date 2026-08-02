# QA Baseline Report — F15 Integrated Production-Readiness Gate

## ChatWidget Readiness Slice — 2026-07-26

Read-only audit of the current public widget and existing feature evidence found that F08/F09/F12 provide secure sessions, owner-scoped active/in-stock search, safe responses, and consented lead persistence. The end-to-end sales flow is incomplete: live greeting differs from configuration, product availability is visually misleading, and no cart/final-cart lead journey exists.

The new product behavior is recorded as F16 under release-plan change control `CC-001`. F16 now covers the chat-card/cart integration with F10/F11; their deterministic generation/modification safety remains under their approved requirements and receives regression coverage.

## Result

F15 cannot pass the anonymous shopper production-readiness gate until F16 is implemented, QA-passed, and reviewed. This is a routing result, not an F15 implementation backlog.

Attempt Result: FAIL

STATUS: BASELINE_FAIL_ROUTED_TO_F16
