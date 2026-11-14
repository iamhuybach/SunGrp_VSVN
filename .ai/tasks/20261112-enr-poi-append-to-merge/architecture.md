RESULT: PASS

## Main brief

### Decision
Use the existing lib MERGE (`sql_merge_target`, RECOMPUTE/MERGE) for `gld_enr_poi_info` (pk `poi_id`) and `gld_enr_poi_review` (pk `review_id`). Both builds become full snapshots, and the changed-key helpers are deleted. A new `NB_CREATE_DDL` cell `enrmergepy` adds `row_hash STRING` and `deleted_at TIMESTAMP` (D-COL-1) and changes ctrl `load_mode` from APPEND to RECOMPUTE. It refuses to run while any grain key is null or duplicated (D-RISK-1). The init seed and `init_tables` mirror these changes. No lib code change.
Precondition: three out-of-scope tests pin the tail cell ids of `NB_CREATE_DDL`. Add them to `scope.files` first (stop 1).

### Invariants Main must preserve
- The MERGE `ON` clause is exactly the pk: ``t.`poi_id` = s.`poi_id` `` for info and ``t.`review_id` = s.`review_id` `` for review.
- Neither build cell calls `ctx.changed(`, `ctx.basis`, or `_input_at(`. The source is the full live key set.
- Both SPECs have `write_mode="MERGE"` and no `soft_delete_set` or `hash_exclude` keyword.
- `BEGIN_INFO_SELECT…END_INFO_SELECT` and the review `rv.select(...)` stay byte-identical.
- Init column order for both tables: business columns, `created_at`, `updated_at`, `row_hash`, `deleted_at`.
- All 11 `init_seed_ctrl` rows for the two targets are `'RECOMPUTE'`. Review rows keep `is_active = 0`. No `'APPEND'` row is left in the seed.
- `enrmergepy` contains no DELETE, DROP, TRUNCATE, RESTORE, `SET is_active`, or `INSERT INTO {CFG}`. Its UPDATE is guarded by `upper(trim(load_mode)) = 'APPEND'`.
- `enrmergepy` raises "Dừng trước khi ghi" before any write when a target has null or duplicate keys.
- Historical `NB_CREATE_DDL` cells stay unchanged.
- No Fabric run is claimed.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | scope.files | task-state | add `tests/test_gld_srv_poi_contract.py`, `tests/test_poi_entity_contract.py`, `tests/test_srv_poi_serving_contract.py` | `vv.py` validation PASS |
| 2 | notebooks/NB_ENR_POI_INFO.ipynb | md `8cef70ac` | text per doc §6.2 (MERGE … theo poi_id, tính lại toàn bộ) | no "APPEND" in cell |
| 3 | notebooks/NB_ENR_POI_INFO.ipynb | `36415d3b` `_flag_keys`, `_i18n_keys`, `_role_keys`, `_vi_i18n` | delete; keep the pure block, `_keys`, `_present`, `_cost`, `_review_json`, `_service_flag`, `_require` | the four names are absent |
| 4 | notebooks/NB_ENR_POI_INFO.ipynb | `36415d3b` `build` | replace the top with the doc §6.2 code (`keys` = full spine); `ml`/`dest` use `keys`; update the COL-009/010 comment | `test_enr_builds_full_snapshot` passes |
| 5 | notebooks/NB_ENR_POI_INFO.ipynb | `36415d3b` `SPEC` | `write_mode="MERGE"` | `test_enr_specs_merge_and_pk` passes |
| 6 | notebooks/NB_ENR_POI_REVIEW.ipynb | md `82a6faef` | text per doc §6.2 | no "APPEND" |
| 7 | notebooks/NB_ENR_POI_REVIEW.ipynb | `04339a06` `_flag_keys`, `build` | delete `_flag_keys`; replace the top of `build` with the doc §6.2 code | the full-snapshot test passes |
| 8 | notebooks/NB_ENR_POI_REVIEW.ipynb | `04339a06` `SPEC` | `write_mode="MERGE"` | the spec test passes |
| 9 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, info and review entries | append `('row_hash','STRING',None), ('deleted_at','TIMESTAMP',None)` after `updated_at` | `test_columns_match_sources` passes |
| 10 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` lines ~907–919 | 11× `'APPEND'` → `'RECOMPUTE'`; add the `[SỬA 12/11]` comment | `test_enr_seed_merge_load_mode` passes |
| 11 | notebooks/NB_CREATE_DDL.ipynb | end of notebook | add md `enrmergemd` and code `enrmergepy`, verbatim from doc §6.3 | patch-cell tests pass |
| 12 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | md `026c3072` | one `[SỬA 12/11]` note line (doc §6.5) | no code diff |
| 13 | tests/test_enr_poi_contract.py | `test_info_patch_cell_guards`, `test_flag_node_contract`, `test_info_source_name_stays_entity`, `test_info_partner_join_matches_entity`, `test_info_removal_keys` | edit per doc §12 | pytest passes |
| 14 | tests/test_enr_poi_contract.py | new tests | add `test_enr_builds_full_snapshot`, `test_enr_specs_merge_and_pk`, `test_enr_sql_merge_target_keys`, `test_enr_merge_patch_cell_constants`, `test_enr_merge_patch_cell_guards`, `test_enr_seed_merge_load_mode` | pytest passes |
| 15 | tests/test_initial_ddl_contract.py | `test_columns_match_sources`, `test_flag_patch_create_matches_init`, `test_pipeline_config_rows_match_sources`, `test_pl_cadence_patch_cell` | add `TECH_ADD`; override mode with `MERGE_TARGETS`; change slice to `[-20:-18]` | pytest passes, 74 seed rows |
| 16 | the 3 test files from row 1 | tail `ids[...]` asserts | shift by −2; add `poidest` at `[-4:-2]` and `enrmerge` at `[-2:]` | pytest passes |
| 17 | docs/context/gld_enr_poi_info_review.md | both tables, lines 54–55, 65, 76–77 | `created_at`/`updated_at` meaning, `row_hash`/`deleted_at` rows, "Ghi" row, D-RISK-1 note | matches doc §16 |
| 18 | docs/context/CTRL_TABLES_CONTEXT.md | §3 line 84, line 145, §10 | RECOMPUTE/MERGE wording; history row | no APPEND for these tables |
| 19 | docs/context/01_DATA_MODEL.md | lines 67, 74, 351 | APPEND → RECOMPUTE / MERGE | grep clean |
| 20 | docs/context/00_README.md | item 8, line 38 | mode RECOMPUTE / MERGE | grep clean |
| 21 | docs/context/03_OPERATOR_GUIDE.md | line 40, §2.1, §2.2 | MERGE wording, log counts, 0/0/0 rerun proof, `deleted_at IS NULL` reader rule | matches doc §16 |

### Order and stop points
1. **STOP (user/Main decision):** add the three tail-index test files to `scope.files` (row 1). If refused, stop. Do not insert the cell mid-notebook.
2. Rows 2–8: node notebooks.
3. Rows 9–10: init.
4. Row 11: patch cell, verbatim.
5. Row 12: lib note.
6. Rows 13–16: tests. Run pytest. **STOP on any failure (evidence):** fix the code, not the assertion intent.
7. Rows 17–21: docs.
8. Run `vv.py verify`. Write the doc §14 runbook into `runtime-runbook.md`. **STOP:** no Fabric execution. The runtime proof (step 9: second RUN shows 0/0/0) is for the user to run on DEV.
9. Backlog: the drawio `gld_enr_poi_info` box is already stale ("40 cột"). Record it in decision.md findings as `backlog`.

### Tests and verification
- `python -m pytest tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py tests/test_gld_srv_poi_contract.py tests/test_poi_entity_contract.py tests/test_srv_poi_serving_contract.py -q`
- `python -m pytest -q`
- `python scripts/vv.py verify`
- New tests: `test_enr_builds_full_snapshot`, `test_enr_specs_merge_and_pk`, `test_enr_sql_merge_target_keys`, `test_enr_merge_patch_cell_constants`, `test_enr_merge_patch_cell_guards`, `test_enr_seed_merge_load_mode`.
- Changed tests: `test_info_patch_cell_guards`, `test_flag_node_contract`, `test_info_source_name_stays_entity`, `test_info_partner_join_matches_entity`, `test_info_removal_keys` (replaced), `test_columns_match_sources`, `test_flag_patch_create_matches_init`, `test_pipeline_config_rows_match_sources`, `test_pl_cadence_patch_cell`, and the tail asserts in the three added files.

### Read only if needed
- §0.1 Scope precondition → row 1, row 16
- §0.2 Answers to model-design questions → rows 4, 5, 8, 9 (column order, `soft_delete_set`, `hash_exclude`, hash stability)
- §5 Alternatives → why rows 11 and 16 are needed and why the lib is unchanged
- §6.1 NodeSpec → rows 5, 8
- §6.2 Build changes (code) → rows 2–4, 6–7
- §6.3 Patch cell (code) → row 11
- §6.4 Init → rows 9–10
- §6.5 Lib → row 12
- §9 Idempotency, §11 Partial failure → rows 11, 14
- §12 Verification → rows 13–16
- §14 Rollout and rollback → runbook, stop 8
- §16 Documentation edits → rows 17–21

# Architecture: 20261112-enr-poi-append-to-merge (round 2)

Round 2 replaces the round-1 EVIDENCE_REQUIRED text. Blocker B1 is resolved by D-COL-1 and `model-design.md`. Blocker B2 is resolved: `tests/test_initial_ddl_contract.py` is in `scope.files`. One scope precondition is new in this round (§0). It is mechanical and does not change the design.

## 0. Preconditions and resolved questions

### 0.1 Scope precondition (hard stop before edit row 10)

The repo rule in `docs/context/02_NAMING_CONVENTION.md` §2.1 says each migration goes in a new cell pair at the **end** of `NB_CREATE_DDL`. Three test files outside `scope.files` check the tail cell ids of that notebook by negative index. Adding `enrmergemd` and `enrmergepy` moves every one of those indices by 2:

- `tests/test_gld_srv_poi_contract.py` lines ~301–312 and ~534–538
- `tests/test_poi_entity_contract.py` lines ~635–648
- `tests/test_srv_poi_serving_contract.py` lines ~211 and ~291

Main must add these three files to `scope.files` before editing `NB_CREATE_DDL`. The only change in each is to shift the slice indices by −2 and add `ids[-4:-2] == ["poidestmd", "poidestpy"]` and `ids[-2:] == ["enrmergemd", "enrmergepy"]`. If the files cannot be added, stop and ask the user. Do not put the migration cell in the middle of the notebook to avoid the tests. That would break the append-only history rule.

### 0.2 Answers to `model-design.md` "Conflicts and questions"

| # | Answer | Evidence |
|---|---|---|
| 1 | D-COL-1 and this document stand in for `proposal.md`. No `ctrl_cfg_schema_registry` rows are needed. The registry describes bronze→silver L1 extract columns only. Gold target columns come from the build plus `TECH_COLUMNS`. | `CTRL_TABLES_CONTEXT.md` §5; lib `ensure_target` |
| 2 | `soft_delete_set` stays empty: do not pass it, so the default `{}` applies. A soft delete sets only `deleted_at` and `updated_at`. Neither table has `is_active`, and D-COL-1 forbids adding it. | lib `sql_merge_target` |
| 3 | Column order is compared **by name**, not by position. `ensure_target` builds a name→type map. `schema_diff` in `NB_SETUP_INITIAL_DDL` says "So theo tên (không theo vị trí)". `sql_merge_target` lists every column by name. Chosen physical order: business columns, `created_at`, `updated_at`, `row_hash`, `deleted_at`. That is what `ALTER TABLE ADD COLUMNS` produces on DEV, and `init_tables` uses the same order. Fresh and migrated tables then have the same shape. `target_ddl` (TECH order) is used only when a table is missing, and init always creates these two tables first. | lib `ensure_target`, init `schema_diff` |
| 4 | `hash_exclude = ()`, which is the default. Every business column is hashed. No business column holds batch time. | `36415d3b`, `04339a06` select lists |
| 5 | `review_json` is deterministic. The window orders by `time DESC, review_id ASC`. `array_sort` then sorts structs whose first field is `rn`. `service_flag` uses `array_sort(collect_set)`. One residual risk: if `slv_3p_poi_review` has two rows with the same `review_id` and `time` but different text, `row_number` can pick either. The runbook's second RUN catches this: it must show `updated = 0`. | `_review_json`, `_service_flag` |
| 6 | Yes, the doc update belongs to this task (§16). | request scope |
| 7 | No reader outside the lib was found. A repo-wide `Grep` outside `.ai/` and `notebooks_lgc/` finds these tables only in the two node notebooks, the DDL notebooks, the lib (a docstring example), tests, `docs/context`, `docs/requirements` (BRD/MAPPING), and the drawio diagrams. `services/` does not reference them. The external consumer rule ("filter `deleted_at IS NULL`") is documented in §16. | Grep |
| 8 | `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio` shows `row_hash`/`deleted_at` for MERGE gold tables. Its `gld_enr_poi_info` box already says "40 cột", which is the old `INFO_OLD` shape, not the current 37. The diagram is already stale for this table and is not in scope. Record a backlog item. It does not block this task. | drawio grep |
| 9 | `review_id` is passed through as `F.col("review_id")` from `slv_3p_poi_review`. This task does not change it. | `04339a06` |

## 1. Scope

- **Nodes:** two gold nodes on `PL_VV_TRANS_SLV_TO_ENR_15M`: `gld_enr_poi_info` (pk `poi_id`) and `gld_enr_poi_review` (pk `review_id`).
  - Today: `load_mode = APPEND`, which runs `execute_append`.
  - After: `load_mode = RECOMPUTE`, which runs `add_row_hash` → `quality_gate` → `diff_counts` → `ensure_target` → `merge_target` (`sql_merge_target`).
- **Builds:** both node builds become full snapshots of the live key set.
- **Columns:** both tables get `row_hash STRING` and `deleted_at TIMESTAMP` (D-COL-1), added through a new `NB_CREATE_DDL` patch cell on DEV and `init_tables` for fresh environments.
- **Ctrl seed:** the 11 `init_seed_ctrl` rows for the two targets change from `'APPEND'` to `'RECOMPUTE'`. `is_active` is unchanged, and review rows stay 0. The DEV ctrl rows change through the same patch cell.
- **Other files:** tests and docs that pin APPEND or the old column lists for these tables.

## 2. Non-goals

- No library code change. The APPEND machinery stays: `EDGE_LOAD_MODES`, `NODE_WRITE_MODE`, `execute_append`, `BEGIN_APPEND_PURE`. Only markdown cell `026c3072` gets a note. After this task the seed has no APPEND edge left: `gld_enr_poi_coordinate` was already removed by `mvpoipy`. APPEND remains a valid mode.
- No change to grain, key, business columns, sources, or `review_id`/`poi_id` derivation.
- No review edge activation.
- No pipeline JSON change: `PL_VV_TRANS_SLV_TO_ENR_15M.json` has no `load_mode`.
- No `services/` or `notebooks_lgc/` change. The drawio diagram is backlog (§0.2 item 8).
- No Fabric execution. The D-RISK-1 review data delete is a runbook step.
- Historical `NB_CREATE_DDL` cells (`enrddlpy`, `enrinfopy`, `enrflagpy`, `rvi18nenrpy`, …) stay byte-identical.

## 3. Invariants

1. **I1. One row per key.** After any successful RUN, each table has at most one row per key. The MERGE `ON` clause is exactly ``t.`poi_id` = s.`poi_id` `` for info and ``t.`review_id` = s.`review_id` `` for review.
2. **I2. No commit on an unchanged rerun.** A rerun with unchanged inputs, forced or not, gives `diff_counts` = 0/0/0. The MERGE is skipped and the target version does not change.
3. **I3. In-place update.** A changed payload for an existing key updates that row. `created_at` is kept. `updated_at`, `row_hash`, and the business columns are refreshed, and `deleted_at` becomes NULL.
4. **I4. Full-snapshot source.** The MERGE source is the full current live key set of the node. No build in this task may call `ctx.changed`, `ctx.basis`, or `ctx._input_at`. On the RECOMPUTE path `ctx.basis == {}`, so any of these calls raises.
5. **I5. Clean build keys.** The build output has no null or duplicate key. The lib `pk_null`/`pk_duplicate` checks block before any write.
6. **I6. Unique target keys before MERGE.** The MERGE never runs on a target whose current rows are not unique on the key. The patch cell refuses to flip `load_mode` while either table has a null or duplicate key (D-RISK-1: delete the review data first).
7. **I7. One `load_mode` per target.** Every ctrl row for the two targets on the PL has `load_mode = 'RECOMPUTE'`. Review rows keep `is_active = 0`. The patch cell never writes `is_active`.
8. **I8. Watermarks.** Edge watermarks move only through NB_00 `advance_edges`. `wm_e__<trg>__<src>` ids do not depend on `load_mode`, so no watermark row changes.
9. **I9. No destructive SQL on info.** No `DELETE`, `DROP`, `TRUNCATE`, or `RESTORE` on `gld_enr_poi_info` in any repo cell.
10. **I10. Business columns frozen.** Business column names, types, and order are unchanged. The `BEGIN_INFO_SELECT` block and the review `select` are unchanged. Only `row_hash` and `deleted_at` are added, after `updated_at`.

## 4. State ownership; grain and keys

- **Grain and keys:** `model-design.md` → `## Entities and grain` and `## Keys`. One row per `poi_id`, and one row per `review_id`. A soft-deleted key keeps its row, and live rows have `deleted_at IS NULL`.
- **Target rows:** the node notebook writes them through the lib. There is one writer, because `node_owner` requires exactly one PL.
- **Technical columns:** the lib owns `row_hash`, `created_at`, `updated_at`, and `deleted_at`. `add_row_hash` rejects a build that returns any of them. Column definitions are in `model-design.md` → `## Columns`.
- **Ctrl `load_mode`:** owned by the `init_seed_ctrl` seed for fresh environments and by `NB_CREATE_DDL` `enrmergepy` for existing environments.
- **Edge watermarks and flow lock:** NB_00 owns them. The patch cell borrows the flow lock while it runs.
- **Current data** (`evidence/results/key-uniqueness.txt`):
  - Info is unique: 20829 rows = 20829 distinct keys, 0 null.
  - Review is not unique: 110342 rows vs 109682 distinct keys.
  - D-RISK-1 empties review in the runbook before `enrmergepy`. The cell re-checks uniqueness (I6), so the runbook order is enforced, not only documented.

## 5. Alternatives

| ID | Option | Verdict |
|---|---|---|
| A1 | Reuse `sql_merge_target` through `run_node` RECOMPUTE. Add the two technical columns through a patch cell. Make builds full snapshots. | **Selected.** This is the only gold target MERGE (D-MERGE-1). It provides update-on-change, soft delete, a skipped commit when nothing changed, and diff counts in the log. |
| A2 | Keep the incremental changed-key build and only flip the write mode. | Rejected. `WHEN NOT MATCHED BY SOURCE` would soft-delete every untouched key on each run (I4). `ctx.basis` is also empty on RECOMPUTE. |
| A3 | Change the lib so `diff_counts` tolerates missing `row_hash`/`deleted_at`, and let `ensure_target` add them on the first RUN. That would remove the ALTER from the patch cell. | Rejected. It changes shared lib behaviour for every gold node. A patch cell is still needed for the ctrl `load_mode`. DRY_RUN would also run against a different schema than RUN. |
| A4 | Put the migration in `NB_SETUP_INITIAL_DDL`. | Rejected. 02 §2.1 rule 2 forbids `ALTER` and `UPDATE` there, and `test_no_destructive_sql` enforces it. |
| A5 | Insert the patch cell before `enrinfomd` so the tail-index tests stay unchanged. | Rejected. It breaks the append-only history convention to work around tests. §0.1 adds three files to scope instead. |
| A6 | DROP and recreate both tables. | Rejected. D-RISK-1 and I9. |

Trade-off: A1 recomputes about 20.8k POIs whenever any info input is dirty. In exchange, rerun safety comes from the shared, tested MERGE instead of per-node changed-key logic. The incremental helpers (`_role_keys`, `_flag_keys`, `_i18n_keys`) and their SPARK-001 edge cases go away.

## 6. Design

### 6.1 NodeSpec

- **Both SPEC cells:** `write_mode="MERGE"`. Do not pass `soft_delete_set` or `hash_exclude`, so the defaults apply.
- **Unchanged:** `pk`, `inputs`, `required_inputs`, `block_checks`, and `warn_checks`.
- **Fail-closed check:** `_resolve_node` checks `NODE_WRITE_MODE[load_mode] == spec.write_mode`. If the notebook and the ctrl `load_mode` disagree during deployment, the node fails with `ConfigError` before reading data.

### 6.2 Build changes

**`NB_ENR_POI_INFO` cell `36415d3b`**

- Delete `_flag_keys`, `_i18n_keys`, `_role_keys`, and `_vi_i18n`. They exist only to find changed keys.
- Keep:
  - the `BEGIN_INFO_PURE` block unchanged, including `PARTNER`;
  - `_keys`, `_present`, `_cost`, `_review_json`, `_service_flag`, and `_require`;
  - the `i18n` role in `inputs` and `REQUIRED_COLS`. `_resolve_node` requires a role for every active edge, and the edge still marks the inbox dirty.
- Replace the top of `build` up to the `base = (...)` join with the code below. Everything from the `base` join through the end of `build` stays unchanged, except two things:
  - the `ml`/`dest` lines use `keys`;
  - the COL-009/COL-010 comment is updated as shown.

```python
def build(ctx: NodeContext) -> DataFrame:
    # [SỬA 12/11] 20261112-enr-poi-append-to-merge: tính lại toàn bộ spine; lib MERGE theo poi_id,
    # khoá không còn trong kết quả bị xoá mềm (deleted_at). Không dùng ctx.changed / ctx.basis.
    _require(ctx)
    spine = ctx.input("entity")  # D-04: lib đã bỏ dòng xoá mềm và row_hash, created_at, updated_at, deleted_at
    keys = _keys(spine, "poi_id").persist(StorageLevel.MEMORY_AND_DISK)
    ctx.cached.append(keys)
    dropped = _keys(ctx.input("review"), "poi_id").join(keys, "poi_id", "left_anti").count()
    ctx.warn("review_poi_not_in_entity", dropped)
    for role in ("multi_lang", "destination"):
        ctx.warn(f"{role}_key_not_in_entity", ctx.input(role).select("poi_id").distinct().join(keys, "poi_id", "left_anti").count())
    e = spine.alias("e")
    am = _service_flag(ctx.input("amenity"), keys).alias("am")
    r = ctx.input("rating").alias("r")
    pr = ctx.input("price").alias("pr")
    rj = _review_json(ctx.input("review").join(keys, "poi_id", "left_semi")).alias("rj")
    # base = (...) joins: unchanged
    ml = _present(ctx, "multi_lang", "poi_id", keys).alias("ml")
    dest = _present(ctx, "destination", "poi_id", keys).alias("dest")
    # unchanged through `return out`, except the comment line:
    # COL-009 — created_at: lib MERGE gán khi insert. COL-010 — updated_at: lib MERGE gán khi row_hash đổi hoặc xoá mềm.
```

- Markdown `8cef70ac` becomes: `MERGE lh_vv_gold.enr.gld_enr_poi_info theo poi_id từ lh_vv_silver.dbo.slv_poi_entity_non_enrich (tính lại toàn bộ).`
- Meaning change: `review_poi_not_in_entity` now counts all review POIs missing from the spine, not only the changed ones. Document it in 03 §2.1.

**`NB_ENR_POI_REVIEW` cell `04339a06`**

- Delete `_flag_keys`.
- Replace the top of `build` up to the `cast_rating` line with:

```python
def build(ctx: NodeContext) -> DataFrame:
    # [SỬA 12/11] 20261112-enr-poi-append-to-merge: tính lại toàn bộ; lib MERGE theo review_id,
    # review_id không còn trong kết quả bị xoá mềm (deleted_at). Không dùng ctx.changed / ctx.basis.
    rv_all = ctx.input("review").where(F.col("review_id").isNotNull())
    live_ids = rv_all.select("review_id").distinct()
    ml_ids = ctx.input("multi_lang").select("review_id").where(F.col("review_id").isNotNull()).distinct()
    ctx.warn("multi_lang_key_not_in_review", ml_ids.join(live_ids, "review_id", "left_anti").count())
    rv = rv_all.join(ml_ids.withColumn("ml_hit", F.lit(True)), "review_id", "left")
    # cast_rating, overflow QG, review_date warn, and `return rv.select(...)`: unchanged
```

