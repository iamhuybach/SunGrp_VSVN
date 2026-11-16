RESULT: PASS

## Main brief

### Decision
- Gold `gld_srv_poi_info.is_active BOOLEAN` goes after `is_bookable` in two places: `init_tables` (fresh install) and a new `NB_CREATE_DDL` cell pair `srvactivemd`/`srvactivepy`, appended after `enrmergepy`. `srvactivepy` is schema-only and holds the 30M lock, following the `poidestpy` pattern. `poidestpy` itself is not edited.
- `NB_GLD_SRV_POI_INFO` emits `F.lit(True).alias("is_active")`. Keep it in `row_hash`: no `hash_exclude`. The first run updates every live row once, which is accepted.
- PostgreSQL: save `sql/postgres/gld_srv_serve.pg.sql` exactly as the FILE block. Entities add `isActive` to `SrvPoiInfo` and `ingestionTs` to all five.
- The D-3 test exception is a single `PG_ONLY = {"ingestion_ts": ("timestamp without time zone", "LocalDateTime")}` that every apps table must have.
- **Scope gap:** three test files outside scope must change. Stop 1.

### Invariants Main must preserve
- `init_tables` `gld_srv_poi_info` == `srvactivepy` `TABLE_COLS` == `poidestpy` cols with `("is_active","BOOLEAN")` right after `is_bookable` == `OUT_COLS` + TECH.
- `srvinfobuild` has exactly one `F.lit(True).alias("is_active")`. It has no `hash_exclude`, no source read of `is_active`, and no `deleted` token.
- Every `apps` table: PostgreSQL cols == gold cols + `ingestion_ts`. `ingestion_ts` is typed `timestamp without time zone` and is the column right after `deleted_at`.
- `apps.srv_poi_info.is_active` is `boolean`, right after `is_bookable`, nullable.
- Entity cols == PostgreSQL cols. `isActive` is `Boolean` and `ingestionTs` is `LocalDateTime`, with the same adjacency as the SQL.
- No `is_active`/`isActive`/`ingestion_ts`/`ingestionTs` in the service `api/` or `service/` packages. No `ingestion_ts` in notebooks, `docs/context/api-mapping/` or `docs/poi-serving-api/`.
- `srvactivepy` comment-free code contains `ALTER TABLE` once and `ADD COLUMNS` once with ` AFTER `. It has no DROP/DELETE/TRUNCATE/REPLACE/RESTORE/columnMapping/INSERT/UPDATE {CFG}/MERGE INTO. A re-run is a no-op.
- The SQL file has no executable `ALTER` line. ALTER text appears only in `--` comments.
- No key, index, DTO, or API-mapping change. `AGENTS.md` is untouched.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, gld_srv_poi_info spec, line `('is_bookable', 'BOOLEAN', None),` | insert `"        ('is_active', 'BOOLEAN', None),\n",` after it | spec cols == srvactivepy TABLE_COLS |
| 2 | notebooks/NB_CREATE_DDL.ipynb | after cell `enrmergepy` | append markdown `srvactivemd` + code `srvactivepy` (JSON shape as enrmerge cells) | sources == doc "NB_CREATE_DDL srvactive cells"; `ids[-2:]==["srvactivemd","srvactivepy"]` |
| 3 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` `OUT_COLS` | add `"is_active"` after `"is_bookable"` | OUT_COLS+TECH == init cols |
| 4 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` `build` final `rows.select(` | after `F.lit(None).cast("boolean").alias("is_bookable"),` add `F.lit(True).alias("is_active"),` | literal once; select order matches OUT_COLS |
| 5 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfomd` | add line: `is_active` hằng `true` mọi dòng ghi (D-1) | text present |
| 6 | docs/context/mapping_gld_srv_poi_info.md | §1.2 after `is_bookable` row | `\| \| boolean \| true: hằng cho mọi dòng NB_GLD_SRV_POI_INFO ghi; không đọc nguồn, không theo deleted_at (D-1) \| is_active \|` | mapping targets == OUT_COLS + created/updated |
| 7 | docs/context/mapping_gld_srv_poi_info.md | §1.1 bullets | add D-1 bullet: true on all build rows; rows soft-deleted earlier keep NULL; first run rewrites row_hash once | bullet present |
| 8 | sql/postgres/gld_srv_serve.pg.sql | whole file | replace with the FILE block verbatim | pg tests pass |
| 9 | .../entity/SrvPoiInfo.java | after `isBookable` field | `@Column(name = "is_active")` `private Boolean isActive;` | entity test passes |
| 10 | .../entity/SrvPoiInfo.java, SrvPoiMultiLang.java, SrvPoiAmenity.java, SrvPoiMediaGallery.java, SrvPoiReview.java | after `deletedAt` field | `@Column(name = "ingestion_ts")` `private LocalDateTime ingestionTs;` | entity test passes; mvn green |
| 11 | tests/test_srv_poi_serving_contract.py | module constants | add `PG_ONLY` (D-3 comment) | — |
| 12 | same | `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys` | compare against `set(pg/entity) - set(PG_ONLY)`; require PG_ONLY col with exact type on every table; assert no gold col named ingestion_ts | pass |
| 13 | same | `test_info_cover_patch_cell`, `test_destination_name_patch_cell` | shift tail by 2; add `ids[-2:]==["srvactivemd","srvactivepy"]` | pass |
| 14 | same | `test_info_cover_build_rule` | drop `"is_active"` from forbidden tokens | pass |
| 15 | same | `test_info_cover_seed_and_init_ddl` | info from srvactivepy; keep cover→poidest chain; assert srvactive == poidest + is_active after is_bookable | pass |
| 16 | same | `test_destination_name_and_review_source_across_layers` | use srvactivepy cols for gld_srv_poi_info | pass |
| 17 | same | new `test_pg_only_ingestion_ts_and_is_active_positions`, new `test_new_columns_stay_out_of_api` | per doc "Test changes" | pass |
| 18 | tests/test_gld_srv_poi_contract.py | `test_info_rating_patch`, `test_review_source_patch_cell` | shift tail by 2 + new tail | pass |
| 19 | same | `test_build_columns_match_ddl` | `gold[INFO_FQ]` from srvactivepy | pass |
| 20 | same | new `test_info_is_active_patch_cell`, `test_info_is_active_literal_true` | per doc "Test changes" | pass |
| 21 | tests/test_initial_ddl_contract.py (after Stop 1) | lines 335, 733 | gld_srv_poi_info cols from srvactivepy `TABLE_COLS` | pass |
| 22 | tests/test_enr_poi_contract.py (after Stop 1) | `test_info_patch_cell_guards` lines 223-237 | shift slices by -2; add srvactive tail | pass |
| 23 | tests/test_poi_entity_contract.py (after Stop 1) | lines 635-649 | shift slices by -2; add srvactive tail | pass |
| 24 | .ai/tasks/20261116-srv-poi-info-is-active/runtime-runbook.md | whole | Vietnamese runbook per doc "Runbook content" | no hosts/creds; stop before Fabric run |

### Order and stop points
1. **STOP (user decision):** approve adding `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py` to `scope.files`. Without them, `vv.py verify` cannot pass, and every placement option breaks them. If refused, halt and report.
2. Rows 1-2: gold DDL and the patch cell.
3. Rows 3-7: notebook and mapping.
4. Rows 8-10: SQL and entities.
5. Rows 11-23: tests. Run pytest and fix until green.
6. Row 24: runbook. Optionally record A-decisions in `decision.md`: srvactivepy placement, accepted row_hash rewrite, PG_ONLY shape.
7. Run `vv.py verify`. **STOP (evidence):** report results. The Fabric DEV run is a later user-run session (`runtime=pending`). Do not run any notebook, pipeline or ALTER.

### Tests and verification
- `python -m pytest tests/test_srv_poi_serving_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
- New tests:
  - `test_srv_poi_serving_contract.py::test_pg_only_ingestion_ts_and_is_active_positions`
  - `::test_new_columns_stay_out_of_api`
  - `test_gld_srv_poi_contract.py::test_info_is_active_patch_cell`
  - `::test_info_is_active_literal_true`
