# Probe P4 — khóa review và ảnh, chỉ đếm.
# Môi trường: Fabric DEV, notebook Spark, chỉ đọc lh_vv_bronze.
# Phạm vi: lower(trim(source_name)) = 'google'.
# Lưu stdout vào evidence/results/P4_child_keys.md.
# Đạt khi review_key_differ = 0, name khác photo_api_uri = 0, không trùng name, không thiếu phần khóa.
# Không in giá trị.

import hashlib
import json

import pandas as pd
from pyspark.sql import functions as F
from pyspark.sql.types import LongType, StringType, StructField, StructType

TABLE = "lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream"
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


def _sha(source_name, source_id, left, right):
    if left is None or right is None:
        return None
    blob = f"{source_name or ''}{source_id or ''}{left}{right}".encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def _bump(counts, name, outcome, n=1):
    key = (name, outcome)
    counts[key] = counts.get(key, 0) + n


def _text(value):
    if isinstance(value, dict):
        return value.get("text")
    return value


def classify_partition(iterator):
    for pdf in iterator:
        counts = {}
        for raw_text, norm_text, source_name, source_id in zip(
            pdf["raw_payload"].tolist(),
            pdf["normalized_payload"].tolist(),
            pdf["source_name"].tolist(),
            pdf["source_id"].tolist(),
        ):
            raw = _parse(raw_text)
            norm = _parse(norm_text)
            if raw is None or norm is None:
                continue
            reviews = raw.get("reviews") if isinstance(raw.get("reviews"), list) else []
            old = norm.get("poi_review") if isinstance(norm.get("poi_review"), list) else []
            _bump(counts, "review_count", "equal" if len(reviews) == len(old) else "differ")
            for index in range(min(len(reviews), len(old))):
                new = reviews[index] if isinstance(reviews[index], dict) else {}
                prev = old[index] if isinstance(old[index], dict) else {}
                author = (new.get("authorAttribution") or {}).get("displayName") if isinstance(new.get("authorAttribution"), dict) else None
                pairs = {
                    "author_name": (prev.get("author_name"), author),
                    "time": (prev.get("time"), new.get("publishTime")),
                    "rating": (prev.get("rating"), new.get("rating")),
                    "text": (prev.get("text"), _text(new.get("text"))),
                }
                for name, (left, right) in pairs.items():
                    if left is None and right is None:
                        _bump(counts, name, "both_null")
                    elif left is None or right is None:
                        _bump(counts, name, "null_side")
                    elif left == right:
                        _bump(counts, name, "equal")
                    else:
                        _bump(counts, name, "differ")
                old_key = _sha(source_name, source_id, prev.get("author_name"), prev.get("time"))
                new_key = _sha(source_name, source_id, author, new.get("publishTime"))
                if new_key is None:
                    _bump(counts, "review_key", "new_key_null_parts")
                elif old_key == new_key:
                    _bump(counts, "review_key", "equal")
                else:
                    _bump(counts, "review_key", "differ")
            names = []
            for item in reviews:
                if not isinstance(item, dict):
                    names.append(None)
                    continue
                author = (item.get("authorAttribution") or {}).get("displayName") if isinstance(item.get("authorAttribution"), dict) else None
                names.append(_sha(source_name, source_id, author, item.get("publishTime")))
            present = [name for name in names if name is not None]
            if len(present) != len(set(present)):
                _bump(counts, "review_key", "dup_within_doc")
            photos = raw.get("photos") if isinstance(raw.get("photos"), list) else []
            media = norm.get("poi_media") if isinstance(norm.get("poi_media"), list) else []
            _bump(counts, "raw_photo_size", str(len(photos)))
            _bump(counts, "norm_media_size", str(len(media)))
            photo_names = []
            for index, photo in enumerate(photos):
                if not isinstance(photo, dict) or photo.get("name") is None:
                    _bump(counts, "photo_name", "null")
                    photo_names.append(None)
                else:
                    photo_names.append(photo.get("name"))
                width = photo.get("widthPx") if isinstance(photo, dict) else None
                height = photo.get("heightPx") if isinstance(photo, dict) else None
                _bump(counts, "widthPx", "integer" if isinstance(width, int) and not isinstance(width, bool) else "other")
                _bump(counts, "heightPx", "integer" if isinstance(height, int) and not isinstance(height, bool) else "other")
            if len([name for name in photo_names if name is not None]) != len(set(name for name in photo_names if name is not None)):
                _bump(counts, "photo_name", "dup_within_doc")
            for index, item in enumerate(media):
                if not isinstance(item, dict):
                    continue
                raw_name = photo_names[index] if index < len(photo_names) else None
                if item.get("photo_api_uri") == raw_name:
                    _bump(counts, "photo_api_uri", "equal")
                else:
                    _bump(counts, "photo_api_uri", "differ")
                if item.get("display_order") == index + 1:
                    _bump(counts, "display_order", "equal_index_plus_1")
                else:
                    _bump(counts, "display_order", "differ")
        rows = [{"check_name": name, "outcome": outcome, "n": n} for (name, outcome), n in sorted(counts.items())]
        yield pd.DataFrame(rows, columns=["check_name", "outcome", "n"])


src = spark.sql(
    f"""
    SELECT raw_payload, normalized_payload, source_name, source_id
    FROM {TABLE}
    WHERE lower(trim(source_name)) = 'google'
    """
)

print("== child key counts ==")
(
    src.mapInPandas(classify_partition, OUT)
    .groupBy("check_name", "outcome")
    .agg(F.sum("n").alias("n"))
    .orderBy("check_name", "outcome")
    .show(200, truncate=False)
)
