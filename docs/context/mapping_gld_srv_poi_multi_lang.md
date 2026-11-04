Sau mỗi thay đổi nghiệp vụ của bảng trong file này, cùng task cập nhật file này trước review.

## 1. Table: `gld_srv_poi_multi_lang`

Lakehouse.schema: `lh_vv_gold.dbo`.

### 1.1. Xử lý

- `SPEC.inputs`: `multi_lang` = `slv_enr_poi_info_multi_lang`, `entity` = `slv_poi_entity_non_enrich`, `i18n` = `slv_pn_business_service_i18ns`. `required_inputs` = (`multi_lang`, `entity`). `i18n` không bắt buộc. Cả ba gọi `live_only=False`. `write_mode = MERGE`.
- Bảng đích có hai nhóm dòng. P1 là dòng do `slv_enr_poi_info_multi_lang` dẫn. P2 là dòng chỉ có `slv_pn_business_service_i18ns`. Notebook hợp P1 và P2 bằng `unionByName` rồi MERGE một lần.
- P1: nguồn là `slv_enr_poi_info_multi_lang` LEFT JOIN `slv_poi_entity_non_enrich` theo `poi_id`. `source_name` lấy từ entity. `slv_enr_poi_info_multi_lang` có cột `source_name` (chỉ DDL, cell `mlsrcpy` của `NB_CREATE_DDL`, chưa có writer) nhưng node không đọc cột này: `ML_COLS` không có `source_name`. `source_name` null thì notebook cảnh báo `multi_lang_source_name_null`. Cảnh báo này chỉ đếm P1.
- P1: partner là `lower(trim(source_name)) = 'partner'`. Null không phải partner.
- P1: partner LEFT JOIN `slv_pn_business_service_i18ns` khi `poi_id` bằng `uuid_md5(business_service_id, 'partner')` và `lang` = `locale`. Cùng cách `NB_SLV_POI_ENTITY_NON_ENRICH` tính `poi_id` dòng partner.
- P1: partner có `description` = `bio`, `bio` null thì `description` của enr. `experience` = `usps`, `usps` null thì `experience` của enr.
- P1: dòng không phải partner lấy `description` và `experience` của `slv_enr_poi_info_multi_lang`.
- P2: mỗi dòng `slv_pn_business_service_i18ns` tạo một dòng gold khi `slv_enr_poi_info_multi_lang` không có dòng cùng `(poi_id, lang)`, với `poi_id` = `uuid_md5(business_service_id, 'partner')` và `lang` = `locale`. So khớp bằng `left_anti` theo `(poi_id, lang)`. Không xét `source_name` của entity, nên P1 và P2 không trùng khoá.
- P2 lấy mọi `locale`. Không lọc dòng partner đã xoá, giữ như hiện tại (`live_only=False`). Dòng P2 vẫn tạo khi `bio` và `usps` cùng null.
- P2: `source_name` = `'partner'`. `description` = `bio`, `experience` = `usps`, không fallback. `time_to_spend`, `best_time`, `cost_vnd` = null. P2 không đọc `slv_poi_entity_non_enrich`. Mỗi cột P2 ép về kiểu của cột P1 cùng tên.
- P2: `business_service_id` hoặc `locale` null hoặc rỗng sau `trim` thì bỏ dòng và đếm vào cảnh báo `multi_lang_i18n_key_blank`. Số dòng P2 ghi vào cảnh báo `multi_lang_i18n_only_rows`.
- Khoá P2 có thêm dòng `slv_enr_poi_info_multi_lang` thì chuyển sang P1 (UPDATE cùng khoá). Dòng multi_lang mất mà dòng i18n còn thì chuyển sang P2. Cả hai trường hợp đều không xoá mềm.
- Bảng `slv_enr_poi_info_multi_lang` rỗng thì node vẫn FAILED vì `required_inputs`. P2 chỉ áp cho khoá không khớp, không áp cho bảng rỗng.
- MERGE theo grain `(poi_id, lang)`. `lang` nguồn `slv_enr_poi_info_multi_lang` là `STRING`; DDL landing không ghi `NOT NULL`. Target `gld_srv_poi_multi_lang.lang` là `STRING NOT NULL`. `quality_gate` trong `NB_LIB_TRANSFORM_SLV_GLD` chặn dòng khóa NULL, nên `poi_id` hoặc `lang` null thì dừng.
- `pl_name` hiện hành: `PL_VV_TRANS_SLV_TO_GLD_30M` (`plcadpy` đổi từ `PL_VV_TRANS_SLV_TO_GLD_30P`). `load_mode = RECOMPUTE`, `priority = 1`. Ba cạnh `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, `slv_pn_business_service_i18ns` → `gld_srv_poi_multi_lang`, `nb_name = NB_GLD_SRV_POI_MULTI_LANG`. Không gắn `PL_VV_TRANS_SLV_TO_ENR_15M`.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| P1: slv_enr_poi_info_multi_lang.poi_id<br>P2: slv_pn_business_service_i18ns.business_service_id | string NOT NULL | P1: transform 1-1<br>P2: uuid_md5(business_service_id, 'partner') | poi_id |
| P1: slv_enr_poi_info_multi_lang.lang<br>P2: slv_pn_business_service_i18ns.locale | string | P1: transform 1-1<br>P2: transform 1-1, mọi locale | lang |
| P1: slv_poi_entity_non_enrich.source_name | string | P1: transform 1-1 theo poi_id<br>P2: hằng 'partner', không đọc entity | source_name |
| P1: slv_enr_poi_info_multi_lang.time_to_spend | string | P1: transform 1-1<br>P2: null | time_to_spend |
| P1: slv_enr_poi_info_multi_lang.best_time | string | P1: transform 1-1<br>P2: null | best_time |
| P1: slv_enr_poi_info_multi_lang.cost_vnd | string | P1: transform 1-1<br>P2: null | cost_vnd |
| P1: slv_pn_business_service_i18ns.bio, fallback slv_enr_poi_info_multi_lang.description<br>P2: slv_pn_business_service_i18ns.bio | string | P1: partner: bio, bio null thì description enr; nguồn khác: description enr<br>P2: bio, không fallback | description |
| P1: slv_pn_business_service_i18ns.usps, fallback slv_enr_poi_info_multi_lang.experience<br>P2: slv_pn_business_service_i18ns.usps | string | P1: partner: usps, usps null thì experience enr; nguồn khác: experience enr<br>P2: usps, không fallback | experience |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |
