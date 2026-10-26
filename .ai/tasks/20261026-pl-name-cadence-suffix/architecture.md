RESULT: PASS

## Main brief

### Decision
Rename the suffix in repo code and seed. One new `NB_CREATE_DDL` cell, `plcadpy`, renames ctrl rows in place: for each pair it takes the flow lock, renames `wm_flow__<old>` to `wm_flow__<new>` (`watermark_id` and `src_tbl`) while holding it, then runs `UPDATE pipeline_config SET pl_name`, then releases. It stops before writing on conflicts and does nothing on a rerun. Logs, `wm_e__` rows, and the lib are not touched. Pipeline JSON: `git mv` to `PL_VV_TRANS_SLV_TO_ENR_15M`; the `@pipeline().Pipeline` expression stays.

### Invariants Main must preserve
- `CADENCE_RE` in lib cell `9ff87eee` is exactly `_(\d+)([MHD])$`, and the lib file is unchanged.
- In the seed, every RECOMPUTE/APPEND `pl_name` matches `CADENCE_RE`, and no active edge has a fast pl reading a node owned by a slower pl.
- After the patch: 0 config rows with the old name; new-name count = old + previous new; no duplicate logical key under the new name.
- After the patch: 0 watermark rows with `wm_flow__<old>` or `src_tbl=<old>`; exactly 1 row with `wm_flow__<new>` and `src_tbl=<new>`.
- The patch has no DROP, DELETE, or TRUNCATE, and does not touch `wm_e__` or log rows.
- A second patch run writes nothing (`đã đổi, không ghi`).
- Every patch write happens under the lock (`_refresh_lock` before each write); the cell stops if the lock is live elsewhere.
- `NB_CREATE_DDL` cells before `plcadmd` stay byte-identical. The only changed old line is the `amenddlpy` closing `}` becoming `},`.
- Pipeline JSON path, folder, and `resources[0].name` are `PL_VV_TRANS_SLV_TO_ENR_15M`; the `p_pl_name` expression stays `@pipeline().Pipeline`; the activity name stays.
- No `PL_…_15P/30P`, `ENR_15P` token, or `` `_15P` ``/`` `_30P` `` anywhere in notebooks except `NB_CREATE_DDL`, nor in pipelines, `AGENTS.md`, or naming §3.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 0 | task scope.files | — | Add `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json` and `tests/test_gld_srv_poi_contract.py` | Scope validation passes |
| 1 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` | `_ENR`→`PL_VV_TRANS_SLV_TO_ENR_15M`, `_GLD30`→`PL_VV_TRANS_SLV_TO_GLD_30M`; add a `# [SỬA 26/10] 20261026-pl-name-cadence-suffix: hậu tố nhịp P -> M.` line | `test_pl_cadence_seed` passes |
| 2 | notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb | markdown `f02e1392` | Default becomes 15M (text and table); replace the `_15P` sentence with "Hậu tố `_15M` khớp `CADENCE_RE`; lib kiểm tra nhịp giữa các luồng." | No old token |
| 3 | notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb | parameters cell (`p_pl_name = …`) | `p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15M"` | `test_pl_cadence_patch_cell` passes |
| 4 | notebooks/NB_SETUP_POI_ENTITY.ipynb | `a1setupedges` (`BEGIN_EDGE_PRECHECK`, `_write_edges`, `PL =`) | Every old literal becomes 15M; the docstring says `pl ENR_15M` | `test_setup_contract` and `test_edge_precheck_blocks_are_identical` pass |
| 5 | notebooks/NB_SETUP_POI_AMENITY.ipynb | `c1setupplan`, `c1setupedges` | Same as row 4; the precheck block stays identical to ENTITY | Same tests pass |
| 6 | notebooks/NB_CREATE_DDL.ipynb | append `plcadmd` (markdown) and `plcadpy` (code) | Copy the full-doc text verbatim; append by text insertion or with the same indent and `ensure_ascii=False`; metadata as in `amenddlpy` | Byte check OK; `test_pl_cadence_patch_cell` passes |
| 7 | pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/… | whole file | `git mv` to `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json`; set `resources[0].name`; remove the old folder | `test_pipeline_timeouts` passes |
| 8 | AGENTS.md | line 61 (cadence sentence) | `PL_VV_TRANS_SLV_TO_ENR_15M` runs every 15 minutes | No old token |
| 9 | docs/context/02_NAMING_CONVENTION.md | §3 rows at L71–72 | Replace with the text under "Naming §3 text" | `test_no_old_cadence_suffix_in_active_surface` passes |
| 10 | docs/context/CTRL_TABLES_CONTEXT.md | §10 table | Append the one 26/10 row from the doc; change no other line | The diff adds one line |
| 11 | tests/test_initial_ddl_contract.py | `test_pipeline_config_rows_match_sources`, `test_enr_initial_edge_state`, `test_enr_15p_dag_order` | Use the new names; map history through `RENAMES` | Tests pass |
| 12 | tests/test_initial_ddl_contract.py | new tests | Add `OLD_SUFFIX_RE`, `_renames`, `_cadence`, `test_pl_cadence_seed`, `test_pl_cadence_patch_cell`, `test_no_old_cadence_suffix_in_active_surface` (code in the doc) | Tests pass |
| 13 | tests/test_enr_poi_contract.py | `test_mapping_comments_and_edges` L197, `test_info_patch_cell_guards` L231–236, `test_pipeline_timeouts`, `test_hours_patch_cell_constants` L518 | Use `RENAMES`; shift ids by −2 and add the `plcad*` tail; new path, plus asserts on name and expression; use 15M | Tests pass |
| 14 | tests/test_poi_entity_contract.py | `test_setup_contract` L233/238, `_edge` L279, `test_create_ddl_patch` L628–633 | Use 15M; shift ids by −2 and add the tail | Tests pass |
| 15 | tests/test_poi_amenity_contract.py | `test_setup_contract` L582 | Use 15M | Test passes |
| 16 | tests/test_poi_media_amenity_contract.py | `test_edges_create_vs_init` L147–162, `test_amenity_untouched` L180–184 | Use 30M and 15M; history `PL` goes through `renames.get(hist, hist)` | Tests pass |
| 17 | tests/test_gld_srv_poi_contract.py | `test_info_rating_patch` L233 | `ids[-10:-2]`, then add `ids[-2:] == ["plcadmd","plcadpy"]` | Test passes |

