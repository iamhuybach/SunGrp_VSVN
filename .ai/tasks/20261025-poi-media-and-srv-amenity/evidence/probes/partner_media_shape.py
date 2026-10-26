# Probe: partner_media_shape
# Environment: Fabric DEV. Lakehouse lh_vv_silver. Spark notebook, read-only.
# Prerequisite: tables lh_vv_silver.dbo.slv_pn_business_service_i18ns and slv_pn_business_services.
# Question: JSON shape of column media (null, blank, object, array, other) and types of url and order.
# Pass: each column has one dominant shape, and url/order are present or reported missing. No guessed array or object.
# Steps: new Spark notebook on DEV, paste this file into one cell, run. Do not %run a library.
# Paste the printed text to evidence/results/partner_media_shape.txt. At most 50 rows. No URL values, no personal data, no secrets.
# Decision: D-MEDIA-SHAPE. Counts and key names only.

import json

from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType, StringType, StructField, StructType

I18N = "lh_vv_silver.dbo.slv_pn_business_service_i18ns"
SERVICES = "lh_vv_silver.dbo.slv_pn_business_services"
OUT = StructType([
    StructField("shape", StringType()),
    StructField("keys", StringType()),
    StructField("url_type", StringType()),
    StructField("order_type", StringType()),
    StructField("n_elem", IntegerType()),
    StructField("n_url", IntegerType()),
    StructField("n_distinct_url", IntegerType()),
])


def _field_types(elements, field):
    kinds = set()
    for item in elements:
        if not isinstance(item, dict):
            kinds.add("elem_" + type(item).__name__)
            continue
        if field not in item:
            kinds.add("missing")
        elif item[field] is None:
            kinds.add("null")
        else:
            kinds.add(type(item[field]).__name__)
    return "|".join(sorted(kinds)) if kinds else "missing"


def describe(raw):
    if raw is None:
        return ("null", "", "", "", 0, 0, 0)
    text = raw.strip()
    if text == "":
        return ("blank", "", "", "", 0, 0, 0)
    try:
        value = json.loads(text)
    except (TypeError, ValueError):
        return ("invalid", "", "", "", 0, 0, 0)
    if isinstance(value, dict):
        elements = [value]
        shape = "object"
    elif isinstance(value, list):
        elements = value
        shape = "array_empty" if not value else "array"
    else:
        return (type(value).__name__, "", "", "", 0, 0, 0)
    keys = sorted({key for item in elements if isinstance(item, dict) for key in item.keys()})
    urls = []
    for item in elements:
        if isinstance(item, dict) and isinstance(item.get("url"), str):
            urls.append(item["url"].strip())
    return (
        shape,
        ",".join(keys[:30]),
        _field_types(elements, "url"),
        _field_types(elements, "order"),
        len(elements),
        len(urls),
        len(set(urls)),
    )


describe_udf = F.udf(describe, OUT)


def shaped(frame, column):
    return frame.select(describe_udf(F.col(column)).alias("d")).select("d.*")


def report(title, frame):
    print("== " + title)
    frame.groupBy("shape", "keys", "url_type", "order_type").count().orderBy(F.desc("count")).show(50, truncate=False)
    frame.agg(
        F.count("*").alias("rows"),
        F.sum(F.when(F.col("n_elem") > 1, 1).otherwise(0)).alias("multi_elem"),
        F.sum(F.when((F.col("n_url") > 0) & (F.col("n_distinct_url") < F.col("n_url")), 1).otherwise(0)).alias("dup_url_docs"),
        F.sum(F.when(F.col("n_url") == 0, 1).otherwise(0)).alias("no_string_url"),
        F.min("n_elem").alias("min_elem"),
        F.max("n_elem").alias("max_elem"),
    ).show(truncate=False)


i18n = spark.table(I18N)
services = spark.table(SERVICES)
vi = i18n.where(F.col("locale") == F.lit("vi"))

print("== row counts")
print("i18n", i18n.count(), "vi", vi.count(), "services", services.count())

report("i18n locale=vi media", shaped(vi, "media"))
report("slv_pn_business_services media", shaped(services, "media"))

fallback = (
    vi.select(F.col("business_service_id").alias("id"), F.col("media").alias("i18n_media"))
    .join(services.select("id", F.col("media").alias("svc_media")), "id", "left")
)
empty_i18n = F.col("i18n_media").isNull() | (F.trim(F.col("i18n_media")) == F.lit(""))
present_svc = F.col("svc_media").isNotNull() & (F.trim(F.col("svc_media")) != F.lit(""))
print("== vi fallback candidates")
fallback.agg(
    F.count("*").alias("vi_rows"),
    F.sum(F.when(empty_i18n, 1).otherwise(0)).alias("vi_media_null_or_blank"),
    F.sum(F.when(empty_i18n & present_svc, 1).otherwise(0)).alias("fallback_services_media_present"),
    F.sum(F.when(empty_i18n & ~present_svc, 1).otherwise(0)).alias("both_empty"),
).show(truncate=False)
