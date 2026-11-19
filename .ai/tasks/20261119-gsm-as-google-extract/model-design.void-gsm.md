VOID 2026-11-19: written for source_name gsm. The user corrected the source to sgm. Do not use this file as model-design.md.

# Model design: 20261119-gsm-as-google-extract

## Scope

- Base task: `20261119-gsm-as-google-extract`. Bronze `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` now also carries rows with `source_name = 'gsm'`. They must be extracted through the existing Google 3P path: the same notebook `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, the same `TABLE_CONFIGS_3P` registry, and the same `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` pipeline.
- `proposal.md` does not exist in the task folder. This design therefore cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. It implements the author input and these ledger rows in `decision.md` `## Quyết định hiện hành`:
  - D-1, gsm identity. `slv_3p_poi` keeps the bronze `source_name`. After `slv_3p_poi`, a `gsm` row uses the effective `source_name = 'google'` and `poi_id = HASH_MD5_UUID('google', source_id)`. There is no second `poi_id` derived from `gsm`.
  - D-2, MERGE key collision. The current formula is `HASH_MD5_UUID` of `_doc.source_name,_doc.source_id`. `review_id` and `media_dedup_key` still read `_doc.source_name`. DEV evidence shows no `gsm` rows yet.
- Constraints carried forward: no new table, column, or dictionary source, and no `source_name = 'gsm'` dictionary. Active grain and keys stay as they are. The `DOC` / `DOC_ARRAY` contract and the 9 active `slv_3p_poi_*` tables stay. The disabled `slv_3p_poi_policy` is not reopened. Unknown payload keys get no `json_path`; this includes `x_lodging`, `x_scraper`, and the other non-registry heads listed in `evidence/payload-shape.md` § Registry keys on this document. The serving API changes only if a gold column set or gold key changes; this design changes neither.
- Out of model scope. These are noted because the model depends on them, but they are not designed here: the `sources` parameter default `google` (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §4) and the pipeline activity value (decision.md `## Lịch sử quyết định`).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` | bronze | one crawl event (`event_id`); `source_name` now includes `gsm`. Read only, no change | Eventstream (no notebook) |
| `lh_vv_silver.dbo.slv_3p_poi` | silver L1 | one row per `poi_id` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_address` | silver L1 | one row per `poi_id` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_contact` | silver L1 | one row per `poi_id` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_price` | silver L1 | one row per `poi_id` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_opening_hours` | silver L1 | one row per `poi_id` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_rating` | silver L1 | one row per `poi_id` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_amenity` | silver L1 | one row per `poi_id` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_review` | silver L1 | one row per `review_id`, from `DOC_ARRAY` over `reviews` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_3p_poi_media` | silver L1 | one row per `media_dedup_key`, from `DOC_ARRAY` over `photos` (unchanged) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `lh_vv_silver.dbo.slv_poi_entity_non_enrich` | silver L2 | unchanged; grain not in this run's read set | `NB_SLV_POI_ENTITY_NON_ENRICH` |
| `lh_vv_silver.dbo.slv_poi_amenity` | silver L2 | unchanged; grain not in this run's read set | `NB_SLV_POI_AMENITY` |
| media-info silver node (table name not in read set, see Q-9) | silver L2 | unchanged | `NB_SLV_POI_MEDIA_INFO` |
| enrich POI info node (table name not in read set, see Q-9) | enrich | unchanged | `NB_ENR_POI_INFO` |
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold | unchanged; grain not in this run's read set | `NB_GLD_SRV_POI_INFO` |
| `lh_vv_gold.dbo.gld_srv_poi_amenity` | gold | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) (unchanged, `mapping_gld_srv_poi_amenity.md` line 33) | `NB_GLD_SRV_POI_AMENITY` |
| `lh_vv_gold.dbo.gld_srv_poi_review` | gold | unchanged; grain not in this run's read set | `NB_GLD_SRV_POI_REVIEW` |
| gold media-info serving table (name not in read set, see Q-9) | gold | unchanged | not in read set |
| `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | gold | unchanged; its mapping has no `google` line | `NB_GLD_SRV_POI_MULTI_LANG` |

## Keys

The `poi_id` formula source is `AGENTS.md` §7, `01_DATA_MODEL.md` §5.2 and §8, `CTRL_TABLES_CONTEXT.md` §5 (3rd-party registry summary), and `NB_CREATE_DDL` cell 14 `POI_ID = {"path": "_doc.source_name,_doc.source_id", "type": "string", "rule": "HASH_MD5_UUID"}`. This design applies D-1 on top of it: for a row whose bronze `source_name` is `gsm`, `poi_id = HASH_MD5_UUID('google', source_id)`. For a `google` row the formula and value do not change. The registry `json_path` grammar (`02_NAMING_CONVENTION.md` §6) has no literal or effective-source token, so the registry cannot express this yet. See Q-1.