- Markdown `82a6faef` becomes: `MERGE lh_vv_gold.enr.gld_enr_poi_review theo review_id. Chỉ 3rd-party. Cạnh đang tắt (is_active = 0).`
- Known limit: the review edges are inactive, so `_resolve_node` rejects any run of this node. Its MERGE is proven by contract tests only.

### 6.3 `NB_CREATE_DDL`: new cells at the end

- Markdown `enrmergemd`, text: `# [THÊM 12/11] 20261112-enr-poi-append-to-merge`
- Code `enrmergepy`, content below. The cell follows the `ohpasspy` pattern:
  1. lock row
  2. lease
  3. "Dừng trước khi ghi" checks
  4. `_refresh_lock` before each write
  5. "Sau khi ghi" checks
  6. `finally` release

```python
# [THÊM 12/11] 20261112-enr-poi-append-to-merge
# 1. gld_enr_poi_info, gld_enr_poi_review: thêm row_hash STRING, deleted_at TIMESTAMP (cho phép NULL, cuối bảng) nếu chưa có (D-COL-1).
# 2. ctrl_mng_pipeline_config: load_mode APPEND -> RECOMPUTE cho mọi dòng tới hai bảng trên PL (D-MERGE-1). Không đổi is_active.
# Dừng trước khi ghi khi khoá grain NULL / trùng (D-RISK-1: runbook xoá dữ liệu gld_enr_poi_review trước), cạnh review đang bật,
# hoặc load_mode lạ. Không xoá dòng, không DROP. Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M suốt cell. Chạy lại: không đổi gì.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_ENR_15M"
WID = f"wm_flow__{PL}"
GLD = "lh_vv_gold.enr"
TARGETS = {"gld_enr_poi_info": "poi_id", "gld_enr_poi_review": "review_id"}
MERGE_TARGETS = ("gld_enr_poi_info", "gld_enr_poi_review")
REVIEW = "gld_enr_poi_review"
TECH_ADD = [("row_hash", "STRING"), ("deleted_at", "TIMESTAMP")]
LEASE_MINUTES = 35  # bằng p_lock_timeout_min của NB_00_ORCHES_SLV_TO_ENR_15P
LOCK = "enrmerge-" + uuid.uuid4().hex
IN_SQL = ", ".join(f"'{name}'" for name in MERGE_TARGETS)


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


def _types(fq):
    return {f.name.lower(): f.dataType.simpleString() for f in spark.table(fq).schema.fields}


def _modes():
    # (trg_tbl, load_mode, is_active) -> số dòng cấu hình.
    return {(row["trg_tbl"], row["load_mode"], row["is_active"]): row["n"] for row in spark.sql(f"""
    SELECT trg_tbl, upper(trim(load_mode)) AS load_mode, is_active, count(*) AS n FROM {CFG}
    WHERE pl_name = '{PL}' AND trg_schema = '{GLD}' AND trg_tbl IN ({IN_SQL})
    GROUP BY trg_tbl, upper(trim(load_mode)), is_active
    """).collect()}


# Tạo dòng khoá nếu chưa có. Không xoá wm_flow__.
spark.sql(f"""
MERGE INTO {WM} AS t
USING (SELECT '{WID}' AS watermark_id, '{PL}' AS src_tbl, 'NB_CREATE_DDL' AS flow_name) AS s
ON t.watermark_id = s.watermark_id
WHEN NOT MATCHED THEN INSERT
    (watermark_id, src_schema, src_tbl, trg_schema, trg_tbl, watermark_column, watermark_value, last_success_at,
     status, flow_name, watermark_sequence, last_run_id, last_src_version, last_src_table_id, error_message,
     lock_exec_id, lock_at, updated_at)
VALUES
    (s.watermark_id, CAST(NULL AS STRING), s.src_tbl, CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS STRING),
     CAST(NULL AS TIMESTAMP), CAST(NULL AS TIMESTAMP), 'INITIALIZED', s.flow_name, CAST(NULL AS BIGINT),
     CAST(NULL AS STRING), CAST(NULL AS BIGINT), CAST(NULL AS STRING), CAST(NULL AS STRING), CAST(NULL AS STRING),
     CAST(NULL AS TIMESTAMP), current_timestamp())
""")
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
    owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
    if not owner or owner["lock_exec_id"] != LOCK:
        other = None if owner is None else owner["lock_exec_id"]
        raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")
    held = True

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    missing = {}
    for trg, key in TARGETS.items():
        fq = f"{GLD}.{trg}"
        if not spark.catalog.tableExists(fq):
            issues.append(f"{fq} chưa có: chạy NB_SETUP_INITIAL_DDL")
            continue
        have = _types(fq)
        for name, dtype in TECH_ADD:
            if name in have and have[name] != dtype.lower():
                issues.append(f"{fq}.{name} là {have[name]}, cần {dtype.lower()}")
        missing[fq] = [(name, dtype) for name, dtype in TECH_ADD if name not in have]
        row = spark.sql(f"SELECT count(*) AS n, count(`{key}`) AS k, count(DISTINCT `{key}`) AS d FROM {fq}").first()
        if row["k"] != row["n"] or row["d"] != row["k"]:
            issues.append(f"{fq}: {row['n']} dòng, {row['n'] - row['k']} khoá NULL, {row['k'] - row['d']} dòng trùng "
                          f"theo {key}; MERGE cần khoá duy nhất (D-RISK-1)")
    modes = _modes()
    for trg in MERGE_TARGETS:
        if not any(name == trg for name, _mode, _flag in modes):
            issues.append(f"{trg}: không có dòng cấu hình trên {PL}")
    odd = sorted({mode for _name, mode, _flag in modes} - {"APPEND", "RECOMPUTE"})
    if odd:
        issues.append(f"load_mode lạ {odd}: cell chỉ đổi APPEND -> RECOMPUTE")
    review_on = sum(n for (name, _mode, flag), n in modes.items() if name == REVIEW and flag == 1)
    if review_on:
        issues.append(f"{REVIEW} có {review_on} cạnh is_active = 1: cell không bật / tắt cạnh")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    _refresh_lock()
    for fq, cols in missing.items():
        if cols:
            spark.sql(f"ALTER TABLE {fq} ADD COLUMNS (" + ", ".join(f"`{name}` {dtype}" for name, dtype in cols) + ")")
    _refresh_lock()
    spark.sql(f"""
    UPDATE {CFG}
    SET load_mode = 'RECOMPUTE'
    WHERE pl_name = '{PL}' AND trg_schema = '{GLD}' AND trg_tbl IN ({IN_SQL})
      AND upper(trim(load_mode)) = 'APPEND'
    """)

    # Sau khi ghi: chỉ xét phần cell đổi.
    problems = []
    for trg in MERGE_TARGETS:
        have = _types(f"{GLD}.{trg}")
        for name, dtype in TECH_ADD:
            if have.get(name) != dtype.lower():
                problems.append(f"{GLD}.{trg}.{name} là {have.get(name)}, cần {dtype.lower()}")
    after = _modes()
    left = {k: n for k, n in after.items() if k[1] != "RECOMPUTE"}
    if left:
        problems.append(f"còn load_mode khác RECOMPUTE: {left}")
    if any(name == REVIEW and flag == 1 for name, _mode, flag in after):
        problems.append(f"{REVIEW} có cạnh is_active = 1")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"{sorted(MERGE_TARGETS)}: row_hash string, deleted_at timestamp; load_mode RECOMPUTE {after}")
except Exception as exc:
    failed = exc
    raise
finally:
    if held:
        status = "FAILED" if failed else "SUCCESS"
        detail = "" if failed is None else str(failed).replace("'", " ")[:500]
        spark.sql(f"""
        UPDATE {WM}
        SET lock_exec_id = NULL, lock_at = NULL, status = '{status}', error_message = '{detail}',
            updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
```

