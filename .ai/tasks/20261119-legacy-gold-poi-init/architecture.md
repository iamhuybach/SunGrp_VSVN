RESULT: PASS

## Main brief

### Decision
RESULT: PASS. The design implements D-04 option B. The lib gets an owner-aware MERGE and `diff_counts` that act only on targets with a `load_origin` column. The `NB_CREATE_DDL` cell `legacyidpy` creates the map and adds `load_origin` to the three `gld_srv_*` tables. The new notebook `NB_SETUP_LEGACY_GOLD_POI` reads pinned old gold (`VERSION AS OF`), and under the `PL_VV_TRANS_SLV_TO_GLD_30M` lock it writes, INSERT-only: the map, then info, then multi-lang, each row `LEGACY_INIT`.
`load_origin` is a separate `OWNER_COL`, not a `TECH_COLUMNS` entry, so no other lib target changes.
P2 confirmed the key formula. The open model-design defaults are gated by PLAN metrics and a user stop before RUN.

### Invariants Main must preserve
- When `owner_col` is None, the `sql_merge_target` output is byte-identical to today's.
- On a target with `load_origin`, NOT MATCHED BY SOURCE requires `load_origin IS NULL`. MATCHED also fires on `load_origin IS NOT NULL` and sets it to `CAST(NULL AS STRING)`. Inserts never set it.
- `diff_counts` mirrors this. Owned matched rows count as `updated`, and owned unmatched rows never count as `deactivated`.
- `TECH_NAMES = tuple(n for n, _ in TECH_COLUMNS) + ("load_origin",)` is self-contained. `TECH_COLUMNS` is unchanged.
- Map `poi_id` comes only from `new_poi_id`: google `uuid_md5(F.lit("google"), source_id)`, partner `uuid_md5(source_id, F.lit("partner"))`. A NULL or blank `source_id`, or a NULL `source_name`, gives NULL and `MISSING_EVIDENCE`. `partner_portal` is never hashed, and `lang` never is.
- Every init MERGE is `WHEN NOT MATCHED THEN INSERT` only. A present key, live or soft-deleted, is skipped.
- Each init source is unique on the target PK, asserted before the MERGE. Keys with more than one payload are excluded and counted, with no winner.
- Old gold is read only with `VERSION AS OF` a pin. Every write FQ starts with `sgr_visitvn_dev.`. The notebook asserts the attached workspace is `sgr_visitvn_dev`.
- RUN refuses to write unless all three targets have `load_origin string` and the lib has `owner_col` and `OWNER_COL`.
- A second RUN with the same `p_pin_json` inserts 0 into the map, info and multi-lang.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | cell `9ff87eee`, after `TECH_COLUMNS` | Add `OWNER_COL` and replace `TECH_NAMES` (doc `## Code: lib constants`) | `test_owner_col_constants` and `test_poi_entity_columns_derived` pass |
| 2 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | cell `926a3f9c` `sql_merge_target` | Add the `owner_col` parameter and the predicates (doc `## Code: sql_merge_target`) | `test_sql_merge_target_without_owner_is_unchanged` and `test_sql_merge_target_owner_predicates` pass |
| 3 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | cell `926a3f9c` `merge_target` | Pass `OWNER_COL` only if it is in `table_columns(fq)` | `test_merge_target_passes_owner_only_when_column_present` passes |
| 4 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | cell `926a3f9c` `diff_counts` | Add `_t_own` to the `upd` and `dea` terms (doc `## Code: diff_counts`) | `test_diff_counts_mirrors_owner` passes |
| 5 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | cell `926a3f9c` `ensure_target` | Exclude `OWNER_COL` from the `extra` warning | `load_origin` is not reported as an extra column |
| 6 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | markdown `191e1851` | One line on `load_origin` ownership (D-04) | text present |
| 7 | notebooks/NB_CREATE_DDL.ipynb | new cells `legacyidmd` + `legacyidpy`, appended after `enrgldpy` | Map `CREATE TABLE IF NOT EXISTS` and a guarded `ADD COLUMNS load_origin STRING` on three tables, under the lock (doc `## Code: DDL cell legacyidpy`) | `test_legacyid_ddl_cell_contract` passes, and a re-run is a no-op |
| 8 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | new cells `lgpmd`, `lgpparams`, `lgplib`, `lgpconst` | Markdown; `p_mode="PLAN"`, `p_pin_json=""`; `%run NB_LIB_TRANSFORM_SLV_GLD`; four-part constants `OLD`, `MAP_FQ`, `INFO_FQ`, `ML_FQ`, `REV_FQ`, `PL` | `test_init_write_targets_dev_only` passes |
| 9 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | cell `lgppure` | `legacy_source_name`, `new_poi_id`, `insert_only_sql`, `single_payload` (doc `## Code: init pure helpers`) | `test_insert_only_sql_has_no_update_or_delete` and `test_new_poi_id_hash_order` pass |
| 10 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | cell `lgpmain` | Preflight, pins, lock, map, info, multi-lang, `write_insert_only`, summary JSON (doc `## Code: init frames`, `## Code: init main flow`) | PLAN writes nothing; RUN gives one commit per table, tagged `LEGACY_INIT:<exec_id>` |
| 11 | tests/test_legacy_gold_poi_init_contract.py (NEEDS SCOPE) | new file | The tests listed below | `python -m pytest tests -q` is green |

### Order and stop points
1. STOP (user decision, scope): add `tests/test_legacy_gold_poi_init_contract.py` to `scope.files`. Until then, rows 1–10 can be edited but row 11 cannot.
2. Edit rows 1–6 (lib), then row 7 (DDL), then rows 8–10 (init), then row 11. Run local tests and `run-gate`.
3. STOP (runtime evidence, R1): run `legacyidpy` on DEV and paste the `DESCRIBE` output. If four-part `CREATE` or `ALTER` is rejected, STOP for a user decision on 3-part names for that cell.
4. STOP (runtime evidence, R2): publish the lib. Run a forced `DRY_RUN` of the three nodes as the baseline, then one normal 30M run. Confirm `load_origin` is all NULL, and have the user confirm the Copy Job is OK with the new column.
5. STOP (user decision, R3): run init PLAN and paste the summary. The user approves RUN, or decides, if any of these hold: `missing_evidence_n`, `cast_fail_n`, `old_inactive_n` or `lang_mismatch_n` is above 0; `cost_loaded` is false; or `conflict_n` or `no_parent_n` looks large.
6. STOP (runtime evidence, R4/R5): take the V4 checksum, run RUN, then RUN with the same `p_pin_json` (expect 0 inserts), then take the V4 checksum again and expect it equal.
7. STOP (runtime evidence, R6): run a forced `DRY_RUN` (deactivated within the baseline), then one normal run (`LEGACY_INIT` rows with `deleted_at` set = 0). Then reviewers and `risk-gate`.

