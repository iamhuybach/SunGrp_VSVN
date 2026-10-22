RESULT: PASS

## Main brief

### Decision
- Each landing table becomes a `SPEC.inputs` role, with one `APPEND` ctrl edge on `PL_VV_TRANS_SLV_TO_ENR_15P`. The lib's `_resolve_node` requires that. A flag is the existence of the key among the distinct landing keys at the pinned version. Keys to recompute are the key-level symmetric difference (`_flag_keys`). The new edges start with a `FULL` baseline, so the first run after the patch rewrites every live key with true/false.
- The flags sit just before `created_at`. `check_append_schema` matches by position, so the patch uses `ADD COLUMNS … AFTER`.
- New cells `enrflagmd` and `enrflagpy` at the end of `NB_CREATE_DDL` hold the current `INFO_COLS`, `REVIEW_COLS`, `LANDING_COLS` and `EDGES_ON`. The tests read them from there.
- `district` and `destination_name` go only through a manual runbook step: column mapping, then `DROP COLUMNS`, after user stop S1. `enrflagpy` stops before writing anything while either column exists. No `DROP TABLE`, no `UPDATE` of gold rows.

### Invariants Main must preserve
- No flag the node writes is NULL. The `block_checks` entry `enrich_flag_null` is present in both SPECs.
- Landing is reduced to `select(key).distinct()` before any join. No landing content column is read.
- Info `BEGIN_INFO_SELECT` aliases + `created_at`, `updated_at` == `INFO`. Review select aliases + `created_at`, `updated_at` == `REVIEW`.
- Info `SPEC.inputs` values == `INFO_INPUTS` (9). Review == `{slv_3p_poi_review, slv_enr_poi_review_multi_lang}`. `required_inputs` unchanged: `("entity",)` and `("review",)`.
- `enrflagpy` with `#` comment lines removed contains no `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE`, `columnMapping`, `SET is_active` or `UPDATE {CFG}`. All preconditions run before the first write.
- `enrflagpy` runs under the `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` lock and releases it in `finally`. A second run changes nothing.
- Setup `TABLE_SPECS` has 16 entries, and `slv_poi_entity_non_enrich` stays last.
- Old `NB_CREATE_DDL` cells are not modified. `COORD` in the tests is unchanged.
- Landing DDL: only the first column is `NOT NULL`. No `UNIQUE`. `description` is spelled correctly. The review landing table has no `lang` column.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_CREATE_DDL.ipynb | new markdown `enrflagmd` (appended after `mvpoipy`) | `# [THÊM 22/10] 20261022-enr-landing-and-gld-flags` | ids[-2:] == enrflagmd, enrflagpy |
| 2 | notebooks/NB_CREATE_DDL.ipynb | new code `enrflagpy` | Full cell per doc §15.1. Inline the `enrinfopy` lock MERGE/UPDATE/owner check, edge INSERT…WHERE NOT EXISTS, and finally block verbatim. | Tests in row 9 pass |
| 3 | notebooks/NB_ENR_POI_INFO.ipynb | cell `36415d3b` header, `REQUIRED_COLS` | `[SỬA 22/10]` line; add `multi_lang`, `destination` → `("poi_id",)` | `_require` covers the 6 roles |
| 4 | notebooks/NB_ENR_POI_INFO.ipynb | cell `36415d3b` new `_flag_keys`, `_present` after `_keys` | Code in doc §15.2 | Same `_flag_keys` text as the review notebook |
| 5 | notebooks/NB_ENR_POI_INFO.ipynb | cell `36415d3b` `build` | union `_flag_keys` for both roles into `changed`; `{role}_key_not_in_entity` warnings; `ml`/`dest` left joins | Changed-key loop for both roles present |
| 6 | notebooks/NB_ENR_POI_INFO.ipynb | cell `36415d3b` `BEGIN_INFO_SELECT` | Delete the district (COL-041) and destination_name (COL-042) lines. Add the 2 `isNotNull().alias` flags after `service_flag`. | `test_info_select_matches_ddl` passes |
| 7 | notebooks/NB_ENR_POI_INFO.ipynb | cell `36415d3b` `SPEC` | Add 2 inputs and the `enrich_flag_null` block check | `test_info_spec_inputs_match_active_edges` passes |
| 8 | notebooks/NB_ENR_POI_REVIEW.ipynb | cell `04339a06` `_flag_keys`, `build`, `SPEC` | Code in doc §15.2. Keep existing checks and COL comments. | `test_flag_node_contract` passes |
| 9 | tests/test_enr_poi_contract.py | constants `INFO`, `REVIEW`; new constants; tests listed in doc §15.5 | Update lists; add `INFO_FLAGS`, `INFO_REMOVED`, `REVIEW_FLAGS`, `LANDING`, `FLAG_EDGES`, `INFO_INPUTS`, `REVIEW_INPUTS`; edit 4 tests; add 3 tests | pytest green |
| 10 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` `TABLE_SPECS` | Info spec −2 / +2 flags after `service_flag`; review +flag after `review_updated_at`; 3 landing specs before the `# [SỬA 20/10] Bảng node` line | `test_columns_match_sources` passes |
| 11 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` | 3 rows after the `slv_pn_business_service_i18ns → gld_enr_poi_info` row, in `EDGES_ON` order | 52 rows; `test_pipeline_config_rows_match_sources` passes |
| 12 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_plan` | `13` → `16` (check and message) | Plan accepts 16 fq |
| 13 | tests/test_initial_ddl_contract.py | `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_info_patch_create_matches_init` (replaced), `test_pipeline_config_rows_match_sources`, `test_enr_initial_edge_state` | Per doc §15.5 | pytest green |