| table | primary key | business key | foreign keys |
|---|---|---|---|
| `slv_3p_poi` | `poi_id` | (`source_name`, `source_id`) as stored; identity per D-1 is (effective `source_name`, `source_id`) | none |
| `slv_3p_poi_address`, `_contact`, `_price`, `_opening_hours`, `_rating`, `_amenity` | `poi_id` | same as `slv_3p_poi` | `poi_id` → `slv_3p_poi.poi_id` |
| `slv_3p_poi_review` | `review_id` = `HASH_SHA256` of `_doc.source_name,_doc.source_id,authorAttribution.displayName,publishTime` (cell 14) | same input tuple | `poi_id` → `slv_3p_poi.poi_id` |
| `slv_3p_poi_media` | `media_dedup_key` = `HASH_SHA256_PIPE` of `_doc.source_name,_doc.source_id,name` (cell 14) | same input tuple | `poi_id` → `slv_3p_poi.poi_id` |
| `slv_poi_entity_non_enrich`, `slv_poi_amenity`, media-info silver, enrich POI info | unchanged (not in read set) | unchanged | `poi_id` from `slv_3p_poi*`. A `gsm` row carries the google `poi_id` (D-1) |
| `gld_srv_poi_amenity` | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) | same | `poi_id` google from `slv_3p_poi_amenity.poi_id` (`mapping_gld_srv_poi_amenity.md` line 11) |
| `gld_srv_poi_info`, `gld_srv_poi_review`, gold media-info, `gld_srv_poi_multi_lang` | unchanged (not in read set) | unchanged | `poi_id` |

The review and media keys still hash the bronze `_doc.source_name` (D-2). Q-2 covers what that means when a `gsm` row and a `google` row share a `source_id`.

## Columns

No column is added or removed. Types come from `NB_CREATE_DDL` cell 14. Nullability is not stated in the files read; existing nullability is unchanged.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_3p_poi` | `source_name` | string | unchanged | `_doc.source_name` | Keeps the bronze value, `gsm` or `google`. D-1; author input "Ở slv_3p_poi, cột source_name giữ nguyên giá trị bronze" |
| `slv_3p_poi` | `source_id` | string | unchanged | `_doc.source_id` | Unchanged. Not filled from payload `id` (author input; `evidence/payload-shape.md` header) |
| all 9 active `slv_3p_poi*` | `poi_id` | string | unchanged | `_doc.source_name,_doc.source_id` today | `gsm` row: `HASH_MD5_UUID('google', source_id)`. `google` row: unchanged. D-1. Registry expression is open (Q-1) |
| `slv_3p_poi_review` | `review_id` | string | unchanged | `_doc.source_name,_doc.source_id,authorAttribution.displayName,publishTime` | Unchanged per D-2; open question Q-2 |
| `slv_3p_poi_media` | `media_dedup_key` | string | unchanged | `_doc.source_name,_doc.source_id,name` | Unchanged per D-2; open question Q-2 |
| all active `slv_3p_poi*` registry columns | existing `json_path` | unchanged | unchanged | `TABLE_CONFIGS_3P` | A key that is present with JSON null (`priceLevel`, `currentOpeningHours`, `regularOpeningHours`, `priceRange`, `parkingOptions`, `paymentOptions`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions`) yields NULL; it is not a missing field. Author input; `payload-shape.md` § Registry keys |
| none | `x_lodging.*`, `x_scraper.*`, other non-registry heads | none | none | none | No `json_path`. Author input; `payload-shape.md` § Registry keys |
| downstream silver L2 / enrich / gold | `source_name` (wherever carried) | string | unchanged | `slv_3p_poi.source_name` via the nodes | The effective value for a `gsm` row is `google`; `google` rows are unchanged. Author input "Mọi xử lý cho các bảng sau slv_3p_poi …"; D-1. Where it is applied and how it is cased is open (Q-3, Q-4) |
| `gld_srv_poi_review` | `source_name` | string | unchanged | literal `'google'` | Unchanged (`mapping_gld_srv_poi_review.md` lines 9, 24) |

## Lineage

- Bronze → silver L1: `brz_3rd_crawler_poi_stream` (`normalized_payload`, `source_name`, `source_id`, `language_code`, `event_id`, `crawled_at`) feeds the 9 active `slv_3p_poi*` tables through `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §5, §8). No other bronze read.
- Silver L1 → silver L2:
  - `slv_poi_entity_non_enrich` reads `slv_3p_poi*`.
  - `slv_poi_amenity` reads `slv_3p_poi_amenity` and `slv_poi_entity_non_enrich` (`mapping_gld_srv_poi_amenity.md` lines 11, 12, 28).
  - The media-info silver node reads `slv_3p_poi_media` (`mapping_poi_media_info.md` line 24).
- Silver → gold:
  - `gld_srv_poi_info` reads `slv_poi_entity_non_enrich`, `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, and `slv_3p_poi_review` (`mapping_gld_srv_poi_info.md` lines 13, 67, 77).
  - `gld_srv_poi_amenity` reads `slv_poi_amenity` (line 33).
  - `gld_srv_poi_review` reads a Google-flow silver table (line 9).
  - Gold media-info reads `slv_3p_poi_media` (`mapping_poi_media_info.md` line 24).
