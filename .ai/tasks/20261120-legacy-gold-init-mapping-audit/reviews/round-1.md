## Review manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`
- Risk gate: completed

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

- `SQL-001` — P1 — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:586`: unordered `vi_key.dropDuplicates(["_new"])` can select different legacy keys across reruns when mappings collide. Prove zero collisions or add a pre-dedup collision guard and a business-approved deterministic selection rule.
- `SQL-002` — P1 — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:588`: casting non-integral `total_reviews` directly to `bigint` can silently truncate while the current cast-failure guard passes. Prove exact bigint representability or add an integrality/round-trip guard before writing.

P2: 2. P3: 0.

Probe: `PASS iff vi_key_collision_n == 0 AND rating_not_exact_bigint_n == 0` on the same pinned input used for RUN.
