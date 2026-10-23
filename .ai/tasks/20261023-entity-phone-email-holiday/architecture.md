RESULT: PASS

## Main brief

### Decision
Add `DETAIL_COLS = ("phone", "email", "holiday_exceptions")` after `HOURS_COLS` in the entity build. Google takes `phone` from the existing `contact` frame and emits `email` and `holiday_exceptions` as string-cast nulls. Partner takes `svc.phone` and `svc.email`, and `_holiday` from the same `vi` select as `_hours`.
The setup spec gets three tuples before `row_hash`. NB_CREATE_DDL gets `peholmd` and `peholpy` after `ohpasspy`. The patch is one append-only `ADD COLUMNS` with prechecks and no lock or ctrl write. On DEV the columns land physically after `opening_hours_text`, which `ohpasspy` placed after `deleted_at`. This is accepted because comparisons and writes use column names.
Scope gap: `tests/test_enr_poi_contract.py::test_info_patch_cell_guards` (lines 231–232) asserts that `ohpasspy` is the last cell. It must be added to `scope.files` (proposed D-PEH-07) before editing.

### Invariants Main must preserve
- `SPEC.pk`, `unique_checks`, `inputs`, `required_inputs`, the `dup_contact` QG, the hours expressions, the hours block and warn checks, and `ohpasspy` are byte-identical.
- `OUT_COLS == POI + CONTACT + ADDRESS + CATEGORY + ESTIMATE + HOURS_COLS + DETAIL_COLS`. The setup entity spec has the same order, followed by `row_hash`.
- All three columns are `STRING` nullable in the build, the setup spec, and `peholpy`.
- Google `email` and `holiday_exceptions` are `F.lit(None).cast("string")`, never an untyped `F.lit(None)` (the lib rejects void).
- Google `phone` comes from the same `contact` select that feeds `dup_contact` and the left join.
- Partner `holiday_exceptions` is `F.get_json_object(F.col("amentities"), "$.policies.holiday_exceptions")` inside the `vi = (...)` select, and is not parsed further.
- The block check `phone_email_holiday_other_source` makes all three columns null for sources other than google and partner.
- `peholpy` has exactly one `ALTER TABLE`. With comments stripped, it has no `DROP`, `AFTER`, `MERGE`, `UPDATE`, `INSERT`, `ctrl_mng`, or `lock_exec_id`. Rerunning it writes nothing.
- `peholpy` stops before writing if `opening_hours_text` is missing, if any existing new column is not nullable string, or if the existing new columns are not a leading prefix of `NEW_COLS`.
- No extract, registry, gold, or ctrl change.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb | `b1entitybuild` constants | Add `DETAIL_COLS` with a D-PEH-01 comment. Append `+ DETAIL_COLS` to `OUT_COLS`. | Matches full doc `### Entity build changes` |
| 2 | same | `_google` | Contact select adds `"phone"`. agg adds `with_phone`, metric `google_with_phone`. Final select appends `"phone"` and the two string-cast null aliases. | `test_entity_detail_columns` passes |
| 3 | same | `_partner` | `vi` select adds `_holiday`. agg and metrics add `partner_with_phone`, `partner_with_email`, `partner_with_holiday`. `cols` adds `phone`, `email`, `holiday_exceptions`. | Same test passes |
| 4 | same | `build` | Add `ConfigError` guards for `contact.phone` and `svc.phone`/`svc.email`. | Code matches full doc |
| 5 | same | `SPEC.block_checks` | Append `phone_email_holiday_other_source`. | Test asserts the name |
| 6 | same | `b1entitymd` | Add one description line. | Text present |
| 7 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables`, `slv_poi_entity_non_enrich` spec (second `opening_hours_text`, around JSON line 430; not the gold spec around line 304) | Insert three `('…', 'STRING', None)` tuples before `row_hash`. | `test_poi_entity_columns_derived` passes |
| 8 | notebooks/NB_CREATE_DDL.ipynb | after `ohpasspy` | Append markdown `peholmd` and code `peholpy`, using the verbatim code in full doc `### Patch cells`, with python/synapse_pyspark metadata. | `test_entity_detail_patch_cell` passes |
| 9 | tests/test_initial_ddl_contract.py | `test_poi_entity_columns_derived` | Exec `init_cfg_partner`, flatten partner rows, add `DETAIL_COLS` and type asserts, extend `expected` after `opening_hours_text`. | Passes |
| 10 | tests/test_poi_entity_contract.py | `test_create_ddl_patch` | Shift to `ids[-10:-4]` and `ids[-4:-2]`; `ids[-2:] == ["peholmd", "peholpy"]`. | Passes |
| 11 | same | new `test_entity_detail_columns`, `test_entity_detail_patch_cell` | Assertions as in full doc `### Test changes`. | Pass |
| 12 | tests/test_enr_poi_contract.py (needs scope amendment) | `test_info_patch_cell_guards` lines 231–232 | Same position shift as row 10. | Passes |
| 13 | docs/context/01_DATA_MODEL.md | §6 table row N6 | Append the `[SỬA 23/10]` sentence. | Text present |

