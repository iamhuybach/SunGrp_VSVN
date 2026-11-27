# Author input

Rewrite `model-design.md` for `lh_vv_gold.dbo.gld_srv_product_offer` only. No `proposal.md`. Close conflicts 11 and 15: D-4 keeps a row with NULL `poi_id`, and relation counts use only `deleted = false`. Do not leave a new question. This task writes the mapping document only. Do not design a notebook edit.

## Ledger

- U-01 table `lh_vv_gold.dbo.gld_srv_product_offer`. U-02 one row per `product_id`; variant element `{variant_id, name, status, attributes}` in `variants_json`.
- U-03 hotel in the same table. Holiday grain `products.id`. Hotel grain `hotel_room_types.id`, `product_type = hotel`.
- U-04 drop the whole product when the relation has more than one `business_service_id`.
- U-05 `poi_id = uuid_md5(business_service_id, 'partner')`, then `slv_enr_poi_destination`.
- U-06 verbatim: "Không transform, giải mã được cho fail job để tìm cách giải mã khác khắc phục."
- U-07 `valid_from` and `valid_to` inside the rate-plan element. No sale flag derived from them.
- U-08 Q-19 tables stay sources. Gold reads L1 and those three.
- D-0: P-1 `cross_collisions` 0, `dup_products` 0, `dup_rooms` 0. Key stays `product_id`.
- D-1: agreed (c). The `slv_pn_product_sale` decoder fails the job on a decode error instead of writing NULL. Gold does not decode and does not change the price. The L2 notebook change is outside this task.
- D-2: holiday `product_type` is `'other'`.
- D-3 and D-10: relation first. U-04 and the "no relation row" test count only `deleted = false` rows. The post id is used only when no live relation row exists.
- D-4 wins over the old "drop when no id" clause. A product with no `business_service_id` is kept, with `poi_id` NULL. A `poi_id` with no destination row is kept and `destination_id` is NULL.
- D-5: copy the `destination_id` JSON array string, same contract as `gld_srv_poi_info.destination_id`.
- D-6: holiday `name` from locale `vi`; `attributes` stay raw JSON; exclude `deleted = true` variants; a product with no variants still gets a row and `variants_json = []`.
- D-7: hotel keys `meal_plan` (number), `kind`, `valid_from`, `valid_to` (ISO-8601 UTC), `include_tax`, `include_service_charge`. A room with no rate plan gets `[]`.
- D-8: `is_active` is only the technical flag. `is_bookable` is copied from L2 with no added gate.
- D-9: keep every listed column. Do not drop `lang`, `price_level`, the six axis columns, or `source_id`.

## Evidence

`evidence/results/product_offer_blocking.txt`: P-2 is `relation_1` 41. P-3 holiday matched 3 unmatched 5; hotel matched 32 unmatched 87; array sizes are 2 or 3 for holiday and 0, 1, 2, 3, or 9 for hotel. P-4 all zeros. P-5: 3 rooms with no live rate plan, max 14 rate plans per `business_service_id`.

## Read

`decision.md` `## Quyết định hiện hành`. `docs/context/mapping_legacy_ai_product.md` §1.1, §1.2, §1.6, §1.8, §1.9, §1.11. `docs/context/mapping_slv_pn_product.md` §9, §10. `docs/context/mapping_slv_pn_product_l2.md` §1, §2, §3. `docs/context/02_NAMING_CONVENTION.md` §1 and §5.2. `docs/context/mapping_gld_srv_poi_info.md` §1.1 for `destination_id` only.
