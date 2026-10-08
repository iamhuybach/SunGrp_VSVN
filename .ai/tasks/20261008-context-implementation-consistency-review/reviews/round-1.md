# UNACCEPTED DRAFT

`python scripts/vv.py run-gate` rejected this file. Codex wrote it during the review, and the immutability check failed. It is not an accepted gate result. Task state remains `reviewing`.

# Round 1 consolidated review

Task: `20261008-context-implementation-consistency-review`

## 1. Model and reviewer manifest

The active coordinator model was confirmed as `gpt-5.6-sol` with `high` reasoning. No model substitution occurred.

| Reviewer | Model / effort | Execution | Verdict |
|---|---|---|---|
| Review Coordinator | `gpt-5.6-sol` / `high` | Active | `USER_DECISION` |
| `spark-runtime-reviewer` | `gpt-5.6-sol` / `high` | Independent, no full-history fork | `FIX_REQUIRED` |
| `fabric-pipeline-reviewer` | `gpt-5.6-sol` / `high` | Independent, no full-history fork | `FIX_REQUIRED` |
| `sql-data-reviewer` | `gpt-5.6-sol` / `high` | Independent, no full-history fork | `FIX_REQUIRED` |
| `state-correctness-reviewer` | `gpt-5.6-sol` / `high` | Independent, no full-history fork | `FIX_REQUIRED` |
| `risk-gate` | `gpt-5.6-sol` / `high` | Run after all specialist results | `USER_DECISION` |

Repository inspection found no tracked implementation diff: `git diff` and `git diff --cached` were empty, while the task directory was untracked. The review therefore assessed the current committed implementation and the proposed audit artifact. Local verification passed its task-state and unit checks, but reported `Files (0): none` and skipped notebook, pipeline, SQL, and JSON validation; it does not establish implementation correctness.

## 2. Gate verdict

`USER_DECISION`

The implementation is not approvable. If judged only as implementation quality, the result is `FIX_REQUIRED`. `USER_DECISION` is required because authoritative contracts conflict and required gold, deployment, and PostgreSQL artifacts are absent. `PASS` is also blocked by one confirmed P0, multiple P1 findings, and missing runtime/data evidence.

## 3. Deduplicated findings

### VSVN-R1-001 — P0 — Expired owners are not fenced from business writes

Evidence: `pipelines/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00/PL_VV_TRANSFORM_BRONZE_TO_SILVER_FL_00.json:1` permits a 12-hour notebook activity while `running_timeout_minutes` is 60; `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` cell 22:222-258 expires and transfers ownership; partner notebook cell 8:127-160 and 205-208 performs an unfenced target MERGE; state is committed later in cell 10:42-46; `NB_LIB_EXTRACT_RAWDATA` cell 22:277-336 fences only the watermark. The analogous transform write path appears in `NB_LIB_TRANSFORM_SLV_GLD.ipynb` cell 11:272-276 and 335-344.

Violated invariant: a run that has lost its lease must be unable to perform any later target, state, edge, or watermark write.

Failure scenario: run A pins raw version 100 and stalls. Its lease expires, run B acquires ownership and commits version 110 to target, CDC state, and watermark. A resumes and its unconditional partner MERGE overwrites target rows with older version-100 values. A cannot rewind state or watermark, leaving target data inconsistent with durable control state; ordinary retries will not repair versions 101-110.

Fix direction: correct the audit's “no P0” conclusion. In a remediation task, introduce a durable fencing generation checked immediately before every target, CDC-state, edge, and watermark commit; align execution deadlines with leases or renew leases; add ordered target-update protection and a forward-recovery procedure that reconstructs Silver and reconciles control state.

Specialist mapping: `STATE-001`, `SPARK-001`, `PIPE-003`, `GATE-001`.

### VSVN-R1-002 — P1 — Crash replay is not a durable no-op

Evidence: partner notebook cell 8:138-160 and 205-208 commits target data before cell 10:42-46 commits `ctrl_cdc_state`; the third-party notebook has the same boundary in cell 8:164-196 and 258-262 followed by cell 10:4-11. Both paths refresh `_ingested_at` during replay.

Violated invariant: replay after any crash point must be a no-op when an event was already applied.

Failure scenario: the target MERGE commits and the process crashes before CDC-state commit. Retry reads old state and reapplies the event, producing another Delta commit and a new technical timestamp. Downstream dirty-edge detection and sync can republish unchanged data.

