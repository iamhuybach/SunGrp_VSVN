RESULT: PASS

# Architecture: 20261012-implement-gld-enr-poi-flow

Architect: Claude Code, `claude-opus-5-5`, effort `high`. Date: 2026-10-13.

## 0. Basis

Sources read for this design:

- `.ai/tasks/20261012-implement-gld-enr-poi-flow/task-state.yaml`, `request.md`, `decision.md`, `evidence/plan.md`, `evidence/probes/*`, `evidence/results/e1_partner_address_keys.txt`, `evidence/results/e2_partner_i18n_locale.txt`.
- Closed rule sources: `docs/requirements/20261012-map-gld-enr-poi-tables/MAPPING.md` v18, `BRD.md` v16, `.ai/tasks/20261012-map-gld-enr-poi-tables/decision.md`, and the `MAIN_CORRECTION 2026-10-12` block of `requirements-analysis.md`.
- Platform context: `AGENTS.md`, `docs/context/01_DATA_MODEL.md`, `02_NAMING_CONVENTION.md`, `CTRL_TABLES_CONTEXT.md`, `NB_00_ORCHES_SLV_TO_GLD.md`, `NB_LIB_TRANSFORM_SLV_GLD.md`.
- Code: `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` (`load_config_rows`, `build_dag`, `cadence_minutes`, `NodeSpec`, `NodeContext`, `run_node`, `plan_run`, `build_run_multiple_dag`, `advance_edges`, `orchestrate`), `notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb`, `notebooks/NB_CREATE_DDL.ipynb` (`TABLE_CONFIGS`, `TABLE_CONFIGS_3P`, pipeline_config seed cells), `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` (`load_table_specs` filter, `ISO_UTC_TS` rule), `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/*.json`, `scripts/vv.py` (`cmd_verify`).

Evidence status: `e1` and `e2` are recorded, and the user closed the partner address keys and the `vi` locale on 2026-10-13. No data fact that this design depends on is still unknown. One expression-level business answer (`U-01`, §16) is still open. It blocks only the `COL-043` expression, not the state, ordering, or recovery design.

## 1. Context and scope

Build a 15-minute Fabric flow that appends history rows to three Delta tables in `lh_vv_gold.enr`. The flow also adds one silver table that computes the partner `poi_id` before gold.

| Object | Layer | Write mode | Grain | Key |
|---|---|---|---|---|
| `lh_vv_silver.dbo.slv_pn_poi` | silver L2 (name chosen by the user, `MQ-063`) | Lib `RECOMPUTE` MERGE | 1 row / `poi_id` | `poi_id` |
| `lh_vv_gold.enr.gld_enr_poi_info` | gold | `APPEND` | 1 row / (`poi_id`, `updated_at`) | `poi_id`, `updated_at` |
| `lh_vv_gold.enr.gld_enr_poi_coordinate` | gold | `APPEND` | 1 row / (`poi_id`, `updated_at`) | `poi_id`, `updated_at` |
| `lh_vv_gold.enr.gld_enr_poi_review` | gold | `APPEND` | 1 row / (`review_id`, `updated_at`) | `review_id`, `updated_at` |

Names from Mapping §2:
- Pipeline: `PL_VV_TRANS_SLV_TO_ENR_15P`.
- Orchestrator: `NB_00_ORCHES_SLV_TO_ENR_15P`.
- Nodes: `NB_SLV_PN_POI`, `NB_ENR_POI_INFO`, `NB_ENR_POI_COORDINATE`, `NB_ENR_POI_REVIEW`.

Files changed (Main owns all of them):

| File | Change |
|---|---|
| `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` | **Additive** `APPEND` edge/node mode (§11.1). **Not in the current `scope.files`. Main must add it to `task-state.yaml` and record why in `decision.md`.** |
| `notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb` | New. Clone of `NB_00_ORCHES_SLV_TO_GLD` (4 cells) with this flow's defaults |
| `notebooks/NB_SLV_PN_POI.ipynb` | New `RECOMPUTE` node |
| `notebooks/NB_ENR_POI_INFO.ipynb`, `NB_ENR_POI_COORDINATE.ipynb`, `NB_ENR_POI_REVIEW.ipynb` | New `APPEND` nodes |
| `notebooks/NB_CREATE_DDL.ipynb` | New cells: `nb_name` column on `ctrl_mng_pipeline_config`, schema `enr` and the 3 gold tables, 14 edge seeds |
| `pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/PL_VV_TRANS_SLV_TO_ENR_15P.json` | New pipeline |
| `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md`, `docs/context/CTRL_TABLES_CONTEXT.md` | Document the `APPEND` mode, the `nb_name` column, and this flow's edges. These are ctrl semantics, `AGENTS.md` §9. **Add to `scope.files`.** |
| `tests/test_enr_poi_contract.py` | Recommended deterministic contract test (§15). **Add to `scope.files` if adopted.** |

## 2. Non-goals

