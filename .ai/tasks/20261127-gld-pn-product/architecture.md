RESULT: PASS

## Main brief

### Decision
PASS. One RECOMPUTE lib node, `NB_GLD_SRV_PRODUCT_OFFER`, writes `lh_vv_gold.dbo.gld_srv_product_offer` (pk `product_id`). It unions a holiday branch and a hotel branch, then joins destination with a left join. It has 15 RECOMPUTE edges on `PL_VV_TRANS_SLV_TO_GLD_30M`: 3 L2 parents, 11 L1 tables and `slv_enr_poi_destination`. The lib requires inputs to equal the edges, and the L1 edges keep gold fresh when L1 changes. DDL goes in `NB_SETUP_INITIAL_DDL` plus an idempotent `NB_CREATE_DDL` patch cell. No probe blocks implementation. P-7 is a readiness stop before the edges are enabled.

### Invariants Main must preserve
- `INPUTS` lists exactly the 15 `slv_` roles of doc §17.1, each with one active `_GLD30` edge. No `gld_` read and no `ai_poi`.
- `pk=("product_id",)`, with no dedupe and no prefix. `hash_exclude=("is_active",)`, `soft_delete_set={"is_active": "false"}`, no `deleted_flag`, `write_mode="MERGE"`. The build emits `is_active=True` and no technical columns.
- `poi_id = uuid_md5(F.col("business_service_id"), F.lit(PARTNER))`. A NULL `business_service_id` keeps the row with a NULL `poi_id`.
- Destination is a LEFT JOIN that never changes the row count, and `destination_id` is copied unchanged. A duplicate `poi_id` among the build's own keys raises `QualityGateError`.
- The three prices are selected by name from L2: no decode, coalesce or cast. Hotel prices are `CAST(NULL AS DOUBLE)`. Only `price_level` uses `coalesce(marketing, original)` with `PRICE_TIERS`.
- Holiday `business_service_id`:
  - Count distinct ids over relation rows with `deleted = false`.
  - More than one id drops the product.
  - Exactly one id is taken.
  - No live relation rows: use the post's id.
  - Live rows that all have a NULL id: NULL, with no fallback.
- `variants_json` is never NULL (`[]` when empty) and is sorted by the `BY_ID` comparator. Every `to_json` passes `ignoreNullFields=false`, and hotel JSON uses `timeZone=UTC` plus the ISO format. No `current_*`, `rand`, `first`, or `valid_from`/`valid_to` comparison.
- `required_inputs=("sale", "room_offer")`. A branch with 0 rows after the U-04 drop raises before the write.
- Every lookup key in doc §3 I10 is unique, or `QualityGateError` is raised. Inputs pass `_require_types`, and the output passes `_require_types(out, OUT_TYPES)`.
- The `TABLE_SPECS` entry equals `gldprdddlpy` `TABLE_COLS` (31 columns, `product_id STRING NOT NULL`), and `PIPELINE_CONFIG_ROWS` contains `gldprdddlpy` `EDGES_ON`.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | notebooks/NB_GLD_SRV_PRODUCT_OFFER.ipynb (new) | `gldprdmd`, `gldprdparam`, `gldprdrun`, `gldprdres`, `gldprdexit` | Copy the `NB_SLV_PN_HOTEL_ROOM_OFFER` layout. Vietnamese markdown summary. | the file loads; `test_product_offer_node_spec` finds the cells |
| 2 | same | `gldprdbuild` constants | `PARTNER`, `PRICE_TIERS`, `AXES`, `AXIS_COLS`, `MAP_T`, `RAW_T`, `JSON_OPTS`, `HOTEL_JSON_OPTS`, `BY_ID`, `INPUTS`, `OUT_TYPES`, `TYPES` as literals (doc §17.1) | `test_product_offer_out_types_match_mapping`, `test_product_offer_axes`, `test_product_offer_json_options` pass |
| 3 | same | `gldprdbuild` `_require_types`, `_require_unique`, `_price_level`, `_sorted_json` | helpers per doc §17.1 | `test_product_offer_prices_passthrough` passes |
| 4 | same | `gldprdbuild` `_holiday` | steps 1–10 of doc §17.1 holiday branch | `test_product_offer_bsid_rule_static`, `test_product_offer_poi_id_literal` pass |
| 5 | same | `gldprdbuild` `_hotel` | steps 1–3 of doc §17.1 hotel branch | `test_product_offer_deterministic_no_sale_flag` passes |
| 6 | same | `gldprdbuild` `build`, `_spec`, `SPEC` | union, destination, type check, persist into `ctx.cached`, metrics, empty-branch raise; `SPEC` and `_spec()` agree | `test_product_offer_node_spec`, `test_product_offer_inputs_silver_only` pass |
| 7 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `TABLE_SPECS` | add the gold entry after `gld_srv_poi_review`, not last (`specs[-1]` must stay `slv_poi_entity_non_enrich`) | `test_columns_match_sources`, `test_poi_entity_columns_derived` pass |
| 8 | same | `init_plan` | count strings 22 → 23 | `test_table_inventory_matches_sources` passes |
| 9 | same | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` | comment `# [THÊM 28/11] 20261127-gld-pn-product` plus 15 rows after the pnl2edge rows, in `INPUTS` order | `test_pipeline_config_rows_match_sources` (99) passes |
| 10 | notebooks/NB_CREATE_DDL.ipynb | new `gldprdddlmd` + `gldprdddlpy` after `pnl2edgepy` | `mediaddlpy` pattern on `_GLD30`; literal `TABLE_COLS`, `EDGES_ON`, `SOURCES`, `PARENTS`; checks before writing (L2 parent edges active, schema, edges); create plus edge MERGE under the lease; check after writing for 15 edges | `test_product_offer_patch_guards`, `test_product_offer_ddl_matches_out_types`, `test_product_offer_edges_create_vs_init` pass |
| 11 | tests/test_gld_srv_product_offer_contract.py (new) | module | the 12 tests in doc §18 | file passes |
| 12 | tests/test_initial_ddl_contract.py | `test_table_inventory_matches_sources`, `test_columns_match_sources`, `test_pipeline_config_rows_match_sources` | read `gldprdddlpy`; counts 23 and 99 | file passes |
| 13 | .ai/tasks/20261127-gld-pn-product/evidence/probes/p7_gld_product_offer_readiness.sql (new) | file | P-7 (a)–(d), aggregates only | the user can run it read-only in DEV |

