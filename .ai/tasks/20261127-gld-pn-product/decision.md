# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| Q-13 | `source_id` thô hay `poi_id` đã hash | Không thêm `source_id` trên silver L1. Khi nối product sang POI: `poi_id = uuid_md5(business_service_id, 'partner')`. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-13 | 2026-11-27 |
| Q-14 | `destination_id` khi bỏ `ai_poi` | Giữ destination ngoài mapping L1. Nếu map được theo `slv_enr_poi_destination` thông qua map product với POI, xử lý transform ở Gold. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-14 | 2026-11-27 |
| Q-15 | Giá NULL giữ NULL hay thành 0 | Giữ NULL. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-15 | 2026-11-27 |
| Q-19 | Ba bảng Silver L2 | Đồng ý tách theo khuyến nghị: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer`. `valid_from` và `valid_to` chỉ chuyển 1-1. Không suy cờ bán từ hai cột vì code cũ không dùng chúng. | 20261127-slv-pn-product-business-mapping `## Quyết định hiện hành` Q-19 | 2026-11-27 |
| D-A | Một bảng như model cũ | Mapping đã xong ở task `20261127-pn-product-one-table-mapping`, file `docs/context/mapping_gld_srv_product_offer.md`. Nhận nguyên văn các dòng U-01 đến D-9 bên dưới. Không mở rule mới. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` | 2026-11-28 |
| U-01 | Lớp và tên bảng | Bảng ở Gold. Tên `lh_vv_gold.dbo.gld_srv_product_offer`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-01 | 2026-11-27 |
| U-02 | Grain | Như mục 1.1: một dòng một `product_id`. Mỗi variant là một phần tử `{variant_id, name, status, attributes}` trong `variants_json`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-02 | 2026-11-27 |
| U-03 | Hotel | Hotel cùng bảng. Holiday: grain `products.id`. Hotel: grain `hotel_room_types.id`, `product_type = hotel`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-03 | 2026-11-27 |
| U-05 | Destination | Gold nối product sang POI bằng `poi_id = uuid_md5(business_service_id, 'partner')`, rồi tới `slv_enr_poi_destination`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-05 | 2026-11-27 |
| U-07 | `valid_from` và `valid_to` | Nằm trong `variants_json` của rate plan, không suy cờ bán. Cột riêng chỉ hợp grain một dòng một rate plan. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-07 | 2026-11-27 |
| U-04 | Nhiều `business_service_id` | Ở bảng đích, product có hơn một `business_service_id` thì loại cả product. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-04 | 2026-11-27 |
| U-06 | Giá | Không transform, giải mã được cho fail job để tìm cách giải mã khác khắc phục. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-06 | 2026-11-27 |
| U-08 | Ba bảng Q-19 | Ba bảng Q-19 còn là nguồn. Bảng gold gom từ L1 và ba bảng đó. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` U-08 | 2026-11-27 |
| D-0 | Khoá khi id holiday trùng id hotel | P-1: `cross_collisions` 0, `dup_products` 0, `dup_rooms` 0. Khoá giữ `product_id`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-0 | 2026-11-28 |
| D-1 | Chỗ fail job khi giải mã giá | Đồng ý khuyến nghị (c): sửa decoder của `slv_pn_product_sale` để lỗi giải mã fail job thay vì ghi NULL. Gold không giải mã và không đổi giá. Việc sửa L2 nằm ngoài task này. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-1 | 2026-11-28 |
| D-2 | `product_type` holiday | Đồng ý khuyến nghị: `'other'`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-2 | 2026-11-28 |
| D-3 | Fallback `business_service_id` | Relation trước, post chỉ khi không có dòng relation `deleted = false`. U-04 đếm các dòng relation `deleted = false` trước fallback. Product không có id vẫn giữ dòng theo D-4. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-3 | 2026-11-28 |
| D-4 | Dòng thiếu POI hoặc destination | Chọn D-4. `poi_id` NULL vẫn giữ dòng. Có `poi_id` mà không có dòng destination thì giữ dòng, `destination_id` NULL. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-4 | 2026-11-28 |
| D-10 | Relation đã xoá | Đồng ý khuyến nghị: U-04 và bước «relation không có dòng» chỉ tính dòng `deleted = false`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-10 | 2026-11-28 |
| D-5 | Dạng `destination_id` | Đồng ý khuyến nghị: copy nguyên chuỗi JSON array, cùng contract `gld_srv_poi_info.destination_id`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-5 | 2026-11-28 |
| D-6 | `variants_json` holiday | Đồng ý khuyến nghị: `name` locale `vi`; `attributes` là JSON thô; bỏ variant `deleted = true`; product không có variant vẫn có dòng, `variants_json = []`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-6 | 2026-11-28 |
| D-7 | `variants_json` hotel | Đồng ý khuyến nghị: khoá `meal_plan` (số), `kind`, `valid_from`, `valid_to` (ISO-8601 UTC), `include_tax`, `include_service_charge`. Phòng không có rate plan thì `[]`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-7 | 2026-11-28 |
| D-8 | `is_active` và `is_bookable` | Đồng ý khuyến nghị: `is_active` chỉ là cờ kỹ thuật. `is_bookable` copy 1-1 từ L2, không thêm cửa. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-8 | 2026-11-28 |
| D-9 | Danh sách cột | Giữ nguyên, không bỏ cột nào: `name`, `lang`, `product_line`, `price_level`, `variant_count`, `active_variant_count`, `variant_tickets`, `variant_dates`, `variant_hotels`, `variant_age_groups`, `variant_room_types`, `variant_departures`, `variant_statuses`, `product_attributes`, `source_id`, `business_service_id`, `product_post_id`. | 20261127-pn-product-one-table-mapping `## Quyết định hiện hành` D-9 | 2026-11-28 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- 2026-11-28: Notebook đặt `spark.sql.legacy.timeParserPolicy = LEGACY` trước khi đọc silver. Lần chạy `exec f66250d8-4c37-44ba-9b72-36b5ffc09bfa` FAILED vì Spark 3 không parse `58774-09-09 16:50:00.000000`. P-7 chỉ đọc được sau cùng cấu hình này. Không đổi giá trị timestamp và không đổi rule nghiệp vụ.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | fixed | Cạnh mới lấy `COALESCE(MAX(id), 0) + s.seq`. | |
| SQL-002 | P1 | fixed | `_require_unique` trên `product_id` ngay sau union, trước join destination. | |
| SQL-003 | P1 | fixed | P-7 chỉ lấy `poi_id` từ dòng holiday và hotel còn sống sau U-04. | |
| SPARK-001 | P1 | fixed | `held = True` ngay sau UPDATE chiếm khoá. Chỉ hạ `held` khi đọc owner thấy chủ khác. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-27: dùng nguyên văn Q-13, Q-14, Q-15, Q-19 của task `20261127-slv-pn-product-business-mapping`. Không mở quyết định mới.
- 2026-11-27: chốt gom thành một bảng như model cũ. Mapping viết lại ở task khác. Task này dừng cho đến khi mapping đó xong.
- 2026-11-28: nhận task `20261127-pn-product-one-table-mapping` và `docs/context/mapping_gld_srv_product_offer.md`. Các dòng U-01 đến D-9 chép nguyên văn. Không mở rule mới.
- 2026-11-28: đóng review vòng 2 bằng chứng đã ghi. P-7, V2–V7 và V6 `updated = 0`, `inserted = 0`.