- No change to `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`, `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, or `NB_LIB_EXTRACT_RAWDATA`.
- No `ref_*` table. No rule moved to `slv_poi_*`. No reads of `destination_ward_mapping`, `poi_address_enrichment_staging`, `SRC-006`, `SRC-008`, `DS-004`, or `DS-008`.
- No `row_hash`, no MERGE, no UPDATE, and no soft delete on the three `gld_enr_*` tables.
- No `description` on info. No `title`, `positive`, `negative`, `response_text`, or `source_review_id` on review.
- No source for `best_time_type`, `best_time_from_month`, `best_time_to_month`, or `cost`. They stay NULL. No `costVnd`.
- No invented minutes column for `time_to_spend`.
- No Delta Change Data Feed. No change to silver table properties.
- No Spark-free pipeline pre-check in this task (deviation D-06, backlog).
- No PostgreSQL sync of these tables. No handling of data returned by the enrichment service (`BQ-001`).
- No commit, push, or merge.

## 3. Invariants

| ID | Invariant |
|---|---|
| INV-01 | The `gld_enr_*` tables are append-only. The flow writes them only with Delta `WRITE` mode `Append`. A flow commit never rewrites, updates, or deletes an existing row. Old rows keep their `created_at` and `updated_at`. |
| INV-02 | One node run appends at most one Delta commit per gold table. All rows of that commit share one `batch_ts`, and `created_at = updated_at = batch_ts` (`PC-09`, `MQ-030`). |
| INV-03 | Within one append commit, the key is unique (`poi_id` for info/coordinate, `review_id` for review). With INV-02 this keeps (`key`, `updated_at`) unique across the table. |
| INV-04 | `poi_id` never contains a language. 3P `poi_id` is copied from `slv_3p_poi.poi_id`. Partner `poi_id` is copied from `slv_pn_poi.poi_id`, which is `uuid_md5('partner_portal', id)` (`ID-004`). Review `review_id` and `poi_id` are copied from `slv_3p_poi_review` and never re-hashed (`MQ-062`). |
| INV-05 | Partner rows and 3P rows are separate rows built by separate branches and combined with `unionByName`. No join between sources (`MQ-058`). |
| INV-06 | Every append commit carries a commit marker in Delta `userMetadata`. The marker names the input versions that produced it (§7.2). The append and its consumed-input record are one atomic commit. |
| INV-07 | An edge watermark never advances past the input version that its node read. Edges advance only after the node reports `SUCCESS` or `NO_DATA`, through the existing `advance_edges` MERGE. |
| INV-08 | A POI or review gets a new row only when it is new, or when its row changed in any input table of that node between the consumed baseline and the read version. Exception: a forced run appends every key (§7). |
| INV-09 | The gold nodes read only silver tables and the commit history of their own target. Gold never reads another gold table. |
| INV-10 | Each gold table's DDL equals Mapping §5: column set, types, and nullability (`NOT NULL` only on `poi_id` for info/coordinate and `review_id` for review). The APPEND path never creates or alters a gold table. A schema mismatch fails the node before any write. |
| INV-11 | Only `NB_00_ORCHES_SLV_TO_ENR_15P` writes this flow's edge rows and `ctrl_log_run`. Nodes only append their own `ctrl_log_table_run` row. |
| INV-12 | The lib change is additive. `RECOMPUTE` nodes behave exactly as before. `PL_VV_TRANSFORM_SLV_TO_GLD_*` behaves exactly as before. |

## 4. State ownership, grain, and keys

| State | Owner (sole writer) | Readers | Notes |
|---|---|---|---|
| `ctrl_mng_pipeline_config` rows where `pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'` | `NB_CREATE_DDL` seed cell (manual, insert-only) | lib `load_config_rows` | 14 edges (§11.3). Logical key: (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`) |
| `ctrl_mng_pipeline_config.nb_name` column | `NB_CREATE_DDL` (`ALTER TABLE ADD COLUMNS` if missing) | lib | Already documented as optional in `CTRL_TABLES_CONTEXT.md` §3. Extracts select explicit columns, so they are unaffected |
| `ctrl_mng_watermark` edge rows `wm_e__<trg_tbl>__<src_tbl>` | `NB_00_ORCHES_SLV_TO_ENR_15P` via `advance_edges` | lib `load_edge_wm` | Created on first advance. Not seeded |
| `ctrl_mng_watermark` lock row `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` | NB_00 (`ensure_lock_row`, `acquire_flow_lock`, `release_flow_lock`). A manual node `RUN` also takes it | lib | `flow_name = NB_00_ORCHES_SLV_TO_ENR_15P` |
| `ctrl_log_run` | NB_00 | operators | One row per `exec_id` |
| `ctrl_log_table_run` | each node | NB_00 `collect_outcomes` | One row per node per exec |
| `lh_vv_silver.dbo.slv_pn_poi` | `NB_SLV_PN_POI` (lib MERGE) | info and coordinate nodes | Business columns: `poi_id`, `business_service_id`, `name`, `short_address`, `ward`, `district`, `province_name`. The lib adds `row_hash`, `created_at`, `updated_at`, `deleted_at` (D-02) |
| `gld_enr_poi_info`, `gld_enr_poi_coordinate`, `gld_enr_poi_review` | the matching `NB_ENR_POI_*` node (append only) | enrichment service (`CSM-001`) | Created by `NB_CREATE_DDL` |
| Gold commit marker (`userMetadata`) | the writing node, atomically with the rows | the same node on later runs | §7.2 |
| `slv_3p_poi*`, `slv_pn_business_services`, `slv_pn_business_service_i18ns` | the extract notebooks | this flow (read-only, by Delta version) | Unchanged |

Grain notes:
- `slv_pn_business_service_i18ns` is unique on (`business_service_id`, `locale`). The `locale = 'vi'` filter therefore gives at most one name per service and cannot fan out.
- Every `slv_3p_poi_*` child used here is unique on `poi_id`, so left joins on `poi_id` cannot fan out.
- QG `pk_duplicate` blocks any fan-out anyway.

## 5. DAG, ordering, and transaction boundaries

DAG for `PL_VV_TRANS_SLV_TO_ENR_15P`, built by the lib from the edges:

```
L0  slv_pn_poi            (RECOMPUTE) <- slv_pn_business_services, slv_pn_business_service_i18ns
L0  gld_enr_poi_review    (APPEND)    <- slv_3p_poi_review
L1  gld_enr_poi_info      (APPEND)    <- slv_3p_poi, slv_3p_poi_address, slv_3p_poi_contact, slv_3p_poi_rating,
                                         slv_3p_poi_price, slv_3p_poi_opening_hours, slv_3p_poi_review, slv_pn_poi
L1  gld_enr_poi_coordinate(APPEND)    <- slv_3p_poi, slv_3p_poi_address, slv_pn_poi
```

Commit order for one NB_00 run. Every step is its own Delta commit, because Delta has no multi-table transaction:

| # | Commit | Table |
|---|---|---|
| C1 | Acquire flow lock (`UPDATE`) | `ctrl_mng_watermark` |
| C2 | Append run log `RUNNING` | `ctrl_log_run` |
| C3 | `slv_pn_poi` MERGE (skipped when diff = 0) | silver |
| C4 | Node log | `ctrl_log_table_run` |
| C5 | `gld_enr_poi_review` append + marker (skipped when 0 rows) | gold |
| C6 | Node log | `ctrl_log_table_run` |
| C7, C8 | `gld_enr_poi_info` append + marker; node log. Runs after C3 succeeds (runMultiple dependency) | gold, ctrl |
| C9, C10 | `gld_enr_poi_coordinate` append + marker; node log. Runs after C3 | gold, ctrl |
| C11 | `advance_edges`: one MERGE for every candidate edge | `ctrl_mng_watermark` |
| C12 | Update run log (status, counts, `read_note`, `output_versions_json`) | `ctrl_log_run` |
| C13 | Release lock | `ctrl_mng_watermark` |

Rules:
- Any gold append (C5, C7, C9) commits before C11 advances that node's edges (INV-07).
- The marker (INV-06) closes the window between the gold commit and C11.
- Review runs in parallel with `slv_pn_poi`. Info and coordinate run in parallel with each other. Concurrency is `p_max_parallel = 2`.

Inputs are pinned by Delta version (`p_pinned_json`), one snapshot per table. Different silver tables can be read while an extract is half-way through writing them. The 3P extract writes about 9 tables as separate commits. A row built in that state reflects what silver showed at read time. The next run detects the remaining changes and appends a corrected row. This is accepted as P2 limitation L-01.

## 6. Change detection (which keys are appended)

Selected rule (C1 in §10): **input-row change by Delta version comparison**, per node and per input.

For each input role `r` of an APPEND node, with read version `V_r` and baseline `B_r` (§7):

