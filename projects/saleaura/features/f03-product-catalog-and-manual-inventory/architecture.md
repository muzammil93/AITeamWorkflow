# Architecture

## Feature ID and Name

`F03 — Product Catalog and Manual Inventory`

## Architecture Mode

Delta architecture after QA-first baseline failure

## Inputs

* F03 CEO request ending `STATUS: CEO_REQUEST_CREATED`
* F03 baseline QA report ending `STATUS: FAIL`
* F03 delta PRD ending `STATUS: PRD_READY`
* SaleAura V1 master architecture
* Integrated F01 owner-authenticated route/session boundaries
* Integrated F02 entitlement and inventory-quota boundaries

## Design Goals

* Introduce one durable product identity model without rewriting the whole import stack.
* Preserve current upload/listing workflows while removing loose name/category identity authority.
* Separate owner inventory reads from customer-safe product reads.
* Enforce Google-managed read-only behavior through product metadata, not UI convention only.
* Preserve zero-stock and archived owner visibility while hiding those products from customer flows.
* Keep later F04–F07 work additive by creating stable fields and trusted boundaries now.

## Component Design

### Canonical product identity

Extend the inventory row into a canonical product model.

Add to `inventory`:

* `sku`
* `normalized_sku`
* `source_type`
* `source_reference`
* `source_row_key`
* `is_active`
* `archive_reason`
* `archived_at`

Add alias table:

* `inventory_sku_aliases`
  * `user_id`
  * `inventory_id`
  * `sku`
  * `normalized_sku`

Rules:

1. `inventory.id` remains the immutable product identity.
2. `sku` is the current owner-visible SKU.
3. `normalized_sku` is used for uniqueness and matching.
4. Replacing a SKU inserts the previous normalized value into `inventory_sku_aliases`.
5. Unique constraints enforce owner-scoped uniqueness across both current SKUs and aliases.

Legacy backfill:

* Existing rows without SKU get deterministic generated legacy SKUs derived from row UUID.
* Existing rows default `source_type = manual` unless known safer provenance is available from an approved backfill rule.

### Matching and persistence

Refactor backend inventory normalization/planning so identity precedence becomes:

1. current SKU match;
2. alias match;
3. safe source row match;
4. bounded legacy fallback for pre-F03 rows only.

The current `_build_identity_key(name, category, brand)` and loose fallback remain usable only as transitional backfill assistance where no stronger identity exists, and must not remain the durable write authority.

`_normalize_item_for_persistence` should produce:

* canonical SKU fields when present;
* source metadata fields;
* owner-safe mutable product fields;
* visibility/state fields;
* embedding artifacts.

### Source ownership and read-only behavior

Per-row source semantics:

* `manual`: owner may create/edit/archive/reactivate/upload image.
* `csv`: owner may edit/archive/reactivate/upload image.
* `google_sheet`: owner may view but cannot edit/archive/reactivate/upload image in SaleAura.

Provide one helper, shared by Next.js and Flask boundaries:

* `isProductEditable(source_type)` or equivalent

Mutation boundaries must reject Google-managed mutations with stable code:

* `SOURCE_MANAGED_READ_ONLY`

Owner UI must render:

* source badge;
* state badge;
* read-only explanation for Google-managed rows.

### Product state

Represent state with:

* `is_active = true|false`
* `archive_reason = null | manual | source_missing`

Interpretation:

* `active`: `is_active = true`
* `manual_archive`: `is_active = false` and `archive_reason = manual`
* `mirror_archive`: `is_active = false` and `archive_reason = source_missing`
* `zero_stock`: orthogonal derived display state when `stock = 0`

This keeps zero-stock separate from archive while still hiding both from customer flows.

### Owner inventory experience

Preserve `app/inventory/page.tsx` as the main owner inventory surface, but extend it to support:

* SKU display/edit for editable products;
* source badge;
* state badge;
* manual create/edit/archive/reactivate actions;
* read-only messaging for Google-managed products.

Current upload preview/save flow remains, but the saved rows must round-trip the new product fields and state.

F03 does not need to ship the full later Google Sheets source-management UI from F07.

### Cloudinary image upload

Harden `app/api/upload-product-image/route.ts`:

