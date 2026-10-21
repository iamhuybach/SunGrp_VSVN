## Review manifest

Model: `gpt-5.6-sol` (`medium`). Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`; `risk-gate` completed.

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

- `SQL-001` — P1 — `notebooks/NB_ENR_POI_INFO.ipynb:240`: The entity spine does not enforce one non-null row per `poi_id`, so duplicate or null keys can fail the append PK check on every retry. Fix: prove the source invariant in DEV or deterministically reduce the spine to exactly one non-null row per `poi_id`.
- `SQL-002` — P1 — `notebooks/NB_ENR_POI_INFO.ipynb:199`: Multiple live Vietnamese i18n rows for one `business_service_id` can multiply partner candidates at the join on line 256. Fix: prove uniqueness in DEV or deterministically select one row per service and reject conflicting values.

`SPARK-001` and `STATE-001` are fixed. P2: 1; P3: 0.

Probe: both queries must return zero rows — `SELECT poi_id, COUNT(*) AS n FROM lh_vv_silver.dbo.slv_poi_entity_non_enrich GROUP BY poi_id HAVING poi_id IS NULL OR COUNT(*) > 1 LIMIT 50;` and `SELECT business_service_id, COUNT(*) AS n FROM lh_vv_silver.dbo.slv_pn_business_service_i18ns WHERE locale='vi' AND NOT COALESCE(deleted,false) GROUP BY business_service_id HAVING business_service_id IS NULL OR COUNT(*) > 1 LIMIT 50;`
