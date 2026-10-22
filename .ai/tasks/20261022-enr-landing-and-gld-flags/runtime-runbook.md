# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`

Task: `20261022-enr-landing-and-gld-flags`. Architecture PASS, review vòng 2 PASS. Runbook này chỉ còn phần backfill (`RUN` hai node), kiểm tra V1–V4 và R7 (architecture §12 R5–R8, §16). Các bước R0–R4 và `DRY_RUN` của R5 đã chạy trên Fabric DEV. Kết quả của chúng nằm ở mục `Kết quả người dùng ghi nhận`; **không chạy lại** các bước đó.

## Phạm vi và môi trường

- Môi trường: Fabric DEV. Workspace: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Fabric DEV>`.
- Lakehouse và bảng liên quan:
  - Gold: `lh_vv_gold.enr.gld_enr_poi_info`, `lh_vv_gold.enr.gld_enr_poi_review`.
  - Landing (chỉ đọc cột khoá, không đọc cột nội dung): `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang`, `lh_vv_silver.dbo.slv_enr_poi_destination`, `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang`.
  - Nguồn live: `lh_vv_silver.dbo.slv_poi_entity_non_enrich` (info), `lh_vv_silver.dbo.slv_3p_poi_review` (review).
  - Ctrl: `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`, `lh_vv_ctrl.dbo.ctrl_mng_watermark`, `lh_vv_ctrl.dbo.ctrl_log_table_run`.
- Luồng ctrl: `pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'`. Dòng khoá luồng: `watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'`.
- Fabric DEV không có pipeline object `PL_VV_TRANS_SLV_TO_ENR_15P`, nên cũng không có trigger để tạm dừng hay bật lại. `PL_VV_TRANS_SLV_TO_ENR_15P` chỉ là giá trị `pl_name` trong ctrl. Vì vậy ở R7, mỗi lần "trigger pipeline" được thay bằng một lần chạy tay hai notebook node với `p_mode="RUN"`, theo thứ tự info rồi review (xem bước 6–9).
- Notebook chạy tay: `NB_ENR_POI_INFO` (cell tham số `6afb4f0e`) và `NB_ENR_POI_REVIEW` (cell tham số `c8309a9e`).
- Tham số dùng cho **mọi** lần chạy node trong runbook này (trừ phần rollback):

| Tham số | Giá trị | Nguồn |
|---|---|---|
| `p_exec_id` | `""` | mặc định cell tham số |
| `p_run_id` | `""` | mặc định cell tham số |
| `p_pl_name` | `"PL_VV_TRANS_SLV_TO_ENR_15P"` | `pl_name` ctrl trong cell `enrflagpy` và trong log `DRY_RUN` |
| `p_trg_fq` | `""` | mặc định cell tham số |
| `p_pinned_json` | `""` | mặc định cell tham số |
| `p_mode` | `"RUN"` | yêu cầu backfill |
| `p_force` | `"false"` | giữ nguyên; backfill dựa vào baseline `FULL` của cạnh mới (§4.3), không dùng force |
| `p_history_limit` | `"1000"` | mặc định cell tham số |

- Quy tắc ghi bằng chứng: mỗi truy vấn trả tối đa 50 dòng. Không chép giá trị `review_text` hoặc `description`, không chép dữ liệu cá nhân. Mọi truy vấn trong runbook chỉ đọc, trừ các bước chạy node và các câu `INSERT`/`DELETE` của R7. Các câu ghi đó được đánh dấu **[GHI]**.

## Điều kiện tiên quyết

1. Đã xong R0–R4 và `DRY_RUN` (xem `Kết quả người dùng ghi nhận`). Bảng info không còn `district`, `destination_name`. Ba bảng landing đã có. Ba cạnh landing có `is_active = 1` và `n = 1`.
2. Khoá luồng đang trống. Chạy truy vấn sau và cần thấy `lock_exec_id` là NULL:

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P';
```

   Nếu `lock_exec_id` khác NULL thì dừng lại. Không tự nhả khoá; hỏi người đang chạy.
