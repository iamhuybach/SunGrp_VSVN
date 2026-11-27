RESULT: PASS

## Main brief

### Decision
Add an opt-in `NodeSpec.deleted_flag` (default `None`) to `NB_LIB_TRANSFORM_SLV_GLD`. It drives `deleted_at` for ids that are still in the build, through a separate MERGE and diff branch. The old code path stays literally unchanged when the flag is `None`.
Build three node notebooks (`NB_SLV_PN_PRODUCT_SALE`, `NB_SLV_PN_HOTEL_ROOM_OFFER`, `NB_SLV_PN_HOTEL_RATE_OFFER`). Each uses build column `_is_deleted` and has no DDL (§2.1 rule 7).
Register 5 RECOMPUTE edges in `PL_VV_TRANS_SLV_TO_GLD_30M` (seed `init_seed_ctrl` plus patch cell `pnl2edgepy`). No `TABLE_SPECS` or registry rows.
Decode prices with a pure Python block wrapped in a UDF, so it can be tested locally. A flag that is NULL blocks QG; it is never coalesced.
Runtime proof is required: Main sets `runtime_required: true` and requests a runbook.

### Invariants Main must preserve
- When `deleted_flag is None`, `sql_merge_target` returns a byte-identical string. `add_row_hash` hashes the same columns. `quality_gate` returns the same block keys. `diff_counts` runs the existing body.
- `_is_deleted` is never in the target DDL, the INSERT/SET lists, or the `row_hash` struct.
- `_is_deleted` is boolean and non-null, or QG block `deleted_flag_null` fails the node before any write.
- The MERGE with the flag follows the I4 table exactly: first-seen `deleted_at` is kept; `deleted_at` goes back to NULL when the flag turns false; missing ids are soft-deleted and keep their business values; `updated_at` changes on any hash change and on every `deleted_at` flip (C-02).
- `diff_counts` with the flag counts a key exactly when one MERGE clause writes it. The "diff = 0 → skip MERGE" shortcut depends on this.
- `deleted_flag` combined with the owner col `load_origin`, a non-empty `soft_delete_set`, or `APPEND` raises `ConfigError`.
- The build has one row per L1 base id, including L1 `deleted = true`. The base entity is never filtered on `deleted`. Posts and variants are filtered on `deleted = false`.
- Build columns follow the model-design `## Columns` order, with `_is_deleted` last. A NULL price stays NULL. No `0` and no cast on the 1-1 columns. `valid_from` and `valid_to` are copied untouched.
- `is_bookable` is never NULL on product sale or room offer (coalesce to false, plus block `is_bookable_null`).
- Each target is owned only by `PL_VV_TRANS_SLV_TO_GLD_30M`. The patch cell refuses to write if any of the 5 L1 sources is missing.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | tests/test_slv_pn_product_l2_contract.py | `test_merge_default_sql_golden` | Record the current default SQL strings (with and without owner) as golden values before any lib edit | passes on the unmodified lib |
| 2 | notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb | `926a3f9c` `NodeSpec` | Add `deleted_flag: Optional[str] = None` after `write_mode` | `test_nodespec_deleted_flag_default` |
| 3 | same | `926a3f9c` `add_row_hash` | Flag validation errors; exclude the flag from hash cols | `test_add_row_hash_flag_rules` |
| 4 | same | `926a3f9c` `quality_gate` | Add `blocks["deleted_flag_null"]` only when the flag is set | `test_quality_gate_flag_null_block` |
| 5 | same | `926a3f9c` `diff_counts` + new `_diff_counts_flag` | Add `deleted_flag=None` param and delegate; flag predicates and 4 extra counts; reject owner col | `test_diff_counts_flag_branch` |
| 6 | same | `926a3f9c` `sql_merge_target` | Add `deleted_flag=None` param; flag branch before the existing return (full doc "sql_merge_target flag branch") | `test_merge_flag_*`, golden test still passes |
| 7 | same | `926a3f9c` `merge_target` + new `persist_schema` | Exclude the flag from `cols`; pass `spec.deleted_flag`; helper drops the flag field from the schema | `test_run_node_flag_wiring` |
| 8 | same | `926a3f9c` `run_node` | Reject APPEND with the flag; call `ensure_target(..., persist_schema(df.schema, spec), ...)`; call `diff_counts(..., spec.deleted_flag)`; fill `qg["delete_flag"]` | `test_run_node_flag_wiring` |
| 9 | same | markdown `191e1851` | One Vietnamese line on the flag branch | text present |
| 10 | notebooks/NB_SLV_PN_PRODUCT_SALE.ipynb | new cells `pnsalemd`…`pnsaleexit` | Pure `decode_price` block plus UDF; build; SPEC (full doc "Product sale build") | `test_l2_node_specs`, `test_price_decode_vectors`, `test_product_sale_build_static` |
| 11 | notebooks/NB_SLV_PN_HOTEL_ROOM_OFFER.ipynb | new cells `pnroommd`…`pnroomexit` | Build plus SPEC (full doc "Room and rate builds") | `test_room_offer_build_static` |
| 12 | notebooks/NB_SLV_PN_HOTEL_RATE_OFFER.ipynb | new cells `pnratemd`…`pnrateexit` | Build plus SPEC | `test_rate_offer_build_static` |
| 13 | notebooks/NB_SETUP_INITIAL_DDL.ipynb | `init_seed_ctrl` `PIPELINE_CONFIG_ROWS` | Append the 5 `_GLD30` rows (full doc "Registration") | `test_l2_edges_create_vs_init` |
| 14 | notebooks/NB_CREATE_DDL.ipynb | new `pnl2edgemd`, `pnl2edgepy` at end | Edge-only patch on the `srvcoverpy`/`mediaddlpy` template, with an L1-exists precheck | `test_l2_patch_cell_guards` |
| 15 | tests/test_slv_pn_product_l2_contract.py | new file | All tests in the full doc "Verification" table | all pass |
| 16 | tests/test_initial_ddl_contract.py | `test_pipeline_config_rows_match_sources` | Add a `pnl2edgepy` loop; 79 → 84 | passes |
| 17 | tests/test_enr_poi_contract.py | `test_dest_portal_patch_cell` | Replace the last-4 check with the slice `oldpricemd`..`destportalpy` and `ids[-2:] == ["pnl2edgemd","pnl2edgepy"]` | passes |
| 18 | tests/test_legacy_gold_poi_init_contract.py | `test_merge_target_passes_owner_only_when_column_present` | New call literal `sql_merge_target(fq, view, cols, spec.pk, spec.soft_delete_set, owner, spec.deleted_flag)` | passes |
| 19 | docs/context/NB_LIB_TRANSFORM_SLV_GLD.md | §4 §6 `NodeSpec` / `sql_merge_target` rows | Document the field and the branch | text present |
| 20 | docs/context/03_OPERATOR_GUIDE.md | §2.8 table | Add 3 rows (silver, key, `MERGE`, notebook) | text present |
| 21 | docs/context/mapping_slv_pn_product_l2.md | `## Câu hỏi cần chốt` items 1–3 | Mark them resolved with pointers; item 4 stays open | text present |

