## Ngoại lệ model

Người dùng duyệt ngày 2026-10-13. Người viết đề xuất này là Claude Code, model `claude-opus-5-5`, effort `medium`. Đây không phải lượt Architect. Architect vẫn là `claude-opus-5-5` effort `high` và chỉ viết `architecture.md` qua `run-gate`. `models.architect.effort` giữ `high` vì validator từ chối giá trị khác.

## Phạm vi đề xuất

- Đổi hằng số `RAW_PAYLOAD` trong `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` từ `normalized_payload` sang `raw_payload`. `RAW_EVENT_ID`, `RAW_DOC_ID = ("source_name", "source_id")`, `RAW_LANG = language_code` giữ nguyên (xem Q1).
- Không xoá cột bronze `normalized_payload` ở lượt này. Không áp dụng mapping ở lượt này.
- Extract chỉ tách cấu trúc và cast kiểu. Không thêm rule nghiệp vụ. Cột cần chọn phần tử theo điều kiện (vd chọn `addressComponents[]` theo `types`) không làm ở L1.
- Bằng chứng: file mẫu có 3 object (xem `payload_shape_md`). Một mẫu không phải hợp đồng schema. Khoá có mặt nhưng chỉ có giá trị null trong mẫu được ghi `NULL_IN_SAMPLE`, không có nghĩa là luôn null.

Quy ước trạng thái:

- `IN_SAMPLE`: khoá có trong mẫu với giá trị khác null.
- `NULL_IN_SAMPLE`: khoá có trong mẫu nhưng chỉ thấy null. Kiểu chưa có bằng chứng.
- `MISSING_EVIDENCE`: không có khoá tương ứng trong mẫu. Không kết luận cột luôn null.

Đề xuất chung cho cột `MISSING_EVIDENCE` đang bật: tắt trong registry (`is_active = false`), không gỡ, để giữ giá trị cũ trong bảng đích và bật lại được khi có bằng chứng (Q4). Cột đã tắt sẵn giữ tắt.

Đề xuất chung cho `src_object`: raw không còn các khối `poi_address`, `poi_contact`, `poi_price`, `poi_opening_hours`, `poi_rating`, `poi_amenity`, `policies`. Bảng DOC lấy từ nhiều khoá cấp 1 chuyển sang `src_object = $` (đường dẫn tính từ gốc, đường dẫn lồng `a.b` như `location.latitude`). Bảng DOC_ARRAY chuyển sang mảng raw. Hệ quả ngữ nghĩa nằm ở Q3.

## slv_3p_poi (DOC, `src_object` `$` giữ nguyên)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `_doc.source_name,_doc.source_id` `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `source_name` | `_doc.source_name`, string | giữ | không đổi | cột bronze, phụ thuộc Q1 | — |
| `source_id` | `_doc.source_id`, string | giữ | không đổi | cột bronze, phụ thuộc Q1 | — |
| `language_code` | `_doc.language_code` `LOWER_TRIM`, string | giữ | không đổi | cột bronze, raw không có khoá ngôn ngữ cấp 1 (Q1) | — |
| `poi_name` | `poi_name`, string | đổi `json_path` | `displayName`, string | `IN_SAMPLE` (Q11) | `gld_enr_poi_info.poi_name`, `gld_enr_poi_coordinate.name`, `slv_poi_localization.poi_name` |
| `poi_name_normalized` | `poi_name_normalized`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `business_sector` | `business_sector`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q6) | `gld_enr_poi_info.business_sector`, `gld_enr_poi_info.time_to_spend`, `slv_poi.business_sector`, `slv_poi.poi_type` |
| `business_category` | `business_category`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q6) | `gld_enr_poi_info.business_category`, `slv_poi.business_category` |
| `types_json` | `types`, string (JSON) | giữ | `types`, string (JSON) | `IN_SAMPLE` | — |
| `operating_status` | `operating_status`, string | đổi `json_path` | `businessStatus`, string | `IN_SAMPLE` | `slv_poi.operating_status` (Q13) |
| `slug` | `slug`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | `slv_poi_localization.slug` (Q13) |
| `partner_id` | `partner_id`, string, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `collector_poi_id` | `poi_id`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `subcategory_tags_json` | `subcategory_tags`, string (JSON) | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | `slv_poi.subcategory_tags` (Q13) |
| `facilities_json` | `facilities`, string (JSON) | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `source_created_at` | `created_at` `ISO_UTC_TS`, timestamp | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `accommodation_type` | `accommodation_type`, string, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `star_rating` | `star_rating`, string, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `awards_json` | `awards`, string, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `slug_history_json` | `slug_history`, string, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `poi_amenity_schema_json` | `poi_amenity_schema`, string, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `primary_type` | — | thêm cột | `primaryType`, string | `IN_SAMPLE` | — |
| `primary_type_display_name` | — | thêm cột | `primaryTypeDisplayName.text`, string | `IN_SAMPLE` | — |
| `primary_type_display_lang` | — | thêm cột | `primaryTypeDisplayName.languageCode`, string | `IN_SAMPLE` | — |
| `pure_service_area_business` | — | thêm cột | `pureServiceAreaBusiness`, boolean | `NULL_IN_SAMPLE` (Q12) | — |

