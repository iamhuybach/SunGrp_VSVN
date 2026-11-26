"""Contract of gld_srv hours and node specs. No Spark."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "docs" / "context" / "mapping_gld_srv_poi_info.md"
ML_MAPPING = ROOT / "docs" / "context" / "mapping_gld_srv_poi_multi_lang.md"
TECH = ("row_hash", "created_at", "updated_at", "deleted_at")
INFO_FQ = "lh_vv_gold.dbo.gld_srv_poi_info"
ML_FQ = "lh_vv_gold.dbo.gld_srv_poi_multi_lang"
OLDPRICE_INFO = [("old_address", "STRING"), ("price_level", "INT"), ("price_min", "DECIMAL(18,2)"), ("price_max", "DECIMAL(18,2)")]
OLDPRICE_ML = [("story", "STRING"), ("local_tips", "STRING")]
ML_BASE = [
    ("poi_id", "STRING NOT NULL"), ("lang", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
    ("time_to_spend", "STRING"), ("best_time", "STRING"), ("cost", "STRING"), ("description", "STRING"),
    ("experience", "STRING"), ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ("deleted_at", "TIMESTAMP"),
]
PRICE_EDGE = (1, "slv_3p_poi_price", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1)
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
    three = _week(monday={"hours": [{"open_time": "08:00", "close_time": "09:00"}] * 3})
    assert fn(three)[1] == "PARTNER_MULTI_HOURS"
    assert fn(_week(tuesday={"hours": None}))[1] == "PARTNER_BAD_HOURS"
    raw = json.loads(_week())
    raw["wednesday"] = None
    assert fn(json.dumps(raw))[1] == "PARTNER_BAD_DAY"
    assert fn(_week(thursday={"hours": [{"open_time": 8, "close_time": "17:00"}]}))[1] == "PARTNER_BAD_HOURS"


def test_partner_two_hours():
    fn = _hours()["partner_hours"]
    single = json.loads(fn(_week())[0])[0]
    two = _week(monday={"status": True, "hours": [{"open_time": "08:00", "close_time": "09:00"},
                                                  {"open_time": "11:00", "close_time": "22:00"}]})
    out, err = fn(two)
    assert err is None
    got = json.loads(out)
    assert [row["day_of_week"] for row in got] == [1, 1, 2, 3, 4, 5, 6, 7]
    assert [row["value"] for row in got[:2]] == ["08:00 - 09:00", "11:00 - 22:00"]
    assert all(list(row) == list(single) and row["label"] == "Thứ Hai" and not row["is_closed"]
               and not row["is_open_all_day"] for row in got[:2])
    swapped = _week(monday={"hours": [{"open_time": "11:00", "close_time": "22:00"},
                                      {"open_time": "08:00", "close_time": "09:00"}]})
    assert [row["open_time"] for row in json.loads(fn(swapped)[0])[:2]] == ["11:00", "08:00"]
    bad = _week(monday={"hours": [{"open_time": "08:00", "close_time": "09:00"},
                                  {"open_time": 11, "close_time": "22:00"}]})
    assert fn(bad) == (None, "PARTNER_BAD_HOURS")


def test_partner_hours_mapping_text():
    section = MAPPING.read_text(encoding="utf-8").split("### 1.5.", 1)[1].split("\n---\n", 1)[0]
    assert "Nhiều hơn một phần tử `hours`" not in section
    assert "Đúng hai phần tử `hours`" in section and "Hơn hai phần tử `hours`" in section
    assert "PARTNER_MULTI_HOURS" in section


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
                       "review": "slv_3p_poi_review", "media": "slv_poi_media_info",
                       "price": "slv_3p_poi_price"},
            "required_inputs": ("entity",),
        },
    }
    for name, cid in builds.items():
        source = _cell(name, cid)
        code = "\n".join(
            line for line in source.splitlines()
            if not line.strip().startswith("#") and "GOLD_FQ" not in line and "cost_vnd" not in line
        )
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
    oldprice = _assign(_cell("NB_CREATE_DDL.ipynb", "oldpricepy"), "TABLE_COLS")
    gold[INFO_FQ] = oldprice[INFO_FQ]
    init: dict = {}
    exec(_cell("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), init)  # noqa: S102
    ml_spec = [
        (col[0], col[1]) for col in next(
            item["cols"] for item in init["TABLE_SPECS"] if item["fq"] == ML_FQ)
    ]
    assert ml_spec == oldprice[ML_FQ]
    gold[ML_FQ] = ml_spec
    pairs = {
        "gld_srv_poi_multi_lang": _assign(_cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"), "OUT_COLS"),
        "gld_srv_poi_info": _assign(_cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"), "OUT_COLS"),
    }
    for table, cols in pairs.items():
        fq = "lh_vv_gold.dbo." + table
        assert list(cols) + list(TECH) == [name for name, _dtype in gold[fq]]


def test_review_node_spec():
    source = _cell("NB_GLD_SRV_POI_REVIEW.ipynb", "srvrvbuild")
    code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
    assert "lh_vv_gold" not in code
    assert "deleted" not in code
    assert ".cast(" not in "\n".join(line for line in source.splitlines() if not line.strip().startswith("#")).replace(
        'F.lit(None).cast("string").alias("title")', "", 1)
    assert source.count(".cast(") == 1
    assert 'F.lit(None).cast("string").alias("title")' in source
    assert 'F.col("text").alias("review_text")' in source
    spec = _spec(source)
    kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in spec.keywords if kw.arg != "build"}
    assert kwargs["write_mode"] == "MERGE"
    assert kwargs["pk"] == ("review_id",)
    assert kwargs["inputs"] == {
        "review": "slv_3p_poi_review",
        "rating": "slv_3p_poi_rating",
    }
    assert kwargs["required_inputs"] == ("review",)
    types = _assign(source, "SOURCE_TYPES")
    assert types["slv_3p_poi_review"] == {"rating": "decimal(4,2)"}
    assert types["slv_3p_poi_rating"] == {"rating_overall": "decimal(4,2)", "rating_count": "bigint"}


def test_review_build_columns_match_ddl():
    cols = _assign(_cell("NB_CREATE_DDL.ipynb", "poidestpy"), "TABLE_COLS")[
        "lh_vv_gold.dbo.gld_srv_poi_review"]
    out = _assign(_cell("NB_GLD_SRV_POI_REVIEW.ipynb", "srvrvbuild"), "OUT_COLS")
    assert list(out) + list(TECH) == [name for name, _dtype in cols]


def test_review_mapping_targets():
    text = (ROOT / "docs" / "context" / "mapping_gld_srv_poi_review.md").read_text(encoding="utf-8")
    table = text.split("## 2. Field Mapping", 1)[1]
    rows = [line.split("|")[1:-1] for line in table.splitlines() if line.startswith("|")][2:]
    out = _assign(_cell("NB_GLD_SRV_POI_REVIEW.ipynb", "srvrvbuild"), "OUT_COLS")
    assert [cells[3].strip() for cells in rows] == list(out) + ["created_at", "updated_at"]


def test_info_rating_patch():
    ids = [cell.get("id") for cell in _nb("NB_CREATE_DDL.ipynb")["cells"]]
    ids = ids[: ids.index("lgpnamepy") + 1]
    assert ids[-10:] == ["enrbrzcfgmd", "enrbrzcfgpy", "enrbrzmd", "enrbrzpy", "enrgldmd", "enrgldpy", "legacyidmd", "legacyidpy", "lgpnamemd", "lgpnamepy"]
    ids = ids[:-10]
    assert ids[-30:-22] == [
        "srvpoimd", "srvpoipy", "srvratemd", "srvratepy",
        "mediaddlmd", "mediaddlpy", "amenddlmd", "amenddlpy",
    ]
    assert ids[-22:-20] == ["plcadmd", "plcadpy"]
    assert ids[-20:-18] == ["mlexpmd", "mlexppy"]
    assert ids[-18:-16] == ["srvrevmd", "srvrevpy"]
    assert ids[-16:-12] == ["rvi18nenrmd", "rvi18nenrpy", "rvi18ngldmd", "rvi18ngldpy"]
    assert ids[-12:-10] == ["mlsrcmd", "mlsrcpy"]
    assert ids[-10:-8] == ["cmscfgmd", "cmscfgpy"]
    assert ids[-8:-6] == ["srvcovermd", "srvcoverpy"]
    assert ids[-6:-4] == ["poidestmd", "poidestpy"]
    assert ids[-4:-2] == ["enrmergemd", "enrmergepy"]
    assert ids[-2:] == ["srvactivemd", "srvactivepy"]
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


def _entity_out_cols(source):
    parts = ("POI_COLS", "CONTACT_COLS", "ADDRESS_COLS", "CATEGORY_COLS", "ESTIMATE_COLS", "HOURS_COLS", "DETAIL_COLS")
    return tuple(col for name in parts for col in _assign(source, name))


def test_partner_without_destination_branch():
    gold = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    entity_out = _entity_out_cols(_cell("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb", "b1entitybuild"))
    assert _assign(gold, "ENTITY_OUT_COLS") == entity_out
    dest_names = _assign(gold, "DEST_COLS")[2:]
    from_entity = tuple(name for name in dest_names if name in entity_out)
    absent = tuple(name for name in dest_names if name not in entity_out)
    assert from_entity == ("full_address", "ward", "city", "lat", "lng")
    assert "street" not in dest_names
    assert "formatted_address" in absent and "ward_with_type" in absent and "city_with_type" in absent
    assert "FROM_ENTITY = tuple(name for name in DEST_COLS[2:] if name in ENTITY_OUT_COLS)" in gold
    assert 'des = des.withColumn("_has_dest", F.lit(True))' in gold
    assert 'is_partner = F.coalesce(SRC == "partner", F.lit(False))' in gold
    assert 'partner_without_dest = is_partner & F.col("_has_dest").isNull()' in gold
    assert "*from_dest" in gold
    assert 'if name in ("ward", "district", "city")' in gold
    assert 'F.coalesce(_text_or_null(name), _text_or_null(f"old_{name}"))' in gold
    assert 'F.coalesce(F.col(f"_e_' not in gold
    assert 'inputs={"entity": "slv_poi_entity_non_enrich"' in gold
    text = MAPPING.read_text(encoding="utf-8")
    handling = text.split("### 1.1. Xử lý", 1)[1].split("### 1.2", 1)[0]
    assert "MISSING" in handling and "_has_dest" in handling
    table = text.split("### 1.2. Field Mapping", 1)[1].split("### 1.3", 1)[0]
    rows = [line for line in table.splitlines() if line.startswith("|")]
    for name in from_entity:
        row = next(line for line in rows if line.rstrip().endswith(f"| {name} |"))
        assert f"slv_poi_entity_non_enrich.{name}" in row
        if name in ("ward", "city"):
            assert f"old_{name}" in row
        else:
            assert "Không coalesce" in row
    gold_absent = tuple(name for name in absent if name not in ("formatted_address", "ward_with_type", "city_with_type"))
    for name in gold_absent:
        row = next(line for line in rows if line.rstrip().endswith(f"| {name} |"))
        assert "null" in row
        assert "slv_poi_entity_non_enrich" not in row
        if name == "district":
            assert "old_district" in row


def test_info_rating_build_rules():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
    assert "countDistinct" not in code and "F.count(F.lit(1))" in code
    assert "INT_MIN, INT_MAX = -2147483648, 2147483647" in code
    assert "poi_id có hơn một dòng" in code and "ngoài miền INT" in code
    assert code.count("F.when(is_google,") == 4
    assert "coalesce(F.col(\"review_count\")" not in code


def _insert_after(cols, name, new):
    out = []
    for col in cols:
        out.append(col)
        if col[0] == name:
            out.append(new)
    return out


def test_multi_lang_experience_patch():
    patch = _cell("NB_CREATE_DDL.ipynb", "mlexppy")
    new = ("experience", "STRING")
    assert _assign(patch, "NEW_COL") == new
    tables = _assign(patch, "TABLE_COLS")
    ml = "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang"
    gld = "lh_vv_gold.dbo.gld_srv_poi_multi_lang"
    landing = _assign(_cell("NB_CREATE_DDL.ipynb", "enrflagpy"), "LANDING_COLS")[ml]
    gold = _assign(_cell("NB_CREATE_DDL.ipynb", "srvpoipy"), "GOLD_COLS")[gld]
    assert tables[ml] == _insert_after(landing, "description", new)
    assert tables[gld] == _insert_after(gold, "description", new)
    assert _assign(patch, "PL") == _assign(_cell("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")[1][1]
    assert "LEASE_MINUTES = 90" in patch
    order = ["held = True", "Dừng trước khi ghi", "_refresh_lock()", "ALTER TABLE", "Sau khi ghi", "finally:"]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in (
        "CREATE TABLE", "INSERT INTO {CFG}", "UPDATE {CFG}", "MERGE INTO {WM}",
        "DROP", "DELETE", "TRUNCATE", "REPLACE", "RESTORE", "columnMapping",
    ):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and " AFTER " in code
    assert "lock_exec_id = '{LOCK}'" in patch


def test_multi_lang_experience_rule():
    source = _cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild")
    assert _assign(source, "ML_COLS")[-1] == "experience"
    assert _assign(source, "OUT_COLS")[-3:] == ("experience", "story", "local_tips")
    rule = 'F.when(partner, F.coalesce(F.col("usps"), F.col("experience"))).otherwise(F.col("experience"))'
    assert rule in source
    assert '("business_service_id", "locale", "bio", "usps")' in source
    assert "hash_exclude" not in source


def test_multi_lang_i18n_only_branch():
    source = _cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild")
    code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
    assert _assign(source, "MEASURE_COLS") == ("time_to_spend", "best_time", "cost")
    assert _assign(source, "I18N_ONLY_WARN") == "multi_lang_i18n_only_rows"
    assert _assign(source, "I18N_KEY_BLANK_WARN") == "multi_lang_i18n_key_blank"
    assert "source_name" not in _assign(source, "ML_COLS")
    for line in (
        'bio = i18n.select(uuid_md5(F.col("business_service_id"), F.lit(PARTNER)).alias("_pid"),',
        'partner = F.coalesce(F.lower(F.trim(F.col("source_name"))) == PARTNER, F.lit(False))',
        'rows = (ml.select(*ML_COLS).join(ent.select("poi_id", "source_name"), "poi_id", "left")',
        '.join(bio, partner & (F.col("poi_id") == F.col("_pid")) & (F.col("lang") == F.col("_loc")), "left"))',
        'ctx.warn("multi_lang_source_name_null", rows.where(F.col("source_name").isNull()).count())',
        'description = F.when(partner, F.coalesce(F.col("bio"), F.col("description"))).otherwise(F.col("description"))',
        'p1 = (rows.withColumn("description", description).withColumn("experience", experience)',
        "return p1.unionByName(_i18n_only(ctx, ml, i18n, p1.schema))",
    ):
        assert line in source
    assert code.count("unionByName") == 1
    assert 'return F.coalesce(F.trim(F.col(name).cast("string")), F.lit("")) != ""' in source
    branch = source.split("def _i18n_only", 1)[1].split("\ndef ", 1)[0]
    for line in (
        'key_ok = _filled("business_service_id") & _filled("locale")',
        "ctx.warn(I18N_KEY_BLANK_WARN, i18n.where(~key_ok).count())",
        'ml_keys = ml.select(F.col("poi_id").alias("_pid"), F.col("lang").alias("_loc"))',
        'only = keyed.join(ml_keys, ["_pid", "_loc"], "left_anti")',
        'F.lit(PARTNER).alias("source_name"), *[F.lit(None).alias(c) for c in MEASURE_COLS],',
        'F.col("bio").alias("description"), F.col("usps").alias("experience"), *I18N_TEXT_COLS)',
        ".select(*[F.col(c).cast(types[c]).alias(c) for c in OUT_COLS]))",
        "ctx.warn(I18N_ONLY_WARN, p2.count())",
    ):
        assert line in branch
    assert 'F.col("source_name")' not in branch and "partner &" not in branch
    assert "coalesce(F.col(" not in branch and not re.search(r"\bent\b", branch)
    assert ".isin(" not in code and '"vi"' not in code


def test_multi_lang_mapping_targets():
    text = ML_MAPPING.read_text(encoding="utf-8")
    handling = text.split("### 1.1. Xử lý", 1)[1].split("### 1.2", 1)[0]
    for token in ("left_anti", "(poi_id, lang)", "'partner'", "mọi `locale`", "chỉ DDL", "mlsrcpy",
                  "multi_lang_i18n_only_rows", "multi_lang_i18n_key_blank", "`required_inputs`"):
        assert token in handling
    table = text.split("### 1.2. Field Mapping", 1)[1]
    rows = [line.split("|")[1:-1] for line in table.splitlines() if line.startswith("|")][2:]
    out = _assign(_cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"), "OUT_COLS")
    assert [cells[3].strip() for cells in rows] == list(out) + ["created_at", "updated_at"]
    transform = {cells[3].strip(): cells[2] for cells in rows}
    for name in out:
        assert "P2:" in transform[name]
    for name in _assign(_cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"), "MEASURE_COLS"):
        assert "P2: null" in transform[name]


def test_multi_lang_source_name_patch():
    patch = _cell("NB_CREATE_DDL.ipynb", "mlsrcpy")
    ml = "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang"
    new = ("source_name", "STRING")
    assert _assign(patch, "NEW_COL") == new and _assign(patch, "ML_FQ") == ml
    tables = _assign(patch, "TABLE_COLS")
    assert list(tables) == [ml]
    base = _assign(_cell("NB_CREATE_DDL.ipynb", "mlexppy"), "TABLE_COLS")[ml]
    assert tables[ml] == _insert_after(base, "experience", new)
    assert _assign(patch, "PL") == _assign(_cell("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")[1][1]
    assert "LEASE_MINUTES = 90" in patch and "lock_exec_id = '{LOCK}'" in patch
    order = ["held = True", "Dừng trước khi ghi", "_refresh_lock()", "ALTER TABLE", "Sau khi ghi", "finally:"]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("CREATE TABLE", "INSERT INTO", "UPDATE {CFG}", "MERGE INTO", "DROP", "DELETE", "TRUNCATE",
                  "REPLACE", "RESTORE", "columnMapping", "lh_vv_gold"):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and " AFTER " in code
    acquire = patch.split("held = False", 1)[1].split("issues = []", 1)[0]
    assert acquire.index("held = True") < acquire.index("SELECT lock_exec_id")
    assert acquire.index("held = False") < acquire.index("raise RuntimeError")
    assert "raise failed from cleanup_exc" in patch


def test_review_text_and_title_rule():
    source = _cell("NB_GLD_SRV_POI_REVIEW.ipynb", "srvrvbuild")
    assert "slv_enr_poi_review_multi_lang" not in source
    assert '"lang"' not in source
    assert 'F.col("text").alias("review_text")' in source
    assert 'F.lit(None).cast("string").alias("title")' in source


def test_review_source_patch_cell():
    patch = _cell("NB_CREATE_DDL.ipynb", "rvi18ngldpy")
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "REPLACE", "RESTORE", "columnMapping", "ALTER TABLE", "INSERT INTO", "SET is_active = 1"):
        assert token not in code
    assert re.search(r"(?m)^\s*_refresh_lock\(\)", patch)
    assert patch.index("Dừng trước khi ghi") < re.search(r"(?m)^\s*_refresh_lock\(\)", patch).start()
    assert _assign(patch, "EDGES_OFF") == [("slv_enr_poi_review_multi_lang", "lh_vv_gold.dbo", "gld_srv_poi_review")]
    assert _assign(patch, "EDGES_KEEP") == ("slv_3p_poi_review", "slv_3p_poi_rating")
    strange = patch.split("for (pl, src_schema, src, flag), n in rows.items():", 1)[1].split("flags =", 1)[0]
    assert "flag == 1" not in strange
    assert "cạnh lạ" in strange
    assert patch.index("if issues:") < patch.index("UPDATE {CFG}")
    acquire = patch.split("owns_lock = False", 1)[1].split("issues = []", 1)[0]
    assert acquire.index("owns_lock = True") < acquire.index("SELECT lock_exec_id")
    assert "owns_lock = False" in acquire.split("SELECT lock_exec_id", 1)[1]
    assert "raise failed from cleanup_exc" in patch
    ids = [cell.get("id") for cell in _nb("NB_CREATE_DDL.ipynb")["cells"]]
    ids = ids[: ids.index("lgpnamepy") + 1]
    assert ids[-10:] == ["enrbrzcfgmd", "enrbrzcfgpy", "enrbrzmd", "enrbrzpy", "enrgldmd", "enrgldpy", "legacyidmd", "legacyidpy", "lgpnamemd", "lgpnamepy"]
    ids = ids[:-10]
    assert ids[-16:-12] == ["rvi18nenrmd", "rvi18nenrpy", "rvi18ngldmd", "rvi18ngldpy"]
    assert ids[-12:-10] == ["mlsrcmd", "mlsrcpy"]
    assert ids[-10:-8] == ["cmscfgmd", "cmscfgpy"]
    assert ids[-8:-6] == ["srvcovermd", "srvcoverpy"]
    assert ids[-6:-4] == ["poidestmd", "poidestpy"]
    assert ids[-4:-2] == ["enrmergemd", "enrmergepy"]
    assert ids[-2:] == ["srvactivemd", "srvactivepy"]


def test_review_source_name_literal():
    source = _cell("NB_GLD_SRV_POI_REVIEW.ipynb", "srvrvbuild")
    assert _assign(source, "SOURCE_NAME") == "google"
    assert 'F.lit(SOURCE_NAME).alias("source_name")' in source
    assert _assign(source, "OUT_COLS")[-2:] == ("author_name", "source_name")
    assert 'slv_3p_poi"' not in source


def test_info_destination_name_passthrough():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    assert _assign(source, "DEST_COLS")[2:4] == ("destination_id", "destination_name")
    out = _assign(source, "OUT_COLS")
    assert out[out.index("destination_id") + 1] == "destination_name"
    assert "destination_name_filled" in source


def test_info_is_active_patch_cell():
    patch = _cell("NB_CREATE_DDL.ipynb", "srvactivepy")
    assert _assign(patch, "NEW_COL") == ("is_active", "BOOLEAN")
    assert _assign(patch, "ANCHOR") == "is_bookable"
    poidest = _assign(_cell("NB_CREATE_DDL.ipynb", "poidestpy"), "TABLE_COLS")[INFO_FQ]
    at = [name for name, _dtype in poidest].index("is_bookable") + 1
    assert _assign(patch, "TABLE_COLS")[INFO_FQ] == poidest[:at] + [("is_active", "BOOLEAN")] + poidest[at:]
    assert _assign(patch, "PL") == _assign(_cell("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")[1][1]
    order = ["held = True", "Dừng trước khi ghi", "_refresh_lock()", "ADD COLUMNS", "Sau khi ghi", "finally:"]
    assert [patch.index(token) for token in order] == sorted(patch.index(token) for token in order)
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "REPLACE", "RESTORE", "columnMapping", "INSERT", "UPDATE {CFG}", "MERGE INTO"):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and code.count("ADD COLUMNS") == 1 and " AFTER " in code
    assert "LEASE_MINUTES = 90" in patch and "lock_exec_id = '{LOCK}'" in patch
    assert "raise failed from cleanup_exc" in patch


def test_info_is_active_literal_true():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    out = _assign(source, "OUT_COLS")
    assert out[out.index("is_bookable") + 1] == "is_active"
    assert source.count('F.lit(True).alias("is_active")') == 1
    assert "hash_exclude" not in source
    for call in re.findall(r"ctx\.input\((.*?)\)", source):
        assert "is_active" not in call
    text = (ROOT / "docs" / "context" / "mapping_gld_srv_poi_info.md").read_text(encoding="utf-8")
    table = text.split("### 1.2. Field Mapping", 1)[1].split("### 1.3", 1)[0]
    matched = False
    for line in table.splitlines():
        if not line.startswith("|"):
            continue
        cells = [item.strip() for item in line.strip("|").split("|")]
        if cells[-1] != "is_active":
            continue
        matched = True
        assert cells[0] == ""
        assert cells[1] == "boolean"
        assert cells[2].startswith("true")
    assert matched


def test_info_full_address_groups_no_concat_ws():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    assert "concat_ws" not in source
    assert 'F.concat(hn, sep, st, sep, F.col("formatted_address"))' in source
    assert "F.coalesce(g1, g2, g3)" in source
    assert 'sep = F.lit(", ")' in source


def test_info_full_address_blank_skips_group():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    assert 'F.when(F.trim(F.col(name)) != "", F.col(name))' in source
    assert "F.when(has_dest, F.coalesce(g1, g2, g3))" in source


def test_info_street_from_entity():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    assert "street" in _assign(source, "ENT_COLS")
    assert "street" not in _assign(source, "DEST_COLS")
    assert 'F.col("street").alias("street")' in source


def test_multi_lang_cost_guard():
    source = _cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild")
    assert source.index("GOLD_FQ") < source.index("def build") or "cost_vnd" in source.split("def build", 1)[1][:500]
    assert 'raise ConfigError("gld_srv_poi_multi_lang còn cost_vnd: chạy enrgldpy của NB_CREATE_DDL (runbook B5.1)")' in source


def test_no_cost_vnd_in_active_surface():
    for path in (ROOT / "notebooks").glob("NB_*.ipynb"):
        if path.name in {"NB_CREATE_DDL.ipynb", "NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb"}:
            continue
        text = path.read_text(encoding="utf-8")
        if path.name == "NB_GLD_SRV_POI_MULTI_LANG.ipynb":
            text = text.replace("cost_vnd", "")
        assert "cost_vnd" not in text, path.name
    pg = (ROOT / "sql" / "postgres" / "gld_srv_serve.pg.sql").read_text(encoding="utf-8")
    assert "RENAME COLUMN cost_vnd TO cost" in pg
    assert pg.count("cost_vnd") == 1
    java = ROOT / "services" / "data-serving-service" / "src" / "main"
    for path in java.rglob("*.java"):
        assert "cost_vnd" not in path.read_text(encoding="utf-8"), path.name


def test_old_price_story_patch_cell():
    ids = [cell.get("id") for cell in _nb("NB_CREATE_DDL.ipynb")["cells"]]
    assert ids[-4:] == ["lgpnamemd", "lgpnamepy", "oldpricemd", "oldpricepy"]
    patch = _cell("NB_CREATE_DDL.ipynb", "oldpricepy")
    assert _assign(patch, "NEW_COLS") == {INFO_FQ: OLDPRICE_INFO, ML_FQ: OLDPRICE_ML}
    active = _assign(_cell("NB_CREATE_DDL.ipynb", "srvactivepy"), "TABLE_COLS")[INFO_FQ]
    info = _assign(patch, "TABLE_COLS")[INFO_FQ]

    def _after(cols, anchor, extra):
        out = []
        for item in cols:
            out.append(item)
            if item[0] == anchor:
                out.extend(extra)
        return out

    want = _after(active, "full_address", [("old_address", "STRING")])
    want = _after(want, "review_count", OLDPRICE_INFO[1:])
    assert info == want
    ml = _assign(patch, "TABLE_COLS")[ML_FQ]
    assert [col for col in ml if col not in OLDPRICE_ML] == ML_BASE
    assert _assign(patch, "EDGES_ON") == [PRICE_EDGE]
    assert _assign(patch, "EDGES_KEEP") == (
        "slv_poi_entity_non_enrich", "slv_enr_poi_destination", "slv_enr_poi_info_multi_lang",
        "slv_3p_poi_rating", "slv_3p_poi_review", "slv_poi_media_info",
    )
    assert len(_assign(patch, "EDGES_KEEP")) == 6
    assert _assign(patch, "PL") == _assign(_cell("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")[1][1]
    assert _assign(patch, "OWNER_COL") == "load_origin"
    order = ["held = True", "Dừng trước khi ghi", "ALTER TABLE", "INSERT INTO {CFG}", "Sau khi ghi", "finally:"]
    assert [patch.index(token) for token in order] == sorted(patch.index(token) for token in order)
    assert patch.index("if issues:") < patch.index("ALTER TABLE")
    calls = [match.start() for match in re.finditer(r"(?m)^\s*_refresh_lock\(\)", patch)]
    alter, insert = patch.index("ALTER TABLE"), patch.index("INSERT INTO {CFG}")
    assert len(calls) == 2 and calls[0] < alter < calls[1] < insert
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "REPLACE", "RESTORE", "columnMapping", "MERGE INTO", "CREATE TABLE", "UPDATE {CFG}"):
        assert token not in code


def test_info_old_address_rule():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    assert _assign(source, "OLD_ADDR") == ("old_formatted_address", "old_ward_with_type", "old_city_with_type")
    out = _assign(source, "OUT_COLS")
    assert out[out.index("full_address") + 1] == "old_address"
    for line in (
        'og1 = F.concat(hn, sep, st, sep, F.col("old_formatted_address"))',
        'og2 = F.concat(hn, sep, st, sep, F.col("old_ward_with_type"), sep, F.col("old_city_with_type"))',
        "old_address = F.when(has_dest, F.coalesce(og1, og2, g3))",
    ):
        assert line in source
    for name in ("old_house_number", "old_street", "old_full_address"):
        assert name not in source
    assert source.count('F.col("_e_full_address")') == 1
    assert set(_assign(source, "OLD_ADDR")).isdisjoint(_assign(source, "DEST_COLS"))


def test_info_price_rule():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    assert _assign(source, "PRICE_COLS") == ("poi_id", "price_level", "price_min", "price_max")
    assert _assign(source, "PRICE_TYPES") == {"price_level": "int", "price_min": "decimal(18,2)", "price_max": "decimal(18,2)"}
    out = _assign(source, "OUT_COLS")
    assert out[out.index("review_count") + 1: out.index("review_count") + 4] == ("price_level", "price_min", "price_max")
    assert out[-2:] == ("cover_id", "cover_blob_url")
    assert 'pr = ctx.input("price")' in source
    assert "poi_id có hơn một dòng" in source
    assert '.join(price, "poi_id", "left")' in source
    assert "currency" not in source
    body = source.split("def _price", 1)[1].split("\ndef ", 1)[0]
    code = "\n".join(line for line in body.splitlines() if not line.strip().startswith("#"))
    assert "source_name" not in code


def test_multi_lang_story_local_tips_rule():
    source = _cell("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild")
    assert _assign(source, "I18N_TEXT_COLS") == ("story", "local_tips")
    assert source.count('F.col("locale").alias("_loc"), "bio", "usps", *I18N_TEXT_COLS)') == 2
    assert '_require(i18n, I18N_TEXT_COLS, "slv_pn_business_service_i18ns")' in source
    assert '_require(i18n, ("business_service_id", "locale", "bio", "usps"), "slv_pn_business_service_i18ns")' in source
    assert 'coalesce(F.col("story")' not in source
    assert 'coalesce(F.col("local_tips")' not in source


def test_old_price_story_mapping_rows():
    text = MAPPING.read_text(encoding="utf-8")
    table = text.split("### 1.2. Field Mapping", 1)[1].split("### 1.3", 1)[0]
    assert "old_formatted_address" in table and "old_ward_with_type" in table and "old_city_with_type" in table
    for name in ("price_level", "price_min", "price_max"):
        assert f"slv_3p_poi_price.{name}" in table
    assert "integer" in table and "decimal(18,2)" in table
    handling = text.split("### 1.1. Xử lý", 1)[1].split("### 1.6", 1)[0]
    assert "slv_3p_poi_price" in handling and "price_matched" in handling
    ml = ML_MAPPING.read_text(encoding="utf-8")
    ml_table = ml.split("### 1.2. Field Mapping", 1)[1]
    assert "slv_pn_business_service_i18ns.story" in ml_table
    assert "slv_pn_business_service_i18ns.local_tips" in ml_table
    assert "không fallback" in ml_table

