# Request

## User outcome

`lh_vv_gold.dbo.gld_srv_poi_info` carries the POI cover on the info row: `cover_id` from `slv_poi_media_info.media_id` and `cover_blob_url` from `slv_poi_media_info.blob_url`. `apps.srv_poi_info` has the same two columns. A POI with no cover stays one `gld_srv_poi_info` row and both columns are null.

## Scope

### In scope

- `notebooks/NB_GLD_SRV_POI_INFO.ipynb` cell `srvinfobuild`: LEFT JOIN the `slv_poi_media_info` row whose `is_cover` is the cover `gld_srv_poi_media_gallery` already uses. Gallery is a 1-1 projection of `slv_poi_media_info`; `is_cover` is computed on silver by `with_cover` and is not recomputed in the gallery.
- Gold DDL for `gld_srv_poi_info` in `notebooks/NB_CREATE_DDL.ipynb` and `notebooks/NB_SETUP_INITIAL_DDL.ipynb`, including a new ctrl edge to `slv_poi_media_info` when the model or architecture adds that read. Column types come from existing `media_id` and `blob_url`.
- `sql/postgres/gld_srv_serve.pg.sql` `CREATE TABLE apps.srv_poi_info`, types mapped by the header of that file.
- JPA entity `services/data-serving-service/src/main/java/vn/visitvietnam/dataserving/domain/entity/SrvPoiInfo.java`.
- `docs/context/mapping_gld_srv_poi_info.md`, updated in this task before review.
- `tests/test_srv_poi_serving_contract.py` must still pass (gold DDL + NodeSpec `pk` = PostgreSQL DDL = JPA entity).

### Out of scope

- A second cover rule, any change to `is_cover` or to `with_cover`, and any change to gallery grain or logic.
- Changing `gld_srv_poi_info` grain: one row per `poi_id`. NodeSpec `pk` stays `("poi_id",)`.
- A new endpoint, DTO, or API field.
- `docs/poi-serving-api/`.
- `pipelines/PL_VV_TRANS_SLV_TO_GLD_30M/PL_VV_TRANS_SLV_TO_GLD_30M.json`, unless the model or architecture shows the new `slv_poi_media_info` edge is declared in that JSON rather than in the ctrl seed inside the DDL notebooks.

## Acceptance criteria

- `gld_srv_poi_info` has `cover_id` and `cover_blob_url`, and each `poi_id` is still one row.
- The two values equal `media_id` and `blob_url` of the `slv_poi_media_info` row with the `is_cover` value that marks the cover for that `poi_id`. Both columns are null when that row does not exist.
- `apps.srv_poi_info` has the same two columns. The contract gold DDL + NodeSpec `pk` = PostgreSQL DDL = JPA entity still holds (`tests/test_srv_poi_serving_contract.py`). No new endpoint.
- `docs/context/mapping_gld_srv_poi_info.md` is updated in this task before review.

## Constraints

- One task for gold, PostgreSQL, the JPA entity, and the ctrl edge. Do not split them.
- Signal `data_model_change`. Do not invent column types or a cover predicate the named files do not show.
- This phase writes the request, classification, and model design, then runs the Architect. It does not edit notebooks, DDL, SQL, or the entity.

## Classification rationale

- Complexity: `medium`. Two new nullable columns and one new silver read. Fast lane does not apply: the column values change, and the edit spans the gold notebook, both DDL notebooks, PostgreSQL DDL, the JPA entity, and the mapping doc.
- Risk: `medium`. Bounded LEFT JOIN onto an existing one-row-per-`poi_id` MERGE. Rollback is reverting those columns. Local proof is `tests/test_srv_poi_serving_contract.py`. Not `high`: no watermark, lock, retry, or commit-order change, and the cross-system column contract is locally testable, so `risk-gate` is not required.
- Architecture: required. Not fast lane. The info node gains a read of `slv_poi_media_info` (ctrl edge, same shape as cell `srvratepy`) and the new columns must match across gold DDL, PostgreSQL, and the JPA entity. `data_model_change` requires `model-design.md` before `run-gate`.
- Evidence: not required. `with_cover` assigns one cover per `poi_id`, `unique_checks` names `one_cover_per_poi`, and `docs/context/mapping_poi_media_info.md` states that rule. `media_id` is `STRING NOT NULL` and `blob_url` is `STRING` on `MEDIA_COLS` in cell `mediaddlpy`. The Architect may still return `EVIDENCE_REQUIRED`.
- Runtime proof: not required for this classification. No new endpoint. Fabric apply and any `docker compose` step stay with the user and are not claimed here.
- Reviewer routing: `spark-runtime-reviewer` (notebook), `sql-data-reviewer` (join, grain, Delta DDL, PostgreSQL DDL), `api-contract-reviewer` (entity and `gld_srv_serve.pg.sql`), `jpa-performance-reviewer` (entity). No `fabric-pipeline-reviewer` while the pipeline JSON stays out of scope. No `app-security-reviewer` (diff does not touch `common/web/`, `config/`, `application*.yml`, `pom.xml`, or Docker files). No `state-correctness-reviewer` (no CDC, watermark, lock, or retry change).
