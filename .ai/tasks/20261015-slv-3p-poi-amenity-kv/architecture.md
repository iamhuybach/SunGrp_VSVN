RESULT: PASS

## Main brief

### Decision
Build `lh_vv_silver.dbo.slv_3p_poi_amenity_kv` as a RECOMPUTE node (`NB_SLV_3P_POI_AMENITY_KV`) on `NB_LIB_TRANSFORM_SLV_GLD`. It reads `slv_3p_poi_amenity` (`poi_id`, `source_flags_json`) and writes by MERGE on `row_hash` with soft delete.
The key is (`poi_id`, `amenity_group`, `amenity_value`); `source_path` is a lineage column. Groups are `general_amenities` and `accessibility`. There are 26 closed rules built from P01/P02-proven keys, including ANY_TRUE `$.parkingOptions` → (`general_amenities`, `parking`).
The node runs in its own flow, `PL_VV_TRANS_SLV_3P_AMENITY_KV_1H` [PROPOSED], with one edge row seeded in `NB_CREATE_DDL`. There is no explicit CREATE TABLE (the library creates the table), no registry row, and no change to the 15P flow.
Risk stays medium. P03 is optional; its expansions are pre-authorized in §16.7.

### Invariants Main must preserve
- Primary key exactly `("poi_id", "amenity_group", "amenity_value")`; `poi_id` copied verbatim from the source.
- Only JSON boolean `true` emits a row. `false`, null, a missing key, or an empty object emit nothing. A group with no hits emits nothing.
- Groups ⊆ {`general_amenities`, `accessibility`}; values match `^[a-z][a-z0-9_]*$`; each (group, value) pair comes from exactly one rule; `amenity_kv_rule_errors()` returns `[]`.
- No rule path equal to, or under, `$.flags.servesWine`, `$.flags.takeout`, or `$.paymentOptions` (MISSING_EVIDENCE).
- `build` selects only `poi_id` and `source_flags_json`. The strings `_crawled_at` and `_event_id` appear nowhere in the node notebook.
- `build` raises before any write on: a NULL `poi_id`, a duplicate `poi_id`, or a non-null `source_flags_json` that is not valid JSON.
- The `kvrules` cell contains no Spark reference (the test `exec`s it).
- The edge seed is idempotent (`WHERE NOT EXISTS` on the logical key) and does not touch the `enrddlpy` cell or the 15P EDGES list. The token `"APPEND"` (double-quoted) is never added.
- `TABLE_CONFIGS_3P` stays unchanged (9 tables, 55 columns).
- Any change to the rules is applied with NB_00 `p_force_nodes = slv_3p_poi_amenity_kv`.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | `.ai/tasks/20261015-slv-3p-poi-amenity-kv/task-state.yaml` | `scope.files` | Add `notebooks/NB_SLV_3P_POI_AMENITY_KV.ipynb`, `notebooks/NB_CREATE_DDL.ipynb`, `tests/test_3p_amenity_kv_contract.py`, `.ai/tasks/20261015-slv-3p-poi-amenity-kv/runtime-runbook.md` (plus `evidence/probes/P03_amenity_child_keys.py` if S2 is taken) | `vv.py verify` task-state PASS |
| 2 | `.ai/tasks/20261015-slv-3p-poi-amenity-kv/decision.md` | `Quyết định hiện hành` row D6 plus history `### D6` | In Vietnamese: rule vocabulary (§5.1), table name, `pl_name` [PROPOSED], MISSING_EVIDENCE list, no schedule yet | ledger has D6 |
| 3 | `notebooks/NB_SLV_3P_POI_AMENITY_KV.ipynb` | cells `kvmd`, `kvparams`, `kvlib` | New notebook; markdown title; parameter cell identical to `NB_SLV_PN_POI` `8c4d8d9c`; `%run NB_LIB_TRANSFORM_SLV_GLD`; metadata copied from `NB_SLV_PN_POI` | file parses as JSON |
| 4 | same | cell `kvrules` | Verbatim from full doc §16.2 | `test_rules_valid_and_proven`, `test_pairs_semantics` pass |
| 5 | same | cell `kvbuild` (`_rule_hit`, `build`, `SPEC`) | Verbatim from full doc §16.3 | `test_node_spec_and_edge_seed` passes |
| 6 | same | cells `kvrun`, `kvexit` | `RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_name, p_trg_fq, p_history_limit)`; `notebookutils.notebook.exit(finish_node(RES))` | same test passes |
| 7 | `notebooks/NB_CREATE_DDL.ipynb` | new cells `kvedgemd` and `kvedgepy` appended after `enrddlpy` | Verbatim from full doc §16.5 | existing `test_enr_poi_contract` and `test_3p_l1_contract` still pass |
| 8 | `tests/test_3p_amenity_kv_contract.py` | new file | Verbatim from full doc §16.6 | 3 tests pass |
| 9 | `.ai/tasks/20261015-slv-3p-poi-amenity-kv/runtime-runbook.md` | all template sections | Vietnamese runbook: V0–V6 (§15), V4 check cell (§16.4), rollback and forward recovery (§17) with exact SQL | Status `CHỜ CHẠY` |
| 10 | `.ai/tasks/20261015-slv-3p-poi-amenity-kv/evidence/probes/P03_amenity_child_keys.py` (optional) | new file | Spec in §16.7 | user output saved under `evidence/results/` |

### Order and stop points
1. Rows 1–2 (scope, D6).
2. **Stop S2 — user decision, optional evidence.** Ask the user whether `servesWine`, `takeout`, payment, and parking-child tokens are wanted in this task. If yes: write P03 (row 10); the user runs it in DEV; apply only the pre-authorized expansions in §16.7 and update the rules, MISSING list, test sets, and count. If no: continue with 26 rules.
3. Rows 3–8.
4. Run local tests and `vv.py verify`. **Stop** on any FAIL; fix before review.
5. Row 9 (runbook), then `run-gate` review (`sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`). **Stop** until there is no open P0/P1.
6. **Stop S4 — user runtime evidence.** The user imports the notebook to DEV, runs `kvedgepy`, then V1–V6 and records the results in the runbook.
7. **Stop S5 — user decision.** Scheduling: clone a Fabric pipeline named `PL_VV_TRANS_SLV_3P_AMENITY_KV_1H` that calls NB_00, or keep runs manual. This is out of scope for this task; record it as backlog.