### Order and stop points
1. STOP (user or Main decision): amend `scope.files` (row 0). Do not edit before this.
2. Rows 1–10 (code and docs), then rows 11–17 (tests).
3. Run the local verification. STOP for evidence: pytest output, byte check, grep.
4. Review gates (state-correctness, sql-data, spark-runtime, fabric-pipeline, risk-gate).
5. Runtime, done by the user and recorded in the runbook (Rollout R0–R8):
   - pause the 15P schedule and confirm no run in progress (STOP for evidence: lock free)
   - sync the notebooks
   - run `plcadpy` alone, twice
   - rename the Fabric pipeline to 15M and resume it
   - create or rename the 30M Fabric pipeline before any manual 30M run
6. STOP (user decision) if `plcadpy` reports `Dừng trước khi ghi` (both lock rows, or an edge clash). Never auto-delete.
7. STOP (evidence): PLAN of `NB_00_ORCHES_SLV_TO_ENR_15P` (default 15M) and PLAN of `NB_00_ORCHES_SLV_TO_GLD` with `p_pl_name=PL_VV_TRANS_SLV_TO_GLD_30M` show no WARN `Không đọc được nhịp` and no ConfigError. A cadence ConfigError means STOP (user decision).
8. Let ENR_15M finish one RUN before the next GLD_30M or GLD_1H RUN.

### Tests and verification
- `python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_poi_media_amenity_contract.py tests/test_gld_srv_poi_contract.py -q`, then `python -m pytest -q`.
- New tests: `test_pl_cadence_seed`, `test_pl_cadence_patch_cell`, `test_no_old_cadence_suffix_in_active_surface`.
- Updated tests: `test_pipeline_config_rows_match_sources`, `test_enr_initial_edge_state`, `test_enr_15p_dag_order`, `test_mapping_comments_and_edges`, `test_info_patch_cell_guards`, `test_pipeline_timeouts`, `test_hours_patch_cell_constants`, `test_setup_contract` (entity and amenity), `test_create_ddl_patch`, `test_edges_create_vs_init`, `test_amenity_untouched`, `test_info_rating_patch`.
- Byte check: `python -c "import json,subprocess;o=json.loads(subprocess.check_output(['git','show','HEAD:notebooks/NB_CREATE_DDL.ipynb']));n=json.load(open('notebooks/NB_CREATE_DDL.ipynb',encoding='utf-8'));assert n['cells'][:-2]==o['cells'] and n['metadata']==o['metadata'];print('ok')"`; `git diff -U0 -- notebooks/NB_CREATE_DDL.ipynb` shows one removed line.
- `rg -n "PL_VV_TRANS_SLV_TO_(ENR_15P|GLD_30P)" notebooks pipelines tests AGENTS.md docs/context/02_NAMING_CONVENTION.md`: hits only in `NB_CREATE_DDL.ipynb`.
- `git diff --quiet -- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`.
- Runtime: the probes under Observability, before and after; `DESCRIBE HISTORY` unchanged after the second run; the two PLAN logs.

### Read only if needed
- "Implementation plan › `plcadpy` code source" and "`plcadmd` markdown source": row 6.
- "Implementation plan › Naming §3 text": row 9. "Implementation plan › Edits per file": rows 1–5, 7, 8, 10.
- "Implementation plan › Test changes": rows 11–17.
- "Scope › Scope gap": row 0. "Scope › Repo facts": why no lib or log change.
- "Ordering", "Transaction and commit boundaries", "Concurrency", "Retry and recovery", "Partial failure": row 6 review, stop 6.
- "Alternatives and selected trade-off": rows 6 and 7 rationale.
- "Rollout", "Rollback and forward recovery", "Observability": stops 5–8 and the runtime runbook.

# Architecture: 20261026-pl-name-cadence-suffix

Rename the recompute `pl_name` cadence suffix from `P` to `M`: `PL_VV_TRANS_SLV_TO_ENR_15P` becomes `PL_VV_TRANS_SLV_TO_ENR_15M` and `PL_VV_TRANS_SLV_TO_GLD_30P` becomes `PL_VV_TRANS_SLV_TO_GLD_30M`. The change covers repo code and seed, plus one idempotent ctrl patch that renames existing rows in place. `NB_LIB_TRANSFORM_SLV_GLD` is not edited.

## Scope

- Repo identity:
  - Seed constants `_ENR` and `_GLD30` in `NB_SETUP_INITIAL_DDL` cell `init_seed_ctrl`.
  - Default `p_pl_name` and header markdown in `NB_00_ORCHES_SLV_TO_ENR_15P`.
  - The operational name in `NB_SETUP_POI_ENTITY` and `NB_SETUP_POI_AMENITY`.
  - The enrich pipeline JSON: folder, file, and `resources[0].name`.
  - `AGENTS.md` line 61.
  - `docs/context/02_NAMING_CONVENTION.md` §3.
  - One history row in `docs/context/CTRL_TABLES_CONTEXT.md` §10.
  - Tests.
- Ctrl state: one new `NB_CREATE_DDL` patch cell (`plcadmd` markdown and `plcadpy` code), appended at the end. It renames:
  - `ctrl_mng_pipeline_config.pl_name`, for every row of the old name, active or inactive.
  - The flow-lock row `wm_flow__<old>`: its `watermark_id` and its `src_tbl`. `src_tbl` equals `pl_name` per `ensure_lock_row`.

### Repo facts that shape the design

- `orchestrate` runs `build_dag` before `ensure_lock_row` in RUN and DRY_RUN modes. A run with a `pl_name` that has no active edges fails before it creates a lock row or a log row. PLAN writes nothing. So NB_00 cannot create a second lock row with the wrong name. Only the setup notebooks and old `NB_CREATE_DDL` cells create lock rows before they check anything.
- Edge mailbox ids `wm_e__<trg>__<src>` and APPEND markers (`find_append_marker`) are not keyed by `pl_name`. The rename does not trigger a recompute or re-append.
- `ctrl_log_run.pl_name` is read by `close_stale_runs(pl)` and `last_output_versions(owner)`. Log rows are history and stay unchanged. See Alternatives C and Partial failure.
- In the seed, the cadence check passes after the rename:
  - ENR_15M reads only unowned landing or silver tables and its own nodes.
  - GLD_30M reads `slv_poi_entity_non_enrich`, owned by ENR_15M (15 ≤ 30).
  - GLD_1H reads `slv_poi_amenity`, owned by ENR_15M (15 ≤ 60).
  - No new `ConfigError` comes from the seed. DEV may have extra edges; the runtime PLAN proves it.

