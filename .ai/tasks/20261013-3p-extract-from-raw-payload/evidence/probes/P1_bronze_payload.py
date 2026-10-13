# Probe P1 — schema bronze và tính hợp lệ của raw_payload.
# Môi trường: Fabric DEV, notebook Spark, lakehouse lh_vv_bronze, chỉ đọc.
# Không in giá trị payload, URL, tên người, hay review.
# Lưu stdout vào evidence/results/P1_bronze_payload.md.
# Đạt khi source google có raw_blank = not_object = invalid_json =
# object_with_trailing_content = crawled_at_null = 0, và raw_payload là string.

import json

import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

TABLE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
COLS = (
    "raw_payload",
    "normalized_payload",
    "source_name",
    "source_id",
    "language_code",
    "event_id",
    "crawled_at",
)

print("== describe ==")
(
    spark.sql(f"DESCRIBE TABLE {TABLE}")
    .select("col_name", "data_type")
    .where(F.col("col_name").isin(list(COLS)))
    .show(50, truncate=False)
)

print("== counts by source_name ==")
spark.sql(
    f"""
    SELECT
      source_name,
      count(*) AS n_rows,
      count(DISTINCT struct(source_name, source_id)) AS n_poi,
      sum(CASE WHEN raw_payload IS NULL OR trim(raw_payload) = '' THEN 1 ELSE 0 END) AS raw_blank,
      sum(CASE WHEN normalized_payload IS NULL OR trim(normalized_payload) = '' THEN 1 ELSE 0 END) AS norm_blank,
      sum(CASE WHEN crawled_at IS NULL THEN 1 ELSE 0 END) AS crawled_at_null,
      cast(min(crawled_at) AS string) AS min_crawled_at,
      cast(max(crawled_at) AS string) AS max_crawled_at,
      sum(CASE
            WHEN NOT (get_json_object(raw_payload, '$.id') <=> source_id) THEN 1
            ELSE 0
          END) AS raw_id_ne_source_id
    FROM {TABLE}
    GROUP BY source_name
    ORDER BY source_name
    """
).show(50, truncate=False)

OUT_SCHEMA = StructType(
    [
        StructField("scope", StringType()),
        StructField("klass", StringType()),
        StructField("n", LongType()),
        StructField("spark_id_and_trailing", LongType()),
    ]
)


def _klass(text):
    if text is None or str(text).strip() == "":
        return "blank", False
    raw = str(text).strip()
    try:
        obj, end = json.JSONDecoder().raw_decode(raw)
    except Exception:
        return "invalid_json", False
    trailing = end < len(raw)
    if not isinstance(obj, dict):
        return "not_object", False
    if trailing:
        return "object_with_trailing_content", True
    return "object_single", False


def classify_partition(iterator):
    for pdf in iterator:
        bucket = {}
        for text, spark_id, scope in zip(
            pdf["raw_payload"].tolist(),
            pdf["spark_id_present"].tolist(),
            pdf["scope"].tolist(),
        ):
            klass, trailing = _klass(text)
            slot = bucket.setdefault((scope, klass), [0, 0])
            slot[0] += 1
            if trailing and int(spark_id or 0) == 1:
                slot[1] += 1
        rows = [
            {
                "scope": scope,
                "klass": klass,
                "n": vals[0],
                "spark_id_and_trailing": vals[1],
            }
            for (scope, klass), vals in sorted(bucket.items())
        ]
        yield pd.DataFrame(rows, columns=["scope", "klass", "n", "spark_id_and_trailing"])


scoped = spark.sql(
    f"""
    SELECT
      CASE WHEN lower(trim(source_name)) = 'google' THEN 'in_scope' ELSE 'other' END AS scope,
      raw_payload,
      CASE WHEN get_json_object(raw_payload, '$.id') IS NOT NULL THEN 1 ELSE 0 END AS spark_id_present
    FROM {TABLE}
    """
)

print("== python class and spark-accepts-trailing ==")
(
    scoped.mapInPandas(classify_partition, OUT_SCHEMA)
    .groupBy("scope", "klass")
    .agg(
        F.sum("n").alias("n"),
        F.sum("spark_id_and_trailing").alias("spark_id_and_trailing"),
    )
    .orderBy("scope", "klass")
    .show(50, truncate=False)
)
