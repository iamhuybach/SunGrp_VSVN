## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium` — khớp cấu hình.
- Reviewers: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`, `api-contract-reviewer`, `jpa-performance-reviewer`.
- `risk-gate`: completed.

## Gate verdict: `USER_DECISION`

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| GATE-001 | P0 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:117` | State dùng thời gian thay cho `version`, nên event version cao đến muộn có thể bị loại vĩnh viễn. | Sắp thứ tự bằng `version`, `EventProcessedUtcTime`, `event_id` và kiểm thử replay hai lần. |
| GATE-002 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:117,232` | Các tên `sources`, `TABLE_SOURCE`, `_crawled_at` không tồn tại làm notebook lỗi trước khi xử lý. | Loại source routing cũ; dùng `TABLE_EVENT_TYPE` và `_event_processed_at` nhất quán. |
| GATE-003 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:164` | Projection làm mất `_src_version`, khiến bước chọn bản ghi mới nhất lỗi trước MERGE. | Giữ `_src_version` xuyên suốt projection, state và MERGE. |
| GATE-004 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:164` | JSON `destinations` lỗi bị chuyển thành NULL mà không kích hoạt fail gate. | Thêm cờ parse failure và đưa vào reject/fail policy. |
| GATE-005 | P1 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:117,164` | `event_id` rỗng hoặc tie toàn bộ tuple làm kết quả `row_number()` không xác định. | Reject ID rỗng và fail tie xung đột, hoặc thêm tie-breaker được phê duyệt. |
| GATE-006 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5967,5990` | Crash sau overwrite có thể khiến retry trả `SKIP` cho rewrite chưa được kiểm chứng. | Lưu version/phase migration và resume validation hoặc RESTORE trước `SKIP`. |
| GATE-007 | P1 | `notebooks/NB_CREATE_DDL.ipynb:5967,5990`; `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb:23` | Lease 120 phút không heartbeat trong khi extract có thể chạy 780 phút, cho phép stale owner tiếp tục ghi. | Heartbeat, revalidate ownership trước mọi durable write/RESTORE và đồng bộ timeout. |
| GATE-008 | P1 | `.ai/tasks/20261116-enr-lang-destination-from-bronze/runtime-runbook.md:34` | Copy Job truncate-first không thể pause có thể xóa dữ liệu PostgreSQL rồi lỗi vì schema lệch. | Người dùng phải chọn pause job hoặc staging + atomic swap; nếu không phải quyết định chấp nhận rủi ro rõ ràng. |
| GATE-009 | P1 | `notebooks/NB_CREATE_DDL.ipynb:299` | Thiếu dấu phẩy giữa các tuple `FROM VALUES` làm seed watermark lỗi cú pháp. | Thêm dấu phẩy và chạy lại deterministic validation. |

P2: 6. P3: 0.

Probe: `WITH g AS (SELECT poi_id,event_type,version,EventProcessedUtcTime,event_id,COUNT(DISTINCT data) payload_variants FROM lh_vv_bronze.dbo.brz_enrichment_result GROUP BY poi_id,event_type,version,EventProcessedUtcTime,event_id) SELECT * FROM g WHERE event_id IS NULL OR trim(event_id)='' OR payload_variants>1 LIMIT 50;`
