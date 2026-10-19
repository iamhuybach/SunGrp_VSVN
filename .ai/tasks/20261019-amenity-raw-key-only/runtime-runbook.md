# Runtime runbook: 20261019-amenity-raw-key-only

## Phạm vi và môi trường

Runbook này dựng lại `lh_vv_silver.dbo.ref_dictionary_amenities` và `lh_vv_silver.dbo.slv_poi_amenity` trên Fabric DEV, sau khi code của task `20261019-amenity-raw-key-only` đã qua review. Trong seed mới, `amenity_raw` chỉ còn dạng key: 158 dòng, gồm google 84 và partner 74. Matcher dùng hai allowlist `FLAG_MATCH` (27 key) và `TYPE_MATCH` (14 key). Thiết kế nằm trong `.ai/tasks/20261019-amenity-raw-key-only/architecture.md`, các mục `Main brief`, §17 và §19.

- Môi trường: Fabric DEV, schema `lh_vv_silver.dbo`. Bảng control nằm ở `lh_vv_ctrl.dbo`.
- Pipeline: `PL = "PL_VV_TRANS_SLV_TO_SLV_1H"`. Pipeline này chưa có schedule và được chạy tay. Repo chưa có JSON của pipeline.
- Notebook được gọi: `NB_SETUP_POI_AMENITY` (tham số `p_apply`) và `NB_SLV_POI_AMENITY` (tham số `p_mode`, `p_force`).
- Bảng live: `lh_vv_silver.dbo.ref_dictionary_amenities` và `lh_vv_silver.dbo.slv_poi_amenity`. Không `DROP` bảng live nào. Runbook chỉ dùng `DELETE`, `MERGE` (qua notebook) và `RESTORE`. Vì không `DROP` nên Delta table id giữ nguyên, và cạnh của NB_00 sẽ không báo `TABLE_RECREATED`.
- Bảng backup: `lh_vv_silver.dbo.bak_ref_dictionary_amenities_20261019` và `lh_vv_silver.dbo.bak_slv_poi_amenity_20261019`. Hai bảng này được giữ lại sau runbook. Việc xoá chúng nằm ngoài runbook.
- Người dùng tự chạy mọi bước. Agent không chạy bước nào và không đặt `gates.runtime`.
- Mọi truy vấn đều chỉ đọc, trừ các bước chạy thật: backup CTAS, `DELETE` có lock, chạy notebook, và `RESTORE` khi rollback. Bằng chứng chỉ ghi số tổng hợp và Delta version. Mẫu kết quả tối đa 50 dòng và không chứa dữ liệu cá nhân.

Notebook scratch trên DEV. Cell đầu tiên:

```python
%run NB_LIB_TRANSFORM_SLV_GLD
```

Cell thứ hai khai báo hằng số và helper dùng chung cho toàn runbook:

```python
import json, uuid

PL = "PL_VV_TRANS_SLV_TO_SLV_1H"
DICT_FQ = "lh_vv_silver.dbo.ref_dictionary_amenities"
AMEN_FQ = "lh_vv_silver.dbo.slv_poi_amenity"
BAK_DICT_FQ = "lh_vv_silver.dbo.bak_ref_dictionary_amenities_20261019"
BAK_AMEN_FQ = "lh_vv_silver.dbo.bak_slv_poi_amenity_20261019"
CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
LOCK_ID = f"wm_flow__{PL}"
NB_TIMEOUT_S = <CẦN NGƯỜI DÙNG CUNG CẤP: timeout (giây) cho notebookutils.notebook.run trên DEV>

EDGE_SQL = f"""
    SELECT src_tbl, is_active, count(*) AS n
    FROM {CFG}
    WHERE pl_name = '{PL}' AND trg_tbl = 'slv_poi_amenity'
    GROUP BY src_tbl, is_active
    ORDER BY src_tbl, is_active
"""
LEGACY_PRED = "(amenity_raw LIKE '% = true' OR amenity_raw LIKE 'types[] = %')"


def edges():
    return sorted(tuple(r) for r in spark.sql(EDGE_SQL).collect())


def locked_sql(statements):
    """Chạy các lệnh ghi dưới flow lock, nhả lock trong finally (giống c1setupedges)."""
    x = str(uuid.uuid4())
    ok, who = acquire_flow_lock(PL, x, x, LOCK_TIMEOUT_DEFAULT_MIN)
    if not ok:
        raise ConfigError(f"Luồng {PL} đang chạy ({who}); dừng runbook")
    status = "FAILED"
    try:
        for sql in statements:
            spark.sql(sql)
        status = "SUCCESS"
    finally:
        release_flow_lock(PL, x, status)


# 14 key TYPE_MATCH, chép từ cell d1amenmatch của NB_SLV_POI_AMENITY
spark.sql("""
CREATE OR REPLACE TEMP VIEW rb_type_keys AS
SELECT * FROM VALUES
    ('accommodation', 'general_amenities', 'swimming_pool'),
    ('accommodation', 'general_amenities', 'hot_spring'),
    ('accommodation', 'general_amenities', 'sauna'),
    ('accommodation', 'general_amenities', 'garden'),
    ('accommodation', 'general_amenities', 'botanical_garden'),
    ('accommodation', 'general_amenities', 'meeting_rooms'),
    ('f_n_b', 'specialty_tags', 'food_stand'),
    ('f_n_b', 'specialty_tags', 'street_food_gathering'),
    ('f_n_b', 'specialty_tags', 'seafood_restaurant'),
    ('f_n_b', 'specialty_tags', 'oyster_bar_restaurant'),
    ('f_n_b', 'specialty_tags', 'steakhouse'),
    ('f_n_b', 'specialty_tags', 'bakery'),
    ('f_n_b', 'specialty_tags', 'pastry_shop'),
    ('f_n_b', 'specialty_tags', 'cake_shop')
AS t(business_sector, amenity_group, amenity_raw)
""")
```

