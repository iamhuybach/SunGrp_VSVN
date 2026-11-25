RESULT: PASS

## Main brief

### Decision
D-07 is implemented as a third parameter `all_day` on `legacy_hours`. It is computed in Spark as `coalesce(lower(trim(get_json_object(poi_opening_hours_json,'$.is_24_7'))) = 'true', false)`. When true, the function returns the case-2 output `_dump([_all_day(d) for d in 1..7])` with reason `IS_24_7` and does not read `periods_json`. The verbatim `google_hours` block, MERGE, `load_origin`, stage order, and the other four columns are unchanged. The round-1 code is already in the notebook. This round edits only `legacy_hours`, the UDF call, the summary `reason` expression, and one summary key. No model design and no DDL. Verdict PASS.

### Invariants Main must preserve
- `test_hours_block_is_verbatim_copy` stays green: the `BEGIN_HOURS_PURE` span is not edited.
- `legacy_hours(src, any_text, True) == (google_hours('[{"open_hour":0,"open_minute":0,"day_of_week":0}]')[0], "IS_24_7")` for src google or partner, including text `None`, `"[]"`, `"{"`, and valid periods.
- `legacy_hours("other", x, True) == (None, "SOURCE_NOT_GOOGLE_PARTNER")`: the source check runs first.
- With `all_day` false (the default), every round-1 result is unchanged: `None`/`[]` give `NO_PERIODS`, and `close_hour` null gives `GOOGLE_BAD_TIME`.
- The case-2 JSON has 7 objects, days 1..7, `is_open_all_day` true, `is_closed` false, and no `open_time`, `close_time`, or `value`.
- `is_247` is never NULL when passed to the UDF (`F.coalesce(..., F.lit(False))`).
- The sum of `summary.info.hours_reason` equals `summary.info.candidates`. `IS_24_7` rows have non-NULL `operating_hours`.
- Rows with `load_origin IS NULL` are identical at info `v_pre` and `v_post`, and there are no duplicate `poi_id` rows.
- No new raise: a row never stops the run (D-05). The existing guards stay before `write_insert_only`.
- The summary holds counts and codes only.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | `lgppure`, `def legacy_hours` | Replace with architecture "E1": signature `(source_name, text, all_day=False)`, updated docstring, and after the source check `if all_day is True: return _dump([_all_day(day) for day in range(1, 8)]), "IS_24_7"`. The rest is unchanged. | row 5 passes; existing `test_legacy_hours_rules` still passes |
| 2 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | `lgpmain`, info stage, `det = det.withColumn("_h", hours_udf(` | Add `is_247 = F.coalesce(F.lower(F.trim(F.get_json_object(F.col("poi_opening_hours_json"), "$.is_24_7"))) == F.lit("true"), F.lit(False))` before it, and pass `is_247` as the third UDF argument (architecture "E2"). | row 6 string asserts pass |
| 3 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | `lgpmain`, info stage, `reason = ` | Replace with `F.coalesce(F.col("_hours_reason"), F.when(F.col("operating_hours").isNotNull(), F.lit("OK")), F.lit("NO_DETAIL"))` (architecture "E3"). | old `.otherwise(F.coalesce(F.col("_hours_reason"), F.lit("NO_DETAIL")))` is gone |
| 4 | notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb | `lgpmain`, info stage, `summary["info"].update({` | Add `"hours_24_7_partner_n": info_src.where(is_p & (F.col("_hours_reason") == F.lit("IS_24_7"))).count(),` (architecture "E4"). | key present before `info_src.drop("_hours_reason")` |
| 5 | tests/test_legacy_gold_poi_init_contract.py | new `test_legacy_hours_is_24_7` | Cases listed in architecture "Verification > Local" | passes |
| 6 | tests/test_legacy_gold_poi_init_contract.py | new `test_init_is_24_7_path` | String asserts on the info-stage text, listed in architecture "Verification > Local" | passes |

