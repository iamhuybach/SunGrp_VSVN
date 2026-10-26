# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D1 | Phạm vi file | Thêm `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json` và `tests/test_gld_srv_poi_contract.py` vào `scope.files` trước khi sửa. | architecture.md, Scope gap | 2026-10-26 |
| D2 | Vòng review thêm | Người dùng duyệt một vòng review thêm ngày 2026-10-26. `review_plan.extra_round_approved_on` là `2026-10-26`. | Chat 2026-10-26 | 2026-10-26 |
| D3 | Đổi id khoá | Delta DEV báo `DELTA_UNSUPPORTED_SUBQUERY` khi `UPDATE` đổi `watermark_id` có subquery đếm `new_id`. Cell đếm trước, `UPDATE` không có subquery, đếm lại sau. Nếu id cũ còn hoặc id mới không đúng 1 dòng thì trả dòng đang giữ `LOCK` về id cũ và dừng trước `UPDATE` config. | Kết quả Fabric DEV 2026-10-26, cell `plcadpy` | 2026-10-26 |
| D4 | Bỏ review round 4 | Người dùng chấp nhận không chạy review round 4 cho sửa `DELTA_UNSUPPORTED_SUBQUERY`. Review round 3 vẫn là vòng review cuối đã chạy. `specialist_review` và `risk_gate` được ghi `pass` theo quyết định này. | Chat 2026-10-26 | 2026-10-26 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- `plcadpy` không còn nguyên văn architecture. Cell khóa cả `old_id` và `new_id`, đếm `new_id` trước và sau `UPDATE` đổi id (Delta không nhận subquery trong `UPDATE`), gọi `_issues` trước nhánh đã đổi, đọc lại cặp khoá sau khi nhả owner hết hạn, và đánh dấu `held` trước `UPDATE` nhận khoá. Lý do: review round 1 GATE-001, review round 2 GATE-002, GATE-003, SPARK-001, và runtime RT-001. Không sửa `NB_LIB_TRANSFORM_SLV_GLD`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P0 | fixed | Đếm `new_id` trước `UPDATE`, câu `UPDATE` không có subquery, đếm lại sau. Lệch thì trả dòng `LOCK` về id cũ, không sửa config. Test `test_pl_cadence_rename_is_conditional`. | |
| RT-001 | P1 | fixed | Fabric DEV: `AnalysisException` `DELTA_UNSUPPORTED_SUBQUERY` trên `UPDATE` đổi `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`. Cùng cách xử lý với D3. Config và id khoá chưa đổi. | |
| GATE-002 | P1 | fixed | `_issues(old, new)` chạy trước nhánh đã đổi và trước mọi ghi. Trùng khoá logic hoặc lệch cặp thì dừng, không báo đã đổi. | |
| GATE-003 | P1 | fixed | Sau khi nhả khoá hết hạn, đọc lại đúng một cặp. Chỉ báo đã đổi khi `lock_exec_id` là NULL. Owner còn sống thì dừng. Hết hạn thì thử lại tối đa 3 lần. | |
| SPARK-001 | P1 | fixed | `held = True` trước `UPDATE` nhận khoá. `finally` nhả theo `lock_exec_id = LOCK`. Cleanup lỗi không che lỗi gốc. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- 2026-10-26: duyệt thêm một vòng review. Main ghi `extra_round_approved_on` rồi sửa GATE-002, GATE-003, SPARK-001 trước review round 3.
- 2026-10-26: chạy lại cell `plcadpy` đã sửa, không mở review round 4. Lần chạy in `ENR_15P -> ENR_15M` cạnh 21 và `GLD_30P -> GLD_30M` cạnh 12, cả hai `khoá đổi id`, run log `RUNNING` tên cũ 0.
- 2026-10-26: D4. Người dùng chấp nhận bỏ review round 4. Main ghi `specialist_review=pass` và `risk_gate=pass`, rồi chuyển `ready_to_merge`.

## Lịch sử quyết định

- 2026-10-26: D1. Architecture yêu cầu thêm hai file vào `scope.files` trước khi sửa. Main thêm đúng hai đường dẫn đó. Không đổi quyết định nghiệp vụ.
- 2026-10-26: GATE-001, GATE-002, GATE-003 fixed trong `plcadpy`. Không sửa lib.
- 2026-10-26: D2. Người dùng duyệt thêm một vòng review. Round 2 còn GATE-002, GATE-003, SPARK-001.
- 2026-10-26: D3 / RT-001. Lần chạy `plcadpy` đầu trên Fabric DEV lỗi `DELTA_UNSUPPORTED_SUBQUERY`. Baseline còn `ENR_15P` 21 dòng (20 active), `GLD_30P` 12 dòng, `n_wm_e` 34, không trùng khoá logic, không log `RUNNING`. `ctrl_mng_pipeline_config` version 24, `ctrl_mng_watermark` version 225. `UPDATE` đổi id không ghi.
- 2026-10-26: Người dùng chạy lại cell đã sửa. Output khớp baseline: cạnh 21 và 12, khoá đổi id, log `RUNNING` tên cũ 0. Chưa có K1–K5 và lần chạy thứ hai.
- 2026-10-26: K1–K5 đạt. A0 là config version 26 và watermark version 238. Lần `plcadpy` thứ hai in `đã đổi, không ghi` cho cả hai cặp. Chưa có version Delta sau lần hai.
- 2026-10-26: Sau lần hai, config vẫn version 26 và watermark vẫn version 238. B1–B3 giống K1–K3, kể cả `updated_at`. Idempotency của `plcadpy` đạt. Chưa đổi tên pipeline Fabric.
- 2026-10-26: Người dùng đổi pipeline Fabric thành `PL_VV_TRANS_SLV_TO_ENR` để dùng lại, không đổi thành `PL_VV_TRANS_SLV_TO_ENR_15M`. PLAN tay với `p_pl_name=PL_VV_TRANS_SLV_TO_ENR_15M` đạt: 4 node, 20 cạnh, không WARN nhịp, không ConfigError. PLAN gold trong log là `PL_VV_TRANS_SLV_TO_GLD_1H`, chưa phải `PL_VV_TRANS_SLV_TO_GLD_30M`.
- 2026-10-26: PLAN `PL_VV_TRANS_SLV_TO_GLD_30M` đạt nhịp: 4 node, 12 cạnh, không WARN `Không đọc được nhịp`, không ConfigError. Có WARN `output_versions_json` của `slv_poi_entity_non_enrich` và 3 cạnh `NEW_EDGE` vào `gld_srv_poi_multi_lang`. Chưa có RUN ENR_15M sau đổi tên.
- 2026-10-26: RUN `PL_VV_TRANS_SLV_TO_ENR` với `p_pl_name` literal `PL_VV_TRANS_SLV_TO_ENR_15M` kết thúc `NO_DATA` sau 53s, `error` null, 0 Dirty Edge. Kiểm tra nhịp của hai tên mới đã đủ. Chưa chạy `GLD_30M`.
- 2026-10-26: D4. Chấp nhận bỏ review round 4 sau khi runtime `pass`.
