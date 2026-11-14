# Model design: 20261112-enr-poi-append-to-merge

## Scope

- Base task: `20261112-enr-poi-append-to-merge`. It switches `lh_vv_gold.enr.gld_enr_poi_info` and `lh_vv_gold.enr.gld_enr_poi_review` from APPEND to the existing gold MERGE.
- `proposal.md` does not exist. Its sections `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` therefore cannot be cited. This design does not invent their content. See Conflicts item 1.
- Ledger rows implemented (`decision.md`, `## Quyết định hiện hành`):
  - D-MERGE-1: `sql_merge_target` is the only gold target MERGE. It runs when `load_mode = RECOMPUTE` and `write_mode = MERGE`.
  - D-RISK-1: switch both tables to MERGE. Review data is deleted and re-initialised later by the Fabric DEV runbook, not in this task. `gld_enr_poi_info` is not deleted. Review edges stay `is_active = 0`.
  - D-COL-1: add only `row_hash` STRING and `deleted_at` TIMESTAMP to both tables. No business-column change. No grain change.
- Architecture input: `architecture.md` §0 gap B1, resolved by D-COL-1, and §5 row A1 (reuse `sql_merge_target` through `run_node` RECOMPUTE and add the two columns).
- Out of scope: new MERGE logic, business-column changes, `gld_enr_poi_coordinate`, and APIs.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.enr.gld_enr_poi_info` | gold | one row per `poi_id`, unchanged (`docs/context/gld_enr_poi_info_review.md`, `gld_enr_poi_info` table, Grain row) | `NB_ENR_POI_INFO` |
| `lh_vv_gold.enr.gld_enr_poi_review` | gold | one row per `review_id`, unchanged (`docs/context/gld_enr_poi_info_review.md`, `gld_enr_poi_review` table, Grain row) | `NB_ENR_POI_REVIEW` |

Under MERGE, a row whose key has left the source is kept, with `deleted_at` set. So the table still has one row per key. That includes soft-deleted keys, and live keys are the rows where `deleted_at IS NULL`.

## Keys

| table | primary key | business key | foreign keys |
|---|---|---|---|
| `gld_enr_poi_info` | `poi_id`, the NodeSpec `pk` (`architecture.md` §1) | `poi_id` | Not applicable. |
| `gld_enr_poi_review` | `review_id`, the NodeSpec `pk` (`architecture.md` §1) | `review_id` | `poi_id` is a logical reference to the POI. No enforced FK is documented. |

- `poi_id` formula source: `AGENTS.md` §7. Third-party `poi_id = uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`). Partner `poi_id = uuid_format(md5(concat(id, 'partner')))`. This task does not change either formula.
- `review_id`: this design does not change its derivation. The source expression is in `NB_ENR_POI_REVIEW`, which was not in the read set for this design.
- `row_hash` and `deleted_at` are not keys. The MERGE `ON` clause stays on `pk` only (`sql_merge_target(fq, view, cols, pk, soft_delete_set)`).

## Columns

Only the affected columns are listed. All business columns keep the names, types, and order shown in `docs/context/gld_enr_poi_info_review.md`.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_enr_poi_info` | `row_hash` | STRING | yes | library: `add_row_hash` in `NB_LIB_TRANSFORM_SLV_GLD` | D-COL-1. The value is the library hash of the business columns: `sha2(to_json(struct(business columns in DataFrame order minus hash_exclude)), 256)`, with timestamps hashed as `unix_micros` (lib §6 markdown; `02_NAMING_CONVENTION.md` §5.2). It excludes the technical columns (comment on `TECH_COLUMNS`). Nullable because rows that exist before the first MERGE have no hash. `sql_merge_target` treats `t.row_hash IS NULL` as changed. |
| `gld_enr_poi_info` | `created_at` | TIMESTAMP | yes (unchanged) | library | Existing column, no type change. Under `sql_merge_target` it is set to `current_timestamp()` on INSERT only, so it means first-insert time and no longer batch time (`architecture.md` §0 B1). |
| `gld_enr_poi_info` | `updated_at` | TIMESTAMP | yes (unchanged) | library | Existing column, no type change. `sql_merge_target` sets it on INSERT, on a matched UPDATE (hash changed, hash NULL, or revived from soft delete), and on soft delete. |
| `gld_enr_poi_info` | `deleted_at` | TIMESTAMP | yes | library: `sql_merge_target` | D-COL-1. NULL means the `poi_id` is in the current source snapshot. Non-null means the `poi_id` left the source: the `WHEN NOT MATCHED BY SOURCE AND t.deleted_at IS NULL` branch set it to `current_timestamp()`, and the row is kept. It is reset to NULL when the key returns (matched UPDATE). |
| `gld_enr_poi_review` | `row_hash` | STRING | yes | library: `add_row_hash` | D-COL-1. Same rule as `gld_enr_poi_info.row_hash`. |
| `gld_enr_poi_review` | `created_at` | TIMESTAMP | yes (unchanged) | library | Same rule as `gld_enr_poi_info.created_at`. |
| `gld_enr_poi_review` | `updated_at` | TIMESTAMP | yes (unchanged) | library | Same rule as `gld_enr_poi_info.updated_at`. |
| `gld_enr_poi_review` | `deleted_at` | TIMESTAMP | yes | library: `sql_merge_target` | D-COL-1. Same rule as `gld_enr_poi_info.deleted_at`, keyed on `review_id`. D-RISK-1: the Fabric DEV runbook deletes the existing review data and re-runs init before MERGE testing, so no legacy APPEND row should carry a NULL `row_hash` into the review MERGE. |

