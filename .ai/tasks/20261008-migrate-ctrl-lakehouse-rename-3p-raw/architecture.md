RESULT: PASS

# Architecture: 20261008-migrate-ctrl-lakehouse-rename-3p-raw

Architect: Claude Opus 5.5 (`claude-opus-5-5`), effort high. Read-only run. No repository file was edited.

## 1. Context and scope

### 1.1 Current state (repository facts)

- Both extract libraries define the control-plane location with one constant: `CTRL_SCHEMA = "lh_vv_bronze.ctrl"` in `NB_LIB_EXTRACT_RAWDATA` §1 and in `NB_LIB_TRANSFORM_SLV_GLD`. All `T_*` names derive from it. The extract notebooks and `NB_00_ORCHES_SLV_TO_GLD` have no executable control-table references of their own. Their only references are in markdown, sample SQL, and stale cell outputs.
- `NB_CREATE_DDL` uses unqualified `ctrl.<table>` names, which resolve through the default lakehouse `lh_vv_bronze`. It also uses `lh_vv_bronze.ctrl.*` in Python constants (`CONFIG_TABLE`, `REGISTRY_TABLE`), in the D1–D7 checks, and in the "Test Precheck" cells. It contains:
  - a DROP cell for the 7 control tables, two registry DROP cells (`ctrl_config_schema_registry`, `ctrl_cfg_schema_registry`), and an optional backup cell (`ctrl.*_bak_20261003`);
  - DDL plus idempotent seeds: `INSERT ... SELECT FROM VALUES ... WHERE NOT EXISTS` for `ctrl_mng_pipeline_config` (partner ids 1–23, 3P ids 24–37) and `ctrl_mng_watermark` (2 source rows), and `seed_registry(...)` writing with `overwrite` + `replaceWhere (src_schema, src_tbl)` for `ctrl_cfg_schema_registry`;
  - "Test Precheck" cells that `UPDATE lh_vv_bronze.ctrl.ctrl_mng_watermark SET last_src_version = <latest>` and then set it back to `NULL`;
  - a `GOLD_LOG_COLUMNS` ALTER cell. Its 5 columns are already in the CREATE TABLE DDL.
- The extract lib finds the source watermark row by `(src_schema, src_tbl, trg_tbl IS NULL)` and reads `watermark_id` from that row. No code derives `wm_transform_<src_tbl>`. `src_partition_cond(src_tbl)` requires `IDENT_RE`, and `brz_3rd_crawler_poi_stream` satisfies it.
- FL_00 (`PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json`):
  - `Get_Config_4Run` is a Script activity on `[parameters('conn_lh_vv_bronze_by_sqlep')]`, `database: lh_vv_bronze`, query `FROM ctrl.ctrl_mng_pipeline_config`.
  - `Lookup_WM` is a `LakehouseTableSource` on linked service `lh_vv_bronze` (`artifactId [parameters('lh_vv_bronze')]`, literal `workspaceId 68c81db2-…`), with `schema: ctrl` and `table: ctrl_mng_watermark`.
  - `GM_DeltaLog` lists `Files/_delta_src/<item().src_tbl>/_delta_log` on `lh_vv_bronze`.
  - The true branch always runs the partner notebook with literal parameters (known finding F-P1-02).
- 3P config rows carry `pl_name = PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`. FL_00's ForEach therefore iterates the 3P source too: it lists the source's `_delta_log` and, when there is work, starts the partner notebook.
- 3P silver MERGE (`build_merge_sql`) updates a matched row only when `(s._crawled_at, s._event_id) >= (t._crawled_at, t._event_id)`. The partner silver MERGE has no row-order guard (C1). Both sources use `ctrl_cdc_state` (no backward moves) and `finalize_watermark` (advances only on SUCCESS/NO_DATA, only while holding the lock, never backward).
- `NB_LIB_TRANSFORM_SLV_GLD.build_dag` raises `ConfigError("pl ... không có cạnh active ...")` when a `pl_name` has no `RECOMPUTE` edges. The gold-flow edges (33 edges per context) are not seeded by `NB_CREATE_DDL`. They come from a `NB_SETUP_*` notebook that is not in this repository.

### 1.2 In scope

1. Move the control plane, all 7 tables, from `lh_vv_bronze.ctrl` to `lh_vv_ctrl.dbo` for every reader and writer: both libraries, both extract notebooks, `NB_00`, `NB_CREATE_DDL`, the FL_00 pre-check, `CHECK_CTRL_SNAPSHOT.py`, and the context docs.
2. Rename the 3P raw source identity from `poi_raw_event` to `brz_3rd_crawler_poi_stream`, and its watermark id to `wm_transform_brz_3rd_crawler_poi_stream`. This covers seed, notebook parameter defaults, docs, sample SQL, and comments. No alias or fallback is kept.
3. Seed `lh_vv_ctrl.dbo` from repository literals and repo-generated rows (`TABLE_CONFIGS`, `TABLE_CONFIGS_3P`). Nothing is copied from `lh_vv_bronze.ctrl`.
4. Define the cutover for both extract sources. With a fresh seed, both start with `last_src_version = NULL` and empty `ctrl_cdc_state`.
5. Record the `normalized_payload` key tree and JSON types, with no values.

## 2. Non-goals

- Silver transform of `normalized_payload`.
- Copying, cloning, or shortcutting live watermarks, CDC state, rejects, logs, or `RECOMPUTE` edges from `lh_vv_bronze.ctrl`.
- Dropping `lh_vv_bronze.ctrl.*` or `lh_vv_bronze.dbo.poi_raw_event`. Old tables remain the rollback anchor and are dropped in a later task.
- Seeding gold-flow `RECOMPUTE` edges, edge watermarks, or flow-lock rows in `lh_vv_ctrl`. NB_00 fails closed until a follow-up task does this (see §11.2).
- Adding a Switch, routing FL_00 by `item().src_tbl`, or calling the 3P notebook from FL_00. F-P1-02 stays as-is (see §13 risk R3).
- Fixing open lib issues C1, C2, M2–M4, or changing extract or MERGE semantics.
- Changing `poi_id` derivation, silver/gold table names, or keys.
- Agent-system files (`AGENTS.md`, `.cursor/rules/*`, `scripts/*`) and historical `.ai/tasks/*` artifacts.
- Creating Fabric items (lakehouse, shortcut, connection) from code. These are user rollout steps.

