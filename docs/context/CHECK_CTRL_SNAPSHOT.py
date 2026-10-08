# =============================================================================
# CHECK_CTRL_SNAPSHOT — chụp dữ liệu hiện có của 7 bảng ctrl (lh_vv_ctrl.dbo). CHỈ ĐỌC, không ghi gì.
# Dùng để cập nhật mục "Dữ liệu hiện có" của CTRL_TABLES_CONTEXT.md.
#   S0  Môi trường + version / số file / dung lượng / property của 7 bảng
#   S1  Cột thực tế của 7 bảng so với DDL tài liệu (thiếu / thừa)
#   S2  ctrl_mng_pipeline_config: tóm tắt theo (pl_name, src_tbl, load_mode) + liệt kê cạnh RECOMPUTE + dòng 3P
#   S3  ctrl_mng_watermark: dòng nguồn + dòng khoá (đủ cột), dòng cạnh (gọn) + đếm theo trạng thái
#   S4  ctrl_cfg_schema_registry: theo bảng (số cột, bật, khoá, TOAST, rule khác NONE)
#   S5  ctrl_log_run: 15 run gần nhất mỗi (pl_name, nguồn)
#   S6  ctrl_log_table_run: dòng của run gần nhất mỗi (pl_name, nguồn)
#   S7  ctrl_cdc_state: số dòng theo (src_tbl, trg_tbl) + kiểm tra trùng khoá (kỳ vọng 0)
#   S8  ctrl_cdc_reject: theo (src_tbl, trg_tbl, lý do), chưa xử lý
# Dán CẢ FILE vào 1 cell. Default lakehouse có thể vẫn là lh_vv_bronze. Chạy, gửi lại toàn bộ output.
# =============================================================================
import json
from pyspark.sql import functions as F
from delta.tables import DeltaTable

CTRL = "lh_vv_ctrl.dbo"
TABLES = ["ctrl_mng_pipeline_config", "ctrl_mng_watermark", "ctrl_cfg_schema_registry", "ctrl_log_run",
          "ctrl_log_table_run", "ctrl_cdc_state", "ctrl_cdc_reject"]
# Cột theo CTRL_TABLES_CONTEXT.md (08/10) — để so với bảng thật
EXPECTED = {
    "ctrl_mng_pipeline_config": "id pl_name src_schema src_tbl trg_schema trg_tbl is_active priority load_mode align_path dedup_order",
    "ctrl_mng_watermark": "watermark_id src_schema src_tbl trg_schema trg_tbl watermark_column watermark_value last_success_at status "
                          "flow_name watermark_sequence last_run_id last_src_version last_src_table_id error_message lock_exec_id "
                          "lock_at updated_at",
    "ctrl_cfg_schema_registry": "src_schema src_tbl src_object_schema src_object trg_schema trg_tbl trg_column json_path data_type "
                                "convert_rule is_key key_order is_toast column_order is_active description",
    "ctrl_log_run": "exec_id run_id pl_name nb_name src_schema src_tbl watermark_id run_mode table_filter src_version_from "
                    "src_version_to watermark_from watermark_to overlap_minutes read_rows valid_rows ignored_rows rejected_rows "
                    "ignored_detail tbl_total_count tbl_success_count tbl_failed_count tbl_no_data_count status started_at "
                    "ended_at duration_ms run_params error_message read_mode read_note output_versions_json",
    "ctrl_log_table_run": "exec_id run_id pl_name src_schema src_tbl src_object trg_schema trg_tbl priority attempt_no input_rows "
                          "stale_rows applicable_rows entity_rows upsert_event_rows delete_event_rows inserted_rows updated_rows "
                          "cast_null_rows rejected_rows status started_at ended_at duration_ms error_message src_versions_json "
                          "trg_version deactivated_rows qg_json",
    "ctrl_cdc_state": "trg_schema trg_tbl entity_key src_schema src_tbl src_object cdc_op cdc_ts_ms cdc_lsn raw_ingested_at "
                      "is_deleted src_version last_run_id updated_at",
    "ctrl_cdc_reject": "event_hash pl_name src_schema src_tbl src_object src_db trg_schema trg_tbl cdc_op entity_key cdc_ts_ms "
                       "cdc_lsn raw_ingested_at reject_reason reject_detail before_payload after_payload source_payload "
                       "first_run_id last_run_id reject_count first_rejected_at last_rejected_at is_resolved resolved_at",
}
print("CHECK_CTRL_SNAPSHOT")
print("session timeZone:", spark.conf.get("spark.sql.session.timeZone"), "| now UTC:",
      spark.sql("SELECT to_utc_timestamp(current_timestamp(), current_timezone())").first()[0])