## slv_3p_poi_address (DOC, `src_object` `poi_address` → `$`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `address_line1` | `address_line1`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | `slv_poi_address` (N3, Q13) |
| `address_line2` | `address_line2`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | `slv_poi_address` (N3, Q13) |
| `house_number` | `house_number`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `slv_poi_address` (N3, Q13) |
| `street` | `street`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `slv_poi_address` (N3, Q13) |
| `ward` | `ward`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `gld_enr_poi_coordinate.ward`, `slv_poi_address.ward_norm` (Q13) |
| `district` | `district`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `gld_enr_poi_coordinate.district`, `gld_enr_poi_info.district`, `gld_enr_poi_info.destination_context` |
| `city` | `city`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `gld_enr_poi_coordinate.province_name`, `gld_enr_poi_coordinate.destination_name`, `gld_enr_poi_info.destination_name`, `gld_enr_poi_info.destination_context` |
| `state_province` | `state_province`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `gld_enr_poi_coordinate.destination_name`, `gld_enr_poi_info.destination_name`, `gld_enr_poi_info.destination_context`, `slv_poi_address.province_norm` (Q13) |
| `country` | `country`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `slv_poi_address` (N3, Q13) |
| `country_code` | `country_code`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `slv_poi_address` (N3, Q13) |
| `postal_code` | `postal_code`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (Q5) | `slv_poi_address` (N3, Q13) |
| `short_address` | `short_address`, string | đổi `json_path` | `shortFormattedAddress`, string | `IN_SAMPLE` | `gld_enr_poi_coordinate.short_address`, `gld_enr_poi_info.destination_context`, `slv_poi_address` (N3, Q13) |
| `full_address` | `full_address`, string | đổi `json_path` | `formattedAddress`, string | `IN_SAMPLE` | `slv_poi_address` (N3, Q13) |
| `address_viet_map` | `address_viet_map`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | `gld_enr_poi_info.short_address`, `slv_poi_address` (N3, Q13) |
| `vietmap_status` | `vietmap_status`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | `slv_poi_address` (N3, Q13) |
| `vietmap_message` | `vietmap_message`, string, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `lat` | `lat`, double | đổi `json_path` | `location.latitude`, double | `IN_SAMPLE` | `gld_enr_poi_coordinate.lat`, `slv_poi_address` (N3, Q13) |
| `lng` | `lng`, double | đổi `json_path` | `location.longitude`, double | `IN_SAMPLE` | `gld_enr_poi_coordinate.lng`, `slv_poi_address` (N3, Q13) |
| `plus_code` | `plus_code`, string | đổi `json_path` | `plusCode.globalCode`, string | `IN_SAMPLE` | `slv_poi_address` (N3, Q13) |
| `timezone` | `timezone`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (raw chỉ có `utcOffsetMinutes`, không phải tên múi giờ) | không thấy consumer trong repo |
| `address_components_json` | — | thêm cột | `addressComponents`, string (JSON) | `IN_SAMPLE` (Q5) | — |
| `plus_compound_code` | — | thêm cột | `plusCode.compoundCode`, string | `IN_SAMPLE` | — |
| `utc_offset_minutes` | — | thêm cột | `utcOffsetMinutes`, int | `IN_SAMPLE` | — |

## slv_3p_poi_contact (DOC, `src_object` `poi_contact` → `$`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `phone` | `phone`, string | đổi `json_path` | `nationalPhoneNumber`, string | `IN_SAMPLE` (1 trên 3 object) | không thấy consumer trong repo |
| `phone_raw` | `phone_raw`, string | đổi `json_path` | `internationalPhoneNumber`, string | `IN_SAMPLE` (1 trên 3 object) | không thấy consumer trong repo |
| `website_url` | `website_url`, string | đổi `json_path` | `websiteUri`, string | `IN_SAMPLE` (1 trên 3 object) | `gld_enr_poi_info.website_url` |
| `google_maps_url` | `google_maps_url`, string | đổi `json_path` | `googleMapsUri`, string | `IN_SAMPLE` | không thấy consumer trong repo |
| `booking_links_json` | `booking_links`, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `delivery_links_json` | `delivery_links`, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `social_links_json` | `social_links`, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `google_maps_links_json` | — | thêm cột | `googleMapsLinks`, string (JSON) | `IN_SAMPLE` | — |

## slv_3p_poi_price (DOC, `src_object` `poi_price` → `$`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `currency` | `currency`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (`priceRange` chỉ null, khoá con chưa thấy) | không thấy consumer trong repo |
| `price_level` | `price_level`, int | đổi `json_path`; kiểu chờ Q9 | `priceLevel`, kiểu chưa xác định | `NULL_IN_SAMPLE` (Q9) | `gld_enr_poi_info.priceLevel` |
| `price_min` | `price_min`, decimal(18,2) | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `price_max` | `price_max`, decimal(18,2) | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `price_range_json` | — | thêm cột | `priceRange`, string (JSON) | `NULL_IN_SAMPLE` | — |

## slv_3p_poi_opening_hours (DOC, `src_object` `poi_opening_hours` → `$`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `is_24_7` | `is_24_7`, boolean | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `is_temporarily_closed` | `is_temporarily_closed`, boolean | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `periods_json` | `periods`, string (JSON) | đổi `json_path` | `regularOpeningHours.periods`, string (JSON) | `MISSING_EVIDENCE` (khối cha chỉ null, khoá con chưa thấy; Q10) | `gld_enr_poi_info.opening_hours_text` |
| `secondary_hours_json` | `secondary_hours`, string (JSON) | đổi `json_path` | `regularSecondaryOpeningHours`, string (JSON) | `IN_SAMPLE` | không thấy consumer trong repo |
| `weekday_text_json` | `weekday_text`, string (JSON) | đổi `json_path` | `regularOpeningHours.weekdayDescriptions`, string (JSON) | `MISSING_EVIDENCE` (Q10) | không thấy consumer trong repo |
| `open_now` | `open_now`, boolean | đổi `json_path` | `currentOpeningHours.openNow`, boolean | `MISSING_EVIDENCE` (Q10) | không thấy consumer trong repo |
| `current_opening_hours_json` | — | thêm cột | `currentOpeningHours`, string (JSON) | `NULL_IN_SAMPLE` | — |
| `current_secondary_hours_json` | — | thêm cột | `currentSecondaryOpeningHours`, string (JSON) | `IN_SAMPLE` | — |

## slv_3p_poi_rating (DOC, `src_object` `poi_rating` → `$`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `rating_overall` | `rating_overall`, decimal(4,2) | đổi `json_path` | `rating`, decimal(4,2) | `IN_SAMPLE` | `gld_enr_poi_info.rating` |
| `rating_count` | `rating_count`, bigint | đổi `json_path` | `userRatingCount`, bigint | `IN_SAMPLE` | `gld_enr_poi_info.userRatingCount` |
| `rating_breakdown_json` | `rating_breakdown`, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `sub_ratings_json` | `sub_ratings`, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |

## slv_3p_poi_amenity (DOC, `src_object` `poi_amenity` → `$`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `amenity_schema_json` | `amenity_schema`, string (JSON) | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `ext_attributes_json` | `ext_attributes`, string (JSON) | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `serves_coffee` | — | thêm cột | `servesCoffee`, boolean | `IN_SAMPLE` | — |
| `outdoor_seating` | — | thêm cột | `outdoorSeating`, boolean | `IN_SAMPLE` | — |
| `restroom` | — | thêm cột | `restroom`, boolean | `IN_SAMPLE` | — |
| `good_for_children` | — | thêm cột | `goodForChildren`, boolean | `IN_SAMPLE` | — |
| `serves_breakfast`, `serves_brunch`, `serves_lunch`, `serves_dinner`, `serves_beer`, `serves_wine`, `serves_cocktails`, `serves_dessert`, `serves_vegetarian_food`, `allows_dogs`, `good_for_groups`, `good_for_watching_sports`, `live_music`, `menu_for_children`, `reservable`, `takeout`, `delivery`, `dine_in`, `curbside_pickup` | — | thêm cột (mỗi khoá 1 cột) | khoá camelCase cùng tên (`servesBreakfast`, …, `curbsidePickup`), boolean | `NULL_IN_SAMPLE` (Q12) | — |
| `parking_options_json` | — | thêm cột | `parkingOptions`, string (JSON) | `IN_SAMPLE` | — |
| `payment_options_json` | — | thêm cột | `paymentOptions`, string (JSON) | `IN_SAMPLE` | — |
| `accessibility_options_json` | — | thêm cột | `accessibilityOptions`, string (JSON) | `IN_SAMPLE` | — |
| `ev_charge_options_json` | — | thêm cột | `evChargeOptions`, string (JSON) | `NULL_IN_SAMPLE` | — |
| `fuel_options_json` | — | thêm cột | `fuelOptions`, string (JSON) | `NULL_IN_SAMPLE` | — |

## slv_3p_poi_review (DOC_ARRAY, `src_object` `poi_review` → `reviews`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `review_id` | `_doc.source_name,_doc.source_id,author_name,time` `HASH_SHA256`, string | đổi `json_path` (giữ rule) | `_doc.source_name,_doc.source_id,authorAttribution.displayName,publishTime` `HASH_SHA256`, string | `IN_SAMPLE` (Q7) | `gld_enr_poi_review.review_id`, `gld_enr_poi_info.review_json` |
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `author_name` | `author_name`, string | đổi `json_path` | `authorAttribution.displayName`, string | `IN_SAMPLE` | không thấy consumer trong repo |
| `rating` | `rating`, decimal(4,2) | giữ | `rating`, decimal(4,2) | `IN_SAMPLE` | — |
| `source` | `source`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `text` | `text`, string | đổi `json_path` | `text.text`, string (trong raw `text` là object) | `IN_SAMPLE` | `gld_enr_poi_review.review_text`, `gld_enr_poi_info.review_json` |
| `time` | `time`, string | đổi `json_path` | `publishTime`, string | `IN_SAMPLE` (Q7) | `gld_enr_poi_review.review_date`, `gld_enr_poi_review.review_updated_at`, `gld_enr_poi_info.review_json` |
| `published_at` | `time` `ISO_UTC_TS`, timestamp | đổi `json_path` | `publishTime` `ISO_UTC_TS`, timestamp | `IN_SAMPLE` | `gld_enr_poi_info.review_json` |
| `review_name` | — | thêm cột | `name`, string | `IN_SAMPLE` | — |
| `relative_publish_time_description` | — | thêm cột | `relativePublishTimeDescription`, string | `IN_SAMPLE` | — |
| `text_language_code` | — | thêm cột | `text.languageCode`, string | `IN_SAMPLE` | — |
| `original_text` | — | thêm cột | `originalText.text`, string | `IN_SAMPLE` | — |
| `original_language_code` | — | thêm cột | `originalText.languageCode`, string | `IN_SAMPLE` | — |
| `author_uri` | — | thêm cột | `authorAttribution.uri`, string | `IN_SAMPLE` | — |
| `author_photo_uri` | — | thêm cột | `authorAttribution.photoUri`, string | `IN_SAMPLE` | — |
| `flag_content_uri` | — | thêm cột | `flagContentUri`, string | `IN_SAMPLE` | — |
| `google_maps_uri` | — | thêm cột | `googleMapsUri`, string | `IN_SAMPLE` | — |