### Scope gap Main must close before editing (stop point 1)

- `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json`: the rename target. It is not in `scope.files`, so this design cannot emit a FILE block for it.
- `tests/test_gld_srv_poi_contract.py`: `test_info_rating_patch` asserts `ids[-8:]` of `NB_CREATE_DDL`. Appending two cells breaks it. It is not in `scope.files`.

Both must be added to `scope.files`. This is not an evidence gap. Nothing else needs a file outside scope.

## Non-goals

- `CADENCE_RE`, `cadence_minutes`, and the `build_dag` cadence check stay unchanged. No edit to `NB_LIB_TRANSFORM_SLV_GLD`.
- No change to names ending in `_1H`, `_1D`, `_15M`, or `FL_00`. `NB_00_ORCHES_SLV_TO_GLD` cell 1 keeps its default `PL_VV_TRANSFORM_SLV_TO_GLD_1H`, and that notebook gets no edit.
- No `_30M` pipeline JSON. No notebook file rename. The pipeline activity name `NB_00_ORCHES_SLV_TO_ENR_15P` is a notebook name and stays.
- No rewrite of `ctrl_log_run` or `ctrl_log_table_run`. No change to `wm_e__` rows, tables, or the registry.
- No edits to the old `NB_CREATE_DDL` cells. No `notebooks_lgc/`. No edits to:
  - `docs/requirements/`
  - the mapping docs
  - existing mentions in `CTRL_TABLES_CONTEXT.md` (§10 gets one appended row only)
  - `00_README.md`, `01_DATA_MODEL.md`, `NB_00_ORCHES_SLV_TO_GLD.md`, `NB_LIB_TRANSFORM_SLV_GLD.md`
  - `.cursor/skills/*`, which name the notebook, not the pl
- No `model-design.md`. This task does not change data-model grain, keys, or columns.

## Invariants

- I1. `CADENCE_RE` in lib cell `9ff87eee` stays exactly `_(\d+)([MHD])$`.
- I2. In the `init_seed_ctrl` seed, every `pl_name` on a `RECOMPUTE` or `APPEND` row matches `CADENCE_RE`. No active edge makes a faster pl read a node owned by a slower pl.
- I3. After the patch, for each rename pair:
  - `ctrl_mng_pipeline_config` has 0 rows with the old name.
  - The count of rows with the new name equals the old count plus the new count measured before the write.
  - The new name has no duplicate logical key (`src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`).
- I4. After the patch, `ctrl_mng_watermark` has 0 rows with `watermark_id = wm_flow__<old>` or `src_tbl = <old>`, and exactly 1 row with `watermark_id = wm_flow__<new>` and `src_tbl = <new>`. At no point do two rows share one id.
- I5. The patch never runs `DROP`, `DELETE`, or `TRUNCATE`. It never deletes a watermark row and never touches `wm_e__` rows or log tables. The only watermark columns it changes are `watermark_id` and `src_tbl` on the lock row, plus the lock idiom columns: `lock_exec_id`, `lock_at`, `status`, `updated_at`.
- I6. A second run of the patch on converged state writes nothing: it prints `đã đổi, không ghi`, and Delta versions of both tables stay the same.
- I7. Every patch write happens while the patch holds the flow lock for that pl, and each write is preceded by `_refresh_lock`. The patch stops before writing when another live run holds the lock.
- I8. All `NB_CREATE_DDL` cells before `plcadmd` are byte-for-byte unchanged. The only diff in older lines is the closing `}` of `amenddlpy` becoming `},`.
- I9. The enrich pipeline JSON file and folder are named `PL_VV_TRANS_SLV_TO_ENR_15M`, and so is `resources[0].name`. The `p_pl_name` expression stays `@pipeline().Pipeline`.
- I10. Notebooks except `NB_CREATE_DDL`, `pipelines/**`, `AGENTS.md`, and naming §3 contain no `PL_…_15P`, `PL_…_30P`, `ENR_15P` pl token, or `` `_15P` ``/`` `_30P` ``. Old names stay only in `NB_CREATE_DDL` history cells and in `RENAMES` in `plcadpy`.

## State ownership

| State | Writers | This task |
|---|---|---|
| `ctrl_mng_pipeline_config` rows | `NB_SETUP_INITIAL_DDL` (insert-only), `NB_CREATE_DDL` patch cells, `NB_SETUP_POI_*` | `plcadpy` updates `pl_name` only |
| `wm_flow__<pl>` lock row | NB_00 (`ensure_lock_row`, acquire, release), setup notebooks, patch cells | `plcadpy` renames `watermark_id` and `src_tbl` while holding the lock |
| `wm_e__…` edge rows | NB_00 only | untouched |
| `ctrl_log_run`, `ctrl_log_table_run` | NB_00, nodes | untouched; patch reads `RUNNING` count for the report |
| Fabric pipeline item name | user in Fabric | runbook step; `@pipeline().Pipeline` yields the new name |
| Repo pipeline JSON | repo | `git mv` plus `name` edit |

## Grain and keys

Table grain is not applicable: no table, column, or grain change, and `model-design.md` is not required (`data_model_change` is out of scope). Two control keys change value but keep their shape:

- The `ctrl_mng_pipeline_config` logical key (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`), per `02_NAMING_CONVENTION.md` §4. The rename maps each old-name key to exactly one new-name key. The precheck rejects collisions.
- The `ctrl_mng_watermark` flow-lock id `wm_flow__<pl_name>`, with `src_tbl = pl_name`. One row per pl before and after.

## Alternatives and selected trade-off

- A. Watermark lock identity.
  - A1, selected: update the existing row in place (`watermark_id`, `src_tbl`). One row survives, and its last status and run id carry over.
  - A2: insert a new row and keep the old one. Rejected: it leaves two lock rows, which is the named risk.
  - A3: a lib alias map from old to new. Rejected: it edits lib, keeps a permanent dual identity, and is out of scope.
- B. Write order inside one pl.
  - B1, selected: lock first. Rename the held lock row to the new id, then rename the config rows, then release. A run with the new name sees a held lock throughout.
  - B2: config first. Between the config rename and the lock rename, a setup notebook with the new name could create `wm_flow__<new>` and collide with the rename.
- C. Run logs.
  - C1, selected: leave them. They are audit history keyed by `exec_id`.
  - C2: update `ctrl_log_run.pl_name`. Rejected: it rewrites history on an unbounded table.
  - Cost of C1: `last_output_versions(ENR_15M)` returns `{}` until the first SUCCESS or NO_DATA run under the new name. During that window GLD_30M and GLD_1H read ENR-owned nodes at their current version, with WARN `chưa có output_versions_json`. The rollout runs ENR_15M first to close the window.
- D. Conflict when both `wm_flow__<old>` and `wm_flow__<new>` exist.
  - D1, selected: stop before writing and leave the decision to the user.
  - D2: merge or delete automatically. Rejected because the request forbids watermark deletes and no repo rule says which row wins.
- E. Widening `CADENCE_RE` to accept `P`. Out of scope per the request.

## Ordering

For each pair in `RENAMES` (ENR first, then GLD30; the two are independent):

1. S0, read: count config rows with the old name and watermark rows with the old id or `src_tbl`. If both counts are 0, report `đã đổi, không ghi` and continue (I6).
2. S1, precheck with no write. Issues that stop the cell:
   - duplicate lock id
   - both old and new lock rows present
   - another watermark row with `src_tbl` set to either name
   - a config key present under both names
3. S2, only when neither lock row exists: `MERGE … WHEN NOT MATCHED INSERT` `wm_flow__<new>`, the same row `ensure_lock_row` would create.
4. S3, acquire the existing lock row (old if present, otherwise new) with the pl's lease: 35 min for ENR, 90 min for GLD30. Then read back the owner. If another live owner holds it, stop with `chạy lại sau`.
5. S4, when the lock row was old: `_refresh_lock(old)`, then `UPDATE … SET watermark_id = new_id, src_tbl = new WHERE watermark_id = old_id AND lock_exec_id = LOCK`.
6. S5, `_refresh_lock(new)`. This also asserts exactly one new-id row, held by `LOCK`.
7. S6, `UPDATE CFG SET pl_name = new WHERE pl_name = old`.
8. S7, post-check I3 and I4. On a mismatch, raise `Sau khi ghi`.
9. S8, in `finally`: release where `watermark_id IN (old_id, new_id) AND lock_exec_id = LOCK`, with status SUCCESS or FAILED.

Rollout order is under Rollout. The patch runs before the Fabric pipeline rename and before any run of the new-code `NB_SETUP_POI_*`.

## Transaction and commit boundaries

Delta has no multi-table transaction. Each of S2 to S6 and S8 is its own single-table Delta commit. Isolation from NB_00, setup notebooks, and other patch cells comes from the flow lock (I7), not from the transaction. Recovery comes from convergence on rerun (see Retry and recovery). Each pair is its own unit, and no write spans two pairs.

## Idempotency

- Every write has a guard:
  - The config `UPDATE` matches only old-name rows.
  - The lock rename matches the old id and `LOCK`.
  - The insert is `MERGE … NOT MATCHED`.
- When converged, S0 skips with no write, including no lock acquire. Lock-row `status` and `updated_at` do not churn.
- `NB_SETUP_INITIAL_DDL` stays insert-only with the new names, so a new environment never sees the old names. NB_00 creates `wm_flow__<new>` on the first run.

## Concurrency

- **NB_00 with the old name, running.** It holds `wm_flow__<old>`, so S3 stops. A zombie run whose lease expired loses the lock row after S4. Its next `refresh_flow_lock(old)` finds no row, raises `mất khoá` before writing, and its release is a no-op.
- **NB_00 with the old name after the patch.** `build_dag` finds no edges and raises `ConfigError` before creating a lock or log row. Nothing is resurrected.
- **NB_00 with the new name before the patch** (Fabric renamed too early). It fails the same way, with no rows written. With the new name during the patch, S6 has not committed yet, so it also fails before taking the lock. After S6 it sees the held lock and logs `SKIPPED_CONCURRENT`.
- **Setup notebooks with the new code.** `ensure_lock_row(new)` creates the new lock row before checking anything:
  - Run before the patch, they leave `wm_flow__<new>` next to `wm_flow__<old>`, so S1 stops on D1.
  - Run concurrently between S1 and S4, they race. S5 detects two rows, raises, and `finally` releases.
  - The runbook forbids running them before or during the patch.
- **Old `NB_CREATE_DDL` cells.** Their `PL` constants still hold old names (`enrddlpy`, `srvpoipy`, `srvratepy`, `mediaddlpy`, and the ENR lock cells). Rerunning them after the patch recreates old-name lock or config rows. `enrddlpy` has no owner guard and would insert duplicate active ENR edges under the old name, which makes `build_dag` raise `node … thuộc nhiều pl`. The `plcadmd` markdown and the runbook forbid Run-all after this patch. A patch rerun detects the clash at S1.

## Retry and recovery

There is no automatic retry. A rerun converges from any interrupted point:

| Interrupted after | State | Rerun |
|---|---|---|
| S1 stop | nothing written | fix the cause (user decision for D1 or a clash), then rerun |
| S2 | new lock row free; config still old | S1 passes; acquire new; S6 |
| S4 or S5 | lock row new, held by the old `LOCK`; config old | `finally` releases both ids. If the driver died, the lease expires (35 or 90 min), then acquire new and run S6 |
| S6 | config new, lock new held | `finally` releases; the rerun skips at S0 |
| S7 raise | written, mismatch reported | investigate with the probes; no automatic undo |

A transient Delta conflict (`ConcurrentAppend` / `ConcurrentDeleteRead`) fails the cell; rerun it.

## Partial failure

- ENR renamed but GLD30 failed: ENR is complete and consistent. Rerunning skips ENR and finishes GLD30.
- Downstream consistent slice: until ENR_15M has one SUCCESS or NO_DATA run, `plan_run` of GLD_30M and GLD_1H falls back to the current version of ENR-owned nodes and logs WARN `(node của PL_VV_TRANS_SLV_TO_ENR_15M) chưa có output_versions_json`. This is accepted and bounded to one ENR cycle. The rollout runs ENR_15M first.
- Old-name `RUNNING` rows in `ctrl_log_run` from killed runs are never closed by `close_stale_runs(new)`. The patch reports their count. They are log-only, with no control effect.

## Observability

- The patch prints one line per pair: edge rows renamed, lock action (`đổi id` or `giữ wm_flow__…`), and the count of `RUNNING` log rows under the old name. Stop messages begin `Dừng trước khi ghi (old -> new)`, and post-check failures begin `Sau khi ghi`.
- Runtime probes (SQL, before and after):
  - `SELECT pl_name, count(*), sum(is_active) FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE pl_name IN (<4 names>) GROUP BY pl_name`
  - `SELECT watermark_id, src_tbl, flow_name, status, lock_exec_id FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id LIKE 'wm_flow__PL_VV_TRANS_SLV_TO_%' OR src_tbl IN (<4 names>)`
  - `SELECT count(*) FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id LIKE 'wm_e__%'`, which must not change
  - `DESCRIBE HISTORY` of both ctrl tables before and after the second run, which must show the same latest version
- PLAN logs must show no WARN `Không đọc được nhịp` naming either new pl.

## Security

The SQL is built only from constants in the cell, with no user input or secrets. The pipeline keeps the `nb_orches_id` and `workspace_id` parameters and the `Validate_Notebook_Binding` guard. Renaming the Fabric pipeline needs workspace edit rights, which the user already has.

## Rollout

The runtime runbook content, for the runtime phase:

1. R0. Record the before probes.
2. R1. Pause the schedule of the Fabric pipeline `PL_VV_TRANS_SLV_TO_ENR_15P`. Confirm no run is in progress: Fabric monitor shows none, and `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P.lock_exec_id` is NULL or expired. **Stop for evidence.**
3. R2. Sync the changed notebooks to the workspace. Do not run `NB_SETUP_POI_*`.
4. R3. In `NB_CREATE_DDL`, run only cell `plcadpy`, never Run-all. Save the output.
   - If it stops on D1 or on an edge clash, **stop for a user decision.** Options: the user removes the inert extra row manually, or keeps it and reverts.
5. R4. Run `plcadpy` a second time. Both lines must say `đã đổi, không ghi`, and the Delta history versions must not change. Record the after probes.
6. R5. Rename the Fabric pipeline to `PL_VV_TRANS_SLV_TO_ENR_15M`, or import the repo JSON. Keep the `nb_orches_id` and `workspace_id` values, check the schedule is attached, and resume it.
7. R6. The user creates or renames the 30-minute Fabric pipeline to `PL_VV_TRANS_SLV_TO_GLD_30M` before any manual run with `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`. Alternatively, run `NB_00_ORCHES_SLV_TO_GLD` by hand with that parameter.
8. R7. Run the runtime proof:
   - `NB_00_ORCHES_SLV_TO_ENR_15P` with `p_mode = PLAN` and the default `p_pl_name`.
   - `NB_00_ORCHES_SLV_TO_GLD` with `p_mode = PLAN` and `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`.
   - Neither may log WARN `Không đọc được nhịp` for these names, and neither may raise `ConfigError`. A cadence `ConfigError` (`đọc node … của luồng chậm hơn`) means a real DEV config violation. **Stop for a user decision.**
   - Optional: PLAN of `PL_VV_TRANS_SLV_TO_GLD_1H` should also lose the WARN about ENR.
9. R8. Let ENR_15M finish one RUN (SUCCESS or NO_DATA) before the next GLD_30M or GLD_1H RUN. This closes the C1 window.

## Rollback and forward recovery

- **Forward recovery (preferred).** Fix a revealed cadence violation in config in a new task. The rename itself does not change data, edge mailboxes, or append markers.
- **Rollback.**
  - In the repo: `git revert` the code commit.
  - In Fabric: rename the pipeline back.
  - In ctrl: run the same algorithm with swapped pairs (`new → old`), delivered as a new dated `NB_CREATE_DDL` cell under a new task id. The I3, I4, I6, and I7 rules apply symmetrically.
  - Edge rows are untouched, so neither direction recomputes nodes. After a rollback the cadence check goes back to WARN-and-skip.

## Implementation plan

### Edits per file

- `NB_SETUP_INITIAL_DDL` `init_seed_ctrl`:
  - Set `_ENR` to `"PL_VV_TRANS_SLV_TO_ENR_15M"` and `_GLD30` to `"PL_VV_TRANS_SLV_TO_GLD_30M"`.
  - Add `# [SỬA 26/10] 20261026-pl-name-cadence-suffix: hậu tố nhịp P -> M.` under `# BEGIN_INIT_CTRL_SEED`.
- `NB_00_ORCHES_SLV_TO_ENR_15P`:
  - Markdown `f02e1392`: the default becomes `PL_VV_TRANS_SLV_TO_ENR_15M`, in the text and in the table row. Replace the `_15P` sentence with: ``Hậu tố `_15M` khớp `CADENCE_RE`; lib kiểm tra nhịp giữa các luồng.``
  - Parameter cell: `p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15M"`.
- `NB_SETUP_POI_ENTITY` `a1setupedges` and `NB_SETUP_POI_AMENITY` `c1setupedges`: replace every old-name literal (`flow =`, the SQL literals, `PL =`). In the docstring, `pl ENR_15P` becomes `pl ENR_15M`. Keep the `BEGIN_EDGE_PRECHECK` blocks byte-identical across the two notebooks (`test_edge_precheck_blocks_are_identical`). `NB_SETUP_POI_AMENITY` `c1setupplan` gets the same literal replacement.
- `NB_CREATE_DDL`: append `plcadmd` and `plcadpy`, as given under the next two headings. Append by inserting text before the closing `]` of `cells`, or re-serialize with the file's exact indent and `ensure_ascii=False`. Then check I8 with the byte check under Verification. The cell metadata follows `amenddlpy`: `microsoft.language = python`, `language_group = synapse_pyspark`.
- Pipeline JSON: `git mv pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/PL_VV_TRANS_SLV_TO_ENR_15P.json pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json`, then remove the empty old folder. Set `resources[0].name` to `PL_VV_TRANS_SLV_TO_ENR_15M`. Leave everything else unchanged, including the activity name and the `@pipeline().Pipeline` expression.
- `AGENTS.md` line 61: `` `PL_VV_TRANS_SLV_TO_ENR_15M` runs every 15 minutes. ``
- `02_NAMING_CONVENTION.md` §3: follow the text under "Naming §3 text".
- `CTRL_TABLES_CONTEXT.md` §10: append the row ``| 26/10 | Đổi hậu tố nhịp `pl_name` P → M cho luồng enrich 15 phút và gold 30 phút (`plcadpy`): đổi `pl_name` dòng cấu hình, id và `src_tbl` dòng `wm_flow__`. Không đổi `wm_e__`, log. Tên cũ ở các mục trên là lịch sử |``.
- Tests: follow the text under "Test changes".

### `plcadmd` markdown source

```
# [THÊM 26/10] 20261026-pl-name-cadence-suffix

Đổi hậu tố nhịp: `PL_VV_TRANS_SLV_TO_ENR_15P` → `PL_VV_TRANS_SLV_TO_ENR_15M`, `PL_VV_TRANS_SLV_TO_GLD_30P` → `PL_VV_TRANS_SLV_TO_GLD_30M`. Đổi `pl_name` của dòng cấu hình, id và `src_tbl` của dòng `wm_flow__`. Không đổi `wm_e__`, log, bảng. Không DROP, không xoá dòng watermark. Chạy lại không ghi.
Chạy cell này trước khi đổi tên pipeline Fabric và trước `NB_SETUP_POI_*`. Sau cell này không Run all và không chạy lại cell cũ có tên `_15P` / `_30P`: chúng tạo lại dòng tên cũ.
```

### `plcadpy` code source

```python
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
RUN_LOG = "lh_vv_ctrl.dbo.ctrl_log_run"
# (pl_name cũ, pl_name mới, phút hết hạn khoá = p_lock_timeout_min của luồng)
RENAMES = [
    ("PL_VV_TRANS_SLV_TO_ENR_15P", "PL_VV_TRANS_SLV_TO_ENR_15M", 35),
    ("PL_VV_TRANS_SLV_TO_GLD_30P", "PL_VV_TRANS_SLV_TO_GLD_30M", 90),
]
LOCK = "plcad-" + uuid.uuid4().hex


def _n(sql):
    return int(spark.sql(sql).first()["n"])


def _lock_rows(wid):
    return spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{wid}'").collect()


def _refresh_lock(pl):
    # STATE-001: gia hạn và kiểm lại chủ khoá ngay trước mỗi lần ghi; phải đúng 1 dòng khoá.
    wid = f"wm_flow__{pl}"
    spark.sql(f"""
    UPDATE {WM}
    SET lock_at = current_timestamp(), updated_at = current_timestamp()
    WHERE watermark_id = '{wid}' AND lock_exec_id = '{LOCK}'
    """)
    rows = _lock_rows(wid)
    if len(rows) != 1 or rows[0]["lock_exec_id"] != LOCK:
        raise RuntimeError(f"Luồng {pl} mất khoá {wid} trước khi ghi ({len(rows)} dòng)")


def _issues(old, new):
    old_id, new_id = f"wm_flow__{old}", f"wm_flow__{new}"
    n_old = _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{old_id}'")
    n_new = _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{new_id}'")
    issues = []
    if n_old > 1 or n_new > 1:
        issues.append(f"id khoá trùng: {old_id}={n_old}, {new_id}={n_new}")
    if n_old and n_new:
        issues.append(f"có cả {old_id} và {new_id}: cell không gộp, không xoá dòng watermark")
    stray = _n(f"""
    SELECT count(*) AS n FROM {WM}
    WHERE src_tbl IN ('{old}', '{new}') AND watermark_id NOT IN ('{old_id}', '{new_id}')
    """)
    if stray:
        issues.append(f"{stray} dòng watermark khác có src_tbl là tên pl: không đoán cách đổi")
    clash = spark.sql(f"""
    SELECT o.src_tbl, o.trg_schema, o.trg_tbl
    FROM {CFG} o JOIN {CFG} n
      ON o.src_schema <=> n.src_schema AND o.src_tbl <=> n.src_tbl
     AND o.trg_schema <=> n.trg_schema AND o.trg_tbl <=> n.trg_tbl
    WHERE o.pl_name = '{old}' AND n.pl_name = '{new}'
    """).collect()
    if clash:
        issues.append(f"cạnh có ở cả {old} và {new}: "
                      + ", ".join(f"{r.src_tbl}->{r.trg_schema}.{r.trg_tbl}" for r in clash))
    return issues, n_old


report = []
for old, new, lease in RENAMES:
    old_id, new_id = f"wm_flow__{old}", f"wm_flow__{new}"
    cfg_old = _n(f"SELECT count(*) AS n FROM {CFG} WHERE pl_name = '{old}'")
    wm_old = _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{old_id}' OR src_tbl = '{old}'")
    if cfg_old == 0 and wm_old == 0:
        report.append(f"{old} -> {new}: đã đổi, không ghi")
        continue
    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues, n_old = _issues(old, new)
    if issues:
        raise RuntimeError(f"Dừng trước khi ghi ({old} -> {new}): " + "; ".join(issues))
    wid = old_id if n_old else new_id
    if not n_old:
        # Chưa có dòng khoá: tạo wm_flow__<tên mới> như ensure_lock_row. Không xoá wm_flow__.
        spark.sql(f"""
        MERGE INTO {WM} AS t
        USING (SELECT '{new_id}' AS watermark_id, '{new}' AS src_tbl, 'NB_CREATE_DDL' AS flow_name) AS s
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
        WHERE watermark_id = '{wid}' AND (
            lock_exec_id IS NULL
            OR coalesce(lock_at < current_timestamp() - INTERVAL {lease} MINUTES, true))
        """)
        rows = _lock_rows(wid)
        if len(rows) != 1 or rows[0]["lock_exec_id"] != LOCK:
            other = rows[0]["lock_exec_id"] if rows else None
            raise RuntimeError(f"Luồng {old} đang giữ khoá {wid} ({other}): chạy lại sau")
        held = True
        cfg_new = _n(f"SELECT count(*) AS n FROM {CFG} WHERE pl_name = '{new}'")
        if wid == old_id:
            _refresh_lock(old)
            spark.sql(f"""
            UPDATE {WM}
            SET watermark_id = '{new_id}', src_tbl = '{new}', updated_at = current_timestamp()
            WHERE watermark_id = '{old_id}' AND lock_exec_id = '{LOCK}'
            """)
        _refresh_lock(new)
        spark.sql(f"UPDATE {CFG} SET pl_name = '{new}' WHERE pl_name = '{old}'")

        # Sau khi ghi: chỉ xét phần cell đổi.
        problems = []
        if _n(f"SELECT count(*) AS n FROM {CFG} WHERE pl_name = '{old}'"):
            problems.append(f"{CFG} còn dòng {old}")
        got = _n(f"SELECT count(*) AS n FROM {CFG} WHERE pl_name = '{new}'")
        if got != cfg_new + cfg_old:
            problems.append(f"{CFG} có {got} dòng {new}, cần {cfg_new + cfg_old}")
        dup = _n(f"""
        SELECT count(*) AS n FROM (
            SELECT 1 AS x FROM {CFG} WHERE pl_name = '{new}'
            GROUP BY src_schema, src_tbl, trg_schema, trg_tbl HAVING count(*) > 1) AS d
        """)
        if dup:
            problems.append(f"{dup} khoá cạnh trùng ở {new}")
        if _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{old_id}' OR src_tbl = '{old}'"):
            problems.append(f"{WM} còn dòng {old_id}")
        if _n(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{new_id}' AND src_tbl = '{new}'") != 1:
            problems.append(f"{WM} không có đúng 1 dòng {new_id}")
        if problems:
            raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
        running = _n(f"SELECT count(*) AS n FROM {RUN_LOG} WHERE pl_name = '{old}' AND status = 'RUNNING'")
        lock_note = "đổi id" if wid == old_id else "giữ " + new_id
        report.append(f"{old} -> {new}: cạnh {cfg_old}, khoá {lock_note}, "
                      f"run log RUNNING tên cũ {running} (không sửa log)")
    except Exception as exc:
        failed = exc
        raise
    finally:
        if held:
            status = "FAILED" if failed else "SUCCESS"
            spark.sql(f"""
            UPDATE {WM}
            SET lock_exec_id = NULL, lock_at = NULL, status = '{status}', updated_at = current_timestamp()
            WHERE watermark_id IN ('{old_id}', '{new_id}') AND lock_exec_id = '{LOCK}'
            """)
print("\n".join(report))
```

### Naming §3 text

Replace line 71 (the cadence suffix row) with:
`` | Hậu tố nhịp `_<n>M` / `_<n>H` / `_<n>D` | `…_15M`, `…_30M` (đang dùng), `…_1H` `[PROPOSED]`, `…_1D` `[PROPOSED]` | **Bắt buộc với luồng tính lại**: lib đọc nhịp từ hậu tố (`CADENCE_RE = _(\d+)([MHD])$`) để chặn luồng nhanh đọc node của luồng chậm |``

Replace line 72 with two rows:
`` | `PL_VV_TRANS_SLV_TO_ENR_15M` | `PL_VV_TRANS_SLV_TO_ENR_15M` | Luồng enrich 15 phút, notebook `NB_00_ORCHES_SLV_TO_ENR_15P`. [SỬA 26/10] đổi hậu tố P sang M để lib kiểm tra nhịp |``
`` | `PL_VV_TRANS_SLV_TO_GLD_30M` | `PL_VV_TRANS_SLV_TO_GLD_30M` | Luồng gold serving 30 phút, chạy bằng `NB_00_ORCHES_SLV_TO_GLD` với `p_pl_name` này. Repo chưa có JSON pipeline; tạo hoặc đổi tên pipeline Fabric trước khi chạy |``

### Test changes

Existing tests. Change constants, and derive old names from `RENAMES` in `plcadpy`, never from a literal:

- `tests/test_initial_ddl_contract.py`:
  - `test_pipeline_config_rows_match_sources`: `enr = "PL_VV_TRANS_SLV_TO_ENR_15M"`, `gld = "PL_VV_TRANS_SLV_TO_GLD_30M"`. Add `renames = {o: n for o, n, _l in _assign(_cell(ddl, "plcadpy"), "RENAMES")}`, `assert renames[_assign(_cell(ddl, "srvpoipy"), "PL")] == gld`, and `assert [n for o, n in renames.items() if o in _cell(ddl, "enrddlpy")] == [enr]`.
  - `test_enr_initial_edge_state` (L686) and `test_enr_15p_dag_order` (L719): `enr = "PL_VV_TRANS_SLV_TO_ENR_15M"`. Keep the function names.
- `tests/test_enr_poi_contract.py`:
  - `test_mapping_comments_and_edges` L197: replace with `renames = {o: n for o, n, _l in _assign(_cell("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")}` and `assert [n for o, n in renames.items() if o in ddl] == ["PL_VV_TRANS_SLV_TO_ENR_15M"]`.
  - `test_info_patch_cell_guards` L231–236: shift each slice by −2 and add `assert ids[-2:] == ["plcadmd", "plcadpy"]`.
  - `test_pipeline_timeouts`: new path; add `assert doc["resources"][0]["name"] == "PL_VV_TRANS_SLV_TO_ENR_15M"` and `assert activity["typeProperties"]["parameters"]["p_pl_name"]["value"]["value"] == "@pipeline().Pipeline"`. The activity name stays.
  - `test_hours_patch_cell_constants` L518: use 15M.
- `tests/test_poi_entity_contract.py`:
  - `test_setup_contract` L233 and L238: use 15M.
  - `_edge` L279: use 15M.
  - `test_create_ddl_patch` L628–633: shift by −2 and add the `plcad*` tail assert.
- `tests/test_poi_amenity_contract.py` `test_setup_contract` L582: use 15M.
- `tests/test_poi_media_amenity_contract.py`:
  - `test_edges_create_vs_init` L147–162: the pair becomes `("mediaddlpy", "PL_VV_TRANS_SLV_TO_GLD_30M")`. Replace `assert _assign(source, "PL") == pl` with `hist = _assign(source, "PL")` and `assert renames.get(hist, hist) == pl`, using `renames` from `plcadpy`. In `by_target`, use 30M.
  - `test_amenity_untouched` L180–184: use 15M.
- `tests/test_gld_srv_poi_contract.py` `test_info_rating_patch` (after the scope add): `assert ids[-10:-2] == [...]`, then `assert ids[-2:] == ["plcadmd", "plcadpy"]`.

New tests in `tests/test_initial_ddl_contract.py`. Reuse `_notebook`, `_by_id`, `_cell`, `_assign`, `_initial`, and `re`; add `ROOT = Path(__file__).resolve().parents[1]` if it is missing.

```python
OLD_SUFFIX_RE = re.compile(r"(?<![A-Za-z0-9])PL_\w*?_(?:15|30)P\b|(?<![A-Za-z0-9_])ENR_(?:15|30)P\b|`_(?:15|30)P`")


def _renames() -> list:
    return _assign(_cell(_notebook("NB_CREATE_DDL.ipynb"), "plcadpy"), "RENAMES")


def _cadence():
    lib = _by_id(_notebook("NB_LIB_TRANSFORM_SLV_GLD.ipynb"))["9ff87eee"]
    pattern = re.search(r'CADENCE_RE = re\.compile\(r"([^"]+)"\)', lib).group(1)
    assert pattern == r"_(\d+)([MHD])$"
    regex, unit = re.compile(pattern), {"M": 1, "H": 60, "D": 1440}

    def minutes(pl):
        m = regex.search(pl)
        return int(m.group(1)) * unit[m.group(2)] if m else None
    return minutes


def test_pl_cadence_seed():
    minutes = _cadence()
    ns: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], ns)  # noqa: S102
    rows = [r for r in ns["PIPELINE_CONFIG_ROWS"] if r[7] in ("RECOMPUTE", "APPEND")]
    assert {r[0] for r in rows} == {new for _o, new, _l in _renames()} | {"PL_VV_TRANS_SLV_TO_GLD_1H"}
    assert all(minutes(r[0]) for r in rows)
    owner = {(r[3], r[4]): r[0] for r in rows if r[5] == 1}
    for pl, src_schema, src, _ts, _trg, active, *_rest in rows:
        other = owner.get((src_schema, src))
        if active == 1 and other and other != pl:
            assert minutes(other) <= minutes(pl), (pl, src, other)


def test_pl_cadence_patch_cell():
    ddl = _notebook("NB_CREATE_DDL.ipynb")
    assert [c.get("id") for c in ddl["cells"]][-2:] == ["plcadmd", "plcadpy"]
    assert _cell(ddl, "plcadmd").startswith("# [THÊM 26/10] 20261026-pl-name-cadence-suffix")
    patch, renames, minutes = _cell(ddl, "plcadpy"), _renames(), _cadence()
    seed: dict = {}
    exec(_by_id(_initial())["init_seed_ctrl"], seed)  # noqa: S102
    assert [new for _o, new, _l in renames] == [seed["_ENR"], seed["_GLD30"]]
    for old, new, _lease in renames:
        assert old.endswith("P") and new == old[:-1] + "M" and minutes(old) is None and minutes(new)
    assert renames[1][0] == _assign(_cell(ddl, "srvpoipy"), "PL")
    assert renames[1][2] == _assign(_cell(ddl, "srvpoipy"), "LEASE_MINUTES")
    assert renames[0][0] in _cell(ddl, "enrddlpy")
    orch = "".join("".join(c["source"]) for c in _notebook("NB_00_ORCHES_SLV_TO_ENR_15P.ipynb")["cells"])
    assert re.search(r'^p_pl_name = "([^"]+)"', orch, re.M).group(1) == renames[0][1]
    assert int(re.search(r'^p_lock_timeout_min = "(\d+)"', orch, re.M).group(1)) == renames[0][2]
    for banned in ("DROP ", "DELETE ", "TRUNCATE"):
        assert banned not in patch.upper()
    assert "UPDATE {CFG} SET pl_name = '{new}' WHERE pl_name = '{old}'" in patch
    assert "SET watermark_id = '{new_id}', src_tbl = '{new}'" in patch
    assert patch.index("Dừng trước khi ghi") < patch.index("_refresh_lock(old)") < patch.index("SET watermark_id = '{new_id}'")
    assert patch.index("_refresh_lock(new)") < patch.index("UPDATE {CFG} SET pl_name")
    assert "Sau khi ghi" in patch and "finally:" in patch and "lock_exec_id = '{LOCK}'" in patch


def test_no_old_cadence_suffix_in_active_surface():
    paths = [p for p in (ROOT / "notebooks").glob("*.ipynb") if p.name != "NB_CREATE_DDL.ipynb"]
    paths += list((ROOT / "pipelines").rglob("*.json")) + [ROOT / "AGENTS.md"]
    hits = [p.relative_to(ROOT).as_posix() for p in paths if OLD_SUFFIX_RE.search(p.read_text(encoding="utf-8"))]
    hits += [p.name for p in (ROOT / "pipelines").iterdir() if OLD_SUFFIX_RE.search(p.name)]
    naming = (ROOT / "docs" / "context" / "02_NAMING_CONVENTION.md").read_text(encoding="utf-8")
    if OLD_SUFFIX_RE.search(naming[naming.index("## 3. Pipeline"):naming.index("## 4.")]):
        hits.append("02_NAMING_CONVENTION.md §3")
    assert hits == []
```

## Verification

- Local:
  - `python -m pytest tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_poi_amenity_contract.py tests/test_poi_media_amenity_contract.py tests/test_gld_srv_poi_contract.py -q`
  - Then the full suite: `python -m pytest -q`.
- I8 byte check, before the commit:
  - `python -c "import json,subprocess;o=json.loads(subprocess.check_output(['git','show','HEAD:notebooks/NB_CREATE_DDL.ipynb']));n=json.load(open('notebooks/NB_CREATE_DDL.ipynb',encoding='utf-8'));assert n['cells'][:-2]==o['cells'] and n['metadata']==o['metadata'];print('ok')"`
  - `git diff -U0 -- notebooks/NB_CREATE_DDL.ipynb` must show exactly one removed line, the closing brace of `amenddlpy`.
- Grep: `rg -n "PL_VV_TRANS_SLV_TO_(ENR_15P|GLD_30P)" notebooks pipelines tests AGENTS.md docs/context/02_NAMING_CONVENTION.md`. Hits are allowed only in `notebooks/NB_CREATE_DDL.ipynb`, in history cells and `plcadpy`.
- Lib unchanged: `git diff --quiet -- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`.
- Runtime proof: Rollout R0–R8. Evidence:
  - the patch output from both runs
  - the before and after probes
  - Delta history versions
  - the two PLAN logs with no `Không đọc được nhịp` for the new names
