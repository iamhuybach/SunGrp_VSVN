# Model design — 20261127-slv-pn-product-business-mapping

## Scope

Base task: `20261127-slv-pn-product-business-mapping`. This design covers only the data model for the three Silver L2 tables that Q-19 settled, as `docs/context/mapping_slv_pn_product_l2.md` §1–§3 specifies them.

The task has no `proposal.md`, so this design cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry` (see Conflicts 1). The settled sources are:

- Mapping L2: the intro, §1 `slv_pn_product_sale` (including §1.3 price decode), §2 `slv_pn_hotel_room_offer`, and §3 `slv_pn_hotel_rate_offer` (including §3.3 `meal_plan`).
- Mapping L1 (`docs/context/mapping_slv_pn_product.md`): this is a read-only contract and stays unchanged. The 13 `slv_pn_product*` and `slv_pn_hotel*` tables get no new column, grain, or key. The four items under L1 `## Câu hỏi cần chốt` stay open, and no L2 column depends on them.
- Ledger rows in `decision.md` `## Quyết định hiện hành`:
  - Q-01: `TABLE_CONFIGS` is the column source.
  - Q-03: L1 prices stay as strings.
  - Q-05: the `metadata` key `holiday_product_post_id`.
  - Q-12: L1 grain.
  - Q-13: `poi_id` formula, used only when joining to POI.
  - Q-14: destination is outside L1 and L2 and is handled at Gold.
  - Q-15: a NULL price stays NULL.
  - Q-16: `deleted` is the extract flag and the source `deleted_at` is kept.
  - Q-17: exact-case `status`.
  - Q-19: the three L2 tables, with `valid_from` and `valid_to` copied 1-1.
  - Q-11 is applied only as Q-19 restates it.
- Legacy reference: cell 15 of `notebooks_lgc/pl_transform_partner_userprofile_cms/5. nb_prepare_product_for_ingestion.ipynb`, used only for the `valid_from` / `valid_to` statement in mapping L2 §3.1.

Excluded from all three tables (mapping L2 intro; author constraints):
- `variants_json`
- LLM steps
- destination and destination remap
- `source_id`
- `poi_id`
- `meal_plan` text labels
- default price `0`

