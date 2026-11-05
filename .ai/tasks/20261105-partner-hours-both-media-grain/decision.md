# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-HOURS-2 | Hai phần tử hours | Với những block có 2 mảng hours, vẫn phải xử lý cả 2. | User 2026-11-05 | 2026-11-05 |
| D-MEDIA-KEY | Grain media | Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất. | User 2026-11-05 | 2026-11-05 |
| D-MEDIA-TIE | Hòa updated_at | Khi nhiều dòng cùng media_id, cùng poi_id và cùng updated_at => Chọn dòng bất kỳ. | User 2026-11-05 | 2026-11-05 |
| D-GALLERY-KEY | Grain gallery | Gallery đổi thành media_id + poi_id như silver. | User 2026-11-05 | 2026-11-05 |
| D-RUN-34516 | Chạy lại GLD 30M | Exec 34516f98-b674-474a-9a66-a7e328431bea SUCCESS, 4/4 node, Tiến 12 cạnh. Info, media và gallery không còn PARTNER_MULTI_HOURS, pk_duplicate, NOT_RUN. | evidence/results/orch-34516f98.txt | 2026-11-05 |
| D-HOURS-ORDER | Thứ tự hai ca | Hai object giờ của một ngày giữ thứ tự trong mảng nguồn, phần tử 0 rồi phần tử 1. Ngày có hơn 2 phần tử vẫn dừng `PARTNER_MULTI_HOURS`. | request.md `## Out of scope`; model-design.md Conflicts 7 | 2026-11-05 |
| D-MEDIA-PARENT | updated_at của phần tử | `updated_at` là cột kỹ thuật extract của đúng dòng cha đã nổ mảng: i18n khi dùng media i18n, services khi fallback, `slv_3p_poi_media` với Google. Null xếp sau mọi giá trị có mốc. | NB_LIB_EXTRACT_RAWDATA TECH_COLUMNS, SNAPSHOT_TECH_COLUMNS | 2026-11-05 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có.

## Sai lệch so với kiến trúc

- GATE-002: Main brief gắn `partner_media_collapsed` vào `.first()` thứ hai của mọi lần chạy. User 2026-11-05: chỉ tính metric khi `DRY_RUN`. `countDistinct` không vào plan của `RUN`.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | null_poi = 0, dup_pair = 0, media_id_many_poi = 0. Lệnh ALTER chạy thành công. gallery_pk là PRIMARY KEY (media_id, poi_id). File sql/postgres/gld_srv_serve.pg.sql được sửa cho khớp. | |
| GATE-003 | P1 | accepted-risk | Ghi accepted-risk, dựa trên hợp đồng extract: cột kỹ thuật updated_at đã là TIMESTAMP. | |
| GATE-002 | P1 | fixed | Chỉ tính metric khi DRY_RUN. `countDistinct` nằm trong `if ctx.mode == "DRY_RUN"` của `partner_media`. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Với những block có 2 mảng hours, vẫn phải xử lý cả 2.
- Với bảng slv_poi_media_info, grain/key sẽ gồm media_id và poi_id. Ở phần DataFrame nguồn sẽ xử lý merge trước, grain/key sẽ gồm media_id và poi_id và lấy theo updated_at lớn nhất.
- Khi nhiều dòng cùng media_id, cùng poi_id và cùng updated_at => Chọn dòng bất kỳ.
- Gallery đổi thành media_id + poi_id như silver.
- Đồng ý mở task mới, nhưng xử lý ngay trong chat này.
- GATE-001. PostgreSQL apps.srv_poi_media_gallery tôi sẽ sửa lại key là media và poi_id. Tôi sẽ tự thao tác.
- GATE-002: Chỉ tính metric khi DRY_RUN.
- GATE-003. Ghi accepted-risk, dựa trên hợp đồng extract: cột kỹ thuật updated_at đã là TIMESTAMP.

## Lịch sử quyết định

- 2026-11-05: Tách từ task `20261104-poi-review-src-and-partner-i18n` sau exec `c2a9f0ef-6d48-4241-b1fb-c9e25eddd4fe`. `PARTNER_MULTI_HOURS` có 8 dòng i18n, mỗi dòng max `hours` = 2. Media có 2 `media_id`, mỗi khóa 3 dòng cùng `poi_id`. Cột `updated_at` dùng cho bước gộp là cột kỹ thuật của extract, không phải `src_updated_at` hay `last_updated_at`.
- 2026-11-05 D-HOURS-ORDER: User nói xử lý cả hai phần tử. Mảng đích có thể dài hơn bảy object. Thứ tự là thứ tự mảng nguồn. Hơn hai phần tử nằm ngoài câu user nên giữ stop hiện tại.
- 2026-11-05 D-MEDIA-PARENT: Không có `proposal.md`. Ledger là căn cứ cho model design. `model-design.md` Conflicts 1 không chặn kiến trúc.
- 2026-11-05: Code đã vào ba notebook và hai mapping. `pytest` 218 passed. Review round 1 `USER_DECISION`: GATE-001 khóa PostgreSQL gallery vẫn `media_id`; GATE-002 `countDistinct` của metric `partner_media_collapsed`. Chưa disposition.
- 2026-11-05 GATE-001: Người dùng tự sửa khóa PostgreSQL `apps.srv_poi_media_gallery`. Disposition `backlog`. GATE-002 chưa disposition. Metric nằm ở `NB_SLV_POI_MEDIA_INFO`, cell `slvmediabuild`, hàm `partner_media`.
- 2026-11-05 GATE-002: User chốt chỉ tính metric khi `DRY_RUN`. `RUN` giữ `partner_url_dropped` và không gọi `countDistinct`.
- 2026-11-05: Review round 2 không lặp GATE-002. Verdict `USER_DECISION`. GATE-001 được nhắc lại vì `backlog` chưa đủ, reviewer muốn `accepted-risk` nếu khóa PostgreSQL chưa đổi trong repo. GATE-003 mới: cast `updated_at` sang timestamp chưa có số liệu kiểu và số cast lỗi. Review đã là vòng 2.
- 2026-11-05 GATE-003: `accepted-risk`. `docs/context/NB_LIB_EXTRACT_RAWDATA.md` mục `TECH_COLUMNS` và `SNAPSHOT_TECH_COLUMNS`: `updated_at` là `TIMESTAMP`. Không probe thêm.
- 2026-11-05 GATE-001: Giao lệnh đổi `apps.srv_poi_media_gallery` từ `PRIMARY KEY (media_id)` sang `(media_id, poi_id)`, sau khi `poi_id` là `NOT NULL`. File `sql/postgres/gld_srv_serve.pg.sql` chưa sửa. Chờ kết quả người dùng.
- 2026-11-05 GATE-001: Người dùng báo null_poi = 0, dup_pair = 0, media_id_many_poi = 0, ALTER thành công, gallery_pk là PRIMARY KEY (media_id, poi_id). Disposition `fixed`. File DDL trong repo sửa cùng nội dung. Review không chạy lại vì đã hết vòng 2.
- 2026-11-05 D-RUN-34516: `p_force_nodes` trống. Ứng viên là info, multi_lang, media, gallery. Review không nằm trong ứng viên. Multi-lang vào vì Dirty Edge `DATA_CHANGED` từ `slv_enr_poi_info_multi_lang`, inserted 0, updated 0. 12 cạnh = 5 info + 3 multi_lang + 3 media + 1 gallery trong seed `NB_SETUP_INITIAL_DDL` cell 7.
