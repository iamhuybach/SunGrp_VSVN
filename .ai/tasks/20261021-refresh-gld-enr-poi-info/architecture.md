RESULT: PASS

## Main brief

### Decision
- Rebuild `NB_ENR_POI_INFO` on the `slv_poi_entity_non_enrich` spine, with 7 roles: entity, amenity, rating, price, hours, review, i18n. Amenity is aggregated per `poi_id`. D-17: partner hours join `uuid_md5(business_service_id, 'partner') = poi_id`, `locale = 'vi'`.
- D-18 on DEV: the DROP of `gld_enr_poi_info` and the delete of its `wm_e__` rows are runbook SQL (R-3/R-4). They are not in any notebook (§2.1 rules 4–5). Coordinate is never touched.
- New `NB_CREATE_DDL` cell `enrinfopy`, locked and idempotent:
  - table missing: creates it with the exact init DDL;
  - old contract: refuses and changes nothing;
  - then turns 6 edges off and adds 3. It has no DROP, REPLACE, or ALTER.
- `NB_SETUP_INITIAL_DDL` is edited in place to the same end state. `enrddlpy`, the lib, the pipeline JSON, review, and coordinate are untouched.

### Invariants Main must preserve
- I1: at most one row per `poi_id` per commit. Amenity is grouped before the join; i18n is unique per (`business_service_id`, `vi`); lib `pk_duplicate` blocks otherwise.
- I2: emitted `poi_id`s come only from the live entity table. No reads of `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_pn_poi`.
- I3: these are all the same list of 40 columns, in order, with only `poi_id` NOT NULL:
  - the gold columns;
  - `enrinfopy.INFO_COLS`;
  - the `init_tables` spec;
  - the select aliases plus `created_at`, `updated_at`.
  - The `enrinfopy` create text == init `create_sql(spec)`.
- I4: non-google rows have NULL `rating`, `user_rating_count`, `price_level`, `review_json`. `opening_hours_text` is set only for google (`periods_json`) or partner (`$.policies.operating_hours`).
- I5: `cost IS NULL ⇔ cost_vnd = 'null'`. Otherwise `{label3:"Từ n,nnnđ"}`, rounded half-up to the thousand.
- I6: the active ENR edges into info are exactly the 7 `INFO_ACTIVE` sources. Coordinate has 0 active edges and its 3 rows are kept.
- I7: the `enrinfopy` text has no `DROP`, `DELETE`, `TRUNCATE`, `ALTER TABLE`, `REPLACE`, `RESTORE`. The cell never modifies an existing table and never re-enables an edge.
- I8: re-running `enrinfopy` changes nothing. A node run with no source change appends 0 rows.
- I9: a POI is re-emitted when its entity, rating, price, hours, review, amenity (including row removal), or `vi` i18n (including `deleted`) row changes.
- I10: the `gld_enr_poi_coordinate` version, its `wm_e__` rows, and `wm_flow__` are never deleted or changed by this task.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_ENR_POI_INFO.ipynb | cell `8cef70ac` | Text: `APPEND lh_vv_gold.enr.gld_enr_poi_info từ lh_vv_silver.dbo.slv_poi_entity_non_enrich.` | names the new source |
| 2 | notebooks/NB_ENR_POI_INFO.ipynb | cell `36415d3b` | Replace with doc §Implementation plan > Code A. Remove `_duration_label`, `_blank`, `_destination_context`. Keep `_keys` and the `_review_json` body verbatim. New `_vi_i18n`, `_partner_hours(ctx)`, `_i18n_keys(ctx)` use lib `uuid_md5` | rows 7–8 tests pass |
| 3 | notebooks/NB_CREATE_DDL.ipynb | new markdown cell `enrinfomd` after `entwebpy` | `# [THÊM 21/10] 20261021-refresh-gld-enr-poi-info` | second-to-last cell |
| 4 | notebooks/NB_CREATE_DDL.ipynb | new code cell `enrinfopy` (last) | Code B verbatim. Constants stay pure literals; no forbidden uppercase tokens; no literal `lh_vv_` FQ after `CREATE TABLE IF NOT EXISTS` | `test_info_patch_cell_*`, `test_info_patch_create_matches_init` pass |
| 5 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` entry `gld_enr_poi_info` | `cols` = the 40 `INFO_COLS` as `(name, dtype, None)` (Code C) | `test_columns_match_sources` |
| 6 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` | Code C: 6 rows get `is_active` 0; 3 new rows go after the coordinate rows; add the comment line | 57 rows; `test_no_destructive_sql` green |
| 7 | tests/test_enr_poi_contract.py | helpers, `INFO`, `INFO_DROPPED`, `EDGES_OFF`/`EDGES_ON`/`INFO_ACTIVE`, tests | Code D: rewrite `test_gold_ddl_matches_mapping`; update `test_mapping_comments_and_edges`; add 7 tests | pytest green |
| 8 | tests/test_initial_ddl_contract.py | `test_columns_match_sources` | Compare info with `enrinfopy` `INFO_COLS` | green |
| 9 | tests/test_initial_ddl_contract.py | `test_pipeline_config_rows_match_sources` | `is_active` from `EDGES_OFF`; append `EDGES_ON`; len 57 | green |
| 10 | tests/test_initial_ddl_contract.py | new `test_enr_initial_edge_state`, `test_info_patch_create_matches_init` | Code D | green |

### Order and stop points
1. Wait for `run-gate` architecture PASS. Do not edit source before it.
2. Rows 1–2.
3. Rows 3–4.
4. Rows 5–6.
5. Rows 7–10, then the local commands. **STOP (evidence):** on any failure, fix it before review. Do not weaken a guard test to make it pass.
6. Commit `docs/context/3p-google/mapping_gld_enr_poi_info.md` with the task, because row 7 reads it. The unrelated working-tree deletion `docs/context/3p-google/Mapping_POI_Service_Data.md` belongs to the user: do not stage it, and mention it.
7. Review: sql-data, spark-runtime, state-correctness, then the risk gate.
8. `python scripts/vv.py run-author 20261021-refresh-gld-enr-poi-info --kind runbook`, from doc §Rollout, §Implementation plan > Runbook SQL, §Verification (P-0..P-8).
9. **STOP (evidence, user runs on DEV).** Steps:
   1. Confirm the workspace is DEV.
   2. Pause the ENR trigger.
   3. Sync the notebooks.
   4. R-1 pre-state saved.
   5. R-2 lock free.
   6. R-3 DROP info, then R-4 delete the 10 info `wm_e__` ids.
   7. Run `enrinfopy` only.
   8. Run `NB_SETUP_INITIAL_DDL` with `p_apply = false`.
   9. NB_00 PLAN, RUN, checks, RUN again.
   10. Resume the trigger.

   Results go to `evidence/results/`.
   - **STOP and return to the Architect** if R-1 shows a schema that is neither the old 23 names nor the new 40.
   - Never re-run `enrddlpy`.
   - Never apply R-3 outside DEV.

### Tests and verification
- `python -m pytest tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest tests -q`
- `python scripts/vv.py verify 20261021-refresh-gld-enr-poi-info`
- New or changed tests:
  - `test_gold_ddl_matches_mapping`, `test_mapping_comments_and_edges`;
  - `test_info_patch_cell_edges`, `test_info_patch_cell_guards`, `test_info_select_matches_ddl`, `test_info_spec_inputs_match_active_edges`, `test_info_partner_join_matches_entity`, `test_info_labels_match_mapping`, `test_best_time_pattern`;
  - `test_columns_match_sources`, `test_info_patch_create_matches_init`, `test_pipeline_config_rows_match_sources`, `test_enr_initial_edge_state`.
- Runtime proof (DEV):
  - after the reset, the info table and its `wm_e__` rows are gone, and coordinate and `wm_flow__` are unchanged;
  - `enrinfopy` creates the table and its re-run is a no-op;
  - the init plan shows no info diff;
  - PLAN has no coordinate node;
  - RUN basis is FULL for all 7 roles, rows = the live entity count, 0 duplicate `poi_id`, block checks 0;
  - partner hours match P-4;
  - the coordinate version is unchanged;
  - a second RUN appends 0 rows;
  - the shape aggregates match D-15, D-16, I4, I5.

### Read only if needed
- §Ordering, §Transaction and commit boundaries, §Partial failure → rows 4, 6; stop 9 (step order, reset window, `enrddlpy` hazard)
- §Alternatives and trade-offs → row 4 and stop 9 (why the DROP is in the runbook; `uuid_md5` reuse)
- §Implementation plan > Code A → rows 1–2
- §Implementation plan > Code B → rows 3–4
- §Implementation plan > Code C → rows 5–6
- §Implementation plan > Code D → rows 7–10
- §Implementation plan > Runbook SQL, §Rollout, §Rollback and forward recovery, §Verification → steps 8–9
- §Concurrency, §Retry and recovery → row 4 (lock lease), row 2 (`_amenity_keys` fallback; 1H freshness note for the user)

# Architecture — 20261021-refresh-gld-enr-poi-info (round 2)

Grain, keys, and the column contract come from `model-design.md`: `## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`. Ledger rows D-01..D-18 in `decision.md` are cited by ID. This document covers only how the contract is built, put in place, ordered, and recovered.