Repository check: `TABLE_SPECS` and `TABLE_CONFIGS` in `notebooks/NB_SETUP_INITIAL_DDL.ipynb` contain none of the three L2 names. No notebook under `notebooks/` mentions them either.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_pn_product_sale` | Silver L2 | One row per `slv_pn_products.id`, including deleted products (mapping L2 §1.1; Q-19) | Not named in the settled files (Conflicts 3) |
| `lh_vv_silver.dbo.slv_pn_hotel_room_offer` | Silver L2 | One row per `slv_pn_hotel_room_types.id`; no rate plan attached, no price (mapping L2 §2.1; Q-19) | Not named in the settled files (Conflicts 3) |
| `lh_vv_silver.dbo.slv_pn_hotel_rate_offer` | Silver L2 | One row per `slv_pn_hotel_rate_plans.id`; no `room_type_id` (mapping L2 §3.1; Q-19) | Not named in the settled files (Conflicts 3) |

The 13 L1 tables are inputs only. Their grain is one source row with key `id` (Q-12), and this design leaves them unchanged.

## Keys

| table | primary key | business key | foreign keys (logical) |
|---|---|---|---|
| `slv_pn_product_sale` | `product_id` (mapping L2 §1.1) | `product_id` = `slv_pn_products.id` | `product_id` → `slv_pn_products.id`; `product_post_id` → `slv_pn_product_posts.id`, NULL unless exactly one post matches (mapping L2 §1.1, §1.2) |
| `slv_pn_hotel_room_offer` | `room_type_id` (mapping L2 §2.1) | `room_type_id` = `slv_pn_hotel_room_types.id` | `room_type_id` → `slv_pn_hotel_room_types.id` |
| `slv_pn_hotel_rate_offer` | `rate_plan_id` (mapping L2 §3.1) | `rate_plan_id` = `slv_pn_hotel_rate_plans.id` | `rate_plan_id` → `slv_pn_hotel_rate_plans.id` |

Join key used only to derive `slv_pn_product_sale.product_post_id`:
- `slv_pn_products.metadata.holiday_product_post_id` = `slv_pn_product_posts.external_id`
- The post must have `deleted = false`.
- Sources: mapping L2 §1.1; Q-05 for the key; mapping L1 §1.3.

`poi_id` is not stored on any of the three tables (mapping L2 intro). When a later Gold step joins a product to POI, the formula is `poi_id = uuid_md5(business_service_id, 'partner')`. Its source is Q-13 and mapping L1 §9.1, using `slv_pn_product_business_service_relation.business_service_id`. This design adds no key for it.

## Columns

Source types come from `TABLE_CONFIGS` (Q-01). `deleted` comes from `TECH_COLUMNS` in `NB_LIB_EXTRACT_RAWDATA`. The L2 technical columns come from the mapping L2 intro and the Silver L2 row of `02_NAMING_CONVENTION.md`.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_pn_product_sale` | `product_id` | string | no (key) | `slv_pn_products.id` | 1-1, key. Mapping L2 §1.2 |
| `slv_pn_product_sale` | `product_post_id` | string | yes | `slv_pn_product_posts.id` via `metadata.holiday_product_post_id` = `external_id` | Exactly one post with `deleted = false` gives that post's `id`. Zero or more than one gives NULL. Never pick an arbitrary post. Mapping L2 §1.1, §1.2 |
| `slv_pn_product_sale` | `original_price` | double | yes | `slv_pn_product_posts.original_price` (string, base64-like per Q-03) | Decode per mapping L2 §1.3 at scale 4. NULL, empty, or decode error gives NULL. No post, or more than one, also gives NULL. Never `0`. Q-15; mapping L2 §1.2 |
| `slv_pn_product_sale` | `marketing_price` | double | yes | `slv_pn_product_posts.marketing_price` (string) | Same as `original_price`, scale 4. Mapping L2 §1.2, §1.3; Q-15 |
| `slv_pn_product_sale` | `markup_percent` | double | yes | `slv_pn_product_posts.markup_percent` (string) | Same decode at scale 2. Mapping L2 §1.2, §1.3; Q-15 |
| `slv_pn_product_sale` | `is_bookable` | boolean | not stated (Conflicts 5) | `slv_pn_product_variants.product_id`, `status` (string), `deleted` (boolean) | true when at least one variant with the same `product_id` has `status = active` (exact match) and `deleted = false`. Mapping L2 §1.1, §1.2; Q-17 |
| `slv_pn_product_sale` | `row_hash` | string | not stated | business columns above | `sha2` of the struct of business columns. Mapping L2 §1.2; Silver L2 naming row. Column set: Conflicts 6 |
| `slv_pn_product_sale` | `created_at` | timestamp | not stated | — | L2 technical column, first compute. Mapping L2 intro, §1.2 |
| `slv_pn_product_sale` | `updated_at` | timestamp | not stated | — | L2 technical column, changes only when the hash changes. Mapping L2 §1.2; naming row |
| `slv_pn_product_sale` | `deleted_at` | timestamp | yes | — | L2 recompute soft delete when the source product no longer exists. Not the L1 source `deleted_at` (Q-16). Mapping L2 intro, §1.2. Trigger: Conflicts 4 |
| `slv_pn_hotel_room_offer` | `room_type_id` | string | no (key) | `slv_pn_hotel_room_types.id` | 1-1, key. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `status` | string | as source (not declared) | `slv_pn_hotel_room_types.status` | 1-1, case kept. Mapping L2 §2.2; Q-17 |
| `slv_pn_hotel_room_offer` | `available_rooms` | int | as source (not declared) | `slv_pn_hotel_room_types.available_rooms` | 1-1. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `max_occupancy` | int | as source (not declared) | `slv_pn_hotel_room_types.max_occupancy` | 1-1. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `adult_capacity` | int | as source (not declared) | `slv_pn_hotel_room_types.adult_capacity` | 1-1. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `child_capacity` | int | as source (not declared) | `slv_pn_hotel_room_types.child_capacity` | 1-1. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `view_type` | string | as source (not declared) | `slv_pn_hotel_room_types.view_type` | 1-1. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `deleted` | boolean | as source | `slv_pn_hotel_room_types.deleted` (extract technical column, `TECH_COLUMNS`) | 1-1 copy of the L1 extract flag (true when `op = d`). Mapping L2 §2.2; Q-16 |
| `slv_pn_hotel_room_offer` | `is_bookable` | boolean | no: §2.1 defines both the true and the NULL→false cases | `status`, `available_rooms`, `deleted` | true when `status = Active` (exact match), `available_rooms > 0`, and `deleted = false`. NULL `available_rooms` gives false. Mapping L2 §2.1, §2.2; Q-17 |
| `slv_pn_hotel_room_offer` | `row_hash` | string | not stated | business columns above | `sha2` of the struct of business columns. Mapping L2 §2.2. Column set: Conflicts 6 |
| `slv_pn_hotel_room_offer` | `created_at` | timestamp | not stated | — | L2 technical column. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `updated_at` | timestamp | not stated | — | L2 technical column, changes only when the hash changes. Mapping L2 §2.2 |
| `slv_pn_hotel_room_offer` | `deleted_at` | timestamp | yes | — | L2 soft delete when the source room no longer exists (Q-16 distinction). Mapping L2 §2.2. Trigger: Conflicts 4 |
| `slv_pn_hotel_rate_offer` | `rate_plan_id` | string | no (key) | `slv_pn_hotel_rate_plans.id` | 1-1, key. Mapping L2 §3.2 |
| `slv_pn_hotel_rate_offer` | `status` | string | as source (not declared) | `slv_pn_hotel_rate_plans.status` | 1-1, case kept. Mapping L2 §3.2; Q-17 |
| `slv_pn_hotel_rate_offer` | `meal_plan` | int | as source (not declared) | `slv_pn_hotel_rate_plans.meal_plan` | 1-1, numeric value kept (0–4), no label column. Mapping L2 §3.2, §3.3 |
| `slv_pn_hotel_rate_offer` | `valid_from` | timestamp | yes | `slv_pn_hotel_rate_plans.valid_from` (timestamp, L1 rule `EPOCH_S_TS`) | 1-1; NULL stays NULL. No sale window or sale flag derived from it. Cell 15 only casts it to string for `variants_json`. Mapping L2 §3.1, §3.2; Q-19 |
| `slv_pn_hotel_rate_offer` | `valid_to` | timestamp | yes | `slv_pn_hotel_rate_plans.valid_to` (timestamp, L1 rule `EPOCH_S_TS`) | Same as `valid_from`. Mapping L2 §3.1, §3.2; Q-19 |
| `slv_pn_hotel_rate_offer` | `row_hash` | string | not stated | business columns above | `sha2` of the struct of business columns. Mapping L2 §3.2. Column set: Conflicts 6 |
| `slv_pn_hotel_rate_offer` | `created_at` | timestamp | not stated | — | L2 technical column. Mapping L2 §3.2 |
| `slv_pn_hotel_rate_offer` | `updated_at` | timestamp | not stated | — | L2 technical column, changes only when the hash changes. Mapping L2 §3.2 |
| `slv_pn_hotel_rate_offer` | `deleted_at` | timestamp | yes | — | L2 soft delete when the source rate plan no longer exists (Q-16 distinction). Mapping L2 §3.2. Trigger: Conflicts 4 |

