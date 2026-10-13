"""Contract of the 3P L1 registry and extract notebook after the raw-payload redesign."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DROPPED = (
    "slv_3p_poi_raw_data",
    "slv_3p_poi_content",
    "slv_3p_poi_enrichment",
    "slv_3p_poi_review_i18n",
)
EXPECTED = {
    "slv_3p_poi": 10,
    "slv_3p_poi_address": 12,
    "slv_3p_poi_contact": 3,
    "slv_3p_poi_price": 5,
    "slv_3p_poi_opening_hours": 4,
    "slv_3p_poi_rating": 3,
    "slv_3p_poi_amenity": 2,
    "slv_3p_poi_review": 7,
    "slv_3p_poi_media": 6,
}
FORBIDDEN = {"_lang", "_langs", "_align"}


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
    assert len(columns) == 52
    assert sum(1 for _, _, spec in columns if spec.get("active") is False) == 0
    assert [table["target_table"] for table in configs] == list(EXPECTED)
    for table in configs:
        assert len(table["columns"]) == EXPECTED[table["target_table"]]


def test_keys_and_open_now():
    configs = {table["target_table"]: table for table in _configs()}
    poi = configs["slv_3p_poi"]["columns"]["poi_id"]
    assert poi["rule"] == "HASH_MD5_UUID"
    assert poi["path"] == "_doc.source_name,_doc.source_id"
    assert configs["slv_3p_poi"]["columns"]["primary_type"]["path"] == "primaryType"
    review = configs["slv_3p_poi_review"]["columns"]["review_id"]
    assert review["rule"] == "HASH_SHA256"
    assert "publishTime" in review["path"]
    media = configs["slv_3p_poi_media"]["columns"]["media_dedup_key"]
    assert media["rule"] == "HASH_SHA256_PIPE"
    assert configs["slv_3p_poi_opening_hours"]["columns"]["open_now"]["rule"] == "COALESCE"
    assert set(configs["slv_3p_poi_amenity"]["columns"]) == {"poi_id", "source_flags_json"}
    flags = configs["slv_3p_poi_amenity"]["columns"]["source_flags_json"]
    keys = []
    for member in flags["arg"]["members"]:
        if "keys" in member:
            keys.extend(member["keys"])
        else:
            keys.append(member["key"])
    assert [part.strip() for part in flags["path"].split(",")] == keys


def test_paths_are_structural():
    for table in _configs():
        for spec in table["columns"].values():
            for part in spec["path"].split(","):
                head = part.strip().split(".", 1)[0]
                assert head not in FORBIDDEN


def test_extract_notebook_has_no_language_contract():
    nb = _notebook("NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb")
    params = next(c for c in nb["cells"] if "THAM SỐ" in _cell_text(c) or "THAM SO" in _cell_text(c))
    text = _cell_text(params)
    for name in ("langs", "lang_object_path", "lang_map_path", "lang_field"):
        assert f"{name} " not in text and f"{name}=" not in text
    whole = _text(nb)
    assert 'EXTRACT_MODES = ("DOC", "DOC_ARRAY")' in whole or "EXTRACT_MODES  = (\"DOC\", \"DOC_ARRAY\")" in whole
    for banned in ("lang_entries", "LANG_MODES", "_lang_entries", "KNOWN_TOP_KEYS", "WATCH_BLOCKS"):
        assert banned not in whole
    assert 'RAW_PAYLOAD    = "raw_payload"' in whole


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
    assert text.count("'slv_3p_poi_policy'") == 2
    assert "SET is_active = 0" not in text
    seed = next(c for c in nb["cells"] if "( 1, 'slv_3p_poi'" in _cell_text(c))
    seed_text = _cell_text(seed)
    for name in DROPPED:
        assert name not in seed_text
    assert "media_id" not in seed_text
