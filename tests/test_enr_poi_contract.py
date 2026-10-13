"""Contract checks for the gld_enr append flow. No Spark."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

INFO = [
    ("poi_id", "STRING NOT NULL"), ("poi_name", "STRING"), ("types", "STRING"),
    ("subcategory_tags", "STRING"), ("business_sector", "STRING"), ("business_category", "STRING"),
    ("website_url", "STRING"), ("short_address", "STRING"), ("district", "STRING"),
    ("destination_name", "STRING"), ("destination_context", "STRING"), ("rating", "DECIMAL(4,2)"),
    ("userRatingCount", "BIGINT"), ("priceLevel", "INT"), ("opening_hours_text", "STRING"),
    ("review_json", "STRING"), ("time_to_spend", "STRING"), ("best_time_type", "STRING"),
    ("best_time_from_month", "INT"), ("best_time_to_month", "INT"), ("cost", "BIGINT"),
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
    ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
]
DROPPED = ("description", "title", "positive", "negative", "response_text", "source_review_id")
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
    src = _nb("NB_CREATE_DDL.ipynb")
    for table, cols in (
        ("gld_enr_poi_info", INFO),
        ("gld_enr_poi_coordinate", COORD),
        ("gld_enr_poi_review", REVIEW),
    ):
        assert table in src
        for name, dtype in cols:
            assert f'("{name}", "{dtype}")' in src
    for dropped in DROPPED:
        assert f"`{dropped}`" not in src.split("gld_enr_poi_info")[-1].split("EDGES")[0] or dropped not in (
            "description", "title", "positive", "negative", "response_text", "source_review_id"
        )
    # Dropped names are absent as DDL columns of the three tables.
    block = src[src.index("INFO_COLS"):src.index("EDGES")]
    for dropped in DROPPED:
        assert f'"{dropped}"' not in block


def test_mapping_comments_and_edges():
    info = _nb("NB_ENR_POI_INFO.ipynb")
    coord = _nb("NB_ENR_POI_COORDINATE.ipynb")
    review = _nb("NB_ENR_POI_REVIEW.ipynb")
    for col in ["COL-001", "COL-003", "COL-004", "COL-005", "COL-006", "COL-007", "COL-008", "COL-009", "COL-010"]:
        assert col in info
    for number in range(35, 49):
        assert f"COL-{number:03d}" in info
    for number in range(11, 22):
        assert f"COL-{number:03d}" in coord
    for col in ("COL-022", "COL-023", "COL-025", "COL-027", "COL-031", "COL-032", "COL-033", "COL-034"):
        assert col in review
    ddl = _nb("NB_CREATE_DDL.ipynb")
    for _seq, src, trg, mode, nb, _priority in EDGES:
        assert f'"{src}"' in ddl and f'"{trg}"' in ddl and f'"{mode}"' in ddl and f'"{nb}"' in ddl
    assert ddl.count('"APPEND"') == 11
    assert "pn_poi" not in info
    assert "PL_VV_TRANS_SLV_TO_ENR_15P" in ddl


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