### Order and stop points
1. Edit rows 1–2, then 10–12, then 3–8, then 9 and 13. Run the local tests.
2. Run `python scripts/vv.py verify 20261022-enr-landing-and-gld-flags`. Go to review.
3. Ask the runbook author for `runtime-runbook.md`, covering doc §12 R0–R8 and §13. Vietnamese prose, with the SQL from §15.3.
4. **STOP S1 (evidence + user decision):**
   - P1: on an empty scratch table, turn on column mapping, drop a column, then read it through the `lh_vv_gold` SQL analytics endpoint and the known semantic models.
   - P2: the user lists readers of `gld_enr_poi_info` outside the repo.
   - P3: record `v_info0` and `v_review0`.
   - The user accepts the irreversible protocol upgrade. If P1 fails, stop at user_decision: REPLACE plus re-insert by time travel (doc §4.4 option c), or change D-05.
5. Pause the trigger and confirm the lock is free. Git sync. Run R3 (the drop SQL). Run `enrflagpy` twice; the second run must change nothing.
6. Run the info node manually, then the review node: `DRY_RUN`, then `RUN`. Record durations (this avoids the 25-minute DAG timeout on the full backfill).
7. **STOP S2 (user approval):** R7 inserts test landing rows in DEV, expects true, deletes them, expects false. Then run V1–V4 and resume the trigger.

### Tests and verification
- `python -m pytest tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest -q`
- `python scripts/vv.py verify 20261022-enr-landing-and-gld-flags`
- New or renamed tests: `test_flag_patch_constants`, `test_flag_patch_guards`, `test_flag_node_contract`, `test_flag_patch_create_matches_init`.
- Edited tests: `test_gold_ddl_matches_mapping`, `test_mapping_comments_and_edges`, `test_info_patch_cell_guards`, `test_info_spec_inputs_match_active_edges`, `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_pipeline_config_rows_match_sources`, `test_enr_initial_edge_state`.
- Runtime V1–V4 and R7 queries are in doc §16. Evidence must contain no `review_text` or `description` values.

### Read only if needed
- §4.1 Flag freshness → rows 7, 8, 11, 2 (`EDGES_ON`)
- §4.2 Keys to recompute → rows 4, 5, 8
- §4.3 Backfill → order step 6, V2
- §4.4 Column removal → row 2 (`_missing_flags`), stop S1, §15.3
- §4.5 Flag position → rows 2 (`_add_flags`), 6, 10
- §4.6 Contract location → rows 1, 2, 9, 13
- §7 Ordering, §11 Partial failure, §13 Rollback → runbook, order steps 4–7
- §14 Observability → rows 5, 8 (warnings, block checks)
- §15.1–15.5 Implementation → every row
- Non-blocking follow-ups for a user scope decision: `docs/context/CTRL_TABLES_CONTEXT.md` line 135, `docs/context/gld_enr_poi_info_review.md`, `docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md` (COL-041/042).

# Architecture: 20261022-enr-landing-and-gld-flags

Grain, keys, columns and lineage come from `model-design.md` (`## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`). This document settles model-design `## Conflicts and questions` items 2, 3, 4 (within the bound set by `decision.md` history 2026-10-22), 6 and 7. It leaves 1, 5 and 8 open, as the ledger says.

## 1. Scope

- DDL for `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination` and `slv_enr_poi_review_multi_lang`, in both DDL notebooks (D-01, D-02, D-08).
- `gld_enr_poi_info`: drop `district` and `destination_name` from the contract and from the build (D-05). Add `is_enriched_multi_lang` and `is_enriched_destination` (D-04, D-07).
- `gld_enr_poi_review`: add `is_enriched_multi_lang`.
- Three ctrl edges, `APPEND`, on `PL_VV_TRANS_SLV_TO_ENR_15P`: landing → gold. The lib requires them (§4.1).
- Contract tests in `tests/test_enr_poi_contract.py` and `tests/test_initial_ddl_contract.py`.
- Required content for `runtime-runbook.md`, which the runbook author writes (§12). It is not a file in this design's scope.

## 2. Non-goals

- No landing loader, no landing key or `UNIQUE` constraint, no landing grain (D-03, D-08).
- No enrich content copied to gold (D-04). The gold columns `time_to_spend`, `best_time` and `cost_vnd` keep their current rules.
- No change to the lib (`NB_LIB_TRANSFORM_SLV_GLD`), to `NB_00`, to pipeline JSON, or to `gld_enr_poi_coordinate`.
- No new node, table tier or schema. No `DROP TABLE`. No `UPDATE` of gold rows.
- Docs are not edited. `docs/context/CTRL_TABLES_CONTEXT.md` line 135 (the list of gold edges) and `docs/context/gld_enr_poi_info_review.md` / `docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md` (COL-041, COL-042) go stale. They are listed as follow-ups for a user scope decision. They are documentation, not runtime readers.

## 3. Invariants

- I1. A flag equals "the gold key has at least one row in the landing table at the version the node read". It is never NULL in a row the node writes. The `block_checks` entry `enrich_flag_null` enforces this.
- I2. A flag never fans out a gold row. Landing is reduced to `distinct` key values before the join. Gold grain stays one row per `poi_id` / `review_id` per append batch (`model-design.md` `## Entities and grain`).
- I3. No landing content column is read. The only landing column a node reads is `poi_id` or `review_id`.
- I4. The physical column order of both gold tables is: build columns in order, then `created_at` and `updated_at`. `check_append_schema` (lib cell `191e1851`) compares name, type, position and nullability exactly. The flags therefore sit immediately before `created_at` in fresh environments and in patched ones.
- I5. Each node's `SPEC.inputs` values equal its active ctrl edge sources exactly (`_resolve_node`). Info has 9 sources and review has 2.
- I6. The patch cell writes nothing until every precondition passes. Running it again changes nothing. It never drops a column or a table, and never deletes a row.
- I7. `district` and `destination_name` are removed from an existing table only by the manual runbook step, after explicit user confirmation.
- I8. Landing tables are external sources: no node writes them, and gold never reads gold.

## 4. Decisions and alternatives

### 4.1 Flag freshness (model-design conflict 2): landing tables are node inputs with ctrl edges

