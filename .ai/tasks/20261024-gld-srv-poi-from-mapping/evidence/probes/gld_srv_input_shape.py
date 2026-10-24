# Environment: Fabric DEV. Paste this file into one notebook cell. Read-only.
# Decision: B2 Google null or empty hours; B3 several periods on one day; B4 destination updated_at ties or nulls; B5 partner hours array length. Also the count lines for C1-C6.
# Pass: the paste has the count and tag lines and no raw JSON. Fail: a query error, or the paste contains raw JSON or personal data.
# Prerequisite: lh_vv_silver.dbo.slv_poi_entity_non_enrich, slv_enr_poi_info_multi_lang, slv_enr_poi_destination, slv_pn_business_service_i18ns.
# Save: .ai/tasks/20261024-gld-srv-poi-from-mapping/evidence/results/gld_srv_input_shape.txt
# Limits: paste counts and tag names only. No raw JSON, names, bios, phones, emails, or addresses.

import json
from collections import Counter
from pyspark.sql import Window, functions as F

S = "lh_vv_silver.dbo"
ent = spark.table(f"{S}.slv_poi_entity_non_enrich")
ml = spark.table(f"{S}.slv_enr_poi_info_multi_lang")
des = spark.table(f"{S}.slv_enr_poi_destination")
i18n = spark.table(f"{S}.slv_pn_business_service_i18ns")
src = F.lower(F.trim(F.col("source_name")))

ent.groupBy(src.alias("src"), F.col("deleted_at").isNotNull().alias("deleted")).count().show(20, False)
print("entity_poi_id_dup", ent.groupBy("poi_id").count().where("count > 1").count())
print("ml_rows", ml.count(), "ml_lang_null", ml.where("lang IS NULL").count(),
      "ml_key_dup", ml.groupBy("poi_id", "lang").count().where("count > 1").count())
ml.groupBy("lang").count().show(20, False)
print("ml_poi_not_in_entity", ml.select("poi_id").distinct().join(ent.select("poi_id"), "poi_id", "left_anti").count())
print("i18n_key_dup", i18n.groupBy("business_service_id", "locale").count().where("count > 1").count())
pid = F.regexp_replace(F.md5(F.concat(F.col("business_service_id"), F.lit("partner"))),
                       r"^(.{8})(.{4})(.{4})(.{4})(.{12})$", "$1-$2-$3-$4-$5")
k = i18n.select(pid.alias("poi_id"), F.col("locale").alias("lang"),
                F.coalesce(F.col("deleted"), F.lit(False)).alias("i18n_deleted"), F.col("bio").isNull().alias("bio_null"))
pml = ml.join(ent.where(src == "partner").select("poi_id"), "poi_id", "left_semi").select("poi_id", "lang")
pml.join(k, ["poi_id", "lang"], "left").groupBy("i18n_deleted", "bio_null").count().show(20, False)

w = Window.partitionBy("poi_id")
d = (des.withColumn("_n", F.count(F.lit(1)).over(w)).withColumn("_max", F.max("updated_at").over(w))
     .withColumn("_nulls", F.count(F.when(F.col("updated_at").isNull(), 1)).over(w)).where("_n > 1"))
vals = F.to_json(F.struct("street", "ward", "district", "city", "full_address"))
tie = (d.where("updated_at = _max").groupBy("poi_id")
       .agg(F.count(F.lit(1)).alias("c"), F.countDistinct(vals).alias("v")).where("c > 1"))
print("des_dup_poi", d.select("poi_id").distinct().count(),
      "des_dup_with_null_updated_at", d.where("_nulls > 0").select("poi_id").distinct().count(),
      "des_tie_poi", tie.count(), "des_tie_values_differ", tie.where("v > 1").count())

def google_tags(text):
    if text is None:
        return ["null"]
    try:
        doc = json.loads(text)
    except ValueError:
        return ["invalid_json"]
    if not isinstance(doc, list):
        return ["not_array"]
    if not doc:
        return ["empty_array"]
    tags = {"key:" + key for item in doc if isinstance(item, dict) for key in item}
    if any(not isinstance(item, dict) for item in doc):
        return sorted(tags | {"non_object_element"})
    days = [item.get("day_of_week") for item in doc]
    if len(doc) == 1 and doc[0] == {"open_hour": 0, "open_minute": 0, "day_of_week": 0}:
        tags.add("all_day_exact")
    if any("close_hour" not in item or "close_minute" not in item for item in doc):
        tags.add("missing_close")
    if len(days) != len(set(days)):
        tags.add("multi_period_day")
    if any(day not in range(7) for day in days):
        tags.add("day_out_of_range")
    if len(set(days)) < 7:
        tags.add("missing_day")
    if any("close_day" in item and item["close_day"] != item.get("day_of_week") for item in doc):
        tags.add("close_day_differs")
    return sorted(tags)

def partner_tags(text):
    if text is None:
        return ["null"]
    try:
        doc = json.loads(text)
    except ValueError:
        return ["invalid_json"]
    if not isinstance(doc, dict):
        return ["not_object"]
    tags = set()
    for day in ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"):
        entry = doc.get(day)
        hours = entry.get("hours", "MISSING") if isinstance(entry, dict) else "MISSING"
        if entry is not None and not isinstance(entry, dict):
            tags.add("day_not_object")
        elif hours == "MISSING":
            tags.add("hours_missing")
        elif hours is None:
            tags.add("hours_null")
        elif not isinstance(hours, list):
            tags.add("hours_not_array")
        else:
            tags.add(f"hours_len_{min(len(hours), 2)}")
            if any(not isinstance(h, dict) or not isinstance(h.get("open_time"), str)
                   or not isinstance(h.get("close_time"), str) for h in hours):
                tags.add("hours_bad_element")
    return sorted(tags)

for name, fn in (("google", google_tags), ("partner", partner_tags)):
    rows = ent.where(src == name).select("opening_hours_text").rdd.map(lambda r: r[0])
    counts = Counter(tag for tags in rows.map(fn).collect() for tag in tags)
    print(name, "rows", rows.count())
    for tag, n in sorted(counts.items()):
        print(name, tag, n)