- `python -m pytest tests -q` (catches other cell-order coupling)
- `cd services/data-serving-service && mvnw.cmd -q -B test` (Testcontainers loads the SQL; Hibernate selects new columns)
- `python scripts/vv.py verify 20261116-srv-poi-info-is-active`

### Read only if needed
- "Scope gap (blocking user decision)" → Stop 1, rows 21-23
- "NB_CREATE_DDL srvactive cells" → row 2 (full cell sources)
- "Idempotency" (row_hash, soft-deleted NULL) → rows 4, 7
- "Ordering" and "Retry and recovery" → row 24, row 2 stop/hint logic
- "Test changes" → rows 11-23
- "Runbook content" → row 24
- "Alternatives" → rows 2, 4, 11-12
- FILE block `sql/postgres/gld_srv_serve.pg.sql` → row 8

# Architecture: 20261116-srv-poi-info-is-active

Inputs: `request.md`, `decision.md` (D-1..D-6), `model-design.md` (`## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`, `## Conflicts and questions`). This document resolves model-design open questions 3, 4, 5 and 7. D-6 already resolves question 6. Grain and keys are cited from `model-design.md` and are not restated.

## Scope

- Gold DDL: `lh_vv_gold.dbo.gld_srv_poi_info.is_active BOOLEAN` (nullable), placed after `is_bookable`, in `NB_SETUP_INITIAL_DDL` cell `init_tables` (fresh install) and in a new `NB_CREATE_DDL` patch cell pair `srvactivemd` / `srvactivepy` that adds the column to existing tables.
- `NB_GLD_SRV_POI_INFO` cell `srvinfobuild`: `OUT_COLS` and the `build` select emit `F.lit(True).alias("is_active")` right after `is_bookable`.
- `docs/context/mapping_gld_srv_poi_info.md`: §1.1 note and a §1.2 row.
- `sql/postgres/gld_srv_serve.pg.sql`: `apps.srv_poi_info.is_active boolean` after `is_bookable`, and `ingestion_ts timestamp without time zone` after `deleted_at` on all five `CREATE TABLE apps.*` statements. The header records the manual ALTERs the user already ran and the D-3 exception (FILE block below).
- Five entities: `SrvPoiInfo.isActive` (`Boolean`), and `ingestionTs` (`LocalDateTime`) on all five.
- Tests: `tests/test_srv_poi_serving_contract.py` (the D-3 allowlist, positions, and API exclusion), `tests/test_gld_srv_poi_contract.py` (the new patch cell and the literal rule), plus the cell-order shifts listed under **Scope gap**.
- `runtime-runbook.md` (Vietnamese): the Fabric DEV gold-column add. This session stops before running it.

