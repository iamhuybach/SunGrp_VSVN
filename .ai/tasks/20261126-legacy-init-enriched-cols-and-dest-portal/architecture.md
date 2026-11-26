RESULT: PASS

## Main brief

### Decision
I'm returning `RESULT: PASS`. G1–G4 are closed by P-DEST, P-AI and P-LEGDEST, and by ledger decisions D-DEST-BACKFILL, D-LEGACY-DEST and D-G4. Conflict 3 is closed too: `NB_ENR_POI_INFO` reads only `poi_id` from the destination table.
- **Silver**: a new patch cell `destportalpy` holds the extract lock. It checks the registry, the schema and the per-row OLD/NEW state, then runs `ALTER … AFTER destination_id` and one backfill MERGE keyed on each row's exact producing bronze event.
- **Extract**: gains the `strapi_document_id` projection and a `PATCH_COLS` guard.
- **Init**: the four info columns come from the `vi_key` row of `ai_enriched_poi`. `story` and `local_tips` come from `(legacy_poi_id, lang)`. A new guard stops RUN if LEGACY_INIT `destination_id` would change.

### Invariants Main must preserve
- `destination_id`, `destination_portal_id` and `destination_name` come from one `from_json(block, DEST_ELEM_SCHEMA)` array. They have the same length, order and null positions. All three are NULL when the block is NULL.
- `destination_portal_id` appears only in silver `TABLE_SPECS`, `init_cfg_enr`, `enrbrzcfgpy`, `enr04` and `destportalpy`. It is never in gold specs, `DEST_COLS`, PostgreSQL, entities, or `mapping_gld_srv_poi_info.md`.
- `NB_GLD_SRV_POI_INFO`, `enrbrzpy`, `oldpricepy` and every other old patch cell stay byte-identical.
- `destportalpy` stops before any write if any of these is non-zero: `no_event_n`, `dup_payload_n`, `name_bad_n`, `drift_n`, `strapi_missing_n`, `key_n != silver_n`. It also stops if `old_n + new_n != silver_n`. A rerun updates 0 rows.
- The extract raises `ConfigError("… chạy destportalpy")` when the registry has `destination_portal_id` and the table does not, and it does so before `ensure_target`.
- The init joins `story` and `local_tips` on `ai.poi_id = mp.legacy_poi_id AND ai.lang = mp.lang`, never on `poi_id` alone. The info columns join only through `vi_key` with `ai.lang = 'vi'`.
- The init reads from `OLD`, through `old()` at pins, only `poi_master`, `poi_enrichment_display`, `poi_detail`, `poi_review`, `poi_rating` and `ai_enriched_poi`.
- The new joins leave the `info_src` and `ml_src` row counts unchanged (guards). `story` and `local_tips` are not in `pay`.
- RUN stops on `enriched.decision != OK` before `write_insert_only(MAP_FQ`, and on `destination_changed_n > 0` before the info write.
- Gold types stay as they are: `price_level` INT, `price_min` and `price_max` DECIMAL(18,2).

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| E1 | notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb | `enr04` `ARRAY_PROJECTIONS`, `DEST_ELEM_SCHEMA` | Add the strapi projection, the 3-field schema, and `PATCH_COLS` (§8.1). Update the `part_value` docstring. | literals present |
| E2 | same | `enr08` after the `missing_null` raise | Guard from §8.2, placed before `ensure_target` | text "chạy destportalpy" appears before `ensure_target(` |
| E3 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` `TABLE_SPECS` `slv_enr_poi_destination` | `('destination_portal_id', 'STRING', None)` between `destination_id` and `destination_name` (§8.4) | order is id, portal, name |
| E4 | same | `init_cfg_enr` `TABLE_CONFIGS_ENR` | Three registry entries (§8.3) | equals E5 |
| E5 | notebooks/NB_CREATE_DDL.ipynb | `enrbrzcfgpy` `TABLE_CONFIGS_ENR` | Same text as E4 | equals E4 |
| E6 | same | new markdown `destportalmd` after `oldpricepy` | §8.5 | ids end with `oldpricemd, oldpricepy, destportalmd, destportalpy` |
| E7 | same | new code `destportalpy` | Code in §8.6 plus steps 1–8: lock, registry gate, schema gate, pre-plan gates under `# Dừng trước khi ghi`, touch, ALTER, `mid == pre`, touch, MERGE tagged `DESTPORTAL:`, `# Sau khi ghi` post-check, `finally:` release | E18 test passes |
| E8 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | `lgpmain` preflight `PINS` loop and after the `pm_pin` checks | Add `ai_enriched_poi` to `PINS`. Add the `AI_TYPES` and unique-`poi_id` stops and the target-column stop (§9.1) | all stops come before `EXEC =` |
| E9 | same | `lgpmain` after the `destination` decision raise | `stage = "enriched"` gate (§9.2) | gate index < `write_insert_only(MAP_FQ` |
| E10 | same | `lgpmain` info stage, after `info_src.join(dest_one` | `destination_changed_n` guard (§9.3) | RUN raises if > 0 |
| E11 | same | `lgpmain` info stage, after `n_before = info_src.count()` | `enr_info` via `vi_key` + `single_payload`, left join, summary keys (§9.3) | the existing guard covers it |
| E12 | same | `lgpmain` multi_lang, after the `name_one` join; `lgpmd` | `enr_ml` and `enr_one`, count guard, summary keys (§9.4). One sentence in `lgpmd` (§9.6) | `pay` unchanged |
| E13 | docs/context/mapping_legacy_gold_to_gld_srv.md | §1 table, line 18, row 7; §2 table; line 157 | §10 bullets: 41 and 16 columns, the D-LEGACY-DEST note, the 8-column read list | rows present and renumbered |
| E14 | docs/context/mapping_gld_srv_poi_info.md | §1.1 line 19; §1.2 line 51 | strapi source, 1-1 copy | no `destination_portal_id` in the file |
| E15 | docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md | §4, §5 | three projections; `PATCH_COLS` guard | text present |
| E16 | tests/test_initial_ddl_contract.py | new tests | `test_enr_registry_configs_equal_create_ddl`: ast-select `_enr` and `TABLE_CONFIGS_ENR` from both cells, exec, assert equal. `test_enr_destination_registry_paths`: exec `init_registry_pure` (`BEGIN_REGISTRY_PURE`) and `flatten_table_configs`; assert the paths and that portal's `column_order` is destination_id's + 1. `test_slv_enr_poi_destination_portal_after_id` | pass |
| E17 | tests/test_enr_extract_contract.py | `test_registry_columns_match_model_design`; `test_silver_rewrite_targets_match_initial_ddl`; new test | Assert the strapi projection and the 3-field schema. In the rewrite test, drop `destination_portal_id` from the expected list for the destination table only, and assert it equals `destportalpy` `NEW_COL[0]`. New `test_extract_preflight_patch_cols`: `PATCH_COLS` exists, and the guard comes after `missing_null` and before `ensure_target(` | pass |
| E18 | tests/test_enr_poi_contract.py | new tests | `test_dest_portal_patch_cell`: cell order; `TABLE_COLS` equals `TABLE_SPECS` (name, lowercase base type, nullable); `DEST_ELEM_SCHEMA` equals `enr04`; `REG_WANT` equals the registry; lock id `wm_transform_brz_enrichment_result`; token order `held = True` < `Dừng trước khi ghi` < `ALTER TABLE` < `MERGE INTO` < `Sau khi ghi` < `finally:`; two `_touch_lock()` calls around the ALTER; the MERGE ON has 3 tuple columns and `destination_portal_id IS NULL`; non-comment code has no DROP, DELETE, TRUNCATE, RESTORE, columnMapping, CREATE TABLE, RENAME or overwriteSchema. `test_enr_poi_info_ignores_destination_ids`: `NB_ENR_POI_INFO` `REQUIRED_COLS["destination"] == ("poi_id",)` and `destination_id` does not appear in cell `36415d3b` | pass |
| E19 | tests/test_gld_srv_poi_contract.py; tests/test_srv_poi_serving_contract.py | `test_old_price_story_patch_cell` line 685; new tests | Slice `ids` up to `oldpricepy` before the `[-4:]` check. `test_info_dest_cols_exclude_portal_id` (`DEST_COLS`). `test_destination_portal_id_silver_only`: absent from `gold_tables()`, `pg_tables()`, entities if `SERVICE`, and `mapping_gld_srv_poi_info.md`; present in silver `TABLE_SPECS`; `GOLD_ONLY` unchanged | `test_gold_and_pg_columns_and_types_match` still passes |
| E20 | tests/test_legacy_gold_poi_init_contract.py | new tests | `test_init_enriched_pins_and_types`, `test_init_enriched_gate_before_writes`, `test_init_info_enriched_vi_row` (vi_key join, `'vi'` filter, decimal casts, after `n_before`), `test_init_ml_story_tips_per_lang` (join on legacy_poi_id and lang, not in `pay`, count guard), `test_init_old_tables_allowlist` (the set matched by `old\("(\w+)"\)` equals the six tables), `test_init_destination_unchanged_guard` | pass |

