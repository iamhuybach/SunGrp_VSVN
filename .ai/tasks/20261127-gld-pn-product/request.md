# Request

## User outcome

One gold serving table, `lh_vv_gold.dbo.gld_srv_product_offer`. One row per `product_id`. Holiday and hotel share the table. Variant facts sit in `variants_json`. Gold attaches `poi_id` and copies `destination_id` from `slv_enr_poi_destination`.

## Scope

### In scope

- The table, grain, and columns in `docs/context/mapping_gld_srv_product_offer.md` §1.
- A recompute gold transform that reads silver only. Sources are the three Q-19 L2 tables plus the L1 tables named in that mapping, then `slv_enr_poi_destination`.
- DDL for `gld_srv_product_offer` and the pipeline edge named by the Architect `Main brief`.

### Out of scope

- A destination column on any silver table.
- Reading any gold table. `gld_srv_poi_info` is a type contract for `destination_id` only.
- Joining `ai_poi`, remapping `destination_id`, or a fallback destination constant.
- Decoding or changing prices. The L2 decoder change in D-1 is another task.
- A sale flag derived from `valid_from` and `valid_to`.
- A new proposal or problem analysis.

## Acceptance criteria

- The gold table is `gld_srv_product_offer`. Grain is one row per `product_id` (U-02, D-0). Holiday `product_type` is `other`. Hotel `product_type` is `hotel`.
- `poi_id = uuid_md5(business_service_id, 'partner')`. Left join `slv_enr_poi_destination` on `poi_id`. A missing POI or destination keeps the row and leaves `destination_id` NULL (D-4). `destination_id` is the JSON array string copied unchanged (D-5).
- Prices pass through from `slv_pn_product_sale`. NULL stays NULL. Gold does not decode them (U-06, D-1).
- `variants_json` is built as mapping §1.3 and §1.5. `valid_from` and `valid_to` are inside the hotel element. No sale flag is derived from them (U-07).
- `is_bookable` is copied 1-1 from L2. `is_active` is the technical flag paired with `deleted_at` (D-8).
- A holiday product with more than one distinct `business_service_id` on `deleted = false` relation rows is dropped entirely (U-04, D-10).

## Constraints

- Do not add a business rule that is absent from `docs/context/mapping_gld_srv_product_offer.md` or from the received ledger. Record the question and stop that line.
- Mapping items still open: attribute value codes, epoch unit of `valid_from` and `valid_to`, and the shape of room `tags` and `amenities`. Do not close them in this task.
- Do not run `run-author --kind analysis` or `run-author --kind proposal`.
- The three-table `model-design.md` from 2026-11-27 is withdrawn.
- Domain for edits: the paths named by the `Main brief`.

## Classification rationale

- Complexity: medium. One gold grain over holiday and hotel silver sources.
- Risk: medium. New gold table and recompute write, with rollback by not publishing the table.
- Architecture: required. Grain, key, and the silver-to-gold boundary change.
- Evidence: the mapping task closed the shape questions. The Architect may still require a probe. Do not rerun P1–P6 unless the new architecture names them.
- Runtime proof: not required at triage.
- Reviewer routing: `sql-data-reviewer` for the gold SQL grain, join, and types; `spark-runtime-reviewer` for the Fabric recompute notebook.
- Signal: `data_model_change`.
