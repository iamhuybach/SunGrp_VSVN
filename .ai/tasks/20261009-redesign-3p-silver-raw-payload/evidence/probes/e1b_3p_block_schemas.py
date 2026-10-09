# Probe E1b: schema của các khối JSON, không lấy giá trị.
# Môi trường: Fabric DEV, notebook Spark, lakehouse lh_vv_bronze, chỉ đọc.
# Chạy sau E1. Idempotent: không ghi bảng, không ghi file.
# schema_of_json trên Spark chỉ nhận chuỗi hằng, nên probe này dùng PySpark.
# In ra: số dòng, tập khóa cấp 1 (tối đa 20), và schema gộp (tên trường + kiểu).
# Nếu một dòng có số điện thoại, review, URL, hoặc giá trị payload: dừng, không lưu.
# Lưu stdout vào evidence/results/e1b_3p_block_schemas.txt.

import json

from pyspark.sql import functions as F

BLOCKS = (
    "extra_info",
    "poi_amenity",
    "poi_content",
    "poi_price",
    "policies",
)


def shape_token(text):
    """Tên khóa cấp 1 hoặc dạng mảng. Không trả giá trị."""
    if text is None:
        return None
    try:
        obj = json.loads(text)
    except Exception:
        return "INVALID"
    if isinstance(obj, dict):
        return "object:" + ",".join(sorted(obj.keys()))
    if isinstance(obj, list):
        if not obj:
            return "array:empty"
        first = obj[0]
        if isinstance(first, dict):
            return "array_object:" + ",".join(sorted(str(k) for k in first.keys()))
        return "array_scalar"
    return "other"


token_udf = F.udf(shape_token, "string")

src = spark.sql(
    """
    SELECT
        get_json_object(normalized_payload, '$.extra_info') AS extra_info,
        get_json_object(normalized_payload, '$.poi_amenity') AS poi_amenity,
        get_json_object(normalized_payload, '$.poi_content') AS poi_content,
        get_json_object(normalized_payload, '$.poi_price') AS poi_price,
        get_json_object(normalized_payload, '$.policies') AS policies
    FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
    """
).cache()

try:
    for name in BLOCKS:
        body = src.select(F.col(name).alias("body")).where(
            F.col("body").isNotNull() & F.col("body").rlike(r"^\s*[{\[]")
        )
        n = body.count()
        print(f"BLOCK\t{name}\tobject_or_array_rows\t{n}")
        if n == 0:
            print(f"KEYS\t{name}\t0\t<none>")
            print(f"SCHEMA\t{name}\t<none>")
            continue
        shapes = (
            body.withColumn("shape", token_udf(F.col("body")))
            .groupBy("shape")
            .count()
            .orderBy(F.desc("count"))
            .limit(20)
            .collect()
        )
        for row in shapes:
            print(f"KEYS\t{name}\t{row['count']}\t{row['shape']}")
        schema = spark.read.json(body.select("body").rdd.map(lambda row: row[0])).schema
        print(f"SCHEMA\t{name}\t{schema.simpleString()}")
finally:
    src.unpersist()
