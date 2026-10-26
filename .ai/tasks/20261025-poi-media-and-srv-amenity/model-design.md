# Model design: 20261025-poi-media-and-srv-amenity

## Scope

Base task: `20261025-poi-media-and-srv-amenity` (`task-state.yaml`, status `waiting_architecture`). This document replaces the previous `model-design.md`.

There is no `proposal.md` in this task, so this design does not cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. It implements:

- `docs/context/mapping_poi_media_info.md` §1.1, §1.2 (`slv_poi_media_info`) and §2 (`gld_srv_poi_media_gallery`).
- `docs/context/mapping_gld_srv_poi_amenity.md` §0 (current state of `slv_poi_amenity`, read only, unchanged) and §1 (`gld_srv_poi_amenity`).
- These `decision.md` `Quyết định hiện hành` rows: D-MEDIA-12, D-MEDIA-SHAPE, U1, U2, U3, U4, U6, U7, Q9, Q11, U-TIE.
- Evidence: `evidence/results/media_key_grain.txt` (P1–P5) and `evidence/results/partner_media_shape.txt`.
- Technical columns: `sql_merge_target` in `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`.

Out of scope: the logic, grain, key, and ctrl edges of `slv_poi_amenity` (mapping amenity §1); architecture concerns (ordering, cadence, idempotency, rollout).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_poi_media_info` | silver L2 (`slv_poi_<topic>`) | One row per media item: one 3P `slv_3p_poi_media` row, or one kept partner `media` array element of a POI. Key `media_id` (U2). | `NB_SLV_POI_MEDIA_INFO` |
| `lh_vv_gold.dbo.gld_srv_poi_media_gallery` | gold serving | Same as `slv_poi_media_info`, 1-1 (mapping media §2). | `NB_GLD_SRV_POI_MEDIA_GALLERY` |
| `lh_vv_gold.dbo.gld_srv_poi_amenity` | gold serving | Same as `slv_poi_amenity`: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`), 1-1 (mapping amenity §0, §1). | `NB_GLD_SRV_POI_AMENITY` |

The physical names and the absence of a SQL schema `slv` are closed decisions. The mapping heading `slv.slv_poi_media_info` refers to `lh_vv_silver.dbo.slv_poi_media_info`. Notebook names follow `NB_<UPPER(trg_tbl)>` (`02_NAMING_CONVENTION.md` §2) and the `scope.files` list in `task-state.yaml`.

`pl_name` (U1, closed): `slv_poi_media_info` and `gld_srv_poi_media_gallery` use `PL_VV_TRANS_SLV_TO_GLD_30P`. `gld_srv_poi_amenity` uses `PL_VV_TRANS_SLV_TO_GLD_1H`. `slv_poi_amenity` stays on `PL_VV_TRANS_SLV_TO_ENR_15P` (mapping amenity §0).

"Append" in mapping media §1.1 means a union of the 3P branch and the partner branch inside the build. The target is still written with `sql_merge_target`. It does not mean a Delta append-only write.

## Keys

### `slv_poi_media_info`

- Primary/MERGE key: `media_id` alone (U2; mapping media §1.1). `sql_merge_target` builds `ON t.media_id = s.media_id`.
- Business key per branch:
  - 3P: `media_dedup_key` of `slv_3p_poi_media`, copied 1-1 to `media_id` (mapping media §1.2 row `media_id`). P1 on DEV: 940 rows, 940 distinct keys, 0 null keys.
  - Partner: `media_id = sha2(concat_ws('|', 'partner', poi_id, trim(url)), 256)`. `url` is the `url` of the chosen element (i18n `media`, or services `media` on fallback) (mapping media §1.2 row `media_id`; U3).
- `poi_id`:
  - 3P: copied 1-1 from `slv_3p_poi_media.poi_id`. Formula `uuid_format(md5(concat(source_name, source_id)))`, `HASH_MD5_UUID` (`AGENTS.md` §7).
  - Partner: `uuid_md5(business_service_id, 'partner')` on `slv_pn_business_service_i18ns`, and `uuid_md5(id, 'partner')` on `slv_pn_business_services` (`AGENTS.md` §7; mapping media §1.2 row `poi_id`). The services fallback is joined on this `poi_id`. P4 on DEV: 0 overlap with 3P `poi_id` for both partner tables.
