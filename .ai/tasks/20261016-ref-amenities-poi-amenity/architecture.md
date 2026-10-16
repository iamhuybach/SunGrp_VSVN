RESULT: PASS

## Main brief

### Decision
- Use the sibling pattern. `NB_SETUP_POI_AMENITY` holds the DDL for both tables, the insert-only seed and 3 edges. `NB_SLV_POI_AMENITY` is a RECOMPUTE/MERGE node in `PL_VV_TRANS_SLV_TO_SLV_1H`. The tests go in `tests/test_poi_amenity_contract.py`. `NB_CREATE_DDL` is not edited.
- Matching: explode `source_flags_json` into (`poi_id`, `_path`, `_v`), with bare flags under `flags.`, then equi-join a broadcast frame of the matchable google conditions on (`business_sector`, `_path`, `_v`).
- A dictionary row is matchable only if it has the form `path = true|false`. Bare paths, comma lists, `types[]`, and prose are seeded but never match. There are 27 matchable conditions.
- The dictionary key is 5 columns (+`amenity`), because 2.3 has `goodForChildren` twice. The `slv_poi_amenity` key is the Q3 key.
- Q4 is decided: F&B sector is `f_n_b` on both `slv_poi_entity` and this dictionary. No alias.

### Invariants Main must preserve
- Neither table has `business_category` or a boolean value column. The column sets match the DDL in the full document exactly.
- Seed rows are unique on (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`). There are 74 partner and 78 google rows.
- Active matchable google conditions are unique on (`business_sector`, `amenity_group`, `amenity_raw`). Otherwise the node raises `QualityGateError` before writing.
- Live `slv_poi_amenity` rows are unique on (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`).
- A row requires the exact path and the exact `true`/`false` literal. A null object, `false` against `= true`, or an unmatched flag produces no row, and no `other` row is created.
- `business_sector` comes from live `slv_poi_entity` (Q1). A POI that is not in the entity table produces no rows.
- No seed value is in SKIP (`Bổ sung sau`, `Fallback`, `Không có field`, `Không có field riêng`, empty). The seed uses `accommodation`, and F&B uses the Q4 code.
- Dictionary sectors ⊆ `NB_SETUP_POI_ENTITY.SEED_SECTORS`. `FLAG_KEYS`/`OBJECT_KEYS` equal the `JSON_PICK` members in `NB_CREATE_DDL`.
- Setup writes nothing with `p_apply="false"`. It fails before writing edges if the 2 `slv_poi_entity` edges are not active.
- The seed is insert-only: no `WHEN MATCHED`, `is_active=true`, `updated_at=current_timestamp()`.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | tests/test_poi_amenity_contract.py | `parse_mapping` | Implement the "Parser rules" | prints 74 partner / 78 google |
| 2 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupmd`, `c1setupparam`, `c1setuprun` | Vietnamese title; `p_apply = "false"`; `%run NB_LIB_TRANSFORM_SLV_GLD` | mirrors `a1setup*` |
| 3 | same | `c1setupseed` (`# BEGIN_AMENITY_SEED`…`# END_AMENITY_SEED`) | `SEED_SECTORS`, `SEED_GROUPS`, `SEED_SKIP`, `SEED_ROWS` (pasted from the parser), `validate_seed` | `test_seed_matches_mapping_file` passes |
| 4 | same | `c1setupplan` | Plan, `missing_keys` on the 5-column key, `entity_edges_ok`, exit when not applying | PLAN JSON contains `entity_edges_ok` |
| 5 | same | `c1setupddl` | Both DDLs and `EXPECTED` schema asserts (section "DDL") | `test_setup_contract` passes |
| 6 | same | `c1setupmerge` | Insert-only MERGE on the 5-column key, dup/missing/drift checks | no `WHEN MATCHED` |
| 7 | same | `c1setupedges` `_write_edges` | Copy `a1setupedges` for `slv_poi_amenity` with 3 src; entity precheck `ConfigError` | expected counts are 3×1 |
| 8 | same | `c1setupexit` | Summary JSON | — |
| 9 | notebooks/NB_SLV_POI_AMENITY.ipynb | `d1amenmd`, `d1amenparam`, `d1amenrun`, `d1amenres`, `d1amenexit` | Copy the `b1entity*` equivalents | — |
| 10 | same | `d1amenmatch` (`# BEGIN_AMENITY_MATCH`) | `FLAG_KEYS`, `OBJECT_KEYS`, `COND_RE`, `resolve_condition` (section "Match block") | `test_resolve_condition_cases` passes |
| 11 | same | `d1amenbuild` | `build` and `SPEC` (section "Build and spec") | `test_amenity_node_contract` passes |
| 12 | tests/test_poi_amenity_contract.py | the 11 tests | Per "Verification" | all pass |
| 13 | docs/context/01_DATA_MODEL.md | §6 table, §6.1 table | Add an N7 `slv_poi_amenity` row and a `ref_dictionary_amenities` row | new rows only |
| 14 | docs/context/CTRL_TABLES_CONTEXT.md | `PL_VV_TRANS_SLV_TO_SLV_1H` block | Add the `slv_poi_amenity` src table and the setup precondition | new rows only |

