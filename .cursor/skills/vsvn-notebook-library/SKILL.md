---
name: vsvn-notebook-library
description: Add or change code in an NB_LIB_* %run library notebook (NB_LIB_EXTRACT_RAWDATA or NB_LIB_TRANSFORM_SLV_GLD) or create a new NB_LIB_* library. Use for shared helpers, retry, identifier quoting, schema-based ctrl appends, target table DDL, temp-view MERGE, parameter validation, and the lock and run-log lifecycle that business notebooks call. Do not use for source-specific extract cells, recompute node build logic, pipeline JSON, or ctrl-table DDL and seeds.
---

# VSVN notebook library

`NB_LIB_*` notebooks are loaded with `%run` and share one Spark session with the caller, so a mistake here reaches every caller at once.

`.cursor/rules/10-fabric-notebook.mdc` and `.cursor/rules/30-sql.mdc` still apply; this skill does not repeat them. If this skill conflicts with `AGENTS.md`, a rule, or the current library code, stop and report the conflict in the task.

## Before editing

1. Read the library's context file: `docs/context/NB_LIB_EXTRACT_RAWDATA.md` or `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md`. Also read `docs/context/02_NAMING_CONVENTION.md` §8. For anything that touches `ctrl_*`, read `docs/context/CTRL_TABLES_CONTEXT.md`.
2. Find the callers by searching for `%run <LIB_NAME>` under `notebooks/`. As of 2026-10-11:
   - `NB_LIB_EXTRACT_RAWDATA` is loaded by `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, and `NB_SETUP_L1_TS_AUDIT`. The setup notebook uses `build_table_specs`, `table_has`, `PC_OPTIONAL_COLUMNS`, `TableSpec` and `ColumnSpec` fields, and the UTC helpers.
   - `NB_LIB_TRANSFORM_SLV_GLD` is loaded by `NB_00_ORCHES_SLV_TO_GLD` and, in future, by `NB_<UPPER(trg_tbl)>` node notebooks.
   In the task, record for each caller which library names it uses and whether the change keeps them working.
3. Do not remove or rename a public function, class, constant, or parameter that a caller uses. Add a new name and migrate the callers in the same task.

### Read budget

- List cells with `python scripts/vv.py toc notebooks/<name>.ipynb`. Read only the cells in the architecture `Main brief` edit list and the cells they call, with `python scripts/vv.py show notebooks/<name>.ipynb cell:<i>` or `def:<function>`.
- Read the matching `docs/context/<name>.md` by section with `toc` and `show`, not whole.
- Search a notebook with `python scripts/vv.py show notebooks/<name>.ipynb grep:<regex>` before opening cells.

## Library contract

Both libraries follow these rules. Keep them.

- A library contains only imports, constants, classes, and functions. `%run` must not read or write a table, start a Spark job, or call `spark.conf.set`. Module-level code is limited to imports, constants, compiled regexes, `threading.Lock()`, read-only `spark.conf.get` (as `CAST_FN` does), and pure-Python tables such as `UNACCENT_SRC, UNACCENT_DST = _build_unaccent_map()`.
- A header markdown cell states the `%run` usage (the `%run` goes in its own cell, right after the caller's parameter cell), the conventions, and a numbered section table.
- Each section is a markdown cell `## N. <name>`, followed by a code cell that starts with the `# N. <name>` banner. Put a new function in the matching section. Add a section only at the end, and update both the header table and the context file's section table.
- Table names are always `lakehouse.schema.table`. Control tables use the `CTRL_SCHEMA` constants (`T_WATERMARK`, `T_LOG_RUN`, and so on). Never use the short form `ctrl.<table>`.
- `NB_LIB_EXTRACT_RAWDATA` stays source-agnostic. It has no partner or third-party names; source specifics come in through parameters, `TableSpec`, or ctrl rows.
- A library does not `%run` another library. `NB_LIB_TRANSFORM_SLV_GLD` keeps its own copies of the shared primitives on purpose. Changing that needs architecture.
- Every function has a Vietnamese docstring: a one-line purpose, `Input :`, `Output:`, and `Ví dụ :` with concrete values (`02_NAMING_CONVENTION.md` §8). Change markers are `[SỬA dd/mm]` or `[THÊM dd/mm]`, with the reason.
- Keep logic that needs no Spark in pure functions, and keep SQL text in separate builder functions (for example `build_table_specs`, `_validate_orch_params`, `sql_merge_target`, `sql_merge_edge_wm`), so it can be tested without Fabric.

## Shared primitives

`NB_LIB_TRANSFORM_SLV_GLD` carries copies marked `chép từ lib extract`. Their behavior must stay the same in both libraries:

