RESULT: PASS

## Main brief

### Decision
Build a new table, `slv_poi_entity_non_enrich`, with notebook `NB_SLV_POI_ENTITY_NON_ENRICH`. Live `slv_poi_entity` is frozen, not renamed and not dropped.
Inside the node: an explicit column list, google rows LEFT JOIN `slv_3p_poi_address`, and partner rows appended (vi only, `deleted` filtered). A pure-Python JSON walk inside a UDF reads `main_category`.
`category_group`: it lands on `ref_dictionary_place_type` through an `NB_CREATE_DDL` patch (ADD COLUMNS, backfill only NULL rows). Google rows use D7. Partner rows use D3 with D9 (`Other` counts as the remainder; a tie blocks the run).
Edges switch with a single MERGE per owner: UPSERT the new edges, RETIRE the old ones (`is_active=0`), all under the flow lock. The two dropped L1 columns come out of the registry only; the live Delta columns stay (A1).

### Invariants Main must preserve
- Output has exactly one live row per `poi_id`. Partner `source_id` is unique (`unique_checks`).
- Partner `poi_id = uuid_md5(F.col("id"), F.lit("partner"))` (D2). It is never joined to the `slv_pn_poi.poi_id` formula.
- The google frame selects `POI_COLS` explicitly. The output never contains `subcategory_tags_json`.
- Every active ref row has non-NULL `category_group`, or the node raises QualityGateError. The output `category_group` is never NULL.
- The D3 step-1 lookup has no source filter and uses exact case. A step-1 result with ≥2 `business_category` blocks the run. A step-2 result with ≥2 named groups (excluding `Other`) blocks the run.
- After the setups: 5 active edges point into the new node, 3 into `slv_poi_amenity`, and 0 active edges have `trg_tbl='slv_poi_entity'` or come from `slv_poi_entity`.
- `NB_SETUP_INITIAL_DDL` stays additive-only: no ALTER, UPDATE, `WHEN MATCHED`, or `ADD COLUMNS`. The seed MERGE in `NB_SETUP_POI_ENTITY` stays insert-only.
- The `BEGIN/END_PLACE_TYPE_SEED` blocks stay byte-identical across both notebooks. `SEED_ROWS` stays as 5-tuples.
- The `TABLE_CONFIGS_3P` cells are identical in `NB_CREATE_DDL` `e9c137c5` and `init_cfg_3p` (53 rows).
- The live `slv_poi_entity` table and its old watermark rows are never written or deleted.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SLV_POI_ENTITY.ipynb → NB_SLV_POI_ENTITY_NON_ENRICH.ipynb | file | git mv; add the new path to scope.files | old path gone, new path in scope |
| 2 | NB_SLV_POI_ENTITY_NON_ENRICH | `b1entitymd` | title and description: google rows plus partner vi rows | text updated |
| 3 | NB_SLV_POI_ENTITY_NON_ENRICH | new cell `b1entityjson` before build | §8.1 block `BEGIN/END_PARTNER_JSON` | test executes it |
| 4 | NB_SLV_POI_ENTITY_NON_ENRICH | `b1entitybuild` | replace with §8.2 | entity tests pass |
| 5 | NB_SETUP_POI_ENTITY | `a1setupmd` | mention `category_group`, new edges, retire | text updated |
| 6 | NB_SETUP_POI_ENTITY | `a1setupseed` | add §8.3 constants and functions; disjointness check in `validate_seed` | seed tests pass |
| 7 | NB_SETUP_POI_ENTITY | `a1setupplan` | `SEED_SCHEMA` gains `category_group`; `with_category_group(SEED_ROWS)`; planned edges = 5 plus retire 2 | plan prints these |
| 8 | NB_SETUP_POI_ENTITY | `a1setupddl` | CREATE gets `category_group STRING` as the last column; add it to `EXPECTED`; error message points to `NB_CREATE_DDL` [THÊM 19/10] | `test_setup_contract` passes |
| 9 | NB_SETUP_POI_ENTITY | `a1setupmerge` | INSERT includes `category_group`; DRIFT compares it | still no `WHEN MATCHED` |
| 10 | NB_SETUP_POI_ENTITY | `a1setupedges` | §8.5 MERGE with UPSERT ×5 and RETIRE ×2, post-checks, flow lock in try/finally | returns (inserted, retired) |
| 11 | NB_SETUP_POI_ENTITY | `a1setupexit` | add `edges_retired` | exit JSON includes it |
| 12 | NB_SETUP_POI_AMENITY | `c1setupplan` | `entity_edges_ok` counts the new target and must equal 5; planned edges use the new name | test passes |
| 13 | NB_SETUP_POI_AMENITY | `c1setupedges` | upsert sources use the new name; RETIRE `slv_poi_entity→slv_poi_amenity`; new message; lock | test passes |
| 14 | NB_SLV_POI_AMENITY | `d1amenmd`, `d1amenbuild` SPEC | `"entity": "slv_poi_entity_non_enrich"` | amenity test passes |
| 15 | NB_CREATE_DDL | cell `e9c137c5` | remove `subcategory_tags_json` and `state_province` entries; mark `[BỎ 19/10]`; 55→53 in comment | registry has 53 rows |
| 16 | NB_CREATE_DDL | new last cells `nonenrmd`, `nonenrpy` | §8.4 patch | patch test passes |
| 17 | NB_SETUP_INITIAL_DDL | `init_cfg_3p` | byte-identical to `e9c137c5` | `test_registry_configs_equal_create_ddl` passes |
| 18 | NB_SETUP_INITIAL_DDL | `init_tables` | ref spec gains `category_group`; entity spec renamed, columns per §6 | columns test passes |
| 19 | NB_SETUP_INITIAL_DDL | `init_seed_ctrl` | SLV_1H rows: 5 entity rows and 3 amenity rows with the new name | 53 rows |
| 20 | NB_SETUP_INITIAL_DDL | `init_seed_place_type` | same seed block; `PLACE_TYPE_ROWS = with_category_group(SEED_ROWS)` | identical-block test passes |
| 21 | NB_SETUP_INITIAL_DDL | `init_plan` | `_v_setup_place_type` schema gains `category_group STRING` | — |
| 22 | NB_SETUP_INITIAL_DDL | `init_seed_write` `_merge_place_type` | INSERT includes `category_group` | still insert-only |
| 23 | NB_ENR_POI_INFO | `dest_name =` | `F.col("a.city")` | token absent |
| 24 | NB_ENR_POI_COORDINATE | `destination_name` line | `F.col("a.city")`; update comment | token absent |
| 25 | tests/test_poi_entity_contract.py | `test_entity_node_contract`, `test_setup_contract`, plus new tests | §20 | pass |
| 26 | tests/test_poi_amenity_contract.py | `test_amenity_node_contract`, setup asserts | §20 | pass |
| 27 | tests/test_initial_ddl_contract.py | inventory, columns_derived, pipeline_config, registry_rows, ref_seed_blocks, new `test_dropped_l1_columns_unread` | §20 | pass |
| 28 | docs/context/01_DATA_MODEL.md | §5.2 (lines ~305-312), §6 N6/N7, §6.1 ref row | 53 columns, A1 note, rename, inputs, partner rows, D2 identity note, `category_group` | — |
| 29 | docs/context/CTRL_TABLES_CONTEXT.md | §3 (lines ~114-128), §10 | new edges, retired edges, notebook name; history line | — |
| 30 | docs/context/02_NAMING_CONVENTION.md | §2.1 rule 7 | rename the entity table | — |
| 31 | docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md | JSON-column list (line ~169) | drop `subcategory_tags_json` | — |
| 32 | docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md | COL-017, COL-042, MQ-034 note | `city` only; `[SỬA 19/10]` note | — |
| 33 | docs/requirements/20261012-map-gld-enr-poi-tables/BRD.md | BR-002, DS-005, BQ-020 note | `city` only | — |

