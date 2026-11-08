"""Static contract for the CMS bronze-to-silver extract."""
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TABLES = (
    "slv_cms_blog",
    "slv_cms_destination",
    "slv_cms_news",
    "slv_cms_promotion_article",
)
SOURCES = {
    "slv_cms_blog": "strapi_blog",
    "slv_cms_destination": "strapi_destination",
    "slv_cms_news": "strapi_news",
    "slv_cms_promotion_article": "strapi_ph_promotion_article",
}
MODEL_COLUMNS = {
    "slv_cms_blog": (
        "document_id", "locale", "id", "slug", "cms_created_at", "cms_updated_at", "cms_published_at",
        "title", "sapo", "first_publish_date", "block_content_json", "seo_json", "platforms_json", "pois_json",
    ),
    "slv_cms_destination": (
        "document_id", "locale", "id", "slug", "cms_created_at", "cms_updated_at", "cms_published_at",
        "name", "description", "cover_gallery_json", "seo_json", "faq_json", "experiences_json",
        "highlight_json", "pois_json",
    ),
    "slv_cms_news": (
        "document_id", "locale", "id", "slug", "cms_created_at", "cms_updated_at", "cms_published_at",
        "title", "sapo", "is_featured", "block_content_json", "seo_json", "news_category_json",
    ),
    "slv_cms_promotion_article": (
        "document_id", "locale", "id", "slug", "cms_created_at", "cms_updated_at", "cms_published_at",
        "title", "short_description", "voucher_code",
        "promotion_start_datetime", "promotion_end_datetime", "usage_start_datetime", "usage_end_datetime",
        "content_json", "terms_json", "pois_json",
    ),
}


def _text(name: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell["source"]) for cell in nb["cells"])


def _fn(source: str, name: str) -> str:
    tree = ast.parse(source)
    for node in tree.body:
        if isinstance(node, ast.FunctionDef) and node.name == name:
            return ast.get_source_segment(source, node)
    raise AssertionError(name)


def _cms_rows() -> list[dict]:
    initial = json.loads((ROOT / "notebooks" / "NB_SETUP_INITIAL_DDL.ipynb").read_text(encoding="utf-8"))
    cells = {cell["id"]: "".join(cell["source"]) for cell in initial["cells"]}
    env: dict = {}
    pure = cells["init_registry_pure"]
    start = pure.index("# BEGIN_REGISTRY_PURE")
    stop = pure.index("# END_REGISTRY_PURE") + len("# END_REGISTRY_PURE")
    exec(pure[start:stop], env)  # noqa: S102
    exec(cells["init_cfg_3p"], env)  # noqa: S102
    exec(cells["init_cfg_cms"], env)  # noqa: S102
    return env["flatten_table_configs"](env["TABLE_CONFIGS_CMS"], "lh_vv_bronze.dbo", "cms_raw_data")


def _notebook_code() -> str:
    nb = json.loads((ROOT / "notebooks" / "NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb").read_text(encoding="utf-8"))
    parts = []
    for cell in nb["cells"]:
        text = "".join(cell["source"])
        if cell["cell_type"] == "code" and not text.lstrip().startswith("%"):
            parts.append(text)
    return "\n".join(parts)


def test_table_source_covers_all_four_tables():
    code = _notebook_code()
    for table, source in SOURCES.items():
        assert f'"{table}": "{source}"' in code


def test_state_key_is_row_and_doc_key_is_document_id():
    code = _notebook_code()
    assert 'doc_key_column = "document_id"' in code
    assert 'state_key      = "row"' in code
    assert 'state_key != "row"' in _fn(code, "build_context")


def test_no_type_or_lang_column_read():
    text = _text("NB_EXTRACT_CMS_CDC_BRZ_TO_SLV.ipynb")
    assert "RAW_LANG" not in text
    assert "language_code" not in text
    assert "ingested_date" not in text
    columns = _fn(_notebook_code(), "doc_columns")
    assert '"type"' not in columns