### Order and stop points
1. Set `scope.files` in `task-state.yaml` to the 6 paths in doc §17.
2. Rows 1–6, the notebook.
3. Rows 7–10, DDL and edges.
4. Rows 11–12, the tests. Run local verification.
5. Row 13, the probe file.
6. STOP for evidence: the user runs P-7 in Fabric DEV, and the results go to `evidence/results/p7_gld_product_offer_readiness.txt`.
   - If any (a) count is above 0, or (b) is 0, or (d) shows missing or inactive L2 parents: STOP for a user decision (fix the data or change the mapping). Do not enable the edges.
7. Publish the notebook, then run `NB_CREATE_DDL` cell `gldprdddlpy`.
8. STOP for evidence: after the first `_GLD30` cycle, run V1–V7 (doc §18) and record the results.

### Tests and verification
- `python -m pytest tests/test_gld_srv_product_offer_contract.py tests/test_initial_ddl_contract.py tests/test_slv_pn_product_l2_contract.py -q`
- `python -m pytest tests -q`
- New tests:
  - `test_product_offer_node_spec`
  - `test_product_offer_inputs_silver_only`
  - `test_product_offer_out_types_match_mapping`
  - `test_product_offer_ddl_matches_out_types`
  - `test_product_offer_poi_id_literal`
  - `test_product_offer_prices_passthrough`
  - `test_product_offer_deterministic_no_sale_flag`
  - `test_product_offer_json_options`
  - `test_product_offer_bsid_rule_static`
  - `test_product_offer_axes`
  - `test_product_offer_edges_create_vs_init`
  - `test_product_offer_patch_guards`
- Edited tests: `test_table_inventory_matches_sources` (23), `test_columns_match_sources`, `test_pipeline_config_rows_match_sources` (99).
- Runtime checks V1–V7 (doc §18):
  - V1: SUCCESS with metrics.
  - V2: row counts against L2.
  - V3: unique `product_id`.
  - V4: prices EXCEPT against L2.
  - V5: `destination_id` EXCEPT.
  - V6: forced rerun gives 0 updates.
  - V7: `variants_json` parses, and the hotel timestamp format is right.

### Read only if needed
- §0 Why PASS, §16 Open questions and P-7 → stops 6 and 8, row 13
- §3 Invariants, §5 Grain and keys → rows 4–6
- §17.1 Build sketch → rows 2–6
- §17.2 DDL and edges → rows 7–10
- §6–§11 Ordering, commit, idempotency, concurrency, retry, partial failure → rows 6, 10
- §12 Observability → row 6 metric names
- §14 Rollout, §15 Rollback → stops 6–8
- §17.3 Alternatives → review challenges (edges, destination scope, sort, time zone)
- §18 Verification → rows 11–12

# Architecture — 20261127-gld-pn-product (round 2, one table)

This replaces the round-1 three-table document. Grain, keys, columns and lineage come from `model-design.md` (`## Entities and grain`, `## Keys`, `## Columns`, `## Lineage`) and `docs/context/mapping_gld_srv_product_offer.md` §1.1–§1.9. They are cited here, not restated.

## 0. Why PASS

- The ledger rows (D-A, U-01…U-08, D-0…D-10) and mapping §1 settle every business rule this node applies.
- `model-design.md` `## Conflicts and questions` items 1–4 belong to the architecture or the DDL, and this document decides them: §5 for nullability, §17.2 for edges, §3 for naming (kept). Items 5–8 are mapping questions 1–4. They stay open and are not closed here. The build applies the mapping's current behavior for them, and they change only values, never structure (§16).
- Every unknown runtime fact is enforced at run time and stops the job when it fails: lookup-key uniqueness, L1/L2 schema, and branch non-emptiness. Probe P-7 (§16) is a readiness check that runs before the edges are enabled. It does not block the design: whatever it returns, the code stays the same.
- `scope.files` is empty. The request delegates the edit domain to the paths in the Main brief. Main sets `scope.files` to the §17 list before editing. No `FILE:` block is emitted.

## 1. Scope

- One RECOMPUTE gold node, `NB_GLD_SRV_PRODUCT_OFFER`, writes `lh_vv_gold.dbo.gld_srv_product_offer` through `NB_LIB_TRANSFORM_SLV_GLD` (`NodeSpec` / `run_node` / `finish_node`). The cell layout copies `NB_SLV_PN_HOTEL_ROOM_OFFER`.
- DDL in `NB_SETUP_INITIAL_DDL` (`TABLE_SPECS`, `init_plan` counts, `PIPELINE_CONFIG_ROWS`) and an idempotent patch cell pair in `NB_CREATE_DDL` after `pnl2edgepy`.
- 15 RECOMPUTE edges on `PL_VV_TRANS_SLV_TO_GLD_30M`.
- Contract tests, plus readiness probe P-7.

## 2. Non-goals

- No change to silver L1 or L2, no destination or `poi_id` on silver, and no change to the L2 price decoder (D-1 is a separate task).
- No read of any gold table or of `ai_poi`. No destination remap, no fallback constant, no translation or name generation.
- No sale flag from `valid_from` / `valid_to` (U-07), and no `is_bookable` gate (D-8).
- No change to `NB_LIB_TRANSFORM_SLV_GLD`, to PostgreSQL serving, or to the data-serving API.
- Mapping questions 1–4 are not answered.

## 3. Invariants

