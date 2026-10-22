RESULT: PASS

## Main brief

### Decision
1. Make the repo match DEV. DEV already runs both silver nodes on `PL_VV_TRANS_SLV_TO_ENR_15P` (D-02). Change every repo writer of their edges and their flow lock to ENR_15P: the seed and both setup notebooks.
2. Append a new last cell pair `mvpoimd`/`mvpoipy` to `NB_CREATE_DDL`. Under the `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` lock, it checks everything first, then DELETEs 8 pipeline_config rows, then 6 watermark rows (D-03). It never inserts, moves, or re-enables an edge, and it never DROPs.
3. The user drops the two tables from the runbook after a CTAS backup to `lh_vv_silver.dbo.<table>_bak_20261021`. DROP on a Fabric managed table deletes its files, so time travel cannot restore it. Record this as ledger row D-06.
4. Delete `NB_SLV_PN_POI` and `NB_ENR_POI_COORDINATE`. Remove the coordinate spec (TABLE_SPECS 14→13) and the 8 seed rows (seed 57→49).

### Invariants Main must preserve
- No seed or setup code writes `PL_VV_TRANS_SLV_TO_SLV_1H`. The only remaining occurrence in the repo is the historical `entwebpy` cell.
- The seed has exactly 49 rows. The 9 node edges are `_ENR`, `RECOMPUTE`, priority 1, `nb_name` None. No seed row has `src_tbl` or `trg_tbl` in (`slv_pn_poi`, `gld_enr_poi_coordinate`). The 3 old info edges are gone.
- Each active (trg_schema, trg_tbl) in the seed has exactly one `pl_name`.
- `TABLE_SPECS` has 13 entries with no coordinate. `init_plan` checks 13.
- `mvpoipy` contains exactly 2 `DELETE FROM`: `{CFG}` first, then `{WM}`. It contains no DROP, TRUNCATE, ALTER TABLE, INSERT INTO, `SET is_active`, RESTORE, or `UPDATE {CFG}`.
- In `mvpoipy`, every check that raises `Dừng trước khi ghi` comes before the first DELETE. The post-checks raise `Sau khi ghi`, and the lock is released in `finally` only when `lock_exec_id = '{LOCK}'`.
- In `mvpoipy`, the old-info DELETE is guarded by `AND NOT (trg_tbl = 'gld_enr_poi_info' AND is_active <=> 1)`, and the watermark DELETE by `AND lock_exec_id IS NULL`.
- The `# BEGIN_EDGE_PRECHECK` blocks stay byte-identical in the two setup notebooks.
- Historical NB_CREATE_DDL cells (`enrddlpy`, `entwebpy`, `enrinfopy`, and all earlier cells) stay byte-identical. The new cells go last: `ids[-4:] == [enrinfomd, enrinfopy, mvpoimd, mvpoipy]`.
- No pipeline JSON changes. `docs/requirements/*` are not touched.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_CREATE_DDL.ipynb | append after `enrinfopy` | markdown cell `mvpoimd`, source `# [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup` | it is the second-to-last cell |
| 2 | notebooks/NB_CREATE_DDL.ipynb | new last cell `mvpoipy` | exact code in §16.2; metadata as in `enrinfopy` | tests #14 and #15 pass |
| 3 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` | §16.3: drop `_SLV1H`, replace the comment line, remove 8 rows, nodes become `_ENR` | 49 rows |
| 4 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` | delete the `gld_enr_poi_coordinate` spec dict | 13 specs |
| 5 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_plan` | `14` → `13` in the check and the message | text updated |
| 6 | notebooks/NB_SETUP_POI_ENTITY.ipynb | `a1setupedges` | every `PL_VV_TRANS_SLV_TO_SLV_1H` → `PL_VV_TRANS_SLV_TO_ENR_15P`; docstring `pl SLV_1H` → `pl ENR_15P` (§16.4) | no `SLV_TO_SLV_1H` in the notebook |
| 7 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupplan` | the `entity_edges_ok` query uses ENR_15P | same |
| 8 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupedges` | same as #6; the precheck block stays identical to the entity notebook | `test_edge_precheck_blocks_are_identical` |
| 9 | notebooks/NB_SLV_PN_POI.ipynb | file | delete | absent |
| 10 | notebooks/NB_ENR_POI_COORDINATE.ipynb | file | delete | absent |
| 11 | tests/test_initial_ddl_contract.py | `test_table_inventory_matches_sources`, `test_columns_match_sources` | drop coordinate; `len(specs) == 13` | pass |
| 12 | tests/test_initial_ddl_contract.py | `test_pipeline_config_rows_match_sources` | skip keys in `mvpoipy` `EDGES_DELETE`; nodes use ENR_15P; 49 rows | pass |
| 13 | tests/test_initial_ddl_contract.py | `test_dropped_l1_columns_unread`, `test_enr_initial_edge_state`, new `test_enr_15p_dag_order` | per §16.5 | pass |
| 14 | tests/test_enr_poi_contract.py | `test_mapping_comments_and_edges`, `test_info_patch_cell_guards` | remove the coordinate notebook read; cell order becomes `ids[-4:]` | pass |
| 15 | tests/test_enr_poi_contract.py | new `test_cleanup_patch_constants`, `test_cleanup_patch_guards`, `test_removed_notebooks_absent` | per §16.5 | pass |
| 16 | tests/test_poi_entity_contract.py | `test_setup_contract`, `_edge`, `test_create_ddl_patch` | ENR_15P; assert `SLV_1H` absent; `ids[-4:]` | pass |
| 17 | tests/test_poi_amenity_contract.py | `test_setup_contract` | ENR_15P in src; `SLV_1H` not in src | pass |
| 18 | docs/context/CTRL_TABLES_CONTEXT.md | §3 `### Dữ liệu hiện có` L114–133; §10 table | ENR_15P node block, gold edges, setup lock, removal note; add a 21/10 history row (§16.6) | no `SLV_TO_SLV_1H` except the history row |
| 19 | docs/context/01_DATA_MODEL.md | §6 N6, N7, L346 | pipeline sentence → ENR_15P; replace `1H` (§16.6) | no `SLV_TO_SLV_1H` |

