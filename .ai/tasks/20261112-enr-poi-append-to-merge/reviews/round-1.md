## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- Reviewers: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`
- Risk gate: completed

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| STATE-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5776` | Một lần refresh trước vòng lặp không bảo đảm quyền sở hữu lease trước từng `ALTER TABLE`, cho phép stale owner ghi bảng thứ hai. | Đặt `_refresh_lock()` ngay trước mỗi `ALTER`, giữ refresh trước UPDATE config và kiểm thử đúng vị trí. |
| SPARK-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5804` | Cleanup lock trong `finally` có thể che lỗi gốc và để pipeline bị khóa tới khi lease hết hạn. | Bọc cleanup bằng `try/except`, bảo toàn lỗi gốc và thêm test cho cả body-failure lẫn cleanup-failure. |
| SQL-001 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:164` | Null/trùng `poi_id` ở entity hoặc nhiều rating/price trên một key có thể nhân bản nguồn và làm PK/MERGE gate thất bại. | Chứng minh các nguồn duy nhất bằng probe hoặc lọc/deduplicate có thứ tự xác định. |
| SQL-002 | P1 | `notebooks/NB_ENR_POI_REVIEW.ipynb:103` | `rv_all` chỉ loại key null, không xử lý nhiều dòng cùng `review_id`, nên MERGE có thể nhận nguồn không duy nhất. | Chứng minh `review_id` duy nhất hoặc chọn một dòng xác định cho mỗi key. |
| SPARK-002 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:160` | Full snapshot mỗi 15 phút chưa có bằng chứng đáp ứng shared F16 và SLA, có nguy cơ spill, throttling, OOM hoặc backlog. | Chạy DEV `DRY_RUN` khi schedule tạm dừng và thu duration, rows/bytes, shuffle, spill, peak memory và capacity utilization. |

P2/P3: **1/0**.

Probe: Trên Fabric DEV, trả về năm count về null/trùng entity, rating, price và review — tất cả phải bằng `0` — đồng thời chạy một paused-schedule info `DRY_RUN` dưới 15 phút, không OOM/throttling/prolonged spill.
