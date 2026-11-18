RESULT: PASS

## Main brief

### Decision

- Layout D-02: three pipelines, one per existing `pl_name`. FL_00 handles all four bronze sources in one sequential ForEach; ENR_15M and GLD_30M each get one SQL gate in front of the orchestrator notebook. `concurrency = 1` everywhere.
- Extract dispatch: the generic `If_HasWork` is unchanged, plus four sibling `If_Run_*` conditions, each holding one notebook with a fixed source. No Switch.
- Transform gate: one Script on `ctrl_log_run` through `conn_lh_vv_bronze_by_sqlep`. It skips only when `gate_reason = 'NO_DATA'`.
- `ctrl` seed: zero edits. Existing rows already match the pipeline names.
- Three stop points: test scope (S1), docs and rule scope (S2), Fabric runbook (S3). Round 2 re-checked round 1 against the repo; the layout is unchanged.

### Invariants Main must preserve

- A `TridentNotebook` activity exists only inside an `ifTrueActivities` list.
- `If_HasWork` in FL_00 keeps its expression and its false branch (`Set_Msg_Skip` only).
- Each `If_Run_*` expression is `@and(equals(item().src_tbl, '<src>'), <body of the If_HasWork expression>)`, with four distinct source literals.
- `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` keeps its notebook id, workspace id, policy, and 14 parameters byte for byte. Only its `dependsOn` becomes `[]`. Its id occurs once in the file.
- New notebook activities take `notebookId` and `workspaceId` from pipeline parameters. No new GUID in any file or in `ctrl`.
- Every notebook activity has a timeout, `retry: 0`, and a parameter map. Every passed parameter name is declared in that notebook's parameter cell.
- Activity names are unique across the three files. Every `dependsOn` target is in the same activity list. Only `Succeeded` is used as a dependency condition.
- `ForEach_Source.isSequential` stays true. `properties.concurrency` is 1 in all three files.
- No `Switch` activity. No edit to `manifest.json`, seed notebooks, `lastModifiedByObjectId`, or `lastPublishTime`.
- The transform `If_HasWork_*` expression runs the notebook for every `gate_reason` other than the literal `NO_DATA`.

### Edit list

| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | `.ai/tasks/20261117-pipeline-precheck-flows/decision.md` | `## Quyết định hiện hành` | Add row D-02 with the layout from "4. Layout decision", including the three rejected layouts and the extract-dispatch and transform-gate choices. Vietnamese prose. | Row exists before any JSON edit. |
| 2 | `pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json` | whole file | Replace with the first `FILE:` block in "19. Files to save verbatim". | File equals the block; parses as JSON. |
| 3 | `pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json` | new file | Create from the second `FILE:` block. | File equals the block; parses as JSON. |
| 4 | `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json` | `Get_Config_4Run` → `scripts[0].text.value` | Replace the query with "18.2". | Query names four sources and orders by `run_order`. |
| 5 | same | top-level `activities` | Add `Validate_Extract_Binding` from "18.3". | Activity present with nested `Fail_Bad_Extract_Binding`. |
| 6 | same | `ForEach_Source.dependsOn` | Append `Validate_Extract_Binding` / `Succeeded`. | Three dependencies. |
| 7 | same | `If_HasWork.ifTrueActivities` | Remove the partner notebook object. Keep `Set_Msg_Run`. | True branch has one activity. Expression and false branch unchanged. |
| 8 | same | `ForEach_Source.typeProperties.activities` | Append `If_Run_PARTNER`, `If_Run_3P`, `If_Run_CMS`, `If_Run_ENRICH` from "18.4". Move the partner notebook object into `If_Run_PARTNER` with `dependsOn: []`. | Four dispatch conditions, one notebook each. |
| 9 | same | pipeline `parameters` | Add `nb_extract_3p_id`, `nb_extract_cms_id`, `nb_extract_enr_id`, `workspace_id`, each `{"type":"String"}`. | Four new parameters, no default value. |
| 10 | same | `properties` | Add `"concurrency":1`. | Key present. |
| 11 | `tests/test_enr_poi_contract.py` (needs S1) | `test_pipeline_timeouts` | Find the notebook under `If_HasWork_ENR.typeProperties.ifTrueActivities`; assert `dependsOn[0].activity == "Set_Msg_Run_ENR"` and `Get_Flow_Gate_ENR.dependsOn[0].activity == "Validate_Notebook_Binding"`. Keep the other assertions. | Test passes. |
| 12 | `tests/test_pipeline_precheck_contract.py` (needs S1) | new file | Ten tests from "15.3 Tests". | All pass. |

For rows 4–10 the file is a one-line minified export. Edit in place and leave every unrelated byte alone. The parameter names in "18.4" were checked against the four parameter cells this round (finding F8): none of the three new activities passes `overlap_minutes`; only the 3rd-party activity passes `doc_key_column` and `state_key`; the enrichment activity passes no `sources`. Do not add or remove a name.

### Order and stop points

1. Row 1: record D-02.
2. **STOP S1 (user decision).** Add `tests/test_enr_poi_contract.py` and `tests/test_pipeline_precheck_contract.py` to `scope.files`. Without this, `vv.py verify` fails on `test_pipeline_timeouts` after row 2. Do not make the notebook top-level to avoid the test change.
3. Rows 2 and 3.
4. Rows 4–10.
5. Rows 11 and 12.
6. Run the commands in the next section.
7. **STOP S2 (user decision).** These describe the old layout and are not in `scope.files`: `.cursor/rules/20-data-pipeline.mdc` line 10 (an agent-system file; needs an explicit user request), `docs/context/CTRL_TABLES_CONTEXT.md` §2–§3, `00_README.md`, `01_DATA_MODEL.md`, `02_NAMING_CONVENTION.md` §3, `03_OPERATOR_GUIDE.md`, the four `NB_EXTRACT_*` docs, and `NB_00_ORCHES_SLV_TO_GLD.md`. Ask whether to extend scope or open a follow-up task.
8. Request the runbook: `python scripts/vv.py run-author 20261117-pipeline-precheck-flows --kind runbook`, with cases C1–C6 and the three rollout prerequisites from "14" and "16".
9. **STOP S3 (runtime).** No Fabric DEV step in this task.
10. Report to the reviewers and the risk gate: R1 (SQL endpoint sync stall, `p_max_idle_min` default 0), R2 (inputs with no owning pipeline need `p_force_run`), R3 (three concurrent Spark sessions unproven on F16), R4 (partner lock 60 minutes is shorter than its 12-hour timeout, unchanged), R5 (ForEach continue-after-failure, `concurrency`, and bool-parameter behavior checked in C4 and C6). Named gap: `PL_VV_TRANS_SLV_TO_GLD_1H` has seed edges and no pipeline.

### Tests and verification

- `python -m pytest -q tests/test_pipeline_precheck_contract.py tests/test_enr_poi_contract.py::test_pipeline_timeouts`
- `python -m pytest -q tests/test_initial_ddl_contract.py::test_no_old_cadence_suffix_in_active_surface`
- `python scripts/vv.py verify 20261117-pipeline-precheck-flows`

`vv.py verify` does not walk these pipeline files for names or `dependsOn` (they keep activities under `resources[0].properties`), so the new tests are the only machine check of those rules.

New test names in `tests/test_pipeline_precheck_contract.py`:

