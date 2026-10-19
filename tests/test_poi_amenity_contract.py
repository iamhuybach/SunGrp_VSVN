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
COND_RE = re.compile(r"([A-Za-z][A-Za-z0-9]*)(?:\.([A-Za-z][A-Za-z0-9]*))? = (true|false)")
MATCHABLE = {
    ("accommodation", "general_amenities", "parkingOptions.freeStreetParking = true"),
    ("accommodation", "general_amenities", "parkingOptions.valetParking = true"),
    ("accommodation", "general_amenities", "parkingOptions.freeGarageParking = true"),
    ("accommodation", "general_amenities", "parkingOptions.paidGarageParking = true"),
    ("accommodation", "general_amenities", "outdoorSeating = true"),
    ("accommodation", "general_amenities", "restroom = true"),
    ("accommodation", "general_amenities", "goodForChildren = true"),
    ("accommodation", "general_amenities", "goodForGroups = true"),
    ("accommodation", "general_amenities", "liveMusic = true"),
    ("accommodation", "general_amenities", "parkingOptions.freeParkingLot = true"),
    ("accommodation", "general_amenities", "parkingOptions.paidParkingLot = true"),
    ("accommodation", "general_amenities", "servesCocktails = true"),
    ("accommodation", "general_amenities", "parkingOptions.freeElectricVehicleParking = true"),
    ("accommodation", "general_amenities", "parkingOptions.paidElectricVehicleParking = true"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleSeating = true"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleElevator = true"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleEntrance = true"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleRestroom = true"),
    ("accommodation", "accessibility", "accessibilityOptions.wheelchairAccessibleParking = true"),
    ("f_n_b", "space_and_services", "restroom = true"),
    ("f_n_b", "space_and_services", "goodForChildren = true"),
    ("f_n_b", "space_and_services", "accessibilityOptions.wheelchairAccessibleEntrance = true"),
    ("f_n_b", "space_and_services", "goodForWatchingSports = true"),
    ("f_n_b", "space_and_services", "liveMusic = true"),
    ("f_n_b", "space_and_services", "dineIn = true"),
    ("attraction", "facilities_and_services", "parkingOptions.freeParkingLot = true"),
    ("attraction", "facilities_and_services", "parkingOptions.paidParkingLot = true"),
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


def resolve_condition(raw):
    """Điều kiện -> (path, giá trị) hoặc None."""
    match = COND_RE.fullmatch((raw or "").strip())
    if match is None:
        return None
    head, leaf, value = match.groups()
    if leaf is None:
        return (f"flags.{head}", value) if head in FLAG_KEYS else None
    if head == "flags":
        return (f"flags.{leaf}", value) if leaf in FLAG_KEYS else None
    return (f"{head}.{leaf}", value) if head in OBJECT_KEYS else None


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
    assert ns["SEED_ROWS"] == rows
    ns["validate_seed"](rows)


def test_seed_counts():
    rows = _seed_ns()["SEED_ROWS"]
    assert sum(row[0] == "partner" for row in rows) == 74
    assert sum(row[0] == "google" for row in rows) == 78
    counts = {}
    for source, sector, *_rest in rows:
        counts[(sector, source)] = counts.get((sector, source), 0) + 1
    assert counts[("accommodation", "partner")] == 22
    assert counts[("accommodation", "google")] == 29
    assert counts[("f_n_b", "partner")] == 18
    assert counts[("f_n_b", "google")] == 30
    assert counts[("attraction", "partner")] == 22
    assert counts[("attraction", "google")] == 16
    assert counts[("shopping_n_retail", "partner")] == 12
    assert counts[("shopping_n_retail", "google")] == 3


def test_seed_excludes_placeholders():
    rows = _seed_ns()["SEED_ROWS"]
    assert all(value not in SKIP for row in rows for value in row)
    rooftop = [row for row in rows if row[3] == "Rooftop Bar" or row[4] == "Rooftop Bar"]
    assert rooftop == [("partner", "f_n_b", "specialty_tags", "Rooftop Bar", "Rooftop Bar", "Bar sân thượng")]
    street = [
        row for row in rows
        if row[0] == "google" and row[3] == "parkingOptions.freeStreetParking = true"
    ]
    assert street == [(
        "google", "accommodation", "general_amenities",
        "parkingOptions.freeStreetParking = true", "Free Street Parking", "Đỗ xe trên phố",
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


def test_hoac_split_same_amenity():
    rows = _seed_ns()["SEED_ROWS"]
    parking = [row for row in rows if row[0] == "google" and row[1] == "accommodation" and row[4] == "Parking"]
    ev = [row for row in rows if row[0] == "google" and row[4] == "EV Charging Station"]
    assert len(parking) == 2
    assert len(ev) == 3
    assert len({(row[4], row[5]) for row in parking}) == 1
    assert len({(row[4], row[5]) for row in ev}) == 1


def test_resolve_condition_cases():
    assert resolve_condition("parkingOptions.freeStreetParking = true") == (
        "parkingOptions.freeStreetParking", "true",
    )
    assert resolve_condition("outdoorSeating = true") == ("flags.outdoorSeating", "true")
    assert resolve_condition("evChargeOptions.x = true") == ("evChargeOptions.x", "true")
    for raw in (
        "outdoorSeating = true = true",
        "restroom",
        "types[] = swimming_pool",
        "serves_meals = true",
        "parkingOptions.freeParkingLot, parkingOptions.paidParkingLot = true",
        "foo.bar = true",
    ):
        assert resolve_condition(raw) is None
    node = _match_ns()["resolve_condition"]
    assert node("outdoorSeating = true") == ("flags.outdoorSeating", "true")


def test_flag_keys_match_registry():
    text = _nb("NB_CREATE_DDL.ipynb")
    start = text.index('"source_flags_json"')
    block = text[start:text.index('"slv_3p_poi_review"', start)]
    flags = tuple(re.findall(r"'([^']+)'", re.search(r"'keys': \[([^\]]+)\]", block).group(1)))
    objects = tuple(re.findall(r"'key': '([^']+)'", block))
    ns = _match_ns()
    assert ns["FLAG_KEYS"] == flags == FLAG_KEYS
    assert ns["OBJECT_KEYS"] == objects == OBJECT_KEYS


def test_matchable_conditions_pinned():
    rows = _seed_ns()["SEED_ROWS"]
    found = {
        (sector, group, raw)
        for source, sector, group, raw, _en, _vi in rows
        if source == "google" and resolve_condition(raw)
    }
    assert found == MATCHABLE
    assert len(found) == 27


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
    assert "(0, 'slv_poi_entity', 'slv_poi_amenity', 'RETIRE')" in src
