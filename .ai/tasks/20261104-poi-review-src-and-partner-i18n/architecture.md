RESULT: PASS

## Main brief

### Decision
- Partner N6 is driven by the live `vi` i18n row with a LEFT JOIN to the live service row. `id` is the USING key (`= business_service_id`), so the `poi_id` and `source_id` expressions are unchanged. `name` and `amentities` are coalesced, and hours, holidays, and main_category are read from the coalesced block. The node-stop rule is removed; idempotency does not need it (§9).
- `gld_srv_poi_review` reads `slv_3p_poi_review` with a LEFT JOIN to rating. No `lang`. `title` is a NULL string. `review_text = text`. Its multi_lang ctrl edge goes to `is_active = 0`, because the lib rejects an active edge with no role.
- `gld_enr_poi_info` drops three columns, their builders, and their checks. `cost` stays.
- Existing environments are migrated by two new `NB_CREATE_DDL` cells, one flow lock each. The setup seed is edited for empty environments only (it is insert-only).
- Physical `DROP COLUMNS` is a manual runbook step behind user stop S1, outside the code. It is mandatory for `gld_enr_poi_info` (APPEND position check) and optional for srv `lang`.

### Invariants Main must preserve
- All `gld_enr_poi_review` edges have `is_active = 0` in the `init_seed_ctrl` seed and after `rvi18nenrpy` runs.
- `gld_srv_poi_review` active edges are exactly `slv_3p_poi_review` and `slv_3p_poi_rating`. `SPEC.inputs == {"review": "slv_3p_poi_review", "rating": "slv_3p_poi_rating"}`, `required_inputs == ("review",)`.
- srv `OUT_COLS` + `row_hash, created_at, updated_at, deleted_at` == `rvi18ngldpy` `REVIEW_COLS` names == setup spec. No `lang`.
- Info select aliases + `created_at, updated_at` == `rvi18nenrpy` `INFO_COLS` names == setup spec (37 columns). `cost` is present. With comments stripped, `\b(time_to_spend|best_time|cost_vnd)\b` does not appear in cell `36415d3b`.
- `_partner`: `vi.join(svc, "id", "left")`. `F.coalesce("_vi_name", "_svc_name")` and `F.coalesce("_vi_am", "_svc_am")`. `_mc`, `_hours`, and `_holiday` are all derived from `_am`. No `if live and not agg["rows"]`.
- In `_partner`, service-only columns come from the `svc` select, so they are NULL when the service does not join. The duplicate partner `place_type` check stays before the join. Both ambiguity raises stay.
- `uuid_md5(F.col("id"), F.lit(PARTNER))` and `"source_id": F.col("id")` are unchanged. The `_google` def is byte-identical.
- Migration cells, comments stripped: none of `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE`, `columnMapping`, `ALTER TABLE`, `INSERT INTO`, `SET is_active = 1`. Every precondition is checked before the first `_refresh_lock()`. The UPDATE is skipped when the edges are already 0.
- History cells (`enrddlpy`, `enrflagpy`, `srvrevpy`, …) are not edited.
- Setup `PIPELINE_CONFIG_ROWS` keeps 69 rows. Only three rows change `is_active` from 1 to 0.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb | `b1entitybuild` def `_partner` | Head through `base` per doc §14.1. Metrics block per §14.1. Delete the node-stop raise. `cols` and `SPEC` unchanged | Tests in rows 13–14 pass |
| 2 | notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb | `b1entitymd` | Partner phrase per §14.1 | Text present |
| 3 | notebooks/NB_GLD_SRV_POI_REVIEW.ipynb | `srvrvbuild` | Constants and `build` per §14.2. `SPEC` inputs and required_inputs | `test_review_*` pass |
| 4 | notebooks/NB_GLD_SRV_POI_REVIEW.ipynb | `srvrvmd` | Text per §14.2 | No `slv_enr_poi_review_multi_lang INNER` |
| 5 | notebooks/NB_ENR_POI_INFO.ipynb | `36415d3b` (`BEGIN_INFO_PURE`, the four defs, `build` select, `SPEC` checks) | Per §14.3 | `test_info_select_matches_ddl` and `test_info_removed_columns_absent` pass |
| 6 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` specs `gld_enr_poi_info`, `gld_srv_poi_review` | Delete 3 tuples and the `lang` tuple | `test_columns_match_sources` passes |
| 7 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` | Three rows get `is_active` 0, plus `[SỬA 04/11]` comments | `test_pipeline_config_rows_match_sources` passes (69 rows) |
| 8 | notebooks/NB_CREATE_DDL.ipynb | end: `rvi18nenrmd`, `rvi18nenrpy` | Append per §14.5 and §14.5.1 | `test_review_flow_inactive_cell` passes |
| 9 | notebooks/NB_CREATE_DDL.ipynb | end: `rvi18ngldmd`, `rvi18ngldpy` | Append per §14.5.2 | `test_review_source_patch_cell` passes. Ids end with the 4 new ids |
| 10 | docs/context/mapping_gld_srv_poi_review.md | whole file | Save the FILE block verbatim | `test_review_mapping_targets` passes |
| 11 | docs/context/gld_enr_poi_info_review.md | whole file | Save the FILE block verbatim | No 3-column rows. Review status row present |
| 12 | docs/context/01_DATA_MODEL.md, docs/context/03_OPERATOR_GUIDE.md | N6 row, §7, §8 / §2.1, §2.2, §2.7 | Text per §14.6 | Grep shows `[SỬA 04/11]` in each anchor |
| 13 | tests/test_poi_entity_contract.py | `test_entity_node_contract`, `test_entity_detail_columns`, `test_create_ddl_patch`; new `test_partner_i18n_driving` | Assert the new `vi`, `svc`, `base` text; `$.policies.holiday_exceptions` in `base`; ids shifted by 4; no `svc.join(vi`; no stop message; `ctx.warn("partner_without_service"` | Pass |
| 14 | tests/test_enr_poi_contract.py | `INFO` → new 37 + `INFO_OLD` (today's); `test_gold_ddl_matches_mapping`; delete `test_info_labels_match_mapping`, `test_best_time_pattern`; `test_info_patch_cell_guards` ids; new `test_info_removed_columns_absent`, `test_review_flow_inactive_cell` | Per §14.7 and invariants 1, 4, 8 | Pass |
| 15 | tests/test_gld_srv_poi_contract.py | `test_review_node_spec` (exactly one `.cast(`, the title literal), `test_review_build_columns_match_ddl` (use `rvi18ngldpy`), `test_info_rating_patch` ids; new `test_review_text_and_title_rule`, `test_review_source_patch_cell` | Per §14.7 | Pass |
| 16 | tests/test_initial_ddl_contract.py | `test_columns_match_sources`, `test_flag_patch_create_matches_init`, `test_gld_srv_review_patch_create_matches_init`, `test_pipeline_config_rows_match_sources`, `test_gld_srv_review_patch_guards` (seed ML edge 0), `test_enr_initial_edge_state` (`review_active == set()`); new `test_review_edges_inactive_in_seed` | Newest contract from the new cells. History cells stay as they are | Pass |

### Order and stop points
1. Rows 5, 6, 8 (info): code, setup spec, and cell A together, then row 14. Run the tests.
2. Rows 3, 4, 6 (srv), 9, then row 15. Run the tests.
3. Rows 1, 2, then row 13.
4. Row 7 (seed), then row 16. Run the full suite.
5. Rows 10–12 (docs). The mapping and enrich contract must be done before review.
6. STOP (evidence, before review closes): paste the pytest output of all four files and the full suite.
7. STOP S1 (user decision, before any environment rollout; not blocking implementation or review): run probes P1 (TBLPROPERTIES / DESCRIBE DETAIL on both gold tables) and P2 (external readers of `gld_srv_poi_review.lang`). The user then approves (a) `DROP COLUMNS` on `gld_enr_poi_info`, which is required; if declined, return to the user, because the request cannot be met. The user also decides (b) whether to drop srv `lang`, which is optional.
8. Rollout (runtime, not this task's acceptance): pause the triggers, deploy, run the R2 SQL, run `rvi18nenrpy` then `rvi18ngldpy`, resume (doc §15). Deploy must come before the srv `lang` drop.

### Tests and verification
- `python -m pytest tests/test_enr_poi_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py -q`
- `python -m pytest -q`
- New tests: `test_partner_i18n_driving`, `test_info_removed_columns_absent`, `test_review_flow_inactive_cell`, `test_review_text_and_title_rule`, `test_review_source_patch_cell`, `test_review_edges_inactive_in_seed`.
- Deleted tests: `test_info_labels_match_mapping`, `test_best_time_pattern`.
- Static: `git diff` shows `_google` unchanged and no edits in history cells of `NB_CREATE_DDL`.
- Next gate: `python scripts/vv.py run-gate 20261104-poi-review-src-and-partner-i18n`.

### Read only if needed
- §3 Resolution of model-design conflicts → rows 1, 3, 5, 10 (why `source_id`, uniqueness, types, and checks were decided without a new model run)
- §8 Alternatives → rows 7, 8, 9 (migration cells vs seed; two locks; DROP COLUMNS via S1)
- §9 Idempotency, §10 Partial failure → rows 1, 8, 9 (removing the stop rule; fail-closed interleavings)
- §11 Observability → rows 1, 3, 5 (metric and QG key renames)
- §14.1–14.5.2 code → rows 1, 3, 5, 8, 9
- §14.6 docs text → row 12
- §14.7 test rules → rows 13–16
- §15 Rollout, §15.1 R2 SQL, §16 Rollback → stop S1, rollout

# Architecture: 20261104-poi-review-src-and-partner-i18n

Risk high/high. Reviewers: sql-data-reviewer, state-correctness-reviewer, spark-runtime-reviewer. Grain and keys come from `model-design.md` `## Entities and grain` and `## Keys`. This document resolves the open items in `model-design.md` `## Conflicts and questions` that it can resolve from repository evidence (§3). It adds no table, column, or key.

## 1. Scope

- `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild` def `_partner` (and markdown `b1entitymd`). The driving set becomes the live `vi` row of `slv_pn_business_service_i18ns`, with a LEFT JOIN to the live `slv_pn_business_services` row. The Google branch is unchanged.
- `NB_GLD_SRV_POI_REVIEW` cell `srvrvbuild` (and markdown `srvrvmd`). Reads `slv_3p_poi_review` with a LEFT JOIN to `slv_3p_poi_rating`. `lang` is dropped, `title` is NULL, and `review_text = text`.
- `NB_ENR_POI_INFO` cell `36415d3b`. Drops `time_to_spend`, `best_time`, `cost_vnd`, their builders, and the checks on them. `cost` stays.
- `NB_SETUP_INITIAL_DDL`. Cell `init_tables` drops the three columns from the `gld_enr_poi_info` spec and `lang` from the `gld_srv_poi_review` spec. Cell `init_seed_ctrl` sets `is_active = 0` on three edges: both `gld_enr_poi_review` edges and `slv_enr_poi_review_multi_lang -> gld_srv_poi_review`.
- `NB_CREATE_DDL`. Four new cells are appended at the end: `rvi18nenrmd`, `rvi18nenrpy`, `rvi18ngldmd`, `rvi18ngldpy`. They hold the ctrl `is_active` migration for existing environments and the new table contracts.
- Docs: `mapping_gld_srv_poi_review.md` and `gld_enr_poi_info_review.md` (FILE blocks), `01_DATA_MODEL.md` (N6, §7, §8), `03_OPERATOR_GUIDE.md` (§2.1, §2.2, §2.7).
- The four contract test files.

## 2. Non-goals

- No DROP of any table. No deletes of rows in data or ctrl tables. Watermark rows stay.
- No change to `NB_ENR_POI_REVIEW`, `NB_LIB_*`, pipeline JSON, `ctrl_cfg_schema_registry`, or `slv_3p_poi_review`. No `title` column is added (D-SRV-TEXT).
- No edit to `sql/postgres/gld_srv_serve.pg.sql`. Impact only: `apps.srv_poi_review` already has no `lang`, so the gold and PG contracts now agree on `lang`.
- No change to `slv_enr_poi_info_multi_lang` or `gld_srv_poi_multi_lang`. Their `time_to_spend`, `best_time`, and `cost_vnd` are different columns, out of scope.
- `docs/context/3p-google/mapping_gld_enr_poi_info.md` §2 (sector labels) becomes unused. Not in `scope.files`; impact only.
- The Google branch of N6 is unchanged.
- History cells in `NB_CREATE_DDL` (`enrddlpy`, `enrflagpy`, `srvrevpy`, …) stay unchanged.

## 3. Resolution of model-design conflicts

| # (model-design) | Resolution | Evidence |
|---|---|---|
| 1 No proposal | `request.md` plus ledger is the accepted scope. | Task state, ledger |
| 2 Registry | No registry change. | D-SRV-TEXT |
| 3 Gold types | Gold DDL holds `rating DECIMAL(4,2)`, `rating_count BIGINT`, `title STRING`, `review_date STRING`. The mapping doc is corrected to these types. `title` is `F.lit(None).cast("string")`. | `NB_SETUP_INITIAL_DDL` `init_tables` gld_srv_poi_review spec; `srvrevpy` `TABLE_COLS` |
| 4 Physical columns | Decision D-ARCH-1, §8 and §15. `gld_enr_poi_info` must physically lose the three columns because `check_append_schema` compares the target to the build by exact position. Physical removal is a manual runbook step after user stop S1. `gld_srv_poi_review.lang` removal is recommended at S1. If it is declined, the node still runs, because `ensure_target` only warns. | `NB_LIB_TRANSFORM_SLV_GLD` `check_append_schema`, `ensure_target`; precedent `20261022-enr-landing-and-gld-flags` R3 (DEV `gld_enr_poi_info` already has column mapping `name`) |
| 5 Partner `source_id` | Not invented: the current expression `F.col("id")` is kept. `id` is the USING join key. Under the new driving table it resolves to `i18n.business_service_id`, which equals `svc.id` on every joined row (join predicate) and is non-NULL on unjoined rows. `poi_id` keeps `uuid_md5(F.col("id"), F.lit(PARTNER))`. | Current `_partner` (`vi` aliases `business_service_id` to `id`, `svc.join(vi, "id")`); `01_DATA_MODEL.md` §8 |
| 6 Partner uniqueness | Registry key of `slv_pn_business_service_i18ns` is `["business_service_id", "locale"]`. With `locale = 'vi'` there is at most one row per `business_service_id`. If it is violated, the existing pk `poi_id` check and `partner_source_id_unique` still block the write. Same behavior as today; no new rule. | `NB_CREATE_DDL` `TABLE_CONFIGS` business_service_i18ns |
| 7 `i18n.name` | Exists: `"name": {"path": "name", "type": "string"}`. | Same registry entry |
| 8 Node-stop rule | Removed. Not needed for idempotency (§9). No USER_DECISION. | §9 |
| 9 Review `poi_id` | `slv_3p_poi_review.poi_id`, the only source. The `review_poi_id_mismatch` and `enrich_without_review` warnings are removed. | request In scope bullet 3 |
| 10 `poi_name_normalized` | Unchanged expression `F.lower(F.col("name"))`. `name` is now the coalesced column. | Current `_partner` `cols` |
| 11 Info checks | `json_text_null` becomes `service_flag IS NULL`. `cost_vnd_mismatch` is removed. Warn `time_to_spend_unfixed` is renamed `avg_range_min_unfixed`, same expression. `SECTOR_LABELS`, `SECTOR_OTHER`, `BEST_TIME_RE`, `_label`, `_time_to_spend_text`, `_best_time_text`, `_cost_vnd` are removed. | Cell `36415d3b` |
| 12 Srv ctrl edges | Edge `slv_enr_poi_review_multi_lang -> gld_srv_poi_review` must become `is_active = 0`. `_resolve_node` raises ConfigError for an active edge with no role in `spec.inputs`. The edges from `slv_3p_poi_review` and `slv_3p_poi_rating` stay and drive the node. | `NB_LIB_TRANSFORM_SLV_GLD` `_resolve_node` |
| 13 Docs | Updated per §14. | — |
| 14 PG | Impact only. | D-SRV-LANG |

## 4. Invariants

1. Every `ctrl_mng_pipeline_config` row with target `lh_vv_gold.enr.gld_enr_poi_review` has `is_active = 0`, both in the setup seed and after `rvi18nenrpy` runs.
2. The only active edges into `lh_vv_gold.dbo.gld_srv_poi_review` are `slv_3p_poi_review` and `slv_3p_poi_rating` on `PL_VV_TRANS_SLV_TO_GLD_30M`. `spec.inputs` equals `{"review": "slv_3p_poi_review", "rating": "slv_3p_poi_rating"}`.
3. `gld_srv_poi_review.OUT_COLS` + tech columns equal the `rvi18ngldpy` `REVIEW_COLS` and the setup spec. No `lang`. `title` is always NULL STRING. `review_text` = `slv_3p_poi_review.text`.
4. The `gld_enr_poi_info` select (`BEGIN_INFO_SELECT`…`END_INFO_SELECT`) + `created_at`, `updated_at` equals the `rvi18nenrpy` `INFO_COLS` and the setup spec. `cost` is present. With comment lines removed, the `\b(time_to_spend|best_time|cost_vnd)\b` tokens do not appear in cell `36415d3b`.
5. Partner N6 rows are one per live `slv_pn_business_service_i18ns` row with `locale = 'vi'`. A deleted `vi` row emits nothing. A service with no live `vi` row emits nothing.
6. Partner `name = coalesce(i18n.name, svc.name)`. `_am = coalesce(i18n.amentities, svc.amentities)` as a whole JSON value. `main_category`, `$.policies.operating_hours`, and `$.policies.holiday_exceptions` are all read from `_am`.
7. `phone`, `email`, `business_sector`, `operation_status`, `address`, and `website_urls` come only from the live service row and are NULL when it does not join.
8. The duplicate partner `place_type` check runs before the dictionary join. Ambiguous step 1 or step 2 raises QualityGateError. The "no remaining row → stop" rule is absent.
9. `poi_id` partner = `uuid_md5(F.col("id"), F.lit(PARTNER))`, `source_id = F.col("id")`, where `id` is `i18n.business_service_id`. The Google branch text is byte-identical to today.
10. Migration cells hold exactly one flow lock each. They check every precondition before the first write. They contain no `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE`, `columnMapping`, `ALTER TABLE`, `INSERT INTO`, or `SET is_active = 1`. A rerun writes nothing.

## 5. State ownership

| State | Owner | Writer in this task |
|---|---|---|
| `ctrl_mng_pipeline_config` rows for `gld_enr_poi_review` | `PL_VV_TRANS_SLV_TO_ENR_15M` | `rvi18nenrpy` (existing env), `init_seed_ctrl` (empty env) |
| `ctrl_mng_pipeline_config` rows for `gld_srv_poi_review` | `PL_VV_TRANS_SLV_TO_GLD_30M` | `rvi18ngldpy`, `init_seed_ctrl` |
| `slv_poi_entity_non_enrich` | N6 node, ENR_15M, MERGE + soft delete | Node run only |
| `gld_enr_poi_info` (APPEND) | `NB_ENR_POI_INFO`, ENR_15M | Node run. Physical schema: runbook R2 |
| `gld_srv_poi_review` (MERGE) | `NB_GLD_SRV_POI_REVIEW`, GLD_30M | Node run. Optional R2 for `lang` |
| `gld_enr_poi_review`, `slv_enr_poi_review_multi_lang` | Frozen. No active writer or reader in repo | None |
| `wm_flow__*` lock rows | Each pipeline | Cells take and release them |

## 6. Grain and keys

Unchanged pk per `model-design.md` `## Entities and grain` and `## Keys`.

- N6 partner subset changes from "live svc ⋈ live vi i18n" to "live vi i18n ⟕ live svc". This is a superset of today's rows: every old partner `poi_id` stays, and i18n rows whose service is deleted or missing are added. For the duplicate case, see §3 #6.
- `gld_srv_poi_review` changes from "enrich ⋈ review" to "all live `slv_3p_poi_review`" (key `review_id`, registry). This is a superset of today's rows.

## 7. Ordering

- N6 precedes `gld_enr_poi_info`, `slv_poi_amenity` (ENR_15M DAG), and GLD_30M readers. No DAG edge changes for N6.
- Inactivating the `gld_enr_poi_review` edges removes that node from the ENR_15M DAG. No edge uses `gld_enr_poi_review` as a source, so no downstream node is orphaned.
- Inactivating the edge from `slv_enr_poi_review_multi_lang` changes no GLD_30M ordering, because that table has no producer.
- Rollout order is fixed (§15). Notebook deploy must precede the srv `lang` drop, because old srv code would re-add `lang` at the end through `ensure_target`.

## 8. Alternatives and selected trade-offs

| Topic | Options | Selected | Why |
|---|---|---|---|
| Removing physical columns (D-ARCH-1) | (a) Column mapping + `ALTER TABLE … DROP COLUMNS`, manual runbook after S1. (b) Keep the columns and write typed NULLs. (c) `CREATE OR REPLACE` / DROP TABLE. (d) Keep the columns and stop writing them. | (a) for `gld_enr_poi_info`, required. (a) recommended for srv `lang`, (d) accepted if S1 declines it. | (b) breaks acceptance ("no … in select"). (c) is forbidden. (d) fails `check_append_schema` for the APPEND table, but works for the MERGE srv table, where it only warns. (a) is metadata-only and does not invalidate the APPEND marker (precedent 20261022). Its cost, the irreversible protocol upgrade, is already paid in DEV for `gld_enr_poi_info`. Because the request says "No DROP", this is a user stop. |
| Ctrl change in existing envs | (a) New migration cells. (b) Edit history cells. (c) Seed edit only. | (a) + seed edit | Setup `_merge_pipeline_config` is insert-only (`WHEN NOT MATCHED`), so (c) reaches only empty environments. History cells are an append-only log (pattern `[THÊM dd/mm]`). |
| Lock scope | One cell holding both flow locks vs two cells with one lock each | Two cells | No nested lock and no deadlock risk. Each pipeline is migrated independently. Matches `ohpasspy` / `srvrevpy`. |
| Srv edge from multi_lang | (a) `is_active = 0`. (b) Keep a dummy unused role. | (a) | (b) still pins and versions the table (it "reads" it), contradicting the request. (a) is reversible. |
| Partner join | USING join on `id` vs explicit predicate with aliases | USING `vi.join(svc, "id", "left")` | Keeps the `poi_id` / `source_id` expressions byte-identical. Spark takes the USING key from the left (i18n) side. |
| Node-stop rule | Keep vs remove | Remove | The request says to remove it. Idempotency does not depend on it (§9). `required_inputs` still blocks when `svc` or `i18n` is entirely empty. That is a table-health guard, not the removed rule. |
| `title` NULL | `F.lit(None).cast("string")` vs `F.expr` | cast | A void type fails `ensure_target`'s type check. The test permits exactly this one cast. |
| `time_to_spend_unfixed` warn | Keep the name vs rename | Rename to `avg_range_min_unfixed` | Makes invariant 4 testable by token. `qg_json` consumers see a new key name (§11). |

## 9. Idempotency

- N6, `gld_srv_poi_review`: RECOMPUTE → MERGE by pk with `row_hash`. A deterministic build over pinned versions makes a rerun produce zero diff, and `diff_counts` skips the MERGE. On the first run after deploy, `gld_srv_poi_review` changes `row_hash` on every row (`lang` gone, `title` and `review_text` changed source), so every row is updated, plus inserts for previously unenriched reviews. The second run produces zero diff.
- Removing the node-stop rule: when the source has no live `vi` rows, MERGE soft-deletes the partner rows. That is the correct image of the source, and it is reversible: matched rows get `deleted_at = NULL` when the source returns. A rerun on the same input gives the same result, so idempotency holds without the rule.
- `gld_enr_poi_info` APPEND: the changed-key derivation is unchanged. Column removal by itself appends nothing. New or changed partner entity rows append through `ctx.changed("entity")`.
- Cells: the UPDATE runs only while some target edge has `is_active = 1`, so a rerun makes no ctrl commit. The post-checks are read-only.

## 10. Transactions, concurrency, retry, partial failure

- Commit boundaries: each node writes one MERGE or APPEND commit. Each cell makes one UPDATE commit on `CFG` plus lock-row updates. Runbook R2 makes one `SET TBLPROPERTIES` commit (only if mapping is not already `name`) and one `DROP COLUMNS` commit per table.
- Concurrency: the cells take `wm_flow__<PL>` with a lease (ENR 35 min, GLD 90 min) and call `_refresh_lock()` immediately before the write. Node runs hold the same lock through NB_00. For R2, pipeline triggers are paused and both `lock_exec_id` must be NULL. A Delta metadata conflict with a concurrent commit fails one side; retry it.
- Retry: cells and R2 are rerunnable. Node failures are retried by the next schedule.

| Failure point | State | Effect | Recovery |
|---|---|---|---|
| New notebooks deployed, R2 not done | `gld_enr_poi_info` still has old columns | `NB_ENR_POI_INFO` raises ConfigError in `check_append_schema`. No write. `rvi18nenrpy` stops before writing. | Do R2, then rerun the cell |
| R2 done, old `NB_ENR_POI_INFO` still deployed | Columns gone | ConfigError, no write | Deploy new notebook |
| New srv notebook, `rvi18ngldpy` not run | Multi_lang edge active | ConfigError "edge without role", no write. Serving table stale. | Run `rvi18ngldpy` |
| `rvi18ngldpy` run, old srv notebook | Role `multi_lang` without edge | ConfigError, no write | Deploy new notebook |
| Srv `lang` dropped, then old srv code runs | `ensure_target` re-adds `lang` at the end | `rvi18ngldpy` rejects the schema | Prevented by order §15. If it happens: deploy new code and run R2 for `lang` again |
| `SET TBLPROPERTIES` ok, `DROP` failed | Mapping on, columns present | Same as row 1 | Rerun `DROP COLUMNS` |
| Cell UPDATE ok, post-check raised | Edges off | Cell FAILED in lock row | Rerun cell; the UPDATE is skipped |
| Cell lost lock before write | Nothing written | RuntimeError | Rerun later |

## 11. Observability

- N6 metrics. `partner_live` = live svc count. `partner_vi_live` (new) = live `vi` i18n count. `partner_rows` = rows emitted, which equals `partner_vi_live`. `partner_without_vi` now means live svc without a live `vi` row (informational). `partner_without_service` (new metric and `ctx.warn`) = partner rows with no live service. Existing `partner_*` counters are kept.
- Srv review: `rating_matched` is kept. Warnings `enrich_without_review` and `review_poi_id_mismatch` are removed.
- Info: QG key `cost_vnd_mismatch` disappears. `time_to_spend_unfixed` → `avg_range_min_unfixed`. Dashboards keyed on the old names must follow.
- Cells print the final edge state. Lock-row `status` / `error_message` record SUCCESS or FAILED.
- First-run signal: `gld_srv_poi_review` inserted ≫ 0 and updated equal to the prior row count. N6 inserted equals `partner_without_service`.

## 12. Security

No secrets, identities, or permissions change. `gld_srv_poi_review` now carries `author_name` for every third-party review, not only enriched ones. This column is already in the serving contract, but the exposure is wider. Noted for the risk gate; no masking is requested.

## 13. Cross-state impact

- New partner rows with NULL service columns reach `slv_poi_amenity` (NULL `business_sector`), `gld_enr_poi_info` (append), `gld_srv_poi_info`, and `gld_srv_poi_multi_lang` (left join). Partner `opening_hours_text` and `holiday_exceptions` can now fall back to `svc.amentities` when `i18n.amentities` is NULL. That changes values that `gld_enr_poi_info` checks with `opening_hours_text_mismatch`. The check compares gold to silver in the same run, so it stays consistent.
- `slv_enr_poi_review_multi_lang` has no active consumer and no in-repo producer. It is kept.
- `gld_enr_poi_review` stops receiving rows. Its edge watermarks stay for rollback.

## 14. Implementation plan

### 14.1 `NB_SLV_POI_ENTITY_NON_ENRICH` `b1entitybuild` def `_partner`

Replace the lines from the function head through the `base = (...)` statement with the code below. Keep `dp`, `s1`, `s2`, `out`, and the dictionary checks exactly as they are. Then make these changes:

- Replace `live = svc.count()` with `svc_live, vi_live = svc.count(), vi.count()`.
- Add `F.count("_svc").alias("with_service")` to the `agg`.
- Replace the `ctx.metrics.update(...)` block as shown below.
- Delete the two lines `if live and not agg["rows"]:` / `raise QualityGateError("slv_pn_business_services: không dòng nào có bản i18n vi")`.
- Keep `cols` and the return unchanged.
- In markdown `b1entitymd`, replace the first line's partner phrase with: "dòng partner: bản i18n `vi` còn sống LEFT JOIN `slv_pn_business_services` còn sống".

```python
def _partner(ctx: NodeContext, d: DataFrame, schema) -> DataFrame:
    # [SỬA 04/11] 20261104-poi-review-src-and-partner-i18n: bảng dẫn là bản i18n vi còn sống;
    # LEFT JOIN svc còn sống theo i18n.business_service_id = svc.id. svc xoá hoặc không có -> cột của svc NULL.
    # id (khoá USING) = business_service_id: poi_id, source_id giữ biểu thức cũ.
    vi = (_live(ctx.input("i18n")).where(F.col("locale") == "vi")
          .select(F.col("business_service_id").alias("id"), F.col("name").alias("_vi_name"),
                  F.col("amentities").alias("_vi_am")))
    svc = (_live(ctx.input("svc"))
           .select("id", F.col("name").alias("_svc_name"), F.col("amentities").alias("_svc_am"), "phone", "email",
                   "business_sector", "operation_status", "address", "website_urls", F.lit(True).alias("_svc")))
    # amentities: cả khối i18n khi khác NULL (kể cả thiếu khoá con), NULL thì cả khối của svc.
    # main_category, giờ, ngày lễ cùng đọc từ khối đã chọn.
    base = (vi.join(svc, "id", "left")
            .withColumn("name", F.coalesce("_vi_name", "_svc_name"))
            .withColumn("_am", F.coalesce("_vi_am", "_svc_am"))
            .withColumn("_mc", main_category_of(F.col("_am")))
            .withColumn("_hours", F.get_json_object(F.col("_am"), "$.policies.operating_hours"))
            .withColumn("_holiday", F.get_json_object(F.col("_am"), "$.policies.holiday_exceptions"))
            .withColumn("_web", website_url_of(F.col("website_urls")))
            .withColumn("primary_type", F.col("_mc.value")))
```

Metrics block replacing the current `ctx.metrics.update(partner_live=live, …)`:

```python
    without_service = agg["rows"] - agg["with_service"]
    ctx.metrics.update(partner_live=svc_live, partner_vi_live=vi_live, partner_rows=agg["rows"],
                       partner_without_vi=svc.join(vi, "id", "left_anti").count(),
                       partner_without_service=without_service,
                       partner_primary=agg["primary"], partner_primary_matched=agg["primary_matched"],
                       partner_named_group=agg["named_group"], partner_with_hours=agg["with_hours"],
                       partner_with_phone=agg["with_phone"], partner_with_email=agg["with_email"],
                       partner_with_holiday=agg["with_holiday"],
                       partner_main_category=status,
                       partner_website=web)
    ctx.warn("partner_without_service", without_service)
```

`SPEC` is unchanged, including `required_inputs` and `unique_checks`.

### 14.2 `NB_GLD_SRV_POI_REVIEW` `srvrvbuild`

Replace the constants and `build` with the code below. `_require` and `_types` are unchanged. `SPEC` changes only in `inputs={"review": "slv_3p_poi_review", "rating": "slv_3p_poi_rating"}` and `required_inputs=("review",)`.

Markdown `srvrvmd`, lines 3–5: "RECOMPUTE `lh_vv_gold.dbo.gld_srv_poi_review`. Grain một dòng một `review_id`. / Bảng gốc `slv_3p_poi_review`; không đọc `slv_enr_poi_review_multi_lang`. `title` NULL, `review_text` = `text`. / LEFT JOIN `slv_3p_poi_rating` theo `poi_id`. Trùng `poi_id` thì dừng, không chọn dòng."

```python
REVIEW_COLS = ("review_id", "poi_id", "rating", "text", "time", "author_name")
RATING_COLS = ("poi_id", "rating_overall", "rating_count")
SOURCE_TYPES = {
    "slv_3p_poi_review": {"rating": "decimal(4,2)"},
    "slv_3p_poi_rating": {"rating_overall": "decimal(4,2)", "rating_count": "bigint"},
}
OUT_COLS = ("review_id", "poi_id", "rating_overall", "rating_count", "title", "review_text",
            "rating", "review_date", "author_name")


def build(ctx):
    rv = ctx.input("review")
    rt = ctx.input("rating")
    _require(rv, REVIEW_COLS, "slv_3p_poi_review")
    _require(rt, RATING_COLS, "slv_3p_poi_rating")
    _types(rv, "slv_3p_poi_review")
    _types(rt, "slv_3p_poi_rating")
    # Một dòng mỗi poi_id. Trùng poi_id -> dừng, không chọn dòng.
    rt = rt.select(*RATING_COLS)
    dup = rt.where(F.col("poi_id").isNotNull()).groupBy("poi_id").count().where("count > 1").count()
    if dup:
        raise QualityGateError(f"gld_srv_poi_review: slv_3p_poi_rating {dup} poi_id có hơn một dòng")
    # D-SRV-TEXT: slv_3p_poi_review không có title -> title NULL; review_text = text. D-SRV-LANG: không có lang.
    review = rv.select("review_id", "poi_id", "rating", F.col("text").alias("review_text"),
                       F.col("time").alias("review_date"), "author_name",
                       F.lit(None).cast("string").alias("title"))
    rows = review.join(rt.withColumn("_rated", F.lit(True)), "poi_id", "left")
    ctx.metrics.update(rating_matched=rows.where("_rated IS NOT NULL").count())
    return rows.select(*OUT_COLS)
```

### 14.3 `NB_ENR_POI_INFO` `36415d3b`

- Add a header comment: `# [SỬA 04/11] 20261104-poi-review-src-and-partner-i18n: bỏ 3 cột chữ theo sector khỏi gold; giữ cost.` Phrase it without the three column names, or keep them; the tests strip comment lines.
- In `BEGIN_INFO_PURE`, delete the `# Mục 2 mapping…` comment, `SECTOR_LABELS`, `SECTOR_OTHER`, the `# Mục 1.2…` comment, and `BEST_TIME_RE`. Keep `GOOGLE, PARTNER` and `REQUIRED_COLS`. `avg_range_min` and `canonical_candidate` stay in `entity`, because they still feed same-named passthrough columns.
- Delete defs `_label`, `_time_to_spend_text`, `_best_time_text`, `_cost_vnd`. Keep `_cost`.
- In `build`, delete `sector = F.col("e.business_sector")`. In the select, delete the `time_to_spend` (2 lines), `best_time` (2 lines), and `cost_vnd` entries. `cost.alias("cost")` stays between `review_json` and `service_flag`.
- `block_checks`: `("json_text_null", "service_flag IS NULL")`, `google_cols_not_google` (unchanged), `enrich_flag_null` (unchanged). Remove `cost_vnd_mismatch`.
- `warn_checks`: `("cost_null", "cost IS NULL")`, `("avg_range_min_unfixed", "avg_range_min IS NULL OR avg_range_min <= 0")`.

### 14.4 `NB_SETUP_INITIAL_DDL`

- `init_tables`, spec `lh_vv_gold.enr.gld_enr_poi_info`: delete the tuples `time_to_spend`, `best_time`, `cost_vnd`. The result equals `rvi18nenrpy` `INFO_COLS` with a third element of `None`.
- `init_tables`, spec `lh_vv_gold.dbo.gld_srv_poi_review`: delete `('lang', 'STRING', None)`.
- `init_seed_ctrl`: set the sixth tuple element to `0` on three rows: `(_ENR, _S, 'slv_3p_poi_review', _E, 'gld_enr_poi_review', …)`, `(_ENR, _S, 'slv_enr_poi_review_multi_lang', _E, 'gld_enr_poi_review', …)`, and `(_GLD30, _S, 'slv_enr_poi_review_multi_lang', _G, 'gld_srv_poi_review', …)`. Add one comment line above each block: `# [SỬA 04/11] 20261104-poi-review-src-and-partner-i18n: cạnh tắt (is_active = 0), giữ dòng.` Row count stays 69.

### 14.5 `NB_CREATE_DDL`: four cells appended at the end

Use the same cell metadata as `srvrevpy` (python, synapse_pyspark). Final cell-id order: `…, "srvrevmd", "srvrevpy", "rvi18nenrmd", "rvi18nenrpy", "rvi18ngldmd", "rvi18ngldpy"`.

`rvi18nenrmd` (markdown): `[THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2)` + blank line + `Tắt mọi cạnh tới \`gld_enr_poi_review\` trên \`PL_VV_TRANS_SLV_TO_ENR_15M\` (is_active = 0, giữ dòng, watermark, bảng, dữ liệu). Kiểm \`gld_enr_poi_info\` đã bỏ \`time_to_spend\`, \`best_time\`, \`cost_vnd\`; bảng còn cột cũ thì dừng trước khi ghi. Chạy lại không ghi.`

`rvi18ngldmd` (markdown): `[THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2)` + blank line + `Tắt cạnh \`slv_enr_poi_review_multi_lang\` → \`gld_srv_poi_review\` trên \`PL_VV_TRANS_SLV_TO_GLD_30M\`. Hợp đồng \`gld_srv_poi_review\` bỏ \`lang\`. Chạy lại không ghi.`

#### 14.5.1 `rvi18nenrpy`

```python
# [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (1/2, luồng ENR_15M)
# 1. Tắt mọi cạnh tới lh_vv_gold.enr.gld_enr_poi_review (is_active = 0). Giữ dòng, watermark, bảng, dữ liệu.
# 2. gld_enr_poi_info: hợp đồng bỏ time_to_spend, best_time, cost_vnd; giữ cost. Cell không bỏ cột:
#    bảng còn cột cũ -> dừng trước khi ghi; làm bước R2 trong architecture.md của task (sau S1) rồi chạy lại.
# Chạy khi workspace đã có NB_ENR_POI_INFO bản 04/11. Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_ENR_15M suốt cell.
# Chạy lại: không ghi. Sau cell này không chạy lại enrflagpy: hợp đồng gld_enr_poi_info trong đó là bản cũ.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_ENR_15M"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.enr"
INFO_FQ = f"{GLD}.gld_enr_poi_info"
REVIEW = "gld_enr_poi_review"
LEASE_MINUTES = 35  # bằng p_lock_timeout_min của NB_00_ORCHES_SLV_TO_ENR_15M
INFO_REMOVED = ("time_to_spend", "best_time", "cost_vnd")
INFO_COLS = [
    ("poi_id", "STRING NOT NULL"), ("source_name", "STRING"), ("source_id", "STRING"),
    ("language_code", "STRING"), ("poi_name", "STRING"), ("poi_name_normalized", "STRING"),
    ("types", "STRING"), ("operating_status", "STRING"), ("primary_type", "STRING"),
    ("website_url", "STRING"), ("house_number", "STRING"), ("street", "STRING"),
    ("ward", "STRING"), ("city", "STRING"), ("full_address", "STRING"), ("lat", "DOUBLE"),
    ("lng", "DOUBLE"), ("business_sector", "STRING"), ("business_category", "STRING"),
    ("business_category_vi", "STRING"), ("category_group", "STRING"),
    ("range_low_min", "INT"), ("range_high_min", "INT"), ("avg_range_min", "INT"),
    ("candidate_best_time_code", "STRING"), ("canonical_candidate", "STRING"),
    ("rating", "DECIMAL(4,2)"), ("user_rating_count", "BIGINT"), ("price_level", "INT"),
    ("opening_hours_text", "STRING"), ("review_json", "STRING"), ("cost", "BIGINT"),
    ("service_flag", "STRING"), ("is_enriched_multi_lang", "BOOLEAN"), ("is_enriched_destination", "BOOLEAN"),
    ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
]
EDGES_OFF = [
    ("slv_3p_poi_review", "lh_vv_gold.enr", "gld_enr_poi_review"),
    ("slv_enr_poi_review_multi_lang", "lh_vv_gold.enr", "gld_enr_poi_review"),
]
LOCK = "rvi18nenr-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


def _edges(trg_schema, trg):
    # (pl_name, src_schema, src_tbl, is_active) -> số dòng, mọi pl.
    return {(r["pl_name"], r["src_schema"], r["src_tbl"], r["is_active"]): r["n"] for r in spark.sql(f"""
    SELECT pl_name, src_schema, src_tbl, is_active, count(*) AS n FROM {CFG}
    WHERE trg_schema = '{trg_schema}' AND trg_tbl = '{trg}'
    GROUP BY pl_name, src_schema, src_tbl, is_active
    """).collect()}


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
    owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
    if not owner or owner["lock_exec_id"] != LOCK:
        other = None if owner is None else owner["lock_exec_id"]
        raise RuntimeError(f"Luồng {PL} đang giữ khoá ({other}): chạy lại sau")
    held = True

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    if not spark.catalog.tableExists(INFO_FQ):
        issues.append(f"{INFO_FQ} chưa có")
    else:
        got = _schema(INFO_FQ)
        old = [col[0] for col in got if col[0] in INFO_REMOVED]
        if old:
            issues.append(f"{INFO_FQ} còn cột {old}: làm bước R2 (bỏ cột, sau S1) rồi chạy lại")
        elif got != _want(INFO_COLS):
            issues.append(f"{INFO_FQ} không khớp hợp đồng, không sửa: có {got}, cần {_want(INFO_COLS)}")
    rows = _edges(GLD, REVIEW)
    off = sorted({(PL, SLV, src) for src, _trg_schema, _trg in EDGES_OFF})
    for (pl, src_schema, src, flag), n in rows.items():
        if flag == 1 and (pl, src_schema, src) not in off:
            issues.append(f"cạnh lạ {pl} {src_schema}.{src} -> {REVIEW} đang active, không sửa")
    flags = {}
    for key in off:
        flags[key] = {flag: n for (pl, ss, src, flag), n in rows.items() if (pl, ss, src) == key}
        if flags[key] not in ({0: 1}, {1: 1}):
            issues.append(f"cạnh {key} -> {REVIEW} là {flags[key]}, cần đúng 1 dòng is_active 0 hoặc 1")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    if any(value == {1: 1} for value in flags.values()):
        srcs = ", ".join(f"'{src}'" for _pl, _ss, src in off)
        _refresh_lock()
        spark.sql(f"""
        UPDATE {CFG} SET is_active = 0
        WHERE pl_name = '{PL}' AND src_schema = '{SLV}' AND trg_schema = '{GLD}' AND trg_tbl = '{REVIEW}'
          AND src_tbl IN ({srcs}) AND is_active = 1
        """)

    # Sau khi ghi: mọi cạnh tới gld_enr_poi_review tắt, đúng 1 dòng mỗi cạnh; hợp đồng info không đổi.
    problems = []
    want = {(pl, ss, src, 0): 1 for pl, ss, src in off}
    if _edges(GLD, REVIEW) != want:
        problems.append(f"cạnh tới {REVIEW} là {_edges(GLD, REVIEW)}, cần {want}")
    if _schema(INFO_FQ) != _want(INFO_COLS):
        problems.append(f"{INFO_FQ} lệch cột")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"cạnh tắt {[src for _pl, _ss, src in off]} -> {REVIEW}; {INFO_FQ} {len(INFO_COLS)} cột")
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

#### 14.5.2 `rvi18ngldpy`

Same skeleton as 14.5.1: the `_want`, `_schema`, `_edges`, `_refresh_lock` defs, the lock acquire and release blocks, and the `finally`. These parts differ:

```python
# [THÊM 04/11] 20261104-poi-review-src-and-partner-i18n (2/2, luồng GLD_30M)
# 1. Tắt cạnh slv_enr_poi_review_multi_lang -> lh_vv_gold.dbo.gld_srv_poi_review (is_active = 0). Giữ dòng, watermark.
#    Cạnh slv_3p_poi_review, slv_3p_poi_rating giữ active.
# 2. gld_srv_poi_review: hợp đồng bỏ lang. Cell không bỏ cột. Chấp nhận bảng đã bỏ lang hoặc còn lang ở vị trí cũ
#    (node không ghi lang, ensure_target chỉ cảnh báo). Lệch khác -> dừng trước khi ghi.
# Chạy khi workspace đã có NB_GLD_SRV_POI_REVIEW bản 04/11. Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M suốt cell.
# Chạy lại: không ghi. Sau cell này không chạy lại srvrevpy: hợp đồng và cạnh trong đó là bản cũ.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
REVIEW = "gld_srv_poi_review"
REVIEW_FQ = f"{GLD}.{REVIEW}"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
REVIEW_COLS = [
    ("review_id", "STRING NOT NULL"), ("poi_id", "STRING"),
    ("rating_overall", "DECIMAL(4,2)"), ("rating_count", "BIGINT"), ("title", "STRING"),
    ("review_text", "STRING"), ("rating", "DECIMAL(4,2)"),
    ("review_date", "STRING"), ("author_name", "STRING"),
    ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
    ("deleted_at", "TIMESTAMP"),
]
OLD_COL = ("lang", "STRING")
EDGES_OFF = [("slv_enr_poi_review_multi_lang", "lh_vv_gold.dbo", "gld_srv_poi_review")]
EDGES_KEEP = ("slv_3p_poi_review", "slv_3p_poi_rating")
LOCK = "rvi18ngld-" + uuid.uuid4().hex
```

Precondition, write, and post-check body (replaces the 14.5.1 body between `held = True` and `except`):

```python
    issues = []
    want = _want(REVIEW_COLS)
    accepted = (want, want[:2] + _want([OLD_COL]) + want[2:])
    if not spark.catalog.tableExists(REVIEW_FQ):
        issues.append(f"{REVIEW_FQ} chưa có")
    elif _schema(REVIEW_FQ) not in accepted:
        issues.append(f"{REVIEW_FQ} không khớp hợp đồng, không sửa: có {_schema(REVIEW_FQ)}, cần {want}")
    rows = _edges(GLD, REVIEW)
    off_src = EDGES_OFF[0][0]
    for (pl, src_schema, src, flag), n in rows.items():
        if flag == 1 and (pl != PL or src_schema != SLV or src not in EDGES_KEEP + (off_src,)):
            issues.append(f"cạnh lạ {pl} {src_schema}.{src} -> {REVIEW} đang active, không sửa")
    flags = {flag: n for (pl, ss, src, flag), n in rows.items() if (pl, ss, src) == (PL, SLV, off_src)}
    if flags not in ({0: 1}, {1: 1}):
        issues.append(f"cạnh {off_src} -> {REVIEW} là {flags}, cần đúng 1 dòng is_active 0 hoặc 1")
    keep = {src: n for (pl, ss, src, flag), n in rows.items() if flag == 1 and (pl, ss) == (PL, SLV) and src in EDGES_KEEP}
    if keep != {src: 1 for src in EDGES_KEEP}:
        issues.append(f"cạnh active giữ lại là {keep}, cần {sorted(EDGES_KEEP)}")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    if flags == {1: 1}:
        _refresh_lock()
        spark.sql(f"""
        UPDATE {CFG} SET is_active = 0
        WHERE pl_name = '{PL}' AND src_schema = '{SLV}' AND trg_schema = '{GLD}' AND trg_tbl = '{REVIEW}'
          AND src_tbl = '{off_src}' AND is_active = 1
        """)

    problems = []
    after = _edges(GLD, REVIEW)
    active = {src: n for (pl, ss, src, flag), n in after.items() if flag == 1}
    if active != {src: 1 for src in EDGES_KEEP}:
        problems.append(f"cạnh active tới {REVIEW} là {active}, cần {sorted(EDGES_KEEP)}")
    if {flag: n for (pl, ss, src, flag), n in after.items() if src == off_src} != {0: 1}:
        problems.append(f"cạnh {off_src} -> {REVIEW} sau ghi không phải đúng 1 dòng is_active = 0")
    if _schema(REVIEW_FQ) not in accepted:
        problems.append(f"{REVIEW_FQ} lệch cột")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"cạnh {off_src} -> {REVIEW} tắt; active {sorted(EDGES_KEEP)}; lang vật lý: {_schema(REVIEW_FQ) != want}")
```

### 14.6 Docs

- `docs/context/mapping_gld_srv_poi_review.md` and `docs/context/gld_enr_poi_info_review.md`: FILE blocks below.
- `docs/context/01_DATA_MODEL.md`:
  - N6 row (L330): append this sentence: `[SỬA 04/11] Partner: bảng dẫn là \`slv_pn_business_service_i18ns\` còn sống, \`locale = 'vi'\`; LEFT JOIN \`slv_pn_business_services\` còn sống theo \`business_service_id = id\`. \`poi_name\` = coalesce(i18n.name, svc.name); \`amentities\` = coalesce cả khối JSON i18n, svc; \`primary_type\` (main_category), opening_hours_text, holiday_exceptions đọc từ khối đã chọn (thay câu partner của [SỬA 23/10]). phone, email, business_sector, operating_status, địa chỉ, website_url chỉ từ svc, NULL khi svc không join. Không còn rule dừng node khi không có dòng partner.`
  - §8 (L365): replace `\`NB_SLV_POI_ENTITY_NON_ENRICH\` (\`id\`)` with `\`NB_SLV_POI_ENTITY_NON_ENRICH\` (\`id\` = \`business_service_id\` của bản i18n \`vi\`, khoá USING của LEFT JOIN)`.
  - §7: after the table, add `[SỬA 04/11] Mọi cạnh tới \`gld_enr_poi_review\` có \`is_active = 0\`; bảng và dữ liệu giữ nguyên, không ghi thêm. \`gld_enr_poi_info\` bỏ \`time_to_spend\`, \`best_time\`, \`cost_vnd\`.`
- `docs/context/03_OPERATOR_GUIDE.md`:
  - §2.1: after `Ghi bằng \`APPEND\`.`, add the line `[SỬA 04/11] Không còn \`time_to_spend\`, \`best_time\`, \`cost_vnd\`; \`cost\` giữ nguyên. Nguồn không đổi.`
  - §2.2: after `Ghi bằng \`APPEND\`.`, add `[SỬA 04/11] Luồng đang tắt: mọi cạnh tới \`gld_enr_poi_review\` có \`is_active = 0\`, \`NB_ENR_POI_REVIEW\` không chạy. Bảng và dữ liệu giữ nguyên. Hình dưới là lineage khi cạnh bật.`
  - §2.7: set the join table rows to `| \`slv_3p_poi_review\` | Bảng gốc |` and `| \`slv_3p_poi_rating\` | \`left\` join theo \`poi_id\` |`. Delete the `slv_enr_poi_review_multi_lang` HTML `<tr>`. Add `[SỬA 04/11] Không đọc \`slv_enr_poi_review_multi_lang\`. Không có \`lang\`; \`title\` NULL; \`review_text\` = \`text\`.`

### 14.7 Tests

Exact names are in the brief. Rules:

- Every test that reads the current contract of `gld_enr_poi_info` or `gld_srv_poi_review` from `enrflagpy` or `srvrevpy` takes it from `rvi18nenrpy` `INFO_COLS` / `rvi18ngldpy` `REVIEW_COLS` instead.
- History assertions on `enrflagpy` and `srvrevpy` constants stay, with an `INFO_OLD` copy of today's `INFO`.
- Every cell-id order assertion (`test_info_patch_cell_guards`, `test_info_rating_patch`, `test_create_ddl_patch`) shifts by 4 and adds `ids[-4:] == ["rvi18nenrmd", "rvi18nenrpy", "rvi18ngldmd", "rvi18ngldpy"]`.
- `test_pipeline_config_rows_match_sources` marks `active = 0` for `(src, trg)` in `rvi18nenrpy` `EDGES_OFF` (applied to `enrddlpy` and `enrflagpy` edges) and in `rvi18ngldpy` `EDGES_OFF` (applied to `srvrevpy` edges). The 69-row count is kept.

## 15. Rollout

Runtime proof is not part of this task's acceptance. These steps run per environment after review and the risk gate.

- R0 probes (read only):
  - P1: `SHOW TBLPROPERTIES` and `DESCRIBE DETAIL` on `lh_vv_gold.enr.gld_enr_poi_info` and `lh_vv_gold.dbo.gld_srv_poi_review`. Record `delta.columnMapping.mode`, `minReaderVersion`, `minWriterVersion`.
  - P2: list the readers of `gld_srv_poi_review` outside the repo (SQL analytics endpoint queries, semantic models, PG sync jobs) and whether they select `lang`.
- **S1 (user decision)**:
  - (a) Approve `DROP COLUMNS (time_to_spend, best_time, cost_vnd)` on `gld_enr_poi_info`, plus the column-mapping upgrade if P1 shows it is not on. Required. If declined, the request cannot be met as written; return to the user.
  - (b) Approve or decline `DROP COLUMNS (lang)` on `gld_srv_poi_review`. If declined, `lang` stays physically with stale values on old rows and NULL on new rows. `rvi18ngldpy` accepts that state.
- R1: Pause the triggers of `PL_VV_TRANS_SLV_TO_ENR_15M` and `PL_VV_TRANS_SLV_TO_GLD_30M`, and wait for both `wm_flow__` `lock_exec_id` to be NULL. Deploy all notebooks.
- R2: Run the SQL in §15.1.
- R3: Run `rvi18nenrpy`, then `rvi18ngldpy`.
- R4: Resume the triggers. On the first runs, check: N6 `inserted = partner_without_service`; `gld_srv_poi_review` updated ≈ prior rows and inserted ≥ 0; `gld_enr_poi_info` APPEND SUCCESS.

### 15.1 Runbook R2 SQL (after S1)

```sql
-- Only if P1 shows columnMapping.mode <> 'name' (irreversible protocol upgrade):
ALTER TABLE lh_vv_gold.enr.gld_enr_poi_info SET TBLPROPERTIES (
  'delta.minReaderVersion' = '2', 'delta.minWriterVersion' = '5', 'delta.columnMapping.mode' = 'name');
ALTER TABLE lh_vv_gold.enr.gld_enr_poi_info DROP COLUMNS (time_to_spend, best_time, cost_vnd);
-- S1(b) approved only; same TBLPROPERTIES step first if needed:
ALTER TABLE lh_vv_gold.dbo.gld_srv_poi_review DROP COLUMNS (lang);
DESCRIBE TABLE lh_vv_gold.enr.gld_enr_poi_info;   -- 37 columns, cost present
DESCRIBE TABLE lh_vv_gold.dbo.gld_srv_poi_review; -- 13 columns, or 14 with lang at position 3
```

## 16. Rollback and forward recovery

- Forward recovery is preferred. Every interleaving in §10 fails closed with no write.
- Code rollback: revert the commit, redeploy the old notebooks with triggers paused, then re-activate the edges:

```sql
UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 1
WHERE (pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15M' AND trg_schema = 'lh_vv_gold.enr' AND trg_tbl = 'gld_enr_poi_review'
       AND src_tbl IN ('slv_3p_poi_review', 'slv_enr_poi_review_multi_lang'))
   OR (pl_name = 'PL_VV_TRANS_SLV_TO_GLD_30M' AND trg_schema = 'lh_vv_gold.dbo' AND trg_tbl = 'gld_srv_poi_review'
       AND src_tbl = 'slv_enr_poi_review_multi_lang');
```

- `gld_enr_poi_info` with old code: `ALTER TABLE … ADD COLUMNS (time_to_spend STRING AFTER review_json, best_time STRING AFTER time_to_spend)` and `(cost_vnd STRING AFTER cost)`, so the positions match `check_append_schema`. Old rows read NULL. Old values are recoverable only by time travel to a version before R2, until VACUUM. The column-mapping protocol cannot be downgraded.
- N6 with old code: MERGE soft-deletes the partner rows that have no service. Clean.
- `gld_srv_poi_review` with old code: `ensure_target` re-adds `lang` at the end. Rows not from enrich are soft-deleted. Clean, apart from the column position.

## 17. Verification

- Local: `python -m pytest tests/test_enr_poi_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py -q`, then `python -m pytest -q`. All must pass. Report failures with their output.
- Static: with comment lines stripped, neither migration cell contains the forbidden tokens of invariant 10. In cell `36415d3b`, `\b(time_to_spend|best_time|cost_vnd)\b` matches nothing. `_google` is unchanged; check with `git diff` restricted to the `_google` def.
- Runtime (optional, R4), read-only SQL:
  - ctrl: active-flag query for the three edges.
  - `SELECT count(*) FROM slv_poi_entity_non_enrich WHERE source_name='partner' AND deleted_at IS NULL` equals the count of live `vi` i18n rows.
  - `gld_srv_poi_review`: `count(title) = 0`; live row count equals live `slv_3p_poi_review`; `review_text` is null-safe equal to `text` on a join by `review_id`.

FILE: docs/context/mapping_gld_srv_poi_review.md

# Table: `gld_srv_poi_review`

## 1. Xử lý

- [SỬA 04/11] Bảng gốc là `slv_3p_poi_review`, một dòng một `review_id`. Không đọc `slv_enr_poi_review_multi_lang`.
- `slv_3p_poi_review` LEFT JOIN `slv_3p_poi_rating` on `poi_id`. `poi_id` trùng trên `slv_3p_poi_rating` thì dừng, không chọn dòng.
- Không có cột `lang` (D-SRV-LANG). `title` luôn NULL: `slv_3p_poi_review` không có cột `title` và không thêm (D-SRV-TEXT). `review_text` lấy từ `slv_3p_poi_review.text`.

## 2. Field Mapping

| Source Field | Data Type | Transform | Target Field |
|---|---|---|---|
| slv_3p_poi_review.review_id | string | transform 1-1 | review_id |
| slv_3p_poi_review.poi_id | string | transform 1-1 | poi_id |
| slv_3p_poi_rating.rating_overall | decimal(4,2) | transform 1-1 | rating_overall |
| slv_3p_poi_rating.rating_count | bigint | transform 1-1 | rating_count |
| | string | NULL | title |
| slv_3p_poi_review.text | string | transform 1-1 | review_text |
| slv_3p_poi_review.rating | decimal(4,2) | transform 1-1 | rating |
| slv_3p_poi_review.time | string | transform 1-1 | review_date |
| slv_3p_poi_review.author_name | string | transform 1-1 | author_name |
| | timestamp | field hệ thống | created_at |
| | timestamp | field hệ thống | updated_at |
END_FILE

FILE: docs/context/gld_enr_poi_info_review.md
# `gld_enr_poi_info` và `gld_enr_poi_review`

Hai bảng gold enrich POI. Cột và kiểu lấy từ `NB_ENR_POI_INFO`, `NB_ENR_POI_REVIEW`, và `NB_SETUP_INITIAL_DDL`. `docs/context/01_DATA_MODEL.md` không có hai bảng này.

## `gld_enr_poi_info`

| Mục | Giá trị |
|---|---|
| Schema | `lh_vv_gold.enr` |
| Grain | Một dòng một `poi_id` |
| Notebook | `NB_ENR_POI_INFO` |
| Nguồn đang dùng | `lh_vv_silver.dbo.slv_poi_entity_non_enrich` (spine, bắt buộc), `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`. [SỬA 22/10] Thêm `slv_enr_poi_info_multi_lang` và `slv_enr_poi_destination`, chỉ đọc `poi_id` để tính cờ. Không chép nội dung enrich sang gold |
| Cột đã bỏ | [SỬA 04/11] `time_to_spend`, `best_time`, `cost_vnd` không còn trong DDL, `select`, và mapping. `cost` giữ nguyên |

`enrich_type` là nhóm trong tài liệu này, không phải cột Delta. Một cột có thể thuộc nhiều nhóm. Ô trống là cột không nằm trong ba rule.

| Cột                        | Kiểu              | Ý nghĩa                                                               | enrich_type                            |
| -------------------------- | ----------------- | --------------------------------------------------------------------- | -------------------------------------- |
| `poi_id`                   | `STRING NOT NULL` | Khóa một POI.                                                         | enrich description                     |
| `source_name`              | `STRING`          | Tên nguồn của POI, ví dụ `google` hoặc `partner`.                     |                                        |
| `source_id`                | `STRING`          | Id của POI ở hệ thống nguồn.                                          |                                        |
| `language_code`            | `STRING`          | Mã ngôn ngữ trên entity.                                              |                                        |
| `poi_name`                 | `STRING`          | Tên hiển thị của POI.                                                 | enrich description                     |
| `poi_name_normalized`      | `STRING`          | Tên POI đã chuẩn hóa.                                                 | enrich description                     |
| `types`                    | `STRING`          | JSON loại hình, lấy từ `types_json`.                                  | enrich description                     |
| `operating_status`         | `STRING`          | Trạng thái hoạt động.                                                 |                                        |
| `primary_type`             | `STRING`          | Loại hình chính.                                                      | enrich description                     |
| `website_url`              | `STRING`          | Website của POI.                                                      | enrich description                     |
| `house_number`             | `STRING`          | Số nhà.                                                               | enrich destination                     |
| `street`                   | `STRING`          | Tên đường.                                                            | enrich description, enrich destination |
| `ward`                     | `STRING`          | Phường hoặc xã.                                                       | enrich description, enrich destination |
| `city`                     | `STRING`          | Thành phố hoặc tỉnh.                                                  | enrich description, enrich destination |
| `full_address`             | `STRING`          | Địa chỉ đầy đủ.                                                       | enrich description, enrich destination |
| `lat`                      | `DOUBLE`          | Vĩ độ.                                                                | enrich destination                     |
| `lng`                      | `DOUBLE`          | Kinh độ.                                                              | enrich destination                     |
| `business_sector`          | `STRING`          | Mã nhóm ngành.                                                        | enrich description                     |
| `business_category`        | `STRING`          | Nhóm danh mục.                                                        | enrich description                     |
| `business_category_vi`     | `STRING`          | Nhóm danh mục tiếng Việt.                                             |                                        |
| `category_group`           | `STRING`          | Nhóm category.                                                        | enrich description                     |
| `range_low_min`            | `INT`             | Cận dưới thời lượng, phút.                                            | enrich description                     |
| `range_high_min`           | `INT`             | Cận trên thời lượng, phút.                                            | enrich description                     |
| `avg_range_min`            | `INT`             | Thời lượng trung bình, phút.                                          | enrich description                     |
| `candidate_best_time_code` | `STRING`          | Mã thời điểm đẹp ứng viên.                                            | enrich description                     |
| `canonical_candidate`      | `STRING`          | Chuỗi thời điểm đẹp đã chốt.                                          | enrich description                     |
| `rating`                   | `DECIMAL(4,2)`    | Điểm rating tổng; chỉ điền khi nguồn là `google`.                     | enrich description                     |
| `user_rating_count`        | `BIGINT`          | Số lượt rating; chỉ điền khi nguồn là `google`.                       | enrich description                     |
| `price_level`              | `INT`             | Mức giá; chỉ điền khi nguồn là `google`.                              | enrich description                     |
| `opening_hours_text`       | `STRING`          | Giờ mở cửa: `periods_json` nếu `google`, giờ trong `amentities` đã chọn (i18n `vi`, NULL thì của service) nếu `partner`. | enrich description                     |
| `review_json`              | `STRING`          | JSON tối đa 20 review; chỉ `google`, không có thì `[]`.               | enrich description                     |
| `cost`                     | `BIGINT`          | Trung bình làm tròn của `price_min` và `price_max` khi đủ cả hai.     | enrich description                     |
| `service_flag`             | `STRING`          | JSON mảng `service_flags` phân biệt, đã sort; không có thì `[]`.      | enrich description                     |
| `is_enriched_multi_lang`   | `BOOLEAN`         | True khi `poi_id` có ít nhất một dòng trong `slv_enr_poi_info_multi_lang`, ngược lại false. Notebook ghi true hoặc false. |                                        |
| `is_enriched_destination`  | `BOOLEAN`         | True khi `poi_id` có ít nhất một dòng trong `slv_enr_poi_destination`, ngược lại false. Notebook ghi true hoặc false. |                                        |
| `created_at`               | `TIMESTAMP`       | Mốc ghi batch; thư viện gán, không nằm trong `select`.                |                                        |
| `updated_at`               | `TIMESTAMP`       | Mốc ghi batch; thư viện gán, không nằm trong `select`.                |                                        |

## `gld_enr_poi_review`

| Mục | Giá trị |
|---|---|
| Schema | `lh_vv_gold.enr` |
| Grain | Một dòng một `review_id` |
| Notebook | `NB_ENR_POI_REVIEW` |
| Nguồn đang dùng | `lh_vv_silver.dbo.slv_3p_poi_review` (chỉ third-party). [SỬA 22/10] Thêm `slv_enr_poi_review_multi_lang`, chỉ đọc `review_id` để tính cờ. Không chép `review_text` sang gold |
| Trạng thái | [SỬA 04/11] Luồng tắt: mọi cạnh tới bảng này có `is_active = 0` trên `PL_VV_TRANS_SLV_TO_ENR_15M`. Notebook không chạy. Bảng và dữ liệu giữ nguyên, không DROP, không xoá dòng |

| Cột | Kiểu | Ý nghĩa |
|---|---|---|
| `review_id` | `STRING NOT NULL` | Khóa một review. |
| `poi_id` | `STRING` | POI mà review thuộc về. |
| `rating` | `DECIMAL(3,1)` | Điểm review; giá trị không vừa kiểu thì notebook dừng. |
| `review_text` | `STRING` | Nội dung review, lấy từ cột `text`. |
| `review_date` | `TIMESTAMP` | Thời điểm review, parse UTC từ cột `time`. |
| `review_updated_at` | `TIMESTAMP` | Parse UTC từ cột `time`, cùng biểu thức với `review_date`. |
| `is_enriched_multi_lang` | `BOOLEAN` | True khi `review_id` có ít nhất một dòng trong `slv_enr_poi_review_multi_lang`, ngược lại false. Notebook ghi true hoặc false. |
| `created_at` | `TIMESTAMP` | Mốc ghi batch; thư viện gán, không nằm trong `select`. |
| `updated_at` | `TIMESTAMP` | Mốc ghi batch; thư viện gán, không nằm trong `select`. |
END_FILE
