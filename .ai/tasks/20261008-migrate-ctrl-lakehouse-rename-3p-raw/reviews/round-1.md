# Round 1 review — 20261008-migrate-ctrl-lakehouse-rename-3p-raw

## 1. Model and reviewer manifest

Active coordinator model was confirmed as `gpt-5.6-sol` with `high` reasoning. Every custom agent used the same required model and effort. Reviews were independent and read-only; the repository was not modified.

| Reviewer | Model / effort | Result |
|---|---|---|
| `sql-data-reviewer` | `gpt-5.6-sol` / `high` | `FIX_REQUIRED` |
| `spark-runtime-reviewer` | `gpt-5.6-sol` / `high` | `FIX_REQUIRED` |
| `state-correctness-reviewer` | `gpt-5.6-sol` / `high` | `USER_DECISION` |
| `fabric-pipeline-reviewer` | `gpt-5.6-sol` / `high` | `FIX_REQUIRED` |
| `risk-gate` | `gpt-5.6-sol` / `high` | `USER_DECISION` |

Local verification is recorded as PASS in `verification/verify.log`, but it does not cover Fabric import, connection binding, runtime data ordering, cross-plane concurrency, or F16 behavior.

## 2. Gate verdict

**USER_DECISION**

The implementation is not safe to roll out as-is. It contains one unresolved P0 data-ordering risk, six implementation or orchestration P1 blockers, and one runtime-evidence P1 blocker. Two blockers require choices that conflict with or extend the approved architecture: FL_00 handling of the 3P configuration and the deliberate post-cutover gold outage. `USER_DECISION` does not constitute risk acceptance or permission to deploy.

## 3. Deduplicated findings

### GATE-001 — P0 — 3P ordering can permanently skip an event

- Evidence: `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/request.md:28`; `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:275`, `:633`, `:670`, `:703`, `:719`; `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb:2082`, `:2138`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/architecture.md:57`.
- Violated invariant: event selection and persisted CDC state must define a deterministic total order, and the raw watermark must not advance past a valid event that was never applied.
- Failure scenario: event A for a POI at timestamp T is committed and state stores T. A later Delta commit contains event B for the same POI at T with a different or null `event_id`. State comparison omits `event_id`, marks B stale before the target MERGE, and permits the raw watermark to advance. B is then permanently skipped. A FULL replay containing tied/null identifiers can also select an arbitrary payload.
- Fix direction: obtain the evidence and upstream contract specified below. If nonblank identifiers and strictly increasing per-entity timestamps cannot be guaranteed, persist and compare a stable total-order tie-breaker in CDC state, or fail closed and reject ambiguous rows. Test replay across separate Delta commits, not only ties inside one batch.

### GATE-002 — P1 — FL_00 does not converge for the 3P source

- Evidence: `notebooks/NB_CREATE_DDL.ipynb:676`; `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json:1`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/architecture.md:446`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:84`.
- Violated invariant: a source-triggered orchestration branch must run the owner of that source state or exclude the source; it must not repeatedly schedule unrelated work while leaving the triggering watermark unchanged.
- Failure scenario: a new 3P raw commit makes the 3P ForEach item actionable. The true branch launches the partner notebook with fixed partner parameters. Only partner state can advance, so the 3P item remains actionable and starts another unrelated Spark session every 10–15 minutes until an external process advances the 3P watermark.
- Fix direction: preferably filter FL_00 configuration to `partner_raw_data`, or assign 3P rows to the external orchestration identity. Correct source routing is another option only if the user expands scope. Retaining this behavior requires explicit P1 risk acceptance, enforced external-run ordering, and lag monitoring; it cannot yield `PASS`.

### GATE-003 — P1 — Gold becomes intentionally unavailable without user acceptance

- Evidence: `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:510`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:19`, `:126`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/decision.md:22`.
- Violated invariant: a control-plane cutover must preserve required serving flows unless the user explicitly accepts the outage.
- Failure scenario: after the transform library points at `lh_vv_ctrl`, `NB_00` creates flow-lock/log state and raises `ConfigError` because no `RECOMPUTE` edges exist. No gold node runs, stopping silver-to-gold serving until a later task seeds the edges.
- Fix direction: seed repository-owned `RECOMPUTE` edges and prove a successful recomputation before cutover, or obtain the explicit P3 user decision required by the runbook. Accepted outage remains `USER_DECISION`; `PASS` requires removing the P1 outage.

### GATE-004 — P1 — Rollback can create old/new control-plane split brain

- Evidence: `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/architecture.md:143`, `:333`, `:353`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:117`–`:122`.
- Violated invariant: control-plane ownership must be exclusive before enabling readers or writers from another plane.
- Failure scenario: a new-plane extract remains active while rollback redeploys and resumes the old pipeline. Independent locks in `lh_vv_ctrl` and `lh_vv_bronze.ctrl` allow both runs to write the same silver targets. The partner MERGE has no row-order guard, so an older batch can overwrite newer state.
- Fix direction: add a mandatory rollback quiescence barrier covering FL_00, the external 3P runner, manual extracts, and NB_00. Verify no active runs, `RUNNING` rows, or live lock owners in either plane before redeploying. Resume only after confirming all active readers and writers point to the old plane. Release stale locks only with a compare-and-set predicate after confirming the owner is dead.

