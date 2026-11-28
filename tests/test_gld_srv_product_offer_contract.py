"""Contract checks for gld_srv_product_offer. No Spark."""
import ast
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = "NB_GLD_SRV_PRODUCT_OFFER.ipynb"
BUILD = "gldprdbuild"
PATCH = "gldprdddlpy"
FQ = "lh_vv_gold.dbo.gld_srv_product_offer"
BUSINESS = [
    "product_id", "name", "lang", "product_type", "is_active", "is_bookable", "product_line",
    "price_level", "original_price", "marketing_price", "markup_percent", "variant_count",
    "active_variant_count", "variants_json", "variant_tickets", "variant_dates", "variant_hotels",
    "variant_age_groups", "variant_room_types", "variant_departures", "variant_statuses",
    "product_attributes", "business_service_id", "source_id", "product_post_id", "poi_id",
    "destination_id",
]
DDL_TYPE = {
    "string": "STRING", "boolean": "BOOLEAN", "int": "INT", "double": "DOUBLE", "bigint": "BIGINT",
}
TECH = [("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP")]


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell(name: str, cell_id: str) -> str:
    return "".join(next(cell["source"] for cell in _notebook(name)["cells"] if cell.get("id") == cell_id))


def _func(source: str, name: str) -> str:
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(f"def {name}("))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("def ")), len(lines))
    return "\n".join(lines[start:end])


def _assign(source: str, name: str):
    tree = ast.parse(source)
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _build() -> str:
    return _cell(NB, BUILD)


def _code_without_comments(source: str) -> str:
    lines = []
    for line in source.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        lines.append(line)
    return "\n".join(lines)


def test_product_offer_time_parser_legacy():
    source = _build()
    assert 'spark.conf.set("spark.sql.legacy.timeParserPolicy", "LEGACY")' in source
    assert source.index("timeParserPolicy") < source.index("def _read(")
    source = _build()
    spec = _func(source, "_spec")
    namespace = {"INPUTS": _assign(source, "INPUTS")}
    exec(spec, namespace)  # noqa: S102
    got = namespace["_spec"]()
    assert got["trg_tbl"] == "gld_srv_product_offer"
    assert got["inputs"] == namespace["INPUTS"]
    assert len(got["inputs"]) == 15
    assert got["pk"] == ("product_id",)
    assert got["required_inputs"] == ("sale", "room_offer")
    assert got["hash_exclude"] == ("is_active",)
    assert got["soft_delete_set"] == {"is_active": "false"}
    assert got.get("deleted_flag") is None
    assert got["write_mode"] == "MERGE"
    body = source[source.index("SPEC = NodeSpec("):]
    for name in ("trg_tbl", "inputs", "pk", "required_inputs", "hash_exclude", "soft_delete_set", "write_mode"):
        assert name in body


def test_product_offer_inputs_silver_only():
    source = _build()
    inputs = _assign(source, "INPUTS")
    assert all(value.startswith("slv_") for value in inputs.values())
    assert "lh_vv_gold" not in source
    assert "ai_poi" not in source


def test_product_offer_out_types_match_mapping():
    source = _build()
    assert list(_assign(source, "OUT_TYPES")) == BUSINESS
    for name in ("row_hash", "created_at", "updated_at", "deleted_at"):
        assert name not in _assign(source, "OUT_TYPES")


def test_product_offer_ddl_matches_out_types():
    out_types = _assign(_build(), "OUT_TYPES")
    table_cols = _assign(_cell("NB_CREATE_DDL.ipynb", PATCH), "TABLE_COLS")[FQ]
    expected = [
        ("product_id", "STRING NOT NULL"),
        *[(name, DDL_TYPE[out_types[name]]) for name in BUSINESS if name != "product_id"],
        *TECH,
    ]
    assert table_cols == expected
    assert len(table_cols) == 31


def test_product_offer_poi_id_literal():
    source = _build()
    assert _assign(source, "PARTNER") == "partner"
    assert 'uuid_md5(F.col("business_service_id"), F.lit(PARTNER))' in source