- Foreign keys: Delta has no declared FK. `poi_id` uses the same formulas as the POI entity tables listed in `AGENTS.md` §7. Neither mapping names a referenced table, so this design declares no FK.

### `gld_srv_poi_media_gallery`

- Primary/MERGE key: `media_id` (U2). `media_id` and `poi_id` are copied 1-1 from `slv_poi_media_info` (mapping media §2).

### `gld_srv_poi_amenity`

- Primary/MERGE key: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). This is the `slv_poi_amenity` key, carried 1-1 (mapping amenity §0, §1).
- `poi_id`: taken from `slv_poi_amenity`. Mapping amenity §0 says the hash formula in `NB_SLV_POI_AMENITY` is `MISSING`. Gold does not recompute it.

## Columns

Types follow the `data type` column of mapping media §1.2. `integer` is written as `int`. Nullability is not stated in mapping media; see question 1. Technical columns come from `sql_merge_target`: it inserts `row_hash`, `created_at = current_timestamp()`, `updated_at = current_timestamp()`, `deleted_at = NULL`. A matched row whose `row_hash` changed, or that was soft-deleted, gets `updated_at` and `row_hash` set and `deleted_at` cleared; `created_at` is not set. A target row that is missing from the source gets `deleted_at`, `updated_at`, and `soft_delete_set`.

### `slv_poi_media_info`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| slv_poi_media_info | media_id | string | not stated (Q1) | 3P `media_dedup_key`; partner derived | Mapping media §1.2 row `media_id`; U2; see Keys |
| slv_poi_media_info | poi_id | string | not stated (Q1) | 3P `poi_id`; partner `uuid_md5(business_service_id, 'partner')`, services `uuid_md5(id, 'partner')` | Mapping media §1.2 row `poi_id`; `AGENTS.md` §7 |
| slv_poi_media_info | source_name | string | not stated (Q1) | literal | `google` for the 3P branch, `partner` for the partner branch (Q9; mapping media §1.2 row `source_name`) |
| slv_poi_media_info | photo_api_uri | string | not stated (Q1) | 3P `photo_api_uri`; partner null | Mapping media §1.2 row `photo_api_uri` |
| slv_poi_media_info | display_order | int | not stated (Q1) | 3P `display_order`; partner element `order` | 3P 1-1. Partner: element `order` of i18n `media`, or of services `media` when i18n `media` is empty (mapping media §1.2 row `display_order`; U4). Element `order` is int (D-MEDIA-SHAPE). An element with null `order` is kept; only a null or blank `url` drops an element (U3). |
| slv_poi_media_info | width_px | int | not stated (Q1) | 3P `width_px`; partner null | Mapping media §1.2 row `width_px` |
| slv_poi_media_info | height_px | int | not stated (Q1) | 3P `height_px`; partner null | Mapping media §1.2 row `height_px` |
| slv_poi_media_info | photographer | string | not stated (Q1) | 3P `photographer`; partner null | Mapping media §1.2 row `photographer` |
| slv_poi_media_info | blob_url | string | not stated (Q1) | 3P `blob_url`; partner element `url` | 3P 1-1. Partner: raw `url` string of the chosen element, not trimmed (Q11; mapping media §1.2 row `blob_url`) |
| slv_poi_media_info | thumbnail_url | string | not stated (Q1) | none | Always null (mapping media §1.2 row `thumbnail_url`) |
| slv_poi_media_info | is_cover | boolean | not stated (Q1) | derived | One cover per `poi_id` (D-MEDIA-12). If the POI has one row, that row is the cover even when `display_order` is null. If it has more than one row, the cover is the row with the smallest non-null `display_order`. On a tie, the row encountered first wins. No sort column is added (U-TIE). All other rows are false. P1: 5 DEV POIs tie at the minimum. |
| slv_poi_media_info | is_active | boolean | not stated (Q1) | literal | `true` in the build; soft delete sets `false` through `soft_delete_set` (U6; mapping media §1.2 row `is_active`) |
| slv_poi_media_info | row_hash | string | nullable per `sql_merge_target` (`t.row_hash IS NULL` is handled) | derived | `sha2(to_json(struct(business columns)), 256)` (`02_NAMING_CONVENTION.md` §5.2); used by `sql_merge_target` |
| slv_poi_media_info | created_at | timestamp | not stated (Q1) | technical | `sql_merge_target` INSERT only (mapping media §1.2 row `created_at`) |
| slv_poi_media_info | updated_at | timestamp | not stated (Q1) | technical | `sql_merge_target` INSERT, changed-hash UPDATE, soft delete (mapping media §1.2 row `updated_at`) |
| slv_poi_media_info | deleted_at | timestamp | nullable | technical | `sql_merge_target`: NULL on INSERT and UPDATE, `current_timestamp()` on soft delete (Q2) |