### Order and stop points
1. Q4 is recorded: F&B sector is `f_n_b`. Continue.
2. Main replaces `scope.files` with the 5 paths in edit rows 1–14 and drops `notebooks/NB_CREATE_DDL.ipynb`.
3. Edit row 1. Run the parser and compare against the pinned counts and the 27 matchable conditions. STOP if they differ (evidence: post the parser output). Do not adjust the pins.
4. Edit rows 2–8, then 9–11, then 12.
5. Run the local tests and `vv.py verify`. Edit rows 13–14.
6. STOP (user, Fabric DEV):
   1. Confirm that the `slv_poi_entity` edges exist.
   2. Run setup with `p_apply=false`, then `true`.
   3. Run the node with `DRY_RUN`.
   4. Run NB_00 for `PL_VV_TRANS_SLV_TO_SLV_1H`.
   5. Run the 4 "Runtime checks"; each must return 0.
7. Main lists mapping defects D1–D5 in `decision.md` as a follow-up for the mapping owner. They do not block.

### Tests and verification
- `python -m pytest tests/test_poi_amenity_contract.py -q`
- `python -m pytest tests -q`
- `python scripts/vv.py verify 20261016-ref-amenities-poi-amenity`
- Tests:
  - `test_seed_matches_mapping_file`
  - `test_seed_counts`
  - `test_seed_excludes_placeholders`
  - `test_seed_sectors_groups`
  - `test_seed_sectors_in_entity_vocabulary`
  - `test_hoac_split_same_amenity`
  - `test_resolve_condition_cases`
  - `test_flag_keys_match_registry`
  - `test_matchable_conditions_pinned`
  - `test_amenity_node_contract`
  - `test_setup_contract`
- Fabric DEV: the SQL in the full document under "Runtime checks (Fabric DEV; user)".

### Read only if needed
- "Q4: sector code for F&B" → stop 1
- "Parser rules (test `parse_mapping`, the source of `SEED_ROWS`)" → rows 1, 3
- "Matchable conditions (27, pinned by test)" → rows 1, 12
- "Mapping defects (non-blocking; for the mapping owner)" → stop 7
- "Implementation plan" → "Setup notebook cells (`NB_SETUP_POI_AMENITY`)" → rows 2–8
- "Implementation plan" → "DDL" → row 5
- "Implementation plan" → "Match block (`d1amenmatch`)" → row 10
- "Implementation plan" → "Build and spec (`d1amenbuild`)" → row 11
- "Implementation plan" → "Docs" → rows 13–14
- "Ordering", "Partial failure", "Retry and recovery" → rows 4, 7, 11
- "Alternatives and selected trade-offs" → reviewer questions on placement, key, and matching
- "Verification" → row 12, stop 6

# Architecture: 20261016-ref-amenities-poi-amenity

Dictionary `lh_vv_silver.dbo.ref_dictionary_amenities` and silver node `lh_vv_silver.dbo.slv_poi_amenity`.

Q4 is recorded: F&B is `f_n_b`. No runtime evidence is missing. The source grain and JSON shape come from the repository:

- `slv_3p_poi_amenity` has one row per `poi_id`. It is an upsert-only DOC table: `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, table list.
- `source_flags_json` is built by `JSON_PICK`. Its shape is `{"flags":{<23 booleans>}, "parkingOptions":{..}|null, "paymentOptions":..., "accessibilityOptions":..., "evChargeOptions":..., "fuelOptions":...}`. A key appears only when the raw document has it, and JSON null is kept. Sources: `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` `json_pick_sql` / `_json_piece`, `notebooks/NB_CREATE_DDL.ipynb` cell `e9c137c5…` (`TABLE_CONFIGS_3P`, `slv_3p_poi_amenity`), and `docs/context/3p-google/amenity-l1-demo.md`.
- `slv_poi_entity` has one row per `poi_id`, with a non-null `business_sector` (fallback `other`). It is a RECOMPUTE node in `PL_VV_TRANS_SLV_TO_SLV_1H`: `notebooks/NB_SLV_POI_ENTITY.ipynb` cell `b1entitybuild`.

## Q4: sector code for F&B

Decided 2026-10-16. `notebooks/NB_SETUP_POI_ENTITY.ipynb` cell `a1setupseed` has `SEED_SECTORS` = accommodation, `f_n_b`, spa_n_wellness, shopping_n_retail, attraction, vehicle_rental, other. Section 2.2 of the amenity mapping is seeded as `f_n_b`. The dictionary join uses that code directly. There is no alias.

## Scope

- New manual setup notebook `notebooks/NB_SETUP_POI_AMENITY.ipynb`. It contains DDL for both tables, an insert-only seed of the dictionary, and the three edges of `slv_poi_amenity` in `PL_VV_TRANS_SLV_TO_SLV_1H`.
- New node notebook `notebooks/NB_SLV_POI_AMENITY.ipynb`. It is RECOMPUTE with MERGE through `NB_LIB_TRANSFORM_SLV_GLD`.
- New test `tests/test_poi_amenity_contract.py`. It runs without Spark.
- Doc rows in `docs/context/CTRL_TABLES_CONTEXT.md` and `docs/context/01_DATA_MODEL.md`.
- Scope change: `task-state.yaml` `scope.files` currently lists only `notebooks/NB_CREATE_DDL.ipynb`. This design does not edit that file. Main replaces the scope with the five paths above before editing.

## Non-goals

- No `business_category` in either table. No rename of `slv_poi_entity` sectors. No change to `NB_SETUP_POI_ENTITY`, `NB_SLV_POI_ENTITY`, or `NB_CREATE_DDL`.
- No matching from `types[]`, `amenity_schema_json`, or `ext_attributes_json`. Partner rows are seeded but never matched by this node.
- No edits to `mapping_amenities.md`. Its defects are listed under "Mapping defects" for the mapping owner.
- No pipeline JSON and no schedule. `PL_VV_TRANS_SLV_TO_SLV_1H` stays manual.

## Alternatives and selected trade-offs

1. **Where the DDL and seed live.**
   - Selected: `NB_SETUP_POI_AMENITY`. `02_NAMING_CONVENTION.md` defines `NB_SETUP_<LUỒNG>` as the one-shot notebook for "create + seed ref, edges", and `NB_SETUP_POI_ENTITY` is the direct precedent.
   - Rejected: `NB_CREATE_DDL` (triage scope). It owns the ctrl tables, registry, and APPEND gold DDL. Adding a flow-specific ref seed and edges there mixes owners and makes it heavier to rerun.
2. **Seed source.**
   - Selected: a literal `SEED_ROWS` in the notebook, plus a test that rebuilds it from `mapping_amenities.md` and asserts equality.
   - Rejected: parsing the markdown at runtime. Fabric notebooks cannot read the repo `docs/`.
3. **Condition semantics.**
   - Selected: the literal request rule. A row is matchable only when it is a single path, ` = `, and `true` or `false`. A bare path, a comma list, `types[]`, or prose is seeded and never matches.
   - Rejected: a liberal rule (bare path means `= true`, split on commas). It invents semantics. It also creates a key collision: section 2.3 has `goodForChildren` twice ("Good for Children" and "Family Friendly") in the one group `facilities_and_services`, which breaks the Q3 key.
   - This choice is consistent with `decision.md` "Giả định còn lại" bullets 3–5.
4. **Matching engine.**
   - Selected: explode `source_flags_json` twice into (`poi_id`, `_path`, `_v`), then an equi-join to a broadcast condition frame on (`business_sector`, `_path`, `_v`). Null objects explode to nothing. `true` never equals `false` or null.
   - Rejected: `get_json_object` with a per-row dynamic path (per-row path parsing, cross product per sector). Also rejected: a Python UDF (serialization cost, harder to review).
5. **Condition resolution.**
   - Selected: a pure Python `resolve_condition` in a marked block of the node, applied to the collected dictionary. The dictionary is small, and the test executes the block.
   - Rejected: a regex in Spark SQL. It cannot be tested locally because there is no pyspark in `tests/`.
6. **Dictionary key and write.**
   - Selected: an insert-only MERGE on (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`). `amenity` must be in the key because the duplicate `goodForChildren` pair in 2.3 collides on four columns. An insert-only write protects operator edits such as `is_active = false`, and the setup reports drift as in the sibling.
   - Rejected: an upsert. It silently overwrites manual deactivation.
7. **`slv_poi_amenity` DDL.**
   - Selected: an explicit `CREATE TABLE IF NOT EXISTS` in setup with the six business columns plus the lib's four technical columns, and the same types the lib expects. `ensure_target` then sees no drift.
   - Rejected: lib auto-create only. The request asks for DDL, and NOT NULL on the key columns is wanted.
   - Pre-creating does not cause `NO_DATA`, because edges that have never been read are New Edges (lib header §, "New Edge khi: chưa đọc lần nào").

## Invariants

1. `ref_dictionary_amenities` has exactly the columns `source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`, `amenity_vi`, `is_active`, `updated_at`. `slv_poi_amenity` has exactly `poi_id`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`, `amenity_vi`, plus the lib technical columns `row_hash`, `created_at`, `updated_at`, `deleted_at`. Neither table has `business_category` or a boolean value column.
2. Seed rows are unique on (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`).
3. Active matchable `google` rows are unique on (`business_sector`, `amenity_group`, `amenity_raw`). The node blocks with `QualityGateError` before any write when this fails.
4. `slv_poi_amenity` live rows are unique on (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). A row exists only if `source_flags_json` has the resolved path with exactly the right-hand literal.
5. `slv_poi_amenity.business_sector` is the `slv_poi_entity` value for that `poi_id` (Q1). A POI that is not in live `slv_poi_entity` produces no rows.
6. No row is created for an unmatched flag, a null object, a `false` value against a `= true` condition, or a non-matchable dictionary row. There is no `other` row.
7. No seed value is in SKIP: `Bổ sung sau`, `Fallback`, `Không có field`, `Không có field riêng`, or an empty cell. Section `accomodation` is seeded as `accommodation`, and `f_n_b` is seeded per Q4.
8. Every dictionary `business_sector` is in `NB_SETUP_POI_ENTITY.SEED_SECTORS` (option A).
9. `FLAG_KEYS` and `OBJECT_KEYS` in the node equal the `JSON_PICK` members of `source_flags_json` in `NB_CREATE_DDL`.
10. A setup run with `p_apply = "false"` writes nothing.

