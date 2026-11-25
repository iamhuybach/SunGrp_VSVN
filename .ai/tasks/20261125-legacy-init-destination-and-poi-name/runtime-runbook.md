# Hướng dẫn kiểm chứng runtime

Trạng thái: `CHỜ CHẠY`

Task: `20261125-legacy-init-destination-and-poi-name`. Người dùng tự chạy mọi bước trên Fabric, PostgreSQL và service. Agent không chạy notebook Fabric hay câu lệnh PostgreSQL trong phiên này.

## Phạm vi và môi trường

Runbook này làm hai việc:

- **Sửa dữ liệu Dev.** Chạy lại `NB_SETUP_LEGACY_GOLD_POI` bản đã sửa ở `p_mode = RUN`. `legacy_upsert_sql` chỉ UPDATE dòng `load_origin = 'LEGACY_INIT'`. Vì vậy lần chạy này sửa các dòng LEGACY_INIT đang có:
  - `gld_srv_poi_info.destination_id` đổi từ phần tử đầu `$[0]` sang cả mảng JSON. Giá trị là `to_json(from_json(destination_ids, 'array<string>'))`.
  - `gld_srv_poi_multi_lang.poi_name` được ghi theo đúng `lang`.
- **Init Prod.** Chỉ làm khi người dùng đưa tên workspace Prod.

Workspace và nguồn:

| Mục | Giá trị | Nguồn |
|---|---|---|
| Workspace đích Dev | `sgr_visitvn_dev` | D-03, architecture Rollout Dev bước 4 |
| Workspace đích Prod | `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Prod>` | D-03: không đoán |
| Nguồn gold cũ, chỉ đọc | `OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo"` | `lgpconst`, giữ nguyên |
| Bảng gold đích | `{TARGET_WS}.lh_vv_gold.dbo.` + `gld_poi_legacy_id_map`, `gld_srv_poi_info`, `gld_srv_poi_multi_lang`, `gld_srv_poi_review`, `gld_srv_poi_amenity`, `gld_srv_poi_media_gallery` | `lgpconst` |
| Từ điển amenity | `{TARGET_WS}.lh_vv_silver.dbo.ref_dictionary_amenities` | `lgpconst` `DICT_FQ` |
| Khoá luồng | `{TARGET_WS}.lh_vv_ctrl.dbo.ctrl_mng_watermark`, `watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'` | `lgpconst` `PL`, `lgpnamepy` |
| Bảng PostgreSQL | `apps.srv_poi_multi_lang`, thêm cột `poi_name text` | `sql/postgres/gld_srv_serve.pg.sql` dòng 23 |
| Kết nối PostgreSQL Dev và Prod | `<CẦN NGƯỜI DÙNG CUNG CẤP: host/database PostgreSQL Dev và Prod>` | Không có trong file |
| Service | `services/data-serving-service`, bản build có field `SrvPoiMultiLang.poiName` (`@Column(name = "poi_name")`) | D-08 |

Tham số của `NB_SETUP_LEGACY_GOLD_POI`, cell `lgpparams`, với giá trị mặc định:

```python
p_mode = "PLAN"
p_pin_json = ""
p_target_ws = ""
```

`p_target_ws` mặc định rỗng, nên chạy không truyền tham số sẽ dừng ở `lgpconst`. Chạy theo thứ tự `PLAN` trước, `RUN` sau.

`p_pin_json` cho Dev lấy từ summary RUN init gần nhất có trong repo. File: `.ai/tasks/20261120-legacy-gold-init-mapping-audit/evidence/results/run-summary-d07.json`, `exec_id` `lgp-0141b690fb824d51a542a63c11d8ce47`.

```json
{"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}
```

Nếu sau lần đó Dev đã chạy RUN init với pin khác, dùng pin của lần sau cùng: `<CẦN NGƯỜI DÙNG CUNG CẤP: p_pin_json của RUN init Dev gần nhất, nếu khác giá trị trên>`. Repo không có summary nào mới hơn.

Giới hạn dữ liệu:

- Mọi truy vấn kiểm tra chỉ đọc. Lệnh ghi duy nhất là bước chạy chính: PostgreSQL `ALTER`, cell `lgpnamepy`, `legacyidpy` hoặc `NB_SETUP_INITIAL_DDL` khi init Prod, deploy service, `RUN`.
- Mẫu kết quả tối đa 50 dòng và chỉ gồm id (`poi_id`, `legacy_poi_id`, `lang`). Không in `destination_id`, `poi_name` hay dữ liệu cá nhân.

## Điều kiện tiên quyết

Chung cho Dev và Prod:

1. Code đã qua kiểm tra local theo `architecture.md` Verification Local: pytest bốn file, `pytest -q`, `PoiServiceTest`, `vv.py verify`.
2. Có quyền đọc `sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master`, `poi_enrichment_display`, `poi_detail`, `poi_review` và `poi_rating`, đọc được theo `VERSION AS OF` các pin.
3. Bảng khoá có đúng 1 dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`. Nếu không, `lgpnamepy` dừng với lỗi "chạy plcadpy trước".
4. Không có run `PL_VV_TRANS_SLV_TO_GLD_30M` đang chạy. Kiểm tra `lock_exec_id` NULL hoặc đã quá hạn 90 phút: `LEASE_MINUTES = 90` trong `lgpnamepy`, `LOCK_TIMEOUT_DEFAULT_MIN = 90` trong `NB_LIB_TRANSFORM_SLV_GLD`. Init và `lgpnamepy` giữ cùng khoá này.
5. Các notebook đã sửa được đưa lên workspace đích: `NB_SETUP_LEGACY_GOLD_POI`, `NB_CREATE_DDL`, `NB_GLD_SRV_POI_MULTI_LANG`, `NB_SETUP_INITIAL_DDL`, `NB_LIB_TRANSFORM_SLV_GLD`. Cách đưa lên: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách deploy notebook lên workspace (git sync / import)>`.
6. Notebook init phải mở trong chính workspace `p_target_ws`. Nếu `_workspace_name() != TARGET_WS`, init dừng với lỗi "Notebook phải mở ở workspace …".

Riêng Dev:

- Bảng `gld_srv_poi_info`, `gld_srv_poi_multi_lang`, `gld_srv_poi_review`, `gld_srv_poi_amenity` và `gld_srv_poi_media_gallery` đã có `load_origin` kiểu string. Bảng `gld_poi_legacy_id_map` đã có từ init trước.

Riêng Prod:

- Người dùng đã đưa tên workspace Prod. Trên Prod có `lh_vv_silver.dbo.ref_dictionary_amenities` và dòng khoá luồng nói ở mục 3.

## Baseline trước khi chạy

Chụp baseline ngay trước bước 1 của "Các bước thực hiện" và ghi vào "Kết quả người dùng ghi nhận".

**B0. Cell hằng dùng chung (PySpark, chỉ đọc).** Mở cell này trong một notebook ở workspace đích và dùng lại cho mọi kiểm tra sau.

```python
from pyspark.sql import functions as F

WS = "sgr_visitvn_dev"   # Prod: "<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Prod>"
OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo"
PIN_PM = 8074            # Prod: pins.poi_master của summary PLAN Prod
PIN_DISP = 6495          # Prod: pins.poi_enrichment_display của summary PLAN Prod
MAP_FQ = f"{WS}.lh_vv_gold.dbo.gld_poi_legacy_id_map"
INFO_FQ = f"{WS}.lh_vv_gold.dbo.gld_srv_poi_info"
ML_FQ = f"{WS}.lh_vv_gold.dbo.gld_srv_poi_multi_lang"
WM_FQ = f"{WS}.lh_vv_ctrl.dbo.ctrl_mng_watermark"
LOG_FQ = f"{WS}.lh_vv_ctrl.dbo.ctrl_log_run"
WID = "wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M"

STR_ELEM = r'"(?:[^"\\]|\\.)*"'
ARRAY_EMPTY = r"^\[\s*\]$"
ARRAY_STRINGS = rf"^\[{STR_ELEM}(?:\s*,\s*{STR_ELEM})*\]$"
ARRAY_STR_OR_NULL = rf"^\[(?:null|{STR_ELEM})(?:\s*,\s*(?:null|{STR_ELEM}))*\]$"

def ver(fq):
    return int(spark.sql(f"DESCRIBE HISTORY {fq} LIMIT 1").first()["version"])

def at(fq, v):
    return spark.sql(f"SELECT * FROM {fq} VERSION AS OF {int(v)}")

def dest_shape(c):
    t = F.trim(c)
    return (F.when(c.isNull(), "null").when(t == "", "blank")
            .when(t.rlike(ARRAY_EMPTY), "json_array_empty")
            .when(t.rlike(ARRAY_STRINGS), "json_array_string")
            .when(t.rlike(ARRAY_STR_OR_NULL), "json_array_null_elem")
            .when(t.startswith("["), "json_array_other")
            .otherwise("not_array"))
```

Các regex lấy từ probe `evidence/probes/destination_id_non_legacy_shape.py`.

**B1. Version và số dòng gold (chỉ đọc).**

