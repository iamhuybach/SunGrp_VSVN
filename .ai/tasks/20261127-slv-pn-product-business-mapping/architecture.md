RESULT: PASS

## Main brief

### Decision
PASS. This task changes documents only. Mapping L1 stays as it is. Main edits mapping L2 so it matches Q-21 to Q-24 and the MERGE behaviour of `NB_LIB_TRANSFORM_SLV_GLD`.
Selected option B: Q-21 needs a delete flag that the lib takes from the build (not stored, not part of `row_hash`). The lib's default MERGE only soft-deletes ids that are missing from the build. Building the flag belongs to a later implementation task, not this one.
Grain, keys and columns are unchanged from `model-design.md`. Its Conflicts 4, 5, 6 and 8 are superseded by Q-21, Q-22, Q-23 and Q-24.

### Invariants Main must preserve
- Each L2 table has one row per L1 `id`, including L1 rows with `deleted = true`. Keys are `product_id`, `room_type_id` and `rate_plan_id`.
- The post join counts posts with `deleted = false` per `external_id` and joins only the groups with count 1. Zero or more than one gives NULL for `product_post_id` and all three prices.
- Variants are aggregated per `product_id` first. `is_bookable` is `false`, never NULL, when no variant qualifies.
- Prices are never `0`. NULL, empty or a decode error gives NULL.
- `row_hash` covers the key plus the business columns in Field Mapping order. The 4 technical columns and the delete flag are excluded. Timestamps are hashed as `unix_micros`.
- `deleted_at` keeps the timestamp of the first run that saw the delete. It returns to NULL when L1 `deleted = false`.
- `updated_at` changes only when `row_hash` changes or `deleted_at` moves between NULL and non-NULL.
- `docs/context/mapping_slv_pn_product.md` is unchanged. No notebook, DDL or test is edited.

### Edit list
| # | file | anchor (cell id, function, or heading) | change | done-when |
|---|---|---|---|---|
| 1 | docs/context/mapping_slv_pn_product_l2.md | intro, after the technical-column paragraph (line 5) | Add a paragraph `Cách tính`: full recompute from L1 at the pinned version, then the `row_hash` MERGE of `NB_LIB_TRANSFORM_SLV_GLD`; any table reading L2 takes only `deleted_at IS NULL`; timestamps hashed as `unix_micros`; Q-21 needs the lib to take the delete flag from the build (flag not stored, not in `row_hash`), because the default MERGE only soft-deletes ids missing from the build | The paragraph names the lib, `unix_micros`, the delete flag and `deleted_at IS NULL` |
| 2 | same | `### 1.1. Xử lý` | Add one sentence: count posts with `deleted = false` per `external_id` and join only groups with exactly one post; aggregate variants per `product_id` before the join; one row per product | The sentence exists and agrees with Q-24 |
| 3 | same | the `updated_at` rows in `### 1.2`, `### 2.2`, `### 3.2` | Transform = `Cột kỹ thuật L2. Đổi khi row_hash đổi hoặc deleted_at đổi giữa NULL và khác NULL` | All 3 rows contain `deleted_at` |
| 4 | same | the `deleted_at` rows in `### 1.2`, `### 2.2`, `### 3.2` | Append: keep the timestamp of the first run that saw the delete and do not rewrite it later; while the L1 row still exists with `deleted = true`, business columns are still computed from it; once the id is gone from L1, they keep the last values | All 3 rows contain `lần tính đầu thấy xoá` |
| 5 | same | `## Câu hỏi cần chốt` | Replace `Không có.` with 4 items that do not block this document: (1) the node notebook that owns the 3 tables; (2) registration in `TABLE_SPECS`/`TABLE_CONFIGS`/`ctrl_cfg_schema_registry`; (3) the lib delete flag as the condition for implementing Q-21; (4) `valid_from`/`valid_to` inherit L1 question 4 | 4 numbered items |
| 6 | .ai/tasks/20261127-slv-pn-product-business-mapping/decision.md | `## Lịch sử quyết định` | Record the 4 items as open. No new Q row | Entry dated 2026-11-27 |