### Order and stop points
1. Implement E1–E5, then E6–E7, then E8–E12, then E13–E15, then E16–E20.
2. Run the pytest command and `python scripts/vv.py verify`. Fix until both PASS. STOP (evidence): save the output.
3. Review by spark-runtime-reviewer and sql-data-reviewer. Handle P0/P1 findings within 2 rounds.
4. STOP (runtime, user, DEV), in this order:
   1. publish the extract;
   2. run `28e2be98`, `0f228dc1`, `enrbrzcfgpy`;
   3. run `destportalpy` (expected `old_n = 19799`, `empty_n = 2`, all gates 0), then rerun it (expect `updated_n = 0`);
   4. extract dry run, then a real run;
   5. GLD_30M;
   6. init PLAN → RUN → RUN, using the original pins plus the printed `ai_enriched_poi` pin.

   Main saves the outputs under `evidence/results/`.
5. STOP (user decision), only if `destination_changed_n > 0` or `enriched.decision != OK`: the user picks the pins or the policy. Do not change the code to get past the gate.

### Tests and verification
- `python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_enr_extract_contract.py tests/test_legacy_gold_poi_init_contract.py tests/test_gld_srv_poi_contract.py tests/test_srv_poi_serving_contract.py -q`
- New tests:
  - `test_enr_registry_configs_equal_create_ddl`
  - `test_enr_destination_registry_paths`
  - `test_slv_enr_poi_destination_portal_after_id`
  - `test_extract_preflight_patch_cols`
  - `test_dest_portal_patch_cell`
  - `test_enr_poi_info_ignores_destination_ids`
  - `test_info_dest_cols_exclude_portal_id`
  - `test_destination_portal_id_silver_only`
  - `test_init_enriched_pins_and_types`
  - `test_init_enriched_gate_before_writes`
  - `test_init_info_enriched_vi_row`
  - `test_init_ml_story_tips_per_lang`
  - `test_init_old_tables_allowlist`
  - `test_init_destination_unchanged_guard`
- Edited tests that must pass: `test_old_price_story_patch_cell`, `test_silver_rewrite_targets_match_initial_ddl`, `test_registry_columns_match_model_design`.
- Existing tests that must still pass: `test_gold_and_pg_columns_and_types_match`, `test_gold_only_columns_stay_out_of_serving`, `test_legacy_upsert_updates_only_legacy_rows`, `test_extract_preflight_retired_and_const_null_columns`.
- `python scripts/vv.py verify` must PASS before review.
- Runtime checks: architecture.md §19.

### Read only if needed
- §0 Verdict and evidence closure → why PASS; Conflict 3
- §3 Invariants → all rows
- §6 Alternatives compared → E7, E11, E17 (why `enrbrzpy` is not edited)
- §7 Ordering, transaction and commit boundaries → E2, E7, stop 4
- §8.1–§8.4 → E1–E5
- §8.5–§8.6 destportalpy → E6, E7, E18
- §9.1–§9.6 Legacy init design → E8–E12, E20
- §10 Docs → E13–E15
- §11–§13 Idempotency, concurrency, retry → E7, E9–E12
- §16–§17 Rollout, rollback → stop 4
- §19 Verification → stops 2, 4

# Architecture: 20261126-legacy-init-enriched-cols-and-dest-portal