- `test_no_switch_and_unique_activity_names`
- `test_depends_on_same_scope_and_succeeded_only`
- `test_notebooks_only_in_true_branch`
- `test_notebook_policy_and_declared_params`
- `test_fl00_sources_and_dispatch`
- `test_fl00_partner_activity_unchanged`
- `test_fl00_binding_fails_closed`
- `test_transform_gate_skips_only_on_no_data`
- `test_gld_pipeline_timeouts`
- `test_lock_outlives_activity_timeout`

### Read only if needed

| Full-document heading | Justifies rows |
|---|---|
| 3. Repository findings that shape the design | 2, 7, 8, 11, stop S1 |
| 4. Layout decision | 1 |
| 5. Invariants | all |
| 10. Transform gate contract | 2, 3 |
| 11. Idempotency, concurrency, retry, recovery, partial failure | 5, 6, 8, 10 |
| 14. Rollout, rollback, forward recovery | step 8 (runbook prerequisites) |
| 15.1 FL_00 edits | 4–10 |
| 15.3 Tests | 11, 12 |
| 16. Verification | step 8 |
| 17. Stop points and residual risks | steps 2, 7, 9, 10 |
| 18.2 FL_00 `Get_Config_4Run` query | 4 |
| 18.3 FL_00 `Validate_Extract_Binding` | 5 |
| 18.4 FL_00 dispatch activities | 8 |
| 19. Files to save verbatim | 2, 3 |

# Architecture: 20261117-pipeline-precheck-flows

The design passes. No new evidence is needed before the JSON edits. Three stop points remain for Main and the user (section 17): a scope extension for two test files, a scope decision for docs and one rule line, and the Fabric DEV runbook.

This round re-checked the round-1 design against the repository. The layout is unchanged. Section 3 lists what was confirmed and what was corrected.

## 1. Scope

- `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`: the pre-check covers four bronze sources. A source with new commits calls its own extract notebook. `NO_DATA` starts no notebook.
- `PL_VV_TRANS_SLV_TO_ENR_15M`: a SQL gate decides whether `NB_00_ORCHES_SLV_TO_ENR_15P` runs.
- `PL_VV_TRANS_SLV_TO_GLD_30M`: new pipeline JSON with the same gate. It calls `NB_00_ORCHES_SLV_TO_GLD` through a parameter binding.
- The layout text for `decision.md` (section 4) and the required runbook cases (section 16).

## 2. Non-goals

- No notebook, seed, DDL, table, column, grain, or key change. `ctrl` seed rows stay as they are: every existing row already carries the `pl_name` of the pipeline that will own it.
- No pipeline for `PL_VV_TRANS_SLV_TO_GLD_1H`. The seed has edges for it (`amenddlpy`, asserted in `tests/test_poi_media_amenity_contract.py`). It has no pipeline JSON and is not in `scope.files`. This is a named gap.
- No change to the partner activity's notebook id, timeout, retry, or parameter values.
- No Fabric run.

## 3. Repository findings that shape the design

| # | Finding (checked this round) | Consequence |
|---|---|---|
| F1 | `scope.files` holds only the three pipeline JSON files. Seed notebooks are out of scope. | The layout must need zero seed edits, so all four extract sources stay under `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. |
| F2 | `tests/test_enr_poi_contract.py::test_pipeline_timeouts` (line 361) looks up `NB_00_ORCHES_SLV_TO_ENR_15P` in the top-level activity list and asserts `dependsOn[0].activity == "Validate_Notebook_Binding"`. `vv.py verify` runs the whole `tests/` directory. | A skip requires the notebook to sit inside an IfCondition, which breaks that test. The test file must enter `scope.files` (stop S1). |
| F3 | `NB_00` advances an edge only for a node that ran `SUCCESS` or `NO_DATA` (`advance_edges`, lib line 1812). | A `_delta_log` pre-check on silver inputs would stay positive after one maintenance commit. See alternative T-A. |
| F4 | `orchestrate` sets `started = utc_now()` (lib line 1882) before `plan_run` (lines 1886 and 1908). It logs `SKIPPED_CONCURRENT` and returns without raising (lines 1899–1901). The four extract notebooks raise on `FAILED`, `PARTIAL_FAILED`, and `SKIPPED_CONCURRENT`. | The gate compares against the start time of the last good run and ignores `SKIPPED_CONCURRENT` rows. |
| F5 | The partner activity passes `running_timeout_minutes = 60` with a 12-hour activity timeout. The notebook default is 780. | Existing value, kept as the request requires. Residual risk R4. |
| F6 | `wm_transform_cms_raw_data` and `wm_transform_brz_enrichment_result` are seeded `INITIALIZED` with NULL `last_src_version` (`CTRL_TABLES_CONTEXT.md` §4). The pipeline passes `allow_full_scan = false`. | The first load of each new source is a manual run. Until then the pre-check says `FIRST_RUN` and the notebook fails visibly. Runbook prerequisite. |
| F7 | `check_json` in `scripts/vv.py` (line 1732) reads `document["properties"]["activities"]`. These files keep activities under `resources[0].properties`, so the name and `dependsOn` rules are not machine-checked today. | New unit tests carry those checks (section 15.3). |
| F8 | Parameter cells: partner has 14 names including `overlap_minutes`. 3rd-party has no `overlap_minutes` and adds `sources`, `doc_key_column`, `state_key`. CMS adds only `sources`; its `doc_key_column` and `state_key` are constants in a later cell. Enrichment has neither `sources` nor the two key names. | Section 18.4 passes exactly the declared names. Round 1 asked Main to re-check them; that check is now done and stays as a test. |
| F9 | `Files/_delta_src/<table>` appears only in the FL_00 JSON, the rule file, and `99_PAIN_POINTS.md`. The repo does not record which shortcuts exist. | Shortcuts for the three new sources are a runbook prerequisite. A missing one fails `GM_DeltaLog` for that source; it does not skip. |
| F10 | The parameter cell of `NB_00_ORCHES_SLV_TO_GLD.ipynb` defaults `p_pl_name` to `PL_VV_TRANSFORM_SLV_TO_GLD_1H`. | The GLD activity always passes `@pipeline().Pipeline`, so the default is never used by the pipeline. |

## 4. Layout decision (Main records this as D-02 in `decision.md` before any JSON edit)

**Selected: three pipelines, one per `pl_name` already in `ctrl`.**

- `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`: all four bronze sources, one sequential ForEach, one notebook at a time.
- `PL_VV_TRANS_SLV_TO_ENR_15M` and `PL_VV_TRANS_SLV_TO_GLD_30M`: one gate and one orchestrator notebook each.
- Every pipeline has `concurrency = 1`.

| Alternative | Why rejected |
|---|---|
| L-A. One combined pipeline (extract, then ENR, then GLD) | `pl_name` equals the pipeline name and one active node belongs to one `pl_name`. One name would force a rewrite of every seed row and of the `wm_flow__` rows, and it would break the cadence suffix that the library validates (`CADENCE_RE`). The 15-minute and 30-minute cadences cannot share one schedule. |
| L-B. One pipeline per extract source | Needs four `pl_name` values, so seed rows, tests, and pipeline files outside `scope.files`. Four schedules can start four Spark sessions at once. |
| L-C. Parent pipeline that invokes children | Needs a fourth pipeline artifact and child pipeline ids that are not in the repo. |

Trade-off accepted: the three pipelines are not serialized against each other. The worst case is three concurrent Spark sessions: one extract notebook, one ENR orchestrator, one GLD orchestrator. The pre-check removes the idle starts, which is what the capacity criterion asks for. Whether three sessions fit F16 is a runtime fact that the runbook measures (case C5).

### Extract dispatch without a Switch

**Selected: one ForEach, the generic `If_HasWork`, and four sibling `If_Run_*` conditions.** `If_HasWork` keeps its expression and its false branch (`Set_Msg_Skip` only). Each `If_Run_<source>` runs after `If_HasWork` and holds exactly one notebook activity with the source fixed in the activity. At most one `If_Run_*` is true per iteration.

| Alternative | Why rejected |
|---|---|
| E-A. Four chained ForEach blocks, each a clone of the template | Isolation between blocks needs `Completed` dependencies, and then a failed block is reported as success unless extra `Fail` leaves are added. About 27 cloned activities with renamed references in a minified file. |
| E-B. One notebook activity with `notebookId` and parameters chosen by expression | One timeout and one parameter map for four notebooks whose parameters differ (F8). The activity name would be wrong for three sources. |
| E-C. Chain blocks on `Succeeded` | One failing source starves every later source on each cycle. |

### Transform gate

**Selected: T-B, one SQL gate on `ctrl_log_run` through the existing SQL endpoint connection.** The notebook runs unless the gate proves `NO_DATA`.

| Alternative | Why rejected |
|---|---|
| T-A. `_delta_log` check per input table against `wm_e__` rows | F3 makes it permanently positive after a maintenance commit. It needs a `Files/_delta_src` shortcut for every silver input, and the repo records none (F9). It costs many activity runs per cycle. |
| T-C. Compare `ctrl_mng_watermark` timestamps only | The flow lock row does not keep the start time of the last good run. A comparison on end times misses an extract that finishes while the transform is running. |

T-B has two costs. The SQL endpoint can lag behind Delta, and inputs with no owning pipeline (a manual `ref_*` edit, a manual node run) are invisible to the gate. Lag only delays a run, because the comparison is against stored state. `p_force_run` and `p_max_idle_min` cover the invisible inputs (section 10).

## 5. Invariants

| ID | Invariant |
|---|---|
| I1 | A notebook activity exists only inside the true branch of an IfCondition. No other path reaches a notebook. |
| I2 | Extract skips only when `v_last_ver` is not empty and `Filter_NewCommits.FilteredItemsCount = 0`. A failed pre-check activity fails the iteration. |
| I3 | Transform skips only when `gate_reason` equals the literal `NO_DATA` and `p_force_run` is false. Any other value, including an unexpected one, runs the notebook. A failed gate Script fails the pipeline. |
| I4 | `ForEach_Source.isSequential` is true. The `If_Run_*` source literals are distinct, so one iteration starts at most one notebook. |
| I5 | Every notebook activity has an explicit `timeout`, `retry = 0`, and a parameter map. Every passed name is declared in that notebook's parameter cell. |
| I6 | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK` keeps its notebook id, workspace id, policy, and 14 parameters byte for byte. Its id appears exactly once in the file. |
| I7 | A new notebook activity takes `notebookId` and `workspaceId` from pipeline parameters. An empty value or one containing `PENDING` fails the pipeline before any pre-check. No new GUID enters the repo or `ctrl`. |
| I8 | Activity names are unique across the three files. Every `dependsOn` target is in the same activity list. |
| I9 | No `Switch` activity in any of the three files. |
| I10 | A failed notebook, gate, or binding check fails the pipeline run. Only `Succeeded` is used as a dependency condition. |
| I11 | `properties.concurrency = 1` in all three files. |
| I12 | The `pl_name` passed to a notebook equals the pipeline name stored in `ctrl`. |