- I1. The node reads exactly the 15 silver roles in §17.1 `INPUTS`, and each has one active `_GLD30` edge (the lib requires inputs equal to edges). No `gld_` and no `ai_poi`.
- I2. Grain is one row per `product_id`, with `pk=("product_id",)`. The build never deduplicates or prefixes. A duplicate after the union fails through the lib `pk_duplicate` check (D-0).
- I3. `poi_id = uuid_md5(F.col("business_service_id"), F.lit(PARTNER))` with `PARTNER = "partner"`. A bare `"partner"` would resolve as a column. A NULL `business_service_id` gives a NULL `poi_id`, and the row is kept (D-4).
- I4. `destination_id` comes from a LEFT JOIN on `poi_id` and is copied as the same string (D-5). The join never changes the row count. A `poi_id` that appears more than once in `slv_enr_poi_destination` among this build's keys raises `QualityGateError` before the write (mapping §1.7).
- I5. `original_price`, `marketing_price` and `markup_percent` are selected by name from `slv_pn_product_sale`, with no decode, coalesce or cast. Hotel rows get `CAST(NULL AS DOUBLE)` (U-06, D-1, Q-15). Only `price_level` reads `coalesce(marketing_price, original_price)`.
- I6. Holiday `business_service_id` follows the steps of mapping §1.7, in that order:
  - Relation rows with `deleted = false` are counted first, as distinct non-NULL ids.
  - More than one distinct id drops the product.
  - Exactly one id is taken.
  - With no live relation rows, the id comes from the post.
  - When live relation rows exist but all their ids are NULL, the result is NULL with no post fallback.
- I7. `variants_json` is never NULL (`[]` when empty). Elements are sorted by `variant_id` with a comparator, because the default `array_sort` cannot order a struct that holds a map. Every `to_json` passes `ignoreNullFields=false`. Hotel timestamps are rendered by the `to_json` options `timeZone=UTC` and `timestampFormat=yyyy-MM-dd'T'HH:mm:ss'Z'`. The build uses no `current_*`, `rand` or `first`.
- I8. `required_inputs=("sale", "room_offer")`. If either branch produces 0 rows after the U-04 drop, the build raises before MERGE (mapping §1.1).
- I9. Write semantics:
  - `hash_exclude=("is_active",)`, `soft_delete_set={"is_active": "false"}`, `deleted_flag=None`, `write_mode="MERGE"`.
  - The build emits `is_active = true` and never emits `row_hash`, `created_at`, `updated_at` or `deleted_at`.
  - The build output types equal `OUT_TYPES`, and `OUT_TYPES` equals the DDL.
- I10. These lookup keys must be unique, or the build raises:
  - (`product_id`, `locale`) of `slv_pn_product_translations` for `en` and `vi`
  - (`variant_id`) of `slv_pn_product_variant_translations` for `vi`
  - `id` of `slv_pn_products`, `slv_pn_product_posts`, `slv_pn_hotel_room_types`, `slv_pn_hotel_rate_plans`
  - `id` of `slv_pn_product_variants` with `deleted = false` (mapping §1.3: one element per `variant_id`)
  - `poi_id` of `slv_enr_poi_destination`, scoped as in I4

  The axis label lookups are not checked (mapping §1.1).

Naming: `model-design.md` conflict 3 is kept as is. D-9 locks the column names, and U-01 locks the table name.

## 4. State ownership

| state | owner | this task |
|---|---|---|
| L1 `slv_pn_*` (11 tables read) | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` on `_FL00` | read only, pinned |
| L2 `slv_pn_product_sale`, `slv_pn_hotel_room_offer`, `slv_pn_hotel_rate_offer` | `NB_SLV_PN_*` nodes on `_GLD30` | read only, DAG parents |
| `slv_enr_poi_destination` | enrichment DOC flow | read only, pinned, `live_only=False` |
| `gld_srv_product_offer`, including technical columns | this node through the lib MERGE | sole writer |
| 15 `ctrl_mng_pipeline_config` rows | `NB_SETUP_INITIAL_DDL` / patch cell `gldprdddlpy` | insert only |
| edge watermarks, `ctrl_log_table_run` | lib orchestrator | unchanged |

## 5. Grain and keys

See `model-design.md` `## Entities and grain` and `## Keys`. Engineering consequences:

- **Driver joins keep the row count.** Holiday is `sale` LEFT JOIN `products`, `posts`, aggregated relation and variant frames. Hotel is `room_offer` LEFT JOIN `room_types`, then rate plans aggregated per `business_service_id`. Every right side is unique on the join key, either through I10 or because it is aggregated first. The row count therefore equals the driver count, minus the U-04 drop on holiday.
- **L1 joins are 1:1 in practice.** L2 and L1 are read in the same pinned slice (§6). A live L2 row implies its L1 row exists. A missing row is impossible by construction, but it is counted (`room_type_missing`, `product_missing`, `rate_plan_missing`) instead of being failed, because the mapping states no such failure.
- **Nullability.** DDL declares `product_id STRING NOT NULL`, the same as other gold PKs (`media_id`, `poi_id`). Every other column, including the four technical columns, is nullable, following the existing gold DDL pattern. This closes `model-design.md` conflict 4 without changing a rule.

## 6. Ordering

- The DAG has three L2 edges, so `plan_run` makes the three L2 nodes parents. runMultiple starts the gold node after they succeed. A failed parent prevents this node from running.
- External inputs are pinned once per run in `plan.pinned`: the 11 L1 tables and `slv_enr_poi_destination`. The L2 parents and this node read the same L1 versions. `gld_srv_poi_info` reads the same pinned `slv_enr_poi_destination`, so both gold tables see the same `destination_id` within a run.
- Build order follows mapping §1.1: holiday, then hotel, then `poi_id` and destination, then checks, then union, then lib hash and MERGE.

## 7. Transaction and commit boundaries

- There is one Delta MERGE commit per run, written by `run_node`. Every check (types, uniqueness, empty branch, destination duplicates, lib quality gate) raises before that commit.
- Edge watermarks advance only after SUCCESS is logged (lib).
- The patch cell commits the table creation and the edge MERGE as two statements under the flow lease. Its post-write check fails loudly. A re-run converges because both statements are idempotent.

## 8. Idempotency