### Tests and verification
- `python -m pytest -q tests/test_3p_amenity_kv_contract.py::test_rules_valid_and_proven tests/test_3p_amenity_kv_contract.py::test_pairs_semantics tests/test_3p_amenity_kv_contract.py::test_node_spec_and_edge_seed`
- Regression: `python -m pytest -q tests/test_3p_l1_contract.py tests/test_enr_poi_contract.py`
- `python scripts/vv.py verify 20261015-slv-3p-poi-amenity-kv`
- Runtime (user, DEV), from §15:
  - V0: `kvedgepy` run twice leaves one row.
  - V1: NB_00 `PLAN` with `p_pl_name = PL_VV_TRANS_SLV_3P_AMENITY_KV_1H`.
  - V2: `RUN` gives SUCCESS.
  - V3: second `RUN` gives `NO_DATA` and the target version is unchanged.
  - V4: check cell prints `VERDICT PASS` (missing 0, extra 0, pk_dup 0).
  - V5: `p_force_nodes = slv_3p_poi_amenity_kv` gives 0/0/0 and no new commit.
  - V6: rollback, then forward recovery.

### Read only if needed
- §3 Invariants, §5 Grain, keys, and schema, §5.1 Rule table → rows 2, 4, 5, 8
- §14 Alternatives and trade-offs → row 2 (D6 rationale), row 7 (separate flow)
- §16.2 Cell `kvrules` → row 4
- §16.3 Cell `kvbuild` → row 5
- §16.4 V4 check cell → row 9
- §16.5 `NB_CREATE_DDL.ipynb` new cells → row 7
- §16.6 Test file → row 8
- §16.7 Optional evidence P03 → row 10, stop S2
- §7 Commit boundaries, §8 Idempotency, §9 Concurrency, §10 Retry and recovery, §11 Partial failure → row 9 and review answers
- §12 Observability → row 9
- §17 Rollout, rollback, and forward recovery → row 9, stops S4 and S5

# Architecture — 20261015-slv-3p-poi-amenity-kv

Risk stays `medium`. The design is a keyed silver projection written by MERGE on `row_hash`, with soft delete. It does not append history and does not overwrite `slv_3p_poi_amenity`. `risk-gate` is not triggered.

## 1. Scope

- New node table `lh_vv_silver.dbo.slv_3p_poi_amenity_kv`, built by the existing recompute library (`NB_LIB_TRANSFORM_SLV_GLD`, `load_mode = 'RECOMPUTE'`) from `lh_vv_silver.dbo.slv_3p_poi_amenity.source_flags_json`.
- New node notebook `notebooks/NB_SLV_3P_POI_AMENITY_KV.ipynb` (one notebook per target table, `nb_name` set explicitly).
- One new `ctrl_mng_pipeline_config` edge row, seeded from a new cell in `notebooks/NB_CREATE_DDL.ipynb`, under a new flow `PL_VV_TRANS_SLV_3P_AMENITY_KV_1H` [PROPOSED].
- A closed rule table, `AMENITY_KV_RULES`, derived only from keys proven by P01/P02 and from rules documented in `get_amenity.md` and `poi_amenity_mapping.md`.
- Contract test `tests/test_3p_amenity_kv_contract.py`. Vietnamese `runtime-runbook.md`. Decision D6 in `decision.md`.

## 2. Non-goals

- No change to `slv_3p_poi_amenity`, its registry entry, or `TABLE_CONFIGS_3P` (the 9-table/55-column contract in `tests/test_3p_l1_contract.py` stays unchanged).
- No change to `PL_VV_TRANS_SLV_TO_ENR_15P` edges, `gld_enr_*`, or the partner flow.
- No `ctrl_cfg_schema_registry` rows. The registry drives extract only, and RECOMPUTE nodes do not read it (precedent: `slv_pn_poi`).
- No explicit `CREATE TABLE`. `run_node` → `ensure_target` creates the table from the build schema, which keeps a single source of schema truth (precedent: `slv_pn_poi`).
- No sector filtering (`detect_category`), no `terms_and_conditions`, no `amenities[]` string rules (`gym`, `pool`, `spa`, `wifi`, `restaurant`, `bar`), no display tags, no internal OR-merged fields (`fnb_*`, `has_*`, `hotel_*`).
- No `false` tags. `get_amenity.md` emits `accessibility_options_*:false`; the request's rule that `false` emits no row overrides it.
- No Fabric pipeline or schedule. Scheduling is a later user decision (§13, stop S5).

## 3. Invariants

- I1. Grain is one row per (`poi_id`, `amenity_group`, `amenity_value`). The QG `pk_duplicate` check blocks any duplicate before MERGE.
- I2. `poi_id` is copied verbatim from `slv_3p_poi_amenity.poi_id`. No hashing and no new ID.
- I3. A row exists (live, `deleted_at IS NULL`) if and only if a rule in `AMENITY_KV_RULES` evaluates true on the source JSON at the version the node read. JSON `false`, JSON `null`, a missing key, a null parent object, or an empty object produce no row. A group with no hits produces no row.
- I4. Groups are a closed set: `general_amenities` and `accessibility`. Values match `^[a-z][a-z0-9_]*$`. Each (`group`, `value`) pair comes from exactly one rule.
- I5. A rule is active only when its source key was proven in P01/P02. The paths in `AMENITY_KV_MISSING_EVIDENCE` never emit.
- I6. Rerunning on the same source version gives `inserted = updated = deactivated = 0` and no Delta commit on the target.
- I7. Only the cell's business columns are hashed: `poi_id`, `amenity_group`, `amenity_value`, `source_path`. Crawl-audit columns of the source are not read, so a recrawl with unchanged flags does not move `updated_at`.
- I8. The node fails before writing when the input has a NULL `poi_id`, a duplicate `poi_id`, or a non-null `source_flags_json` that is not valid JSON.
- I9. Only this node writes the target, and only under the lock of its own flow.
- I10. Any change to `AMENITY_KV_RULES` is applied by an NB_00 run with `p_force_nodes = slv_3p_poi_amenity_kv`. A code change alone does not dirty any edge.

