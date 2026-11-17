RESULT: PASS

## Main brief

### Decision
RESULT: PASS (architecture round 2). U-1 to U-4, P-1, P-3, P-4, and the Copy Job column mapping are closed (D-5, D-9 to D-11).
Change from round 1: the silver and gold schema changes are now in-place Delta overwrite rewrites (`overwriteSchema`, read from pinned `v0`). There is no DROP and no column mapping. Each rewrite checks the result and runs `RESTORE` to `v0` if a check fails (A-11, A-12). This keeps the 3 silver multi_lang rows (D-10) and leaves gold at protocol 1/2. That matters because the Copy Job reads gold by name (D-11).
Whether the Copy Job can be paused does not change any code. It is runtime stop R-0. The PostgreSQL `ALTER` runs right after the gold rewrite, in the same Copy Job interval (A-14).
`model-design.md` stands. Do not re-author it.

### Invariants Main must preserve
- Silver multi_lang gets only `trim(event_type)='LANG'` rows, and destination only `'DESTINATION'` rows. Exact match. No `lit(True)` presence branch.
- One row per (`poi_id`,`lang`) and per `poi_id`. Blank keys are rejected. The MERGE guard is a strict `>` on (`_src_version`, `_event_processed_at`, `_event_id`), with `coalesce(t._src_version,-1)`.
- `destination_id` and `destination_name` are JSON array text, same length and order as `data.destinations`, with null kept. Never `get_json_object('$[*]…')`.
- `country_code` and `postal_code` are not in the registry and are NULL. The extract preflight raises `ConfigError` if a target is missing, still has `cost_vnd` or `street`, or lacks the constant-NULL columns.
- The rewrite cells never use `DROP TABLE`, `columnMapping`, or `RENAME COLUMN`. Each one: row count equal, `EXCEPT ALL` empty in both directions against `v0`, new columns all NULL, props ⊇ before, NOT NULL restored. Any failure → `RESTORE` to `v0`, then raise.
- The gold multi_lang `build` raises `ConfigError` if the gold target still has `cost_vnd`. The check is in `build`, so it runs before the lib's `ensure_target`.
- Gold `full_address`: for destination rows, `coalesce(concat(G1), concat(G2), G3)`. `house_number` or `street` NULL or Spark-`trim` blank → NULL (value itself not trimmed). Partner rows without destination keep the entity `full_address`. Never `concat_ws`. Gold `street` = entity `street` on every row.
- `StoredJsonParser.labelValue` also maps an object with exactly the keys {`text`,`label`} (both textual) to `LabelValue(label, text)`. Other shapes keep today's rule.
- Do not edit `NB_LIB_EXTRACT_RAWDATA`, `NB_LIB_TRANSFORM_SLV_GLD`, historical `NB_CREATE_DDL` cells, or `gld_enr_poi_info`.
- `cost_vnd` must not remain in active notebooks, the PostgreSQL DDL, or Java main. Exceptions: historical cells and the planner's rename map.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | `.ai/tasks/.../decision.md` | `Quyết định hiện hành` D-8 | A-10 superseded. Add A-11 to A-15 (doc §19). Round 2 PASS | Ledger rows exist |
| 2 | `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb` | new, `enr00`–`enr14` | Copy the CMS notebook, then apply doc §17.1: constants incl. `RETIRED_COLS`, classify, projection, preflight, MERGE guard | `test_enr_extract_contract.py` extract tests pass |
| 3 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `TABLE_SPECS`, seed cells | Silver specs (doc §17.3), gold multi_lang `cost`, seeds (doc §17.2) | `test_initial_ddl_contract.py` passes |
| 4 | `notebooks/NB_CREATE_DDL.ipynb` | new `enrbrzcfgmd`/`enrbrzcfgpy` | Insert-if-missing seeds identical to #3 | `test_seed_cells_match_between_ddl_notebooks` passes |
| 5 | `notebooks/NB_CREATE_DDL.ipynb` | new `enrbrzmd`/`enrbrzpy` | Silver rewrite: `BEGIN_REWRITE_PURE` planner plus the cell flow (doc §17.3), 3 locks (doc §9), "do not rerun" list | Planner and silver rewrite tests pass |
| 6 | `notebooks/NB_CREATE_DDL.ipynb` | new `enrgldmd`/`enrgldpy` | Gold rewrite, rename map `{"cost":"cost_vnd"}` only, 30M flow lock, run only from runbook B5.1 | `test_gold_rewrite_rename_map_only_cost` passes |
| 7 | `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` | `srvmlbuild` constants and `build`, `srvmlmd` | `cost`. P2 null. `cost_vnd` guard first in `build` (doc §17.5) | `test_multi_lang_cost_guard` and `test_multi_lang_i18n_only_branch` pass |
| 8 | `notebooks/NB_GLD_SRV_POI_INFO.ipynb` | `srvinfobuild` (`ENT_COLS`, `DEST_COLS`, `from_dest`, metrics, `_require` hint), `srvinfomd` | Formula, blank rule, and street as doc §17.5. Metrics as doc §12 | `test_info_*` and `test_partner_without_destination_branch` pass |
| 9 | `sql/postgres/gld_srv_serve.pg.sql` | header, `apps.srv_poi_multi_lang` line 74 | `cost text`. Header line for the manual `ALTER` (doc §17.6) | Serving contract tests pass |
| 10 | `.../domain/entity/SrvPoiMultiLang.java` | `costVnd` field | `@Column(name="cost") String cost` | Compiles |
| 11 | `.../service/PoiService.java` | lines 180–181 | `getCost`, label `"cost"` | `PoiServiceTest` passes |
| 12 | `.../service/util/StoredJsonParser.java` | `labelValue` | Accept `{text,label}` (doc §17.6) | New `PoiServiceTest` cases pass |
| 13 | `PoiServiceTest.java`, `PoiRepositoryIntegrationTest.java` | `cost_vnd`/`costVnd` uses | `cost`. Shape cases (doc §17.6) | `mvn` passes |
| 14 | `tests/test_enr_extract_contract.py` | new | Every test listed in doc §18 under this file | Passes |
| 15 | `tests/test_gld_srv_poi_contract.py` and the other existing tests | tests named in doc §18 | `cost`, new columns, branch, new tests | `pytest` is green |
| 16 | `docs/context/*.md` | doc §17.7 targets | Mapping, practical_info, CTRL, new notebook doc | Docs match the code |
| 17 | `runtime-runbook.md` | new | R-0, B1–B5, §16 rollback (RESTORE and reverse snippet), §18 runtime checks | The runbook covers every step |

### Order and stop points
1. Record #1 in `decision.md`. Set `scope.files` from doc §20. Rerun the architecture gate.
2. Implement #3–#8 (notebooks; in `NB_CREATE_DDL` the cell order is #4, then #5, then #6). Then #9–#13 (PostgreSQL and API), then #14–#16 (tests and docs), then #17.
3. Local verification (below). Fix until green. Record `PoiRepositoryIntegrationTest` as skipped if Docker is unavailable.
4. STOP (evidence, user): R-0. Copy Job interval, write mode for `apps.srv_poi_multi_lang`, whether it can be paused, and the PostgreSQL and gold baseline counts.
5. STOP (runtime, user): B1 deploy notebooks → B2 `enrbrzpy` (silver) → B3 `enrbrzcfgpy` (seeds) → B4 extract dry run, then real run. Stop if a rewrite is not REWRITTEN or SKIP, `cast_null > 0`, or `other > 0`.
6. STOP (user decision, user executes): B5 window. `enrgldpy` → PostgreSQL `ALTER` with `lock_timeout` → API deploy → NB_00 forced → Copy Job resumes. Then the PostgreSQL count and `count(cost)` checks. If R-0 says truncate-first and no pause: run B5.1–B5.2 inside one Copy Job interval.

