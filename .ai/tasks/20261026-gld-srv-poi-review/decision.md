# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | rating_count | Kiểu Long như source hiện tại | user 2026-10-26 | 2026-10-26 |
| D-02 | rating | Kết quả là decimal(4,2) | user 2026-10-27 | 2026-10-27 |
| D-03 | scope.files | approve | user 2026-10-27 | 2026-10-27 |
| D-04 | runtime load | Nguồn gld_srv_poi_review chưa có nên job lỗi. Hiện tại tôi chỉ cần khung bảng và khung transform. Khi có data, nếu chạy có vấn đề gì sẽ coi là task khác. | user 2026-10-27 | 2026-10-27 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Rollout kiến trúc yêu cầu `DRY_RUN` rồi `RUN` ghi gold. DEV dừng ở `QualityGateError` vì `slv_enr_poi_review_multi_lang` có 0 dòng. D-04 nhận khung bảng và khung transform. Không sửa node để cho phép đầu vào rỗng. Lần chạy khi đã có dòng enrich thuộc task khác.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SQL-001 | P1 | fixed | Probe `sql-001` trên Fabric DEV không trả dòng. Tiêu chí pass là 0 dòng. `evidence/results/sql-001.txt` | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Kiểu Long như source hiện tại
- Kết quả là decimal(4,2)
- approve
- Nguồn gld_srv_poi_review chưa có nên job lỗi. Hiện tại tôi chỉ cần khung bảng và khung transform. Khi có data, nếu chạy có vấn đề gì sẽ coi là task khác.

## Lịch sử quyết định

- 2026-10-26: triage đọc `TABLE_CONFIGS_3P` cell `init_cfg_3p`. `rating_count` type là `bigint`. Mapping mục 2 ghi `integer`.
- 2026-10-26: user chọn D-01: "Kiểu Long như source hiện tại". Cột gold `rating_count` là `bigint` (Spark Long), cùng kiểu registry, không cast sang `integer`.
- 2026-10-27: Architect vòng 1 trả `EVIDENCE_REQUIRED`. G1: model phải thêm `row_hash` STRING và `deleted_at` TIMESTAMP vì `RECOMPUTE` đi qua MERGE của lib. G2: kiểu `rating` còn chờ user. P1–P3 không chặn thiết kế.
- 2026-10-27: user chọn D-02: "Kết quả là decimal(4,2)". Cột gold `rating` là `DECIMAL(4,2)`, cùng kiểu registry `slv_3p_poi_review.rating`, không cast sang `string`. Mapping §2 ghi `string` không còn là kiểu cột.
- 2026-10-27: Architect vòng 2 `PASS`. Dừng trước khi sửa code: patch cuối `NB_CREATE_DDL` làm fail assert thứ tự cell ở 3 file test ngoài `scope.files`. Chờ user cho thêm 3 file đó vào scope.
- 2026-10-27: user chọn D-03: "approve". Thêm `tests/test_gld_srv_poi_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py` vào `scope.files`.
- 2026-10-27: user chạy probe `sql-001`: "Đã chạy, không có data". Ghi `evidence/results/sql-001.txt`. `SQL-001` là `fixed`.
- 2026-10-27: user chạy runtime. `srvrevpy` lần 1 thêm `lang`, `title` và tạo gold; lần 2 không thêm gì. P3 khớp `decimal(4,2)` và `bigint`. P4 là WRITE Append, không có positional INSERT. Node `DRY_RUN` và `RUN` đều `QualityGateError` vì enrich có 0 dòng. User chọn D-04.
