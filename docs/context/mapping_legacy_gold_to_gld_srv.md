# Mapping gold cũ sang năm bảng gold mới

Nguồn cũ: `sgr_visitvn_prd_batch.lh_vv_gold.dbo`. Đích: `<p_target_ws>.lh_vv_gold.dbo`. Đây là mapping của lần init `NB_SETUP_LEGACY_GOLD_POI`. Pipeline định kỳ vẫn đọc silver, không đọc bảng này.

Mỗi cột của năm bảng gold mới có một dòng. Cột ghi `Không nạp` là cột gold cũ không có giá trị tương ứng, nên dòng init để NULL. Lần chạy sau cập nhật dòng `load_origin = LEGACY_INIT` và không sửa dòng do pipeline ghi.

`poi_id` mới không copy từ `poi_master.poi_id`. Bảng `gld_poi_legacy_id_map` tính nó từ `poi_master.source_id` và `poi_master.ingestion_source`:

| `ingestion_source` cũ | `source_name` mới | Công thức |
|---|---|---|
| `google` | `google` | `regexp_replace(md5(concat('google', source_id)), 8-4-4-4-12)` |
| `partner_portal` | `partner` | `regexp_replace(md5(concat(source_id, 'partner')), 8-4-4-4-12)` |

Thứ tự cột info, multi-lang và review theo `DESCRIBE` trên DEV ngày 2026-11-20. Amenity và media theo `AMENITY_COLS` và `MEDIA_COLS` trong `NB_CREATE_DDL`. Hai bảng đó không có `DESCRIBE` trong task này và không có `load_origin`.

## 1. `gld_srv_poi_info` (37 cột)

`poi_name` và `district` lấy từ dòng `poi_master` có `lang = vi`. Các cột nghiệp vụ còn lại phải giống nhau giữa mọi lang của cùng `poi_id` mới. Lệch thì không ghi khóa đó.

| # | Cột mới | Bảng cũ | Trường cũ | Cách lấy |
|---|---|---|---|---|
| 1 | `poi_id` | `poi_master` | `source_id`, `ingestion_source` | `poi_id` trên map |
| 2 | `poi_name` | `poi_master` | `poi_name` | Dòng `lang = vi`. Không có `vi` thì NULL |
| 3 | `source_name` | `poi_master` | `ingestion_source` | `google` giữ nguyên. `partner_portal` thành `partner` |
| 4 | `business_sector` | `poi_master` | `business_sector` | Cùng tên. Phải giống nhau giữa các lang |
| 5 | `business_category` | `poi_master` | `business_category` | Cùng tên. Phải giống nhau giữa các lang |
| 6 | `subcategory_tags` | `poi_master` | `subcategory_tags` | Giữ chuỗi. Phải giống nhau giữa các lang |
| 7 | `destination_id` | `poi_master` | `destination_ids` | Cả JSON array, `to_json(from_json(.., array<string>))`, mọi lang của `poi_id` mới phải giống nhau; shape khác hoặc lệch thì dừng USER_DECISION |
| 8 | `destination_name` | `poi_master` | `destination_names` | Nguyên chuỗi JSON, dòng `lang = vi` |
| 9 | `full_address` | `poi_detail` | `poi_address_json` | `$.full_address` |
| 10 | `street` | `poi_detail` | `poi_address_json` | `$.address_line1` |
| 11 | `ward` | `poi_detail` | `poi_address_json` | `$.ward` |
| 12 | `district` | `poi_master` | `district` | Dòng `lang = vi`. Không có `vi` thì NULL |
| 13 | `city` | `poi_detail` | `poi_address_json` | `$.city` |
| 14 | `country_code` | `poi_detail` | `poi_address_json` | `$.country_code` |
| 15 | `postal_code` | `poi_detail` | `poi_address_json` | `$.postal_code` |
| 16 | `lat` | `poi_detail` | `poi_address_json` | `$.lat` |
| 17 | `lng` | `poi_detail` | `poi_address_json` | `$.lng` |
| 18 | `phone` | `poi_detail` | `poi_contact_json` | `$.phone` |
| 19 | `email` | `poi_detail` | `poi_contact_json` | `$.email` |
| 20 | `website_url` | `poi_detail` | `poi_contact_json` | `$.website_url` |
| 21 | `operating_status` | `poi_master` | `operating_status` | Cùng tên. Phải giống nhau giữa các lang |
| 22 | `is_verified` | `poi_master` | `is_verified` | Cùng tên. Phải giống nhau giữa các lang |
| 23 | `is_recommended` | `poi_master` | `is_recommended` | Dòng `lang = vi` |
| 24 | `is_bookable` | `poi_master` | `is_bookable` | Cùng tên. Phải giống nhau giữa các lang |
| 25 | `is_active` |  |  | Hằng `true`. Không lấy `poi_master.is_active` |
| 26 | `operating_hours` | `poi_detail` | `poi_content_json` | `$.hours_weekday_text` |
| 27 | `holiday_exceptions` | `poi_detail` | `poi_opening_hours_json` | `$.holiday_exceptions` |
| 28 | `rating_overall` | `poi_master` | `rating_overall` | Chỉ `google`. Cast `decimal(3,1)` sang `decimal(4,2)`. Partner để NULL |
| 29 | `rating_count` | `poi_master` | `rating_count` | Chỉ `google`. Cast `bigint` sang `int`. Partner để NULL |
| 30 | `review_count` | `poi_rating` | `total_reviews` | Cùng `poi_id` cũ của dòng `lang = vi` |
| 31 | `cover_id` | `poi_detail` | `poi_media_json` | `$.cover.media_id` |
| 32 | `cover_blob_url` | `poi_detail` | `poi_media_json` | `$.cover.blob_url` |
| 33 | `row_hash` |  |  | Hash các cột nghiệp vụ lúc ghi. Không copy hash cũ |
| 34 | `created_at` |  |  | Thời điểm init. Không copy `poi_master.created_at` |
| 35 | `updated_at` |  |  | Thời điểm init. Không copy `poi_master.updated_at` |
| 36 | `deleted_at` |  |  | NULL |
| 37 | `load_origin` |  |  | Hằng `LEGACY_INIT` trên dòng init chèn |

