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
