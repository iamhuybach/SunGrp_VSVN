# Model design: 20261023-entity-opening-hours-passthrough

## Scope

- Base task: `20261023-entity-opening-hours-passthrough` (`task-state.yaml` status `triage`, signals `data_model_change`, `runtime_proof_required`).
- `proposal.md`, `problem-analysis.md` and `requirements-analysis.md` do not exist. This design therefore cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. The locked rules are `request.md` (`## User outcome`, `## Scope`, `## Acceptance criteria`, `## Constraints`) and author-input `## Locked model` items 1–9.
- `decision.md` `## Quyết định hiện hành` has no rows. No ledger row is implemented. D-17 is the code decision tag in `NB_ENR_POI_INFO` cell 3, not a row in this task's ledger.
- This design covers:
  - the new silver column `slv_poi_entity_non_enrich.opening_hours_text` (Locked model 1–4, 6, 8, 9);
  - the gold passthrough `gld_enr_poi_info.opening_hours_text` (Locked model 5);
  - the quality checks that move to silver (Locked model 7).
- Ctrl edges, orchestration, watermarks, and commit order belong to the Architect. They are not covered here.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_poi_entity_non_enrich` | Silver L2 (N6, `01_DATA_MODEL.md` §6) | one row per `poi_id`; unchanged (Locked model 1) | `NB_SLV_POI_ENTITY_NON_ENRICH` (cell 4 `SPEC`, `write_mode="MERGE"`) |
| `lh_vv_gold.enr.gld_enr_poi_info` | Gold (`01_DATA_MODEL.md` §7) | one row per `poi_id`; unchanged (`SPEC.pk=("poi_id",)`, `write_mode="APPEND"`) | `NB_ENR_POI_INFO` (cell 3 `SPEC`) |
| `lh_vv_silver.dbo.slv_3p_poi_opening_hours` | Silver L1 3P (read only, new input of N6) | not shown in the files read; see Question 3 | none (L1 extract, created by the lib from the registry) |
| `lh_vv_silver.dbo.slv_pn_business_service_i18ns` | Silver L1 partner (read only, already an N6 input) | not shown in the files read; the files show only the columns `business_service_id`, `locale`, `amentities`, `deleted` | none (L1 extract) |

## Keys

### `slv_poi_entity_non_enrich`

- **Primary key:** `poi_id` (`SPEC.pk=("poi_id",)`, cell 4). Unchanged.
- **`poi_id` formula** (Locked model 9, `request.md` Constraints, N6):
  - **Google:** `poi_id` is carried from `slv_3p_poi.poi_id` (`POI_COLS`, `_google`).
  - **Partner:** `uuid_md5(F.col("id"), F.lit(PARTNER))` with `PARTNER = "partner"` (cell 4 `_partner`, comment `D2`). `id` is `slv_pn_business_services.id` joined to the i18n `business_service_id`.
  - This is the same function and argument order as `_vi_i18n` in `NB_ENR_POI_INFO` cell 3: `uuid_md5(F.col("business_service_id"), F.lit(PARTNER))`.
  - Do not use `poi_uid` or `partner_portal`.
- **Business key:** (`source_name`, `source_id`). The files show only one uniqueness check on it: `unique_checks` `partner_source_id_unique` on `source_id` where `source_name = 'partner'`.
- **Foreign keys this column adds** (logical; no Delta constraint):
  - Google rows: `poi_id` → `slv_3p_poi_opening_hours.poi_id`, left join (the gold cell 3 join is `F.col("e.poi_id") == F.col("oh.poi_id")`, `left`).
  - Partner rows: `source_id` (`= business_service_id`) → `slv_pn_business_service_i18ns.business_service_id`, filtered to `locale = 'vi'` and non-deleted. This is the same key path `_partner_hours` uses through `_vi_i18n`.

### `gld_enr_poi_info`

- **Primary key:** `poi_id` (`SPEC.pk`). Unchanged.
- **Foreign key:** `poi_id` → `slv_poi_entity_non_enrich.poi_id`. This is the existing spine join (`spine = ctx.input("entity")`). `opening_hours_text` is read through this key only (Locked model 5).

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_poi_entity_non_enrich` | `opening_hours_text` | `STRING` | yes | **Google:** `slv_3p_poi_opening_hours.periods_json`, left join on `poi_id`. **Partner:** `get_json_object(slv_pn_business_service_i18ns.amentities, '$.policies.operating_hours')`. **Other sources:** none. | Locked model 1–4. `request.md` Acceptance criteria 1 and Constraints item 1. Move the cell 3 when-chain unchanged: `F.when(google, oh.periods_json).when(source == 'partner', ph.partner_hours)`, with no `otherwise`, where `source = lower(trim(source_name))`. Partner: non-deleted rows (`~coalesce(deleted, false)`), `_vi_i18n` (`locale = 'vi'`, `poi_id = uuid_md5(business_service_id, 'partner')`). A missing key stays null. Other sources stay null. The `amentities` value must come from the **i18n** table (`_partner_hours` reads `ctx.input("i18n")`), not from `slv_pn_business_services.amentities`, which `_partner` reads for `main_category_of`. See Question 2. |
| `gld_enr_poi_info` | `opening_hours_text` | `STRING` | yes | `slv_poi_entity_non_enrich.opening_hours_text` (`e.opening_hours_text`) | Locked model 5. `request.md` Acceptance criteria 2 and 4. Pure passthrough with no Google/partner branch. Name, `STRING` type, and position stay as `NB_CREATE_DDL` cell 35 `enrflagpy` `INFO_COLS`: after `price_level`, before `review_json`. `NB_SETUP_INITIAL_DDL` `TABLE_SPECS` already has the same position and needs no change. No new gold column. |

### DDL placement of the silver column

- **`NB_SETUP_INITIAL_DDL` `TABLE_SPECS`:** add `('opening_hours_text', 'STRING', None)` to the `slv_poi_entity_non_enrich` spec, in place. Per `02_NAMING_CONVENTION.md` §2.1 point 7, the spec must list exactly the `ensure_target` columns in order (build columns, then `TECH_COLUMNS` `row_hash`, `created_at`, `updated_at`, `deleted_at`). The column therefore goes at the same position it takes in `OUT_COLS` (Question 1).
- **`NB_CREATE_DDL`:** add the markdown `[THÊM 23/10] 20261023-entity-opening-hours-passthrough` and one self-contained patch cell: `ALTER TABLE lh_vv_silver.dbo.slv_poi_entity_non_enrich ADD COLUMNS (opening_hours_text STRING)`, run only when the column is missing, nullable, with no `DROP` (Locked model 8, §2.1 points 3 and 5).

### Quality checks (Locked model 7)

| node | kind | name | condition |
|---|---|---|---|
| `NB_SLV_POI_ENTITY_NON_ENRICH` | block | `opening_hours_other_source` | `coalesce(lower(trim(source_name)), '') NOT IN ('google', 'partner') AND opening_hours_text IS NOT NULL` (copied unchanged from cell 3 `block_checks`) |
| `NB_SLV_POI_ENTITY_NON_ENRICH` | warn | `partner_opening_hours_null` | `lower(trim(source_name)) = 'partner' AND opening_hours_text IS NULL` (copied unchanged from cell 3 `warn_checks`) |
| `NB_ENR_POI_INFO` | (not shown) | passthrough match | The files do not define the condition, the check name, or the check kind. See Question 5. |

Both checks are removed from the gold `SPEC`.

## Lineage

