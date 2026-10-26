Sau mỗi thay đổi nghiệp vụ của bảng trong file này, cùng task cập nhật file này trước review.

## 1. Table: `gld_srv_poi_multi_lang`

Lakehouse.schema: `lh_vv_gold.dbo`.

### 1.1. Xử lý

- `SPEC.inputs`: `multi_lang` = `slv_enr_poi_info_multi_lang`, `entity` = `slv_poi_entity_non_enrich`, `i18n` = `slv_pn_business_service_i18ns`. `required_inputs` = (`multi_lang`, `entity`). `i18n` không bắt buộc. Cả ba gọi `live_only=False`. `write_mode = MERGE`.
- Nguồn là `slv_enr_poi_info_multi_lang` LEFT JOIN `slv_poi_entity_non_enrich` theo `poi_id`. `source_name` lấy từ entity. `slv_enr_poi_info_multi_lang` không có `source_name`. `source_name` null thì notebook cảnh báo `multi_lang_source_name_null`.
- Partner là `lower(trim(source_name)) = 'partner'`. Null không phải partner.
- Partner LEFT JOIN `slv_pn_business_service_i18ns` khi `poi_id` bằng `uuid_md5(business_service_id, 'partner')` và `lang` = `locale`. Cùng cách `NB_SLV_POI_ENTITY_NON_ENRICH` tính `poi_id` dòng partner.
- Partner: `description` = `bio`, `bio` null thì `description` của enr. `experience` = `usps`, `usps` null thì `experience` của enr.
- Dòng không phải partner lấy `description` và `experience` của `slv_enr_poi_info_multi_lang`.
- MERGE theo grain `(poi_id, lang)`. `lang` nguồn `slv_enr_poi_info_multi_lang` là `STRING`; DDL landing không ghi `NOT NULL`. Target `gld_srv_poi_multi_lang.lang` là `STRING NOT NULL`. `quality_gate` trong `NB_LIB_TRANSFORM_SLV_GLD` chặn dòng khóa NULL, nên `poi_id` hoặc `lang` null thì dừng.
- `pl_name` hiện hành: `PL_VV_TRANS_SLV_TO_GLD_30M` (`plcadpy` đổi từ `PL_VV_TRANS_SLV_TO_GLD_30P`). `load_mode = RECOMPUTE`, `priority = 1`. Ba cạnh `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, `slv_pn_business_service_i18ns` → `gld_srv_poi_multi_lang`, `nb_name = NB_GLD_SRV_POI_MULTI_LANG`. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15M`.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_enr_poi_info_multi_lang.poi_id | string NOT NULL | transform 1-1 | poi_id |
| slv_enr_poi_info_multi_lang.lang | string | transform 1-1 | lang |
| slv_poi_entity_non_enrich.source_name | string | transform 1-1 theo poi_id | source_name |
| slv_enr_poi_info_multi_lang.time_to_spend | string | transform 1-1 | time_to_spend |
| slv_enr_poi_info_multi_lang.best_time | string | transform 1-1 | best_time |
| slv_enr_poi_info_multi_lang.cost_vnd | string | transform 1-1 | cost_vnd |
| slv_pn_business_service_i18ns.bio, fallback slv_enr_poi_info_multi_lang.description | string | partner: bio, bio null thì description enr; nguồn khác: description enr | description |
| slv_pn_business_service_i18ns.usps, fallback slv_enr_poi_info_multi_lang.experience | string | partner: usps, usps null thì experience enr; nguồn khác: experience enr | experience |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |
