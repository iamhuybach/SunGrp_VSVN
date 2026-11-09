RESULT: PASS

## Main brief

### Decision
- LEFT JOIN the live `slv_poi_media_info` row where `is_cover` is true, on `poi_id`, in `srvinfobuild`, using `ctx.input("media")` with the default `live_only`, the same as gallery. Output `cover_id` = `media_id` and `cover_blob_url` = `blob_url`, placed after `review_count`. More than one cover per emitted `poi_id` → `QualityGateError`. `required_inputs` stays `("entity",)`.
- Existing environments: a new trailing `NB_CREATE_DDL` pair `srvcovermd`/`srvcoverpy` ALTERs both columns `AFTER` and inserts one edge on `PL_VV_TRANS_SLV_TO_GLD_30M`, under the flow lock. New environments: `init_tables` and `init_seed_ctrl` hold the same contract.
- PostgreSQL gets two `text` columns and the entity two `String` fields. The pipeline JSON is unchanged: the DAG comes from ctrl rows.
- Blocking: 4 test files outside `scope.files` pin cell positions, the info inputs, the info DDL source cell, and the seed row count (73).

### Invariants Main must preserve
- `srvinfobuild` `SPEC`: `pk=("poi_id",)`, `write_mode="MERGE"`, `required_inputs=("entity",)`. `inputs` = the old 5 + `"media": "slv_poi_media_info"`.
- Order `... review_count, cover_id, cover_blob_url, row_hash, created_at, updated_at, deleted_at` is identical in `OUT_COLS`+TECH, `srvcoverpy` `INFO_COLS`, and `init_tables`.
- Cover predicate is exactly `.where(F.col("is_cover"))`. No `with_cover`, `row_number`, `is_active`, `deleted`, cast, trim, or `F.when(is_google, ...)` on the cover columns.
- `srvinfobuild` keeps `live_only=False` exactly 3 times, `F.when(is_google,` exactly 4 times, and no `lh_vv_gold`.
- `srvcoverpy`: one textual `ALTER TABLE` with ` AFTER `, `_refresh_lock()` before the ALTER and before the INSERT, no DROP/DELETE/TRUNCATE/`UPDATE {CFG}`/REPLACE/RESTORE/columnMapping/`_30P`. Rerun = no write.
- The new seed row is the last entry in `PIPELINE_CONFIG_ROWS`. Active `gld_srv_poi_info` edges = `SPEC.inputs` values, all on `_GLD30`.
- `gld_srv_serve.pg.sql` has no executable `ALTER`. The Testcontainers init runs the file.
- Gold, PostgreSQL, and entity column sets and types match: STRING→text→String, nullable.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 0 | `.ai/tasks/20261108-gld-srv-poi-info-cover/task-state.yaml` | `scope.files` | add `tests/test_gld_srv_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py` | `python scripts/vv.py validate 20261108-gld-srv-poi-info-cover` passes |
| 1 | `notebooks/NB_GLD_SRV_POI_INFO.ipynb` | `srvinfobuild` | apply doc `### Build cell changes` (COVER_COLS, OUT_COLS, `_cover`, `md` input/_require, join, select, metric, SPEC.inputs) | `test_info_cover_build_rule`, `test_node_specs` pass |
| 2 | `notebooks/NB_GLD_SRV_POI_INFO.ipynb` | `srvinfomd` | append the cover line (doc `## Implementation plan` step 1) | the line is present |
| 3 | `notebooks/NB_CREATE_DDL.ipynb` | after `cmscfgpy` | append markdown `srvcovermd` + code `srvcoverpy`, verbatim from doc `### srvcovermd` / `### srvcoverpy`; JSON key layout like `mlsrcpy` | `test_info_cover_patch_cell` passes |
| 4 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_tables` gld_srv_poi_info spec | after `('review_count', 'INT', None),` add `('cover_id', 'STRING', None),` `('cover_blob_url', 'STRING', None),` | `test_info_cover_seed_and_init_ddl` passes |
| 5 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` end | comment + row `(_GLD30, _S, 'slv_poi_media_info', _G, 'gld_srv_poi_info', 1, 1, 'RECOMPUTE', None, None, 'NB_GLD_SRV_POI_INFO'),` as the last entry | the same test passes |
| 6 | `sql/postgres/gld_srv_serve.pg.sql` | header + `CREATE TABLE apps.srv_poi_info` | after header line 16, the comment with the manual ALTER (doc step 5); after `review_count integer,` add `cover_id text,` `cover_blob_url text,` | `test_gold_and_pg_columns_and_types_match`, `test_info_cover_mapping_and_pg_ddl` pass |
| 7 | `services/.../entity/SrvPoiInfo.java` | after `reviewCount` | `@Column(name = "cover_id") private String coverId;` and `@Column(name = "cover_blob_url") private String coverBlobUrl;` (two-line style) | `test_entities_match_gold_columns_types_and_keys` passes; mvnw compile is OK |
| 8 | `docs/context/mapping_gld_srv_poi_info.md` | §1.1, §1.2 | doc `### Mapping doc edits` (inputs, live_only line, line 18 list, edge list, new cover bullet, 2 table rows after `review_count`) | `test_mapping_targets_match_out_cols`, `test_info_cover_mapping_and_pg_ddl` pass |
| 9 | `tests/test_srv_poi_serving_contract.py` | end of file | append the doc `### Test changes` block (4 tests + helpers) | all 4 tests pass |
| 10 | `tests/test_gld_srv_poi_contract.py` | `test_node_specs`, `test_build_columns_match_ddl`, `test_info_rating_patch`, `test_review_source_patch_cell` | add the media input; `srvratepy`→`srvcoverpy` for INFO_COLS; shift id slices by 2 and add `ids[-2:] == ["srvcovermd","srvcoverpy"]` | the file passes |
| 11 | `tests/test_initial_ddl_contract.py` | gold info line in the table-spec test; `test_gld_srv_patch_create_matches_init`; `test_pipeline_config_rows_match_sources`; `test_pl_cadence_patch_cell` | `srvratepy`→`srvcoverpy` (2 places); add the `srvcoverpy` EDGES_ON loop after the `srvrevpy` loop, `73`→`74`; `[-14:-12]`→`[-16:-14]` | the file passes |
| 12 | `tests/test_enr_poi_contract.py` | id-slice block (l.223–234) | shift all slices by 2; cmscfg at `[-4:-2]`; add srvcover `[-2:]` | the file passes |
| 13 | `tests/test_poi_entity_contract.py` | id-slice block (l.635–646) | same as #12 | the file passes |

