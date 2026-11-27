# Runtime runbook — 20261127-slv-pn-product-l2-transform

Nguồn: `architecture.md` (`## Main brief`, `## Rollout`, `## Rollback and forward recovery`, `## Verification` R1–R3), các parameter cell `pnsaleparam`, `pnroomparam`, `pnrateparam`, cell `pnl2edgepy` của `notebooks/NB_CREATE_DDL.ipynb`, probe `evidence/probes/pnl2_invariants.py`, và `docs/context/CTRL_TABLES_CONTEXT.md` §3, §4, §6, §7. Không có pipeline JSON cho task này.

## Phạm vi và môi trường

- Môi trường: Fabric DEV. Lakehouse đích là `lh_vv_silver` (schema `lh_vv_silver.dbo`). Bảng control nằm ở `lh_vv_ctrl.dbo`.
- Workspace id: `<CẦN NGƯỜI DÙNG CUNG CẤP: workspace id Fabric DEV>`. Capacity: `<CẦN NGƯỜI DÙNG CUNG CẤP: capacity DEV>`. Runbook không giả định hai giá trị này.
- Commit cần deploy: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit SHA đã merge gồm lib, 3 node, seed, patch cell và test>`. Cách import notebook (git sync hoặc import tay): `<CẦN NGƯỜI DÙNG CUNG CẤP: cách deploy notebook lên DEV>`.
- Notebook trong phạm vi:
  - `NB_LIB_TRANSFORM_SLV_GLD`: thêm `NodeSpec.deleted_flag`. Khi giá trị là `None`, code path cũ giữ nguyên (I1).
  - `NB_SLV_PN_PRODUCT_SALE` → `lh_vv_silver.dbo.slv_pn_product_sale`, khoá `product_id`.
  - `NB_SLV_PN_HOTEL_ROOM_OFFER` → `lh_vv_silver.dbo.slv_pn_hotel_room_offer`, khoá `room_type_id`.
  - `NB_SLV_PN_HOTEL_RATE_OFFER` → `lh_vv_silver.dbo.slv_pn_hotel_rate_offer`, khoá `rate_plan_id`.
  - `NB_CREATE_DDL`: chỉ chạy cell `pnl2edgepy`. Cell này thêm 5 cạnh RECOMPUTE vào `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` và không có DDL.
- Pipeline sở hữu cả ba bảng: `PL_VV_TRANS_SLV_TO_GLD_30M`. Notebook điều phối là `NB_00_ORCHES_SLV_TO_GLD`. Khoá luồng là dòng `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` trong `lh_vv_ctrl.dbo.ctrl_mng_watermark`.
- Nguồn L1, chỉ đọc: `lh_vv_silver.dbo.slv_pn_products`, `slv_pn_product_posts`, `slv_pn_product_variants`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`.
- Bảng tạm của R1: `lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8>`. `<exec8>` là 8 ký tự hex do script R1 tự sinh.
- Ngoài phạm vi: STG/PROD, `TABLE_SPECS`, `ctrl_cfg_schema_registry`, và chạy `NB_SETUP_INITIAL_DDL`. Seed `init_seed_ctrl` chỉ dùng cho môi trường dựng mới, không chạy trên DEV.
- Thứ tự bắt buộc của người dùng: deploy `NB_LIB_TRANSFORM_SLV_GLD` trước ba notebook node. Không chạy `NB_00` (cả GLD30 và ENR15) cho đến khi R1 PASS.
  - Mục Rollout của architecture đặt bước quan sát GLD30/ENR15 (bước 2) trước R1 (bước 3). Runbook này đổi chỗ hai bước để giữ đúng ràng buộc trên: R1 chạy ngay sau khi import lib, sau đó mới quan sát NB_00.
  - Trigger lịch GLD30/ENR15 vẫn có thể tự chạy NB_00 với lib mới trong lúc R1 chưa xong. Có tạm dừng trigger lịch trên DEV trong khoảng này hay không: `<CẦN NGƯỜI DÙNG CUNG CẤP: tạm dừng trigger lịch PL_VV_TRANS_SLV_TO_GLD_30M và PL_VV_TRANS_SLV_TO_ENR_15M trong lúc chạy R1 hay không>`.
- Quy ước kết quả: dán toàn bộ output vào `.ai/tasks/20261127-slv-pn-product-l2-transform/evidence/results/` với tên file ghi ở từng bước. Mẫu kết quả tối đa 50 dòng. Không in dữ liệu cá nhân và không in giá trị giá.

## Điều kiện tiên quyết

1. Kiểm tra local đã PASS trên commit sẽ deploy:
   ```
   python -m pytest tests/test_slv_pn_product_l2_contract.py tests/test_legacy_gold_poi_init_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q
   python -m pytest -q
   python scripts/vv.py verify 20261127-slv-pn-product-l2-transform
   ```
   Kết quả: `<CẦN NGƯỜI DÙNG CUNG CẤP: kết quả ba lệnh trên commit deploy>`.