Partner branch rules (mapping media §1.1; U3, U4, U7; D-MEDIA-SHAPE):

- Driving rows: `slv_pn_business_service_i18ns` where `locale` is `vi`, excluding `deleted` rows. P2: 121 rows, 121 ids, 0 deleted.
- i18n `media` is empty when it is SQL null, blank, JSON `null`, or `[]`. Then `slv_pn_business_services.media` of the same `poi_id` is used, excluding `deleted` services rows. P3: 47 empty `vi` rows, 0 fallback hits.
- `media` is parsed as a JSON array of objects. Only `url` (string) and `order` (int) are read. There is no root object. `preview` is optional and not mapped. Element keys `description` and `is_cover` are not target columns. The element `is_cover` key does not feed the target `is_cover`.
- An element whose chosen `url` is null or blank is dropped. P5: 1 null url and 1 null order among 192 elements.

### `gld_srv_poi_media_gallery`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| gld_srv_poi_media_gallery | media_id, poi_id, source_name, photo_api_uri, display_order, width_px, height_px, photographer, blob_url, thumbnail_url, is_cover, is_active | same as silver | same as silver (Q1) | `slv_poi_media_info` same-name columns | 1-1 (mapping media §2). No new business columns. |
| gld_srv_poi_media_gallery | row_hash | string | nullable | derived | `sql_merge_target` of the gold MERGE |
| gld_srv_poi_media_gallery | created_at | timestamp | not stated (Q1) | technical | Own gold MERGE value from `sql_merge_target`, not copied from silver (mapping media §2) |
| gld_srv_poi_media_gallery | updated_at | timestamp | not stated (Q1) | technical | Own gold MERGE value from `sql_merge_target`, not copied from silver (mapping media §2) |
| gld_srv_poi_media_gallery | deleted_at | timestamp | nullable | technical | `sql_merge_target` (Q2) |

Gold soft delete sets `is_active = false` (U6; `02_NAMING_CONVENTION.md` §5.2).

### `gld_srv_poi_amenity`

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| gld_srv_poi_amenity | poi_id | string | NOT NULL in source DDL | `slv_poi_amenity.poi_id` | 1-1 (mapping amenity §1) |
| gld_srv_poi_amenity | business_sector | string | NOT NULL in source DDL | `slv_poi_amenity.business_sector` | 1-1 |
| gld_srv_poi_amenity | amenity_group | string | NOT NULL in source DDL | `slv_poi_amenity.amenity_group` | 1-1 |
| gld_srv_poi_amenity | amenity_raw | string | NOT NULL in source DDL | `slv_poi_amenity.amenity_raw` | 1-1 |
| gld_srv_poi_amenity | amenity | string | nullable | `slv_poi_amenity.amenity` | 1-1 |
| gld_srv_poi_amenity | amenity_vi | string | nullable | `slv_poi_amenity.amenity_vi` | 1-1 |
| gld_srv_poi_amenity | service_flags | string | nullable | `slv_poi_amenity.service_flags` | 1-1 |
| gld_srv_poi_amenity | row_hash | string | nullable | derived | `sql_merge_target` |
| gld_srv_poi_amenity | created_at | timestamp | nullable | technical | Own gold MERGE value, not copied from silver (mapping amenity §1) |
| gld_srv_poi_amenity | updated_at | timestamp | nullable | technical | Own gold MERGE value, not copied from silver (mapping amenity §1) |
| gld_srv_poi_amenity | deleted_at | timestamp | nullable | technical | `sql_merge_target` |

