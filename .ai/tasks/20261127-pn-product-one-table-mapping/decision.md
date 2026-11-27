# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| U-01 | Lớp và tên bảng | Bảng ở Gold. Tên `lh_vv_gold.dbo.gld_srv_product_offer`. | user 2026-11-27 | 2026-11-27 |
| U-02 | Grain | Như mục 1.1: một dòng một `product_id`. Mỗi variant là một phần tử `{variant_id, name, status, attributes}` trong `variants_json`. | user 2026-11-27 | 2026-11-27 |
| U-03 | Hotel | Hotel cùng bảng. Holiday: grain `products.id`. Hotel: grain `hotel_room_types.id`, `product_type = hotel`. | user 2026-11-27 | 2026-11-27 |
| U-05 | Destination | Gold nối product sang POI bằng `poi_id = uuid_md5(business_service_id, 'partner')`, rồi tới `slv_enr_poi_destination`. | user 2026-11-27 | 2026-11-27 |
| U-07 | `valid_from` và `valid_to` | Nằm trong `variants_json` của rate plan, không suy cờ bán. Cột riêng chỉ hợp grain một dòng một rate plan. | user 2026-11-27 | 2026-11-27 |
| U-04 | Nhiều `business_service_id` | Ở bảng đích, product có hơn một `business_service_id` thì loại cả product. | user 2026-11-27; evidence/results/product_business_service_cardinality.txt | 2026-11-27 |
| U-06 | Giá | Không transform, giải mã được cho fail job để tìm cách giải mã khác khắc phục. | user 2026-11-27; evidence/results/product_price_shape.txt | 2026-11-27 |
| U-08 | Ba bảng Q-19 | Ba bảng Q-19 còn là nguồn. Bảng gold gom từ L1 và ba bảng đó. | user 2026-11-27 | 2026-11-27 |
| D-0 | Khoá khi id holiday trùng id hotel | P-1: `cross_collisions` 0, `dup_products` 0, `dup_rooms` 0. Khoá giữ `product_id`. | evidence/results/product_offer_blocking.txt | 2026-11-28 |
| D-1 | Chỗ fail job khi giải mã giá | Đồng ý khuyến nghị (c): sửa decoder của `slv_pn_product_sale` để lỗi giải mã fail job thay vì ghi NULL. Gold không giải mã và không đổi giá. Việc sửa L2 nằm ngoài task này. | user 2026-11-28; architecture.md §2 D-1 | 2026-11-28 |
| D-2 | `product_type` holiday | Đồng ý khuyến nghị: `'other'`. | user 2026-11-28; architecture.md §2 D-2 | 2026-11-28 |
| D-3 | Fallback `business_service_id` | Relation trước, post chỉ khi không có dòng relation `deleted = false`. U-04 đếm các dòng relation `deleted = false` trước fallback. Product không có id vẫn giữ dòng theo D-4. | user 2026-11-28 | 2026-11-28 |
| D-4 | Dòng thiếu POI hoặc destination | Chọn D-4. `poi_id` NULL vẫn giữ dòng. Có `poi_id` mà không có dòng destination thì giữ dòng, `destination_id` NULL. | user 2026-11-28 | 2026-11-28 |
| D-10 | Relation đã xoá | Đồng ý khuyến nghị: U-04 và bước «relation không có dòng» chỉ tính dòng `deleted = false`. | user 2026-11-28 | 2026-11-28 |
| D-5 | Dạng `destination_id` | Đồng ý khuyến nghị: copy nguyên chuỗi JSON array, cùng contract `gld_srv_poi_info.destination_id`. | user 2026-11-28; architecture.md §2 D-5 | 2026-11-28 |
| D-6 | `variants_json` holiday | Đồng ý khuyến nghị: `name` locale `vi`; `attributes` là JSON thô; bỏ variant `deleted = true`; product không có variant vẫn có dòng, `variants_json = []`. | user 2026-11-28; architecture.md §2 D-6 | 2026-11-28 |
| D-7 | `variants_json` hotel | Đồng ý khuyến nghị: khoá `meal_plan` (số), `kind`, `valid_from`, `valid_to` (ISO-8601 UTC), `include_tax`, `include_service_charge`. Phòng không có rate plan thì `[]`. | user 2026-11-28; architecture.md §2 D-7 | 2026-11-28 |
| D-8 | `is_active` và `is_bookable` | Đồng ý khuyến nghị: `is_active` chỉ là cờ kỹ thuật. `is_bookable` copy 1-1 từ L2, không thêm cửa. | user 2026-11-28; architecture.md §2 D-8 | 2026-11-28 |
| D-9 | Danh sách cột | Giữ nguyên, không bỏ cột nào: `name`, `lang`, `product_line`, `price_level`, `variant_count`, `active_variant_count`, `variant_tickets`, `variant_dates`, `variant_hotels`, `variant_age_groups`, `variant_room_types`, `variant_departures`, `variant_statuses`, `product_attributes`, `source_id`, `business_service_id`, `product_post_id`. | user 2026-11-28 | 2026-11-28 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Trên Fabric DEV 2026-11-28, holiday `(product_id, id)` với `deleted = false` và hotel `(business_service_id, rate_plan_id)` với `deleted_at IS NULL` không trùng. `anomaly_count` 0. `business_service_id` lấy từ `slv_pn_hotel_rate_plans`, không có trên `slv_pn_hotel_rate_offer`.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | rejected-false-positive | Probe sửa nối `offer.rate_plan_id = plan.id`. `anomaly_count` 0, bảng kết quả rỗng. Không thêm guard. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- U-01, U-02, U-03, U-05, U-07, U-08: user 2026-11-27, nguyên văn ở bảng trên.
- U-01 tên `lh_vv_gold.dbo.gld_srv_product_offer`: user 2026-11-27.
- U-04: ở bảng đích, product có hơn một `business_service_id` thì loại cả product.
- U-06: "Không transform, giải mã được cho fail job để tìm cách giải mã khác khắc phục."
- 2026-11-28: D-1, D-2, D-3, D-5, D-6, D-7, D-8 đồng ý khuyến nghị architecture §2. D-4: `poi_id` NULL vẫn giữ dòng; không có destination thì giữ dòng và `destination_id` NULL. D-9: giữ nguyên, không bỏ cột nào.

## Lịch sử quyết định

- 2026-11-27: user chốt lớp Gold, grain `variants_json`, hotel cùng bảng, destination theo `poi_id` rồi `slv_enr_poi_destination`, `valid_from`/`valid_to` trong `variants_json` của rate plan và không suy cờ bán, ba bảng Q-19 còn là nguồn.
- 2026-11-27: probe bronze không thấy `product_id` nào có hơn một `business_service_id`. Probe giá: post là base64, sale đã là số dương, markup có 4 số 0. Hotel không có cột giá.
- 2026-11-27: user chốt tên `lh_vv_gold.dbo.gld_srv_product_offer`. U-04 đổi thành loại cả product khi hơn một `business_service_id`. U-06 đổi thành không transform; giải mã không được thì fail job.
- 2026-11-28: P-1 không trùng id. P-2 41/41 `relation_1`. P-3 holiday matched 3 unmatched 5, hotel matched 32 unmatched 87. P-4 không có product thiếu variant hay thiếu locale `vi`. P-5: 3 phòng không có rate plan sống, tối đa 14 rate plan trên một `business_service_id`. User chốt D-1 đến D-9.
- 2026-11-28: user chọn D-4 thay cho việc loại product không có id. U-04 và fallback chỉ tính relation `deleted = false`.
- 2026-11-28: SQL-001 probe `anomaly_count` 0. Không sửa mapping.