def test_product_offer_prices_passthrough():
    source = _build()
    assert "decode_price" not in source
    assert "b64decode" not in source
    assert "DECODE[" not in source
    assert _assign(source, "PRICE_TIERS") == ((500000, 1), (2000000, 2), (5000000, 3))
    outside = source.replace(_func(source, "_price_level"), "")
    for name in ("original_price", "markup_percent", "marketing_price"):
        assert not re.search(rf"coalesce\([^)\n]*{name}", outside)
        assert not re.search(rf"cast\([^)\n]*{name}", outside)


def test_product_offer_deterministic_no_sale_flag():
    source = _build()
    for token in ("current_timestamp", "current_date", "rand(", "F.first", "now("):
        assert token not in source
    for name in ("valid_from", "valid_to"):
        assert not re.search(rf"{name}\s*(=|<|>|!)", source)


def test_product_offer_json_options():
    source = _build()
    assert _assign(source, "JSON_OPTS")["ignoreNullFields"] == "false"
    hotel = _assign(source, "HOTEL_JSON_OPTS")
    assert hotel["timeZone"] == "UTC"
    assert hotel["timestampFormat"] == "yyyy-MM-dd'T'HH:mm:ss'Z'"
    assert "variant_id" in _assign(source, "BY_ID")
    assert "array_sort(" in source
    assert "BY_ID" in source[source.index("array_sort("):]


def test_product_offer_union_product_id_unique():
    source = _func(_build(), "build")
    union_at = source.index("unionByName")
    unique_at = source.index('_require_unique(rows, ("product_id",), "union product_id")')
    destination_at = source.index('ctx.input("destination"')
    assert union_at < unique_at < destination_at


def test_product_offer_bsid_rule_static():
    source = _build()
    assert 'F.col("deleted") == F.lit(False)' in source
    assert "countDistinct" in source
    assert "_rel_rows" in source and "isNull()" in source
    assert "_rel_n > 1" in source or '_rel_n") > 1' in source


def test_product_offer_axes():
    assert _assign(_build(), "AXES") == {
        "holiday:swticket": "variant_tickets",
        "holiday:use_date": "variant_dates",
        "holiday:hotel": "variant_hotels",
        "holiday:quantity": "variant_age_groups",
        "holiday:age_group": "variant_age_groups",
        "holiday:zone": "variant_room_types",
        "holiday:depature": "variant_departures",
    }


def test_product_offer_edges_create_vs_init():
    from test_initial_ddl_contract import _by_id, _initial

    edges = _assign(_cell("NB_CREATE_DDL.ipynb", PATCH), "EDGES_ON")
    namespace: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], namespace)  # noqa: S102
    rows = [row for row in namespace["PIPELINE_CONFIG_ROWS"] if row[4] == "gld_srv_product_offer"]
    assert len(edges) == 15
    assert len(rows) == 15
    assert [edge[1] for edge in edges] == [row[2] for row in rows]
    assert all(row[0] == "PL_VV_TRANS_SLV_TO_GLD_30M" for row in rows)
    assert all(row[10] == "NB_GLD_SRV_PRODUCT_OFFER" for row in rows)
    assert all(edge[5] == "NB_GLD_SRV_PRODUCT_OFFER" for edge in edges)


def test_product_offer_patch_guards():
    source = _code_without_comments(_cell("NB_CREATE_DDL.ipynb", PATCH))
    markers = [
        "Dừng trước khi ghi",
        "_refresh_lock()",
        "CREATE TABLE IF NOT EXISTS",
        "WHEN NOT MATCHED THEN INSERT",
        "Sau khi ghi",
    ]
    positions = [source.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert "COALESCE((SELECT MAX(id) FROM {CFG}), 0) + s.seq" in source
    acquire = source.index("status = 'RUNNING'")
    owner = source.index("owner = spark.sql", acquire)
    assert source.index("held = True", acquire) < owner
    assert "held = False" in source[owner:source.index("Dừng trước khi ghi")]
    assert "finally:" in source
    for word in ("DROP", "DELETE", "TRUNCATE", "ALTER"):
        assert re.search(rf"\b{word}\b", source) is None
    for name in (
        "slv_pn_product_sale", "slv_pn_hotel_room_offer", "slv_pn_hotel_rate_offer", "slv_enr_poi_destination",
    ):
        assert name in source