### Tests and verification
- New tests in `tests/test_legacy_gold_poi_init_contract.py`:
  - `test_sql_merge_target_without_owner_is_unchanged`
  - `test_sql_merge_target_owner_predicates`
  - `test_owner_col_constants`
  - `test_diff_counts_mirrors_owner`
  - `test_merge_target_passes_owner_only_when_column_present`
  - `test_insert_only_sql_has_no_update_or_delete`
  - `test_new_poi_id_hash_order`
  - `test_init_write_targets_dev_only`
  - `test_legacyid_ddl_cell_contract`
- Existing tests that must stay green:
  - `tests/test_enr_poi_contract.py::test_enr_sql_merge_target_keys`
  - `tests/test_initial_ddl_contract.py::test_poi_entity_columns_derived`
- Commands: `python -m pytest tests -q`, then `python scripts/vv.py run-gate 20261119-legacy-gold-poi-init`.
- Runtime checks V1–V7 are in doc `## Verification`, run through `runtime-runbook.md` (`waiting_runtime`).

### Read only if needed
- `## Alternatives`: rows 1–5 (why `OWNER_COL` and not `TECH_COLUMNS`, why `diff_counts`), and rows 9–10 (insert-only, lock, pin, parent filter).
- `## Code: lib constants`, `## Code: sql_merge_target`, `## Code: diff_counts`: rows 1–5.
- `## Code: DDL cell legacyidpy`: row 7.
- `## Code: init pure helpers`, `## Code: init frames`, `## Code: init main flow`: rows 9–10.
- `## Grain and keys`: row 10 collapse rules.
- `## Ordering`, `## Transaction and commit boundaries`, `## Concurrency`: rows 7 and 10, stops 3–6.
- `## Idempotency`, `## Partial failure`, `## Retry and recovery`: row 10, stop 6.
- `## Observability`: row 10 summary fields, stop 5.
- `## Rollout`, `## Rollback and forward recovery`: stops 3–7.
- `## Verification`: row 11 and the V1–V7 checks.

# Architecture: 20261119-legacy-gold-poi-init (round 2)

## Basis

- The ledger closes the round-1 blockers. D-04 picks option B. D-05 sets the map name `gld_poi_legacy_id_map` and the notebook name `NB_SETUP_LEGACY_GOLD_POI`. D-06 sets the `vi` rule and the no-`vi` rule. `scope.files` now lists the lib and the init notebook.
- Evidence used:
  - P1 types: 0 `try_cast` failures.
  - P2 overlap: info has 19594/45521 google and 151/155 partner. Multi-lang has 58536/136315 google and 436/448 partner. No soft-deleted rows.
  - P4 lang diff.
  - P5: `VERSION AS OF` works across workspaces. Old `poi_master` is still being written: version 6995 is a MERGE at 2026-11-19T15:25Z.
  - P7: one owner, `PL_VV_TRANS_SLV_TO_GLD_30M`, for all three targets. There is no lock column in config. The lock row is `ctrl_mng_watermark` `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`, with a 90-minute lease, as in cell `srvactivepy`.
- P2 proves the key formula: it matches pipeline-written keys for both sources.
- Grain, keys and columns come from `model-design.md` `## Entities and grain`, `## Keys` (`### gld_poi_legacy_id_map`, `### New poi_id formula`, `### Rules for init target keys`) and `## Columns`. This document does not extend them.
- Model-design `## Conflicts and questions` items 3–11 have deterministic defaults in model design. Where a default could land wrong data, this design adds a PLAN metric and a user stop before RUN (`## Rollout` R3). It does not override model design.

## Scope

1. Lib `NB_LIB_TRANSFORM_SLV_GLD` (D-04). Every lib MERGE target that has a `load_origin` column follows these rules:
   - The periodic MERGE soft-deletes only rows where `load_origin IS NULL`.
   - A MATCHED row with `load_origin IS NOT NULL` is always updated, and the update resets `load_origin` to NULL.
   - `diff_counts` mirrors both rules.
   - Targets without the column behave exactly as today, and their SQL is byte-identical.
2. `NB_CREATE_DDL`: one new appended cell pair. It creates `sgr_visitvn_dev.lh_vv_gold.dbo.gld_poi_legacy_id_map` and adds `load_origin STRING` to `gld_srv_poi_info`, `gld_srv_poi_multi_lang` and `gld_srv_poi_review`.
3. New notebook `NB_SETUP_LEGACY_GOLD_POI`, with modes PLAN and RUN.
   - It reads old `poi_master` and `poi_enrichment_display` at pinned versions.
   - It writes the map, then INSERT-only `gld_srv_poi_info`, then INSERT-only `gld_srv_poi_multi_lang`, marking each row `load_origin = 'LEGACY_INIT'`.
   - It writes no review rows (model design `### Not loaded`).

## Non-goals

- Pipeline JSON, schedules, DAG edges, `ctrl_mng_pipeline_config` rows and registry rows. The init is not a DAG node.
- Running anything on Fabric in this chat.
- Loading `gld_srv_poi_review`, `gld_srv_poi_amenity` or `gld_srv_poi_media_gallery`, or any column that `model-design.md` `### Not loaded` lists.
- A planned cleanup of `LEGACY_INIT` rows. D-04 says there is none. Rollback deletes are incident-only.
- Any write to `sgr_visitvn_prd_batch`.
- `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md`. It is outside scope. The lib's own section 6 markdown cell is updated instead, and the docs file is flagged as a follow-up.

## Invariants

- **I1 Map grain.** `count(*) = count(DISTINCT legacy_poi_id)` = `count(DISTINCT poi_id)` of old `poi_master` at the pinned version (136763 at probe time). If old `poi_master` has duplicate `poi_id` at the pinned version, the run stops before any write.
- **I2 Key formula.** The map `poi_id` comes only from `new_poi_id(source_name, source_id)`, which calls lib `uuid_md5`:
  - google: `uuid_md5(F.lit("google"), F.col("source_id"))`;
  - partner: `uuid_md5(F.col("source_id"), F.lit("partner"))`.

  There is no join to silver or to new gold, and `lang` is never hashed.
