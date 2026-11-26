RESULT: PASS

## Main brief

### Decision
Add the six gold-only columns in place, keeping grain and MERGE keys. `old_address` = coalesce of G1' (`house_number, street, old_formatted_address`), G2' (`house_number, street, old_ward_with_type, old_city_with_type`), and G3 (`slv_enr_poi_destination.full_address`). It is NULL when there is no destination row. Price comes from a 1:1 LEFT JOIN on `slv_3p_poi_price` with the default live-only read, no `source_name` filter, a stop on duplicates, and a type guard. `story` and `local_tips` reuse the partner i18n join with no fallback. One new trailing `NB_CREATE_DDL` cell (`oldpricemd`/`oldpricepy`) adds the columns (checked by name, ignoring `load_origin`) and the price edge under the 30M flow lock.

### Invariants Main must preserve
- `SPEC.pk`, `write_mode="MERGE"`, and `required_inputs` do not change: info `("entity",)`, multi_lang `("multi_lang","entity")`.
- In each build cell, `live_only=False` appears exactly 3 times. The price input uses the default read. Code lines never contain `deleted`. `F.when(is_google,` appears exactly 4 times.
- `OLD_ADDR` is not in `DEST_COLS`. `old_address` never reads `_e_full_address`, and no name `old_house_number`, `old_street`, or `old_full_address` appears.
- More than one `slv_3p_poi_price` row for a kept `poi_id` raises `QualityGateError` and writes nothing. Price types are pinned to `int` and `decimal(18,2)`.
- `story` and `local_tips` have no `coalesce` or fallback. P1 non-partner rows get NULL.
- The exact line `_require(i18n, ("business_service_id", "locale", "bio", "usps"), "slv_pn_business_service_i18ns")` stays unchanged.
- The six columns are absent from every `apps.*` table body and every `Srv*.java` entity. All other gold columns still match PostgreSQL by name and type.
- `oldpricepy` has exactly one `ALTER TABLE` (with `AFTER`) and one `INSERT INTO {CFG}`. A line-start `_refresh_lock()` comes before each. It contains no DROP, DELETE, TRUNCATE, REPLACE, RESTORE, `columnMapping`, `MERGE INTO`, `CREATE TABLE`, or `UPDATE {CFG}`. A rerun writes nothing.
- Seed and live data each have exactly seven active `PL_VV_TRANS_SLV_TO_GLD_30M` edges into `gld_srv_poi_info`, equal to `SPEC.inputs` values. The price edge is the last seed row.
- `TABLE_SPECS` for both tables equals `oldpricepy` `TABLE_COLS`. `OUT_COLS + TECH` equals those names in order.

