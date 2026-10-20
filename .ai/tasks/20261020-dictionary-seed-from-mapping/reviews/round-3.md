## Manifest

Model: `gpt-5.6-sol`, reasoning `medium`.

Reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`, `state-correctness-reviewer`; final `risk-gate` completed.

## Verdict

`EVIDENCE_REQUIRED`

All reviewers and the risk gate confirmed `GATE-001` and `GATE-002` are fixed. No unresolved P0/P1 findings; P2/P3: `0/0`. Required Fabric DEV runtime evidence remains pending, so the constitution prevents `PASS`.

Probe: User runs `runtime-runbook.md` R3–R10 in Fabric DEV and records sanitized backup-equivalence, `inserted=0`/`drift=0`, and post-R10 outputs under `evidence/results/`.