- **I3 Missing evidence.** `source_id` NULL or blank after trim, or `source_name` NULL, gives `poi_id` NULL and `poi_id_status = 'MISSING_EVIDENCE'`. These rows are kept in the map and never reach a target. Lib `uuid_md5` does not null a blank input, so the guard lives in `new_poi_id`.
- **I4 Source name.** `google` → `google`, `partner_portal` → `partner`, anything else → NULL. The literal `partner_portal` never reaches `uuid_md5`.
- **I5 Insert-only.** Every init MERGE has exactly one clause, `WHEN NOT MATCHED THEN INSERT`. Init never updates, deletes or revives an existing key, live or soft-deleted, so the `poi_id` values the pipeline already computed never change.
- **I6 Unique source.** Every init source frame is unique on the target PK, and this is asserted before the MERGE. Delta does not reject duplicate source rows in a NOT MATCHED-only MERGE, so a missed duplicate would insert twice. Keys with more than one distinct payload are excluded and counted. No winner is picked.
- **I7 Idempotent.** A second RUN with the same `p_pin_json` inserts 0 rows into the map, info and multi-lang.
- **I8 Ownership.**
  - A row with `load_origin = 'LEGACY_INIT'` is never soft-deleted by the periodic MERGE.
  - The first periodic MATCHED update sets it to NULL.
  - Rows with `load_origin` NULL keep today's soft-delete behaviour.
- **I9 Isolation.** No periodic node reads old gold or the map. The lib reads only `load_origin` on its own target.
- **I10 Names and direction.**
  - The init's data reads and writes use four-part names.
  - Every write target starts with `sgr_visitvn_dev.`.
  - Old gold is read only with `VERSION AS OF <pinned>`.
  - The notebook refuses to run unless it is attached to workspace `sgr_visitvn_dev`.
- **I11 Lib first.** Init RUN refuses to write unless:
  - all three targets have `load_origin STRING`;
  - the attached lib exposes `OWNER_COL == "load_origin"`;
  - `sql_merge_target` has the `owner_col` parameter.

## State ownership

| state | writer | readers | notes |
|---|---|---|---|
| `gld_poi_legacy_id_map` | init only (INSERT-only) | init only | No technical columns (model design). No periodic access. |
| `gld_srv_*` rows with `load_origin` NULL | periodic node | serving copy, init (existence only) | Unchanged semantics. Init skips their keys. |
| `gld_srv_*` rows with `load_origin = 'LEGACY_INIT'` | init inserts them. The periodic node updates them only on MATCHED, which hands ownership over. | serving copy | Never soft-deleted while marked. Kept until the pipeline produces the key (D-04). |
| `load_origin` column | DDL cell adds it. Init sets it. The lib resets it. | lib `merge_target` and `diff_counts` | Not in `TECH_COLUMNS`, so `ensure_target` never adds it to other tables. |
| lock row `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` | orchestrator, DDL cell, init RUN | orchestrator, nodes | Same protocol as the lib's `acquire_flow_lock`, `refresh_flow_lock` and `release_flow_lock`. |
| old gold `sgr_visitvn_prd_batch` | old pipelines (still running) | init, pinned | Read-only for this task. |

## Grain and keys

- Map: `model-design.md` `### gld_poi_legacy_id_map`. The PK is `legacy_poi_id`. The new `poi_id` is many-to-one: up to 3 langs, plus the partner `source_id` that has two `vi` rows. Both map rows stay.
- Targets: `model-design.md` `### Existing targets (keys unchanged)`. These are `gld_srv_poi_info.poi_id`, `gld_srv_poi_multi_lang.(poi_id, lang)` and `gld_srv_poi_review.review_id`.
- Collapse to target grain follows `### Rules for init target keys`, items 3 and 4. It is implemented as a `collect_set` of a payload struct per target PK (`## Code: init frames`):
  - **Info.**
    - Compared payload: `source_name`, `business_sector`, `business_category`, `subcategory_tags`, `operating_status`, `is_verified` and `is_bookable`, plus `rating_overall` and `rating_count` for google. The partner ratings are NULL before the compare.
    - Name pair: `(poi_name, district)` is collected from `lang = 'vi'` rows only.
    - The key is written only when the compared set has exactly 1 element and the `vi` set has at most 1. With no `vi` row, `poi_name` and `district` are NULL (D-06). Two `vi` rows with identical values collapse to one.
  - **Multi-lang.** The payload is `source_name`, `description`, `time_to_spend`, `best_time`, plus `cost` only when the target has a `cost` column (model-design Conflict 7). The key is written only when the set has exactly 1 element. `lang` comes from the map, which is the model-design rule.
  - **Logical FK (architecture rule).** A multi-lang key is written only when its `poi_id` has a live `gld_srv_poi_info` row after the info step. Excluded keys are counted as `no_parent_n`.

## Alternatives

| decision | options | selected | why |
|---|---|---|---|
| Writer separation | A INSERT-only with the lib unchanged; B `load_origin`; C the lib reads the map; D seed silver; E map only | B (D-04) | Decided by the user. A fails because the next dirty MERGE soft-deletes about 26k legacy info rows. C and D break D-01. |
| Where `load_origin` lives in the lib | (a) add it to `TECH_COLUMNS`; (b) a separate `OWNER_COL`, detected per target, plus `TECH_NAMES` | (b) | (a) would make `ensure_target` and `target_ddl` add the column to every lib target (silver and the `gld_enr_*` tables), a schema change outside D-04. With (b), only the three altered tables change behaviour, and every other target's SQL stays byte-identical. |
| `diff_counts` | leave it as is, or mirror the predicates | mirror | If left as is, `deactivated` counts the legacy-only rows on every run, so the MERGE runs every 30 minutes even when nothing changed and the run logs are wrong. A legacy row whose hash happens to match would also never be handed over. |
| Init write | (a) left-anti join + append; (b) INSERT-only MERGE; (c) upsert MERGE | (b) | (b) re-checks key existence at commit and gives one atomic commit per table. (a) races with a writer that does not hold the lock. (c) breaks I5. |
| Lock | inline four-part SQL, or the lib helpers with a workspace guard | lib helpers + guard | One lock protocol, with precedent in `NB_SETUP_POI_AMENITY`. The lib's 3-part ctrl names resolve to `sgr_visitvn_dev` only because the guard (I10) asserts the attached workspace. |
| Old snapshot | read latest, or `VERSION AS OF` pinned | pinned (P5) | Old gold is still being merged. Pinning makes PLAN, RUN and the re-run see the same input. |
| Multi-lang orphans | write all, or require a live info parent | require a parent | Honours the model's logical FK `poi_id → gld_srv_poi_info.poi_id`. It drops only children of info keys that were skipped as conflicts. PLAN reports how many. |
| Rollback of init rows | `RESTORE`, hard `DELETE`, or soft-delete | soft-delete first | Soft-deleted rows stay consistent with the downstream copy and with the lib: MATCHED revives a key when the pipeline produces it. `RESTORE` would erase pipeline commits made after the init. |
| Run log | `ctrl_log_table_run` rows, or a JSON summary plus a Delta `userMetadata` tag | the latter | Rows under a fake `pl_name` could confuse orchestrator readers such as `node_logs` and `last_output_versions`. The commit tag `LEGACY_INIT:<exec_id>` is durable in `DESCRIBE HISTORY`. |

