# Môi trường: Fabric DEV. Notebook gắn lakehouse đọc được lh_vv_silver. Chỉ đọc. Không ghi, không OPTIMIZE.
# Điều kiện: lh_vv_silver.dbo.slv_pn_products và lh_vv_silver.dbo.slv_pn_product_posts tồn tại. Chạy cả file trong một cell.
# Kết quả: .ai/tasks/20261127-slv-pn-product-business-mapping/evidence/results/holiday_product_post_id_type.txt
# Giới hạn: chỉ đếm lớp kiểu và số post khớp. Không in giá trị JSON, id, giá, tên. Tối đa 50 dòng.
# Quyết định: kiểu JSON của metadata.holiday_product_post_id khi so với slv_pn_product_posts.external_id.
# Đạt: in được số product theo lớp kiểu, và số product theo nhóm khớp 0 / 1 / nhiều. Không exception.
# Không đạt: in ra giá trị, hoặc một mục ném lỗi. Dán cả text lỗi.
# Chạy lại: cùng số đếm, vì script không ghi.
# Lần 1: SparkUpgradeException khi parse timestamp '58774-09-09 16:50:00.000000'. Chưa có lớp kiểu.
# Lần này đặt timeParserPolicy=LEGACY trước mọi lệnh đọc, và chỉ SELECT cột không phải timestamp.

from pyspark.sql import functions as F

spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")

LIMIT = 50
SILVER = "lh_vv_silver.dbo"
KEY = "holiday_product_post_id"

products = spark.sql(
    f"SELECT `id` AS product_id, cast(`metadata` AS string) AS metadata FROM {SILVER}.slv_pn_products"
)
posts = spark.sql(
    f"SELECT cast(`external_id` AS string) AS external_id, `deleted` FROM {SILVER}.slv_pn_product_posts"
)

token = F.trim(F.regexp_extract(F.col("metadata"), rf'"{KEY}"\s*:\s*([^,}}\]]+)', 1))
first = F.substring(token, 1, 1)
value_class = (
    F.when(F.col("metadata").isNull() | ~F.col("metadata").contains(KEY), "key_absent")
    .when(token == "", "empty_token")
    .when(first == F.lit('"'), "string")
    .when(first.rlike(r"[0-9-]"), "number")
    .when(first.isin("t", "T", "f", "F"), "boolean")
    .when(token.startswith("null"), "null")
    .when(first == F.lit("{"), "object")
    .when(first == F.lit("["), "array")
    .otherwise("other")
)
scalar = F.when(value_class == "string", F.regexp_replace(token, r'^"|"$', "")).otherwise(token)

classified = products.select("product_id", value_class.alias("value_class"), scalar.alias("scalar"))
active_posts = posts.filter(F.col("deleted") == F.lit(False)).select("external_id")

print("## value_class")
print("class\tproducts")
class_rows = (
    classified.groupBy("value_class")
    .count()
    .orderBy(F.desc("count"))
    .limit(LIMIT)
    .collect()
)
for row in class_rows:
    print(f"{row['value_class']}\t{row['count']}")

matched = (
    classified.join(active_posts, classified.scalar == active_posts.external_id, "left")
    .groupBy("product_id", "value_class")
    .agg(F.count("external_id").alias("match_count"))
)
bucket = (
    F.when(F.col("match_count") == 0, "0")
    .when(F.col("match_count") == 1, "1")
    .otherwise("many")
)

print("\n## string_compare_to_active_external_id")
print("value_class\tmatch_bucket\tproducts")
bucket_rows = (
    matched.groupBy("value_class", bucket.alias("match_bucket"))
    .count()
    .orderBy("value_class", "match_bucket")
    .limit(LIMIT)
    .collect()
)
for row in bucket_rows:
    print(f"{row['value_class']}\t{row['match_bucket']}\t{row['count']}")