## 6. State ownership

| State | Writer | Pipeline access |
|---|---|---|
| `ctrl_mng_pipeline_config` | Setup notebooks, operators | Read through the SQL endpoint. |
| `ctrl_mng_watermark` source rows | Extract notebooks | Read by `Lookup_WM`. Never written by a pipeline. |
| `ctrl_mng_watermark` edge and flow rows | `NB_00` | Not read by any pipeline. |
| `ctrl_log_run` | Extract notebooks, `NB_00` | Read by the transform gate through the SQL endpoint. |
| Pipeline variables `v_*` | Pipeline | Run-local, for monitoring only. |

The pipelines hold no durable state. Every decision is recomputed from `ctrl` on each run.

## 7. Grain and keys

Not applicable: no table, column, grain, or key changes, so no `model-design.md` is needed. The gate reads `ctrl_log_run` (one row per `exec_id`) and `ctrl_mng_pipeline_config` (one row per `pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`), as documented in `docs/context/CTRL_TABLES_CONTEXT.md` §1, §3, and §6.

## 8. Ordering

- FL_00 top level: `Validate_Extract_Binding`, `Get_Config_4Run`, and `Lookup_WM` start together. `ForEach_Source` waits for all three.
- Source order is fixed by `run_order` in the config query: partner, 3rd-party, CMS, enrichment. The sources are independent; the order only makes logs predictable.
- Inside one iteration: `Set_src` → `Filter_WM` → (`Set_LastVer`, `Set_LastFile`, `GM_DeltaLog`) → `Filter_NewCommits` → `If_HasWork` → the four `If_Run_*`.
- Transform: binding check → `Get_Flow_Gate_*` → `If_HasWork_*` → (`Set_Msg_Run_*` → notebook) or `Set_Msg_Skip_*`.
- There is no ordering across pipelines. A transform sees an extract through `ctrl_log_run` on its next cycle.

## 9. Transaction and commit boundaries

The pipelines commit nothing. Each notebook keeps its own boundaries: an extract advances the source watermark only while it holds the lock and only forward; `NB_00` advances edges in one MERGE after `runMultiple`. A pipeline skip leaves every watermark untouched, so the next run evaluates the same state.

## 10. Transform gate contract

The query is in the `FILE:` blocks of section 19. It returns exactly one row: `me` and `up` are aggregates without `GROUP BY`, joined with `CROSS JOIN`.

| `gate_reason` | Condition, evaluated in this order | Result |
|---|---|---|
| `FIRST_RUN` | No `RUN` row of this `pl_name` with status `SUCCESS` or `NO_DATA`. | Run |
| `LAST_RUN_NOT_OK` | A `RUN` row of this `pl_name` (not `SKIPPED_CONCURRENT`) started after the last good one. Covers `FAILED`, `PARTIAL_FAILED`, `ABANDONED`, and `RUNNING`. | Run |
| `UPSTREAM_CHANGED` | An upstream pipeline has a finished run that is not `NO_DATA`, `SKIPPED_CONCURRENT`, `RUNNING`, or `DRY_RUN`, with `ended_at` at or after the last good start minus 2 minutes. | Run |
| `IDLE_BACKSTOP` | `p_max_idle_min > 0` and the last good run started at least that many minutes ago. | Run |
| `NO_DATA` | None of the above. | Skip |

- Upstream pipelines come from config, not from a hardcoded list: any other `pl_name` that owns, as an active target, a table this pipeline reads as an active source. For ENR this resolves to FL_00. For GLD it resolves to FL_00 and any flow whose nodes it reads.
- Start time is the baseline because `NB_00` stamps `started_at` before it plans (F4). An upstream run that ended before that start was visible to the plan.
- The 2-minute margin exists because the timestamps come from different Spark drivers. It can cause one extra run, which ends `NO_DATA` and moves the baseline forward.
- An upstream `FAILED` or `PARTIAL_FAILED` run counts as a change. A partial run may have written tables; a failed one costs one extra transform run.
- `p_force_run` (bool, default false): operator override after a manual `ref_*` edit, a manual node run, or a table recreate.
- `p_max_idle_min` (int, default 0, which turns it off): a bound on undetected staleness. With the default, an idle flow never starts Spark. A value above 0 trades one idle Spark start per window for that bound.