**Fail-closed halves.** The ALTER and the UPDATE are separate commits.

- ALTER done, UPDATE not done: an info APPEND run fails in `check_append_schema` because the schema is no longer the exact APPEND schema.
- UPDATE done, ALTER not done: the UPDATE comes after the ALTER in the cell, so this can only happen if the ALTER failed. In that case the cell raised before the UPDATE ran.

In both cases the fix is to rerun the cell.

### 6.4 `NB_SETUP_INITIAL_DDL`

- **`init_tables`:** in the `lh_vv_gold.enr.gld_enr_poi_info` and `lh_vv_gold.enr.gld_enr_poi_review` entries, append `('row_hash', 'STRING', None), ('deleted_at', 'TIMESTAMP', None)` after `('updated_at', 'TIMESTAMP', None)`.
- **`init_seed_ctrl`:**
  - The 11 rows at lines ~907–919 change `'APPEND'` to `'RECOMPUTE'`. Nothing else in those rows changes.
  - Add the comment `# [SỬA 12/11] 20261112-enr-poi-append-to-merge: gld_enr_poi_info, gld_enr_poi_review RECOMPUTE / MERGE.` above the first of them.
- **No other cells change.** `init_plan` compares by name. It raises on a DEV table that has no technical columns yet. That is intended, and it is why the runbook runs `enrmergepy` before init.

### 6.5 `NB_LIB_TRANSFORM_SLV_GLD`

- No code change.
- Append one line to markdown cell `026c3072`: `[SỬA 12/11] gld_enr_poi_info, gld_enr_poi_review chuyển sang RECOMPUTE / MERGE (20261112-enr-poi-append-to-merge); APPEND giữ trong lib cho cạnh khác.`

## 7. Ordering

- **Inside a node:** the existing `run_node` order is unchanged.
  1. Lock check.
  2. Pin versions.
  3. Inbox check: NO_DATA unless an input is dirty, `p_force` is set, or the target is missing.
  4. `build`, then `add_row_hash`, then `quality_gate`.
  5. `diff_counts`, which reads `row_hash` and `deleted_at` from the target. This is why the columns must exist before the first run, including DRY_RUN.
  6. RUN only: `ensure_target`, then MERGE if the diff is non-zero.
  7. Node log.
- **DAG:** `slv_poi_entity_non_enrich` → `slv_poi_amenity` → `gld_enr_poi_info`. Unchanged.
- **Deployment:** §14. Code sync and ctrl flip happen with the schedule paused. A mismatch in either order fails closed in `_resolve_node`.

## 8. Transaction and commit boundaries

- **Node write:** one MERGE is one Delta commit on the target. Business and technical columns change atomically.
- **Node log:** `ctrl_log_table_run` is a separate append in `finally`.
- **Watermark advance:** NB_00 `advance_edges` is a separate MERGE after the nodes run. If the target commit succeeds and the advance fails, the next run recomputes. The diff is then 0/0/0, so no second commit is written (I2).
- **Patch cell:** ALTER on info, ALTER on review, and the ctrl UPDATE are three commits under one lease. The fail-closed analysis is in §6.3.

## 9. Idempotency

- **Same inputs, normal or forced rerun:** the hashes match and `deleted_at` is NULL, so there is no matched update, no insert, and no deactivation. The MERGE is skipped (I2).
- **First MERGE on migrated info:** every row has `row_hash IS NULL`.
  - Expect `updated` = 20829 minus keys absent from the spine.
  - Expect `deactivated` = info keys no longer in the spine. APPEND never removed them.
  - This happens once, and `created_at` is kept.
- **Review after D-RISK-1:** the table is empty, so the first future run is all inserts. This is out of scope while the edges are off.
- **`enrmergepy` rerun:** it adds only missing columns and updates only `APPEND` rows, so a rerun is a no-op. Its post-checks pass on a rerun.

## 10. Concurrency

- **Writers:** one writer per node (`node_owner`). No other notebook writes these tables. Gold srv notebooks read silver, not gold.
- **Flow lock `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M`:**
  - NB_00 runs hold it.
  - A manual RUN acquires it.
  - `enrmergepy` acquires it with a 35-minute lease and refreshes it before each write. While NB_00 is running, the cell refuses to start.
- **MERGE conflicts:** Delta MERGE uses optimistic concurrency, and `merge_target` retries transient conflicts through `with_retry`. A retried full-snapshot MERGE gives the same result.

## 11. Retry, recovery, partial failure

