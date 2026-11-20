# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-01 | Chỗ đặt bảng map và init một lần | Bảng map ở `lh_vv_gold`, tiền tố `gld_`, một dòng mỗi `poi_id` cũ. Init một lần từ gold cũ sang gold mới. Chỉ notebook init được đọc gold khác. Pipeline định kỳ không đọc đường này. | request.md User outcome | 2026-11-19 |
| D-02 | Bảng POI cũ không có gold mới | Chỉ điền cột đã có cặp với bảng `gld_srv_*` hiện có. Cột không có cặp không điền. Không tạo bảng nghiệp vụ mới. Áp cho `ai_poi`, `ai_poi_rating`, `ai_poi_review`, `ai_enriched_poi`, `poi_enrichment_display`, `poi_address_enrichment_staging`, `poi_rating`. | Người dùng, 2026-11-19 | 2026-11-19 |
| D-03 | Hai workspace | Model cũ đọc và ghi ở workspace `sgr_visitvn_prd_batch`. Model mới đọc và ghi ở workspace `sgr_visitvn_dev`. Cùng tenant, cả hai đều có quyền đọc và viết. Mọi script kiểm tra dùng tên đủ `workspace.lakehouse.schema.table`. Lakehouse vẫn là `lh_vv_gold` và `lh_vv_silver`, schema `dbo`. | Người dùng, 2026-11-19 | 2026-11-19 |
| D-04 | Hai writer trên `gld_srv_*` | Phương án B. Thêm cột kỹ thuật `load_origin` STRING trên `gld_srv_poi_info`, `gld_srv_poi_multi_lang`, `gld_srv_poi_review`. Init ghi `LEGACY_INIT`. Lib chỉ xóa mềm dòng `load_origin` NULL. Lần MATCHED đầu của pipeline đặt `load_origin` về NULL. Dòng pipeline không sinh ra thì giữ đến khi pipeline sinh đúng khóa. Không có đợt xóa riêng. | Người dùng, 2026-11-19 | 2026-11-19 |
| D-05 | Tên map và notebook init | Bảng map `lh_vv_gold.dbo.gld_poi_legacy_id_map`. Notebook một lần `NB_SETUP_LEGACY_GOLD_POI`. Không gắn pipeline 15 phút. | model-design.md sau D-04 | 2026-11-19 |
| D-06 | `poi_name` và `district` nhiều lang | Lấy hai cột từ dòng `poi_master` có `lang = vi` của cùng `source_id`. Không chọn lang khác. Không có dòng `vi` thì hai cột NULL, vẫn ghi dòng info khi các cột đã cặp còn lại không khác nhau giữa các lang. | Người dùng, 2026-11-19 | 2026-11-19 |
| D-07 | Nạp đủ cột có nguồn | Người dùng yêu cầu nạp toàn bộ field. Init lấy các cột có nguồn trong gold cũ (địa chỉ, liên hệ, giờ, destination, cover, experience, review, media). Cập nhật dòng `load_origin = LEGACY_INIT`. Không sửa dòng pipeline. Amenity theo D-08. Media không có `photo_api_uri`, kích thước, photographer, thumbnail. | Người dùng, 2026-11-20 | 2026-11-20 |
| D-08 | Amenity từ enum và từ điển | Lấy enum của `poi_detail.amenities_json` (dòng `lang = vi`) và `business_sector` của `poi_master`. Khớp `ref_dictionary_amenities` cùng `source_name` và `business_sector`: chuỗi enum bằng `amenity_raw`, `amenity_en` hoặc `amenity_vi`; cờ `true` khớp `amenity_raw` bằng đường dẫn JSON. Một enum khớp nhiều dòng thì bỏ. `load_origin` trên `gld_srv_poi_amenity` giữ dòng init khỏi pipeline 1 giờ. | Người dùng, 2026-11-20 | 2026-11-20 |
| D-09 | `load_origin` trên media | Thêm `load_origin` STRING cho `gld_srv_poi_media_gallery`. `NB_GLD_SRV_POI_MEDIA_GALLERY` không sửa code: `run_node` thấy cột thì không xóa mềm dòng `LEGACY_INIT` và bàn giao khi MATCHED. Init ghi `LEGACY_INIT`. Dòng init đã chèn khi bảng chưa có cột được gắn `LEGACY_INIT` nếu `row_hash` khớp. | Người dùng, 2026-11-20 | 2026-11-20 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Một `source_id` partner có hai `poi_id` cùng lang `vi`: `32895ee7-d6e9-4a95-b40a-f7f3d1385065`. Bảng map giữ cả hai. Dòng info không ghi khi payload còn lại khác nhau.

