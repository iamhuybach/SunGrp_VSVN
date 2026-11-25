# Env: Fabric DEV. Read-only PySpark. One synthetic row. Do not read gold tables.
# 1. Open a notebook on workspace sgr_visitvn_dev.
# 2. Paste this file into one cell and run it.
# Pass: the assert holds. old_json equals new_json and old_hash equals new_hash.
# Fail: AssertionError. That means poi_name null changes to_json and the row hash.
# Paste the full stdout at evidence/results/poi_name_null_hash.txt.
# Limit: one synthetic row (poi_id=p, lang=vi, source_name=partner). No table scan, no UUID, no personal data.
# Resolves GATE-001: does to_json drop a null poi_name on this runtime?

from pyspark.sql import functions as F

p = spark.range(1).select(
    F.lit("p").alias("poi_id"),
    F.lit("vi").alias("lang"),
    F.lit("partner").alias("source_name"),
)
r = p.select(
    F.to_json(F.struct("poi_id", "lang", "source_name")).alias("old_json"),
    F.to_json(F.struct("poi_id", "lang", F.lit(None).cast("string").alias("poi_name"), "source_name")).alias("new_json"),
    F.sha2(F.to_json(F.struct("poi_id", "lang", "source_name")), 256).alias("old_hash"),
    F.sha2(F.to_json(F.struct("poi_id", "lang", F.lit(None).cast("string").alias("poi_name"), "source_name")), 256).alias("new_hash"),
).first()
try:
    ignore_null = spark.conf.get("spark.sql.jsonGenerator.ignoreNullFields")
except Exception:
    ignore_null = "unset"
print("spark.sql.jsonGenerator.ignoreNullFields=", ignore_null, r.asDict())
assert r.old_json == r.new_json and r.old_hash == r.new_hash
print("verdict\tnull_poi_name_hash_unchanged")
