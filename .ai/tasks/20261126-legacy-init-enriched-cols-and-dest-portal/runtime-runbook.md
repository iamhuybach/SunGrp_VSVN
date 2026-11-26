# Runtime runbook — 20261126-legacy-init-enriched-cols-and-dest-portal

## Phạm vi và môi trường

- Môi trường: Fabric DEV, workspace `sgr_visitvn_dev`. Người dùng tự chạy mọi bước. Agent không chạy gì trên Fabric.
- Việc cần làm:
  1. Silver `lh_vv_silver.dbo.slv_enr_poi_destination` có thêm cột `destination_portal_id` STRING NULL ngay sau `destination_id`. Dòng đang có được backfill tại chỗ từ đúng event bronze đã sinh ra dòng đó: `destination_id` ← `destinations[].strapi_document_id`, `destination_portal_id` ← `destinations[].id` (D-DEST-ID, D-DEST-PORTAL, D-DEST-ARRAY, D-DEST-BACKFILL).
  2. Extract `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` chiếu thêm `strapi_document_id` và có guard `PATCH_COLS`.
  3. Gold `gld_srv_poi_info.destination_id` copy lại silver qua `PL_VV_TRANS_SLV_TO_GLD_30M` (D-DEST-GOLD).
  4. Init legacy `NB_SETUP_LEGACY_GOLD_POI` điền `old_address`, `price_level`, `price_min`, `price_max` (dòng `vi` qua `vi_key`, D-INIT-INFO-VI) và `story`, `local_tips` theo `(legacy_poi_id, lang)` (D-INIT-KEY, D-LANG-ROW) từ `ai_enriched_poi` tại pin.
- Ngoài phạm vi:
  - `destination_id` của phần INIT (dòng `load_origin = 'LEGACY_INIT'`) đã đúng. Không đổi mapping, không chạy lại riêng (D-LEGACY-DEST, ý kiến người dùng 26/11).
  - `destination_portal_id` chỉ có ở silver. Nó không có trong gold, PostgreSQL hay API (D-DEST-SCOPE).
  - Không chạy lại `enrbrzpy` sau `destportalpy`.
- Bảng ctrl liên quan: `lh_vv_ctrl.dbo.ctrl_mng_watermark` (dòng `wm_transform_brz_enrichment_result`, `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`), `ctrl_cfg_schema_registry`, `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_cdc_state`.
- Mọi truy vấn trong runbook chỉ đọc, trừ các bước chạy notebook hoặc pipeline. Mẫu kết quả tối đa 50 dòng. Không xuất dữ liệu cá nhân.
- Truy vấn dùng tên 3 phần `lh_vv_*.dbo.*`. Hãy chạy chúng trong một notebook Spark SQL của workspace `sgr_visitvn_dev`.

## Điều kiện tiên quyết

1. Local đã PASS bước STOP evidence (architecture.md Main brief, Order mục 2):
   `python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_enr_extract_contract.py tests/test_legacy_gold_poi_init_contract.py tests/test_gld_srv_poi_contract.py tests/test_srv_poi_serving_contract.py -q` và `python scripts/vv.py verify`. Review spark-runtime-reviewer và sql-data-reviewer không còn P0/P1. SPARK-001 và SPARK-002 đã `fixed`.
2. Các notebook đã sửa đã được đưa lên DEV. Phải publish `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` trước mọi lần chạy cần `PATCH_COLS`, tức trước bước 2. Sau bước 2, code extract cũ không được chạy nữa.
3. Không có run nào khác đang chạy trên extract enrichment hoặc trên luồng GLD_30M. Kiểm tra bằng truy vấn B1 và B2 ở mục Baseline.
4. Tham số người dùng phải cung cấp:
   - Pin gốc của lần init legacy trước, cho 5 bảng `poi_master`, `poi_enrichment_display`, `poi_detail`, `poi_review`, `poi_rating` (architecture §16): `<CẦN NGƯỜI DÙNG CUNG CẤP: version Delta của 5 bảng tại sgr_visitvn_prd_batch.lh_vv_gold.dbo, đúng pin của lần init LEGACY_INIT trước>`.
   - Tham số pipeline GLD_30M `nb_orches_id`: `<CẦN NGƯỜI DÙNG CUNG CẤP: id notebook NB_00_ORCHES_SLV_TO_GLD trên DEV>`.
   - Tham số pipeline GLD_30M `workspace_id`: `<CẦN NGƯỜI DÙNG CUNG CẤP: workspace id của sgr_visitvn_dev>`.
