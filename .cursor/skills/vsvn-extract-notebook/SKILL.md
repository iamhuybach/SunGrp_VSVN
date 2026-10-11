---
name: vsvn-extract-notebook
description: Create or change an NB_EXTRACT_<SOURCE>_CDC_BRZ_TO_SLV notebook that loads one bronze raw table into silver L1 tables through NB_LIB_EXTRACT_RAWDATA. Use when adding a raw source or editing the parameter, classification, per-table, target MERGE, commit, or exit cells of NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV or NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV. Do not use for NB_LIB_* code, silver-to-gold recompute notebooks, pipeline JSON, or ctrl-table DDL and seeds.
---

# VSVN extract notebook

An extract notebook holds only what is specific to one raw source. `NB_LIB_EXTRACT_RAWDATA` owns the rest: lock, run log, snapshot pinning, read mode, watermark, waves, table retry, and the state and reject MERGE statements.

`.cursor/rules/10-fabric-notebook.mdc` and `.cursor/rules/30-sql.mdc` still apply; this skill does not repeat them. If this skill conflicts with `AGENTS.md`, a rule, or the current notebook code, stop and report the conflict in the task.

## Before editing

1. Read the closer existing notebook in full. Use `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` for change events with deletes. Use `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` for full-document snapshots with derived keys.
2. Read `docs/context/NB_LIB_EXTRACT_RAWDATA.md` (section 4 and the function tables for §11, §13, §14) and the source's context file. Read `docs/context/CTRL_TABLES_CONTEXT.md` before changing anything that writes `ctrl_*`.
3. When a notebook and its context file disagree, report the difference in the task. Do not pick one. Known differences on 2026-10-11:
   - Both notebooks default `allow_full_scan = True` and `max_parallel = 12`. The partner context file lists `False` and `4`. The third-party context file lists `allow_full_scan` as `False`. Take defaults from the task, not from either file.
   - The third-party context file still describes `LANG` / `LANG_ARRAY` modes and a `langs` parameter. The notebook accepts only `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`.
4. If source facts are missing from task evidence (event-order column, key uniqueness, null rates, payload shape), use the `fabric-runtime-evidence` skill. Do not infer them from column names.

## Notebook layout

Keep this cell order. Both notebooks use it.

1. Markdown cell: purpose, caller, reads, writes, parallelism, rerun and concurrency behavior.
2. Parameter cell with the `parameters` tag. Shared names, in this order: `pl_name`, `run_id`, `src_schema`, `src_tbl`, `allow_full_scan`, `max_parallel`, `max_retries`, `table_filter`, `full_reload`, `dry_run`, `stop_on_failure`, `cast_null_policy`, `running_timeout_minutes`. Source-only parameters follow, with plain names and no `p_` prefix. Partner also keeps the unused `overlap_minutes` for old callers; a new source omits it.
3. `%run NB_LIB_EXTRACT_RAWDATA`, alone in its cell.
4. A markdown table of the source constants, then a code cell with the constants and `NB_NAME`:

   ```python
   try:
       NB_NAME = notebookutils.runtime.context.get("currentNotebookName") or "<NOTEBOOK_NAME>"
   except Exception:
       NB_NAME = "<NOTEBOOK_NAME>"
   ```

5. Section A (read and classify), section B (one table), section C (commit), Main, Exit, then a `Vận hành` markdown cell. A markdown table of its functions precedes each code section.

Comments, docstrings, and log text are Vietnamese. Identifiers are English. Mark changes with `[SỬA dd/mm]` or `[THÊM dd/mm]` and the reason.

## Section A: read and classify