```python
print("versions", {fq.split(".")[-1]: ver(fq) for fq in (MAP_FQ, INFO_FQ, ML_FQ)})
print("map", spark.table(MAP_FQ).agg(F.count("*").alias("n"),
      F.countDistinct("legacy_poi_id").alias("legacy_d"), F.countDistinct("poi_id").alias("poi_d")).first())
for fq, keys in ((INFO_FQ, ["poi_id"]), (ML_FQ, ["poi_id", "lang"])):
    for r in (spark.table(fq).groupBy("load_origin")
              .agg(F.count("*").alias("n"), F.countDistinct(*keys).alias("k")).collect()):
        print(fq.split(".")[-1], r["load_origin"], r["n"], r["k"])
print("ml poi_name type", dict(spark.table(ML_FQ).dtypes).get("poi_name"))
for r in (spark.table(INFO_FQ).where("load_origin = 'LEGACY_INIT'")
          .groupBy(dest_shape(F.col("destination_id")).alias("s")).count().orderBy("s").collect()):
    print("legacy dest shape", r["s"], r["count"])
```

Kỳ vọng trên Dev trước khi sửa:

- `ml poi_name type` là `None`. Nếu đã là `string`, `lgpnamepy` hoặc `ensure_target` đã chạy trước, và bước 2 sẽ là no-op.
- Các dòng LEGACY_INIT có nhiều `not_array`, do `$[0]` cũ. Để tham chiếu, probe 25/11 đếm được 25921 dòng LEGACY_INIT và 19909 dòng `load_origin` NULL.

**B2. Khoá luồng (chỉ đọc).**

```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, error_message, updated_at
FROM <WS>.lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```

Kỳ vọng: đúng 1 dòng và `lock_exec_id` NULL.

**B3. PostgreSQL (chỉ đọc).**

```sql
SELECT column_name, data_type, is_nullable
FROM information_schema.columns
WHERE table_schema = 'apps' AND table_name = 'srv_poi_multi_lang' AND column_name = 'poi_name';
```

Kỳ vọng trên Dev trước bước 1: 0 dòng. Trên DB Prod mới tạo bằng `gld_srv_serve.pg.sql` bản mới: 1 dòng `text`.

## Các bước thực hiện

### Dev (`p_target_ws = "sgr_visitvn_dev"`)

Thứ tự bắt buộc: PostgreSQL `ALTER`, rồi `lgpnamepy`, rồi deploy service, rồi `PLAN`, rồi `RUN`, rồi các kiểm tra (a) đến (e). Không đảo bước 1 và bước 3: service có `ddl-auto: none`, nên nếu entity map cột `poi_name` mà PostgreSQL chưa có cột này thì query sẽ lỗi.

**Bước 1. PostgreSQL Dev (ghi).**

```sql
ALTER TABLE apps.srv_poi_multi_lang ADD COLUMN poi_name text;
```

Chạy lại B3 và kỳ vọng 1 dòng `text`, `YES`. Nếu lệnh báo "already exists", cột đã có và không có gì thay đổi.

**Bước 2. `NB_CREATE_DDL` cell `lgpnamepy` (ghi schema).**

- Mở `NB_CREATE_DDL` trong `sgr_visitvn_dev` và chạy đúng một cell `lgpnamepy`. Cell này tự đọc `currentWorkspaceName` và giữ khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`.
- Không chạy lại `legacyidpy` trên Dev, vì map và `load_origin` đã có.
- Kỳ vọng in ra `lgpname: + poi_name sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang`. Nếu cột đã có thì in `=`.
- Nếu báo "đang giữ khoá", chờ run 30M xong rồi chạy lại.
- Nếu pipeline 30M bản mới đã chạy trước bước này, `ensure_target` đã thêm `poi_name` ở cuối bảng. Khi đó `lgpnamepy` in `=` và không cần làm gì thêm.

**Bước 3. Deploy service (ghi, outward).**

- Deploy bản build có `SrvPoiMultiLang.poiName`: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách deploy và phiên bản build service Dev>`.
- Kiểm tra service khởi động và log không có lỗi về cột `poi_name`. Endpoint health hoặc API để thử: `<CẦN NGƯỜI DÙNG CUNG CẤP: URL health/API Dev>`.
- JSON của API không đổi, vì DTO không được sửa.

**Bước 4. `NB_SETUP_LEGACY_GOLD_POI` ở `PLAN` (chỉ đọc, không lấy khoá).**

```text
p_mode = "PLAN"
p_target_ws = "sgr_visitvn_dev"
p_pin_json = '{"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}'
```

Lưu toàn bộ JSON summary (`print` hoặc `notebook.exit`). Các cổng cần qua:

- `target_ws` = `sgr_visitvn_dev` và `pins` đúng như trên.
- `map.drift_n = 0` và `map.bad_key_n = 0`.
- `destination.decision = "OK"`, tức là `stop_n = 0` và `conflict_n = 0`. Ghi lại `destination.shape`, có dạng `{class: n}` với các lớp `NULL`, `EMPTY`, `STRINGS`.
- Ghi lại `info.destination_filled_n`.
- Ghi lại `multi_lang.name_conflict_n` và `multi_lang.name_filled_n`.
- Ghi lại `info.candidates`, `info.to_insert`, `multi_lang.candidates` và `multi_lang.to_insert`. Với cùng pin, `info.candidates` nên bằng 45476 như ở `run-summary-d07.json`. Nếu khác, dừng lại và báo.