### Edit list
| # | file | anchor | change | done-when |
|---|---|---|---|---|
| E0 | (task state) | `scope.files` | Get user approval to add `tests/test_enr_extract_contract.py`, `tests/test_enr_poi_contract.py`, `tests/test_poi_entity_contract.py` | scope updated |
| E1 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_tables` gld_srv_poi_info, multi_lang specs | `old_address` after `full_address`; 3 price columns after `review_count`; `story`, `local_tips` after `experience` (doc "NB_SETUP_INITIAL_DDL edits") | specs equal `oldpricepy` TABLE_COLS |
| E2 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` PIPELINE_CONFIG_ROWS | Append comment and the `slv_3p_poi_price` row after the media row | 79 rows; last row is price |
| E3 | notebooks/NB_CREATE_DDL.ipynb | new cells after `lgpnamepy` | Add `oldpricemd` and `oldpricepy` verbatim from doc "Code: NB_CREATE_DDL cells" | ids end `lgpnamemd, lgpnamepy, oldpricemd, oldpricepy` |
| E4 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` constants | Add `OLD_ADDR`, `PRICE_COLS`, `PRICE_TYPES`; replace `OUT_COLS` | matches doc |
| E5 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` new `_price` after `_cover` | As in doc | dup message present |
| E6 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfobuild` `build` | Price input and guard, destination select and `_require` with `*OLD_ADDR`, price join, `og1`/`og2`/`old_address`/`old_group`, select items, single-`agg` metrics, drop | doc "Code: srvinfobuild changes" applied |
| E7 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `SPEC` | Add `"price": "slv_3p_poi_price"` after `media` | inputs has 7 entries |
| E8 | notebooks/NB_GLD_SRV_POI_INFO.ipynb | `srvinfomd` | One line for `old_address` (D-OLD-ADDR), one for price; you may remove the duplicated last line | text only |
| E9 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | `srvmlbuild` | `I18N_TEXT_COLS`, `OUT_COLS`, `keyed`/`bio` select tails, p2 select tail, second `_require` | doc "Code: srvmlbuild changes" |
| E10 | notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb | `srvmlmd` | One line: `story`, `local_tips` from i18n, no fallback | text only |
| E11 | docs/context/mapping_gld_srv_poi_info.md | §1.1, §1.6, §1.2 | Per doc "Mapping doc edits": 4 new rows in `OUT_COLS` order; types `integer`, `decimal(18,2)` | mapping tests pass |
| E12 | docs/context/mapping_gld_srv_poi_multi_lang.md | §1.1, §1.2 | Bullet and 2 rows, each with `P2:` | `test_multi_lang_mapping_targets` passes |
| E13 | tests/test_gld_srv_poi_contract.py | `test_node_specs` | Add `"price": "slv_3p_poi_price"` to the info expected inputs | pass |
| E14 | tests/test_gld_srv_poi_contract.py | `test_build_columns_match_ddl` | Info from `oldpricepy` TABLE_COLS; also assert multi_lang TABLE_SPECS == `oldpricepy` TABLE_COLS[ML_FQ] | pass |
| E15 | tests/test_gld_srv_poi_contract.py | `test_info_rating_patch`, `test_review_source_patch_cell` | Prefix trim (doc "Test edits") | pass |
| E16 | tests/test_gld_srv_poi_contract.py | `test_multi_lang_experience_rule` | `ML_COLS[-1] == "experience"`; `OUT_COLS[-3:] == ("experience","story","local_tips")` | pass |
| E17 | tests/test_gld_srv_poi_contract.py | `test_multi_lang_i18n_only_branch` | Expected P2 line → `'F.col("bio").alias("description"), F.col("usps").alias("experience"), *I18N_TEXT_COLS)'` | pass |
| E18 | tests/test_gld_srv_poi_contract.py | new `test_old_price_story_patch_cell` | ids tail; NEW_COLS == {INFO_FQ: OLDPRICE_INFO, ML_FQ: OLDPRICE_ML}; info TABLE_COLS == srvactivepy contract with `old_address` after `full_address` and price after `review_count`; ML minus new == ML_BASE; EDGES_ON == [PRICE_EDGE]; EDGES_KEEP is 6; PL == plcadpy RENAMES[1][1]; OWNER_COL; token order `held = True` < `Dừng trước khi ghi` < `ALTER TABLE` < `INSERT INTO {CFG}` < `Sau khi ghi` < `finally:`; forbidden tokens; 2 line-start `_refresh_lock()` around ALTER and INSERT; `if issues:` before ALTER | pass |
| E19 | tests/test_gld_srv_poi_contract.py | new `test_info_old_address_rule` | OLD_ADDR value; `old_address` follows `full_address` in OUT_COLS; the `og1`/`og2`/`old_address` lines present; no `old_house_number`/`old_street`/`old_full_address`; `source.count('F.col("_e_full_address")') == 1`; OLD_ADDR disjoint from DEST_COLS | pass |
| E20 | tests/test_gld_srv_poi_contract.py | new `test_info_price_rule` | PRICE_COLS and PRICE_TYPES values; OUT_COLS slice after `review_count` is the price trio; `out[-2:]` is cover; `pr = ctx.input("price")`; dup message; `.join(price, "poi_id", "left")`; `currency` absent; `source_name` absent from the `_price` body | pass |
| E21 | tests/test_gld_srv_poi_contract.py | new `test_multi_lang_story_local_tips_rule` | `I18N_TEXT_COLS`; `'F.col("locale").alias("_loc"), "bio", "usps", *I18N_TEXT_COLS)'` count == 2; second `_require` line; no `coalesce(F.col("story")` or `coalesce(F.col("local_tips")` | pass |
| E22 | tests/test_gld_srv_poi_contract.py | new `test_old_price_story_mapping_rows` | Info rows contain `old_formatted_address`, `old_ward_with_type`, `old_city_with_type`, `slv_3p_poi_price.price_*`, types `integer` and `decimal(18,2)`; handling has `slv_3p_poi_price` and `price_matched`; ML rows contain `slv_pn_business_service_i18ns.story` / `.local_tips` and `không fallback` | pass |
| E23 | tests/test_initial_ddl_contract.py | `test_columns_match_sources` L342, `test_gld_srv_patch_create_matches_init` L759-760 | `srvactivepy` → `oldpricepy` | pass |
| E24 | tests/test_initial_ddl_contract.py | `test_pipeline_config_rows_match_sources` | After the `srvcoverpy` loop, add the same loop for `oldpricepy` EDGES_ON; `len(expected) == 79` | pass |
| E25 | tests/test_initial_ddl_contract.py | `test_pl_cadence_patch_cell` | Prefix trim | pass |
| E26 | tests/test_srv_poi_serving_contract.py | module constants | `GOLD_ONLY = {"srv_poi_info": {"old_address","price_level","price_min","price_max"}, "srv_poi_multi_lang": {"story","local_tips"}}` | — |
| E27 | tests/test_srv_poi_serving_contract.py | `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys` | Compare `{c: t for c, t in spec["cols"].items() if c not in GOLD_ONLY.get(name, set())}` | pass |
| E28 | tests/test_srv_poi_serving_contract.py | new `test_gold_only_columns_stay_out_of_serving` | GOLD_ONLY ⊆ gold cols; disjoint from `pg_tables()` cols; if SERVICE exists, disjoint from `entity_tables()` cols | pass |
| E29 | tests/test_srv_poi_serving_contract.py | `test_info_cover_patch_cell`, `test_destination_name_patch_cell` | Prefix trim | pass |
| E30 | tests/test_srv_poi_serving_contract.py | `test_info_cover_build_rule` | `OUT_COLS[-2:] == ("cover_id","cover_blob_url")`; inputs exclude `("media","price")` == INFO_SOURCES; `inputs["price"] == "slv_3p_poi_price"` | pass |
| E31 | tests/test_srv_poi_serving_contract.py | `test_info_cover_seed_and_init_ddl` | `ROWS[-2:]` == [media row, price row]; `info` = oldpricepy; keep the srvactivepy chain on `active` and assert `[c for c in info if c not in OLDPRICE_INFO] == active` | pass |
| E32 | tests/test_srv_poi_serving_contract.py | `test_destination_name_and_review_source_across_layers` | `srvactivepy` → `oldpricepy` for info | pass |
| E33 | tests/test_enr_extract_contract.py:242, tests/test_enr_poi_contract.py:223, tests/test_poi_entity_contract.py:635 | the `ids[-10:]` asserts | Prefix trim (only after E0) | pass |

### Order and stop points
1. **STOP (user decision).** Get approval to add the three out-of-scope test files to `scope.files` (E0). Without it, E33 cannot be made and verification fails on the cell-id pins.
2. E1–E3 (DDL and seed), then E4–E10 (notebooks), then E11–E12 (docs), then E13–E33 (tests).
3. Run the local tests. **STOP (evidence).** All pass, or report failures with their output.
4. Main writes `runtime-runbook.md` from doc "Rollout" and the R/P probes. **STOP (runtime evidence, user on Fabric DEV).** Run P1, then `oldpricepy`, then publish both notebooks, then the 30M run, then R1–R6. Never publish the notebooks before `oldpricepy` succeeds.
5. Specialist review (`spark-runtime-reviewer`, `sql-data-reviewer`), with P0/P1 findings handled within 2 rounds.

### Tests and verification
- `python -m pytest tests/test_gld_srv_poi_contract.py tests/test_initial_ddl_contract.py tests/test_srv_poi_serving_contract.py tests/test_enr_extract_contract.py tests/test_enr_poi_contract.py tests/test_poi_entity_contract.py -q`
- New tests: `test_old_price_story_patch_cell`, `test_info_old_address_rule`, `test_info_price_rule`, `test_multi_lang_story_local_tips_rule`, `test_old_price_story_mapping_rows`, `test_gold_only_columns_stay_out_of_serving`.
- Must still pass: `test_node_specs`, `test_build_columns_match_ddl`, `test_partner_without_destination_branch`, `test_info_rating_build_rules`, `test_mapping_targets_match_out_cols`, `test_multi_lang_mapping_targets`, `test_pipeline_config_rows_match_sources`, `test_gold_and_pg_columns_and_types_match`, `test_info_cover_seed_and_init_ddl`, `test_pl_cadence_seed`.
- Full suite: `python -m pytest tests -q`.
- Runtime: probes P1 and R1–R6 in doc "Verification".

### Read only if needed
- "Scope" (scope gap) → E0, E33
- "Resolved model-design questions" → E4, E7, E8 (positions, read mode, required_inputs)
- "Alternatives considered" → E3 (by-name check), E6 (single agg), E15/E25/E29/E33 (prefix trim)
- "Code: srvinfobuild changes" → E4–E7
- "Code: srvmlbuild changes" → E9, E17, E21
- "Code: NB_CREATE_DDL cells oldpricemd and oldpricepy" → E3, E18
- "NB_SETUP_INITIAL_DDL edits" → E1, E2
- "Mapping doc edits" → E11, E12, E22
- "Test edits" → E13–E33 constants
- "Ordering", "Partial failure", "Rollout", "Rollback and forward recovery" → step 4 runbook
- "Idempotency" → runbook note: one-time update of every row through `row_hash`
- "Verification" → P1, R1–R6

# Architecture — 20261126-gld-srv-old-address-price-story

Basis: `request.md`, `decision.md` row `D-OLD-ADDR` and `## Quyết định của người dùng`, and `model-design.md` (`## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`). This design does not change grain, keys, or column types. It settles the five open items in `model-design.md` `## Conflicts and questions`. See "Resolved model-design questions".

## Scope

- `gld_srv_poi_info` gains `old_address`, `price_level`, `price_min`, `price_max`. `gld_srv_poi_multi_lang` gains `story`, `local_tips`. All six are gold-only.
- `NB_SETUP_INITIAL_DDL`: `init_tables` `TABLE_SPECS` (six columns) and `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` (one edge).
- `NB_CREATE_DDL`: two new trailing cells, `oldpricemd` and `oldpricepy` (schema patch and edge insert).
- `NB_GLD_SRV_POI_INFO` (`srvinfomd`, `srvinfobuild`) and `NB_GLD_SRV_POI_MULTI_LANG` (`srvmlmd`, `srvmlbuild`).
- The two mapping docs and three in-scope contract tests.
- **Scope gap (Stop 1).** Three out-of-scope tests pin the last 10 cell ids of `NB_CREATE_DDL` to end at `lgpnamepy`: `tests/test_enr_extract_contract.py:242`, `tests/test_enr_poi_contract.py:223`, and `tests/test_poi_entity_contract.py:635`. A new trailing cell is required by the acceptance criteria, and it breaks all three. Each needs the same one-line prefix trim (see "Test edits"). Main must get these three paths added to `scope.files` before editing them. Without that, verification cannot pass.

## Non-goals

PostgreSQL DDL, Java entities and DTOs, `docs/context/api-mapping/`, `currency`, a `source_name` filter on price, choosing one price row among duplicates, fallback of `story` or `local_tips` to enr, `old_house_number`, `old_street`, `old_full_address`, entity `full_address` as `old_address`, `pipelines/*.json`, and registry changes. All three price columns and both i18n columns are already registered.

## Invariants

1. Grain and MERGE keys do not change: info `pk=("poi_id",)` and multi_lang `pk=("poi_id","lang")`, both `write_mode="MERGE"`.
2. `old_address`, when a destination row exists, is `coalesce(G1', G2', G3)`, joined with `", "`:
   - G1' = `house_number, street, old_formatted_address`.
   - G2' = `house_number, street, old_ward_with_type, old_city_with_type`.
   - G3 = `slv_enr_poi_destination.full_address`.
   `house_number` and `street` go through `_text_or_null`, exactly as in `full_address`. With no destination row, `old_address` is NULL for every source, partner included. `_e_full_address` is never read for `old_address`.
3. The price columns come from a 1:1 LEFT JOIN on `poi_id` over every kept row, with no `source_name` filter. No price row gives NULL. More than one live price row for a kept `poi_id` raises `QualityGateError` and nothing is written. The types stay exactly `int` and `decimal(18,2)`. A drift raises `ConfigError` before the MERGE.
4. On P1, `story` and `local_tips` come only from the partner-gated i18n join, the same join `bio` and `usps` use. Non-partner P1 rows get NULL. P2 takes them straight from i18n. There is no fallback anywhere.
5. The six columns never appear in `apps.*` PostgreSQL tables or in `Srv*.java` entities. Every other gold column still matches PostgreSQL by name and type.
6. The `oldpricepy` cell writes nothing unless all pre-write checks pass. A rerun writes nothing. It never drops, deletes, rewrites, reorders, or re-enables an edge.
7. `gld_srv_poi_info` has exactly seven active `PL_VV_TRANS_SLV_TO_GLD_30M` edges, and they equal `SPEC.inputs` values. The same holds in the seed.
8. Rollout order: `oldpricepy` runs before either notebook is published.

## State ownership

| State | Owner (writer) | This task |
|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` and `gld_srv_poi_multi_lang` rows | `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_MULTI_LANG` via `run_node` MERGE | new business columns |
| The same tables' schema | `NB_SETUP_INITIAL_DDL` (fresh workspace) and `NB_CREATE_DDL` `oldpricepy` (existing workspace). `ensure_target` adds missing columns at the end as a fallback. | add six nullable columns |
| `load_origin` | `legacyidpy` and the lib owner logic | untouched. The patch tolerates it. |
| `slv_3p_poi_price` | `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00` / `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | read-only |
| `slv_pn_business_service_i18ns`, `slv_enr_poi_destination` | the partner and enrichment extracts | read-only |
| `ctrl_mng_pipeline_config` edge `slv_3p_poi_price → gld_srv_poi_info` | `oldpricepy` (existing) and the `init_seed_ctrl` seed (fresh) | one insert |
| `ctrl_mng_watermark` `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` lock | `NB_00_ORCHES_SLV_TO_GLD` and patch cells | taken and released by `oldpricepy` |

## Grain and keys

Unchanged. See `model-design.md` `## Entities and grain` and `## Keys`.
- Price join: `gld_srv_poi_info.poi_id = slv_3p_poi_price.poi_id`. The source grain is one row per `poi_id` (registry `key: "poi_id"`). The duplicate stop enforces it at read time.
- i18n join: the existing `(uuid_md5(business_service_id,'partner'), locale)` join, with the source grain one row per (`business_service_id`, `locale`).

## Resolved model-design questions

| # | Question | Decision | Why |
|---|---|---|---|
| 1 | No proposal | Basis is `request.md` and `D-OLD-ADDR` | The request is complete and the ledger holds the only open choice |
| 2 | `old_` wording | Follow `D-OLD-ADDR` | The user's later decision |
| 3 | Price read mode | Default `ctx.input("price")`, live rows only | Same as `rating`, `review`, `media`. `test_node_specs` pins `live_only=False` to three calls. A soft-deleted price means no price. |
| 4 | Positions | `old_address` after `full_address`; the price columns after `review_count` and before `cover_id`; `story` and `local_tips` after `experience` | Keeps address and 3P metrics grouped. One `AFTER` anchor chain per group. |
| 5 | `required_inputs` | Price stays optional: info stays `("entity",)` | Same as rating, review, and media. An empty price table gives NULLs, not a failure. |

## Alternatives considered

| Choice | Options | Selected | Trade-off |
|---|---|---|---|
| Existing-workspace DDL | (a) rely on `ensure_target` auto-add; (b) an explicit patch cell | (b) | (a) appends at the end, misplaces columns, and adds no edge. (b) also seeds the edge under the flow lock. |
| Patch schema check | (a) strict ordered equality like `srvactivepy`; (b) by name and type, ignoring `load_origin` | (b) | `legacyidpy` appended `load_origin` to the live tables after `srvactivepy`, so (a) would always stop on DEV. (b) still stops on a missing base column, a type drift, or an unknown column. Positions are cosmetic in Delta: the cell warns on drift and does not reorder (no `columnMapping`). |
| Price duplicates | stop or pick | stop | Required by the request. Same as `_rating`. |
| Price types | cast to a target type or keep the source type | keep, with a guard | Acceptance criterion 3. The guard gives a clear message before `ensure_target` raises its generic type error. |
| Breaking cell-id pins in old tests | re-index every slice or trim the prefix to `lgpnamepy` | trim | One line per test. Future trailing cells do not break them again. |
| Metrics | one `count()` per metric (current style) or one `agg` | one `agg` for the five new metrics | Avoids five extra full recomputes of an uncached plan. |

## Ordering

1. The `oldpricepy` cell takes the lock, checks everything, then runs: ALTER info (`old_address`, `price_level`, `price_min`, `price_max`, in contract order, each `AFTER` the previous contract column), ALTER multi_lang (`story`, `local_tips`), then INSERT the edge, then post-checks.
2. Publish both notebooks after the cell succeeds. If a notebook is published first, its price input has no edge. Expect a `run_node` `ConfigError` or an unpinned read, and `ensure_target` appends the columns at the end. Recovery: run `oldpricepy`. It accepts the existing columns, reports position drift, and adds the edge.
3. Inside the info build: `_destination`, then filter, then `_cover` and `_price` on the kept keys, then the joins, then the expressions, then `select(*OUT_COLS)`. `OUT_COLS` order defines the `row_hash` order.

## Transaction and commit boundaries

- Each `ALTER TABLE ADD COLUMNS` is a separate metadata-only Delta commit. The edge `INSERT … WHERE NOT EXISTS` is one commit on `ctrl_mng_pipeline_config`. There is no cross-table transaction; idempotent reruns cover the gaps.
- Each node writes one MERGE commit per run (lib-owned). The quality gate and the duplicate-price stop raise before the MERGE, so nothing is written.

## Idempotency

- `oldpricepy` only adds missing columns, and the INSERT is guarded by `NOT EXISTS` on (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`). A second run prints `+[]` and makes no commit.
- Nodes: a RECOMPUTE MERGE keyed on `row_hash`. Repeated runs on the same inputs update nothing.
- Expected one-time effect: the first run after publish changes `row_hash` for every live row in both tables, because the business columns changed. Every row is updated once and `updated_at` moves. Any downstream incremental consumer re-reads all rows once. The same effect was accepted for `is_active` (`mapping_gld_srv_poi_info.md` §1.1).

## Concurrency

- `oldpricepy` holds `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` with a 90-minute lease, calls `_refresh_lock()` before each write, and releases the lock in `finally`. This excludes the 30M flow, which runs both nodes, during the ALTERs.
- Silver writers (FL_00, ENR_15M) run concurrently. Their tables are not altered here. The gold node reads pinned versions as before.
- A second operator running the cell fails to take the lock and stops without writing.

## Retry and recovery

- Cell: rerun after any failure. It converges: missing columns are added, an existing edge is skipped, and a lock lost mid-cell raises before the next write.
- Node: a `QualityGateError` on duplicate prices or a `ConfigError` on a type drift or missing column is not retried by the lib. Fix the source data or schema, then rerun the flow.

## Partial failure

| Failure point | State left | Recovery |
|---|---|---|
| After some info ALTERs | some columns added, no edge | rerun the cell |
| After all ALTERs, before INSERT | columns present, no edge | rerun. The old notebook still works and ignores the new columns. |
| Notebook published, cell never run | columns appended at the end by `ensure_target`, price input without an edge | run the cell. It warns on drift and adds the edge. |
| One node published, the other not | that table has NULLs in the new columns until its node is published | publish the other node |

## Observability

- Cell prints `oldprice: +[table.col …]; cạnh [...]`, and `WARN oldprice: … lệch vị trí` when columns pre-existed out of position.
- Info metrics: `old_address_g1`, `old_address_g2`, `old_address_g3`, `old_address_null`, `price_matched`. The existing metrics are unchanged.
- Stop messages: `slv_3p_poi_price {n} poi_id có hơn một dòng` and `slv_3p_poi_price kiểu {...}, cần {...}`.
- No new warnings on multi_lang. The existing `multi_lang_i18n_*` warnings are unchanged.

## Security

No new inputs from users. All SQL in the cell is built from module constants. No secrets. The columns are public POI content. Gold-only placement is enforced by tests, so nothing reaches PostgreSQL or the API.

## Rollout (user, Fabric DEV, via `runtime-runbook.md`)

1. Pre-flight probe P1 (see "Verification").
2. Run `NB_CREATE_DDL` cell `oldpricepy` only. Expect `+[...]`. Rerun and expect `+[]`.
3. Publish `NB_GLD_SRV_POI_INFO` and `NB_GLD_SRV_POI_MULTI_LANG`.
4. Run `PL_VV_TRANS_SLV_TO_GLD_30M` once, or the two nodes through it. Check the metrics and probes R1–R6.
5. Confirm that the next gold→PostgreSQL serving load succeeds and `apps.srv_poi_info` and `apps.srv_poi_multi_lang` are unchanged. That sink is not in this repo. The precedent is `load_origin`, which is already gold-only.
- After `oldpricepy`, do not rerun `srvactivepy` or `srvcoverpy`. Their strict contracts are the old versions, so they would stop safely, but the run is wasted.

## Rollback and forward recovery

- Dropping a column on Delta needs `delta.columnMapping.mode = name`, which the patch cells must not use. So rollback is not a column drop, contrary to the triage note.
- Rollback: republish the previous notebook versions. `ensure_target` then logs a WARN for the build-missing columns and they keep stale values. Optionally the user runs a manual `UPDATE … SET <col> = NULL` and sets the price edge `is_active = 0`. Both are outside this task.
- Preferred: forward-fix the notebook.

## Implementation plan

Rows E1–E14 in the Main brief. The code blocks follow.

### Code: `srvinfobuild` changes

Constants. Add these after `COVER_COLS`, and replace `OUT_COLS`:

```python
OLD_ADDR = ("old_formatted_address", "old_ward_with_type", "old_city_with_type")
PRICE_COLS = ("poi_id", "price_level", "price_min", "price_max")
PRICE_TYPES = {"price_level": "int", "price_min": "decimal(18,2)", "price_max": "decimal(18,2)"}
OUT_COLS = ("poi_id", "poi_name", "source_name", "business_sector", "business_category", "subcategory_tags",
            "destination_id", "destination_name", "full_address", "old_address", "street", "ward", "district", "city",
            "country_code", "postal_code", "lat", "lng", "phone", "email", "website_url", "operating_status",
            "is_verified", "is_recommended", "is_bookable", "is_active", "operating_hours", "holiday_exceptions",
            "rating_overall", "rating_count", "review_count", "price_level", "price_min", "price_max",
            "cover_id", "cover_blob_url")
```

Do not add `OLD_ADDR` to `DEST_COLS`. The `from_dest` loop and `test_partner_without_destination_branch` iterate `DEST_COLS[2:]`.

New function, after `_cover`:

```python
def _price(price, keys):
    # 20261126: một dòng mỗi poi_id, mọi nguồn, không lọc source_name. Trùng poi_id -> dừng, không chọn dòng.
    p = price.select(*PRICE_COLS).join(keys, "poi_id", "left_semi")
    dup = p.groupBy("poi_id").count().where("count > 1").count()
    if dup:
        raise QualityGateError(f"gld_srv_poi_info: slv_3p_poi_price {dup} poi_id có hơn một dòng")
    return p.withColumn("_priced", F.lit(True))
```

Changes in `build(ctx)`. Apply them in place and leave every other line unchanged:

```python
    md = ctx.input("media")
    pr = ctx.input("price")
    ...
    _require(des, DEST_COLS + ("old_ward", "old_district", "old_city") + OLD_ADDR, "slv_enr_poi_destination", ": chạy enrbrzpy của NB_CREATE_DDL")
    ...
    _require(md, COVER_COLS, "slv_poi_media_info")
    _require(pr, PRICE_COLS, "slv_3p_poi_price")
    price_type = {name: dtype for name, dtype in pr.dtypes if name in PRICE_TYPES}
    if price_type != PRICE_TYPES:
        raise ConfigError(f"gld_srv_poi_info: slv_3p_poi_price kiểu {price_type}, cần {PRICE_TYPES}")
    ...
    des, dup = _destination(des.select(*DEST_COLS, "old_ward", "old_district", "old_city", *OLD_ADDR), ent.select("poi_id"))
    ...
    cover = _cover(md, rows.select("poi_id"))
    price = _price(pr, rows.select("poi_id"))
    rows = (rows.join(_rating(rt, google), "poi_id", "left").join(_reviews(rv, google), "poi_id", "left")
            .join(cover, "poi_id", "left").join(price, "poi_id", "left")
            .withColumn("_h", _hours(F.col("source_name"), F.col("opening_hours_text"))))
    ...
    # (after the addr_group definition)
    # D-OLD-ADDR: cùng luật nhóm của full_address. house_number, street của entity; nhóm 3 là full_address của destination.
    og1 = F.concat(hn, sep, st, sep, F.col("old_formatted_address"))
    og2 = F.concat(hn, sep, st, sep, F.col("old_ward_with_type"), sep, F.col("old_city_with_type"))
    old_address = F.when(has_dest, F.coalesce(og1, og2, g3))
    old_group = F.when(has_dest, F.when(og1.isNotNull(), F.lit("G1")).when(og2.isNotNull(), F.lit("G2"))
                       .when(g3.isNotNull(), F.lit("G3")))
```

In `out = rows.select(...)`:
- After `full_address.alias("full_address"),`, insert `old_address.alias("old_address"),`.
- After `addr_group.alias("_addr_group"),`, insert `old_group.alias("_old_group"),`.
- After the `review_count` line, insert `"price_level", "price_min", "price_max",`.
- After the `_rated` item, insert `F.col("_priced").alias("_priced"),`.

After the existing `ctx.metrics.update(...)`:

```python
    extra = out.agg(*[F.sum(F.when(F.col("_old_group") == g, 1).otherwise(0)).alias(f"old_address_{g.lower()}")
                      for g in ("G1", "G2", "G3")],
                    F.sum(F.when(F.col("old_address").isNull(), 1).otherwise(0)).alias("old_address_null"),
                    F.sum(F.when(F.col("_priced").isNotNull(), 1).otherwise(0)).alias("price_matched")).first().asDict()
    ctx.metrics.update({name: int(value or 0) for name, value in extra.items()})
    out = out.drop("_err", "_addr_group", "_old_group", "_priced")
```

In `SPEC.inputs`, append `"price": "slv_3p_poi_price"` after `"media"`. `required_inputs` stays `("entity",)`.

Do not add a `F.when(is_google, …)` wrapper or the word `deleted` to code lines. Existing tests count these.

### Code: `srvmlbuild` changes

```python
I18N_TEXT_COLS = ("story", "local_tips")
OUT_COLS = ("poi_id", "lang", "poi_name", "source_name", "time_to_spend", "best_time", "cost", "description", "experience",
            "story", "local_tips")
```

- `_i18n_only`, `keyed` select line: `F.col("locale").alias("_loc"), "bio", "usps", *I18N_TEXT_COLS)`.
- `_i18n_only`, `p2` first select: end with `F.col("bio").alias("description"), F.col("usps").alias("experience"), *I18N_TEXT_COLS)`.
- `build`: keep `_require(i18n, ("business_service_id", "locale", "bio", "usps"), "slv_pn_business_service_i18ns")` byte-for-byte. Add `_require(i18n, I18N_TEXT_COLS, "slv_pn_business_service_i18ns")` after it.
- `build`: the second line of `bio = i18n.select(...)` becomes `F.col("locale").alias("_loc"), "bio", "usps", *I18N_TEXT_COLS)`.
- No other change. The P1 join is already partner-gated, so non-partner rows get NULL. `p1 … .select(*OUT_COLS)` picks up the joined columns. P2 casts to the P1 types.

### Code: `NB_CREATE_DDL` cells `oldpricemd` and `oldpricepy`

Append both after `lgpnamepy`. The code cell uses the same `metadata.microsoft` block as `srvactivepy`, with `outputs: []` and `execution_count: null`.

`oldpricemd` source:

```
# [THÊM 26/11] 20261126-gld-srv-old-address-price-story