| Option | Verdict |
|---|---|
| A. Add each landing table to `SPEC.inputs` and add one `APPEND` edge each in ctrl. | **Selected.** `_resolve_node` rejects any input that has no edge. Each run pins the landing version, the edge inbox detects new landing commits, and `NB_00` advances the edge watermark. A new landing row refreshes the flag on the next 15-minute run. No new tier or node. |
| B. Read landing with `spark.table` inside `build`, with no edge. | Rejected. Reads are not pinned, there is no dirty detection, and flags stay stale until another input changes for that key. |
| C. A separate flag node or table. | Rejected. It adds a table and a node, and gold would read gold. |

The landing tables have no producer in any pipeline, so `build_dag` treats them as external. `NB_00` fails with "Bảng đầu vào ngoài chưa tồn tại" if a landing table is missing, so the DDL must exist before the edges go active. The patch cell creates the tables before it inserts the edges.

### 4.2 Keys to recompute: key-level symmetric difference

A flag can change only when a key appears in or disappears from the landing key set. `_flag_keys` returns `(keys@to − keys@from) ∪ (keys@from − keys@to)` over distinct keys. It is exact and does not depend on grain (D-03). The alternative was to reuse `_role_keys`, which subtracts full rows. That would also re-append gold rows when only landing content changes (for example `description`), and it subtracts long text columns. Rejected.

When there is no usable baseline (`FULL`, `FORCE`, `FULL_VERSION_UNAVAILABLE`, or `from` is None), the helper returns every live key. `ctx.changed(role)` is called first because it can switch the basis (same reason as the comment in `_role_keys`).

### 4.3 Backfill of existing rows (conflict 3)

A new edge has no watermark and no marker entry, so `choose_append_baseline` returns `FULL` for the landing role. The first run after the patch therefore recomputes and appends every live key once, writing true or false. No `UPDATE`: it would invalidate the append marker and rewrite history. `p_force=true` is only the fallback. Rows appended before the patch keep NULL flags (D-07). Consumers that read the latest row per key get non-NULL values.

### 4.4 Removing `district` and `destination_name` (conflict 4)

`check_append_schema` requires an exact match, so leaving the columns in place while the build stops writing them fails every run. `decision.md` history also rules that option out.

| Option | Verdict |
|---|---|
| a. Manual runbook step: turn on Delta column mapping (`name` mode), then `ALTER TABLE … DROP COLUMNS (district, destination_name)`. | **Selected.** Metadata only. No data rewrite and no empty-table window. The append marker survives: `DROP COLUMNS` and `SET TBLPROPERTIES` are not in `APPEND_INVALIDATING_OPS`. No transform node reads gold info, so `DEFAULT_NON_DATA_OPS` does not matter here. Cost: the protocol upgrade (reader 2 / writer 5) cannot be undone. Hence probe P1 and user stop S1. |
| b. `DROP TABLE` + recreate (the 20261021 D-18 style reset). | Rejected. The request's acceptance criteria say "No `DROP` of a table that has data". |
| c. `CREATE OR REPLACE TABLE` with the new schema, then re-insert from `VERSION AS OF v0`. | Contingency only. No protocol upgrade, but it takes two statements with an empty-table window, rewrites all history, and invalidates the marker. Offer it at S1 only if P1 fails. |
| d. The patch cell runs the drop behind a flag. | Rejected. The `NB_CREATE_DDL` markdown (cell 4) forbids combining `ALTER TABLE` and `DROP COLUMN` in one cell. The request says no silent `DROP COLUMN`. |

When the old columns are present, the patch cell stops before any write. Its message names the runbook step. Its header comment states the method.

### 4.5 Flag position (conflict 6)

I4 decides this. In `NB_SETUP_INITIAL_DDL` the flags go after `service_flag` / `review_updated_at`. The patch uses `ALTER TABLE … ADD COLUMNS (`flag` BOOLEAN AFTER `anchor`)`, one statement per flag, in contract order.

### 4.6 Where the new contract lives (conflict 7)

New cells `enrflagmd` (markdown) and `enrflagpy` (code) go at the end of `NB_CREATE_DDL`. `enrflagpy` holds the full current `INFO_COLS`, `REVIEW_COLS` and `LANDING_COLS`, and the tests read from it. `enrinfopy` and `enrddlpy` stay unchanged as history.

## 5. State ownership

| State | Owner (writer) |
|---|---|
| Landing table DDL | `NB_SETUP_INITIAL_DDL` `init_tables`, `NB_CREATE_DDL` `enrflagpy` |
| Landing rows | A future loader (D-08). Nobody in this task. |
| `gld_enr_poi_info` / `gld_enr_poi_review` rows | `NB_ENR_POI_INFO` / `NB_ENR_POI_REVIEW` through lib `APPEND` |
| Gold schema additions | `enrflagpy`. The removal is the runbook step. |
| `ctrl_mng_pipeline_config` landing edges | `init_seed_ctrl` (empty environment), `enrflagpy` (existing environment) |
| `ctrl_mng_watermark` edge rows `wm_e__gld_enr_poi_*__slv_enr_*` | `NB_00` only, created on the first successful run. `enrflagpy` touches only the lock fields of `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`. |
| Append marker | Lib `append_target` |

## 6. Grain and keys

No change to the grain or keys in `model-design.md` `## Entities and grain` and `## Keys`. The gold primary keys stay `poi_id` / `review_id` (`SPEC.pk`). Landing has no declared key (D-02, D-03). The flag joins use distinct landing keys (I2). A NULL landing key is filtered out and cannot occur anyway on a `NOT NULL` column. `slv_enr_poi_review_multi_lang.poi_id` is never read (model-design item 8).

## 7. Ordering

- Inside the DAG: unchanged. Info still runs after entity and amenity. Landing edges are external and add no node dependency.
- Rollout order is in §12. Every intermediate state fails closed:
  - Old node code with the new schema: `check_append_schema` → `ConfigError`, nothing written.
  - New node code without the edges: `_resolve_node` → `ConfigError`.
  - New code with the old columns present: schema mismatch.