### Order and stop points
1. Rows 1–5 in mapping L2, then row 6.
2. Run the validation in Tests. STOP for evidence: if any check fails, fix it and run again. Do not advance the gate.
3. No user decision is needed for this task. The 4 items in row 5 belong to the later implementation task. STOP for a user decision only if the user rejects option B. Q-21 would then have to be amended before any implementation.
4. Advance local verification according to the workflow. Do not commit and do not run Fabric DEV (request).

### Tests and verification
- `python scripts/vv.py validate 20261127-slv-pn-product-business-mapping`
- `python scripts/vv.py verify 20261127-slv-pn-product-business-mapping`
- Grep `docs/context/mapping_slv_pn_product_l2.md`:
  - 3× `Lakehouse.schema:`
  - 3× `\. Xử lý`
  - 3× `\. Field Mapping`
  - 3 `updated_at` rows containing `deleted_at`
  - 3× `lần tính đầu thấy xoá`
  - 4 numbered items under `## Câu hỏi cần chốt`
- `git diff --stat docs/context/mapping_slv_pn_product.md` returns empty output.
- Grep `notebooks/NB_SETUP_INITIAL_DDL.ipynb` for `slv_pn_product_sale|slv_pn_hotel_room_offer|slv_pn_hotel_rate_offer` returns 0 matches.

### Read only if needed
- `## Selected design and alternatives` and `### Lib delete-flag MERGE contract` → rows 1, 4, 5(3)
- `## Invariants` → rows 2, 3, 4
- `## Idempotency` → rows 3, 4
- `## Grain and keys` → row 2
- `## State ownership` → row 5(1)
- `## Implementation plan (this task)` → rows 1–6
- `## Follow-ups` → none (naming-convention line 117 is outside scope)

# Architecture: 20261127-slv-pn-product-business-mapping

## Scope

This task produces mapping documents and nothing else. `docs/context/mapping_slv_pn_product.md` (L1) is already complete and stays as it is. `docs/context/mapping_slv_pn_product_l2.md` (L2) defines three Silver L2 tables: `slv_pn_product_sale`, `slv_pn_hotel_room_offer` and `slv_pn_hotel_rate_offer`. `model-design.md` `## Entities and grain` and `## Keys` give their grain and keys.

This design does two things:

- It sets the recompute and soft-delete semantics that the L2 contract requires from whatever notebook later builds these tables.
- It lists the edits to mapping L2 that make the contract consistent with the shared transform library (`notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb`) and with ledger rows Q-21 to Q-24.

## Non-goals

- No change to notebooks, DDL, `TABLE_SPECS`, `TABLE_CONFIGS`, `ctrl_cfg_schema_registry`, pipelines or tests.
- No node notebook for the L2 tables, and no change to the lib. The lib extension in "Selected design" is a contract for a later implementation task. Main does not apply it in this task.
- No new column, grain or key on the 13 L1 tables. The four open L1 questions stay open.
- No Gold mapping, no destination, no `poi_id` on L2 (Q-13, Q-14).
- No change to `docs/context/02_NAMING_CONVENTION.md`. It is outside `scope.files`. See "Follow-ups".

## Invariants

