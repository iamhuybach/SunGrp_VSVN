# Probe P3 — so sánh cột normalized với raw trên toàn bộ DEV, chỉ đếm.
# Môi trường: Fabric DEV, notebook Spark, chỉ đọc lh_vv_bronze.
# Phạm vi: lower(trim(source_name)) = 'google', cả hai payload parse được thành object.
# Lưu stdout vào evidence/results/P3_column_equivalence.md.
# Giữ cột khi normalized_only = raw_only = differ = 0.
# Không in giá trị.

import json

import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

TABLE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
ADDRESS_PICK = {
    "house_number": ("longText", ("street_number",)),
    "street": ("longText", ("route",)),
    "ward": ("longText", ("administrative_area_level_2",)),
    "city": ("longText", ("administrative_area_level_1",)),
    "state_province": ("longText", ("administrative_area_level_1",)),
    "postal_code": ("longText", ("postal_code",)),
    "country_code": ("shortText", ("country",)),
}
ADDRESS_FIELDS = (
    "house_number",
    "street",
    "ward",
    "district",
    "city",
    "state_province",
    "country",
    "country_code",
    "postal_code",
    "address_line1",
    "address_line2",
    "short_address",
)

OUT = StructType(
    [
        StructField("check_name", StringType()),
        StructField("outcome", StringType()),
        StructField("n", LongType()),
    ]
)


def _parse(text):
    if text is None or str(text).strip() == "":
        return None
    try:
        obj, end = json.JSONDecoder().raw_decode(str(text).strip())
    except Exception:
        return None
    if not isinstance(obj, dict) or end < len(str(text).strip()):
        return None
    return obj


def _get(obj, path):
    cur = obj
    for part in path.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return None
        cur = cur[part]
    return cur


def _pick(raw, take, tokens):
    comps = raw.get("addressComponents")
    if not isinstance(comps, list):
        return None
    for token in tokens:
        for comp in comps:
            if not isinstance(comp, dict):
                continue
            types = comp.get("types")
            hit = types == token or (isinstance(types, list) and token in types)
            if hit:
                return comp.get(take)
    return None


def _norm_text(value):
    if isinstance(value, str):
        return value
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return format(value, "f").rstrip("0").rstrip(".") if isinstance(value, float) else str(value)
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"))


def _outcome(left, right):
    if left is None and right is None:
        return "both_null"
    if left is None:
        return "raw_only"
    if right is None:
        return "normalized_only"
    same = left == right
    if isinstance(left, str) or isinstance(right, str):
        if str(left).strip() == str(right).strip() and not same:
            return "equal_after_trim"
    if isinstance(left, (int, float)) and isinstance(right, (int, float)) and not isinstance(left, bool) and not isinstance(right, bool):
        if float(left) == float(right) and _norm_text(left) != _norm_text(right):
            return "equal_number_differ_text"
    return "equal" if same else "differ"


def _bump(counts, name, outcome):
    key = (name, outcome)
    counts[key] = counts.get(key, 0) + 1


