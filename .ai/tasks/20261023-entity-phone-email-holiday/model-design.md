# Model design: 20261023-entity-phone-email-holiday

## Scope

- Base task: `20261023-entity-phone-email-holiday`. The task is `triage`, `architecture_required: true`, signal `data_model_change` (`task-state.yaml`). It edits the uncommitted working tree of `20261023-entity-opening-hours-passthrough` and keeps it (D-PEH-04 history).
- `proposal.md`, `problem-analysis.md` and `requirements-analysis.md` do not exist for this task, so this design cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. The design uses `request.md` (`## Acceptance criteria`, `## Constraints`) and the `Quyết định hiện hành` ledger instead.
- Ledger rows implemented: D-PEH-01 (columns, type, order, no gold column), D-PEH-02 (Google rule), D-PEH-03 (partner rule), D-PEH-04 (hours unchanged), D-PEH-05 (other sources null, contact QG kept), D-PEH-06 (registry already has the source columns, no extract change, no new input).
- Out of scope, per `request.md` `### Out of scope`: gold columns and `NB_ENR_POI_INFO`, the `opening_hours_text` formula, hours ctrl edges, cell `ohpasspy`, extract-column additions, new ctrl edges, `DROP`.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_poi_entity_non_enrich` | silver (L2 node, `write_mode="MERGE"`) | One row per `poi_id`. Unchanged (`SPEC.pk=("poi_id",)` in `NB_SLV_POI_ENTITY_NON_ENRICH` cell `b1entitybuild`) | `NB_SLV_POI_ENTITY_NON_ENRICH` |

These source tables are read but their schema and registry rows do not change (D-PEH-06):

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_3p_poi_contact` | silver L1 | registry `key` `poi_id` (`NB_SETUP_INITIAL_DDL` cell `init_cfg_3p`; `NB_CREATE_DDL` cell 14) | `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` (unchanged) |
| `lh_vv_silver.dbo.slv_pn_business_services` | silver L1 | registry `key` `id` (setup cell `init_cfg_partner`; create cell 11) | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` (unchanged) |
| `lh_vv_silver.dbo.slv_pn_business_service_i18ns` | silver L1 | the entity reads only the `locale = 'vi'` rows, joined on `business_service_id = id` | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` (unchanged) |

## Keys

`slv_poi_entity_non_enrich`:
- Primary key: `poi_id` (`SPEC.pk`). The DDL declares `poi_id` as `STRING` with no `NOT NULL` (setup cell `init_tables`, entity spec). This task does not change it.
- Business key: (`source_name`, `source_id`). The existing unique check `partner_source_id_unique` covers `source_id` where `source_name = 'partner'`. This task does not change it.
- `poi_id` formula source:
  - Google rows pass through `slv_3p_poi.poi_id`. That column comes from the registry `"poi_id": POI_ID` of the 3P configs, and AGENTS.md §7 gives the third-party formula as `HASH_MD5_UUID`. No new formula is applied.
  - Partner rows use the formula already in the notebook: `uuid_md5(F.col("id"), F.lit(PARTNER))` (comment `D2`, cell `b1entitybuild`; asserted by `tests/test_poi_entity_contract.py:174`). No second formula is applied. See Conflicts item 1.
- Join keys used by the three new columns (none are new):
  - Google `phone`: `slv_3p_poi_contact.poi_id` = entity `poi_id`. This is a left join on the existing `contact` frame that already supplies `website_url`, after `poi_id IS NOT NULL` and the unchanged duplicate-`poi_id` `QualityGateError` (D-PEH-02, D-PEH-05).
  - Partner `phone`, `email`: `slv_pn_business_services.id` = entity `source_id`. These come from the existing live `svc` rows in `base` (D-PEH-03).
  - Partner `holiday_exceptions`: `slv_pn_business_service_i18ns.business_service_id` = `svc.id`, filtered on `locale == "vi"` and live rows. This is the same `vi` frame that projects `$.policies.operating_hours` (D-PEH-03).

## Columns

