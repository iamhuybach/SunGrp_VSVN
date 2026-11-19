# Hướng dẫn kiểm chứng runtime — 20261119-gsm-as-google-extract

Trạng thái: `CHỜ CHẠY`

Tài liệu này chỉ là hướng dẫn. Chưa có lần chạy nào được ghi nhận ở đây. Mọi kết quả phải do người vận hành điền vào mục `Kết quả người dùng ghi nhận`.

## Phạm vi và môi trường

- Môi trường: **chỉ Fabric DEV**. Không chạy trên production. Theo `architecture.md` `## Rollout` bước 8, production chỉ được chạy sau khi gate runtime DEV PASS.
- Notebook chính: `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, tham số ở cell `e3eb64e4`.
- Pipeline: `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, activity 3P extract (`src_tbl = brz_3rd_crawler_poi_stream`).
- Nguồn raw: `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`. Các cột dùng trong truy vấn kiểm tra: `source_name`, `source_id`, `crawled_at`, `event_id`, `normalized_payload`.
- 9 bảng đích active, đều ở `lh_vv_silver.dbo`:
  - Khoá `poi_id`: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_rating`, `slv_3p_poi_amenity`.
  - Khoá `review_id`: `slv_3p_poi_review`.
  - Khoá `media_dedup_key`: `slv_3p_poi_media`.
  - `slv_3p_poi_policy` đang tắt và không nằm trong 9 bảng.
- Bảng control `lh_vv_ctrl.dbo`: `ctrl_mng_watermark` (dòng `wm_transform_brz_3rd_crawler_poi_stream`), `ctrl_cdc_state` (partition `src_tbl = 'brz_3rd_crawler_poi_stream'`), `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_cdc_reject`.
- Downstream, chạy sau extract theo đúng thứ tự: `NB_SLV_POI_ENTITY_NON_ENRICH`, rồi amenity (`NB_SLV_POI_AMENITY`) và media (`NB_SLV_POI_MEDIA_INFO`), rồi `NB_ENR_POI_INFO`, rồi gold (`NB_GLD_SRV_POI_INFO` và các node gold còn lại: `<CẦN NGƯỜI DÙNG CUNG CẤP: danh sách đủ các notebook gold cần chạy sau NB_ENR_POI_INFO, gồm notebook ghi gld_srv_poi_multi_lang và gld_enr_poi_info>`).
- Schema của gold và dictionary: `<CẦN NGƯỜI DÙNG CUNG CẤP: schema đầy đủ của gld_srv_poi_info, gld_srv_poi_multi_lang, gld_enr_poi_info, ref_dictionary_amenities, ref_dictionary_place_type>`. Các truy vấn bên dưới ghi tạm là `<GOLD_SCHEMA>` và `<REF_SCHEMA>`.
- Bảng silver downstream đã biết schema: `lh_vv_silver.dbo.slv_poi_entity_non_enrich`, `lh_vv_silver.dbo.slv_poi_amenity`.

Rủi ro đã được người dùng chấp nhận ("accept risk cho cả 2 GATE"). Runbook này không yêu cầu đổi tham số vì hai rủi ro này, nhưng người vận hành phải giữ đúng giá trị dưới đây:
- **GATE-001.** Nếu chạy tay với `table_filter` có `slv_3p_poi` mà thiếu các bảng con, bảng cha có thể chuyển sang `google` mà không có takeover. Pipeline theo lịch truyền `table_filter` rỗng. Runbook này luôn dùng `table_filter = ""`.
- **GATE-002.** Nếu chạy tay với `state_key = row`, takeover không xoá state của review và media. Pipeline theo lịch truyền `state_key = doc`. Runbook này luôn dùng `state_key = "doc"`.

## Điều kiện tiên quyết

1. Code đã merge và đã deploy lên workspace DEV:
   - Trong notebook DEV, cell `e3eb64e4` có `sources = "google,sgm"`.
   - Trên pipeline DEV, activity 3P (`src_tbl = brz_3rd_crawler_poi_stream`) có `sources = "google,sgm"`, `state_key = "doc"`, `table_filter = ""`, `full_reload = false`, `allow_full_scan = false`, `dry_run = false`, `max_parallel = 12`, `max_retries = 1`, `cast_null_policy = "FAIL"`. Activity CMS vẫn giữ `sources = "strapi_blog,strapi_destination,strapi_news,strapi_ph_promotion_article"`.
   - `NB_SLV_POI_ENTITY_NON_ENRICH` DEV đã có phép map `sgm`→`google` (cell `b1entitybuild`).
2. Test local và gate đã PASS. Ghi lại kết quả vào mục cuối:
   - `python -m pytest tests/test_3p_l1_contract.py tests/test_3p_raw_rules.py tests/test_pipeline_precheck_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_enr_poi_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_3p_visibility_sql.py tests/test_l1_ts_contract.py -q`
   - `python -m pytest tests/test_3p_sgm_identity_contract.py -q`
   - `python scripts/vv.py run-gate 20261119-gsm-as-google-extract`
3. Không có run nào khác của FL_00 hoặc của notebook extract 3P đang chạy. Tạm dừng trigger theo lịch của FL_00 trên DEV trong suốt runbook, vì một run theo lịch chen vào sẽ làm sai phép so sánh `v0` và phép kiểm tra 0 insert. Cách tạm dừng: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên trigger/lịch FL_00 trên DEV và người được phép tạm dừng>`.
4. Kiểm tra khoá nguồn (chỉ đọc):

```sql
SELECT watermark_id, status, last_src_version, last_src_table_id, watermark_value,
       last_success_at, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_transform_brz_3rd_crawler_poi_stream';
```

   Kỳ vọng: `lock_exec_id` là NULL và `status` khác `RUNNING`. Nếu còn khoá thì DỪNG. Chỉ nhả khoá theo `CTRL_TABLES_CONTEXT.md` §4 khi chắc chắn không còn run nào đang chạy, và phải có người dùng xác nhận.
