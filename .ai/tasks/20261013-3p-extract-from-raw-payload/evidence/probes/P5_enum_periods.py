# Probe P5 — enum priceLevel, hình period, và open_now.
# Môi trường: Fabric DEV, notebook Spark, chỉ đọc lh_vv_bronze.
# Phạm vi: lower(trim(source_name)) = 'google'.
# Được in token enum và tên khóa. Không in giá trị địa chỉ, review, URL.
# Lưu stdout vào evidence/results/P5_enum_periods.md.

import json

import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

TABLE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
FIELDS = (
    ("day_of_week", ("open", "day")),
    ("open_hour", ("open", "hour")),
    ("open_minute", ("open", "minute")),
    ("close_day", ("close", "day")),
    ("close_hour", ("close", "hour")),
    ("close_minute", ("close", "minute")),
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


def _as_int(value):
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, float) and value.is_integer():
        return int(value)
    if isinstance(value, str) and value.strip().lstrip("-").isdigit():
        return int(value.strip())
    return None


def _project(periods, keep_nulls):
    rows = []
    for period in periods or []:
        if not isinstance(period, dict):
            continue
        row = {}
        for name, (side, leaf) in FIELDS:
            container = period.get(side) if isinstance(period.get(side), dict) else {}
            value = _as_int(container.get(leaf))
            if value is None and not keep_nulls:
                continue
            row[name] = value
        rows.append(row)
    return rows


def _norm_periods(hours):
    rows = []
    for period in (hours or {}).get("periods") or []:
        if not isinstance(period, dict):
            continue
        row = {}
        for key, value in period.items():
            coerced = _as_int(value)
            row[key] = coerced if coerced is not None else value
        rows.append(row)
    return rows


def _bump(counts, name, outcome, n=1):
    key = (name, str(outcome))
    counts[key] = counts.get(key, 0) + n


def classify_partition(iterator):
    for pdf in iterator:
        counts = {}
        for raw_text, norm_text in zip(pdf["raw_payload"].tolist(), pdf["normalized_payload"].tolist()):
            raw = _parse(raw_text)
            norm = _parse(norm_text)
            if raw is None or norm is None:
                continue
            token = raw.get("priceLevel")
            token_name = "null" if token is None else str(token).strip()
            price = norm.get("poi_price") if isinstance(norm.get("poi_price"), dict) else {}
            _bump(counts, "priceLevel", token_name + "|poi_price=" + str(price.get("price_level")) + "|top=" + str(norm.get("price_level")))
            regular = raw.get("regularOpeningHours") if isinstance(raw.get("regularOpeningHours"), dict) else {}
            periods = regular.get("periods") if isinstance(regular.get("periods"), list) else []
            missing_close = 0
            for period in periods:
                if not isinstance(period, dict) or "close" not in period or period.get("close") is None:
                    missing_close += 1
            _bump(counts, "periods_missing_close", str(missing_close > 0), missing_close if missing_close else 0)
            if missing_close:
                hours = norm.get("poi_opening_hours") if isinstance(norm.get("poi_opening_hours"), dict) else {}
                for period in hours.get("periods") or []:
                    if isinstance(period, dict):
                        _bump(counts, "norm_period_keys_when_raw_close_missing", ",".join(sorted(period.keys())))
            hours = norm.get("poi_opening_hours") if isinstance(norm.get("poi_opening_hours"), dict) else {}
            observed = _norm_periods(hours)
            if observed:
                _bump(counts, "norm_period_key_order", ",".join(observed[0].keys()))
                for key, value in observed[0].items():
                    _bump(counts, "norm_period_field_type_" + key, type(value).__name__)
            _bump(counts, "periods_projection", "keep_nulls_true" if observed == _project(periods, True) else "keep_nulls_true_differ")
            _bump(counts, "periods_projection", "keep_nulls_false" if observed == _project(periods, False) else "keep_nulls_false_differ")
            current = raw.get("currentOpeningHours") if isinstance(raw.get("currentOpeningHours"), dict) else None
            current_open = None if current is None else current.get("openNow")
            regular_open = regular.get("openNow") if regular else None
            norm_open = hours.get("open_now") if isinstance(hours, dict) else None
            if current is None:
                _bump(counts, "open_now", "current_absent_regular_equal" if regular_open == norm_open else "current_absent_regular_differ")
            elif current_open == regular_open:
                _bump(counts, "open_now", "booleans_equal")
            else:
                _bump(counts, "open_now", "booleans_differ")
            if norm_open is not None:
                if current_open == norm_open:
                    _bump(counts, "open_now_vs_norm", "current_equal")
                elif regular_open == norm_open:
                    _bump(counts, "open_now_vs_norm", "regular_equal")
                else:
                    _bump(counts, "open_now_vs_norm", "neither_equal")
        rows = [{"check_name": name, "outcome": outcome, "n": n} for (name, outcome), n in sorted(counts.items())]
        yield pd.DataFrame(rows, columns=["check_name", "outcome", "n"])


src = spark.sql(
    f"""
    SELECT raw_payload, normalized_payload
    FROM {TABLE}
    WHERE lower(trim(source_name)) = 'google'
    """
)

print("== enum, periods, open_now ==")
(
    src.mapInPandas(classify_partition, OUT)
    .groupBy("check_name", "outcome")
    .agg(F.sum("n").alias("n"))
    .orderBy("check_name", "outcome")
    .show(200, truncate=False)
)
