## Model và reviewer manifest

`gpt-5.6-sol`, reasoning `medium`. Đã chạy độc lập: state-correctness, spark-runtime, sql-data, fabric-pipeline; risk-gate đã hoàn tất.

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P0 | `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:96,187` | Với `table_filter`, Google trên POI đang thuộc `sgm` không được đánh takeover nhưng vẫn có thể cập nhật target/state; nếu parent đổi sang Google thì lần chạy unfiltered sau không còn nhận diện takeover, gây phân kỳ liên bảng không tự phục hồi. | Xác định takeover candidate độc lập với `table_filter`; filtered run phải defer/fail trước mọi target, state và watermark mutation, rồi thêm test parent-only/child-only cho cả Google mới hơn và cũ hơn. |
| GATE-002 | P1 | `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:23,119,187` | `state_key='row'` vẫn hợp lệ nhưng reset chỉ xóa `entity_key=poi_id`, nên row-state `sgm` có thể tồn tại và khiến Google hợp lệ sau takeover bị đánh stale. | Fail closed trong `check_config` khi `state_key != 'doc'` cho luồng `sgm/google`, hoặc reset đầy đủ row-state; thêm contract test cho cấu hình row-state. |

`PIPE-001` đã được xác nhận fixed. P2/P3: `1/0`. Không thiếu evidence để kết luận hai lỗi tĩnh này.