## 4. State ownership

| State | Owner | Writer |
|---|---|---|
| `slv_3p_poi_amenity` (input) | 3P extract | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` (read-only here) |
| `slv_3p_poi_amenity_kv` | this node | `run_node` MERGE in `NB_SLV_3P_POI_AMENITY_KV` |
| Edge config row | `NB_CREATE_DDL` new cell `kvedgepy` | user runs once |
| `wm_e__slv_3p_poi_amenity_kv__slv_3p_poi_amenity`, `wm_flow__PL_VV_TRANS_SLV_3P_AMENITY_KV_1H` | NB_00 (`orchestrate`) | created on first run; the node never writes them |
| `ctrl_log_run` | NB_00 | one row per run |
| `ctrl_log_table_run` | node | one row per node execution |
| Rule vocabulary | notebook cell `kvrules` (D6) | Main |

## 5. Grain, keys, and schema

Target columns, in build order: `poi_id STRING`, `amenity_group STRING`, `amenity_value STRING`, `source_path STRING`. The library then adds `row_hash STRING`, `created_at`, `updated_at`, `deleted_at TIMESTAMP`.

- MERGE key `pk = ("poi_id", "amenity_group", "amenity_value")`.
- `source_path` is lineage, for example `$.flags.dineIn` or `$.parkingOptions`. It is functionally dependent on the key under I4.
- Consumers read live rows with `deleted_at IS NULL`. Tombstoned keys reactivate in place, so a key never appears twice, live or dead.
- Input grain is one row per `poi_id` (registry key; asserted at runtime by I8).

### 5.1 Rule table (D6)

Value tokens are the snake_case Google key. This matches `get_amenity.md` Step 2 and the `poi_amenity_mapping.md` §7.1 strings. The one documented exception is `restroom` → `has_restroom` (`get_amenity.md`). `parking` is the §7.1 string for `has_parking`, and §7.3 says that any `parkingOptions` key set to true sets `has_parking`. This produces the user's (`general_amenities`, `parking`) pair. The `accessibility` group is backed by D3 and by the §7.1 group "Accessibility". Every other token goes to `general_amenities`, where `get_amenity.md` Step 4 places all such tags.

| kind | json_path | group | value |
|---|---|---|---|
| FLAG | `$.flags.<k>` for the 21 P02-proven `k` | `general_amenities` | snake_case(`k`); `restroom` → `has_restroom` |
| ANY_TRUE | `$.parkingOptions` (P01 top-level, 57/57) | `general_amenities` | `parking` |
| FLAG | `$.accessibilityOptions.wheelchairAccessible{Entrance,Parking,Restroom,Seating}` | `accessibility` | `wheelchair_accessible_{entrance,parking,restroom,seating}` |

MISSING_EVIDENCE: `$.flags.servesWine` and `$.flags.takeout` were in the truncated 20 tokens of P02, and the child keys of `$.paymentOptions` are unproven. `$.parkingOptions` child tokens are also unproven, but the ANY_TRUE rule does not need their names. `evChargeOptions` and `fuelOptions` have no documented object rule, so they get no rule. §7.1 `amenities[]` strings have no source key.

## 6. Ordering

- Order is by key only. The build is a pure function of one source snapshot, and no row depends on another.
- The source is read with `VERSION AS OF` at the pinned version. NB_00 pins external inputs to the last completed extract batch, so a half-written extract batch is never read.
- On the first run the target does not exist, so the node runs regardless of the edge state.

## 7. Transaction and commit boundaries

| # | Commit | Atomicity |
|---|---|---|
| C0 | First RUN only: `CREATE TABLE` (`ensure_target`) | Delta commit |
| C1 | Target MERGE (insert, update, soft delete) | single Delta commit; skipped when the diff is 0 |
| C2 | `ctrl_log_table_run` append (node `finally`) | separate |
| C3 | Edge watermark advance (NB_00 `advance_edges`) | separate, only after the node reports SUCCESS or NO_DATA |
| C4 | Run-log close and lock release | separate |

There is no cross-table transaction. Correctness relies on idempotent recompute: a crash after C0 or C1 but before C3 leaves the edge un-advanced, so the next run recomputes, finds diff 0 or the remaining delta, and then advances.

## 8. Idempotency

- Full recompute from one snapshot, then MERGE that updates only when `row_hash` differs or the row is tombstoned. The same input therefore gives diff 0, MERGE is skipped, and there is no commit (I6).
- The edge is unchanged, so NB_00 reports `NO_DATA` with zero node work.
- A forced rerun (`p_force_nodes`) on the same input still gives diff 0 and no commit.
- `kvedgepy` is idempotent through `INSERT ... WHERE NOT EXISTS` on the logical key (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`).

## 9. Concurrency

- Flow lock `wm_flow__PL_VV_TRANS_SLV_3P_AMENITY_KV_1H`. A second NB_00 gets `SKIPPED_CONCURRENT`. A manual node RUN while NB_00 holds the lock is refused, and only DRY_RUN is allowed.
- The extract may commit to the source during a run. The node reads its pinned version, so it is unaffected. A commit after pinning makes the edge dirty for the next run.
- `build_dag` rejects a node owned by more than one active `pl_name`, which enforces a single writer.
- Inherited library limitation (`NB_LIB_TRANSFORM_SLV_GLD.md` §6): a run that lost its lock to timeout can still MERGE. Mitigation: `p_lock_timeout_min > p_dag_timeout_min + 5` (validated by `_validate_orch_params`). The runbook uses the defaults (`p_lock_timeout_min = 90` > `p_dag_timeout_min = 45` + 5). Accepted, not changed here.

## 10. Retry and recovery

- Transient Delta or connection errors on MERGE: `with_retry` (6 attempts with jitter) inside `merge_target`.
- runMultiple `retry = 0`. A failed node leaves its edge un-advanced, and the next NB_00 run recomputes it automatically.
- There is no pipeline retry because no pipeline exists yet. The operator reruns NB_00.
- Rule fix: edit `kvrules`, then run NB_00 with `p_force_nodes = slv_3p_poi_amenity_kv` (I10).