### Order and stop points
1. Add `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` to `scope.files`. Record A1–A8 in `decision.md`; record D9 as pending `USER_DECISION`.
2. Rows 1–4, then rows 5–11, then rows 12–14.
3. Rows 15–22. Keep the two notebooks' cells identical.
4. Rows 23–24.
5. Rows 25–27, then the local tests.
6. Rows 28–33.
7. **STOP (user decision): D9.** The user confirms that `Other` is the remainder in D3 step 2 and that a tie blocks the run. If the user rejects it, return to architecture.
8. **STOP (evidence): probes P1, P2, P3** from §16. If P1 is nonzero, stop for a user decision on the `destination_name` change. P2 needs user acknowledgement of the frozen-table readers.
9. Runtime on DEV, runbook §16 steps 1–9. **STOP (evidence)** if V1–V10 fail.
10. Prod rollout only after the risk gate.

### Tests and verification
- `python -m pytest tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q`
- `python -m pytest -q`
- New or changed tests:
  - `test_entity_node_contract`, `test_partner_json_first`, `test_category_groups_seed`, `test_partner_group_resolution_on_seed`, `test_setup_contract`, `test_create_ddl_patch`
  - `test_amenity_node_contract`
  - `test_table_inventory_matches_sources`, `test_poi_entity_columns_derived`, `test_pipeline_config_rows_match_sources` (53), `test_registry_rows_valid` (53), `test_ref_seed_blocks_identical`, `test_dropped_l1_columns_unread`
- Runtime V1–V10 (§20). Expected DEV values: 24 partner rows, partner `category_group='Other'`, `business_category=business_sector`, rerun gives `NO_DATA`, old table version unchanged.

### Read only if needed
- §3 Design decisions (A1–A8, D9) → rows 4, 15, 16, 23–24
- §6 Grain and keys (column order) → rows 4, 18, 27
- §8.1 Partner JSON helper → row 3
- §8.2 Node build → row 4
- §8.3 Seed block additions → rows 6, 7, 20
- §8.4 NB_CREATE_DDL patch → row 16
- §8.5 Edge switch → rows 10, 13
- §9–13 Commits, idempotency, concurrency, partial failure → rows 10, 13, 16
- §16 Rollout and probes → stops 8 and 9
- §17 Rollback SQL → runtime runbook
- §20 Verification → rows 25–27, stop 9

# Architecture: 20261019-poi-entity-non-enrich

Risk: high. Ledger inputs: D1 to D8 in `decision.md`, probe `evidence/results/partner-json-shape.txt`. This document adds design decisions A1 to A8 and one interpretation, D9, which the user must confirm before the runtime RUN.

## 1. Scope

- Registry: remove `slv_3p_poi.subcategory_tags_json` and `slv_3p_poi_address.state_province` from `TABLE_CONFIGS_3P`, identically in `NB_CREATE_DDL` cell `e9c137c5` and `NB_SETUP_INITIAL_DDL` cell `init_cfg_3p`. 3P registry rows go from 55 to 53.
- Readers of `state_province`: `NB_ENR_POI_INFO` (`dest_name`) and `NB_ENR_POI_COORDINATE` (`destination_name`) switch from `coalesce(a.city, a.state_province)` to `a.city`. Both columns come from the same `ARRAY_PICK administrative_area_level_1/longText`.
- `ref_dictionary_place_type` gains `category_group STRING`, NULL allowed:
  - Seeded from one `CATEGORY_GROUPS` constant by exact `place_type` membership, otherwise `Other`.
  - Existing environments get the column through a new `NB_CREATE_DDL` patch cell: `ADD COLUMNS` plus a backfill `WHERE category_group IS NULL`.
  - New environments get it from the CREATE in `NB_SETUP_POI_ENTITY` / `NB_SETUP_INITIAL_DDL` plus the insert-only seed.
- Node rename: `slv_poi_entity` becomes `slv_poi_entity_non_enrich`, and notebook `NB_SLV_POI_ENTITY` becomes `NB_SLV_POI_ENTITY_NON_ENRICH`. `nb_name` stays NULL, so the lib derives the notebook name.
- Entity columns:
  - Explicit list. `subcategory_tags_json` is dropped.
  - Google rows LEFT JOIN `slv_3p_poi_address` on `poi_id` for `house_number, street, ward, city, full_address, lat, lng`.
  - `category_group` is added (D7).
- Partner rows are appended from `slv_pn_business_services` INNER JOIN `slv_pn_business_service_i18ns` on `locale = 'vi'`. The mapping follows the request, with D2, D3 (+D9), D4, and D5.
- Control edges in `PL_VV_TRANS_SLV_TO_SLV_1H`:
  - 5 edges go into the new node.
  - The 2 old entity edges are retired (`is_active = 0`).
  - The amenity edge source moves to the new node and the old amenity edge is retired.
  - The edge switch is written by the owning setup notebooks while they hold the flow lock.
- Docs and tests listed in `scope.files`.

## 2. Non-goals

- No `DROP TABLE` of live `lh_vv_silver.dbo.slv_poi_entity` (D8). It stays frozen at its last version and serves as the rollback target. Cleanup is a separate, user-approved task after a soak period.
- No physical `ALTER TABLE … DROP COLUMN` on live `slv_3p_poi` / `slv_3p_poi_address` (A1).
- No new place-type dictionary rows. Seven mapping tokens have no dictionary row today: `food`, `resort`, `theme_park`, `tourist_attraction`, `pagoda`, `night_market`, `souvenir_store`. Google POIs whose only match would be one of these get `Other` through D7. Adding rows would change `business_*` and is out of scope.
- No change to `slv_pn_poi` or its `partner_portal` poi_id formula. The two partner identities stay different by D2 (see §5).
- No pipeline JSON. `PL_VV_TRANS_SLV_TO_SLV_1H` is unscheduled and runs manually.
- No lib (`NB_LIB_*`) change.

## 3. Design decisions taken here (Main records in `decision.md`)

| ID | Decision | Why | Alternative rejected |
|---|---|---|---|
| A1 | Live L1 Delta keeps the physical columns. Registry removal stops writes (new inserts NULL, old values stay stale). No `DROP COLUMN`. | `DROP COLUMN` needs a column-mapping protocol upgrade that cannot be undone and may break SQL endpoint or other readers. `ensure_target` never drops. Naming §2.1 rule 5 forbids destructive DDL on tables with data. | Protocol upgrade plus DROP: irreversible, with no rollback. |
| A2 | Partner rows exclude `deleted = true` on both `slv_pn_business_services` and the i18n table. | §5.2: `deleted` is the CDC soft delete. A deleted service must soft-delete its entity row (`deleted_at`). | Not filtering, as `slv_pn_poi` does: produces ghost entities. |
| A3 | Partner address values are copied raw from `get_json_object`. Empty strings stay empty strings. | Same convention as `slv_pn_poi` (decision 2026-10-13). An L1-to-L2 copy without silent normalisation. | Mapping `''` to NULL: an unrequested rule. |
| A4 | `primary_type` is read from `slv_pn_business_services.amentities`, not the i18n `amentities`. | The request lists every other partner field from `slv_pn_business_services`. The probe and D1 targeted that column. | i18n vi `amentities`: not probed and not requested. |
| A5 | A partner `primary_type` that matches no `source_name='partner'` row gives `business_category` / `_vi` = NULL, counted by a warn check. | The request defines only the NULL-`primary_type` fallback. A LEFT lookup yields NULL. DEV impact is 0 rows. | Falling back to `business_sector`: an invented rule. |
| A6 | Partner lookups use exact `place_type = trim(primary_type)`. Google keeps `lower(trim)`. | D3 step 1 has no source filter. Lower-casing would collide partner `Hotel` with google `hotel` and make step 1 ambiguous. Exact case keeps the seed collision-free. | `lower(trim)` on both: creates step-1 ambiguity. |
| A7 | The backfill touches only rows with `category_group IS NULL`. The seed MERGE stays insert-only. | Ref tables are hand-edited (§6.1). Rule §2.1-3 requires the UPDATE to have a value-differs condition. | Overwriting all rows from seed: destroys manual curation. |
| A8 | `main_category` is extracted by a pure-Python JSON walk wrapped in a Spark UDF (§8.1). | The parent key is not fixed and the depth is unknown. Exact JSON semantics. Testable locally without Spark. The table is small (DEV 30 rows). | Regex on JSON text: escaping edge cases and Java/Python regex drift in tests. Bounded `from_json` map levels: fixed depth breaks "parent not fixed". |
| D9 (user confirm) | D3 step 2: collect the distinct `category_group` of active google rows with that `business_category`, ignoring `Other`. 0 named groups gives `Other`. 1 gives that group. 2 or more gives a QualityGateError (no priority invented). Step 1 matching 2 or more distinct `business_category` also gives a QualityGateError. | The request defines `Other` as "phần còn lại", the residue, not a group. On the seed, every `business_category` maps to at most one named group (for example `Café`: {Light Snacks / Cafe, Other} gives Light Snacks / Cafe). DEV impact today is 0, because all partner `primary_type` are NULL and get `Other`. | Treating `Other` as a peer: every mixed category becomes an unresolved tie and blocks. Ordering by seed position: an invented priority. |