- No gold table reads another gold table in the files read. Placing the effective-source rule in silver L2 or earlier matches `AGENTS.md` §7, but the placement is open (Q-3).

## Conflicts and questions

1. Q-1, `poi_id` registry expression. `POI_ID` hashes `_doc.source_name,_doc.source_id`, so a `gsm` row would get `HASH_MD5_UUID('gsm', source_id)`, which breaks D-1. The `json_path` grammar (`02_NAMING_CONVENTION.md` §6) has no literal or effective-source token, and the constraint forbids a new column. Which registry `path`, `rule`, or `arg` should produce `'google'` for a `gsm` row while keeping `slv_3p_poi.source_name` as the bronze value? The files show no such rule.
2. Q-2, `review_id` and `media_dedup_key`. Both hash the bronze `_doc.source_name` (cell 14; D-2). If a `gsm` document and a `google` document share a `source_id`, they share one `poi_id` (D-1), but each review or photo gets two different `review_id` / `media_dedup_key` values. That doubles rows under one `poi_id`, and `review_count = COUNT(*)` per `poi_id` (`mapping_gld_srv_poi_info.md` line 77) counts both. Keeping the bronze `source_name` in these keys without a second key or a duplicate count does not seem possible with the files shown. No resolution is chosen here.
3. Q-3, where to apply the effective `source_name`. The author input requires `gsm` to become `google` in every table after `slv_3p_poi`: dictionary, enrich, gold, and `source_name = 'google'` filters. Which node applies the rule first? Is it `NB_SLV_POI_ENTITY_NON_ENRICH` or each listed notebook? The files do not show which column carries `source_name` into `slv_poi_entity_non_enrich`. If the rule is not applied before gold, `gld_srv_poi_info` keeps a `gsm` row as "not google" and skips the enrichment gate (line 13), and the opening-hours step stops with `SOURCE_NOT_GOOGLE_PARTNER` (line 126).
4. Q-4, matching and casing. `sources` is case-insensitive (§4) and gold compares `lower(trim(source_name))` (line 13). Should the effective rule match `gsm` after `lower(trim(...))`? The files do not say.
5. Q-5, the same `source_id` under both names on `slv_3p_poi`. The grain is one row per `poi_id`. When a `gsm` and a `google` document share a `source_id`, which bronze `source_name` should the stored row hold? D-2 notes that the `crawled_at` UPDATE can change a `google` row's `source_name`. The author input says existing `google` rows keep their `source_name`. These two conflict. DEV has `overlap_source_id = 0` only because `bronze_gsm = 0`.
6. Q-6, payload `id` versus `source_id`. DEV has no `gsm` rows, so `ID_MATCH` and `KEY_ROWS` measured nothing. The model keeps `source_id` from the bronze column and does not use payload `id`. Whether `gsm` bronze `source_id` uses the same id space as `google` is unknown, and D-1 depends on it.
7. Q-7, absent registry keys. The 23 `serves*` / `allows*` / `goodFor*` / service keys are absent from the `gsm` sample, not JSON null. The `slv_3p_poi_amenity` registry line in cell 14 was not fully visible in this read. Should an absent key be treated the same as JSON null for `amenity_schema_json` and for `source_flags_json` matching (`mapping_gld_srv_poi_amenity.md` line 28)? This is one document only, not a distribution.
8. Q-8, address picks. The sample has no `street_number` or `administrative_area_level_2` entries in `addressComponents[].types`, so `house_number` and `ward` would be NULL for that document. This is not a contract change. Is NULL acceptable for `gsm`, given that one document is not a distribution?
9. Q-9, names not in the read set. The target table names of `NB_SLV_POI_MEDIA_INFO` and `NB_ENR_POI_INFO`, the gold media-info table, and the grain and keys of `slv_poi_entity_non_enrich`, `slv_poi_amenity`, `gld_srv_poi_info`, `gld_srv_poi_review`, and `gld_srv_poi_multi_lang` are not in the files read. They are marked unchanged and not restated. `mapping_gld_srv_poi_multi_lang.md` has no `google` line. Does it filter on `source_name` anywhere?
10. Q-10, missing proposal. `proposal.md` does not exist, so this design cannot cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. Should a proposal be authored before the Architect reads this design?
