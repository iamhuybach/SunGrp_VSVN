# Evidence plan

## Decision to resolve

Architecture §16 and review round 2. Lookup-key duplicates, both live branches non-empty, and the three L2 parents active before the gold edges are enabled.

## Existing evidence

The mapping task closed the column-shape questions. P-7 has not been run. P1–P6 belonged to the withdrawn three-table design.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| P-7 | Fabric DEV, Spark SQL | Lookup duplicates, branch sizes, deleted lookup rows, L2 parent edges | (a) every `n` is 0. (b) both counts are above 0. (d) five active `PL_VV_TRANS_SLV_TO_GLD_30M` rows for the three L2 targets. (c) is information only. | `evidence/results/p7_gld_product_offer_readiness.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