def test_presence_routes_by_source_name():
    code = _notebook_code()
    body = _fn(code, "presence")
    assert "TABLE_SOURCE" in body
    assert "F.lit(True)" not in body
    assert "_doc__source_name" in body
    assert "presence(spec)" in _fn(code, "expand_rows")


def test_key_null_checks_document_id_only():
    code = _notebook_code()
    for name in ("build_table_rows", "element_reject_rows"):
        body = _fn(code, name)
        assert "NULLABLE_KEYS" in body
        assert "doc_key_column" in body
    assert "_parse_failed" in _fn(code, "build_table_rows")


def test_merge_on_is_null_safe():
    body = _fn(_notebook_code(), "build_merge_sql")
    assert "<=>" in body
    assert "spec.key_cols" in body


def test_merge_guard_orders_by_cms_updated_at_first():
    body = _fn(_notebook_code(), "build_merge_sql")
    guard = body[body.index("WHEN MATCHED"):]
    assert guard.index("cms_updated_at") < guard.index("_crawled_at")


def test_resolve_latest_orders_by_cms_updated_at_first():
    body = _fn(_notebook_code(), "resolve_latest")
    assert body.index("cms_updated_at") < body.index("_cdc_ts_ms")
    assert "desc_nulls_last" in body


def test_registry_keys_document_id_locale():
    rows = _cms_rows()
    for table in TABLES:
        keys = [(row["trg_column"], row["key_order"]) for row in rows if row["trg_tbl"] == table and row["is_key"]]
        assert keys == [("document_id", 1), ("locale", 2)]


def test_cms_updated_at_active_on_all_tables():
    rows = _cms_rows()
    body = _fn(_notebook_code(), "check_config")
    assert "cms_updated_at" in body
    for table in TABLES:
        match = [row for row in rows if row["trg_tbl"] == table and row["trg_column"] == "cms_updated_at"]
        assert len(match) == 1 and match[0]["is_active"] is True


def test_no_date_days_on_cms_registry():
    assert all(row["convert_rule"] != "DATE_DAYS" for row in _cms_rows())


def test_no_rule_on_locale():
    for row in _cms_rows():
        if row["trg_column"] == "locale":
            assert row["convert_rule"] == "NONE"
            assert row["convert_rule"] != "LOWER_TRIM"


def test_first_publish_date_is_date_none():
    match = [row for row in _cms_rows() if row["trg_column"] == "first_publish_date"]
    assert len(match) == 1
    assert match[0]["data_type"] == "date"
    assert match[0]["convert_rule"] == "NONE"


def test_registry_columns_match_model_design():
    grouped: dict[str, list[str]] = {table: [] for table in TABLES}
    for row in _cms_rows():
        grouped[row["trg_tbl"]].append(row["trg_column"])
    assert grouped == {table: list(columns) for table, columns in MODEL_COLUMNS.items()}
    assert sum(len(columns) for columns in grouped.values()) == 59


def test_config_rows_doc_mode_fl00():
    seed = _text("NB_SETUP_INITIAL_DDL.ipynb")
    for table in TABLES:
        assert f"(_FL00, _B, 'cms_raw_data', _S, '{table}', 1, 1, 'DOC', None, None, None)" in seed


def test_watermark_row_seeded():
    seed = _text("NB_SETUP_INITIAL_DDL.ipynb")
    assert 'wm_transform_cms_raw_data' in seed
    assert "NB_EXTRACT_CMS_CDC_BRZ_TO_SLV" in seed


def test_seed_cells_match_between_ddl_notebooks():
    initial = _text("NB_SETUP_INITIAL_DDL.ipynb")
    create = _text("NB_CREATE_DDL.ipynb")
    start = initial.index("TABLE_CONFIGS_CMS = [")
    stop = initial.index("]", start) + 1
    block = initial[start:stop]
    assert block in create
    assert 'seed_registry(TABLE_CONFIGS_CMS, "lh_vv_bronze.dbo", "cms_raw_data")' in create