## 0. Verdict and evidence closure

Round 1 ended at EVIDENCE_REQUIRED with gaps G1–G4. All four are now closed, and the design is ready to implement.

| Gap | Closed by | Effect on design |
|---|---|---|
| G1: existing silver rows | P-DEST-1 shows `joined_rows = silver_n = 19799`, `no_event_n = 0`, `id_eq_n = name_eq_n = 19799`, `blk_null_n = 0`, `sd_partial_n = 0`, `sd_none_n = 2`. P-DEST-2 shows `elem_null_n = 0` and string ids on every element. Decision D-DEST-BACKFILL picked option B. | The in-place backfill in `destportalpy` (§8.6) goes ahead. The 2 rows with no elements store `[]` in both id columns. |
| G2: meaning of `ai_enriched_poi.poi_id` | P-AI-1 shows `map_hit_n = map_same_lang_n = map_ok_n = 136754` and `new_id_hit_n = 0`. Ledger rows D-INIT-KEY, D-INIT-INFO-VI, D-INIT-ENRICH-ONLY. | The join is `ai.poi_id = map.legacy_poi_id AND ai.lang = map.lang` (§9). |
| G3: id space of LEGACY_INIT `destination_id` | P-LEGDEST-1 shows 24 values, 0 of them portal ids and 1 a strapi id. Decision D-LEGACY-DEST. | The init destination mapping does not change. One doc note is added. A new guard stops any change to init `destination_id` (§9.3). |
| G4: test files outside scope | Decision D-G4. `scope.files` now lists both test files and the extract doc. | Rows E17–E20. |

`model-design.md` conflicts:
- Conflict 1 (where the note goes) and Conflict 2 (malformed `scope.files`) were closed by Main.
- Conflict 3 is closed here. In `NB_ENR_POI_INFO` cell `36415d3b`, `REQUIRED_COLS["destination"] = ("poi_id",)`, and `_present` selects only the key column. The notebook neither unions silver by position nor reads `destination_id`.

Grain, keys, columns and lineage come from `model-design.md` ## Entities and grain, ## Keys, ## Columns and ## Lineage. This design does not change them.

## 1. Scope

- **Extract** (`NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`):
  - `enr04`: add the `strapi_document_id` projection and add `PATCH_COLS`.
  - `enr08`: add a preflight guard.
- **DDL**:
  - `NB_SETUP_INITIAL_DDL` `init_tables`: one row in `TABLE_SPECS`.
  - Registry text for the destination table in `init_cfg_enr` and `NB_CREATE_DDL` `enrbrzcfgpy`.
  - New cell pair `destportalmd` / `destportalpy` appended after `oldpricepy`. It does the ALTER and the backfill.
- **Legacy init** (`NB_SETUP_LEGACY_GOLD_POI` `lgpmain`, `lgpmd`): pinned read of `ai_enriched_poi`, filling 4 info columns and 2 multi-lang columns.
- **Docs**: `mapping_legacy_gold_to_gld_srv.md`, `mapping_gld_srv_poi_info.md`, `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md`.
- **Tests**: the six contract test files in `scope.files`.

## 2. Non-goals

- No new gold column, no grain change, no MERGE key change (D-NO-GOLD-COL).
- No change to PostgreSQL, Java, or `api-mapping` (D-GOLD-ONLY, D-DEST-SCOPE).
- No change to the `NB_GLD_SRV_POI_INFO` formula or its `DEST_COLS` (D-OLD-ADDR, D-DEST-GOLD).
- No legacy table other than `ai_enriched_poi` is added (D-LEGACY-READ). The init's legacy `destination_id` mapping does not change (D-LEGACY-DEST).
- No edit to pipeline JSON, and no edit to the older patch cells (`enrbrzpy`, `oldpricepy`, …).

## 3. Invariants

1. `slv_enr_poi_destination` stays one row per `poi_id`, with MERGE key `poi_id`.
2. `destination_id`, `destination_portal_id` and `destination_name` are projected from one `from_json(block, DEST_ELEM_SCHEMA)` array. They have the same length, the same order, and nulls in the same positions. If the block is NULL, all three are NULL.
3. `destination_portal_id` appears only in silver `TABLE_SPECS`, the two registry cells, `enr04`, and `destportalpy`. It never appears in gold specs, `DEST_COLS`, PostgreSQL DDL, entities, or `mapping_gld_srv_poi_info.md`.
4. Gold `destination_id` is still a 1-1 copy of silver. `NB_GLD_SRV_POI_INFO` does not change.
5. Before the backfill MERGE, every silver row is classed as exactly one of:
   - OLD: `destination_portal_id IS NULL` and `destination_id <=> id_proj`.
   - NEW: `destination_id <=> sd_proj` and `destination_portal_id <=> id_proj`.

   `destination_name <=> name_proj` must also hold. Any other state, a missing event, more than one payload, or a null `strapi_document_id` where an element exists stops the cell before any write.
6. The extract never lets `ensure_target` append `destination_portal_id`. If the registry has the column and the table lacks it, the extract raises `ConfigError`.
7. Init `story` and `local_tips` land only on gold `(map.poi_id, map.lang)` where `ai.lang = map.lang` (D-LANG-ROW). The four info columns come only from the `ai` row of the legacy `vi` row that `vi_key` selected (D-INIT-INFO-VI).
8. Init updates only `load_origin = 'LEGACY_INIT'` rows and inserts only new keys (`legacy_upsert_sql`). It creates no row from `ai_enriched_poi` alone (D-INIT-ENRICH-ONLY). The new joins do not change the row counts of `info_src` or `ml_src`.
9. Init reads exactly six tables from `OLD`, all through `old()` at pins: `poi_master`, `poi_enrichment_display`, `poi_detail`, `poi_review`, `poi_rating`, `ai_enriched_poi`.
10. Init does not change `destination_id` on existing LEGACY_INIT rows (D-LEGACY-DEST). RUN stops if `destination_changed_n > 0`.
11. Gold types do not change: `price_level` INT, `price_min` and `price_max` DECIMAL(18,2), the other columns STRING.

## 4. State ownership