| Failure point | State left | Recovery |
|---|---|---|
| Build or QG raises (`pk_duplicate`, `opening_hours_text_mismatch`, `json_text_null`, …) | No target commit. Node FAILED. Edge not advanced. | Fix the source data. Do not relax the QG. The next cycle retries. |
| Full-snapshot QG finds an old violation that the incremental path never read | Same. | The runbook DRY_RUN finds it before the first RUN. |
| MERGE fails | No commit. | Same as above. |
| MERGE commits, watermark advance fails | Target is correct. Edge is stale. | The next run computes a 0 diff and writes no commit. |
| `enrmergepy` stops in "Dừng trước khi ghi" | Nothing written. | Fix the cause, for example the D-RISK-1 delete, then rerun. |
| `enrmergepy` fails between ALTER and UPDATE | Columns added. Ctrl still APPEND. | An info APPEND run fails in `check_append_schema` and writes nothing. Rerun the cell. |
| Notebook synced, ctrl not flipped, or the reverse | `_resolve_node` raises `ConfigError`. | Finish the other half. |

## 12. Verification

### Contract tests: `tests/test_enr_poi_contract.py`

**Changed tests**

- `test_info_patch_cell_guards`:
  - Shift every tail slice by −2.
  - Add `ids[-4:-2] == ["poidestmd", "poidestpy"]` and `ids[-2:] == ["enrmergemd", "enrmergepy"]`.
- `test_flag_node_contract`: replace the `_flag_keys` equality line with `assert "def _flag_keys" not in info and "def _flag_keys" not in review`.
- `test_info_source_name_stays_entity`: the expected string becomes `ml = _present(ctx, "multi_lang", "poi_id", keys).alias("ml")`.
- `test_info_partner_join_matches_entity`:
  - Keep the entity-side assertions and `_info_pure()["PARTNER"] == "partner"`.
  - Replace the two info-side `uuid_md5`/`locale` assertions with `assert "_vi_i18n" not in info and "_i18n_keys" not in info`.
- `test_info_removal_keys`: replace it with `test_enr_builds_full_snapshot`:
  - Neither build cell contains `ctx.changed(`, `ctx.basis`, `_input_at(`, `_role_keys`, or `_flag_keys`.
  - Info contains `keys = _keys(spine, "poi_id")` and `e = spine.alias("e")`.
  - Review contains `rv = rv_all.join(`.

**New tests**

- `test_enr_specs_merge_and_pk`: parse `SPEC` with `ast` in both cells and check:
  - `write_mode == "MERGE"`;
  - `pk == ("poi_id",)` for info and `pk == ("review_id",)` for review;
  - there is no `soft_delete_set` or `hash_exclude` keyword;
  - neither cell contains `"APPEND"`.
- `test_enr_sql_merge_target_keys`:
  - Extract `sql_merge_target` from lib cell `926a3f9c` with `ast` (the same way `_func_text` works) and exec it with a `quote_name` stub.
  - Call it with the info columns (`INFO` names minus `created_at`/`updated_at`) and pk `("poi_id",)`, and again for review.
  - Assert that the `ON` line equals ``ON t.`poi_id` = s.`poi_id` `` (and the `review_id` version).
  - Assert that the `NOT MATCHED BY SOURCE` set list is exactly the `deleted_at` and `updated_at` assignments.
  - Assert that the INSERT column list ends with `row_hash`, `created_at`, `updated_at`, `deleted_at`.
- `test_enr_merge_patch_cell_constants`: in `enrmergepy`, `_assign` gives:
  - `PL == "PL_VV_TRANS_SLV_TO_ENR_15M"`;
  - `TARGETS == {"gld_enr_poi_info": "poi_id", "gld_enr_poi_review": "review_id"}`;
  - `MERGE_TARGETS == tuple(TARGETS)`;
  - `TECH_ADD == [("row_hash", "STRING"), ("deleted_at", "TIMESTAMP")]`.

  Each `TECH_ADD` name and its lowercased type is in the lib `TECH_COLUMNS`.
- `test_enr_merge_patch_cell_guards`:
  - Token order: `held = True` < `Dừng trước khi ghi` < `ALTER TABLE` < `SET load_mode = 'RECOMPUTE'` < `Sau khi ghi` < `finally:`.
  - Exactly 2 `_refresh_lock()` calls at the start of a line, one before the ALTER and one before the UPDATE.
  - The code without comments contains none of `DROP`, `DELETE`, `TRUNCATE`, `RESTORE`, `REPLACE`, `INSERT INTO {CFG}`, `SET is_active`, or ` AFTER `.
  - It contains `AND upper(trim(load_mode)) = 'APPEND'`, `count(DISTINCT`, `LEASE_MINUTES = 35`, and `lock_exec_id = '{LOCK}'`.
- `test_enr_seed_merge_load_mode`:
  - Exec `init_seed_ctrl`.
  - Every row whose `row[4]` is one of the two targets has `row[7] == "RECOMPUTE"`.
  - Review rows have `row[5] == 0`.
  - There are 11 such rows.
  - There is no `"APPEND"` row left in `PIPELINE_CONFIG_ROWS`.

**Kept unchanged:** `test_mapping_comments_and_edges` (it reads historical `enrddlpy`, so the APPEND count stays 11), `test_info_select_matches_ddl`, and `test_info_removed_columns_absent`.

### Contract tests: `tests/test_initial_ddl_contract.py`

- `test_columns_match_sources`: the expected info and review columns become the current source list plus `[(n, t, None) for n, t in TECH_ADD]`, with `TECH_ADD` read from `enrmergepy`.
- `test_flag_patch_create_matches_init`: the info and review contracts become `cols + TECH_ADD`.
- `test_pipeline_config_rows_match_sources`:
  - Read `MERGE_TARGETS` from `enrmergepy`.
  - In the three `enr` loops (`edges`, `added`, `flagged`), use `"RECOMPUTE" if target in merge else mode`.
  - The count stays 74.
- `test_pl_cadence_patch_cell`: the slice becomes `[-20:-18]`.

### Tail-index tests (after §0.1)

`tests/test_gld_srv_poi_contract.py`, `tests/test_poi_entity_contract.py`, and `tests/test_srv_poi_serving_contract.py` each get the −2 shift and the new last pair.

### Commands

