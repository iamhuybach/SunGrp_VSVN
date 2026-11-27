# Fabric DEV. Spark notebook. Lakehouse lh_vv_bronze in the same workspace.
# Resolves U-04 on the legacy model tables lh_vv_bronze.partner.*
# listed in mapping_legacy_ai_product.md section 1.1.
# Paste the console into evidence/results/product_business_service_cardinality.txt
# At most 50 sample rows. No personal data, no secrets.
# Set LEGACY before any read. Spark 3 rejects timestamp year 58774.

spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
print("timeParserPolicy", spark.conf.get("spark.sql.legacy.timeParserPolicy"))

TABLES = (
    "products",
    "product_translations",
    "product_variants",
    "product_variant_translations",
    "product_attributes",
    "product_attribute_translations",
    "product_attribute_values",
    "product_attribute_value_translations",
    "product_business_service_relation",
    "product_posts",
    "hotel_room_types",
    "hotel_rate_plans",
)


def show(title, sql):
    print("\n==", title)
    try:
        spark.sql(sql).show(50, truncate=False)
    except Exception as exc:
        print("ERROR", type(exc).__name__)
        print(str(exc)[:2000])


def bucket_sql(table, group_col, bs_col):
    return f"""
SELECT
  CASE
    WHEN distinct_bs = 0 THEN '0'
    WHEN distinct_bs = 1 THEN '1'
    ELSE '2+'
  END AS distinct_business_service_id,
  COUNT(*) AS group_count
FROM (
  SELECT {group_col} AS group_id, COUNT(DISTINCT {bs_col}) AS distinct_bs
  FROM lh_vv_bronze.partner.{table}
  GROUP BY {group_col}
) counted
GROUP BY
  CASE
    WHEN distinct_bs = 0 THEN '0'
    WHEN distinct_bs = 1 THEN '1'
    ELSE '2+'
  END
ORDER BY distinct_business_service_id
"""


schemas = {}
for name in TABLES:
    full = f"lh_vv_bronze.partner.{name}"
    try:
        frame = spark.table(full)
        schemas[name] = frame.schema
        print(name, frame.columns)
    except Exception as exc:
        print(name, "ERROR", type(exc).__name__, str(exc)[:500])

for name, schema in schemas.items():
    by_lower = {field.name.lower(): field.name for field in schema}
    if "business_service_id" not in by_lower:
        print(name, "no business_service_id")
        continue
    if "product_id" in by_lower:
        group_col = by_lower["product_id"]
    elif name != "product_posts" and "id" in by_lower:
        group_col = by_lower["id"]
    else:
        print(name, "business_service_id present; grouped in the post-link query")
        continue
    show(
        f"{name} by {group_col}",
        bucket_sql(name, group_col, by_lower["business_service_id"]),
    )
    show(
        f"{name} sample 2+",
        f"""
SELECT
  {group_col} AS group_id,
  COUNT(*) AS row_count,
  COUNT(DISTINCT {by_lower["business_service_id"]}) AS distinct_business_service_id
FROM lh_vv_bronze.partner.{name}
GROUP BY {group_col}
HAVING COUNT(DISTINCT {by_lower["business_service_id"]}) > 1
ORDER BY distinct_business_service_id DESC, group_id
LIMIT 50
""",
    )

if "products" in schemas and "product_posts" in schemas:
    product_fields = {field.name.lower(): field for field in schemas["products"]}
    post_fields = {field.name.lower(): field.name for field in schemas["product_posts"]}
    metadata = product_fields.get("metadata")
    if metadata is not None and "external_id" in post_fields and "business_service_id" in post_fields:
        if metadata.dataType.simpleString() == "string":
            post_key = "get_json_object(product.metadata, '$.holiday_product_post_id')"
        elif "holiday_product_post_id" in {item.lower() for item in getattr(metadata.dataType, "fieldNames", lambda: [])()}:
            post_key = "product.metadata.holiday_product_post_id"
        else:
            post_key = None
            print("products.metadata type", metadata.dataType.simpleString())
        if post_key:
            show(
                "products to product_posts",
                f"""
SELECT
  CASE
    WHEN distinct_bs = 0 THEN '0'
    WHEN distinct_bs = 1 THEN '1'
    ELSE '2+'
  END AS distinct_post_business_service_id,
  COUNT(*) AS product_count
FROM (
  SELECT product.id AS product_id, COUNT(DISTINCT post.{post_fields["business_service_id"]}) AS distinct_bs
  FROM lh_vv_bronze.partner.products product
  LEFT JOIN lh_vv_bronze.partner.product_posts post
    ON {post_key} = post.{post_fields["external_id"]}
  GROUP BY product.id
) counted
GROUP BY
  CASE
    WHEN distinct_bs = 0 THEN '0'
    WHEN distinct_bs = 1 THEN '1'
    ELSE '2+'
  END
ORDER BY distinct_post_business_service_id
""",
            )