## 11. Partial failure

| Failure | Effect | Recovery |
|---|---|---|
| Input empty | `required_inputs` QG blocks; no MERGE; no mass soft delete | rerun after the extract refills the table |
| Input contract break (I8) | `QualityGateError` from `build`; node FAILED; target untouched | fix L1 data, rerun |
| Rule-constant error | `ConfigError` from `build` before any write | fix the constant |
| MERGE fails | Delta atomic, nothing committed | automatic recompute next run |
| Crash after C1, before C3 | target already correct, edge stale | next run: diff 0, edge advances |
| Rule regression soft-deletes many rows | reversible: the corrected rerun reactivates rows (`deleted_at = NULL`) and keeps `created_at` | fix the rules, force rerun; `output_empty` warning flags the extreme case |
| `parkingOptions` not an object | no `parking` row for that POI; `parking_options_unparsed` warning counts it | evidence plus a rule change if needed |

## 12. Observability

- `ctrl_log_table_run` per execution: `status`, `entity_rows`, `inserted_rows`, `updated_rows`, `deactivated_rows`, `src_versions_json` (source version read), `trg_version`, `error_message`.
- `qg_json` also carries:
  - `metrics.input_rows`, `metrics.output_rows`, `metrics.rows_by_group`.
  - `warns.source_json_null`, `warns.parking_options_unparsed`, `warns.output_empty`.
  - `blocks.pk_null`, `blocks.pk_duplicate`.
- `ctrl_log_run` per flow run: `status`, `read_note` (plan summary).
- The runbook's read-only check (§15 V4) compares live rows with a pure-Python oracle (`amenity_kv_pairs`) at the exact source version the node read.

## 13. Security and data handling

- Amenity flags are POI business attributes, not personal data. The check scripts print counts only: no `poi_id` lists and no JSON values.
- SQL contains only constant identifiers. No user input is concatenated into SQL.
- No secrets. No new access paths: same Lakehouses and same `lh_vv_ctrl` tables as the 15P flow.

## 14. Alternatives and trade-offs

| Decision | Selected | Rejected and why |
|---|---|---|
| Engine | RECOMPUTE node on `NB_LIB_TRANSFORM_SLV_GLD` | (a) Extend the L1 extract with an explode load mode: violates "L1 extracts 1:1, business rules in L2" and changes the shared extract library. (b) Standalone notebook with its own MERGE: reimplements locking, version pinning, logs, and QG. |
| Write mode | MERGE by `row_hash` plus soft delete | Full overwrite: churns `created_at`, gives no diff counts, and raises risk to high. Append: breaks the no-duplicate-key requirement. |
| Flow placement | New `pl_name` `PL_VV_TRANS_SLV_3P_AMENITY_KV_1H`, run manually through `NB_00_ORCHES_SLV_TO_GLD` | Add a 14th edge to `PL_VV_TRANS_SLV_TO_ENR_15P`: free scheduling, but a node failure would turn the gold enrichment run `PARTIAL_FAILED` and couple rollback to the enr flow, which is outside this task. Trade-off: the table is not refreshed automatically until the user decides scheduling (S5). |
| Vocabulary | Snake_case Google key, plus `parking` and `has_restroom` | Internal fields (`fnb_dine_in`, `has_parking`): OR-merges lose information, and the user's example tokens are §7.1 strings. Display tags: out of scope. |
| Key | Natural composite (`poi_id`, `group`, `value`) | Surrogate hash ID: adds nothing because the library MERGE accepts composite keys. |
| Empty-output guard | Warning only | Block: a legitimate "all flags false" state could never be applied, and a wrong soft delete is reversible. |
| Truthiness in Spark | `get_json_object(path) = 'true'`; ANY_TRUE via `from_json(..., 'map<string,string>')` + `exists` | Typed `from_json` struct or boolean map: a single non-boolean child nulls the whole parse. Known divergence: Spark also accepts the JSON string `"true"`, which P02 never observed for proven paths, while the oracle accepts only a boolean. V4 surfaces any divergence. |

## 15. Verification

Local checks (no Spark):

- `python -m pytest -q tests/test_3p_amenity_kv_contract.py tests/test_3p_l1_contract.py tests/test_enr_poi_contract.py`
- `python scripts/vv.py verify 20261015-slv-3p-poi-amenity-kv`

Runtime checks in Fabric DEV (Main writes these into `runtime-runbook.md`, in Vietnamese):

| ID | Step | Pass |
|---|---|---|
| V0 | Run cell `kvedgepy` twice | one row for `trg_tbl = 'slv_3p_poi_amenity_kv'`, `is_active = 1`, `load_mode = 'RECOMPUTE'`, `nb_name = 'NB_SLV_3P_POI_AMENITY_KV'` |
| V1 | `NB_00_ORCHES_SLV_TO_GLD` with `p_pl_name = PL_VV_TRANS_SLV_3P_AMENITY_KV_1H`, `p_mode = PLAN` | plan lists one candidate, `slv_3p_poi_amenity_kv`, with reason "no target table" |
| V2 | Same, `p_mode = RUN` | run SUCCESS; node SUCCESS; `inserted_rows = output_rows`; `blocks` all 0 |
| V3 | Same, `RUN` again | run `NO_DATA`; target `DESCRIBE HISTORY` version unchanged |
| V4 | Read-only check: paste cell `kvrules` into cell 1 of a scratch notebook and the check cell (§16.4) into cell 2 | `missing = 0`, `extra = 0`, `pk_dup = 0`, groups ⊆ {`general_amenities`, `accessibility`}; prints per-group counts and the count of POIs with `parking` |
| V5 | RUN with `p_force_nodes = slv_3p_poi_amenity_kv` | node SUCCESS with 0/0/0; target version unchanged |
| V6 | Rollback (§17), then forward recovery | table absent, config row absent; after re-seed plus RUN, V2 holds again |

## 16. Implementation plan

### 16.1 Notebook `notebooks/NB_SLV_3P_POI_AMENITY_KV.ipynb`

Cells in this order, using the same metadata and kernel as `NB_SLV_PN_POI.ipynb`:

1. `kvmd` (markdown): `# NB_SLV_3P_POI_AMENITY_KV`, followed by one line: RECOMPUTE `lh_vv_silver.dbo.slv_3p_poi_amenity_kv` from `slv_3p_poi_amenity.source_flags_json`; when the rules change, run NB_00 with `p_force_nodes = slv_3p_poi_amenity_kv`.
2. `kvparams`: the parameter cell, identical to `NB_SLV_PN_POI` cell `8c4d8d9c`.
3. `kvlib`: `%run NB_LIB_TRANSFORM_SLV_GLD`.
4. `kvrules`: the code in §16.2. It must not reference Spark, so the test can `exec` it.
5. `kvbuild`: the code in §16.3.
6. `kvrun`: `RES = run_node(SPEC, p_exec_id, p_run_id, p_pinned_json, p_mode, p_force, p_pl_name, p_trg_fq, p_history_limit)`
7. `kvexit`: `notebookutils.notebook.exit(finish_node(RES))`

### 16.2 Cell `kvrules`

```python
# [THÊM 15/10] Rule gom nhóm amenity cho slv_3p_poi_amenity_kv (decision D6).
# Cell này không dùng Spark để test local exec được.
# Nguồn: get_amenity.md Bước 2 (camelCase -> snake_case, restroom -> has_restroom);
#        poi_amenity_mapping.md 7.1 (chuỗi parking, wheelchair_accessible_*, nhóm Accessibility), 7.3 (parkingOptions).
# Chỉ dùng khóa đã thấy ở P01 / P02. Khóa chưa có bằng chứng nằm ở AMENITY_KV_MISSING_EVIDENCE, không sinh dòng.
# FLAG: giá trị JSON tại path là true. ANY_TRUE: object tại path có ít nhất 1 khóa con true.
# false, null, thiếu khóa, object rỗng: không sinh dòng.
import json
import re

AMENITY_KV_GROUPS = ("general_amenities", "accessibility")
AMENITY_KV_RULES = (
    # (kind, json_path, amenity_group, amenity_value)
    ("FLAG", "$.flags.allowsDogs", "general_amenities", "allows_dogs"),
    ("FLAG", "$.flags.curbsidePickup", "general_amenities", "curbside_pickup"),
    ("FLAG", "$.flags.delivery", "general_amenities", "delivery"),
    ("FLAG", "$.flags.dineIn", "general_amenities", "dine_in"),
    ("FLAG", "$.flags.goodForChildren", "general_amenities", "good_for_children"),
    ("FLAG", "$.flags.goodForGroups", "general_amenities", "good_for_groups"),
    ("FLAG", "$.flags.goodForWatchingSports", "general_amenities", "good_for_watching_sports"),
    ("FLAG", "$.flags.liveMusic", "general_amenities", "live_music"),
    ("FLAG", "$.flags.menuForChildren", "general_amenities", "menu_for_children"),
    ("FLAG", "$.flags.outdoorSeating", "general_amenities", "outdoor_seating"),
    ("FLAG", "$.flags.reservable", "general_amenities", "reservable"),
    ("FLAG", "$.flags.restroom", "general_amenities", "has_restroom"),
    ("FLAG", "$.flags.servesBeer", "general_amenities", "serves_beer"),
    ("FLAG", "$.flags.servesBreakfast", "general_amenities", "serves_breakfast"),
    ("FLAG", "$.flags.servesBrunch", "general_amenities", "serves_brunch"),
    ("FLAG", "$.flags.servesCocktails", "general_amenities", "serves_cocktails"),
    ("FLAG", "$.flags.servesCoffee", "general_amenities", "serves_coffee"),
    ("FLAG", "$.flags.servesDessert", "general_amenities", "serves_dessert"),
    ("FLAG", "$.flags.servesDinner", "general_amenities", "serves_dinner"),
    ("FLAG", "$.flags.servesLunch", "general_amenities", "serves_lunch"),
    ("FLAG", "$.flags.servesVegetarianFood", "general_amenities", "serves_vegetarian_food"),
    ("ANY_TRUE", "$.parkingOptions", "general_amenities", "parking"),
    ("FLAG", "$.accessibilityOptions.wheelchairAccessibleEntrance", "accessibility", "wheelchair_accessible_entrance"),
    ("FLAG", "$.accessibilityOptions.wheelchairAccessibleParking", "accessibility", "wheelchair_accessible_parking"),
    ("FLAG", "$.accessibilityOptions.wheelchairAccessibleRestroom", "accessibility", "wheelchair_accessible_restroom"),
    ("FLAG", "$.accessibilityOptions.wheelchairAccessibleSeating", "accessibility", "wheelchair_accessible_seating"),
)
# P02 cắt 20 token khóa con: servesWine, takeout và khóa con paymentOptions chưa có bằng chứng.
AMENITY_KV_MISSING_EVIDENCE = ("$.flags.servesWine", "$.flags.takeout", "$.paymentOptions")


def amenity_kv_rule_errors(rules=AMENITY_KV_RULES) -> list:
    """Kiểm tra bảng rule trước khi build.

    Input : rules — tuple (kind, json_path, amenity_group, amenity_value)
    Output: list lỗi, rỗng = hợp lệ
    Ví dụ : amenity_kv_rule_errors() -> []
    """
    errs, seen = [], set()
    for kind, path, group, value in rules:
        if kind not in ("FLAG", "ANY_TRUE"):
            errs.append(f"{path}: kind {kind}")
        if group not in AMENITY_KV_GROUPS:
            errs.append(f"{path}: nhóm {group}")
        if not re.fullmatch(r"[a-z][a-z0-9_]*", value or ""):
            errs.append(f"{path}: giá trị {value}")
        if not path.startswith("$.") or any(path == m or path.startswith(m + ".") for m in AMENITY_KV_MISSING_EVIDENCE):
            errs.append(f"{path}: path chưa có bằng chứng")
        if (group, value) in seen:
            errs.append(f"{path}: trùng ({group}, {value})")
        seen.add((group, value))
    return errs


def amenity_kv_pairs(text) -> list:
    """Cặp mà rule sinh cho một source_flags_json. Dùng cho test local và kiểm chứng runtime (V4).

    Input : text — chuỗi JSON hoặc None
    Output: list (amenity_group, amenity_value, source_path) đã sắp xếp
    Ví dụ : amenity_kv_pairs('{"flags": {"dineIn": true}}') -> [("general_amenities", "dine_in", "$.flags.dineIn")]
    """
    if text is None:
        return []
    root = json.loads(text)
    out = []
    for kind, path, group, value in AMENITY_KV_RULES:
        node = root
        for part in path[2:].split("."):
            node = node.get(part) if isinstance(node, dict) else None
        if kind == "FLAG":
            hit = node is True
        else:
            hit = isinstance(node, dict) and any(v is True for v in node.values())
        if hit:
            out.append((group, value, path))
    return sorted(out)
```

