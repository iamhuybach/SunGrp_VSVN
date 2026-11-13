RESULT: PASS

## Main brief

### Decision
- PASS. Columns, types and keys come from `model-design.md` (second pass) and D-1..D-4.
- Existing lakehouses migrate through one new `NB_CREATE_DDL` cell pair, `poidestmd` and `poidestpy`, appended last. It holds the `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` lock and adds three columns with `ADD COLUMNS ... AFTER`. Edges do not change.
- Positions:
  - silver `destination_name` after `lng`
  - gold info `destination_name` after `destination_id`
  - gold review `source_name` after `author_name`
  - PostgreSQL columns at the same positions
- `data.destinations` is always `{id, name}` in compact and practical_info, built from one shared record, `CompactPoiResponse.Destinations`.
- Scope gap: `tests/test_initial_ddl_contract.py` and `tests/test_poi_entity_contract.py` must change but are not in `scope.files`.

### Invariants Main must preserve
- Gold info `OUT_COLS + TECH` == `init_tables` spec == `poidestpy` `TABLE_COLS["lh_vv_gold.dbo.gld_srv_poi_info"]` == mapping §1.2 targets. `destination_name` follows `destination_id`.
- Gold review `OUT_COLS + TECH` == `init_tables` spec == `poidestpy` `TABLE_COLS[review]` == mapping §2 targets. `source_name` follows `author_name`.
- `NB_GLD_SRV_POI_REVIEW` sets `source_name` only via `F.lit(SOURCE_NAME)`, `SOURCE_NAME = "google"`. No new input, and `.cast(` count stays 1.
- `NB_GLD_SRV_POI_INFO` changes only `DEST_COLS`, `OUT_COLS` and one metric. The partner-without-destination branch yields null through the existing `from_dest` loop.
- `poidestpy` has none of: DROP, DELETE, TRUNCATE, REPLACE, RESTORE, `columnMapping`, `INSERT`, `UPDATE {CFG}`. It has exactly one `ADD COLUMNS` statement, with `_refresh_lock()` before it. It stops before any write on an unknown state and is a no-op on rerun.
- PostgreSQL columns == gold columns (`STRING -> text`). Entity `@Column` names == PostgreSQL columns. There is no uncommented `ALTER` line in `gld_srv_serve.pg.sql`.
- Amenities `items[]` has only `amenity_code` and `service_flags`. `PoiService` never calls `getAmenityEn` or `getAmenityVi`. The entity keeps both fields.
- `practical_info` has no top-level `business_sector`. `business_tags.business_sector` stays.
- `icon_key` is the textual `keyword` of the same `experience` element, else null. Docs cite `apps.srv_poi_multi_lang.experience` and never `apps.srv_poi_multi_lang.keyword`.
- `AGENTS.md` D-10 is narrowed only for `srv_poi_review.source_name`. `source` and `lang` stay forbidden.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 0 | task-state `scope.files` | — | add `tests/test_initial_ddl_contract.py`, `tests/test_poi_entity_contract.py` | gate accepts scope |
| 1 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`: specs `slv_enr_poi_destination`, `gld_srv_poi_info`, `gld_srv_poi_review` | insert `('destination_name','STRING',None)` after `lng` and after `destination_id`; insert `('source_name','STRING',None)` after `author_name` | equals `poidestpy` `TABLE_COLS` |
| 2 | notebooks/NB_CREATE_DDL.ipynb | append `poidestmd` + `poidestpy` after `srvcoverpy` | doc `## Migration cell`, verbatim; fill the 3 `srvcoverpy` copy placeholders | the cell is the last 2 ids; new test passes |
| 3 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild`: `DEST_COLS`, `OUT_COLS`, `ctx.metrics.update` | add `destination_name` after `destination_id` in both tuples; add the metric `destination_name_filled` | T2 tests pass |
| 4 | same | `srvinfomd` | one line on D-1 | — |
| 5 | notebooks/NB_GLD_SRV_POI_REVIEW.ipynb | `srvrvbuild`: `SOURCE_NAME`, `review = rv.select(...)`, `OUT_COLS` | constant, literal column, append after `author_name` | `test_review_node_spec` and the new literal test pass |
| 6 | same | `srvrvmd` | one line on D-3 | — |
| 7 | sql/postgres/gld_srv_serve.pg.sql | header after line 17; `CREATE TABLE apps.srv_poi_info`; `CREATE TABLE apps.srv_poi_review` | commented manual BEGIN/ALTER x2/COMMIT; `destination_name text` after `destination_id`; `source_name text` after `author_name` | serving contract tests pass |
| 8 | .../entity/SrvPoiInfo.java | after `destinationId` | `@Column(name = "destination_name") private String destinationName;` | entity test passes |
| 9 | .../entity/SrvPoiReview.java | after `authorName` | `@Column(name = "source_name") private String sourceName;` | same |
| 10 | services/data-serving-service/AGENTS.md | `## Contract` bullet 3 (line 9) | text in doc `## PostgreSQL and service` | — |
| 11 | .../util/StoredJsonParser.java | `ExperienceDraft`, `experiences()` | add `keyword` = `textOrNull(element.get("keyword"))` | — |
| 12 | .../dto/PoiExperiencesResponse.java | `Item` | add `@JsonProperty("icon_key") String iconKey` | — |
| 13 | .../dto/PoiAmenityGroupResponse.java | `Item` | remove `amenityLabelEn` and `amenityLabelVi` | — |
| 14 | .../dto/CompactPoiResponse.java | record components; new nested `Destinations` | last component `Destinations destinations`; `record Destinations(String id, String name)` with `@JsonInclude(ALWAYS)` | — |
| 15 | .../dto/PoiPracticalInfoResponse.java | components; nested `Destinations` | remove the `businessSector` component; type `CompactPoiResponse.Destinations`; delete the nested record | — |
| 16 | .../dto/PoiReviewItemResponse.java | components | last `@JsonProperty("source_name") String sourceName` | — |
| 17 | .../service/PoiService.java | `getExperiences`, `getPracticalInfo`, `getAmenities`, `mapToCompactResponse`, `mapReview` | per doc `## PostgreSQL and service` | compiles; Java tests pass |
| 18 | docs/context/mapping_gld_srv_poi_info.md | §1.1, §1.2 row after `destination_id` | D-1 bullet; null list; row text in doc `## Docs` | `test_mapping_targets_match_out_cols` passes |
| 19 | docs/context/mapping_gld_srv_poi_review.md | §1, §2 row after `author_name` | D-3 bullet and row | `test_review_mapping_targets` passes |
| 20 | docs/context/api-mapping/amenities.md | `## Response` rows 8-9, `## Sample response` | delete, renumber, remove label keys | — |
| 21 | docs/context/api-mapping/compact.md | `## Response`, `## Sample response` | add a `destinations` row and key | api-mapping tests pass |
| 22 | docs/context/api-mapping/practical_info.md | `## Response` row 7 and row 20, sample | delete row 7, renumber, `{id, name}`, sample | same |
| 23 | docs/context/api-mapping/experiences.md | `## Tổng quan`, `## Response`, sample | `icon_key` row citing `experience` | same |
| 24 | docs/context/api-mapping/reviews.md | `## Response`, sample | `source_name` row and key | same |
| 25 | tests/test_srv_poi_serving_contract.py | `test_info_cover_patch_cell`, `test_info_cover_seed_and_init_ddl`, `test_review_entity_has_no_source_or_lang`; new tests | per doc `## Implementation plan` T1 | pass |
| 26 | tests/test_gld_srv_poi_contract.py | `test_build_columns_match_ddl`, `test_review_build_columns_match_ddl`, `test_info_rating_patch`, `test_review_source_patch_cell`, `test_partner_without_destination_branch`; new tests | per T2 | pass |
| 27 | tests/test_enr_poi_contract.py | ids block lines 223-235 | shift by -2 and add `ids[-2:] == ["poidestmd","poidestpy"]` | pass |
| 28 | tests/test_initial_ddl_contract.py (scope ext) | lines 322-338, 687-699, 720-724, 751-752 | read the 3 contracts from `poidestpy` `TABLE_COLS` | pass |
| 29 | tests/test_poi_entity_contract.py (scope ext) | lines 635-647 | shift by -2 and add the poidest pair | pass |
| 30 | PoiServiceTest.java | listed in doc `## Verification` | update and add tests | pass |
| 31 | PoiControllerIntegrationTest.java | listed in doc `## Verification` | update constructors and jsonPath; new practical_info test | pass |

### Order and stop points
1. **STOP (user/gate decision):** extend `scope.files` with the two test files (row 0). Run `git status notebooks/NB_CREATE_DDL.ipynb`. If task `20261112-enr-poi-append-to-merge` has appended cells, rebase the `ids[-N:]` shifts on that state.
2. Rows 1-6 (notebooks), then 25-29 (Python tests). Run the pytest command. All must pass before step 3.
3. Rows 7-10 (PostgreSQL DDL, entities, `AGENTS.md`), then rows 18-24 (docs). Rerun pytest, including `test_srv_poi_api_mapping_required.py`.
4. Rows 11-17 (Java), then 30-31. Run the targeted Maven tests (no Docker needed).
5. **STOP (evidence):** full `mvnw.cmd -q -B test` and `vv.py verify` need Docker, which is down. `gates.local_verification` passes only when `vv.py verify` passes with Docker.
6. Write `runtime-runbook.md` from doc `## Rollout` (local): fresh-volume DDL or the two-ALTER transaction, an `information_schema` check, synthetic seed, and `curl` of the five endpoints.
   - **STOP (user):** the user runs `docker compose`.
7. Do not run any notebook, cell, pipeline or Copy Job. No commit unless the user asks.

### Tests and verification
- `python -m pytest tests/test_enr_poi_contract.py tests/test_gld_srv_poi_contract.py tests/test_srv_poi_serving_contract.py tests/test_srv_poi_api_mapping_required.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py -q`
- New or renamed Python tests:
  - `test_srv_poi_serving_contract.py::test_destination_name_patch_cell`
  - `test_srv_poi_serving_contract.py::test_destination_name_and_review_source_across_layers`
  - `test_srv_poi_serving_contract.py::test_review_entity_source_name_only`
  - `test_gld_srv_poi_contract.py::test_review_source_name_literal`
  - `test_gld_srv_poi_contract.py::test_info_destination_name_passthrough`
- `cd services/data-serving-service && mvnw.cmd -q -B test -Dtest=PoiServiceTest,PoiControllerIntegrationTest`
- New or updated Java tests:
  - `PoiServiceTest#shouldReturnCompactDestinationsObjectWhenColumnsNull`
  - `PoiServiceTest#shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector`
  - updated `shouldFallBackExperiencesToViWhenTargetEmpty` (`icon_key` = walk / null / null)
  - `PoiControllerIntegrationTest#shouldReturnPracticalInfoWithoutTopLevelBusinessSector`
  - updated amenities `doesNotExist` for `amenity_label_en` and `amenity_label_vi`
- `cd services/data-serving-service && mvnw.cmd -q -B test` (Docker; Testcontainers loads the new DDL and entity mapping)
- `python scripts/vv.py verify 20261112-poi-destination-name-api` (Docker)
- `rg -n "getAmenityEn|getAmenityVi" services/data-serving-service/src/main` returns nothing.
- `rg -n "srv_poi_multi_lang\.keyword" docs` returns nothing.

### Read only if needed
- `## Scope gap` → rows 0, 28, 29
- `## Invariants` → rows 1-17, 25-26
- `## Migration cell` → row 2 (full cell source and the placeholder rule)
- `## Notebook transforms` → rows 1, 3-6
- `## PostgreSQL and service` → rows 7-17
- `## Docs` → rows 18-24
- `## Implementation plan` → rows 25-29 (per-test assertions)
- `## Verification` → rows 30-31, step 5
- `## Rollout`, `## Partial failure` → step 6 runbook; deploy order (PostgreSQL ALTER before the service, otherwise HTTP 500)
- `## Retry and recovery`, `## Idempotency` → reviewer questions on rerun, the ensure_target misorder, and the review `row_hash` one-time rewrite
- `## Alternatives and trade-offs` → reviewer questions on positions, the always-object `destinations`, and the shared DTO

# Architecture: 20261112-poi-destination-name-api

Inputs: `model-design.md` (second pass, `## Conflicts and questions`: Not applicable), ledger D-1..D-4. This design cites `model-design.md` `## Entities and grain`, `## Keys` and `## Columns`. It does not restate them.

Pre-edit stop: two test files outside `scope.files` must change. They are `tests/test_initial_ddl_contract.py` and `tests/test_poi_entity_contract.py`. See `## Scope gap`.

## Scope

- Silver DDL: `slv_enr_poi_destination.destination_name STRING` (D-1, DDL only).
- Gold DDL and transform:
  - `gld_srv_poi_info.destination_name`, copied 1-1 from silver.
  - `gld_srv_poi_review.source_name`, the literal `google` (D-3).
- Migration for existing lakehouses: one new `NB_CREATE_DDL` cell pair, `poidestmd` and `poidestpy`, appended at the end.
- PostgreSQL:
  - `apps.srv_poi_info.destination_name text` and `apps.srv_poi_review.source_name text` in `gld_srv_serve.pg.sql`.
  - Header comment with the manual `ALTER` for existing databases.
- Service:
  - Entities `SrvPoiInfo` and `SrvPoiReview`.
  - Five response contracts (`model-design.md` `## Scope`, D-4 bullets).
  - Edit the D-10 forbid line in the service `AGENTS.md`.
- Mapping docs and contract tests listed in `scope.files`.

## Non-goals

- Any writer for `slv_enr_poi_destination.destination_name`. The value stays null until a later load exists (D-1).
- Running any notebook, cell, pipeline, Copy Job, or Fabric probe. Data reload.
- The Copy Job column mapping from gold to PostgreSQL. It is not in the repo scope. See `## Rollout`, step 4.
- Dropping `amenity_en` or `amenity_vi` from any table.
- Dropping `business_sector` from any table.
- `docs/poi-serving-api/`. Task `20261110-serving-poi-read-apis`.

## Scope gap

These two files are not in `scope.files`, but the change breaks their assertions. No design avoids this.

- `tests/test_initial_ddl_contract.py`
  - Lines ~322-338, 687-699, 720-724 and 751-752 compare `init_tables` specs for:
    - `slv_enr_poi_destination`, against `srvpoipy` `DEST_BASE + DEST_NEW_COLS`.
    - `gld_srv_poi_info`, against `srvcoverpy` `INFO_COLS`.
    - `gld_srv_poi_review`, against `rvi18ngldpy` `REVIEW_COLS`.
  - Acceptance requires all three `init_tables` specs to change.
- `tests/test_poi_entity_contract.py`
  - Lines 635-647 pin the `NB_CREATE_DDL` cell ids by negative index, ending at `ids[-2:] == ["srvcovermd", "srvcoverpy"]`.
  - Appending `poidestmd` and `poidestpy` shifts every index by 2.

Options considered:
- Insert the new cells before `enrinfomd` so negative indices do not move. Rejected: the cell would sit before the cells whose contracts it extends, and a top-down run would stop on `srvcoverpy`.
- Mutate `srvcoverpy` or `rvi18ngldpy` in place. Rejected: those cells have already run, tests pin their constants, and history cells are append-only.

Decision: Main adds both files to `scope.files` before editing, with user or gate approval. The edits are mechanical (`## Implementation plan`, rows T5 and T6).

## Invariants

1. Silver `slv_enr_poi_destination` has 14 columns, in the order of `TABLE_COLS["lh_vv_silver.dbo.slv_enr_poi_destination"]` in `## Migration cell`. `destination_name` comes last, after `lng`.
2. Gold `gld_srv_poi_info` has 35 columns, with `destination_name` immediately after `destination_id`. These four sources are equal:
   - `NB_GLD_SRV_POI_INFO` `OUT_COLS + TECH`
   - the `init_tables` spec
   - `poidestpy` `TABLE_COLS`
   - `mapping_gld_srv_poi_info.md` §1.2 targets
3. Gold `gld_srv_poi_review` has `source_name` immediately after `author_name`. These four sources are equal:
   - `OUT_COLS + TECH`
   - the `init_tables` spec
   - `poidestpy` `TABLE_COLS`
   - `mapping_gld_srv_poi_review.md` §2 targets
4. `NB_GLD_SRV_POI_REVIEW` sets `source_name` only from `F.lit(SOURCE_NAME)` with `SOURCE_NAME = "google"`. There is no `slv_3p_poi` join and no new input.
5. `NB_GLD_SRV_POI_INFO`:
   - Reads `destination_name` only through `DEST_COLS` from `slv_enr_poi_destination`.
   - The partner-without-destination branch yields null, because the name is not in `ENTITY_OUT_COLS`.
   - `_require` still fails closed when the silver column is missing.
6. The PostgreSQL column set equals the gold column set. Types follow `STRING -> text`. Entity `@Column` names equal the PostgreSQL columns.
7. Response contracts:
   - Amenities `items[]` keys are exactly `amenity_code` and `service_flags`. `PoiService.getAmenities` does not call `getAmenityEn` or `getAmenityVi`.
   - `practical_info`: no top-level `data.business_sector`, but `data.business_tags.business_sector` stays.
   - `data.destinations` is always the object `{id, name}`, in both practical_info and compact.
   - Experiences: `items[].icon_key` is the textual `keyword` of the same `experience` element. If it is missing or not textual, it is null. It never comes from a column.
   - Reviews: `data[].source_name` is `apps.srv_poi_review.source_name`.
8. Mapping docs:
   - Cite only columns that exist in `gld_srv_serve.pg.sql`. `test_srv_poi_api_mapping_required.py::test_cited_source_columns_exist_in_ddl` enforces this.
   - `icon_key` cites `apps.srv_poi_multi_lang.experience` (key `keyword`). It never cites `apps.srv_poi_multi_lang.keyword`.
9. `poidestpy`:
   - Never issues DROP, DELETE, TRUNCATE, REPLACE, RESTORE, `columnMapping`, `INSERT`, or `UPDATE {CFG}`.
   - Issues exactly one `ALTER TABLE ... ADD COLUMNS ... AFTER` statement inside a loop.
   - Calls `_refresh_lock()` before each write.
