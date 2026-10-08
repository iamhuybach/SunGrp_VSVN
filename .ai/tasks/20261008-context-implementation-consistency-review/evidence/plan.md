# Evidence plan

## Decision to resolve

Which written contract is the source of truth when `AGENTS.md` or `.cursor/rules/20-data-pipeline.mdc` disagrees with `docs/context/**` and the notebooks or pipeline JSON.

Whether Fabric DEV already has the gold-log columns and an overlapping FL_00 schedule. Those facts are not in the repository.

## Existing evidence

- Repository notebooks under `notebooks/*.ipynb`.
- Pipeline JSON `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json`.
- `docs/context/CTRL_TABLES_CONTEXT.md` (present and detailed; historical counts are labeled through 05/10/2026).
- `docs/context/CHECK_CTRL_SNAPSHOT.py` (read-only script, not executed here).

## Required probes

| Probe | Environment | Question | Pass/fail criterion | Output file |
|---|---|---|---|---|
| `ctrl-column-presence` | Fabric DEV | Do `ctrl_log_run.output_versions_json` and `ctrl_log_table_run.src_versions_json`, `trg_version`, `deactivated_rows`, `qg_json` exist? | Each column is present or explicitly absent | `evidence/results/ctrl-column-presence.md` |
| `fl00-active-sources` | Fabric DEV | Which `src_tbl` rows are `is_active = 1` for `PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00`? | Aggregate counts by `src_tbl` only | `evidence/results/fl00-active-sources.md` |
| `fl00-schedule-overlap` | Fabric DEV | Can a second FL_00 run start while the first notebook is still inside the 12-hour activity timeout? | Schedule or trigger evidence, no row samples | `evidence/results/fl00-schedule-overlap.md` |

## Data-handling limits

- Use Fabric DEV unless explicitly approved otherwise.
- Prefer aggregates; limit samples to 50 rows.
- Do not store personal data, secrets, or production extracts.
