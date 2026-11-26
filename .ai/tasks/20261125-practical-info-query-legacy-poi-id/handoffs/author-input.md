# Author input

Kind: model. `proposal.md`, `problem-analysis.md`, and `requirements-analysis.md` are absent. Do not invent them.

## Design question

`sql/postgres/gld_srv_serve.pg.sql` (schema `apps`) and the Java entities under `services/data-serving-service` have no table or column that resolves a legacy `poi_id` to the new `poi_id`. Design the minimum gold and PostgreSQL shape so `/api/v1/pois/**` can accept either id and return the same already-mapped record.

## Use only these sources

- Formula already stored on the map: `docs/context/mapping_legacy_gold_to_gld_srv.md` (the `gld_poi_legacy_id_map` table and the google / partner_portal formulas). Do not write a second `poi_id` formula.
- Map columns already declared in `notebooks/NB_CREATE_DDL.ipynb` cell `legacyidpy`, `MAP_COLS`: `legacy_poi_id` STRING NOT NULL, `lang` STRING, `legacy_ingestion_source` STRING, `source_id` STRING, `source_name` STRING, `poi_id` STRING, `poi_id_status` STRING NOT NULL. Table `lh_vv_gold.dbo.gld_poi_legacy_id_map`.
- How rows are written and joined: `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb` cell `lgpmain`. Key used there is `legacy_poi_id`. Joins that build the new gold rows keep `poi_id_status = 'OK'`.
- Silver name of the old id: `docs/context/01_DATA_MODEL.md` §6.1 `ref_poi_legacy_id` (key `legacy_poi_id`) and §8 `legacy_poi_id`. Do not re-guess the old id formula.
- Serving keys today: `services/data-serving-service/AGENTS.md` section Contract, and `sql/postgres/gld_srv_serve.pg.sql`. The API reads PostgreSQL `apps` only.

## Rules

- A column that is not in `MAP_COLS` or in `gld_srv_serve.pg.sql` goes under `## Conflicts and questions`. Do not add it.
- Prefer exposing the existing map columns to the PostgreSQL contract. Do not recompute `poi_id` in the API.
- `proposal.md` has no `## Dòng thay đổi`. Where the template asks for that citation, write `Not applicable.` Cite D-ID-UNIT only to exclude it.

## Out of scope

- Ledger D-ID-UNIT: one request accepts at least 1 and at most 500 `poi_id` values. That is an API input count. It is not a column, a numeric domain, a string length, or pagination `size`.
- Endpoint grain, `required_fields`, `source`, `poi_name`, `lang`, `page`, `size`, `sort_field`, `sort_order`. The Architect owns those.
- Do not read `docs/poi-serving-api/`, `notebooks_lgc/`, pipeline manifests, or other tasks.
