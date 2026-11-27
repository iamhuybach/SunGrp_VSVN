"""Contract checks for Silver L2 product sale and hotel offers. No Spark."""
import ast
import inspect
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIB = "NB_LIB_TRANSFORM_SLV_GLD.ipynb"
CELL = "926a3f9c"

GOLDEN_NO_OWNER = """
MERGE INTO lh.dbo.t AS t
USING v AS s
ON t.`poi_id` = s.`poi_id`
WHEN MATCHED AND (t.`row_hash` IS NULL OR t.`row_hash` <> s.`row_hash` OR t.`deleted_at` IS NOT NULL) THEN UPDATE SET
    t.`poi_name` = s.`poi_name`,
    t.`row_hash` = s.`row_hash`,
    t.`updated_at` = current_timestamp(),
    t.`deleted_at` = NULL
WHEN NOT MATCHED THEN INSERT (`poi_id`, `poi_name`, `row_hash`, `created_at`, `updated_at`, `deleted_at`)
VALUES (s.`poi_id`, s.`poi_name`, s.`row_hash`, current_timestamp(), current_timestamp(), CAST(NULL AS TIMESTAMP))
WHEN NOT MATCHED BY SOURCE AND t.`deleted_at` IS NULL THEN UPDATE SET
    t.`deleted_at` = current_timestamp(),
    t.`updated_at` = current_timestamp()
"""

GOLDEN_OWNER = """
MERGE INTO lh.dbo.t AS t
USING v AS s
ON t.`poi_id` = s.`poi_id`
WHEN MATCHED AND (t.`row_hash` IS NULL OR t.`row_hash` <> s.`row_hash` OR t.`deleted_at` IS NOT NULL OR t.`load_origin` IS NOT NULL) THEN UPDATE SET
    t.`row_hash` = s.`row_hash`,
    t.`updated_at` = current_timestamp(),
    t.`deleted_at` = NULL,
    t.`load_origin` = CAST(NULL AS STRING)
WHEN NOT MATCHED THEN INSERT (`poi_id`, `row_hash`, `created_at`, `updated_at`, `deleted_at`)
VALUES (s.`poi_id`, s.`row_hash`, current_timestamp(), current_timestamp(), CAST(NULL AS TIMESTAMP))
WHEN NOT MATCHED BY SOURCE AND t.`deleted_at` IS NULL AND t.`load_origin` IS NULL THEN UPDATE SET
    t.`deleted_at` = current_timestamp(),
    t.`updated_at` = current_timestamp()
"""

SALE_COLS = (
    "product_id", "product_post_id", "original_price", "marketing_price", "markup_percent", "is_bookable",
)
ROOM_COLS = (
    "room_type_id", "status", "available_rooms", "max_occupancy", "adult_capacity", "child_capacity",
    "view_type", "deleted", "is_bookable",
)
RATE_COLS = ("rate_plan_id", "status", "meal_plan", "valid_from", "valid_to")

NODE_SPEC = {
    "NB_SLV_PN_PRODUCT_SALE.ipynb": {
        "cell": "pnsalebuild",
        "trg_tbl": "slv_pn_product_sale",
        "inputs": {
            "products": "slv_pn_products",
            "posts": "slv_pn_product_posts",
            "variants": "slv_pn_product_variants",
        },
        "required_inputs": ("products", "posts", "variants"),
        "block_checks": (("is_bookable_null", "is_bookable IS NULL"),),
        "pk": ("product_id",),
        "out_cols": SALE_COLS,
    },
    "NB_SLV_PN_HOTEL_ROOM_OFFER.ipynb": {
        "cell": "pnroombuild",
        "trg_tbl": "slv_pn_hotel_room_offer",
        "inputs": {"room_types": "slv_pn_hotel_room_types"},
        "required_inputs": ("room_types",),
        "block_checks": (("is_bookable_null", "is_bookable IS NULL"),),
        "pk": ("room_type_id",),
        "out_cols": ROOM_COLS,
    },
    "NB_SLV_PN_HOTEL_RATE_OFFER.ipynb": {
        "cell": "pnratebuild",
        "trg_tbl": "slv_pn_hotel_rate_offer",
        "inputs": {"rate_plans": "slv_pn_hotel_rate_plans"},
        "required_inputs": ("rate_plans",),
        "block_checks": (),
        "pk": ("rate_plan_id",),
        "out_cols": RATE_COLS,
    },
}


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell(name: str, cell_id: str) -> str:
    return "".join(next(cell["source"] for cell in _notebook(name)["cells"] if cell.get("id") == cell_id))


