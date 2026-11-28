## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`
- Risk gate: not required

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `SQL-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:7366`: All missing control edges receive the same `MAX(id) + 1`, potentially corrupting control-row identity. Fix: carry `seq` into the MERGE source and assign `COALESCE(MAX(id), 0) + s.seq`.
- `SQL-002` — P1 — `notebooks/NB_GLD_SRV_PRODUCT_OFFER.ipynb:461`: The union lacks an enforced `product_id` uniqueness gate, so cross-branch collisions can create duplicate MERGE source keys. Fix: call `_require_unique` after `unionByName` and before enrichment/write.
- `SQL-003` — P1 — `.ai/tasks/20261127-gld-pn-product/evidence/probes/p7_gld_product_offer_readiness.sql:64`: P-7 checks destination duplicates for unused/deleted source keys and can incorrectly block deployment. Fix: derive candidate POIs only from effective live holiday and hotel rows before checking duplicates.
- `SPARK-001` — P1 — `notebooks/NB_CREATE_DDL.ipynb:7300`: A failure during the owner read after lease acquisition skips cleanup because `held` is still false, leaving `_GLD30` locked for up to 90 minutes. Fix: set `held = True` immediately after the acquisition update and clear it only when a successful owner read proves another owner.

## Lower-severity findings

P2: 1; P3: 0.

Probe: After correcting `SQL-003`, run P-7 in Fabric DEV and save its aggregate-only result before enabling the edges.
