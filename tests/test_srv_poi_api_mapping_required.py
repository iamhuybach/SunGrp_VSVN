"""Mapping contract for the six POI serving read APIs (task 20261110-serving-poi-read-apis).

Checks the Required rule (D-4), the ApiResponse envelope (D-3), the D-1 source columns,
the D-5 rating_summary placement, and that every cited apps.srv_poi_* column exists in the DDL.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
MAPPING_DIR = ROOT / "docs" / "context" / "api-mapping"
DDL = ROOT / "sql" / "postgres" / "gld_srv_serve.pg.sql"
FILES = ("compact", "gallery", "reviews", "features", "experiences", "practical_info")
PATH_POI_ID_FILES = ("gallery", "reviews", "experiences", "practical_info")
REQUEST_SECTIONS = ("Request header", "Request param", "Request body")
ENVELOPE_KEYS = {"success", "code", "message", "data", "meta", "errors"}
PAGINATION_KEYS = {"type", "page", "per_page", "total_items", "total_pages", "has_next", "has_prev"}


def _text(name: str) -> str:
    return (MAPPING_DIR / f"{name}.md").read_text(encoding="utf-8")


def _section(text: str, heading: str) -> str | None:
    match = re.search(rf"^## {re.escape(heading)}[ \t]*$(.*?)(?=^## |\Z)", text, re.M | re.S)
    return match.group(1) if match else None


def _rows(section: str | None) -> list[dict[str, str]]:
    if not section:
        return []
    lines = [line.strip() for line in section.splitlines() if line.strip().startswith("|")]
    if len(lines) < 3:
        return []
    header = [cell.strip() for cell in lines[0].strip("|").split("|")]
    return [dict(zip(header, (cell.strip() for cell in line.strip("|").split("|")), strict=False)) for line in lines[2:]]


def _request_rows(name: str) -> list[tuple[str, dict[str, str]]]:
    text = _text(name)
    return [(heading, row) for heading in REQUEST_SECTIONS for row in _rows(_section(text, heading))]


def _sample_response(name: str) -> dict:
    section = _section(_text(name), "Sample response")
    assert section, f"{name}.md has no Sample response section"
    match = re.search(r"```json[ \t]*\n(.*?)\n```", section, re.S)
    assert match, f"{name}.md Sample response has no json block"
    return json.loads(match.group(1))


def _ddl_columns() -> dict[str, set[str]]:
    tables: dict[str, set[str]] = {}
    ddl = DDL.read_text(encoding="utf-8")
    for table, body in re.findall(r"CREATE TABLE apps\.(\w+) \((.*?)\n\);", ddl, re.S):
        tables[table] = {m.group(1) for m in re.finditer(r"^\s+(\w+)\s+\w", body, re.M) if m.group(1) != "PRIMARY"}
    return tables


@pytest.mark.parametrize("name", FILES)
def test_only_path_poi_id_or_compact_body_ids_is_required(name):
    rows = _request_rows(name)
    assert rows, f"{name}.md has no request table"
    for heading, row in rows:
        field, required = row.get("Field", ""), row.get("Required", "")
        assert required in {"có", "không"}, f"{name}.md {heading} {field}: Required={required!r}"
        if required == "có":
            assert name != "compact", f"{name}.md {heading} {field} must be Required = không"
            assert (heading, field) == ("Request param", "poi_id"), (
                f"{name}.md {heading} {field} must be Required = không"
            )


@pytest.mark.parametrize("name", PATH_POI_ID_FILES)
def test_path_poi_id_is_required(name):
    params = {row["Field"]: row for heading, row in _request_rows(name) if heading == "Request param"}
    assert params["poi_id"]["Required"] == "có"


def test_compact_is_post_with_optional_body_fields():
    text = _text("compact")
    assert re.search(r"^\|\s*Method\s*\|\s*POST\s*\|", _section(text, "Tổng quan") or "", re.M)
    body = {row["Field"]: row for row in _rows(_section(text, "Request body"))}
    assert body["ids"]["Required"] == "không"
    assert body["lang"]["Required"] == "không"
    other = {row["Field"] for heading, row in _request_rows("compact") if heading != "Request body"}
    assert not other & {"ids", "page", "size", "sort", "poi_id"}


@pytest.mark.parametrize("name", FILES)
def test_sample_response_uses_api_response_envelope(name):
    body = _sample_response(name)
    expected = ENVELOPE_KEYS | ({"rating_summary"} if name == "reviews" else set())
    assert set(body) == expected
    assert body["success"] is True
    assert body["code"] == 200
    assert body["errors"] is None
    assert isinstance(body["meta"]["timestamp"], str)
    assert isinstance(body["meta"]["trace_id"], str)


@pytest.mark.parametrize("name", ("gallery", "reviews", "features"))
def test_paged_sample_has_full_offset_pagination(name):
    assert set(_sample_response(name)["meta"]["pagination"]) == PAGINATION_KEYS


@pytest.mark.parametrize("name", ("compact", "experiences", "practical_info"))
def test_unpaged_sample_has_no_pagination(name):
    assert "pagination" not in _sample_response(name)["meta"]


def test_compact_sample_drops_omitted_fields():
    item = _sample_response("compact")["data"][0]
    assert set(item["cover"]) == {"id", "file_key"}
    assert "business_sector_label" not in item["business_tags"]


def test_gallery_sample_item_has_three_keys():
    assert set(_sample_response("gallery")["data"][0]) == {"id", "file_key", "display_order"}


def test_reviews_rating_summary_is_one_element_sibling_of_data():
    body = _sample_response("reviews")
    assert isinstance(body["data"], list)
    assert len(body["rating_summary"]) == 1
    assert set(body["rating_summary"][0]) == {"rating_count", "rating_avg_score"}


def test_d1_source_columns():
    for name in ("compact", "features"):
        response = _section(_text(name), "Response") or ""
        assert "apps.srv_poi_info.cover_id" in response, name
        assert "apps.srv_poi_info.cover_blob_url" in response, name
        assert "srv_poi_media_gallery" not in response, name
    experiences = _section(_text("experiences"), "Response") or ""
    assert "apps.srv_poi_multi_lang.source_name" in experiences
    assert not re.search(r"apps\.srv_poi_multi_lang\.source(?!_name)", experiences)
    gallery = _section(_text("gallery"), "Response") or ""
    assert "apps.srv_poi_media_gallery.blob_url" in gallery
    assert "photo_api_uri" not in gallery


@pytest.mark.parametrize("name", FILES)
def test_cited_source_columns_exist_in_ddl(name):
    tables = _ddl_columns()
    for table, column in re.findall(r"apps\.(srv_poi_\w+)\.(\w+)", _text(name)):
        assert table in tables, f"{name}.md cites unknown table apps.{table}"
        assert column in tables[table], f"{name}.md cites missing column apps.{table}.{column}"
