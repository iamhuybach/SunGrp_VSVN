# Probe: google_bad_time_cause
# Classifies Google periods_json rows that google_hours marks GOOGLE_BAD_TIME.
# Same pins as PLAN lgp-200ee509c66b41c2af9ac0b1f30a54b5.
# Output is counts of which time field is null or not a whole number.
# No poi ids, no hour values, no names.
# Paste into:
# .ai/tasks/20261120-legacy-gold-init-mapping-audit/evidence/results/google-bad-time-cause.txt

import json

from pyspark.sql import functions as F

DETAIL = "sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_detail"
MASTER = "sgr_visitvn_prd_batch.lh_vv_gold.dbo.poi_master"

detail = spark.sql(f"""
SELECT poi_id, poi_opening_hours_json
FROM {DETAIL} VERSION AS OF 6912
WHERE lang = 'vi'
""")
master = spark.sql(f"""
SELECT poi_id
FROM {MASTER} VERSION AS OF 8065
WHERE lang = 'vi' AND ingestion_source = 'google'
""").dropDuplicates(["poi_id"])

raw = F.get_json_object("poi_opening_hours_json", "$.periods_json")
is_24_7 = F.get_json_object("poi_opening_hours_json", "$.is_24_7")
periods = F.from_json(
    raw,
    "array<struct<open_hour:double,open_minute:double,close_hour:double,close_minute:double,day_of_week:double>>",
)
src = detail.join(master, "poi_id", "inner").select(
    "poi_id", raw.alias("raw"), is_24_7.alias("is_24_7"), periods.alias("periods"),
)
elem = src.select("poi_id", "is_24_7", F.explode("periods").alias("e"))

def whole(column):
    return column.isNotNull() & (column == F.floor(column))

open_ok = whole(F.col("e.open_hour")) & whole(F.col("e.open_minute"))
close_null = F.col("e.close_hour").isNull() | F.col("e.close_minute").isNull()
open_null = F.col("e.open_hour").isNull() | F.col("e.open_minute").isNull()
not_whole = (
    (F.col("e.open_hour").isNotNull() & (F.col("e.open_hour") != F.floor(F.col("e.open_hour"))))
    | (F.col("e.open_minute").isNotNull() & (F.col("e.open_minute") != F.floor(F.col("e.open_minute"))))
    | (F.col("e.close_hour").isNotNull() & (F.col("e.close_hour") != F.floor(F.col("e.close_hour"))))
    | (F.col("e.close_minute").isNotNull() & (F.col("e.close_minute") != F.floor(F.col("e.close_minute"))))
    | (F.col("e.day_of_week").isNotNull() & (F.col("e.day_of_week") != F.floor(F.col("e.day_of_week"))))
)
flags = elem.groupBy("poi_id", "is_24_7").agg(
    F.max(F.when(close_null & open_ok, 1).otherwise(0)).alias("close_null"),
    F.max(F.when(open_null, 1).otherwise(0)).alias("open_null"),
    F.max(F.when(not_whole, 1).otherwise(0)).alias("not_whole"),
    F.max(F.when(~open_ok & ~open_null & ~close_null & ~not_whole, 1).otherwise(0)).alias("other"),
)
bad = flags.where("close_null = 1 OR open_null = 1 OR not_whole = 1 OR other = 1")
cause = (
    F.when(F.col("not_whole") == 1, "not_whole_number")
    .when(F.col("open_null") == 1, "open_null")
    .when(F.col("close_null") == 1, "close_null")
    .otherwise("other")
)
rows = [r.asDict() for r in bad.groupBy(cause.alias("cause"), "is_24_7").count().orderBy("cause", "is_24_7").collect()]
print(json.dumps({"rows": rows, "bad_poi_n": int(bad.count())}, ensure_ascii=False))