The mapping states nullability only for the `slv_poi_amenity` DDL. Gold nullability is assumed to be the same (Q1). The gold table has no `is_active`; see Q3.

## Lineage

| target | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_poi_media_info` | None | `lh_vv_silver.dbo.slv_3p_poi_media`, `lh_vv_silver.dbo.slv_pn_business_service_i18ns` (`locale = vi`, not deleted), `lh_vv_silver.dbo.slv_pn_business_services` (fallback only, not deleted) | None |
| `lh_vv_gold.dbo.gld_srv_poi_media_gallery` | None | `lh_vv_silver.dbo.slv_poi_media_info` | None |
| `lh_vv_gold.dbo.gld_srv_poi_amenity` | None | `lh_vv_silver.dbo.slv_poi_amenity` | None |

Gold never reads gold. The edges into `slv_poi_amenity` (`slv_3p_poi_amenity`, `slv_poi_entity_non_enrich`, `ref_dictionary_amenities`; the retired `slv_poi_entity` edge) are unchanged (mapping amenity §0).

## Conflicts and questions

1. Nullability of `slv_poi_media_info` and both gold tables is not stated. Mapping media §1.2 gives types only. The gold tables are created by `ensure_target` (`02_NAMING_CONVENTION.md` §2.1 rule 7). Do the media key columns (`media_id`, `poi_id`, `source_name`) need NOT NULL? Does gold amenity copy the four NOT NULL key columns of the `slv_poi_amenity` DDL? DEV evidence shows no null `media_id` or `poi_id` on the 3P branch (P1).
2. The mapping lists only `created_at` and `updated_at` as technical columns. `sql_merge_target` also writes `row_hash` and `deleted_at`, and the closed decision says timestamps follow `sql_merge_target`. This design includes `row_hash` and `deleted_at` on all three tables. Please confirm.
3. `gld_srv_poi_amenity` has no `is_active`, because `OUT_COLS` has none and gold may not add business columns (mapping amenity §1). `02_NAMING_CONVENTION.md` §5.2 says gold soft delete comes with `is_active = false`. Should gold amenity soft delete set only `deleted_at`, with an empty `soft_delete_set`?
4. Do gold gallery and gold amenity read silver rows that are already soft-deleted (`deleted_at` not null)? Or do they read only rows where `deleted_at` is null and let the gold MERGE soft-delete the rest? Neither mapping says.
5. `is_cover` when a POI has more than one row and every `display_order` is null: D-MEDIA-12 and U-TIE do not cover this. P1 shows 0 null `display_order` on 3P, but P5 shows one partner element with a null `order`. Is there no cover in that case, or the first row encountered?
6. Partner `media_id` uses `trim(url)`. Two elements of one POI whose urls differ only in surrounding whitespace would get the same `media_id`. The DEV `dup_url_docs = 0` was measured on the raw string, not the trimmed one. Which row is kept on a duplicate `media_id`?
7. Partner rows are driven by `vi` i18n rows (mapping media §1.1). Does a services row with no `vi` i18n row produce media rows? The mapping does not say. DEV: 121 `vi` ids, 30 services ids.
8. Partner `deleted` exclusion: should a row with `deleted` null be kept? DEV shows `deleted = 0` on both tables (P2), so the case was not observed.
9. Note only, no change requested: `PL_VV_TRANS_SLV_TO_GLD_1H` (U1) has no row in `NB_CREATE_DDL`, and the `NB_00_ORCHES_SLV_TO_GLD` parameter cell uses `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. The token stays as decided; the Architect owns the ctrl seeding and invocation.