### Tests and verification
- `python -m pytest tests -q`
- New `tests/test_enr_extract_contract.py`:
  - `test_presence_routes_by_event_type_exact`, `test_no_lit_true_presence`
  - `test_state_key_row_and_all_keys_checked`, `test_order_columns_version_then_event_processed`
  - `test_merge_guard_strict_tuple`, `test_merge_on_keys`
  - `test_array_projection_uses_from_json_transform_to_json`, `test_no_get_json_object_wildcard`
  - `test_registry_paths_relative_to_data`, `test_registry_columns_match_model_design`
  - `test_const_null_cols_not_in_registry`, `test_config_and_watermark_rows`, `test_seed_cells_match_between_ddl_notebooks`
  - `test_extract_preflight_retired_and_const_null_columns`
  - `test_rewrite_plan_skip_when_equal`, `test_rewrite_plan_renames_cost_vnd`, `test_rewrite_plan_drop_only_allowed`
  - `test_rewrite_plan_rejects_old_and_new_together`, `test_rewrite_plan_type_mismatch_raises`, `test_rewrite_plan_not_null_without_source_raises`
  - `test_rewrite_pure_block_identical_in_both_cells`, `test_rewrite_cells_no_drop_table_columnmapping_rename`
  - `test_rewrite_cells_overwrite_schema_from_pinned_version`, `test_rewrite_cells_restore_on_failed_check`, `test_rewrite_cells_hold_locks`
  - `test_silver_rewrite_targets_match_initial_ddl`, `test_gold_rewrite_rename_map_only_cost`, `test_rewrite_cells_order_after_seeds_cell`
- `tests/test_gld_srv_poi_contract.py`:
  - update `test_multi_lang_i18n_only_branch`, `test_partner_without_destination_branch`, `test_build_columns_match_ddl`
  - add `test_info_full_address_groups_no_concat_ws`, `test_info_full_address_blank_skips_group`, `test_info_street_from_entity`, `test_multi_lang_cost_guard`, `test_no_cost_vnd_in_active_surface`
- Existing tests to update:
  - `test_enr_poi_contract.py` `LANDING_ML` (line 78 only)
  - `test_initial_ddl_contract.py::test_columns_match_sources`, `::test_pipeline_config_rows_match_sources`, `::test_watermark_rows_match_source`
  - `test_srv_poi_serving_contract.py::test_gold_and_pg_columns_and_types_match`, `::test_entities_match_gold_columns_types_and_keys`
  - `test_srv_poi_api_mapping_required.py::test_cited_source_columns_exist_in_ddl`
- `mvn -q -f services/data-serving-service/pom.xml test -Dtest=PoiServiceTest`. Run `PoiRepositoryIntegrationTest` only if Docker is available.
- `python scripts/vv.py verify 20261116-enr-lang-destination-from-bronze`
- Runtime checks: doc §18 "Runtime".

### Read only if needed
- §0 Verdict, §14 Alternatives: #5, #6, and why there is no column mapping
- §3 Invariants, §5 Grain and keys, §6 Ordering: #2, #14
- §7–§11 Commit, Idempotency, Concurrency, Retry, Partial failure: #2, #5, #6, stop points 5–6
- §12 Observability: #2, #5, #6, #8
- §15 Rollout (R-0, B1–B5), §16 Rollback: #17, stop points 4–6
- §17.1 Extract notebook: #2, #14
- §17.2 Registry and seeds: #3, #4
- §17.3 DDL and rewrite cells (planner code, cell flow, do-not-rerun list): #3, #5, #6, #14
- §17.4 Gold rename runbook: #6, #17
- §17.5 Gold notebooks (guard and formula code): #7, #8, #15
- §17.6 PostgreSQL and API: #9–#13
- §17.7 Docs: #16
- §18 Verification: #14, #15, #17
- §19 Decisions: #1
- §20 scope.files: stop point 1

# Architecture: 20261116-enr-lang-destination-from-bronze (round 2)

## 0. Verdict

Round 2 is PASS. U-1 to U-4 are closed (D-5, D-9). P-1, P-3, and P-4 are closed (D-10). The Copy Job maps columns by gold name (D-11). Every edit below is determined.

Round 2 changes three round-1 decisions:

1. Silver schema change (supersedes A-10 for silver). P-1 found 3 rows in `slv_enr_poi_info_multi_lang`, and D-10 says do not recreate it. Both silver tables are now rewritten in place: one Delta overwrite with `overwriteSchema`, read from the pinned current version, no DROP, no column mapping. Existing rows and table history are kept. The repo already uses this pattern in `NB_SETUP_L1_TS_AUDIT` (`frame.write…mode("overwrite").option("overwriteSchema","true")…saveAsTable`, then props re-applied and post-checked).
2. Gold `cost_vnd` → `cost` (supersedes A-10 for gold). Same in-place rewrite, not column mapping plus `RENAME COLUMN`. Reasons:
   - The Copy Job reads gold by name. Its support for column-mapped Delta is unproven.
   - The repo's own direct-file reader rejects column mapping (`NB_LIB_EXTRACT_RAWDATA` `delta_added_files`: "bật column mapping" → `DeltaReadUnsupported`).
   - Gold is reader 1 / writer 2 (P-1). Enabling column mapping upgrades it to 2/5, which cannot be undone.
   - The rewrite keeps every value, including `created_at`, `deleted_at`, and `row_hash`, and can be undone with `RESTORE`.
3. Rollout order. The Copy Job follows gold column names, so PostgreSQL must be renamed in the same short window as gold. Whether the job can be paused is still unknown. That question does not change any code. It is a runtime stop (R-0, §15). Both answers have a safe procedure.

`model-design.md` has no conflict with D-1 to D-11. Grain and keys come from model-design `## Entities and grain` and `## Keys`. Technical columns (model Q-9) are the Architect's choice (A-3) and change no grain or key. Do not re-run `run-author --kind model`.

## 1. Scope

- New extract notebook `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`. It reads `lh_vv_bronze.dbo.brz_enrichment_result` and writes:
  - `slv_enr_poi_info_multi_lang` from `event_type = LANG`
  - `slv_enr_poi_destination` from `event_type = DESTINATION`
  - It uses `NB_LIB_EXTRACT_RAWDATA` unchanged.
- Control rows: 2 `ctrl_mng_pipeline_config` rows, the registry rows, and the watermark row `wm_transform_brz_enrichment_result`.
- Silver DDL, in place: `cost_vnd` → `cost` (multi_lang), drop `street` (destination), and add the new and technical columns. `NB_SETUP_INITIAL_DDL` `TABLE_SPECS` and seeds are mirrored.
- Gold:
  - `NB_GLD_SRV_POI_MULTI_LANG` uses `cost` and gets a `cost_vnd` guard.
  - `NB_GLD_SRV_POI_INFO` takes `street` from the entity and uses the three-group `full_address` with the blank rule (D-5).
  - `gld_srv_poi_multi_lang.cost_vnd` is renamed by an in-place rewrite cell that the user runs from the runbook.
- PostgreSQL: `apps.srv_poi_multi_lang.cost_vnd` → `cost` in the DDL file, plus a manual `ALTER` noted in the header.
- API:
  - Entity and service read `cost`.
  - `StoredJsonParser.labelValue` also accepts `{text,label}` (U-1 = B).