**DỪNG nếu `destination.decision = "USER_DECISION"`.**

- Không chạy `RUN`.
- Báo lại `destination.shape`, `destination.stop_n`, `destination.conflict_n`, `destination.stop_samples` (tối đa 5 `legacy_poi_id`) và `destination.conflict_samples` (tối đa 5 `poi_id`).
- Không sửa code cho đến khi quyết định được ghi vào `decision.md`.
- Ở lần dừng này chưa có gì được ghi.

**Bước 5. `NB_SETUP_LEGACY_GOLD_POI` ở `RUN` (ghi).**

```text
p_mode = "RUN"
p_target_ws = "sgr_visitvn_dev"
p_pin_json = '{"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}'
```

Dùng đúng pin của bước 4. Lần RUN này UPDATE các dòng LEGACY_INIT đang có của info và multi_lang. Dòng có `load_origin` NULL không bị đụng tới. Lưu summary (gọi là **RUN1**) và ghi lại các mục sau:

- `exec_id`.
- `map.v_pre`, `map.v_post`, `map.inserted`, `map.commit`.
- `info.v_pre`, `info.v_post`, `info.inserted`.
- `multi_lang.v_pre`, `multi_lang.v_post`, `multi_lang.inserted`.

Kỳ vọng:

- `map.inserted = 0` và `map.commit = "NOT_COMMITTED"`, vì map chỉ INSERT và cùng pin.
- `info.inserted` bằng `info.to_insert` của PLAN, và `multi_lang.inserted` bằng `multi_lang.to_insert` của PLAN.
- `info.commit` và `multi_lang.commit` là `"COMMITTED"`.

Nếu lỗi, xem `failed_stage` rồi đọc "Rollback và forward recovery".

**Bước 6.** Chạy các kiểm tra (a), (b) và (d) ở "Kiểm tra kết quả". Sau đó chạy (c) ở "Chạy lại để kiểm tra idempotency", rồi (e).

### Prod (`p_target_ws = "<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Prod>"`)

Chỉ làm sau khi Dev đã PASS và người dùng đã đưa tên workspace Prod.

1. **PostgreSQL Prod.**
   - Chạy B3 trước.
   - Nếu chưa có cột: `ALTER TABLE apps.srv_poi_multi_lang ADD COLUMN poi_name text;`.
   - DB mới tạo bằng `gld_srv_serve.pg.sql` bản mới đã có cột này, nên bỏ qua bước này.
2. **Schema gold Prod.**
   - Workspace mới: chạy `NB_SETUP_INITIAL_DDL`. Notebook này tạo `poi_name` ngay sau `lang`.
   - Bảng đã có: chạy cell `lgpnamepy` của `NB_CREATE_DDL`.
3. **`NB_CREATE_DDL` cell `legacyidpy`.** Cell này tự lấy workspace đang chạy và tạo `gld_poi_legacy_id_map` cùng cột `load_origin`.
4. **Deploy service Prod:** `<CẦN NGƯỜI DÙNG CUNG CẤP: cách deploy và phiên bản build service Prod>`. Không deploy trước bước 1.
5. **PLAN:** `p_mode = "PLAN"`, `p_target_ws = "<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Prod>"`, `p_pin_json = ""`. Khi rỗng, init lấy version mới nhất và in ra `pins`.
   - Áp các cổng giống bước 4 của Dev.
   - Gặp `USER_DECISION` thì dừng như trên.
   - Ghi lại `pins` của summary PLAN Prod.
6. **RUN:** `p_mode = "RUN"`, cùng `p_target_ws`, và `p_pin_json` = đúng chuỗi JSON `pins` của summary PLAN Prod ở bước 5.
7. **Kiểm tra (a) đến (e)** với B0: `WS` = workspace Prod, `PIN_PM` và `PIN_DISP` lấy từ `pins` Prod. Ở lần init Prod đầu tiên, `map.inserted` và `inserted` của các bảng sẽ lớn hơn 0.

## Kiểm tra kết quả

Mọi kiểm tra dưới đây chỉ đọc, chạy sau RUN1 và dùng cell B0.

**(a) Dạng `destination_id` của dòng LEGACY_INIT.**