def show(title, rows, cols, width=110):
    """In bảng gọn: mỗi giá trị cắt còn `width` ký tự."""
    print(f"\n=== {title}")
    print(" | ".join(cols))
    for r in rows:
        d = r if isinstance(r, dict) else r.asDict()
        print(" | ".join("(không có cột)" if c not in d else "NULL" if d[c] is None else str(d[c])[:width] for c in cols))
    if not rows:
        print("(không có dòng)")


def q(sql, **args):
    return spark.sql(sql, args=args).collect() if args else spark.sql(sql).collect()


# S0 -------------------------------------------------------------------------
s0 = []
for t in TABLES:
    fq = f"{CTRL}.{t}"
    try:
        d = spark.sql(f"DESCRIBE DETAIL {fq}").first().asDict()
        h = DeltaTable.forName(spark, fq).history(1).select("version", "timestamp", "operation").first()
        props = d.get("properties") or {}
        s0.append({"bang": t, "version": h["version"], "commit_cuoi": h["timestamp"], "op_cuoi": h["operation"],
                   "so_file": d.get("numFiles"), "MB": round((d.get("sizeInBytes") or 0) / 1e6, 1),
                   "partition": ",".join(d.get("partitionColumns") or []) or "-",
                   "optimizeWrite": props.get("delta.autoOptimize.optimizeWrite", "-"),
                   "autoCompact": props.get("delta.autoOptimize.autoCompact", "-")})
    except Exception as e:
        s0.append({"bang": t, "version": f"LỖI {type(e).__name__}", "commit_cuoi": None, "op_cuoi": None, "so_file": None,
                   "MB": None, "partition": None, "optimizeWrite": None, "autoCompact": None})
show("S0 bảng ctrl", s0, ["bang", "version", "commit_cuoi", "op_cuoi", "so_file", "MB", "partition", "optimizeWrite", "autoCompact"])

# S1 -------------------------------------------------------------------------
s1 = []
for t in TABLES:
    try:
        real = [c.lower() for c in spark.table(f"{CTRL}.{t}").columns]
    except Exception:
        continue
    exp = EXPECTED[t].split()
    s1.append({"bang": t, "so_cot": len(real), "thieu": [c for c in exp if c not in real] or "-",
               "thua": [c for c in real if c not in exp] or "-"})
show("S1 cột thực tế so với tài liệu", s1, ["bang", "so_cot", "thieu", "thua"], 300)

# S2 -------------------------------------------------------------------------
PC = f"{CTRL}.ctrl_mng_pipeline_config"
show("S2a pipeline_config theo (pl_name, src_tbl, load_mode)", q(f"""
    SELECT pl_name, src_tbl, upper(coalesce(load_mode, 'CDC')) AS load_mode, count(*) AS so_dong, sum(is_active) AS active,
           min(id) AS id_min, max(id) AS id_max, concat_ws(',', sort_array(collect_set(priority))) AS priority
    FROM {PC} GROUP BY 1, 2, 3 ORDER BY 1, 2, 3"""),
     ["pl_name", "src_tbl", "load_mode", "so_dong", "active", "id_min", "id_max", "priority"])
show("S2b dòng extract không active / có align_path / dedup_order", q(f"""
    SELECT id, src_tbl, trg_tbl, is_active, priority, load_mode, align_path, dedup_order FROM {PC}
    WHERE upper(coalesce(load_mode, 'CDC')) <> 'RECOMPUTE'
      AND (is_active <> 1 OR align_path IS NOT NULL OR dedup_order IS NOT NULL) ORDER BY id"""),
     ["id", "src_tbl", "trg_tbl", "is_active", "priority", "load_mode", "align_path", "dedup_order"])
