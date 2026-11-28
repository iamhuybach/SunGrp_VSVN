# Author input — 20261127-gld-pn-product

No proposal. The accepted model is the mapping below. Replace the withdrawn three-table design. Do not invent a rule.

## Read

- `docs/context/mapping_gld_srv_product_offer.md`: `## 1. Table` through §1.9, and `## Câu hỏi cần chốt`.
- `.ai/tasks/20261127-gld-pn-product/decision.md`: `## Quyết định hiện hành`, rows U-01, U-02, U-03, U-04, U-05, U-06, U-07, U-08, D-0 through D-10.
- `docs/context/02_NAMING_CONVENTION.md`: §1 `gld_srv_<topic>_<grain>`; §5.2 gold technical columns.

## Locked

- U-01: one gold table `lh_vv_gold.dbo.gld_srv_product_offer`.
- U-02, D-0: one row per `product_id`. Holiday driver `slv_pn_product_sale.product_id`. Hotel driver `slv_pn_hotel_room_offer.room_type_id`. Duplicate `product_id` after the union fails the job.
- U-03, D-2: both branches in that table. Holiday `product_type = other`. Hotel `product_type = hotel`.
- U-08: Q-19 tables stay sources. Gold also reads the L1 tables named in mapping §1.
- U-04, D-3, D-10: drop a holiday product with more than one distinct `business_service_id` on relation rows `deleted = false`. Relation first; post only when no such row exists.
- U-05, D-4, D-5: `poi_id = uuid_md5(business_service_id, 'partner')`, then left join `slv_enr_poi_destination`. Missing POI or destination keeps the row. `destination_id` is the JSON array string, same contract as `gld_srv_poi_info.destination_id`. Do not read that gold table.
- U-06, D-1: copy the three prices. NULL stays NULL. Gold does not decode or change them. Hotel prices are NULL.
- U-07, D-6, D-7: `variants_json` per §1.3 and §1.5. `valid_from` and `valid_to` live inside the hotel element. No sale flag.
- D-8: `is_bookable` 1-1 from L2. `is_active` is technical only.
- D-9: keep every column named there. Column order and types are mapping §1.2.

## Ask

Copy mapping `## Câu hỏi cần chốt` items 1–4 into `## Conflicts and questions` when a column depends on them. Do not answer them. Item 5 is this task's notebook, not a model question.
