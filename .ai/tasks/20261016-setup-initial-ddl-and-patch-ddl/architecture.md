RESULT: PASS

## Main brief

### Decision
RESULT PASS (round 2). Decisions bound: U1 = A (the existing `nb_name` pair: the `enrddlpy` guarded ALTER plus `nb_name` in the first-run CREATE) and U2 (`slv_poi_entity` is table #14).
New insert-only `notebooks/NB_SETUP_INITIAL_DDL.ipynb`: 14 tables and 5 seeds, `p_apply="false"` by default. `NB_CREATE_DDL.ipynb` stays byte-unchanged.
`slv_poi_entity` has no CREATE literal in the repo. Its 21 columns are derived from `b1entitybuild` plus the lib tech columns (§5.1a) and pinned by a derivation test.
The rule lives in `02_NAMING_CONVENTION.md` §2.1, with one sentence in `AGENTS.md`. First fix the malformed `scope.files`.

### Invariants Main must preserve
- The first-run uses only `CREATE SCHEMA/TABLE IF NOT EXISTS` and `MERGE … WHEN NOT MATCHED THEN INSERT`. No DROP, DELETE, TRUNCATE, ALTER, UPDATE, `WHEN MATCHED`, `replaceWhere`, overwrite, or `INSERT INTO`.
- When `p_apply` is not true-ish: zero writes. Print 14 table actions, CREATE text, and per-seed `defined`/`to_insert`, then exit `PLAN`.
- Two apply runs give the same rows; each §5.2 logical key appears exactly once.
- An existing table with a column, type, nullability, or partition diff (by name) raises `ConfigError` in `init_plan` before any write.
- One MERGE per seed table, each in `with_retry`. pipeline_config `id = COALESCE(MAX(id),0)+seq`, with MAX read inside the retried function.
- First-run definitions equal the repo sources (tables #1–#13, `nb_name` folded into #1, `TABLE_CONFIGS`, `TABLE_CONFIGS_3P`, byte-identical ref seed blocks, 50 pipeline_config rows, 2 watermark rows).
- The `slv_poi_entity` spec matches §10.1a exactly: 21 columns, all nullable, PROPS, no comment, no partition (whatever `ensure_target` would create).
- `git diff --exit-code notebooks/NB_CREATE_DDL.ipynb` passes.
- Seeds are repo literals only. `AGENTS.md` < 8192 bytes.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| E0 | `.ai/tasks/20261016-setup-initial-ddl-and-patch-ddl/task-state.yaml` | `scope.files` | Replace the malformed joined string (lines 29–30) with separate items: `docs/context/CTRL_TABLES_CONTEXT.md`, `AGENTS.md`, `notebooks/NB_SETUP_POI_AMENITY.ipynb`, `notebooks/NB_SLV_POI_ENTITY.ipynb`, `notebooks/NB_SLV_POI_AMENITY.ipynb`; add `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, `tests/test_initial_ddl_contract.py` | YAML list has 10 separate paths; `vv.py verify` accepts it |
| E1 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_md`, `init_param`, `init_run` | VN header with preconditions; `p_apply = "false"` tagged `parameters`; `%run NB_LIB_TRANSFORM_SLV_GLD`; metadata copied from `NB_SETUP_POI_ENTITY` | `test_param_default_false` |
| E2 | same | `init_tables` | `BEGIN/END_INIT_TABLE_SPECS`: specs #1–#13 per §5.1 (columns/comments exact, `nb_name` in #1), #14 per §10.1a; `create_sql`, `schema_diff` (§10.1) | `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_poi_entity_columns_derived`, `test_create_sql_renders` |
| E3 | same | `init_cfg_partner`, `init_cfg_3p` | verbatim copies of `28e2be98`, `e9c137c5` | `test_registry_configs_equal_create_ddl` |
| E4 | same | `init_registry_pure` | `BEGIN/END_REGISTRY_PURE` from `0f228dc1`, then `REGISTRY_SCHEMA` | `test_registry_rows_valid` |
| E5 | same | `init_seed_ctrl` | `PIPELINE_CONFIG_ROWS` (50), `WATERMARK_ROWS` (2) (§10.2) | `test_pipeline_config_rows_match_sources`, `test_watermark_rows_match_source` |
| E6 | same | `init_seed_place_type`, `init_seed_amenity` | byte-identical seed blocks; then `validate_seed`; bind `PLACE_TYPE_ROWS`/`AMENITY_ROWS` in the same cell | `test_ref_seed_blocks_identical` |
| E7 | same | `init_plan` | §10.3 steps 1–8 | `test_plan_precedes_writes`; R1 |
| E8 | same | `init_ddl` | `CREATE SCHEMA IF NOT EXISTS lh_vv_gold.enr`; 14 CREATEs with retry; re-check all 14 | R2: 14 tables |
| E9 | same | `init_seed_write` | 5 insert-only MERGEs in §6 order (§10.4) | `test_no_destructive_sql`; R3 `inserted=0` |
| E10 | same | `init_verify`, `init_exit` | dup and missing = 0 else `ConfigError`; drift; cross-checks; SUCCESS JSON | R2/R3 JSON per §12 |
| E11 | `tests/test_initial_ddl_contract.py` | new file | tests below (§16) | all pass |
| E12 | `notebooks/NB_CREATE_DDL.ipynb` | — | **no edit** (U1 = A) | `git diff --exit-code` clean; `test_example_patch_dual_update` |
| E13 | `docs/context/02_NAMING_CONVENTION.md` | `## 2. Notebook` table | replace the `NB_CREATE_DDL` row, add the `NB_SETUP_INITIAL_DDL` row (§18) | rows present |
| E14 | same | new `### 2.1` before `## 3. Pipeline` | insert the §18 text exactly (rule 3 example `nb_name`, rule 7 exception) | `test_roles_documented` |
| E15 | `AGENTS.md` | §7 "Notebook roles" bullet | replace the `NB_CREATE_DDL creates the control tables.` sentence (§19) | < 8192 bytes; no `vv.py verify` budget warning |
| E16 | `docs/context/CTRL_TABLES_CONTEXT.md` | line 4; §1 rows 1 and 3; §3 DDL line 70 (`nb_name`); §10 | edits from §19 | text present |

### Order and stop points
1. E0. If the scope edit is refused, STOP (user decision).
2. E1–E10 in cell order, then E11. Run `python -m pytest tests/test_initial_ddl_contract.py -q`.
3. E13–E16; confirm E12 with `git diff`. Run the full test suite and `vv.py verify`.
4. **STOP (runtime evidence)**: the user provides an empty env (4 lakehouses with `dbo`, no tables, no schedules) and runs R1–R5 (§14). Results go to `evidence/results/`.
5. **STOP (runtime evidence)**: on DEV, run `p_apply=false` only (R6). Record the per-table lines; expect `ctrl_mng_pipeline_config` `EXISTS_OK`, plus `slv_poi_entity` `EXISTS_OK` if the node has run. Never apply on DEV. Diffs become findings.

### Tests and verification
- `tests/test_initial_ddl_contract.py`:
  - `test_param_default_false`, `test_plan_precedes_writes`
  - `test_no_destructive_sql`: excludes the verbatim-copy cells `init_cfg_partner`, `init_cfg_3p`, `init_registry_pure`, `init_seed_place_type`, `init_seed_amenity` and strips comment lines; the excluded cells must have no `spark.sql(`/`.write`/`saveAsTable`.
  - `test_table_inventory_matches_sources`: 14 tables, including `b1entitybuild` `SPEC.trg_tbl`.
  - `test_columns_match_sources`, `test_create_sql_renders`
  - `test_poi_entity_columns_derived`: §16 algorithm. Inputs: `TABLE_CONFIGS_3P` flatten for `slv_3p_poi`; `ast`-evaluated `SNAPSHOT_TECH_COLUMNS` (lib extract cell `b756d39b`), `TECH_COLUMNS`/`TECH_NAMES` (lib transform cell `9ff87eee`), `CATEGORY_COLS` (`b1entitybuild`), `EXPECTED` (`a1setupddl`). Ordered equality with spec #14.
  - `test_registry_configs_equal_create_ddl`, `test_registry_rows_valid`, `test_ref_seed_blocks_identical`
  - `test_pipeline_config_rows_match_sources`, `test_watermark_rows_match_source`
  - `test_example_patch_dual_update`: `enrddlpy` guard plus ALTER text; spec #1 has `nb_name`; `80154b61` CREATE lacks it; the first-run has no `ADD COLUMNS`.
  - `test_roles_documented`
- Commands:
  - `python -m pytest tests/test_initial_ddl_contract.py -q`
  - `python -m pytest tests -q` (existing `test_3p_l1_contract`, `test_enr_poi_contract`, `test_l1_ts_contract`, `test_poi_*` stay green)
  - `git diff --exit-code notebooks/NB_CREATE_DDL.ipynb`
  - `python scripts/vv.py verify 20261016-setup-initial-ddl-and-patch-ddl`
- Runtime: R1–R5 and the §14 SQL (`n = k`; `n` unchanged between R2 and R3), then R6 on DEV, plan only.

### Read only if needed
- §0 Status and decisions bound → E0, E12, `test_no_destructive_sql` fix
- §1 Scope, §2 Non-goals → E0, E2 exclusions
- §5.1 Tables, §5.1a `slv_poi_entity` derivation → E2, `test_poi_entity_columns_derived`
- §5.2 Seeds, §5.3 Excluded statements → E5, E6, E9
- §6 Ordering → E1–E10 cell ids
- §7 Commit boundaries, §8 Idempotency, §9 Concurrency/partial failure → E8, E9, E10
- §10.1 `init_tables`, §10.1a spec #14 → E2; §10.2 → E5; §10.3 → E7; §10.4 → E9
- §11 Alternatives → reviewer questions (copy vs `%run`, literal vs runtime-derived `slv_poi_entity`)
- §12 Observability → E7, E10
- §14 Rollout/runbook SQL, §15 Rollback → stops 4–5, `runtime-runbook.md`
- §16 Verification → E11
- §18 Naming doc text → E13, E14; §19 AGENTS/CTRL edits → E15, E16

# Architecture: 20261016-setup-initial-ddl-and-patch-ddl (round 2)

## 0. Status and decisions bound

Round 1 stopped only on U1. Round 2 binds the two recorded decisions:
- **U1 = A.** The dual-update demonstration is the existing pair. `NB_CREATE_DDL` cell `enrddlpy` holds the guarded patch `if "nb_name" not in cols: ALTER TABLE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config ADD COLUMNS (nb_name STRING)`. The first-run notebook holds `nb_name STRING` in the full CREATE of `ctrl_mng_pipeline_config`, with no ALTER. No new column is added, and **`NB_CREATE_DDL` is not edited by this task**. A contract test asserts the pair (§16).
- **U2.** `lh_vv_silver.dbo.slv_poi_entity` joins the first-run inventory as table #14. The repo has no `CREATE TABLE` literal for it. The transform lib (`ensure_target` / `target_ddl`) creates it from the `b1entitybuild` output schema plus `TECH_COLUMNS`. Its column list is therefore **derived** from repo definitions (§5.1a) and checked by a test that recomputes the derivation. No column is invented.

Round-2 corrections to round 1:
- `scope.files` is malformed: line 29–30 of `task-state.yaml` is one string that joins five paths with ` - `. E0 replaces it with a proper list.
- `test_no_destructive_sql` would fail on the verbatim `TABLE_CONFIGS_3P` copy, whose comments contain `UPDATE registry …`. It now excludes the verbatim-copy cells and strips comment lines (§16).
- Rule 7 in §18 is updated for node targets that the first-run notebook pre-creates.

## 1. Scope

- New `notebooks/NB_SETUP_INITIAL_DDL.ipynb`: the full current DDL for 14 tables plus 5 configuration seeds. Insert-only, `p_apply = "false"` by default, and self-contained apart from `%run NB_LIB_TRANSFORM_SLV_GLD`.
- `notebooks/NB_CREATE_DDL.ipynb` stays the patch notebook and is unchanged (U1 = A).
- `docs/context/02_NAMING_CONVENTION.md`: §2 table rows plus a new §2.1 (roles and agent rule).
- `AGENTS.md` §7: one sentence replaced. The file stays under 8192 bytes.
- `docs/context/CTRL_TABLES_CONTEXT.md`: header pointer, "Ghi bởi" cells, `nb_name` in the §3 DDL, and a §10 history row.
- New `tests/test_initial_ddl_contract.py`, with no Spark.
- Read-only sources, not edited: `NB_SETUP_POI_ENTITY`, `NB_SETUP_POI_AMENITY`, `NB_SLV_POI_ENTITY`, `NB_SLV_POI_AMENITY`, `NB_LIB_EXTRACT_RAWDATA` (cell `b756d39b`), and `NB_LIB_TRANSFORM_SLV_GLD` (cell `9ff87eee`). The test reads the two lib notebooks. They do not need to be in `scope.files` because they are not edited.

## 2. Non-goals

- Replacing or editing `NB_CREATE_DDL`, or restoring removed `DROP` cells.
- Any `DROP`, `DELETE`, `TRUNCATE`, `UPDATE`, `ALTER`, overwrite, or `replaceWhere` in the first-run notebook.
- Seeds from live Fabric tables.
- Other lib-created tables: `slv_pn_*` and `slv_3p_poi*` (extract `ensure_target` from the registry), and any other node target (`slv_pn_poi`, etc.). Only `slv_poi_amenity` (which has a repo literal) and `slv_poi_entity` (U2) are pre-created.
- Runtime watermark rows (`wm_e__*`, `wm_flow__*`).
- `NB_SETUP_L1_TS_AUDIT`, the K1 diagnostic `5784a286`, ctrl `TBLPROPERTIES` changes, pipeline JSON, and any extract, recompute, node, or lib edit.

## 3. Invariants

- I1: The first-run notebook issues only `CREATE SCHEMA IF NOT EXISTS`, `CREATE TABLE IF NOT EXISTS`, and `MERGE … WHEN NOT MATCHED THEN INSERT`.
- I2: When `p_apply` is not true-ish, there are zero writes. The notebook prints the DDL list and the per-seed `defined`/`to_insert` counts, then exits with `PLAN`.
- I3: Running apply N≥2 times leaves the same row set as one run. Each logical key appears exactly once.
- I4: The first-run definitions equal the repo sources: the table set, columns (CREATE plus ALTER-added `nb_name`), the derived `slv_poi_entity` columns, `TABLE_CONFIGS`, `TABLE_CONFIGS_3P`, the ref seed blocks, 50 pipeline_config rows, and 2 watermark rows. Tests enforce this.
- I5: An existing table with a column, type, nullability, or partition diff (compared by name) raises `ConfigError` in `init_plan` before any write.
- I6: `NB_CREATE_DDL.ipynb` is byte-unchanged by this task.
- I7: Seeds are repo literals only.
- I8: `AGENTS.md` stays under 8192 bytes.
- I9: The `slv_poi_entity` spec equals what `ensure_target` would create from the current `b1entitybuild` and registry: the same names, `simpleString` types, and order, all columns nullable, PROPS, no comment, and no partition. A later `run_node` therefore returns `None` from `ensure_target` (no ALTER and no `ConfigError`).

## 4. State ownership

| State | Writer | This task |
|---|---|---|
| Table existence/schema in an empty env | `NB_SETUP_INITIAL_DDL` | New |
| Schema/config changes in an existing env | `NB_CREATE_DDL` patch cells; lib `ensure_target` for node and extract targets | Rule only |
| `ctrl_mng_pipeline_config` rows | First-run (insert), historical setup cells, operator | Insert missing keys only |
| `ctrl_mng_watermark` source rows | First-run inserts `INITIALIZED`; extract owns later changes | Insert-only by `watermark_id` |
| `ctrl_cfg_schema_registry` | First-run (insert missing), `NB_CREATE_DDL` `seed_registry` (replaceWhere per source) | Insert-only |
| `ref_dictionary_place_type`, `ref_dictionary_amenities` | First-run and setup notebooks | Insert-only |
| Rows of `slv_poi_entity`, `slv_poi_amenity`, `gld_enr_*`, logs, CDC | Node or runtime notebooks | First-run creates empty tables only |
| Columns later added to `slv_poi_entity` | Transform `ensure_target` (ALTER ADD) in existing envs | The first-run spec must be updated in the same task (rule 7) |

## 5. Inventory (grain and keys)

### 5.1 Tables, in CREATE order

| # | Table | Column source | Extra folded in | Partition / props / comment |
|---|---|---|---|---|
| 1 | `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` | `NB_CREATE_DDL` `80154b61` | `nb_name STRING` (U1, from `enrddlpy` ALTER, no comment) | none |
| 2 | `lh_vv_ctrl.dbo.ctrl_mng_watermark` | `3ea73e14` (18 cols) | — | none |
| 3 | `lh_vv_ctrl.dbo.ctrl_cfg_schema_registry` | `d06c9671` (17 cols) | — | table COMMENT |
| 4 | `lh_vv_ctrl.dbo.ctrl_log_run` | `7dad05d9` | — | table COMMENT |
| 5 | `lh_vv_ctrl.dbo.ctrl_log_table_run` | `7dad05d9` | — | table COMMENT |
| 6 | `lh_vv_ctrl.dbo.ctrl_cdc_state` | `7dad05d9` | — | `PARTITIONED BY (src_tbl)`, COMMENT |
| 7 | `lh_vv_ctrl.dbo.ctrl_cdc_reject` | `7dad05d9` | — | `PARTITIONED BY (src_tbl)`, COMMENT |
| — | `CREATE SCHEMA IF NOT EXISTS lh_vv_gold.enr` | `enrddlpy` | — | — |
| 8–10 | `lh_vv_gold.enr.gld_enr_poi_info` / `_coordinate` / `_review` | `enrddlpy` `INFO_COLS`/`COORD_COLS`/`REVIEW_COLS` | — | PROPS |
| 11 | `lh_vv_silver.dbo.ref_dictionary_place_type` | `a1setupddl` | — | PROPS |
| 12 | `lh_vv_silver.dbo.ref_dictionary_amenities` | `NB_SETUP_POI_AMENITY` `c1setupddl` | — | PROPS |
| 13 | `lh_vv_silver.dbo.slv_poi_amenity` | `c1setupddl` | — | PROPS |
| 14 | `lh_vv_silver.dbo.slv_poi_entity` | Derived (§5.1a) | — | PROPS, no comment, all nullable |

PROPS = `'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'`, the same value as the sources and as the transform lib's `TABLE_PROPERTIES`.

### 5.1a Derivation of `slv_poi_entity` columns

These are the facts the derivation rests on. Each one is in the repo:
1. `slv_3p_poi` columns come from extract `target_ddl(spec)`: the active registry columns ordered by `column_order`, then `spec.tech_columns`. `slv_3p_poi` is `DOC`, which is in `SNAPSHOT_MODES`, so the tech columns are `SNAPSHOT_TECH_COLUMNS` = `_crawled_at` timestamp, `_event_id` string, `_first_seen_at` timestamp, `_last_seen_at` timestamp, `created_at` timestamp, `updated_at` timestamp (lib extract `b756d39b`). Inactive registry columns are not created (`NB_CREATE_DDL` D1 comment). `slv_3p_poi` has none today.
2. `TABLE_CONFIGS_3P` entry `slv_3p_poi` (`e9c137c5`) has 10 string columns in this order: `poi_id`, `source_name`, `source_id`, `language_code`, `poi_name`, `poi_name_normalized`, `types_json`, `subcategory_tags_json`, `operating_status`, `primary_type`.
3. `b1entitybuild` returns `*keep` (every `slv_3p_poi` column whose lower name is not in `TECH_NAMES` = `row_hash, created_at, updated_at, deleted_at`), then `business_sector`, `business_category`, `business_category_vi`. Each is STRING, either from the `ref_dictionary_place_type` struct, where `a1setupddl` defines all three as STRING, or from `F.lit("other")` / `F.lit(None).cast("string")`.
4. Transform `target_ddl`/`ensure_target` (lib `9ff87eee`, `ensure_target`) use the build fields without `row_hash`, followed by `TECH_COLUMNS` = `row_hash` string, `created_at`, `updated_at`, `deleted_at` timestamp, with `TABLE_PROPERTIES`, no NOT NULL, and no comment.

The result is 21 columns, given in §10.1a. Because types are compared by `simpleString`, a later `ensure_target` on this pre-created table finds no mismatch and nothing missing. Pre-creating a node target has a precedent in `c1setupddl`, which pre-creates `slv_poi_amenity`.

### 5.2 Seeds

| Seed | Target | Logical key | Rows | Source |
|---|---|---|---|---|
| `pipeline_config` | #1 | (`pl_name`,`src_schema`,`src_tbl`,`trg_schema`,`trg_tbl`) | 50 | `80154b61` partner VALUES (23; priority 2 if `trg_tbl LIKE 'slv_pn_product%'` else 1; `CDC`), plus 3P VALUES (9; media `dedup_order = 'display_order ASC'`), plus `enrddlpy` `EDGES` (13, with `nb_name`), plus `a1setupedges` (2), plus `c1setupedges` (3; `PL_VV_TRANS_SLV_TO_SLV_1H`, `RECOMPUTE`, priority 1, `nb_name` NULL) |
| `watermark` | #2 | `watermark_id` | 2 | `3ea73e14` VALUES |
| `registry` | #3 | (`src_schema`,`src_tbl`,`trg_schema`,`trg_tbl`,`trg_column`) | flatten(partner) + 55 | `TABLE_CONFIGS`, `TABLE_CONFIGS_3P`, flattened with `0f228dc1` functions |
| `place_type` | #11 | (`source_name`,`place_type`) | `len(SEED_ROWS)` | `a1setupseed` block |
| `amenities` | #12 | (`source_name`,`business_sector`,`amenity_group`,`amenity_raw`,`amenity`) | `len(SEED_ROWS)` | `c1setupseed` block |

`id` = `COALESCE(MAX(id),0) + seq`. It is not a business key (`02_NAMING_CONVENTION.md` §4).

### 5.3 Statements not carried into the first run

| Source | Statement | Reason |
|---|---|---|
| `502cd242` | `DELETE` of dropped 3P rows | The first run never creates those rows |
| `80154b61` tail | `UPDATE … dedup_order` | The final value is seeded |
| `0f228dc1` | `convert_arg` ALTER guard; `replaceWhere` | The column is in the CREATE; seeding is insert-only |
| `ea524452` | gold-log ALTER | The columns are in the CREATE |
| `enrddlpy` | `nb_name` ALTER | Folded into spec #1 (U1 pair) |
| `6e95fc60` / `5784a286` | D1–D7 / K1 | Replaced by `init_verify` / not DDL |
| `a1setupedges`, `c1setupedges` | `WHEN MATCHED … UPDATE` repair branch | The first run is insert-only; the rows are seeded as literals |
| `b1entitybuild` | Node logic | Only its output schema is used (§5.1a) |

## 6. Ordering (cell layout of `NB_SETUP_INITIAL_DDL`)

| # | Cell id | Content | Writes |
|---|---|---|---|
| 0 | `init_md` | Vietnamese header: role, preconditions (empty `lh_vv_ctrl`/`lh_vv_silver`/`lh_vv_gold` with `dbo`, no pipeline running), no DROP, link to 02 §2.1 | no |
| 1 | `init_param` | Tagged `parameters`: `p_apply = "false"` | no |
| 2 | `init_run` | `%run NB_LIB_TRANSFORM_SLV_GLD` | no |
| 3 | `init_tables` | `# BEGIN_INIT_TABLE_SPECS` … `# END_INIT_TABLE_SPECS` (§10.1, §10.1a) | no |
| 4 | `init_cfg_partner` | Verbatim copy of `28e2be98` | no |
| 5 | `init_cfg_3p` | Verbatim copy of `e9c137c5` | no |
| 6 | `init_registry_pure` | `# BEGIN_REGISTRY_PURE` (copied from `0f228dc1`) `# END_REGISTRY_PURE`, then `REGISTRY_SCHEMA` | no |
| 7 | `init_seed_ctrl` | `# BEGIN_INIT_CTRL_SEED` … `# END_INIT_CTRL_SEED` (§10.2) | no |
| 8 | `init_seed_place_type` | Byte-identical seed block, then `validate_seed(SEED_ROWS)`; `PLACE_TYPE_ROWS = list(SEED_ROWS)` | no |
| 9 | `init_seed_amenity` | Byte-identical seed block, then `validate_seed(SEED_ROWS)`; `AMENITY_ROWS = list(SEED_ROWS)` | no |
| 10 | `init_plan` | §10.3 | no |
| 11 | `init_ddl` | `CREATE SCHEMA IF NOT EXISTS lh_vv_gold.enr`; for each of the 14 specs, `with_retry(lambda: spark.sql(create_sql(spec)))`; re-check all 14 schemas | DDL |
| 12 | `init_seed_write` | §10.4: five MERGEs, pipeline_config → watermark → registry → place_type → amenities | seeds |
| 13 | `init_verify` | dup = 0 and missing = 0 per seed; drift printed; cross-checks (registry pairs ↔ pipeline_config; one source watermark per active extract source) | no |
| 14 | `init_exit` | Print and `notebookutils.notebook.exit(json.dumps(summary))` | no |

Cells 8 and 9 rebind `SEED_ROWS`/`validate_seed`. Each binding to `PLACE_TYPE_ROWS`/`AMENITY_ROWS` stays in the same cell, right after its END marker.

## 7. Transaction and commit boundaries

- Each CREATE is one catalog plus Delta commit. There is no cross-table atomicity, and none is needed because every step is idempotent.
- Each seed is one MERGE (one commit) into one table, so a table holds either none or all of the rows missing at the start of an attempt.
- The schema re-check runs after all CREATEs and before any seed.
- Commit order: tables 1–14, then seeds in §6 order. There are no FKs. The order only fixes `id` ranges and keeps runs reproducible.

## 8. Idempotency

- DDL uses `IF NOT EXISTS`. An existing table must match by name (`schema_diff`).
- Seeds use `MERGE … ON key WHEN NOT MATCHED THEN INSERT` with no `WHEN MATCHED`. A rerun inserts 0 rows and changes none.
- `id` base is read inside the retried function, and the new ids (`base + seq`) are unique. A clean env gets ids 1–50.
- `with_retry` around each MERGE: if a commit succeeded but its acknowledgement was lost, the retry inserts 0 rows.
- `inserted` = missing before minus missing after; missing after must be 0.
- `slv_poi_entity` is created empty. The first `run_node` sees `ensure_target → None` and performs a normal MERGE. `CREATE TABLE` is in `DEFAULT_NON_DATA_OPS`, so the empty-table commit does not count as a data change for edge watermarks.

## 9. Concurrency, retry, recovery, partial failure

- Precondition (runbook): no pipeline, extract, NB_00, or node runs during apply. The notebook cannot detect this.
- Concurrent applies: CREATE races fail with "already exists" and a rerun clears them. Concurrent insert-only MERGEs conflict, and the retry inserts 0. No duplicates in either case.
- A `run_node` racing the `slv_poi_entity` CREATE: whichever creates first wins, both produce the same DDL (I9), and the loser's `ensure_target` sees the table. This is excluded by the precondition anyway.
- Failure after k CREATEs: a rerun creates the rest. Failure between seeds: a rerun fills only the tables still missing keys.
- `ConfigError` (validation, schema diff, existing duplicate keys) is raised in `init_plan`, before any write, and is not retried.
- Residual risk: a catalog entry left without a Delta log after an aborted CREATE. `spark.table` fails, and recovery is manual through the runbook. The notebook never drops anything.
- Older env missing a patched column: the plan raises `thiếu <col>`. Run the `NB_CREATE_DDL` patches first. On DEV, `slv_poi_entity` columns can differ if DEV's `slv_3p_poi` registry differs from the repo. The plan then reports the diff and does not write.

## 10. Implementation details

### 10.1 `init_tables` (pure)

```python
# BEGIN_INIT_TABLE_SPECS
PROPS = "'delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true'"
# Mỗi bảng: định nghĩa đầy đủ hiện hành. Cột thêm sau ở NB_CREATE_DDL ghi thẳng vào đây.
# cols: (tên, kiểu Spark SQL kèm NOT NULL nếu có, comment hoặc None)
TABLE_SPECS = [
    {"fq": "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config", "partition": None, "comment": None, "props": None,
     "cols": [("id", "BIGINT", None), ("pl_name", "STRING", None),  # ... every column of 80154b61 ...
              ("nb_name", "STRING", None)]},
    # ... specs #2-#13 in §5.1 order, columns/comments copied exactly ...
    # #14 slv_poi_entity: §10.1a
]


def _q(text):
    return text.replace("\\", "\\\\").replace("'", "\\'")


def create_sql(spec):
    body = ",\n    ".join(f"`{n}` {t}" + (f" COMMENT '{_q(c)}'" if c else "") for n, t, c in spec["cols"])
    sql = f"CREATE TABLE IF NOT EXISTS {spec['fq']} (\n    {body}\n) USING DELTA"
    if spec["partition"]:
        sql += f"\nPARTITIONED BY ({', '.join(spec['partition'])})"
    if spec["comment"]:
        sql += f"\nCOMMENT '{_q(spec['comment'])}'"
    if spec["props"]:
        sql += f"\nTBLPROPERTIES ({spec['props']})"
    return sql


def schema_diff(spec, fields, partition_cols):
    """So theo tên (không theo vị trí): thiếu / thừa / lệch kiểu hoặc nullability / lệch partition."""
    want = {n.lower(): (t.replace(" NOT NULL", "").lower(), "NOT NULL" not in t) for n, t, _ in spec["cols"]}
    got = {f.name.lower(): (f.dataType.simpleString(), f.nullable) for f in fields}
    issues = [f"thiếu {n}" for n in want if n not in got]
    issues += [f"thừa {n}" for n in got if n not in want]
    issues += [f"{n}: có {got[n]}, cần {want[n]}" for n in want if n in got and got[n] != want[n]]
    if [p.lower() for p in partition_cols] != [p.lower() for p in (spec["partition"] or [])]:
        issues.append(f"partition: có {list(partition_cols)}, cần {spec['partition']}")
    return issues
# END_INIT_TABLE_SPECS
```

Partition columns at runtime come from `DESCRIBE DETAIL … partitionColumns`. Types in the specs must be written so that `lower()` equals `simpleString()`, for example `DECIMAL(18,2)` with no space.

### 10.1a `slv_poi_entity` spec (last entry of `TABLE_SPECS`)

```python
    # [THÊM 16/10] Bảng node: cột = cột build b1entitybuild + TECH_COLUMNS lib transform (giống ensure_target).
    # Registry slv_3p_poi đổi cột -> sửa ở đây (tests/test_initial_ddl_contract.py kiểm tra).
    {"fq": "lh_vv_silver.dbo.slv_poi_entity", "partition": None, "comment": None, "props": PROPS,
     "cols": [("poi_id", "STRING", None), ("source_name", "STRING", None), ("source_id", "STRING", None),
              ("language_code", "STRING", None), ("poi_name", "STRING", None),
              ("poi_name_normalized", "STRING", None), ("types_json", "STRING", None),
              ("subcategory_tags_json", "STRING", None), ("operating_status", "STRING", None),
              ("primary_type", "STRING", None),
              ("_crawled_at", "TIMESTAMP", None), ("_event_id", "STRING", None),
              ("_first_seen_at", "TIMESTAMP", None), ("_last_seen_at", "TIMESTAMP", None),
              ("business_sector", "STRING", None), ("business_category", "STRING", None),
              ("business_category_vi", "STRING", None),
              ("row_hash", "STRING", None), ("created_at", "TIMESTAMP", None),
              ("updated_at", "TIMESTAMP", None), ("deleted_at", "TIMESTAMP", None)]},
```

### 10.2 `init_seed_ctrl` (pure)

```python
# BEGIN_INIT_CTRL_SEED
_FL00, _ENR, _SLV1H = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00", "PL_VV_TRANS_SLV_TO_ENR_15P", "PL_VV_TRANS_SLV_TO_SLV_1H"
_B, _S, _E = "lh_vv_bronze.dbo", "lh_vv_silver.dbo", "lh_vv_gold.enr"
# (pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)
PIPELINE_CONFIG_ROWS = [
    (_FL00, _B, "partner_raw_data", _S, "slv_pn_products", 1, 2, "CDC", None, None, None),
    # ... 23 partner rows (80154b61 order), 9 3P rows (80154b61 order),
    #     13 ENR rows (EDGES order, src_schema _S, nb_name from EDGES),
    #     2 slv_poi_entity rows (a1setupedges seq order), 3 slv_poi_amenity rows (c1setupedges order) ...
]
# (watermark_id, src_schema, src_tbl, watermark_column, status, flow_name, watermark_sequence)
WATERMARK_ROWS = [
    ("wm_transform_partner_raw_data", _B, "partner_raw_data", "EventProcessedUtcTime", "INITIALIZED",
     "NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV", -1),
    ("wm_transform_brz_3rd_crawler_poi_stream", _B, "brz_3rd_crawler_poi_stream", "crawled_at", "INITIALIZED",
     "NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV", -1),
]
# END_INIT_CTRL_SEED
```

The other watermark columns are NULL, and `updated_at = current_timestamp()`, as in `3ea73e14`.

### 10.3 `init_plan` (read-only, in order)

1. `apply = to_bool(p_apply)`.
2. Pure validation, collecting every error into one `ConfigError`: `validate_rows` per registry source; registry key uniqueness across both sources; pipeline_config key uniqueness; unique `watermark_id`; unique `fq` across the 14 specs.
3. Lakehouse precondition: `SHOW TABLES IN` each of `lh_vv_ctrl.dbo`, `lh_vv_silver.dbo`, `lh_vv_gold.dbo`. An exception becomes `ConfigError("thiếu lakehouse/schema …")`.
4. For each spec: if `table_exists`, run `schema_diff` and collect issues. Print `fq`, `CREATE` or `EXISTS_OK`, and `create_sql(spec)`.
5. Create the temp views `_v_setup_pipeline_config` (with `seq`), `_v_setup_watermark`, `_v_setup_registry`, `_v_setup_place_type`, `_v_setup_amenities`. For each seed: `defined`, `missing` (LEFT ANTI on the key, or `defined` when the table is absent), and `dup_keys`.
6. Raise `ConfigError` on any schema issue or `dup_keys > 0`.
7. Print `seed=<name> defined=<n> to_insert=<missing>`.
8. If `not apply`: `notebookutils.notebook.exit(json.dumps({"status": "PLAN", "p_apply": False, "tables": [...], "seeds": {...}}))`.

### 10.4 `init_seed_write` (pattern)

```python
def _merge_pipeline_config():
    base = int(spark.sql(f"SELECT COALESCE(MAX(id), 0) AS m FROM {PC_FQ}").first()["m"])
    spark.sql(f"""
        MERGE INTO {PC_FQ} AS t
        USING _v_setup_pipeline_config AS s
        ON t.pl_name = s.pl_name AND t.src_schema = s.src_schema AND t.src_tbl = s.src_tbl
           AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
        WHEN NOT MATCHED THEN INSERT
            (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority,
             load_mode, align_path, dedup_order, nb_name)
        VALUES ({base} + s.seq, s.pl_name, s.src_schema, s.src_tbl, s.trg_schema, s.trg_tbl, s.is_active,
                s.priority, s.load_mode, s.align_path, s.dedup_order, s.nb_name)
    """)
```

The other four seeds have the same shape without `base`. Watermark: `ON watermark_id`. Registry: the 5-column key, inserting all 17 columns by name. place_type and amenities: the ON/INSERT of `a1setupmerge`/`c1setupmerge`. Each is called as `with_retry(fn, "seed <name>")`. Drift (key matches, non-key columns differ via `<=>`) is printed and never corrected.

## 11. Alternatives and trade-offs

| Choice | Selected | Rejected | Why |
|---|---|---|---|
| Definition source | Self-contained copy plus equality tests | `notebook.run` of the sources; shared `%run` library | `notebook.run` fails on an empty env (`c1setupplan` reads pipeline_config; `NB_CREATE_DDL` has DELETE/ALTER and no `p_apply`). The shared library restructures `NB_CREATE_DDL` and breaks the existing tests that read its cells |
| Seed semantics | Insert-only plus a drift report | Upsert to canonical values | An upsert would silently revert operator changes and break I1 |
| Commit unit | One MERGE per table | One per source group | Fewer partial states |
| Schema check | By name | By position | ALTER-added columns sit at the end in older envs |
| `slv_poi_entity` DDL | Literal spec derived from the lib, with a derivation test | (a) leave it to `ensure_target` at runtime; (b) compute the StructType at runtime from `TABLE_CONFIGS_3P` plus copies of the lib constants | (a) violates U2. (b) copies lib constants into the notebook and hides the DDL from the plan print. A literal plus a test is visible in the plan and fails CI on drift |
| U1 demonstration | Existing `nb_name` pair (A) | New column (B) | User decision |
| Rule location | 02 §2.1 plus one AGENTS sentence | Full rule in AGENTS; a new `.cursor` rule | The 8 KB limit; config the user did not request |

## 12. Observability

- Plan: the per-table action and CREATE text (14), per-seed `defined`/`to_insert`, and the PLAN exit JSON.
- Apply: per-seed `inserted` and `drift`, verify results, and the exit JSON `{"status":"SUCCESS","tables":[…14],"seeds":{name:{"defined","inserted","drift"}}}`.
- Delta `DESCRIBE HISTORY`: a rerun MERGE shows `numTargetRowsInserted = 0`.
- No `ctrl_log_run` row, the same as the existing `NB_SETUP_*`.

## 13. Security

Not applicable: no credentials or personal data. The SQL uses repo literals only, and `p_apply` is read only through `to_bool`.

## 14. Rollout

1. E0 (fix `scope.files`), then E1–E11 and E13–E16, then local tests.
2. Runtime proof in an **empty environment** that the user provides (lakehouses `lh_vv_bronze`, `lh_vv_ctrl`, `lh_vv_silver`, `lh_vv_gold` with `dbo`, no tables, no schedules):
   - R1: `p_apply=false`. PLAN, 14 × `CREATE`, `to_insert = defined`, and `SHOW TABLES` shows nothing created.
   - R2: `p_apply=true`. SUCCESS, 14 tables, `inserted = defined`, `drift = 0`.
   - R3: `p_apply=true` again. `inserted = 0`, `drift = 0`.
   - R4: the SQL below after R2 and R3: `n = k`, and `n` is unchanged.
   - R5: `p_apply=false`. 14 × `EXISTS_OK`, `to_insert = 0`.
3. R6 (DEV, read-only, dual-update proof for U1 and the U2 derivation): run `p_apply=false` on DEV and record the per-table lines. Expected: `ctrl_mng_pipeline_config EXISTS_OK`, which proves the patched env (`enrddlpy` ALTER) matches the full definition, and `slv_poi_entity EXISTS_OK` if the node has run on DEV. If DEV reports diffs elsewhere, the plan raises after printing, with no writes. Record the diffs as findings and do not apply. If `slv_poi_entity` is absent on DEV, record "not provable on DEV". R2 plus the test remain the proof.

```sql
SELECT 'pipeline_config' AS t, COUNT(*) AS n, COUNT(DISTINCT pl_name, src_schema, src_tbl, trg_schema, trg_tbl) AS k FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config
UNION ALL SELECT 'watermark', COUNT(*), COUNT(DISTINCT watermark_id) FROM lh_vv_ctrl.dbo.ctrl_mng_watermark
UNION ALL SELECT 'registry', COUNT(*), COUNT(DISTINCT src_schema, src_tbl, trg_schema, trg_tbl, trg_column) FROM lh_vv_ctrl.dbo.ctrl_cfg_schema_registry
UNION ALL SELECT 'place_type', COUNT(*), COUNT(DISTINCT source_name, place_type) FROM lh_vv_silver.dbo.ref_dictionary_place_type
UNION ALL SELECT 'amenities', COUNT(*), COUNT(DISTINCT source_name, business_sector, amenity_group, amenity_raw, amenity) FROM lh_vv_silver.dbo.ref_dictionary_amenities;
```

## 15. Rollback and forward recovery

- Code: revert the commit. All changes are additive, and `NB_CREATE_DDL` is untouched.
- Empty env: forward recovery is to rerun apply. A full undo is for the operator to remove that env's tables using runbook steps only, since they hold no data.
- Apply run by mistake on a non-empty env: only missing tables (empty) and missing rows are added. Undo with `RESTORE TABLE … TO VERSION AS OF <pre-MERGE version>`, as runbook steps.
- A wrong `slv_poi_entity` spec found after R2 in the empty env: the table is empty, so the operator removes it (runbook), fixes the spec, and reruns. In an env where the node has written rows, there is no DROP. Use a forward fix through an `NB_CREATE_DDL` patch.

## 16. Verification (local)

`tests/test_initial_ddl_contract.py` (JSON-loads the notebooks the way `tests/test_3p_l1_contract.py` does; no Spark):
- `test_param_default_false`: the `parameters` cell is exactly `p_apply = "false"\n`.
- `test_plan_precedes_writes`: cell order `init_param < init_plan < init_ddl < init_seed_write`. Cells before `init_plan` contain no `spark.sql(`, `.write`, or `saveAsTable`. `init_plan` has `if not apply:` followed by `notebookutils.notebook.exit`.
- `test_no_destructive_sql`: scan the code cells except `init_cfg_partner`, `init_cfg_3p`, `init_registry_pure`, `init_seed_place_type`, `init_seed_amenity`, with comment-only lines removed. Fail on `DROP `, `DELETE FROM`, `TRUNCATE`, `ALTER TABLE`, `UPDATE `, `WHEN MATCHED`, `replaceWhere`, `mode("overwrite")`, or `INSERT INTO`. Every `MERGE INTO` must be followed by `WHEN NOT MATCHED THEN INSERT`. The excluded cells must contain no `spark.sql(`, `.write`, or `saveAsTable`.
- `test_table_inventory_matches_sources`: the set of spec `fq` values equals every `CREATE TABLE IF NOT EXISTS (lh_vv_\w+\.\w+\.\w+)` in `NB_CREATE_DDL`, `NB_SETUP_POI_ENTITY`, and `NB_SETUP_POI_AMENITY`, plus the `enrddlpy` `TABLES` keys, plus `lh_vv_silver.dbo.` + `SPEC.trg_tbl` of `b1entitybuild` (14 in total).
- `test_columns_match_sources`: tables #1–#13 match their source CREATE columns and types (plus `nb_name` for #1); partitions match for both cdc tables.
- `test_poi_entity_columns_derived`: recompute §5.1a.
  - Exec `REGISTRY_PURE` plus `TABLE_CONFIGS_3P`.
  - Take the rows `trg_tbl == "slv_3p_poi"` with `is_active`, sorted by `column_order`, as (`trg_column`, `data_type`).
  - Use `ast` to evaluate only the assignments `AUDIT_COLUMNS`, `SNAPSHOT_TECH_COLUMNS` (lib extract cell `b756d39b`); `TECH_COLUMNS`, `TECH_NAMES` (lib transform cell `9ff87eee`); `CATEGORY_COLS` (`b1entitybuild`); and `EXPECTED` (`a1setupddl`, for the category types).
  - Expected = [c for c in registry + SNAPSHOT_TECH_COLUMNS if name not in TECH_NAMES] + category columns + TECH_COLUMNS.
  - Assert ordered equality of (name, lower type) with spec #14, no `NOT NULL`, comments None, `props == PROPS`, partition None.
  - Assert that `b1entitybuild` still contains `keep = [c for c in src.columns if c.lower() not in TECH_NAMES]` and `return out.select(*keep, pick("business_sector"`.
- `test_create_sql_renders`: every spec renders `CREATE TABLE IF NOT EXISTS` with all its columns. `PARTITIONED BY (src_tbl)` appears only for the two cdc tables.
- `test_registry_configs_equal_create_ddl`, `test_registry_rows_valid` (3P flatten = 55 rows, keys unique), `test_ref_seed_blocks_identical`, `test_pipeline_config_rows_match_sources` (50 rows), `test_watermark_rows_match_source` (2 rows).
- `test_example_patch_dual_update` (U1 = A):
  - `enrddlpy` contains `if "nb_name" not in cols:` and `ALTER TABLE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config ADD COLUMNS (nb_name STRING)`.
  - Spec #1 contains `("nb_name", "STRING", None)`.
  - The `80154b61` CREATE has no `nb_name`, which proves the patch-only origin.
  - The first-run notebook contains no `ADD COLUMNS`.
- `test_roles_documented`: 02 has `### 2.1` naming both notebooks. `AGENTS.md` contains `NB_SETUP_INITIAL_DDL` and is under 8192 bytes.

Commands: `python -m pytest tests/test_initial_ddl_contract.py -q`, `python -m pytest tests -q`, and `python scripts/vv.py verify 20261016-setup-initial-ddl-and-patch-ddl`. Also `git diff --exit-code notebooks/NB_CREATE_DDL.ipynb` (I6).

## 17. User decisions

Resolved: U1 = A and U2 (see `decision.md`). There are no open decisions. Runtime prerequisite (not an architecture blocker): the user provides an empty environment for R1–R5 and DEV access for R6.

## 18. Exact text for `docs/context/02_NAMING_CONVENTION.md`

In the §2 table, replace the `NB_CREATE_DDL` row and add one row after it:

```
| `NB_SETUP_INITIAL_DDL` | Dựng 1 lần môi trường trống: DDL đầy đủ + seed cấu hình, chỉ thêm. Mặc định chỉ in (`p_apply = false`). Xem §2.1 | — |
| `NB_CREATE_DDL` | Patch DDL / seed cho môi trường đã có bảng. Mỗi yêu cầu mới = 1 cell ở cuối. Xem §2.1 | — |
```

Insert after the paragraph "Notebook cũ (không đổi tên): …" and before `## 3. Pipeline`:

```
### 2.1 Hai notebook DDL: dựng môi trường trống và patch

| Notebook | Chứa gì | Chạy ở đâu |
|---|---|---|
| `NB_SETUP_INITIAL_DDL` | Định nghĩa đầy đủ hiện hành: `CREATE TABLE IF NOT EXISTS` mọi bảng có DDL trong repo (cột thêm sau đã gộp vào `TABLE_SPECS`) và seed cấu hình (`pipeline_config`, watermark nguồn, registry, ref). Chỉ `MERGE … WHEN NOT MATCHED THEN INSERT`, không sửa dòng đã có | Môi trường chưa có bảng. Chạy lại không nhân đôi dòng |
| `NB_CREATE_DDL` | Cell cũ giữ làm lịch sử. Mỗi yêu cầu mới thêm cell patch ở cuối, chỉ chứa thay đổi đó | Môi trường đang có bảng |

Luật cho mọi yêu cầu DDL hoặc `INSERT` cấu hình mới (agent bắt buộc):
1. Sửa cả hai notebook trong cùng task.
2. `NB_SETUP_INITIAL_DDL`: sửa định nghĩa tại chỗ (cột vào `TABLE_SPECS`, dòng vào danh sách seed). Không thêm `ALTER`, `UPDATE`, `DELETE`, `DROP`, overwrite.
3. `NB_CREATE_DDL`: thêm 1 markdown `[THÊM dd/mm] <task-id>` và 1 cell code ở cuối. Cell tự chứa, chạy lại không đổi kết quả: `ALTER TABLE … ADD COLUMNS` chỉ khi cột chưa có; dòng cấu hình bằng `MERGE` / `INSERT … WHERE NOT EXISTS` theo khoá logic; `UPDATE` phải có điều kiện giá trị đang khác. Kiểm tra sau patch chỉ xét phần patch thêm, không so toàn bộ schema. Ví dụ: cột `nb_name` (cell `enrddlpy` có `ALTER` khi chưa có cột; `NB_SETUP_INITIAL_DDL` có `nb_name` trong CREATE).
4. Không sửa, không xoá cell cũ của `NB_CREATE_DDL`; không đưa lại cell `DROP` đã bỏ. Ngoại lệ: `TABLE_CONFIGS` / `TABLE_CONFIGS_3P` là trạng thái đầy đủ của registry theo nguồn. Sửa giống hệt ở cả hai notebook, rồi chạy lại cell seed registry của nguồn đó trong `NB_CREATE_DDL`.
5. Không `DROP` bảng đã có dữ liệu ở cả hai notebook. Cột thêm vào bảng đã có phải cho phép NULL.
6. Seed lấy từ định nghĩa trong repo, không `INSERT … SELECT` từ bảng Fabric đang chạy.
7. Bảng do lib tự tạo khi chạy (`slv_pn_*`, `slv_3p_poi*` theo registry; node L2 / gold qua `ensure_target`) không có DDL ở hai notebook. Ngoại lệ: `slv_poi_amenity`, `slv_poi_entity` có DDL trong `NB_SETUP_INITIAL_DDL`, cột phải giống hệt cột `ensure_target` tạo (cột build + `TECH_COLUMNS`). Đổi cột build hoặc đổi registry `slv_3p_poi` thì sửa `TABLE_SPECS` cùng task; môi trường đã có bảng thì `ensure_target` tự thêm cột, không cần cell patch.
8. Khối seed `BEGIN_PLACE_TYPE_SEED` / `BEGIN_AMENITY_SEED` giữ giống hệt giữa `NB_SETUP_POI_*` và `NB_SETUP_INITIAL_DDL`. `tests/test_initial_ddl_contract.py` kiểm tra hai notebook khớp nguồn; thêm bảng mới thì cập nhật nguồn của test.
```

## 19. Exact edits for `AGENTS.md` and `docs/context/CTRL_TABLES_CONTEXT.md`

- `AGENTS.md` §7, the "Notebook roles" bullet: replace `` `NB_CREATE_DDL` creates the control tables. `` with `` `NB_SETUP_INITIAL_DDL` builds an empty environment and `NB_CREATE_DDL` patches an existing one; every DDL or configuration-insert change updates both (`docs/context/02_NAMING_CONVENTION.md` §2.1). ``. The file must stay under 8192 bytes.
- CTRL line 4: `> DDL + seed đầy đủ cho môi trường trống: `notebooks/NB_SETUP_INITIAL_DDL.ipynb`. Patch cho môi trường đã có bảng: `notebooks/NB_CREATE_DDL.ipynb` (`02_NAMING_CONVENTION.md` §2.1).`
- CTRL §1 table: row 1 "Ghi bởi" becomes `Tay / `NB_SETUP_INITIAL_DDL` / `NB_CREATE_DDL``; row 3 becomes `Tay (seed `NB_SETUP_INITIAL_DDL`, cell seed `NB_CREATE_DDL`)`.
- CTRL §3 DDL block: add `,` after the `dedup_order` line, add `    nb_name     STRING` before `) USING DELTA;`, and replace line 70 (`-- Tuỳ chọn (chưa tạo): nb_name …`) with `-- [THÊM 13/10] nb_name: notebook của node khi khác NB_<UPPER(trg_tbl)>; NULL = suy từ trg_tbl. Môi trường cũ: ALTER ở cell enrddlpy`.
- CTRL §10: add the row `| 16/10 | Tách `NB_SETUP_INITIAL_DDL` (dựng môi trường trống, chỉ thêm; gồm `slv_poi_amenity`, `slv_poi_entity`) khỏi `NB_CREATE_DDL` (patch) |`.