3. Không ai chạy `NB_00_ORCHES_SLV_TO_ENR_15P`, `NB_CREATE_DDL` hoặc hai notebook node trong suốt runbook. Người dùng xác nhận: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận không có run song song>`.
4. Ba bảng landing đang rỗng, vì khoá probe `probe-spark-001` đã bị xoá:

```sql
SELECT 'info_multi_lang' AS t, count(*) AS n FROM lh_vv_silver.dbo.slv_enr_poi_info_multi_lang
UNION ALL SELECT 'destination', count(*) FROM lh_vv_silver.dbo.slv_enr_poi_destination
UNION ALL SELECT 'review_multi_lang', count(*) FROM lh_vv_silver.dbo.slv_enr_poi_review_multi_lang;
```

   Kỳ vọng: cả ba bằng 0. Nếu khác 0 thì ghi lại số và báo người dùng trước khi chạy, vì kết quả V3 và R7 phụ thuộc vào tập khoá landing.
5. Không có VACUUM nào được lên lịch trên `gld_enr_poi_info` và `gld_enr_poi_review` trong cửa sổ rollback (P3). Người dùng xác nhận: `<CẦN NGƯỜI DÙNG CUNG CẤP: xác nhận không VACUUM và độ dài cửa sổ rollback>`.
6. **Stop S2.** R7 ghi dữ liệu test vào landing DEV. Phải có phê duyệt của người dùng trước bước 6: `<CẦN NGƯỜI DÙNG CUNG CẤP: phê duyệt S2>`.

## Baseline trước khi chạy

Ghi kết quả từng truy vấn vào `Kết quả người dùng ghi nhận`.

B1. Version gốc để rollback (P3). `v_info0` là version của `gld_enr_poi_info` ngay trước lệnh `SET TBLPROPERTIES` ở R3. `v_review0` là version của `gld_enr_poi_review` ngay trước lệnh `ADD COLUMNS` của `enrflagpy`. Nếu P3 đã ghi hai số này thì dùng lại, không tính lại: `<CẦN NGƯỜI DÙNG CUNG CẤP: v_info0, v_review0 nếu đã ghi ở P3>`. Nếu chưa ghi, tra lịch sử:

```sql
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 20;
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_review LIMIT 20;
```

   Chỉ ghi các cột `version`, `timestamp`, `operation`. Với info, `v_info0` = (version của dòng `SET TBLPROPERTIES` sớm nhất ngày 2026-10-22) − 1. Với review, `v_review0` = (version của dòng `ADD COLUMNS` do `enrflagpy` tạo) − 1.

B2. Version hiện tại, trước `RUN`. `DRY_RUN` không ghi gì nên đây cũng là version sau R4:

```sql
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 1;
DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_review LIMIT 1;
```

   Ghi lại thành `v_info1` và `v_review1`.

B3. Số dòng gold và batch mới nhất:

```sql
SELECT 'info' AS t, count(*) AS n_rows, count(DISTINCT poi_id) AS n_keys, max(created_at) AS last_batch
FROM lh_vv_gold.enr.gld_enr_poi_info
UNION ALL
SELECT 'review', count(*), count(DISTINCT review_id), max(created_at)
FROM lh_vv_gold.enr.gld_enr_poi_review;
```

   Để đối chiếu: lúc `DRY_RUN`, info có 65 dòng và review có 455 dòng.

B4. Số khoá live của hai nguồn (để so ở V2). `ctx.input` của lib chỉ lọc `deleted_at IS NULL` khi bảng có cả `row_hash` và `deleted_at`. `slv_poi_entity_non_enrich` có hai cột đó. `slv_3p_poi_review` là bảng extract snapshot, không có `deleted_at`.

```sql
SELECT count(DISTINCT poi_id) AS live_poi
FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich
WHERE deleted_at IS NULL AND poi_id IS NOT NULL;

SELECT count(DISTINCT review_id) AS live_review
FROM lh_vv_silver.dbo.slv_3p_poi_review
WHERE review_id IS NOT NULL;
```

   Để tham khảo: `DRY_RUN` báo info inserted 65 và review inserted 285. Với baseline `FULL`, hai số này là số khoá live tại thời điểm `DRY_RUN`.

B5. Ba cạnh landing (đọc lại, không sửa):

```sql
SELECT id, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
  AND src_tbl IN ('slv_enr_poi_info_multi_lang', 'slv_enr_poi_destination', 'slv_enr_poi_review_multi_lang');
