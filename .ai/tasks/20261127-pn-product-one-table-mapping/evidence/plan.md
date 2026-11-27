# Evidence plan

## Decision to resolve

- U-04: whether one product currently has more than one `business_service_id`.
- U-06: the observed shape of price fields, so the transform rule can be chosen after the result.

## Existing evidence

- `docs/context/mapping_slv_pn_product.md` §9 keeps many relation rows. §10 stores post prices as base64 strings. That file does not count distinct `business_service_id` per product.
- Q-03 in `.ai/tasks/20261127-slv-pn-product-business-mapping/decision.md`: on an earlier probe, 36/36 post price strings were `base64_like`. This task rechecks the current rows.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `product_offer_blocking.py` | Fabric DEV, `lh_vv_silver` | P-1 through P-5 in one cell: id collision, holiday business-service class, destination coverage, variant shape, hotel rate attach | The console has sections P-1, P-2, P-3 coverage, P-3 destination_count, P-4 variant_counts, P-4 variants_without_vi, and P-5. A failed section is an ERROR line and the next section still runs. | `evidence/results/product_offer_blocking.txt` |
| `variant_id_uniqueness.py` | Fabric DEV, `lh_vv_silver` | SQL-001: duplicate live holiday `(product_id, id)` or hotel `(business_service_id, rate_plan_id)` | `anomaly_count` is 0, or the console lists at most 50 anomaly rows. | `evidence/results/variant_id_uniqueness.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