## Ordering

1. **DDL cell** (`legacyidpy`). It holds the PL lock, creates the map if it is missing, and adds `load_origin` to the three targets if it is missing. Each `ALTER` is a metadata commit. The cell writes no rows.
2. **Publish the lib** with the owner-aware MERGE. Then run one periodic pass, or a forced `DRY_RUN` of the three nodes.
   - The lib and the `ALTER` may land in either order. Without the column, the lib predicate is off. Without the new lib, the column stays NULL and `ensure_target` only warns.
   - Both must be in place before step 3. I11 enforces this.
3. **Init PLAN.** It reads only and writes nothing, prints the summary and stops for user review (R3).
4. **Init RUN** under the lock, in this order:
   1. pin the old versions;
   2. map MERGE;
   3. re-read the map from Delta;
   4. info MERGE;
   5. re-read live info keys;
   6. multi-lang MERGE;
   7. release the lock in `finally`.
5. **Init RUN again** with the same `p_pin_json`. It must insert 0 everywhere.
6. **Periodic soak:** a forced `DRY_RUN`, then a normal run (`## Verification`).

Why this order:

- The map comes first, so every target derives `poi_id` from one persisted Delta version.
- Info comes before multi-lang because the multi-lang parent filter reads info after its commit.
- The lib comes before any init row, because the first periodic run after an init with the old lib would soft-delete every legacy-only row.

## Transaction and commit boundaries

- One Delta commit per table write: the map, info, and multi-lang. Nothing is atomic across tables. Each step's correctness depends only on committed state that earlier steps left (`## Partial failure`).
- Before each MERGE, the init records `v_pre` from `DESCRIBE HISTORY <fq> LIMIT 1`. After it, it records `v_post` and `operationMetrics.numTargetRowsInserted`.
- Each init commit carries `spark.databricks.delta.commitInfo.userMetadata = LEGACY_INIT:<exec_id>`. The conf is unset in `finally`.
- The old inputs are read with `VERSION AS OF` from `p_pin_json`. When the parameter is empty, the init uses the latest versions at run start and prints them.
- The DDL cell commits are schema-only (`CREATE TABLE IF NOT EXISTS`, `ALTER TABLE ADD COLUMNS`). Each is idempotent, with a check before and after.

## Idempotency

- **Map**: `MERGE ON legacy_poi_id` with `WHEN NOT MATCHED THEN INSERT` only. A re-run with the same pin inserts 0.
  - A re-run with a newer pin inserts only new old ids. Existing rows are never updated.
  - `drift_n` counts existing rows whose `lang`, `legacy_ingestion_source` or `source_id` differ from the new pin. It is reported, not applied.
- **Targets**: INSERT-only on the PK (I5).
  - A second run finds every key present, whether it is a `LEGACY_INIT` row, a handed-over row or a pipeline row.
  - A pipeline soft-delete is never undone, because a present deleted key is also skipped.
- **Pipeline-computed `poi_id`**: init derives the same deterministic key (P2), finds it present and skips it. The pipeline's keys and rows are untouched.
- **DDL cell**: re-running it changes nothing.
- **Lib reset**: after handover, `load_origin` is NULL and the row is steady-state pipeline-owned. Repeated periodic runs do nothing more.

## Concurrency

- **Init RUN and the 30M flow.** RUN calls `acquire_flow_lock(PL, EXEC, EXEC, LOCK_TIMEOUT_DEFAULT_MIN)` and aborts with no write if the lock is held.
  - It calls `refresh_flow_lock` immediately before each of its three MERGEs. `refresh_flow_lock` raises if the lock was lost.
  - While the init holds the lock, the orchestrator gets "lock held" and skips the run. A manual `run_node` also takes this lock.
- **Lease.** The lease is 90 minutes and is refreshed before each write. The expected compute is about 140k + 137k rows, which takes minutes.
- **Defence in depth.** If a writer that does not hold the lock commits during an init MERGE, Delta optimistic concurrency fails one of the two. The init does not retry. It releases the lock and exits non-zero, and the operator re-runs it, which is idempotent.
- **PLAN** takes no lock and writes nothing. Its counts are advisory, and RUN recomputes them under the lock.
- **Old-model writers.** They keep merging into `sgr_visitvn_prd_batch`. Pinning isolates the init from them. A `VACUUM` on the old side that removes the pinned files makes the read fail with no write. Recovery is a re-run with a newer pin.
- **Readers.** The serving copy and any SQL endpoint read Delta snapshots. They see the map and info commits before the multi-lang commit, which is an acceptable gap of seconds.
- **The DDL cell** holds the same lock, as `srvactivepy` does, so an `ALTER` never interleaves with a node MERGE.

## Retry and recovery

- There is no automatic retry inside the init. Every failure path releases the lock, prints the partial summary and raises.
- Recovery is always "re-run RUN with the same `p_pin_json`". There is no resume pointer, because the idempotency rules make finished steps no-ops.
- If the pinned version is no longer readable, re-run with an empty `p_pin_json`, which takes the latest version. The map's INSERT-only rule keeps existing rows, and the `drift_n` count makes any change visible.

## Partial failure

| failure point | state left | effect on the periodic flow | recovery |
|---|---|---|---|
| preflight (I10, I11, I1 duplicate, cast failure) | nothing written | none | fix the cause, re-run |
| map MERGE fails | map unchanged | none | re-run |
| after map, info fails | map complete | none. The map is not read periodically. | re-run. The map inserts 0. |
| after info, multi-lang fails | info `LEGACY_INIT` rows live | Safe under I8. Info rows have no children until the re-run. | re-run. Info inserts 0, then multi-lang. |
| lock lost before a MERGE | earlier commits stay | none | re-run after the periodic run ends |
| lib published without the column, or the reverse | mixed | none (`## Ordering` step 2) | finish the missing half |

## Observability

The init prints one JSON summary and returns it as the notebook exit value. The operator pastes it into the runtime evidence. It holds counts only:

- `exec_id`, `mode`, `pins` (`{poi_master: v, poi_enrichment_display: v}`).
- `map`:
  - rows by (`legacy_ingestion_source`, `source_name`, `poi_id_status`);
  - `missing_evidence_n`, `drift_n`;
  - `candidates`, `inserted`, `v_pre`, `v_post`.