### GATE-005 — P1 — Pipeline-config seed does not match its complete logical key

- Evidence: `notebooks/NB_CREATE_DDL.ipynb:716`–`:720`, `:754`–`:758`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/architecture.md:59`, `:71`.
- Violated invariant: `ctrl_mng_pipeline_config` grain is `(pl_name, src_schema, src_tbl, trg_schema, trg_tbl)`.
- Failure scenario: if the same source and `trg_tbl` already exists under a different target schema, the anti-join treats it as the intended row and skips the required `lh_vv_silver.dbo` entry. Extract configuration can then be absent or point to the wrong schema.
- Fix direction: add `c.trg_schema = 'lh_vv_silver.dbo'` to both seed anti-joins. Verify exact-key uniqueness and stable row counts after repeated seed execution.

### GATE-006 — P1 — Pipeline manifest contradicts the pipeline dependencies

- Evidence: `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json:1`; `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/manifest.json:1`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/architecture.md:240`.
- Violated invariant: generated pipeline JSON and its dependency manifest must identify the same linked services.
- Failure scenario: pipeline JSON requires `conn_lh_vv_ctrl_by_sqlep`, `lh_vv_ctrl`, and `lh_vv_bronze`, while the manifest still advertises the removed bronze SQL connection and only the bronze lakehouse. Git sync/import may fail or leave the new control dependencies unbound, preventing the pre-check from reading `lh_vv_ctrl`.
- Fix direction: amend the architecture. Bind and re-export the pipeline from Fabric DEV so the pipeline JSON and manifest are generated together; do not hand-edit the generated manifest. Add deterministic dependency-name parity validation and perform an import/binding smoke test.

### GATE-007 — P1 — `NB_CREATE_DDL` contains an invalid nbformat-4.5 cell

- Evidence: `notebooks/NB_CREATE_DDL.ipynb:2`–`:3`, `:621`–`:628`.
- Violated invariant: every cell in an nbformat 4.5 notebook must have a unique stable `id`.
- Failure scenario: the new migration markdown cell has no `id`. A strict Jupyter or Fabric importer can reject the setup notebook, blocking creation and seeding of the new control plane.
- Fix direction: assign a stable unique ID, run strict nbformat validation, extend local verification to detect missing/duplicate cell IDs, and import-smoke the notebook in Fabric DEV.

### GATE-008 — P1 — Required Fabric runtime proof and safe concurrency evidence are absent

- Evidence: `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/task-state.yaml` (`gates.runtime: pending`); `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:52`–`:55`; `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:1004`–`:1007`.
- Violated invariant: runtime-only correctness and F16 capacity assumptions must be proven in Fabric DEV before rollout.
- Failure scenario: a 13-way FULL replay competes with Eventstream, the SQL endpoint, and other workloads, causing throttling, executor loss, timeout, or partial completion. A NULL watermark then forces repeated FULL attempts, amplifying load. Binding, shortcut, seed, replay, and idempotency failures also remain untested locally.
- Fix direction: after code remediation, execute the bounded DEV runbook. Start with a conservative measured concurrency cap and raise it only if evidence supports 13. Complete P1–P3, R-D1–R-D3, R-E1–R-E3, and R-FL1–R-FL4 before enabling the schedule.

## 4. Disagreements and uncertainty

