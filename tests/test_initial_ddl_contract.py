"""Contract of the empty-environment DDL notebook against the repository sources."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'"
EXCLUDED = {
    "init_cfg_partner",
    "init_cfg_3p",
    "init_registry_pure",
    "init_seed_place_type",
    "init_seed_amenity",
}
DESTRUCTIVE = (
    "DROP ",
    "DELETE FROM",
    "TRUNCATE",
    "ALTER TABLE",
    "UPDATE ",
    "WHEN MATCHED",
    "replaceWhere",
    'mode("overwrite")',
    "INSERT INTO",
)


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _text(cell: dict) -> str:
    return "".join(cell["source"])


def _cell(nb: dict, prefix: str) -> str:
    found = [cell for cell in nb["cells"] if str(cell.get("id", "")).startswith(prefix)]
    if len(found) != 1:
        raise AssertionError(f"{prefix}: {len(found)} cells")
    return _text(found[0])


def _initial() -> dict:
    return _notebook("NB_SETUP_INITIAL_DDL.ipynb")


def _by_id(nb: dict) -> dict:
    return {cell["id"]: _text(cell) for cell in nb["cells"]}


def _marker(source: str, begin: str, end: str) -> str:
    start = source.index(begin)
    stop = source.index(end) + len(end)
    return source[start:stop].strip()


def _assign(source: str, name: str):
    tree = ast.parse(source)
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _exec_assigns(source: str, names: set[str]) -> dict:
    tree = ast.parse(source)
    namespace: dict = {}
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if any(isinstance(target, ast.Name) and target.id in names for target in targets):
            exec(ast.unparse(node), namespace)  # noqa: S102 - assignment copied from a repo cell
    return namespace


def strip_sql_comments(text: str) -> str:
    out: list[str] = []
    quote = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "'":
            if quote and index + 1 < len(text) and text[index + 1] == "'":
                out.append("''")
                index += 2
                continue
            quote = not quote
            out.append(char)
        elif not quote and text.startswith("--", index):
            while index < len(text) and text[index] != "\n":
                index += 1
            continue
        else:
            out.append(char)
            index += 1
            continue
        index += 1
    return "".join(out)


def _split_top(body: str) -> list[str]:
    parts: list[str] = []
    buf: list[str] = []
    quote = False
    depth = 0
    index = 0
    while index < len(body):
        char = body[index]
        if char == "'":
            if quote and index + 1 < len(body) and body[index + 1] == "'":
                buf.append("''")
                index += 2
                continue
            quote = not quote
            buf.append(char)
        elif not quote and char == "(":
            depth += 1
            buf.append(char)
        elif not quote and char == ")":
            depth -= 1
            buf.append(char)
        elif not quote and char == "," and depth == 0:
            parts.append("".join(buf))
            buf = []
        else:
            buf.append(char)
        index += 1
    if "".join(buf).strip():
        parts.append("".join(buf))
    return parts


_COL_RE = re.compile(
    r"^([A-Za-z_][A-Za-z0-9_]*)\s+"
    r"([A-Za-z]+(?:\s*\(\s*\d+\s*(?:,\s*\d+\s*)?\))?)"
    r"(\s+NOT\s+NULL)?"
    r"(?:\s+COMMENT\s+'((?:[^']|'')*)')?\s*$",
    re.IGNORECASE,
)


def parse_creates(sql: str) -> dict:
    clean = strip_sql_comments(sql)
    specs = {}
    upper = clean.upper()
    key = "CREATE TABLE IF NOT EXISTS"
    pos = 0
    while True:
        at = upper.find(key, pos)
        if at < 0:
            break
        rest = clean[at + len(key):].lstrip()
        name, _, rest = rest.partition("(")
        depth = 1
        quote = False
        index = 0
        while index < len(rest) and depth:
            char = rest[index]
            if char == "'":
                if quote and index + 1 < len(rest) and rest[index + 1] == "'":
                    index += 2
                    continue
                quote = not quote
            elif not quote and char == "(":
                depth += 1
            elif not quote and char == ")":
                depth -= 1
            index += 1
        body, tail = rest[: index - 1], rest[index:]
        semi = None
        quote = False
        for cursor, char in enumerate(tail):
            if char == "'":
                if quote and cursor + 1 < len(tail) and tail[cursor + 1] == "'":
                    continue
                quote = not quote
            elif char == ";" and not quote:
                semi = cursor
                break
        if semi is not None:
            tail = tail[:semi]
        cols = []
        for part in _split_top(body):
            match = _COL_RE.match(" ".join(part.split()))
            if not match:
                raise AssertionError(f"bad column in {name.strip()}: {part!r}")
            dtype = " ".join(match.group(2).split())
            if match.group(3):
                dtype += " NOT NULL"
            comment = match.group(4).replace("''", "'") if match.group(4) else None
            cols.append((match.group(1), dtype, comment))
        tail_upper = tail.upper()
        partition = None
        if "PARTITIONED BY" in tail_upper:
            inner = tail[tail_upper.find("PARTITIONED BY"):].split("(", 1)[1].split(")", 1)[0]
            partition = [item.strip() for item in inner.split(",") if item.strip()]
        specs[name.strip()] = {"cols": cols, "partition": partition}
        pos = at + len(key)
    return specs


def _specs():
    namespace: dict = {}
    exec(_by_id(_initial())["init_tables"], namespace)  # noqa: S102 - pure table spec cell
    return namespace["TABLE_SPECS"], namespace


def test_param_default_false():
    cell = next(item for item in _initial()["cells"] if item["id"] == "init_param")
    assert _text(cell) == 'p_apply = "false"\n'
    assert cell["metadata"]["tags"] == ["parameters"]


def test_plan_precedes_writes():
    cells = _initial()["cells"]
    order = [cell["id"] for cell in cells]
    assert order.index("init_param") < order.index("init_plan") < order.index("init_ddl")
    assert order.index("init_ddl") < order.index("init_seed_write")
    plan_at = order.index("init_plan")
    for cell in cells[:plan_at]:
        if cell["cell_type"] != "code":
            continue
        text = _text(cell)
        assert "spark.sql(" not in text
        assert ".write" not in text
        assert "saveAsTable" not in text
    plan = _text(cells[plan_at])
    assert "if not apply:" in plan
    assert "notebookutils.notebook.exit" in plan


def test_no_destructive_sql():
    for cell in _initial()["cells"]:
        if cell["cell_type"] != "code":
            continue
        text = _text(cell)
        if cell["id"] in EXCLUDED:
            assert "spark.sql(" not in text
            assert ".write" not in text
            assert "saveAsTable" not in text
            continue
        code = "\n".join(line for line in text.splitlines() if not line.strip().startswith("#"))
        for token in DESTRUCTIVE:
            assert token not in code, cell["id"]
        if "MERGE INTO" in code:
            assert "WHEN NOT MATCHED THEN INSERT" in code


def test_target_duplicate_keys_block_apply_and_verify():
    cells = _by_id(_initial())
    plan = cells["init_plan"]
    verify = cells["init_verify"]
    assert "def _target_dup_keys(table, keys):" in plan
    assert "if not table_exists(table):" in plan
    assert "FROM {table} GROUP BY" in plan
    assert plan.index("_target_dup_keys(table, SEED_KEYS[name])") < plan.index('raise ConfigError("\\n".join(schema_issues))')
    assert plan.index('raise ConfigError("\\n".join(schema_issues))') < plan.index("notebookutils.notebook.exit")
    assert "_target_dup_keys(table, SEED_KEYS[name])" in verify
    assert "dup_target" in verify
    assert 'raise ConfigError("\\n".join(verify_errors))' in verify
    order = [cell["id"] for cell in _initial()["cells"]]
    assert order.index("init_plan") < order.index("init_ddl") < order.index("init_verify")


def test_table_inventory_matches_sources():
    specs, _namespace = _specs()
    found = set()
    for name in ("NB_CREATE_DDL.ipynb", "NB_SETUP_POI_ENTITY.ipynb", "NB_SETUP_POI_AMENITY.ipynb"):
        text = "\n".join(_text(cell) for cell in _notebook(name)["cells"])
        found.update(re.findall(r"CREATE TABLE IF NOT EXISTS (lh_vv_\w+\.\w+\.\w+)", text))
    enr = _cell(_notebook("NB_CREATE_DDL.ipynb"), "enrddlpy")
    found.update(_assign(enr, "INFO_COLS") and {
        "lh_vv_gold.enr.gld_enr_poi_info",
        "lh_vv_gold.enr.gld_enr_poi_review",
    })
    entity = _cell(_notebook("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb"), "b1entitybuild")
    match = re.search(r'trg_tbl\s*=\s*"([^"]+)"', entity)
    assert match
    found.add("lh_vv_silver.dbo." + match.group(1))
    ddl = _notebook("NB_CREATE_DDL.ipynb")
    found.update(_assign(_cell(ddl, "enrflagpy"), "LANDING_COLS").keys())
    found.update(_assign(_cell(ddl, "srvpoipy"), "GOLD_COLS").keys())
    found.update(_exec_assigns(_cell(ddl, "mediaddlpy"), {"MEDIA_COLS", "TABLE_COLS"})["TABLE_COLS"])
    found.update(_exec_assigns(_cell(ddl, "amenddlpy"), {"AMENITY_COLS", "TABLE_COLS"})["TABLE_COLS"])
    assert {spec["fq"] for spec in specs} == found
    assert len(specs) == 21
    plan = _by_id(_initial())["init_plan"]
    assert f"len(fqs) != {len(specs)}" in plan
    assert f"TABLE_SPECS cần {len(specs)} fq duy nhất" in plan


def test_columns_match_sources():
    specs, _namespace = _specs()
    by_fq = {spec["fq"]: spec for spec in specs}
    parsed = {}
    ddl = _notebook("NB_CREATE_DDL.ipynb")
    for prefix in ("80154b61", "3ea73e14", "d06c9671", "7dad05d9"):
        parsed.update(parse_creates(_cell(ddl, prefix)))
    parsed.update(parse_creates(_cell(_notebook("NB_SETUP_POI_ENTITY.ipynb"), "a1setupddl")))
    parsed.update(parse_creates(_cell(_notebook("NB_SETUP_POI_AMENITY.ipynb"), "c1setupddl")))
    pipe = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
    assert parsed[pipe]["cols"] == by_fq[pipe]["cols"][:-1]
    assert by_fq[pipe]["cols"][-1] == ("nb_name", "STRING", None)
    for fq, source in parsed.items():
        if fq == pipe:
            continue
        assert by_fq[fq]["cols"] == source["cols"]
        assert by_fq[fq]["partition"] == source["partition"]
    flag = _cell(ddl, "enrflagpy")
    ml_cols = _assign(_cell(ddl, "mlexppy"), "TABLE_COLS")
    for fq, name in {
        "lh_vv_gold.enr.gld_enr_poi_info": "INFO_COLS",
        "lh_vv_gold.enr.gld_enr_poi_review": "REVIEW_COLS",
    }.items():
        assert by_fq[fq]["cols"] == [(col, dtype, None) for col, dtype in _assign(flag, name)]
        assert by_fq[fq]["props"] == PROPS
    dest = "lh_vv_silver.dbo.slv_enr_poi_destination"
    srv = _cell(ddl, "srvpoipy")
    for fq, cols in _assign(flag, "LANDING_COLS").items():
        if fq == dest:
            cols = cols + _assign(srv, "DEST_NEW_COLS")
        if fq in ml_cols:
            cols = ml_cols[fq]
        assert by_fq[fq]["cols"] == [(col, dtype, None) for col, dtype in cols]
        assert by_fq[fq]["props"] == PROPS
    gold = _assign(srv, "GOLD_COLS")
    gold["lh_vv_gold.dbo.gld_srv_poi_info"] = _assign(_cell(ddl, "srvratepy"), "INFO_COLS")
    gold["lh_vv_gold.dbo.gld_srv_poi_multi_lang"] = ml_cols["lh_vv_gold.dbo.gld_srv_poi_multi_lang"]
    for fq, cols in gold.items():
        assert by_fq[fq]["cols"] == [(col, dtype, None) for col, dtype in cols]
        assert by_fq[fq]["props"] == PROPS
    for cell_id, names in (
        ("mediaddlpy", {"MEDIA_COLS", "TABLE_COLS"}),
        ("amenddlpy", {"AMENITY_COLS", "TABLE_COLS"}),
    ):
        for fq, cols in _exec_assigns(_cell(ddl, cell_id), names)["TABLE_COLS"].items():
            assert by_fq[fq]["cols"] == [(col, dtype, None) for col, dtype in cols]
            assert by_fq[fq]["props"] == PROPS
    assert by_fq["lh_vv_ctrl.dbo.ctrl_cdc_state"]["partition"] == ["src_tbl"]
    assert by_fq["lh_vv_ctrl.dbo.ctrl_cdc_reject"]["partition"] == ["src_tbl"]


def test_poi_entity_columns_derived():
    specs, namespace = _specs()
    spec = specs[-1]
    initial = _by_id(_initial())
    pure = _marker(initial["init_registry_pure"], "# BEGIN_REGISTRY_PURE", "# END_REGISTRY_PURE")
    env: dict = {}
    exec(pure, env)  # noqa: S102 - pure registry helpers
    exec(initial["init_cfg_3p"], env)  # noqa: S102 - verbatim config cell
    exec(initial["init_cfg_partner"], env)  # noqa: S102 - verbatim config cell
    rows = env["flatten_table_configs"](env["TABLE_CONFIGS_3P"], "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream")
    registry = [
        (row["trg_column"], row["data_type"])
        for row in sorted(
            (row for row in rows if row["trg_tbl"] == "slv_3p_poi" and row["is_active"]),
            key=lambda row: row["column_order"],
        )
    ]
    extract = _cell(_notebook("NB_LIB_EXTRACT_RAWDATA.ipynb"), "b756d39b")
    transform = _cell(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"), "9ff87eee")
    build = _cell(_notebook("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb"), "b1entitybuild")
    place = _cell(_notebook("NB_SETUP_POI_ENTITY.ipynb"), "a1setupddl")
    snap = _exec_assigns(extract, {"AUDIT_COLUMNS", "SNAPSHOT_TECH_COLUMNS"})
    tech = _exec_assigns(transform, {"TECH_COLUMNS", "TECH_NAMES"})
    poi_cols = _assign(build, "POI_COLS")
    contact_cols = _assign(build, "CONTACT_COLS")
    address_cols = _assign(build, "ADDRESS_COLS")
    category = _assign(build, "CATEGORY_COLS")
    estimate_cols = _assign(build, "ESTIMATE_COLS")
    expected_types = {name: dtype for name, dtype, _nullable in _assign(place, "EXPECTED")}
    names = set(tech["TECH_NAMES"])
    snap_names = {name for name, _dtype in snap["SNAPSHOT_TECH_COLUMNS"]}
    address = {
        row["trg_column"]: row["data_type"]
        for row in rows
        if row["trg_tbl"] == "slv_3p_poi_address" and row["is_active"]
    }
    contact = {
        row["trg_column"]: row["data_type"]
        for row in rows
        if row["trg_tbl"] == "slv_3p_poi_contact" and row["is_active"]
    }
    svc = {
        row["trg_column"]: row["data_type"]
        for row in env["flatten_table_configs"](env["TABLE_CONFIGS"], "lh_vv_bronze.dbo", "partner_raw_data")
        if row["trg_tbl"] == "slv_pn_business_services" and row["is_active"]
    }
    expected = [col for col in registry if col[0] not in names and col[0] not in snap_names]
    expected += [(name, contact[name]) for name in contact_cols]
    expected += [(name, address[name]) for name in address_cols]
    expected += [(name, expected_types[name]) for name in category]
    hours = {
        row["trg_column"]: row["data_type"]
        for row in rows
        if row["trg_tbl"] == "slv_3p_poi_opening_hours" and row["is_active"]
    }
    assert hours["periods_json"].lower() == "string"
    assert _assign(build, "HOURS_COLS") == ("opening_hours_text",)
    assert _assign(build, "DETAIL_COLS") == ("phone", "email", "holiday_exceptions")
    assert contact["phone"].lower() == svc["phone"].lower() == svc["email"].lower() == "string"
    expected += [(name, expected_types[name]) for name in estimate_cols]
    expected += [("opening_hours_text", hours["periods_json"])]
    expected += [("phone", contact["phone"]), ("email", svc["email"]), ("holiday_exceptions", "string")]
    expected += list(tech["TECH_COLUMNS"])
    got = [(name, dtype.lower()) for name, dtype, _comment in spec["cols"]]
    assert got == [(name, dtype.lower()) for name, dtype in expected]
    assert [name for name, _dtype in expected if name in set(poi_cols)][:len(poi_cols)] == list(poi_cols)
    assert all("NOT NULL" not in dtype and comment is None for _name, dtype, comment in spec["cols"])
    assert spec["props"] == PROPS and spec["partition"] is None
    assert spec["fq"] == "lh_vv_silver.dbo.slv_poi_entity_non_enrich"
    kept = {name for name, _dtype in tech["TECH_COLUMNS"]}
    assert (snap_names - kept).isdisjoint({name for name, _dtype, _comment in spec["cols"]})
    assert _assign(build, "POI_COLS") == poi_cols
    assert _assign(build, "ADDRESS_COLS") == address_cols
    assert category == ("business_sector", "business_category", "business_category_vi", "category_group")
    assert "create_sql" in namespace


def test_create_sql_renders():
    specs, namespace = _specs()
    create_sql = namespace["create_sql"]
    partitioned = []
    for spec in specs:
        sql = create_sql(spec)
        assert sql.startswith("CREATE TABLE IF NOT EXISTS " + spec["fq"])
        for name, _dtype, _comment in spec["cols"]:
            assert f"`{name}`" in sql
        if "PARTITIONED BY (src_tbl)" in sql:
            partitioned.append(spec["fq"])
    assert partitioned == [
        "lh_vv_ctrl.dbo.ctrl_cdc_state",
        "lh_vv_ctrl.dbo.ctrl_cdc_reject",
    ]


def test_registry_configs_equal_create_ddl():
    initial = _by_id(_initial())
    ddl = _notebook("NB_CREATE_DDL.ipynb")
    assert initial["init_cfg_partner"].strip() == _cell(ddl, "28e2be98").strip()
    assert initial["init_cfg_3p"].strip() == _cell(ddl, "e9c137c5").strip()


def test_registry_rows_valid():
    initial = _by_id(_initial())
    env: dict = {}
    exec(_marker(initial["init_registry_pure"], "# BEGIN_REGISTRY_PURE", "# END_REGISTRY_PURE"), env)  # noqa: S102
    exec(initial["init_cfg_3p"], env)  # noqa: S102
    rows = env["flatten_table_configs"](env["TABLE_CONFIGS_3P"], "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream")
    env["validate_rows"](env["TABLE_CONFIGS_3P"], rows)
    assert len(rows) == 53
    keys = [(row["src_schema"], row["src_tbl"], row["trg_schema"], row["trg_tbl"], row["trg_column"]) for row in rows]
    assert len(keys) == len(set(keys))


def test_ref_seed_blocks_identical():
    initial = _by_id(_initial())
    place = _cell(_notebook("NB_SETUP_POI_ENTITY.ipynb"), "a1setupseed")
    amenity = _cell(_notebook("NB_SETUP_POI_AMENITY.ipynb"), "c1setupseed")
    assert _marker(initial["init_seed_place_type"], "# BEGIN_PLACE_TYPE_SEED", "# END_PLACE_TYPE_SEED") == place.strip()
    assert _marker(initial["init_seed_amenity"], "# BEGIN_AMENITY_SEED", "# END_AMENITY_SEED") == amenity.strip()
    assert "PLACE_TYPE_ROWS = list(SEED_ROWS)" in initial["init_seed_place_type"]
    assert "AMENITY_ROWS = list(SEED_ROWS)" in initial["init_seed_amenity"]


def _sql_string(token: str):
    token = token.strip()
    if token.upper() == "NULL":
        return None
    assert token.startswith("'") and token.endswith("'")
    return token[1:-1].replace("''", "'")


def test_pipeline_config_rows_match_sources():
    ddl = _notebook("NB_CREATE_DDL.ipynb")
    cfg = _cell(ddl, "80154b61")
    partner_sql, _, third_sql = cfg.partition("-- 3. INSERT")
    partner = re.findall(r"\(\s*\d+\s*,\s*'(slv_pn_[^']+)'\s*\)", partner_sql)
    third = re.findall(
        r"\(\s*\d+\s*,\s*'([^']+)'\s*,\s*'([^']+)'\s*,\s*(NULL|'(?:[^']*)')\s*,\s*(NULL|'(?:[^']*)')\s*,\s*(\d+)\s*\)",
        third_sql,
    )
    edges = _assign(_cell(ddl, "enrddlpy"), "EDGES")
    off = set(map(tuple, _assign(_cell(ddl, "enrinfopy"), "EDGES_OFF")))
    added = _assign(_cell(ddl, "enrinfopy"), "EDGES_ON")
    flagged = _assign(_cell(ddl, "enrflagpy"), "EDGES_ON")
    hours_off = {(src, target) for src, _schema, target in _assign(_cell(ddl, "ohpasspy"), "EDGES_OFF")}
    hours_on = _assign(_cell(ddl, "ohpasspy"), "EDGES_ON")
    deleted = {(src, target) for src, _schema, target in _assign(_cell(ddl, "mvpoipy"), "EDGES_DELETE")}
    bronze, silver = "lh_vv_bronze.dbo", "lh_vv_silver.dbo"
    flow = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"
    enr = "PL_VV_TRANS_SLV_TO_ENR_15M"
    expected = []
    for target in partner:
        priority = 2 if target.startswith("slv_pn_product") else 1
        expected.append((flow, bronze, "partner_raw_data", silver, target, 1, priority, "CDC", None, None, None))
    for target, mode, align, dedup, active in third:
        expected.append((
            flow, bronze, "brz_3rd_crawler_poi_stream", silver, target, int(active), 1, mode,
            _sql_string(align), _sql_string(dedup), None,
        ))
    for _seq, src, schema, target, mode, notebook, priority in edges:
        if (src, target) in deleted:
            continue
        active = 0 if (src, target) in off or (src, target) in hours_off else 1
        expected.append((enr, silver, src, schema, target, active, priority, mode, None, None, notebook))
    for seq, src, schema, target, mode, notebook, priority in added:
        if (src, target) in deleted:
            continue
        expected.append((enr, silver, src, schema, target, 1, priority, mode, None, None, notebook))
        assert seq > 0
    for seq, src, schema, target, mode, notebook, priority in flagged:
        if (src, target) in deleted:
            continue
        expected.append((enr, silver, src, schema, target, 1, priority, mode, None, None, notebook))
        assert seq > 0
    for src in (
        "slv_3p_poi", "slv_3p_poi_address", "ref_dictionary_place_type",
        "slv_pn_business_services", "slv_pn_business_service_i18ns", "slv_3p_poi_contact",
    ):
        expected.append((enr, silver, src, silver, "slv_poi_entity_non_enrich", 1, 1, "RECOMPUTE", None, None, None))
    for src, schema, trg, mode in hours_on:
        expected.append((enr, silver, src, schema, trg, 1, 1, mode, None, None, None))
    for src in ("slv_3p_poi_amenity", "slv_poi_entity_non_enrich", "ref_dictionary_amenities"):
        expected.append((enr, silver, src, silver, "slv_poi_amenity", 1, 1, "RECOMPUTE", None, None, None))
    gld = "PL_VV_TRANS_SLV_TO_GLD_30M"
    renames = {old: new for old, new, _lease in _assign(_cell(ddl, "plcadpy"), "RENAMES")}
    assert renames[_assign(_cell(ddl, "srvpoipy"), "PL")] == gld
    assert [new for old, new in renames.items() if old in _cell(ddl, "enrddlpy")] == [enr]
    for seq, src, schema, target, mode, notebook, priority in _assign(_cell(ddl, "srvpoipy"), "EDGES_ON"):
        expected.append((gld, silver, src, schema, target, 1, priority, mode, None, None, notebook))
        assert seq > 0
    for seq, src, schema, target, mode, notebook, priority in _assign(_cell(ddl, "srvratepy"), "EDGES_ON"):
        expected.append((gld, silver, src, schema, target, 1, priority, mode, None, None, notebook))
        assert seq > 0
    for seq, src, schema, target, mode, notebook, priority in _assign(_cell(ddl, "mediaddlpy"), "EDGES_ON"):
        expected.append((gld, silver, src, schema, target, 1, priority, mode, None, None, notebook))
        assert seq > 0
    for seq, src, schema, target, mode, notebook, priority in _assign(_cell(ddl, "amenddlpy"), "EDGES_ON"):
        expected.append(("PL_VV_TRANS_SLV_TO_GLD_1H", silver, src, schema, target, 1, priority, mode, None, None, notebook))
        assert seq > 0
    namespace: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], namespace)  # noqa: S102
    assert namespace["PIPELINE_CONFIG_ROWS"] == expected
    assert len(expected) == 66


def test_watermark_rows_match_source():
    source = _cell(_notebook("NB_CREATE_DDL.ipynb"), "3ea73e14")
    namespace: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], namespace)  # noqa: S102
    rows = namespace["WATERMARK_ROWS"]
    assert rows == [
        ("wm_transform_partner_raw_data", "lh_vv_bronze.dbo", "partner_raw_data", "EventProcessedUtcTime",
         "INITIALIZED", "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV", -1),
        ("wm_transform_brz_3rd_crawler_poi_stream", "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream", "crawled_at",
         "INITIALIZED", "NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV", -1),
    ]
    for row in rows:
        assert row[0] in source and row[3] in source and row[5] in source


def test_example_patch_dual_update():
    enr = _cell(_notebook("NB_CREATE_DDL.ipynb"), "enrddlpy")
    assert 'if "nb_name" not in cols:' in enr
    assert "ALTER TABLE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config ADD COLUMNS (nb_name STRING)" in enr
    specs, _namespace = _specs()
    assert ("nb_name", "STRING", None) in specs[0]["cols"]
    create = _cell(_notebook("NB_CREATE_DDL.ipynb"), "80154b61").split("-- 2. INSERT", 1)[0]
    assert "nb_name" not in create
    assert "ADD COLUMNS" not in "\n".join(_text(cell) for cell in _initial()["cells"])


def test_dropped_l1_columns_unread():
    initial = _by_id(_initial())
    env: dict = {}
    exec(_marker(initial["init_registry_pure"], "# BEGIN_REGISTRY_PURE", "# END_REGISTRY_PURE"), env)  # noqa: S102
    exec(initial["init_cfg_3p"], env)  # noqa: S102
    rows = env["flatten_table_configs"](env["TABLE_CONFIGS_3P"], "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream")
    pairs = {(row["trg_tbl"], row["trg_column"]) for row in rows}
    assert ("slv_3p_poi", "subcategory_tags_json") not in pairs
    assert ("slv_3p_poi_address", "state_province") not in pairs
    specs, _namespace = _specs()
    names = {name for spec in specs for name, _dtype, _comment in spec["cols"]}
    assert "subcategory_tags_json" not in names
    assert "state_province" not in names

    def code(name):
        parts = []
        for item in _notebook(name)["cells"]:
            if item.get("cell_type") != "code":
                continue
            for line in _text(item).splitlines():
                if line.strip().startswith("#"):
                    continue
                parts.append(line.split("#", 1)[0])
        return "\n".join(parts)

    for name in ("NB_ENR_POI_INFO.ipynb", "NB_SLV_POI_ENTITY_NON_ENRICH.ipynb"):
        text = code(name)
        assert "state_province" not in text
        assert "subcategory_tags_json" not in text


def test_roles_documented():
    naming = (ROOT / "docs/context/02_NAMING_CONVENTION.md").read_text(encoding="utf-8")
    assert "### 2.1 Hai notebook DDL" in naming
    assert "NB_SETUP_INITIAL_DDL" in naming and "NB_CREATE_DDL" in naming
    agents = (ROOT / "AGENTS.md").read_text(encoding="utf-8")
    assert "NB_SETUP_INITIAL_DDL" in agents
    assert (ROOT / "AGENTS.md").stat().st_size < 8192


def test_flag_patch_create_matches_init():
    specs, namespace = _specs()
    patch = _cell(_notebook("NB_CREATE_DDL.ipynb"), "enrflagpy")
    module = ast.parse(patch)
    selected = []
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_create_sql":
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == "PROPS" for target in node.targets
        ):
            selected.append(node)
    env: dict = {}
    exec(ast.unparse(ast.Module(body=selected, type_ignores=[])), env)  # noqa: S102
    contracts = {
        "lh_vv_gold.enr.gld_enr_poi_info": _assign(patch, "INFO_COLS"),
        "lh_vv_gold.enr.gld_enr_poi_review": _assign(patch, "REVIEW_COLS"),
        **_assign(patch, "LANDING_COLS"),
    }
    dest = "lh_vv_silver.dbo.slv_enr_poi_destination"
    extra = _assign(_cell(_notebook("NB_CREATE_DDL.ipynb"), "srvpoipy"), "DEST_NEW_COLS")
    ml = "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang"
    ml_cols = _assign(_cell(_notebook("NB_CREATE_DDL.ipynb"), "mlexppy"), "TABLE_COLS")
    create_sql = namespace["create_sql"]
    for fq, cols in contracts.items():
        if fq == dest:
            cols = cols + extra
        if fq == ml:
            cols = ml_cols[fq]
        spec = next(item for item in specs if item["fq"] == fq)
        assert env["_create_sql"](fq, cols) == create_sql(spec)


def test_gld_srv_patch_create_matches_init():
    specs, namespace = _specs()
    patch = _cell(_notebook("NB_CREATE_DDL.ipynb"), "srvpoipy")
    module = ast.parse(patch)
    selected = []
    for node in module.body:
        if isinstance(node, ast.FunctionDef) and node.name == "_create_sql":
            selected.append(node)
        elif isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id in {"PROPS", "DEST_BASE", "DEST_NEW_COLS", "GOLD_COLS"}
            for target in node.targets
        ):
            selected.append(node)
    env: dict = {}
    exec(ast.unparse(ast.Module(body=selected, type_ignores=[])), env)  # noqa: S102
    create_sql = namespace["create_sql"]
    dest = "lh_vv_silver.dbo.slv_enr_poi_destination"
    contracts = {fq: cols for fq, cols in env["GOLD_COLS"].items()}
    contracts[dest] = env["DEST_BASE"] + env["DEST_NEW_COLS"]
    contracts["lh_vv_gold.dbo.gld_srv_poi_info"] = _assign(
        _cell(_notebook("NB_CREATE_DDL.ipynb"), "srvratepy"), "INFO_COLS")
    contracts["lh_vv_gold.dbo.gld_srv_poi_multi_lang"] = _assign(
        _cell(_notebook("NB_CREATE_DDL.ipynb"), "mlexppy"), "TABLE_COLS")["lh_vv_gold.dbo.gld_srv_poi_multi_lang"]
    for fq, cols in contracts.items():
        spec = next(item for item in specs if item["fq"] == fq)
        assert env["_create_sql"](fq, cols) == create_sql(spec)
    flag = _cell(_notebook("NB_CREATE_DDL.ipynb"), "enrflagpy")
    assert env["DEST_BASE"] == _assign(flag, "LANDING_COLS")[dest]


def test_gld_srv_patch_guards():
    patch = _cell(_notebook("NB_CREATE_DDL.ipynb"), "srvpoipy")
    order = ["held = True", "Dừng trước khi ghi", "ALTER TABLE", "INSERT INTO {CFG}", "Sau khi ghi", "finally:"]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "UPDATE {CFG}", "REPLACE", "columnMapping", " AFTER "):
        assert token not in code
    assert code.count("ALTER TABLE") == 1
    assert "LEASE_MINUTES = 90" in patch
    assert "lock_exec_id = '{LOCK}'" in patch
    assert patch.count("_refresh_lock()") == 4
    assert patch.index("_refresh_lock()") < patch.index("ALTER TABLE")
    assert patch.rindex("_refresh_lock()") < patch.index("INSERT INTO {CFG}")
    assert "src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name" in patch


def test_enr_initial_edge_state():
    from test_enr_poi_contract import INFO_INPUTS, REVIEW_INPUTS

    seed = _by_id(_initial())["init_seed_ctrl"]
    namespace: dict = {}
    exec(seed, namespace)  # noqa: S102
    rows = namespace["PIPELINE_CONFIG_ROWS"]
    enr = "PL_VV_TRANS_SLV_TO_ENR_15M"
    removed = {"slv_pn_poi", "gld_enr_poi_coordinate"}
    old_info = {
        ("slv_3p_poi", "gld_enr_poi_info"),
        ("slv_3p_poi_address", "gld_enr_poi_info"),
        ("slv_3p_poi_contact", "gld_enr_poi_info"),
    }
    active = {src for _pl, _ss, src, _ts, trg, active_flag, *_rest in rows if trg == "gld_enr_poi_info" and active_flag == 1}
    review_active = {
        src for _pl, _ss, src, _ts, trg, active_flag, *_rest in rows
        if trg == "gld_enr_poi_review" and active_flag == 1
    }
    assert active == set(INFO_INPUTS)
    assert review_active == set(REVIEW_INPUTS)
    assert not any(row[0] == "PL_VV_TRANS_SLV_TO_SLV_1H" for row in rows)
    assert not any(src in removed or trg in removed for _pl, _ss, src, _ts, trg, *_rest in rows)
    assert not any((src, trg) in old_info for _pl, _ss, src, _ts, trg, *_rest in rows)
    owners: dict = {}
    for pl, _ss, _src, schema, trg, active_flag, *_rest in rows:
        if active_flag == 1:
            owners.setdefault((schema, trg), set()).add(pl)
    assert all(len(names) == 1 for names in owners.values())
    assert owners[("lh_vv_silver.dbo", "slv_poi_entity_non_enrich")] == {enr}
    assert owners[("lh_vv_silver.dbo", "slv_poi_amenity")] == {enr}
    assert sum(trg == "gld_enr_poi_coordinate" for _pl, _ss, _src, _ts, trg, *_rest in rows) == 0
    specs, _namespace = _specs()
    assert not any(spec["fq"] == "lh_vv_gold.enr.gld_enr_poi_coordinate" for spec in specs)
    assert "_SLV1H" not in seed


def test_enr_15p_dag_order():
    namespace: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], namespace)  # noqa: S102
    enr = "PL_VV_TRANS_SLV_TO_ENR_15M"
    active = {
        (src, trg)
        for pl, _ss, src, _ts, trg, active_flag, *_rest in namespace["PIPELINE_CONFIG_ROWS"]
        if pl == enr and active_flag == 1
    }
    assert ("slv_poi_entity_non_enrich", "slv_poi_amenity") in active
    assert ("slv_poi_entity_non_enrich", "gld_enr_poi_info") in active
    assert ("slv_poi_amenity", "gld_enr_poi_info") in active


OLD_SUFFIX_RE = re.compile(r"(?<![A-Za-z0-9])PL_\w*?_(?:15|30)P\b|(?<![A-Za-z0-9_])ENR_(?:15|30)P\b|`_(?:15|30)P`")


def _renames() -> list:
    return _assign(_cell(_notebook("NB_CREATE_DDL.ipynb"), "plcadpy"), "RENAMES")


def _cadence():
    lib = _by_id(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"))["9ff87eee"]
    pattern = re.search(r'CADENCE_RE = re\.compile\(r"([^"]+)"\)', lib).group(1)
    assert pattern == r"_(\d+)([MHD])$"
    regex, unit = re.compile(pattern), {"M": 1, "H": 60, "D": 1440}

    def minutes(pl):
        m = regex.search(pl)
        return int(m.group(1)) * unit[m.group(2)] if m else None
    return minutes


def test_pl_cadence_seed():
    minutes = _cadence()
    ns: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], ns)  # noqa: S102
    rows = [r for r in ns["PIPELINE_CONFIG_ROWS"] if r[7] in ("RECOMPUTE", "APPEND")]
    assert {r[0] for r in rows} == {new for _o, new, _l in _renames()} | {"PL_VV_TRANS_SLV_TO_GLD_1H"}
    assert all(minutes(r[0]) for r in rows)
    owner = {(r[3], r[4]): r[0] for r in rows if r[5] == 1}
    for pl, src_schema, src, _ts, _trg, active, *_rest in rows:
        other = owner.get((src_schema, src))
        if active == 1 and other and other != pl:
            assert minutes(other) <= minutes(pl), (pl, src, other)


def test_pl_cadence_patch_cell():
    ddl = _notebook("NB_CREATE_DDL.ipynb")
    assert [c.get("id") for c in ddl["cells"]][-4:-2] == ["plcadmd", "plcadpy"]
    assert _cell(ddl, "plcadmd").startswith("# [THÊM 26/10] 20261026-pl-name-cadence-suffix")
    patch, renames, minutes = _cell(ddl, "plcadpy"), _renames(), _cadence()
    seed: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], seed)  # noqa: S102
    assert [new for _o, new, _l in renames] == [seed["_ENR"], seed["_GLD30"]]
    for old, new, _lease in renames:
        assert old.endswith("P") and new == old[:-1] + "M" and minutes(old) is None and minutes(new)
    assert renames[1][0] == _assign(_cell(ddl, "srvpoipy"), "PL")
    assert renames[1][2] == _assign(_cell(ddl, "srvpoipy"), "LEASE_MINUTES")
    assert renames[0][0] in _cell(ddl, "enrddlpy")
    orch = "".join("".join(c["source"]) for c in _notebook("NB_00_ORCHES_SLV_TO_ENR.ipynb")["cells"])
    assert re.search(r'^p_pl_name = "([^"]+)"', orch, re.M).group(1) == renames[0][1]
    assert int(re.search(r'^p_lock_timeout_min = "(\d+)"', orch, re.M).group(1)) == renames[0][2]
    for banned in ("DROP ", "DELETE ", "TRUNCATE"):
        assert banned not in patch.upper()
    assert "UPDATE {CFG} SET pl_name = '{new}' WHERE pl_name = '{old}'" in patch
    assert "SET watermark_id = '{new_id}', src_tbl = '{new}'" in patch
    assert patch.index("Dừng trước khi ghi") < patch.index("_refresh_lock(old)") < patch.index("SET watermark_id = '{new_id}'")
    assert patch.index("_refresh_lock(new)") < patch.index("UPDATE {CFG} SET pl_name")
    assert "Sau khi ghi" in patch and "finally:" in patch and "lock_exec_id = '{LOCK}'" in patch


def test_no_old_cadence_suffix_in_active_surface():
    paths = [p for p in (ROOT / "notebooks").glob("*.ipynb") if p.name != "NB_CREATE_DDL.ipynb"]
    paths += list((ROOT / "pipelines").rglob("*.json")) + [ROOT / "AGENTS.md"]
    hits = [p.relative_to(ROOT).as_posix() for p in paths if OLD_SUFFIX_RE.search(p.read_text(encoding="utf-8"))]
    hits += [p.name for p in (ROOT / "pipelines").iterdir() if OLD_SUFFIX_RE.search(p.name)]
    naming = (ROOT / "docs" / "context" / "02_NAMING_CONVENTION.md").read_text(encoding="utf-8")
    if OLD_SUFFIX_RE.search(naming[naming.index("## 3. Pipeline"):naming.index("## 4.")]):
        hits.append("02_NAMING_CONVENTION.md §3")
    assert hits == []


def test_pl_cadence_dup_key_before_write():
    patch = _cell(_notebook("NB_CREATE_DDL.ipynb"), "plcadpy")
    marker = "GROUP BY pl_name, src_schema, src_tbl, trg_schema, trg_tbl"
    assert marker in patch and "HAVING count(*) > 1" in patch
    assert patch.index(marker) < patch.index("UPDATE {CFG} SET pl_name")
    assert patch.index(marker) < patch.index("_refresh_lock(old)")
    assert patch.index("issues, n_old = _issues(old, new)") < patch.index("đã đổi, không ghi")
    assert patch.count("issues, n_old = _issues(old, new)") == 1


def test_pl_cadence_rename_is_conditional():
    """A new lock id must not be renamed into, and a raced duplicate is reverted."""
    patch = _cell(_notebook("NB_CREATE_DDL.ipynb"), "plcadpy")
    rename_at = patch.index("SET watermark_id = '{new_id}', src_tbl = '{new}'")
    before = patch[patch.rindex("_refresh_lock(old)", 0, rename_at):rename_at]
    assert "SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{new_id}'" in before
    assert "(SELECT count(*)" not in patch
    revert_at = patch.index("SET watermark_id = '{old_id}', src_tbl = '{old}'")
    config_at = patch.index("UPDATE {CFG} SET pl_name")
    assert rename_at < revert_at < config_at
    assert "n_new_after != 1" in patch[rename_at:revert_at]
    assert "for target in (old_id, new_id)" in patch
    assert patch.index("có cả {old_id} và {new_id}") < rename_at

    def rename(rows: list[str], new_exists: bool) -> list[str]:
        if new_exists:
            return list(rows)
        return ["new" if row == "old" else row for row in rows]

    assert rename(["old"], new_exists=True) == ["old"]
    assert rename(["old"], new_exists=False).count("new") == 1
    assert rename(["new"], new_exists=True).count("new") == 1


def test_pl_cadence_rerun_checks_lock():
    patch = _cell(_notebook("NB_CREATE_DDL.ipynb"), "plcadpy")
    done = patch.index('đã đổi, không ghi')
    head = patch[:done]
    assert "watermark_id = '{new_id}' AND src_tbl = '{new}'" in head
    assert "không có đúng 1 cặp" in head
    assert "đang giữ khoá" in head
    assert "INTERVAL {lease} MINUTES" in head
    assert head.index("không có đúng 1 cặp") < done
    recover = head[head.rindex("UPDATE {WM}"):done]
    assert "lock_exec_id = NULL" in recover
    assert "lock_exec_id = '{owner_sql}'" in recover
    assert "for _attempt in range(3)" in head
    assert head.index("for _attempt in range(3)") < head.rindex("UPDATE {WM}") < head.rindex(".collect()")
    assert "vẫn hết hạn sau 3 lần" in head
    assert "DELETE " not in patch.upper()
    lock_update = patch.index("SET lock_exec_id = '{LOCK}'")
    assert patch.rindex("held = True", 0, lock_update) < lock_update
    assert "if failed is None:" in patch[patch.index("finally:"):]
