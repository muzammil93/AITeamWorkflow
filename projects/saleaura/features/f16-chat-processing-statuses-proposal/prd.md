# Product Requirements Document

## Feature Name

Backend-Driven Chat Processing Statuses

## Feature ID and Execution Mode

`F16-STATUS-PROPOSAL` — standard new-behavior proposal, approval-gated.

This proposal is not yet part of the CEO-approved SaleAura V1 release plan.
Architecture planning may follow this PRD, but product implementation may begin
only after the CEO approves both plans and the Orchestrator records any required
release-plan change control.

## CEO Request

Replace the chat typing indicator's misleading hardcoded visible text with
truthful customer-facing processing statuses reported by the backend while the
corresponding work is genuinely occurring. Preserve the current Send-button
spinner unchanged, keep the loading state clear and accessible, and make the
smallest change compatible with the existing chat widget.

## Master Requirement References

The following approved requirements constrain this proposal but do not, by
themselves, authorize the new customer-visible behavior:

* `CHAT-001` — English, Urdu, and Roman Urdu response behavior.
* `CHAT-002` — Structured intent, action, and response contracts.
* `CART-008` — Clear widget failure and cancellation states.
* `CART-010` — Reachable and readable desktop and mobile widget content.
* `REL-005` — Multilingual, mobile, loading, empty, and failure validation.

## Dependency References

* F08 widget/session behavior so a status belongs only to the active anonymous
  request and session.
* F09 chat processing and structured response behavior.
* F10 verified-build generation and F11 build-modification processing where
  those stages are reported.
* Existing F16 chat widget loading indicator and responsive presentation.

## Baseline QA Findings

`NOT_APPLICABLE`

This is a new customer-visible behavior request, not a repair already covered by
the approved F16 PRD.

## Clarifying Questions

No clarification required.

## Finalized Scope

### In Scope

* Keep the existing assistant avatar and animated typing dots as the immediate
  visual loading indication after a chat request starts.
* Show no visible processing text until the backend reports an active,
  customer-meaningful work stage for that request.
* Display the latest valid backend-reported stage only while that work is
  genuinely in progress.
* Allow sequential status changes within one request when the backend genuinely
  moves between stages.
* Use this minimal approved customer-facing status vocabulary:

| Meaning | English | Urdu | Roman Urdu | Truth condition |
| --- | --- | --- | --- | --- |
| Request interpretation | Understanding your request | آپ کی درخواست کو سمجھا جا رہا ہے | Aap ki request samjhi ja rahi hai | The backend is actively classifying the request or extracting its language/preferences. |
| Inventory search | Searching products | مصنوعات تلاش کی جا رہی ہیں | Products talash kiye ja rahe hain | The backend is actively querying or ranking eligible owner inventory. |
| Product comparison | Comparing products | مصنوعات کا موازنہ کیا جا رہا ہے | Products ka muqabla kiya ja raha hai | The backend is actively preparing a requested inventory comparison. |
| Verified build generation | Building your PC | آپ کا پی سی بنایا جا رہا ہے | Aap ka PC build tayar kiya ja raha hai | The backend is actively selecting or deterministically validating a requested build. |
| Build modification | Checking build changes | بلڈ کی تبدیلیاں چیک کی جا رہی ہیں | Build ki tabdeeliyan check ki ja rahi hain | The backend is actively preparing, revalidating, or applying a requested build change. |
| Response composition | Preparing response | جواب تیار کیا جا رہا ہے | Jawab tayar kiya ja raha hai | The backend is actively composing or assembling the customer response. |

* Match the visible status language to the active chat response language:
  English, Urdu, or Roman Urdu. Urdu status text is right-to-left; English and
  Roman Urdu are left-to-right.
* Keep the status ephemeral: it is part of the in-progress loader and is not
  saved as a customer or assistant chat message.
* Remove the status and typing indicator when the response completes, the
  request fails, or the active request is cancelled/aborted.
* Ignore late or stale status updates from a completed, failed, cancelled, or
  superseded request.
* Preserve the widget's existing safe response/error outcome after a failure;
  the processing status must not replace or obscure that outcome.
* Expose status changes through a polite assistive-technology announcement
  without moving keyboard focus or repeatedly announcing an unchanged status.
* Validate the behavior at desktop and mobile widget widths.

### Out of Scope

* Any visual, behavioral, copy, timing, or accessibility change to the existing
  Send-button spinner.
* Timer-driven rotation, random status selection, frontend inference from the
  customer's words, fixed minimum display times, simulated progress, percentage
  completion, elapsed-time estimates, or completion estimates.
* A new generic visible fallback phrase before the first genuine backend status;
  the existing dots remain sufficient during that interval.
* New customer cancel controls. This proposal only defines cleanup when an
  existing request is aborted or cancelled.
* Persisting processing statuses in chat history, Supabase, owner dashboards,
  analytics, or audit logs.
* Owner-customizable status wording, additional status themes, or changes to
  other loaders outside the chat typing indicator.
* Changes to search, comparison, build, modification, cart, lead, quota,
  entitlement, inventory, or AI decision behavior.
* Database migrations, new external services, deployment changes, production
  mutation, or changes to the approved Send action.
* Product-code implementation before explicit CEO approval of the Product
  Manager and Architect plans and completion of required change control.

## Assumptions

* A chat request may complete too quickly for one or more statuses to be
  meaningfully seen; no status is delayed or kept visible merely for display.