```

   Kỳ vọng: 3 dòng, `src_schema = 'lh_vv_silver.dbo'`, `trg_schema = 'lh_vv_gold.enr'`, `is_active = 1`, `load_mode = 'APPEND'`. `slv_enr_poi_info_multi_lang` và `slv_enr_poi_destination` trỏ tới `gld_enr_poi_info`; `slv_enr_poi_review_multi_lang` trỏ tới `gld_enr_poi_review`.

B6. Watermark cạnh landing. Chỉ `NB_00` tạo các dòng này, nên lúc này kỳ vọng là 0 dòng:

```sql
SELECT watermark_id, status, last_src_version, last_src_table_id, last_success_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
  'wm_e__gld_enr_poi_info__slv_enr_poi_info_multi_lang',
  'wm_e__gld_enr_poi_info__slv_enr_poi_destination',
  'wm_e__gld_enr_poi_review__slv_enr_poi_review_multi_lang');
```

B7. Thời điểm bắt đầu runbook (UTC). Dùng giá trị này để lọc log ở V4: `SELECT current_timestamp() AS t0;`. Ghi lại thành `t0`.

## Các bước thực hiện

**Bước 1 — R5 `RUN` info (backfill).** Mở `NB_ENR_POI_INFO` và đặt cell `6afb4f0e` theo bảng tham số ở mục `Phạm vi và môi trường`:

```python
p_exec_id = ""
p_run_id = ""
p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15P"
p_trg_fq = ""
p_pinned_json = ""
p_mode = "RUN"
p_force = "false"
p_history_limit = "1000"
```

Chạy cả notebook. Ghi lại exit value (status, inserted, updated, deactivated, trg_version), thời gian chạy và các cảnh báo.

- Kỳ vọng: `SUCCESS`. inserted bằng số khoá live (`live_poi` ở B4). `trg_version` khác NULL.
- Nếu `FAILED`: không ghi gì vào gold. Không chạy bước 2. Đi tới `Rollback và forward recovery`.

**Bước 2 — R5 `RUN` review (backfill).** Chỉ chạy sau khi bước 1 `SUCCESS`. Mở `NB_ENR_POI_REVIEW` và đặt cell `c8309a9e` đúng như bước 1 (giá trị giống hệt). Chạy cả notebook và ghi lại như bước 1.

- Kỳ vọng: `SUCCESS`. inserted bằng `live_review` ở B4. `trg_version` khác NULL.

**Bước 3 — R6.** Chạy V1–V4 ở mục `Kiểm tra kết quả` và mục `Kiểm tra log và watermark`. Nếu có kiểm tra nào FAIL thì dừng, không sang R7.

**Bước 4 — Chạy lại để kiểm tra idempotency.** Xem mục `Chạy lại để kiểm tra idempotency`.

**Bước 5 — R7 chuẩn bị (chỉ đọc).** Chỉ làm khi đã có phê duyệt S2. Chọn khoá có sẵn bằng truy vấn, không gõ tay id. Dùng một notebook nháp gắn `lh_vv_gold` và `lh_vv_silver`, giữ nguyên session từ bước 5 đến bước 10 để các biến `r7_poi`, `r7_review` còn tồn tại. Không in giá trị khoá ra bằng chứng.

```python
r7_poi = spark.sql("""
SELECT poi_id FROM lh_vv_gold.enr.gld_enr_poi_info
WHERE created_at = (SELECT max(created_at) FROM lh_vv_gold.enr.gld_enr_poi_info)
  AND is_enriched_multi_lang = false AND is_enriched_destination = false
ORDER BY poi_id LIMIT 1
""").collect()[0]["poi_id"]
r7_review = spark.sql("""
SELECT review_id FROM lh_vv_gold.enr.gld_enr_poi_review
WHERE created_at = (SELECT max(created_at) FROM lh_vv_gold.enr.gld_enr_poi_review)
  AND is_enriched_multi_lang = false
ORDER BY review_id LIMIT 1
""").collect()[0]["review_id"]
R7_TS = "TIMESTAMP'1900-01-01 00:00:00'"  # dấu nhận dòng test; không dùng cột nội dung
spark.sql(f"""
SELECT
  (SELECT count(*) FROM lh_vv_silver.dbo.slv_enr_poi_info_multi_lang WHERE created_at = {R7_TS}) AS ml_marker,
  (SELECT count(*) FROM lh_vv_silver.dbo.slv_enr_poi_destination WHERE created_at = {R7_TS}) AS dest_marker,
  (SELECT count(*) FROM lh_vv_silver.dbo.slv_enr_poi_review_multi_lang WHERE created_at = {R7_TS}) AS rv_marker
""").show()
```

Kỳ vọng: hai câu chọn khoá đều trả được 1 dòng, và ba số `*_marker` bằng 0. Nếu không có khoá nào thỏa điều kiện thì dừng và báo người dùng.

**Bước 6 — R7.1 chèn dòng test [GHI].** Mỗi bảng landing nhận 1 dòng với khoá đã chọn. Cột nội dung để NULL; `created_at` và `updated_at` dùng dấu `R7_TS`. Hai bảng landing của info dùng cùng `r7_poi`.

```python
spark.sql(f"""INSERT INTO lh_vv_silver.dbo.slv_enr_poi_info_multi_lang
  (poi_id, lang, time_to_spend, best_time, cost_vnd, description, created_at, updated_at)
  VALUES ('{r7_poi}', NULL, NULL, NULL, NULL, NULL, {R7_TS}, {R7_TS})""")
