# Mapping SLV Partner Product

Nguồn cột là `TABLE_CONFIGS` trong `notebooks/NB_SETUP_INITIAL_DDL.ipynb` (Q-01). `TABLE_SPECS` không có 13 bảng này. Grain silver L1: một dòng nguồn, khoá `id` (Q-12). Ghi bởi `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`. Lakehouse của mọi bảng dưới đây là `lh_vv_silver.dbo`.

Cột kỹ thuật do extract thêm, không nằm trong `TABLE_CONFIGS`: `deleted` boolean, `_source_db` string, `created_at` timestamp, `updated_at` timestamp (`NB_LIB_EXTRACT_RAWDATA`, `TECH_COLUMNS`). `deleted` = true khi `op = d` (Q-16). `deleted_at` là cột nguồn, giữ nguyên.

Probe `product_payload_shape` (2026-11-27): `DESCRIBE DETAIL.numRecords` trả `None`. Số dòng dưới đây là count của group-by. Không đọc `src_created_at`, `src_updated_at`, `validity_from`, `validity_to` vì timestamp năm 58774.

Không mang sang L1: một dòng product với `variants_json`, join `ai_poi` / `ai_enriched_poi`, remap `destination_id` cứng, cache dịch, và mọi bước LLM. Tên tiếng Anh lấy từ dòng `locale = en` đã có. Không sinh tên.

## Quyết định đã chốt

- Q-01: cột Field Mapping lấy từ `TABLE_CONFIGS`. Cột model cũ không có trên silver thì trace; map được thì map, không bịa cột.
- Q-12: grain L1, khoá `id`.
- Q-13: không có `source_id`. `poi_id = uuid_md5(business_service_id, 'partner')` chỉ khi nối sang POI.
- Q-15: giá NULL giữ NULL.
- Q-16: `deleted` là cờ extract. `deleted_at` giữ nguyên.
- Q-11: hai bảng hotel nằm trong tài liệu L1 này vì extract đã có dòng.
- Q-19: ba bảng Silver L2 được tách theo khuyến nghị. Chi tiết ở `docs/context/mapping_slv_pn_product_l2.md`. Chưa có trong DDL.
- Q-14: destination nằm ngoài mapping L1. Nếu map được product sang POI rồi sang `slv_enr_poi_destination`, transform đó thuộc Gold. Tài liệu này không ghi Field Mapping Gold.

## Câu hỏi cần chốt

1. **Mô tả product.** `slv_pn_product_translations` không có `description`. `short_description` nằm ở `slv_pn_product_post_translations`. `raw_sync_data` cũng có khóa `shortDescription`. Chưa chứng minh ba chỗ này là cùng một mô tả của `product_translations.description` cũ.
2. **Value của `attributes`.** Probe chỉ có khóa `holiday:*`, không có value. Chưa ghi value là `value_code`.
3. **Hai kiểu locale.** Bảng translation dùng `vi` / `en` / `ko`. `raw_sync_data.translations[0].languageCode` dùng `en-VN` / `ko-VN` / `vi-VN`. L1 không chuẩn hoá hai kiểu này.
4. **`src_created_at` / `src_updated_at`.** Khai báo `timestamp`, rule `EPOCH_S_TS`. Probe không đọc được vì giá trị năm 58774. Chưa kết luận đơn vị epoch trên dữ liệu đang chạy.

## 1. Table: `slv_pn_products`

Lakehouse.schema: `lh_vv_silver.dbo`

### 1.1. Xử lý