5. V-10 và V-11 **không thuộc lần chạy này** (xem mục `Kiểm tra kết quả`). Không ghi vào bronze và không đặt `table_filter` khác rỗng trong runbook này.

## Baseline trước khi chạy

Mọi truy vấn trong mục này chỉ đọc. Chạy B-1 đến B-4 trước bước 1 (dry run). Chạy lại B-5 (`v0`) **ngay trước** bước 2 (run thật).

**B-1. Phân bố `source_name` hiện tại của `slv_3p_poi`.** Kỳ vọng: không có dòng `sgm`, vì trước đây `sources = google`.

```sql
SELECT source_name, COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_3p_poi
GROUP BY source_name ORDER BY source_name;
```

**B-2. Số dòng của 9 bảng và của state 3P** (PySpark, chỉ in số tổng):

```python
TABLES = ["slv_3p_poi", "slv_3p_poi_address", "slv_3p_poi_contact", "slv_3p_poi_price",
          "slv_3p_poi_opening_hours", "slv_3p_poi_rating", "slv_3p_poi_amenity",
          "slv_3p_poi_review", "slv_3p_poi_media"]
for t in TABLES:
    print(t, spark.table(f"lh_vv_silver.dbo.{t}").count())
print("ctrl_cdc_state_3p",
      spark.sql("SELECT COUNT(*) c FROM lh_vv_ctrl.dbo.ctrl_cdc_state "
                "WHERE src_tbl = 'brz_3rd_crawler_poi_stream'").first()["c"])
```

**B-3. Các lý do reject 3P chưa xử lý hiện có**, để sau run so sánh xem có lý do mới hay không:

```sql
SELECT trg_tbl, reject_reason, COUNT(*) AS so_dong
FROM lh_vv_ctrl.dbo.ctrl_cdc_reject
WHERE src_tbl = 'brz_3rd_crawler_poi_stream' AND NOT is_resolved
GROUP BY 1, 2 ORDER BY 1, 2;
```

**B-4. Tập cột của gold**, để dùng cho V-7:

```sql
DESCRIBE TABLE <GOLD_SCHEMA>.gld_srv_poi_info;
DESCRIBE TABLE <GOLD_SCHEMA>.gld_srv_poi_multi_lang;
DESCRIBE TABLE <GOLD_SCHEMA>.gld_enr_poi_info;
```

**B-5. Ghi `v0`.** Lấy Delta version hiện tại của 9 bảng và của `ctrl_cdc_state`. Chạy ngay trước bước 2, sau dry run:

```python
for t in [f"lh_vv_silver.dbo.{x}" for x in TABLES] + ["lh_vv_ctrl.dbo.ctrl_cdc_state"]:
    h = spark.sql(f"DESCRIBE HISTORY {t} LIMIT 1").select("version", "timestamp").first()
    print(t, h["version"], h["timestamp"])
```

Ghi 10 giá trị này vào mục cuối. Từ đây gọi tắt là `<v0_slv_3p_poi>`, `<v0_ctrl_cdc_state>` và tương tự cho từng bảng. Đồng thời chạy lại truy vấn ở bước 4 phần `Điều kiện tiên quyết` và ghi `last_src_version` trước run thật.

## Các bước thực hiện

Mỗi bước chạy tay notebook `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` trên DEV. Gán tham số bằng một cell ghi đè đặt ngay sau cell `e3eb64e4`, hoặc truyền tham số cho lần chạy. Không lưu và không commit cell ghi đè đó vào git.

**Bước 1 — Dry run backfill (preview, không ghi).**

```python
pl_name                 = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"
run_id                  = ""
src_schema              = "lh_vv_bronze.dbo"
src_tbl                 = "brz_3rd_crawler_poi_stream"
allow_full_scan         = True
max_parallel            = 12
max_retries             = 1
table_filter            = ""
full_reload             = True
dry_run                 = True
stop_on_failure         = False
cast_null_policy        = "FAIL"
running_timeout_minutes = 780
sources                 = "google,sgm"
doc_key_column          = "poi_id"
state_key               = "doc"
```

Đọc JSON exit của notebook (cell cuối, `RUN_SUMMARY`). Kỳ vọng:
- `sgm_valid = 2630`
- `google_priority_skipped = 402`
- `takeover_poi = 0`
- cast null = 0
- không có lý do reject mới so với B-3

Nếu một giá trị khác kỳ vọng thì DỪNG. Không chạy bước 2. Ghi giá trị thực tế vào mục cuối.

**Bước 2 — Run thật backfill.** Trước hết chạy B-5 để ghi `v0`. Sau đó dùng đúng các tham số ở bước 1, chỉ đổi một giá trị:

```python
dry_run                 = False
```

Các tham số còn lại giữ nguyên: `full_reload = True`, `allow_full_scan = True`, `max_retries = 1`, `max_parallel = 12`, `table_filter = ""`, `state_key = "doc"`, `sources = "google,sgm"`, `cast_null_policy = "FAIL"`, `src_schema = "lh_vv_bronze.dbo"`, `src_tbl = "brz_3rd_crawler_poi_stream"`.

Kỳ vọng:
- JSON exit có `sgm_valid = 2630`, `google_priority_skipped = 402`, `takeover_poi = 0`, `takeover_deferred = 0`.
- `ctrl_log_run.status = SUCCESS`.
- `slv_3p_poi` có 2228 dòng `source_name = 'sgm'` (V-4).

Ghi `exec_id` và `run_id` của run này. Khi chạy tay, `run_id` bằng `exec_id`.