Main adds every path above to `scope.files`.

### Order and stop points
1. Row 1 golden test, run against the current lib. STOP (evidence): it must pass before row 2.
2. Rows 2–9 (lib), then the lib tests.
3. Rows 10–12 (nodes).
4. Rows 13–14 (registration) and rows 16–18.
5. Rows 15, 19–21. Run the full local verification.
6. STOP (gate): `local_verification`, then specialist review (sql-data, spark-runtime, state-correctness).
7. Set `runtime_required: true` and run `python scripts/vv.py run-author 20261127-slv-pn-product-l2-transform --kind runbook` (Rollout steps 2–5 and R1–R3).
8. STOP (evidence, user on Fabric DEV): lib-only import and unchanged GLD30/ENR runs → R1 scratch self-test → `pnl2edgepy` → manual DRY_RUN for each node → RUN → R2 forced rerun → R3 probe. Results go under `evidence/results/`.
9. STOP (user decision) only if R1–R3 fail or the user wants a pipeline other than `PL_VV_TRANS_SLV_TO_GLD_30M`.

### Tests and verification
```
python -m pytest tests/test_slv_pn_product_l2_contract.py tests/test_legacy_gold_poi_init_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q
python -m pytest -q
python scripts/vv.py verify 20261127-slv-pn-product-l2-transform
```
New tests: `test_merge_default_sql_golden`, `test_merge_flag_clause_order`, `test_merge_flag_excluded_from_columns`, `test_merge_flag_rejects_owner`, `test_diff_counts_flag_branch`, `test_nodespec_deleted_flag_default`, `test_add_row_hash_flag_rules`, `test_quality_gate_flag_null_block`, `test_run_node_flag_wiring`, `test_l2_node_specs`, `test_l2_out_cols_match_model_design`, `test_l2_excluded_columns_absent`, `test_price_decode_vectors`, `test_product_sale_build_static`, `test_room_offer_build_static`, `test_rate_offer_build_static`, `test_l2_edges_create_vs_init`, `test_l2_patch_cell_guards`.
Price vectors: `"EtZE"`,4 → 123.45; `"/w=="`,4 → -0.0001; `"AA=="`,4 → 0.0; `"1234"`,4 → 1234.0; `"12.5"`,2 → 12.5; `None`/`""`/`"true"`/`"false"`/`"@@"` → None.
Runtime (Fabric DEV): R1 scratch MERGE self-test over the 10 I4 transitions, with and without the flag, checking diff against `operationMetrics`; R2 a `p_force=true` rerun gives 0/0/0 and no commit; R3 read-only count invariants (full doc "Verification").

### Read only if needed
- "Invariants" (I4 table) → rows 5, 6, 15
- "Lib design", "sql_merge_target flag branch", "diff_counts flag branch" → rows 2–9
- "Node design", "Price decode pure block", "Product sale build", "Room and rate builds" → rows 10–12
- "Registration" → rows 13, 14, 16, 17
- "Selected design and alternatives" → why GLD30, why a UDF, why a QG block on a NULL flag, room `is_bookable` reading
- "Partial failure", "Rollout", "Rollback and forward recovery" → steps 7–8, the runbook
- "Verification" → rows 1, 15–18, R1–R3

# Architecture: 20261127-slv-pn-product-l2-transform

Inputs: `model-design.md` (grain, keys, columns, lineage), the `decision.md` ledger (C-01..C-06, Q-19..Q-24), `docs/context/mapping_slv_pn_product_l2.md`, the business-mapping architecture `## Selected design and alternatives` (option B) and `### Lib delete-flag MERGE contract`, and the current code in `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` cell `926a3f9c`. This design does not restate model design. It resolves the eight model-design questions that need an architecture answer (registration, flag name, nullability, JSON access) in the sections below.

## Scope