2. Specialist review (sql-data, spark-runtime, state-correctness) đã xong theo Main brief bước 6.
3. Có quyền chạy notebook trên Fabric DEV, đọc và ghi `lh_vv_silver`, đọc và ghi `lh_vv_ctrl`.
4. Cả 5 bảng L1 nguồn đã tồn tại. Cell `pnl2edgepy` sẽ dừng trước khi ghi nếu thiếu bảng nào.
5. Không có run GLD30 nào đang giữ khoá lúc chạy tay ở chế độ `RUN`. Node chạy tay ở `RUN` sẽ lấy khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` (hạn khoá chạy tay là 90 phút theo CTRL_TABLES_CONTEXT §4). Nếu khoá đang bận, node báo lỗi "chạy tay lúc này chỉ được p_mode = DRY_RUN".
6. Tham số của cả ba notebook node, lấy từ parameter cell. Giá trị mặc định giống hệt nhau ở `pnsaleparam`, `pnroomparam` và `pnrateparam`:

   | tham số | mặc định trong cell | giá trị cho chạy tay |
   |---|---|---|
   | `p_exec_id` | `""` | `""` (để trống, lib tự sinh uuid) |
   | `p_run_id` | `""` | `""` (bằng exec_id) |
   | `p_pl_name` | `""` | `""` |
   | `p_trg_fq` | `""` | `""` |
   | `p_pinned_json` | `""` | `""` |
   | `p_mode` | `"RUN"` | `"DRY_RUN"` hoặc `"RUN"` tuỳ bước |
   | `p_force` | `"false"` | `"false"` hoặc `"true"` tuỳ bước |
   | `p_history_limit` | `"1000"` | `"1000"` |

7. Cách truyền tham số khi chạy tay. Có hai cách:
   - Dùng một notebook tạm trên DEV và gọi `notebookutils.notebook.run("<tên notebook>", <timeout>, {...})`. Timeout: `<CẦN NGƯỜI DÙNG CUNG CẤP: timeout giây cho mỗi lần chạy node>`.
   - Mở notebook node, sửa giá trị `p_mode`/`p_force` ngay trong phiên rồi Run all. Không lưu thay đổi này vào notebook.

   Giá trị exit của node là JSON gồm `status`, `node`, `inserted`, `updated`, `deactivated`, `trg_version`.

## Baseline trước khi chạy

Mọi truy vấn trong mục này chỉ đọc. Lưu output vào `evidence/results/baseline.txt`.

B1. Chưa có cạnh nào cho ba bảng đích (kỳ vọng 0 dòng):
```sql
SELECT pl_name, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
LIMIT 50;
```

B2. Số cạnh hiện có của GLD30. Ghi lại thành `N_GLD30_BEFORE`:
```sql
SELECT COUNT(*) AS n FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M';
```

B3. Dòng khoá luồng:
```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```

B4. Kiểm tra bảng nào đã tồn tại (PySpark, chỉ đọc). Kỳ vọng: 5 L1 là `True`, 3 đích là `False`.
```python
for fq in ["lh_vv_silver.dbo.slv_pn_products", "lh_vv_silver.dbo.slv_pn_product_posts",
           "lh_vv_silver.dbo.slv_pn_product_variants", "lh_vv_silver.dbo.slv_pn_hotel_room_types",
           "lh_vv_silver.dbo.slv_pn_hotel_rate_plans", "lh_vv_silver.dbo.slv_pn_product_sale",
           "lh_vv_silver.dbo.slv_pn_hotel_room_offer", "lh_vv_silver.dbo.slv_pn_hotel_rate_offer"]:
    print(fq, spark.catalog.tableExists(fq))
```

B5. Đếm L1 theo `deleted` (chỉ đếm). Ghi lại `L1_TOTAL`, `L1_DEL_TRUE` và `L1_DEL_NULL` cho từng bảng.
- `L1_DEL_NULL > 0` thì QG `deleted_flag_null` sẽ chặn node. Đó là điểm dừng, phải hỏi người dùng.
- `slv_pn_product_posts` và `slv_pn_product_variants` cũng phải khác rỗng vì đều thuộc `required_inputs`.
```sql
SELECT 'slv_pn_products' AS t, COUNT(*) AS total, SUM(CASE WHEN deleted = true THEN 1 ELSE 0 END) AS del_true,
       SUM(CASE WHEN deleted IS NULL THEN 1 ELSE 0 END) AS del_null FROM lh_vv_silver.dbo.slv_pn_products
UNION ALL SELECT 'slv_pn_hotel_room_types', COUNT(*), SUM(CASE WHEN deleted = true THEN 1 ELSE 0 END),
       SUM(CASE WHEN deleted IS NULL THEN 1 ELSE 0 END) FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
UNION ALL SELECT 'slv_pn_hotel_rate_plans', COUNT(*), SUM(CASE WHEN deleted = true THEN 1 ELSE 0 END),
       SUM(CASE WHEN deleted IS NULL THEN 1 ELSE 0 END) FROM lh_vv_silver.dbo.slv_pn_hotel_rate_plans
UNION ALL SELECT 'slv_pn_product_posts', COUNT(*), NULL, NULL FROM lh_vv_silver.dbo.slv_pn_product_posts
UNION ALL SELECT 'slv_pn_product_variants', COUNT(*), NULL, NULL FROM lh_vv_silver.dbo.slv_pn_product_variants;
```

B6. Version hiện tại của 5 L1. Dùng để biết L1 có đổi giữa các lần chạy hay không (chạy cho từng bảng):
```sql
DESCRIBE HISTORY lh_vv_silver.dbo.slv_pn_products LIMIT 1;
```
Lặp lại với `slv_pn_product_posts`, `slv_pn_product_variants`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`. Chỉ ghi `version` và `timestamp`.

