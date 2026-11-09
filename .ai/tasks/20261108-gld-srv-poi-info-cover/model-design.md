# Model design — 20261108-gld-srv-poi-info-cover

## Scope

- Base task: `20261108-gld-srv-poi-info-cover` (`task-state.yaml`: `data_model_change`, `cross_system`; status `waiting_architecture`).
- Ledger row implemented: `decision.md` `## Quyết định hiện hành` **D-01**. Add `cover_id` and `cover_blob_url` to `lh_vv_gold.dbo.gld_srv_poi_info` and `apps.srv_poi_info` in one task. They come from `slv_poi_media_info.media_id` and `.blob_url` through a LEFT JOIN on the `is_cover` row that gallery already uses. Not in scope: a second cover rule, any change to `is_cover`, or any change to the one-row-per-`poi_id` grain.
- Request sections: `request.md` `## User outcome`, `## Scope`, `## Acceptance criteria`.
- `proposal.md`, `problem-analysis.md` and `requirements-analysis.md` do not exist for this task. So `proposal.md` `## Dòng thay đổi` and `## ctrl_cfg_schema_registry` cannot be cited. D-01 and `request.md` are the only sources for every rule below.
- Out of scope, per `request.md` `### Out of scope`: `with_cover`, `is_cover`, `NB_GLD_SRV_POI_MEDIA_GALLERY`, `slv_poi_media_info` schema, endpoints, DTOs, `docs/poi-serving-api/`, pipeline JSON.

## Entities and grain

| table | layer | grain | node notebook |
|---|---|---|---|
| `lh_vv_gold.dbo.gld_srv_poi_info` | gold | one row per `poi_id` (unchanged; D-01) | `NB_GLD_SRV_POI_INFO` (`id:srvinfobuild`) |
| `apps.srv_poi_info` | PostgreSQL serving (`sql/postgres/gld_srv_serve.pg.sql`), JPA entity `SrvPoiInfo` | one row per `poi_id` (`PRIMARY KEY (poi_id)`, unchanged) | none (DDL file and JPA entity) |
| `lh_vv_silver.dbo.slv_poi_media_info` | silver, read-only here | one row per (`media_id`, `poi_id`); one `is_cover` row per `poi_id` (`with_cover`, `unique_checks` `one_cover_per_poi`) | `NB_SLV_POI_MEDIA_INFO` (unchanged) |
| `lh_vv_ctrl.dbo.ctrl_mng_pipeline_config` | ctrl | one row per edge | none. New edge row `slv_poi_media_info` → `gld_srv_poi_info`, seeded in `NB_CREATE_DDL` and in `NB_SETUP_INITIAL_DDL` `id:init_seed_ctrl` |

## Keys

- `gld_srv_poi_info`
  - Primary key: `poi_id`. NodeSpec `pk=("poi_id",)` stays as is. Gold DDL `('poi_id', 'STRING NOT NULL')` in `NB_SETUP_INITIAL_DDL` `id:init_tables` and in `INFO_COLS` of `NB_CREATE_DDL` `id:srvratepy`.
  - Business key: `poi_id`. AGENTS.md §7 gives the formula. Third-party `poi_id = uuid_format(md5(concat(source_name, source_id)))` (`HASH_MD5_UUID`). Partner `poi_id = uuid_md5(id, lit('partner'))` from `slv_pn_business_services.id` / `slv_pn_business_service_i18ns.business_service_id`.
  - Foreign key (logical, not enforced): `poi_id` → `slv_poi_media_info.poi_id`, restricted to the row where `is_cover` is true. Optional: zero or one match. `cover_id` names the matched `slv_poi_media_info.media_id`, so (`cover_id`, `poi_id`) is the key of that silver row and of the matching `gld_srv_poi_media_gallery` row (`pk=("media_id", "poi_id")`). No physical constraint is added.
- `apps.srv_poi_info`: primary key `poi_id`, `PRIMARY KEY (poi_id)`, unchanged. No FK constraint. The file header says it creates no index, view or grant.
- `slv_poi_media_info`: primary key (`media_id`, `poi_id`), unchanged. `poi_id` uses the same formula. `mapping_poi_media_info.md` §1.2 states Google `slv_3p_poi_media.poi_id` 1-1 and partner `uuid_md5(business_service_id, 'partner')`, which matches AGENTS.md §7.
- `ctrl_mng_pipeline_config`: the new edge keys on (`pl_name`, `src_schema`, `src_tbl`, `trg_schema`, `trg_tbl`), the `NOT EXISTS` predicate in `id:srvratepy`. Values: `src_schema` = `lh_vv_silver.dbo`, `src_tbl` = `slv_poi_media_info`, `trg_schema` = `lh_vv_gold.dbo`, `trg_tbl` = `gld_srv_poi_info`. `pl_name` is open: see Conflicts 3.

## Columns

