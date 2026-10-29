# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-TYPE | Ánh xạ kiểu | STRING → text, BOOLEAN → boolean, INT → integer, DOUBLE → double precision, DECIMAL(p,s) → numeric(p,s), TIMESTAMP → timestamp without time zone. BIGINT sẽ là INT8. Kiểu khác: MISSING, không bịa varchar(n) hay timestamptz. | request.md Acceptance criteria; User 2026-10-29 | 2026-10-29 |
| D-SCHEMA | Tên schema PostgreSQL | Tên schema: apps. | User 2026-10-29 | 2026-10-29 |
| D-NAME | Tên bảng PostgreSQL | Tên bảng tiền tố bỏ gld_; Bắt đầu bằng srv_. `apps.srv_poi_info`, `apps.srv_poi_multi_lang`, `apps.srv_poi_amenity`, `apps.srv_poi_media_gallery`, `apps.srv_poi_review`. | User 2026-10-29 | 2026-10-29 |
| D-LANG | Cột lang của review | review_id bỏ field lang. Bảng PostgreSQL `apps.srv_poi_review` (pk `review_id`) không có cột `lang`. Gold `gld_srv_poi_review.lang` giữ nguyên. | User 2026-10-29 | 2026-10-29 |
| D-BIGINT | Kiểu BIGINT | BIGINT sẽ là INT8. Cột `gld_srv_poi_review.rating_count` trên PostgreSQL là `int8`. | User 2026-10-29 | 2026-10-29 |
| D-MODEL | data_model_change | Gắn data_model_change vì cột PostgreSQL khác gold: `apps.srv_poi_review` không có `lang`. Khóa không đổi, vẫn `NodeSpec.pk` (`review_id`). `model-design.md` đã có. Architecture PASS. | request.md Constraints; WORKFLOW.md §Classification; architecture.md RESULT | 2026-10-29 |
| D-FILE | Tên file SQL | Chốt A: `sql/postgres/gld_srv_serve.pg.sql`. Lý do: `.sqlfluff` L2 và `vv.py` lint `*.sql` bằng sparksql, `*.pg.sql` bằng postgres. | User 2026-10-29; architecture.md Main brief Stop 1 | 2026-10-29 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Bảng kiểm

Khóa lấy từ `NodeSpec.pk`. Cột và kiểu Fabric lấy từ `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`. Cell `NB_CREATE_DDL` ở cột nguồn là hợp đồng mới nhất và khớp `init_tables`. `OUT_COLS` của notebook node không gồm `row_hash`, `created_at`, `updated_at`, `deleted_at`; các cột đó vẫn có trong DDL gold nên vẫn nằm trong bảng kiểm. Tên bảng PostgreSQL theo D-NAME: bỏ tiền tố `gld_`, đặt trong schema `apps`. Cột `lang` của review không tạo, theo D-LANG.

