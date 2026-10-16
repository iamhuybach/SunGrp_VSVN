"""Contract checks for ref_dictionary_place_type and slv_poi_entity. No Spark."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "docs" / "context" / "3p-google" / "mapping_place_type.md"

SECTOR = {"1": "accommodation", "2": "f_n_b", "3": "spa_n_wellness", "4": "shopping_n_retail",
          "5": "attraction", "6": "vehicle_rental", "7": "other"}
SKIP = {"Partner Portal bổ sung", "Partner Portal Bổ sung", "Fallback", "Không có"}
SECTION_RE = re.compile(r"^#\s+\*\*1\.(\d)")
TOKEN_RE = re.compile(r"[a-z0-9_]+")
ROLES = (("Partner Portal Enum", "partner"), ("Google Place API", "google"), ("(VI)", "vi"),
         ("(EN)", "en"), ("Fabric Enum", "fabric"))
U2_TOKENS = {"national_park", "hiking_area", "church", "hindu_temple", "mosque", "synagogue"}


def _cell(text):
    text = text.replace("**", "").replace("`", "").replace("\xa0", " ").strip()
    return text or None


def parse_mapping(md):
    rows, sector, cols = [], None, None
    for line in md.splitlines():
        m = SECTION_RE.match(line)
        if m:
            sector, cols = SECTOR[m.group(1)], None
            continue
        if not line.lstrip().startswith("|"):
            continue
        cells = [_cell(c) for c in line.strip().strip("|").split("|")]
        if all(c is None or set(c) <= {"-"} for c in cells):
            continue
        if any(c and "Google Place API" in c for c in cells):
            cols = {role: i for i, c in enumerate(cells) for key, role in ROLES if c and key in c}
            continue
        if cols is None:
            continue
        get = lambda r: cells[cols[r]] if r in cols else None  # noqa: B023
        en, vi = (get("fabric"), None) if "fabric" in cols else (get("en"), get("vi"))
        partner, google = get("partner"), get("google")
        if partner and partner not in SKIP:
            rows.append(("partner", partner, sector, en, vi))
        if google and google not in SKIP:
            for tok in (t.strip() for t in google.split(",")):
                if tok and not TOKEN_RE.fullmatch(tok):
                    raise ValueError(f"bad token {tok!r} in {sector}")
                if tok:
                    rows.append(("google", tok, sector, en, vi))
    seen, out, conflicts = {}, [], set()
    for r in rows:
        k = r[:2]
        if k not in seen:
            seen[k] = r
            out.append(r)
        elif seen[k] != r:
            conflicts.add(k)
    return out, conflicts


def _nb(name: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "".join("".join(cell["source"]) for cell in nb["cells"])


def _seed_ns():
    text = _nb("NB_SETUP_POI_ENTITY.ipynb")
    start = text.index("# BEGIN_PLACE_TYPE_SEED")
    end = text.index("# END_PLACE_TYPE_SEED")
    ns: dict = {}
    exec(text[start:end], ns)  # noqa: S102
    return ns


def test_seed_matches_mapping_file():
    ns = _seed_ns()
    rows, _conflicts = parse_mapping(MAPPING.read_text(encoding="utf-8"))
    assert ns["SEED_ROWS"] == rows
    ns["validate_seed"](ns["SEED_ROWS"])


def test_seed_excludes_placeholders():
    ns = _seed_ns()
    rows = ns["SEED_ROWS"]
    assert not any(place in SKIP for _source, place, *_rest in rows)
    stay = [source for source, place, *_rest in rows if place == "extended_stay_hotel"]
    assert stay == ["google"]
    for place in ("Blind Massage", "Local Specialty"):
        sources = [source for source, token, *_rest in rows if token == place]
        assert sources == ["partner"]


def test_seed_keys_unique_and_tokens_valid():
    ns = _seed_ns()
    rows = ns["SEED_ROWS"]
    keys = [(source, place) for source, place, *_rest in rows]
    assert len(keys) == len(set(keys))
    token_re = re.compile(r"^[a-z0-9_]+$")
    assert all(token_re.fullmatch(place) for source, place, *_rest in rows if source == "google")


def test_seed_sector_normalization():
    ns = _seed_ns()
    rows = ns["SEED_ROWS"]
    assert {sector for _source, _place, sector, *_rest in rows} == set(SECTOR.values())
    hotel = [sector for source, place, sector, *_rest in rows if source == "google" and place == "hotel"]
    airport = [sector for source, place, sector, *_rest in rows if source == "google" and place == "airport"]
    assert hotel == ["accommodation"]
    assert airport == ["other"]


def test_seed_conflicts_pinned():
    rows, conflicts = parse_mapping(MAPPING.read_text(encoding="utf-8"))
    assert {place for _source, place in conflicts} == U2_TOKENS
    winners = {place: (sector, en, vi) for source, place, sector, en, vi in rows if source == "google"}
    assert winners["national_park"] == ("attraction", "Nature Reserve", "Khu bảo tồn thiên nhiên")
    assert winners["hiking_area"] == ("attraction", "Nature Reserve", "Khu bảo tồn thiên nhiên")
    for place in ("church", "hindu_temple", "mosque", "synagogue"):
        assert winners[place] == ("attraction", "Religious Site", "Điểm đến tâm linh")


def test_seed_counts():
    ns = _seed_ns()
    rows = ns["SEED_ROWS"]
    assert sum(source == "google" for source, *_rest in rows) == 297
    assert sum(source == "partner" for source, *_rest in rows) == 59


def test_entity_node_contract():
    src = _nb("NB_SLV_POI_ENTITY.ipynb")
    assert 'trg_tbl="slv_poi_entity"' in src
    assert '"poi": "slv_3p_poi"' in src
    assert '"dict": "ref_dictionary_place_type"' in src
    assert 'pk=("poi_id",)' in src
    assert 'write_mode="MERGE"' in src
    assert 'required_inputs=("poi", "dict")' in src
    assert "posexplode(" in src
    assert "min_by(" in src
    assert '"_pos"' in src
    assert 'F.lit(None).cast("string")' in src
    assert "== GOOGLE" in src
    assert "posexplode_outer" not in src
    assert "explode(" not in src.replace("posexplode(", "")
    assert src.index('F.col("_p")') < src.index('F.col("_m")')


def test_setup_contract():
    src = _nb("NB_SETUP_POI_ENTITY.ipynb")
    assert 'p_apply = "false"' in src
    ddl = src[src.index("CREATE TABLE"):src.index("TBLPROPERTIES")]
    for name, dtype in (
        ("source_name", "STRING"),
        ("place_type", "STRING"),
        ("business_sector", "STRING"),
        ("business_category", "STRING"),
        ("business_category_vi", "STRING"),
        ("is_active", "BOOLEAN"),
        ("updated_at", "TIMESTAMP"),
    ):
        assert name in ddl and dtype in ddl
    seed = src[src.index("MERGE INTO lh_vv_silver.dbo.ref_dictionary_place_type"):src.index("inserted=")]
    assert "WHEN NOT MATCHED" in seed
    assert "WHEN MATCHED" not in seed
    edges = src[src.index("def _write_edges"):src.index("with_retry(_write_edges")]
    match_on = edges[edges.index("ON t.pl_name"):edges.index("WHEN MATCHED")]
    assert "src_schema" not in match_on and "trg_schema" not in match_on
    assert "<=>" in edges
    assert "src_schema = 'lh_vv_silver.dbo'" in edges
    assert "trg_schema = 'lh_vv_silver.dbo'" in edges
    assert "PL_VV_TRANS_SLV_TO_SLV_1H" in edges
    assert "RECOMPUTE" in edges
    assert "WHEN MATCHED" in edges
    assert "WHEN NOT MATCHED" in edges
    assert "NOT EXISTS" in edges
    assert "pl_name <> 'PL_VV_TRANS_SLV_TO_SLV_1H'" in edges
    assert "is_active = 1" in edges
    assert "priority = 1" in edges
    assert "'slv_3p_poi'" in edges
    assert "'ref_dictionary_place_type'" in edges
    assert "cạnh active không đúng" in edges