- `changed(r)` is the set of rows of `input(r) @ V_r` that are not identical, across all columns, to any row of `input(r) @ B_r`. This is a Spark `subtract` over all columns.
- For lib-written inputs (`slv_pn_poi`), `ctx.input` already keeps live rows only and drops the 4 technical columns. Both versions must go through that same filter.
- If the schema changed between `B_r` and `V_r`: select `V_r`'s column list from both sides. A column missing at `B_r` becomes `CAST(NULL AS <V_r type>)`, and a column dropped in `V_r` is ignored. A column that appears therefore counts as a change.
- `B_r` is `None` (FULL) or the run is forced: `changed(r) = input(r) @ V_r`.
- `B_r >= V_r` (nothing new on this edge): `changed(r)` is empty.
- Reading `@ B_r` fails because that version is no longer available (time travel refused, or missing files after VACUUM): fall back to FULL for that role. Record `basis = FULL_VERSION_UNAVAILABLE` in `qg_json` and log a WARN. Any other error fails the node.

Rows that disappear between versions are ignored. L1 never removes rows (`01_DATA_MODEL.md` §5.2: no delete branch, upsert only; partner soft delete keeps the row). `MQ-046` says there is no delete handling.

Mapping changed rows to target keys:

| Node | Role → key taken from changed rows | Universe filter |
|---|---|---|
| info, 3P branch | `poi`, `addr`, `contact`, `rating`, `price`, `hours` → `poi_id`. `review` → `poi_id` of the changed review rows | ∩ `poi_id` of `slv_3p_poi @ V_r` |
| info, partner branch | `pn_poi` → `poi_id` | ∩ `slv_pn_poi @ V_r` (live) |
| coordinate, 3P branch | `poi`, `addr` → `poi_id` | ∩ `slv_3p_poi @ V_r` |
| coordinate, partner branch | `pn_poi` → `poi_id` | ∩ `slv_pn_poi @ V_r` |
| review | `review` → `review_id` | ∩ `slv_3p_poi_review @ V_r` |

The node builds full target rows only for the changed key set. It filters every input by a semi-join on the key set (broadcast when small) and reads every input at `V_r`. Changed review rows whose `poi_id` is missing from `slv_3p_poi` are dropped and counted in `ctx.warn("review_poi_not_in_slv_3p_poi", n)`.

Consequence, recorded as D-01: every change to a silver row counts, including technical columns such as `_last_seen_at` and `updated_at` that change when the extract re-MERGEs a recrawled document. This matches `MQ-027` ("new data → append"), `MQ-040`, `MQ-047` ("every change counts as an update"), and the rejection of `row_hash` (`PC-09`). Volume is bounded by how often the source changes, not by the 15-minute cadence.

## 7. Idempotency, concurrency, retry, and recovery

### 7.1 Baseline per input

For each edge (input `s`, target `t`):

- `E` = the edge watermark (`last_src_version`, `last_src_table_id`) from `load_edge_wm`.
- `M` = the `src[s]` entry of the newest **valid** marker on `t` (§7.2).
- Keep only candidates whose `tid` equals the current table id of `s`.
- `B_s` = the max version among the kept candidates, or `None` if no candidate is kept.

`basis` label per input:
- `EDGE` when `E` wins.
- `MARKER` when `M` wins strictly (crash-recovery case).
- `FULL` when no candidate is kept: new edge with no marker, table recreated, or both stale.
- `FORCE` when `p_force = true`.

The lib's existing `edge_status` and `NO_DATA` shortcut are unchanged. If no edge is dirty against `E`, and the run is not forced, and the target exists, the node returns `NO_DATA` without reading the marker.

### 7.2 Commit marker

Write path, one call:

```
df.write.format("delta").mode("append").option("userMetadata", marker_json).saveAsTable(trg_fq)
```

Marker JSON, using lib `json_dumps` (sorted keys, compact). It contains only identifiers, versions, and counts, never data values:

```
{"vv_append": 1, "exec_id": "<uuid>", "run_id": "<id>", "pl_name": "PL_VV_TRANS_SLV_TO_ENR_15P",
 "node": "lh_vv_gold.enr.gld_enr_poi_info", "batch_ts": "<ISO UTC>", "rows": <n>, "force": false,
 "src": {"lh_vv_silver.dbo.slv_3p_poi": {"v": <V_r>, "tid": "<table id>"}, ...}}
```

`find_append_marker(trg_fq, history_limit)` scans `DeltaTable.history(history_limit)` from newest to oldest and returns the first commit whose `userMetadata` parses as JSON with `vv_append`.

Scanning **stops and returns None** at any of these:
- A commit whose operation is in `APPEND_INVALIDATING_OPS`: `RESTORE`, `DELETE`, `UPDATE`, `MERGE`, `TRUNCATE`, `CREATE OR REPLACE TABLE`, `REPLACE TABLE`, or `WRITE` with `mode = Overwrite`.
- The history being shorter than the table's commit chain.

After a manual rollback, older markers therefore stop counting, and the runbook requires a forced run (§12).

### 7.3 Behaviour matrix

| Scenario | Result |
|---|---|
| First run after DDL | Edges `NEW_EDGE`, no marker → FULL → every 3P and partner key is appended once |
| Unforced rerun, no new silver commit | All edges `UNCHANGED` or `MAINTENANCE_ONLY` → `NO_DATA`, 0 commits. Old rows untouched |
| New silver data for some POIs | Only those keys get a new row. Old rows untouched |
| Forced rerun (`p_force_nodes = <trg_tbl>`) | Every key gets another row with a new `batch_ts`. Old rows untouched. Forcing `slv_pn_poi` also forces info and coordinate (descendants) |
| Crash after gold commit, before node log or C11 | Next run: edge dirty against `E`, but `B = M` → only data newer than the marker → no duplicate |
| Transient error during the append (`with_retry`) | Each attempt first calls `find_append_marker` and looks for this `exec_id`. If found, the earlier attempt committed: take that commit's version and do not write again. An ambiguous commit is never written twice |
| NB_00 dies after C11 | Run log stays `RUNNING`. The lock expires after `p_lock_timeout_min = 35`. `close_stale_runs` marks the run `ABANDONED`. Later runs return `SKIPPED_CONCURRENT` until the lock expires. No data effect |
| Silver input recreated (new table id) | `FULL` for that role → keys present in that input are re-appended |
| Gold target dropped and recreated by DDL | Table exists with no marker, and edges are already advanced → `NO_DATA`. **Runbook: force the node** |
| `DRY_RUN` | Basis, changed counts, and QG are computed. No write, no marker. NB_00 does not advance edges (existing behaviour) |

### 7.4 Concurrency