All three columns go after `opening_hours_text` and before `row_hash`, in this order (D-PEH-01; `request.md` acceptance criterion 1). The same order applies to the `b1entitybuild` output, the `NB_SETUP_INITIAL_DDL` entity spec (in place, §2.1 rule 2, rule 7), and the `NB_CREATE_DDL` patch cell after `ohpasspy`, which adds a column only when it is missing and nullable (§2.1 rule 3, rule 5).

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_poi_entity_non_enrich` | `phone` | `STRING` | yes | Google: `slv_3p_poi_contact.phone`. The registry maps it to `_str("nationalPhoneNumber")` (setup `init_cfg_3p`; create cell 14). Partner: `slv_pn_business_services.phone`, registry `path` `phone`, `type` `string` (setup `init_cfg_partner`; create cell 11). | Google: the value from the left join on `poi_id` in the `contact` frame (D-PEH-02). Partner: `svc.phone` (D-PEH-03). Any other `source_name`: null (D-PEH-05). Type `STRING` (D-PEH-01, D-PEH-06). |
| `slv_poi_entity_non_enrich` | `email` | `STRING` | yes | Partner: `slv_pn_business_services.email`, registry `path` `email`, `type` `string` (setup `init_cfg_partner`; create cell 11). Google: none. The contact registry has no `email`. | Google: null typed as string, the same form as the existing `F.lit(None).cast("string")` (D-PEH-02). Partner: `svc.email` (D-PEH-03). Other source: null (D-PEH-05). |
| `slv_poi_entity_non_enrich` | `holiday_exceptions` | `STRING` | yes | Partner: `slv_pn_business_service_i18ns.amentities`, an existing entity input column (checked by the `ConfigError` in `build`). It is not a registry column (D-PEH-06). | Partner: `get_json_object(amentities, '$.policies.holiday_exceptions')` on the `locale = 'vi'` live row, projected in the same `vi` select as `$.policies.operating_hours`. The JSON string is kept and not parsed further (D-PEH-03). Google: null typed as string (D-PEH-02). Other source: null (D-PEH-05). |

Type note: `_partner` casts every output column to `google.schema[c].dataType`. The Google branch must therefore emit all three columns as `string`, with `email` and `holiday_exceptions` as string-cast nulls. A bare untyped null would not match the `STRING` DDL (D-PEH-01).

No other column changes. `opening_hours_text`, `website_url`, and `TECH_COLUMNS` (`row_hash`, `created_at`, `updated_at`, …) stay as they are (D-PEH-04).

## Lineage

`slv_poi_entity_non_enrich`:
- Bronze: none read directly. `slv_3p_poi_contact` is extracted from `lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream` (setup `init_seed_ctrl` edge, `DOC`). `slv_pn_business_services` and `slv_pn_business_service_i18ns` come from the partner extract `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`. The files read for this design do not name their bronze table. Neither extract changes (D-PEH-06).
- Silver reads, all already in `SPEC.inputs` and already `RECOMPUTE` edges into the entity (setup `init_seed_ctrl`):
  - `phone` (Google): input role `contact` → `slv_3p_poi_contact`.
  - `phone`, `email` (partner): input role `svc` → `slv_pn_business_services`.
  - `holiday_exceptions` (partner): input role `i18n` → `slv_pn_business_service_i18ns`.
  - No new input role, required input, or ctrl edge.
- Gold reads: none. No gold column is added (D-PEH-01). The existing edge `slv_poi_entity_non_enrich` → `gld_enr_poi_info` does not change, and gold does not recompute these attributes (`request.md` `## User outcome`). Gold never reads gold.

## Conflicts and questions

1. Partner `poi_id` formula conflict (existing, not introduced here). AGENTS.md §7 says partner `poi_id = uuid_format(md5('partner_portal' || business_service_id))` and that no current notebook applies it. `b1entitybuild` already applies `uuid_md5(F.col("id"), F.lit(PARTNER))` with `PARTNER = "partner"` (D2). This design keeps the notebook formula, as the author input instructs. The two need reconciling in AGENTS.md or a separate task. I did not read the `uuid_md5` definition in `NB_LIB_TRANSFORM_SLV_GLD`, so I do not claim that its argument order or prefix matches §7.
2. Column grouping versus order. `tests/test_initial_ddl_contract.py:358` puts every `CONTACT_COLS` name right after the POI columns and before the address columns. If `phone` were added to `CONTACT_COLS`, it would land before `house_number`, which breaks the D-PEH-01 order. The three columns therefore need their own build group after `HOURS_COLS`, and the contract test's expected list (lines 367–370) needs them after `opening_hours_text`. The ledger does not name this group. Question: what should the tuple be called?
3. The other-source block check shape is not fixed. D-PEH-05 says "same branch style as hours" (`opening_hours_other_source`). It does not say whether to add one block check per column or one combined predicate, and it gives no check names. Question: which shape and which names?
4. Missing-column guards are not decided. `build` raises `ConfigError` when `website_url`, `website_urls`, `periods_json` or `amentities` is missing. No ledger row says whether `contact.phone`, `svc.phone` and `svc.email` get the same guard. Question: add them or not?
5. The warn check is not decided. Hours has `partner_opening_hours_null`. No ledger row asks for a null-rate warn check or a metric (such as `google_with_phone`) for the new columns. Question: should any be added, and with which names?
6. Unread scope file. `docs/context/01_DATA_MODEL.md` is listed in `task-state.yaml` `scope.files` but was not in this author's read list, so this design does not specify its update.