## slv_3p_poi_media (DOC_ARRAY, `src_object` `poi_media` → `photos`)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `media_dedup_key` | `_doc.source_name,_doc.source_id,photo_api_uri` `HASH_SHA256_PIPE`, string | đổi `json_path` (giữ rule) | `_doc.source_name,_doc.source_id,name` `HASH_SHA256_PIPE`, string | `IN_SAMPLE` (Q8) | không thấy consumer trong repo |
| `poi_id` | `HASH_MD5_UUID`, string | giữ | không đổi | phụ thuộc Q1 | — |
| `media_id` | `media_id`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `photo_api_uri` | `photo_api_uri`, string | đổi `json_path` | `name`, string | `IN_SAMPLE` (Q8) | không thấy consumer trong repo |
| `media_type` | `media_type`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `blob_url` | `blob_url`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `original_url` | `original_url`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `thumbnail_url` | `thumbnail_url`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `processing_status` | `processing_status`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `category` | `category`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `caption` | `caption`, đang tắt | giữ tắt | — | `MISSING_EVIDENCE` | — |
| `is_blessed` | `is_blessed`, boolean | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `display_order` | `display_order`, int | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | `ctrl_mng_pipeline_config.dedup_order` của `slv_3p_poi_media` |
| `photographer` | `photographer`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` (tên người đăng nằm trong mảng `authorAttributions[]`, chọn phần tử là rule) | không thấy consumer trong repo |
| `license` | `license`, string | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `file_size_bytes` | `file_size_bytes`, bigint | tắt (`is_active = false`) | — | `MISSING_EVIDENCE` | không thấy consumer trong repo |
| `width_px` | `width_px`, int, đang tắt | đổi `json_path`, bật (`is_active = true`) | `widthPx`, int | `IN_SAMPLE` | — |
| `height_px` | `height_px`, int, đang tắt | đổi `json_path`, bật (`is_active = true`) | `heightPx`, int | `IN_SAMPLE` | — |
| `photo_pos` | — | thêm cột | `_pos`, int | vị trí phần tử trong `photos[]` | — |
| `author_attributions_json` | — | thêm cột | `authorAttributions`, string (JSON) | `IN_SAMPLE` | — |
| `flag_content_uri` | — | thêm cột | `flagContentUri`, string | `IN_SAMPLE` | — |
| `google_maps_uri` | — | thêm cột | `googleMapsUri`, string | `IN_SAMPLE` | — |

## slv_3p_poi_policy (DOC, `src_object` `policies`, bảng đang tắt)

| Cột | Hiện tại (`json_path`, kiểu) | Hành động | Đề xuất (`json_path`, kiểu) | Trạng thái | Consumer (bảng.cột) |
|---|---|---|---|---|---|
| `poi_id` | `HASH_MD5_UUID`, string | giữ, bảng giữ tắt | không đổi | — | — |
| `policies_json` | `$` của khối `policies`, string | giữ, bảng giữ tắt | không đổi | `MISSING_EVIDENCE` (raw không có khoá `policies`; Q15) | — |

## ctrl_cfg_schema_registry và ctrl_mng_pipeline_config

Ngoài config: hằng số `RAW_PAYLOAD` trong notebook đổi thành `raw_payload`. Khi áp dụng, các dòng registry mới cần thêm vào `TABLE_CONFIGS_3P` trong `notebooks/NB_CREATE_DDL.ipynb`.

| Bảng config | Dòng config (`trg_tbl` / `col_name`) | `json_path` | `src_object` | `load_mode` | `data_type` | `is_active` |
|---|---|---|---|---|---|---|
| `ctrl_cfg_schema_registry` | `slv_3p_poi` / `poi_name`, `operating_status` | đổi | không đổi (`$`) | — | không đổi | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi` / `poi_name_normalized`, `business_sector`, `business_category`, `slug`, `collector_poi_id`, `subcategory_tags_json`, `facilities_json`, `source_created_at` | không đổi | không đổi | — | không đổi | `true` → `false` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi` / thêm `primary_type`, `primary_type_display_name`, `primary_type_display_lang`, `pure_service_area_business` | dòng mới | `$` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_address` / mọi dòng | — | `poi_address` → `$` | — | — | — |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_address` / `short_address`, `full_address`, `lat`, `lng`, `plus_code` | đổi | đổi (`$`) | — | không đổi | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_address` / `address_line1`, `address_line2`, `house_number`, `street`, `ward`, `district`, `city`, `state_province`, `country`, `country_code`, `postal_code`, `address_viet_map`, `vietmap_status`, `timezone` | không đổi | đổi (`$`) | — | không đổi | `true` → `false` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_address` / thêm `address_components_json`, `plus_compound_code`, `utc_offset_minutes` | dòng mới | `$` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_contact` / `phone`, `phone_raw`, `website_url`, `google_maps_url` | đổi | `poi_contact` → `$` | — | không đổi | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_contact` / thêm `google_maps_links_json` | dòng mới | `$` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_price` / `price_level` | đổi | `poi_price` → `$` | — | chờ Q9 (hiện `int`) | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_price` / `currency`, `price_min`, `price_max` | không đổi | đổi (`$`) | — | không đổi | `true` → `false` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_price` / thêm `price_range_json` | dòng mới | `$` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_opening_hours` / `periods_json`, `secondary_hours_json`, `weekday_text_json`, `open_now` | đổi | `poi_opening_hours` → `$` | — | không đổi | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_opening_hours` / `is_24_7`, `is_temporarily_closed` | không đổi | đổi (`$`) | — | không đổi | `true` → `false` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_opening_hours` / thêm `current_opening_hours_json`, `current_secondary_hours_json` | dòng mới | `$` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_rating` / `rating_overall`, `rating_count` | đổi | `poi_rating` → `$` | — | không đổi | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_amenity` / `amenity_schema_json`, `ext_attributes_json` | không đổi | `poi_amenity` → `$` | — | không đổi | `true` → `false` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_amenity` / thêm 23 cột boolean và 5 cột `*_options_json` | dòng mới | `$` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_review` / `review_id`, `author_name`, `text`, `time`, `published_at` | đổi | `poi_review` → `reviews` | — | không đổi | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_review` / `source` | không đổi | đổi (`reviews`) | — | không đổi | `true` → `false` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_review` / thêm 9 cột (`review_name` … `google_maps_uri`) | dòng mới | `reviews` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_media` / `media_dedup_key`, `photo_api_uri` | đổi | `poi_media` → `photos` | — | không đổi | không đổi |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_media` / `width_px`, `height_px` | đổi | đổi (`photos`) | — | không đổi | `false` → `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_media` / `media_id`, `media_type`, `blob_url`, `original_url`, `thumbnail_url`, `processing_status`, `category`, `is_blessed`, `display_order`, `photographer`, `license`, `file_size_bytes` | không đổi | đổi (`photos`) | — | không đổi | `true` → `false` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_media` / thêm `photo_pos`, `author_attributions_json`, `flag_content_uri`, `google_maps_uri` | dòng mới | `photos` | — | dòng mới | `true` |
| `ctrl_cfg_schema_registry` | `slv_3p_poi_policy` / `poi_id`, `policies_json` | không đổi | không đổi | — | không đổi | không đổi |
| `ctrl_mng_pipeline_config` | `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_rating`, `slv_3p_poi_amenity` | — | — | không đổi (`DOC`) | — | không đổi (`1`) |
| `ctrl_mng_pipeline_config` | `slv_3p_poi_review` | — | — | không đổi (`DOC_ARRAY`) | — | không đổi (`1`) |
| `ctrl_mng_pipeline_config` | `slv_3p_poi_media` | — | — | không đổi (`DOC_ARRAY`) | — | không đổi (`1`). Ngoài 5 trường: `dedup_order` `display_order ASC, media_id ASC` → `photo_pos ASC` vì hai cột cũ là `MISSING_EVIDENCE` |
| `ctrl_mng_pipeline_config` | `slv_3p_poi_policy` | — | — | không đổi (`DOC`) | — | giữ `0` |