- **Flow lock.** `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` serialises NB_00 runs and manual node `RUN`s. Parameters: `p_lock_timeout_min = 35` is greater than `p_dag_timeout_min + 5 = 30`. The pipeline activity timeout is 32 minutes, which is less than the lock timeout. A run that would still be appending after its lock could expire is therefore cancelled first. The pipeline has `concurrency = 1`.
- **Residual risk R-01 (P2).** The lib has no `LockLostError` (`NB_LIB_TRANSFORM_SLV_GLD.md` §6). If a run survives past its lock (the activity timeout did not cancel the Spark job) and a second run takes the lock, both can append the same slice. Result: duplicate history rows with different `updated_at`. No loss, and no change to existing rows. Backlog: Delta `txnAppId`/`txnVersion` idempotent writes.
- **Gold appends** are blind appends. They do not conflict with optimizeWrite/autoCompact or OPTIMIZE.
- **ctrl conflicts** (edge MERGE against extract watermark updates) are retried by the lib's existing `with_retry`.
- **The other recompute flow** (`PL_VV_TRANSFORM_SLV_TO_GLD_*`) has its own lock and its own edges. The lib's single-owner check now covers `APPEND` edges as well.

### 7.5 Retry policy

- Pipeline activity `retry = 0`. runMultiple `retry = 0` (lib). Inside a node, `with_retry` handles transient Delta/HTTP errors, using the marker check before each append attempt.
- A failed node does not advance its edges. The next scheduled run recomputes from the same baseline. That is the recovery path. No manual step is needed for code/data errors once they are fixed.

## 8. Partial-failure behaviour

| Failure | Effect | Recovery |
|---|---|---|
| `slv_pn_poi` FAILED (e.g. QG `required_inputs` on an empty `slv_pn_business_services`) | info and coordinate are `SKIPPED` (lib parent rule). Review still runs. Run is `PARTIAL_FAILED` and the pipeline goes red. 3P rows for info and coordinate are delayed too (L-02) | Fix the cause. The next run processes everything since the old baseline |
| info OK, coordinate FAILED | Only info's edges advance. The tables drift apart in time | Next run: coordinate appends its slice from its own baseline. Consumers must not assume the same `updated_at` across tables |
| QG block (pk null, pk duplicate, schema mismatch, rating overflow) | Node FAILED before the write. No commit | Fix the data or code. Automatic on the next run |
| Required input empty (`slv_3p_poi` for info and coordinate, `slv_3p_poi_review` for review, `slv_pn_business_services` for `slv_pn_poi`) | Node FAILED. Edges keep the pre-reload baseline, so a later refill is diffed against real history instead of being re-appended in full | Resumes automatically |
| runMultiple timeout or cancel | Node has no log row → `NOT_RUN`. Its edges are not advanced. If it committed, the marker prevents a duplicate | Automatic |
| Gold commit succeeded, node log append failed | `NOT_RUN` in ctrl, but the data is in gold. The marker has the `exec_id` for traceability | Automatic. The next run appends 0 rows for that slice |

## 9. Gold and silver expressions

Rules for every expression:
- Comments are in Vietnamese and include the Mapping row ID and its `context_ref`, e.g. `# COL-043 — MQ-036, MQ-061, docs/context/01_DATA_MODEL.md §4`.
- `build(ctx)` never sets `created_at` or `updated_at`. The lib adds them.
- Typed NULLs use `CAST(NULL AS <type>)`. Void types are rejected by the lib.
- Column order of `build` output equals the DDL order below.

### 9.1 `slv_pn_poi` (`NB_SLV_PN_POI`, RECOMPUTE)

- `NodeSpec`: `trg_tbl = "slv_pn_poi"`, `inputs = {"bs": "slv_pn_business_services", "i18n": "slv_pn_business_service_i18ns"}`, `pk = ("poi_id",)`, `required_inputs = ("bs",)`, `unique_checks = (("business_service_id_unique", ("business_service_id",), None),)`, default `write_mode = "MERGE"`.
- `vi = ctx.input("i18n").where(col("locale") == "vi").select("business_service_id", "name")`. `vi` is the only Vietnamese code in `e2`. User decision 2026-10-13.
- `bs = ctx.input("bs")` left-joined to `vi` on `bs.id = vi.business_service_id`.
- No `deleted` filter on either input. `MQ-046` says there is no delete handling (D-03).

| Column | Expression | Ref |
|---|---|---|
| `poi_id` | `uuid_md5(lit("partner_portal"), col("id"))` (`id` is `string` in `TABLE_CONFIGS`) | `ID-004`, `MQ-063`, `AGENTS.md` §9 |
| `business_service_id` | `id` | `DS-013` |
| `name` | `vi.name` (NULL when there is no `vi` row) | `decision.md` 2026-10-13, `e2` |
| `short_address` | `get_json_object(address, '$.full_address')` | `MQ-025`, `e1` |
| `ward` | `get_json_object(address, '$.ward')` | `decision.md` 2026-10-13, `e1` |
| `district` | `get_json_object(address, '$.district')` (an empty string is copied as is) | `decision.md` 2026-10-13 |
| `province_name` | `get_json_object(address, '$.city')` | `decision.md` 2026-10-13, `e1` |

### 9.2 `gld_enr_poi_info` (`NB_ENR_POI_INFO`, APPEND)

- `NodeSpec`: `write_mode = "APPEND"`, `pk = ("poi_id",)` (batch uniqueness), `required_inputs = ("poi",)`.
- Inputs: `poi`, `addr`, `contact`, `rating`, `price`, `hours`, `review`, `pn_poi`.
- 3P base is `slv_3p_poi p` restricted to the changed keys. Left joins on `poi_id`: `slv_3p_poi_address a`, `slv_3p_poi_contact c`, `slv_3p_poi_rating r`, `slv_3p_poi_price pr`, `slv_3p_poi_opening_hours oh`, and the review aggregate `rj`.

| # | Column | Type | 3P expression | Partner | Ref |
|---|---|---|---|---|---|
| 1 | `poi_id` | `STRING NOT NULL` | `p.poi_id` | `pn.poi_id` | `COL-001` |
| 2 | `poi_name` | `STRING` | `p.poi_name` | NULL | `COL-035` |
| 3 | `types` | `STRING` | `p.types_json` | NULL | `COL-036` |
| 4 | `subcategory_tags` | `STRING` | `p.types_json` | NULL | `COL-008`, `RULE-004` |
| 5 | `business_sector` | `STRING` | `p.business_sector` | NULL | `COL-037` |
| 6 | `business_category` | `STRING` | `p.business_category` | NULL | `COL-038` |
| 7 | `website_url` | `STRING` | `c.website_url` | NULL | `COL-039` |
| 8 | `short_address` | `STRING` | `a.address_viet_map` | NULL | `COL-040` |
| 9 | `district` | `STRING` | `a.district` | NULL | `COL-041` |
| 10 | `destination_name` | `STRING` | `coalesce(a.city, a.state_province)` | NULL | `COL-042`, `MQ-050` |
| 11 | `destination_context` | `STRING` | Sentence from `MQ-036`, built from `a.short_address`, `a.district`, `a.city`, and #10. **NULL rendering pending `U-01`** | NULL | `COL-043` |
| 12 | `rating` | `DECIMAL(4,2)` | `r.rating_overall` | NULL | `COL-044` |
| 13 | `userRatingCount` | `BIGINT` | `r.rating_count` | NULL | `COL-045` |
| 14 | `priceLevel` | `INT` | `pr.price_level` | NULL | `COL-046` |
| 15 | `opening_hours_text` | `STRING` | `oh.periods_json` | NULL | `COL-047` |
| 16 | `review_json` | `STRING` | §9.2.1 | NULL | `COL-048`, `RULE-006` |
| 17 | `time_to_spend` | `STRING` | `to_json(map(duration_label, 'Không cố định'))` | NULL (`COL-003` has no partner source) | `COL-003`, `RULE-003`, `decision.md` |
| 18 | `best_time_type` | `STRING` | NULL | NULL | `COL-004` |
| 19 | `best_time_from_month` | `INT` | NULL | NULL | `COL-005` |
| 20 | `best_time_to_month` | `INT` | NULL | NULL | `COL-006` |
| 21 | `cost` | `BIGINT` | NULL | NULL | `COL-007` |
| 22 | `created_at` | `TIMESTAMP` | lib `batch_ts` | lib | `COL-009` |
| 23 | `updated_at` | `TIMESTAMP` | lib `batch_ts` | lib | `COL-010` |