| affected table | bronze reads | silver reads | gold reads |
|---|---|---|---|
| `slv_poi_entity_non_enrich` | None directly. The L1 inputs are extracted from `partner_raw_data` (`slv_pn_*`) and `brz_3rd_crawler_poi_stream` (`slv_3p_*`), `02_NAMING_CONVENTION.md` §1. | Existing: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `ref_dictionary_place_type`, `slv_pn_business_services`, `slv_pn_business_service_i18ns`. New input: `slv_3p_poi_opening_hours` (column `periods_json`, key `poi_id`), Locked model 6. `slv_pn_business_service_i18ns` is now also read for `amentities` (it was already an input, `SPEC.inputs["i18n"]`). | None |
| `gld_enr_poi_info` | None | `opening_hours_text` reads only `slv_poi_entity_non_enrich.opening_hours_text` through the spine. Other columns read the same tables as today. Whether `slv_3p_poi_opening_hours` (role `hours`, still used by the changed-key loop `_role_keys`) stays a gold input is decided by the Architect under `request.md` Acceptance criterion 8. `slv_pn_business_service_i18ns` stays while `_i18n_keys` reads it (`request.md` Constraints). | None. The gold node reads only silver tables (including the landing tables `slv_enr_*`). It never reads gold. |

## Conflicts and questions

1. **Position of the silver column (unknown).** Locked model 1 sets the name, type, and nullability, but not the position in `OUT_COLS`. My recommendation: append it as the last build column, after `canonical_candidate` (a new `HOURS_COLS = ("opening_hours_text",)` at the end of `OUT_COLS`), and put it before `row_hash` in `TABLE_SPECS`. However, `ALTER TABLE … ADD COLUMNS` on an existing table puts the column after `deleted_at`, so the physical order differs from the setup DDL. Please confirm the position, and confirm that `ensure_target` and the `MERGE` match columns by name, so this order difference is acceptable.
2. **`amentities` name collision (unknown).** In `_partner`, `base = svc.join(vi, "id")` and `vi` keeps only `id`. So `F.col("amentities")` in the entity notebook means `slv_pn_business_services.amentities`. The cell 3 formula reads `slv_pn_business_service_i18ns.amentities`. The design requires the i18n column, as `_partner_hours` does today. Please confirm that the implementation must bring the i18n `amentities` in under a separate alias, so the silver value equals today's gold value.
3. **Grain of `slv_3p_poi_opening_hours` (unknown).** The files do not show that `poi_id` is unique in this table. A left join with duplicate `poi_id` would duplicate entity rows and break the `poi_id` grain. For `slv_3p_poi_contact`, the entity stops on duplicates (`QualityGateError`). Please confirm whether the same stop-on-duplicate rule applies to `slv_3p_poi_opening_hours`. This design adds no such check.
4. **Type of `periods_json` (unknown).** `_partner` casts every column to `google.schema[c].dataType`, so the silver column type follows the type of `periods_json` on the Google branch. The files do not show that type, but Locked model 1 and gold `INFO_COLS` require `STRING`. Please confirm that `periods_json` is `STRING`, or that an explicit `.cast("string")` is allowed. Without that confirmation, this design adds no cast.
5. **Gold passthrough check (unknown).** Locked model 7 and `request.md` Acceptance criterion 6 say gold checks that its value matches the silver column. Neither file gives a condition, a check name, a kind (block or warn), or a comparison that treats null as equal to null. Please supply them.
6. **Other-source branch is unreachable on the entity (observation, no conflict).** The entity holds only Google rows (`lower(trim(source_name)) = 'google'`) and partner rows (`source_name = 'partner'`). The null value for other sources (Locked model 4) and the `opening_hours_other_source` check therefore hold trivially. The when-chain is still moved unchanged.
7. **Partner rows where i18n `vi` is missing or deleted (observation).** The entity keeps only partner rows that have a live `vi` i18n row (`svc.join(vi, "id")`). Gold today left-joins `_partner_hours` onto the entity spine, so the set of partner rows that have a value matches. Please confirm this observation with no change.
8. **Missing upstream artifacts.** `proposal.md` (`## Dòng thay đổi`, `## ctrl_cfg_schema_registry`) and the ledger rows do not exist, so this design cites `request.md` and the author input. If a proposal is added later, it must be checked against Locked model 1–9.
