# Request

## User outcome

Môi trường Fabric DEV được xóa dữ liệu để init lại. Lần này chỉ dựng lại dữ liệu ctrl. Bảng ref và mọi bảng bronze, silver, gold giữ nguyên cấu trúc, chưa nạp lại.

Yêu cầu nguyên văn:

Cho cụ thể các step chạy để:

- Xóa hết data của các phần từ bronze đến gold, kể cả ctrl. Các bảng ref không xóa. Mục đích là chạy init lại.
- Chỉ init các bảng ctrl. Chưa init các bảng bronze đến gold. Việc đó thuộc task khác.

Lý do nghiệp vụ: môi trường được xóa dữ liệu để init lại. Lần này chỉ dựng lại dữ liệu ctrl. Bảng ref và mọi bảng bronze, silver, gold giữ nguyên cấu trúc, chưa nạp lại.

## Scope

### In scope

- Runtime runbook để người dùng chạy trên Fabric DEV.
- Xóa dòng trong `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold` (schema `dbo` và `enr`) và bảy bảng `lh_vv_ctrl.dbo` liệt kê ở `docs/context/CTRL_TABLES_CONTEXT.md` §1.
- Seed lại đúng ba bảng: `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, `ctrl_cfg_schema_registry`.

### Out of scope

- DROP TABLE, đổi schema, VACUUM, OPTIMIZE.
- Xóa bảng có tên bắt đầu bằng `ref_`. Danh sách ref lấy từ `TABLE_SPECS` trong `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, không lấy từ ví dụ trong tài liệu đặt tên.
- Seed `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_cdc_state`, `ctrl_cdc_reject`.
- Chạy `NB_SETUP_INITIAL_DDL` hoặc `NB_CREATE_DDL`.
- Seed `ref_dictionary_place_type` hoặc `ref_dictionary_amenities`.
- Init dữ liệu bronze, silver, gold. Việc đó thuộc task khác.
- Sửa notebook, DDL, pipeline. Signal `data_model_change`.

## Acceptance criteria

- Có `runtime-runbook.md`. Người dùng chạy trên Fabric DEV. Agent không chạy lệnh xóa, không chạy notebook init.
- Xóa data nghĩa là xóa dòng. Không DROP TABLE, không đổi schema, không VACUUM.
- Phạm vi xóa: dữ liệu trong `lh_vv_bronze`, `lh_vv_silver`, `lh_vv_gold` (cả schema `dbo` và `enr`), và bảy bảng `lh_vv_ctrl.dbo` liệt kê ở `CTRL_TABLES_CONTEXT.md` §1. Loại trừ mọi bảng có tên bắt đầu bằng `ref_`. Danh sách ref lấy từ `TABLE_SPECS`, không lấy từ ví dụ trong tài liệu đặt tên.
- Init chỉ ba seed ctrl: `ctrl_mng_pipeline_config`, `ctrl_mng_watermark`, `ctrl_cfg_schema_registry`. Bốn bảng log và state của ctrl chỉ bị xóa, không seed.
- Không chạy nguyên notebook `NB_SETUP_INITIAL_DDL` và không chạy `NB_CREATE_DDL`. Không seed `ref_dictionary_place_type` hay `ref_dictionary_amenities`.
- Runbook có bước kiểm trước khi xóa, lệnh xóa, lệnh seed ctrl, và bước kiểm sau. Mỗi lệnh dẫn tới cell trong repo. Chỗ notebook không tách riêng phần ctrl thì ghi `MISSING` và đưa câu lệnh seed chỉ ba bảng ctrl, không bịa lệnh tạm dừng pipeline.
- Dòng đầu runbook ghi rõ chỉ Fabric DEV. Môi trường khác thì dừng ở `user_decision`.
- Trước khi xóa, người dùng chạy probe đọc danh sách bảng và số dòng. Bảng không có trong repo thì dừng, không xóa.

## Constraints

- Agent không chạy lệnh xóa và không chạy notebook init.
- Seed cell `id=init_seed_write` chỉ `WHEN NOT MATCHED THEN INSERT` (không `WHEN MATCHED`), và cùng cell ghi cả hai bảng ref. Không chạy cell đó. Xóa dòng ba bảng ctrl trước khi seed.
- `NB_CREATE_DDL` là notebook patch, không phải init của task này.
- Không đọc `notebooks_lgc/`.

## Classification rationale

- Complexity: `medium`. The deliverable is an operator runbook for a bounded DEV reset. It does not change table grain, keys, or notebook logic. Signals: `runtime_proof_required`, `idempotency` (the cited MERGE inserts only when the key is absent, so a second seed without another delete inserts nothing).
- Risk: `high`. Proof exists only after the user runs the runbook, and the runbook deletes rows across bronze, silver, gold, and ctrl. Row delete keeps the tables; the runbook forbids DROP, schema change, and VACUUM, and it stops outside Fabric DEV.
- Architecture: not required. No grain, key, state-owner, orchestration, or CDC-behavior change. `data_model_change` is not set.
- Evidence: not required as a gate before the runbook. The pre-delete check is a read-only table-list probe inside the runbook. There is no destructive probe.
- Runtime proof: required. The user runs the runbook on Fabric DEV. `gates.runtime` stays `pending` until the user reports results.
- Reviewer routing: `sql-data-reviewer`. The operator steps are statement-level `DELETE` and the three ctrl `MERGE` statements cited from the notebook. No pipeline, notebook-contract, or state-machine change, so the pipeline, Spark-runtime, and state-correctness reviewers are not routed. `risk_gate` stays `pending` because risk is `high`. This phase does not run review.