### Order and stop points
1. Edit rows 1–4, then add tests 5–6. Do not modify existing tests. Run the local tests. If a test fails, fix the code and keep the invariants.
2. Re-author the runbook for D-07 expectations: `python scripts/vv.py run-author 20261120-legacy-gold-init-mapping-audit --kind runbook`. It must carry architecture "Verification > Runtime" items 1–6 and pins `{"poi_master": 8065, "poi_enrichment_display": 6489, "poi_detail": 6912, "poi_review": 69, "poi_rating": 63}`. Then run the specialist review (`sql-data-reviewer`, `spark-runtime-reviewer`).
3. **STOP: evidence (`waiting_runtime`).** The user runs PLAN and pastes the summary. Continue only if all of these hold:
   - `map.drift_n = 0`, `detail_conflict_n = 0`, `rating_cast_fail_n = 0`, `candidates = 45476`;
   - the sum of `hours_reason` equals `candidates`;
   - `GOOGLE_BAD_TIME` is absent or 0;
   - `IS_24_7 >= 6430`, `OK <= 29988`, `NO_PERIODS <= 9058`, and `NO_DETAIL` is absent or 0.

   Report `29988 - OK`, `9058 - NO_PERIODS`, and `hours_24_7_partner_n`. D-07 accepts these, so they do not block. If any condition fails, stop and report. Do not invent a rule.
4. **STOP: evidence (`waiting_runtime`).** The user runs RUN and the post-checks. Pass when:
   - commit is `COMMITTED`, there are no duplicate `poi_id`, and the `load_origin IS NULL` EXCEPT ALL returns 0 rows in both directions;
   - Google legacy `oh_null < 25917` and `<= NO_PERIODS + NO_DETAIL + GOOGLE_*`;
   - Google `all_day_n > 0` and `all_day_bad_n = 0`;
   - Google `holiday_exceptions` is NULL;
   - the partner rating and review columns are NULL, and `is_recommended` is true exactly for partner.
5. No commit unless the user asks.

### Tests and verification
- `python -m pytest tests/test_legacy_gold_poi_init_contract.py tests/test_gld_srv_poi_contract.py -q`
- New: `test_legacy_hours_is_24_7`, `test_init_is_24_7_path`.
- Must stay green unchanged: `test_hours_block_is_verbatim_copy`, `test_legacy_hours_rules`, `test_init_hours_and_holiday_paths`, `test_init_rating_review_recommended`, `test_legacy_upsert_updates_only_legacy_rows`, `test_init_write_targets_dev_only`, and the rest of the file.
- Runtime: runbook items from architecture "Verification > Runtime" 1–6.

### Read only if needed
- "Implementation plan > E1" covers row 1, "E2" row 2, "E3" row 3, "E4" row 4.
- "Verification > Local" covers rows 5–6. "Verification > Runtime" covers stops 3–4.
- "Partial failure" covers rows 1–3 and stop 3: evaluation order, expected bucket counts, and accepted D-07 consequences.
- "Alternatives" covers row 1–2: why a UDF parameter instead of a Spark literal or a `google_hours` change, and why `lower(trim)` runs in Spark.
- "Grain and keys" covers row 2 and the `detail_conflict_n = 0` check.
- "Idempotency", "Rollback and forward recovery" cover stops 3–4: same pins, git revert plus rerun.

# Architecture: 20261120-legacy-gold-init-mapping-audit (round 2)

Risk: high. This round adds D-07 (`is_24_7` true gives the mapping case-2 output) on top of the round-1 design, which is already in `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb` (cells `lgphours`, `lgppure.legacy_hours`, and the info stage of `lgpmain`) and in `tests/test_legacy_gold_poi_init_contract.py`. I read those cells for this round. Round-1 decisions that still hold are only summarized here. The new work is the D-07 delta (sections E1–E4). Column verdicts come from `evidence/column-mapping.md`. Shapes come from `evidence/results/hours-shape.txt` and `evidence/results/google-bad-time-cause.txt`. The PLAN baseline is `evidence/results/plan-summary.json` (exec `lgp-200ee509…`).

## Scope

Five `gld_srv_poi_info` columns are fixed in the init notebook. Round 1 implemented them, and round 2 changes only `operating_hours`.

