# Request

## User outcome

`slv_poi_entity_non_enrich` stores `phone`, `email`, and `holiday_exceptions` for each POI. Google and partner each have one rule. Gold does not recompute these attributes.

## Scope

### In scope

- Add `phone`, `email`, and `holiday_exceptions` to `slv_poi_entity_non_enrich` in `NB_SLV_POI_ENTITY_NON_ENRICH`, `NB_SETUP_INITIAL_DDL`, and `NB_CREATE_DDL`.
- Keep the uncommitted `20261023-entity-opening-hours-passthrough` diff. This task edits that working tree and does not revert the hours change.
- When runtime is reached, one new runbook covers both the not-yet-applied `ohpasspy` cell and the three-column patch.

### Out of scope

- Gold columns, gold formulas, and `NB_ENR_POI_INFO`.
- The `opening_hours_text` formula, the hours ctrl edges, and cell `ohpasspy`.
- Extract-column additions, a new orchestration tier, and `DROP` of an existing table.
- Running the hours-task runbook or `run-gate` on `20261023-entity-opening-hours-passthrough`.
- A new ctrl edge unless architecture names a source that is not already an entity input.

## Acceptance criteria

- `phone`, `email`, and `holiday_exceptions` are `STRING`, nullable, in that order, after `opening_hours_text` and before `row_hash`.
- Google: `phone` is `slv_3p_poi_contact.phone` for the same `poi_id`, on the join frame that already supplies `website_url`. `email` is null. `holiday_exceptions` is null.
- Partner: `phone` is `slv_pn_business_services.phone`. `email` is `slv_pn_business_services.email`. `holiday_exceptions` is `get_json_object(amentities, '$.policies.holiday_exceptions')` on the i18n `vi` row, the same row and the same access as `operating_hours` at `$.policies.operating_hours`. Keep the JSON string. Do not parse it further.
- Any other source leaves all three columns null, using the same branch style as hours.
- The contact duplicate-`poi_id` quality gate stays as it is.
- `NB_SETUP_INITIAL_DDL` updates the `slv_poi_entity_non_enrich` spec in place. `NB_CREATE_DDL` appends one markdown cell `[THÊM 23/10] 20261023-entity-phone-email-holiday` and one self-contained patch cell after `ohpasspy`. The patch only `ALTER`s in missing nullable columns. It does not edit `ohpasspy` and does not `DROP` the table.
- `slv_3p_poi_contact`, `slv_pn_business_services`, and `slv_pn_business_service_i18ns` stay the inputs they already are.

## Constraints

- Domain: lib transform/gold and DDL/registry. Signal: `data_model_change`.
- Registry already declares the source columns as string. `NB_SETUP_INITIAL_DDL` cell 4 `slv_pn_business_services` has `phone` (`path` `phone`) and `email` (`path` `email`). Cell 5 `slv_3p_poi_contact` has `phone` = `_str("nationalPhoneNumber")` and no `email`. `NB_CREATE_DDL` cells 11 and 14 carry the same mappings. Extract notebooks project `spec.columns` from `ctrl_cfg_schema_registry` through `load_table_specs`. Do not add extract columns and do not invent a type.
- `holiday_exceptions` is not its own registry column. It is a JSON path on `amentities`, which the entity notebook already reads for hours.
- Setup and create DDL follow `docs/context/02_NAMING_CONVENTION.md` §2.1.
- The hours task records the runtime pause in its own `decision.md` and stays `waiting_runtime`.

## Classification rationale

- Complexity: medium. The change adds three columns to a silver node and both DDL notebooks. It does not add a new orchestration tier.
- Risk: medium. The entity output gains values, rollback is a nullable add, and the hours patch is still unapplied on DEV.
- Architecture: required. The silver table's committed column set changes, and those attributes are owned by `slv_poi_entity_non_enrich`, not by gold.
- Evidence: not required. The source `phone` and `email` columns and their string types are in both registry seeds. Extract follows that registry. `holiday_exceptions` reuses `amentities`.
- Runtime proof: required. DEV must apply `ohpasspy` and the new nullable `ALTER`, then the entity recompute.
- Reviewer routing: `spark-runtime-reviewer` for the entity notebook; `sql-data-reviewer` for the DDL patch and the column expressions. No pipeline reviewer. No state-correctness reviewer unless architecture adds a ctrl or lock change.