```python
d = F.col("destination_id")
canon = F.to_json(F.from_json(d, "array<string>"))
info = spark.table(INFO_FQ).where("load_origin = 'LEGACY_INIT'")
for r in info.groupBy(dest_shape(d).alias("s")).count().orderBy("s").collect():
    print("shape", r["s"], r["count"])
print(info.agg(
    F.count("*").alias("legacy_n"),
    F.count(d).alias("filled_n"),
    F.sum(F.when(d.isNotNull() & ~d.startswith("["), 1).otherwise(0)).alias("not_bracket_n"),
    F.sum(F.when(d.isNotNull() & ~canon.eqNullSafe(d), 1).otherwise(0)).alias("not_canonical_n"),
).first())
```

Pass khi:

- `bad = 0`, tức là tổng của `blank`, `json_array_other` và `not_array` bằng 0.
- `json_array_null_elem = 0`.
- `not_bracket_n = 0`, tương đương `count(destination_id NOT LIKE '[%' AND destination_id IS NOT NULL) = 0`.
- `not_canonical_n = 0`, nghĩa là chuỗi đúng dạng compact của `to_json`.

`filled_n` không lớn hơn `info.destination_filled_n` của summary. Summary đếm cả khoá mà pipeline đang sở hữu, init không UPDATE các khoá đó.

Nếu có lỗi, lấy mẫu id (tối đa 50, không in giá trị):

```python
info.where(dest_shape(d).isin("blank", "json_array_other", "not_array", "json_array_null_elem")) \
    .select("poi_id").orderBy("poi_id").limit(50).show(50, False)
```

**(b) `poi_name` theo lang trên multi_lang LEGACY_INIT.** Truy vấn này dựng lại tên kỳ vọng đúng như init: display tại pin, nối với map `OK`, rồi nối với `poi_master` tại pin.

```python
mp = spark.table(MAP_FQ).where("poi_id_status = 'OK'").select("legacy_poi_id", "lang", "poi_id")
disp = (at(f"{OLD}.poi_enrichment_display", PIN_DISP).where("lang IS NOT NULL")
        .select(F.col("poi_id").alias("legacy_poi_id")))
pm = at(f"{OLD}.poi_master", PIN_PM).select(F.col("poi_id").alias("legacy_poi_id"), F.col("poi_name").alias("n"))
exp = (disp.join(mp, "legacy_poi_id").join(pm, "legacy_poi_id", "left")
       .groupBy("poi_id", "lang").agg(F.collect_set(F.struct("n")).alias("s")))
vi = (mp.where("lang = 'vi'").join(pm, "legacy_poi_id")
      .groupBy("poi_id").agg(F.collect_set(F.struct("n")).alias("v")))
t = spark.table(ML_FQ).where("load_origin = 'LEGACY_INIT'").select("poi_id", "lang", "poi_name")
j = t.join(exp, ["poi_id", "lang"], "left").join(vi, "poi_id", "left")
one = F.coalesce(F.size("s") == 1, F.lit(False))
many = F.coalesce(F.size("s") > 1, F.lit(False))
e = F.col("s").getItem(0)["n"]
vn = F.when(F.size("v") == 1, F.col("v").getItem(0)["n"])
print(j.agg(
    F.count("*").alias("ml_legacy_n"),
    F.count("poi_name").alias("name_filled_n"),
    F.sum(F.when(F.col("s").isNull(), 1).otherwise(0)).alias("no_expect_n"),
    F.sum(F.when(many, 1).otherwise(0)).alias("name_conflict_keys"),
    F.sum(F.when(many & F.col("poi_name").isNotNull(), 1).otherwise(0)).alias("conflict_not_null_n"),
    F.sum(F.when(one & ~F.col("poi_name").eqNullSafe(e), 1).otherwise(0)).alias("mismatch_n"),
    F.sum(F.when(one & (F.col("lang") != "vi") & F.col("poi_name").isNotNull()
                 & (F.col("poi_name") == vn) & (e != vn), 1).otherwise(0)).alias("vi_copied_n"),
).first())
```

Pass khi:

- `mismatch_n = 0`, sau khi đã loại các khoá xung đột tên.
- `conflict_not_null_n = 0`. Khoá xung đột tên phải có `poi_name` NULL.
- `vi_copied_n = 0`. Không có tên `vi` bị chép sang lang khác.

Ghi lại `name_filled_n`, `name_conflict_keys` và `no_expect_n`. `name_conflict_keys` không lớn hơn `multi_lang.name_conflict_n` của summary. Nếu `mismatch_n > 0`, lấy mẫu `poi_id`, `lang` (tối đa 50) bằng `j.where(one & ~F.col("poi_name").eqNullSafe(e)).select("poi_id","lang").limit(50)` và không in tên.

**(d) Dòng có `load_origin` NULL không đổi.** Thay `<…>` bằng `v_pre` và `v_post` của RUN1, và làm lại với RUN2.

