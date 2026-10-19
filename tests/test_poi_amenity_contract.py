"""Contract checks for ref_dictionary_amenities and slv_poi_amenity. No Spark."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MAPPING = ROOT / "docs" / "context" / "3p-google" / "mapping_amenities.md"
SECTOR = {"1": "accommodation", "2": "f_n_b", "3": "attraction", "4": "shopping_n_retail"}
SKIP = {"Bổ sung sau", "Fallback", "Không có field", "Không có field riêng"}
SECTION_RE = re.compile(r"^####\s+\*\*2\.(\d)")
FLAG_KEYS = (
    "servesBreakfast", "servesBrunch", "servesLunch", "servesDinner", "servesBeer", "servesWine",
    "servesCocktails", "servesDessert", "servesCoffee", "servesVegetarianFood", "allowsDogs",
    "goodForChildren", "goodForGroups", "goodForWatchingSports", "liveMusic", "menuForChildren",
    "outdoorSeating", "restroom", "reservable", "takeout", "delivery", "dineIn", "curbsidePickup",
)
OBJECT_KEYS = ("parkingOptions", "paymentOptions", "accessibilityOptions", "evChargeOptions", "fuelOptions")
FLAG_MATCH = {
    ("accommodation", "general_amenities", "parkingOptions.freeStreetParking"),
    ("accommodation", "general_amenities", "parkingOptions.valetParking"),
    ("accommodation", "general_amenities", "parkingOptions.freeGarageParking"),
    ("accommodation", "general_amenities", "parkingOptions.paidGarageParking"),
    ("accommodation", "general_amenities", "outdoorSeating"),
    ("accommodation", "general_amenities", "restroom"),
    ("accommodation", "general_amenities", "goodForChildren"),
    ("accommodation", "general_amenities", "goodForGroups"),
    ("accommodation", "general_amenities", "liveMusic"),
    ("accommodation", "general_amenities", "parkingOptions.freeParkingLot"),
    ("accommodation", "general_amenities", "parkingOptions.paidParkingLot"),
    ("accommodation", "general_amenities", "servesCocktails"),
    ("accommodation", "general_amenities", "parkingOptions.freeElectricVehicleParking"),
    ("accommodation", "general_amenities", "parkingOptions.paidElectricVehicleParking"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleSeating"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleElevator"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleEntrance"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleRestroom"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleParking"),
    ("f_n_b", "space_and_services", "restroom"),
    ("f_n_b", "space_and_services", "goodForChildren"),
    ("f_n_b", "space_and_services", "accessibilityOptions.wheelchairAccessibleEntrance"),
    ("f_n_b", "space_and_services", "goodForWatchingSports"),
    ("f_n_b", "space_and_services", "liveMusic"),
    ("f_n_b", "space_and_services", "dineIn"),
    ("attraction", "facilities_and_services", "parkingOptions.freeParkingLot"),
    ("attraction", "facilities_and_services", "parkingOptions.paidParkingLot"),
}
TYPE_MATCH = {
    ("accommodation", "general_amenities", "swimming_pool"),
    ("accommodation", "general_amenities", "hot_spring"),
    ("accommodation", "general_amenities", "sauna"),
    ("accommodation", "general_amenities", "garden"),
    ("accommodation", "general_amenities", "botanical_garden"),
    ("accommodation", "general_amenities", "meeting_rooms"),
    ("f_n_b", "specialty_tags", "food_stand"),
    ("f_n_b", "specialty_tags", "street_food_gathering"),
    ("f_n_b", "specialty_tags", "seafood_restaurant"),
    ("f_n_b", "specialty_tags", "oyster_bar_restaurant"),
    ("f_n_b", "specialty_tags", "steakhouse"),
    ("f_n_b", "specialty_tags", "bakery"),
    ("f_n_b", "specialty_tags", "pastry_shop"),
    ("f_n_b", "specialty_tags", "cake_shop"),
}


def clean(text):
    text = text.replace("**", "").replace("`", "")
    text = text.replace("\\[", "[").replace("\\]", "]")
    text = text.replace("\xa0", " ")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s*=\s*", " = ", text)
    text = text.strip()
    return text or None


def parse_mapping(md):
    rows, sector, group, cols = [], None, None, None
    for line in md.splitlines():
        match = SECTION_RE.match(line)
        if match:
            sector, group, cols = SECTOR[match.group(1)], None, None
            continue
        if not line.lstrip().startswith("|"):
            continue
        raw = [cell.strip() for cell in line.strip().strip("|").split("|")]
        cells = [clean(cell) for cell in raw]
        if all(cell is None or set(cell) <= {"-"} for cell in cells):
            continue
        if any(cell and "Google Place API" in cell for cell in cells):
            cols = {}
            for index, cell in enumerate(cells):
                if not cell:
                    continue
                if "Partner Portal Enum" in cell:
                    cols["partner"] = index
                elif "Google Place API" in cell:
                    cols["google"] = index
                elif "(VI)" in cell:
                    cols["vi"] = index
                elif "(EN)" in cell:
                    cols["en"] = index
            continue
        if raw and raw[0].startswith("**") and all(cell is None for cell in cells[1:]):
            group = clean(raw[0])
            continue
        if cols is None or group is None:
            continue
        partner = cells[cols["partner"]] if "partner" in cols and cols["partner"] < len(cells) else None
        google = cells[cols["google"]] if "google" in cols and cols["google"] < len(cells) else None
        en = cells[cols["en"]] if "en" in cols and cols["en"] < len(cells) else None
        vi = cells[cols["vi"]] if "vi" in cols and cols["vi"] < len(cells) else None
        if partner and partner not in SKIP:
            rows.append(("partner", sector, group, partner, en, vi))
        if google and google not in SKIP:
            for part in re.split(r"\s+hoặc\s+", google):
                part = part.strip().rstrip(",").strip()
                if part and part not in SKIP:
                    rows.append(("google", sector, group, part, en, vi))
    return rows


def _expand(rows, keys):
    out = []
    for source, sector, group, raw, en, vi in rows:
        for key in keys(raw):
            out.append((source, sector, group, key, en, vi))
    return out


def _google(rows):
    return [(sector, group, raw, en, vi) for source, sector, group, raw, en, vi in rows if source == "google"]


def _nb(name: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return "".join("".join(cell["source"]) for cell in nb["cells"])


def _between(text, start, end):
    start_at = text.index(start)
    return text[start_at:text.index(end, start_at)]


def _seed_ns():
    ns: dict = {}
    exec(_between(_nb("NB_SETUP_POI_AMENITY.ipynb"), "# BEGIN_AMENITY_SEED", "# END_AMENITY_SEED"), ns)  # noqa: S102
    return ns


def _match_ns():
    ns: dict = {"re": re}
    exec(_between(_nb("NB_SLV_POI_AMENITY.ipynb"), "# BEGIN_AMENITY_MATCH", "# END_AMENITY_MATCH"), ns)  # noqa: S102
    return ns


def test_seed_matches_mapping_file():
    ns = _seed_ns()
    rows = parse_mapping(MAPPING.read_text(encoding="utf-8"))
    assert ns["SEED_ROWS"] == _expand(rows, ns["amenity_keys"])
    ns["validate_seed"](ns["SEED_ROWS"])


def test_amenity_keys_cases():
    keys = _seed_ns()["amenity_keys"]
    assert keys("outdoorSeating = true") == ["outdoorSeating"]
    assert keys("parkingOptions.freeElectricVehicleParking = true") == ["parkingOptions.freeElectricVehicleParking"]
    assert keys("types[] = hot_spring, sauna") == ["hot_spring", "sauna"]
    assert keys("types[] = bakery, pastry_shop, cake_shop") == ["bakery", "pastry_shop", "cake_shop"]
    ns = _seed_ns()
    keys = ns["amenity_keys"]
    assert keys("types[] có art_gallery") == ["json_type = 'art_gallery'"]
    assert keys("types[] thuộc business_category = Bar & Pub/Nightlife") == [
        ns["AMENITY_JSON_TYPE"]["types[] thuộc business_category = Bar & Pub/Nightlife"]
    ]
    for raw in (
        "outdoorSeating = true = true",
        "serves_meals = true",
        "parkingOptions.freeParkingLot, parkingOptions.paidParkingLot = true",
        "cat_cafe, dog_cafe",
        "dim_sum_restaurant",
        "Hồ bơi",
    ):
        assert keys(raw) == [raw]
    for row in _seed_ns()["SEED_ROWS"]:
        assert keys(row[3]) == [row[3]]


def test_seed_census():
    ns = _seed_ns()
    rows = parse_mapping(MAPPING.read_text(encoding="utf-8"))
    flag = types = unchanged = type_keys = json_type = 0
    for source, _sector, _group, raw, _en, _vi in rows:
        got = ns["amenity_keys"](raw)
        if source == "partner":
            assert got == [raw]
        if ns["AMENITY_FLAG_RE"].fullmatch(raw):
            flag += 1
        elif ns["AMENITY_TYPES_RE"].fullmatch(raw):
            types += 1
            type_keys += len(got)
        elif raw in ns["AMENITY_JSON_TYPE"]:
            json_type += 1
            assert got == [ns["AMENITY_JSON_TYPE"][raw]]
        else:
            unchanged += 1
            assert got == [raw]
    assert (flag, types, type_keys, json_type, unchanged) == (27, 8, 14, 12, 105)


def test_seed_counts():
    rows = _seed_ns()["SEED_ROWS"]
    assert len(rows) == 158
    assert sum(row[0] == "partner" for row in rows) == 74
    assert sum(row[0] == "google" for row in rows) == 84
    counts = {}
    for source, sector, *_rest in rows:
        counts[(sector, source)] = counts.get((sector, source), 0) + 1
    assert counts[("accommodation", "partner")] == 22
    assert counts[("accommodation", "google")] == 31
    assert counts[("f_n_b", "partner")] == 18
    assert counts[("f_n_b", "google")] == 34
    assert counts[("attraction", "partner")] == 22
    assert counts[("attraction", "google")] == 16
    assert counts[("shopping_n_retail", "partner")] == 12
    assert counts[("shopping_n_retail", "google")] == 3


def test_seed_split_rows_keep_columns():
    rows = _seed_ns()["SEED_ROWS"]
    sauna = [row for row in rows if row[3] in {"hot_spring", "sauna"}]
    assert sauna == [
        ("google", "accommodation", "general_amenities", "hot_spring", "Sauna", "Xông hơi"),
        ("google", "accommodation", "general_amenities", "sauna", "Sauna", "Xông hơi"),
    ]
    bakery = [row for row in rows if row[3] in {"bakery", "pastry_shop", "cake_shop"}]
    assert {(row[4], row[5]) for row in bakery} == {("Bakery", "Tiệm bánh")}
    assert [row[3] for row in bakery] == ["bakery", "pastry_shop", "cake_shop"]


def test_seed_excludes_placeholders():
    rows = _seed_ns()["SEED_ROWS"]
    assert all(value not in SKIP for row in rows for value in row)
    rooftop = [row for row in rows if row[3] == "Rooftop Bar" or row[4] == "Rooftop Bar"]
    assert rooftop == [("partner", "f_n_b", "specialty_tags", "Rooftop Bar", "Rooftop Bar", "Bar sân thượng")]
    street = [
        row for row in rows
        if row[0] == "google" and row[3] == "parkingOptions.freeStreetParking"
    ]
    assert street == [(
        "google", "accommodation", "general_amenities",
        "parkingOptions.freeStreetParking", "Free Street Parking", "Đỗ xe trên phố",
    )]


def test_seed_sectors_groups():
    rows = _seed_ns()["SEED_ROWS"]
    assert {row[1] for row in rows} == {"accommodation", "f_n_b", "attraction", "shopping_n_retail"}
    assert "accomodation" not in {row[1] for row in rows}
    assert "fnb" not in {row[1] for row in rows}
    attraction = [row[2] for row in rows if row[1] == "attraction"]
    assert attraction and set(attraction) == {"facilities_and_services"}


def test_seed_sectors_in_entity_vocabulary():
    entity = _between(_nb("NB_SETUP_POI_ENTITY.ipynb"), "SEED_SECTORS = ", ")")
    allowed = set(re.findall(r'"([^"]+)"', entity))
    assert {row[1] for row in _seed_ns()["SEED_ROWS"]} <= allowed


def test_seed_raw_unique_within_group():
    ns = _seed_ns()
    rows = ns["SEED_ROWS"]
    counts = {}
    for row in rows:
        counts[row[:4]] = counts.get(row[:4], 0) + 1
    dups = {key for key, n in counts.items() if n > 1}
    assert dups == set(ns["AMENITY_SHARED_RAW"])
    assert counts[ns["AMENITY_SHARED_RAW"][0]] == 2
    extra = rows + [("google", "accommodation", "general_amenities", "sauna", "Steam", "Hơi")]
    try:
        ns["validate_seed"](extra)
    except ValueError:
        pass
    else:
        raise AssertionError("duplicate sauna key was accepted")
    legacy = rows + [("google", "accommodation", "general_amenities", "outdoorSeating = true", "Outdoor Seating", "x")]
    try:
        ns["validate_seed"](legacy)
    except ValueError:
        pass
    else:
        raise AssertionError("legacy amenity_raw was accepted")


def test_hoac_split_same_amenity():
    rows = _seed_ns()["SEED_ROWS"]
    parking = [row for row in rows if row[0] == "google" and row[1] == "accommodation" and row[4] == "Parking"]
    ev = [row for row in rows if row[0] == "google" and row[4] == "EV Charging Station"]
    assert len(parking) == 2
    assert len(ev) == 3
    assert len({(row[4], row[5]) for row in parking}) == 1
    assert len({(row[4], row[5]) for row in ev}) == 1


def test_resolve_condition_cases():
    resolve = _match_ns()["resolve_condition"]
    assert resolve("accommodation", "general_amenities", "outdoorSeating") == (
        "flag", "flags.outdoorSeating", "true",
    )
    assert resolve("accommodation", "general_amenities", "parkingOptions.freeStreetParking") == (
        "flag", "parkingOptions.freeStreetParking", "true",
    )
    assert resolve("f_n_b", "specialty_tags", "bakery") == ("type", "types[]", "bakery")
    assert resolve("attraction", "facilities_and_services", "json_type = 'art_gallery'") == (
        "type", "types[]", "art_gallery",
    )
    history = resolve(
        "attraction", "facilities_and_services",
        _seed_ns()["AMENITY_JSON_TYPE"]["types[] có enum thuộc business_category = Historical Site"],
    )
    assert history[0] == "json_in" and history[1] == "types[]"
    assert history[2].split(",")[0] == "historical_landmark"
    for args in (
        ("attraction", "facilities_and_services", "restroom"),
        ("attraction", "facilities_and_services", "goodForChildren"),
        ("attraction", "facilities_and_services", "accessibilityOptions.wheelchairAccessibleEntrance"),
        ("shopping_n_retail", "facilities_and_services", "delivery"),
        ("f_n_b", "specialty_tags", "dim_sum_restaurant"),
        ("accommodation", "general_amenities", "outdoorSeating = true"),
        ("f_n_b", "space_and_services", "outdoorSeating = true = true"),
    ):
        assert resolve(*args) is None


def test_flag_keys_match_registry():
    text = _nb("NB_CREATE_DDL.ipynb")
    start = text.index('"source_flags_json"')
    block = text[start:text.index('"slv_3p_poi_review"', start)]
    flags = tuple(re.findall(r"'([^']+)'", re.search(r"'keys': \[([^\]]+)\]", block).group(1)))
    objects = tuple(re.findall(r"'key': '([^']+)'", block))
    ns = _match_ns()
    assert ns["FLAG_KEYS"] == flags == FLAG_KEYS
    assert ns["OBJECT_KEYS"] == objects == OBJECT_KEYS


def test_match_sets_pinned():
    seed = _seed_ns()
    match = _match_ns()
    md = parse_mapping(MAPPING.read_text(encoding="utf-8"))
    flag_from_md = set()
    type_from_md = set()
    for source, sector, group, raw, _en, _vi in md:
        if source != "google":
            continue
        if seed["AMENITY_FLAG_RE"].fullmatch(raw):
            flag_from_md.add((sector, group, seed["amenity_keys"](raw)[0]))
        elif seed["AMENITY_TYPES_RE"].fullmatch(raw):
            type_from_md.update((sector, group, key) for key in seed["amenity_keys"](raw))
    assert match["FLAG_MATCH"] == FLAG_MATCH == flag_from_md
    assert match["TYPE_MATCH"] == TYPE_MATCH == type_from_md
    assert (len(FLAG_MATCH), len(TYPE_MATCH)) == (27, 14)
    assert FLAG_MATCH.isdisjoint(TYPE_MATCH)
    shared = {key[1:] for key in seed["AMENITY_SHARED_RAW"]}
    assert shared.isdisjoint(FLAG_MATCH) and shared.isdisjoint(TYPE_MATCH)
    google_keys = {(sector, group, raw) for source, sector, group, raw, _en, _vi in seed["SEED_ROWS"] if source == "google"}
    assert FLAG_MATCH <= google_keys and TYPE_MATCH <= google_keys
    json_from_seed = {
        (sector, group, raw)
        for source, sector, group, raw, _en, _vi in seed["SEED_ROWS"]
        if source == "google" and raw.startswith("json_type ")
    }
    assert match["JSON_MATCH"] == json_from_seed
    assert len(json_from_seed) == 12
    for sector, group, raw in FLAG_MATCH:
        hit = match["resolve_condition"](sector, group, raw)
        assert hit is not None and hit[0] == "flag"


def test_legacy_form_consistent():
    seed = _seed_ns()
    match = _match_ns()
    for _source, _sector, _group, raw, _en, _vi in parse_mapping(MAPPING.read_text(encoding="utf-8")):
        changed = seed["amenity_keys"](raw) != [raw]
        if raw in seed["AMENITY_JSON_TYPE"]:
            assert changed and not match["is_legacy_form"](raw)
        else:
            assert match["is_legacy_form"](raw) == changed
    assert all(not match["is_legacy_form"](row[3]) for row in seed["SEED_ROWS"])


def test_match_conditions_states():
    seed = _seed_ns()
    match = _match_ns()
    md = parse_mapping(MAPPING.read_text(encoding="utf-8"))
    new_rows = _google(seed["SEED_ROWS"])
    old_rows = _google(md)
    conds, dup, legacy = match["match_conditions"](new_rows)
    assert len(conds) == 53
    assert sum(row[5] == "flag" for row in conds) == 27
    assert sum(row[5] == "json_in" for row in conds) == 8
    assert dup == [] and legacy == 0
    old_conds, _old_dup, _old_legacy = match["match_conditions"](old_rows)
    assert old_conds == []
    mixed, mixed_dup, mixed_legacy = match["match_conditions"](old_rows + new_rows)
    assert len(mixed) == 53 and mixed_dup == [] and mixed_legacy == 35
    assert match["legacy_blocks_write"](mixed_legacy)
    assert not match["legacy_blocks_write"](0)
    dup_rows = new_rows + [("accommodation", "general_amenities", "sauna", "Steam", "Hơi")]
    _conds, dup_keys, _legacy = match["match_conditions"](dup_rows)
    assert dup_keys == [("accommodation", "general_amenities", "sauna")]


def test_match_coverage_requires_full_allowlist():
    seed = _seed_ns()
    match = _match_ns()
    rows = _google(seed["SEED_ROWS"])
    conds, dup, _legacy = match["match_conditions"](rows)
    assert dup == []
    assert match["match_coverage"](conds) == ([], [])
    dropped = [row for row in rows if row[2] != "sauna"]
    partial, _dup, _legacy = match["match_conditions"](dropped)
    missing, extra = match["match_coverage"](partial)
    assert ("accommodation", "general_amenities", "sauna") in missing
    assert extra == []


def test_amenity_node_contract():
    src = _nb("NB_SLV_POI_AMENITY.ipynb")
    assert 'trg_tbl="slv_poi_amenity"' in src
    assert '"amenity": "slv_3p_poi_amenity"' in src
    assert '"entity": "slv_poi_entity_non_enrich"' in src
    assert '"dict": "ref_dictionary_amenities"' in src
    assert 'pk=("poi_id", "business_sector", "amenity_group", "amenity_raw")' in src
    assert 'write_mode="MERGE"' in src
    assert 'required_inputs=("amenity", "entity", "dict")' in src
    assert '"map<string,string>"' in src
    assert "F.broadcast(" in src
    assert "business_category" not in src
    assert "explode_outer" not in src
    assert "get_json_object" not in src
    assert "có POI join entity nhưng không khớp điều kiện nào" not in src
    assert "rows=n" in src
    assert '"array<string>"' in src
    assert "types_json" in src
    assert "dropDuplicates" in src
    assert "TYPES_PATH" in src
    assert "JSON_MATCH" in src
    assert "array_contains" in src
    assert "json_in" in src
    assert "dict_legacy_form=" in src
    assert "legacy_blocks_write" in src
    assert "conditions_type=" in src


def test_setup_contract():
    src = _nb("NB_SETUP_POI_AMENITY.ipynb")
    assert 'p_apply = "false"' in src
    for column in (
        "source_name", "business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_vi",
        "is_active", "updated_at", "poi_id", "row_hash", "created_at", "deleted_at",
    ):
        assert column in src
    ddl = src.split("CREATE TABLE IF NOT EXISTS lh_vv_silver.dbo.ref_dictionary_amenities", 1)[1]
    ddl = ddl.split("for fq, expected", 1)[0]
    assert "business_category" not in ddl
    merge = src.split("def _seed_merge", 1)[1].split("missing_before", 1)[0]
    assert "WHEN NOT MATCHED" in merge
    assert "WHEN MATCHED" not in merge
    assert "PL_VV_TRANS_SLV_TO_SLV_1H" in src
    assert "RECOMPUTE" in src
    for name in ("slv_3p_poi_amenity", "slv_poi_entity_non_enrich", "ref_dictionary_amenities"):
        assert name in src
    assert "slv_poi_amenity: chưa có cạnh slv_poi_entity_non_enrich, chạy NB_SETUP_POI_ENTITY trước" in src
    assert "entity_edges_ok != 5" in src
    assert "(0, 'lh_vv_silver.dbo', 'slv_poi_entity', 'lh_vv_silver.dbo', 'slv_poi_amenity', 'RETIRE')" in src
    edges = src[src.index("# BEGIN_EDGE_PRECHECK"):src.index("with_retry(_write_edges")]
    merge_at = edges.index("MERGE INTO")
    pre = edges[:merge_at]
    match_on = edges[edges.index("ON t.pl_name"):edges.index("WHEN MATCHED")]
    assert "t.src_schema = s.src_schema" in match_on and "t.trg_schema = s.trg_schema" in match_on
    for token in (
        "entity_edges_ok != 5",
        "còn cạnh active ngoài cạnh chuẩn",
        "slv_poi_amenity: còn cạnh active slv_poi_entity",
        "src_schema = 'lh_vv_silver.dbo'",
        "trg_schema = 'lh_vv_silver.dbo'",
    ):
        assert token in pre
    assert "stale_keys" in src
    assert '"stale": STALE' in src
