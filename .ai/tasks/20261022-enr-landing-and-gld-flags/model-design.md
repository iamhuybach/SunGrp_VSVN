# Model design — 20261022-enr-landing-and-gld-flags

## Scope

Base task: `20261022-enr-landing-and-gld-flags` ("Silver enrich landing tables and gold enrich flags"), status `triage`, `architecture_required: true`.

The task has no `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md`. So this design cites no `## Dòng thay đổi` or `## ctrl_cfg_schema_registry` section. The accepted source is `request.md` (through the author input) and the `Quyết định hiện hành` ledger in `decision.md`:

- D-01: landing prefix `slv_enr_`, schema `lh_vv_silver.dbo`, no new schema.
- D-02: landing columns. The column is `description`, not `descrption`. No `lang` column on the review landing table. `created_at` and `updated_at` are nullable `TIMESTAMP`. No `UNIQUE` and no composite key beyond the stated `NOT NULL`.
- D-03: landing grain and unique key are not decided. Flags do not depend on grain.
- D-04: a flag checks only that the key exists. Enrich content is not copied to gold. A key that does not match gives false.
- D-05: drop `district` and `destination_name` from `gld_enr_poi_info`. Keep `street`, `ward`, `city`, `full_address`.
- D-06: the info contract comes from `NB_CREATE_DDL` cell `enrinfopy` `INFO_COLS`. The review contract comes from cell `enrddlpy` `REVIEW_COLS`.
- D-07: columns added to an existing gold table are nullable in `ALTER`. The node writes true or false.
- D-08: no loader notebook for the three landing tables.

This design covers:
- the DDL model of three new landing tables;
- removing two columns from `lh_vv_gold.enr.gld_enr_poi_info` and adding two flag columns;
- adding one flag column to `lh_vv_gold.enr.gld_enr_poi_review`.