```python
def null_owned_diff(fq, v_pre, v_post):
    a = at(fq, v_pre).where("load_origin IS NULL")
    b = at(fq, v_post).where("load_origin IS NULL")
    return a.exceptAll(b).count(), b.exceptAll(a).count()

print("info", null_owned_diff(INFO_FQ, <info.v_pre RUN1>, <info.v_post RUN1>))
print("ml", null_owned_diff(ML_FQ, <multi_lang.v_pre RUN1>, <multi_lang.v_post RUN1>))
```

Pass khi cả hai chiều đều bằng `(0, 0)`. Info và multi_lang dùng `legacy_upsert_sql` với `claim_null=False`, nên init không UPDATE hay chiếm dòng pipeline.

**Kiểm tra PostgreSQL và service sau khi sync.** Sau lần sync gold sang serving kế tiếp, chạy:

```sql
SELECT count(*) AS n, count(poi_name) AS name_n FROM apps.srv_poi_multi_lang;
```

Ghi lại kết quả. Không đặt ngưỡng, vì cơ chế sync không nằm trong file của task này. Ngoài ra kiểm tra API trả multi-lang như trước.

## Chạy lại để kiểm tra idempotency

**(c) RUN lần hai (RUN2) với cùng tham số.** Chạy ngay sau RUN1:

```text
p_mode = "RUN"
p_target_ws = "sgr_visitvn_dev"   # Prod: workspace Prod
p_pin_json = '{"poi_master": 8074, "poi_enrichment_display": 6495, "poi_detail": 6920, "poi_review": 69, "poi_rating": 63}'   # Prod: pins của PLAN Prod
```

Kỳ vọng trong summary RUN2:

- `map.inserted = 0`, `info.inserted = 0`, `multi_lang.inserted = 0`.
- `info.to_insert = 0` và `multi_lang.to_insert = 0`.
- `destination.decision = "OK"`.
- `destination.shape`, `info.destination_filled_n`, `multi_lang.name_filled_n` và `multi_lang.name_conflict_n` bằng RUN1.

Đã biết trước: mỗi RUN đặt lại `updated_at` của mọi dòng LEGACY_INIT thành `batch_ts`, kể cả khi giá trị không đổi.

Kiểm tra `poi_id` không đổi:

```python
R1_MAP, R1_INFO, R1_ML = <map.v_post RUN1>, <info.v_post RUN1>, <multi_lang.v_post RUN1>
cols = ["legacy_poi_id", "lang", "legacy_ingestion_source", "source_id", "source_name", "poi_id", "poi_id_status"]
a, b = at(MAP_FQ, R1_MAP).select(*cols), spark.table(MAP_FQ).select(*cols)
print("map diff", a.exceptAll(b).count(), b.exceptAll(a).count())
for fq, v, keys in ((INFO_FQ, R1_INFO, ["poi_id"]), (ML_FQ, R1_ML, ["poi_id", "lang"])):
    x, y = at(fq, v), spark.table(fq)
    print(fq.split(".")[-1],
          x.agg(F.count("*"), F.countDistinct("poi_id")).first(),
          y.agg(F.count("*"), F.countDistinct("poi_id")).first(),
          x.select(*keys).exceptAll(y.select(*keys)).count(),
          y.select(*keys).exceptAll(x.select(*keys)).count())
```

Pass khi:

- `map diff` bằng `(0, 0)`.
- Với info và multi_lang, `count(*)` và `count(DISTINCT poi_id)` không đổi, và khoá lệch cả hai chiều bằng 0.

Nếu một run 30M chen vào giữa RUN1 và RUN2, `last_run_id` của `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` sẽ đổi. Khi đó số dòng info và multi_lang có thể đổi một cách hợp lệ. Trường hợp này vẫn bắt buộc `inserted = 0` và `map diff = (0, 0)`, rồi ghi rõ là có run chen vào.

Chạy lại (d) với `v_pre` và `v_post` của RUN2.

**(e) Sau đúng một run `PL_VV_TRANS_SLV_TO_GLD_30M` sau RUN2.**

```python
post = at(ML_FQ, <multi_lang.v_post RUN2>).where("load_origin = 'LEGACY_INIT'").select("poi_id", "lang")
took = spark.table(ML_FQ).where("load_origin IS NULL").join(post, ["poi_id", "lang"], "left_semi")
print("taken_over_n", took.count(), "taken_over_null_name_n", took.where("poi_name IS NULL").count())
```

Kỳ vọng `taken_over_n = taken_over_null_name_n`. Theo D-02, pipeline nhận dòng thì ghi `poi_name` NULL, và đây là hành vi đã chấp nhận. Báo lại số này.

## Kiểm tra log và watermark