Target column order (`TECH_COLUMNS` and `create_target` in `NB_LIB_TRANSFORM_SLV_GLD`): business columns, then `row_hash`, `created_at`, `updated_at`, `deleted_at`. For the physical order on the existing `gld_enr_poi_info` after a column add, see Conflicts item 3.

`created_at` and `updated_at` appear in the table because D-COL-1 places the new columns around them in `TECH_COLUMNS` and because their meaning changes. Their type and nullability do not change.

## Lineage

| table | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `gld_enr_poi_info` | None (not direct). | `lh_vv_silver.dbo.slv_poi_entity_non_enrich` (spine), `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`, `slv_enr_poi_info_multi_lang` (`poi_id` only, for the flag), and `slv_enr_poi_destination` (`poi_id` only, for the flag). Source: `docs/context/gld_enr_poi_info_review.md`. | None. The MERGE reads its own target in `diff_counts` and `MERGE`. That is a write-target read, not an input. |
| `gld_enr_poi_review` | None (not direct). | `lh_vv_silver.dbo.slv_3p_poi_review` and `slv_enr_poi_review_multi_lang` (`review_id` only, for the flag). Source: `docs/context/gld_enr_poi_info_review.md`. | None. Same note on the target read. |

The new technical columns come from the library, not from any upstream table. Gold never reads gold (`AGENTS.md` §7).

## Conflicts and questions

1. `proposal.md`, `problem-analysis.md`, and `requirements-analysis.md` do not exist, so `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. Should this model design be revised after `proposal.md` exists? Or do D-COL-1 and `architecture.md` §5 A1 stand in for the proposal? Any `ctrl_cfg_schema_registry` rows for the two new columns are unknown, and this design does not define them.
2. `soft_delete_set`: `02_NAMING_CONVENTION.md` §5.2 says a gold soft delete also sets `is_active = false`. Neither table has an `is_active` business column, and D-COL-1 forbids adding one. Should `soft_delete_set` stay empty for both nodes, so that soft delete sets only `deleted_at` and `updated_at`? Please confirm. This design does not add a column for it.
3. Physical column order: `ALTER TABLE ADD COLUMNS` on the existing `gld_enr_poi_info` gives business, `created_at`, `updated_at`, `row_hash`, `deleted_at`. `TECH_COLUMNS` and `create_target` give business, `row_hash`, `created_at`, `updated_at`, `deleted_at`. The `ensure_target` body was not read in full. Does its `wanted` check compare order or only the set of columns? Is the difference between the migrated `gld_enr_poi_info` and a freshly initialised `gld_enr_poi_review` acceptable? `init_tables` in `NB_SETUP_INITIAL_DDL` and the lists pinned in `tests/test_initial_ddl_contract.py` need one agreed order.
4. `hash_exclude`: the NodeSpec values for these two nodes are unknown. Should every business column be hashed? This design assumes the default `()` only if you confirm it.
5. Hash stability: the lib requires arrays to be sorted in `build`. `service_flag` is documented as a sorted JSON array. `review_json` (up to 20 reviews) has no ordering rule in the files read. If its order is not deterministic, `row_hash` changes on every run. Is `review_json` ordering deterministic in `NB_ENR_POI_INFO`? This design does not invent an order.
6. Doc drift: `docs/context/gld_enr_poi_info_review.md` describes `created_at` and `updated_at` as "Mốc ghi batch" and does not list `row_hash` or `deleted_at`. It needs to describe first-insert `created_at`, change-driven `updated_at`, and the two new columns. The file is in `scope.files`. Please confirm that the update belongs to this task.
7. Readers outside the lib: `ctx.input` filters `deleted_at IS NULL` and drops the four technical columns only for nodes that read through the lib. Do any readers of `gld_enr_poi_info` or `gld_enr_poi_review` outside `run_node`, such as enrich notebooks or exports, need to filter `deleted_at IS NULL`? I did not open `notebooks_lgc/` or `services/`.
8. `docs/diagram/VSVN_SLV_GLD_DATA_MODEL.drawio` was not in the read set. Does it show technical columns (`row_hash`, `created_at`, `updated_at`, `deleted_at`) for gold tables? If it does, it should join `scope.files` and show the two new columns on both tables (`architecture.md` §0 B2).
9. `review_id` derivation was not in the read set. This design assumes it stays unchanged and does not restate it. Please confirm that nothing in this task touches it.
