# Quyết định

## Giả định còn lại

- Probe E1 ngày 2026-10-08 trên Fabric DEV trả `missing_event_id_rows = 0`, `conflicting_exact_ties = 0`, `conflicting_entity_time_ties = 0`.
- 2026-10-08, người dùng xác nhận nguồn bảo đảm `crawled_at` tăng nghiêm ngặt theo từng POI qua mọi commit sau này. Task này không đổi thứ tự CDC.
- Partner FULL `19c15ef9` reject 199418. Bằng 199.408 event `product*` `after` rỗng cộng 10 event `order_item_*` đã ghi ở `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` và `99_PAIN_POINTS.md` D1. Log ghi lỗi theo bảng = 0. Không có số reject của bảng control cũ trong log này để so từng dòng.
- 3P FULL `21733707` đọc 1 dòng raw, hợp lệ 1, reject 0, ghi 16 dòng silver trên 8 bảng. Năm bảng `NO_DATA` vì tài liệu không có khối tương ứng. `vi` có trong danh sách ngôn ngữ của tài liệu. `en` và `ko` không có.

## Sai lệch so với kiến trúc

- Mặt dữ liệu ban đầu đi theo `architecture.md`. Sau review round 1 có hai chỗ siết thêm, ghi ở đây trước khi sửa tiếp:
  - `WHERE NOT EXISTS` của seed `ctrl_mng_pipeline_config` thêm `c.trg_schema = 'lh_vv_silver.dbo'` cho cả partner và 3P. I9 đã yêu cầu đúng một dòng theo khoá đủ gồm `trg_schema`. §9.7 chỉ nêu predicate `src_tbl`. Bảng trống thì kết quả seed không đổi. Lần seed lại không bỏ sót dòng silver khi đã có cùng `trg_tbl` ở schema khác.
  - Rollback trong `runtime-runbook.md` thêm hàng rào dừng trên cả `lh_vv_ctrl` và `lh_vv_bronze.ctrl` trước khi deploy bản cũ. `architecture.md` §11.1 chưa có hàng rào này. Main không sửa `architecture.md`.
- Ngoài mặt dữ liệu: `scripts/agent_runner.py` đổi `--max-turns` từ 20 thành 80 theo quyết định người dùng ngày 2026-10-08, trước khi chạy lại cổng kiến trúc. Không đổi hành vi extract, MERGE, watermark hay pipeline.
- 2026-10-08, trước khi sửa pipeline: người dùng chọn lọc config `FL_00` còn `partner_raw_data` (GATE-002). `Get_Config_4Run` thêm `src_tbl = 'partner_raw_data'`. Dòng config 3P giữ nguyên trong `ctrl_mng_pipeline_config` để notebook 3P chạy tay vẫn đọc được. §9.6 và R-FL1 trong `architecture.md` vẫn mô tả query không lọc nguồn và kỳ vọng 2 dòng. Main không sửa `architecture.md`. Không sửa `manifest.json`.
- 2026-10-08, trước khi sửa tiếp: người dùng chọn `max_parallel = 12` cho cả dry-run và lần ghi 3P (GATE-009). §9 và bước 6 trong `architecture.md` vẫn ghi 13.
- 2026-10-08, trước khi sửa `orchestrate`: người dùng yêu cầu bỏ lock và cấu hình gold hiện tại (GATE-003). `NB_00` kiểm tra cạnh `RECOMPUTE` trước khi tạo `wm_flow__<pl>` hoặc log. Seed vẫn không có cạnh gold. Runbook có `DELETE` các dòng `load_mode = RECOMPUTE`, `wm_flow__%`, `wm_e__%` trên cả `lh_vv_bronze.ctrl` và `lh_vv_ctrl.dbo`. §11.1 cấm sửa archive; §11.2 mô tả `NB_00` tạo khoá rồi mới `ConfigError`. Main không sửa `architecture.md`. Năm cột gold-log giữ nguyên vì extract và lib đang đọc chúng.

## Xử lý findings