## 8. Transaction and commit boundaries

- Each Delta statement is its own commit. There is no transaction across tables.
- Patch cell commit order: up to 5 `CREATE TABLE IF NOT EXISTS`, then up to 3 `ALTER … ADD COLUMNS`, then 1 `INSERT INTO ctrl … WHERE NOT EXISTS`. All of it runs under the flow lock, after all preconditions.
- Runbook drop step: 1 `SET TBLPROPERTIES` commit and 1 `DROP COLUMNS` commit.
- A node run makes one append commit (`append_target`, deduplicated by `exec_id` marker). `NB_00` advances the edge watermarks after the node succeeds. This lib behaviour is unchanged.

## 9. Idempotency

- Patch cell:
  - `CREATE … IF NOT EXISTS` runs only for missing tables.
  - An `ADD COLUMNS` runs only for a missing flag. The precondition `got == want minus missing flags` guarantees the anchor exists.
  - Edge insert is `WHERE NOT EXISTS` on (pl, src_schema, src_tbl, trg_schema, trg_tbl).
  - A second run prints no change.
- Node:
  - Unchanged lib idempotency. A retry with the same `exec_id` does not append again.
  - After a failure, the next run recomputes the same keys. The extra append rows have the same content, so the latest-per-key result does not change.
  - Flags are a pure function of the pinned landing version.

## 10. Concurrency

- `enrflagpy` takes `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` with the same lease pattern as `enrinfopy` (35 minutes) and releases it in `finally`. It cannot overlap an `NB_00` run or a manual node `RUN`.
- The runbook drop step runs outside the lock. It requires the 15P trigger to be paused and `lock_exec_id IS NULL`, checked before and after the step.
- A future landing writer that runs while the node runs: the node reads the pinned `VERSION AS OF`, and a later landing commit makes the edge dirty for the next run. No lost update.

## 11. Retry, recovery and partial failure

| Failure point | State | Recovery |
|---|---|---|
| Patch precondition fails | Nothing written. Lock released with `FAILED`. | Fix the cause (runbook drop step, edge `is_active`), then run the cell again. |
| Patch fails after some commits | Some landing tables or flags exist, edges not yet inserted. Nodes fail closed (§7). | Run the cell again. Every step is idempotent. |
| Drop step: `SET TBLPROPERTIES` succeeded, `DROP` failed | Column mapping is on, the old columns are still there. | Run `DROP COLUMNS` again. |
| First full run exceeds the 25-minute DAG timeout | No edge watermark for landing. The next run is `FULL` again. | Run the node manually once (§12 R5). The manual-run marker records the landing source versions, so the next `NB_00` run uses `MARKER`. |
| Full run trips an existing QG (`rating_cast_overflow`, `block_checks`) on old rows | Node `FAILED`, nothing written. | Evidence item. Fix the data or the rule in a separate decision. Do not bypass. |
| Landing version vacuumed | `ctx.changed` switches the basis to `FULL_VERSION_UNAVAILABLE` and `_flag_keys` returns every key. | Automatic. |

## 12. Rollout (required `runtime-runbook.md` content, Vietnamese prose)

- **R0 probes (stop S1, user decision).**
  - P1: in DEV, create an empty scratch table in `lh_vv_gold.enr`, turn on column mapping (`'delta.minReaderVersion'='2','delta.minWriterVersion'='5','delta.columnMapping.mode'='name'`), drop one column, then query it through the `lh_vv_gold` SQL analytics endpoint and every semantic model or shortcut that reads `gld_enr_poi_info`. Record the result, then drop the empty scratch table.
  - P2: the user lists the readers of `gld_enr_poi_info` outside the repo.
  - P3: record `DESCRIBE HISTORY … LIMIT 1` versions `v_info0` and `v_review0`, and confirm no VACUUM is planned during the rollback window.
  - Decision blocked: whether to accept the irreversible protocol upgrade. If P1 fails → user decision between §4.4 option c and changing D-05.
- **R1.** Pause the 15P trigger and wait until `lock_exec_id IS NULL` on `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`.
- **R2.** Git sync the four notebooks.
- **R3. "Bỏ cột cũ gld_enr_poi_info".** Only after S1 approval. Run the two statements in §15.3, then check with `DESCRIBE TABLE`.
- **R4.** Run `NB_CREATE_DDL` cell `enrflagpy` only. Run it a second time and expect no change.
- **R5.** Run `NB_ENR_POI_INFO` and then `NB_ENR_POI_REVIEW` manually: first `p_mode=DRY_RUN`, then `RUN`. Record the durations from `ctrl_log_table_run`.
- **R6.** Verification queries V1–V4 (§16).
- **R7 (stop S2, user approval: writes DEV test data).**
  1. Insert one row into `slv_enr_poi_info_multi_lang`, `slv_enr_poi_destination` and `slv_enr_poi_review_multi_lang`, each with an existing key.
  2. Trigger the pipeline once and expect true for those keys.
  3. `DELETE` the test rows, trigger again, and expect false.
- **R8.** Resume the trigger. Check that the next scheduled run is `NO_DATA` or incremental.

## 13. Rollback and forward recovery

- Prefer forward fixes: every intermediate state fails closed and writes no wrong data.
- Full rollback, user-run:
  1. `UPDATE ctrl_mng_pipeline_config SET is_active = 0` for the 3 landing edges, with a condition that the value differs. Keep the rows.
  2. `RESTORE TABLE gld_enr_poi_info TO VERSION AS OF v_info0`. The old columns come back. The protocol upgrade stays.
  3. `RESTORE TABLE gld_enr_poi_review TO VERSION AS OF v_review0`.
  4. Revert the four notebooks and git sync.
  5. Run both nodes manually with `p_force=true`. RESTORE invalidated the markers and removed the rows appended after v0, while the edge watermarks may have moved past those changes.
  6. Keep the landing tables. Never drop them.
- Before R3 there is nothing to roll back except git.

## 14. Observability

