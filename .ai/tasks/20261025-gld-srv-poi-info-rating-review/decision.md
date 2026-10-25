# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Grain `slv_3p_poi_rating` | Fabric DEV 2026-10-26: 345 dòng, distinct_poi_id 345, null_poi_id_rows 0, duplicate_poi_id_groups 0. Cột đo được: poi_id string, rating_overall decimal(4,2), rating_count bigint. Grain hiện tại một dòng mỗi poi_id; left join 1-1 được dùng. Lệch grain sau này thì không chọn dòng. | evidence/results/rating_grain.txt | 2026-10-26 |
| D-02 | `review_count` | `review_count` là count số lượng review theo `poi_id`: `COUNT(*)` nhóm theo `poi_id`, cast `INT`. Không dùng `COUNT(DISTINCT review_id)`. Dòng `review_id` NULL vẫn đếm. Không có dòng thì NULL sau left join. | request.md User outcome | 2026-10-26 |
| D-03 | Cast integer | `rating_count` và `review_count` là integer (`INT`). Transform 1-1 từ `bigint` hoặc từ count. Giá trị ngoài miền `INT` làm node dừng. Không ghi NULL thay giá trị và không đổi cột thành `bigint`. | request.md User outcome | 2026-10-26 |
| D-04 | NULL partner | Dòng partner, sau lower/trim như notebook, để NULL ở cả ba cột. Mọi dòng không khớp rating hoặc review cũng NULL và vẫn giữ `poi_id`. | request.md User outcome | 2026-10-26 |
| D-05 | Nguồn mô tả cột | Cột mới ghi ở mapping §1.2, DDL, `OUT_COLS`, contract test và registry input. Không sửa `docs/context/01_DATA_MODEL.md` trong task này. | request.md Acceptance criteria | 2026-10-26 |
| D-06 | Scope test | Có thêm ba file này vào scope.files: tests/test_initial_ddl_contract.py, tests/test_enr_poi_contract.py, tests/test_poi_entity_contract.py | Main brief, Order and stop points, stop 1 | 2026-10-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Snapshot Fabric DEV 2026-10-26. Delta không có UNIQUE. Lệch grain về sau vẫn dừng, không tự chọn dòng.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-26: Có thêm ba file này vào scope.files: tests/test_initial_ddl_contract.py, tests/test_enr_poi_contract.py, tests/test_poi_entity_contract.py

## Lịch sử quyết định

- 2026-10-25: Triage. `01_DATA_MODEL.md` §5.2 và registry trong hai notebook DDL khai báo `slv_3p_poi_rating` là DOC, khóa `poi_id`, `rating_overall` decimal(4,2), `rating_count` bigint. Không có UNIQUE và không có số đo. `slv_3p_poi_review` là DOC_ARRAY theo `review_id`. Evidence grain rating là bắt buộc trước model-design và architecture.
- 2026-10-26: Probe `rating_grain` đạt. 345 dòng, 345 `poi_id`, 0 null, 0 nhóm trùng. D-01 chuyển sang cho phép left join 1-1 trên snapshot này.
- 2026-10-26: D-02 đến D-05 chốt các câu hỏi model-design theo câu chữ request: `COUNT(*)` theo `poi_id`, cast `INT` và node dừng khi tràn, partner NULL tường minh, không sửa `01_DATA_MODEL.md`.
- 2026-10-26: Người dùng chấp nhận stop 1. D-06 thêm ba file test vào `scope.files`.
