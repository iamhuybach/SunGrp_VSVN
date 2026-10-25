RESULT: PASS

## Main brief

### Decision
Add a new `NB_CREATE_DDL` patch pair at the end, `srvratemd` and `srvratepy`. It runs `ALTER … ADD COLUMNS … AFTER`, one column at a time, then inserts 2 GLD_30P edges. It holds the GLD_30P flow lock, the same pattern as `srvpoipy`.
Do not edit `srvpoipy` (02_NAMING §2.1 rule 4).
In `srvinfobuild`: a grain stop on rating over the kept Google keys, a `COUNT(*)` review aggregate, Google-only `F.when` on the three columns, an explicit INT range stop, and two new inputs.
`NB_SETUP_INITIAL_DDL` gets the target definitions in place. Mapping §1.2 gets 3 rows and 1 rule paragraph.
The edits force changes in three test files that are not in `scope.files`. Stop 1 handles that.

### Invariants Main must preserve
- For the same pinned inputs, the output `poi_id` set equals the pre-change build. One row per `poi_id`, MERGE on `poi_id`.
- Rows whose `lower(trim(source_name)) != 'google'` get NULL in `rating_overall`, `rating_count` and `review_count`.
- A missing rating or review gives NULL. `review_count` is never 0 and never coalesced.
- `review_count` = `COUNT(*)` per `poi_id` (`F.count(F.lit(1))`), never `countDistinct`.
- `rating_overall` stays `decimal(4,2)` with no cast; any other source type raises ConfigError. `rating_count` and `review_count` are INT. A value outside the INT range raises QualityGateError before the write.
- A kept Google `poi_id` with more than one rating row raises QualityGateError. No row is chosen.
- `OUT_COLS`+TECH, `srvratepy.INFO_COLS`, the `NB_SETUP_INITIAL_DDL` spec and the mapping §1.2 targets are identical lists. The new columns sit right after `holiday_exceptions`.
- `SPEC.inputs` has 5 roles and equals the active GLD_30P edges. `required_inputs` stays `("entity",)`. New inputs use the default `live_only`, so the count of `live_only=False` stays 3.
- In `srvratepy`, every write follows `_refresh_lock()`. ALTER runs before INSERT. There is no DROP, DELETE or `UPDATE {CFG}`. A rerun does nothing.
- §1.1, `operating_hours`, `is_recommended`, every existing column, and the cell `srvpoipy` stay unchanged.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | docs/context/mapping_gld_srv_poi_info.md | §1.2 table, after `holiday_exceptions` row | Add 3 rows (full doc "Mapping §1.2") | `test_mapping_targets_match_out_cols` passes |
| 2 | docs/context/mapping_gld_srv_poi_info.md | §1.2, after the table, before `### 1.3` | Add the rule paragraph verbatim | Text present; §1.1 diff empty |
| 3 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfomd` | Add one line about the 3 columns | Markdown only |
| 4 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` constants | Add `RATING_COLS`, `INT_MIN, INT_MAX`; append 3 names to `OUT_COLS` | `test_build_columns_match_ddl` passes |
| 5 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` after `_destination` | Add `_rating`, `_reviews` (full doc "Build changes") | `test_info_rating_build_rules` passes |
| 6 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` `build` | Inputs, `_require`, type check, google keys, joins, INT stop, select `F.when(is_google, …)` ×4, 2 metrics | Same test; no `deleted` or `countDistinct` |
| 7 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` `SPEC.inputs` | Add `rating`, `review` | `test_node_specs` passes |
| 8 | notebooks/NB_CREATE_DDL.ipynb | new cell `srvratemd` after `srvpoipy` | Markdown verbatim (full doc "Patch cell") | ids[-2:] order |
| 9 | notebooks/NB_CREATE_DDL.ipynb | new cell `srvratepy`, last | Code from full doc "Patch cell". Replace each `<<< copy verbatim >>>` marker with the matching `srvpoipy` lines | `test_info_rating_patch` passes; no `<<<` |
| 10 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, `gld_srv_poi_info` spec | Insert 3 tuples after the first `('holiday_exceptions', 'STRING', None)` | `test_columns_match_sources`, `test_gld_srv_patch_create_matches_init` pass |
| 11 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` end | Append rating and review GLD30 rows | `test_pipeline_config_rows_match_sources` (61) passes |
| 12 | tests/test_gld_srv_poi_contract.py | `test_node_specs` | Expected info inputs get rating and review | passes |
| 13 | tests/test_gld_srv_poi_contract.py | `test_build_columns_match_ddl` | Info contract comes from `srvratepy.INFO_COLS` | passes |
| 14 | tests/test_gld_srv_poi_contract.py | new `test_info_rating_patch`, `test_mapping_targets_match_out_cols`, `test_info_rating_build_rules` + constants | Code in full doc "Contract tests" | pass |
| 15 | tests/test_initial_ddl_contract.py (needs stop 1) | `test_columns_match_sources`, `test_gld_srv_patch_create_matches_init` | Info contract comes from `srvratepy.INFO_COLS` | pass |
| 16 | tests/test_initial_ddl_contract.py (needs stop 1) | `test_pipeline_config_rows_match_sources` | Loop over `srvratepy` EDGES_ON; 59→61 | passes |
| 17 | tests/test_enr_poi_contract.py (needs stop 1) | `test_info_patch_cell_guards` | Shift id slices by 2; add `["srvratemd","srvratepy"]` | passes |
| 18 | tests/test_poi_entity_contract.py (needs stop 1) | `test_create_ddl_patch` | Same shift | passes |