| Column | Init expression after this round | Rule | Round |
|---|---|---|---|
| operating_hours | `legacy_hours(source_name, get_json_object(poi_opening_hours_json,'$.periods_json'), is_247)`. `is_247` is `coalesce(lower(trim(get_json_object(poi_opening_hours_json,'$.is_24_7'))) = 'true', false)`. A true value returns case 2 (7 all-day days) with reason `IS_24_7`, and `periods_json` is not read. Otherwise the result is the verbatim `google_hours`. NULL or `[]` gives NULL `NO_PERIODS`, and an error code gives NULL plus the code. | D-01, D-02, D-05, D-07 | 1 + 2 |
| holiday_exceptions | Partner: the raw `$.holiday_exceptions_json`. Google: NULL. | D-03 | 1 (no change) |
| rating_count | Google only: `poi_rating.total_reviews`. NULL stays NULL. | D-04 | 1 (no change) |
| review_count | Google only: `COUNT(*)` of old `poi_review`. No rows gives NULL. | D-04 | 1 (no change) |
| is_recommended | `coalesce(lower(trim(source_name)) = 'partner', false)` | D-04 | 1 (no change) |

Every other column, table, and stage keeps its current behavior. `column-mapping.md` marks them `match`.

## Non-goals

- No change to `poi_id`, `load_origin`, the map table, `insert_only_sql`, `legacy_upsert_sql`, `write_insert_only`, `to_target`, locks, pins, or the stage list and order.
- No change to the `# BEGIN_HOURS_PURE`..`# END_HOURS_PURE` block. It stays byte-equal to `NB_GLD_SRV_POI_INFO` `srvinfohours`. `google_hours` does not learn about `is_24_7`, because the current model has no such branch (D-07 rationale).
- No change to `NB_GLD_SRV_POI_INFO`, `NB_LIB_TRANSFORM_SLV_GLD`, DDL, or the serving API.
- No rewriting of `periods_json` elements, for example by turning null `close_*` into an `ALL_DAY` element. D-07 says `periods_json` is not read on 24/7 rows.
- No `is_24_7` handling for sources other than google or partner. Those rows keep `SOURCE_NOT_GOOGLE_PARTNER`.
- No parser for `policies.operating_hours` (mapping §1.5). That object is not in old gold (D-01).
- No change to `holiday_exceptions` on 24/7 rows. D-03 still applies.

## Model design

Not applicable: no table, column, type, grain, or key changes. Case 2 is an existing value of `operating_hours` in `docs/context/mapping_gld_srv_poi_info.md` (rule 3.3, Case 2), and `google_hours` already emits it for the `ALL_DAY` element. `run-author --kind model` is not a blocking step.

## Invariants

1. I1: Only rows with `load_origin = 'LEGACY_INIT'` are updated. Rows of `gld_srv_poi_info` with `load_origin IS NULL` are identical at info `v_pre` and `v_post` (EXCEPT ALL in both directions returns 0 rows).
2. I2: No duplicate `poi_id` after the rerun. The pre-MERGE duplicate check in `write_insert_only` and the `poi_id` MERGE key are unchanged.
3. I3: The `BEGIN_HOURS_PURE` span in `lgphours` is byte-equal to `srvinfohours`. D-07 lives only in `legacy_hours`.
4. I4 (D-07): for source google or partner, `all_day is True` returns exactly `(_dump([_all_day(d) for d in range(1, 8)]), "IS_24_7")`, whatever `text` holds (NULL, `[]`, invalid JSON, valid periods). That value equals `google_hours('[{"open_hour":0,"open_minute":0,"day_of_week":0}]')[0]`: 7 objects for days 1–7, `is_open_all_day` true, `is_closed` false, and no `open_time`, `close_time`, or `value` key.
5. I5: `is_247` is computed in Spark as `coalesce(lower(trim(get_json_object(poi_opening_hours_json, '$.is_24_7'))) = 'true', false)`. It is never NULL when passed to the UDF. Any value other than `true` (including `false`, NULL, or a missing key) leaves the round-1 path unchanged.
6. I6: With `all_day` false, `legacy_hours` behaves exactly as in round 1. `None`/`[]` gives `(None, "NO_PERIODS")`, never seven closed days. Error codes give `(None, code)`, the run continues, and the code is counted (D-05).
7. I7: The source check runs before the 24/7 branch. Source `other` with `all_day` true still returns `(None, "SOURCE_NOT_GOOGLE_PARTNER")`.
8. I8: Every info candidate has exactly one `hours_reason` bucket. The sum of `summary.info.hours_reason` equals `summary.info.candidates`. `IS_24_7` rows have non-NULL `operating_hours`. `OK` rows have non-NULL `operating_hours` and a NULL `_hours_reason`.
9. I9: Google `holiday_exceptions` is always NULL. Partner keeps the unparsed string. `rating_count` and `review_count` are NULL for non-Google rows. The `info_src` row count is unchanged by the overrides (round-1 guard).
10. I10: The summary holds counts and codes only, with no hours text, names, or ids.

