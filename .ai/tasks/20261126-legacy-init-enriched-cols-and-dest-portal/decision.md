# Quyết định

## Quyết định hiện hành

| ID | Chủ đề | Quyết định hiện hành | Nguồn (mục) | Ngày |
|---|---|---|---|---|
| D-ONE-TASK | Phạm vi | Một task, không tách hai việc. | request.md ## User outcome | 2026-11-26 |
| D-OLD-ADDR | old_address | Không sửa công thức old_address của NB_GLD_SRV_POI_INFO (D-OLD-ADDR). | request.md ## Constraints | 2026-11-26 |
| D-NO-GOLD-COL | Cột gold | Không thêm cột gold, không đổi grain hay khóa MERGE. | request.md ## Scope | 2026-11-26 |
| D-MAP-OLD-ADDR | old_address init | old_address lấy address_line_2 | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-PRICE-LEVEL | price_level init | price_level lấy cột cùng tên | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-PRICE-MIN | price_min init | price_min lấy cột cùng tên | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-PRICE-MAX | price_max init | price_max lấy cột cùng tên | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-STORY | story init | story lấy story. Khớp (poi_id, lang). | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-MAP-TIPS | local_tips init | local_tips lấy local_tips_or_neighborhood. Khớp (poi_id, lang). | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-LANG-ROW | Khớp lang | story và local_tips gắn đúng dòng (poi_id, lang). Không nhân một giá trị sang mọi lang của POI. | request.md ## Acceptance criteria | 2026-11-26 |
| D-PRICE-TYPE | Kiểu giá | Gold giữ INT và DECIMAL(18,2); nguồn giá là int. | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-GOLD-ONLY | Sáu cột | Sáu cột vẫn gold-only: PostgreSQL, Java, docs/context/api-mapping/ không nhận chúng. | request.md ## Constraints | 2026-11-26 |
| D-LEGACY-READ | Bảng legacy | Các bảng legacy khác vẫn không được đọc để nạp. | request.md ## Acceptance criteria | 2026-11-26 |
| D-DEST-ID | destination_id | destination_id = strapi_document_id của từng phần tử | request.md ## User outcome | 2026-11-26 |
| D-DEST-PORTAL | destination_portal_id | destination_portal_id = id của từng phần tử. Payload có khóa id, không có khóa destination_id | request.md ## User outcome | 2026-11-26 |
| D-DEST-NAME | destination_name | destination_name giữ nguyên | request.md ## Scope | 2026-11-26 |
| D-DEST-ARRAY | Thứ tự mảng | destination_id, destination_portal_id, destination_name cùng dạng chuỗi JSON mảng, cùng thứ tự phần tử, kể cả phần tử null | request.md ## Scope | 2026-11-26 |
| D-DEST-SCOPE | Phạm vi cột mới | destination_portal_id chỉ có trên slv_enr_poi_destination. Không thêm sang gld_srv_poi_info, PostgreSQL, API | request.md ## Scope | 2026-11-26 |
| D-DEST-GOLD | Gold copy | gld_srv_poi_info.destination_id vẫn copy 1-1 từ silver, nên giá trị gold đổi theo strapi_document_id | request.md ## User outcome | 2026-11-26 |
| D-SCHEMA | Schema ai_enriched_poi | Người dùng chọn mục 1. old_address lấy address_line_2. price_level, price_min, price_max lấy cột cùng tên. story lấy story. local_tips lấy local_tips_or_neighborhood. Khớp (poi_id, lang). Gold giữ INT và DECIMAL(18,2); nguồn giá là int. | decision.md ## Câu hỏi đang mở mục 1 | 2026-11-26 |
| D-INIT-KEY | Khóa init | ai_enriched_poi.poi_id = gld_poi_legacy_id_map.legacy_poi_id, và ai_enriched_poi.lang phải bằng map.lang. Lệch lang thì RUN dừng. | architecture.md ## 2; evidence/results/p_gaps.txt P-AI-1 | 2026-11-26 |
| D-INIT-INFO-VI | Bốn cột info | Bốn cột gld_srv_poi_info lấy từ dòng ai_enriched_poi lang vi mà vi_key đã chọn. | architecture.md ## 2 và ## 6 | 2026-11-26 |
| D-INIT-ENRICH-ONLY | Không tạo dòng mới | Sáu cột chỉ điền dòng init đã dựng. Thiếu nguồn thì NULL. Không tạo dòng gold chỉ từ ai_enriched_poi. | architecture.md ## 2 | 2026-11-26 |
| D-DEST-BACKFILL | Backfill silver | B. Backfill tại chỗ từ event bronze đã sinh dòng silver. Hai dòng không có phần tử strapi_document_id ghi mảng rỗng. | decision.md ## Câu hỏi đang mở, D-DEST-BACKFILL mục 1 | 2026-11-26 |
| D-LEGACY-DEST | destination_id init | Giữ mapping destination_id của init legacy. destination_id của phần INIT đã đúng, không cần thay đổi hay chạy lại. Ghi chú ở mapping_legacy_gold_to_gld_srv.md tại dòng destination_id của init: giá trị LEGACY_INIT đứng ngoài id portal, và 1/24 giá trị trùng strapi. | Người dùng, 2026-11-26 | 2026-11-26 |
| D-G4 | Scope thêm | Thêm tests/test_enr_extract_contract.py, tests/test_legacy_gold_poi_init_contract.py và docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md vào scope.files. | decision.md ## Câu hỏi đang mở, G4 mục 2 | 2026-11-26 |
| D-NULL-LIVE | Nullable Delta | Cổng schema của destportalpy so tên và kiểu theo thứ tự. Không so nullable. Delta DEV báo mọi cột của slv_enr_poi_destination là nullable True, kể cả poi_id. TABLE_COLS vẫn giữ nullable của TABLE_SPECS. | evidence/results/destportal-schema.txt | 2026-11-26 |
| D-ARRAY-ALLOW | Path mảng extract | enr12 cho phép destinations.strapi_document_id cùng destinations.id và destinations.name. | Người dùng, log ConfigError 2026-11-26 | 2026-11-26 |
| D-DEST-KEEP | Upsert info | Đồng ý mục 2. Upsert info không cập nhật destination_id của dòng LEGACY_INIT. destination_changed_n chỉ là số báo cáo, không raise. Sáu cột vẫn ghi. | Người dùng, 2026-11-27 | 2026-11-27 |
| D-MAP-DRIFT | Cổng drift map | Mục 1. RUN không raise khi drift_n > 0. drift_n chỉ báo cáo. Map vẫn insert-only: dòng đã có không đổi, chỉ insert legacy_poi_id mới. Stage sau dùng map đã ghi. | Người dùng, 2026-11-27 | 2026-11-27 |