- The lib already writes `qg_json` with `basis`, `changed` and `inbox` for each role, including the landing roles.
- New warnings:
  - `multi_lang_key_not_in_entity` and `destination_key_not_in_entity` (info).
  - `multi_lang_key_not_in_review` (review).
  - These count distinct landing keys with no live gold key. They expose model-design item 5 (partner `poi_id` formula) as soon as a loader exists.
- New block check `enrich_flag_null`.
- `enrflagpy` prints the tables it created, the flags it added and the active landing edges. It raises "Sau khi ghi: …" if the post-check fails.

## 15. Implementation plan

### 15.1 `NB_CREATE_DDL` — append `enrflagmd`, then `enrflagpy`

- `enrflagmd`: markdown, one line: `# [THÊM 22/10] 20261022-enr-landing-and-gld-flags`.
- `enrflagpy`: code cell with the same metadata as `enrinfopy`. Write `INFO_COLS` and `REVIEW_COLS` one tuple per line, as in `enrinfopy`.
  - `INFO_COLS` = `enrinfopy` `INFO_COLS` without `district` and `destination_name`, with `("is_enriched_multi_lang","BOOLEAN")` and `("is_enriched_destination","BOOLEAN")` inserted after `service_flag`. 40 columns.
  - `REVIEW_COLS` = `enrddlpy` `REVIEW_COLS` with `("is_enriched_multi_lang","BOOLEAN")` after `review_updated_at`. 9 columns.