spark.sql(f"""INSERT INTO lh_vv_silver.dbo.slv_enr_poi_destination
  (poi_id, street, ward, district, city, full_address, created_at, updated_at)
  VALUES ('{r7_poi}', NULL, NULL, NULL, NULL, NULL, {R7_TS}, {R7_TS})""")
spark.sql(f"""INSERT INTO lh_vv_silver.dbo.slv_enr_poi_review_multi_lang
  (review_id, poi_id, review_text, created_at, updated_at)
  VALUES ('{r7_review}', NULL, NULL, {R7_TS}, {R7_TS})""")
```

Chạy lại câu đếm marker ở bước 5. Kỳ vọng: 1, 1, 1.

**Bước 7 — R7.2 "trigger" lần 1.** Không có pipeline object, nên chạy tay `NB_ENR_POI_INFO` rồi `NB_ENR_POI_REVIEW` với đúng bộ tham số của bước 1. Không chạy hai notebook này song song với notebook nháp đang giữ session; notebook nháp chỉ cần giữ biến, không giữ khoá. Kỳ vọng: cả hai `SUCCESS`, info inserted 1, review inserted 1.

**Bước 8 — R7.2 kiểm tra true** (chạy trong notebook nháp):

```python
spark.sql(f"""
SELECT 'info' AS t, is_enriched_multi_lang AS f1, is_enriched_destination AS f2, created_at
FROM (SELECT *, row_number() OVER (PARTITION BY poi_id ORDER BY created_at DESC) AS rn
      FROM lh_vv_gold.enr.gld_enr_poi_info WHERE poi_id = '{r7_poi}') WHERE rn = 1
UNION ALL
SELECT 'review', is_enriched_multi_lang, NULL, created_at
FROM (SELECT *, row_number() OVER (PARTITION BY review_id ORDER BY created_at DESC) AS rn
      FROM lh_vv_gold.enr.gld_enr_poi_review WHERE review_id = '{r7_review}') WHERE rn = 1
""").show()
```

Kỳ vọng: info `f1 = true` và `f2 = true`; review `f1 = true`.

**Bước 9 — R7.3 xoá dòng test [GHI], rồi "trigger" lần 2.**

```python
spark.sql(f"DELETE FROM lh_vv_silver.dbo.slv_enr_poi_info_multi_lang WHERE poi_id = '{r7_poi}' AND created_at = {R7_TS}")
spark.sql(f"DELETE FROM lh_vv_silver.dbo.slv_enr_poi_destination WHERE poi_id = '{r7_poi}' AND created_at = {R7_TS}")
spark.sql(f"DELETE FROM lh_vv_silver.dbo.slv_enr_poi_review_multi_lang WHERE review_id = '{r7_review}' AND created_at = {R7_TS}")
```

Chạy lại câu đếm ở điều kiện tiên quyết số 4. Kỳ vọng: 0, 0, 0. Sau đó chạy tay `NB_ENR_POI_INFO` rồi `NB_ENR_POI_REVIEW` một lần nữa, với tham số của bước 1. Kỳ vọng: cả hai `SUCCESS`, info inserted 1, review inserted 1.

**Bước 10 — R7.3 kiểm tra false.** Chạy lại truy vấn của bước 8. Kỳ vọng: info `f1 = false` và `f2 = false`; review `f1 = false`. Ghi `changed` ở V4 cho hai lần chạy R7.

**Bước 11 — R8.** Không có trigger để bật lại: Fabric DEV không có pipeline object. Kiểm tra khoá luồng đã được nhả (truy vấn ở điều kiện tiên quyết số 2): `lock_exec_id` phải là NULL. Khi nào tạo pipeline object, phải xác nhận lần chạy theo lịch đầu tiên ra `NO_DATA` hoặc incremental: `<CẦN NGƯỜI DÙNG CUNG CẤP: thời điểm tạo pipeline object và trigger 15P, nếu có>`.

## Kiểm tra kết quả

**V1 — Schema** (sau bước 2):

```sql
DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_info;
DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_review;
DESCRIBE TABLE lh_vv_silver.dbo.slv_enr_poi_info_multi_lang;
DESCRIBE TABLE lh_vv_silver.dbo.slv_enr_poi_destination;
DESCRIBE TABLE lh_vv_silver.dbo.slv_enr_poi_review_multi_lang;
```

Kỳ vọng:
- `gld_enr_poi_info` có 40 cột. Không có `district` hay `destination_name`. Vẫn còn `street`, `ward`, `city`, `full_address`. Đuôi bảng là `service_flag`, `is_enriched_multi_lang` (boolean), `is_enriched_destination` (boolean), `created_at`, `updated_at`.
- `gld_enr_poi_review` có 9 cột. `is_enriched_multi_lang` (boolean) đứng ngay sau `review_updated_at` và ngay trước `created_at`, `updated_at`.
- Landing khớp `LANDING_COLS`:
  - `slv_enr_poi_info_multi_lang`: `poi_id` string NOT NULL, `lang`, `time_to_spend`, `best_time`, `cost_vnd`, `description` (string), `created_at`, `updated_at` (timestamp).
  - `slv_enr_poi_destination`: `poi_id` string NOT NULL, `street`, `ward`, `district`, `city`, `full_address` (string), `created_at`, `updated_at` (timestamp).
  - `slv_enr_poi_review_multi_lang`: `review_id` string NOT NULL, `poi_id`, `review_text` (string), `created_at`, `updated_at` (timestamp). Không có cột `lang`.

**V2 — Batch backfill không có cờ NULL** (sau bước 2, trước R7):

```sql
SELECT count(*) AS n_rows, count(DISTINCT poi_id) AS n_keys,
       count_if(is_enriched_multi_lang IS NULL OR is_enriched_destination IS NULL) AS n_null,
       count_if(is_enriched_multi_lang) AS n_ml_true, count_if(is_enriched_destination) AS n_dest_true