| table | column | type | nullable | source | rule |
|---|---|---|---|---|---|
| `gld_srv_poi_info` | `cover_id` | `STRING` | yes | `slv_poi_media_info.media_id` | D-01. The value is `media_id` of the `slv_poi_media_info` row for the same `poi_id` where `is_cover` is true. `with_cover` sets `is_cover = row_number() == 1` per `poi_id`, so true marks the cover. `mapping_poi_media_info.md` §1.2 `is_cover` states the same. LEFT JOIN: null when no such row exists. The source is `STRING NOT NULL` (`MEDIA_COLS` in `id:mediaddlpy`), but the target is nullable because of the LEFT JOIN (D-01). No cast and no fallback. |
| `gld_srv_poi_info` | `cover_blob_url` | `STRING` | yes | `slv_poi_media_info.blob_url` | D-01. Same row and same join as `cover_id`. Copied 1-1 with no trim, as silver already applies (`mapping_poi_media_info.md` §1.2 `blob_url`). Null when there is no cover row, or when that row's `blob_url` is null. The source is `STRING` (`MEDIA_COLS`). |
| `apps.srv_poi_info` | `cover_id` | `text` | yes | `gld_srv_poi_info.cover_id` | D-01. Uses the `STRING -> text` row of the `gld_srv_serve.pg.sql` header. No `NOT NULL`: the header puts `NOT NULL` only on gold `NOT NULL` key columns. JPA `SrvPoiInfo`: `@Column(name = "cover_id") private String coverId;`, like the existing `String` fields. |
| `apps.srv_poi_info` | `cover_blob_url` | `text` | yes | `gld_srv_poi_info.cover_blob_url` | D-01. Same mapping. JPA `@Column(name = "cover_blob_url") private String coverBlobUrl;`. |

Column order inside `OUT_COLS`, gold DDL, PostgreSQL DDL and the entity: see Conflicts 1. No source filter on `source_name`: D-01 applies the cover to every `gld_srv_poi_info` row, Google and partner alike. `rating_*` and `review_count` differ because they are Google-only (mapping §1.2).

## Lineage

- `gld_srv_poi_info`
  - Bronze reads: none directly.
  - Silver reads, existing: `slv_poi_entity_non_enrich`, `slv_enr_poi_destination`, `slv_enr_poi_info_multi_lang`, `slv_3p_poi_rating`, `slv_3p_poi_review` (`SPEC.inputs`; ctrl edges at `NB_SETUP_INITIAL_DDL` `id:init_seed_ctrl` and `id:srvratepy`).
  - Silver read, new: `slv_poi_media_info`, selecting `poi_id`, `media_id`, `blob_url`, `is_cover`. It needs a new `SPEC.inputs` entry and a new ctrl edge with the same shape as the `id:srvratepy` `EDGES_ON` rows: `RECOMPUTE`, `nb_name` `NB_GLD_SRV_POI_INFO`, priority `1`.
  - Gold reads: none. The cover comes from silver `slv_poi_media_info`, not from `gld_srv_poi_media_gallery`. Gallery is a 1-1 `select(*OUT_COLS)` of the same silver table (`id:srvgallerybuild`), so both gold tables get the same `is_cover` row from the same source.
- `apps.srv_poi_info`: loaded from `gld_srv_poi_info`. This design adds no loader and no edge for it.
- `slv_poi_media_info`: upstream is silver `slv_3p_poi_media`, `slv_pn_business_service_i18ns`, `slv_pn_business_services` (unchanged; `id:mediaddlpy` `EDGES_ON`).

## Conflicts and questions

1. **Column position.** None of the named files says where `cover_id` and `cover_blob_url` go. The last additive change (`id:srvratepy`) placed `rating_overall`, `rating_count`, `review_count` right after `holiday_exceptions`, before `row_hash`, using `ALTER ... AFTER`. Should the new pair go right after `review_count` and before `row_hash`, in the order `cover_id`, `cover_blob_url`, consistently in `OUT_COLS`, gold DDL (`id:init_tables`, the new `NB_CREATE_DDL` cell), `apps.srv_poi_info`, and `SrvPoiInfo`? Please confirm.
2. **Soft-deleted silver rows and the cover predicate.** `slv_poi_media_info` has `soft_delete_set={"is_active": "false"}` with `write_mode="MERGE"`. The files do not show whether a soft-deleted row keeps `is_cover = true`. They also do not show whether `unique_checks` `one_cover_per_poi` checks the build output or the persisted table, or whether `ctx.input(...)` without `live_only` (gallery's call) filters such rows. Constraint applied: do not add `is_active`. The design therefore copies gallery exactly: the input is read with the same `ctx.input` default as gallery, the predicate is `is_cover` true, and nothing else is added. Open: can more than one `is_cover` row per `poi_id` reach the info node through that input? If yes, the LEFT JOIN breaks the one-row-per-`poi_id` grain. The Architect should settle this, either with evidence or with a guard that stops the run instead of choosing a row.
3. **`pl_name` of the new ctrl edge.** `id:srvratepy` and `id:mediaddlpy` hold the literal `PL_VV_TRANS_SLV_TO_GLD_30P`. `mapping_gld_srv_poi_info.md` §1.1 says the current pipeline is `PL_VV_TRANS_SLV_TO_GLD_30M` (renamed by `plcadpy`). `id:init_seed_ctrl` uses `_GLD30`, whose value I did not read. Which `pl_name` should the new edge in `NB_CREATE_DDL` use? Please confirm that it must match the five existing `gld_srv_poi_info` edges.
4. **Required vs optional input.** D-01 asks for a LEFT JOIN with null on no match. The files do not say whether `slv_poi_media_info` goes into `required_inputs` (today `("entity",)`) or stays optional. When the input is missing or empty, should both columns be null or should the run stop? This is for the Architect; no rule is invented here.
5. **Mapping doc.** `request.md` requires updating `docs/context/mapping_gld_srv_poi_info.md` §1.1 (inputs, edge list) and §1.2 (two new field-mapping rows) in this task. The wording follows D-01 and the answers to 1–3.
