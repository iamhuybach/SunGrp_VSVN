# `gld_enr_poi_info` và `gld_enr_poi_review`

Hai bảng gold enrich POI. Cột và kiểu lấy từ `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`, và `NB_SETUP_INITIAL_DDL`. `docs/context/01_DATA_MODEL.md` không có hai bảng này.

## `gld_enr_poi_info`

| Mục | Giá trị |
|---|---|
| Schema | `lh_vv_gold.enr` |
| Grain | Một dòng một `poi_id` |
| Notebook | `NB_ENR_POI_INFO` |
| Nguồn đang dùng | `lh_vv_silver.dbo.slv_poi_entity_non_enrich` (spine, bắt buộc), `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns` |

`enrich_type` là nhóm trong tài liệu này, không phải cột Delta. Một cột có thể thuộc nhiều nhóm. Ô trống là cột không nằm trong ba rule.

| Cột                        | Kiểu              | Ý nghĩa                                                               | enrich_type                            |
| -------------------------- | ----------------- | --------------------------------------------------------------------- | -------------------------------------- |
| `poi_id`                   | `STRING NOT NULL` | Khóa một POI.                                                         | enrich description                     |
| `source_name`              | `STRING`          | Tên nguồn của POI, ví dụ `google` hoặc `partner`.                     |                                        |
| `source_id`                | `STRING`          | Id của POI ở hệ thống nguồn.                                          |                                        |
| `language_code`            | `STRING`          | Mã ngôn ngữ trên entity.                                              |                                        |
| `poi_name`                 | `STRING`          | Tên hiển thị của POI.                                                 | enrich description                     |
| `poi_name_normalized`      | `STRING`          | Tên POI đã chuẩn hóa.                                                 | enrich description                     |
| `types`                    | `STRING`          | JSON loại hình, lấy từ `types_json`.                                  | enrich description                     |
| `operating_status`         | `STRING`          | Trạng thái hoạt động.                                                 |                                        |
| `primary_type`             | `STRING`          | Loại hình chính.                                                      | enrich description                     |
| `website_url`              | `STRING`          | Website của POI.                                                      | enrich description                     |
| `house_number`             | `STRING`          | Số nhà.                                                               | enrich destination                     |
| `street`                   | `STRING`          | Tên đường.                                                            | enrich description, enrich destination |
| `ward`                     | `STRING`          | Phường hoặc xã.                                                       | enrich description, enrich destination |
| `district`                 | `STRING`          | Copy giá trị `ward`.                                                  |                                        |
| `city`                     | `STRING`          | Thành phố hoặc tỉnh.                                                  | enrich description, enrich destination |
| `destination_name`         | `STRING`          | Copy giá trị `city`.                                                  | enrich description                     |
| `full_address`             | `STRING`          | Địa chỉ đầy đủ.                                                       | enrich description, enrich destination |
| `lat`                      | `DOUBLE`          | Vĩ độ.                                                                | enrich destination                     |
| `lng`                      | `DOUBLE`          | Kinh độ.                                                              | enrich destination                     |
| `business_sector`          | `STRING`          | Mã nhóm ngành, dùng để chọn nhãn câu chữ.                             | enrich description                     |
| `business_category`        | `STRING`          | Nhóm danh mục.                                                        | enrich description                     |
| `business_category_vi`     | `STRING`          | Nhóm danh mục tiếng Việt.                                             |                                        |
| `category_group`           | `STRING`          | Nhóm category.                                                        | enrich description                     |
| `range_low_min`            | `INT`             | Cận dưới thời lượng, phút.                                            | enrich description                     |
| `range_high_min`           | `INT`             | Cận trên thời lượng, phút.                                            | enrich description                     |
| `avg_range_min`            | `INT`             | Thời lượng trung bình, phút.                                          | enrich description                     |
| `candidate_best_time_code` | `STRING`          | Mã thời điểm đẹp ứng viên.                                            | enrich description                     |
| `canonical_candidate`      | `STRING`          | Chuỗi thời điểm đẹp đã chốt.                                          | enrich description                     |
| `rating`                   | `DECIMAL(4,2)`    | Điểm rating tổng; chỉ điền khi nguồn là `google`.                     | enrich description                     |
| `user_rating_count`        | `BIGINT`          | Số lượt rating; chỉ điền khi nguồn là `google`.                       | enrich description                     |
| `price_level`              | `INT`             | Mức giá; chỉ điền khi nguồn là `google`.                              | enrich description                     |
| `opening_hours_text`       | `STRING`          | Giờ mở cửa: `periods_json` nếu `google`, giờ i18n `vi` nếu `partner`. | enrich description                     |
| `review_json`              | `STRING`          | JSON tối đa 20 review; chỉ `google`, không có thì `[]`.               | enrich description                     |
| `time_to_spend`            | `STRING`          | JSON một nhãn theo sector và câu thời lượng từ `avg_range_min`.       | enrich description, enrich multi-lang  |
| `best_time`                | `STRING`          | JSON một nhãn theo sector và câu mùa từ `canonical_candidate`.        | enrich description, enrich multi-lang  |
| `cost`                     | `BIGINT`          | Trung bình làm tròn của `price_min` và `price_max` khi đủ cả hai.     | enrich description                     |
| `cost_vnd`                 | `STRING`          | JSON câu giá VND theo sector; `cost` null thì chuỗi `null`.           | enrich description, enrich multi-lang  |
| `service_flag`             | `STRING`          | JSON mảng `service_flags` phân biệt, đã sort; không có thì `[]`.      | enrich description                     |
| `created_at`               | `TIMESTAMP`       | Mốc ghi batch; thư viện gán, không nằm trong `select`.                |                                        |
| `updated_at`               | `TIMESTAMP`       | Mốc ghi batch; thư viện gán, không nằm trong `select`.                |                                        |

## `gld_enr_poi_review`

| Mục | Giá trị |
|---|---|
| Schema | `lh_vv_gold.enr` |
| Grain | Một dòng một `review_id` |
| Notebook | `NB_ENR_POI_REVIEW` |
| Nguồn đang dùng | `lh_vv_silver.dbo.slv_3p_poi_review` (chỉ third-party) |

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `review_id` | `STRING NOT NULL` | Khóa một review. |
| `poi_id` | `STRING` | POI mà review thuộc về. |
| `rating` | `DECIMAL(3,1)` | Điểm review; giá trị không vừa kiểu thì notebook dừng. |
| `review_text` | `STRING` | Nội dung review, lấy từ cột `text`. |
| `review_date` | `TIMESTAMP` | Thời điểm review, parse UTC từ cột `time`. |
| `review_updated_at` | `TIMESTAMP` | Parse UTC từ cột `time`, cùng biểu thức với `review_date`. |
| `created_at` | `TIMESTAMP` | Mốc ghi batch; thư viện gán, không nằm trong `select`. |
| `updated_at` | `TIMESTAMP` | Mốc ghi batch; thư viện gán, không nằm trong `select`. |
