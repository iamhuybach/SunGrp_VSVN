## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`
- Risk gate: not required

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| STATE-002 | P1 | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1109`; `tests/test_slv_pn_product_l2_contract.py:217` | `deleted_flag=""` vượt qua các validation dùng truthiness, nên `ensure_target` có thể chạy theo semantics mặc định và ghi trạng thái sai. | Xử lý mọi giá trị khác `None` là cấu hình cờ, từ chối tên rỗng/không hợp lệ trước write và thêm test thực thi chứng minh `ensure_target`/MERGE không được gọi. |
| SPARK-001 | P1 | `.ai/tasks/20261127-slv-pn-product-l2-transform/task-state.yaml:14` | `runtime_required` đã được sửa thành `true`, nhưng chưa có kết quả Fabric DEV để xác minh Delta MERGE, diff parity và rerun không tạo commit. | Chạy đầy đủ R1–R3 trên Fabric DEV và lưu kết quả; chỉ đóng finding khi mọi invariant đạt. |

P2/P3: `0/0`.

Probe: `Fabric DEV: chạy R1 scratch MERGE self-test → R2 p_force=true rerun (0/0/0 và không có Delta commit) → R3 evidence/probes/pnl2_invariants.py, rồi lưu toàn bộ output vào evidence/results/.`