## Lịch sử quyết định

- 2026-11-27: chép Q-13, Q-14, Q-15, Q-19 vào ledger task này từ `## Quyết định hiện hành` của task silver product. Q-01 đến Q-19 bên đó vẫn đóng.
- 2026-11-27: D-A. Câu của người dùng: gom thành một bảng như model cũ, viết lại mapping ở task mới, rồi quay lại task này. Chưa ghi cột, grain chi tiết, hay việc thay Q-19. Model cũ nằm ở `docs/context/mapping_legacy_ai_product.md`, bảng `ai_product`.
- 2026-11-28: D-A cập nhật. Nguồn nhận là `## Quyết định hiện hành` của `20261127-pn-product-one-table-mapping` và `docs/context/mapping_gld_srv_product_offer.md`. Q-19 giữ nguyên: ba bảng L2 vẫn là nguồn (U-08).
- 2026-11-28: `test_dest_portal_patch_cell` chờ `gldprdddlmd` và `gldprdddlpy` ngay sau `pnl2edgepy`, đúng thứ tự cell ở architecture §17.2. Không đổi rule nghiệp vụ.
- 2026-11-28: P-7 đạt. (a) mọi `n` = 0, gồm `destination`. (b) `sale` 41, `room_offer` 423. (c) mọi `deleted` = 0. (d) năm cạnh active trên `PL_VV_TRANS_SLV_TO_GLD_30M` cho ba bảng L2. Kiểu ba bảng L2 khớp `TYPES`. File `evidence/results/p7_gld_product_offer_readiness.txt`.
- 2026-11-28: Cell `gldprdddlpy` in `tạo lh_vv_gold.dbo.gld_srv_product_offer` và 15 cạnh active, cùng `PL_VV_TRANS_SLV_TO_GLD_30M`, `RECOMPUTE`, `NB_GLD_SRV_PRODUCT_OFFER`. Đủ 15 nguồn trong `INPUTS`.
- 2026-11-28: Lần chạy tay `exec f66250d8-4c37-44ba-9b72-36b5ffc09bfa` FAILED, phân loại `data`. Spark 3 không parse timestamp năm 58774. Cách đọc đã chứng minh ở P-7 là `timeParserPolicy = LEGACY`.
- 2026-11-28: `exec ff15ac6b-1e09-4ce4-9ad7-b958944a890f` SUCCESS, 84s, `trg_version` 1. Insert 464, update 0, xoá mềm 0, nguồn 464. 464 = 41 sale + 423 room offer của P-7. V3–V7 chưa có trong log.
- 2026-11-28: Script `v_gld_product_offer_checks` đạt V2, V3, V4, V7. `v5_dest_minus_gold` = 0. `v5_gold_minus_dest` = 92, bằng P-3 trong mapping §1.1: holiday 5 và hotel 87 không có dòng destination. D-4 giữ những dòng này với `destination_id` NULL. File `evidence/results/v_gld_product_offer_checks.txt`. V6 chưa chạy.
- 2026-11-28: V6. Người dùng xác nhận lần chạy lại `p_force = true` cho `updated = 0` và `inserted = 0`.
- 2026-11-28: Người dùng đóng review vòng 2 bằng chứng đã ghi. `specialist_review` = pass.