### Scope gap (blocking user decision)

These test files are outside `scope.files`. They break whatever placement is chosen for the gold contract (see Alternatives):
- `tests/test_initial_ddl_contract.py`: lines 335 and 733 assert that `init_tables`' `gld_srv_poi_info` equals the `poidestpy` `TABLE_COLS`. Adding `is_active` to `init_tables` breaks both.
- `tests/test_enr_poi_contract.py` lines 223-237 and `tests/test_poi_entity_contract.py` lines 635-649 assert the cell-id tail with `ids[-2:] == ["enrmergemd", "enrmergepy"]`. Appending `srvactivemd` / `srvactivepy` breaks both.

`python scripts/vv.py verify` cannot pass without editing these three files. The task cannot meet its acceptance criteria inside the current `scope.files`. The user must approve adding the three paths to `scope.files` before any edit. The change in each is mechanical (see Implementation plan, steps 7-8).

## Non-goals

- No change to grain, keys, `poi_id` formula, JSON API, DTOs, `docs/context/api-mapping/`, `docs/poi-serving-api/`.
- No `ingestion_ts` in silver or gold, and no writer for it. Nothing in the repository assigns it.
- No change to the gold-to-PostgreSQL load path (Copy Job). No ALTER on PostgreSQL. No notebook, pipeline, or Fabric run in this session.
- No edit to `services/data-serving-service/AGENTS.md` (model-design Q3). D-3/D-5 name `model-design.md` and `decision.md` as the record. Its `## Contract` text ("Entities and DTOs expose only columns that exist there") becomes slightly stale. If the user wants that wording updated, it is a separate scope change.
- No filtering on `SrvPoiInfo.isActive` in queries or specifications. API behaviour stays unchanged.

## Invariants

1. Gold `gld_srv_poi_info` column list equals the `srvactivepy` `TABLE_COLS`, which equals the `poidestpy` contract with `("is_active","BOOLEAN")` inserted immediately after `is_bookable` (36 columns). This also equals `OUT_COLS` plus the tech columns.
2. `NB_GLD_SRV_POI_INFO` writes `is_active = true` on every row it outputs. The value is a literal with no source read, no `deleted_at` dependence, and no `hash_exclude`.
3. PostgreSQL `apps.srv_poi_info` columns equal the gold columns plus `ingestion_ts`. Every other `apps.*` table equals its gold table plus `ingestion_ts`. `ingestion_ts` is the only allowed gold-absent column, its type is exactly `timestamp without time zone`, and it sits immediately after `deleted_at`.
4. `apps.srv_poi_info.is_active` is `boolean`, sits immediately after `is_bookable`, and is nullable.
5. Entity columns equal the PostgreSQL columns. `is_active` maps to `Boolean` and `ingestion_ts` to `LocalDateTime`, in the same adjacency as the SQL.
6. `is_active`, `isActive`, `ingestion_ts` and `ingestionTs` appear in no file under `api/` or `service/` of the service. `ingestion_ts` appears in no notebook, no `docs/context/api-mapping/` file and no `docs/poi-serving-api/` file.
7. No key, unique constraint, or index changes.
8. `srvactivepy` is schema-only. It never writes rows or pipeline config. A re-run is a no-op, and any state other than "exact contract" or "contract minus `is_active`" stops before writing.
9. `gld_srv_serve.pg.sql` contains no executable `ALTER` line. ALTER text lives only in `--` comments.

## State ownership

| State | Owner | This task |
|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` schema | `NB_SETUP_INITIAL_DDL` (fresh) / `NB_CREATE_DDL` patch cells (existing) | adds `is_active` |
| `gld_srv_poi_info` rows | `NB_GLD_SRV_POI_INFO` via `run_node` MERGE, under `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` | writes `true` |
| `apps.*` schema | user (manual DDL); repo file is the fresh-install record | records the columns the user already added |
| `apps.*` rows | gold-to-PostgreSQL load path (outside repo files read) | unchanged |
| `apps.*.ingestion_ts` value | no owner (D-2) | none |

## Grain and keys

Unchanged. See `model-design.md` `## Entities and grain` and `## Keys`. Neither new column joins a key.

## Ordering

1. The `srvactivepy` ALTER runs on Fabric DEV before `NB_GLD_SRV_POI_INFO` (16/11 version) runs there.
   - Why: `ensure_target` in `NB_LIB_TRANSFORM_SLV_GLD` does `ALTER TABLE ADD COLUMNS` without `AFTER` for a missing build column, so the column would land after `deleted_at`.
   - Consequence: `srvactivepy` would then stop with the "sai vị trí" hint and need a manual `ALTER COLUMN is_active AFTER is_bookable`.
   - Mitigation: the runbook pauses the `PL_VV_TRANS_SLV_TO_GLD_30M` trigger before syncing and resumes it after `srvactivepy` succeeds.