- `info`:
  - `groups`, `cmp_conflict_n`, `vi_conflict_n`, `no_vi_n`;
  - `cast_fail_n`, which blocks when above 0;
  - `old_inactive_n`, the keys to insert where an old row has `is_active = false` (model-design Conflict 6);
  - `candidates`, `present_live`, `present_deleted`, `to_insert`, `inserted`, `v_pre`, `v_post`.
- `multi_lang`:
  - `display_rows`, `orphan_n` (display rows with no map row), `null_lang_n`, `lang_mismatch_n` (display `lang` ≠ map `lang`);
  - `conflict_n`, `no_parent_n`, `cost_loaded` (bool);
  - `candidates`, `present_live`, `present_deleted`, `to_insert`, `inserted`, `v_pre`, `v_post`.
- `review`: `load_origin_present` (bool), with `inserted` always 0.

Durable trail: Delta `userMetadata` `LEGACY_INIT:<exec_id>` on each init commit, and `load_origin` on each init row.

Periodic side: the `ctrl_log_table_run.deactivated_rows` of the three nodes now excludes legacy rows. The baseline is recorded at R2.

The init logs no `source_id`, names, addresses, phone numbers, emails or text.

## Security

- The workspace guard (I10) and the prefix assertion on every write target (`sgr_visitvn_dev.`) mean the init has no code path that writes `sgr_visitvn_prd_batch`.
- It uses the notebook identity, with cross-workspace access per D-03. There are no secrets or connection strings.
- Data moves gold to gold inside one tenant. Partner contact columns are not loaded, and output is aggregates only.
- The SQL is built only from constants and identifiers validated by `is_fq_name`. No parameter value is concatenated into SQL. `p_pin_json` values are cast to `int` before use.

## Rollout

DEV only, run by the user through `runtime-runbook.md`. The status is `waiting_runtime`.

- **R1 DDL.** Run cell `legacyidpy`. Paste the `DESCRIBE` of the map and the `load_origin` type on the three tables.
  - If Fabric rejects four-part `CREATE` or `ALTER`, stop for a user decision: allow 3-part names for this one cell, since the cell runs attached to `sgr_visitvn_dev`, which D-03 does not cover.
- **R2 Lib and downstream copy.** Publish the lib. Run `NB_GLD_SRV_POI_INFO`, `_MULTI_LANG` and `_REVIEW` with `p_mode=DRY_RUN, p_force=true`.
  - Record `inserted`, `updated` and `deactivated` as the baseline.
  - Then let one normal 30M run finish. Confirm `count(load_origin IS NOT NULL) = 0` on all three tables.
  - The user confirms the gold → PostgreSQL Copy Job ran successfully with the new column present. Its mapping is outside the repo. **Stop for evidence.**
- **R3 PLAN.** Run the init with `p_mode=PLAN`. **Stop for a user decision** if any of these hold:
  - `missing_evidence_n > 0`;
  - `cast_fail_n > 0`;
  - `old_inactive_n > 0` (Conflict 6);
  - `cost_loaded = false` (Conflict 7);
  - `lang_mismatch_n > 0`;
  - `no_parent_n` or `conflict_n` looks larger than expected. P2 bounds info inserts to at most 25927 google and 4 partner.

  Otherwise the user approves RUN.
- **R4 RUN**, then **R5 RUN** with the same `p_pin_json`, which must insert 0.
- **R6 Soak.** Run the forced `DRY_RUN` of the info and multi-lang nodes. `deactivated` must stay within the R2 baseline: it must not grow by the legacy count. Then let one normal run finish, and run the checks in `## Verification`.
- **Consequence the user accepts with D-04.** About 26k legacy info rows without `destination_id`, address or coordinates become visible to serving until the pipeline produces them. R3 shows the exact number.

## Rollback and forward recovery

- **Before any init row exists**, the lib and DDL changes can be reverted freely. The extra NULL column is harmless.
- **Init rows, preferred: soft rollback.**
  - Run `UPDATE <info|multi_lang> SET deleted_at = current_timestamp(), updated_at = current_timestamp() WHERE load_origin = 'LEGACY_INIT' AND deleted_at IS NULL`.
  - Handed-over rows have `load_origin` NULL and are not touched.
  - If the pipeline later produces a soft-deleted legacy key, the lib's MATCHED clause revives it and hands it over.
  - The map can stay, or be dropped. Nothing periodic reads it.
- **Hard rollback**, only to re-init: `DELETE ... WHERE load_origin = 'LEGACY_INIT'`, then re-run the init. Soft-deleted keys would otherwise block re-insert under I5.
- `RESTORE TABLE ... TO VERSION v_pre` is allowed only when `DESCRIBE HISTORY` shows no commit after `v_post`.
- **Lib revert after an init** must come after the soft or hard rollback above. Otherwise the next run soft-deletes every live `LEGACY_INIT` row. That outcome is recoverable but uncontrolled.
- **Forward recovery**: fix the cause and re-run the init. It inserts only missing keys.
- Every rollback action is a user-run incident step. D-04 has no planned cleanup.

## Implementation plan

1. Lib cell `9ff87eee`: constants (`## Code: lib constants`).
2. Lib cell `926a3f9c`:
   - `diff_counts` (`## Code: diff_counts`);
   - `ensure_target`: exclude `OWNER_COL` from the extra-column warning;
   - `sql_merge_target` (`## Code: sql_merge_target`);
   - `merge_target`: pass `owner_col` only when the target has it.
3. Lib markdown `191e1851`: add one line on `load_origin` ownership.
4. `NB_CREATE_DDL`: append markdown cell `legacyidmd` and code cell `legacyidpy` after `enrgldpy` (`## Code: DDL cell legacyidpy`).
5. `NB_SETUP_LEGACY_GOLD_POI` (new) cells:
   - `lgpmd`: purpose, modes and the runbook pointer;
   - `lgpparams`: parameters cell, `p_mode = "PLAN"`, `p_pin_json = ""`;
   - `lgplib`: `%run NB_LIB_TRANSFORM_SLV_GLD`;
   - `lgpconst`: constants;
   - `lgppure`: pure helpers (`## Code: init pure helpers`);
   - `lgpmain`: preflight, frames, PLAN or RUN (`## Code: init frames`, `## Code: init main flow`).
6. New test file `tests/test_legacy_gold_poi_init_contract.py`. It needs a `scope.files` expansion first.

## Code: lib constants

Cell `9ff87eee`, directly after `TECH_COLUMNS`. `TECH_NAMES` must stay self-contained, because `tests/test_initial_ddl_contract.py::_exec_assigns` runs that one assignment alone.

