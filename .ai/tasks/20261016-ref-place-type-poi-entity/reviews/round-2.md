## Review manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: not required

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

| ID | Severity | Location | Failure | Fix |
|---|---|---|---|---|
| SQL-001 | P1 | `notebooks/NB_SETUP_POI_ENTITY.ipynb:716,721`; `docs/context/CTRL_TABLES_CONTEXT.md:120` | Schema fields in the `MERGE ON` clause prevent normalization of a same-pipeline edge with schema drift, while nullable state comparisons can evaluate to `UNKNOWN` and skip the required update. | Match by logical edge identity, update `src_schema` and `trg_schema`, and use null-safe comparisons for every expected state field. |
| STATE-001 | P1 | `notebooks/NB_SETUP_POI_ENTITY.ipynb:691,711,755,773` | Another writer can activate a different owner between the owner check and MERGE, leaving durable multiple-owner state even though the post-check fails. | Serialize owner-check, MERGE, and post-check with a shared lock or lease honored by all edge writers, recheck ownership after locking, and define recovery for existing multi-owner state. |

## Lower-severity findings

P2: 2; P3: 0.
