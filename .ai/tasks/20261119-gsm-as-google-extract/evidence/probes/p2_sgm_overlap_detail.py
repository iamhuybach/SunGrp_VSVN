# Probe p2_sgm_overlap_detail. Môi trường: Fabric DEV. Chỉ đọc lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream và lh_vv_silver.dbo.slv_3p_poi.
# Điều kiện: một cell PySpark. Không ghi bảng, không sửa watermark.
# Cách chạy: dán cả file vào cell rồi Run.
# Dán stdout vào .ai/tasks/20261119-gsm-as-google-extract/evidence/results/p2_sgm_overlap_detail.txt
# Giới hạn: chỉ dòng tổng hợp. Không payload, tên, số điện thoại, URL, giá trị source_id.
# Câu hỏi: cách viết source_name; overlap exact và trim; poi_id google đã có trên silver; crawled_at nào mới hơn; review và ảnh sgm trùng google trên 402 khóa.
# Tiêu chí: NAME khác đúng 'google' hoặc 'sgm', hoặc overlap_exact < overlap_trimmed, thì dừng và báo. Không sửa code.

from pyspark.sql import functions as F
from pyspark.sql.window import Window

BRONZE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
SILVER = "lh_vv_silver.dbo.slv_3p_poi"

bronze = spark.table(BRONZE).select("source_name", "source_id", "crawled_at", "event_id", "normalized_payload")
name_l = F.lower(F.trim(F.col("source_name")))
scoped = bronze.where(name_l.isin("google", "sgm"))
sid = F.trim(F.col("source_id"))
usable = sid.isNotNull() & (sid != "")

for row in scoped.groupBy("source_name").count().collect():
    value = row["source_name"]
    if value is not None and value.strip().lower() in ("google", "sgm"):
        print(f"NAME value={value} n={row['count']}")

sgm = scoped.where(name_l == F.lit("sgm"))
google = scoped.where(name_l == F.lit("google"))
sgm_exact = sgm.select("source_id").distinct()
google_exact = google.select("source_id").distinct()
sgm_trim = sgm.where(usable).select(sid.alias("source_id")).distinct()
google_trim = google.where(usable).select(sid.alias("source_id")).distinct()
overlap_exact = sgm_exact.join(google_exact, "source_id", "inner")
overlap_trim = sgm_trim.join(google_trim, "source_id", "inner")
sgm_distinct = sgm_trim.count()
overlap_exact_n = overlap_exact.count()
overlap_trim_n = overlap_trim.count()
print(
    "IDS "
    f"sgm_distinct={sgm_distinct} sgm_only={sgm_distinct - overlap_trim_n} "
    f"overlap_exact={overlap_exact_n} overlap_trimmed={overlap_trim_n}"
)

# Hash the stored sgm source_id. A trimmed id hits when any stored spelling hashes to a google silver poi_id.
sgm_rows = sgm.where(usable).alias("s")
hashed = sgm_rows.join(overlap_trim.alias("o"), F.trim(F.col("s.source_id")) == F.col("o.source_id"), "inner").select(
    F.trim(F.col("s.source_id")).alias("trim_id"),
    F.regexp_replace(
        F.md5(F.concat(F.lit("google"), F.col("s.source_id"))),
        r"^(.{8})(.{4})(.{4})(.{4})(.{12})$",
        "$1-$2-$3-$4-$5",
    ).alias("poi_id"),
).distinct()
silver_google = spark.table(SILVER).where(F.col("source_name") == F.lit("google")).select("poi_id").distinct()
silver_hit = hashed.join(silver_google, "poi_id", "inner").select("trim_id").distinct().count()
print(f"POI silver_hit={silver_hit}")

def _max_ts(df):
    return df.where(usable).groupBy(sid.alias("source_id")).agg(F.max(F.col("crawled_at").cast("string")).alias("ts"))

order = _max_ts(sgm).select("source_id", F.col("ts").alias("sgm_ts")).join(
    _max_ts(google).select("source_id", F.col("ts").alias("google_ts")), "source_id", "inner"
)
counts = order.agg(
    F.sum(F.when(F.col("sgm_ts") > F.col("google_ts"), 1).otherwise(0)).alias("sgm_newer"),
    F.sum(F.when(F.col("google_ts") > F.col("sgm_ts"), 1).otherwise(0)).alias("google_newer"),
    F.sum(F.when(F.col("sgm_ts").eqNullSafe(F.col("google_ts")), 1).otherwise(0)).alias("equal"),
).first()
print(
    "ORDER "
    f"sgm_newer={counts['sgm_newer'] or 0} google_newer={counts['google_newer'] or 0} equal={counts['equal'] or 0}"
)

latest_window = Window.partitionBy(name_l, sid).orderBy(F.col("crawled_at").cast("string").desc(), F.col("event_id").desc())
latest = (
    scoped.where(usable).alias("b")
    .join(overlap_trim.alias("o"), F.trim(F.col("b.source_id")) == F.col("o.source_id"), "inner")
    .select("b.*")
    .withColumn("_rn", F.row_number().over(latest_window))
    .where(F.col("_rn") == 1)
    .select(name_l.alias("src"), sid.alias("source_id"), "normalized_payload")
)

def _elements(frame, path):
    raw = F.get_json_object(F.col("normalized_payload"), path)
    return frame.select("src", "source_id", F.explode(F.from_json(raw, "array<string>")).alias("element"))

reviews = _elements(latest, "$.reviews").select(
    "src", "source_id",
    F.get_json_object("element", "$.authorAttribution.displayName").alias("author"),
    F.get_json_object("element", "$.publishTime").alias("publish_time"),
)
sgm_reviews = reviews.where(F.col("src") == F.lit("sgm"))
google_reviews = reviews.where(F.col("src") == F.lit("google"))
exact_keys = google_reviews.select("source_id", "author", "publish_time").distinct()
name_keys = google_reviews.select("source_id", "author").distinct()
matched_exact = sgm_reviews.join(exact_keys, ["source_id", "author", "publish_time"], "left_semi")
matched_name = sgm_reviews.join(name_keys, ["source_id", "author"], "left_semi")
print(
    "REVIEW "
    f"sgm_reviews={sgm_reviews.count()} match_exact={matched_exact.count()} "
    f"match_name_only={matched_name.join(matched_exact, ['source_id', 'author', 'publish_time'], 'left_anti').count()}"
)

photos = _elements(latest, "$.photos").select(
    "src", "source_id", F.get_json_object("element", "$.name").alias("photo_name")
)
sgm_photos = photos.where(F.col("src") == F.lit("sgm"))
google_names = photos.where(F.col("src") == F.lit("google")).select("source_id", "photo_name").distinct()
print(
    "PHOTO "
    f"sgm_photos={sgm_photos.count()} "
    f"match_name={sgm_photos.join(google_names, ['source_id', 'photo_name'], 'left_semi').count()} "
    f"scraper_named={sgm_photos.where(F.col('photo_name').contains('/photos/scraper-')).count()}"
)