- Init không ghi `ctrl_log_run`. Cell `lgpmain` chỉ dùng `acquire_flow_lock`, `refresh_flow_lock` và `release_flow_lock`. Bằng chứng của mỗi lần chạy là summary JSON và Delta history.
- **Khoá luồng sau mỗi lần chạy** (`lgpnamepy`, RUN1, RUN2): chạy lại truy vấn B2.
  - Kỳ vọng `lock_exec_id` NULL và `lock_at` NULL.
  - Sau RUN, `status = 'SUCCESS'`.
  - Sau `lgpnamepy`, `status = 'SUCCESS'` và `error_message = ''`.
  - Lỗi thì có `status = 'FAILED'` kèm `error_message`.
  - PLAN không lấy khoá, nên dòng khoá không đổi.
- **Delta history.** Mỗi bảng info, multi_lang, review, media và amenity có đúng một commit `userMetadata = 'LEGACY_INIT:<exec_id>'` cho mỗi RUN. Map chỉ có commit này khi `map.inserted > 0`.

```sql
DESCRIBE HISTORY <WS>.lh_vv_gold.dbo.gld_srv_poi_info LIMIT 10;
DESCRIBE HISTORY <WS>.lh_vv_gold.dbo.gld_srv_poi_multi_lang LIMIT 10;
```

  Đối chiếu `version` của các commit này với `v_post` trong summary.
- **`lgpnamepy`.** `DESCRIBE HISTORY` của `gld_srv_poi_multi_lang` có một commit `ADD COLUMNS` cho `poi_name`. Lần chạy lại không tạo commit mới.
- **Run 30M dùng cho (e).**

```sql
SELECT exec_id, pl_name, status, started_at, ended_at, error_message
FROM <WS>.lh_vv_ctrl.dbo.ctrl_log_run
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'
ORDER BY started_at DESC
LIMIT 5;
```

  Kỳ vọng có ít nhất một dòng `SUCCESS` hoặc `NO_DATA`, với `started_at` sau thời điểm RUN2 kết thúc.

## Rollback và forward recovery

**Lỗi giữa chừng.**

- Summary có `failed_stage`, và khoá được nhả trong `finally`.
- Chạy lại RUN với cùng `p_target_ws` và `p_pin_json`. Các stage đã commit sẽ được áp lại theo cách idempotent.
- Khoá bận ("Không nhận khoá"): chạy lại sau.
- Preflight báo "chưa có poi_name string: chạy lgpnamepy của NB_CREATE_DDL trước": chạy bước 2 rồi chạy lại.
- `USER_DECISION`: chưa có gì được ghi. Báo lại và chờ quyết định.

**Code.**

- Revert các notebook. Cột gold `poi_name` nullable được giữ lại. Code pipeline cũ không trả `poi_name`: `ensure_target` chỉ cảnh báo và để nguyên giá trị.
- **Không chạy lại code init cũ**, vì nó sẽ ghi lại `$[0]`.

**Service.**

- Rollback service trước: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách rollback service>`.
- Sau đó, nếu muốn, bỏ cột PostgreSQL: `ALTER TABLE apps.srv_poi_multi_lang DROP COLUMN poi_name;`.
- Không bỏ cột khi service mới còn đang chạy.

**Dữ liệu.**

- **Không `RESTORE`** bảng gold, vì làm vậy sẽ mất các commit của pipeline.
- Cách ưu tiên là forward recovery: sửa code rồi chạy lại init. Init chỉ ghi đè dòng LEGACY_INIT.
- Nếu cần trả đúng một bảng về trạng thái trước RUN, dùng MERGE từ `VERSION AS OF <v_pre>` lấy trong summary. Chỉ áp cho khoá có `load_origin = 'LEGACY_INIT'` ở cả hai version.
- Chạy khi `lock_exec_id` của `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` là NULL. Đây là lệnh ghi và chỉ chạy khi người dùng quyết định.
- Revert này đưa `destination_id` về dạng `$[0]` cũ.

```sql
MERGE INTO <WS>.lh_vv_gold.dbo.gld_srv_poi_info AS t
USING (SELECT * FROM <WS>.lh_vv_gold.dbo.gld_srv_poi_info VERSION AS OF <info.v_pre>) AS s
ON t.poi_id = s.poi_id AND t.load_origin = 'LEGACY_INIT' AND s.load_origin = 'LEGACY_INIT'
WHEN MATCHED THEN UPDATE SET *;

