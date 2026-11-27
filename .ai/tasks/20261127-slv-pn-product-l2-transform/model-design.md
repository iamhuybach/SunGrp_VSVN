# Model design: 20261127-slv-pn-product-l2-transform

## Scope

Base task: `20261127-slv-pn-product-l2-transform` (Silver L2 product sale and hotel offer transforms). This design gives the data model for three new Silver L2 tables in `lh_vv_silver.dbo`, built from the existing partner Silver L1 tables.

There is no `proposal.md`, so `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. This design follows the `Quyết định hiện hành` ledger in `decision.md` and the contract in `docs/context/mapping_slv_pn_product_l2.md`. Where current code disagrees, the ledger and the L2 mapping win.

Ledger rows implemented:

- C-01: classification (`data_model_change`, `idempotency`, `stateful_logic`). Only the data-model part is in scope here.
- C-02: `updated_at` changes when `row_hash` changes or when `deleted_at` flips between NULL and non-NULL.
- C-03: one node notebook per target table, named `NB_<UPPER(trg_tbl)>`.
- Q-19: the three-table split. `valid_from` and `valid_to` copy 1-1. No sale-window flag.
- Q-20: grain and keys for the three tables.
- Q-21: `deleted_at` semantics. The delete flag exists only in the build. It is not stored and is not in `row_hash` (option B of `.ai/tasks/20261127-slv-pn-product-business-mapping/architecture.md` `## Selected design and alternatives`).
- Q-22: `is_bookable` on `slv_pn_product_sale`.
- Q-23: what goes into `row_hash` and how it is computed.
- Q-24: `holiday_product_post_id` is a string and is compared as a string to `external_id`.

The L1 contract (`docs/context/mapping_slv_pn_product.md` §1, §7, §10, §12, §13) is read-only input. All 13 `slv_pn_product*` and `slv_pn_hotel*` L1 tables stay unchanged. This design adds no L1 columns, grain, or keys.