Round 2 supersedes round 1 on two points:
- D-17: the partner i18n join is `uuid_md5(business_service_id, 'partner') = entity.poi_id` with `locale = 'vi'`. It is no longer `source_id`/`language_code`.
- D-18: on DEV, `gld_enr_poi_info` is dropped and recreated as on first init. `CREATE OR REPLACE` is gone.
  - The DROP is a manual DEV runbook step. It follows the documented DEV node reset in `docs/context/CTRL_TABLES_CONTEXT.md` §4 "Thao tác thường gặp": DROP the table, then delete the `wm_e__` rows of that `trg_tbl`, and keep `wm_flow__`.
  - Neither DDL notebook contains a DROP. This is required by `02_NAMING_CONVENTION.md` §2.1 rules 4–5.

No new user decision is needed.

## Scope

- `notebooks/NB_ENR_POI_INFO.ipynb`:
  - Rebuild cell `36415d3b` around the spine `slv_poi_entity_non_enrich`.
  - Roles: `entity`, `amenity`, `rating`, `price`, `hours`, `review`, `i18n`. Removed roles: `poi`, `addr`, `contact`.
  - Update markdown cell `8cef70ac`.
- `notebooks/NB_CREATE_DDL.ipynb`: append markdown `enrinfomd` and code `enrinfopy` after `entwebpy`.
  - `enrinfopy` creates `gld_enr_poi_info` with the new contract only when the table is missing. It is byte-for-byte the same DDL as `init_tables`.
  - It refuses the old contract and points to the DEV reset.
  - It switches the `PL_VV_TRANS_SLV_TO_ENR_15P` edges.
  - Cell `enrddlpy` is not touched.
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, edited in place:
  - the `init_tables` entry for `gld_enr_poi_info` gets the 40 columns;
  - in `init_seed_ctrl`, 6 edges get `is_active = 0` and 3 active edges are added.
- `tests/test_enr_poi_contract.py` and `tests/test_initial_ddl_contract.py`: cover the contract, the edges, the guards, the D-17 join, the formatter constants, and the equality of the create DDL with init.
- The DEV reset SQL is specified in §Rollout for `run-author --kind runbook`. `runtime-runbook.md` is a task artifact, not a scope file.

## Non-goals

- `NB_ENR_POI_REVIEW` and the `gld_enr_poi_review` columns (D-03). Edge `slv_3p_poi_review → gld_enr_poi_review` stays active.
- `NB_ENR_POI_COORDINATE` and table `gld_enr_poi_coordinate`. The table is not dropped. Its `wm_e__` rows are not deleted, and it stays in both DDL notebooks (D-02, D-18).
- Pipeline JSON, `NB_LIB_TRANSFORM_SLV_GLD`, `NB_00_ORCHES_SLV_TO_ENR_15P`.
- Edges `slv_pn_business_services` / `slv_pn_business_service_i18ns → slv_pn_poi`. After this change `slv_pn_poi` has no ENR consumer. Report it to the user as backlog.
- Propagating deletions to gold. APPEND gold is a history. A POI soft-deleted in the entity table emits no new row.
- Doc drift in `CTRL_TABLES_CONTEXT.md` and `01_DATA_MODEL.md`. These files are outside `scope.files`; report the drift to the user.
- Out by the ledger: LLM cost, `cost_method`, `cost_confidence`, `time_to_spend_minutes`, `best_time_type`, `types_json`, `destination_context` (D-05, D-08, D-13, D-14, D-16). The mapping table still lists `time_to_spend_minutes` and `best_time_type`; the ledger overrides it.
- Dropping the old-contract table in any environment other than DEV. D-18 covers DEV only. There, `enrinfopy` refuses the old contract and the user must decide.

## Invariants

1. I1 grain: each APPEND commit of `gld_enr_poi_info` has at most one row per `poi_id`.
   - Amenity is aggregated to `poi_id` before the join.
   - Rating, price, and hours join on `poi_id`, which is their primary key.
   - Review is packed per `poi_id`.
   - i18n gives one `vi` row per `business_service_id` (primary key (`business_service_id`, `locale`)), so one per partner `poi_id`.
   - A violation is blocked by lib `quality_gate` `pk_duplicate`. Nothing is picked silently.
2. I2 spine:
   - Every emitted `poi_id` is in the live entity table (`ctx.input("entity")`, `deleted_at IS NULL`).
   - Nothing reads `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, or `slv_pn_poi`.
3. I3 schema: the physical columns of `gld_enr_poi_info` equal `enrinfopy.INFO_COLS`, all 40 in order.
   - This list also equals the `init_tables` spec, and the build select aliases followed by `created_at`, `updated_at`.
   - Only `poi_id` is NOT NULL.
   - The `enrinfopy` create statement renders the same text as `init_tables` `create_sql` for that spec.
4. I4 source rule (D-07, D-17):
   - When `lower(trim(source_name)) <> 'google'`: `rating`, `user_rating_count`, `price_level`, `review_json` are NULL.
   - `opening_hours_text` is set only for google (`periods_json`) or partner (`$.policies.operating_hours` of the `vi` i18n row joined by `uuid_md5(business_service_id, 'partner')`).
5. I5 cost (D-08..D-11, D-15):
   - `cost IS NULL ⇔ cost_vnd = 'null'` (JSON text).
   - Otherwise `cost_vnd = {label3: "Từ n,nnnđ"}`, with n = cost rounded half-up to a multiple of 1000.
6. I6 edges: after `enrinfopy`, the active ENR edges into `gld_enr_poi_info` are exactly the 7 `INFO_ACTIVE` sources, one row each. `gld_enr_poi_coordinate` has 0 active edges and its 3 rows remain. `NB_SETUP_INITIAL_DDL` seeds the same state.
7. I7 destructive DDL:
   - The `enrinfopy` text contains none of `DROP`, `DELETE`, `TRUNCATE`, `ALTER TABLE`, `REPLACE`, `RESTORE`, comments included.
   - An existing table is never modified by the cell.
   - The only destructive operations of this task are runbook steps R-3 and R-4 (§Rollout), on DEV, under the preconditions R-1 and R-2.
8. I8 idempotency:
   - Re-running `enrinfopy` changes nothing.
   - A node run with no source change appends 0 rows.
   - A retry with the same `exec_id` does not append twice (lib marker).
9. I9 change completeness: a POI is re-emitted when any of these changes:
   - its entity row;
   - its rating, price, hours, or review row;
   - any of its amenity rows, including removal of a row;
   - its `vi` i18n row, including `deleted = true`.
10. I10 coordinate untouched: the version of `gld_enr_poi_coordinate` and its `wm_e__` rows are the same before and after the rollout.

## State ownership

| State | Owner | Writer in this task |
|---|---|---|
| `lh_vv_gold.enr.gld_enr_poi_info` data | `NB_ENR_POI_INFO` via lib `execute_append` | node (APPEND only) |
| `gld_enr_poi_info` existence and schema | DDL notebooks; DEV reset in the runbook | runbook R-3 (DROP, DEV only); `enrinfopy` (create when missing); `init_tables` (empty env) |
| `ctrl_mng_pipeline_config` rows of `PL_VV_TRANS_SLV_TO_ENR_15P` | DDL notebooks | `enrinfopy` (INSERT WHERE NOT EXISTS; UPDATE `is_active` where different); `init_seed_ctrl` (MERGE NOT MATCHED) |
| `ctrl_mng_watermark` `wm_e__gld_enr_poi_info__*` rows | NB_00 (`sql_merge_edge_wm`) | runbook R-4 deletes all 10 possible ids (DEV reset); NB_00 inserts the 7 active ones on the first run |
| `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` lock | NB_00 / manual node | `enrinfopy` takes it and releases it (35-minute lease = ENR `p_lock_timeout_min`). The runbook never deletes it |
| `slv_poi_entity_non_enrich`, `slv_poi_amenity` | `PL_VV_TRANS_SLV_TO_SLV_1H` nodes | read only |
| `slv_3p_poi_*`, `slv_pn_business_service_i18ns` | FL_00 extract notebooks | read only |
| `gld_enr_poi_coordinate` and its `wm_e__` rows | `NB_ENR_POI_COORDINATE` / NB_00 | none (I10) |

## Grain and keys

Grain and keys are those of model-design `## Entities and grain` and `## Keys`. The build enforces them as follows:
- `amenity`: `groupBy("poi_id")` before the join (`_service_flag`).
- `rating`, `price`, `hours`: joined on `poi_id`, their DOC key (01_DATA_MODEL §5.2).
- `review`: packed per `poi_id` by the unchanged `_review_json`.
- `i18n` (D-17), in `_vi_i18n`:
  - filter `locale == 'vi'`, the same exact match as N6 `_partner`;
  - compute `poi_id = uuid_md5(F.col("business_service_id"), F.lit(PARTNER))`. This is the lib function N6 uses for partner `poi_id` (`uuid_md5(F.col("id"), F.lit(PARTNER))`, where `id` = `business_service_id` through the N6 join).
  - For hours, live rows only (`deleted` not true, as N6 `_live`). For change detection, all changed rows, so a newly deleted row re-emits the POI.
  - Joined to the spine on `poi_id`. The select applies the value only when `source_name = 'partner'`.
- If an upstream key is violated, `pk_duplicate` blocks the commit, the node is FAILED, and the edge watermarks do not advance.

## Ordering

### `enrinfopy` (one cell, one lock)

1. Merge the lock row if it is missing (as `entwebpy` does), then take the `wm_flow__` lock.
2. Preconditions:
   - the `nb_name` column exists (`enrddlpy` has run);
   - `slv_poi_entity_non_enrich`, `slv_poi_amenity`, and `slv_pn_business_service_i18ns` exist.
3. Schema step:
   - table missing: create it with the init DDL;
   - schema == new contract: no-op;
   - names == the old 23 (`OLD_INFO_NAMES`): raise "DEV reset first" and touch nothing;
   - anything else: raise and touch nothing.