Một dòng nguồn, khoá `id`. Probe: `metadata` là object trên 41 dòng. `status` = `active` trên 41 dòng. `deleted_at`: null 31, `timestamp_text` 10.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| products.id | string | 1-1 | id |
| products.external_id | string | 1-1 | external_id |
| products.product_line | string | 1-1 | product_line |
| products.status | string | 1-1. Quan sát `active` 41/41. Không đổi hoa thường | status |
| products.attributes | string | 1-1. Chưa probe shape | attributes |
| products.metadata | string | 1-1 JSON. Không tách cột. Xem 1.3 | metadata |
| products.raw_sync_data | string | 1-1. Chưa probe shape | raw_sync_data |
| products.created_at | timestamp | `EPOCH_S_TS` → `src_created_at`. Chưa đọc được giá trị đang chạy | src_created_at |
| products.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at`. Chưa đọc được giá trị đang chạy | src_updated_at |
| products.deleted_at | string | 1-1. Quan sát null 31, `timestamp_text` 10. Không suy epoch. Không dùng làm cờ xoá | deleted_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

### 1.3. `metadata`

Khóa quan sát, không thành cột riêng: `holiday_product_post_id` và `main_attribute_code` trên 41 dòng. `start_date` và `end_date` trên 15 dòng. Join cũ `holiday_product_post_id` = `product_posts.external_id` không thực hiện ở L1.

## 2. Table: `slv_pn_product_translations`

Lakehouse.schema: `lh_vv_silver.dbo`

### 2.1. Xử lý

Một dòng nguồn, khoá `id` (bigint). Nhiều locale là nhiều dòng. Probe `locale`: `vi` 41, `ko` 28, `en` 25. Tên tiếng Anh là `name` của dòng `locale = en`. Không có cột `description`.

### 2.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_translations.id | bigint | 1-1 | id |
| product_translations.product_id | string | 1-1 | product_id |
| product_translations.locale | string | 1-1. Giá trị quan sát `vi`, `ko`, `en` | locale |
| product_translations.name | string | 1-1. Dòng `en` là tên tiếng Anh đã có trên nguồn | name |
| product_translations.metadata | string | 1-1. Chưa probe shape | metadata |
| product_translations.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_translations.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 3. Table: `slv_pn_product_attributes`

Lakehouse.schema: `lh_vv_silver.dbo`

### 3.1. Xử lý

Một dòng nguồn, khoá `id`. Chưa có probe đếm bảng này. Bản dịch nằm ở bảng 4.

### 3.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_attributes.id | string | 1-1 | id |
| product_attributes.external_id | string | 1-1 | external_id |
| product_attributes.code | string | 1-1 | code |
| product_attributes.status | string | 1-1 | status |
| product_attributes.product_category_scope | string | 1-1 | product_category_scope |
| product_attributes.raw_sync_data | string | 1-1 | raw_sync_data |
| product_attributes.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_attributes.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 4. Table: `slv_pn_product_attribute_translations`

Lakehouse.schema: `lh_vv_silver.dbo`

### 4.1. Xử lý

Một dòng nguồn, khoá `id` (bigint). Probe `locale`: `vi` 16, `ko` 13, `en` 11.

### 4.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_attribute_translations.id | bigint | 1-1 | id |
| product_attribute_translations.attribute_id | string | 1-1 | attribute_id |
| product_attribute_translations.locale | string | 1-1. Giá trị quan sát `vi`, `ko`, `en` | locale |
| product_attribute_translations.name | string | 1-1. Dòng `en` là tên tiếng Anh đã có | name |
| product_attribute_translations.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_attribute_translations.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 5. Table: `slv_pn_product_attribute_values`

Lakehouse.schema: `lh_vv_silver.dbo`

### 5.1. Xử lý

Một dòng nguồn, khoá `id`. Chưa có probe đếm bảng này. Cột mã là `code`.

### 5.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_attribute_values.id | string | 1-1 | id |
| product_attribute_values.attribute_id | string | 1-1 | attribute_id |
| product_attribute_values.external_id | string | 1-1 | external_id |
| product_attribute_values.code | string | 1-1 | code |
| product_attribute_values.raw_sync_data | string | 1-1 | raw_sync_data |
| product_attribute_values.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_attribute_values.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 6. Table: `slv_pn_product_attribute_value_translations`

Lakehouse.schema: `lh_vv_silver.dbo`

### 6.1. Xử lý

Một dòng nguồn, khoá `id` (bigint). Bốn cột nghiệp vụ. Probe `locale`: `vi` 58, `ko` 43, `en` 38. `attribute_id` giữ 1-1, không dựng lại join của notebook cũ.

### 6.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_attribute_value_translations.id | bigint | 1-1 | id |
| product_attribute_value_translations.attribute_id | string | 1-1 | attribute_id |
| product_attribute_value_translations.locale | string | 1-1. Giá trị quan sát `vi`, `ko`, `en` | locale |
| product_attribute_value_translations.name | string | 1-1. Dòng `en` là tên tiếng Anh đã có | name |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 7. Table: `slv_pn_product_variants`

Lakehouse.schema: `lh_vv_silver.dbo`

### 7.1. Xử lý

Một dòng nguồn, khoá `id`. Probe: `attributes` là object trên 212 dòng. `status` = `active` trên 212 dòng. `deleted_at`: null 136, `timestamp_text` 76. Không gộp variant vào một dòng product.

### 7.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_variants.id | string | 1-1 | id |
| product_variants.product_id | string | 1-1 | product_id |
| product_variants.status | string | 1-1. Quan sát `active` 212/212 | status |
| product_variants.external_id | string | 1-1 | external_id |
| product_variants.attributes | string | 1-1 JSON. Không tách cột. Xem 7.3 | attributes |
| product_variants.raw_sync_data | string | 1-1. Chưa probe shape | raw_sync_data |
| product_variants.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_variants.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| product_variants.deleted_at | string | 1-1. Quan sát null 136, `timestamp_text` 76. Không dùng làm cờ xoá | deleted_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

### 7.3. `attributes`

Khóa quan sát là mã `holiday:*`, ví dụ `holiday:age_group`, `holiday:use_date`, `holiday:restaurant`. Mỗi dòng có một tập khóa. Value không được in. Không tạo cột axis hay `variants_json`.

## 8. Table: `slv_pn_product_variant_translations`

Lakehouse.schema: `lh_vv_silver.dbo`

### 8.1. Xử lý

Một dòng nguồn, khoá `id` (bigint). Probe `locale`: `vi` 212, `ko` 136, `en` 102.

### 8.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_variant_translations.id | bigint | 1-1 | id |
| product_variant_translations.variant_id | string | 1-1 | variant_id |
| product_variant_translations.locale | string | 1-1. Giá trị quan sát `vi`, `ko`, `en` | locale |
| product_variant_translations.name | string | 1-1. Dòng `en` là tên tiếng Anh đã có | name |
| product_variant_translations.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_variant_translations.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 9. Table: `slv_pn_product_business_service_relation`

Lakehouse.schema: `lh_vv_silver.dbo`

### 9.1. Xử lý

Một dòng nguồn, khoá `id` (bigint). Chưa có probe đếm. Một product nhiều `business_service_id` thì giữ nhiều dòng. Không có cột `source_id`. `poi_id` không lưu ở bảng này. Công thức khi nối POI: `uuid_md5(business_service_id, 'partner')`. Nối tiếp sang `slv_enr_poi_destination` là transform Gold (Q-14), không có cột destination ở L1.

### 9.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_business_service_relation.id | bigint | 1-1 | id |
| product_business_service_relation.product_id | string | 1-1 | product_id |
| product_business_service_relation.business_service_id | string | 1-1. Không hash ở L1 | business_service_id |
| product_business_service_relation.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_business_service_relation.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 10. Table: `slv_pn_product_posts`

Lakehouse.schema: `lh_vv_silver.dbo`

### 10.1. Xử lý

Một dòng nguồn, khoá `id`. Probe trên cột được chọn: `raw_sync_data` object 27 và null 9. `status` null 36. `deleted_at` null 29 và `timestamp_text` 7. Ba cột giá đều `base64_like` 36/36.

### 10.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_posts.id | string | 1-1 | id |
| product_posts.business_service_id | string | 1-1. Không hash ở L1 | business_service_id |
| product_posts.created_by | string | 1-1 | created_by |
| product_posts.updated_by | string | 1-1 | updated_by |
| product_posts.post_code | string | 1-1 | post_code |
| product_posts.external_id | string | 1-1. Khóa JSON `holiday_product_post_id` không join ở L1 | external_id |
| product_posts.status | string | 1-1. Quan sát null 36/36 | status |
| product_posts.original_price | string | Giữ chuỗi base64. NULL giữ NULL. Quan sát `base64_like` 36/36. Không có cột decimal | original_price |
| product_posts.markup_percent | string | Giữ chuỗi base64. NULL giữ NULL. Quan sát `base64_like` 36/36 | markup_percent |
| product_posts.marketing_price | string | Giữ chuỗi base64. NULL giữ NULL. Quan sát `base64_like` 36/36 | marketing_price |
| product_posts.thumbnail_url | string | 1-1 | thumbnail_url |
| product_posts.gallery | string | 1-1 | gallery |
| product_posts.product_list | string | 1-1 | product_list |
| product_posts.raw_sync_data | string | 1-1 JSON. Không tách cột. Xem 10.3 | raw_sync_data |
| product_posts.validity_from | timestamp | 1-1. Probe không đọc cột timestamp này | validity_from |
| product_posts.validity_to | timestamp | 1-1. Probe không đọc cột timestamp này | validity_to |
| product_posts.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_posts.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| product_posts.deleted_at | string | 1-1. Quan sát null 29, `timestamp_text` 7. Không dùng làm cờ xoá | deleted_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

### 10.3. `raw_sync_data`

27 dòng là object. Khóa gồm `translations`, `shortDescription`, `tags`, `originalPrice`, `salePrice`, và các khóa nội dung khác. 22 dòng có `translations[0].languageCode` và `shortDescription`. 5 dòng trong số đó có thêm `tags[0].label` và `tags[0].code`. `languageCode` quan sát: `en-VN` 16, `ko-VN` 7, `vi-VN` 4. 9 dòng null. Không tách các khóa này thành cột.

## 11. Table: `slv_pn_product_post_translations`

Lakehouse.schema: `lh_vv_silver.dbo`

### 11.1. Xử lý

Một dòng nguồn, khoá `id` (bigint). Probe `locale`: `vi` 18, `en` 3, `ko` 1. `short_description` là cột riêng, không lấy từ LLM.

### 11.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| product_post_translations.id | bigint | 1-1 | id |
| product_post_translations.product_post_id | string | 1-1 | product_post_id |
| product_post_translations.locale | string | 1-1. Giá trị quan sát `vi`, `en`, `ko` | locale |
| product_post_translations.title | string | 1-1. Dòng `en` là title tiếng Anh đã có | title |
| product_post_translations.short_description | string | 1-1 | short_description |
| product_post_translations.tags | string | 1-1 | tags |
| product_post_translations.filter_tags | string | 1-1 | filter_tags |
| product_post_translations.ai_tags | string | 1-1 | ai_tags |
| product_post_translations.faqs | string | 1-1 | faqs |
| product_post_translations.sections | string | 1-1 | sections |
| product_post_translations.meta_title | string | 1-1 | meta_title |
| product_post_translations.meta_description | string | 1-1 | meta_description |
| product_post_translations.slug | string | 1-1 | slug |
| product_post_translations.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| product_post_translations.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 12. Table: `slv_pn_hotel_room_types`

Lakehouse.schema: `lh_vv_silver.dbo`

### 12.1. Xử lý

Một dòng nguồn, khoá `id`. Extract đã có dòng. Probe `status`: `Active` 374, `Inactive` 38, `Draft` 10, `Archived` 1. Không gộp một phòng thành một dòng product. Không có probe cho `available_rooms` hay `view_type`.

### 12.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| hotel_room_types.id | string | 1-1 | id |
| hotel_room_types.code | string | 1-1 | code |
| hotel_room_types.name | string | 1-1 | name |
| hotel_room_types.description | string | 1-1 | description |
| hotel_room_types.status | string | 1-1. Quan sát `Active`, `Inactive`, `Draft`, `Archived`. Không đổi hoa thường | status |
| hotel_room_types.max_occupancy | int | 1-1 | max_occupancy |
| hotel_room_types.adult_capacity | int | 1-1 | adult_capacity |
| hotel_room_types.child_capacity | int | 1-1 | child_capacity |
| hotel_room_types.max_extra_bed | int | 1-1 | max_extra_bed |
| hotel_room_types.max_child_surcharge | int | 1-1 | max_child_surcharge |
| hotel_room_types.room_size | int | 1-1 | room_size |
| hotel_room_types.view_type | string | 1-1 | view_type |
| hotel_room_types.total_physical_rooms | int | 1-1 | total_physical_rooms |
| hotel_room_types.total_pseudo_rooms | int | 1-1 | total_pseudo_rooms |
| hotel_room_types.out_of_service_count | int | 1-1 | out_of_service_count |
| hotel_room_types.out_of_order_count | int | 1-1 | out_of_order_count |
| hotel_room_types.total_rooms | int | 1-1 | total_rooms |
| hotel_room_types.available_rooms | int | 1-1. Không tính `is_bookable` ở L1 | available_rooms |
| hotel_room_types.amenities | string | 1-1 | amenities |
| hotel_room_types.media_files | string | 1-1 | media_files |
| hotel_room_types.tags | string | 1-1 | tags |
| hotel_room_types.business_service_id | string | 1-1. Không hash ở L1 | business_service_id |
| hotel_room_types.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| hotel_room_types.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| hotel_room_types.deleted_at | string | 1-1. Không dùng làm cờ xoá | deleted_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

## 13. Table: `slv_pn_hotel_rate_plans`

Lakehouse.schema: `lh_vv_silver.dbo`

### 13.1. Xử lý

Một dòng nguồn, khoá `id`. Extract đã có dòng. Probe `status`: `Active` 199, `Draft` 16, `Inactive` 14. `meal_plan` là int: `0` 172, `1` 44, `4` 6, `3` 4, `2` 3. Không dựng `variants_json` từ rate plan.

### 13.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| hotel_rate_plans.id | string | 1-1 | id |
| hotel_rate_plans.business_service_id | string | 1-1. Không hash ở L1 | business_service_id |
| hotel_rate_plans.code | string | 1-1 | code |
| hotel_rate_plans.name | string | 1-1 | name |
| hotel_rate_plans.description | string | 1-1 | description |
| hotel_rate_plans.status | string | 1-1. Quan sát `Active`, `Draft`, `Inactive` | status |
| hotel_rate_plans.kind | string | 1-1 | kind |
| hotel_rate_plans.meal_plan | int | 1-1. Giữ số. Không ghi nhãn chữ. Xem 13.3 | meal_plan |
| hotel_rate_plans.include_tax | boolean | 1-1 | include_tax |
| hotel_rate_plans.include_service_charge | boolean | 1-1 | include_service_charge |
| hotel_rate_plans.is_derived | boolean | 1-1 | is_derived |
| hotel_rate_plans.valid_from | timestamp | 1-1. Probe không đọc cột timestamp này | valid_from |
| hotel_rate_plans.valid_to | timestamp | 1-1. Probe không đọc cột timestamp này | valid_to |
| hotel_rate_plans.is_visible_on_website | boolean | 1-1 | is_visible_on_website |
| hotel_rate_plans.tags | string | 1-1 | tags |
| hotel_rate_plans.cancellation_policies | string | 1-1 | cancellation_policies |
| hotel_rate_plans.created_at | timestamp | `EPOCH_S_TS` → `src_created_at` | src_created_at |
| hotel_rate_plans.updated_at | timestamp | `EPOCH_S_TS` → `src_updated_at` | src_updated_at |
| hotel_rate_plans.deleted_at | string | 1-1. Không dùng làm cờ xoá | deleted_at |
| op = d | boolean | true khi `op = d`. Cột kỹ thuật | deleted |
| source.db | string | 1-1. Cột kỹ thuật | _source_db |
| lần INSERT đầu | timestamp | Cột kỹ thuật extract | created_at |
| lần MERGE | timestamp | Cột kỹ thuật extract | updated_at |

### 13.3. `meal_plan`

L1 lưu int. Notebook cũ gắn nhãn `0` Room only, `1` Breakfast, `2` Half board, `3` Full board, `4` All inclusive. Nhãn đó không ghi thành cột ở L1. Số quan sát nằm trong 0–4.
