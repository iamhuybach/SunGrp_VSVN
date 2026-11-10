"""Serving contract: gold DDL + NodeSpec pk == PostgreSQL DDL == JPA entities. No Spark, no JDK, no Docker."""
import ast
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "services" / "data-serving-service"
ENTITY_DIR = SERVICE / "src" / "main" / "java" / "vn" / "visitvietnam" / "dataserving" / "domain" / "entity"
PG_DDL = ROOT / "sql" / "postgres" / "gld_srv_serve.pg.sql"
GOLD_PREFIX = "lh_vv_gold.dbo.gld_"
BUILD_CELLS = {
    "srv_poi_info": ("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"),
    "srv_poi_multi_lang": ("NB_GLD_SRV_POI_MULTI_LANG.ipynb", "srvmlbuild"),
    "srv_poi_amenity": ("NB_GLD_SRV_POI_AMENITY.ipynb", "srvamenitybuild"),
    "srv_poi_media_gallery": ("NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb", "srvgallerybuild"),
    "srv_poi_review": ("NB_GLD_SRV_POI_REVIEW.ipynb", "srvrvbuild"),
}
# Ánh xạ kiểu Fabric -> PostgreSQL theo đầu file gld_srv_serve.pg.sql (decision D-TYPE, D-BIGINT).
GOLD_TO_PG = {
    "STRING": "text", "BOOLEAN": "boolean", "INT": "integer", "BIGINT": "int8",
    "DOUBLE": "double precision", "TIMESTAMP": "timestamp without time zone",
}
GOLD_TO_JAVA = {
    "STRING": "String", "BOOLEAN": "Boolean", "INT": "Integer", "BIGINT": "Long",
    "DOUBLE": "Double", "TIMESTAMP": "LocalDateTime",
}


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell_source(name: str, cell_id: str) -> str:
    found = [cell for cell in _notebook(name)["cells"] if cell.get("id") == cell_id]
    assert len(found) == 1, f"{name}: cell {cell_id}"
    return "".join(found[0]["source"])


def _normalize_gold_type(value: str) -> str:
    base = value.upper().replace(" NOT NULL", "").strip()
    return base


