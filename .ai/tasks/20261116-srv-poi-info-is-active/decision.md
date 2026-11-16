# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-1 | `gld_srv_poi_info.is_active` | Add `gld_srv_poi_info.is_active` BOOLEAN, nullable, immediately after `is_bookable`. `NB_GLD_SRV_POI_INFO` assigns `true` on every row it writes. Do not read it from a source and do not tie it to `deleted_at`. | request.md Constraints | 2026-11-16 |
| D-2 | PostgreSQL `is_active` và `ingestion_ts` | `apps.srv_poi_info.is_active` is a copy of that gold column, boolean, nullable, immediately after `is_bookable`. The user already added the column. Do not run ALTER. Every `apps` table in `sql/postgres/gld_srv_serve.pg.sql` receives `ingestion_ts timestamp without time zone`, nullable, immediately after `deleted_at`. The user already ran `ADD COLUMN ingestion_ts timestamp without time zone`. Do not run ALTER. Do not add `ingestion_ts` to silver or gold. Do not invent a job that writes this column. | request.md Constraints | 2026-11-16 |
| D-3 | Ngoại lệ hợp đồng serving | `tests/test_srv_poi_serving_contract.py` may allow `ingestion_ts` on every apps table even though gold has no such column. `apps.srv_poi_info.is_active` must match `gld_srv_poi_info`. Record this exception in `model-design.md` and `decision.md`. | request.md Constraints | 2026-11-16 |
| D-4 | Entity và JSON API | Entities map every new PostgreSQL column. Do not put `is_active` or `ingestion_ts` into the JSON API or `docs/context/api-mapping/`. | request.md Constraints | 2026-11-16 |
| D-5 | Nơi ghi ngoại lệ D-3 | Record this exception in `model-design.md` and `decision.md`. | request.md Constraints | 2026-11-16 |
| D-6 | Kiểu Java của `ingestion_ts` | Java type follows the mapping for `timestamp without time zone` already used by `deleted_at` (`LocalDateTime deletedAt`; `GOLD_TO_JAVA["TIMESTAMP"]`). | model-design.md Columns | 2026-11-16 |
| D-7 | Mở rộng scope test | Duyệt: Main thêm ba path rồi implement đúng edit list, gồm cell srvactivepy, không sửa poidestpy, không chạy ALTER hay Fabric. | Quyết định của người dùng | 2026-11-16 |
| D-8 | Vị trí `srvactivepy` | Gold `gld_srv_poi_info.is_active BOOLEAN` goes after `is_bookable` in two places: `init_tables` (fresh install) and a new `NB_CREATE_DDL` cell pair `srvactivemd`/`srvactivepy`, appended after `enrmergepy`. `srvactivepy` is schema-only and holds the 30M lock, following the `poidestpy` pattern. `poidestpy` itself is not edited. | architecture.md Main brief Decision | 2026-11-16 |
| D-9 | `row_hash` lần chạy đầu | `NB_GLD_SRV_POI_INFO` emits `F.lit(True).alias("is_active")`. Keep it in `row_hash`: no `hash_exclude`. The first run updates every live row once, which is accepted. | architecture.md Main brief Decision | 2026-11-16 |
| D-10 | Hình `PG_ONLY` | The D-3 test exception is a single `PG_ONLY = {"ingestion_ts": ("timestamp without time zone", "LocalDateTime")}` that every apps table must have. | architecture.md Main brief Decision | 2026-11-16 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Người dùng đã thêm `apps.srv_poi_info.is_active` và `ingestion_ts timestamp without time zone` trên PostgreSQL. Agent không chạy `ALTER`.
- Một task đi tiếp model, architecture, implement, verify, review trong cùng chat. Dừng trước bước Fabric DEV.
- Duyệt: Main thêm ba path rồi implement đúng edit list, gồm cell srvactivepy, không sửa poidestpy, không chạy ALTER hay Fabric.
- Rút EX-REVIEW-01: Main xóa exception và D-11. Review quay về Codex gpt-5.6-sol medium sau 7:51 PM.

## Lịch sử quyết định

- 2026-11-16: Ghi D-1 đến D-4 từ `request.md` Constraints. `ingestion_ts` chỉ ở PostgreSQL. `is_active` của `apps.srv_poi_info` khớp `gld_srv_poi_info`. `apps.srv_poi_media_gallery.is_active` đã có, giữ nguyên.
- 2026-11-16: D-5 đóng câu hỏi model về `AGENTS.md`: ngoại lệ D-3 chỉ ở `model-design.md` và `decision.md`. D-6 chốt `ingestion_ts` là `LocalDateTime`, cùng kiểu với `deleted_at`. Cell `NB_CREATE_DDL`, `row_hash`, và đường load PostgreSQL để Architect quyết.
- 2026-11-16: Người dùng duyệt D-7. D-8, D-9, D-10 chép từ Main brief: cell `srvactivepy` sau `enrmergepy`, `row_hash` gồm `is_active`, ngoại lệ test là `PG_ONLY`.
- 2026-11-16: `tests/test_initial_ddl_contract.py` `test_pl_cadence_patch_cell` cũng khoá đuôi cell. Dịch `[-20:-18]` thành `[-22:-20]` cùng cách với các assert đuôi đã duyệt, nếu không `pytest tests` fail.
- 2026-11-16: D-11, `exceptions` EX-REVIEW-01. Model `claude-opus-5-5`, effort `medium`, runtime `claude-code-extension`. `models.review.expected` giữ `gpt-5.6-sol`. Chưa chạy gate vì `run_review` vẫn gọi Codex.
- 2026-11-16: Người dùng rút EX-REVIEW-01. Xóa exception và dòng D-11. Review quay về Codex `gpt-5.6-sol` medium sau 7:51 PM. Gate chưa chạy.
- 2026-11-16: Người dùng báo Fabric DEV. `srvactivepy` lần đầu `+is_active`, `DESCRIBE` thấy `is_active boolean` ngay sau `is_bookable`, chạy lại `=is_active`. PostgreSQL đúng kỳ vọng. Trigger `PL_VV_TRANS_SLV_TO_GLD_30M` đã tắt. Chưa có pipeline, `count_if`, `lock_exec_id`, hay smoke API. `gates.runtime` giữ `pending`.
- 2026-11-16: `NB_00` `PL_VV_TRANS_SLV_TO_GLD_30M` `p_force_nodes` trống kết thúc `NO_DATA` (0 Dirty Edge, 0 node ứng viên, exec `679e2273-b5f2-4591-8bbf-7450362e832f`). `count_if` dòng sống = 292. Backfill phải ép `p_force_nodes = "gld_srv_poi_info"`. `gates.runtime` giữ `pending`.
- 2026-11-16: Ép `p_force_nodes = "gld_srv_poi_info"`, exec `de0decbc-28a2-436e-8572-9d1d73191da6`, `SUCCESS`, `updated` 292, `inserted` 0. `count_if` dòng sống = 0. Chưa có `lock_exec_id` và smoke API. `gates.runtime` giữ `pending`.
- 2026-11-16: `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` có `lock_exec_id` null, `status` `SUCCESS`, `updated_at` `2026-11-16T13:54:11Z`. Người dùng xác nhận API đã pass. `gates.runtime` = `pass`. Chưa chuyển `ready_to_merge`. Trigger sau backfill chưa được báo.
- 2026-11-16: Người dùng yêu cầu chuyển task sang `ready_to_merge`, commit, và nhận lệnh push. Main không push.