- `SQL-002` initially framed GATE-001 as an in-batch tie problem. The risk gate found a stronger cross-commit failure: persisted CDC state omits `event_id`, so a later equal-timestamp event can be discarded before MERGE. The consolidated severity remains P0 pending evidence.
- `SPARK-003` and `STATE-001` describe the same non-convergent FL_00 behavior and are consolidated as GATE-002.
- `SPARK-004` is consolidated into GATE-008. The risk is not proof that 13-way concurrency will fail, but the selected value has no runtime evidence on shared F16.
- The architecture says not to edit `manifest.json`; the pipeline reviewer and risk gate reject that instruction because the manifest is now factually inconsistent with the pipeline JSON. Resolution should be a Fabric-generated re-export, not a manual edit.
- Filtering FL_00 to partner-only or making gold runnable changes the approved design. Main must obtain the user decision and, where necessary, revise architecture before implementation continues.

## 5. Required evidence probes

### E1 — 3P ordering and identifier probe

Run in Fabric DEV using aggregates only; do not return payloads:

```sql
WITH base AS (
    SELECT
        source_name,
        source_id,
        TRY_CAST(crawled_at AS TIMESTAMP) AS crawled_ts,
        event_id,
        SHA2(CONCAT_WS('\u0001',
            COALESCE(normalized_payload, ''),
            COALESCE(language_code, '')
        ), 256) AS output_signature
    FROM lh_vv_bronze.dbo.brz_3rd_crawler_poi_stream
),
exact_ties AS (
    SELECT source_name, source_id, crawled_ts, event_id
    FROM base
    WHERE crawled_ts IS NOT NULL
    GROUP BY source_name, source_id, crawled_ts, event_id
    HAVING COUNT(DISTINCT output_signature) > 1
),
entity_time_ties AS (
    SELECT source_name, source_id, crawled_ts
    FROM base
    WHERE crawled_ts IS NOT NULL
    GROUP BY source_name, source_id, crawled_ts
    HAVING COUNT(DISTINCT COALESCE(event_id, '<NULL>')) > 1
        OR COUNT(DISTINCT output_signature) > 1
)
SELECT
    SUM(CASE WHEN event_id IS NULL OR TRIM(event_id) = '' THEN 1 ELSE 0 END) AS missing_event_id_rows,
    (SELECT COUNT(*) FROM exact_ties) AS conflicting_exact_ties,
    (SELECT COUNT(*) FROM entity_time_ties) AS conflicting_entity_time_ties
FROM base;
```

Pass criteria: all three values are `0`, and an upstream contract guarantees nonblank identifiers plus strictly increasing `crawled_at` per entity across commits. Otherwise remediate GATE-001. After remediation, replay two separate commits for the same entity and prove deterministic silver/state/watermark results.

### E2 — Pipeline import and binding smoke test

After Fabric re-export, prove exact parity between linked-service parameters in pipeline JSON and `manifest.json`. Import/sync in Fabric DEV, bind `conn_lh_vv_ctrl_by_sqlep`, `lh_vv_ctrl`, and `lh_vv_bronze`, then show that `Get_Config_4Run` and `Lookup_WM` succeed before ForEach starts.

### E3 — F16 bounded concurrency probe

Pause FL_00, NB_00, and other extract runs. Run the 3P dry run with `allow_full_scan=True`, `max_retries=0`, and a conservative concurrency value. Record pinned `src_version_to`, all active-table statuses and durations, executor loss/OOM, HTTP 430 or capacity throttling, and Fabric capacity metrics. Increase toward 13 only while all tables finish `SUCCESS`/`NO_DATA` with zero executor loss, throttling, or transient failure.

### E4 — Full runtime runbook

Complete and record P1–P3, R-D1–R-D3, R-E1–R-E3, and R-FL1–R-FL4. Evidence must include state/watermark monotonicity, lock release, no writes to the archived control plane, rerun idempotency, pipeline binding, and the selected concurrency cap.

## 6. Round-2 closure table

| Finding | Required closure evidence | Round-2 status |
|---|---|---|
| GATE-001 | E1 results, upstream contract or ordering remediation, and separate-commit replay | Open |
| GATE-002 | Approved design decision plus remediation diff and new-commit pipeline trace | Open |
| GATE-003 | Repository-owned edge seed plus successful recomputation, or explicit user risk decision | Open |
| GATE-004 | Runbook/architecture diff with rollback quiescence and lock-owner checks | Open |
| GATE-005 | Seed anti-join diff plus repeated-seed exact-key validation | Open |
| GATE-006 | Revised architecture, Fabric-generated manifest/pipeline pair, parity check, import smoke | Open |
| GATE-007 | Stable cell ID, strict nbformat validation, Fabric import smoke | Open |
| GATE-008 | Completed E3/E4 evidence with measured safe concurrency | Open |

Round 2 must review the remediation diff, close every P0/P1 item, and check for regressions. No rollout or `PASS` is valid before that closure.