- Docs:
  - `mapping_gld_srv_poi_info.md`
  - `mapping_gld_srv_poi_multi_lang.md`
  - `api-mapping/practical_info.md`
  - `CTRL_TABLES_CONTEXT.md`
  - new `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md`

## 2. Non-goals

- Pipeline activity or schedule for the new extract. It runs manually, as CMS does. Pipeline JSON is out of scope.
- Changes to:
  - `NB_LIB_EXTRACT_RAWDATA` and `NB_LIB_TRANSFORM_SLV_GLD`
  - `gld_enr_poi_info`
  - historical `NB_CREATE_DDL` cells
  - `slv_poi_entity_non_enrich.street`
  - `(ood).general-information.md` (D-2)
- Changes to the Fabric Copy Job definition. It is not in the repo, and it maps by name (D-11).
- Delete or soft-delete in silver. Bronze has no delete event.
- Removing the 3 legacy silver multi_lang rows. They are kept (D-10). §18 reports them.
- Trimming `house_number` or `street` in the output. D-5 only says blank values skip a group.
- Fabric DEV runs, `docker compose`, and commits.

## 3. Invariants

- I-1: `slv_enr_poi_info_multi_lang` gets rows only from `trim(event_type) = 'LANG'`. `slv_enr_poi_destination` gets rows only from `trim(event_type) = 'DESTINATION'`. The match is exact and case-sensitive. Any other value is IGNORED `OUT_OF_SCOPE` and counted. There is no `lit(True)` presence branch.
- I-2: One row per (`poi_id`, `lang`) and one row per `poi_id`. A blank key part is rejected, never written.
- I-3: For each key, the stored row comes from the event with the greatest (`version`, `EventProcessedUtcTime`, `event_id`) (D-3). The MERGE guard uses a strict `>`, so replaying the same event updates 0 rows.
- I-4: `cost`, `best_time`, `time_to_spend`, `experience`, and `destination` store the source JSON text unchanged. `destination_id` and `destination_name` are JSON array text with the same length and order as `data.destinations`, with JSON `null` kept in place (D-9 U-3).
- I-5: `country_code` and `postal_code` are not in the registry and are NULL on every row the extract writes.
- I-6: The watermark source row advances only when every table is SUCCESS or NO_DATA (lib `finalize_watermark`).
- I-7: Gold `full_address`:
  - For rows with a destination row: the first non-null of `concat(G1)`, `concat(G2)`, G3, joined with `", "`. Never `concat_ws`.
  - `house_number` or `street` that is NULL or blank under Spark `trim` makes G1 and G2 null.
  - Partner rows without a destination row keep the entity `full_address` (D-5, D-9 U-2).
  - Gold `street` is the entity `street` on every row.
- I-8: No table holds both `cost_vnd` and `cost`:
  - The gold multi_lang `build` raises `ConfigError` if the target has `cost_vnd`. This runs before `ensure_target`, which would otherwise `ADD COLUMNS cost`.
  - The extract preflight raises `ConfigError` if a silver target has a retired column (`cost_vnd` or `street`).
- I-9: Gold nodes fail closed on the wrong silver shape: `_require` raises `ConfigError` and nothing is written.
- I-10: The in-place rewrites keep every row and every carried value:
  - Row count is equal.
  - `EXCEPT ALL` in both directions between the old version (columns renamed) and the new version is empty.
  - New columns are all NULL.
  - Otherwise the cell restores the old version and raises.
  - The cells never run `DROP TABLE`, `columnMapping`, or `RENAME COLUMN`.

## 4. State ownership

| state | only writer | readers |
|---|---|---|
| both `slv_enr_*` tables (data) | the extract (MERGE) | `NB_GLD_SRV_POI_INFO`, `NB_GLD_SRV_POI_MULTI_LANG`, `NB_ENR_POI_INFO` (reads `poi_id` only) |
| both `slv_enr_*` tables (schema) | `NB_CREATE_DDL` `enrbrzpy` | extract preflight, gold `_require` |
| `gld_srv_poi_multi_lang` (data) | NB_00 30M node | Fabric Copy Job (by name, D-11) |
| `gld_srv_poi_multi_lang` (schema) | `NB_CREATE_DDL` `enrgldpy` (runbook) | gold guard, Copy Job |
| `gld_srv_poi_info` | NB_00 30M node | Copy Job |
| `wm_transform_brz_enrichment_result` | the extract (lock, `last_src_version`); `enrbrzpy` takes only its lock | the extract |
| `ctrl_cdc_state` and `ctrl_cdc_reject` partition `src_tbl = brz_enrichment_result` | the extract | the extract, operators |
| `apps.srv_poi_multi_lang` | Copy Job (data); user (manual `ALTER`) | API |

## 5. Grain and keys

As model-design `## Entities and grain` and `## Keys` define them. Additions:
- MERGE `ON` uses `=` on the key columns, because blank keys are rejected first.
- `ctrl_cdc_state.entity_key` is the row key (`state_key = "row"`): `poi_id|lang` for multi_lang, `poi_id` for destination. Per-`poi_id` state would mark a `ko` event stale after a `vi` event.
- The 3 legacy multi_lang rows keep their keys. Their technical columns are NULL, so the first bronze event with the same key replaces them (`coalesce(t._src_version, -1)`).

## 6. Ordering

- Read order follows the Delta commit versions of bronze (`read_incremental`). `EventProcessedUtcTime` is the watermark column, used for monitoring only (D-4).
- The extract fills the lib event contract with:
  - `_cdc_ts_ms = version` (BIGINT)
  - `_cdc_lsn = unix_micros(EventProcessedUtcTime)`
  - `_raw_ingested_at = EventProcessedUtcTime`
  - `_is_delete = 0`, `_op = NULL`
- The lib's `event_order()` compares `struct(ts, lsn, ing, del)`. State staleness, `resolve_latest`, and the MERGE guard therefore all use the D-3 order. The final tie-break is `event_id`, which is deterministic and adds no business rule. `ctrl_cdc_state.cdc_ts_ms` holds `version` for this source. The notebook doc must say so.
- Rejected: ordering by `EventProcessedUtcTime` only, as CMS does. A commit that lands late with a higher `version` would be marked stale.
- Rollout order is in §15. Each step either works or fails closed with the previous data kept.

## 7. Transaction and commit boundaries

- Extract run (lib `run_controlled`):
  1. lock
  2. run log RUNNING
  3. pin the bronze snapshot
  4. per table: preflight, then build, then the `cast_null` gate, then one MERGE (one Delta commit per table)
  5. `commit_state`
  6. `merge_rejects`
  7. table log
  8. `finalize_watermark`
  9. unlock
  - There is no atomicity across the two tables.
- Rewrite cell, per table:
  - Read `v0`, then one overwrite commit `v1` with `userMetadata = 20261116-enr-lang-destination-from-bronze`.
  - Then metadata-only commits: `SET NOT NULL`, and `SET TBLPROPERTIES` for props that went missing.
  - Then post-check. On failure, `RESTORE TABLE … TO VERSION AS OF v0` (one commit), then raise.
- PostgreSQL: `ALTER … RENAME COLUMN` is one transaction.
- Gold-to-PostgreSQL consistency is eventual. It follows Copy Job runs.

## 8. Idempotency