4. Insert the 3 new edges (`WHERE NOT EXISTS` on the logical key).
5. Set the 6 old edges to `is_active = 0` where `is_active <> 0`.
6. Verify I6. On mismatch, raise. The cell never re-enables an edge.
7. Release the lock in `finally`, only if this run still owns it.

The schema step runs before the edge step on purpose:
- On the old contract the cell stops before any ctrl write, so ctrl still matches the old notebook.
- If the edge step fails after the create, the info node fails loudly with `ConfigError` ("spec.inputs lệch config"). A re-run converges.

### DEV deployment order

The runbook (§Rollout) does these steps in this order. Each step depends on the one before it.
1. Pause the ENR trigger.
2. Sync the notebooks.
3. Pre-state probe (R-1).
4. Lock-free check (R-2).
5. Drop the info table (R-3).
6. Delete the info `wm_e__` rows (R-4).
7. Run `enrinfopy` only.
8. Run `NB_SETUP_INITIAL_DDL` with `p_apply = false` as a read-only check.
9. NB_00 PLAN, then RUN, then the checks, then a second RUN.
10. Resume the trigger.

Order rules:
- Do not re-run `enrddlpy`.
  - Between R-3 and `enrinfopy`, it would create the old contract. `enrinfopy` would then refuse, and R-1..R-4 must be repeated.
  - After `enrinfopy`, its column check raises (`enrddlpy` line "lệch cột hoặc nullability").
- Do not run `NB_SETUP_INITIAL_DDL` with `p_apply = true` before `enrinfopy`. Running it after is unnecessary.

### Inside the node

1. `_require`: column presence for entity, amenity, price, and i18n.
2. The changed-key union over all roles, semi-joined to the spine and persisted.
3. Inputs restricted to the changed keys.
4. Joins and the select.
5. Lib `_reject_append_build`, `check_append_schema`, QG.
6. One append commit.

## Transaction and commit boundaries

- Node: one Delta append commit per successful run, carrying the lib `vv_append` marker.
  - Edge watermarks advance in a separate NB_00 MERGE after `runMultiple`.
  - If a crash happens between the two, the next run's baseline is the max of EDGE and MARKER (`choose_append_baseline`). Nothing is appended twice.
- `enrinfopy`: each statement is its own Delta commit, and there is no cross-table transaction. Correctness relies on:
  - the flow lock;
  - idempotent steps;
  - the schema step running before the edge step;
  - any half state making the info node fail loudly.
- DEV reset: R-3 (DROP) and R-4 (DELETE) are two separate commits on two tables. Either order leaves a safe state (§Partial failure). The runbook runs R-3 first, as the CTRL doc does.
- After R-3, the recreated table has a new Delta table id and empty history. `find_append_marker` finds no marker, so baselines come only from edges. After R-4 no edge rows exist, so every role is FULL.

## Idempotency

- `enrinfopy` re-run:
  - the schema matches, so no create;
  - INSERT WHERE NOT EXISTS inserts 0 rows;
  - the UPDATE matches 0 rows;
  - verify passes;
  - no new commit on `gld_enr_poi_info`.
- `NB_SETUP_INITIAL_DDL` uses MERGE WHEN NOT MATCHED only, so a re-run inserts nothing.
- Runbook R-3 uses `DROP TABLE IF EXISTS` and R-4 deletes by an explicit id list, so both can be retried.
  - R-3 may run only when R-1 shows the old 23 names.
  - If `enrinfopy` has already created the new table, skip R-3 and R-4. Re-dropping would only discard the refresh.
- Node:
  - No source change: every `ctx.changed` is empty, the build has 0 rows, and the lib logs "APPEND 0 dòng -> không ghi".
  - A retry with the same `exec_id` is absorbed by the marker.
  - First run after the reset: all 7 roles are FULL (no edge rows, no marker). Every live entity POI is emitted once, which is the intended init-like refresh.

## Concurrency

- NB_00, manual node runs, and `enrinfopy` share the `wm_flow__` lock.
  - If NB_00 holds a fresh lock, the cell raises "đang giữ khoá" and the operator re-runs it later.
  - The 35-minute lease matches NB_00's `_lock_expired_sql(p_lock_timeout_min)`.
- Runbook R-3/R-4 do not take the lock. They rely on the paused trigger plus R-2: the lock is NULL or older than 35 minutes, and no ENR run is in progress in the Fabric monitor.
  - If an ENR run still starts between R-3 and `enrinfopy`, the info node raises `ConfigError` "chưa có bảng đích, tạo bằng NB_CREATE_DDL" (lib APPEND precondition) and writes nothing.
  - Review and coordinate run as before. Coordinate edges are still active until `enrinfopy`, which is harmless.
- `PL_VV_TRANS_SLV_TO_SLV_1H` writes entity and amenity while ENR reads them.
  - Reads are pinned to Delta versions (`read_versions`).
  - Entity and amenity can be read at versions from different 1H runs. The next amenity change re-emits the POI (I9), so gold converges.
- Cadence: `_15P` does not match `CADENCE_RE`, so `build_dag` skips the faster-reads-slower check with a WARN (documented in NB_00). Reading 1H tables is safe because the reads are pinned and APPEND emits only changed keys.
- 1H is run by hand today, so entity-driven gold columns refresh only after a 1H run. Tell the user about this freshness consequence of D-01.

## Retry and recovery

- Node failure (QG block, `ConfigError`, timeout):
  - nothing is appended and the edge watermarks keep their versions;
  - the next run recomputes the same changed set plus any newer changes;
  - for a full re-emission, run NB_00 with `p_force_nodes = 'gld_enr_poi_info'`.
- Source version vacuumed: `ctx.changed` falls back to `FULL_VERSION_UNAVAILABLE`. `_amenity_keys` reads the basis after calling `ctx.changed`, then returns all spine keys. Full emission is correct here.
- `enrinfopy` failure: re-run the cell. A lock left by a killed session expires after 35 minutes.
- The first full run takes longer than `p_node_timeout_min` (15): re-run NB_00 by hand with a larger `p_node_timeout_min`, at most `p_dag_timeout_min`. The runbook records the duration.

## Partial failure

| State | Effect | Recovery |
|---|---|---|
| Notebooks synced, R-3 not done | `enrinfopy` raises "hợp đồng cũ"; info node `ConfigError` (`check_append_schema`); review OK | do R-1..R-4, then `enrinfopy` |
| R-3 done, R-4 not done | old edge rows keep versions with the old source table ids. Entity, amenity, and i18n are FULL anyway, so all POIs are emitted | do R-4 (idempotent); otherwise harmless |
| R-3 done, `enrinfopy` not run | info node `ConfigError` "chưa có bảng đích"; no write | run `enrinfopy` |
| `enrddlpy` re-run after R-3 | old contract recreated, empty | repeat R-1..R-4, then `enrinfopy` |
| Table created, edge step failed | info node `ConfigError` (inputs mismatch) | re-run `enrinfopy` (schema no-op; edges converge) |
| Table created, first RUN not successful yet | `gld_enr_poi_info` empty for consumers | run NB_00 at once. The trigger pause lasts only minutes. DEV only (D-18) |
| Upstream duplicate key | `pk_duplicate` blocks; no write | fix upstream; never auto-pick |
| Partner `amentities` shape differs | `partner_opening_hours_null` warn is high; rows are still written | probe P-4; return to the user if confirmed |
| Table has neither the new nor the old contract | `enrinfopy` raises; nothing written | stop; return to the Architect |

## Observability

- Lib `qg_json` per run:
  - `basis` and `changed` per role;
  - `rows`;
  - `block_checks`: `json_text_null`, `cost_vnd_mismatch`, `google_cols_not_google`, `opening_hours_other_source`;
  - `warn_checks`: `cost_null`, `time_to_spend_unfixed`, `partner_opening_hours_null`;
  - the warn `review_poi_not_in_entity`, renamed from `review_poi_not_in_slv_3p_poi`.
- `enrinfopy` prints:
  - whether it created the table or found the new contract;
  - the final active edge sources.
  - On the old contract, it raises with the exact runbook pointer.
- NB_00 `RUN_SUMMARY` lists the nodes that ran. The proof uses it to show that coordinate is absent.
- The runbook saves R-1 (pre-state) to `evidence/results/` before R-3. After the DROP it is the only record of the old table.

## Security

- No secrets and no personal data.
- `enrinfopy` builds SQL from in-cell constants and a uuid lock id only; there is no external input.
- JSON text is produced by Spark `to_json`, which escapes values.
- R-3/R-4 run only in the DEV workspace. The runbook's first step confirms the workspace. If it is not DEV, stop.
- Runtime samples follow the AGENTS §6 limits: aggregates, at most 50 rows.

## Rollout

