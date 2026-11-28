# Model design — 20261127-gld-pn-product

## Scope

- Base task: `20261127-gld-pn-product` (Gold partner product from silver L2). The mapping was built in task `20261127-pn-product-one-table-mapping`. This task's ledger takes it over unchanged through row D-A.
- This task has no `proposal.md`, `problem-analysis.md` or `requirements-analysis.md`. As the author input instructs, the accepted model is `docs/context/mapping_gld_srv_product_offer.md` `## 1. Table: gld_srv_product_offer` §1.1–§1.9. `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited (see Conflicts 1).
- Ledger rows implemented, from `.ai/tasks/20261127-gld-pn-product/decision.md` `## Quyết định hiện hành`: D-A, U-01, U-02, U-03, U-04, U-05, U-06, U-07, U-08, D-0, D-1, D-2, D-3, D-4, D-5, D-6, D-7, D-8, D-9, D-10. Context rows: Q-13 (partner `poi_id` formula), Q-14 (destination resolved in gold), Q-15 (NULL price stays NULL), Q-19 (three L2 tables).
- This design replaces the withdrawn three-table design with one gold table (U-01).
- Out of scope, owned by the Architect: write mode (MERGE, `RECOMPUTE`, soft delete, the single commit), version pinning, failing on an empty branch, ordering and run metrics. Mapping §1.1 states these, and this document does not design them. The pipeline edge and the notebook are this task's build work, not model questions (mapping `## Câu hỏi cần chốt` item 5).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_product_offer` | gold (serving, `gld_srv_<topic>_<grain>`, `02_NAMING_CONVENTION.md` §1) | One row per `product_id` (U-02, D-0). Holiday branch: one row per `slv_pn_product_sale.product_id` with `deleted_at IS NULL`, which is `slv_pn_products.id`. Hotel branch: one row per `slv_pn_hotel_room_offer.room_type_id` with `deleted_at IS NULL`, which is `slv_pn_hotel_room_types.id` (U-03, mapping §1.1). Variants and rate plans are elements of `variants_json`, not rows (U-02, U-07). | `NB_GLD_SRV_PRODUCT_OFFER` (proposed in the mapping header, `02_NAMING_CONVENTION.md` §2 `NB_<UPPER(trg_tbl)>`) |

## Keys

**`gld_srv_product_offer`**

- Primary key: `product_id`. The holiday and hotel branches are unioned. A duplicate `product_id` after the union fails the job. There is no row selection and no prefix (D-0, mapping §1.1). Probe P-1 found 0 cross-branch collisions and 0 duplicates in either source (D-0).
- Business key: the same `product_id`. It is `slv_pn_products.id` for holiday rows (`product_type = 'other'`, D-2) and `slv_pn_hotel_room_types.id` for hotel rows (`product_type = 'hotel'`, U-03).
- Derived key `poi_id = uuid_md5(business_service_id, lit('partner'))`, which is `md5(concat(business_service_id, 'partner'))` formatted 8-4-4-4-12. Sources: U-05, Q-13, mapping §1.7, `AGENTS.md` §7 (partner `poi_id`). It is NULL when `business_service_id` is NULL.
- Logical foreign keys. These are lookups with a LEFT JOIN or a driver join. Nothing enforces them as constraints.
  - `poi_id` → `slv_enr_poi_destination.poi_id`, LEFT JOIN. A miss keeps the row and sets `destination_id` to NULL (D-4). A duplicate `poi_id` in `slv_enr_poi_destination` fails the job (mapping §1.7). The table does not join `gld_srv_poi_info` (gold does not read gold; author input U-05).
  - `product_post_id` → `slv_pn_product_posts.id` (holiday; mapping §1.6, §1.7).
  - Holiday `product_id` → `slv_pn_products.id`, `slv_pn_product_translations.(product_id, locale)`, `slv_pn_product_variants.product_id`, `slv_pn_product_business_service_relation.product_id` (mapping §1.1–§1.4, §1.7).
  - Hotel `product_id` (`room_type_id`) → `slv_pn_hotel_room_types.id`. Hotel `business_service_id` → `slv_pn_hotel_rate_offer` / `slv_pn_hotel_rate_plans`, joined on `slv_pn_hotel_rate_plans.id = rate_plan_id` (mapping §1.5).