- Replaying bronze commits after the state commit: `_is_stale` drops them, giving NO_DATA.
- A crash between the MERGE and `commit_state`: the strict-`>` guard updates 0 rows on replay.
- `full_reload = True`: the guard keeps the newest row, so the result is the same.
- Rewrite cells: a rerun plans `SKIP` when the schema (name, type, nullability, order) already matches the target. A table with both `cost_vnd` and `cost` stops.
- Seed cell: inserts missing rows. It stops if a row with the same key has different values. A rerun is a no-op.
- Gold recompute is deterministic.
  - `row_hash = sha2(to_json(struct(cols)))` includes column names. The first node run after the gold rename therefore rewrites `row_hash` and `updated_at` once for all 859 live rows.
  - That re-copies every row once, which also repairs a Copy Job run that was missed during the rename window.

## 9. Concurrency

- Extract: one run per source, enforced by the atomic lock on `wm_transform_brz_enrichment_result`.
- `enrbrzpy` (silver rewrite) holds three locks:
  - The extract lock (`lock_exec_id` and `lock_at` only, with the lib `acquire_lock` predicate. `status` is not touched) when the row exists.
  - `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` and `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M` (flow-lock pattern of `entwebpy`).
  - Before locking, the cell reads `ctrl_mng_pipeline_config` for active edges with `src_tbl` in the two silver tables. It stops if a third `pl_name` is found.
  - Locks are taken in sorted `watermark_id` order and released in `finally`. If any lock is busy, the cell releases the ones it holds and stops.
- `enrgldpy` (gold rewrite) holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`. It stops if any active edge with `trg_tbl = gld_srv_poi_multi_lang` belongs to another flow.
- Delta optimistic concurrency is the second guard: a commit that lands between `v0` and the overwrite makes the overwrite fail. The post-check compares against `v0`.
- The Copy Job reads gold at a snapshot: either `v0` with `cost_vnd` or `v1+` with `cost`, never a mix.
- NB_00 can see multi_lang updated before destination within one extract run. Accepted eventual consistency (the next 30M cycle).

## 10. Retry and recovery

- Transient Delta conflicts: lib `with_retry` and `process_with_retry`.
- Version gap: `allow_full_scan = True`, so the run does a FULL read at the pinned version.
- Stale lock: taken over after `running_timeout_minutes`.
- Bad extract load: set the watermark to INITIALIZED (CTRL §4 recipe), then `full_reload = True`. Bronze is the system of record. P-5 reports retention at runtime.
- Failed rewrite: the cell restores automatically. To retry, rerun the cell; it replans from the current state.
- Failed PostgreSQL `ALTER` (for example `lock_timeout`): retry it. Gold is already renamed, and the Copy Job fails closed until the retry succeeds.

## 11. Partial failure

| failure point | state left | action |
|---|---|---|
| one extract table fails | run PARTIAL_FAILED, watermark unchanged, only SUCCESS tables write state | rerun; state drops what was already applied |
| `cast_null > 0` (`lat`, `lng`, `translated_at`, projection flag) | that table FAILS before its MERGE | fix the data or config, then rerun |
| rewrite post-check fails | table restored to `v0`, cell raises | investigate; PostgreSQL untouched |
| after new notebooks are deployed, before the rewrites | gold info and multi_lang nodes raise `ConfigError` (`_require` or guard); gold keeps the last good data | finish the rewrites |
| gold renamed, PostgreSQL not yet | a Copy Job run fails on the missing `cost` column; PostgreSQL keeps the old data if the write mode is not truncate-first (R-0) | run the `ALTER`, then the next Copy Job run |
| PostgreSQL renamed, old API still deployed | multi_lang reads in the old API fail (`ddl-auto: none`, so it starts but its queries fail) | deploy the API; keep the window short |
| old gold notebook runs after the gold rename | `_require(ML_COLS with cost_vnd)` on new silver raises; nothing is written | prevented by deploying the new notebooks first (§15 B1) |

## 12. Observability

- Extract exit JSON (lib `build_summary`) plus `extra`:
  - `by_event_type` {LANG, DESTINATION, other}
  - `ignored_detail.OUT_OF_SCOPE`
  - rejects by reason
  - `order_ties`
  - `destination_null_elements`
  - `destinations_not_array`
  - `watch.unmapped_top_keys` and `mapped_heads_missing`
- Rewrite cells print one JSON per table:
  - `table`, `action` (SKIP, REWRITTEN, RESTORED, FAILED), `v0`, `v1`
  - `rows_before`, `rows_after`, `renamed_nonnull` (old and new)
  - `dropped_nonnull`, `props_reapplied`, `not_null_set`
- Gold `gld_srv_poi_info` new metrics:
  - `full_address_g1`, `full_address_g2`, `full_address_g3` (counted among destination rows)
  - `full_address_entity` (partner without a destination row)
  - `full_address_null`, `street_null`
  - `destination_name_filled` stays.
- `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_cdc_reject` with `src_tbl = 'brz_enrichment_result'`.
- API: the existing `stored_json_parse_failed` warning, now with field `cost`.

## 13. Security

- No secrets or connection strings in notebooks, the runbook, or the repo. Table names are fully qualified.
- `ctrl_cdc_reject.after_payload` holds bronze `data`: POI address and enrichment text, no personal data. Same data class as CMS.
- The PostgreSQL `ALTER` and the Copy Job pause are manual user steps. The API bearer check is unchanged. No new endpoint.

## 14. Alternatives and trade-offs

| decision | selected | rejected and why |
|---|---|---|
| Extract home | New notebook copied from `NB_EXTRACT_CMS_CDC_BRZ_TO_SLV` (DOC `$`) | Extending CMS: different raw table, watermark, and lock. Changing the lib: shared by partner, 3P, and CMS |
| `destination_id` / `_name` | Local projection: `from_json(array<struct<id,name>>)` → `transform` → `to_json` | `get_json_object('$[*].id')` drops nulls and returns a bare scalar for a 1-element array. A lib rule means a lib change. Delimited text cannot hold null, and names contain `", "` |
| Silver schema change | In-place overwrite rewrite, guarded and auto-restoring | DROP and CREATE: D-10 forbids it (3 rows). Column mapping plus RENAME/DROP: irreversible protocol upgrade, and the repo's direct-file reader rejects column mapping. ADD `cost` and keep `cost_vnd`: breaks I-8 |
| Gold `cost_vnd` → `cost` | In-place overwrite rewrite (one commit, keeps `created_at`, `deleted_at`, `row_hash`; `RESTORE` undoes it) | Column mapping plus RENAME (round 1): Copy Job support for column mapping is unproven, protocol goes to 2/5 for good. DROP, CREATE, and recompute: loses `created_at`, and a Copy Job reading the empty table could empty PostgreSQL. Expand/contract in gold: by-name copy would push both columns |
| PostgreSQL rename | `ALTER … RENAME COLUMN` right after the gold rewrite, with `lock_timeout` | Expand/contract (ADD `cost`, backfill, DROP later): correctness depends on the unknown Copy Job write mode (D-11), and the old column would go stale in between. Not worth it for a DEV window of a few minutes |
| State and order | `state_key = row`, with `version` mapped into `_cdc_ts_ms` | Per-POI state wrongly marks other languages stale |
| Constant NULL columns | Not in the registry; the DDL keeps them; the preflight asserts they exist | A registry row with path `null` is invalid for snapshot rules (CTRL §5) |
| Extract target guard | Preflight: the target must exist, have no retired column, and have the constant-NULL columns. New registry columns are still auto-added by the lib | Fully strict schema equality: blocks the documented "INSERT registry → ADD COLUMNS" operation |

## 15. Rollout

Prerequisite: local verification PASS (§18), then review.

A. Repo: every edit in §17 and tests green.

B. Fabric DEV, by the user from `runtime-runbook.md`. Each step lists its stop condition.

- R-0 (STOP, user): record:
  - the Copy Job schedule interval
  - its write mode for `apps.srv_poi_multi_lang` (append, upsert, or truncate/overwrite)
  - whether its schedule can be turned off
  - baseline: `SELECT count(*), count(cost_vnd) FROM apps.srv_poi_multi_lang`, and gold `count(*)` and `count(cost_vnd)`
- B1. Deploy `NB_CREATE_DDL`, the new extract, `NB_GLD_SRV_POI_MULTI_LANG`, and `NB_GLD_SRV_POI_INFO`.
  - From here, the two gold nodes fail closed (I-8, I-9) until B5. Gold keeps its last good data.
- B2. Run `enrbrzpy` (silver rewrite).
  - Stop if `action` is not REWRITTEN or SKIP for both tables.
  - Run it before the seeds, so the extract cannot run meanwhile.
- B3. Run `enrbrzcfgpy` (config, registry, watermark seeds).
- B4. Run the extract with `dry_run = True`.
  - Stop if `cast_null > 0` or `by_event_type.other > 0`.
  - Then run it for real.
- B5. Gold and PostgreSQL window. Run it right after a Copy Job run finishes, or with the Copy Job schedule off if R-0 says that is possible:
  1. Run `enrgldpy` (gold rewrite). Stop if it is not REWRITTEN.
  2. In PostgreSQL:
     ```sql
     BEGIN; SET LOCAL lock_timeout = '10s';
     ALTER TABLE apps.srv_poi_multi_lang RENAME COLUMN cost_vnd TO cost;
     COMMIT;
     ```
  3. Deploy the API build that reads `cost`.
  4. Run NB_00 30M with `p_force_nodes = gld_srv_poi_multi_lang,gld_srv_poi_info`.
     - Expect both nodes SUCCESS.
     - Expect a one-time update of all 859 multi_lang rows (`row_hash` now hashes the new column name).
     - Expect an update of the gold info rows whose `street` or `full_address` changes.
  5. Turn the Copy Job schedule back on, or wait for its next run.
     - Verify that the PostgreSQL count equals the gold live count, and that `count(cost)` in PostgreSQL equals the gold `count(cost)`.
  - If R-0 says the write mode is truncate-first and the job cannot be paused: run B5.1 and B5.2 within the same Copy Job interval, right after a completed run. Check the PostgreSQL count after the next run.
- Expected side effects, from P-3 data:
  - 113 partner POIs get a destination row. In gold info they switch `ward`, `city`, `lat`, `lng`, `destination_id`, and `destination_name` to the destination values (existing D-SRV-22 rule). `district` is NULL, because the source has 0/113 non-empty.
  - No Google POI has a DESTINATION event, so no new Google rows appear in `gld_srv_poi_info`.
  - Gold multi_lang (poi, lang) keys that now exist in silver move from the P2 branch to the P1 branch (`cost` filled).
  - `gld_enr_poi_info.is_enriched_*` flags flip for enriched POIs.

## 16. Rollback and forward recovery

- Extract: set `is_active = 0` on both config rows. Silver keeps its data.
- Silver schema:
  - If the extract has not written yet: `RESTORE TABLE … TO VERSION AS OF v0` (`v0` from the cell output), then redeploy the old gold notebooks.
  - After extract writes: forward recovery only. Fix forward, or `full_reload` from bronze.
- Gold:
  - If no node run happened after `v1`: `RESTORE TABLE lh_vv_gold.dbo.gld_srv_poi_multi_lang TO VERSION AS OF v0`.
  - Otherwise: rerun the rewrite function with the reverse rename (`{"cost_vnd": "cost"}`) from the runbook snippet.
  - In both cases, redeploy the old gold notebook, then `ALTER TABLE apps.srv_poi_multi_lang RENAME COLUMN cost TO cost_vnd;`, then redeploy the previous API build. Keep the same window order as B5, reversed.
- `RESTORE` needs the files of `v0` not yet vacuumed (default retention 7 days). After that, use the reverse rewrite.
- Gold info formula: git revert, then NB_00 with `p_force_nodes = gld_srv_poi_info`.

## 17. Implementation plan

### 17.1 Extract notebook `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb`

Copy the CMS notebook cell for cell. Cell ids `enr00` to `enr14` mirror `cms00` to `cms14`. Only these deltas:

Parameters (`enr01`): `src_tbl = "brz_enrichment_result"`, `max_parallel = 2`. Remove `sources`. Other parameters keep the CMS defaults.

Constants (`enr04`):
```python
RAW_PAYLOAD    = "data"
RAW_EVENT_ID   = "event_id"
RAW_DOC_ID     = ("poi_id",)
RAW_EXTRA      = ("event_type", "version")
TABLE_EVENT_TYPE = {"slv_enr_poi_info_multi_lang": "LANG", "slv_enr_poi_destination": "DESTINATION"}
ARRAY_PROJECTIONS = {"destinations.id": "id", "destinations.name": "name"}
DEST_ELEM_SCHEMA = "array<struct<id:string,name:string>>"
CONST_NULL_COLS = {"slv_enr_poi_destination": ("country_code", "postal_code")}
RETIRED_COLS    = {"slv_enr_poi_info_multi_lang": ("cost_vnd",), "slv_enr_poi_destination": ("street",)}
doc_key_column = "poi_id"
state_key      = "row"
EXTRACT_MODES  = ("DOC",)
ENR_TECH_COLUMNS = (("_src_version", "bigint"), ("_event_processed_at", "timestamp"), ("_event_id", "string"),
                    ("_first_seen_at", "timestamp"), ("_last_seen_at", "timestamp"),
                    ("created_at", "timestamp"), ("updated_at", "timestamp"))