Biến trong session scratch, ví dụ `EDGES_R1` hay `V_dict0`, sẽ mất khi session hết hạn. Vì vậy hãy ghi mọi giá trị vào mục `Kết quả người dùng ghi nhận` ngay khi có.

Tham số notebook lấy từ file:
- `NB_SETUP_POI_AMENITY`, cell `c1setupparam`: `p_apply = "false"` là mặc định. Runbook truyền `"false"` (PLAN) hoặc `"true"` (apply).
- `NB_SLV_POI_AMENITY`, cell `d1amenparam`: mặc định `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`. Runbook chỉ truyền `p_mode` và `p_force` theo §19. Các tham số còn lại giữ mặc định.

## Điều kiện tiên quyết

Bước R0. Chỉ đi tiếp khi mọi điều kiện dưới đây đều đúng.

R0.1. Code trên DEV khớp với commit đã merge: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash đã merge của task>`. Review đã PASS cho sql-data, spark-runtime, state-correctness và risk-gate. Đã sync các notebook `NB_SETUP_POI_AMENITY`, `NB_SLV_POI_AMENITY`, `NB_SETUP_INITIAL_DDL` và `NB_LIB_TRANSFORM_SLV_GLD` lên workspace DEV. Từ lúc sync đến khi reseed xong, một lần chạy node sẽ fail closed (I9). Đây là hành vi đúng.

R0.2. Pipeline `PL_VV_TRANS_SLV_TO_SLV_1H` không có trigger hay schedule. Kiểm tra trong UI Fabric DEV, vì repo không có JSON pipeline.

R0.3. Lock row của luồng tồn tại và đang trống:

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H'
```

Kỳ vọng: đúng 1 dòng, `lock_exec_id` là NULL.

R0.4. Chạy setup ở chế độ PLAN. Chế độ này không ghi gì:

```python
out = notebookutils.notebook.run("NB_SETUP_POI_AMENITY", NB_TIMEOUT_S, {"p_apply": "false"})
print(out)
PLAN_R0 = json.loads(out)
```

Kỳ vọng: `status = "PLAN"`, `google = 84`, `partner = 74`, `entity_edges_ok = 5`. Ghi lại `missing_keys` và `stale_keys`. Nếu DEV đang đúng bằng seed cũ, `stale_keys` dự kiến là 35. Nếu `entity_edges_ok` khác 5, dừng lại: phải chạy `NB_SETUP_POI_ENTITY` trước, việc này nằm ngoài runbook. Nếu notebook raise lỗi `validate_seed`, đó là lỗi code: dừng lại và sửa theo hướng forward fix.

## Baseline trước khi chạy

Bước R1. Mọi truy vấn ở đây chỉ đọc.

R1.0. Ghi lại thời điểm bắt đầu. Mốc này dùng để lọc log:

```python
T0 = spark.sql("SELECT current_timestamp() AS t").first()["t"]
print(T0)
```

R1.1. Delta version mới nhất của bảng đích và bảng đầu vào:

```python
V0 = {}
for fq in [DICT_FQ, AMEN_FQ, "lh_vv_silver.dbo.slv_3p_poi_amenity", "lh_vv_silver.dbo.slv_poi_entity_non_enrich"]:
    r = spark.sql(f"DESCRIBE HISTORY {fq} LIMIT 1").select("version", "timestamp", "operation").first()
    V0[fq] = r["version"]
    print(fq, r["version"], r["timestamp"], r["operation"])
V_dict0, V_amen0 = V0[DICT_FQ], V0[AMEN_FQ]
```

Ghi lại `V_dict0`, `V_amen0`, `V_src0` (version của `slv_3p_poi_amenity`) và `V_ent0` (version của `slv_poi_entity_non_enrich`).