| State | Owner / lock | Writers in this task |
|---|---|---|
| `slv_enr_poi_destination` rows and schema | extract, under watermark lock `wm_transform_brz_enrichment_result` (lib `NB_LIB_EXTRACT_RAWDATA`) | extract; `destportalpy` (ALTER and MERGE) while it holds the same lock |
| registry rows for source `brz_enrichment_result` | `enrbrzcfgpy` → `seed_registry` (`replaceWhere` per source) | `enrbrzcfgpy` rerun |
| `gld_srv_poi_info.destination_id` | `NB_GLD_SRV_POI_INFO` (GLD_30M) on pipeline rows; init on LEGACY_INIT rows | none directly. Gold follows silver on the next GLD_30M run. |
| six gold columns on LEGACY_INIT rows | `NB_SETUP_LEGACY_GOLD_POI`, under lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` | init RUN |
| six gold columns on pipeline rows | GLD_30M nodes | no change |

## 5. Grain and keys

Grain and keys are cited from `model-design.md` ## Entities and grain and ## Keys. The join keys this design uses:

- **Gate**: `ai.poi_id = map_rows.legacy_poi_id`, and `ai.lang <=> map_rows.lang` is required.
- **Info**: `ai.poi_id = vi_key.poi_id` (the legacy `vi` row) with `ai.lang = 'vi'`; then `vi_key._new` becomes gold `poi_id`. Each `_new` has exactly one `vi_key` row (`row_number`), and `ai` is unique on `poi_id`, so there is at most one row per key. `single_payload` stays as the guard.
- **Multi-lang**: `ai.poi_id = mp.legacy_poi_id AND ai.lang = mp.lang`, giving `(mp.poi_id, mp.lang)`. Several legacy rows can map to one `(poi_id, lang)`. `collect_set` then sees more than one value and both columns become NULL.
- **Backfill**:
  - Match: silver `(poi_id, _src_version, _event_processed_at, _event_id)` against bronze `(poi_id, CAST(version AS BIGINT), CAST(EventProcessedUtcTime AS TIMESTAMP), CAST(event_id AS STRING))` with `trim(event_type) = 'DESTINATION'`. P-DEST-1 proved this tuple matches every row exactly once.
  - MERGE: `poi_id` plus the same tuple, null-safe.

## 6. Alternatives compared

Re-projecting existing silver rows:

| Option | Verdict |
|---|---|
| A. Forward only (rows change on their next event) | Rejected. Two id spaces would live in silver and gold with no end date. |
| B. In-place backfill from the producing bronze event, one MERGE with classified rows | **Selected** (D-DEST-BACKFILL). Exact, idempotent, one atomic data commit. P-DEST proved coverage. |
| B'. Re-project from silver's own raw `destination` column (`_enr("destinations")`) | Rejected. Nothing proves that column keeps `strapi_document_id`, and the ledger names bronze as the source. |
| C. Empty silver, clear `ctrl_cdc_state`, then `full_reload` | Rejected. Silver is empty while it runs, and the reset also hits the multi-lang target. |
| D. Loosen the extract MERGE guard to `>=` | Rejected. It changes the CDC ordering guarantee for every DOC table. |

Schema change:
- Selected: a new patch cell with `ALTER … ADD COLUMNS … AFTER destination_id`.
- Rejected: extending `enrbrzpy` `SILVER_TARGETS`. That would edit a historical patch cell and would rewrite the whole table with `overwriteSchema` to add one nullable column.
- Consequence: a rerun of `enrbrzpy` after this task fails closed. `plan_rewrite` raises `ValueError("cột không có trong đích: ['destination_portal_id']")`. The test compares `SILVER_TARGETS` with `TABLE_SPECS` minus this one column (E17).

Source row for the four info columns:
- Selected: the `vi_key` row. It is the rule `lgpmain` already uses for detail, master and rating.
- Rejected: requiring equality across langs. `address_line_2` is language-specific, so whole POIs would be dropped.

Registry:
- Selected: reseed the whole source with `seed_registry` / `replaceWhere`. Inserting a key shifts `column_order`.
- Rejected: editing single rows.

Locks for `destportalpy`:
- Selected: hold only the extract watermark lock, because the extract is the single writer.
- Readers select by name on a Delta snapshot: `NB_GLD_SRV_POI_INFO` reads `DEST_COLS`, and `NB_ENR_POI_INFO` reads only `poi_id`. Holding the GLD and ENR locks as well would block them for no gain.

## 7. Ordering, transaction and commit boundaries

1. Publish the new extract notebook. With the old registry it behaves exactly like the old code: no registry column points at the strapi path, and `PATCH_COLS` only fires when the registry has `destination_portal_id`.
2. Run `NB_CREATE_DDL` cells `28e2be98`, `0f228dc1`, then the edited `enrbrzcfgpy`. This is one `replaceWhere` commit on the registry. From here until step 3 the extract raises `ConfigError("… chạy destportalpy")` and writes nothing.
3. Run `destportalpy`. It takes the lock, then runs every gate read-only, then makes two commits:
   - (a) the ALTER, when the column is missing;
   - (b) one backfill MERGE, tagged `DESTPORTAL:<LOCK>`.

   A failure between (a) and (b) is a safe state. Rows stay OLD with a NULL column, the guard is satisfied, and a later extract writes NEW rows for new events. A rerun of the cell finishes (b).
4. Run the extract once (dry run, then real). New events MERGE with the new projection.
5. GLD_30M on its schedule recomputes gold `destination_id` from one silver snapshot. Because (b) is one commit, any gold run sees either all OLD rows or all NEW rows.
6. Publish `NB_SETUP_LEGACY_GOLD_POI`. Run PLAN, then RUN, then RUN again. Each stage write is one MERGE commit tagged `LEGACY_INIT:<EXEC>` (existing behaviour). Steps 1–5 and step 6 are independent and touch different tables, but step 6 holds the GLD_30M lock, so it never overlaps step 5.

Old extract code must not run after step 2. Today the extract only runs by hand, and step 1 comes before step 2.

## 8. Extract and DDL design

### 8.1 `enr04`
- `ARRAY_PROJECTIONS = {"destinations.id": "id", "destinations.name": "name", "destinations.strapi_document_id": "strapi_document_id"}`
- `DEST_ELEM_SCHEMA = "array<struct<id:string,name:string,strapi_document_id:string>>"`. P-DEST-2 shows all three fields are strings.
- `PATCH_COLS = {"slv_enr_poi_destination": ("destination_portal_id",)}`
- `part_value` and the `bad` parse check loop over `ARRAY_PROJECTIONS` and `c.json_path`, so their logic does not change. Only update the docstring.

### 8.2 `enr08` preflight
Insert right after the `missing_null` raise and before `note = ensure_target(...)`:
```python
pending = [c for c in PATCH_COLS.get(spec.trg_tbl, ())
           if c in {x.name for x in spec.columns} and c.lower() not in have]