FROM lh_vv_gold.enr.gld_enr_poi_info
WHERE created_at = (SELECT max(created_at) FROM lh_vv_gold.enr.gld_enr_poi_info);

SELECT count(*) AS n_rows, count(DISTINCT review_id) AS n_keys,
       count_if(is_enriched_multi_lang IS NULL) AS n_null, count_if(is_enriched_multi_lang) AS n_ml_true
FROM lh_vv_gold.enr.gld_enr_poi_review
WHERE created_at = (SELECT max(created_at) FROM lh_vv_gold.enr.gld_enr_poi_review);
```

Kỳ vọng:
- info: `n_rows = n_keys = live_poi` (B4), `n_null = 0`.
- review: `n_rows = n_keys = live_review` (B4), `n_null = 0`.
- Landing rỗng nên mọi `*_true` bằng 0.

**V3 — Cờ của dòng mới nhất mỗi khoá khớp với `EXISTS` trong landing** (chạy sau bước 2, và chạy lại sau bước 10):

```sql
WITH g AS (
  SELECT poi_id, is_enriched_multi_lang AS f_ml, is_enriched_destination AS f_dest,
         row_number() OVER (PARTITION BY poi_id ORDER BY created_at DESC) AS rn
  FROM lh_vv_gold.enr.gld_enr_poi_info),
ml AS (SELECT DISTINCT poi_id FROM lh_vv_silver.dbo.slv_enr_poi_info_multi_lang),
d AS (SELECT DISTINCT poi_id FROM lh_vv_silver.dbo.slv_enr_poi_destination)
SELECT count(*) AS n_keys,
       count_if(g.f_ml <> (ml.poi_id IS NOT NULL)) AS bad_ml,
       count_if(g.f_dest <> (d.poi_id IS NOT NULL)) AS bad_dest,
       count_if(g.f_ml IS NULL OR g.f_dest IS NULL) AS null_latest
FROM g LEFT JOIN ml ON g.poi_id = ml.poi_id LEFT JOIN d ON g.poi_id = d.poi_id
WHERE g.rn = 1;

WITH g AS (
  SELECT review_id, is_enriched_multi_lang AS f_ml,
         row_number() OVER (PARTITION BY review_id ORDER BY created_at DESC) AS rn
  FROM lh_vv_gold.enr.gld_enr_poi_review),