## State ownership

Not changed. Init owns `LEGACY_INIT` rows. `PL_VV_TRANS_SLV_TO_GLD_30M` owns rows with `load_origin` NULL and takes over a legacy row through the existing `sql_merge_target` owner predicates. D-07 changes only a value init computes for rows it owns or inserts.

## Grain and keys

`gld_srv_poi_info` is one row per `poi_id`, as defined in the reference task's `model-design.md` and unchanged here. `det` is `poi_detail` joined to `vi_key`, which has one legacy id per `_new` under D-06. `is_247` is a per-row function of the same `poi_detail` row that supplies `periods_json`, so it adds no rows and no join. `_hours_reason` is already part of `det_cols`, so the new `IS_24_7` value enters `single_payload` like any other code. A detail conflict can come only from more than one `poi_detail` row per legacy id, as in round 1. The baseline `detail_conflict_n` is 0 and PLAN must show 0 again.

## Ordering

The stage order (map, info, multi_lang, review, media, amenity) is unchanged. Inside the info stage:

1. Build `det`. Compute `is_247` and `_h = hours_udf(source_name, periods_json, is_247)` (E2).
2. `det_rows`, `single_payload`, and join `det_one`. Unchanged.
3. `master_one` join, the `is_recommended`, `rating_count`, and `review_count` overrides, and the guards. Unchanged.
4. Summary: `reason` uses the new expression (E3), and `hours_24_7_partner_n` is added.
5. `to_target` and `write_insert_only(..., upsert=True)`. Unchanged.

Every raising guard still runs before `write_insert_only`.

## Transaction and commit boundaries

Not changed. Each table gets one Delta MERGE commit tagged `LEGACY_INIT:{EXEC}`, and `_commit_lookup` checks it. The D-07 values land in the same info MERGE commit as the other info columns.

## Idempotency

Rerunning is a `legacy_upsert_sql` MERGE. Matched `LEGACY_INIT` rows get all mutable columns again, including the recomputed `row_hash`. With the same pins, `is_247` and `legacy_hours` are deterministic: `_dump` uses a fixed key order, `ensure_ascii=False`, and compact separators. A second rerun therefore writes identical values. Pipeline rows match no UPDATE clause.

## Concurrency

Not changed. RUN holds `acquire_flow_lock(PL, ...)`, and `refresh_flow_lock` runs before each write.

## Retry and recovery

A guard that raises before the info MERGE writes nothing to info and records `failed_stage`. Fix the cause and rerun with the same pins. A failure after the info commit leaves info correct, and a rerun is safe (Idempotency).

## Partial failure

Row-level hours outcomes, in evaluation order inside `legacy_hours`:

| Order | Condition | Value | Reason | Expected (pins of plan-summary) |
|---|---|---|---|---|
| 1 | source not google/partner | NULL | `SOURCE_NOT_GOOGLE_PARTNER` | 0 (map nulls these `poi_id`) |
| 2 | `all_day` true (D-07) | case 2 | `IS_24_7` | at least 6430 (all GOOGLE_BAD_TIME rows had `is_24_7 = true`), plus any OK/NO_PERIODS row with the flag |
| 3 | `periods_json` NULL or `[]` | NULL | `NO_PERIODS` | at most 9058 |
| 4 | `google_hours` error | NULL | `GOOGLE_*` | `GOOGLE_BAD_TIME` 0: the probe found every bad row is `close_null` with `is_24_7 = true` |
| 5 | `google_hours` OK | 7+ day objects | none, counted `OK` | at most 29988 |
| n/a | no detail payload joined | NULL | `NO_DETAIL` | 0 |

