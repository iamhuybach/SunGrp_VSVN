# Model design: 20261112-poi-destination-name-api

## Scope

- Base task: `20261112-poi-destination-name-api`.
  - `task-state.yaml`: `status: user_decision`, `evidence_required: false`.
  - Signals: `data_model_change`, `cross_system`, `runtime_proof_required`.
- This second pass replaces the first pass. Ledger rows D-1, D-2 and D-3 in `decision.md` `## Quyết định hiện hành`, with details under `## Lịch sử quyết định`, settle first-pass Conflicts 1–3. `request.md` `## Constraints` says these decisions supersede the earlier stop rules for a missing source.
- `proposal.md`, `problem-analysis.md` and `requirements-analysis.md` do not exist in the task folder. This design therefore cannot cite `proposal.md` `## Dòng thay đổi` or `## ctrl_cfg_schema_registry`. Its scope sources are `request.md` `### In scope`, `request.md` `## Constraints`, and ledger rows D-1 to D-4.
- Ledger rows implemented:
  - **D-1**: add `slv_enr_poi_destination.destination_name` as DDL only, with no writer. Then `gld_srv_poi_info.destination_name` and `apps.srv_poi_info.destination_name` copy it 1-1 (request.md In scope bullets 1–3).
  - **D-2**: `GET /experiences` `data.items[].icon_key` is the `keyword` key inside the `experience` JSON of the selected `apps.srv_poi_multi_lang` row. No new column (request.md In scope bullet 7).
  - **D-3**: `gld_srv_poi_review.source_name` is the literal `google`, set in `NB_GLD_SRV_POI_REVIEW`. `apps.srv_poi_review.source_name` copies it (request.md In scope bullet 8).
  - **D-4**: API only, with no data-model change.
    - Remove `data[].items[].amenity_label_en` and `amenity_label_vi` from the amenities response.
    - Remove `data.business_sector` from the practical_info response.
    - `apps.srv_poi_amenity.amenity_en` and `amenity_vi` stay. `data.business_tags.business_sector` stays.
    - No column is added or dropped.
- The compact and practical_info `destinations.name` fields (request.md In scope bullets 5–6) need only `apps.srv_poi_info.destination_name` from D-1. Until a later load fills the silver column, they read null.
- This design does not cover rollout, ordering, transaction boundaries or idempotency. They belong to the Architect.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_silver.dbo.slv_enr_poi_destination` | silver (enrich landing) | One row per `poi_id` is the intent. `NB_GLD_SRV_POI_INFO` `_destination` keeps the row with the latest `updated_at` | None. DDL-only landing table, and D-1 adds no writer |
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold | `poi_id` | `NB_GLD_SRV_POI_INFO` |
| `apps.srv_poi_info` | PostgreSQL serving | `poi_id` (`sql/postgres/gld_srv_serve.pg.sql:56`) | Copy of `gld_srv_poi_info` |
| `apps.srv_poi_multi_lang` | PostgreSQL serving | `(poi_id, lang)` (`sql/postgres/gld_srv_serve.pg.sql:72`) | Copy of `gld_srv_poi_multi_lang` (`NB_GLD_SRV_POI_MULTI_LANG`). Read only, with no column change (D-2) |
| `lh_vv_gold.dbo.gld_srv_poi_review` | gold | `review_id` | `NB_GLD_SRV_POI_REVIEW` |
| `apps.srv_poi_review` | PostgreSQL serving | `review_id` (`sql/postgres/gld_srv_serve.pg.sql:125`) | Copy of `gld_srv_poi_review` |

## Keys

- `poi_id` formula source: `AGENTS.md` §7.
  - Third party: `poi_id = uuid_format(md5(concat(source_name, source_id)))`. This is `HASH_MD5_UUID` in `NB_SETUP_INITIAL_DDL` `TABLE_CONFIGS_3P`.
  - Partner: `uuid_md5(id, lit('partner'))`.
  - `poi_id` never includes language.
  - This task changes no key.
- `slv_enr_poi_destination`
  - Primary key: `poi_id STRING NOT NULL`. No uniqueness constraint is declared.
  - Business key: `poi_id`.
  - Foreign keys: none declared. `destination_id` has no declared target table.
- `gld_srv_poi_info`
  - Primary key: `poi_id`.
  - Business key: `poi_id`.
  - Foreign key: `poi_id` to `slv_enr_poi_destination.poi_id` (LEFT join).
- `apps.srv_poi_info`
  - Primary key: `poi_id`.
- `apps.srv_poi_multi_lang`
  - Primary key: `(poi_id, lang)`. Unchanged.
- `gld_srv_poi_review`
  - Primary key: `review_id`. It is `HASH_SHA256` over `_doc.source_name,_doc.source_id,authorAttribution.displayName,publishTime` in `TABLE_CONFIGS_3P` for `slv_3p_poi_review`.
  - Foreign key: `poi_id` to `slv_3p_poi_rating.poi_id` (LEFT join).
  - D-3 adds no key. The literal `source_name` is not part of the key.
- `apps.srv_poi_review`
  - Primary key: `review_id`. Unchanged.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `slv_enr_poi_destination` | `destination_name` | `STRING` | yes | None. DDL only, with no writer, so the value is null until a later load exists | D-1. The type is the same as the existing text columns `destination_id`, `city` and `street` (`decision.md` `## Lịch sử quyết định` D-1; request.md Constraints D-1) |