Out of scope: invariants, state ownership, transaction and commit boundaries, ordering, locking, watermarks, idempotency, retry, recovery, rollout, DDL, and notebook code.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_pn_product_sale` | Silver L2 | One row per `slv_pn_products.id`, including products with `deleted = true` (L2 mapping §1.1) | `NB_SLV_PN_PRODUCT_SALE` (C-03) |
| `lh_vv_silver.dbo.slv_pn_hotel_room_offer` | Silver L2 | One row per `slv_pn_hotel_room_types.id`. No rate plan attached and no price (L2 mapping §2.1) | `NB_SLV_PN_HOTEL_ROOM_OFFER` (C-03) |
| `lh_vv_silver.dbo.slv_pn_hotel_rate_offer` | Silver L2 | One row per `slv_pn_hotel_rate_plans.id`. No `room_type_id` (L2 mapping §3.1) | `NB_SLV_PN_HOTEL_RATE_OFFER` (C-03) |

Under Q-21, an L2 row stays in place after its L1 row is marked deleted or disappears. In both cases the row is soft-deleted through `deleted_at`.

## Keys

`poi_id` is excluded from all three tables (L2 mapping line 9, author input), so no `poi_id` formula applies. None of the three tables has a surrogate or hash key.

| table | primary key | business key | foreign keys (logical, not enforced) |
|---|---|---|---|
| `slv_pn_product_sale` | `product_id` | `product_id` = `slv_pn_products.id` (L1 §1 key `id`) | `product_id` → `slv_pn_products.id`. `product_post_id` → `slv_pn_product_posts.id` (L1 §10 key `id`), filled only when exactly one post with `deleted = false` matches (Q-24). `slv_pn_product_variants.product_id` (L1 §7) is read to build `is_bookable` and is not stored |
| `slv_pn_hotel_room_offer` | `room_type_id` | `room_type_id` = `slv_pn_hotel_room_types.id` (L1 §12 key `id`) | `room_type_id` → `slv_pn_hotel_room_types.id` |
| `slv_pn_hotel_rate_offer` | `rate_plan_id` | `rate_plan_id` = `slv_pn_hotel_rate_plans.id` (L1 §13 key `id`) | `rate_plan_id` → `slv_pn_hotel_rate_plans.id` |

Join key for `product_post_id`: `slv_pn_products.metadata.holiday_product_post_id` compared as a string to `slv_pn_product_posts.external_id`. Only posts with `deleted = false` count, and only `external_id` groups with exactly one such post can join (L2 mapping §1.1, Q-24). Variants are grouped by `product_id` before the join, so the output keeps one row per product.

## Columns

The order inside each table matches the Field Mapping table, and that order is also the `row_hash` struct order (Q-23).

`row_hash` covers the key and the business columns above it in Field Mapping order: `sha2(to_json(struct(...)), 256)`. Timestamps inside the struct are hashed as `unix_micros` (L2 mapping line 7). Kept out of the struct: `row_hash`, `created_at`, `updated_at`, `deleted_at`, and the build-only delete flag (Q-21, Q-23).

"Not stated" in the nullable column means the L2 and L1 mappings give no nullability. See Conflicts item 6.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_pn_product_sale` | `product_id` | string | no (key) | `slv_pn_products.id` | 1-1, key (L2 §1.2; Q-20) |
| `slv_pn_product_sale` | `product_post_id` | string | yes | `slv_pn_product_posts.id` via `slv_pn_products.metadata.holiday_product_post_id` = `slv_pn_product_posts.external_id` | Filled when exactly one post with `deleted = false` matches. NULL when none or more than one matches. Never pick an arbitrary post (L2 §1.1, §1.2; Q-24) |
| `slv_pn_product_sale` | `original_price` | double | yes | `slv_pn_product_posts.original_price` (L1 §10, base64 string) | Decode per L2 §1.3, scale 4. NULL, boolean, decode failure, empty value, or no unique post gives NULL. Never write 0 (L2 §1.2, §1.3, line 9) |
| `slv_pn_product_sale` | `marketing_price` | double | yes | `slv_pn_product_posts.marketing_price` | Decode per L2 §1.3, scale 4. Same NULL rule. Never write 0 (L2 §1.2, §1.3) |
| `slv_pn_product_sale` | `markup_percent` | double | yes | `slv_pn_product_posts.markup_percent` | Decode per L2 §1.3, scale 2. Same NULL rule. Never write 0 (L2 §1.2, §1.3) |
| `slv_pn_product_sale` | `is_bookable` | boolean | no (rule yields true or false) | `slv_pn_product_variants.product_id`, `status`, `deleted` | true when at least one variant with the same `product_id` has `status = active` (exact match) and `deleted = false`. Otherwise false. Product `status` and `deleted` are not used (L2 §1.1, §1.2; Q-22) |
| `slv_pn_product_sale` | `row_hash` | string | no | build | Over `product_id` through `is_bookable` in the order above (Q-23) |
| `slv_pn_product_sale` | `created_at` | timestamp | no | build | First computation (L2 §1.2; naming §5.2) |
| `slv_pn_product_sale` | `updated_at` | timestamp | no | build | Changes when `row_hash` changes or when `deleted_at` flips between NULL and non-NULL (C-02) |
| `slv_pn_product_sale` | `deleted_at` | timestamp | yes | `slv_pn_products.deleted`, or id gone from L1 | L2 recompute soft-delete, not the L1 source `deleted_at`. Set when `deleted = true` or when the id is gone. The first timestamp is kept and later runs do not rewrite it. Back to NULL on the next run after `deleted = false`. When the L1 row exists with `deleted = true`, business columns are still computed from it. When the id is gone, business columns keep their last computed values (L2 §1.2; Q-21) |
| `slv_pn_hotel_room_offer` | `room_type_id` | string | no (key) | `slv_pn_hotel_room_types.id` | 1-1, key (L2 §2.2; Q-20) |
| `slv_pn_hotel_room_offer` | `status` | string | not stated | `slv_pn_hotel_room_types.status` | 1-1 (L2 §2.2) |
| `slv_pn_hotel_room_offer` | `available_rooms` | int | not stated | `slv_pn_hotel_room_types.available_rooms` | 1-1 (L2 §2.2) |
| `slv_pn_hotel_room_offer` | `max_occupancy` | int | not stated | `slv_pn_hotel_room_types.max_occupancy` | 1-1 (L2 §2.2) |
| `slv_pn_hotel_room_offer` | `adult_capacity` | int | not stated | `slv_pn_hotel_room_types.adult_capacity` | 1-1 (L2 §2.2) |
| `slv_pn_hotel_room_offer` | `child_capacity` | int | not stated | `slv_pn_hotel_room_types.child_capacity` | 1-1 (L2 §2.2) |
| `slv_pn_hotel_room_offer` | `view_type` | string | not stated | `slv_pn_hotel_room_types.view_type` | 1-1 (L2 §2.2) |
| `slv_pn_hotel_room_offer` | `deleted` | boolean | not stated | `slv_pn_hotel_room_types.deleted` | 1-1 business column. It stays even when `deleted_at` is set (L2 §2.2; business-mapping architecture, Lib delete-flag contract) |
| `slv_pn_hotel_room_offer` | `is_bookable` | boolean | not stated (see Conflicts item 6) | `status`, `available_rooms`, `deleted` | true when `status = Active` (exact match), `available_rooms > 0`, and `deleted = false`. NULL `available_rooms` gives false (L2 §2.1, §2.2) |
| `slv_pn_hotel_room_offer` | `row_hash` | string | no | build | Over `room_type_id` through `is_bookable` in the order above (Q-23) |
| `slv_pn_hotel_room_offer` | `created_at` | timestamp | no | build | First computation (L2 §2.2) |
| `slv_pn_hotel_room_offer` | `updated_at` | timestamp | no | build | Same rule as product sale (C-02) |
| `slv_pn_hotel_room_offer` | `deleted_at` | timestamp | yes | `slv_pn_hotel_room_types.deleted`, or id gone from L1 | Same rule as product sale. `deleted` is still copied 1-1 (L2 §2.2; Q-21) |
| `slv_pn_hotel_rate_offer` | `rate_plan_id` | string | no (key) | `slv_pn_hotel_rate_plans.id` | 1-1, key (L2 §3.2; Q-20) |
| `slv_pn_hotel_rate_offer` | `status` | string | not stated | `slv_pn_hotel_rate_plans.status` | 1-1 (L2 §3.2) |
| `slv_pn_hotel_rate_offer` | `meal_plan` | int | not stated | `slv_pn_hotel_rate_plans.meal_plan` | 1-1. Kept as the integer 0–4. No label column (L2 §3.2, §3.3) |
| `slv_pn_hotel_rate_offer` | `valid_from` | timestamp | yes (NULL stays NULL) | `slv_pn_hotel_rate_plans.valid_from` | 1-1. No sale window is derived. No unit is assigned (L2 §3.1, §3.2; Q-19; Conflicts item 4). Hashed as `unix_micros` |
| `slv_pn_hotel_rate_offer` | `valid_to` | timestamp | yes (NULL stays NULL) | `slv_pn_hotel_rate_plans.valid_to` | Same rule as `valid_from` |
| `slv_pn_hotel_rate_offer` | `row_hash` | string | no | build | Over `rate_plan_id` through `valid_to` in the order above (Q-23) |
| `slv_pn_hotel_rate_offer` | `created_at` | timestamp | no | build | First computation (L2 §3.2) |
| `slv_pn_hotel_rate_offer` | `updated_at` | timestamp | no | build | Same rule as product sale (C-02) |
| `slv_pn_hotel_rate_offer` | `deleted_at` | timestamp | yes | `slv_pn_hotel_rate_plans.deleted`, or id gone from L1 | Same rule as product sale. This table does not copy `deleted` (L2 §3.2; Q-21) |

