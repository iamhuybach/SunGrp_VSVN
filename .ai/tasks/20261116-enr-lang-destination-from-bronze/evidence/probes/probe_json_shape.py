# Environment: Fabric DEV. Notebook on lakehouse lh_vv_bronze. Read-only. Do not write or OPTIMIZE.
# Prerequisite: lh_vv_bronze.dbo.brz_enrichment_result exists. Run this file as one cell. Paste the whole printout.
# Result: .ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_json_shape.txt
# Limits: counts and schema strings only. No JSON values, addresses, or names. At most 50 rows per section.
# Decision: whether display.cost, best_time, and time_to_spend are objects with keys text and label; experiences and destinations are arrays; destination elements have id and name; translated_at parses as one timestamp format.
# Pass: every non-empty LANG display path has exactly the keys text and label, experiences is an array, every destinations element has id and name, and translated_at has one parse result.
# Fail: a section raises, or any non-empty group has a schema or key set other than the one above. Paste the error text too.
# Do not print data values.

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


def object_keys(subset, path, label):
    raw = F.get_json_object(text, path)
    keys = F.array_join(F.array_sort(F.map_keys(F.from_json(raw, "map<string,string>"))), ",")
    grouped = (
        subset.filter(raw.isNotNull())
        .groupBy(keys.alias("key_set"))
        .count()
        .orderBy(F.desc("count"))
    )
    show(f"OBJECT_KEYS {label} {path}", grouped.limit(LIMIT).collect())


for path in ("$.display.cost", "$.display.best_time", "$.display.time_to_spend"):
    object_keys(lang, path, "LANG")

print("\n## STOP")
print("Object keys above are enough for this file. Run probe_json_shape_rest.py for arrays and translated_at.")
print("Do not use schema_of_json on a column. Spark requires a literal.")