5. Số kỳ vọng lấy từ evidence P-DEST-1 (decision.md): `silver_n = 19799`, `old_n = 19799`, `empty_n = 2`. Các gate `no_event_n`, `dup_payload_n`, `name_bad_n`, `drift_n`, `strapi_missing_n` đều bằng 0. Nếu silver có event mới sau lần probe, `silver_n` và `old_n` có thể khác 19799. Khi đó dừng lại và báo người dùng trước khi ghi.

## Baseline trước khi chạy

Chạy các truy vấn sau và lưu kết quả vào `evidence/results/` (Main lưu).

B1 — khoá và watermark của extract:
```sql
SELECT watermark_id, status, last_src_version, last_success_at, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN ('wm_transform_brz_enrichment_result', 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M');
```
Kỳ vọng: `lock_exec_id` NULL trên cả hai dòng.

B2 — không có run đang chạy:
```sql
SELECT exec_id, pl_name, nb_name, src_tbl, run_mode, status, started_at, ended_at
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE (src_tbl = 'brz_enrichment_result' OR pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M')
ORDER BY started_at DESC LIMIT 20;
```
Kỳ vọng: không có dòng `status = 'RUNNING'`.

B3 — registry hiện tại của bảng destination:
```sql
SELECT trg_column, json_path, column_order, is_active
FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry
WHERE src_tbl = 'brz_enrichment_result' AND trg_tbl = 'slv_enr_poi_destination'
ORDER BY column_order;
```
Ghi lại `json_path` của `destination_id`. Trước bước 2 giá trị kỳ vọng là `destinations.id`.

B4 — schema và version silver:
```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_enr_poi_destination;
DESCRIBE HISTORY lh_vv_silver.dbo.slv_enr_poi_destination LIMIT 5;
SELECT count(*) AS silver_n, count(DISTINCT poi_id) AS key_n,
       count(destination_id) AS dest_nonnull_n
FROM lh_vv_silver.dbo.slv_enr_poi_destination;
```
Ghi lại `version` đầu tiên, gọi là `v_silver_baseline`. Kỳ vọng: chưa có cột `destination_portal_id`, và `silver_n = key_n`.

B5 — gold và LEGACY_INIT:
```sql
DESCRIBE HISTORY lh_vv_gold.dbo.gld_srv_poi_info LIMIT 5;
DESCRIBE HISTORY lh_vv_gold.dbo.gld_srv_poi_multi_lang LIMIT 5;
SELECT load_origin, count(*) AS n, count(destination_id) AS dest_n,
       count(old_address) AS old_address_n,
       count(coalesce(price_level, price_min, price_max)) AS price_n
FROM lh_vv_gold.dbo.gld_srv_poi_info GROUP BY load_origin;
SELECT count(*) AS n, count(story) AS story_n, count(local_tips) AS local_tips_n
FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang;
```
Ghi lại version mới nhất của `gld_srv_poi_info`, gọi là `v_info_baseline`. Bước kiểm tra sẽ dùng version này để so `destination_id` của LEGACY_INIT. Theo P-LEGDEST-2: LEGACY_INIT có 34254 dòng (34167 dòng có `destination_id`); `load_origin` trống có 19909 dòng (19799 dòng có `destination_id`).

## Các bước thực hiện

### Bước 1 — Publish extract
Publish `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` lên DEV. Ở bước này chưa chạy gì. Với registry cũ, notebook mới chạy y như code cũ (architecture §7.1).

### Bước 2 — Seed registry (NB_CREATE_DDL)
Mở `NB_CREATE_DDL` trên DEV và chạy lần lượt từng cell, không chạy cả notebook:
1. `28e2be98-7f9a-41d5-b7f8-b4d4a5baf5ff`: định nghĩa `TABLE_CONFIGS`.
2. `0f228dc1-7bc8-4ed2-a10f-e6125a806e83`: `seed_registry` / `show_registry`, ghi bằng `replaceWhere` theo từng nguồn. Chạy lại cho cùng kết quả.
3. `enrbrzcfgpy`: seed `TABLE_CONFIGS_ENR` cho `brz_enrichment_result`.