### Order and stop points
1. **STOP (user/triage decision):** add `tests/test_enr_poi_contract.py` to `scope.files` and record D-PEH-07. Without it, row 12 cannot be edited and `test_info_patch_cell_guards` fails.
2. Rows 1–6 (entity notebook), then row 7 (setup spec), then row 8 (patch cells).
3. Rows 9–12 (tests), row 13 (doc).
4. Run local verification. **STOP for evidence:** all three test files green before review.
5. Runtime (combined runbook, written later):
   - Deploy both tasks' notebooks together.
   - Snapshot `DESCRIBE`, the history version, and counts by source.
   - With the 15P lock free, run `ohpasspy`, then `peholpy`.
   - Trigger `PL_VV_TRANS_SLV_TO_ENR_15P`.
   - **STOP for evidence:** the runtime checks in full doc `## Verification` items 1–7.
6. Rollback is a code-only redeploy. Nulling the stale values or a `RESTORE` is a data write: **STOP for user decision**.

### Tests and verification
- `python -m pytest tests/test_poi_entity_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q`
- Key tests:
  - `test_poi_entity_contract.py`: `test_entity_node_contract`, `test_create_ddl_patch`, `test_entity_detail_columns` (new), `test_entity_detail_patch_cell` (new).
  - `test_initial_ddl_contract.py`: `test_poi_entity_columns_derived`, `test_columns_match_sources`.
  - `test_enr_poi_contract.py`: `test_info_patch_cell_guards`, `test_hours_patch_cell_guards`, `test_hours_patch_cell_constants`.
- `python scripts/vv.py verify 20261023-entity-phone-email-holiday`
- Runtime DEV checks:
  - Schema positions increasing.
  - PK unique.
  - Google `email` and `holiday_exceptions` are all null, and google `phone` equals contact `phone` (`<=>`).
  - Partner `phone`, `email`, and `holiday_exceptions` mismatches are 0, and the hours regression mismatch is 0.
  - Other-source rows: 0.
  - Metrics present, block check = 0, gold run SUCCESS.
  - Rerunning `peholpy` adds no Delta version.

### Read only if needed
- `## Scope gap`: rows 10 and 12, stop 1.
- `## Invariants`, `## Grain and keys`: rows 1–5.
- `## Ordering`, `## Concurrency`, `## Alternatives`: row 8 (why append, no `AFTER`, no lock).
- `### Entity build changes`: rows 1–6.
- `### Setup spec`: row 7.
- `### Patch cells`: row 8 (verbatim code).
- `### Data model doc`: row 13.
- `### Test changes`: rows 9–12.
- `## Rollout`, `## Rollback and forward recovery`, `## Verification`: stops 5 and 6.
- `## Observability`, `## Security`: rows 2, 3, 5.

# Architecture: 20261023-entity-phone-email-holiday

The ledger rows are D-PEH-01..06. Grain, keys, and lineage come from `model-design.md` `## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`. This design answers the open questions in `model-design.md` `## Conflicts and questions` items 2–6. Item 1 (the partner `poi_id` formula against AGENTS.md §7) is a separate, existing issue. This task does not touch it.

## Scope