Thêm `old_address` STRING sau `full_address`; `price_level` INT, `price_min`, `price_max` DECIMAL(18,2) sau `review_count` vào `gld_srv_poi_info`. Thêm `story`, `local_tips` STRING sau `experience` vào `gld_srv_poi_multi_lang`. Cho phép NULL, chỉ ở gold. Thêm 1 cạnh `PL_VV_TRANS_SLV_TO_GLD_30M`: `slv_3p_poi_price` → `gld_srv_poi_info`. Chạy lại không đổi gì.
Chạy trước khi publish `NB_GLD_SRV_POI_INFO` và `NB_GLD_SRV_POI_MULTI_LANG` bản 26/11. Sau cell này không chạy lại `srvactivepy`, `srvcoverpy`.
```

`oldpricepy` source:

```python
# [THÊM 26/11] 20261126-gld-srv-old-address-price-story (D-OLD-ADDR)
# 1. gld_srv_poi_info: old_address STRING sau full_address; price_level INT, price_min, price_max DECIMAL(18,2) sau review_count.
# 2. gld_srv_poi_multi_lang: story, local_tips STRING sau experience.
# 3. Cạnh slv_3p_poi_price -> gld_srv_poi_info (RECOMPUTE, priority 1, NB_GLD_SRV_POI_INFO). Không bật lại cạnh tắt.
# Sáu cột chỉ ở gold: không thêm vào PostgreSQL, API không đọc.
# So cột theo tên, không theo vị trí; bỏ qua load_origin (legacyidpy). Thiếu cột nền, lệch kiểu, cột lạ, cạnh lạ -> dừng, chưa ghi.
# Giữ khoá wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M suốt cell. Chạy lại: không ghi.
import uuid

