# Author input

Replace the previous `model-design.md`. No `proposal.md`. Do not invent a sort column, a `pl_name`, or a JSON shape.

## Read

- `docs/context/mapping_poi_media_info.md` (whole)
- `docs/context/mapping_gld_srv_poi_amenity.md` (whole)
- `.ai/tasks/20261025-poi-media-and-srv-amenity/decision.md` section `Quyết định hiện hành`
- `.ai/tasks/20261025-poi-media-and-srv-amenity/evidence/results/media_key_grain.txt`
- `.ai/tasks/20261025-poi-media-and-srv-amenity/evidence/results/partner_media_shape.txt`
- `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` function `sql_merge_target` only

## Closed decisions

- Physical: `lh_vv_silver.dbo.slv_poi_media_info`. Gold: `lh_vv_gold.dbo.gld_srv_poi_media_gallery`, `lh_vv_gold.dbo.gld_srv_poi_amenity`. No SQL schema `slv`.
- `pl_name`: media silver and gallery `PL_VV_TRANS_SLV_TO_GLD_30P`. Amenity gold `PL_VV_TRANS_SLV_TO_GLD_1H`. Keep that token. Do not rename it to `PL_VV_TRANSFORM_SLV_TO_GLD_1H`.
- MERGE key of silver media and gallery: `media_id` alone.
- 3P `media_dedup_key` maps 1-1 to `media_id`. DEV: 940 rows, 940 distinct keys, no null key, poi, or `display_order`.
- Partner `media_id = sha2(concat_ws('|', 'partner', poi_id, trim(url)), 256)`. `blob_url` keeps the raw url string, not trimmed.
- Partner `poi_id`: i18n `uuid_md5(business_service_id, 'partner')`; services `uuid_md5(id, 'partner')`. DEV overlap with 3P `poi_id` is 0 for both.
- Populated `media` is a JSON array of objects. `url` string, `order` int. No root object. `preview` is optional. Element keys `description` and `is_cover` are not target columns.
- Empty i18n `media`: SQL null, blank, JSON null, or `[]`, then use services `media`. DEV: 47 empty `vi` rows, 0 fallback hits. `vi` is 121 rows and 121 ids. Services is 30 rows and 30 ids. `deleted = 0` on both.
- Drop a partner element whose chosen `url` is null or blank. DEV: 1 null url and 1 null order among 192 elements.
- Exclude partner rows with `deleted`.
- `source_name`: `google` for 3P, `partner` for the partner branch.
- `is_cover` boolean. One url row: null `display_order` is still the cover. More than one row: smallest order that is not null. Tie: the row encountered first. Do not add a sort column. DEV has 5 POIs with more than one row at the minimum `display_order`.
- `is_active` true. Soft delete sets it false.
- Timestamps follow `sql_merge_target`. Gold is 1-1, no new business columns. Do not change `slv_poi_amenity` grain, key, logic, or edges.
- Silver media is a union. The mapping word Append is not Delta append-only.

## Ask instead of inventing

Only if a rule above still has no column or literal. Do not reopen U1–U7.