### Order and stop points
1. STOP (user decision / Main): widen `scope.files` (row 0). If the user declines, stop: the change cannot pass the contract tests.
2. Rows 1–2, then 3, then 4–5 (one contract across the three notebooks).
3. Rows 6–8.
4. Rows 9–13, then run the tests below. Stop for a fix if any test fails; do not relax an assertion other than the ones in rows 10–13.
5. STOP (user, runtime, not claimed): Fabric rollout from doc `## Rollout`: run `srvcoverpy`, then publish `NB_GLD_SRV_POI_INFO` right away, ideally with the 30M trigger paused. Then the PostgreSQL ALTER on existing databases, then the service deploy. Confirm the loader maps by name.

### Tests and verification
- `python -m pytest tests/test_srv_poi_serving_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_poi_media_amenity_contract.py -q`
- New: `test_info_cover_patch_cell`, `test_info_cover_build_rule`, `test_info_cover_seed_and_init_ddl`, `test_info_cover_mapping_and_pg_ddl`. Existing, must pass: `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys`, `test_node_specs`, `test_build_columns_match_ddl`, `test_info_rating_patch`, `test_info_rating_build_rules`, `test_mapping_targets_match_out_cols`, `test_pipeline_config_rows_match_sources`, `test_gld_srv_patch_create_matches_init`, `test_pl_cadence_seed`, `test_no_old_cadence_suffix_in_active_surface`, `test_edges_create_vs_init`.
- `python -m pytest tests -q`
- `services\data-serving-service\mvnw.cmd -f services/data-serving-service/pom.xml -q -DskipTests compile`. The Testcontainers tests need Docker; the user runs them.
- Runtime probes (user): doc `## Verification` runtime section.

### Read only if needed
- `## Resolution of model-design questions`: rows 1, 3, 4, 5 (position, cover predicate, pl_name, optional input).
- `## Ordering`, `## Partial failure`: rows 1, 3 and Stop 5.
- `### Build cell changes`: rows 1–2.
- `### srvcovermd`, `### srvcoverpy`: row 3.
- `## Implementation plan` steps 3–6: rows 4–7.
- `### Mapping doc edits`: row 8.
- `### Test changes`: rows 9–13.
- `## Rollout`, `## Rollback and forward recovery`: Stop 5.
- `## Alternatives`: why not gallery, a new cover rule, `required_inputs`, an edit to `srvratepy`, or `ensure_target`.

# Architecture: 20261108-gld-srv-poi-info-cover

Ledger: D-01. Model: `model-design.md` `## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`. This document closes `## Conflicts and questions` 1–5 with the evidence cited below. It does not change grain, keys, or column types.

Blocking precondition (scope, not evidence): adding the edge, the columns, and the trailing `NB_CREATE_DDL` cells breaks pinned assertions in four test files that are not in `scope.files`: `tests/test_gld_srv_poi_contract.py`, `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py`. Main adds them to `scope.files` before editing (precedent: `20261026-add-poi-multi-lang-experience` architecture, Stop 1). No other file is needed. The pipeline JSON stays out of scope: the 30M DAG comes from `ctrl_mng_pipeline_config` rows (`NB_00_ORCHES_SLV_TO_GLD` header, `orchestrate`). The JSON only passes `p_pl_name`.

## Scope

- `NB_GLD_SRV_POI_INFO` `srvinfobuild`: new input role `media` = `slv_poi_media_info`. LEFT JOIN the `is_cover` row on `poi_id`, which gives `cover_id`, `cover_blob_url`. Add a guard and a metric. `srvinfomd` gets one line.
- `NB_CREATE_DDL`: new trailing cells `srvcovermd` / `srvcoverpy`. They ALTER the two columns `AFTER review_count` and insert one ctrl edge, under lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`.
- `NB_SETUP_INITIAL_DDL`: `init_tables` gets the two columns. `init_seed_ctrl` gets one edge row.
- `sql/postgres/gld_srv_serve.pg.sql`: two `text` columns, plus a header comment with the manual ALTER for existing databases.
- `SrvPoiInfo.java`: two `String` fields.
- `docs/context/mapping_gld_srv_poi_info.md` §1.1 and §1.2.
- Tests: new cover tests in `tests/test_srv_poi_serving_contract.py`, plus pinned-count and position updates in the four test files above.

## Non-goals

- No change to `with_cover`, `is_cover`, `NB_SLV_POI_MEDIA_INFO`, `NB_GLD_SRV_POI_MEDIA_GALLERY`, gallery grain, or the `slv_poi_media_info` schema.
- No `is_active` / `deleted` predicate in the gold node. The cover is the live `is_cover` row, as gallery reads it.
- No DTO, endpoint, or API field. No `docs/poi-serving-api/`. No pipeline JSON. No PostgreSQL loader change.
- No change to `srvratepy`, `srvpoipy`, or any earlier `NB_CREATE_DDL` cell.

## Resolution of model-design questions

1. Column position: `cover_id`, `cover_blob_url`, right after `review_count` and before `row_hash`, in `OUT_COLS`, `INFO_COLS`, `init_tables`, PostgreSQL, and the entity. This follows the precedent of `srvratepy` (`ALTER ... AFTER`). `ensure_target` would otherwise append after `deleted_at`, and `test_build_columns_match_ddl` pins the order.
2. Duplicate covers. Evidence: `NodeContext.input(role, live_only=True)` in `NB_LIB_TRANSFORM_SLV_GLD` keeps only `deleted_at IS NULL` rows. `sql_merge_target` sets `deleted_at` on every target row missing from the source and keeps every other row equal to the latest build output. The exit QG (`quality_gate`, `for name, cols, where in spec.unique_checks`) runs `one_cover_per_poi` on that build output. So the live rows of `slv_poi_media_info` hold at most one `is_cover = true` per `poi_id`, and they all have `is_active = true` (`build` sets `F.lit(True)`). Soft-deleted rows can keep `is_cover = true`, but `live_only` removes them. Gallery calls `ctx.input("media")` with the same default. The info node calls `ctx.input("media")` without `live_only`. It also adds a `_cover` guard that stops with `QualityGateError` instead of choosing a row (same pattern as `_rating`, D-01 of the rating task). The pk QG on `poi_id` is a second stop.
3. `pl_name`: `PL_VV_TRANS_SLV_TO_GLD_30M`. `plcadpy` renamed `_30P` → `_30M`. `init_seed_ctrl` has `_GLD30 = "PL_VV_TRANS_SLV_TO_GLD_30M"`. All five current `gld_srv_poi_info` edges, and the `slv_poi_media_info` producer edges, are on `_GLD30`. `test_no_old_cadence_suffix_in_active_surface` forbids `_30P` outside `NB_CREATE_DDL`.
4. Optional input: `required_inputs` stays `("entity",)`. If `slv_poi_media_info` is empty, both columns are null on every row (LEFT JOIN, D-01). `required_inputs` exists to stop mass soft-deletes of the target, and an empty media input soft-deletes no info row. The media node already stops on empty input (`required_inputs=("media_3p", "i18n")`).
5. Mapping doc: see `## Implementation plan` step 7.