B7. Baseline I1: run gần nhất của GLD30 và ENR15, cùng kết quả từng node:
```sql
SELECT exec_id, pl_name, run_mode, status, started_at, tbl_total_count, tbl_success_count, tbl_failed_count
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_GLD_30M', 'PL_VV_TRANS_SLV_TO_ENR_15M') AND run_mode = 'RUN'
ORDER BY started_at DESC
LIMIT 10;
```
```sql
SELECT exec_id, pl_name, trg_tbl, status, inserted_rows, updated_rows, deactivated_rows, trg_version
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE exec_id IN ('<exec_id GLD30 gần nhất từ truy vấn trên>', '<exec_id ENR15 gần nhất từ truy vấn trên>')
ORDER BY pl_name, trg_tbl
LIMIT 50;
```

## Các bước thực hiện

### Bước 1 — Import lib, chưa import node

1. Import `NB_LIB_TRANSFORM_SLV_GLD` từ commit `<CẦN NGƯỜI DÙNG CUNG CẤP: commit SHA>`.
2. Chưa import `NB_SLV_PN_PRODUCT_SALE`, `NB_SLV_PN_HOTEL_ROOM_OFFER`, `NB_SLV_PN_HOTEL_RATE_OFFER` và chưa import `NB_CREATE_DDL` mới.
3. Không chạy `NB_00_ORCHES_SLV_TO_GLD` và `NB_00_ORCHES_SLV_TO_ENR` bằng tay.

### Bước 2 — R1: scratch MERGE self-test (chỉ ghi bảng tạm)

Dùng một notebook tạm trên DEV. Cell đầu tiên là `%run NB_LIB_TRANSFORM_SLV_GLD`; dán script dưới đây vào cell thứ hai.
- Script chỉ ghi `lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8>`. Nếu tên này đã tồn tại, script dừng.
- Cuối script chỉ DROP đúng bảng này.
- Dữ liệu là 10 khoá giả `k01`…`k10` với giá trị `a`/`b`, không có dữ liệu thật.

Lưu output vào `evidence/results/pnl2_selftest.txt`.

