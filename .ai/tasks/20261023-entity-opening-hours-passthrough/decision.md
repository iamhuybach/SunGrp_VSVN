# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-OH-01 | Vị trí cột silver | `opening_hours_text` là cột build cuối của `slv_poi_entity_non_enrich`, sau `canonical_candidate` và trước `row_hash`, trong `OUT_COLS` và `TABLE_SPECS`. `ALTER` thêm cột nullable; bảng đã có nhận cột ở cuối. Khớp theo tên cột. | Lịch sử D-OH-01 | 2026-10-23 |
| D-OH-02 | Nguồn partner | Giờ partner lấy `amentities` của `slv_pn_business_service_i18ns`, không lấy `slv_pn_business_services.amentities`. Cột i18n đi vào build bằng alias riêng. | Lịch sử D-OH-02 | 2026-10-23 |
| D-OH-03 | Grain giờ Google | Registry khóa `slv_3p_poi_opening_hours` là `poi_id`. Giữ left join theo `poi_id` như `NB_ENR_POI_INFO` cell 3. Không thêm quality gate dừng khi trùng `poi_id`. | Lịch sử D-OH-03 | 2026-10-23 |
| D-OH-04 | Kiểu periods_json | Registry khai báo `periods_json` kiểu `string`. Cột silver và gold là `STRING`. Không thêm cast mới. | Lịch sử D-OH-04 | 2026-10-23 |
| D-OH-05 | Kiểm tra gold | Gold có block check `opening_hours_text_mismatch`: giá trị gold khác `slv_poi_entity_non_enrich.opening_hours_text` của cùng `poi_id`, kể cả một bên null. | Lịch sử D-OH-05 | 2026-10-23 |
| D-OH-06 | Tiêu đề cell gold | Dòng `[SỬA 23/10]` của `NB_ENR_POI_INFO` cell 3 không chứa token mà `test_info_hours_passthrough` cấm. Ý nghĩa giữ nguyên: `opening_hours_text` lấy từ `slv_poi_entity_non_enrich`. | Lịch sử D-OH-06 | 2026-10-23 |
| D-OH-07 | Chấp nhận risk review | Người dùng chấp nhận risk `STATE-001`, `SQL-001` và `SQL-002` ngày 2026-10-23. Không chạy vòng review 3. Runbook tắt trigger `PL_VV_TRANS_SLV_TO_ENR_15P` trước `ohpasspy` và bật lại sau lần chạy orchestrator thứ hai. | Lịch sử D-OH-07 | 2026-10-23 |
| D-OH-08 | Runtime tạm dừng | Runtime của task này tạm dừng vì `phone`, `email` và `holiday_exceptions` nằm ở task `20261023-entity-phone-email-holiday`. Giữ status `waiting_runtime`. Không chạy `ohpasspy`, không gọi `run-gate`, không sửa D-OH-01 đến D-OH-07. | Lịch sử D-OH-08 | 2026-10-23 |
| D-OH-09 | ohpasspy đã chạy | `ohpasspy` đã chạy trên DEV ngày 2026-10-23: entity version 2 là `ADD COLUMNS` `opening_hours_text`. Người dùng chấp nhận risk không chạy lại orchestrator vì không có data mới. Giữ status `waiting_runtime`. `gates.runtime` giữ `pending`. Không gọi `run-gate`. Không sửa D-OH-01 đến D-OH-07. | Lịch sử D-OH-09 | 2026-10-23 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- `ohpasspy`: pre-check cạnh giờ tới gold chỉ nhận đúng một dòng có `is_active` 0 hoặc 1 (SQL-001). `nb_name` escape `'` thành `''` trước MERGE (SQL-002). E4 chưa có hai điều này.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| STATE-002 | P1 | fixed | Vòng 2 xác nhận. Cạnh giờ tới gold phải có đúng 1 dòng trước khi ghi, và còn `is_active = 0` sau khi ghi. | |
| STATE-001 | P1 | accepted-risk | Người dùng chấp nhận 2026-10-23. Lease 35 phút vẫn chiếm được nếu `ALTER` hoặc `MERGE` chạy lâu hơn lease. Runbook tắt trigger trước `ohpasspy`. | |
| SQL-001 | P1 | accepted-risk | Người dùng chấp nhận 2026-10-23. Code đã chặn `is_active` null trước khi ghi. Vòng 3 không chạy. | |
| SQL-002 | P1 | accepted-risk | Người dùng chấp nhận 2026-10-23. Code đã escape `'` trong `nb_name`. Vòng 3 không chạy. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-23: chấp nhận risk `STATE-001`, `SQL-001`, `SQL-002`. Không duyệt vòng review 3.

## Lịch sử quyết định

### D-OH-01

`opening_hours_text` là cột build cuối của `slv_poi_entity_non_enrich`, sau `canonical_candidate` và trước `row_hash`, trong `OUT_COLS` và `TABLE_SPECS`. `ALTER` thêm cột nullable; bảng đã có nhận cột ở cuối. Khớp theo tên cột.

