## Model và reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium` — khớp yêu cầu.
- Reviewers: `fabric-pipeline-reviewer`, `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`.
- Risk gate: đã hoàn tất.

## Gate verdict: `FIX_REQUIRED`

- `GATE-001` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:942`, `notebooks/NB_SETUP_POI_AMENITY.ipynb:730`, `notebooks/NB_CREATE_DDL.ipynb:2433`: lease setup 90 phút có thể bị contender dùng ngưỡng 35 phút chiếm khi setup vẫn chạy, phá vỡ mutual exclusion. Fix: dùng một lease tương thích hoặc heartbeat/explicit expiry cho mọi lock owner và thêm concurrency test.
- `GATE-002` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2593`: retained info-edge set chỉ được kiểm tra sau hai `DELETE`, nên patch có thể ghi rồi mới phát hiện trạng thái sai. Fix: kiểm tra đầy đủ retained info edges trước `DELETE` đầu tiên và giữ post-check.
- `GATE-003` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2496`: `_info_edges()` bỏ qua `src_schema` và full logical key, nên cạnh đúng tên bảng nhưng sai schema vẫn có thể vượt kiểm tra. Fix: so sánh đủ khóa `(pl_name, src_schema, src_tbl, trg_schema, trg_tbl)`.
- `GATE-004` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2566`, `notebooks/NB_SETUP_POI_ENTITY.ipynb:845`, `notebooks/NB_SETUP_POI_AMENITY.ipynb:646`: SQL three-valued logic cho phép owner hoặc key chứa `NULL` thoát khỏi các predicate `=`/`<>` trước ghi. Fix: từ chối `NULL` trong toàn bộ owner/logical-key columns hoặc dùng predicate null-safe và thêm test tương ứng.
- `GATE-005` — P1 — `notebooks/NB_CREATE_DDL.ipynb:2621`: một optimistic-concurrency conflict ở lệnh release lock duy nhất có thể để lock ở trạng thái `RUNNING` và chặn R4 tới khi lease hết hạn. Fix: release bằng bounded Delta retry và cung cấp recovery rõ ràng khi retry cạn.

P2/P3: 0.