## Khoá trong mẫu chưa có cột L1

- `id` → `slv_3p_poi` chỉ khi Q1 xác nhận khác `source_id`. Nếu bằng `source_id` thì không thêm cột.
- `primaryType` → `slv_3p_poi.primary_type`
- `primaryTypeDisplayName.text`, `primaryTypeDisplayName.languageCode` → `slv_3p_poi.primary_type_display_name`, `slv_3p_poi.primary_type_display_lang`
- `pureServiceAreaBusiness` → `slv_3p_poi.pure_service_area_business`
- `addressComponents` (cả mảng, gồm `longText`, `shortText`, `types`, `languageCode`) → `slv_3p_poi_address.address_components_json`
- `plusCode.compoundCode` → `slv_3p_poi_address.plus_compound_code`
- `utcOffsetMinutes` → `slv_3p_poi_address.utc_offset_minutes`
- `googleMapsLinks` (`directionsUri`, `placeUri`, `writeAReviewUri`, `reviewsUri`, `photosUri`) → `slv_3p_poi_contact.google_maps_links_json`
- `priceRange` → `slv_3p_poi_price.price_range_json`
- `currentOpeningHours` → `slv_3p_poi_opening_hours.current_opening_hours_json`
- `currentSecondaryOpeningHours` → `slv_3p_poi_opening_hours.current_secondary_hours_json`
- `servesBreakfast`, `servesBrunch`, `servesLunch`, `servesDinner`, `servesBeer`, `servesWine`, `servesCocktails`, `servesDessert`, `servesCoffee`, `servesVegetarianFood`, `allowsDogs`, `goodForChildren`, `goodForGroups`, `goodForWatchingSports`, `liveMusic`, `menuForChildren`, `outdoorSeating`, `restroom`, `reservable`, `takeout`, `delivery`, `dineIn`, `curbsidePickup` → `slv_3p_poi_amenity`, mỗi khoá 1 cột boolean snake_case
- `parkingOptions`, `paymentOptions`, `accessibilityOptions`, `evChargeOptions`, `fuelOptions` → `slv_3p_poi_amenity.*_options_json`
- `photos[].authorAttributions` → `slv_3p_poi_media.author_attributions_json`
- `photos[].flagContentUri`, `photos[].googleMapsUri` → `slv_3p_poi_media.flag_content_uri`, `slv_3p_poi_media.google_maps_uri`
- `reviews[].name` → `slv_3p_poi_review.review_name`
- `reviews[].relativePublishTimeDescription` → `slv_3p_poi_review.relative_publish_time_description`
- `reviews[].text.languageCode` → `slv_3p_poi_review.text_language_code`
- `reviews[].originalText.text`, `reviews[].originalText.languageCode` → `slv_3p_poi_review.original_text`, `slv_3p_poi_review.original_language_code`
- `reviews[].authorAttribution.uri`, `reviews[].authorAttribution.photoUri` → `slv_3p_poi_review.author_uri`, `slv_3p_poi_review.author_photo_uri`
- `reviews[].flagContentUri`, `reviews[].googleMapsUri` → `slv_3p_poi_review.flag_content_uri`, `slv_3p_poi_review.google_maps_uri`
- `editorialSummary` → chưa có chỗ chứa
- `generativeSummary` → chưa có chỗ chứa
- `reviewSummary` → chưa có chỗ chứa
- `routingSummaries` → chưa có chỗ chứa

## Quyết định đã chốt (2026-10-13)

- Q1: Giữ cột bronze `source_name`, `source_id`, `language_code`. `poi_id` vẫn là `HASH_MD5_UUID` của `source_name` và `source_id`. Ba cặp sample xác nhận `raw.id` bằng `normalized.source_id`. `poi_id` nằm trong object normalized là chuỗi khác, không dùng làm `source_id`.
- Q2: Mỗi ô `raw_payload` là đúng một JSON object. File raw mới tách thành ba section, mỗi section một object.
- Q3: Bảng DOC con dùng `src_object = $`. Khóa null MERGE đè dữ liệu cũ. Đây là đổi ngữ nghĩa so với extract hiện tại: khối normalized null thì dòng bảng con không được ghi.
- Q4: Cột không còn được extract thì gỡ khỏi registry và khỏi DDL trong `NB_CREATE_DDL`, theo kiểu tạo lần đầu. Không chuyển `is_active = false` để giữ cột cũ.
- Ảnh: lấy đủ ảnh trong `photos`, không cắt còn 5 ảnh như `normalized_payload`. `display_order` là chỉ số 1-based của toàn bộ mảng. `photo_api_uri` = `photos[].name`. `width_px` và `height_px` lấy từ `widthPx` và `heightPx` khi raw có số.
- Danh sách cột gỡ đã xác nhận: `slv_3p_poi.business_sector`, `slv_3p_poi.business_category`, `slv_3p_poi_address.district`, `slv_3p_poi_address.country`, `slv_3p_poi_address.short_address`, `slv_3p_poi_contact.phone`, `slv_3p_poi_contact.phone_raw`, `slv_3p_poi_address.address_viet_map`, `slv_3p_poi_address.vietmap_status`, `slv_3p_poi_address.timezone`, `slv_3p_poi.slug`, các cột slug hoặc partner đang tắt, `slv_3p_poi_policy`, và `poi_content`. Không thêm 23 cột boolean.
- Q16: Dòng bronze cũ có `raw_payload`. Init lại từ đầu vẫn chạy được. Không cần mốc version để né dòng thiếu payload.
- `open_now`: lấy `currentOpeningHours.openNow`. Khối current không có thì lấy `regularOpeningHours.openNow`.

Đoạn đề xuất phía trên ghi "tắt `is_active`" cho cột `MISSING_EVIDENCE` bị quyết định Q4 thay thế.