`duration_label` is a `CASE p.business_sector` with the 11 exact labels from BRD `RULE-003`:
- Explicit branches: `accommodation`, `f_n_b`, `attraction`, `tour_n_activities`, `shopping_n_retail`, `transport_route_base`, `transport_on_demand`, `vehicle_rental`, `spa_n_wellness`, `event`.
- `ELSE 'Thời lượng trải nghiệm'`, which also covers NULL.
- Match exactly. The 250 rows spelled `accomodation` (`NB_CREATE_DDL` comment V6b) fall to `ELSE`, as the rule is written.

`duration_text` is `'Không cố định'` because the minutes input does not exist. The NULL/`<= 0` branch of `COL-003` is the only reachable branch. The other display branches need a minutes source and are not written.

#### 9.2.1 `review_json` (3P)

1. Take reviews for the changed 3P POIs at `V_r`.
2. `rn = row_number() OVER (PARTITION BY poi_id ORDER BY time DESC, review_id ASC)`. Keep `rn <= 20`.
3. Element: `struct(rn, review_id, substring(text, 1, 350) AS review_text, time, published_at)`.
4. Per POI: `to_json(transform(array_sort(collect_list(elem)), x -> struct(x.review_id AS review_id, x.review_text AS review_text, x.time AS time, x.published_at AS published_at)))`.
5. A 3P POI with no review row gets `'[]'`: `coalesce(rj.review_json, '[]')`. Reason: `COL-048` defines the 3P value as a JSON array, and only the partner value as NULL. Main records this literal reading in `decision.md` (D-07).

`time` sorts as the raw ISO string, as the rule says. `review_id` is the deterministic tie-break. Fabric's session timezone is UTC, so `published_at` serialises from the UTC session (`[VERIFY]` in the runbook).

### 9.3 `gld_enr_poi_coordinate` (`NB_ENR_POI_COORDINATE`, APPEND)

- `NodeSpec`: `write_mode = "APPEND"`, `pk = ("poi_id",)`, `required_inputs = ("poi",)`, inputs `poi`, `addr`, `pn_poi`.

| # | Column | Type | 3P | Partner | Ref |
|---|---|---|---|---|---|
| 1 | `poi_id` | `STRING NOT NULL` | `p.poi_id` | `pn.poi_id` | `COL-011` |
| 2 | `name` | `STRING` | `p.poi_name` | `pn.name` | `COL-012` |
| 3 | `short_address` | `STRING` | `a.short_address` | `pn.short_address` | `COL-013` |
| 4 | `ward` | `STRING` | `a.ward` | `pn.ward` | `COL-014` |
| 5 | `district` | `STRING` | `a.district` | `pn.district` | `COL-015` |
| 6 | `province_name` | `STRING` | `a.city` | `pn.province_name` | `COL-016`, `MQ-026` |
| 7 | `destination_name` | `STRING` | `coalesce(a.city, a.state_province)` | NULL | `COL-017` |
| 8 | `lat` | `DOUBLE` | `a.lat` | NULL | `COL-018`, `RULE-005` |
| 9 | `lng` | `DOUBLE` | `a.lng` | NULL | `COL-019`, `RULE-005` |
| 10 | `created_at` | `TIMESTAMP` | lib | lib | `COL-020` |
| 11 | `updated_at` | `TIMESTAMP` | lib | lib | `COL-021` |

### 9.4 `gld_enr_poi_review` (`NB_ENR_POI_REVIEW`, APPEND, 3P only)

- `NodeSpec`: `write_mode = "APPEND"`, `pk = ("review_id",)`, `required_inputs = ("review",)`, inputs `review`.
- `block_checks = (("rating_cast_overflow", "rating IS NULL AND _src_rating IS NOT NULL"),)`. Implement it as a count inside `build` that raises `QualityGateError` (or `ctx.warn` plus a raise), because the output must contain only target columns.

| # | Column | Type | Expression | Ref |
|---|---|---|---|---|
| 1 | `review_id` | `STRING NOT NULL` | `rv.review_id` (copy, no hash) | `COL-022`, `MQ-062` |
| 2 | `poi_id` | `STRING` | `rv.poi_id` | `COL-023` |
| 3 | `rating` | `DECIMAL(3,1)` | `CAST(rv.rating AS DECIMAL(3,1))` (source `decimal(4,2)`) | `COL-025`, `MQ-051` |
| 4 | `review_text` | `STRING` | `rv.text` | `COL-027`, `MQ-057` |
| 5 | `review_date` | `TIMESTAMP` | `iso_utc_ts(rv.time)` | `COL-031`, `MQ-023` |
| 6 | `review_updated_at` | `TIMESTAMP` | `iso_utc_ts(rv.time)` | `COL-032`, `MQ-004` |
| 7 | `created_at` | `TIMESTAMP` | lib | `COL-033` |
| 8 | `updated_at` | `TIMESTAMP` | lib | `COL-034` |

`iso_utc_ts(col)` is a new lib §8 helper. It copies the extract rule `ISO_UTC_TS` exactly: the `ISO_INSTANT_RE` guard, then `to_utc_timestamp(CAST(col AS TIMESTAMP), current_timezone())`. Its result therefore equals `slv_3p_poi_review.published_at` (`COL-032` note).

`build` records `ctx.warn("review_date_ne_published_at", n)`. The expected value is 0.

## 10. Alternatives and trade-offs

### 10.1 Orchestration and write path

