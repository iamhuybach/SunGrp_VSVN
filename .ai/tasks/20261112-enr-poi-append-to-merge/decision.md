# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-MERGE-1 | Hợp đồng MERGE đích | Lib có một MERGE bảng đích, `sql_merge_target`, khi `load_mode = RECOMPUTE` và `write_mode = MERGE`. Notebook gold srv gọi cùng lib. `sql_merge_edge_wm` là MERGE watermark, không phải kiểu ghi gold thứ hai. Không dừng để chọn kiểu MERGE. | Lịch sử quyết định, D-MERGE-1 | 2026-11-12 |
| D-RISK-1 | Phạm vi sau probe khóa | Sửa code MERGE cho cả hai bảng. Dòng thừa của `gld_enr_poi_review` là dữ liệu APPEND cũ. Để test đúng, xóa dữ liệu bảng đó và chạy init lại. Không xóa `gld_enr_poi_info`. Không bật cạnh review. Bước xóa và init nằm trong runbook Fabric DEV, không chạy trong task này. | Quyết định của người dùng, D-RISK-1 | 2026-11-12 |
| D-COL-1 | Hai cột kỹ thuật MERGE | Đồng ý, chấp nhận hai cột kỹ thuật. Thêm `row_hash` STRING và `deleted_at` TIMESTAMP vào `gld_enr_poi_info` và `gld_enr_poi_review`, đúng `TECH_COLUMNS` của MERGE hiện có. Không thêm cột nghiệp vụ. Không đổi grain. | Quyết định của người dùng, D-COL-1 | 2026-11-12 |
| D-SCOPE-1 | Ba test đuôi cell | Thêm `tests/test_gld_srv_poi_contract.py`, `tests/test_poi_entity_contract.py`, và `tests/test_srv_poi_serving_contract.py` vào scope. Chỉ dịch chỉ số cell đuôi của `NB_CREATE_DDL` để nhận cell `enrmerge`. | Architecture §0.1, người dùng nói tiếp tục xử lý | 2026-11-13 |
| D-SPARK-2 | Bỏ phần metrics còn thiếu | Người dùng cho qua spill và Capacity Metrics. Giữ bằng chứng đã có: DRY_RUN 53s, 8/72 core, job 270 shuffle 2,1 MiB. Không suy ra spill bằng 0. Tiếp tục bước `RUN`. | Quyết định của người dùng, D-SPARK-2 | 2026-11-14 |
| D-READY-1 | Sẵn sàng merge | Người dùng yêu cầu `ready_to_merge`. Không còn finding P0/P1 mở. Runtime đã pass. Hai gate review đóng theo quyết định này, không phải một verdict PASS mới của reviewer. | Quyết định của người dùng, D-READY-1 | 2026-11-14 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Probe `key-uniqueness` không cho biết 660 dòng thừa của `gld_enr_poi_review` nằm trên bao nhiêu `review_id`, và các dòng cùng khóa có cùng nội dung hay khác nhau. Không suy ra phân bố đó.

## Sai lệch so với kiến trúc

- STATE-001: `_refresh_lock()` nằm trong vòng `for` của `enrmergepy`, ngay trước từng `ALTER TABLE`, và vẫn có một lần ngay trước `UPDATE` `load_mode`. Ô kiến trúc chỉ refresh một lần trước cả vòng.
- SPARK-001: `finally` gọi `_release_lock`. Lỗi lúc nhả khoá không thay lỗi của thân cell. Ô kiến trúc gọi `spark.sql` trực tiếp trong `finally`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| DRAWIO-ENR-INFO | P3 | backlog | `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio` hộp `gld_enr_poi_info` vẫn ghi "40 cột". Hộp đã cũ so với 37 cột nghiệp vụ hiện tại và chưa có `row_hash`, `deleted_at`. Không sửa trong task này. | Cập nhật hộp khi có đợt sửa diagram. |
| STATE-001 | P1 | fixed | `enrmergepy` gọi `_refresh_lock()` ngay trước từng `ALTER`, rồi một lần nữa trước `UPDATE` config. `test_enr_merge_patch_cell_guards` khóa vị trí đó. | |
| SPARK-001 | P1 | fixed | `_release_lock` bọc lệnh nhả khoá. Test chạy cả lỗi thân cell và lỗi lúc nhả khoá. | |
| SQL-001 | P1 | fixed | `source-uniqueness.txt` 2026-11-14: entity, rating, price đều `null_key_count = 0` và `row_count = distinct_key_count`. Không thêm dedupe. | |
| SQL-002 | P1 | fixed | Cùng file: `slv_3p_poi_review.review_id` 109682 dòng, 0 null, 109682 khoá phân biệt. Không thêm dedupe. | |
| SPARK-002 | P1 | accepted-risk | Người dùng cho qua ngày 2026-11-14. Đã có DRY_RUN SUCCESS 53s, pool 8/72 core, job 270 0,2s, shuffle read/write 2,1 MiB. Chưa có spill và Capacity Metrics. Không ghi spill bằng 0. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

