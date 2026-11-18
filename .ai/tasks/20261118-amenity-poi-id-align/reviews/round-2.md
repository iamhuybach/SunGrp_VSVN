## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — confirmed.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`.
- Risk gate: not required.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| SQL-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2211,2233,2260` | Edge hiện hữu với `load_mode != 'RECOMPUTE'` vẫn có thể được kích hoạt và vượt post-check. | Đặt hoặc kiểm tra `load_mode = 'RECOMPUTE'`, đồng thời xác nhận trường này trong post-check. |
| SQL-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2176,2211` | Hai edge vật lý trùng nhau tạo một kết quả `n=2`, nhưng guard `len(hits) == 1` vẫn cho phép ghi. | Trước mọi write, yêu cầu `len(hits) == 1` và `hits[0]['n'] == 1`. |
| SPARK-001 | P1 | `notebooks/NB_SLV_POI_AMENITY.ipynb:292` | Hai `collect()` không giới hạn có thể làm cạn bộ nhớ driver trên Fabric F16 trước quality gate hoặc write. | Phát hiện duplicate bằng `groupBy`/join phân tán; chỉ collect mẫu xác định với `orderBy(...).limit(20)`. |

P2/P3: 0.

Không có file thay đổi hoặc disposition hợp lệ kể từ vòng 1, nên cả ba finding vẫn chưa được xử lý.