| Option | Pros | Cons | Decision |
|---|---|---|---|
| **A1. Additive `APPEND` mode in `NB_LIB_TRANSFORM_SLV_GLD`; NB_00 clone calls `orchestrate()`** | Reuses the proven lock, inbox, pinning, runMultiple, logs, and edge advance. One code path for state. The NB_00 clone stays 4 cells, matching `MQ-044` | Edits a shared lib outside `scope.files`. Regression risk to the RECOMPUTE flow | **Selected.** Changes are additive and behind `load_mode`/`write_mode`. The other flow has no seeded edges yet (`NB_00_ORCHES_SLV_TO_GLD.md` §1). INV-12 is verified locally and at runtime |
| A2. Append notebooks with their own lock and inbox, built on lib helpers | Shared lib untouched | Duplicates the state machine (lock, inbox, edge MERGE). The two copies would drift. `orchestrate()` ignores non-`RECOMPUTE` edges anyway | Rejected |
| A3. Seed edges as `RECOMPUTE` and use MERGE | No lib change | Breaks `APPEND`, `MQ-027`, and `PC-08`. Updates rows | Rejected |
| A4. Pipeline runs the 3 notebooks directly and appends a full snapshot every 15 minutes | Simplest | Unbounded growth (about 19k rows × 96 per day per table). Breaks `MQ-040`. No lock, no inbox, no orchestrator | Rejected |

### 10.2 Change detection

| Option | Decision and reason |
|---|---|
| **C1. Input-row diff between Delta versions (baseline vs read)** | **Selected.** Version-based, matching ADR-G01. "Every change counts", matching `MQ-047`. Needs no stored hash, matching `PC-09`. Cost is two snapshot reads of small tables per dirty edge |
| C2. Compare candidate rows with the latest appended gold row | Self-idempotent. But it is content gating, which in practice is the `row_hash` rule the user rejected (`MQ-013` → `MQ-030`). It also reads an ever-growing history. Rejected |
| C3. Silver `updated_at` greater than a time watermark | Compares clocks across processes. `NB_LIB_TRANSFORM_SLV_GLD.md` §2 forbids this. Rejected |
| C4. Delta Change Data Feed | Needs table properties on extract-owned silver tables. Out of scope. Rejected |

### 10.3 Append idempotency

| Option | Decision and reason |
|---|---|
| **I1. Commit marker in `userMetadata` and baseline = max(edge, marker)** | **Selected.** Atomic with the data. Closes the crash window between the gold commit and the edge advance, and makes in-node retries safe. No extra column |
| I2. Accept at-least-once | Any crash or ambiguous retry duplicates a whole slice. Rejected |
| I3. `txnAppId`/`txnVersion` idempotent writes | Guards against concurrent writers, but needs a monotonic slice id. Backlog for R-01 |
| I4. `exec_id` column on gold rows | Breaks INV-10 (the DDL must equal Mapping §5). Rejected |

### 10.4 `slv_pn_poi`

| Option | Decision and reason |
|---|---|
| **S1. `RECOMPUTE` node in this pipeline (lib MERGE with `row_hash`)** | **Selected.** Follows the silver L2 contract (`01_DATA_MODEL.md` §6). Only real changes create commits, so gold edges stay quiet. The `row_hash` exclusion in `PC-09` is scoped to the three `gld_enr_*` tables. Recorded as D-02 |
| S2. Overwrite every run, without `row_hash` | Avoids a hash, but breaks the silver L2 convention and the lib contract. Every run creates a data commit. Not selected. It is the fallback if the user reads `row_hash` as excluded everywhere |
| S3. Compute the partner `poi_id` in gold | Breaks `MQ-063`. Rejected |

### 10.5 Seed location

Alternatives:
- `NB_CREATE_DDL` new cells. In `scope.files`, and the request asks for the existing locations.
- A new `NB_SETUP_ENR_POI`. This is the naming-convention role for seeding edges, `02_NAMING_CONVENTION.md` §2.

**Selected: `NB_CREATE_DDL`.** Record it as deviation D-05.

## 11. Implementation plan

Deploy and run in the order below. The lib must be deployed before any notebook that calls it (`02_NAMING_CONVENTION.md` §8).

### 11.1 `NB_LIB_TRANSFORM_SLV_GLD` (additive)

1. **§1 constants**
   - Add `EDGE_LOAD_MODES = ("RECOMPUTE", "APPEND")`, and keep `EDGE_LOAD_MODE`.
   - Add `NODE_WRITE_MODE = {"RECOMPUTE": "MERGE", "APPEND": "APPEND"}`.
   - Add `APPEND_TECH_COLUMNS = (("created_at", "timestamp"), ("updated_at", "timestamp"))`.
   - Add `APPEND_MARKER_KEY = "vv_append"`.
   - Add `APPEND_INVALIDATING_OPS` (§7.2).
2. **§4 config and DAG**
   - Add a trailing `load_mode: str = "RECOMPUTE"` field to `Edge`, so positional construction still works.
   - `load_config_rows` filters with `upper(trim(load_mode)) IN ('RECOMPUTE','APPEND')` and returns `load_mode`.
   - `build_dag` adds the error "node <fq> has edges with more than one load_mode" and stores `nodes[fq]["load_mode"]`. Its error message lists both modes.
3. **§6 node: spec and context**
   - Add `NodeSpec.write_mode: str = "MERGE"`.
   - `_resolve_node` raises `ConfigError` when `spec.write_mode != NODE_WRITE_MODE[node load_mode]`.
   - `NodeContext` gets a `basis` dict (role → {from, to, basis}) and `changed(role)` (§6).
   - Add `find_append_marker(trg_fq, history_limit, exec_id=None)`.
   - Add `check_append_schema(trg_fq, df)`. Build columns must equal the target columns minus `APPEND_TECH_COLUMNS`: same names (case-insensitive) and `simpleString` types. Otherwise `ConfigError`.
   - Add `append_target(trg_fq, df, marker, exec_id)`. Inside `with_retry`: if the marker for this `exec_id` exists, return its version. Otherwise write once.
4. **§6 node: `run_node`**
   - Keep steps 1 to 4 (config, lock, parent skip, versions, `edge_status`, `NO_DATA` shortcut).
   - For `APPEND`, a missing target → `ConfigError("create with NB_CREATE_DDL")`.
   - Then compute the baselines (§7.1), check `required_inputs`, and call `build(ctx)`.
   - Reject technical columns and void types, then call `check_append_schema` and `quality_gate`.
   - Persist `df` with `MEMORY_AND_DISK`. Its inputs are version-pinned, so recomputing it gives the same result.
   - If `n > 0` and the mode is `RUN`: `batch_ts` = one `current_timestamp()` from Spark, added with `lit`; then `append_target`.
   - `res`: `inserted = n`, `updated = 0`, `deactivated = 0`, `trg_version`, and `qg` with `basis` and changed counts per role.
   - Never call `add_row_hash`, `diff_counts`, `ensure_target`, or `merge_target` on this path.
5. **§8 helpers**: add `iso_utc_ts(col)` (§9.4).
6. **`orchestrate`**: no logic change. It already advances APPEND edges from `src_versions_json`.

### 11.2 Notebooks