1. Grain is one L2 row per L1 `id` of the source table, including L1 rows with `deleted = true` (Q-21; `model-design.md` `## Entities and grain`). Keys are `product_id`, `room_type_id` and `rate_plan_id` (`model-design.md` `## Keys`).
2. The `product_post_id` lookup never fans out. Group the posts with `deleted = false` by `external_id` and keep only the groups with count 1. The match is a string comparison with `metadata.holiday_product_post_id` (Q-24). If no post matches, or more than one does, `product_post_id` and all three prices are NULL.
3. Aggregate variants by `product_id` before the join. `is_bookable` is `false` (never NULL) when no variant has `status = 'active'` (exact case) and `deleted = false`. The product's own `status` and `deleted` do not affect the flag (Q-22, Q-17).
4. A NULL price, an empty price or a decode error gives NULL, never `0` (Q-15).
5. `row_hash = sha2(to_json(struct(<key + business columns in Field Mapping order>)), 256)`. `row_hash`, `created_at`, `updated_at`, `deleted_at` and the build's delete flag are outside the struct. Timestamps are hashed as `unix_micros`, which is the lib behaviour (Q-23).
6. Set `deleted_at` when L1 `deleted = true` or the id is no longer in L1. Once set, keep the timestamp of the first run that saw the delete. Set it back to NULL on the first run where L1 `deleted = false` (Q-21).
7. `updated_at` changes when `row_hash` changes, or when `deleted_at` moves between NULL and non-NULL. Nothing else changes it.
8. A rerun on unchanged L1 inputs writes zero changed rows: no change to `row_hash`, `updated_at` or `deleted_at`.
9. L2 consumers read only `deleted_at IS NULL`. This is the lib `ctx.input(..., live_only=True)` default.

## State ownership

- L1 tables: `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` owns them. L2 only reads them.
- L2 tables: a single node notebook will own each table, which no settled file names yet (`model-design.md` Conflicts 3). It writes through `run_node` and `merge_target` in `NB_LIB_TRANSFORM_SLV_GLD`. No other writer is allowed.
- Technical columns: `row_hash`, `created_at`, `updated_at` and `deleted_at` belong to the lib MERGE. The build never emits them; `add_row_hash` raises `ConfigError` if it does.
- Run log: the lib appends one `ctrl_log_table_run` row per node run.

## Grain and keys

See `model-design.md` `## Entities and grain` and `## Keys`. Invariants 1–3 cover the two things that could change the grain: the post join (count = 1 only) and the variant aggregate (one row per `product_id`). The lib exit quality gate (`NodeSpec` pk checks) blocks a NULL or duplicate key before any write.

## Ordering

The L2 node runs after the extract of its L1 inputs:

- `slv_pn_product_sale` reads `slv_pn_products`, `slv_pn_product_posts` and `slv_pn_product_variants`.
- `slv_pn_hotel_room_offer` reads `slv_pn_hotel_room_types`.
- `slv_pn_hotel_rate_offer` reads `slv_pn_hotel_rate_plans`.

The three L2 tables do not depend on each other and can run in parallel. The lib pins each L1 input to a version per run. A cross-table skew (for example, a post extracted in a later batch than its product) converges on the next full recompute. No watermark is needed because every run recomputes everything.

## Transaction and commit boundaries

One Delta MERGE per L2 table per run is the commit unit. The `ctrl_log_table_run` append comes after the MERGE, as a separate commit. Nothing commits across tables.

## Idempotency

Every run fully recomputes from the pinned L1 versions, and the MERGE is keyed on the primary key and gated on the hash, so a rerun is a no-op (invariant 8). `deleted_at` stays fixed because the delete branch only fires when `t.deleted_at IS NULL`, or for a new key, on insert. `created_at` is written only on insert.

## Concurrency

Each table has one writer. The lib runs nodes in a shared Spark session with uniquely named temp views. A concurrent extract MERGE on L1 does not conflict, because L2 reads pinned versions. Two runs of the same L2 node at once are not supported. Orchestration must serialise them, as for existing lib nodes.

## Retry and recovery

A failed run commits nothing to the target, or commits the whole MERGE: Delta is atomic per MERGE. A retry recomputes from the current L1 versions and converges. The lib re-raises `FAILED` and `SKIPPED` so the orchestrator can retry them.

## Partial failure