- Lib `NB_LIB_TRANSFORM_SLV_GLD` cell `926a3f9c`: one opt-in `NodeSpec.deleted_flag` that drives `deleted_at` for ids that are still in the build. Default `None`. With `None`, the generated SQL, hash, QG keys, diff and DDL stay exactly as they are today.
- Three node notebooks (C-03): `NB_SLV_PN_PRODUCT_SALE`, `NB_SLV_PN_HOTEL_ROOM_OFFER`, `NB_SLV_PN_HOTEL_RATE_OFFER`.
- Registration: 5 `ctrl_mng_pipeline_config` RECOMPUTE edges in `PL_VV_TRANS_SLV_TO_GLD_30M`. They go into `NB_SETUP_INITIAL_DDL` cell `init_seed_ctrl` and into one new patch cell pair at the end of `NB_CREATE_DDL`. No `TABLE_SPECS`, `TABLE_CONFIGS` or `ctrl_cfg_schema_registry` rows (see Registration decision).
- Contract tests, plus doc sync for the lib doc, the operator guide §2.8 and the L2 mapping open questions 1–3.

## Non-goals

- No change to the 13 L1 `slv_pn_product*` / `slv_pn_hotel*` tables or to the extract.
- No `EPOCH_S_TS` unit decision. `valid_from` and `valid_to` copy 1-1.
- No §1 / §5.2 amendment in `02_NAMING_CONVENTION.md`. C-02 and C-04 are local exceptions already in the ledger.
- No gold consumer, no PostgreSQL sync, no `variants_json`, LLM, destination, `source_id` or `poi_id`.
- No combination of `deleted_flag` with `load_origin` owner rows, with `soft_delete_set`, or with `write_mode = APPEND`. Each is rejected with `ConfigError` (fail closed). A later task may extend this.

## Invariants

- I1 Default path is unchanged. When `deleted_flag is None`, `sql_merge_target` returns a byte-identical string for every existing argument shape. `add_row_hash` hashes the same columns. `quality_gate` returns the same `blocks` keys. `diff_counts` runs today's code. `ensure_target` receives the same schema.
- I2 The flag is never persisted and never hashed. It is not in the target DDL, not in the MERGE `INSERT`/`UPDATE SET` lists, and not in the `row_hash` struct.
- I3 The flag column is boolean and non-null on every build row, or the node fails with QG block `deleted_flag_null` before any write.
- I4 State transitions per key, with flag on. `s` is the build and `t` the target. Model-design `## Columns`, rows `deleted_at`, and C-02:

| t state | s state | result |
|---|---|---|
| absent | present, flag false | insert, `deleted_at` NULL |
| absent | present, flag true | insert, `deleted_at` = now |
| live | flag false, same hash | no write |
| live | flag false, hash changed | update business, `updated_at` = now |
| live | flag true | update business, `deleted_at` = now, `updated_at` = now |
| deleted | flag true, same hash | no write. First `deleted_at` kept |
| deleted | flag true, hash changed | update business, `updated_at` = now, `deleted_at` kept |
| deleted | flag false | update business, `deleted_at` NULL, `updated_at` = now |
| live | absent | `deleted_at` = now, `updated_at` = now, business kept |
| deleted | absent | no write |

- I5 `diff_counts` counts a key as insert or update exactly when one MERGE clause would write it. If diff and MERGE disagree, the "diff = 0 → skip MERGE" shortcut drops writes.
- I6 Build output: exactly one row per L1 base id, including L1 `deleted = true`. The base L1 entity is not filtered on `deleted`. Posts and variants are filtered on `deleted = false` as the mapping says.
- I7 Column order of each build equals the model-design `## Columns` order. The flag is last. A NULL price stays NULL, and no `0` is substituted.
- I8 One writer per L2 table: one node, one active pl (`build_dag`), one flow lock.

## State ownership

| State | Owner | Writer |
|---|---|---|
| `lh_vv_silver.dbo.slv_pn_product_sale` / `slv_pn_hotel_room_offer` / `slv_pn_hotel_rate_offer` rows, `row_hash`, `created_at`, `updated_at`, `deleted_at` | lib MERGE via node | `run_node` → `merge_target` only |
| Edge mailbox `wm_e__<trg>__<src>` (5 rows) | NB_00 | `advance_edges` after node success |
| Flow lock `wm_flow__PL_VV_TRANS_SLV_TO_GLD_30M` | NB_00 / manual run | existing lock functions |
| Edge config rows | repo seed + patch cell | user runs `NB_CREATE_DDL` cell `pnl2edgepy` |
| L1 inputs | extract (`PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`) | read-only here |

`deleted_at` on L2 is derived state. It depends on L1 `deleted`, on L1 id presence, and on the target's own previous `deleted_at`, which keeps the first-seen timestamp. The target's own state is read only inside the MERGE condition. The build never reads the target (`reads_self = False`).

## Grain and keys

As in model-design `## Entities and grain` and `## Keys`: `product_id`, `room_type_id`, `rate_plan_id`. No surrogate key. `pk` in each `NodeSpec` is that single column. Uniqueness is enforced by lib QG `pk_null` / `pk_duplicate`. Variants are grouped by `product_id` and posts by `external_id` before the joins, so the join cannot fan out. QG `pk_duplicate` is the backstop.

## Ordering

- The three nodes are level-0 nodes with no dependencies among them. runMultiple may run them in parallel.
- Within a node the steps are: read L1 at the pinned versions (`p_pinned_json`, extract batch pin), then build, `add_row_hash`, QG, diff, `ensure_target`, and one MERGE.
- MERGE clause order matters. Delta takes the first `WHEN MATCHED` clause whose condition holds. The clauses are ordered: live/undelete, newly deleted, still deleted with a changed hash. The third clause is only reached when the flag is true and `t.deleted_at IS NOT NULL`.
- Rollout order: lib first, observed unchanged, then nodes, then the edge seed. See Rollout.

## Transaction and commit boundaries