```

Read and classify (`enr06`):
- `doc_columns` adds `RAW_EXTRA`. `read_raw` aliases `EventProcessedUtcTime` as `_event_processed_at`.
- Classification rules, first match wins:
  1. blank `poi_id` → REJECTED `MISSING_ENTITY_KEY`
  2. `trim(event_type)` not in `TABLE_EVENT_TYPE.values()` → IGNORED `OUT_OF_SCOPE`
  3. blank or corrupt `data`, or `data` not an object → REJECTED `INVALID_PAYLOAD`
  4. `version` NULL or `_event_processed_at` NULL → REJECTED `MISSING_EVENT_ORDER`
- Event columns as §6.
- `presence(spec) = trim(_doc__event_type) == TABLE_EVENT_TYPE[spec.trg_tbl]`.
- `doc_source_payload` and `doc_reject_rows` carry `event_id`, `poi_id`, `event_type`, `version`, and `EventProcessedUtcTime`.

Rows and MERGE (`enr08`):
- `part_value(path)`: when `path in ARRAY_PROJECTIONS`, use
  ```python
  arr = F.from_json(F.col(block_col("destinations")), DEST_ELEM_SCHEMA, JSON_OPTIONS)
  F.when(arr.isNotNull(), F.to_json(F.transform(arr, lambda x: x.getField(field))))
  ```
  and add the flag `_bad__<col> = _b__destinations IS NOT NULL AND arr IS NULL`. `table_stats` counts it as `_cn__<col>`, so it fails under the FAIL policy. Other paths keep the CMS behaviour.
- `key_null` checks every `spec.key_cols`. `NULLABLE_KEYS = ()`.
- `resolve_latest` orders by `_src_version DESC, _event_processed_at DESC, _event_id DESC`.
- MERGE columns are the spec columns plus `ENR_TECH_COLUMNS`. `_src_version = version`, `_event_processed_at = _raw_ingested_at`.
- Preflight, before the first table and in dry run as well:
  - The target must exist (`ConfigError("run enrbrzpy")`).
  - It must have no column from `RETIRED_COLS`.
  - It must have every `CONST_NULL_COLS` column.
  - Then `ensure_target(spec, ctx.dry_run, ENR_TECH_COLUMNS)`.

MERGE guard:
```sql
MERGE INTO {target} AS t USING {view} AS s ON {t.k = s.k AND ...}
WHEN MATCHED AND (
      s._src_version > coalesce(t._src_version, -1)
   OR (s._src_version = t._src_version AND s._event_processed_at > t._event_processed_at)
   OR (s._src_version = t._src_version AND s._event_processed_at = t._event_processed_at
       AND s._event_id > t._event_id))