One L2 table can succeed while another fails. Since they are independent, each table stays internally consistent. A failed build leaves the previous version of that table in place. Consumers might briefly see `slv_pn_product_sale` newer than `slv_pn_hotel_room_offer`, which is acceptable because no L2 table joins another.

## Observability

Use the existing lib `ctrl_log_table_run` row (counts and the `qg_json` quality-gate payload). Recommended `warn_checks` for the later node:

- `product_post_id IS NULL`: no post matched, or more than one did.
- `product_post_id IS NOT NULL AND original_price IS NULL`: decode failure.
- `meal_plan NOT BETWEEN 0 AND 4`.

These checks only count rows; they block nothing.

## Security

Not applicable: internal lakehouse tables with the same access as L1. No PII is added. Prices are already on L1 in encoded form.

## Selected design and alternatives

The problem is that the lib MERGE (`sql_merge_target`) only soft-deletes keys that are missing from the build. Any key present in the build gets `deleted_at = NULL`. Q-21 needs a key that is present (its L1 row exists with `deleted = true`) to carry a non-NULL `deleted_at`.

| Option | Description | Q-21 holds | Cost |
|---|---|---|---|
| A. Lib default | The build filters L1 to `deleted = false`. Deleted ids drop out and the lib soft-deletes them | No. An id already deleted before its first insert never gets an L2 row. Room offer `deleted` stays `false` on soft-deleted rows, which contradicts `deleted_at` | None |
| B. Lib delete flag (selected) | Add an optional `NodeSpec` field naming a boolean build column. That column is left out of `row_hash`, not persisted, and drives `deleted_at` in the MERGE | Yes, including first insert and undelete | Lib change and tests in the implementation task. Existing nodes are unaffected because the field defaults to off |
| C. Custom MERGE in the node | The node writes its own MERGE | Yes | Duplicates the hash, quality-gate and log logic, and drifts from the lib |
| D. Physical delete | Delete L2 rows | No | Contradicts Q-21 |

B is the only option that satisfies a settled user decision without duplicating lib logic. If the user later accepts the gaps of A, Q-21 has to be amended first.

### Lib delete-flag MERGE contract (implementation task, not this task)

Proposed field: `deleted_flag: Optional[str] = None`. The flag column must be boolean and non-null. It is automatically left out of the hash and the persisted columns. The MERGE branches:

```
-- s = build output with row_hash and s._del (boolean); t = target
WHEN MATCHED AND NOT s._del AND (t.row_hash <> s.row_hash OR t.deleted_at IS NOT NULL)
  THEN UPDATE business cols, row_hash, updated_at = now, deleted_at = NULL
WHEN MATCHED AND s._del AND t.deleted_at IS NULL
  THEN UPDATE business cols, row_hash, updated_at = now, deleted_at = now
WHEN MATCHED AND s._del AND t.deleted_at IS NOT NULL AND t.row_hash <> s.row_hash
  THEN UPDATE business cols, row_hash, updated_at = now          -- keep deleted_at
WHEN NOT MATCHED
  THEN INSERT business cols, row_hash, created_at = now, updated_at = now,
       deleted_at = CASE WHEN s._del THEN now ELSE NULL END
WHEN NOT MATCHED BY SOURCE AND t.deleted_at IS NULL
  THEN UPDATE deleted_at = now, updated_at = now                  -- existing branch
```

Delete flag expressions per table:

- product sale: `slv_pn_products.deleted`.
- room offer: `slv_pn_hotel_room_types.deleted`. The persisted `deleted` business column also stays, as a 1-1 copy.
- rate offer: `slv_pn_hotel_rate_plans.deleted`.

When an id is gone from L1, its business columns stay at the last computed values.

## Rollout

For this task: merge the doc edits. For the later implementation: add the lib field (default off) and its tests, register the three tables, add the node notebook(s), then run on Fabric DEV. That is a separate task with its own gates.

## Rollback and forward recovery