```python
# R1 — scratch MERGE self-test. Fabric DEV. Chỉ ghi và chỉ DROP lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8>.
import time, uuid

EXEC8 = uuid.uuid4().hex[:8]
FQ = f"lh_vv_silver.dbo.tmp_pnl2_selftest_{EXEC8}"
FLAG, PK, COLS = "_is_deleted", ("k",), ["k", "v"]
if spark.catalog.tableExists(FQ):
    raise RuntimeError(f"Dừng: {FQ} đã tồn tại, không ghi đè")
print("R1 table", FQ)
fails, created = [], False

def build_src(rows, with_flag=True):
    df = spark.createDataFrame(rows, "k string, v string, _is_deleted boolean")
    df = df.withColumn("row_hash", F.sha2(F.to_json(F.struct("k", "v")), 256))
    return df if with_flag else df.drop(FLAG)

def step(name, df, flag):
    diff = diff_counts(df, FQ, PK, flag)
    view = f"_v_r1_{EXEC8}_{name}"
    df.createOrReplaceTempView(view)
    try:
        spark.sql(sql_merge_target(FQ, view, COLS, PK, {}, None, flag))
    finally:
        spark.catalog.dropTempView(view)
    h = spark.sql(f"DESCRIBE HISTORY {FQ} LIMIT 1").first()
    m = {k: int(v) for k, v in h["operationMetrics"].items() if k.startswith("numTarget")}
    print(name, "version", h["version"], "op", h["operation"])
    print(name, "diff", diff)
    print(name, "operationMetrics", m)
    return diff, m

def check_metrics(name, diff, m):
    ins, upd, dea = diff["inserted"], diff["updated"], diff["deactivated"]
    if m.get("numTargetRowsInserted") != ins:
        fails.append(f"{name}: inserted {ins} != numTargetRowsInserted {m.get('numTargetRowsInserted')}")
    if "numTargetRowsMatchedUpdated" in m:
        if m["numTargetRowsMatchedUpdated"] != upd:
            fails.append(f"{name}: updated {upd} != numTargetRowsMatchedUpdated {m['numTargetRowsMatchedUpdated']}")
        if m.get("numTargetRowsNotMatchedBySourceUpdated") != dea:
            fails.append(f"{name}: deactivated {dea} != numTargetRowsNotMatchedBySourceUpdated "
                         f"{m.get('numTargetRowsNotMatchedBySourceUpdated')}")
    elif m.get("numTargetRowsUpdated") != upd + dea:
        fails.append(f"{name}: updated+deactivated {upd + dea} != numTargetRowsUpdated {m.get('numTargetRowsUpdated')}")
    if m.get("numTargetRowsDeleted", 0) != 0:
        fails.append(f"{name}: numTargetRowsDeleted {m.get('numTargetRowsDeleted')} != 0")

def expect_diff(name, diff, want):
    for key, val in want.items():
        if diff.get(key) != val:
            fails.append(f"{name}: diff {key} = {diff.get(key)}, cần {val}")

ROUND1 = [("k03", "a", False), ("k04", "a", False), ("k05", "a", False), ("k06", "a", True),
          ("k07", "a", True), ("k08", "a", True), ("k09", "a", False), ("k10", "a", True)]
ROUND2 = [("k01", "a", False), ("k02", "a", True), ("k03", "a", False), ("k04", "b", False),
          ("k05", "a", True), ("k06", "a", True), ("k07", "b", True), ("k08", "a", False)]
try:
    ensure_target(FQ, T.StructType([T.StructField("k", T.StringType()), T.StructField("v", T.StringType())]),
                  "r1_selftest")
    created = True
    # Vòng 1 (cờ bật): tạo trạng thái ban đầu live / deleted
    d1, m1 = step("flag_round1", build_src(ROUND1), FLAG)
    expect_diff("flag_round1", d1, {"inserted": 8, "insert_deleted": 4, "updated": 0, "deactivated": 0})
    check_metrics("flag_round1", d1, m1)
    time.sleep(3)
    # Vòng 2 (cờ bật): 10 chuyển trạng thái I4
    d2, m2 = step("flag_round2", build_src(ROUND2), FLAG)
    expect_diff("flag_round2", d2, {"inserted": 2, "insert_deleted": 1, "updated": 4, "deactivated": 1,
                                    "to_deleted": 1, "undeleted": 1, "deleted_changed": 1})
    check_metrics("flag_round2", d2, m2)
    snap = {r["k"]: r for r in spark.table(FQ).collect()}       # 10 dòng giả
    t1, t2 = snap["k03"]["created_at"], snap["k01"]["created_at"]
    if not (t1 and t2 and t2 > t1):
        fails.append(f"timestamp vòng: t1={t1} t2={t2}")
    want = {  # k: (v, deleted_at, updated_at)
        "k01": ("a", None, t2), "k02": ("a", t2, t2), "k03": ("a", None, t1), "k04": ("b", None, t2),
        "k05": ("a", t2, t2), "k06": ("a", t1, t1), "k07": ("b", t1, t2), "k08": ("a", None, t2),
        "k09": ("a", t2, t2), "k10": ("a", t1, t1),
    }
    for k, (v, dat, uat) in want.items():
        r = snap.get(k)
        got = None if r is None else (r["v"], r["deleted_at"], r["updated_at"])
        print("I4", k, "ok" if got == (v, dat, uat) else f"SAI got={got} want={(v, dat, uat)}")
        if got != (v, dat, uat):
            fails.append(f"I4 {k}")
    # Vòng 3 (deleted_flag=None): hành vi mặc định hôm nay, có mặt = sống
    d3, m3 = step("default_round3", build_src(ROUND2, with_flag=False), None)
    expect_diff("default_round3", d3, {"inserted": 0, "updated": 4, "deactivated": 0})
    check_metrics("default_round3", d3, m3)
    snap = {r["k"]: r for r in spark.table(FQ).collect()}
    for k in ("k01", "k02", "k03", "k04", "k05", "k06", "k07", "k08"):
        if snap[k]["deleted_at"] is not None:
            fails.append(f"default {k} deleted_at phải NULL")
    for k in ("k09", "k10"):
        if snap[k]["deleted_at"] is None:
            fails.append(f"default {k} deleted_at phải giữ")
finally:
    if created:
        spark.sql(f"DROP TABLE IF EXISTS {quote_name(FQ)}")
        print("dropped", FQ, "exists now", spark.catalog.tableExists(FQ))
print("R1", "PASS" if not fails else "FAIL", fails)
```

Bảng 10 chuyển trạng thái I4 mà script kiểm. `t1` là thời điểm commit vòng 1, `t2` là thời điểm commit vòng 2.

| khoá | t trước vòng 2 | s ở vòng 2 | kỳ vọng |
|---|---|---|---|
| k01 | absent | có, cờ false | insert, `deleted_at` NULL |
| k02 | absent | có, cờ true | insert, `deleted_at` = t2 |
| k03 | live | cờ false, hash giữ | không ghi (`updated_at` = t1) |
| k04 | live | cờ false, hash đổi | `v` = b, `updated_at` = t2 |
| k05 | live | cờ true | `deleted_at` = t2, `updated_at` = t2 |
| k06 | deleted | cờ true, hash giữ | không ghi, `deleted_at` = t1 |
| k07 | deleted | cờ true, hash đổi | `v` = b, `updated_at` = t2, `deleted_at` giữ t1 |
| k08 | deleted | cờ false | `deleted_at` NULL, `updated_at` = t2 |
| k09 | live | absent | `deleted_at` = t2, `v` giữ a |
| k10 | deleted | absent | không ghi |

Điều kiện PASS của R1:
- Dòng cuối in `R1 PASS []`.
- Mọi dòng `I4 kXX ok`.
- `diff_counts` khớp `operationMetrics` ở cả ba vòng, kể cả vòng `deleted_flag=None`.
- Dòng `dropped ... exists now False`.

Nếu R1 FAIL: dừng runbook. Không import node và không chạy NB_00. Làm theo "Rollback và forward recovery", nhánh trước bước 4.

### Bước 3 — Quan sát I1 với lib mới (chỉ sau khi R1 PASS)

