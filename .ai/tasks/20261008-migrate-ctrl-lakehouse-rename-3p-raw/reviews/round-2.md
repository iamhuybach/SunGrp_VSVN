# Round 2 review — 20261008-migrate-ctrl-lakehouse-rename-3p-raw

## 1. Model and reviewer manifest

The coordinator and all project custom agents were confirmed as `gpt-5.6-sol` with `high` reasoning. Reviews were read-only; no repository files were modified.

| Reviewer | Model / effort | Result |
|---|---|---|
| `sql-data-reviewer` | `gpt-5.6-sol` / `high` | `PASS` |
| `spark-runtime-reviewer` | `gpt-5.6-sol` / `high` | `EVIDENCE_REQUIRED` |
| `state-correctness-reviewer` | `gpt-5.6-sol` / `high` | `EVIDENCE_REQUIRED` |
| `fabric-pipeline-reviewer` | `gpt-5.6-sol` / `high` | `FIX_REQUIRED` |
| `risk-gate` | `gpt-5.6-sol` / `high` | `USER_DECISION` |

Local verification is recorded as passing in `verification/verify.log`. It does not prove Fabric import, dependency binding, deployed state transitions, or F16 capacity safety.

## 2. Gate verdict

**USER_DECISION**

This is the final allowed review round. The implementation still has an accepted P1 gold outage, an unresolved P1 pipeline-manifest mismatch, and required Fabric evidence that has not been produced. `PASS` is therefore invalid. Further remediation followed by another review requires an explicit workflow exception from the user; an automatic round 3 is not permitted.

## 3. Deduplicated findings

### GATE-003 — P1 — Gold remains intentionally unavailable

- Evidence: `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/decision.md:16`, `:26`, `:39`, `:42`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:21`, `:134`; `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb:1528`.
- Violated invariant: a control-plane cutover must preserve required serving flows unless the user explicitly accepts the outage.
- Failure scenario: the gold `RECOMPUTE` configuration and flow watermarks are removed, while the new control plane has no replacement edges. `NB_00` now fails before creating a lock or log, which prevents orphan state but also prevents every gold node from running.
- Fix direction: to obtain `PASS`, seed repository-owned `RECOMPUTE` edges and prove a successful, idempotent recomputation. Keeping the explicitly accepted outage remains a `USER_DECISION`, not a technical closure.

### GATE-006 — P1 — Pipeline JSON and dependency manifest disagree

- Evidence: `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json:1`; `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/manifest.json:1`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/decision.md:29`.
- Violated invariant: a generated pipeline and its manifest must declare the same deployable dependencies.
- Failure scenario: the pipeline requires `conn_lh_vv_ctrl_by_sqlep`, `lh_vv_ctrl`, and `lh_vv_bronze`, but the manifest still declares `conn_lh_vv_bronze_by_sqlep` and only `lh_vv_bronze`. Git sync/import can fail or leave the control dependencies unbound, preventing `Get_Config_4Run` or `Lookup_WM` from executing.
- Fix direction: re-export the pipeline and manifest together from Fabric DEV; do not hand-edit the generated manifest. Verify exact dependency parity and complete an import/binding smoke test.

### GATE-007 — P1 — Fabric importability of the setup notebook is unproven

- Evidence: `notebooks/NB_CREATE_DDL.ipynb:621`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/decision.md:30`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/reviews/round-1.md:67`.
- Violated invariant: the notebook that creates the control plane must be demonstrably valid and importable before rollout.
- Failure scenario: local inspection confirms unique cell IDs, empty outputs, and compilable non-magic code, but no strict nbformat validation or Fabric import smoke is recorded. Import rejection would prevent all seven control tables from being created and seeded.
- Fix direction: run strict nbformat validation on every edited notebook, import/open `NB_CREATE_DDL` in Fabric DEV, and persist the results.

### GATE-008 — P1 — Required runtime and state-transition proof is absent

- Evidence: `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/task-state.yaml:80`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:175`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/decision.md:31`; `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:818`; `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb:2375`.
- Violated invariant: a state-owner cutover must prove replay convergence, watermark monotonicity, lock release, archive immutability, and deployment binding before rollout.
- Failure scenario: a process can fail after some target/state commits but before watermark advancement or lock cleanup. The repository logic is designed to recover, but no deployed replay proves that partial writes converge, the watermark never regresses, stale ownership is handled safely, and the archived control plane remains unchanged.
- Fix direction: complete and record P1–P3, B1–B3, R-D1–R-D3, R-E1–R-E3, and R-FL1–R-FL4. Include a two-commit replay for one non-personal test entity and a no-new-commit rerun proving deterministic silver/state results, monotonic watermark, and a released lock.

### GATE-009 — P1 — Concurrency is aligned to 12 but not proven safe on F16

