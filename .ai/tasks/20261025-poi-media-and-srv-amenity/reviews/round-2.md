## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`.
- Risk gate: không chạy vì `risk_gate_required: false`.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| STATE-001 | P1 | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1609` | Lease chỉ được refresh trước `ensure_target`; run có thể mất lease trong hoặc sau bước này rồi vẫn thực hiện `merge_target`, ghi đè snapshot mới hơn. | Refresh lại sau `ensure_target` và ngay trước `merge_target`; cập nhật test để bắt buộc thứ tự này. Nếu MERGE có thể kéo dài quá lease, cần atomic fencing hoặc bảo đảm lease còn hiệu lực đến lúc commit. |
| SPARK-001 | P1 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb:113` | Nếu aggregation hoặc `ctx.warn` lỗi sau khi cache được materialize, `unpersist()` bị bỏ qua, khiến cache tồn tại trong Fabric session và gây áp lực bộ nhớ F16 khi retry. | Bọc toàn bộ metrics block sau `persist()` bằng `try/finally` và gọi `unpersist()` trong `finally`. |

## P2/P3

P2: 1. P3: 0.
