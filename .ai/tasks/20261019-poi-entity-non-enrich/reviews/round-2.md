## Manifest

Model: `gpt-5.6-sol`, reasoning: `medium`.

Reviewers: `state-correctness-reviewer`, `spark-runtime-reviewer`, `sql-data-reviewer`; `risk-gate` completed.

## Verdict

`FIX_REQUIRED`

## P0/P1 findings

- `STATE-001` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:733,774-781,822`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:678,705-716,744`: Pre-validation rejects the valid legacy `slv_poi_entity → slv_poi_amenity` edge before the MERGE can retire it, so every cutover retry fails. Fix: allow only the exact planned RETIRE tuple through `extra`, continue rejecting wrong owners/schemas, and add an executable state-fixture test.
- `SQL-001` — P1 — `notebooks/NB_SETUP_POI_ENTITY.ipynb:782-798`; `notebooks/NB_SETUP_POI_AMENITY.ipynb:717-723`: Stale checks count same-named active edges from foreign schemas and incorrectly block setup. Fix: constrain each stale query directly by both silver schemas and add a foreign-schema isolation fixture.

`GATE-003` is closed. No additional P0/P1 was found by the risk gate.

P2/P3: `0/0`.

Probe: none required; both failures follow deterministically from the SQL predicates.