- `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`: add three output columns. Also update the one-line notebook description in `b1entitymd`.
- `NB_SETUP_INITIAL_DDL` cell `init_tables`: in the `slv_poi_entity_non_enrich` spec, insert three tuples after `opening_hours_text` and before `row_hash`.
- `NB_CREATE_DDL`: append markdown cell `peholmd` and code cell `peholpy` after `ohpasspy`.
- Tests: `tests/test_poi_entity_contract.py`, `tests/test_initial_ddl_contract.py`. **Scope gap:** `tests/test_enr_poi_contract.py` also needs a change. See `## Scope gap`.
- `docs/context/01_DATA_MODEL.md` §6 row N6: one `[SỬA 23/10]` sentence.
- Runtime: the runbook sequence for one combined runbook (`## Rollout`). The runbook author writes `runtime-runbook.md` later.

## Non-goals

- No gold column, no `NB_ENR_POI_INFO` change, no gold recompute of these attributes.
- No change to the `opening_hours_text` formula, the hours edges, or cell `ohpasspy`.
- No extract or registry change, no new input role, no new `required_inputs`, no ctrl edge, no lock change, no `DROP`.
- No warn check for null rates of the new columns. Phone and email are often null at the source, so a warn would be noise. Metrics cover this (`## Observability`).

## Scope gap

Two tests assert `ids[-2:] == ["ohpassmd", "ohpasspy"]` on `NB_CREATE_DDL`:
- `tests/test_poi_entity_contract.py::test_create_ddl_patch` (in scope).
- `tests/test_enr_poi_contract.py::test_info_patch_cell_guards`, lines 231–232. This file is **not** in `scope.files`.

The request requires the new cells to be appended after `ohpasspy`, so both assertions must move by two positions. No design that meets the request keeps `test_enr_poi_contract.py` green unchanged. The only change needed there is the cell-position lines: `ids[-8:-2]` becomes `ids[-10:-4]`, `ids[-2:]` becomes `ids[-4:-2]`, and a new line asserts `ids[-2:] == ["peholmd", "peholpy"]`. No gold assertion changes. Add the file to `scope.files` and record it in the ledger (proposed D-PEH-07) before editing. This is a scope amendment, not missing evidence.

## Invariants

1. Grain stays one row per `poi_id`. `SPEC.pk`, `unique_checks`, and the contact duplicate-`poi_id` `QualityGateError` are byte-identical (D-PEH-05).
2. Output column order is `OUT_COLS = POI_COLS + CONTACT_COLS + ADDRESS_COLS + CATEGORY_COLS + ESTIMATE_COLS + HOURS_COLS + DETAIL_COLS`, with `DETAIL_COLS = ("phone", "email", "holiday_exceptions")`. The setup spec has the same order, followed by `TECH_COLUMNS` (D-PEH-01).
3. All three columns are `STRING` and nullable everywhere: build schema, setup spec, patch.
4. Google: `phone` comes from the same `contact` frame (same filter, same duplicate check, same left join) as `website_url`. `email` and `holiday_exceptions` are `F.lit(None).cast("string")`. They are never untyped nulls, because the lib rejects `void` (D-PEH-02).
5. Partner: `phone` = `svc.phone`, `email` = `svc.email`. `holiday_exceptions` = `get_json_object(amentities, '$.policies.holiday_exceptions')`, projected in the same `vi = (...)` select as `_hours`, kept as a string and not parsed (D-PEH-03).
6. Rows from any source other than google or partner have all three null. A block check enforces this (D-PEH-05).
7. The `opening_hours_text` expressions, the hours block and warn checks, and `ohpasspy` do not change (D-PEH-04).
8. `peholpy` only adds missing nullable columns, in one `ALTER`. It writes no ctrl table, holds no lock, and has no `DROP`, `AFTER`, `ALTER COLUMN`, `MERGE`, or `UPDATE`.
9. The source tables and `SPEC.inputs` are unchanged (D-PEH-06).

## State ownership

- `slv_poi_entity_non_enrich` data: owned by the entity node through `run_node` MERGE. The patch cell writes schema only.
- Entity schema: owned by setup `init_tables` for new environments and by NB_CREATE_DDL patch cells for existing ones. The lib `ensure_target` also appends missing build columns at run time. This is a fallback that ends in the same schema (`## Concurrency`).
- ctrl (`ctrl_mng_pipeline_config`, `ctrl_mng_watermark`): not touched by this task. `ohpasspy` keeps its own ctrl ownership.

## Grain and keys