### 16.3 Cell `kvbuild`

```python
def _rule_hit(src: Column, kind: str, path: str) -> Column:
    """Điều kiện một rule khớp trên cột JSON, cùng nghĩa với amenity_kv_pairs.

    Input : src — cột source_flags_json; kind — FLAG | ANY_TRUE; path — JSON path
    Output: Column boolean, không NULL
    Ví dụ : _rule_hit(F.col("source_flags_json"), "FLAG", "$.flags.dineIn")
    """
    if kind == "FLAG":
        hit = F.get_json_object(src, path) == F.lit("true")
    else:
        child = F.from_json(F.get_json_object(src, path), "map<string,string>")
        hit = F.exists(F.map_values(child), lambda v: v == F.lit("true"))
    return F.coalesce(hit, F.lit(False))


def build(ctx: NodeContext) -> DataFrame:
    # D6 — rule ở cell kvrules. poi_id copy từ slv_3p_poi_amenity. Không lọc ngành vì bảng nguồn không có types.
    # Chỉ đọc poi_id và source_flags_json: cột audit crawl đổi mỗi lần crawl, không đưa vào row_hash.
    bad_rules = amenity_kv_rule_errors()
    if bad_rules:
        raise ConfigError(f"AMENITY_KV_RULES sai: {bad_rules}")
    src = ctx.input("amenity").select("poi_id", "source_flags_json")
    js = F.col("source_flags_json")
    parking = F.get_json_object(js, "$.parkingOptions")
    st = src.agg(
        F.count(F.lit(1)).alias("rows"),
        F.countDistinct("poi_id").alias("pois"),
        F.sum(F.when(F.col("poi_id").isNull(), 1).otherwise(0)).alias("poi_null"),
        F.sum(F.when(js.isNull(), 1).otherwise(0)).alias("json_null"),
        F.sum(F.when(js.isNotNull() & F.get_json_object(js, "$").isNull(), 1).otherwise(0)).alias("json_bad"),
        F.sum(F.when(parking.isNotNull() & F.from_json(parking, "map<string,string>").isNull(), 1)
              .otherwise(0)).alias("parking_unparsed"),
    ).first()
    poi_null, json_bad = int(st["poi_null"] or 0), int(st["json_bad"] or 0)
    dup = int(st["rows"]) - poi_null - int(st["pois"])
    if poi_null or json_bad or dup:
        raise QualityGateError(f"Đầu vào amenity lỗi: poi_id NULL {poi_null}, JSON hỏng {json_bad}, poi_id trùng {dup}")
    ctx.warn("source_json_null", st["json_null"])
    ctx.warn("parking_options_unparsed", st["parking_unparsed"])
    entries = [
        F.when(_rule_hit(js, kind, path), F.struct(
            F.lit(group).alias("amenity_group"), F.lit(value).alias("amenity_value"), F.lit(path).alias("source_path")))
        for kind, path, group, value in AMENITY_KV_RULES
    ]
    out = (src.select("poi_id", F.explode(F.filter(F.array(*entries), lambda e: e.isNotNull())).alias("kv"))
           .select("poi_id", "kv.amenity_group", "kv.amenity_value", "kv.source_path"))
    by_group = {r["amenity_group"]: int(r["count"]) for r in out.groupBy("amenity_group").count().collect()}
    ctx.metrics.update(input_rows=int(st["rows"]), output_rows=sum(by_group.values()), rows_by_group=by_group)
    ctx.warn("output_empty", 1 if int(st["rows"]) and not by_group else 0)
    return out


SPEC = NodeSpec(
    trg_tbl="slv_3p_poi_amenity_kv",
    inputs={"amenity": "slv_3p_poi_amenity"},
    pk=("poi_id", "amenity_group", "amenity_value"),
    build=build,
    required_inputs=("amenity",),
    write_mode="MERGE",
)
```

`Column`, `F`, `ConfigError`, `QualityGateError`, `NodeContext`, `NodeSpec`, and `DataFrame` come from the `%run` library (`_hash_expr` already uses `Column`). Do not mention the source's audit-column names anywhere in this notebook; the test asserts they are absent.

### 16.4 V4 check cell (for the runbook, read-only, counts only)

```python
# Kiểm chứng V4: so dòng live với amenity_kv_pairs tại đúng version node đã đọc. Chỉ in số đếm.
import json as _json
log_row = spark.sql("""
    SELECT src_versions_json FROM lh_vv_ctrl.dbo.ctrl_log_table_run
    WHERE trg_tbl = 'slv_3p_poi_amenity_kv' AND status = 'SUCCESS'
    ORDER BY ended_at DESC LIMIT 1""").first()
ver = _json.loads(log_row["src_versions_json"])["lh_vv_silver.dbo.slv_3p_poi_amenity"]["v"]
rows = spark.sql(f"SELECT poi_id, source_flags_json FROM lh_vv_silver.dbo.slv_3p_poi_amenity VERSION AS OF {int(ver)}").collect()
expected = {(r["poi_id"], g, v, p) for r in rows for g, v, p in amenity_kv_pairs(r["source_flags_json"])}
live = {tuple(x) for x in spark.sql("""SELECT poi_id, amenity_group, amenity_value, source_path
    FROM lh_vv_silver.dbo.slv_3p_poi_amenity_kv WHERE deleted_at IS NULL""").collect()}
dup = spark.sql("""SELECT COUNT(*) AS n FROM (SELECT poi_id, amenity_group, amenity_value
    FROM lh_vv_silver.dbo.slv_3p_poi_amenity_kv GROUP BY 1, 2, 3 HAVING COUNT(*) > 1)""").first()["n"]
print("SOURCE_VERSION", ver, "SOURCE_ROWS", len(rows))
print("EXPECTED", len(expected), "LIVE", len(live), "missing", len(expected - live), "extra", len(live - expected), "pk_dup", dup)
for g in sorted({k[1] for k in live}):
    print("GROUP", g, sum(1 for k in live if k[1] == g))
print("PARKING_POIS", sum(1 for k in live if k[1:3] == ("general_amenities", "parking")))
print("VERDICT", "PASS" if expected == live and dup == 0 else "FAIL")
```

