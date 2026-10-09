"""Contract of the 3P L1 registry and extract notebook after the raw-payload redesign."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DROPPED = (
    "slv_3p_poi_price",
    "slv_3p_poi_raw_data",
    "slv_3p_poi_content",
    "slv_3p_poi_enrichment",
    "slv_3p_poi_review_i18n",
)
TOP_KEYS = {
    "accommodation_type", "awards", "business_category", "business_sector", "country_code",
    "created_at", "extra_info", "facilities", "language_code", "operating_status", "partner_id",
    "poi_address", "poi_amenity", "poi_amenity_schema", "poi_contact", "poi_content", "poi_id",
    "poi_media", "poi_name", "poi_name_normalized", "poi_opening_hours", "poi_price", "poi_rating",
    "poi_review", "policies", "price_level", "raw_data", "slug", "slug_history", "source",
    "source_id", "star_rating", "subcategory_tags", "types",
}
EXPECTED = {
    "slv_3p_poi": (21, 15),
    "slv_3p_poi_address": (21, 20),
    "slv_3p_poi_contact": (8, 5),
    "slv_3p_poi_opening_hours": (7, 7),
    "slv_3p_poi_policy": (2, 2),
    "slv_3p_poi_rating": (5, 3),
    "slv_3p_poi_amenity": (3, 3),
    "slv_3p_poi_review": (8, 8),
    "slv_3p_poi_media": (18, 15),
}
FORBIDDEN = {"_lang", "_langs", "_align", "extra_info"}


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _text(nb: dict) -> str:
    return "\n".join("".join(cell["source"]) for cell in nb["cells"])


def _cell_text(cell: dict) -> str:
    return "".join(cell["source"])


def _configs():
    nb = _notebook("NB_CREATE_DDL.ipynb")
    cell = next(c for c in nb["cells"] if "TABLE_CONFIGS_3P = [" in _cell_text(c))
    ns: dict = {}
    exec(_cell_text(cell), ns)  # noqa: S102 - cell is project source, no Spark
    return ns["TABLE_CONFIGS_3P"]


def test_registry_shape():
    configs = _configs()
    assert len(configs) == 9
    columns = [(table, name, spec) for table in configs for name, spec in table["columns"].items()]
    assert len(columns) == 93
    assert sum(1 for _, _, spec in columns if spec.get("active") is False) == 15
    assert [table["target_table"] for table in configs] == list(EXPECTED)
    for table in configs:
        total, active = EXPECTED[table["target_table"]]
        specs = list(table["columns"].values())
        assert len(specs) == total
        assert sum(1 for spec in specs if spec.get("active") is not False) == active


def test_keys_and_open_now():
    configs = {table["target_table"]: table for table in _configs()}
    poi = configs["slv_3p_poi"]["columns"]["poi_id"]
    assert poi["rule"] == "HASH_MD5_UUID"
    assert poi["path"] == "_doc.source_name,_doc.source_id"
    review = configs["slv_3p_poi_review"]["columns"]["review_id"]
    assert review["rule"] == "HASH_SHA256"
    media = configs["slv_3p_poi_media"]["columns"]["media_dedup_key"]
    assert media["rule"] == "HASH_SHA256_PIPE"
    assert configs["slv_3p_poi_opening_hours"]["columns"]["open_now"]["type"] == "boolean"
    assert set(configs["slv_3p_poi_amenity"]["columns"]) == {
        "poi_id", "amenity_schema_json", "ext_attributes_json",
    }


def test_paths_are_structural():
    for table in _configs():
        source = table["source_table"].split(".", 1)[0]
        if source != "$":
            assert source in TOP_KEYS
        for name, spec in table["columns"].items():
            for part in spec["path"].split(","):
                head = part.strip().split(".", 1)[0]
                assert head not in FORBIDDEN
                if table["target_table"] == "slv_3p_poi" and head not in {"_doc", "$"}:
                    assert head in TOP_KEYS, name


def test_extract_notebook_has_no_language_contract():
    nb = _notebook("NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb")
    params = next(c for c in nb["cells"] if "THAM SỐ" in _cell_text(c) or "THAM SO" in _cell_text(c))
    text = _cell_text(params)
    for name in ("langs", "lang_object_path", "lang_map_path", "lang_field"):
        assert f"{name} " not in text and f"{name}=" not in text
    whole = _text(nb)
    assert 'EXTRACT_MODES = ("DOC", "DOC_ARRAY")' in whole or "EXTRACT_MODES  = (\"DOC\", \"DOC_ARRAY\")" in whole
    for banned in ("lang_entries", "LANG_MODES", "_lang_entries"):
        assert banned not in whole


def test_deactivation_list():
    nb = _notebook("NB_CREATE_DDL.ipynb")
    cell = next(
        c for c in nb["cells"]
        if "DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config" in _cell_text(c)
        and "DELETE FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry" in _cell_text(c)
    )
    text = _cell_text(cell)
    for name in DROPPED:
        assert text.count(f"'{name}'") == 2
    assert "slv_3p_poi_policy" not in text
    assert "SET is_active = 0" not in text
    seed = next(c for c in nb["cells"] if "( 1, 'slv_3p_poi'" in _cell_text(c))
    seed_text = _cell_text(seed)
    for name in DROPPED:
        assert name not in seed_text