- One Delta MERGE per node run is the only data commit. `current_timestamp()` is fixed within the statement, so on insert `created_at = updated_at = deleted_at`.
- `ensure_target` (CREATE / ADD COLUMNS) is a separate earlier commit. It is idempotent.
- Edge advance is a later ctrl commit by NB_00. If the advance is lost, the next run recomputes. See Idempotency.
- The patch cell writes ctrl config under the flow lock in one MERGE `WHEN NOT MATCHED THEN INSERT`, after a stop-before-write precheck.

## Idempotency

- The build is deterministic for fixed L1 versions. It has no `first()`, no `rand`, and no `current_*`. The Python UDF is pure. `get_json_object` and the joins are deterministic. The post join only keeps groups with exactly one live post.
- Rerunning with the same inputs gives the same `row_hash` and the same flag. Every key falls into a "no write" row of I4, so diff is 0 and there is no commit. The runtime check proves this with `p_force = true`.
- A MERGE retry after an unseen successful commit is a no-op, because inserted rows now match with an equal hash and flagged rows already carry `deleted_at`.
- The patch cell can be rerun. It inserts only missing edges by logical key and changes nothing that already matches.

## Concurrency

Not applicable beyond the existing model. Writes go through the pl flow lock, and the lock is refreshed before each MERGE attempt (`before_write`). Each table has a single owning node. The patch cell takes the same flow lock, using the `srvcoverpy` template.

## Retry and recovery

- MERGE uses the existing `with_retry` (transient only). This is safe by Idempotency.
- A failed node does not advance its edges, so the next GLD30 run recomputes it. Manual recovery is a node run with `p_force = true`.
- `ConfigError` (type drift on L1, invalid flag or spec combination) and `QualityGateError` are not retried. The node is FAILED and nothing is written.

## Partial failure

- One of the three nodes fails: the other two still commit. Each table stays at its last good version. There are no descendants to skip.
- L1 type drift: `_require_types` raises `ConfigError` before build. Nothing is written.
- L1 base table empty (reload): `required_inputs` blocks, so no mass soft-delete happens. Posts or variants empty: also required, so no mass NULL prices or mass `is_bookable = false`.
- An external input table is missing: `plan_run` raises `ConfigError` for the whole GLD30 run, which would stop serving nodes too. Mitigation: the patch cell refuses to seed unless all 5 L1 source tables exist. L1 tables are lib-created and are not dropped in normal operation.
- Flag NULL on any row: QG `deleted_flag_null` blocks the node.

## Observability

- `ctrl_log_table_run` (unchanged schema): `inserted`, `updated`, and `deactivated` (ids missing from the build only, same meaning as today).
- `qg_json.delete_flag` is present only when the flag is on: `insert_deleted`, `to_deleted`, `undeleted`, `deleted_changed`.
- `qg_json.blocks` gains `deleted_flag_null` only when the flag is on.
- Node warns: `post_match_none` (product has a key but no unique live post), `post_match_many` (a referenced `external_id` has more than one live post), `price_decode_null` (raw price not NULL, decoded NULL) on product sale. `room_status_null` on room offer.
- Runtime probe output is counts only (see Verification).

## Security

Not applicable: no secrets, no personal data. Prices are business data and are never printed by probes. Probe samples are limited to 50 rows and print no values.

## Selected design and alternatives

| Decision | Selected | Rejected and why |
|---|---|---|
| Delete for present ids | Lib `deleted_flag` (option B, already chosen). Separate MERGE string only when the flag is set | Custom node MERGE: duplicates hash, QG and log logic. Lib default: breaks Q-21 (see business-mapping option A) |
| Default-path safety | Branch at the top of `sql_merge_target` / `diff_counts`. Old code is literally untouched for `None` | One unified predicate with `_s_flag = false`: logically equal, but it changes the SQL text of every old node and cannot be proven byte-identical |
| Flag combos | Reject owner col, `soft_delete_set` and APPEND together with the flag | Defining the semantics now: no consumer needs it, and it would be untested |
| Flag NULL | QG block | `coalesce(flag, false)`: invents a rule. Neither the mapping nor the ledger gives one |
| Pipeline | `PL_VV_TRANS_SLV_TO_GLD_30M` | `_ENR_15M`: no enrich consumer, and it would use twice the F16 capacity. A new pl: needs a new Fabric pipeline and runbook for 5 edges. GLD30 already hosts the silver L2 node `slv_poi_media_info`, and future gold product nodes in GLD30 can read these tables (same cadence) |
| Registration | Edges only. No DDL | `TABLE_SPECS` DDL: §2.1 rule 7 says lib-created L2 nodes have no DDL. `ctrl_cfg_schema_registry` is the L1 extract registry, and L2 nodes are not registered there |
| Price decode | Pure Python `decode_price` in a `# BEGIN_PRICE_PURE` block, wrapped by `F.udf(DoubleType)` | Native `unbase64` + `conv`: unsigned only, overflows past 8 bytes, not lenient on invalid input, and cannot be tested locally because there is no Spark in `tests/`. The UDF cost is negligible at this volume. Precedent: `F.udf(legacy_hours)` |
| Flag build name | `_is_deleted` (§5.3 internal `_` prefix). `NodeSpec` field `deleted_flag` (name from option B) | `deleted`: clashes with the room-offer business column |
| JSON access | `F.get_json_object("metadata", "$.holiday_product_post_id")`. For a JSON string it returns the unquoted value, which matches the Q-24 probe's string compare | regexp extraction: fragile |
| Room `is_bookable` with NULL `status` | `coalesce(status = 'Active' AND available_rooms > 0 AND deleted = false, false)` plus warn `room_status_null`. The mapping defines the true-set exactly and states the flag is false for NULL `available_rooms`, so the flag is two-valued. NULL `deleted` cannot reach here because it also feeds the flag, which blocks | Leave NULL: contradicts the two-valued reading. Ask a question: no new rule is introduced |
| Nullability | Lib-created Delta columns are nullable. Non-null is enforced only where a rule gives it: QG `pk_null`, and block `is_bookable_null` on both `is_bookable` tables | DDL `NOT NULL`: there is no DDL by rule 7 |