1. Chờ một run lịch, hoặc chạy một lần NB_00 của `PL_VV_TRANS_SLV_TO_GLD_30M` và một lần của `PL_VV_TRANS_SLV_TO_ENR_15M`. Cách kích hoạt: `<CẦN NGƯỜI DÙNG CUNG CẤP: chờ trigger lịch hay chạy tay pipeline, và tham số NB_00 nếu chạy tay>`.
2. Chạy lại hai truy vấn B7 cho exec_id mới, lưu vào `evidence/results/i1_after_lib.txt`.
3. Kỳ vọng:
   - Danh sách node giống baseline.
   - Không có node mới bị `FAILED`.
   - Với node mà đầu vào không đổi, `inserted_rows`/`updated_rows`/`deactivated_rows` theo cùng mẫu như baseline.
   - `qg_json` của node cũ không có khoá `delete_flag`.

### Bước 4 — Import ba node và seed cạnh `pnl2edgepy`

1. Import `NB_SLV_PN_PRODUCT_SALE`, `NB_SLV_PN_HOTEL_ROOM_OFFER`, `NB_SLV_PN_HOTEL_RATE_OFFER` và `NB_CREATE_DDL` từ cùng commit.
2. Kiểm tra lại B3. Nếu `lock_exec_id` khác NULL và chưa quá hạn, chờ GLD30 nhả khoá.
3. Mở `NB_CREATE_DDL` và chỉ chạy cell `pnl2edgepy`. Không chạy các cell khác.
   - Cell giữ khoá `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` với `LEASE_MINUTES = 90`.
   - Cell dừng trước khi ghi nếu:
     - thiếu một trong 5 L1;
     - một bảng đích đã có nhưng thiếu `row_hash`/`deleted_at`;
     - một cạnh đang active ở pipeline khác;
     - một cạnh đã có nhưng không active đúng một dòng.
4. Kỳ vọng output:
   ```
   pnl2edge: ['slv_pn_hotel_rate_plans', 'slv_pn_hotel_room_types', 'slv_pn_product_posts', 'slv_pn_product_variants', 'slv_pn_products']
   ```
5. 5 cạnh được ghi với `pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`, `src_schema = trg_schema = lh_vv_silver.dbo`, `is_active = 1`, `priority = 1`, `load_mode = RECOMPUTE`:

   | src_tbl | trg_tbl | nb_name |
   |---|---|---|
   | `slv_pn_products` | `slv_pn_product_sale` | `NB_SLV_PN_PRODUCT_SALE` |
   | `slv_pn_product_posts` | `slv_pn_product_sale` | `NB_SLV_PN_PRODUCT_SALE` |
   | `slv_pn_product_variants` | `slv_pn_product_sale` | `NB_SLV_PN_PRODUCT_SALE` |
   | `slv_pn_hotel_room_types` | `slv_pn_hotel_room_offer` | `NB_SLV_PN_HOTEL_ROOM_OFFER` |
   | `slv_pn_hotel_rate_plans` | `slv_pn_hotel_rate_offer` | `NB_SLV_PN_HOTEL_RATE_OFFER` |

6. Chạy lại B1 (kỳ vọng đúng 5 dòng trên) và B2 (kỳ vọng `N_GLD30_BEFORE + 5`). Lưu vào `evidence/results/pnl2edge.txt`.
7. Từ lúc này, trigger GLD30 kế tiếp sẽ chạy ba node và tạo bảng. Architecture chấp nhận điều đó vì ba bảng chưa có reader.

### Bước 5 — DRY_RUN từng node, ngay sau khi seed

Chạy lần lượt từng node với `p_mode = "DRY_RUN"`, `p_force = "false"`, `p_history_limit = "1000"`; các tham số khác để `""`. Ví dụ với notebook tạm:
```python
P = {"p_exec_id": "", "p_run_id": "", "p_pl_name": "", "p_trg_fq": "", "p_pinned_json": "",
     "p_mode": "DRY_RUN", "p_force": "false", "p_history_limit": "1000"}
for nb in ("NB_SLV_PN_PRODUCT_SALE", "NB_SLV_PN_HOTEL_ROOM_OFFER", "NB_SLV_PN_HOTEL_RATE_OFFER"):
    print(nb, notebookutils.notebook.run(nb, <CẦN NGƯỜI DÙNG CUNG CẤP: timeout giây>, P))
```

Kỳ vọng (khi bảng đích chưa có):
- `status = SUCCESS` và `trg_version = null`.
- `inserted` = `L1_TOTAL` của bảng gốc (product sale tính theo `slv_pn_products`); `updated = 0`; `deactivated = 0`.
- DRY_RUN không tạo bảng: chạy lại B4 thì 3 đích vẫn `False`.

Nếu GLD30 đã kịp tạo bảng trước bước này, DRY_RUN vẫn hợp lệ và diff tính trên bảng đã có. Ghi lại điều đó vào kết quả.

Đọc QG và diff của mỗi node trong `ctrl_log_table_run` (truy vấn L1 ở mục "Kiểm tra log và watermark"). Kỳ vọng:
- `qg_json.blocks.deleted_flag_null = 0`.
- `qg_json.blocks.is_bookable_null = 0` (product sale, room offer).
- `qg_json.delete_flag.insert_deleted = L1_DEL_TRUE`.
- Ghi lại các warn: `post_match_none`, `post_match_many`, `price_decode_null` (product sale) và `room_status_null` (room offer).

Lưu vào `evidence/results/dry_run.txt`.

### Bước 6 — RUN lần đầu

