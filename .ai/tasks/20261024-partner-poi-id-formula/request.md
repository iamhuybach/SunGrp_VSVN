# Request

## User outcome

Partner `poi_id` is one value per business service. `slv_pn_business_services.id` and `slv_pn_business_service_i18ns.business_service_id` are that same value, so i18n rows and the business service map to each other.

## Scope

### In scope

- Audit every partner `poi_id` expression in `notebooks/`.
- Where an expression already matches the standard, leave the notebook unchanged.
- Record the standard in `AGENTS.md` and `docs/context/01_DATA_MODEL.md` §8, including the notebooks that call it.

### Out of scope

- `notebooks_lgc/`, `docs/templates/`, `docs/requirements/`, and artifacts of other tasks.
- Adding a `poi_id` column to any `slv_pn_*` table.
- Changing `ref_source` value `partner_portal` (source name, not the `poi_id` formula).
- Changing `uuid_md5` while it still concatenates arguments in call order, then applies `md5` and `regexp_replace` to the 8-4-4-4-12 form.
- `NB_GLD_SRV_POI_MULTI_LANG.ipynb` when its expression is already correct (task `20261024-gld-srv-poi-from-mapping`).

## Acceptance criteria

- Each partner `poi_id` expression in `notebooks/` uses that source table's `<id>` and the literal `partner`.
- `AGENTS.md` and `docs/context/01_DATA_MODEL.md` §8 state this standard and name the notebooks that call it.
- `ref_source` = `partner_portal` stays as the source name.
- No `poi_id` column is added to `slv_pn_*`. Extract tables keep source keys.

## Constraints

- Standard: `poi_id = md5(concat(<id>, 'partner'))`, then insert dashes 8-4-4-4-12.
- `<id>` for `slv_pn_business_services` is column `id`. The repository table name is `slv_pn_business_services`.
- `<id>` for `slv_pn_business_service_i18ns` is column `business_service_id`.
- `uuid_md5(<id>, lit('partner'))` in `NB_LIB_TRANSFORM_SLV_GLD` is the standard call. Do not put `partner` first.
- A change to stored `poi_id` values would require a runtime runbook. This task does not change those values.
- Do not run Fabric.

## Classification rationale

- Complexity: `low`. No signal. The running notebook expressions already match the standard, so the edit is the two documentation sentences.
- Risk: `low`. No behavior change.
- Architecture: not required. No grain, key, state owner, commit order, layer move, CDC, watermark, lock, or orchestration change. One viable documentation fix. Two files.
- Evidence: not required. The audit is repository inspection of the named notebooks.
- Runtime proof: not required. Stored `poi_id` values are not rewritten. `partner_portal` keys are not retired by this change.
- Reviewer routing: none. No SQL/Delta MERGE, pipeline, Spark logic, or state-transition change is in the diff.
- Fast lane: `complexity=low`, `risk_level=low`, no behavior change, two changed files (`AGENTS.md`, `docs/context/01_DATA_MODEL.md`).