def _func(source: str, name: str) -> str:
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(f"def {name}("))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("def ")), len(lines))
    return "\n".join(lines[start:end])


def _merge():
    source = _cell(LIB, CELL)
    namespace = {
        "quote_name": lambda fq: fq,
        "Optional": __import__("typing").Optional,
        "ConfigError": type("ConfigError", (Exception,), {}),
    }
    exec(_func(source, "_flag_name_ok"), namespace)  # noqa: S102
    exec(_func(source, "sql_merge_target"), namespace)  # noqa: S102
    return namespace["sql_merge_target"]


def _assign(source: str, name: str):
    tree = ast.parse(source)
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _pure(source: str, begin: str, end: str) -> str:
    start = source.index(begin)
    stop = source.index(end) + len(end)
    return source[start:stop]


def test_merge_default_sql_golden():
    merge = _merge()
    plain = merge("lh.dbo.t", "v", ["poi_id", "poi_name"], ("poi_id",), {})
    owner = merge("lh.dbo.t", "v", ["poi_id"], ("poi_id",), {}, "load_origin")
    assert plain == GOLDEN_NO_OWNER
    assert owner == GOLDEN_OWNER
    if "deleted_flag" in inspect.signature(merge).parameters:
        explicit = merge("lh.dbo.t", "v", ["poi_id", "poi_name"], ("poi_id",), {}, None, None)
        assert explicit == plain


def test_merge_flag_clause_order():
    merge = _merge()
    sql = merge("lh.dbo.t", "v", ["poi_id", "name"], ("poi_id",), {}, None, "_is_deleted")
    default = merge("lh.dbo.t", "v", ["poi_id", "name"], ("poi_id",), {})
    markers = (
        "WHEN MATCHED AND NOT s.`_is_deleted` AND (",
        "WHEN MATCHED AND s.`_is_deleted` AND t.`deleted_at` IS NULL THEN UPDATE SET",
        "WHEN MATCHED AND s.`_is_deleted` AND (t.`row_hash` IS NULL OR t.`row_hash` <> s.`row_hash`) THEN UPDATE SET",
    )
    positions = [sql.index(marker) for marker in markers]
    assert positions == sorted(positions)
    assert "CASE WHEN s.`_is_deleted` THEN current_timestamp() ELSE CAST(NULL AS TIMESTAMP) END" in sql
    assert sql[sql.index("WHEN NOT MATCHED BY SOURCE"):] == default[default.index("WHEN NOT MATCHED BY SOURCE"):]


def test_merge_flag_excluded_from_columns():
    sql = _merge()("lh.dbo.t", "v", ["poi_id", "name"], ("poi_id",), {}, None, "_is_deleted")
    insert = sql.split("WHEN NOT MATCHED THEN INSERT", 1)[1].split("VALUES", 1)[0]
    assert "_is_deleted" not in insert
    assert "t.`_is_deleted`" not in sql
    third = sql.split("WHEN MATCHED")[3].split("WHEN NOT MATCHED THEN")[0]
    assert "deleted_at" not in third


def test_merge_flag_rejects_owner():
    merge = _merge()
    try:
        merge("lh.dbo.t", "v", ["poi_id"], ("poi_id",), {}, "load_origin", "_is_deleted")
    except Exception as exc:
        assert type(exc).__name__ == "ConfigError"
    else:
        raise AssertionError("owner")
    try:
        merge("lh.dbo.t", "v", ["poi_id", "_is_deleted"], ("poi_id",), {}, None, "_is_deleted")
    except Exception as exc:
        assert type(exc).__name__ == "ConfigError"
    else:
        raise AssertionError("cols")