Review chính thức round 2 chạy bằng Codex `gpt-5.6-sol` effort high và kết luận `USER_DECISION`. Đây là round review cuối. `PASS` không hợp lệ. Bản Cursor medium được giữ ở `reviews/round-2-cursor-medium.md`.

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P0 | fixed | Codex high đóng premise thứ tự nhờ E1 và cam kết `crawled_at`. Replay hai commit nằm ở GATE-008. | |
| GATE-002 | P1 | fixed | Codex high xác nhận `Get_Config_4Run` lọc `partner_raw_data`. | |
| GATE-003 | P1 | accepted-risk | Khoá không còn được tạo khi thiếu cạnh. Gold vẫn không chạy vì không có cạnh `RECOMPUTE`. Người dùng đã yêu cầu bỏ cấu hình gold. Codex high: outage này chặn `PASS`. | |
| GATE-004 | P1 | fixed | Codex high xác nhận hàng rào dừng hai mặt phẳng. | |
| GATE-005 | P1 | fixed | Codex high xác nhận anti-join có `trg_schema`. | |
| GATE-006 | P1 | accepted-risk | Người dùng coi như xong và sẽ export sau. Codex high vẫn để mở cho đến khi có cặp JSON/manifest từ Fabric. | |
| GATE-007 | P1 | chờ runtime | Id cell đã có. Codex high yêu cầu import `NB_CREATE_DDL` trên Fabric DEV. | |
| GATE-008 | P1 | accepted-risk | Người dùng coi như xong và sẽ gửi log sau. `gates.runtime` vẫn `pending`. Codex high không nhận chấp nhận rủi ro thay cho log. | |
| GATE-009 | P1 | fixed | Dry-run, lần ghi, default notebook và doc context đều là 12. Đo F16 nằm trong log GATE-008. | |
| GATE-010 | P2 | fixed | Runbook bỏ câu phục hồi vòng 3P của `FL_00`. Sửa sau review cuối, chưa được review lại. | |

Giá trị đóng hợp lệ, khi người dùng hoặc round 2 chốt: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-08: chấp thuận sửa hệ thống agent, tăng `--max-turns` của Claude Architect trong `scripts/agent_runner.py` từ 20 lên 80, rồi chạy lại `run-gate`.
- 2026-10-08: probe E1 trả ba số 0. Chọn lọc `FL_00` còn `partner_raw_data`. Chấp nhận gold dừng cho đến khi có seed cạnh `RECOMPUTE`. Bỏ qua lệch `manifest.json`; người dùng sẽ export lại sau.
- 2026-10-08: Codex hết hạn mức. Người dùng chấp nhận chạy review round 2 trên Cursor bằng slug `gpt-5.6-sol-medium`. Báo cáo đó được giữ ở `reviews/round-2-cursor-medium.md`.
- 2026-10-08: Codex đã có token. Người dùng yêu cầu chạy lại review bằng `gpt-5.6-sol` effort high. Round medium không tính là round Codex. Bộ đếm review đưa về 1 để `run-gate` ghi round 2 chính thức.
- 2026-10-08: GATE-001, nguồn bảo đảm `crawled_at` tăng nghiêm ngặt theo từng POI. GATE-009, `max_parallel = 12`. GATE-008 và GATE-006, người dùng coi như xong và sẽ bổ sung log cùng bản export sau. GATE-003, bỏ lock và cấu hình gold hiện tại.
- 2026-10-09: người dùng đã chạy bốn `DELETE` gold. Đã export `FL_00`. Manifest và JSON cùng khai báo `conn_lh_vv_bronze_by_sqlep`, `lh_vv_ctrl`, `lh_vv_bronze`. Query export đọc `dbo.ctrl_mng_pipeline_config` trên database `lh_vv_ctrl` và làm mất điều kiện `src_tbl = 'partner_raw_data'`. Activity notebook trong export tên `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`. Main thêm lại điều kiện `partner_raw_data` vào JSON repo. Lần chạy 09/10 00:13 có hai vòng ForEach, cả hai `Set_Msg_Skip`, không mở notebook.
- 2026-10-09: người dùng đã dán lại `src_tbl = 'partner_raw_data'` vào `Get_Config_4Run` trên Fabric và xác nhận `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` là notebook vừa chạy thành công, không phải bản backup cũ.
