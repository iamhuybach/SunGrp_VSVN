RESULT: PASS

## Main brief

### Decision

RESULT: PASS. The ledger rows D-MEDIA-12, D-MEDIA-SHAPE, U1–U7, Q9, Q11 and U-TIE fix grain, keys, row set and `pl_name`. This design settles model-design Q1–Q9 (doc `## Resolution of model-design questions`).
Silver union node plus two 1-1 gold copy nodes. RECOMPUTE → MERGE. Guarded `from_json` + `posexplode`. Two DDL patch cells, one per pipeline lock.
`is_cover` order is `display_order ASC NULLS LAST, _pos, media_id` (A7). When a POI has more than one row and every order is null, it has no cover (A8). Both need user confirmation but do not block.
Duplicate `media_id` makes the quality gate block the run. No dedupe (A9).

### Invariants Main must preserve

- One active owner per target: media silver and gallery → `PL_VV_TRANS_SLV_TO_GLD_30P`; gold amenity → `PL_VV_TRANS_SLV_TO_GLD_1H`, exact token. No duplicate edge 5-tuple.
- The `slv_poi_amenity` DDL, its 3 ENR edges and its retired edge are unchanged.
- The build is unique on the pk with no null pk. At most one `is_cover = true` per live `poi_id` (`unique_checks`). Exactly one when the POI has one row or any non-null order.
- Deterministic build: no `monotonically_increasing_id`, no unordered `first()`/`row_number()`, no timestamps in business columns. Second run: 0 inserts and 0 updates.
- `is_active` is `true` in every build. Soft delete sets it `false` on silver media and the gallery. Gold amenity `soft_delete_set = {}`.
- Gold business columns equal the source `OUT_COLS`. Gold timestamps come from the gold MERGE. No build returns `row_hash`/`created_at`/`updated_at`/`deleted_at`.
- Gold reads silver with `ctx.input(role)` (live_only default).
- Partner: only `vi`, `NOT coalesce(deleted,false)`. Fallback only when the i18n media is empty (SQL null, blank, `'null'`, `[]`). An unparsed document gives no rows and no fallback. Drop elements whose url is null or blank. `blob_url` is the raw url; `media_id` uses `trim(url)`.
- `NB_CREATE_DDL` patch cells and `NB_SETUP_INITIAL_DDL` have identical CREATE text and edge tuples.
- Patch cells hold `wm_flow__<PL>` and call `_refresh_lock()` before every write. `LEASE_MINUTES = 90`.

### Edit list

| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 0 | `.ai/tasks/.../task-state.yaml` (via vv.py) | `scope.files` | Add `tests/test_poi_media_amenity_contract.py`, `tests/test_initial_ddl_contract.py` | Validation passes |
| 1 | `notebooks/NB_CREATE_DDL.ipynb` | new `mediaddlmd` + `mediaddlpy` after `srvratepy` | PL 30P. `TABLE_COLS` (2 tables) + `EDGES_ON` (4 edges) from doc `### DDL patch cells`. Skeleton of `srvratepy`, without ALTER | DEV second run: 0 inserts; `test_setup_patch_guards` |
| 2 | `notebooks/NB_CREATE_DDL.ipynb` | new `amenddlmd` + `amenddlpy` after row 1 | PL 1H. 1 table, 1 edge | Same |
| 3 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_tables`, after the `gld_srv_poi_info` dict | 3 dicts, cols `(name, dtype, None)` equal to rows 1–2 | `test_ddl_parity_create_vs_init` |
| 4 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_seed_ctrl` | `_GLD1H` constant + 5 tuples after the `srvratepy` rows | `test_edges_create_vs_init` |
| 5 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb` | new; cells `slvmediamd/param/run/build/res/exit` | `slvmediabuild` = doc `### Silver build cell` verbatim | `test_node_specs`, `test_media_build_static`, fixture F1–F11 |
| 6 | `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb` | new; cells `srvgallery*` | Doc `### Gold build cells` (gallery) | `test_gold_copy_one_to_one` |
| 7 | `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb` | new; cells `srvamenity*` | Doc `### Gold build cells` (amenity) | Same |
| 8 | `tests/test_initial_ddl_contract.py` | `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_pipeline_config_rows_match_sources` | Read the new cells' `TABLE_COLS`/`EDGES_ON` with their own `PL`. Counts +3 tables, +5 edges (working tree now 18/61) | Green |
| 9 | `tests/test_poi_media_amenity_contract.py` | new | Tests below | Green |
| 10 | `docs/context/mapping_poi_media_info.md` | §1.2 row `is_cover` | Only if the user confirms or changes A7/A8: one sentence | Matches `decision.md` |

### Order and stop points

1. STOP (user decision): the working tree holds uncommitted edits from `20261025-gld-srv-poi-info-rating-review` in `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL` and `tests/test_initial_ddl_contract.py`. Commit them, or get the user's go-ahead, before rows 1–4 and 8.
2. Row 0. Record A1–A12 in `decision.md` (`Giả định còn lại`). Ask the user to confirm A7 (stable `media_id` pick among tied 3P rows) and A8 (no cover when there are several rows and every order is null). Not blocking; on an answer that changes them, edit only `with_cover` and row 10.
3. Rows 1–4 (DDL + edges), then rows 5–7 (nodes), then rows 8–9 (tests). Run the local tests.
4. STOP (runtime evidence, Fabric DEV): patch cells ×2 (R1); fixture F1–F11; `NB_00_ORCHES_SLV_TO_GLD` 30P PLAN then RUN ×2; 1H RUN ×2; R2–R8. Save to `runtime-runbook.md` and `evidence/results/`.
5. STOP (ops, outside the repo): a scheduled Fabric pipeline that passes `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_1H`. Until then gold amenity refreshes only by manual run. Report it; do not create it.

