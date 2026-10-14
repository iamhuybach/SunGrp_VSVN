## Model and reviewer manifest

`gpt-5.6-sol`, reasoning `medium`. Reviewers: `state-correctness-reviewer`, `sql-data-reviewer`, `spark-runtime-reviewer`; `risk-gate` completed.

## Gate verdict

`EVIDENCE_REQUIRED`

## P0/P1 findings

- `GATE-001` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:666`: Documents sharing the complete ordering tuple can contain different payloads, making visibility selection and retries nondeterministic. Fix: prove no conflicting ties exist, or reject them/add an immutable total-order field consistently across selection, state, and MERGE.
- `GATE-002` — P1 — `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:698`: Duplicate target `review_id` rows generate duplicate hide-source keys and can make the Delta MERGE ambiguous. Fix: prove target uniqueness; otherwise repair duplicates and add a preflight uniqueness guard.

P2/P3: 2 (`P2=1`, `P3=1`).

Probe: run one DEV query returning `ambiguous_order_groups` for differing `normalized_payload` values grouped by `(source_name, source_id, CAST(crawled_at AS TIMESTAMP), event_id)` and `duplicate_target_review_id_groups` grouped by non-null `review_id`; both counts must be `0`.