### D-SPARK-2 — 2026-11-14

Người dùng: "Có thể pass qua. Tiếp tục các step để chạy mode RUN."

Chấp nhận thiếu Spill (Memory), Spill (Disk) và Fabric Capacity Metrics. Không coi các số đó là 0. Bước runtime tiếp theo là `NB_ENR_POI_INFO` với `p_mode = RUN`.

### D-READY-1 — 2026-11-14

Người dùng: "Chuyển trạng thái ready_to_merge và commit."

`specialist_review` và `risk_gate` chuyển `pass` để máy nhận `ready_to_merge`. Review vòng 2 vẫn là `EVIDENCE_REQUIRED`; SPARK-002 vẫn `accepted-risk`. Không chạy thêm vòng review.

## Quyết định của người dùng

### D-RISK-1 — 2026-11-12

Sửa code MERGE cho cả hai bảng. Dòng thừa của `gld_enr_poi_review` là dữ liệu APPEND cũ. Để test đúng, xóa dữ liệu bảng đó và chạy init lại. Không xóa `gld_enr_poi_info`. Không bật cạnh review. Bước xóa và init nằm trong runbook Fabric DEV, không chạy trong task này.

Lần chọn trước, cùng ngày, là giữ nguyên dòng review và chấp nhận lần chạy sau không an toàn. Người dùng đổi quyết định đó: 660 dòng thừa là do APPEND cũ, không phải grain mới. `gld_enr_poi_info` vẫn đạt khóa (`row_count` 20829 = `distinct_key_count` 20829). `gld_enr_poi_review` vẫn không đạt trên dữ liệu hiện tại (`row_count` 110342, `distinct_key_count` 109682).

### D-COL-1 — 2026-11-12

Đồng ý, chấp nhận hai cột kỹ thuật.

Thêm `row_hash` STRING và `deleted_at` TIMESTAMP vào `gld_enr_poi_info` và `gld_enr_poi_review`, đúng `TECH_COLUMNS` của MERGE hiện có. Không thêm cột nghiệp vụ. Không đổi grain.

## Lịch sử quyết định

### D-MERGE-1 — 2026-11-12

Lib có một MERGE bảng đích, `sql_merge_target`, khi `load_mode = RECOMPUTE` và `write_mode = MERGE`. Notebook gold srv gọi cùng lib. `sql_merge_edge_wm` là MERGE watermark, không phải kiểu ghi gold thứ hai. Không dừng để chọn kiểu MERGE.

`NODE_WRITE_MODE` trong `NB_LIB_TRANSFORM_SLV_GLD` chỉ map `RECOMPUTE` → `MERGE` và `APPEND` → `APPEND`. Các notebook `NB_GLD_SRV_POI_*` dùng `%run NB_LIB_TRANSFORM_SLV_GLD` và `write_mode = MERGE`. Không có hàm MERGE đích thứ hai cho gold.

### D-RISK-1 — 2026-11-12

Sửa code MERGE cho cả hai bảng, giữ nguyên dòng review hiện có, và chấp nhận lần chạy review sau này không an toàn trên bảng đang trùng khóa.

Main ghi `accepted-risk` cho dữ liệu `gld_enr_poi_review` hiện có: 660 dòng vượt quá số `review_id` phân biệt. Phân bố các dòng đó không được đo. Task vẫn đổi đường ghi của cả hai bảng sang MERGE đang có. Cạnh review giữ `is_active = 0`. Runbook sau này không được yêu cầu chạy `NB_ENR_POI_REVIEW` trên bảng review hiện tại.

Cùng ngày, người dùng thay phần giữ dòng review: dòng thừa là APPEND cũ. Runbook sẽ xóa dữ liệu `gld_enr_poi_review` rồi chạy init lại trước khi test MERGE. Không xóa `gld_enr_poi_info`. Không chạy bước Fabric đó trong task này.

### D-COL-1 — 2026-11-12

Đồng ý, chấp nhận hai cột kỹ thuật.

Thêm `row_hash` STRING và `deleted_at` TIMESTAMP vào `gld_enr_poi_info` và `gld_enr_poi_review`, đúng `TECH_COLUMNS` của MERGE hiện có. Không thêm cột nghiệp vụ. Không đổi grain. Signal `data_model_change` được bật. `tests/test_initial_ddl_contract.py` vào `scope.files`.
