# Author input

No `proposal.md` or `problem-analysis.md`. Write `Not applicable.` for `## Dòng thay đổi` and `## ctrl_cfg_schema_registry`.

## Scope

Task `20261116-enr-lang-destination-from-bronze`. `requirements-analysis.md` is `USER_DECISION` only because PC-01 remains on source rows. The user accepted that on 2026-11-16. Ledger rows D-1 through D-7 are the rules.

## Read

- `request.md` section `Verbatim request`
- `decision.md` section `Quyết định hiện hành`
- `requirements-analysis.md` sections 3 and 5
- `docs/requirements/20261116-enr-lang-destination-from-bronze/MAPPING.md` sections 3–5, version 5
- `docs/requirements/20261116-enr-lang-destination-from-bronze/BRD.md` sections 5–6, version 4
- `docs/context/mapping_gld_srv_poi_multi_lang.md` §2
- `docs/context/mapping_gld_srv_poi_info.md` §1.6
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` `TABLE_SPECS` for both `slv_enr_*` tables, `gld_srv_poi_multi_lang`, and `gld_srv_poi_info`
- `sql/postgres/gld_srv_serve.pg.sql` table `apps.srv_poi_multi_lang`
- `evidence/results/probe_brz_enrichment_result.txt` sections SCHEMA and UNIQUENESS
- `evidence/results/probe_json_shape.txt` and `probe_json_shape_rest.txt`

## Decided rules

- LANG rows only into `slv_enr_poi_info_multi_lang`. Grain (`poi_id`, `lang`). DESTINATION rows only into `slv_enr_poi_destination`. Grain `poi_id`.
- Same key: keep the higher `version`, then the higher `EventProcessedUtcTime`.
- Extract `load_mode` DOC, `src_object` `$`, watermark `EventProcessedUtcTime`.
- `cost_vnd` becomes `cost` on silver multi_lang, gold multi_lang, and `apps.srv_poi_multi_lang` (`text`). The API reads `cost`. No new API column. No Mapping row `TRG-005`.
- `data.experiences` writes the existing `experience` STRING column. `destination` is the whole JSON array as STRING. `destination_id` and `destination_name` keep element order, including the one DEV element whose id and name are null.
- `translated_at` is TIMESTAMP with `ISO_UTC_TS`. New text columns are STRING. `country_code` and `postal_code` are NULL, not read from JSON.
- Drop `street` on `slv_enr_poi_destination`. Gold `street` comes from `slv_poi_entity_non_enrich.street`.
- Gold `full_address` joins with `, `. If any field in a group is null, skip the whole group. Group 1: `house_number` + `street` + `formatted_address`. Group 2: `house_number` + `street` + `ward_with_type` + `city_with_type`. Group 3: `slv_enr_poi_destination.full_address`. Do not use `concat_ws` for this rule.
- Keep both `slv_enr_` names. PC-01 on `SRC-003` and `SRC-004` is accepted.
- Out of scope: `gld_enr_poi_info`, historical `NB_CREATE_DDL` cells, dropping `slv_poi_entity_non_enrich.street`, and `(ood).general-information.md`.
- `docs/context/api-mapping/practical_info.md` is in scope for the rename only. Do not design the API.

## Constraints

Do not invent a json path, type, key, or separator. Column paths are Mapping section 5. Keep the null destination element in order.