### Order and stop points
1. Make edits #1–#19 in one change set, then run the local tests. **Stop: evidence** (pytest output) for review and the risk gate.
2. **Stop: user decision.** Can the ENR_15P schedule be paused on DEV for about 30 minutes? If not, use the fallback (§14): split the change, and delete the notebooks (#9, #10, and their assertions in #14 and #15) only after R3.
3. Copy §17 R0–R8 into the task `runtime-runbook.md` during the runtime phase. That file is not in `scope.files`.
4. User runs R0 (pre-flight, R0 step 2 registry count must be 0), R1 (pause), R2 (sync), R3/R4 (`mvpoipy` twice), and R5 (PLAN). **Stop: evidence.** R3 must print `cạnh=8 watermark=6`, R4 must print `0/0`, and the DAG must show entity → amenity → info. Any `Dừng trước khi ghi` is a **user decision**; do not patch around it.
5. R6 backup + DROP. **Stop: user confirmation** before the DROP, and evidence of backup counts and tableExists.
6. R7 forced RUN (entity and amenity only; never force info) and R8 resume + re-probe. **Stop: evidence** for the runtime gate.

### Tests and verification
- `python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py -q`
- `python -m pytest -q`
- `python -c "import json,sys;[json.load(open(p,encoding='utf-8')) for p in sys.argv[1:]]" notebooks/NB_CREATE_DDL.ipynb notebooks/NB_SETUP_INITIAL_DDL.ipynb notebooks/NB_SETUP_POI_ENTITY.ipynb notebooks/NB_SETUP_POI_AMENITY.ipynb`
- Named tests that must pass:
  - New: `test_cleanup_patch_constants`, `test_cleanup_patch_guards`, `test_removed_notebooks_absent`, `test_enr_15p_dag_order`.
  - Updated: `test_pipeline_config_rows_match_sources`, `test_enr_initial_edge_state`, `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_info_patch_cell_guards`, `test_create_ddl_patch`, both `test_setup_contract`.
  - Unchanged: `test_edge_precheck_blocks_are_identical`, `test_legacy_retire_and_foreign_schema_do_not_block`, `test_pipeline_timeouts`.
- Runtime: R3–R8 expected values in §17 (INV-1 = 16, INV-3 = 17 after the change).

### Read only if needed
- §1 Scope, §2 Non-goals → #3, #6–#8, #18, #19
- §3 Invariants, §5 Grain and keys → #2, #3, #12, #13
- §6 Ordering, §7 Commit boundaries, §10 Retry, §11 Partial failure → #1, #2, #15; order steps 4–6
- §9 Concurrency → #6–#8 (setup now takes the ENR_15P lock; the 90-minute stale bound is safe)
- §14 Rollout, §15 Rollback → order step 2 and the D-06 ledger row
- §16.1 Alternatives → why the DROP is not in the cell and why there is no move branch
- §16.2 → #1, #2 code; §16.3 → #3–#5; §16.4 → #6–#8; §16.5 → #11–#17; §16.6 → #18, #19
- §17 Runbook → order steps 3–6; §18 Verification → the acceptance mapping

# Architecture — 20261021-move-poi-nodes-enr-15p-cleanup

Inputs: `decision.md` D-01 to D-05, `evidence/results/ctrl-inventory.txt` (INV-1 to INV-8), `model-design.md`. There is no `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md` (D-05). Grain and keys come from `model-design.md` `## Entities and grain` and `## Keys`. This document does not change them.

## 1. Scope

On DEV, the ctrl move is already done: all 9 node edges are on `PL_VV_TRANS_SLV_TO_ENR_15P`, and no row belongs to `PL_VV_TRANS_SLV_TO_SLV_1H` (D-02). This task therefore does three things:

1. **Align the repo with DEV.** Every repo writer of these 9 edges, and of the flow lock that guards them, must target `PL_VV_TRANS_SLV_TO_ENR_15P`:
   - `NB_SETUP_INITIAL_DDL` cell `init_seed_ctrl`;
   - `NB_SETUP_POI_ENTITY` cell `a1setupedges`;
   - `NB_SETUP_POI_AMENITY` cells `c1setupplan` and `c1setupedges`.

   If these writers keep the old name, the next setup run fails at the `owners` check. Worse, `ensure_lock_row` recreates `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` after cleanup. The seed MERGE key includes `pl_name`, so a fresh-environment seed would also insert 9 duplicate `SLV_1H` edges.
2. **Delete ctrl rows on DEV.** A new last cell `mvpoipy` in `NB_CREATE_DDL` does this under the `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` lock:
   - 8 `ctrl_mng_pipeline_config` rows;
   - 6 `ctrl_mng_watermark` rows (D-03).
3. **Remove the dead objects.**
   - The user-run runbook backs up and DROPs `lh_vv_gold.enr.gld_enr_poi_coordinate` and `lh_vv_silver.dbo.slv_pn_poi` (D-04).
   - The repo deletes `NB_SLV_PN_POI.ipynb` and `NB_ENR_POI_COORDINATE.ipynb`, the coordinate DDL spec in `init_tables`, the 8 seed rows, and the test references.
   - `CTRL_TABLES_CONTEXT.md` and `01_DATA_MODEL.md` are updated.

Resolved model-design questions:
- **Q7:** the lib maps a null `nb_name` to `NB_<UPPER(trg_tbl)>` (`NB_LIB_TRANSFORM_SLV_GLD` `build_dag`). The two nodes therefore resolve to `NB_SLV_POI_ENTITY_NON_ENRICH` and `NB_SLV_POI_AMENITY`. No change is needed.
- **Q1:** the repo registry has no rows for the removed tables. DEV is unprobed, so `mvpoipy` stops if `ctrl_cfg_schema_registry` has any row that touches them (fail closed, no assumption).
- **Q4:** `slv_pn_poi` has no repo DDL; the lib creates it on first MERGE. The runbook captures `SHOW CREATE TABLE` before the DROP.

## 2. Non-goals

- No change to build logic in `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_SLV_POI_AMENITY`, `NB_ENR_POI_INFO`, or `NB_ENR_POI_REVIEW`.
- No change to pipeline JSON (`test_pipeline_timeouts` stays green).
- No DROP of `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, or `slv_poi_entity`.
- `ctrl_log_run` and `ctrl_log_table_run` are not touched.
- No rewrite of historical `NB_CREATE_DDL` cells (`enrddlpy`, `entwebpy`, `enrinfopy` stay byte-identical).
- No generic `SLV_1H` → `ENR_15P` move logic. DEV is already moved (D-02), so `mvpoipy` stops if any `SLV_1H` row exists.
- `docs/requirements/20261012-map-gld-enr-poi-tables/*` are historical requirement documents and stay as they are.
- `gld_enr_poi_review` edges, the FL_00 extract edges, and `ctrl_cdc_*` are not touched.
- Staging and production are out of scope.

## 3. Invariants

- **INV-A.** Each node has active edges in exactly one pipeline. After the change, `slv_poi_entity_non_enrich` and `slv_poi_amenity` have exactly the 9 active `RECOMPUTE` edges listed in INV-2, all on `PL_VV_TRANS_SLV_TO_ENR_15P`, each exactly once.
- **INV-B.** No `ctrl_mng_pipeline_config` row has `pl_name = 'PL_VV_TRANS_SLV_TO_SLV_1H'`, and no row has `src_tbl` or `trg_tbl` in (`slv_pn_poi`, `gld_enr_poi_coordinate`). This holds on DEV and in the seed.
- **INV-C.** The active `gld_enr_poi_info` edges on ENR_15P are exactly the 7 in `INFO_ACTIVE`, each once. The three old info edges (`slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` → info) no longer exist. The cell deletes an old info edge only if it is inactive.
- **INV-D.** The 6 watermark ids in D-03 are gone. The 7 info watermarks, the 9 node watermarks, and `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` are kept unchanged (17 rows).
- **INV-E.** DAG order inside ENR_15P comes from the edges, not from priority: `slv_poi_entity_non_enrich` → `slv_poi_amenity` (edge `slv_poi_entity_non_enrich` → `slv_poi_amenity`), and both → `gld_enr_poi_info`.
- **INV-F.** `mvpoipy` checks everything before its first write. Re-running it changes nothing, and it never inserts, re-enables, or moves an edge.
- **INV-G.** No DROP runs until `mvpoipy` reports SUCCESS and the pre-DROP gate query returns 0. Each table is backed up and its row count checked before it is dropped.
- **INV-H.** `gld_enr_poi_info` and `gld_enr_poi_review` still exist after the DROP.
- **INV-I.** The seed `PIPELINE_CONFIG_ROWS` has 49 rows, and `TABLE_SPECS` has 13 entries.

## 4. State ownership

| State | Owner (writer) | This task |
|---|---|---|
| `ctrl_mng_pipeline_config` rows on ENR_15P | Setup notebooks (`NB_SETUP_POI_*`) for node edges; NB_CREATE_DDL patch cells; `NB_SETUP_INITIAL_DDL` for an empty environment | `mvpoipy` deletes 8 rows. The setup notebooks become ENR_15P writers. |
| `ctrl_mng_watermark` `wm_e__*` | `NB_00` (the only runtime writer) | `mvpoipy` deletes 5 rows under the ENR_15P flow lock, so NB_00 cannot write concurrently. |
| `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` (lock) | NB_00 `acquire_flow_lock`, the setup notebooks, and the patch cells | Held by `mvpoipy` and, after the change, by both setup notebooks. Never deleted. |
| `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` | Formerly setup and `entwebpy` | Deleted. No repo writer remains except the historical `entwebpy` (see §11). |
| `gld_enr_poi_coordinate`, `slv_pn_poi` data | Formerly `NB_ENR_POI_COORDINATE`, `NB_SLV_PN_POI` | Backed up, then dropped by the user runbook. |
| Backups `lh_vv_silver.dbo.*_bak_20261021` | User runbook | Created by this task. Dropping them later is the user's call (follow-up). |

## 5. Grain and keys

- **Kept tables.** Grain and keys are unchanged; see `model-design.md` `## Entities and grain` and `## Keys`. N6 `slv_poi_entity_non_enrich` is keyed on `poi_id`. N7 `slv_poi_amenity` is keyed on (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`).
- **Removed tables.** Their documented grain lives only in `model-design.md` and in the runbook's `SHOW CREATE TABLE` capture. Model-design question 3 (the two partner `poi_id` formulas) is closed by removing both tables. Any reader outside ctrl is covered by the backup (§15).
- **Ctrl logical keys used by the patch:**
  - pipeline_config: (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`), the same as `SEED_KEYS["pipeline_config"]`;
  - watermark: `watermark_id`;
  - node identity: `trg_schema.trg_tbl`.
- **DELETE predicate.** The full 5-column key; the cell never deletes by a single column.

## 6. Ordering

Repo order does not matter for correctness. The runtime order does:

1. Pause the ENR_15P schedule trigger, then wait until `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P.lock_exec_id IS NULL`. This step comes first because syncing the workspace deletes the `NB_SLV_PN_POI` item while its 2 edges are still active. A scheduled run in that gap would fail its runMultiple.
2. Sync the Fabric workspace from git.
3. Run only cell `mvpoipy`. Inside the cell, the `pipeline_config` DELETE commits before the `watermark` DELETE. If the cell stops between them, the only leftover is an orphan watermark, which nothing reads. The reverse order would leave active edges without a watermark, which NB_00 treats as New Edge and rebuilds needlessly.
4. Re-run `mvpoipy` as the idempotency proof.
5. Run NB_00 with `p_mode=PLAN`. It does no writes and proves INV-E.
6. Backup → count check → DROP.
7. Forced RUN of the two silver nodes.
8. Resume the schedule and observe one scheduled run.

## 7. Transaction and commit boundaries

Delta has no multi-table transaction, so the plan uses these commits:

| # | Commit | Table | Atomic unit |
|---|---|---|---|
| C0 | Lock-row MERGE (insert only if missing) | watermark | 1 row |
| C1 | Lock acquire UPDATE | watermark | lock row |
| C2 | `DELETE` 8 edges | pipeline_config | 1 Delta commit |
| C3 | `DELETE` 6 watermark ids (`lock_exec_id IS NULL`) | watermark | 1 Delta commit |
| C4 | Lock release UPDATE (status SUCCESS/FAILED) | watermark | lock row |
| C5, C6 | CTAS backups | silver | 1 per table |
| C7, C8 | `DROP TABLE IF EXISTS` | gold enr, silver | 1 per table |

C2 and C3 run under the lock taken in C1, and all checks run before C2. C5 to C8 run outside any lock. That is safe because after C2 no ctrl edge references the two tables, so no NB_00 node reads or writes them.

## 8. Idempotency

- **`mvpoipy`.** On a re-run, the pre-checks find 0 rows to delete and both DELETEs match nothing. The post-checks still pass, and the only side effect is the lock row's status and `updated_at`, the same as `enrinfopy`.
- **Seed and setup.** `NB_SETUP_INITIAL_DDL` with the new seed on DEV finds all 49 keys present (`to_insert=0`), because DEV already has the ENR_15P node rows. `NB_SETUP_POI_ENTITY` and `NB_SETUP_POI_AMENITY` with `p_apply=true` MERGE onto the existing ENR_15P rows. Because the stored values already match (priority 1, `RECOMPUTE`, `nb_name` NULL), no UPDATE branch fires and no INSERT fires, so the runs print `edges_inserted=0 edges_retired=0`.
- **Runbook.** The backup CTAS fails if the backup already exists; the runbook checks for that before the step and skips it if the count matches. The DROPs use `IF EXISTS`.

## 9. Concurrency

- **NB_00 ENR_15P.** It is excluded by the shared flow lock: `mvpoipy` uses a 35-minute lease, equal to `p_lock_timeout_min`. The schedule pause removes the race during workspace sync.
- **Setup notebooks.** They now take the ENR_15P lock, with `LOCK_TIMEOUT_DEFAULT_MIN = 90` as their staleness bound. This is stricter than NB_00's 35-minute bound, so a setup run never steals a live NB_00 lock. The trade-off is that a setup run can no longer overlap a 15-minute run. That is correct, because the setup writes edges of nodes in this DAG.
- **FL_00 extract.** It writes its own `wm_transform_*` rows to `ctrl_mng_watermark` without our lock. A Delta concurrent-modification conflict on C3 is possible. The cell then fails, C2 is already committed, and re-running the cell is the recovery (§10). No retry loop is added; this follows the `enrinfopy` precedent.
- **No other writers.** No other writer touches `ctrl_mng_pipeline_config`.

## 10. Retry and recovery

| Failure | State left | Recovery |
|---|---|---|
| Lock busy | Nothing written | Re-run after the in-flight run ends. |
| Pre-check `RuntimeError("Dừng trước khi ghi: …")` | Nothing written | Read the issue list. A stray, active, or extra row, or a registry row, is a **user decision**; do not edit around it. |
| C3 conflict or failure after C2 | 8 edges gone, 6 watermarks remain (inert) | Re-run `mvpoipy`. |
| Post-check `RuntimeError("Sau khi ghi: …")` | Writes done, verification mismatch | Stop and paste the output. Do not DROP. |
| C4 fails (lock not released) | Lock held, at most 35 minutes | Wait for lease expiry; NB_00 and the cell reclaim the lock automatically. |
| CTAS fails | No backup, tables intact | Fix and repeat. Do not DROP. |
| One DROP done, the other not | Mixed | Repeat the DROP step; `IF EXISTS` makes it idempotent. |

## 11. Partial failure and hazards outside the cell

- **`enrddlpy` (13/10) re-run.** It would re-insert all 13 of its edges as active, including the 8 deleted ones, and recreate `gld_enr_poi_coordinate`.
- **`entwebpy` (20/10) re-run.** It would recreate the `SLV_1H` contact edge and `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`. NB_00 `build_dag` would then fail closed with "node … thuộc nhiều pl đang active". That is not silent corruption.
- **Treatment.** Both hazards are mitigated, not removed, because history cells cannot be edited. The new `mvpoimd` note and the `mvpoipy` header say not to re-run them, and re-running `mvpoipy` detects either state: an `SLV_1H` row or a stray row stops the cell. The recovery for both cases is a manual DELETE of the recreated rows, then re-running `mvpoipy`.
- **External readers.** If a report or PG sync reads a dropped table, the forward fix is to point it at `gld_enr_poi_info`. The backup (§15) is the fallback.

## 12. Observability

- **`mvpoipy` output.**
  - SUCCESS prints `đã xoá cạnh=<n> watermark=<n>; …`; the expected first-run values are 8 and 6.
  - On the re-run, the same line prints 0 and 0.
  - On failure, the issue list is raised in the exception, and the lock row ends with `status = FAILED` and `error_message`.
- **NB_00 PLAN.** The output shows the plan and `run_multiple_dag` with dependencies.
- **Forced RUN.** `ctrl_log_run` and `ctrl_log_table_run` rows for the exec_id show node start and end order.
- **Probe re-run.** Re-running `evidence/probes/ctrl-inventory.sql` should show INV-1 = 16, INV-3 = 17, an INV-5 and INV-6 error "table not found", and INV-7 = 58 and INV-8 = 65 (or later counts).
- **Evidence files.** Each runtime output is pasted into `evidence/results/runtime-<step>.txt`.

## 13. Security

- All SQL in `mvpoipy` is built from literal constants in the cell; there is no user input, so there is no injection surface.
- No secrets, and no workspace or lakehouse IDs are changed.
- DEV only: the constants match DEV evidence, so in any other environment the pre-checks stop the cell before it writes.
- The user runs the DROP and the backup with their own DEV permissions. The agent does not run Fabric.

## 14. Rollout

1. **Repo.** Make all edits in one change set (§16). Run local tests, then specialist review and the risk gate.
2. **User decision.** The user confirms that the ENR_15P schedule can be paused on DEV for about 30 minutes. If not, use the fallback: split into two repo changes. Change 1 holds everything except the two notebook deletions and their test assertions. After `mvpoipy` succeeds, change 2 deletes the notebooks.
3. **Runtime.** Follow §17 R0 to R8. Main copies §17 into the task `runtime-runbook.md` during the runtime phase, because that file is not in `scope.files`.

## 15. Rollback and forward recovery

**Forward recovery is preferred.** Every failure in §10 is fixed by re-running a step.

**Rollback window.** The window is the Delta time-travel retention of the ctrl tables (`VACUUM` default 7 days) plus the backup tables. Roll back in this order:

1. Pause the ENR_15P schedule.
2. `git revert` the change set and sync the workspace. This restores `NB_SLV_PN_POI` and `NB_ENR_POI_COORDINATE` before their edges come back.
3. Recreate the tables:
   - run the `SHOW CREATE TABLE` text captured in R0;
   - `INSERT INTO <table> SELECT * FROM lh_vv_silver.dbo.<table>_bak_20261021`;
   - or, for `slv_pn_poi` only, let NB_00 rebuild it once its edges are restored (RECOMPUTE, New Edge).
4. Restore the ctrl rows from the versions recorded in R0. Do not use `RESTORE`, which would also revert later NB_00 watermark writes.

```sql
INSERT INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
SELECT * FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config VERSION AS OF <V_cfg>
WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND src_schema = 'lh_vv_silver.dbo' AND (
  (trg_tbl = 'slv_pn_poi' AND src_tbl IN ('slv_pn_business_services', 'slv_pn_business_service_i18ns'))
  OR (trg_tbl = 'gld_enr_poi_coordinate' AND src_tbl IN ('slv_3p_poi', 'slv_3p_poi_address', 'slv_pn_poi'))
  OR (trg_tbl = 'gld_enr_poi_info' AND src_tbl IN ('slv_3p_poi', 'slv_3p_poi_address', 'slv_3p_poi_contact')));
INSERT INTO lh_vv_ctrl.dbo.ctrl_mng_watermark
SELECT * FROM lh_vv_ctrl.dbo.ctrl_mng_watermark VERSION AS OF <V_wm>
WHERE watermark_id IN (
  'wm_e__gld_enr_poi_coordinate__slv_3p_poi', 'wm_e__gld_enr_poi_coordinate__slv_3p_poi_address',
  'wm_e__gld_enr_poi_coordinate__slv_pn_poi', 'wm_e__slv_pn_poi__slv_pn_business_service_i18ns',
  'wm_e__slv_pn_poi__slv_pn_business_services');
```

Leave `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H` deleted, because no pipeline uses it. After the restore, run NB_00 PLAN, then resume the schedule. After the 7-day window, the ctrl rows can be re-seeded from the INV-2 values; the edge watermarks are then lost and those edges rebuild as New Edge.

**Why not time travel for the tables.** The request planned a Delta time-travel rollback. `DROP TABLE` on a Fabric managed table removes its folder, so time travel is not available after the DROP. This design uses a CTAS backup instead. Main should record this as a new ledger row.

## 16. Implementation plan

### 16.1 Alternatives

| Choice | Selected | Rejected | Why |
|---|---|---|---|
| Where to DROP | User runbook after `mvpoipy`, with backup | DROP inside `mvpoipy` | `NB_CREATE_DDL` has had no DROP cell since 08/10, and resets live in runbooks (D-18 precedent). The backup and a human stop must come before the irreversible step. Ordering is still guaranteed by the gate query. |
| How to clean ctrl | `DELETE` by full key, after checking everything first | `is_active = 0` | The request requires row deletion. |
| How to move the edges | Assert on ENR_15P; stop on any `SLV_1H` row | Generic move (`UPDATE pl_name`, dedupe) | DEV is already moved (D-02). A move branch could not be proven on DEV and would act on rows never probed. |
| How to avoid the sync race | Pause the schedule | Two-step repo rollout | One change set and fewer moving parts. The two-step rollout is the fallback if the user cannot pause. |
| How to back up | CTAS into `lh_vv_silver.dbo.<table>_bak_20261021` | Time travel; SHALLOW CLONE | DROP removes the files, and a shallow clone points at those same files. Silver keeps the gold `enr` schema free of extra tables that a downstream reader might pick up. This follows the `ctrl_cfg_schema_registry_bak_20261001` precedent. |
| Retrying C3 | Fail, then re-run the cell | In-cell retry loop | `enrinfopy` precedent; the C2-then-C3 order makes the re-run safe. |

### 16.2 Patch cells `mvpoimd` and `mvpoipy` (append at the end of `NB_CREATE_DDL.ipynb`)

`mvpoimd` is a markdown cell with `metadata: {}`. Its source is one line:

`# [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup`

`mvpoipy` is a code cell with metadata `{"microsoft": {"language": "python", "language_group": "synapse_pyspark"}}`, `execution_count: null`, and `outputs: []`. Its exact source:

```python
# [THÊM 21/10] 20261021-move-poi-nodes-enr-15p-cleanup
# 1. Kiểm tra 9 cạnh vào slv_poi_entity_non_enrich / slv_poi_amenity đã ở PL_VV_TRANS_SLV_TO_ENR_15P, active đúng một dòng.
#    Cell không chuyển cạnh, không bật cạnh. Còn dòng PL_VV_TRANS_SLV_TO_SLV_1H thì dừng.
# 2. Xoá dòng (không chỉ tắt) 8 cạnh: 2 cạnh -> slv_pn_poi, 3 cạnh -> gld_enr_poi_coordinate, 3 cạnh info cũ đã tắt.
# 3. Xoá 5 watermark cạnh của các cạnh đó và khoá wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H.
# Không DROP bảng: DROP gld_enr_poi_coordinate, slv_pn_poi theo runtime-runbook.md của task, sau khi cell SUCCESS.
# Kiểm tra hết trước khi ghi. Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P suốt cell. Chạy lại: không đổi gì.
# Sau cell này không chạy lại enrddlpy, entwebpy: hai cell đó tạo lại cạnh đã xoá.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
REG = "lh_vv_ctrl.dbo.ctrl_cfg_schema_registry"
PL = "PL_VV_TRANS_SLV_TO_ENR_15P"
OLD_PL = "PL_VV_TRANS_SLV_TO_SLV_1H"
WID = f"wm_flow__{PL}"
SLV = "lh_vv_silver.dbo"
LEASE_MINUTES = 35  # bằng p_lock_timeout_min của NB_00_ORCHES_SLV_TO_ENR_15P
REMOVED = ("slv_pn_poi", "gld_enr_poi_coordinate")
EDGES_DELETE = [
    ("slv_pn_business_services", "lh_vv_silver.dbo", "slv_pn_poi"),
    ("slv_pn_business_service_i18ns", "lh_vv_silver.dbo", "slv_pn_poi"),
    ("slv_3p_poi", "lh_vv_gold.enr", "gld_enr_poi_coordinate"),
    ("slv_3p_poi_address", "lh_vv_gold.enr", "gld_enr_poi_coordinate"),
    ("slv_pn_poi", "lh_vv_gold.enr", "gld_enr_poi_coordinate"),
    ("slv_3p_poi", "lh_vv_gold.enr", "gld_enr_poi_info"),
    ("slv_3p_poi_address", "lh_vv_gold.enr", "gld_enr_poi_info"),
    ("slv_3p_poi_contact", "lh_vv_gold.enr", "gld_enr_poi_info"),
]
WM_DELETE = (
    "wm_e__gld_enr_poi_coordinate__slv_3p_poi",
    "wm_e__gld_enr_poi_coordinate__slv_3p_poi_address",
    "wm_e__gld_enr_poi_coordinate__slv_pn_poi",
    "wm_e__slv_pn_poi__slv_pn_business_service_i18ns",
    "wm_e__slv_pn_poi__slv_pn_business_services",
    "wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H",
)
OLD_INFO_WM = (
    "wm_e__gld_enr_poi_info__slv_3p_poi",
    "wm_e__gld_enr_poi_info__slv_3p_poi_address",
    "wm_e__gld_enr_poi_info__slv_3p_poi_contact",
)
NODE_EDGES = [
    ("slv_3p_poi", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_address", "slv_poi_entity_non_enrich"),
    ("ref_dictionary_place_type", "slv_poi_entity_non_enrich"),
    ("slv_pn_business_services", "slv_poi_entity_non_enrich"),
    ("slv_pn_business_service_i18ns", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_contact", "slv_poi_entity_non_enrich"),
    ("slv_3p_poi_amenity", "slv_poi_amenity"),
    ("slv_poi_entity_non_enrich", "slv_poi_amenity"),
    ("ref_dictionary_amenities", "slv_poi_amenity"),
]
INFO_ACTIVE = (
    "slv_poi_entity_non_enrich", "slv_poi_amenity", "slv_3p_poi_rating", "slv_3p_poi_price",
    "slv_3p_poi_opening_hours", "slv_3p_poi_review", "slv_pn_business_service_i18ns",
)
KEPT_WM_TRG = ("gld_enr_poi_info", "slv_poi_entity_non_enrich", "slv_poi_amenity")
LOCK = "mvpoi-" + uuid.uuid4().hex


def _names(items):
    return ", ".join(f"'{item}'" for item in items)


def _n(sql):
    return int(spark.sql(sql).first()["n"])


def _node_edges():
    keys = " OR ".join(f"(src_tbl = '{src}' AND trg_tbl = '{trg}')" for src, trg in NODE_EDGES)
    rows = spark.sql(f"""
    SELECT src_tbl, trg_tbl, count(*) AS n FROM {CFG}
    WHERE pl_name = '{PL}' AND src_schema = '{SLV}' AND trg_schema = '{SLV}' AND is_active = 1
      AND upper(trim(load_mode)) = 'RECOMPUTE' AND ({keys})
    GROUP BY src_tbl, trg_tbl
    """).collect()
    return {(row["src_tbl"], row["trg_tbl"]): row["n"] for row in rows}


def _info_edges():
    rows = spark.sql(f"""
    SELECT src_tbl, count(*) AS n FROM {CFG}
    WHERE pl_name = '{PL}' AND trg_schema = 'lh_vv_gold.enr' AND trg_tbl = 'gld_enr_poi_info' AND is_active = 1
    GROUP BY src_tbl
    """).collect()
    return {row["src_tbl"]: row["n"] for row in rows}


EDGE_KEYS = " OR ".join(
    f"(src_tbl = '{src}' AND trg_schema = '{schema}' AND trg_tbl = '{trg}')" for src, schema, trg in EDGES_DELETE
)
IN_DELETE = f"pl_name = '{PL}' AND src_schema = '{SLV}' AND ({EDGE_KEYS})"
TOUCHES = f"(src_tbl IN ({_names(REMOVED)}) OR trg_tbl IN ({_names(REMOVED)}))"
KEPT_WM_SQL = f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{WID}' OR trg_tbl IN ({_names(KEPT_WM_TRG)})"
WANT_NODES = {key: 1 for key in NODE_EDGES}
WANT_INFO = {src: 1 for src in INFO_ACTIVE}

# Tạo dòng khoá nếu chưa có. Không xoá wm_flow__ của luồng này.
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
        raise RuntimeError(f"{CFG} chưa có cột nb_name: môi trường chưa qua enrddlpy, cell này không áp dụng")

    issues = []
    old_rows = _n(f"SELECT count(*) AS n FROM {CFG} WHERE pl_name = '{OLD_PL}'")
    if old_rows:
        issues.append(f"còn {old_rows} dòng {OLD_PL}: cell không chuyển cạnh, xử lý theo runbook")
    for row in spark.sql(f"""
    SELECT src_tbl, trg_tbl, count(*) AS n, sum(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) AS active_n
    FROM {CFG} WHERE {IN_DELETE}
    GROUP BY src_tbl, trg_schema, trg_tbl
    """).collect():
        if row["n"] > 1:
            issues.append(f"cạnh {row['src_tbl']} -> {row['trg_tbl']} có {row['n']} dòng")
        if row["trg_tbl"] == "gld_enr_poi_info" and row["active_n"]:
            issues.append(f"cạnh info cũ {row['src_tbl']} đang active: cell chỉ xoá cạnh đã tắt")
    stray = spark.sql(f"SELECT pl_name, src_tbl, trg_tbl FROM {CFG} WHERE {TOUCHES} AND NOT ({IN_DELETE})").collect()
    if stray:
        issues.append(f"dòng ngoài danh sách xoá chạm bảng bỏ: {[tuple(row) for row in stray]}")
    got_nodes = _node_edges()
    if got_nodes != WANT_NODES:
        issues.append(f"cạnh node trên {PL} là {got_nodes}, cần {WANT_NODES}")
    owners = [row["pl_name"] for row in spark.sql(f"""
    SELECT DISTINCT pl_name FROM {CFG}
    WHERE trg_schema = '{SLV}' AND trg_tbl IN ('slv_poi_entity_non_enrich', 'slv_poi_amenity')
      AND is_active = 1 AND pl_name <> '{PL}'
    """).collect()]
    if owners:
        issues.append(f"node entity / amenity còn active ở pl khác: {owners}")
    locked = _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id IN ({_names(WM_DELETE)}) AND lock_exec_id IS NOT NULL")
    if locked:
        issues.append(f"{locked} dòng watermark cần xoá đang có lock_exec_id")
    wm_stray = spark.sql(f"""
    SELECT watermark_id FROM {WM}
    WHERE ({TOUCHES} OR src_tbl = '{OLD_PL}' OR watermark_id IN ({_names(OLD_INFO_WM)}))
      AND watermark_id NOT IN ({_names(WM_DELETE)})
    """).collect()
    if wm_stray:
        issues.append(f"watermark ngoài danh sách xoá: {[row['watermark_id'] for row in wm_stray]}")
    registry = _n(f"SELECT count(*) AS n FROM {REG} WHERE {TOUCHES}")
    if registry:
        issues.append(f"{REG} còn {registry} dòng chạm bảng bỏ: hỏi người dùng trước khi xoá")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    cfg_n = _n(f"SELECT count(*) AS n FROM {CFG} WHERE {IN_DELETE}")
    wm_n = _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id IN ({_names(WM_DELETE)})")
    kept_before = _n(KEPT_WM_SQL)
    # Cạnh trước, watermark sau: dừng giữa chừng chỉ để lại watermark mồ côi, chạy lại cell là xong.
    spark.sql(f"DELETE FROM {CFG} WHERE {IN_DELETE} AND NOT (trg_tbl = 'gld_enr_poi_info' AND is_active <=> 1)")
    spark.sql(f"DELETE FROM {WM} WHERE watermark_id IN ({_names(WM_DELETE)}) AND lock_exec_id IS NULL")

    problems = []
    left_cfg = _n(f"SELECT count(*) AS n FROM {CFG} WHERE pl_name = '{OLD_PL}' OR {TOUCHES} OR ({IN_DELETE})")
    if left_cfg:
        problems.append(f"{CFG} còn {left_cfg} dòng cần xoá")
    left_wm = _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id IN ({_names(WM_DELETE)})")
    if left_wm:
        problems.append(f"{WM} còn {left_wm} dòng cần xoá")
    kept_after = _n(KEPT_WM_SQL)
    if kept_after != kept_before:
        problems.append(f"watermark giữ lại đổi từ {kept_before} thành {kept_after}")
    if _node_edges() != WANT_NODES:
        problems.append(f"cạnh node trên {PL} là {_node_edges()}, cần {WANT_NODES}")
    if _info_edges() != WANT_INFO:
        problems.append(f"cạnh active của info là {_info_edges()}, cần {WANT_INFO}")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"đã xoá cạnh={cfg_n} watermark={wm_n}; watermark giữ lại={kept_after}; "
          f"9 cạnh node trên {PL}; info active {sorted(WANT_INFO)}")
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

### 16.3 `NB_SETUP_INITIAL_DDL` cell `init_seed_ctrl` (new `PIPELINE_CONFIG_ROWS` head and tail)

- Replace the constants line with:
  `_FL00, _ENR = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_15P"`
- Replace the `# [SỬA 21/10] 20261021-refresh-gld-enr-poi-info: …` comment line with:
  `# [SỬA 21/10] 20261021-move-poi-nodes-enr-15p-cleanup: bỏ 8 cạnh (slv_pn_poi, gld_enr_poi_coordinate, 3 cạnh info cũ); 9 cạnh node silver thuộc _ENR.`
- Keep the 32 `_FL00` rows unchanged.

The `_ENR` and node block becomes exactly:

```python
    (_ENR, _S, 'slv_3p_poi_review', _E, 'gld_enr_poi_review', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_REVIEW'),
    (_ENR, _S, 'slv_3p_poi_rating', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),
    (_ENR, _S, 'slv_3p_poi_price', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),
    (_ENR, _S, 'slv_3p_poi_opening_hours', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),
    (_ENR, _S, 'slv_3p_poi_review', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),
    (_ENR, _S, 'slv_poi_entity_non_enrich', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),
    (_ENR, _S, 'slv_poi_amenity', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),
    (_ENR, _S, 'slv_pn_business_service_i18ns', _E, 'gld_enr_poi_info', 1, 1, 'APPEND', None, None, 'NB_ENR_POI_INFO'),
    (_ENR, _S, 'slv_3p_poi', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'slv_3p_poi_address', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'ref_dictionary_place_type', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'slv_pn_business_services', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'slv_pn_business_service_i18ns', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'slv_3p_poi_contact', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'slv_3p_poi_amenity', _S, 'slv_poi_amenity', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'slv_poi_entity_non_enrich', _S, 'slv_poi_amenity', 1, 1, 'RECOMPUTE', None, None, None),
    (_ENR, _S, 'ref_dictionary_amenities', _S, 'slv_poi_amenity', 1, 1, 'RECOMPUTE', None, None, None),
]
```

The 49 rows are the 32 FL_00 rows, 8 ENR gold edges, and 9 node edges. `WATERMARK_ROWS` is unchanged.

Two more edits in this notebook:
- **`init_tables`:** delete the whole `{"fq": 'lh_vv_gold.enr.gld_enr_poi_coordinate', …}` dict (11 cols).
- **`init_plan`:** change `len(fqs) != 14` and `TABLE_SPECS cần 14 fq` to 13.

### 16.4 Setup notebooks

In `NB_SETUP_POI_ENTITY` `a1setupedges` and `NB_SETUP_POI_AMENITY` `c1setupedges`:
- Replace every `PL_VV_TRANS_SLV_TO_SLV_1H` with `PL_VV_TRANS_SLV_TO_ENR_15P`. This covers `flow` in the precheck, the `dup`, `owners`, `missing`, and `retired` SQL, the MERGE `ON` and INSERT, `PL =`, and the amenity `entity_edges_ok`.
- In the precheck docstring, change `pl SLV_1H` to `pl ENR_15P`.
- The `# BEGIN_EDGE_PRECHECK`…`# END_EDGE_PRECHECK` blocks must stay byte-identical between the two notebooks.
- Keep the RETIRE rows. They are harmless no-ops and are still asserted by the tests.

In `NB_SETUP_POI_AMENITY` `c1setupplan`, make the same replacement in the `entity_edges_ok` query.

When done, no notebook contains `SLV_TO_SLV_1H` except the historical `entwebpy` cell.

### 16.5 Tests

- **`tests/test_initial_ddl_contract.py`**
  - `test_table_inventory_matches_sources`: the set becomes `{info, review}`, and `len(specs) == 13`.
  - `test_columns_match_sources`: drop the coordinate entry from the `COORD_COLS`/`REVIEW_COLS` map.
  - `test_pipeline_config_rows_match_sources`: skip each `(src, target)` that is in `{(s, t) for s, _sc, t in _assign(_cell(ddl, "mvpoipy"), "EDGES_DELETE")}`. The 9 node rows use `"PL_VV_TRANS_SLV_TO_ENR_15P"`, and `len(expected) == 49`.
  - `test_dropped_l1_columns_unread`: drop `NB_ENR_POI_COORDINATE.ipynb` from the list.
  - `test_enr_initial_edge_state`: add four assertions:
    - no `pl_name == "PL_VV_TRANS_SLV_TO_SLV_1H"`;
    - no `src_tbl` or `trg_tbl` in the removed tables, and no old info `(src, "gld_enr_poi_info")`;
    - every active `(trg_schema, trg_tbl)` has exactly one `pl_name`, and the two nodes map to `{ENR_15P}`;
    - no spec `fq` for coordinate, and `"_SLV1H" not in init_seed_ctrl`.

    Replace the coordinate count assertion (`== 3`) with `== 0`.
  - New `test_enr_15p_dag_order`: on the seed, assert the active `_ENR` edges `slv_poi_entity_non_enrich` → `slv_poi_amenity`, `slv_poi_entity_non_enrich` → `gld_enr_poi_info`, and `slv_poi_amenity` → `gld_enr_poi_info`.
- **`tests/test_enr_poi_contract.py`**
  - `test_mapping_comments_and_edges`: remove the `coord = _nb("NB_ENR_POI_COORDINATE.ipynb")` read and the `COL-011..021` loop. Keep the `enrddlpy` historical assertions.
  - `test_info_patch_cell_guards`: replace the `ids[-1]` and `ids[-2]` checks with `ids[-4:] == ["enrinfomd", "enrinfopy", "mvpoimd", "mvpoipy"]`.
  - New `test_cleanup_patch_constants`:
    - `EDGES_DELETE`, `WM_DELETE`, `NODE_EDGES`, and `INFO_ACTIVE` equal module literals that copy D-03 and INV-2;
    - `set(EDGES_OFF) <= {(s, t) for s, _sc, t in EDGES_DELETE}`;
    - the `wm_e__` ids equal `{f"wm_e__{t}__{s}"}` for the non-info deletions;
    - `"wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H" in WM_DELETE`;
    - no seed row key is in `EDGES_DELETE`.
  - New `test_cleanup_patch_guards`:
    - `patch.count("DELETE FROM") == 2`;
    - none of `DROP`, `TRUNCATE`, `ALTER TABLE`, `INSERT INTO`, `SET is_active`, `RESTORE`, or `UPDATE {CFG}` appears in the cell;
    - these tokens appear in increasing order: `held = True`, `Dừng trước khi ghi`, `DELETE FROM {CFG}`, `DELETE FROM {WM}`, `Sau khi ghi`, `finally:`;
    - `"AND NOT (trg_tbl = 'gld_enr_poi_info' AND is_active <=> 1)"` and `"AND lock_exec_id IS NULL\")"` appear in the DELETE lines;
    - `"lock_exec_id = '{LOCK}'"` appears in the release;
    - `LEASE_MINUTES = 35`.
  - New `test_removed_notebooks_absent`: neither notebook file exists, and no `notebooks/*.ipynb` other than `NB_CREATE_DDL.ipynb` matches `\bslv_pn_poi\b` or `gld_enr_poi_coordinate`.
- **`tests/test_poi_entity_contract.py`**
  - `test_setup_contract`: both pipeline-name assertions use `PL_VV_TRANS_SLV_TO_ENR_15P`, plus `"PL_VV_TRANS_SLV_TO_SLV_1H" not in src`.
  - `_edge`: the default `pl_name` becomes `"PL_VV_TRANS_SLV_TO_ENR_15P"`.
  - `test_create_ddl_patch`: `ids[-4:] == ["enrinfomd", "enrinfopy", "mvpoimd", "mvpoipy"]`.
- **`tests/test_poi_amenity_contract.py`**
  - `test_setup_contract`: `"PL_VV_TRANS_SLV_TO_ENR_15P" in src` and `"PL_VV_TRANS_SLV_TO_SLV_1H" not in src`.

### 16.6 Docs

- **`docs/context/CTRL_TABLES_CONTEXT.md` §3 `### Dữ liệu hiện có`, L114–133.**
  - Replace the `PL_VV_TRANS_SLV_TO_SLV_1H` block with a `**PL_VV_TRANS_SLV_TO_ENR_15P** (NB_00_ORCHES_SLV_TO_ENR_15P)` block that has three tables:
    - the 6 entity edges (`RECOMPUTE`, `nb_name` NULL → `NB_SLV_POI_ENTITY_NON_ENRICH`);
    - the 3 amenity edges (→ `NB_SLV_POI_AMENITY`);
    - the gold edges: review ← `slv_3p_poi_review`, and info ← the 7 `INFO_ACTIVE` (`APPEND`).
  - Add one sentence on order: entity → amenity → info by edges.
  - Restate the setup notes: `NB_SETUP_POI_ENTITY` / `NB_SETUP_POI_AMENITY` write on ENR_15P and take the `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` lock.
  - Add one sentence on removal: `slv_pn_poi`, `gld_enr_poi_coordinate`, and the old info edges were removed on 21/10, along with `wm_flow__PL_VV_TRANS_SLV_TO_SLV_1H`, and `SLV_1H` has no rows.
- **`CTRL_TABLES_CONTEXT.md` §10.** Add the row `| 21/10 | Hai node silver thuộc ENR_15P; xoá cạnh/watermark slv_pn_poi, gld_enr_poi_coordinate, info cũ; DROP hai bảng trên DEV |`.
- **`docs/context/01_DATA_MODEL.md` §6.**
  - In N6 and N7, replace `Pipeline \`PL_VV_TRANS_SLV_TO_SLV_1H\`, chưa schedule, chạy tay.` with `Pipeline \`PL_VV_TRANS_SLV_TO_ENR_15P\`, chạy trước \`gld_enr_poi_info\` trong cùng DAG.`
  - In L346, replace `lần chạy 1H sau` with `lần chạy sau của pipeline sở hữu node`.

### 16.7 Deletions

Delete `notebooks/NB_SLV_PN_POI.ipynb` and `notebooks/NB_ENR_POI_COORDINATE.ipynb`.

## 17. Runtime runbook (user-run, Fabric DEV only)

**R0 Pre-flight (read-only).**
1. Check the lock rows:
   `SELECT watermark_id, lock_exec_id, lock_at, status FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id LIKE 'wm_flow__PL_VV_TRANS_SLV_TO_%'`
2. Count registry rows that touch the removed tables:
   `SELECT count(*) AS n FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry WHERE src_tbl IN ('slv_pn_poi','gld_enr_poi_coordinate') OR trg_tbl IN ('slv_pn_poi','gld_enr_poi_coordinate')`
   The expected result is 0. A non-zero count is a user decision.
3. Record `V_cfg` and `V_wm`: `DESCRIBE HISTORY` on each ctrl table, `LIMIT 1`.
4. For each of the two tables, record `SHOW CREATE TABLE`, `DESCRIBE DETAIL`, and `count(*)`.

Paste all R0 output to `evidence/results/runtime-r0.txt`.

**R1.** Pause the `PL_VV_TRANS_SLV_TO_ENR_15P` schedule. Wait until `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P.lock_exec_id IS NULL`.

**R2.** Sync the workspace from git. Confirm that the `NB_SLV_PN_POI` and `NB_ENR_POI_COORDINATE` items are gone.

**R3.** In `NB_CREATE_DDL`, run only cell `mvpoipy`. Expected output: `đã xoá cạnh=8 watermark=6; watermark giữ lại=17; …`.

**R4.** Run `mvpoipy` again. Expected output: `đã xoá cạnh=0 watermark=0; watermark giữ lại=17`.

**R5.** Run `NB_00_ORCHES_SLV_TO_ENR_15P` with `p_mode=PLAN`. Paste the plan and `run_multiple_dag`. Expected:
- the amenity activity depends on the entity activity;
- the info activity depends on both;
- no `slv_pn_poi` or coordinate activity;
- no ConfigError.

Also run `NB_SETUP_POI_AMENITY` with `p_apply=false`. Expected: `entity_edges_ok=6`.

**R6.** Backup and DROP. **Stop here for the user's confirmation.**
1. Gate query; continue only if it returns 0:
   `SELECT count(*) AS n FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE src_tbl IN ('slv_pn_poi','gld_enr_poi_coordinate') OR trg_tbl IN ('slv_pn_poi','gld_enr_poi_coordinate')`
2. Back up both tables:
   `CREATE TABLE lh_vv_silver.dbo.gld_enr_poi_coordinate_bak_20261021 AS SELECT * FROM lh_vv_gold.enr.gld_enr_poi_coordinate`
   `CREATE TABLE lh_vv_silver.dbo.slv_pn_poi_bak_20261021 AS SELECT * FROM lh_vv_silver.dbo.slv_pn_poi`
3. Check that each backup's count equals the R0 count (94 and 30 at probe time).
4. Drop both tables:
   `DROP TABLE IF EXISTS lh_vv_gold.enr.gld_enr_poi_coordinate`
   `DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_pn_poi`
5. Check `spark.catalog.tableExists` for the 4 tables. The expected result is coordinate False, `slv_pn_poi` False, info True, review True.

**R7.** Run NB_00 with `p_mode=RUN` and `p_force_nodes=slv_poi_entity_non_enrich,slv_poi_amenity`. Do not force `gld_enr_poi_info`: the FORCE baseline re-appends the whole table. Paste the `ctrl_log_table_run` rows for that `exec_id`, ordered by start time. Expected: entity ends before amenity starts, and the run status is SUCCESS.

**R8.** Resume the schedule. Paste the next scheduled `ctrl_log_run` row; SUCCESS or NO_DATA are both expected. Re-run `ctrl-inventory.sql`. Expected: INV-1 = 16, INV-3 = 17, an INV-5 and INV-6 "not found" error, and INV-7 and INV-8 return counts.

## 18. Verification

| Acceptance criterion | Proof |
|---|---|
| Two nodes only on ENR_15P | `mvpoipy` pre- and post-checks; R8 INV-2; `test_enr_initial_edge_state`; both setup `test_setup_contract` tests |
| Order entity → amenity → info | R5 PLAN DAG, R7 log order, `test_enr_15p_dag_order` |
| No ctrl row for `slv_pn_poi` or coordinate | R3 post-check, R6 gate, R8 INV-2, seed test |
| Old info edges gone | R3, R8 INV-2, `test_cleanup_patch_constants` |
| Tables dropped; info and review kept | R6 step 5 |
| Re-run creates and duplicates nothing | R4, `test_cleanup_patch_guards`, the seed MERGE plan `to_insert=0` (optional run of `NB_SETUP_INITIAL_DDL` with `p_apply=false`) |
| Notebooks removed from repo | `test_removed_notebooks_absent` |

Local commands:
- `python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py -q`
- `python -m pytest -q`
- A JSON load of the 4 edited notebooks.
