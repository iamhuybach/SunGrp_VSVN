"""Contract checks for ref_dictionary_place_type and slv_poi_entity_non_enrich. No Spark."""
import ast
import json
import re
from datetime import datetime, timedelta
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
            sector, cols = SECTOR.get(m.group(1)), None
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


def _nb_cell(name: str, cell_id: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    for item in nb["cells"]:
        if item.get("id") == cell_id:
            return "".join(item["source"])
    raise AssertionError(cell_id)


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
    assert [row[:5] for row in ns["SEED_ROWS"][:356]] == rows
    new = ns["SEED_ROWS"][356:]
    assert [row[1] for row in new] == [
        "cable_car", "safari", "theme", "vinwonders", "night_market", "pagoda", "temple", "prison",
        "snorkel", "island", "boat",
        "snorkeling", "diving", "scuba", "canoe", "ferry", "sailing", "sunset", "coast", "coastal",
        "stream", "suối", "thác", "forest", "hiking", "trekking", "trail", "shopping", "mall",
        "wellness", "theme_park",
    ]
    assert all(row[2:5] == ("other", "other", "other") for row in new)
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
    keep = set(ns["TOKEN_KEEP"])
    assert all(place in keep or token_re.fullmatch(place) for source, place, *_rest in rows if source == "google")


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
    assert sum(source == "google" for source, *_rest in rows) == 328
    assert sum(source == "partner" for source, *_rest in rows) == 59


def test_entity_node_contract():
    src = _nb("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb")
    assert 'trg_tbl="slv_poi_entity_non_enrich"' in src
    for role in (
        '"poi": "slv_3p_poi"',
        '"address": "slv_3p_poi_address"',
        '"contact": "slv_3p_poi_contact"',
        '"dict": "ref_dictionary_place_type"',
        '"svc": "slv_pn_business_services"',
        '"i18n": "slv_pn_business_service_i18ns"',
        '"hours": "slv_3p_poi_opening_hours"',
    ):
        assert role in src
    assert "HOURS_COLS" in src
    assert 'pk=("poi_id",)' in src
    assert 'write_mode="MERGE"' in src
    assert 'required_inputs=("poi", "address", "contact", "dict", "svc", "i18n")' in src
    build = _nb_cell("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb", "b1entitybuild")
    for name in ("website_url_of", "top_level_text", '"_web.value"', "*ESTIMATE_COLS", '"slv_3p_poi_contact: "'):
        assert name in src
    for name in ("_crawled_at", "_event_id", "_first_seen_at", "_last_seen_at"):
        assert name not in build
    assert 'get_json_object("website_urls"' not in src
    assert 'uuid_md5(F.col("id"), F.lit(PARTNER))' in src
    assert '"operation_status"' in src
    assert '== "vi"' in src
    partner = next(item for item in ast.parse(build).body if isinstance(item, ast.FunctionDef) and item.name == "_partner")
    vi = next(
        node for node in partner.body
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "vi" for target in node.targets)
    )
    vi_text = ast.get_source_segment(build, vi)
    assert vi_text and vi_text.startswith("vi = (")
    assert "$.policies.operating_hours" in vi_text
    assert "opening_hours_other_source" in build
    assert "partner_opening_hours_null" in build
    assert "subcategory_tags_json" not in src
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
    edges = src[src.index("# BEGIN_EDGE_PRECHECK"):src.index("with_retry(_write_edges")]
    merge_at = edges.index("MERGE INTO")
    pre = edges[:merge_at]
    match_on = edges[edges.index("ON t.pl_name"):edges.index("WHEN MATCHED")]
    assert "t.src_schema = s.src_schema" in match_on and "t.trg_schema = s.trg_schema" in match_on
    for token in (
        "cạnh active không đúng",
        "còn cạnh active ngoài cạnh chuẩn",
        "slv_poi_entity: còn",
        "slv_poi_amenity: còn cạnh active slv_poi_entity",
        "src_schema = 'lh_vv_silver.dbo'",
        "trg_schema = 'lh_vv_silver.dbo'",
    ):
        assert token in pre
    assert "'slv_poi_amenity'" in edges and "'slv_3p_poi_amenity'" in edges
    assert "<=>" in edges
    assert "src_schema = 'lh_vv_silver.dbo'" in edges
    assert "trg_schema = 'lh_vv_silver.dbo'" in edges
    assert "PL_VV_TRANS_SLV_TO_ENR_15M" in edges
    assert "RECOMPUTE" in edges
    assert "WHEN MATCHED" in edges
    assert "WHEN NOT MATCHED" in edges
    assert "NOT EXISTS" in edges
    assert "pl_name <> 'PL_VV_TRANS_SLV_TO_ENR_15M'" in edges
    assert "is_active = 1" in edges
    assert "priority = 1" in edges
    assert "'slv_3p_poi'" in edges
    assert "'ref_dictionary_place_type'" in edges
    assert "cạnh active không đúng" in edges
    assert "category_group" in ddl
    for name, dtype in (
        ("range_low_min", "INT"),
        ("range_high_min", "INT"),
        ("avg_range_min", "INT"),
        ("candidate_best_time_code", "STRING"),
        ("canonical_candidate", "STRING"),
    ):
        assert name in ddl and dtype in ddl
    assert "unseeded_rows" in src
    assert "dòng thiếu cột/giá trị 1.8–1.9" in src
    for name in (
        "slv_3p_poi", "slv_3p_poi_address", "slv_3p_poi_contact", "ref_dictionary_place_type",
        "slv_pn_business_services", "slv_pn_business_service_i18ns",
    ):
        assert f"'{name}'" in edges
    assert "'RETIRE'" in edges
    assert "is_active = 0" in edges
    assert "acquire_flow_lock" in src
    assert "finally:" in src[src.index("acquire_flow_lock"):src.index("release_flow_lock")]
    assert "PL_VV_TRANS_SLV_TO_SLV_1H" not in src
    assert "pl_name IS NULL" in src