## 4. Invariants

1. `slv_poi_entity_non_enrich` has one live row per `poi_id`. The lib QG blocks a NULL or duplicate `poi_id`. The partner rows also have unique `source_id`.
2. Google `poi_id` / `source_id` / name / type fields are copied from `slv_3p_poi`, filtered `lower(trim(source_name)) = 'google'`, by the explicit `POI_COLS` list. `subcategory_tags_json` is never selected, even though the live L1 column still exists.
3. Partner `poi_id = uuid_md5(id, 'partner')`, which is `md5(concat(id,'partner'))` with 8-4-4-4-12 dashes (D2). It is never compared with `slv_pn_poi.poi_id` (`partner_portal` formula).
4. Partner rows exist only for live services with a live `vi` i18n row. A deleted service or a missing vi row means no row, so MERGE soft-deletes it.
5. Google `category_group` comes from the same dictionary row that resolves `business_*` (primary first, then the first matching `types_json` position). Unmatched gives `Other`. Partner `category_group` follows D3 + D9. The node never writes NULL `category_group`.
6. Every active `ref_dictionary_place_type` row has non-NULL `category_group`. The node blocks otherwise. Manual edits to `category_group` are never overwritten.
7. Exactly one active owner for each node. After the switch there are 0 active edges with `trg_tbl='slv_poi_entity'` and 0 active edges `slv_poi_entity → slv_poi_amenity`. There are exactly 5 active edges into `slv_poi_entity_non_enrich` and exactly 3 into `slv_poi_amenity`.
8. Live `slv_poi_entity` is not written after cutover. Its Delta version stays fixed.
9. The 3P registry has no rows for the two dropped columns, and no repo code reads `state_province` or `subcategory_tags_json` from silver.
10. `NB_SETUP_INITIAL_DDL` stays additive-only: no `ALTER`, `UPDATE`, `WHEN MATCHED`, or `ADD COLUMNS` (existing tests).

## 5. State ownership

| State | Owner (sole writer) | Readers |
|---|---|---|
| `ctrl_cfg_schema_registry` 3P rows | `NB_CREATE_DDL` cell `0271d481` (`seed_registry` replaceWhere per source) | 3P extract |
| `slv_3p_poi`, `slv_3p_poi_address` | 3P extract | entity node, ENR nodes |
| `slv_pn_business_services`, `slv_pn_business_service_i18ns` | partner extract | entity node (new), `slv_pn_poi` |
| `ref_dictionary_place_type` rows | Seed: `NB_SETUP_POI_ENTITY` (insert-only). `category_group` backfill: `NB_CREATE_DDL` patch `nonenrpy`. Manual edits. | entity node |
| Edges `* → slv_poi_entity_non_enrich` and retirement of `* → slv_poi_entity` | `NB_SETUP_POI_ENTITY` `_write_edges` | lib `_resolve_node`, NB_00 |
| Edges `* → slv_poi_amenity` (including retirement of the `slv_poi_entity` source) | `NB_SETUP_POI_AMENITY` `_write_edges` | lib, NB_00 |
| `slv_poi_entity_non_enrich` | node `NB_SLV_POI_ENTITY_NON_ENRICH` via lib MERGE | `NB_SLV_POI_AMENITY` |
| Edge watermarks `wm_e__slv_poi_entity_non_enrich__*` | lib / NB_00 (unchanged) | lib |
| Old `wm_e__slv_poi_entity__*`, `wm_e__slv_poi_amenity__slv_poi_entity` | nobody after cutover. Kept for rollback. | rollback only |

Cross-system identity: the same partner service has `poi_id` X here (D2) and Y in `slv_pn_poi` / `gld_enr_poi_coordinate` (`partner_portal`). Docs must say that the two must not be joined on `poi_id`. Join on `source_id` = `business_service_id` instead.

## 6. Grain and keys

| Dataset | Grain | Guard |
|---|---|---|
| `slv_3p_poi` | `poi_id` (registry key) | L1 MERGE key |
| `slv_3p_poi_address` | `poi_id` (registry key), so the LEFT JOIN is 1:1 | lib dup-key QG on output |
| services ⋈ i18n vi | `id`. i18n key is (`business_service_id`, `locale`). Probe: `multi_vi_ids = 0` | lib dup-key QG + `partner_source_id_unique` |
| dict, partner lookup | (`partner`, `place_type`) | explicit QG on duplicate `place_type` |
| dict, D3 step 1 | `place_type` (any source) | QG if a hit has 2 or more distinct `business_category` |
| dict, D3 step 2 | google `business_category` | QG if a hit has 2 or more named groups |
| output | `poi_id`. Google and partner md5 inputs differ, so collision is negligible and blocked anyway | lib QG |

Column order (build = `ensure_target` = `TABLE_SPECS`). Types come from the google frame; partner literals are cast to them.
`POI_COLS` (registry `slv_3p_poi` minus `subcategory_tags_json`, then the snapshot tech columns without `created_at` / `updated_at`): `poi_id, source_name, source_id, language_code, poi_name, poi_name_normalized, types_json, operating_status, primary_type, _crawled_at, _event_id, _first_seen_at, _last_seen_at`. Then `ADDRESS_COLS`: `house_number, street, ward, city, full_address` (string), `lat, lng` (double). Then `CATEGORY_COLS`: `business_sector, business_category, business_category_vi, category_group`. Then the lib `TECH_COLUMNS`.

## 7. Ordering

Build order inside the node:
1. Validate inputs.
2. Ref gate.
3. Google frame.
4. Partner frame (cast to the google schema).
5. `unionByName`.
6. Lib `row_hash`, QG, diff, MERGE.

Rollout order and why each step precedes the next:
1. Deploy notebooks. The flow must not run until step 5. SLV_1H is manual, and the setup lock covers it.
2. Re-seed the 3P registry. It must come before the patch cell's check.
3. Run the `NB_CREATE_DDL` patch `nonenrpy`. It must come before `NB_SETUP_POI_ENTITY`, whose strict `EXPECTED` schema now includes `category_group`.
4. Run `NB_SETUP_POI_ENTITY`. It must come before the amenity setup, whose precondition is 5 active new edges.
5. Run `NB_SETUP_POI_AMENITY`.
6. Run the node RUNs: entity, then amenity. The DAG level guarantees this order under NB_00.
7. Run the ENR flow.

## 8. Code

### 8.1 Partner JSON helper (new cell `b1entityjson`, before `b1entitybuild`)