R1.2. Số dòng của từ điển:

```sql
SELECT source_name,
       count(*) AS n,
       sum(CASE WHEN is_active = false THEN 1 ELSE 0 END) AS inactive,
       sum(CASE WHEN is_active IS NULL THEN 1 ELSE 0 END) AS active_null,
       sum(CASE WHEN amenity_raw LIKE '% = true' OR amenity_raw LIKE 'types[] = %' THEN 1 ELSE 0 END) AS legacy_form
FROM lh_vv_silver.dbo.ref_dictionary_amenities
GROUP BY source_name
ORDER BY source_name
```

`LIKE '% = true'` rộng hơn dạng mà `validate_seed` chặn. Seed mới cố ý giữ 4 dòng vẫn khớp LIKE: `serves_meals = true`, câu `types[] có ... servesBeer = true`, `outdoorSeating = true = true`, và `parkingOptions.freeParkingLot, parkingOptions.paidParkingLot = true`.
- dòng LIKE nằm trong seed mới = tổng `legacy_form` − `stale_keys`. Kỳ vọng 4 khi DEV còn đúng seed cũ.
- stale khác = `stale_keys` − (tổng `legacy_form` − 4). Kỳ vọng 0.
- Nếu hiệu âm hoặc stale khác khác 0, đó là dòng sửa tay. Dừng ở STOP R1.

R1.3. Drift do sửa tay trên DEV. Số `drift` chính xác chỉ được tính trong lúc setup apply. Lúc đó bảng đã bị DELETE, nên con số không còn nói lên trạng thái hiện tại. Vì vậy baseline kiểm drift qua lịch sử Delta. Seed MERGE chỉ insert, nên mọi UPDATE hay DELETE trong lịch sử đều là sửa tay:

```python
(spark.sql(f"DESCRIBE HISTORY {DICT_FQ}")
    .selectExpr("version", "timestamp", "operation",
                "operationMetrics['numTargetRowsInserted'] AS merge_ins",
                "operationMetrics['numTargetRowsUpdated'] AS merge_upd",
                "operationMetrics['numTargetRowsDeleted'] AS merge_del",
                "operationMetrics['numUpdatedRows'] AS upd",
                "operationMetrics['numDeletedRows'] AS del")
    .orderBy(F.desc("version")).limit(50).show(50, False))
```

Drift = 0 khi cả ba điều sau đều đúng:
- lịch sử không có operation `UPDATE` hay `DELETE`;
- mọi `MERGE` có `merge_upd` và `merge_del` bằng NULL hoặc 0;
- `inactive` ở R1.2 bằng 0.

R1.4. Số dòng của `slv_poi_amenity`:

```sql
SELECT count(*) AS total,
       sum(CASE WHEN deleted_at IS NULL THEN 1 ELSE 0 END) AS live,
       sum(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS soft_deleted,
       sum(CASE WHEN deleted_at IS NULL AND amenity_raw LIKE '% = true' THEN 1 ELSE 0 END) AS live_flag_legacy,
       sum(CASE WHEN deleted_at IS NULL AND amenity_raw LIKE 'types[] = %' THEN 1 ELSE 0 END) AS live_types_legacy,
       count(DISTINCT CASE WHEN deleted_at IS NULL THEN poi_id END) AS live_pois
FROM lh_vv_silver.dbo.slv_poi_amenity
```

R1.5. Cạnh trong ctrl:

```python
EDGES_R1 = edges()
print(EDGES_R1)
```

```sql
SELECT src_schema, src_tbl, trg_schema, count(*) AS n
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND trg_tbl = 'slv_poi_amenity'
GROUP BY src_schema, src_tbl, trg_schema
HAVING count(*) > 1
```

Kỳ vọng:
- `EDGES_R1` có `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich` và `ref_dictionary_amenities`, mỗi cạnh `is_active = 1`, `n = 1`;
- có thể có thêm `slv_poi_entity` với `is_active = 0`, `n = 1`;
- truy vấn trùng cặp trả về 0 dòng.

R1.6. Snapshot watermark để so sánh ở bước sau:

```sql
SELECT watermark_id, status, last_src_version, last_src_table_id, last_success_at, lock_exec_id, lock_at, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H'
   OR watermark_id LIKE 'wm\\_e\\_\\_slv\\_poi\\_amenity\\_\\_%'
ORDER BY watermark_id
LIMIT 50
```

## Các bước thực hiện

Đường đang chạy, quyết định D7, 2026-10-20. Không backup. Không `DELETE` dưới lock. Không đụng `slv_poi_amenity`.

R2. DROP từ điển rồi chạy setup. Cả hai đều là bước ghi. `CREATE TABLE IF NOT EXISTS` trong notebook tạo lại bảng trống, rồi MERGE insert-only nạp 158 dòng. History version 1 mất theo bảng bị DROP. Phục hồi từ điển là chạy lại đúng hai lệnh này.