### Order and stop points
1. STOP, user decision: add `tests/test_initial_ddl_contract.py`, `tests/test_enr_poi_contract.py` and `tests/test_poi_entity_contract.py` to `scope.files`, and record it in `decision.md`. The requested acceptance criteria break those files' hard-coded seed count (59) and cell order whatever design is chosen. If the user refuses, the task cannot pass local verification. Do not edit any file before the answer.
2. Rows 1–3 (docs and markdown).
3. Rows 4–7 (build), then rows 12–14. Run `pytest tests/test_gld_srv_poi_contract.py -q`.
4. Rows 8–11 (DDL), then rows 15–18. Run the full local suite. STOP, evidence: save the pytest output to the verification log.
5. Deploy all three notebooks to DEV together. Collect baseline R0. STOP, evidence: B2 shows 6 edges, config count 59, gold table has 29 columns.
6. Run `srvratepy` (R1), then again (R2). STOP, evidence: the outputs, DESCRIBE, config count 61, 5 active edges. If it prints `không khớp hợp đồng`, stop for a user decision.
7. R3, then the R4 helper probe. STOP, evidence: counts only.
8. Node DRY_RUN, RUN, RUN (R5), then R6 and R7 PLAN. STOP, evidence: logs, metrics, the R6 numbers. Any QualityGateError on rating grain or INT range is a user-decision stop. Do not change the code to pick rows.
9. Never rerun `srvpoipy` on DEV after step 6. It stops safely, by design.

### Tests and verification
- `python -m pytest tests/test_gld_srv_poi_contract.py -q`: includes `test_node_specs`, `test_build_columns_match_ddl`, `test_info_rating_patch`, `test_mapping_targets_match_out_cols`, `test_info_rating_build_rules`.
- `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
- `python -m pytest -q`
- DEV checks R0–R7 are in the full doc's "Verification":
  - R1/R2: `srvratepy` prints `+[3 cols]`, then `+[]`;
  - R3: 18 `EXISTS_OK`, pipeline 61;
  - R5: RUN 2 gives 0/0/0 with no new version;
  - R6: `non_google_filled=0`, `review_zero=0`, `mismatches=0`, live count unchanged;
  - R7: info has 5 edges.

### Read only if needed
- "Implementation plan › Build changes": rows 4–7.
- "Implementation plan › Patch cell": rows 8–9.
- "Implementation plan › NB_SETUP_INITIAL_DDL": rows 10–11.
- "Implementation plan › Mapping §1.2": rows 1–3.
- "Implementation plan › Contract tests": rows 12–18.
- "Alternatives": why a new cell rather than editing `srvpoipy` or using `ensure_target` (rows 8–9, 15–18).
- "Partial failure", "Retry and recovery", "Rollback and forward recovery": steps 5–9.
- "Idempotency": row_hash behaviour on RUN 1 (step 8).
- "Verification": steps 5–8.

# Architecture: 20261025-gld-srv-poi-info-rating-review

Grain, keys, column types and lineage come from `model-design.md` (`## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`) and from ledger rows D-01 to D-05. This document does not restate them. It covers only the runtime, DDL, config and test design.

## Scope

- `NB_GLD_SRV_POI_INFO` (`srvinfobuild`):
  - two new inputs, `rating` → `slv_3p_poi_rating` and `review` → `slv_3p_poi_review`;
  - a per-key grain stop on rating, a `COUNT(*)` review aggregate, a Google-only left join and an INT range stop;
  - three new `OUT_COLS`;
  - two new metrics.
- `NB_CREATE_DDL`: a new patch pair at the end, `srvratemd` and `srvratepy`. The cell adds the three nullable columns to the existing gold table at their contract position and inserts the two GLD_30P edges.
- `NB_SETUP_INITIAL_DDL`: the three columns go into the `gld_srv_poi_info` `TABLE_SPECS` entry, and two rows go into `PIPELINE_CONFIG_ROWS`.
- Mapping §1.2 gets three rows and one rule paragraph.
- Contract tests.

## Non-goals

- Mapping §1.1, the Google intersection, the partner-full rule, `operating_hours`, `is_recommended` and every existing column stay unchanged.
- No row is chosen among duplicate rating rows. No `review_count` is coalesced to 0. No column is widened to BIGINT.
- No change to `ctrl_cfg_schema_registry`, `01_DATA_MODEL.md`, `NB_LIB_TRANSFORM_SLV_GLD`, or the GLD_30P schedule.
- No edit of the old cell `srvpoipy`. `02_NAMING_CONVENTION.md` §2.1 rule 4 forbids it.

## Invariants

1. The output has one row per `poi_id`, and the MERGE key is `poi_id`. The rating join is 1:1 only after the grain stop. The review join is on a grouped aggregate.
2. Row set equality: the set of `poi_id` values is the same as with the pre-change build on the same pinned inputs. The new joins never add or remove a row.
3. Rows whose `lower(trim(source_name))` is not `google` get NULL in all three columns (D-04).
4. A Google row with no rating match gets NULL `rating_overall` and NULL `rating_count`. A Google row with no review row gets NULL `review_count`, never 0 (D-02).
5. `review_count` is `COUNT(*)` grouped by `poi_id`. Rows with a NULL `review_id` are counted (D-02).
6. `rating_overall` is passed through as `decimal(4,2)`. Any other source type stops the node with ConfigError. `rating_count` and `review_count` are INT. Any value outside the INT range stops the node with QualityGateError, before the write (D-03).
7. If a kept Google `poi_id` has more than one `slv_3p_poi_rating` row, the node stops with QualityGateError before the write (D-01).
8. The following five lists are equal, column for column and in order:
   - `OUT_COLS` + TECH;
   - `srvratepy.INFO_COLS`;
   - the `NB_SETUP_INITIAL_DDL` spec for the table;
   - the mapping §1.2 Target Fields, with `row_hash`/`deleted_at` excluded, plus `created_at`/`updated_at`;
   - the DEV physical schema after the patch.
9. `SPEC.inputs` equals the set of active GLD_30P edges into `gld_srv_poi_info`, which has 5 sources. `required_inputs` stays `("entity",)`.

## State ownership

| State | Owner | Writer in this task |
|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` schema | `NB_CREATE_DDL` (patch cell) / `NB_SETUP_INITIAL_DDL` (empty env) | `srvratepy` ALTER |
| `gld_srv_poi_info` rows | `run_node` MERGE in `NB_GLD_SRV_POI_INFO` | node RUN |
| GLD_30P edges in `ctrl_mng_pipeline_config` | DDL notebooks | `srvratepy` INSERT … WHERE NOT EXISTS; initial seed MERGE NOT MATCHED |
| Flow lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30P` | lib + DDL patch cells | `srvratepy` acquires and releases it, like `srvpoipy` |
| `slv_3p_poi_rating`, `slv_3p_poi_review` | FL_00 extract | read only, at pinned versions |

## Grain and keys

See `model-design.md` `## Keys` and `## Columns`. The architecture adds two runtime guards:

- The grain stop runs on the rating rows semi-joined to the kept Google keys, the same scope as `_destination`. Only those rows can fan out the MERGE source.
- The existing lib `quality_gate` checks `pk_duplicate`. That check stays as the backstop.

## Ordering

The build executes in this order:

1. The current filter `~is_google | _both`, then the left join to `des`. Both are unchanged.
2. `google = rows.where(is_google).select("poi_id")`.
3. `_rating(rt, google)`: grain stop.
4. Left join of rating, then left join of `_reviews(rv, google)`.
5. INT range stop.
6. The hours UDF and the select, with `F.when(is_google, …)` on the three columns.
7. The existing `_err` stop.
8. Metrics.

Every stop raises inside `build`. `run_node` therefore marks the run FAILED before `ensure_target` and before MERGE.

The patch cell runs in this order:

1. Acquire the lock.
2. Pre-check everything without writing.
3. Run one ALTER per missing column, with `_refresh_lock()` before each.
4. Call `_refresh_lock()`, then INSERT the edges.
5. Post-check.
6. Release the lock in `finally`.

ALTER precedes INSERT. Once the edges exist, the new node is runnable. If the node ran before the columns existed, `ensure_target` would append them after `deleted_at`.

## Transaction and commit boundaries

- `srvratepy` makes:
  - up to 3 ALTER commits, one per column, the same per-column pattern as `enrflagpy` `_add_flags`;
  - 1 INSERT commit on config;
  - lock-row UPDATEs on `ctrl_mng_watermark`.
- The node makes:
  - 0 commits on the target when the diff is empty;
  - otherwise 1 MERGE commit;
  - plus 1 append to `ctrl_log_table_run`.
- After the patch, `ensure_target` is a no-op because every column already exists.

## Idempotency

- `srvratepy` rerun: the missing set is empty, so there is no ALTER. The INSERT has a NOT EXISTS clause, so it adds 0 rows. The post-check passes. The cell prints `gld_srv_poi_info +[]`.
- Node RUN twice: the second run gives 0/0/0 and no new Delta version.
- `row_hash` is computed as `sha2(to_json(struct))`. Spark's default `to_json` omits NULL fields. So rows where all three new values are NULL keep their hash and are not rewritten. Google rows with values get a new hash and are updated once.
- Both outcomes are correct, because the ALTER-added columns start as NULL.

## Concurrency

- `srvratepy` and every node RUN share the GLD_30P flow lock (90-minute lease, `_refresh_lock` owner re-check), the same as `srvpoipy`.
- FL_00 may write the rating and review tables during a run. `run_node` reads pinned source versions, so the grain check and the join see one snapshot.
- GLD_30P is not scheduled (runbook of task 20261024), so there is no automatic overlap.