def gold_tables() -> dict[str, dict]:
    namespace: dict = {}
    exec(_cell_source("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), namespace)  # noqa: S102 - pure table spec cell
    tables: dict[str, dict] = {}
    for spec in namespace["TABLE_SPECS"]:
        fq = spec["fq"]
        if not fq.startswith(GOLD_PREFIX + "srv_poi_"):
            continue
        name = fq[len(GOLD_PREFIX):]
        cols = {col[0]: _normalize_gold_type(col[1]) for col in spec["cols"]}
        notebook, cell_id = BUILD_CELLS[name]
        tree = ast.parse(_cell_source(notebook, cell_id))
        spec_call = next(
            node.value for node in ast.walk(tree)
            if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SPEC" for t in node.targets)
        )
        kwargs = {kw.arg: ast.literal_eval(kw.value) for kw in spec_call.keywords if kw.arg != "build"}
        tables[name] = {"cols": cols, "pk": tuple(kwargs["pk"])}
    assert set(tables) == set(BUILD_CELLS)
    return tables


def pg_tables() -> dict[str, dict]:
    text = PG_DDL.read_text(encoding="utf-8")
    tables: dict[str, dict] = {}
    for match in re.finditer(r"CREATE TABLE apps\.(\w+) \((.*?)\n\);", text, re.S):
        name, body = match.group(1), match.group(2)
        cols: dict[str, str] = {}
        pk: tuple[str, ...] = ()
        for raw in body.split("\n"):
            line = raw.strip().rstrip(",")
            if not line:
                continue
            if line.upper().startswith("PRIMARY KEY"):
                pk = tuple(item.strip() for item in line[line.index("(") + 1:line.rindex(")")].split(","))
                continue
            col, rest = line.split(" ", 1)
            cols[col] = rest.replace(" NOT NULL", "").strip()
        tables[name] = {"cols": cols, "pk": pk}
    return tables


def entity_tables() -> dict[str, dict]:
    tables: dict[str, dict] = {}
    for path in sorted(ENTITY_DIR.glob("Srv*.java")):
        text = path.read_text(encoding="utf-8")
        table = re.search(r'@Table\(name = "(\w+)", schema = "apps"\)', text)
        assert table, f"{path.name}: @Table(name=..., schema=\"apps\") required"
        cols: dict[str, str] = {}
        pk: list[str] = []
        pending_id = False
        for line in text.splitlines():
            stripped = line.strip()
            if stripped == "@Id":
                pending_id = True
                continue
            column = re.match(r'@Column\(name = "(\w+)"', stripped)
            if column:
                current = column.group(1)
                cols[current] = ""
                if pending_id:
                    pk.append(current)
                    pending_id = False
                continue
            field = re.match(r"private (\w+) (\w+);", stripped)
            if field and cols and not cols[current]:
                cols[current] = field.group(1)
        tables[table.group(1)] = {"cols": cols, "pk": tuple(pk), "id_class": "@IdClass(" in text}
    return tables


def _require_service() -> None:
    if not SERVICE.is_dir():
        pytest.skip("services/data-serving-service not imported yet (CT-3)")


def test_gold_and_pg_columns_and_types_match():
    gold, pg = gold_tables(), pg_tables()
    assert set(gold) == set(pg)
    for name, spec in gold.items():
        assert set(spec["cols"]) == set(pg[name]["cols"]), name
        for col, gold_type in spec["cols"].items():
            expected = GOLD_TO_PG.get(gold_type)
            if expected is None:
                decimal = re.fullmatch(r"DECIMAL\((\d+),(\d+)\)", gold_type)
                assert decimal, f"{name}.{col}: unmapped gold type {gold_type}"
                expected = f"numeric({decimal.group(1)}, {decimal.group(2)})"
            assert pg[name]["cols"][col] == expected, f"{name}.{col}: {pg[name]['cols'][col]} != {expected}"
        assert pg[name]["pk"] == spec["pk"], f"{name}: pk {pg[name]['pk']} != NodeSpec {spec['pk']}"


def test_entities_match_gold_columns_types_and_keys():
    _require_service()
    gold, entities = gold_tables(), entity_tables()
    assert set(gold) == set(entities)
    for name, spec in gold.items():
        entity = entities[name]
        assert set(entity["cols"]) == set(spec["cols"]), f"{name}: entity columns differ from gold"
        for col, gold_type in spec["cols"].items():
            expected = GOLD_TO_JAVA.get(gold_type, "BigDecimal" if gold_type.startswith("DECIMAL(") else None)
            assert entity["cols"][col] == expected, f"{name}.{col}: {entity['cols'][col]} != {expected}"
        assert set(entity["pk"]) == set(spec["pk"]), f"{name}: @Id columns {entity['pk']} != {spec['pk']}"
        assert entity["id_class"] == (len(spec["pk"]) > 1), f"{name}: @IdClass must match composite pk"


def test_amenity_en_order_across_layers():
    namespace: dict = {}
    exec(_cell_source("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), namespace)  # noqa: S102
    for fq in ("lh_vv_silver.dbo.slv_poi_amenity", "lh_vv_gold.dbo.gld_srv_poi_amenity"):
        spec = next(item for item in namespace["TABLE_SPECS"] if item["fq"] == fq)
        names = [col[0] for col in spec["cols"]]
        assert names[names.index("amenity") + 1] == "amenity_en"
    amenity_cols = _cell_source("NB_CREATE_DDL.ipynb", "amenddlpy").split("AMENITY_COLS = [", 1)[1].split("]", 1)[0]
    assert amenity_cols.index("'amenity_en'") > amenity_cols.index("'amenity'")
    pg = pg_tables()["srv_poi_amenity"]["cols"]
    pg_names = list(pg)
    assert pg_names[pg_names.index("amenity") + 1] == "amenity_en"
    entity = (ENTITY_DIR / "SrvPoiAmenity.java").read_text(encoding="utf-8")
    amenity_at = entity.index('@Column(name = "amenity")')
    amenity_en_at = entity.index('@Column(name = "amenity_en")')
    amenity_vi_at = entity.index('@Column(name = "amenity_vi")')
    assert amenity_at < amenity_en_at < amenity_vi_at


def test_review_entity_has_no_source_or_lang():
    _require_service()
    text = (ENTITY_DIR / "SrvPoiReview.java").read_text(encoding="utf-8")
    assert "source_name" not in text and '"lang"' not in text and '"source"' not in text


def test_no_flyway_in_service():
    _require_service()
    assert not list(SERVICE.rglob("db/migration"))
    assert "flyway" not in (SERVICE / "pom.xml").read_text(encoding="utf-8").lower()
    for yml in SERVICE.rglob("application*.yml"):
        assert "flyway" not in yml.read_text(encoding="utf-8").lower(), yml


COVER = [("cover_id", "STRING"), ("cover_blob_url", "STRING")]
TECH = ("row_hash", "created_at", "updated_at", "deleted_at")
INFO_SOURCES = ("slv_poi_entity_non_enrich", "slv_enr_poi_destination", "slv_enr_poi_info_multi_lang",
                "slv_3p_poi_rating", "slv_3p_poi_review")
COVER_EDGE = (1, "slv_poi_media_info", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1)


def _literal(source: str, name: str):
    node = next(n for n in ast.parse(source).body
                if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == name for t in n.targets))
    return ast.literal_eval(node.value)


def _code(source: str) -> str:
    return "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))


def _info_spec() -> dict:
    tree = ast.parse(_cell_source("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"))
    call = next(n.value for n in ast.walk(tree)
                if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "SPEC" for t in n.targets))
    return {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords if kw.arg != "build"}


def test_info_cover_patch_cell():
    ids = [cell.get("id") for cell in _notebook("NB_CREATE_DDL.ipynb")["cells"]]
    assert ids[-2:] == ["srvcovermd", "srvcoverpy"]
    patch = _cell_source("NB_CREATE_DDL.ipynb", "srvcoverpy")
    base = _literal(_cell_source("NB_CREATE_DDL.ipynb", "srvratepy"), "INFO_COLS")
    at = [name for name, _dtype in base].index("review_count") + 1
    assert _literal(patch, "INFO_NEW_COLS") == COVER
    assert _literal(patch, "INFO_COLS") == base[:at] + COVER + base[at:]
    assert _literal(patch, "EDGES_ON") == [COVER_EDGE]
    assert _literal(patch, "EDGES_KEEP") == INFO_SOURCES
    assert _literal(patch, "PL") == _literal(_cell_source("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")[1][1]
    order = ["held = True", "Dừng trước khi ghi", "ALTER TABLE", "INSERT INTO {CFG}", "Sau khi ghi", "finally:"]
    assert [patch.index(t) for t in order] == sorted(patch.index(t) for t in order)
    code = _code(patch)
    for token in ("DROP", "DELETE", "TRUNCATE", "UPDATE {CFG}", "REPLACE", "RESTORE", "columnMapping", "_30P"):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and " AFTER " in code
    calls = [m.start() for m in re.finditer(r"(?m)^\s*_refresh_lock\(\)", patch)]
    alter, insert = patch.index("ALTER TABLE"), patch.index("INSERT INTO {CFG}")
    assert len(calls) == 2 and calls[0] < alter < calls[1] < insert
    assert "LEASE_MINUTES = 90" in patch and "lock_exec_id = '{LOCK}'" in patch
    assert "raise failed from cleanup_exc" in patch


def test_info_cover_build_rule():
    source = _cell_source("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    code = _code(source)
    assert _literal(source, "OUT_COLS")[-3:] == ("review_count", "cover_id", "cover_blob_url")
    assert _literal(source, "COVER_COLS") == ("poi_id", "media_id", "blob_url", "is_cover")
    assert 'md = ctx.input("media")' in code
    assert '.where(F.col("is_cover"))' in code
    assert 'F.col("media_id").alias("cover_id")' in code
    assert 'F.col("blob_url").alias("cover_blob_url")' in code
    assert 'join(cover, "poi_id", "left")' in code
    assert "có hơn một cover" in code
    for token in ("with_cover", "row_number", "is_active", "lh_vv_gold", "deleted"):
        assert token not in code
    spec = _info_spec()
    assert spec["pk"] == ("poi_id",) and spec["write_mode"] == "MERGE"
    assert spec["required_inputs"] == ("entity",)
    assert spec["inputs"]["media"] == "slv_poi_media_info"
    assert tuple(v for k, v in spec["inputs"].items() if k != "media") == INFO_SOURCES


def test_info_cover_seed_and_init_ddl():
    seed: dict = {}
    exec(_cell_source("NB_SETUP_INITIAL_DDL.ipynb", "init_seed_ctrl"), seed)  # noqa: S102
    rows = [r for r in seed["PIPELINE_CONFIG_ROWS"] if r[4] == "gld_srv_poi_info"]
    assert seed["PIPELINE_CONFIG_ROWS"][-1] == (
        seed["_GLD30"], seed["_S"], "slv_poi_media_info", seed["_G"], "gld_srv_poi_info",
        1, 1, "RECOMPUTE", None, None, "NB_GLD_SRV_POI_INFO")
    assert sorted(r[2] for r in rows if r[5] == 1) == sorted(_info_spec()["inputs"].values())
    assert {r[0] for r in rows} == {"PL_VV_TRANS_SLV_TO_GLD_30M"}
    init: dict = {}
    exec(_cell_source("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), init)  # noqa: S102
    spec = next(s for s in init["TABLE_SPECS"] if s["fq"] == "lh_vv_gold.dbo.gld_srv_poi_info")
    patch = _cell_source("NB_CREATE_DDL.ipynb", "srvcoverpy")
    assert [(c[0], c[1]) for c in spec["cols"]] == _literal(patch, "INFO_COLS")
    out = _literal(_cell_source("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"), "OUT_COLS")
    assert list(out) + list(TECH) == [c[0] for c in spec["cols"]]


def test_info_cover_mapping_and_pg_ddl():
    text = (ROOT / "docs" / "context" / "mapping_gld_srv_poi_info.md").read_text(encoding="utf-8")
    table = text.split("### 1.2. Field Mapping", 1)[1].split("### 1.3", 1)[0]
    rows = {line.split("|")[4].strip(): line for line in table.splitlines() if line.startswith("|")}
    assert "slv_poi_media_info.media_id" in rows["cover_id"] and "is_cover" in rows["cover_id"]
    assert "slv_poi_media_info.blob_url" in rows["cover_blob_url"]
    handling = text.split("### 1.1. Xử lý", 1)[1].split("### 1.2", 1)[0]
    assert "`media` = `slv_poi_media_info`" in handling and "cover_matched" in handling
    pg = PG_DDL.read_text(encoding="utf-8")
    body = re.search(r"CREATE TABLE apps\.srv_poi_info \((.*?)\n\);", pg, re.S).group(1)
    assert "    review_count integer,\n    cover_id text,\n    cover_blob_url text,\n" in body
    assert not re.search(r"(?m)^\s*ALTER\s", pg)
