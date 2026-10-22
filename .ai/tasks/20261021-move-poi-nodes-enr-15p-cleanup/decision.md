# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Probe | INV-1 = 24 và INV-2 có 24 dòng. INV-3 = 23 và INV-4 có 23 dòng. Không câu nào chạm 50 dòng. INV-5 đến INV-8 đều trả một số đếm. Mọi `lock_exec_id` và `lock_at` đều null. | evidence/results/ctrl-inventory.txt | 2026-10-21 |
| D-02 | Pipeline hai node | Trên DEV, 3 cạnh `slv_poi_amenity` và 6 cạnh `slv_poi_entity_non_enrich` đã có `pl_name = PL_VV_TRANS_SLV_TO_ENR_15P`, `is_active = 1`. Không có dòng ctrl nào thuộc `PL_VV_TRANS_SLV_TO_SLV_1H`. Seed repo vẫn gán 9 cạnh đó cho `PL_VV_TRANS_SLV_TO_SLV_1H`. Repo phải đổi theo DEV. Patch DEV không được nhân đôi cạnh đã ở ENR. | evidence/results/ctrl-inventory.txt INV-2; notebooks/NB_SETUP_INITIAL_DDL.ipynb cell `init_seed_ctrl` | 2026-10-21 |
| D-03 | Cạnh và watermark xóa | Xóa 3 cạnh `gld_enr_poi_coordinate` (`is_active = 0`), 3 cạnh info cũ từ `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` (`is_active = 0`), và 2 cạnh `slv_pn_poi` (`is_active = 1`). Xóa 3 watermark coordinate, 2 watermark `slv_pn_poi`, và `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` (`status = NO_DATA`, `flow_name = NB_SLV_POI_ENTITY`). Ba cạnh info cũ không có watermark. Giữ 7 watermark info đang active, 9 watermark của hai node, và `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`. | evidence/results/ctrl-inventory.txt INV-2, INV-4 | 2026-10-21 |
| D-04 | DROP | DROP trên Fabric DEV: `lh_vv_gold.enr.gld_enr_poi_coordinate` (94 dòng) và `lh_vv_silver.dbo.slv_pn_poi` (30 dòng). Giữ `slv_poi_amenity` (58 dòng) và `slv_poi_entity_non_enrich` (65 dòng). Không đổi grain hay cột của hai bảng giữ. | evidence/results/ctrl-inventory.txt INV-5 đến INV-8; request.md User outcome | 2026-10-21 |
| D-05 | Model | `model-design.md` là hợp đồng model. Không có `proposal.md` vì task không đi lane proposal. `NB_SETUP_INITIAL_DDL` cell `init_tables` không có `target_table` cho hai bảng bị xóa. Câu hỏi 4 và 5 trong model không chặn DROP: cột coordinate nằm ở cell `init_tables`; cột business của `slv_pn_poi` nằm ở `NB_SLV_PN_POI` cell `379af200`. `architecture.md` hiện là template, chưa phải output của Architect. | model-design.md Conflicts and questions; notebooks/NB_SETUP_INITIAL_DDL.ipynb cell `init_tables` | 2026-10-21 |
| D-06 | Rollback DROP | The user drops the two tables from the runbook after a CTAS backup to `lh_vv_silver.dbo.<table>_bak_20261021`. DROP on a Fabric managed table deletes its files, so time travel cannot restore it. | architecture.md Main brief Decision 3 | 2026-10-21 |
| D-07 | Tạm dừng trigger | Tạm dừng được `PL_VV_TRANS_SLV_TO_ENR_15P` khoảng 30 phút trên DEV. Sửa một lần gồm xóa `NB_SLV_PN_POI` và `NB_ENR_POI_COORDINATE`. | user 2026-10-21 | 2026-10-21 |
| D-08 | Quiesce SQL của SLV_1H | Q1 có 1 dòng `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`, `status = NO_DATA`, `lock_exec_id` null, `lock_at` null, `flow_name = NB_SLV_POI_ENTITY`. Q2 có `NO_DATA` 1, `PARTIAL_FAILED` 2, `SUCCESS` 1, không có `RUNNING`. Q3 có 4 dòng, cả bốn là `NB_00_ORCHES_SLV_TO_GLD`, đều có `ended_at`, dòng mới nhất kết thúc `2026-10-20T13:54:03Z`. Không chạm LIMIT 20. | evidence/results/slv-1h-quiesce.txt | 2026-10-21 |
| D-09 | Item pipeline SLV_1H | Pipeline `PL_VV_TRANS_SLV_TO_SLV_1H` không tồn tại trên DEV. Tên này chỉ là param của notebook orchestrator. Không có schedule và không có lịch sử run của item pipeline đó. | user 2026-10-21; evidence/results/slv-1h-quiesce.txt | 2026-10-21 |
| D-10 | R0 đến R5 | Registry `n = 0`. `V_cfg = 17`, `V_wm = 140`. Hai khoá luồng null. R2: hai notebook không còn. R3: `cạnh=8 watermark=6`, giữ 17. R4: `cạnh=0 watermark=0`, giữ 17. R5 PLAN: 4 node, 17 cạnh, 0 Dirty Edge, 0 ứng viên, `activities` rỗng, status `PLAN`, không ConfigError. Chưa có `count(*)` hai bảng, chưa có `SHOW CREATE TABLE`, chưa có `entity_edges_ok`. Chưa chạy R6. | evidence/results/runtime-r0-r5.txt | 2026-10-22 |
| D-11 | R5b | `gld_enr_poi_coordinate` 94 dòng. `slv_pn_poi` 30 dòng. `entity_edges_ok=6`. PLAN ép node: amenity phụ thuộc entity, info phụ thuộc amenity và entity. Status `PLAN`. Không activity coordinate hay `slv_pn_poi`. Chưa có `SHOW CREATE TABLE`. Chưa backup, chưa DROP. | evidence/results/runtime-r5b.txt | 2026-10-22 |
| D-12 | Backup R6 | Câu cửa `n = 0`. Backup `gld_enr_poi_coordinate_bak_20261021` có 94 dòng. Backup `slv_pn_poi_bak_20261021` có 30 dòng. Cả hai bảng gốc là Delta, không partition, `tableFeatures` gồm `appendOnly` và `invariants`. Chưa DROP. | evidence/results/runtime-r6.txt | 2026-10-22 |
| D-13 | DROP và R7 | Người dùng xác nhận đã DROP hai bảng gốc. `tableExists` chưa có trong paste. R7 `exec_id` `5edc3634-ad7a-4545-8465-d0c7830dc543`, status `SUCCESS`. Ép `slv_poi_entity_non_enrich` và `slv_poi_amenity`. `gld_enr_poi_info` chạy như node sau, status `NO_DATA`, `trg_version` null. Tiến 16 cạnh. | evidence/results/runtime-r7.txt | 2026-10-22 |
| D-14 | Sau DROP | `tableExists`: coordinate False, `slv_pn_poi` False, info True, review True. Entity kết thúc `2026-10-22T03:18:02Z`, amenity bắt đầu `2026-10-22T03:18:16Z`. INV-1 = 16, INV-3 = 17. INV-5 và INV-6 là `TABLE_OR_VIEW_NOT_FOUND`. Amenity 58 dòng, entity 65 dòng. Mọi khoá null. Chưa có dòng `ctrl_log_run` của lần schedule sau khi bật lại. | evidence/results/runtime-r8.txt | 2026-10-22 |
| D-15 | Log sau R7 | `exec_id` `5edc3634-ad7a-4545-8465-d0c7830dd555`, `run_id` cùng giá trị, `NB_00_ORCHES_SLV_TO_ENR_15P`, `SUCCESS`, bắt đầu `2026-10-22T03:19:44Z`, kết thúc `2026-10-22T03:23:23Z`. `run_id = exec_id` là chạy tay. Không dùng dòng này làm bằng chứng schedule. | evidence/results/runtime-r8.txt; docs/context/CTRL_TABLES_CONTEXT.md mục `run_id` | 2026-10-22 |
| D-16 | Chấp nhận rủi ro R8 | Người dùng chấp nhận rủi ro: schedule `PL_VV_TRANS_SLV_TO_ENR_15P` vẫn tắt, không có dòng `ctrl_log_run` với `run_id` khác `exec_id`. Gate runtime = pass trên D-14 và lần chạy tay D-15. Rủi ro còn lại: lần schedule đầu tiên sau khi bật chưa được chứng minh. | user 2026-10-22 | 2026-10-22 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Người dùng gửi inventory và không sửa `request.md`. Cách hiểu trong mục `Cách hiểu đang dùng` vẫn là phạm vi.
- Ba bảng `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` giữ lại. Cạnh `slv_3p_poi_contact` → `slv_poi_entity_non_enrich` giữ và đã nằm trên `PL_VV_TRANS_SLV_TO_ENR_15P`.
- Không xóa `ctrl_log_run` và `ctrl_log_table_run`.
- Không đụng `slv_poi_entity` và `gld_enr_poi_review`.
- Chạy tay notebook orchestrator với param `PL_VV_TRANS_SLV_TO_SLV_1H` trong lúc `mvpoipy` vẫn là thao tác người vận hành. D-08 cho thấy bốn lần chạy cũ đã kết thúc ngày 2026-10-20. Không có item pipeline để queue hoặc retry.