Kiểm tra: chạy lại B3. Kỳ vọng 3 dòng active liền nhau: `destination_id` → `destinations.strapi_document_id`, `destination_portal_id` → `destinations.id`, `destination_name` → `destinations.name`. `column_order` của portal phải bằng `column_order` của `destination_id` + 1.

Từ lúc này đến hết bước 3, extract sẽ dừng với `ConfigError("slv_enr_poi_destination thiếu ['destination_portal_id']: chạy destportalpy")` và không ghi gì. Đây là hành vi đúng. Không chạy extract trong khoảng này.

### Bước 3 — Chạy `destportalpy` (NB_CREATE_DDL)
Chỉ chạy cell `destportalpy`, nằm sau `destportalmd`. Cell không có tham số. Các hằng số trong cell:
- `WID = "wm_transform_brz_enrichment_result"`, `LEASE_MINUTES = 90`
- `DEST_FQ = "lh_vv_silver.dbo.slv_enr_poi_destination"`, `BRZ_FQ = "lh_vv_bronze.dbo.brz_enrichment_result"`
- `DEST_ELEM_SCHEMA = "array<struct<id:string,name:string,strapi_document_id:string>>"`
- `LOCK = "destportal-" + uuid4().hex`; commit MERGE có tag `DESTPORTAL:<LOCK>`.

Trình tự trong cell:
1. Nhận khoá.
2. Gate registry. Lỗi thì báo `chạy enrbrzcfgpy`.
3. Gate schema.
4. Plan `pre` và các gate `# Dừng trước khi ghi`.
5. Touch khoá, rồi `ALTER TABLE … ADD COLUMNS (destination_portal_id STRING AFTER destination_id)` nếu thiếu cột. Tính `mid`, phải bằng `pre`.
6. Touch khoá, rồi chạy một MERGE backfill.
7. Post-check `# Sau khi ghi`.
8. Nhả khoá trong `finally`.

Kỳ vọng ở dòng `print(pre)`:
- `old_n = 19799`, `empty_n = 2`, `new_n = 0`, `silver_n = key_n = old_n + new_n`.
- `no_event_n = dup_payload_n = name_bad_n = drift_n = strapi_missing_n = 0`.

Kỳ vọng ở dòng in cuối `{v_pre, v_post, updated_n, pre, post}`:
- `updated_n = pre.old_n = 19799`.
- `post.old_n = 0`, `post.drift_n = 0`, `post.new_n = post.silver_n`.

Điểm dừng:
- Cell báo `dừng trước khi ghi: [...]`, `schema … không khớp TABLE_COLS`, `plan sau ALTER khác plan trước` hoặc `sau khi ghi lệch`: dừng, lưu output, báo người dùng. Không sửa code để vượt gate.
- `old_n` khác 19799 nhưng mọi gate vẫn bằng 0 (silver có event mới sau probe): cell sẽ ghi. Ghi chú lại số này trong mục Kết quả và báo người dùng.

**Nếu cell bị hủy giữa chừng (SPARK-002):**
1. Dừng session Spark đang dùng và mở session mới. Nếu `finally` không kịp chạy, conf `spark.databricks.delta.commitInfo.userMetadata` có thể vẫn còn trong session cũ.
2. Kiểm tra khoá:
   ```sql
   SELECT watermark_id, lock_exec_id, lock_at, current_timestamp() AS now_ts,
          lock_at + INTERVAL 90 MINUTES AS lease_end
   FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
   WHERE watermark_id = 'wm_transform_brz_enrichment_result';
   ```
   - `lock_exec_id` NULL: khoá trống, chạy lại cell `destportalpy`.
   - `lock_exec_id` bắt đầu bằng `destportal-` và `now_ts >= lease_end`: chạy lại cell. `_take` tự lấy lại khoá quá hạn 90 phút.
   - `lock_exec_id` bắt đầu bằng `destportal-` và `now_ts < lease_end`: đợi tới `lease_end` (tối đa 90 phút kể từ `lock_at`), rồi chạy lại cell. Nếu chạy sớm, cell sẽ báo `wm_transform_brz_enrichment_result đang bị giữ` và không ghi gì.
   - `lock_exec_id` không bắt đầu bằng `destportal-`: khoá đang thuộc một run extract. Chạy B2. Nếu run đó còn `RUNNING`, đợi nó kết thúc. Không chạy `destportalpy` khi extract còn chạy, vì sau 90 phút `_take` sẽ lấy khoá của run đó.
