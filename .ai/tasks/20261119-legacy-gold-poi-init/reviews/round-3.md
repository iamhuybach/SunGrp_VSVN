## Model and reviewer manifest

- Model: `gpt-5.6-sol`, reasoning: `medium`
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: completed

## Gate verdict

`FIX_REQUIRED`

## P0/P1 findings

- `GATE-004` — P1 — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:152`: History iteration or `operationMetrics` parsing can fail after MERGE, skip cleanup, and mask the original write result or exception. Fix: place all reconciliation inside a best-effort boundary, accept map and JSON metrics, return `UNKNOWN` on failure, run cleanup in `finally`, and preserve the original exception.
- `GATE-005` — P1 — `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:365`: A lock-release failure after successful commits is suppressed while the notebook still reports `SUCCESS`, potentially leaving an ambiguous stale lock. Fix: propagate unlock failure when there is no primary exception; suppress it only to preserve an existing primary exception.

`GATE-001` is closed: source-only rows remain insert candidates and do not count as drift.

P2: 4. P3: 0.

Probe: none required; both P1 failures are deterministic from source control flow.