```python
spark.sql("DROP TABLE IF EXISTS lh_vv_silver.dbo.ref_dictionary_amenities")
out = notebookutils.notebook.run("NB_SETUP_POI_AMENITY", NB_TIMEOUT_S, {"p_apply": "true"})
print(out)
```

Kỳ vọng: `status = "SUCCESS"`, `inserted = 158`, `drift = 0`, `stale = 0`, `edges_inserted = 0`, `edges_retired = 0`.

Nếu setup raise `ConfigError` ở bước kiểm cạnh, seed đã được ghi đúng nhưng cạnh chưa đổi. Khi đó dừng lại để người dùng quyết định về cạnh ctrl. Không sửa cạnh bằng tay.

R2.3. Kiểm tra từ điển. Mọi truy vấn chỉ đọc.

```sql
SELECT source_name, count(*) AS n,
       sum(CASE WHEN NOT (is_active <=> true) THEN 1 ELSE 0 END) AS not_active,
       sum(CASE WHEN amenity_raw LIKE '% = true' OR amenity_raw LIKE 'types[] = %' THEN 1 ELSE 0 END) AS legacy_form
FROM lh_vv_silver.dbo.ref_dictionary_amenities
GROUP BY source_name ORDER BY source_name
```

Kỳ vọng: google 84, partner 74, tổng 158. `not_active = 0`. `legacy_form` google = 4, partner = 0: bốn câu seed cố ý giữ vẫn khớp `LIKE '% = true'`. Không còn dòng `types[] = `.

```sql
SELECT business_sector, count(*) AS n
FROM lh_vv_silver.dbo.ref_dictionary_amenities
WHERE source_name = 'google'
GROUP BY business_sector ORDER BY business_sector
```

Kỳ vọng: `accommodation` 31, `attraction` 16, `f_n_b` 34, `shopping_n_retail` 3.

```sql
SELECT count(*) AS dup5 FROM (
    SELECT source_name, business_sector, amenity_group, amenity_raw, amenity
    FROM lh_vv_silver.dbo.ref_dictionary_amenities
    GROUP BY 1, 2, 3, 4, 5 HAVING count(*) > 1
)
```

Kỳ vọng: `dup5 = 0`.

```sql
SELECT source_name, business_sector, amenity_group, amenity_raw, count(*) AS n
FROM lh_vv_silver.dbo.ref_dictionary_amenities
GROUP BY 1, 2, 3, 4 HAVING count(*) > 1
ORDER BY 1, 2, 3, 4 LIMIT 50
```

Kỳ vọng: đúng 1 dòng, `('google', 'attraction', 'facilities_and_services', 'goodForChildren')` với `n = 2`.

```python
EDGES_R2 = edges()
print(EDGES_R2 == EDGES_R1, EDGES_R2)
```

Kỳ vọng: `True`.

R2.4. Chạy lại PLAN. Bước này không ghi:

```python
out = notebookutils.notebook.run("NB_SETUP_POI_AMENITY", NB_TIMEOUT_S, {"p_apply": "false"})
print(out)
```

Kỳ vọng: `status = "PLAN"`, `google = 84`, `partner = 74`, `missing_keys = 0`, `stale_keys = 0`, `entity_edges_ok = 5`.

R2.5. Ghi lại `V_dict1`, là version mới nhất của từ điển:

```python
print(spark.sql(f"DESCRIBE HISTORY {DICT_FQ} LIMIT 1").select("version", "timestamp", "operation").first())
```

**STOP R2 (bằng chứng).** Ghi toàn bộ kết quả của R2.2 đến R2.5. Chỉ sang R3 khi từ điển có 158 dòng (84/74) và cạnh không đổi so với R1. Nếu có kết quả lệch, dừng lại và xử lý theo `Rollback và forward recovery`. Lúc này `slv_poi_amenity` chưa bị đụng tới.

Bước R3. Dựng lại `slv_poi_amenity`.

R3.1. Chạy DRY_RUN. Chế độ này không commit:

```python
out = notebookutils.notebook.run("NB_SLV_POI_AMENITY", NB_TIMEOUT_S, {"p_mode": "DRY_RUN", "p_force": "true"})
print(out)
print(spark.sql(f"DESCRIBE HISTORY {AMEN_FQ} LIMIT 1").select("version").first())
```

Kỳ vọng về metrics:
- `dict_google_active = 84`, `dict_legacy_form = 0`;
- `conditions_matchable = 53`, `conditions_flag = 27`, `conditions_type = 26`, `conditions_skipped = 31`;
- `conditions_type` gồm 14 key `types[] =` và 12 dòng `json_type`;
- `rows = rows_flag + rows_type`.