if pending:
    raise ConfigError(f"{spec.trg_tbl} thiếu {pending}: chạy destportalpy")
```
Dry run also passes through this guard.

### 8.3 Registry (`init_cfg_enr` and `enrbrzcfgpy`, identical text)
In the `slv_enr_poi_destination` columns dict, replace the `destination_id` entry with three entries in this key order:
```
"destination_id": _enr("destinations.strapi_document_id"),
"destination_portal_id": _enr("destinations.id"),
"destination_name": _enr("destinations.name"),
```
The resulting `column_order` values are consecutive.

### 8.4 `TABLE_SPECS`
In `lh_vv_silver.dbo.slv_enr_poi_destination`, put `('destination_portal_id', 'STRING', None),` between `('destination_id', …)` and `('destination_name', …)`. A fresh environment then creates the column directly. On such an environment `destportalpy` skips the ALTER and updates 0 rows.

### 8.5 `destportalmd`
Heading: `# [THÊM 26/11] 20261126-legacy-init-enriched-cols-and-dest-portal`. Then one paragraph in Vietnamese that says:
- the cell adds `destination_portal_id` STRING NULL after `destination_id` on `slv_enr_poi_destination`, on silver only;
- it re-projects existing rows from their own bronze event (`destination_id` ← `strapi_document_id`, `destination_portal_id` ← `id`), and rows with no element store `[]`;
- run order: publish extract → `enrbrzcfgpy` → this cell;
- it holds `wm_transform_brz_enrichment_result`;
- a rerun writes nothing;
- do not rerun `enrbrzpy` after this cell.

### 8.6 `destportalpy`
Copy the lock take, touch and release semantics from `enrbrzpy` (`_take` without a status change, the owner check, a release only when owned). The cell checks everything before it writes.

```python
# [THÊM 26/11] 20261126-legacy-init-enriched-cols-and-dest-portal (D-DEST-ID, D-DEST-PORTAL, D-DEST-ARRAY, D-DEST-BACKFILL)
import uuid
WM, REG = "lh_vv_ctrl.dbo.ctrl_mng_watermark", "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry"
WID = "wm_transform_brz_enrichment_result"
DEST_FQ, BRZ_FQ = "lh_vv_silver.dbo.slv_enr_poi_destination", "lh_vv_bronze.dbo.brz_enrichment_result"
NEW_COL, ANCHOR = ("destination_portal_id", "string"), "destination_id"
TABLE_COLS = [("poi_id", "string", False), ..., ("destination_id", "string", True),
              ("destination_portal_id", "string", True), ("destination_name", "string", True), ...]  # == TABLE_SPECS (test)
DEST_ELEM_SCHEMA = "array<struct<id:string,name:string,strapi_document_id:string>>"  # == enr04 (test)
REG_WANT = {"destination_id": "destinations.strapi_document_id",
            "destination_portal_id": "destinations.id", "destination_name": "destinations.name"}  # == registry (test)
TUPLE = ("_src_version", "_event_processed_at", "_event_id")
LOCK = "destportal-" + uuid.uuid4().hex
held = False

def _proj(block, field):
    arr = F.from_json(block, DEST_ELEM_SCHEMA)
    return F.when(arr.isNotNull(), F.to_json(F.transform(arr, lambda x: x.getField(field))))

def _schema():
    return [(f.name, f.dataType.simpleString(), f.nullable) for f in spark.table(DEST_FQ).schema]

def _plan(has_col):
    s = spark.table(DEST_FQ).select("poi_id", *TUPLE, "destination_id", "destination_name",
        (F.col(NEW_COL[0]) if has_col else F.lit(None).cast("string")).alias("_portal"))
    ev = (spark.table(BRZ_FQ).where(F.trim("event_type") == "DESTINATION")
          .select(F.col("poi_id").alias("_e_poi"), F.col("version").cast("bigint").alias("_e_v"),
                  F.col("EventProcessedUtcTime").cast("timestamp").alias("_e_ts"),
                  F.col("event_id").cast("string").alias("_e_id"),
                  F.get_json_object("data", "$.destinations").alias("_blk"))
          .select("_e_poi", "_e_v", "_e_ts", "_e_id", _proj(F.col("_blk"), "id").alias("_id_p"),
                  _proj(F.col("_blk"), "name").alias("_name_p"),
                  _proj(F.col("_blk"), "strapi_document_id").alias("_sd_p")))
    on = ((s["poi_id"] == ev["_e_poi"]) & s["_src_version"].eqNullSafe(ev["_e_v"])
          & s["_event_processed_at"].eqNullSafe(ev["_e_ts"]) & s["_event_id"].eqNullSafe(ev["_e_id"]))
    g = (s.join(ev, on, "left").groupBy("poi_id", *TUPLE, "destination_id", "destination_name", "_portal")
         .agg(F.count("_e_id").alias("_ev_n"), F.collect_set(F.struct("_id_p", "_name_p", "_sd_p")).alias("_p")))
    p = F.col("_p").getItem(0)
    one = (F.col("_ev_n") > 0) & (F.size("_p") == 1)
    sd_null = F.exists(F.from_json(p["_sd_p"], "array<string>"), lambda x: x.isNull())
    return g.select("*",
        one.alias("_one"),
        (one & F.col("_portal").isNull() & F.col("destination_id").eqNullSafe(p["_id_p"])).alias("_old"),
        (one & F.col("destination_id").eqNullSafe(p["_sd_p"]) & F.col("_portal").eqNullSafe(p["_id_p"])).alias("_new"),
        (one & ~F.col("destination_name").eqNullSafe(p["_name_p"])).alias("_name_bad"),
        (one & ((p["_sd_p"].isNull() & p["_id_p"].isNotNull()) | F.coalesce(sd_null, F.lit(False)))).alias("_sd_missing"),
        (one & (p["_id_p"] == F.lit("[]"))).alias("_empty"),
        p["_id_p"].alias("_id_p"), p["_sd_p"].alias("_sd_p"))

def _counts(plan):
    r = plan.agg(F.count("*").alias("silver_n"), F.countDistinct("poi_id").alias("key_n"),
        F.sum(F.when(F.col("_ev_n") == 0, 1).otherwise(0)).alias("no_event_n"),
        F.sum(F.when((F.col("_ev_n") > 0) & (F.size("_p") > 1), 1).otherwise(0)).alias("dup_payload_n"),
        F.sum(F.col("_name_bad").cast("int")).alias("name_bad_n"),
        F.sum(F.col("_old").cast("int")).alias("old_n"), F.sum(F.col("_new").cast("int")).alias("new_n"),
        F.sum(F.when(F.col("_one") & ~F.col("_old") & ~F.col("_new"), 1).otherwise(0)).alias("drift_n"),
        F.sum((F.col("_old") & F.col("_sd_missing")).cast("int")).alias("strapi_missing_n"),
        F.sum((F.col("_old") & F.col("_empty")).cast("int")).alias("empty_n")).first().asDict()
    return {k: int(v or 0) for k, v in r.items()}
```

