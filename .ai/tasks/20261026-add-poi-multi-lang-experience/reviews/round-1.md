## Model and reviewer manifest

- Coordinator: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`
- Risk gate: not required

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

| ID | Severity | File:line | Failure | Fix |
|---|---|---|---|---|
| SPARK-001 | P1 | `notebooks/NB_CREATE_DDL.ipynb:4428`; `notebooks/NB_GLD_SRV_POI_MULTI_LANG.ipynb:82` | Fabric DEV evidence is missing for the physical `usps STRING` contract, Delta column patch, idempotent rerun, and resulting gold `experience` rule. | Complete the bounded DEV runtime probe before publishing or granting runtime PASS. |

P2/P3: **0**.

Probe: Confirm `usps` is physical `string`; run `mlexppy` twice with the second run returning `experience: +[]`; verify nullable `experience string` after `description` and released lock; then run gold and require `mismatch = 0` and duplicate `(poi_id, lang)` count `= 0`.