Kỳ vọng về diff: số soft-delete bằng `live` của R1.4, và số insert bằng `rows`. Đọc diff từ exit value. Nếu DRY_RUN có ghi log, đọc thêm các cột `inserted_rows` và `deactivated_rows` trong `ctrl_log_table_run`; xem mục log.

Version của `slv_poi_amenity` vẫn phải bằng `V_amen0`. Nếu DRY_RUN raise QualityGateError (trùng key hoặc lệch allowlist), chưa có gì được ghi: dừng lại và kiểm tra từ điển.

R3.2. Xoá bảng amenity và watermark cạnh của bảng đó, để RUN tạo lại như lần đầu. Không DROP từ điển, không DROP `slv_3p_poi_amenity`, không DROP `slv_poi_entity_non_enrich`, không xoá `ctrl_mng_pipeline_config`.

```python
spark.sql("DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_poi_amenity")
spark.sql("""
DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id LIKE 'wm\\_e\\_\\_slv\\_poi\\_amenity\\_\\_%'
""")
```

R3.3. Chạy RUN. Đây là bước ghi:

```python
out = notebookutils.notebook.run("NB_SLV_POI_AMENITY", NB_TIMEOUT_S, {"p_mode": "RUN", "p_force": "true"})
print(out)
RUN1_OUT = out
```

Kỳ vọng: SUCCESS, với cùng metrics như R3.1.

Nếu RUN lỗi, bảng amenity đang rỗng, và không cạnh downstream nào đọc bảng này. Khi đó sửa theo hướng forward rồi chạy lại R3.3, hoặc rollback theo §17.

R3.4. Ghi lại version sau khi chạy:

```python
for fq in [AMEN_FQ, "lh_vv_silver.dbo.slv_3p_poi_amenity", "lh_vv_silver.dbo.slv_poi_entity_non_enrich"]:
    print(fq, spark.sql(f"DESCRIBE HISTORY {fq} LIMIT 1").select("version", "timestamp", "operation").first())
```

Ghi lại `V_amen1`, `V_src1` và `V_ent1`. Nếu `V_src1 = V_src0` và `V_ent1 = V_ent0`, phép so `rows_flag` ở mục kiểm tra là hard check. Nếu khác, chỉ báo cáo độ lệch.

R3.5. Làm các mục `Kiểm tra kết quả`, `Chạy lại để kiểm tra idempotency` và `Kiểm tra log và watermark`.

**STOP R3 (người dùng nghiệm thu).** Sau khi xong R3.5, người dùng chọn một trong hai: chấp nhận kết quả, hoặc chạy rollback theo mục `Rollback và forward recovery`. Bảng backup được giữ lại cho đến khi người dùng quyết định xoá. Việc xoá nằm ngoài runbook.

## Kiểm tra kết quả

Mọi truy vấn chỉ đọc và chạy sau R3.3.

K1. Tổng số dòng, trạng thái live và dạng cũ:

```sql
SELECT count(*) AS total,
       sum(CASE WHEN deleted_at IS NULL THEN 1 ELSE 0 END) AS live,
       sum(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS soft_deleted,
       sum(CASE WHEN amenity_raw LIKE '% = true' OR amenity_raw LIKE 'types[] = %' THEN 1 ELSE 0 END) AS legacy_form,
       count(DISTINCT poi_id) AS pois
FROM lh_vv_silver.dbo.slv_poi_amenity
```

Kỳ vọng: `soft_deleted = 0`, `legacy_form = 0`, `total = live = rows` của R3.3. Báo cáo `total` so với `live` của R1.4, và `pois` so với `live_pois` của R1.4.

K2. Khoá chính không trùng:

```sql
SELECT count(*) AS dup_pk FROM (
    SELECT poi_id, business_sector, amenity_group, amenity_raw
    FROM lh_vv_silver.dbo.slv_poi_amenity
    GROUP BY 1, 2, 3, 4 HAVING count(*) > 1
)
```

Kỳ vọng: `dup_pk = 0`.

K3. So `rows_flag` với backup. Dòng mới không thuộc `TYPE_MATCH` là dòng cờ. Dòng cũ dạng `key = true` bỏ đi 7 ký tự cuối ` = true`.

