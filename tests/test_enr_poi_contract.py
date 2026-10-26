"""Contract checks for the gld_enr append flow. No Spark."""
import ast
import json
import re
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INFO = [
    ("poi_id", "STRING NOT NULL"), ("source_name", "STRING"), ("source_id", "STRING"),
    ("language_code", "STRING"), ("poi_name", "STRING"), ("poi_name_normalized", "STRING"),
    ("types", "STRING"), ("operating_status", "STRING"), ("primary_type", "STRING"),
    ("website_url", "STRING"), ("house_number", "STRING"), ("street", "STRING"),
    ("ward", "STRING"), ("city", "STRING"),
    ("full_address", "STRING"), ("lat", "DOUBLE"),
    ("lng", "DOUBLE"), ("business_sector", "STRING"), ("business_category", "STRING"),
    ("business_category_vi", "STRING"), ("category_group", "STRING"),
    ("range_low_min", "INT"), ("range_high_min", "INT"), ("avg_range_min", "INT"),
    ("candidate_best_time_code", "STRING"), ("canonical_candidate", "STRING"),
    ("rating", "DECIMAL(4,2)"), ("user_rating_count", "BIGINT"), ("price_level", "INT"),
    ("opening_hours_text", "STRING"), ("review_json", "STRING"), ("time_to_spend", "STRING"),
    ("best_time", "STRING"), ("cost", "BIGINT"), ("cost_vnd", "STRING"), ("service_flag", "STRING"),
    ("is_enriched_multi_lang", "BOOLEAN"), ("is_enriched_destination", "BOOLEAN"),
    ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
]
COORD = [
    ("poi_id", "STRING NOT NULL"), ("name", "STRING"), ("short_address", "STRING"),
    ("ward", "STRING"), ("district", "STRING"), ("province_name", "STRING"),
    ("destination_name", "STRING"), ("lat", "DOUBLE"), ("lng", "DOUBLE"),
    ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
]
REVIEW = [
    ("review_id", "STRING NOT NULL"), ("poi_id", "STRING"), ("rating", "DECIMAL(3,1)"),
    ("review_text", "STRING"), ("review_date", "TIMESTAMP"), ("review_updated_at", "TIMESTAMP"),
    ("is_enriched_multi_lang", "BOOLEAN"),
    ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
]
DROPPED = ("description", "title", "positive", "negative", "response_text", "source_review_id")
INFO_DROPPED = (
    "subcategory_tags", "short_address", "destination_context", "best_time_type",
    "best_time_from_month", "best_time_to_month", "userRatingCount", "priceLevel", "types_json",
)
EDGES_OFF = [
    ("slv_3p_poi", "gld_enr_poi_info"),
    ("slv_3p_poi_address", "gld_enr_poi_info"),
    ("slv_3p_poi_contact", "gld_enr_poi_info"),
    ("slv_3p_poi", "gld_enr_poi_coordinate"),
    ("slv_3p_poi_address", "gld_enr_poi_coordinate"),
    ("slv_pn_poi", "gld_enr_poi_coordinate"),
]
EDGES_ON = [
    (1, "slv_poi_entity_non_enrich", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (2, "slv_poi_amenity", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (3, "slv_pn_business_service_i18ns", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
]
INFO_ACTIVE = (
    "slv_poi_entity_non_enrich", "slv_poi_amenity", "slv_3p_poi_rating", "slv_3p_poi_price",
    "slv_3p_poi_opening_hours", "slv_3p_poi_review", "slv_pn_business_service_i18ns",
)
INFO_FLAGS = ("is_enriched_multi_lang", "is_enriched_destination")
INFO_REMOVED = ("district", "destination_name")
REVIEW_FLAGS = ("is_enriched_multi_lang",)
LANDING = {
    "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang": [
        ("poi_id", "STRING NOT NULL"), ("lang", "STRING"), ("time_to_spend", "STRING"), ("best_time", "STRING"),
        ("cost_vnd", "STRING"), ("description", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
    "lh_vv_silver.dbo.slv_enr_poi_destination": [
        ("poi_id", "STRING NOT NULL"), ("street", "STRING"), ("ward", "STRING"), ("district", "STRING"),
        ("city", "STRING"), ("full_address", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
    "lh_vv_silver.dbo.slv_enr_poi_review_multi_lang": [
        ("review_id", "STRING NOT NULL"), ("poi_id", "STRING"), ("review_text", "STRING"),
        ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
}
FLAG_EDGES = [
    (1, "slv_enr_poi_info_multi_lang", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (2, "slv_enr_poi_destination", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (3, "slv_enr_poi_review_multi_lang", "lh_vv_gold.enr", "gld_enr_poi_review", "APPEND", "NB_ENR_POI_REVIEW", 1),
]
HOURS_OFF = ("slv_3p_poi_opening_hours",)
INFO_INPUTS = tuple(s for s in INFO_ACTIVE if s not in HOURS_OFF) + (
    "slv_enr_poi_info_multi_lang", "slv_enr_poi_destination",
)
REVIEW_INPUTS = ("slv_3p_poi_review", "slv_enr_poi_review_multi_lang")
EDGES = [
    (1, "slv_pn_business_services", "slv_pn_poi", "RECOMPUTE", "NB_SLV_PN_POI", 1),
    (2, "slv_pn_business_service_i18ns", "slv_pn_poi", "RECOMPUTE", "NB_SLV_PN_POI", 1),
    (3, "slv_3p_poi_review", "gld_enr_poi_review", "APPEND", "NB_ENR_POI_REVIEW", 1),
    (4, "slv_3p_poi", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (5, "slv_3p_poi_address", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (6, "slv_3p_poi_contact", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (7, "slv_3p_poi_rating", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (8, "slv_3p_poi_price", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (9, "slv_3p_poi_opening_hours", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (10, "slv_3p_poi_review", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (11, "slv_3p_poi", "gld_enr_poi_coordinate", "APPEND", "NB_ENR_POI_COORDINATE", 2),
    (12, "slv_3p_poi_address", "gld_enr_poi_coordinate", "APPEND", "NB_ENR_POI_COORDINATE", 2),
    (13, "slv_pn_poi", "gld_enr_poi_coordinate", "APPEND", "NB_ENR_POI_COORDINATE", 2),
]


def _nb(name: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "".join("".join(cell["source"]) for cell in nb["cells"])


def _cell(name: str, cell_id: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    found = [cell for cell in nb["cells"] if cell.get("id") == cell_id]
    assert len(found) == 1, cell_id
    return "".join(found[0]["source"])


def _assign(source: str, name: str):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _info_pure() -> dict:
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    ns: dict = {}
    exec(info[info.index("# BEGIN_INFO_PURE"):info.index("# END_INFO_PURE")], ns)  # noqa: S102
    return ns


def _mapping_labels() -> dict[str, tuple[str, str, str]]:
    text = (ROOT / "docs" / "context" / "3p-google" / "mapping_gld_enr_poi_info.md").read_text(encoding="utf-8")
    section = text.split("# 2. Mapping business_sector", 1)[1]
    labels = {}
    for line in section.splitlines():
        if not line.startswith("|") or line.startswith("|---") or "business_sector" in line:
            continue
        cells = [part.strip() for part in line.strip("|").split("|")]
        if len(cells) < 2:
            continue
        parts = [unicodedata.normalize("NFC", part.strip()) for part in cells[1].split(" / ")]
        labels[cells[0].strip()] = tuple(parts)
    return labels


def _pure():
    text = _nb("NB_LIB_TRANSFORM_SLV_GLD.ipynb")
    start = text.index("# BEGIN_APPEND_PURE")
    end = text.index("# END_APPEND_PURE")
    ns = {
        "json": json,
        "APPEND_MARKER_KEY": "vv_append",
        "APPEND_INVALIDATING_OPS": (
            "RESTORE", "DELETE", "UPDATE", "MERGE", "TRUNCATE",
            "CREATE OR REPLACE TABLE", "REPLACE TABLE",
        ),
    }
    exec(text[start:end], ns)  # noqa: S102
    return ns


def test_gold_ddl_matches_mapping():
    patch = _cell("NB_CREATE_DDL.ipynb", "enrflagpy")
    previous = _cell("NB_CREATE_DDL.ipynb", "enrinfopy")
    old = _cell("NB_CREATE_DDL.ipynb", "enrddlpy")
    assert _assign(patch, "INFO_COLS") == INFO
    assert _assign(patch, "REVIEW_COLS") == REVIEW
    assert [col for col in _assign(previous, "INFO_COLS") if col[0] not in INFO_REMOVED] == [
        col for col in INFO if col[0] not in INFO_FLAGS
    ]
    assert [col for col in REVIEW if col[0] not in REVIEW_FLAGS] == _assign(old, "REVIEW_COLS")
    assert _assign(old, "COORD_COLS") == COORD
    names = [name for name, _dtype in INFO]
    for dropped in INFO_DROPPED:
        assert dropped not in names
    review_names = [name for name, _dtype in REVIEW]
    for dropped in DROPPED:
        assert dropped not in review_names


def test_mapping_comments_and_edges():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    review = _nb("NB_ENR_POI_REVIEW.ipynb")
    for col in ("COL-001", "COL-003", "COL-007", "COL-009", "COL-010"):
        assert col in info
    for number in (35, 36, 37, 38, 39, 44, 45, 46, 47, 48):
        assert f"COL-{number:03d}" in info
    for col in ("COL-004", "COL-005", "COL-006", "COL-008", "COL-040", "COL-041", "COL-042", "COL-043"):
        assert col not in info
    for col in ("COL-022", "COL-023", "COL-025", "COL-027", "COL-031", "COL-032", "COL-033", "COL-034"):
        assert col in review
    ddl = _cell("NB_CREATE_DDL.ipynb", "enrddlpy")
    for _seq, src, trg, mode, nb, _priority in EDGES:
        assert f'"{src}"' in ddl and f'"{trg}"' in ddl and f'"{mode}"' in ddl and f'"{nb}"' in ddl
    assert ddl.count('"APPEND"') == 11
    assert "pn_poi" not in info
    assert "PL_VV_TRANS_SLV_TO_ENR_15P" in ddl


def test_info_patch_cell_edges():
    patch = _cell("NB_CREATE_DDL.ipynb", "enrinfopy")
    old = _cell("NB_CREATE_DDL.ipynb", "enrddlpy")
    assert _assign(patch, "EDGES_OFF") == EDGES_OFF
    assert _assign(patch, "EDGES_ON") == EDGES_ON
    assert _assign(patch, "INFO_ACTIVE") == INFO_ACTIVE
    pairs = {(src, trg) for _seq, src, _schema, trg, _mode, _nb, _priority in _assign(old, "EDGES")}
    assert set(map(tuple, EDGES_OFF)) <= pairs
    off = set(map(tuple, EDGES_OFF))
    kept = {src for src, trg in pairs if trg == "gld_enr_poi_info" and (src, trg) not in off}
    added = {src for _seq, src, _schema, _trg, _mode, _nb, _priority in EDGES_ON}
    assert kept | added == set(INFO_ACTIVE)
    assert not any(trg == "gld_enr_poi_coordinate" and (src, trg) not in off for src, trg in pairs)


def test_info_patch_cell_guards():
    patch = _cell("NB_CREATE_DDL.ipynb", "enrinfopy")
    old = _cell("NB_CREATE_DDL.ipynb", "enrddlpy")
    assert list(_assign(patch, "OLD_INFO_NAMES")) == [name for name, _dtype in _assign(old, "INFO_COLS")]
    for token in ("DROP", "DELETE", "TRUNCATE", "ALTER TABLE", "REPLACE", "RESTORE"):
        assert token not in patch
    order = [
        "held = True", "tableExists(INFO_FQ)", "OLD_INFO_NAMES]",
        "STATE-001:", "INSERT INTO {CFG}", "SET is_active = 0", "finally:",
    ]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    assert "SET is_active = 1" not in patch
    assert "lock_exec_id = '{LOCK}'" in patch
    nb = json.loads((ROOT / "notebooks" / "NB_CREATE_DDL.ipynb").read_text(encoding="utf-8"))
    ids = [cell.get("id") for cell in nb["cells"]]
    assert ids[-18:-12] == ["enrinfomd", "enrinfopy", "mvpoimd", "mvpoipy", "enrflagmd", "enrflagpy"]
    assert ids[-12:-10] == ["ohpassmd", "ohpasspy"]
    assert ids[-10:-8] == ["peholmd", "peholpy"]
    assert ids[-8:-6] == ["srvpoimd", "srvpoipy"]
    assert ids[-6:-4] == ["srvratemd", "srvratepy"]
    assert ids[-4:] == ["mediaddlmd", "mediaddlpy", "amenddlmd", "amenddlpy"]


def test_info_select_matches_ddl():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    block = info.split("# BEGIN_INFO_SELECT", 1)[1].split("# END_INFO_SELECT", 1)[0]
    assert re.findall(r'\.alias\("(\w+)"\)', block) + ["created_at", "updated_at"] == [name for name, _dtype in INFO]


def test_info_spec_inputs_match_active_edges():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    spec = next(
        node.value for node in ast.parse(info).body
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SPEC" for t in node.targets)
    )
    inputs = next(kw.value for kw in spec.keywords if kw.arg == "inputs")
    assert {elt.value for elt in inputs.values} == set(INFO_INPUTS)
    landing = {src for _seq, src, _schema, trg, *_rest in FLAG_EDGES if trg == "gld_enr_poi_info"}
    assert (set(INFO_ACTIVE) - set(HOURS_OFF)) | landing == set(INFO_INPUTS)
    for name in ('"slv_3p_poi"', '"slv_3p_poi_address"', '"slv_3p_poi_contact"'):
        assert name not in info


def _func_text(source: str, name: str) -> str:
    tree = ast.parse(source)
    node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == name)
    segment = ast.get_source_segment(source, node)
    assert segment
    return segment


def test_flag_patch_constants():
    patch = _cell("NB_CREATE_DDL.ipynb", "enrflagpy")
    assert _assign(patch, "LANDING_COLS") == LANDING
    assert _assign(patch, "EDGES_ON") == FLAG_EDGES
    for cols in LANDING.values():
        assert all("UNIQUE" not in name and "UNIQUE" not in dtype for name, dtype in cols)
        assert "NOT NULL" in cols[0][1]
        assert all("NOT NULL" not in dtype for _name, dtype in cols[1:])


def test_flag_patch_guards():
    raw = _cell("NB_CREATE_DDL.ipynb", "enrflagpy")
    code = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "REPLACE", "RESTORE", "columnMapping", "SET is_active", "UPDATE {CFG}"):
        assert token not in code
    assert "ADD COLUMNS (" in raw
    assert "BOOLEAN AFTER" in raw
    order = [
        "held = True", "Dừng trước khi ghi", "spark.sql(_create_sql(fq, CONTRACTS[fq]))",
        "_add_flags(fq, flags)", "INSERT INTO {CFG}", "Sau khi ghi", "finally:",
    ]
    positions = [raw.index(token) for token in order]
    assert positions == sorted(positions)
    assert "lock_exec_id = '{LOCK}'" in raw


def test_flag_node_contract():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    review = _cell("NB_ENR_POI_REVIEW.ipynb", "04339a06")
    present = _func_text(info, "_present")
    assert "ctx.input(role).select(key)" in present
    assert ".distinct()" in present
    assert 'isNotNull().alias("is_enriched_multi_lang")' in info
    assert 'isNotNull().alias("is_enriched_destination")' in info
    assert 'required_inputs=("entity",)' in info
    assert "enrich_flag_null" in info
    block = review.split("return rv.select(", 1)[1].split("SPEC =", 1)[0]
    bare = re.findall(r'^\s*F\.col\("(\w+)"\),\s*(?:#|$)', block, re.M)
    aliases = re.findall(r'\.alias\("(\w+)"\)', block)
    assert bare + aliases + ["created_at", "updated_at"] == [name for name, _dtype in REVIEW]
    spec = next(
        node.value for node in ast.parse(review).body
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SPEC" for t in node.targets)
    )
    inputs = next(kw.value for kw in spec.keywords if kw.arg == "inputs")
    assert {elt.value for elt in inputs.values} == set(REVIEW_INPUTS)
    assert 'required_inputs=("review",)' in review
    assert "enrich_flag_null" in review
    assert _func_text(info, "_flag_keys") == _func_text(review, "_flag_keys")


def test_info_partner_join_matches_entity():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    assert 'uuid_md5(F.col("business_service_id"), F.lit(PARTNER))' in info
    assert 'F.col("locale") == F.lit("vi")' in info
    assert _info_pure()["PARTNER"] == "partner"
    entity = _cell("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb", "b1entitybuild")
    assert 'uuid_md5(F.col("id"), F.lit(PARTNER))' in entity
    assert 'PARTNER = "partner"' in entity
    assert '["source_id", "language_code"]' not in info


def test_info_labels_match_mapping():
    pure = _info_pure()
    got = {key: tuple(unicodedata.normalize("NFC", part) for part in value) for key, value in pure["SECTOR_LABELS"].items()}
    got["other"] = tuple(unicodedata.normalize("NFC", part) for part in pure["SECTOR_OTHER"])
    assert got == _mapping_labels()


def test_best_time_pattern():
    pattern = re.compile(_info_pure()["BEST_TIME_RE"])
    seed = _assign(_cell("NB_SETUP_INITIAL_DDL.ipynb", "init_seed_place_type"), "BEST_TIME_CANONICAL")
    for value in seed.values():
        match = pattern.fullmatch(value.strip())
        if value == "all_year":
            assert match is None
        else:
            assert match and all(1 <= int(group) <= 12 for group in match.groups())
    assert pattern.fullmatch("Month 11-3").groups() == ("11", "3")
    assert pattern.fullmatch("Month 11–4").groups() == ("11", "4")
    for value in ("Month 13-2", "Month 0-5", ""):
        assert pattern.fullmatch(value) is None


def test_info_removal_keys():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    assert "def _role_keys(ctx, role, spine_keys):" in info
    assert 'for role in ("rating", "price", "review", "amenity"):' in info
    assert "old.subtract(current)" in info
    assert 'if info["basis"] not in ("EDGE", "MARKER") or info["from"] is None:' in info
    assert "return spine_keys" in info
    assert "_amenity_keys" not in info
    assert '_keys(ctx.changed("entity"), "poi_id")' in info


def test_pipeline_timeouts():
    doc = json.loads((ROOT / "pipelines" / "PL_VV_TRANS_SLV_TO_ENR_15P" / "PL_VV_TRANS_SLV_TO_ENR_15P.json").read_text(encoding="utf-8"))
    raw = json.dumps(doc)
    assert "PENDING_FABRIC_NOTEBOOK_ID" not in raw
    assert "68c81db2-fa14-4fee-91f3-a9f31b1ca2c8" not in raw
    props = doc["resources"][0]["properties"]
    activity = next(item for item in props["activities"] if item["name"] == "NB_00_ORCHES_SLV_TO_ENR_15P")
    guard = next(item for item in props["activities"] if item["name"] == "Validate_Notebook_Binding")
    assert activity["policy"]["timeout"] == "0.00:32:00"
    assert activity["policy"]["retry"] == 0
    assert props["concurrency"] == 1
    assert activity["dependsOn"][0]["activity"] == "Validate_Notebook_Binding"
    assert "PENDING" in guard["typeProperties"]["expression"]["value"]
    assert activity["typeProperties"]["notebookId"]["value"] == "@pipeline().parameters.nb_orches_id"
    assert activity["typeProperties"]["workspaceId"]["value"] == "@pipeline().parameters.workspace_id"
    params = activity["typeProperties"]["parameters"]
    assert params["p_pl_name"]["value"]["value"] == "@pipeline().Pipeline"
    assert params["p_run_id"]["value"]["value"] == "@pipeline().RunId"
    assert params["p_dag_timeout_min"]["value"] == "25"
    assert params["p_lock_timeout_min"]["value"] == "35"
    assert int(params["p_lock_timeout_min"]["value"]) > int(params["p_dag_timeout_min"]["value"]) + 5


def test_append_guards():
    lib = _nb("NB_LIB_TRANSFORM_SLV_GLD.ipynb")
    empty_at = lib.index("Đầu vào bắt buộc rỗng")
    append_at = lib.index("df = execute_append(")
    assert empty_at < append_at
    assert "frame.count()" in lib
    assert "actual != expected" in lib
    ddl = _nb("NB_CREATE_DDL.ipynb")
    assert "field.nullable" in ddl


def test_append_baseline_and_marker():
    ns = _pure()
    choose = ns["choose_append_baseline"]
    assert choose(4, "t", 7, "t", "t", False) == (7, "MARKER")
    assert choose(8, "t", 7, "t", "t", False) == (8, "EDGE")
    assert choose(5, "t", 5, "t", "t", False) == (5, "EDGE")
    assert choose(5, "old", 3, "old", "new", False) == (None, "FULL")
    assert choose(1, "t", 2, "t", "t", True) == (None, "FORCE")
    assert ns["append_history_stops"]("MERGE", None) is True
    assert ns["append_history_stops"]("WRITE", "Overwrite") is True
    assert ns["append_history_stops"]("WRITE", "Append") is False
    marker = ns["parse_append_marker"]('{"vv_append": 1, "exec_id": "a"}')
    assert marker["exec_id"] == "a"
    assert ns["parse_append_marker"]('{"exec_id": "a"}') is None
    assert ns["parse_append_marker"]("not-json") is None


EDGES_DELETE = [
    ("slv_pn_business_services", "lh_vv_silver.dbo", "slv_pn_poi"),
    ("slv_pn_business_service_i18ns", "lh_vv_silver.dbo", "slv_pn_poi"),
    ("slv_3p_poi", "lh_vv_gold.enr", "gld_enr_poi_coordinate"),
    ("slv_3p_poi_address", "lh_vv_gold.enr", "gld_enr_poi_coordinate"),
    ("slv_pn_poi", "lh_vv_gold.enr", "gld_enr_poi_coordinate"),
    ("slv_3p_poi", "lh_vv_gold.enr", "gld_enr_poi_info"),
    ("slv_3p_poi_address", "lh_vv_gold.enr", "gld_enr_poi_info"),
    ("slv_3p_poi_contact", "lh_vv_gold.enr", "gld_enr_poi_info"),
]
WM_DELETE = (
    "wm_e__gld_enr_poi_coordinate__slv_3p_poi",
    "wm_e__gld_enr_poi_coordinate__slv_3p_poi_address",
    "wm_e__gld_enr_poi_coordinate__slv_pn_poi",
    "wm_e__slv_pn_poi__slv_pn_business_service_i18ns",
    "wm_e__slv_pn_poi__slv_pn_business_services",
    "wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H",
)
NODE_EDGES = [
    ("slv_3p_poi", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_address", "slv_poi_entity_non_enrich"),
    ("ref_dictionary_place_type", "slv_poi_entity_non_enrich"),
    ("slv_pn_business_services", "slv_poi_entity_non_enrich"),
    ("slv_pn_business_service_i18ns", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_contact", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_amenity", "slv_poi_amenity"),
    ("slv_poi_entity_non_enrich", "slv_poi_amenity"),
    ("ref_dictionary_amenities", "slv_poi_amenity"),
]


def test_cleanup_patch_constants():
    from test_initial_ddl_contract import _by_id, _initial

    patch = _cell("NB_CREATE_DDL.ipynb", "mvpoipy")
    edges = _assign(patch, "EDGES_DELETE")
    watermarks = _assign(patch, "WM_DELETE")
    assert edges == EDGES_DELETE
    assert watermarks == WM_DELETE
    assert _assign(patch, "NODE_EDGES") == NODE_EDGES
    assert _assign(patch, "INFO_ACTIVE") == INFO_ACTIVE
    assert set(map(tuple, EDGES_OFF)) <= {(src, trg) for src, _schema, trg in edges}
    edge_wm = {f"wm_e__{trg}__{src}" for src, _schema, trg in edges if trg != "gld_enr_poi_info"}
    assert {item for item in watermarks if item.startswith("wm_e__")} == edge_wm
    assert "wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H" in watermarks
    namespace: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], namespace)  # noqa: S102
    seed_keys = {(src, schema, trg) for _pl, _ss, src, schema, trg, *_rest in namespace["PIPELINE_CONFIG_ROWS"]}
    assert seed_keys.isdisjoint(set(map(tuple, edges)))


def test_cleanup_patch_guards():
    patch = _cell("NB_CREATE_DDL.ipynb", "mvpoipy")
    assert patch.count("DELETE FROM") == 2
    for token in ("DROP", "TRUNCATE", "ALTER TABLE", "INSERT INTO", "SET is_active", "RESTORE", "UPDATE {CFG}"):
        assert token not in patch
    order = ["held = True", "Dừng trước khi ghi", "DELETE FROM {CFG}", "DELETE FROM {WM}", "Sau khi ghi", "finally:"]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    assert "AND NOT (trg_tbl = 'gld_enr_poi_info' AND is_active <=> 1)" in patch
    assert "AND lock_exec_id IS NULL\")" in patch
    assert "lock_exec_id = '{LOCK}'" in patch
    assert "LEASE_MINUTES = 35" in patch
    assert patch.index("cạnh active của info") < patch.index("DELETE FROM {CFG}")
    assert "GROUP BY src_schema, src_tbl" in patch
    assert patch.index("pl_name IS NULL") < patch.index("DELETE FROM {CFG}")


def test_info_hours_passthrough():
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    assert 'F.col("e.opening_hours_text").alias("opening_hours_text")' in info
    for token in (
        "_partner_hours", "periods_json", '"hours"', "slv_3p_poi_opening_hours",
        "$.policies.operating_hours", "opening_hours_other_source", "partner_opening_hours_null",
    ):
        assert token not in info
    assert "opening_hours_text_mismatch" in info
    assert "eqNullSafe" in info
    pure = _info_pure()
    assert "opening_hours_text" in pure["REQUIRED_COLS"]["entity"]
    assert pure["REQUIRED_COLS"]["i18n"] == ("business_service_id", "locale")


def test_hours_patch_cell_constants():
    patch = _cell("NB_CREATE_DDL.ipynb", "ohpasspy")
    assert _assign(patch, "EDGES_ON") == [
        ("slv_3p_poi_opening_hours", "lh_vv_silver.dbo", "slv_poi_entity_non_enrich", "RECOMPUTE"),
    ]
    assert _assign(patch, "EDGES_OFF") == [
        ("slv_3p_poi_opening_hours", "lh_vv_gold.enr", "gld_enr_poi_info"),
    ]
    assert set(_assign(patch, "INFO_KEEP")) == set(INFO_INPUTS)
    node_edges = _assign(_cell("NB_CREATE_DDL.ipynb", "mvpoipy"), "NODE_EDGES")
    entity_src = tuple(src for src, trg in node_edges if trg == "slv_poi_entity_non_enrich")
    assert _assign(patch, "ENTITY_SRC") == entity_src
    assert _assign(patch, "NEW_COL") == ("opening_hours_text", "STRING")
    from test_initial_ddl_contract import _by_id, _initial

    namespace: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], namespace)  # noqa: S102
    rows = namespace["PIPELINE_CONFIG_ROWS"]

    def flags(src, schema, trg):
        return [
            active for pl, _ss, name, trg_schema, target, active, *_rest in rows
            if pl == "PL_VV_TRANS_SLV_TO_ENR_15P" and name == src and trg_schema == schema and target == trg
        ]

    assert flags("slv_3p_poi_opening_hours", "lh_vv_silver.dbo", "slv_poi_entity_non_enrich") == [1]
    assert flags("slv_3p_poi_opening_hours", "lh_vv_gold.enr", "gld_enr_poi_info") == [0]


def test_hours_patch_cell_guards():
    raw = _cell("NB_CREATE_DDL.ipynb", "ohpasspy")
    code = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("#"))
    for token in (
        "DROP", "DELETE", "TRUNCATE", "REPLACE", "RESTORE", "columnMapping",
        " AFTER ", "SET is_active = 1", "CREATE TABLE",
    ):
        assert token not in code
    assert "ADD COLUMNS (`{NEW_COL[0]}` {NEW_COL[1]})" in raw
    order = [
        "held = True", "Dừng trước khi ghi", "ALTER TABLE", "MERGE INTO {CFG}", "Sau khi ghi", "finally:",
    ]
    positions = [raw.index(token) for token in order]
    assert positions == sorted(positions)
    assert "lock_exec_id = '{LOCK}'" in raw
    assert "LEASE_MINUTES = 35" in raw
    assert raw.count("MERGE INTO {CFG}") == 1
    calls = [match.start() for match in re.finditer(r"(?m)^\s*_refresh_lock\(\)", raw)]
    assert len(calls) == 2
    assert calls[0] < raw.index("ALTER TABLE") < calls[1] < raw.index("MERGE INTO {CFG}")
    assert "if off_flags not in ({0: 1}, {1: 1}):" in raw
    assert ".replace(\"'\", \"''\")" in raw
    assert "cần đúng 1 dòng is_active = 0" in raw


def test_removed_notebooks_absent():
    for name in ("NB_SLV_PN_POI.ipynb", "NB_ENR_POI_COORDINATE.ipynb"):
        assert not (ROOT / "notebooks" / name).exists()
    pattern = re.compile(r"\bslv_pn_poi\b|gld_enr_poi_coordinate")
    for path in (ROOT / "notebooks").glob("*.ipynb"):
        if path.name == "NB_CREATE_DDL.ipynb":
            continue
        text = path.read_text(encoding="utf-8")
        if path.name == "NB_SETUP_INITIAL_DDL.ipynb":
            code = "\n".join(
                line.split("#", 1)[0] for line in text.splitlines()
            )
            assert pattern.search(code) is None
            continue
        assert pattern.search(text) is None

