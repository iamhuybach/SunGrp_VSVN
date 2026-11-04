# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-SRV-LANG | Cột lang của gold review | Yêu cầu này bỏ lang trên gold. File `sql/postgres/gld_srv_serve.pg.sql` chỉ được nêu trong tác động; chưa sửa ở phase triage. | User 2026-11-04; request.md `## Out of scope` | 2026-11-04 |
| D-SRV-TEXT | title và review_text của gold review | slv_3p_poi_review.title gán là null. gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text. | User 2026-11-04 | 2026-11-04 |
| D-REINIT | Chạy lại trên Fabric | Có thể xóa bảng và chạy như lần init đầu tiên. | User 2026-11-04 | 2026-11-04 |
| D-GLD-ML | Chạy gold multi-lang cùng lần GLD | Ok tôi muốn việc chạy NB này sẽ thực hiện bởi task 20261104-poi-review-src-and-partner-i18n luôn. | User 2026-11-04 | 2026-11-04 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- GATE-001, GATE-002 (review round 1): hai cell `rvi18nenrpy` và `rvi18ngldpy` từ chối cạnh lạ mọi `is_active` trước khi ghi. Nhả khoá theo `lock_exec_id` cả khi câu đọc chủ khoá lỗi sau UPDATE; lỗi nhả khoá không che lỗi gốc (`raise failed from cleanup_exc`).

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | Cạnh lạ mọi is_active bị từ chối trước UPDATE ctrl. | |
| GATE-002 | P1 | fixed | `owns_lock` bật ngay sau UPDATE khoá; finally nhả theo token và giữ lỗi gốc. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- slv_3p_poi_review.title gán là null
- gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text

## Lịch sử quyết định

- 2026-11-04 D-SRV-LANG: Ledger task `20261029-pg-ddl-gld-srv-serve` quyết định D-LANG giữ `gld_srv_poi_review.lang` và không tạo `lang` trên PostgreSQL `apps.srv_poi_review`. Yêu cầu 2026-11-04 bỏ `lang` trên gold. File PostgreSQL chưa sửa trong phase triage.
- 2026-11-04 D-SRV-TEXT: `slv_3p_poi_review` không có cột `title` và không có cột `review_text`. Người dùng chốt `title` gán null và `review_text` lấy từ cột `text`. Không thêm cột `title` vào bảng nguồn.
- 2026-11-04 D-REINIT: Người dùng cho phép xóa bảng và chạy lại như init. Không dùng `DROP COLUMNS` của S1. Seed `NB_SETUP_INITIAL_DDL` chỉ INSERT khi chưa có khóa, nên `is_active` của cạnh đã có phải UPDATE trước khi seed.
- 2026-11-04 D-GLD-ML: Lần chạy `NB_GLD_SRV_POI_MULTI_LANG` thuộc task này. `p_force_nodes` thêm `gld_srv_poi_multi_lang` cạnh `gld_srv_poi_review`. Trước orchestrator, chạy cell `mlsrcpy` của `NB_CREATE_DDL` một lần để thêm cột `source_name`.