## Lib design (cell `926a3f9c`)

`NodeSpec`: add `deleted_flag: Optional[str] = None` after `write_mode`, with the comment `# [THÊM 27/11] cột boolean của build, không lưu, không băm; điều khiển deleted_at cho id còn trong build`.

`add_row_hash`: when `spec.deleted_flag` is set, add errors when any of these hold: the flag column is missing; its type is not `BooleanType`; it is in `pk`; it is a tech name; `spec.soft_delete_set` is non-empty. Then `cols = [c for c in df.columns if c not in spec.hash_exclude and c != spec.deleted_flag]`. With `None`, the existing line is unchanged in effect.

`quality_gate`: only when the flag is set, add `blocks["deleted_flag_null"]` = count of `flag IS NULL`, through the existing agg.

New helper `persist_schema(schema, spec)` returns `StructType` without the flag field. `run_node` calls `ensure_target(trg_fq, persist_schema(df.schema, spec), node)`.

`merge_target`: `cols = [c for c in df.columns if c != "row_hash" and c != spec.deleted_flag]`, then `sql_merge_target(fq, view, cols, spec.pk, spec.soft_delete_set, owner, spec.deleted_flag)`.

`run_node`: after `load_mode` is read, raise `ConfigError` when `spec.deleted_flag` is set and `load_mode == "APPEND"`. Call `diff = diff_counts(df, trg_fq, spec.pk, spec.deleted_flag)`. When the flag is set, `res["qg"]["delete_flag"] = {k: diff[k] for k in ("insert_deleted", "to_deleted", "undeleted", "deleted_changed")}`. The MERGE-skip condition stays `inserted or updated or deactivated`. Flag transitions are counted in `inserted` / `updated`.

### sql_merge_target flag branch

Signature: `sql_merge_target(fq, view, cols, pk, soft_delete_set, owner_col=None, deleted_flag=None)`. All existing statements stay as they are. Insert the branch just before the existing `return`:

```python
    if deleted_flag:
        if owner_col:
            raise ConfigError(f"{fq}: deleted_flag không dùng chung với {owner_col}")
        if deleted_flag in cols:
            raise ConfigError(f"{fq}: cột cờ '{deleted_flag}' không được nằm trong cols")
        flag = f"s.`{deleted_flag}`"
        hash_changed = "t.`row_hash` IS NULL OR t.`row_hash` <> s.`row_hash`"
        keep = [x for x in upd if not x.startswith("t.`deleted_at`")]
        ins_vals[-1] = f"CASE WHEN {flag} THEN current_timestamp() ELSE CAST(NULL AS TIMESTAMP) END"
        return f"""
MERGE INTO {quote_name(fq)} AS t
USING {view} AS s
ON {on}
WHEN MATCHED AND NOT {flag} AND ({changed}) THEN UPDATE SET
    {nl.join(upd)}
WHEN MATCHED AND {flag} AND t.`deleted_at` IS NULL THEN UPDATE SET
    {nl.join(keep + ["t.`deleted_at` = current_timestamp()"])}
WHEN MATCHED AND {flag} AND ({hash_changed}) THEN UPDATE SET
    {nl.join(keep)}
WHEN NOT MATCHED THEN INSERT ({', '.join(ins_cols)})
VALUES ({', '.join(ins_vals)})
WHEN NOT MATCHED BY SOURCE AND {sd_when} THEN UPDATE SET
    {nl.join(sd)}
"""
```

`ConfigError` is defined in lib §2. Tests must put it in the exec namespace.

### diff_counts flag branch

Signature: `diff_counts(src, trg_fq, pk, deleted_flag=None)`. First line: `if deleted_flag: return _diff_counts_flag(src, trg_fq, pk, deleted_flag)`. After that the existing body is unchanged. `_diff_counts_flag` works like this:

- Target missing: `inserted = src.count()`, `insert_deleted` = count of the flag being true, every other count 0.
- If `OWNER_COL` is among the target columns, raise `ConfigError`. This mirrors the MERGE rejection and also covers DRY_RUN.
- Full outer join on `pk` with `_s_hash`, `_s_flag`, `_s_in`, `_t_hash`, `_t_del`, `_t_in`. Let `hc = _t_hash IS NULL OR _t_hash <> _s_hash` and `both = _s_in AND _t_in`.
  - `inserted` = `_s_in AND NOT _t_in`. `insert_deleted` = inserted rows that also have `_s_flag`.
  - `updated` = `both AND ((NOT _s_flag AND (hc OR _t_del IS NOT NULL)) OR (_s_flag AND (_t_del IS NULL OR hc)))`.
  - `to_deleted` = `both AND _s_flag AND _t_del IS NULL`. `undeleted` = `both AND NOT _s_flag AND _t_del IS NOT NULL`. `deleted_changed` = `both AND _s_flag AND _t_del IS NOT NULL AND hc`.
  - `deactivated` = `NOT _s_in AND _t_in AND _t_del IS NULL`.

Each `updated` term maps 1-1 to one `WHEN MATCHED` clause (I5).

## Node design

