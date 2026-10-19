# Environment: Fabric DEV. Notebook Spark gắn lakehouse lh_vv_silver. Chỉ đọc, không ghi.
# Prerequisite: lh_vv_silver.dbo.slv_pn_business_services và slv_pn_business_service_i18ns.
# Steps: 1) Mở notebook tạm trên DEV. 2) Dán cả file. 3) Run all.
# Pass: in COUNTS rồi tối đa 50 dòng KEYS/PATHS. Không địa chỉ, tên, secret.
# Paste: .ai/tasks/20261019-poi-entity-non-enrich/evidence/results/partner-json-shape.txt
# Resolves: shape address và amentities; grain locale=vi. Fail nếu thiếu cột address.

import json

from pyspark.sql import functions as F
from pyspark.sql.types import ArrayType, StringType

SVCS = "lh_vv_silver.dbo.slv_pn_business_services"
I18N = "lh_vv_silver.dbo.slv_pn_business_service_i18ns"
ADDR_KEYS = (
    "full_address", "address_line1", "address_line2", "street", "ward",
    "district", "city", "state", "zip", "country",
)
LIMIT = 50


def _kind(node):
    if isinstance(node, dict):
        return "object"
    if isinstance(node, list):
        return "array"
    if isinstance(node, str):
        return "string"
    if isinstance(node, bool):
        return "bool"
    if isinstance(node, (int, float)):
        return "number"
    if node is None:
        return "null"
    return "other"


def _parse(raw):
    if raw is None:
        return "null", None
    if not isinstance(raw, str):
        return "not_string", None
    if raw.strip() == "":
        return "blank", None
    try:
        doc = json.loads(raw)
    except Exception:
        return "unparsed", None
    if isinstance(doc, str):
        try:
            doc = json.loads(doc)
        except Exception:
            return "root_string", None
        return "double_" + _kind(doc), doc
    return "root_" + _kind(doc), doc


def _nonempty(value):
    if value is None or value == "":
        return False
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False
    return True


def _address_tokens(raw):
    label, doc = _parse(raw)
    tokens = ["shape|" + label]
    if not isinstance(doc, dict):
        return tokens
    for key in ADDR_KEYS:
        if key not in doc:
            tokens.append("known|" + key + "|absent")
        else:
            flag = "nonempty" if _nonempty(doc[key]) else "empty"
            tokens.append("known|" + key + "|" + flag + "|" + _kind(doc[key]))
    for key in doc:
        if key not in ADDR_KEYS:
            tokens.append("extra|" + str(key) + "|" + _kind(doc[key]))
    return tokens


def _category_tokens(raw):
    label, doc = _parse(raw)
    if doc is None:
        return ["shape|" + label]
    found = []

    def walk(node, path, budget):
        if budget[0] <= 0:
            return
        if isinstance(node, dict):
            for key, value in node.items():
                nxt = key if not path else path + "." + key
                if key == "main_category":
                    budget[0] -= 1
                    found.append(nxt + "|" + _kind(value))
                walk(value, nxt, budget)
        elif isinstance(node, list):
            for value in node:
                walk(value, path + "[]", budget)

    walk(doc, "", [20])
    if not found:
        return ["shape|" + label, "main|none"]
    mark = "main|n" + str(len(found))
    if len(found) >= 20:
        mark += "|truncated"
    return ["shape|" + label, mark] + ["path|" + item for item in found]


address_udf = F.udf(_address_tokens, ArrayType(StringType()))
category_udf = F.udf(_category_tokens, ArrayType(StringType()))


def _print_counts(title, df, token_col="token"):
    print("== " + title)
    rows = df.groupBy(token_col).count().orderBy(F.desc("count"), token_col).limit(LIMIT + 1).collect()
    extra = len(rows) > LIMIT
    for row in rows[:LIMIT]:
        print(f"{row['count']}\t{row[token_col]}")
    if extra:
        print("TRUNCATED\tmore than " + str(LIMIT) + " groups")


def main():
    svc_cols = set(spark.table(SVCS).columns)
    i18n_cols = set(spark.table(I18N).columns)
    print("== COLUMNS")
    print("services_address\t" + str("address" in svc_cols))
    print("services_amentities\t" + str("amentities" in svc_cols))
    print("services_amenities\t" + str("amenities" in svc_cols))
    print("services_deleted\t" + str("deleted" in svc_cols))
    print("i18n_locale\t" + str("locale" in i18n_cols))
    print("i18n_business_service_id\t" + str("business_service_id" in i18n_cols))
    if "address" not in svc_cols:
        raise RuntimeError("missing slv_pn_business_services.address")

    services = spark.table(SVCS)
    if "deleted" in svc_cols:
        print("== DELETED")
        services.groupBy(F.col("deleted").cast("string").alias("deleted")).count().orderBy("deleted").show(LIMIT, False)

    _print_counts("ADDRESS", services.select(F.explode(address_udf(F.col("address"))).alias("token")))
    amen_col = "amentities" if "amentities" in svc_cols else "amenities"
    if amen_col not in svc_cols:
        print("== AMENITIES")
        print("0\tmissing_both_spellings")
    else:
        print("amenity_column\t" + amen_col)
        _print_counts("AMENITIES", services.select(F.explode(category_udf(F.col(amen_col))).alias("token")))

    print("== I18N")
    i18n = spark.table(I18N)
    vi = i18n.where(F.lower(F.trim(F.col("locale"))) == F.lit("vi"))
    vi_ids = vi.select(F.col("business_service_id").alias("vi_id")).distinct()
    multi = vi.groupBy("business_service_id").count().where(F.col("count") > 1)
    joined = services.join(vi_ids, services["id"] == vi_ids["vi_id"], "left")
    print("i18n_rows\t" + str(i18n.count()))
    print("vi_rows\t" + str(vi.count()))
    print("vi_ids\t" + str(vi_ids.count()))
    print("multi_vi_ids\t" + str(multi.count()))
    print("services\t" + str(services.count()))
    print("services_with_vi\t" + str(joined.where(F.col("vi_id").isNotNull()).count()))
    print("== LOCALES")
    i18n.groupBy(F.lower(F.trim(F.col("locale"))).alias("locale")).count().orderBy(F.desc("count")).show(LIMIT, False)


main()