See `model-design.md` `## Entities and grain` and `## Keys`. Grain, PK, business key, and `poi_id` formulas do not change. The new joins add no rows:
- Google `contact` is unique per `poi_id`, otherwise the QG stops the run before the join.
- Partner columns come from `svc` and the existing `vi` frame. They add no join.

## Ordering

1. **Columns.** On a fresh table, setup creates `… opening_hours_text, phone, email, holiday_exceptions, row_hash, created_at, updated_at, deleted_at`. On DEV, `ohpasspy` appends `opening_hours_text` at the end of the table (it has no `AFTER`, as its test requires). `peholpy` then appends the three columns after it. The result is `… deleted_at, opening_hours_text, phone, email, holiday_exceptions`. They are in order after `opening_hours_text`, but on DEV they are physically after `row_hash`. This is accepted: `schema_diff` compares by name (`init_tables` docstring), the lib MERGE uses names, and moving `opening_hours_text` would mean editing `ohpasspy` (out of scope). The patch checks that the positions of `opening_hours_text < phone < email < holiday_exceptions` are increasing.
2. **Cells.** `peholpy` refuses to run before `ohpasspy`: `opening_hours_text` must already exist as nullable string.
3. **Runtime steps.** See `## Rollout`.

## Transaction and commit boundaries

- `peholpy`: one `ALTER TABLE … ADD COLUMNS (phone STRING, email STRING, holiday_exceptions STRING)` with only the missing columns. That is one Delta metadata commit. No other write.
- Entity node: unchanged. One lib MERGE commit per run, then the lib exit QG and logging, as today.
- Gold `gld_enr_poi_info` runs later in the same 15P DAG, in its own commit. It does not read the new columns.

## Idempotency

- `peholpy` rerun: all three columns are present and valid, so `missing` is empty and nothing is written. It prints the state.
- Entity rerun on the same inputs gives the same `row_hash`, so MERGE updates nothing. `row_hash` is `sha2(to_json(struct(...)))`. `to_json` drops null fields by default, so rows where all three new values are null probably keep their old hash. Rows with a non-null value get one update on the first recompute. Runtime confirms the count; the design does not depend on it.

## Concurrency

- The patch takes no lock (dictseedpy precedent: a pure nullable `ADD COLUMNS`). Every interleaving with a 15P run ends in the same schema:
  - If the new entity notebook runs before `peholpy`, `ensure_target` appends the missing columns in build order. Those are the same names, types, and order, so `peholpy` then does nothing.
  - If an old notebook runs after `peholpy`, `ensure_target` logs a WARN about extra columns. MERGE leaves the new columns as they are.
  - If ALTER and MERGE commit at the same time, Delta optimistic concurrency fails one of them (metadata changed). The failed side is rerun: `peholpy` by the operator, the node by the next 15P trigger or a manual rerun. Neither leaves a partial schema.
- The runbook still runs `peholpy` only while `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P.lock_exec_id IS NULL`. This avoids a noisy conflict. It is not needed for correctness.

## Retry and recovery

- `peholpy` raising "Dừng trước khi ghi" means nothing was written. Fix the reported condition and rerun.
- `peholpy` raising "Sau khi ghi" means the ALTER committed but the result is wrong. Stop and inspect `DESCRIBE`. Do not drop. Forward fix only (`## Rollback and forward recovery`).
- Entity node failure uses the existing lib retry and QG semantics: no MERGE commit on a QG or config failure, so the last good version stays.

## Partial failure

- Patch: a single commit, so there is no partially applied column set. A state where only some new columns exist (manual edits, or an `ensure_target` race) is accepted only if the existing columns are a leading prefix of `NEW_COLS`, in order, after the anchor. Otherwise the cell stops before writing.
- Between `ohpasspy` and `peholpy`, the entity may run once with `opening_hours_text` and without the new columns, if the old notebook is still deployed. That is a valid state.
- Entity succeeds but gold fails: gold retries independently. Gold does not depend on the new columns.

## Observability

- New metrics in the existing `ctx.metrics.update` calls, computed in the existing `agg` passes with no extra Spark action: `google_with_phone`, `partner_with_phone`, `partner_with_email`, `partner_with_holiday`.
- New block check `phone_email_holiday_other_source`. Its violation count shows up in `qg_json` like `opening_hours_other_source`.
- `peholpy` prints the final column state and the list of columns it added. Stop conditions raise with every issue listed together.