Then the steps, in order:
1. `_take(WID)`, and set `held = True` only if the lock is owned.
2. **Registry gate.** For `src_tbl = 'brz_enrichment_result'` and `trg_tbl = 'slv_enr_poi_destination'`:
   - the active rows' `json_path` per `REG_WANT` must match;
   - `column_order(portal) == column_order(destination_id) + 1`.

   Otherwise stop with "chạy enrbrzcfgpy".
3. **Schema gate.**
   - `_schema()` equal to `[c for c in TABLE_COLS if c[0] != NEW_COL[0]]` → `need_alter = True`.
   - Equal to `TABLE_COLS` → `need_alter = False`.
   - Anything else → stop.
4. **Pre-write plan.** `pre = _counts(_plan(not need_alter))`. Under the comment `# Dừng trước khi ghi`, stop (`issues`) on any of:
   - `key_n != silver_n`;
   - `no_event_n`, `dup_payload_n`, `name_bad_n`, `drift_n` or `strapi_missing_n` non-zero;
   - `old_n + new_n != silver_n`.

   Print `pre`.
5. `_touch_lock()`. If `need_alter`, run `ALTER TABLE {DEST_FQ} ADD COLUMNS (\`destination_portal_id\` STRING AFTER \`destination_id\`)`. Then `_schema()` must equal `TABLE_COLS`, else stop. A fresh plan, `mid = _counts(_plan(True))`, must equal `pre`, else stop. The fresh plan avoids reusing a DataFrame analysed before the schema change.
6. `_touch_lock()`.
   - If `pre["old_n"] == 0`, skip the write.
   - Otherwise:
     - record `v_pre`;
     - create temp view `_v_destportal` from `_plan(True).where("_old")` with `poi_id`, the tuple, `_id_p`, `_sd_p`;
     - set `userMetadata = DESTPORTAL:{LOCK}`;
     - run:

       `MERGE INTO {DEST_FQ} t USING _v_destportal s ON t.poi_id = s.poi_id AND t._src_version <=> s._src_version AND t._event_processed_at <=> s._event_processed_at AND t._event_id <=> s._event_id WHEN MATCHED AND t.destination_portal_id IS NULL AND t.destination_id <=> s._id_p THEN UPDATE SET destination_id = s._sd_p, destination_portal_id = s._id_p, updated_at = current_timestamp()`

     - unset the metadata in a `try`/`finally`.
7. **Post-check** (`# Sau khi ghi`): `post = _counts(_plan(True))` must show `old_n == 0`, `drift_n == 0`, `new_n == silver_n`. Read `numTargetRowsUpdated` from the commit tagged `DESTPORTAL:{LOCK}`; it must equal `pre["old_n"]`. Print `{v_pre, v_post, updated_n, pre, post}`.
8. `finally:` release the lock if held.

The code must not contain `DROP`, `DELETE`, `TRUNCATE`, `RESTORE`, `columnMapping`, `CREATE TABLE`, `RENAME`, or `overwriteSchema`. The source groups by the silver key, so each target row matches at most one source row, which Delta MERGE requires. `updated_at` is bumped on purpose: NB_GLD_SRV_POI_INFO dedupes on it, and the value really changed.

## 9. Legacy init design (`lgpmain`)

### 9.1 Preflight (before `EXEC`)
- Add `"ai_enriched_poi"` to the `PINS` table tuple.
- Then:
  ```python
  AI_TYPES = {"poi_id": "string", "lang": "string", "address_line_2": "string", "price_level": "int",
              "price_min": "int", "price_max": "int", "story": "string", "local_tips_or_neighborhood": "string"}
  ai_pin = old("ai_enriched_poi")
  bad_types = {k: dict(ai_pin.dtypes).get(k) for k in AI_TYPES if dict(ai_pin.dtypes).get(k) != AI_TYPES[k]}
  ```
  Raise if `bad_types` is non-empty. Raise if `count != countDistinct("poi_id")`.
- Raise "chạy oldpricepy của NB_CREATE_DDL trước" unless:
  - `table_columns(INFO_FQ)` has `old_address` string, `price_level` int, and `price_min` / `price_max` `decimal(18,2)`;
  - `table_columns(ML_FQ)` has `story` and `local_tips` string.

