## Model and reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Reviewers: `spark-runtime-reviewer`, `sql-data-reviewer`, `api-contract-reviewer`, `jpa-performance-reviewer`.
- Risk gate: không chạy (`not_required`).

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

- `SPARK-001` — P1 — `notebooks/NB_GLD_SRV_POI_INFO.ipynb:245`: `_cover` thực hiện duplicate-check bằng action, sau đó subplan media chưa cache có thể bị tính lại cho metric và MERGE, tạo rủi ro scan/shuffle lặp đáng kể trên F16 nhưng chưa có runtime evidence. Nếu probe xác nhận chi phí đáng kể, materialize và tái sử dụng subplan với cache/unpersist có giới hạn hoặc hợp nhất validation/metrics để tránh recompute.

## P2/P3

0.

Probe: Chạy một lần `gld_srv_poi_info` trên Fabric DEV và xuất Spark UI metrics cho mọi job đọc `slv_poi_media_info`: job count, scan bytes, shuffle read/write, spill, peak executor memory, wall time và tổng thời gian node.