Two consequences of D-07 are accepted by the decision and only reported:

- An OK row with valid periods and `is_24_7 = true` becomes case 2. The PLAN delta `29988 - OK` measures this.
- A NO_PERIODS row with `is_24_7 = true` becomes case 2. The delta `9058 - NO_PERIODS` measures this.

Under the same pins, `IS_24_7 = 6430 + (29988 - OK) + (9058 - NO_PERIODS) + (6430-baseline GOOGLE_BAD_TIME rows now flagged, already counted in the 6430) - remaining GOOGLE_BAD_TIME`. Put simply, buckets only move into `IS_24_7`, and the total stays 45476.

The run raises before the write on:

- a rating cast failure;
- an INT overflow;
- a candidate-count change.

These are unchanged. No new raise is added: per D-05, a row never stops the run.

## Observability

Keys in `summary["info"]`, counts only:

| Key | Change |
|---|---|
| `hours_reason` | gains the bucket `IS_24_7`. The bucket expression becomes `coalesce(_hours_reason, when(operating_hours IS NOT NULL, 'OK'), 'NO_DETAIL')` (E3). For every round-1 case it gives the same bucket. |
| `hours_24_7_partner_n` | new: partner candidates whose reason is `IS_24_7` |
| `detail_conflict_n`, `rating_*`, `review_*`, `holiday_partner_nonnull_n` | unchanged |

PLAN prints them without writing.

## Security

Reads `sgr_visitvn_prd_batch` through `VERSION AS OF` pins, read-only. Writes only `sgr_visitvn_dev.` targets, through the existing guard. Summary and runbook outputs hold counts only. No secrets.

## Alternatives

| Option | Verdict | Reason |
|---|---|---|
| A. Third parameter `all_day` on `legacy_hours`, computed in Spark with `lower(trim)`. The branch returns `_dump([_all_day(d) …])` with reason `IS_24_7`. | Selected | Pure and unit-testable without Spark. It reuses `_all_day`/`_dump` from the verbatim block, so case 2 cannot drift from the model. The `lower(trim)` semantics are exactly the Spark functions D-07 names. The default `False` keeps every round-1 call and test valid. |
| B. Spark `F.when(is_247, F.lit(<case-2 JSON literal>))` around the UDF | Rejected | Duplicates the case-2 JSON as a literal that can drift from `_all_day`/`DAY_LABELS`, and needs a second reason path outside the UDF. |
| C. Add an `is_24_7` branch to `google_hours` | Rejected | Breaks I3 (verbatim copy) and changes the pipeline model, which has no such branch. |
| D. Rewrite null-`close_*` elements into the `ALL_DAY` element, then call `google_hours` | Rejected | Reads and reinterprets `periods_json` on 24/7 rows, contrary to D-07. It would also miss 24/7 rows with NULL or valid periods. |
| E. Do the `lower(trim)` check in Python (`str.strip().lower()`) | Rejected | Python `strip` removes all whitespace while Spark `trim` removes spaces, a semantic gap against D-07's wording. A boolean argument keeps the UDF simpler. |

Trade-off: option A adds one UDF argument and one reason code. It keeps the rule in a single pure function covered by tests, and leaves the pipeline untouched.

## Rollout

1. Apply E1–E4 and run the local tests.
2. Re-author the runbook (`python scripts/vv.py run-author 20261120-legacy-gold-init-mapping-audit --kind runbook`), since PLAN and post-check expectations change for D-07. Then run the specialist review (`sql-data-reviewer`, `spark-runtime-reviewer`).
3. The user runs PLAN on Fabric DEV with `p_pin_json = {"poi_master": 8065, "poi_enrichment_display": 6489, "poi_detail": 6912, "poi_review": 69, "poi_rating": 63}`. Main checks it against "Verification > Runtime" item 1.
4. The user runs RUN and the post-checks.