### Tests and verification

- `python -m pytest -q tests/test_poi_media_amenity_contract.py`: `test_node_specs`, `test_build_columns_match_ddl`, `test_ddl_parity_create_vs_init`, `test_edges_create_vs_init`, `test_amenity_untouched`, `test_gold_copy_one_to_one`, `test_media_build_static`, `test_setup_patch_guards`, `test_mapping_targets_match_out_cols`.
- Regression: `python -m pytest -q tests/test_initial_ddl_contract.py tests/test_poi_amenity_contract.py tests/test_gld_srv_poi_contract.py`, then `python -m pytest -q`.
- Runtime: fixture F1–F11 (`evidence/probes/media_build_fixture.py`); R1 second setup run inserts 0 edges; R2 one owner per target; R3 second RUN has 0 inserts and 0 updates (`DESCRIBE HISTORY`); R4 cover query returns 0 rows; R5 gold vs live silver `EXCEPT` returns 0 rows both ways; R6 `slv_poi_amenity` not written by 1H; R7 info and multi_lang SUCCESS in the 30P exec; R8 `qg_json` warnings recorded.

### Read only if needed

- `## Resolution of model-design questions` → rows 5–7, stop 2
- `## Architecture-owned decisions` (A3–A12) → rows 1–7
- `### DDL patch cells` → rows 1–4, 8
- `### Silver build cell` → row 5
- `### Gold build cells` → rows 6–7
- `## Invariants`, `## Idempotency`, `## Concurrency` → rows 1–2, 9
- `## Ordering`, `## Partial failure` → rows 5–7, stop 4
- `## Verification` → rows 8–9, stop 4
- `## Rollout`, `## Rollback and forward recovery` → stops 1, 4, 5

# Architecture: 20261025-poi-media-and-srv-amenity

## Verdict

Architecture round 2. `model-design.md` is current: it cites D-MEDIA-12, D-MEDIA-SHAPE, U1–U7, Q9, Q11 and U-TIE, and the full P1–P5 results. Grain, MERGE keys, row set, `pl_name` and value rules all come from the decision ledger. The nine questions left in `model-design.md` `## Conflicts and questions` are physical or determinism choices, and this design settles them in `## Resolution of model-design questions` without inventing business rules. Two readings, A7 (the 3P tie-break) and A8 (more than one row with every order null), should be confirmed by the user. Neither blocks: each is a one-expression change, and on DEV it affects at most 5 POIs (A7) or 0 POIs (A8).

## Scope

- New silver node `NB_SLV_POI_MEDIA_INFO` → `lh_vv_silver.dbo.slv_poi_media_info` (`model-design.md` `## Entities and grain`).
- New gold nodes `NB_GLD_SRV_POI_MEDIA_GALLERY` → `lh_vv_gold.dbo.gld_srv_poi_media_gallery` and `NB_GLD_SRV_POI_AMENITY` → `lh_vv_gold.dbo.gld_srv_poi_amenity`.
- DDL and ctrl edges for the three targets. `NB_CREATE_DDL` gets two dated patch cells, one per owning pipeline. `NB_SETUP_INITIAL_DDL` gets the same text in `init_tables` and `init_seed_ctrl`.
- Contract tests. They need two test files added to `scope.files` (see `## Implementation plan`).
- Mapping docs: `mapping_gld_srv_poi_amenity.md` §0/§1 are already written. `mapping_poi_media_info.md` changes only if the user confirms or changes A7/A8.

## Non-goals

- No change to the logic, grain, key, edges, DDL or `PL_VV_TRANS_SLV_TO_ENR_15P` rows of `slv_poi_amenity`.
- No change to the `NB_LIB_TRANSFORM_SLV_GLD` library. Everything used already exists: `NodeSpec`, `run_node`, `sql_merge_target`, `ensure_target`, `uuid_md5`, `quality_gate`, `soft_delete_set`, `ctx.warn`, `ctx.metrics`.
- No Fabric pipeline artifact. The scheduled Fabric pipeline that calls `NB_00_ORCHES_SLV_TO_GLD` with `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_1H` is not in the repo or in scope (see `## Rollout`).
- The partner element keys `description`, `is_cover` and `preview` are not mapped. The element key `is_cover` does not feed the target `is_cover`.

## Resolution of model-design questions