```python
# BEGIN_PARTNER_JSON
import json

JSON_OK, JSON_NO_VALUE, JSON_NULL, JSON_INVALID = "OK", "NO_VALUE", "NULL_JSON", "INVALID_JSON"


def _first_text(value):
    """Chuỗi đầu tiên khác rỗng (đã trim). Mảng -> phần tử chuỗi đầu tiên khác rỗng; kiểu khác -> None."""
    for item in value if isinstance(value, list) else [value]:
        if isinstance(item, str) and item.strip():
            return item.strip()
    return None


def first_child_value(text, key):
    """Giá trị đầu tiên của khoá con `key` ở mọi độ sâu, theo thứ tự trong tài liệu (duyệt sâu trước).

    Input : text — chuỗi JSON hoặc None ; key — tên khoá con
    Output: (giá trị | None, OK | NO_VALUE | NULL_JSON | INVALID_JSON)
    Ví dụ : first_child_value('{"facilities": {"classification": {"main_category": ["Hotel"]}}}', "main_category")
            -> ("Hotel", "OK")
    """
    if text is None:
        return None, JSON_NULL
    try:
        doc = json.loads(text)
    except (TypeError, ValueError):
        return None, JSON_INVALID
    if doc is None:
        return None, JSON_NULL

    def walk(node):
        if isinstance(node, dict):
            for name, value in node.items():
                if name == key:
                    found = _first_text(value)
                    if found is not None:
                        return found
                hit = walk(value)
                if hit is not None:
                    return hit
        elif isinstance(node, list):
            for item in node:
                hit = walk(item)
                if hit is not None:
                    return hit
        return None

    found = walk(doc)
    return (found, JSON_OK) if found is not None else (None, JSON_NO_VALUE)
# END_PARTNER_JSON
```

Semantics:
- "First" means the first occurrence in document order whose value is a non-empty string, or an array with a non-empty string element.
- An occurrence with an empty or NULL value does not stop the search.
- A TOAST sentinel or invalid JSON returns `INVALID_JSON`, and the node counts it in metrics.

### 8.2 Node build (replace cell `b1entitybuild`)

```python
GOOGLE = "google"
PARTNER = "partner"
OTHER = "other"
OTHER_GROUP = "Other"
POI_COLS = ("poi_id", "source_name", "source_id", "language_code", "poi_name", "poi_name_normalized", "types_json",
            "operating_status", "primary_type", "_crawled_at", "_event_id", "_first_seen_at", "_last_seen_at")
ADDRESS_COLS = ("house_number", "street", "ward", "city", "full_address", "lat", "lng")
CATEGORY_COLS = ("business_sector", "business_category", "business_category_vi", "category_group")
OUT_COLS = POI_COLS + ADDRESS_COLS + CATEGORY_COLS
PARTNER_ADDRESS = {"house_number": "address_line1", "street": "street", "ward": "ward", "city": "city",
                   "full_address": "full_address"}
main_category_of = F.udf(lambda text: first_child_value(text, "main_category"), "struct<value:string,status:string>")


def _live(df: DataFrame) -> DataFrame:
    # Partner L1 CDC: deleted = true là dòng đã xoá ở nguồn (A2).
    return df.where(~F.coalesce(F.col("deleted"), F.lit(False)))


def _google(ctx: NodeContext, poi: DataFrame, d: DataFrame) -> DataFrame:
    # D7: primary_type -> phần tử đầu tiên của types_json khớp (theo vị trí) -> other / other / NULL / Other.
    g = (d.where(F.lower(F.trim("source_name")) == GOOGLE)
         .select(F.lower(F.trim("place_type")).alias("_k"), F.struct(*CATEGORY_COLS).alias("_cat")))
    dup = g.groupBy("_k").count().where("count > 1").count()
    if dup:
        raise QualityGateError(f"ref_dictionary_place_type: {dup} place_type google trùng")
    g = F.broadcast(g)
    by_primary = (poi.select("poi_id", F.lower(F.trim("primary_type")).alias("_k"))
                  .join(g, "_k").select("poi_id", F.col("_cat").alias("_p")))
    by_types = (poi.select("poi_id", F.posexplode(F.from_json("types_json", "array<string>")).alias("_pos", "_t"))
                .withColumn("_k", F.lower(F.trim("_t"))).join(g, "_k")
                .groupBy("poi_id").agg(F.min_by("_cat", "_pos").alias("_m")))
    addr = ctx.input("address").select("poi_id", *ADDRESS_COLS, F.lit(1).alias("_a"))
    out = poi.join(by_primary, "poi_id", "left").join(by_types, "poi_id", "left").join(addr, "poi_id", "left")
    agg = out.agg(F.count(F.lit(1)).alias("rows"), F.count("_p").alias("by_primary"),
                  F.count(F.when(F.col("_p").isNull(), F.col("_m"))).alias("by_types"),
                  F.count("_a").alias("with_address")).first()
    ctx.metrics.update(google_rows=agg["rows"], by_primary=agg["by_primary"], by_types=agg["by_types"],
                       unmatched=agg["rows"] - agg["by_primary"] - agg["by_types"],
                       google_with_address=agg["with_address"], dict_google_rows=g.count())

    def pick(c, default):
        return (F.when(F.col("_p").isNotNull(), F.col(f"_p.{c}"))
                .when(F.col("_m").isNotNull(), F.col(f"_m.{c}"))
                .otherwise(default).alias(c))

    return out.select(*POI_COLS, *ADDRESS_COLS, pick("business_sector", F.lit(OTHER)),
                      pick("business_category", F.lit(OTHER)),
                      pick("business_category_vi", F.lit(None).cast("string")),
                      pick("category_group", F.lit(OTHER_GROUP)))


def _partner(ctx: NodeContext, d: DataFrame, schema) -> DataFrame:
    svc = _live(ctx.input("svc"))
    vi = _live(ctx.input("i18n")).where(F.col("locale") == "vi").select(F.col("business_service_id").alias("id"))
    base = (svc.join(vi, "id").withColumn("_mc", main_category_of(F.col("amentities")))
            .withColumn("primary_type", F.col("_mc.value")))
    # business_category: source_name = partner, place_type = primary_type, khớp đúng chữ (A6).
    dp = (d.where(F.lower(F.trim("source_name")) == PARTNER)
          .select(F.col("place_type").alias("primary_type"),
                  F.struct("business_category", "business_category_vi").alias("_pc")))
    if dp.groupBy("primary_type").count().where("count > 1").count():
        raise QualityGateError("ref_dictionary_place_type: place_type partner trùng")
    # D3 bước 1: place_type = primary_type, không lọc source_name.
    s1 = d.groupBy(F.col("place_type").alias("primary_type")).agg(F.collect_set("business_category").alias("_bcs"))
    # D3 bước 2 + D9: dòng google cùng business_category; Other là phần còn lại, không tính là một nhóm.
    s2 = (d.where(F.lower(F.trim("source_name")) == GOOGLE)
          .groupBy(F.col("business_category").alias("_bc"))
          .agg(F.collect_set(F.when(F.col("category_group") != OTHER_GROUP, F.col("category_group"))).alias("_gs")))
    out = (base.join(F.broadcast(dp), "primary_type", "left").join(F.broadcast(s1), "primary_type", "left")
           .withColumn("_bc", F.when(F.size("_bcs") == 1, F.element_at("_bcs", 1)))
           .join(F.broadcast(s2), "_bc", "left")).persist()
    ctx.cached.append(out)
    live = svc.count()
    agg = out.agg(F.count(F.lit(1)).alias("rows"), F.count("primary_type").alias("primary"),
                  F.count("_pc").alias("primary_matched"),
                  F.count(F.when(F.size("_bcs") > 1, 1)).alias("amb_step1"),
                  F.count(F.when(F.size("_gs") > 1, 1)).alias("amb_step2"),
                  F.count(F.when(F.size("_gs") == 1, 1)).alias("named_group")).first()
    status = {r["s"]: r["n"] for r in out.groupBy(F.col("_mc.status").alias("s")).count()
              .withColumnRenamed("count", "n").collect()}
    ctx.metrics.update(partner_live=live, partner_rows=agg["rows"], partner_without_vi=live - agg["rows"],
                       partner_primary=agg["primary"], partner_primary_matched=agg["primary_matched"],
                       partner_named_group=agg["named_group"], partner_main_category=status)
    if agg["amb_step1"] or agg["amb_step2"]:
        raise QualityGateError(f"ref_dictionary_place_type: D3 không xác định category_group "
                               f"(bước 1: {agg['amb_step1']}, bước 2: {agg['amb_step2']} dòng partner)")
    if live and not agg["rows"]:
        raise QualityGateError("slv_pn_business_services: không dòng nào có bản i18n vi")
    no_type = F.col("primary_type").isNull()
    cols = {
        "poi_id": uuid_md5(F.col("id"), F.lit(PARTNER)),  # D2
        "source_name": F.lit(PARTNER),
        "source_id": F.col("id"),
        "language_code": F.lit("vi"),
        "poi_name": F.col("name"),
        "poi_name_normalized": F.lower(F.col("name")),
        "operating_status": F.col("operation_status"),  # D4
        "primary_type": F.col("primary_type"),
        "business_sector": F.col("business_sector"),
        "business_category": F.when(no_type, F.col("business_sector")).otherwise(F.col("_pc.business_category")),
        "business_category_vi": F.when(no_type, F.col("business_sector")).otherwise(F.col("_pc.business_category_vi")),
        "category_group": F.when(F.size("_gs") == 1, F.element_at("_gs", 1)).otherwise(F.lit(OTHER_GROUP)),
        **{c: F.get_json_object("address", f"$.{k}") for c, k in PARTNER_ADDRESS.items()},
    }
    return out.select(*[cols.get(c, F.lit(None)).cast(schema[c].dataType).alias(c) for c in OUT_COLS])


def build(ctx: NodeContext) -> DataFrame:
    src = ctx.input("poi")
    missing = [c for c in POI_COLS if c not in src.columns]
    if missing:
        raise ConfigError(f"slv_poi_entity_non_enrich: slv_3p_poi thiếu cột {missing}")
    d = ctx.input("dict")
    if "category_group" not in d.columns:
        raise ConfigError("ref_dictionary_place_type chưa có category_group: chạy cell [THÊM 19/10] của NB_CREATE_DDL")
    d = d.where(F.col("is_active") == F.lit(True))
    no_group = d.where(F.col("category_group").isNull()).count()
    if no_group:
        raise QualityGateError(f"ref_dictionary_place_type: {no_group} dòng active thiếu category_group")
    total = src.count()
    google = _google(ctx, src.where(F.lower(F.trim("source_name")) == GOOGLE).select(*POI_COLS), d)
    ctx.metrics.update(non_google_rows=total - ctx.metrics["google_rows"])
    if total and not ctx.metrics["google_rows"]:
        raise QualityGateError("slv_poi_entity_non_enrich: slv_3p_poi không có dòng google")
    return google.unionByName(_partner(ctx, d, google.schema))


SPEC = NodeSpec(
    trg_tbl="slv_poi_entity_non_enrich",
    inputs={"poi": "slv_3p_poi", "address": "slv_3p_poi_address", "dict": "ref_dictionary_place_type",
            "svc": "slv_pn_business_services", "i18n": "slv_pn_business_service_i18ns"},
    pk=("poi_id",),
    build=build,
    required_inputs=("poi", "address", "dict", "svc", "i18n"),
    unique_checks=(("partner_source_id_unique", ("source_id",), "source_name = 'partner'"),),
    warn_checks=(("types_json_unparsed",
                  "types_json IS NOT NULL AND from_json(types_json, 'array<string>') IS NULL"),
                 ("partner_primary_type_unmatched",
                  "source_name = 'partner' AND primary_type IS NOT NULL AND business_category IS NULL")),
    write_mode="MERGE",
)
```