- The table is fully recomputed and merged on `row_hash`. Re-running on the same pins writes no rows (mapping §1.9).
- Hash stability rests on sorted arrays (comparator and `array_sort`), the fixed key order of `product_attributes`, UTC timestamp rendering, and `max()` over a single distinct relation id. No nondeterministic expression is used.
- Holiday `attributes` maps keep the source key order. The same input string gives the same output. A source that re-serializes keys in another order would only cause a no-op content update. Sorting the keys was rejected because the mapping says to keep `attributes` raw (D-6).
- The patch cell uses `CREATE TABLE IF NOT EXISTS` with a pre-write schema check and an edge `MERGE … WHEN NOT MATCHED THEN INSERT`, so a re-run is a no-op.

## 9. Concurrency

- Only the lib MERGE writes the table, and one node instance runs per pipeline under the `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` lock. Upstream commits during a run are isolated by the pins.
- The patch cell takes and refreshes the same lease before every write (`mediaddlpy` / `pnl2edgepy` pattern) and releases it in `finally`.

## 10. Retry and recovery

- runMultiple retry is 0. The edges stay dirty, so the next 30-minute cycle re-plans and recomputes. `p_force` reruns the node by hand.
- Every failure happens before the commit (§7), so a retry never repeats a partial write.

## 11. Partial failure

| failure | effect | recovery |
|---|---|---|
| L2 parent fails | this node is skipped; the table stays at its last version | next cycle |
| `sale` or `room_offer` empty (lib `required_inputs`) | FAILED, no write; prevents a mass soft delete | fix upstream |
| a branch has 0 rows after U-04 | `QualityGateError`, no write | inspect `dropped_multi_bsid` |
| L1/L2 schema drift | `_require_types` raises `ConfigError` | align DDL |
| lookup key duplicate (I10) | `QualityGateError` naming the table and count | fix the source or change the mapping (user) |
| destination duplicate among keys | `QualityGateError` | enrichment data |
| `slv_enr_poi_destination` empty | not required; every `destination_id` is NULL and `no_destination` rises | enrichment flow |
| union `product_id` collision | lib `pk_duplicate` blocks | D-0 holds today (P-1 = 0); a collision needs a user decision |

## 12. Observability

Mapping §1.1 metrics go to `ctx.metrics` and the run log:

- `holiday_rows`, `hotel_rows`
- `dropped_multi_bsid`, `null_business_service_id`, `relation_null_bsid_only`
- `no_destination` (`poi_id IS NOT NULL AND destination_id IS NULL`)
- `empty_variants_holiday`, `empty_variants_hotel`
- `variant_attributes_unparsed`
- `null_price_with_post`

Integrity warnings go to `ctx.warn` and are expected to be 0: `product_missing`, `room_type_missing`, `rate_plan_missing`.

The lib quality-gate JSON adds `pk_null`, `pk_duplicate` and the diff counts. None of these metrics fails the job.

## 13. Security

Not applicable: lakehouse-internal reads and writes, no secrets, no external calls, no new identity.

## 14. Rollout

1. Main implements and runs the local tests (§18).
2. STOP for evidence: the user runs P-7 in Fabric DEV, and the results go to `evidence/results/p7_gld_product_offer_readiness.txt`. If any lookup key is duplicated, the first run fails by design. The user then decides whether to fix the data or change the mapping before step 4.
3. Publish `NB_GLD_SRV_PRODUCT_OFFER`.
4. Run the `NB_CREATE_DDL` cell `gldprdddlpy`. It creates the table and the 15 active edges and verifies them after writing.
5. On the next `_GLD30` cycle, run checks V1–V7 (§18).

The table has no readers yet (the serving API reads only `gld_srv_poi_*`), so publishing it carries no consumer risk.

## 15. Rollback and forward recovery

- **Rollback:** `UPDATE lh_vv_ctrl.dbo.ctrl_mng_pipeline_config SET is_active = 0 WHERE trg_schema = 'lh_vv_gold.dbo' AND trg_tbl = 'gld_srv_product_offer'` under the flow lease. The table is kept but not published. No DROP is used.
- **Forward recovery:** fix the notebook and rerun with `p_force`. Because the MERGE converges, a wrong table is fully rebuilt. If a DDL change is ever needed, it is an additive patch cell, never a drop.

## 16. Open questions (non-blocking) and probe P-7

These are kept open and are not decided here:

- Mapping Q1: whether variant attribute values are value codes. If they are not, the six axis columns are NULL.
- Mapping Q2: the epoch unit of `valid_from` / `valid_to`. Gold formats the L2 timestamp as it is.
- Mapping Q3: room `tags` / `amenities` are copied as strings.
- Mapping Q4: the D-1 decoder task.
- OQ-5 (new, for the mapping owner): mapping §1.2–§1.4 filter `deleted` only on variants and relation. Translation and attribute lookups read every row, so a deleted translation can supply `name`, and a deleted-plus-live pair fails I10. The build follows the mapping literally. P-7 (c) measures the effect.

P-7 is read-only Spark SQL and returns aggregates only. Main writes it to `evidence/probes/p7_gld_product_offer_readiness.sql`.

- (a) Lookup duplicates. One `SELECT '<name>' t, count(*) n FROM (SELECT <keys> FROM <tbl> [WHERE <filter>] GROUP BY <keys> HAVING count(*) > 1)` per I10 key, combined with UNION ALL. Destination is checked among partner keys: `poi_id IN (SELECT K(business_service_id) FROM slv_pn_hotel_room_types UNION SELECT K(business_service_id) FROM slv_pn_product_business_service_relation UNION SELECT K(business_service_id) FROM slv_pn_product_posts)`, where `K(x) = regexp_replace(md5(concat(x,'partner')),'^(.{8})(.{4})(.{4})(.{4})(.{12})$','$1-$2-$3-$4-$5')`. Pass: every `n = 0`.
- (b) Branch sizes: `count(*)` of `slv_pn_product_sale` and `slv_pn_hotel_room_offer` `WHERE deleted_at IS NULL`. Pass: both are above 0.
- (c) OQ-5: `count_if(deleted)` on `slv_pn_product_translations`, `slv_pn_product_variant_translations`, `slv_pn_product_attributes`, `slv_pn_product_attribute_values`, `slv_pn_product_attribute_value_translations`. This is information only.
- (d) Schema and parents: `DESCRIBE TABLE` on the three L2 tables, plus `SELECT pl_name, src_tbl, trg_tbl, is_active FROM lh_vv_ctrl.dbo.ctrl_mng_pipeline_config WHERE trg_tbl IN ('slv_pn_product_sale','slv_pn_hotel_room_offer','slv_pn_hotel_rate_offer')`. Pass: 5 active `_GLD30` rows, with types matching §17.1 `TYPES`.