## 3. Invariants

| ID | Invariant | Enforced by |
|---|---|---|
| I1 | Single control plane: at any instant, every deployed reader and writer of a `ctrl_*` table resolves to the same physical location. After cutover that is `lh_vv_ctrl.dbo`. No code path reads one location and writes the other. | One constant per lib; all callers depend on the lib; quiesced cutover (§10) |
| I2 | `NB_CREATE_DDL` contains no statement that drops, overwrites, or updates any table in `lh_vv_bronze.ctrl`, and no unqualified `ctrl.` name. | Remove the DROP, backup, and Test-Precheck cells; local grep check (§12.1) |
| I3 | `NB_CREATE_DDL` contains no DROP of `lh_vv_ctrl.dbo.*`. Re-running it is non-destructive. | DDL is `CREATE TABLE IF NOT EXISTS`; seeds are `WHERE NOT EXISTS` / `replaceWhere` |
| I4 | Seed rows come only from literals and repository constants. No `INSERT ... SELECT`, `COPY`, `CLONE`, or shortcut sourced from `lh_vv_bronze.ctrl.*`. | Code review; grep |
| I5 | Watermarks never move backward. They advance only on SUCCESS/NO_DATA while the run holds the lock. | Unchanged lib (`finalize_watermark`) |
| I6 | `ctrl_cdc_state` never moves backward per `(trg_schema, trg_tbl, entity_key)`. `ctrl_cdc_state` and `ctrl_cdc_reject` are `PARTITIONED BY (src_tbl)`, and each MERGE is restricted to its own `src_tbl` partition. | DDL; unchanged `src_partition_cond` |
| I7 | 3P silver rows are never regressed: a matched row is updated only by an equal-or-newer `(_crawled_at, _event_id)`. This, not CDC state, protects existing 3P silver rows during the fresh-state cutover. | Unchanged `build_merge_sql`; must not be modified in this task |
| I8 | `poi_id = uuid_format(md5(concat(source_name, source_id)))` is independent of the raw table name. Silver keys, and therefore `entity_key`, are identical before and after the rename. | Unchanged registry (`HASH_MD5_UUID` on `_doc.source_name,_doc.source_id`) |
| I9 | Exactly one source-level watermark row (`trg_tbl IS NULL`) exists per active `(src_schema, src_tbl)`. Exactly one `pipeline_config` row exists per `(pl_name, src_schema, src_tbl, trg_schema, trg_tbl)`. | Seed `WHERE NOT EXISTS`; `load_watermark` and `build_table_specs` raise `ConfigError` otherwise (fail closed) |
| I10 | With `last_src_version = NULL`, an extract reads FULL only when `allow_full_scan = True`. Otherwise it raises `VersionGapError` and writes nothing to silver. | Unchanged lib |
| I11 | The FL_00 pre-check reads config and watermark from `lh_vv_ctrl.dbo`, reads `_delta_log` from `lh_vv_bronze` `Files/_delta_src/<src_tbl>`, and does not start Spark when there is no work. Activity names, ForEach (`isSequential = true`), `If_HasWork`, and the fixed partner notebook activity (including `notebookId`, timeout `0.00:59:00`, retry 0) are unchanged. | Pipeline edit limited to §9.6 |
| I12 | No Fabric GUID for `lh_vv_ctrl` and no workspace id other than the existing one is written into the repository. | Template parameter `lh_vv_ctrl`; no `known_lakehouses` edits |
| I13 | `lh_vv_ctrl` is a schema-enabled lakehouse in the same workspace as `lh_vv_bronze` (`68c81db2-fa14-4fee-91f3-a9f31b1ca2c8`). Three-part Spark names and the reuse of the existing literal `workspaceId` in `Lookup_WM` depend on this. | Runbook precondition P1 (verified before any deploy) |

## 4. State ownership, grain, and keys

### 4.1 Ownership after cutover