Before running, Main checks:
- `ctx.cached` exists as a list. The lib unpersists it in `finally`.
- `uuid_md5` takes Column arguments.
- `F.size(NULL)` returns -1 or NULL. Either way it is ≠ 1 and not > 1.

The markdown cell `b1entitymd` changes to: RECOMPUTE `lh_vv_silver.dbo.slv_poi_entity_non_enrich`, google rows plus partner rows (vi).

### 8.3 Seed block additions (`a1setupseed` and `init_seed_place_type`, byte-identical between `BEGIN/END_PLACE_TYPE_SEED`)

```python
CATEGORY_OTHER = "Other"
CATEGORY_GROUPS = (
    ("Lodging", ("lodging", "hotel", "resort_hotel", "motel", "guest_house", "hostel", "bed_and_breakfast", "resort")),
    ("Main Meals", ("restaurant", "food", "meal_takeaway", "seafood_restaurant", "bistro")),
    ("Light Snacks / Cafe", ("cafe", "bakery", "coffee_shop", "tea_house")),
    ("Heavy Entertainment", ("amusement_park", "theme_park", "water_park", "zoo", "aquarium", "national_park",
                             "hiking_area")),
    ("Light Sightseeing / Culture & Nature", ("tourist_attraction", "museum", "place_of_worship", "beach", "park",
                                              "historical_landmark", "pagoda", "church")),
    ("Shopping & Nightlife", ("shopping_mall", "market", "night_market", "bar", "night_club", "souvenir_store")),
)


def category_group(place_type):
    """Nhóm theo CATEGORY_GROUPS, khớp đúng chữ. Ví dụ: hotel -> Lodging ; Hotel (partner) -> Other."""
    for group, types in CATEGORY_GROUPS:
        if place_type in types:
            return group
    return CATEGORY_OTHER


def with_category_group(rows):
    """Dòng seed 5 trường -> 6 trường (thêm category_group)."""
    return [tuple(row) + (category_group(row[1]),) for row in rows]
```

`validate_seed` gains a check that raises `ValueError` if a token appears in two groups. `SEED_ROWS` stays as 5-tuples, so `test_seed_matches_mapping_file` keeps passing.

### 8.4 `NB_CREATE_DDL` patch (new markdown `nonenrmd`: `[THÊM 19/10] 20261019-poi-entity-non-enrich`; new code `nonenrpy`, last cells)

```python
# [THÊM 19/10] 20261019-poi-entity-non-enrich
# 1. ref_dictionary_place_type thêm category_group (cho phép NULL). Backfill chỉ dòng đang NULL (giữ sửa tay).
#    CATEGORY_GROUPS giống hệt khối BEGIN_PLACE_TYPE_SEED (test kiểm tra).
# 2. Kiểm tra registry 3P đã bỏ slv_3p_poi.subcategory_tags_json, slv_3p_poi_address.state_province.
#    Chạy lại cell 0f228dc1, e9c137c5, 0271d481 trước cell này. Cột Delta cũ giữ nguyên, không DROP.
import re

PT_FQ = "lh_vv_silver.dbo.ref_dictionary_place_type"
REG_FQ = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry"
CATEGORY_OTHER = "Other"
CATEGORY_GROUPS = (...)  # chép nguyên văn từ §8.3

token_re, group_re = re.compile(r"^[a-z0-9_]+$"), re.compile(r"^[A-Za-z /&]+$")
bad = [t for _g, ts in CATEGORY_GROUPS for t in ts if not token_re.fullmatch(t)]
bad += [g for g, _ts in CATEGORY_GROUPS if not group_re.fullmatch(g)]
if bad:
    raise RuntimeError(f"CATEGORY_GROUPS sai: {bad}")

if "category_group" not in {f.name.lower() for f in spark.table(PT_FQ).schema.fields}:
    spark.sql(f"ALTER TABLE {PT_FQ} ADD COLUMNS (category_group STRING)")
case = " ".join(f"WHEN place_type IN ({', '.join(repr(t) for t in ts)}) THEN '{g}'" for g, ts in CATEGORY_GROUPS)
spark.sql(f"""
    UPDATE {PT_FQ}
    SET category_group = CASE {case} ELSE '{CATEGORY_OTHER}' END, updated_at = current_timestamp()
    WHERE category_group IS NULL
""")

errors = []
n_null = spark.sql(f"SELECT count(*) AS n FROM {PT_FQ} WHERE category_group IS NULL").first()["n"]
if n_null:
    errors.append(f"{PT_FQ}: còn {n_null} dòng category_group NULL")
left = spark.sql(f"""
    SELECT trg_tbl, trg_column FROM {REG_FQ}
    WHERE src_tbl = 'brz_3rd_crawler_poi_stream'
      AND ((trg_tbl = 'slv_3p_poi' AND trg_column = 'subcategory_tags_json')
           OR (trg_tbl = 'slv_3p_poi_address' AND trg_column = 'state_province'))
""").collect()
if left:
    errors.append(f"registry 3P còn {[(r.trg_tbl, r.trg_column) for r in left]}: chạy lại cell 0271d481")
if errors:
    raise RuntimeError("\n".join(errors))
spark.sql(f"SELECT source_name, category_group, count(*) AS n FROM {PT_FQ} GROUP BY 1, 2 ORDER BY 1, 2").show(50, False)
```