- `NB_00_ORCHES_SLV_TO_ENR_15P`: same 4 cells as `NB_00_ORCHES_SLV_TO_GLD`. Defaults:
  - `p_pl_name = "PL_VV_TRANS_SLV_TO_ENR_15P"`, `p_mode = "RUN"`.
  - `p_max_parallel = "2"`, `p_node_timeout_min = "15"`, `p_dag_timeout_min = "25"`, `p_lock_timeout_min = "35"`.
  - `p_history_limit = "1000"`; `p_force_nodes`, `p_non_data_ops`, and `p_run_id` empty.
  - Default lakehouse `lh_vv_bronze`.
- Node notebooks follow the lib node contract (5 cells, `p_*` string parameters, `finish_node`). Default lakehouse `lh_vv_bronze`. All table names are fully qualified.

### 11.3 `NB_CREATE_DDL` new cells (idempotent, Vietnamese comments)

1. `nb_name`: if the column is missing, `ALTER TABLE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config ADD COLUMNS (nb_name STRING)`.
2. `CREATE SCHEMA IF NOT EXISTS lh_vv_gold.enr`.
3. `CREATE TABLE IF NOT EXISTS` for the three tables, with exactly the column order, types, and `NOT NULL` in §9.2 to §9.4. Use `USING DELTA` and `TBLPROPERTIES` with the same optimizeWrite/autoCompact keys as lib `TABLE_PROPERTIES`. No partitioning, no `CLUSTER BY`.
4. After the create, run `DESCRIBE` and compare with the expected list. Raise on any difference, for example an existing table with drifted columns.
5. Seed 14 edges with insert-only `WHERE NOT EXISTS` on the logical key:
   - `id = MAX(id) + seq`, `is_active = 1`.
   - `align_path` and `dedup_order` NULL.
   - `src_schema = 'lh_vv_silver.dbo'`.
   - Every row has `pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'`.

| seq | src_tbl | trg_schema.trg_tbl | load_mode | nb_name | priority |
|---|---|---|---|---|---|
| 1 | `slv_pn_business_services` | `lh_vv_silver.dbo.slv_pn_poi` | `RECOMPUTE` | `NB_SLV_PN_POI` | 1 |
| 2 | `slv_pn_business_service_i18ns` | `lh_vv_silver.dbo.slv_pn_poi` | `RECOMPUTE` | `NB_SLV_PN_POI` | 1 |
| 3 | `slv_3p_poi_review` | `lh_vv_gold.enr.gld_enr_poi_review` | `APPEND` | `NB_ENR_POI_REVIEW` | 1 |
| 4–11 | `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_pn_poi` | `lh_vv_gold.enr.gld_enr_poi_info` | `APPEND` | `NB_ENR_POI_INFO` | 2 |
| 12–14 | `slv_3p_poi`, `slv_3p_poi_address`, `slv_pn_poi` | `lh_vv_gold.enr.gld_enr_poi_coordinate` | `APPEND` | `NB_ENR_POI_COORDINATE` | 2 |

Do not seed watermark rows. NB_00 creates the lock row and the edge rows.

The extracts are unaffected:
- Extracts filter `ctrl_mng_pipeline_config` by `pl_name` and source table (`NB_LIB_EXTRACT_RAWDATA` `load_table_specs`).
- Extracts read only watermark rows where `trg_tbl IS NULL` and the source table matches.
- The FL_00 pre-check filters on `src_tbl = 'partner_raw_data'`.

### 11.4 Pipeline `PL_VV_TRANS_SLV_TO_ENR_15P`

- One `TridentNotebook` activity, `NB_00_ORCHES_SLV_TO_ENR_15P`, in the FL_00 export format. `notebookId` and `workspaceId` are per environment, as in FL_00.
- Activity parameters, all string type:
  - `p_pl_name = @pipeline().Pipeline`, `p_run_id = @pipeline().RunId`, `p_mode = RUN`.
  - The timeouts from §11.2.
- Activity policy: `timeout = 0.00:32:00`, `retry = 0`. Pipeline `concurrency = 1`.
- The 15-minute schedule is set in Fabric and enabled only after the runbook passes.
- NB_00 raises when the status is not `SUCCESS` or `NO_DATA`, so the activity fails visibly. `SKIPPED_CONCURRENT` returns without raising.

### 11.5 `decision.md` entries Main writes before code (Vietnamese)

| ID | Item |
|---|---|
| D-01 | Change-detection rule: input-row diff by version, every column, including silver technical columns (§6) |
| D-02 | `slv_pn_poi` uses the lib RECOMPUTE MERGE with `row_hash`. The `PC-09` `row_hash` exclusion applies to the `gld_enr_*` tables only. Fallback is S2 |
| D-03 | No `deleted` filter on the partner inputs, per `MQ-046`. Residual R-02: a deleted business service keeps appearing |
| D-04 | `slv_pn_poi` is an L2 table with the L1 prefix `slv_pn_` (user name, `MQ-063`). The `_15P` suffix does not match `CADENCE_RE`, so the lib's cadence check is skipped (WARN) for any cross-flow read |
| D-05 | Edge seed and gold DDL live in `NB_CREATE_DDL`, not in `NB_SETUP_*`. The lib and the two context docs are added to the scope |
| D-06 | No Spark-free pre-check. A Spark session starts every 15 minutes on the shared F16. Backlog |
| D-07 | 3P `review_json` with no reviews is `'[]'` (§9.2.1) |

## 12. Rollout, rollback, and forward recovery

**Rollout (Fabric DEV):**
1. Deploy the lib.
2. Run `NB_00_ORCHES_SLV_TO_GLD` with `p_mode = PLAN`. Expect the same `ConfigError` as before (no RECOMPUTE edges), which proves INV-12.
3. Deploy the 4 nodes and the orchestrator.
4. Run the new `NB_CREATE_DDL` cells.
5. Run NB_00 `PLAN`: 4 nodes, 14 edges, all edges `NEW_EDGE`.
6. Run NB_00 `RUN` for the first full append.
7. Run NB_00 `RUN` again. Expect `NO_DATA` and 0 new commits.
8. Run NB_00 `RUN` with `p_force_nodes = gld_enr_poi_review` (and the others). Expect a second batch and old rows unchanged.
9. When a new silver commit arrives naturally, run `RUN`. Expect only the changed keys.
10. Create the pipeline, trigger it once, then enable the schedule.

**Rollback:**
- Stop: disable the schedule, then `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0 WHERE pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P'`.
- Bad batch:
  1. Identify the commit with `DESCRIBE HISTORY` (`userMetadata.exec_id`, `batch_ts`).
  2. Run `RESTORE TABLE … TO VERSION AS OF <v-1>` (latest batch only) or `DELETE … WHERE updated_at = <batch_ts>`. Either one needs explicit user approval.
  3. This stops the marker scan (§7.2) and the edges are already advanced. **You must then run NB_00 with `p_force_nodes = <trg_tbl>`** to re-append a full, correct snapshot.
- Full removal (task rollback):
  1. Deactivate the edges.
  2. Delete this pl's config rows.
  3. Delete the watermark rows `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P`, `wm_e__gld_enr_poi_%`, and `wm_e__slv_pn_poi__%`.
  4. `DROP TABLE` the 3 gold tables and `slv_pn_poi`.
  
  `AGENTS.md` §11 requires these steps, with forward recovery, in `runtime-runbook.md`. Leave the `nb_name` column in place: it is harmless, and a Delta column cannot be dropped without column mapping.