2. PostgreSQL columns must exist in every environment before a service build with the new entity fields is deployed there. Hibernate selects every mapped column, so a missing `ingestion_ts` or `is_active` causes SQL errors (HTTP 500) on every POI call. The user reports DEV PostgreSQL is altered. Any other environment needs the same manual ALTER first. The runbook lists this as a precondition, not as an agent step.
3. Repository order: this task's branch must contain `enrmergemd` / `enrmergepy` (task `20261112-enr-poi-append-to-merge`, now on the current branch). The new cell is appended after them.

## Transaction and commit boundaries

- `srvactivepy`: one Delta metadata commit (`ALTER TABLE ... ADD COLUMNS (is_active BOOLEAN AFTER is_bookable)`) inside the 30M flow lock, with a lock refresh just before it. No row commit.
- `NB_GLD_SRV_POI_INFO`: unchanged `run_node` path. One MERGE commit per run, skipped when the diff is empty.
- PostgreSQL file: the existing single `BEGIN; ... COMMIT;` for a fresh install. Unchanged structure.

## Idempotency

- `srvactivepy` re-run: schema already equals the contract, so it prints `=` and writes nothing.
- `row_hash` (model-design Q5): `add_row_hash` hashes every build column in DataFrame order except `hash_exclude`. Adding `is_active` changes `row_hash` for every row.
  - First run after deploy: `updated` = all live rows. Each gets `is_active = true` and a new `updated_at`. This is expected and accepted, and the runbook states it.
  - Later runs: hashes are stable, so there is no churn.
- Rows soft-deleted before deploy are not in the build output and are not matched for update, so they keep `is_active = NULL`. This is consistent with D-1 ("every row it writes"). The mapping §1.1 and runbook record it.

## Concurrency

- `srvactivepy` takes `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` with the same compare-and-set and 90-minute lease as `poidestpy`. It refreshes the lock and re-checks the owner before the ALTER, and releases the lock in `finally` with `raise failed from cleanup_exc`. A concurrent 30M run cannot MERGE during the ALTER.
- Readers of gold, such as the Copy Job, see an added nullable column. Name-based consumers are unaffected.

## Retry and recovery

| Failure | Recovery |
|---|---|
| Lock held by another run | Cell raises before writing; rerun later |
| Table missing | Stop; run `NB_SETUP_INITIAL_DDL` first |
| `is_active` present but misplaced (notebook ran first) | Stop with a hint. Manual `ALTER TABLE lh_vv_gold.dbo.gld_srv_poi_info ALTER COLUMN is_active AFTER is_bookable`, then rerun `srvactivepy`, which reports `=` |
| Schema differs in another way | Stop; investigate; no auto-fix |
| `NB_GLD_SRV_POI_INFO` fails after ALTER | Column exists with NULLs; fix and rerun (MERGE is idempotent) |
| Service deployed where PostgreSQL lacks columns | Roll back the service image, or the user applies the ALTER; no data impact |

## Partial failure

- ALTER succeeds and the cell then fails in the post-check or lock release: the schema is correct. Rerunning gives a no-op `=`.
- Gold has `is_active` but the PostgreSQL load path does not carry it: `apps.srv_poi_info.is_active` stays NULL. The API is unaffected because the field is not exposed. This is out of scope (model-design Q7) and listed as a runbook follow-up check.
- Physical column order: the existing PostgreSQL DB (manual `ADD COLUMN`) has `is_active` and `ingestion_ts` at the end of each table. A fresh install puts them after `is_bookable` / `deleted_at`. Loads must map by name. The SQL header and runbook state this.

## Observability

- `srvactivepy` prints `srvactive: +lh_vv_gold.dbo.gld_srv_poi_info.is_active` (added) or `=` (no-op).
- `run_node` logs: no "Bảng đích: ADDED" line when the order is respected. If it appears, the ordering was violated. `ctrl_log_table_run.updated` for the first run should be about the live row count.
- Post-run query (runbook): `SELECT count(*) FILTER/count_if(deleted_at IS NULL AND is_active IS NOT TRUE)` must be 0.
- No new metric is added. The value is constant.

## Security

No credentials, hosts or connection strings go into the repository or the runbook. PostgreSQL verification uses environment variables (`POSTGRES__DP_POI__*`) or an ignored `.env`. The new entity fields are not serialized, and there is no new endpoint.

## Rollout

1. Merge the repository changes.
2. Fabric DEV, following the runbook:
   - Pause the `PL_VV_TRANS_SLV_TO_GLD_30M` trigger and wait for any active run to finish.
   - Sync the workspace.
   - Run only cell `srvactivepy` of `NB_CREATE_DDL`.
   - Check `DESCRIBE` / the printed result.
   - Resume the trigger, or run the pipeline once.
   - Verify `is_active` on live rows, then check the load path.
3. Service: confirm that PostgreSQL in the target environment has `apps.srv_poi_info.is_active` and `ingestion_ts` on all five tables (`information_schema.columns`, read-only), then deploy. Run the docker compose smoke from the runbook.

## Rollback and forward recovery

- Gold: no DROP (Delta without column mapping; the patch cell forbids DROP and `columnMapping`). Rolling back the notebook to remove `is_active` from `OUT_COLS` makes `ensure_target` WARN about the extra column. The column keeps its values and becomes NULL on inserts, and `row_hash` changes again, causing one more full update. Forward fix is preferred.
- PostgreSQL: user-owned. The repository SQL is a fresh-install record only.
- Service: the previous image works against the altered DB because extra columns are ignored. The new image needs the columns.

