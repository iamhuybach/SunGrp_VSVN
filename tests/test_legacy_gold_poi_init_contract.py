"""Contract checks for the one-time legacy gold init. No Spark."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _notebook(name: str) -> dict:
    return json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))


def _cell(nb: dict, cell_id: str) -> str:
    return "".join(next(cell["source"] for cell in nb["cells"] if cell.get("id") == cell_id))


def _func(source: str, name: str) -> str:
    lines = source.splitlines()
    start = next(i for i, line in enumerate(lines) if line.startswith(f"def {name}("))
    end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("def ")), len(lines))
    return "\n".join(lines[start:end])


def test_owner_col_constants():
    source = _cell(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"), "9ff87eee")
    start = source.index("TECH_COLUMNS = ")
    end = source.index("TABLE_PROPERTIES = ")
    namespace: dict = {}
    exec(source[start:end], namespace)  # noqa: S102
    assert namespace["OWNER_COL"] == "load_origin"
    assert namespace["TECH_NAMES"] == tuple(name for name, _dtype in namespace["TECH_COLUMNS"]) + ("load_origin",)


def test_sql_merge_target_without_owner_is_unchanged():
    source = _cell(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"), "926a3f9c")
    namespace = {"quote_name": lambda fq: fq, "Optional": __import__("typing").Optional}
    exec(_func(source, "sql_merge_target"), namespace)  # noqa: S102
    sql = namespace["sql_merge_target"]("lh.dbo.t", "v", ["poi_id", "poi_name"], ("poi_id",), {})
    matched = "WHEN MATCHED AND (t.`row_hash` IS NULL OR t.`row_hash` <> s.`row_hash` OR t.`deleted_at` IS NOT NULL) THEN UPDATE SET"
    assert matched in sql
    assert "WHEN NOT MATCHED BY SOURCE AND t.`deleted_at` IS NULL THEN UPDATE SET" in sql
    assert "load_origin" not in sql


def test_sql_merge_target_owner_predicates():
    source = _cell(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"), "926a3f9c")
    namespace = {"quote_name": lambda fq: fq, "Optional": __import__("typing").Optional}
    exec(_func(source, "sql_merge_target"), namespace)  # noqa: S102
    sql = namespace["sql_merge_target"]("lh.dbo.t", "v", ["poi_id"], ("poi_id",), {}, "load_origin")
    assert "t.`load_origin` = CAST(NULL AS STRING)" in sql
    assert "OR t.`load_origin` IS NOT NULL" in sql
    assert "WHEN NOT MATCHED BY SOURCE AND t.`deleted_at` IS NULL AND t.`load_origin` IS NULL THEN UPDATE SET" in sql


def test_merge_target_passes_owner_only_when_column_present():
    source = _cell(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"), "926a3f9c")
    assert "owner = OWNER_COL if OWNER_COL in table_columns(fq) else None" in source
    assert "sql_merge_target(fq, view, cols, spec.pk, spec.soft_delete_set, owner)" in source
    assert "before_write()" in source
    assert "merge_target(trg_fq, df, spec, tag, lambda: refresh_flow_lock(pl, exec_id))" in source


def test_diff_counts_mirrors_owner():
    source = _func(_cell(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"), "926a3f9c"), "diff_counts")
    assert "_t_own" in source
    assert 'F.col("_t_own").isNotNull()' in source
    assert 'F.col("_t_own").isNull()' in source


def test_insert_only_sql_has_no_update_or_delete():
    source = _cell(_notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgppure")
    namespace = {"quote_name": lambda fq: fq}
    exec(_func(source, "insert_only_sql"), namespace)  # noqa: S102
    sql = namespace["insert_only_sql"]("sgr_visitvn_dev.lh_vv_gold.dbo.t", "v", ["poi_id"], ("poi_id",))
    assert "WHEN NOT MATCHED THEN INSERT" in sql
    assert "UPDATE SET" not in sql
    assert "DELETE" not in sql


def test_legacy_upsert_updates_only_legacy_rows():
    source = _cell(_notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgppure")
    namespace = {"quote_name": lambda fq: fq}
    exec(_func(source, "legacy_upsert_sql"), namespace)  # noqa: S102
    sql = namespace["legacy_upsert_sql"](
        "sgr_visitvn_dev.lh_vv_gold.dbo.t",
        "v",
        ["poi_id", "poi_name", "created_at", "deleted_at", "load_origin"],
        ("poi_id",),
    )
    update = sql.split("UPDATE SET", 1)[1].split("WHEN NOT MATCHED", 1)[0]
    assert "t.`load_origin` = 'LEGACY_INIT'" in sql
    assert "WHEN NOT MATCHED THEN INSERT" in sql
    assert "t.`poi_name` = s.`poi_name`" in update
    assert "created_at" not in update
    assert "deleted_at" not in update
    assert "load_origin" not in update
    plain = namespace["legacy_upsert_sql"](
        "sgr_visitvn_dev.lh_vv_gold.dbo.t", "v", ["poi_id", "row_hash", "load_origin"], ("poi_id",))
    claimed = namespace["legacy_upsert_sql"](
        "sgr_visitvn_dev.lh_vv_gold.dbo.t", "v", ["poi_id", "row_hash", "load_origin"], ("poi_id",), True)
    assert "load_origin IS NULL" not in plain
    assert "t.`load_origin` IS NULL AND t.`row_hash` = s.`row_hash`" in claimed
    assert "t.`load_origin` = 'LEGACY_INIT'" in claimed
    main = _cell(_notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgpmain")
    assert '"info", "info", True)' in main
    assert '"multi_lang", True)' in main
    assert 'display["experiences"].alias("experience")' in main
    assert '"media", "media", True, True)' in main
    assert 'MEDIA_FQ = "sgr_visitvn_dev.lh_vv_gold.dbo.gld_srv_poi_media_gallery"' in _cell(
        _notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgpconst")


def test_new_poi_id_hash_order():
    source = _cell(_notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgppure")
    google = source.index('uuid_md5(F.lit("google"), source_id)')
    partner = source.index('uuid_md5(source_id, F.lit("partner"))')
    assert google < partner
    assert "partner_portal" not in _func(source, "new_poi_id")


def test_init_write_targets_dev_only():
    notebook = _notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb")
    constants = _cell(notebook, "lgpconst")
    for name in ("MAP_FQ", "INFO_FQ", "ML_FQ", "REV_FQ"):
        assert f'{name} = "sgr_visitvn_dev.' in constants
    assert 'OLD = "sgr_visitvn_prd_batch.lh_vv_gold.dbo"' in constants
    assert 'fq.startswith("sgr_visitvn_dev.")' in _cell(notebook, "lgpmain")
    main = _cell(notebook, "lgpmain")
    assert 'F.col("_s_legacy_poi_id").isNotNull()' in main
    assert "LEGACY_INIT:{EXEC}" in main
    assert "isinstance(raw, dict)" in main
    assert 'if status == "SUCCESS":' in main
    assert 'summary["info"]["detail_conflict_n"]' in main


def test_legacyid_ddl_cell_contract():
    source = _cell(_notebook("NB_CREATE_DDL.ipynb"), "legacyidpy")
    assert "gld_poi_legacy_id_map" in source
    assert "CREATE TABLE IF NOT EXISTS" in source
    assert "ADD COLUMNS" in source
    assert 'OWNER = ("load_origin", "STRING")' in source
    for table in ("gld_srv_poi_info", "gld_srv_poi_multi_lang", "gld_srv_poi_review", "gld_srv_poi_amenity", "gld_srv_poi_media_gallery"):
        assert table in source
    assert 'WS = "sgr_visitvn_dev"' in source


def test_amenity_enum_values_and_dictionary_join():
    pure = _cell(_notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgppure")
    namespace = {}
    exec(_func(pure, "amenity_enum_values"), namespace)  # noqa: S102
    raw = (
        '{"facilities":{"specialty_tags":{"enum":["seafood_restaurant"," seafood_restaurant "],'
        '"type":"array"},"empty":{"enum":["", "  "]}}}'
    )
    rows = namespace["amenity_enum_values"](raw)
    assert rows == ["seafood_restaurant\x1ffacilities.specialty_tags"]
    flag = '{"parkingOptions":{"freeStreetParking":true}}'
    assert namespace["amenity_enum_values"](flag) == ["true\x1fparkingOptions.freeStreetParking"]
    assert namespace["amenity_enum_values"]("{") == []
    main = _cell(_notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgpmain")
    assert "ref_dictionary_amenities" in _cell(_notebook("NB_SETUP_LEGACY_GOLD_POI.ipynb"), "lgpconst")
    assert 'F.col("e._token") == F.col("d._en")' in main
    assert 'F.col("e._path") == F.col("d._raw")' in main
    assert 'F.lower(F.trim(F.col("e.business_sector"))) == F.col("d._sector")' in main
    assert '"amenity", "amenity", True)' in main
