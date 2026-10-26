# 1. Table: `slv.slv_poi_media_info`

## 1.1. Xử lý

Append `slv_3p_poi_media` và:

- `slv_pn_business_service_i18ns` (filter chỉ lấy `locale` là `vi`). Bỏ dòng partner `deleted`.
- `media` của i18n là SQL null, chuỗi trắng, JSON `null`, hoặc `[]` thì lấy `slv_pn_business_services.media` của `poi_id` tương ứng. Bỏ dòng `deleted` của bảng services.
- `url` của nguồn đã chọn null hoặc trắng: bỏ phần tử.
- `poi_id` đã có công thức tính cho 2 bảng này. Khóa MERGE của bảng này và `gld_srv_poi_media_gallery` là `media_id`.

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
| | | boolean | Mỗi poi_id có đúng một cover. Một bản ghi: display_order null vẫn là cover. Nhiều bản ghi: order nhỏ nhất khác null. Hòa order, hoặc mọi display_order đều null: dòng gặp đầu tiên là cover | is_cover |
| | | boolean | true. Soft delete thì false | is_active |
| | | timestamp | cột kỹ thuật, cùng rule MERGE `sql_merge_target` của `NB_LIB_TRANSFORM_SLV_GLD` | created_at |
| | | timestamp | cột kỹ thuật, cùng rule MERGE `sql_merge_target` của `NB_LIB_TRANSFORM_SLV_GLD` | updated_at |

---

# 2. Table: `gld_srv_poi_media_gallery`

Transform 1-1 từ `slv.slv_poi_media_info`, chỉ thay đổi `created_at` và `updated_at`.

---