The DDL change applies to both DDL notebooks (`docs/context/02_NAMING_CONVENTION.md` §2.1). `ctrl_cfg_schema_registry`: Not applicable. No registry row is added.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` | silver (enrich landing) | Undecided (D-03). Only `poi_id` NOT NULL is declared. | None. DDL only (D-08). |
| `lh_vv_silver.dbo.slv_enr_poi_destination` | silver (enrich landing) | Undecided (D-03). Only `poi_id` NOT NULL is declared. | None. DDL only (D-08). |
| `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang` | silver (enrich landing) | Undecided (D-03). Only `review_id` NOT NULL is declared. | None. DDL only (D-08). |
| `lh_vv_gold.enr.gld_enr_poi_info` | gold | One row per `poi_id` (`NB_ENR_POI_INFO` cell `36415d3b` `SPEC.pk=("poi_id",)`). Unchanged. | `NB_ENR_POI_INFO` |
| `lh_vv_gold.enr.gld_enr_poi_review` | gold | One row per `review_id` (`NB_ENR_POI_REVIEW` cell `04339a06` `SPEC.pk=("review_id",)`). Unchanged. | `NB_ENR_POI_REVIEW` |

Notes:
- `slv_enr_poi_destination` is a different table from the L2 node `slv_poi_destination` (N5, `docs/context/01_DATA_MODEL.md` §6). This task neither reads nor changes N5.
- The `slv_enr_` prefix is not in `docs/context/02_NAMING_CONVENTION.md` §1. The user accepted it (D-01).

## Keys

`slv_enr_poi_info_multi_lang`
- Primary key: none declared (D-02, D-03).
- Business key: undecided (D-03). See Conflicts 1.
- Foreign key, logical and not enforced: `poi_id` → `gld_enr_poi_info.poi_id`. It is used only for the existence check of `is_enriched_multi_lang` (D-04).

`slv_enr_poi_destination`
- Primary key: none declared (D-02, D-03).
- Business key: undecided (D-03). See Conflicts 1.
- Foreign key, logical: `poi_id` → `gld_enr_poi_info.poi_id`, for `is_enriched_destination` (D-04).

`slv_enr_poi_review_multi_lang`
- Primary key: none declared (D-02, D-03).
- Business key: undecided (D-03). See Conflicts 1.
- Foreign key, logical: `review_id` → `gld_enr_poi_review.review_id`, for `is_enriched_multi_lang` (D-04). `poi_id` is carried but not used by any flag.

`gld_enr_poi_info`
- Primary key: `poi_id` (`SPEC.pk`, cell `36415d3b`; `STRING NOT NULL` in `enrinfopy` `INFO_COLS` and `NB_SETUP_INITIAL_DDL` `init_tables`). Unchanged.
- `poi_id` formula source:
  - Third-party rows follow `AGENTS.md` §7: `uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`).
  - For partner rows, the notebook and `AGENTS.md` §7 disagree (Conflicts 5).
  - This task does not recompute `poi_id`. The flag matches the `poi_id` already stored in gold.

`gld_enr_poi_review`
- Primary key: `review_id` (`SPEC.pk`, cell `04339a06`; `STRING NOT NULL` in `enrddlpy` `REVIEW_COLS` and `init_tables`). Unchanged.
- `review_id` is taken as-is from `slv_3p_poi_review`. This task does not recompute it.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_enr_poi_info_multi_lang` | `poi_id` | STRING | no | None in this task (no loader, D-08) | request column list; D-02 |
| `slv_enr_poi_info_multi_lang` | `lang` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_info_multi_lang` | `time_to_spend` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_info_multi_lang` | `best_time` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_info_multi_lang` | `cost_vnd` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_info_multi_lang` | `description` | STRING | yes | None (D-08) | D-02 (typo `descrption` corrected) |
| `slv_enr_poi_info_multi_lang` | `created_at` | TIMESTAMP | yes | None (D-08) | D-02 (same type as `gld_enr_poi_info.created_at`) |
| `slv_enr_poi_info_multi_lang` | `updated_at` | TIMESTAMP | yes | None (D-08) | D-02 |
| `slv_enr_poi_destination` | `poi_id` | STRING | no | None (D-08) | request column list; D-02 |
| `slv_enr_poi_destination` | `street` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_destination` | `ward` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_destination` | `district` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_destination` | `city` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_destination` | `full_address` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_destination` | `created_at` | TIMESTAMP | yes | None (D-08) | D-02 |
| `slv_enr_poi_destination` | `updated_at` | TIMESTAMP | yes | None (D-08) | D-02 |
| `slv_enr_poi_review_multi_lang` | `review_id` | STRING | no | None (D-08) | request column list; D-02 |
| `slv_enr_poi_review_multi_lang` | `poi_id` | STRING | yes | None (D-08) | request column list; D-02 |
| `slv_enr_poi_review_multi_lang` | `review_text` | STRING | yes | None (D-08) | request column list; D-02 (no `lang` column) |
| `slv_enr_poi_review_multi_lang` | `created_at` | TIMESTAMP | yes | None (D-08) | D-02 |
| `slv_enr_poi_review_multi_lang` | `updated_at` | TIMESTAMP | yes | None (D-08) | D-02 |
| `gld_enr_poi_info` | `district` | STRING | yes | Removed. Today it is `e.ward` (cell `36415d3b`, `COL-041`). | D-05: drop from the contract and from the build select |
| `gld_enr_poi_info` | `destination_name` | STRING | yes | Removed. Today it is `e.city` (cell `36415d3b`, `COL-042`). | D-05: drop from the contract and from the build select |
| `gld_enr_poi_info` | `is_enriched_multi_lang` | BOOLEAN | yes | `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang.poi_id` | D-04, D-07: true if gold `poi_id` has at least one row in the landing table, otherwise false. The node writes true or false, never NULL. |
| `gld_enr_poi_info` | `is_enriched_destination` | BOOLEAN | yes | `lh_vv_silver.dbo.slv_enr_poi_destination.poi_id` | D-04, D-07: true if gold `poi_id` has at least one row in the landing table, otherwise false. |
| `gld_enr_poi_review` | `is_enriched_multi_lang` | BOOLEAN | yes | `lh_vv_silver.dbo.slv_enr_poi_review_multi_lang.review_id` | D-04, D-07: true if gold `review_id` has at least one row in the landing table, otherwise false. |

Unchanged columns:
- `gld_enr_poi_info` keeps `street`, `ward`, `city`, `full_address` as they are today (`e.street`, `e.ward`, `e.city`, `e.full_address`; D-05). Every other `enrinfopy` `INFO_COLS` column is also unchanged.
- In `gld_enr_poi_review`, every `enrddlpy` `REVIEW_COLS` column and its logic is unchanged.

Flag rules (D-04):
- A flag is an existence test on the key only. It must not fan out the gold row, whatever the landing grain. No landing content column (`time_to_spend`, `best_time`, `cost_vnd`, `description`, address parts, `review_text`) is read into gold.
- Gold `gld_enr_poi_info` already has columns named `time_to_spend`, `best_time`, `cost_vnd`. They keep their current computed rules (cell `36415d3b`) and are not replaced by the landing values.

Where the contract lists change:
- `tests/test_enr_poi_contract.py`:
  - `INFO` loses `district` and `destination_name` and gains the two flags.
  - `REVIEW` gains `is_enriched_multi_lang`.
  - `COORD` (`gld_enr_poi_coordinate`) is out of scope and keeps its own `district` and `destination_name`.
- `NB_SETUP_INITIAL_DDL` `init_tables`: specs for both gold tables, plus three new landing specs.

## Lineage

| table | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `slv_enr_poi_info_multi_lang` | None (no bronze source in this task) | None | None |
| `slv_enr_poi_destination` | None | None | None |
| `slv_enr_poi_review_multi_lang` | None | None | None |
| `gld_enr_poi_info` | None | Today: `slv_poi_entity_non_enrich` (spine), `slv_poi_amenity`, `slv_3p_poi_rating`, `slv_3p_poi_price`, `slv_3p_poi_opening_hours`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns` (cell `36415d3b` `SPEC.inputs`). New: `slv_enr_poi_info_multi_lang` (`poi_id` only) and `slv_enr_poi_destination` (`poi_id` only). | None |
| `gld_enr_poi_review` | None | Today: `slv_3p_poi_review` (cell `04339a06` `SPEC.inputs`). New: `slv_enr_poi_review_multi_lang` (`review_id` only). | None |

