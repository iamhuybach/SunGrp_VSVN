# Model design — 20261021-refresh-gld-enr-poi-info

## Scope

- Base task: `20261021-refresh-gld-enr-poi-info`. The task has no `proposal.md`, so `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. The `Quyết định hiện hành` ledger in `decision.md` is the accepted scope.
- This design implements ledger rows D-01, D-04 through D-17, and the history entries dated 2026-10-21 that explain them.
- D-02 (coordinate) only switches off pipeline edges, so it changes no data model. D-03 keeps the `gld_enr_poi_review` logic and column contract. Neither table appears in the column design.
- The ledger now decides several items that earlier designs left open: `service_flag` (D-12), `types` (D-13), `destination_context` (D-14), the `cost_vnd` text (D-15), the `time_to_spend` text (D-16), and the non-google columns plus partner opening hours (D-17).
- The physical DDL change is the Architect's job: dropping the D-05 columns and `destination_context`, renaming `userRatingCount` and `priceLevel`, and adding the new columns. This design gives only the target contract.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.enr.gld_enr_poi_info` (written) | gold | one row per `poi_id` (D-12: the amenity and price joins must not multiply rows) | `NB_ENR_POI_INFO` |
| `lh_vv_silver.dbo.slv_poi_entity_non_enrich` (read, spine) | silver L2 (N6) | `poi_id` | `NB_SLV_POI_ENTITY_NON_ENRICH` |
| `lh_vv_silver.dbo.slv_poi_amenity` (read) | silver L2 (N7) | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`); aggregated to `poi_id` before the join | `NB_SLV_POI_AMENITY` |
| `lh_vv_silver.dbo.slv_3p_poi_price` (read) | silver L1 | `poi_id` (01_DATA_MODEL §5.2) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_rating` (read) | silver L1 | `poi_id` (01_DATA_MODEL §5.2) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_opening_hours` (read) | silver L1 | `poi_id` (01_DATA_MODEL §5.2) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_review` (read) | silver L1 | `review_id`; packed to one `review_json` per `poi_id` by `_review_json` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_pn_business_service_i18ns` (read) | silver L1 | (`business_service_id`, `locale`) (01_DATA_MODEL §5.1; `TABLE_CONFIGS` key) | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` |

## Keys

### `gld_enr_poi_info`

- Primary key: `poi_id` (`NB_ENR_POI_INFO` `SPEC.pk = ("poi_id",)`; `init_tables` `poi_id STRING NOT NULL`). The value is copied from `slv_poi_entity_non_enrich.poi_id`. Gold does not compute it again (D-01; 2026-10-21 history).
- Where `poi_id` comes from:
  - google rows: `uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`; 01_DATA_MODEL §5.2; AGENTS.md §7).
  - partner rows: `uuid_md5(id, 'partner')`, with `source_id = id` and `language_code = 'vi'` (`NB_SLV_POI_ENTITY_NON_ENRICH` `_partner`; 01_DATA_MODEL §5.2 partner note).
- Business key: (`source_name`, `source_id`), the inputs to the `poi_id` formula. The only uniqueness check the entity node runs is `partner_source_id_unique` on `source_id` where `source_name = 'partner'`.
- Foreign keys (logical, not enforced):
  - `poi_id` → `slv_poi_entity_non_enrich.poi_id`.
  - `poi_id` → `slv_poi_amenity.poi_id`, after aggregation to one row per `poi_id` (D-12).
  - `poi_id` → `slv_3p_poi_price.poi_id` (D-08, D-10).
  - google rows only: `poi_id` → `slv_3p_poi_rating.poi_id`, `slv_3p_poi_opening_hours.poi_id`, and `slv_3p_poi_review.poi_id` (D-07). Google entity rows share `poi_id` with `slv_3p_*`; N6 already left-joins `slv_3p_poi_contact` on `poi_id`.
  - partner rows only: `uuid_md5(i18n.business_service_id, 'partner') = e.poi_id` and `i18n.locale = 'vi'` when `e.source_name = 'partner'` (D-17, 2026-10-21). Same `uuid_md5` as `NB_SLV_POI_ENTITY_NON_ENRICH` `_partner`. The i18n table has no `poi_id`. One `vi` row per `business_service_id`.

### Read sources