All three notebooks follow the `NB_SLV_POI_MEDIA_INFO` layout. Cells: markdown, parameters (tagged `parameters`, same 8 params), `%run NB_LIB_TRANSFORM_SLV_GLD`, build plus `SPEC`, `RES = run_node(...)`, `notebookutils.notebook.exit(finish_node(RES))`. Each has `FLAG = "_is_deleted"`, a tuple `OUT_COLS` equal to the model-design `## Columns` business columns of that table, and `_require_types(df, {col: simpleString}, name)` raising `ConfigError` on a missing column or a type that differs from the L1 Field Mapping type (`docs/context/mapping_slv_pn_product.md` §1, §7, §10, §12, §13). Columns are not cast. Each `build` ends with `return rows.select(*OUT_COLS, FLAG)`.

| notebook | cell ids | inputs (role: L1) | required_inputs | block_checks | flag source |
|---|---|---|---|---|---|
| `NB_SLV_PN_PRODUCT_SALE` | `pnsalemd`, `pnsaleparam`, `pnsalerun`, `pnsalebuild`, `pnsaleres`, `pnsaleexit` | products: `slv_pn_products`, posts: `slv_pn_product_posts`, variants: `slv_pn_product_variants` | all three | `("is_bookable_null", "is_bookable IS NULL")` | `slv_pn_products.deleted` |
| `NB_SLV_PN_HOTEL_ROOM_OFFER` | `pnroommd`, `pnroomparam`, `pnroomrun`, `pnroombuild`, `pnroomres`, `pnroomexit` | room_types: `slv_pn_hotel_room_types` | room_types | `("is_bookable_null", "is_bookable IS NULL")` | `slv_pn_hotel_room_types.deleted` |
| `NB_SLV_PN_HOTEL_RATE_OFFER` | `pnratemd`, `pnrateparam`, `pnraterun`, `pnratebuild`, `pnrateres`, `pnrateexit` | rate_plans: `slv_pn_hotel_rate_plans` | rate_plans | none | `slv_pn_hotel_rate_plans.deleted` |

Every `SPEC` sets `pk` to its single key, `deleted_flag="_is_deleted"`, `write_mode="MERGE"`, and no `soft_delete_set`. `ctx.input` does not filter L1, because L1 has no `row_hash`. The build must not add a `deleted` filter on the base entity (I6).

### Price decode pure block (product sale)

```python
# BEGIN_PRICE_PURE
import base64
import binascii
import re

PRICE_NUM_RE = re.compile(r"^[+-]?(\d+(\.\d*)?|\.\d+)([eE][+-]?\d+)?$")


def decode_price(value, scale):
    """mapping_slv_pn_product_l2.md §1.3: NULL/boolean -> None; số giữ; chuỗi số parse; còn lại base64
    integer big-endian có dấu / 10^scale; lỗi hoặc rỗng -> None. Không bao giờ trả 0 thay cho None."""
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value)
    if text == "" or text in ("true", "false"):   # boolean JSON ở cột string L1
        return None
    if PRICE_NUM_RE.match(text):
        return float(text)
    try:
        raw = base64.b64decode(text, validate=True)
    except (binascii.Error, ValueError):
        return None
    if not raw:
        return None
    return int.from_bytes(raw, "big", signed=True) / (10 ** scale)
# END_PRICE_PURE
```

`DECODE = {s: F.udf(lambda v, s=s: decode_price(v, s), T.DoubleType()) for s in (2, 4)}`. Scales: `original_price` 4, `marketing_price` 4, `markup_percent` 2.

### Product sale build

```python
def build(ctx):
    products, posts, variants = ctx.input("products"), ctx.input("posts"), ctx.input("variants")
    _require_types(products, PRODUCT_TYPES, "slv_pn_products")
    _require_types(posts, POST_TYPES, "slv_pn_product_posts")
    _require_types(variants, VARIANT_TYPES, "slv_pn_product_variants")
    live = posts.where(F.col("deleted") == F.lit(False))
    groups = live.groupBy("external_id").agg(F.count(F.lit(1)).alias("_n"))
    unique = (live.join(groups.where(F.col("_n") == 1), "external_id")
              .select(F.col("external_id").alias("_ext"), F.col("id").alias("product_post_id"),
                      "original_price", "marketing_price", "markup_percent"))
    ok = (F.col("status") == F.lit("active")) & (F.col("deleted") == F.lit(False))
    book = variants.groupBy(F.col("product_id").alias("_pid")).agg(F.max(F.when(ok, 1).otherwise(0)).alias("_ok"))
    base = products.select(F.col("id").alias("product_id"),
                           F.get_json_object(F.col("metadata"), "$.holiday_product_post_id").alias("_ext"),
                           F.col("deleted").alias(FLAG))
    rows = (base.join(unique, "_ext", "left").join(book, F.col("product_id") == F.col("_pid"), "left")
            .select("product_id", "product_post_id",
                    DECODE[4](F.col("original_price")).alias("original_price"),
                    DECODE[4](F.col("marketing_price")).alias("marketing_price"),
                    DECODE[2](F.col("markup_percent")).alias("markup_percent"),
                    F.coalesce(F.col("_ok") == 1, F.lit(False)).alias("is_bookable"), FLAG,
                    "_ext", F.col("original_price").alias("_rp"), F.col("marketing_price").alias("_rm"),
                    F.col("markup_percent").alias("_rk")))
    # warns from one agg over rows (+ groups for post_match_many); then:
    return rows.select(*OUT_COLS, FLAG)
```

Warns, taken from one `agg` on `rows` (persisted and unpersisted in `finally`):
- `post_match_none` = `_ext IS NOT NULL AND product_post_id IS NULL`.
- `price_decode_null` = sum over the three prices of `raw IS NOT NULL AND decoded IS NULL`.
- `post_match_many` = count of distinct referenced `_ext` whose group has `_n > 1`.

### Room and rate builds

