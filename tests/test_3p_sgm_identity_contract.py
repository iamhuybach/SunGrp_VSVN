"""Contract for sgm identity on the Google 3P extract path."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(name: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell["source"]) for cell in nb["cells"])


def _extract() -> str:
    return _text("NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb")


def _configs():
    nb = json.loads((ROOT / "notebooks" / "NB_CREATE_DDL.ipynb").read_text(encoding="utf-8"))
    cell = next(c for c in nb["cells"] if "TABLE_CONFIGS_3P = [" in "".join(c["source"]))
    ns: dict = {}
    exec("".join(cell["source"]), ns)  # noqa: S102
    return ns["TABLE_CONFIGS_3P"]


def test_sources_default_and_fl00_include_sgm():
    assert 'sources                 = "google,sgm"' in _extract()
    pipeline = (ROOT / "pipelines" / "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"
                / "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json").read_text(encoding="utf-8")
    marker = pipeline.find("NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV")
    window = pipeline[marker:marker + 2500]
    assert '"sources":{"value":"google,sgm","type":"string"}' in window
    cms = pipeline.find("NB_EXTRACT_CMS_CDC_BRZ_TO_SLV")
    assert '"value":"google,sgm"' not in pipeline[cms:cms + 2500]


def test_identity_source_only_maps_sgm():
    text = _extract()
    assert "F.broadcast" not in text
    assert 'IDENTITY_SOURCE = {"sgm": "google"}' in text
    assert "F.coalesce(skip, F.lit(False))" in text or "coalesce(valid & src_name.isin(*IDENTITY_SOURCE) & owned, F.lit(False))" in text


def test_identity_key_columns_match_d4b():
    assert 'IDENTITY_KEY_COLUMNS = ("poi_id", "review_id", "media_dedup_key")' in _extract()


def test_google_priority_is_ignore_reason():
    text = _extract()
    assert 'IGNORE_REASONS = ("OUT_OF_SCOPE", "GOOGLE_PRIORITY")' in text


def test_check_config_guards_identity_and_synthetic_cols():
    text = _extract()
    assert "HASH_MD5_UUID" in text
    assert "SYNTHETIC_DOC_COLS" in text
    assert "doc_key_column != \"poi_id\"" in text


def test_registry_key_paths_unchanged():
    configs = {table["target_table"]: table for table in _configs()}
    assert configs["slv_3p_poi"]["columns"]["poi_id"]["path"] == "_doc.source_name,_doc.source_id"
    assert configs["slv_3p_poi_review"]["columns"]["review_id"]["path"].startswith("_doc.source_name,")
    assert configs["slv_3p_poi_media"]["columns"]["media_dedup_key"]["path"].startswith("_doc.source_name,")
    assert configs["slv_3p_poi"]["columns"]["source_name"]["path"] == "_doc.source_name"


def test_merge_guard_takeover_bypass():
    text = _extract()
    assert "s.`_doc__{TAKEOVER_DOC_COL}`" in text
    assert "s.`_crawled_at` > coalesce(t.`_crawled_at`" in text


def test_stale_filter_excludes_takeover():
    assert "not_takeover" in _extract()
    assert "TAKEOVER_DOC_COL" in _extract()


def test_poi_owner_snapshot_version_pinned():
    assert "VERSION AS OF {version}" in _extract()


def test_takeover_state_reset_before_load_state():
    text = _extract()
    reset = text.find("reset_takeover_state(takeover_ids, specs, ctx)")
    load = text.find("state_df = load_state(specs)", reset)
    assert 0 < reset < load


def test_poi_gate_before_children_when_no_takeover():
    text = _extract()
    branch = text.find("if not n_take:")
    poi = text.find("poi_first = ", branch)
    children = text.find("children = ", poi)
    run_poi = text.find("run_tables(poi_first", poi)
    run_children = text.find("run_tables(children", run_poi)
    assert 0 < branch < poi < children < run_poi < run_children
    assert "poi gate: slv_3p_poi failed" in text


def test_poi_table_last_when_takeover():
    text = _extract()
    rest = text.find("rest = [s for s in specs if s.trg_tbl != POI_TABLE]")
    poi = text.find("poi = [s for s in specs if s.trg_tbl == POI_TABLE]", rest)
    assert 0 < rest < poi


def test_entity_maps_sgm_to_google_before_filter():
    text = _text("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb")
    mapped = text.find('SOURCE_AS_GOOGLE = ("sgm",)')
    filtered = text.find('F.lower(F.trim("source_name")) == GOOGLE', mapped)
    assert 0 < mapped < filtered


def test_no_sgm_dictionary_rows():
    for name in ("NB_CREATE_DDL.ipynb", "NB_SETUP_INITIAL_DDL.ipynb", "NB_SETUP_POI_AMENITY.ipynb"):
        assert "sgm" not in _text(name).lower()