## 2. `gld_srv_poi_multi_lang` (14 cột)

`lang` là `poi_master.lang` của đúng `poi_id` cũ. Nội dung lấy từ `poi_enrichment_display` cùng `poi_id` cũ.

| # | Cột mới | Bảng cũ | Trường cũ | Cách lấy |
|---|---|---|---|---|
| 1 | `poi_id` | `poi_master` | `source_id`, `ingestion_source` | `poi_id` trên map |
| 2 | `lang` | `poi_master` | `lang` | Qua map |
| 3 | `poi_name` | `poi_master` | `poi_name` | Dòng legacy cùng lang. Nhiều tên thì NULL |
| 4 | `source_name` | `poi_master` | `ingestion_source` | Qua map. Không lấy `poi_enrichment_display.ingestion_source` |
| 5 | `time_to_spend` | `poi_enrichment_display` | `time_to_spend` | Cùng tên |
| 6 | `best_time` | `poi_enrichment_display` | `best_time` | Cùng tên |
| 7 | `cost` | `poi_enrichment_display` | `cost` | Cùng tên, kiểu string |
| 8 | `description` | `poi_enrichment_display` | `description` | Cùng tên |
| 9 | `experience` | `poi_enrichment_display` | `experiences` | Đổi tên cột |
| 10 | `row_hash` |  |  | Hash lúc ghi |
| 11 | `created_at` |  |  | Thời điểm init |
| 12 | `updated_at` |  |  | Thời điểm init |
| 13 | `deleted_at` |  |  | NULL |
| 14 | `load_origin` |  |  | Hằng `LEGACY_INIT` trên dòng init chèn |

## 3. `gld_srv_poi_review` (15 cột)

Giữ `review_id` của `poi_review`. Không tính lại bằng sha2. Chỉ chèn khóa chưa có, và chỉ cập nhật dòng `load_origin = LEGACY_INIT`.

| # | Cột mới | Bảng cũ | Trường cũ | Cách lấy |
|---|---|---|---|---|
| 1 | `review_id` | `poi_review` | `review_id` | Giữ nguyên |
| 2 | `poi_id` | `gld_poi_legacy_id_map` | `poi_id` | Map theo `poi_review.poi_id` cũ |
| 3 | `rating_overall` | `poi_rating` | `overall` | Điểm của địa điểm, không phải điểm từng review |
| 4 | `rating_count` | `poi_rating` | `total_reviews` | Số review của địa điểm |
| 5 | `title` | `poi_review` | `title` | Giữ nguyên |
| 6 | `review_text` | `poi_review` | `review_text` | Giữ nguyên |
| 7 | `rating` | `poi_review` | `rating` | Điểm của review |
| 8 | `review_date` | `poi_review` | `review_date` | Ép string |
| 9 | `author_name` | `poi_review` | `reviewer_name` | Đổi tên |
| 10 | `source_name` | `poi_review` | `source` | Nếu `source` null thì lấy `source_name` của map |
| 11 | `row_hash` |  |  | NULL trên dòng init |
| 12 | `created_at` |  |  | Thời điểm init |
| 13 | `updated_at` |  |  | Thời điểm init |
| 14 | `deleted_at` |  |  | NULL |
| 15 | `load_origin` |  |  | Hằng `LEGACY_INIT` |

`ai_poi_review` không được ghép. `positive`, `negative`, `sentiment_score`, `awards_json`, `response_text`, `media_urls_json` không có cột mới.

## 4. `gld_srv_poi_amenity` (12 cột)

Nguồn là mọi chuỗi trong mảng `enum` của `poi_detail.amenities_json` (dòng `lang = vi`) và `poi_master.business_sector` cùng dòng đó. Inner join `sgr_visitvn_dev.lh_vv_silver.dbo.ref_dictionary_amenities` khi `is_active` là true, cùng `source_name` và `business_sector`. Chuỗi enum khớp `amenity_raw`, `amenity_en` hoặc `amenity_vi` (không phân biệt hoa thường). Giá trị `true` khớp `amenity_raw` bằng đường dẫn JSON, ví dụ `parkingOptions.freeStreetParking`. Một enum khớp nhiều dòng từ điển thì bỏ enum đó. Bảng có `load_origin`; chỉ cập nhật dòng `LEGACY_INIT`.