## 17. Implementation plan

`scope.files`:

- `notebooks/NB_GLD_SRV_PRODUCT_OFFER.ipynb` (new)
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb`
- `notebooks/NB_CREATE_DDL.ipynb`
- `tests/test_gld_srv_product_offer_contract.py` (new)
- `tests/test_initial_ddl_contract.py`
- `.ai/tasks/20261127-gld-pn-product/evidence/probes/p7_gld_product_offer_readiness.sql` (new)

### 17.1 Build sketch (cell `gldprdbuild`)

Cells:

- `gldprdmd`: Vietnamese summary.
- `gldprdparam`: the same 8 parameters as the L2 nodes.
- `gldprdrun`: `%run NB_LIB_TRANSFORM_SLV_GLD`.
- `gldprdbuild`
- `gldprdres`: `RES = run_node(SPEC, …)`, same argument list as the L2 nodes.
- `gldprdexit`: `notebookutils.notebook.exit(finish_node(RES))`.

Comments are in Vietnamese (AGENTS §1). `_require_types` is copied from the L2 cells (existing pattern).

Constants. Each one is a literal so tests can `ast.literal_eval` it.

```python
PARTNER = "partner"
PRICE_TIERS = ((500000, 1), (2000000, 2), (5000000, 3))        # còn lại 4; NULL -> 0 (mapping §1.2)
AXES = {"holiday:swticket": "variant_tickets", "holiday:use_date": "variant_dates",
        "holiday:hotel": "variant_hotels", "holiday:quantity": "variant_age_groups",
        "holiday:age_group": "variant_age_groups", "holiday:zone": "variant_room_types",
        "holiday:depature": "variant_departures"}
AXIS_COLS = ("variant_tickets", "variant_dates", "variant_hotels", "variant_age_groups",
             "variant_room_types", "variant_departures")
MAP_T = "map<string,string>"
RAW_T = ("struct<shortDescription:string,translations:array<struct<languageCode:string,"
         "shortDescription:string>>,tags:array<struct<label:string,code:string>>>")
JSON_OPTS = {"ignoreNullFields": "false"}
HOTEL_JSON_OPTS = {"ignoreNullFields": "false", "timeZone": "UTC", "timestampFormat": "yyyy-MM-dd'T'HH:mm:ss'Z'"}
BY_ID = "(l, r) -> CASE WHEN l.variant_id < r.variant_id THEN -1 WHEN l.variant_id > r.variant_id THEN 1 ELSE 0 END"
INPUTS = {"sale": "slv_pn_product_sale", "room_offer": "slv_pn_hotel_room_offer",
          "rate_offer": "slv_pn_hotel_rate_offer", "products": "slv_pn_products",
          "product_tr": "slv_pn_product_translations", "variants": "slv_pn_product_variants",
          "variant_tr": "slv_pn_product_variant_translations", "attributes": "slv_pn_product_attributes",
          "attribute_values": "slv_pn_product_attribute_values",
          "attribute_value_tr": "slv_pn_product_attribute_value_translations",
          "posts": "slv_pn_product_posts", "relation": "slv_pn_product_business_service_relation",
          "room_types": "slv_pn_hotel_room_types", "rate_plans": "slv_pn_hotel_rate_plans",
          "destination": "slv_enr_poi_destination"}
OUT_TYPES = {"product_id": "string", "name": "string", "lang": "string", "product_type": "string",
             "is_active": "boolean", "is_bookable": "boolean", "product_line": "string", "price_level": "int",
             "original_price": "double", "marketing_price": "double", "markup_percent": "double",
             "variant_count": "bigint", "active_variant_count": "bigint", "variants_json": "string",
             "variant_tickets": "string", "variant_dates": "string", "variant_hotels": "string",
             "variant_age_groups": "string", "variant_room_types": "string", "variant_departures": "string",
             "variant_statuses": "string", "product_attributes": "string", "business_service_id": "string",
             "source_id": "string", "product_post_id": "string", "poi_id": "string", "destination_id": "string"}