```sql
WITH new_flag AS (
    SELECT a.business_sector, a.amenity_group, a.amenity_raw, count(*) AS n_new
    FROM lh_vv_silver.dbo.slv_poi_amenity a
    LEFT ANTI JOIN rb_type_keys k
      ON a.business_sector = k.business_sector
     AND a.amenity_group = k.amenity_group
     AND a.amenity_raw = k.amenity_raw
    WHERE a.deleted_at IS NULL
    GROUP BY a.business_sector, a.amenity_group, a.amenity_raw
),
old_flag AS (
    SELECT business_sector, amenity_group,
           substring(amenity_raw, 1, length(amenity_raw) - 7) AS amenity_raw,
           count(*) AS n_old
    FROM lh_vv_silver.dbo.bak_slv_poi_amenity_20261019
    WHERE deleted_at IS NULL AND amenity_raw LIKE '% = true'
    GROUP BY 1, 2, 3
)
SELECT coalesce(n.business_sector, o.business_sector) AS business_sector,
       coalesce(n.amenity_group, o.amenity_group) AS amenity_group,
       coalesce(n.amenity_raw, o.amenity_raw) AS amenity_raw,
       o.n_old, n.n_new
FROM new_flag n
FULL OUTER JOIN old_flag o
  ON n.business_sector = o.business_sector
 AND n.amenity_group = o.amenity_group
 AND n.amenity_raw = o.amenity_raw
WHERE NOT (n.n_new <=> o.n_old)
ORDER BY 1, 2, 3
LIMIT 50
```

Kỳ vọng: 0 dòng. Đây là hard check nếu input không đổi (xem R3.4). Nếu input đã đổi, ghi lại các dòng lệch. Ngoài ra, tổng `n_new` của `new_flag` phải bằng metric `rows_flag`:

```sql
SELECT count(*) AS rows_flag_tbl
FROM lh_vv_silver.dbo.slv_poi_amenity a
LEFT ANTI JOIN rb_type_keys k
  ON a.business_sector = k.business_sector AND a.amenity_group = k.amenity_group AND a.amenity_raw = k.amenity_raw
WHERE a.deleted_at IS NULL
```

K4. Dòng type:

```sql
SELECT a.business_sector, a.amenity_group, a.amenity_raw, count(*) AS n
FROM lh_vv_silver.dbo.slv_poi_amenity a
JOIN rb_type_keys k
  ON a.business_sector = k.business_sector AND a.amenity_group = k.amenity_group AND a.amenity_raw = k.amenity_raw
WHERE a.deleted_at IS NULL
GROUP BY 1, 2, 3 ORDER BY 1, 2, 3 LIMIT 50
```

Tổng `n` phải bằng metric `rows_type`. Kỳ vọng `rows_type > 0`. Nếu bằng 0 thì đó là cảnh báo, không phải lỗi.

K5. Cạnh không đổi:

```python
EDGES_R3 = edges()
print(EDGES_R3 == EDGES_R1, EDGES_R3)
```

Kỳ vọng: `True`.

## Chạy lại để kiểm tra idempotency

Phần này chạy sau `Kiểm tra kết quả` và trước khi quyết định ở STOP R3.

I0. Ghi lại dấu vân tay của bảng trước khi chạy lại:

```sql
SELECT count(*) AS n,
       sum(crc32(concat_ws('|', poi_id, business_sector, amenity_group, amenity_raw, row_hash))) AS fp,
       max(updated_at) AS max_updated_at
FROM lh_vv_silver.dbo.slv_poi_amenity
```

I1. Chạy lại setup apply. Đây là bước ghi, nhưng dự kiến không thay đổi gì:

```python
out = notebookutils.notebook.run("NB_SETUP_POI_AMENITY", NB_TIMEOUT_S, {"p_apply": "true"})
print(out)
```

Kỳ vọng: `inserted = 0`, `drift = 0`, `stale = 0`, `edges_inserted = 0`, `edges_retired = 0`. Từ điển vẫn có 158 dòng (84/74), lặp lại truy vấn đầu tiên của R2.3. `edges()` vẫn bằng `EDGES_R1`.

I2. Chạy lại node RUN với input không đổi. Đây là bước ghi, nhưng dự kiến diff bằng 0:

```python
out = notebookutils.notebook.run("NB_SLV_POI_AMENITY", NB_TIMEOUT_S, {"p_mode": "RUN", "p_force": "true"})
print(out)
```

Kỳ vọng:
- SUCCESS, với metrics giống R3.3;
- trong `ctrl_log_table_run` của lần chạy này, `inserted_rows = 0`, `updated_rows = 0` và `deactivated_rows = 0`;
- chạy lại truy vấn I0 cho đúng `n`, `fp` và `max_updated_at` như trước.

Nếu Delta có commit thêm một version, ghi lại version đó. Điều kiện bắt buộc là dữ liệu không đổi.

Các bước DELETE trong runbook cũng idempotent: DELETE trên bảng rỗng không làm gì. RESTORE về một version cố định cũng idempotent. Mọi bước đều có thể lặp lại từ STOP gần nhất đã đạt.

## Kiểm tra log và watermark

Mọi truy vấn chỉ đọc. Mốc `T0` lấy từ R1.0.

L1. Log node `slv_poi_amenity` kể từ `T0`:

```python
spark.sql(f"""
    SELECT exec_id, run_id, pl_name, trg_tbl, status, entity_rows, inserted_rows, updated_rows,
           deactivated_rows, trg_version, started_at, ended_at, error_message,
           get_json_object(qg_json, '$.mode') AS mode,
           get_json_object(qg_json, '$.force') AS force,
           get_json_object(qg_json, '$.metrics') AS metrics,
           src_versions_json
    FROM lh_vv_ctrl.dbo.ctrl_log_table_run
    WHERE trg_tbl = 'slv_poi_amenity' AND started_at >= TIMESTAMP '{T0}'
    ORDER BY started_at
    LIMIT 50
""").show(50, False)
```

Kỳ vọng:
- Có dòng cho lần RUN ở R3.3 và lần RUN ở I2, và có thể có thêm dòng của DRY_RUN ở R3.1. Ghi lại DRY_RUN có được log hay không.
- Lần RUN ở R3.3 có `status = SUCCESS`, `inserted_rows = rows`, `deactivated_rows = 0`. `trg_version` của nó bằng `V_amen1`.
- Lần RUN ở I2 có `status = SUCCESS` và `inserted_rows`, `updated_rows`, `deactivated_rows` đều bằng 0.
- `metrics` khớp với kỳ vọng §15.
- Trong `src_versions_json`, version của `slv_3p_poi_amenity` và `slv_poi_entity_non_enrich` dùng để quyết định K3 có phải hard check hay không. Version của `ref_dictionary_amenities` phải bằng `V_dict1`, hoặc bằng version của lần setup ở I1 nếu lần đó có commit.

L2. Log mức run cho các `exec_id` ở L1:

```python
spark.sql(f"""
    SELECT r.exec_id, r.run_id, r.pl_name, r.nb_name, r.run_mode, r.status, r.started_at, r.ended_at, r.error_message
    FROM lh_vv_ctrl.dbo.ctrl_log_run r
    WHERE r.exec_id IN (
        SELECT exec_id FROM lh_vv_ctrl.dbo.ctrl_log_table_run
        WHERE trg_tbl = 'slv_poi_amenity' AND started_at >= TIMESTAMP '{T0}')
       OR (r.pl_name = '{PL}' AND r.started_at >= TIMESTAMP '{T0}')
    ORDER BY r.started_at
    LIMIT 50
""").show(50, False)
```

Ghi lại các dòng tìm thấy. Với lần chạy tay, `run_id` bằng `exec_id`. Không được còn dòng nào `status = RUNNING` sau khi runbook kết thúc.

L3. Watermark. Chạy lại truy vấn R1.6 rồi so với snapshot.

Kỳ vọng về lock row `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`: `lock_exec_id` là NULL, và `status` là trạng thái của lần nhả lock gần nhất (SUCCESS).

Kỳ vọng về các dòng cạnh `wm_e__slv_poi_amenity__*`: giữ nguyên so với R1.6. Chỉ NB_00 ghi dòng cạnh; lần chạy tay và setup không ghi.

Lưu ý: ở lần chạy NB_00 kế tiếp, cạnh của `ref_dictionary_amenities` và `slv_poi_amenity` sẽ thấy version mới và tính lại node. Điều này là dự kiến. Table id không đổi vì runbook không `DROP`.

## Rollback và forward recovery

D7: sau DROP, `ref_dictionary_amenities` không còn version 1 để `RESTORE`. Phục hồi từ điển là chạy lại hai lệnh R2. `slv_poi_amenity` chưa bị DROP, nên `V_amen0` vẫn dùng được nếu bước amenity về sau bị từ chối.

Rollback áp dụng khi kết quả bị từ chối ở STOP R3 hoặc muộn hơn, theo §17. Các bước ghi phải chạy dưới flow lock.

RB1. RESTORE cả hai bảng về version baseline:

```python
locked_sql([
    f"RESTORE TABLE {DICT_FQ} TO VERSION AS OF {V_dict0}",
    f"RESTORE TABLE {AMEN_FQ} TO VERSION AS OF {V_amen0}",
])
```

Nếu session đã mất biến, thay `V_dict0` và `V_amen0` bằng số đã ghi ở R1.1.

RB2. Nếu RESTORE lỗi vì file đã bị vacuum, nạp lại từ backup, vẫn dưới lock và cho từng bảng bị lỗi:

```python
locked_sql([
    f"DELETE FROM {DICT_FQ}",
    f"INSERT INTO {DICT_FQ} SELECT * FROM {BAK_DICT_FQ}",
])
locked_sql([
    f"DELETE FROM {AMEN_FQ}",
    f"INSERT INTO {AMEN_FQ} SELECT * FROM {BAK_AMEN_FQ}",
])
```

RB3. Người dùng chạy `git revert` cho commit code `<CẦN NGƯỜI DÙNG CUNG CẤP: commit hash cần revert>` rồi sync DEV. Thứ tự giữa dữ liệu và code không quan trọng về mặt an toàn: nếu chỉ một nửa được rollback, node fail closed (I9), nên không bao giờ ghi ra dòng sai.