### 9.2 Gate (`stage = "enriched"`)
Place it after the `destination` decision raise and before `stage = "map"` / `write_insert_only(MAP_FQ`.
```python
stage = "enriched"
ai = ai_pin.select(F.col("poi_id").alias("_ai_id"), F.col("lang").alias("_ai_lang"), "address_line_2",
                   "price_level", "price_min", "price_max", "story", "local_tips_or_neighborhood")
hit = ai.join(map_rows.select("legacy_poi_id", F.col("lang").alias("_m_lang"), "poi_id_status"),
              F.col("_ai_id") == F.col("legacy_poi_id"), "left")
e = summary["enriched"] = {
    "ai_rows": ai.count(),
    "map_hit_n": hit.where("legacy_poi_id IS NOT NULL").count(),
    "map_miss_n": hit.where("legacy_poi_id IS NULL").count(),
    "lang_mismatch_n": hit.where("legacy_poi_id IS NOT NULL AND NOT (_ai_lang <=> _m_lang)").count(),
    "not_ok_n": hit.where("legacy_poi_id IS NOT NULL AND poi_id_status <> 'OK'").count()}
e["decision"] = "USER_DECISION" if e["lang_mismatch_n"] or (e["ai_rows"] and not e["map_hit_n"]) else "OK"
if p_mode == "RUN" and e["decision"] != "OK":
    raise RuntimeError(f"USER_DECISION ai_enriched_poi: {e}")
```

### 9.3 Info stage
- **D-LEGACY-DEST guard.** Right after `info_src = info_src.join(dest_one, …)`:
  - `prev = spark.table(INFO_FQ).where("load_origin = 'LEGACY_INIT'").select("poi_id", F.col("destination_id").alias("_prev_dest"))`
  - `summary["info"]["destination_changed_n"] = info_src.join(prev, "poi_id").where(~F.col("destination_id").eqNullSafe(F.col("_prev_dest"))).count()`
  - Raise in RUN if it is non-zero. A non-zero value means the `poi_master` pin differs from the earlier init.
- **Enrichment join.** After `n_before = info_src.count()`, so the existing guard `info_src.count() != n_before` covers it:
  ```python
  enr_cols = ["old_address", "price_level", "price_min", "price_max"]
  enr_info = (ai.join(vi_key, ai["_ai_id"] == vi_key["poi_id"]).where(F.col("_ai_lang") == "vi")
              .select(vi_key["_new"].alias("poi_id"), F.col("address_line_2").alias("old_address"), "price_level",
                      F.col("price_min").cast("decimal(18,2)").alias("price_min"),
                      F.col("price_max").cast("decimal(18,2)").alias("price_max")))
  ei_ok, ei_bad = single_payload(enr_info, ["poi_id"], enr_cols)
  info_src = info_src.join(ei_ok.select("poi_id", *[F.col("_p").getItem(0)[c].alias(c) for c in enr_cols]), "poi_id", "left")
  ```
- **Summary keys:** `enriched_info_conflict_n` (= `ei_bad.count()`), `old_address_filled_n`, `price_filled_n` (any of the three prices non-null), `price_inverted_n` (min > max; report only).

### 9.4 Multi-lang stage
Place after `ml_src = ml_src.join(name_one, …)` and before `before_parent = ml_src.count()`:
```python
n_ml = ml_src.count()
enr_ml = (ai.join(mp, (ai["_ai_id"] == mp["legacy_poi_id"]) & (ai["_ai_lang"] == mp["lang"]))
          .select(mp["poi_id"], mp["lang"], "story", F.col("local_tips_or_neighborhood").alias("local_tips")))
eg = enr_ml.groupBy("poi_id", "lang").agg(F.collect_set(F.struct("story", "local_tips")).alias("_e"))
enr_one = eg.select("poi_id", "lang",
                    F.when(F.size("_e") == 1, F.col("_e").getItem(0)["story"]).alias("story"),
                    F.when(F.size("_e") == 1, F.col("_e").getItem(0)["local_tips"]).alias("local_tips"))
ml_src = ml_src.join(enr_one, ["poi_id", "lang"], "left")
if ml_src.count() != n_ml:
    raise RuntimeError("multi_lang guard: enriched join changed rows")
```
- Do not add `story` or `local_tips` to `pay`. A conflict on them never drops an ML row.
- After the `parents` semi-join, add these summary keys:
  - `enriched_ml_conflict_n` (`size(_e) > 1`);
  - `story_filled_n`, `local_tips_filled_n`;
  - `enriched_ml_unplaced_n`: rows of `enr_one` with a non-null value whose key is not in the final `ml_src`.

### 9.5 Writes
No change. `to_target` casts and NULL-fills by target type, and `write_insert_only(..., upsert=True)` runs `legacy_upsert_sql`.

### 9.6 `lgpmd`
Add one sentence: the init reads `ai_enriched_poi` at a pin for `old_address`, the prices, `story` and `local_tips`, and only fills rows the init already builds.

## 10. Docs

- `mapping_legacy_gold_to_gld_srv.md`:
  - §1 header becomes "41 cột". Insert `old_address` after `full_address`, and `price_level`, `price_min`, `price_max` after `review_count`. For the source, write `ai_enriched_poi`.`address_line_2` or the same column name, and the rule "dòng `ai_enriched_poi` của dòng legacy `lang = vi` mà `vi_key` chọn; không có thì NULL; giá int → DECIMAL(18,2)". Renumber the rows.
  - Line 18: add that these four columns follow the `vi` row, not equality across langs.
  - §1 row 7 (`destination_id`): append "Giá trị LEGACY_INIT nằm ngoài id portal; 1/24 giá trị trùng strapi_document_id (P-LEGDEST-1, 26/11). Không đổi mapping, không chạy lại riêng."
  - §2 header becomes "16 cột". After `experience`, add `story` ← `ai_enriched_poi.story` and `local_tips` ← `ai_enriched_poi.local_tips_or_neighborhood`, with "khớp `poi_id` cũ và `lang`; nhiều giá trị thì NULL; không tạo dòng mới".
  - Line 157: remove `ai_enriched_poi`. Add: "`ai_enriched_poi`: chỉ đọc `poi_id`, `lang`, `address_line_2`, `price_level`, `price_min`, `price_max`, `story`, `local_tips_or_neighborhood` tại version pin. Cột khác không nạp."
  - Add one sentence: pipeline MERGE claims LEGACY_INIT rows of POIs that have silver, and its own values then replace the init values.
- `mapping_gld_srv_poi_info.md`:
  - §1.1, next to line 19: "`destination_id` của silver là chuỗi JSON mảng `destinations[].strapi_document_id`, cùng thứ tự và vị trí null như `destination_name` (từ 26/11; trước đó là `destinations[].id`). Gold copy 1-1."
  - §1.2 row `destination_id` (line 51): add "giá trị là strapi_document_id theo silver".
  - The string `destination_portal_id` must not appear in this file.
