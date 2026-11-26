# Model design — 20261126-gld-srv-old-address-price-story

## Scope

- Base task: `20261126-gld-srv-old-address-price-story` (`request.md` `## User outcome`, `## Scope`, `## Verbatim request` and its `Diễn giải đã chốt` bullets).
- Proposal sections: `proposal.md` is not in the task folder, so this design cannot cite `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. `problem-analysis.md` and `requirements-analysis.md` are not there either. See Conflicts item 1. Until a proposal exists, the design rests on `request.md` and the decision ledger.
- Ledger row implemented: `decision.md` `## Quyết định hiện hành` row `D-OLD-ADDR`. The applied formula comes from `decision.md` `## Quyết định của người dùng`, second paragraph.
- Columns added: `gld_srv_poi_info`.`old_address`, `price_level`, `price_min`, `price_max`; `gld_srv_poi_multi_lang`.`story`, `local_tips`. All six are gold-only. They do not go into `sql/postgres/gld_srv_serve.pg.sql`, Java entities, DTOs, or `docs/context/api-mapping/` (`request.md` `### Out of scope`).
- Grain and MERGE keys do not change (`request.md` `Diễn giải đã chốt`, bullet 1).

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `gld_srv_poi_info` (target, 4 columns added) | gold `lh_vv_gold.dbo` | one row per `poi_id` (`mapping_gld_srv_poi_info.md` §1.1; NodeSpec `pk=("poi_id",)`) | `NB_GLD_SRV_POI_INFO` |
| `gld_srv_poi_multi_lang` (target, 2 columns added) | gold `lh_vv_gold.dbo` | one row per (`poi_id`, `lang`) (`mapping_gld_srv_poi_multi_lang.md` §1.1; NodeSpec `pk=("poi_id", "lang")`) | `NB_GLD_SRV_POI_MULTI_LANG` |
| `slv_3p_poi_price` (new input, schema unchanged) | silver `lh_vv_silver.dbo` | one row per `poi_id` (registry `key: "poi_id"`, `load_mode = DOC`; `01_DATA_MODEL.md` §5.2) | written by `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` |
| `slv_pn_business_service_i18ns` (existing input, schema unchanged) | silver `lh_vv_silver.dbo` | one row per (`business_service_id`, `locale`) (registry `key: ["business_service_id", "locale"]`) | written by `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV` |
| `slv_enr_poi_destination` (existing input, schema unchanged, three more columns read) | silver `lh_vv_silver.dbo` | one row per `poi_id` (`mapping_gld_srv_poi_info.md` §1.6) | written by `NB_EXTRACT_ENRICHMENT_CDC_BRZ_TO_SLV` (`mapping_gld_srv_poi_info.md` §1.1) |
| `slv_poi_entity_non_enrich` (existing input, no change) | silver `lh_vv_silver.dbo` | one row per `poi_id` | `NB_SLV_POI_ENTITY_NON_ENRICH` |

## Keys

`gld_srv_poi_info`
- Primary key: `poi_id` `STRING NOT NULL` (`NB_SETUP_INITIAL_DDL` `TABLE_SPECS`; NodeSpec `pk`). MERGE on `poi_id`, unchanged.
- Business key: `poi_id`. It never includes language (`AGENTS.md` §7).
- Join key to `slv_3p_poi_price`: `gld_srv_poi_info.poi_id = slv_3p_poi_price.poi_id`. The third-party `poi_id` formula is `uuid_format(md5(concat(source_name, source_id)))`, rule `HASH_MD5_UUID` (`AGENTS.md` §7). In the registry it is the `POI_ID` constant `{"path": "_doc.source_name,_doc.source_id", "type": "string", "rule": "HASH_MD5_UUID"}` that the `slv_3p_poi_price` entry uses (`NB_SETUP_INITIAL_DDL`). Partner `poi_id` comes from `uuid_md5(id, 'partner')`, so partner rows have no price match and get null.
- Join key to `slv_enr_poi_destination`: `poi_id`, the existing LEFT JOIN after `_destination` dedup (`mapping_gld_srv_poi_info.md` §1.1). Unchanged.
- No declared foreign keys. Delta has no FK constraints, so all joins are logical LEFT JOINs.

