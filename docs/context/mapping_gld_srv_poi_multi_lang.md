## 1. Table: `gld_srv_poi_multi_lang`

Lakehouse.schema: `lh_vv_gold.dbo`.

### 1.1. Xử lý

- `source_name` lấy từ `slv_poi_entity_non_enrich.source_name` theo `poi_id`. `slv_enr_poi_info_multi_lang` không có `source_name`.
- Với `source_name = 'partner'`, `slv_enr_poi_info_multi_lang` LEFT JOIN `slv_pn_business_service_i18ns`. `poi_id` của i18n tính bằng `uuid_md5(business_service_id, 'partner')`, cùng cách `NB_SLV_POI_ENTITY_NON_ENRICH` tính `poi_id` dòng partner. Join `poi_id = poi_id` và `lang` = `locale` của `slv_pn_business_service_i18ns`.
- Partner: `description` lấy `bio`. Khi `bio` null, lấy `description` của `slv_enr_poi_info_multi_lang`.
- Dòng không phải partner lấy `description` của `slv_enr_poi_info_multi_lang`.
- MERGE theo grain `(poi_id, lang)`.
- `pl_name`: `PL_VV_TRANS_SLV_TO_GLD_30P`. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15P`.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_poi_entity_non_enrich.source_name | string | transform 1-1 theo poi_id | source_name |
| slv_enr_poi_info_multi_lang.poi_id | string | transform 1-1 | poi_id |
| slv_enr_poi_info_multi_lang.lang | string | transform 1-1 | lang |
| slv_enr_poi_info_multi_lang.time_to_spend | string | transform 1-1 | time_to_spend |
| slv_enr_poi_info_multi_lang.best_time | string | transform 1-1 | best_time |
| slv_enr_poi_info_multi_lang.cost_vnd | string | transform 1-1 | cost_vnd |
| slv_pn_business_service_i18ns.bio, fallback slv_enr_poi_info_multi_lang.description | string | partner: bio, bio null thì description enr; nguồn khác: description enr | description |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |
