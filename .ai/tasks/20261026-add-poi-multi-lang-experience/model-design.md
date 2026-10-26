# Model design — 20261026-add-poi-multi-lang-experience

## Scope

- Base task: `20261026-add-poi-multi-lang-experience` ("Add experience string to POI multi-lang landing and gold"). In `task-state.yaml` its status is `triage` and it has the signal `data_model_change`.
- There is no `proposal.md`, `problem-analysis.md` or `requirements-analysis.md` in the task folder. So this design cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. The source is the verbatim request in the author input:
  - R1: "Thêm cột experience type string cho slv_enr_poi_info_multi_lang."
  - R2: "Bảng gld_srv_poi_multi_lang thêm cột experience: lấy 1-1 slv_enr_poi_info_multi_lang.experience".
  - R3: "lấy 1-1 slv_pn_business_service_i18ns.usps".
- The `Quyết định hiện hành` ledger in `decision.md` has no rows, so no ledger row is implemented.
- In scope:
  - Schema-only landing change on `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang`.
  - Column add on `lh_vv_gold.dbo.gld_srv_poi_multi_lang`.
  - The mapping of the gold column from its two named sources.
  - Grain and keys stay unchanged.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_enr_poi_info_multi_lang` | silver (enrich landing) | Unchanged. The DDL declares only `poi_id` NOT NULL. The files read show no landing key. | None. No writer notebook is in scope (author input, Facts). The DDL is in `NB_CREATE_DDL` (`LANDING_COLS`) and `NB_SETUP_INITIAL_DDL`. |
| `lh_vv_gold.dbo.gld_srv_poi_multi_lang` | gold (serving) | `(poi_id, lang)`, unchanged (`SPEC.pk` in cell `srvmlbuild`; mapping §1.1 "MERGE theo grain `(poi_id, lang)`") | `NB_GLD_SRV_POI_MULTI_LANG` |
| `lh_vv_silver.dbo.slv_pn_business_service_i18ns` | silver (partner) | `(business_service_id, locale)` (registry `key` in `NB_CREATE_DDL`) | Read only, no change. `usps` is already a registry column. |

## Keys

- `slv_enr_poi_info_multi_lang`:
  - No change.
  - `poi_id` is STRING NOT NULL.
  - The DDL and the files read declare no primary or business key.
- `gld_srv_poi_multi_lang`:
  - Primary key `(poi_id, lang)`, unchanged. Both are NOT NULL in the DDL of both notebooks.
  - Foreign keys used by the build:
    - `poi_id` joins `slv_poi_entity_non_enrich.poi_id` (left join) to get `source_name`.
    - On partner rows, `(poi_id, lang)` joins i18n `(_pid, _loc)`.
  - The new column `experience` is not a key column.
- `slv_pn_business_service_i18ns`:
  - Business key `(business_service_id, locale)` (registry `key`).
  - Its `poi_id` is derived as `uuid_md5(business_service_id, 'partner')`.
  - Formula source: cell `srvmlbuild` (`uuid_md5(F.col("business_service_id"), F.lit(PARTNER))`) and `docs/context/mapping_gld_srv_poi_multi_lang.md` §1.1, which says this matches how `NB_SLV_POI_ENTITY_NON_ENRICH` computes partner `poi_id`.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_enr_poi_info_multi_lang` | `experience` | STRING | yes | Landing schema only. No writer is in scope, and the files do not show who writes the value. | R1. Constraint "Both new columns are STRING and nullable". Add to `NB_CREATE_DDL` `LANDING_COLS` and to the `NB_SETUP_INITIAL_DDL` cols list. Position in the column list is not specified (Q4). |
| `gld_srv_poi_multi_lang` | `experience` | STRING | yes | `slv_enr_poi_info_multi_lang.experience` (R2) and `slv_pn_business_service_i18ns.usps` (R3) | Each source maps 1-1 with no transform. Which source wins when both are non-null for one row is open (Q1). No coalesce, fallback, truncation or partner branch is defined, and this design does not reuse the `description` pattern from mapping §1.1. Add to the DDL in both notebooks and to `ML_COLS` / `OUT_COLS`. |
| `slv_pn_business_service_i18ns` | `usps` | string (registry) | yes (registry column, not `CREATE TABLE`, per naming convention §2.1.7) | Registry `{"path": "usps", "type": "string"}`, `target_table` `slv_pn_business_service_i18ns`, present in both DDL notebooks | No change. The gold build must now read it. Today `_require(i18n, ...)` checks only `business_service_id`, `locale` and `bio`. |

## Lineage

- `slv_enr_poi_info_multi_lang.experience`:
  - Bronze: none shown.
  - Silver: landing column with no writer notebook in scope (Q2).
- `gld_srv_poi_multi_lang.experience`:
  - Bronze: none read directly.
  - Silver reads, which are all inputs already on the node (`SPEC.inputs`; ctrl edges `NB_CREATE_DDL` ~3254–3256 and `NB_SETUP_INITIAL_DDL` ~840–842):
    - `slv_enr_poi_info_multi_lang` (`multi_lang`) → `experience`.
    - `slv_pn_business_service_i18ns` (`i18n`) → `usps`, joined on `uuid_md5(business_service_id, 'partner') = poi_id` and `locale = lang`. The build applies this join only when `source_name` is partner.
    - `slv_poi_entity_non_enrich` (`entity`) → `source_name`. This is not a source of `experience`, but it decides whether the i18n join matches.
  - Gold reads: none. No new input and no new ctrl edge. Gold does not read gold.

## Conflicts and questions

1. Source precedence (open). Two sources can both be non-null on one row:
   - A gold row with `source_name = partner` and a matching i18n row (`poi_id = uuid_md5(business_service_id, 'partner')`, `lang = locale`) can have both `slv_enr_poi_info_multi_lang.experience` and `slv_pn_business_service_i18ns.usps` non-null.
   - R2 and R3 both say "lấy 1-1" into the single column `gld_srv_poi_multi_lang.experience`, and neither says which value to keep.
   - The design does not choose. The user must decide which source wins, or whether something else applies (e.g. a per-`source_name` rule).
2. No writer for the landing column (unknown). `slv_enr_poi_info_multi_lang.experience` is schema only, and no writer notebook is in scope. The files read do not show which process fills the column or from which upstream field. Until that is known, the enr-sourced side of the gold column has no stated producer.
3. `row_hash` participation (unknown). `gld_srv_poi_multi_lang` has a `row_hash` column. The files read do not show whether a new output column joins the hash automatically through `NB_LIB_TRANSFORM_SLV_GLD`. That library was not in the read list.
4. Column position (unknown). The request does not give an ordinal position for `experience` in the landing DDL, the gold DDL or `OUT_COLS`. The existing tests compare `LANDING` and `OUT_COLS` as exact ordered lists.
5. Missing proposal and mapping doc (process). There is no `proposal.md`, so the sections the handoff names (`## Dòng thay đổi`, `## ctrl_cfg_schema_registry`) cannot be cited, and no registry change is needed (`usps` already exists). `docs/context/mapping_gld_srv_poi_multi_lang.md` §1.2 has no `experience` row. Whether to update it is outside this read-only design.