def classify_partition(iterator):
    for pdf in iterator:
        counts = {}
        for raw_text, norm_text in zip(pdf["raw_payload"].tolist(), pdf["normalized_payload"].tolist()):
            raw = _parse(raw_text)
            norm = _parse(norm_text)
            if raw is None or norm is None:
                continue
            pairs = {
                "poi_name": (_get(norm, "poi_name"), raw.get("displayName")),
                "poi_name_normalized": (
                    _get(norm, "poi_name_normalized"),
                    raw.get("displayName").strip().lower() if isinstance(raw.get("displayName"), str) else None,
                ),
                "types": (_get(norm, "types"), raw.get("types")),
                "subcategory_tags": (_get(norm, "subcategory_tags"), raw.get("types")),
                "operating_status": (
                    _get(norm, "operating_status"),
                    raw.get("businessStatus").strip().lower() if isinstance(raw.get("businessStatus"), str) else None,
                ),
                "full_address": (_get(norm, "poi_address.full_address") if False else _get(_get(norm, "poi_address") or {}, "full_address"), raw.get("formattedAddress")),
                "lat": (_get(_get(norm, "poi_address") or {}, "lat"), _get(raw, "location.latitude")),
                "lng": (_get(_get(norm, "poi_address") or {}, "lng"), _get(raw, "location.longitude")),
                "plus_code": (_get(_get(norm, "poi_address") or {}, "plus_code"), _get(raw, "plusCode.globalCode")),
                "website_url": (_get(_get(norm, "poi_contact") or {}, "website_url"), raw.get("websiteUri")),
                "google_maps_url": (_get(_get(norm, "poi_contact") or {}, "google_maps_url"), raw.get("googleMapsUri")),
                "rating_overall": (_get(_get(norm, "poi_rating") or {}, "rating_overall"), raw.get("rating")),
                "rating_count": (_get(_get(norm, "poi_rating") or {}, "rating_count"), raw.get("userRatingCount")),
                "weekday_text": (
                    _get(_get(norm, "poi_opening_hours") or {}, "weekday_text"),
                    _get(raw, "regularOpeningHours.weekdayDescriptions"),
                ),
            }
            addr = _get(norm, "poi_address") or {}
            for col, (take, tokens) in ADDRESS_PICK.items():
                pairs[col] = (addr.get(col) if isinstance(addr, dict) else None, _pick(raw, take, tokens))
            for name, (left, right) in pairs.items():
                _bump(counts, name, _outcome(left, right))
            comps = raw.get("addressComponents") if isinstance(raw.get("addressComponents"), list) else []
            for col in ADDRESS_FIELDS:
                value = addr.get(col) if isinstance(addr, dict) else None
                if value is None:
                    _bump(counts, "attr_" + col, "normalized_null")
                    continue
                matched = False
                for side in ("longText", "shortText"):
                    for comp in comps:
                        if isinstance(comp, dict) and comp.get(side) == value:
                            types = comp.get("types")
                            token = "+".join(types) if isinstance(types, list) else _jtype_token(types)
                            _bump(counts, "attr_" + col + "_" + side, token)
                            matched = True
                if not matched:
                    _bump(counts, "attr_" + col, "no_component_match")
            price = _get(norm, "poi_price") or {}
            start = _get(raw, "priceRange.startPrice") or {}
            end = _get(raw, "priceRange.endPrice") or {}
            if isinstance(price, dict):
                _bump(counts, "currency", _outcome(price.get("currency"), start.get("currencyCode") if isinstance(start, dict) else None))
                _bump(counts, "price_min", _outcome(price.get("price_min"), start.get("units") if isinstance(start, dict) else None))
                _bump(counts, "price_max", _outcome(price.get("price_max"), end.get("units") if isinstance(end, dict) else None))
            hours = _get(norm, "poi_opening_hours") or {}
            if isinstance(hours, dict):
                _bump(counts, "is_24_7", "null" if hours.get("is_24_7") is None else str(bool(hours.get("is_24_7"))).lower())
                closed = hours.get("is_temporarily_closed")
                status = raw.get("businessStatus")
                if closed is True and status == "CLOSED_TEMPORARILY":
                    _bump(counts, "is_temporarily_closed", "true_and_status")
                elif closed is True:
                    _bump(counts, "is_temporarily_closed", "true_other_status")
                elif closed is False:
                    _bump(counts, "is_temporarily_closed", "false")
                else:
                    _bump(counts, "is_temporarily_closed", "null")
            for label, value in (
                ("norm_secondary_hours", _get(hours if isinstance(hours, dict) else {}, "secondary_hours")),
                ("norm_poi_id", norm.get("poi_id")),
                ("norm_facilities", norm.get("facilities")),
                ("norm_created_at", norm.get("created_at")),
                ("norm_amenity_schema", _get(_get(norm, "poi_amenity") or {}, "amenity_schema")),
                ("norm_ext_attributes", _get(_get(norm, "poi_amenity") or {}, "ext_attributes")),
            ):
                _bump(counts, label, "null" if value is None else "non_null")
        rows = [{"check_name": name, "outcome": outcome, "n": n} for (name, outcome), n in sorted(counts.items())]
        yield pd.DataFrame(rows, columns=["check_name", "outcome", "n"])


def _jtype_token(value):
    if isinstance(value, list):
        return "+".join(str(item) for item in value)
    return "other"


src = spark.sql(
    f"""
    SELECT raw_payload, normalized_payload
    FROM {TABLE}
    WHERE lower(trim(source_name)) = 'google'
    """
)

print("== equivalence counts ==")
(
    src.mapInPandas(classify_partition, OUT)
    .groupBy("check_name", "outcome")
    .agg(F.sum("n").alias("n"))
    .orderBy("check_name", "outcome")
    .show(500, truncate=False)
)