`model-design.md` câu 1 không có vị trí cột. Tiêu chí nghiệm thu chỉ khóa vị trí trên gold. `02_NAMING_CONVENTION.md` §2.1 mục 7 yêu cầu `TABLE_SPECS` đúng thứ tự cột `ensure_target` (cột build rồi `TECH_COLUMNS`). Đặt cột mới ở cuối danh sách build không đổi thứ tự cột cũ.

### D-OH-02

Giờ partner lấy `amentities` của `slv_pn_business_service_i18ns`, không lấy `slv_pn_business_services.amentities`. Cột i18n đi vào build bằng alias riêng.

`_partner_hours` đọc `ctx.input("i18n")`. Trong `_partner`, `amentities` sau join là cột của `slv_pn_business_services`. Alias riêng giữ đúng công thức D-17.

### D-OH-03

Registry khóa `slv_3p_poi_opening_hours` là `poi_id`. Giữ left join theo `poi_id` như `NB_ENR_POI_INFO` cell 3. Không thêm quality gate dừng khi trùng `poi_id`.

`NB_CREATE_DDL` cell 14: `"target_table": "slv_3p_poi_opening_hours"`, `"key": "poi_id"`. Gold cell 3 gán `oh = ctx.input("hours")` và left join, không có check trùng. Không bịa gate mới.

### D-OH-04

Registry khai báo `periods_json` kiểu `string`. Cột silver và gold là `STRING`. Không thêm cast mới.

`NB_CREATE_DDL` cell 14: `"periods_json": {"path": "regularOpeningHours.periods", "type": "string", ...}`. `get_json_object` của nhánh partner cũng trả chuỗi.

### D-OH-05

Gold có block check `opening_hours_text_mismatch`: giá trị gold khác `slv_poi_entity_non_enrich.opening_hours_text` của cùng `poi_id`, kể cả một bên null.

Tiêu chí nghiệm thu: gold bằng đúng cột silver. So sánh phải coi null bằng null. Lệch giá trị là sai hợp đồng, nên là block check. Hai check công thức giờ (`opening_hours_other_source`, `partner_opening_hours_null`) chuyển sang notebook silver như `model-design.md`.

### D-OH-07

Người dùng chấp nhận risk `STATE-001`, `SQL-001` và `SQL-002` ngày 2026-10-23. Không chạy vòng review 3. Runbook tắt trigger `PL_VV_TRANS_SLV_TO_ENR_15P` trước `ohpasspy` và bật lại sau lần chạy orchestrator thứ hai.

Cổng `specialist_review` đóng sau quyết định này. Reviewer không trả `PASS`. Ba finding không còn trong `open_findings`. Sửa `is_active` và escape `nb_name` trong `ohpasspy` giữ nguyên.

### STATE-001 còn mở

Vòng 2 giữ `STATE-001`: lease 35 phút vẫn có thể bị lấy sau khi `ALTER` hoặc `MERGE` chạy lâu hơn lease. Cell vẫn dùng lease của E4 và `_refresh_lock` trước mỗi lần ghi. Không đổi sang khoá không thể chiếm. Cần người dùng duyệt vòng review thêm, hoặc chấp nhận chạy `ohpasspy` khi trigger `PL_VV_TRANS_SLV_TO_ENR_15P` đang tắt.

### D-OH-06

Dòng `[SỬA 23/10]` của `NB_ENR_POI_INFO` cell 3 không chứa token mà `test_info_hours_passthrough` cấm. Ý nghĩa giữ nguyên: `opening_hours_text` lấy từ `slv_poi_entity_non_enrich`.

`### E2` ghi tiêu đề có `_partner_hours` và `slv_3p_poi_opening_hours`. `### E6` cấm đúng các token đó trong cả cell. Giữ E6 để test chứng minh cell gold không còn công thức giờ.

### D-OH-08

Runtime của task này tạm dừng vì `phone`, `email` và `holiday_exceptions` nằm ở task `20261023-entity-phone-email-holiday`. Giữ status `waiting_runtime`. Không chạy `ohpasspy`, không gọi `run-gate`, không sửa D-OH-01 đến D-OH-07.

Runbook của task giờ không được chạy. Runbook của task ba cột sẽ gồm `ohpasspy` chưa áp trên DEV và patch cột mới.

### D-OH-09

`ohpasspy` đã chạy trên DEV ngày 2026-10-23: entity version 2 là `ADD COLUMNS` `opening_hours_text`. Người dùng chấp nhận risk không chạy lại orchestrator vì không có data mới. Giữ status `waiting_runtime`. `gates.runtime` giữ `pending`. Không gọi `run-gate`. Không sửa D-OH-01 đến D-OH-07.

Chứng cứ nằm ở task `20261023-entity-phone-email-holiday`, D-PEH-09. Version 2 lúc 2026-10-23T09:59:45Z. Giá trị giờ trên silver chưa được MERGE. Không chạy runbook của task này.