ml AS (SELECT DISTINCT review_id FROM lh_vv_silver.dbo.slv_enr_poi_review_multi_lang)
SELECT count(*) AS n_keys,
       count_if(g.f_ml <> (ml.review_id IS NOT NULL)) AS bad_ml,
       count_if(g.f_ml IS NULL) AS null_latest
FROM g LEFT JOIN ml ON g.review_id = ml.review_id
WHERE g.rn = 1;
```

Kỳ vọng: `bad_ml = 0` và `bad_dest = 0`. `null_latest` chỉ được khác 0 với khoá đã không còn live: dòng mới nhất của những khoá này là dòng trước patch, nên còn NULL (D-07). Nếu `null_latest > n_keys − live_*` thì đó là lỗi, dừng lại. Câu so sánh dùng `<>`, nên dòng có cờ NULL không bị đếm vào `bad_*`; vì vậy phải đọc thêm `null_latest`.

**R7 — Kết quả kỳ vọng:** bước 8 ra true, bước 10 ra false. Ở V4, `changed` của mỗi landing role bằng 1 (số khoá test) trong cả hai lần chạy R7.

## Chạy lại để kiểm tra idempotency

- `enrflagpy` đã chạy lần hai trên DEV và không tạo lại bảng. Ba cạnh vẫn `is_active = 1`, `n = 1`. Không chạy lại.
- Node: ngay sau bước 2 và V1–V3, trước R7, chạy tay `NB_ENR_POI_INFO` rồi `NB_ENR_POI_REVIEW` thêm một lần, với tham số của bước 1. Lần này landing không đổi và đã có marker của lần chạy tay trước, nên basis của landing role là `MARKER` và `_flag_keys` không trả khoá nào.
  - Kỳ vọng mỗi node: status `NO_DATA`, hoặc `SUCCESS` với inserted 0.
  - Chạy lại B3: `n_rows` không đổi so với ngay sau bước 2.
  - `DESCRIBE HISTORY … LIMIT 1` không có commit append mới.
  - Nếu inserted > 0 thì ghi lại `changed` của từng role trong `qg_json` và dừng lại. Nguồn khác (entity, review) đổi trong lúc chạy có thể giải thích con số này. Phải đối chiếu `src_versions_json` trước khi kết luận.

## Kiểm tra log và watermark

**V4 — Log node:**

```sql
SELECT exec_id, trg_tbl, status, started_at, duration_ms, inserted_rows, updated_rows, deactivated_rows,
       trg_version, error_message,
       get_json_object(qg_json, '$.mode')   AS mode,
       get_json_object(qg_json, '$.inbox')  AS inbox,
       get_json_object(qg_json, '$.warns')  AS warns,
       get_json_object(qg_json, '$.blocks') AS blocks,
       qg_json, src_versions_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
  AND trg_tbl IN ('gld_enr_poi_info', 'gld_enr_poi_review')
  AND started_at >= '<t0 ở B7>'
ORDER BY started_at
LIMIT 50;
```

Kỳ vọng:
- Lần backfill (bước 1, 2):
  - `status = 'SUCCESS'`, `trg_version` khác NULL.
  - `inbox` của các landing role (`slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination`, `slv_enr_poi_review_multi_lang`) là `NEW_EDGE`, giống lúc `DRY_RUN`.
  - basis của các landing role là `FULL` (§4.3).
  - `blocks` không có `enrich_flag_null`.
  - `warns` có `multi_lang_key_not_in_entity`, `destination_key_not_in_entity` (info) và `multi_lang_key_not_in_review` (review), đều bằng 0 vì landing rỗng.
  - Ghi `duration_ms` của từng node. Để đối chiếu: `DRY_RUN` info 89s, review 75s.
- Lần idempotency: `NO_DATA` hoặc inserted 0.
- Hai lần R7: info inserted 1, review inserted 1. `changed` của từng landing role bằng 1. Ba cảnh báo `*_key_not_in_*` bằng 0, vì khoá test lấy từ gold live.
- Nếu basis của landing role ở lần backfill không phải `FULL` (hoặc `FULL_VERSION_UNAVAILABLE`), hoặc có block check nào chặn, thì dừng và ghi `qg_json` vào bằng chứng. `qg_json` chỉ chứa số đếm và lý do, không chứa nội dung landing.

**Khoá luồng** (sau mỗi lần chạy node và ở cuối runbook):

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P';
```

Kỳ vọng: `lock_exec_id` là NULL. `status` mang trạng thái của lần chạy cuối.