THEN UPDATE SET <non-key spec cols>, _src_version, _event_processed_at, _event_id,
     _first_seen_at = least(coalesce(t._first_seen_at, s._first_seen_at), s._first_seen_at),
     _last_seen_at = greatest(coalesce(t._last_seen_at, s._last_seen_at), s._last_seen_at),
     updated_at = {clock}
WHEN NOT MATCHED THEN INSERT (<spec cols>, <ENR_TECH_COLUMNS>) VALUES (..., {clock}, {clock})
```

Context (`enr11`): `load_table_specs(ctx, allowed_modes=("DOC",))`. `check_config` rejects:
- `src_object` other than `$`
- a path that starts with `data.`
- a `destinations.<f>` path where `<f>` is not in {`id`, `name`}
- a `trg_tbl` missing from `TABLE_EVENT_TYPE`

### 17.2 Registry, config, and watermark seeds

`json_path` values are relative to the payload `data` (A-9): the Mapping §5 paths with the leading `data.` removed.

| trg_tbl | column | json_path | type / rule | key |
|---|---|---|---|---|
| multi_lang | poi_id | `_doc.poi_id` | string / NONE | 1 |
| multi_lang | lang | `_doc.lang` | string / NONE | 2 |
| multi_lang | time_to_spend | `display.time_to_spend` | string / NONE | |
| multi_lang | best_time | `display.best_time` | string / NONE | |
| multi_lang | cost | `display.cost` | string / NONE | |
| multi_lang | description | `description` | string / NONE | |
| multi_lang | experience | `experiences` | string / NONE | |
| multi_lang | source_name | `_doc.source` | string / NONE | |
| multi_lang | translated_at | `translated_at` | timestamp / ISO_UTC_TS | |
| destination | poi_id | `_doc.poi_id` | string / NONE | 1 |
| destination | source_name | `_doc.source` | string / NONE | |
| destination | ward, ward_with_type, district, district_with_type, city, city_with_type, formatted_address | `address.new.ward.name`, `address.new.ward.name_with_type`, `address.new.district.name`, `address.new.district.name_with_type`, `address.new.province.name`, `address.new.province.name_with_type`, `address.new.formatted_address` | string / NONE | |
| destination | old_* (7 columns) | the same paths under `address.old.` | string / NONE | |
| destination | lat, lng | `lat`, `lng` | double / NONE | |
| destination | full_address | `request.address` | string / NONE | |
| destination | destination | `destinations` | string / NONE | |
| destination | destination_id, destination_name | `destinations.id`, `destinations.name` | string / NONE (projection) | |

Other seed rows:
- Config: `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, `src_schema = lh_vv_bronze.dbo`, `src_tbl = brz_enrichment_result`, `trg_schema = lh_vv_silver.dbo`, `priority = 1`, `load_mode = DOC`, `is_active = 1`, `nb_name = NULL`, `align_path = NULL`, `dedup_order = NULL`.
- Watermark: `wm_transform_brz_enrichment_result`, `trg_tbl = NULL`, `watermark_column = EventProcessedUtcTime`, `status = INITIALIZED`, `flow_name = NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV`, `watermark_sequence = -1`.

The FL_00 pre-check filters on `src_tbl = partner_raw_data`, so these rows do not affect it.

### 17.3 DDL notebooks and the rewrite cells

`NB_SETUP_INITIAL_DDL` `TABLE_SPECS`:
- multi_lang: `poi_id STRING NOT NULL, lang STRING, time_to_spend, best_time, cost, description, experience, source_name, translated_at TIMESTAMP, _src_version BIGINT, _event_processed_at TIMESTAMP, _event_id STRING, _first_seen_at TIMESTAMP, _last_seen_at TIMESTAMP, created_at TIMESTAMP, updated_at TIMESTAMP`
- destination: `poi_id STRING NOT NULL, source_name, ward, ward_with_type, district, district_with_type, city, city_with_type, formatted_address, old_ward, old_ward_with_type, old_district, old_district_with_type, old_city, old_city_with_type, old_formatted_address, lat DOUBLE, lng DOUBLE, full_address, destination, destination_id, destination_name, country_code, postal_code, <the five _ tech columns>, created_at, updated_at`
- Untyped columns are nullable STRING (A-5).
- Gold `gld_srv_poi_multi_lang`: `cost_vnd` → `cost`, same position.
- Seeds from §17.2.

`NB_CREATE_DDL`: append new cells at the end, in this order. Historical cells stay untouched.

1. `enrbrzcfgmd` / `enrbrzcfgpy`: insert the §17.2 rows where they are missing. Stop on a same-key row with different values. The rows must be identical to the `NB_SETUP_INITIAL_DDL` seeds (test).
2. `enrbrzmd` / `enrbrzpy`: silver rewrite.
   - Targets are the two `TABLE_SPECS` lists above, copied inline (test: equal).
   - Renames: `{"cost": "cost_vnd"}` for multi_lang, none for destination.
   - Drops: `{"street"}` for destination only.
   - Locks as §9.
3. `enrgldmd` / `enrgldpy`: gold rewrite of `lh_vv_gold.dbo.gld_srv_poi_multi_lang`.
   - The target is the current schema with `cost_vnd` renamed to `cost` in place. Every other column is kept in order, including `row_hash`, `created_at`, `updated_at`, `deleted_at`.
   - Renames: `{"cost": "cost_vnd"}`. Drops: none. Lock as §9.
   - The markdown says it is run only from runbook step B5.1.
4. Both markdown cells say: after these cells, do not rerun historical cells whose contract still lists `cost_vnd` on silver or gold multi_lang, or `street` on silver destination. Main enumerates them with `Grep "cost_vnd|\"street\"" NB_CREATE_DDL.ipynb`. Expected: `enrinfopy`, `enrflagpy`, `srvpoipy`, `mlexppy`, `mlsrcpy`, `poidestpy`. Follow the existing "Sau cell này không chạy lại …" precedent. Also update the `_require` hint in `NB_GLD_SRV_POI_INFO` from `poidestpy` to `enrbrzpy`.