```python
# [THÊM 19/11] 20261119-legacy-gold-poi-init D-04: cột chủ dòng. Chỉ có trên bảng đã ALTER (NB_CREATE_DDL legacyidpy);
# không nằm trong TECH_COLUMNS nên ensure_target / target_ddl không thêm vào bảng khác. Build không được trả cột này.
OWNER_COL = "load_origin"
TECH_NAMES = tuple(n for n, _ in TECH_COLUMNS) + ("load_origin",)
```

## Code: sql_merge_target

Cell `926a3f9c`. The insert clause and the soft-delete SET list are unchanged. When `owner_col` is None, the output string must equal today's output.

```python
def sql_merge_target(fq: str, view: str, cols: list, pk: tuple, soft_delete_set: dict,
                     owner_col: Optional[str] = None) -> str:
    """Câu MERGE row_hash + xoá mềm (tách hàm để test parse).

    Input : cols — cột nghiệp vụ (không gồm row_hash) ; soft_delete_set — {cột: biểu thức SQL} ;
            owner_col — [THÊM 19/11] cột chủ dòng (load_origin) khi bảng đích có: không xoá mềm dòng có chủ,
            MATCHED luôn cập nhật dòng có chủ và trả chủ về NULL. None -> câu MERGE như cũ.
    """
    on = " AND ".join(f"t.`{c}` = s.`{c}`" for c in pk)
    upd = [f"t.`{c}` = s.`{c}`" for c in cols if c not in pk]
    upd += ["t.`row_hash` = s.`row_hash`", "t.`updated_at` = current_timestamp()", "t.`deleted_at` = NULL"]
    changed = "t.`row_hash` IS NULL OR t.`row_hash` <> s.`row_hash` OR t.`deleted_at` IS NOT NULL"
    sd_when = "t.`deleted_at` IS NULL"
    if owner_col:
        upd.append(f"t.`{owner_col}` = CAST(NULL AS STRING)")
        changed += f" OR t.`{owner_col}` IS NOT NULL"
        sd_when += f" AND t.`{owner_col}` IS NULL"
    ins_cols = [f"`{c}`" for c in cols] + ["`row_hash`", "`created_at`", "`updated_at`", "`deleted_at`"]
    ins_vals = [f"s.`{c}`" for c in cols] + ["s.`row_hash`", "current_timestamp()", "current_timestamp()",
                                             "CAST(NULL AS TIMESTAMP)"]
    sd = ["t.`deleted_at` = current_timestamp()", "t.`updated_at` = current_timestamp()"]
    sd += [f"t.`{c}` = {expr}" for c, expr in soft_delete_set.items()]
    nl = ",\n    "
    return f"""
MERGE INTO {quote_name(fq)} AS t
USING {view} AS s
ON {on}
WHEN MATCHED AND ({changed}) THEN UPDATE SET
    {nl.join(upd)}
WHEN NOT MATCHED THEN INSERT ({', '.join(ins_cols)})
VALUES ({', '.join(ins_vals)})
WHEN NOT MATCHED BY SOURCE AND {sd_when} THEN UPDATE SET
    {nl.join(sd)}
"""
```

`merge_target` change, two lines:

```python
    owner = OWNER_COL if OWNER_COL in table_columns(fq) else None
    sql = sql_merge_target(fq, view, cols, spec.pk, spec.soft_delete_set, owner)
```

`ensure_target` change, one line:

```python
    extra = sorted(set(existing) - {n.lower() for n, _ in wanted} - {OWNER_COL})
```

## Code: diff_counts

Cell `926a3f9c`. This mirrors the MERGE: owned rows count as updates when matched, and never count as deactivations.

```python
    pk = list(pk)
    own = (F.col(OWNER_COL) if OWNER_COL in {c.lower() for c in t.columns}
           else F.lit(None).cast("string"))
    s = src.select(*pk, F.col("row_hash").alias("_s_hash"), F.lit(1).alias("_s_in"))
    tt = t.select(*pk, F.col("row_hash").alias("_t_hash"), F.col("deleted_at").alias("_t_del"),
                  own.alias("_t_own"), F.lit(1).alias("_t_in"))
    j = s.join(tt, pk, "full_outer")
    both = F.col("_s_in").isNotNull() & F.col("_t_in").isNotNull()
    r = j.agg(
        F.sum(F.when(F.col("_s_in").isNotNull() & F.col("_t_in").isNull(), 1).otherwise(0)).alias("ins"),
        F.sum(F.when(both & (F.col("_t_hash").isNull() | (F.col("_t_hash") != F.col("_s_hash"))
                             | F.col("_t_del").isNotNull() | F.col("_t_own").isNotNull()), 1).otherwise(0)).alias("upd"),
        F.sum(F.when(F.col("_s_in").isNull() & F.col("_t_in").isNotNull() & F.col("_t_del").isNull()
                     & F.col("_t_own").isNull(), 1).otherwise(0)).alias("dea"),
    ).first()
```

## Code: DDL cell legacyidpy

The lock acquire, `_refresh_lock` and `finally` release are copied verbatim from `srvactivepy`, with `WM` four-part and `LOCK = "legacyid-" + uuid.uuid4().hex`.

```python
# [THÊM 19/11] 20261119-legacy-gold-poi-init (D-04, D-05)
# Tạo gld_poi_legacy_id_map; thêm load_origin STRING cuối gld_srv_poi_info / _multi_lang / _review.
# Chỉ đổi schema: không ghi dòng, không đổi cạnh / registry. Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M. Chạy lại: không ghi.
import uuid

WS = "sgr_visitvn_dev"
WM = f"{WS}.lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
GLD = f"{WS}.lh_vv_gold.dbo"
MAP_FQ = f"{GLD}.gld_poi_legacy_id_map"
MAP_COLS = [
    ("legacy_poi_id", "STRING NOT NULL"), ("lang", "STRING"), ("legacy_ingestion_source", "STRING"),
    ("source_id", "STRING"), ("source_name", "STRING"), ("poi_id", "STRING"), ("poi_id_status", "STRING NOT NULL"),
]
OWNER = ("load_origin", "STRING")
OWNER_TABLES = (f"{GLD}.gld_srv_poi_info", f"{GLD}.gld_srv_poi_multi_lang", f"{GLD}.gld_srv_poi_review")
PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'"
LOCK = "legacyid-" + uuid.uuid4().hex

def _want(cols):
    return [(n.lower(), t.replace(" NOT NULL", "").lower(), "NOT NULL" not in t) for n, t in cols]

def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]

def _exists(fq):
    try:
        spark.table(fq).schema
        return True
    except Exception:
        return False

# acquire lock (srvactivepy) ... then:
#   stop before write:
#     any OWNER_TABLES missing -> raise
#     load_origin present with type != string -> raise
#     map exists and _schema(MAP_FQ) != _want(MAP_COLS) -> raise
#   write:
#     map missing -> _refresh_lock(); CREATE TABLE IF NOT EXISTS {MAP_FQ} (<MAP_COLS>) USING DELTA TBLPROPERTIES ({PROPS})
#     for each table lacking load_origin -> _refresh_lock(); ALTER TABLE {fq} ADD COLUMNS (`load_origin` STRING)
#   after write: _schema(MAP_FQ) == _want(MAP_COLS) and load_origin string on all three, else raise
#   print("legacyid: map {+|=}, owner +[...] / =[...]")
# finally: release lock (srvactivepy)
```