| Primitive | Behavior to keep |
|---|---|
| `TRANSIENT_MARKERS`, `is_transient(e)` | Matches on class name plus message text, including Java errors that arrive through Py4J |
| `with_retry(fn, label, attempts=6, base_s=2.0)` | Retries transient errors only; waits `base_s * 2 ** (i - 1) + random.uniform(0, 1)`; re-raises the original error on the last attempt or on a non-transient error |
| `IDENT_RE`, `is_identifier`, `is_fq_name`, `quote_name` | `[A-Za-z][A-Za-z0-9_]*` per part, for external names (schema, table, column). A leading `_` is rejected on purpose: that prefix is reserved for internal columns and temp views. `quote_name` quotes only a name that already passed validation |
| `append_rows(table, rows)` | Builds the DataFrame from the table's current schema (missing keys become NULL) and appends inside `with_retry`. A retry can append the same rows twice; see "Retries and blind appends" |
| `utc_now`, `to_bool`, `split_csv`, `short_error` | UTC without tzinfo; `"1"`, `"true"`, `"yes"`, `"y"` are true; CSV items trimmed and empty ones dropped; `"<Type>: <message>"` cut to `limit` |
| `_lock_expired_sql`, lock acquire and release | See "Run lifecycle" |

Change both copies in the same task. Otherwise, record the deviation in `decision.md` before changing code. `log` is thread-safe in both libraries through `_LOG_LOCK`, but the signatures differ: `wave` and `table` in extract, `node` in transform. Keep each library's own signature.

Business notebooks never get a copy. A new library that needs these primitives copies them unchanged and marks the copy with its origin.

## SQL and writes inside a library

- An external name placed into SQL text must pass `is_identifier` or `is_fq_name` and is then wrapped with `quote_name`. Values go through `spark.sql(sql, args={...})`. The only other interpolations in the current code are integers passed through `int(...)`, a `src_tbl` checked by `is_identifier`, a timestamp string checked by `UTC_TS_RE`, and temp view names built by the rule below. A new interpolation needs the same kind of check right before it.
- For a MERGE from a DataFrame: `createOrReplaceTempView(<view>)`, run the statement, then `spark.catalog.dropTempView` in `finally`. Wave threads and node notebooks can share one Spark session, so the view name must be unique per run and target.
- Temp view names are internal names, not external identifiers. Never pass a view name to `is_identifier` or `quote_name`, and never relax `IDENT_RE` to accept a leading `_`. Build every view name only from:
  - a prefix from `02_NAMING_CONVENTION.md` §5.3 (`_v_`, `_v_wm_`) or the existing `_v_lock_`;
  - parts that already passed `is_identifier`, such as `trg_tbl`;
  - a hex tag cut from a uuid4, such as `exec_id[:8]`, `exec_id.replace("-", "")[:12]`, or `uuid.uuid4().hex[:8]`.
  The result matches `_v_[A-Za-z0-9_]+` and is used unquoted. Never build a part from a raw parameter, from config text that skipped `is_identifier`, or from a timestamp.
- A new helper that receives a view name from its caller checks `re.fullmatch(r"_v_[A-Za-z0-9_]+", view)` and raises `ConfigError` otherwise. `run_merge` does not check yet, so its callers must follow the construction rule.
- Wave threads write only their own target table. The main thread writes shared control tables after the wave. The exception is per-node `ctrl_log_table_run` rows, which are blind appends.

## Retries and blind appends

- Wrap each control-table write in `with_retry`. Do not add a third retry layer around `with_retry` or `process_with_retry`.
- A retry is safe only when the write is idempotent on its grain key. That means a MERGE on that key, such as `commit_state` by entity, `merge_rejects` by `event_hash`, the extract library's `write_run_log` by `exec_id`, or `merge_edge_wm` by edge. It also covers a conditional UPDATE, such as lock acquire and release or `update_run_log` by `exec_id`.
- A blind append is not idempotent under retry. Delta conflict errors (`Concurrent*Exception`, `MetadataChangedException`, `ProtocolChangedException`) mean nothing was committed. `Connection reset` and `TooManyRequestsForCapacity`, however, can arrive after the commit succeeded, and the retry then appends the rows again. Current blind appends are `ctrl_log_table_run` in both libraries and the `RUNNING` row of `ctrl_log_run` in `NB_LIB_TRANSFORM_SLV_GLD` (`write_run_log`). A duplicate row with the same grain key is therefore possible (open, review finding GATE-003, task `20261011-notebook-design-skills`, 2026-10-11).
- Until that gap is fixed under architecture:
  - Never use a blind append for state, watermark, reject, or lock data, or for any row whose duplicate changes behavior. Write those with a MERGE on the grain key.
  - Code that reads an append-only log reduces it to one row per grain key (`ctrl_log_table_run`: `exec_id`, `trg_schema`, `trg_tbl`, `attempt_no`), as `node_logs` keeps the latest row per node. It never counts log rows as attempts or runs.
  - Changing `append_rows`, whether to a MERGE on the grain key or to no retry on ambiguous errors, is a change to both library copies and needs architecture.

## Target table DDL

Both libraries create targets the same way. `target_ddl` emits `CREATE TABLE IF NOT EXISTS <quoted name> (...) USING DELTA TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true')`, with no `CLUSTER BY` (Runtime 1.3). `ensure_target`:

- creates the table when it is missing;
- raises `ConfigError` before any write when an existing column has a different type;
- adds missing columns with `ALTER TABLE ... ADD COLUMNS`;
- never drops, renames, or retypes a column.

