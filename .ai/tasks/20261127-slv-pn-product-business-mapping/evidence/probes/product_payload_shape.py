# Môi trường: Fabric DEV. Notebook gắn lakehouse đọc được lh_vv_silver và lh_vv_bronze. Chỉ đọc. Không ghi, không OPTIMIZE.
# Điều kiện: lh_vv_silver.dbo.slv_pn_products và lh_vv_bronze.dbo.partner_raw_data tồn tại. Chạy cả file trong một cell. Dán toàn bộ phần in.
# Kết quả: .ai/tasks/20261127-slv-pn-product-business-mapping/evidence/results/product_payload_shape.txt
# Giới hạn: đếm và tên khóa JSON. Không in giá trị JSON, giá, mô tả, tên người. Mỗi mục tối đa 50 dòng.
# Quyết định: shape của metadata, attributes, raw_sync_data; chuỗi giá và deleted_at; locale và status đang có.
# Đạt: mỗi mục in được số dòng, phân loại, và không có exception. Bảng silver 0 dòng thì mục bronze của bảng nguồn đó có số dòng.
# Không đạt: một mục ném lỗi, hoặc in ra giá trị nghiệp vụ. Dán cả text lỗi.
# Chạy lại: cùng kết quả đếm, vì script không ghi. Nếu mọi bảng silver ở mục shape có count > 0 thì script không đọc bronze.
# Lần chạy 2026-11-27: slv_pn_products = 41, rồi SparkUpgradeException khi parse timestamp '58774-09-09 16:50:00.000000'.
# Bản này chỉ SELECT cột cần phân loại. Không đọc src_created_at, src_updated_at, validity_from, validity_to.
# Nếu cột được chọn vẫn là timestamp hỏng, cell đặt spark.sql.legacy.timeParserPolicy=LEGACY rồi đọc lại cột đó. Không ghi bảng.

from pyspark.sql import functions as F

LIMIT = 50
SILVER = "lh_vv_silver.dbo"
BRONZE = "lh_vv_bronze.dbo.partner_raw_data"

# silver table, bronze source.table, checks (column, kind)
SPECS = [
    ("slv_pn_products", "products", [
        ("metadata", "json"), ("status", "enum"), ("deleted_at", "time"),
    ]),
    ("slv_pn_product_variants", "product_variants", [
        ("attributes", "json"), ("status", "enum"), ("deleted_at", "time"),
    ]),
    ("slv_pn_product_posts", "product_posts", [
        ("raw_sync_data", "json_post"), ("status", "enum"), ("deleted_at", "time"),
        ("original_price", "price"), ("marketing_price", "price"), ("markup_percent", "price"),
    ]),
    ("slv_pn_product_translations", "product_translations", [("locale", "enum")]),
    ("slv_pn_product_variant_translations", "product_variant_translations", [("locale", "enum")]),
    ("slv_pn_product_post_translations", "product_post_translations", [("locale", "enum")]),
    ("slv_pn_product_attribute_translations", "product_attribute_translations", [("locale", "enum")]),
    ("slv_pn_product_attribute_value_translations", "product_attribute_value_translations", [("locale", "enum")]),
    ("slv_pn_hotel_room_types", "hotel_room_types", [("status", "enum")]),
    ("slv_pn_hotel_rate_plans", "hotel_rate_plans", [("status", "enum"), ("meal_plan", "enum")]),
]


def show(title, rows):
    print(f"\n## {title}")
    if not rows:
        print("(0 rows)")
        return
    headers = list(rows[0].asDict().keys())
    print("\t".join(headers))
    for row in rows[:LIMIT]:
        values = row.asDict()
        print("\t".join("" if values[name] is None else str(values[name]) for name in headers))


def kind_expr(raw):
    text = F.trim(raw.cast("string"))
    return (
        F.when(raw.isNull(), "null")
        .when(text == "", "blank")
        .when(text.startswith("{"), "object")
        .when(text.startswith("["), "array")
        .otherwise("other")
    )


def price_class(raw):
    text = F.trim(raw.cast("string"))
    numeric = text.rlike(r"^-?[0-9]+(\.[0-9]+)?$")
    return (
        F.when(raw.isNull(), "null")
        .when(text == "", "blank")
        .when(numeric, "numeric_text")
        .when(text.rlike(r"^[A-Za-z0-9+/]+={0,2}$") & (F.length(text) >= 4), "base64_like")
        .otherwise("other")
    )