- Lookup keys that must be unique, or the job fails. They are listed in mapping §1.1 and not repeated here.

## Columns

Column order and types follow mapping §1.2 (D-9). Technical columns follow `02_NAMING_CONVENTION.md` §5.2. "Nullable" is derived only from the stated rule. "not stated" means the files do not say (see Conflicts 4).

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| gld_srv_product_offer | product_id | string | not stated (primary key) | holiday `slv_pn_product_sale.product_id`; hotel `slv_pn_hotel_room_offer.room_type_id` | 1-1. A duplicate after the union fails the job. Mapping §1.2 row `product_id`; U-02, D-0 |
| gld_srv_product_offer | name | string | no (falls back to `product_id`) | holiday `slv_pn_product_translations.name` (`en`, then `vi`); hotel `slv_pn_hotel_room_types.name` | Holiday `coalesce(name en, name vi, product_id)`, hotel `coalesce(name, product_id)`. No translation or generated name. Mapping §1.2 row `name`; D-9 |
| gld_srv_product_offer | lang | string | no | constant | `'en'`. Mapping §1.2 row `lang`; D-9 |
| gld_srv_product_offer | product_type | string | no | constant | Holiday `'other'`, hotel `'hotel'`. Mapping §1.2; D-2, U-03 |
| gld_srv_product_offer | is_active | boolean | no | technical | `true` on every row the build writes, `false` when `deleted_at` is not NULL. Does not read `status`. Excluded from `row_hash`. Mapping §1.2, §1.9; D-8 |
| gld_srv_product_offer | is_bookable | boolean | not stated (copied from L2) | holiday `slv_pn_product_sale.is_bookable`; hotel `slv_pn_hotel_room_offer.is_bookable` | 1-1, no added gate. Mapping §1.2; D-8 |
| gld_srv_product_offer | product_line | string | not stated (holiday copied 1-1 from L1) | holiday `slv_pn_products.product_line`; hotel constant | Holiday 1-1, hotel `'accommodation'`. Mapping §1.2; D-9 |
| gld_srv_product_offer | price_level | int | no | holiday `slv_pn_product_sale.marketing_price`, `original_price` | Tier from `coalesce(marketing_price, original_price)` with the thresholds in mapping §1.2. NULL becomes 0. Hotel `0`. No decoding. Mapping §1.2, §1.8; D-9 |
| gld_srv_product_offer | original_price | double | yes | holiday `slv_pn_product_sale.original_price` | 1-1, NULL stays NULL, hotel NULL. Mapping §1.2, §1.8; U-06, D-1, Q-15 |
| gld_srv_product_offer | marketing_price | double | yes | holiday `slv_pn_product_sale.marketing_price` | 1-1, NULL stays NULL, hotel NULL. Mapping §1.2, §1.8; U-06, D-1, Q-15 |
| gld_srv_product_offer | markup_percent | double | yes | holiday `slv_pn_product_sale.markup_percent` | 1-1, NULL stays NULL, hotel NULL. Mapping §1.2, §1.8; U-06, D-1 |
| gld_srv_product_offer | variant_count | long | yes (holiday) | holiday `slv_pn_product_variants`; hotel `slv_pn_hotel_rate_offer`, `slv_pn_hotel_rate_plans` | Holiday: count of variants with `deleted = false`, NULL when there are none. Hotel: count of live rate plans for the room's `business_service_id`, 0 when there are none. Mapping §1.2; D-9 |
| gld_srv_product_offer | active_variant_count | long | yes (holiday) | holiday `slv_pn_product_variants.status`; hotel `slv_pn_hotel_rate_offer.status` | Holiday: `deleted = false` and `status = 'active'`, NULL when there are no variants. Hotel: `status = 'Active'`, 0 when there are none. Exact string match. Mapping §1.2; D-9 |
| gld_srv_product_offer | variants_json | string | no (`[]` when empty) | holiday mapping §1.3; hotel mapping §1.5 | JSON array of `{variant_id, name, status, attributes}`, sorted by `variant_id`. Holiday excludes deleted variants and keeps `attributes` raw. Hotel `attributes` holds `meal_plan`, `kind`, `valid_from`, `valid_to`, `include_tax`, `include_service_charge`. No sale flag. Mapping §1.2, §1.3, §1.5; U-02, U-07, D-6, D-7 |
| gld_srv_product_offer | variant_tickets | string | yes | `slv_pn_product_variants.attributes` + attribute labels | Axis `holiday:swticket`, `to_json(array_sort(collect_set(value_name_vi)))`. Empty gives NULL. Hotel NULL. Mapping §1.2, §1.4; D-9 |
| gld_srv_product_offer | variant_dates | string | yes | same | Axis `holiday:use_date`. Mapping §1.2, §1.4; D-9 |
| gld_srv_product_offer | variant_hotels | string | yes | same | Axis `holiday:hotel`. Mapping §1.2, §1.4; D-9 |
| gld_srv_product_offer | variant_age_groups | string | yes | same | Axes `holiday:quantity`, `holiday:age_group`. Mapping §1.2, §1.4; D-9 |
| gld_srv_product_offer | variant_room_types | string | yes | same | Axis `holiday:zone`. Mapping §1.2, §1.4; D-9 |
| gld_srv_product_offer | variant_departures | string | yes | same | Axis `holiday:depature`, spelled exactly as in the source. Mapping §1.2, §1.4; D-9 |
| gld_srv_product_offer | variant_statuses | string | yes | `slv_pn_product_variants.status` | `to_json(array_sort(collect_set(status)))` over variants with `deleted = false`. Empty gives NULL. Hotel NULL. Mapping §1.2; D-9 |
| gld_srv_product_offer | product_attributes | string | no (the object always has its fixed keys) | holiday `slv_pn_product_posts.raw_sync_data`; hotel `slv_pn_hotel_room_offer`, `slv_pn_hotel_room_types` | JSON object with fixed key order per mapping §1.6 (holiday 4 keys, hotel 13 keys). Mapping §1.2, §1.6; D-9 |
| gld_srv_product_offer | business_service_id | string | yes | holiday `slv_pn_product_business_service_relation.business_service_id`, then `slv_pn_product_posts.business_service_id`; hotel `slv_pn_hotel_room_types.business_service_id` | Steps 1–6 in mapping §1.7. A holiday product with more than one distinct non-NULL id among relation rows with `deleted = false` is dropped. The post fallback applies only when no such relation row exists. Not hashed. Mapping §1.2, §1.7; U-04, D-3, D-10 |
| gld_srv_product_offer | source_id | string | yes | `business_service_id` | Cast to string, not hashed, NULL stays NULL. Mapping §1.2; D-9 |
| gld_srv_product_offer | product_post_id | string | yes | holiday `slv_pn_product_sale.product_post_id` | Holiday 1-1, hotel NULL. Mapping §1.2; D-9 |
| gld_srv_product_offer | poi_id | string | yes | `business_service_id` | `uuid_md5(business_service_id, lit('partner'))`, NULL when the input is NULL. Mapping §1.2, §1.7; U-05, Q-13 |
| gld_srv_product_offer | destination_id | string | yes | `slv_enr_poi_destination.destination_id` | LEFT JOIN on `poi_id`. The JSON array string is copied 1-1, with the same contract as `gld_srv_poi_info.destination_id`. A miss gives NULL. Mapping §1.2, §1.7; U-05, D-4, D-5, Q-14 |
| gld_srv_product_offer | row_hash | string | not stated | business columns `product_id` … `destination_id` in §1.2 order, without `is_active` | `sha2(to_json(struct(...)), 256)`. Mapping §1.9; `02_NAMING_CONVENTION.md` §5.2 |
| gld_srv_product_offer | created_at | timestamp | not stated | technical | Gold technical column. Mapping §1.2; §5.2 |
| gld_srv_product_offer | updated_at | timestamp | not stated | technical | Changes only when `row_hash` changes, or when `deleted_at` switches between NULL and not NULL. Mapping §1.2; §5.2 |
| gld_srv_product_offer | deleted_at | timestamp | yes | technical | Not NULL means a soft delete, together with `is_active = false`. Mapping §1.2; §5.2 |

