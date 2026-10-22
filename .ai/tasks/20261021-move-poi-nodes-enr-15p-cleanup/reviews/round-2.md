## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp policy.
- Reviewers: `fabric-pipeline-reviewer`, `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`.
- Risk gate: completed.

## Gate verdict: `EVIDENCE_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| PIPE-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2460,2570,2614` | Cleanup xóa watermark của `PL_VV_TRANS_SLV_TO_SLV_1H` mà không giữ lock hoặc chặn luồng cũ, nên một active/queued/retry run có thể acquire hoặc tạo lại watermark sau pre-check và làm trạng thái retirement phân kỳ. | Chứng minh trigger cũ đã disable và không còn active/queued/retry run trong toàn bộ cleanup, đồng thời retire dưới exclusion; hoặc thêm durable retirement guard mà orchestrator cũ bắt buộc kiểm tra. |

P2/P3: `P2=4`, `P3=1`.

Probe: disable trigger `PL_VV_TRANS_SLV_TO_SLV_1H`, xuất Fabric run history chứng minh số run `active`, `queued` hoặc `retrying` bằng `0` ngay trước cleanup và vẫn bằng `0` sau post-check.
