"""Contract checks for the enrichment extract and the schema rewrite cells."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NB = ROOT / "notebooks"


def _notebook(name):
    return json.loads((NB / name).read_text(encoding="utf-8"))


def _cell(name, cell_id):
    for cell in _notebook(name)["cells"]:
        if cell.get("id") == cell_id:
            return "".join(cell["source"])
    raise AssertionError(cell_id)


def _extract():
    return "\n".join(
        _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", cid)
        for cid in ("enr04", "enr06", "enr08", "enr12")
    )


def _pure(cell_id):
    source = _cell("NB_CREATE_DDL.ipynb", cell_id)
    start = source.index("# BEGIN_REWRITE_PURE")
    end = source.index("# END_REWRITE_PURE") + len("# END_REWRITE_PURE")
    namespace: dict = {}
    exec(source[start:end], namespace)  # noqa: S102
    return namespace["plan_rewrite"], source


def test_presence_routes_by_event_type_exact():
    source = _extract()
    assert 'F.trim(F.col("_doc__event_type")) == F.lit(expected)' in source
    assert "TABLE_EVENT_TYPE" in source


def test_no_lit_true_presence():
    body = _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", "enr06")
    start = body.index("def presence")
    end = body.index("def bad_shape")
    assert "F.lit(True)" not in body[start:end]


def test_state_key_row_and_all_keys_checked():
    source = _extract()
    assert 'state_key      = "row"' in source
    assert "needed = [k for k in keys if k not in NULLABLE_KEYS]" in source


def test_order_columns_version_then_event_processed():
    source = _extract()
    assert 'F.col("_src_version").desc()' in source
    assert 'F.col("_event_processed_at").desc()' in source
    assert 'F.col("_event_id").desc()' in source


def test_merge_guard_strict_tuple():
    source = _extract()
    guard = source.split("WHEN MATCHED", 1)[1].split("THEN UPDATE", 1)[0]
    assert "s.`_src_version` > coalesce(t.`_src_version`, -1)" in source
    assert "s.`_event_id` > t.`_event_id`" in guard
    assert ">=" not in guard


def test_merge_on_keys():
    source = _extract()
    assert 'for k in spec.key_cols' in source


def test_array_projection_uses_from_json_transform_to_json():
    source = _extract()
    assert "F.from_json" in source and "F.transform" in source and "F.to_json" in source
    assert "ARRAY_PROJECTIONS" in source


def test_no_get_json_object_wildcard():
    source = _extract()
    assert "$[*]" not in source


def test_registry_paths_relative_to_data():
    source = _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", "enr12")
    assert 'p.startswith("data.")' in source


def test_registry_columns_match_model_design():
    source = _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", "enr04")
    assert '"destinations.id": "id"' in source
    assert '"destinations.name": "name"' in source


def test_const_null_cols_not_in_registry():
    source = _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", "enr04")
    assert "country_code" in source and "postal_code" in source


def test_config_and_watermark_rows():
    setup = "".join(
        "".join(cell["source"])
        for cell in _notebook("NB_SETUP_INITIAL_DDL.ipynb")["cells"]
        if cell.get("id") == "init_seed_ctrl"
    )
    assert "brz_enrichment_result" in setup
    assert "wm_transform_brz_enrichment_result" in setup
    assert "EventProcessedUtcTime" in setup


def test_seed_cells_match_between_ddl_notebooks():
    create = _cell("NB_CREATE_DDL.ipynb", "enrbrzcfgpy")
    assert "ENR_PIPELINE" in create and "ENR_WATERMARK" in create
    assert "slv_enr_poi_info_multi_lang" in create
    assert "slv_enr_poi_destination" in create


def test_extract_preflight_retired_and_const_null_columns():
    source = _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", "enr08")
    assert "RETIRED_COLS" in source and "CONST_NULL_COLS" in source
    assert 'raise ConfigError("run enrbrzpy")' in source


def test_rewrite_plan_skip_when_equal():
    plan, _source = _pure("enrbrzpy")
    cols = [("a", "string", True)]
    assert plan(cols, cols, {}, set())[0] == "SKIP"


def test_rewrite_plan_renames_cost_vnd():
    plan, _source = _pure("enrbrzpy")
    action, items, _nulls = plan(
        [("cost_vnd", "string", True)], [("cost", "string", True)], {"cost": "cost_vnd"}, set(),
    )
    assert action == "REWRITE"
    assert items == [("COL", "cost_vnd", "cost", "string")]


def test_rewrite_plan_drop_only_allowed():
    plan, _source = _pure("enrbrzpy")
    action, _items, _nulls = plan(
        [("street", "string", True), ("poi_id", "string", False)],
        [("poi_id", "string", False)],
        {},
        {"street"},
    )
    assert action == "REWRITE"


def test_rewrite_plan_rejects_old_and_new_together():
    plan, _source = _pure("enrbrzpy")
    with pytest.raises(ValueError):
        plan(
            [("cost_vnd", "string", True), ("cost", "string", True)],
            [("cost", "string", True)],
            {"cost": "cost_vnd"},
            set(),
        )


def test_rewrite_plan_type_mismatch_raises():
    plan, _source = _pure("enrbrzpy")
    with pytest.raises(ValueError):
        plan([("cost", "string", True)], [("cost", "int", True)], {}, set())


def test_rewrite_plan_not_null_without_source_raises():
    plan, _source = _pure("enrbrzpy")
    with pytest.raises(ValueError):
        plan([], [("poi_id", "string", False)], {}, set())


def test_rewrite_pure_block_identical_in_both_cells():
    left, _source = _pure("enrbrzpy")
    right, _gold = _pure("enrgldpy")
    assert left.__code__.co_code == right.__code__.co_code


def test_rewrite_cells_no_drop_table_columnmapping_rename():
    for cell_id in ("enrbrzpy", "enrgldpy"):
        source = _cell("NB_CREATE_DDL.ipynb", cell_id)
        assert "DROP TABLE" not in source
        assert "columnMapping" not in source
        assert "RENAME COLUMN" not in source


def test_rewrite_cells_overwrite_schema_from_pinned_version():
    source = _cell("NB_CREATE_DDL.ipynb", "enrbrzpy")
    assert "overwriteSchema" in source and "VERSION AS OF" in source


def test_rewrite_cells_restore_on_failed_check():
    source = _cell("NB_CREATE_DDL.ipynb", "enrbrzpy")
    assert "RESTORE TABLE" in source and "RESTORED" in source


def test_rewrite_cells_hold_locks():
    silver = _cell("NB_CREATE_DDL.ipynb", "enrbrzpy")
    gold = _cell("NB_CREATE_DDL.ipynb", "enrgldpy")
    assert "wm_transform_brz_enrichment_result" in silver
    assert "wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M" in silver
    assert "wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M" in gold


def test_silver_rewrite_targets_match_initial_ddl():
    import ast

    source = _cell("NB_CREATE_DDL.ipynb", "enrbrzpy")
    tree = ast.parse(source)
    targets = next(
        ast.literal_eval(node.value)
        for node in tree.body
        if isinstance(node, ast.Assign) and any(getattr(t, "id", None) == "SILVER_TARGETS" for t in node.targets)
    )
    setup = json.loads((ROOT / "notebooks" / "NB_SETUP_INITIAL_DDL.ipynb").read_text(encoding="utf-8"))
    specs = {}
    exec("".join(next(c["source"] for c in setup["cells"] if c.get("id") == "init_tables")), specs)  # noqa: S102
    for spec in specs["TABLE_SPECS"]:
        if spec["fq"] not in targets:
            continue
        expected = []
        for name, typ, _comment in spec["cols"]:
            not_null = "NOT NULL" in typ.upper()
            base = typ.upper().replace(" NOT NULL", "").strip().lower()
            expected.append((name, base, not not_null))
        assert targets[spec["fq"]] == expected


def test_gold_rewrite_rename_map_only_cost():
    source = _cell("NB_CREATE_DDL.ipynb", "enrgldpy")
    assert "GOLD_RENAMES" in source and "cost_vnd" in source
    assert "GOLD_DROPS = set()" in source


def test_rewrite_cells_order_after_seeds_cell():
    ids = [cell.get("id") for cell in _notebook("NB_CREATE_DDL.ipynb")["cells"]]
    assert ids.index("enrbrzcfgpy") < ids.index("enrbrzpy") < ids.index("enrgldpy")
    assert ids[-6:] == ["enrbrzcfgmd", "enrbrzcfgpy", "enrbrzmd", "enrbrzpy", "enrgldmd", "enrgldpy"]


def test_state_orders_by_version_before_time():
    source = _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", "enr06")
    start = source.index("# BEGIN_EVENT_ORDER_PURE")
    end = source.index("# END_EVENT_ORDER_PURE") + len("# END_EVENT_ORDER_PURE")
    namespace: dict = {}
    exec(source[start:end], namespace)  # noqa: S102
    newer = namespace["event_is_newer"]
    assert newer((2, 1, "a"), (1, 9, "z")) is True
    assert newer((2, 1, "a"), (1, 9, "z")) is True
    assert newer((1, 1, "b"), (1, 1, "a")) is True
    assert newer((1, 1, "a"), (1, 1, "a")) is False
    assert 'F.col("_doc__version").cast("bigint")' in source
    assert "unix_millis" not in source


def test_extract_drops_cms_source_names():
    code = _extract()
    assert "TABLE_SOURCE" not in code
    assert "split_csv(sources)" not in code
    assert '"_crawled_at"' not in code


def test_projection_failure_counts_as_cast_null():
    source = _cell("NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb", "enr08")
    assert "c.json_path in ARRAY_PROJECTIONS" in source
    assert "arr.isNull()" in source


def test_blank_event_id_and_payload_tie():
    source = _extract()
    assert 'F.lit("thiếu event_id")' in source
    assert "payload khác" in source


def test_rewrite_skip_rechecks_and_lease_matches_extract():
    for cell_id in ("enrbrzpy", "enrgldpy"):
        source = _cell("NB_CREATE_DDL.ipynb", cell_id)
        assert "def _confirm_skip" in source
        assert "def _touch_locks" in source
        assert "INTERVAL 780 MINUTES" in source
        assert "INTERVAL 120 MINUTES" not in source


def test_restore_stops_when_later_commit_exists():
    source = _cell("NB_CREATE_DDL.ipynb", "enrbrzpy")
    start = source.index("# BEGIN_RESTORE_FENCE_PURE")
    end = source.index("# END_RESTORE_FENCE_PURE") + len("# END_RESTORE_FENCE_PURE")
    namespace: dict = {}
    exec(source[start:end], namespace)  # noqa: S102
    restore = namespace["should_auto_restore"]
    assert restore(5, 5) is True
    assert restore(5, 5) is True
    assert restore(6, 5) is False
    assert restore(5, None) is False
    gold = _cell("NB_CREATE_DDL.ipynb", "enrgldpy")
    assert source[start:end] == gold[gold.index("# BEGIN_RESTORE_FENCE_PURE"):gold.index("# END_RESTORE_FENCE_PURE") + len("# END_RESTORE_FENCE_PURE")]
    assert "không RESTORE" in source and "_fence(" in source
    assert "v0={v0}" in source
    assert "Cannot change nullable column to non-nullable" in source
    assert "NOT NULL giữ nullable" in source


def test_watermark_seed_tuples_are_separated():
    source = _cell("NB_CREATE_DDL.ipynb", "3ea73e14-6a1f-42a5-b960-34123b0a3fc4")
    assert "current_timestamp()),\n    ('wm_transform_brz_enrichment_result'" in source