## Lineage

**`lh_vv_gold.dbo.gld_srv_product_offer`**

- Bronze reads: none (mapping header: "Không đọc bronze").
- Silver reads (mapping §1.1–§1.7; U-08):
  - Silver L2 (Q-19): `slv_pn_product_sale` (holiday driver), `slv_pn_hotel_room_offer` (hotel driver), `slv_pn_hotel_rate_offer`. Rows are read only when `deleted_at IS NULL`.
  - Silver L1, holiday: `slv_pn_products`, `slv_pn_product_translations`, `slv_pn_product_variants`, `slv_pn_product_variant_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`, `slv_pn_product_posts`, `slv_pn_product_business_service_relation`.
  - Silver L1, hotel: `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`.
  - Silver enrich: `slv_enr_poi_destination`, read the same way as `gld_srv_poi_info` reads it (`live_only=False`, mapping §1.7).
- Gold reads: none. The table does not read `gld_srv_poi_info` or any other gold table (`AGENTS.md` §7; mapping header; U-05 in the author input).

## Conflicts and questions

1. Missing proposal artifacts. The handoff asks for citations of `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`. The task has no `proposal.md`, `problem-analysis.md` or `requirements-analysis.md`. Following the author input, this design uses mapping §1 as the accepted model. Whoever owns those sections needs to say whether a proposal will be written or the mapping stands in for it.
2. Pipeline edges and lineage do not match. Mapping `## Câu hỏi cần chốt` item 5 describes the edge into `gld_srv_product_offer` as three L2 tables plus `slv_enr_poi_destination`. U-08 and mapping §1.1–§1.7 also read the L1 tables listed under Lineage. This design follows U-08. The Architect has to decide whether the L1 reads get their own edges. This design does not decide it.
3. Column names and `02_NAMING_CONVENTION.md` §5.1. `*_json` is the suffix for JSON strings. Several columns hold JSON strings without that suffix: `variant_tickets`, `variant_dates`, `variant_hotels`, `variant_age_groups`, `variant_room_types`, `variant_departures`, `variant_statuses`, `product_attributes`, `destination_id`. D-9 keeps these names and §1.2 fixes the order, so this design keeps them. It is recorded only as a deviation from the convention. A related point: U-01 locks the table name `gld_srv_product_offer`, while the grain is one row per product (§1 `gld_srv_<topic>_<grain>`). This design keeps the name.
4. Nullability is not stated for `product_id`, `is_bookable`, `product_line`, `row_hash`, `created_at` and `updated_at`. Mapping §1.2 gives no NOT NULL constraint, and the L1/L2 nullability of the copied columns is not shown. The DDL owner has to decide whether `product_id` and the technical columns are declared NOT NULL.
5. (Mapping question 1, inherited from question 2 of `mapping_slv_pn_product.md`.) It is not confirmed that the values in `slv_pn_product_variants.attributes` are value codes. If they are not, all six axis columns are NULL. This affects `variant_tickets`, `variant_dates`, `variant_hotels`, `variant_age_groups`, `variant_room_types` and `variant_departures`.
6. (Mapping question 2, inherited from question 4 of `mapping_slv_pn_product_l2.md`.) The epoch unit of `valid_from` and `valid_to` is not settled. Gold still formats them from the L2 timestamp. This affects `variants_json` (hotel `attributes.valid_from`, `attributes.valid_to`) and therefore `row_hash`.
7. (Mapping question 3.) Room `tags` and `amenities` are stored as strings in L1, and no probe has checked their element format. For now they are copied 1-1 as strings, without splitting labels. This affects `product_attributes` (hotel keys `tags`, `amenities`).
8. (Mapping question 4.) D-1 needs a separate task to change the `slv_pn_product_sale` decoder so that a decoding error fails the job. No such task exists yet. Until it does, L2 writes NULL on a decoding error and gold copies that NULL. This affects `original_price`, `marketing_price`, `markup_percent` and `price_level`. The ledger text of U-06 ("fail the job") is met only after that L2 change. D-1 places the change outside this task.