10. `pipeline_config` keeps the same edges. No edge is added or toggled.

## State ownership

| state | owner | this task |
|---|---|---|
| `slv_enr_poi_destination` schema | `NB_SETUP_INITIAL_DDL` (fresh env) and `NB_CREATE_DDL` patch cells (existing env). No row writer (D-1) | adds 1 column |
| `gld_srv_poi_info` and `gld_srv_poi_review` rows | `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_REVIEW` through `run_node` MERGE on flow `PL_VV_TRANS_SLV_TO_GLD_30M` | build columns |
| gold schema | the same DDL cells. `ensure_target` auto-adds missing columns at the end, after `deleted_at` | the cell pre-empts that |
| `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` lock | the orchestrator and DDL patch cells | the cell holds it |
| `apps.*` schema | the data side: `gld_srv_serve.pg.sql` and manual `ALTER` | 2 columns |
| `apps.*` rows | the Copy Job (outside repo scope) | none |
| API contract | `services/data-serving-service` | 5 endpoints |

## Grain and keys

Unchanged. See `model-design.md` `## Entities and grain` and `## Keys`.
- `gld_srv_poi_info` and `apps.srv_poi_info` are keyed on `poi_id`.
- `gld_srv_poi_review` and `apps.srv_poi_review` are keyed on `review_id`.
- `apps.srv_poi_multi_lang` is keyed on `(poi_id, lang)`.
- The new columns are not part of any key.
- `_destination` still picks one silver row per `poi_id` by the latest `updated_at`. `destination_name` comes from that same row.

## Ordering

Within the code:
- Info: `DEST_COLS` gets `destination_name` right after `destination_id`. Because `from_dest` iterates `DEST_COLS[2:]`, the column flows through the existing loop with no new branch.
- Review: `OUT_COLS` gets `source_name` after `author_name`.

Within `poidestpy`: tables are processed in the order silver, then info, then review. Each table is checked, and the cell stops before any write if any table is in an unknown state.

Deployment ordering is in `## Rollout`.

## Transaction and commit boundaries

- Delta: each `ALTER TABLE ADD COLUMNS` is its own commit. There is no cross-table atomicity. The cell makes this safe because it accepts a per-table "done" state (`## Retry and recovery`).
- `NB_LIB_TRANSFORM_SLV_GLD` lists `ADD COLUMNS` as a non-data operation, next to `APPEND_INVALIDATING_OPS` at line ~105. So the ALTER does not invalidate the APPEND baseline of `gld_enr_poi_info`, which reads only `poi_id` from this silver table.
- PostgreSQL:
  - The fresh-database script is already wrapped in `BEGIN`/`COMMIT`.
  - For an existing database, the header comment tells the operator to run both `ALTER`s in one transaction.
- Service: unchanged `@Transactional(readOnly = true)`.

## Idempotency

- `poidestpy`: if a table already matches the target contract, that table is a no-op. A rerun after success writes nothing.
- Gold MERGE uses `row_hash = sha2(to_json(struct(...)))`. Spark `to_json` omits null fields by default.
  - `destination_name` is always null for now, so `gld_srv_poi_info` hashes do not change and no rows are rewritten.
  - `source_name = 'google'` changes every `gld_srv_poi_review` hash. The first run after deploy updates every row once (`updated_at` bump), then the table is stable. This is intended, because it fills the column.
- PostgreSQL DDL for a fresh database: a rerun fails with "already exists" and rolls back (existing behaviour).

## Concurrency

