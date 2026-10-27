RESULT: PASS

## Main brief

### Decision
RESULT: PASS. G1 and G2 from round 1 are closed (model rerun, D-02).
New blocker: the patch cell must go at the end of `NB_CREATE_DDL`, and that breaks negative-index cell-order asserts in 3 test files outside `scope.files`. The user must approve adding them before the `NB_CREATE_DDL` edit.
Build: enrich INNER JOIN `slv_3p_poi_review` on `review_id`, LEFT JOIN rating on the enrich `poi_id`. No casts: `rating` decimal(4,2) (D-02), `rating_count` bigint (D-01). A duplicate rating `poi_id` raises `QualityGateError`.

### Invariants Main must preserve
- Live gold has one row per `review_id`. Lib `pk_null` and `pk_duplicate` stop the run before any write. No row is picked.
- Rows exist only for enrich ∩ `slv_3p_poi_review`. Rating attaches by LEFT JOIN on the enrich `poi_id`.
- A non-null `poi_id` with more than one row in `slv_3p_poi_rating` raises `QualityGateError` before any write.
- `rating` and `rating_overall` are `decimal(4,2)` and `rating_count` is `bigint`, with no `.cast(` in the build. A different source type raises `ConfigError`.
- One gold column list in the same order: `OUT_COLS`+TECH = Setup spec = `srvrevpy` `TABLE_COLS` (see `### Gold contract`).
- Silver order is `review_id, poi_id, lang, title, review_text, created_at, updated_at` in both DDL notebooks.
- Exactly 3 edges, all GLD_30M / RECOMPUTE / priority 1 / `NB_GLD_SRV_POI_REVIEW`, and none in another PL.
- No `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `UPDATE {CFG}`, `RESTORE` or `columnMapping` in `srvrevpy` code. A second run writes nothing.
- `srvrevpy` holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M`. Exactly 3 line-start `_refresh_lock()` calls, one right before each write.
- The `slv_poi_entity_non_enrich` spec stays last in `TABLE_SPECS`. `NB_ENR_POI_REVIEW` and `enrflagpy` are unchanged.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_GLD_SRV_POI_REVIEW.ipynb | new cells `srvrvmd`, `srvrvparam`, `srvrvrun`, `srvrvbuild`, `srvrvres`, `srvrvexit` | Layout of `NB_GLD_SRV_POI_INFO` without the hours cell. Build and SPEC per `### Node build sketch`. | DEV DRY_RUN QG blocks are 0 |
| 2 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, spec `slv_enr_poi_review_multi_lang` | Add `('lang','STRING',None), ('title','STRING',None)` after `poi_id` | equals `srvrevpy` `TABLE_COLS[ML_FQ]` |
| 3 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, after `gld_srv_poi_amenity`, before the `# [SỬA 20/10]` entity spec | New spec `lh_vv_gold.dbo.gld_srv_poi_review` per `### Gold contract`, `PROPS`, no partition | `create_sql(spec) == _create_sql(...)` |
| 4 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_plan` | `len(fqs) != 21` → `22`; `cần 21 fq` → `cần 22 fq` | inventory test passes |
| 5 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl`, end of `PIPELINE_CONFIG_ROWS` | Comment `# [THÊM 27/10] 20261026-gld-srv-poi-review: 3 cạnh gold serving review.` plus 3 `_GLD30` rows in `EDGES_ON` order | seed equals expected, 69 rows |
| 6 | notebooks/NB_CREATE_DDL.ipynb | new markdown `srvrevmd`, at the end | `# [THÊM 27/10] 20261026-gld-srv-poi-review` plus one line (see `## Implementation plan` item 3) | cell is at `ids[-2]` |
| 7 | notebooks/NB_CREATE_DDL.ipynb | new code `srvrevpy`, at the end | Per `### Patch cell design`: literal constants, lock, pre-checks, ALTER loop `AFTER` anchor, `_create_sql`, `FROM VALUES` INSERT `WHERE NOT EXISTS`, post-checks, `finally` | guard test passes; second DEV run adds nothing |
| 8 | tests/test_initial_ddl_contract.py | `test_table_inventory_matches_sources` | Add the `srvrevpy` `TABLE_COLS` keys; `21` → `22` | pass |
| 9 | tests/test_initial_ddl_contract.py | `test_columns_match_sources` | Override landing cols with `srvrevpy` `TABLE_COLS`; add the gold fq | pass |
| 10 | tests/test_initial_ddl_contract.py | `test_pipeline_config_rows_match_sources` | Loop `srvrevpy` `EDGES_ON` with gld after `amenddlpy`; `66` → `69` | pass |
| 11 | tests/test_initial_ddl_contract.py | `test_flag_patch_create_matches_init` | `if fq in rev: cols = rev[fq]` | pass |
| 12 | tests/test_initial_ddl_contract.py | `test_pl_cadence_patch_cell` | `[-4:-2]` → `[-6:-4]` | pass |
| 13 | tests/test_initial_ddl_contract.py | new `test_gld_srv_review_patch_create_matches_init`, `test_gld_srv_review_patch_guards` | Per `### Test changes` | pass |
| 14 | tests/test_gld_srv_poi_contract.py (after scope extension) | `test_info_rating_patch`; new `test_review_node_spec`, `test_review_build_columns_match_ddl`, `test_review_mapping_targets` | Shift slices by −2 and add `ids[-2:] == ["srvrevmd","srvrevpy"]`; node tests per `### Test changes` | pass |
| 15 | tests/test_enr_poi_contract.py (after scope extension) | cell-order block, lines 236–244 | Shift every slice by −2; add `ids[-2:]` | pass |
| 16 | tests/test_poi_entity_contract.py (after scope extension) | cell-order block, lines 627–635 | Same as row 15 | pass |

### Order and stop points
1. STOP (user decision): add `tests/test_gld_srv_poi_contract.py`, `tests/test_enr_poi_contract.py` and `tests/test_poi_entity_contract.py` to `scope.files`. Without them, rows 6–7 fail the suite and the task cannot meet the request. Recommendation: approve.
2. Rows 2–5 (Setup).
3. Rows 6–7 (Create patch).
4. Rows 8–16 (tests).
5. Row 1 (node).
6. Run the local tests, then `run-gate`.
7. STOP (evidence, Fabric DEV): probes P1–P4 (`## Verification`). P4 must show by-name writes before `srvrevpy` runs.
8. Run `srvrevpy` twice. Node DRY_RUN, RUN, then a second RUN with no commit. Then the SQL checks.

### Tests and verification
- `python -m pytest tests/test_initial_ddl_contract.py -q` (new: `test_gld_srv_review_patch_create_matches_init`, `test_gld_srv_review_patch_guards`; changed: `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_pipeline_config_rows_match_sources`, `test_flag_patch_create_matches_init`, `test_pl_cadence_patch_cell`)
- `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q` (new: `test_review_node_spec`, `test_review_build_columns_match_ddl`, `test_review_mapping_targets`)
- `python -m pytest tests -q`
- `python scripts/vv.py run-gate 20261026-gld-srv-poi-review`
- DEV after RUN:
  - live `count(*) = count(DISTINCT review_id)`;
  - the left anti join of gold to `slv_3p_poi_review` returns 0 rows;
  - `DESCRIBE` shows `rating decimal(4,2)` and `rating_count bigint`.

### Read only if needed
- `## Scope gap` → stop 1, rows 12, 14–16
- `## Invariants`, `## Grain and keys`, `### Gold contract` → rows 2, 3, 7, 9
- `### Node build sketch` → row 1
- `### Patch cell design`, `## Idempotency`, `## Concurrency`, `## Partial failure` → row 7
- `### Test changes` → rows 8–16
- `## Alternatives` → rows 1, 7
- `## Verification`, `## Rollout` → stops 7–8

# Architecture: 20261026-gld-srv-poi-review

This is architecture round 2. It replaces the round 1 design (EVIDENCE_REQUIRED). The two gaps from round 1 are closed:
- G1 is closed. `model-design.md` `## Columns` now lists `row_hash STRING` and `deleted_at TIMESTAMP` as lib technical columns.
- G2 is closed. D-02 (`decision.md`, 2026-10-27) sets gold `rating` to `DECIMAL(4,2)`. Transform 1-1, no cast.

Round 2 found one new item: a scope gap. It is a user decision, not missing evidence, so the verdict is PASS with a mandatory stop before the `NB_CREATE_DDL` edit. See `## Scope gap`.

## Scope gap

The request says the Create patch goes at the end of `NB_CREATE_DDL`. Four test files check the last cell ids of that notebook using negative slices. Appending `srvrevmd` and `srvrevpy` shifts every slice by 2, so all four tests fail:

| file | anchor | in `scope.files` |
|---|---|---|
| `tests/test_initial_ddl_contract.py` | `test_pl_cadence_patch_cell`: `[-4:-2] == ["plcadmd", "plcadpy"]` | yes |
| `tests/test_gld_srv_poi_contract.py` | `test_info_rating_patch`: `ids[-12:-4]`, `ids[-4:-2]`, `ids[-2:]` | no |
| `tests/test_enr_poi_contract.py` | the cell-order block at lines 236–244 (`ids[-22:-16]` … `ids[-2:]`) | no |
| `tests/test_poi_entity_contract.py` | the cell-order block at lines 627–635 (same slices) | no |

There is no in-scope workaround. Putting the cell anywhere other than the end breaks the request, and leaving the tests alone makes `pytest tests` fail.

The fix is mechanical: shift each slice by −2 and add `ids[-2:] == ["srvrevmd", "srvrevpy"]`.

Decision needed: add the three files to `scope.files`. `tests/test_gld_srv_poi_contract.py` is also where the node-level tests belong (the round 1 "Scope gap" item), so adding it closes both gaps. If the user declines, stop: the task cannot meet "Create adds a patch cell at the end" with a green suite.

## Scope

- New node notebook `NB_GLD_SRV_POI_REVIEW`. It writes only `lh_vv_gold.dbo.gld_srv_poi_review`, through `run_node`.
- `NB_SETUP_INITIAL_DDL`, edited in place:
  - `init_tables`: two silver columns, one gold spec.
  - `init_seed_ctrl`: three edges.
  - `init_plan`: spec count 21 → 22.
- `NB_CREATE_DDL`: markdown `srvrevmd` and code `srvrevpy`, appended at the end.
- `tests/test_initial_ddl_contract.py`: updated contract and new guard tests.
- After the scope extension: the cell-order slices in three test files, plus node tests in `tests/test_gld_srv_poi_contract.py`.

## Non-goals

- `NB_ENR_POI_REVIEW` logic.
- A loader for `lang` / `title`.
- Schema `lh_vv_gold.enr`.
- `PL_VV_TRANS_SLV_TO_ENR_15M` edges.
- Pipeline JSON.
- `notebooks_lgc/`.
- A mapping-doc edit. D-01 and D-02 are the record (model Conflicts 2).
- Changes to `enrflagpy` `LANDING_COLS`. That cell keeps the old contract, as it does after `mlexppy`.

## Invariants

1. Live gold has one row per `review_id`. Lib QG `pk_null` and `pk_duplicate` stop the run before any write. No survivor row is picked.
2. A row reaches gold only when its `review_id` is in both `slv_enr_poi_review_multi_lang` and `slv_3p_poi_review` (INNER JOIN).
3. Rating attaches by LEFT JOIN on the enrich `poi_id`. If any non-null `poi_id` has more than one row in `slv_3p_poi_rating`, the build raises `QualityGateError` and writes nothing.
4. Types are 1-1 with no cast:
   - `rating` is `decimal(4,2)` (D-02).
   - `rating_overall` is `decimal(4,2)`.
   - `rating_count` is `bigint` (D-01).
   If a source type differs, the build raises `ConfigError`, so `ensure_target` never sees a type mismatch.
5. The gold column list and order are the same in four places: build `OUT_COLS` + `TECH_COLUMNS`, the Setup `TABLE_SPECS` entry, `srvrevpy` `TABLE_COLS`, and what `ensure_target` would build. The first RUN therefore issues no `ALTER`.
6. The silver order is `review_id, poi_id, lang, title, review_text, created_at, updated_at`, the same in Setup and `srvrevpy`.
7. There are exactly three edges `(PL_VV_TRANS_SLV_TO_GLD_30M, lh_vv_silver.dbo, src, lh_vv_gold.dbo, gld_srv_poi_review, 1, 1, RECOMPUTE, NULL, NULL, NB_GLD_SRV_POI_REVIEW)`, for `src` in `slv_enr_poi_review_multi_lang`, `slv_3p_poi_review`, `slv_3p_poi_rating`. No other pipeline has one.
8. `srvrevpy` has no `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `UPDATE {CFG}`, `RESTORE` or `columnMapping` outside comments. A second run writes nothing.
9. `srvrevpy` holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` and calls `_refresh_lock()` right before each write.
10. The `slv_poi_entity_non_enrich` spec stays last in `TABLE_SPECS`, because `test_poi_entity_columns_derived` reads `specs[-1]`.

## State ownership

- `gld_srv_poi_review`: the `NB_GLD_SRV_POI_REVIEW` node in `PL_VV_TRANS_SLV_TO_GLD_30M` is its only writer.
- `slv_enr_poi_review_multi_lang`: the external enrich landing owns the data. This task changes only the schema, through `srvrevpy`. `NB_ENR_POI_REVIEW` reads only `review_id` from it. The new node reads five columns.
- `slv_3p_poi_review` and `slv_3p_poi_rating`: the FL_00 extract owns them. They are read-only here.
- `ctrl_mng_pipeline_config` edges: Setup and `srvrevpy` write them. NB_00 creates the flow-lock and edge watermark rows at runtime. This task seeds no watermark, as with `mediaddlpy` and `srvratepy`.

## Grain and keys

- Grain and key are as in `model-design.md` `## Entities and grain` and `## Keys`: `NodeSpec.pk = ("review_id",)`.
- Join keys are as in `model-design.md` `## Keys` (logical foreign keys) and `## Lineage`.
- Columns, types and order are as in `model-design.md` `## Columns`. They are restated as a literal in `### Gold contract` only because Main copies them verbatim.
- Model Conflicts 4 (enrich may hold several rows per `review_id`) is covered by invariant 1. Probe P1 tells whether the first DEV RUN will stop.
- Model Conflicts 5 (which `poi_id` to use) is kept as the enrich `poi_id`, with the warn metric `review_poi_id_mismatch`.

### Gold contract

`srvrevpy` `TABLE_COLS` uses the same list without the third tuple element.

```
('review_id', 'STRING NOT NULL', None), ('poi_id', 'STRING', None), ('lang', 'STRING', None),
('rating_overall', 'DECIMAL(4,2)', None), ('rating_count', 'BIGINT', None), ('title', 'STRING', None),
('review_text', 'STRING', None), ('rating', 'DECIMAL(4,2)', None),
('review_date', 'STRING', None), ('author_name', 'STRING', None),
('row_hash', 'STRING', None), ('created_at', 'TIMESTAMP', None), ('updated_at', 'TIMESTAMP', None),
('deleted_at', 'TIMESTAMP', None)
```

Silver `slv_enr_poi_review_multi_lang`: insert `('lang', 'STRING', None), ('title', 'STRING', None)` right after `('poi_id', 'STRING', None)`.

## Ordering

- The node is a root of the GLD_30M DAG. None of its three sources is a node target in GLD_30M, so it runs at priority 1 alongside the other roots.
- Within a deployment, `srvrevpy` must run before the first node RUN. If it has not, `_require` on `lang` / `title` raises `ConfigError`, and the hint names `srvrevpy`.
- Inside `srvrevpy`: lock, pre-checks, silver ALTERs, gold CREATE, edge INSERT, post-checks, release. The edges go last, so NB_00 cannot schedule the node before the gold table exists.

## Transaction and commit boundaries

- Node: one Delta MERGE commit on gold, made by the lib. The lib skips the MERGE when the diff is 0. Every stop (`ConfigError` or `QualityGateError` in `build`, and the lib QG) happens before the MERGE.
- `srvrevpy`: each step is its own Delta commit:
  - up to two `ALTER TABLE … ADD COLUMNS`, one column each;
  - one `CREATE TABLE IF NOT EXISTS`;
  - one `INSERT INTO {CFG} … WHERE NOT EXISTS`.
- Delta has no cross-table transaction. Recovery relies on idempotency, not rollback.

## Idempotency

- Node: MERGE by `row_hash`. A rerun on the same pinned inputs inserts, updates and soft-deletes 0 rows and makes no commit.
- `srvrevpy`:
  - Silver: the accepted live states are `want`, `want` without `title`, and `want` without `lang, title`. `add` is the missing names, in `NEW_COLS` order. Any other state goes into `issues`.
  - Gold: if absent, CREATE. If present, its schema must equal `_want(TABLE_COLS[REVIEW_FQ])`.
  - Edges: `INSERT … FROM VALUES … WHERE NOT EXISTS` on `(pl_name, src_schema, src_tbl, trg_schema, trg_tbl)`.
  - Post-checks: both schemas equal `want`, and the active `PL` edges equal `EDGES_ON` with `n = 1`.

## Concurrency

- `srvrevpy` takes the GLD_30M flow lock with the `mlexppy` pattern: lease update, owner check, `held = True`, and `_refresh_lock()` before each write. While edges and schemas change, NB_00 GLD_30M cannot run the new node or `NB_GLD_SRV_POI_INFO`.
- ENR_15M is not locked:
  - `ADD COLUMNS` is a non-data op, so it does not wake ENR nodes.
  - `NB_ENR_POI_REVIEW` selects only `review_id`.
  - Reads pinned to a version are isolated.
- A concurrent external landing write can conflict with an `ALTER` (`MetadataChangedException`). One side fails. Rerunning the cell finishes the work.
- Temp views are unique per node through the lib `_v_{trg_tbl}_{tag}`.

## Retry and recovery

- Node: the lib `with_retry` wraps the MERGE. A failure writes a `FAILED` row to `ctrl_log_table_run` and raises. The next tick retries from new pinned versions.
- `srvrevpy`: the `finally` block releases the lock with `FAILED` and `error_message`. Fix the cause and rerun. The idempotency checks detect partial progress and finish it.

## Partial failure

| failure point | state | recovery |
|---|---|---|
| after `ALTER lang`, before `ALTER title` | silver has `lang` only | rerun: `add = [title]` |
| after the silver ALTERs, before CREATE | no gold table, no edges | rerun: CREATE, then INSERT |
| after CREATE, before INSERT | empty gold table, no edges, node not scheduled | rerun: INSERT |
| the external landing writer uses positional SQL INSERT | its write fails on the column count | the writer changes to by-name writes. P4 checks this before `srvrevpy` runs. |
| build stops on a duplicate (rating `poi_id` or review `review_id`) | no gold commit | fix the source, then the next tick |
| enrich or review input is empty | `required_inputs` gives `FAILED`; no mass soft-delete | reload the source |

## Observability

- `ctrl_log_table_run.qg_json` holds:
  - the lib blocks `pk_null` and `pk_duplicate`;
  - warns `enrich_without_review` (enrich ids dropped by the INNER JOIN) and `review_poi_id_mismatch` (enrich `poi_id` not null-safe equal to `slv_3p_poi_review.poi_id`);
  - metric `rating_matched`.
- Stop messages start with `gld_srv_poi_review:` and name the source and the count, for example `slv_3p_poi_rating {n} poi_id có hơn một dòng`.
- `srvrevpy` prints the columns it added, whether it created gold, and the active edges.

## Security

Not applicable: no new identity, secret or endpoint. Reads and writes stay in the existing lakehouses under the workspace identity.

## Rollout

1. The user approves the scope extension (`## Scope gap`).
2. Merge the code.
3. DEV probes P1–P4 (`## Verification`).
4. Run `srvrevpy`, then run it again. The second run adds nothing.
5. Run the node with `p_mode=DRY_RUN`, then `RUN`, then `RUN` again (no commit).
6. Wait for one NB_00 GLD_30M tick.
7. Fresh environments get the same state from `NB_SETUP_INITIAL_DDL`.

## Rollback and forward recovery

- Rollback is forward only, because `DROP` is not allowed. To stop scheduling, a later task sets the three edges to `is_active = 0`. The gold table stays. Readers filter `deleted_at IS NULL`.
- The nullable silver columns stay. Existing readers select by name.
- A wrong gold type cannot be changed in place. Invariant 4 stops the run before any write, so this cannot happen silently.

## Alternatives

| choice | selected | rejected, and why |
|---|---|---|
| Rating duplicate scope | All non-null `poi_id`s in the rating input (the request text) | Joined keys only (`_rating` in `NB_GLD_SRV_POI_INFO`): narrower than "more than one row for one `poi_id`, stop". The lib `pk_duplicate` already catches joined duplicates. Switch only by ledger decision. |
| Source type check | Explicit `ConfigError` for `rating`, `rating_overall`, `rating_count` | Relying on `ensure_target`: it raises too, but only after build, and it names the target, not the source. |
| Review grain enforcement | Lib `pk_duplicate` | A pre-check in `build`: same stop, duplicated logic. |
| Silver column position | `AFTER poi_id`, then `AFTER lang`, two ALTERs (`mlexppy` precedent) | Appending after `updated_at` puts business columns after system columns. One ALTER with chained `AFTER`: resolution order not proven in this repo. |
| Cell placement | At the end, with the test slices updated | Before `plcadmd`: breaks the request rule, and the tests too. |
| Flow lock | GLD_30M only | Also locking ENR_15M: not needed for a metadata change, and it doubles the deadlock surface. |

## Implementation plan

1. `NB_GLD_SRV_POI_REVIEW`: copy the cell layout and parameters of `NB_GLD_SRV_POI_INFO`, without the hours cell. Cell ids:
   - `srvrvmd`: title, grain, joins;
   - `srvrvparam`: the same eight parameters;
   - `srvrvrun`: `%run NB_LIB_TRANSFORM_SLV_GLD`;
   - `srvrvbuild`: `### Node build sketch`;
   - `srvrvres`: `RES = run_node(SPEC, …)`, the same line;
   - `srvrvexit`: `notebookutils.notebook.exit(finish_node(RES))`.
2. `NB_SETUP_INITIAL_DDL`:
   - `init_tables`: in the `slv_enr_poi_review_multi_lang` spec, add `lang` and `title` after `poi_id`. Add the gold spec (`### Gold contract`, `PROPS`, partition `None`, comment `None`) right after `gld_srv_poi_amenity` and before the `# [SỬA 20/10]` entity spec.
   - `init_plan`: `len(fqs) != 21` → `22`, and `cần 21 fq` → `cần 22 fq`.
   - `init_seed_ctrl`: after the `_GLD1H` amenity row, add `# [THÊM 27/10] 20261026-gld-srv-poi-review: 3 cạnh gold serving review.` and three rows `(_GLD30, _S, src, _G, 'gld_srv_poi_review', 1, 1, 'RECOMPUTE', None, None, 'NB_GLD_SRV_POI_REVIEW')`, in `EDGES_ON` order.
3. `NB_CREATE_DDL`: append `srvrevmd` with `# [THÊM 27/10] 20261026-gld-srv-poi-review` and one line: "Thêm `lang`, `title` vào `slv_enr_poi_review_multi_lang`; tạo `gld_srv_poi_review`; 3 cạnh GLD_30M. Chạy lại không đổi gì." Then append `srvrevpy` (`### Patch cell design`).
4. `tests/test_initial_ddl_contract.py`: `### Test changes`.
5. After the scope extension, update the three out-of-scope tests (`### Test changes`).

### Node build sketch

```python
ML_COLS = ("review_id", "poi_id", "lang", "title", "review_text")
REVIEW_COLS = ("review_id", "poi_id", "rating", "time", "author_name")
RATING_COLS = ("poi_id", "rating_overall", "rating_count")
SOURCE_TYPES = {
    "slv_3p_poi_review": {"rating": "decimal(4,2)"},                                      # D-02
    "slv_3p_poi_rating": {"rating_overall": "decimal(4,2)", "rating_count": "bigint"},  # D-01
}
# Thứ tự mapping §2.
OUT_COLS = ("review_id", "poi_id", "lang", "rating_overall", "rating_count", "title", "review_text",
            "rating", "review_date", "author_name")


def _require(df, cols, name, hint=""):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ConfigError(f"gld_srv_poi_review: {name} thiếu {missing}{hint}")


def _types(df, name):
    got = dict(df.dtypes)
    bad = {c: got[c] for c, t in SOURCE_TYPES[name].items() if got[c] != t}
    if bad:
        raise ConfigError(f"gld_srv_poi_review: {name} sai kiểu {bad}, cần {SOURCE_TYPES[name]}")


def build(ctx):
    ml = ctx.input("multi_lang", live_only=False)
    rv = ctx.input("review")
    rt = ctx.input("rating")
    _require(ml, ML_COLS, "slv_enr_poi_review_multi_lang", ": chạy srvrevpy của NB_CREATE_DDL")
    _require(rv, REVIEW_COLS, "slv_3p_poi_review")
    _require(rt, RATING_COLS, "slv_3p_poi_rating")
    _types(rv, "slv_3p_poi_review")
    _types(rt, "slv_3p_poi_rating")
    # Một dòng mỗi poi_id. Trùng poi_id -> dừng, không chọn dòng.
    rt = rt.select(*RATING_COLS)
    dup = rt.where(F.col("poi_id").isNotNull()).groupBy("poi_id").count().where("count > 1").count()
    if dup:
        raise QualityGateError(f"gld_srv_poi_review: slv_3p_poi_rating {dup} poi_id có hơn một dòng")
    review = rv.select("review_id", F.col("poi_id").alias("_rv_poi"), "rating",
                       F.col("time").alias("review_date"), "author_name")
    ml = ml.select(*ML_COLS)
    ctx.warn("enrich_without_review", ml.join(review, "review_id", "left_anti").count())
    rows = (ml.join(review, "review_id", "inner")
              .join(rt.withColumn("_rated", F.lit(True)), "poi_id", "left"))
    ctx.warn("review_poi_id_mismatch", rows.where(~F.col("poi_id").eqNullSafe(F.col("_rv_poi"))).count())
    ctx.metrics.update(rating_matched=rows.where("_rated IS NOT NULL").count())
    return rows.select(*OUT_COLS)


SPEC = NodeSpec(
    trg_tbl="gld_srv_poi_review",
    inputs={"multi_lang": "slv_enr_poi_review_multi_lang", "review": "slv_3p_poi_review",
            "rating": "slv_3p_poi_rating"},
    pk=("review_id",),
    build=build,
    required_inputs=("multi_lang", "review"),
    write_mode="MERGE",
)
```

No literal `lh_vv_gold` and no `deleted` appears in the build code. That matches the `test_node_specs` style.

### Patch cell design

`srvrevpy` follows `mlexppy` for the lock, `_want`, `_schema` and `_edge_rows`, and `mediaddlpy` / `amenddlpy` for `_create_sql` and the `FROM VALUES` edge INSERT. Header comments:
- what the cell adds;
- the accepted states;
- "Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M suốt cell";
- "Sau cell này không chạy lại enrflagpy: hợp đồng slv_enr_poi_review_multi_lang trong đó là bản cũ."

All constants are literals, so `ast.literal_eval` can read them:

```python
CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'"
ML_FQ = "lh_vv_silver.dbo.slv_enr_poi_review_multi_lang"
REVIEW_FQ = "lh_vv_gold.dbo.gld_srv_poi_review"
NEW_COLS = [("lang", "STRING"), ("title", "STRING")]
TABLE_COLS = {
    "lh_vv_silver.dbo.slv_enr_poi_review_multi_lang": [<silver list, 7 pairs>],
    "lh_vv_gold.dbo.gld_srv_poi_review": [<gold list, 14 pairs>],
}
SOURCES = ("lh_vv_silver.dbo.slv_3p_poi_review", "lh_vv_silver.dbo.slv_3p_poi_rating")
EDGES_ON = [
    (1, "slv_enr_poi_review_multi_lang", "lh_vv_gold.dbo", "gld_srv_poi_review", "RECOMPUTE", "NB_GLD_SRV_POI_REVIEW", 1),
    (2, "slv_3p_poi_review", "lh_vv_gold.dbo", "gld_srv_poi_review", "RECOMPUTE", "NB_GLD_SRV_POI_REVIEW", 1),
    (3, "slv_3p_poi_rating", "lh_vv_gold.dbo", "gld_srv_poi_review", "RECOMPUTE", "NB_GLD_SRV_POI_REVIEW", 1),
]
LOCK = "srvrev-" + uuid.uuid4().hex
```

Steps:
1. Stop if the `WID` row count is not 1 ("chạy plcadpy trước"). Take the lease, check the owner, set `held = True`. Stop if `CFG` has no `nb_name` column.
2. `# Dừng trước khi ghi`: collect every issue before any write.
   - Silver: missing table, or a schema not in the three accepted states.
   - Either `SOURCES` table is missing.
   - Gold exists and its schema is not `want`.
   - An edge to `gld_srv_poi_review` is active in another `pl_name`.
   - A `PL` row to `gld_srv_poi_review` whose payload is not in `EDGES_ON`, or that has `n != 1`, or that exists but is inactive. Such a row cannot be fixed without an UPDATE, so it is an issue.
   Raise `RuntimeError("Dừng trước khi ghi: …")` if there are any issues.
3. Writes. Each is directly preceded by a line-start `_refresh_lock()`:
   - `for` each name in `add`: `ALTER TABLE {ML_FQ} ADD COLUMNS (\`{name}\` {dtype} AFTER \`{anchor}\`)`. `anchor` is the previous name in `TABLE_COLS[ML_FQ]`. This is one `ALTER TABLE` literal in the code.
   - `spark.sql(_create_sql(REVIEW_FQ, TABLE_COLS[REVIEW_FQ]))` when gold is absent.
   - One `INSERT INTO {CFG} … FROM VALUES … AS t(seq, src_tbl, trg_schema, trg_tbl, load_mode, nb_name, priority) WHERE NOT EXISTS (…)`, with the column list `src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, nb_name` and `align_path` / `dedup_order` set to `CAST(NULL AS STRING)`.
4. `# Sau khi ghi`: both schemas equal `want`, and the active `PL` edges equal `EDGES_ON` with `n = 1`. Otherwise raise `RuntimeError("Sau khi ghi: …")`.
5. `except` sets `failed`. `finally` releases the lock: `WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'`, with status `SUCCESS` or `FAILED`.

### Test changes

`tests/test_initial_ddl_contract.py` (in scope):
- `test_table_inventory_matches_sources`: add `found.update(_assign(_cell(ddl, "srvrevpy"), "TABLE_COLS").keys())`. Change `len(specs) == 21` → `22`.
- `test_columns_match_sources`:
  - read `rev = _assign(_cell(ddl, "srvrevpy"), "TABLE_COLS")`;
  - in the `LANDING_COLS` loop, add `if fq in rev: cols = rev[fq]`;
  - add `gold["lh_vv_gold.dbo.gld_srv_poi_review"] = rev["lh_vv_gold.dbo.gld_srv_poi_review"]`.
