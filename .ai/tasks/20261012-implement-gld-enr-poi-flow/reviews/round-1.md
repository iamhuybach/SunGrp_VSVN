## Model và reviewer manifest

`gpt-5.6-sol`, reasoning `medium`. Đã chạy độc lập: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, `fabric-pipeline-reviewer`; `risk-gate` đã hoàn tất.

## Gate verdict: `FIX_REQUIRED`

- `GATE-001` — P1 — `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1573`: Nhánh APPEND bỏ qua kiểm tra `required_inputs`, nên nguồn bắt buộc rỗng có thể trả `SUCCESS` và làm watermark tiến sai. Sửa bằng cách kiểm tra mọi input bắt buộc trước APPEND và thêm test bảo đảm không ghi hoặc tiến watermark khi input rỗng.
- `GATE-002` — P1 — `notebooks/NB_CREATE_DDL.ipynb:1907`; `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1373`: Kiểm tra schema không xác nhận đầy đủ nullability và hai timestamp kỹ thuật, nên schema sai hợp đồng vẫn có thể vượt qua validation. Sửa bằng cách so sánh schema có thứ tự đầy đủ, gồm tên, kiểu, `created_at`, `updated_at` và nullability của khóa.
- `GATE-003` — P1 — `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1038`: `subtract` và `persist` là lazy, nên lỗi baseline đã bị VACUUM chỉ xuất hiện ngoài khối fallback và khiến node không thể phục hồi. Sửa bằng cách materialize phép diff trong khối được bảo vệ, unpersist khi lỗi và materialize lại snapshot hiện tại theo `FULL_VERSION_UNAVAILABLE`.
- `GATE-004` — P1 — `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/PL_VV_TRANS_SLV_TO_ENR_15P.json:25`: Pipeline còn `PENDING_FABRIC_NOTEBOOK_ID` và workspace ID cố định, nên deployment có thể không gọi được orchestrator. Sửa bằng binding theo môi trường và validation từ chối placeholder hoặc ID sai môi trường.

P2/P3: 5 P2 / 1 P3 theo tổng thô của specialists; chưa thể deduplicate vì risk gate không nhận chi tiết các finding mức thấp.

Probe: Trong Fabric DEV, xác nhận `userMetadata` nằm nguyên tử trong chính APPEND commit và fault-injection không tạo batch trùng; đồng thời xác nhận `runMultiple` được Fabric chấp nhận và timeout phút 32 hủy toàn bộ child notebooks trước khi lock hết hạn phút 35.