- `read_raw` only calls `read_incremental(ctx, <raw columns>, "<order alias>")`. Never filter the raw table by time. Never scan it with `spark.table` for data; reading `.columns` for a schema check is fine.
- Classification is one ordered list of `(condition, reason, detail)` folded with `reversed(rules)`, so the first matching rule wins. It sets `_reason` and `_reject_detail`, and sets `_status`: `VALID` when no rule matched, `IGNORED` when the reason is in `IGNORE_REASONS`, otherwise `REJECTED`.
- A new reason value is an enum change. Add it to `docs/context/02_NAMING_CONVENTION.md` §6 and `docs/context/CTRL_TABLES_CONTEXT.md` §9 in the same task.
- Build the event columns the library reads (lib §13): `_cdc_ts_ms` BIGINT, `_cdc_lsn` BIGINT or NULL, `_raw_ingested_at` TIMESTAMP, `_is_delete` INT, `_op` STRING or NULL, and later `_entity_key` STRING. `event_order()` does not replace a NULL `_cdc_ts_ms`, so classification must reject rows without it (`MISSING_EVENT_ORDER`).
- Set raw payload columns to NULL as soon as no later step reads them. Partner keeps payloads for VALID and REJECTED rows. Third party keeps the payload only for REJECTED rows. Per-table frames keep raw values only on `_key_null` rows.

### Profile

- Profile the read in one grouped aggregate (`groupBy`, then `agg` with a count and the max of the order alias), then `collect()`. `watermark_to` is the maximum over every row read, including IGNORED and REJECTED. Never `limit` this aggregate, because `read_rows` and `watermark_to` need every group.
- A grouped `collect()` needs a row bound that the code enforces. Group only by `_status`, `_reason`, and columns whose values the code has already restricted to the ctrl config. Before grouping, replace any raw-derived value outside that set with one literal such as `"(other)"`. Partner's `objects_cond(configured)` is the test for a configured source object.
- A watch list that must name raw-derived values, such as unknown JSON keys, is sorted by count descending and cut with `.limit(<named constant, at most 50>)` before `collect()`. Log a warning when the limit is reached.
- Known gap on 2026-10-11 (review finding GATE-005, task `20261011-notebook-design-skills`): partner `profile_events` groups by the raw `_src_object_schema` and `_src_object`, which are unbounded for UNCONFIGURED and REJECTED rows. Third-party `profile_docs` groups by the raw `source_name` and collects every unknown top-level key. Do not copy either form into a new source. Changing those functions is a separate task.

### Reject rows

- Reject frames select every `ctrl_cdc_reject` column explicitly. Set `first_run_id = last_run_id = ctx.run_id`, `reject_count = 1`, and `is_resolved = false`.
- `event_hash` is the MERGE key of `ctrl_cdc_reject` (`merge_rejects`). Two different rejects must never share a hash, and the same rejected event or element must get the same hash on every reread. Never put a run id or a processing time in the identity fields.
- A new source computes `F.sha2(F.to_json(F.struct(<identity fields>)), 256)`. Give each field a fixed alias and keep the order fixed; renaming or reordering a field changes every hash. Convert timestamps with `unix_micros` and dates with `cast("string")`, as `_hash_expr` in `NB_LIB_TRANSFORM_SLV_GLD` does. JSON quoting keeps field boundaries, and `to_json` writes a NULL field as absent or `null`, never as `""`.
- Known gap on 2026-10-11 (review finding GATE-001, same task): partner `reject_rows` and third-party `doc_reject_rows` and `element_reject_rows` hash `concat_ws('\u0001', <fields with NULL coalesced to ''>)`. That form gives NULL and `''` the same hash and does not escape the delimiter. Do not copy it. Changing an existing notebook's formula is a migration: rows already in `ctrl_cdc_reject` stop matching, and the next reread inserts new rows instead of raising `reject_count`. That needs architecture.

## Section B: one table

`_run_table(res, <inputs>, state_df, ctx)` runs in a wave thread. It writes only its own target table and fills `res`. Steps, in this order:

