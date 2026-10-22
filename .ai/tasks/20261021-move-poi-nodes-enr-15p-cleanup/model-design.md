# Model design — 20261021-move-poi-nodes-enr-15p-cleanup

## Scope

- Base task: `.ai/tasks/20261021-move-poi-nodes-enr-15p-cleanup`. The scope comes from `request.md` sections `User outcome` and `Cách hiểu đang dùng`.
- There is no `proposal.md`, so this design cannot cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. See Conflicts and questions item 1. There is also no `problem-analysis.md` or `requirements-analysis.md`.
- Ledger rows implemented: `decision.md` `Quyết định hiện hành` D-01 to D-04.
  - D-01: the inventory is complete enough to use as the lineage source (INV-2 has 24 rows and INV-4 has 23 rows; neither hit the cap).
  - D-02: the 3 `slv_poi_amenity` edges and the 6 `slv_poi_entity_non_enrich` edges already read from silver on DEV. This design uses them as the current lineage of the two kept nodes.
  - D-03: the coordinate edges, the old info edges, and the `slv_pn_poi` edges are removed. This design shows only the lineage effect. Edge, watermark, and lock deletion belong to the Architect.
  - D-04: remove `lh_vv_gold.enr.gld_enr_poi_coordinate` and `lh_vv_silver.dbo.slv_pn_poi` from the model. Keep `slv_poi_amenity` and `slv_poi_entity_non_enrich` with no change to grain or columns.
- Model change:
  - Removed: `lh_vv_gold.enr.gld_enr_poi_coordinate`, `lh_vv_silver.dbo.slv_pn_poi`.
  - Kept with no change (not redesigned): `slv_poi_entity_non_enrich` (N6), `slv_poi_amenity` (N7), `gld_enr_poi_info`, `gld_enr_poi_review`, `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`.
  - Only change to kept tables: `gld_enr_poi_info` stops listing `slv_3p_poi`, `slv_3p_poi_address`, and `slv_3p_poi_contact` as inputs (D-03).
- Out of scope: pipeline names as a design choice, ctrl edges, watermarks, locks, ordering, DROP mechanics, and rollback. These belong to the Architect.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.enr.gld_enr_poi_coordinate` (removed, D-04) | gold, schema `enr` | Not declared in `NB_SETUP_INITIAL_DDL` cell `init_tables`. The only NOT NULL column is `poi_id`, and no PK is shown. See question 5. | `NB_ENR_POI_COORDINATE` (INV-2 `nb_name`; removed per `request.md` Cách hiểu đang dùng) |
| `lh_vv_silver.dbo.slv_pn_poi` (removed, D-04) | silver, schema `dbo` | One row per `poi_id`: `NodeSpec.pk=("poi_id",)` in `NB_SLV_PN_POI` cell `379af200` | `NB_SLV_PN_POI` (cell `379af200`; INV-2 `nb_name`) |
| `lh_vv_silver.dbo.slv_poi_entity_non_enrich` (kept) | silver L2 | `poi_id` (`01_DATA_MODEL.md` N6). Unchanged. | `NB_SLV_POI_ENTITY_NON_ENRICH` (N6; INV-4 `flow_name`) |
| `lh_vv_silver.dbo.slv_poi_amenity` (kept) | silver L2 | (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) (`01_DATA_MODEL.md` N7). Unchanged. | `NB_SLV_POI_AMENITY` (N7; INV-4 `flow_name`) |
| `lh_vv_gold.enr.gld_enr_poi_info` (kept; inputs reduced) | gold, schema `enr` | Not in the named files. Unchanged; not redesigned. | `NB_ENR_POI_INFO` (INV-2 `nb_name`) |
| `lh_vv_gold.enr.gld_enr_poi_review` (kept) | gold, schema `enr` | Not in the named files. Unchanged; not redesigned. | `NB_ENR_POI_REVIEW` (`request.md` Out of scope) |
| `lh_vv_silver.dbo.slv_3p_poi` (kept) | silver L1 | Unchanged; not restated here | Not in the named files |
| `lh_vv_silver.dbo.slv_3p_poi_address` (kept) | silver L1 | Unchanged; not restated here | Not in the named files |
| `lh_vv_silver.dbo.slv_3p_poi_contact` (kept) | silver L1 | Unchanged; not restated here | Not in the named files |

## Keys

- `slv_pn_poi` (removed):
  - Primary key: `poi_id`, from `NodeSpec.pk` in cell `379af200`.
  - `poi_id` formula: `uuid_md5(F.lit("partner_portal"), F.col("id"))` over `slv_pn_business_services.id` (cell `379af200`, `build` select list).
  - Business key: `business_service_id`, a copy of `slv_pn_business_services.id`. It is checked unique by `unique_checks` `business_service_id_unique` (cell `379af200`).
  - Foreign keys: none declared. `build` left-joins `slv_pn_business_service_i18ns` on `id = business_service_id`, filtered to `locale = 'vi'`.
- `gld_enr_poi_coordinate` (removed):
  - Primary key: not declared in cell `init_tables`. `poi_id` is `STRING NOT NULL`.
  - `poi_id` formula: the named files do not show where it comes from. See question 5.
  - Business and foreign keys: not shown.
- `slv_poi_entity_non_enrich` (kept, unchanged):
  - Primary key: `poi_id` (N6).
  - Partner-row `poi_id`: `md5(concat(id, 'partner'))` with 8-4-4-4-12 dashes. Source: `01_DATA_MODEL.md`, the `poi_id` sentence above section 6. That sentence also says not to use the `partner_portal` formula.
  - This formula is **not** the `slv_pn_poi` formula. Partner `poi_id` values in `slv_pn_poi` and in `slv_poi_entity_non_enrich` must not be treated as the same key.
- `slv_poi_amenity` (kept, unchanged):
  - Primary key: (`poi_id`, `business_sector`, `amenity_group`, `amenity_raw`) (N7).
  - `business_sector` comes from `slv_poi_entity_non_enrich` (N7). N7 does not state the join key, and this design does not add one.
- `gld_enr_poi_info`, `gld_enr_poi_review`, `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`: unchanged. Their keys are not in the named sections and are not redesigned.

## Columns

This section lists only the columns of the two removed tables. The kept tables have no column changes (D-04; author input), so no columns are listed for them.

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_enr_poi_coordinate` | `poi_id` | `STRING` | no (`NOT NULL`) | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `name` | `STRING` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `short_address` | `STRING` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `ward` | `STRING` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `district` | `STRING` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `province_name` | `STRING` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `destination_name` | `STRING` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `lat` | `DOUBLE` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `lng` | `DOUBLE` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `created_at` | `TIMESTAMP` | yes | Not in the named files | Removed with the table (D-04) |
| `gld_enr_poi_coordinate` | `updated_at` | `TIMESTAMP` | yes | Not in the named files | Removed with the table (D-04) |
| `slv_pn_poi` | `poi_id` | Not in the named cell (question 4) | PK; nullability not declared | `uuid_md5('partner_portal', slv_pn_business_services.id)` | Removed with the table (D-04) |
| `slv_pn_poi` | `business_service_id` | Not in the named cell (question 4) | Not declared | `slv_pn_business_services.id` | Removed with the table (D-04) |
| `slv_pn_poi` | `name` | Not in the named cell (question 4) | NULL when there is no `vi` row | `slv_pn_business_service_i18ns.name` where `locale = 'vi'`, left join | Removed with the table (D-04) |
| `slv_pn_poi` | `short_address` | Not in the named cell (question 4) | Not declared | `get_json_object(address, '$.full_address')` from `slv_pn_business_services` | Removed with the table (D-04) |
| `slv_pn_poi` | `ward` | Not in the named cell (question 4) | Not declared | `get_json_object(address, '$.ward')` from `slv_pn_business_services` | Removed with the table (D-04) |
| `slv_pn_poi` | `district` | Not in the named cell (question 4) | Not declared | `get_json_object(address, '$.district')` from `slv_pn_business_services` | Removed with the table (D-04) |
| `slv_pn_poi` | `province_name` | Not in the named cell (question 4) | Not declared | `get_json_object(address, '$.city')` from `slv_pn_business_services` | Removed with the table (D-04) |

The `slv_pn_poi` sources are the `build` select list in cell `379af200`. Technical columns written by the node framework do not appear in that select list and are not listed here (question 4).

## Lineage

Edge sources are INV-2 in `evidence/results/ctrl-inventory.txt`, plus N6 and N7. No gold table reads another gold table, either before or after the change.

- `slv_pn_poi` (removed):
  - Bronze: not in the named files.
  - Silver: `slv_pn_business_services` (input `bs`, required) and `slv_pn_business_service_i18ns` (input `i18n`) (cell `379af200`; INV-2, active).
  - Gold: none.
  - After removal: no table in INV-2 reads `slv_pn_poi` except `gld_enr_poi_coordinate`, which is also removed.
- `gld_enr_poi_coordinate` (removed):
  - Bronze: none.
  - Silver: `slv_3p_poi`, `slv_3p_poi_address`, `slv_pn_poi` (INV-2, `is_active = 0`).
  - Gold: none.
  - After removal: no table in INV-2 reads it.
- `slv_poi_entity_non_enrich` (kept):
  - Bronze: none.
  - Silver: `ref_dictionary_place_type`, `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`, `slv_pn_business_services`, `slv_pn_business_service_i18ns` (N6; INV-2, 6 active edges).
  - Gold: none.
  - It does not read `slv_pn_poi`, so the removal leaves its lineage unchanged.
- `slv_poi_amenity` (kept):
  - Bronze: none.
  - Silver: `ref_dictionary_amenities`, `slv_3p_poi_amenity`, `slv_poi_entity_non_enrich` (N7; INV-2, 3 active edges).
  - Gold: none.
  - Unchanged.
- `gld_enr_poi_info` (kept):
  - Bronze: none.
  - Silver after the change: `slv_3p_poi_opening_hours`, `slv_3p_poi_price`, `slv_3p_poi_rating`, `slv_3p_poi_review`, `slv_pn_business_service_i18ns`, `slv_poi_amenity`, `slv_poi_entity_non_enrich` (INV-2, active).
  - Silver inputs removed: `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact`. These edges were already inactive (INV-2; D-03).
  - Gold: none. It does not read `gld_enr_poi_coordinate`.
- `gld_enr_poi_review` (kept): not in INV-2. Unchanged.
- `slv_3p_poi`, `slv_3p_poi_address`, `slv_3p_poi_contact` (kept):
  - Bronze reads: not in the named files.
  - After the change, their only downstream reader in INV-2 is `slv_poi_entity_non_enrich`.
  - Their reads into `gld_enr_poi_info` and `gld_enr_poi_coordinate` are removed (D-03).

## Conflicts and questions

1. **No proposal.** `proposal.md` does not exist, so `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. This design is built from `request.md` and D-01 to D-04 only. Does `ctrl_cfg_schema_registry` have rows for `slv_pn_poi` or `gld_enr_poi_coordinate` that need removing? None of the named files show that table.
2. **N6 and N7 name the wrong pipeline.** Both rows in `01_DATA_MODEL.md` say `PL_VV_TRANS_SLV_TO_SLV_1H`. D-02 records that DEV already has all 9 edges on `PL_VV_TRANS_SLV_TO_ENR_15P`. The doc text conflicts with the ledger. The grain and columns are unaffected. The doc fix is in task scope (`request.md` In scope), but its wording is not a model decision.
3. **Two different partner `poi_id` formulas.**
   - `slv_pn_poi` uses `uuid_md5('partner_portal', id)`.
   - `slv_poi_entity_non_enrich` uses `md5(concat(id, 'partner'))` with dashes. The data-model sentence explicitly rejects the `partner_portal` formula.
   - The two formulas produce different keys for the same partner. Removing `slv_pn_poi` and `gld_enr_poi_coordinate` removes both affected tables that might hold `partner_portal`-formula keys.
   - Unknown: does any reader outside INV-2 (a report, export, or PG sync) store or join on `slv_pn_poi.poi_id`? The named files do not say.
4. **`slv_pn_poi` types, nullability, and technical columns are unknown.** Cell `379af200` shows no column types, no NOT NULL constraints, and no technical columns (for example a row hash or audit timestamps). The `slv_pn_poi` DDL is not in the named `init_tables` excerpt. Please provide the DDL source if the removed schema needs to be recorded, for example for rollback, which the Architect owns.
5. **`gld_enr_poi_coordinate` grain, PK, and column sources are unknown.** Cell `init_tables` shows the column list and that `poi_id` is NOT NULL, but no PK, no grain, and no column sources. `NB_ENR_POI_COORDINATE` is not in the named files. Was its `poi_id` copied from `slv_pn_poi`, from `slv_3p_poi`, or from both? This decides whether question 3 also applies to its 94 DEV rows (D-04).
6. **Kept gold tables are not described.** The grain and keys of `gld_enr_poi_info` and `gld_enr_poi_review` are not in the named files. They are left unchanged and not redesigned. `gld_enr_poi_review` does not appear in INV-2, so its inputs are not confirmed here.
7. **INV-2 shows `nb_name = null` for the two kept nodes.** All 9 `slv_poi_amenity` and `slv_poi_entity_non_enrich` edges have a null `nb_name`. N6, N7, and INV-4 `flow_name` name `NB_SLV_POI_ENTITY_NON_ENRICH` and `NB_SLV_POI_AMENITY`. This does not change the model, but the Architect should confirm how the orchestrator resolves these nodes.
8. **`architecture.md` already exists.** The task folder already has an `architecture.md`, but `request.md` says `model-design.md` must exist before the Architect step. That file was not read for this design. Please confirm it is a placeholder and not an Architect output that this design needs to match.