- Evidence: `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb:52`, `:1006`; `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:52`; `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md:52`, `:208`.
- Violated invariant: runtime concurrency on shared F16 must be measured, and operator documentation must agree with the selected cap.
- Failure scenario: executable paths and the runbook now use `max_parallel = 12`, but no capacity evidence supports twelve concurrent target actions. The context document still says default 8 and recommends at least 13. Excess pressure can cause throttling, executor loss, partial completion, and repeated FULL retries.
- Fix direction: run a bounded DEV capacity probe beginning at a conservative value, approve 12 only if evidence is clean, and update the context document to the measured value.

### GATE-010 — P2 — Runbook retains obsolete 3P pipeline recovery guidance

- Evidence: `.ai/tasks/20261008-migrate-ctrl-lakehouse-rename-3p-raw/runtime-runbook.md:173`; pipeline JSON at `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json:1`.
- Violated invariant: operational recovery instructions must match deployed routing.
- Failure scenario: the runbook directs an operator to recover an FL_00 “3P iteration,” although `Get_Config_4Run` now excludes 3P. The operator could investigate the unrelated 3P shortcut instead of the partner-only failure path.
- Fix direction: replace this instruction with partner-only FL_00 recovery and keep 3P shortcut recovery under the external/manual 3P workflow.

## 4. Disagreements and uncertainty

- SQL review closes GATE-001 because `evidence/results/e1_3p_ordering.txt:5`–`:7` contains three zero results and `decision.md:6` records the strictly increasing per-POI `crawled_at` contract. State review still requires deployed replay proof. The consolidated result closes the original ordering premise and includes replay under GATE-008.
- `decision.md` labels GATE-003 fixed, but the remediation fixes orphan lock/log state, not gold availability. The outage is an accepted P1 risk and continues to block `PASS`.
- The architecture says not to edit `manifest.json`; pipeline review correctly identifies the resulting mismatch. Resolution must be a Fabric-generated re-export, not a manual edit.
- GATE-007 is structurally closed by local inspection but remains open for strict validation and Fabric import evidence.
- `task-state.yaml` still lists GATE-001 and GATE-009 using their pre-remediation status. This report reflects the source, recorded decisions, and current evidence rather than treating that stale list as proof.

## 5. Required evidence probes

### E2 — Pipeline artifact parity and binding

Re-export the pipeline and manifest from Fabric DEV. Verify that their dependency names agree and include `conn_lh_vv_ctrl_by_sqlep`, `lh_vv_ctrl`, and `lh_vv_bronze`. Import/sync the pair, bind all dependencies, and prove `Get_Config_4Run` and `Lookup_WM` succeed before `ForEach_Source` starts.

### E3 — Bounded F16 concurrency

With FL_00, NB_00, manual extracts, and the external 3P runner paused, run the 3P dry run using `allow_full_scan=True`, `max_retries=0`, and a conservative concurrency value. Record pinned `src_version_to`, per-table statuses and durations, executor loss/OOM, HTTP 430 or other throttling, and capacity metrics. Increase toward 12 only while the run remains clean.

### E4 — Full runtime cutover and replay

Complete P1–P3, B1–B3, R-D1–R-D3, R-E1–R-E3, and R-FL1–R-FL4. For a non-personal test entity, process two distinct commits with `T2 > T1`, confirm silver/state/watermark advancement, then rerun without a new commit and confirm `NO_DATA`, unchanged state, a monotonic watermark, and a null lock. Prove archived-control row counts remain equal to the baseline.

### E5 — Notebook validation and Fabric import

Run strict nbformat validation for all edited notebooks. Import/open `NB_CREATE_DDL` in Fabric DEV and record that its cells, parameters, attached lakehouse metadata, and execution order are accepted. Do not include payload samples or personal data.

## 6. Round-2 closure table

| Finding | Round-2 status |
|---|---|
| GATE-001 | Closed logically by E1 plus the recorded upstream contract; runtime replay is covered by GATE-008. |
| GATE-002 | Closed statically: FL_00 filters `partner_raw_data`, retains the fixed partner notebook, and adds no Switch. Runtime trace remains under GATE-008. |
| GATE-003 | Accepted P1 risk; blocks `PASS`. |
| GATE-004 | Closed: rollback quiesces both control planes and checks active runs and lock ownership. |
| GATE-005 | Closed: both seed anti-joins include `trg_schema`. |
| GATE-006 | Open — fix required. |
| GATE-007 | Open — evidence required. |
| GATE-008 | Open — evidence required; risk acceptance cannot replace runtime proof. |
| GATE-009 | Executable alignment closed; F16 safety and documentation remain open. |
| GATE-010 | Open P2 documentation regression. |

Exact conditions for a future `PASS`: restore and prove runnable gold configuration; re-export and bind the pipeline artifact pair; complete strict notebook validation/import; complete the full runtime runbook and replay evidence; establish a measured F16 concurrency cap and align all documentation; rerun deterministic verification; and obtain explicit authorization for any review beyond round 2.