## 11. Idempotency, concurrency, retry, recovery, partial failure

**Idempotency.** A pipeline rerun re-evaluates the same `ctrl` state. A rerun after a skip skips again. A rerun after a notebook success finds the watermark advanced and skips. Notebook idempotency is unchanged.

**Concurrency.**
- Inside FL_00: sequential ForEach, one notebook at a time. `ctrl_cdc_state` and `ctrl_cdc_reject` are read by `src_tbl` partition, so a manual run of another source does not conflict.
- Same pipeline: `concurrency = 1`. Whether Fabric queues or rejects a second trigger is checked in the runbook (C6).
- Manual run against a scheduled run: the notebook locks stay the guard. An extract raises `SKIPPED_CONCURRENT`, so the pipeline fails visibly. `NB_00` logs `SKIPPED_CONCURRENT` and returns; the gate ignores that row and the next cycle re-evaluates.
- Across pipelines: at most three Spark sessions (section 4).

**Retry.** Notebook activities use `retry = 0`. A retry would start a second Spark session against a lock that may still be held; the next schedule is the retry, and it is state-driven. The gate Script uses `retry = 1`, 30 seconds, timeout 5 minutes; it is read-only. Existing FL_00 pre-check activities keep their exported policy.

**Recovery.**
- An extract notebook fails: the source watermark does not advance. The next cycle finds the same commits and runs again.
- `NB_00` fails or is cancelled: the log row is `FAILED`, `PARTIAL_FAILED`, `RUNNING`, or later `ABANDONED`. The gate returns `LAST_RUN_NOT_OK` until a run ends `SUCCESS` or `NO_DATA`.
- An activity timeout cancels a notebook: the lock outlives the activity for every new activity (extract 60 > 59 minutes; ENR 35 > 32; GLD 90 > 52). After a cancelled extract, later cycles of that source fail with `SKIPPED_CONCURRENT` until the lock expires, at most 60 minutes, or until the operator releases it (`CTRL_TABLES_CONTEXT.md` §4).

**Partial failure.**

| Failure | Behavior |
|---|---|
| Binding empty or placeholder | `Fail_Bad_*` fails the pipeline before any pre-check. Nothing runs. |
| `Get_Config_4Run`, `Lookup_WM`, or the gate Script fails | Pipeline fails. No notebook starts. |
| `GM_DeltaLog` fails for one source, for example a missing shortcut | That iteration fails. Later sources still run. ForEach and pipeline fail. |
| One extract notebook fails | Same as above. Other sources are not starved. |
| Source has a config row and no watermark row | `v_last_ver` is empty, the pre-check says `FIRST_RUN`, the notebook raises. Visible failure. |
| Raw table recreated with a lower version | The pre-check sees no file name above the stored one and skips. This is an existing limit of the template. Recovery is the documented watermark reset plus a manual full load. |
| SQL endpoint lags | The gate sees older state. It runs once more than needed or one cycle late. |
| SQL endpoint stops syncing | The gate keeps its last answer. If that answer was `NO_DATA`, the flow stalls with green runs (R1). |

## 12. Observability

- `v_msg` and `v_msg_skip`: one line per source or flow with `RUN` or `SKIP`, the reason, and the compared values, visible in the activity output.
- Extract runs: `ctrl_log_run` by `run_id`. The three new activities pass `@pipeline().RunId`. The partner activity still passes an empty `run_id`.
- Transform runs: `ctrl_log_run.pl_name` and `status`. A skipped cycle writes no row, so skips are visible only in pipeline monitoring.
- Stall check for R1 (runbook query): compare the newest finished non-`NO_DATA` run of FL_00 with the newest good run of each transform flow. An upstream run older than two cadences with no later transform run is a stall.
- Capacity: Fabric Capacity Metrics app, items `PL_VV_*` and the notebooks. The runbook records the measured CU; this design derives no figure.

## 13. Security

- No credential, host, or notebook GUID is added to the repo or to `ctrl`. The only embedded notebook id remains the partner one.
- Notebook and workspace ids for new activities are pipeline parameters that the user sets in Fabric.
- SQL text interpolates only `pipeline().Pipeline`, `p_pipeline_code`, and the int parameter `p_max_idle_min`. No value from data is concatenated into SQL.
- The ENR and GLD files hold no workspace GUID. `test_pipeline_timeouts` asserts this for ENR.

## 14. Rollout, rollback, forward recovery

**Rollout (by the user in Fabric DEV, after merge, per the runbook).**
1. Prerequisites: shortcuts `Files/_delta_src/brz_3rd_crawler_poi_stream`, `cms_raw_data`, and `brz_enrichment_result` in `lh_vv_bronze`; one `wm_transform_<src_tbl>` row per source; a manual first load of each new source with `allow_full_scan = True`; the four extract notebooks and both orchestrators published.
2. Import the three pipelines. Bind `nb_extract_3p_id`, `nb_extract_cms_id`, `nb_extract_enr_id`, `nb_orches_id`, `workspace_id`, and the connection `conn_lh_vv_bronze_by_sqlep`.
3. Run the runbook cases with schedules off. Enable schedules last, offset from each other.

**Rollback.** Disable the schedule and re-import the previous JSON from Git (`9a62b9f`). Pipelines write no state, so no data repair is needed. The GLD pipeline is new: its rollback is to disable or delete it.

**Forward recovery.** A stalled transform: run the pipeline once with `p_force_run = true`, or run `NB_00` by hand. A stalled extract after a raw recreate: reset the watermark row (`CTRL_TABLES_CONTEXT.md` §4) and run the notebook by hand with `allow_full_scan = True`.

## 15. Implementation plan

Order: D-02 in `decision.md` → scope extension (S1) → ENR and GLD files → FL_00 edits → tests → `vv.py verify`.

### 15.1 FL_00 edits (minified one-line export; edit in place, keep every unrelated byte)

1. `Get_Config_4Run.typeProperties.scripts[0].text.value`: replace with section 18.2.
2. Top-level `activities`: add the activity in section 18.3.
3. `ForEach_Source.dependsOn`: append `{"activity":"Validate_Extract_Binding","dependencyConditions":["Succeeded"]}`.
4. `If_HasWork.ifTrueActivities`: remove `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK`. `Set_Msg_Run` stays. `expression` and `ifFalseActivities` are unchanged.
5. `ForEach_Source.typeProperties.activities`: append the four activities in section 18.4. The partner activity moves into `If_Run_PARTNER` with `dependsOn: []`; nothing else in it changes.
6. Pipeline `parameters`: add `nb_extract_3p_id`, `nb_extract_cms_id`, `nb_extract_enr_id`, and `workspace_id`, each `{"type":"String"}`.
7. `properties`: add `"concurrency":1`.
8. Do not touch `lastModifiedByObjectId`, `lastPublishTime`, the linked services, or `manifest.json`.

### 15.2 ENR and GLD

Save the two `FILE:` blocks in section 19 verbatim.

### 15.3 Tests (needs S1)

- Edit `tests/test_enr_poi_contract.py::test_pipeline_timeouts`: find the notebook in `If_HasWork_ENR.typeProperties.ifTrueActivities`; assert `dependsOn[0].activity == "Set_Msg_Run_ENR"`; assert `Get_Flow_Gate_ENR.dependsOn[0].activity == "Validate_Notebook_Binding"`. Keep every other assertion.
- New `tests/test_pipeline_precheck_contract.py` with a recursive walker over `resources[0].properties.activities` (ForEach `activities`, If `ifTrueActivities` and `ifFalseActivities`):