`gld_srv_poi_multi_lang`
- Primary key: (`poi_id`, `lang`), both `STRING NOT NULL` (`TABLE_SPECS`; NodeSpec `pk`). MERGE on these, unchanged.
- Join key to `slv_pn_business_service_i18ns`: `poi_id = uuid_md5(business_service_id, lit('partner'))` and `lang = locale`. The partner formula `uuid_format(md5(concat(id, 'partner')))` is from `AGENTS.md` §7 and `01_DATA_MODEL.md` (paragraph before §5.2). This is the same join that `bio` and `usps` use (`mapping_gld_srv_poi_multi_lang.md` §1.1, P1 bullets 3–4 and P2 bullet 1). On P1 the join only applies when `lower(trim(source_name)) = 'partner'`.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_srv_poi_info` | `old_address` | `STRING` | yes | `slv_poi_entity_non_enrich.house_number`, `slv_poi_entity_non_enrich.street`, `slv_enr_poi_destination.old_formatted_address`, `slv_enr_poi_destination.old_ward_with_type`, `slv_enr_poi_destination.old_city_with_type`, `slv_enr_poi_destination.full_address` (all `STRING` in `TABLE_SPECS`) | `D-OLD-ADDR` and `decision.md` `## Quyết định của người dùng`. With a destination row (`_has_dest` true), coalesce three groups joined by `, `. Group 1: `house_number` + `street` + `old_formatted_address`. Group 2: `house_number` + `street` + `old_ward_with_type` + `old_city_with_type`. Group 3: `slv_enr_poi_destination.full_address`. Groups are dropped by the same rule as `full_address` (`mapping_gld_srv_poi_info.md` §1.6): if any field is null, or `house_number` or `street` is blank after trim, the whole group is dropped. With no destination row, the value is null on every source, including partner. Entity `full_address` is never used (`request.md` `### Out of scope`). No `old_house_number`, `old_street`, or `old_full_address` column is created. |
| `gld_srv_poi_info` | `price_level` | `INT` (source registry `"type": "int"`) | yes | `slv_3p_poi_price.price_level` | `request.md` `Diễn giải đã chốt` bullet 3. 1-1 LEFT JOIN on `poi_id`. No price row gives null. No `source_name` filter. If `slv_3p_poi_price` has more than one row for a `poi_id`, stop and pick no row. Keep the source type. |
| `gld_srv_poi_info` | `price_min` | `DECIMAL(18,2)` (source registry `"type": "decimal(18,2)"`; `CTRL_TABLES_CONTEXT.md` row `slv_3p_poi_price`) | yes | `slv_3p_poi_price.price_min` | Same as `price_level`. |
| `gld_srv_poi_info` | `price_max` | `DECIMAL(18,2)` (same evidence as `price_min`) | yes | `slv_3p_poi_price.price_max` | Same as `price_level`. `currency` is not added (`request.md` `### Out of scope`). |
| `gld_srv_poi_multi_lang` | `story` | `STRING` (source registry `"type": "string"`) | yes | `slv_pn_business_service_i18ns.story` | `request.md` `Diễn giải đã chốt` bullet 4. P1 partner takes `story` from the joined i18n row, with no fallback to `slv_enr_poi_info_multi_lang`. P1 non-partner gets null. P2 takes `story` directly with no fallback, cast to the P1 type like the other P2 columns (`mapping_gld_srv_poi_multi_lang.md` §1.1, P2 bullet 3). |
| `gld_srv_poi_multi_lang` | `local_tips` | `STRING` (source registry `"type": "string"`) | yes | `slv_pn_business_service_i18ns.local_tips` | Same as `story`. |

All six columns allow NULL, because a column added to an existing table must allow NULL (`02_NAMING_CONVENTION.md` §2.1 rule 5). Column order in `TABLE_SPECS`, `OUT_COLS`, and the `NB_CREATE_DDL` `AFTER` anchor is open; see Conflicts item 4.

## Lineage

`gld_srv_poi_info`
- Bronze: none read by the gold node. `slv_3p_poi_price` comes from bronze `brz_3rd_crawler_poi_stream`, block `poi_price`, via `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` (`03_OPERATOR_GUIDE.md` §2.12.2).
- Silver reads:
  - `slv_poi_entity_non_enrich`: unchanged. `house_number` and `street` are already in `ENT_COLS`.
  - `slv_enr_poi_destination`: also reads `old_formatted_address`, `old_ward_with_type`, `old_city_with_type`. `full_address` is already in `DEST_COLS`.
  - `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review`, `slv_poi_media_info`: unchanged.
  - `slv_3p_poi_price` (new): columns `poi_id`, `price_level`, `price_min`, `price_max`.
- Gold reads: none.
- Pipeline edge (new): `slv_3p_poi_price` → `gld_srv_poi_info`, `pl_name = PL_VV_TRANS_SLV_TO_GLD_30M`, `load_mode = RECOMPUTE`, `priority = 1`, `nb_name = NB_GLD_SRV_POI_INFO`. This matches the existing edge rows in the `NB_SETUP_INITIAL_DDL` seed and `mapping_gld_srv_poi_info.md` §1.1 bullet `pl_name`. `ctrl_cfg_schema_registry` does not change, because the three price columns are already registered.

`gld_srv_poi_multi_lang`
- Bronze: none read by the gold node.
- Silver reads:
  - `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich`: unchanged.
  - `slv_pn_business_service_i18ns`: also reads `story`, `local_tips` (already registered as `string`).
- Gold reads: none.
- Pipeline edge: no new edge. The existing edge `slv_pn_business_service_i18ns` → `gld_srv_poi_multi_lang` is reused (`request.md` acceptance criterion 2).

## Conflicts and questions

1. **No proposal.** `proposal.md` is missing from `.ai/tasks/20261126-gld-srv-old-address-price-story/`, so this design cannot cite its `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. `problem-analysis.md` and `requirements-analysis.md` are missing too. The design uses `request.md` and ledger row `D-OLD-ADDR` instead. Main confirms that is the accepted basis, or supplies the proposal.
2. **Request wording vs. `D-OLD-ADDR`.** The request says "lấy các field có tiền tố old_". `D-OLD-ADDR` keeps entity `house_number` and `street`, and keeps group 3 as the current `slv_enr_poi_destination.full_address`, not an `old_` column. This design follows the ledger, which is the user's later decision. No open question unless Main records otherwise.
3. **Read mode for the price input.** For `ctx.input("price")`, the files do not say whether to pass `live_only=False` (as for `entity`, `destination`, `multi_lang`) or the default `deleted_at IS NULL` (as for `rating`, `review`, `media`). Main or the Architect decides.
4. **Column positions.** The files do not say where the six columns go in `TABLE_SPECS` and `OUT_COLS`, or which `AFTER` anchor the new `NB_CREATE_DDL` patch cell uses. Main decides, for example after `full_address` for `old_address`, after `review_count` for the price columns, and after `experience` for `story` and `local_tips`. None of these is decided.
5. **`required_inputs`.** The request does not say whether `slv_3p_poi_price` is added to `required_inputs`. The current value is (`entity`,), and `rating`, `review`, and `media` are not required. Main confirms that price stays optional.