Main must write `CATEGORY_GROUPS` out in full; the `(...)` above is only a placeholder in this document. The cell must not contain `CREATE TABLE IF NOT EXISTS lh_vv_…`, because `test_table_inventory_matches_sources` scans for that string.

### 8.5 Edge switch (`a1setupedges`; same pattern in `c1setupedges`)

Single MERGE, so the switch for one node is one Delta commit:

```sql
MERGE INTO {cfg} AS t
USING (
  SELECT * FROM VALUES
    (1, 'slv_3p_poi', 'slv_poi_entity_non_enrich', 'UPSERT'),
    (2, 'slv_3p_poi_address', 'slv_poi_entity_non_enrich', 'UPSERT'),
    (3, 'ref_dictionary_place_type', 'slv_poi_entity_non_enrich', 'UPSERT'),
    (4, 'slv_pn_business_services', 'slv_poi_entity_non_enrich', 'UPSERT'),
    (5, 'slv_pn_business_service_i18ns', 'slv_poi_entity_non_enrich', 'UPSERT'),
    (0, 'slv_3p_poi', 'slv_poi_entity', 'RETIRE'),
    (0, 'ref_dictionary_place_type', 'slv_poi_entity', 'RETIRE') AS v(seq, src_tbl, trg_tbl, action)
) AS s
ON t.pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND t.src_tbl = s.src_tbl AND t.trg_tbl = s.trg_tbl
WHEN MATCHED AND s.action = 'RETIRE' AND NOT (t.is_active <=> 0) THEN UPDATE SET is_active = 0
WHEN MATCHED AND s.action = 'UPSERT' AND NOT (<existing normal-form predicate>) THEN UPDATE SET <existing set list>
WHEN NOT MATCHED AND s.action = 'UPSERT' THEN INSERT (<existing columns>)
  VALUES (COALESCE((SELECT MAX(id) FROM {cfg}), 0) + s.seq, 'PL_VV_TRANS_SLV_TO_SLV_1H', 'lh_vv_silver.dbo', s.src_tbl,
          'lh_vv_silver.dbo', s.trg_tbl, 1, 1, 'RECOMPUTE', CAST(NULL AS STRING), CAST(NULL AS STRING){nb_val})
```

Changes to the surrounding checks:
- The duplicate check and the `missing` count cover both target names.
- The `owners` / `extra` / `ok` checks target `slv_poi_entity_non_enrich` with the 5 sources.
- New post-check: zero active rows with `trg_tbl = 'slv_poi_entity'` in any `pl_name`. Otherwise `ConfigError`.
- `_write_edges` returns `(inserted, retired)`. `a1setupexit` reports both.

Amenity setup changes:
- The upsert sources are `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich`, `ref_dictionary_amenities`.
- Retire row: `(0,'slv_poi_entity','slv_poi_amenity','RETIRE')`.
- `entity_edges_ok` counts active `trg_tbl = 'slv_poi_entity_non_enrich'` edges and requires `== 5`.
- The precondition message becomes `slv_poi_amenity: chưa có cạnh slv_poi_entity_non_enrich, chạy NB_SETUP_POI_ENTITY trước`.

Flow lock around the edge write, in both setups. This mirrors the manual path in `run_node`:

```python
PL = "PL_VV_TRANS_SLV_TO_SLV_1H"
SETUP_EXEC = str(uuid.uuid4())
ensure_lock_row(PL, current_notebook_name("NB_SETUP_POI_ENTITY"))
ok, who = acquire_flow_lock(PL, SETUP_EXEC, SETUP_EXEC, LOCK_TIMEOUT_DEFAULT_MIN)
if not ok:
    raise ConfigError(f"Luồng {PL} đang chạy ({who}); chạy setup sau")
status = "FAILED"
try:
    EDGES_INSERTED, EDGES_RETIRED = with_retry(_write_edges, "edges slv_poi_entity_non_enrich")
    status = "SUCCESS"
finally:
    release_flow_lock(PL, SETUP_EXEC, status)
```

Main confirms that `ensure_lock_row`'s second argument is only used to create a missing row. If it overwrites an NB_00 field, Main drops the `ensure_lock_row` call and skips the lock when `read_flow_lock` returns None, because a missing lock row means the flow has never run.

## 9. Transaction and commit boundaries

| Step | Commits | Atomic unit |
|---|---|---|
| Registry reseed (`0271d481`) | 1 (replaceWhere for the 3P source) | the whole 3P registry |
| Patch `nonenrpy` | ALTER (metadata) + UPDATE (data) | each statement |
| Setup entity | ref seed MERGE + edge MERGE | edge switch for the entity node = 1 commit |
| Setup amenity | ref seed MERGE + edge MERGE | edge switch for the amenity = 1 commit |
| First node RUN | CREATE target + MERGE | MERGE |
| Later RUNs | at most 1 MERGE. No commit when diff = 0 | MERGE |

The two edge commits (entity, amenity) are not one transaction. The window between them is safe because both setups hold the flow lock while writing, and NB_00 cannot start without that lock. No node runs between the two setups.

## 10. Idempotency

- Registry reseed is a full replace of a deterministic set.
- Patch: ALTER runs only if the column is absent. UPDATE touches only NULL rows. A rerun is a no-op.
- Seed MERGE is insert-only. The edge MERGE updates only when values differ, and RETIRE runs only when `is_active` is not already 0. A rerun gives 0 inserted / 0 retired.
- Node: deterministic build. `min_by` uses position, the JSON walk uses document order, and `collect_set` is followed by size checks only, so element order never matters except when the size is 1. Unchanged inputs give `NO_DATA`. `p_force=true` with unchanged inputs gives diff 0 and no commit.

## 11. Concurrency

- SLV_1H node runs are serialised by the flow lock, and the setups now take it too.
- The 3P and partner extracts write the L1 inputs concurrently. The node reads each input at a pinned Delta version, which gives a consistent snapshot per input. Cross-input skew (for example services vs i18n) is the same as in existing nodes, and the next run repairs it.
- Run the registry reseed while the 3P extract is idle: check that the lock on `wm_transform_brz_3rd_crawler_poi_stream` is empty. If an extract is mid-run, it already loaded its config, so the effect is only a delay.
- Manual ref edits during a run go to a later version, so the next run sees them.

## 12. Retry and recovery

- Setup writes use `with_retry`, which covers Delta conflicts. Lock release is in `finally`.
- If a node fails, the lib records FAILED, nothing is MERGEd, and edge watermarks do not advance. The next run recomputes from scratch.
- If the target CREATE succeeds and the MERGE fails, the table is left empty. The next run sees a missing watermark, so the edges are dirty and the node rebuilds.

## 13. Partial failure

