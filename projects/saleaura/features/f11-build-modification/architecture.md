# Architecture — F11 Build Modification

1. Load the current `f10.v1` snapshot only through the F08 protected session state, scoped to its owner.
2. Normalize the requested modification and create a pending proposal containing the complete next component map, change set, validation, price/performance deltas, and source snapshot version.
3. Keep pending state in protected `widget_sessions.build_state`; public responses receive only customer-safe cards.
4. Require a confirm intent to re-fetch/revalidate selected inventory and write an immutable next snapshot; cancel clears only the proposal.
5. Reuse the full F04 compatibility validator and F05 verified CPU/GPU performance data. Candidate selection fails closed on inactive, out-of-stock, ineligible, or unverified critical data.

STATUS: ARCHITECTURE_READY