```

`TYPES[role]` gives the expected input types per role:

| role | expected types |
|---|---|
| `sale` | `product_id`, `product_post_id` string; three prices double; `is_bookable` boolean |
| `room_offer` | `room_type_id`, `status`, `view_type` string; `available_rooms`, `max_occupancy`, `adult_capacity`, `child_capacity` int; `is_bookable` boolean |
| `rate_offer` | `rate_plan_id`, `status` string; `meal_plan` int; `valid_from`, `valid_to` timestamp |
| `products` | `id`, `product_line` string |
| `product_tr` | `product_id`, `locale`, `name` string |
| `variants` | `id`, `product_id`, `status`, `attributes` string; `deleted` boolean |
| `variant_tr` | `variant_id`, `locale`, `name` string |
| `attributes` | `id`, `code` string |
| `attribute_values` | `id`, `attribute_id`, `code` string |
| `attribute_value_tr` | `attribute_id`, `locale`, `name` string |
| `posts` | `id`, `business_service_id`, `raw_sync_data` string |
| `relation` | `product_id`, `business_service_id` string; `deleted` boolean |
| `room_types` | `id`, `name`, `description`, `tags`, `amenities`, `business_service_id` string; `max_extra_bed`, `room_size`, `total_rooms` int |
| `rate_plans` | `id`, `business_service_id`, `name`, `kind` string; `include_tax`, `include_service_charge` boolean |
| `destination` | `poi_id`, `destination_id` string |

Helpers:

- `_require_unique(df, keys, name)`: `df.groupBy(*keys).count().where("count > 1").count()`. Above 0 raises `QualityGateError(f"gld_srv_product_offer: {name} trùng khoá {keys}: {n}")`.
- `_price_level(p)`: chains `F.when` over `PRICE_TIERS`; `F.when(p.isNull(), 0)` first; `.otherwise(4)`; `.cast("int")`.
- `_sorted_json(col, opts)`: `F.when(col.isNull(), F.lit("[]")).otherwise(F.to_json(F.expr(f"array_sort({name}, {BY_ID})"), opts))`. Apply it to a named column.

Holiday branch, `_holiday(ctx)`:

1. Read `sale` (live), `products`, `product_tr`, `variants`, `variant_tr`, `attributes`, `attribute_values`, `attribute_value_tr`, `posts`, `relation`. Run `_require_types` on each, and `_require_unique` per I10.
2. Relation aggregate: `rel.where(F.col("deleted") == F.lit(False)).groupBy("product_id").agg(count(lit(1)) "_rel_rows", countDistinct("business_service_id") "_rel_n", max("business_service_id") "_rel_bsid")`.
3. `base = sale` LEFT `rel_agg` on `product_id`, then LEFT `posts.select(id→product_post_id, business_service_id→_post_bsid, raw_sync_data)` on `product_post_id`. `dropped = base.where("_rel_n > 1")`. `base = base.where("coalesce(_rel_n, 0) <= 1")`.
4. `business_service_id = F.when(F.col("_rel_rows").isNull(), F.col("_post_bsid")).when(F.col("_rel_n") == 1, F.col("_rel_bsid"))`, which is NULL otherwise.
5. Live variants are `variants.where(deleted == False)`. Join them LEFT to `variant_tr` (`locale = 'vi'`) on `variant_id = id`. `_attrs = F.when(attributes.isNull(), F.from_json(F.lit("{}"), MAP_T)).otherwise(F.from_json("attributes", MAP_T))`. `_unparsed = attributes IS NOT NULL AND _attrs IS NULL`.
6. Aggregate by `product_id`:
   - `_v`: `collect_list(struct(id AS variant_id, _vname AS name, status, _attrs AS attributes))`
   - `variant_count`: `count`
   - `active_variant_count`: `sum(status = 'active')` cast to long
   - `_st`: `array_sort(collect_set(status))`
   - `_unparsed`: `sum`
7. Axis:
   - Explode `_attrs` into (`attr_code`, `value_code`).
   - Join `attributes` on `code = attr_code`, which gives `_aid`.
   - Join `attribute_values` on (`attribute_id = _aid`, `code = value_code`), which gives `_vid`.
   - Join `attribute_value_tr` on (`attribute_id = _vid`, `locale = 'vi'`), which gives `_label`.
   - `_axis = element_at(create_map(AXES literals), attr_code)`.
   - Group by `product_id`. For each column `c` in `AXIS_COLS`, `array_sort(collect_set(when(_axis = c, _label)))`.
   - Output is `when(size > 0, to_json)`, NULL otherwise.
8. Name: LEFT join `product_tr` en and vi, then `coalesce(_en, _vi, product_id)`. `product_line` comes from LEFT `products` on `id`.
9. `product_attributes`:
   - Parse `raw_sync_data` with `F.from_json(raw_sync_data, RAW_T)` as `r`.
   - `en = F.filter(r.translations, t -> t.languageCode.startswith("en"))`, and the same for `vi`.
   - `shortDescription = coalesce(when(size(en)>0, en[0].shortDescription), when(size(vi)>0, vi[0].shortDescription), r.shortDescription)`.
   - `tg = F.transform(r.tags, t -> coalesce(t.label, t.code))`, and `tags = when(size(tg) > 0, tg)`.
   - Write `to_json(struct(shortDescription, tags, price_level AS priceLevel, lit(True) AS isActive), JSON_OPTS)`. NULL `product_post_id` therefore gives null keys and keeps all four.
10. Select into `OUT_TYPES` order:
    - `lang = 'en'`, `product_type = 'other'`, `is_active = True`.
    - Prices are selected by name.
    - `variants_json = _sorted_json(_v, JSON_OPTS)`.
    - `variant_statuses = when(size(_st) > 0, to_json(_st))`.
    - `source_id = business_service_id.cast("string")`.
    - `poi_id = uuid_md5(F.col("business_service_id"), F.lit(PARTNER))`.

Hotel branch, `_hotel(ctx)`:

1. `plans = rate_offer` (live) LEFT `rate_plans.select(id→rate_plan_id, business_service_id, name→_pname, kind, include_tax, include_service_charge)`. Keep `business_service_id IS NOT NULL`. Group by `business_service_id`:
   - `_v`: `collect_list(struct(rate_plan_id AS variant_id, coalesce(_pname, rate_plan_id) AS name, status, struct(meal_plan, kind, valid_from, valid_to, include_tax, include_service_charge) AS attributes))`
   - `_n`: `count`
   - `_a`: `sum(status = 'Active')`
2. `rooms = room_offer` (live) LEFT `room_types.select(id→room_type_id, name, description, tags, amenities, max_extra_bed, room_size, total_rooms, business_service_id)`, then LEFT `plans` on `business_service_id`.
3. Columns:
   - `name = coalesce(name, room_type_id)`, `product_type = 'hotel'`, `product_line = 'accommodation'`, `price_level = 0`.
   - The three prices, the axis columns, `variant_statuses` and `product_post_id` are typed NULLs.
   - `variant_count = coalesce(_n, 0)` and `active_variant_count = coalesce(_a, 0)`, both long.
   - `variants_json = _sorted_json(_v, HOTEL_JSON_OPTS)`.
   - `product_attributes = to_json(struct(description AS shortDescription, tags, CAST(NULL AS INT) AS priceLevel, lit(True) AS isActive, max_occupancy AS maxOccupancy, adult_capacity AS adultCapacity, child_capacity AS childCapacity, max_extra_bed AS maxExtraBed, room_size AS roomSize, view_type AS viewType, amenities, available_rooms AS availableRooms, total_rooms AS totalRooms), JSON_OPTS)`.

`build(ctx)`:

```python
def build(ctx):
    hol, hol_stats = _holiday(ctx)                 # hol_stats: dropped_multi_bsid, variant_attributes_unparsed, product_missing
    hot, hot_stats = _hotel(ctx)                   # hot_stats: room_type_missing, rate_plan_missing
    rows = hol.select(*OUT_TYPES).unionByName(hot.select(*OUT_TYPES))
    des = ctx.input("destination", live_only=False)
    _require_types(des, TYPES["destination"], "slv_enr_poi_destination")
    keys = rows.where(F.col("poi_id").isNotNull()).select("poi_id").distinct()
    d = des.select("poi_id", "destination_id").join(keys, "poi_id", "left_semi")
    _require_unique(d, ("poi_id",), "slv_enr_poi_destination")          # I4: chỉ poi_id của bản build
    out = rows.drop("destination_id").join(d, "poi_id", "left").select(*OUT_TYPES)
    _require_types(out, OUT_TYPES, "gld_srv_product_offer")             # kiểu build = DDL
    out = out.persist(StorageLevel.MEMORY_AND_DISK)
    ctx.cached.append(out)                                               # lib unpersist sau run_node
    s = out.agg(<one F.sum(F.when(...)) per §12 metric, split by product_type>).first()
    ctx.metrics.update({**hol_stats, **<s as dict>})
    for name in ("product_missing", "room_type_missing", "rate_plan_missing"):
        ctx.warn(name, {**hol_stats, **hot_stats}[name])
    if not s["holiday_rows"] or not s["hotel_rows"]:
        raise QualityGateError(f"gld_srv_product_offer: nhánh rỗng holiday={s['holiday_rows']} hotel={s['hotel_rows']}")
    return out