- Lib rollback: only after the flow is deactivated. The old lib ignores `APPEND` edges, and the `slv_pn_poi` edges alone would form a partial DAG.

**Forward recovery:**
- Code or expression fix: deploy, then force the affected node(s). They append a full snapshot with the new logic.
- Silver input recreated: automatic (`FULL` basis).
- Gold target recreated: run `NB_CREATE_DDL`, then force the node.

## 13. Observability

- `ctrl_log_run` row per run: `read_mode = VERSION_INBOX`, `read_note` holds the plan summary.
- `ctrl_log_table_run` row per node, APPEND fields:
  - `entity_rows` = rows built, `inserted_rows` = rows appended, `updated_rows = 0`, `deactivated_rows = 0`.
  - `trg_version` = the append commit version.
  - `src_versions_json` = read versions.
  - `qg_json` = {`mode`, `force`, `inbox`, `basis` per input {from, to, basis}, `changed` per role, `rows`, `blocks`, `warns`}.
- Gold `DESCRIBE HISTORY`: every flow commit is `WRITE` (Append) with a `vv_append` marker, or maintenance. **A `MERGE`, `UPDATE`, or `DELETE` here is an INV-01 violation.**
- Runbook checks (aggregates only):
  - `GROUP BY key, updated_at HAVING count(*) > 1` gives 0.
  - `count(*) WHERE created_at <> updated_at` gives 0.
  - One distinct `updated_at` per append commit.
  - Rows per batch match `inserted_rows`.
  - Warn counters `review_poi_not_in_slv_3p_poi` and `review_date_ne_published_at` are 0, or explained.

## 14. Security and data handling

- No secrets or tokens. The pipeline uses only the workspace notebook reference, as FL_00 does.
- SQL values go through `spark.sql(..., args=...)`. Identifiers go through `is_identifier`/`is_fq_name` and then `quote_name`, as in the lib.
- The commit marker contains no data values.
- `review_text` and addresses are copied by design (Mapping §5). `author_name` is not copied.
- Runbook and evidence queries print only counts, keys or IDs, versions, and timestamps. They print no review text, address, or name. Samples are limited to 50 rows (`AGENTS.md` §8).
- Fabric DEV only, until the user approves otherwise.

## 15. Verification strategy

**Local (before review):**
- `python scripts/vv.py verify 20261012-implement-gld-enr-poi-flow` must pass. Note that `cmd_verify` lints `.py`, `.sql`, and `.json` files and runs `tests/`. It does **not** inspect `.ipynb` files.
- Add `tests/test_enr_poi_contract.py`: pure Python, no Spark. It parses the notebook JSON and the pipeline JSON and asserts:
  1. The `NB_CREATE_DDL` DDL for the 3 tables equals Mapping §5 (names, order, types, `NOT NULL` only on `poi_id`/`review_id`), and the dropped columns are absent.
  2. Every `COL-xxx` row of Mapping §5 for each table appears as an expression comment in its node notebook.
  3. The edge seed has exactly the 14 rows in §11.3.
  4. The pipeline passes `p_pl_name = @pipeline().Pipeline` and the timeouts, with lock > DAG + 5 and activity timeout < lock.
  5. The pure helpers for baseline choice (§7.1) and marker parse/stop rules (§7.2) behave as specified. Factor them out as Spark-free functions in the lib cell, or mirror them.
- Spot-check that the RECOMPUTE path of `run_node` is byte-for-byte unchanged in behaviour (diff review).

**Review routing** (unchanged from `task-state.yaml`):
- `state-correctness-reviewer`: §5, §7, §8.
- `sql-data-reviewer`: §6, §9.
- `spark-runtime-reviewer`: lib edits and F16 cost.
- `fabric-pipeline-reviewer`: §11.4.
- Then `risk-gate`.

**Runtime (`runtime-runbook.md`, Vietnamese, Fabric DEV):**
- Follow the rollout steps 1 to 10.
- `[VERIFY]` items:
  1. Delta writer option `userMetadata` shows up in `DESCRIBE HISTORY`. **If not: stop, classify as `architecture`, and route back.**
  2. `lh_vv_gold.enr` can be created, and `NOT NULL` is enforced.
  3. The activity timeout cancels the Spark job.
  4. The session timezone is UTC.
  5. First-run row counts equal the distinct `poi_id` counts (`slv_3p_poi` plus live `slv_pn_poi`) and the review count.
  6. The second `RUN` is `NO_DATA`.
  7. The forced run doubles the row count and leaves old rows' timestamps unchanged.
  8. A natural new input appends only the changed keys.
  9. A simulated crash: cancel NB_00 after a node's commit, then rerun. No duplicate appears, and `qg_json.basis` shows `MARKER`.
- The change-detection proof needs a real new silver commit in DEV. Do not hand-edit extract-owned silver tables.

## 16. Evidence needed

No data evidence is missing. The evidence gate stays `pass`.

One user answer is required before Main writes one expression. It does not block the state, ordering, or recovery design:

| ID | Blocks | Question | Why the rule sources do not answer it |
|---|---|---|---|
| `U-01` | `COL-043` expression only | When `slv_3p_poi_address.short_address`, `district`, `city`, or `destination_name` is NULL, should `destination_context` be NULL, use an empty string for that placeholder, or something else? | `MQ-036` fixes the sentence but not how missing parts are rendered. SQL `concat` and `format_string` give different results |

If `U-01` is not answered and recorded in `decision.md`, Main routes the task to `user_decision` instead of choosing a rendering.

Optional sizing probe to support the `U-01` answer (read-only, Fabric DEV, counts only): NULL and empty-string counts of `short_address`, `district`, `city`, and `state_province` on `lh_vv_silver.dbo.slv_3p_poi_address`. Pass: one row of counts and no address text.

## 17. Residual risks

| ID | Severity | Risk | Mitigation |
|---|---|---|---|
| R-01 | P2 | Duplicate appends if a run outlives its lock | Activity timeout (32 minutes) < lock timeout (35). Backlog: `txnAppId`/`txnVersion` |
| R-02 | P3 | Deleted partner services keep their rows (`MQ-046`) | Visible in `slv_pn_business_services.deleted`. Revisit when delete handling is specified |
| L-01 | P2 | A row built while an extract is half-written can mix input versions | Corrected on the next run. History keeps the intermediate row |
| L-02 | P2 | A failed `slv_pn_poi` delays 3P appends for info and coordinate | Pipeline goes red. Automatic catch-up |
| L-03 | P2 | Spark starts every 15 minutes on the shared F16 (no Spark-free pre-check) | D-06 backlog |
| L-04 | P3 | Silver technical-column churn (recrawls) creates appends whose gold content is identical | Intended per D-01. Monitor `inserted_rows` |