| model-design Q | Decision | Owner / basis |
|---|---|---|
| Q1 nullability | **A2.** Only MERGE key columns are `NOT NULL`: `media_id` on silver media and the gallery, and the four `slv_poi_amenity` keys on gold amenity. Every other column is nullable. Required silver fields are enforced before the MERGE by `block_checks` (`poi_id`, `source_name`, `is_cover`, `is_active` not null). | Architecture. Precedent: `gld_srv_poi_multi_lang` and `gld_srv_poi_info` DDL |
| Q2 `row_hash`, `deleted_at` | **A1.** All three tables carry `row_hash, created_at, updated_at, deleted_at` in `TECH_COLUMNS` order. These columns are owned by the library MERGE. A build never returns them (`add_row_hash` raises). | Library contract |
| Q3 gold amenity soft delete | `soft_delete_set = {}`. Only `deleted_at` and `updated_at` are set. No `is_active` column is added. | Mapping amenity §1 (no new business columns). Precedent: `NB_GLD_SRV_POI_MULTI_LANG` |
| Q4 gold read set | **A10.** Both gold nodes read silver with `ctx.input(role)` (`live_only=True`). Rows that silver soft-deleted are absent from the source, so gold soft-deletes them in the same run. | Architecture |
| Q5 several rows, every order null | **A8.** No cover. The ledger rule for more than one row is "the smallest non-null order", and no row meets it. The build counts these POIs in `ctx.warn("poi_without_cover")`. DEV: 0 such POIs (P1 `null_order = 0`; P5 has the single null order inside a document that also has int orders). | Literal D-MEDIA-12. **Confirm with the user** |
| Q6 duplicate `media_id` | **A9.** No dedupe. The quality gate's built-in duplicate-pk block stops the run before the MERGE, so the target is untouched. | Architecture (fail-closed, no invented row-set rule) |
| Q7 services row without a `vi` row | Produces no rows. Partner rows are driven by `vi` i18n rows. Services rows are read only as a fallback. | Mapping media §1.1 |
| Q8 `deleted` null | Kept. The filter is `NOT coalesce(deleted, false)`. `deleted` is boolean on both tables: the P2 `CASE WHEN deleted` ran. | U7 excludes rows marked deleted; null is not marked |
| Q9 1H token | The ctrl rows use `PL_VV_TRANS_SLV_TO_GLD_1H` exactly (U1, U1-1H). `_1H` matches `CADENCE_RE`. Reading `slv_poi_amenity`, which `_ENR_15P` owns, gives a cadence WARN, not an error (`build_dag`). | Ledger |

## Invariants