### 16.5 `NB_CREATE_DDL.ipynb`: new cells after `enrddlpy` (the last cell)

Markdown cell `kvedgemd`: `# [THÊM 15/10] Cạnh RECOMPUTE slv_3p_poi_amenity_kv`. Code cell `kvedgepy`, Python, same metadata as `enrddlpy`:

```python
# [THÊM 15/10] Cạnh RECOMPUTE slv_3p_poi_amenity -> slv_3p_poi_amenity_kv, luồng riêng PL_VV_TRANS_SLV_3P_AMENITY_KV_1H.
# Luồng riêng để node lỗi không làm PL_VV_TRANS_SLV_TO_ENR_15P báo lỗi. Chạy sau cell [THÊM 13/10] (cần cột nb_name).
# Idempotent: INSERT WHERE NOT EXISTS theo khóa logic. Không tạo bảng đích: run_node tạo từ schema build ở lần RUN đầu.
# Không seed watermark: NB_00 tự tạo dòng khóa và dòng cạnh. Không thêm ctrl_cfg_schema_registry: registry chỉ cho extract.
cols = {row.col_name.lower() for row in spark.sql("DESCRIBE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config").collect()}
if "nb_name" not in cols:
    raise RuntimeError("Thiếu cột nb_name: chạy cell [THÊM 13/10] trước")
spark.sql("""
INSERT INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
    (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)
SELECT
    COALESCE((SELECT MAX(id) FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config), 0) + t.seq AS id,
    'PL_VV_TRANS_SLV_3P_AMENITY_KV_1H' AS pl_name,
    'lh_vv_silver.dbo' AS src_schema,
    'slv_3p_poi_amenity' AS src_tbl,
    'lh_vv_silver.dbo' AS trg_schema,
    'slv_3p_poi_amenity_kv' AS trg_tbl,
    1 AS is_active,
    1 AS priority,
    'RECOMPUTE' AS load_mode,
    CAST(NULL AS STRING) AS align_path,
    CAST(NULL AS STRING) AS dedup_order,
    'NB_SLV_3P_POI_AMENITY_KV' AS nb_name
FROM VALUES (1) AS t(seq)
WHERE NOT EXISTS (
    SELECT 1 FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config c
    WHERE c.pl_name = 'PL_VV_TRANS_SLV_3P_AMENITY_KV_1H'
      AND c.src_schema = 'lh_vv_silver.dbo' AND c.src_tbl = 'slv_3p_poi_amenity'
      AND c.trg_schema = 'lh_vv_silver.dbo' AND c.trg_tbl = 'slv_3p_poi_amenity_kv'
)
""")
spark.sql("""
SELECT id, pl_name, src_tbl, trg_tbl, is_active, load_mode, nb_name
FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
WHERE trg_tbl = 'slv_3p_poi_amenity_kv'
""").show(truncate=False)
```

Do not add `"APPEND"` (double-quoted) anywhere in this cell; `test_enr_poi_contract` counts that token.

### 16.6 Test `tests/test_3p_amenity_kv_contract.py`