1. `ensure_target(spec, ctx.dry_run)`; log the returned note.
2. Build the table frame, `persist(StorageLevel.MEMORY_AND_DISK)` it, and append it to `res.cached`.
3. `table_stats(spec, frame)`: one `agg(...).first()` returning `input_rows`, `rejected_rows`, `stale_rows`, `applicable_rows`, `entity_rows`, `upsert_event_rows`, `delete_event_rows`, and the `_cn__*` and `_unset__*` counts.
4. If any value became NULL during conversion and `ctx.cast_null_policy == "FAIL"`, raise `CastNullError` before any MERGE. Third party only warns in `dry_run`; partner raises. Do not change either without a task decision.
5. Put the `_key_null` rows in `res.reject_df`. Nothing is written yet.
6. Return when `res.applicable_rows == 0` or `ctx.dry_run`.
7. `resolve_latest`, persist into `res.cached`, `merge_into_target`, then set `res.state_df`.

`process_table` is only `process_with_retry(spec, wave, ctx, lambda res: _run_table(...))`. Do not add another retry loop. Do not catch exceptions inside `_run_table`.

Row flags (names fixed by `docs/context/02_NAMING_CONVENTION.md` §5.3):

- `_key_null`: `_parse_failed`, or any key column the table needs is NULL or blank.
- `_entity_key`: set only when not `_key_null`.
- `_is_stale`: a state row exists and `NOT (event_order() > _st_order)`. Join `state_df` filtered to this `trg_schema` and `trg_tbl`, selecting `_st_key` and `_st_order`, with a left join on `_entity_key == _st_key`, then drop both columns. With `full_reload`, `state_df` is `None` and nothing is stale.
- `_applicable`: `NOT _key_null AND NOT _is_stale`.

Latest row and state rows:

- `resolve_latest` keeps one row per target MERGE key, using `row_number()` over a window ordered newest first by the source's event-order contract. Partner orders by `_cdc_ts_ms`, `_cdc_lsn` (nulls last), `_raw_ingested_at`, `_is_delete`. Third party orders by `_cdc_ts_ms`, `_raw_ingested_at`, `_event_id`, then the table's `dedup_order`, then `_pos`.
- New code partitions the window by the real key columns `spec.key_cols`, as third party does. Partitioning by a `|`-joined key string is partner's known issue L4.
- The window order must end with a column the source contract documents as unique per event. If no such column is documented, stop and request evidence.
- `res.state_df` must hold exactly one row per `_entity_key`, because `commit_state` MERGEs it without deduplication. When `_entity_key` is not the target key (third party `state_key = "doc"`), build a separate latest-per-`_entity_key` frame, as `doc_state_latest` does, before calling `state_rows`.

## Target MERGE

`build_merge_sql(spec, target, view, merge_clock)` builds the statement, and `merge_into_target` runs it.

- Compute `merge_clock = utc_ts_text(utc_now())` once per table. Check `UTC_TS_RE.fullmatch(merge_clock)` or raise `ConfigError`. Every audit timestamp in the statement uses `to_utc_timestamp(CAST('<merge_clock>' AS TIMESTAMP), current_timezone())`.
- `ON` compares every column of `spec.key_cols` and nothing else.
- Set `created_at` only in the INSERT branch. Set `updated_at` in every UPDATE and INSERT branch.
- Build `tech_expr` for the technical columns, and raise `ConfigError` unless its keys equal the library constant: `TECH_COLUMNS` for CDC, `SNAPSHOT_TECH_COLUMNS` for snapshot. A source that needs other technical columns is a library change.
- List INSERT columns explicitly: `spec.columns`, then the technical columns.
- Select only the columns the statement reads, then call `run_merge(source, spec.fq_name, lambda target, view: build_merge_sql(...), f"_v_{ctx.exec_id[:8]}_{spec.trg_tbl}")`. Wave threads share one Spark session, so the view name must be unique per run and table.
- The view name is an internal name. It starts with `_`, so it never passes `is_identifier`, and it is never passed to `is_identifier` or `quote_name`. It is safe because every part is controlled: the `_v_` literal, the first 8 hex characters of the uuid4 `exec_id`, and `spec.trg_tbl`, which `build_table_specs` already checked with `is_identifier`. Never add a part taken from a parameter or from raw data.
- Never use `WHEN NOT MATCHED BY SOURCE`. An extract batch holds only the entities that changed, so that clause would delete or soft-delete every other row.
- Deletes differ by source. In partner, a matched row with `_cdc_op = 'd'` gets `deleted = true`, and a delete is never inserted. Third party has no delete branch.
- Rerun guard on the target: the third-party MERGE updates a matched row only when `(_crawled_at, _event_id)` is not older than the target row. The partner MERGE has no guard and relies on state and the lock (known issue C1). A new source states in its architecture which form it uses. Do not copy the unguarded form as a default.