Build-only delete flag: a boolean in each table's build output, not stored and not in `row_hash`. It comes from `slv_pn_products.deleted` for product sale, `slv_pn_hotel_room_types.deleted` for room offer, and `slv_pn_hotel_rate_plans.deleted` for rate offer (business-mapping architecture, `### Lib delete-flag MERGE contract`; Q-21). Its build column name is not set. See Conflicts item 5.

Excluded from all three tables: `variants_json`, LLM output, destination, `source_id`, `poi_id`, the `meal_plan` text label, and the default price `0` (L2 mapping line 9; author input).

## Lineage

| table | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `slv_pn_product_sale` | None | `lh_vv_silver.dbo.slv_pn_products` (`id`, `metadata`, `deleted`); `lh_vv_silver.dbo.slv_pn_product_posts` (`id`, `external_id`, `original_price`, `marketing_price`, `markup_percent`, `deleted`); `lh_vv_silver.dbo.slv_pn_product_variants` (`product_id`, `status`, `deleted`). Also reads its own target's current `deleted_at` and `row_hash` through the lib MERGE | None |
| `slv_pn_hotel_room_offer` | None | `lh_vv_silver.dbo.slv_pn_hotel_room_types` (`id`, `status`, `available_rooms`, `max_occupancy`, `adult_capacity`, `child_capacity`, `view_type`, `deleted`). Own target through the lib MERGE | None |
| `slv_pn_hotel_rate_offer` | None | `lh_vv_silver.dbo.slv_pn_hotel_rate_plans` (`id`, `status`, `meal_plan`, `valid_from`, `valid_to`, `deleted`). Own target through the lib MERGE | None |