## Retry and recovery

- Patch cell:
  - A lock is held by someone else, or the lock was lost: no write. Rerun later.
  - The cell is interrupted after 1 or 2 ALTERs: the pre-check accepts any in-order subset of the new columns as missing. A rerun adds the rest with the correct `AFTER` anchor.
  - The cell is interrupted after the ALTERs and before the INSERT: a rerun inserts the edges.
- Node: every stop is pre-write. Fix the cause, or record a decision for a grain change, then rerun RUN. The build is a full recompute.

## Partial failure

| Point | State left | Effect | Recovery |
|---|---|---|---|
| New notebook deployed, `srvratepy` not run | 3 edges in config, SPEC has 5 inputs | Node fails with ConfigError `spec.inputs lệch config`, no write | Run `srvratepy` |
| `srvratepy` ran, old notebook still deployed | 5 edges, SPEC has 3 inputs | Same ConfigError, no write | Deploy the notebook |
| Some ALTERs done, no INSERT | 1–3 NULL columns, 3 edges | Node fails with ConfigError | Rerun the cell |
| Node ran before the cell (not reachable, ConfigError comes first) | — | — | — |
| DEV columns appended after `deleted_at` by any other path | Order mismatch | The cell stops with `không khớp hợp đồng` and does not fix it | User decision |

Deploy all three notebooks and run `srvratepy` back to back. The window between the two steps is safe because every failure in it is a pre-write ConfigError.

## Observability

- New metrics in `qg_json.metrics`:
  - `rating_matched`: output rows with a rating match, Google only;
  - `review_matched`: output rows with a non-NULL `review_count`.
- Existing metrics are unchanged.
- Stop messages:
  - `gld_srv_poi_info: slv_3p_poi_rating {n} poi_id có hơn một dòng`;
  - `gld_srv_poi_info: ngoài miền INT {json}`;
  - the ConfigError for the type of `rating_overall`.
- The patch cell prints `gld_srv_poi_info +{missing}; cạnh {sources}`.

## Security

- The new reads are only `poi_id`, `rating_overall` and `rating_count`, plus a row count of `poi_id` in review. Review text is not read.
- Probes print counts only.
- No credentials and no new external access.

## Rollout

1. Local tests pass.
2. Deploy `NB_CREATE_DDL`, `NB_SETUP_INITIAL_DDL` and `NB_GLD_SRV_POI_INFO` to DEV together.
3. Run `srvratepy` once, then again for idempotency.
4. Run `NB_SETUP_INITIAL_DDL` with `p_apply=false`.
5. Run the node as DRY_RUN, then RUN, then RUN again.
6. Run `NB_00_ORCHES_SLV_TO_GLD` with PLAN for `PL_VV_TRANS_SLV_TO_GLD_30P`.
7. Run the read-only checks in Verification.

Do not rerun `srvpoipy` on DEV after step 3. Its whole-schema and edge pre-checks will stop safely with `lệch cột` / `Cell không tự bật cạnh`. This is the same accepted pattern as `enrflagpy` after `srvpoipy`. Record it in the runbook.

## Rollback and forward recovery

- Forward recovery is preferred: fix the build and rerun RUN.
- Rollback needs all three of these steps:
  1. A new patch task sets the two edges to `is_active = 0`, with a value-differs condition. Without this, the old SPEC fails with ConfigError.
  2. Redeploy the previous `NB_GLD_SRV_POI_INFO`.
  3. The three columns stay, because they are nullable and DROP is forbidden by rule 5. Their last values on Google rows stay stale, because the old build does not write them. Clearing them needs a one-off `UPDATE … SET … = NULL`, which requires user approval.
- `review_count = 0` never appears, so NULL keeps the meaning "unknown/none" throughout.

## Alternatives

| Option | Verdict | Reason |
|---|---|---|
| A. New patch cell `srvratepy` with `ADD COLUMNS … AFTER` and edges (selected) | Selected | Follows §2.1 rules 3–5. `AFTER` is proven on Fabric by `enrflagpy`. The DEV physical order equals the empty-env order. Cost: three out-of-scope test edits (cell-order slices, contract composition, seed count 59→61), and `srvpoipy` can no longer be rerun on DEV (safe stop). |
| B. Edit `srvpoipy` `GOLD_COLS`/`EDGES_ON` in place | Rejected | Violates rule 4. Its pre-check would block DEV, and `test_gld_srv_patch_guards` forbids `AFTER` and a second ALTER. |
| C. Let `run_node.ensure_target` append the columns | Rejected | The columns land after `deleted_at` on DEV but before TECH in a fresh env, so environments drift. `srvpoipy`-style list checks break. The DDL notebooks would no longer own the schema. |
| D. DROP and recreate the gold table | Rejected | Rule 5; it loses history and `created_at`. |
| Grain check on every rating row vs on kept Google keys | Kept keys | Only those keys can multiply the MERGE source. Same scope as `_destination`. |
| Rely on cast vs explicit INT range check | Explicit check | Fabric runs with ANSI off, so `cast("int")` silently wraps. D-03 requires a stop. |

