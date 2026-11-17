# Environment: Fabric DEV. Notebook on lakehouse lh_vv_bronze. Read-only. Do not write or OPTIMIZE.
# Prerequisite: lh_vv_bronze.dbo.brz_enrichment_result exists. Run this file as one cell. Paste the whole printout.
# Result: .ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape_rest.txt
# Limits: counts and key-set names only. No JSON values, addresses, or names. At most 50 rows per section.
# Decision: experiences and destinations are arrays; destination elements have id and name; translated_at parses as a timestamp.
# Pass: experiences_not_array=0, experiences_parse_null=0, destinations_not_array=0, destinations_parse_null=0, null_id=0, null_name=0, translated_at parse_null=0.
# Fail: any of those counts is above 0, or a section raises. Paste the error text too.
# Do not print data values. Do not call schema_of_json on a column.

from pyspark.sql import functions as F

TABLE = "lh_vv_bronze.dbo.brz_enrichment_result"
LIMIT = 50
frame = spark.table(TABLE)
text = F.col("data").cast("string")
lang = frame.filter(F.col("event_type") == F.lit("LANG"))
dest = frame.filter(F.col("event_type") == F.lit("DESTINATION"))


def show(title, rows):
    print(f"\n## {title}")
    if not rows:
        print("(0 rows)")
        return
    headers = list(rows[0].asDict().keys())
    print("\t".join(headers))
    for row in rows[:LIMIT]:
        values = row.asDict()
        print("\t".join("" if values[name] is None else str(values[name]) for name in headers))


def array_report(subset, path, element_type, label):
    raw = F.get_json_object(text, path)
    present = subset.filter(raw.isNotNull())
    parsed = F.from_json(raw, element_type)
    first = F.get_json_object(raw, "$[0]")
    keys = F.array_join(F.array_sort(F.map_keys(F.from_json(first, "map<string,string>"))), ",")
    stats = present.agg(
        F.count(F.lit(1)).alias("nonempty"),
        F.sum(F.when(F.substring(F.ltrim(raw), 1, 1) == F.lit("["), 0).otherwise(1)).alias("not_array"),
        F.sum(F.when(parsed.isNull(), 1).otherwise(0)).alias("parse_null"),
    )
    show(f"{label}_PARSE", stats.collect())
    grouped = present.groupBy(keys.alias("first_element_keys")).count().orderBy(F.desc("count"))
    show(f"{label}_FIRST_ELEMENT_KEYS", grouped.limit(LIMIT).collect())
    return parsed


array_report(lang, "$.experiences", "array<struct<title:string,keyword:string,description:string>>", "EXPERIENCES")
dest_parsed = array_report(
    dest,
    "$.destinations",
    "array<struct<id:string,name:string>>",
    "DESTINATIONS",
)
dest_raw = F.get_json_object(text, "$.destinations")
elements = dest.filter(dest_raw.isNotNull()).select(F.explode_outer(dest_parsed).alias("el"))
el_agg = elements.agg(
    F.count(F.lit(1)).alias("elements"),
    F.sum(F.when(F.col("el.id").isNull(), 1).otherwise(0)).alias("null_id"),
    F.sum(F.when(F.col("el.name").isNull(), 1).otherwise(0)).alias("null_name"),
)
show("DESTINATION_ELEMENT_NULLS", el_agg.collect())

translated = F.get_json_object(text, "$.translated_at")
parsed_ts = F.to_timestamp(translated)
ts_agg = lang.filter(translated.isNotNull()).agg(
    F.count(F.lit(1)).alias("nonempty"),
    F.sum(F.when(parsed_ts.isNull(), 1).otherwise(0)).alias("parse_null"),
)
show("TRANSLATED_AT_PARSE", ts_agg.collect())