## Kiểm chứng cặp sample

Chi tiết khóa, kiểu và kết quả so sánh nằm ở `evidence/payload-pair-comparison.md`. Không có giá trị mẫu trong repository.

Output extract `raw_payload` cần khớp output extract `normalized_payload` ở những chỗ sample chứng minh được bằng đường dẫn hoặc rule cấu trúc. Job vẫn đọc registry (`src_object`, `json_path`, `convert_rule`). Không viết tên khóa Google trong notebook extract.

Khớp trực tiếp, giữ cột L1 hiện có:

- `poi_name` = `displayName`. `poi_name_normalized` = `LOWER_TRIM` của đường dẫn đó.
- `operating_status` = `LOWER_TRIM` của `businessStatus`.
- `types_json` và `subcategory_tags_json` = `types`.
- `full_address` = `formattedAddress`. `lat` = `location.latitude`. `lng` = `location.longitude`. `plus_code` = `plusCode.globalCode`.
- `website_url` = `websiteUri`. `google_maps_url` = `googleMapsUri`.
- `rating_overall` = `rating`. `rating_count` = `userRatingCount`.
- Review: `author_name`, `time`, `rating`, `text` lấy từ `reviews[]` như bảng so sánh. `review_id` giữ `HASH_SHA256` của `source_name`, `source_id`, `author_name`, `time`.
- Media: lấy đủ phần tử `photos`. `photo_api_uri` = `photos[].name`. `display_order` là chỉ số 1-based. `width_px` = `widthPx`. `height_px` = `heightPx`. Normalized cũ chỉ giữ 5 ảnh và để rộng, cao là null.

Rule cấu trúc cần khai báo trong registry hoặc `convert_rule` dùng lại, không viết nhánh trong notebook:

- Chọn một phần tử `addressComponents[]` theo `types` rồi lấy `longText` hoặc `shortText`. Sample khớp `house_number`, `street`, `ward`, `city`, `state_province`, `country_code`, `postal_code`.
- `periods` làm phẳng `open` và `close` (`day`, `hour`, `minute`) từ `regularOpeningHours`. `weekday_text` = `regularOpeningHours.weekdayDescriptions`. `open_now` lấy `currentOpeningHours.openNow`, không có thì `regularOpeningHours.openNow`.
- `price_level`: map enum `PRICE_LEVEL_*` sang int theo chỉ số Google. `CAST` int của chuỗi raw không ra số normalized.

Không tái tạo được bằng đường dẫn trên ba cặp này, nên theo Q4 gỡ khỏi DDL và registry chứ không tắt:

- `business_sector`, `business_category` (không bằng `primaryType` hay `primaryTypeDisplayName.text`).
- `district`, `country`, `short_address`.
- Chuỗi `phone` và `phone_raw` đúng định dạng. Chỉ chữ số khớp `nationalPhoneNumber` và `internationalPhoneNumber`.
- `address_viet_map`, `vietmap_status`, `timezone`, `slug` và các cột slug hoặc partner đang tắt, `policies`, `poi_content`.
- Không thêm 23 cột boolean. Normalized đang nhét một phần cờ vào `ext_attributes` dạng chuỗi. Bảng amenity hiện tại không được điền lại bằng json_path.

`src_object = $` theo Q3 vẫn áp cho bảng DOC con. Hệ quả đã được người dùng xác nhận: document thiếu giờ hoặc thiếu giá sẽ ghi NULL đè dòng cũ. Sample 1 và 2 có `poi_opening_hours` và `poi_price` null đúng khi raw null.

## Kết quả probe DEV (2026-10-13)

Nguồn: `evidence/results/P1` đến `P6`. DEV chỉ có `source_name = google`, 53 dòng, 17 `poi_id`. P2 đếm một số khóa cấp 1 hai lần vì probe cộng cả khóa top-level và đường dẫn lồng. Số thật của các khóa đó là một nửa.

Đạt, giữ cột:

- P1: `raw_payload` là string. `raw_blank`, `norm_blank`, `crawled_at_null`, `raw_id_ne_source_id` đều 0. 53 object JSON đúng một object.
- P2: `displayName` là string. Không có `displayName.text`. `priceLevel` là string hoặc null. `widthPx` và `heightPx` là integer. `userRatingCount` và `reviews[].rating` là integer. `rating` và tọa độ là number.
- P3 khớp toàn bộ 53 dòng: `poi_name`, `poi_name_normalized`, `types`, `subcategory_tags`, `operating_status`, `full_address`, `lat`, `lng`, `plus_code`, `website_url`, `google_maps_url`, `rating_overall`, `rating_count`, `weekday_text`, `state_province`, `country_code`, `house_number`, `street`, `postal_code`.
- `currency` khớp `priceRange.startPrice.currencyCode` trên 13 dòng có giá, 40 dòng cả hai null.
- `price_min` và `price_max` khớp nội dung sau khi đưa về chuỗi trên 13 dòng, 40 dòng cả hai null. Kiểu hai bên không giống hệt nhau.
- P4: 265 review, khóa review không đổi. `photos[].name` khớp `photo_api_uri` ở 5 ảnh đầu. Raw có 10 ảnh trên cả 53 dòng. Không thấy `name` null hay trùng trong document.
- P5: `PRICE_LEVEL_INEXPENSIVE` → 1 (6 dòng), `PRICE_LEVEL_MODERATE` → 2 (7 dòng), null → null (40 dòng). Không có token lạ. Period không thiếu `close`. Cả `keep_nulls` true và false đều khớp 53 dòng. Thứ tự khóa period trong normalized là `close_hour`, `close_day`, `open_hour`, `close_minute`, `open_minute`, `day_of_week`. `open_now` của current bằng regular trên 48 dòng. 5 dòng không có current và regular khớp normalized.

Không đạt điều kiện giữ nguyên:

