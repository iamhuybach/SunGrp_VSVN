"""Contract of POI media, gallery, and serving amenity. No Spark."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TECH = ("row_hash", "created_at", "updated_at", "deleted_at")
INT_COLS = {"display_order", "width_px", "height_px"}
BOOL_COLS = {"is_cover", "is_active"}
AMENITY_COLS = [
    ("poi_id", "STRING NOT NULL", None),
    ("business_sector", "STRING NOT NULL", None),
    ("amenity_group", "STRING NOT NULL", None),
    ("amenity_raw", "STRING NOT NULL", None),
    ("amenity", "STRING", None),
    ("amenity_vi", "STRING", None),
    ("service_flags", "STRING", None),
    ("row_hash", "STRING", None),
    ("created_at", "TIMESTAMP", None),
    ("updated_at", "TIMESTAMP", None),
    ("deleted_at", "TIMESTAMP", None),
]


def _nb(name):
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell(name, cid):
    found = [cell for cell in _nb(name)["cells"] if cell.get("id") == cid]
    assert len(found) == 1
    return "".join(found[0]["source"])


def _assign(source, name):
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _exec_names(source, names):
    tree = ast.parse(source)
    env: dict = {}
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in names for t in node.targets):
            exec(ast.unparse(node), env)  # noqa: S102
    return env


def _spec(source):
    tree = ast.parse(source)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SPEC" for t in node.targets):
            return {kw.arg: ast.literal_eval(kw.value) for kw in node.value.keywords if kw.arg != "build"}
    raise AssertionError("SPEC")


def _build(source):
    tree = ast.parse(source)
    return next(ast.unparse(node) for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "build")


def test_node_specs():
    silver = _spec(_cell("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediabuild"))
    gallery = _spec(_cell("NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb", "srvgallerybuild"))
    amenity = _spec(_cell("NB_GLD_SRV_POI_AMENITY.ipynb", "srvamenitybuild"))
    assert silver["trg_tbl"] == "slv_poi_media_info"
    assert silver["inputs"] == {
        "media_3p": "slv_3p_poi_media",
        "i18n": "slv_pn_business_service_i18ns",
        "services": "slv_pn_business_services",
    }
    assert silver["pk"] == ("media_id",)
    assert silver["required_inputs"] == ("media_3p", "i18n")
    assert silver["unique_checks"] == (("one_cover_per_poi", ("poi_id",), "is_cover"),)
    assert silver["block_checks"] == (
        ("media_required_null", "poi_id IS NULL OR source_name IS NULL OR is_cover IS NULL OR is_active IS NULL"),
    )
    assert silver["soft_delete_set"] == {"is_active": "false"}
    assert silver["write_mode"] == "MERGE"
    assert gallery["trg_tbl"] == "gld_srv_poi_media_gallery"
    assert gallery["inputs"] == {"media": "slv_poi_media_info"}
    assert gallery["pk"] == ("media_id",)
    assert gallery["required_inputs"] == ("media",)
    assert "unique_checks" not in gallery and "block_checks" not in gallery
    assert gallery["soft_delete_set"] == {"is_active": "false"}
    assert gallery["write_mode"] == "MERGE"
    assert amenity["trg_tbl"] == "gld_srv_poi_amenity"
    assert amenity["inputs"] == {"amenity": "slv_poi_amenity"}
    assert amenity["pk"] == ("poi_id", "business_sector", "amenity_group", "amenity_raw")
    assert amenity["required_inputs"] == ("amenity",)
    assert "unique_checks" not in amenity and "block_checks" not in amenity and "soft_delete_set" not in amenity
    assert amenity["write_mode"] == "MERGE"


def test_build_columns_match_ddl():
    init = {}
    exec(_cell("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), init)  # noqa: S102
    specs = {item["fq"]: item for item in init["TABLE_SPECS"]}
    media = _exec_names(_cell("NB_CREATE_DDL.ipynb", "mediaddlpy"), {"MEDIA_COLS", "TABLE_COLS"})
    amenity = _exec_names(_cell("NB_CREATE_DDL.ipynb", "amenddlpy"), {"AMENITY_COLS", "TABLE_COLS"})
    silver_cols = _assign(_cell("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediabuild"), "OUT_COLS")
    gallery_cols = _assign(_cell("NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb", "srvgallerybuild"), "OUT_COLS")
    amenity_cols = _assign(_cell("NB_GLD_SRV_POI_AMENITY.ipynb", "srvamenitybuild"), "OUT_COLS")
    pairs = (
        ("lh_vv_silver.dbo.slv_poi_media_info", silver_cols, media),
        ("lh_vv_gold.dbo.gld_srv_poi_media_gallery", gallery_cols, media),
        ("lh_vv_gold.dbo.gld_srv_poi_amenity", amenity_cols, amenity),
    )
    for fq, out_cols, env in pairs:
        ddl = env["TABLE_COLS"][fq]
        spec_cols = specs[fq]["cols"]
        assert [name for name, _dtype in ddl] == list(out_cols) + list(TECH)
        assert spec_cols == [(name, dtype, None) for name, dtype in ddl]
        for name, dtype in ddl:
            if name in INT_COLS:
                assert dtype == "INT"
            if name in BOOL_COLS:
                assert dtype == "BOOLEAN"


def test_ddl_parity_create_vs_init():
    init = {}
    exec(_cell("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), init)  # noqa: S102
    specs = {item["fq"]: item for item in init["TABLE_SPECS"]}
    for cid, names in (
        ("mediaddlpy", {"PROPS", "MEDIA_COLS", "TABLE_COLS"}),
        ("amenddlpy", {"PROPS", "AMENITY_COLS", "TABLE_COLS"}),
    ):
        source = _cell("NB_CREATE_DDL.ipynb", cid)
        tree = ast.parse(source)
        env = _exec_names(source, names)
        fn = next(node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef) and node.name == "_create_sql")
        exec(ast.unparse(fn), env)  # noqa: S102
        for fq, cols in env["TABLE_COLS"].items():
            assert env["_create_sql"](fq, cols) == init["create_sql"](specs[fq])


def test_edges_create_vs_init():
    seed = {}
    exec(_cell("NB_SETUP_INITIAL_DDL.ipynb", "init_seed_ctrl"), seed)  # noqa: S102
    rows = seed["PIPELINE_CONFIG_ROWS"]
    seen = []
    renames = {old: new for old, new, _lease in _assign(_cell("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")}
    for cid, pl in (("mediaddlpy", "PL_VV_TRANS_SLV_TO_GLD_30M"), ("amenddlpy", "PL_VV_TRANS_SLV_TO_GLD_1H")):
        source = _cell("NB_CREATE_DDL.ipynb", cid)
        hist = _assign(source, "PL")
        assert renames.get(hist, hist) == pl
        for seq, src, schema, target, mode, notebook, priority in _assign(source, "EDGES_ON"):
            match = (pl, "lh_vv_silver.dbo", src, schema, target, 1, priority, mode, None, None, notebook)
            assert match in rows
            assert seq > 0
            seen.append((pl, "lh_vv_silver.dbo", src, schema, target))
    targets = {item[4] for item in seen}
    by_target = {}
    for pl, _ss, _src, _ts, trg, *_rest in rows:
        if trg in targets:
            by_target.setdefault(trg, set()).add(pl)
    assert by_target == {
        "slv_poi_media_info": {"PL_VV_TRANS_SLV_TO_GLD_30M"},
        "gld_srv_poi_media_gallery": {"PL_VV_TRANS_SLV_TO_GLD_30M"},
        "gld_srv_poi_amenity": {"PL_VV_TRANS_SLV_TO_GLD_1H"},
    }
    assert len(seen) == len(set(seen)) == 5


def test_amenity_untouched():
    init = {}
    exec(_cell("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), init)  # noqa: S102
    spec = next(item for item in init["TABLE_SPECS"] if item["fq"] == "lh_vv_silver.dbo.slv_poi_amenity")
    assert spec["cols"] == AMENITY_COLS
    seed = {}
    exec(_cell("NB_SETUP_INITIAL_DDL.ipynb", "init_seed_ctrl"), seed)  # noqa: S102
    enr = [
        row for row in seed["PIPELINE_CONFIG_ROWS"]
        if row[4] == "slv_poi_amenity"
    ]
    assert enr == [
        ("PL_VV_TRANS_SLV_TO_ENR_15M", "lh_vv_silver.dbo", "slv_3p_poi_amenity", "lh_vv_silver.dbo", "slv_poi_amenity",
         1, 1, "RECOMPUTE", None, None, None),
        ("PL_VV_TRANS_SLV_TO_ENR_15M", "lh_vv_silver.dbo", "slv_poi_entity_non_enrich", "lh_vv_silver.dbo", "slv_poi_amenity",
         1, 1, "RECOMPUTE", None, None, None),
        ("PL_VV_TRANS_SLV_TO_ENR_15M", "lh_vv_silver.dbo", "ref_dictionary_amenities", "lh_vv_silver.dbo", "slv_poi_amenity",
         1, 1, "RECOMPUTE", None, None, None),
    ]
    for cid in ("mediaddlpy", "amenddlpy"):
        edges = _assign(_cell("NB_CREATE_DDL.ipynb", cid), "EDGES_ON")
        assert all(trg != "slv_poi_amenity" for _seq, _src, _schema, trg, _mode, _nb, _priority in edges)
    for name, cid in (
        ("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediabuild"),
        ("NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb", "srvgallerybuild"),
        ("NB_GLD_SRV_POI_AMENITY.ipynb", "srvamenitybuild"),
    ):
        assert _spec(_cell(name, cid))["trg_tbl"] != "slv_poi_amenity"


def test_gold_copy_one_to_one():
    silver = _assign(_cell("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediabuild"), "OUT_COLS")
    gallery = _assign(_cell("NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb", "srvgallerybuild"), "OUT_COLS")
    assert gallery == silver
    amenity = _assign(_cell("NB_GLD_SRV_POI_AMENITY.ipynb", "srvamenitybuild"), "OUT_COLS")
    amenity_nb = "\n".join("".join(cell["source"]) for cell in _nb("NB_SLV_POI_AMENITY.ipynb")["cells"])
    match = re.search(r"OUT_COLS = \((.*?)\)", amenity_nb, re.S)
    assert match
    assert amenity == ast.literal_eval("(" + match.group(1) + ")")
    for name, cid in (
        ("NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb", "srvgallerybuild"),
        ("NB_GLD_SRV_POI_AMENITY.ipynb", "srvamenitybuild"),
    ):
        body = _build(_cell(name, cid))
        for token in ("join", "where", "withColumn", *TECH):
            assert token not in body


def test_flow_lock_before_writes():
    lib = "\n".join("".join(cell["source"]) for cell in _nb("NB_LIB_TRANSFORM_SLV_GLD.ipynb")["cells"])
    assert "def refresh_flow_lock(" in lib
    run = lib.split("def run_node(", 1)[1].split("\ndef finish_node(", 1)[0]
    first = run.index("refresh_flow_lock(pl, exec_id)")
    ensure = run.index("ensure_target(")
    second = run.index("refresh_flow_lock(pl, exec_id)", first + 1)
    merge = run.index("merge_target(")
    assert first < ensure < second < merge
    orch = lib.split("def orchestrate(", 1)[1]
    assert orch.index("refresh_flow_lock(pl, exec_id)") < orch.index("advance_edges(")


def test_media_build_static():
    source = _cell("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediabuild")
    for token in (
        "posexplode", "asc_nulls_last", 'startswith("[")', 'isin("", "null")', 'concat_ws("|",', "sha2(",
        '"google"', '"partner"',
    ):
        assert token in source
    assert "256" in source
    assert "monotonically_increasing_id" not in source
    assert "F.first(" not in source
    assert ".count()" not in source
    assert source.count(".persist()") == 1 and source.count(".unpersist()") == 1
    metrics = source.split("cached = docs.persist()", 1)[1].split("return kept.select", 1)[0]
    assert metrics.index("try:") < metrics.index("finally:") < metrics.index("cached.unpersist()")
    assert source.count(".first()") == 2
    blob = next(line for line in source.splitlines() if "blob_url" in line)
    assert "trim" not in blob
    assert 'url.alias("blob_url")' in source


def test_setup_patch_guards():
    order = ["held = True", "Dừng trước khi ghi", "CREATE TABLE IF NOT EXISTS", "INSERT INTO {CFG}", "Sau khi ghi", "finally:"]
    for cid in ("mediaddlpy", "amenddlpy"):
        patch = _cell("NB_CREATE_DDL.ipynb", cid)
        positions = [patch.index(token) for token in order]
        assert positions == sorted(positions)
        assert "LEASE_MINUTES = 90" in patch
        code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
        for token in ("DROP", "DELETE", "TRUNCATE", "UPDATE {CFG}", "ALTER TABLE"):
            assert token not in code


def test_mapping_targets_match_out_cols():
    text = (ROOT / "docs" / "context" / "mapping_poi_media_info.md").read_text(encoding="utf-8")
    section = text.split("## 1.2. Field Mapping", 1)[1].split("# 2.", 1)[0]
    targets = []
    for line in section.splitlines():
        if not line.startswith("|") or line.startswith("| source") or line.startswith("|---"):
            continue
        target = line.strip().strip("|").split("|")[-1].strip()
        if target and target != "target field":
            targets.append(target)
    out_cols = _assign(_cell("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediabuild"), "OUT_COLS")
    assert tuple(name for name in targets if name not in {"created_at", "updated_at"}) == out_cols
