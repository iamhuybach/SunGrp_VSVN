## Model và reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Reviewers: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`, `fabric-pipeline-reviewer`.
- Risk gate: hoàn tất.
- Carry-over: `STATE-001` và `SQL-001` tiếp tục là `rejected-false-positive`; `SPARK-001` đã được sửa.

## Gate verdict

`FIX_REQUIRED`

## P0/P1

- `PIPE-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:187`: Một wave `sgm` thông thường có thể ghi thành công bảng con nhưng thất bại ở `slv_3p_poi`; Google cũ hơn ở lần retry không được nhận diện là takeover, nên state/MERGE guard có thể để dữ liệu parent Google và child SGM lệch lâu dài. Fix: chạy và gate `slv_3p_poi` trước các bảng con cho wave `sgm`, hoặc lưu ownership độc lập/atomic; thêm test parent-failure/child-success rồi replay Google cũ hơn để chứng minh mọi bảng hội tụ.

## P2/P3

- P2: 1; P3: 0.
