# Fabric DEV. Spark notebook. Lakehouse lh_vv_silver in the same workspace.
# Resolves U-06. Read only. Paste the console into
# evidence/results/product_price_shape.txt
# Aggregates only. Do not paste price strings. No personal data, no secrets.
# The previous SQL failed while parsing timestamp 58774-09-09.
# Set LEGACY before any read of slv_pn_product_posts or slv_pn_product_sale.

spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
print("timeParserPolicy", spark.conf.get("spark.sql.legacy.timeParserPolicy"))


def show(title, sql):
    print("\n==", title)
    try:
        spark.sql(sql).show(50, truncate=False)
    except Exception as exc:
        print("ERROR", type(exc).__name__)
        print(str(exc)[:2000])


show(
    "post price shape",
    r"""
SELECT field_name, CAST(deleted AS STRING) AS deleted, shape, COUNT(*) AS row_count
FROM (
  SELECT deleted, 'original_price' AS field_name,
    CASE
      WHEN original_price IS NULL THEN 'null'
      WHEN TRIM(CAST(original_price AS STRING)) = '' THEN 'empty'
      WHEN LOWER(TRIM(CAST(original_price AS STRING))) IN ('true', 'false') THEN 'bool_text'
      WHEN TRIM(CAST(original_price AS STRING)) RLIKE '^-?[0-9]+(\\.[0-9]+)?$' THEN 'numeric_text'
      WHEN TRIM(CAST(original_price AS STRING)) RLIKE '^[A-Za-z0-9+/]+={0,2}$' THEN 'base64_like'
      ELSE 'other'
    END AS shape
  FROM lh_vv_silver.dbo.slv_pn_product_posts
  UNION ALL
  SELECT deleted, 'marketing_price',
    CASE
      WHEN marketing_price IS NULL THEN 'null'
      WHEN TRIM(CAST(marketing_price AS STRING)) = '' THEN 'empty'
      WHEN LOWER(TRIM(CAST(marketing_price AS STRING))) IN ('true', 'false') THEN 'bool_text'
      WHEN TRIM(CAST(marketing_price AS STRING)) RLIKE '^-?[0-9]+(\\.[0-9]+)?$' THEN 'numeric_text'
      WHEN TRIM(CAST(marketing_price AS STRING)) RLIKE '^[A-Za-z0-9+/]+={0,2}$' THEN 'base64_like'
      ELSE 'other'
    END
  FROM lh_vv_silver.dbo.slv_pn_product_posts
  UNION ALL
  SELECT deleted, 'markup_percent',
    CASE
      WHEN markup_percent IS NULL THEN 'null'
      WHEN TRIM(CAST(markup_percent AS STRING)) = '' THEN 'empty'
      WHEN LOWER(TRIM(CAST(markup_percent AS STRING))) IN ('true', 'false') THEN 'bool_text'
      WHEN TRIM(CAST(markup_percent AS STRING)) RLIKE '^-?[0-9]+(\\.[0-9]+)?$' THEN 'numeric_text'
      WHEN TRIM(CAST(markup_percent AS STRING)) RLIKE '^[A-Za-z0-9+/]+={0,2}$' THEN 'base64_like'
      ELSE 'other'
    END
  FROM lh_vv_silver.dbo.slv_pn_product_posts
) classified
GROUP BY field_name, CAST(deleted AS STRING), shape
ORDER BY field_name, deleted, shape
""",
)

show(
    "sale price sign",
    """
SELECT
  COUNT(*) AS row_count,
  SUM(CASE WHEN original_price IS NULL THEN 1 ELSE 0 END) AS original_null,
  SUM(CASE WHEN original_price = 0 THEN 1 ELSE 0 END) AS original_zero,
  SUM(CASE WHEN original_price < 0 THEN 1 ELSE 0 END) AS original_negative,
  SUM(CASE WHEN original_price > 0 THEN 1 ELSE 0 END) AS original_positive,
  SUM(CASE WHEN marketing_price IS NULL THEN 1 ELSE 0 END) AS marketing_null,
  SUM(CASE WHEN marketing_price = 0 THEN 1 ELSE 0 END) AS marketing_zero,
  SUM(CASE WHEN marketing_price < 0 THEN 1 ELSE 0 END) AS marketing_negative,
  SUM(CASE WHEN marketing_price > 0 THEN 1 ELSE 0 END) AS marketing_positive,
  SUM(CASE WHEN markup_percent IS NULL THEN 1 ELSE 0 END) AS markup_null,
  SUM(CASE WHEN markup_percent = 0 THEN 1 ELSE 0 END) AS markup_zero,
  SUM(CASE WHEN markup_percent < 0 THEN 1 ELSE 0 END) AS markup_negative,
  SUM(CASE WHEN markup_percent > 0 THEN 1 ELSE 0 END) AS markup_positive
FROM lh_vv_silver.dbo.slv_pn_product_sale
""",
)
