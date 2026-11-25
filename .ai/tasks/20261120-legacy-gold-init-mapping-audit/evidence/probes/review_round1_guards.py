# Probe: review_round1_guards
# Resolves review round 1 SQL-001 and SQL-002.
# PASS iff vi_key_collision_n == 0 AND rating_not_exact_bigint_n == 0.
#
# Environment: Fabric notebook in workspace sgr_visitvn_dev, default lakehouse
# lh_vv_gold. Read-only. No parameters. Uses the map and old gold already read
# by NB_SETUP_LEGACY_GOLD_POI. Do not pass a new pin.
#
# Output: one JSON object of two counts. No POI ids, names, or rating values.
# Paste it into:
# .ai/tasks/20261120-legacy-gold-init-mapping-audit/evidence/results/review-round1-guards.txt

import json

from pyspark.sql import functions as F

OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo"
MAP = "sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map"

mp = (
    spark.table(MAP)
    .where((F.col("lang") == "vi") & (F.col("poi_id_status") == "OK"))
    .select("legacy_poi_id", F.col("poi_id").alias("_new"))
)
vi_key_collision_n = mp.groupBy("_new").count().where("count > 1").count()

rating = spark.table(f"{OLD}.poi_rating")
dtype = dict(rating.dtypes)["total_reviews"]
raw = F.col("total_reviews")
joined = rating.join(mp.select(F.col("legacy_poi_id").alias("poi_id")), "poi_id", "inner")
rating_not_exact_bigint_n = joined.where(
    raw.isNotNull() & ~raw.cast("bigint").cast(dtype).eqNullSafe(raw)
).count()

print(json.dumps({
    "total_reviews_type": dtype,
    "vi_key_collision_n": int(vi_key_collision_n),
    "rating_not_exact_bigint_n": int(rating_not_exact_bigint_n),
}))
