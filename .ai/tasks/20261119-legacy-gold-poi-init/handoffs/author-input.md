# Author input

## User comments

"Accept risk"

GATE-004 and GATE-005 are accepted-risk. Do not treat them as open defects. Do not change code.

## Read

- `.ai/tasks/20261119-legacy-gold-poi-init/architecture.md` — `## Main brief`, `## Rollout`, `## Rollback and forward recovery`, `## Verification`
- `notebooks/NB_SETUP_LEGACY_GOLD_POI.ipynb` cell `lgpparams` only
- `notebooks/NB_CREATE_DDL.ipynb` cell `legacyidpy` header comments only
- `docs/context/CTRL_TABLES_CONTEXT.md` only if a step names a `ctrl_*` table

## Constraints

- Vietnamese runbook. Old workspace `sgr_visitvn_prd_batch`. New workspace `sgr_visitvn_dev`. Four-part names.
- Order: DDL cell `legacyidpy` first, publish the lib, then `NB_SETUP_LEGACY_GOLD_POI` with `p_mode = PLAN`, user approves, then `p_mode = RUN`, then the same `p_pin_json` again and expect 0 inserts.
- `p_pin_json` default in the notebook is `""`. The runbook must say the operator pastes the PLAN pins into the second and third runs. If a pin value is not in the files, write `<CẦN NGƯỜI DÙNG CUNG CẤP: …>`.
- Include how to rerun and how to roll back the gold tables this init writes: `gld_poi_legacy_id_map`, `gld_srv_poi_info`, `gld_srv_poi_multi_lang`. Do not invent a DELETE of pipeline-owned rows.
- Accepted risk: history parse can hide a committed write; a failed unlock can leave the 30-minute flow lock until the 90-minute lease. The runbook must say how the operator notices those two cases.
- Samples at most 50 rows. No names, addresses, phones, emails, or review text.
- The agent does not run any Fabric step.
