## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`.
- Risk gate: không chạy (`not_required`).

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `SQL-001` — **P1** — `notebooks/NB_CREATE_DDL.ipynb:3281`: `_edge_rows()` không kiểm tra đầy đủ schema và payload của sáu pipeline edge, nên cấu hình sai `load_mode`, `nb_name`, `priority` hoặc `src_schema` có thể tồn tại hoặc chỉ bị phát hiện sau khi đã ghi một phần. Fix: so sánh toàn bộ tuple mong muốn (`pl_name`, source/target schema và table, `is_active`, `priority`, `load_mode`, `nb_name`) trước mọi write và dùng cùng điều kiện đầy đủ cho hậu kiểm.

## P2/P3

P2: 1; P3: 0.

Probe: Trong Fabric DEV, chạy `srvpoipy` hai lần; chạy `NB_GLD_SRV_POI_INFO` theo `DRY_RUN`, `RUN`, `RUN`; chạy `NB_GLD_SRV_POI_MULTI_LANG` ở `RUN`; lưu exit contract, QG/metrics, row counts và Delta history, xác nhận lần RUN thứ hai có `inserted=updated=deleted=0`, Delta version không đổi, lock được giải phóng, và multi-lang dừng trước write vì input bắt buộc rỗng.