- `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md`:
  - §4: three projections — `strapi_document_id` → `destination_id`, `id` → `destination_portal_id`, `name` → `destination_name`.
  - §5: add the `PATCH_COLS` guard ("chạy destportalpy").

## 11. Idempotency

- **Extract**: the MERGE guard does not change. A rerun on the same events writes nothing.
- **`destportalpy`**: the ALTER is skipped when the schema already equals `TABLE_COLS`. The MERGE only matches OLD rows, so a rerun after success has `old_n = 0` and does not write.
- **Init**: MERGE on the PK with a duplicate check before the write, so a second RUN inserts 0 rows and does not multiply rows. LEGACY_INIT rows get the same values; `updated_at` and `row_hash` are rewritten each run (existing behaviour).

## 12. Concurrency

- `destportalpy` holds the extract watermark lock for the whole cell and touches it before each commit. The MERGE ON tuple also skips any row a newer event replaced.
- GLD_30M and `NB_ENR_POI_INFO` read Delta snapshots by column name. The ALTER commit and the MERGE commit are each atomic.
- Init holds the GLD_30M flow lock (existing), so it never runs at the same time as gold pipeline nodes.

## 13. Retry, recovery, partial failure

- **`destportalpy`**:
  - A gate failure writes nothing.
  - A failure after the ALTER and before the MERGE is safe (§7.3). The rerun skips the ALTER and finishes the MERGE.
  - A failure inside the MERGE leaves no commit (one transaction). The post-check reads the history by tag.
  - A lost lock stops at the next touch.
- **Init**: each stage is its own commit (existing). A failed stage leaves the earlier stages committed and idempotent. Retry with the same `p_pin_json`, taken from the printed `summary["pins"]` that now includes `ai_enriched_poi`.
- **Extract** during the window between step 2 and step 3: it raises `ConfigError` with nothing written. Rerun it after step 3.

## 14. Observability

- **Extract**: `ConfigError` text names `destportalpy`.
- **`destportalpy`**: prints `pre`, `mid` and `post` counts (`silver_n`, `key_n`, `no_event_n`, `dup_payload_n`, `name_bad_n`, `old_n`, `new_n`, `drift_n`, `strapi_missing_n`, `empty_n`), plus `v_pre`, `v_post` and `updated_n`. The commit tag is `DESTPORTAL:<LOCK>`. Expected values from the evidence: `old_n = 19799`, `empty_n = 2`, all others 0.
- **Init**: the exit JSON gains `summary["enriched"]`, the new info keys (including `destination_changed_n`) and the new multi_lang keys.

## 15. Security

- Read-only cross-workspace reads of `OLD` at pins (existing).
- SQL is built from constants and from the regex-validated `p_target_ws`.
- No secrets, no external calls, no new identities.
- `address_line_2` is a business address, not personal data.

## 16. Rollout

The user runs the §7 steps 1–6 on DEV. The runtime runbook (written after review PASS) must include:
- the `destportalpy` summary and a rerun with `updated_n = 0`;
- the extract dry run, then a real run;
- one GLD_30M run;
- init PLAN, then RUN, then RUN, using the `poi_master`, `poi_enrichment_display`, `poi_detail`, `poi_review` and `poi_rating` pins of the earlier init. Otherwise `drift_n` or `destination_changed_n` stops the run.

## 17. Rollback and forward recovery

- **Preferred: forward.** Every step can be rerun (§11, §13).
- **Value rollback of silver.** `destination_portal_id` holds the exact previous `destination_id` (P-DEST-1 `id_eq_n = silver_n`). If needed:
  - run, under the extract lock, a one-off `UPDATE … SET destination_id = destination_portal_id WHERE destination_portal_id IS NOT NULL`;
  - republish the previous extract;
  - reseed the registry with the previous `enrbrzcfgpy` text.

  The NULL-able column can stay.
- **`RESTORE TABLE … TO VERSION AS OF <v_pre>`** is only valid if no extract run committed after the backfill, because `ctrl_cdc_state` would not replay newer events.
- **Gold** follows silver on the next GLD_30M run. Do not RESTORE gold tables, because that would undo pipeline commits.
- **Init**: rerun the previous notebook version with the same pins. That rewrites LEGACY_INIT rows with NULL in the six columns.

## 18. Implementation plan

E1–E20 in the Main brief, in this order:
1. E1–E5: extract and DDL.
2. E6–E7: patch cell.
3. E8–E12: init.
4. E13–E15: docs.
5. E16–E20: tests.

## 19. Verification

**Local:**
```
python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_enr_extract_contract.py tests/test_legacy_gold_poi_init_contract.py tests/test_gld_srv_poi_contract.py tests/test_srv_poi_serving_contract.py -q
python scripts/vv.py verify
```
Both must PASS before review.

**Runtime (user, DEV):**
- **Silver**:
  - the `destportalpy` gates are 0;
  - `updated_n = old_n`, and a rerun gives `updated_n = 0`;
  - this query returns 0: `SELECT count(*) FROM slv_enr_poi_destination WHERE size(from_json(destination_id,'array<string>')) <> size(from_json(destination_portal_id,'array<string>')) OR size(from_json(destination_id,'array<string>')) <> size(from_json(destination_name,'array<string>'))`;
  - no row has `destination_portal_id IS NULL AND destination_id IS NOT NULL`.
- **Gold**, after GLD_30M: `gld_srv_poi_info.destination_id <=> slv.destination_id` for rows with `load_origin IS NULL`.
- **Init RUN 1**:
  - `enriched.decision = OK` and `destination_changed_n = 0`;
  - the filled counts match PLAN.
- **Init RUN 2**:
  - `inserted = 0` on every stage;
  - the row counts of `gld_srv_poi_info` and `gld_srv_poi_multi_lang` are unchanged;
  - a `(poi_id, lang)` duplicate query returns 0;
  - LEGACY_INIT `destination_id` equals the value before RUN 1 (time-travel compare).
- **Spot check**: five POIs with two or more langs and a non-null `story` show a different `story` per lang, as in the source.