MERGE INTO <WS>.lh_vv_gold.dbo.gld_srv_poi_multi_lang AS t
USING (SELECT * FROM <WS>.lh_vv_gold.dbo.gld_srv_poi_multi_lang VERSION AS OF <multi_lang.v_pre>) AS s
ON t.poi_id = s.poi_id AND t.lang = s.lang AND t.load_origin = 'LEGACY_INIT' AND s.load_origin = 'LEGACY_INIT'
WHEN MATCHED THEN UPDATE SET *;
```

Các khoá mới được RUN INSERT thêm không bị MERGE này xoá. Trên Dev, khi `to_insert = 0` thì không có khoá như vậy.

## Kết quả người dùng ghi nhận

| Mốc | Môi trường | Thời điểm | exec_id | Kết quả chính | PASS/FAIL |
|---|---|---|---|---|---|
| B1–B3 baseline | Dev | | — | versions; số dòng theo `load_origin`; shape LEGACY_INIT; `poi_name` gold/PG | |
| Bước 1 PG ALTER | Dev | 2026-11-25 15:52:35 GMT+07 | — | `ALTER TABLE apps.srv_poi_multi_lang ADD COLUMN poi_name text` hết 0.056s, không báo lỗi. Client ghi Updated Rows 0. | PASS |
| Bước 2 `lgpnamepy` | Dev | 2026-11-25 | — | `lgpname: + poi_name sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_multi_lang` | PASS |
| Bước 3 service | Dev | 2026-11-25 | 3851581 | Đã push `develop` của `SunGrp_VSVN_API`: entity `poi_name`, JSON API không đổi. Bản chạy trên server là bước deploy sau push. | PASS git |
| Bước 4 PLAN | Dev | 2026-11-25 | lgp-49df85f0d5234ef3ae217f2b18037776 | `target_ws=sgr_visitvn_dev`. Pin đúng. `drift_n=0`, `bad_key_n=0`. `destination.decision=OK`, `stop_n=0`, `conflict_n=0`, shape `STRINGS` 136352, `NULL` 411. `destination_filled_n=45336`. `name_conflict_n=0`, `name_filled_n=136532`. `info.candidates=45476`, `info.to_insert=0`, `multi_lang.to_insert=0`. | PASS |
| Bước 5 RUN1 | Dev | 2026-11-25 | lgp-8f6cffbe4f0f426f9442f98734fee186 | map `v_pre=1` `v_post=1` `inserted=0` `commit=NOT_COMMITTED`. info `v_pre=23` `v_post=24` `inserted=0` `commit=COMMITTED`. multi_lang `v_pre=16` `v_post=17` `inserted=0` `commit=COMMITTED`. `destination.decision=OK`. | PASS |
| (a) | Dev | 2026-11-25 | lgp-8f6cffbe4f0f426f9442f98734fee186 | `json_array_string` 25917, `null` 4. `legacy_n=25921`, `filled_n=25917`, `not_bracket_n=0`, `not_canonical_n=0`. | PASS |
| (b) | Dev | 2026-11-25 | lgp-8f6cffbe4f0f426f9442f98734fee186 | `ml_legacy_n=77751`, `name_filled_n=77751`, `no_expect_n=0`, `name_conflict_keys=0`, `conflict_not_null_n=0`, `mismatch_n=0`, `vi_copied_n=0`. | PASS |
| (d) RUN1 | Dev | 2026-11-25 | lgp-8f6cffbe4f0f426f9442f98734fee186 | info `(0, 0)`; ml `(0, 0)`. | PASS |
| (c) RUN2 | Dev | 2026-11-25 | lgp-439e1bfac7674dbb9479a765543b7915 | `map diff` 0 0. info 45830/45830 cả hai version, lệch khóa 0 0. multi_lang 137477 dòng, 45833 `poi_id`, lệch khóa 0 0. | PASS |
| (d) RUN2 | Dev | 2026-11-25 | lgp-439e1bfac7674dbb9479a765543b7915 | info `(0, 0)`; ml `(0, 0)`. | PASS |
| (e) | Dev | 2026-11-25 | 583b27ed-41b6-492a-afdf-9ee90a65d4e5 | `NB_00` `NO_DATA` 86s: 5 node, 15 cạnh, 0 Dirty Edge, 0 node ứng viên. `taken_over_n=0`, `taken_over_null_name_n=0`. | PASS |
| Khoá/log | Dev | 2026-11-25 | lgp-439e1bfac7674dbb9479a765543b7915 | `lock_exec_id` null, `lock_at` null, `status=SUCCESS`. | PASS |
| Prod (bước 1–7) | `<CẦN NGƯỜI DÙNG CUNG CẤP: tên workspace Prod>` | | | pins PLAN Prod; (a)–(e) | |

Ghi chú hoặc quyết định `USER_DECISION`, nếu có: PLAN Dev 2026-11-25 không dừng. `info.cmp_conflict_n=200`, `amenity.conflict_n=87`, `vi_key_collision_n=1` không nằm trong cổng dừng của task này. Kiểm tra (e): orchestrator không chạy node nào, nên không có dòng `LEGACY_INIT` bị pipeline nhận. Hai số takeover bằng nhau.
