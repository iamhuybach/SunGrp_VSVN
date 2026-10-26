# Evidence plan

## Decision to resolve

D-MEDIA-SHAPE: the JSON shape of `lh_vv_silver.dbo.slv_pn_business_service_i18ns.media` (`locale = vi`) and `lh_vv_silver.dbo.slv_pn_business_services.media`. Registry type is `string`. The mapping reads `media.url` and `media.order`. The probe must show whether each value is null, blank, a JSON object, a JSON array, or something else, and the Python types of `url` and `order`.

## Existing evidence

- `NB_CREATE_DDL` partner registry: both `media` columns are `type: string`. No element schema.
- `docs/context/01_DATA_MODEL.md` does not define the JSON shape.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| partner_media_shape | Fabric DEV, `lh_vv_silver` | Shape and `url` / `order` types of both `media` columns; count of `vi` rows whose i18n `media` is null or blank while services `media` is present | Aggregates print. A shape is accepted only if the counts show it. Mixed shapes stay unresolved. | `evidence/results/partner_media_shape.txt` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, production extracts, or media URL values.