**Watermark cạnh:** chạy lại B6. Kỳ vọng vẫn là 0 dòng: chỉ `NB_00` ghi dòng `wm_e__…`, còn lần chạy tay ghi marker của append. Nếu xuất hiện dòng thì ghi lại `status`, `last_src_version` và `last_success_at`, và tìm xem ai đã chạy `NB_00`.

## Rollback và forward recovery

**Ưu tiên forward fix.** Mọi trạng thái trung gian đều fail closed và không ghi dữ liệu sai (§7, §11).

| Tình huống | Trạng thái | Xử lý |
|---|---|---|
| Bước 1 `FAILED` (QG `rating_cast_overflow`, `block_checks`, schema) | Không ghi gold | Ghi `error_message` và `qg_json` làm bằng chứng. Sửa dữ liệu hoặc luật trong một quyết định riêng. Không bỏ qua QG, không dùng `p_force="true"` để vượt. |
| Bước 1 `SUCCESS`, bước 2 `FAILED` | Info đã backfill, review chưa | Sửa nguyên nhân rồi chỉ chạy lại bước 2 với cùng tham số. Không chạy lại info. |
| Lần chạy bị kill, khoá còn giữ | `lock_exec_id` khác NULL | Chờ khoá hết hạn (node chạy tay: 90 phút). Không tự `UPDATE` dòng khoá trừ khi người dùng xác nhận chắc chắn không còn run nào. |
| Version landing đã bị vacuum | basis `FULL_VERSION_UNAVAILABLE` | Tự xử lý: `_flag_keys` trả mọi khoá. |
| R7: chèn được nhưng node lỗi | Landing còn dòng test | Vẫn làm bước 9 (xoá theo `created_at = TIMESTAMP'1900-01-01 00:00:00'`). Sau khi sửa lỗi node thì chạy lại hai node. |
| Mất session notebook nháp giữa R7 | Mất biến `r7_poi`, `r7_review` | Xoá theo dấu: `DELETE FROM <bảng landing> WHERE created_at = TIMESTAMP'1900-01-01 00:00:00'` trên cả ba bảng **[GHI]**, rồi kiểm tra count về 0. Chạy lại hai node và V3. |

**Rollback toàn phần.** Người dùng tự chạy, chỉ khi họ quyết định như vậy: `<CẦN NGƯỜI DÙNG CUNG CẤP: quyết định rollback>`.

1. Tắt ba cạnh landing, giữ dòng [GHI]:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'
  AND src_schema = 'lh_vv_silver.dbo' AND trg_schema = 'lh_vv_gold.enr'
  AND ((src_tbl = 'slv_enr_poi_info_multi_lang' AND trg_tbl = 'gld_enr_poi_info')
    OR (src_tbl = 'slv_enr_poi_destination' AND trg_tbl = 'gld_enr_poi_info')
    OR (src_tbl = 'slv_enr_poi_review_multi_lang' AND trg_tbl = 'gld_enr_poi_review'))
  AND is_active <> 0;