| # | Cột mới | Bảng cũ | Trường cũ | Cách lấy |
|---|---|---|---|---|
| 1 | `poi_id` | `gld_poi_legacy_id_map` | `poi_id` | Map của dòng `lang = vi` |
| 2 | `business_sector` | `ref_dictionary_amenities` | `business_sector` | Khớp `poi_master.business_sector` |
| 3 | `amenity_group` | `ref_dictionary_amenities` | `amenity_group` | Dòng từ điển khớp |
| 4 | `amenity_raw` | `ref_dictionary_amenities` | `amenity_raw` | Dòng từ điển khớp enum hoặc khớp đường dẫn khi enum là `true` |
| 5 | `amenity` | `ref_dictionary_amenities` | `amenity` | Dòng từ điển khớp |
| 6 | `amenity_en` | `ref_dictionary_amenities` | `amenity_en` | Dòng từ điển khớp |
| 7 | `amenity_vi` | `ref_dictionary_amenities` | `amenity_vi` | Dòng từ điển khớp |
| 8 | `service_flags` | `ref_dictionary_amenities` | `service_flags` | Dòng từ điển khớp |
| 9 | `row_hash` |  |  | NULL trên dòng init |
| 10 | `created_at` |  |  | Thời điểm init |
| 11 | `updated_at` |  |  | Thời điểm init |
| 12 | `deleted_at` |  |  | NULL |

`load_origin` không nằm trong 12 cột nghiệp vụ. Cell `legacyidpy` thêm cột này. Init ghi `LEGACY_INIT`. Enum không có trong từ điển thì không ghi.

## 5. `gld_srv_poi_media_gallery` (16 cột)

Nguồn là `poi_detail.poi_media_json` của dòng `lang = vi`: `cover` và từng phần tử `gallery`. Bảng có `load_origin`. Init ghi `LEGACY_INIT`. Dòng đã ghi trước khi có cột được đánh dấu lại khi `row_hash` khớp payload init. Dòng pipeline (`load_origin` null và `row_hash` khác) không bị sửa. `NB_GLD_SRV_POI_MEDIA_GALLERY` dùng `run_node`, nên khi cột có trên bảng thì RECOMPUTE không xóa mềm dòng `LEGACY_INIT`.

| # | Cột mới | Bảng cũ | Trường cũ | Cách lấy |
|---|---|---|---|---|
| 1 | `media_id` | `poi_detail` | `poi_media_json` | `cover.media_id` hoặc `gallery[].media_id` |
| 2 | `poi_id` | `gld_poi_legacy_id_map` | `poi_id` | Map của dòng `lang = vi` |
| 3 | `source_name` | `gld_poi_legacy_id_map` | `source_name` | Cùng dòng map |
| 4 | `photo_api_uri` |  |  | Không nạp. JSON cũ không có |
| 5 | `display_order` |  |  | Không nạp. JSON cũ không có |
| 6 | `width_px` |  |  | Không nạp. JSON cũ không có |
| 7 | `height_px` |  |  | Không nạp. JSON cũ không có |
| 8 | `photographer` |  |  | Không nạp. JSON cũ không có |
| 9 | `blob_url` | `poi_detail` | `poi_media_json` | `cover.blob_url` hoặc `gallery[].blob_url` |
| 10 | `thumbnail_url` |  |  | Không nạp. JSON cũ không có |
| 11 | `is_cover` | `poi_detail` | `poi_media_json` | `true` nếu media nằm ở `cover` |
| 12 | `is_active` |  |  | Hằng `true` |
| 13 | `row_hash` |  |  | NULL trên dòng init |
| 14 | `created_at` |  |  | Thời điểm init |
| 15 | `updated_at` |  |  | Thời điểm init |
| 16 | `deleted_at` |  |  | NULL |

`poi_detail.poi_media_json` không được tách vào các cột media ở trên.

## Cột gold cũ không có dòng trong năm bảng

`poi_master`: `slug`, `short_description`, `short_address`, `destination_ids`, `destination_names`, `nearby_pois`, `version`, `event_id`, `ref_type`, `ref_business_sector`, `partner_id`, `poi_group_id`, `is_active`, `is_enrichable`, `is_recommended`, `created_at`, `updated_at`.

`poi_enrichment_display`: `display_id`, `enrichment_id`, `poi_id`, `poi_name`, `display_category`, `experiences`, `enrichment_job_id`, `validation_status`, `display_generated_at`, `is_current`, `created_at`, `updated_at`, `ingestion_source`. `poi_id` và `lang` của bảng này chỉ dùng để khớp dòng, không ghi sang cột đích riêng.

Không đọc để nạp: `poi_detail`, `poi_review`, `poi_rating`, `ai_poi`, `ai_poi_rating`, `ai_poi_review`, `ai_enriched_poi`, `poi_address_enrichment_staging`.