## Security

- No secret, no external call. The patch builds SQL from constants only.
- `phone` and `email` of partner business services can be personal contact data. They stay in silver, which already holds them in `slv_pn_business_services` and `slv_3p_poi_contact`. No new exposure layer, and gold does not read them. No masking was requested. If gold ever exposes these columns, that task needs its own data-classification decision.

## Rollout

The single combined runbook (written later by the runbook author) follows this sequence. It needs one shared DEV deploy of both tasks' working tree.

1. Locally, run the tests in `## Verification` and confirm they pass.
2. Deploy `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_ENR_POI_INFO` (hours task, 23/10), `NB_CREATE_DDL`, and `NB_SETUP_INITIAL_DDL` to DEV together.
3. Snapshot before any change:
   - `DESCRIBE TABLE` of the entity.
   - `DESCRIBE HISTORY … LIMIT 1` (record the version).
   - `count(*)` grouped by `source_name`.
   - The `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` lock row.
4. With the flow lock free, run `ohpasspy`. It holds the flow lock itself. Check that its success print appears.
5. With the lock free, run `peholpy`. Check the print: three columns, string, nullable, after `opening_hours_text`.
6. Trigger `PL_VV_TRANS_SLV_TO_ENR_15P`. The entity recomputes, then `gld_enr_poi_info` runs.
7. Run the runtime checks from `## Verification`. Record the outcome in this task. The hours task keeps its own state; this task does not run its gate.

## Rollback and forward recovery

- **Code rollback.** Redeploy the previous entity notebook (the hours-only working tree). `ensure_target` WARNs about the extra columns. MERGE stops writing them, so matched rows keep stale `phone`, `email`, and `holiday_exceptions` values and new rows get nulls. No consumer reads them, so this is harmless. Optional cleanup is `UPDATE … SET phone = NULL, email = NULL, holiday_exceptions = NULL`. That is a data write and needs user approval.
- **Schema.** The columns stay. Nullable additions are safe for every reader. A `DROP COLUMN` would need column mapping and is out of scope.
- **Data.** `RESTORE` to the snapshot version from Rollout step 3 is possible only if no later run must be kept. It needs a user decision and is not the default.
- **Forward recovery.** Fix the notebook and let the next 15P run recompute. The entity is a full recompute plus MERGE, so one good run repairs every value.

## Alternatives

| Option | Trade-off | Decision |
|---|---|---|
| A. Patch with one append `ADD COLUMNS`, plus prefix and position prechecks; no lock (selected) | One commit, no ctrl writes, same as `ohpasspy` and `dictseedpy`. On DEV the physical position is after `row_hash`, which is accepted because all comparisons and writes use names. | Selected |
| B. One `ALTER … ADD COLUMNS (c STRING AFTER prev)` per column (`enrflagpy` style) | Places the columns next to `opening_hours_text`, but on DEV that column is itself after `deleted_at`, so nothing is gained. Three commits create a partial-state window. Would differ in style from the sibling `ohpasspy` on the same table. | Rejected |
| C. No patch; rely on lib `ensure_target` | Simplest, but mixes DDL into the node run with no type or order precheck. The request requires a patch cell. | Rejected; kept only as a converging fallback |
| D. Hold the flow lock in `peholpy` | Prevents a harmless concurrency conflict at the cost of ctrl writes and a state-correctness review. | Rejected |
| E. Put `phone` in `CONTACT_COLS` | Puts `phone` before `house_number`, which breaks D-PEH-01 and the setup-order test. | Rejected; use the new `DETAIL_COLS` |
| F. One block check per column, plus a Google-null block check | More diagnostics, more scans. Google nulls are already literal, statically asserted casts. | Rejected; one combined other-source check |

Missing-column guards (`model-design.md` item 4): **add them**. Add a `ConfigError` for `contact.phone` and for `svc.phone`/`svc.email`, in the same style as the existing `website_url`, `website_urls`, `periods_json`, and `amentities` guards. That gives a clear config error instead of a Spark `AnalysisException`. `amentities` is already guarded.

## Implementation plan

### Entity build changes (`b1entitybuild`)

Constants (after `HOURS_COLS`):