**Bước 3 — Chạy lại để kiểm tra idempotency.** Xem mục `Chạy lại để kiểm tra idempotency`.

**Bước 4 — Downstream.** Chạy theo đúng thứ tự:
1. `NB_SLV_POI_ENTITY_NON_ENRICH`
2. `NB_SLV_POI_AMENITY` và `NB_SLV_POI_MEDIA_INFO`
3. `NB_ENR_POI_INFO`
4. Các node gold

Cách chạy và tham số: `<CẦN NGƯỜI DÙNG CUNG CẤP: chạy qua NB_00_ORCHES_SLV_TO_GLD hay chạy tay từng node; pipeline và tham số chính xác, ví dụ giá trị p_force_nodes nếu dùng>`. Mỗi node phải `SUCCESS` hoặc `NO_DATA` thì mới chạy node sau.

**Bước 5 — Chạy V-1 đến V-9** (mục `Kiểm tra kết quả`).

## Kiểm tra kết quả

Mọi truy vấn chỉ đọc và chỉ trả số tổng. Không in `source_id`, tên, nội dung review hay URL.

**V-1. Khoá duy nhất.** Kỳ vọng: `n = n_key` ở cả 9 dòng kết quả.

```sql
SELECT 'slv_3p_poi' t, COUNT(*) n, COUNT(DISTINCT poi_id) n_key FROM lh_vv_silver.dbo.slv_3p_poi
UNION ALL SELECT 'slv_3p_poi_address', COUNT(*), COUNT(DISTINCT poi_id) FROM lh_vv_silver.dbo.slv_3p_poi_address
UNION ALL SELECT 'slv_3p_poi_contact', COUNT(*), COUNT(DISTINCT poi_id) FROM lh_vv_silver.dbo.slv_3p_poi_contact
UNION ALL SELECT 'slv_3p_poi_price', COUNT(*), COUNT(DISTINCT poi_id) FROM lh_vv_silver.dbo.slv_3p_poi_price
UNION ALL SELECT 'slv_3p_poi_opening_hours', COUNT(*), COUNT(DISTINCT poi_id) FROM lh_vv_silver.dbo.slv_3p_poi_opening_hours
UNION ALL SELECT 'slv_3p_poi_rating', COUNT(*), COUNT(DISTINCT poi_id) FROM lh_vv_silver.dbo.slv_3p_poi_rating
UNION ALL SELECT 'slv_3p_poi_amenity', COUNT(*), COUNT(DISTINCT poi_id) FROM lh_vv_silver.dbo.slv_3p_poi_amenity
UNION ALL SELECT 'slv_3p_poi_review', COUNT(*), COUNT(DISTINCT review_id) FROM lh_vv_silver.dbo.slv_3p_poi_review
UNION ALL SELECT 'slv_3p_poi_media', COUNT(*), COUNT(DISTINCT media_dedup_key) FROM lh_vv_silver.dbo.slv_3p_poi_media;
```

**V-2. Công thức khoá của `sgm`.** Kỳ vọng `sgm_poi_not_google_hash = 0`. Truy vấn dùng `source_id` bronze nguyên văn, không trim, theo I-2.

```sql
WITH sgm_hash AS (
  SELECT DISTINCT regexp_replace(md5(concat('google', source_id)),
         '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5') AS poi_id
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
  WHERE lower(trim(source_name)) = 'sgm'
)
SELECT COUNT(*) AS sgm_poi_not_google_hash
FROM lh_vv_silver.dbo.slv_3p_poi p
LEFT ANTI JOIN sgm_hash h ON p.poi_id = h.poi_id
WHERE p.source_name = 'sgm';
```

Spot-check bảng con (PySpark, chỉ in số). Truy vấn tính lại `review_id` và `media_dedup_key` từ payload `sgm` của các POI đang là `sgm`, theo công thức `01_DATA_MODEL.md` §8. Kỳ vọng:
- `*_missing_google = 0`
- `*_hit_sgm = 0`

Nếu `*_missing_google > 0` thì đối chiếu với rule `HASH_SHA256` / `HASH_SHA256_PIPE` của lib trước khi kết luận FAIL. Truy vấn này có thể khác lib ở cách xử lý NULL hoặc trim.

```python
from pyspark.sql import functions as F
b = spark.table("lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream").where(F.lower(F.trim("source_name")) == "sgm")
b = b.withColumn("poi_id", F.regexp_replace(F.md5(F.concat(F.lit("google"), F.col("source_id"))),
                 r"^(.{8})(.{4})(.{4})(.{4})(.{12})$", "$1-$2-$3-$4-$5"))
sgm_poi = spark.table("lh_vv_silver.dbo.slv_3p_poi").where("source_name = 'sgm'").select("poi_id")
b = b.join(sgm_poi, "poi_id", "left_semi")
def elems(path):
    return b.select("source_id", F.explode(F.from_json(F.get_json_object("normalized_payload", path), "array<string>")).alias("e"))
rv = elems("$.reviews").select("source_id",
        F.get_json_object("e", "$.authorAttribution.displayName").alias("a"),
        F.get_json_object("e", "$.publishTime").alias("t")).where("a IS NOT NULL AND t IS NOT NULL")
rv_g = rv.select(F.sha2(F.concat(F.lit("google"), "source_id", "a", "t"), 256).alias("review_id")).distinct()
rv_s = rv.select(F.sha2(F.concat(F.lit("sgm"), "source_id", "a", "t"), 256).alias("review_id")).distinct()
md = elems("$.photos").select("source_id", F.get_json_object("e", "$.name").alias("n")).where("n IS NOT NULL")
md_g = md.select(F.sha2(F.concat_ws("|", F.trim(F.lit("google")), F.trim("source_id"), F.trim("n")), 256).alias("media_dedup_key")).distinct()
md_s = md.select(F.sha2(F.concat_ws("|", F.trim(F.lit("sgm")), F.trim("source_id"), F.trim("n")), 256).alias("media_dedup_key")).distinct()
R = spark.table("lh_vv_silver.dbo.slv_3p_poi_review").select("review_id")
M = spark.table("lh_vv_silver.dbo.slv_3p_poi_media").select("media_dedup_key")
print("review_expected", rv_g.count(), "review_missing_google", rv_g.join(R, "review_id", "left_anti").count(),
      "review_hit_sgm", rv_s.join(R, "review_id", "left_semi").count())
print("media_expected", md_g.count(), "media_missing_google", md_g.join(M, "media_dedup_key", "left_anti").count(),
      "media_hit_sgm", md_s.join(M, "media_dedup_key", "left_semi").count())
```

