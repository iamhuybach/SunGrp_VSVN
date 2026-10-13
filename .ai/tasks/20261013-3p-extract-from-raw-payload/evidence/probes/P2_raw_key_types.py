# Probe P2 — khóa và kiểu JSON của raw_payload, không lấy giá trị.
# Môi trường: Fabric DEV, notebook Spark, chỉ đọc lh_vv_bronze.
# Phạm vi: lower(trim(source_name)) = 'google' và raw_payload là một object.
# Lưu stdout vào evidence/results/P2_raw_key_types.md.
# Đạt khi mỗi đường dẫn được giữ có một họ kiểu khớp data_type,
# và displayName là string trên mọi trường hợp khác null.

import json

import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

TABLE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
NESTED = (
    "displayName",
    "displayName.text",
    "businessStatus",
    "priceLevel",
    "location.latitude",
    "location.longitude",
    "plusCode.globalCode",
    "rating",
    "userRatingCount",
    "websiteUri",
    "googleMapsUri",
    "regularOpeningHours.openNow",
    "regularOpeningHours.weekdayDescriptions",
    "currentOpeningHours.openNow",
    "photos[].name",
    "photos[].widthPx",
    "photos[].heightPx",
    "reviews[].publishTime",
    "reviews[].rating",
    "reviews[].text",
    "reviews[].text.text",
    "reviews[].authorAttribution.displayName",
)

OUT = StructType(
    [
        StructField("path", StringType()),
        StructField("kind", StringType()),
        StructField("json_type", StringType()),
        StructField("n", LongType()),
    ]
)


def _jtype(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, int):
        return "number_int"
    if isinstance(value, float):
        return "number_float"
    if isinstance(value, str):
        return "string"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return "other"


def _get(obj, path):
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return "missing", None
        cur = cur[part]
    return "present", cur


def _walk_array(obj, head, rest):
    """Đếm kiểu trên từng phần tử mảng. rest rỗng nghĩa là chính phần tử."""
    if not isinstance(obj, dict) or head not in obj:
        return [("docs_missing_key", "missing")]
    arr = obj[head]
    if arr is None:
        return [("docs_present", "null")]
    if not isinstance(arr, list):
        return [("docs_present", _jtype(arr))]
    if not rest:
        return [("element", _jtype(item)) for item in arr] or [("docs_present", "array_empty")]
    rows = []
    for item in arr:
        if not isinstance(item, dict):
            rows.append(("element", _jtype(item)))
            continue
        cur = item
        missing = False
        for part in rest.split("."):
            if not isinstance(cur, dict) or part not in cur:
                missing = True
                break
            cur = cur[part]
        rows.append(("element_missing", "missing") if missing else ("element", _jtype(cur)))
    return rows or [("docs_present", "array_empty")]


def classify_partition(iterator):
    for pdf in iterator:
        counts = {}
        for text in pdf["raw_payload"].tolist():
            try:
                obj, end = json.JSONDecoder().raw_decode(str(text).strip())
            except Exception:
                continue
            if not isinstance(obj, dict) or end < len(str(text).strip()):
                continue
            for key, value in obj.items():
                slot = counts.setdefault((key, "docs_present", _jtype(value)), 0)
                counts[(key, "docs_present", _jtype(value))] = slot + 1
            for path in NESTED:
                if "[]" in path:
                    head, _, rest = path.partition("[].")
                    if path.endswith("[]"):
                        head, rest = path[:-2], ""
                    observed = _walk_array(obj, head, rest)
                else:
                    state, value = _get(obj, path)
                    observed = [("docs_missing_key", "missing")] if state == "missing" else [("docs_present", _jtype(value))]
                for kind, jtype in observed:
                    key = (path, kind, jtype)
                    counts[key] = counts.get(key, 0) + 1
        yield pd.DataFrame(
            [
                {"path": path, "kind": kind, "json_type": jtype, "n": n}
                for (path, kind, jtype), n in sorted(counts.items())
            ]
        )


src = spark.sql(
    f"""
    SELECT raw_payload
    FROM {TABLE}
    WHERE lower(trim(source_name)) = 'google'
      AND raw_payload IS NOT NULL
      AND trim(raw_payload) <> ''
    """
)

print("== key and type counts ==")
(
    src.mapInPandas(classify_partition, OUT)
    .groupBy("path", "kind", "json_type")
    .agg(F.sum("n").alias("n"))
    .orderBy("path", "kind", "json_type")
    .show(500, truncate=False)
)