Fix direction: change audit invariant `INV-26` from `PARTIAL_MATCH/P2` to `MISMATCH/P1`. Make target MERGEs independently replay-safe with durable event-order or content-hash predicates and stable technical timestamps, then failure-test every commit boundary.

Specialist mapping: `STATE-002`, `GATE-002`.

### VSVN-R1-003 — P1 — Third-party state discards the documented event-ID tie-breaker

Evidence: `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` cell 8:115-120, 150-161, and 199-204; `NB_LIB_EXTRACT_RAWDATA.ipynb` cell 26:8-22 and 56-70; `NB_CREATE_DDL.ipynb` cell 19:72-87. Durable state compares `crawled_at` but does not persist `event_id`, although `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md:135-138` defines `(crawled_at, event_id)` ordering.

Violated invariant: snapshot order must be total and all tie-breaker fields must survive in durable state.

Failure scenario: event A at time T is committed. A later event B for the same POI also has time T but a greater `event_id`. State filtering treats B as equal/stale before the MERGE predicate can inspect its ID; the watermark can then advance beyond B.

Fix direction: change `INV-19` from `MATCH` to `MISMATCH`. Define approved null and ordering semantics, persist `event_id` in CDC state, migrate existing state safely, and use it in all state comparisons and deduplication windows.

Specialist mapping: `SQL-001`, `GATE-003`.

### VSVN-R1-004 — P1 — FL_00 does not route sources and always invokes the partner notebook