RB4. Kiểm tra sau rollback:
- chạy lại R1.2 và R1.4, kết quả phải bằng baseline;
- `edges()` phải bằng `EDGES_R1`;
- lock row có `lock_exec_id` là NULL.

Cạnh không cần rollback vì chưa bao giờ thay đổi. Giữ nguyên các bảng backup.

Forward recovery, dùng khi gặp lỗi code hoặc lỗi dữ liệu thay vì từ chối kết quả: sửa lỗi, đưa bản sửa qua review, redeploy lên DEV, rồi chạy lại từ STOP gần nhất đã đạt.
- Lỗi sau STOP R1: làm lại từ R2.
- Lỗi sau STOP R2: làm lại từ R3.
- Đã RESTORE từ điển cũ nhưng DEV đang chạy code mới: node fail closed. Phục hồi bằng cách làm lại R2 rồi R3.
- Lỗi tạm thời, ví dụ Delta conflict hoặc lỗi mạng: chạy lại đúng bước bị lỗi. Không cần rollback.

Bảng trạng thái khi lỗi giữa chừng, theo §13:
- Sau DELETE từ điển, trước khi seed: node fail closed; chạy lại R2.2.
- Seed MERGE đã commit nhưng bước kiểm cạnh raise `ConfigError`: dừng lại để người dùng quyết định; không sửa cạnh bằng tay.
- Sau DELETE amenity, RUN lỗi: chạy lại R3.3 hoặc rollback.
- MERGE của node bị ngắt giữa chừng: MERGE là atomic nên version trước vẫn còn; chạy lại R3.3.

## Kết quả người dùng ghi nhận

DEV, 2026-10-20. Aggregate, không dữ liệu cá nhân.

R0.1 người dùng xác nhận code DEV khớp commit đã merge. R0.2 pipeline không schedule; coi là pass.

R0.3 `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`: status `SUCCESS`, `lock_exec_id` null, `lock_at` null, `updated_at` 2026-10-19T16:06:29Z. Pass.

R0.4 PLAN: `google=84`, `partner=74`, `missing_keys=41`, `stale_keys=35`, `entity_edges_ok=5`. Pass. Cùng mục có exit `SUCCESS` `inserted=41`, `drift=0`, `stale=35`, `edges_inserted=0`, `edges_retired=0`. Đó là `p_apply=true`, không thuộc R0.4.

R1.0 `T0` = 2026-10-19 19:04:07.920547.

R1.1 `V_dict0=1` (2026-10-16 MERGE), `V_amen0=2` (2026-10-19 16:05:56 MERGE), `slv_3p_poi_amenity` version 4, `slv_poi_entity_non_enrich` version 2.

R1.2 google 78 / inactive 0 / legacy_form 39; partner 74 / inactive 0 / legacy_form 0. Tổng 152. LIKE trong seed mới = 39 − 35 = 4. Stale khác = 0. Pass.

R1.3 history từ điển chỉ CREATE và MERGE insert 152; không UPDATE/DELETE; `merge_upd`/`merge_del` NULL. Drift = 0. Pass.

R1.4 amenity total 97, live 54, soft_deleted 43, live_flag_legacy 54, live_types_legacy 0, live_pois 20.

R1.5 cạnh: `ref_dictionary_amenities` active 1, `slv_3p_poi_amenity` active 1, `slv_poi_entity_non_enrich` active 1, `slv_poi_entity` inactive 1. Truy vấn trùng cặp không có dòng. Pass.

R1.6 cùng watermark flow, `last_src_version` null, `lock_exec_id` null. Không thấy watermark `wm_e__slv_poi_amenity_*`.

Đếm lại từ điển: 193. D7 rồi D8: DROP và `NB_SETUP_POI_AMENITY` `p_apply=true` lần sau cùng thành công: `inserted=158`, `drift=0`, `stale=0`, `edges_inserted=0`, `edges_retired=0`. Từ điển đang là seed `json_type`. R3 `NB_SLV_POI_AMENITY` exec `2f705327-ad9e-43ef-aa95-e94748d81f22`: bảng đích CREATED, ba cạnh `NEW_EDGE`, nguồn 58 dòng, `inserted=58`, `updated=0`, `deactivated=0`, `trg_version=1`, `status=SUCCESS`. Quality gate đã qua vì notebook ghi được. K1: total 58, live 58, soft_deleted 0, legacy_form 0, pois 22. K2: dup_pk 0. Pass. So với R1.4: live 54 thành 58, pois 20 thành 22. Idempotency exec `e2dcb0e9-dceb-4917-a409-237001184aed`: nguồn 58, insert 0, update 0, xoá mềm 0, bỏ qua MERGE, `trg_version` vẫn 1, SUCCESS. User nghiệm thu D9.