## Alternatives

| Decision | Options | Selected and trade-off |
|---|---|---|
| Where the existing-table gold contract lives (model-design Q4) | A. Edit `poidestpy` `TABLE_COLS`. B. New cell `srvactivemd`/`srvactivepy`. C. Runbook-only manual ALTER | **B.** A rewrites an applied patch cell: `poidestpy` would then stop on any DEV table that lacks `is_active`, and it breaks `test_info_cover_seed_and_init_ddl`'s chain. C has no guarded, locked, idempotent script, and still breaks `test_initial_ddl_contract.py`. B follows precedent (one patch cell per task). Its cost is cell-tail shifts in 5 test files, 3 of them outside scope |
| `row_hash` | Include `is_active` / `hash_exclude=("is_active",)` | **Include.** `hash_exclude` would leave every existing row NULL, because MERGE only updates on a hash change, which breaks D-1. The cost is one full update on the first run |
| D-3 test exception | Per-table allowlist / subset check / single `PG_ONLY` map | **Single `PG_ONLY = {"ingestion_ts": (pg_type, java_type)}`** required on every table. A subset check would hide other drift |
| Cell-tail tests | Shift every index by 2 / strip helper | **Shift**, matching how the enr-merge task edited the same tests |

## Implementation plan

1. **Stop:** get user approval to add `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py` to `scope.files`.
2. `NB_SETUP_INITIAL_DDL` `init_tables`: after the source line `"        ('is_bookable', 'BOOLEAN', None),\n",` (spec `lh_vv_gold.dbo.gld_srv_poi_info`), insert `"        ('is_active', 'BOOLEAN', None),\n",`.
3. `NB_CREATE_DDL`: append a markdown cell `srvactivemd` and a code cell `srvactivepy` after `enrmergepy`. Use the same JSON shape as `enrmergemd`/`enrmergepy`: `metadata.microsoft.language = python`, `language_group = synapse_pyspark`, `execution_count: null`, `outputs: []`. Sources are under **NB_CREATE_DDL srvactive cells**.
4. `NB_GLD_SRV_POI_INFO` `srvinfobuild`:
   - In `OUT_COLS`, change `"is_bookable", "operating_hours"` to `"is_bookable", "is_active", "operating_hours"`.
   - In the `build` select, after `F.lit(None).cast("boolean").alias("is_bookable"),` add `F.lit(True).alias("is_active"),`. Keep the line comment-free or add `# D-1`.
   - In `srvinfomd`, add one line: `` `is_active`: hằng `true` mọi dòng ghi (D-1); không đọc nguồn, không theo `deleted_at`. ``
5. Mapping doc:
   - In §1.2, after the `is_bookable` row, add `| | boolean | true: hằng cho mọi dòng NB_GLD_SRV_POI_INFO ghi; không đọc nguồn, không theo deleted_at (D-1) | is_active |`.
   - In §1.1, add a bullet: `` `is_active` (D-1): `true` mọi dòng build trả. Dòng đã xoá mềm trước khi có cột (không còn trong build) giữ NULL. Lần chạy đầu sau khi thêm cột đổi `row_hash` mọi dòng sống (cập nhật toàn bộ một lần). ``
6. `gld_srv_serve.pg.sql`: replace with the FILE block below.
7. Entities:
   - `SrvPoiInfo`: after the `isBookable` field, add `@Column(name = "is_active")` / `private Boolean isActive;`.
   - All five entities: after `deletedAt`, add `@Column(name = "ingestion_ts")` / `private LocalDateTime ingestionTs;`. `LocalDateTime` is already imported in each.
8. Tests: see **Test changes**.
9. Write `runtime-runbook.md` (Vietnamese) per **Runbook content**. Record A-decisions in `decision.md` if the workflow allows: srvactivepy placement, accepted full `row_hash` update, `PG_ONLY` exception shape.
10. Run verification.

## NB_CREATE_DDL srvactive cells

`srvactivemd` source:

```
# [THÊM 16/11] 20261116-srv-poi-info-is-active

Thêm `is_active` BOOLEAN (cho phép NULL) vào `gld_srv_poi_info` sau `is_bookable` (D-1). `NB_GLD_SRV_POI_INFO` ghi `true` mọi dòng. Không đổi cạnh. Không DROP. Chạy lại không đổi gì.
Chạy trước khi publish `NB_GLD_SRV_POI_INFO` bản 16/11. Sau cell này không chạy lại `poidestpy` (hợp đồng `gld_srv_poi_info` trong đó là bản cũ).
```

`srvactivepy` source:

