Sau mỗi thay đổi nghiệp vụ của bảng trong file này, cùng task cập nhật file này trước review.

# 1. Table: `slv.slv_poi_media_info`

## 1.1. Xử lý

Append `slv_3p_poi_media` và:

- `slv_pn_business_service_i18ns` (filter chỉ lấy `locale` là `vi`). Bỏ dòng partner `deleted`.
- `media` của i18n là SQL null, chuỗi trắng, JSON `null`, hoặc `[]` thì lấy `slv_pn_business_services.media` của `poi_id` tương ứng. Bỏ dòng `deleted` của bảng services.
- `url` của nguồn đã chọn null hoặc trắng: bỏ phần tử.
- Chuỗi `media` chỉ parse khi bắt đầu bằng `[`. Không parse được thì không ra phần tử và notebook cảnh báo `partner_media_unparsed`.
- `poi_id` đã có công thức tính cho 2 bảng này. Khóa MERGE của bảng này và `gld_srv_poi_media_gallery` là `media_id`. `write_mode = MERGE`. Nullability của `slv_3p_poi_media.media_dedup_key`: `MISSING`. Target `media_id` là `STRING NOT NULL`. `quality_gate` chặn `media_id` null.
- `SPEC.inputs`: `media_3p` = `slv_3p_poi_media`, `i18n` = `slv_pn_business_service_i18ns`, `services` = `slv_pn_business_services`. `required_inputs` = (`media_3p`, `i18n`). `services` không bắt buộc. `soft_delete_set`: `is_active` = false.
- Pipeline hiện hành `PL_VV_TRANS_SLV_TO_GLD_30M` (`plcadpy` đổi từ `PL_VV_TRANS_SLV_TO_GLD_30P`; cell `mediaddlpy` còn literal `30P`). `load_mode = RECOMPUTE`, `priority = 1`. Ba cạnh `slv_3p_poi_media`, `slv_pn_business_service_i18ns`, `slv_pn_business_services` → `slv_poi_media_info`, `nb_name = NB_SLV_POI_MEDIA_INFO`. Markdown notebook ghi RECOMPUTE.

## 1.2. Field Mapping

| source field 3p | source field partner | data type | transform | target field |
|---|---|---|---|---|
| slv_3p_poi_media.media_dedup_key | | string | 3rd: transform 1-1<br>partner: (media_id tính bằng `sha2(concat_ws('\|', 'partner', poi_id, trim(slv_pn_business_service_i18ns.media.url)), 256)`)<br>hoặc (media_id tính bằng `sha2(concat_ws('\|', 'partner', poi_id, trim(slv_pn_business_services.media.url)), 256)`) | media_id |
| slv_3p_poi_media.poi_id | | string | 3rd: transform 1-1<br>partner: poi_id của i18n tính bằng `uuid_md5(business_service_id, 'partner')` | poi_id |
| | | string | data từ slv_3p_poi_media tương ứng google; data từ slv_pn_business_service_i18ns và slv_pn_business_services tương ứng partner | source_name |
| slv_3p_poi_media.photo_api_uri | null | string | 3rd: transform 1-1 | photo_api_uri |
| slv_3p_poi_media.display_order | slv_pn_business_service_i18ns.media.order hoặc slv_pn_business_services.media.order | integer | 3rd: transform 1-1<br>partner: slv_pn_business_service_i18ns.media.order hoặc nếu slv_pn_business_service_i18ns.media null/rỗng thì lấy slv_pn_business_services.media.order | display_order |
| slv_3p_poi_media.width_px | null | integer | 3rd: transform 1-1 | width_px |
| slv_3p_poi_media.height_px | null | integer | 3rd: transform 1-1 | height_px |
| slv_3p_poi_media.photographer | null | string | 3rd: transform 1-1 | photographer |
| slv_3p_poi_media.blob_url | slv_pn_business_service_i18ns.media.url hoặc slv_pn_business_services.media.url | string | 3rd: transform 1-1<br>partner: giữ nguyên chuỗi `media.url`, không trim. i18n null/rỗng thì lấy url của services | blob_url |
| null | null | string | null | thumbnail_url |
| | | boolean | Mỗi poi_id một cover: row_number = 1 theo display_order tăng, null cuối, rồi _pos tăng, null cuối, rồi media_id tăng. Google _pos là null. Partner _pos là vị trí posexplode. Một dòng vẫn là cover kể cả display_order null | is_cover |
| | | boolean | true. Soft delete thì false | is_active |
| | | timestamp | cột kỹ thuật, cùng rule MERGE `sql_merge_target` của `NB_LIB_TRANSFORM_SLV_GLD` | created_at |
| | | timestamp | cột kỹ thuật, cùng rule MERGE `sql_merge_target` của `NB_LIB_TRANSFORM_SLV_GLD` | updated_at |

---

# 2. Table: `gld_srv_poi_media_gallery`

`NB_GLD_SRV_POI_MEDIA_GALLERY` RECOMPUTE `lh_vv_gold.dbo.gld_srv_poi_media_gallery`. Bản 1-1: `build` trả `select(*OUT_COLS)` từ `slv_poi_media_info`. `SPEC.inputs`: `media` = `slv_poi_media_info`. `required_inputs` = (`media`,). Khóa MERGE `media_id`. `write_mode = MERGE`. `soft_delete_set`: `is_active` = false.

Notebook không gán `created_at` hay `updated_at`. `sql_merge_target` ghi `row_hash`, `created_at`, `updated_at`, `deleted_at`.

Pipeline `PL_VV_TRANS_SLV_TO_GLD_30M`. Cạnh `slv_poi_media_info` → `gld_srv_poi_media_gallery`, `load_mode = RECOMPUTE`, `priority = 1`, `nb_name = NB_GLD_SRV_POI_MEDIA_GALLERY`.

---
