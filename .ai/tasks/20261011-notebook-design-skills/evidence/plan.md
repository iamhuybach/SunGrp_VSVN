# Evidence plan

## Decision to resolve

Which notebook-design rules already repeat across at least two notebooks or two extract sources, using only files in this repository.

## Existing evidence

- `notebooks/` and `docs/context/` are the survey sources.
- No Fabric DEV probe is required. The user ruled that out on 2026-10-11.

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