Gold never reads gold. Both flags are computed from silver landing tables, not from another gold table.

## Conflicts and questions

1. **Landing grain and unique key (D-03).** The repo does not decide a unique key for any landing table, and the author must not pick one. The flags do not need one. The key matters only if a future loader uses `MERGE` or must prevent duplicates. Candidates the files allow, with no recommendation:
   - `slv_enr_poi_info_multi_lang`:
     - (a) no key, append;
     - (b) `poi_id`;
     - (c) (`poi_id`, `lang`), which would require `lang` NOT NULL. D-02 does not declare that.
   - `slv_enr_poi_destination`:
     - (a) no key;
     - (b) `poi_id`.
   - `slv_enr_poi_review_multi_lang`:
     - (a) no key;
     - (b) `review_id`.
     - A language-level key is impossible because D-02 forbids a `lang` column.

   D-02 forbids adding `UNIQUE` in this task. The choice belongs to the task that writes the loader (D-08).

2. **Flag freshness after a landing row changes.**
   - `NB_ENR_POI_INFO` `build` recomputes only `changed` `poi_id`s, derived from its declared inputs (`ctx.changed`, `_role_keys`, `_i18n_keys`).
   - `NB_ENR_POI_REVIEW` `build` recomputes only `review_id`s changed in `slv_3p_poi_review`.
   - So when a landing row is added or removed and nothing else changes for that key, the stored flag stays stale.

   The files do not decide whether:
   - the landing tables become node inputs that feed changed keys;
   - they need `ctrl_mng_pipeline_config` edges on `PL_VV_TRANS_SLV_TO_ENR_15P` (a ctrl change in both DDL notebooks, outside this author's scope);
   - staleness until the next upstream change is accepted.

   This is for the Architect.
3. **Existing gold rows after `ALTER`.** D-07 makes the new flag columns nullable. Rows already in gold hold NULL until the node rewrites them. The files do not decide whether a full refresh, `p_force`, or a backfill sets them to true or false. This is for the Architect.
4. **Physical removal of `district` and `destination_name` in an existing environment.**
   - D-05 removes them from the contract and from the build.
   - `docs/context/02_NAMING_CONVENTION.md` §2.1 rule 3 describes only `ALTER TABLE … ADD COLUMNS` for patch cells. Rule 5 forbids dropping tables that hold data.
   - The `enrinfopy` patch cell stops when the table schema does not equal its contract.

   The files do not say whether the existing table:
   - (a) drops the two columns with `ALTER TABLE … DROP COLUMN`, which needs Delta column mapping;
   - (b) keeps them physically while the node stops writing them;
   - (c) goes through a reset like the one cited for `enrinfopy`.

   The user must decide this.
5. **Partner `poi_id` formula disagreement.**
   - `AGENTS.md` §7 gives `uuid_format(md5('partner_portal' || business_service_id))` and says no current notebook applies it.
   - `NB_ENR_POI_INFO` `_vi_i18n` comments that the partner `poi_id` is `uuid_md5(business_service_id, 'partner')`, the same as `NB_SLV_POI_ENTITY_NON_ENRICH`.
   - The flags match the `poi_id` already stored in gold, so a future landing writer must write that stored value or partner flags will be false (D-04).

   Which formula a future landing writer must follow is open. This task does not fix it.
6. **Column position of the new flags.**
   - `tests/test_enr_poi_contract.py` asserts that the `BEGIN_INFO_SELECT` aliases plus `created_at`, `updated_at` equal `INFO` in order.
   - `ALTER TABLE … ADD COLUMNS` appends after `updated_at`, while `NB_SETUP_INITIAL_DDL` `init_tables` can place the flags anywhere.

   The request does not state the flag position in `INFO` and `REVIEW`, or whether patched and fresh environments must have the same physical order. Decide before the test lists change.
7. **Where the new info contract lives.**
   - D-06 names `enrinfopy` `INFO_COLS` as the current contract, and the test reads that cell as `patch`.
   - §2.1 rule 4 forbids editing old `NB_CREATE_DDL` cells, so the new contract must live in a new patch cell.
   - The test's source cell for `INFO` and `REVIEW` must then move to that new cell.

   The files do not name the new cell id. This is for the implementer, not the model.
8. **Null landing keys.** `slv_enr_poi_review_multi_lang.poi_id` is nullable (D-02). It is not used by any flag, so a NULL value does not affect `gld_enr_poi_review.is_enriched_multi_lang`. No question for this task. Recorded so that no reviewer reads `poi_id` as the review flag key.
