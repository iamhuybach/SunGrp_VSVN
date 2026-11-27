# Fabric DEV. Lakehouse lh_vv_silver phải được gắn vào notebook này.
# Cell ngay phía trên phải là đúng một dòng: %run NB_LIB_TRANSFORM_SLV_GLD
# Ba notebook node phải đã import cùng commit với lib: NB_SLV_PN_PRODUCT_SALE,
# NB_SLV_PN_HOTEL_ROOM_OFFER, NB_SLV_PN_HOTEL_RATE_OFFER.
# NOTEBOOK_TIMEOUT_SEC = 240 phút, trần p_node_timeout_min của lib.
# In ra console. Không in giá. Gửi nguyên output cho agent.
# Nếu L1 có deleted IS NULL, script dừng trước R1.

# Parser Spark 3 từ chối timestamp năm 58774 trên log L1. Đặt trước mọi truy vấn của cell này.
spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
print("timeParserPolicy", spark.conf.get("spark.sql.legacy.timeParserPolicy"))

NOTEBOOK_TIMEOUT_SEC = 240 * 60
NODES = ("NB_SLV_PN_PRODUCT_SALE", "NB_SLV_PN_HOTEL_ROOM_OFFER", "NB_SLV_PN_HOTEL_RATE_OFFER")
TARGETS = ("slv_pn_product_sale", "slv_pn_hotel_room_offer", "slv_pn_hotel_rate_offer")
L1 = ("slv_pn_products", "slv_pn_product_posts", "slv_pn_product_variants",
      "slv_pn_hotel_room_types", "slv_pn_hotel_rate_plans")


def show(title, sql):
    print("\n==", title)
    spark.sql(sql).show(50, truncate=False)


def history_version(fq):
    """Đọc version Delta. DESCRIBE HISTORY không bọc trong SELECT."""
    previous = spark.conf.get("spark.sql.legacy.timeParserPolicy", "EXCEPTION")
    spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
    try:
        row = spark.sql(f"DESCRIBE HISTORY {fq} LIMIT 1").select("version", "operation").first()
        return None if row is None else int(row["version"]), None if row is None else row["operation"]
    except Exception as exc:
        print(fq, "history FAIL", type(exc).__name__, str(exc)[:300])
        return None, None
    finally:
        spark.conf.set("spark.sql.legacy.timeParserPolicy", previous)


def run_nb(nb, args):
    payload = dict(args)
    payload["useRootDefaultLakehouse"] = True
    try:
        print(nb, notebookutils.notebook.run(nb, NOTEBOOK_TIMEOUT_SEC, payload))
    except Exception as exc:
        print(nb, "FAIL", type(exc).__name__, str(exc)[:500])


print("\n== B1 edges")
show("B1", """
SELECT pl_name, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
LIMIT 50
""")
show("B2", """
SELECT COUNT(*) AS n FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M'
""")
show("B3 lock", """
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'
""")
print("\n== B4 exists")
for name in L1 + TARGETS:
    print("lh_vv_silver.dbo." + name, spark.catalog.tableExists("lh_vv_silver.dbo." + name))
show("B5 counts", """
SELECT 'slv_pn_products' AS t, COUNT(*) AS total,
       SUM(CASE WHEN deleted = true THEN 1 ELSE 0 END) AS del_true,
       SUM(CASE WHEN deleted IS NULL THEN 1 ELSE 0 END) AS del_null
FROM lh_vv_silver.dbo.slv_pn_products
UNION ALL SELECT 'slv_pn_hotel_room_types', COUNT(*),
       SUM(CASE WHEN deleted = true THEN 1 ELSE 0 END),
       SUM(CASE WHEN deleted IS NULL THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_hotel_room_types
UNION ALL SELECT 'slv_pn_hotel_rate_plans', COUNT(*),
       SUM(CASE WHEN deleted = true THEN 1 ELSE 0 END),
       SUM(CASE WHEN deleted IS NULL THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_hotel_rate_plans
UNION ALL SELECT 'slv_pn_product_posts', COUNT(*), NULL, NULL
FROM lh_vv_silver.dbo.slv_pn_product_posts
UNION ALL SELECT 'slv_pn_product_variants', COUNT(*), NULL, NULL
FROM lh_vv_silver.dbo.slv_pn_product_variants
""")
print("del_null trên ba bảng gốc ở B5 là 0. Không quét timestamp L1 thêm một lần nữa.")
print("\n== B6 history")
try:
    for name in L1:
        version, operation = history_version("lh_vv_silver.dbo." + name)
        print(name, "version", version, "operation", operation)
