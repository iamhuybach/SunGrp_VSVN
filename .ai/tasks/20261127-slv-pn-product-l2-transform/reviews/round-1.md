## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`.
- Reviewers: `state-correctness-reviewer` (`FIX_REQUIRED`), `spark-runtime-reviewer` (`EVIDENCE_REQUIRED`), `sql-data-reviewer` (`PASS`).
- Risk gate: không chạy, đúng theo task state.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| STATE-002 | P1 | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1109` | Tên `deleted_flag` không hợp lệ chỉ bị phát hiện sau khi `ensure_target` đã tạo hoặc đổi schema, để lại trạng thái dở dang và retry tiếp tục thất bại. | Kiểm tra quy tắc tên cờ trong validation trước write và thêm test chứng minh cờ không hợp lệ không tạo bảng hoặc commit schema. |
| SPARK-001 | P1 | `.ai/tasks/20261127-slv-pn-product-l2-transform/task-state.yaml:14` | `runtime_required: false` trái với bằng chứng runtime bắt buộc tại `architecture.md:446`, nên MERGE Delta, UDF, diff parity và no-commit rerun chưa được xác minh trên Fabric. | Đặt `runtime_required: true` và thực hiện các probe Fabric DEV R1–R3 đã quy định trong architecture. |

P2: 2. P3: 0.

Probe: Chạy R1 scratch cho 10 state transitions và nhánh mặc định, đối chiếu `diff_counts` với Delta `operationMetrics`; sau đó R2 forced rerun yêu cầu `0/0/0` và không có commit mới, cùng R3 count-only invariants.