## Code: init pure helpers

Cell `lgppure`. These depend only on `F`, `uuid_md5` and `quote_name` from the lib.

```python
ORIGIN = "LEGACY_INIT"

def legacy_source_name(c):
    """google -> google ; partner_portal -> partner ; khác -> NULL (không tự đặt)."""
    return F.when(c == F.lit("google"), F.lit("google")).when(c == F.lit("partner_portal"), F.lit("partner"))

def new_poi_id(source_name, source_id):
    """poi_id model mới; không lang; source_id NULL / trống -> NULL (uuid_md5 không tự chặn chuỗi trống)."""
    ok = source_id.isNotNull() & (F.trim(source_id) != F.lit(""))
    return (F.when(ok & (source_name == F.lit("google")), uuid_md5(F.lit("google"), source_id))
             .when(ok & (source_name == F.lit("partner")), uuid_md5(source_id, F.lit("partner"))))

def insert_only_sql(fq: str, view: str, cols: list, pk: tuple) -> str:
    """MERGE chỉ INSERT: khoá đã có (sống hoặc xoá mềm) thì bỏ qua."""
    on = " AND ".join(f"t.`{c}` = s.`{c}`" for c in pk)
    ins = ", ".join(f"`{c}`" for c in cols)
    val = ", ".join(f"s.`{c}`" for c in cols)
    return (f"MERGE INTO {quote_name(fq)} AS t\nUSING {view} AS s\nON {on}\n"
            f"WHEN NOT MATCHED THEN INSERT ({ins})\nVALUES ({val})")

def single_payload(df, keys: list, payload: list, name: str = "_p"):
    """Gom theo khoá đích. (khoá có đúng 1 payload, khoá có > 1 payload). Không chọn winner."""
    g = df.groupBy(*keys).agg(F.collect_set(F.struct(*payload)).alias(name))
    return g.where(F.size(name) == 1), g.where(F.size(name) > 1)
```

## Code: init frames

Cell `lgpmain`. Here `old(t)` is `spark.sql(f"SELECT * FROM {quote_name(OLD + '.' + t)} VERSION AS OF {int(PINS[t])}")`.

```python
pm = old("poi_master")
map_src = (pm.select(F.col("poi_id").alias("legacy_poi_id"), "lang",
                     F.col("ingestion_source").alias("legacy_ingestion_source"), "source_id")
             .withColumn("source_name", legacy_source_name(F.col("legacy_ingestion_source")))
             .withColumn("poi_id", new_poi_id(F.col("source_name"), F.col("source_id")))
             .withColumn("poi_id_status", F.when(F.col("poi_id").isNotNull(), F.lit("OK"))
                                           .otherwise(F.lit("MISSING_EVIDENCE"))))
# RUN: MERGE map, rồi đọc lại MAP_FQ. PLAN: dùng map hiện có union map_src chưa có (chỉ để đếm).
mp = map_rows.where("poi_id_status = 'OK'")

CMP = ["business_sector", "business_category", "subcategory_tags", "operating_status",
       "is_verified", "is_bookable", "rating_overall", "rating_count"]
g = mp["source_name"] == F.lit("google")
rows = pm.join(mp, pm["poi_id"] == mp["legacy_poi_id"]).select(
    mp["poi_id"], mp["source_name"], pm["lang"], pm["poi_name"], pm["district"], pm["is_active"].alias("_old_active"),
    *[pm[c] for c in CMP[:6]],
    F.when(g, pm["rating_overall"].cast("decimal(4,2)")).alias("rating_overall"),
    F.when(g, pm["rating_count"].cast("int")).alias("rating_count"))
agg = rows.groupBy("poi_id").agg(
    F.collect_set(F.struct("source_name", *CMP)).alias("_cmp"),
    F.collect_set(F.when(F.col("lang") == "vi", F.struct("poi_name", "district"))).alias("_vi"),
    F.max(F.when(F.col("_old_active") == F.lit(False), 1).otherwise(0)).alias("_inactive"))
keep = (F.size("_cmp") == 1) & (F.size("_vi") <= 1)
one_vi = F.size("_vi") == 1
info_src = agg.where(keep).select(
    "poi_id", *[F.col("_cmp").getItem(0)[c].alias(c) for c in ["source_name", *CMP]],
    F.when(one_vi, F.col("_vi").getItem(0)["poi_name"]).alias("poi_name"),
    F.when(one_vi, F.col("_vi").getItem(0)["district"]).alias("district"),
    F.lit(True).alias("is_active"), "_inactive")
# cast_fail_n: dòng google có rating khác NULL mà cast ra NULL -> > 0 thì dừng trước khi ghi.

ML_PAY = ["description", "time_to_spend", "best_time"] + (["cost"] if "cost" in table_columns(ML_FQ) else [])
d = old("poi_enrichment_display")
x = d.join(mp, d["poi_id"] == mp["legacy_poi_id"]).select(
    mp["poi_id"], mp["lang"], mp["source_name"], *[d[c] for c in ML_PAY], d["lang"].alias("_d_lang"))
ml_ok, ml_conflict = single_payload(x.where("lang IS NOT NULL"), ["poi_id", "lang"], ["source_name", *ML_PAY])
ml_src = ml_ok.select("poi_id", "lang", *[F.col("_p").getItem(0)[c].alias(c) for c in ["source_name", *ML_PAY]])
# parent: RUN -> spark.table(INFO_FQ) deleted_at IS NULL sau commit info; PLAN -> info sống ∪ khoá info sẽ insert.
ml_src = ml_src.join(parents, "poi_id", "left_semi")

def to_target(src, fq, batch_ts):
    """Khung đúng cột bảng đích: cột không nạp = NULL đúng kiểu; row_hash lib; LEGACY_INIT."""
    cols = table_columns(fq)
    biz = [c for c in cols if c not in TECH_NAMES]
    df = src.select(*[(F.col(c) if c in src.columns else F.lit(None)).cast(cols[c]).alias(c) for c in biz])
    df = df.withColumn("row_hash", _hash_expr(df, biz))
    ts = F.lit(batch_ts).cast("timestamp")
    return (df.withColumn("created_at", ts).withColumn("updated_at", ts)
              .withColumn("deleted_at", F.lit(None).cast("timestamp")).withColumn(OWNER_COL, F.lit(ORIGIN)))
```