has_nb = "nb_name" in [c.lower() for c in spark.table(PC).columns]
show("S2c cạnh RECOMPUTE", q(f"""
    SELECT id, pl_name, is_active, priority, concat(trg_schema, '.', trg_tbl) AS trg, concat(src_schema, '.', src_tbl) AS src,
           {'nb_name' if has_nb else 'CAST(NULL AS STRING)'} AS nb_name
    FROM {PC} WHERE upper(coalesce(load_mode, '')) = 'RECOMPUTE' ORDER BY pl_name, priority, trg, src"""),
     ["id", "pl_name", "is_active", "priority", "trg", "src", "nb_name"])

# S3 -------------------------------------------------------------------------
WM = f"{CTRL}.ctrl_mng_watermark"
show("S3a watermark: dòng nguồn + dòng khoá", q(f"""
    SELECT * FROM {WM} WHERE watermark_id NOT LIKE 'wm\\_e\\_\\_%' ORDER BY watermark_id"""),
     EXPECTED["ctrl_mng_watermark"].split(), 60)
show("S3b watermark cạnh: đếm theo trạng thái", q(f"""
    SELECT status, count(*) AS so_dong, count(last_src_version) AS da_doc, max(last_success_at) AS tien_gan_nhat
    FROM {WM} WHERE watermark_id LIKE 'wm\\_e\\_\\_%' GROUP BY 1 ORDER BY 1"""),
     ["status", "so_dong", "da_doc", "tien_gan_nhat"])
show("S3c watermark cạnh", q(f"""
    SELECT watermark_id, status, last_src_version, substr(last_src_table_id, 1, 8) AS tid8, watermark_value,
           last_success_at, last_run_id, error_message
    FROM {WM} WHERE watermark_id LIKE 'wm\\_e\\_\\_%' ORDER BY trg_tbl, src_tbl"""),
     ["watermark_id", "status", "last_src_version", "tid8", "watermark_value", "last_success_at", "last_run_id",
      "error_message"], 80)
show("S3d watermark: dòng nguồn (trg_tbl NULL) trùng src (kỳ vọng 0 dòng)", q(f"""
    SELECT src_schema, src_tbl, count(*) AS n FROM {WM}
    WHERE trg_tbl IS NULL AND watermark_id LIKE 'wm\\_transform\\_%' GROUP BY 1, 2 HAVING count(*) > 1"""),
     ["src_schema", "src_tbl", "n"])

# S4 -------------------------------------------------------------------------
show("S4 registry theo bảng", q(f"""
    SELECT src_tbl, trg_tbl, first(src_object) AS src_object, count(*) AS so_cot,
           sum(CASE WHEN is_active THEN 1 ELSE 0 END) AS bat,
           concat_ws(',', transform(sort_array(collect_list(CASE WHEN is_key THEN struct(key_order, trg_column) END)),
                                    x -> x.trg_column)) AS khoa,
           sum(CASE WHEN is_toast THEN 1 ELSE 0 END) AS toast,
           concat_ws(',', sort_array(collect_set(CASE WHEN upper(coalesce(convert_rule, 'NONE')) <> 'NONE'
                                                      THEN concat(trg_column, ':', convert_rule) END))) AS rule_khac
    FROM {CTRL}.ctrl_cfg_schema_registry GROUP BY 1, 2 ORDER BY 1, 2"""),
     ["src_tbl", "trg_tbl", "src_object", "so_cot", "bat", "khoa", "toast", "rule_khac"], 200)
show("S4b registry tổng theo nguồn", q(f"""
    SELECT src_tbl, count(DISTINCT trg_tbl) AS so_bang, count(*) AS so_cot,
           sum(CASE WHEN is_active THEN 1 ELSE 0 END) AS bat, sum(CASE WHEN is_toast THEN 1 ELSE 0 END) AS toast
    FROM {CTRL}.ctrl_cfg_schema_registry GROUP BY 1 ORDER BY 1"""), ["src_tbl", "so_bang", "so_cot", "bat", "toast"])

