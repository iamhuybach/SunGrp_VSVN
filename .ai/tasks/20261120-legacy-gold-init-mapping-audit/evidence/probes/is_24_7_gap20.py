# Probe: is_24_7_gap20
# Why 6462 Google vi rows have is_24_7 true while info IS_24_7 is 6442.
# Pins of PLAN lgp-acfe492d29374536abd9e56f0fcc8838.
# Counts only. No poi ids, names, or hour text.
# Paste into:
# .ai/tasks/20261120-legacy-gold-init-mapping-audit/evidence/results/is-24-7-gap20.txt

import json

from pyspark.sql import functions as F
from pyspark.sql.window import Window

DETAIL = "sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_detail"
MASTER = "sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master"
MAP = "sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map"

detail = spark.sql(f"""
SELECT poi_id, poi_opening_hours_json
FROM {DETAIL} VERSION AS OF 6920
WHERE lang = 'vi'
""")
pm = spark.sql(f"""
SELECT poi_id, lang, source_id, ingestion_source,
       business_sector, business_category, subcategory_tags, operating_status,
       is_verified, is_bookable, rating_overall, rating_count,
       poi_name, district, is_active, created_at
FROM {MASTER} VERSION AS OF 8074
""")
mp_all = (
    spark.table(MAP)
    .where(F.col("poi_id_status") == "OK")
    .select(F.col("legacy_poi_id").alias("poi_id"), F.col("poi_id").alias("new_id"), "source_name", "lang")
)
mp = mp_all.where(F.col("lang") == "vi").select("poi_id", "new_id", "source_name")
flag = F.lower(F.trim(F.get_json_object("poi_opening_hours_json", "$.is_24_7"))) == F.lit("true")
google_vi = pm.where((F.col("lang") == "vi") & (F.col("ingestion_source") == "google")).select("poi_id")
flagged = (
    detail.join(google_vi, "poi_id", "inner")
    .where(flag)
    .select("poi_id")
    .dropDuplicates(["poi_id"])
    .join(mp, "poi_id", "left")
)

g = F.col("source_name") == F.lit("google")
rows = pm.join(mp_all.select(F.col("poi_id").alias("legacy_poi_id"), "new_id", "source_name"),
               pm["poi_id"] == F.col("legacy_poi_id")).select(
    F.col("new_id").alias("poi_id"),
    "source_name",
    "lang",
    "business_sector", "business_category", "subcategory_tags", "operating_status",
    "is_verified", "is_bookable",
    F.when(g, F.col("rating_overall").cast("decimal(4,2)")).alias("rating_overall"),
    F.when(g, F.col("rating_count").cast("int")).alias("rating_count"),
)
cmp_cols = ["source_name", "business_sector", "business_category", "subcategory_tags",
            "operating_status", "is_verified", "is_bookable", "rating_overall", "rating_count"]
agg = rows.groupBy("poi_id").agg(F.collect_set(F.struct(*cmp_cols)).alias("_cmp"))
cmp_conflict = agg.where(F.size("_cmp") > 1).select(F.col("poi_id").alias("new_id"))
kept = agg.where(F.size("_cmp") == 1).select(F.col("poi_id").alias("new_id"))

order = Window.partitionBy("new_id").orderBy(F.col("created_at").desc_nulls_last(), F.col("poi_id").desc())
chosen = (
    mp.join(pm.where(F.col("lang") == "vi").select("poi_id", "created_at"), "poi_id", "left")
    .withColumn("_rn", F.row_number().over(order))
    .where(F.col("_rn") == 1)
    .select("new_id", F.col("poi_id").alias("chosen_legacy"))
)
chosen_flag = chosen.join(flagged.select("poi_id").withColumn("_flagged_choice", F.lit(1)),
                           chosen["chosen_legacy"] == F.col("poi_id"), "left")

labeled = (
    flagged.join(cmp_conflict.withColumn("_conflict", F.lit(1)), "new_id", "left")
    .join(kept.withColumn("_kept", F.lit(1)), "new_id", "left")
    .join(chosen_flag.select("new_id", "_flagged_choice"), "new_id", "left")
)
reason = (
    F.when(F.col("new_id").isNull(), "no_map")
    .when(F.col("_conflict") == 1, "cmp_conflict")
    .when(F.col("_kept").isNull(), "not_kept")
    .when(F.col("_flagged_choice").isNull(), "chosen_legacy_not_flagged")
    .otherwise("in_info")
)
out = labeled.withColumn("reason", reason)
by_reason = [r.asDict() for r in out.groupBy("reason").count().orderBy("reason").collect()]
in_info_ids = out.where(F.col("reason") == "in_info").select("new_id").dropDuplicates(["new_id"])
print(json.dumps({
    "flagged_legacy_n": int(flagged.count()),
    "in_info_new_id_n": int(in_info_ids.count()),
    "cmp_conflict_groups": int(cmp_conflict.count()),
    "by_reason": by_reason,
}, ensure_ascii=False))
