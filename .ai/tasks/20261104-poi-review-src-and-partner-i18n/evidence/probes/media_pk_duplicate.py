# Environment: Fabric DEV. Read-only. One cell. Do not run NB_00.
# 1. Open a notebook on lh_vv_silver. Paste this file into one cell and run it.
# 2. Pass: stdout prints dup_keys and a table of at most 50 rows.
# 3. Paste that stdout into evidence/results/media_pk_duplicate.txt.
# Columns: media_id, origin, poi_id, business_service_id, rows. origin is google, i18n, or services.
# No URL, no media JSON, no name. Current tables, not VERSION AS OF.
# Decision: which input produced each duplicated media_id. Expect dup_keys = 2 if data is unchanged.

from pyspark.sql import functions as F
from pyspark.sql import types as T

SILVER = "lh_vv_silver.dbo"
PARTNER = "partner"
MEDIA_SCHEMA = T.ArrayType(T.StructType([
    T.StructField("url", T.StringType()),
    T.StructField("order", T.IntegerType()),
]))


def drop_live_target(df):
    cols = {name.lower() for name in df.columns}
    if {"row_hash", "deleted_at"} <= cols:
        keep = [name for name in df.columns if name.lower() not in {"row_hash", "created_at", "updated_at", "deleted_at"}]
        df = df.where(F.col("deleted_at").isNull()).select(*keep)
    return df


def live(df):
    return df.where(~F.coalesce(F.col("deleted"), F.lit(False)))


def array_state(raw):
    blank = raw.isNull() | F.trim(raw).isin("", "null")
    parsed = F.when(F.trim(raw).startswith("["), F.from_json(raw, MEDIA_SCHEMA))
    empty = blank | (parsed.isNotNull() & (F.size(parsed) == 0))
    return parsed, empty


def poi_id_of(sid):
    digest = F.md5(F.concat(sid, F.lit(PARTNER)))
    return F.regexp_replace(digest, r"^(.{8})(.{4})(.{4})(.{4})(.{12})$", r"$1-$2-$3-$4-$5")


google = drop_live_target(spark.table(f"{SILVER}.slv_3p_poi_media"))
google_rows = google.select(
    F.col("media_dedup_key").alias("media_id"),
    F.lit("google").alias("origin"),
    F.col("poi_id").cast("string").alias("poi_id"),
    F.lit(None).cast("string").alias("business_service_id"),
)

i18n = live(drop_live_target(spark.table(f"{SILVER}.slv_pn_business_service_i18ns"))).where(F.col("locale") == "vi")
services = live(drop_live_target(spark.table(f"{SILVER}.slv_pn_business_services")))
vi = i18n.select(F.col("business_service_id").cast("string").alias("business_service_id"), F.col("media").alias("_mi"))
svc = services.select(F.col("id").cast("string").alias("business_service_id"), F.col("media").alias("_ms"))
arr_i, empty_i = array_state(F.col("_mi"))
arr_s, _empty_s = array_state(F.col("_ms"))
docs = (vi.join(svc, "business_service_id", "left")
        .select("business_service_id",
                poi_id_of(F.col("business_service_id")).alias("poi_id"),
                F.when(empty_i, arr_s).otherwise(arr_i).alias("_arr"),
                F.when(empty_i, F.lit("services")).otherwise(F.lit("i18n")).alias("origin")))
url = F.col("_e.url")
kept = (docs.select("business_service_id", "poi_id", "origin", F.posexplode("_arr").alias("pos", "_e"))
        .where(url.isNotNull() & (F.trim(url) != "")))
partner_rows = kept.select(
    F.sha2(F.concat_ws("|", F.lit(PARTNER), F.col("poi_id"), F.trim(url)), 256).alias("media_id"),
    "origin", "poi_id", "business_service_id",
)
keyed = (google_rows.unionByName(partner_rows)
         .groupBy("media_id", "origin", "poi_id", "business_service_id")
         .agg(F.count(F.lit(1)).alias("rows")))
dup_ids = keyed.groupBy("media_id").agg(F.sum("rows").alias("copies")).where("copies > 1").select("media_id")
detail = keyed.join(dup_ids, "media_id", "inner")
print("dup_keys", dup_ids.count())
detail.orderBy("media_id", "origin", "poi_id").limit(50).show(50, truncate=False)
