# Evidence plan

## Decision to resolve

Đã chốt từ probe `legacy_gold_poi_profile` (2026-11-19):

- `poi_master` chỉ có `google` (136315 dòng, 45521 `source_id`, 0 `source_id` trống) và `partner_portal` (448 dòng, 155 `source_id`, 0 trống). Không có giá trị `ingestion_source` khác.
- Google: 7 id một lang, 234 id hai lang, 45280 id ba lang. Số dòng bằng số `poi_id` và bằng 1×7 + 2×234 + 3×45280. Mỗi (`source_id`, lang) một dòng.
- Partner: 7 id một lang, 4 id hai lang, 144 id ba lang. 1×7 + 2×4 + 3×144 = 447, trong khi có 448 dòng và 448 `poi_id`. Một `source_id` có hai `poi_id` cùng lang.
- 151/155 id partner có trong `slv_pn_business_services`. 4 id có `source_id` nhưng không có dòng silver. Không inner-join để tính `poi_id`.
- Mẫu 50 khóa google đều là place id, lang `en`, `ko`, `vi`.
- Gold mới đã có dòng: `gld_srv_poi_info` 19909, `gld_srv_poi_multi_lang` 59726, `gld_srv_poi_review` 121479.

Còn chờ người dùng: bảng POI cũ không có bảng gold mới tương ứng. Không tạo bảng nghiệp vụ mới. Chọn một hướng trước architecture: bỏ qua khi init, hoặc chỉ điền cột đã có cặp trong notebook cũ và DDL `gld_srv_*` hiện có.

Bảng POI cũ không có bảng `gld_*` tương ứng, đếm trên `sgr_visitvn_prd_batch`:

- `ai_poi` — 136815
- `ai_poi_rating` — 56188
- `ai_poi_review` — 271454
- `ai_enriched_poi` — 136754
- `poi_enrichment_display` — 136562
- `poi_address_enrichment_staging` — 92533
- `poi_rating` — 166107. Cột `overall`, `total_reviews`, `score_label`, `sources_json`, `breakdown_json`, `sentiment_avg` không trùng tên cột `gld_srv_poi_info`

Notebook 4 còn ghi các tên không kèm lakehouse: `poi_enrichment`, `poi_enrichment_staging`, `destination_enrichment`. Coi là chưa có bảng gold mới cho tới khi DEV cho biết chúng có nằm ở `lh_vv_gold` không.

Không copy (không phải dữ liệu POI, hoặc là bảng kỹ thuật):

- `partner_gold_watermark`, `stg_poi_master_sync`, `stg_poi_detail_sync`
- `ai_eventhub_sync_config`, `ai_eventhub_watermark`, `ai_eventhub_push_audit`, `ai_eventhub_run_audit`
- `destination`, `blog`, `news`, `destination_ward_mapping`, `ai_product`, `ai_product_translation`

Có chỗ nhận trong gold mới đã có, theo tên field hoặc yêu cầu người dùng: `poi_master`, `poi_detail`, `poi_review`.

## Existing evidence

Công thức `poi_id` cũ, không chép notebook:

- Google, `notebooks_lgc/3rd_data_ingested_orches/NB_10_BRONZE_TO_SILVER_PREPROCESS.ipynb` cell 0: `uuidish_md5_sql("concat(source_name, source_id, lang)")`. `source_name` và `source_id` lấy từ bronze `poi_raw_event`. `NB_30` gán `source_name` thành `canonical_source`. `NB_40` ghi `canonical_source` vào `poi_master.ingestion_source` và `source_id` vào `poi_master.source_id`.
- Partner, `notebooks_lgc/pl_transform_partner_userprofile_cms/2.1. transform_partner_to_gold_poi_master.ipynb` cell 0: `INGESTION = "partner_portal"`. `poi_id` = UUID của `md5(concat(partner_portal, business_services.id, lang))`. `source_id` gold = `row["id"]` của `lh_vv_bronze.partner.business_services`.
- `poi_group_id` google là hash `concat(source_name, source_id)` không có lang. Không dùng làm `poi_id` mới. Không thấy `poi_uid` trong hai công thức này.

Gold mới đã có DDL `gld_` trong `notebooks/NB_CREATE_DDL.ipynb`: `gld_enr_poi_info`, `gld_enr_poi_review`, `gld_srv_poi_info`, `gld_srv_poi_multi_lang`, `gld_srv_poi_amenity`, `gld_srv_poi_media_gallery`, `gld_srv_poi_review`. `gld_enr_poi_coordinate` nằm trong cell xóa cạnh, không phải đích init.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `legacy_gold_poi_profile.sql` | Cùng tenant, chỉ đọc. Đã chạy 2026-11-19 | Giá trị `ingestion_source`, `source_id` trống, số lang, khớp id partner, số dòng | Đã có `evidence/results/legacy_gold_poi_profile.txt` | `evidence/results/legacy_gold_poi_profile.txt` |
| `legacy_gold_types.sql` | P1. Gold cũ `sgr_visitvn_prd_batch` | Kiểu cột đã cặp và số giá trị `try_cast` thất bại | Có `DESCRIBE` và số thất bại, không có giá trị gốc | `evidence/results/legacy_gold_types.txt` |
| `legacy_key_overlap.sql` | P2. Cũ `sgr_visitvn_prd_batch`, mới `sgr_visitvn_dev` | Bao nhiêu `poi_id` mới đã có trên từng bảng đích, tách dòng sống và đã xóa mềm | Chỉ số đếm | `evidence/results/legacy_key_overlap.txt` |
| `legacy_lang_payload_diff.sql` | P4. Gold cũ | Bao nhiêu `source_id` có cột nghiệp vụ khác nhau giữa các lang | Chỉ số đếm. Khóa partner trùng lang: tối đa 5 dòng `source_id` | `evidence/results/legacy_lang_payload_diff.txt` |
| `cross_ws_time_travel.sql` | P5. Notebook mở ở `sgr_visitvn_dev` | `VERSION AS OF` đọc được `poi_master` của workspace cũ không | Một số đếm, hoặc dòng lỗi | `evidence/results/cross_ws_time_travel.txt` |
| `gld_srv_owner_pl.sql` | P7. `sgr_visitvn_dev.lh_vv_ctrl` | Pipeline đang sở hữu 3 bảng đích và ngưỡng khóa | Các dòng config, không secret | `evidence/results/gld_srv_owner_pl.txt` |

P3 không chạy thêm: model sau D-04 không nạp `gld_srv_poi_review` vì notebook cũ không có cùng công thức `review_id`. P6 lấy từ repo: `sql/postgres/gld_srv_serve.pg.sql` khai cột tường minh cho `apps.srv_poi_*`, không có `load_origin`, và API không đọc gold. Chưa thấy notebook sync chọn `SELECT *`.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
