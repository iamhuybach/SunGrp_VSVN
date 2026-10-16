## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`.
- Risk gate: không yêu cầu, không chạy.

## Gate verdict: `FIX_REQUIRED`

## P0/P1 findings

- `SPARK-001` — **P1** — `notebooks/NB_SLV_POI_AMENITY.ipynb:158`: Khi các POI chỉ có cờ không khớp hoặc giá trị null/false hợp lệ, điều kiện `joined > 0` và `n == 0` làm notebook lỗi trước MERGE, khiến RECOMPUTE không thể soft-delete các amenity cũ. Xóa quality gate `if joined and not n`, cho phép DataFrame rỗng đi qua `run_node` và ghi metric `rows=0` vì không có kết quả khớp là trạng thái hợp lệ.

## Lower-severity findings

- P2: 1
- P3: 0