# S5 -------------------------------------------------------------------------
LR = f"{CTRL}.ctrl_log_run"
show("S5 ctrl_log_run: 15 run gần nhất mỗi (pl_name, nguồn)", q(f"""
    SELECT * FROM (
        SELECT pl_name, coalesce(src_tbl, '-') AS nguon, exec_id, run_mode, status, started_at, ended_at,
               round(duration_ms / 1000, 0) AS giay, read_mode, src_version_from, src_version_to, watermark_to,
               read_rows, valid_rows, ignored_rows, rejected_rows, tbl_total_count, tbl_success_count, tbl_failed_count,
               tbl_no_data_count, substr(error_message, 1, 200) AS loi,
               row_number() OVER (PARTITION BY pl_name, src_tbl ORDER BY started_at DESC) AS rn
        FROM {LR}) WHERE rn <= 15 ORDER BY pl_name, nguon, started_at DESC"""),
     ["pl_name", "nguon", "exec_id", "run_mode", "status", "started_at", "giay", "read_mode", "src_version_from",
      "src_version_to", "watermark_to", "read_rows", "valid_rows", "ignored_rows", "rejected_rows", "tbl_total_count",
      "tbl_success_count", "tbl_failed_count", "tbl_no_data_count", "loi"], 60)
show("S5b đếm theo trạng thái", q(f"""
    SELECT pl_name, coalesce(src_tbl, '-') AS nguon, status, count(*) AS so_run, min(started_at) AS tu, max(started_at) AS den
    FROM {LR} GROUP BY 1, 2, 3 ORDER BY 1, 2, 3"""), ["pl_name", "nguon", "status", "so_run", "tu", "den"])

# S6 -------------------------------------------------------------------------
last = q(f"""SELECT pl_name, src_tbl, max_by(exec_id, started_at) AS exec_id FROM {LR}
             WHERE status NOT IN ('SKIPPED_CONCURRENT', 'RUNNING') GROUP BY 1, 2""")
for r in last:
    rows = q(f"""
        SELECT trg_tbl, status, attempt_no, priority, input_rows, stale_rows, applicable_rows, entity_rows, inserted_rows,
               updated_rows, deactivated_rows, delete_event_rows, cast_null_rows, rejected_rows,
               round(duration_ms / 1000, 1) AS giay, trg_version, substr(error_message, 1, 150) AS loi
        FROM {CTRL}.ctrl_log_table_run WHERE exec_id = :e ORDER BY priority, trg_tbl""", e=r["exec_id"])
    show(f"S6 table log — {r['pl_name']} / {r['src_tbl'] or '-'} / exec {r['exec_id']}", rows,
         ["trg_tbl", "status", "attempt_no", "priority", "input_rows", "stale_rows", "applicable_rows", "entity_rows",
          "inserted_rows", "updated_rows", "deactivated_rows", "delete_event_rows", "cast_null_rows", "rejected_rows",
          "giay", "trg_version", "loi"], 60)

# S7 -------------------------------------------------------------------------
ST = f"{CTRL}.ctrl_cdc_state"
show("S7 ctrl_cdc_state theo bảng", q(f"""
    SELECT src_tbl, trg_tbl, count(*) AS so_dong, sum(CASE WHEN is_deleted THEN 1 ELSE 0 END) AS da_xoa,
           max(src_version) AS src_version_max, max(updated_at) AS cap_nhat_cuoi
    FROM {ST} GROUP BY 1, 2 ORDER BY 1, 2"""),
     ["src_tbl", "trg_tbl", "so_dong", "da_xoa", "src_version_max", "cap_nhat_cuoi"])
show("S7b trùng khoá state (kỳ vọng 0 dòng)", q(f"""
    SELECT trg_schema, trg_tbl, count(*) AS so_khoa_trung FROM (
        SELECT trg_schema, trg_tbl, entity_key FROM {ST} GROUP BY 1, 2, 3 HAVING count(*) > 1) GROUP BY 1, 2"""),
     ["trg_schema", "trg_tbl", "so_khoa_trung"])

# S8 -------------------------------------------------------------------------
show("S8 ctrl_cdc_reject theo lý do", q(f"""
    SELECT src_tbl, coalesce(trg_tbl, '-') AS trg_tbl, reject_reason, substr(reject_detail, 1, 80) AS chi_tiet,
           count(*) AS so_dong, sum(reject_count) AS so_lan, sum(CASE WHEN is_resolved THEN 1 ELSE 0 END) AS da_xu_ly,
           min(first_rejected_at) AS tu, max(last_rejected_at) AS den
    FROM {CTRL}.ctrl_cdc_reject GROUP BY 1, 2, 3, 4 ORDER BY so_dong DESC LIMIT 60"""),
     ["src_tbl", "trg_tbl", "reject_reason", "chi_tiet", "so_dong", "so_lan", "da_xu_ly", "tu", "den"])

print("\nXONG")