| Failure point | State | Recovery |
|---|---|---|
| After the registry reseed, before deploying ENR | Extract writes NULL to the dropped columns for new rows. Old ENR code still reads `coalesce(city, NULL)`, which equals `city`. | Continue the rollout. |
| Patch: after ALTER, before UPDATE | Column exists with NULLs. The node blocks on its ref gate. | Rerun the patch cell. |
| Setup entity: after seed, before edges | Old edges are still active, but the node notebook has been renamed, so an old-flow run would fail. The lock is released. | Rerun setup. Do not run the flow first. |
| After the entity edge switch, before the amenity switch | Amenity edge from `slv_poi_entity` is still active; new amenity code expects the new input, so its run would fail with ConfigError. | Run the amenity setup. |
| Node QG block (D3 ambiguity, missing vi, NULL `category_group`) | Nothing written. | Fix the ref data or confirm with the user, then rerun. |
| ENR step reveals `city` ≠ `state_province` in history | Gold `destination_name` would change. | This is pre-checked by probe P1 (§16), which stops for a user decision. |

## 14. Observability

- `ctrl_log_table_run.qg_json.metrics` for the entity node:
  - `google_rows`, `by_primary`, `by_types`, `unmatched`, `google_with_address`, `dict_google_rows`, `non_google_rows`.
  - `partner_live`, `partner_rows`, `partner_without_vi`, `partner_primary`, `partner_primary_matched`, `partner_named_group`, `partner_main_category` ({status: n}).
- Warn checks: `types_json_unparsed`, `partner_primary_type_unmatched`.
- Setup exit JSON reports `edges_inserted` and `edges_retired`. The patch cell prints the `category_group` distribution.
- Expected DEV values from the probe: `partner_live=30`, `partner_rows=24`, `partner_without_vi=6`, `partner_primary=0`, `partner_main_category={NULL_JSON: 29, NO_VALUE: 1}`. The probe's "1 null" row and its 28 JSON-null rows are both NULL_JSON.

## 15. Security

- No secrets, and no new external calls.
- Business address text stays in silver. Metrics and logs carry counts only, never address or name values.
- The SQL built in the patch cell comes from regex-validated constants only (naming §8, SQL safety).
- The UDF runs in-cluster on data that is already in the lakehouse.

## 16. Rollout (DEV first, then the same runbook for prod)

Evidence probes before the RUN. All are read-only and record their results in `evidence/results/`.
- **P1** (stop if nonzero), from `lh_vv_silver.dbo.slv_3p_poi_address`:
  - `count(*)`
  - `sum(city IS NULL AND state_province IS NOT NULL)`
  - `sum(city <> state_province)`

  If either sum is > 0, removing the coalesce changes gold `destination_name` for history rows. Main stops for a user decision.
- **P2**: list Fabric items (reports, SQL views, other workspaces) that reference `slv_poi_entity`. They will read a frozen table. Manual check and user acknowledgement.
- **P3**: `lh_vv_silver.dbo.slv_pn_business_service_i18ns` has column `deleted` (`DESCRIBE`).

Runbook:
1. Merge the code and deploy the notebooks. `NB_SLV_POI_ENTITY_NON_ENRICH` must exist in the workspace. Do not run SLV_1H until step 6.
2. In `NB_CREATE_DDL`, run cells `0f228dc1`, `e9c137c5`, `0271d481`. Check that the registry 3P count is 53.
3. In `NB_CREATE_DDL`, run cell `nonenrpy`.
4. Run `NB_SETUP_POI_ENTITY` with `p_apply=false`. Check the plan, then run with `p_apply=true`. Expect `edges_inserted=5`, `edges_retired=2`.
5. Run `NB_SETUP_POI_AMENITY` with `p_apply=false`, then `true`. Expect `edges_inserted=1`, `edges_retired=1`.
6. Run `NB_SLV_POI_ENTITY_NON_ENRICH` with `p_mode=DRY_RUN`, then `RUN`. Then run `NB_SLV_POI_AMENITY` with `RUN`, or run NB_00 for SLV_1H.
7. Let the 3P extract run once (scheduled or manual) and confirm it ends SUCCESS.
8. Run the ENR_15P flow.
9. Run verification V1 to V10.

## 17. Rollback and forward recovery

Forward recovery is preferred. Every step is rerunnable and every gate fails closed.

Rollback, with SLV_1H idle:
1. `git revert` the merge and redeploy the notebooks, so `NB_SLV_POI_ENTITY` and the old amenity code come back.
2. Swap the edges back:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND is_active = 1
  AND (trg_tbl = 'slv_poi_entity_non_enrich' OR (trg_tbl = 'slv_poi_amenity' AND src_tbl = 'slv_poi_entity_non_enrich'));
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 1
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND is_active = 0
  AND ((trg_tbl = 'slv_poi_entity' AND src_tbl IN ('slv_3p_poi', 'ref_dictionary_place_type'))
       OR (trg_tbl = 'slv_poi_amenity' AND src_tbl = 'slv_poi_entity'));