Sửa dòng tại chỗ khi quyết định đổi. Chi tiết ghi thêm ở `## Lịch sử quyết định`.

## Giả định còn lại

- Không có. Schema `ai_enriched_poi` lấy từ probe. Nguồn thay cho `poi_address_json` và `local_tips` là câu hỏi đang mở, chưa giả định.

## Xử lý findings

| Finding ID | Severity | Quyết định | Lý do / bằng chứng | Backlog |
|---|---|---|---|---|
| SPARK-001 | P1 | fixed | `finally` của `destportalpy` gỡ `userMetadata` khi MERGE lỗi, rồi mới nhả khoá. | |
| SPARK-002 | P1 | fixed | Hạn khoá lấy `LEASE_MINUTES = 90`, cùng mốc `LOCK_TIMEOUT_DEFAULT_MIN`. Runbook sẽ có bước chiếm lại khoá sau khi hủy giữa chừng. | |

Giá trị quyết định hợp lệ: `fixed`, `accepted-risk`, `rejected-false-positive`, `backlog`.

## Lịch sử quyết định

- 2026-11-26. Ledger `20261126-gld-srv-old-address-price-story` giữ D-OLD-ADDR: lấy `house_number`, `street`, `full_address` chứ không phải `old_house_number`, `old_street`, `old_full_address`. Task này không sửa công thức đó.
- 2026-11-26. `TABLE_SPECS` trong `NB_SETUP_INITIAL_DDL` đã có `gld_srv_poi_info.old_address` STRING, `price_level` INT, `price_min` DECIMAL(18,2), `price_max` DECIMAL(18,2), và `gld_srv_poi_multi_lang.story` STRING, `local_tips` STRING, khóa `(poi_id, lang)`.
- 2026-11-26. `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` hiện parse `DEST_ELEM_SCHEMA = array<struct<id:string,name:string>>` và `ARRAY_PROJECTIONS` `destinations.id` → `id`, `destinations.name` → `name`. Chưa có `strapi_document_id` hay `destination_portal_id`. Khóa payload destination lấy từ quyết định người dùng, không từ probe.
- 2026-11-26. Triage dừng ở `waiting_evidence` vì schema `ai_enriched_poi` không có trong `notebooks/`, `docs/context/`, `sql/`, `tests/`.
- 2026-11-26. Probe `ai_enriched_poi_schema` trên `sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi`: 136754 dòng, 136754 `poi_id` phân biệt, `poi_id` null = 0, mọi POI một dòng. Cột ngôn ngữ là `lang`, null hoặc blank = 0, `(poi_id, lang)` trùng = 0. `story` có, null = 136321. `local_tips` không có. `poi_address_json` không có. Cột cùng vùng tên quan sát được: `address_line_1`, `address_line_2`, `short_address` (string); `price_level`, `price_min`, `price_max` (int); `local_tips_or_neighborhood` (string).
- 2026-11-26. Người dùng trả lời `Chọn 1.` Nguyên văn mục 1: `old_address` lấy `address_line_2`. `price_level`, `price_min`, `price_max` lấy cột cùng tên. `story` lấy `story`. `local_tips` lấy `local_tips_or_neighborhood`. Khớp `(poi_id, lang)`. Gold giữ INT và DECIMAL(18,2); nguồn giá là int.
- 2026-11-26. `run-author --kind model` ghi `model-design.md`. Architect vòng 1 trả `EVIDENCE_REQUIRED`. Gap G1–G3 nằm trong một script `evidence/probes/p_gaps.py`. G4 là thêm `tests/test_enr_extract_contract.py` và `tests/test_legacy_gold_poi_init_contract.py` vào `scope.files`.
- 2026-11-26. `p_gaps.txt`. P-DEST-1: silver_n = joined_rows = id_eq_n = name_eq_n = sd_full_n = 19799, no_event_n = 0, blk_null_n = 0, sd_partial_n = 0, sd_none_n = 2. P-DEST-2: elem_n = sd_string_n = id_string_n = 43241, elem_null_n = sd_number_n = id_number_n = 0, sd_first_seen = 2026-11-16 07:05:57.134825. P-AI-1: 136754/136754 khớp `poi_master` và `legacy_poi_id`, cùng lang, `poi_id_status` OK, `new_id_hit_n` = 0, `price_inverted_n` = 0. P-AI-2: en 45659, vi 45674, ko 45421. P-LEGDEST-1: 24 giá trị, `in_portal_id` = 0, `in_strapi` = 1. P-LEGDEST-2: LEGACY_INIT 34254 dòng, 34167 có destination_id; `load_origin` trống 19909 dòng, 19799 có destination_id. `sd_none_n` = 2 đồng thời nằm trong `sd_full_n` vì mảng không có phần tử non-null.
- 2026-11-26. Người dùng: D-DEST-BACKFILL chọn 1. D-LEGACY-DEST chọn 1. Nguyên văn: `destination_id của phần INIT đã đúng, không cần thay đổi hay chạy lại`. G4: `Đồng ý mục 2.`
- 2026-11-26. PLAN `lgp-2496ae06c9354e3c81bcee45e38a3851`: `enriched.decision=OK`, pin `ai_enriched_poi=10968`, `destination_changed_n=4038`. Dừng trước RUN theo cổng info.
- 2026-11-27. RUN `lgp-ce830a17ae014740ba09da6e28ee7ba6` dừng ở stage map: `drift_n=25345`, `review.inserted=0`. Raise nằm trước `map_rows = stored.unionByName(fresh_only)`. Các stage sau dùng map đã ghi, không dùng bản tính lại.
- 2026-11-27. Người dùng chọn D-MAP-DRIFT mục 1. Bỏ raise. Map vẫn insert-only.

## Câu hỏi đang mở

Đã trả lời ngày 2026-11-27. D-MAP-DRIFT mục 1. Không còn câu hỏi mở.