- Room: `ok = (status == "Active") & (available_rooms > 0) & (deleted == False)`. Select `id→room_type_id, status, available_rooms, max_occupancy, adult_capacity, child_capacity, view_type, deleted, coalesce(ok, false)→is_bookable, deleted→FLAG`. Add `ctx.warn("room_status_null", count status IS NULL)`.
- Rate: select `id→rate_plan_id, status, meal_plan, valid_from, valid_to, deleted→FLAG`. No cast, no window flag, no label.

## Registration

`init_seed_ctrl` `PIPELINE_CONFIG_ROWS`: append 5 rows, after the `oldpricepy` group, with the comment `# [THÊM 27/11] 20261127-slv-pn-product-l2-transform`:

```
(_GLD30, _S, 'slv_pn_products', _S, 'slv_pn_product_sale', 1, 1, 'RECOMPUTE', None, None, 'NB_SLV_PN_PRODUCT_SALE'),
(_GLD30, _S, 'slv_pn_product_posts', _S, 'slv_pn_product_sale', 1, 1, 'RECOMPUTE', None, None, 'NB_SLV_PN_PRODUCT_SALE'),
(_GLD30, _S, 'slv_pn_product_variants', _S, 'slv_pn_product_sale', 1, 1, 'RECOMPUTE', None, None, 'NB_SLV_PN_PRODUCT_SALE'),
(_GLD30, _S, 'slv_pn_hotel_room_types', _S, 'slv_pn_hotel_room_offer', 1, 1, 'RECOMPUTE', None, None, 'NB_SLV_PN_HOTEL_ROOM_OFFER'),
(_GLD30, _S, 'slv_pn_hotel_rate_plans', _S, 'slv_pn_hotel_rate_offer', 1, 1, 'RECOMPUTE', None, None, 'NB_SLV_PN_HOTEL_RATE_OFFER'),
```

`NB_CREATE_DDL`: append markdown `pnl2edgemd` (`# [THÊM 27/11] 20261127-slv-pn-product-l2-transform`, plus one Vietnamese line: add 5 edges `PL_VV_TRANS_SLV_TO_GLD_30M`, no DDL, a rerun adds nothing) and code `pnl2edgepy`. The code copies the edge part of `srvcoverpy` and `mediaddlpy`:
- `PL = "PL_VV_TRANS_SLV_TO_GLD_30M"`, `SLV`, `CFG`, `LEASE_MINUTES = 90`.
- `EDGES_ON` holds the same 5 edges as `(seq, src, "lh_vv_silver.dbo", trg, "RECOMPUTE", nb, 1)`, seq 1..5.
- Flow lock acquire, then `_refresh_lock()` before each write.
- Stop before writing ("Dừng trước khi ghi") when any of these hold:
  - any of the 5 L1 sources is missing;
  - any of the 3 targets has an active edge in another pl;
  - an `EDGES_ON` key exists but is not exactly one active row;
  - a target table already exists and was not written by this lib (no `row_hash`/`deleted_at`).
- `MERGE … WHEN NOT MATCHED THEN INSERT` with `MAX(id) + seq`, then a check after the write ("Sau khi ghi"), and lock release in `finally`.
- No `DROP`/`DELETE`/`TRUNCATE`/`ALTER`.

## Rollout

1. Merge the lib, nodes, seed, patch cell and tests together after local verification and review.
2. Fabric DEV: import the lib only. Watch one normal `PL_VV_TRANS_SLV_TO_GLD_30M` and one `PL_VV_TRANS_SLV_TO_ENR_15M` run. Node statuses and diff counts should match the previous runs (I1).
3. Run the scratch MERGE self-test (Verification R1).
4. Import the three node notebooks, then run `pnl2edgepy`. The edges go live at the next GLD30 trigger, which is acceptable because the tables have no readers. Right after seeding, run each node by hand with `p_mode = DRY_RUN` and read the diff and QG.
5. Let GLD30 (or a manual `RUN`) create the tables, then run R2 and R3.

## Rollback and forward recovery

- Before step 4: revert the lib commit and re-import. Old nodes never took the new branch.
- After step 4: a runbook statement sets the 5 edges `is_active = 0`. It updates only rows whose value is still 1, then the node notebooks are reverted. The tables stay, with no readers and no DROP. Edge watermark rows are harmless.
- Forward fix: correct the build, then run the node with `p_force = true`. MERGE converges to the correct business values. Rows wrongly flagged are undeleted by the `deleted_at → NULL` branch.
- If wrong first-seen `deleted_at` timestamps must be erased, drop and rebuild only that L2 table under `runtime-runbook.md` steps. This loses `created_at` history, which nothing consumes.

## Implementation plan

1. Write `test_merge_default_sql_golden` against the current lib first, and confirm it passes before any lib edit. Record the exact strings for `(…, {})` and `(…, {}, "load_origin")`.
2. Lib edits as in Lib design. Update the lib markdown `191e1851` with one line on the flag branch.
3. Three node notebooks as in Node design.
4. Seed rows and the patch cell as in Registration.
5. Tests (new file plus 3 updated tests).
6. Docs:
   - `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md` §4 §6: the `NodeSpec` field and the MERGE row.
   - `docs/context/03_OPERATOR_GUIDE.md` §2.8: three table rows (silver, key, `MERGE`, notebook).
   - `docs/context/mapping_slv_pn_product_l2.md` `## Câu hỏi cần chốt` items 1–3: mark them resolved with pointers to C-03, this architecture's Registration, and `deleted_flag`. Item 4 stays open.
7. Main sets `runtime_required: true` (see Verification) and requests `python scripts/vv.py run-author 20261127-slv-pn-product-l2-transform --kind runbook`.

## Verification

Local (no Spark):