```python
# [THÊM 16/11] 20261116-srv-poi-info-is-active (D-1)
# gld_srv_poi_info: đúng hợp đồng -> không ghi; chỉ thiếu is_active -> thêm cột AFTER is_bookable; khác -> dừng trước khi ghi.
# Chỉ đổi schema: không ghi dòng, không đổi cạnh pipeline_config. Dòng cũ có is_active NULL tới lần chạy NB_GLD_SRV_POI_INFO kế tiếp.
# Chạy trước khi publish NB_GLD_SRV_POI_INFO bản 16/11. Sau cell này không chạy lại poidestpy.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M suốt cell. Chạy lại: không ghi.
import uuid

WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
INFO_FQ = "lh_vv_gold.dbo.gld_srv_poi_info"
NEW_COL = ("is_active", "BOOLEAN")
ANCHOR = "is_bookable"
TABLE_COLS = {
    "lh_vv_gold.dbo.gld_srv_poi_info": [
        ("poi_id", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
        ("business_sector", "STRING"), ("business_category", "STRING"), ("subcategory_tags", "STRING"),
        ("destination_id", "STRING"), ("destination_name", "STRING"), ("full_address", "STRING"),
        ("street", "STRING"), ("ward", "STRING"), ("district", "STRING"), ("city", "STRING"),
        ("country_code", "STRING"), ("postal_code", "STRING"), ("lat", "DOUBLE"), ("lng", "DOUBLE"),
        ("phone", "STRING"), ("email", "STRING"), ("website_url", "STRING"), ("operating_status", "STRING"),
        ("is_verified", "BOOLEAN"), ("is_recommended", "BOOLEAN"), ("is_bookable", "BOOLEAN"),
        ("is_active", "BOOLEAN"),
        ("operating_hours", "STRING"), ("holiday_exceptions", "STRING"), ("rating_overall", "DECIMAL(4,2)"),
        ("rating_count", "INT"), ("review_count", "INT"), ("cover_id", "STRING"), ("cover_blob_url", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
    ],
}
LOCK = "srvactive-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


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

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    if not spark.catalog.tableExists(INFO_FQ):
        raise RuntimeError(f"Dừng trước khi ghi: {INFO_FQ} chưa có: chạy NB_SETUP_INITIAL_DDL trước")
    want = _want(TABLE_COLS[INFO_FQ])
    got = _schema(INFO_FQ)
    todo = got != want
    if todo and got != [col for col in want if col[0] != NEW_COL[0]]:
        hint = ""
        if NEW_COL[0] in {col[0] for col in got}:
            hint = (
                f" ({NEW_COL[0]} sai vị trí: chạy tay "
                + "ALTER "
                + "TABLE "
                + f"{INFO_FQ} ALTER COLUMN {NEW_COL[0]} AFTER {ANCHOR})"
            )
        raise RuntimeError(f"Dừng trước khi ghi: {INFO_FQ} không khớp hợp đồng, không sửa: có {got}, cần {want}{hint}")

    def _refresh_lock():
        # STATE-001: gia hạn và kiểm lại chủ khoá ngay trước khi ghi.
        spark.sql(f"""
        UPDATE {WM}
        SET lock_at = current_timestamp(), updated_at = current_timestamp()
        WHERE watermark_id = '{WID}' AND lock_exec_id = '{LOCK}'
        """)
        owner = spark.sql(f"SELECT lock_exec_id FROM {WM} WHERE watermark_id = '{WID}'").first()
        if not owner or owner["lock_exec_id"] != LOCK:
            raise RuntimeError(f"Luồng {PL} mất khoá trước khi ghi")

    if todo:
        _refresh_lock()
        spark.sql(f"ALTER TABLE {INFO_FQ} ADD COLUMNS (`{NEW_COL[0]}` {NEW_COL[1]} AFTER `{ANCHOR}`)")

    # Sau khi ghi: chỉ xét phần cell thêm.
    if _schema(INFO_FQ) != want:
        raise RuntimeError(f"Sau khi ghi: {INFO_FQ} lệch cột")
    print(f"srvactive: {'+' if todo else '='}{INFO_FQ}.{NEW_COL[0]}")
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

`TABLE_COLS` keys must be string literals so that `ast.literal_eval` works in tests.

## Test changes

**`tests/test_srv_poi_serving_contract.py`**
- Add `PG_ONLY = {"ingestion_ts": ("timestamp without time zone", "LocalDateTime")}  # D-3: chỉ PostgreSQL, mọi bảng apps`.
- `test_gold_and_pg_columns_and_types_match`, per table:
  - Assert that `PG_ONLY` and the gold columns do not intersect.
  - For each `PG_ONLY` column, assert `pg[name]["cols"][col] == pg_type`.
  - Compare `set(spec["cols"]) == set(pg[name]["cols"]) - set(PG_ONLY)`.
- `test_entities_match_gold_columns_types_and_keys`: same pattern using the Java type.
- `test_info_cover_patch_cell`, `test_destination_name_patch_cell`: change the tail assertions to `ids[-8:-6]` srvcover, `ids[-6:-4]` poidest, `ids[-4:-2]` enrmerge, `ids[-2:] == ["srvactivemd", "srvactivepy"]`.
- `test_info_cover_build_rule`: remove `"is_active"` from the forbidden-token tuple.
- `test_info_cover_seed_and_init_ddl`:
  - Take `info` from the `srvactivepy` `TABLE_COLS`.
  - Assert that `poidest_info == cover[:at] + [destination_name] + cover[at:]`, which keeps the chain.
  - Assert `info == poidest_info` with `("is_active","BOOLEAN")` inserted after `is_bookable`.
- `test_destination_name_and_review_source_across_layers`: in the loop, use the `srvactivepy` cols for `lh_vv_gold.dbo.gld_srv_poi_info`.
- New `test_pg_only_ingestion_ts_and_is_active_positions`:
  - For every `pg_tables()` and `entity_tables()` entry, `names[names.index("deleted_at") + 1] == "ingestion_ts"`.
  - `srv_poi_info` in the PostgreSQL DDL, the entity, `init_tables`, and `OUT_COLS`: `is_bookable` is followed by `is_active`.
  - The PostgreSQL type of `is_active` is `boolean`, and the entity type is `Boolean`.