3. Trạng thái an toàn sau khi hủy:
   - Hủy sau ALTER, trước MERGE: dòng vẫn OLD, cột mới NULL. Lần chạy lại bỏ qua ALTER và chạy MERGE.
   - Hủy trong lúc MERGE: không có commit.
   - Chạy lại sau một backfill đã thành công: `updated_n = 0`.

### Bước 4 — Chạy lại `destportalpy` (idempotency)
Chạy lại đúng cell `destportalpy`, không sửa gì. Xem kỳ vọng ở mục "Chạy lại để kiểm tra idempotency".

### Bước 5 — Extract: dry run, rồi chạy thật
Chạy tay `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`. Giá trị tham số lấy từ cell `enr01`:

| Tham số | Dry run | Chạy thật |
|---|---|---|
| `pl_name` | `"PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"` | `"PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"` |
| `run_id` | `""` (chạy tay) | `""` |
| `src_schema` | `"lh_vv_bronze.dbo"` | `"lh_vv_bronze.dbo"` |
| `src_tbl` | `"brz_enrichment_result"` | `"brz_enrichment_result"` |
| `allow_full_scan` | `True` | `True` |
| `max_parallel` | `2` | `2` |
| `max_retries` | `1` | `1` |
| `table_filter` | `""` | `""` |
| `full_reload` | `False` | `False` |
| `dry_run` | **`True`** | `False` |
| `stop_on_failure` | `False` | `False` |
| `cast_null_policy` | `"FAIL"` | `"FAIL"` |
| `running_timeout_minutes` | `780` | `780` |

- Dry run phải qua guard `PATCH_COLS`, tức không có `ConfigError … chạy destportalpy`. Silver không có version mới so với `v_post` của bước 3.
- Chạy thật: status `SUCCESS` hoặc `NO_DATA`. Event mới (nếu có) được MERGE với 3 phép chiếu mới.

### Bước 6 — `PL_VV_TRANS_SLV_TO_GLD_30M`
Trigger pipeline một lần với các tham số:
- `nb_orches_id` = `<CẦN NGƯỜI DÙNG CUNG CẤP: id NB_00_ORCHES_SLV_TO_GLD trên DEV>`
- `workspace_id` = `<CẦN NGƯỜI DÙNG CUNG CẤP: workspace id sgr_visitvn_dev>`
- `p_force_run` = `true` (khuyến nghị). Nếu để mặc định `false`, gate có thể trả `NO_DATA` và bỏ qua run.
- `p_max_idle_min` = `0` (mặc định).

Pipeline cố định các tham số NB_00: `p_mode = RUN`, `p_max_parallel = 3`, `p_node_timeout_min = 20`, `p_dag_timeout_min = 45`, `p_lock_timeout_min = 90`, `p_force_nodes = ""`, `p_history_limit = 1000`, `p_non_data_ops = ""`. Sau run này, gold `destination_id` copy silver.

### Bước 7 — `NB_SETUP_LEGACY_GOLD_POI`: PLAN → RUN → RUN
Tham số ở cell `lgpparams`: `p_mode`, `p_pin_json`, `p_target_ws`. `p_target_ws` = `"sgr_visitvn_dev"`. Notebook kiểm tra regex `[A-Za-z][A-Za-z0-9_]*`, và giá trị không được là `sgr_visitvn_prd_batch`.

`p_pin_json` là JSON `{bảng: version}`. Bảng nào không có trong JSON thì notebook tự lấy version mới nhất của bảng đó và in ra ở `summary["pins"]`.

1. **PLAN**
   - `p_mode = "PLAN"`, `p_target_ws = "sgr_visitvn_dev"`
   - `p_pin_json = '{"poi_master": <CẦN NGƯỜI DÙNG CUNG CẤP>, "poi_enrichment_display": <CẦN NGƯỜI DÙNG CUNG CẤP>, "poi_detail": <CẦN NGƯỜI DÙNG CUNG CẤP>, "poi_review": <CẦN NGƯỜI DÙNG CUNG CẤP>, "poi_rating": <CẦN NGƯỜI DÙNG CUNG CẤP>}'`
   - Lấy `summary["pins"]["ai_enriched_poi"]` từ exit JSON và gọi là `<AI_PIN>`.
   - Kiểm tra trong output: `enriched.decision`, `info.destination_changed_n`, `drift_n`.
