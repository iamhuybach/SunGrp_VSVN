RESULT: PASS

## Main brief

### Decision
Compute `opening_hours_text` in `NB_SLV_POI_ENTITY_NON_ENRICH` using the old gold when-chain: Google `periods_json` via left join on `poi_id`, partner `$.policies.operating_hours` from the i18n `vi` `amentities`, otherwise NULL. Gold `NB_ENR_POI_INFO` passes it through and blocks on a null-safe mismatch (`opening_hours_text_mismatch`).

The ctrl change is one atomic MERGE in a new `NB_CREATE_DDL` patch cell `ohpasspy`: add the RECOMPUTE edge `slv_3p_poi_opening_hours -> slv_poi_entity_non_enrich` and set `slv_3p_poi_opening_hours -> gld_enr_poi_info` to `is_active` 0, keeping the row and its watermark. The i18n gold edge stays. The orchestrator is unchanged, because the DAG comes from the edges.

### Invariants Main must preserve
- The gold select is `F.col("e.opening_hours_text").alias("opening_hours_text")` at its current position, with `# COL-047` kept. The `INFO` order test passes unchanged.
- Entity `OUT_COLS` ends with `HOURS_COLS = ("opening_hours_text",)`. The setup spec lists it after `canonical_candidate` and before `row_hash`.
- Partner hours come from the i18n `vi` frame under the alias `_hours`, never from `svc.amentities` (D-OH-02).
- No cast is added (D-OH-04). No duplicate-hours gate is added (D-OH-03); the lib's PK QG covers it.
- Entity `required_inputs` is unchanged. `hours` is an optional input.
- Every entity `spec.inputs` role has an active edge and vice versa; the same holds for gold. The ctrl switch is one MERGE.
- `ohpasspy` contains no DROP, DELETE, TRUNCATE, REPLACE, RESTORE, AFTER, `SET is_active = 1`, or `CREATE TABLE`. It holds the `wm_flow__` lock, checks everything before writing, and a re-run changes nothing.
- Gold keeps the `i18n` input, `_vi_i18n`, and `_i18n_keys`. `_partner_hours`, the `hours` role, and the `oh`/`ph` joins are removed.
- Both hours checks move to the entity SPEC. Gold keeps only the mismatch block.
- Do not edit `NB_00_ORCHES_SLV_TO_ENR_15P`, the pipeline JSON, or `docs/context/gld_enr_poi_info_review.md`.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb | `b1entitybuild` constants | add `HOURS_COLS`, append it to `OUT_COLS` | `OUT_COLS[-1] == "opening_hours_text"` |
| 2 | same | `b1entitybuild` `_google` | hours left join, `with_hours` metric, `*HOURS_COLS` in select (doc E1) | the Google frame has the column |
| 3 | same | `b1entitybuild` `_partner` | `vi` select adds `_hours`; `cols["opening_hours_text"]`; `partner_with_hours` (doc E1) | the partner frame has the column |
| 4 | same | `b1entitybuild` `build` + `SPEC` | `periods_json`/`amentities` ConfigError guards; `"hours"` input; block `opening_hours_other_source`; warn `partner_opening_hours_null` | both checks are in SPEC |
| 5 | same | `b1entitymd` | mention `slv_3p_poi_opening_hours` and i18n `amentities` | text updated |
| 6 | notebooks/NB_ENR_POI_INFO.ipynb | `36415d3b` header + `REQUIRED_COLS` | `[SỬA 23/10]` line; entity adds `opening_hours_text`; i18n becomes `("business_service_id","locale")` | pure block parses |
| 7 | same | `36415d3b` `_partner_hours`, `build`, `SPEC` | delete `_partner_hours`; remove `hours` from the loop, joins, and inputs; passthrough select; persisted `out` plus mismatch block (doc E2); drop the two hours checks | the grep tokens in test row 12 pass |
| 8 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` entity spec | insert `('opening_hours_text', 'STRING', None)` before `row_hash` | derived-columns test passes |
| 9 | same | `init_seed_ctrl` | `[SỬA 23/10]` comment; gold hours row `is_active` 0; new entity edge row after the contact edge (doc E3) | the seed has 53 rows |
| 10 | notebooks/NB_CREATE_DDL.ipynb | append after `enrflagpy` | markdown `ohpassmd` + code `ohpasspy`, verbatim from doc E4 | `ids[-2:] == ["ohpassmd","ohpasspy"]` |
| 11 | docs/context/01_DATA_MODEL.md | §6 row N6 | add the input and the `[SỬA 23/10]` sentence (doc E5) | row updated |
| 12 | tests/test_enr_poi_contract.py | `INFO_INPUTS`, `test_info_spec_inputs_match_active_edges`, `test_info_removal_keys`, `test_info_patch_cell_guards`; new `test_info_hours_passthrough`, `test_hours_patch_cell_constants`, `test_hours_patch_cell_guards` | per doc E6 | the file passes |
| 13 | tests/test_poi_entity_contract.py | `test_entity_node_contract`, `test_create_ddl_patch` | per doc E6 | passes |
| 14 | tests/test_initial_ddl_contract.py | `test_poi_entity_columns_derived`, `test_pipeline_config_rows_match_sources` | per doc E6 (registry `periods_json` is string; count 53) | passes |

### Order and stop points
1. Rows 1–5, then 13. Run the entity tests.
2. Rows 6–7, then 12 (gold parts).
3. Rows 8–10, then 12 (patch tests) and 14.
4. Row 11. Run the full local suite. **STOP (evidence):** report the pytest output.
5. **STOP (user decision):** ask whether to pause the `PL_VV_TRANS_SLV_TO_ENR_15P` trigger in DEV, or whether to run steps 6–7 within one 15-minute gap. Record `V0` (the latest `gld_enr_poi_info` version).
6. Sync the notebooks, run `ohpasspy`, then the orchestrator with `p_mode=RUN`. **STOP (evidence):** probes R1–R5.
7. Run the orchestrator again and re-run `ohpasspy`. **STOP (evidence):** R6. Resume the trigger. Watch R7 on later ticks.
8. On any failure, follow `## Partial failure` and `## Rollback and forward recovery`. Do not improvise a ctrl edit.