- New `test_new_columns_stay_out_of_api`:
  - Files under `src/main/java/.../api/` and `.../service/` contain none of `is_active`, `isActive`, `ingestion_ts`, `ingestionTs`.
  - No `notebooks/*.ipynb`, `docs/context/api-mapping/*.md` or `docs/poi-serving-api/**` file contains `ingestion_ts`.
  - Skip the service checks via `_require_service()`.

**`tests/test_gld_srv_poi_contract.py`**
- `test_info_rating_patch`, `test_review_source_patch_cell`: shift the tail by 2 and add `ids[-2:] == ["srvactivemd", "srvactivepy"]`.
- `test_build_columns_match_ddl`: `gold[INFO_FQ]` comes from the `srvactivepy` `TABLE_COLS`.
- New `test_info_is_active_patch_cell`:
  - `NEW_COL == ("is_active","BOOLEAN")` and `ANCHOR == "is_bookable"`.
  - `TABLE_COLS[INFO_FQ] == _insert_after(poidest[INFO_FQ], "is_bookable", NEW_COL)`.
  - `PL == plcadpy RENAMES[1][1]`.
  - Token order `["held = True", "Dừng trước khi ghi", "_refresh_lock()", "ADD COLUMNS", "Sau khi ghi", "finally:"]`.
  - Comment-free code has no `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE`, `columnMapping`, `INSERT`, `UPDATE {CFG}`, `MERGE INTO`.
  - `code.count("ALTER TABLE") == 1`, `code.count("ADD COLUMNS") == 1`, and `" AFTER "` is present.
  - `LEASE_MINUTES = 90`, `lock_exec_id = '{LOCK}'`, and `raise failed from cleanup_exc` are present.
- New `test_info_is_active_literal_true`:
  - `OUT_COLS` has `is_active` right after `is_bookable`.
  - The source has exactly one `F.lit(True).alias("is_active")`.
  - `hash_exclude` and `ctx.input(` do not reference `is_active`, and the cell has no `hash_exclude` at all.
  - The mapping row with target `is_active` has type `boolean`, a transform starting with `true`, and an empty source.

**Out-of-scope files (after approval)**
- `tests/test_initial_ddl_contract.py` lines 335 and 733: replace `poidest["lh_vv_gold.dbo.gld_srv_poi_info"]` with `_assign(_cell(<ddl>, "srvactivepy"), "TABLE_COLS")["lh_vv_gold.dbo.gld_srv_poi_info"]`.
- `tests/test_enr_poi_contract.py` 223-237 and `tests/test_poi_entity_contract.py` 635-649: shift every slice by -2 and add `assert ids[-2:] == ["srvactivemd", "srvactivepy"]`.

## Runbook content

`runtime-runbook.md`, in Vietnamese. No hosts or credentials.

**Preconditions**
- The branch has been merged.
- PostgreSQL DEV has the new columns, as the user reports. Read-only check: `SELECT table_name, column_name, data_type FROM information_schema.columns WHERE table_schema='apps' AND column_name IN ('is_active','ingestion_ts')`. Expect 6 rows: `srv_poi_media_gallery.is_active` already exists, plus `srv_poi_info.is_active` and 5 × `ingestion_ts`.

**Steps**
1. Pause the `PL_VV_TRANS_SLV_TO_GLD_30M` trigger and wait until `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` has `lock_exec_id` NULL.
2. Sync the workspace.
3. Run only cell `srvactivepy`. Expect `srvactive: +...is_active` (or `=` on a re-run).
4. `DESCRIBE lh_vv_gold.dbo.gld_srv_poi_info`: `is_active boolean` follows `is_bookable`.
5. Resume the trigger, or run the pipeline once. In `ctrl_log_table_run` for `gld_srv_poi_info`, `updated` is about the live row count. This is the one-time `row_hash` change.
6. `SELECT count_if(deleted_at IS NULL AND is_active IS NOT TRUE) FROM lh_vv_gold.dbo.gld_srv_poi_info` returns 0. Rows with `deleted_at` set may be NULL.
7. Follow-up check outside this task's scope: does the gold-to-PostgreSQL load carry `is_active` by column name? `apps` column order differs from gold for DBs altered by hand.
8. Service: run the docker compose smoke from `services/data-serving-service/AGENTS.md`. `GET /api/v1/pois` with the bearer token returns 200, and the JSON has no `is_active` or `ingestion_ts`.

**Recovery and rollback**
- Recovery table: as in **Retry and recovery** above.
- Rollback: as in **Rollback and forward recovery** above.
- Stop point: every Fabric step is user-run. The agent records results only.

## Verification