```python
# [THÊM 22/10] 20261022-enr-landing-and-gld-flags
# 1. Tạo 3 bảng landing lh_vv_silver.dbo.slv_enr_* (chỉ DDL, không nạp). Đã có đúng cột -> không đổi; lệch -> dừng.
# 2. gld_enr_poi_info: hợp đồng bỏ district, destination_name; thêm is_enriched_multi_lang, is_enriched_destination
#    ngay sau service_flag (check_append_schema so đúng vị trí; created_at, updated_at ở cuối).
#    Bảng còn district hoặc destination_name -> dừng trước khi ghi, cell không bỏ cột. Làm bước
#    "Bỏ cột cũ gld_enr_poi_info" trong runtime-runbook.md của task (bật delta.columnMapping.mode = 'name' rồi
#    ALTER TABLE ... DROP COLUMNS, chạy tay sau khi người dùng xác nhận) rồi chạy lại cell.
# 3. gld_enr_poi_review: thêm is_enriched_multi_lang ngay sau review_updated_at.
# 4. Thêm 3 cạnh APPEND landing -> gold trên PL_VV_TRANS_SLV_TO_ENR_15P để cờ làm mới khi landing đổi.
# Cột thêm cho phép NULL: dòng cũ giữ NULL; lần chạy node đầu sau cell ghi lại mọi khoá với true / false.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P suốt cell. Chạy lại: không đổi gì.
# Sau cell này không chạy lại enrddlpy, enrinfopy, mvpoipy: hợp đồng và cạnh trong đó là bản cũ.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_ENR_15P"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.enr"
INFO_FQ = f"{GLD}.gld_enr_poi_info"
REVIEW_FQ = f"{GLD}.gld_enr_poi_review"
PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'"
LEASE_MINUTES = 35  # bằng p_lock_timeout_min của NB_00_ORCHES_SLV_TO_ENR_15P

LANDING_COLS = {
    "lh_vv_silver.dbo.slv_enr_poi_info_multi_lang": [
        ("poi_id", "STRING NOT NULL"), ("lang", "STRING"), ("time_to_spend", "STRING"), ("best_time", "STRING"),
        ("cost_vnd", "STRING"), ("description", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
    "lh_vv_silver.dbo.slv_enr_poi_destination": [
        ("poi_id", "STRING NOT NULL"), ("street", "STRING"), ("ward", "STRING"), ("district", "STRING"),
        ("city", "STRING"), ("full_address", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
    "lh_vv_silver.dbo.slv_enr_poi_review_multi_lang": [
        ("review_id", "STRING NOT NULL"), ("poi_id", "STRING"), ("review_text", "STRING"),
        ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ],
}
INFO_COLS = [...]    # 40 dòng, xem 15.1
REVIEW_COLS = [...]  # 9 dòng, xem 15.1
INFO_REMOVED = ("district", "destination_name")
FLAG_COLS = {
    "gld_enr_poi_info": ("is_enriched_multi_lang", "is_enriched_destination"),
    "gld_enr_poi_review": ("is_enriched_multi_lang",),
}
EDGES_ON = [
    (1, "slv_enr_poi_info_multi_lang", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (2, "slv_enr_poi_destination", "lh_vv_gold.enr", "gld_enr_poi_info", "APPEND", "NB_ENR_POI_INFO", 1),
    (3, "slv_enr_poi_review_multi_lang", "lh_vv_gold.enr", "gld_enr_poi_review", "APPEND", "NB_ENR_POI_REVIEW", 1),
]
CONTRACTS = {INFO_FQ: INFO_COLS, REVIEW_FQ: REVIEW_COLS, **LANDING_COLS}
FLAGS = {INFO_FQ: FLAG_COLS["gld_enr_poi_info"], REVIEW_FQ: FLAG_COLS["gld_enr_poi_review"]}
LOCK = "enrflag-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


def _create_sql(fq, cols):
    # Cùng câu với create_sql(spec) của NB_SETUP_INITIAL_DDL (test kiểm tra).
    body = ",\n    ".join(f"`{name}` {dtype}" for name, dtype in cols)
    return f"CREATE TABLE IF NOT EXISTS {fq} (\n    {body}\n) USING DELTA\nTBLPROPERTIES ({PROPS})"


def _missing_flags(fq):
    # Bảng gold đã có: trả cờ còn thiếu. Còn cột cũ hoặc lệch hợp đồng ở chỗ khác -> dừng, không sửa.
    got = _schema(fq)
    names = {name for name, _dtype, _nullable in got}
    old = sorted(names & set(INFO_REMOVED)) if fq == INFO_FQ else []
    if old:
        raise RuntimeError(f"{fq} còn cột {old}: làm bước 'Bỏ cột cũ gld_enr_poi_info' trong runtime-runbook.md "
                           "của task 20261022-enr-landing-and-gld-flags rồi chạy lại cell. Cell không bỏ cột")
    missing = [flag for flag in FLAGS[fq] if flag not in names]
    want = _want(CONTRACTS[fq])
    if got != [col for col in want if col[0] not in missing]:
        raise RuntimeError(f"{fq} không khớp hợp đồng, không sửa: có {got}, cần {want}")
    return missing


def _add_flags(fq, missing):
    # Theo thứ tự hợp đồng, mỗi cờ ngay sau cột đứng trước nó. ADD COLUMNS cho phép NULL (D-07).
    names = [name for name, _dtype in CONTRACTS[fq]]
    for flag in missing:
        anchor = names[names.index(flag) - 1]
        spark.sql(f"ALTER TABLE {fq} ADD COLUMNS (`{flag}` BOOLEAN AFTER `{anchor}`)")


def _edge_rows():
    keys = " OR ".join(f"(src_tbl = '{src}' AND trg_tbl = '{trg}')" for _q, src, _s, trg, _m, _n, _p in EDGES_ON)
    return [(row["src_tbl"], row["trg_tbl"], row["is_active"], row["n"]) for row in spark.sql(f"""
    SELECT src_tbl, trg_tbl, is_active, count(*) AS n FROM {CFG}
    WHERE pl_name = '{PL}' AND src_schema = '{SLV}' AND trg_schema = '{GLD}' AND ({keys})
    GROUP BY src_tbl, trg_tbl, is_active
    """).collect()]


# Tạo dòng khoá nếu chưa có: chép nguyên câu MERGE INTO {WM} của enrinfopy.
held = False
failed = None
try:
    # Nhận khoá: chép nguyên UPDATE {WM} ... lock_exec_id IS NULL OR lease hết hạn, và kiểm tra owner của enrinfopy.
    held = True
    if "nb_name" not in {f.name.lower() for f in spark.table(CFG).schema.fields}:
        raise RuntimeError(f"{CFG} chưa có cột nb_name: chạy enrddlpy trước")

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    create = [fq for fq in CONTRACTS if not spark.catalog.tableExists(fq)]
    for fq, cols in LANDING_COLS.items():
        if fq not in create and _schema(fq) != _want(cols):
            raise RuntimeError(f"{fq} đã có nhưng lệch cột, không sửa: có {_schema(fq)}, cần {_want(cols)}")
    missing = {fq: _missing_flags(fq) for fq in FLAGS if fq not in create}
    bad = [row for row in _edge_rows() if row[2] != 1 or row[3] != 1]
    if bad:
        raise RuntimeError(f"{CFG}: cạnh EDGES_ON đã có nhưng không active đúng một dòng {bad}. Cell không tự bật cạnh")

    for fq in create:
        spark.sql(_create_sql(fq, CONTRACTS[fq]))
        print(f"{fq}: đã tạo theo định nghĩa NB_SETUP_INITIAL_DDL")
    for fq, flags in missing.items():
        _add_flags(fq, flags)
    # INSERT INTO {CFG} ... WHERE NOT EXISTS: chép nguyên câu của enrinfopy (values từ EDGES_ON).

    # Sau khi ghi: chỉ xét phần cell thêm.
    problems = [f"{fq} lệch cột" for fq, cols in LANDING_COLS.items() if _schema(fq) != _want(cols)]
    for fq, flags in FLAGS.items():
        got = _schema(fq)
        names = [name for name, _dtype, _nullable in got]
        contract = [name for name, _dtype in CONTRACTS[fq]]
        for flag in flags:
            anchor = contract[contract.index(flag) - 1]
            if flag not in names or anchor not in names or names.index(flag) != names.index(anchor) + 1:
                problems.append(f"{fq}.{flag} không đứng ngay sau {anchor}")
            elif got[names.index(flag)][1:] != ("boolean", True):
                problems.append(f"{fq}.{flag} cần boolean cho phép NULL")
    left = sorted(set(INFO_REMOVED) & {name for name, _dtype, _nullable in _schema(INFO_FQ)})
    if left:
        problems.append(f"{INFO_FQ} còn {left}")
    active = {(src, trg): n for src, trg, flag, n in _edge_rows() if flag == 1}
    want_edges = {(src, trg): 1 for _q, src, _s, trg, _m, _n, _p in EDGES_ON}
    if active != want_edges:
        problems.append(f"cạnh landing active là {active}, cần {want_edges}")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"landing {sorted(LANDING_COLS)}; cờ {FLAGS}; cạnh {sorted(want_edges)}")
except Exception as exc:
    failed = exc
    raise
finally:
    pass  # nhả khoá: chép nguyên khối finally của enrinfopy (WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}')
```

The comment placeholders ("chép nguyên …") stand for the exact `enrinfopy` statements: the lock-row `MERGE`, the lock `UPDATE` plus the owner check, the edge `INSERT … WHERE NOT EXISTS`, and the `finally` release. Main inlines them verbatim. They must not remain as comments.

### 15.2 Node notebooks

`NB_ENR_POI_INFO` cell `36415d3b`:

1. Add a header line: `# [SỬA 22/10] 20261022-enr-landing-and-gld-flags: bỏ district, destination_name (D-05); thêm 2 cờ landing (D-04).`
2. `REQUIRED_COLS`: add `"multi_lang": ("poi_id",)` and `"destination": ("poi_id",)`.
3. Add the two helpers below after `_keys`. `NB_ENR_POI_REVIEW` gets an identical copy of `_flag_keys`.
4. In `build`, after the existing `_role_keys` loop, add `for role in ("multi_lang", "destination"): changed = changed.union(_flag_keys(ctx, role, "poi_id", spine_keys))`.
5. After `ctx.warn("review_poi_not_in_entity", …)`, for each role add `ctx.warn(f"{role}_key_not_in_entity", ctx.input(role).select("poi_id").distinct().join(spine_keys, "poi_id", "left_anti").count())`.
6. Define `ml = _present(ctx, "multi_lang", "poi_id", changed).alias("ml")` and `dest = _present(ctx, "destination", "poi_id", changed).alias("dest")`. Append two left joins to `base` on `e.poi_id`.
7. In `BEGIN_INFO_SELECT`, delete the `district` (COL-041) and `destination_name` (COL-042) lines. After `service_flag`, add `F.col("ml.poi_id").isNotNull().alias("is_enriched_multi_lang"),  # D-04` and `F.col("dest.poi_id").isNotNull().alias("is_enriched_destination"),  # D-04`.
8. `SPEC.inputs`: add `"multi_lang": "slv_enr_poi_info_multi_lang"` and `"destination": "slv_enr_poi_destination"`. `block_checks`: add `("enrich_flag_null", "is_enriched_multi_lang IS NULL OR is_enriched_destination IS NULL")`. `required_inputs` stays `("entity",)`.

```python
def _flag_keys(ctx, role, key, scope):
    # D-04: cờ chỉ đổi khi tập khoá landing đổi; không phụ thuộc grain (D-03).
    # Không có baseline (cạnh mới, FULL, FORCE, mất version) -> mọi khoá trong scope: lần đầu sau patch ghi lại hết.
    ctx.changed(role)  # gọi trước: có thể đổi basis sang FULL_VERSION_UNAVAILABLE
    info = ctx.basis[role]
    if info["basis"] not in ("EDGE", "MARKER") or info["from"] is None:
        return scope
    if info["from"] >= info["to"]:
        return scope.limit(0)
    now = ctx._input_at(role, info["to"]).select(key).where(F.col(key).isNotNull()).distinct()
    old = ctx._input_at(role, info["from"]).select(key).where(F.col(key).isNotNull()).distinct()
    return now.subtract(old).union(old.subtract(now))


def _present(ctx, role, key, keys):
    # Khoá có >= 1 dòng landing; distinct nên không nhân dòng gold; chỉ đọc cột khoá.
    return ctx.input(role).select(key).where(F.col(key).isNotNull()).distinct().join(keys, key, "left_semi")
```

`NB_ENR_POI_REVIEW` cell `04339a06`. Every existing check and `COL-0xx` comment stays.

```python
def build(ctx: NodeContext) -> DataFrame:
    live_ids = ctx.input("review").select("review_id").where(F.col("review_id").isNotNull()).distinct()
    changed_ids = (ctx.changed("review").select("review_id").where(F.col("review_id").isNotNull())
                   .union(_flag_keys(ctx, "multi_lang", "review_id", live_ids))
                   .distinct()).persist(StorageLevel.MEMORY_AND_DISK)
    ctx.cached.append(changed_ids)
    ml_ids = ctx.input("multi_lang").select("review_id").where(F.col("review_id").isNotNull()).distinct()
    ctx.warn("multi_lang_key_not_in_review", ml_ids.join(live_ids, "review_id", "left_anti").count())
    ml = ml_ids.join(changed_ids, "review_id", "left_semi").withColumn("ml_hit", F.lit(True))
    rv = ctx.input("review").join(changed_ids, "review_id", "left_semi").join(ml, "review_id", "left")
    # ... cast_rating, overflow, review_date, mismatch: giữ nguyên ...
    return rv.select(
        # ... 6 cột hiện có giữ nguyên, kèm comment COL-022..COL-032 ...
        F.col("ml_hit").isNotNull().alias("is_enriched_multi_lang"),  # D-04
        # COL-033 / COL-034 giữ nguyên
    )
```

The review `SPEC` changes:
- `inputs={"review": "slv_3p_poi_review", "multi_lang": "slv_enr_poi_review_multi_lang"}`
- add `block_checks=(("enrich_flag_null", "is_enriched_multi_lang IS NULL"),)`
- `required_inputs=("review",)` stays.

### 15.3 Runbook drop SQL (R3, after S1)

```sql
ALTER TABLE lh_vv_gold.enr.gld_enr_poi_info SET TBLPROPERTIES (
  'delta.minReaderVersion' = '2', 'delta.minWriterVersion' = '5', 'delta.columnMapping.mode' = 'name');
ALTER TABLE lh_vv_gold.enr.gld_enr_poi_info DROP COLUMNS (district, destination_name);
```

### 15.4 `NB_SETUP_INITIAL_DDL`

- `init_tables`:
  - In the `gld_enr_poi_info` spec, delete `district` and `destination_name`. Insert `('is_enriched_multi_lang', 'BOOLEAN', None)` and `('is_enriched_destination', 'BOOLEAN', None)` after `service_flag`.
  - In the `gld_enr_poi_review` spec, insert `('is_enriched_multi_lang', 'BOOLEAN', None)` after `review_updated_at`.
  - Insert three landing specs (`partition` None, `comment` None, `props` PROPS, columns exactly as `LANDING_COLS`, comment None) immediately before the `# [SỬA 20/10] Bảng node` line. `slv_poi_entity_non_enrich` must stay last: `test_poi_entity_columns_derived` uses `specs[-1]`. Add a comment `# [THÊM 22/10] 20261022-enr-landing-and-gld-flags: landing enrich, chỉ DDL.`
- `init_seed_ctrl`: insert after the `slv_pn_business_service_i18ns → gld_enr_poi_info` row, in `EDGES_ON` order:
  - `(_ENR, _S, 'slv_enr_poi_info_multi_lang', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO')`
  - the same shape for `slv_enr_poi_destination` → info
  - `slv_enr_poi_review_multi_lang` → `gld_enr_poi_review` with `'NB_ENR_POI_REVIEW'`
  - plus one comment line `[SỬA 22/10]`.
- `init_plan`: change `13` to `16` in both the check and the message.

### 15.5 Tests