Pure planner, shared verbatim by `enrbrzpy` and `enrgldpy` and exec'd by tests. Precedent: `# BEGIN_REGISTRY_PURE` in `test_cms_l1_contract.py`.
```python
# BEGIN_REWRITE_PURE
def plan_rewrite(current, target, renames, drops):
    """current, target: [(name, type, nullable)] in column order. renames: {new: old}. drops: allowed old names.
    -> ("SKIP", [], []) | ("REWRITE", [(kind, src, name, type)], [not_null names]). kind: COL | NULL.
    Raises ValueError on anything unplanned."""
    norm = lambda cols: [(n.lower(), t.lower(), bool(nl)) for n, t, nl in cols]
    if norm(current) == norm(target):
        return "SKIP", [], []
    cur = {n.lower(): (n, t.lower()) for n, t, _ in current}
    used, items, errors = set(), [], []
    for name, dtype, nullable in target:
        old = renames.get(name)
        if old and old.lower() in cur and name.lower() in cur:
            errors.append(f"{old} và {name} cùng có")
        src = old if old and old.lower() in cur else name
        if src.lower() in cur:
            if cur[src.lower()][1] != dtype.lower():
                errors.append(f"{src}: {cur[src.lower()][1]} khác {dtype}")
            used.add(src.lower())
            items.append(("COL", cur[src.lower()][0], name, dtype))
        elif nullable:
            items.append(("NULL", None, name, dtype))
        else:
            errors.append(f"{name} NOT NULL không có nguồn")
    unknown = sorted(c for c in set(cur) - used if c not in {d.lower() for d in drops})
    if unknown:
        errors.append(f"cột không có trong đích: {unknown}")
    if errors:
        raise ValueError("; ".join(errors))
    return "REWRITE", items, [n for n, _, nl in target if not nl]
# END_REWRITE_PURE
```

Cell flow per table, inside the locks:
1. `v0` = latest version from `DESCRIBE HISTORY … LIMIT 1`. `props0` = `DESCRIBE DETAIL`.`properties`. `current` comes from `spark.table(fq).schema`.
2. `plan_rewrite(...)`. SKIP → print and continue.
3. `dropped_nonnull` = count of non-null values in each dropped column at `v0`. If > 0, stop. Destination had 0 rows at P-1; any value now means an unknown writer.
4. Build `SELECT <items> FROM fq VERSION AS OF v0`:
   - `COL` → `` `src` AS `name` ``
   - `NULL` → `CAST(NULL AS type) AS name`
5. `.write.format("delta").mode("overwrite").option("overwriteSchema", "true").option("userMetadata", "20261116-enr-lang-destination-from-bronze").saveAsTable(fq)`.
6. For each NOT NULL target column that is nullable now: `ALTER TABLE fq ALTER COLUMN c SET NOT NULL`. Re-`SET TBLPROPERTIES` for every key of `props0` that is missing or different.
7. Post-check, all must hold:
   - schema equals the target (name, type, nullability, order)
   - `count(v0) == count(current)`
   - `(old projection at v0) EXCEPT ALL (carried columns now)` is empty, and the reverse too
   - every `NULL` item column has `count(col) = 0`
   - properties ⊇ `props0`
8. On any failure from step 5 on: `RESTORE TABLE fq TO VERSION AS OF v0`, print `RESTORED`, raise.

### 17.4 Gold rename runbook step

Runbook B5.1 runs `enrgldpy`. No hand-written SQL rewrite and no column mapping.

The runbook also holds:
- the PostgreSQL `ALTER` for B5.2
- the reverse snippet for §16: the same planner with renames `{"cost_vnd": "cost"}`
- the `RESTORE` command with the `v0` from the cell output

### 17.5 Gold notebooks

`NB_GLD_SRV_POI_MULTI_LANG` (`srvmlbuild`, `srvmlmd`):
- `ML_COLS`, `OUT_COLS`, and `MEASURE_COLS` use `cost`. P2 sets `cost` to NULL. Update the markdown.
- First lines of `build`. This runs before the lib's `ensure_target`, since `run_node` calls `spec.build` and then `ensure_target`.
  ```python
  GOLD_FQ = "lh_vv_gold.dbo.gld_srv_poi_multi_lang"
  if spark.catalog.tableExists(GOLD_FQ) and "cost_vnd" in {c.lower() for c in spark.table(GOLD_FQ).columns}:
      raise ConfigError("gld_srv_poi_multi_lang còn cost_vnd: chạy enrgldpy của NB_CREATE_DDL (runbook B5.1)")
  ```

`NB_GLD_SRV_POI_INFO` (`srvinfobuild`, `srvinfomd`):
```python
ENT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_category", "types_json", "phone",
            "email", "website_url", "operating_status", "opening_hours_text", "holiday_exceptions",
            "house_number", "street")
DEST_COLS = ("poi_id", "updated_at", "destination_id", "destination_name", "full_address", "ward", "district", "city",
             "country_code", "postal_code", "lat", "lng", "formatted_address", "ward_with_type", "city_with_type")
ADDR_ONLY = ("formatted_address", "ward_with_type", "city_with_type")   # read for the formula, not output
SEP = F.lit(", ")

def _text_or_null(name):
    # D-5 / U-4: NULL or blank under Spark trim -> NULL, so F.concat makes the whole group NULL. Value kept untrimmed.
    return F.when(F.trim(F.col(name)) != "", F.col(name))

hn, st = _text_or_null("house_number"), _text_or_null("street")
g1 = F.concat(hn, SEP, st, SEP, F.col("formatted_address"))
g2 = F.concat(hn, SEP, st, SEP, F.col("ward_with_type"), SEP, F.col("city_with_type"))
g3 = F.col("full_address")                                   # destination silver (request.address)
has_dest = F.col("_has_dest").isNotNull()
full_address = (F.when(has_dest, F.coalesce(g1, g2, g3))
                 .when(partner_without_dest, F.col("_e_full_address")))   # else NULL, as today
addr_group = (F.when(~has_dest, F.when(partner_without_dest, "ENTITY"))
                .when(g1.isNotNull(), "G1").when(g2.isNotNull(), "G2").when(g3.isNotNull(), "G3"))
```
Further changes:
- `FROM_ENTITY` is derived as today. It becomes (`full_address`, `ward`, `city`, `lat`, `lng`).
- The `from_dest` loop skips `ADDR_ONLY` and `full_address`. Output `full_address` and `addr_group` (as `_addr_group`) from the expressions above. Output `F.col("street")` from the entity.
- The destination silver no longer has `street`, so there is no ambiguity.
- Metrics from `_addr_group` as §12, then drop `_addr_group`. Change the `_require` hint to `enrbrzpy`.
- Markdown:
  - `street` comes from the entity.
  - The `full_address` groups and the blank rule.
  - `destination_name` is no longer "chưa có luồng ghi".

### 17.6 PostgreSQL and API

- `sql/postgres/gld_srv_serve.pg.sql`:
  - `cost_vnd text` → `cost text`.
  - Add a header line: `-- DB đã có bảng trước 20261116-enr-lang-destination-from-bronze: chạy tay ALTER TABLE apps.srv_poi_multi_lang RENAME COLUMN cost_vnd TO cost; (runbook B5.2)`.
- `SrvPoiMultiLang.java`: `@Column(name = "cost") private String cost;`.
- `PoiService.java:180-181`: use `getCost`, and field label `"cost"`.
- `StoredJsonParser.labelValue`:
  - Also accept an object whose key set is exactly {`text`, `label`}, both textual. Return `LabelValue(label, text)`.
  - Every other shape keeps today's one-key rule and warning.
- Tests:
  - `PoiRepositoryIntegrationTest` uses `.cost(...)`.
  - `PoiServiceTest` adds both shapes, `{text,label}` with a non-text value (null result plus warning), and extra keys (null result).

### 17.7 Docs

- `mapping_gld_srv_poi_multi_lang.md`: §1.1 and §1.2 use `cost`.
- `mapping_gld_srv_poi_info.md`:
  - §1.1 (`DEST_COLS`, `FROM_ENTITY`)
  - the §1.2 rows for `full_address` and `street`
  - `destination_name` has a writer now
  - §1.6 is already updated (D-5)
- `practical_info.md`: row 9 is `apps.srv_poi_multi_lang.cost`. Rows 8 to 10 describe both stored shapes.
- New `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md`, structured like the CMS doc:
  - `cdc_ts_ms` holds `version`
  - the preflight
  - the 3 legacy rows