- `python -m pytest tests/test_srv_poi_serving_contract.py tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
- `python -m pytest tests -q`, to catch any other cell-order or contract coupling.
- `cd services/data-serving-service && mvnw.cmd -q -B test`. Testcontainers loads `gld_srv_serve.pg.sql`, so a Hibernate select of `is_active`/`ingestion_ts` proves that the SQL and entity agree.
- `python scripts/vv.py verify 20261116-srv-poi-info-is-active` (needs Docker).
- Runtime: the runbook steps above (later session; `runtime=pending`).

FILE: sql/postgres/gld_srv_serve.pg.sql
-- PostgreSQL DDL cho 5 bảng gold serving, schema apps. Task 20261029-pg-ddl-gld-srv-serve.
-- Nguồn cột: lh_vv_gold.dbo.gld_srv_poi_* (NB_SETUP_INITIAL_DDL cell init_tables, NB_CREATE_DDL).
-- Ngoại lệ (20261116-srv-poi-info-is-active D-3): ingestion_ts chỉ có ở PostgreSQL, trên mọi bảng apps, ngay sau deleted_at. Gold không có cột này; repo không có job ghi.
-- Khóa chính theo NodeSpec.pk của notebook NB_GLD_SRV_POI_* tương ứng.
-- Ánh xạ kiểu Fabric -> PostgreSQL (decision.md D-TYPE, D-BIGINT):
--   STRING       -> text
--   BOOLEAN      -> boolean
--   INT          -> integer
--   BIGINT       -> int8
--   DOUBLE       -> double precision
--   DECIMAL(p,s) -> numeric(p,s)
--   TIMESTAMP    -> timestamp without time zone
--   Kiểu khác    -> MISSING
-- NOT NULL chỉ ở cột gold NOT NULL; đó đều là cột khóa chính.
-- apps.srv_poi_review không có cột lang (decision.md D-LANG). Gold gld_srv_poi_review vẫn giữ lang.
-- Schema apps phải có sẵn. File không tạo schema, index, view hay quyền.
-- Chạy: psql -v ON_ERROR_STOP=1 -f <file>. Chạy lại sẽ lỗi "already exists" và rollback, không đổi gì.
-- DB đã có apps.srv_poi_info trước 20261108-gld-srv-poi-info-cover: chạy tay ALTER TABLE apps.srv_poi_info ADD COLUMN cover_id text, ADD COLUMN cover_blob_url text;
-- DB đã có bảng trước 20261112-poi-destination-name-api: chạy tay BEGIN; ALTER TABLE apps.srv_poi_info ADD COLUMN destination_name text; ALTER TABLE apps.srv_poi_review ADD COLUMN source_name text; COMMIT;
-- DB đã có bảng trước 20261116-srv-poi-info-is-active (người dùng đã chạy tay; ghi nhận, không phải lệnh cho agent):
--   ALTER TABLE apps.srv_poi_info ADD COLUMN is_active boolean;
--   ALTER TABLE apps.<srv_poi_info | srv_poi_multi_lang | srv_poi_amenity | srv_poi_media_gallery | srv_poi_review> ADD COLUMN ingestion_ts timestamp without time zone;
--   ADD COLUMN đặt cột ở cuối bảng: thứ tự vật lý khác CREATE TABLE dưới đây. Nạp dữ liệu phải theo tên cột.

BEGIN;

CREATE TABLE apps.srv_poi_info (
    poi_id text NOT NULL,
    poi_name text,
    source_name text,
    business_sector text,
    business_category text,
    subcategory_tags text,
    destination_id text,
    destination_name text,
    full_address text,
    street text,
    ward text,
    district text,
    city text,
    country_code text,
    postal_code text,
    lat double precision,
    lng double precision,
    phone text,
    email text,
    website_url text,
    operating_status text,
    is_verified boolean,
    is_recommended boolean,
    is_bookable boolean,
    is_active boolean,
    operating_hours text,
    holiday_exceptions text,
    rating_overall numeric(4, 2),
    rating_count integer,
    review_count integer,
    cover_id text,
    cover_blob_url text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    ingestion_ts timestamp without time zone,
    PRIMARY KEY (poi_id)
);

CREATE TABLE apps.srv_poi_multi_lang (
    poi_id text NOT NULL,
    lang text NOT NULL,
    source_name text,
    time_to_spend text,
    best_time text,
    cost_vnd text,
    description text,
    experience text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    ingestion_ts timestamp without time zone,
    PRIMARY KEY (poi_id, lang)
);

CREATE TABLE apps.srv_poi_amenity (
    poi_id text NOT NULL,
    business_sector text NOT NULL,
    amenity_group text NOT NULL,
    amenity_raw text NOT NULL,
    amenity text,
    amenity_en text,
    amenity_vi text,
    service_flags text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    ingestion_ts timestamp without time zone,
    PRIMARY KEY (poi_id, business_sector, amenity_group, amenity_raw)
);

CREATE TABLE apps.srv_poi_media_gallery (
    media_id text NOT NULL,
    poi_id text NOT NULL,
    source_name text,
    photo_api_uri text,
    display_order integer,
    width_px integer,
    height_px integer,
    photographer text,
    blob_url text,
    thumbnail_url text,
    is_cover boolean,
    is_active boolean,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    ingestion_ts timestamp without time zone,
    PRIMARY KEY (media_id, poi_id)
);

CREATE TABLE apps.srv_poi_review (
    review_id text NOT NULL,
    poi_id text,
    rating_overall numeric(4, 2),
    rating_count int8,
    title text,
    review_text text,
    rating numeric(4, 2),
    review_date text,
    author_name text,
    source_name text,
    row_hash text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone,
    deleted_at timestamp without time zone,
    ingestion_ts timestamp without time zone,
    PRIMARY KEY (review_id)
);

COMMIT;
END_FILE
