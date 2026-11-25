## Model and reviewer manifest

- Model: `gpt-5.6-sol`; reasoning: `medium`.
- Independent reviewers: `sql-data-reviewer`, `spark-runtime-reviewer`.
- `risk-gate`: completed. Its `GATE-001` duplicates `SQL-001`; its round-cap concern is resolved by the user's explicit round-4 request and the recorded approval in `decision.md`.

## Gate verdict: `EVIDENCE_REQUIRED`

| ID | Severity | Location | Failure | Fix |
|---|---|---|---|---|
| SQL-001 | P1 | `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb:549` | Runtime evidence does not yet prove the complete `$.is_24_7 → is_247 → Python UDF → operating_hours/hours_reason` path, so affected rows could remain null or be misclassified. | Run the bounded Fabric DEV `PLAN` probe and require exact classification plus valid seven-day all-day JSON before `RUN`. |

P2: 1. P3: 0.

Probe: PASS only when `eligible_n = reason_n`, `reason_n >= 6430`, `bad_n = 0`, `unexpected_n = 0`, `sum(hours_reason) = candidates`, `GOOGLE_BAD_TIME = 0`, `NO_DETAIL = 0`, and `hours_24_7_partner_n` is reported.