Có hai cách:
- Để trigger GLD30 kế tiếp tạo bảng.
- Chạy tay từng node với `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`, các tham số khác `""`. Dùng dict `P` ở bước 5 với `"p_mode": "RUN"`.

Chạy tay cần khoá luồng trống (B3). Nếu khoá bận, chờ rồi chạy lại.

Kỳ vọng exit của lần đầu:
- `status = SUCCESS`.
- `inserted = L1_TOTAL`, `updated = 0`, `deactivated = 0`.
- `trg_version` là số (version đầu tiên sau CREATE + MERGE).

Lưu exit JSON vào `evidence/results/run1.txt`.

### Bước 7 — R2 (xem mục "Chạy lại để kiểm tra idempotency")

### Bước 8 — R3 (xem mục "Kiểm tra kết quả")

## Kiểm tra kết quả

Mọi truy vấn trong mục này chỉ đọc.

K1. Sau RUN lần đầu, ba bảng tồn tại và số dòng bằng `L1_TOTAL`:
```sql
SELECT 'slv_pn_product_sale' AS t, COUNT(*) AS n, SUM(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS n_deleted
FROM lh_vv_silver.dbo.slv_pn_product_sale
UNION ALL SELECT 'slv_pn_hotel_room_offer', COUNT(*), SUM(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_hotel_room_offer
UNION ALL SELECT 'slv_pn_hotel_rate_offer', COUNT(*), SUM(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_hotel_rate_offer;
```
Kỳ vọng: `n = L1_TOTAL` và `n_deleted = L1_DEL_TRUE`, nếu L1 không đổi từ B5.

K2. R3: dán nguyên nội dung `evidence/probes/pnl2_invariants.py` vào một notebook tạm và chạy. Probe chỉ đọc và chỉ in số đếm.
- Điều kiện chạy: version L1 hiện tại (B6) phải bằng `src_versions_json` của lần RUN gần nhất. Nếu L1 đã đổi, chạy lại node với `p_mode = "RUN"`, `p_force = "true"` rồi mới chạy probe.
- Lưu output vào `evidence/results/pnl2_invariants.txt`.
- Điều kiện PASS:
  - Mọi count bằng 0: `l1_missing_on_l2`, `deleted_at_set_but_l1_live`, `deleted_at_null_but_l1_deleted`, `updated_before_created`, `is_bookable_null` (product sale, room offer), `price_without_post` (product sale).
  - Mỗi bảng in `_is_deleted False`.
  - Danh sách cột in ra đúng như sau (theo model-design `## Columns`):
    - `slv_pn_product_sale`: `product_id, product_post_id, original_price, marketing_price, markup_percent, is_bookable, row_hash, created_at, updated_at, deleted_at`
    - `slv_pn_hotel_room_offer`: `room_type_id, status, available_rooms, max_occupancy, adult_capacity, child_capacity, view_type, deleted, is_bookable, row_hash, created_at, updated_at, deleted_at`
    - `slv_pn_hotel_rate_offer`: `rate_plan_id, status, meal_plan, valid_from, valid_to, row_hash, created_at, updated_at, deleted_at`

K3. `valid_from` và `valid_to` phải được chuyển 1-1 từ L1, so sánh null-safe và không gán đơn vị. Kỳ vọng `n = 0`:
```sql
SELECT COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_pn_hotel_rate_offer t
JOIN lh_vv_silver.dbo.slv_pn_hotel_rate_plans s ON s.id = t.rate_plan_id
WHERE NOT (t.valid_from <=> s.valid_from) OR NOT (t.valid_to <=> s.valid_to);
```

K4. Kiểu cột của bảng đích (chỉ in tên và kiểu, không in dữ liệu):
```sql
DESCRIBE TABLE lh_vv_silver.dbo.slv_pn_product_sale;
```
Lặp lại với `slv_pn_hotel_room_offer` và `slv_pn_hotel_rate_offer`. Kỳ vọng:
- Giá trong product sale là `double`, `is_bookable` là `boolean`.
- `valid_from`/`valid_to` là `timestamp`, `meal_plan` là `int`.

## Chạy lại để kiểm tra idempotency

R2: làm cho từng node sau RUN đầu tiên.

1. Ghi version hiện tại của bảng đích: `DESCRIBE HISTORY lh_vv_silver.dbo.<trg_tbl> LIMIT 1`. Ghi `version` là `V_BEFORE`.
2. Chạy node với `p_exec_id = ""`, `p_run_id = ""`, `p_pl_name = ""`, `p_trg_fq = ""`, `p_pinned_json = ""`, `p_mode = "RUN"`, `p_force = "true"`, `p_history_limit = "1000"`.
3. Kỳ vọng exit JSON:
   - `status = SUCCESS`, `inserted = 0`, `updated = 0`, `deactivated = 0`, `trg_version = V_BEFORE`.
   - Log node có dòng "Không có dòng đổi -> bỏ qua MERGE (không tạo commit)".
4. Chạy lại `DESCRIBE HISTORY lh_vv_silver.dbo.<trg_tbl> LIMIT 1`. `version` vẫn phải bằng `V_BEFORE`, tức không có commit mới.
5. Đối chiếu `src_versions_json` của hai lần chạy (truy vấn L1 ở mục sau). Nếu một L1 có `v` khác nhau, R2 chưa kết luận được; chạy lại bước 2 thêm một lần.
6. `qg_json.delete_flag` phải có `insert_deleted = to_deleted = undeleted = deleted_changed = 0`.