For this task: revert the doc commit. For the later implementation: the lib field defaults to off, so reverting the node notebook leaves the other nodes untouched. The L2 tables can be dropped and fully recomputed from L1, because they hold no state that cannot be derived from it.

## Implementation plan (this task)

Main edits `docs/context/mapping_slv_pn_product_l2.md` only. The text stays in Vietnamese, in the document's style.

1. Intro: after the technical-column paragraph (line 5), add a paragraph `Cách tính` that says:
   - Every run recomputes everything from L1, then runs the `row_hash` MERGE of `NB_LIB_TRANSFORM_SLV_GLD`. L1 is read at the version pinned for that run.
   - Any table that reads L2 takes only rows with `deleted_at IS NULL`.
   - Timestamps are hashed as `unix_micros`.
   - Q-21 needs the lib to take the delete flag from the build. The flag is not stored and is not part of `row_hash`. The lib's default MERGE only soft-deletes ids that are missing from the build.
2. §1.1: add one sentence. Count the posts with `deleted = false` per `external_id` and join only the groups that have exactly one post. Aggregate variants per `product_id` before the join. Either way the result keeps one row per product.
3. The `updated_at` rows in §1.2, §2.2 and §3.2: Transform becomes `Cột kỹ thuật L2. Đổi khi row_hash đổi hoặc deleted_at đổi giữa NULL và khác NULL`.
4. The `deleted_at` rows in §1.2, §2.2 and §3.2: append to Transform:
   - Keep the timestamp of the first run that saw the delete. Later runs do not write it again.
   - While the L1 row still exists with `deleted = true`, business columns are still computed from it.
   - Once the id is gone from L1, business columns keep the values from the last run.
5. `## Câu hỏi cần chốt`: replace `Không có.` with four items, none of which blocks this document:
   - (1) the node notebook that owns the three tables;
   - (2) registration in `TABLE_SPECS` / `TABLE_CONFIGS` / `ctrl_cfg_schema_registry`;
   - (3) the lib delete flag as the condition for implementing Q-21;
   - (4) `valid_from` / `valid_to` inherit L1 question 4 (`EPOCH_S_TS` unit).
6. `decision.md` `## Lịch sử quyết định`: record the four items as open. Do not add a Q row until the user decides.

`model-design.md` Conflicts 4, 5, 6 and 8 are superseded by Q-21, Q-22, Q-23 and Q-24. No model-design rerun is needed, because grain, keys and columns are unchanged.

## Verification

- `python scripts/vv.py validate 20261127-slv-pn-product-business-mapping` passes.
- `python scripts/vv.py verify 20261127-slv-pn-product-business-mapping` passes.
- Grep mapping L2: three `Lakehouse.schema:` lines, three `### *.1. Xử lý`, three `### *.2. Field Mapping`. Each `updated_at` row contains `deleted_at`. Each `deleted_at` row contains `lần tính đầu thấy xoá`. `## Câu hỏi cần chốt` has four numbered items.
- `git diff --stat docs/context/mapping_slv_pn_product.md` is empty.
- Grep `notebooks/NB_SETUP_INITIAL_DDL.ipynb` for `slv_pn_product_sale|slv_pn_hotel_room_offer|slv_pn_hotel_rate_offer`: zero matches. This confirms the DDL is untouched.

Acceptance for the later implementation task, recorded here only:

- Unit tests of `sql_merge_target` with the delete flag cover: insert deleted, delete then undelete, a deleted row whose hash changes, and a rerun no-op.
- An exit quality-gate test of the post fan-out (two posts with the same `external_id` give a NULL `product_post_id`).
- A test that `is_bookable` is `false` when the product has no variants.

## Follow-ups

`02_NAMING_CONVENTION.md` line 117 says "`updated_at` chỉ đổi khi hash đổi", but the lib already bumps it on soft-delete. Align that line in a separate docs task. It is outside `scope.files`.