## Sai lệch so với kiến trúc

- Không có.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| GATE-001 | P1 | fixed | Drift chỉ tính dòng đã ghi bị thiếu nguồn hoặc lệch field. Dòng chỉ có ở nguồn vẫn là insert. Map rỗng không còn drift. | |
| GATE-002 | P1 | fixed | `to_insert` và parent bỏ mọi khóa đã có, kể cả `deleted_at` khác NULL. Vòng 2 xác nhận đóng. | |
| GATE-003 | P1 | fixed | Dừng khi `legacy_poi_id` trùng trên map nguồn hoặc map đã ghi. Vòng 2 xác nhận đóng. | |
| GATE-004 | P1 | accepted-risk | Người dùng chấp nhận 2026-11-20. Lỗi đọc history sau MERGE có thể che kết quả ghi. Chạy lại cùng pin không nhân dòng vì MERGE chỉ INSERT. | |
| GATE-005 | P1 | accepted-risk | Người dùng chấp nhận 2026-11-20. Lỗi nhả khóa sau ghi thành công có thể để khóa luồng tới hết lease 90 phút. Exit vẫn có thể là SUCCESS. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Đã chốt: map ở gold; init một lần; `partner_portal` thành `partner`; không hash lang; không dùng `poi_uid`.
- Đã chốt D-02 (2026-11-19): chỉ điền cột đã có cặp với `gld_srv_*` hiện có. Cột không có cặp để trống. Không tạo bảng mới.
- Đã chốt D-04 (2026-11-19): phương án B. Dòng chỉ có từ gold cũ ở lại đến khi pipeline sinh đúng khóa. Không có lệnh dọn riêng.
- D-05: bảng map `gld_poi_legacy_id_map`, notebook `NB_SETUP_LEGACY_GOLD_POI`.
- Đã chốt D-06 (2026-11-19): `poi_name` và `district` lấy từ dòng `lang = vi`.
- Đã chấp nhận rủi ro GATE-004 và GATE-005 (2026-11-20): "Accept risk".
- PLAN 2026-11-20, pins `poi_master` 7011 và `poi_enrichment_display` 5706. Chưa duyệt RUN vì `old_inactive_n` = 2601.
- 2026-11-20: "duyệt RUN và chấp nhận dòng mới ghi is_active = true".
- 2026-11-20: RUN đầu lỗi ở stage map. `operationMetrics` là dict, `json.loads` ném TypeError. Phân loại `code`. Đã sửa `_metrics` nhận dict hoặc chuỗi, và lỗi nhả khóa sau SUCCESS thì raise.

## Lịch sử quyết định

- 2026-11-19: mở D-01 theo yêu cầu. D-02 để trống cho tới khi có lựa chọn.
- 2026-11-19: D-03. Người dùng chốt model cũ ở `sgr_visitvn_prd_batch`, model mới ở `sgr_visitvn_dev`. Probe bỏ tên tắt `lh_vv_gold`.
- 2026-11-19: probe `legacy_gold_poi_profile` trả về. `gates.evidence` = pass. D-02 chờ chọn.
- 2026-11-19: người dùng chọn D-02, chỉ điền cột đã có cặp với `gld_srv_*` hiện có.
- 2026-11-19: `run-author --kind model` rồi `run-gate`. Architect trả `EVIDENCE_REQUIRED` và kết luận hai writer không tách được nếu không đổi MERGE định kỳ. D-04 chờ người dùng. Chưa sửa code.
- 2026-11-19: người dùng chọn D-04 phương án B. Dòng `LEGACY_INIT` mà pipeline không sinh thì giữ đến khi pipeline sinh đúng khóa.
- 2026-11-19: chạy lại `run-author --kind model`. Bản đầy đủ thay `model-design.md`. D-05 ghi tên map và notebook. Chưa chạy lại Architect.
- 2026-11-19: P1, P4, P5, P7 có kết quả. P2 lỗi `uuid_format`; probe đổi sang `regexp_replace(md5(...))`. P4: 32883/45514 id google khác `poi_name` giữa các lang.
- 2026-11-19: người dùng chọn D-06, lấy `poi_name` và `district` từ dòng `lang = vi`.
- 2026-11-19: P2. Info đã có 19594/45521 google và 151/155 partner. Multi-lang đã có 58536/136315 google và 436/448 partner. Không có dòng xóa mềm.
- 2026-11-20: người dùng "Accept risk" cho GATE-004 và GATE-005. Hai gate review đóng bằng accepted-risk. Chưa chạy Fabric.