| Bảng | pk | Cột | Kiểu Fabric | Kiểu PostgreSQL | Nguồn cell |
|---|---|---|---|---|---|
| gld_srv_poi_info | 1 | poi_id | STRING NOT NULL | text NOT NULL | init_tables L327; NB_GLD_SRV_POI_INFO cell 4 pk; NB_CREATE_DDL srvratepy |
| gld_srv_poi_info |  | poi_name | STRING | text | init_tables L328; srvratepy |
| gld_srv_poi_info |  | source_name | STRING | text | init_tables L329; srvratepy |
| gld_srv_poi_info |  | business_sector | STRING | text | init_tables L330; srvratepy |
| gld_srv_poi_info |  | business_category | STRING | text | init_tables L331; srvratepy |
| gld_srv_poi_info |  | subcategory_tags | STRING | text | init_tables L332; srvratepy |
| gld_srv_poi_info |  | destination_id | STRING | text | init_tables L333; srvratepy |
| gld_srv_poi_info |  | full_address | STRING | text | init_tables L334; srvratepy |
| gld_srv_poi_info |  | street | STRING | text | init_tables L335; srvratepy |
| gld_srv_poi_info |  | ward | STRING | text | init_tables L336; srvratepy |
| gld_srv_poi_info |  | district | STRING | text | init_tables L337; srvratepy |
| gld_srv_poi_info |  | city | STRING | text | init_tables L338; srvratepy |
| gld_srv_poi_info |  | country_code | STRING | text | init_tables L339; srvratepy |
| gld_srv_poi_info |  | postal_code | STRING | text | init_tables L340; srvratepy |
| gld_srv_poi_info |  | lat | DOUBLE | double precision | init_tables L341; srvratepy |
| gld_srv_poi_info |  | lng | DOUBLE | double precision | init_tables L342; srvratepy |
| gld_srv_poi_info |  | phone | STRING | text | init_tables L343; srvratepy |
| gld_srv_poi_info |  | email | STRING | text | init_tables L344; srvratepy |
| gld_srv_poi_info |  | website_url | STRING | text | init_tables L345; srvratepy |
| gld_srv_poi_info |  | operating_status | STRING | text | init_tables L346; srvratepy |
| gld_srv_poi_info |  | is_verified | BOOLEAN | boolean | init_tables L347; srvratepy |
| gld_srv_poi_info |  | is_recommended | BOOLEAN | boolean | init_tables L348; srvratepy |
| gld_srv_poi_info |  | is_bookable | BOOLEAN | boolean | init_tables L349; srvratepy |
| gld_srv_poi_info |  | operating_hours | STRING | text | init_tables L350; srvratepy |
| gld_srv_poi_info |  | holiday_exceptions | STRING | text | init_tables L351; srvratepy |
| gld_srv_poi_info |  | rating_overall | DECIMAL(4,2) | numeric(4,2) | init_tables L352; srvratepy |
| gld_srv_poi_info |  | rating_count | INT | integer | init_tables L353; srvratepy |
| gld_srv_poi_info |  | review_count | INT | integer | init_tables L354; srvratepy |
| gld_srv_poi_info |  | row_hash | STRING | text | init_tables L355; srvratepy |
| gld_srv_poi_info |  | created_at | TIMESTAMP | timestamp without time zone | init_tables L356; srvratepy |
| gld_srv_poi_info |  | updated_at | TIMESTAMP | timestamp without time zone | init_tables L357; srvratepy |
| gld_srv_poi_info |  | deleted_at | TIMESTAMP | timestamp without time zone | init_tables L358; srvratepy |
| gld_srv_poi_multi_lang | 1 | poi_id | STRING NOT NULL | text NOT NULL | init_tables L312; NB_GLD_SRV_POI_MULTI_LANG cell 3 pk; NB_CREATE_DDL mlexppy |
| gld_srv_poi_multi_lang | 2 | lang | STRING NOT NULL | text NOT NULL | init_tables L313; cell 3 pk; mlexppy |
| gld_srv_poi_multi_lang |  | source_name | STRING | text | init_tables L314; mlexppy |
| gld_srv_poi_multi_lang |  | time_to_spend | STRING | text | init_tables L315; mlexppy |
| gld_srv_poi_multi_lang |  | best_time | STRING | text | init_tables L316; mlexppy |
| gld_srv_poi_multi_lang |  | cost_vnd | STRING | text | init_tables L317; mlexppy |
| gld_srv_poi_multi_lang |  | description | STRING | text | init_tables L318; mlexppy |
| gld_srv_poi_multi_lang |  | experience | STRING | text | init_tables L319; mlexppy |
| gld_srv_poi_multi_lang |  | row_hash | STRING | text | init_tables L320; mlexppy |
| gld_srv_poi_multi_lang |  | created_at | TIMESTAMP | timestamp without time zone | init_tables L321; mlexppy |
| gld_srv_poi_multi_lang |  | updated_at | TIMESTAMP | timestamp without time zone | init_tables L322; mlexppy |
| gld_srv_poi_multi_lang |  | deleted_at | TIMESTAMP | timestamp without time zone | init_tables L323; mlexppy |
| gld_srv_poi_amenity | 1 | poi_id | STRING NOT NULL | text NOT NULL | init_tables L401; NB_GLD_SRV_POI_AMENITY cell 3 pk; NB_CREATE_DDL amenddlpy |
| gld_srv_poi_amenity | 2 | business_sector | STRING NOT NULL | text NOT NULL | init_tables L402; cell 3 pk; amenddlpy |
| gld_srv_poi_amenity | 3 | amenity_group | STRING NOT NULL | text NOT NULL | init_tables L403; cell 3 pk; amenddlpy |
| gld_srv_poi_amenity | 4 | amenity_raw | STRING NOT NULL | text NOT NULL | init_tables L404; cell 3 pk; amenddlpy |
| gld_srv_poi_amenity |  | amenity | STRING | text | init_tables L405; amenddlpy |
| gld_srv_poi_amenity |  | amenity_vi | STRING | text | init_tables L406; amenddlpy |
| gld_srv_poi_amenity |  | service_flags | STRING | text | init_tables L407; amenddlpy |
| gld_srv_poi_amenity |  | row_hash | STRING | text | init_tables L408; amenddlpy |
| gld_srv_poi_amenity |  | created_at | TIMESTAMP | timestamp without time zone | init_tables L409; amenddlpy |
| gld_srv_poi_amenity |  | updated_at | TIMESTAMP | timestamp without time zone | init_tables L410; amenddlpy |
| gld_srv_poi_amenity |  | deleted_at | TIMESTAMP | timestamp without time zone | init_tables L411; amenddlpy |
| gld_srv_poi_media_gallery | 1 | media_id | STRING NOT NULL | text NOT NULL | init_tables L382; NB_GLD_SRV_POI_MEDIA_GALLERY cell 3 pk; NB_CREATE_DDL mediaddlpy |
| gld_srv_poi_media_gallery |  | poi_id | STRING | text | init_tables L383; mediaddlpy |
| gld_srv_poi_media_gallery |  | source_name | STRING | text | init_tables L384; mediaddlpy |
| gld_srv_poi_media_gallery |  | photo_api_uri | STRING | text | init_tables L385; mediaddlpy |
| gld_srv_poi_media_gallery |  | display_order | INT | integer | init_tables L386; mediaddlpy |
| gld_srv_poi_media_gallery |  | width_px | INT | integer | init_tables L387; mediaddlpy |
| gld_srv_poi_media_gallery |  | height_px | INT | integer | init_tables L388; mediaddlpy |
| gld_srv_poi_media_gallery |  | photographer | STRING | text | init_tables L389; mediaddlpy |
| gld_srv_poi_media_gallery |  | blob_url | STRING | text | init_tables L390; mediaddlpy |
| gld_srv_poi_media_gallery |  | thumbnail_url | STRING | text | init_tables L391; mediaddlpy |
| gld_srv_poi_media_gallery |  | is_cover | BOOLEAN | boolean | init_tables L392; mediaddlpy |
| gld_srv_poi_media_gallery |  | is_active | BOOLEAN | boolean | init_tables L393; mediaddlpy |
| gld_srv_poi_media_gallery |  | row_hash | STRING | text | init_tables L394; mediaddlpy |
| gld_srv_poi_media_gallery |  | created_at | TIMESTAMP | timestamp without time zone | init_tables L395; mediaddlpy |
| gld_srv_poi_media_gallery |  | updated_at | TIMESTAMP | timestamp without time zone | init_tables L396; mediaddlpy |
| gld_srv_poi_media_gallery |  | deleted_at | TIMESTAMP | timestamp without time zone | init_tables L397; mediaddlpy |
| gld_srv_poi_review | 1 | review_id | STRING NOT NULL | text NOT NULL | init_tables L415; NB_GLD_SRV_POI_REVIEW cell 3 pk; NB_CREATE_DDL srvrevpy |
| gld_srv_poi_review |  | poi_id | STRING | text | init_tables L416; srvrevpy |
| gld_srv_poi_review |  | lang | STRING | không tạo (D-LANG) | init_tables L417; srvrevpy; User 2026-10-29 |
| gld_srv_poi_review |  | rating_overall | DECIMAL(4,2) | numeric(4,2) | init_tables L418; srvrevpy |
| gld_srv_poi_review |  | rating_count | BIGINT | int8 | init_tables L419; srvrevpy; D-BIGINT |
| gld_srv_poi_review |  | title | STRING | text | init_tables L420; srvrevpy |
| gld_srv_poi_review |  | review_text | STRING | text | init_tables L421; srvrevpy |
| gld_srv_poi_review |  | rating | DECIMAL(4,2) | numeric(4,2) | init_tables L422; srvrevpy |
| gld_srv_poi_review |  | review_date | STRING | text | init_tables L423; srvrevpy |
| gld_srv_poi_review |  | author_name | STRING | text | init_tables L424; srvrevpy |
| gld_srv_poi_review |  | row_hash | STRING | text | init_tables L425; srvrevpy |
| gld_srv_poi_review |  | created_at | TIMESTAMP | timestamp without time zone | init_tables L426; srvrevpy |
| gld_srv_poi_review |  | updated_at | TIMESTAMP | timestamp without time zone | init_tables L427; srvrevpy |
| gld_srv_poi_review |  | deleted_at | TIMESTAMP | timestamp without time zone | init_tables L428; srvrevpy |

