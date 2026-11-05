# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-SRV-LANG | Cột lang của gold review | Yêu cầu này bỏ lang trên gold. File `sql/postgres/gld_srv_serve.pg.sql` chỉ được nêu trong tác động; chưa sửa ở phase triage. | User 2026-11-04; request.md `## Out of scope` | 2026-11-04 |
| D-SRV-TEXT | title và review_text của gold review | slv_3p_poi_review.title gán là null. gld_srv_poi_review.review_text lấy từ slv_3p_poi_review.text. | User 2026-11-04 | 2026-11-04 |
| D-REINIT | Chạy lại trên Fabric | Có thể xóa bảng và chạy như lần init đầu tiên. | User 2026-11-04 | 2026-11-04 |
| D-GLD-ML | Chạy gold multi-lang cùng lần GLD | Ok tôi muốn việc chạy NB này sẽ thực hiện bởi task 20261104-poi-review-src-and-partner-i18n luôn. | User 2026-11-04 | 2026-11-04 |
| D-RUN-REVIEW | Gold review lần GLD | SUCCESS, không phải lỗi. Insert 109682, updated 0, deactivated 0, trg_version 1. Hai cạnh active đã advance: `slv_3p_poi_review`, `slv_3p_poi_rating`. Cạnh `slv_enr_poi_review_multi_lang` có `is_active = 0`, không nằm trong 5 cạnh advance. | evidence/results/reinit-gld.txt; NB_SETUP_INITIAL_DDL cell 7 | 2026-11-04 |
| D-RUN-ML | Gold multi-lang lần GLD | SUCCESS, khớp D-GLD-ML. Insert 859, updated 0, deactivated 0, trg_version 2. Ba cạnh active đã advance. Task này không chốt số dòng kỳ vọng. | D-GLD-ML; evidence/results/reinit-gld.txt; NB_SETUP_INITIAL_DDL cell 7 | 2026-11-04 |
| D-EDGE-5 | Cạnh đã commit exec c2a9f0ef | Advance đúng 5 cạnh của hai node SUCCESS. Cạnh của node FAILED và NOT_RUN chỉ ghi trạng thái, không đổi version đã đọc. Lần sau không đưa hai node SUCCESS vào `p_force_nodes` nếu không muốn chọn lại. | NB_LIB `advance_edges`; seed cell 7; reinit-gld.txt | 2026-11-04 |
| D-GALLERY | Gallery NOT_RUN | Không phải lỗi riêng. Không có dòng log nên NOT_RUN; cạnh không advance. | reinit-gld.txt; `collect_outcomes` | 2026-11-04 |
| D-HOURS-8 | Hai phần tử hours | Với những block có 2 mảng hours, vẫn phải xử lý cả 2. | User 2026-11-05 | 2026-11-05 |
| D-MEDIA-PK | Grain slv_poi_media_info | Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất. | User 2026-11-05 | 2026-11-05 |

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
- Với những block có 2 mảng hours, vẫn phải xử lý cả 2.
- Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất.
- Khi nhiều dòng cùng media_id, cùng poi_id và cùng updated_at => Chọn dòng bất kỳ.
- Gallery đổi thành media_id + poi_id như silver.
- Đồng ý mở task mới: `20261105-partner-hours-both-media-grain`.

## Lịch sử quyết định

