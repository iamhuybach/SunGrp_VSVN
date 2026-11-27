# Mapping SLV Partner Product — Silver L2

Ba bảng này chưa có trong `TABLE_SPECS` và `TABLE_CONFIGS`. Q-19 chốt tách theo khuyến nghị. Tài liệu này là hợp đồng mapping, chưa phải DDL. Lakehouse của cả ba bảng là `lh_vv_silver.dbo`. Nguồn chỉ là partner, nên prefix `slv_pn_`.

Cột kỹ thuật của silver L2, theo `docs/context/02_NAMING_CONVENTION.md`: `row_hash` string, `created_at` timestamp, `updated_at` timestamp, `deleted_at` timestamp. `deleted_at` ở đây là xoá mềm của dòng tính lại, khác `deleted_at` nguồn trên L1.

Không đưa vào ba bảng: `variants_json`, destination, `poi_id`, nhãn chữ của `meal_plan`, giá mặc định `0`.

## 1. Table: `slv_pn_product_sale`

Lakehouse.schema: `lh_vv_silver.dbo`

### 1.1. Xử lý

Một dòng cho mỗi `slv_pn_products.id`, kể cả product đã `deleted`. Khoá `product_id`.

Nối `metadata.holiday_product_post_id` với `slv_pn_product_posts.external_id` của post có `deleted = false`. Đúng một post thì ghi `product_post_id` và giải mã giá của post đó. Không có post, hoặc nhiều hơn một post, thì `product_post_id` và ba giá là NULL. Không chọn một post bất kỳ.

Giải mã theo `mapping_legacy_ai_product.md` §1.4, dừng trước bước ghi `0`: NULL giữ NULL (Q-15). `original_price` và `marketing_price` scale 4. `markup_percent` scale 2. Kiểu đích của rule cũ là `double`.

`is_bookable` = true khi có ít nhất một `slv_pn_product_variants` cùng `product_id`, `status = active`, `deleted = false`. So khớp đúng chữ `active`.

### 1.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_pn_products.id | string | 1-1, khoá | product_id |
| slv_pn_products.metadata.holiday_product_post_id, slv_pn_product_posts.external_id | string | Đúng một post `deleted = false` thì lấy `slv_pn_product_posts.id`. Ngược lại NULL | product_post_id |
| slv_pn_product_posts.original_price | string | Giải mã base64, scale 4, ra `double`. NULL hoặc lỗi giải mã thì NULL | original_price |
| slv_pn_product_posts.marketing_price | string | Giải mã base64, scale 4, ra `double`. NULL hoặc lỗi giải mã thì NULL | marketing_price |
| slv_pn_product_posts.markup_percent | string | Giải mã base64, scale 2, ra `double`. NULL hoặc lỗi giải mã thì NULL | markup_percent |
| slv_pn_product_variants.product_id, status, deleted | string, boolean | true khi có dòng `status = active` và `deleted = false` | is_bookable |
| các cột nghiệp vụ ở trên | — | `sha2` của struct các cột nghiệp vụ | row_hash |
| lần tính đầu | timestamp | Cột kỹ thuật L2 | created_at |
| lần tính khi hash đổi | timestamp | Cột kỹ thuật L2 | updated_at |
| product nguồn không còn | timestamp | Xoá mềm dòng L2 | deleted_at |

### 1.3. Giải mã giá

Thứ tự của §1.4: NULL hoặc boolean thành NULL. Số thì giữ. Chuỗi số thì parse. Còn lại thì base64, đọc integer big-endian có dấu, chia `10^scale`. Decode lỗi hoặc rỗng thành NULL. Không ghi `0` sau đó.

## 2. Table: `slv_pn_hotel_room_offer`

Lakehouse.schema: `lh_vv_silver.dbo`

### 2.1. Xử lý

Một dòng cho mỗi `slv_pn_hotel_room_types.id`. Khoá `room_type_id`. Không gắn rate plan. Không tạo giá.

`is_bookable` = true khi `status = Active`, `available_rooms` lớn hơn 0, và `deleted = false`. `available_rooms` NULL thì cờ false. So khớp đúng chữ `Active`.

### 2.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_pn_hotel_room_types.id | string | 1-1, khoá | room_type_id |
| slv_pn_hotel_room_types.status | string | 1-1 | status |
| slv_pn_hotel_room_types.available_rooms | int | 1-1 | available_rooms |
| slv_pn_hotel_room_types.max_occupancy | int | 1-1 | max_occupancy |
| slv_pn_hotel_room_types.adult_capacity | int | 1-1 | adult_capacity |
| slv_pn_hotel_room_types.child_capacity | int | 1-1 | child_capacity |
| slv_pn_hotel_room_types.view_type | string | 1-1 | view_type |
| slv_pn_hotel_room_types.deleted | boolean | 1-1 | deleted |
| status, available_rooms, deleted | string, int, boolean | true khi `Active`, `available_rooms` > 0, `deleted = false` | is_bookable |
| các cột nghiệp vụ ở trên | — | `sha2` của struct các cột nghiệp vụ | row_hash |
| lần tính đầu | timestamp | Cột kỹ thuật L2 | created_at |
| lần tính khi hash đổi | timestamp | Cột kỹ thuật L2 | updated_at |
| phòng nguồn không còn | timestamp | Xoá mềm dòng L2 | deleted_at |

## 3. Table: `slv_pn_hotel_rate_offer`

Lakehouse.schema: `lh_vv_silver.dbo`

### 3.1. Xử lý

Một dòng cho mỗi `slv_pn_hotel_rate_plans.id`. Khoá `rate_plan_id`. Không có `room_type_id`. `meal_plan` giữ số. Không thêm cột nhãn.

`valid_from` và `valid_to` chuyển 1-1, NULL giữ NULL. Cell 15 của notebook cũ chỉ `cast` hai cột sang string rồi ghi vào `variants_json`. Notebook đó không so hai cột với thời điểm hiện tại và không loại rate plan khi một cột NULL. Bảng này không có cờ còn bán suy từ hai cột.

### 3.2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_pn_hotel_rate_plans.id | string | 1-1, khoá | rate_plan_id |
| slv_pn_hotel_rate_plans.status | string | 1-1 | status |
| slv_pn_hotel_rate_plans.meal_plan | int | 1-1. Giữ số 0–4 | meal_plan |
| slv_pn_hotel_rate_plans.valid_from | timestamp | 1-1. NULL giữ NULL. Không suy cửa sổ bán | valid_from |
| slv_pn_hotel_rate_plans.valid_to | timestamp | 1-1. NULL giữ NULL. Không suy cửa sổ bán | valid_to |
| các cột nghiệp vụ ở trên | — | `sha2` của struct các cột nghiệp vụ | row_hash |
| lần tính đầu | timestamp | Cột kỹ thuật L2 | created_at |
| lần tính khi hash đổi | timestamp | Cột kỹ thuật L2 | updated_at |
| rate plan nguồn không còn | timestamp | Xoá mềm dòng L2 | deleted_at |

### 3.3. `meal_plan`

Số giữ nguyên. Notebook cũ gọi `0` Room only, `1` Breakfast, `2` Half board, `3` Full board, `4` All inclusive. Các nhãn này không có cột ở L2.

## Câu hỏi cần chốt

Không có.