```

```python
SPEC = NodeSpec(trg_tbl="gld_srv_product_offer", inputs=INPUTS, pk=("product_id",), build=build,
                required_inputs=("sale", "room_offer"), hash_exclude=("is_active",),
                soft_delete_set={"is_active": "false"}, write_mode="MERGE")
```

A `_spec()` function returns the same values as a dict, the L2 test pattern.

- `rows.drop("destination_id")`: each branch emits `destination_id` as `CAST(NULL AS STRING)` so the union shape equals `OUT_TYPES`. The join then supplies the real value.
- The lib rejects void-typed columns, so every literal NULL must be cast.

### 17.2 DDL and edges

`TABLE_COLS` (DDL types) is `OUT_TYPES` mapped as string→`STRING`, boolean→`BOOLEAN`, int→`INT`, double→`DOUBLE`, bigint→`BIGINT`. `product_id` is `STRING NOT NULL`. Then come `row_hash STRING`, `created_at TIMESTAMP`, `updated_at TIMESTAMP`, `deleted_at TIMESTAMP`, for 31 columns.

- `NB_SETUP_INITIAL_DDL` `TABLE_SPECS`: add `{"fq": 'lh_vv_gold.dbo.gld_srv_product_offer', "partition": None, "comment": None, "props": PROPS, "cols": [...]}`. Insert it after the `gld_srv_poi_review` entry, not at the end. `test_poi_entity_columns_derived` reads `specs[-1]` as `slv_poi_entity_non_enrich`.
- `init_plan`: change the count strings from 22 to 23 (`len(fqs) != 23`, `TABLE_SPECS cần 23 fq duy nhất`).
- `init_seed_ctrl` `PIPELINE_CONFIG_ROWS`: after the `pnl2edge` rows, add the comment `# [THÊM 28/11] 20261127-gld-pn-product` and 15 rows `(_GLD30, _S, '<src>', _G, 'gld_srv_product_offer', 1, 1, 'RECOMPUTE', None, None, 'NB_GLD_SRV_PRODUCT_OFFER')`, in `INPUTS` value order. The total goes from 84 to 99.
- `NB_CREATE_DDL`: add a markdown cell `gldprdddlmd` and a code cell `gldprdddlpy` after `pnl2edgepy`. They copy `mediaddlpy`, with `PL = "PL_VV_TRANS_SLV_TO_GLD_30M"`. Literals:
  - `TABLE_COLS = {"lh_vv_gold.dbo.gld_srv_product_offer": [...]}`
  - `EDGES_ON = [(seq, src, "lh_vv_gold.dbo", "gld_srv_product_offer", "RECOMPUTE", "NB_GLD_SRV_PRODUCT_OFFER", 1), ...]` (15 rows)
  - `SOURCES` = the 11 L1 tables plus `slv_enr_poi_destination`
  - `PARENTS` = the 3 L2 names

  Before writing, under the lease, the cell stops on any of these:
  - `nb_name` is missing from the config table
  - a source table is missing
  - an L2 parent edge is not active on `PL`, or an existing L2 table lacks `row_hash` / `deleted_at`. An inactive parent would make the L2 table external and missing, and `plan_run` would raise for the whole pipeline.
  - the gold table exists with a schema different from `TABLE_COLS`
  - an edge for this target is active on another PL, or a matching edge is not exactly one active row with the same payload

  Writes:
  1. `_refresh_lock()`, then `CREATE TABLE IF NOT EXISTS … USING DELTA TBLPROPERTIES (PROPS)`.
  2. `_refresh_lock()`, then the edge MERGE `WHEN NOT MATCHED THEN INSERT`.

  After writing, it checks that the schema equals `TABLE_COLS` and that exactly 15 active edges exist for this target, equal to `EDGES_ON`. Locks are released in `finally`. No DROP, DELETE, TRUNCATE or ALTER.
- `pnl2edgepy` filters its checks on its own `TARGETS`, so the new edges do not break a re-run of it.

### 17.3 Alternatives

