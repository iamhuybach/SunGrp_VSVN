# Author input

## User comments verbatim

Tên schema: apps.
Tên bảng tiền tố bỏ gld_; Bắt đầu bằng srv_.
review_id bỏ field lang
BIGINT sẽ là INT8

## Files and anchors

- `.ai/tasks/20261029-pg-ddl-gld-srv-serve/decision.md` — `Quyết định hiện hành` and `Bảng kiểm`
- `.ai/tasks/20261029-pg-ddl-gld-srv-serve/request.md` — User outcome, Acceptance criteria, Constraints
- `AGENTS.md` — section 7, `poi_id` formulas
- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` — cell 4 `NodeSpec` `pk`
- `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb` — cell 3 `NodeSpec` `pk`
- `notebooks/NB_GLD_SRV_POI_AMENITY.ipynb` — cell 3 `NodeSpec` `pk`
- `notebooks/NB_GLD_SRV_POI_MEDIA_GALLERY.ipynb` — cell 3 `NodeSpec` `pk`
- `notebooks/NB_GLD_SRV_POI_REVIEW.ipynb` — cell 3 `NodeSpec` `pk`
- `notebooks/NB_SETUP_INITIAL_DDL.ipynb` — cell id `init_tables`, only the five `lh_vv_gold.dbo.gld_srv_poi_*` specs
- Do not read `notebooks_lgc/` or `srv_*` tags in `docs/diagram/VSVN_DATA_MODEL.drawio`.

## Constraints

- Design the five PostgreSQL serving tables only. Do not change Fabric tables, keys, or columns.
- Schema `apps`. Table names: `srv_poi_info`, `srv_poi_multi_lang`, `srv_poi_amenity`, `srv_poi_media_gallery`, `srv_poi_review`.
- Grain and primary-key order are `NodeSpec.pk`. Do not change keys.
- `apps.srv_poi_review` omits gold column `lang`. Every other gold column is copied.
- Types: `STRING` → `text`, `BOOLEAN` → `boolean`, `INT` → `integer`, `DOUBLE` → `double precision`, `DECIMAL(p,s)` → `numeric(p,s)`, `TIMESTAMP` → `timestamp without time zone`, `BIGINT` → `int8`.
- `NOT NULL` only where gold DDL says `NOT NULL`, plus primary-key columns. Those key columns are already `STRING NOT NULL` in gold DDL.
- No extra columns, indexes, views, or a sync job.
- `proposal.md` does not exist. Ledger rows D-TYPE, D-SCHEMA, D-NAME, D-LANG, D-BIGINT, and D-MODEL are the accepted decisions.
- `poi_id` formulas are in `AGENTS.md` section 7. Do not invent another formula.