1. Implement, run the local tests, then the reviews (sql-data, spark-runtime, state-correctness) and the risk gate.
2. Commit `docs/context/3p-google/mapping_gld_enr_poi_info.md`. It is untracked, and `test_info_labels_match_mapping` reads it.
3. `run-author --kind runbook` writes these steps on Fabric DEV.
   1. Confirm the workspace is DEV. Pause the `PL_VV_TRANS_SLV_TO_ENR_15P` trigger.
   2. Sync the notebooks from git.
   3. R-1 pre-state (save to `evidence/results/`). Continue only if the info column names are the 23 `OLD_INFO_NAMES`. If they already equal the new contract, skip R-3 and R-4.
      - `DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_info LIMIT 1`;
      - `SELECT count(*), min(created_at), max(created_at) FROM lh_vv_gold.enr.gld_enr_poi_info`;
      - the column names (`DESCRIBE TABLE`);
      - `DESCRIBE HISTORY lh_vv_gold.enr.gld_enr_poi_coordinate LIMIT 1`;
      - `SELECT watermark_id, last_src_version FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id LIKE 'wm_e%' AND trg_tbl IN ('gld_enr_poi_info', 'gld_enr_poi_coordinate')`;
      - `SELECT src_tbl, trg_tbl, is_active FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'`.
   4. R-2 lock-free check: `SELECT lock_exec_id, lock_at FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id = 'wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P'`.
      - `lock_exec_id` must be NULL or `lock_at` older than 35 minutes;
      - the Fabric monitor must show no ENR run in progress.
   5. R-3 and R-4: run the SQL in §Implementation plan > Runbook SQL.
   6. Run cell `enrinfopy` only. It prints "đã tạo".
   7. Run `NB_SETUP_INITIAL_DDL` with `p_apply = false`. It is read-only; its plan output must show no schema issue for `gld_enr_poi_info`.
   8. NB_00 `p_mode = PLAN`, then `RUN`, then the checks in §Verification, then a second `RUN`.
   9. Resume the trigger.
4. Other environments: `enrinfopy` refuses the old contract. Do not apply R-3 there without a new user decision.

## Rollback and forward recovery

- Forward recovery is preferred:
  - re-run `enrinfopy`;
  - fix the notebook;
  - `p_force_nodes = 'gld_enr_poi_info'` re-emits all POIs.
  - The silver sources are intact, so the refresh can always be regenerated.
- Data rollback is impossible after R-3. The DROP removes the table and its Delta history, and D-18 accepts this on DEV.
  - The lost rows came from the outdated logic: `time_to_spend` was always "Không cố định", and `cost` and `best_time_*` were always NULL.
  - R-1 keeps the count and the date range.
- Contract rollback (DEV, trigger paused):
  1. Revert the task commit and sync.
  2. Repeat R-2..R-4.
  3. Re-run `enrddlpy`. It creates the old contract, and its NOT EXISTS inserts nothing.
  4. `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 1` for the 3 `EDGES_OFF` info rows, and for the 3 coordinate rows only if the user wants coordinate back.
  5. `SET is_active = 0` for the 3 `EDGES_ON` rows.
  6. Run NB_00. The old logic re-emits every POI from current silver (FULL).
- Git: revert the task commit. `NB_SETUP_INITIAL_DDL` affects only empty environments.

## Alternatives and trade-offs

1. Putting the new info contract in place on DEV (D-18 fixes the outcome: drop and recreate as init, no `CREATE OR REPLACE`).
   - (a) Selected: the DROP plus `wm_e__` cleanup as runbook SQL, then `enrinfopy` creates the table with the init DDL.
     - It follows the documented DEV node reset and keeps rules 4–5 of §2.1, so neither notebook carries a DROP.
     - It cannot destroy data in an environment D-18 does not cover.
     - Cost: two manual SQL statements. They are not unit-testable, so R-1/R-2 preconditions and the evidence capture guard them.
   - (b) Rejected: a guarded DROP inside `enrinfopy`. It is testable, but it violates §2.1 rule 5, it reintroduces a DROP cell (rule 4), and it would fire in any environment that still has the old contract.
   - (c) Rejected: R-3, then running `NB_SETUP_INITIAL_DDL` `p_apply = true` to recreate the table.
     - It checks and seeds all 14 tables, so unrelated DEV drift can block it.
     - Its MERGE NOT MATCHED cannot set `is_active = 0`, so `enrinfopy` is still needed.
     - Instead, step 3.7 runs it read-only to prove that DEV equals init.
   - (d) Rejected by D-18: `CREATE OR REPLACE`, which was round 1.
   - (e) Rejected: column mapping plus `ALTER DROP/RENAME COLUMN`. The protocol upgrade is irreversible, and earlier tasks rejected it.
   - (f) Rejected: back up the old rows to a `_bak` table first. It adds an unowned table. D-18 says to recreate as init, and the old values were placeholders. Offer it to the user only if they ask.
2. Watermark cleanup in R-4.
   - Selected: delete all 10 `wm_e__gld_enr_poi_info__*` ids, the 7 old edges plus the 3 new ones in case of a retry.
     - The result matches init, which seeds no edge rows: every role is FULL and the evidence is clean.
   - Rejected: keep the rows. That is correct too, since entity FULL drives all keys, but the roles would show mixed EDGE/FULL. The CTRL doc procedure says to delete them.
   - `wm_flow__` and the coordinate rows are never deleted.
3. Detecting amenity removals.
   - Selected: a backward diff `old.subtract(current)` on top of the forward-only `ctx.changed`. It reuses `ctx._input_at` and `_align_snapshot` (private, commented).
   - Rejected: forward-only, which leaves a POI stale after its last flag disappears.
   - Rejected: a full recompute every 15 minutes, which defeats APPEND.
4. Retiring edges.
   - Selected: `is_active = 0`. It is reversible, keeps the audit trail, and `enrddlpy`'s NOT EXISTS will not re-insert the rows.
   - Rejected: `DELETE`, because a later `enrddlpy` run would re-insert the edges as active.
5. Separator in `canonical_candidate`.
   - Selected: accept `-` and the en dash U+2013. The repo seed `BEST_TIME_CANONICAL` stores `Month 11–4`, and mapping §1.2 shows `Month 11-3` (decision history 2026-10-21).
6. D-17 join helper.
   - Selected: the lib `uuid_md5`, the same function and argument order as N6. A test pins both cells.
   - Rejected: re-implementing md5 formatting in gold, which risks drift from N6.

## Implementation plan

### Code A — `NB_ENR_POI_INFO` cell `36415d3b` (replace the whole cell)

- Remove `_duration_label`, `_blank`, `_destination_context`.
- Keep `_keys` and `_review_json` exactly as today, including the `COL-048` comment. The `_review_json` placeholder line below means: paste the current function there verbatim.
- `F`, `Window`, `StorageLevel`, `ConfigError`, `NodeContext`, `NodeSpec`, `DataFrame`, `_align_snapshot`, and `uuid_md5` come from `%run NB_LIB_TRANSFORM_SLV_GLD`.
- `BEST_TIME_RE` contains a literal en dash inside `[-–]`.

