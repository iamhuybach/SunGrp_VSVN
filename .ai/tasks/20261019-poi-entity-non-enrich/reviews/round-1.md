## Manifest

Model: `gpt-5.6-sol` (`medium`). Reviewers: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`; `risk-gate` completed.

## Verdict

`FIX_REQUIRED`

## P0/P1 findings

- `GATE-001` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:852,861`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:785,794`: Releasing the flow lock between the entity and amenity switches lets `NB_00` observe mixed edge generations and advance partial state. Fix: hold one durable cutover lease across both switches or commit both edge sets atomically.
- `GATE-002` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:770,824`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:706,757`: The edge MERGE commits before conflicting/stale-state validation, so a failed post-check leaves partially switched durable control state. Fix: perform complete ownership and stale-state validation under the lock before MERGE.
- `GATE-003` — P1 — `notebooks/NB_SLV_POI_ENTITY_NON_ENRICH.ipynb:134`: Deeply nested `amentities` can raise `RecursionError`, causing deterministic Spark retries and node failure. Fix: use iterative document-order traversal and classify parser/depth failures as `JSON_INVALID`.
- `GATE-004` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:782`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:715`: MERGE keys omit `src_schema` and `trg_schema`, allowing same-named foreign-schema edges to be rewritten or retired. Fix: include both schemas in the MERGE source, match key, and all related validation predicates.

P2: 3. P3: 0.