## Implementation plan

### Build changes (`srvinfobuild`)

Add the constants after `DEST_COLS`, and extend `OUT_COLS`:

```python
RATING_COLS = ("poi_id", "rating_overall", "rating_count")
INT_MIN, INT_MAX = -2147483648, 2147483647
OUT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_category", "subcategory_tags",
            "destination_id", "full_address", "street", "ward", "district", "city", "country_code", "postal_code",
            "lat", "lng", "phone", "email", "website_url", "operating_status", "is_verified", "is_recommended",
            "is_bookable", "operating_hours", "holiday_exceptions", "rating_overall", "rating_count", "review_count")
```

Add the helpers after `_destination`:

```python
def _rating(rating, keys):
    # D-01: một dòng mỗi poi_id. Trùng poi_id -> dừng, không chọn dòng.
    r = rating.select(*RATING_COLS).join(keys, "poi_id", "left_semi")
    dup = r.groupBy("poi_id").count().where("count > 1").count()
    if dup:
        raise QualityGateError(f"gld_srv_poi_info: slv_3p_poi_rating {dup} poi_id có hơn một dòng")
    return r.withColumn("_rated", F.lit(True))


def _reviews(review, keys):
    # D-02: COUNT(*) theo poi_id, review_id NULL vẫn đếm. Không có dòng -> NULL sau left join, không coalesce 0.
    return (review.select("poi_id").join(keys, "poi_id", "left_semi")
            .groupBy("poi_id").agg(F.count(F.lit(1)).alias("review_count")))
```

`build(ctx)` changes. Lines not shown stay as they are.

```python
    rt = ctx.input("rating")
    rv = ctx.input("review")
    # after the existing _require calls:
    _require(rt, RATING_COLS, "slv_3p_poi_rating")
    _require(rv, ("poi_id",), "slv_3p_poi_review")
    rating_type = dict(rt.dtypes)["rating_overall"]
    if rating_type != "decimal(4,2)":
        raise ConfigError(f"gld_srv_poi_info: slv_3p_poi_rating.rating_overall là {rating_type}, cần decimal(4,2)")
    ...
    rows = ent.join(both, "poi_id", "left").where(~is_google | F.col("_both").isNotNull()).join(des, "poi_id", "left")
    google = rows.where(is_google).select("poi_id")
    rows = (rows.join(_rating(rt, google), "poi_id", "left").join(_reviews(rv, google), "poi_id", "left")
            .withColumn("_h", _hours(F.col("source_name"), F.col("opening_hours_text"))))
    bad = rows.agg(*[F.sum(F.when(~F.col(c).between(INT_MIN, INT_MAX), 1).otherwise(0)).alias(c)
                     for c in ("rating_count", "review_count")]).first().asDict()
    over = {c: n for c, n in bad.items() if n}
    if over:
        raise QualityGateError("gld_srv_poi_info: ngoài miền INT " + json_dumps(over))   # D-03
    out = rows.select(
        ...,  # unchanged through "holiday_exceptions"
        "holiday_exceptions", F.when(is_google, F.col("rating_overall")).alias("rating_overall"),
        F.when(is_google, F.col("rating_count")).cast("int").alias("rating_count"),
        F.when(is_google, F.col("review_count")).cast("int").alias("review_count"),
        F.when(is_google, F.col("_rated")).alias("_rated"), F.col("_h.error").alias("_err"))
    ...
    ctx.metrics.update(..., rating_matched=out.where("_rated IS NOT NULL").count(),
                       review_matched=out.where("review_count IS NOT NULL").count())
    return out.select(*OUT_COLS)
```

`SPEC.inputs` becomes `{"entity": …, "destination": …, "multi_lang": …, "rating": "slv_3p_poi_rating", "review": "slv_3p_poi_review"}`.

Constraints on the build source:

- Read the new inputs with the default `live_only`. The 3P snapshot tables have no `row_hash`/`deleted_at`. This keeps `live_only=False` at 3 occurrences.
- Do not write the word `deleted` in code.
- Do not use `countDistinct`.

### Patch cell (`NB_CREATE_DDL` `srvratemd`, `srvratepy`)

Append both cells after `srvpoipy`, with the same metadata shape (`microsoft.language` python / `synapse_pyspark`, `execution_count: null`, `outputs: []`).

`srvratemd` source:

```
# [THÊM 26/10] 20261025-gld-srv-poi-info-rating-review

Thêm `rating_overall` DECIMAL(4,2), `rating_count` INT, `review_count` INT vào `gld_srv_poi_info`, ngay sau `holiday_exceptions`.
Thêm 2 cạnh `PL_VV_TRANS_SLV_TO_GLD_30P`: `slv_3p_poi_rating`, `slv_3p_poi_review` → `gld_srv_poi_info`. Không DROP. Chạy lại không đổi gì.
Sau cell này không chạy lại `srvpoipy` (hợp đồng `gld_srv_poi_info` trong cell đó là bản 29 cột).
```

`srvratepy` source:

```python
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30P"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
INFO_FQ = "lh_vv_gold.dbo.gld_srv_poi_info"
INFO_NEW_COLS = [("rating_overall", "DECIMAL(4,2)"), ("rating_count", "INT"), ("review_count", "INT")]
INFO_COLS = [
    ("poi_id", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
    ("business_sector", "STRING"), ("business_category", "STRING"), ("subcategory_tags", "STRING"),
    ("destination_id", "STRING"), ("full_address", "STRING"), ("street", "STRING"), ("ward", "STRING"),
    ("district", "STRING"), ("city", "STRING"), ("country_code", "STRING"), ("postal_code", "STRING"),
    ("lat", "DOUBLE"), ("lng", "DOUBLE"), ("phone", "STRING"), ("email", "STRING"), ("website_url", "STRING"),
    ("operating_status", "STRING"), ("is_verified", "BOOLEAN"), ("is_recommended", "BOOLEAN"),
    ("is_bookable", "BOOLEAN"), ("operating_hours", "STRING"), ("holiday_exceptions", "STRING"),
    ("rating_overall", "DECIMAL(4,2)"), ("rating_count", "INT"), ("review_count", "INT"),
    ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
]
EDGES_KEEP = ("slv_poi_entity_non_enrich", "slv_enr_poi_destination", "slv_enr_poi_info_multi_lang")
EDGES_ON = [
    (1, "slv_3p_poi_rating", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
    (2, "slv_3p_poi_review", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
]
LOCK = "srvrate-" + uuid.uuid4().hex


def _want(cols):
    return [(name.lower(), dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols]


def _schema(fq):
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields]


def _edge_rows():
    return [(r["pl_name"], r["src_schema"], r["src_tbl"], r["is_active"], r["priority"], r["load_mode"],
             r["nb_name"], r["n"]) for r in spark.sql(f"""
    SELECT pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
    FROM {CFG}
    WHERE trg_schema = '{GLD}' AND trg_tbl = 'gld_srv_poi_info'
    GROUP BY pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name
    """).collect()]


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


# <<< copy verbatim from srvpoipy: the "# Tạo dòng khoá nếu chưa có" MERGE INTO {WM} statement >>>
held = False
failed = None
try:
    # <<< copy verbatim from srvpoipy: lock UPDATE, owner check, RuntimeError "đang giữ khoá" >>>
    held = True
    if "nb_name" not in {f.name.lower() for f in spark.table(CFG).schema.fields}:
        raise RuntimeError(f"{CFG} chưa có cột nb_name: chạy enrddlpy trước")

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    missing = []
    if not spark.catalog.tableExists(INFO_FQ):
        issues.append(f"{INFO_FQ} chưa có: chạy srvpoipy hoặc NB_SETUP_INITIAL_DDL")
    else:
        got = _schema(INFO_FQ)
        have_cols = {name for name, _dtype, _nullable in got}
        missing = [name for name, _dtype in INFO_NEW_COLS if name not in have_cols]
        want = _want(INFO_COLS)
        if got != [col for col in want if col[0] not in missing]:
            issues.append(f"{INFO_FQ} không khớp hợp đồng, không sửa: có {got}, cần {want}")
    keep = {(PL, SLV, src, 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_INFO") for src in EDGES_KEEP}
    new = {(PL, SLV, src, 1, priority, mode, nb) for _q, src, _s, _t, mode, nb, priority in EDGES_ON}
    rows = _edge_rows()
    for pl, src_schema, src, flag, priority, mode, nb, n in rows:
        if pl != PL and flag == 1:
            issues.append(f"cạnh {src}->gld_srv_poi_info đang active ở {pl}")
        if pl == PL and ((pl, src_schema, src, flag, priority, mode, nb) not in keep | new or n != 1):
            issues.append(f"Cell không tự bật cạnh: {pl} {src_schema}.{src} active={flag} "
                          f"priority={priority} mode={mode} nb={nb} n={n}")
    have_edges = {row[:7] for row in rows}
    if not keep <= have_edges:
        issues.append(f"thiếu cạnh của srvpoipy: {sorted(keep - have_edges)}")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

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
    # <<< copy verbatim from srvpoipy: INSERT INTO {CFG} … FROM VALUES {values} … WHERE NOT EXISTS (…) >>>

    # Sau khi ghi: chỉ xét phần cell thêm.
    problems = []
    if _schema(INFO_FQ) != _want(INFO_COLS):
        problems.append(f"{INFO_FQ} lệch cột")
    active = {row[:7]: row[7] for row in _edge_rows() if row[3] == 1}
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
    # <<< copy verbatim from srvpoipy: release UPDATE {WM} … WHERE lock_exec_id = '{LOCK}' >>>
```

The four `<<< copy verbatim >>>` markers stand for the statements in `srvpoipy` with the same purpose (the lock-row MERGE, acquire, the config INSERT, and release). Main replaces each marker with those exact lines. The final cell must contain no `<<<` text.

### `NB_SETUP_INITIAL_DDL`

