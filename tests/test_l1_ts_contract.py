"""Registry and notebook contract for L1 UTC timestamps and audit columns."""
import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MS_TABLES = {
    "slv_pn_orders",
    "slv_pn_order_refs",
    "slv_pn_order_item_tickets",
    "slv_pn_order_item_hotels",
    "slv_pn_order_item_flights",
}
ISO = {
    ("slv_pn_order_item_tickets", "usage_date"),
    ("slv_pn_order_item_tickets", "valid_from"),
    ("slv_pn_order_item_tickets", "valid_to"),
    ("slv_pn_order_item_hotels", "check_in_date"),
    ("slv_pn_order_item_hotels", "checkout_date"),
    ("slv_pn_order_item_flights", "departure_time"),
    ("slv_pn_order_item_flights", "arrival_time"),
    ("slv_3p_poi", "source_created_at"),
    ("slv_3p_poi_review", "published_at"),
}


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell(nb: dict, needle: str) -> str:
    return "".join(next(c["source"] for c in nb["cells"] if needle in "".join(c["source"])))


def _partner():
    nb = _notebook("NB_CREATE_DDL.ipynb")
    ns: dict = {}
    exec(_cell(nb, "TABLE_CONFIGS = ["), ns)  # noqa: S102
    return ns["TABLE_CONFIGS"]


def _third():
    nb = _notebook("NB_CREATE_DDL.ipynb")
    ns: dict = {}
    exec(_cell(nb, "TABLE_CONFIGS_3P = ["), ns)  # noqa: S102
    return ns["TABLE_CONFIGS_3P"]


def test_utc_text_truncates_without_rounding():
    moment = datetime(2026, 10, 9, 16, 20, 1, 123999)
    text = moment.strftime("%Y-%m-%dT%H:%M:%S.") + f"{moment.microsecond // 1000:03d}Z"
    assert text == "2026-10-09T16:20:01.123Z"
    lib = _notebook("NB_LIB_EXTRACT_RAWDATA.ipynb")
    assert "dt.microsecond // 1000" in _cell(lib, "def utc_ts_text")


def test_partner_epoch_rules_and_rename():
    for table in _partner():
        names = set(table["columns"])
        assert "created_at" not in names
        assert "updated_at" not in names
        assert "_ingested_at" not in names
        target = table["target_table"]
        for name, spec in table["columns"].items():
            rule = spec.get("rule", "NONE")
            if (target, name) in ISO:
                assert spec["type"] == "timestamp" and rule == "ISO_UTC_TS"
            elif name in {"src_created_at", "src_updated_at"} or name == "expire_at":
                assert spec["type"] == "timestamp"
                expect = "EPOCH_MS_TS" if target in MS_TABLES else "EPOCH_S_TS"
                assert rule == expect, (target, name, rule)
                if name.startswith("src_"):
                    assert spec["path"] == name[len("src_"):]
            elif rule in {"EPOCH_S_TS", "EPOCH_MS_TS", "ISO_UTC_TS"}:
                assert spec["type"] == "timestamp"
                assert rule == "EPOCH_S_TS"
        deleted = table["columns"].get("deleted_at")
        if deleted:
            assert deleted["type"] == "string"
            assert deleted.get("rule", "NONE") == "NONE"


def test_third_party_iso_and_review_key():
    configs = {table["target_table"]: table for table in _third()}
    created = configs["slv_3p_poi"]["columns"]["source_created_at"]
    assert created["path"] == "created_at"
    assert created["type"] == "timestamp" and created["rule"] == "ISO_UTC_TS"
    review = configs["slv_3p_poi_review"]["columns"]
    assert review["time"]["type"] == "string"
    assert review["time"].get("rule", "NONE") == "NONE"
    assert review["published_at"]["path"] == "time"
    assert review["published_at"]["rule"] == "ISO_UTC_TS"
    assert review["review_id"]["rule"] == "HASH_SHA256"
    assert "time" in review["review_id"]["path"]


def test_l1_notebooks_do_not_write_ingested_at():
    for name in (
        "NB_LIB_EXTRACT_RAWDATA.ipynb",
        "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb",
        "NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb",
    ):
        text = "\n".join("".join(c["source"]) for c in _notebook(name)["cells"])
        text = text.replace("_raw_ingested_at", "").replace("raw_ingested_at", "")
        text = text.replace("Không còn `_ingested_at`", "")
        assert "_ingested_at" not in text, name
    merge = _cell(_notebook("NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb"), "def build_merge_sql")
    assert "t.`created_at`" not in merge
    assert '"created_at": clock' in merge
    assert "t.`updated_at`" in merge