except Exception as exc:
    print("B6 FAIL", type(exc).__name__, str(exc)[:300])
show("B7 runs", """
SELECT exec_id, pl_name, run_mode, status, started_at, tbl_total_count, tbl_success_count, tbl_failed_count
FROM lh_vv_ctrl.dbo.ctrl_log_run
WHERE pl_name IN ('PL_VV_TRANS_SLV_TO_GLD_30M', 'PL_VV_TRANS_SLV_TO_ENR_15M') AND run_mode = 'RUN'
ORDER BY started_at DESC
LIMIT 10
""")

print('\n== R1')

# R1 — scratch MERGE self-test. Chỉ ghi và chỉ DROP lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8>.
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
            fails.append(
                f"{name}: deactivated {dea} != numTargetRowsNotMatchedBySourceUpdated "
                f"{m.get('numTargetRowsNotMatchedBySourceUpdated')}"
            )
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
    d1, m1 = step("flag_round1", build_src(ROUND1), FLAG)
    expect_diff("flag_round1", d1, {"inserted": 8, "insert_deleted": 4, "updated": 0, "deactivated": 0})
    check_metrics("flag_round1", d1, m1)
    time.sleep(3)
    d2, m2 = step("flag_round2", build_src(ROUND2), FLAG)
    expect_diff("flag_round2", d2, {"inserted": 2, "insert_deleted": 1, "updated": 4, "deactivated": 1,
                                    "to_deleted": 1, "undeleted": 1, "deleted_changed": 1})
    check_metrics("flag_round2", d2, m2)
    snap = {r["k"]: r for r in spark.table(FQ).collect()}
    t1, t2 = snap["k03"]["created_at"], snap["k01"]["created_at"]
    if not (t1 and t2 and t2 > t1):
        fails.append(f"timestamp vòng: t1={t1} t2={t2}")
    want = {
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
if fails:
    raise RuntimeError("R1 FAIL, dừng trước seed và trước node: " + "; ".join(fails))


print("\n== seed pnl2edgepy")

# [THÊM 27/11] 20261127-slv-pn-product-l2-transform
# Thêm 5 cạnh RECOMPUTE của PL_VV_TRANS_SLV_TO_GLD_30M. Không DDL. Chạy lại không thêm dòng.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
SLV = "lh_vv_silver.dbo"
LEASE_MINUTES = 90
L1_SOURCES = [
    "lh_vv_silver.dbo.slv_pn_products",
    "lh_vv_silver.dbo.slv_pn_product_posts",
    "lh_vv_silver.dbo.slv_pn_product_variants",
    "lh_vv_silver.dbo.slv_pn_hotel_room_types",
    "lh_vv_silver.dbo.slv_pn_hotel_rate_plans",
]
TARGETS = (
    "slv_pn_product_sale",
    "slv_pn_hotel_room_offer",
    "slv_pn_hotel_rate_offer",
)
EDGES_ON = [
    (1, "slv_pn_products", "lh_vv_silver.dbo", "slv_pn_product_sale", "RECOMPUTE", "NB_SLV_PN_PRODUCT_SALE", 1),
    (2, "slv_pn_product_posts", "lh_vv_silver.dbo", "slv_pn_product_sale", "RECOMPUTE", "NB_SLV_PN_PRODUCT_SALE", 1),
    (3, "slv_pn_product_variants", "lh_vv_silver.dbo", "slv_pn_product_sale", "RECOMPUTE", "NB_SLV_PN_PRODUCT_SALE", 1),
    (4, "slv_pn_hotel_room_types", "lh_vv_silver.dbo", "slv_pn_hotel_room_offer", "RECOMPUTE", "NB_SLV_PN_HOTEL_ROOM_OFFER", 1),
    (5, "slv_pn_hotel_rate_plans", "lh_vv_silver.dbo", "slv_pn_hotel_rate_offer", "RECOMPUTE", "NB_SLV_PN_HOTEL_RATE_OFFER", 1),
]
LOCK = "pnl2edge-" + uuid.uuid4().hex


def _target_edges():
    names = ", ".join("'" + name + "'" for name in TARGETS)
    return list(spark.sql(f"""
    SELECT pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
    FROM {CFG}
    WHERE trg_schema = '{SLV}' AND trg_tbl IN ({names})
    GROUP BY pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name
    """).collect())


spark.sql(f"""
INSERT INTO {WM}
    (watermark_id, src_schema, src_tbl, trg_schema, trg_tbl, watermark_column, watermark_value, last_success_at,
     status, flow_name, watermark_sequence, last_run_id, last_src_version, last_src_table_id, error_message,
     lock_exec_id, lock_at, updated_at)
SELECT '{WID}', CAST(NULL AS STRING), '{PL}', CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS STRING),
       CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP), 'INITIALIZED', 'NB_CREATE_DDL', CAST(NULL AS BIGINT),
       CAST(NULL AS STRING), CAST(NULL AS BIGINT), CAST(NULL AS STRING), CAST(NULL AS STRING),
       CAST(NULL AS STRING), CAST(NULL AS TIMESTAMP), current_timestamp()
WHERE NOT EXISTS (SELECT 1 FROM {WM} WHERE watermark_id = '{WID}')
""")
held = False
failed = None
try:
    spark.sql(f"""
    UPDATE {WM}
    SET lock_exec_id = '{LOCK}', lock_at = current_timestamp(), status = 'RUNNING', updated_at = current_timestamp()
    WHERE watermark_id = '{WID}' AND (
        lock_exec_id IS NULL
        OR coalesce(lock_at < current_timestamp() - INTERVAL {LEASE_MINUTES} MINUTES, true))
    """)
    owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
    if not owner or owner["lock_exec_id"] != LOCK:
        other = None if owner is None else owner["lock_exec_id"]
        raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")
    held = True

    # Dừng trước khi ghi: thiếu L1, đích không do lib ghi, hoặc cạnh không đúng một dòng active.
    issues = []
    for fq in L1_SOURCES:
        if not spark.catalog.tableExists(fq):
            issues.append(f"thiếu nguồn {fq}")
    for name in TARGETS:
        fq = f"{SLV}.{name}"
        if spark.catalog.tableExists(fq):
            cols = {field.name.lower() for field in spark.table(fq).schema.fields}
            if "row_hash" not in cols or "deleted_at" not in cols:
                issues.append(f"{fq} đã có nhưng không do lib này ghi")
    rows = _target_edges()
    for row in rows:
        if row["pl_name"] != PL and row["is_active"] == 1:
            issues.append(f"cạnh {row['src_tbl']}->{row['trg_tbl']} đang active ở {row['pl_name']}")
    for seq, src, schema, trg, mode, nb, priority in EDGES_ON:
        found = [row for row in rows if row["pl_name"] == PL and row["src_tbl"] == src and row["trg_tbl"] == trg]
        if not found:
            continue
        active = [row for row in found if row["is_active"] == 1 and row["n"] == 1]
        payload_ok = len(found) == 1 and len(active) == 1 and active[0]["src_schema"] == SLV and active[0]["trg_schema"] == schema and active[0]["priority"] == priority and active[0]["load_mode"] == mode and active[0]["nb_name"] == nb
        if not payload_ok:
            issues.append(f"cạnh {src}->{trg} đã có nhưng không active đúng một dòng")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    def _refresh_lock():
        spark.sql(f"""
        UPDATE {WM}
        SET lock_at = current_timestamp(), updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
        owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
        if not owner or owner["lock_exec_id"] != LOCK:
            raise RuntimeError(f"Luồng {PL} mất khoá trước khi ghi")


    values = ",\n        ".join(
        f"({seq}, '{src}', '{schema}', '{trg}', '{mode}', '{nb}', {priority})"
        for seq, src, schema, trg, mode, nb, priority in EDGES_ON
    )
    _refresh_lock()
    spark.sql(f"""
    MERGE INTO {CFG} AS t
    USING (
        SELECT COALESCE((SELECT MAX(id) FROM {CFG}), 0) + seq AS id,
               '{PL}' AS pl_name, '{SLV}' AS src_schema, src_tbl, trg_schema, trg_tbl,
               1 AS is_active, priority, load_mode, nb_name
        FROM VALUES
            {values}
        AS v(seq, src_tbl, trg_schema, trg_tbl, load_mode, nb_name, priority)
    ) AS s
    ON t.pl_name = s.pl_name AND t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
       AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
    WHEN NOT MATCHED THEN INSERT
        (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)
    VALUES
        (s.id, s.pl_name, s.src_schema, s.src_tbl, s.trg_schema, s.trg_tbl, s.is_active, s.priority,
         s.load_mode, CAST(NULL AS STRING), CAST(NULL AS STRING), s.nb_name)
    """)

    # Sau khi ghi: đúng 5 cạnh active của pipeline này.
    problems = []
    active = [row for row in _target_edges() if row["is_active"] == 1]
    want = {(PL, SLV, src, schema, trg, priority, mode, nb) for _seq, src, schema, trg, mode, nb, priority in EDGES_ON}
    got = {
        (row["pl_name"], row["src_schema"], row["src_tbl"], row["trg_schema"], row["trg_tbl"], row["priority"], row["load_mode"], row["nb_name"])
        for row in active if row["n"] == 1
    }
    if got != want or len(active) != len(want):
        problems.append(f"cạnh active là {got}, cần {want}")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"pnl2edge: {sorted(src for _seq, src, *_rest in EDGES_ON)}")
except Exception as exc:
    failed = exc
    raise
finally:
    if held:
        status = "FAILED" if failed else "SUCCESS"
        detail = "" if failed is None else str(failed).replace("'", " ")[:500]
        try:
            spark.sql(f"""
            UPDATE {WM}
            SET lock_exec_id = NULL, lock_at = NULL, status = '{status}', error_message = '{detail}',
                updated_at = current_timestamp()
            WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
            """)
        except Exception as cleanup_exc:
            if failed is None:
                raise
            raise failed from cleanup_exc


print("\n== DRY_RUN")
dry = {"p_exec_id": "", "p_run_id": "", "p_pl_name": "", "p_trg_fq": "", "p_pinned_json": "",
       "p_mode": "DRY_RUN", "p_force": "false", "p_history_limit": "1000"}
for nb in NODES:
    run_nb(nb, dry)
print("\n== after DRY_RUN exists")
for name in TARGETS:
    print("lh_vv_silver.dbo." + name, spark.catalog.tableExists("lh_vv_silver.dbo." + name))

print("\n== RUN")
run = dict(dry)
run["p_mode"] = "RUN"
for nb in NODES:
    run_nb(nb, run)

print("\n== after RUN exists")
missing = [name for name in TARGETS if not spark.catalog.tableExists("lh_vv_silver.dbo." + name)]
for name in TARGETS:
    print(name, name not in missing)
print("\n== L1 node log ngay sau RUN")
show("L1", """
SELECT trg_tbl, status, started_at, inserted_rows, updated_rows, deactivated_rows,
       error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
ORDER BY started_at DESC
LIMIT 20
""")

if missing:
    print("K1/R2/R3 bỏ qua. RUN chưa tạo:", missing)
else:
    print("\n== K1 after RUN")
    show("K1", """
SELECT 'slv_pn_product_sale' AS t, COUNT(*) AS n,
       SUM(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END) AS n_deleted
FROM lh_vv_silver.dbo.slv_pn_product_sale
UNION ALL SELECT 'slv_pn_hotel_room_offer', COUNT(*),
       SUM(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_hotel_room_offer
UNION ALL SELECT 'slv_pn_hotel_rate_offer', COUNT(*),
       SUM(CASE WHEN deleted_at IS NOT NULL THEN 1 ELSE 0 END)
FROM lh_vv_silver.dbo.slv_pn_hotel_rate_offer
""")

print("\n== R2")
if missing:
    print("R2 bỏ qua")
else:
    before = {}
    for name in TARGETS:
        version, _operation = history_version("lh_vv_silver.dbo." + name)
        before[name] = version
        print(name, "V_BEFORE", version)
    rerun = dict(run)
    rerun["p_force"] = "true"
    for nb, name in zip(NODES, TARGETS):
        run_nb(nb, rerun)
        version, _operation = history_version("lh_vv_silver.dbo." + name)
        same = version is not None and version == before[name]
        print(name, "V_AFTER", version, "same" if same else "CHANGED")

print("\n== R3")


TABLES = {
    "slv_pn_product_sale": ("product_id", "slv_pn_products", ("product_post_id", "original_price", "marketing_price", "markup_percent")),
    "slv_pn_hotel_room_offer": ("room_type_id", "slv_pn_hotel_room_types", ()),
    "slv_pn_hotel_rate_offer": ("rate_plan_id", "slv_pn_hotel_rate_plans", ()),
}
SLV = "lh_vv_silver.dbo"

for target, (key, source, prices) in TABLES.items():
    fq, src = f"{SLV}.{target}", f"{SLV}.{source}"
    if not spark.catalog.tableExists(fq):
        print(target, "skip R3, bảng chưa có")
        continue
    cols = [field.name for field in spark.table(fq).schema.fields]
    print(target, "columns", cols)
    print(target, "_is_deleted", "_is_deleted" in cols)
    checks = {
        "l1_missing_on_l2": f"""
            SELECT COUNT(*) AS n FROM {src} s
            LEFT ANTI JOIN {fq} t ON s.id = t.{key}
        """,
        "deleted_at_set_but_l1_live": f"""
            SELECT COUNT(*) AS n FROM {fq} t
            JOIN {src} s ON s.id = t.{key}
            WHERE t.deleted_at IS NOT NULL AND s.deleted = false
        """,
        "deleted_at_null_but_l1_deleted": f"""
            SELECT COUNT(*) AS n FROM {fq} t
            JOIN {src} s ON s.id = t.{key}
            WHERE t.deleted_at IS NULL AND s.deleted = true
        """,
        "is_bookable_null": f"SELECT COUNT(*) AS n FROM {fq} WHERE is_bookable IS NULL"
        if target != "slv_pn_hotel_rate_offer" else None,
        "updated_before_created": f"SELECT COUNT(*) AS n FROM {fq} WHERE updated_at < created_at",
    }
    if prices:
        pred = " OR ".join(f"{col} IS NOT NULL" for col in prices)
        checks["price_without_post"] = f"SELECT COUNT(*) AS n FROM {fq} WHERE product_post_id IS NULL AND ({pred})"
    for name, sql in checks.items():
        if sql is None:
            continue
        print(target, name, spark.sql(sql).first()["n"])

print("\n== K3 valid_from valid_to")
if missing:
    print("K3 bỏ qua")
else:
    try:
        show("K3", """
SELECT COUNT(*) AS n
FROM lh_vv_silver.dbo.slv_pn_hotel_rate_offer t
JOIN lh_vv_silver.dbo.slv_pn_hotel_rate_plans s ON s.id = t.rate_plan_id
WHERE NOT (t.valid_from <=> s.valid_from) OR NOT (t.valid_to <=> s.valid_to)
""")
    except Exception as exc:
        print("K3 FAIL", type(exc).__name__, str(exc)[:300])
print("\n== K4 describe")
if missing:
    print("K4 bỏ qua")
else:
    for name in TARGETS:
        print("--", name)
        spark.sql(f"DESCRIBE TABLE lh_vv_silver.dbo.{name}").show(50, truncate=False)
print("\n== L1 node log")
show("L1", """
SELECT exec_id, pl_name, trg_tbl, status, entity_rows, inserted_rows, updated_rows, deactivated_rows,
       trg_version, started_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
ORDER BY started_at DESC
LIMIT 50
""")
show("L1 qg", """
SELECT trg_tbl, status, started_at, qg_json
FROM lh_vv_ctrl.dbo.ctrl_log_table_run
WHERE trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
ORDER BY started_at DESC
LIMIT 9
""")
show("L2 lock", """
SELECT watermark_id, status, lock_exec_id, lock_at, last_run_id, error_message, updated_at
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'
""")
show("L3 edge wm", """
SELECT watermark_id, status, last_src_version, last_src_table_id, watermark_value, last_success_at, error_message
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
  'wm_e__slv_pn_product_sale__slv_pn_products',
  'wm_e__slv_pn_product_sale__slv_pn_product_posts',
  'wm_e__slv_pn_product_sale__slv_pn_product_variants',
  'wm_e__slv_pn_hotel_room_offer__slv_pn_hotel_room_types',
  'wm_e__slv_pn_hotel_rate_offer__slv_pn_hotel_rate_plans')
""")
show("B1 after", """
SELECT pl_name, src_tbl, trg_tbl, is_active, priority, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_schema = 'lh_vv_silver.dbo'
  AND trg_tbl IN ('slv_pn_product_sale', 'slv_pn_hotel_room_offer', 'slv_pn_hotel_rate_offer')
LIMIT 50
""")
show("B2 after", """
SELECT COUNT(*) AS n FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M'
""")
print("\n== DONE")
print("I1 và L4 chưa nằm trong script: chờ một lần GLD30 và một lần ENR15, rồi gửi thêm output B7 và L3.")