```python
# [SỬA 21/10] 20261021-refresh-gld-enr-poi-info: nguồn slv_poi_entity_non_enrich (D-01). Bỏ slv_3p_poi, address, contact.
# BEGIN_INFO_PURE
# Mục 2 mapping_gld_enr_poi_info.md: (time_to_spend, best_time, cost_vnd). Khớp đúng chữ; sector lạ hoặc NULL -> other.
SECTOR_LABELS = {
    "accommodation": ("Thời gian lưu trú lý tưởng", "Mùa lưu trú đẹp nhất", "Giá phòng tham khảo"),
    "f_n_b": ("Thời gian dùng bữa", "Thời điểm nên ghé", "Mức giá tham khảo"),
    "attraction": ("Thời gian tham quan", "Mùa đẹp nhất", "Chi phí tham quan"),
    "tour_n_activities": ("Thời lượng hoạt động", "Thời điểm phù hợp", "Chi phí tham khảo"),
    "shopping_n_retail": ("Thời gian mua sắm", "Thời điểm nên ghé", "Chi tiêu tham khảo"),
    "transport_route_base": ("Thời gian đưa đón", "Thời điểm phù hợp", "Chi phí đưa đón"),
    "transport_on_demand": ("Thời gian thuê phổ biến", "Thời điểm nên thuê", "Giá thuê tham khảo"),
    "vehicle_rental": ("Thời gian thuê phổ biến", "Thời điểm nên thuê", "Giá thuê tham khảo"),
    "spa_n_wellness": ("Thời lượng liệu trình", "Thời điểm phù hợp", "Giá dịch vụ tham khảo"),
    "event": ("Thời lượng chương trình", "Thời điểm nên xem", "Giá vé tham khảo"),
}
SECTOR_OTHER = ("Thời lượng trải nghiệm", "Thời điểm phù hợp", "Chi phí tham khảo")
# Mục 1.2. Seed ghi "Month 11–4" (gạch dài), mapping ghi "Month 11-3": nhận cả hai, tháng 1–12.
BEST_TIME_RE = r"^Month ([1-9]|1[0-2])[-–]([1-9]|1[0-2])$"
GOOGLE, PARTNER = "google", "partner"
REQUIRED_COLS = {
    "entity": ("poi_id", "source_name", "source_id", "language_code", "website_url", "ward", "city",
               "avg_range_min", "canonical_candidate"),
    "amenity": ("poi_id", "service_flags"),
    "price": ("poi_id", "price_level", "price_min", "price_max"),
    "i18n": ("business_service_id", "locale", "amentities", "deleted"),
}
# END_INFO_PURE


def _keys(frame, column):
    return frame.select(F.col(column).alias("poi_id")).where(F.col("poi_id").isNotNull()).distinct()


def _label(sector, k):
    # RULE-003. k: 0 time_to_spend, 1 best_time, 2 cost_vnd.
    expr = None
    for name, labels in SECTOR_LABELS.items():
        cond = sector == F.lit(name)
        expr = F.when(cond, F.lit(labels[k])) if expr is None else expr.when(cond, F.lit(labels[k]))
    return expr.otherwise(F.lit(SECTOR_OTHER[k]))


def _time_to_spend_text(minutes, sector):
    # D-16, mục 1.1: xét đúng thứ tự nhánh.
    hours = F.floor(minutes / 60).cast("int")
    rest = minutes % 60
    return (F.when(minutes.isNull() | (minutes <= 0), F.lit("Không cố định"))
             .when(sector == F.lit("accommodation"), F.concat(F.ceil(minutes / 1440).cast("string"), F.lit(" ngày")))
             .when((sector == F.lit("tour_n_activities")) & (minutes > 420), F.lit("Cả ngày"))
             .when(minutes < 60, F.concat(minutes.cast("string"), F.lit(" phút")))
             .when(minutes == 60, F.lit("1 tiếng"))
             .when(rest == 0, F.concat(hours.cast("string"), F.lit(" tiếng")))
             .otherwise(F.concat(hours.cast("string"), F.lit(" tiếng "), rest.cast("string"), F.lit(" phút"))))


def _best_time_text(candidate):
    # D-05, mục 1.2: From-To theo thứ tự trong chuỗi; còn lại Quanh năm.
    value = F.trim(candidate)
    return (F.when(value.rlike(BEST_TIME_RE),
                   F.concat(F.lit("Tháng "), F.regexp_extract(value, BEST_TIME_RE, 1),
                            F.lit(" - Tháng "), F.regexp_extract(value, BEST_TIME_RE, 2)))
             .otherwise(F.lit("Quanh năm")))


def _cost(price_min, price_max):
    # COL-007. D-08, D-10, mục 1.9.3 mapping_place_type.md: đủ hai giá mới tính. Không gọi LLM.
    both = price_min.isNotNull() & price_max.isNotNull()
    return F.when(both, F.round((price_min + price_max) / F.lit(2), 0)).cast("bigint")


def _cost_vnd(cost, sector):
    # D-11, D-15, mục 1.3: làm tròn half-up về nghìn, "Từ 546,000đ". cost NULL -> chuỗi JSON null (D-09, D-10).
    rounded = (F.round(cost.cast("decimal(20,0)") / F.lit(1000), 0) * F.lit(1000)).cast("bigint")
    text = F.concat(F.lit("Từ "), F.format_number(rounded, 0), F.lit("đ"))
    return F.when(cost.isNull(), F.lit("null")).otherwise(F.to_json(F.create_map(_label(sector, 2), text)))


# _review_json: giữ nguyên hàm hiện tại (chép đúng thân hàm và comment COL-048).


def _service_flag(amenity, keys):
    # D-12: một dòng / poi_id: mảng JSON giá trị khác nhau, bỏ NULL, sort tăng dần. Không có dòng -> [] ở build.
    return (amenity.join(keys, "poi_id", "left_semi").groupBy("poi_id")
            .agg(F.to_json(F.array_sort(F.collect_set("service_flags"))).alias("service_flag")))


def _vi_i18n(frame):
    # D-17: chỉ locale = vi. i18n không có poi_id: poi_id partner = uuid_md5(business_service_id, 'partner'),
    # cùng hàm và thứ tự đối số với _partner của NB_SLV_POI_ENTITY_NON_ENRICH.
    return (frame.where(F.col("locale") == F.lit("vi"))
            .withColumn("poi_id", uuid_md5(F.col("business_service_id"), F.lit(PARTNER))))


def _partner_hours(ctx):
    # D-17: bỏ dòng deleted = true (như _live của N6). Không có key policies.operating_hours -> NULL.
    live = ctx.input("i18n").where(~F.coalesce(F.col("deleted"), F.lit(False)))
    return _vi_i18n(live).select(
        "poi_id", F.get_json_object(F.col("amentities"), "$.policies.operating_hours").alias("partner_hours"))


def _i18n_keys(ctx):
    # D-17: bản i18n vi đổi, kể cả deleted = true -> poi_id partner. build lọc lại theo spine.
    return _keys(_vi_i18n(ctx.changed("i18n")), "poi_id")


def _amenity_keys(ctx, spine_keys):
    # D-12: dòng amenity bị xoá mềm làm đổi service_flag nhưng ctx.changed chỉ thấy dòng đang có.
    # Thêm poi_id của dòng có ở baseline mà không còn ở version đọc. Không có baseline -> mọi POI.
    forward = _keys(ctx.changed("amenity"), "poi_id")  # gọi trước: có thể đổi basis sang FULL_VERSION_UNAVAILABLE
    info = ctx.basis["amenity"]
    if info["basis"] not in ("EDGE", "MARKER") or info["from"] is None:
        return spine_keys
    if info["from"] >= info["to"]:
        return forward
    current = ctx._input_at("amenity", info["to"])
    old = _align_snapshot(current, ctx._input_at("amenity", info["from"]))
    return forward.union(_keys(old.subtract(current), "poi_id"))


def _require(ctx):
    for role, cols in REQUIRED_COLS.items():
        have = {c.lower() for c in ctx.input(role).columns}
        missing = [c for c in cols if c not in have]
        if missing:
            raise ConfigError(f"gld_enr_poi_info: {ctx.spec.inputs[role]} thiếu cột {missing}")


def build(ctx: NodeContext) -> DataFrame:
    _require(ctx)
    spine = ctx.input("entity")  # D-04: lib đã bỏ dòng xoá mềm và row_hash, created_at, updated_at, deleted_at
    spine_keys = spine.select("poi_id")
    changed = _keys(ctx.changed("entity"), "poi_id")
    for role in ("rating", "price", "hours", "review"):
        changed = changed.union(_keys(ctx.changed(role), "poi_id"))
    changed = (changed.union(_amenity_keys(ctx, spine_keys)).union(_i18n_keys(ctx))
               .distinct().join(spine_keys, "poi_id", "left_semi")).persist(StorageLevel.MEMORY_AND_DISK)
    ctx.cached.append(changed)
    dropped = _keys(ctx.changed("review"), "poi_id").join(spine_keys, "poi_id", "left_anti").count()
    ctx.warn("review_poi_not_in_entity", dropped)
    e = spine.join(changed, "poi_id", "left_semi").alias("e")
    am = _service_flag(ctx.input("amenity"), changed).alias("am")
    r = ctx.input("rating").alias("r")
    pr = ctx.input("price").alias("pr")
    oh = ctx.input("hours").alias("oh")
    rj = _review_json(ctx.input("review").join(changed, "poi_id", "left_semi")).alias("rj")
    ph = _partner_hours(ctx).join(changed, "poi_id", "left_semi").alias("ph")
    base = (e.join(am, F.col("e.poi_id") == F.col("am.poi_id"), "left")
             .join(r, F.col("e.poi_id") == F.col("r.poi_id"), "left")
             .join(pr, F.col("e.poi_id") == F.col("pr.poi_id"), "left")
             .join(oh, F.col("e.poi_id") == F.col("oh.poi_id"), "left")
             .join(rj, F.col("e.poi_id") == F.col("rj.poi_id"), "left")
             .join(ph, F.col("e.poi_id") == F.col("ph.poi_id"), "left"))
    source = F.lower(F.trim(F.col("e.source_name")))
    google = source == F.lit(GOOGLE)
    sector = F.col("e.business_sector")
    cost = _cost(F.col("pr.price_min"), F.col("pr.price_max"))
    # COL-009 — created_at do lib gán batch_ts. COL-010 — updated_at do lib gán batch_ts.
    return base.select(
        # BEGIN_INFO_SELECT
        F.col("e.poi_id").alias("poi_id"),  # COL-001 — D-01
        F.col("e.source_name").alias("source_name"),
        F.col("e.source_id").alias("source_id"),
        F.col("e.language_code").alias("language_code"),
        F.col("e.poi_name").alias("poi_name"),  # COL-035
        F.col("e.poi_name_normalized").alias("poi_name_normalized"),
        F.col("e.types_json").alias("types"),  # COL-036 — D-13
        F.col("e.operating_status").alias("operating_status"),
        F.col("e.primary_type").alias("primary_type"),
        F.col("e.website_url").alias("website_url"),  # COL-039 — D-04
        F.col("e.house_number").alias("house_number"),
        F.col("e.street").alias("street"),
        F.col("e.ward").alias("ward"),
        F.col("e.ward").alias("district"),  # COL-041 — D-06
        F.col("e.city").alias("city"),
        F.col("e.city").alias("destination_name"),  # COL-042 — D-06
        F.col("e.full_address").alias("full_address"),
        F.col("e.lat").alias("lat"),
        F.col("e.lng").alias("lng"),
        F.col("e.business_sector").alias("business_sector"),  # COL-037
        F.col("e.business_category").alias("business_category"),  # COL-038
        F.col("e.business_category_vi").alias("business_category_vi"),
        F.col("e.category_group").alias("category_group"),
        F.col("e.range_low_min").alias("range_low_min"),
        F.col("e.range_high_min").alias("range_high_min"),
        F.col("e.avg_range_min").alias("avg_range_min"),
        F.col("e.candidate_best_time_code").alias("candidate_best_time_code"),
        F.col("e.canonical_candidate").alias("canonical_candidate"),
        F.when(google, F.col("r.rating_overall")).alias("rating"),  # COL-044 — D-07, D-17
        F.when(google, F.col("r.rating_count")).alias("user_rating_count"),  # COL-045 — D-07
        F.when(google, F.col("pr.price_level")).alias("price_level"),  # COL-046 — D-07
        F.when(google, F.col("oh.periods_json"))
         .when(source == F.lit(PARTNER), F.col("ph.partner_hours")).alias("opening_hours_text"),  # COL-047 — D-17
        F.when(google, F.coalesce(F.col("rj.review_json"), F.lit("[]"))).alias("review_json"),  # COL-048 — D-07
        F.to_json(F.create_map(_label(sector, 0), _time_to_spend_text(F.col("e.avg_range_min"), sector)))
         .alias("time_to_spend"),  # COL-003 — D-16
        F.to_json(F.create_map(_label(sector, 1), _best_time_text(F.col("e.canonical_candidate"))))
         .alias("best_time"),  # D-05
        cost.alias("cost"),  # COL-007 — D-08
        _cost_vnd(cost, sector).alias("cost_vnd"),  # D-15
        F.coalesce(F.col("am.service_flag"), F.lit("[]")).alias("service_flag"),  # D-12
        # END_INFO_SELECT
    )


SPEC = NodeSpec(
    trg_tbl="gld_enr_poi_info",
    inputs={
        "entity": "slv_poi_entity_non_enrich", "amenity": "slv_poi_amenity",
        "rating": "slv_3p_poi_rating", "price": "slv_3p_poi_price", "hours": "slv_3p_poi_opening_hours",
        "review": "slv_3p_poi_review", "i18n": "slv_pn_business_service_i18ns",
    },
    pk=("poi_id",),
    build=build,
    required_inputs=("entity",),
    block_checks=(
        ("json_text_null", "time_to_spend IS NULL OR best_time IS NULL OR cost_vnd IS NULL OR service_flag IS NULL"),
        ("cost_vnd_mismatch", "(cost IS NULL) <> (cost_vnd = 'null')"),
        ("google_cols_not_google", "coalesce(lower(trim(source_name)), '') <> 'google' AND (rating IS NOT NULL "
                                   "OR user_rating_count IS NOT NULL OR price_level IS NOT NULL OR review_json IS NOT NULL)"),
        ("opening_hours_other_source", "coalesce(lower(trim(source_name)), '') NOT IN ('google', 'partner') "
                                       "AND opening_hours_text IS NOT NULL"),
    ),
    warn_checks=(
        ("cost_null", "cost IS NULL"),
        ("time_to_spend_unfixed", "avg_range_min IS NULL OR avg_range_min <= 0"),
        ("partner_opening_hours_null", "lower(trim(source_name)) = 'partner' AND opening_hours_text IS NULL"),
    ),
    write_mode="APPEND",
)
```