## Sai lệch so với kiến trúc

- Comment đầu cell `mvpoipy` trong §16.2 có chữ `DROP`. Mục 16.5 cấm token đó trong cả cell. Dòng comment đổi thành câu không chứa `DROP`. Cell vẫn không có lệnh xóa bảng.
- Comment seed ở §16.3 ghi tên `slv_pn_poi` và `gld_enr_poi_coordinate`. `test_removed_notebooks_absent` cho phép hai tên đó trong comment của `NB_SETUP_INITIAL_DDL`, và vẫn cấm chúng trong code của notebook đó cũng như trong mọi notebook khác ngoài `NB_CREATE_DDL`.
- `mvpoipy` thêm ba kiểm tra trước DELETE so với §16.2: info active theo `(src_schema, src_tbl)`, dòng khóa NULL, và owner `pl_name IS NULL`. Post-check và hai lệnh DELETE giữ nguyên. Đây là GATE-002, GATE-003, GATE-004.
- `SHOW CREATE TABLE` trên Delta trả `DELTA_OPERATION_NOT_ALLOWED`. Runbook đổi sang `DESCRIBE TABLE` và `DESCRIBE DETAIL`. Rollback bảng đã DROP là CTAS từ bảng `*_bak_20261021`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | rejected-false-positive | §9 giữ lease setup 90 phút để setup không chiếm khóa NB_00. §10 thu hồi khóa cell sau tối đa 35 phút. Chiều ngược lại không xảy ra trong rollout: trigger ENR_15P được tạm dừng và setup không chạy trong `mvpoipy`. | |
| GATE-002 | P1 | fixed | So `_info_edges()` với `WANT_INFO` được đưa vào `issues` trước `Dừng trước khi ghi`. Post-check sau DELETE giữ nguyên. | |
| GATE-003 | P1 | fixed | `_info_edges()` nhóm theo `(src_schema, src_tbl)`. `WANT_INFO` là `(lh_vv_silver.dbo, src)`. | |
| GATE-004 | P1 | fixed | Cell đếm dòng khóa NULL trước khi ghi. Hai notebook setup đổi predicate owner thành `pl_name <> ENR OR pl_name IS NULL`. | |
| GATE-005 | P1 | rejected-false-positive | §10: C4 không nhả khóa thì chờ lease hết hạn, tối đa 35 phút. §9 không thêm vòng retry, theo tiền lệ `enrinfopy`. | |
| PIPE-001 | P1 | rejected-false-positive | D-09: không có item pipeline `PL_VV_TRANS_SLV_TO_SLV_1H`, tên chỉ là param notebook. D-08: khoá luồng null và không có log `RUNNING`. Không có trigger để disable, không có run queued hoặc retry. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-21: Duyệt một vòng review thêm. `review_plan.extra_round_approved_on = 2026-10-21`.
- 2026-10-22: Chấp nhận rủi ro thiếu dòng schedule của `PL_VV_TRANS_SLV_TO_ENR_15P`. D-16. Gate runtime = pass.

