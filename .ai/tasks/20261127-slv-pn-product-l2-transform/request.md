# Request

## User outcome

Three Silver L2 tables exist and recompute from the closed L1 product mapping: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, and `slv_pn_hotel_rate_offer`. The shared transform library can soft-delete a row that is still present in the build when the build supplies a delete flag. Existing nodes keep today's MERGE behavior.

## Scope

### In scope

- The three L2 tables, their grain and keys, technical columns, and the node notebooks that own them.
- Registering those tables only where the architecture edit list names a `TABLE_SPECS` or ctrl row.
- One opt-in delete-flag branch in `NB_LIB_TRANSFORM_SLV_GLD`, default off.

### Out of scope

- Changing columns, grain, or keys of the 13 `slv_pn_product*` and `slv_pn_hotel*` L1 tables.
- Re-deciding business rules or the silver/gold layer split.
- `variants_json`, an LLM, destination, `source_id`, and `poi_id` on the three L2 tables.
- Task `20261127-slv-pn-product-business-mapping` (read-only source of Q-19 through Q-24 and option B).

## Acceptance criteria

- L1 tables above stay unchanged in columns, grain, and keys.
- Names and grain: `slv_pn_product_sale` (`product_id`), `slv_pn_hotel_room_offer` (`room_type_id`), `slv_pn_hotel_rate_offer` (`rate_plan_id`).
- `valid_from` and `valid_to` copy 1-1. NULL stays NULL. No sale flag is derived from those columns. The open `EPOCH_S_TS` unit is inherited from L1 and is not assigned here.
- A NULL price stays NULL. The value 0 is not written in its place.
- `slv_pn_product_sale.is_bookable` is false when no variant has `status = active` and `deleted = false`.
- `row_hash` covers the key and the business columns in Field Mapping order. Timestamps inside the hash use `unix_micros`. Outside the struct: `row_hash`, `created_at`, `updated_at`, `deleted_at`, and the delete flag.
- `deleted_at` keeps the timestamp of the first run that sees a delete. A later run sets it to NULL when L1 `deleted = false`. When an id disappears from L1, business columns keep the last computed values.
- The delete flag comes from the build and is not stored as a column. The lib default still soft-deletes only ids missing from the build. Old nodes do not change behavior while the flag defaults off.
- The three L2 tables have no `variants_json`, LLM output, destination, `source_id`, or `poi_id`.

## Constraints

- Q-19 through Q-24 and `docs/context/mapping_slv_pn_product_l2.md` win when current code disagrees.
- A rule that is not in those sources, or in option B of the prior architecture, stops that line as a question.
- No `run-author --kind analysis` and no `run-author --kind proposal`.
- Do not edit task `20261127-slv-pn-product-business-mapping`.

## Classification rationale

- Complexity: medium. Three new tables and one opt-in MERGE branch. Not a fast lane.
- Risk: medium. The new branch is opt-in and existing nodes stay on the default path. Rollback is reverting the notebooks. Local tests can prove the branch.
- Architecture: required. New grain and keys, plus a MERGE delete branch in the shared lib.
- Evidence: not required. L1 shape, the post-id probe, and Q-19 through Q-24 are already closed. The epoch unit stays unresolved because the copy is 1-1.
- Runtime proof: not required at classification. A Fabric run is only added if architecture requires it.
- Reviewer routing: `sql-data-reviewer` for the MERGE, `spark-runtime-reviewer` for the lib and node notebooks, `state-correctness-reviewer` for `deleted_at` retention and missing-id soft delete. Signals: `data_model_change`, `idempotency`, `stateful_logic`.
