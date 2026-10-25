"""Contract of gld_srv hours and node specs. No Spark."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "docs" / "context" / "mapping_gld_srv_poi_info.md"
TECH = ("row_hash", "created_at", "updated_at", "deleted_at")
INFO_FQ = "lh_vv_gold.dbo.gld_srv_poi_info"
NEW_INFO = [("rating_overall", "DECIMAL(4,2)"), ("rating_count", "INT"), ("review_count", "INT")]
NEW_EDGES = [
    (1, "slv_3p_poi_rating", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
    (2, "slv_3p_poi_review", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
]
PARTNER_DAYS = ("monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday")


def _nb(name):
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell(name, cid):
    found = [cell for cell in _nb(name)["cells"] if cell.get("id") == cid]
    assert len(found) == 1
    return "".join(found[0]["source"])


def _hours():
    env: dict = {}
    exec(_cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfohours"), env)  # noqa: S102
    return env


def _fence(text):
    match = re.search(r"```json\n(.*?)```", text, re.S)
    assert match
    return json.loads(match.group(1))


def _case(number):
    text = MAPPING.read_text(encoding="utf-8")
    block = text.split(f"#### Case {number}", 1)[1]
    if "#### Case" in block:
        block = block.split("#### Case", 1)[0]
    fences = re.findall(r"```json\n(.*?)```", block, re.S)
    before, after = json.loads(fences[0]), json.loads(fences[1])
    return json.dumps(before, ensure_ascii=False), after


def _keys(rows):
    return [list(row) for row in rows]


def _week(**overrides):
    doc = {
        key: {"status": False, "hours": [{"open_time": "8:00", "close_time": "17:00"}]}
        for key in PARTNER_DAYS
    }
    for key, value in overrides.items():
        if value is None:
            doc.pop(key, None)
        else:
            doc[key] = value
    return json.dumps(doc, ensure_ascii=False)


def _assign(source, name):
    tree = ast.parse(source)
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _spec(source):
    tree = ast.parse(source)
    return next(
        node.value for node in tree.body
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "SPEC" for t in node.targets)
    )


def test_google_case1():
    env = _hours()
    raw, after = _case(1)
    out, err = env["google_hours"](raw)
    assert err is None
    got = json.loads(out)
    assert got == after
    assert _keys(got) == _keys(after)


def test_google_case2_all_day():
    env = _hours()
    raw, after = _case(2)
    out, err = env["google_hours"](raw)
    assert err is None
    got = json.loads(out)
    assert got == after
    assert _keys(got) == _keys(after)


def test_google_multi_period_rule9():
    text = MAPPING.read_text(encoding="utf-8")
    example = _fence(text.split("9. Nhiều", 1)[1].split("### 1.4", 1)[0])
    raw = json.dumps([
        {"open_hour": 8, "open_minute": 0, "close_hour": 12, "close_minute": 0, "day_of_week": 1},
        {"open_hour": 13, "open_minute": 0, "close_hour": 17, "close_minute": 0, "day_of_week": 1},
    ])
    out, err = _hours()["google_hours"](raw)
    assert err is None
    got = json.loads(out)
    assert got[:2] == example
    assert len(got) == 8
    assert [row["day_of_week"] for row in got] == [1, 1, 2, 3, 4, 5, 6, 7]


def test_google_null_and_empty():
    env = _hours()
    assert env["google_hours"](None) == (None, None)
    out, err = env["google_hours"]("[]")
    assert err is None
    got = json.loads(out)
    assert len(got) == 7
    assert all(row["is_closed"] and row["value"] == "Đóng cửa" for row in got)


def test_google_stop_codes():
    env = _hours()
    assert env["google_hours"]("{")[1] == "GOOGLE_INVALID_JSON"
    assert env["google_hours"]("{}")[1] == "GOOGLE_NOT_ARRAY"
    assert env["google_hours"](json.dumps([{"day_of_week": 7, "open_hour": 8, "open_minute": 0,
                                           "close_hour": 12, "close_minute": 0}]))[1] == "GOOGLE_BAD_DAY"
    assert env["google_hours"](json.dumps([{"day_of_week": 1, "open_hour": True, "open_minute": 0,
                                           "close_hour": 12, "close_minute": 0}]))[1] == "GOOGLE_BAD_TIME"
    assert env["google_hours"](json.dumps([{"day_of_week": 1, "open_hour": 8, "open_minute": 0}]))[1] == "GOOGLE_BAD_TIME"
    assert env["google_hours"](json.dumps([{"open_hour": 0.0, "open_minute": 0, "day_of_week": 0}]))[1] == "GOOGLE_BAD_TIME"


def test_partner_single_hours():
    out, err = _hours()["partner_hours"](_week())
    assert err is None
    got = json.loads(out)
    assert len(got) == 7
    assert all(row["open_time"] == "8:00" and row["close_time"] == "17:00" and not row["is_closed"] for row in got)


def test_partner_closed_forms():
    fn = _hours()["partner_hours"]
    missing, err = fn(_week(sunday=None))
    assert err is None and json.loads(missing)[6]["is_closed"]
    no_hours, err = fn(_week(monday={"status": True}))
    assert err is None and json.loads(no_hours)[0]["is_closed"]
    empty, err = fn(_week(tuesday={"status": False, "hours": []}))
    assert err is None and json.loads(empty)[1]["is_closed"]
    status_only = json.dumps({key: {"status": False} for key in PARTNER_DAYS})
    out, err = fn(status_only)
    assert err is None
    assert all(row["is_closed"] for row in json.loads(out))


def test_partner_stop_codes():
    fn = _hours()["partner_hours"]
    two = _week(monday={"hours": [{"open_time": "08:00", "close_time": "12:00"},
                                  {"open_time": "13:00", "close_time": "17:00"}]})
    assert fn(two)[1] == "PARTNER_MULTI_HOURS"
    assert fn(_week(tuesday={"hours": None}))[1] == "PARTNER_BAD_HOURS"
    raw = json.loads(_week())
    raw["wednesday"] = None
    assert fn(json.dumps(raw))[1] == "PARTNER_BAD_DAY"
    assert fn(_week(thursday={"hours": [{"open_time": 8, "close_time": "17:00"}]}))[1] == "PARTNER_BAD_HOURS"


def test_unknown_source_stops():
    env = _hours()
    assert env["operating_hours"]("bing", "[]") == (None, "SOURCE_NOT_GOOGLE_PARTNER")
    assert env["operating_hours"](None, "[]") == (None, "SOURCE_NOT_GOOGLE_PARTNER")


def test_node_specs():
    builds = {
        "NB_GLD_SRV_POI_MULTI_LANG.ipynb": "srvmlbuild",
        "NB_GLD_SRV_POI_INFO.ipynb": "srvinfobuild",
    }
    expected = {
        "srvmlbuild": {
            "pk": ("poi_id", "lang"),
            "inputs": {"multi_lang": "slv_enr_poi_info_multi_lang", "entity": "slv_poi_entity_non_enrich",
                       "i18n": "slv_pn_business_service_i18ns"},
            "required_inputs": ("multi_lang", "entity"),
        },
        "srvinfobuild": {
            "pk": ("poi_id",),
            "inputs": {"entity": "slv_poi_entity_non_enrich", "destination": "slv_enr_poi_destination",
                       "multi_lang": "slv_enr_poi_info_multi_lang", "rating": "slv_3p_poi_rating",
                       "review": "slv_3p_poi_review"},
            "required_inputs": ("entity",),
        },
    }
    for name, cid in builds.items():
        source = _cell(name, cid)
        code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
        assert "lh_vv_gold" not in code
        assert "deleted" not in code
        assert source.count("live_only=False") == 3
        spec = _spec(source)
        kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in spec.keywords if kw.arg != "build"}
        assert kwargs["write_mode"] == "MERGE"
        assert kwargs["pk"] == expected[cid]["pk"]
        assert kwargs["inputs"] == expected[cid]["inputs"]
        assert kwargs["required_inputs"] == expected[cid]["required_inputs"]
    multi = _cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild")
    assert 'PARTNER = "partner"' in multi
    assert 'uuid_md5(F.col("business_service_id"), F.lit(PARTNER))' in multi


def test_build_columns_match_ddl():
    gold = _assign(_cell("NB_CREATE_DDL.ipynb", "srvpoipy"), "GOLD_COLS")
    gold[INFO_FQ] = _assign(_cell("NB_CREATE_DDL.ipynb", "srvratepy"), "INFO_COLS")
    pairs = {
        "gld_srv_poi_multi_lang": _assign(_cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"), "OUT_COLS"),
        "gld_srv_poi_info": _assign(_cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"), "OUT_COLS"),
    }
    for table, cols in pairs.items():
        fq = "lh_vv_gold.dbo." + table
        assert list(cols) + list(TECH) == [name for name, _dtype in gold[fq]]


def test_info_rating_patch():
    ids = [cell.get("id") for cell in _nb("NB_CREATE_DDL.ipynb")["cells"]]
    assert ids[-4:] == ["srvpoimd", "srvpoipy", "srvratemd", "srvratepy"]
    patch = _cell("NB_CREATE_DDL.ipynb", "srvratepy")
    base = _assign(_cell("NB_CREATE_DDL.ipynb", "srvpoipy"), "GOLD_COLS")[INFO_FQ]
    assert _assign(patch, "INFO_NEW_COLS") == NEW_INFO
    assert _assign(patch, "INFO_COLS") == base[:-len(TECH)] + NEW_INFO + base[-len(TECH):]
    assert _assign(patch, "EDGES_ON") == NEW_EDGES
    order = ["held = True", "Dừng trước khi ghi", "ALTER TABLE", "INSERT INTO {CFG}", "Sau khi ghi", "finally:"]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "UPDATE {CFG}", "REPLACE", "columnMapping", "<<<"):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and " AFTER " in code
    assert "LEASE_MINUTES = 90" in patch and "lock_exec_id = '{LOCK}'" in patch
    assert patch.rindex("_refresh_lock()") < patch.index("INSERT INTO {CFG}")


def test_mapping_targets_match_out_cols():
    table = MAPPING.read_text(encoding="utf-8").split("### 1.2. Field Mapping", 1)[1].split("### 1.3", 1)[0]
    rows = [line.split("|")[1:-1] for line in table.splitlines() if line.startswith("|")][2:]
    out = _assign(_cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"), "OUT_COLS")
    assert [cells[3].strip() for cells in rows] == list(out) + ["created_at", "updated_at"]
    types = {cells[3].strip(): cells[1].strip() for cells in rows}
    assert types["rating_overall"] == "decimal(4,2)"
    assert types["rating_count"] == types["review_count"] == "integer"


def test_info_rating_build_rules():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
    assert "countDistinct" not in code and "F.count(F.lit(1))" in code
    assert "INT_MIN, INT_MAX = -2147483648, 2147483647" in code
    assert "poi_id có hơn một dòng" in code and "ngoài miền INT" in code
    assert code.count("F.when(is_google,") == 4
    assert "coalesce(F.col(\"review_count\")" not in code