- In `init_tables`, inside the `'lh_vv_gold.dbo.gld_srv_poi_info'` spec (the first `('holiday_exceptions', 'STRING', None)`, not the entity spec), insert three tuples after `holiday_exceptions`: `('rating_overall', 'DECIMAL(4,2)', None)`, `('rating_count', 'INT', None)`, `('review_count', 'INT', None)`.
- In `init_seed_ctrl`, append two rows at the end of `PIPELINE_CONFIG_ROWS`, after the `slv_enr_poi_info_multi_lang` → `gld_srv_poi_info` row:
  - `(_GLD30, _S, 'slv_3p_poi_rating', _G, 'gld_srv_poi_info', 1, 1, 'RECOMPUTE', None, None, 'NB_GLD_SRV_POI_INFO'),`
  - the same row for `'slv_3p_poi_review'`.

### Mapping §1.2

Insert after the `holiday_exceptions` row:

```
| slv_3p_poi_rating.rating_overall | decimal(4,2) | transform 1-1 | rating_overall |
| slv_3p_poi_rating.rating_count | integer | transform 1-1 | rating_count |
| slv_3p_poi_review | integer | count review theo poi_id | review_count |
```

After the table, before `### 1.3`, add:

```
`rating_overall`, `rating_count`, `review_count`: `slv_3p_poi_rating` và `slv_3p_poi_review` LEFT JOIN qua `poi_id`, chỉ điền cho dòng `source_name` google (lower/trim). Dòng partner và dòng không khớp để NULL, vẫn giữ `poi_id`. `review_count` = `COUNT(*)` theo `poi_id`, kể cả `review_id` NULL; không coalesce 0. `slv_3p_poi_rating` có hơn một dòng cho một `poi_id` thì dừng, không chọn dòng. `rating_count`, `review_count` ngoài miền INT thì dừng.
```

Add to `srvinfomd` the line: ``rating_overall`, `rating_count`, `review_count`: chỉ Google, left join `slv_3p_poi_rating` / `slv_3p_poi_review` theo `poi_id` (mapping §1.2).`

### Contract tests

`tests/test_gld_srv_poi_contract.py` (in scope):

```python
INFO_FQ = "lh_vv_gold.dbo.gld_srv_poi_info"
NEW_INFO = [("rating_overall", "DECIMAL(4,2)"), ("rating_count", "INT"), ("review_count", "INT")]
NEW_EDGES = [
    (1, "slv_3p_poi_rating", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
    (2, "slv_3p_poi_review", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
]


def test_info_rating_patch():
    ids = [cell.get("id") for cell in _nb("NB_CREATE_DDL.ipynb")["cells"]]
    assert ids[-4:] == ["srvpoimd", "srvpoipy", "srvratemd", "srvratepy"]
    patch = _cell("NB_CREATE_DDL.ipynb", "srvratepy")
    base = _assign(_cell("NB_CREATE_DDL.ipynb", "srvpoipy"), "GOLD_COLS")[INFO_FQ]
    assert _assign(patch, "INFO_NEW_COLS") == NEW_INFO
    assert _assign(patch, "INFO_COLS") == base[:-len(TECH)] + NEW_INFO + base[-len(TECH):]
    assert _assign(patch, "EDGES_ON") == NEW_EDGES
    order = ["held = True", "Dừng trước khi ghi", "ALTER TABLE", "INSERT INTO {CFG}", "Sau khi ghi", "finally:"]
    positions = [patch.index(token) for token in order]
    assert positions == sorted(positions)
    code = "\n".join(line for line in patch.splitlines() if not line.strip().startswith("#"))
    for token in ("DROP", "DELETE", "TRUNCATE", "UPDATE {CFG}", "REPLACE", "columnMapping", "<<<"):
        assert token not in code
    assert code.count("ALTER TABLE") == 1 and " AFTER " in code
    assert "LEASE_MINUTES = 90" in patch and "lock_exec_id = '{LOCK}'" in patch
    assert patch.rindex("_refresh_lock()") < patch.index("INSERT INTO {CFG}")


def test_mapping_targets_match_out_cols():
    table = MAPPING.read_text(encoding="utf-8").split("### 1.2. Field Mapping", 1)[1].split("### 1.3", 1)[0]
    rows = [line.split("|")[1:-1] for line in table.splitlines() if line.startswith("|")][2:]
    out = _assign(_cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild"), "OUT_COLS")
    assert [cells[3].strip() for cells in rows] == list(out) + ["created_at", "updated_at"]
    types = {cells[3].strip(): cells[1].strip() for cells in rows}
    assert types["rating_overall"] == "decimal(4,2)"
    assert types["rating_count"] == types["review_count"] == "integer"


def test_info_rating_build_rules():
    source = _cell("NB_GLD_SRV_POI_INFO.ipynb", "srvinfobuild")
    code = "\n".join(line for line in source.splitlines() if not line.strip().startswith("#"))
    assert "countDistinct" not in code and "F.count(F.lit(1))" in code
    assert "INT_MIN, INT_MAX = -2147483648, 2147483647" in code
    assert "poi_id có hơn một dòng" in code and "ngoài miền INT" in code
    assert code.count("F.when(is_google,") == 4
    assert "coalesce(F.col(\"review_count\")" not in code
```

The existing tests also change:

