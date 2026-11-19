# Probe p1_sgm_source_id. Môi trường: Fabric DEV. Chỉ đọc lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream và lh_vv_silver.dbo.slv_3p_poi.
# Điều kiện: một cell PySpark trên DEV. Không ghi bảng, không sửa watermark.
# Cách chạy: dán cả file vào cell rồi Run. Đọc ba dòng in SUMMARY, ID_MATCH, OVERLAP và các dòng KEY.
# Dán stdout vào .ai/tasks/20261119-gsm-as-google-extract/evidence/results/p1_sgm_source_id.txt
# Giới hạn: tối đa 50 dòng. Không payload, tên, số điện thoại, URL, giá trị source_id.
# Câu hỏi: source_id sgm có trùng google không; id payload có bằng source_id không (chỉ đếm); khóa registry vắng hay JSON null.
# Tiêu chí: overlap_source_id > 0 thì dừng user_decision, không sửa code. = 0 thì dòng google hiện có chưa cùng khóa MERGE.

from pyspark.sql import functions as F

BRONZE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
SILVER = "lh_vv_silver.dbo.slv_3p_poi"
KEYS = (
    "displayName", "types", "businessStatus", "primaryType",
    "addressComponents", "formattedAddress", "location", "plusCode",
    "websiteUri", "googleMapsUri", "nationalPhoneNumber",
    "priceRange", "priceLevel",
    "regularOpeningHours", "currentOpeningHours",
    "rating", "userRatingCount",
    "reviews", "photos",
    "servesBreakfast", "servesBrunch", "servesLunch", "servesDinner",
    "servesBeer", "servesWine", "servesCocktails", "servesDessert",
    "servesCoffee", "servesVegetarianFood", "allowsDogs", "goodForChildren",
    "goodForGroups", "goodForWatchingSports", "liveMusic", "menuForChildren",
    "outdoorSeating", "restroom", "reservable", "takeout", "delivery",
    "dineIn", "curbsidePickup", "parkingOptions", "paymentOptions",
    "accessibilityOptions", "evChargeOptions", "fuelOptions",
)


def _blank(column):
    return column.isNull() | (F.trim(column) == "")


bronze = spark.table(BRONZE).select("source_name", "source_id", "normalized_payload")
name = F.lower(F.trim(F.col("source_name")))
sgm = bronze.where(name == F.lit("sgm"))
google = bronze.where(name == F.lit("google"))
silver = spark.table(SILVER).select("source_name")
silver_name = F.lower(F.trim(F.col("source_name")))

sgm_ids = sgm.where(~_blank(F.col("source_id"))).select(F.trim(F.col("source_id")).alias("source_id")).distinct()
google_ids = google.where(~_blank(F.col("source_id"))).select(F.trim(F.col("source_id")).alias("source_id")).distinct()
overlap = sgm_ids.join(google_ids, "source_id", "inner").count()

payload_id = F.get_json_object(F.col("normalized_payload"), "$.id")
id_match = sgm.agg(
    F.sum(F.when(payload_id.isNull(), 1).otherwise(0)).alias("id_null"),
    F.sum(F.when(payload_id.isNotNull() & (payload_id == F.col("source_id")), 1).otherwise(0)).alias("id_eq_source_id"),
    F.sum(F.when(payload_id.isNotNull() & (payload_id != F.col("source_id")), 1).otherwise(0)).alias("id_ne_source_id"),
).first()

summary = {
    "bronze_sgm": sgm.count(),
    "bronze_google": google.count(),
    "sgm_source_id_blank": sgm.where(_blank(F.col("source_id"))).count(),
    "google_source_id_blank": google.where(_blank(F.col("source_id"))).count(),
    "silver_sgm": silver.where(silver_name == F.lit("sgm")).count(),
    "silver_google": silver.where(silver_name == F.lit("google")).count(),
}
print("SUMMARY " + " ".join(f"{key}={value}" for key, value in summary.items()))
print(
    "ID_MATCH "
    f"id_null={id_match['id_null'] or 0} "
    f"id_eq_source_id={id_match['id_eq_source_id'] or 0} "
    f"id_ne_source_id={id_match['id_ne_source_id'] or 0}"
)
print(f"OVERLAP overlap_source_id={overlap}")

keys_col = F.expr("json_object_keys(normalized_payload)")
keyed = sgm.select(keys_col.alias("ks"), "normalized_payload")
aggs = [F.sum(F.when(F.col("ks").isNull(), 1).otherwise(0)).alias("keys_null")]
for key in KEYS:
    present = F.array_contains(F.col("ks"), F.lit(key))
    value = F.get_json_object(F.col("normalized_payload"), f"$.{key}")
    aggs.append(F.sum(F.when(~present, 1).otherwise(0)).alias(f"{key}__absent"))
    aggs.append(F.sum(F.when(present & value.isNull(), 1).otherwise(0)).alias(f"{key}__null"))
    aggs.append(F.sum(F.when(present & value.isNotNull(), 1).otherwise(0)).alias(f"{key}__value"))
row = keyed.agg(*aggs).first()
print(f"KEY_PARSE keys_null={row['keys_null'] or 0}")
shown = 0
for key in KEYS:
    absent = int(row[f"{key}__absent"] or 0)
    nulls = int(row[f"{key}__null"] or 0)
    if absent == 0 and nulls == 0:
        continue
    print(f"KEY {key} absent={absent} present_null={nulls} present_value={int(row[f'{key}__value'] or 0)}")
    shown += 1
print(f"KEY_ROWS shown={shown}")