1. Authenticate owner session.
2. Require a target inventory product ID.
3. Load the product by exact owner identity.
4. Reject missing/not-owned/read-only products.
5. Validate bounded image payload and safe response.
6. Return only the Cloudinary URL/public id needed by the caller.

This route becomes an owner action, not a generic public upload endpoint.

### Owner inventory APIs

Current `GET /api/inventory/[user_id]` and Flask `GET /api/inventory/<user_id>` are too broad.

Replace with owner-authenticated boundaries that derive owner identity from session/server context rather than trusting the path parameter as authorization.

Recommended shape:

* Next.js owner route(s) authenticate via Supabase server client.
* Owner inventory list returns owner-oriented DTO with SKU/source/state fields.
* Owner create/update/archive/reactivate routes call trusted backend/service functions.

The path can still include an ID if needed for lookup, but it must not be the source of authorization truth.

### Customer-safe product DTO

Introduce one allowlisted DTO for customer/search/build/widget consumers.

Suggested fields:

* `id`
* `name`
* `brand`
* `category`
* `price`
* selected safe spec/display fields
* `image_url`
* `product_url`
* `description`

Exclude:

* `user_id`
* source metadata
* archive fields
* raw internal matching fields
* future system-managed compatibility/performance internals not needed by the customer surface

All customer-facing inventory/build/search queries must use:

* exact owner;
* `is_active = true`;
* `stock > 0`;
* customer DTO projection.

### Raw inventory and embedding hardening

Remove unintended direct public raw access by changing schema/policies and application paths together.

Database direction:

* remove broad public `SELECT` on `inventory`;
* remove unintended public access to `inventory_embeddings`;
* preserve owner-authenticated reads where needed;
* keep trusted server/service-role paths for backend search/build logic.

Application direction:

* public/customer consumers stop reading raw `inventory` directly;
* owner inventory surfaces use owner-authenticated routes;
* backend search/build code fetches only customer-visible rows for customer requests.

### Search/build service compatibility with F03

F03 does not implement F04 verified eligibility rules, but it must still narrow customer-visible product selection to:

* owner’s products only;
* `is_active = true`;
* `stock > 0`.

Where the service currently returns `select('*')`, it should migrate to the customer-safe DTO or an internal trusted row shape depending on caller type.

## Database / Migration Design

Create one additive F03 migration that:

1. adds new inventory identity/source/state columns;
2. backfills deterministic legacy SKUs and default source state;
3. creates `inventory_sku_aliases`;
4. adds indexes/constraints for owner-scoped SKU uniqueness and source/state lookup;
5. updates RLS/grants for inventory and embeddings;
6. preserves F02 quota functions and owner data.

Also reconcile `supabase-schema.sql` and `lib/types/database.ts`.

### Backfill approach

Backfill must be deterministic and non-destructive:

* Existing rows keep their UUIDs.
* Generated legacy SKUs are stable and derived from immutable row identity.
* Existing rows default to editable/manual unless a safer source-specific backfill rule is explicitly available.
* No existing inventory data is deleted.

### Constraints

* owner + normalized current SKU unique
* owner + normalized alias SKU unique
* `source_type` limited to approved values
* `archive_reason` limited to `manual` or `source_missing`

## API and Service Boundaries

### Next.js

Own:

* authenticated owner inventory listing/actions;
* authenticated product-image upload;
* typed DTO responses for owner and customer surfaces where Next.js is the boundary.

### Flask

Own:

* canonical inventory normalization/planning;
* batch import save pipeline;
* trusted update/mutation helpers used by owner routes;
* internal customer-visible search/build retrieval over trusted filtered rows.

### Supabase

Own:

* durable inventory identity/source/state fields;
* alias uniqueness and archival state;
* RLS/grant hardening;
* owner- and customer-safe data separation.

## Test Strategy

Add focused evidence for:

* legacy SKU backfill and owner-scoped uniqueness;
* SKU replacement creates alias and preserves row identity;
* source-type editable vs read-only behavior;
* archive/reactivate state transitions;
* zero-stock/archived customer filtering;
* customer DTO projection;
* denial of unintended raw public inventory/embedding access;
* authenticated product-image upload restrictions.

Use:

* TypeScript tests for route/helper/DTO behavior;
* Python tests for inventory normalization/matching logic;
* executable SQL tests for backfill, constraints, and RLS/grants.

## Status

STATUS: ARCHITECTURE_READY