| Test | Asserts |
|---|---|
| `test_no_switch_and_unique_activity_names` | I8 (names) and I9 across the three files. |
| `test_depends_on_same_scope_and_succeeded_only` | I8 (`dependsOn`) and I10. |
| `test_notebooks_only_in_true_branch` | I1. |
| `test_notebook_policy_and_declared_params` | I5: timeout, `retry == 0`, non-empty parameters; each name is assigned in the notebook's parameter cell. |
| `test_fl00_sources_and_dispatch` | The config SQL names the four sources; four `If_Run_*`, each with one notebook whose `src_tbl` equals the literal in its expression; each expression is `@and(equals(item().src_tbl, '<src>'), <body of the If_HasWork expression>)`; `isSequential` is true (I2, I4). |
| `test_fl00_partner_activity_unchanged` | I6: id `2baecfc9-a8a3-4905-965f-f16eb6244fee` occurs once; policy and the 14 parameters equal the values in commit `9a62b9f`. |
| `test_fl00_binding_fails_closed` | I7 for the three ids and `workspace_id`; `ForEach_Source` depends on `Validate_Extract_Binding`. |
| `test_transform_gate_skips_only_on_no_data` | I3 for ENR and GLD; the gate SQL contains the five reasons and excludes `SKIPPED_CONCURRENT`, `DRY_RUN`, and `RUNNING`. |
| `test_gld_pipeline_timeouts` | Name, `concurrency == 1`, timeout `0.00:52:00`, `p_lock_timeout_min` 90 > `p_dag_timeout_min` 45 + 5, no workspace GUID, `p_pl_name` is `@pipeline().Pipeline`. |
| `test_lock_outlives_activity_timeout` | For the three new extract activities, `running_timeout_minutes` (60) exceeds the activity timeout in minutes (59). |

## 16. Verification

Local: `python -m pytest -q tests/test_pipeline_precheck_contract.py tests/test_enr_poi_contract.py::test_pipeline_timeouts`, then `python scripts/vv.py verify 20261117-pipeline-precheck-flows`.

Runtime runbook (author with `python scripts/vv.py run-author 20261117-pipeline-precheck-flows --kind runbook`; the user runs it later). Required cases:

| Case | Setup | Pass condition |
|---|---|---|
| C1 extract no data | All four watermarks current, no new bronze commit. | Four `SKIP` messages, no notebook activity run, no new `ctrl_log_run` row, no Spark session in the Monitoring hub. |
| C2 extract has data | New commit on one source. | Only that source's notebook runs; `ctrl_log_run` has one row with the pipeline `run_id`; a second run skips. |
| C3 transform no data | Last ENR run `SUCCESS` or `NO_DATA`, no later upstream run. | `gate_reason = NO_DATA`, no notebook run. Same for GLD. |
| C4 transform has data | After C2. | `gate_reason = UPSTREAM_CHANGED` on the next ENR run; the notebook runs; the following run skips, or runs once more with `NO_DATA` and then skips. Record the delay between the extract `ended_at` and the gate seeing it. Also run once with `p_force_run = true` and confirm the notebook starts. |
| C5 capacity | C2 and C4 overlapping, plus one idle hour. | Capacity Metrics shows no throttling; record the CU of pipeline operations and of Spark for the hour. |
| C6 failure and overlap | One id left empty; one notebook forced to fail; a second trigger while a run is active. | Empty id: the pipeline fails with `BAD_NOTEBOOK_BINDING` and nothing runs. Failed notebook: the pipeline fails and later sources still ran. Second trigger: no second notebook starts. |

Stop before every Fabric step in this task.

## 17. Stop points and residual risks

| ID | Type | Item |
|---|---|---|
| S1 | Scope decision (Main, user) | Add `tests/test_enr_poi_contract.py` and `tests/test_pipeline_precheck_contract.py` to `scope.files`. Without it, `vv.py verify` fails on `test_pipeline_timeouts` after the ENR edit. |
| S2 | Scope and rule decision (user) | Text that describes the old layout and is not in `scope.files`: `.cursor/rules/20-data-pipeline.mdc` line 10 (an agent-system file that needs an explicit user request), `docs/context/CTRL_TABLES_CONTEXT.md` §2–§3, `00_README.md`, `01_DATA_MODEL.md`, `02_NAMING_CONVENTION.md` §3, `03_OPERATOR_GUIDE.md`, the four `NB_EXTRACT_*` docs, and `NB_00_ORCHES_SLV_TO_GLD.md`. |
| S3 | Runtime | Fabric DEV runbook, cases C1–C6. |
| R1 | Residual risk | The SQL endpoint stops syncing: a transform flow can stall with green runs. Levers: `p_max_idle_min`, the stall query, `p_force_run`. The default is off so an idle flow starts no Spark. The risk gate decides whether DEV keeps 0. |
| R2 | Residual risk | Inputs without an owning pipeline (`ref_*`, manual node runs) do not open the gate. The operator uses `p_force_run`. |
| R3 | Residual risk | Three concurrent Spark sessions are possible. Not proven against F16 until C5. |
| R4 | Existing, unchanged | The partner lock (60 minutes) is shorter than its activity timeout (12 hours). |
| R5 | Unverified platform behavior | A sequential ForEach continues after a failed iteration and then fails; `concurrency = 1` holds a second trigger; a bool pipeline parameter reaches `@or(...)` as a bool. C4 and C6 check these. |

## 18. Reference content

### 18.1 Transform gate SQL (T-SQL, SQL analytics endpoint, database `lh_vv_ctrl`)

The exact text is inside the `FILE:` blocks of section 19 (`Get_Flow_Gate_ENR`, `Get_Flow_Gate_GLD`). Shape: CTE `up_pl` (upstream pipelines from config), CTE `me` (last good start and last start of this pipeline, `run_mode = 'RUN'`, not `SKIPPED_CONCURRENT`), CTE `up` (newest finished upstream run), then one row with `gate_reason`, `ok_started_at`, `last_started_at`, `up_at`.

### 18.2 FL_00 `Get_Config_4Run` query (JSON string value)

```
SELECT DISTINCT src_schema, src_tbl,\n  CASE src_tbl WHEN 'partner_raw_data' THEN 1 WHEN 'brz_3rd_crawler_poi_stream' THEN 2 WHEN 'cms_raw_data' THEN 3 ELSE 4 END AS run_order\nFROM dbo.ctrl_mng_pipeline_config\nWHERE pl_name = '@{pipeline().parameters.p_pipeline_code}'\n  AND is_active = 1\n  AND src_tbl IN ('partner_raw_data', 'brz_3rd_crawler_poi_stream', 'cms_raw_data', 'brz_enrichment_result')\nORDER BY run_order;
```

The allowlist is deliberate: a future active source without an `If_Run_*` would otherwise iterate and run nothing.

### 18.3 FL_00 `Validate_Extract_Binding` (top-level activity)