## Lineage

| table | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `slv_pn_product_sale` | None directly. Bronze reaches silver L1 through `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` (mapping L1 intro), which this design leaves unchanged | `lh_vv_silver.dbo.slv_pn_products` (`id`, `metadata`); `slv_pn_product_posts` (`id`, `external_id`, `deleted`, `original_price`, `marketing_price`, `markup_percent`); `slv_pn_product_variants` (`product_id`, `status`, `deleted`) | None |
| `slv_pn_hotel_room_offer` | None directly | `lh_vv_silver.dbo.slv_pn_hotel_room_types` (`id`, `status`, `available_rooms`, `max_occupancy`, `adult_capacity`, `child_capacity`, `view_type`, `deleted`) | None |
| `slv_pn_hotel_rate_offer` | None directly | `lh_vv_silver.dbo.slv_pn_hotel_rate_plans` (`id`, `status`, `meal_plan`, `valid_from`, `valid_to`) | None |

None of the three tables reads `ai_poi`, `ai_enriched_poi`, `slv_enr_poi_destination`, or any gold table. The destination join through product → POI → `slv_enr_poi_destination` happens at Gold and is outside this design (Q-14).

## Conflicts and questions

1. **Missing `proposal.md`.** The handoff asks this design to cite `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`, but the task folder has no `proposal.md`. The author input confirms there is none. This design therefore cites mapping L2 and Q-19 instead. Open question: should the three L2 tables be registered in `ctrl_cfg_schema_registry` and/or `TABLE_SPECS` / `TABLE_CONFIGS`? Nothing in the settled files says so, and mapping L2 intro says the document "chưa phải DDL".
2. **Naming conflict, closed by Q-19.** `02_NAMING_CONVENTION.md` §1 lists Silver L2 as `slv_poi_<chủ đề>`, with the L2/gold prefix chosen by topic. The three tables use the source prefix `slv_pn_`. Q-19 and the mapping L2 intro ("Nguồn chỉ là partner, nên prefix `slv_pn_`") settle the names. No rename.
3. **Node notebook unknown.** None of the settled files names the notebook that computes the three L2 tables, and no notebook in the repository mentions them. Which node notebook owns each table?
4. **When `deleted_at` is set on deleted sources.** Mapping L2 §1.1 keeps one row per `slv_pn_products.id` "kể cả product đã `deleted`", while §1.2 sets `deleted_at` when "product nguồn không còn". Neither says whether an L1 row with `deleted = true` (`op = d`) means the source "no longer exists" (set L2 `deleted_at`) or a kept row with NULL `deleted_at`. Room offer (§2.2) has the same open question; it also copies `deleted` 1-1. Rate offer (§3) has no `deleted` column and does not say whether rate plans with `deleted = true` are kept. All three triggers need a decision.
5. **`slv_pn_product_sale.is_bookable` when no variant qualifies.** Mapping L2 §1.1 defines only the true case. Unlike room offer (§2.1), it does not say whether no matching variant gives `false` or NULL. It also does not say whether the product's own `status` or `deleted` affects the flag.
6. **`row_hash` column set.** Each mapping table says "`sha2` của struct các cột nghiệp vụ ở trên". It does not say whether the key column (`product_id`, `room_type_id`, `rate_plan_id`) is in the struct, or what the column order is. The naming row gives `sha2(to_json(struct(...)), 256)` but not the list.
7. **Nullability not declared.** `TABLE_CONFIGS` and the mappings do not declare nullability for the 1-1 columns or for `created_at` / `updated_at`. This design marks them "as source (not declared)" or "not stated" and does not invent NOT NULL constraints.
8. **Value type of `metadata.holiday_product_post_id`.** Q-05 confirms the key exists on 41/41 rows. The evidence does not print the JSON value type. The join compares it with `slv_pn_product_posts.external_id` (string). Should the extracted value be compared as a string? No `json_path` beyond the key name shown in mapping L2 §1.2 is assumed.
9. **Price decode reference.** Mapping L2 §1.1 points to `mapping_legacy_ai_product.md` §1.4, which this run was not allowed to read. The design uses only the mapping L2 §1.3 sequence: NULL/boolean gives NULL; a number is kept; a numeric string is parsed; otherwise base64 → signed big-endian integer / `10^scale`; failure or empty gives NULL; no `0`. Because L1 types all three prices as `string` (Q-03), the "number is kept" branch should not fire. Please confirm.
10. **`valid_from` / `valid_to` values not probed.** L1 declares both as `timestamp` with rule `EPOCH_S_TS` (mapping L1 §13.2), and the probe did not read them. Cell 15 read them as `long` and cast to string. L2 copies the L1 timestamp 1-1 and inherits any epoch-unit issue. This relates to L1 open question 4, which this design leaves open.
11. **Q-11 stale clauses, closed by Q-19.** The author input flags "2 bảng mới" and "Tài liệu L2 chưa tạo" as stale. The current ledger row for Q-11 has already been edited in place to defer to Q-19, and the L2 mapping file exists. No action in this design.
