# Round 2 review — 20261008-migrate-ctrl-lakehouse-rename-3p-raw

## 1. Model and reviewer manifest

User-approved exception: Codex `gpt-5.6-sol` high was unavailable because of a usage limit. Round 2 ran in Cursor as `gpt-5.6-sol-medium`. This is not the configured high-effort Codex review. Specialists were read-only and did not see each other's round-2 findings. The risk gate ran after them.

| Reviewer | Model | Result |
|---|---|---|
| `sql-data-reviewer` | `gpt-5.6-sol-medium` | `PASS` |
| `spark-runtime-reviewer` | `gpt-5.6-sol-medium` | `FIX_REQUIRED` |
| `state-correctness-reviewer` | `gpt-5.6-sol-medium` | `FIX_REQUIRED` |
| `fabric-pipeline-reviewer` | `gpt-5.6-sol-medium` | `PASS` |
| `risk-gate` | `gpt-5.6-sol-medium` | `USER_DECISION` |

## 2. Gate verdict

**USER_DECISION**

This is the last allowed review round. `PASS` is not valid. New remediation cannot enter another review round unless the user opens that process exception.

## 3. Deduplicated findings

### GATE-001 — P0 — future 3P event can still be skipped

- Evidence: `evidence/results/e1_3p_ordering.txt`; `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb` CDC state comparison omits `event_id`.
- What is closed: the Fabric DEV snapshot has `missing_event_id_rows = 0`, `conflicting_exact_ties = 0`, and `conflicting_entity_time_ties = 0`. SQL review accepts that snapshot.
- What stays open: persisted CDC order still has no `event_id` tie-breaker, and the repository has no contract that later commits keep `crawled_at` strictly increasing per entity. A later event at the same timestamp can be marked stale while the watermark advances.
- Required resolution: an enforceable upstream contract plus a two-commit replay, or a durable tie-breaker / fail-closed change. That code change is outside the approved architecture.

### GATE-003 — P1 — gold outage accepted, still blocks PASS

- The user accepted the gold outage until a later task seeds `RECOMPUTE` edges.
- Risk gate: accepted P1 risk does not yield `PASS`.

### GATE-006 — P1 — manifest mismatch accepted, still blocks PASS

- `manifest.json` was not hand-edited. It still describes the old bronze connection.
- The user will re-export from Fabric later.
- Risk gate: accepted P1 risk does not yield `PASS`.

### GATE-008 — P1 — runtime proof is absent

- `gates.runtime` is `pending`. Runbook result rows are empty.
- Required resolution: execute the runbook on Fabric DEV, including a measured concurrency cap, before enabling the FL_00 schedule.

### GATE-009 — P1 — 3P concurrency instructions disagree

- Evidence: `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` default `max_parallel = 12`; the first-run note and runbook dry-run say `13`; the runbook real-run sentence does not pass `max_parallel`, so the write uses `12`.
- Failure: a dry-run at 13 does not represent the write, or an operator follows the notebook and runs 13 without F16 evidence.
- Required resolution: pick one cap from the F16 probe and pass that same value on both the dry-run and the write.

## 4. Closed in this round

| Finding | Closure |
|---|---|
| GATE-002 | `Get_Config_4Run` filters `is_active = 1` and `src_tbl = 'partner_raw_data'`. Partner notebook activity is unchanged. No Switch. |
| GATE-004 | Runbook rollback quiesces both control planes before redeploy. |
| GATE-005 | Both seed anti-joins include `trg_schema = 'lh_vv_silver.dbo'`. |
| GATE-007 | Migration cell id `b7e4c1a0-6f28-4d3e-9a15-2c8d0e4f6a91`. Twenty cells, unique ids, empty outputs. Fabric import was not smoked. |

## 5. Disagreements

- SQL review treats GATE-001 as closed by the snapshot. State review and the risk gate keep it open for future commits. The consolidated result follows the risk gate.
- The user had marked GATE-001 `fixed` and GATE-003 / GATE-006 `accepted-risk` before this round. Those decisions remain recorded. They do not produce a `PASS` verdict.

## 6. Conditions required to pass

1. Close GATE-001 with a contract plus replay, or with an ordering change approved as a new architecture.
2. Remove GATE-003 and GATE-006 by seeding gold edges and re-exporting the pipeline, or explicitly accept that this task stops short of `PASS`.
3. Finish GATE-008 on Fabric DEV.
4. Align GATE-009 to one measured `max_parallel`.

## 7. Round-2 closure table

| Finding | Round-2 status |
|---|---|
| GATE-001 | Open |
| GATE-002 | Closed |
| GATE-003 | Accepted risk; blocks PASS |
| GATE-004 | Closed |
| GATE-005 | Closed |
| GATE-006 | Accepted risk; blocks PASS |
| GATE-007 | Closed locally |
| GATE-008 | Open |
| GATE-009 | Open |
