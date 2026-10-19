# Evidence plan

## Decision to resolve

Whether architecture needs a Fabric DEV group-by of `amenity_raw` before design.

## Existing evidence

Repository census of `SEED_ROWS` in `notebooks/NB_SETUP_POI_AMENITY.ipynb`, recorded in `request.md` §Repository impact.

- 152 seed rows today (74 partner, 78 google).
- 27 rows match the flag form `key = true` or `head.leaf = true`.
- 8 rows match `types[] = ...` and expand to 14 keys (158 rows if nothing is dropped).
- 117 rows stay character-for-character.
- One duplicate key after that census: `google` / `attraction` / `facilities_and_services` / `goodForChildren` on two amenities.
- `types` is `slv_3p_poi.types_json`. It is not a member of `source_flags_json`.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|

None. The design contract is the seed in the repository plus the two form rules in the request. DEV row counts belong to the later rebuild runbook, not to this design gate.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
