## Review manifest

- Model: `gpt-5.6-sol` (`medium`)
- Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`
- Risk gate: not required

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

- `SPARK-001` — P1 — `notebooks/NB_ENR_POI_INFO.ipynb:275`, `notebooks/NB_ENR_POI_REVIEW.ipynb:120`: unconditional full-set `distinct`, `left_anti`, and `count()` warning jobs may exceed the 15-minute cadence or pressure shared F16 capacity at unknown production scale. Fix: persist and reuse distinct-key frames and run unmatched-key diagnostics only for dirty landing roles, or move the diagnostics outside the 15-minute node, if the runtime probe fails.

P2/P3: 0/0.

Probe: In Fabric DEV after the full baseline, add one landing key and run both nodes in `DRY_RUN`; capture wall time, input bytes, shuffle read/write, spill, and peak executor memory for warning jobs, requiring completion under 15 minutes without OOM or sustained spill.