- `slv_poi_entity_non_enrich`: primary key `poi_id`.
- `slv_poi_amenity`: primary key (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`).
- `slv_3p_poi_price`, `slv_3p_poi_rating`, `slv_3p_poi_opening_hours`: primary key `poi_id`.
- `slv_3p_poi_review`: primary key `review_id`.
- `slv_pn_business_service_i18ns`: primary key (`business_service_id`, `locale`), both `string` in `TABLE_CONFIGS`.

## Columns

Notation:
- `e` = `slv_poi_entity_non_enrich`
- `am` = `slv_poi_amenity`
- `pr` = `slv_3p_poi_price`
- `r` = `slv_3p_poi_rating`
- `oh` = `slv_3p_poi_opening_hours`
- `rv` = `slv_3p_poi_review`
- `i18n` = `slv_pn_business_service_i18ns`
- "label(k)" = the k-th label in the `mapping_gld_enr_poi_info.md` mục 2 row for `e.business_sector`. 1 = time_to_spend, 2 = best time, 3 = cost_vnd.

Entity types come from `init_tables` for `slv_poi_entity_non_enrich`. Types of existing gold columns come from `init_tables` for `gld_enr_poi_info`.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| gld_enr_poi_info | poi_id | STRING NOT NULL | no | e.poi_id | Copy (D-01, D-04) |
| gld_enr_poi_info | source_name | STRING | yes | e.source_name | Copy the entity business column (D-04) |
| gld_enr_poi_info | source_id | STRING | yes | e.source_id | Copy (D-04) |
| gld_enr_poi_info | language_code | STRING | yes | e.language_code | Copy (D-04) |
| gld_enr_poi_info | poi_name | STRING | yes | e.poi_name | Copy (D-04) |
| gld_enr_poi_info | poi_name_normalized | STRING | yes | e.poi_name_normalized | Copy (D-04) |
| gld_enr_poi_info | types | STRING | yes | e.types_json | Keep the gold name `types`; value is `e.types_json`; no `types_json` column (D-13) |
| gld_enr_poi_info | operating_status | STRING | yes | e.operating_status | Copy (D-04) |
| gld_enr_poi_info | primary_type | STRING | yes | e.primary_type | Copy (D-04) |
| gld_enr_poi_info | website_url | STRING | yes | e.website_url | Copy; no longer read from `slv_3p_poi_contact` (D-01, D-04) |
| gld_enr_poi_info | house_number | STRING | yes | e.house_number | Copy (D-04) |
| gld_enr_poi_info | street | STRING | yes | e.street | Copy (D-04) |
| gld_enr_poi_info | ward | STRING | yes | e.ward | Copy (D-04; 2026-10-21 history keeps both `ward` and `district`) |
| gld_enr_poi_info | district | STRING | yes | e.ward | `district = e.ward` (D-06) |
| gld_enr_poi_info | city | STRING | yes | e.city | Copy (D-04; 2026-10-21 history keeps both `city` and `destination_name`) |
| gld_enr_poi_info | destination_name | STRING | yes | e.city | `destination_name = e.city` (D-06) |
| gld_enr_poi_info | full_address | STRING | yes | e.full_address | Copy (D-04) |
| gld_enr_poi_info | lat | DOUBLE | yes | e.lat | Copy (D-04) |
| gld_enr_poi_info | lng | DOUBLE | yes | e.lng | Copy (D-04) |
| gld_enr_poi_info | business_sector | STRING | yes | e.business_sector | Copy (D-04) |
| gld_enr_poi_info | business_category | STRING | yes | e.business_category | Copy (D-04) |
| gld_enr_poi_info | business_category_vi | STRING | yes | e.business_category_vi | Copy (D-04) |
| gld_enr_poi_info | category_group | STRING | yes | e.category_group | Copy (D-04) |
| gld_enr_poi_info | range_low_min | INT | yes | e.range_low_min | Copy the estimate column (D-04) |
| gld_enr_poi_info | range_high_min | INT | yes | e.range_high_min | Copy the estimate column (D-04) |
| gld_enr_poi_info | avg_range_min | INT | yes | e.avg_range_min | Copy the estimate column (D-04). No `time_to_spend_minutes` column (D-16) |
| gld_enr_poi_info | candidate_best_time_code | STRING | yes | e.candidate_best_time_code | Copy the estimate column (D-04) |
| gld_enr_poi_info | canonical_candidate | STRING | yes | e.canonical_candidate | Copy the estimate column (D-04). It also feeds `best_time`. It does not create `best_time_type` (D-05) |
| gld_enr_poi_info | rating | DECIMAL(4,2) | yes | r.rating_overall | google: existing rule `r.rating_overall` (D-07; `build`). Other sources: null (D-17) |
| gld_enr_poi_info | user_rating_count | BIGINT | yes | r.rating_count | Renamed from `userRatingCount` (D-07). google: `r.rating_count`. Other sources: null (D-17) |
| gld_enr_poi_info | price_level | INT | yes | pr.price_level | Renamed from `priceLevel` (D-07). google: `pr.price_level`. Other sources: null (D-17) |
| gld_enr_poi_info | opening_hours_text | STRING | yes | oh.periods_json; i18n.amentities | google: `oh.periods_json` (D-07; `build`). partner: JSON text of the object at `$.policies.operating_hours` in `i18n.amentities` (`string`), joined as in Keys; missing join row or key gives null (D-17). Other sources: null (D-17) |
| gld_enr_poi_info | review_json | STRING | yes | rv | google: existing `_review_json` (top 20 by `time` desc, `review_id` asc; `review_text` = first 350 chars), coalesced to `[]` (D-07; `build`). Other sources: null (D-17) |
| gld_enr_poi_info | time_to_spend | STRING | no | e.avg_range_min, e.business_sector | JSON object `{label(1): text}`. Text follows the D-16 branches in ledger order. Sectors outside mục 2 use the `other` label (D-16; mapping mục 1, 1.1, 2) |
| gld_enr_poi_info | best_time | STRING | no | e.canonical_candidate, e.business_sector | JSON object `{label(2): text}`. `Tháng {from} - Tháng {to}` in string order when `canonical_candidate` matches `Month {from}-{to}` with both months in 1–12; otherwise `Quanh năm` (D-05, mục 1.2). A sector that is null or outside mục 2 uses the `other` label |
| gld_enr_poi_info | cost | BIGINT | yes | pr.price_min, pr.price_max | `ROUND((price_min + price_max) / 2)` when both are non-null; otherwise null. No LLM, no `cost_method`, no `cost_confidence` (D-08, D-10) |
| gld_enr_poi_info | cost_vnd | STRING | no | cost, e.business_sector | When `cost` is non-null: `{label(3): "Từ {n}đ"}`, where `n = 1000 * round_half_up(cost / 1000)` with a comma thousands separator (D-11, D-15). When `cost` is null: the JSON text `null`, not SQL NULL and not `{label: null}` (D-09, D-10). A sector that is null or outside mục 2 uses the `other` label |
| gld_enr_poi_info | service_flag | STRING | no | am.service_flags | JSON array of distinct non-null `am.service_flags` per `poi_id`, sorted in ascending text order; `[]` when the POI has none (D-12). Only amenity rows with `deleted_at` null are included |
| gld_enr_poi_info | created_at | TIMESTAMP | yes | lib | Lib assigns the batch timestamp; not copied from the entity (D-04; `build` comment) |
| gld_enr_poi_info | updated_at | TIMESTAMP | yes | lib | Lib assigns the batch timestamp; not copied from the entity (D-04; `build` comment) |
| gld_enr_poi_info | subcategory_tags | — | — | — | Drop (D-05) |
| gld_enr_poi_info | short_address | — | — | — | Drop (D-05) |
| gld_enr_poi_info | best_time_type | — | — | — | Drop; do not recreate (D-05) |
| gld_enr_poi_info | best_time_from_month | — | — | — | Drop (D-05) |
| gld_enr_poi_info | best_time_to_month | — | — | — | Drop (D-05) |
| gld_enr_poi_info | destination_context | — | — | — | Drop (D-14) |
| gld_enr_poi_info | userRatingCount | — | — | — | Replaced by `user_rating_count` (D-07) |
| gld_enr_poi_info | priceLevel | — | — | — | Replaced by `price_level` (D-07) |

These entity columns are not carried to gold:
- `row_hash`, `created_at`, `updated_at`, `deleted_at` (D-04).
- `types_json`, whose value goes to `types` (D-13).

The gold spine is entity rows with `deleted_at` null.

## Lineage

`gld_enr_poi_info`:
- Bronze: none read directly.
- Silver:
  - `slv_poi_entity_non_enrich` (spine, D-01)
  - `slv_poi_amenity` (D-12)
  - `slv_3p_poi_price` (D-07, D-08)
  - `slv_3p_poi_rating` (D-07)
  - `slv_3p_poi_opening_hours` (D-07)
  - `slv_3p_poi_review` (D-07)
  - `slv_pn_business_service_i18ns` (D-17)
- No longer read: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`. Their values now arrive through `slv_poi_entity_non_enrich`. `slv_pn_poi` is not a source (D-01).
- Gold: none. Gold does not read gold (AGENTS.md §7).

Upstream of the spine, for reference only (01_DATA_MODEL §6 N6, N7):
- N6 reads `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `ref_dictionary_place_type`, `slv_pn_business_services`, and `slv_pn_business_service_i18ns`.
- N7 reads `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich`, and `ref_dictionary_amenities`.

## Conflicts and questions

Not applicable. Ledger D-04 keeps `canonical_candidate` as a column. Mục 2 `other` supplies all three labels. Mục 1.2 sends every other candidate to `Quanh năm`. `cost_vnd` stores the JSON text `null`. New JSON columns are `STRING`. The spine and amenity aggregation use `deleted_at` null.