## Invariants

- I1. `gld_srv_poi_info` has one row per `poi_id`. NodeSpec `pk=("poi_id",)`, `write_mode="MERGE"`, and `required_inputs=("entity",)` do not change.
- I2. `cover_id` / `cover_blob_url` equal `media_id` / `blob_url` of the live `slv_poi_media_info` row with the same `poi_id` and `is_cover = true`. Otherwise both are null. There is no fallback, cast, trim, or source filter, and the rule applies to Google and partner rows alike.
- I3. More than one live cover row for an emitted `poi_id` raises `QualityGateError` before any write.
- I4. Column order is identical in `OUT_COLS` + TECH, `srvcoverpy` `INFO_COLS`, and `init_tables`: `... rating_overall, rating_count, review_count, cover_id, cover_blob_url, row_hash, created_at, updated_at, deleted_at`.
- I5. The column sets, types, and pk match across gold DDL + NodeSpec `pk`, `apps.srv_poi_info`, and `SrvPoiInfo` (`STRING`→`text`→`String`). Both columns are nullable everywhere.
- I6. The active `gld_srv_poi_info` edges on `PL_VV_TRANS_SLV_TO_GLD_30M` are exactly the five existing sources plus `slv_poi_media_info`, each `RECOMPUTE`, priority 1, `nb_name = NB_GLD_SRV_POI_INFO`, n = 1. They are equal to `SPEC.inputs` values.
- I7. `srvcoverpy` writes nothing on a rerun. It never DROPs, DELETEs, re-enables, or edits an existing edge, and it writes only while it holds the flow lock.
- I8. The gold node reads no gold table. Its existing calls keep `live_only=False` exactly 3 times, and the word `deleted` is not in its code.
- I9. `gld_srv_serve.pg.sql` stays create-only. It must not hold an executable `ALTER`: the Testcontainers init runs this file after it creates the tables, and an ALTER would fail with a duplicate column.

## State ownership

- `lh_vv_gold.dbo.gld_srv_poi_info`: data is owned by `NB_GLD_SRV_POI_INFO` through `run_node`. Schema is owned by `srvcoverpy` on existing environments and by `NB_SETUP_INITIAL_DDL` on new ones.
- `lh_vv_silver.dbo.slv_poi_media_info`: owned by `NB_SLV_POI_MEDIA_INFO` and read-only here. Its producer edges are on `_GLD30`, so producer and consumer use the same cadence (`test_pl_cadence_seed`).
- `ctrl_mng_pipeline_config`: the new row is owned by `srvcoverpy` and the `init_seed_ctrl` seed. `ctrl_mng_watermark` edge state is owned by `run_node`, and the new edge starts with no watermark.
- `apps.srv_poi_info`: the schema file and manual ALTER belong to the user / DBA. The loader is unchanged and outside this task.

## Grain and keys

See `model-design.md` `## Entities and grain` and `## Keys`. The join key is `poi_id` only. The joined side is restricted to `is_cover`, so at most one row per `poi_id` (I3). `(cover_id, poi_id)` is the pk of the matching silver row and gallery row. This is a logical key only, not a physical constraint.

## Ordering

- In the DAG, the new edge makes `slv_poi_media_info` a parent of `gld_srv_poi_info` in the same 30M run. `run_node` reads the parent at its current version, after the media node has finished. Gallery and info therefore see the same media version in one exec, and the cover agrees between the two tables.
- New coupling: if the media node fails or is skipped, the info node is `SKIPPED` ("node cha lỗi / bị bỏ qua"). The other info inputs then wait one cycle too. The critical path becomes media → info instead of the two running in parallel. Both are accepted. They follow from D-01 (read silver), and the DAG offers no ordering without the edge.
- Inside `build`: the `_cover` keys are taken from `rows` after the Google/partner filter and before the rating join. The dup guard therefore only counts emitted `poi_id`s.

## Transaction and commit boundaries

- Gold node: one Delta MERGE per run (`run_node`). The QG and the cover guard run before the MERGE, so a failure writes nothing.
- `srvcoverpy`: at most three commits, `ALTER cover_id`, `ALTER cover_blob_url`, and the edge `INSERT`. Each is atomic on its own; there is no cross-table transaction. All checks run before the first write ("Dừng trước khi ghi"). `_refresh_lock()` runs before each write.
- PostgreSQL: the manual `ALTER TABLE` is a single statement, atomic in PostgreSQL.

## Idempotency

