# Evidence plan

## Decision to resolve

Exec `c2a9f0ef-6d48-4241-b1fb-c9e25eddd4fe` is PARTIAL_FAILED. Success nodes, the gallery NOT_RUN, and the five advanced edges are classified from the repository and `evidence/results/reinit-gld.txt`. Two gates still need row identity.

## Existing evidence

- `evidence/results/reinit-gld.txt`: node outcomes and the advanced-edge count.
- `evidence/results/reinit-enr-2.txt`: last successful enrich run, exec `50f67abb-1a15-4bba-a456-8fed55925b95`.
- `evidence/results/mlsrcpy.txt`: `source_name` added on `slv_enr_poi_info_multi_lang` before the GLD run.
- `evidence/results/partner_multi_hours.txt`: 8 rows, all `chosen=i18n`, `hours_entity=hours_i18n=2`. Classified data (D-HOURS-8).
- `evidence/results/media_pk_duplicate.txt`: 2 keys, each 3 rows, origin `i18n` only. Classified data (D-MEDIA-PK).

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| partner_multi_hours.py | Fabric DEV, read-only | For each partner entity row with more than one `hours` element on a day: was the chosen amenities block i18n or service, and what is the max element count on each side? | `fail_rows` prints and the table has at most 50 key/count rows. A query error, or any JSON, name, or URL, fails the paste. | evidence/results/partner_multi_hours.txt |
| media_pk_duplicate.py | Fabric DEV, read-only | Which `media_id` values are duplicated, and does each copy come from google, i18n `media`, or services `media`? | `dup_keys` prints and the table has at most 50 key rows. A query error, or any URL, fails the paste. | evidence/results/media_pk_duplicate.txt |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
