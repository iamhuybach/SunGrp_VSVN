# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Tiền tố landing | Prefix `slv_enr_` chưa có trong §1 naming. Người dùng đã chốt tên bảng. Dùng `lh_vv_silver.dbo.slv_enr_*`. Không tạo schema mới. | request.md Constraints | 2026-10-22 |
| D-02 | Cột landing | Người yêu cầu gõ nhầm `descrption`; tên cột là `description`. Không thêm cột `lang` vào bảng review. `created_at` và `updated_at` cùng kiểu `TIMESTAMP` với `gld_enr_poi_info`, nullable vì không được khai `NOT NULL`. Không thêm `UNIQUE` hay khoá tổ hợp ngoài `NOT NULL` đã nêu. | request.md Acceptance criteria | 2026-10-22 |
| D-03 | Grain landing | Grain và khoá duy nhất của 3 bảng landing chưa được chốt. Cờ không phụ thuộc grain. Không tự chọn khoá. | request.md Constraints | 2026-10-22 |
| D-04 | Cờ gold | Cờ chỉ kiểm tra tồn tại khoá. Không chép nội dung enrich sang gold. `poi_id` hoặc `review_id` không khớp thì false. | request.md Acceptance criteria | 2026-10-22 |
| D-05 | Cột info bỏ | Bỏ `district` và `destination_name` khỏi hợp đồng và khỏi câu xử lý của `gld_enr_poi_info`. Giữ `street`, `ward`, `city`, `full_address`. | request.md Scope | 2026-10-22 |
| D-06 | Hợp đồng cột | Hợp đồng cột `gld_enr_poi_info` lấy từ cell patch hiện hành `enrinfopy` của `NB_CREATE_DDL` (`INFO_COLS` đang có `district`, `destination_name`). Không dùng `INFO_COLS` của cell `enrddlpy`. `REVIEW_COLS` chỉ còn ở cell `enrddlpy` vì chưa có patch sau thay nó. | request.md Acceptance criteria | 2026-10-22 |
| D-07 | NULL khi ALTER | Cột thêm vào bảng gold đã tồn tại phải nullable ở `ALTER`. Notebook ghi true hoặc false khi chạy. | request.md Acceptance criteria | 2026-10-22 |
| D-08 | Không nạp landing | Task này không viết notebook nạp dữ liệu vào 3 bảng landing. | request.md Scope | 2026-10-22 |
| D-09 | Test đuôi DDL | `tests/test_poi_entity_contract.py` `test_create_ddl_patch` khóa 4 cell cuối `NB_CREATE_DDL`. Architecture không nêu file này. Đổi assert thành 6 cell cuối `enrinfomd`, `enrinfopy`, `mvpoimd`, `mvpoipy`, `enrflagmd`, `enrflagpy`. Không đổi phần còn lại của test. | architecture.md Main brief Invariants | 2026-10-22 |
| D-10 | R7 | Không chạy R7. Người dùng chấp nhận rủi ro ngày 2026-10-22. Cờ false khi landing trống đã chứng minh trên DEV. Nhánh cờ true chưa chạy. | Người dùng, 2026-10-22 | 2026-10-22 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có notebook, test, SQL, hay JSON ngoài phạm vi task đọc `gld_enr_poi_info.district` hoặc `gld_enr_poi_info.destination_name`. `tests/test_enr_poi_contract.py` là contract của node: sửa list INFO và REVIEW, không sửa list COORD. `docs/context/gld_enr_poi_info_review.md` mô tả hai cột bị bỏ; không sửa file đó trong task này. `gld_enr_poi_coordinate` giữ `district` và `destination_name` của bảng đó.

## Sai lệch so với kiến trúc

- D-09: thêm `tests/test_poi_entity_contract.py` vào scope và sửa assert đuôi cell. Architecture không liệt kê file này. `pytest` đầy đủ không PASS nếu giữ assert cũ.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | accepted-risk | `DRY_RUN` info 89s và review 75s, `SUCCESS`, không có OOM trong log. Quy mô DEV: 65 dòng info, 455 dòng review. Ba count sau `DELETE` đều bằng 0. Spill, shuffle và peak memory không đo vì Spark UI đã đóng; người dùng chọn phương án này ngày 2026-10-22. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-22: chốt tên ba bảng `slv_enr_*`, schema `lh_vv_silver.dbo`, danh sách cột, hai cờ info, một cờ review, và cách vá DDL.

## Lịch sử quyết định

- 2026-10-22: D-01 đến D-08 chép từ yêu cầu đã chốt trong `request.md`. Main không chọn grain hay khoá duy nhất.
- 2026-10-22: `model-design.md` conflict 1 không chọn khoá; task nạp sau mới chọn. Conflict 4 không mở phương án giữ cột trên hợp đồng: D-05 bỏ `district` và `destination_name`; cell patch và runbook nói rõ cách bỏ, không `DROP COLUMN` im lặng. Conflict 2, 3, 6 để Architect. Conflict 5 và 8 không sửa trong task này.
- 2026-10-22: D-09. `pytest` đầy đủ fail ở `test_create_ddl_patch` vì cell mới nằm sau `mvpoipy`. Sửa assert đuôi cell. Không sửa cell cũ.
- 2026-10-22: Người dùng xác nhận Fabric DEV không có pipeline `PL_VV_TRANS_SLV_TO_ENR_15P` nên không tắt trigger. `lock_exec_id` của `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` là NULL. Bốn notebook đã đồng bộ. `p_pl_name` trong probe vẫn là chuỗi `pl_name` của ctrl, không phải pipeline Fabric.
- 2026-10-22: Kết quả một phần trong `evidence/results/spark-001-dry-run.txt`. Bước 4–6 đạt: bỏ `district` và `destination_name`; `enrflagpy` lần hai không tạo lại bảng; ba cạnh `is_active = 1`, `n = 1`. `DRY_RUN` info 89s và review 75s, `SUCCESS`, `trg_version` null. Quy mô đo được: 65 dòng info, 455 dòng review, mỗi landing 1 dòng probe.
- 2026-10-22: Người dùng xác nhận ba count sau `DELETE` đều bằng 0 và Spark UI đã đóng. `SPARK-001` ghi `accepted-risk`: thời gian và log đạt; spill không đo được.
- 2026-10-22: Review round 2 PASS. Runbook do author ghi. Main điền B4: live entity là `deleted_at IS NULL`; `slv_3p_poi_review` không có `deleted_at`, chỉ lọc `review_id IS NOT NULL`.
- 2026-10-22: V3 info 65/0/0/0 và review 285/0/0. V4 hai dòng SUCCESS, landing inbox `NEW_EDGE`, `enrich_flag_null` 0. Khóa null lúc 07:37:05Z, không có watermark cạnh. Lần chạy lại cả hai `SUCCESS`, inserted 0. R7 chưa chạy.
- 2026-10-22: D-10. Người dùng chọn `accepted-risk` cho R7 và yêu cầu đóng task.
