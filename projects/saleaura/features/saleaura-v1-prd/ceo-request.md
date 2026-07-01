# CEO Request

Create the Product Requirements Document for SaleAura V1.

The PRD must document both:

* The current SaleAura product state.
* The target production-ready SaleAura V1.

SaleAura V1 is intended for a public paid launch and is focused specifically on custom PC builders and PC component businesses.

## Locked Product Direction

* Target market: PC component retailers, custom PC builders, PC-focused e-commerce businesses, and system integrators.
* Customer scope: anonymous customers using an embedded chat widget; no customer accounts for V1.
* Owner scope: one owner account per business; no staff/team accounts for V1.
* Language support: English, Urdu, and Roman Urdu.
* Plans are locked for now:
  * Free: 30-day trial, 100 inventory items, 25 leads/month, 500 AI responses/month.
  * Starter: $19/month, 500 inventory items, 150 leads/month, 2,000 AI responses/month.
  * Growth: $49/month, unlimited inventory items, 600 leads/month, 8,000 AI responses/month.
* Voice input and text-to-speech are deferred and should be hidden for V1.
* Customer-facing WhatsApp chat is parked for later discussion.
* Public-launch deployment and migration away from legacy Replit setup are parked for later discussion before deployment.
* Existing owner email and WhatsApp lead notification behavior should remain unchanged for this PRD.

## Inventory Direction

* Supabase inventory is the runtime source of truth.
* Every product must have a unique SKU.
* Existing products without SKUs should receive stable generated legacy SKUs; owners may later replace them with unique custom SKUs.
* CSV, manual entry, and Google Sheets inventory sources must be supported.
* Google Sheets V1 should support one active spreadsheet and one active worksheet/tab per owner, with manual connected sync.
* Google Sheets products should be read-only inside SaleAura; users must see a clear explanation.
* Google Sheets image editing should happen through the sheet for V1.
* CSV/manual products can be edited inside SaleAura.
* Blank imported cells should clear existing values.
* Missing products should be archived only when explicit mirror mode is enabled.
* Products auto-archived by mirror-mode sync should reactivate if they return to the sheet.
* Owner-manually archived products should remain archived even if they return to the sheet.
* Zero-stock products should remain visible to owners but hidden from customers.
* Product images should support imported URLs and direct Cloudinary upload where editing is allowed.
* Existing partial-import behavior should remain: update existing products, insert only permitted new products, and provide a failed-row report.

## PC Build Direction

* `build_modify` is required for V1.
* V1 builds should focus on GPU-based tower PCs for gaming, editing/content creation, and general performance.
* V1 should not claim verified support for office/integrated-graphics builds, peripherals, monitors, OS, multi-GPU builds, custom water loops, or multi-storage/multi-RAM-kit optimization unless later approved.
* Verified builds require CPU, discrete GPU, motherboard, one RAM kit, one primary SSD, PSU, case, and a valid CPU cooling solution.
* CPU cooling may be satisfied by a verified included stock cooler or by a compatible cooler inventory item.
* `build_modify` must preview changes before confirmation and show old component, replacement, dependent changes, price difference, new total, stock, compatibility result, and budget impact.
* Required build components must not be removable.
* Dependent changes must be explicit and require confirmation.
* Compatibility verification and build eligibility must be category-wise, not a single generic product flag.

## Performance Reference Direction

* SaleAura V1 must include a Supabase-backed CPU/GPU performance reference catalog.
* The catalog should cover common desktop consumer CPUs and GPUs relevant to custom PC builders.
* Imported CPU/GPU inventory should be normalized and matched against this catalog.
* Matched products receive a verified SaleAura performance score.
* Unmatched products remain searchable but are not eligible for verified upgrade/downgrade decisions until matched or reviewed.
* Scores should come from a curated SaleAura reference catalog based on trusted benchmark sources, not user-entered guesses or AI-only inference.

## Known Development Concerns to Capture

* The current product is not production-ready.
* Current build generation, build modification, compatibility validation, widget UI, imports, tests, and security need hardening.
* Important security finding to carry into development: `public.leads` currently has RLS disabled in staging and must be fixed during development.

## Requested Output

Create the Product Manager PRD artifact only.

Do not create architecture.
Do not implement code.
Do not modify agent prompts, templates, orchestrator files, or product code.

STATUS: CEO_REQUEST_CREATED