Notes on Code A:
- Types, verified against `init_tables` and `TABLE_CONFIGS_3P`:
  - `price_min` and `price_max` are `decimal(18,2)`, so `/2` and `round(…,0)` are HALF_UP decimal arithmetic, and `cast("bigint")` matches `BIGINT`.
  - `rating_overall` is `decimal(4,2)`, `rating_count` is `bigint`, `price_level` is `int`.
  - `F.when` without `otherwise` keeps the source type, so no void column reaches `_reject_append_build`.
- `slv_poi_amenity.service_flags` is a scalar `STRING` (`init_tables`). `collect_set` drops NULLs, and an all-NULL POI gives `[]`.
- `slv_pn_business_service_i18ns` is an L1 CDC table with a `deleted` flag and no `row_hash`/`deleted_at`. `ctx.input` therefore returns all rows, and `_partner_hours` filters `deleted` itself. `ctx.changed("i18n")` includes a row whose `deleted` became true.
- Rounding checks (D-11): 545899 → 546,000; 5455 → 5,000. `format_number(x, 0)` uses comma grouping.
- The `.alias("…")` names between the select markers must stay in `INFO_COLS` order. A test enforces this.
- Markdown cell `8cef70ac`: `APPEND lh_vv_gold.enr.gld_enr_poi_info từ lh_vv_silver.dbo.slv_poi_entity_non_enrich.`

### Code B — `NB_CREATE_DDL` new cells (append after `entwebpy`)

- Markdown cell `enrinfomd`: `# [THÊM 21/10] 20261021-refresh-gld-enr-poi-info`.
- Code cell `enrinfopy`:
  - `PROPS`, `INFO_COLS`, `OLD_INFO_NAMES`, `EDGES_OFF`, `EDGES_ON`, `INFO_ACTIVE` stay pure literals, because the tests read them with `ast.literal_eval`.
  - The cell text must not contain `DROP`, `DELETE`, `TRUNCATE`, `ALTER TABLE`, `REPLACE`, or `RESTORE` (uppercase). The lowercase `str.replace` is fine.
  - Do not write a literal `CREATE TABLE IF NOT EXISTS lh_vv_…`. The f-string keeps `{INFO_FQ}`, so `test_table_inventory_matches_sources` does not count it twice.

