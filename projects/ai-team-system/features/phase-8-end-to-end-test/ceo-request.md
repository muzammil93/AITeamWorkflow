# CEO Request

Run a controlled end-to-end test of the AI Team workflow inside Codex.

The goal is to verify that the Product Manager, Architect, Developer, QA, Reviewer, and Final Report stages can execute through file-based artifacts from one CEO request.

This test should only validate the AI Team workflow itself.

Do not add new agents.
Do not add new phases.
Do not add external integrations.
Do not add dashboards.
Do not add RAG or semantic search.
Do not modify production app code.
Do not change the locked workflow.

The expected result is a complete feature folder containing:

* ceo-request.md
* prd.md
* architecture.md
* implementation-report.md
* qa-report.md
* review-report.md
* final-report.md

The workflow should finish with the final report ready for CEO review.

STATUS: CEO_REQUEST_CREATED
