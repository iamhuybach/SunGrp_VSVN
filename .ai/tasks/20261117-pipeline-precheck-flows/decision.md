# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Model lane | Main giữ Grok 4.7 medium (`models.main.actual=grok-4.7`). Ba lane Claude Opus 5.5 của task này chạy Claude Code Fable 5.2, effort medium: EX-ARCH role architect, EX-AUTHOR role author, EX-PROPOSAL role author_proposal. kind `model_override`, runtime `claude-code-extension`, approved_by user, approved_on 2026-11-17. Review giữ gpt-5.6-sol medium. CLI không nhận `claude-fable-5-2` thì dừng, không đổi về Opus. | Người dùng, 2026-11-17 | 2026-11-17 |
| D-02 | Bố trí pipeline | Ba pipeline, mỗi pipeline một `pl_name` đã có trong `ctrl`. `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` xử lý bốn nguồn bronze trong một ForEach tuần tự, một notebook tại một thời điểm. `PL_VV_TRANS_SLV_TO_ENR_15M` và `PL_VV_TRANS_SLV_TO_GLD_30M` mỗi pipeline một cổng SQL và một notebook điều phối. Mọi pipeline `concurrency = 1`. Dispatch extract: một ForEach, `If_HasWork` giữ nguyên biểu thức và nhánh false, bốn `If_Run_*` anh em, không Switch. Cổng transform: một Script trên `ctrl_log_run` qua `conn_lh_vv_bronze_by_sqlep`; notebook chạy trừ khi `gate_reason = 'NO_DATA'`. Seed `ctrl` không sửa. | `architecture.md` §4 | 2026-11-17 |
| D-03 | Phạm vi test | Thêm `tests/test_enr_poi_contract.py` và `tests/test_pipeline_precheck_contract.py` vào `scope.files`. Người dùng yêu cầu implement đúng Edit list và `verify` pass trong cùng chat, nên S1 không tách thành lượt hỏi riêng. | Edit list hàng 11–12, S1, yêu cầu người dùng | 2026-11-17 |
| D-04 | Sửa P1 review vòng 1 | PIPE-001: `or()` của binding ENR và GLD chỉ còn hai đối số, lồng nhau. SQL-001: mỗi Script lọc đúng `src_schema = 'lh_vv_bronze.dbo'` và một `src_tbl`. SQL-002: so sánh `status` qua `COALESCE(status, '')` để NULL không thành `NO_DATA`. Phần PIPE-002 của dòng này bị D-05 thay thế. | `reviews/round-1.md` PIPE-001, SQL-001, SQL-002 | 2026-11-17 |
| D-05 | Vòng review thêm cho PIPE-002 | Người dùng duyệt thêm một vòng review ngày 2026-11-17 (`review_plan.extra_round_approved_on`). Mỗi nguồn là một `Wave_*`. `Get_Config_*` nằm trong wave. Wave sau phụ thuộc `Completed` của wave trước. Lỗi config hoặc `ForEach` chỉ ghi `v_any_failed = true`. `Fail_Extract_Waves` chạy một lần sau `Wave_ENRICH`. | Người dùng, 2026-11-17; `reviews/round-2.md` PIPE-002 | 2026-11-17 |
| D-06 | Phần Fabric và S2 còn lại | Người dùng chấp nhận rủi ro ngày 2026-11-17. C1–C6 không chạy trên Fabric. Baseline B1, B2, B3, B5, B6 ENR và L3 đã có. B4 có file `_delta_log` mới hơn watermark. S2 giữ nguyên rule và doc layout cũ. `classification.runtime_required` thành false. | Người dùng, 2026-11-17 | 2026-11-17 |
| D-07 | Bốn extract song song | Người dùng muốn bốn nguồn extract trong FL_00 chạy cùng lúc, 2026-11-18. Bốn `ForEach` chỉ phụ thuộc `Validate_Extract_Binding` và `Lookup_WM`. `If_Any_Failed` chờ cả bốn `Completed`. `concurrency` của pipeline vẫn là 1. | Người dùng, 2026-11-18 | 2026-11-18 |
| D-08 | Biến pre-check theo nguồn | Bốn `ForEach` song song không dùng chung `v_src`, `v_last_ver`, `v_last_file`. `Filter_WM_*` so khóa literal `lh_vv_bronze.dbo\|<src_tbl>`. `Filter_NewCommits_*` và `If_HasWork_*` đọc `activity('Filter_WM_*')`, không đọc biến pipeline. Mỗi nguồn một `v_msg_*` và `v_msg_skip_*`. `v_any_failed` giữ vì chỉ ghi `true`. | Run `Set_Msg_Run_CMS`, 2026-11-18 | 2026-11-18 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- S2 không làm trong task này. Không sửa `.cursor/rules/20-data-pipeline.mdc` và các doc mô tả layout cũ, vì đó là đổi phạm vi và rule agent-system cần yêu cầu riêng của người dùng.
- D-04 lệch I10 và khối FILE verbatim: cạnh nối nguồn dùng `Completed` và `Failed`, không chỉ `Succeeded`. SQL cổng transform và query FL_00 không còn đúng từng byte của §18–§19. Bố trí ba pipeline ở D-02 giữ nguyên.
- D-05 thay `Fail_Source_*` bằng cờ `v_any_failed` và một `Fail_Extract_Waves` sau wave cuối.
- D-08: file dán Fabric bỏ `Set_src_*`, `Set_LastVer_*`, `Set_LastFile_*`. JSON trong `pipelines/` không đổi; layout repo vẫn là D-02.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| PIPE-001 | P1 | fixed | `or()` binding ENR và GLD lồng hai đối số. Test `test_expression_calls_are_binary`. | |
| SQL-001 | P1 | fixed | Mỗi `Get_Config_*` lọc `src_schema = 'lh_vv_bronze.dbo'` và một `src_tbl`. | |
| SQL-002 | P1 | fixed | `COALESCE(status, '')` trên `me` và `up` của ENR và GLD. NULL không bị loại khỏi quyết định có việc. | |
| PIPE-002 | P1 | fixed | Review vòng 3 PASS. Bốn `Wave_*` nối `Completed`. Lỗi config hoặc `ForEach` ghi `v_any_failed`. `Fail_Extract_Waves` chạy sau `Wave_ENRICH`. | |
| RT-C1-C6 | — | accepted-risk | Case C1–C6 chưa chạy. B4 cho thấy còn commit mới, nên lần FL_00 kế tiếp không phải case không có data. R1, R3, R5 chưa đo trên Fabric. | |
| S2 | — | accepted-risk | Không sửa `.cursor/rules/20-data-pipeline.mdc` và các doc mô tả layout cũ trong task này. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-11-17 — PIPE-002: duyệt thêm một vòng review. Không chọn `accept-risk` hay `backlog`.
- 2026-11-17 — Chấp nhận rủi ro phần còn lại: không chạy C1–C6, giữ S2 ngoài task. Workflow đi tiếp tới `ready_to_merge`.
- 2026-11-18 — Người dùng xác nhận bốn pipeline trên Fabric đã xong: `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, `PL_VV_TRANS_SLV_TO_ENR_15M`, `PL_VV_TRANS_SLV_TO_GLD_30M`, `PL_VV_TRANS_SLV_TO_GLD_1H`. Gate `runtime` vẫn `not_required`. `PL_VV_TRANS_SLV_TO_GLD_1H` không có file trong `pipelines/`.

## Lịch sử quyết định

- 2026-11-17 — D-01. Người dùng duyệt exception trước `run-author` và `run-gate`. Mỗi role một entry trong `task-state.yaml` `exceptions`, scope là lane đó của task `20261117-pipeline-precheck-flows`. `models.*.expected` và `models.architect.effort` / `models.author_proposal.effort` giữ giá trị policy; lane thực tế lấy từ exception.
- 2026-11-17 — D-02. Chọn ba pipeline theo `pl_name` sẵn có. Bác L-A (một pipeline gộp phá `pl_name`, seed, hậu tố nhịp). Bác L-B (một pipeline mỗi nguồn bronze, bốn lịch có thể mở bốn session Spark). Bác L-C (pipeline cha gọi con, thiếu artifact và id). Bác E-A, E-B, E-C cho dispatch extract. Bác T-A và T-C cho cổng transform. Chấp nhận ba session Spark cùng lúc; runbook đo ở case C5. Ghi trước khi sửa JSON.
- 2026-11-17 — D-03. S1: thêm hai file test vào `scope.files` rồi implement, vì lượt này yêu cầu làm đúng Edit list và không dừng sau architecture PASS.
- 2026-11-17 — D-05. Người dùng duyệt `extra_round_approved_on = 2026-11-17` để review vòng 3 sau khi sửa PIPE-002. Bỏ `Fail_Source_*` vì activity `Fail` có thể kết thúc pipeline trước wave sau.
- 2026-11-18 — D-07. Bốn nguồn extract trong file dán Fabric chạy song song. Chấp nhận tối đa bốn phiên Spark khi cả bốn đều có data. ENR và GLD vẫn chạy sau, không nằm trong bốn `ForEach` này.
- 2026-11-18 — D-08. Run CMS báo `last_src_version=186` và `new_commits=1302`. `1488 - 186 = 1302`: `Filter_WM_CMS` và `Filter_NewCommits_CMS` đã dùng watermark của `brz_3rd_crawler_poi_stream` vì biến pipeline là một bản dùng chung. Notebook CMS sau đó đọc đúng watermark 1488 và xử lý 0 dòng, nhưng Spark đã mở. Sửa file dán trước lần chạy sau. Lần sau, `v_msg_skip_CMS` ghi `last_src_version=1488`, `new_commits=0`.
- 2026-11-18 — Người dùng xác nhận cả bốn pipeline Fabric đã xong. Repo vẫn chỉ có JSON của FL_00, ENR_15M và GLD_30M.
- 2026-11-18 — JSON live của `PL_VV_TRANS_SLV_TO_GLD_1H` vẫn lọc `ctrl_log_run` và cạnh upstream theo `PL_VV_TRANS_SLV_TO_GLD_30M`. `p_pl_name` gửi notebook đã là `PL_VV_TRANS_SLV_TO_GLD_1H`. File dán sửa: `evidence/fabric-editor-gld-1h.json`. Không thêm pipeline 1H vào `pipelines/`.