- `CTRL_TABLES_CONTEXT.md`: data rows in §3, §4, and §5 for the new source.

## 18. Verification

Local (Main):
- `python -m pytest tests -q`.
- New `tests/test_enr_extract_contract.py`, modelled on `test_cms_l1_contract.py`:
  - `test_presence_routes_by_event_type_exact`, `test_no_lit_true_presence`
  - `test_state_key_row_and_all_keys_checked`, `test_order_columns_version_then_event_processed`
  - `test_merge_guard_strict_tuple`, `test_merge_on_keys`
  - `test_array_projection_uses_from_json_transform_to_json`, `test_no_get_json_object_wildcard`
  - `test_registry_paths_relative_to_data`, `test_registry_columns_match_model_design`
  - `test_const_null_cols_not_in_registry`, `test_config_and_watermark_rows`, `test_seed_cells_match_between_ddl_notebooks`
  - `test_extract_preflight_retired_and_const_null_columns`
  - planner tests, exec'ing `BEGIN_REWRITE_PURE`:
    - `test_rewrite_plan_skip_when_equal`
    - `test_rewrite_plan_renames_cost_vnd`
    - `test_rewrite_plan_drop_only_allowed`
    - `test_rewrite_plan_rejects_old_and_new_together`
    - `test_rewrite_plan_type_mismatch_raises`
    - `test_rewrite_plan_not_null_without_source_raises`
  - cell text tests:
    - `test_rewrite_pure_block_identical_in_both_cells`
    - `test_rewrite_cells_no_drop_table_columnmapping_rename`
    - `test_rewrite_cells_overwrite_schema_from_pinned_version`
    - `test_rewrite_cells_restore_on_failed_check`
    - `test_rewrite_cells_hold_locks`
    - `test_silver_rewrite_targets_match_initial_ddl`
    - `test_gold_rewrite_rename_map_only_cost`
    - `test_rewrite_cells_order_after_seeds_cell` (cell order `enrbrzcfg` → `enrbrz` → `enrgld`)
- `tests/test_gld_srv_poi_contract.py`:
  - update `test_multi_lang_i18n_only_branch`, `test_partner_without_destination_branch`, `test_build_columns_match_ddl`
  - add:
    - `test_info_full_address_groups_no_concat_ws`
    - `test_info_full_address_blank_skips_group` (trim-based NULL on `house_number` and `street`)
    - `test_info_street_from_entity`
    - `test_multi_lang_cost_guard` (guard is in `build`, before any write)
    - `test_no_cost_vnd_in_active_surface` (notebooks, PostgreSQL DDL, Java main; excludes `notebooks_lgc`, historical cells, and the planner's rename map)
- Existing tests to update:
  - `test_enr_poi_contract.py` `LANDING_ML` (line 78; leave the `LANDING` history at line 64 unchanged)
  - `test_initial_ddl_contract.py::test_columns_match_sources`, `::test_pipeline_config_rows_match_sources`, `::test_watermark_rows_match_source`
  - `test_srv_poi_serving_contract.py::test_gold_and_pg_columns_and_types_match`, `::test_entities_match_gold_columns_types_and_keys`
  - `test_srv_poi_api_mapping_required.py::test_cited_source_columns_exist_in_ddl`
- API: `mvn -q -f services/data-serving-service/pom.xml test -Dtest=PoiServiceTest`. Run `PoiRepositoryIntegrationTest` only if Docker is available; otherwise record it as skipped with the reason.
- `python scripts/vv.py verify 20261116-enr-lang-destination-from-bronze`.

Runtime (user, `runtime-runbook.md`, after local PASS):
- R-0 answers recorded.
- `enrbrzpy` output for multi_lang:
  - REWRITTEN, `rows_before = rows_after = 3`
  - `renamed_nonnull` old = new
  - `not_null_set` covers `poi_id`
- `enrbrzpy` output for destination: REWRITTEN with 0 rows, `dropped_nonnull = 0`.
- Extract dry run: `cast_null = 0`, `by_event_type.other = 0`.
- After the real extract run:
  - `COUNT(*) = COUNT(DISTINCT poi_id, lang)` on multi_lang, and `COUNT(*) = COUNT(DISTINCT poi_id)` on destination.
  - A rerun gives NO_DATA and 0 updated rows.
  - `size(from_json(destination_id,'array<string>')) = size(from_json(destination,'array<string>'))` on every row.
  - The known null element is present at its position.
  - `country_code` and `postal_code` are NULL everywhere.
  - Report the legacy rows: `count(*) WHERE _src_version IS NULL` on multi_lang.
- `enrgldpy`: REWRITTEN, `rows = 859` (or the current live count), `renamed_nonnull` old = new, props ⊇ P-1 props, reader 1 / writer 2 unchanged.
- NB_00 forced run: both nodes SUCCESS. The `full_address_g1/g2/g3/entity/null` counts match a SQL recomputation.
- PostgreSQL after the next Copy Job run:
  - row count = gold live count
  - `count(cost)` = gold `count(cost)`
- API `practical_info` returns a non-null `cost` for an enriched POI, with the label taken from the stored `label`.

## 19. Decisions for `decision.md`

- A-1 to A-9: unchanged (D-8).
- A-10: superseded by A-11 and A-12.
- A-11: both silver tables change by an in-place overwrite rewrite (`enrbrzpy`) that keeps rows and history and restores itself on a failed check. No DROP, no column mapping.
- A-12: gold `cost_vnd` → `cost` by the same rewrite (`enrgldpy`), run only in runbook B5.1. No column mapping. Gold protocol stays 1/2.
- A-13: the extract preflight fails closed on retired columns or missing constant-NULL columns. The gold multi_lang guard runs inside `build`, before `ensure_target`.
- A-14: rollout order B1 to B5. The PostgreSQL `ALTER` follows the gold rewrite in the same Copy Job interval. Copy Job pause and write mode are a runtime stop (R-0), not a code dependency.
- A-15: blank in D-5 means Spark `trim(x) = ''`, the same definition as probe P-4. The output keeps the value untrimmed.

Probe status:
- P-1, P-3, P-4: closed (D-10).
- P-2: closed by D-11 (by name). Pause and write mode move to R-0.
- P-5 and P-6: runtime, non-blocking.

## 20. Proposed scope.files

`scope.files` is empty, so this document has no `FILE` blocks. Main sets these paths before implementation:
- `notebooks/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.ipynb`
- `notebooks/NB_CREATE_DDL.ipynb`
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb`
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb`
- `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb`
- `sql/postgres/gld_srv_serve.pg.sql`
- `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiMultiLang.java`
- `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/PoiService.java`
- `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/service/util/StoredJsonParser.java`
- `services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/service/PoiServiceTest.java`
- `services/data-serving-service/src/test/java/vn/visitvietnam/dataserving/domain/repository/PoiRepositoryIntegrationTest.java`
- `tests/test_enr_extract_contract.py`
- `tests/test_gld_srv_poi_contract.py`
- `tests/test_enr_poi_contract.py`
- `tests/test_initial_ddl_contract.py`
- `tests/test_srv_poi_serving_contract.py`
- `tests/test_srv_poi_api_mapping_required.py`
- `docs/context/mapping_gld_srv_poi_info.md`
- `docs/context/mapping_gld_srv_poi_multi_lang.md`
- `docs/context/api-mapping/practical_info.md`
- `docs/context/CTRL_TABLES_CONTEXT.md`
- `docs/context/NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV.md`
- `.ai/tasks/20261116-enr-lang-destination-from-bronze/runtime-runbook.md`