| Table (`lh_vv_ctrl.dbo.`) | Grain / logical key (unchanged) | Partition | Writer(s) | Reader(s) |
|---|---|---|---|---|
| `ctrl_mng_pipeline_config` | (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`) | none | `NB_CREATE_DDL` seed; manual | FL_00 `Get_Config_4Run` (SQL endpoint), both extracts, NB_00 |
| `ctrl_mng_watermark` | `watermark_id` | none | Extract lib (source rows), NB_00 (edge and flow-lock rows), `NB_CREATE_DDL` seed (source rows only) | FL_00 `Lookup_WM`, extracts, NB_00, nodes |
| `ctrl_cfg_schema_registry` | (`src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`, `trg_column`) | none | `NB_CREATE_DDL` `seed_registry` (`replaceWhere` per source) | Both extracts |
| `ctrl_log_run` | `exec_id` | none | Extract (MERGE by `exec_id`), NB_00 (append + UPDATE) | Ops, extract stale-run check, NB_00 |
| `ctrl_log_table_run` | (`exec_id`, `trg_schema`, `trg_tbl`, `attempt_no`) | none | Extract (append), nodes (append) | Ops, NB_00 |
| `ctrl_cdc_state` | (`trg_schema`, `trg_tbl`, `entity_key`) | `src_tbl` | Extract `commit_state` | Extract `load_state` |
| `ctrl_cdc_reject` | `event_hash` | `src_tbl` | Extract `merge_rejects` | Ops |

`lh_vv_bronze.ctrl.*` becomes a frozen archive with no reader or writer in the repository. It remains only as the rollback anchor (§11).

### 4.2 Source identities after rename

| Source | `src_schema` | `src_tbl` | `watermark_id` | `watermark_column` | `flow_name` |
|---|---|---|---|---|---|
| Partner | `lh_vv_bronze.dbo` | `partner_raw_data` (unchanged) | `wm_transform_partner_raw_data` (unchanged) | `EventProcessedUtcTime` | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` |
| 3rd-party | `lh_vv_bronze.dbo` | `brz_3rd_crawler_poi_stream` | `wm_transform_brz_3rd_crawler_poi_stream` | `crawled_at` | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |

All other seed values (ids, `trg_*`, `priority`, `load_mode`, `align_path`, `dedup_order`, `is_active` including `slv_3p_poi_policy = 0`, registry columns, and the 36 inactive 3P columns) stay byte-identical to the current `NB_CREATE_DDL` seed.

### 4.3 What the fresh seed means

- Partner and 3P source rows start `INITIALIZED`, with `last_src_version`, `last_src_table_id`, `watermark_value`, `last_success_at`, and the lock columns all `NULL`.
- `ctrl_cdc_state` has no partition for either source. The old `src_tbl = poi_raw_event` and `partner_raw_data` partitions live only in `lh_vv_bronze.ctrl`, and no code reads them.
- `ctrl_log_run`, `ctrl_log_table_run`, and `ctrl_cdc_reject` start empty. Reject counts restart at 1 and history stays in the archive.
- The gold flow has no `RECOMPUTE` rows, edge rows, or flow-lock rows (§11.2).

## 5. Ordering and transaction boundaries

Each Delta statement is its own commit. There is no multi-table atomicity, so safety comes from ordering plus idempotent re-execution.

### 5.1 `NB_CREATE_DDL` commit order (one operator, top to bottom)

1. `CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`, then partner `INSERT ... WHERE NOT EXISTS`, then 3P `INSERT ... WHERE NOT EXISTS`. The two inserts run as separate statements, in that order.
2. `CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_mng_watermark`, then one `INSERT ... WHERE NOT EXISTS` with the 2 source rows.
3. `CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.ctrl_cfg_schema_registry`, then `seed_registry(TABLE_CONFIGS, 'lh_vv_bronze.dbo', 'partner_raw_data')`, then `seed_registry(TABLE_CONFIGS_3P, 'lh_vv_bronze.dbo', 'brz_3rd_crawler_poi_stream')`.
4. `CREATE TABLE IF NOT EXISTS` for `ctrl_log_run`, `ctrl_log_table_run`, `ctrl_cdc_state PARTITIONED BY (src_tbl)`, and `ctrl_cdc_reject PARTITIONED BY (src_tbl)`.
5. `GOLD_LOG_COLUMNS` cell, retargeted. It is a no-op on fresh tables.
6. D1–D7 read-only checks, retargeted.

Config is created before the watermark so that any partial state is detectable: a source without a watermark row makes the extract fail with `ConfigError`, which is closed. The log and state tables come last because no reader exists before an extract runs.

### 5.2 Extract run commit order (unchanged, documented because cutover safety depends on it)

`acquire_lock` (watermark UPDATE) → `write_run_log(RUNNING)` → `pin_snapshot` → per-table silver MERGE (parallel threads, one writer per table) → `commit_state` (one MERGE, SUCCESS tables only) → `merge_rejects` → table-log append → `finalize_watermark` → `write_run_log(final)` → `release_lock`.

| Crash point | Durable state | Next run (`allow_full_scan = True` while `last_src_version` is NULL) |
|---|---|---|
| After some silver MERGEs, before `commit_state` | Silver partly updated; no state; watermark NULL | FULL again; state empty, so the same rows are re-applied. 3P is idempotent through I7. Partner is idempotent because it applies the deterministic latest event per entity over the same pinned snapshot or a superset. |
| After `commit_state`, before `finalize_watermark` | State present; watermark NULL | FULL again; state marks the already-applied events as stale, so they are not re-applied; remaining work is processed. |
| After `finalize_watermark`, before `release_lock` | Watermark advanced; lock held | Lock expires after `running_timeout_minutes` (780), or the documented manual release in `lh_vv_ctrl` is used. |

### 5.3 Cutover order across systems

The full sequence is in §10. The ordering constraints are:

- `lh_vv_ctrl` exists and is seeded and verified before any lib is deployed (C1 before C2).
- Libraries are deployed before the notebooks that `%run` them (repository rule).
- Partner and 3P first FULL runs complete before FL_00 is re-enabled, because FL_00 passes `allow_full_scan = false` and would otherwise fail with `VersionGapError`.
- FL_00 is redeployed and its connection bound only after the `lh_vv_ctrl` SQL analytics endpoint shows the seeded rows.

## 6. Idempotency, concurrency, and recovery

### 6.1 Idempotency

- **`NB_CREATE_DDL`:** every statement is idempotent. Re-running after partial failure converges.
  - `pipeline_config.id = COALESCE(MAX(id), 0) + seq` may yield different id numbers on a partial re-run. `id` is not a key, so this is harmless.
- **3P first FULL:** fresh state applies every valid document. I7 makes the silver result order-independent and repeatable. A repeat with state present yields `applicable_rows = 0` for already-applied documents.
- **Partner first FULL:** this equals the 04/10 recreate-and-rerun procedure. It resolves the latest event per entity over the full raw at the pinned version; TOAST columns keep the target value. The result is deterministic and repeatable.
- **Steady state** (`allow_full_scan = false`, VERSION read): re-running with no new commits gives NO_DATA and leaves the watermark unchanged.

### 6.2 Concurrency

- **Cutover window:** FL_00 schedule paused, no manual extract or NB_00 runs, and no in-flight runs in either location (§10 step 0). Rationale: a lock row in `lh_vv_ctrl` does not exclude a run that still uses `lh_vv_bronze.ctrl`. Two partner extracts under different control planes could overlap on `slv_pn_*`, where the MERGE has no row-order guard (C1), and an older batch could overwrite a newer one.
- **First FULL runs:** run partner, then 3P, sequentially. This avoids two 16-VCore sessions on F16 and ctrl-table write contention (E4). The code tolerates parallel runs via partitioned state/reject and `with_retry`, but there is no reason to pay for it during cutover.
- **`NB_CREATE_DDL`:** single operator. A concurrent run could duplicate `WHERE NOT EXISTS` inserts. This is detected by D1/D5 and by extract `ConfigError` (fail closed). Fix by deleting the duplicate rows in `lh_vv_ctrl` (§11.3).
- **Steady state:** unchanged. FL_00 concurrency 1; activity timeout 59 min < 780 min lock expiry; atomic lock on the watermark row; ForEach sequential.

### 6.3 Retry and recovery

| Failure | Behavior | Recovery |
|---|---|---|
| Transient Delta conflict | `with_retry` (6 attempts) and per-table `max_retries` | None |
| `VersionGapError` (NULL watermark, table id changed, unsupported log) | Run FAILED; no silver write; watermark unchanged | One manual run with `allow_full_scan = True` |
| `ConfigError` (missing or duplicate config/watermark, bad registry, raw column missing) | Fails before the lock | Fix rows in `lh_vv_ctrl` (§11.3), then re-run |
| `CastNullError` / `bad_shape` / unexpected `source_name` (IGNORED) on the new raw | Table FAILED, or counted in exit JSON | Inspect with `dry_run = True`; fix registry or params; re-run with `allow_full_scan = True` (watermark is still NULL) |
| `SKIPPED_CONCURRENT` with no live run | Lock held by a killed run | Wait for expiry or use the documented release `UPDATE lh_vv_ctrl.dbo.ctrl_mng_watermark ... WHERE lock_exec_id = '<id>'` |
| FL_00 `GM_DeltaLog` fails for `brz_3rd_crawler_poi_stream` | Iteration fails; pipeline run Failed | Create the shortcut (P2), then re-trigger |
| SQL endpoint not yet synced (`Get_Config_4Run` returns 0 rows) | ForEach has 0 items; pipeline "succeeds" doing nothing (silent) | Runbook gate R-FL3: SQL endpoint query must return 2 sources before enabling the schedule |

## 7. Partial failures

| Scenario | Effect | Handling |
|---|---|---|
| `NB_CREATE_DDL` stops mid-way | Some tables or rows missing | Re-run from the top (idempotent). Extracts fail closed on missing rows. |
| Libs deployed, extract notebooks not (or the reverse) | 3P: old notebook default `src_tbl = poi_raw_event` against the new ctrl, or new notebook against the old lib, finds 0 watermark rows → `ConfigError`. Partner switches with the lib alone. | Deploy all 5 notebooks in one window while FL_00 is paused (§10 step 4) |
| `NB_LIB_EXTRACT_RAWDATA` switched, `NB_LIB_TRANSFORM_SLV_GLD` not | Violates I1 for log/watermark tables | Same window. Verification R-D2 confirms both libs print `ctrl=lh_vv_ctrl.dbo`. |
| Partner FULL succeeds, 3P FULL fails | Partner live in the new plane; 3P watermark NULL; 3P silver partly updated (safe by I7) | Fix and re-run 3P with `allow_full_scan = True`. Keep FL_00 paused until 3P succeeds (§13 R3). |
| 3P PARTIAL_FAILED | State committed for SUCCESS tables only; watermark NULL | Re-run FULL. SUCCESS tables see stale (skipped) rows; failed tables are reprocessed. |
| FL_00 redeployed but connection not bound | `Get_Config_4Run` fails, so the pipeline fails (loud) | Bind `conn_lh_vv_ctrl_by_sqlep`, then re-trigger |
| Lakehouse not resolvable from a notebook session | `AnalysisException` before the lock (fail closed) | Attach `lh_vv_ctrl` in Fabric. The resulting `known_lakehouses` change comes from Fabric Git sync, not from an agent. |

## 8. Alternatives and trade-offs

| Decision | Options | Selected | Reason |
|---|---|---|---|
| D1 Seed source | (a) Literal / repo-generated fresh seed. (b) `INSERT ... SELECT` / `CLONE` from `lh_vv_bronze.ctrl`. (c) OneLake shortcuts from `lh_vv_ctrl` to the old tables. | (a) | (b) is forbidden. It would also carry the old `src_tbl = poi_raw_event` identity into state partitions and watermark ids, which would need in-place rewrites of durable state. (c) gives two names for one state, violating I1. The cost of (a) is one FULL replay per source (~5 min partner, ~4 min 3P based on 04/10 timings), with idempotency proven by §6.1. |
| D2 Location switch | (a) Constant `CTRL_SCHEMA` in each lib. (b) Notebook parameter `ctrl_schema`. (c) Spark conf / Environment variable. | (a) | (b) allows per-run split-brain (I1). (c) hides control-plane location outside the repository. (a) is a single reviewed constant per lib, and all callers inherit it. |
| D3 3P cutover read start | (a) `last_src_version = NULL` + `allow_full_scan = True` FULL of the new raw. (b) Seed `last_src_version` = current version of the new raw. (c) `full_reload = True`. | (a) | (b) infers a data position and silently skips unprocessed documents (data loss). (c) never initializes the watermark (`updates_watermark = false`). (a) is closed by default (I10) and safe by I7. |
| D4 FL_00 config read | (a) New template parameter `conn_lh_vv_ctrl_by_sqlep`, `database: lh_vv_ctrl`, three-part query `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config`. (b) Keep the bronze connection and use a cross-database three-part query. | (a) | (b) needs no new connection but makes control-plane reads depend on the bronze endpoint, contrary to the request. In (a) the three-part name stays correct even if the connection is bound to another same-workspace endpoint. |
| D5 FL_00 watermark lookup | (a) New linked service `lh_vv_ctrl` with `artifactId [parameters('lh_vv_ctrl')]`, existing `workspaceId` literal, `schema: dbo`. (b) Hardcode a GUID. | (a) | (b) is forbidden (I12). (a) binds the GUID at deploy time. |
| D6 Destructive cells in `NB_CREATE_DDL` | (a) Remove the DROP, backup, and Test-Precheck cells. (b) Retarget to `lh_vv_ctrl`. (c) Keep behind a flag. | (a) | Left as-is, unqualified `ctrl.` DROPs would delete the rollback anchor on a top-to-bottom run. Retargeting is forbidden and would make a re-run destroy live state. Test-Precheck moves a source watermark to the latest version, which skips data. Teardown and reset become runbook-only procedures. |
| D7 Gold-flow control rows | (a) Not seeded; NB_00 fails closed until a follow-up re-seeds `RECOMPUTE` edges into `lh_vv_ctrl`. (b) Leave `NB_LIB_TRANSFORM_SLV_GLD` on `lh_vv_bronze.ctrl`. (c) Copy edges from bronze. | (a) | (b) splits the control plane (I1) and keeps `lh_vv_bronze.ctrl` live. (c) is forbidden. The edges are not in the repository, so (a) is the only compliant option. The gold flow has no pipeline in the repository and its flow is "chưa chốt" per context. Needs user acknowledgment (§11.2). |
| D8 Default lakehouse | (a) Keep `lh_vv_bronze`; fully qualify every control name. (b) Switch `NB_CREATE_DDL` default to `lh_vv_ctrl`. | (a) | (b) needs a GUID in notebook metadata (I12). (a) plus the I2 grep makes resolution explicit. |

## 9. Selected design and implementation plan

Main implements in this order. All comments and markdown edits in notebooks are in Vietnamese, following the existing `[SỬA 08/10]` marker convention. Clear all cell outputs in every edited notebook: they contain old names and stale run logs, and clearing them is part of meeting the acceptance grep.

### 9.1 `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`

- §1: `CTRL_SCHEMA = "lh_vv_ctrl.dbo"`. `T_*` stay derived from it.
- Update docstring examples: `append_rows("lh_vv_ctrl.dbo.ctrl_log_table_run", ...)`, `src_partition_cond("brz_3rd_crawler_poi_stream")`, and the `load_table_specs` example source name.
- Update header markdown: control tables are in `lh_vv_ctrl.dbo`, and the 3P source is `brz_3rd_crawler_poi_stream`. The "Thay đổi 03/10" table may keep the old raw name only inside one explicitly marked migration note.
- Observability: emit one `log(f"ctrl={CTRL_SCHEMA}")` line at the start of `run_controlled` (before `acquire_lock`), including in `dry_run`. Do not change the exit JSON schema.
- No other code changes.

### 9.2 `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`

- `CTRL_SCHEMA = "lh_vv_ctrl.dbo"`.
- Emit `log(f"ctrl={CTRL_SCHEMA}")` once at the start of `orchestrate()` and once at the start of `run_node()`.
- No other code changes.
- Default lakehouse stays `lh_vv_bronze`, as runMultiple requires.

### 9.3 `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb`

- Parameter cell: `src_tbl = "brz_3rd_crawler_poi_stream"`. Leave other defaults unchanged.
- Markdown: source is `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`, controls are in `lh_vv_ctrl.dbo`, and the lock row is `wm_transform_brz_3rd_crawler_poi_stream`. Rename the section "Hằng số nguồn `poi_raw_event`".
- Sample SQL: `lh_vv_ctrl.dbo.ctrl_log_run WHERE src_tbl = 'brz_3rd_crawler_poi_stream'`, and the same pattern for `ctrl_log_table_run` and `ctrl_cdc_reject`.
- Clear outputs.

### 9.4 `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`

- Markdown and sample SQL only: replace every `lh_vv_bronze.ctrl.` with `lh_vv_ctrl.dbo.`.
- Remove the stale note "Cần cột khoá: `ALTER TABLE ... ADD COLUMNS (lock_exec_id ...)`". The new DDL contains the lock columns. If the note is kept, retarget it.
- Clear outputs.

### 9.5 `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb`

- Code is unchanged; it inherits from the lib.
- Update markdown that names the control location, if any.
- Clear outputs.

### 9.6 `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json`

- Template `parameters`:
  - add `conn_lh_vv_ctrl_by_sqlep` (string) and `lh_vv_ctrl` (string);
  - remove `conn_lh_vv_bronze_by_sqlep`, which no activity references after the change;
  - keep `lh_vv_bronze`, which `GM_DeltaLog` still uses.
- `Get_Config_4Run`:
  - `externalReferences.connection = "[parameters('conn_lh_vv_ctrl_by_sqlep')]"`;
  - `database = "lh_vv_ctrl"`;
  - query text `SELECT DISTINCT src_schema, src_tbl\nFROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config\nWHERE pl_name = '@{pipeline().parameters.p_pipeline_code}'\n  AND is_active = 1;`
- `Lookup_WM` linked service:
  - `name = "lh_vv_ctrl"`;
  - `typeProperties.artifactId = "[parameters('lh_vv_ctrl')]"`;
  - `workspaceId` unchanged (I13);
  - `rootFolder = "Tables"`;
  - dataset `typeProperties = {"schema": "dbo", "table": "ctrl_mng_watermark"}`.
- Everything else stays byte-identical: activity names, `dependsOn`, ForEach, `GM_DeltaLog`, filters, If, variables, and the notebook activity.
- Do not edit `manifest.json`.

### 9.7 `notebooks/NB_CREATE_DDL.ipynb`

- Header markdown:
  - controls in `lh_vv_ctrl.dbo`; default lakehouse `lh_vv_bronze`, with every control name fully qualified;
  - run order: create, then seed, then checks;
  - recreate-from-scratch and reset are runbook-only procedures; this notebook never drops anything.
- Delete these cells: "Xoá bảng ctrl cũ" markdown, the BACKUP cell, the 7-table DROP cell, both registry DROP cells, the "Test Precheck" markdown, and both Test-Precheck code cells.
- Replace them with one Vietnamese markdown cell. It states that DROP and reset were removed in the 08/10 migration, and that teardown of the old location is a separate task. This cell is the single allowed migration note naming `lh_vv_bronze.ctrl`.
- Retarget every DDL, INSERT, and check to fully qualified `lh_vv_ctrl.dbo.<table>`. That includes `CONFIG_TABLE`, `REGISTRY_TABLE`, the `show_registry` join, `GOLD_LOG_COLUMNS` table names, and D1–D7.
- DDL must match `docs/context/CTRL_TABLES_CONTEXT.md` (as updated in §9.9) column-for-column, including comments, the 5 gold-log columns, the lock columns, `last_src_table_id`, and `PARTITIONED BY (src_tbl)` on `ctrl_cdc_state` and `ctrl_cdc_reject`. Partition comments must not claim parallel ForEach (F-P3-01): FL_00 ForEach is sequential, and partitioning isolates partner and 3P manual or other-pipeline runs.
- 3P `pipeline_config` INSERT:
  - literal `'brz_3rd_crawler_poi_stream' AS src_tbl`;
  - `NOT EXISTS` predicate on `c.src_tbl = 'brz_3rd_crawler_poi_stream'`;
  - VALUES list unchanged.
- Watermark INSERT, 3P row: `('wm_transform_brz_3rd_crawler_poi_stream', 'lh_vv_bronze.dbo', 'brz_3rd_crawler_poi_stream', NULL, NULL, 'crawled_at', NULL, NULL, 'INITIALIZED', 'NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV', -1, NULL, NULL, NULL, NULL, NULL, NULL, current_timestamp())`. Keep the explicit 18-column list (E1). The partner row is unchanged.
- Registry: `seed_registry(TABLE_CONFIGS_3P, "lh_vv_bronze.dbo", "brz_3rd_crawler_poi_stream")` and `show_registry(...)` with the same arguments. Update the `TABLE_CONFIGS_3P` header comment.
- D4/D6/D7 expectations and comments: use `brz_3rd_crawler_poi_stream`. Expected values are unchanged: 14 tables, 182 columns, 1 wave.
- Seeds must not read any `lh_vv_bronze.ctrl` object (I4).
- Clear outputs.

### 9.8 `docs/context/CHECK_CTRL_SNAPSHOT.py`

- `CTRL = "lh_vv_ctrl.dbo"`.
- Header comment: snapshot of `lh_vv_ctrl.dbo`; default lakehouse may stay `lh_vv_bronze`.
- Replace any `poi_raw_event` literal.
- Must pass `ruff check`.

### 9.9 Context docs (Vietnamese prose; identifiers in English)

- **`CTRL_TABLES_CONTEXT.md`:**
  - title and conventions: location `lh_vv_ctrl.dbo`; code always uses full names; no `ctrl.` short form;
  - all DDL headers become `CREATE TABLE IF NOT EXISTS lh_vv_ctrl.dbo.<table>`;
  - every `poi_raw_event` becomes `brz_3rd_crawler_poi_stream`, and `wm_transform_poi_raw_event` becomes the new id;
  - FL_00 paragraph: config via `conn_lh_vv_ctrl_by_sqlep`, watermark via `lh_vv_ctrl` table lookup, `_delta_log` via `lh_vv_bronze` `Files/_delta_src/<src_tbl>`;
  - "Dữ liệu hiện có" sections: values measured before 08/10 belong to the archived location. Mark them in one migration-note block per section, or replace them with "chưa có số sau cutover — chạy `CHECK_CTRL_SNAPSHOT.py`";
  - add a §10 history row for 08/10: move to `lh_vv_ctrl.dbo`, fresh seed, rename of the 3P source, DROP cells removed, gold edges not seeded;
  - "Thao tác thường gặp" SQL uses `lh_vv_ctrl.dbo`.
- **`01_DATA_MODEL.md`:**
  - storage row: medallion lakehouses plus `lh_vv_ctrl` (schema `dbo`) for control tables;
  - ctrl row uses `lh_vv_ctrl.dbo.ctrl_*`;
  - Mermaid node and raw table row become `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`. Drop the "21.168 dòng, dừng từ 16/09" facts, which describe the old raw;
  - add a subsection "Cấu trúc `normalized_payload`" (format in §9.10).
- **`02_NAMING_CONVENTION.md`:**
  - raw row lists `partner_raw_data` and `brz_3rd_crawler_poi_stream`, as user-confirmed names. Do not invent a general raw-naming rule beyond noting both;
  - control row becomes `lh_vv_ctrl.dbo` with prefix `ctrl_`;
  - the watermark id rule `wm_transform_<src_tbl>` is unchanged.
- **`00_README.md`:** platform line names the 3 medallion lakehouses plus `lh_vv_ctrl.dbo` for ctrl; raw line names `brz_3rd_crawler_poi_stream`.
- **`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md`, `NB_LIB_EXTRACT_RAWDATA.md`, `NB_00_ORCHES_SLV_TO_GLD.md`:**
  - names, parameter defaults, and sample SQL updated;
  - 3P §9 measurements are labeled as old-raw (pre-08/10) inside a migration note;
  - 3P §10 "Lần đầu" says to pass `allow_full_scan = True`, `max_parallel = 13`, `max_retries = 1` explicitly;
  - NB_00 doc states that after migration NB_00 raises `ConfigError` until `RECOMPUTE` edges are seeded into `lh_vv_ctrl`.

### 9.10 `normalized_payload` shape recording

- Main reads `C:\Users\bachnh\Downloads\data_sample.json` locally and records only the structure:
  - a table of `path | JSON type (object/array/string/number/boolean/null) | element type for arrays`;
  - array element keys listed once under `path[]`.
- Map-like objects whose keys are data rather than schema (identifiers, phone numbers, URLs, free text) are recorded as `<dynamic-key>`. Language-code keys may be listed.
- No values, no example strings, and no `raw_payload` structure beyond "JSON string".
- Label the subsection: "suy ra từ 1 dòng mẫu, không phải hợp đồng schema".

### 9.11 Runtime runbook content Main must write (`runtime-runbook.md`, Vietnamese)

It must implement §10 exactly, including:

- preconditions P1–P3;
- the baseline B1–B3;
- the gates R-D1…R-FL4 in §12.2;
- rollback (§11.1) and forward recovery (§11.3).

Read-only SQL against `lh_vv_bronze.ctrl` is allowed only inside a section titled as a migration note.

## 10. Rollout

### Preconditions (user, Fabric DEV)

- **P1:** Lakehouse `lh_vv_ctrl` exists, is schema-enabled, and is in workspace `68c81db2-fa14-4fee-91f3-a9f31b1ca2c8`. Verified by `SHOW TABLES IN lh_vv_ctrl.dbo` from a session with default lakehouse `lh_vv_bronze`.
- **P2:** Shortcut `lh_vv_bronze` `Files/_delta_src/brz_3rd_crawler_poi_stream` exists and points to `Tables/dbo/brz_3rd_crawler_poi_stream`. Listing `_delta_log` shows `*.json` commit files. Never delete files inside a shortcut (F5).
- **P3:** User records in `decision.md` acknowledgment of §11.2: gold flow is non-runnable on `lh_vv_ctrl` until a follow-up task.

### Baseline (read-only, migration note)

- **B1:** Old `lh_vv_bronze.ctrl.ctrl_mng_watermark` source rows: `watermark_id`, `status`, `last_src_version`, `lock_exec_id`. Old `ctrl_log_run` rows with `status = 'RUNNING'` (expect 0).
- **B2:** `DESCRIBE HISTORY ... LIMIT 1` versions of all 23 `slv_pn_*` and 14 `slv_3p_poi_*` tables. These are the RESTORE points for the optional rollback.
- **B3:** Current version and row count of `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream`.

### Steps

| Step | Action | Commit point |
|---|---|---|
| 0 | Pause FL_00 schedule; stop manual triggers; wait until no FL_00, extract, or NB_00 run is active (pipeline monitor + B1) | C0 quiesced |
| 1 | Import updated `NB_CREATE_DDL`; run top to bottom; gate R-D1 | C1 new plane seeded |
| 2 | Drift check R-D3 (read-only, new vs old config/registry); must be 0 differences or have user sign-off | — |
| 3 | Deploy `NB_LIB_EXTRACT_RAWDATA` and `NB_LIB_TRANSFORM_SLV_GLD` | C2 switch point |
| 4 | Deploy both extract notebooks and `NB_00` in the same window | — |
| 5 | Partner: `dry_run = True, allow_full_scan = True`, then a real run with `allow_full_scan = True, max_retries = 1, max_parallel = 12`; gate R-E1 | C3 |
| 6 | 3P: `dry_run = True, allow_full_scan = True, max_parallel = 13`; inspect `cast_null`, `bad_shape`, `langs`, `ignored_detail`. Then a real run with `allow_full_scan = True`; gate R-E2 | C4 (3P silver now reflects the new raw) |
| 7 | Idempotency: rerun both with `allow_full_scan = False`; gate R-E3 | — |
| 8 | Create the Fabric connection to the `lh_vv_ctrl` SQL analytics endpoint; deploy FL_00 binding `conn_lh_vv_ctrl_by_sqlep`, `lh_vv_ctrl`, and `lh_vv_bronze`; gates R-FL1–R-FL3; trigger FL_00 once manually; gate R-FL4 | C5 |
| 9 | Re-enable the FL_00 schedule | C6 |

## 11. Rollback and forward recovery

### 11.1 Rollback

- **Before C3** (no extract has written in the new plane):
  - redeploy the previous notebook and pipeline versions from Git (commit `eedb718` or the merge base);
  - rebind `conn_lh_vv_bronze_by_sqlep`;
  - resume the schedule.
  - No data effect. `lh_vv_ctrl` tables may be left in place or dropped manually; nothing reads them.
- **After C3/C4:** same redeploy. This is safe because:
  - the old partner watermark resumes from its pre-cutover `last_src_version`, and re-reading events already applied in the new plane yields the same latest-per-entity result;
  - the old 3P path reads the dormant `poi_raw_event`, and I7 prevents regressing 3P rows written from the new raw;
  - old `ctrl_cdc_state` is unchanged.
  - 3P silver keeps the documents applied from `brz_3rd_crawler_poi_stream`.
- **Removing new-raw data from 3P silver** requires `RESTORE TABLE ... TO VERSION AS OF <B2>` on the 14 `slv_3p_poi_*` tables. This is destructive to any later writes. It is a user decision only, never automatic, and gold must be recomputed afterwards.
- The archive `lh_vv_bronze.ctrl` must not be modified by any rollback step.

### 11.2 Gold flow (accepted consequence)

- After C2, any NB_00 run creates a `wm_flow__<pl>` lock row and log rows in `lh_vv_ctrl`, then raises `ConfigError` (no edges). No node runs and no gold table is touched.
- A follow-up task must seed `RECOMPUTE` edges into `lh_vv_ctrl` from repository-owned literals. Every edge then starts dirty, so the first NB_00 run recomputes all nodes. That run is idempotent: MERGE on `row_hash`, with silver inputs unchanged.

### 11.3 Forward recovery

- **Wrong seed row, before step 5:** dropping the 7 `lh_vv_ctrl.dbo` tables manually (runbook SQL, never a notebook cell) and re-running `NB_CREATE_DDL` is allowed.
- **Wrong seed row, after step 5:** do not drop. Apply a targeted `UPDATE`/`DELETE` on `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` or `ctrl_mng_watermark` by logical key. For the registry, fix `TABLE_CONFIGS*` and re-run `seed_registry` (`replaceWhere` per source).
- **Extract failures:** see §6.3. While a watermark is NULL, every re-run needs `allow_full_scan = True`.
- **FL_00 failure on the 3P iteration:** fix P2 and re-trigger. The partner iteration is unaffected because ForEach is sequential.

## 12. Verification strategy

### 12.1 Local (Main, before review)

- `python scripts/vv.py verify 20261008-migrate-ctrl-lakehouse-rename-3p-raw` passes. It covers ruff on `CHECK_CTRL_SNAPSHOT.py` and the JSON/pipeline structure check on FL_00.
- Grep gates over `notebooks/`, `pipelines/`, and `docs/`:
  - `poi_raw_event`, `wm_transform_poi_raw_event`, and `lh_vv_bronze.ctrl` appear only inside explicitly titled migration notes. Report the list of remaining hits with file and line.
  - Regex `(?<![\w.])ctrl\.ctrl_` gives 0 hits in `notebooks/` (I2).
  - `DROP TABLE` gives 0 hits in `NB_CREATE_DDL`.
  - `INSERT` / `MERGE` / `COPY` / `CLONE` sourced from `lh_vv_bronze.ctrl` gives 0 hits (I4).
- Notebook integrity, as an ad-hoc command rather than a verifier change:
  - every edited `.ipynb` parses as JSON;
  - every Python code cell (magics such as `%run` and `%%sql` excluded or stripped) passes `compile()`;
  - all outputs are empty;
  - `metadata.dependencies.lakehouse` is unchanged (I12).
- Pipeline:
  - every `[parameters('x')]` reference is declared and every declared parameter is referenced;
  - activity set, names, `dependsOn`, and the notebook activity are byte-identical to `HEAD` except the fields in §9.6.
- Seed equivalence (pure Python over notebook source):
  - `TABLE_CONFIGS_3P` and the 3P `pipeline_config` VALUES are unchanged versus `HEAD` apart from `src_tbl`;
  - `seed_registry` still flattens 3P to 14 tables / 182 columns (36 inactive) and partner to 23 tables / 301 columns.
- Informational, non-gating: compare the `src_object` and `json_path` roots of `TABLE_CONFIGS_3P` against the recorded `normalized_payload` key tree and list missing roots. One sample is not proof; the runtime `dry_run` is the gate.

### 12.2 Runtime gates (Fabric DEV, in `runtime-runbook.md`)

- **R-D1:** 7 tables exist in `lh_vv_ctrl.dbo`. `DESCRIBE DETAIL` shows `partitionColumns = [src_tbl]` for `ctrl_cdc_state` and `ctrl_cdc_reject`.
  - `pipeline_config`: 37 rows (partner 23, 3P 14, `policy` `is_active = 0`).
  - `watermark`: 2 rows, both `INITIALIZED`, `last_src_version` NULL.
  - registry: partner 301, 3P 182.
  - D1 duplicates: 0. D5: exactly 1 source row per active source.
- **R-D2:** The first line of each extract and NB_00 run log prints `ctrl=lh_vv_ctrl.dbo`.
- **R-D3:** Read-only diff of new versus archived `pipeline_config` and `ctrl_cfg_schema_registry` (migration note), mapping `poi_raw_event` to `brz_3rd_crawler_poi_stream`. Expect 0 differences. Any difference (for example manual `is_active` edits in the archive) stops rollout for a user decision.
- **R-E1 (partner):**
  - `ctrl_log_run` status `SUCCESS`, `read_mode = FULL`, `lock_mode` atomic (no WARN about lock columns);
  - watermark `status = SUCCESS`, `last_src_version = src_version_to`, `last_src_table_id` set, lock NULL;
  - `ctrl_cdc_state` rows only in partition `partner_raw_data`;
  - `(trg_tbl, entity_key)` duplicates = 0.
- **R-E2 (3P):**
  - `SUCCESS`; `read_rows` equals the count of `brz_3rd_crawler_poi_stream VERSION AS OF src_version_to`; `valid_rows + ignored_rows + rejected_rows = read_rows`;
  - watermark `wm_transform_brz_3rd_crawler_poi_stream` advanced;
  - `ctrl_cdc_state` / `ctrl_cdc_reject` rows only in partition `brz_3rd_crawler_poi_stream`; duplicates = 0;
  - for each `slv_3p_poi_*`: `MAX(_crawled_at)` ≥ the B2-era value, and no row has `_crawled_at` lower than in the B2 snapshot for the same key. Sample-free aggregate check via `VERSION AS OF <B2>` join count, which must be 0 (I7).
- **R-E3:** Both reruns end `NO_DATA` with `read_mode = VERSION` (or process only commits after `src_version_to`). `last_src_version` is not lower than before. State row counts are unchanged when there are no new commits.
- **R-FL1:** In the SQL analytics endpoint of `lh_vv_ctrl`, `SELECT DISTINCT src_schema, src_tbl FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE pl_name = 'PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00' AND is_active = 1` returns 2 rows.
- **R-FL2:** `Lookup_WM` output contains both source rows with non-null `last_src_version`.
- **R-FL3:** `GM_DeltaLog` succeeds for both sources.
- **R-FL4:** The manual FL_00 run succeeds:
  - each iteration's `v_msg` / `v_msg_skip` shows the correct `last_src_version`;
  - with no new raw commits, both iterations take the SKIP branch and start no Spark session;
  - a new `ctrl_log_run` row appears only if a branch ran;
  - nothing is written to `lh_vv_bronze.ctrl` (archive row counts equal B1).

## 13. Observability, security, and risks

### 13.1 Observability

- New `ctrl=<CTRL_SCHEMA>` log line in both libs (§9.1, §9.2).
- Existing `read_mode`/`read_note` already record the FULL reason "chưa có last_src_version (lần đầu / sau reset / sau cutover)".
- Exit JSON, run log, table log, and FL_00 `v_msg` are unchanged.
- `CHECK_CTRL_SNAPSHOT.py` targets the new plane.

### 13.2 Security and data handling

- No secrets, connection strings, or GUIDs are added. Connection and artifact ids are bound at deploy time.
- `ctrl_cdc_reject.after_payload` continues to store raw 3P payloads, which may contain personal data. `lh_vv_ctrl` must carry the same workspace-role access as `lh_vv_bronze` (a runbook check).
- The `normalized_payload` record contains keys and types only (§9.10). Runtime evidence uses aggregates; samples ≤ 50 rows and none from payload columns.

### 13.3 Risks

| ID | Risk | Impact | Mitigation |
|---|---|---|---|
| R1 | Split-brain during deploy | Overlapping partner runs (C1) | Quiesce (C0), single window, R-D2 |
| R2 | Seed drifts from the archived manual config | Different silver columns / behavior | R-D3 stop gate |
| R3 | F-P1-02: the 3P iteration in FL_00 starts the partner notebook whenever `brz_3rd_crawler_poi_stream` has new commits, or while its watermark is NULL. If the new raw is live (unknown), this adds one partner Spark session per FL_00 run on F16. | Capacity (P1-class performance) | Run 3P first-FULL before C6. Observe in R-FL4 and the first scheduled day. A route or filter fix is a separate task (user decision). |
| R4 | SQL endpoint metadata lag leads to an empty config result and a silent no-op FL_00 | Missed SLA | R-FL1 before C6 |
| R5 | The new raw has a different payload shape or `source_name` set | Tables FAILED or documents IGNORED | `dry_run` in step 6; closed by I10 / C2-safe semantics |

## 14. Review routing

`sql-data-reviewer` (seed SQL, DDL, partition, `NOT EXISTS`/`replaceWhere`), `spark-runtime-reviewer` (lib constants, notebook integrity, three-part names), `state-correctness-reviewer` (cutover timelines §5.2, §7, §11), `fabric-pipeline-reviewer` (§9.6, R-FL*), then `risk-gate`.

## 15. Evidence needed

None before implementation. The facts that depend on the environment are rollout preconditions and runtime gates, not design inputs:

- P1 (lakehouse placement);
- P2 (shortcut);
- R-D3 (config drift);
- whether the new raw is live (R3);
- new-raw payload conformance (step 6 `dry_run`).

Each has a defined stop or continue action, so none of them changes the selected design.