```python
# [THÊM 21/10] 20261021-refresh-gld-enr-poi-info
# 1. gld_enr_poi_info: hợp đồng cột mới, nguồn slv_poi_entity_non_enrich. Chưa có bảng -> tạo đúng định nghĩa
#    của NB_SETUP_INITIAL_DDL. Đã đúng hợp đồng mới -> không đổi. Còn 23 cột cũ của enrddlpy -> dừng, không sửa:
#    DEV làm bước reset trong runtime-runbook.md của task (D-18) rồi chạy lại cell. Hợp đồng khác -> dừng.
# 2. Cạnh PL_VV_TRANS_SLV_TO_ENR_15P: tắt (is_active = 0, giữ dòng) 3 cạnh 3P -> info và 3 cạnh -> coordinate;
#    thêm 3 cạnh entity / amenity / i18n -> info. Bảng gld_enr_poi_coordinate giữ nguyên.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P suốt cell. Chạy lại: không đổi gì.
# Sau cell này không chạy lại enrddlpy: INFO_COLS của enrddlpy là hợp đồng cũ.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_ENR_15P"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.enr"
INFO_FQ = f"{GLD}.gld_enr_poi_info"
PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'"
LEASE_MINUTES = 35  # bằng p_lock_timeout_min của NB_00_ORCHES_SLV_TO_ENR_15P
SOURCES = (f"{SLV}.slv_poi_entity_non_enrich", f"{SLV}.slv_poi_amenity", f"{SLV}.slv_pn_business_service_i18ns")

INFO_COLS = [
    ("poi_id", "STRING NOT NULL"),
    ("source_name", "STRING"),
    ("source_id", "STRING"),
    ("language_code", "STRING"),
    ("poi_name", "STRING"),
    ("poi_name_normalized", "STRING"),
    ("types", "STRING"),
    ("operating_status", "STRING"),
    ("primary_type", "STRING"),
    ("website_url", "STRING"),
    ("house_number", "STRING"),
    ("street", "STRING"),
    ("ward", "STRING"),
    ("district", "STRING"),
    ("city", "STRING"),
    ("destination_name", "STRING"),
    ("full_address", "STRING"),
    ("lat", "DOUBLE"),
    ("lng", "DOUBLE"),
    ("business_sector", "STRING"),
    ("business_category", "STRING"),
    ("business_category_vi", "STRING"),
    ("category_group", "STRING"),
    ("range_low_min", "INT"),
    ("range_high_min", "INT"),
    ("avg_range_min", "INT"),
    ("candidate_best_time_code", "STRING"),
    ("canonical_candidate", "STRING"),
    ("rating", "DECIMAL(4,2)"),
    ("user_rating_count", "BIGINT"),
    ("price_level", "INT"),
    ("opening_hours_text", "STRING"),
    ("review_json", "STRING"),
    ("time_to_spend", "STRING"),
    ("best_time", "STRING"),
    ("cost", "BIGINT"),
    ("cost_vnd", "STRING"),
    ("service_flag", "STRING"),
    ("created_at", "TIMESTAMP"),
    ("updated_at", "TIMESTAMP"),
]
OLD_INFO_NAMES = (
    "poi_id", "poi_name", "types", "subcategory_tags", "business_sector", "business_category", "website_url",
    "short_address", "district", "destination_name", "destination_context", "rating", "userRatingCount",
    "priceLevel", "opening_hours_text", "review_json", "time_to_spend", "best_time_type", "best_time_from_month",
    "best_time_to_month", "cost", "created_at", "updated_at",
)
EDGES_OFF = [
    ("slv_3p_poi", "gld_enr_poi_info"),
    ("slv_3p_poi_address", "gld_enr_poi_info"),
    ("slv_3p_poi_contact", "gld_enr_poi_info"),
    ("slv_3p_poi", "gld_enr_poi_coordinate"),
    ("slv_3p_poi_address", "gld_enr_poi_coordinate"),
    ("slv_pn_poi", "gld_enr_poi_coordinate"),
]
EDGES_ON = [
    (1, "slv_poi_entity_non_enrich", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (2, "slv_poi_amenity", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (3, "slv_pn_business_service_i18ns", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
]
INFO_ACTIVE = (
    "slv_poi_entity_non_enrich", "slv_poi_amenity", "slv_3p_poi_rating", "slv_3p_poi_price",
    "slv_3p_poi_opening_hours", "slv_3p_poi_review", "slv_pn_business_service_i18ns",
)

want = [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in INFO_COLS]
body = ",\n    ".join(f"`{name}` {dtype}" for name, dtype in INFO_COLS)
LOCK = "enrinfo-" + uuid.uuid4().hex


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


def _create():
    # Cùng câu với create_sql(spec) của NB_SETUP_INITIAL_DDL cho bảng này (test kiểm tra).
    spark.sql(f"CREATE TABLE IF NOT EXISTS {INFO_FQ} (\n    {body}\n) USING DELTA\nTBLPROPERTIES ({PROPS})")


# Tạo dòng khoá nếu chưa có. Không xoá wm_flow__.
spark.sql(f"""
MERGE INTO {WM} AS t
USING (SELECT '{WID}' AS watermark_id, '{PL}' AS src_tbl, 'NB_CREATE_DDL' AS flow_name) AS s
ON t.watermark_id = s.watermark_id
WHEN NOT MATCHED THEN INSERT
    (watermark_id, src_schema, src_tbl, trg_schema, trg_tbl, watermark_column, watermark_value, last_success_at,
     status, flow_name, watermark_sequence, last_run_id, last_src_version, last_src_table_id, error_message,
     lock_exec_id, lock_at, updated_at)
VALUES
    (s.watermark_id, CAST(NULL AS STRING), s.src_tbl, CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS STRING),
     CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP), 'INITIALIZED', s.flow_name, CAST(NULL AS BIGINT),
     CAST(NULL AS STRING), CAST(NULL AS BIGINT), CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS STRING),
     CAST(NULL AS TIMESTAMP), current_timestamp())
""")
held = False
failed = None
try:
    spark.sql(f"""
    UPDATE {WM}
    SET lock_exec_id = '{LOCK}', lock_at = current_timestamp(), status = 'RUNNING', updated_at = current_timestamp()
    WHERE watermark_id = '{WID}' AND (
        lock_exec_id IS NULL
        OR coalesce(lock_at < current_timestamp() - INTERVAL {LEASE_MINUTES} MINUTES, true))
    """)
    owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
    if not owner or owner["lock_exec_id"] != LOCK:
        other = None if owner is None else owner["lock_exec_id"]
        raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")
    held = True
    if "nb_name" not in {f.name.lower() for f in spark.table(CFG).schema.fields}:
        raise RuntimeError(f"{CFG} chưa có cột nb_name: chạy enrddlpy trước")
    missing = [fq for fq in SOURCES if not spark.catalog.tableExists(fq)]
    if missing:
        raise RuntimeError(f"Chưa có {missing}: chạy NB_SETUP_POI_ENTITY, NB_SETUP_POI_AMENITY trước")

    if not spark.catalog.tableExists(INFO_FQ):
        _create()
        print(f"{INFO_FQ}: đã tạo theo định nghĩa NB_SETUP_INITIAL_DDL")
    got = _schema(INFO_FQ)
    if got != want:
        if [name for name, _dtype, _nullable in got] == [name.lower() for name in OLD_INFO_NAMES]:
            raise RuntimeError(f"{INFO_FQ} còn hợp đồng cũ: DEV làm bước reset trong runtime-runbook.md của task "
                               "(D-18) rồi chạy lại cell. Cell không sửa bảng đã có")
        raise RuntimeError(f"{INFO_FQ} không khớp hợp đồng mới, không sửa: có {got}, cần {want}")

    values = ",\n    ".join(
        f"({seq}, '{src}', '{schema}', '{trg}', '{mode}', '{nb}', {priority})"
        for seq, src, schema, trg, mode, nb, priority in EDGES_ON
    )
    spark.sql(f"""
    INSERT INTO {CFG}
        (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)
    SELECT COALESCE((SELECT MAX(id) FROM {CFG}), 0) + t.seq, '{PL}', '{SLV}', t.src_tbl, t.trg_schema, t.trg_tbl,
           1, t.priority, t.load_mode, CAST(NULL AS STRING), CAST(NULL AS STRING), t.nb_name
    FROM VALUES
        {values}
    AS t(seq, src_tbl, trg_schema, trg_tbl, load_mode, nb_name, priority)
    WHERE NOT EXISTS (
        SELECT 1 FROM {CFG} c
        WHERE c.pl_name = '{PL}' AND c.src_schema = '{SLV}' AND c.src_tbl = t.src_tbl
          AND c.trg_schema = t.trg_schema AND c.trg_tbl = t.trg_tbl)
    """)
    off = " OR ".join(f"(src_tbl = '{src}' AND trg_tbl = '{trg}')" for src, trg in EDGES_OFF)
    spark.sql(f"""
    UPDATE {CFG} SET is_active = 0
    WHERE pl_name = '{PL}' AND src_schema = '{SLV}' AND trg_schema = '{GLD}' AND is_active <> 0 AND ({off})
    """)
    rows = spark.sql(f"""
    SELECT src_tbl, trg_tbl, count(*) AS n FROM {CFG}
    WHERE pl_name = '{PL}' AND is_active = 1 AND trg_schema = '{GLD}'
      AND trg_tbl IN ('gld_enr_poi_info', 'gld_enr_poi_coordinate')
    GROUP BY src_tbl, trg_tbl
    """).collect()
    got_edges = {(row["src_tbl"], row["trg_tbl"]): row["n"] for row in rows}
    want_edges = {(src, "gld_enr_poi_info"): 1 for src in INFO_ACTIVE}
    if got_edges != want_edges:
        raise RuntimeError(f"{CFG}: cạnh active của info / coordinate là {got_edges}, cần {want_edges}. "
                           "Cạnh mới có nhưng đang tắt thì xử lý theo runbook, cell không tự bật")
    print(f"{INFO_FQ}: hợp đồng mới; cạnh active {sorted(src for src, _trg in got_edges)}; coordinate không còn cạnh active")
except Exception as exc:
    failed = exc
    raise
finally:
    if held:
        status = "FAILED" if failed else "SUCCESS"
        detail = "" if failed is None else str(failed).replace("'", " ")[:500]
        spark.sql(f"""
        UPDATE {WM}
        SET lock_exec_id = NULL, lock_at = NULL, status = '{status}', error_message = '{detail}',
            updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
```

Notes on Code B:
- `§2.1` rule 3 says the post-patch check covers only the patch. Here the patch is the whole table contract, so the full schema comparison is the patch check.
- The edge `id` uses `MAX(id) + seq`, the same scheme as `entwebpy` and `_merge_pipeline_config`.

### Code C — `NB_SETUP_INITIAL_DDL`

- `init_tables`, entry `'lh_vv_gold.enr.gld_enr_poi_info'`: replace `cols` with the 40 `INFO_COLS` entries as 3-tuples `(name, dtype, None)`, in the same order. `partition`, `comment`, and `props` stay as they are (`None`, `None`, `PROPS`).
- `init_seed_ctrl`, `PIPELINE_CONFIG_ROWS`:
  - add the comment line `# [SỬA 21/10] 20261021-refresh-gld-enr-poi-info: tắt 6 cạnh (is_active = 0), thêm 3 cạnh vào gld_enr_poi_info.`;
  - set the 6th field to `0` in the 3 rows `slv_3p_poi` / `slv_3p_poi_address` / `slv_3p_poi_contact → gld_enr_poi_info` and in the 3 rows `→ gld_enr_poi_coordinate`;
  - directly after the last coordinate row and before the first `_SLV1H` row, insert:
    - `(_ENR, _S, 'slv_poi_entity_non_enrich', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),`
    - `(_ENR, _S, 'slv_poi_amenity', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),`
    - `(_ENR, _S, 'slv_pn_business_service_i18ns', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),`
- No other cell changes. `init_plan` uses `len(PIPELINE_CONFIG_ROWS)`, so the 57 rows need no other edit. `test_no_destructive_sql` must stay green.

### Code D — tests

`tests/test_enr_poi_contract.py`:
- Add imports `ast`, `re`, `unicodedata`.
- Add these helpers. Match cell ids exactly; do not use a prefix, because `enrinfomd` and `enrinfopy` share one.

```python
def _cell(name: str, cell_id: str) -> str:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    found = [cell for cell in nb["cells"] if cell.get("id") == cell_id]
    assert len(found) == 1, cell_id
    return "".join(found[0]["source"])


def _assign(source: str, name: str):
    for node in ast.parse(source).body:
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == name for t in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(name)


def _info_pure() -> dict:
    info = _cell("NB_ENR_POI_INFO.ipynb", "36415d3b")
    ns: dict = {}
    exec(info[info.index("# BEGIN_INFO_PURE"):info.index("# END_INFO_PURE")], ns)  # noqa: S102
    return ns
```

- Constants:
  - `INFO`: the 40 `(name, dtype)` pairs equal to Code B `INFO_COLS`;
  - `INFO_DROPPED = ("subcategory_tags", "short_address", "destination_context", "best_time_type", "best_time_from_month", "best_time_to_month", "userRatingCount", "priceLevel", "types_json")`;
  - `EDGES_OFF`, `EDGES_ON`, `INFO_ACTIVE`, equal to Code B.
- `test_gold_ddl_matches_mapping` (rewrite):
  - `_assign(enrinfopy, "INFO_COLS") == INFO`;
  - `COORD_COLS` and `REVIEW_COLS` of `enrddlpy` are unchanged (`COORD`, `REVIEW`);
  - no `INFO_DROPPED` name is in `INFO`;
  - no `DROPPED` name is in `REVIEW`.
- `test_mapping_comments_and_edges` (update):
  - the info cell contains COL-001, 003, 007, 009, 010, 035–039, 041, 042, 044–048;
  - it contains none of COL-004, 005, 006, 008, 040, 043;
  - the coordinate and review loops are unchanged;
  - the 13 `EDGES` checks and `count('"APPEND"') == 11` run on the `enrddlpy` text only;
  - `"pn_poi" not in info`.
- New `test_info_patch_cell_edges`:
  - the `EDGES_OFF`, `EDGES_ON`, and `INFO_ACTIVE` literals equal the constants;
  - `EDGES_OFF` ⊆ the (src, trg) pairs of `enrddlpy` EDGES;
  - (active info sources of `enrddlpy` minus `EDGES_OFF`) ∪ the `EDGES_ON` sources == `set(INFO_ACTIVE)`;
  - no remaining active pair targets `gld_enr_poi_coordinate`.