```
python -m pytest tests/test_slv_pn_product_l2_contract.py tests/test_legacy_gold_poi_init_contract.py tests/test_initial_ddl_contract.py tests/test_enr_poi_contract.py -q
python -m pytest -q
python scripts/vv.py verify 20261127-slv-pn-product-l2-transform
```

New `tests/test_slv_pn_product_l2_contract.py`:

| test | asserts |
|---|---|
| `test_merge_default_sql_golden` | Default output is byte-equal to the strings recorded in step 1, both with and without owner. `deleted_flag=None` explicitly gives the same string |
| `test_merge_flag_clause_order` | With the flag: three `WHEN MATCHED` in the I4 order, with the exact predicates in Lib design. `CASE WHEN s.`_is_deleted`` in INSERT. `NOT MATCHED BY SOURCE` text equals the default |
| `test_merge_flag_excluded_from_columns` | Flag absent from INSERT columns and every `SET`. Clause 3 has no `deleted_at` assignment |
| `test_merge_flag_rejects_owner` | `ConfigError` with owner col, and with the flag inside `cols` |
| `test_diff_counts_flag_branch` | `diff_counts` signature has `deleted_flag=None`. The first statement delegates. The existing `_t_own` body is unchanged. `_diff_counts_flag` has the five count names and the `updated` predicate terms |
| `test_nodespec_deleted_flag_default` | Field `deleted_flag: Optional[str] = None` |
| `test_add_row_hash_flag_rules` | Exclusion of the flag from `cols`. Errors for missing, non-boolean, pk, tech name, `soft_delete_set` |
| `test_quality_gate_flag_null_block` | `deleted_flag_null` added only under `if spec.deleted_flag` |
| `test_run_node_flag_wiring` | `persist_schema(df.schema, spec)` in `ensure_target`. `diff_counts(df, trg_fq, spec.pk, spec.deleted_flag)`. APPEND rejection. `qg["delete_flag"]` |
| `test_l2_node_specs` | `_spec()` of the three notebooks equals the Node design table |
| `test_l2_out_cols_match_model_design` | `OUT_COLS` equals the model-design order. `build` ends with `rows.select(*OUT_COLS, FLAG)`. `FLAG == "_is_deleted"` |
| `test_l2_excluded_columns_absent` | No `variants_json`, `poi_id`, `source_id`, `destination`, `meal_plan_label`, `llm` in the three build cells |
| `test_price_decode_vectors` | Exec of the PURE block: `None`, `""`, `"true"`, `"false"`, `"@@"` → None. `"EtZE"`, 4 → 123.45. `"/w=="`, 4 → -0.0001. `"AA=="`, 4 → 0.0. `"1234"`, 4 → 1234.0. `"12.5"`, 2 → 12.5 |
| `test_product_sale_build_static` | `"$.holiday_product_post_id"`, posts `deleted == F.lit(False)`, `_n == 1`, `F.lit("active")`, no `lower(`, no `F.first`, price columns only via `DECODE` |
| `test_room_offer_build_static` | `"Active"`, `available_rooms") > 0`, `coalesce(ok, F.lit(False))`, `room_status_null` |
| `test_rate_offer_build_static` | `valid_from` and `valid_to` selected without cast, compare or `current_` |
| `test_l2_edges_create_vs_init` | `pnl2edgepy` `EDGES_ON` maps 1-1 to the 5 seed rows. Each target is owned only by `PL_VV_TRANS_SLV_TO_GLD_30M`. `nb_name` follows C-03 |
| `test_l2_patch_cell_guards` | Order: "Dừng trước khi ghi" before `_refresh_lock()` before `WHEN NOT MATCHED THEN INSERT` before "Sau khi ghi". `finally:`. No `DROP`/`DELETE`/`TRUNCATE`/`ALTER`. L1 existence check present |

Updated tests:
- `tests/test_initial_ddl_contract.py::test_pipeline_config_rows_match_sources`: add a `pnl2edgepy` loop (gld pl) and change 79 → 84.
- `tests/test_enr_poi_contract.py::test_dest_portal_patch_cell`: replace `ids[-4:]` with the contiguous slice from `oldpricemd` to `destportalpy`, and assert `ids[-2:] == ["pnl2edgemd", "pnl2edgepy"]`.
- `tests/test_legacy_gold_poi_init_contract.py::test_merge_target_passes_owner_only_when_column_present`: change the call literal to `sql_merge_target(fq, view, cols, spec.pk, spec.soft_delete_set, owner, spec.deleted_flag)`.

Runtime proof (required by this architecture). The repo has no local Spark or Delta, so the MERGE clause semantics, the UDF wiring and the L1 timestamp values cannot be proven locally. The runbook must cover:
- R1 Scratch self-test on Fabric DEV, under task `evidence/probes/`. It creates `lh_vv_silver.dbo.tmp_pnl2_selftest_<exec8>` (it refuses to start if the name exists), runs `sql_merge_target` with the flag for the 10 I4 rows in two rounds, and checks `deleted_at`, `updated_at`, business values and `diff_counts` against the MERGE `operationMetrics`. It repeats with `deleted_flag=None` to show today's behaviour, then drops only that table name.
- R2 After the first RUN, a second run of each node with `p_force = true` gives `inserted = updated = deactivated = 0` and no new target commit.
- R3 Read-only invariants probe, counts only:
  - L1 base id anti-join to L2 = 0.
  - Present ids with `deleted_at IS NOT NULL` and L1 `deleted = false` = 0.
  - Present ids with `deleted_at IS NULL` and L1 `deleted = true` = 0.
  - `product_post_id IS NULL` with any price not NULL = 0.
  - `is_bookable IS NULL` = 0.
  - `updated_at < created_at` = 0.
  - The column list of each table equals model-design `## Columns`, with no `_is_deleted`.