- `city`: 20 dòng khớp `administrative_area_level_1`, 33 dòng khác và không trùng component nào. `state_province` mới là cột khớp `administrative_area_level_1` trên cả 53 dòng.
- `ward`: token `administrative_area_level_2` chỉ khớp 17 dòng. 36 dòng normalized có ward nhưng token này không chọn được. `longText` của ward còn trùng `locality` (33) và `neighborhood` (2). 3 dòng không trùng component nào.
- `address_line1`, `address_line2`: 53 dòng không trùng component. `is_24_7` và `is_temporarily_closed` không có đường dẫn raw. `secondary_hours` có giá trị ở 35 dòng nhưng không có cặp raw đã chứng minh.

P6 mới có danh sách consumer gold `PL_VV_TRANS_SLV_TO_ENR_15P`. Chưa có `SHOW TABLES` của `slv_poi*`, danh sách notebook L2, và schedule.

## Quyết định bổ sung (2026-10-13, tối)

Context nằm ở `evidence/context/`: hai sample payload, `ward_mapping_satnhap.txt`, `get_amenity.md`, `business_sector_rule.md`, `mapping_sector.md`.

- P6 đủ cho phạm vi này. `slv_poi*` không có trong DEV. Partner là `slv_pn*`. 3rd là `slv_3p*`. Không có notebook L2 `slv_poi_*` trong DEV.
- Gold và silver L2 không thuộc task này. Task này không sửa notebook gold, không ghi NULL vào gold, và không đụng `slv_pn_*`.
- `city`: `longText` của component có type đầu tiên là `administrative_area_level_1`. Người dùng chấp nhận đường dẫn này dù 33 dòng DEV không khớp `city` normalized cũ.
- `state_province`: cùng component đó. P3 khớp cả 53 dòng.
- `ward`: `longText` của component có type đầu tiên là `administrative_area_level_2`. Người dùng chọn token này dù chỉ khớp 17 dòng normalized cũ.
- Component có nhiều type: lấy type đầu tiên để chọn cột. Cột đích ưu tiên tên đang có ở normalized khi map được: `street_number` → `house_number`, `route` → `street`, `postal_code` → `postal_code`, `country` + `shortText` → `country_code`.
- Phần địa chỉ còn lại chỉ giữ số nhà và tên đường. Plus code, mã đường, tên quận hoặc tỉnh không đưa vào `address_line1` hoặc `address_line2`. Ba sample cho thấy hai cột này chứa số nhà và tên đường nhưng không bằng phép nối `longText` hay `shortText`. Extract không bịa chuỗi. L1 giữ `house_number` và `street`. Không điền `address_line1` và `address_line2`.
- `price_min` = `priceRange.startPrice.units`. `price_max` = `priceRange.endPrice.units`. `currency` = `priceRange.startPrice.currencyCode`. Ba sample có giá khớp sau khi đưa về chuỗi.
- `is_24_7` và `is_temporarily_closed`: ba sample không có khóa raw tương ứng. Không map. Không điền hai cột này.
- `secondary_hours_json`: không lưu `regularSecondaryOpeningHours`.
- Amenity L1 đã chốt: `slv_3p_poi_amenity.source_flags_json` dùng đúng hình JSON trong `evidence/context/amenity-l1-demo.md`. Thêm cột nguồn `slv_3p_poi.primary_type` từ `primaryType`. Không đổi snake_case và không lọc theo ngành ở L1.
- Người dùng duyệt architecture round 2 vào 2026-10-13. Round này chốt disposition cột và đối số rule theo quyết định đã ghi và kết quả P1–P6. Gold và silver L2 vẫn ngoài phạm vi.
- UA1 đã chốt ngày 2026-10-14: `PL_VV_TRANS_SLV_TO_ENR_15P` đã tắt và giữ tắt đến khi có task gold riêng. Task này không sửa notebook gold.
- `open_now` dùng `COALESCE` trên giá trị `currentOpeningHours.openNow` rồi `regularOpeningHours.openNow`. P2 không có object current nào thiếu `openNow`, nên COALESCE khớp quy tắc không có khối current thì lấy regular.
- `periods_json` dùng `keep_nulls = false` vì P5 không phân biệt được hai chế độ. Thứ tự khóa là `close_hour`, `close_day`, `open_hour`, `close_minute`, `open_minute`, `day_of_week`.
- `price_level` map `PRICE_LEVEL_FREE` 0, `INEXPENSIVE` 1, `MODERATE` 2, `EXPENSIVE` 3, `VERY_EXPENSIVE` 4. Token khác làm fail closed.

## Kết quả runtime DEV (2026-10-14)

Full reload `3b3804b5-e61a-4b75-aec8-d1cdc7885453` đọc 53 tài liệu, rejected 0, `cast_null` 0, chín bảng `SUCCESS`. Mỗi bảng `DOC` insert 17. Review insert 85. Media insert 530. Lần full thứ hai và lần incremental đều success. Lần incremental không có update mới.

`city_differ = 1`, `ward_differ = 3` trên grain 17 POI so với `bak_20261014_slv_3p_poi_address`. Đúng phần báo cáo đã chấp nhận: `city` lấy `administrative_area_level_1`, `ward` lấy `administrative_area_level_2`. Không phải lỗi cutover.

Watch `mapped_heads_missing` đếm nhầm khóa nằm trong `reviews` và `photos`. Dữ liệu đã ghi đủ. Code watch sửa sau lần chạy, không cần init lại.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | Giữ cột `_bad__` đến sau biểu thức `_cn__`, rồi select bỏ cột đó | |
| GATE-002 | P1 | fixed | `UPDATE` idempotent đặt `dedup_order = 'display_order ASC'` sau INSERT | |
| GATE-003 | P1 | fixed | Incremental dừng khi target thiếu hoặc rỗng mà `ctrl_cdc_state` còn dòng | |
| GATE-004 | P1 | fixed | Người dùng chấp nhận ngày 2026-10-14: fixture `proj_cn` đã thêm sau round 2, không review lại. Cùng ngày, người dùng chấp nhận đặt `specialist_review` và `risk_gate` thành `pass` vì hết lượt review | |
| GATE-005 | P1 | fixed | Fixture SQL dựng bằng nối chuỗi, không dùng quote lồng trong f-string | |

## Câu hỏi còn lại

