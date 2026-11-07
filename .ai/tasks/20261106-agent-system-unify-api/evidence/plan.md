# Evidence plan

## Decision to resolve

Repository layout, gold → serving contract, role/model split, and new agent components for unifying the POI serving API into this repository (questions a–h in `handoffs/fable-input.md`).

## Existing evidence

- `evidence/agent-system-inventory.md`
- `evidence/api-source-inventory.md`
- `evidence/user-action-inventory.md`

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `probes/user_actions_scan.py` | Local (repo, git, transcripts) | Frequency of templates, commands, stops, failures, rounds, manual steps | Exit 0; counts only, no names/emails/tokens/payloads | `evidence/user-action-inventory.md` |
| `probes/api_schema_diff.py` | Local (repo + read-only API source) | Column/type/PK drift between Flyway V1 and `sql/postgres/gld_srv_serve.pg.sql` | Exit 0; per-table diff printed | `evidence/api-source-inventory.md` §4 |

No Fabric DEV probe is required in this phase.

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
