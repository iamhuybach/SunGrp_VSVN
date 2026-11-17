# Environment: Fabric DEV. Notebook on lakehouse lh_vv_bronze. Read-only. Do not write or OPTIMIZE.
# Prerequisite: Spark can read lh_vv_bronze.dbo. Run this file as one cell. Paste the whole printout.
# Result: .ai/tasks/20261116-enr-lang-destination-from-bronze/evidence/results/probe_brz_enrichment_result.txt
# Limits: schema and aggregates only. No data values, addresses, or names. At most 50 rows per section.
# Decision: table existence, column names and types, event_id and LANG/DESTINATION grain uniqueness, watermark-candidate nulls and bounds.
# Pass: TABLE_STATUS=PRESENT, SCHEMA lists columns, UNIQUENESS and WATERMARK print. TABLE_STATUS=MISSING still completes the probe.
# Fail: a section raises before it prints its status. Paste the error text as well.
# Do not select the data column. Do not add a filter that returns payload text.

from pyspark.sql import functions as F

TABLE = "lh_vv_bronze.dbo.brz_enrichment_result"
LIMIT = 50
TIME_CANDIDATES = ("produced_at", "eventprocessedutctime", "eventenqueuedutctime")
LANG_PATHS = (
    "$.display.cost",
    "$.display.best_time",
    "$.display.time_to_spend",
    "$.description",
    "$.experiences",
    "$.translated_at",
)
DEST_PATHS = (
    "$.address.new.ward.name",
    "$.address.new.ward.name_with_type",
    "$.address.new.district.name",
    "$.address.new.district.name_with_type",
    "$.address.new.province.name",
    "$.address.new.province.name_with_type",
    "$.address.new.formatted_address",
    "$.address.old.ward.name",
    "$.address.old.ward.name_with_type",
    "$.address.old.district.name",
    "$.address.old.district.name_with_type",
    "$.address.old.province.name",
    "$.address.old.province.name_with_type",
    "$.address.old.formatted_address",
    "$.lat",
    "$.lng",
    "$.request.address",
    "$.destinations",
)


def show(title, frame):
    print(f"\n## {title}")
    rows = frame.limit(LIMIT).collect()
    if not rows:
        print("(0 rows)")
        return
    headers = list(rows[0].asDict().keys())
    print("\t".join(headers))
    for row in rows:
        values = row.asDict()
        print("\t".join("" if values[name] is None else str(values[name]) for name in headers))


def col(columns, name):
    return columns.get(name.lower())


print("## TABLE_LOOKUP")
listed = spark.sql("SHOW TABLES IN lh_vv_bronze.dbo")
name_col = "tableName" if "tableName" in listed.columns else listed.columns[-1]
matches = listed.filter(F.lower(F.col(name_col)).contains("enrich")).select(name_col).limit(LIMIT)
show("ENRICH_TABLE_NAMES", matches)
present = (
    listed.filter(F.lower(F.col(name_col)) == F.lit("brz_enrichment_result")).limit(1).count() > 0
)
print(f"TABLE_STATUS\t{'PRESENT' if present else 'MISSING'}")
if not present:
    print("STOP\ttable lh_vv_bronze.dbo.brz_enrichment_result was not found")
else:
    frame = spark.table(TABLE)
    columns = {field.name.lower(): field.name for field in frame.schema.fields}
    show("SCHEMA", spark.sql(f"DESCRIBE TABLE {TABLE}").select("col_name", "data_type"))

    def grain(label, subset, keys):
        print(f"\n## UNIQUENESS {label}")
        present_keys = [col(columns, key) for key in keys if col(columns, key)]
        missing_keys = [key for key in keys if not col(columns, key)]
        print("keys_present\t" + ",".join(present_keys))
        print("keys_missing\t" + ",".join(missing_keys))
        total = subset.count()
        print(f"rows\t{total}")
        if not present_keys:
            return
        distinct = subset.select(*present_keys).distinct().count()
        null_expr = " OR ".join(f"`{name}` IS NULL" for name in present_keys)
        nulls = subset.filter(null_expr).count()
        print(f"distinct_key\t{distinct}")
        print(f"duplicate_row_surplus\t{total - distinct}")
        print(f"rows_with_any_null_key\t{nulls}")

    grain("ALL event_id", frame, ("event_id",))
    if col(columns, "event_type"):
        event_type = col(columns, "event_type")
        show("EVENT_TYPE_COUNTS", frame.groupBy(event_type).count().orderBy(F.desc("count")))
        grain("LANG poi_id+lang+version", frame.filter(F.col(event_type) == F.lit("LANG")), ("poi_id", "lang", "version"))
        grain("LANG poi_id+lang", frame.filter(F.col(event_type) == F.lit("LANG")), ("poi_id", "lang"))
        grain("DESTINATION poi_id+version", frame.filter(F.col(event_type) == F.lit("DESTINATION")), ("poi_id", "version"))
        grain("DESTINATION poi_id", frame.filter(F.col(event_type) == F.lit("DESTINATION")), ("poi_id",))
    else:
        print("\n## UNIQUENESS LANG/DESTINATION\nkeys_missing\tevent_type")

    print("\n## WATERMARK")
    for candidate in TIME_CANDIDATES:
        actual = col(columns, candidate)
        if not actual:
            print(f"{candidate}\tABSENT")
            continue
        stats = frame.agg(
            F.sum(F.when(F.col(actual).isNull(), 1).otherwise(0)).alias("nulls"),
            F.min(F.col(actual).cast("string")).alias("min_value"),
            F.max(F.col(actual).cast("string")).alias("max_value"),
        ).collect()[0]
        print(f"{actual}\tnulls={stats['nulls']}\tmin={stats['min_value']}\tmax={stats['max_value']}")

    data_col = col(columns, "data")
    event_type = col(columns, "event_type")
    if data_col and event_type:
        print("\n## JSON_PATH_NONEMPTY")
        text = F.col(data_col).cast("string")

        def path_count(label, predicate, paths):
            subset = frame.filter(predicate)
            total = subset.count()
            print(f"group\t{label}\trows\t{total}")
            for path in paths:
                found = subset.filter(F.get_json_object(text, path).isNotNull()).count()
                print(f"path\t{path}\tnoneempty\t{found}")

        path_count("LANG", F.col(event_type) == F.lit("LANG"), LANG_PATHS)
        path_count("DESTINATION", F.col(event_type) == F.lit("DESTINATION"), DEST_PATHS)
    else:
        print("\n## JSON_PATH_NONEMPTY\nSKIP\tdata or event_type column is absent")