- `srvcoverpy` adds only the columns that are missing (it accepts the full contract or the contract minus any subset of the two new columns), and the `INSERT ... WHERE NOT EXISTS` uses key (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`). A rerun after success changes nothing. A rerun after a partial failure finishes the rest.
- `init_seed_ctrl` / `init_tables` in a new environment, followed by `srvcoverpy`: no-op.
- Gold build: deterministic for pinned inputs, and `row_hash` covers the two new columns (no `hash_exclude`). The first run after rollout updates every row whose hash changed, including rows with null covers. This one-time mass `updated_at` bump is expected.

## Concurrency

- `srvcoverpy` holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` with the same acquire, verify, and refresh steps as `mlsrcpy`, so no 30M run can be inside the node while the ALTER or INSERT happens. Edge `id` = `MAX(id)+seq` follows the existing pattern; a concurrent `ctrl_mng_pipeline_config` writer on another flow would get a Delta conflict and one side fails, so the user reruns it.
- Notebook publish is not covered by the lock. See `## Rollout` for the fail-closed window.

## Retry and recovery

- Gold node failure (guard, QG, ConfigError): no write, and the watermark does not advance. The next 30M run retries the dirty edges. The `p_force_nodes` override is not needed.
- `srvcoverpy` failure: the `finally` block releases the lock with `FAILED` and `error_message`. Rerun the cell.

## Partial failure

| State | Effect | Recovery |
|---|---|---|
| ALTER done, edge INSERT failed | The old notebook still runs: `ensure_target` warns about extra columns, the new columns stay null, and serving is unaffected | Rerun `srvcoverpy` |
| Edge inserted, old notebook still published | `_resolve_node` raises ConfigError "cạnh từ ... không có vai trò", the info node FAILS with no write, and the run ends `PARTIAL_FAILED` | Publish the new notebook; the next run recovers |
| New notebook published, edge missing | ConfigError "vai trò 'media' -> slv_poi_media_info: không có cạnh", no write | Run `srvcoverpy` |
| Media node fails | Info is SKIPPED; gold keeps its last values | Fix media; the next run recovers |
| PG ALTER not run, new service deployed | Hibernate (`ddl-auto: none`) selects `cover_id`, so every `srv_poi_info` query fails | Run the PG ALTER, or roll back the service |

## Observability

- `ctx.metrics.cover_matched` = count of rows with `cover_id IS NOT NULL`, logged in `ctrl_log_table_run` with the existing metrics.
- Guard message: `gld_srv_poi_info: slv_poi_media_info {n} poi_id có hơn một cover`.
- `srvcoverpy` prints `gld_srv_poi_info +[missing]; cạnh [slv_poi_media_info]` and writes `status`/`error_message` on the lock row.
- PLAN mode of `NB_00_ORCHES_SLV_TO_GLD` (`p_mode=PLAN`) shows the new parent edge in the DAG before the first RUN.

## Security

Not applicable: there are no secrets, no new endpoint or DTO, and no auth change. The SQL in `srvcoverpy` uses only cell constants. `blob_url` is already stored and served through `apps.srv_poi_media_gallery`.

## Alternatives

| Option | Verdict | Reason |
|---|---|---|
| A. LEFT JOIN live `slv_poi_media_info` where `is_cover` (selected) | Selected | D-01, same source and filter as gallery, one predicate |
| B. Read `gld_srv_poi_media_gallery` | Rejected | Gold must not read gold (author-input); adds a gold-to-gold DAG level for the same data |
| C. Recompute the cover in info (window over media) | Rejected | Second cover rule, forbidden by D-01 |
| D. `media` in `required_inputs` | Rejected | D-01 wants nulls on no match; the media node already guards empty input |
| E. Edit `srvratepy` `INFO_COLS` | Rejected | That cell was already applied; changing it breaks its rerun contract and `test_info_rating_patch` |
| F. Let `ensure_target` add the columns | Rejected | It appends after `deleted_at`, so it breaks I4 and the contract tests; the edge still needs a ctrl write |
| G. Silent dedupe (pick one cover) | Rejected | Model-design question 2 asks to stop instead of choosing |

The trade-off accepted with A: info freshness now depends on the media node (see `## Ordering`).

## Rollout

The user owns every Fabric and PostgreSQL step. The order keeps every intermediate state fail-closed.

1. Merge the repo changes and run local tests (see `## Verification`).
2. Optional preview: run `NB_00_ORCHES_SLV_TO_GLD` with `p_pl_name=PL_VV_TRANS_SLV_TO_GLD_30M`, `p_mode=PLAN` after step 3. It should show the edge `slv_poi_media_info → gld_srv_poi_info`.
3. On an existing environment, run `NB_CREATE_DDL` cell `srvcoverpy` (only that cell), then publish `NB_GLD_SRV_POI_INFO` right away. Between the two steps a 30M run fails closed (see `## Partial failure` row 2). Pausing the 30M trigger for the window is preferable. A new environment uses `NB_SETUP_INITIAL_DDL` with `p_apply=true`, and `srvcoverpy` is then a no-op.
4. Let one 30M run complete. Check `cover_matched` and run the probes in `## Verification` (runtime).
5. PostgreSQL that already has `apps.srv_poi_info`: `ALTER TABLE apps.srv_poi_info ADD COLUMN cover_id text, ADD COLUMN cover_blob_url text;`. A new database uses the file. PostgreSQL appends the columns at the end; JPA maps by name, and the contract test compares sets.
6. Deploy `data-serving-service` only after step 5.
7. User-owned precondition: confirm the gold → `apps.srv_poi_info` loader maps columns by name. Until it carries the new columns they stay null in PostgreSQL. This is not claimed here.

## Rollback and forward recovery

- Service: redeploy the previous build. It works against PostgreSQL with the extra columns.
- PostgreSQL: the columns are nullable and can stay. To remove them: `ALTER TABLE apps.srv_poi_info DROP COLUMN cover_blob_url, DROP COLUMN cover_id;`, after the service rollback.
- Gold: republish the previous `NB_GLD_SRV_POI_INFO`, then, holding the flow lock, set the edge to `is_active = 0` (keep the row, as `rvi18ngldpy` does). Do not DROP the Delta columns: that needs column mapping, which the tests ban. Their values stay stale because the old build no longer writes them. If stale covers are unacceptable, run `UPDATE lh_vv_gold.dbo.gld_srv_poi_info SET cover_id = NULL, cover_blob_url = NULL` once, under the lock.
- Forward recovery is preferred: fix the build and rerun, because the edge and columns can stay.

## Implementation plan

0. Add the four test files to `scope.files` (Stop 1).
1. `NB_GLD_SRV_POI_INFO` `srvinfobuild`: apply `### Build cell changes`. In `srvinfomd`, append the line `` `cover_id`, `cover_blob_url`: mọi nguồn, left join dòng `is_cover` của `slv_poi_media_info` theo `poi_id` (mapping §1.2). ``
2. `NB_CREATE_DDL`: append a markdown cell `srvcovermd` and a code cell `srvcoverpy` after `cmscfgpy`, using `### srvcovermd` and `### srvcoverpy`. Use JSON keys in the same order as `mlsrcpy` (`cell_type`, `id`, `metadata` with `microsoft.language/language_group` for code, `execution_count: null`, `outputs: []`, `source` as a list of `\n`-terminated lines). Do not mention `_30P` in the new cells.
3. `NB_SETUP_INITIAL_DDL` `init_tables`: in the `lh_vv_gold.dbo.gld_srv_poi_info` spec, insert `('cover_id', 'STRING', None),` and `('cover_blob_url', 'STRING', None),` right after `('review_count', 'INT', None),`.
4. `NB_SETUP_INITIAL_DDL` `init_seed_ctrl`: insert these lines as the last entries of `PIPELINE_CONFIG_ROWS`, after the `slv_3p_poi_rating → gld_srv_poi_review` row:
   `    # [THÊM 08/11] 20261108-gld-srv-poi-info-cover: cạnh cover cho gld_srv_poi_info.`
   `    (_GLD30, _S, 'slv_poi_media_info', _G, 'gld_srv_poi_info', 1, 1, 'RECOMPUTE', None, None, 'NB_GLD_SRV_POI_INFO'),`
5. `gld_srv_serve.pg.sql`: after `    review_count integer,` add `    cover_id text,` and `    cover_blob_url text,`. After header line 16, add:
   `-- DB đã có apps.srv_poi_info trước 20261108-gld-srv-poi-info-cover: chạy tay ALTER TABLE apps.srv_poi_info ADD COLUMN cover_id text, ADD COLUMN cover_blob_url text;`
6. `SrvPoiInfo.java`: after `reviewCount`, add `@Column(name = "cover_id") private String coverId;` and `@Column(name = "cover_blob_url") private String coverBlobUrl;`. Keep the existing two-line field style and a blank line between fields.
7. Mapping doc, see `### Mapping doc edits`.
8. Tests, see `### Test changes`.

### Build cell changes

Constants, after `RATING_COLS = ...`:

```python
COVER_COLS = ("poi_id", "media_id", "blob_url", "is_cover")
```

`OUT_COLS`: the last line becomes `"is_bookable", "operating_hours", "holiday_exceptions", "rating_overall", "rating_count", "review_count", "cover_id", "cover_blob_url")`. Wrap the line under the existing width if needed, but keep this order.

New function after `_reviews`:

```python
def _cover(media, keys):
    # D-01 (task cover): dòng is_cover của slv_poi_media_info, cùng dòng gallery chiếu. Không tính lại cover.
    # Trùng poi_id -> dừng, không chọn dòng.
    c = (media.select(*COVER_COLS).where(F.col("is_cover")).join(keys, "poi_id", "left_semi")
         .select("poi_id", F.col("media_id").alias("cover_id"), F.col("blob_url").alias("cover_blob_url")))
    dup = c.groupBy("poi_id").count().where("count > 1").count()
    if dup:
        raise QualityGateError(f"gld_srv_poi_info: slv_poi_media_info {dup} poi_id có hơn một cover")
    return c
```

In `build`:

```python
    rv = ctx.input("review")
    md = ctx.input("media")
    ...
    _require(rv, ("poi_id",), "slv_3p_poi_review")
    _require(md, COVER_COLS, "slv_poi_media_info")
    ...
    google = rows.where(is_google).select("poi_id")
    cover = _cover(md, rows.select("poi_id"))
    rows = (rows.join(_rating(rt, google), "poi_id", "left").join(_reviews(rv, google), "poi_id", "left")
            .join(cover, "poi_id", "left")
            .withColumn("_h", _hours(F.col("source_name"), F.col("opening_hours_text"))))
```

In `out = rows.select(...)`, right after `F.when(is_google, F.col("review_count")).cast("int").alias("review_count"),` insert `"cover_id", "cover_blob_url",`. Do not wrap them in `F.when(is_google, ...)`: `test_info_rating_build_rules` requires exactly 4.

`ctx.metrics.update(...)`: add `cover_matched=out.where("cover_id IS NOT NULL").count()`.

`SPEC.inputs`: add `"media": "slv_poi_media_info"` after `"review": "slv_3p_poi_review"`. Everything else in `SPEC` is unchanged.

### srvcovermd

```
# [THÊM 08/11] 20261108-gld-srv-poi-info-cover

Thêm `cover_id` STRING, `cover_blob_url` STRING (cho phép NULL) vào `gld_srv_poi_info`, ngay sau `review_count`. Thêm 1 cạnh `PL_VV_TRANS_SLV_TO_GLD_30M`: `slv_poi_media_info` → `gld_srv_poi_info`. Không DROP. Chạy lại không đổi gì.
Sau cell này không chạy lại `srvratepy` (hợp đồng `gld_srv_poi_info` trong cell đó là bản 32 cột).
```

### srvcoverpy

```python
# [THÊM 08/11] 20261108-gld-srv-poi-info-cover (D-01)
# 1. gld_srv_poi_info: thêm cover_id, cover_blob_url STRING cho phép NULL ngay sau review_count. Thiếu cột nào thêm cột đó.
# 2. Thêm cạnh slv_poi_media_info -> gld_srv_poi_info (RECOMPUTE, priority 1, NB_GLD_SRV_POI_INFO). Không bật lại cạnh tắt.
# Lệch hợp đồng, cạnh lạ, slv_poi_media_info sai kiểu hoặc không do luồng này ghi -> dừng trước khi ghi.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M suốt cell. Chạy lại: không ghi.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
INFO_FQ = "lh_vv_gold.dbo.gld_srv_poi_info"
MEDIA_FQ = "lh_vv_silver.dbo.slv_poi_media_info"
MEDIA_SRC = [("media_id", "string", False), ("blob_url", "string", True)]
INFO_NEW_COLS = [("cover_id", "STRING"), ("cover_blob_url", "STRING")]
INFO_COLS = [
    ("poi_id", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
    ("business_sector", "STRING"), ("business_category", "STRING"), ("subcategory_tags", "STRING"),
    ("destination_id", "STRING"), ("full_address", "STRING"), ("street", "STRING"), ("ward", "STRING"),
    ("district", "STRING"), ("city", "STRING"), ("country_code", "STRING"), ("postal_code", "STRING"),
    ("lat", "DOUBLE"), ("lng", "DOUBLE"), ("phone", "STRING"), ("email", "STRING"), ("website_url", "STRING"),
    ("operating_status", "STRING"), ("is_verified", "BOOLEAN"), ("is_recommended", "BOOLEAN"),
    ("is_bookable", "BOOLEAN"), ("operating_hours", "STRING"), ("holiday_exceptions", "STRING"),
    ("rating_overall", "DECIMAL(4,2)"), ("rating_count", "INT"), ("review_count", "INT"),
    ("cover_id", "STRING"), ("cover_blob_url", "STRING"),
    ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
]
EDGES_KEEP = ("slv_poi_entity_non_enrich", "slv_enr_poi_destination", "slv_enr_poi_info_multi_lang",
              "slv_3p_poi_rating", "slv_3p_poi_review")
EDGES_ON = [
    (1, "slv_poi_media_info", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
]
LOCK = "srvcover-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


def _edge_rows(trg_schema, trg):
    return [(r["pl_name"], r["src_schema"], r["src_tbl"], r["is_active"], r["priority"], r["load_mode"],
             r["nb_name"], r["n"]) for r in spark.sql(f"""
    SELECT pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
    FROM {CFG}
    WHERE trg_schema = '{trg_schema}' AND trg_tbl = '{trg}'
    GROUP BY pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name
    """).collect()]


n_lock = spark.sql(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{WID}'").first()["n"]
if n_lock != 1:
    raise RuntimeError(f"{WM} không có đúng 1 dòng {WID}: chạy plcadpy trước")
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
    held = True
    owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
    if not owner or owner["lock_exec_id"] != LOCK:
        held = False
        other = None if owner is None else owner["lock_exec_id"]
        raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")
    if "nb_name" not in {f.name.lower() for f in spark.table(CFG).schema.fields}:
        raise RuntimeError(f"{CFG} chưa có cột nb_name: chạy enrddlpy trước")

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    missing = []
    if not spark.catalog.tableExists(MEDIA_FQ):
        issues.append(f"{MEDIA_FQ} chưa có: chạy mediaddlpy hoặc NB_SETUP_INITIAL_DDL")
    else:
        media = {name: (dtype, nullable) for name, dtype, nullable in _schema(MEDIA_FQ)}
        for name, dtype, nullable in MEDIA_SRC:
            if media.get(name) != (dtype, nullable):
                issues.append(f"{MEDIA_FQ}.{name} là {media.get(name)}, cần {(dtype, nullable)}")
    if not spark.catalog.tableExists(INFO_FQ):
        issues.append(f"{INFO_FQ} chưa có: chạy NB_SETUP_INITIAL_DDL hoặc srvpoipy / srvratepy")
    else:
        got = _schema(INFO_FQ)
        have_cols = {name for name, _dtype, _nullable in got}
        missing = [name for name, _dtype in INFO_NEW_COLS if name not in have_cols]
        want = _want(INFO_COLS)
        if got != [col for col in want if col[0] not in missing]:
            issues.append(f"{INFO_FQ} không khớp hợp đồng, không sửa: có {got}, cần {want}")
    owners = {pl for pl, _ss, _src, flag, *_rest in _edge_rows(SLV, "slv_poi_media_info") if flag == 1}
    if owners != {PL}:
        issues.append(f"slv_poi_media_info phải do đúng {PL} ghi, đang là {sorted(owners)}")
    keep = {(PL, SLV, src, 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_INFO") for src in EDGES_KEEP}
    new = {(PL, SLV, src, 1, priority, mode, nb) for _q, src, _s, _t, mode, nb, priority in EDGES_ON}
    rows = _edge_rows(GLD, "gld_srv_poi_info")
    for pl, src_schema, src, flag, priority, mode, nb, n in rows:
        if pl != PL and flag == 1:
            issues.append(f"cạnh {src}->gld_srv_poi_info đang active ở {pl}")
        if pl == PL and ((pl, src_schema, src, flag, priority, mode, nb) not in keep | new or n != 1):
            issues.append(f"Cell không tự bật / sửa cạnh: {pl} {src_schema}.{src} active={flag} "
                          f"priority={priority} mode={mode} nb={nb} n={n}")
    have_edges = {row[:7] for row in rows}
    if not keep <= have_edges:
        issues.append(f"thiếu cạnh gld_srv_poi_info: {sorted(keep - have_edges)}")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    def _refresh_lock():
        # STATE-001: gia hạn và kiểm lại chủ khoá ngay trước mỗi lần ghi.
        spark.sql(f"""
        UPDATE {WM}
        SET lock_at = current_timestamp(), updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
        owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
        if not owner or owner["lock_exec_id"] != LOCK:
            raise RuntimeError(f"Luồng {PL} mất khoá trước khi ghi")

    names = [name for name, _dtype in INFO_COLS]
    dtypes = dict(INFO_NEW_COLS)
    for name in missing:
        _refresh_lock()
        spark.sql(f"ALTER TABLE {INFO_FQ} ADD COLUMNS (`{name}` {dtypes[name]} AFTER `{names[names.index(name) - 1]}`)")
    values = ",\n    ".join(
        f"({seq}, '{src}', '{schema}', '{trg}', '{mode}', '{nb}', {priority})"
        for seq, src, schema, trg, mode, nb, priority in EDGES_ON
    )
    _refresh_lock()
    spark.sql(f"""
    INSERT INTO {CFG}
        (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)
    SELECT COALESCE((SELECT MAX(id) FROM {CFG}), 0) + t.seq, '{PL}', '{SLV}', t.src_tbl, t.trg_schema, t.trg_tbl,
           1, t.priority, t.load_mode, CAST(NULL AS STRING), CAST(NULL AS STRING), t.nb_name
    FROM VALUES
        {values}
    AS t(seq, src_tbl, trg_schema, trg_tbl, load_mode, nb_name, priority)
    WHERE NOT EXISTS (
        SELECT 1 FROM {CFG} c
        WHERE c.pl_name = '{PL}' AND c.src_schema = '{SLV}' AND c.src_tbl = t.src_tbl
          AND c.trg_schema = t.trg_schema AND c.trg_tbl = t.trg_tbl)
    """)

    # Sau khi ghi: chỉ xét phần cell thêm.
    problems = []
    if _schema(INFO_FQ) != _want(INFO_COLS):
        problems.append(f"{INFO_FQ} lệch cột")
    active = {row[:7]: row[7] for row in _edge_rows(GLD, "gld_srv_poi_info") if row[3] == 1}
    want_active = {payload: 1 for payload in keep | new}
    if active != want_active:
        problems.append(f"cạnh active là {active}, cần {want_active}")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"gld_srv_poi_info +{missing}; cạnh {sorted(src for _q, src, *_r in EDGES_ON)}")
except Exception as exc:
    failed = exc
    raise
finally:
    if held:
        status = "FAILED" if failed else "SUCCESS"
        detail = "" if failed is None else str(failed).replace("'", " ")[:500]
        try:
            spark.sql(f"""
            UPDATE {WM}
            SET lock_exec_id = NULL, lock_at = NULL, status = '{status}', error_message = '{detail}',
                updated_at = current_timestamp()
            WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
            """)
        except Exception as cleanup_exc:
            if failed is None:
                raise
            raise failed from cleanup_exc
```

### Mapping doc edits

§1.1:
- Line `SPEC.inputs`: add `` `media` = `slv_poi_media_info` `` after `review`. Change "`rating` và `review`: notebook không truyền `live_only`" to "`rating`, `review` và `media`: notebook không truyền `live_only` (chỉ dòng `deleted_at IS NULL`)".
- Line 18 (partner with destination ...): add `cover_id`, `cover_blob_url` to the "không đổi" list.
- Line `pl_name` hiện hành: add `slv_poi_media_info` to the edge list (6 edges).
- New bullet after line 23: "`cover_id`, `cover_blob_url` (D-01): LEFT JOIN dòng `slv_poi_media_info` có `is_cover = true` cùng `poi_id`, cùng dòng `gld_srv_poi_media_gallery` chiếu. `is_cover` do `with_cover` của `NB_SLV_POI_MEDIA_INFO` tính; notebook gold không tính lại. Mọi nguồn. Không có dòng cover thì cả hai null, vẫn giữ một dòng `poi_id`. Hơn một dòng cover cho một `poi_id` thì dừng, không chọn dòng. Metric `cover_matched`. Không thuộc `required_inputs`."

§1.2: insert these rows right after the `review_count` row, before `created_at`:
```
| slv_poi_media_info.media_id | string | LEFT JOIN dòng is_cover = true cùng poi_id; không có dòng thì null | cover_id |
| slv_poi_media_info.blob_url | string | cùng dòng cover với cover_id, transform 1-1; không có dòng thì null | cover_blob_url |
```

### Test changes

Append to `tests/test_srv_poi_serving_contract.py`, after `test_no_flyway_in_service`:

```python
COVER = [("cover_id", "STRING"), ("cover_blob_url", "STRING")]
TECH = ("row_hash", "created_at", "updated_at", "deleted_at")
INFO_SOURCES = ("slv_poi_entity_non_enrich", "slv_enr_poi_destination", "slv_enr_poi_info_multi_lang",
                "slv_3p_poi_rating", "slv_3p_poi_review")
COVER_EDGE = (1, "slv_poi_media_info", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1)


def _literal(source: str, name: str):
    node = next(n for n in ast.parse(source).body
                if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == name for t in n.targets))
    return ast.literal_eval(node.value)


def _code(source: str) -> str:
    return "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))


def _info_spec() -> dict:
    tree = ast.parse(_cell_source("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"))
    call = next(n.value for n in ast.walk(tree)
                if isinstance(n, ast.Assign) and any(getattr(t, "id", None) == "SPEC" for t in n.targets))
    return {kw.arg: ast.literal_eval(kw.value) for kw in call.keywords if kw.arg != "build"}


def test_info_cover_patch_cell():
    ids = [cell.get("id") for cell in _notebook("NB_CREATE_DDL.ipynb")["cells"]]
    assert ids[-2:] == ["srvcovermd", "srvcoverpy"]
    patch = _cell_source("NB_CREATE_DDL.ipynb", "srvcoverpy")
    base = _literal(_cell_source("NB_CREATE_DDL.ipynb", "srvratepy"), "INFO_COLS")
    at = [name for name, _dtype in base].index("review_count") + 1
    assert _literal(patch, "INFO_NEW_COLS") == COVER
    assert _literal(patch, "INFO_COLS") == base[:at] + COVER + base[at:]
    assert _literal(patch, "EDGES_ON") == [COVER_EDGE]
    assert _literal(patch, "EDGES_KEEP") == INFO_SOURCES
    assert _literal(patch, "PL") == _literal(_cell_source("NB_CREATE_DDL.ipynb", "plcadpy"), "RENAMES")[1][1]
    order = ["held = True", "Dừng trước khi ghi", "ALTER TABLE", "INSERT INTO {CFG}", "Sau khi ghi", "finally:"]
    assert [patch.index(t) for t in order] == sorted(patch.index(t) for t in order)
    code = _code(patch)
    for token in ("DROP", "DELETE", "TRUNCATE", "UPDATE {CFG}", "REPLACE", "RESTORE", "columnMapping", "_30P"):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and " AFTER " in code
    calls = [m.start() for m in re.finditer(r"(?m)^\s*_refresh_lock\(\)", patch)]
    alter, insert = patch.index("ALTER TABLE"), patch.index("INSERT INTO {CFG}")
    assert len(calls) == 2 and calls[0] < alter < calls[1] < insert
    assert "LEASE_MINUTES = 90" in patch and "lock_exec_id = '{LOCK}'" in patch
    assert "raise failed from cleanup_exc" in patch


def test_info_cover_build_rule():
    source = _cell_source("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    code = _code(source)
    assert _literal(source, "OUT_COLS")[-3:] == ("review_count", "cover_id", "cover_blob_url")
    assert _literal(source, "COVER_COLS") == ("poi_id", "media_id", "blob_url", "is_cover")
    assert 'md = ctx.input("media")' in code
    assert '.where(F.col("is_cover"))' in code
    assert 'F.col("media_id").alias("cover_id")' in code
    assert 'F.col("blob_url").alias("cover_blob_url")' in code
    assert 'join(cover, "poi_id", "left")' in code
    assert "có hơn một cover" in code
    for token in ("with_cover", "row_number", "is_active", "lh_vv_gold", "deleted"):
        assert token not in code
    spec = _info_spec()
    assert spec["pk"] == ("poi_id",) and spec["write_mode"] == "MERGE"
    assert spec["required_inputs"] == ("entity",)
    assert spec["inputs"]["media"] == "slv_poi_media_info"
    assert tuple(v for k, v in spec["inputs"].items() if k != "media") == INFO_SOURCES


def test_info_cover_seed_and_init_ddl():
    seed: dict = {}
    exec(_cell_source("NB_SETUP_INITIAL_DDL.ipynb", "init_seed_ctrl"), seed)  # noqa: S102
    rows = [r for r in seed["PIPELINE_CONFIG_ROWS"] if r[4] == "gld_srv_poi_info"]
    assert seed["PIPELINE_CONFIG_ROWS"][-1] == (
        seed["_GLD30"], seed["_S"], "slv_poi_media_info", seed["_G"], "gld_srv_poi_info",
        1, 1, "RECOMPUTE", None, None, "NB_GLD_SRV_POI_INFO")
    assert sorted(r[2] for r in rows if r[5] == 1) == sorted(_info_spec()["inputs"].values())
    assert {r[0] for r in rows} == {"PL_VV_TRANS_SLV_TO_GLD_30M"}
    init: dict = {}
    exec(_cell_source("NB_SETUP_INITIAL_DDL.ipynb", "init_tables"), init)  # noqa: S102
    spec = next(s for s in init["TABLE_SPECS"] if s["fq"] == "lh_vv_gold.dbo.gld_srv_poi_info")
    patch = _cell_source("NB_CREATE_DDL.ipynb", "srvcoverpy")
    assert [(c[0], c[1]) for c in spec["cols"]] == _literal(patch, "INFO_COLS")
    out = _literal(_cell_source("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"), "OUT_COLS")
    assert list(out) + list(TECH) == [c[0] for c in spec["cols"]]


def test_info_cover_mapping_and_pg_ddl():
    text = (ROOT / "docs" / "context" / "mapping_gld_srv_poi_info.md").read_text(encoding="utf-8")
    table = text.split("### 1.2. Field Mapping", 1)[1].split("### 1.3", 1)[0]
    rows = {line.split("|")[4].strip(): line for line in table.splitlines() if line.startswith("|")}
    assert "slv_poi_media_info.media_id" in rows["cover_id"] and "is_cover" in rows["cover_id"]
    assert "slv_poi_media_info.blob_url" in rows["cover_blob_url"]
    handling = text.split("### 1.1. Xử lý", 1)[1].split("### 1.2", 1)[0]
    assert "`media` = `slv_poi_media_info`" in handling and "cover_matched" in handling
    pg = PG_DDL.read_text(encoding="utf-8")
    body = re.search(r"CREATE TABLE apps\.srv_poi_info \((.*?)\n\);", pg, re.S).group(1)
    assert "    review_count integer,\n    cover_id text,\n    cover_blob_url text,\n" in body
    assert not re.search(r"(?m)^\s*ALTER\s", pg)
```

Pinned updates outside the original scope (after Stop 1):
- `tests/test_gld_srv_poi_contract.py`
  - `test_node_specs`: `expected["srvinfobuild"]["inputs"]` gains `"media": "slv_poi_media_info"` after `"review"`.
  - `test_build_columns_match_ddl`: `gold[INFO_FQ] = _assign(_cell("NB_CREATE_DDL.ipynb", "srvcoverpy"), "INFO_COLS")`.
  - `test_info_rating_patch`: shift every slice by 2. `ids[-24:-16]` is the 8-id list, `ids[-16:-14]` plcad, `ids[-14:-12]` mlexp, `ids[-12:-10]` srvrev, `ids[-10:-6]` rvi18n, `ids[-6:-4]` mlsrc, `ids[-4:-2]` cmscfg. Add `ids[-2:] == ["srvcovermd", "srvcoverpy"]`. All other assertions stay the same.
  - `test_review_source_patch_cell` (end of the function): `ids[-10:-6]` rvi18n, `ids[-6:-4]` mlsrc, `ids[-4:-2]` cmscfg. Add `ids[-2:]` srvcover.
- `tests/test_initial_ddl_contract.py`
  - `test_table_specs...` (the line `gold["lh_vv_gold.dbo.gld_srv_poi_info"] = _assign(_cell(ddl, "srvratepy"), "INFO_COLS")`): `srvratepy` → `srvcoverpy`.
  - `test_gld_srv_patch_create_matches_init`: the `contracts["lh_vv_gold.dbo.gld_srv_poi_info"]` source `srvratepy` → `srvcoverpy`.
  - `test_pipeline_config_rows_match_sources`: after the `srvrevpy` loop, add `for seq, src, schema, target, mode, notebook, priority in _assign(_cell(ddl, "srvcoverpy"), "EDGES_ON"): expected.append((gld, silver, src, schema, target, 1, priority, mode, None, None, notebook)); assert seq > 0`. Change `len(expected) == 73` → `74`.
  - `test_pl_cadence_patch_cell`: `[-14:-12]` → `[-16:-14]`.
- `tests/test_enr_poi_contract.py` (lines 223–234) and `tests/test_poi_entity_contract.py` (lines 635–646): shift every negative slice by 2 (`[-32:-26]`→`[-34:-28]`, ..., `[-2:]` cmscfg → `[-4:-2]`). Add `ids[-2:] == ["srvcovermd", "srvcoverpy"]`.

## Verification

Local (Main):
- `python -m pytest tests/test_srv_poi_serving_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_poi_media_amenity_contract.py -q`
- `python -m pytest tests -q` (full suite, none of it regressed).
- `services/data-serving-service/mvnw -f services/data-serving-service/pom.xml -q -DskipTests compile` (Windows: `mvnw.cmd`). The Testcontainers tests (`DataServingApplicationTests`, `PoiRepositoryIntegrationTest`) need Docker; the user runs them, and they are not claimed here.

Runtime probes (user, Fabric SQL, after the first 30M RUN). These are not claimed by this task:
- `SELECT count(*), count(DISTINCT poi_id) FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL`: the two counts are equal.
- `SELECT count(*) FROM lh_vv_gold.dbo.gld_srv_poi_info i LEFT JOIN lh_vv_gold.dbo.gld_srv_poi_media_gallery g ON g.poi_id = i.poi_id AND g.is_cover AND g.deleted_at IS NULL WHERE i.deleted_at IS NULL AND NOT (i.cover_id <=> g.media_id AND i.cover_blob_url <=> g.blob_url)`: the result is 0.
- `cover_matched` in `ctrl_log_table_run` for node `gld_srv_poi_info` equals the count of non-null `cover_id`.