```python
"""Contract of slv_3p_poi_amenity_kv. No Spark."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NB = "NB_SLV_3P_POI_AMENITY_KV.ipynb"
PL = "PL_VV_TRANS_SLV_3P_AMENITY_KV_1H"
# evidence/results/P01_amenity_json_keys.txt and P02_amenity_enum_groups.txt
P01_TOP = {"flags", "accessibilityOptions", "evChargeOptions", "fuelOptions", "parkingOptions", "paymentOptions"}
P02_FLAGS = {
    "allowsDogs", "curbsidePickup", "delivery", "dineIn", "goodForChildren", "goodForGroups",
    "goodForWatchingSports", "liveMusic", "menuForChildren", "outdoorSeating", "reservable", "restroom",
    "servesBeer", "servesBreakfast", "servesBrunch", "servesCocktails", "servesCoffee", "servesDessert",
    "servesDinner", "servesLunch", "servesVegetarianFood",
}
P02_ACCESSIBILITY = {
    "wheelchairAccessibleEntrance", "wheelchairAccessibleParking",
    "wheelchairAccessibleRestroom", "wheelchairAccessibleSeating",
}


def _cells(name: str) -> list:
    nb = json.loads((ROOT / "notebooks" / name).read_text(encoding="utf-8"))
    return ["".join(cell["source"]) for cell in nb["cells"]]


def _rules() -> dict:
    cell = next(c for c in _cells(NB) if "AMENITY_KV_RULES = (" in c)
    ns: dict = {}
    exec(cell, ns)  # noqa: S102 - project source, no Spark
    return ns


def test_rules_valid_and_proven():
    ns = _rules()
    assert ns["amenity_kv_rule_errors"]() == []
    assert ns["AMENITY_KV_GROUPS"] == ("general_amenities", "accessibility")
    rules = ns["AMENITY_KV_RULES"]
    assert len(rules) == 26
    for kind, path, group, value in rules:
        parts = path[2:].split(".")
        assert parts[0] in P01_TOP
        if parts[0] == "flags":
            assert kind == "FLAG" and parts[1] in P02_FLAGS and group == "general_amenities"
        elif parts[0] == "accessibilityOptions":
            assert kind == "FLAG" and parts[1] in P02_ACCESSIBILITY and group == "accessibility"
        else:
            assert (kind, path, group, value) == ("ANY_TRUE", "$.parkingOptions", "general_amenities", "parking")
    assert "terms_and_conditions" not in json.dumps(rules)
    bad = ns["amenity_kv_rule_errors"]((("FLAG", "$.flags.takeout", "general_amenities", "takeout"),))
    assert bad and "bằng chứng" in bad[0]


def test_pairs_semantics():
    pairs = _rules()["amenity_kv_pairs"]
    doc = {
        "flags": {"dineIn": True, "servesBeer": False, "liveMusic": None, "servesWine": True},
        "parkingOptions": {"freeParkingLot": False, "paidStreetParking": True},
        "accessibilityOptions": None, "paymentOptions": {"acceptsNfc": True}, "evChargeOptions": None,
    }
    assert pairs(json.dumps(doc)) == [
        ("general_amenities", "dine_in", "$.flags.dineIn"),
        ("general_amenities", "parking", "$.parkingOptions"),
    ]
    assert pairs(json.dumps({"parkingOptions": {"freeParkingLot": False}})) == []
    assert pairs(json.dumps({"parkingOptions": {}})) == []
    assert pairs(json.dumps({"accessibilityOptions": {"wheelchairAccessibleSeating": True}})) == [
        ("accessibility", "wheelchair_accessible_seating", "$.accessibilityOptions.wheelchairAccessibleSeating"),
    ]
    assert pairs(json.dumps({"flags": {"restroom": True}})) == [
        ("general_amenities", "has_restroom", "$.flags.restroom"),
    ]
    assert pairs(None) == []


def test_node_spec_and_edge_seed():
    text = "\n".join(_cells(NB))
    for needle in (
        'trg_tbl="slv_3p_poi_amenity_kv"', 'inputs={"amenity": "slv_3p_poi_amenity"}',
        'pk=("poi_id", "amenity_group", "amenity_value")', 'required_inputs=("amenity",)',
        'write_mode="MERGE"', "%run NB_LIB_TRANSFORM_SLV_GLD", "finish_node(RES)",
    ):
        assert needle in text
    assert "_crawled_at" not in text and "_event_id" not in text
    ddl = _cells("NB_CREATE_DDL.ipynb")
    seed = next(c for c in ddl if "'slv_3p_poi_amenity_kv'" in c and "INSERT INTO" in c)
    for needle in (PL, "'RECOMPUTE'", "'NB_SLV_3P_POI_AMENITY_KV'", "'slv_3p_poi_amenity'", "WHERE NOT EXISTS"):
        assert needle in seed
    enr = next(c for c in ddl if "'PL_VV_TRANS_SLV_TO_ENR_15P' AS pl_name" in c)
    assert "slv_3p_poi_amenity_kv" not in enr
```

### 16.7 Optional evidence P03 (non-blocking)

`evidence/probes/P03_amenity_child_keys.py`: the same read, UDF, and token walk as P02. Print only `CHILD` tokens whose path equals or starts with `$.flags.servesWine`, `$.flags.takeout`, `$.fuelOptions`, `$.parkingOptions`, or `$.paymentOptions`, with no 50-line cap. Print kind and count only, no values. Output goes to `evidence/results/P03_amenity_child_keys.txt`.

Expansions pre-authorized when P03 shows `kind=bool` (no new architecture round needed):

| Proven path | Rule added |
|---|---|
| `$.flags.servesWine` | FLAG → (`general_amenities`, `serves_wine`) |
| `$.flags.takeout` | FLAG → (`general_amenities`, `takeout`) |
| `$.paymentOptions.{acceptsCreditCards,acceptsDebitCards,acceptsNfc,acceptsCashOnly}` | FLAG → (`general_amenities`, snake_case) |
| `$.parkingOptions.{freeParkingLot,paidParkingLot,freeStreetParking,paidStreetParking,valetParking,freeGarageParking,paidGarageParking}` | FLAG → (`general_amenities`, snake_case), in addition to `parking` |

Any other child key stays MISSING_EVIDENCE because no documented rule exists for it. After an expansion, Main updates `AMENITY_KV_RULES`, `AMENITY_KV_MISSING_EVIDENCE`, the proven sets and count in the test, and D6. The change is applied with a forced run (I10).

## 17. Rollout, rollback, and forward recovery

**Rollout**

1. Main implements §16, updates `scope.files`, and records D6.
2. Local verification.
3. Specialist review.
4. The user imports `NB_SLV_3P_POI_AMENITY_KV` into the DEV workspace (default lakehouse `lh_vv_bronze`, as for the other nodes) and runs `kvedgepy`.
5. The user runs V1–V5.
6. Scheduling decision (S5).

The user must also commit `docs/context/3p-google/poi_amenity_mapping.md`, which is untracked and cited by D6.

**Rollback** (`runtime-runbook.md` must contain it before any DROP, per AGENTS §8):

1. Confirm there is no consumer: `SELECT COUNT(*) FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE src_tbl = 'slv_3p_poi_amenity_kv'` returns 0.
2. Disable the edge: `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0 WHERE pl_name = 'PL_VV_TRANS_SLV_3P_AMENITY_KV_1H'`. This is enough for a soft rollback.
3. Full removal:
   - `DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE pl_name = 'PL_VV_TRANS_SLV_3P_AMENITY_KV_1H' AND trg_tbl = 'slv_3p_poi_amenity_kv'`
   - `DELETE FROM lh_vv_ctrl.dbo.ctrl_mng_watermark WHERE watermark_id IN ('wm_e__slv_3p_poi_amenity_kv__slv_3p_poi_amenity', 'wm_flow__PL_VV_TRANS_SLV_3P_AMENITY_KV_1H')`
   - `DROP TABLE IF EXISTS lh_vv_silver.dbo.slv_3p_poi_amenity_kv`
   - Log rows stay as history.

Content rollback for a bad rule needs no DROP: revert `kvrules` and force-run. Tombstoned rows reactivate.

**Forward recovery**: run `kvedgepy` again (or `UPDATE ... SET is_active = 1`), then NB_00 RUN. The missing target is rebuilt from the current pinned source, and V2–V4 apply.

## 18. Evidence status

P01 and P02 are sufficient for every active rule. P03 (§16.7) is optional and only widens the rule table under pre-authorized expansions. No decision in this document depends on it.
