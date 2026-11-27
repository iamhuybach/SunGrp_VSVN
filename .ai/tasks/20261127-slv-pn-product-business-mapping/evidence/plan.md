# Evidence plan

## Decision to resolve

Whether the legacy product JSON paths and the stored form of price, `deleted_at`, `locale`, and `status` exist on silver L1. Column names and declared types are already in `TABLE_CONFIGS` of `notebooks/NB_SETUP_INITIAL_DDL.ipynb`. `TABLE_SPECS` has no `slv_pn_product*` or `slv_pn_hotel*` block.

## Existing evidence

- `problem-analysis.md` `RESULT: EVIDENCE_REQUIRED`, questions 3–7, 10, and 18.
- `01_DATA_MODEL.md` `### 5.1 Partner`: product tables were NO_DATA on the 04/10 rerun. That note is not a current payload shape.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `evidence/probes/product_payload_shape.py` | Fabric DEV, read-only | JSON kind and keys for `metadata`, `attributes`, `raw_sync_data`; class of price and `deleted_at`; distinct `locale` and `status` | Each section prints counts and no values. A silver table with 0 rows has a bronze section for its source table. | `evidence/results/product_payload_shape.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