def test_diff_counts_flag_branch():
    source = _cell(LIB, CELL)
    body = _func(source, "diff_counts")
    signature = body.splitlines()[0]
    assert "deleted_flag=None" in signature
    after_doc = body.split('"""', 2)[-1].lstrip()
    assert after_doc.startswith("if deleted_flag is not None:")
    assert "_t_own" in body
    helper = _func(source, "_diff_counts_flag")
    for name in ("insert_deleted", "to_deleted", "undeleted", "deleted_changed", "deactivated"):
        assert name in helper
    assert "_s_flag" in helper and "_t_del" in helper
    assert "OWNER_COL" in helper


def test_nodespec_deleted_flag_default():
    source = _cell(LIB, CELL)
    assert "deleted_flag: Optional[str] = None" in source


def test_add_row_hash_flag_rules():
    source = _func(_cell(LIB, CELL), "add_row_hash")
    assert "c != spec.deleted_flag" in source
    assert "BooleanType" in source
    assert "soft_delete_set" in source
    assert "spec.pk" in source
    assert "TECH_NAMES" in source
    assert "if spec.deleted_flag is not None:" in source


def test_quality_gate_flag_null_block():
    source = _func(_cell(LIB, CELL), "quality_gate")
    assert source.count("deleted_flag_null") == 1
    guard = source.index("if spec.deleted_flag is not None:")
    assert source.index("deleted_flag_null") > guard


def test_invalid_flag_name_rejected_before_schema_write():
    source = _cell(LIB, CELL)
    checker = _func(source, "_flag_name_ok")
    namespace: dict = {}
    exec(checker, namespace)  # noqa: S102
    ok = namespace["_flag_name_ok"]
    assert ok("_is_deleted") is True
    assert ok("deleted") is False
    assert ok("is_deleted") is False
    assert ok("_1bad") is False
    hashed = _func(source, "add_row_hash")
    assert hashed.index("_flag_name_ok") < hashed.index('withColumn("row_hash"')
    run = _func(source, "run_node")
    assert run.index("reject_deleted_flag(") < run.index("add_row_hash(")
    assert run.index("add_row_hash(") < run.index("diff_counts(")
    assert run.index("diff_counts(") < run.index("ensure_target(")
    assert run.index("ensure_target(") < run.index("merge_target(")
    namespace = {"ConfigError": type("ConfigError", (Exception,), {}), "Optional": __import__("typing").Optional}
    exec(_func(source, "_flag_name_ok"), namespace)  # noqa: S102
    exec(_func(source, "reject_deleted_flag"), namespace)  # noqa: S102
    writes: list[str] = []

    def _stopped(name: str) -> None:
        namespace["reject_deleted_flag"](name)
        writes.append("ensure_target")
        writes.append("merge_target")

    for bad in ("", "deleted", "_1bad"):
        writes.clear()
        try:
            _stopped(bad)
        except Exception as exc:
            assert type(exc).__name__ == "ConfigError"
        else:
            raise AssertionError(bad)
        assert writes == []
    _stopped(None)
    assert writes == ["ensure_target", "merge_target"]


def test_run_node_flag_wiring():
    source = _cell(LIB, CELL)
    assert "persist_schema(df.schema, spec)" in source
    assert "diff_counts(df, trg_fq, spec.pk, spec.deleted_flag)" in source
    assert 'res["qg"]["delete_flag"]' in source
    assert "deleted_flag" in source and "APPEND" in source
    assert "def persist_schema(" in source


def test_l2_node_specs():
    for name, expect in NODE_SPEC.items():
        source = _cell(name, expect["cell"])
        namespace: dict = {}
        exec(_func(source, "_spec"), namespace)  # noqa: S102
        got = namespace["_spec"]()
        assert got["trg_tbl"] == expect["trg_tbl"]
        assert got["inputs"] == expect["inputs"]
        assert got["required_inputs"] == expect["required_inputs"]
        assert got["block_checks"] == expect["block_checks"]
        assert got["pk"] == expect["pk"]
        assert got["deleted_flag"] == "_is_deleted"
        assert got["write_mode"] == "MERGE"


def test_l2_out_cols_match_model_design():
    for name, expect in NODE_SPEC.items():
        source = _cell(name, expect["cell"])
        assert _assign(source, "OUT_COLS") == expect["out_cols"]
        assert _assign(source, "FLAG") == "_is_deleted"
        assert "return rows.select(*OUT_COLS, FLAG)" in source


