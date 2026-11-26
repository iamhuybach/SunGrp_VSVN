# Environment: Fabric DEV notebook, one Python cell, read-only. No parameters.
# Table: sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi (OLD in NB_SETUP_LEGACY_GOLD_POI).
# Steps: open a DEV notebook, paste this file into one cell, run, copy stdout.
# Pass: stdout has COLUMNS, NEEDED, and JSON_TOKEN. Fail: table missing or an exception.
# Paste: .ai/tasks/20261126-legacy-init-enriched-cols-and-dest-portal/evidence/results/ai_enriched_poi_schema.txt
# Limits: names, types, and counts only. No cell values. Cap printed key rows at 50.

from pyspark.sql import functions as F

TABLE = "sgr_visitvn_prd_batch.lh_vv_gold.dbo.ai_enriched_poi"
LANG_NAMES = ("lang", "language", "locale", "lang_code", "language_code", "poi_lang")
NEEDED = ("poi_id", "story", "local_tips", "poi_address_json")
JSON_KEYS = ("address_line2", "price_level", "price_min", "price_max")

df = spark.table(TABLE)
fields = list(df.schema.fields)
names = {field.name.lower(): field.name for field in fields}

print("COLUMNS\t" + ",".join(f"{field.name}:{field.dataType.simpleString()}" for field in fields))
print("NEEDED\t" + " ".join(f"{name}={'present' if name in names else 'MISSING'}" for name in NEEDED))
print(f"ROW_COUNT\t{df.count()}")

found = [names[name] for name in LANG_NAMES if name in names]
print("LANG_CANDIDATES\t" + (" ".join(found) if found else "NONE"))

if "poi_id" in names:
    poi = names["poi_id"]
    print(f"POI_ID_DISTINCT\t{df.select(poi).distinct().count()}")
    print(f"POI_ID_NULL\t{df.where(F.col(poi).isNull()).count()}")
    buckets = (
        df.groupBy(poi)
        .count()
        .groupBy("count")
        .count()
        .orderBy(F.col("count"))
        .limit(20)
        .collect()
    )
    print("ROWS_PER_POI\t" + " ".join(f"{row[0]}:{row[1]}" for row in buckets))
    for lang in found:
        pairs = df.groupBy(poi, lang).count()
        duplicate_keys = pairs.where(F.col("count") > 1).count()
        blank = df.where(F.col(lang).isNull() | (F.trim(F.col(lang).cast("string")) == "")).count()
        print(f"GRAIN\t{lang}\tduplicate_keys={duplicate_keys}\tnull_or_blank={blank}")

for column in ("story", "local_tips"):
    if column in names:
        source = names[column]
        nulls = df.where(F.col(source).isNull()).count()
        print(f"NULL\t{source}\t{nulls}")

if "poi_address_json" not in names:
    print("JSON_TOKEN\tMISSING_COLUMN")
else:
    source = names["poi_address_json"]
    present = df.where(F.col(source).isNotNull() & (F.trim(F.col(source).cast("string")) != ""))
    print(f"JSON_NONEMPTY\t{present.count()}")
    aggs = []
    for key in JSON_KEYS:
        aggs.append(F.sum(F.when(F.col(source).rlike(rf'"{key}"'), 1).otherwise(0)).alias(f"{key}_present"))
        aggs.append(F.sum(F.when(F.col(source).rlike(rf'"{key}"\s*:\s*-?[0-9]'), 1).otherwise(0)).alias(f"{key}_number"))
        aggs.append(F.sum(F.when(F.col(source).rlike(rf'"{key}"\s*:\s*"'), 1).otherwise(0)).alias(f"{key}_string"))
        aggs.append(F.sum(F.when(F.col(source).rlike(rf'"{key}"\s*:\s*null'), 1).otherwise(0)).alias(f"{key}_null"))
    token_row = present.agg(*aggs).collect()[0]
    for key in JSON_KEYS:
        print(
            "JSON_TOKEN\t{0}\tpresent={1}\tnumber={2}\tstring={3}\tnull={4}".format(
                key,
                token_row[f"{key}_present"],
                token_row[f"{key}_number"],
                token_row[f"{key}_string"],
                token_row[f"{key}_null"],
            )
        )
    try:
        key_rows = (
            present.select(F.explode(F.map_keys(F.from_json(F.col(source), "MAP<STRING,STRING>"))).alias("json_key"))
            .where(F.col("json_key").isNotNull())
            .groupBy("json_key")
            .count()
            .orderBy("json_key")
            .limit(50)
            .collect()
        )
        print("JSON_KEYS\t" + " ".join(f"{row[0]}:{row[1]}" for row in key_rows))
    except Exception:
        print("JSON_KEYS\tERROR")