Mọi cột thuộc `PRIMARY KEY` đã là `STRING NOT NULL` trong DDL gold. Không có cột khóa nào cần thêm `NOT NULL` ngoài DDL.

## Giả định còn lại

- Không có. Schema PostgreSQL và kiểu `BIGINT` đang chờ người dùng, không giả định.

## Sai lệch so với kiến trúc

- Không có. Architecture chưa chạy.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Quyết định của người dùng

- Tên schema: apps.
- Tên bảng tiền tố bỏ gld_; Bắt đầu bằng srv_.
- review_id bỏ field lang.
- BIGINT sẽ là INT8.
- Tên file SQL: Chốt A, `sql/postgres/gld_srv_serve.pg.sql`.

## Lịch sử quyết định

- 2026-10-29: Phân loại `complexity=medium`, `risk_level=low`, `architecture_required=true`, `evidence_required=false`, `runtime_required=false`, signal `cross_system`, reviewer `sql-data-reviewer`. Không gắn `data_model_change`. Repository không có file `sql/postgres/` và không có tên schema PostgreSQL cho serve. `init_tables` khớp cell mới nhất của `NB_CREATE_DDL` cho năm bảng. Dừng trước `run-gate` vì D-SCHEMA và D-BIGINT.
- 2026-10-29: Người dùng chốt schema `apps`, bỏ tiền tố `gld_` và để tên bảng bắt đầu bằng `srv_`, bỏ cột `lang` khỏi bảng review. Gắn signal `data_model_change`. Khóa `review_id` không đổi. D-BIGINT vẫn MISSING, nên chưa chuyển `waiting_architecture` và chưa gọi `run-author --kind model`.
- 2026-10-29: Người dùng chốt `BIGINT sẽ là INT8` cho `gld_srv_poi_review.rating_count`. Hết mục chờ trước architecture.
- 2026-10-29: Người dùng chốt A. File là `sql/postgres/gld_srv_serve.pg.sql`. Dòng `FILE:` trong `architecture.md` đổi sang đường dẫn đó để `materialize` ghi đúng scope. Thân SQL không đổi.
- 2026-10-29: `materialize --write` tạo `sql/postgres/gld_srv_serve.pg.sql`. `verify` với `PYTHONUTF8=1` PASS (`sqlfluff[postgres]`, `pytest`, `task-state`). Lần chạy trước FAIL vì sqlfluff đọc `.sqlfluff` bằng cp1252, không phải lỗi SQL. Review round 1 PASS, không có P0/P1. Runner chuyển `user_decision` vì `runtime_required=false`. Chưa áp file lên PostgreSQL.