- Runtime: `poidestpy` holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` with `LEASE_MINUTES = 90`, the same as `srvcoverpy`. That flow reads the silver table and writes both gold tables.
- The `PL_VV_TRANS_SLV_TO_ENR_15M` lock is not taken:
  - That flow reads only `poi_id` from `slv_enr_poi_destination` at a pinned version.
  - `ADD COLUMNS` is a metadata commit and is not invalidating.
  - Taking two locks adds lock-ordering risk for no benefit.
- Repository: task `20261112-enr-poi-append-to-merge` (untracked) may also append `NB_CREATE_DDL` cells and shift the same index assertions. Whichever task lands second rebases the `ids[-N:]` assertions. Main checks `git status` on `NB_CREATE_DDL.ipynb` before editing.

## Retry and recovery

`poidestpy` classifies each table into one of three states:
1. **Done**: matches `TABLE_COLS`. For review, the accepted variant also covers the physical `lang` column after `poi_id`, the same as `rvi18ngldpy`.
2. **Missing only the new column**: the same list without the new column → `ALTER ... AFTER <anchor>`.
3. **Anything else**: stop before any write.

- A failure between ALTERs leaves some tables Done and some Missing. A rerun completes them.
- Lock lost (`_refresh_lock` raises): the cell records FAILED and releases the lock. Rerun.
- Known bad state: a new `NB_GLD_SRV_POI_REVIEW` ran before `poidestpy`. `ensure_target` then appended `source_name` after `deleted_at`. The cell stops with a hint, and the operator runs `ALTER TABLE lh_vv_gold.dbo.gld_srv_poi_review ALTER COLUMN source_name AFTER author_name` once, then reruns the cell.
- The info notebook cannot get ahead of the migration, because `_require(des, DEST_COLS, ...)` raises `ConfigError` first.

## Partial failure

| failure | effect | handling |
|---|---|---|
| Silver altered, gold not | The info node runs with the new code. Gold `ensure_target` appends `destination_name` at the end | Rollout runs the cell before publishing notebooks. If it happens anyway, the cell stops on info with the same manual `ALTER COLUMN ... AFTER destination_id` hint |
| Service deployed before the PostgreSQL `ALTER` | Hibernate selects `destination_name` / `source_name`, so every `srv_poi_info` and `srv_poi_review` query fails with SQL "column does not exist". Affected endpoints: compact, features, practical_info, reviews (HTTP 500) | Hard rollout invariant: run the `ALTER` before deploy. The runbook checks `information_schema.columns` first |
| PostgreSQL altered, Copy Job not remapped | New columns stay null. API returns `destination_name: null`, `source_name: null` | Acceptable. The contract allows null |
| Gold altered, PostgreSQL not | No API impact. Whether the Copy Job ignores or fails on an extra source column is outside repo evidence | Follow-up for the data side |

## Observability

- `NB_GLD_SRV_POI_INFO` `ctx.metrics.update(...)` adds `destination_name_filled=out.where("destination_name IS NOT NULL").count()`. It is expected to be 0 until a loader exists (D-1). It is a cheap proof that the passthrough works.
- `NB_GLD_SRV_POI_REVIEW`: no new metric. `row_hash` drives the expected one-time update count, which shows in the existing `ctrl_log_table_run` diff counts.
- `poidestpy` prints the added columns per table, for example `+[...]` / `=`.
- Service: no new logs. A non-textual `keyword` silently yields a null `icon_key` and does not warn, the same as `title` and `description`.

## Security

- No new PII:
  - `destination_name` is a place name.
  - `source_name` is a constant.
  - The `AGENTS.md` rule on `email`, `phone` and `author_name` is unchanged.
- No credentials or hosts.
- No request value reaches SQL. The PostgreSQL `ALTER`s are static text.
- The `AGENTS.md` edit narrows D-10 only for `source_name`. `source` and `lang` stay forbidden on `srv_poi_review`.

## Rollout

1. Merge the code. This task stops before step 2 because of the no-rerun constraint.
2. Fabric, run by the user later: run `NB_CREATE_DDL` cell `poidestpy` after confirming that `srvcoverpy` and `rvi18ngldpy` state is current.
3. Publish `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_REVIEW`. The next scheduled 30M run fills `gld_srv_poi_review.source_name`.
4. Each serving PostgreSQL database: run the two `ALTER`s in one transaction. Then update the data-side Copy Job mapping (outside the repo).
5. Deploy `data-serving-service`. This must not happen before step 4.

Local runtime for this task (`runtime-runbook.md`, run by the user):
- Fresh compose volume: `CREATE SCHEMA IF NOT EXISTS apps`, then `psql -v ON_ERROR_STOP=1 -f ../../sql/postgres/gld_srv_serve.pg.sql`.
- Existing volume: the two-`ALTER` transaction from the file header.
- Verify the columns with `SELECT column_name FROM information_schema.columns WHERE table_schema='apps' AND column_name IN ('destination_name','source_name')`.
- Seed synthetic rows.
- `curl` the five endpoints and check the changed keys.
- Main stops before `docker compose up`.

## Rollback and forward recovery

- Service: revert the commit. This is code only. The added PostgreSQL columns are harmless to the old entity, because Hibernate ignores unmapped columns.
- PostgreSQL: `ALTER TABLE ... DROP COLUMN` only after the old service is live. Optional.
- Delta: forward-only. Dropping columns needs column mapping, which the repo bans. To roll back the notebooks, revert them and leave the columns:
  - Info: `ensure_target` WARNs about the extra column, and the value stays null.
  - Review: existing rows keep `google`, and new inserts get null.
  - The `NB_SETUP_INITIAL_DDL` `schema_diff` would then report `thừa`. The forward fix is to re-land the change.
- If `poidestpy` was run and the code is reverted, `srvcoverpy` and `rvi18ngldpy` stop on rerun with "không khớp hợp đồng" before writing. That is safe.

## Alternatives and trade-offs

| decision | selected | rejected and why |
|---|---|---|
| Existing-env migration | New `poidestpy` cell under the 30M lock with strict per-table states | Rely on `ensure_target`: no silver writer, so the silver column is never added; gold columns would land after `deleted_at`, breaking positional contract cells; no lock. Edit old cells: already run, tests pin them |
| Gold info position | After `destination_id` | At the end: `test_info_cover_build_rule` pins `OUT_COLS[-3:]` to the cover columns, and it is less readable |
| Review position | After `author_name` | After `poi_id`: collides with the accepted physical `lang` variant |
| Silver position | After `lng` | After `destination_id`: matches how `DEST_NEW_COLS` were appended, and is the simplest ALTER |
| compact `destinations` | Always the object `{id, name}` | Null when both are null: inconsistent with practical_info row 20 ("Luôn") and the request literal shape. Cost: clients see `{id:null,name:null}` |
| `Destinations` DTO | One `CompactPoiResponse.Destinations(id, name)`, reused by practical_info like `Address` and `GeoLocation` | Two nested records named `Destinations` with different shapes: springdoc names schemas by simple name, so they collide |
| `icon_key` parsing | Extend `StoredJsonParser.ExperienceDraft` with `keyword` | Re-parse in `PoiService`: parses twice and splits the rule |

## Migration cell

Append a markdown cell `poidestmd`, then a code cell `poidestpy`, after `srvcoverpy`. Use the same cell metadata as `srvcoverpy`.

`poidestmd` source:

```
# [THÊM 12/11] 20261112-poi-destination-name-api

Thêm `destination_name` STRING (cho phép NULL) vào `slv_enr_poi_destination` (sau `lng`, D-1, không có luồng ghi) và `gld_srv_poi_info` (sau `destination_id`). Thêm `source_name` STRING vào `gld_srv_poi_review` (sau `author_name`, D-3). Không đổi cạnh. Không DROP. Chạy lại không đổi gì.
Sau cell này không chạy lại `srvpoipy`, `srvcoverpy`, `rvi18ngldpy` (hợp đồng trong đó là bản cũ).
```

`poidestpy` source:

```python
# [THÊM 12/11] 20261112-poi-destination-name-api (D-1, D-3)
# Mỗi bảng: đúng hợp đồng -> không ghi; chỉ thiếu cột mới -> ALTER ADD COLUMNS AFTER; khác -> dừng trước khi ghi.
# gld_srv_poi_review: chấp nhận lang vật lý sau poi_id như rvi18ngldpy. Không đổi cạnh pipeline_config.
# Chạy trước khi publish NB_GLD_SRV_POI_INFO / NB_GLD_SRV_POI_REVIEW bản 12/11.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M suốt cell. Chạy lại: không ghi.
import uuid

WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
NEW_COLS = {
    "lh_vv_silver.dbo.slv_enr_poi_destination": ("destination_name", "STRING"),
    "lh_vv_gold.dbo.gld_srv_poi_info": ("destination_name", "STRING"),
    "lh_vv_gold.dbo.gld_srv_poi_review": ("source_name", "STRING"),
}
TABLE_COLS = {
    "lh_vv_silver.dbo.slv_enr_poi_destination": [
        ("poi_id", "STRING NOT NULL"), ("street", "STRING"), ("ward", "STRING"), ("district", "STRING"),
        ("city", "STRING"), ("full_address", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
        ("destination_id", "STRING"), ("country_code", "STRING"), ("postal_code", "STRING"), ("lat", "DOUBLE"),
        ("lng", "DOUBLE"), ("destination_name", "STRING"),
    ],
    "lh_vv_gold.dbo.gld_srv_poi_info": [
        ("poi_id", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
        ("business_sector", "STRING"), ("business_category", "STRING"), ("subcategory_tags", "STRING"),
        ("destination_id", "STRING"), ("destination_name", "STRING"), ("full_address", "STRING"),
        ("street", "STRING"), ("ward", "STRING"), ("district", "STRING"), ("city", "STRING"),
        ("country_code", "STRING"), ("postal_code", "STRING"), ("lat", "DOUBLE"), ("lng", "DOUBLE"),
        ("phone", "STRING"), ("email", "STRING"), ("website_url", "STRING"), ("operating_status", "STRING"),
        ("is_verified", "BOOLEAN"), ("is_recommended", "BOOLEAN"), ("is_bookable", "BOOLEAN"),
        ("operating_hours", "STRING"), ("holiday_exceptions", "STRING"), ("rating_overall", "DECIMAL(4,2)"),
        ("rating_count", "INT"), ("review_count", "INT"), ("cover_id", "STRING"), ("cover_blob_url", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
    ],
    "lh_vv_gold.dbo.gld_srv_poi_review": [
        ("review_id", "STRING NOT NULL"), ("poi_id", "STRING"),
        ("rating_overall", "DECIMAL(4,2)"), ("rating_count", "BIGINT"), ("title", "STRING"),
        ("review_text", "STRING"), ("rating", "DECIMAL(4,2)"),
        ("review_date", "STRING"), ("author_name", "STRING"), ("source_name", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"),
        ("deleted_at", "TIMESTAMP"),
    ],
}
OLD_REVIEW_COL = ("lang", "STRING")
LOCK = "poidest-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


def _accepted(fq):
    want = _want(TABLE_COLS[fq])
    if fq.endswith(".gld_srv_poi_review"):
        return [want, want[:2] + _want([OLD_REVIEW_COL]) + want[2:]]
    return [want]


def _anchor(fq):
    names = [name for name, _dtype in TABLE_COLS[fq]]
    return names[names.index(NEW_COLS[fq][0]) - 1]


n_lock = spark.sql(f"SELECT count(*) AS n FROM {WM} WHERE watermark_id = '{WID}'").first()["n"]
if n_lock != 1:
    raise RuntimeError(f"{WM} không có đúng 1 dòng {WID}: chạy plcadpy trước")
held = False
failed = None
try:
    # (lock acquire: copy srvcoverpy verbatim: UPDATE ... lock_exec_id = '{LOCK}' ..., held = True, owner check)

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    todo = []
    for fq, (name, _dtype) in NEW_COLS.items():
        if not spark.catalog.tableExists(fq):
            issues.append(f"{fq} chưa có: chạy NB_SETUP_INITIAL_DDL hoặc cell tạo bảng trước")
            continue
        got = _schema(fq)
        if got in _accepted(fq):
            continue
        if got in [[col for col in want if col[0] != name] for want in _accepted(fq)]:
            todo.append(fq)
            continue
        hint = ""
        if name in {col[0] for col in got}:
            hint = f" ({name} sai vị trí: chạy tay ALTER TABLE {fq} ALTER COLUMN {name} AFTER {_anchor(fq)})"
        issues.append(f"{fq} không khớp hợp đồng, không sửa: có {got}, cần {_accepted(fq)[0]}{hint}")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    def _refresh_lock():
        # (copy srvcoverpy verbatim)
        ...

    for fq in todo:
        name, dtype = NEW_COLS[fq]
        _refresh_lock()
        spark.sql(f"ALTER TABLE {fq} ADD COLUMNS (`{name}` {dtype} AFTER `{_anchor(fq)}`)")

    # Sau khi ghi: chỉ xét phần cell thêm.
    problems = [f"{fq} lệch cột" for fq in NEW_COLS if _schema(fq) not in _accepted(fq)]
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print("poidest: " + "; ".join(f"{'+' if fq in todo else '='}{fq}.{NEW_COLS[fq][0]}" for fq in NEW_COLS))
except Exception as exc:
    failed = exc
    raise
finally:
    # (copy srvcoverpy finally block verbatim, including `raise failed from cleanup_exc`)
    ...
```

Main replaces the three `(copy srvcoverpy ...)` placeholders with the exact `srvcoverpy` lines: the lock acquire, the `_refresh_lock` body, and the `finally` release.
- Keep `lock_exec_id = '{LOCK}'` and `LEASE_MINUTES = 90`.
- Use no `CFG` reads. The `nb_name` precondition from `srvcoverpy` is not needed.
- The code has exactly one `ALTER TABLE` token, the `ADD COLUMNS ... AFTER` statement. The hint text puts `ALTER TABLE` inside a string, so write that hint as `"ALTER " + "TABLE"`, or have the test count `ALTER TABLE {fq} ADD COLUMNS` instead. Recommended: test for `code.count("ADD COLUMNS") == 1`.

## Notebook transforms

`NB_GLD_SRV_POI_INFO` cell `srvinfobuild`:
- `DEST_COLS = ("poi_id", "updated_at", "destination_id", "destination_name", "full_address", ...)`, otherwise unchanged.
- `OUT_COLS`: insert `"destination_name"` after `"destination_id"`.
- `ctx.metrics.update(...)`: add `destination_name_filled=out.where("destination_name IS NOT NULL").count()`.
- No other code change. The `from_dest` loop and `FROM_ENTITY` handle the column. The partner-without-destination branch gets `F.lit(None).cast("string")`.
- Cell `srvinfomd`: add one line, "`destination_name`: 1-1 từ `slv_enr_poi_destination` (D-1, hiện chưa có luồng ghi → NULL)."

`NB_GLD_SRV_POI_REVIEW` cell `srvrvbuild`:
- Add `SOURCE_NAME = "google"  # D-3: bảng nguồn thuộc luồng Google`.
- Add `F.lit(SOURCE_NAME).alias("source_name")` to the `review = rv.select(...)` list.
- `OUT_COLS`: append `"source_name"` after `"author_name"`.
- Keep `.cast(` count at 1.
- Cell `srvrvmd`: add one line about `source_name` = literal `google`.

`NB_SETUP_INITIAL_DDL` cell `init_tables`: insert the tuples at the positions in `TABLE_COLS` above, in the form `('destination_name', 'STRING', None)` and `('source_name', 'STRING', None)`.

## PostgreSQL and service

`sql/postgres/gld_srv_serve.pg.sql`:
- In `apps.srv_poi_info`: `destination_id text,` then `destination_name text,`.
- In `apps.srv_poi_review`: `author_name text,` then `source_name text,`.
- Add a header line after line 17: `-- DB đã có bảng trước 20261112-poi-destination-name-api: chạy tay BEGIN; ALTER TABLE apps.srv_poi_info ADD COLUMN destination_name text; ALTER TABLE apps.srv_poi_review ADD COLUMN source_name text; COMMIT;`
- No uncommented `ALTER` line. `test_info_cover_mapping_and_pg_ddl` asserts `(?m)^\s*ALTER\s` is absent.

Entities:
- `SrvPoiInfo`: `@Column(name = "destination_name") private String destinationName;` after `destinationId`.
- `SrvPoiReview`: `@Column(name = "source_name") private String sourceName;` after `authorName`.

DTOs:
- `CompactPoiResponse`:
  - Add a last component, `@Schema(description = "Điểm đến") Destinations destinations`.
  - Add a nested `@JsonInclude(ALWAYS) public record Destinations(@Schema(description = "apps.srv_poi_info.destination_id") String id, @Schema(description = "apps.srv_poi_info.destination_name") String name) {}`.
- `PoiPracticalInfoResponse`: remove the `businessSector` component. Change the type to `CompactPoiResponse.Destinations destinations`. Delete the nested `Destinations` record.
- `PoiAmenityGroupResponse.Item`: keep `amenity_code` and `service_flags` only.
- `PoiExperiencesResponse.Item(String title, String description, String source, @JsonProperty("icon_key") String iconKey)`.
- `PoiReviewItemResponse`: add a last component, `@JsonProperty("source_name") @Schema(description = "Nguồn đánh giá", example = "google") String sourceName`.

`StoredJsonParser`:
- `ExperienceDraft(String title, String description, String keyword)`.
- In `experiences()`: `items.add(new ExperienceDraft(title, description, textOrNull(element.get("keyword"))));`.
- The filter and the limit of 3 are unchanged.

`PoiService`:
- `getExperiences`: `new PoiExperiencesResponse.Item(item.title(), item.description(), source, item.keyword())`.
- `getPracticalInfo`:
  - Delete the 4th constructor argument `poi.getBusinessSector()` (line 178). The `BusinessTags` argument still passes it.
  - The last argument becomes `new CompactPoiResponse.Destinations(poi.getDestinationId(), poi.getDestinationName())`.
- `getAmenities`: `new PoiAmenityGroupResponse.Item(a.getAmenity(), a.getServiceFlags())`.
- `mapToCompactResponse`: append `new CompactPoiResponse.Destinations(poi.getDestinationId(), poi.getDestinationName())`.
- `mapReview`: append `review.getSourceName()`.

`services/data-serving-service/AGENTS.md` line 9 becomes:

`poi_id` never includes language. `srv_poi_review` has no `source` or `lang` (D-10 of task `20261106-agent-system-unify-api`). `srv_poi_review.source_name` is the gold literal `google` (D-3 of task `20261112-poi-destination-name-api`, superseding D-10 for `source_name` only).

## Docs

- `mapping_gld_srv_poi_info.md`:
  - §1.1: add one bullet for D-1. Update the `FROM_ENTITY` null list to `destination_id`, `destination_name`, `district`, `country_code`, `postal_code`.
  - §1.2: add a row after `destination_id`: `| slv_enr_poi_destination.destination_name | string | partner chưa có dòng destination: null; còn lại transform 1-1 (D-1: chưa có luồng ghi, hiện NULL) | destination_name |`. This must contain `null` and must not contain `slv_poi_entity_non_enrich` (`test_partner_without_destination_branch`).
- `mapping_gld_srv_poi_review.md`:
  - §1: add a D-3 bullet.
  - §2: add a row after `author_name`: `| | string | literal 'google' (D-3) | source_name |`.
- `amenities.md`: delete rows 8-9, renumber, and remove both label keys from the sample.
- `compact.md`: add a row `data[].destinations | object | có | apps.srv_poi_info.destination_id; apps.srv_poi_info.destination_name | Luôn {id, name}; name null tới khi có luồng ghi (D-1).` Add the matching key to the sample.
- `practical_info.md`:
  - Delete row 7 and renumber.
  - Row `data.destinations` cites both columns and says "Luôn `{id, name}`".
  - In the sample, remove top-level `business_sector`, keep it in `business_tags`, and add `destinations.name`.
- `experiences.md`:
  - Add a row `data.items[].icon_key | string | có | apps.srv_poi_multi_lang.experience | Khóa keyword của cùng phần tử; thiếu hoặc không phải text thì null (D-2).`
  - Mention `icon_key` in the description and the sample.
- `reviews.md`: add a row `data[].source_name | string | có | apps.srv_poi_review.source_name | Gold literal google (D-3).` Add it to the sample.

## Implementation plan

| # | file | anchor | change |
|---|---|---|---|
| N1 | NB_SETUP_INITIAL_DDL | `init_tables` 3 specs | `## Notebook transforms` |
| N2 | NB_CREATE_DDL | append `poidestmd`, `poidestpy` | `## Migration cell` |
| N3 | NB_GLD_SRV_POI_INFO | `srvinfobuild`, `srvinfomd` | `## Notebook transforms` |
| N4 | NB_GLD_SRV_POI_REVIEW | `srvrvbuild`, `srvrvmd` | `## Notebook transforms` |
| P1 | gld_srv_serve.pg.sql | header and 2 CREATEs | `## PostgreSQL and service` |
| J1-J9 | entities, DTOs, parser, service, AGENTS.md | as listed | `## PostgreSQL and service` |
| D1-D7 | docs | as listed | `## Docs` |
| T1 | test_srv_poi_serving_contract.py | `test_info_cover_patch_cell` | `ids[-4:-2]` is srvcover |
| T1 | same | `test_info_cover_seed_and_init_ddl` | the init spec equals `poidestpy` `TABLE_COLS[info]` and equals `srvcoverpy` `INFO_COLS` with `destination_name` inserted after `destination_id` |
| T1 | same | `test_review_entity_has_no_source_or_lang` | rename to `test_review_entity_source_name_only`: `"source_name"` is present; `'"lang"'` and `'"source"'` are absent |
| T1 | same | new `test_destination_name_patch_cell` | constants equal `## Migration cell`; `ids[-2:] == ["poidestmd", "poidestpy"]`; `PL` equals `plcadpy` `RENAMES[1][1]`; token order `held = True` < `Dừng trước khi ghi` < `_refresh_lock()` < `ADD COLUMNS` < `Sau khi ghi` < `finally:`; forbidden tokens from invariant 9; `code.count("ADD COLUMNS") == 1` and `" AFTER "` is present; `raise failed from cleanup_exc` is present |
| T1 | same | new `test_destination_name_and_review_source_across_layers` | silver, gold and PostgreSQL positions; `SrvPoiInfo` `destination_name` follows `destination_id`; `SrvPoiReview` `source_name` follows `author_name` |
| T2 | test_gld_srv_poi_contract.py | `test_build_columns_match_ddl`, `test_review_build_columns_match_ddl` | read contracts from `poidestpy` `TABLE_COLS` |
| T2 | same | `test_info_rating_patch`, `test_review_source_patch_cell` | shift each `ids[...]` by -2 and add the poidest pair |
| T2 | same | `test_partner_without_destination_branch` | `absent == ("destination_id", "destination_name", "district", "country_code", "postal_code")` |
| T2 | same | new `test_review_source_name_literal` | `SOURCE_NAME == "google"`; `'F.lit(SOURCE_NAME).alias("source_name")'` is in the source; `OUT_COLS[-2:] == ("author_name", "source_name")`; no `slv_3p_poi"` input |
| T2 | same | new `test_info_destination_name_passthrough` | `DEST_COLS[2:4] == ("destination_id", "destination_name")`; `OUT_COLS` has it after `destination_id`; `destination_name_filled` is in the source |
| T3 | test_enr_poi_contract.py | lines 223-235 | shift by -2 and add the poidest pair |
| T4 | Java tests | see `## Verification` | |
| T5 | test_initial_ddl_contract.py (scope ext) | lines 322-338, 687-699, 720-724, 751-752 | use `poidestpy` `TABLE_COLS` for the 3 tables instead of `DEST_NEW_COLS`, `srvcoverpy` and `rvi18ngldpy` |
| T6 | test_poi_entity_contract.py (scope ext) | lines 635-647 | shift by -2 and add the poidest pair |

## Verification

Python, no Spark:

```
python -m pytest tests/test_enr_poi_contract.py tests/test_gld_srv_poi_contract.py tests/test_srv_poi_serving_contract.py tests/test_srv_poi_api_mapping_required.py tests/test_initial_ddl_contract.py tests/test_poi_entity_contract.py -q
```

Java tests in `PoiServiceTest`:
- `shouldReturnCompactPoisSuccessfully`: add `destinationId` and `destinationName` and assert `destinations()`.
- New `shouldReturnCompactDestinationsObjectWhenColumnsNull`.
- `shouldMapAmenityColumnsToD01Fields`: drop the label asserts.
- `shouldFallBackExperiencesToViWhenTargetEmpty`: elements carry `"keyword":"walk"`, a missing keyword, and `"keyword":1`. Assert `iconKey` is `walk`, null, null.
- New `shouldReturnPracticalInfoDestinationsAndNoTopLevelBusinessSector`: serialize with `ObjectMapper`. Assert there is no top-level `"business_sector"` key outside `business_tags`, and assert `destinations.name`.
- `shouldReturnReviewsSuccessfully`: add `.sourceName("google")` and assert it.

Java tests in `PoiControllerIntegrationTest`:
- Update the constructors in `shouldReturnCompactPois`, `shouldSupportGetCompactPoisWithIdsAndAcceptLanguage`, `shouldReturnReviewsSuccessfully`, `shouldReturnExperiences` and `shouldReturnAmenitiesSuccessfully`.
- jsonPath checks:
  - `$.data[0].destinations.id` and `.name`.
  - `$.data[0].source_name`.
  - `$.data.items[0].icon_key`.
  - `$.data[0].items[0].amenity_label_en` and `amenity_label_vi` use `doesNotExist()`.
- New `shouldReturnPracticalInfoWithoutTopLevelBusinessSector`:
  - `$.data.business_sector` does not exist.
  - `$.data.business_tags.business_sector` exists.
  - `$.data.destinations.name` exists.

Commands:
- `cd services/data-serving-service && mvnw.cmd -q -B test -Dtest=PoiServiceTest,PoiControllerIntegrationTest`
- Then run the full `mvnw.cmd -q -B test` with Docker. `PoiRepositoryIntegrationTest` and `DataServingApplicationTests` load the new DDL and the entity mapping through Testcontainers.
- Gate: `python scripts/vv.py verify 20261112-poi-destination-name-api`. It needs JDK 26 and Docker. Docker is currently down, so this is a stop point.

Static checks:
- `rg -n "getAmenityEn|getAmenityVi" services/data-serving-service/src/main` returns nothing.
- `rg -n "srv_poi_multi_lang\.keyword" docs` returns nothing.

Runtime: the user runs `runtime-runbook.md` (`## Rollout`, local).
