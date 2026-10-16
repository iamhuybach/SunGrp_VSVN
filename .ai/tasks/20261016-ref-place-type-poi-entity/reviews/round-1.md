## Manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer` — FIX_REQUIRED; `spark-runtime-reviewer` — PASS; `state-correctness-reviewer` — FIX_REQUIRED.
- Risk gate: không bắt buộc, không chạy.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| SQL-001 / STATE-001 | P1 | `notebooks/NB_SETUP_POI_ENTITY.ipynb:668`, `:689-692`, `:696-712` | Setup có thể trả `SUCCESS` nhưng không thiết lập đúng hai edge active duy nhất: `NOT EXISTS` chấp nhận edge inactive/drifted, còn owner pre-check có race với writer đồng thời. | Đưa kiểm tra ownership vào write path có retry; MERGE hoặc fail closed đối với edge inactive/drifted, rồi hậu kiểm chính xác hai edge active có schema, priority và `RECOMPUTE` đúng, đồng thời không có active owner khác trước khi trả `SUCCESS`. |

P2: 2. P3: 0.

Probe: không cần; finding được chứng minh trực tiếp từ predicate và control flow.