def _edge_precheck(notebook: str):
    text = _nb(notebook)
    start = text.index("# BEGIN_EDGE_PRECHECK")
    end = text.index("# END_EDGE_PRECHECK")
    ns: dict = {}
    exec(text[start:end], ns)  # noqa: S102
    return ns["setup_edge_issues"]


def _edge(src_tbl, trg_tbl, **overrides):
    row = {
        "pl_name": "PL_VV_TRANS_SLV_TO_ENR_15M",
        "src_schema": "lh_vv_silver.dbo",
        "src_tbl": src_tbl,
        "trg_schema": "lh_vv_silver.dbo",
        "trg_tbl": trg_tbl,
        "is_active": 1,
    }
    row.update(overrides)
    return row


_ENTITY_UPSERTS = {
    ("slv_3p_poi", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_address", "slv_poi_entity_non_enrich"),
    ("ref_dictionary_place_type", "slv_poi_entity_non_enrich"),
    ("slv_pn_business_services", "slv_poi_entity_non_enrich"),
    ("slv_pn_business_service_i18ns", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_contact", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_amenity", "slv_poi_amenity"),
    ("slv_poi_entity_non_enrich", "slv_poi_amenity"),
    ("ref_dictionary_amenities", "slv_poi_amenity"),
}
_ENTITY_RETIRES = {
    ("slv_3p_poi", "slv_poi_entity"),
    ("ref_dictionary_place_type", "slv_poi_entity"),
    ("slv_poi_entity", "slv_poi_amenity"),
}
_AMENITY_UPSERTS = {
    ("slv_3p_poi_amenity", "slv_poi_amenity"),
    ("slv_poi_entity_non_enrich", "slv_poi_amenity"),
    ("ref_dictionary_amenities", "slv_poi_amenity"),
}
_AMENITY_RETIRES = {("slv_poi_entity", "slv_poi_amenity")}


def test_edge_precheck_blocks_are_identical():
    entity = _nb("NB_SETUP_POI_ENTITY.ipynb")
    amenity = _nb("NB_SETUP_POI_AMENITY.ipynb")
    def block(text):
        return text[text.index("# BEGIN_EDGE_PRECHECK"):text.index("# END_EDGE_PRECHECK")]
    assert block(entity) == block(amenity)


def test_legacy_retire_and_foreign_schema_do_not_block():
    check = _edge_precheck("NB_SETUP_POI_ENTITY.ipynb")
    legacy = [_edge("slv_poi_entity", "slv_poi_amenity")]
    assert check(legacy, _ENTITY_UPSERTS, _ENTITY_RETIRES) == []
    assert check(legacy, _AMENITY_UPSERTS, _AMENITY_RETIRES) == []
    other_owner = [_edge("slv_poi_entity", "slv_poi_amenity", pl_name="OTHER")]
    blocked = check(other_owner, _ENTITY_UPSERTS, _ENTITY_RETIRES)
    assert any("còn cạnh active ngoài cạnh chuẩn" in item for item in blocked)
    wrong_schema = [_edge("slv_poi_entity", "slv_poi_amenity", src_schema="other.dbo")]
    assert check(wrong_schema, _ENTITY_UPSERTS, _ENTITY_RETIRES) == []
    foreign = [_edge(
        "slv_3p_poi", "slv_poi_entity", src_schema="other.dbo", trg_schema="other.dbo",
    )]
    assert check(foreign, _ENTITY_UPSERTS, _ENTITY_RETIRES) == []
    unexpected = [_edge("other_src", "slv_poi_entity")]
    stale = check(unexpected, _ENTITY_UPSERTS, _ENTITY_RETIRES)
    assert any(item.startswith("slv_poi_entity: còn") for item in stale)


def _assign(source: str, name: str):
    tree = ast.parse(source)
    for node in tree.body:
        targets = node.targets if isinstance(node, ast.Assign) else []
        if any(isinstance(target, ast.Name) and target.id == name for target in targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _partner_json():
    text = _nb("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb")
    start = text.index("# BEGIN_PARTNER_JSON")
    end = text.index("# END_PARTNER_JSON")
    ns: dict = {}
    exec(text[start:end], ns)  # noqa: S102
    return ns["first_child_value"], ns


def test_partner_json_first():
    first, ns = _partner_json()
    assert first('{"facilities": {"classification": {"main_category": ["Hotel"]}}}', "main_category") == ("Hotel", "OK")
    assert first('{"main_category": ["", "Hostel"]}', "main_category") == ("Hostel", "OK")
    assert first('{"x": {"main_category": "A"}, "main_category": "B"}', "main_category") == ("A", "OK")
    assert first('{"main_category": "", "x": {"main_category": "Later"}}', "main_category") == ("Later", "OK")
    assert first("null", "main_category") == (None, ns["JSON_NULL"])
    assert first(None, "main_category") == (None, ns["JSON_NULL"])
    assert first("{", "main_category") == (None, ns["JSON_INVALID"])
    assert first('{"other": "Hotel"}', "main_category") == (None, ns["JSON_NO_VALUE"])


def test_partner_json_depth():
    first, ns = _partner_json()
    limit = ns["MAX_JSON_DEPTH"]
    ok = '{"k":' * (limit - 1) + '{"main_category": "Hotel"}' + "}" * (limit - 1)
    assert first(ok, "main_category") == ("Hotel", "OK")
    too_deep = '{"k":' * limit + '{"main_category": "Hotel"}' + "}" * limit
    assert first(too_deep, "main_category") == (None, ns["JSON_INVALID"])
    bomb = "[" * 3000 + "]" * 3000
    assert first(bomb, "main_category") == (None, ns["JSON_INVALID"])


CATEGORY_GROUPS = (
    ("Lodging", ("lodging", "hotel", "resort_hotel", "motel", "guest_house", "hostel", "bed_and_breakfast", "resort")),
    ("Main Meals", ("restaurant", "food", "meal_takeaway", "seafood_restaurant", "bistro")),
    ("Light Snacks / Cafe", ("cafe", "bakery", "coffee_shop", "tea_house")),
    ("Heavy Entertainment", ("amusement_park", "theme_park", "water_park", "zoo", "aquarium", "national_park", "hiking_area")),
    ("Light Sightseeing / Culture & Nature", ("tourist_attraction", "museum", "place_of_worship", "beach", "park", "historical_landmark", "pagoda", "church")),
    ("Shopping & Nightlife", ("shopping_mall", "market", "night_market", "bar", "night_club", "souvenir_store")),
)


def _md_tables(md, heading):
    body = md.split(heading, 1)[1]
    stop = re.search(r"^#{1,3} ", body, re.M)
    body = body[:stop.start()] if stop else body
    tables = []
    current = None
    for line in body.splitlines():
        if not line.lstrip().startswith("|"):
            if current:
                tables.append(current)
                current = None
            continue
        cells = [_cell(part) for part in line.strip().strip("|").split("|")]
        if all(part is None or set(part) <= {"-"} for part in cells):
            continue
        if current is None:
            current = []
        current.append(cells)
    if current:
        tables.append(current)
    return tables


def _snake(token):
    if " " in token and all(ord(ch) < 128 for ch in token):
        return token.replace(" ", "_")
    return token


def _ints(text):
    return int(text.replace(",", "").replace(".", ""))


def _range_pair(text):
    low, high = re.split(r"[–-]", text)
    return _ints(low), _ints(high)


def section_1_8_lookup(md):
    table = _md_tables(md, "# **1.8. Category Group**")[0]
    lookup = {}
    groups = []
    for cells in table[1:]:
        group, raw = cells[0], cells[1]
        tokens = tuple(re.findall(r"[a-z0-9_]+", raw))
        groups.append((group, tokens))
        for token in tokens:
            lookup[token] = group
    return groups, lookup


def _partner_row_groups(md, lookup):
    found = {}
    sector, cols = None, None
    for line in md.splitlines():
        match = SECTION_RE.match(line)
        if match:
            sector, cols = SECTOR.get(match.group(1)), None
            continue
        if sector is None or not line.lstrip().startswith("|"):
            continue
        cells = [_cell(part) for part in line.strip().strip("|").split("|")]
        if all(part is None or set(part) <= {"-"} for part in cells):
            continue
        if any(part and "Google Place API" in part for part in cells):
            cols = {role: i for i, part in enumerate(cells) for key, role in ROLES if part and key in part}
            continue
        if cols is None:
            continue
        partner = cells[cols["partner"]] if "partner" in cols else None
        google = cells[cols["google"]] if "google" in cols else None
        if not partner or partner in SKIP:
            continue
        groups = found.setdefault(partner, set())
        if google and google not in SKIP:
            for token in (part.strip() for part in google.split(",")):
                if token:
                    group = lookup.get(token, "Other")
                    if group != "Other":
                        groups.add(group)
    assert all(len(groups) < 2 for groups in found.values())
    return {partner: next(iter(groups)) if len(groups) == 1 else "Other" for partner, groups in found.items()}


def _estimate_oracle(md):
    tables = _md_tables(md, "## 1.9.1")
    group_range = {}
    for cells in tables[0][1:]:
        low, high = _range_pair(cells[1])
        group_range[cells[0]] = (low, high, _ints(cells[2]))
    special = {}
    for cells in tables[1][1:]:
        low, high = _range_pair(cells[1])
        values = (low, high, _ints(cells[2]))
        for token in (part.strip() for part in cells[0].split(",")):
            special[_snake(token)] = values
    best = {}
    for cells in _md_tables(md, "## 1.9.2")[0][1:]:
        priority, raw, code = cells
        if priority in {"10", "Default"}:
            continue
        text = raw.replace("Exact type là ", "").replace("hoặc có ", "").replace("Có ", "")
        for part in re.split(r"[,;]", text):
            token = _snake(part.strip())
            if token:
                best.setdefault(token, code)
    canon = {}
    for cells in _md_tables(md, "Giá trị ước tính theo")[0][1:]:
        for code in (part.strip() for part in cells[0].split(",")):
            canon[code] = cells[1]
    return group_range, special, best, canon


def test_category_group_from_section_1_8():
    md = MAPPING.read_text(encoding="utf-8")
    groups, lookup = section_1_8_lookup(md)
    assert groups == list(CATEGORY_GROUPS)
    rows = _seed_ns()["SEED_ROWS"]
    for row in rows:
        if row[0] != "google":
            continue
        assert row[5] == lookup.get(row[1], "Other")
    assert lookup["pagoda"] == "Light Sightseeing / Culture & Nature"
    assert lookup["night_market"] == "Shopping & Nightlife"
    assert lookup["theme_park"] == "Heavy Entertainment"


def test_partner_category_group_from_mapping_row():
    md = MAPPING.read_text(encoding="utf-8")
    _groups, lookup = section_1_8_lookup(md)
    expected = _partner_row_groups(md, lookup)
    assert expected["Hotel"] == "Lodging"
    assert expected["Homestay"] == "Lodging"
    assert expected["Café"] == "Light Snacks / Cafe"
    assert expected["Vietnamese"] == "Other"
    assert expected["Car with Driver"] == "Other"
    rows = _seed_ns()["SEED_ROWS"]
    seeded = {place: group for source, place, _sector, _cat, _vi, group, *_rest in rows if source == "partner"}
    assert seeded == expected
    partner_table = _md_tables(md, "# **1.8. Category Group**")[1]
    documented = [(cells[0], cells[1]) for cells in partner_table[1:]]
    seed_order = [(place, group) for source, place, _s, _c, _v, group, *_r in rows if source == "partner"]
    assert documented == seed_order


def test_partner_group_matches_node_rule():
    rows = _seed_ns()["SEED_ROWS"]
    step1, named = {}, {}
    for _source, place, _sector, category, _vi, _group, *_rest in rows:
        step1.setdefault(place, set()).add(category)
    for source, _place, _sector, category, _vi, group, *_rest in rows:
        if source == "google" and group != "Other":
            named.setdefault(category, set()).add(group)
    assert all(len(values) == 1 for values in step1.values())

    def resolved(place):
        category = next(iter(step1[place]))
        groups = named.get(category, set())
        return next(iter(groups)) if len(groups) == 1 else "Other"

    for source, place, _sector, _cat, _vi, group, *_rest in rows:
        if source == "partner":
            assert group == resolved(place)


def test_estimates_from_section_1_9():
    group_range, special, best, canon = _estimate_oracle(MAPPING.read_text(encoding="utf-8"))
    for row in _seed_ns()["SEED_ROWS"]:
        _source, place, _sector, _cat, _vi, group, low, high, avg, code, canonical = row
        assert (low, high, avg) == special.get(place, group_range[group])
        expect = best.get(place, "all")
        assert (code, canonical) == (expect, canon[expect])


def test_estimate_spot_values():
    rows = {(row[0], row[1]): row for row in _seed_ns()["SEED_ROWS"]}
    assert rows[("google", "beach")][5:] == (
        "Light Sightseeing / Culture & Nature", 120, 240, 180, "beach_coast", "Month 12–4",
    )
    assert rows[("google", "market")][5:] == (
        "Shopping & Nightlife", 90, 150, 120, "shopping_nightlife", "all_year",
    )
    assert rows[("google", "national_park")][5:] == (
        "Heavy Entertainment", 180, 360, 270, "forest_hiking", "Month 11–3",
    )
    assert rows[("google", "water_park")][5:] == (
        "Heavy Entertainment", 180, 360, 270, "outdoor_entertainment", "Month 11–4",
    )
    assert rows[("google", "suối")][5:] == ("Other", 60, 90, 75, "waterfall_green_season", "Month 6–10")
    assert rows[("google", "cable_car")][5:] == ("Other", 180, 360, 270, "all", "all_year")
    assert rows[("google", "ferry_terminal")][5:] == ("Other", 60, 90, 75, "all", "all_year")
    assert rows[("google", "hindu_temple")][5:] == ("Other", 60, 90, 75, "all", "all_year")
    assert rows[("google", "hotel")][5:] == ("Lodging", 1200, 1200, 1200, "all", "all_year")
    assert rows[("partner", "Café")][5:] == ("Light Snacks / Cafe", 45, 60, 60, "all", "all_year")


def test_validate_seed_rejects_bad_rows():
    ns = _seed_ns()
    good = ns["SEED_ROWS"][0]
    cases = [
        good[:5] + ("Not a group",) + good[6:],
        good[:6] + (90, 60, 75) + good[9:],
        good[:9] + ("all", "Month 12–5"),
        good[:10],
        good[:6] + (None, good[7], good[8]) + good[9:],
    ]
    for bad in cases:
        try:
            ns["validate_seed"]([bad])
        except ValueError:
            continue
        raise AssertionError(bad)


def test_no_category_group_function():
    for name in ("NB_SETUP_POI_ENTITY.ipynb", "NB_SETUP_INITIAL_DDL.ipynb"):
        src = _nb(name)
        assert "def category_group" not in src
        assert "with_category_group" not in src


def test_section_1_9_preserved():
    md = MAPPING.read_text(encoding="utf-8")
    for heading in (
        "# **1.9. Category Group Estimation**",
        "## 1.9.1 Để tính candidate_time_to_spend_minutes",
        "## 1.9.2 Để tính candidate_best_time_code và candidate_best_time",
        "## 1.9.3 deterministic_cost_vnd",
    ):
        assert heading in md
    assert "deterministic_cost_vnd = ROUND((price_min + price_max) / 2)" in md


def test_create_ddl_patch():
    nb = json.loads((ROOT / "notebooks" / "NB_CREATE_DDL.ipynb").read_text(encoding="utf-8"))
    ids = [cell.get("id") for cell in nb["cells"]]
    assert ids[-20:-14] == ["enrinfomd", "enrinfopy", "mvpoimd", "mvpoipy", "enrflagmd", "enrflagpy"]
    assert ids[-14:-12] == ["ohpassmd", "ohpasspy"]
    assert ids[-12:-10] == ["peholmd", "peholpy"]
    assert ids[-10:-8] == ["srvpoimd", "srvpoipy"]
    assert ids[-8:-6] == ["srvratemd", "srvratepy"]
    assert ids[-6:-2] == ["mediaddlmd", "mediaddlpy", "amenddlmd", "amenddlpy"]
    assert ids[-2:] == ["plcadmd", "plcadpy"]
    assert ids[ids.index("entwebpy") - 1] == "entwebmd"
    assert ids.index("entwebpy") < ids.index("enrinfomd")


def test_entity_detail_columns():
    build = _nb_cell("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb", "b1entitybuild")
    tree = ast.parse(build)
    google_node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_google")
    partner_node = next(item for item in tree.body if isinstance(item, ast.FunctionDef) and item.name == "_partner")
    google = ast.get_source_segment(build, google_node)
    partner = ast.get_source_segment(build, partner_node)
    assert google and partner
    assert '.select("poi_id", *CONTACT_COLS, "phone")' in google
    assert 'F.lit(None).cast("string").alias("email")' in google
    assert 'F.lit(None).cast("string").alias("holiday_exceptions")' in google
    assert "dup_contact" in google  # D-PEH-08: biến của QG, không phải string literal
    assert "$.policies.holiday_exceptions" not in google
    vi = next(
        node for node in partner_node.body
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "vi" for t in node.targets)
    )
    vi_text = ast.get_source_segment(build, vi)
    assert vi_text and vi_text.startswith("vi = (")
    assert "$.policies.operating_hours" in vi_text
    assert '$.policies.holiday_exceptions").alias("_holiday")' in vi_text
    assert '"phone": F.col("phone")' in partner
    assert '"email": F.col("email")' in partner
    assert '"holiday_exceptions": F.col("_holiday")' in partner
    assert partner.count('F.col("_holiday")') == 1
    assert "+ HOURS_COLS + DETAIL_COLS" in build
    assert "phone_email_holiday_other_source" in build
    assert "opening_hours_other_source" in build
    assert "partner_opening_hours_null" in build


def test_entity_detail_patch_cell():
    nb = json.loads((ROOT / "notebooks" / "NB_CREATE_DDL.ipynb").read_text(encoding="utf-8"))
    markdown = "".join(next(cell["source"] for cell in nb["cells"] if cell.get("id") == "peholmd"))
    title = "# [THÊM 23/10] 20261023-entity-phone-email-holiday"
    assert markdown.strip() == title
    raw = _nb_cell("NB_CREATE_DDL.ipynb", "peholpy")
    assert raw.startswith(title)
    code = "\n".join(line for line in raw.splitlines() if not line.strip().startswith("#"))
    for token in (
        "DROP", "DELETE", "TRUNCATE", "REPLACE", "RESTORE", "columnMapping",
        " AFTER ", "ALTER COLUMN", "ctrl_mng", "MERGE", "UPDATE", "INSERT",
        "CREATE TABLE", "lock_exec_id",
    ):
        assert token not in code
    entity = _nb_cell("NB_SLV_POI_ENTITY_NON_ENRICH.ipynb", "b1entitybuild")
    assert _assign(raw, "NEW_COLS") == tuple((name, "STRING") for name in _assign(entity, "DETAIL_COLS"))
    assert _assign(raw, "ANCHOR") == _assign(entity, "HOURS_COLS")[-1]
    assert raw.count("ALTER TABLE") == 1
    stop, alter, after = (raw.index(token) for token in ("Dừng trước khi ghi", "ALTER TABLE", "Sau khi ghi"))
    assert stop < alter < after
    from test_initial_ddl_contract import _specs

    specs, _namespace = _specs()
    spec = next(item for item in specs if item["fq"] == "lh_vv_silver.dbo.slv_poi_entity_non_enrich")
    names = [name for name, _dtype, _comment in spec["cols"]]
    at = names.index("opening_hours_text")
    assert [name for name, _dtype in _assign(raw, "NEW_COLS")] == names[at + 1:at + 4]
    assert any(cell.get("id") == "nonenrpy" for cell in nb["cells"])
    patch = _nb_cell("NB_CREATE_DDL.ipynb", "dictseedpy")
    assert "ADD COLUMNS" in patch and "missing" in patch
    assert "UPDATE" not in patch and "CATEGORY_GROUPS" not in patch
    entity = _nb("NB_SETUP_POI_ENTITY.ipynb")
    start = entity.index("EXPECTED = ")
    expected = _assign(entity[start:entity.index("\ndescribed", start)], "EXPECTED")
    assert _assign(patch, "NEW_COLS") == tuple((name, dtype.upper()) for name, dtype, _null in expected[-5:])


def test_partner_website_top_level():
    _first, ns = _partner_json()
    top = ns["top_level_text"]
    assert top('{"website_url": "https://a.example/"}', "website_url") == ("https://a.example/", "OK")
    assert top('{"website_url": ""}', "website_url") == ("", "OK")
    assert top('{"website_url": " x "}', "website_url") == (" x ", "OK")
    for text in (
        '{"website_url": 1}',
        '{"website_url": true}',
        '{"website_url": {"a": 1}}',
        '{"website_url": ["u"]}',
    ):
        assert top(text, "website_url") == (None, "NOT_STRING")
    assert top('{"website_url": null}', "website_url") == (None, "NO_VALUE")
    assert top('{"x": {"website_url": "u"}}', "website_url") == (None, "NO_VALUE")
    assert top('["u"]', "website_url") == (None, "NO_VALUE")
    assert top(None, "website_url") == (None, "NULL_JSON")
    assert top("null", "website_url") == (None, "NULL_JSON")
    assert top("{", "website_url") == (None, "INVALID_JSON")
    assert top("[" * 3000 + "]" * 3000, "website_url") == (None, "INVALID_JSON")


def test_create_ddl_contact_edge_patch():
    src = _nb_cell("NB_CREATE_DDL.ipynb", "entwebpy")
    for token in ("INSERT INTO", "WHERE NOT EXISTS", "'slv_3p_poi_contact'", "wm_flow__", "RECOMPUTE"):
        assert token in src
    for token in ("DROP ", "DELETE FROM", "ALTER TABLE"):
        assert token not in src
    assert src.count("UPDATE ") == 2
    parts = src.split("UPDATE {WM}")
    assert len(parts) == 3
    acquire_where = parts[1].split("WHERE", 1)[1]
    assert "lock_exec_id = '{LOCK}'" not in acquire_where
    assert "lock_exec_id = '{LOCK}'" in parts[2]
    assert "lock_exec_id IS NULL" in parts[1]
    assert "INTERVAL {LEASE_MINUTES} MINUTES" in parts[1]
    assert 'owner["lock_exec_id"] != LOCK' in src
    assert "uuid.uuid4().hex" in src
    assert 'status = "FAILED" if failed else "SUCCESS"' in src
    assert "finally:" in src
    start = src.index("from datetime import timedelta")
    end = src.index('LOCK = "entweb-"')
    ns: dict = {}
    exec(src[start:end], ns)  # noqa: S102
    now = datetime(2026, 10, 20, 16, 0, 0)
    free = ns["lock_is_free"]
    assert free(None, None, now)
    assert free("stale", None, now)
    assert not free("live", now - timedelta(minutes=1), now)
    assert free("stale", now - timedelta(minutes=90), now)
    state = {"owner": None, "lock_at": None}
    assert free(state["owner"], state["lock_at"], now)
    state = {"owner": "A", "lock_at": now}
    assert state["owner"] != "B"
    assert not free(state["owner"], state["lock_at"], now)
    state = {"owner": "old", "lock_at": now - timedelta(minutes=91)}
    assert free(state["owner"], state["lock_at"], now)
    state = {"owner": "new", "lock_at": now}
    assert state["owner"] != "old"