| `gld_srv_poi_info` | `destination_name` | `STRING` | yes | `slv_enr_poi_destination.destination_name` | D-1. Copy 1-1. Add it to `DEST_COLS` and to the gold output columns. For the partner-without-destination branch, the value is null because the name is not on the entity (`destination_name` is not in `ENTITY_OUT_COLS`) |
| `apps.srv_poi_info` | `destination_name` | `text` | yes | `gld_srv_poi_info.destination_name` | D-1. Copy 1-1. `text` is the same as `destination_id text` (`gld_srv_serve.pg.sql:28`). Add it to entity `SrvPoiInfo` (request.md In scope bullet 3) |
| `apps.srv_poi_multi_lang` | `experience` (unchanged) | `text` | yes | `gld_srv_poi_multi_lang.experience` | D-2. No new column. API `icon_key` = key `keyword` of the selected row's `experience` JSON element. A missing `keyword` gives null `icon_key` |
| `gld_srv_poi_review` | `source_name` | `STRING` | yes | Literal `google`, set in `NB_GLD_SRV_POI_REVIEW` | D-3. No join to `slv_3p_poi`. The active inputs stay `slv_3p_poi_review` and `slv_3p_poi_rating` |
| `apps.srv_poi_review` | `source_name` | `text` | yes | `gld_srv_poi_review.source_name` | D-3. Copy 1-1. The D-10 forbid line in `services/data-serving-service/AGENTS.md` is edited in this task (`decision.md` `## Lịch sử quyết định` D-3; request.md Constraints D-3) |

## Lineage

- `slv_enr_poi_destination`
  - Bronze: none.
  - Silver: this table is the landing table, and it has no writer (D-1).
  - `destination_name` is added by DDL only.
- `gld_srv_poi_info`
  - Bronze: none read directly.
  - Silver reads: `slv_poi_entity_non_enrich`, `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review`, `slv_poi_media_info`.
  - `slv_enr_poi_destination` `DEST_COLS` gains `destination_name`.
  - Gold reads: none.
- `apps.srv_poi_info`: copied from `gld_srv_poi_info`. PostgreSQL is not a lakehouse layer, so it has no gold-to-gold read.
- `apps.srv_poi_multi_lang`
  - Copied from `gld_srv_poi_multi_lang`. That table reads silver `slv_enr_poi_info_multi_lang`, `slv_poi_entity_non_enrich` and `slv_pn_business_service_i18ns`, and no gold.
  - No lineage change. `keyword` is read at the API from `experience` (D-2).
- `gld_srv_poi_review`
  - Bronze: `brz_3rd_crawler_poi_stream` feeds silver through `TABLE_CONFIGS_3P` (`NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`).
  - Silver reads: `slv_3p_poi_review` and `slv_3p_poi_rating`. These are unchanged, and there is no `slv_3p_poi` join.
  - `source_name` is a literal, not a read (D-3).
  - Gold reads: none.
- `apps.srv_poi_review`: copied from `gld_srv_poi_review`.

## Conflicts and questions

Not applicable.
