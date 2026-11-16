# Author input — model

No `proposal.md`, `problem-analysis.md`, or `requirements-analysis.md`. Rules are `request.md` and `decision.md` ledger D-1 through D-4. Cite those rows in `rule`. Write `Not applicable.` for a missing proposal section.

## Read

- `.ai/tasks/20261116-srv-poi-info-is-active/request.md`
- `.ai/tasks/20261116-srv-poi-info-is-active/decision.md` section `Quyết định hiện hành`
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` cell `srvinfobuild` (`OUT_COLS`)
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` cell `init_tables`, spec `lh_vv_gold.dbo.gld_srv_poi_info`
- `notebooks/NB_CREATE_DDL.ipynb` cells `srvpoipy`, `srvratepy`, `srvcoverpy`, `poidestpy` (current `gld_srv_poi_info` columns only)
- `docs/context/mapping_gld_srv_poi_info.md` section `1. Table`
- `sql/postgres/gld_srv_serve.pg.sql`
- `tests/test_srv_poi_serving_contract.py`: `test_gold_and_pg_columns_and_types_match`, `test_entities_match_gold_columns_types_and_keys`
- `services/data-serving-service/AGENTS.md` section `Contract`
- Entities `SrvPoiInfo`, `SrvPoiMultiLang`, `SrvPoiAmenity`, `SrvPoiMediaGallery`, `SrvPoiReview`

## Rules for the model

- Grain and keys stay. `poi_id` formulas unchanged. Gold does not read gold. Do not design migration, locks, or rollout.
- D-1: `lh_vv_gold.dbo.gld_srv_poi_info.is_active` BOOLEAN, nullable, immediately after `is_bookable`. No source column. Literal `true` on every row `NB_GLD_SRV_POI_INFO` writes. Not derived from `deleted_at`.
- D-2: `apps.srv_poi_info.is_active` copies that gold column. `ingestion_ts` is `timestamp without time zone`, nullable, immediately after `deleted_at`, on every `CREATE TABLE apps` in the file. Today those tables are `srv_poi_info`, `srv_poi_multi_lang`, `srv_poi_amenity`, `srv_poi_media_gallery`, `srv_poi_review`. `apps.srv_poi_media_gallery.is_active` already exists; leave it. `ingestion_ts` is PostgreSQL only: not silver, not gold, and no writer job. State that in Columns and Lineage.
- D-3: the serving contract may allow `ingestion_ts` on every apps table although gold has no such column. `apps.srv_poi_info.is_active` must match `gld_srv_poi_info`. Record this as a resolved rule under Conflicts and questions, not an open question.
- D-4: entities map every new PostgreSQL column. JSON API and `docs/context/api-mapping/` do not gain these columns.
- Do not invent a `json_path`, source, or job for `ingestion_ts`.