Evidence: pipeline JSON path `$.resources[0].properties.activities[2].typeProperties.activities[6].typeProperties.ifTrueActivities[1]` contains only `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, with fixed `src_tbl = partner_raw_data`; no Switch exists. This violates `.cursor/rules/20-data-pipeline.mdc:10`. Repository DDL and context describe `poi_raw_event` as another configured source.

Violated invariant: every supported source item must route to its correct notebook, with unsupported sources failing closed.

Failure scenario: an active `poi_raw_event` item with new commits starts the partner notebook; the third-party notebook never runs. Future unsupported sources also fall through to the partner path.

Fix direction: the user must choose whether the pipeline rule or dated context pack is authoritative. If both sources remain supported, implement a Switch on `item().src_tbl`, item-derived mappings, explicit partner and third-party cases, and a default failure branch.

Specialist mapping: `PIPE-001`, `GATE-004`.

### VSVN-R1-005 — P1 — Pre-check can skip forever after raw-table recreation

Evidence: pipeline JSON line 1 builds `v_last_file` only from `last_src_version`; `Filter_NewCommits` accepts filenames greater than it; `If_HasWork` skips when none exist. `Lookup_WM` does not use `last_src_table_id`, and the notebook receives `allow_full_scan = false`. Relevant contracts are in `CTRL_TABLES_CONTEXT.md:168,190-191,223-226`.

Violated invariant: table recreation or version regression must enter an explicit recovery path rather than be classified as `NO_DATA`.

Failure scenario: raw is recreated and its current version is below the stored version. The pre-check finds no greater commit filename, so Spark never starts and notebook-level table-ID detection cannot run. Ingestion remains skipped indefinitely.

Fix direction: make the pre-check generation-aware and distinguish recovery-required from no-data. Add a controlled, audited bootstrap/full-scan path and tests for table recreation and version regression.

Specialist mapping: `PIPE-002`, `GATE-004`.

### VSVN-R1-006 — P1 — Lock and child-status failures do not fail closed

Evidence: `NB_LIB_EXTRACT_RAWDATA.ipynb` cell 22:178-190 and 237-245 deliberately falls back to non-atomic run-log locking when lock columns are absent; cell 22:321-336 and cell 28:119-144 leave the summary successful on ownership loss or release failure. FL_00 has no activity that validates notebook exit JSON. `NB_LIB_TRANSFORM_SLV_GLD.ipynb` cell 13:203-208 calls `close_stale_runs` before acquiring the flow lock and returns `SKIPPED_CONCURRENT` normally; `NB_00_ORCHES_SLV_TO_GLD.ipynb` cell 3 only prints the result.

Violated invariant: ownership must be atomic, stale-run mutation must occur only under ownership, and missing, malformed, skipped, unknown, or failed child outcomes must fail the activity.

Failure scenario: concurrent runs both pass the fallback inspection, or a run loses ownership/cannot release its lock but still returns `SUCCESS`. The pipeline accepts completion because it does not parse a fail-closed payload. NB00 can likewise report activity success although the requested flow did not run.

Fix direction: require lock columns and remove the production fallback; move stale-run mutation behind lock acquisition; make ownership loss and exhausted release failure terminal; emit and parse a stable exit contract with an allowlist of successful statuses.

Specialist mapping: `STATE-003`, `STATE-004`, `PIPE-004`, `SPARK-003`, `GATE-005`.

### VSVN-R1-007 — P1 — Invalid retry parameters can advance the watermark without processing

Evidence: both extract notebooks cast but do not validate `max_retries`; `NB_LIB_EXTRACT_RAWDATA.ipynb` cell 28:12-30 uses `range(1, max_retries + 2)`, and cell 22:419-431 does not reject `PENDING` as a terminally invalid status.

Violated invariant: parameters must be validated before state acquisition, and only explicitly terminal table results may produce run success.

Failure scenario: `max_retries = -1` produces an empty attempt loop. Tables remain `PENDING`, the run is classified successful, and the source watermark advances past raw commits that were never merged.

Fix direction: validate `max_retries >= 0`, `max_parallel >= 1`, and positive timeout domains before acquiring a lock. Treat every status outside a terminal allowlist as failure and add negative-parameter tests.

Specialist mapping: `SPARK-004`, `GATE-006`.

### VSVN-R1-008 — P1 — Clean deployments cannot reproduce the claimed gold runtime

Evidence: `NB_CREATE_DDL.ipynb` cell 19:6-68 omits `output_versions_json`, `src_versions_json`, `trg_version`, `deactivated_rows`, and `qg_json`; `NB_LIB_TRANSFORM_SLV_GLD.ipynb` cell 3:134-138 and cell 13:190 fail fast when they are absent. `NB_SETUP_GOLD_POI_1H`, eight node notebooks, the hourly pipeline, deployment mappings, and PostgreSQL SQL are absent.

Violated invariant: a tracked deployment must create every required schema element and include every executable artifact needed by its runtime contract.

Failure scenario: a new environment created only from repository DDL fails before NB00 planning. If external artifacts exist, their Spark behavior, identifiers, state transitions, and PostgreSQL replay semantics cannot be reviewed.

Fix direction: correct audit finding F-P1-03: missing columns cause fail-fast, not silent edge-watermark freezing. Import an idempotent setup/migration, node notebooks, hourly pipeline, deployment bindings, and PostgreSQL artifacts, or explicitly remove those capabilities from the repository contract by user decision.

Specialist mapping: `SQL-003`, `SPARK-002`, `SPARK-009`, `GATE-007`.

### VSVN-R1-009 — P1 — Key and identifier contracts are unresolved

Evidence: `CTRL_TABLES_CONTEXT.md:301-302` and `NB_CREATE_DDL.ipynb` cell 13:493-520 identify unconfirmed `order_id` keys for hotel/flight items. `AGENTS.md:194` requires a 32-character third-party MD5, while `NB_LIB_EXTRACT_RAWDATA.ipynb` cell 12:79-81 and `NB_CREATE_DDL.ipynb` cell 16:46-47 emit UUID-formatted MD5. Partner `poi_id` and `poi_uid` implementations are absent with the missing node notebooks.

Violated invariant: MERGE keys must preserve source grain, and identifier representation must be consistent across Silver, Gold, and PostgreSQL.

Failure scenario: multiple source items sharing an assumed `order_id` collapse to one target row. Separately, 32-character and UUID-formatted hashes fail equality joins despite identical inputs.

Fix direction: change `INV-18` to `EVIDENCE_REQUIRED` and `INV-04` to `MISMATCH`. Obtain partner key-cardinality evidence, then have the user choose the authoritative third-party and partner identity contracts. Any data-format change requires mapping and forward recovery.

Specialist mapping: `SQL-002`, `SQL-004`, `GATE-008`.

### VSVN-R1-010 — P1 — Deduplication lacks a proven total order

Evidence: partner notebook cell 4:16-19 and cell 8:105-124; third-party notebook cell 8:150-161. Both use `row_number()` without a final stable tie-breaker after their documented order fields.

Violated invariant: selection before MERGE must be deterministic across retries and repartitioning.

Failure scenario: two rows have the same ordering tuple but different payloads. Spark may select different winners on reruns, changing target values for identical input history.

Fix direction: add a stable content hash as the final ordering field or reject conflicting exact ties. Do not mark source uniqueness/determinism as proven until the bounded tie probe passes.

Specialist mapping: `SPARK-006`, `GATE-003`.

### VSVN-R1-011 — P1 — Fabric child cancellation and deployment bindings are unproven

Evidence: `NB_LIB_TRANSFORM_SLV_GLD.ipynb` cell 13:223-235 catches `runMultiple` errors and later releases the flow lock; nodes check ownership only at startup. Pipeline JSON embeds workspace/notebook IDs, while repository deployment metadata does not demonstrate environment remapping.

Violated invariant: the flow lock must remain effective until all child writers are terminal, and promoted IDs must resolve to the intended artifacts.

Failure scenario: the parent times out and releases its lock while a child continues and writes late; a new run then overlaps it. Separately, promotion can retain a DEV GUID or resolve the wrong notebook.

Fix direction: run the bounded cancellation probe and provide per-environment logical-name-to-ID deployment evidence. If children survive, add cooperative fencing before MERGE and retain ownership until all sessions are terminal.

Specialist mapping: `SPARK-007`, `PIPE-006`, `GATE-009`.

### VSVN-R1-012 — P1 — Incremental file discovery has no bounded driver-safety contract

Evidence: `NB_LIB_EXTRACT_RAWDATA.ipynb` cell 20:163-217 and 221-237 collects Delta-log actions for the complete version gap to the driver and expands the resulting file list into one read.

Violated invariant: incremental recovery must have explicit limits for version gaps, actions, files, and bytes on shared F16 capacity.

Failure scenario: a long outage or small-file burst exhausts driver memory or produces an oversized query plan before processing begins.

Fix direction: define hard commit/action/file/byte thresholds and route over-limit gaps to a controlled backfill path. Establish thresholds from the bounded DEV probe.

Specialist mapping: `SPARK-005`.

### VSVN-R1-013 — P2 — Pipeline correlation parameters violate the written rule

Evidence: pipeline JSON line 1 passes `run_id = ""` and a literal `pl_name`; `.cursor/rules/20-data-pipeline.mdc:12` requires `@pipeline().RunId` and `@pipeline().Pipeline`.

Violated invariant: notebook/control logs must retain the originating Fabric pipeline identity.

Failure scenario: control logs cannot be directly correlated to the Fabric run, and a copied pipeline can pre-check one name while loading notebook configuration for another.

Fix direction: after the user selects the authoritative contract, map both values as Fabric expressions. This is P2 rather than P1 absent evidence that correlation loss itself breaks recovery.

Specialist mapping: `PIPE-005`.

### VSVN-R1-014 — P2 — Reject counters are not replay-idempotent

Evidence: `NB_LIB_EXTRACT_RAWDATA.ipynb` cell 26:121-146 increments `reject_count` on every matched replay.

Violated invariant: retrying the same raw occurrence must not multiply durable metrics.

Failure scenario: reject merge commits, then execution crashes before watermark completion. Retry rereads the interval and increments the same rejection again.

Fix direction: deduplicate contributions with a durable raw-occurrence token or suppress increments already attributed to that occurrence.

Specialist mapping: `STATE-005`.

### VSVN-R1-015 — P2 — Control-state reads omit the partition key

Evidence: `NB_CREATE_DDL.ipynb` cell 19:71-89 partitions `ctrl_cdc_state` by `src_tbl`; `NB_LIB_EXTRACT_RAWDATA.ipynb` cell 26:25-46 loads state without filtering `src_tbl` directly.

Violated invariant: reads of partitioned control state should use its partition key.

Failure scenario: each extract scans unrelated source partitions, increasing I/O and shuffle pressure as state grows.

Fix direction: pass `ctx.src_tbl` into `load_state`, filter directly by source and target fields, and confirm partition pruning with `EXPLAIN FORMATTED`.

Specialist mapping: `SPARK-008`.

### VSVN-R1-016 — P2 — Shared-F16 parallelism is not justified

Evidence: `AGENTS.md:187`; partner and third-party parameter cells allow 12 concurrent table operations; NB00 allows concurrent child notebooks. No capacity evidence is recorded.

Violated invariant: concurrency must be justified against the shared F16 workload.

Failure scenario: extracts, orchestration, Eventstream, Copy Job, and SQL endpoint contend, increasing queues, spill, and SLA failures. Severity remains P2 until measurements demonstrate serious performance impact.

Fix direction: capture representative DEV capacity and throttling metrics, set environment-specific caps, and document schedule offsets.

Specialist mapping: `PIPE-007`, `SPARK-010`.

## 4. Disagreements and uncertainty

- The original audit's “None confirmed” P0 conclusion is incorrect. VSVN-R1-001 is statically demonstrable and can leave target data behind durable state without automatic repair.
- Missing gold-log columns cause `require_ctrl_columns()` to fail before planning; the audit's silent-drop/frozen-edge scenario is not the executed path.
- `INV-19 = MATCH` is incorrect because durable third-party state omits `event_id`. `INV-18 = MATCH` is unsupported because partner grain depends on unproven keys.
- The audit understates retry non-idempotency in `INV-26`; the target/state crash window is provable without runtime evidence.
- Empty `run_id` primarily harms correlation and is consolidated as P2, not the audit's P1, unless recovery is shown to rely on Fabric run identity.
- F16 impact is retained as P2 pending measurements; the configured concurrency alone does not prove a serious performance failure.
- Repository evidence proves the design defects but not every current DEV exposure. Live schemas, active rows, schedules, ID bindings, data distributions, and cancellation semantics still require probes.
- `AGENTS.md`, `.cursor/rules/20-data-pipeline.mdc`, dated context, and implementation conflict on routing, IDs, parameter mapping, and hierarchy. Remediation must not choose a source of truth implicitly.

## 5. Required evidence probes

All probes must run read-only in Fabric DEV and return aggregates or metadata without personal data.

1. `ctrl-column-presence`: verify the five gold-log columns and `ctrl_mng_watermark.lock_exec_id` / `lock_at`.
2. `fl00-active-sources`: aggregate active configuration rows by `src_tbl` for FL_00.
3. `fl00-schedule-overlap`: establish scheduled and permitted manual overlap relative to the 60-minute lease and 12-hour activity timeout.
4. `third-party-order-ties`: count null `event_id` values and groups by normalized source key plus `crawled_at` having multiple event IDs or payload hashes.
5. `partner-key-cardinality`: reconstruct latest live CDC candidates and count hotel/flight cases where one configured `order_id` maps to multiple proposed business keys.
6. `dedup-exact-ties`: count ordering tuples with more than one distinct payload hash for each source object.
7. `runmultiple-cancellation`: use an isolated child that waits beyond a short DAG timeout and writes one marker to a disposable Delta table; check whether it writes after the parent has returned, then clean up.
8. `deployment-id-map`: map logical notebook/Lakehouse names to deployed IDs for each environment and confirm pipeline remapping.
9. `incremental-gap-bounds`: report version gap, action count, data-changing add-file count, and bytes per raw table, capped at 10,000 versions with `OVER_LIMIT` output.
10. `f16-coload`: capture queue time, peak CU, executor CPU/memory, spill, throttling, job concurrency, and duration for representative co-load.

## 6. User decisions required

- Choose whether Switch routing and expression-based `run_id`/`pl_name` from the pipeline rule or the dated context behavior is authoritative.
- Choose the canonical third-party identifier representation and whether `poi_uid` remains mandatory.
- Choose the notebook hierarchy standard.
- Decide whether missing gold node notebooks, setup notebook, hourly pipeline, deployment bindings, and PostgreSQL SQL must be imported before this repository can claim those capabilities.

## 7. Round-2 closure table

| Finding | Round-1 status | Required closure evidence |
|---|---|---|
| VSVN-R1-001 | OPEN | Fencing implementation, lease-takeover failure test, and Silver/state recovery procedure |
| VSVN-R1-002 | OPEN | Crash-after-target-commit test proving replay is a no-op |
| VSVN-R1-003 | OPEN | Approved total-order contract, state migration, and same-timestamp tests |
| VSVN-R1-004 | OPEN | User routing decision, corrected routing, and source-case tests |
| VSVN-R1-005 | OPEN | Generation-aware pre-check and raw-recreation regression test |
| VSVN-R1-006 | OPEN | Atomic lock requirement, fail-closed exit handling, and ownership/release tests |
| VSVN-R1-007 | OPEN | Parameter validation and negative-value tests |
| VSVN-R1-008 | OPEN | Corrected audit plus tracked/re-scoped runtime and deployment artifacts |
| VSVN-R1-009 | OPEN | User identity decision and passing grain/identity evidence |
| VSVN-R1-010 | OPEN | Deterministic final tie-breaker and passing conflict probe |
| VSVN-R1-011 | OPEN | Cancellation and deployment-binding evidence; remediation if children survive |
| VSVN-R1-012 | OPEN | Enforced discovery limits and controlled over-limit recovery test |

Round 2 must check both closure and regressions from remediation. It cannot pass while any P0/P1 remains unresolved or required evidence is absent.
