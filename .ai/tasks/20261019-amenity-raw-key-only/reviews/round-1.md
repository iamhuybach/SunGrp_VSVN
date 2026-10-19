## Manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: completed

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P1 | `notebooks/NB_SLV_POI_AMENITY.ipynb:199` | Quality gate chỉ chặn khi không có condition nào; thiếu một key như `sauna` vẫn cho phép RECOMPUTE và có thể soft-delete các fact tương ứng. | Trước mọi write, yêu cầu tập key đã resolve bằng chính xác `FLAG_MATCH ∪ TYPE_MATCH`, ném `QualityGateError` khi thừa/thiếu, và thêm regression test xóa một expected key. |

P2: 1. P3: 0.
