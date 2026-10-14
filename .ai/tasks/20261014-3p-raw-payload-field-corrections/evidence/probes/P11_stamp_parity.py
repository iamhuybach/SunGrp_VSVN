# Chạy trong notebook Spark Fabric DEV. Chỉ in counts.
# Baseline = Delta version mới nhất trước 2026-10-14 13:02:00 UTC.
# Pass: diffs = 0 và lost_keys = 0 ở cả chín bảng.

from pyspark.sql import functions as F

TABLES = [
    ("slv_3p_poi", "poi_id"),
    ("slv_3p_poi_address", "poi_id"),
    ("slv_3p_poi_amenity", "poi_id"),
    ("slv_3p_poi_contact", "poi_id"),
    ("slv_3p_poi_opening_hours", "poi_id"),
    ("slv_3p_poi_price", "poi_id"),
    ("slv_3p_poi_rating", "poi_id"),
    ("slv_3p_poi_review", "review_id"),
    ("slv_3p_poi_media", "media_dedup_key"),
]
CUTOFF = F.lit("2026-10-14 13:02:00").cast("timestamp")
rows = []
for table, key in TABLES:
    version = (
        spark.sql(f"DESCRIBE HISTORY lh_vv_silver.dbo.{table}")
        .where(F.col("timestamp") < CUTOFF)
        .agg(F.max("version").alias("v"))
        .collect()[0].v
    )
    old = spark.sql(f"SELECT * FROM lh_vv_silver.dbo.{table} VERSION AS OF {int(version)}")
    new = spark.table(f"lh_vv_silver.dbo.{table}")
    shared = [c for c in old.columns if c in set(new.columns) and c != "updated_at"]
    old.createOrReplaceTempView("_p11_old")
    new.createOrReplaceTempView("_p11_new")
    same = " AND ".join(f"n.`{c}` <=> o.`{c}`" for c in shared)
    joined = spark.sql(f"""
        SELECT
          count(*) AS joined_keys,
          sum(CASE WHEN n.`_crawled_at` <=> o.`_crawled_at`
                    AND n.`_event_id` <=> o.`_event_id` THEN 1 ELSE 0 END) AS same_stamp,
          sum(CASE WHEN n.`_crawled_at` <=> o.`_crawled_at`
                    AND n.`_event_id` <=> o.`_event_id`
                    AND NOT ({same}) THEN 1 ELSE 0 END) AS diffs,
          sum(CASE WHEN NOT (n.`_crawled_at` <=> o.`_crawled_at`
                    AND n.`_event_id` <=> o.`_event_id`) THEN 1 ELSE 0 END) AS stamp_changed
        FROM _p11_new n
        INNER JOIN _p11_old o ON n.`{key}` <=> o.`{key}`
    """).collect()[0]
    lost = spark.sql(f"""
        SELECT count(*) AS lost_keys
        FROM _p11_old o
        LEFT ANTI JOIN _p11_new n ON n.`{key}` <=> o.`{key}`
    """).collect()[0].lost_keys
    rows.append((table, int(version), int(joined.joined_keys), int(joined.same_stamp or 0),
                 int(joined.diffs or 0), int(joined.stamp_changed or 0), int(lost)))

spark.createDataFrame(
    rows,
    ["tbl", "baseline_version", "joined_keys", "same_stamp", "diffs", "stamp_changed", "lost_keys"],
).show(20, False)
