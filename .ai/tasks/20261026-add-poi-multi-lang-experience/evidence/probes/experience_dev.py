# Fabric DEV. SPARK-001: usps vật lý, patch experience, chạy lại mlexppy, rule gold.
# Pass: usps string; lần 2 in experience: +[]; experience string nullable ngay sau description;
# lock_exec_id null; mismatch 0; count PK trùng (poi_id, lang) = 0.
# Fail nếu lệch. Dán output vào evidence/results/experience_dev.txt.
# Tối đa 50 dòng. Không dữ liệu cá nhân. Không secret.
# Trước script: runtime-runbook.md R0, P1, R1 hai lần, R2, R3, rồi publish và chạy GLD-30M (R4).
# Chưa publish NB_GLD_SRV_POI_MULTI_LANG trước khi mlexppy thành công.

%run NB_LIB_TRANSFORM_SLV_GLD

usps = spark.sql("DESCRIBE lh_vv_silver.dbo.slv_pn_business_service_i18ns").where("col_name = 'usps'")
print("usps", usps.collect())

def _cols(fq):
    rows = spark.sql(f"DESCRIBE {fq}").collect()
    return [(r.col_name, r.data_type) for r in rows if r.col_name and not r.col_name.startswith("#")]

for fq in (
    "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang",
    "lh_vv_gold.dbo.gld_srv_poi_multi_lang",
):
    cols = _cols(fq)
    names = [name for name, _dtype in cols]
    idx = names.index("description")
    print(fq, cols[idx:idx + 2])

lock = spark.sql("""
SELECT watermark_id, lock_exec_id, status
FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M'
""")
print("lock", lock.collect())

g = spark.table("lh_vv_gold.dbo.gld_srv_poi_multi_lang").where("deleted_at IS NULL")
ml = spark.table("lh_vv_silver.dbo.slv_enr_poi_info_multi_lang").select(
    "poi_id", "lang", F.col("experience").alias("ml_exp"))
pn = spark.table("lh_vv_silver.dbo.slv_pn_business_service_i18ns").select(
    uuid_md5(F.col("business_service_id"), F.lit("partner")).alias("poi_id"),
    F.col("locale").alias("lang"), "usps")
j = g.join(ml, ["poi_id", "lang"], "left").join(pn, ["poi_id", "lang"], "left")
partner = F.coalesce(F.lower(F.trim(F.col("source_name"))) == "partner", F.lit(False))
want = F.when(partner, F.coalesce(F.col("usps"), F.col("ml_exp"))).otherwise(F.col("ml_exp"))
print("mismatch", j.where(~F.col("experience").eqNullSafe(want)).count())
print("nonnull", g.where(F.col("experience").isNotNull()).count())
dup = g.groupBy("poi_id", "lang").count().where("count > 1")
print("duplicate_pk", dup.count())
j.groupBy(
    partner.alias("partner"),
    F.col("usps").isNotNull().alias("usps"),
    F.col("ml_exp").isNotNull().alias("ml"),
).count().show(50, truncate=False)
