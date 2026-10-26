## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — đúng yêu cầu.
- Specialists: `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`, `fabric-pipeline-reviewer`.
- `risk-gate`: completed.

## Gate verdict: `FIX_REQUIRED`

| ID | Severity | file:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P0 | `notebooks/NB_CREATE_DDL.ipynb:4124`; `notebooks/NB_SETUP_POI_ENTITY.ipynb:944`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:732` | Setup có thể tạo `wm_flow__<new>` giữa precheck và rename; do Delta không bảo đảm uniqueness, migration có thể commit dòng trùng rồi mới phát hiện corruption. | Serialize cả `old_id` và `new_id` hoặc dùng protocol tạo/rename conflict-safe dùng chung cho mọi writer; thêm concurrency test chứng minh luôn còn tối đa một dòng mới. |
| GATE-002 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4102`, `:4177` | Duplicate logical key sẵn có trong cùng old/new `pl_name` chỉ bị phát hiện sau khi `UPDATE CFG` đã commit. | Trước mọi write, group cả hai tên theo complete logical key và dừng nếu bất kỳ nhóm nào có `count(*) > 1`. |
| GATE-003 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4089`, `:4168`, `:4198` | Watermark malformed hoặc crash sau CFG commit có thể để new lock còn giữ, nhưng rerun fast path vẫn báo hội tụ mà không kiểm tra hoặc recovery. | Cả pre-write và idempotent path phải xác nhận đúng một cặp `watermark_id`/`src_tbl`, yêu cầu lock-free, dừng với live owner và guarded-recover expired owner; thêm crash-recovery test. |

P2/P3: `1/0`.

Không cần probe bổ sung để chứng minh các lỗi này; runtime evidence chỉ cần sau remediation.
