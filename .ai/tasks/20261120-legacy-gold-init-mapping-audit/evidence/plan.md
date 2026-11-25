# Evidence plan

## Decision to resolve

D-01, D-03, D-04, and D-05 are recorded in `decision.md`. D-02 waits on `evidence/probes/hours_shape.py`: the key set inside `$.periods` for `ingestion_source = google`.

## Existing evidence

- `evidence/column-mapping.md` — column comparison from the init notebook, the old-flow notebooks, and the current gold notebooks.
- `evidence/results/hours-shape.txt` — key names and counts from the 2026-11-24 probe. `$.periods` is null. Hours are in `$.periods_json`.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| evidence/probes/hours_shape.py | Notebook in workspace `sgr_visitvn_dev`, default lakehouse `lh_vv_gold`. Read-only. | Which keys sit inside old `poi_opening_hours_json.periods` and `holiday_exceptions_json`, and how many new-gold hour columns are null? | Done. `$.periods` is null. Hours are in `$.periods_json`. | evidence/results/hours-shape.txt |
| evidence/probes/review_round1_guards.py | Same notebook. Read-only. | Do two `lang = vi` map rows share one new `poi_id`, and does `total_reviews` survive a bigint round trip? | Done. `vi_key_collision_n` = 1. `rating_not_exact_bigint_n` = 0. | evidence/results/review-round1-guards.txt |
| evidence/probes/vi_key_rank1_source.py | Same notebook. Read-only. | After D-06 rank 1, does one new `poi_id` still have two `source_name` values? | PASS iff `rank1_source_conflict_n` = 0. | evidence/results/vi-key-rank1-source.txt |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