## Section C: commit

`commit(classified, profile, results, ctx)` runs on the main thread after every wave, in this order:

1. `commit_state(results, ctx.src_tbl)`.
2. `merge_rejects(parts, note, ctx.src_tbl)`. `parts` holds the `reject_df` of SUCCESS tables, plus the classification rejects when `profile.rejected_rows > 0`.
3. `append_rows(T_LOG_TABLE_RUN, [table_log_row(r, ctx) for r in results])`.

Always pass `ctx.src_tbl`. `ctrl_cdc_state` and `ctrl_cdc_reject` are partitioned by `src_tbl`, and the partition predicate keeps two sources from conflicting. The library commits state only for SUCCESS tables. If the run stops after any step, the watermark has not moved, so the next run rereads the same raw versions and state drops the events already applied.

The table log has one row per table in scope, with the final `attempt_no`. `.cursor/rules/10-fabric-notebook.mdc` says one row per table attempt. That mismatch is open; do not change either side without a task.

`append_rows` retries a blind append inside `with_retry`. After a `Connection reset` or capacity error the append may already have committed, so the table log can hold a duplicate row for the same `(exec_id, trg_schema, trg_tbl, attempt_no)` (open, review finding GATE-003, task `20261011-notebook-design-skills`). Read the table log per grain key, never count its rows as attempts, and never write state or rejects by append.

Never write `ctrl_mng_watermark` or `ctrl_log_run` from the notebook. `run_controlled` owns both.

## Main

- `build_context()` checks every parameter, adds each problem to an `errors` list, and raises one `ConfigError` before anything is written. This is the third-party form; partner still raises on the first error. It sets `exec_id = str(uuid.uuid4())`, `run_id = str(run_id or "").strip() or exec_id`, and `run_mode` as `DRY_RUN`, else `FULL_RELOAD`, else `INCREMENTAL`. It converts flags with `to_bool` and lists with `split_csv`, and stores `run_params = json.dumps(params, ensure_ascii=False)`.
- `run_extract()` calls, in order: `build_context()`, `assert_utc_format()`, `load_table_specs(ctx, <allowed load modes>)`, the source's `check_config(ctx, specs)` if it has one, `load_watermark(ctx)`, one summary `log` line, then `return run_controlled(ctx, lambda out: process_run(...))`. Allowed modes are `("CDC",)` for partner and `("DOC", "DOC_ARRAY")` for third party. A new source passes its own tuple.
- `process_run(..., out)`:
  - Classify the raw read, persist it, and append it to `out.cached`.
  - Set `out.profile`.
  - Unless `full_reload`, persist `load_state(specs)` and append it to `out.cached`.
  - Call `run_tables(specs, <rows per table>, <worker>, ctx, out.results)`.
  - Set `out.status = decide_status(out.results)`.
  - Call `commit` unless `ctx.dry_run`.
  - Put source-specific exit fields in `out.extra`.
- Every persisted DataFrame goes into `out.cached` or `res.cached`, and the library unpersists them. Do not call `unpersist` in the notebook.
- `RUN_SUMMARY = run_extract()` is the last line of the Main cell.

