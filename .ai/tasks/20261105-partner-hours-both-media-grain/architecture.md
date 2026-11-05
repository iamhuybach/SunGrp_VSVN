RESULT: PASS

## Main brief

### Decision
- Partner hours: a day with 2 elements emits 2 open objects in source order. Length above 2 still stops with `PARTNER_MULTI_HOURS`. Any bad element stops with `PARTNER_BAD_HOURS` for the whole record.
- Silver media: copy the parent row's extract `updated_at` onto each element as `_src_ts`. Then `collapse()` keeps one row per (`media_id`, `poi_id`) using a fixed total order, before `with_cover`. Silver and gallery `pk=("media_id","poi_id")`.
- No DDL, ctrl, edge, or PostgreSQL change. `media_id → poi_id` already holds for both sources, so existing target rows match 1:1 under the new key.
- Add metric `partner_media_collapsed`, computed inside the existing second `.first()`. No new action.

### Invariants Main must preserve
- `partner_hours`: lengths 0/1/2 give 1 closed / 1 open / 2 open objects. Above 2 gives `(None,"PARTNER_MULTI_HOURS")`. Days run Monday→Sunday, and the two objects of one day are adjacent and in source order.
- A two-interval object has exactly the keys of the single-interval object. Any bad element gives `(None,"PARTNER_BAD_HOURS")`.
- `_src_ts` comes from the extract `updated_at` of the exploded parent: i18n row, services row on fallback, or `slv_3p_poi_media` row. The cell contains no `src_updated_at`, `last_updated_at`, `dropDuplicates`, or `F.first(`.
- Collapse order inside `partitionBy("media_id","poi_id")`: `_src_ts` desc nulls last, then `display_order`, `_pos`, `blob_url`, `photo_api_uri`, `width_px`, `height_px`, `photographer`, `source_name`, all asc nulls last. Keep `row_number()==1`.
- `collapse` runs before `with_cover`. `_rn` and `_src_ts` are dropped and never reach `OUT_COLS`.
- `slvmediabuild` keeps exactly one `.persist()`, one `.unpersist()`, two `.first()`, and no `.count()`. The first source line containing `blob_url` has no `trim`.
- Gallery `build` stays `media.select(*OUT_COLS)`. Only the pk changes.
- No `OUT_COLS` change, and no new rows in the §1.2 table of `mapping_poi_media_info.md`.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfohours` / `partner_hours` | Replace the `len(hours) > 1` stop and the single-item block with the loop in doc "Hours code" | `test_partner_two_hours` and `test_partner_stop_codes` pass |
| 2 | notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | `slvmediabuild` / `google_media` | Add `F.col("updated_at").cast("timestamp").alias("_src_ts")` | static tokens pass |
| 3 | notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | `slvmediabuild` / `partner_media` selects | Add `_ui` and `_us` aliases. `docs` selects `_src_ts` with `when(empty_i, _us).otherwise(_ui)`. `elems` and the final select carry `_src_ts` | static tokens pass |
| 4 | notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | `slvmediabuild` / `partner_media` metrics `try:` | Replace the `n_drop` aggregate with the `elem` aggregate plus metric `partner_media_collapsed` (doc "Media build code" step 3) | `.first()` count == 2 |
| 5 | notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | `slvmediabuild` / new `def collapse` | Add the function from doc "Media build code" step 4 | `test_media_collapse_before_cover` passes |
| 6 | notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | `slvmediabuild` / `build` | Add `updated_at` to all three `_require` calls. `rows = collapse(union)` then `rows = with_cover(rows)` | collapse precedes with_cover |
| 7 | notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | `slvmediabuild` / `SPEC` | `pk=("media_id", "poi_id")` | `test_node_specs` passes |
| 8 | notebooks/NB_SLV_POI_MEDIA_INFO.ipynb | `slvmediamd` | Key sentence becomes (`media_id`, `poi_id`) plus the source collapse sentence | `test_media_key_mapping_text` passes |
| 9 | notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb | `srvgallerybuild` / `SPEC` | `pk=("media_id", "poi_id")` | `test_node_specs` passes |
| 10 | docs/context/mapping_gld_srv_poi_info.md | §1.5 | Probe sentence, "JSON đích" line, new "Đúng hai phần tử" bullet, and the "Hơn hai phần tử" bullet replacing "Nhiều hơn một phần tử" (doc "Mapping text") | `test_partner_hours_mapping_text` passes |
| 11 | docs/context/mapping_poi_media_info.md | §1.1 key bullet plus new collapse bullet | Text from doc "Mapping text" | `test_media_key_mapping_text` passes |
| 12 | docs/context/mapping_poi_media_info.md | §2 | Key sentence becomes `Khóa MERGE (\`media_id\`, \`poi_id\`), như silver.` | `test_media_key_mapping_text` passes |
| 13 | tests/test_gld_srv_poi_contract.py | `test_partner_stop_codes`, new `test_partner_two_hours`, new `test_partner_hours_mapping_text` | Code in doc "Hours tests" | the tests pass |
| 14 | tests/test_poi_media_amenity_contract.py | `test_node_specs`, `test_media_build_static`, new `test_media_collapse_before_cover`, new `test_media_key_mapping_text` | Code in doc "Media tests" | the tests pass |

### Order and stop points
1. Rows 1, 10, 13 (hours). Run the hours tests. Stop for evidence: paste the pytest output.
2. Rows 2–8 and 11 (silver), then row 9 and row 12 (gallery). Then row 14.
3. Run the commands in Tests. Stop for evidence: paste the outputs.
4. `python scripts/vv.py run-gate 20261105-partner-hours-both-media-grain`.
5. Optional operator DRY_RUN of `NB_SLV_POI_MEDIA_INFO` in Fabric, not a gate. Expect no `pk_duplicate` and `partner_media_collapsed == 4`. Stop for a user decision on whether to run it before merge.
6. Record the backlog: PostgreSQL `apps.srv_poi_media_gallery` keeps `PRIMARY KEY (media_id)`. That is out of scope and safe while `media_id → poi_id` holds. Stop for a user decision: accept the backlog item.

### Tests and verification
- `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_poi_media_amenity_contract.py -q`
  - New: `test_partner_two_hours`, `test_partner_hours_mapping_text`, `test_media_collapse_before_cover`, `test_media_key_mapping_text`.
  - Changed: `test_partner_stop_codes` (now a length-3 case), `test_node_specs` (media), `test_media_build_static`.
  - Unchanged and must still pass: `test_partner_single_hours`, `test_partner_closed_forms`, `test_gold_copy_one_to_one`, `test_mapping_targets_match_out_cols`, `test_build_columns_match_ddl`.
- `python -m pytest -q`
- `python -c "import json,sys;[json.load(open(p,encoding='utf-8')) for p in sys.argv[1:]]" notebooks/NB_GLD_SRV_POI_INFO.ipynb notebooks/NB_SLV_POI_MEDIA_INFO.ipynb notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb`
- `python scripts/vv.py run-gate 20261105-partner-hours-both-media-grain`

### Read only if needed
- "Evidence used" and "Resolution of model-design Conflicts": rows 2–9 (why `ctx.input` keeps `updated_at`, why Google collapse does nothing, why no DDL change).
- "Ordering" and "Idempotency": rows 5 and 14.
- "Observability": row 4.
- "Implementation plan → Hours code": row 1.
- "Implementation plan → Media build code": rows 2–8.
- "Implementation plan → Mapping text": rows 8, 10–12.
- "Verification → Hours tests / Media tests": rows 13 and 14.
- "Rollout", "Rollback and forward recovery", "Partial failure": stop points 5 and 6.
- "Alternatives considered", "Residual risk and backlog": reviewer questions and the stop 6 decision.

# Architecture: 20261105-partner-hours-both-media-grain

Grain and keys come from `model-design.md` (`## Entities and grain`, `## Keys`, `## Columns`). This document covers execution, state, and recovery. It also closes model-design `## Conflicts and questions` items 1 to 7 with evidence read in this run.

## Evidence used (read in this run)

- `NB_LIB_TRANSFORM_SLV_GLD` `NodeContext.input`: `live_only=True` filters `deleted_at IS NULL` and drops the four lib technical columns only when the input has both `row_hash` and `deleted_at`. The partner CDC tables carry `deleted`, `_source_db`, `created_at`, `updated_at` (`NB_LIB_EXTRACT_RAWDATA` `TECH_COLUMNS`). `slv_3p_poi_media` carries `SNAPSHOT_TECH_COLUMNS`. Neither has `row_hash` plus `deleted_at`, so `ctx.input(...)` keeps `updated_at` on all three media inputs. No `live_only=False` is needed.
- `slv_3p_poi_media` is written by `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` with MERGE key `media_dedup_key` (`NB_SETUP_INITIAL_DDL` `init_cfg_3p`). `build_merge_sql` sets `updated_at = merge_clock` on update and `created_at`, `updated_at` on insert. So Google `updated_at` exists, and `media_dedup_key` is unique in that table.
- `media_dedup_key = HASH_SHA256_PIPE(source_name, source_id, name)` and Google `poi_id = md5(source_name, source_id)`. So `poi_id` is a function of `media_dedup_key`. Partner `media_id = sha2('partner'|poi_id|trim(url))`, so `poi_id` is a function of partner `media_id` too. Conclusion: in both sources `media_id → poi_id` holds by construction. Rows unique on `media_id` are exactly the rows unique on (`media_id`, `poi_id`).
- Lib `quality_gate` blocks `pk_null` (any pk column null) and `pk_duplicate` through `groupBy(*pk)`. The MERGE `ON` clause is `" AND ".join(t.c = s.c for c in pk)`. A composite pk is already in production use (`gld_srv_poi_amenity`, 4 columns).
- DDL: `NB_CREATE_DDL` `mediaddlpy` and `NB_SETUP_INITIAL_DDL` `init_tables` declare `media_id STRING NOT NULL` and `poi_id STRING`. Neither declares a Delta PK constraint. `ctrl_cfg_schema_registry` serves bronze→silver extract only. A transform pk lives only in `NodeSpec.pk`.
- PostgreSQL `apps.srv_poi_media_gallery` has `PRIMARY KEY (media_id)` (`sql/postgres/gld_srv_serve.pg.sql:104`). That file is out of scope. The functional dependency above keeps it satisfied.
- No local test imports pyspark. Media checks are static, as in the existing tests. `partner_hours` is pure Python and runs locally.

## Resolution of model-design Conflicts

1. No proposal: the request and the ledger (`D-HOURS-2`, `D-MEDIA-KEY`, `D-MEDIA-TIE`, `D-GALLERY-KEY`, `D-HOURS-ORDER`, `D-MEDIA-PARENT`) are enough. This does not block.
2. Mapping text: the edit list covers it (§1.5, §1.1, §2, cell `slvmediamd`).
3. Google `updated_at`: the column exists (SNAPSHOT_TECH_COLUMNS). Google rows go through the same collapse. It does nothing for them because `media_dedup_key` is the source MERGE key. `_require` adds `updated_at`, so a missing column fails closed with `ConfigError`.
4. Partner parent `updated_at`: `D-MEDIA-PARENT` settles it. Use i18n `updated_at` when the i18n `media` is used, and services `updated_at` when the fallback is taken. Nulls rank last.
5. DDL: no change. `poi_id` stays nullable in the DDL. The lib's `pk_null` and `media_required_null` already block null `poi_id` before MERGE. A NOT NULL change would need `ALTER TABLE`, which `test_setup_patch_guards` forbids, and the DDL notebooks are out of scope.
6. Duplicate observability: add a metric `partner_media_collapsed`, computed inside the existing second `.first()` action (see Observability). It is not a warning: the duplicates are now legitimate input.
7. Length above 2: keep stop `PARTNER_MULTI_HOURS` (`D-HOURS-ORDER`).

## Scope

- `NB_GLD_SRV_POI_INFO` cell `srvinfohours`, function `partner_hours`: a day with exactly two `hours` elements emits two open-day objects.
- `NB_SLV_POI_MEDIA_INFO` cells `slvmediabuild` and `slvmediamd`: carry the parent `updated_at` as `_src_ts`, collapse to one row per (`media_id`, `poi_id`) before `with_cover`, set `pk=("media_id", "poi_id")`, and add the metric.
- `NB_GLD_SRV_POI_MEDIA_GALLERY` cell `srvgallerybuild`: `pk=("media_id", "poi_id")`.
- Mapping docs `mapping_gld_srv_poi_info.md` §1.5 and `mapping_poi_media_info.md` §1.1 and §2.
- The two contract test files.

## Non-goals

- DDL, ctrl seed, pipeline edges, and the PostgreSQL DDL. `apps.srv_poi_media_gallery` keeps PK `media_id`.
- The `media_id` formulas, Google `media_dedup_key`, and output columns. No `OUT_COLS` change.
- A `hours` length above 2. Google hours are unchanged.
- Backfill or migration. None is needed (see Rollout).
- `NB_SLV_POI_ENTITY_NON_ENRICH`, the review and enrich notebooks, the orchestrator, and the parent task's notebooks.

## Invariants

- I1 `partner_hours`: for each day, `len(hours)` in {0 or missing} gives 1 closed object, 1 gives 1 open object, 2 gives 2 open objects in source order, and more than 2 stops with `(None, "PARTNER_MULTI_HOURS")`.
- I2: every open object has exactly the keys of today's single-interval object: `day_of_week`, `label`, `value`, `open_time`, `close_time`, `is_open_all_day=false`, `is_closed=false`.
- I3: an element that is not a dict, or whose `open_time` or `close_time` is not a string, makes the whole record `(None, "PARTNER_BAD_HOURS")`. No partial array is returned.
- I4: days are ordered Monday → Sunday. The two objects of one day are adjacent and not sorted by time.
- M1: the output of the media `build` holds at most one row per (`media_id`, `poi_id`). The lib `pk_duplicate` gate is only a backstop.
- M2: the kept row has the greatest `_src_ts` in its group. A null `_src_ts` ranks below any non-null value.
- M3: `_src_ts` is the extract technical `updated_at` of the exploded parent row. Neither `src_updated_at` nor `last_updated_at` appears in the cell.
- M4: the same pinned input versions give the same output rows and the same `row_hash` on every rerun.
- M5: `is_cover` is computed after the collapse, so `one_cover_per_poi` holds on the rows that are written.
- M6: `_src_ts` and `_rn` never reach `OUT_COLS`. The build never returns a lib technical column.
- G1: the gallery `build` stays `media.select(*OUT_COLS)`, and its pk equals the silver pk.
- F1 (relied on, not enforced): `media_id → poi_id` for both sources. PostgreSQL `PRIMARY KEY (media_id)` depends on it.

## State ownership

- `slv_poi_media_info` is owned by `NB_SLV_POI_MEDIA_INFO` in `PL_VV_TRANS_SLV_TO_GLD_30M`. `gld_srv_poi_media_gallery` is owned by `NB_GLD_SRV_POI_MEDIA_GALLERY` in the same pipeline, as a child of silver. `gld_srv_poi_info` is owned by `NB_GLD_SRV_POI_INFO`. Ownership is unchanged.
- The extract notebooks own the source `updated_at`. This task only reads it.
- The lib owns the edge watermarks and the flow lock. No change.

## Grain and keys

See model-design `## Entities and grain` and `## Keys`. Architecture additions:
- The pre-gate collapse key equals the MERGE key: (`media_id`, `poi_id`), in that order in `NodeSpec.pk`, for silver and gallery.
- Because of F1, switching the key does not change which target row any source row matches. Existing target rows stay unique under the new key. `ON t.media_id = s.media_id AND t.poi_id = s.poi_id` matches the same pairs as `ON t.media_id = s.media_id` did.

## Ordering

- Hours: day loop over `PARTNER_DAYS`, then source array order within a day (`D-HOURS-ORDER`).
- Collapse, a total order inside `Window.partitionBy("media_id", "poi_id")`:
  `_src_ts desc nulls last`, `display_order asc nulls last`, `_pos asc nulls last`, `blob_url asc nulls last`, `photo_api_uri asc nulls last`, `width_px asc nulls last`, `height_px asc nulls last`, `photographer asc nulls last`, `source_name asc nulls last`, then keep `row_number() == 1`.
  - After these keys, tied rows agree on every column in `OUT_COLS`. The remaining columns are pk, constants, or `is_cover`, which is computed afterwards.
  - So Spark's arbitrary pick among physically tied rows cannot change the content or the `row_hash`. That meets `D-MEDIA-TIE` ("any tied row") and the rerun-stability constraint.
  - `source_name` is in the list only so the order is total even if a cross-source hash collided.
- Cover: `with_cover` is unchanged (`display_order`, `_pos`, `media_id`). It runs over the collapsed rows.

## Transaction and commit boundaries

- Each node writes one Delta MERGE commit, which is atomic. The build, `quality_gate`, and `diff_counts` all run before the commit. A QG block means no commit.
- Silver and gallery are separate commits. The gallery reads silver at the version silver just committed (a parent node in the same execution).
- `gld_srv_poi_info` is one commit. The hours UDF runs before the gate. Any hours error raises `QualityGateError` for the whole node, as today.

## Idempotency

- The collapse is a deterministic function of the pinned input versions (M4). The order is total on content, and `posexplode` `_pos` is deterministic per parent row.
- MERGE updates only when `row_hash` differs. A rerun with the same input gives `diff = 0`, and the lib skips the MERGE.
- Forbidden constructs, guarded by tests: `F.first(`, `dropDuplicates`, `monotonically_increasing_id`, and an order without the full tie-break list.
- Hours: a pure function of `opening_hours_text`.

## Concurrency

Not applicable: no new writers. The single-owner node, the flow lock (`refresh_flow_lock` before `ensure_target` and before `merge_target`), and the edge model are unchanged.

## Retry and recovery

- Transient Spark or Delta errors: the lib's existing `with_retry`, and the pipeline re-runs the node from the same pinned versions. The same result follows (Idempotency).
- `ConfigError` (missing `updated_at`) and `QualityGateError` are not retried. Fix the input or the config, then rerun the node with `p_force` if the edges are clean.

## Partial failure

- Silver commits and the gallery fails: the silver→gallery edge watermark does not advance, so the next pipeline run marks the edge dirty and rebuilds the gallery from the current silver. Silver is already correct and its rerun is a no-op.
- Silver fails: no commit. The gallery sees an unchanged parent and returns `NO_DATA`, or is `SKIPPED` in the same execution.
- `gld_srv_poi_info` is independent of the media nodes. A failure there leaves the media tables untouched.
- PostgreSQL sync after the Fabric commit is out of scope. F1 keeps `PRIMARY KEY (media_id)` valid.

## Observability

- New `ctx.metrics["partner_media_collapsed"]`: partner elements with a non-blank URL minus the distinct (`poi_id`, `trim(url)`). This equals the partner rows the collapse removes, because that pair is exactly the `media_id` hash input.
  - It is computed in the existing second action (the `n_drop` aggregate over `cached`). The `.first()` count stays 2, and there is no `.count()`.
  - The expected value on current data is 4: 2 `media_id` × 3 rows, minus 1 kept each.
- Existing warnings `partner_media_unparsed`, `partner_url_dropped`, `poi_without_cover` and metric `partner_fallback_docs` are unchanged.
- Google collapse is not counted: it is impossible by the source key, and the `pk_duplicate` backstop would show it.
- Hours: the existing `operating_hours` error histogram in the `QualityGateError` message. `PARTNER_MULTI_HOURS` now means length above 2 only.

## Security

Not applicable: no new data source, credential, PII column, or external call.

## Rollout

1. Merge the notebook, doc, and test changes. Fabric picks up the notebooks through the existing git sync. No DDL, ctrl seed, or edge change.
2. First `PL_VV_TRANS_SLV_TO_GLD_30M` run:
   - Silver builds the collapsed set and passes `pk_duplicate`, which blocked it before.
   - MERGE under the composite key: existing rows match 1:1 (F1) and their `row_hash` is unchanged, because the columns and their order are unchanged. Only real changes and the previously blocked rows are written.
   - The gallery follows.
3. `gld_srv_poi_info`: the next run that has dirty edges (or a run with `p_force=true`) writes partner `operating_hours` for the 8 two-interval rows. That node was blocked before.
4. Optional operator check, not a task gate: run the silver node with `p_mode=DRY_RUN` and confirm `qg` has no `pk_duplicate` and `metrics.partner_media_collapsed == 4`.

## Rollback and forward recovery

- Rollback means reverting the commit.
  - Media nodes return to `pk=("media_id",)` without the collapse, and `pk_duplicate` blocks again. That is fail-closed and nothing is written.
  - Rows already written under the composite key are unique on `media_id` (F1), so the old key reads them correctly.
  - Hours returns to `PARTNER_MULTI_HOURS`, which blocks the node. Already-written `operating_hours` stay until the next successful run.
- Forward recovery is preferred. Any defect in the collapse order is fixed in code and rerun. The MERGE converges because content determines the result.
- No Delta `RESTORE` is needed. The lib treats `RESTORE` as a data change.

## Alternatives considered

- Hours shape:
  - (a) Two objects per day (selected): keeps the single-object shape and matches how Google rule 9 already handles multi-period days, so consumers already accept more than 7 objects.
  - (b) Join both intervals into one `value`: rejected, it breaks the shape constraint.
  - (c) Keep the stop: rejected by `D-HOURS-2`.
- Tie rule:
  - (a) A total order on existing columns (selected): deterministic, no new column.
  - (b) `dropDuplicates` or `F.first`: the pick is nondeterministic and violates rerun stability.
  - (c) Block on ties, like `D-SRV-21`: contradicts `D-MEDIA-TIE`.
  - (d) Order by `sha2(to_json(row))`: equivalent but opaque. Rejected for readability.
- Collapse position:
  - Before `with_cover` (selected).
  - After it is rejected: the dropped row could hold `is_cover`, which leaves a POI with no cover.
- Gallery: change the pk only (selected). Re-collapsing in gold would break the 1-1 copy contract (`test_gold_copy_one_to_one` forbids `where` and `withColumn`), and silver already guarantees uniqueness.
- Fabric guard for F1 (block when a `media_id` appears under two `poi_id`): rejected. It would bring back the old grain against `D-MEDIA-KEY`, and it needs an extra action. Record as backlog for the PostgreSQL DDL owner.

## Implementation plan

### Hours code (`srvinfohours`, `partner_hours`)

Replace the block from `if len(hours) > 1:` through `days.append(_open(day, item["open_time"], item["close_time"]))` with:

```python
        if len(hours) > 2:
            return None, "PARTNER_MULTI_HOURS"                       # §1.5 stop, D-HOURS-ORDER
        for item in hours:                                           # D-HOURS-2: source order
            if not isinstance(item, dict) or not isinstance(item.get("open_time"), str) \
                    or not isinstance(item.get("close_time"), str):
                return None, "PARTNER_BAD_HOURS"
            days.append(_open(day, item["open_time"], item["close_time"]))
```

Returning early discards `days`, so I3 holds.

### Media build code (`slvmediabuild`)

1. `google_media`: append `F.col("updated_at").cast("timestamp").alias("_src_ts")` after the `_pos` literal.
2. `partner_media`:
   - `vi` select: add `F.col("updated_at").cast("timestamp").alias("_ui")`.
   - `svc` select: add `F.col("updated_at").cast("timestamp").alias("_us")`.
   - `docs` select: add `F.when(empty_i, F.col("_us")).otherwise(F.col("_ui")).alias("_src_ts")`.
   - `elems = docs.select("poi_id", "_src_ts", F.posexplode("_arr").alias("_pos", "_e"))`.
   - Final `kept.select(...)`: end with `url.alias("blob_url"), "_pos", "_src_ts")`.
3. Metrics block inside `try:`. Replace the `n_drop` statement and its `ctx.warn` with:

```python
            key = F.when(url.isNotNull() & (F.trim(url) != ""), F.concat_ws("|", F.col("poi_id"), F.trim(url)))
            elem = cached.select("poi_id", F.posexplode("_arr").alias("_pos", "_e")).agg(
                F.sum(F.when(url.isNotNull() & (F.trim(url) != ""), 0).otherwise(1)).alias("n"),
                (F.count(key) - F.countDistinct(key)).alias("dup")).first()
            ctx.warn("partner_url_dropped", elem["n"])
            ctx.metrics["partner_media_collapsed"] = int(elem["dup"] or 0)   # D-MEDIA-KEY
```

4. New function between `partner_media` and `with_cover`:

```python
def collapse(df):
    # D-MEDIA-KEY, D-MEDIA-TIE: một dòng mỗi (media_id, poi_id), updated_at nguồn lớn nhất, null cuối.
    # Hòa: thứ tự cố định trên cột đã có, dòng còn hòa giống nhau ở mọi cột đích -> chạy lại cùng kết quả.
    order = Window.partitionBy("media_id", "poi_id").orderBy(
        F.col("_src_ts").desc_nulls_last(), F.col("display_order").asc_nulls_last(), F.col("_pos").asc_nulls_last(),
        F.col("blob_url").asc_nulls_last(), F.col("photo_api_uri").asc_nulls_last(),
        F.col("width_px").asc_nulls_last(), F.col("height_px").asc_nulls_last(),
        F.col("photographer").asc_nulls_last(), F.col("source_name").asc_nulls_last())
    return df.withColumn("_rn", F.row_number().over(order)).where(F.col("_rn") == 1).drop("_rn", "_src_ts")
```

5. `build`:
   - `_require(media, MEDIA_3P_COLS + ("updated_at",), "slv_3p_poi_media")`.
   - i18n required tuple: add `"updated_at"`. Services required tuple: add `"updated_at"`.
   - Replace the `rows = with_cover(...)` line with two statements:
     `rows = collapse(google_media(media).unionByName(partner_media(i18n, services, ctx)))`, then `rows = with_cover(rows)`.
6. `SPEC.pk=("media_id", "poi_id")`.
7. Cell `slvmediamd`: replace `Khóa \`media_id\`.` with: `Khóa (\`media_id\`, \`poi_id\`). Gộp nguồn trước: một dòng mỗi khóa, \`updated_at\` nguồn lớn nhất.`

Keep the first source line that contains `blob_url` as the `MEDIA_3P_COLS` line, which has no `trim` (`test_media_build_static`).

### Gallery code

In cell `srvgallerybuild`, change `pk=("media_id",)` to `pk=("media_id", "poi_id")`. Nothing else changes.

### Mapping text

`mapping_gld_srv_poi_info.md` §1.5:
- Probe paragraph: append `Probe \`partner_multi_hours\` (2026-11-04, task 20261104-poi-review-src-and-partner-i18n): 8 dòng có \`hours\` dài 2, không dòng nào dài hơn 2.`
- Replace `JSON đích cùng dạng mục 1.4: bảy phần tử, thứ tự Thứ Hai → Chủ Nhật.` with `JSON đích cùng dạng mục 1.4, thứ tự Thứ Hai → Chủ Nhật. Mỗi ngày một phần tử. Ngày có hai phần tử \`hours\` ra hai phần tử liền nhau.`
- After the `Đúng một phần tử \`hours\`` bullet, insert: `- Đúng hai phần tử \`hours\`: ra hai object cùng \`day_of_week\`, mỗi object theo rule một phần tử ở trên, giữ thứ tự mảng nguồn (\`hours[0]\` rồi \`hours[1]\`), không sắp theo giờ, không ghép chuỗi. Ví dụ \`monday\` \`08:00\`–\`09:00\` và \`11:00\`–\`22:00\` ra hai object Thứ Hai \`08:00 - 09:00\` rồi \`11:00 - 22:00\`. Một phần tử sai kiểu thì dừng \`PARTNER_BAD_HOURS\`.`
- Replace the `Nhiều hơn một phần tử \`hours\`` bullet with `- Hơn hai phần tử \`hours\` trong một ngày: dừng \`PARTNER_MULTI_HOURS\`, không chọn phần tử, không ghép chuỗi.`

`mapping_poi_media_info.md`:
- §1.1, the bullet starting `\`poi_id\` đã có công thức`: change `là \`media_id\`.` to `là (\`media_id\`, \`poi_id\`).` and change `\`quality_gate\` chặn \`media_id\` null.` to `\`quality_gate\` chặn \`media_id\` hoặc \`poi_id\` null (\`pk_null\`).`
- §1.1: insert a new bullet after that one: `- Gộp nguồn trước \`quality_gate\`: một dòng mỗi (\`media_id\`, \`poi_id\`), giữ dòng có \`updated_at\` nguồn lớn nhất. \`updated_at\` nguồn là cột kỹ thuật extract của dòng cha đã nổ mảng: i18n khi dùng \`media\` của i18n, services khi lấy fallback, \`slv_3p_poi_media\` với Google. Không dùng \`src_updated_at\`, \`last_updated_at\`. Null xếp sau mọi mốc. Hòa \`updated_at\` thì xếp tiếp theo \`display_order\`, \`_pos\`, \`blob_url\`, \`photo_api_uri\`, \`width_px\`, \`height_px\`, \`photographer\`, \`source_name\` tăng, null cuối. Dòng còn hòa giống nhau ở mọi cột đích nên chạy lại cho cùng kết quả. \`is_cover\` tính sau bước gộp. Notebook ghi metric \`partner_media_collapsed\`.`
- §2: replace `Khóa MERGE \`media_id\`.` with `Khóa MERGE (\`media_id\`, \`poi_id\`), như silver.`
- Do not add rows to the §1.2 table (`test_mapping_targets_match_out_cols`).

## Verification

### Hours tests (`tests/test_gld_srv_poi_contract.py`)

In `test_partner_stop_codes`, replace the `two` case with:

```python
    three = _week(monday={"hours": [{"open_time": "08:00", "close_time": "09:00"}] * 3})
    assert fn(three)[1] == "PARTNER_MULTI_HOURS"
```

New tests:

```python
def test_partner_two_hours():
    fn = _hours()["partner_hours"]
    single = json.loads(fn(_week())[0])[0]
    two = _week(monday={"status": True, "hours": [{"open_time": "08:00", "close_time": "09:00"},
                                                  {"open_time": "11:00", "close_time": "22:00"}]})
    out, err = fn(two)
    assert err is None
    got = json.loads(out)
    assert [row["day_of_week"] for row in got] == [1, 1, 2, 3, 4, 5, 6, 7]
    assert [row["value"] for row in got[:2]] == ["08:00 - 09:00", "11:00 - 22:00"]
    assert all(list(row) == list(single) and row["label"] == "Thứ Hai" and not row["is_closed"]
               and not row["is_open_all_day"] for row in got[:2])
    swapped = _week(monday={"hours": [{"open_time": "11:00", "close_time": "22:00"},
                                      {"open_time": "08:00", "close_time": "09:00"}]})
    assert [row["open_time"] for row in json.loads(fn(swapped)[0])[:2]] == ["11:00", "08:00"]
    bad = _week(monday={"hours": [{"open_time": "08:00", "close_time": "09:00"},
                                  {"open_time": 11, "close_time": "22:00"}]})
    assert fn(bad) == (None, "PARTNER_BAD_HOURS")


def test_partner_hours_mapping_text():
    section = MAPPING.read_text(encoding="utf-8").split("### 1.5.", 1)[1].split("\n---\n", 1)[0]
    assert "Nhiều hơn một phần tử `hours`" not in section
    assert "Đúng hai phần tử `hours`" in section and "Hơn hai phần tử `hours`" in section
    assert "PARTNER_MULTI_HOURS" in section
```

### Media tests (`tests/test_poi_media_amenity_contract.py`)

- `test_node_specs`: `silver["pk"] == ("media_id", "poi_id")` and `gallery["pk"] == ("media_id", "poi_id")`.
- `test_media_build_static`:
  - Add these tokens to the required loop: `'Window.partitionBy("media_id", "poi_id")'`, `'F.col("_src_ts").desc_nulls_last()'`, `'F.col("updated_at").cast("timestamp").alias("_ui")'`, `'F.col("updated_at").cast("timestamp").alias("_us")'`, `'F.when(empty_i, F.col("_us")).otherwise(F.col("_ui"))'`, `'ctx.metrics["partner_media_collapsed"]'`.
  - Add `for token in ("src_updated_at", "last_updated_at", "dropDuplicates"): assert token not in source`.
  - Existing asserts stay: `.first()` count == 2, no `.count()`, a single `persist`.
- New tests:

```python
def test_media_collapse_before_cover():
    source = _cell("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediabuild")
    fn = next(ast.unparse(n) for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == "collapse")
    tail = fn.split("orderBy(", 1)[1]
    order = ["_src_ts", "display_order", "_pos", "blob_url", "photo_api_uri", "width_px", "height_px",
             "photographer", "source_name"]
    positions = [tail.index(f"'{name}'") for name in order]
    assert positions == sorted(positions)
    assert "row_number()" in fn and "== 1" in fn and "'_src_ts'" in fn.split(".drop(", 1)[1]
    body = _build(source)
    assert body.index("collapse(") < body.index("with_cover(")
    assert "'updated_at'" in body


def test_media_key_mapping_text():
    text = (ROOT / "docs" / "context" / "mapping_poi_media_info.md").read_text(encoding="utf-8")
    s11 = text.split("## 1.1.", 1)[1].split("## 1.2.", 1)[0]
    s2 = text.split("# 2.", 1)[1]
    assert "là `media_id`." not in s11 and "Khóa MERGE `media_id`." not in s2
    assert "(`media_id`, `poi_id`)" in s11 and "(`media_id`, `poi_id`)" in s2
    assert "`updated_at` nguồn lớn nhất" in s11 and "src_updated_at" in s11
    assert "(`media_id`, `poi_id`)" in _cell("NB_SLV_POI_MEDIA_INFO.ipynb", "slvmediamd")
```

### Commands

- `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_poi_media_amenity_contract.py -q`
- `python -m pytest -q`: the full suite, to catch other readers of these cells.
- `python -c "import json,sys;[json.load(open(p,encoding='utf-8')) for p in sys.argv[1:]]" notebooks/NB_GLD_SRV_POI_INFO.ipynb notebooks/NB_SLV_POI_MEDIA_INFO.ipynb notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb`
- `python scripts/vv.py run-gate 20261105-partner-hours-both-media-grain`

### Residual risk and backlog

- F1 is relied on, not enforced. If a future source assigns one `media_id` to two `poi_id`, Fabric accepts it, but PostgreSQL `PRIMARY KEY (media_id)` would reject the sync. Backlog: align the PostgreSQL gallery PK with (`media_id`, `poi_id`) in a PG DDL task.
- No local Spark run. Collapse semantics are checked by static tests and the lib's `pk_duplicate` backstop. The optional DRY_RUN in Rollout step 4 confirms them on real data.