- `test_node_specs`: the `srvinfobuild` expected inputs add `"rating": "slv_3p_poi_rating", "review": "slv_3p_poi_review"`. `required_inputs` stays `("entity",)`.
- `test_build_columns_match_ddl`: after `gold = …`, add `gold[INFO_FQ] = _assign(_cell("NB_CREATE_DDL.ipynb", "srvratepy"), "INFO_COLS")`.

Out-of-scope tests. These edits need the scope amendment in Order stop 1.

- `tests/test_initial_ddl_contract.py`:
  - `test_columns_match_sources`: replace the gold contract of `gld_srv_poi_info` with `srvratepy` `INFO_COLS` before the loop over `GOLD_COLS`.
  - `test_gld_srv_patch_create_matches_init`: set `contracts["lh_vv_gold.dbo.gld_srv_poi_info"] = _assign(_cell(_notebook("NB_CREATE_DDL.ipynb"), "srvratepy"), "INFO_COLS")`.
  - `test_pipeline_config_rows_match_sources`: after the `srvpoipy` loop, add the same loop over `_assign(_cell(ddl, "srvratepy"), "EDGES_ON")`, and change `59` to `61`.
- `tests/test_enr_poi_contract.py::test_info_patch_cell_guards` and `tests/test_poi_entity_contract.py::test_create_ddl_patch`:
  - shift the id slices by 2: `[-14:-8]`, `[-8:-6]`, `[-6:-4]`, `[-4:-2] == ["srvpoimd", "srvpoipy"]`;
  - add `ids[-2:] == ["srvratemd", "srvratepy"]`.

## Verification

Local:

- `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
- `python -m pytest -q`

Fabric DEV, read only except the planned runs. Print counts only.

- **R0 baseline:**
  - `DESCRIBE TABLE lh_vv_gold.dbo.gld_srv_poi_info` gives 29 columns;
  - the B2 query from task 20261024 gives 6 GLD_30P edges;
  - config `count(*)` gives 59;
  - `DESCRIBE HISTORY` gives the last version.
- **R1 `srvratepy` run 1:** prints `+['rating_overall', 'rating_count', 'review_count']`. DESCRIBE gives 32 columns, with the new ones at positions 26–28 typed `decimal(4,2)`, `int`, `int`, nullable. Config count is 61. `gld_srv_poi_info` has 5 active edges with n=1.
- **R2 `srvratepy` run 2:** prints `+[]`. No new version on the gold table. Config count stays 61.
- **R3 `NB_SETUP_INITIAL_DDL` with `p_apply=false`:** 18 `EXISTS_OK`, no `schema_issues`, pipeline seed `to_insert=0` with 61 rows.
- **R4 helper probe** in a scratch session. Paste the `srvinfobuild` definitions after `%run NB_LIB_TRANSFORM_SLV_GLD`. Use `keys` = Google `poi_id`s of `slv_poi_entity_non_enrich`. Print:
  - `_rating(rt, keys).count()`;
  - `_reviews(rv, keys).count()`;
  - `_reviews(rv, keys).agg(F.max("review_count"))`.

  The probe must not raise. This exercises the matched path even when the Google intersection is empty.
- **R5 node runs:**
  - DRY_RUN: SUCCESS, no new target version.
  - RUN 1: SUCCESS. The updated count is at most the Google rows with any value. Metrics include `rating_matched` and `review_matched`.
  - RUN 2: 0/0/0, no new version.
- **R6:** run on the live rows (`deleted_at IS NULL`), then the cross-check right after RUN 1.

  ```sql
  SELECT count(*) n_live, count(DISTINCT poi_id) n_poi,
    sum(CASE WHEN coalesce(lower(trim(source_name)),'') <> 'google' AND (rating_overall IS NOT NULL OR rating_count IS NOT NULL OR review_count IS NOT NULL) THEN 1 ELSE 0 END) non_google_filled,
    sum(CASE WHEN review_count = 0 THEN 1 ELSE 0 END) review_zero
  FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL
  ```

  Expected: `n_live = n_poi =` the pre-change live count, `non_google_filled = 0`, `review_zero = 0`.

  ```sql
  SELECT count(*) mismatches FROM lh_vv_gold.dbo.gld_srv_poi_info g
  LEFT JOIN lh_vv_silver.dbo.slv_3p_poi_rating r ON g.poi_id = r.poi_id
  LEFT JOIN (SELECT poi_id, count(*) c FROM lh_vv_silver.dbo.slv_3p_poi_review GROUP BY poi_id) v ON g.poi_id = v.poi_id
  WHERE g.deleted_at IS NULL AND lower(trim(g.source_name)) = 'google'
    AND NOT (g.rating_overall <=> r.rating_overall AND g.rating_count <=> CAST(r.rating_count AS INT) AND g.review_count <=> CAST(v.c AS INT))
  ```

  Expected: 0. Any FL_00 write between RUN and the query can cause drift; record the source versions if that happens.
- **R7 PLAN:** `NB_00_ORCHES_SLV_TO_GLD` with PLAN shows 2 nodes, and `gld_srv_poi_info` has 5 edges. Only the accepted cadence WARNs appear.