1. Each new target has exactly one active owner `pl_name`. `slv_poi_media_info` and `gld_srv_poi_media_gallery` belong to `PL_VV_TRANS_SLV_TO_GLD_30P`. `gld_srv_poi_amenity` belongs to `PL_VV_TRANS_SLV_TO_GLD_1H`. Each edge appears once per (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`).
2. The `slv_poi_amenity` DDL, its three ENR edges and its retired edge are unchanged.
3. The build output is unique on the MERGE key and has no null key (quality gate). MERGE never sees duplicate source keys.
4. Determinism: the same pinned inputs give byte-identical build rows. No `monotonically_increasing_id`, no unordered `first()`/`row_number()`, no `current_timestamp` in business columns. A second run on unchanged inputs inserts 0 rows and updates 0 rows.
5. At most one live row per `poi_id` has `is_cover = true` (`unique_checks`). Exactly one is true when the POI has one row or at least one non-null `display_order`.
6. `is_active` is `true` on every built row. Soft delete sets it to `false` (U6), on silver media and on the gallery.
7. The gold business columns equal the source business columns. The gallery has the 12 silver `OUT_COLS`. Gold amenity has the 7 `slv_poi_amenity` `OUT_COLS`. Gold timestamps come from the gold MERGE and are never copied.
8. An empty required input fails the node (`required_inputs`). It never soft-deletes the whole target.
9. `NB_CREATE_DDL` and `NB_SETUP_INITIAL_DDL` render identical CREATE text and identical edge tuples for the three targets.
10. The partner `blob_url` is the raw element `url`, not trimmed (Q11). Only `media_id` uses `trim(url)`.

## State ownership

| State | Owner | Writer |
|---|---|---|
| `slv_poi_media_info` business columns | `NB_SLV_POI_MEDIA_INFO.build` | `run_node` → `merge_target` |
| Gallery and gold amenity business columns | Silver source, copied 1-1 | Gold node MERGE |
| `row_hash`, `created_at`, `updated_at`, `deleted_at` (all three tables) | Library `add_row_hash` and `sql_merge_target` | MERGE only |
| Five new ctrl edges | `mediaddlpy` (4 edges, lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P`) and `amenddlpy` (1 edge, lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H`); `init_seed_ctrl` for a fresh environment | Setup cells |
| `wm_flow__PL_VV_TRANS_SLV_TO_GLD_1H` lock row | `amenddlpy` MERGE-if-missing; also `ensure_lock_row` in the orchestrator | Setup and orchestrator |
| Edge watermarks `wm_e__<trg>__<src>`, run logs | Library | Unchanged |
| `slv_3p_poi_media`, `slv_pn_*`, `slv_poi_amenity` | Existing owners (`FL_00`, `_ENR_15P`) | Read only here |

## Grain and keys

See `model-design.md` `## Entities and grain` and `## Keys`. Silver media and the gallery: one row per media item, MERGE key `media_id`. The 3P `media_id` is `media_dedup_key`. The partner `media_id` is `sha2(concat_ws('|','partner',poi_id,trim(url)),256)`. Gold amenity: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`). This design does not extend the model.

## Architecture-owned decisions

- **A3. Load mode.** All five edges are `load_mode = RECOMPUTE`, `priority = 1`, `nb_name = NB_<UPPER(trg_tbl)>`, so `write_mode = "MERGE"`. "Append" in mapping §1.1 is the in-build union.
- **A4. Partner parse.** `from_json` with an explicit `array<struct<url:string,order:int>>` schema, applied only when `trim(raw)` starts with `[`. This guards against Spark wrapping a root object into a one-element array; D-MEDIA-SHAPE found no root objects. Predicates: *empty* = SQL null, or trimmed `''` or `'null'`, or a parsed array of size 0 (U4). *Unparsed* = not empty and the parse is null. An unparsed document gives no rows and no fallback, and is counted in `partner_media_unparsed`.
- **A5. Fallback join.** `vi` i18n rows (not deleted) are left-joined to services rows (not deleted) on `business_service_id = id`, which equals the `poi_id` join because both sides use the same `uuid_md5(..., 'partner')`. `poi_id` is computed once, from the i18n id. The services array is used only when the i18n media is *empty*.
- **A6. Element filter.** `posexplode` keeps the 0-based array position `_pos`. Elements with a null or blank `url` are dropped (U3) and counted in `partner_url_dropped`. An element with a null `order` is kept.
- **A7. Cover order.** `row_number() OVER (PARTITION BY poi_id ORDER BY display_order ASC NULLS LAST, _pos ASC NULLS LAST, media_id ASC)`. For partner rows, "encountered first" is the array position. That is the literal meaning, and positions are unique per POI because each POI has one source document. 3P rows (5 tied POIs on DEV) have no physical encounter order in Spark: a Delta scan plus a shuffle gives no stable row order. So the stable existing key `media_id` stands in. Nothing is added to the table. This matches `Giả định còn lại` ("Không thêm cột sắp"), which round 1 framed as "no stored sort column". `_pos` is dropped before `select(*OUT_COLS)`. **Confirm with the user** that any stable pick among the tied 3P rows is acceptable.
- **A8 to A10.** See the resolution table.
- **A11. Required inputs.** Silver media: `("media_3p", "i18n")`. `services` is fallback-only, and an empty services table is valid. The gallery requires `("media",)`. Gold amenity requires `("amenity",)`. Trade-off: if `slv_poi_amenity` ever becomes legitimately empty, gold amenity fails instead of soft-deleting everything. That fail-closed behaviour is accepted.
- **A12. Two DDL patch cells.** One cell per owning pipeline, so each cell takes exactly one flow lock, as in the `srvpoipy`/`srvratepy` pattern. `LEASE_MINUTES = 90` in both, because both pipelines run through `NB_00_ORCHES_SLV_TO_GLD` with the default `p_lock_timeout_min` of 90.

## Alternatives

| Choice | Selected | Rejected | Trade-off |
|---|---|---|---|
| Media layering | Silver union node plus a 1-1 gold copy | Gold reads 3P and partner directly | `media_id` and `is_cover` are derived in one place, and gold stays 1-1 as mapping §2 says. Cost: one extra hop |
| Partner parse | Guarded `from_json` + `posexplode` | Python UDF; `get_json_object` per index | Vectorized, typed, keeps the position. Cost: the schema must be declared |
| 3P cover tie | Stable `media_id` | Nondeterministic window pick; `_first_seen_at` or `_last_seen_at` | A nondeterministic pick flips `row_hash` between runs and makes the gallery cover flicker, which breaks invariant 4. The timestamp columns would invent a business meaning ("oldest" or "newest" wins) that the user did not give |
| Duplicate `media_id` | Block the run | Keep the first by `_pos` | Nothing is dropped silently, at the cost of halting the media node until the source is fixed. DEV raw `dup_url_docs = 0` |
| DDL | Explicit DDL in both setup notebooks | `ensure_target` CREATE only | Parity is required by the request, and keys are NOT NULL. A contract test keeps the two notebooks in sync |
| Patch cells | One per pipeline lock | One cell taking two locks | Same lock discipline as the existing cells, and simpler to release on failure |

## Ordering

- Within `_30P`, the edge `slv_poi_media_info → gld_srv_poi_media_gallery` makes `build_dag` run silver before the gallery in the same exec. The gallery reads the silver version that run just committed (pinned).
- The silver media node reads `slv_3p_poi_media` and `slv_pn_*`, which `FL_00` owns. Those are external inputs, and the latest committed versions are pinned at run start.
- `_1H` reads `slv_poi_amenity`, which `_ENR_15P` owns. Gold amenity lags silver by at most one `_1H` cycle plus one `_15P` cycle. That is accepted for a 1-1 serving copy.
- The media nodes are an independent DAG branch from `gld_srv_poi_info` and `gld_srv_poi_multi_lang`. A media failure marks its child SKIPPED, but the info and multi_lang nodes still run.

## Transaction and commit boundaries

- One Delta MERGE per node is the only commit. The silver union and the cover window are computed fully before the MERGE, so there is no per-branch commit.
- The quality gate (pk null or duplicate, `unique_checks`, `block_checks`) runs before the MERGE. A block leaves the target at its previous version.
- Setup cells, in order: take the lock, run every pre-write check, `_refresh_lock`, `CREATE TABLE IF NOT EXISTS` for each table, `_refresh_lock`, one `INSERT … WHERE NOT EXISTS` of the edges, post-write checks, release the lock in `finally`. Tables exist before any edge points at them.

## Idempotency

- Nodes: MERGE on the pk with the `row_hash` guard. Invariant 4 makes a rerun a no-op. RECOMPUTE soft-deletes keys that disappear and revives keys that reappear (`deleted_at` cleared, `is_active` taken from the build).
- Setup: `CREATE TABLE IF NOT EXISTS`, and the edge insert is guarded by `NOT EXISTS` on (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`). A second run inserts 0 rows. A post-write check requires the active edge set to equal exactly the cell's set, with `n = 1` each.
- `NB_SETUP_INITIAL_DDL`: the existing `init_plan` duplicate checks (`_dup_keys`, `_target_dup_keys`) cover the five new tuples with no code change.

## Concurrency

- Each setup cell holds `wm_flow__<PL>` with `_refresh_lock` before each write (STATE-001 pattern), and aborts if it does not own the lock. The orchestrator therefore never reads half-seeded edges.
- Nodes run under the library's flow lock for their pipeline. Each target has one owning pipeline (invariant 1), so no target has two writers.
- `_1H` reads `slv_poi_amenity` while `_15P` writes it. Delta snapshot isolation and the pinned read version make this safe.

## Retry and recovery

- MERGE retries come from the library. A failed node leaves its target at the prior version. The next run recomputes everything (RECOMPUTE), so no manual repair is needed.
- If a setup cell fails after CREATE and before the edge insert, the tables exist with no edges. That is harmless, and a rerun completes it. A pre-write check failure writes nothing.
- A lock held by a crashed setup cell expires after `LEASE_MINUTES`.

## Partial failure

- Silver media succeeds and the gallery fails: the gallery stays on its old version and catches up on the next run.
- Silver media blocks (duplicate `media_id`, null `poi_id`, two covers): the gallery is SKIPPED and both tables keep their old versions. The `_30P` run is marked failed, and the info and multi_lang nodes still run.
- Unparsed partner documents and dropped null-url elements never fail the run. They are counted.

## Observability

Everything lands in the existing `qg_json` of `ctrl_log_table_run`. No new table.

- Silver warnings (`ctx.warn`): `partner_media_unparsed`, `partner_url_dropped`, `poi_without_cover`.
- Silver metrics (`ctx.metrics`): `partner_fallback_docs`.
- Quality-gate blocks: `one_cover_per_poi`, `media_required_null`, plus the built-in pk null and duplicate blocks.
- Gold nodes: the library row counts only.

## Security

Not applicable: no credentials, external calls or new PII. The media URLs already exist in silver, and the probes print aggregates only.

## Rollout

0. Precondition (user decision): the working tree has uncommitted edits from task `20261025-gld-srv-poi-info-rating-review` in `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL` and `tests/test_initial_ddl_contract.py`. Commit them, or get the user's go-ahead, before this task edits the same files. Otherwise a rollback of this task would also revert that task's work.
1. Merge. On DEV, run `mediaddlpy` and then `amenddlpy` in `NB_CREATE_DDL`. Run each a second time: no inserts, no schema change.
2. Run the fixture probe (see `## Verification`, Runtime F1–F11) in a DEV Spark session. It only creates in-memory DataFrames.
3. Run `NB_00_ORCHES_SLV_TO_GLD` with `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_30P`, `p_mode = PLAN`, then `RUN` twice.
4. Do the same with `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_1H`.
5. Ops dependency (outside the repo): a scheduled Fabric pipeline that passes `p_pl_name = PL_VV_TRANS_SLV_TO_GLD_1H`. Until it exists, gold amenity refreshes only on a manual run. The existing `_30P` pipeline picks up the media nodes from ctrl automatically.

## Rollback and forward recovery

- Rollback (manual DEV SQL, not a patch cell, because patch cells must not `UPDATE {CFG}`): under the owning flow lock, set the five new edges to `is_active = 0`, then drop the three new tables. `slv_poi_amenity` and the existing `_30P` nodes are untouched. In git, revert only this task's commit.
- Forward fix: correct the build and rerun. RECOMPUTE re-derives every row, and a changed `row_hash` updates rows in place. Changing the A7 or A8 expression moves `is_cover` for the affected POIs only.

## Implementation plan

Before editing tests, Main adds `tests/test_poi_media_amenity_contract.py` (new) and `tests/test_initial_ddl_contract.py` (count and cell updates) to `scope.files`.

| # | File | Anchor | Change |
|---|---|---|---|
| 1 | `notebooks/NB_CREATE_DDL.ipynb` | new `mediaddlmd` + `mediaddlpy` after `srvratepy` | `PL = PL_VV_TRANS_SLV_TO_GLD_30P`. `TABLE_COLS` for 2 tables and `EDGES_ON` with 4 edges (see `### DDL patch cells`). Copy the `srvratepy` lock/check/insert/finally skeleton. No ALTER |
| 2 | `notebooks/NB_CREATE_DDL.ipynb` | new `amenddlmd` + `amenddlpy` after row 1 | `PL = PL_VV_TRANS_SLV_TO_GLD_1H`. 1 table, 1 edge. Same skeleton |
| 3 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_tables`, after the `gld_srv_poi_info` dict | 3 dicts, same columns as rows 1–2, `(name, dtype, None)` |
| 4 | `notebooks/NB_SETUP_INITIAL_DDL.ipynb` | `init_seed_ctrl` | `_GLD1H = "PL_VV_TRANS_SLV_TO_GLD_1H"`. Append the 5 tuples after the `srvratepy` rows |
| 5 | `notebooks/NB_SLV_POI_MEDIA_INFO.ipynb` | new; cells `slvmediamd/param/run/build/res/exit` laid out like `NB_GLD_SRV_POI_MULTI_LANG` | `### Silver build cell` |
| 6 | `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb` | new; cells `srvgallery*` | `### Gold build cells` |
| 7 | `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb` | new; cells `srvamenity*` | `### Gold build cells` |
| 8 | `tests/test_initial_ddl_contract.py` | `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_pipeline_config_rows_match_sources` | Read `TABLE_COLS` and `EDGES_ON` (each with its own `PL`) from the two new cells. Table count +3, edge count +5 against the working-tree values (currently 18 and 61) |
| 9 | `tests/test_poi_media_amenity_contract.py` | new | Tests in `## Verification` |
| 10 | `docs/context/mapping_poi_media_info.md` | §1.2 row `is_cover` | Only if the user confirms or changes A7/A8: one sentence with the confirmed rule |

### DDL patch cells

```python
MEDIA_COLS = [
    ("media_id", "STRING NOT NULL"), ("poi_id", "STRING"), ("source_name", "STRING"), ("photo_api_uri", "STRING"),
    ("display_order", "INT"), ("width_px", "INT"), ("height_px", "INT"), ("photographer", "STRING"),
    ("blob_url", "STRING"), ("thumbnail_url", "STRING"), ("is_cover", "BOOLEAN"), ("is_active", "BOOLEAN"),
    ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
]
TABLE_COLS = {  # mediaddlpy
    "lh_vv_silver.dbo.slv_poi_media_info": MEDIA_COLS,
    "lh_vv_gold.dbo.gld_srv_poi_media_gallery": MEDIA_COLS,
}
EDGES_ON = [  # (seq, src_tbl, trg_schema, trg_tbl, load_mode, nb_name, priority); src_schema = SLV
    (1, "slv_3p_poi_media", "lh_vv_silver.dbo", "slv_poi_media_info", "RECOMPUTE", "NB_SLV_POI_MEDIA_INFO", 1),
    (2, "slv_pn_business_service_i18ns", "lh_vv_silver.dbo", "slv_poi_media_info", "RECOMPUTE", "NB_SLV_POI_MEDIA_INFO", 1),
    (3, "slv_pn_business_services", "lh_vv_silver.dbo", "slv_poi_media_info", "RECOMPUTE", "NB_SLV_POI_MEDIA_INFO", 1),
    (4, "slv_poi_media_info", "lh_vv_gold.dbo", "gld_srv_poi_media_gallery", "RECOMPUTE", "NB_GLD_SRV_POI_MEDIA_GALLERY", 1),
]
# amenddlpy
TABLE_COLS = {"lh_vv_gold.dbo.gld_srv_poi_amenity": [
    ("poi_id", "STRING NOT NULL"), ("business_sector", "STRING NOT NULL"), ("amenity_group", "STRING NOT NULL"),
    ("amenity_raw", "STRING NOT NULL"), ("amenity", "STRING"), ("amenity_vi", "STRING"), ("service_flags", "STRING"),
    ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
]}
EDGES_ON = [(1, "slv_poi_amenity", "lh_vv_gold.dbo", "gld_srv_poi_amenity", "RECOMPUTE", "NB_GLD_SRV_POI_AMENITY", 1)]
```

Differences from `srvratepy`:

- `_edge_rows` filters `(trg_schema, trg_tbl) IN` the cell's targets.
- `_create_sql(fq, cols)` must equal the `init_tables` `create_sql(spec)` (copy from `srvpoipy`).
- Pre-write issues:
  - a source table is missing (`slv_3p_poi_media`, `slv_pn_business_service_i18ns`, `slv_pn_business_services`, or `slv_poi_amenity`);
  - an existing target whose `_schema` differs from `_want`;
  - an active edge into a target in another `pl_name`;
  - a row of this `PL` that is not in `EDGES_ON` or has `n != 1`.
- Post-write: every table schema equals `_want`, and the active edge set equals `EDGES_ON` exactly.
- Forbidden tokens: `DROP`, `DELETE`, `TRUNCATE`, `UPDATE {CFG}`, `ALTER TABLE`.

### Silver build cell

```python
from pyspark.sql import Window

GOOGLE, PARTNER = "google", "partner"
MEDIA_3P_COLS = ("media_dedup_key", "poi_id", "photo_api_uri", "display_order", "width_px", "height_px",
                 "photographer", "blob_url")
OUT_COLS = ("media_id", "poi_id", "source_name", "photo_api_uri", "display_order", "width_px", "height_px",
            "photographer", "blob_url", "thumbnail_url", "is_cover", "is_active")
MEDIA_SCHEMA = T.ArrayType(T.StructType([T.StructField("url", T.StringType()),
                                         T.StructField("order", T.IntegerType())]))


def _require(df, cols, name):
    missing = [c for c in cols if c not in df.columns]
    if missing:
        raise ConfigError(f"slv_poi_media_info: {name} thiếu {missing}")


def _live(df):
    return df.where(~F.coalesce(F.col("deleted"), F.lit(False)))


def media_state(raw):
    """(mảng, rỗng, không parse được). Rỗng: SQL null, trắng, JSON null, []. Chỉ parse chuỗi bắt đầu bằng '['."""
    blank = raw.isNull() | F.trim(raw).isin("", "null")
    parsed = F.when(F.trim(raw).startswith("["), F.from_json(raw, MEDIA_SCHEMA))
    empty = blank | (parsed.isNotNull() & (F.size(parsed) == 0))
    return parsed, empty, ~blank & parsed.isNull()


def google_media(media):
    return media.select(F.col("media_dedup_key").alias("media_id"), "poi_id", F.lit(GOOGLE).alias("source_name"),
                        "photo_api_uri", "display_order", "width_px", "height_px", "photographer", "blob_url",
                        F.lit(None).cast("int").alias("_pos"))


def partner_media(i18n, services, ctx=None):
    vi = (_live(i18n).where(F.col("locale") == "vi")
          .select(F.col("business_service_id").alias("_sid"),
                  uuid_md5(F.col("business_service_id"), F.lit(PARTNER)).alias("poi_id"), F.col("media").alias("_mi")))
    svc = _live(services).select(F.col("id").alias("_sid"), F.col("media").alias("_ms"))
    arr_i, empty_i, bad_i = media_state(F.col("_mi"))
    arr_s, _empty_s, bad_s = media_state(F.col("_ms"))
    docs = (vi.join(svc, "_sid", "left")
            .select("poi_id", F.when(empty_i, arr_s).otherwise(arr_i).alias("_arr"), empty_i.alias("_fallback"),
                    F.when(empty_i, bad_s).otherwise(bad_i).alias("_bad")))
    elems = docs.select("poi_id", F.posexplode("_arr").alias("_pos", "_e"))
    url = F.col("_e.url")
    kept = elems.where(url.isNotNull() & (F.trim(url) != ""))
    if ctx is not None:
        ctx.warn("partner_media_unparsed", docs.where("_bad").count())
        ctx.warn("partner_url_dropped", elems.count() - kept.count())
        ctx.metrics["partner_fallback_docs"] = docs.where("_fallback AND size(_arr) > 0").count()
    return kept.select(
        F.sha2(F.concat_ws("|", F.lit(PARTNER), F.col("poi_id"), F.trim(url)), 256).alias("media_id"), "poi_id",
        F.lit(PARTNER).alias("source_name"), F.lit(None).cast("string").alias("photo_api_uri"),
        F.col("_e.order").alias("display_order"), F.lit(None).cast("int").alias("width_px"),
        F.lit(None).cast("int").alias("height_px"), F.lit(None).cast("string").alias("photographer"),
        url.alias("blob_url"), "_pos")


def with_cover(df):
    order = Window.partitionBy("poi_id").orderBy(F.col("display_order").asc_nulls_last(),
                                                 F.col("_pos").asc_nulls_last(), F.col("media_id").asc())
    single = F.count(F.lit(1)).over(Window.partitionBy("poi_id")) == 1
    first = (F.row_number().over(order) == 1) & F.col("display_order").isNotNull()
    return df.withColumn("is_cover", single | first)


def build(ctx):
    media, i18n, services = ctx.input("media_3p"), ctx.input("i18n"), ctx.input("services")
    _require(media, MEDIA_3P_COLS, "slv_3p_poi_media")
    _require(i18n, ("business_service_id", "locale", "media", "deleted"), "slv_pn_business_service_i18ns")
    _require(services, ("id", "media", "deleted"), "slv_pn_business_services")
    rows = with_cover(google_media(media).unionByName(partner_media(i18n, services, ctx)))
    rows = rows.withColumn("thumbnail_url", F.lit(None).cast("string")).withColumn("is_active", F.lit(True))
    covers = rows.groupBy("poi_id").agg(F.max(F.col("is_cover").cast("int")).alias("_c"))
    ctx.warn("poi_without_cover", covers.where("_c = 0").count())
    return rows.select(*OUT_COLS)


SPEC = NodeSpec(
    trg_tbl="slv_poi_media_info",
    inputs={"media_3p": "slv_3p_poi_media", "i18n": "slv_pn_business_service_i18ns",
            "services": "slv_pn_business_services"},
    pk=("media_id",),
    build=build,
    required_inputs=("media_3p", "i18n"),
    unique_checks=(("one_cover_per_poi", ("poi_id",), "is_cover"),),
    block_checks=(("media_required_null",
                   "poi_id IS NULL OR source_name IS NULL OR is_cover IS NULL OR is_active IS NULL"),),
    soft_delete_set={"is_active": "false"},
    write_mode="MERGE",
)
```

The 3P columns are not cast. `ensure_target` raises if the source types drift from the DDL (`int`, `string`).

### Gold build cells

- Gallery: `OUT_COLS` is the same 12 columns. `build(ctx)` is `_require` on `ctx.input("media")`, then `.select(*OUT_COLS)`. `SPEC(trg_tbl="gld_srv_poi_media_gallery", inputs={"media": "slv_poi_media_info"}, pk=("media_id",), required_inputs=("media",), soft_delete_set={"is_active": "false"}, write_mode="MERGE")`.
- Amenity: `OUT_COLS = ("poi_id", "business_sector", "amenity_group", "amenity_raw", "amenity", "amenity_vi", "service_flags")`. `build` is `ctx.input("amenity").select(*OUT_COLS)`. `SPEC(trg_tbl="gld_srv_poi_amenity", inputs={"amenity": "slv_poi_amenity"}, pk=(the four keys), required_inputs=("amenity",), write_mode="MERGE")`, with no `soft_delete_set`.
- Both use the default `live_only=True`. They add no columns, joins or filters.

## Verification

Local: `python -m pytest -q tests/test_poi_media_amenity_contract.py`. No Spark; static checks with `ast`, `json` and `re`, in the style of `test_gld_srv_poi_contract.py`.

- `test_node_specs`: for all three specs, check `trg_tbl`, `inputs`, `pk`, `required_inputs`, `unique_checks`, `block_checks`, `soft_delete_set` and `write_mode` as listed above.
- `test_build_columns_match_ddl`: each `OUT_COLS` plus `TECH` equals the column names in the `TABLE_COLS` of the new patch cells and in the `init_tables` dicts. The types map `INT`→display/width/height and `BOOLEAN`→`is_cover`/`is_active`.
- `test_ddl_parity_create_vs_init`: `_create_sql` from `mediaddlpy` and `amenddlpy` equals `create_sql(spec)` from `init_tables` (pattern `test_gld_srv_patch_create_matches_init`).
- `test_edges_create_vs_init`: `EDGES_ON` with each cell's `PL` equals the matching rows of `PIPELINE_CONFIG_ROWS`. Each target has exactly one `pl_name` and no duplicate 5-tuple.
- `test_amenity_untouched`: the `slv_poi_amenity` `init_tables` dict and its three ENR tuples are exactly as described in mapping amenity §0. No new cell mentions `slv_poi_amenity` as `trg_tbl`.
- `test_gold_copy_one_to_one`: the gallery `OUT_COLS` equals the silver `OUT_COLS`. The gold amenity `OUT_COLS` equals `NB_SLV_POI_AMENITY` `OUT_COLS`. The gold build source has no `join`, `where`, `withColumn` or technical column.
- `test_media_build_static`: the build has `posexplode`, `asc_nulls_last`, `startswith("[")`, `isin("", "null")`, `concat_ws("|"`, `sha2(` with `256`, and literals `google`/`partner`. It has no `monotonically_increasing_id`, no `.first(`, and no `F.trim` applied to `blob_url`.
- `test_setup_patch_guards`: in both new cells, the order is `held = True` < `Dừng trước khi ghi` < `CREATE TABLE IF NOT EXISTS` < `INSERT INTO {CFG}` < `Sau khi ghi` < `finally:`. `LEASE_MINUTES = 90`. Forbidden tokens are absent.
- `test_mapping_targets_match_out_cols`: the target fields of mapping media §1.2, minus `created_at`/`updated_at`, equal the silver `OUT_COLS`.
- Regression: `python -m pytest -q tests/test_initial_ddl_contract.py tests/test_poi_amenity_contract.py tests/test_gld_srv_poi_contract.py`, then the full `python -m pytest -q`.

Runtime fixture (Fabric DEV; in-memory DataFrames passed to `partner_media` and `with_cover` after `%run NB_SLV_POI_MEDIA_INFO` cell `slvmediabuild` is pasted; saved as `evidence/probes/media_build_fixture.py` with output in `evidence/results/media_build_fixture.txt`):

- F1: i18n array with orders (2, 1) → 2 rows; the cover is order 1.
- F2: i18n `[]` with a services array → rows use the i18n `poi_id`; `partner_fallback_docs = 1`.
- F3: i18n JSON `null` with services null → 0 rows.
- F4: i18n SQL null, and i18n `'  '` → fallback.
- F5: url null and url `'  '` → dropped; `partner_url_dropped = 2`.
- F6: one element with null order → cover.
- F7: two elements, both orders null → no cover.
- F8: orders tie (1, 1) → the cover is at `_pos` 0.
- F9: a deleted i18n row is excluded; a deleted services row gives no fallback; `deleted` null is kept.
- F10: object root `{"url":"x"}` → `partner_media_unparsed = 1`, 0 rows, no fallback.
- F11: `with_cover` on `repartition(7)` and on `coalesce(1)` of the 3P tie fixture gives identical rows.

Runtime pipeline (Fabric DEV, recorded in `runtime-runbook.md`):

- R1: the second run of each patch cell inserts 0 edges and changes no schema.
- R2: `SELECT trg_tbl, collect_set(pl_name), count(*) FROM ctrl_mng_pipeline_config WHERE is_active = 1 AND trg_tbl IN (3 targets) GROUP BY trg_tbl` → one `pl_name` per target, and the edge counts are 3, 1 and 1.
- R3: the second `_30P` RUN and the second `_1H` RUN show `numTargetRowsInserted = 0` and `numTargetRowsUpdated = 0` in `DESCRIBE HISTORY` for all three targets.
- R4: `SELECT poi_id FROM slv_poi_media_info WHERE deleted_at IS NULL GROUP BY poi_id HAVING sum(CAST(is_cover AS INT)) > 1 OR (sum(CAST(is_cover AS INT)) = 0 AND (count(*) = 1 OR count(display_order) > 0))` → 0 rows.
- R5: business-column `EXCEPT` in both directions → 0 rows, for gallery vs live silver and for gold amenity vs live `slv_poi_amenity`.
- R6: the `slv_poi_amenity` history has no version written by the `_1H` exec.
- R7: in the `_30P` exec, `gld_srv_poi_info` and `gld_srv_poi_multi_lang` are SUCCESS.
- R8: the silver `qg_json` warnings are recorded. Expected: `partner_url_dropped ≥ 1` (P5), `poi_without_cover = 0`.