- 2026-11-04 D-SRV-LANG: Ledger task `20261029-pg-ddl-gld-srv-serve` quyết định D-LANG giữ `gld_srv_poi_review.lang` và không tạo `lang` trên PostgreSQL `apps.srv_poi_review`. Yêu cầu 2026-11-04 bỏ `lang` trên gold. File PostgreSQL chưa sửa trong phase triage.
- 2026-11-04 D-SRV-TEXT: `slv_3p_poi_review` không có cột `title` và không có cột `review_text`. Người dùng chốt `title` gán null và `review_text` lấy từ cột `text`. Không thêm cột `title` vào bảng nguồn.
- 2026-11-04 D-REINIT: Người dùng cho phép xóa bảng và chạy lại như init. Không dùng `DROP COLUMNS` của S1. Seed `NB_SETUP_INITIAL_DDL` chỉ INSERT khi chưa có khóa, nên `is_active` của cạnh đã có phải UPDATE trước khi seed.
- 2026-11-04 D-GLD-ML: Lần chạy `NB_GLD_SRV_POI_MULTI_LANG` thuộc task này. `p_force_nodes` thêm `gld_srv_poi_multi_lang` cạnh `gld_srv_poi_review`. Trước orchestrator, chạy cell `mlsrcpy` của `NB_CREATE_DDL` một lần để thêm cột `source_name`.
- 2026-11-04 D-RUN-REVIEW, D-RUN-ML, D-EDGE-5, D-GALLERY: Exec `c2a9f0ef-6d48-4241-b1fb-c9e25eddd4fe`, `PARTIAL_FAILED`, log `Tiến 5 cạnh`. `advance_edges` chỉ advance cạnh của node `SUCCESS` hoặc `NO_DATA` khi `src_versions` có version. Seed active: review 2 cạnh (`slv_3p_poi_review`, `slv_3p_poi_rating`), multi-lang 3 cạnh (`slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`, `slv_pn_business_service_i18ns`). 2+3=5. Info 5 cạnh, media 3 cạnh, gallery 1 cạnh không advance. `NB_GLD_SRV_POI_INFO` và `NB_SLV_POI_MEDIA_INFO` không nằm trong `scope.files`. Review round đã là 2.
- 2026-11-04 D-HOURS-8: `partner_hours` trả `PARTNER_MULTI_HOURS` khi một ngày có `len(hours) > 1`. Entity ghi `opening_hours_text` từ `$.policies.operating_hours` của cả khối `coalesce(i18n.amentities, svc.amentities)`. Probe 2026-10-24 không đo độ dài mảng `hours`. Chưa có khóa của 8 dòng nên chưa kết luận khối i18n hay dữ liệu cũ.
- 2026-11-04 D-MEDIA-PK: `quality_gate` đếm số giá trị khóa có `count > 1`. Khóa MERGE là `media_id`. Google dùng `media_dedup_key`. Partner dùng `sha2(partner|poi_id|trim(url))`; mảng lấy từ i18n `vi` khi không rỗng, ngược lại từ `slv_pn_business_services.media`. Nhánh amenities của entity không ghi bảng này. Chưa có khóa nên chưa kết luận nguồn.
- 2026-11-05 D-HOURS-8: Probe `fail_rows 8`. Cả 8 có `vi_rows=1`, `svc_rows=1`, `chosen=i18n`, `hours_entity=2`, `hours_i18n=2`. `hours_svc` NULL ở `c1cc9bf6-656a-4390-8c6d-e4f301fbcdef`, `2114384b-2231-40b5-b3da-522c8e64f420`, `8df8d89e-4a89-454f-a8ed-78c84fd68288`, `4e7d4dca-9257-4a01-947a-745d7024dbac`, `fcf56a51-2d46-424b-8dba-99bfb678ffe2`, `f8cf9645-85ac-415d-b2e5-4afb1781910a`. `hours_svc=2` ở `2c94c9da-5a31-489b-ae86-1214483b7a98` và `1d10f1ad-dbc6-4f81-8ba1-c638fb1bda53`. Commit `e6f86b3` đổi coalesce, nhưng câu cũ là giờ lấy từ i18n `vi`, không lấy của svc. Tám dòng này vẫn đọc khối i18n. Gate nằm ở `NB_GLD_SRV_POI_INFO`, file không có trong commit và không có trong `scope.files`.
- 2026-11-05 D-MEDIA-PK: Probe `dup_keys 2`. Khóa `2eb9db73…850cf76` / `poi_id fdfba9de-c001-22d8-b240-8ff8fa79541b` / `business_service_id 941cd626-8d08-496c-a739-b57f077c0ea2`, và khóa `930e048b…e21addbd` / `poi_id 2cf23f28-d1f2-9e97-cc6e-69a1043ab59e` / `business_service_id 48a636f9-52ef-4071-877a-f40a69e16b7b`. Mỗi khóa một dòng `origin=i18n`, `rows=3`. Probe gộp theo khóa nên không tách ba phần tử cùng url trong một mảng với ba dòng `vi`. Cả hai cơ chế đều nằm ở `slv_pn_business_service_i18ns`. `NB_SLV_POI_MEDIA_INFO` không có trong `e6f86b3`.
- 2026-11-05 D-HOURS-8: Người dùng chốt xử lý cả hai phần tử khi một block có 2 mảng hours. Bản ghi đã dán có `monday.hours` dài 2: `08:00`–`09:00` và `11:00`–`22:00`. Chưa sửa `NB_GLD_SRV_POI_INFO`.
- 2026-11-05 D-MEDIA-PK: Người dùng chốt grain `media_id` + `poi_id`, gộp DataFrame nguồn theo grain đó và giữ `updated_at` lớn nhất. Hai khóa probe đã cùng cả hai cột, mỗi khóa 3 dòng. Build hiện không có `updated_at`. Gallery vẫn khóa một cột `media_id`. Chưa sửa notebook.
- 2026-11-05: Khi hòa `updated_at`, chọn dòng bất kỳ. Gallery dùng `media_id` + `poi_id`. Việc sửa code chuyển sang task `20261105-partner-hours-both-media-grain`. Task này không sửa notebook.