## Exit cell

Put this code in a separate cell after Main, outside any try/except:

```python
_summary_json = json.dumps(RUN_SUMMARY, ensure_ascii=False, default=str)
print(json.dumps(RUN_SUMMARY, ensure_ascii=False, indent=2, default=str))
if RUN_SUMMARY["status"] in ("FAILED", "PARTIAL_FAILED", "SKIPPED_CONCURRENT"):
    raise RuntimeError(f"{NB_NAME} {RUN_SUMMARY['status']}: {_summary_json}")
notebookutils.notebook.exit(_summary_json)
```

The raise fails the pipeline activity. `SKIPPED_CONCURRENT` raises because an overlapping run is unexpected; its error names the `exec_id` that holds the lock. Keep the `build_summary` keys, and add source fields only through `out.extra`. Wiring the notebook into a pipeline is outside this skill; see `.cursor/rules/20-data-pipeline.mdc`.

## Stop conditions

- The source needs a different lock, watermark, read mode, state, or reject behavior. That is an `NB_LIB_EXTRACT_RAWDATA` change and needs architecture.
- A new `ctrl_*` column, enum value, or table is needed. Update `docs/context/CTRL_TABLES_CONTEXT.md` with evidence first.
- Source facts are not in task evidence. Use `fabric-runtime-evidence`.

## Check before handing off

- Run `python scripts/vv.py verify <task-id>`. Its pytest step reads `NB_LIB_EXTRACT_RAWDATA`, both extract notebooks, and `NB_CREATE_DDL` as JSON and checks the L1 timestamp contract (`tests/test_l1_ts_contract.py`, `tests/test_3p_l1_contract.py`). It does not compile code cells, and it does not cover a new notebook.
- Compile every Python code cell of each notebook you changed. The command blanks `%` line magics such as `%run`, skips `%%` cells and non-Python cells, and does not execute anything. Run it from the repository root, in PowerShell or Bash:

  ```text
  python -c "import json,sys;[compile(''.join('\n' if l.startswith('%') else l for l in ''.join(c['source']).splitlines(True)),p+'#cell'+str(i),'exec') for p in sys.argv[1:] for i,c in enumerate(json.load(open(p,encoding='utf-8'))['cells']) if c['cell_type']=='code' and c.get('metadata',{}).get('microsoft',{}).get('language','python')=='python' and not ''.join(c['source']).startswith('%%')];print('compiled',len(sys.argv)-1,'notebooks')" notebooks/<NOTEBOOK>.ipynb
  ```

  It must print `compiled N notebooks`. A `SyntaxError` names the file and the cell index. `SyntaxWarning` lines are not failures.
- The parameter cell still has the `parameters` tag.
- The notebook has exactly one `%run NB_LIB_EXTRACT_RAWDATA`, no `spark.conf.set`, no `toPandas()`, no `collect()` without an enforced row bound, and no workspace or lakehouse GUID in code.
- Local checks cannot prove `%run`, Spark, or exit behavior. A new extract notebook, or a change to its parameter, `%run`, Main, or Exit cell, needs runtime proof. Set `classification.runtime_required: true` and write `runtime-runbook.md` with these Fabric DEV runs, which the user executes (see `vsvn-task-workflow`):
  1. `dry_run = True`. Expect the `%run` to load, the exit value to be JSON with `run_mode` `DRY_RUN`, and no new Delta version on the target or `ctrl_*` tables. A dry run takes no lock and writes no control row.
  2. A normal run when the raw table has no new version. Expect exit status `NO_DATA`, a `ctrl_log_run` row with the same `exec_id` and status, and a run that finishes without error. Make sure no DEV pipeline run of the same source is active, or the run ends `SKIPPED_CONCURRENT` and raises.

## Keep this skill current

This skill describes the code as of 2026-10-11. A task that changes behavior described here lists this skill in its scope. The skill is agent-system configuration, so the user decides how it is updated.
