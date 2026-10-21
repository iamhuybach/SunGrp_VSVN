## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp yêu cầu.
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`.
- `risk-gate`: đã hoàn tất.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | Vị trí | Lỗi | Cách sửa |
|---|---|---|---|---|
| STATE-001 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:239` | Entity bị xóa, soft-delete hoặc đổi `poi_id` bị lọc khỏi live spine, nên APPEND không phát removal transition và gold giữ dữ liệu stale sau khi watermark tiến lên. | Thêm transition xóa idempotent bằng tombstone có contract rõ ràng hoặc MERGE/delete trước watermark advancement; kiểm thử delete, re-key, replay và crash giữa target commit với watermark commit. |
| GATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:2332` | `enrinfopy` thêm cạnh active rồi mới tắt cạnh cũ bằng các statement riêng; lỗi giữa chừng có thể để lại routing graph một phần và vẫn nhả lock. | Kiểm tra toàn bộ precondition trước mutation và chuyển graph theo cách atomic/fail-safe, kèm compensation và failure-injection test sau từng mutation. |
| SQL-001 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:239` | Entity, rating, price, hours và i18n tiếng Việt được join mà chưa chứng minh uniqueness, nên dữ liệu trùng có thể nhân dòng và làm node thất bại tại PK guard. | Chứng minh live snapshots duy nhất theo join key hoặc thêm blocking uniqueness assertion; không chọn dòng tùy ý. |
| SPARK-001 | P1 | `notebooks/NB_ENR_POI_INFO.ipynb:226` | Amenity removal detection chạy full-width `old.subtract(current)` trước khi chiếu `poi_id`, có nguy cơ shuffle/spill hoặc timeout trên F16. | Đo trên DEV; nếu spill hoặc quá 5 phút, dùng CDF/deletion-aware processing hoặc chỉ chiếu stable identifiers trước phép trừ. |

P2/P3: `1/0`.

Probe: Trên Fabric DEV, chạy duplicate probe cho năm join inputs và `EXPLAIN FORMATTED` cùng timed `count()` cho amenity snapshot subtraction; PASS chỉ khi không có key trùng, không spill và hoàn tất trong 5 phút.