**V-3. Dòng `google` không đổi so với `v0`.** Kỳ vọng: cả hai giá trị bằng 0.

```sql
SELECT
  (SELECT COUNT(*) FROM (
     SELECT poi_id, source_name FROM lh_vv_silver.dbo.slv_3p_poi VERSION AS OF <v0_slv_3p_poi> WHERE source_name = 'google'
     EXCEPT
     SELECT poi_id, source_name FROM lh_vv_silver.dbo.slv_3p_poi WHERE source_name = 'google')) AS google_lost,
  (SELECT COUNT(*) FROM lh_vv_silver.dbo.slv_3p_poi n
     JOIN lh_vv_silver.dbo.slv_3p_poi VERSION AS OF <v0_slv_3p_poi> o ON n.poi_id = o.poi_id
     WHERE n.source_name = 'sgm' AND o.source_name = 'google') AS google_turned_sgm;
```

**V-4. Số liệu backfill.** Lấy từ JSON exit của bước 2: `sgm_valid = 2630`, `google_priority_skipped = 402`, `takeover_poi = 0`. Lý do reject so với B-3: không có cặp (`trg_tbl`, `reject_reason`) mới. Số dòng `sgm`:

```sql
SELECT COUNT(*) AS sgm_rows FROM lh_vv_silver.dbo.slv_3p_poi WHERE source_name = 'sgm';  -- kỳ vọng 2228
```

**V-5. 0 insert khi chạy lại.** Xem mục `Chạy lại để kiểm tra idempotency`.

**V-6. Entity.** Kỳ vọng:
- `sgm_rows = 0`
- `google_rows` bằng tổng số dòng `slv_3p_poi`
- metric `sgm_as_google_rows` của lần chạy entity bằng 2228 (số dòng `sgm` ở V-4)

```sql
SELECT
  (SELECT COUNT(*) FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich WHERE source_name = 'sgm') AS sgm_rows,
  (SELECT COUNT(*) FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich WHERE source_name = 'google') AS google_rows,
  (SELECT COUNT(*) FROM lh_vv_silver.dbo.slv_3p_poi) AS slv_3p_poi_rows;

SELECT exec_id, status, entity_rows, qg_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl = 'slv_poi_entity_non_enrich'
ORDER BY started_at DESC LIMIT 1;   -- đọc metrics.sgm_as_google_rows trong qg_json
```

**V-7. Gold.** Kỳ vọng: mỗi bảng có 0 dòng `sgm`, và `DESCRIBE TABLE` trùng với B-4.

```sql
SELECT 'gld_srv_poi_info' t, COUNT(*) n FROM <GOLD_SCHEMA>.gld_srv_poi_info WHERE source_name = 'sgm'
UNION ALL SELECT 'gld_srv_poi_multi_lang', COUNT(*) FROM <GOLD_SCHEMA>.gld_srv_poi_multi_lang WHERE source_name = 'sgm'
UNION ALL SELECT 'gld_enr_poi_info', COUNT(*) FROM <GOLD_SCHEMA>.gld_enr_poi_info WHERE source_name = 'sgm';
```

**V-8. Amenity và dictionary.** Kỳ vọng:
- `amenity_rows_on_sgm_poi > 0`
- `dict_amenities_sgm = 0`
- `dict_place_type_sgm = 0`

```sql
SELECT
  (SELECT COUNT(*) FROM lh_vv_silver.dbo.slv_poi_amenity a
     JOIN lh_vv_silver.dbo.slv_3p_poi p ON a.poi_id = p.poi_id WHERE p.source_name = 'sgm') AS amenity_rows_on_sgm_poi,
  (SELECT COUNT(*) FROM <REF_SCHEMA>.ref_dictionary_amenities WHERE source_name = 'sgm') AS dict_amenities_sgm,
  (SELECT COUNT(*) FROM <REF_SCHEMA>.ref_dictionary_place_type WHERE source_name = 'sgm') AS dict_place_type_sgm;
```

**V-9. Không ghi state cho tài liệu `sgm` bị bỏ qua vì `GOOGLE_PRIORITY`.** Kỳ vọng: `skipped_keys = 402`, `new_state_rows = 0` và `state_at_sgm_ts = 0`.