```python
HOURS_COLS = ("opening_hours_text",)
# D-PEH-01: sau opening_hours_text, trước row_hash. Gold không tính lại.
DETAIL_COLS = ("phone", "email", "holiday_exceptions")
OUT_COLS = POI_COLS + CONTACT_COLS + ADDRESS_COLS + CATEGORY_COLS + ESTIMATE_COLS + HOURS_COLS + DETAIL_COLS
```

`_google`:
- Keep the D3/D7 comment. Add `# D-PEH-02: phone cùng khung contact, cùng QG trùng poi_id.`
- `contact = ctx.input("contact").where(F.col("poi_id").isNotNull()).select("poi_id", *CONTACT_COLS, "phone")`. The `dup_contact` block stays unchanged.
- `agg`: add `F.count("phone").alias("with_phone")`. Metrics: add `google_with_phone=agg["with_phone"]`.
- Final select: after `*HOURS_COLS` append `"phone", F.lit(None).cast("string").alias("email"), F.lit(None).cast("string").alias("holiday_exceptions")`.

`_partner`:

```python
    # D-OH-02: giờ partner lấy amentities của bản i18n vi (như _partner_hours cũ của NB_ENR_POI_INFO), không lấy của svc.
    # D-PEH-03: holiday_exceptions cùng dòng vi, cùng cách lấy; giữ chuỗi JSON.
    vi = (_live(ctx.input("i18n")).where(F.col("locale") == "vi")
          .select(F.col("business_service_id").alias("id"),
                  F.get_json_object(F.col("amentities"), "$.policies.operating_hours").alias("_hours"),
                  F.get_json_object(F.col("amentities"), "$.policies.holiday_exceptions").alias("_holiday")))
```

- `agg`: add `F.count("phone").alias("with_phone"), F.count("email").alias("with_email"), F.count("_holiday").alias("with_holiday")`. Metrics: add `partner_with_phone`, `partner_with_email`, `partner_with_holiday`.
- `cols` dict, after `"opening_hours_text"`:

```python
        "phone": F.col("phone"),  # D-PEH-03
        "email": F.col("email"),  # D-PEH-03
        "holiday_exceptions": F.col("_holiday"),  # D-PEH-03: chuỗi JSON, không parse
```

There is no name collision: `vi`, `dp`, `s1`, and `s2` carry no `phone` or `email`. The return still casts to `schema[c].dataType` over `OUT_COLS`.

`build` guards, after the `website_url` guard:

```python
    if "phone" not in ctx.input("contact").columns:
        raise ConfigError("slv_poi_entity_non_enrich: slv_3p_poi_contact thiếu cột phone")
    missing_svc = [c for c in ("phone", "email") if c not in ctx.input("svc").columns]
    if missing_svc:
        raise ConfigError(f"slv_poi_entity_non_enrich: slv_pn_business_services thiếu cột {missing_svc}")
```

`SPEC.block_checks`: append

```python
                  ("phone_email_holiday_other_source", "coalesce(lower(trim(source_name)), '') NOT IN ('google', 'partner') "
                   "AND coalesce(phone, email, holiday_exceptions) IS NOT NULL"),
```

`b1entitymd`: add the line `Đọc thêm phone của slv_3p_poi_contact, phone / email của partner và holiday_exceptions trong amentities của bản i18n vi.`

### Setup spec (`init_tables`)

In the `slv_poi_entity_non_enrich` spec (the second `opening_hours_text`, around JSON line 430; **not** the `gld_enr_poi_info` spec around line 304):

```
        ('opening_hours_text', 'STRING', None),
        ('phone', 'STRING', None),
        ('email', 'STRING', None),
        ('holiday_exceptions', 'STRING', None),
        ('row_hash', 'STRING', None),
```

### Patch cells (`peholmd`, `peholpy`)

`peholmd` is a markdown cell with source `# [THÊM 23/10] 20261023-entity-phone-email-holiday`. `peholpy` is a code cell with metadata `{"microsoft": {"language": "python", "language_group": "synapse_pyspark"}}`, `execution_count: null`, `outputs: []`. Both go after `ohpasspy`. The source of `peholpy`:

```python
# [THÊM 23/10] 20261023-entity-phone-email-holiday
# slv_poi_entity_non_enrich: thêm phone, email, holiday_exceptions STRING cho phép NULL (D-PEH-01), một ALTER (một commit).
# Chạy sau ohpasspy: opening_hours_text phải có, string cho phép NULL. Cột mới nối cuối bảng theo thứ tự NEW_COLS,
# như ohpasspy; schema_diff của NB_SETUP_INITIAL_DDL và MERGE của lib so theo tên.
# Không ghi ctrl, không giữ khoá luồng: cell chỉ thêm cột cho phép NULL. Đúng kiểu -> không đổi; lệch -> dừng trước khi ghi.
# Chạy lại: không đổi gì. Không xoá bảng, không sửa ohpasspy.
ENTITY_FQ = "lh_vv_silver.dbo.slv_poi_entity_non_enrich"
ANCHOR = "opening_hours_text"
NEW_COLS = (("phone", "STRING"), ("email", "STRING"), ("holiday_exceptions", "STRING"))
NAMES = [name for name, _dtype in NEW_COLS]


def _fields():
    # [(tên thường, kiểu, nullable)] theo vị trí trong bảng.
    return [(f.name.lower(), f.dataType.simpleString(), f.nullable) for f in spark.table(ENTITY_FQ).schema.fields]


def _issues(fields, names):
    # ANCHOR rồi names: string cho phép NULL, vị trí tăng dần.
    pos = {name: i for i, (name, _dtype, _nullable) in enumerate(fields)}
    kind = {name: (dtype, nullable) for name, dtype, nullable in fields}
    found = [f"{ENTITY_FQ}.{c} là {kind.get(c)}, cần string cho phép NULL"
             for c in [ANCHOR] + names if kind.get(c) != ("string", True)]
    at = [pos[c] for c in [ANCHOR] + names if c in pos]
    if at != sorted(at):
        found.append(f"vị trí {[ANCHOR] + names} trong {ENTITY_FQ} là {at}, cần tăng dần")
    return found


# Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
if not spark.catalog.tableExists(ENTITY_FQ):
    raise RuntimeError(f"Dừng trước khi ghi: {ENTITY_FQ} chưa có, chạy NB_SETUP_INITIAL_DDL")
before = _fields()
have = {name for name, _dtype, _nullable in before}
present = [c for c in NAMES if c in have]
issues = [] if ANCHOR in have else [f"{ENTITY_FQ} chưa có {ANCHOR}: chạy ohpasspy trước"]
issues += _issues(before, present)
if present != NAMES[:len(present)]:
    issues.append(f"cột đã có {present} không phải phần đầu của {NAMES}: thêm tiếp sẽ sai thứ tự")
if issues:
    raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))
missing = [(c, t) for c, t in NEW_COLS if c not in have]
if missing:
    spark.sql(f"ALTER TABLE {ENTITY_FQ} ADD COLUMNS (" + ", ".join(f"`{c}` {t}" for c, t in missing) + ")")

# Sau khi ghi: đủ ba cột, đúng kiểu, đúng thứ tự sau ANCHOR.
problems = _issues(_fields(), NAMES)
if problems:
    raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
print(f"{ENTITY_FQ}: {NAMES} string NULL sau {ANCHOR}; vừa thêm {[c for c, _t in missing]}")
```

### Data model doc

At the end of the §6 N6 "Quyết định" cell, append: `[SỬA 23/10] phone, email, holiday_exceptions (STRING NULL, sau opening_hours_text): google phone = slv_3p_poi_contact.phone (cùng left join poi_id với website_url), email và holiday_exceptions NULL; partner phone, email của slv_pn_business_services, holiday_exceptions = $.policies.holiday_exceptions trong amentities của i18n vi (giữ chuỗi JSON); nguồn khác NULL. Gold không tính lại.`

### Test changes

`tests/test_initial_ddl_contract.py::test_poi_entity_columns_derived`:
- Also `exec(initial["init_cfg_partner"], env)` and build `svc` from `flatten_table_configs(env["TABLE_CONFIGS"], "lh_vv_bronze.dbo", "partner_raw_data")`, keeping rows with `trg_tbl == "slv_pn_business_services"` and `is_active`.
- Assert `_assign(build, "DETAIL_COLS") == ("phone", "email", "holiday_exceptions")`.
- Assert `contact["phone"].lower() == svc["phone"].lower() == svc["email"].lower() == "string"`.
- After the `opening_hours_text` line, add `expected += [("phone", contact["phone"]), ("email", svc["email"]), ("holiday_exceptions", "string")]`.