`tests/test_enr_poi_contract.py`:
- `INFO`: remove `district` and `destination_name`. Add `("is_enriched_multi_lang","BOOLEAN"), ("is_enriched_destination","BOOLEAN")` after `service_flag`.
- `REVIEW`: add `("is_enriched_multi_lang","BOOLEAN")` after `review_updated_at`.
- `COORD`: unchanged.
- Add constants:
  - `INFO_FLAGS`, `INFO_REMOVED`, `REVIEW_FLAGS`
  - `LANDING` (equal to `LANDING_COLS`)
  - `FLAG_EDGES` (equal to `EDGES_ON`)
  - `INFO_INPUTS = INFO_ACTIVE + ("slv_enr_poi_info_multi_lang", "slv_enr_poi_destination")`
  - `REVIEW_INPUTS = ("slv_3p_poi_review", "slv_enr_poi_review_multi_lang")`
- `test_gold_ddl_matches_mapping`:
  - `enrflagpy` `INFO_COLS == INFO` and `REVIEW_COLS == REVIEW`.
  - `[c for c in enrinfopy INFO_COLS if c[0] not in INFO_REMOVED] == [c for c in INFO if c[0] not in INFO_FLAGS]`.
  - `[c for c in REVIEW if c[0] not in REVIEW_FLAGS] == enrddlpy REVIEW_COLS`.
  - `COORD` check unchanged.
- `test_mapping_comments_and_edges`: drop 41 and 42 from the "present" list. Add `COL-041` and `COL-042` to the "absent" list.
- `test_info_patch_cell_guards`: `ids[-6:] == ["enrinfomd","enrinfopy","mvpoimd","mvpoipy","enrflagmd","enrflagpy"]`.
- `test_info_spec_inputs_match_active_edges`: compare with `set(INFO_INPUTS)`. Also assert `set(INFO_ACTIVE) | {src for _q, src, _s, trg, *_ in FLAG_EDGES if trg == "gld_enr_poi_info"} == set(INFO_INPUTS)`.
- New `test_flag_patch_constants`: `LANDING_COLS == LANDING` and `EDGES_ON == FLAG_EDGES`. No landing column string contains `UNIQUE`. Only the first column of each landing table is `NOT NULL`.
- New `test_flag_patch_guards`, on `enrflagpy` with `#` comment lines removed:
  - none of `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE`, `columnMapping`, `SET is_active`, `UPDATE {CFG}` appears;
  - `ADD COLUMNS (` and `BOOLEAN AFTER` are present;
  - on the raw text, tokens appear in this order: `held = True`, `Dừng trước khi ghi`, `spark.sql(_create_sql(fq, CONTRACTS[fq]))`, `_add_flags(fq, flags)`, `INSERT INTO {CFG}`, `Sau khi ghi`, `finally:`;
  - `lock_exec_id = '{LOCK}'` is present.
- New `test_flag_node_contract`:
  - Info: `ctx.input(role).select(key)` and `.distinct()` appear in `_present`. Both `isNotNull().alias("is_enriched_…")` expressions are present. `required_inputs=("entity",)`. `enrich_flag_null` is in the cell.
  - Review: the aliases in the select plus `created_at`, `updated_at` equal the `REVIEW` names. `SPEC` inputs equal `set(REVIEW_INPUTS)`. `required_inputs=("review",)`.
  - Both notebooks contain the same `_flag_keys` source text.

`tests/test_initial_ddl_contract.py`:
- `test_table_inventory_matches_sources`: add `_assign(enrflagpy, "LANDING_COLS").keys()` to `found`. Expect `len(specs) == 16`.
- `test_columns_match_sources`: the info, review and landing specs equal the `enrflagpy` lists, with props equal to `PROPS`. Remove the comparisons with `enrinfopy` `INFO_COLS` and `enrddlpy` `REVIEW_COLS`.
- Replace `test_info_patch_create_matches_init` with `test_flag_patch_create_matches_init`:
  - exec the `PROPS` assignment and the `_create_sql` `FunctionDef` from `enrflagpy` (with `ast.unparse`);
  - assert `_create_sql(fq, cols) == create_sql(spec)` for the 5 tables.
- `test_pipeline_config_rows_match_sources`: after the `enrinfopy` `EDGES_ON` loop, add the same loop over `enrflagpy` `EDGES_ON`. Expect `len(expected) == 52`.
- `test_enr_initial_edge_state`: import `INFO_INPUTS` and `REVIEW_INPUTS`. The active info sources equal `set(INFO_INPUTS)`, and the active `gld_enr_poi_review` sources equal `set(REVIEW_INPUTS)`.

## 16. Verification

- Local: `python -m pytest tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py -q`, then `python -m pytest -q`, then `python scripts/vv.py verify 20261022-enr-landing-and-gld-flags`.
- Runtime (R6/R7). Evidence must not contain `review_text` or `description` values.
  - V1: `DESCRIBE TABLE` on both gold tables and the 3 landing tables.
    - Info has no `district` or `destination_name`. The flags sit immediately before `created_at`.
    - The landing columns match `LANDING_COLS`.
  - V2: on the latest info batch (`created_at = max(created_at)`):
    - `count(*)` equals the live POI count of `slv_poi_entity_non_enrich`;
    - `count_if(is_enriched_multi_lang IS NULL OR is_enriched_destination IS NULL) = 0`.
    - Same check for review against the live `slv_3p_poi_review` count.
  - V3: no disagreement between the flag on the latest row per key and `EXISTS` in landing:
    - `row_number() OVER (PARTITION BY poi_id ORDER BY created_at DESC) = 1` left join `SELECT DISTINCT poi_id FROM landing`;
    - `count_if(flag <> (l.poi_id IS NOT NULL)) = 0`;
    - the same for destination and for review.
  - V4: `ctrl_log_table_run` for both nodes shows `SUCCESS`, `basis` `FULL` for the landing roles on the backfill run, and warning counts. A second `enrflagpy` run prints no change.
  - R7: true after the test rows are inserted, false after they are deleted. The `changed` count for the landing role equals the number of test keys.
