# CEO Request — Backend-Driven Chat Processing Statuses

## Context

The current chat request loader keeps the Send-button spinner and also shows an
animated typing indicator with hardcoded visible text. The Send-button spinner
is acceptable and must not be changed. The visible typing text is misleading
when it describes work that the backend has not actually reported.

## Requested Outcome

Plan a minimal customer-facing improvement in which the typing indicator shows
truthful processing statuses emitted by the backend, such as `Searching
products`, only while that work is genuinely occurring.

## Constraints

* Do not change the Send-button spinner.
* Do not display timer-driven, randomly rotated, inferred, or otherwise guessed
  processing text.
* Preserve a clear loading indication and accessibility.
* Keep the change minimal and compatible with the existing chat widget.
* Do not implement product code, change the release plan/state, or begin the
  Developer stage until the CEO reviews and explicitly approves the Product
  Manager and Architect plan.

## Workflow Classification

This is a new customer-visible behavior proposal related to F16. It is not yet
part of the locked SaleAura V1 release plan and remains approval-gated.

STATUS: CEO_REQUEST_RECORDED
