# Evidence plan

## Decision to resolve

How `lh_vv_silver.dbo.slv_pn_business_services.address` and `.amentities` are shaped on Fabric DEV, and whether `locale = vi` on `slv_pn_business_service_i18ns` is one row per `business_service_id`.

The registry types both JSON columns as `string`. It does not record object keys or the path to `main_category`. Architecture cannot invent that shape.

## Existing evidence

- `evidence/results/partner-json-shape.txt` (Fabric DEV, 2026-10-19). Address is a JSON object on all 30 services. The sample keys are the only top-level keys. `full_address` is nonempty on 30. `address_line1`, `street`, `ward`, and `city` are nonempty on 23 and empty strings on 7. `address_line2`, `district`, `state`, and `zip` are empty strings on 30. `country` is nonempty on 12.
- Amenity column name is `amentities`. 28 values are JSON null, 1 is null, 1 is an object with no `main_category`. No observed path.
- `slv_pn_business_service_i18ns` locale `vi` is unique per `business_service_id` (121/121, `multi_vi_ids = 0`). 24 of 30 services have a `vi` row.
- Legacy `category_group` is `infer_group` in `notebooks_lgc/pl_transform_partner_userprofile_cms/4. nb_data_enrichment_partner.ipynb` cell 9. It is not a partner-only rule. D3 is still open, so this is evidence, not the decision.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `partner-json-shape.py` | Fabric DEV, Spark notebook on `lh_vv_silver` | Address key census, `main_category` paths, vi join grain | Aggregates only, at most 50 detail rows, no address text, names, or secrets | `evidence/results/partner-json-shape.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
