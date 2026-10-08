# Context versus implementation consistency audit

Task: `20261008-context-implementation-consistency-review`

Main model recorded: `grok-4.7` with high reasoning.

This audit is read-only. It does not treat the context pack or the notebooks as automatically correct.

Preliminary verdict before specialist review: `USER_DECISION`.

`PASS` is not available. Several P1 items are open, two written contracts disagree, and three live facts are `NOT_VERIFIABLE`.

## 1. Executive summary

The bronze-to-silver extract path that is actually in the repository largely matches the context pack updated on 08/10/2026. It does not match every platform invariant in `AGENTS.md` or `.cursor/rules/20-data-pipeline.mdc`.

What matches:

- FL_00 pre-check reads `ctrl_mng_pipeline_config` and `ctrl_mng_watermark`, then lists `_delta_log` under `Files/_delta_src/<table>`.
- A source with a stored version and no newer commit files does not start the notebook.
- ForEach is sequential. The only notebook activity is `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, with `partner_raw_data` fixed in the activity.
- Extract notebooks have a parameter cell, substitute a blank `run_id` with `exec_id`, log `SUCCESS` / `NO_DATA` / `FAILED`, and advance the watermark only after the table body, only forward, and only while the lock is still held.
- Partner and third-party MERGE sources are reduced to one row per match key before MERGE.
- Silver L1 names `slv_pn_*` and `slv_3p_poi_*` in `NB_CREATE_DDL` match the names in the control-table context.

What does not match, or is missing:

- The pipeline rule requires a Switch on `item().src_tbl` and `run_id = @pipeline().RunId`. The JSON has no Switch, `run_id` is `""`, and `pl_name` is a literal.
- The same pipeline activity ignores `item()`. A `poi_raw_event` config row with new commits still starts the partner notebook. The third-party notebook is never called.
- Notebook lock timeout is 60 minutes. The notebook activity timeout is 12 hours. A later run can take the lock while the first activity is still allowed to run.
- `NB_00` calls `close_stale_runs` before `acquire_flow_lock`. The orchestrator context says the stale-run update happens after the lock is held.
- Gold and silver L2 node notebooks, the hourly pipeline, and `NB_SETUP_GOLD_POI_1H` are not in the repository. Repo DDL does not create `output_versions_json` or `src_versions_json`. The transform library drops columns that are not on the live table.
- `poi_uid` appears only in `AGENTS.md`. Partner `poi_id = uuid_format(md5('partner_portal' || business_service_id))` is documented and is not implemented in any notebook here. Third-party `poi_id` is implemented as UUID-formatted `md5(concat(source_name, source_id))` without language.
- No `sql/**/*.sql` or `sql/**/*.pg.sql` files exist. `fabric/notebooks` and `fabric/pipelines` do not exist.

Source-of-truth conflicts are unresolved. See section 9.

## 2. Artifacts checked

| Area | Path | Result |
|---|---|---|
| Constitution | `AGENTS.md` section 9 | Read |
| Pipeline rule | `.cursor/rules/20-data-pipeline.mdc` | Read |
| Context index | `docs/context/README.md`, `docs/context/00_README.md` | Read |
| Data model and naming | `docs/context/01_DATA_MODEL.md`, `docs/context/02_NAMING_CONVENTION.md` | Read |
| Control tables | `docs/context/CTRL_TABLES_CONTEXT.md` | Read; file is present and specifies 7 tables, grains, writers, and watermark rules |
| Notebook notes | `docs/context/NB_*.md` | Read for contracts cited below |
| Read-only snapshot script | `docs/context/CHECK_CTRL_SNAPSHOT.py` | Present; not executed |
| Extract library | `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` | 29 cells |
| Partner extract | `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` | 15 cells |
| Third-party extract | `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` | 15 cells |
| Transform library | `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` | 16 cells |
| Silver-to-gold orchestrator | `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb` | 4 cells |
| Control DDL | `notebooks/NB_CREATE_DDL.ipynb` | 26 cells |
| Pipeline | `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json` | Single-line deployment template |
| Pipeline manifest | `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/manifest.json` | Diagram metadata only |

Notebook cell numbers below are 0-based. Line numbers are lines inside that cell.

## 3. Missing inputs

| Requested path | Status |
|---|---|
| `fabric/notebooks/**/*.Notebook/` | `MISSING_INPUT` |
| `fabric/pipelines/**/*.DataPipeline/` | `MISSING_INPUT` |
| `sql/**/*.sql` | `MISSING_INPUT` |
| `sql/**/*.pg.sql` | `MISSING_INPUT` |
| `claude/**` cited by `docs/context/00_README.md` lines 46-56 and `CTRL_TABLES_CONTEXT.md` line 3 | `MISSING_INPUT` |
| `pipelines/PL_VV_TRANSFORM_SLV_TO_GLD_1H/` | Withdrawn 08/10/2026. User: processing is not finalized, so this pipeline is out of scope. Removed from `docs/context`. |
| `NB_SLV_POI*`, `NB_GLD_SRV_*`, `NB_SETUP_GOLD_POI_1H` | Withdrawn 08/10/2026. User: these notebooks are out of scope. Removed from `docs/context`. |

`docs/context/CTRL_TABLES_CONTEXT.md` itself is not missing. Historical row counts in that file are explicitly through 05/10/2026 and were not re-read from Fabric.

## 4. Traceability matrix

| Context ID | Context statement | Context evidence | Implementation evidence | Status | Severity | Notes |
|---|---|---|---|---|---|---|
| INV-01 | Bronze, silver, and gold are separate lakehouses. Bronze holds raw and `ctrl`. Silver holds cleansing and canonical entities. Gold is expose/sync only. | `AGENTS.md` 187-191; `docs/context/00_README.md` 27-33; `docs/context/01_DATA_MODEL.md` 168-170 | Extract notebooks write `slv_pn_*` / `slv_3p_poi_*`. Transform lib `merge_target` is generic. Gold notebooks are absent. | `PARTIAL_MATCH` | P1 | L1 placement matches. Gold "sync only" cannot be checked. See F-P1-05. |
| INV-02 | Silver prefixes `slv_pn_` and `slv_3p_`. Gold prefix `gld_`. | `AGENTS.md` 192; `docs/context/02_NAMING_CONVENTION.md` 16-21 | `NB_CREATE_DDL` seeds the L1 names listed in `CTRL_TABLES_CONTEXT.md` 91-111. No `gld_*` identifier in that notebook. | `PARTIAL_MATCH` | P1 | L1 names match. Gold table notebooks are `NOT_IMPLEMENTED` in this repo. |
| INV-03 | `poi_uid = md5(source_name + source_id)` and never includes language. | `AGENTS.md` 193 | No `poi_uid` in notebooks or context pack. | `NOT_IMPLEMENTED` | P2 | Only the constitution uses this name. See F-P2-03. |
| INV-04 | Third-party `poi_id = md5(concat(source_name, source_id))`. | `AGENTS.md` 194; `docs/context/01_DATA_MODEL.md` 182 | `NB_CREATE_DDL` cell 16 defines `POI_ID` as `HASH_MD5_UUID` on `_doc.source_name,_doc.source_id`. `NB_LIB_EXTRACT_RAWDATA` cell 12 `derived_sql` formats `md5(concat(...))` as 8-4-4-4-12. | `PARTIAL_MATCH` | P2 | Inputs exclude language and match the context formula, including UUID dashes. `AGENTS.md` does not mention `uuid_format` for this id. |
| INV-05 | Partner `poi_id = uuid_format(md5('partner_portal' \|\| business_service_id))`. | `AGENTS.md` 195; `docs/context/01_DATA_MODEL.md` 183 | `uuid_md5` exists in `NB_LIB_TRANSFORM_SLV_GLD` cell 15. No `partner_portal` literal in any notebook. Node notebook that would call it is missing. | `NOT_IMPLEMENTED` | P1 | Formula is documented. Caller is `MISSING_INPUT`. See F-P1-05. |
| INV-06 | Notebook hierarchy is NB00, then NBx0, then NBxy, with no deeper tier. | `AGENTS.md` 196 | Repo uses `NB_LIB_*`, `NB_EXTRACT_*`, `NB_00_ORCHES_*`. `docs/context/02_NAMING_CONVENTION.md` 30-39 documents that scheme. | `MISMATCH` | P2 | Constitution and context pack disagree. Implementation follows the context pack. See F-P2-03. |
| INV-07 | Extract and orchestrator notebooks expose a parameter cell. | `docs/context/02_NAMING_CONVENTION.md` 146-154; partner and 3P context parameter tables | Partner cell 1, third-party cell 1, and `NB_00` cell 1 are tagged `parameters`. | `MATCH` |  | Pipeline overrides only the partner activity, and only with literals. |
| INV-08 | `run_id` from the pipeline is `@pipeline().RunId`. Blank manual runs become `exec_id`. | `.cursor/rules/20-data-pipeline.mdc` 12; `docs/context/02_NAMING_CONVENTION.md` 154; `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` 37 and 163 | Pipeline activity parameter `run_id` value is `""`. Partner `build_context` cell 12 uses `run_id or exec_id`. | `MISMATCH` | P1 | Value propagation from the pipeline run is absent. Blank-to-`exec_id` behavior matches the extract context. See F-P1-06. |
| INV-09 | `pl_name` is `@pipeline().Pipeline`. | `.cursor/rules/20-data-pipeline.mdc` 12; `docs/context/02_NAMING_CONVENTION.md` 55 and 154 | Pipeline sets literal `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. Config query uses `pipeline().parameters.p_pipeline_code`, whose default is that same name. | `PARTIAL_MATCH` | P2 | Today's string matches the pipeline name. It is not the pipeline-name expression. |
| INV-10 | Notebook exit payload is the run summary. Failure statuses fail the activity. | Partner notebook cell 13 comment; `NB_LIB_EXTRACT_RAWDATA` cell 22 `build_summary`; `.cursor/rules/20-data-pipeline.mdc` 17 | Partner and third-party cell 13 raise on `FAILED`, `PARTIAL_FAILED`, `SKIPPED_CONCURRENT`, then `notebookutils.notebook.exit` only if not raised. Pipeline JSON has no activity that reads `exitValue`. `NB_00` cell 3 only prints JSON. `orchestrate` returns `SKIPPED_CONCURRENT` without raising. | `PARTIAL_MATCH` | P2 | Extract failure is signaled by the exception, not by a parsed exit. See F-P2-04. |
| INV-11 | Pre-check reads config and watermark, then `_delta_log` through `Files/_delta_src/<table>`. | `AGENTS.md` 197; `CTRL_TABLES_CONTEXT.md` 43-45 | Activities `Get_Config_4Run`, `Lookup_WM`, `GM_DeltaLog`. Folder expression `_delta_src/{src_tbl}/_delta_log` on the Files root. | `MATCH` |  | `Get_Config_4Run` and `Lookup_WM` have empty `dependsOn` and both must succeed before `ForEach_Source`. |
| INV-12 | No new data means no Spark startup. | `AGENTS.md` 197; pipeline rule line 9 | `If_HasWork` expression is empty `v_last_ver` OR `FilteredItemsCount > 0`. False branch is only `Set_Msg_Skip`. | `MATCH` |  | A stored version and zero new `*.json` commit files do not start `TridentNotebook`. First run (empty version) does start it. |
| INV-13 | `ctrl_mng_pipeline_config` and `ctrl_mng_watermark` are the pre-check and extract control tables. | `CTRL_TABLES_CONTEXT.md` 9-12 and 49-174 | Config query filters `pl_name` and `is_active = 1`. Lookup reads `ctrl.ctrl_mng_watermark` with `firstRowOnly: false`. Extract calls `load_watermark`. | `MATCH` |  | Semantics used here are the ones written in the control-table context. |
| INV-14 | FL_00 routes each source through ForEach, If_HasWork, and Switch on `item().src_tbl`. | `.cursor/rules/20-data-pipeline.mdc` 10 | JSON has `ForEach_Source` and `If_HasWork`. No `Switch` activity. Notebook parameters are constants, not `item().src_tbl`. | `MISMATCH` | P1 | Context pack was aligned to say there is no Switch. See F-P1-02. |
| INV-15 | ForEach concurrency is sequential and must be defined against locks and shared control tables. | `docs/context/00_README.md` 29; `CTRL_TABLES_CONTEXT.md` 45; pipeline rule line 15 | `ForEach_Source.typeProperties.isSequential` is `true`. | `MATCH` |  | The DDL comment in `NB_CREATE_DDL` cell 19 says partner and third-party MERGE run in parallel inside ForEach. That comment disagrees with the JSON. See F-P3-01. |
| INV-16 | Activities have explicit timeout and retry. Notebook timeout must stay below the lock timeout. | Pipeline rule line 12; `docs/context/NB_LIB_EXTRACT_RAWDATA.md` 250; partner parameter comment in cell 1 line 17 | `Get_Config_4Run`, `Lookup_WM`, `GM_DeltaLog`, and the notebook use timeout `0.12:00:00` and `retry` 0. `running_timeout_minutes` default is 60. | `MISMATCH` | P1 | Fields exist. 12 hours is longer than 60 minutes. See F-P1-01. |
| INV-17 | A failed notebook or failed state update must not be reported as pipeline success. | Pipeline rule line 16; partner cell 13 | The notebook raises before exit on failure. ForEach has no continue-on-error policy. Skip branch can succeed without a control-log row. | `PARTIAL_MATCH` | P2 | Pipeline failure propagation for a raised notebook matches. Pipeline skip is only a variable write. `NB_00` concurrent skip does not raise. |
| INV-18 | Partner MERGE source has one row per entity key. Match is the table key. | `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` 117-118 | Cell 8 `resolve_latest` uses `row_number` over `partitionBy("_entity_key")` and keeps `_rn = 1`. `build_merge_sql` uses `ON` the `spec.key_cols`. | `MATCH` |  | Uniqueness is by `_entity_key`. Match columns are `key_cols`. Context says those are the same business key. |
| INV-19 | Third-party MERGE source has one row per table key, and updates only when the document is newer. | `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` 16 and 135 | Cell 8 `resolve_latest` partitions by `spec.key_cols`. `build_merge_sql` matches on those columns and updates only when crawled time/event id is newer or equal. | `MATCH` |  | |
| INV-20 | Silver L2 and gold MERGE use the node primary key and `row_hash`. Duplicate keys are blocked by the node quality gate. | `docs/context/01_DATA_MODEL.md` 144-176; `NB_LIB_TRANSFORM_SLV_GLD.md` | `sql_merge_target` in cell 11 matches `spec.pk` and updates when `row_hash` differs. `quality_gate` can count duplicate keys if the node spec defines `unique_checks`. No node notebook supplies a spec. | `NOT_VERIFIABLE` | P1 | Library behavior is present. Target grain for the eight nodes is not in the repo. |
| INV-21 | Extract watermark advances only on `SUCCESS` or `NO_DATA`, only forward, after the business body, and only while this run holds the lock. Failure leaves the version pointer unchanged. | `CTRL_TABLES_CONTEXT.md` 196-197; `NB_LIB_EXTRACT_RAWDATA.md` 57-67 | `run_controlled` cell 28 orders body, then `finalize_watermark`, then `write_run_log`, then `release_lock`. `finalize_watermark` cell 22 applies the forward predicate and `lock_exec_id = exec_id`. | `MATCH` |  | `PARTIAL_FAILED` is stored on the watermark row as `FAILED` and does not move `last_src_version`. Table MERGE for successful tables has already happened inside the body. |
| INV-22 | Extract lock is an atomic update on the source watermark row and is released in `finally` only by the holder. | `CTRL_TABLES_CONTEXT.md` 193; `NB_LIB_EXTRACT_RAWDATA.md` 191-195 | `acquire_lock` / `release_lock` in cell 22. Release predicate is `lock_exec_id = exec_id`. | `MATCH` |  | Expiry uses `running_timeout_minutes` (60), which is shorter than the activity timeout. See F-P1-01. |
| INV-23 | Flow lock expiry is `lock_at` plus the caller timeout. Release clears the lock only for the holder. | `docs/context/README.md` 9; `NB_LIB_TRANSFORM_SLV_GLD.md` 114-117 | `acquire_flow_lock` and `release_flow_lock` in cell 9. `_lock_expired_sql(timeout_min)` uses the caller timeout. `NB_00` passes `p_lock_timeout_min` default `"90"`. | `MATCH` |  | The hourly pipeline that would pass this parameter is `MISSING_INPUT`. |
| INV-24 | `NB_00` marks other `RUNNING` rows `ABANDONED` only after it holds the flow lock. | `docs/context/NB_00_ORCHES_SLV_TO_GLD.md` 63-64 | `orchestrate` in cell 13 calls `close_stale_runs` and then `acquire_flow_lock`. | `MISMATCH` | P1 | Order is visible in source. Harm under overlap is a hypothesis. See F-P1-04. |
| INV-25 | Logging covers `SUCCESS`, `NO_DATA`, and `FAILED` on the run log. | `docs/context/02_NAMING_CONVENTION.md` 128-131; `CTRL_TABLES_CONTEXT.md` 358 | `decide_status` and `write_run_log` MERGE on `exec_id`. Status set includes those values plus `PARTIAL_FAILED`, `SKIPPED_CONCURRENT`, `ABANDONED`. | `PARTIAL_MATCH` | P2 | Notebook runs log those statuses. Pipeline `NO_NEW_COMMITS` only sets `v_msg_skip` and writes no `ctrl_log_run` row. |
| INV-26 | Partial table failure does not advance the extract watermark. Retry remains safe because state ignores already applied entities. | `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` 16 and 130 | `decide_status` returns `PARTIAL_FAILED` when some processed tables fail. `finalize_watermark` treats that as not success. `commit` is still invoked from `process_run` before the controller finalizes the watermark. | `PARTIAL_MATCH` | P2 | Confirmed: watermark does not move. Idempotent retry depends on `commit_state` completing for the tables that already merged. A crash between target MERGE and state MERGE is not proven from a runtime trace. |
| INV-27 | Fabric capacity is F16 and is shared. Extract parallelism and gold fan-out must fit that capacity. | `AGENTS.md` 187; `docs/context/00_README.md` 27 | Partner `max_parallel = 12`. `NB_00` `p_max_parallel = "3"`. No capacity guard in code. | `NOT_VERIFIABLE` | P2 | The knobs exist. Whether they fit a shared F16 was not measured in this task. |
| INV-28 | One notebook per source, selected inside the pipeline. | `docs/context/02_NAMING_CONVENTION.md` 35; `docs/context/00_README.md` 29 | Third-party notebook exists. FL_00 never references it. | `NOT_IMPLEMENTED` | P1 | The context index also says this pipeline calls only the partner notebook. See F-P1-02. |
| INV-29 | Hourly silver-to-gold pipeline calls `NB_00` with `p_pl_name` and `p_run_id`. | `docs/context/NB_00_ORCHES_SLV_TO_GLD.md` 14 and 31-39 | `NB_00` notebook exists. Pipeline directory does not. | `MISSING_INPUT` | P1 | Orchestrator code cannot be tied to a pipeline artifact. |
| INV-30 | Gold-log columns exist: `output_versions_json`, `src_versions_json`, `trg_version`, `deactivated_rows`, `qg_json`. | `CTRL_TABLES_CONTEXT.md` 366-370 and 431-435 | `NB_CREATE_DDL` cell 19 CREATE statements omit them. `require_ctrl_columns` in transform cell 3 raises `ConfigError` when any new log column is missing. Setup notebook is missing. | `MISMATCH` | P1 | A clean deploy fails before `NB_00` plans. Live DEV may already have the columns. See F-P1-03. |
| INV-31 | PostgreSQL sync SQL exists for gold expose. | `AGENTS.md` 191 | `sql/` directory absent. | `MISSING_INPUT` | P2 | No SQL artifact to compare. |
| INV-32 | Control-table DDL in the repo matches the control-table context for the original extract columns, including `lock_exec_id` and `lock_at`. | `CTRL_TABLES_CONTEXT.md` 56-70 and 154-174 | `NB_CREATE_DDL` cells 5 and 8. | `MATCH` |  | Gold columns added later in the context are the exception in INV-30. Context still points DDL authorship at missing `claude/NB_CREATE_DDL.ipynb`. |

## 5. Findings

### P0

None confirmed from repository evidence alone.

### P1

| ID | Finding | Evidence | Failure scenario |
|---|---|---|---|
| F-P1-01 | Lock window is 60 minutes and the notebook activity window is 12 hours. | Pipeline notebook policy `timeout` `0.12:00:00`, `retry` 0. Partner cell 1 `running_timeout_minutes = 60`. `acquire_lock` expiry SQL in extract cell 22. | Hypothesis: a second pipeline start after 60 minutes takes the watermark lock while the first Spark run still holds writers. Confirmed: the two timeouts disagree. |
| F-P1-02 | ForEach does not route by source table. | `ForEach_Source` items come from config rows. `If_HasWork` true branch always runs activity `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` with `src_tbl` `partner_raw_data`. No Switch. | Confirmed: a `poi_raw_event` item with new commit files starts the partner notebook. Third-party extract never runs from this pipeline. Whether live config still has that row active is `NOT_VERIFIABLE`. |
| F-P1-03 | Repo DDL does not create the gold-log columns, and `NB_00` refuses to start without them. | `CTRL_TABLES_CONTEXT.md` 366-435 versus `NB_CREATE_DDL` cell 19. `require_ctrl_columns` in `NB_LIB_TRANSFORM_SLV_GLD` cell 3 raises `ConfigError` listing every missing column. `NB_SETUP_GOLD_POI_1H` is `MISSING_INPUT`. | Confirmed for a clean environment: planning does not start. Whether DEV already has the columns is `NOT_VERIFIABLE`. |
| F-P1-04 | Stale-run abandonment runs before the flow lock is acquired. | `NB_00_ORCHES` context lines 63-64 versus `orchestrate` cell 13: `close_stale_runs` then `acquire_flow_lock`. | Hypothesis: two overlapping `NB_00` runs can mark each other's `RUNNING` log `ABANDONED` before either owns `wm_flow__*`. The call order is confirmed. |
| F-P1-05 | Silver L2, gold node notebooks, and the partner `poi_id` formula are not in the repo. | `01_DATA_MODEL.md` 146-176 and 183. `uuid_md5` has no `partner_portal` caller. Eight notebook paths are `MISSING_INPUT`. | The hourly DAG described in context cannot be rebuilt from this repository. Identity for partner POIs is not implemented here. |
| F-P1-06 | Pipeline `run_id` is empty, so extract logs store `exec_id` instead of the pipeline run id. | Pipeline parameter `run_id` value `""`. Partner cell 12 `run_id or exec_id`. Naming convention line 154 and pipeline rule line 12 require `@pipeline().RunId`. | Confirmed: `ctrl_log_run.run_id` will not equal `pipeline().RunId` for FL_00. Correlation across systems is lost. Context partner page documents the empty string on purpose, so the written contracts disagree. |

### P2

| ID | Finding | Evidence |
|---|---|---|
| F-P2-03 | `poi_uid` and the NB00 / NBx0 / NBxy hierarchy exist in `AGENTS.md` and not in the implementation or the context pack. | `AGENTS.md` 193-196; `02_NAMING_CONVENTION.md` 30-39. |
| F-P2-04 | Exit JSON is not parsed by the pipeline. `NB_00` does not call `notebook.exit`. Concurrent skip raises in extract and returns normally in `orchestrate`. | Partner cell 13; `NB_00` cell 3; `orchestrate` cell 13 return on `SKIPPED_CONCURRENT`. |
| F-P2-05 | Context authorship paths under `claude/` are `MISSING_INPUT`. The notebooks that match those names are under `notebooks/`. | `00_README.md` 46-56; `CTRL_TABLES_CONTEXT.md` line 3. |
| F-P2-06 | Shared F16 limits are stated and not enforced. `max_parallel` 12 is only a parameter. | `AGENTS.md` 187; partner cell 1. |

### P3

| ID | Finding | Evidence |
|---|---|---|
| F-P3-01 | `ctrl_cdc_state` DDL comment says partner and third-party MERGE run in parallel inside ForEach. The pipeline ForEach is sequential. | `NB_CREATE_DDL` cell 19 partition comment; JSON `isSequential: true`. |

## 6. Context statements with no implementation

- Switch on `item().src_tbl` (pipeline rule).
- `run_id = @pipeline().RunId` and `pl_name = @pipeline().Pipeline` as expressions.
- `poi_uid`.
- Partner `poi_id` formula.
- Notebook names `NB_SLV_*`, `NB_GLD_*`, `NB_SETUP_GOLD_POI_1H`.
- Pipeline `PL_VV_TRANSFORM_SLV_TO_GLD_1H`.
- PostgreSQL sync SQL.
- Gold serving tables as executable notebooks.

## 7. Implementation behavior not documented as the platform invariant

These behaviors are documented in the 08/10/2026 context pack and differ from `AGENTS.md` or the pipeline rule:

- FL_00 hardcodes one partner notebook and has no Switch (`docs/context/README.md` line 9).
- Pipeline `run_id` is intentionally empty (`NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` line 163).
- Flow-lock expiry is computed from `lock_at` plus the caller timeout. The watermark row does not store `LOCK_EXPIRES_AT` (`CTRL_TABLES_CONTEXT.md` line 183).
- Third-party `poi_id` is UUID-formatted.

`UNDOCUMENTED_IMPLEMENTATION` was not used as a matrix status because each of these has a context sentence. The gap is between constitution/rule and context, not between code and every document.

## 8. Mismatches

| Topic | Context may be stale | Implementation may be wrong | Both incomplete | Not enough evidence |
|---|---|---|---|---|
| Switch and hardcoded partner activity | Pipeline rule still requires Switch. Context pack was edited to describe the JSON. | JSON cannot select the third-party notebook. | Yes. Rule, pack, and JSON cannot all be current. | Live `is_active` rows are unknown. |
| `run_id` / `pl_name` expressions | Naming convention and pipeline rule require expressions. Partner context describes literals. | Empty `run_id` drops the pipeline run id. | Yes. |  |
| Lock 60 minutes versus activity 12 hours | Extract pain-point text says activity timeout is shorter than the lock. Partner ops text says 12 hours. | Both numbers are implemented. | Yes. The two context sentences disagree with each other. | Overlapping triggers are unknown. |
| `close_stale_runs` order | Orchestrator context says after the lock. | Code runs before the lock. | The loser is not proven without a concurrency trace. | No hourly pipeline in repo. |
| Gold-log columns | Context DDL includes them and delegates ALTER to a missing notebook. | `NB_CREATE_DDL` omits them. | Repo cannot create the documented schema by itself. | DEV column presence is unknown. |
| `poi_uid` and NB00 hierarchy | `AGENTS.md` may be a shortened invariant that the context pack replaced. | Code follows the context pack. | Yes. | User must pick the source of truth. |
| Partner `poi_id` | Documented as decided on 05/10. | Not implemented in this repo. | Node notebook missing, so neither side can be executed here. |  |

## 9. Confirmed root cause or hypothesis

Confirmed from repository text:

- FL_00 has no Switch and always calls the partner notebook with fixed parameters.
- `run_id` passed by that activity is an empty string.
- Activity timeout `0.12:00:00` and `running_timeout_minutes = 60` are both present.
- `close_stale_runs` is invoked before `acquire_flow_lock`.
- `NB_CREATE_DDL` does not create the five gold-log columns. `require_ctrl_columns` stops `NB_00` before planning when they are absent. `append_rows` would drop unknown keys, and the orchestrator does not rely on that silent path.
- `poi_uid` and the partner `poi_id` formula have no notebook implementation in this repo.

Hypothesis, not a confirmed root cause:

- A second FL_00 trigger can steal the extract lock and produce two writers. Needs the schedule probe.
- Missing gold-log columns in DEV would stop `NB_00` with `ConfigError`. Needs the column probe to see whether DEV already passed that check.
- `AGENTS.md` and the pipeline rule were not updated when the context pack was aligned on 08/10/2026. That is consistent with the text dates, and it is still an inference about intent.

## 10. Evidence or probes still required

1. `ctrl-column-presence` in Fabric DEV. List whether `output_versions_json`, `src_versions_json`, `trg_version`, `deactivated_rows`, and `qg_json` exist. No row samples.
2. `fl00-active-sources`. Counts of active `ctrl_mng_pipeline_config` rows by `src_tbl` for `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`.
3. `fl00-schedule-overlap`. Whether a new FL_00 run can start before the 12-hour activity timeout ends.

`CTRL_TABLES_CONTEXT.md` is sufficient to interpret those results. Do not invent column meanings beyond that file.

User decision required before any fix task:

- Is the source of truth the pipeline rule (Switch, expression `run_id` and `pl_name`) or the 08/10/2026 context pack (no Switch, literal partner parameters, empty `run_id`)?
- Is `poi_uid` still a required identifier, or has `poi_id` replaced it?
- Is the NB00 / NBx0 / NBxy hierarchy required, or is the `NB_LIB` / `NB_EXTRACT` / `NB_00_ORCHES` / `NB_<TABLE>` scheme the standard?
- Should the missing node notebooks and hourly pipeline be imported before another consistency pass?

## 11. Reviewer verdict

`python scripts/vv.py run-gate 20261008-context-implementation-consistency-review --round 1 --timeout 2700` failed before it could accept a review.

Exact runner error:

```text
AUTOMATED GATE FAIL: Codex review changed the repository unexpectedly.
```

The immutability check compares `git status --porcelain` before and after the Codex process. During that process `reviews/round-1.md` appeared, so the runner discarded the result and did not commit gate state. Task state is restored to `reviewing` with `specialist_review: pending` and `risk_gate: pending`.

`reviews/round-1.md` is an unaccepted draft. It names model `gpt-5.6-sol` at high effort and lists `spark-runtime-reviewer`, `fabric-pipeline-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`, and `risk-gate`. Its draft verdict is `USER_DECISION`. It also records one P0, `VSVN-R1-001`: target MERGE is not fenced by the lock, while the lease is 60 minutes and the activity timeout is 12 hours. That P0 was not adopted into `open_findings` because the gate did not complete.

## 12. Risk-gate status

Required because `risk_level` is `high`. Official status: `pending`. The unaccepted draft says risk-gate ran and returned `USER_DECISION`.

## 13. Final verdict

`USER_DECISION`

Blocking reasons:

- Open P1 findings F-P1-01 through F-P1-06.
- Written contracts disagree, so a code or context edit would choose a source of truth.
- Live column presence and schedule overlap are `NOT_VERIFIABLE` from the repository.
