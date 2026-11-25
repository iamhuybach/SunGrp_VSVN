# Probe: hours_shape
# Decision: D-02. Confirm the keys inside old-gold poi_opening_hours_json.periods
# and the partner holiday_exceptions_json element keys. Also count nulls of the
# two new-gold columns already written by init.
#
# Environment: Fabric notebook in workspace sgr_visitvn_dev, default lakehouse
# lh_vv_gold. Read-only. No parameters.
#
# Output: printed JSON aggregates. Key names and counts only. No POI name,
# address, phone, email, or hour text. At most 50 rows per result set.
# Paste the whole cell output into:
# .ai/tasks/20261120-legacy-gold-init-mapping-audit/evidence/results/hours-shape.txt
#
# Pass: Google periods element keys are visible, and each result below has
# at most 50 rows. A key set other than open_hour, open_minute, close_hour,
# close_minute, day_of_week stops D-02. No new parser is written from this file.

import json

from pyspark.sql import functions as F

OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo"
INFO = "sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_info"
LIMIT = 50


def show(title, df):
    rows = df.limit(LIMIT + 1).collect()
    if len(rows) > LIMIT:
        raise RuntimeError(f"{title}: more than {LIMIT} rows; narrow the probe")
    payload = [row.asDict(recursive=True) for row in rows]
    print(title)
    print(json.dumps(payload, ensure_ascii=False, default=str))
    print()


def kind_expr(raw):
    text = F.trim(raw)
    return (
        F.when(raw.isNull(), "null")
        .when(text == "", "empty")
        .when(text == "[]", "empty_array")
        .when(text == "{}", "empty_object")
        .when(text.startswith("["), "array")
        .when(text.startswith("{"), "object")
        .when(text.startswith('"'), "string")
        .otherwise("other")
    )


def object_keys(raw, kind):
    element = F.when(kind == F.lit("array"), F.get_json_object(raw, "$[0]")).otherwise(raw)
    parsed = F.from_json(
        F.when(kind.isin("array", "object"), element),
        "map<string,string>",
    )
    return F.when(kind.isin("array", "object"), F.array_sort(F.map_keys(parsed)))


detail = (
    spark.table(f"{OLD}.poi_detail")
    .where(F.col("lang") == "vi")
    .select("poi_id", "poi_opening_hours_json", "poi_content_json")
    .dropDuplicates(["poi_id"])
)
master = (
    spark.table(f"{OLD}.poi_master")
    .where(F.col("lang") == "vi")
    .select("poi_id", "ingestion_source")
    .dropDuplicates(["poi_id"])
)
src = detail.join(master, "poi_id", "inner")

info = spark.table(INFO).where(F.col("deleted_at").isNull())
show(
    "NEW_GOLD_NULLS",
    info.groupBy("source_name", "load_origin").agg(
        F.count(F.lit(1)).alias("n"),
        F.sum(F.when(F.col("operating_hours").isNull(), 1).otherwise(0)).alias("operating_hours_null"),
        F.sum(F.when(F.col("holiday_exceptions").isNull(), 1).otherwise(0)).alias("holiday_exceptions_null"),
    ).orderBy("source_name", "load_origin"),
)

top_keys = F.array_sort(F.map_keys(F.from_json("poi_opening_hours_json", "map<string,string>")))
show(
    "OLD_OPENING_TOP_KEYS",
    src.groupBy("ingestion_source", top_keys.alias("keys")).agg(F.count(F.lit(1)).alias("n"))
    .orderBy(F.desc("n")),
)

content_flag = F.get_json_object("poi_content_json", "$.hours_weekday_text")
show(
    "OLD_HOURS_WEEKDAY_TEXT",
    src.groupBy(
        "ingestion_source",
        F.when(content_flag.isNull(), "null").otherwise("present").alias("hours_weekday_text"),
    ).agg(F.count(F.lit(1)).alias("n")).orderBy("ingestion_source"),
)

PATHS = (
    "$.periods",
    "$.periods_json",
    "$.holiday_exceptions",
    "$.holiday_exceptions_json",
)
pieces = []
for path in PATHS:
    raw = F.get_json_object("poi_opening_hours_json", path)
    kind = kind_expr(raw)
    pieces.append(
        src.select(
            "ingestion_source",
            F.lit(path).alias("path"),
            kind.alias("kind"),
            object_keys(raw, kind).alias("element_keys"),
        )
    )
shaped = pieces[0]
for piece in pieces[1:]:
    shaped = shaped.unionByName(piece)
show(
    "OLD_FIELD_SHAPES",
    shaped.groupBy("ingestion_source", "path", "kind", "element_keys")
    .agg(F.count(F.lit(1)).alias("n"))
    .orderBy("ingestion_source", "path", F.desc("n")),
)

# One level under the first array element, or under the object itself.
# Child name and child key names only.
nested_parts = []
for path in PATHS:
    raw = F.get_json_object("poi_opening_hours_json", path)
    kind = kind_expr(raw)
    element = F.when(kind == F.lit("array"), F.get_json_object(raw, "$[0]")).otherwise(raw)
    parsed = F.from_json(F.when(kind.isin("array", "object"), element), "map<string,string>")
    nested_parts.append(
        src.select(
            "ingestion_source",
            F.lit(path).alias("path"),
            F.explode_outer(parsed).alias("child", "child_json"),
        ).where(F.col("child").isNotNull())
    )
nested = nested_parts[0]
for part in nested_parts[1:]:
    nested = nested.unionByName(part)
child_kind = kind_expr(F.col("child_json"))
child_keys = F.array_sort(
    F.map_keys(F.from_json(F.when(child_kind == F.lit("object"), F.col("child_json")), "map<string,string>"))
)
show(
    "OLD_FIELD_CHILD_KEYS",
    nested.groupBy(
        "ingestion_source",
        "path",
        "child",
        child_kind.alias("child_kind"),
        F.when(child_kind == F.lit("object"), child_keys).alias("child_keys"),
    ).agg(F.count(F.lit(1)).alias("n"))
    .orderBy("ingestion_source", "path", F.desc("n")),
)