## State ownership

| State | Owner | Writer |
|---|---|---|
| `ref_dictionary_amenities` | this task | `NB_SETUP_POI_AMENITY` (insert-only). Operator `UPDATE is_active` is allowed. |
| `slv_poi_amenity` | this task | `NB_SLV_POI_AMENITY` through `run_node` only |
| 3 edges `* -> slv_poi_amenity` in `ctrl_mng_pipeline_config` | this task | `NB_SETUP_POI_AMENITY` |
| `ctrl_mng_watermark`, `ctrl_log_run` | NB_00 | unchanged |
| `ctrl_log_table_run` row | lib | `run_node` |
| `slv_poi_entity` and its 2 edges | other flow | read-only here |
| `slv_3p_poi_amenity` | 3P extract | read-only here |

## Grain and keys

- Dictionary: one row per (`source_name`, `business_sector`, `amenity_group`, `amenity_raw`, `amenity`).
- `slv_poi_amenity`: one row per (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`), which is the Q3 key and the `NodeSpec.pk`. The values are `amenity` and `amenity_vi`.
- Proof of uniqueness: `poi_id` is unique in both inputs. Flattened paths are unique per POI because the map keys are unique and the `flags.` and `<object>.` prefixes are disjoint. Condition keys are unique by invariant 3, and each condition maps to one (`_path`, `_v`). The lib exit QG also blocks a null or duplicate pk.
- The expected seed size comes from the mapping file and the parser rules below:
  - `partner` 74 and `google` 78 rows, 152 in total.
  - By sector: accommodation P22/G29, F&B P18/G30, attraction P22/G16, shopping_n_retail P12/G3.
  - Matchable `google` conditions: 27, listed under "Matchable conditions".

## Parser rules (test `parse_mapping`, the source of `SEED_ROWS`)

1. Section line `^####\s+\*\*2\.(\d)`. The sectors are 1 `accommodation`, 2 `f_n_b` (Q4), 3 `attraction`, 4 `shopping_n_retail`.
2. Only lines starting with `|` are table rows. Cells come from `strip().strip("|").split("|")`. Keep the raw text to detect bold.
3. Clean each cell in this order:
   1. Remove `**` and backticks.
   2. `\[` becomes `[` and `\]` becomes `]`.
   3. NBSP becomes a space.
   4. `\s+` becomes one space.
   5. `\s*=\s*` becomes ` = `.
   6. Strip. An empty result becomes None.
4. Skip separator rows, where every cell is None or dashes.
5. A row containing `Google Place API` is the header. Map columns by substring: `Partner Portal Enum` is partner, `Google Place API` is google, `(VI)` is vi, `(EN)` is en.
6. A row whose first raw cell starts with `**` and whose other cells are all None is a group label. The cleaned text becomes `amenity_group` until the next label. The repeated label in 2.3 yields the same group.
7. Data row, partner cell: if not None and not in SKIP, emit `("partner", sector, group, partner, en, vi)`.
8. Data row, google cell: if not None and not in SKIP, split it on `\s+hoặc\s+`. For each part, apply `strip().rstrip(",").strip()` and drop it if empty or in SKIP. Emit `("google", sector, group, part, en, vi)`. Commas are not split.
9. Order follows the markdown. Within a markdown row, the partner row comes before the google rows.

Main generates `SEED_ROWS` by running this parser and pastes the literal into cell `c1setupseed`. If the parser's counts differ from those in "Grain and keys", stop and report. Do not edit the pinned counts to fit.

## Matchable conditions (27, pinned by test)

- `accommodation`/`general_amenities` (14):
  - `parkingOptions.freeStreetParking = true`, `parkingOptions.valetParking = true`, `parkingOptions.freeGarageParking = true`, `parkingOptions.paidGarageParking = true`
  - `outdoorSeating = true`, `restroom = true`, `goodForChildren = true`, `goodForGroups = true`, `liveMusic = true`
  - `parkingOptions.freeParkingLot = true`, `parkingOptions.paidParkingLot = true`, `servesCocktails = true`
  - `parkingOptions.freeElectricVehicleParking = true`, `parkingOptions.paidElectricVehicleParking = true`
- `accommodation`/`accessibility` (5): `accessibilityOptions.wheelchairAccessibleSeating = true`, `...Elevator = true`, `...Entrance = true`, `...Restroom = true`, `...Parking = true`. Each is the full `accessibilityOptions.wheelchairAccessible<X> = true` path.
- `f_n_b`/`space_and_services` (6): `restroom = true`, `goodForChildren = true`, `accessibilityOptions.wheelchairAccessibleEntrance = true` (after the ` = ` normalization), `goodForWatchingSports = true`, `liveMusic = true`, `dineIn = true`.
- `attraction`/`facilities_and_services` (2): `parkingOptions.freeParkingLot = true`, `parkingOptions.paidParkingLot = true`.
- `shopping_n_retail`: none.

## Mapping defects (non-blocking; for the mapping owner)

Each of these is seeded verbatim and never matches:

- D1: 2.2 `outdoorSeating = true = true`.
- D2: comma lists `parkingOptions.freeParkingLot, parkingOptions.paidParkingLot = true` (2.2) and `parkingOptions.freeParkingLot, parkingOptions.paidParkingLot` (2.4).
- D3: bare paths in 2.3 (`restroom`, `goodForChildren` twice, `liveMusic`, `goodForGroups`, three `accessibilityOptions.*`) and in 2.4 (`delivery`, `paymentOptions.acceptsCreditCards`). If the owner adds `= true` to both `goodForChildren` rows in 2.3, invariant 3 fails. The owner must first choose one amenity for that condition.
- D4: in the 2.1 Bar row, `hoặc` is missing before `servesBeer = true`.
- D5: `serves_meals` is not a key in `source_flags_json`.

A corrected mapping is re-seeded as new keys, because the seed is insert-only. Stale non-matchable rows are harmless. The operator may set them `is_active = false`.

## Ordering

1. The other flow has run `NB_SETUP_POI_ENTITY`: `slv_poi_entity` edges are active in `PL_VV_TRANS_SLV_TO_SLV_1H`. `NB_SETUP_POI_AMENITY` checks this and fails with `ConfigError` before it writes any edge.
2. Setup steps, in order:
   1. Validate the seed.
   2. Plan, and exit if `p_apply` is false.
   3. Create both tables and assert their schemas.
   4. Seed MERGE.
   5. Write the edges.
3. The node runs inside the pl DAG. `slv_poi_entity` is a parent because it is the `src_tbl` of an edge in the same pl, so `build_dag` orders entity before amenity, and a failed or skipped entity makes amenity `SKIPPED`. The lib ignores config `priority`, so the level comes from the DAG. Use `priority = 1` as in the sibling.

## Transaction and commit boundaries

- Setup: each statement is its own Delta commit. `CREATE TABLE` (x2) is idempotent. The seed MERGE is one atomic commit. The edges MERGE into `ctrl_mng_pipeline_config` is one atomic commit after the duplicate, owner, and entity-edge prechecks. Post-checks run after each commit and raise on violation.
- Node: `build`, then the exit QG, then one MERGE commit into `slv_poi_amenity`, then one append to `ctrl_log_table_run`. NB_00 advances the watermark only after node SUCCESS. A QG failure writes nothing.

## Idempotency

- Rerunning the seed inserts 0 rows because the anti-join on the 5-column key is empty, and `updated_at` of existing rows is unchanged. Edges are MERGEd on (`pl_name`, `src_tbl`, `trg_tbl`) and normalized, so they are not duplicated.
- The node recomputes the whole output from pinned inputs. The `row_hash` MERGE gives zero diff on an unchanged rerun.
  - A flag that turns false soft-deletes its row (`deleted_at = now`). Turning true again clears `deleted_at`.
  - A sector change soft-deletes the old-sector keys and inserts the new ones.

## Concurrency

- NB_00 holds the pl lock, and a manual node RUN takes the lock (lib step 2). External inputs are read with `VERSION AS OF` the pinned versions, so an extract or seed writing at the same time does not tear a run.
- Run setup when `PL_VV_TRANS_SLV_TO_SLV_1H` is idle. The edges MERGE uses `with_retry` against concurrent writers of `ctrl_mng_pipeline_config`, as in the sibling.

## Retry and recovery

- Setup: rerun the notebook. Every step is idempotent, and `with_retry` wraps the seed MERGE and the edges.
- Node: a FAILED run does not advance the watermark, so the next NB_00 run recomputes. If the run crashes after the MERGE and before the log, the next run's diff is 0.
- Pinned `slv_3p_poi_amenity` can include a POI that the pinned `slv_3p_poi` (and so `slv_poi_entity`) does not have yet. The POI then has no rows for that run. The next entity change marks amenity as a child to recompute (`plan_run`: dirty node plus its children), so the gap lasts one run. It shows in the `pois_without_entity` metric.

## Partial failure

| Failure point | State | Action |
|---|---|---|
| After DDL, before seed | empty tables, no edges | rerun setup |
| After seed, before edges | dictionary seeded, node not wired | rerun setup |
| Entity edges missing | `ConfigError`, no edge written | run `NB_SETUP_POI_ENTITY`, then rerun |
| Node QG (duplicate condition key, no matchable condition, zero output with joined POIs > 0) | target untouched | fix the dictionary (`is_active`) or investigate the JSON shape, then rerun |
| Input empty | `required_inputs` gives FAILED, no mass soft delete | fix upstream |

The zero-output guard trades a possible false block on a tiny DEV dataset for protection against mass soft deletes when the `source_flags_json` shape drifts, for example if `flags` is renamed.

## Observability

- Node `ctx.metrics`, written to `ctrl_log_table_run`:
  - `src_rows`
  - `pois_joined`
  - `pois_without_entity`
  - `unparsed_json` (non-null and `from_json` map is null)
  - `dict_google_active`
  - `conditions_matchable`
  - `conditions_skipped`
  - `rows`
- Setup prints and exits with JSON:
  - plan mode: `{status: PLAN, google, partner, matchable_hint: n/a, missing_keys, entity_edges_ok, planned_edges}`
  - run mode: `{status: SUCCESS, inserted, drift, edges_inserted}`
  - `drift` counts seed keys whose `amenity_vi` differs or whose `is_active` is not true.

## Security

Not applicable: the data is boolean amenity flags and static labels. There is no personal data, and there are no secrets. The sample JSON is not stored.

## Rollout

1. Q4 is recorded. Main updates `scope.files`.
2. Implement, then run local tests and `vv.py verify`.
3. In Fabric DEV, the user:
   1. Confirms that `slv_poi_entity` exists and its edges are active.
   2. Runs `NB_SETUP_POI_AMENITY` with `p_apply=false`, then with `true`.
   3. Runs `NB_SLV_POI_AMENITY` with `p_mode=DRY_RUN`.
   4. Runs NB_00 for `PL_VV_TRANS_SLV_TO_SLV_1H`.
   5. Runs the checks in "Runtime checks".

## Rollback and forward recovery

- Disable: `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0 WHERE pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H' AND trg_tbl = 'slv_poi_amenity'`. Entity runs are unaffected.
- Bad output: `RESTORE TABLE lh_vv_silver.dbo.slv_poi_amenity TO VERSION AS OF <v>`, or fix the dictionary and rerun. The recompute converges.
- Removing the tables (`DROP TABLE`) needs `runtime-runbook.md` steps first (AGENTS §8). Forward recovery is to rerun setup and then the node.
- Bad dictionary row: `UPDATE ... SET is_active = false`. The next run soft-deletes the affected keys.

## Implementation plan

### Setup notebook cells (`NB_SETUP_POI_AMENITY`)

| Cell id | Content |
|---|---|
| `c1setupmd` | Vietnamese title. Insert-only. `p_apply` defaults to `false`. |
| `c1setupparam` | `p_apply = "false"` |
| `c1setuprun` | `%run NB_LIB_TRANSFORM_SLV_GLD` |
| `c1setupseed` | `# BEGIN_AMENITY_SEED` … `# END_AMENITY_SEED`: `SEED_SECTORS = ("accommodation", "f_n_b", "attraction", "shopping_n_retail")`, `SEED_GROUPS` (5 labels), `SEED_SKIP` (4 values), `SEED_ROWS`, and `validate_seed(rows)`. `validate_seed` checks: 5-column uniqueness, source in {google, partner}, sector in `SEED_SECTORS`, group in `SEED_GROUPS`, `amenity_raw` non-empty and not in SKIP, `amenity` non-empty. |
| `c1setupplan` | Mirror `a1setupplan`. Seed schema `source_name string, business_sector string, amenity_group string, amenity_raw string, amenity string, amenity_vi string`. Temp view `seed_amenities`. `missing_keys` is an anti-join on the 5-column key. `entity_edges_ok` is the count of active `PL_VV_TRANS_SLV_TO_SLV_1H` edges with `trg_tbl='slv_poi_entity'`, which must be 2. Exit when not applying. |
| `c1setupddl` | DDL (below) and an `EXPECTED` schema assertion for both tables, as in `a1setupddl`. |
| `c1setupmerge` | Mirror `a1setupmerge`. `ON` the 5-column key. `WHEN NOT MATCHED THEN INSERT` with `is_active = true` and `updated_at = current_timestamp()`. No `WHEN MATCHED`. Duplicate check, missing-after check, and `DRIFT` on `amenity_vi` / `is_active`. |
| `c1setupedges` | Mirror `a1setupedges` `_write_edges` for `trg_tbl = 'slv_poi_amenity'` and the src list `(1,'slv_3p_poi_amenity'), (2,'slv_poi_entity'), (3,'ref_dictionary_amenities')`, all `lh_vv_silver.dbo`, `RECOMPUTE`, `priority 1`. First, if `entity_edges_ok != 2`, raise `ConfigError("slv_poi_amenity: chưa có cạnh slv_poi_entity, chạy NB_SETUP_POI_ENTITY trước")`. Expect counts `{3 src: 1 each}`. |
| `c1setupexit` | Summary JSON. |

### DDL

```sql
CREATE TABLE IF NOT EXISTS lh_vv_silver.dbo.ref_dictionary_amenities (
    source_name     STRING NOT NULL,
    business_sector STRING NOT NULL,
    amenity_group   STRING NOT NULL,
    amenity_raw     STRING NOT NULL,
    amenity         STRING NOT NULL,
    amenity_vi      STRING,
    is_active       BOOLEAN,
    updated_at      TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true');

CREATE TABLE IF NOT EXISTS lh_vv_silver.dbo.slv_poi_amenity (
    poi_id          STRING NOT NULL,
    business_sector STRING NOT NULL,
    amenity_group   STRING NOT NULL,
    amenity_raw     STRING NOT NULL,
    amenity         STRING,
    amenity_vi      STRING,
    row_hash        STRING,
    created_at      TIMESTAMP,
    updated_at      TIMESTAMP,
    deleted_at      TIMESTAMP
) USING DELTA
TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true');
```

### Node notebook cells (`NB_SLV_POI_AMENITY`)

| Cell id | Content |
|---|---|
| `d1amenmd` | Vietnamese title |
| `d1amenparam` | The same eight parameters as `b1entityparam` |
| `d1amenrun` | `%run NB_LIB_TRANSFORM_SLV_GLD` |
| `d1amenmatch` | Match block (below) |
| `d1amenbuild` | Build and spec (below) |
| `d1amenres` | `RES = run_node(SPEC, ...)`, same as `b1entityres` |
| `d1amenexit` | `notebookutils.notebook.exit(finish_node(RES))` |

### Match block (`d1amenmatch`)

```python
# BEGIN_AMENITY_MATCH
import re

FLAG_KEYS = ("servesBreakfast", "servesBrunch", "servesLunch", "servesDinner", "servesBeer", "servesWine",
             "servesCocktails", "servesDessert", "servesCoffee", "servesVegetarianFood", "allowsDogs",
             "goodForChildren", "goodForGroups", "goodForWatchingSports", "liveMusic", "menuForChildren",
             "outdoorSeating", "restroom", "reservable", "takeout", "delivery", "dineIn", "curbsidePickup")
OBJECT_KEYS = ("parkingOptions", "paymentOptions", "accessibilityOptions", "evChargeOptions", "fuelOptions")
COND_RE = re.compile(r"([A-Za-z][A-Za-z0-9]*)(?:\.([A-Za-z][A-Za-z0-9]*))? = (true|false)")


def resolve_condition(raw):
    """Điều kiện -> (path trong source_flags_json, giá trị) hoặc None. Ví dụ outdoorSeating = true -> (flags.outdoorSeating, true)."""
    m = COND_RE.fullmatch((raw or "").strip())
    if m is None:
        return None
    head, leaf, value = m.groups()
    if leaf is None:
        return (f"flags.{head}", value) if head in FLAG_KEYS else None
    if head == "flags":
        return (f"flags.{leaf}", value) if leaf in FLAG_KEYS else None
    return (f"{head}.{leaf}", value) if head in OBJECT_KEYS else None
# END_AMENITY_MATCH
```

### Build and spec (`d1amenbuild`)

```python
from collections import Counter

GOOGLE = "google"
COND_SCHEMA = ("business_sector string, amenity_group string, amenity_raw string, amenity string, "
               "amenity_vi string, _path string, _v string")
OUT_COLS = ("poi_id", "business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_vi")


def build(ctx: NodeContext) -> DataFrame:
    # Từ điển google active -> điều kiện khớp được. Điều kiện không đúng dạng path = true/false thì bỏ qua.
    rows = (ctx.input("dict")
            .where((F.lower(F.trim("source_name")) == GOOGLE) & (F.col("is_active") == F.lit(True)))
            .select("business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_vi").collect())
    conds = [tuple(r) + hit for r in rows if (hit := resolve_condition(r.amenity_raw))]
    dup = sorted(k for k, n in Counter(c[:3] for c in conds).items() if n > 1)
    if dup:
        raise QualityGateError(f"ref_dictionary_amenities: điều kiện google trùng khoá {dup}")
    if not conds:
        raise QualityGateError("ref_dictionary_amenities: không có điều kiện google khớp được")
    cond = F.broadcast(spark.createDataFrame(conds, COND_SCHEMA))
    # source_flags_json = {"flags": {...}, "parkingOptions": {...} | null, ...}; object null -> không nổ dòng.
    src = ctx.input("amenity").select("poi_id", "source_flags_json")
    top = src.select("poi_id", F.explode(F.from_json("source_flags_json", "map<string,string>")).alias("_top", "_obj"))
    flat = (top.select("poi_id", "_top", F.explode(F.from_json("_obj", "map<string,string>")).alias("_leaf", "_v"))
               .select("poi_id", F.concat_ws(".", "_top", "_leaf").alias("_path"), "_v"))
    ent = ctx.input("entity").select("poi_id", "business_sector")
    out = flat.join(ent, "poi_id").join(cond, ["business_sector", "_path", "_v"]).select(*OUT_COLS)
    src_rows = src.count()
    unparsed = src.where(F.col("source_flags_json").isNotNull()
                         & F.from_json("source_flags_json", "map<string,string>").isNull()).count()
    joined = src.join(ent, "poi_id").count()
    n = out.count()
    ctx.metrics.update(src_rows=src_rows, pois_joined=joined, pois_without_entity=src_rows - joined,
                       unparsed_json=unparsed, dict_google_active=len(rows),
                       conditions_matchable=len(conds), conditions_skipped=len(rows) - len(conds), rows=n)
    if joined and not n:
        raise QualityGateError("slv_poi_amenity: có POI join entity nhưng không khớp điều kiện nào")
    return out


SPEC = NodeSpec(
    trg_tbl="slv_poi_amenity",
    inputs={"amenity": "slv_3p_poi_amenity", "entity": "slv_poi_entity", "dict": "ref_dictionary_amenities"},
    pk=("poi_id", "business_sector", "amenity_group", "amenity_raw"),
    build=build,
    required_inputs=("amenity", "entity", "dict"),
    write_mode="MERGE",
)
```

### Docs

- `01_DATA_MODEL.md` §6: add row N7 `slv_poi_amenity`, with the key, the 3 inputs, and the match rule. §6.1: add the `ref_dictionary_amenities` row with the 5-column key and "152 rows: 78 google + 74 partner, seed insert-only from `mapping_amenities.md`".
- `CTRL_TABLES_CONTEXT.md`, under the `PL_VV_TRANS_SLV_TO_SLV_1H` block: add a `slv_poi_amenity` sub-table with its 3 `src_tbl`, seeded by `NB_SETUP_POI_AMENITY`, and the precondition that entity edges exist.
- Both files already have uncommitted edits from the other flow. Edit only the new rows.

## Verification

### Local

`python -m pytest tests/test_poi_amenity_contract.py -q`, then `python -m pytest tests -q`, then `python scripts/vv.py verify 20261016-ref-amenities-poi-amenity`.

The test module reuses the sibling's helpers `_nb` and exec-between-markers. Tests:

- `test_seed_matches_mapping_file`: `SEED_ROWS == parse_mapping(md)`, and `validate_seed` passes.
- `test_seed_counts`: partner 74, google 78, and the per-sector counts from "Grain and keys".
- `test_seed_excludes_placeholders`: no SKIP value in any row. `Rooftop Bar` yields only a partner row. `parkingOptions.freeStreetParking = true` is exactly one google row, at (`accommodation`, `general_amenities`).
- `test_seed_sectors_groups`: sectors = {accommodation, f_n_b, attraction, shopping_n_retail}. No `accomodation` and no `fnb`. All 2.3 rows are in `facilities_and_services`.
- `test_seed_sectors_in_entity_vocabulary`: sectors ⊆ `SEED_SECTORS` from `NB_SETUP_POI_ENTITY`.
- `test_hoac_split_same_amenity`: accommodation Parking gives 2 google rows, and EV gives 3. Each group has identical (`amenity`, `amenity_vi`).
- `test_resolve_condition_cases`:
  - `parkingOptions.freeStreetParking = true` → (`parkingOptions.freeStreetParking`, `true`)
  - `outdoorSeating = true` → `flags.outdoorSeating`
  - `evChargeOptions.x = true` → resolved
  - None for each of: `outdoorSeating = true = true`, `restroom`, `types[] = swimming_pool`, `serves_meals = true`, the 2.2 comma cell, `foo.bar = true`
- `test_flag_keys_match_registry`: regex-extract the `JSON_PICK` arg of `source_flags_json` from `NB_CREATE_DDL.ipynb`. It must equal `FLAG_KEYS` and `OBJECT_KEYS`.
- `test_matchable_conditions_pinned`: {(sector, group, raw) for google seed rows where `resolve_condition` is set} equals the 27 listed, with no duplicates.
- `test_amenity_node_contract`: the source contains:
  - `trg_tbl="slv_poi_amenity"`
  - the three input pairs
  - `pk=("poi_id", "business_sector", "amenity_group", "amenity_raw")`
  - `write_mode="MERGE"`
  - `required_inputs=("amenity", "entity", "dict")`
  - `"map<string,string>"`
  - `F.broadcast(`
  
  It does not contain `business_category`, `explode_outer`, or `get_json_object`.
- `test_setup_contract`:
  - `p_apply = "false"`.
  - The two DDL blocks have exactly the listed columns and no `business_category`.
  - The seed MERGE has `WHEN NOT MATCHED` and no `WHEN MATCHED`.
  - The edges block contains `PL_VV_TRANS_SLV_TO_SLV_1H`, `RECOMPUTE`, the 3 src names, and the entity precheck message.

### Runtime checks (Fabric DEV; user)

Each check must return 0:

1. Duplicate live keys: `SELECT count(*) FROM (SELECT poi_id, business_sector, amenity_group, amenity_raw FROM lh_vv_silver.dbo.slv_poi_amenity WHERE deleted_at IS NULL GROUP BY 1,2,3,4 HAVING count(*) > 1)`.
2. Missing positives:
   - `SELECT count(*) FROM lh_vv_silver.dbo.slv_3p_poi_amenity a JOIN lh_vv_silver.dbo.slv_poi_entity e USING (poi_id)`
   - `LEFT ANTI JOIN (SELECT poi_id FROM lh_vv_silver.dbo.slv_poi_amenity WHERE deleted_at IS NULL AND amenity_raw = 'parkingOptions.freeStreetParking = true') s USING (poi_id)`
   - `WHERE e.business_sector = 'accommodation' AND get_json_object(a.source_flags_json, '$.parkingOptions.freeStreetParking') = 'true'`
3. False positives: count live rows with `amenity_raw = 'parkingOptions.freeParkingLot = true'` whose source has `get_json_object(... '$.parkingOptions.freeParkingLot') <> 'true'` or null.
4. Live rows whose `amenity_raw` starts with `evChargeOptions.`.