## Lịch sử quyết định

- 2026-10-21: Mở task từ yêu cầu chuyển hai node sang `PL_VV_TRANS_SLV_TO_ENR_15P` và xóa bảng cùng cấu hình không dùng. Chưa chốt cách hiểu.
- 2026-10-21: Ghi D-01 đến D-04 từ inventory DEV. Chín cạnh của hai node đã ở ENR trên DEV. Seed repo vẫn để `PL_VV_TRANS_SLV_TO_SLV_1H`.
- 2026-10-21: `run-author --kind model` ghi `model-design.md`. D-05: các câu hỏi model không chặn Architect.
- 2026-10-21: Architect PASS. Ghi D-06 từ Main brief Decision 3. Chưa sửa notebook.
- 2026-10-21: Người dùng xác nhận tạm dừng được `PL_VV_TRANS_SLV_TO_ENR_15P`. D-07: xóa hai notebook trong cùng lần sửa.
- 2026-10-21: Review vòng 1 FIX_REQUIRED. GATE-002, GATE-003, GATE-004 đã sửa. GATE-001 và GATE-005 giữ theo §9 và §10.
- 2026-10-21: Review vòng 2 `EVIDENCE_REQUIRED`, finding `PIPE-001`. Chưa diễn giải. Probe đọc `evidence/probes/slv-1h-quiesce.sql` cộng quan sát Monitor. Ảnh sau post-check để runtime.
- 2026-10-21: D-08 từ Q1–Q3. Phần SQL đạt. Monitor chưa có, nên chưa chuyển review.
- 2026-10-21: D-09. Người dùng xác nhận item `PL_VV_TRANS_SLV_TO_SLV_1H` không tồn tại; tên chỉ là param của notebook orchestrator. `PIPE-001` ghi `rejected-false-positive`. Vòng review đã ở cap 2.
- 2026-10-21: Người dùng duyệt vòng review thêm. `extra_round_approved_on = 2026-10-21`.
- 2026-10-21: Review vòng 3 PASS. `PIPE-001` được xác nhận `rejected-false-positive`. Không còn P0/P1. Status `waiting_runtime`.
- 2026-10-21: Ghi `runtime-runbook.md` từ architecture §17, R0 đến R8. Chưa chạy Fabric. Dừng trước R6.
- 2026-10-22: D-10. R0–R4 đạt. R5 không hiện thứ tự vì 0 ứng viên. Chưa đủ số dòng và `entity_edges_ok` để sang R6.
- 2026-10-22: D-11. R5b đạt thứ tự entity, amenity, info. Số dòng 94 và 30. Chưa DROP.
- 2026-10-22: `SHOW CREATE TABLE` lỗi `DELTA_OPERATION_NOT_ALLOWED` trên cả hai bảng Delta. Chưa backup. Runbook đổi sang `DESCRIBE`.
- 2026-10-22: D-12. Backup 94 và 30 dòng. Câu cửa bằng 0. Chờ xác nhận trước DROP.
- 2026-10-22: D-13. Người dùng đã DROP. R7 SUCCESS. Info là node sau, `NO_DATA`. Chưa có `tableExists` và R8.
- 2026-10-22: D-14. `tableExists` và inventory đạt. Chưa có log lần schedule. Gate runtime vẫn pending.
- 2026-10-22: Người dùng nhắn đã pass. Paste không có `exec_id`, `run_id`, `status`, `started_at`. Không đóng gate runtime.
- 2026-10-22: D-15. Một dòng SUCCESS sau `03:19:31Z`, nhưng `run_id = exec_id`. Đó là chạy tay. R8 vẫn chờ dòng schedule.
- 2026-10-22: D-16. Người dùng chấp nhận rủi ro vì pipeline chưa bật. Gate runtime = pass.
