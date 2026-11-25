## Manifest

- Model: `gpt-5.6-sol`, reasoning `medium`
- Reviewers: `sql-data-reviewer` PASS; `spark-runtime-reviewer` PASS; `risk-gate` EVIDENCE_REQUIRED
- `SQL-001`: closed; `rank1_source_conflict_n = 0`

## Gate verdict

`EVIDENCE_REQUIRED` — không có P0/P1 trong implementation diff, nhưng runtime gate Fabric DEV vẫn đang pending.

## Findings

Không có P0/P1. P2: 0. P3: 0.

Probe: Chạy PLAN, RUN và replay cùng `pins`; yêu cầu `map.drift_n=0`, `rating_cast_fail_n=0`, commit `COMMITTED`, không duplicate `poi_id`, hai chiều `EXCEPT ALL` cho `load_origin IS NULL` đều bằng 0, partner rating/review đều NULL và `is_recommended` chỉ true cho partner.