* Some requests legitimately use only a subset of the approved statuses. For
  example, a general component question must not show `Searching products`
  unless inventory search actually occurs.
* The existing typing dots remain visible throughout the active request even
  when no customer-facing stage is available.
* The backend is authoritative for whether a stage is active. The frontend may
  localize and present a reported stage but may not invent, reorder, or
  time-rotate stages.
* Architecture will define the smallest compatible delivery contract without
  changing the product meanings or truth conditions in this PRD.
* Existing safe chat error messaging and existing request cancellation/abort
  behavior remain authoritative.

## User Stories

* As a shopper, I want the loader to describe only work SaleAura is actually
  doing so that I am not misled while waiting.
* As a shopper, I want a clear loading indication even before a meaningful
  backend stage is available.
* As an English, Urdu, or Roman Urdu shopper, I want processing statuses in the
  language and direction of my conversation.
* As a keyboard or screen-reader user, I want status changes announced without
  losing my focus or hearing the same message repeatedly.
* As a shopper whose request fails or is cancelled, I want the loader and stale
  status to disappear so the widget does not appear permanently busy.

## Functional Requirements

* `CHAT-STATUS-001` — Starting a chat request must preserve the existing
  assistant typing dots and the existing Send-button spinner behavior.
* `CHAT-STATUS-002` — The typing indicator must show no visible status text
  before a valid stage is reported by the backend.
* `CHAT-STATUS-003` — Every visible status must correspond to the active
  backend-reported work stage for the same request and must satisfy the truth
  condition in the approved vocabulary.
* `CHAT-STATUS-004` — The frontend must not create or change visible status text
  based on timers, random choice, message-content inference, a predetermined
  sequence, or simulated progress.
* `CHAT-STATUS-005` — A request may show zero, one, or multiple reported
  statuses. A completed stage may be replaced only by the next genuinely active
  reported stage; it must not be held visible for a minimum duration.
* `CHAT-STATUS-006` — Status text must use the active response language:
  English, Urdu, or Roman Urdu, with correct text direction.
* `CHAT-STATUS-007` — The active status must be exposed as a polite live status
  for assistive technology, must not take keyboard focus, and must not announce
  an unchanged value repeatedly.
* `CHAT-STATUS-008` — A successful terminal response must remove the processing
  status and typing indicator before or when the response becomes available.
* `CHAT-STATUS-009` — A failed request must remove the processing status and
  typing indicator and preserve the existing safe, retryable error experience.
* `CHAT-STATUS-010` — Cancellation, abort, navigation, or request replacement
  must clear that request's status, and later updates from it must not affect the
  current widget.
* `CHAT-STATUS-011` — Processing statuses must remain ephemeral and must not
  appear as persisted chat-history messages after reload.
* `CHAT-STATUS-012` — Status presentation must remain readable without
  horizontal overflow at the existing supported desktop and mobile widget
  widths.

## Acceptance Criteria

* Before any backend stage is reported, the typing indicator shows only the
  assistant visual and animated dots; no hardcoded visible processing phrase is
  present.
* During an actual owner-inventory search, `Searching products` is displayed in
  English, `مصنوعات تلاش کی جا رہی ہیں` in Urdu, or
  `Products talash kiye ja rahe hain` in Roman Urdu, according to the active
  response language.
* A general request that does not execute inventory search never displays the
  inventory-search status.
* A comparison, verified-build, or build-modification request shows its
  corresponding status only if and while that backend stage executes.
* If the backend reports multiple genuine stages, the visible text follows
  those reports without timer-based rotation, predetermined sequencing, or
  minimum display duration.
* If the backend reports no customer-facing stage, the request can still finish
  normally with dots-only loading.
* Completion clears the typing indicator and status; the final assistant
  response remains visible and the status is not added to chat history.
* A backend or network failure clears the loader/status and leaves the existing
  safe error/retry outcome usable.
* Cancellation or abortion clears the loader/status, and a late update from the
  old request cannot overwrite the next request's loading state.
* Screen-reader inspection identifies the changing text as a polite status,
  keyboard focus remains unchanged, and the same unchanged value is not
  repeatedly announced.
* English and Roman Urdu statuses render left-to-right, Urdu renders
  right-to-left, and the indicator remains readable without horizontal overflow
  at the existing desktop and mobile widget widths.
* Regression verification confirms the Send-button spinner is unchanged and
  existing chat response, error, session, search, comparison, build,
  modification, cart, and lead behavior still works.
* Automated contract/component coverage and staging Playwright evidence cover
  normal status progression, no-status loading, multilingual direction,
  malformed/unknown/stale status rejection, completion, failure, cancellation,
  desktop, mobile, accessibility, and the unchanged Send-button spinner.

## Risks / Open Questions

* Status delivery must remain timely enough to be useful without delaying the
  actual response. Architecture must stop if the existing request transport
  cannot deliver genuine in-progress stages without a disproportionate rewrite.
* Rapid status changes can create visual or assistive-technology noise. The
  product permits omission of very short stages but does not permit artificial
  display delays or frontend timing rules.
* Any future status meaning or customer-facing wording beyond the six approved
  entries requires a separately reviewed product change; unknown statuses must
  not be displayed as raw customer text.
* Release-plan authorization remains open. CEO approval of this PRD and the
  Architect plan is required before the Orchestrator may record change control
  and route implementation.

## Status

STATUS: PRD_READY