```
{"name":"Validate_Extract_Binding","type":"IfCondition","dependsOn":[],"typeProperties":{"expression":{"value":"@or(or(or(empty(pipeline().parameters.nb_extract_3p_id), contains(pipeline().parameters.nb_extract_3p_id, 'PENDING')), or(empty(pipeline().parameters.nb_extract_cms_id), contains(pipeline().parameters.nb_extract_cms_id, 'PENDING'))), or(or(empty(pipeline().parameters.nb_extract_enr_id), contains(pipeline().parameters.nb_extract_enr_id, 'PENDING')), or(empty(pipeline().parameters.workspace_id), contains(pipeline().parameters.workspace_id, 'PENDING'))))","type":"Expression"},"ifTrueActivities":[{"name":"Fail_Bad_Extract_Binding","type":"Fail","dependsOn":[],"typeProperties":{"message":"nb_extract_3p_id, nb_extract_cms_id, nb_extract_enr_id or workspace_id is empty or a placeholder","errorCode":"BAD_NOTEBOOK_BINDING"}}]}}
```

### 18.4 FL_00 dispatch activities (append inside `ForEach_Source.typeProperties.activities`)

`<WORK>` is the body of the existing `If_HasWork` expression, copied without change: `or(empty(variables('v_last_ver')), greater(activity('Filter_NewCommits').output.FilteredItemsCount, 0))`.

`<DEP>` is `[{"activity":"If_HasWork","dependencyConditions":["Succeeded"]}]`.

`<POL>` is `{"timeout":"0.00:59:00","retry":0,"retryIntervalInSeconds":30,"secureOutput":false,"secureInput":false}`.

`<BIND:x>` is `"notebookId":{"value":"@pipeline().parameters.x","type":"Expression"},"workspaceId":{"value":"@pipeline().parameters.workspace_id","type":"Expression"}`.

`<COMMON:src,par>` is `"pl_name":{"value":"PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00","type":"string"},"run_id":{"value":{"value":"@pipeline().RunId","type":"Expression"},"type":"string"},"src_schema":{"value":"lh_vv_bronze.dbo","type":"string"},"src_tbl":{"value":"src","type":"string"},"allow_full_scan":{"value":false,"type":"bool"},"max_parallel":{"value":"par","type":"int"},"max_retries":{"value":"1","type":"int"},"table_filter":{"value":"","type":"string"},"full_reload":{"value":false,"type":"bool"},"dry_run":{"value":false,"type":"bool"},"stop_on_failure":{"value":false,"type":"bool"},"cast_null_policy":{"value":"FAIL","type":"string"},"running_timeout_minutes":{"value":"60","type":"int"}`.

```
{"name":"If_Run_PARTNER","type":"IfCondition","dependsOn":<DEP>,"typeProperties":{"expression":{"value":"@and(equals(item().src_tbl, 'partner_raw_data'), <WORK>)","type":"Expression"},"ifTrueActivities":[ <the existing NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV_BK object, with "dependsOn":[] and no other change> ]}}

{"name":"If_Run_3P","type":"IfCondition","dependsOn":<DEP>,"typeProperties":{"expression":{"value":"@and(equals(item().src_tbl, 'brz_3rd_crawler_poi_stream'), <WORK>)","type":"Expression"},"ifTrueActivities":[{"name":"NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV","type":"TridentNotebook","dependsOn":[],"policy":<POL>,"typeProperties":{<BIND:nb_extract_3p_id>,"parameters":{<COMMON:brz_3rd_crawler_poi_stream,12>,"sources":{"value":"google","type":"string"},"doc_key_column":{"value":"poi_id","type":"string"},"state_key":{"value":"doc","type":"string"}}}}]}}

{"name":"If_Run_CMS","type":"IfCondition","dependsOn":<DEP>,"typeProperties":{"expression":{"value":"@and(equals(item().src_tbl, 'cms_raw_data'), <WORK>)","type":"Expression"},"ifTrueActivities":[{"name":"NB_EXTRACT_CMS_CDC_BRZ_TO_SLV","type":"TridentNotebook","dependsOn":[],"policy":<POL>,"typeProperties":{<BIND:nb_extract_cms_id>,"parameters":{<COMMON:cms_raw_data,4>,"sources":{"value":"strapi_blog,strapi_destination,strapi_news,strapi_ph_promotion_article","type":"string"}}}}]}}

{"name":"If_Run_ENRICH","type":"IfCondition","dependsOn":<DEP>,"typeProperties":{"expression":{"value":"@and(equals(item().src_tbl, 'brz_enrichment_result'), <WORK>)","type":"Expression"},"ifTrueActivities":[{"name":"NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV","type":"TridentNotebook","dependsOn":[],"policy":<POL>,"typeProperties":{<BIND:nb_extract_enr_id>,"parameters":{<COMMON:brz_enrichment_result,2>}}}]}}
```

Parameter values come from each notebook's parameter cell (`sources`, `max_parallel`, `doc_key_column`, `state_key`), except `allow_full_scan = false` and `running_timeout_minutes = 60`, which follow the partner activity. The names match F8: none of the three new activities passes `overlap_minutes`; only the 3rd-party activity passes `doc_key_column` and `state_key`; the enrichment activity passes no `sources`.

## 19. Files to save verbatim

