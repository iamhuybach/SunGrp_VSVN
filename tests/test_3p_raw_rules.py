"""Pure checks for snapshot convert_arg rules."""
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]


def _block():
    nb = json.loads((ROOT / "notebooks" / "NB_LIB_EXTRACT_RAWDATA.ipynb").read_text(encoding="utf-8"))
    text = "".join(next(c["source"] for c in nb["cells"] if "# BEGIN_RULE_PURE" in "".join(c["source"])))
    start = text.index("# BEGIN_RULE_PURE")
    end = text.index("# END_RULE_PURE") + len("# END_RULE_PURE")
    ns: dict = {}
    exec(text[start:end], ns)  # noqa: S102
    return ns


def test_enum_and_reject_injection():
    ns = _block()
    parsed = ns["parse_convert_arg"]("ENUM_MAP", '{"map":{"PRICE_LEVEL_FREE":0,"PRICE_LEVEL_MODERATE":2}}')
    assert parsed["map"]["PRICE_LEVEL_FREE"] == 0
    with pytest.raises(ValueError):
        ns["parse_convert_arg"]("ENUM_MAP", '{"map":{"a;drop":1}}')
    with pytest.raises(ValueError):
        ns["parse_convert_arg"]("ARRAY_PICK", '{"match":"types","values":[],"take":"longText"}')
    with pytest.raises(ValueError):
        ns["parse_convert_arg"]("NONE", '{"map":{}}')


def test_sql_builders_keep_order():
    ns = _block()
    pick = ns["array_pick_sql"](
        "_raw__x",
        ns["parse_convert_arg"]("ARRAY_PICK", '{"match":"types","values":["street_number"],"take":"longText"}'),
    )
    assert "types[0]" in pick and "longText" in pick
    proj = ns["array_project_sql"](
        "_raw__x",
        ns["parse_convert_arg"](
            "ARRAY_PROJECT",
            '{"fields":[{"name":"close_hour","path":"close.hour","type":"int"}],"keep_nulls":false}',
        ),
        "CAST",
    )
    assert proj.index("close_hour") < proj.index("ignoreNullFields")
    assert "ignoreNullFields', 'true'" in proj
