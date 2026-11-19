### Model và reviewer manifest

`gpt-5.6-sol` / `medium`. Đã chạy độc lập: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`, `fabric-pipeline-reviewer`; `risk-gate` đã hoàn tất.

### Gate verdict: `FIX_REQUIRED`

- `STATE-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:96`: Khi Google takeover thiếu một child block, parent vẫn có thể đổi sang Google trong khi child SGM cũ tồn tại và các Google event cũ hơn về sau bị guard loại, gây lệch xuyên bảng lâu dài. Fix: chỉ flip parent sau khi mọi child hiện hữu đã được ghi/xóa rõ ràng, hoặc lưu takeover debt theo table/key cho đến khi từng child hoàn tất; thêm test missing-block rồi replay Google cũ hơn.
- `SPARK-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:96`: Forced broadcast toàn bộ owner snapshot và Google key set chưa có bằng chứng an toàn trên F16, có thể gây memory pressure hoặc timeout. Fix: giới hạn owner theo POI của batch và bỏ broadcast hint, hoặc cung cấp DEV plan/size/peak-memory/spill/runtime đạt ngưỡng.
- `SQL-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:119`: `resolve_latest` không có tie-break ổn định khi các event trùng `source_id`, `crawled_at`, `event_id` nhưng khác payload, nên rerun có thể chọn kết quả khác nhau. Fix: thêm payload tie-break/reject conflict xác định, hoặc chứng minh không có conflict bằng probe DEV.

P2/P3: `P2=3`, `P3=0`.

Probe: Trên Fabric DEV, xác nhận `conflicting_duplicate_groups=0` cho SGM theo `(source_name, source_id, crawled_at, event_id)` và ghi nhận kích thước/plan/peak-memory/spill/runtime của cả hai broadcast trên full reload cùng batch 15 phút.
