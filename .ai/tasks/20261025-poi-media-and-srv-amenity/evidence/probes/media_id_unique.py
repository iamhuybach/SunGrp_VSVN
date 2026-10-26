# Fabric DEV. Read-only. No URL values, no personal data, at most 50 rows.
# Cell 1: %run NB_LIB_TRANSFORM_SLV_GLD
# Cell 2: paste only the code cell slvmediabuild from NB_SLV_POI_MEDIA_INFO. Do not run the node.
# Cell 3: paste this file.
# Save stdout to evidence/results/media_id_unique.txt.
# Pass: dup_media_id = 0. If it is not 0, stop. Do not dedupe.

from pyspark.sql import functions as F

TECH = {"row_hash", "created_at", "updated_at", "deleted_at"}


class _Ctx:
    def __init__(self):
        self.warns = {}
        self.metrics = {}
        self.frames = {}

    def input(self, role, live_only=True):
        df = self.frames[role]
        cols = {name.lower() for name in df.columns}
        if live_only and {"row_hash", "deleted_at"} <= cols:
            df = df.where(F.col("deleted_at").isNull()).drop(*[c for c in df.columns if c.lower() in TECH])
        return df

    def warn(self, name, n):
        self.warns[name] = int(n or 0)


ctx = _Ctx()
ctx.frames["media_3p"] = spark.table("lh_vv_silver.dbo.slv_3p_poi_media")
ctx.frames["i18n"] = spark.table("lh_vv_silver.dbo.slv_pn_business_service_i18ns")
ctx.frames["services"] = spark.table("lh_vv_silver.dbo.slv_pn_business_services")
built = build(ctx)
dups = built.groupBy("media_id").count().where("count > 1")
print("rows", built.count())
print("dup_media_id", dups.count())
print("warns", ctx.warns)
print("partner_fallback_docs", ctx.metrics.get("partner_fallback_docs"))
dups.select("media_id", "count").limit(50).show(50, truncate=False)