```

3. Run the old entity node and then the amenity node. The old watermarks still exist, so the inputs show as dirty and the nodes recompute.
4. Registry (optional): rerun `0271d481` with the reverted config. The two columns come back for new extracts; rows written in the gap stay NULL until the next crawl.

Do not drop `category_group` and do not rerun the old `NB_SETUP_POI_ENTITY`, whose strict schema check would fail. The column is additive and the old node ignores it. `slv_poi_entity_non_enrich` stays orphaned until the user decides.

## 18. Alternatives and trade-offs

| Topic | Selected | Alternative | Why selected |
|---|---|---|---|
| Rename mechanics | New table via `ensure_target`. Old table frozen. Edges retired. | `ALTER TABLE RENAME` of live Delta. | Rename is invisible to watermarks: `table_id` stays, but the edge ids change and the lib checks table identity. It also loses the rollback target, and D8 forbids dropping. A new table costs one full build (about 19k google rows + partner), which is cheap. |
| Edge switch | One MERGE per owner with RETIRE rows, under the flow lock. | Delete the old edges. | Delete loses history and rollback. RETIRE is reversible. |
| Edge atomicity across nodes | Two commits plus the flow lock. | Entity setup also writes the amenity edges. | Keeps one writer per edge set (current test contract). The lock closes the window. |
| Input frame | Explicit `POI_COLS`. | Keep "all `slv_3p_poi` columns". | The live L1 keeps `subcategory_tags_json` physically (A1), so passthrough would re-add it. |
| Mass-delete protection | All 5 inputs required, plus a "partner live > 0 but 0 vi rows" gate. | Partner inputs optional. | Optional inputs would let an empty partner snapshot soft-delete every partner row. Cost: the node needs partner L1 tables present, which is already true because `run_node` fails on missing inputs. |
| `category_group` backfill location | `NB_CREATE_DDL` patch (rule §2.1-3). Setup schema check fails fast with a hint. | ALTER inside `NB_SETUP_POI_ENTITY`. | Follows the repo's DDL-patch rule and keeps the setup seed insert-only, which the test asserts. |

## 19. Implementation plan

Rows match the Main brief edit list.
1. Scope: rename `notebooks/NB_SLV_POI_ENTITY.ipynb` to `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb`. Add the new path to `scope.files`.
2. Entity notebook: cells `b1entitymd`, new `b1entityjson` (§8.1), and `b1entitybuild` (§8.2).
3. `NB_SETUP_POI_ENTITY`:
   - `a1setupmd`.
   - `a1setupseed` (§8.3).
   - `a1setupplan`: `SEED_SCHEMA` gets `category_group string`, `seed_df` uses `with_category_group(SEED_ROWS)`, and the planned edges list the 5 sources plus retire 2.
   - `a1setupddl`: CREATE gets `category_group STRING` last. `EXPECTED` gets `("category_group","string",True)`. The error mentions the `NB_CREATE_DDL` cell `[THÊM 19/10]`.
   - `a1setupmerge`: INSERT adds `category_group`. `DRIFT` adds `t.category_group <=> s.category_group`.
   - `a1setupedges` (§8.5).
   - `a1setupexit`.
4. `NB_SETUP_POI_AMENITY`: `c1setupplan` and `c1setupedges` (§8.5).
5. `NB_SLV_POI_AMENITY`: `d1amenmd` text, and `d1amenbuild` SPEC `"entity": "slv_poi_entity_non_enrich"`.
6. `NB_CREATE_DDL`: `e9c137c5` removes the 2 entries and adds a `[BỎ 19/10]` comment, changing "55 cột" to "53 cột". It also drops `subcategory_tags_json` from the JSON-array comment. Add the new cells `nonenrmd` / `nonenrpy` (§8.4).
7. `NB_SETUP_INITIAL_DDL`:
   - `init_cfg_3p` is byte-identical to `e9c137c5`.
   - `init_tables`: ref spec adds `('category_group','STRING',None)` last. The entity spec is renamed to `lh_vv_silver.dbo.slv_poi_entity_non_enrich` with columns from §6 plus TECH.
   - `init_seed_ctrl`: SLV_1H rows are the 5 entity edges plus the 3 amenity edges with source `slv_poi_entity_non_enrich`.
   - `init_seed_place_type`: same seed block, plus `PLACE_TYPE_ROWS = with_category_group(SEED_ROWS)`.
   - `init_plan`: the place-type view schema adds `category_group STRING`.
   - `init_seed_write`: `_merge_place_type` INSERT adds `category_group`.
8. ENR readers: `NB_ENR_POI_INFO` `dest_name = F.col("a.city")`. `NB_ENR_POI_COORDINATE` `F.col("a.city").alias("destination_name")`, with the comment updated to cite this task.
9. Tests (§20).
10. Docs:
    - `01_DATA_MODEL.md` §5.2: 55→53, remove `subcategory_tags_json`, add a note on A1.
    - `01_DATA_MODEL.md` §6 N6/N7 and §6.1 `ref_dictionary_place_type` row: rename, inputs, partner rows, D2 identity note, `category_group`.
    - `CTRL_TABLES_CONTEXT.md` §3: SLV_1H edges, `NB_SLV_POI_ENTITY_NON_ENRICH`, retired edges. §10: history line.
    - `02_NAMING_CONVENTION.md` §2.1 rule 7: rename.
    - `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`: JSON-column list.
    - `MAPPING.md` / `BRD.md`: COL-017, COL-042, BR-002, DS-005 use `city`. Add a note `[SỬA 19/10] state_province bỏ khỏi slv_3p_poi_address (trùng city)`. MQ-034 / BQ-020 stay as history, with a superseded note.
11. Ledger: record A1 to A8, and D9 as `USER_DECISION` pending.

## 20. Verification

Local (no Spark): `python -m pytest tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q`, then `python -m pytest -q`.

Test changes in `tests/test_poi_entity_contract.py`:
- `test_entity_node_contract`: reads `NB_SLV_POI_ENTITY_NON_ENRICH.ipynb`. Asserts:
  - `trg_tbl="slv_poi_entity_non_enrich"`, all 5 input roles, and `required_inputs=("poi", "address", "dict", "svc", "i18n")`.
  - `uuid_md5(F.col("id"), F.lit(PARTNER))`, `"operation_status"`, `== "vi"`, `"subcategory_tags_json" not in src`.
  - All existing posexplode / `min_by` / `_p` before `_m` asserts.
- New `test_partner_json_first`: execs `BEGIN/END_PARTNER_JSON` and covers these cases:
  - Nested sample: `facilities.classification.main_category`.
  - Array: first non-empty element wins.
  - Document order: `{"x":{"main_category":"A"},"main_category":"B"}` gives A.
  - Empty first occurrence followed by a valid one gives the later value.
  - `"null"` gives `NULL_JSON`. `None` gives `NULL_JSON`. Invalid text gives `INVALID_JSON`. No key gives `NO_VALUE`.
- New `test_category_groups_seed`:
  - Groups and tokens equal the request literal and are disjoint.
  - `category_group("hotel") == "Lodging"`, `("Hotel") == "Other"`, `("vietnamese_restaurant") == "Other"`.
  - `with_category_group(SEED_ROWS)` returns 356 6-tuples.
- New `test_partner_group_resolution_on_seed`: a pure-Python model of D3+D9 over the seed.
  - Step 1 is never ambiguous.
  - No `business_category` has 2 or more named groups.
  - `Hotel` → Lodging, `Homestay` → Lodging, `Café` → Light Snacks / Cafe, `Vietnamese` → Other, `Car with Driver` → Other.
- `test_setup_contract`:
  - DDL includes `category_group`.
  - Seed MERGE still has no `WHEN MATCHED`.
  - Edges contain the 5 new sources, `'RETIRE'`, `is_active = 0`, `acquire_flow_lock`, and `release_flow_lock` inside `finally`.
- New `test_create_ddl_patch`:
  - The last two cells are `nonenrmd` / `nonenrpy`.
  - `ADD COLUMNS (category_group STRING)` sits behind a not-in guard.
  - `WHERE category_group IS NULL`.
  - `CATEGORY_GROUPS` equals the seed block's (via `_assign`).

Test changes in `tests/test_poi_amenity_contract.py`: `"entity": "slv_poi_entity_non_enrich"`, the new precondition message, `== 5`, and a `'RETIRE'` row for `slv_poi_entity`.

Test changes in `tests/test_initial_ddl_contract.py`:
- `test_table_inventory_matches_sources` reads the new notebook name. The spec count stays 14.
- `test_poi_entity_columns_derived`: expected columns = registry `slv_3p_poi` active + snapshot (minus tech) + registry `slv_3p_poi_address` rows for `ADDRESS_COLS` in that order + `CATEGORY_COLS` with `EXPECTED` types + `TECH_COLUMNS`. It also asserts `POI_COLS`, `ADDRESS_COLS`, `CATEGORY_COLS` against the build (replacing the `keep = …` asserts) and `spec["fq"] == "lh_vv_silver.dbo.slv_poi_entity_non_enrich"`.
- `test_pipeline_config_rows_match_sources`: new SLV_1H rows. `len(expected) == 53`.
- `test_registry_rows_valid`: `len(rows) == 53`.
- `test_ref_seed_blocks_identical`: `"PLACE_TYPE_ROWS = with_category_group(SEED_ROWS)"`.
- New `test_dropped_l1_columns_unread`:
  - The flattened 3P registry has no (`slv_3p_poi`, `subcategory_tags_json`) and no (`slv_3p_poi_address`, `state_province`).
  - Non-comment code in `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, and `NB_SLV_POI_ENTITY_NON_ENRICH` contains neither token.
  - `TABLE_SPECS` contains neither token.

Runtime on DEV (results go to `evidence/results/`):
- **V1**: registry 3P has 53 rows and 0 rows for the dropped pair.
- **V2**: `ref_dictionary_place_type` has 0 NULL `category_group`. Spot checks: (google, `hotel`) → Lodging, (google, `cafe`) → Light Snacks / Cafe, (partner, `Hotel`) → Other.
- **V3**: active SLV_1H edges are exactly 5 into the new node and 3 into amenity, with 0 active into `slv_poi_entity`.
- **V4**: entity RUN is SUCCESS.
  - Google row count = `count(slv_3p_poi WHERE lower(trim(source_name))='google')`.
  - Partner rows = 24 (probe).
  - `count(distinct poi_id) = count(*)`.
  - Partner `poi_id RLIKE '^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'`.
  - Partner `business_category = business_sector` and `category_group = 'Other'` on all rows (since `primary_type` is NULL).
- **V5**: `google_with_address` ≈ address rows for google `poi_id`. `subcategory_tags_json` is absent from the table schema.
- **V6**: rerun with no input change gives `NO_DATA`. `p_force=true` gives 0/0/0 with no new Delta version.
- **V7**: amenity RUN is SUCCESS. The live amenity row count equals the pre-cutover count, since partner rows do not join `slv_3p_poi_amenity`.
- **V8**: the 3P extract run after the reseed is SUCCESS. Newly inserted rows have NULL `subcategory_tags_json` / `state_province`.
- **V9**: the ENR run is SUCCESS. The `destination_name` distribution is unchanged vs the previous run (given P1 = 0).
- **V10**: `DESCRIBE HISTORY lh_vv_silver.dbo.slv_poi_entity` shows no version after cutover.