## Code: init main flow

Cell `lgpmain`, as ordered steps:

1. Preflight, read-only:
   - the workspace name from `notebookutils.runtime.context` equals `sgr_visitvn_dev`;
   - `OWNER_COL == "load_origin"`, it is in `TECH_NAMES`, and `"owner_col" in inspect.signature(sql_merge_target).parameters`;
   - `MAP_FQ` exists with the DDL schema;
   - the three targets have `load_origin` of type `string`;
   - `p_mode` is in (`PLAN`, `RUN`).
2. Pins: from `p_pin_json`, with each value cast to int, or from `DESCRIBE HISTORY <old> LIMIT 1`.
   - Stop if old `poi_master` at the pin has `count(*) != count(DISTINCT poi_id)`.
3. RUN only: `acquire_flow_lock(PL, EXEC, EXEC, LOCK_TIMEOUT_DEFAULT_MIN)`, or raise. Everything after this runs in `try`, and the `finally` calls `release_flow_lock(PL, EXEC, status)`.
4. Build `map_src`. Count the summary `map` fields.
5. RUN: `write_insert_only(MAP_FQ, map_src, ("legacy_poi_id",), "map")`.
6. Build `info_src`. Compute `present_counts` against `INFO_FQ` (left join on PK, split by `deleted_at`). Block when `cast_fail_n > 0`.
   - RUN: `write_insert_only(INFO_FQ, to_target(info_src.drop("_inactive"), INFO_FQ, ts), ("poi_id",), "info")`.
7. Build `ml_src` with parents. Compute `present_counts`.
   - RUN: `write_insert_only(ML_FQ, to_target(ml_src, ML_FQ, ts), ("poi_id", "lang"), "ml")`.
8. Print the summary JSON and return it with `notebookutils.notebook.exit`.

`write_insert_only(fq, df, pk, tag)` does the following:

1. Asserts `fq.startswith("sgr_visitvn_dev.")`.
2. Asserts `df.groupBy(*pk).count().where("count > 1").count() == 0` (I6).
3. Calls `refresh_flow_lock(PL, EXEC)` and records `v_pre`.
4. Creates temp view `_v_lgp_<tag>` and sets `userMetadata`.
5. Runs `spark.sql(insert_only_sql(fq, view, df.columns, pk))` with no retry.
6. In `finally`, unsets the conf and drops the view.
7. Reads `DESCRIBE HISTORY <fq> LIMIT 1` for `v_post` and `numTargetRowsInserted`.

## Verification

Local, offline, with `pytest`. These are contract tests in the repo's style: they extract cells by id and `exec` the pure SQL builders.

- `tests/test_legacy_gold_poi_init_contract.py`, which needs a scope expansion:
  - `test_sql_merge_target_without_owner_is_unchanged`: the output equals a golden string built from today's function text.
  - `test_sql_merge_target_owner_predicates`: the MATCHED condition ends with `` OR t.`load_origin` IS NOT NULL ``. The update set contains `` t.`load_origin` = CAST(NULL AS STRING) ``. NOT MATCHED BY SOURCE is `` t.`deleted_at` IS NULL AND t.`load_origin` IS NULL ``. The insert list has no `load_origin`.
  - `test_owner_col_constants`: `OWNER_COL == "load_origin"`, it is in `TECH_NAMES`, and it is not in `TECH_COLUMNS`.
  - `test_diff_counts_mirrors_owner`: the text of `diff_counts` references `_t_own` in both `upd` and `dea`.
  - `test_merge_target_passes_owner_only_when_column_present`.
  - `test_insert_only_sql_has_no_update_or_delete`: it contains no `WHEN MATCHED`, `BY SOURCE`, `UPDATE` or `DELETE`.
  - `test_new_poi_id_hash_order`: an AST check of `new_poi_id`. It verifies `uuid_md5(F.lit("google"), source_id)` and `uuid_md5(source_id, F.lit("partner"))`, that the literal `partner_portal` appears only inside `legacy_source_name`, and that `lang` is not referenced.
  - `test_init_write_targets_dev_only`: every write FQ constant starts with `sgr_visitvn_dev.`, every old read goes through `VERSION AS OF`, and no `sgr_visitvn_prd_batch` name appears in a MERGE, INSERT, UPDATE, DELETE or ALTER.
  - `test_legacyid_ddl_cell_contract`: `MAP_COLS` equals the model-design `## Columns` rows for the map, `OWNER == ("load_origin", "STRING")`, the three `OWNER_TABLES`, and the lock id `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`.
- Existing tests that must stay green: `tests/test_enr_poi_contract.py::test_enr_sql_merge_target_keys` and `tests/test_initial_ddl_contract.py::test_poi_entity_columns_derived` (it runs `TECH_NAMES` alone).
- Commands: `python -m pytest tests -q`, then `python scripts/vv.py run-gate 20261119-legacy-gold-poi-init`.

Runtime on DEV, through the runbook, with aggregate SQL only and four-part names:

- **V1 (R1)**: the `DESCRIBE` of the map matches `MAP_COLS`, and `load_origin` is `string` on the three tables.
- **V2 (R2)**: `count(load_origin IS NOT NULL) = 0` on the three tables after a periodic run, the forced `DRY_RUN` baseline is recorded, and the Copy Job is confirmed OK.
- **V3 (R3)**: PLAN summary fields as listed in `## Rollout` R3.
- **V4, before R4**: record `count(*)` and `sum(crc32(concat_ws('|', <pk>, row_hash)))` over rows where `load_origin IS NULL`, for info and multi-lang. Repeat after R5, before any periodic run. The values must be equal, which proves init changed no pipeline row.
- **V5 (R4)**:
  - map rows = old distinct `poi_id` at the pin;
  - inserted equals `to_insert` per table;
  - `count(load_origin = 'LEGACY_INIT')` equals inserted;
  - no `(poi_id)` or `(poi_id, lang)` duplicates on the targets.
- **V6 (R5)**: `inserted = 0` for the map, info and multi-lang.
- **V7 (R6)**:
  - forced `DRY_RUN` `deactivated` stays within the R2 baseline;
  - after a normal run, `count(load_origin = 'LEGACY_INIT' AND deleted_at IS NOT NULL) = 0`;
  - pipeline-row deactivations are in the normal range;
  - any key the run produced has `load_origin` NULL (handover).
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`, then `risk-gate`.