### Tests and verification
- `python -m pytest tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest -q`
- Changed or new tests:
  - `test_info_spec_inputs_match_active_edges`, `test_info_removal_keys`, `test_info_patch_cell_guards`, `test_info_hours_passthrough`, `test_hours_patch_cell_constants`, `test_hours_patch_cell_guards`
  - `test_entity_node_contract`, `test_create_ddl_patch`
  - `test_poi_entity_columns_derived`, `test_pipeline_config_rows_match_sources`
  - `test_enr_initial_edge_state` follows through the new `INFO_INPUTS`
- Runtime R1–R7 under `## Verification`. R3 (gold equals silver) and R4 (gold unchanged against `V0`) must both be 0.

### Read only if needed
- `## Implementation plan` / `### E1 Entity build` → rows 1–5
- `### E2 Gold cell` → rows 6–7
- `### E3 Setup` → rows 8–9
- `### E4 Patch cells` → row 10 (verbatim source)
- `### E5 Doc` → row 11
- `### E6 Tests` → rows 12–14
- `## Alternatives`, `## Transaction and commit boundaries`, `## Idempotency` → row 10 design (one MERGE; deactivate, don't delete)
- `## Grain and keys`, `## Invariants` → rows 2–3, 7
- `## Rollout (DEV)`, `## Partial failure`, `## Rollback and forward recovery`, `## Verification` → steps 5–8

# Architecture: 20261023-entity-opening-hours-passthrough

Inputs: `model-design.md` (`## Keys`, `## Columns`, `### DDL placement of the silver column`, `### Quality checks (Locked model 7)`, `## Lineage`) and ledger D-OH-01..D-OH-05. The ledger answers model-design questions 1–5. Questions 6–7 are observations and stay unchanged. No proposal, problem analysis, or requirements analysis exists.

Facts read from source and relied on:
- `_resolve_node` (`NB_LIB_TRANSFORM_SLV_GLD`) fails with `ConfigError` before any read or write if `spec.inputs` and the node's active edges differ in either direction. Spec and ctrl edges must therefore switch together.
- `load_config_rows` reads only `is_active = 1` edges. The DAG comes from those edges. `orchestrate` has no hard-coded order, so `NB_00_ORCHES_SLV_TO_ENR_15P` needs no change.
- `ctx.changed()` aligns the old version to the current schema with `_align_snapshot`: a new column becomes NULL in the old version. An entity row whose `opening_hours_text` changes therefore shows up in gold's `ctx.changed("entity")`.
- The RECOMPUTE MERGE updates rows by `row_hash`. `ensure_target` adds missing columns by name. The QG blocks duplicate PKs.
- `NB_SETUP_INITIAL_DDL` seeding is insert-only (`WHEN NOT MATCHED`).

## Scope

- `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild` computes `opening_hours_text` with the moved when-chain (Google `periods_json`, partner i18n `$.policies.operating_hours`, otherwise NULL). It gets a new input role `hours`, the two hours checks, and two metrics. Markdown `b1entitymd` gets one line.
- `NB_ENR_POI_INFO` cell `36415d3b` passes `e.opening_hours_text` through. It drops the `hours` role, the `oh` and `ph` joins, and `_partner_hours`. It removes the two hours checks and adds the D-OH-05 mismatch block in `build`.
- `NB_SETUP_INITIAL_DDL`: in `init_tables`, the entity spec gets the column. In `init_seed_ctrl`, add the new entity edge and set the gold hours edge to `is_active` 0.
- `NB_CREATE_DDL`: add markdown `ohpassmd` and the self-contained patch cell `ohpasspy` at the end.
- `docs/context/01_DATA_MODEL.md` §6 row N6: one input and one sentence.
- Three contract test files.

## Non-goals

- No gold column, rename, type change, or position change. `INFO_COLS` in `enrflagpy` and the gold `TABLE_SPECS` stay as they are.
- No orchestrator, pipeline JSON, or manifest change. `NB_00_ORCHES_SLV_TO_ENR_15P` is not edited.
- `slv_pn_business_service_i18ns` stays a gold input, because `_i18n_keys` still reads it.
- No new transform. No cast (D-OH-04). No duplicate-`poi_id` gate on hours (D-OH-03).
- No deletion of ctrl or watermark rows. No `DROP`.

## Invariants

1. I1: for every live entity `poi_id`, the latest `gld_enr_poi_info.opening_hours_text` is null-safe equal to `slv_poi_entity_non_enrich.opening_hours_text` (D-OH-05).
2. I2: for each `poi_id`, the silver value equals what the old gold cell 3 formula produced on the same input versions:
   - Google: `periods_json` from a left join on `poi_id`.
   - Partner: live i18n `vi` row, `get_json_object(amentities, '$.policies.operating_hours')`.
   - Any other source: NULL.
3. I3: entity grain stays one row per `poi_id`. Gold grain and PK are unchanged.
4. I4: the gold column name, `STRING` type, and position match `enrflagpy` `INFO_COLS`.
5. I5: the silver column is `STRING` and nullable. Setup puts it after `canonical_candidate` and before `row_hash`. On an existing table, `ALTER` appends it at the end (D-OH-01). Code matches it by name.
6. I6: at every moment a flow run can see, each node's active edges equal its `spec.inputs`.
7. I7: in the 15P DAG, gold runs after the entity node. A change to `slv_3p_poi_opening_hours` makes the entity edge dirty.
8. I8: the patch cell is idempotent. A re-run changes nothing.

## State ownership

| State | Owner | Change |
|---|---|---|
| `slv_poi_entity_non_enrich.opening_hours_text` | entity node (MERGE) | new. Created by the patch `ALTER` or by `ensure_target` |
| `gld_enr_poi_info.opening_hours_text` | gold node (APPEND) | value now comes only from the entity |
| ctrl edge `slv_3p_poi_opening_hours -> slv_poi_entity_non_enrich` | `ohpasspy` (DEV), `init_seed_ctrl` (fresh) | new, active |
| ctrl edge `slv_3p_poi_opening_hours -> gld_enr_poi_info` | `ohpasspy` / seed | `is_active` 0. The row is kept |
| watermark `wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours` | lib (`sql_merge_edge_wm` inserts it on the first SUCCESS) | new. The cell does not write it |
| watermark `wm_e__gld_enr_poi_info__slv_3p_poi_opening_hours` | lib | frozen and kept for rollback. `load_edge_wm` reads only active edges, so it is inert |

## Grain and keys

Grain and keys are as in model-design.md `## Keys`. The Google join is `poi_id = poi_id`. The partner value comes from the `vi` frame that `_partner` already inner-joins on `id = business_service_id`, so the row count does not change. A duplicate `poi_id` in `slv_3p_poi_opening_hours` is caught by the lib's PK-duplicate QG on the entity (D-OH-03, no extra gate).

Blast radius change: before, such a duplicate failed only gold info. Now it fails the entity, so amenity and gold info are both SKIPPED. This is accepted because the registry keys that table on `poi_id`.

## Ordering

- DAG: the entity reads only external or FL_00 tables (level 0), amenity is level 1, gold is level 2. All of this comes from the existing edges `entity -> amenity` and `entity -> gold`. The orchestrator is unchanged.
- In one exec, the entity reads hours at the pinned version, MERGEs, and commits. Gold then reads the entity at its current version. Gold no longer reads hours at all.
- Inside `ohpasspy`: take the lock, run every pre-check, `ALTER` (only if the column is missing), run one ctrl `MERGE`, run the post-checks, release the lock.

## Transaction and commit boundaries

- `ALTER TABLE ... ADD COLUMNS` is one Delta commit on the entity. It is harmless to old code: the old entity notebook's `ensure_target` only WARNs, and old gold does not read the column.
- The ctrl switch is **one MERGE, one commit** on `ctrl_mng_pipeline_config`: insert the entity edge and deactivate the gold edge together. The ctrl table is never left half-switched.
- Node writes are unchanged: entity MERGE, then gold APPEND with its marker.

## Idempotency

- Patch cell re-run:
  - The column already exists, so no `ALTER`.
  - The MERGE `ON` row matches, and there is no `WHEN MATCHED` action for `ON`.
  - The `OFF` row is already 0, so its `t.is_active = 1` guard fails. If the `OFF` row is absent, `WHEN NOT MATCHED` requires `action = 'ON'`, so nothing is inserted.
- The entity re-run with the same inputs gives no diff and no commit. Gold re-derives the same changed keys from its unadvanced watermark.
- A second orchestrator run with no source change ends with entity `NO_DATA` and gold `NO_DATA`.

## Concurrency

- `ohpasspy` holds `wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P` with the same lease pattern as `enrflagpy` (35 min). While it holds the lock, `orchestrate` and standalone `run_node` return `SKIPPED_CONCURRENT`.
- FL_00 may write `slv_3p_poi_opening_hours` at any time. The entity reads the pinned version, and the next tick sees the edge as dirty.
- Code deployment (git sync) is not covered by the lock. See Rollout.

## Retry and recovery

- A node failure writes nothing, and its edges do not advance. The next 15-minute tick retries. If the entity fails, gold is SKIPPED, so gold stays consistent with the last good entity version.
- A patch-cell failure releases the lock with `FAILED`. Re-run the cell after fixing the reported issue.

## Partial failure

| Point | State | Effect | Recovery |
|---|---|---|---|
| Notebooks synced, cell not yet run | entity spec has `hours` but no edge; gold has an active hours edge but no role | both nodes fail with `ConfigError` in `_resolve_node` before any write | run `ohpasspy` |
| Cell ran, notebooks not synced | mirror image | same | sync the notebooks |
| `ALTER` done, MERGE failed | column exists, edges unchanged | old code runs as before; new code fails as in row 1 | re-run the cell |
| Entity SUCCESS, gold mismatch block | entity has the new values, gold not appended | gold FAILED, its entity edge does not advance | investigate. The next run retries the same keys |

## Observability

- Entity `qg_json`:
  - block `opening_hours_other_source`
  - warn `partner_opening_hours_null` (moved from gold)
  - metrics `google_with_hours` and `partner_with_hours`
- Gold:
  - `ctx.metrics["opening_hours_text_mismatch"]`
  - a non-zero value raises `QualityGateError` naming `opening_hours_text_mismatch`
- Consumers that read `partner_opening_hours_null` from the gold node's `qg_json` must switch to the entity row in `ctrl_log_table_run`. No such consumer was found in scope.
- `ohpasspy` prints the column state and the active edge sets.

## Security

Not applicable: no new credentials, endpoints, or user input. The SQL text is built only from cell constants and from `nb_name`/`priority` values read from ctrl. The lib already validates `nb_name` as an identifier.

## Rollout (DEV)

1. Merge the code. Pause the `PL_VV_TRANS_SLV_TO_ENR_15P` trigger, or confirm no run is in flight. If the trigger cannot be paused, finish steps 2–3 inside one 15-minute gap; a tick that lands in between fails safely (see Partial failure).
2. Record the baseline: the current version of `gld_enr_poi_info` (`DESCRIBE HISTORY`, latest version `V0`).
3. Sync the notebooks to the workspace. Run `NB_CREATE_DDL` cell `ohpasspy` and expect the success print.
4. Run `NB_00_ORCHES_SLV_TO_ENR_15P` with `p_mode = RUN`. Expected:
   - The entity is dirty with `NEW_EDGE` on hours. The MERGE updates every row (new `row_hash`).
   - Amenity runs and finds no diff.
   - Gold appends the keys whose `opening_hours_text` is non-NULL. This is a one-time volume.
5. Run the runtime probes (Verification), then a second orchestrator run (expect `NO_DATA`). Resume the trigger.

## Rollback and forward recovery

- Forward recovery is preferred. A failure caused by data, such as a duplicate hours `poi_id`, is fixed at the source while gold stays at its last consistent state.
- Rollback:
  1. Pause the trigger.
  2. Revert the code commit and sync.
  3. Run this under a manual lock or a paused trigger. It is one statement, so one commit:

```sql
MERGE INTO lh_vv_ctrl.dbo.ctrl_mng_pipeline_config AS t
USING (SELECT 'lh_vv_silver.dbo' AS trg_schema, 'slv_poi_entity_non_enrich' AS trg_tbl, 0 AS flag
       UNION ALL SELECT 'lh_vv_gold.enr', 'gld_enr_poi_info', 1) AS s
ON t.pl_name = 'PL_VV_TRANS_SLV_TO_ENR_15P' AND t.src_schema = 'lh_vv_silver.dbo'
   AND t.src_tbl = 'slv_3p_poi_opening_hours' AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
WHEN MATCHED THEN UPDATE SET t.is_active = s.flag
```

- After the rollback, the reactivated gold hours edge has a stale watermark. Its status becomes `DATA_CHANGED` or `HISTORY_GAP`, and `_role_keys` returns a superset of keys, so the result stays correct.
- The entity column stays (nullable). The old notebook leaves it stale and does not read it. No data repair is needed: the probe on `V0` proves the gold values did not change.

## Alternatives

| Option | Verdict | Reason |
|---|---|---|
| Keep the gold `hours` role as a redundant changed-key trigger | rejected | No gold column reads it (acceptance 8). An entity `row_hash` change already covers it, deleted hours rows included (they become NULL, so the row changes). |
| Delete the gold edge and watermark rows (as `mvpoipy` did) | rejected | Deactivating (the `enrinfopy` precedent) makes rollback a flag flip. The stale watermark is inert. |
| A separate INSERT and UPDATE on ctrl | rejected | Two commits leave a window where ctrl is half-switched. One MERGE is atomic. |
| Mismatch check as a `block_checks` SQL condition | impossible | A row-level check needs the silver value in the output, which would add a gold column. |
| Mismatch check only as a runtime SQL probe | insufficient | D-OH-05 requires a gold block. The probe is kept as well, for persisted state. |
| Mismatch check in `build` on persisted output (selected) | selected | It reuses the cache the lib consumes next. The extra cost is one narrow join and count. |
| `ALTER ... AFTER canonical_candidate` | rejected | D-OH-01 fixes plain `ADD COLUMNS`. Name matching makes the order irrelevant. |
| Make `hours` a required input of the entity | rejected | Gold did not require it, and an empty table must keep NULL behavior. |

## Implementation plan

### E1 Entity build (`b1entitybuild`)

- Constants: `HOURS_COLS = ("opening_hours_text",)` and `OUT_COLS = ... + ESTIMATE_COLS + HOURS_COLS`.
- `_google`:

```python
    # D-OH-03: giờ google left join slv_3p_poi_opening_hours theo poi_id như cell 3 cũ của NB_ENR_POI_INFO; poi_id trùng thì QG khoá chặn.
    hours = ctx.input("hours").select("poi_id", F.col("periods_json").alias("opening_hours_text"))
    out = (poi.join(by_primary, "poi_id", "left").join(by_types, "poi_id", "left").join(addr, "poi_id", "left")
           .join(contact, "poi_id", "left").join(hours, "poi_id", "left"))
```

  - Add `F.count("opening_hours_text").alias("with_hours")` to `agg`, and `google_with_hours=agg["with_hours"]` to the metrics.
  - Append `*HOURS_COLS` after `*[pick(c, F.lit(None)) for c in ESTIMATE_COLS]` in the final select.
- `_partner`:

```python
    # D-OH-02: giờ partner lấy amentities của bản i18n vi (như _partner_hours cũ của NB_ENR_POI_INFO), không lấy của svc.
    vi = (_live(ctx.input("i18n")).where(F.col("locale") == "vi")
          .select(F.col("business_service_id").alias("id"),
                  F.get_json_object(F.col("amentities"), "$.policies.operating_hours").alias("_hours")))
```

  - Add `F.count("_hours").alias("with_hours")` to `agg`, and `partner_with_hours=agg["with_hours"]` to the metrics.
  - Add `"opening_hours_text": F.col("_hours"),  # D-OH-02` to `cols`.
  - The existing final cast uses `google.schema`, which gives `string` (D-OH-04).
- `build`: add these after the `website_urls` guard:

```python
    if "periods_json" not in ctx.input("hours").columns:
        raise ConfigError("slv_poi_entity_non_enrich: slv_3p_poi_opening_hours thiếu cột periods_json")
    if "amentities" not in ctx.input("i18n").columns:
        raise ConfigError("slv_poi_entity_non_enrich: slv_pn_business_service_i18ns thiếu cột amentities")
```

- `SPEC`:
  - Add `"hours": "slv_3p_poi_opening_hours"` to `inputs`. `required_inputs` is unchanged.
  - Add `block_checks=(("opening_hours_other_source", "coalesce(lower(trim(source_name)), '') NOT IN ('google', 'partner') " "AND opening_hours_text IS NOT NULL"),)`.
  - Append `("partner_opening_hours_null", "lower(trim(source_name)) = 'partner' AND opening_hours_text IS NULL")` to `warn_checks`.
- `b1entitymd`: also mention `slv_3p_poi_opening_hours` and the i18n `amentities`.

### E2 Gold cell (`36415d3b`)

- Header line: `# [SỬA 23/10] 20261023-entity-opening-hours-passthrough: opening_hours_text lấy nguyên từ slv_poi_entity_non_enrich (D-OH-05). Bỏ slv_3p_poi_opening_hours, _partner_hours.`
- `REQUIRED_COLS`:
  - Add `"opening_hours_text"` to `"entity"`.
  - Set `"i18n"` to `("business_service_id", "locale")`, the only columns `_i18n_keys` reads.
- Delete `def _partner_hours`. Keep `_vi_i18n` and `_i18n_keys`.
- `build`:
  - The role loop becomes `for role in ("rating", "price", "review", "amenity"):`.
  - Remove `oh = ...`, `ph = ...`, and their two `.join`s.
  - The select line is `F.col("e.opening_hours_text").alias("opening_hours_text"),  # COL-047 — D-OH-05`.
  - Change `return base.select(` to `out = base.select(` with the same body, then add the tail below.
- `SPEC`:
  - Remove `"hours"` from `inputs`.
  - Remove `opening_hours_other_source` from `block_checks` and `partner_opening_hours_null` from `warn_checks`.

The tail that replaces the `return`:

```python
    out = out.persist(StorageLevel.MEMORY_AND_DISK)
    ctx.cached.append(out)
    # D-OH-05: khác giá trị silver cùng poi_id, kể cả một bên NULL -> chặn.
    mismatch = (out.select("poi_id", "opening_hours_text").alias("g")
                .join(spine.select("poi_id", "opening_hours_text").alias("s"), "poi_id", "left")
                .where(~F.col("g.opening_hours_text").eqNullSafe(F.col("s.opening_hours_text"))).count())
    ctx.metrics.update(opening_hours_text_mismatch=mismatch)
    if mismatch:
        raise QualityGateError(f"gld_enr_poi_info: opening_hours_text_mismatch {mismatch} dòng khác slv_poi_entity_non_enrich")
    return out
```

### E3 Setup (`NB_SETUP_INITIAL_DDL`)

- `init_tables`: in the `slv_poi_entity_non_enrich` spec, insert `('opening_hours_text', 'STRING', None),` between `canonical_candidate` and `row_hash`.
- `init_seed_ctrl`:
  - Add the comment `# [SỬA 23/10] 20261023-entity-opening-hours-passthrough: tắt cạnh giờ -> info; thêm cạnh giờ -> entity.`
  - Change the `slv_3p_poi_opening_hours -> gld_enr_poi_info` row's `is_active` from `1` to `0`.
  - After the `slv_3p_poi_contact -> slv_poi_entity_non_enrich` row, add `(_ENR, _S, 'slv_3p_poi_opening_hours', _S, 'slv_poi_entity_non_enrich', 1, 1, 'RECOMPUTE', None, None, None),`.

### E4 Patch cells (`NB_CREATE_DDL`, appended after `enrflagpy`)

- Markdown cell, id `ohpassmd`, source `# [THÊM 23/10] 20261023-entity-opening-hours-passthrough\n`.
- Code cell, id `ohpasspy`, with the same metadata as `enrflagpy` (`microsoft.language = python`, `language_group = synapse_pyspark`). Source:

```python
# [THÊM 23/10] 20261023-entity-opening-hours-passthrough
# 1. slv_poi_entity_non_enrich: thêm opening_hours_text STRING cho phép NULL, ở cuối bảng (D-OH-01). Đúng kiểu -> không đổi; lệch -> dừng.
# 2. Một MERGE (một commit) trên ctrl_mng_pipeline_config: thêm cạnh RECOMPUTE slv_3p_poi_opening_hours -> entity,
#    tắt cạnh slv_3p_poi_opening_hours -> gld_enr_poi_info (is_active = 0; giữ dòng và watermark để rollback).
# Chạy khi workspace đã có NB_SLV_POI_ENTITY_NON_ENRICH, NB_ENR_POI_INFO bản 23/10: spec.inputs phải khớp cạnh active.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_ENR_15P suốt cell. Chạy lại: không đổi gì.
# Sau cell này không chạy lại enrddlpy, enrinfopy, mvpoipy.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_ENR_15P"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.enr"
ENTITY, INFO = "slv_poi_entity_non_enrich", "gld_enr_poi_info"
ENTITY_FQ = f"{SLV}.{ENTITY}"
HOURS_FQ = f"{SLV}.slv_3p_poi_opening_hours"
LEASE_MINUTES = 35  # bằng p_lock_timeout_min của NB_00_ORCHES_SLV_TO_ENR_15P
NEW_COL = ("opening_hours_text", "STRING")
ENTITY_SRC = (
    "slv_3p_poi", "slv_3p_poi_address", "ref_dictionary_place_type", "slv_pn_business_services",
    "slv_pn_business_service_i18ns", "slv_3p_poi_contact",
)
INFO_KEEP = (
    "slv_poi_entity_non_enrich", "slv_poi_amenity", "slv_3p_poi_rating", "slv_3p_poi_price", "slv_3p_poi_review",
    "slv_pn_business_service_i18ns", "slv_enr_poi_info_multi_lang", "slv_enr_poi_destination",
)
EDGES_ON = [("slv_3p_poi_opening_hours", "lh_vv_silver.dbo", "slv_poi_entity_non_enrich", "RECOMPUTE")]
EDGES_OFF = [("slv_3p_poi_opening_hours", "lh_vv_gold.enr", "gld_enr_poi_info")]
NEW_WM = "wm_e__slv_poi_entity_non_enrich__slv_3p_poi_opening_hours"
LOCK = "ohpass-" + uuid.uuid4().hex


def _rows(trg_schema, trg):
    # (src_tbl, is_active) -> số dòng của node trên PL.
    return {(row["src_tbl"], row["is_active"]): row["n"] for row in spark.sql(f"""
    SELECT src_tbl, is_active, count(*) AS n FROM {CFG}
    WHERE pl_name = '{PL}' AND src_schema = '{SLV}' AND trg_schema = '{trg_schema}' AND trg_tbl = '{trg}'
    GROUP BY src_tbl, is_active
    """).collect()}


def _active(trg_schema, trg):
    return {src: n for (src, flag), n in _rows(trg_schema, trg).items() if flag == 1}


def _column():
    for field in spark.table(ENTITY_FQ).schema.fields:
        if field.name.lower() == NEW_COL[0]:
            return field.dataType.simpleString(), field.nullable
    return None


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
    if "nb_name" not in {f.name.lower() for f in spark.table(CFG).schema.fields}:
        raise RuntimeError(f"{CFG} chưa có cột nb_name: chạy enrddlpy trước")

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    for fq in (ENTITY_FQ, HOURS_FQ):
        if not spark.catalog.tableExists(fq):
            issues.append(f"{fq} chưa có")
    if not issues:
        hours_types = {f.name.lower(): f.dataType.simpleString() for f in spark.table(HOURS_FQ).schema.fields}
        if hours_types.get("periods_json") != "string":
            issues.append(f"{HOURS_FQ}.periods_json là {hours_types.get('periods_json')}, cần string (D-OH-04)")
        col = _column()
        if col not in (None, ("string", True)):
            issues.append(f"{ENTITY_FQ}.{NEW_COL[0]} là {col}, cần string cho phép NULL")
        src, schema, trg, mode = EDGES_ON[0]
        on_rows = {flag: n for (name, flag), n in _rows(SLV, ENTITY).items() if name == src}
        if on_rows not in ({}, {1: 1}):
            issues.append(f"cạnh {src} -> {trg} có {on_rows}: cell không tự bật cạnh")
        others = {name: n for name, n in _active(SLV, ENTITY).items() if name != src}
        if others != {name: 1 for name in ENTITY_SRC}:
            issues.append(f"cạnh active của {ENTITY} là {others}, cần {sorted(ENTITY_SRC)}")
        template = spark.sql(f"""
        SELECT DISTINCT priority, upper(trim(load_mode)) AS load_mode, nb_name FROM {CFG}
        WHERE pl_name = '{PL}' AND src_schema = '{SLV}' AND trg_schema = '{SLV}' AND trg_tbl = '{ENTITY}' AND is_active = 1
        """).collect()
        if len(template) != 1 or template[0]["load_mode"] != mode or template[0]["priority"] is None:
            issues.append(f"cạnh active của {ENTITY} lệch priority / load_mode / nb_name: {[tuple(r) for r in template]}")
        off_src, off_schema, off_trg = EDGES_OFF[0]
        off_n = sum(n for (name, _flag), n in _rows(off_schema, off_trg).items() if name == off_src)
        if off_n > 1:
            issues.append(f"cạnh {off_src} -> {off_trg} có {off_n} dòng")
        info = {name: n for name, n in _active(GLD, INFO).items() if name != off_src}
        if info != {name: 1 for name in INFO_KEEP}:
            issues.append(f"cạnh active của {INFO} là {info}, cần {sorted(INFO_KEEP)}")
        stale = [tuple(row) for row in spark.sql(
            f"SELECT src_schema, src_tbl, trg_schema, trg_tbl FROM {WM} WHERE watermark_id = '{NEW_WM}'").collect()]
        if any(row != (SLV, src, schema, trg) for row in stale):
            issues.append(f"{NEW_WM} đã có nhưng lệch cạnh: {stale}")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

    if col is None:
        spark.sql(f"ALTER TABLE {ENTITY_FQ} ADD COLUMNS (`{NEW_COL[0]}` {NEW_COL[1]})")
    row = template[0]
    nb = "CAST(NULL AS STRING)" if row["nb_name"] is None else f"'{row['nb_name']}'"
    spark.sql(f"""
    MERGE INTO {CFG} AS t
    USING (
        SELECT 'ON' AS action, '{src}' AS src_tbl, '{schema}' AS trg_schema, '{trg}' AS trg_tbl,
               (SELECT COALESCE(MAX(id), 0) + 1 FROM {CFG}) AS next_id
        UNION ALL
        SELECT 'OFF', '{off_src}', '{off_schema}', '{off_trg}', CAST(NULL AS BIGINT)
    ) AS s
    ON t.pl_name = '{PL}' AND t.src_schema = '{SLV}' AND t.src_tbl = s.src_tbl
       AND t.trg_schema = s.trg_schema AND t.trg_tbl = s.trg_tbl
    WHEN MATCHED AND s.action = 'OFF' AND t.is_active = 1 THEN UPDATE SET t.is_active = 0
    WHEN NOT MATCHED AND s.action = 'ON' THEN INSERT
        (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)
    VALUES (s.next_id, '{PL}', '{SLV}', s.src_tbl, s.trg_schema, s.trg_tbl, 1, {row['priority']}, '{mode}',
            CAST(NULL AS STRING), CAST(NULL AS STRING), {nb})
    """)

    # Sau khi ghi: chỉ xét phần cell đổi.
    problems = []
    if _column() != ("string", True):
        problems.append(f"{ENTITY_FQ}.{NEW_COL[0]} là {_column()}, cần string cho phép NULL")
    want_entity = {name: 1 for name in ENTITY_SRC + (src,)}
    if _active(SLV, ENTITY) != want_entity:
        problems.append(f"cạnh active của {ENTITY} là {_active(SLV, ENTITY)}, cần {want_entity}")
    want_info = {name: 1 for name in INFO_KEEP}
    if _active(GLD, INFO) != want_info:
        problems.append(f"cạnh active của {INFO} là {_active(GLD, INFO)}, cần {want_info}")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    print(f"{ENTITY_FQ}.{NEW_COL[0]} string NULL; cạnh {ENTITY} {sorted(want_entity)}; cạnh {INFO} {sorted(want_info)}")
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

### E5 Doc (`01_DATA_MODEL.md` §6 row N6)

- Add `slv_3p_poi_opening_hours` to the Đầu vào column.
- Add this sentence to the decisions column: `[SỬA 23/10] opening_hours_text: google periods_json của slv_3p_poi_opening_hours (left join poi_id); partner $.policies.operating_hours trong amentities của i18n vi; nguồn khác NULL. gld_enr_poi_info lấy nguyên cột này.`

### E6 Tests

- `test_enr_poi_contract.py`:
  - Add `HOURS_OFF = ("slv_3p_poi_opening_hours",)`.
  - Set `INFO_INPUTS = tuple(s for s in INFO_ACTIVE if s not in HOURS_OFF) + ("slv_enr_poi_info_multi_lang", "slv_enr_poi_destination")`. Keep `INFO_ACTIVE`, which is the `enrinfopy` history.
  - In `test_info_spec_inputs_match_active_edges`, use `(set(INFO_ACTIVE) - set(HOURS_OFF)) | landing`.
  - In `test_info_removal_keys`, the expected tuple is `("rating", "price", "review", "amenity")`.
  - In `test_info_patch_cell_guards`, check `ids[-8:-2]` against the old six and `ids[-2:] == ["ohpassmd", "ohpasspy"]`.
  - New `test_info_hours_passthrough`:
    - `'F.col("e.opening_hours_text").alias("opening_hours_text")'` is in the cell.
    - None of `_partner_hours`, `periods_json`, `"hours"`, `slv_3p_poi_opening_hours`, `$.policies.operating_hours`, `opening_hours_other_source`, or `partner_opening_hours_null` are in the cell.
    - `opening_hours_text_mismatch` and `eqNullSafe` are in the cell.
    - `_info_pure()["REQUIRED_COLS"]["entity"]` contains `opening_hours_text`.
    - `_info_pure()["REQUIRED_COLS"]["i18n"] == ("business_service_id", "locale")`.
  - New `test_hours_patch_cell_constants`:
    - `EDGES_ON` and `EDGES_OFF` equal the literals above.
    - `set(INFO_KEEP) == set(INFO_INPUTS)`.
    - `ENTITY_SRC` equals the entity sources of the `mvpoipy` `NODE_EDGES`.
    - `NEW_COL == ("opening_hours_text", "STRING")`.
    - The seed (`init_seed_ctrl`) has the `EDGES_ON` row active and the `EDGES_OFF` row with `is_active` 0.
  - New `test_hours_patch_cell_guards`:
    - Code lines without comments contain none of `DROP`, `DELETE`, `TRUNCATE`, `REPLACE`, `RESTORE`, `columnMapping`, ` AFTER `, `SET is_active = 1`, `CREATE TABLE`.
    - It contains ``ADD COLUMNS (`{NEW_COL[0]}` {NEW_COL[1]})``.
    - Token order: `held = True` < `Dừng trước khi ghi` < `ALTER TABLE` < `MERGE INTO {CFG}` < `Sau khi ghi` < `finally:`.
    - `"lock_exec_id = '{LOCK}'"` and `LEASE_MINUTES = 35` are present.
    - `MERGE INTO {CFG}` appears exactly once.
- `test_poi_entity_contract.py`:
  - In `test_entity_node_contract`, add `'"hours": "slv_3p_poi_opening_hours"'` and `HOURS_COLS`.
  - Assert that `"$.policies.operating_hours"` occurs inside the `vi = (` statement of `_partner` (D-OH-02).
  - Assert that `opening_hours_other_source` and `partner_opening_hours_null` are in the build.
  - Leave the `required_inputs` assertion unchanged.
  - In `test_create_ddl_patch`, apply the same `ids` change as in `test_info_patch_cell_guards`.
- `test_initial_ddl_contract.py`:
  - In `test_poi_entity_columns_derived`, after the estimates and before `TECH_COLUMNS`, add `("opening_hours_text", hours["periods_json"])`, where `hours` holds the active registry rows of `slv_3p_poi_opening_hours`. Assert `hours["periods_json"].lower() == "string"` and `_assign(build, "HOURS_COLS") == ("opening_hours_text",)`.
  - In `test_pipeline_config_rows_match_sources`:
    - Set `active` to 0 for pairs in the `ohpasspy` `EDGES_OFF`.
    - After the six entity rows, add the `ohpasspy` `EDGES_ON` row as `(enr, silver, src, schema, trg, 1, 1, mode, None, None, None)`.
    - Change the count from 52 to 53.

## Verification

Local:
- `python -m pytest tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py tests/test_initial_ddl_contract.py -q`
- `python -m pytest -q`

Runtime (DEV, after Rollout step 4):

- R1. Run `DESCRIBE TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich`. Expect `opening_hours_text string`, nullable. The ctrl query for the two edges shows the entity edge `is_active = 1` and the gold edge `0`.
- R2. In `ctrl_log_table_run` for the exec, expect entity `SUCCESS`, amenity `SUCCESS` or `NO_DATA`, gold `SUCCESS`. The gold `qg_json` metric is `opening_hours_text_mismatch = 0`. The entity `qg_json` has the block `opening_hours_other_source = 0` and the warn `partner_opening_hours_null`.
- R3. I1 equality. Expect 0:

```sql
WITH g AS (SELECT poi_id, opening_hours_text,
                  row_number() OVER (PARTITION BY poi_id ORDER BY updated_at DESC, created_at DESC) AS rn
           FROM lh_vv_gold.enr.gld_enr_poi_info)
SELECT count(*) FROM g JOIN lh_vv_silver.dbo.slv_poi_entity_non_enrich e
  ON e.poi_id = g.poi_id AND e.deleted_at IS NULL
WHERE g.rn = 1 AND NOT (g.opening_hours_text <=> e.opening_hours_text)
```

- R4. Value preserved. Run the same latest-row CTE on `gld_enr_poi_info VERSION AS OF V0` and on the current version, joined on `poi_id`. Expect a count of 0 where `NOT (old <=> new)`.
- R5. I2 formula equivalence. Read the input versions from the entity's `src_versions_json` for the exec. Then, using `VERSION AS OF`:
  - Google rows: compare `e.opening_hours_text` with `oh.periods_json`.
  - Partner rows: compare with `get_json_object(i.amentities, '$.policies.operating_hours')`, where `i` is the live `vi` row of `business_service_id = source_id`.
  - Expect 0 mismatches.
- R6. Run the orchestrator again with no source change. Expect entity and gold `NO_DATA`. Re-run `ohpasspy` and expect the same print with no new ctrl commit (`DESCRIBE HISTORY` on ctrl is unchanged).
- R7. Propagation, observed on later ticks: when FL_00 changes `slv_3p_poi_opening_hours`, the entity inbox shows `DATA_CHANGED` on the hours edge and gold runs after the entity in the same exec.
