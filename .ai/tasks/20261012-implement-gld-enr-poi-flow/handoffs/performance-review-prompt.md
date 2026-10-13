# Advisory performance review: 20261012-implement-gld-enr-poi-flow

You are the VSVN Review Coordinator. This is a read-only advisory review. Do not edit any file. Do not run notebooks or pipelines. Do not call risk-gate, state-correctness-reviewer, fabric-pipeline-reviewer, Architect, or requirements-analyst.

Spawn these two specialists independently. They must not read each other's findings:

- spark-runtime-reviewer
- sql-data-reviewer

Both use model gpt-5.6-sol and reasoning effort medium. After both finish, write one consolidated report.

## Scope

Read:

- .ai/tasks/20261012-implement-gld-enr-poi-flow/task-state.yaml
- .ai/tasks/20261012-implement-gld-enr-poi-flow/decision.md
- .ai/tasks/20261012-implement-gld-enr-poi-flow/runtime-runbook.md
- .ai/tasks/20261012-implement-gld-enr-poi-flow/architecture.md
- notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb
- notebooks/NB_00_ORCHES_SLV_TO_ENR_15P.ipynb
- notebooks/NB_SLV_PN_POI.ipynb
- notebooks/NB_ENR_POI_INFO.ipynb
- notebooks/NB_ENR_POI_COORDINATE.ipynb
- notebooks/NB_ENR_POI_REVIEW.ipynb
- notebooks/NB_CREATE_DDL.ipynb, only the enrich DDL and seed cell
- pipelines/PL_VV_TRANS_SLV_TO_ENR_15P/PL_VV_TRANS_SLV_TO_ENR_15P.json

Capacity is shared Fabric F16. Design cadence is 15 minutes. Targets are append-only Delta tables lh_vv_gold.enr.gld_enr_poi_info, gld_enr_poi_coordinate, and gld_enr_poi_review.

Observed Fabric DEV results already in runtime-runbook.md. Do not invent new volumes:

- First RUN, exec bfa377b3-6294-483c-ac0d-9c267ff4e344, SUCCESS, 169s. inserted: info 17, review 85, slv_pn_poi 30, coordinate 47. 13 edges advanced.
- Second RUN, exec b98cfec5-48a5-491a-8f16-84d27979b945, NO_DATA, 39s, 0 dirty edges.
- Force review, exec 85e5431c-c336-4fcf-8343-4d7079aaebdc, SUCCESS, 102s, inserted 85, version 2, 1 edge.
- Force info, exec b003ae85-8c7f-4ea0-861a-7bfe8d7295da, SUCCESS, 102s, inserted 17, version 2, 7 edges.
- Force coordinate, exec e98b1132-1209-4398-8ed6-a9f801ca957b, SUCCESS, 84s, inserted 47, version 2, 3 edges.
- DESCRIBE HISTORY: version 0 CREATE TABLE; versions 1 and 2 are WRITE Append with userMetadata vv_append 1. No MERGE, UPDATE, or DELETE.

The pipeline trigger step is waived for this turn. Still review the pipeline JSON. Do not ask the operator to run it.

## What to propose

Proposals only. Do not treat this as a new remediation round. Keep append grain, keys (poi_id, updated_at) or (review_id, updated_at), and the decisions already recorded in decision.md.

Each proposal must name the file, the cell or function, the extra work or the slow step, and the change direction.

Split the report into two groups:

1. Correct processing: redundant work, wrong action placement, unnecessary scans, or logic that can produce the wrong append set.
2. Speed: F16 cost, Spark actions, shuffles, cache, and the 15-minute cadence.

The report must start with these two lines:

Model: gpt-5.6-sol
Effort: medium

Then a section for spark-runtime-reviewer and a section for sql-data-reviewer, then the consolidated proposal list.
