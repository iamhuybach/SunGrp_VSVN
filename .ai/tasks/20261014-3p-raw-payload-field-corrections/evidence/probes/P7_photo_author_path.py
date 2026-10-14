# Probe P7 — tác giả ảnh và blob_url, chỉ đếm.
# Môi trường: Fabric DEV, notebook Spark, chỉ đọc lh_vv_bronze.
# Nguồn: normalized_payload. lower(trim(source_name)) = 'google'.
# Lưu ba bảng đếm vào evidence/results/P7_photo_author_path.md.
# Không ghi tên người, URL, số điện thoại, hay nội dung ảnh. Tối đa 50 dòng.

from pyspark.sql import functions as F

TABLE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
arr = "array<string>"
base = spark.table(TABLE).where("lower(trim(source_name)) = 'google'")
base.agg(
    F.count(F.lit(1)).alias("google_docs"),
    F.sum(F.when(
        F.col("normalized_payload").isNotNull() & (F.trim(F.col("normalized_payload")) != ""),
        1,
    ).otherwise(0)).alias("normalized_nonblank"),
).show(truncate=False)

b = base.where("normalized_payload IS NOT NULL AND trim(normalized_payload) <> ''")
e = b.select(F.explode(F.from_json(F.get_json_object("normalized_payload", "$.photos"), arr)).alias("e"))
e = e.withColumn("k", F.json_object_keys("e")) \
     .withColumn("n_attr", F.size(F.from_json(F.get_json_object("e", "$.authorAttributions"), arr)))

def cnt(c):
    return F.sum(F.when(c, 1).otherwise(0))

e.agg(
    F.count(F.lit(1)).alias("photo_elements"),
    cnt(F.array_contains("k", "authorAttribution")).alias("singular_key_present"),
    cnt(F.get_json_object("e", "$.authorAttribution.displayName").isNotNull()).alias("singular_display_name_nonnull"),
    cnt(F.array_contains("k", "authorAttributions")).alias("plural_key_present"),
    cnt(F.get_json_object("e", "$.authorAttributions[0].displayName").isNotNull()).alias("plural_first_display_name_nonnull"),
    cnt(F.array_contains("k", "blob_url")).alias("blob_url_key_present"),
    cnt(F.get_json_object("e", "$.blob_url").isNotNull()).alias("blob_url_nonnull"),
).show(truncate=False)
e.groupBy(F.coalesce(F.col("n_attr").cast("string"), F.lit("null")).alias("authorAttributions_size")).count() \
 .orderBy("authorAttributions_size").show(truncate=False)
