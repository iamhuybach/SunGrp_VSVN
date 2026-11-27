# Model design: `lh_vv_gold.dbo.gld_srv_product_offer`

## Scope

- Task: `20261127-pn-product-one-table-mapping`. Target file in scope: `docs/context/mapping_gld_srv_product_offer.md` (`task-state.yaml` `scope.files`). This design covers the mapping document only. It does not design a notebook edit, DDL, or a `ctrl_cfg_schema_registry` row.
- No `proposal.md` exists for this run. No `## Dòng thay đổi` or `## ctrl_cfg_schema_registry` section can be cited. Gold and Silver L2 tables have no registry rows (`mapping_slv_pn_product_l2.md` `## Câu hỏi cần chốt` item 2).
- Ledger rows implemented (`decision.md` `## Quyết định hiện hành`): U-01, U-02, U-03, U-04, U-05, U-06, U-07, U-08, D-0, D-1, D-2, D-3, D-4, D-5, D-6, D-7, D-8, D-9, D-10.
- Evidence used: `evidence/results/product_offer_blocking.txt` P-1 to P-5.
- Legacy behaviour comes from `mapping_legacy_ai_product.md` §1.1, §1.2, §1.6, §1.8, §1.9 and §1.11. Where the ledger differs, the ledger wins. This affects the drop rules in §1.1 steps 6–7 and §1.11 step 5, deleted variants kept in `variants_json` in §1.1, the destination remap and fallback in §1.11 steps 3–4, the `ai_poi` / `ai_enriched_poi` reads, price `NULL → 0`, and the translation cache in §1.7.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_product_offer` | Gold serving | One row per `product_id` (U-02, D-0). Holiday rows: one per `slv_pn_product_sale.product_id`, which is `slv_pn_products.id` (U-03, `mapping_slv_pn_product_l2.md` §1.1). Hotel rows: one per `slv_pn_hotel_room_offer.room_type_id`, which is `slv_pn_hotel_room_types.id`, with `product_type = 'hotel'` (U-03). Holiday variants are elements of `variants_json` (U-02, D-6). Hotel rate plans are elements of `variants_json` (U-07, D-7) | `NB_GLD_SRV_PRODUCT_OFFER` `[PROPOSED]` (`02_NAMING_CONVENTION.md` §2, `NB_<UPPER(trg_tbl)>`). Name only; no notebook edit in this task |

Rows are not created for:
- a holiday product that has more than one distinct `business_service_id` across relation rows with `deleted = false`. The whole product is dropped (U-04, D-3, D-10).
- an L2 driver row with `deleted_at IS NOT NULL`. Readers of L2 take only `deleted_at IS NULL` rows (`mapping_slv_pn_product_l2.md` preamble).

Rows are kept for:
- a holiday product with no variants, with `variants_json = []` (D-6).
- a product with no `business_service_id`, with `poi_id` NULL (D-4).
- a `poi_id` with no destination row, with `destination_id` NULL (D-4).
- a hotel room with no live rate plan, with `variants_json = []` (D-7). P-5 found 3 such rooms.

## Keys

| table | key kind | columns | rule / source |
|---|---|---|---|
| `gld_srv_product_offer` | Primary (MERGE key) | `product_id` | D-0. P-1 found `cross_collisions` 0, `dup_products` 0 and `dup_rooms` 0, so holiday and hotel ids share one key space without a type prefix |
| `gld_srv_product_offer` | Business | `business_service_id` (partner, raw) | Holiday: relation first, then post (D-3, D-10). Hotel: `slv_pn_hotel_room_types.business_service_id` (`mapping_legacy_ai_product.md` §1.6, `source_id, destination_id` row). Not unique; one business service has many products, and up to 14 rate plans per business service (P-5) |
| `gld_srv_product_offer` | Derived join key | `poi_id` | `poi_id = uuid_md5(business_service_id, 'partner')`. Formula source: U-05, `AGENTS.md` §7 (cited in `mapping_legacy_ai_product.md` §1.1 last bullet), `mapping_slv_pn_product.md` Q-13 and §9.1. NULL when `business_service_id` is NULL (D-4) |
| `gld_srv_product_offer` | Foreign (optional) | `poi_id` → `lh_vv_silver.dbo.slv_enr_poi_destination.poi_id` | U-05. LEFT JOIN. `slv_enr_poi_destination` has one row per `poi_id` (`mapping_gld_srv_poi_info.md` §1.6). Unmatched rows are kept (D-4). P-3: holiday matched 3, unmatched 5; hotel matched 32, unmatched 87 |
| `gld_srv_product_offer` | Foreign (optional) | `product_post_id` → `lh_vv_silver.dbo.slv_pn_product_posts.id` | Copied from `slv_pn_product_sale.product_post_id` (`mapping_slv_pn_product_l2.md` §1.2). NULL for hotel rows |
| `gld_srv_product_offer` | Element key inside `variants_json` | `variant_id` | Holiday: `slv_pn_product_variants.id` (`mapping_legacy_ai_product.md` §1.8). Hotel: `slv_pn_hotel_rate_offer.rate_plan_id`, which is `slv_pn_hotel_rate_plans.id` (`mapping_slv_pn_product_l2.md` §3.2) |

## Columns

Types come from the `Data Type` column of `mapping_legacy_ai_product.md` §1.2, or from the source column on L1/L2 where the value is copied. Technical columns follow `02_NAMING_CONVENTION.md` §5.2 (Silver L2 + gold).

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| gld_srv_product_offer | product_id | string | no | holiday `slv_pn_product_sale.product_id`; hotel `slv_pn_hotel_room_offer.room_type_id` | U-02, U-03, D-0. Copied 1-1 |
| gld_srv_product_offer | name | string | yes | holiday `slv_pn_product_translations.name`; hotel `slv_pn_hotel_room_types.name` | Legacy §1.2 and §1.6: `coalesce(en name, vi name, product_id)`. The English name comes from the existing `locale = en` row. No translation cache and no generated name (`mapping_slv_pn_product.md` preamble, "Không sinh tên"). Hotel rooms have one `name`, so the rule is `coalesce(name, product_id)` |
| gld_srv_product_offer | lang | string | yes | constant | Legacy §1.2: constant `'en'`. Kept by D-9 |
| gld_srv_product_offer | product_type | string | no | constant | D-2: holiday `'other'`. U-03: hotel `'hotel'` |
| gld_srv_product_offer | is_active | boolean | yes | technical | D-8: technical flag only. `true` on every row the build writes. `false` when the row is soft-deleted (`deleted_at` not NULL), per `02_NAMING_CONVENTION.md` §5.2. Product or room `status` is not used (replaces legacy §1.2 and §1.6) |
| gld_srv_product_offer | is_bookable | boolean | yes | holiday `slv_pn_product_sale.is_bookable`; hotel `slv_pn_hotel_room_offer.is_bookable` | D-8: copied 1-1 from L2, with no extra gate (replaces legacy §1.6) |
| gld_srv_product_offer | product_line | string | yes | holiday `slv_pn_products.product_line`; hotel constant | Legacy §1.2: holiday 1-1; hotel `'accommodation'` (§1.6). Kept by D-9 |
| gld_srv_product_offer | price_level | int | yes | holiday `slv_pn_product_sale.marketing_price`, `original_price`; hotel constant | Legacy §1.2 bands on `coalesce(marketing_price, original_price)`: ≤ 500000 → 1, ≤ 2000000 → 2, ≤ 5000000 → 3, else 4, NULL → 0. Hotel `0` (§1.6). Kept by D-9. Bands are read from the L2 price; gold does not decode (D-1) |
| gld_srv_product_offer | original_price | double | yes | holiday `slv_pn_product_sale.original_price`; hotel none | U-06, D-1: copied 1-1 from L2, no transform, NULL stays NULL. No `NULL → 0` (`mapping_slv_pn_product_l2.md` preamble). Hotel: NULL |
| gld_srv_product_offer | marketing_price | double | yes | holiday `slv_pn_product_sale.marketing_price`; hotel none | U-06, D-1: as `original_price` |
| gld_srv_product_offer | markup_percent | double | yes | holiday `slv_pn_product_sale.markup_percent`; hotel none | U-06, D-1: as `original_price` |
| gld_srv_product_offer | variant_count | long | yes | holiday `slv_pn_product_variants`; hotel `slv_pn_hotel_rate_plans` + `slv_pn_hotel_rate_offer` | Legacy §1.2: count of holiday variants with `deleted = false` per `product_id` (D-6), NULL when none. Legacy §1.6: count of live hotel rate plans with the same `business_service_id` as the room, NULL → 0 |
| gld_srv_product_offer | active_variant_count | long | yes | holiday `slv_pn_product_variants.status`; hotel `slv_pn_hotel_rate_offer.status` | Legacy §1.2: variants with `deleted = false` and `status = 'active'`. Legacy §1.6: live rate plans with `status = 'Active'` |
| gld_srv_product_offer | variants_json | string | no | holiday `slv_pn_product_variants`, `slv_pn_product_variant_translations`; hotel `slv_pn_hotel_rate_offer`, `slv_pn_hotel_rate_plans` | U-02: JSON array of `{variant_id, name, status, attributes}`. Holiday (D-6, legacy §1.8): `variant_id` = `id`, `name` from the translation with `locale = 'vi'` (NULL when missing), `status` = `status`, `attributes` = raw `slv_pn_product_variants.attributes` JSON, with no label resolution. Variants with `deleted = true` are excluded. No variant gives `[]`. Hotel (U-07, D-7, legacy §1.6): one element per live rate plan with the room's `business_service_id`. `variant_id` = `rate_plan_id`, `name` = rate-plan `name` with fallback to the id, `status` from L2. `attributes` keys: `meal_plan` as a number from L2 (no label, `mapping_slv_pn_product_l2.md` §3.3), `kind`, `valid_from` and `valid_to` as ISO-8601 UTC strings from L2 timestamps (no sale flag, U-07), `include_tax`, `include_service_charge`. No rate plan gives `[]` |
| gld_srv_product_offer | variant_tickets | string | yes | `slv_pn_product_variants.attributes` resolved via `slv_pn_product_attribute*` and `slv_pn_product_attribute_value*_translations` | Legacy §1.8 resolve table and §1.9: `to_json(collect_set(value_name_vi))` over variants with `deleted = false`. NULL when empty. Hotel NULL (§1.6). Kept by D-9 |
| gld_srv_product_offer | variant_dates | string | yes | same as `variant_tickets` | Legacy §1.9, code `holiday:use_date`. Hotel NULL. D-9 |
| gld_srv_product_offer | variant_hotels | string | yes | same as `variant_tickets` | Legacy §1.9, code `holiday:hotel`. Hotel NULL. D-9 |
| gld_srv_product_offer | variant_age_groups | string | yes | same as `variant_tickets` | Legacy §1.9, codes `holiday:quantity` and `holiday:age_group`. Hotel NULL. D-9 |
| gld_srv_product_offer | variant_room_types | string | yes | same as `variant_tickets` | Legacy §1.9, code `holiday:zone`. Hotel NULL (§1.2). D-9 |
| gld_srv_product_offer | variant_departures | string | yes | same as `variant_tickets` | Legacy §1.9, code `holiday:depature`. Hotel NULL. D-9 |
| gld_srv_product_offer | variant_statuses | string | yes | `slv_pn_product_variants.status` | Legacy §1.9: `to_json(collect_set(status))` over variants with `deleted = false`. Hotel NULL. D-9 |
| gld_srv_product_offer | product_attributes | string | yes | holiday `slv_pn_product_posts.raw_sync_data` via `product_post_id`; hotel `slv_pn_hotel_room_offer` and `slv_pn_hotel_room_types` | Legacy §1.2: holiday JSON `{shortDescription, tags, priceLevel, isActive}`, with `priceLevel` = gold `price_level` and `isActive` = gold `is_active`. Hotel: JSON room object with the keys listed in legacy §1.6, value from L2 where the column exists there, otherwise from L1. Hotel `priceLevel` is NULL (§1.6). D-9 |
| gld_srv_product_offer | business_service_id | string | yes | holiday `slv_pn_product_business_service_relation.business_service_id`, else `slv_pn_product_posts.business_service_id`; hotel `slv_pn_hotel_room_types.business_service_id` | D-3, D-10: holiday takes the single distinct id across relation rows with `deleted = false`. More than one distinct id drops the product (U-04). With no live relation row, it takes the post's id via `slv_pn_product_sale.product_post_id`. Otherwise NULL and the row is kept (D-4). P-2: every product falls in `relation_1` (41). Hotel: 1-1. D-9 |
| gld_srv_product_offer | source_id | string | yes | `business_service_id` | Legacy §1.11 step 1: `source_id` = `business_service_id` cast to string, not hashed. No `TEST_MODE` constant. D-9 |
| gld_srv_product_offer | product_post_id | string | yes | `slv_pn_product_sale.product_post_id` | Copied 1-1 (`mapping_slv_pn_product_l2.md` §1.2). Hotel NULL. D-9 |
| gld_srv_product_offer | poi_id | string | yes | `business_service_id` | U-05: `uuid_md5(business_service_id, 'partner')`. NULL when `business_service_id` is NULL (D-4) |
| gld_srv_product_offer | destination_id | string | yes | `slv_enr_poi_destination.destination_id` | U-05, D-5: LEFT JOIN on `poi_id`, copying the JSON array string 1-1 under the same contract as `gld_srv_poi_info.destination_id` (`mapping_gld_srv_poi_info.md` §1.1, `destinations[].strapi_document_id`). No remap and no fallback (D-4 replaces legacy §1.11 steps 3–5). No match gives NULL. P-3: arrays have 2 or 3 elements for holiday and 0, 1, 2, 3 or 9 for hotel |
| gld_srv_product_offer | row_hash | string | no | business columns above | `02_NAMING_CONVENTION.md` §5.2: `sha2(to_json(struct(business columns)), 256)` |
| gld_srv_product_offer | created_at | timestamp | no | technical | `02_NAMING_CONVENTION.md` §5.2 |
| gld_srv_product_offer | updated_at | timestamp | no | technical | `02_NAMING_CONVENTION.md` §5.2: changes only when `row_hash` changes. Replaces legacy business `updated_at` (§1.2), because a business column may not share a technical column's name (§5.2, `ConfigError`) |
| gld_srv_product_offer | deleted_at | timestamp | yes | technical | `02_NAMING_CONVENTION.md` §5.2: not NULL means soft-deleted, with `is_active = false` |

## Lineage

| table | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `gld_srv_product_offer` | None directly. The L1 tables are extracted from `lh_vv_bronze.dbo.partner_raw_data` by `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` (`mapping_slv_pn_product.md` preamble) | L2 (U-08), only `deleted_at IS NULL`: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer`. L1 (U-08): `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_translations`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_business_service_relation`, `slv_pn_product_posts`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`. Destination: `slv_enr_poi_destination` (U-05) | None. Gold never reads gold. Legacy reads of `ai_poi`, `ai_enriched_poi` and `ai_product_translation` (§1.1) are not carried over |

## Conflicts and questions

1. Closed (former item 11). An earlier rule dropped a product with no `business_service_id`, which conflicted with D-4. D-4 wins: the row is kept with `poi_id` NULL, `source_id` NULL and `destination_id` NULL. The legacy drop in §1.1 step 6 and §1.11 step 5 is not carried over.
2. Closed (former item 15). It was unclear which relation rows count. D-3 and D-10 settle it: U-04's count of distinct `business_service_id` and the "no relation row" test both use only `slv_pn_product_business_service_relation` rows with `deleted = false`. The post's `business_service_id` is used only when no live relation row exists.