Idempotency của cell `pnl2edgepy` (tuỳ chọn):
1. Chạy lại cell. Kỳ vọng in cùng dòng `pnl2edge: [...]`.
2. B1 vẫn ra đúng 5 dòng và B2 vẫn là `N_GLD30_BEFORE + 5`.
3. `DESCRIBE HISTORY lh_vv_ctrl.dbo.ctrl_mng_pipeline_config LIMIT 1` có `operation = MERGE` và `numTargetRowsInserted = 0`.

Lưu vào `evidence/results/r2_idempotency.txt`.

## Kiểm tra log và watermark

Mọi truy vấn trong mục này chỉ đọc.

L1. Log node của ba bảng (mỗi lần chạy tay ghi 1 dòng, kể cả DRY_RUN và FAILED):
```sql
SELECT exec_id, pl_name, trg_tbl, status, entity_rows, inserted_rows, updated_rows, deactivated_rows,
       trg_version, started_at, error_message, src_versions_json, qg_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
ORDER BY started_at DESC
LIMIT 50;
```
Kỳ vọng:
- `pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`.
- `qg_json` có `mode`, `force`, `inbox`, `rows`, `blocks` (gồm `deleted_flag_null`), `warns`, `metrics` và `delete_flag`.
- `entity_rows = L1_TOTAL`.

L2. Khoá luồng sau mỗi lần chạy tay ở `RUN`: `lock_exec_id` và `lock_at` phải về NULL, `status` là trạng thái của run vừa xong.
```sql
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M';
```
Sau cell `pnl2edgepy`, dòng này có `status = SUCCESS` (hoặc `FAILED` kèm `error_message`) và `lock_exec_id = NULL`.

L3. Watermark cạnh. Chỉ NB_00 ghi các dòng này, chạy tay không tiến cạnh. Trước run GLD30 đầu tiên sau seed, 5 dòng chưa tồn tại. Sau run đó, mỗi dòng có `status = SUCCESS`, `last_src_version` và `last_src_table_id`.
```sql
SELECT watermark_id, status, last_src_version, last_src_table_id, watermark_value, last_success_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
  'wm_e__slv_pn_product_sale__slv_pn_products',
  'wm_e__slv_pn_product_sale__slv_pn_product_posts',
  'wm_e__slv_pn_product_sale__slv_pn_product_variants',
  'wm_e__slv_pn_hotel_room_offer__slv_pn_hotel_room_types',
  'wm_e__slv_pn_hotel_rate_offer__slv_pn_hotel_rate_plans');
```

L4. Run GLD30 đầu tiên sau R2. Nếu L1 không đổi, ba node trong exec đó phải có `inserted_rows = updated_rows = deactivated_rows = 0` và `trg_version` không đổi (lý do: cạnh mới coi là bẩn, node tính lại, diff bằng 0 nên không commit).
- Dùng truy vấn B7 với exec_id mới.
- `ctrl_log_run.status` của exec đó không được là `FAILED`/`PARTIAL_FAILED` do ba node này.

Lưu vào `evidence/results/logs_watermark.txt`.

## Rollback và forward recovery

Mọi lệnh ghi trong mục này chỉ chạy khi người dùng quyết định rollback hoặc sửa. Trước mỗi lệnh ghi, kiểm tra L2: khoá luồng phải trống.

Trước bước 4 (chưa seed cạnh, gồm trường hợp R1 FAIL):
- Revert commit lib và re-import `NB_LIB_TRANSFORM_SLV_GLD` bản trước. Commit cần re-import: `<CẦN NGƯỜI DÙNG CUNG CẤP: commit SHA lib trước khi deploy>`.
- Node cũ chưa từng đi vào nhánh cờ nên không cần dọn dữ liệu.
- Nếu R1 dừng giữa chừng, script đã DROP bảng tạm trong `finally`. Kiểm tra lại `spark.catalog.tableExists("lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8 in ra ở R1>")`, kỳ vọng `False`. Chỉ khi vẫn còn, chạy `DROP TABLE IF EXISTS lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8 in ra ở R1>` với đúng tên đó.

Sau bước 4 (đã seed cạnh):
1. Tắt đúng 5 cạnh, chỉ cập nhật dòng còn `is_active = 1`:
   ```sql
   UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
   SET is_active = 0
   WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M'
     AND src_schema = 'lh_vv_silver.dbo' AND trg_schema = 'lh_vv_silver.dbo'
     AND ((src_tbl IN ('slv_pn_products', 'slv_pn_product_posts', 'slv_pn_product_variants') AND trg_tbl = 'slv_pn_product_sale')
       OR (src_tbl = 'slv_pn_hotel_room_types' AND trg_tbl = 'slv_pn_hotel_room_offer')
       OR (src_tbl = 'slv_pn_hotel_rate_plans' AND trg_tbl = 'slv_pn_hotel_rate_offer'))
     AND is_active = 1;
   ```
   Kỳ vọng `num_affected_rows = 5`, hoặc ít hơn nếu đã tắt một phần. Sau đó chạy B1: cả 5 dòng có `is_active = 0`.
2. Revert ba notebook node, tức gỡ hoặc re-import bản trước: `<CẦN NGƯỜI DÙNG CUNG CẤP: cách gỡ notebook node trên DEV>`.
3. Ba bảng L2 giữ nguyên: không có reader và không DROP. Các dòng watermark cạnh `wm_e__...` vô hại nên không xoá.