- `test_pipeline_config_rows_match_sources`: after the `amenddlpy` loop, loop over `srvrevpy` `EDGES_ON` with `gld` and `assert seq > 0`. Change `66` → `69`.
- `test_flag_patch_create_matches_init`: in the contracts loop, add `if fq in rev: cols = rev[fq]`.
- `test_pl_cadence_patch_cell`: `[-4:-2]` → `[-6:-4]`.
- New `test_gld_srv_review_patch_create_matches_init`: exec the `_create_sql` and `PROPS` nodes of `srvrevpy`, as `test_gld_srv_patch_create_matches_init` does. Assert `_create_sql(fq, cols) == create_sql(spec)` for both `TABLE_COLS` entries. Assert `TABLE_COLS[ML_FQ]` equals the `enrflagpy` `LANDING_COLS[ML_FQ]` with `NEW_COLS` inserted after `poi_id`.
- New `test_gld_srv_review_patch_guards`:
  - token order: `held = True` < `Dừng trước khi ghi` < `ALTER TABLE` < `CREATE TABLE IF NOT EXISTS` (inside `_create_sql`: use the call `_create_sql(REVIEW_FQ` instead) < `INSERT INTO {CFG}` < `Sau khi ghi` < `finally:`;
  - in non-comment code, none of `DROP`, `DELETE`, `TRUNCATE`, `UPDATE {CFG}`, `REPLACE`, `RESTORE`, `columnMapping`;
  - `code.count("ALTER TABLE") == 1` and `" AFTER "` in code;
  - line-start `_refresh_lock()` calls (regex `(?m)^\s*_refresh_lock\(\)`) are exactly 3, with `calls[0] < ALTER < calls[1] < _create_sql(REVIEW_FQ < calls[2] < INSERT INTO {CFG}`;
  - `PL` equals `RENAMES[1][1]` from `plcadpy`;
  - `LEASE_MINUTES = 90` and `lock_exec_id = '{LOCK}'`;
  - `EDGES_ON` equals the three rows in invariant 7 order;
  - the `init_seed_ctrl` rows for `gld_srv_poi_review` equal `EDGES_ON` mapped to the seed tuple.

After the scope extension:
- `tests/test_gld_srv_poi_contract.py`:
  - `test_info_rating_patch`: `ids[-12:-4]` → `ids[-14:-6]`, `ids[-4:-2]` → `ids[-6:-4]`, `ids[-2:]` → `ids[-4:-2]`, then add `ids[-2:] == ["srvrevmd", "srvrevpy"]`.
  - New `test_review_node_spec`: SPEC kwargs (`pk`, `inputs`, `required_inputs`, `write_mode == "MERGE"`); no `lh_vv_gold` and no `deleted` in code; no `.cast(` in `srvrvbuild`; `SOURCE_TYPES` matches D-01 and D-02.
  - New `test_review_build_columns_match_ddl`: `list(OUT_COLS) + list(TECH) == names(srvrevpy TABLE_COLS[REVIEW_FQ])`.
  - New `test_review_mapping_targets`: the mapping §2 target column, in order, equals `OUT_COLS + ("created_at", "updated_at")`.
- `tests/test_enr_poi_contract.py` and `tests/test_poi_entity_contract.py`: shift every slice in the cell-order block by −2 and add `ids[-2:] == ["srvrevmd", "srvrevpy"]`.

## Verification

- Local:
  - `python -m pytest tests/test_initial_ddl_contract.py -q`
  - `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
  - `python -m pytest tests -q`
  - `python scripts/vv.py run-gate 20261026-gld-srv-poi-review`
- Fabric DEV probes (read-only). None blocks the design. P1 and P2 set the expectation for the first RUN. P4 gates step 4 of `## Rollout`.

| id | probe | result means |
|---|---|---|
| P1 | `SELECT count(*) FROM (SELECT review_id FROM lh_vv_silver.dbo.slv_enr_poi_review_multi_lang GROUP BY review_id HAVING count(*) > 1)` | above 0: the first RUN stops on `pk_duplicate` (model Conflicts 4) |
| P2 | `SELECT count(*) FROM (SELECT poi_id FROM lh_vv_silver.dbo.slv_3p_poi_rating WHERE poi_id IS NOT NULL GROUP BY poi_id HAVING count(*) > 1)` | above 0: the first RUN stops on the rating duplicate |
| P3 | `DESCRIBE lh_vv_silver.dbo.slv_3p_poi_review` and `DESCRIBE lh_vv_silver.dbo.slv_3p_poi_rating` | `rating decimal(4,2)`, `rating_overall decimal(4,2)`, `rating_count bigint`; otherwise `ConfigError` |
| P4 | `DESCRIBE HISTORY lh_vv_silver.dbo.slv_enr_poi_review_multi_lang LIMIT 20` (`operation`, `operationParameters`) | by-name writes (`WRITE`, `MERGE`) are safe. A positional SQL `INSERT` means the landing writer must change before `srvrevpy` runs. |

- Runtime:
  - `srvrevpy` twice. The second run prints no additions and no CREATE.
  - Node `DRY_RUN`: `qg_json` blocks are 0, and diff `inserted` equals the inner-join count.
  - Then `RUN`, then a second `RUN` with no commit.
  - SQL checks on live rows:
    - `count(*) = count(DISTINCT review_id)`;
    - a left anti join of gold to `slv_3p_poi_review` returns 0 rows;
    - `DESCRIBE` shows `rating decimal(4,2)` and `rating_count bigint`.