def time_class(raw):
    text = F.trim(raw.cast("string"))
    return (
        F.when(raw.isNull(), "null")
        .when(text == "", "blank")
        .when(text.rlike(r"^[0-9]{10}$"), "digits_10")
        .when(text.rlike(r"^[0-9]{13}$"), "digits_13")
        .when(text.rlike(r"^[0-9]+$"), "digits_other")
        .when(text.rlike(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}"), "timestamp_text")
        .otherwise("other")
    )


def grouped(df, label_col, title):
    rows = (
        df.groupBy(label_col.alias("class"))
        .count()
        .orderBy(F.desc("count"))
        .limit(LIMIT)
        .collect()
    )
    show(title, rows)


def json_flags(raw):
    def present(path):
        return F.get_json_object(raw, path).isNotNull()

    return F.concat_ws(
        ",",
        F.when(present("$.holiday_product_post_id"), "holiday_product_post_id"),
        F.when(present("$.translations"), "translations"),
        F.when(present("$.translations[0].languageCode"), "translations_0_languageCode"),
        F.when(present("$.translations[0].shortDescription"), "translations_0_shortDescription"),
        F.when(present("$.tags"), "tags"),
        F.when(present("$.tags[0].label"), "tags_0_label"),
        F.when(present("$.tags[0].code"), "tags_0_code"),
    )


def inspect(df, column, kind, title):
    raw = F.col(column)
    if kind == "json":
        grouped(df, kind_expr(raw), title + " kind")
        keys = F.array_join(F.array_sort(F.map_keys(F.from_json(raw.cast("string"), "map<string,string>"))), ",")
        grouped(df, keys, title + " object_keys")
    elif kind == "json_post":
        grouped(df, kind_expr(raw), title + " kind")
        keys = F.array_join(F.array_sort(F.map_keys(F.from_json(raw.cast("string"), "map<string,string>"))), ",")
        grouped(df, keys, title + " object_keys")
        grouped(df, json_flags(raw.cast("string")), title + " paths")
        codes = F.get_json_object(raw.cast("string"), "$.translations[0].languageCode")
        grouped(df, codes, title + " translations_0_languageCode")
    elif kind == "price":
        grouped(df, price_class(raw), title)
    elif kind == "time":
        grouped(df, time_class(raw), title)
    else:
        grouped(df, F.trim(raw.cast("string")), title)


def project(table, columns):
    listed = ", ".join(f"`{column}`" for column in columns)
    return spark.sql(f"SELECT {listed} FROM {table}")


def run_inspect(df, column, kind, title):
    try:
        inspect(df, column, kind, title)
    except Exception as exc:
        if "PARSE_DATETIME" not in str(exc) and "SparkUpgradeException" not in type(exc).__name__:
            print(f"\n## {title}")
            print(f"ERROR {type(exc).__name__}: {exc}")
            return
        spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")
        print(f"\n## {title}")
        print("WARN timeParserPolicy=LEGACY")
        try:
            inspect(df, column, kind, title)
        except Exception as again:
            print(f"ERROR {type(again).__name__}: {again}")


print("## silver_counts")
print("table\trows")
empty_sources = []
for silver_name, source_name, checks in SPECS:
    full_name = f"{SILVER}.{silver_name}"
    detail = spark.sql(f"DESCRIBE DETAIL {full_name}").collect()[0].asDict()
    count = detail.get("numRecords")
    print(f"{silver_name}\t{count}")
    if count == 0:
        empty_sources.append(source_name)
        continue
    frame = project(full_name, [column for column, _kind in checks])
    for column, kind in checks:
        run_inspect(frame, column, kind, f"{silver_name}.{column}")

if empty_sources:
    print("\n## bronze_fallback")
    print("sources\t" + ",".join(empty_sources))
    raw = spark.table(BRONZE).select("source", "op", "before", "after")
    source_table = F.get_json_object(F.col("source").cast("string"), "$.table")
    payload = F.when(F.col("op") == F.lit("d"), F.col("before")).otherwise(F.col("after"))
    bronze = raw.filter(source_table.isin(empty_sources)).select(
        source_table.alias("src_table"), payload.cast("string").alias("payload"),
    )
    grouped(bronze, F.col("src_table"), "bronze rows by src_table")
    for silver_name, source_name, checks in SPECS:
        if source_name not in empty_sources:
            continue
        one = bronze.filter(F.col("src_table") == F.lit(source_name))
        for column, kind in checks:
            extracted = one.withColumn(column, F.get_json_object(F.col("payload"), f"$.{column}"))
            inspect(extracted, column, kind, f"bronze.{source_name}.{column}")
else:
    print("\n## bronze_fallback")
    print("skipped")