Forward fix (build sai):
- Sửa build, deploy notebook node, rồi chạy node với `p_mode = "RUN"`, `p_force = "true"`, `p_history_limit = "1000"`, các tham số khác `""`.
- MERGE hội tụ về giá trị nghiệp vụ đúng. Dòng bị gắn cờ sai sẽ được bỏ xoá qua nhánh `deleted_at → NULL`.
- Sau đó chạy lại R2 và R3.

Xoá timestamp `deleted_at` first-seen sai (chỉ DEV, chỉ một bảng L2):
- Thao tác này phá huỷ dữ liệu: mất lịch sử `created_at` của bảng đó (không ai dùng). Cần người dùng xác nhận tên bảng: `<CẦN NGƯỜI DÙNG CUNG CẤP: tên một bảng L2 cần dựng lại>`.
1. Kiểm tra L2: khoá trống.
2. `DROP TABLE lh_vv_silver.dbo.<tên bảng đã xác nhận>;`
3. Xoá các dòng `wm_e__` của đúng bảng đó. Không xoá dòng `wm_flow__`. Ví dụ với `slv_pn_product_sale`:
   ```sql
   DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
   WHERE watermark_id IN ('wm_e__slv_pn_product_sale__slv_pn_products',
                          'wm_e__slv_pn_product_sale__slv_pn_product_posts',
                          'wm_e__slv_pn_product_sale__slv_pn_product_variants');
   ```
   Với `slv_pn_hotel_room_offer`: chỉ `'wm_e__slv_pn_hotel_room_offer__slv_pn_hotel_room_types'`. Với `slv_pn_hotel_rate_offer`: chỉ `'wm_e__slv_pn_hotel_rate_offer__slv_pn_hotel_rate_plans'`.
4. Chạy node với `p_mode = "RUN"`, `p_force = "false"`, `p_history_limit = "1000"`. Bảng chưa có nên node tự tạo lại.
5. Chạy lại R2 và R3 cho bảng đó.

## Kết quả người dùng ghi nhận

Người dùng điền phần này sau khi chạy trên Fabric DEV. Đính kèm file trong `evidence/results/`.

| hạng mục | kỳ vọng | kết quả thực tế | file |
|---|---|---|---|
| Commit deploy | — | `<CẦN NGƯỜI DÙNG CUNG CẤP>` | — |
| Baseline B1–B7 | B1 0 dòng lúc đầu; 3 đích chưa có; `del_null = 0` | B1 lúc đầu 0 dòng. Sau seed: 5 cạnh active. `N_GLD30` 17 rồi 22. `del_null = 0`. B6 history lỗi cú pháp, không chặn R1 | `baseline.txt` |
| R1 scratch self-test | `R1 PASS []`, 10 dòng `I4 ok`, diff khớp `operationMetrics` ở 3 vòng, bảng tạm đã DROP | `R1 PASS []`. `tmp_pnl2_selftest_fb47ce23` đã DROP, `exists now False` | `pnl2_selftest.txt` |
| I1 sau import lib | node cũ không đổi trạng thái, không có `delete_flag` | Chưa chạy | `i1_after_lib.txt` |
| `pnl2edgepy` | in `pnl2edge: [...]`, 5 cạnh active, `N_GLD30_BEFORE + 5` | Đủ 5 cạnh, `nb_name` đúng, `is_active = 1`. Count 22 = 17 + 5 | `pnl2edge.txt` |
| DRY_RUN 3 node | SUCCESS, `inserted = L1_TOTAL`, blocks 0, không tạo bảng | 41, 423, 229. `trg_version` null. `updated = deactivated = 0` | `run1.txt` |
| RUN lần đầu | SUCCESS, `inserted = L1_TOTAL`, `n_deleted = L1_DEL_TRUE` | 41, 423, 229. Version 1. `L1_DEL_TRUE = 0` | `run1.txt` |
| R2 rerun `p_force = true` | 0/0/0, `trg_version` = `V_BEFORE`, không commit mới | 0/0/0 cả ba. Version 1 giữ 1 | `r2_r3.txt` |
| R3 probe | mọi count 0, `_is_deleted False`, cột đúng model-design | Mọi count 0. `_is_deleted False`. Cột đúng thứ tự Field Mapping cộng 4 cột kỹ thuật | `r2_r3.txt` |
| K3 `valid_from`/`valid_to` | `n = 0` | `valid_from_valid_to_mismatch 0` | `r2_r3.txt` |
| Log và watermark | khoá nhả; 5 `wm_e__` SUCCESS sau GLD30; GLD30 đầu tiên 0/0/0 | Khoá nhả, `lock_exec_id` NULL. `wm_e__` chưa có vì chưa có run GLD30 sau seed | `logs_watermark.txt` |
| Warn product sale / room offer | ghi số `post_match_none`, `post_match_many`, `price_decode_null`, `room_status_null` | Cả bốn warn bằng 0. `deleted_flag_null`, `is_bookable_null`, `pk_null`, `pk_duplicate` bằng 0 | `r2_r3.txt` |
| Quyết định | PASS → giữ; FAIL → nhánh rollback đã chọn | `<CẦN NGƯỜI DÙNG CUNG CẤP>` | — |
