## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`
- Risk gate: completed

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

- `SQL-001` — P1 — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:538`: D-06 đã được triển khai, nhưng chưa chứng minh các candidate đứng đầu không đồng hạng về `created_at` và `legacy_poi_id` trong khi khác `source_name`, khiến `row_number()` có thể chọn không ổn định và làm thay đổi dữ liệu Gold giữa các lần chạy. Chạy probe xác nhận không có tie khác `source_name`; nếu có, thêm conflict guard hoặc một tie-breaker cuối đã được người dùng phê duyệt.

`SQL-002` không tái diễn.

## P2/P3

P2: 1; P3: 0.

## Probe

Join `vi_rows` với `arrived`, dùng `dense_rank()` theo đúng D-06, giữ rank 1, rồi đếm distinct null-safe `source_name` theo `_new`; đạt khi không có group nào có count lớn hơn 1.