def test_l2_excluded_columns_absent():
    banned = ("variants_json", "poi_id", "source_id", "destination", "meal_plan_label", "llm")
    for name, expect in NODE_SPEC.items():
        source = _cell(name, expect["cell"]).lower()
        for token in banned:
            assert token not in source


def test_price_decode_vectors():
    namespace: dict = {}
    exec(_pure(_cell("NB_SLV_PN_PRODUCT_SALE.ipynb", "pnsalebuild"), "# BEGIN_PRICE_PURE", "# END_PRICE_PURE"), namespace)  # noqa: S102
    decode = namespace["decode_price"]
    for value in (None, "", "true", "false", "@@"):
        assert decode(value, 4) is None
    assert decode("EtZE", 4) == 123.45
    assert decode("/w==", 4) == -0.0001
    assert decode("AA==", 4) == 0.0
    assert decode("1234", 4) == 1234.0
    assert decode("12.5", 2) == 12.5


def test_product_sale_build_static():
    source = _cell("NB_SLV_PN_PRODUCT_SALE.ipynb", "pnsalebuild")
    assert '"$.holiday_product_post_id"' in source
    assert 'F.col("deleted") == F.lit(False)' in source
    assert '_n") == 1' in source or '_n") == 1' in source or '== 1' in source
    assert 'F.lit("active")' in source
    assert "lower(" not in source
    assert "F.first" not in source
    assert "DECODE[4]" in source and "DECODE[2]" in source


def test_room_offer_build_static():
    source = _cell("NB_SLV_PN_HOTEL_ROOM_OFFER.ipynb", "pnroombuild")
    assert '"Active"' in source
    assert 'available_rooms") > 0' in source
    assert "coalesce(ok, F.lit(False))" in source
    assert "room_status_null" in source


def test_rate_offer_build_static():
    source = _cell("NB_SLV_PN_HOTEL_RATE_OFFER.ipynb", "pnratebuild")
    assert "valid_from" in source and "valid_to" in source
    lowered = source.lower()
    assert ".cast(" not in lowered
    assert "current_" not in lowered
    assert "valid_from" in source
    build = source[source.index("def build"):]
    for token in (">", "<", "cast(", "current_"):
        assert token not in build


def test_l2_edges_create_vs_init():
    edges = _assign(_cell("NB_CREATE_DDL.ipynb", "pnl2edgepy"), "EDGES_ON")
    namespace: dict = {}
    seed = _cell("NB_SETUP_INITIAL_DDL.ipynb", "init_seed_ctrl")
    exec(seed, namespace)  # noqa: S102
    rows = [
        row for row in namespace["PIPELINE_CONFIG_ROWS"]
        if row[4] in {"slv_pn_product_sale", "slv_pn_hotel_room_offer", "slv_pn_hotel_rate_offer"}
    ]
    assert len(rows) == 5
    assert len(edges) == 5
    for seq, src, schema, target, mode, notebook, priority in edges:
        assert seq > 0
        match = [row for row in rows if row[2] == src and row[4] == target]
        assert match == [(
            "PL_VV_TRANS_SLV_TO_GLD_30M", "lh_vv_silver.dbo", src, schema, target,
            1, priority, mode, None, None, notebook,
        )]
    assert {row[0] for row in rows} == {"PL_VV_TRANS_SLV_TO_GLD_30M"}
    assert {row[10] for row in rows} == {
        "NB_SLV_PN_PRODUCT_SALE", "NB_SLV_PN_HOTEL_ROOM_OFFER", "NB_SLV_PN_HOTEL_RATE_OFFER",
    }


def test_l2_patch_cell_guards():
    source = _cell("NB_CREATE_DDL.ipynb", "pnl2edgepy")
    order = ["Dừng trước khi ghi", "_refresh_lock()", "WHEN NOT MATCHED THEN INSERT", "Sau khi ghi"]
    assert [source.index(token) for token in order] == sorted(source.index(token) for token in order)
    assert "finally:" in source
    code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "ALTER"):
        assert token not in code
    for table in (
        "slv_pn_products", "slv_pn_product_posts", "slv_pn_product_variants",
        "slv_pn_hotel_room_types", "slv_pn_hotel_rate_plans",
    ):
        assert table in source