2. **RUN lần 1**
   - `p_mode = "RUN"`, `p_target_ws = "sgr_visitvn_dev"`
   - `p_pin_json` = 5 pin gốc như trên, cộng `"ai_enriched_poi": <AI_PIN>`.
3. **RUN lần 2**: tham số giống hệt RUN lần 1.

Điểm dừng (STOP, người dùng quyết định):
- `enriched.decision != OK` (RUN báo `USER_DECISION ai_enriched_poi: …`): dừng, lưu exit JSON, hỏi người dùng. Không đổi code. Không đổi và không chạy lại mapping `destination_id` của LEGACY_INIT (D-LEGACY-DEST).
- `info.destination_changed_n > 0` chỉ là số báo cáo (D-DEST-KEEP). RUN vẫn ghi sáu cột và không cập nhật `destination_id` của dòng LEGACY_INIT.
- `destination.decision != OK`: dừng và hỏi người dùng.
- `map.drift_n` > 0 chỉ là số báo cáo (D-MAP-DRIFT). Map ghi insert-only nên dòng đã có không đổi. RUN vẫn tiếp tục ghi sáu cột.

RUN giữ khoá luồng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` (`LOCK_TIMEOUT_DEFAULT_MIN`), nên không chạy cùng lúc với bước 6.

## Kiểm tra kết quả

Silver, sau bước 3 và bước 5:
```sql
-- K1: kỳ vọng 0
SELECT count(*) FROM lh_vv_silver.dbo.slv_enr_poi_destination
WHERE size(from_json(destination_id,'array<string>')) <> size(from_json(destination_portal_id,'array<string>'))
   OR size(from_json(destination_id,'array<string>')) <> size(from_json(destination_name,'array<string>'));
-- K2: kỳ vọng 0
SELECT count(*) FROM lh_vv_silver.dbo.slv_enr_poi_destination
WHERE destination_portal_id IS NULL AND destination_id IS NOT NULL;
-- K3: kỳ vọng empty_n = 2 (theo evidence)
SELECT count(*) AS empty_n FROM lh_vv_silver.dbo.slv_enr_poi_destination WHERE destination_portal_id = '[]';
-- K4: schema, kỳ vọng thứ tự destination_id, destination_portal_id, destination_name
DESCRIBE TABLE lh_vv_silver.dbo.slv_enr_poi_destination;
-- K5: commit backfill
SELECT version, operation, userMetadata, operationMetrics['numTargetRowsUpdated'] AS updated_n
FROM (DESCRIBE HISTORY lh_vv_silver.dbo.slv_enr_poi_destination)
WHERE userMetadata LIKE 'DESTPORTAL:%';
```
Nếu môi trường không cho `SELECT` từ `DESCRIBE HISTORY`, chạy `DESCRIBE HISTORY … LIMIT 10` rồi đọc cột `userMetadata`. Kỳ vọng ở K5: đúng 1 commit `DESTPORTAL:` với `updated_n = 19799`.

Gold, sau bước 6:
```sql
-- K6: kỳ vọng 0 (dòng pipeline, load_origin IS NULL; nối theo poi_id)
SELECT count(*) FROM lh_vv_gold.dbo.gld_srv_poi_info g
JOIN lh_vv_silver.dbo.slv_enr_poi_destination s ON g.poi_id = s.poi_id
WHERE g.load_origin IS NULL AND NOT (g.destination_id <=> s.destination_id);
-- K7: kỳ vọng không có cột destination_portal_id ở gold
DESCRIBE TABLE lh_vv_gold.dbo.gld_srv_poi_info;
```
Nếu khoá nối gold–silver không phải `poi_id`: `<CẦN NGƯỜI DÙNG CUNG CẤP: khoá nối đúng giữa gld_srv_poi_info và slv_enr_poi_destination>`.

Init, sau RUN lần 1:
- Exit JSON phải có `enriched.decision = OK`. Tham chiếu P-AI-1: `map_miss_n = 0`, `lang_mismatch_n = 0`, `not_ok_n = 0`.
- `info.destination_changed_n` có thể vẫn 4038. Số này đếm trước khi giữ `destination_id` cũ (D-DEST-KEEP). K8 mới là bằng chứng giá trị không đổi.
- `old_address_filled_n`, `price_filled_n`, `story_filled_n`, `local_tips_filled_n` của RUN bằng số tương ứng của PLAN.
- `price_inverted_n` chỉ để báo cáo (P-AI-1 bằng 0).

```sql
-- K8: destination_id của LEGACY_INIT không đổi so với baseline; kỳ vọng 0
SELECT count(*) FROM lh_vv_gold.dbo.gld_srv_poi_info c
JOIN lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <v_info_baseline> b ON c.poi_id = b.poi_id
WHERE c.load_origin = 'LEGACY_INIT' AND b.load_origin = 'LEGACY_INIT'
  AND NOT (c.destination_id <=> b.destination_id);