- New `test_info_patch_cell_guards`:
  - `list(OLD_INFO_NAMES)` == the names of `enrddlpy` `INFO_COLS`;
  - none of `"DROP"`, `"DELETE"`, `"TRUNCATE"`, `"ALTER TABLE"`, `"REPLACE"`, `"RESTORE"` is in the cell text;
  - index order: `held = True` < `tableExists(INFO_FQ)` < `OLD_INFO_NAMES]` < `INSERT INTO {CFG}` < `SET is_active = 0` < `finally:`;
  - `"lock_exec_id = '{LOCK}'"` is in the cell;
  - the notebook's last cell id is `enrinfopy` and the one before it is `enrinfomd`.
- New `test_info_select_matches_ddl`: `re.findall(r'\.alias\("(\w+)"\)', block) + ["created_at", "updated_at"]` == the `INFO` names, where `block` is the text between `# BEGIN_INFO_SELECT` and `# END_INFO_SELECT`.
- New `test_info_spec_inputs_match_active_edges`:
  - the values of the `inputs` keyword of `SPEC = NodeSpec(...)`, read with `ast`, equal `set(INFO_ACTIVE)`;
  - `'"slv_3p_poi"'`, `'"slv_3p_poi_address"'`, `'"slv_3p_poi_contact"'` do not appear in the info cell.
- New `test_info_partner_join_matches_entity` (D-17):
  - the info cell contains `uuid_md5(F.col("business_service_id"), F.lit(PARTNER))` and `F.col("locale") == F.lit("vi")`;
  - `_info_pure()["PARTNER"] == "partner"`;
  - `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild` contains `uuid_md5(F.col("id"), F.lit(PARTNER))` and `PARTNER = "partner"`;
  - the info cell does not contain `["source_id", "language_code"]`.
- New `test_info_labels_match_mapping`:
  - parse the mục 2 table of `docs/context/3p-google/mapping_gld_enr_poi_info.md`, skipping the header and separator rows;
  - split the labels on `" / "`;
  - compare with `SECTOR_LABELS` plus `{"other": SECTOR_OTHER}`, after NFC normalization of both sides.
- New `test_best_time_pattern`, with `re.fullmatch(BEST_TIME_RE, value.strip())`:
  - every `BEST_TIME_CANONICAL` value except `all_year` (literal in `NB_SETUP_INITIAL_DDL` cell `init_seed_place_type`) matches, with both groups in 1–12;
  - `all_year` does not match;
  - `Month 11-3` → ("11", "3");
  - `Month 11–4` → ("11", "4");
  - `Month 13-2`, `Month 0-5`, and `""` do not match.

`tests/test_initial_ddl_contract.py`:
- `test_columns_match_sources`: compare `lh_vv_gold.enr.gld_enr_poi_info` with `_assign(_cell(ddl, "enrinfopy"), "INFO_COLS")`. Coordinate and review still compare with `enrddlpy`. The props assert is unchanged.
- New `test_info_patch_create_matches_init`, with `specs, ns = _specs()`, the info spec from `specs`, and `cols = _assign(enrinfopy, "INFO_COLS")`:
  - `ns["create_sql"](spec) == "CREATE TABLE IF NOT EXISTS lh_vv_gold.enr.gld_enr_poi_info (\n    " + ",\n    ".join(f"`{n}` {t}" for n, t in cols) + "\n) USING DELTA\nTBLPROPERTIES (" + PROPS + ")"`;
  - `_assign(enrinfopy, "PROPS") == PROPS`;
  - `r'f"CREATE TABLE IF NOT EXISTS {INFO_FQ} (\n    {body}\n) USING DELTA\nTBLPROPERTIES ({PROPS})"'` is in the `enrinfopy` text.
- `test_pipeline_config_rows_match_sources`:
  - `off = set(_assign(_cell(ddl, "enrinfopy"), "EDGES_OFF"))`;
  - the ENR expected rows use `0 if (src, target) in off else 1`;
  - then append the `EDGES_ON` rows with `1`, before the SLV_1H rows;
  - `len(expected) == 57`.
- New `test_enr_initial_edge_state`, from `PIPELINE_CONFIG_ROWS`:
  - the active `gld_enr_poi_info` sources == `set(INFO_ACTIVE)`;
  - no active row targets `gld_enr_poi_coordinate`;
  - exactly 3 coordinate rows exist;
  - `lh_vv_gold.enr.gld_enr_poi_coordinate` is still in `TABLE_SPECS`.
- `test_table_inventory_matches_sources` is unchanged. `enrinfopy` has no literal FQ after `CREATE TABLE IF NOT EXISTS`, so the inventory stays at 14.

### Runbook SQL (DEV only; for `run-author --kind runbook`, steps R-3 and R-4)

Preconditions:
- R-1 is saved, and the info column names equal the 23 `OLD_INFO_NAMES`;
- R-2 passed;
- the trigger is paused.

```sql
-- R-3 (D-18): chỉ bảng info. Không đụng gld_enr_poi_coordinate.
DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_info;
-- R-4: xoá cạnh của đúng trg_tbl này (CTRL_TABLES_CONTEXT §4). Không xoá wm_flow__, không xoá cạnh coordinate.
DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
WHERE watermark_id IN (
    'wm_e__gld_enr_poi_info__slv_3p_poi', 'wm_e__gld_enr_poi_info__slv_3p_poi_address',
    'wm_e__gld_enr_poi_info__slv_3p_poi_contact', 'wm_e__gld_enr_poi_info__slv_3p_poi_rating',
    'wm_e__gld_enr_poi_info__slv_3p_poi_price', 'wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours',
    'wm_e__gld_enr_poi_info__slv_3p_poi_review', 'wm_e__gld_enr_poi_info__slv_poi_entity_non_enrich',
    'wm_e__gld_enr_poi_info__slv_poi_amenity', 'wm_e__gld_enr_poi_info__slv_pn_business_service_i18ns');
```

Post-checks (P-1 below): the info table does not exist; 0 `wm_e__gld_enr_poi_info__%` rows remain; the coordinate `wm_e__` rows and the `wm_flow__` row match R-1.

## Verification

Local:
- `python -m pytest tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest tests -q`
- `python scripts/vv.py verify 20261021-refresh-gld-enr-poi-info`

Runtime proof (Fabric DEV, through the runbook; aggregates only, at most 50 sample rows):
- P-0: the R-1 pre-state is saved.
- P-1 after R-3 and R-4:
  - `spark.catalog.tableExists('lh_vv_gold.enr.gld_enr_poi_info')` is false;
  - 0 info `wm_e__` rows;
  - coordinate `wm_e__` rows, the `wm_flow__` row, and the `gld_enr_poi_coordinate` version equal R-1.
- P-2 after `enrinfopy`:
  - it printed "đã tạo";
  - the schema equals `INFO_COLS` and `DESCRIBE HISTORY` shows one `CREATE TABLE` commit;
  - the ctrl edges satisfy I6;
  - a second run of the cell prints the "hợp đồng mới" summary and adds no commit to `gld_enr_poi_info` or `ctrl_mng_pipeline_config`.
- P-3: `NB_SETUP_INITIAL_DDL` with `p_apply = false` shows no schema issue for `gld_enr_poi_info`.
- P-4 partner hours:
  - run `SELECT count(*) FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns WHERE locale = 'vi' AND NOT coalesce(deleted, false) AND get_json_object(amentities, '$.policies.operating_hours') IS NOT NULL`;
  - compare with `count(opening_hours_text)` of the partner rows in the first commit. They must be equal, give or take partner POIs that are absent from the live spine.
- P-5: NB_00 `p_mode = PLAN` shows the DAG nodes `slv_pn_poi`, `gld_enr_poi_review`, `gld_enr_poi_info`. `gld_enr_poi_coordinate` is absent.
- P-6: NB_00 `RUN`.
  - `RUN_SUMMARY` shows info and review SUCCESS and no coordinate node;
  - the info `qg_json` basis is FULL for all 7 roles;
  - all block checks are 0;
  - the rows written equal `SELECT count(*) FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich WHERE deleted_at IS NULL` at the pinned version;
  - `SELECT poi_id FROM lh_vv_gold.enr.gld_enr_poi_info GROUP BY poi_id HAVING count(*) > 1` returns 0 rows;
  - the `gld_enr_poi_coordinate` version is unchanged (I10);
  - after the run, 7 `wm_e__gld_enr_poi_info__*` rows exist, one per `INFO_ACTIVE` source.
- P-7: shape aggregates.
  - `SELECT business_sector, avg_range_min, time_to_spend, count(*) … GROUP BY 1,2,3 ORDER BY 4 DESC LIMIT 50`, checked against D-16;
  - `SELECT canonical_candidate, best_time, count(*) … GROUP BY 1,2`: every `Month a–b` / `Month a-b` maps to `Tháng a - Tháng b`;
  - `SELECT cost, cost_vnd … WHERE cost IS NOT NULL LIMIT 20`, plus `count(*) WHERE (cost IS NULL) <> (cost_vnd = 'null')` = 0 (I5);
  - `SELECT service_flag, count(*) … GROUP BY 1 ORDER BY 2 DESC LIMIT 20`;
  - `SELECT source_name, count(opening_hours_text), count(rating), count(review_json), count(price_level) … GROUP BY 1` (I4).
- P-8: a second NB_00 `RUN` with no source commits in between (compare source versions) appends 0 rows and creates no commit on info.
- Resume the trigger.

The amenity-removal path (I9) is covered by the review of `_amenity_keys` and is not provoked on DEV. If a reviewer requires it, add a probe that runs the node with a pinned older amenity version through `p_pinned_json`.
