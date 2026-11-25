# Probe: vi_key_rank1_source
# Resolves review round 2 SQL-001.
# PASS iff rank1_source_conflict_n == 0.
#
# Environment: Fabric notebook in workspace sgr_visitvn_dev, default lakehouse
# lh_vv_gold. Read-only. No parameters.
# Rank matches D-06: created_at descending, nulls last, then legacy poi_id descending.
# Output is one count. No poi ids and no names.
# Paste into:
# .ai/tasks/20261120-legacy-gold-init-mapping-audit/evidence/results/vi-key-rank1-source.txt

import json

from pyspark.sql import functions as F
from pyspark.sql.window import Window

OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo"
MAP = "sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map"

vi_rows = (
    spark.table(MAP)
    .where((F.col("lang") == "vi") & (F.col("poi_id_status") == "OK"))
    .select(F.col("legacy_poi_id").alias("poi_id"), F.col("poi_id").alias("_new"), "source_name")
)
arrived = (
    spark.table(f"{OLD}.poi_master")
    .where(F.col("lang") == "vi")
    .select("poi_id", "created_at")
)
order = Window.partitionBy("_new").orderBy(F.col("created_at").desc_nulls_last(), F.col("poi_id").desc())
rank1 = (
    vi_rows.join(arrived, "poi_id", "left")
    .withColumn("_rk", F.dense_rank().over(order))
    .where(F.col("_rk") == 1)
)
rank1_source_conflict_n = (
    rank1.groupBy("_new")
    .agg(F.countDistinct(F.coalesce(F.col("source_name"), F.lit(""))).alias("n"))
    .where("n > 1")
    .count()
)
print(json.dumps({"rank1_source_conflict_n": int(rank1_source_conflict_n)}))