```sql
WITH sgm AS (
  SELECT regexp_replace(md5(concat('google', source_id)), '^(.{8})(.{4})(.{4})(.{4})(.{12})$', '$1-$2-$3-$4-$5') AS poi_id,
         unix_millis(CAST(crawled_at AS TIMESTAMP)) AS ts_ms
  FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream WHERE lower(trim(source_name)) = 'sgm'
),
skipped AS (
  SELECT DISTINCT s.poi_id FROM sgm s
  JOIN lh_vv_silver.dbo.slv_3p_poi p ON p.poi_id = s.poi_id WHERE p.source_name = 'google'
),
now_st AS (SELECT trg_tbl, entity_key, cdc_ts_ms FROM lh_vv_ctrl.dbo.ctrl_cdc_state
           WHERE src_tbl = 'brz_3rd_crawler_poi_stream' AND entity_key IN (SELECT poi_id FROM skipped)),
v0_st AS (SELECT trg_tbl, entity_key FROM lh_vv_ctrl.dbo.ctrl_cdc_state VERSION AS OF <v0_ctrl_cdc_state>
          WHERE src_tbl = 'brz_3rd_crawler_poi_stream' AND entity_key IN (SELECT poi_id FROM skipped))
SELECT
  (SELECT COUNT(*) FROM skipped) AS skipped_keys,
  (SELECT COUNT(*) FROM (SELECT trg_tbl, entity_key FROM now_st EXCEPT SELECT trg_tbl, entity_key FROM v0_st)) AS new_state_rows,
  (SELECT COUNT(*) FROM now_st n JOIN sgm s ON n.entity_key = s.poi_id AND n.cdc_ts_ms = s.ts_ms) AS state_at_sgm_ts;
```

Thêm một kiểm tra theo `CTRL_TABLES_CONTEXT.md` §8. Kỳ vọng 0 dòng:

```sql
SELECT trg_tbl, entity_key, COUNT(*) FROM lh_vv_ctrl.dbo.ctrl_cdc_state
WHERE src_tbl = 'brz_3rd_crawler_poi_stream' GROUP BY 1, 2 HAVING COUNT(*) > 1 LIMIT 50;
```

**V-10 và V-11 — KHÔNG THUỘC LẦN CHẠY NÀY.**
- V-10 (takeover D-5) cần một fixture DEV. Fixture gồm một `source_id` chỉ có ở `sgm`, cộng một event `google` có `crawled_at` cũ hơn, ghi vào bronze DEV.
- V-11 (gate) cần chạy với `table_filter` khác rỗng trên cùng fixture.
- Cả hai đều cần người dùng **xác nhận riêng, rõ ràng** trước khi ghi vào bronze hoặc đặt `table_filter` khác rỗng. Nếu không có xác nhận đó, người dùng chấp nhận bằng chứng gồm test tĩnh cộng lần takeover tự nhiên đầu tiên (theo `architecture.md` Main brief, stop point 6).
- Quyết định của người dùng về fixture: `<CẦN NGƯỜI DÙNG CUNG CẤP: có tạo fixture V-10/V-11 hay không, ngày và người xác nhận>`.

## Chạy lại để kiểm tra idempotency

Chạy các bước này sau bước 2 và trước downstream. Không có dữ liệu bronze mới giữa các lần chạy.

**R-1. Chạy lại incremental.** Dùng tham số của activity pipeline:

```python
pl_name = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"; run_id = ""
src_schema = "lh_vv_bronze.dbo"; src_tbl = "brz_3rd_crawler_poi_stream"
allow_full_scan = False; max_parallel = 12; max_retries = 1; table_filter = ""
full_reload = False; dry_run = False; stop_on_failure = False; cast_null_policy = "FAIL"
running_timeout_minutes = 780; sources = "google,sgm"; doc_key_column = "poi_id"; state_key = "doc"
```

Kỳ vọng:
- `takeover_poi = 0`
- `ctrl_log_run.status` là `NO_DATA` hoặc `SUCCESS`
- `inserted_rows = 0` ở mọi bảng có dòng log

**R-2. Chạy lại `full_reload`.** Dùng đúng tham số của bước 2 (`full_reload = True`, `allow_full_scan = True`, `dry_run = False`, các tham số còn lại như bước 1). Kỳ vọng:
- `inserted_rows = 0` ở cả 9 bảng
- `takeover_poi = 0`
- `google_priority_skipped = 402`
- `updated_rows` được phép lớn hơn 0, vì `full_reload` cập nhật lại cùng giá trị

Kiểm tra cho mỗi lần chạy lại (thay `<exec_id>`):

```sql
SELECT trg_tbl, status, inserted_rows, updated_rows, stale_rows, applicable_rows, cast_null_rows, rejected_rows
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '<exec_id>' ORDER BY trg_tbl;
```

Sau đó chạy lại B-2. Số dòng của 9 bảng phải bằng số đếm ngay sau bước 2.

Nếu `src_version_to` của R-1 hoặc R-2 lớn hơn của bước 2, nghĩa là bronze DEV đã nhận dữ liệu mới. Khi đó V-5 không kết luận được. Ghi nhận lại và lặp lại khi bronze đứng yên.

## Kiểm tra log và watermark

**L-1. Log run.** Lấy các run extract gần nhất:

```sql
SELECT exec_id, run_id, run_mode, table_filter, status, src_version_from, src_version_to,
       read_mode, read_rows, valid_rows, ignored_rows, rejected_rows, ignored_detail,
       tbl_total_count, tbl_success_count, tbl_failed_count, tbl_no_data_count,
       started_at, ended_at, duration_ms, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE src_tbl = 'brz_3rd_crawler_poi_stream'
ORDER BY started_at DESC LIMIT 10;
```

Kỳ vọng:
- Bước 1 có `run_mode = DRY_RUN`, nếu dry run có ghi log.
- Bước 2 và R-2 có `run_mode = FULL_RELOAD`, `status = SUCCESS`, `tbl_failed_count = 0`.
- R-1 có `run_mode = INCREMENTAL`.
- `table_filter` là NULL hoặc rỗng ở mọi run.
- `ignored_detail` tách `GOOGLE_PRIORITY` theo `source_name`, với 402 tài liệu thuộc `sgm`.

**L-2. Log theo bảng của run thật:**