Technical columns come after business columns and are taken from the library's own `TECH_COLUMNS` (plus `SNAPSHOT_TECH_COLUMNS` in the extract library). The two libraries' `TECH_COLUMNS` are different sets with the same name, so never import one into the other.

## Validation before writes

- Parse and check every parameter and config row first. Collect all messages and raise one `ConfigError` before taking a lock or writing, as `build_table_specs` and `_validate_orch_params` do.
- Range-check numeric parameters, as `_validate_orch_params` does. `NB_LIB_EXTRACT_RAWDATA` does not check `max_retries` yet. A negative value leaves tables `PENDING`, and the run can report `SUCCESS` (open finding E7 in `docs/context/99_PAIN_POINTS.md`). Do not copy that unchecked form.
- `ConfigError` is never retried. `CastNullError` and `QualityGateError` stop the write for that table or node.

## Run lifecycle

`run_controlled` (extract library), and `orchestrate` plus a manual `run_node` (transform library), implement the same lifecycle. Business notebooks call it and never rebuild it. Do not write a new lock, watermark, or run-log primitive. Extend the existing one under architecture, with `state-correctness-reviewer`.

1. Validate parameters and config. Nothing is written.
2. Acquire the lock:
   - Read the lock row. Refuse when it is held and not expired.
   - Otherwise run `UPDATE ... SET lock_exec_id = <exec_id>, lock_at = current_timestamp() WHERE lock_exec_id IS NULL OR <expired>`, then read the row again. Only the run whose `exec_id` is now stored owns the lock.
   - In `run_controlled` and `orchestrate`, a refused run writes one `SKIPPED_CONCURRENT` run-log row and returns.
   - RUNNING run-log rows past the timeout become `ABANDONED`. The extract library does this after acquiring the lock; the transform library does it before.
3. Open the run log as `RUNNING`.
4. Do the work.
5. Advance durable state (the source watermark or the edge watermarks) only for successful outcomes, and only forward. The extract library does this in `finally`, where a failed status writes `FAILED` and keeps the watermark. The transform library does it before `finally`.
6. In `finally`, close the run log, then release the lock with `WHERE lock_exec_id = <exec_id>`, then unpersist the DataFrames the library cached. A failure in one closing step does not skip the next.
7. Raise for a non-success status only after step 6.

Known gaps to keep in mind; do not copy them into new code:

- Lock expiry is `coalesce(lock_at < current_timestamp() - INTERVAL <n> MINUTES, true)` using the caller's timeout, not the holder's (open finding E8). A caller with a shorter timeout can take a lock that is still valid for its holder.
- Neither library checks lock ownership again just before the target MERGE (C1 in extract; `run_node` step 6 in transform). Safety depends on the activity timeout being shorter than the lock timeout.

## Deploy and check

- Deploy the library before any caller that uses the change (`02_NAMING_CONVENTION.md` §8).
- Run `python scripts/vv.py verify <task-id>`. Its pytest step reads `NB_LIB_EXTRACT_RAWDATA` as JSON and checks `utc_ts_text`. No test reads `NB_LIB_TRANSFORM_SLV_GLD`, and no test compiles code cells.
- Compile every Python code cell of the library and of each caller you changed. The command blanks `%` line magics such as `%run`, skips `%%` cells and non-Python cells, and does not execute anything. Run it from the repository root, in PowerShell or Bash:

  ```text
  python -c "import json,sys;[compile(''.join('\n' if l.startswith('%') else l for l in ''.join(c['source']).splitlines(True)),p+'#cell'+str(i),'exec') for p in sys.argv[1:] for i,c in enumerate(json.load(open(p,encoding='utf-8'))['cells']) if c['cell_type']=='code' and c.get('metadata',{}).get('microsoft',{}).get('language','python')=='python' and not ''.join(c['source']).startswith('%%')];print('compiled',len(sys.argv)-1,'notebooks')" notebooks/<LIBRARY>.ipynb
  ```

  It must print `compiled N notebooks`. A `SyntaxError` names the file and the cell index. `SyntaxWarning` lines are not failures.
- Search both libraries for every shared primitive you changed, and confirm the copies still match.
- Local checks cannot prove `%run` behavior. A library change needs runtime proof. Set `classification.runtime_required: true` and list in `runtime-runbook.md` one Fabric DEV run per caller, after the library is deployed, in a mode that writes nothing:
  - `dry_run = True` for each extract notebook;
  - `p_mode = "PLAN"` for `NB_00_ORCHES_SLV_TO_GLD`;
  - `p_apply = "false"` for `NB_SETUP_L1_TS_AUDIT`.
  Each `%run` must load and each notebook must finish with its normal output. A change to the lock, run log, watermark, or MERGE path also needs a run that exercises that path; its architecture names the run. The user executes the runbook (see `vsvn-task-workflow`).
- Runtime behavior (Delta versions, history, MERGE metrics, runMultiple) is proven only by a runtime runbook in Fabric DEV (`docs/context/99_PAIN_POINTS.md` §0, lesson 8).

## Keep this skill current

This skill describes the code as of 2026-10-11. A task that changes behavior described here lists this skill in its scope. The skill is agent-system configuration, so the user decides how it is updated.
