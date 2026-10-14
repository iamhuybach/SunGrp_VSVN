"""Soft delete stays out of this task. Review MERGE remains insert/update only."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _text(name: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "\n".join("".join(cell["source"]) for cell in nb["cells"])


def test_soft_delete_is_not_in_this_task():
    extract = _text("NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb")
    library = _text("NB_LIB_EXTRACT_RAWDATA.ipynb")
    ddl = _text("NB_CREATE_DDL.ipynb")
    for text in (extract, library, ddl):
        assert "LATEST_DOC_FLAG" not in text
        assert "is_visibility" not in text
    assert "visibility_source_sql" not in extract
    assert "NOT MATCHED BY SOURCE" not in extract
    assert '"is_visible"' not in ddl