```sql
SELECT trg_tbl, priority, attempt_no, status, input_rows, stale_rows, applicable_rows,
       entity_rows, inserted_rows, updated_rows, cast_null_rows, rejected_rows, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id = '<exec_id bước 2>' ORDER BY priority, trg_tbl;
```

Kỳ vọng:
- Có 9 bảng, mỗi bảng `SUCCESS` hoặc `NO_DATA`.
- `cast_null_rows = 0`.
- Riêng `slv_3p_poi` có `inserted_rows` ≥ 2228, chênh lệch là dữ liệu `google` mới nếu có.

**L-3. Watermark.** Chạy lại truy vấn ở bước 4 phần `Điều kiện tiên quyết`. Kỳ vọng:
- `lock_exec_id` là NULL.
- `status = SUCCESS`.
- `last_run_id` là run cuối cùng.
- `last_src_version` không lùi so với giá trị đã ghi trước bước 2.

**L-4. State 3P.** So số dòng state với B-2:

```sql
SELECT trg_tbl, COUNT(*) AS n FROM lh_vv_ctrl.dbo.ctrl_cdc_state
WHERE src_tbl = 'brz_3rd_crawler_poi_stream' GROUP BY trg_tbl ORDER BY trg_tbl;
```

Kỳ vọng: số dòng chỉ tăng ở các khoá `poi_id` mới của `sgm`, và không đổi giữa bước 2, R-1 và R-2.

**L-5. Reject.** Chạy lại B-3. Kỳ vọng: không có cặp (`trg_tbl`, `reject_reason`) mới.

## Rollback và forward recovery

**Forward recovery (ưu tiên):**
- `PARTIAL_FAILED` hoặc một bảng `FAILED` (kể cả `CastNullError` khi `cast_null_policy = "FAIL"`): watermark được giữ nguyên. Đọc `error_message` ở L-1 và L-2, sửa nguyên nhân, rồi chạy lại đúng tham số của bước 2. Run sau sẽ làm lại cùng phạm vi và vẫn cho 0 insert trùng.
- `SKIPPED_CONCURRENT`: đợi run kia kết thúc. Chỉ nhả khoá theo `CTRL_TABLES_CONTEXT.md` §4 khi chắc chắn không còn run nào, và phải có người dùng xác nhận.
- `takeover_deferred > 0`: không xảy ra trong lần backfill này, vì kỳ vọng `takeover_poi = 0`. Nếu xuất hiện thì DỪNG và báo lại. Run đầy đủ tiếp theo (không `table_filter`) sẽ làm lại takeover.
- Downstream lỗi: sửa nguyên nhân rồi chạy lại node đó và các node sau theo đúng thứ tự ở bước 4.

**Rollback — dừng nhận `sgm` (làm trước tiên):**
1. Đặt `sources = "google"` trên activity 3P của `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` trước.
2. Sau đó đặt `sources = "google"` ở default của cell `e3eb64e4`. Có thể làm trong cùng lần deploy, nhưng không được muộn hơn bước 3.
3. Chỉ revert code notebook sau, hoặc cùng lúc, khi `sources` đã về `google`. Nếu revert notebook trong khi silver còn dòng `sgm`, D-3 và D-5 không còn được bảo vệ.

Các dòng `sgm` đã ghi vẫn ở lại. Chúng hợp lệ dưới danh tính `google`. Event `sgm` mới sẽ thành `IGNORED` / `OUT_OF_SCOPE`.

**Rollback — xoá dữ liệu `sgm` (phá huỷ, KHÔNG làm trong runbook này):** cần **xác nhận riêng, rõ ràng** của người dùng trước bất kỳ lệnh DELETE nào. Phạm vi theo `architecture.md` `## Rollback and forward recovery`:
- Lấy tập `P` gồm `poi_id` của `slv_3p_poi` có `source_name = 'sgm'`.
- Xoá các dòng thuộc `P` ở cả 9 bảng.
- Xoá các dòng `ctrl_cdc_state` có `src_tbl = 'brz_3rd_crawler_poi_stream'` và `entity_key` thuộc `P`.
- Dòng con `sgm` còn sót trên POI đã bị `google` takeover được tìm bằng cách khớp `_event_id` của dòng con với `event_id` bronze có `source_name = 'sgm'`.
- Sau đó để các node `RECOMPUTE` chạy lại.

Trước khi xin xác nhận, chỉ được chạy truy vấn đếm (chỉ đọc):

```sql
SELECT COUNT(*) AS p_size FROM lh_vv_silver.dbo.slv_3p_poi WHERE source_name = 'sgm';
```

