# Environment: Fabric DEV. Read-only. One cell. Do not run NB_00.
# 1. Open a notebook on lh_vv_silver. Paste this file into one cell and run it.
# 2. Pass: stdout prints fail_rows and a table of at most 50 rows.
# 3. Paste that stdout into evidence/results/partner_multi_hours.txt.
# Columns: poi_id, source_id, vi_rows, svc_rows, chosen, hours_entity, hours_i18n, hours_svc.
# chosen=i18n when exactly one live vi row has a non-null amentities block; else svc or not_one_vi.
# No JSON, name, description, URL, or hour text. Current tables, not VERSION AS OF.
# Decision: whether the PARTNER_MULTI_HOURS rows use the i18n block or the service block.

import json

from pyspark.sql import functions as F

DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")
SILVER = "lh_vv_silver.dbo"


def max_elems(text):
    if text is None:
        return None
    try:
        doc = json.loads(text)
    except (TypeError, ValueError, RecursionError):
        return -1
    if not isinstance(doc, dict):
        return -1
    best = 0
    for key in DAYS:
        entry = doc.get(key)
        hours = entry.get("hours") if isinstance(entry, dict) else None
        if isinstance(hours, list):
            best = max(best, len(hours))
    return best


def live_target(df):
    cols = {name.lower() for name in df.columns}
    if {"row_hash", "deleted_at"} <= cols:
        df = df.where(F.col("deleted_at").isNull())
    return df


def live_partner(df):
    return df.where(~F.coalesce(F.col("deleted"), F.lit(False)))


hours_n = F.udf(max_elems, "int")

entity = live_target(spark.table(f"{SILVER}.slv_poi_entity_non_enrich"))
bad = (entity.where(F.lower(F.trim(F.col("source_name"))) == "partner")
       .withColumn("hours_entity", hours_n(F.col("opening_hours_text")))
       .where(F.col("hours_entity") > 1)
       .select("poi_id", F.col("source_id").cast("string").alias("source_id"), "hours_entity"))

i18n = live_partner(spark.table(f"{SILVER}.slv_pn_business_service_i18ns")).where(F.col("locale") == "vi")
i18n_hours = F.get_json_object(F.col("amentities"), "$.policies.operating_hours")
i18n_agg = (i18n.groupBy(F.col("business_service_id").cast("string").alias("source_id"))
            .agg(F.count(F.lit(1)).alias("vi_rows"),
                 F.max(F.when(F.col("amentities").isNotNull(), F.lit(1)).otherwise(F.lit(0))).alias("i18n_block"),
                 F.max(hours_n(i18n_hours)).alias("hours_i18n")))

svc = live_partner(spark.table(f"{SILVER}.slv_pn_business_services"))
svc_hours = F.get_json_object(F.col("amentities"), "$.policies.operating_hours")
svc_agg = (svc.groupBy(F.col("id").cast("string").alias("source_id"))
           .agg(F.count(F.lit(1)).alias("svc_rows"),
                F.max(hours_n(svc_hours)).alias("hours_svc")))

chosen = (F.when(F.col("vi_rows").isNull() | (F.col("vi_rows") != 1), F.lit("not_one_vi"))
          .when(F.col("i18n_block") == 1, F.lit("i18n"))
          .otherwise(F.lit("svc")))
out = (bad.join(i18n_agg, "source_id", "left").join(svc_agg, "source_id", "left")
       .withColumn("chosen", chosen)
       .select("poi_id", "source_id", "vi_rows", "svc_rows", "chosen",
               "hours_entity", "hours_i18n", "hours_svc"))
print("fail_rows", out.count())
out.orderBy("poi_id").limit(50).show(50, truncate=False)