`tests/test_poi_entity_contract.py`:
- `test_create_ddl_patch`: change to `ids[-10:-4]`, `ids[-4:-2] == ["ohpassmd", "ohpasspy"]`, and `ids[-2:] == ["peholmd", "peholpy"]`.
- New `test_entity_detail_columns`. Use AST segments of `_google` and `_partner` and assert:
  - `_google` contains `.select("poi_id", *CONTACT_COLS, "phone")`, `F.lit(None).cast("string").alias("email")`, `F.lit(None).cast("string").alias("holiday_exceptions")`, and `"dup_contact"`.
  - `_google` does not contain `$.policies.holiday_exceptions`.
  - The `vi = (` segment contains both `$.policies.operating_hours` and `$.policies.holiday_exceptions").alias("_holiday")`.
  - `_partner` contains `"phone": F.col("phone")`, `"email": F.col("email")`, and `"holiday_exceptions": F.col("_holiday")`.
  - `_partner.count('F.col("_holiday")') == 1`.
  - `build` contains `"+ HOURS_COLS + DETAIL_COLS"` and `phone_email_holiday_other_source`.
  - `opening_hours_other_source` and `partner_opening_hours_null` are still present.
- New `test_entity_detail_patch_cell`:
  - With comment lines stripped, the code contains none of `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE`, `columnMapping`, ` AFTER `, `ALTER COLUMN`, `ctrl_mng`, `MERGE`, `UPDATE`, `INSERT`, `CREATE TABLE`, `lock_exec_id`.
  - `_assign(raw, "NEW_COLS") == tuple((n, "STRING") for n in DETAIL_COLS)`.
  - `_assign(raw, "ANCHOR") == HOURS_COLS[-1]`.
  - `raw.count("ALTER TABLE") == 1`.
  - The positions of `Dừng trước khi ghi` < `ALTER TABLE` < `Sau khi ghi` are increasing.
  - The markdown text equals `# [THÊM 23/10] 20261023-entity-phone-email-holiday` and the code starts with the same line.
  - `NEW_COLS` names equal the three setup spec names that follow `opening_hours_text` (via `from test_initial_ddl_contract import _specs`, the same import pattern `test_enr_poi_contract` uses).

`tests/test_enr_poi_contract.py::test_info_patch_cell_guards` (after the scope amendment): apply the same position shift as `test_create_ddl_patch`.

## Verification

Local:
- `python -m pytest tests/test_poi_entity_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q`
- `python scripts/vv.py verify 20261023-entity-phone-email-holiday`
- Confirm that `NB_CREATE_DDL.ipynb` and `NB_SLV_POI_ENTITY_NON_ENRICH.ipynb` load as JSON (the tests load them).

Runtime (DEV, after Rollout step 6):
1. `DESCRIBE` the entity. The three columns are string and nullable, and the positions `opening_hours_text < phone < email < holiday_exceptions` are increasing.
2. Row count per `source_name` equals the snapshot, plus or minus normal source drift. `count(*) = count(DISTINCT poi_id)`.
3. Google: `count_if(email IS NOT NULL OR holiday_exceptions IS NOT NULL) = 0`. Mismatch count against `slv_3p_poi_contact` joined on `poi_id`, using `NOT (e.phone <=> c.phone)`, is 0.
4. Partner:
   - Phone and email mismatches against live `slv_pn_business_services` on `source_id = id` are 0.
   - `holiday_exceptions` mismatches against `get_json_object(amentities, '$.policies.holiday_exceptions')` on live `vi` i18n rows are 0.
   - `opening_hours_text` mismatches against `$.policies.operating_hours` are 0, the hours regression check.
5. Other sources: zero rows with any non-null new column.
6. `ctrl_log`: the entity run is SUCCESS, metrics include `google_with_phone`, `partner_with_phone`, `partner_with_email`, `partner_with_holiday`, and block check `phone_email_holiday_other_source` = 0. The `gld_enr_poi_info` run is SUCCESS and its schema is unchanged.
7. Rerun `peholpy`: it prints `vừa thêm []` and `DESCRIBE HISTORY` shows no new version.