Every run recomputes from L1 in full, reading L1 at the version pinned for that run, then merges by `row_hash` through `NB_LIB_TRANSFORM_SLV_GLD` (L2 mapping line 7). Downstream readers take only rows with `deleted_at IS NULL` (L2 mapping line 7). No gold table is read.

## Conflicts and questions

1. **Registration.** None of the three tables is registered in `TABLE_SPECS`, `TABLE_CONFIGS`, or `ctrl_cfg_schema_registry` (L2 mapping line 3 and question 2). With no proposal, there is no `## ctrl_cfg_schema_registry` section. This design invents no rows. Open question: who defines the registry, `TABLE_SPECS`, and `TABLE_CONFIGS` rows (including any `pipeline_config` `trg_tbl` entries for C-03), and in which task?
2. **`updated_at` rule versus naming §5.2.** §5.2 says L2 `updated_at` changes only when the hash changes. C-02 and every L2 Field Mapping table say it also changes when `deleted_at` flips between NULL and non-NULL. Both rules govern the same single column, so they cannot both hold. C-02 wins for these three tables, and the business-mapping lib contract (option B) already sets `updated_at` on every `deleted_at` flip. §5.2 itself is unchanged, so the clash stands as a recorded exception. Question: should §5.2 be amended, or does the exception stay local to these three tables?
3. **Table prefix versus naming §1.** §1 says L2 tables are named by topic (`slv_poi_<chủ đề>`) and the source prefix `slv_pn_` is reserved for L1 extracts that keep the Postgres table name. These three L2 tables use `slv_pn_` because the only source is partner (L2 mapping line 3), and Q-19 and C-03 accept the names. Question: should this be recorded as a naming exception, or should §1 be amended?
4. **`EPOCH_S_TS` unit for `valid_from` and `valid_to`.** L2 mapping question 4 says these columns inherit L1 question 4. But L1 §13.2 maps `hotel_rate_plans.valid_from` and `valid_to` as plain 1-1 `timestamp` ("Probe không đọc cột timestamp này"), and L1 question 4 only names `src_created_at` and `src_updated_at` under `EPOCH_S_TS`. No unit is assigned here. Question: does the open epoch unit actually apply to `valid_from` and `valid_to`, and is the L1 timestamp value correct before it is hashed as `unix_micros`?
5. **Name and lib field for the build-only delete flag.** No file names the boolean build column. The business-mapping contract only shows `s._del` as an illustration, and the `NodeSpec` field `deleted_flag: Optional[str] = None` is proposed, not implemented (L2 mapping question 3). On room offer, the source `slv_pn_hotel_room_types.deleted` feeds both the stored business column `deleted` and the flag. Since the lib leaves the flag column out of storage and out of the hash, the flag needs a build name different from `deleted`. Question: what is the flag column name, and which task adds the lib field?
6. **Nullability.** Neither the L2 nor the L1 Field Mapping states nullability for the 1-1 columns (`status`, `available_rooms`, `max_occupancy`, `adult_capacity`, `child_capacity`, `view_type`, `deleted`, `meal_plan`). For room-offer `is_bookable`, only NULL `available_rooms` → false is stated. The result for NULL `status` or NULL `deleted` is not given. Question: what nullability should DDL declare for these columns, and must room-offer `is_bookable` always be non-NULL (false when any input is NULL)?
7. **Type cell on the `deleted_at` row.** In all three L2 Field Mapping tables, the `deleted_at` row shows Data Type `boolean`, which is the type of the source `deleted` flag. The target type comes from L2 mapping line 5 and naming §5.2: `timestamp`. This design uses `timestamp`. Please confirm the `boolean` cell describes the source only.
8. **Price decoding reference.** L2 §1.1 defers to `mapping_legacy_ai_product.md` §1.4, which is outside this run's read scope. This design relies only on the summary in L2 §1.3 (signed big-endian integer from base64, divided by `10^scale`, no `0` fallback). Question: should the implementation task check §1.4 for decoding steps that L2 §1.3 leaves out?
9. **JSON access to `holiday_product_post_id`.** L1 §1 stores `metadata` as a JSON string with no columns split out. The L2 mapping names the key `metadata.holiday_product_post_id` but gives no extraction expression. No `json_path` syntax is invented here. Question: confirm the extraction expression for the implementation task.
