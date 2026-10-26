# Cell 2 of a Fabric DEV notebook. Do not %run. uuid_md5 below is the same expression as NB_LIB_TRANSFORM_SLV_GLD.
# Environment: lh_vv_silver. Read-only. No URL values.
# Paste stdout to evidence/results/media_key_grain.txt. At most 50 rows. No personal data, no secrets.
# P1-P3 already observed 2026-10-26. This rerun is for P4 and P5 after uuid_md5 was missing.
# Pass: overlap_vi, overlap_services, null_url, null_order, elems. deleted: MISSING if that column is absent.

from pyspark.sql import functions as F

def uuid_md5(*cols):
    """Same expression as NB_LIB_TRANSFORM_SLV_GLD.uuid_md5. Local copy so the probe does not %run."""
    parts = [F.col(c) if isinstance(c, str) else c for c in cols]
    return F.regexp_replace(F.md5(F.concat(*parts)), r"^(.{8})(.{4})(.{4})(.{4})(.{12})$", "$1-$2-$3-$4-$5")

MEDIA = "lh_vv_silver.dbo.slv_3p_poi_media"
I18N = "lh_vv_silver.dbo.slv_pn_business_service_i18ns"
SERVICES = "lh_vv_silver.dbo.slv_pn_business_services"


def has_deleted(table):
    cols = {name.lower() for name in spark.table(table).columns}
    if "deleted" not in cols:
        print("deleted: MISSING on " + table)
        return False
    return True


print("== P1 3P key and cover determinism")
spark.sql(f"""
SELECT count(*) n, count(DISTINCT media_dedup_key) n_key,
       sum(CASE WHEN media_dedup_key IS NULL THEN 1 ELSE 0 END) null_key,
       sum(CASE WHEN poi_id IS NULL THEN 1 ELSE 0 END) null_poi,
       sum(CASE WHEN display_order IS NULL THEN 1 ELSE 0 END) null_order
FROM {MEDIA}
""").show(truncate=False)
spark.sql(f"""
SELECT count(*) poi_with_min_tie FROM (
  SELECT poi_id FROM (
    SELECT poi_id, display_order, min(display_order) OVER (PARTITION BY poi_id) m
    FROM {MEDIA}
  ) t
  WHERE display_order <=> m
  GROUP BY poi_id
  HAVING count(*) > 1
) u
""").show(truncate=False)

print("== P2 partner document grain")
i18n_deleted = "sum(CASE WHEN deleted THEN 1 ELSE 0 END) vi_deleted" if has_deleted(I18N) else "CAST(NULL AS BIGINT) vi_deleted"
svc_deleted = "sum(CASE WHEN deleted THEN 1 ELSE 0 END) deleted" if has_deleted(SERVICES) else "CAST(NULL AS BIGINT) deleted"
spark.sql(f"""
SELECT count(*) vi_rows, count(DISTINCT business_service_id) vi_ids, {i18n_deleted}
FROM {I18N} WHERE locale = 'vi'
""").show(truncate=False)
spark.sql(f"""
SELECT count(*) n, count(DISTINCT id) ids, {svc_deleted}
FROM {SERVICES}
""").show(truncate=False)

print("== P3 fallback for empty array and JSON null")
spark.sql(f"""
WITH i AS (
  SELECT business_service_id id, from_json(media, 'array<struct<url:string,`order`:int>>') a
  FROM {I18N} WHERE locale = 'vi'
),
s AS (
  SELECT id, from_json(media, 'array<struct<url:string,`order`:int>>') a
  FROM {SERVICES}
)
SELECT sum(CASE WHEN i.a IS NULL OR size(i.a) = 0 THEN 1 ELSE 0 END) vi_empty_any,
       sum(CASE WHEN (i.a IS NULL OR size(i.a) = 0) AND s.a IS NOT NULL AND size(s.a) > 0 THEN 1 ELSE 0 END) fallback_hits
FROM i LEFT JOIN s ON i.id = s.id
""").show(truncate=False)

print("== P4 cross-branch poi_id overlap")
google = spark.table(MEDIA).select("poi_id").where(F.col("poi_id").isNotNull()).distinct()
vi_ids = spark.table(I18N).where(F.col("locale") == F.lit("vi")).select(
    uuid_md5(F.col("business_service_id"), F.lit("partner")).alias("poi_id")
).distinct()
svc_ids = spark.table(SERVICES).select(
    uuid_md5(F.col("id"), F.lit("partner")).alias("poi_id")
).distinct()
print("overlap_vi", vi_ids.join(google, "poi_id", "left_semi").count())
print("overlap_services", svc_ids.join(google, "poi_id", "left_semi").count())

print("== P5 element-level nulls in vi arrays")
spark.sql(f"""
SELECT sum(CASE WHEN e.url IS NULL OR trim(e.url) = '' THEN 1 ELSE 0 END) null_url,
       sum(CASE WHEN e.`order` IS NULL THEN 1 ELSE 0 END) null_order,
       count(*) elems
FROM (
  SELECT explode(from_json(media, 'array<struct<url:string,`order`:int>>')) e
  FROM {I18N} WHERE locale = 'vi'
)
""").show(truncate=False)