| option | verdict |
|---|---|
| Edges only for the three L2 tables plus destination (mapping question 5 wording) | Rejected. The lib requires `inputs` to equal the edges, and L1 changes to names, variants or relations would not mark gold dirty, so it would go stale. |
| Two tables (holiday, hotel) plus a view | Rejected: conflicts with U-01 and U-03. |
| D-SRV-21 destination tie rule (max `updated_at`, as in `gld_srv_poi_info`) | Rejected. Mapping §1.7 says a duplicate fails the job. |
| Destination uniqueness over the whole table | Rejected. The mapping's reason is row multiplication in this join. A duplicate on a Google `poi_id` this build never joins cannot multiply rows, and failing on it would couple partner products to Google enrichment quality. |
| `deleted_flag` instead of `soft_delete_set` | Rejected. Deletion comes from rows that are absent (L2 `live_only`, U-04), and mapping §1.2 pairs `is_active = false` with `deleted_at`. |
| `date_format` for `valid_from` / `valid_to` | Rejected. It depends on the session time zone. `to_json` with `timeZone=UTC` is deterministic. |
| Default `array_sort` on variant structs | Not possible: the holiday struct holds a map. A comparator on `variant_id` sorts both branches the same way. |
| Lib `unique_checks` for lookups | Not applicable: it runs on the build output, not on inputs. |
| Fail on a missing L1 row behind a live L2 row | Rejected as a new rule. The row is counted with `ctx.warn` instead. |

## 18. Verification

Local checks:

- `python -m pytest tests/test_gld_srv_product_offer_contract.py tests/test_initial_ddl_contract.py tests/test_slv_pn_product_l2_contract.py -q`
- `python -m pytest tests -q`

`tests/test_gld_srv_product_offer_contract.py` uses the `_cell`, `_func` and `_assign` helpers, copied from `test_slv_pn_product_l2_contract.py`:

- `test_product_offer_node_spec`: `_spec()` gives `trg_tbl`, `inputs == INPUTS` (15), `pk == ("product_id",)`, `required_inputs == ("sale", "room_offer")`, `hash_exclude == ("is_active",)`, `soft_delete_set == {"is_active": "false"}`, `deleted_flag` absent or None, `write_mode == "MERGE"`. The `SPEC = NodeSpec(` source uses the same names.
- `test_product_offer_inputs_silver_only`: every `INPUTS` value starts with `slv_`. The source has no `gld_` read and no `ai_poi`.
- `test_product_offer_out_types_match_mapping`: `list(OUT_TYPES)` equals the business columns of mapping §1.2, in order. `"row_hash"`, `"created_at"`, `"updated_at"` and `"deleted_at"` do not appear in the build output.
- `test_product_offer_ddl_matches_out_types`: `gldprdddlpy` `TABLE_COLS` equals `OUT_TYPES` mapped to DDL types, plus the 4 technical columns. `product_id` is NOT NULL.
- `test_product_offer_poi_id_literal`: `PARTNER == "partner"`, and the source contains `uuid_md5(F.col("business_service_id"), F.lit(PARTNER))`.
- `test_product_offer_prices_passthrough`: no `decode_price`, `b64decode` or `DECODE[`. No `coalesce`/`cast` wraps `"original_price"`, `"markup_percent"` or `"marketing_price"` except inside `_price_level`. `PRICE_TIERS == ((500000, 1), (2000000, 2), (5000000, 3))`.
- `test_product_offer_deterministic_no_sale_flag`: the build source has no `current_timestamp`, `current_date`, `rand(`, `F.first` or `now(`. No comparison operator is applied to `valid_from` / `valid_to`.
- `test_product_offer_json_options`: `JSON_OPTS["ignoreNullFields"] == "false"`. `HOTEL_JSON_OPTS` has `timeZone == "UTC"` and the mapping format. `BY_ID` compares `variant_id`. `array_sort(` uses `BY_ID`.
- `test_product_offer_bsid_rule_static`: the relation is filtered on `F.col("deleted") == F.lit(False)` before `countDistinct`, the post fallback is conditioned on `_rel_rows` being NULL, and the drop uses `_rel_n > 1`.
- `test_product_offer_axes`: `AXES` equals the mapping §1.4 table, including `holiday:depature`.
- `test_product_offer_edges_create_vs_init`: `gldprdddlpy` `EDGES_ON` equals the `PIPELINE_CONFIG_ROWS` rows whose `row[4] == "gld_srv_product_offer"`, with 15 rows, all `_GLD30`, all on `NB_GLD_SRV_PRODUCT_OFFER`.
- `test_product_offer_patch_guards`: the order is `Dừng trước khi ghi` < `_refresh_lock()` < `CREATE TABLE IF NOT EXISTS` < `WHEN NOT MATCHED THEN INSERT` < `Sau khi ghi`. `finally:` is present. Non-comment code has no `DROP`, `DELETE`, `TRUNCATE` or `ALTER`. The three L2 parent names and `slv_enr_poi_destination` appear.

Changes to `tests/test_initial_ddl_contract.py`:

- `test_table_inventory_matches_sources`: add `_assign(_cell(ddl, "gldprdddlpy"), "TABLE_COLS").keys()` and change the count from 22 to 23.
- `test_columns_match_sources`: compare the new fq name with `gldprdddlpy` `TABLE_COLS` and `PROPS`.
- `test_pipeline_config_rows_match_sources`: after the `pnl2edgepy` loop, add a loop over `gldprdddlpy` `EDGES_ON` with `gld`, and change the count from 84 to 99.

Runtime checks after the first cycle (stop 4):

- V1: `ctrl_log_table_run` shows SUCCESS with the §12 metrics.
- V2: `count(*) = holiday_rows + hotel_rows`. `holiday_rows` equals the live `slv_pn_product_sale` count minus `dropped_multi_bsid`. `hotel_rows` equals the live `slv_pn_hotel_room_offer` count.
- V3: `count(DISTINCT product_id) = count(*)`.
- V4: the three prices EXCEPT both ways against the live L2 rows on `product_id` return 0.
- V5: `destination_id` EXCEPT both ways against `slv_enr_poi_destination` on matched `poi_id` returns 0.
- V6: a second run with `p_force="true"` on the same pins gives `updated = 0, inserted = 0`.
- V7: `from_json(variants_json, 'array<struct<variant_id:string>>')` is not NULL on every row. Hotel `valid_from` matches `^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$` or is null.
