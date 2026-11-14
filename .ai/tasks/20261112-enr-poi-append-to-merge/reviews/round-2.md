## Model và reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Reviewers: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`.
- Risk gate: completed.

## Gate verdict: `EVIDENCE_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| SPARK-002 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:160` | DRY_RUN 53 giây với 20.829 dòng chưa chứng minh shuffle, spill, peak memory hoặc shared-F16 headroom, nên cadence 15 phút và SLA vẫn chưa được xác nhận. | Giữ finding mở, thu đủ Spark UI và Fabric Capacity Metrics rồi chạy lại specialist/risk gate. |

STATE-001, SPARK-001, SQL-001 và SQL-002 đã được xác nhận fixed. Không phát hiện regression P0/P1 trong scoped diff.

P2/P3: 0.

Probe: Tạm dừng `PL_VV_TRANS_SLV_TO_ENR_15M`; chạy `NB_ENR_POI_INFO` với `p_mode=DRY_RUN`, `p_force=true`; ghi UTC interval, job ID, duration, rows, input bytes, shuffle read/write, memory/disk spill, peak executor/driver memory, retries/executor loss và shared-F16 utilization/throttling từ Spark UI cùng Capacity Metrics.