Xác nhận DELETE: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận riêng nếu cần xoá dữ liệu sgm>`.

## Kết quả người dùng ghi nhận

Người vận hành điền mục này. Không để trống bằng giá trị đoán.

| Mục | Kỳ vọng | Thực tế | PASS/FAIL |
|---|---|---|---|
| Test local + `run-gate` | PASS | | |
| B-1 `sgm` trước run | 0 | | |
| B-2 số dòng 9 bảng + state | ghi số | | |
| B-5 `v0` (9 bảng + `ctrl_cdc_state`) | ghi version | | |
| `last_src_version` trước bước 2 | ghi số | | |
| Bước 1 dry run full_reload: `sgm_valid` / bỏ qua / `google_priority_skipped` / `takeover_poi` / cast null | 2630 / 402 / 402 / 0 / 0 | `exec_id=9d8db495-d090-483c-978c-459163c2f739`. `read_mode=FULL`. `sgm_valid=2630`, log bỏ qua 402, field `google_priority_skipped=0`, `takeover_poi=0`, `cast_null=0`, `rejected=0`, `valid=26583`, `read=26985`. Không ghi. PASS theo số dòng; field counter lệch | PASS với ghi chú |
| Bước 2 `exec_id`, `status` | ghi, `SUCCESS` | `17986a1c-353e-4eb1-ab68-c1afaa13d8f9`, `SUCCESS`. `slv_3p_poi` ins=2228 upd=20537. Bảy bảng DOC ins=2228. Review và media ins=0. `takeover_poi=0`, `cast_null=0`, bỏ qua 402. `v0` chưa thấy trong báo cáo | PASS bước ghi; thiếu `v0` |
| V-1 khoá duy nhất (9 bảng) | `n = n_key` | Cả 9 bảng `n = n_key`. `slv_3p_poi` và address 22765. Năm bảng contact/price/hours/rating/amenity 23036. Review 121479. Media 258032 | PASS |
| V-2 `sgm_poi_not_google_hash`; review/media `missing_google`, `hit_sgm` | 0; 0, 0 | `sgm_poi_not_google_hash=0`. Spot-check review/media chưa chạy | PASS phần poi |
| V-3 `google_lost`, `google_turned_sgm` | 0, 0 | chưa có `v0` | |
| V-4 JSON exit; `sgm_rows` | 2630 / 402 / 0; 2228 | `sgm_rows=2228` | PASS |
| V-5 R-1 `inserted_rows` (mọi bảng) | 0 | `9609d878-c47e-4368-80c6-d7c00589eaeb` NO_DATA, read 0, inserted 0 | PASS |
| V-5 R-2 `inserted_rows` (9 bảng) | 0 | `eafc3d5a-d4a9-422c-a011-f558e71632af`. Bảy bảng DOC ins=0. Review ins=11797. Media ins=16616 | FAIL |
| V-5 xác nhận sau khi ghi bù | 0 | `449d25da-3c06-40f7-9358-23537aa53589`. Cả 9 bảng ins=0. `rows.inserted=0`. Review upd=121399. Media upd=257502 | PASS |
| V-6 entity `sgm_rows`; `google_rows` = `slv_3p_poi_rows`; `sgm_as_google_rows` | 0; bằng nhau; 2228 | `167046e1-7155-45f2-8d61-f7258c788f90` SUCCESS. 0, 22765, 22765. `sgm_as_google_rows=2228`. Insert 2228, update 0. Nguồn 23060 = 22765 + 295 partner | PASS |
| V-7 gold `sgm` (3 bảng); tập cột | 0; không đổi | `gld_srv_poi_info=0`, `gld_srv_poi_multi_lang=0`, `gld_enr_poi_info=0`. Tập cột không đối chiếu vì B-4 chưa ghi; task không đổi DDL gold | PASS phần đếm |
| V-8 amenity trên POI `sgm`; dictionary `sgm` | > 0; 0, 0 | `f864fb03-82e9-42b8-80af-a6c86449a550` amenity SUCCESS, insert 213. `4a0a8266-945c-4087-9d17-088a5c7ebcb4` media SUCCESS, insert 16616. V-8: 213, 0, 0 | PASS |
| V-9 `skipped_keys` / `new_state_rows` / `state_at_sgm_ts`; trùng state | 402 / 0 / 0; 0 dòng | `skipped_keys=402`, `state_at_sgm_ts=0`, `duplicate_state_keys=0`. `new_state_rows` chưa tính vì không có `v0` | PASS phần tính được |
| L-3 watermark sau cùng | không khoá, `SUCCESS`, không lùi | `status=SUCCESS`, `last_src_version=273`, `watermark_value=2026-11-18T05:11:31Z`, `lock_exec_id` null. `last_run_id=673ae7a7-72c6-4562-97d7-8a8bb361e6bc` không nằm trong các `exec_id` đã dán | PASS |
| L-5 reject mới | không | 0 dòng chưa xử lý | PASS |
| V-10, V-11 | không thuộc lần chạy này | người dùng chấp nhận không chạy, 2026-11-19 | PASS với ghi chú |
| Quyết định fixture V-10/V-11 | người dùng quyết định | không tạo fixture; chấp nhận cùng kết luận runtime | PASS với ghi chú |

Kết luận của người dùng (`PASS` / `FAIL`), ngày chạy, người chạy: `PASS`, 2026-11-19, Bách. Gồm các mục chưa chứng minh: V-3, `new_state_rows`, spot-check review/media, V-10/V-11.

Bước 1 lúc 2026-11-19 06:41 UTC, `exec_id=3a7e0da3-5010-4118-8e7d-dfb02120d4d7`. `run_mode=DRY_RUN`, `read_mode=VERSION`, `read_note=không có commit mới (v273)`, `status=NO_DATA`, `rows.read=0`, `sgm_valid=0`, `google_priority_skipped=0`, `takeover_poi=0`, `takeover_enabled=true`, `google_owned_stored=20537`, `poi_owner_version=2`, `last_src_version=273`, `watermark_from=2026-11-18 05:11:31.292870`. Không ghi bảng. Đây chưa phải preview backfill: `full_reload` không bật nên các dòng `sgm` cũ nằm trước watermark không được đọc. Chưa chạy bước 2.

Bước 1 full_reload lúc 2026-11-19 06:48 UTC, `exec_id=9d8db495-d090-483c-978c-459163c2f739`. `read_mode=FULL`, `status=SUCCESS`, `dry_run` nên `inserted=0`. `sgm_valid=2630`. Hợp lệ 26583, bỏ qua 402, lỗi 0. 26583 - 24355 dòng google = 2228 dòng `sgm` còn lại, đúng `sgm_only`. `takeover_poi=0`, `cast_null=0`. `slv_3p_poi` chạy trước 8 bảng con. Field `google_priority_skipped=0` không khớp log bỏ qua 402; số dòng vẫn đúng D-3. `unmapped_top_keys` chỉ là watch, không reject. `x_lodging` và `x_scraper` có 2228, đúng tập chỉ `sgm`.

Bước 2 lúc 2026-11-19 06:57 UTC, `exec_id=17986a1c-353e-4eb1-ab68-c1afaa13d8f9`, `run_mode=FULL_RELOAD`, `status=SUCCESS`. `sgm_valid=2630`, hợp lệ 26583, bỏ qua 402, lỗi 0, `takeover_poi=0`, `cast_null=0`. Insert: `slv_3p_poi`, address, contact, price, rating, amenity, opening_hours mỗi bảng 2228. 2228 x 7 = 15596, khớp `rows.inserted`. Review ins=0 upd=109602. Media ins=0 upd=240886. `docs_by_table` review 24352 và media 24355 không gồm 2228 dòng `sgm` chỉ có một mình, nên hai bảng đó không có dòng mới. Update trên `slv_3p_poi` là 20537 dòng `google` đã có, do `full_reload` ghi lại. Chưa có `v0` trong báo cáo. Chưa chạy R-1, R-2, downstream, V-1 đến V-9.

Xác nhận idempotency lúc 2026-11-19 07:25 UTC, `exec_id=449d25da-3c06-40f7-9358-23537aa53589`, `FULL_RELOAD`, `SUCCESS`. `rows.inserted=0`. `slv_3p_poi` và address upd=22765. contact, price, rating, amenity, opening_hours upd=22732. Review ins=0 upd=121399. Media ins=0 upd=257502. `sgm_valid=2630`, bỏ qua 402, `takeover_poi=0`, `cast_null=0`, `src_version=273`. `google_owned_stored=20537` nên 2228 dòng vẫn không bị đếm là `google`. `poi_owner_version=4`.

Entity lúc 2026-11-19 07:41 UTC, `exec_id=167046e1-7155-45f2-8d61-f7258c788f90`, `SUCCESS`. V-6: `sgm_rows=0`, `google_rows=22765`, `slv_3p_poi_rows=22765`. `sgm_as_google_rows=2228`. Diff insert 2228, update 0, xoá mềm 0. Nguồn 23060 = 22765 google + 295 partner. `non_google_rows=0`. Cảnh báo partner không thuộc `sgm`.

Amenity lúc 2026-11-19 07:51 UTC, `exec_id=f864fb03-82e9-42b8-80af-a6c86449a550`, `SUCCESS`. Insert 213, update 0, xoá mềm 0. Nguồn 42545. `trg_version=6`. Media lúc 2026-11-19 07:53 UTC, `exec_id=4a0a8266-945c-4087-9d17-088a5c7ebcb4`, `SUCCESS`. Insert 16616, update 0, xoá mềm 0. Nguồn 259063. `trg_version=5`. V-8: `amenity_rows_on_sgm_poi=213`, `dict_amenities_sgm=0`, `dict_place_type_sgm=0`. 213 amenity mới nằm trên POI `sgm`. Cảnh báo partner không thuộc `sgm`. Chưa chạy enrich và gold.

NB_00 lúc 2026-11-19 09:10 UTC, `exec_id=aa12e1da-3ce0-4662-9d50-0422f454757c`, `PL_VV_TRANS_SLV_TO_GLD_30M`, `PARTIAL_FAILED`. Watermark lỗi tạm rồi thử lại được. Kế hoạch 5 node, cả 5 `NOT_RUN`. `runMultiple` 404: workspace không có `NB_GLD_SRV_POI_REVIEW`. Không ghi gold. V-7 chưa chạy. `NB_ENR_POI_INFO` không nằm trong pipeline 30M này.

Enrich lúc 2026-11-19 09:15 UTC, `exec_id=2eed85b5-15de-46fd-9c72-95df2ec90baa`, `PL_VV_TRANS_SLV_TO_ENR_15M`, `SUCCESS`. Nguồn 23060. Insert 2228, update 16820, xoá mềm 0. `trg_version=7`. Cảnh báo `review_poi_not_in_entity=1`, `multi_lang_key_not_in_entity=1`, `cost_null=10532`, `avg_range_min_unfixed=1507`. Gold info lúc 09:37 UTC và multi_lang lúc 09:36 UTC cùng `exec_id=e11068da-a728-4d46-9330-b17dcb54b6e0`, `PL_VV_TRANS_SLV_TO_GLD_30M`, cả hai `SUCCESS`. Info: nguồn 19909, insert 16817, update 2, `trg_version=16`. Multi_lang: nguồn 59726, insert 50917, update 9, `trg_version=8`. Cảnh báo `multi_lang_source_name_null=3`, `multi_lang_i18n_only_rows=44`.

V-7 lúc 2026-11-19: `gld_srv_poi_info=0`, `gld_srv_poi_multi_lang=0`, `gld_enr_poi_info=0`. Ba bảng gold không có dòng `source_name=sgm`.

V-9, L-3, L-5 lúc 2026-11-19: `skipped_keys=402`, `state_at_sgm_ts=0`, `duplicate_state_keys=0`. Watermark `SUCCESS`, không khóa, `last_src_version=273`, mốc `2026-11-18T05:11:31Z` không lùi. `last_run_id=673ae7a7-72c6-4562-97d7-8a8bb361e6bc` chưa có trong các log đã dán. Reject chưa xử lý: 0 dòng.

Kết luận runtime của Bách lúc 2026-11-19: `PASS`. Các mục chưa chứng minh vẫn là V-3, `new_state_rows`, spot-check review/media, và V-10/V-11. `gates.runtime=pass`. Cùng ngày, D-6 đóng `specialist_review` và `risk_gate` thành `pass` vì GATE-001 và GATE-002 đã accepted-risk, rồi chuyển `ready_to_merge`.