## Rollback and forward recovery

Forward recovery is preferred: revert the notebook change in git and rerun RUN with the same pins. Under I1 this rewrites only `LEGACY_INIT` rows. `RESTORE TABLE … TO VERSION AS OF <info v_pre>` is allowed only if `DESCRIBE HISTORY` shows no commit after the init commit. Otherwise it would roll back pipeline commits.

## Implementation plan

Round-1 code (H1–H4) is already in the notebook. Only E1–E4 are new.

### E1. `lgppure`: `legacy_hours`

Replace the whole function (signature, docstring, and the new branch). The body after the 24/7 branch is unchanged.

```python
def legacy_hours(source_name, text, all_day=False):
    """D-01/D-02/D-05/D-07: periods_json cũ -> google_hours cho google và partner.
    all_day (is_24_7 true) -> case 2 bảy ngày mở cả ngày, mã IS_24_7, không đọc periods_json.
    NULL hoặc [] -> (None, 'NO_PERIODS'). Mã lỗi -> (None, mã). Không dừng."""
    import json as _json
    if source_name not in ("google", "partner"):
        return None, "SOURCE_NOT_GOOGLE_PARTNER"
    if all_day is True:
        return _dump([_all_day(day) for day in range(1, 8)]), "IS_24_7"
    if text is None:
        return None, "NO_PERIODS"
    try:
        doc = _json.loads(text)
    except (TypeError, ValueError, RecursionError):
        return None, "GOOGLE_INVALID_JSON"
    if isinstance(doc, list) and len(doc) == 0:
        return None, "NO_PERIODS"
    return google_hours(text)
```

`_dump` and `_all_day` come from `lgphours`, the same way `google_hours` does. The test helper `_func` runs this function in the namespace where `lgphours` was executed.

### E2. `lgpmain`, info stage: the `hours_udf` call

Replace the two statements that start with `det = det.withColumn("_h", hours_udf(`:

```python
    is_247 = F.coalesce(
        F.lower(F.trim(F.get_json_object(F.col("poi_opening_hours_json"), "$.is_24_7"))) == F.lit("true"),
        F.lit(False))
    det = det.withColumn("_h", hours_udf(
        F.col("source_name"), F.get_json_object(F.col("poi_opening_hours_json"), "$.periods_json"), is_247))
```

`hours_udf = F.udf(legacy_hours, "struct<value:string,reason:string>")` stays as it is. `det_cols` and `det_rows` are unchanged. The media stage still reads `det` (`_new`, `source_name`, `poi_media_json`) and is not affected.

### E3. `lgpmain`, info stage: `reason` expression

Replace the existing `reason = (F.when(F.col("operating_hours").isNotNull(), F.lit("OK")) .otherwise(...))` with:

```python
    reason = F.coalesce(F.col("_hours_reason"),
                        F.when(F.col("operating_hours").isNotNull(), F.lit("OK")),
                        F.lit("NO_DETAIL"))
```

### E4. `lgpmain`, info stage: summary key

In the existing `summary["info"].update({...})`, add:

```python
        "hours_24_7_partner_n": info_src.where(is_p & (F.col("_hours_reason") == F.lit("IS_24_7"))).count(),
```

It must come before `info_src = info_src.drop("_hours_reason")`. The `update` call already sits before that drop.

### E5. Tests

Add two new tests (see Verification). Every existing test stays unchanged and must pass. They still find `F.udf(legacy_hours`, `"$.periods_json"`, `"hours_reason"`, and `info_src.count() != n_before`, and the 2-argument calls in `test_legacy_hours_rules` still work through `all_day=False`.

## Verification

### Local, no Spark

Command: `python -m pytest tests/test_legacy_gold_poi_init_contract.py tests/test_gld_srv_poi_contract.py -q`

New tests in `tests/test_legacy_gold_poi_init_contract.py`:

- `test_legacy_hours_is_24_7`: exec `lgphours`, then `_func(lgppure, "legacy_hours")`. Let `case2 = google_hours('[{"open_hour":0,"open_minute":0,"day_of_week":0}]')[0]`. Assert:
  - `legacy_hours("google", <element with close_hour None>, True) == (case2, "IS_24_7")`.
  - `legacy_hours("partner", None, True) == (case2, "IS_24_7")`.
  - `legacy_hours("google", "{", True) == (case2, "IS_24_7")`, which shows `periods_json` is not read.
  - `legacy_hours("partner", <valid Sunday 08:00–17:00>, True) == (case2, "IS_24_7")`.
  - `legacy_hours("google", "[]", True) == (case2, "IS_24_7")`.
  - `legacy_hours("other", "[]", True) == (None, "SOURCE_NOT_GOOGLE_PARTNER")`.
  - `legacy_hours("google", <close_hour None>, False) == (None, "GOOGLE_BAD_TIME")`, which shows D-05 still applies without the flag.
  - `json.loads(case2)` has 7 objects with `day_of_week` 1..7 in order, each `is_open_all_day is True` and `is_closed is False`, and none has the keys `open_time`, `close_time`, or `value`.
- `test_init_is_24_7_path`: the info-stage text of `lgpmain` (before `stage = "multi_lang"`) contains:
  - `F.lower(F.trim(F.get_json_object(F.col("poi_opening_hours_json"), "$.is_24_7")))`;
  - `== F.lit("true")`;
  - `"$.periods_json"), is_247)`;
  - `F.coalesce(F.col("_hours_reason")`;
  - `"hours_24_7_partner_n"`.

  It does not contain `.otherwise(F.coalesce(F.col("_hours_reason"), F.lit("NO_DETAIL")))`.
- Existing tests unchanged and green, including `test_hours_block_is_verbatim_copy`, which proves I3.

### Runtime (Fabric DEV, run by the user, written in the re-authored runbook)

1. PLAN with the pins above. Pass when:
   - `map.drift_n = 0`, `info.detail_conflict_n = 0`, `info.rating_cast_fail_n = 0`, `info.candidates = 45476`;
   - the sum of `hours_reason` equals `candidates`;
   - `hours_reason` has no `GOOGLE_BAD_TIME` key, or its value is 0;
   - `hours_reason.IS_24_7 >= 6430`, `OK <= 29988`, `NO_PERIODS <= 9058`, and `NO_DETAIL` is absent or 0.

   Report `29988 - OK`, `9058 - NO_PERIODS`, and `hours_24_7_partner_n`. D-07 accepts these, so they do not block. If any pass condition fails, stop and report. Do not run RUN.
2. RUN. Pass when `summary.info.commit = COMMITTED`.
3. Duplicates: `SELECT poi_id, count(*) FROM gld_srv_poi_info GROUP BY poi_id HAVING count(*) > 1` returns 0 rows.
4. Pipeline rows (I1): `(SELECT * … VERSION AS OF v_pre WHERE load_origin IS NULL) EXCEPT ALL (SELECT * … VERSION AS OF v_post WHERE load_origin IS NULL)` returns 0 rows in both directions.
5. Hours on `load_origin = 'LEGACY_INIT'`, grouped by `source_name`. Compute `n`, `oh_null`, `all_day_n` (`operating_hours LIKE '%"is_open_all_day":true%'`), and `all_day_bad_n` (`all_day_n` rows that also contain `"open_time"`, `"close_time"`, or `"value"`). Pass when:
   - Google `oh_null < 25917` and `oh_null <= NO_PERIODS + NO_DETAIL + sum(GOOGLE_*)` from PLAN;
   - Google `all_day_n > 0`;
   - `all_day_bad_n = 0` for every source;
   - Google `holiday_exceptions` is NULL on every row.
6. Other columns: `rating_count` and `review_count` are NULL on every partner legacy row, and `is_recommended` is true exactly for partner rows. Unchanged from round 1.

Reviewers: `sql-data-reviewer` and `spark-runtime-reviewer`. `state-correctness-reviewer` is not needed, because MERGE, `load_origin`, and write order do not change.