```
python -m pytest tests/test_enr_poi_contract.py tests/test_initial_ddl_contract.py tests/test_gld_srv_poi_contract.py tests/test_poi_entity_contract.py tests/test_srv_poi_serving_contract.py -q
python -m pytest -q
python scripts/vv.py verify
```

### Runtime proof

This task does not run it. The Fabric DEV runbook in §14 goes into `runtime-runbook.md`.

## 13. Observability and security

- **Observability:** `ctrl_log_table_run` records `inserted_rows`, `updated_rows`, `deactivated_rows`, `trg_version`, and `qg_json` for these nodes.
  - Under RECOMPUTE, `updated_rows`/`deactivated_rows` can be non-zero.
  - `qg_json` no longer carries `basis`.
  - Rerun proof: a second RUN shows 0/0/0 and an unchanged `trg_version`.
- **`enrmergepy` output:** it prints the final mode map, and its lock row status records SUCCESS or FAILED with the error text.
- **Security:** no credentials, hosts, or personal data. Probes and runbook queries are aggregates only.

## 14. Rollout, rollback, forward recovery

### Rollout: Fabric DEV runbook (not run in this task)

1. Pause the `PL_VV_TRANS_SLV_TO_ENR_15M` schedule. Confirm the flow lock is free.
2. Record the current version of `gld_enr_poi_info` with `DESCRIBE HISTORY … LIMIT 1`. This is the rollback point.
3. D-RISK-1: run `DELETE FROM lh_vv_gold.enr.gld_enr_poi_review`. Never run it on info.
4. Sync the branch notebooks to the workspace.
5. Run `NB_CREATE_DDL` cell `enrmergepy`. It must print RECOMPUTE for both targets.
6. Run `NB_SETUP_INITIAL_DDL` with `p_apply = "false"`, then `"true"`. There must be no schema issue, and `to_insert = 0` for `pipeline_config`.
7. Run `NB_ENR_POI_INFO` with `p_mode = DRY_RUN` and `p_force = true`.
   - Expect: QG passes, `inserted` = new spine keys, `updated` ≈ 20829, and `deactivated` = info keys absent from the spine.
   - Stop on any QG block.
8. Run `NB_ENR_POI_INFO` with `p_mode = RUN` and `p_force = true`.
9. Repeat step 8. It must show 0/0/0 with an unchanged `trg_version`. This is the acceptance proof.
10. Rerun `evidence/probes/key-uniqueness.sql`.
    - Info: `row_count = distinct_key_count`, `null_key_count = 0`.
    - Review: 0 rows.
11. Resume the schedule. One NB_00 cycle must be SUCCESS or NO_DATA, and the edges must advance.

The review MERGE gets no runtime proof while its edges are off. Record this limit in the runbook.

### Rollback

- **Before step 8:**
  - Revert the code.
  - Run `UPDATE … SET load_mode = 'APPEND'` for the two targets.
  - `RESTORE TABLE gld_enr_poi_info TO VERSION AS OF <step 2>` to remove the added columns. `check_append_schema` requires the exact APPEND schema.
  - RESTORE on info needs explicit user approval at that time (I9 covers repo cells, not this manual step).
- **After step 8:** use forward recovery only. Fix the build or source and rerun. A full-snapshot MERGE heals itself, and any MERGE commit invalidates the APPEND marker baseline anyway.

## 15. Implementation plan

1. Main adds the three tail-index test files to `scope.files` (§0.1).
2. `NB_ENR_POI_INFO`: cells `8cef70ac` and `36415d3b` (§6.1, §6.2).
3. `NB_ENR_POI_REVIEW`: cells `82a6faef` and `04339a06`.
4. `NB_SETUP_INITIAL_DDL`: `init_tables` and `init_seed_ctrl` (§6.4).
5. `NB_CREATE_DDL`: append `enrmergemd` and `enrmergepy` (§6.3). Keep the notebook JSON cell format the same as `poidestpy`: `execution_count: null`, `outputs: []`.
6. `NB_LIB_TRANSFORM_SLV_GLD`: the note in `026c3072` (§6.5).
7. Tests (§12).
8. Docs (§16).
9. Run the commands in §12.

## 16. Documentation edits

- **`docs/context/gld_enr_poi_info_review.md`**
  - Lines 54–55 and 76–77: `created_at` is "thời điểm insert lần đầu (lib MERGE)". `updated_at` is "lần MERGE đổi dòng (row_hash đổi, hồi sinh, hoặc xoá mềm)".
  - Add rows for `row_hash STRING` and `deleted_at TIMESTAMP`.
  - Add a "Ghi" row to both header tables: `MERGE theo poi_id / review_id; khoá rời nguồn -> giữ dòng, deleted_at set; người đọc lọc deleted_at IS NULL`.
  - Line 65: replace "không xoá dòng" with the D-RISK-1 note. The runbook deletes the old APPEND review data before MERGE, and the flow stays off.
- **`CTRL_TABLES_CONTEXT.md`**
  - Line 84: `APPEND` no longer names these tables. It is "hợp lệ; hiện không cạnh nào dùng".
  - Line 145: `(RECOMPUTE / MERGE, trg_schema = lh_vv_gold.enr)`.
  - §10: add a history row for 12/11.
- **`01_DATA_MODEL.md`:** line 67 (mermaid label), line 74, and line 351: replace `APPEND` with `RECOMPUTE / MERGE`.
- **`00_README.md`:** line 38: mode `RECOMPUTE / MERGE`.
- **`03_OPERATOR_GUIDE.md`**
  - Line 40: the APPEND row stays valid. Note that no current edge uses it.
  - §2.1 line 239 and §2.2 line 267: replace "Ghi bằng `APPEND`" with "MERGE theo `poi_id` / `review_id`".
  - Add the log-count meaning, the rerun proof (0/0/0), the `review_poi_not_in_entity` scope, and the `deleted_at IS NULL` reader rule.

## 17. Remaining evidence (runbook prechecks, not design blockers)

| Probe | Question | Blocks |
|---|---|---|
| Runbook step 7 DRY_RUN | Does the full-snapshot QG pass on every info key? How many keys are soft-deleted? | Runbook step 8 |
| Runbook step 9 | Is `row_hash` stable across runs (§0.2 item 5)? | Acceptance |
| External consumers (SQL endpoint, BI, PG sync) | Do they filter `deleted_at IS NULL`? | Doc wording only. Ask the user. |