CFG = "lh_vv_ctrl.dbo.ctrl_mng_pipeline_config"
WM = "lh_vv_ctrl.dbo.ctrl_mng_watermark"
PL = "PL_VV_TRANS_SLV_TO_GLD_30M"
WID = f"wm_flow__{PL}"
SLV, GLD = "lh_vv_silver.dbo", "lh_vv_gold.dbo"
LEASE_MINUTES = 90  # bằng p_lock_timeout_min mặc định của NB_00_ORCHES_SLV_TO_GLD
OWNER_COL = "load_origin"
PRICE_FQ = "lh_vv_silver.dbo.slv_3p_poi_price"
PRICE_OWNER = "PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00"
PRICE_SRC = [("poi_id", "string"), ("price_level", "int"), ("price_min", "decimal(18,2)"), ("price_max", "decimal(18,2)")]
NEW_COLS = {
    "lh_vv_gold.dbo.gld_srv_poi_info": [("old_address", "STRING"), ("price_level", "INT"),
                                        ("price_min", "DECIMAL(18,2)"), ("price_max", "DECIMAL(18,2)")],
    "lh_vv_gold.dbo.gld_srv_poi_multi_lang": [("story", "STRING"), ("local_tips", "STRING")],
}
TABLE_COLS = {
    "lh_vv_gold.dbo.gld_srv_poi_info": [
        ("poi_id", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
        ("business_sector", "STRING"), ("business_category", "STRING"), ("subcategory_tags", "STRING"),
        ("destination_id", "STRING"), ("destination_name", "STRING"), ("full_address", "STRING"),
        ("old_address", "STRING"),
        ("street", "STRING"), ("ward", "STRING"), ("district", "STRING"), ("city", "STRING"),
        ("country_code", "STRING"), ("postal_code", "STRING"), ("lat", "DOUBLE"), ("lng", "DOUBLE"),
        ("phone", "STRING"), ("email", "STRING"), ("website_url", "STRING"), ("operating_status", "STRING"),
        ("is_verified", "BOOLEAN"), ("is_recommended", "BOOLEAN"), ("is_bookable", "BOOLEAN"),
        ("is_active", "BOOLEAN"),
        ("operating_hours", "STRING"), ("holiday_exceptions", "STRING"), ("rating_overall", "DECIMAL(4,2)"),
        ("rating_count", "INT"), ("review_count", "INT"),
        ("price_level", "INT"), ("price_min", "DECIMAL(18,2)"), ("price_max", "DECIMAL(18,2)"),
        ("cover_id", "STRING"), ("cover_blob_url", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
    ],
    "lh_vv_gold.dbo.gld_srv_poi_multi_lang": [
        ("poi_id", "STRING NOT NULL"), ("lang", "STRING NOT NULL"), ("poi_name", "STRING"), ("source_name", "STRING"),
        ("time_to_spend", "STRING"), ("best_time", "STRING"), ("cost", "STRING"), ("description", "STRING"),
        ("experience", "STRING"), ("story", "STRING"), ("local_tips", "STRING"),
        ("row_hash", "STRING"), ("created_at", "TIMESTAMP"), ("updated_at", "TIMESTAMP"), ("deleted_at", "TIMESTAMP"),
    ],
}
EDGES_KEEP = ("slv_poi_entity_non_enrich", "slv_enr_poi_destination", "slv_enr_poi_info_multi_lang",
              "slv_3p_poi_rating", "slv_3p_poi_review", "slv_poi_media_info")
EDGES_ON = [
    (1, "slv_3p_poi_price", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1),
]
LOCK = "oldprice-" + uuid.uuid4().hex


def _want(cols):
    return {name.lower(): (dtype.replace(" NOT NULL", "").lower(), "NOT NULL" not in dtype) for name, dtype in cols}


def _fields(fq):
    return {f.name.lower(): (f.dataType.simpleString(), f.nullable) for f in spark.table(fq).schema.fields}


def _names(fq):
    return [f.name.lower() for f in spark.table(fq).schema.fields]


def _edge_rows(trg_schema, trg):
    return [(r["pl_name"], r["src_schema"], r["src_tbl"], r["is_active"], r["priority"], r["load_mode"],
             r["nb_name"], r["n"]) for r in spark.sql(f"""
    SELECT pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name, count(*) AS n
    FROM {CFG}
    WHERE trg_schema = '{trg_schema}' AND trg_tbl = '{trg}'
    GROUP BY pl_name, src_schema, src_tbl, is_active, priority, load_mode, nb_name
    """).collect()]


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
    if "nb_name" not in {f.name.lower() for f in spark.table(CFG).schema.fields}:
        raise RuntimeError(f"{CFG} chưa có cột nb_name: chạy enrddlpy trước")

    # Dừng trước khi ghi: xét hết điều kiện, chưa ghi gì.
    issues = []
    plan = {}
    for fq, cols in TABLE_COLS.items():
        if not spark.catalog.tableExists(fq):
            issues.append(f"{fq} chưa có: chạy NB_SETUP_INITIAL_DDL trước")
            continue
        want, got = _want(cols), _fields(fq)
        new = {name for name, _dtype in NEW_COLS[fq]}
        for name, (dtype, _nullable) in want.items():
            if name in new:
                if name in got and got[name] != (dtype, True):
                    issues.append(f"{fq}.{name} là {got[name]}, cần {(dtype, True)}")
            elif name not in got:
                issues.append(f"{fq} thiếu cột {name}")
            elif got[name][0] != dtype:
                issues.append(f"{fq}.{name} là {got[name][0]}, cần {dtype}")
        extra = sorted(set(got) - set(want) - {OWNER_COL})
        if extra:
            issues.append(f"{fq} có cột ngoài hợp đồng {extra}, không sửa")
        plan[fq] = [(name, dtype) for name, dtype in NEW_COLS[fq] if name not in got]
    if not spark.catalog.tableExists(PRICE_FQ):
        issues.append(f"{PRICE_FQ} chưa có: chạy NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV trước")
    else:
        price = {name: dtype for name, (dtype, _nullable) in _fields(PRICE_FQ).items()}
        for name, dtype in PRICE_SRC:
            if price.get(name) != dtype:
                issues.append(f"{PRICE_FQ}.{name} là {price.get(name)}, cần {dtype}")
    owners = {pl for pl, _ss, _src, flag, *_rest in _edge_rows(SLV, "slv_3p_poi_price") if flag == 1}
    if owners != {PRICE_OWNER}:
        issues.append(f"slv_3p_poi_price phải do đúng {PRICE_OWNER} ghi, đang là {sorted(owners)}")
    keep = {(PL, SLV, src, 1, 1, "RECOMPUTE", "NB_GLD_SRV_POI_INFO") for src in EDGES_KEEP}
    new_edges = {(PL, SLV, src, 1, priority, mode, nb) for _q, src, _s, _t, mode, nb, priority in EDGES_ON}
    rows = _edge_rows(GLD, "gld_srv_poi_info")
    for pl, src_schema, src, flag, priority, mode, nb, n in rows:
        if pl != PL and flag == 1:
            issues.append(f"cạnh {src}->gld_srv_poi_info đang active ở {pl}")
        if pl == PL and ((pl, src_schema, src, flag, priority, mode, nb) not in keep | new_edges or n != 1):
            issues.append(f"Cell không tự bật / sửa cạnh: {pl} {src_schema}.{src} active={flag} "
                          f"priority={priority} mode={mode} nb={nb} n={n}")
    have_edges = {row[:7] for row in rows}
    if not keep <= have_edges:
        issues.append(f"thiếu cạnh gld_srv_poi_info: {sorted(keep - have_edges)}")
    if issues:
        raise RuntimeError("Dừng trước khi ghi: " + "; ".join(issues))

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

    added = []
    for fq, cols in plan.items():
        names = [name for name, _dtype in TABLE_COLS[fq]]
        for name, dtype in cols:
            _refresh_lock()
            spark.sql(f"ALTER TABLE {fq} ADD COLUMNS (`{name}` {dtype} AFTER `{names[names.index(name) - 1]}`)")
            added.append(f"{fq.rsplit('.', 1)[-1]}.{name}")
    values = ",\n    ".join(
        f"({seq}, '{src}', '{schema}', '{trg}', '{mode}', '{nb}', {priority})"
        for seq, src, schema, trg, mode, nb, priority in EDGES_ON
    )
    _refresh_lock()
    spark.sql(f"""
    INSERT INTO {CFG}
        (id, pl_name, src_schema, src_tbl, trg_schema, trg_tbl, is_active, priority, load_mode, align_path, dedup_order, nb_name)
    SELECT COALESCE((SELECT MAX(id) FROM {CFG}), 0) + t.seq, '{PL}', '{SLV}', t.src_tbl, t.trg_schema, t.trg_tbl,
           1, t.priority, t.load_mode, CAST(NULL AS STRING), CAST(NULL AS STRING), t.nb_name
    FROM VALUES
        {values}
    AS t(seq, src_tbl, trg_schema, trg_tbl, load_mode, nb_name, priority)
    WHERE NOT EXISTS (
        SELECT 1 FROM {CFG} c
        WHERE c.pl_name = '{PL}' AND c.src_schema = '{SLV}' AND c.src_tbl = t.src_tbl
          AND c.trg_schema = t.trg_schema AND c.trg_tbl = t.trg_tbl)
    """)

    # Sau khi ghi: chỉ xét phần cell thêm.
    problems = []
    drift = []
    for fq, cols in NEW_COLS.items():
        got, live = _fields(fq), _names(fq)
        names = [name for name, _dtype in TABLE_COLS[fq]]
        for name, dtype in cols:
            if got.get(name) != (dtype.lower(), True):
                problems.append(f"{fq}.{name} là {got.get(name)}")
            elif live.index(name) != live.index(names[names.index(name) - 1]) + 1:
                drift.append(f"{fq.rsplit('.', 1)[-1]}.{name}")
    active = {row[:7]: row[7] for row in _edge_rows(GLD, "gld_srv_poi_info") if row[3] == 1}
    want_active = {payload: 1 for payload in keep | new_edges}
    if active != want_active:
        problems.append(f"cạnh active là {active}, cần {want_active}")
    if problems:
        raise RuntimeError("Sau khi ghi: " + "; ".join(problems))
    if drift:
        print(f"WARN oldprice: cột có sẵn nhưng lệch vị trí {drift}; cell không tự dời")
    print(f"oldprice: +{added}; cạnh {sorted(src for _q, src, *_r in EDGES_ON)}")
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

### `NB_SETUP_INITIAL_DDL` edits

- `init_tables`, spec `lh_vv_gold.dbo.gld_srv_poi_info`:
  - After `('full_address', 'STRING', None),`, add `('old_address', 'STRING', None),`.
  - After `('review_count', 'INT', None),`, add `('price_level', 'INT', None),`, `('price_min', 'DECIMAL(18,2)', None),`, `('price_max', 'DECIMAL(18,2)', None),`.
- Spec `lh_vv_gold.dbo.gld_srv_poi_multi_lang`: after `('experience', 'STRING', None),`, add `('story', 'STRING', None),` and `('local_tips', 'STRING', None),`.
- `init_seed_ctrl`, after the `slv_poi_media_info → gld_srv_poi_info` row and before `]`:
  - `# [THÊM 26/11] 20261126-gld-srv-old-address-price-story: cạnh giá cho gld_srv_poi_info.`
  - `(_GLD30, _S, 'slv_3p_poi_price', _G, 'gld_srv_poi_info', 1, 1, 'RECOMPUTE', None, None, 'NB_GLD_SRV_POI_INFO'),`

### Mapping doc edits

`mapping_gld_srv_poi_info.md`:
- §1.1 `SPEC.inputs` bullet: add `price` = `slv_3p_poi_price`. Change the read-mode sentence to "`rating`, `review`, `media` và `price`: … không truyền `live_only`". Keep the substring "`media` = `slv_poi_media_info`".
- §1.1 `pl_name` bullet: add `slv_3p_poi_price` to the edge list.
- New §1.1 bullet, price: 1:1 LEFT JOIN, all sources, no `source_name` filter, NULL when no row, stop on duplicate, types `int` and `decimal(18,2)` kept with a type guard, metric `price_matched`, not in `required_inputs`.
- New §1.1 bullet, gold-only: the six columns are not in PostgreSQL or the API. The first run changes `row_hash` for every live row.
- New §1.6 bullet, `old_address` per invariant 2: `D-OLD-ADDR`, metrics `old_address_g1`, `old_address_g2`, `old_address_g3`, `old_address_null`.
- §1.2: insert a row after `full_address`, Source = the three groups (G1' / G2' / G3) and entity `house_number` and `street`, Type `string`, Transform "Chỉ gold (D-OLD-ADDR). Có dòng destination: coalesce ba nhóm …; không có dòng destination: null, kể cả partner. Không lấy full_address của entity", Target `old_address`.
- §1.2: insert three rows after `review_count`: `slv_3p_poi_price.price_level | integer`, `slv_3p_poi_price.price_min | decimal(18,2)`, `slv_3p_poi_price.price_max | decimal(18,2)`. Transform for each: "Chỉ gold. LEFT JOIN theo poi_id, mọi nguồn; không có dòng thì null; hơn một dòng thì dừng".

`mapping_gld_srv_poi_multi_lang.md`:
- New §1.1 bullet: `story` and `local_tips` come only from i18n through the same partner join. P1 non-partner is NULL. There is no fallback to enr on P1 or P2. Gold-only.
- §1.2: after `experience`, add `| P1: slv_pn_business_service_i18ns.story<br>P2: slv_pn_business_service_i18ns.story | string | P1: partner: story, không fallback; nguồn khác: null<br>P2: story, không fallback | story |`.
- §1.2: add the same row for `local_tips`.

### Test edits

Common one-line trim: insert `ids = ids[: ids.index("lgpnamepy") + 1]` immediately before each `assert ids[-10:] == [...]` that ends in `"lgpnamepy"`. The existing slice assertions then stay valid.

Constants for the new tests:
- `ML_FQ = "lh_vv_gold.dbo.gld_srv_poi_multi_lang"`.
- `OLDPRICE_INFO = [("old_address","STRING"),("price_level","INT"),("price_min","DECIMAL(18,2)"),("price_max","DECIMAL(18,2)")]`.
- `OLDPRICE_ML = [("story","STRING"),("local_tips","STRING")]`.
- `ML_BASE` = the current 13-tuple multi_lang contract: `poi_id STRING NOT NULL`, `lang STRING NOT NULL`, `poi_name`, `source_name`, `time_to_spend`, `best_time`, `cost`, `description`, `experience`, `row_hash`, `created_at TIMESTAMP`, `updated_at TIMESTAMP`, `deleted_at TIMESTAMP`. The remaining types are `STRING`.
- `PRICE_EDGE = (1, "slv_3p_poi_price", "lh_vv_gold.dbo", "gld_srv_poi_info", "RECOMPUTE", "NB_GLD_SRV_POI_INFO", 1)`.

## Verification

Local tests: named in the Main brief.

Runtime probes, run by the user on Fabric DEV:
- P1 (pre-flight, before publish): `SELECT count(*) FROM (SELECT poi_id FROM lh_vv_silver.dbo.slv_3p_poi_price WHERE deleted_at IS NULL GROUP BY poi_id HAVING count(*) > 1)`. Expect 0. A non-zero result means the info node will stop by design.
- R1: `DESCRIBE lh_vv_gold.dbo.gld_srv_poi_info` and `… gld_srv_poi_multi_lang` show the six columns with the right types, nullable, at the contract positions. `load_origin` is still present.
- R2: `SELECT source_name, count(*), count(price_level), count(price_min), count(price_max) FROM lh_vv_gold.dbo.gld_srv_poi_info WHERE deleted_at IS NULL GROUP BY 1`. The partner price counts are 0.
- R3: `SELECT count(*) FROM lh_vv_gold.dbo.gld_srv_poi_info i LEFT ANTI JOIN lh_vv_silver.dbo.slv_enr_poi_destination d ON i.poi_id = d.poi_id WHERE i.old_address IS NOT NULL`. Expect 0.
- R4: `SELECT count(*) FROM lh_vv_gold.dbo.gld_srv_poi_multi_lang WHERE coalesce(lower(trim(source_name)), '') <> 'partner' AND (story IS NOT NULL OR local_tips IS NOT NULL)`. Expect 0.
- R5: the node metrics `old_address_g1`, `old_address_g2`, `old_address_g3`, and `old_address_null` sum to the row count. `price_matched` is at most the count of Google plus other non-partner rows.
- R6: rerun `oldpricepy` and expect `+[]`. One active `slv_3p_poi_price → gld_srv_poi_info` edge exists. The next serving load succeeds with the PostgreSQL schema unchanged.