```

2. Khôi phục info [GHI]. Hai cột `district` và `destination_name` quay lại, còn protocol reader 2 / writer 5 thì giữ nguyên:
   `RESTORE TABLE lh_vv_gold.enr.gld_enr_poi_info TO VERSION AS OF <CẦN NGƯỜI DÙNG CUNG CẤP: v_info0>;`
3. Khôi phục review [GHI]:
   `RESTORE TABLE lh_vv_gold.enr.gld_enr_poi_review TO VERSION AS OF <CẦN NGƯỜI DÙNG CUNG CẤP: v_review0>;`
4. Revert bốn notebook `NB_CREATE_DDL`, `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`, `NB_SETUP_INITIAL_DDL` về `<CẦN NGƯỜI DÙNG CUNG CẤP: commit trước task>`, rồi git sync vào Fabric DEV.
5. Chạy tay `NB_ENR_POI_INFO` rồi `NB_ENR_POI_REVIEW` với tham số của bước 1, nhưng `p_force = "true"`. Lý do: RESTORE đã làm mất hiệu lực marker và gỡ các dòng append sau v0, trong khi watermark cạnh có thể đã đi quá các thay đổi đó.
6. Giữ ba bảng landing. Không bao giờ DROP chúng.

Sau rollback, chạy V1 để xác nhận schema cũ (info có `district`, `destination_name`, không có cờ; review không có cờ), rồi chạy truy vấn khoá luồng.

## Kết quả người dùng ghi nhận

**Đã làm trên Fabric DEV (2026-10-22). Không chạy lại.**

- R1/R2:
  - Không có Fabric pipeline object `PL_VV_TRANS_SLV_TO_ENR_15P`, nên không có trigger để tạm dừng.
  - `lock_exec_id` của `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` là NULL.
  - Bốn notebook đã được git sync.
- R0/P1: đã thử trên bảng nháp rỗng `lh_vv_gold.enr.probe_spark001_scratch`. Bật column mapping, bỏ cột `drop_me`, rồi xoá bảng nháp. Người dùng báo thành công.
- R3: `ALTER TABLE lh_vv_gold.enr.gld_enr_poi_info DROP COLUMNS (district, destination_name)` thành công. `DESCRIBE` trước `enrflagpy` có 38 cột, không có `district` hay `destination_name`; còn `street`, `ward`, `city`, `full_address`.
- R4: cell `enrflagpy` đã chạy hai lần.
  - Lần 1 tạo ba bảng `lh_vv_silver.dbo.slv_enr_*`. Lần 2 không tạo lại.
  - Kiểm tra cạnh cả hai lần: 3 dòng, `is_active = 1`, `n = 1`.
- R5 `DRY_RUN`:
  - `NB_ENR_POI_INFO` `SUCCESS` 89s, `NEW_EDGE` trên cả hai landing info. Exit: inserted 65, updated 0, deactivated 0, `trg_version` null.
  - `NB_ENR_POI_REVIEW` `SUCCESS` 75s, `NEW_EDGE` trên landing review. Exit: inserted 285, updated 0, deactivated 0, `trg_version` null.
  - Quy mô lúc đó: info 65 dòng, review 455 dòng, mỗi landing có 1 dòng probe.
- Dọn probe:
  - Khoá `probe-spark-001` đã bị xoá. Người dùng báo cả ba count bằng 0.
  - Spark UI đã đóng. `SPARK-001` được ghi `accepted-risk` trong `decision.md`. Spill, shuffle và peak memory không đo được.

**Còn phải chạy (người dùng điền):**

| Mục | Kết quả |
|---|---|
| Phê duyệt S2 | accepted-risk, không chạy R7 |
| Landing count trước khi chạy (3 số) | 0, 0, 0 |
| B1 `v_info0`, `v_review0` | 1, 3 |
| B2 `v_info1`, `v_review1` | 6, 4 |
| B3 số dòng / khoá / batch cuối | chưa dán riêng; V2 batch mới là 65 và 285 |
| B4 `live_poi`, `live_review` | chưa dán |
| B6 số dòng watermark cạnh | chưa dán |
| B7 `t0` | chưa dán; log node bắt đầu 07:29:49Z và 07:35:11Z |
| Bước 1 info `RUN`: status, giây, inserted, updated, deactivated, trg_version | SUCCESS, 111s, 65, 0, 0, 7. Chạy sau review |
| Bước 2 review `RUN`: status, giây, inserted, updated, deactivated, trg_version | SUCCESS, 30s, 285, 0, 0, 5. Chạy trước info, 07:29Z |
| V1 schema (đạt / không đạt, số cột) | lịch sử: ADD COLUMNS đúng vị trí; chưa dán DESCRIBE sau RUN |
| V2 info và review (`n_rows`, `n_keys`, `n_null`) | info 65, 65, 0. review 285, 285, 0 |
| V3 sau backfill (`bad_*`, `null_latest`) | info 65, bad 0, 0, null_latest 0. review 285, bad 0, null_latest 0 |
| V4 backfill (inbox, basis, warns, blocks) | cả hai SUCCESS. Landing inbox NEW_EDGE. enrich_flag_null 0. Cảnh báo khóa lệch bằng 0 |
| Idempotency: status và inserted của lần chạy lại | cả hai SUCCESS, inserted 0 |
| R7 lần 1: inserted và `changed`; cờ ở bước 8 | không chạy, D-10 |
| R7 lần 2: inserted và `changed`; cờ ở bước 10; landing count sau `DELETE` | không chạy, D-10 |
| V3 sau R7 | không chạy, D-10 |
| Khoá luồng cuối runbook (`lock_exec_id`) | null, status SUCCESS, updated_at 2026-10-22T07:37:05Z. Ba watermark cạnh không có dòng |
| Kết luận PASS / FAIL | PASS phần backfill và idempotency. R7 accepted-risk |