FILE: pipelines/PL_VV_TRANS_SLV_TO_ENR_15M/PL_VV_TRANS_SLV_TO_ENR_15M.json
{
  "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "conn_lh_vv_bronze_by_sqlep": {"type": "string"}
  },
  "variables": {},
  "resources": [
    {
      "name": "PL_VV_TRANS_SLV_TO_ENR_15M",
      "type": "pipelines",
      "apiVersion": "2018-06-01",
      "properties": {
        "activities": [
          {
            "name": "Validate_Notebook_Binding",
            "type": "IfCondition",
            "dependsOn": [],
            "typeProperties": {
              "expression": {
                "value": "@or(empty(pipeline().parameters.nb_orches_id), contains(pipeline().parameters.nb_orches_id, 'PENDING'), empty(pipeline().parameters.workspace_id), contains(pipeline().parameters.workspace_id, 'PENDING'))",
                "type": "Expression"
              },
              "ifTrueActivities": [
                {
                  "name": "Fail_Bad_Binding",
                  "type": "Fail",
                  "dependsOn": [],
                  "typeProperties": {
                    "message": "nb_orches_id or workspace_id is empty or a placeholder",
                    "errorCode": "BAD_NOTEBOOK_BINDING"
                  }
                }
              ]
            }
          },
          {
            "name": "Get_Flow_Gate_ENR",
            "type": "Script",
            "dependsOn": [
              {
                "activity": "Validate_Notebook_Binding",
                "dependencyConditions": ["Succeeded"]
              }
            ],
            "policy": {
              "timeout": "0.00:05:00",
              "retry": 1,
              "retryIntervalInSeconds": 30,
              "secureOutput": false,
              "secureInput": false
            },
            "typeProperties": {
              "scripts": [
                {
                  "type": "Query",
                  "text": {
                    "value": "WITH up_pl AS (\n    SELECT DISTINCT p.pl_name\n    FROM dbo.ctrl_mng_pipeline_config AS m\n    INNER JOIN dbo.ctrl_mng_pipeline_config AS p\n        ON p.trg_schema = m.src_schema AND p.trg_tbl = m.src_tbl\n    WHERE m.pl_name = '@{pipeline().Pipeline}'\n      AND m.is_active = 1\n      AND p.is_active = 1\n      AND p.pl_name <> m.pl_name\n),\nme AS (\n    SELECT\n        MAX(CASE WHEN status IN ('SUCCESS', 'NO_DATA') THEN started_at END) AS ok_started_at,\n        MAX(started_at) AS last_started_at\n    FROM dbo.ctrl_log_run\n    WHERE pl_name = '@{pipeline().Pipeline}'\n      AND run_mode = 'RUN'\n      AND status <> 'SKIPPED_CONCURRENT'\n),\nup AS (\n    SELECT MAX(r.ended_at) AS up_at\n    FROM dbo.ctrl_log_run AS r\n    INNER JOIN up_pl AS u ON u.pl_name = r.pl_name\n    WHERE r.status NOT IN ('NO_DATA', 'SKIPPED_CONCURRENT', 'RUNNING')\n      AND COALESCE(r.run_mode, '') <> 'DRY_RUN'\n      AND r.ended_at IS NOT NULL\n)\nSELECT\n    CASE\n        WHEN me.ok_started_at IS NULL THEN 'FIRST_RUN'\n        WHEN me.last_started_at > me.ok_started_at THEN 'LAST_RUN_NOT_OK'\n        WHEN up.up_at >= DATEADD(MINUTE, -2, me.ok_started_at) THEN 'UPSTREAM_CHANGED'\n        WHEN @{pipeline().parameters.p_max_idle_min} > 0\n             AND DATEDIFF(MINUTE, me.ok_started_at, SYSUTCDATETIME()) >= @{pipeline().parameters.p_max_idle_min} THEN 'IDLE_BACKSTOP'\n        ELSE 'NO_DATA'\n    END AS gate_reason,\n    me.ok_started_at,\n    me.last_started_at,\n    up.up_at\nFROM me CROSS JOIN up;",
                    "type": "Expression"
                  }
                }
              ],
              "scriptBlockExecutionTimeout": "00:04:00",
              "database": "lh_vv_ctrl"
            },
            "externalReferences": {
              "connection": "[parameters('conn_lh_vv_bronze_by_sqlep')]"
            }
          },
          {
            "name": "If_HasWork_ENR",
            "type": "IfCondition",
            "dependsOn": [
              {
                "activity": "Get_Flow_Gate_ENR",
                "dependencyConditions": ["Succeeded"]
              }
            ],
            "typeProperties": {
              "expression": {
                "value": "@or(pipeline().parameters.p_force_run, not(equals(string(activity('Get_Flow_Gate_ENR').output.resultSets[0].rows[0].gate_reason), 'NO_DATA')))",
                "type": "Expression"
              },
              "ifFalseActivities": [
                {
                  "name": "Set_Msg_Skip_ENR",
                  "type": "SetVariable",
                  "dependsOn": [],
                  "policy": {"secureOutput": false, "secureInput": false},
                  "typeProperties": {
                    "variableName": "v_msg_skip",
                    "value": {
                      "value": "@concat('SKIP | ', pipeline().Pipeline, ' | reason=NO_DATA', ' | last_ok_started_at=', string(coalesce(activity('Get_Flow_Gate_ENR').output.resultSets[0].rows[0].ok_started_at, '')), ' | upstream_at=', string(coalesce(activity('Get_Flow_Gate_ENR').output.resultSets[0].rows[0].up_at, '')))",
                      "type": "Expression"
                    }
                  }
                }
              ],
              "ifTrueActivities": [
                {
                  "name": "Set_Msg_Run_ENR",
                  "type": "SetVariable",
                  "dependsOn": [],
                  "policy": {"secureOutput": false, "secureInput": false},
                  "typeProperties": {
                    "variableName": "v_msg",
                    "value": {
                      "value": "@concat('RUN | ', pipeline().Pipeline, ' | reason=', if(pipeline().parameters.p_force_run, 'FORCE', string(activity('Get_Flow_Gate_ENR').output.resultSets[0].rows[0].gate_reason)), ' | last_ok_started_at=', string(coalesce(activity('Get_Flow_Gate_ENR').output.resultSets[0].rows[0].ok_started_at, '')), ' | upstream_at=', string(coalesce(activity('Get_Flow_Gate_ENR').output.resultSets[0].rows[0].up_at, '')))",
                      "type": "Expression"
                    }
                  }
                },
                {
                  "name": "NB_00_ORCHES_SLV_TO_ENR_15P",
                  "type": "TridentNotebook",
                  "dependsOn": [
                    {
                      "activity": "Set_Msg_Run_ENR",
                      "dependencyConditions": ["Succeeded"]
                    }
                  ],
                  "policy": {
                    "timeout": "0.00:32:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                  },
                  "typeProperties": {
                    "notebookId": {
                      "value": "@pipeline().parameters.nb_orches_id",
                      "type": "Expression"
                    },
                    "workspaceId": {
                      "value": "@pipeline().parameters.workspace_id",
                      "type": "Expression"
                    },
                    "parameters": {
                      "p_pl_name": {
                        "value": {
                          "value": "@pipeline().Pipeline",
                          "type": "Expression"
                        },
                        "type": "string"
                      },
                      "p_run_id": {
                        "value": {
                          "value": "@pipeline().RunId",
                          "type": "Expression"
                        },
                        "type": "string"
                      },
                      "p_mode": {"value": "RUN", "type": "string"},
                      "p_max_parallel": {"value": "2", "type": "string"},
                      "p_node_timeout_min": {"value": "15", "type": "string"},
                      "p_dag_timeout_min": {"value": "25", "type": "string"},
                      "p_lock_timeout_min": {"value": "35", "type": "string"},
                      "p_force_nodes": {"value": "", "type": "string"},
                      "p_history_limit": {"value": "1000", "type": "string"},
                      "p_non_data_ops": {"value": "", "type": "string"}
                    }
                  }
                }
              ]
            }
          }
        ],
        "concurrency": 1,
        "parameters": {
          "nb_orches_id": {"type": "string"},
          "workspace_id": {"type": "string"},
          "p_force_run": {"type": "bool", "defaultValue": false},
          "p_max_idle_min": {"type": "int", "defaultValue": 0}
        },
        "variables": {
          "v_msg": {"type": "String"},
          "v_msg_skip": {"type": "String"}
        }
      },
      "dependsOn": []
    }
  ]
}
END_FILE

