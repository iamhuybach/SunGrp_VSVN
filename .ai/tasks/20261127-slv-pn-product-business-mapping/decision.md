# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| Q-01 | Nguồn cột Field Mapping | Nhận `TABLE_CONFIGS` là nguồn cột. Cột thiếu so với data hoặc model cũ thì trace nguồn. Map được theo bảng và model mới thì map. | user 2026-11-27 | 2026-11-27 |
| Q-02 | Cột silver mà rule legacy dùng | Đã trace trong mapping. Cột không có trên silver thì không có dòng Field Mapping. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-03 | Kiểu giá đã giải mã hay chuỗi | `original_price`, `marketing_price`, `markup_percent` là `string`, 36/36 `base64_like`. L1 giữ chuỗi. NULL giữ NULL. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-04 | `deleted_at` và thời điểm nguồn | `deleted_at` là chuỗi `timestamp_text` hoặc null. `src_created_at` / `src_updated_at` chưa đọc vì timestamp năm 58774. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-05 | JSON `products.metadata` | Object 41/41. Khóa `holiday_product_post_id`, `main_attribute_code` trên 41 dòng. `start_date`, `end_date` trên 15 dòng. Không tách cột. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-06 | JSON `product_variants.attributes` | Object 212/212. Khóa dạng `holiday:*`. Không in value. Không tách cột. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-07 | JSON `product_posts.raw_sync_data` | Object 27, null 9. Có `translations`, `shortDescription`, `tags`. `languageCode` quan sát: `en-VN`, `ko-VN`, `vi-VN`. Không tách cột. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-08 | Khoá join bản dịch giá trị thuộc tính | `attribute_id` có trong `TABLE_CONFIGS`. L1 giữ 1-1. Không dựng lại join của notebook cũ. | TABLE_CONFIGS | 2026-11-27 |
| Q-09 | Cột hotel mà §1.6 dùng | Cột có trong `TABLE_CONFIGS`. Room type và rate plan đã có dòng. Mapping L1, không gộp thành một dòng product. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-10 | Bảng product còn rỗng sau 04/10 | Không còn rỗng. `DESCRIBE DETAIL.numRecords` trả `None`. Số dòng lấy từ group-by của probe. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-11 | Hotel có trong phạm vi mapping đã chốt | Extract thiếu thì ghi việc extract lại. Probe: hai bảng hotel đã có dòng và nằm trong mapping L1. Logic khác extract là Silver L2. Ba bảng, tên, và file mapping nằm ở Q-19. | user 2026-11-27; Q-19 | 2026-11-27 |
| Q-12 | Grain đích khác silver L1 | Giữ silver L1: một dòng nguồn, khoá `id`. Từ L1 mới xét Silver L2 hay Gold. | user 2026-11-27 | 2026-11-27 |
| Q-13 | `source_id` thô hay `poi_id` đã hash | Không thêm `source_id` trên silver L1. Khi nối product sang POI: `poi_id = uuid_md5(business_service_id, 'partner')`. | user 2026-11-27 | 2026-11-27 |
| Q-14 | `destination_id` khi bỏ `ai_poi` | Giữ destination ngoài mapping L1. Nếu map được theo `slv_enr_poi_destination` thông qua map product với POI, xử lý transform ở Gold. | user 2026-11-27 | 2026-11-27 |
| Q-15 | Giá NULL giữ NULL hay thành 0 | Giữ NULL. | user 2026-11-27 | 2026-11-27 |
| Q-16 | Xoá mềm: `deleted`, `deleted_at`, hay cả hai | Cờ xoá của extract là `deleted` khi `op = d`. `deleted_at` là cột nguồn, giữ nguyên giá trị. | user 2026-11-27 | 2026-11-27 |
| Q-17 | So khớp `status` có phân biệt hoa thường | L1 giữ chuỗi nguồn. Product và variant: `active`. Hotel: `Active`, `Inactive`, `Draft`, `Archived`. `slv_pn_product_posts.status` null 36/36. Không đổi hoa thường. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-18 | Locale tiếng Anh trên bảng translation | Có dòng `locale = en` trên các bảng translation. Tên tiếng Anh lấy từ dòng đó. Không sinh tên. | evidence/results/product_payload_shape.txt | 2026-11-27 |
| Q-19 | Ba bảng Silver L2 | Đồng ý tách theo khuyến nghị: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer`. `valid_from` và `valid_to` chỉ chuyển 1-1. Không suy cờ bán từ hai cột vì code cũ không dùng chúng. | user 2026-11-27 | 2026-11-27 |
| Q-20 | Phân loại trước gate kiến trúc | Thêm signal `data_model_change`. `architecture_required` = true. `gates.architecture` = pending. Ba bảng Q-19 thêm grain và khoá. Kiểu JSON nằm ở Q-24. Chat này không sửa notebook, DDL, pipeline. | user 2026-11-27 | 2026-11-27 |
| Q-21 | `deleted_at` của ba bảng L2 | A. Dòng L2 vẫn có cho mọi id đang nằm trên L1. Ghi `deleted_at` khi L1 `deleted = true` hoặc id không còn. Lần tính sau, nếu nguồn về `deleted = false`, `deleted_at` trở lại NULL. | user 2026-11-27 | 2026-11-27 |
| Q-22 | `is_bookable` của `slv_pn_product_sale` | A. Không có variant `status = active` và `deleted = false` thì `false`. `status` và `deleted` của product không đi vào cờ này. | user 2026-11-27 | 2026-11-27 |
| Q-23 | Cột trong `row_hash` | A. Gồm khoá và các cột nghiệp vụ phía trên dòng hash, đúng thứ tự Field Mapping. Công thức `sha2(to_json(struct(...)), 256)`. `row_hash`, `created_at`, `updated_at`, `deleted_at` ở ngoài struct. | user 2026-11-27 | 2026-11-27 |
| Q-24 | Kiểu `holiday_product_post_id` | Giá trị JSON là chuỗi. 41/41 lớp `string`. So sánh chuỗi với `external_id` của post `deleted = false`: 41/41 khớp đúng một post. Không có post, hoặc nhiều hơn một post, thì `product_post_id` và ba giá vẫn NULL. | evidence/results/holiday_product_post_id_type.txt | 2026-11-27 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Tên cột và kiểu ở Q-01 lấy từ `TABLE_CONFIGS` trong repo. Chưa đọc schema Delta trên Fabric.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Chưa có.

## Lịch sử quyết định

- 2026-11-27: `problem-analysis.md` mở đầu bằng `RESULT: EVIDENCE_REQUIRED`. Main không viết `docs/context/mapping_slv_pn_product.md`.
- 2026-11-27: Khối `TABLE_SPECS` không chứa `slv_pn_product*` hay `slv_pn_hotel*`. `TABLE_CONFIGS` trong cùng notebook khai báo đủ 13 bảng, đúng số cột ở `01_DATA_MODEL.md` §5.1, schema `lh_vv_silver.dbo`, khoá `id`. Đây là đối chiếu repository, chưa phải schema Delta đã chạy.
- 2026-11-27: Probe lần 1 in `slv_pn_products` = 41 rồi dừng với `SparkUpgradeException`, không parse được timestamp `58774-09-09 16:50:00.000000`. Chưa có shape JSON, giá, `deleted_at`, `locale`, `status`. Probe được sửa để chỉ đọc cột cần phân loại.
- 2026-11-27: Probe lần 2 đủ group-by. `numRecords` của `DESCRIBE DETAIL` là `None`. User chốt Q-01, Q-11, Q-12, Q-13, Q-15, Q-16. Q-14 giữ mở.
- 2026-11-27: Q-14 chốt. Destination ngoài mapping L1. Transform nối product–POI–`slv_enr_poi_destination` thuộc Gold, chưa viết trong tài liệu này.
- 2026-11-27: Khuyến nghị chưa chốt cho Q-11/Q-12: rule dùng chung ở Silver L2; hình dạng serving và destination ở Gold. Chưa tạo bảng.
- 2026-11-27: Tên L2 khuyến nghị, chưa chốt: `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer`.
- 2026-11-27: User đồng ý tách theo khuyến nghị. Q-19 chốt ba bảng. Mapping nằm ở `docs/context/mapping_slv_pn_product_l2.md`. Chưa sửa DDL.
- 2026-11-27: Bỏ `is_on_sale`. `valid_from` và `valid_to` chỉ 1-1. Code cũ không dùng hai cột để lọc.
- 2026-11-27: Q-11 lệch Q-19 ở hai câu "2 bảng mới" và "Tài liệu L2 chưa tạo vì chưa có tên bảng". Mapping L2 đã có ba bảng. Q-19 thắng. Sửa dòng Q-11 tại chỗ. Không đổi mapping.
- 2026-11-27: Phân loại lại trước gate kiến trúc. Signal thêm `data_model_change`. `architecture_required` = true. `gates.architecture` = pending. Evidence giữ pass. Chat này không sửa notebook, DDL, pipeline.
- 2026-11-27: `run-author --kind model` ghi `model-design.md`. Không chạy Architect. Conflict 4, 5, 6 là câu hỏi người dùng. Conflict 8 thiếu kiểu JSON của `holiday_product_post_id`. Probe: `evidence/probes/holiday_product_post_id_type.py`. `gates.evidence` = `evidence_required`.
- 2026-11-27: User chuyển task sang `ready_to_merge`. `gates.local_verification` = `not_required` vì diff là tài liệu mapping, không có thay đổi hành vi cần test.
- 2026-11-27: User chốt Q-21, Q-22, Q-23 theo lựa chọn A. Mapping L2 sửa cùng ba rule. Probe `holiday_product_post_id_type` lần 1 dừng với `SparkUpgradeException` tại timestamp `58774-09-09 16:50:00.000000`. Chưa có lớp kiểu JSON. Probe đặt `spark.sql.legacy.timeParserPolicy=LEGACY` trước khi đọc, và chỉ SELECT cột không phải timestamp.
- 2026-11-27: Probe lần 2. `holiday_product_post_id` là chuỗi JSON, 41/41. So sánh chuỗi với `external_id` của post `deleted = false` khớp đúng một post, 41/41. Q-24. `gates.evidence` = pass.
- 2026-11-27: Architect PASS, phương án B. Bốn mục mở, chưa thành dòng Q: (1) notebook node của ba bảng; (2) đăng ký `TABLE_SPECS` / `TABLE_CONFIGS` / `ctrl_cfg_schema_registry`; (3) cờ xoá của lib là điều kiện hiện thực Q-21; (4) `valid_from` / `valid_to` kế thừa câu hỏi 4 của L1 về đơn vị `EPOCH_S_TS`. Mapping L2 đã ghi `Cách tính` và ba dòng `deleted_at` / `updated_at`.
