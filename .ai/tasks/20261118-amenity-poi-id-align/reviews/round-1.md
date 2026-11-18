## Model và reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`.
- Risk gate: không yêu cầu, không chạy.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| SQL-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2211`, `:2233`, `:2260` | Edge đã tồn tại với `load_mode != 'RECOMPUTE'` có thể được kích hoạt mà không sửa mode, trong khi post-check vẫn báo thành công. | Kiểm tra hoặc cập nhật `load_mode` thành `RECOMPUTE`, rồi đưa trường này vào post-check. |
| SQL-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2176`, `:2211` | Hai edge vật lý trùng nhau bị gom thành một dòng `n=2`, khiến guard `len(hits) == 1` không chặn trước khi ghi. | Trước mọi write, yêu cầu `len(hits) == 1` và `hits[0]['n'] == 1`. |
| SPARK-001 | P1 | `notebooks/NB_SLV_POI_AMENITY.ipynb:292` | Hai `collect()` không giới hạn đưa toàn bộ dictionary key và nhãn sống lên driver, có thể làm cạn bộ nhớ Fabric F16 trước quality gate/write. | Phát hiện duplicate bằng phép `groupBy`/join phân tán và chỉ collect diagnostic sample có `orderBy(...).limit(20)`. |

P2/P3: **1/0**.