-- K9: số cột đã điền theo load_origin
SELECT load_origin, count(*) AS n, count(old_address) AS old_address_n,
       count(coalesce(price_level, price_min, price_max)) AS price_n
FROM lh_vv_gold.dbo.gld_srv_poi_info GROUP BY load_origin;
-- K10: spot check story theo lang, 5 POI, chỉ hiện độ dài và hash, không in nội dung
SELECT poi_id, lang, length(story) AS story_len, sha2(story, 256) AS story_hash
FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
WHERE poi_id IN (SELECT poi_id FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
                 WHERE story IS NOT NULL GROUP BY poi_id HAVING count(*) >= 2 LIMIT 5)
ORDER BY poi_id, lang LIMIT 50;
```
Kỳ vọng ở K10: các lang khác nhau có `story_hash` khác nhau, giống nguồn. Không nhân một giá trị sang mọi lang (D-LANG-ROW).

## Chạy lại để kiểm tra idempotency

1. `destportalpy` chạy lại (bước 4):
   - `pre.old_n = 0`, `pre.new_n = pre.silver_n`, mọi gate bằng 0.
   - Không ALTER (schema đã bằng `TABLE_COLS`), không MERGE, `updated_n = 0`.
   - `v_pre = v_post`: không có version silver mới.
   - K5 vẫn chỉ có 1 commit `DESTPORTAL:`.
2. Init RUN lần 2 (bước 7.3):
   - Mọi stage có `inserted = 0`: `map`, `info`, `multi_lang`, `review`, `media`, `amenity`.
   - `enriched.decision = OK`. `destination_changed_n` có thể vẫn 4038. K8 vẫn 0.
   - Số dòng `gld_srv_poi_info` và `gld_srv_poi_multi_lang` bằng số sau RUN lần 1.
   - `updated_at` và `row_hash` của dòng LEGACY_INIT được ghi lại mỗi lần. Đây là hành vi có sẵn.
   ```sql
   -- K11: kỳ vọng 0 dòng
   SELECT poi_id, lang, count(*) AS n FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang
   GROUP BY poi_id, lang HAVING count(*) > 1 LIMIT 50;
   SELECT poi_id, count(*) AS n FROM lh_vv_gold.dbo.gld_srv_poi_info
   GROUP BY poi_id HAVING count(*) > 1 LIMIT 50;
   ```
   Chạy lại K8 sau RUN lần 2. Kỳ vọng 0.
3. Không chạy lại extract để kiểm tra riêng: guard MERGE của extract không đổi, nên chạy lại trên cùng event không ghi gì.

## Kiểm tra log và watermark

```sql
-- L1: khoá đã nhả, watermark extract đã tiến sau lần chạy thật
SELECT watermark_id, status, last_src_version, last_success_at, lock_exec_id, lock_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN ('wm_transform_brz_enrichment_result', 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M');
-- L2: các run extract và GLD_30M
SELECT exec_id, pl_name, nb_name, run_mode, status, read_rows, valid_rows, rejected_rows,
       tbl_success_count, tbl_failed_count, started_at, ended_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE src_tbl = 'brz_enrichment_result' OR pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M'
ORDER BY started_at DESC LIMIT 20;
-- L3: chi tiết bảng destination (extract) và node gold
SELECT exec_id, trg_tbl, status, input_rows, applicable_rows, inserted_rows, updated_rows,
       rejected_rows, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_tbl IN ('slv_enr_poi_destination', 'gld_srv_poi_info')
ORDER BY started_at DESC LIMIT 20;
-- L4: state CDC không trùng; kỳ vọng 0 dòng
SELECT trg_tbl, entity_key, count(*) FROM lh_vv_ctrl.dbo.ctrl_cdc_state
WHERE trg_tbl = 'slv_enr_poi_destination' GROUP BY 1, 2 HAVING count(*) > 1 LIMIT 50;
```
Kỳ vọng:
- Sau bước 3, 4 và 7: `lock_exec_id` NULL trên cả hai dòng. `destportalpy` không đổi `status` của `wm_transform_brz_enrichment_result`.
- Dry run: `run_mode = 'DRY_RUN'`, `last_src_version` giữ như baseline B1.
- Chạy thật: `status` `SUCCESS` hoặc `NO_DATA`, `tbl_failed_count = 0`. `last_src_version` và `last_success_at` tiến lên hoặc giữ nguyên (khi `NO_DATA`), không lùi.
- GLD_30M: một dòng `run_mode = 'RUN'` với `status = 'SUCCESS'`. Node `gld_srv_poi_info` có `status = 'SUCCESS'`.
- Nếu extract có dòng `ConfigError … chạy destportalpy`, đó là run nằm giữa bước 2 và bước 3. Không ghi gì, không cần xử lý.

## Rollback và forward recovery

- **Ưu tiên forward.** Mọi bước đều chạy lại được (architecture §11, §13):
  - `destportalpy` lỗi ở gate: không ghi gì. Sửa nguyên nhân (thường là chưa chạy `enrbrzcfgpy`), rồi chạy lại.
  - Lỗi sau ALTER, trước MERGE: chạy lại cell. Cách lấy lại khoá xem bước 3.
  - Extract lỗi: sửa nguyên nhân rồi chạy lại với cùng tham số.
  - Init lỗi giữa các stage: stage trước đã commit và idempotent. Chạy lại với cùng `p_pin_json`, gồm cả `ai_enriched_poi` lấy từ `summary["pins"]`.
- **Rollback giá trị silver** (chỉ khi người dùng quyết định). `destination_portal_id` giữ đúng giá trị `destination_id` cũ (P-DEST-1 `id_eq_n = silver_n`):
  1. Dưới khoá extract `wm_transform_brz_enrichment_result`, chạy một lần `UPDATE lh_vv_silver.dbo.slv_enr_poi_destination SET destination_id = destination_portal_id WHERE destination_portal_id IS NOT NULL`.
  2. Publish lại extract bản trước.
  3. Seed lại registry bằng text `enrbrzcfgpy` bản trước.
  4. Cột NULL-able `destination_portal_id` có thể để nguyên.
  Lệnh UPDATE này là thao tác ghi. Cần người dùng xác nhận trước khi chạy.
- **`RESTORE TABLE lh_vv_silver.dbo.slv_enr_poi_destination TO VERSION AS OF <v_pre>`** chỉ hợp lệ khi chưa có lần extract nào commit sau backfill. Nếu không, `ctrl_cdc_state` sẽ không phát lại event mới hơn. Kiểm tra bằng `DESCRIBE HISTORY` trước khi quyết định.
- **Gold**: không RESTORE bảng gold vì sẽ xoá các commit của pipeline. Gold đi theo silver ở lần chạy `PL_VV_TRANS_SLV_TO_GLD_30M` kế tiếp.
- **Init**: chạy lại notebook bản trước với cùng pin. Dòng LEGACY_INIT sẽ được ghi lại với NULL ở 6 cột. `destination_id` của LEGACY_INIT không đổi theo D-LEGACY-DEST.
- Không chạy lại `enrbrzpy` sau `destportalpy`, kể cả khi rollback.

## Kết quả người dùng ghi nhận

Người dùng điền bảng này. Main lưu output gốc vào `evidence/results/`.

| Bước | Thời điểm (UTC) | exec_id / LOCK | Số liệu chính | Kết quả (PASS/FAIL/STOP) | Ghi chú |
|---|---|---|---|---|---|
| Baseline B1–B5 | | | `v_silver_baseline` =, `v_info_baseline` =, silver_n = | | |
| 1. Publish extract | | | — | | |
| 2. `28e2be98`, `0f228dc1`, `enrbrzcfgpy` | | | Seed 32 cột / 2 bảng. `enrbrzcfgpy` 2 pipeline, watermark `wm_transform_brz_enrichment_result` | PASS | Khớp `TABLE_CONFIGS_ENR`: 9 + 23. `destination_portal_id` nằm giữa `destination_id` và `destination_name` |
| 3. `destportalpy` | | | pre old_n=19799, empty_n=2, gates 0; updated_n=19799; v_pre=9, v_post=10; post old_n=0, new_n=19799 | PASS | Lần STOP trước là cổng nullable. `empty_n` sau ghi = 0 vì metric chỉ đếm dòng `_old` |
| 4. `destportalpy` chạy lại | | | updated_n=0; v_pre=v_post=10; old_n=0; new_n=19799; gates 0 | PASS | Không ghi, không tăng version |
| 5a. Extract dry run | 2026-11-26 16:55:49 | f046277f-af09-4721-8bd7-e2204504db23 | SUCCESS, DRY_RUN, v341..v386, read 8916, ins=0 upd=0, cast_null=0, bad_shape={} | PASS | Lần trước STOP vì allowlist. `mapped_heads_missing.destinations=6687` khớp số doc LANG |
| 5b. Extract chạy thật | 2026-11-26 17:01:28 | b03961bb-5e23-4993-b586-f2809b31ee64 | SUCCESS, INCREMENTAL, last_src_version=386, inserted=8912, updated=4, cast_null=0 | PASS | destination ins=2228 upd=1; multi_lang ins=6684 upd=3 |
| 6. GLD_30M | 2026-11-26 17:10:56 | 194610f7-c548-45b4-ad74-7d139aed0827 | SUCCESS. info ins=1122 upd=20903 v=32. multi_lang ins=3366 upd=3318 v=23. destination edge 8→11 commits [10, 11] | PASS | QG warn source_name_null=3, i18n_only_rows=44 |
| 7.1 Init PLAN | | lgp-2030cc421f3649a39196e859b4844753 | enriched.decision=OK; destination.decision=OK; destination_changed_n=4038; ai_enriched_poi pin=10970; info to_insert=0; multi_lang to_insert=0 | PASS | D-DEST-KEEP. Pin ai_enriched_poi đổi 10968 → 10970. RUN dùng pin của PLAN này |
| 7.2 Init RUN 1 | | lgp-76028ef9872c4724b11f3d36d32103d9 | enriched.decision=OK; inserted=0 mọi stage; info v32→33; multi_lang v23→24; old_address_filled_n=45167; price_filled_n=22123; story_filled_n=282; local_tips_filled_n=268; destination_changed_n=4038; drift_n=25345 map NOT_COMMITTED | PASS | Pin ai_enriched_poi=10971. Lần STOP trước là lgp-ce830a17, trước D-MAP-DRIFT |
| 7.3 Init RUN 2 | | lgp-621dd8ef60984aa2b664c5626fe7f605 | inserted=0 mọi stage; info v33→34; multi_lang v24→25; K8=0; K11=0 dòng | PASS | Pin ai_enriched_poi=10972. Version tăng vì upsert ghi lại updated_at và row_hash |
| K1, K2, K6, K8, K10, K11 | | | k1=k2=k6=k8=0; k11=0 dòng; K10 năm POI, có lang null và có hash khác nhau | PASS | POI 1749e554 ba lang cùng hash độ dài 3. POI 41b4cc1b ko null. POI d6b4bbf7 en null. Không nhân một story sang lang đang null |
| K9 theo load_origin | | | info LEGACY 33148, old_address 24592, price_level 9826, price_min 9910, price_max 9838. info null-origin 22137, old_address 17966. multi_lang LEGACY 99254, story 3, local_tips 3. multi_lang null-origin story 798, local_tips 771 | PASS | Số exit đếm cả ứng viên. MERGE init chỉ ghi dòng LEGACY_INIT. Story nguồn gần như null |
| L1 | | | hai watermark SUCCESS, lock_exec_id NULL | PASS | |