FILE: pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json
{
  "$schema": "http://schema.management.azure.com/schemas/2015-01-01/deploymentTemplate.json#",
  "contentVersion": "1.0.0.0",
  "parameters": {
    "conn_lh_vv_bronze_by_sqlep": {"type": "string"}
  },
  "variables": {},
  "resources": [
    {
      "name": "PL_VV_TRANS_SLV_TO_GLD_30M",
      "type": "pipelines",
      "apiVersion": "2018-06-01",
      "properties": {
        "activities": [
          {
            "name": "Validate_Notebook_Binding_GLD",
            "type": "IfCondition",
            "dependsOn": [],
            "typeProperties": {
              "expression": {
                "value": "@or(empty(pipeline().parameters.nb_orches_id), contains(pipeline().parameters.nb_orches_id, 'PENDING'), empty(pipeline().parameters.workspace_id), contains(pipeline().parameters.workspace_id, 'PENDING'))",
                "type": "Expression"
              },
              "ifTrueActivities": [
                {
                  "name": "Fail_Bad_Binding_GLD",
                  "type": "Fail",
                  "dependsOn": [],
                  "typeProperties": {
                    "message": "nb_orches_id or workspace_id is empty or a placeholder",
                    "errorCode": "BAD_NOTEBOOK_BINDING"
                  }
                }
              ]
            }
          },
          {
            "name": "Get_Flow_Gate_GLD",
            "type": "Script",
            "dependsOn": [
              {
                "activity": "Validate_Notebook_Binding_GLD",
                "dependencyConditions": ["Succeeded"]
              }
            ],
            "policy": {
              "timeout": "0.00:05:00",
              "retry": 1,
              "retryIntervalInSeconds": 30,
              "secureOutput": false,
              "secureInput": false
            },
            "typeProperties": {
              "scripts": [
                {
                  "type": "Query",
                  "text": {
                    "value": "WITH up_pl AS (\n    SELECT DISTINCT p.pl_name\n    FROM dbo.ctrl_mng_pipeline_config AS m\n    INNER JOIN dbo.ctrl_mng_pipeline_config AS p\n        ON p.trg_schema = m.src_schema AND p.trg_tbl = m.src_tbl\n    WHERE m.pl_name = '@{pipeline().Pipeline}'\n      AND m.is_active = 1\n      AND p.is_active = 1\n      AND p.pl_name <> m.pl_name\n),\nme AS (\n    SELECT\n        MAX(CASE WHEN status IN ('SUCCESS', 'NO_DATA') THEN started_at END) AS ok_started_at,\n        MAX(started_at) AS last_started_at\n    FROM dbo.ctrl_log_run\n    WHERE pl_name = '@{pipeline().Pipeline}'\n      AND run_mode = 'RUN'\n      AND status <> 'SKIPPED_CONCURRENT'\n),\nup AS (\n    SELECT MAX(r.ended_at) AS up_at\n    FROM dbo.ctrl_log_run AS r\n    INNER JOIN up_pl AS u ON u.pl_name = r.pl_name\n    WHERE r.status NOT IN ('NO_DATA', 'SKIPPED_CONCURRENT', 'RUNNING')\n      AND COALESCE(r.run_mode, '') <> 'DRY_RUN'\n      AND r.ended_at IS NOT NULL\n)\nSELECT\n    CASE\n        WHEN me.ok_started_at IS NULL THEN 'FIRST_RUN'\n        WHEN me.last_started_at > me.ok_started_at THEN 'LAST_RUN_NOT_OK'\n        WHEN up.up_at >= DATEADD(MINUTE, -2, me.ok_started_at) THEN 'UPSTREAM_CHANGED'\n        WHEN @{pipeline().parameters.p_max_idle_min} > 0\n             AND DATEDIFF(MINUTE, me.ok_started_at, SYSUTCDATETIME()) >= @{pipeline().parameters.p_max_idle_min} THEN 'IDLE_BACKSTOP'\n        ELSE 'NO_DATA'\n    END AS gate_reason,\n    me.ok_started_at,\n    me.last_started_at,\n    up.up_at\nFROM me CROSS JOIN up;",
                    "type": "Expression"
                  }
                }
              ],
              "scriptBlockExecutionTimeout": "00:04:00",
              "database": "lh_vv_ctrl"
            },
            "externalReferences": {
              "connection": "[parameters('conn_lh_vv_bronze_by_sqlep')]"
            }
          },
          {
            "name": "If_HasWork_GLD",
            "type": "IfCondition",
            "dependsOn": [
              {
                "activity": "Get_Flow_Gate_GLD",
                "dependencyConditions": ["Succeeded"]
              }
            ],
            "typeProperties": {
              "expression": {
                "value": "@or(pipeline().parameters.p_force_run, not(equals(string(activity('Get_Flow_Gate_GLD').output.resultSets[0].rows[0].gate_reason), 'NO_DATA')))",
                "type": "Expression"
              },
              "ifFalseActivities": [
                {
                  "name": "Set_Msg_Skip_GLD",
                  "type": "SetVariable",
                  "dependsOn": [],
                  "policy": {"secureOutput": false, "secureInput": false},
                  "typeProperties": {
                    "variableName": "v_msg_skip",
                    "value": {
                      "value": "@concat('SKIP | ', pipeline().Pipeline, ' | reason=NO_DATA', ' | last_ok_started_at=', string(coalesce(activity('Get_Flow_Gate_GLD').output.resultSets[0].rows[0].ok_started_at, '')), ' | upstream_at=', string(coalesce(activity('Get_Flow_Gate_GLD').output.resultSets[0].rows[0].up_at, '')))",
                      "type": "Expression"
                    }
                  }
                }
              ],
              "ifTrueActivities": [
                {
                  "name": "Set_Msg_Run_GLD",
                  "type": "SetVariable",
                  "dependsOn": [],
                  "policy": {"secureOutput": false, "secureInput": false},
                  "typeProperties": {
                    "variableName": "v_msg",
                    "value": {
                      "value": "@concat('RUN | ', pipeline().Pipeline, ' | reason=', if(pipeline().parameters.p_force_run, 'FORCE', string(activity('Get_Flow_Gate_GLD').output.resultSets[0].rows[0].gate_reason)), ' | last_ok_started_at=', string(coalesce(activity('Get_Flow_Gate_GLD').output.resultSets[0].rows[0].ok_started_at, '')), ' | upstream_at=', string(coalesce(activity('Get_Flow_Gate_GLD').output.resultSets[0].rows[0].up_at, '')))",
                      "type": "Expression"
                    }
                  }
                },
                {
                  "name": "NB_00_ORCHES_SLV_TO_GLD_30M",
                  "type": "TridentNotebook",
                  "dependsOn": [
                    {
                      "activity": "Set_Msg_Run_GLD",
                      "dependencyConditions": ["Succeeded"]
                    }
                  ],
                  "policy": {
                    "timeout": "0.00:52:00",
                    "retry": 0,
                    "retryIntervalInSeconds": 30,
                    "secureOutput": false,
                    "secureInput": false
                  },
                  "typeProperties": {
                    "notebookId": {
                      "value": "@pipeline().parameters.nb_orches_id",
                      "type": "Expression"
                    },
                    "workspaceId": {
                      "value": "@pipeline().parameters.workspace_id",
                      "type": "Expression"
                    },
                    "parameters": {
                      "p_pl_name": {
                        "value": {
                          "value": "@pipeline().Pipeline",
                          "type": "Expression"
                        },
                        "type": "string"
                      },
                      "p_run_id": {
                        "value": {
                          "value": "@pipeline().RunId",
                          "type": "Expression"
                        },
                        "type": "string"
                      },
                      "p_mode": {"value": "RUN", "type": "string"},
                      "p_max_parallel": {"value": "3", "type": "string"},
                      "p_node_timeout_min": {"value": "20", "type": "string"},
                      "p_dag_timeout_min": {"value": "45", "type": "string"},
                      "p_lock_timeout_min": {"value": "90", "type": "string"},
                      "p_force_nodes": {"value": "", "type": "string"},
                      "p_history_limit": {"value": "1000", "type": "string"},
                      "p_non_data_ops": {"value": "", "type": "string"}
                    }
                  }
                }
              ]
            }
          }
        ],
        "concurrency": 1,
        "parameters": {
          "nb_orches_id": {"type": "string"},
          "workspace_id": {"type": "string"},
          "p_force_run": {"type": "bool", "defaultValue": false},
          "p_max_idle_min": {"type": "int", "defaultValue": 0}
        },
        "variables": {
          "v_msg": {"type": "String"},
          "v_msg_skip": {"type": "String"}
        }
      },
      "dependsOn": []
    }
  ]
}
END_FILE

The GLD notebook parameter values (3, 20, 45, 90) are the defaults in the parameter cell of `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb`. The 52-minute activity timeout keeps the ENR margin (DAG timeout plus 7) and stays below the 90-minute lock. A 45-minute DAG timeout is longer than the 30-minute cadence; `concurrency = 1` holds the next trigger. Tuning those values needs runtime durations and is not part of this task.