`open_now` đã chốt: `currentOpeningHours.openNow`, không có khối current thì `regularOpeningHours.openNow`. Period và `weekday_text` vẫn lấy từ `regularOpeningHours`. Khóa `date` của current không ghi vào period đã làm phẳng.

Q16 đã chốt: dòng bronze cũ có `raw_payload`. Init lại từ đầu vẫn chạy được. Không cần mốc version để né dòng thiếu `raw_payload`.

## Câu hỏi

- Q1 `source_id` và `id`: mẫu chỉ có payload, không có cột bronze `source_name`, `source_id`, `language_code`, `crawled_at`, `event_id`. Bronze có còn điền đủ các cột này cho dòng đọc từ `raw_payload` không? Nếu còn, `poi_id` giữ `HASH_MD5_UUID` của `source_name`, `source_id`. Mẫu không chứng minh được `id` luôn bằng `source_id`. Nếu bronze không còn `source_id`, hoặc `id` khác `source_id`, người dùng cần quyết định nguồn của `source_id`. Đề xuất này không tự đặt công thức mới.
- Q2 Định dạng payload: file mẫu có 3 object. Dòng 1 chứa 2 object nối liền, không có dấu phân cách, cùng `id`. Dòng 2 chứa 1 object. Mỗi dòng bronze `raw_payload` là đúng 1 JSON object không? Nếu một ô chứa nhiều object nối liền thì luật phân loại số 3 sẽ trả `INVALID_PAYLOAD`.
- Q3 `src_object = $` cho các bảng DOC con: hiện tại khối vắng thì bảng không nhận tài liệu đó và giữ dữ liệu cũ. Với `$`, mọi tài liệu đều sinh dòng, khoá null sẽ ghi NULL đè giá trị cũ khi MERGE. Có chấp nhận đổi ngữ nghĩa này không, hay chọn một khoá neo cho từng bảng (vd `regularOpeningHours` cho `slv_3p_poi_opening_hours`)? Nếu dùng khoá neo, các cột ngoài khối đọc bằng `_root.<path>`, và tài liệu có khoá neo null sẽ không vào bảng dù có giờ phụ.
- Q4 Cột `MISSING_EVIDENCE` đang bật: đề xuất tắt (`is_active = false`) để giữ giá trị cũ. Hệ quả: consumer tiếp tục đọc giá trị cũ từ thời `normalized_payload` và không được cập nhật. Chọn tắt hay gỡ khỏi registry?
- Q5 `addressComponents`: đề xuất giữ cả mảng ở `address_components_json`. Lấy `ward`, `district`, `city`, `state_province`, `country`, `country_code`, `postal_code`, `house_number`, `street` cần chọn phần tử theo `types`, là rule và không làm ở L1. Có cần tách mảng thành bảng DOC_ARRAY riêng (khoá `poi_id` + vị trí) không? Bảng con chỉ upsert, nên vị trí cũ vẫn còn khi mảng ngắn lại. Các consumer `gld_enr_poi_coordinate.ward`, `district`, `province_name`, `destination_name` và `gld_enr_poi_info.district`, `destination_name`, `destination_context`, `short_address` mất nguồn mới cho tới khi có quyết định này.
- Q6 `business_sector`, `business_category` không có trong raw. `primaryType`, `types` là dữ liệu khác. Map sang sector hay category là rule của L2 (`ref_business_category`). Nguồn thay thế là gì? Ảnh hưởng `gld_enr_poi_info.business_sector`, `business_category`, `time_to_spend` và `slv_poi`.
- Q7 `review_id`: `authorAttribution.displayName` và `publishTime` có cùng chuỗi với `author_name`, `time` của `normalized_payload` không? Nếu khác, `review_id` của review cũ đổi giá trị, và review cũ bị nhân đôi ở `slv_3p_poi_review` (không có nhánh xoá) và `gld_enr_poi_review` (APPEND). `reviews[].name` là một định danh khác có trong mẫu, nhưng đề xuất này không đổi công thức.
- Q8 `media_dedup_key`: `photos[].name` có bằng `photo_api_uri` của `normalized_payload` không? Nếu khác, khoá media đổi và ảnh cũ bị nhân đôi.
- Q9 `priceLevel` chỉ null trong cả 3 object. Kiểu thật là gì? Hiện registry để `int`. Nếu nguồn trả chuỗi thì cast `int` sinh NULL, có thể gây `CastNullError`.
- Q10 `regularOpeningHours`, `currentOpeningHours` chỉ null trong mẫu. Cấu trúc con (`periods`, `weekdayDescriptions`, `openNow`) mới chỉ thấy trong các phần tử của `regularSecondaryOpeningHours[]` và `currentSecondaryOpeningHours[]`. Cần mẫu có giờ mở cửa chính. `open_now` nên đọc từ `currentOpeningHours.openNow` hay `regularOpeningHours.openNow`?
- Q11 `displayName` là string trong cả 3 object. Có trường hợp nào là object (`text`, `languageCode`) không? Nếu có, `poi_name` cần đường dẫn `displayName.text`.
- Q12 Các cờ chỉ null trong mẫu: kiểu boolean chưa có bằng chứng. Có cần mẫu có giá trị trước khi thêm cột không?
- Q13 Notebook node L2 `slv_poi` (N2) và `slv_poi_localization` (N4) chưa có trong repo. `slv_poi_address` (N3) không đọc được ở mức cột. Tên cột consumer ở các bảng này lấy từ `docs/context/01_DATA_MODEL.md` §6 và §7, chưa xác minh trên code.
- Q14 `editorialSummary`, `generativeSummary`, `reviewSummary`, `routingSummaries`: chưa có chỗ chứa vì `slv_3p_poi_content` đã bị gỡ. Có cần bảng hoặc cột không?
- Q15 `slv_3p_poi_policy`: raw không có `policies`. Giữ tắt hay gỡ khỏi registry và pipeline config?
- Q16 Dòng bronze cũ: các dòng crawl trước khi chuyển có `raw_payload` không? Nếu `full_reload` gặp `raw_payload` NULL thì tài liệu bị REJECTED `INVALID_PAYLOAD`. Có cần một mốc version để không đọc lại dòng cũ không?
