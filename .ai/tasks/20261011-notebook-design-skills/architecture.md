RESULT: PASS

# Architecture: 20261011-notebook-design-skills (round 2)

Architect model for this run: `claude-opus-5-5` (effort `high`). Main records it in `task-state.yaml` and sets `rounds.architecture: 2`.

This round answers the five P1 skill-content findings in `reviews/round-1.md` (GATE-001 to GATE-005). The skill set, its boundaries, and the copy procedure from round 1 do not change. Both skill bodies are reissued in full at the end of this document. Main replaces both files from these blocks under the user-approved exception dated 2026-10-11, and only then may it record disposition `fixed` for each finding.

## Summary

This task creates two Cursor skills for Main:

| Skill path | Notebook role | Evidence that the rule repeats |
|---|---|---|
| `.cursor/skills/vsvn-extract-notebook/SKILL.md` | `NB_EXTRACT_*_CDC_BRZ_TO_SLV` | Two extract sources: `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb`, `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` |
| `.cursor/skills/vsvn-notebook-library/SKILL.md` | `NB_LIB_*` | Two libraries: `notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb`, `notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb` |

No skill is created for `NB_00_ORCHES_*`, `NB_<UPPER(trg_tbl)>`, `NB_SETUP_*`, or `NB_CREATE_DDL`. Each of those roles has one implementation or none in the repository.

No evidence is missing. Every round-2 change rests on repository code that was re-read for this round. No Fabric DEV probe is needed.

## Round 2: finding resolution

Each finding was checked against the cited code before the text was changed. All five are valid as skill-content defects. In each case the round-1 skill presented a current implementation choice as safe when the code does not support that claim.

| Finding | Verified cause in the repository | Skill change (round 2) |
|---|---|---|
| GATE-001 (`vsvn-extract-notebook` line 49) | Partner `reject_rows`, third-party `doc_reject_rows` and `element_reject_rows` hash `concat_ws('\u0001', coalesce(<field>, ''))`. NULL and `''` hash the same, and the delimiter is not escaped. | New sections "Reject rows". A new source uses `sha2(to_json(struct(...)), 256)` with fixed aliases, timestamps through `unix_micros`, and dates as strings. This is the repository precedent `_hash_expr` in `NB_LIB_TRANSFORM_SLV_GLD`. The existing formula is labelled a known gap. Changing it in an existing notebook is stated as a `ctrl_cdc_reject` migration that needs architecture. |
| GATE-002 (`vsvn-notebook-library` lines 42, 53-54; `vsvn-extract-notebook` line 88) | `IDENT_RE = [A-Za-z][A-Za-z0-9_]*`. The extract library's own doc says a leading `_` is rejected because it is reserved for internal names. Views `_v_...` are never passed to `is_identifier` or `quote_name`. They are built from a literal prefix, parts that passed `is_identifier` (`trg_tbl` in `build_table_specs`), and uuid-derived hex tags. `run_merge` does not check the view name. | The library skill now separates external identifiers from internal temp-view names. It states the construction rule for view names, forbids relaxing `IDENT_RE`, and requires a `_v_[A-Za-z0-9_]+` check in any new helper that receives a view name. It also records that `run_merge` does not check yet. The extract skill explains why its `_v_{exec_id[:8]}_{trg_tbl}` name is safe. |
| GATE-003 (`vsvn-notebook-library` lines 43, 55-56) | `append_rows` runs a blind Delta append inside `with_retry`. Conflict exceptions mean nothing was committed. The markers `Connection reset` and `TooManyRequestsForCapacity`, however, can follow a commit that succeeded. The blind appends are `ctrl_log_table_run` in both libraries and the transform library's `RUNNING` row of `ctrl_log_run`. The extract library writes `ctrl_log_run` by MERGE on `exec_id`. `node_logs` already keeps the latest row per node. | New library section "Retries and blind appends". Retry is safe only for writes that are idempotent on their grain key. Duplicate log rows are labelled an open gap. Blind append is forbidden for any row whose duplicate changes behavior. Readers must reduce a log to one row per grain key. Changing `append_rows` is a library architecture change. The extract skill's commit section repeats the reader rule. |
| GATE-004 (`vsvn-extract-notebook` line 144; `vsvn-notebook-library` line 99) | No test compiles code cells. `vv.py verify` does not check `.ipynb` files, and the pytest tests only `json.loads` notebooks and `exec` two DDL config cells. `run_controlled` takes no lock and writes no control row in `dry_run`. `decide_status` returns `NO_DATA` when every table has no data. | Both skills replace the `json.load` check with a one-line `compile()` of every Python code cell, with `%` line magics blanked and `%%`/non-Python cells skipped. A new or structurally changed extract notebook, and every library change, now needs `classification.runtime_required: true` and a Fabric DEV runbook. For an extract notebook that means a `dry_run` run plus a `NO_DATA` run. For a library it means one non-writing run per caller. |
| GATE-005 (`vsvn-extract-notebook` line 48) | Partner `profile_events` groups by the raw `_src_object_schema` and `_src_object`. Their values are unbounded for UNCONFIGURED and REJECTED rows. Third-party `profile_docs` groups by the raw `source_name` and collects every unknown top-level key. Neither enforces a bound. Rule 10 forbids unbounded `collect()`. | The profile rule now requires an enforced row bound. Group only by `_status`, `_reason`, and config-restricted columns, and map any other raw-derived value to one literal. Watch lists of raw names are sorted by count and passed through `.limit(<=50)` before `collect()`, with a warning when the limit is hit. The profile aggregate itself is never limited, because `watermark_to` needs every group. Both current forms are labelled a known gap. |

P2 count `1` in `reviews/round-1.md` has no ID or content. It cannot be dispositioned from this document. In round 2, Main asks the review runner to return its ID and text, or records it in `decision.md` as unidentified.

## Context and scope

In scope:

- The survey of notebook roles in `docs/context/02_NAMING_CONVENTION.md` §2 against `notebooks/` and `docs/context/`.
- Which skills exist, with the notebook evidence for each repeated rule.
- The complete text of each selected skill, revised for GATE-001 to GATE-005.
- The procedure Main uses to replace the files byte for byte, plus verification and reviewer routing for review round 2.

Survey result by role (unchanged from round 1):

| Role | Notebooks in repository | Repeated implementation | Decision |
|---|---|---|---|
| `NB_LIB_*` | `NB_LIB_EXTRACT_RAWDATA`, `NB_LIB_TRANSFORM_SLV_GLD` | Yes (2) | Skill `vsvn-notebook-library` |
| `NB_EXTRACT_*_CDC_BRZ_TO_SLV` | `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV` | Yes (2 sources) | Skill `vsvn-extract-notebook` |
| `NB_00_ORCHES_*` | `NB_00_ORCHES_SLV_TO_GLD` | No (1) | No skill |
| `NB_<UPPER(trg_tbl)>` | none | No (0) | No skill (the request forbids inventing one) |
| `NB_SETUP_*` | `NB_SETUP_L1_TS_AUDIT` | No (1) | No skill |
| `NB_CREATE_DDL` | `NB_CREATE_DDL` | No (1) | No skill |

## Non-goals

- No change to any notebook, pipeline, ctrl table, test, `.cursor/rules/*.mdc`, `AGENTS.md`, `CLAUDE.md`, the two existing skills, `scripts/agent_runner.py`, or `scripts/vv.py`.
- No fix to the code gaps that the round-1 findings exposed in the existing notebooks: the `event_hash` formula, the unbounded profile `collect()`, duplicate log appends, and the absence of a compile test. The skills label them, and they are listed under "Observed repository discrepancies" for the user to plan.
- No pipeline skill, partner business-rule skill, gold-sync skill, or recompute-node skill.
- The skills do not repeat `.cursor/rules/10-fabric-notebook.mdc` or `.cursor/rules/30-sql.mdc`. They point to those rules and add only the repository-specific procedure.
- The skills do not duplicate `vsvn-task-workflow` or `fabric-runtime-evidence`. They refer to those skills by name.
- No commit, push, or merge.

## Repeated-rule evidence

### `vsvn-extract-notebook`

| Rule in the skill | Partner notebook | Third-party notebook |
|---|---|---|
| Cell order: markdown, `parameters` cell, `%run NB_LIB_EXTRACT_RAWDATA`, constants plus `NB_NAME`, sections A/B/C, Main, Exit, `Vận hành` | cells `df470ac8` … `9e922ec6` | same order, cells through `f33f88d2` |
| Shared parameter names and order | parameter cell `f6c1e91a` | parameter cell `e3eb64e4` |
| `NB_NAME` from `notebookutils.runtime.context` with a literal fallback | constants cell | constants cell |
| `read_raw` only calls `read_incremental` | `read_raw` | `read_raw` |
| Ordered `(condition, reason, detail)` rules folded with `reversed`; `_status` VALID / IGNORED / REJECTED | `classify_events` | `classify_docs` |
| Event columns from lib §13; a NULL order value is rejected as `MISSING_EVENT_ORDER` | `classify_events` + `build_table_events` | `classify_docs` |
| One grouped profile aggregate; `watermark_to` covers every row read | `profile_events` | `profile_docs` |
| Known gap: profile groups by raw-derived values without a bound (GATE-005) | `profile_events` groups by `_src_object_schema`, `_src_object` | `profile_docs` groups by `_doc__source_name`; `unknown_top_keys` collects every key |
| Reject frame with every column listed; `event_hash` stable across rereads | `reject_rows` | `reject_frame`, `doc_reject_rows`, `element_reject_rows` |
| Known gap: `concat_ws('\u0001', coalesce(..., ''))` hash (GATE-001) | `reject_rows` | `doc_reject_rows`, `element_reject_rows` |
| Remediation precedent for the hash: `sha2(to_json(struct(...)), 256)`, timestamps through `unix_micros` | `NB_LIB_TRANSFORM_SLV_GLD` `_hash_expr` (shared precedent) | same |
| `_run_table` step order: ensure, build+persist, one-job stats, cast-null check before MERGE, rejects, early return, latest, MERGE, state | `_run_table` | `_run_table` |
| `process_table` = `process_with_retry` | `process_table` | `process_table` |
| Stale and applicable flags from state | `build_table_events` | `build_table_rows` |
| `resolve_latest` uses `row_number()` over the event-order window | `resolve_latest` | `resolve_latest` |
| One state row per `_entity_key` | `state_rows(spec, latest, ctx)` | `state_rows(spec, doc_state_latest(...), ctx)` |
| MERGE clock checked by `UTC_TS_RE`; `created_at` only on INSERT; `tech_expr` checked against the lib constant; `ON` = key columns only | `build_merge_sql` | `build_merge_sql` |
| `run_merge` with view `_v_{exec_id[:8]}_{trg_tbl}`; `trg_tbl` checked by `is_identifier` in lib `build_table_specs` | `merge_into_target` | `merge_into_target` |
| No `WHEN NOT MATCHED BY SOURCE` in an extract MERGE | `build_merge_sql` | `build_merge_sql` |
| Commit order: `commit_state` → `merge_rejects` → `append_rows(T_LOG_TABLE_RUN)`, always with `ctx.src_tbl` | `commit`, `commit_rejects` | `commit` |
| `build_context` / `run_extract` / `process_run` structure | Main cell | Main cell |
| Exit cell code | `b01a9ea0` | `f33f88d2` (identical code lines) |
| `dry_run`: no lock, no control write (lib `run_controlled`); `decide_status` → `NO_DATA` when every table has no data | Both notebooks call `run_controlled` | same |

Where the two sources differ, the skill labels the behavior as a per-source difference and does not present it as a rule. This covers deletes, the target rerun guard, cast-null handling in `dry_run`, first-error versus collect-all parameter validation, the window partition, and allowed load modes.

### `vsvn-notebook-library`

| Rule in the skill | `NB_LIB_EXTRACT_RAWDATA` | `NB_LIB_TRANSFORM_SLV_GLD` |
|---|---|---|
| Header markdown with `%run` usage and conventions; definitions only; no reads or writes on `%run`; no `spark.conf.set` | cell `a988badc` | cell `026c3072` |
| Numbered `## N.` / `# N.` sections | §1–§14 | §1–§8 |
| `CTRL_SCHEMA` and `T_*` constants; fully qualified names | §1 | §1 |
| `TRANSIENT_MARKERS`, `is_transient`, `with_retry(6, 2.0, jitter)` | §5 | §2 (marked `chép từ lib extract`) |
| `IDENT_RE`, `is_identifier`, `is_fq_name`, `quote_name`; leading `_` rejected on purpose | §1, §4 (doc table: "Không cho bắt đầu bằng `_`…") | §1, §2 |
| Temp views `_v_...` built from a literal prefix, validated parts, and uuid hex tags; never passed to `is_identifier` | `run_merge` callers (`_v_{exec_id[:8]}_{trg_tbl}`) | `merge_target` (`_v_{trg_tbl}_{tag}`), `merge_edge_wm` (`_v_wm_{tag}`), `ensure_lock_row` (`_v_lock_{uuid4().hex[:8]}`) |
| `append_rows` built from the table schema, inside `with_retry` (blind append) | §10 | §2 |
| Idempotent ctrl writes: MERGE on grain key or conditional UPDATE | `write_run_log` (MERGE on `exec_id`), `commit_state`, `merge_rejects`, lock UPDATE | `update_run_log`, `merge_edge_wm`, lock UPDATE |
| Blind log appends that a retry can duplicate (GATE-003) | `ctrl_log_table_run` | `ctrl_log_table_run` (`write_node_log`), `ctrl_log_run` RUNNING row (`write_run_log`) |
| Readers reduce an append-only log by key | n/a | `node_logs` (latest row per node) |
| `utc_now`, `to_bool`, `split_csv`, `short_error`, thread-safe `log` | §2, §3 | §2 |
| `target_ddl` with `optimizeWrite` + `autoCompact` and no `CLUSTER BY`; `ensure_target` creates, raises `ConfigError` on a type mismatch, or adds columns | §10 | §6 |
| MERGE through a uniquely named temp view, dropped in `finally` | `run_merge` | `merge_target`, `merge_edge_wm`, `ensure_lock_row` |
| Collect all config errors, then raise one `ConfigError` before writes | `build_table_specs` | `_validate_orch_params`, `build_dag` |
| SQL values through `spark.sql(..., args=...)` | `load_table_specs`, `load_watermark`, `read_lock` | `load_config_rows`, `read_flow_lock`, `close_stale_runs` |
| Lock: read, conditional UPDATE, re-read, compare `exec_id`; release only with `WHERE lock_exec_id = exec_id`; stale RUNNING rows → `ABANDONED` | `acquire_lock`, `release_lock`, `_abandon_stale_runs` | `acquire_flow_lock`, `release_flow_lock`, `close_stale_runs` |
| Lifecycle: validate → lock → RUNNING log → work → advance state → close log → release lock → raise after closing | `run_controlled` | `orchestrate`, `run_node` |
| Pure functions and separate SQL builders, testable without Fabric | `build_table_specs` | `sql_merge_target`, `sql_merge_edge_wm`, `_validate_orch_params` |
| Non-writing caller modes for a DEV smoke run | extract callers: `dry_run = True`; `NB_SETUP_L1_TS_AUDIT`: `p_apply = "false"` (returns `PLANNED`) | `NB_00_ORCHES_SLV_TO_GLD`: `p_mode = "PLAN"` (no lock, no write) |

## Selected skills: purpose and limits

### `vsvn-extract-notebook`

- **Why it exists:** a new raw source, or a change to either extract, must reuse the same cell structure, library calls, commit order, MERGE conventions, and exit contract. These details live in about 2,000 lines of two notebooks plus the library doc. Grok 4.7 Medium is likely to reimplement lifecycle code, or to copy a per-source shortcut or a known gap as if it were the norm. Examples are partner's unguarded MERGE, the `concat_ws` reject hash, and the unbounded profile collect.
- **What it does not do:** library changes, lock, watermark, or state semantics, pipeline wiring, ctrl DDL or seeds, recompute nodes, business rules, or source facts that need evidence.

### `vsvn-notebook-library`

- **Why it exists:** both libraries share a contract (no side effects on `%run`, numbered sections, Vietnamese docstrings) and a set of duplicated primitives that must stay identical. Both also implement the same lock and run-log lifecycle, which has open findings E7, E8, C1, and now the duplicate-append gap. A change to one copy without the other, or a new lock or log write built from scratch, is a low-probability, high-impact failure across every caller.
- **What it does not do:** source-specific extract cells, recompute node `build` logic, orchestration planning, pipeline JSON, ctrl DDL or seeds. It never authorizes a new lock, watermark, or run-log primitive, and it never authorizes changing `append_rows`. Those stay architecture decisions.

## Rejected candidates

| Candidate | Reason |
|---|---|
| `NB_00_ORCHES_*` thin-wrapper skill | One notebook. The wrapper is four cells, and the logic lives in the library, which the library skill covers. |
| Recompute node skill (`NodeSpec`, `build`, `run_node`) | No `NB_<UPPER(trg_tbl)>` notebook exists. The contract is only described in `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md` §5. |
| `NB_SETUP_*` plan/apply skill | One notebook (`NB_SETUP_L1_TS_AUDIT`). Revisit when a second setup notebook exists. |
| `NB_CREATE_DDL` seed skill | One notebook. Seed idempotency is already in rule 10 and `02_NAMING_CONVENTION.md` §8. |
| `p_` parameter-cell skill | Fully stated in `02_NAMING_CONVENTION.md` §7 and rule 10. |
| Separate exit-contract skill | Only the two extract notebooks share an exit cell. It is part of the extract skill. |
| Separate "notebook check" skill for the compile command | The command applies to both roles and is one line. Splitting it out would add a third trigger for every notebook edit. It is repeated in both skills instead. |

## Alternatives and trade-offs

### Skill set (unchanged)

| Option | Benefit | Cost | Decision |
|---|---|---|---|
| A. One umbrella "Fabric notebook design" skill | One file | Loads extract-only rules into library or orchestrator work. A weak trigger fires on every notebook edit. | Rejected |
| B. One skill per role with a repeated implementation | Precise triggers. Each rule traces to two implementations. Smallest context. | Two files to keep current | **Selected** |
| C. Skills per concern (MERGE, lock, exit, parameters) | Reuse across roles | A lock skill invites new lock code. MERGE and parameter skills mostly repeat rules 10 and 30. | Rejected |
| D. Extend rule 10 | Always loaded | Role detail loads for every notebook. It is an unrequested agent-system change. | Rejected |
| E. Also cover single-notebook roles | Coverage | Violates the "two notebooks or two sources" constraint | Rejected |

### Round-2 remediation choices

| Finding | Options considered | Selected and why |
|---|---|---|
| GATE-001 | (a) New sources use `to_json(struct)` and existing code is labelled a gap. (b) Tell Main to switch the existing notebooks now. (c) Keep `concat_ws` with a NULL marker. | **(a).** It follows the repository precedent `_hash_expr`, and JSON gives field boundaries and NULL distinction. (b) is a `ctrl_cdc_reject` migration: existing rows would stop matching, and rereads would insert duplicate reject history. That needs its own architecture. (c) has no precedent and still lacks escaping. |
| GATE-002 | (a) Separate internal view names from external identifiers, give a construction rule, and require a pattern check in new helpers. (b) Relax `IDENT_RE` to allow a leading `_`. | **(a).** It matches what the code already does. (b) would weaken validation of external column and table names, where `_` is reserved for internal columns. |
| GATE-003 | (a) Label the gap, forbid blind append for behavior-driving rows, and make readers reduce by grain key. (b) Tell Main to make `append_rows` idempotent now. (c) Remove the retry from appends. | **(a).** (b) and (c) change a shared primitive in both libraries, and the lifecycle of every caller. That is forbidden to a skill by I7 and needs architecture with `state-correctness-reviewer` and runtime proof. (c) would also drop table logs on conflict errors, which are safe to retry. |
| GATE-004 | (a) A local compile command plus a Fabric DEV runbook for `%run` and the exit contract. (b) Add a pytest that compiles every notebook. | **(a).** (b) changes `tests/`, which is source code outside this task's scope. It is listed as a follow-up for the user. The skill's command can become that test later. |
| GATE-005 | (a) Closed-domain grouping, capped named watch lists, and a labelled gap. (b) Only scalar counts. | **(a).** It keeps the per-reason and per-object operational detail that both notebooks log, and the bound is enforced in code. (b) loses that detail. |

## Invariants

Task-level:

- **I1:** Exactly two skill paths exist after implementation: `.cursor/skills/vsvn-extract-notebook/SKILL.md` and `.cursor/skills/vsvn-notebook-library/SKILL.md`. No other skill path is created, changed, or deleted.
- **I2:** Each file's bytes equal its block's body bytes in the persisted `architecture.md`. The body is every line after the block's start line and before its `END_SKILL_FILE` line, each line with its own terminator. The persisted `architecture.md` uses CRLF; this was confirmed on the round-1 file, where every line ends in CR. The skill files are therefore CRLF, like the existing skill files.
- **I3:** The directory name equals the frontmatter `name`.
- **I4:** Main does not write skill prose. Any change goes through a new architecture round (user-approved exception, 2026-10-11).

Skill-content invariants, which reviewers check:

- **I5:** Every normative statement must meet one of these conditions:
  - Both notebooks of the role back it.
  - It is explicitly labelled as a per-source difference, a dated documentation mismatch, or a known gap with its finding ID.
  - It is remediation guidance for a labelled gap. Where a repository precedent exists, the guidance uses that precedent and names it.
- **I6:** No skill restates rule 10 or rule 30 text as a second copy.
- **I7:** No skill tells Main to create or change a lock, watermark, run-log, state, or reject primitive, to change `append_rows`, or to change `ctrl_*` semantics without architecture and `CTRL_TABLES_CONTEXT.md`.
- **I8:** No skill contains workspace, lakehouse, or artifact GUIDs, secrets, personal data, or data samples.
- **I9:** On conflict, `AGENTS.md`, the rules, and the current notebook code outrank a skill. Each skill tells Main to stop and report a conflict.
- **I10 (new):** No skill tells Main that a check is sufficient when it does not test the stated property. Examples: JSON parsing does not prove code compiles, and local checks do not prove `%run`, Spark, or exit behavior.

## State ownership, grain, and keys

| Artifact | Owner | Grain / key |
|---|---|---|
| `architecture.md` (this file) | Architect content; persisted by `python scripts/vv.py run-gate` | One per task; overwritten per architecture round |
| `.cursor/skills/<name>/SKILL.md` prose | Architect (task-scoped exception) | One file per skill. Key = `<name>` = frontmatter `name` |
| Writing the skill files to disk | Main, verbatim copy only | Same |
| `verification/skill-diff-round-2.txt` | Main (generated, no prose) | One per review round |
| `task-state.yaml`, `decision.md`, `reviews/` import | Main | One per task |
| Review findings | Codex reviewers (read-only) | `reviews/round-N.md` |
| Commit | User | n/a |

## Ordering and transaction or commit boundaries

1. `run-gate` persists this `architecture.md` with `RESULT: PASS`.
2. Main saves the round-1 skill files outside the repository for the diff (implementation plan step 2).
3. Main replaces both skill files from the persisted blocks in one step. The unit of work is complete only when the byte comparison passes for both.
4. Main writes the round-1 → round-2 diff to `verification/skill-diff-round-2.txt`.
5. Main runs the skills' compile command against all seven notebooks. This is a read-only check that the taught command works on the current repository.
6. Main runs `python scripts/vv.py verify 20261011-notebook-design-skills`.
7. Review round 2 runs through `python scripts/vv.py run-gate 20261011-notebook-design-skills --round 2` at `reviewing`. It receives only GATE-001 to GATE-005 and the remediation diff.
8. Main records `fixed` for each GATE finding that round 2 does not reopen.
9. The user commits.

No Fabric state is written at any step, and there is no cross-system transaction.

## Idempotency, concurrency, retry, and recovery

- **Idempotency:** the copy procedure is deterministic. Rerunning it on the same `architecture.md` writes identical bytes. The comparison and the compile command are read-only.
- **Concurrency:** only Main writes the skill files, so there are no concurrent writers. The runner rejects repository edits during the architecture gate.
- **Retry:** if the copy or the comparison fails, rerun the copy. Do not hand-edit.
- **Recovery after a round-2 P0 or P1 on skill content:** review round 2 is the last review round allowed by `AGENTS.md` §6.8. A remaining P0 or P1 routes to `user_decision`, and the user decides whether a third architecture round is allowed. P2 and P3 findings also need an architecture round to change text, because Main may not edit prose. Otherwise Main records `backlog` or `accepted-risk` in `decision.md`.

## Partial failures

| Failure | Detection | Handling |
|---|---|---|
| Only one file replaced | Comparison reports `DIFF` | Rerun the copy with `--write` |
| A file has different bytes (editor reformatting, LF/CRLF change, trailing newline added) | Comparison `DIFF` | Rerun the copy. Never edit by hand. |
| A block is unterminated or a path is unexpected | Script exits with `block mismatch` | Stop. This is an architecture defect; return it to the architect. |
| An extra skill directory created | `git status --porcelain -- .cursor/skills` | Remove the extra path (I1) |
| Compile command fails on an unchanged notebook | `SyntaxError` naming `<path>#cell<N>`, or a Python traceback from the command itself | Stop. Do not edit the notebook or the skill. Report the path, cell index, and message. Either the repository has a real syntax defect or the taught command is wrong; both route to `user_decision` (architecture round cap). |
| Round-1 files not saved before the overwrite | No diff source | Rebuild them from Git history of `architecture.md` if committed. Otherwise give the reviewers this document's "Round 2: finding resolution" table and the full new files. |
| Later code changes make a skill stale | Each skill ends with a dated "Keep this skill current" section | The later task lists the affected skill in scope. The user decides how it is updated. |

## Observability

- The comparison prints one line per file: `OK` or `DIFF`, the path, and the byte count.
- The compile command prints `compiled 7 notebooks` on success.
- `git status --porcelain -- .cursor/skills` lists exactly the two new directories.
- `verification/skill-diff-round-2.txt` holds the remediation diff for review round 2.
- Review findings land in `reviews/round-2.md`. Dispositions go in `decision.md`.

## Security and data handling

- The skills contain only paths, function names, enum values, commands, and code shapes from the repository. They include no GUIDs, secrets, personal data, or row samples.
- The compile command only parses notebook JSON and compiles source text. It does not execute notebook code.
- The copy procedure reads and writes only files inside the repository, plus a temporary copy of the round-1 skill files under the user's temp directory. Nothing is sent outside the machine.

## Rollout, rollback, and forward recovery

- **Rollout:** Cursor discovers both skills once the files exist. No Fabric deployment.
- **Rollback:** delete `.cursor/skills/vsvn-extract-notebook/` and `.cursor/skills/vsvn-notebook-library/` before commit, or revert the commit after it. Nothing else depends on them.
- **Forward recovery:** a new architecture round with corrected blocks, copied by the same procedure, if the user allows one after `user_decision`.

## Implementation plan (Main)

1. Confirm that `architecture.md` starts with `RESULT: PASS` and that `gates.architecture` is `pass`. Record `models.architect.actual: claude-opus-5-5` and `rounds.architecture: 2`.
2. Save the current (round-1) skill files outside the repository, keeping their bytes. PowerShell example:
   `New-Item -ItemType Directory -Force "$env:TEMP\vsvn-skills-r1" | Out-Null; Copy-Item .cursor/skills/vsvn-extract-notebook/SKILL.md "$env:TEMP\vsvn-skills-r1\extract.md"; Copy-Item .cursor/skills/vsvn-notebook-library/SKILL.md "$env:TEMP\vsvn-skills-r1\library.md"`
3. Run the copy script below with `--write`. It is the same script as round 1: ASCII-only, reads `architecture.md` as bytes, and writes only the two expected paths. Run it from the repository root without saving it in the repository. PowerShell: `$script | python - --write`, where `$script` is a here-string holding the script. Bash: `python - --write <<'EOF'` … `EOF`.
4. Run the same script without `--write`. It must print `OK` for both files and exit 0.
5. Write the remediation diff:
   `git diff --no-index "$env:TEMP\vsvn-skills-r1\extract.md" .cursor/skills/vsvn-extract-notebook/SKILL.md > .ai/tasks/20261011-notebook-design-skills/verification/skill-diff-round-2.txt`
   Then run the same command for `library.md` against `.cursor/skills/vsvn-notebook-library/SKILL.md`, appending with `>>`. Exit code 1 from `git diff --no-index` means differences were found and is expected.
6. Run `git status --porcelain -- .cursor/skills`. Expect exactly the two new directories.
7. Run the compile command from the skills against all seven notebooks:
   `python -c "<command from the skill>" notebooks/NB_LIB_EXTRACT_RAWDATA.ipynb notebooks/NB_LIB_TRANSFORM_SLV_GLD.ipynb notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb notebooks/NB_00_ORCHES_SLV_TO_GLD.ipynb notebooks/NB_SETUP_L1_TS_AUDIT.ipynb notebooks/NB_CREATE_DDL.ipynb`
   Copy the quoted command character for character from the persisted skill file. Expect `compiled 7 notebooks`. `SyntaxWarning` lines are not failures. On any error, follow "Partial failures".
8. Run `python scripts/vv.py verify 20261011-notebook-design-skills` and record the result.
9. Keep `review_plan.required_reviewers` as `spark-runtime-reviewer`, `sql-data-reviewer`, `state-correctness-reviewer`, and `fabric-pipeline-reviewer`. `risk-gate` runs because `risk_level` is `high`. Set `review_plan.round: 2`.
10. Transition to `reviewing` and run `python scripts/vv.py run-gate 20261011-notebook-design-skills --round 2`. The round-2 input is GATE-001 to GATE-005 plus `verification/skill-diff-round-2.txt`. Ask for the ID and text of the unidentified round-1 P2.
11. Update `decision.md`. Record `fixed` for each GATE finding that round 2 does not reopen, citing this round's change. Record any reopened finding as unresolved and route to `user_decision`.
12. In the commit request, list only this task's files and the two skill files. `docs/AGENT_PROMPT_SAMPLES.md` was already modified before this task began, so it is not part of this change unless the user says so.

```python
import pathlib
import sys

ARCH = pathlib.Path(".ai/tasks/20261011-notebook-design-skills/architecture.md")
EXPECTED = {
    ".cursor/skills/vsvn-extract-notebook/SKILL.md",
    ".cursor/skills/vsvn-notebook-library/SKILL.md",
}
START = b"SKILL" + b"_FILE: "
END = b"END_" + b"SKILL_FILE"

blocks, path, body = {}, None, []
for line in ARCH.read_bytes().splitlines(keepends=True):
    text = line.rstrip(b"\r\n")
    if path is None and text.startswith(START):
        path, body = text[len(START):].decode("utf-8"), []
    elif path is not None and text == END:
        blocks[path], path = b"".join(body), None
    elif path is not None:
        body.append(line)
if path is not None or set(blocks) != EXPECTED:
    sys.exit(f"block mismatch: open={path} found={sorted(blocks)}")

write = sys.argv[1:] == ["--write"]
bad = []
for name in sorted(blocks):
    data = blocks[name]
    target = pathlib.Path(name)
    if write:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    ok = target.is_file() and target.read_bytes() == data
    if not ok:
        bad.append(name)
    print(("OK  " if ok else "DIFF") + f" {name} {len(data)} bytes")
sys.exit(1 if bad else 0)
```

## Verification strategy

Deterministic checks (Main):

- The comparison script exits 0 with `OK` for both paths (I1, I2).
- `git status --porcelain -- .cursor/skills` lists only the two new directories (I1).
- Each file starts with `---`, `name: <directory name>`, and a single-line `description:` without `: ` inside the value, then `---` (I3).
- The compile command prints `compiled 7 notebooks` (I10; it proves the taught command runs on the current repository).
- `python scripts/vv.py verify 20261011-notebook-design-skills` passes.

Review round 2 (Codex, read-only). Each reviewer checks the findings in its domain and any regression the diff introduces:

- **`sql-data-reviewer`:** GATE-001. The `to_json(struct)` hash is canonical, NULL and `''` are distinct, the field-alias and order rule holds, and the migration warning is correct. GATE-002: the view-name rule and the unquoted use of `_v_...` names.
- **`spark-runtime-reviewer`:** GATE-005. The row bound is enforced, the profile aggregate is not limited, and the watch-list cap is applied before `collect()`. GATE-004: the compile command handles magics, `%%` cells, and non-Python cells. GATE-002: temp-view uniqueness in a shared session.
- **`state-correctness-reviewer`:** GATE-003. The split between idempotent writes and blind appends is correct, the reader rule holds, and no instruction moves state, reject, watermark, or lock data to append.
- **`fabric-pipeline-reviewer`:** GATE-004. The DEV runbook steps (`dry_run`, `NO_DATA`) exercise the exit contract and failure propagation.
- **`risk-gate`:** any remaining statement that, reused across notebooks, could cause data loss, duplicate rows, a watermark moving past unprocessed data, or an unbounded driver collect.

Every reviewer checks I5–I10.

Runtime proof: not required for this task. No notebook, pipeline, or table changes.

## Observed repository discrepancies (not fixed by this task)

These are reported for the user and are not resolved here. The skills label them so Main does not pick a side silently.

1. **Parameter defaults.** Both extract notebooks set `allow_full_scan = True` and `max_parallel = 12`. `docs/context/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.md` §3 lists `False` and `4`. `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` §4 lists `allow_full_scan` as partner (`False`).
2. **Table log grain.** `.cursor/rules/10-fabric-notebook.mdc` says one `ctrl_log_table_run` row per table attempt. Both extracts append one row per table in scope, carrying the final `attempt_no`. That matches `CTRL_TABLES_CONTEXT.md` §7.
3. **Orchestrator exit.** `NB_00_ORCHES_SLV_TO_GLD` prints the summary and does not call `notebookutils.notebook.exit`.
4. **Third-party doc drift.** `docs/context/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.md` and the notebook's `Vận hành` cell still describe `LANG` / `LANG_ARRAY` modes and a `langs` parameter.
5. **Open finding E7.** `NB_LIB_EXTRACT_RAWDATA` does not range-check `max_retries`.
6. **Partner parameter errors.** Partner `build_context` raises on the first parameter error.
7. **Reject hash (GATE-001).** Both extracts hash rejects with `concat_ws('\u0001', coalesce(..., ''))`. Distinct rejects that differ only by NULL versus `''`, or by a delimiter inside a value, merge into one `ctrl_cdc_reject` row. Fixing this is a reject-table migration.
8. **Unbounded profile collect (GATE-005).** Partner `profile_events` and third-party `profile_docs` (including `unknown_top_keys`) group by raw-derived values without a bound, which rule 10 forbids.
9. **Duplicate log appends (GATE-003).** `append_rows` retries a blind append after errors that may follow a successful commit. This applies to `ctrl_log_table_run` in both libraries and to the transform library's RUNNING `ctrl_log_run` row.
10. **No compile test (GATE-004).** No test compiles notebook code cells, and `vv.py verify` does not check `.ipynb` files. A pytest built on the skills' compile command is a suggested follow-up task.

## Evidence needed

None. Every decision in this round depends only on repository files, which were re-read for the cited functions. The user ruled out Fabric DEV probes for this task on 2026-10-11.

## Skill files

Each block below follows the request's delivery contract. The outer four-backtick fences only help Markdown rendering and are not part of any body.

````text
SKILL_FILE: .cursor/skills/vsvn-extract-notebook/SKILL.md
---
name: vsvn-extract-notebook
description: Create or change an NB_EXTRACT_<SOURCE>_CDC_BRZ_TO_SLV notebook that loads one bronze raw table into silver L1 tables through NB_LIB_EXTRACT_RAWDATA. Use when adding a raw source or editing the parameter, classification, per-table, target MERGE, commit, or exit cells of NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV or NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV. Do not use for NB_LIB_* code, silver-to-gold recompute notebooks, pipeline JSON, or ctrl-table DDL and seeds.
---

# VSVN extract notebook

An extract notebook holds only what is specific to one raw source. `NB_LIB_EXTRACT_RAWDATA` owns the rest: lock, run log, snapshot pinning, read mode, watermark, waves, table retry, and the state and reject MERGE statements.

`.cursor/rules/10-fabric-notebook.mdc` and `.cursor/rules/30-sql.mdc` still apply; this skill does not repeat them. If this skill conflicts with `AGENTS.md`, a rule, or the current notebook code, stop and report the conflict in the task.

## Before editing

1. Read the closer existing notebook in full. Use `notebooks/NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV.ipynb` for change events with deletes. Use `notebooks/NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV.ipynb` for full-document snapshots with derived keys.
2. Read `docs/context/NB_LIB_EXTRACT_RAWDATA.md` (section 4 and the function tables for §11, §13, §14) and the source's context file. Read `docs/context/CTRL_TABLES_CONTEXT.md` before changing anything that writes `ctrl_*`.
3. When a notebook and its context file disagree, report the difference in the task. Do not pick one. Known differences on 2026-10-11:
   - Both notebooks default `allow_full_scan = True` and `max_parallel = 12`. The partner context file lists `False` and `4`. The third-party context file lists `allow_full_scan` as `False`. Take defaults from the task, not from either file.
   - The third-party context file still describes `LANG` / `LANG_ARRAY` modes and a `langs` parameter. The notebook accepts only `EXTRACT_MODES = ("DOC", "DOC_ARRAY")`.
4. If source facts are missing from task evidence (event-order column, key uniqueness, null rates, payload shape), use the `fabric-runtime-evidence` skill. Do not infer them from column names.

## Notebook layout

Keep this cell order. Both notebooks use it.

1. Markdown cell: purpose, caller, reads, writes, parallelism, rerun and concurrency behavior.
2. Parameter cell with the `parameters` tag. Shared names, in this order: `pl_name`, `run_id`, `src_schema`, `src_tbl`, `allow_full_scan`, `max_parallel`, `max_retries`, `table_filter`, `full_reload`, `dry_run`, `stop_on_failure`, `cast_null_policy`, `running_timeout_minutes`. Source-only parameters follow, with plain names and no `p_` prefix. Partner also keeps the unused `overlap_minutes` for old callers; a new source omits it.
3. `%run NB_LIB_EXTRACT_RAWDATA`, alone in its cell.
4. A markdown table of the source constants, then a code cell with the constants and `NB_NAME`:

   ```python
   try:
       NB_NAME = notebookutils.runtime.context.get("currentNotebookName") or "<NOTEBOOK_NAME>"
   except Exception:
       NB_NAME = "<NOTEBOOK_NAME>"
   ```

5. Section A (read and classify), section B (one table), section C (commit), Main, Exit, then a `Vận hành` markdown cell. A markdown table of its functions precedes each code section.

Comments, docstrings, and log text are Vietnamese. Identifiers are English. Mark changes with `[SỬA dd/mm]` or `[THÊM dd/mm]` and the reason.

## Section A: read and classify

- `read_raw` only calls `read_incremental(ctx, <raw columns>, "<order alias>")`. Never filter the raw table by time. Never scan it with `spark.table` for data; reading `.columns` for a schema check is fine.
- Classification is one ordered list of `(condition, reason, detail)` folded with `reversed(rules)`, so the first matching rule wins. It sets `_reason` and `_reject_detail`, and sets `_status`: `VALID` when no rule matched, `IGNORED` when the reason is in `IGNORE_REASONS`, otherwise `REJECTED`.
- A new reason value is an enum change. Add it to `docs/context/02_NAMING_CONVENTION.md` §6 and `docs/context/CTRL_TABLES_CONTEXT.md` §9 in the same task.
- Build the event columns the library reads (lib §13): `_cdc_ts_ms` BIGINT, `_cdc_lsn` BIGINT or NULL, `_raw_ingested_at` TIMESTAMP, `_is_delete` INT, `_op` STRING or NULL, and later `_entity_key` STRING. `event_order()` does not replace a NULL `_cdc_ts_ms`, so classification must reject rows without it (`MISSING_EVENT_ORDER`).
- Set raw payload columns to NULL as soon as no later step reads them. Partner keeps payloads for VALID and REJECTED rows. Third party keeps the payload only for REJECTED rows. Per-table frames keep raw values only on `_key_null` rows.

### Profile

- Profile the read in one grouped aggregate (`groupBy`, then `agg` with a count and the max of the order alias), then `collect()`. `watermark_to` is the maximum over every row read, including IGNORED and REJECTED. Never `limit` this aggregate, because `read_rows` and `watermark_to` need every group.
- A grouped `collect()` needs a row bound that the code enforces. Group only by `_status`, `_reason`, and columns whose values the code has already restricted to the ctrl config. Before grouping, replace any raw-derived value outside that set with one literal such as `"(other)"`. Partner's `objects_cond(configured)` is the test for a configured source object.
- A watch list that must name raw-derived values, such as unknown JSON keys, is sorted by count descending and cut with `.limit(<named constant, at most 50>)` before `collect()`. Log a warning when the limit is reached.
- Known gap on 2026-10-11 (review finding GATE-005, task `20261011-notebook-design-skills`): partner `profile_events` groups by the raw `_src_object_schema` and `_src_object`, which are unbounded for UNCONFIGURED and REJECTED rows. Third-party `profile_docs` groups by the raw `source_name` and collects every unknown top-level key. Do not copy either form into a new source. Changing those functions is a separate task.

### Reject rows

- Reject frames select every `ctrl_cdc_reject` column explicitly. Set `first_run_id = last_run_id = ctx.run_id`, `reject_count = 1`, and `is_resolved = false`.
- `event_hash` is the MERGE key of `ctrl_cdc_reject` (`merge_rejects`). Two different rejects must never share a hash, and the same rejected event or element must get the same hash on every reread. Never put a run id or a processing time in the identity fields.
- A new source computes `F.sha2(F.to_json(F.struct(<identity fields>)), 256)`. Give each field a fixed alias and keep the order fixed; renaming or reordering a field changes every hash. Convert timestamps with `unix_micros` and dates with `cast("string")`, as `_hash_expr` in `NB_LIB_TRANSFORM_SLV_GLD` does. JSON quoting keeps field boundaries, and `to_json` writes a NULL field as absent or `null`, never as `""`.
- Known gap on 2026-10-11 (review finding GATE-001, same task): partner `reject_rows` and third-party `doc_reject_rows` and `element_reject_rows` hash `concat_ws('\u0001', <fields with NULL coalesced to ''>)`. That form gives NULL and `''` the same hash and does not escape the delimiter. Do not copy it. Changing an existing notebook's formula is a migration: rows already in `ctrl_cdc_reject` stop matching, and the next reread inserts new rows instead of raising `reject_count`. That needs architecture.

## Section B: one table

`_run_table(res, <inputs>, state_df, ctx)` runs in a wave thread. It writes only its own target table and fills `res`. Steps, in this order:

1. `ensure_target(spec, ctx.dry_run)`; log the returned note.
2. Build the table frame, `persist(StorageLevel.MEMORY_AND_DISK)` it, and append it to `res.cached`.
3. `table_stats(spec, frame)`: one `agg(...).first()` returning `input_rows`, `rejected_rows`, `stale_rows`, `applicable_rows`, `entity_rows`, `upsert_event_rows`, `delete_event_rows`, and the `_cn__*` and `_unset__*` counts.
4. If any value became NULL during conversion and `ctx.cast_null_policy == "FAIL"`, raise `CastNullError` before any MERGE. Third party only warns in `dry_run`; partner raises. Do not change either without a task decision.
5. Put the `_key_null` rows in `res.reject_df`. Nothing is written yet.
6. Return when `res.applicable_rows == 0` or `ctx.dry_run`.
7. `resolve_latest`, persist into `res.cached`, `merge_into_target`, then set `res.state_df`.

`process_table` is only `process_with_retry(spec, wave, ctx, lambda res: _run_table(...))`. Do not add another retry loop. Do not catch exceptions inside `_run_table`.

Row flags (names fixed by `docs/context/02_NAMING_CONVENTION.md` §5.3):

- `_key_null`: `_parse_failed`, or any key column the table needs is NULL or blank.
- `_entity_key`: set only when not `_key_null`.
- `_is_stale`: a state row exists and `NOT (event_order() > _st_order)`. Join `state_df` filtered to this `trg_schema` and `trg_tbl`, selecting `_st_key` and `_st_order`, with a left join on `_entity_key == _st_key`, then drop both columns. With `full_reload`, `state_df` is `None` and nothing is stale.
- `_applicable`: `NOT _key_null AND NOT _is_stale`.

Latest row and state rows:

- `resolve_latest` keeps one row per target MERGE key, using `row_number()` over a window ordered newest first by the source's event-order contract. Partner orders by `_cdc_ts_ms`, `_cdc_lsn` (nulls last), `_raw_ingested_at`, `_is_delete`. Third party orders by `_cdc_ts_ms`, `_raw_ingested_at`, `_event_id`, then the table's `dedup_order`, then `_pos`.
- New code partitions the window by the real key columns `spec.key_cols`, as third party does. Partitioning by a `|`-joined key string is partner's known issue L4.
- The window order must end with a column the source contract documents as unique per event. If no such column is documented, stop and request evidence.
- `res.state_df` must hold exactly one row per `_entity_key`, because `commit_state` MERGEs it without deduplication. When `_entity_key` is not the target key (third party `state_key = "doc"`), build a separate latest-per-`_entity_key` frame, as `doc_state_latest` does, before calling `state_rows`.

## Target MERGE

`build_merge_sql(spec, target, view, merge_clock)` builds the statement, and `merge_into_target` runs it.

- Compute `merge_clock = utc_ts_text(utc_now())` once per table. Check `UTC_TS_RE.fullmatch(merge_clock)` or raise `ConfigError`. Every audit timestamp in the statement uses `to_utc_timestamp(CAST('<merge_clock>' AS TIMESTAMP), current_timezone())`.
- `ON` compares every column of `spec.key_cols` and nothing else.
- Set `created_at` only in the INSERT branch. Set `updated_at` in every UPDATE and INSERT branch.
- Build `tech_expr` for the technical columns, and raise `ConfigError` unless its keys equal the library constant: `TECH_COLUMNS` for CDC, `SNAPSHOT_TECH_COLUMNS` for snapshot. A source that needs other technical columns is a library change.
- List INSERT columns explicitly: `spec.columns`, then the technical columns.
- Select only the columns the statement reads, then call `run_merge(source, spec.fq_name, lambda target, view: build_merge_sql(...), f"_v_{ctx.exec_id[:8]}_{spec.trg_tbl}")`. Wave threads share one Spark session, so the view name must be unique per run and table.
- The view name is an internal name. It starts with `_`, so it never passes `is_identifier`, and it is never passed to `is_identifier` or `quote_name`. It is safe because every part is controlled: the `_v_` literal, the first 8 hex characters of the uuid4 `exec_id`, and `spec.trg_tbl`, which `build_table_specs` already checked with `is_identifier`. Never add a part taken from a parameter or from raw data.
- Never use `WHEN NOT MATCHED BY SOURCE`. An extract batch holds only the entities that changed, so that clause would delete or soft-delete every other row.
- Deletes differ by source. In partner, a matched row with `_cdc_op = 'd'` gets `deleted = true`, and a delete is never inserted. Third party has no delete branch.
- Rerun guard on the target: the third-party MERGE updates a matched row only when `(_crawled_at, _event_id)` is not older than the target row. The partner MERGE has no guard and relies on state and the lock (known issue C1). A new source states in its architecture which form it uses. Do not copy the unguarded form as a default.

## Section C: commit

`commit(classified, profile, results, ctx)` runs on the main thread after every wave, in this order:

1. `commit_state(results, ctx.src_tbl)`.
2. `merge_rejects(parts, note, ctx.src_tbl)`. `parts` holds the `reject_df` of SUCCESS tables, plus the classification rejects when `profile.rejected_rows > 0`.
3. `append_rows(T_LOG_TABLE_RUN, [table_log_row(r, ctx) for r in results])`.

Always pass `ctx.src_tbl`. `ctrl_cdc_state` and `ctrl_cdc_reject` are partitioned by `src_tbl`, and the partition predicate keeps two sources from conflicting. The library commits state only for SUCCESS tables. If the run stops after any step, the watermark has not moved, so the next run rereads the same raw versions and state drops the events already applied.

The table log has one row per table in scope, with the final `attempt_no`. `.cursor/rules/10-fabric-notebook.mdc` says one row per table attempt. That mismatch is open; do not change either side without a task.

`append_rows` retries a blind append inside `with_retry`. After a `Connection reset` or capacity error the append may already have committed, so the table log can hold a duplicate row for the same `(exec_id, trg_schema, trg_tbl, attempt_no)` (open, review finding GATE-003, task `20261011-notebook-design-skills`). Read the table log per grain key, never count its rows as attempts, and never write state or rejects by append.

Never write `ctrl_mng_watermark` or `ctrl_log_run` from the notebook. `run_controlled` owns both.

## Main

- `build_context()` checks every parameter, adds each problem to an `errors` list, and raises one `ConfigError` before anything is written. This is the third-party form; partner still raises on the first error. It sets `exec_id = str(uuid.uuid4())`, `run_id = str(run_id or "").strip() or exec_id`, and `run_mode` as `DRY_RUN`, else `FULL_RELOAD`, else `INCREMENTAL`. It converts flags with `to_bool` and lists with `split_csv`, and stores `run_params = json.dumps(params, ensure_ascii=False)`.
- `run_extract()` calls, in order: `build_context()`, `assert_utc_format()`, `load_table_specs(ctx, <allowed load modes>)`, the source's `check_config(ctx, specs)` if it has one, `load_watermark(ctx)`, one summary `log` line, then `return run_controlled(ctx, lambda out: process_run(...))`. Allowed modes are `("CDC",)` for partner and `("DOC", "DOC_ARRAY")` for third party. A new source passes its own tuple.
- `process_run(..., out)`:
  - Classify the raw read, persist it, and append it to `out.cached`.
  - Set `out.profile`.
  - Unless `full_reload`, persist `load_state(specs)` and append it to `out.cached`.
  - Call `run_tables(specs, <rows per table>, <worker>, ctx, out.results)`.
  - Set `out.status = decide_status(out.results)`.
  - Call `commit` unless `ctx.dry_run`.
  - Put source-specific exit fields in `out.extra`.
- Every persisted DataFrame goes into `out.cached` or `res.cached`, and the library unpersists them. Do not call `unpersist` in the notebook.
- `RUN_SUMMARY = run_extract()` is the last line of the Main cell.

## Exit cell

Put this code in a separate cell after Main, outside any try/except:

```python
_summary_json = json.dumps(RUN_SUMMARY, ensure_ascii=False, default=str)
print(json.dumps(RUN_SUMMARY, ensure_ascii=False, indent=2, default=str))
if RUN_SUMMARY["status"] in ("FAILED", "PARTIAL_FAILED", "SKIPPED_CONCURRENT"):
    raise RuntimeError(f"{NB_NAME} {RUN_SUMMARY['status']}: {_summary_json}")
notebookutils.notebook.exit(_summary_json)
```

The raise fails the pipeline activity. `SKIPPED_CONCURRENT` raises because an overlapping run is unexpected; its error names the `exec_id` that holds the lock. Keep the `build_summary` keys, and add source fields only through `out.extra`. Wiring the notebook into a pipeline is outside this skill; see `.cursor/rules/20-data-pipeline.mdc`.

## Stop conditions

- The source needs a different lock, watermark, read mode, state, or reject behavior. That is an `NB_LIB_EXTRACT_RAWDATA` change and needs architecture.
- A new `ctrl_*` column, enum value, or table is needed. Update `docs/context/CTRL_TABLES_CONTEXT.md` with evidence first.
- Source facts are not in task evidence. Use `fabric-runtime-evidence`.

## Check before handing off

- Run `python scripts/vv.py verify <task-id>`. Its pytest step reads `NB_LIB_EXTRACT_RAWDATA`, both extract notebooks, and `NB_CREATE_DDL` as JSON and checks the L1 timestamp contract (`tests/test_l1_ts_contract.py`, `tests/test_3p_l1_contract.py`). It does not compile code cells, and it does not cover a new notebook.
- Compile every Python code cell of each notebook you changed. The command blanks `%` line magics such as `%run`, skips `%%` cells and non-Python cells, and does not execute anything. Run it from the repository root, in PowerShell or Bash:

  ```text
  python -c "import json,sys;[compile(''.join('\n' if l.startswith('%') else l for l in ''.join(c['source']).splitlines(True)),p+'#cell'+str(i),'exec') for p in sys.argv[1:] for i,c in enumerate(json.load(open(p,encoding='utf-8'))['cells']) if c['cell_type']=='code' and c.get('metadata',{}).get('microsoft',{}).get('language','python')=='python' and not ''.join(c['source']).startswith('%%')];print('compiled',len(sys.argv)-1,'notebooks')" notebooks/<NOTEBOOK>.ipynb
  ```

  It must print `compiled N notebooks`. A `SyntaxError` names the file and the cell index. `SyntaxWarning` lines are not failures.
- The parameter cell still has the `parameters` tag.
- The notebook has exactly one `%run NB_LIB_EXTRACT_RAWDATA`, no `spark.conf.set`, no `toPandas()`, no `collect()` without an enforced row bound, and no workspace or lakehouse GUID in code.
- Local checks cannot prove `%run`, Spark, or exit behavior. A new extract notebook, or a change to its parameter, `%run`, Main, or Exit cell, needs runtime proof. Set `classification.runtime_required: true` and write `runtime-runbook.md` with these Fabric DEV runs, which the user executes (see `vsvn-task-workflow`):
  1. `dry_run = True`. Expect the `%run` to load, the exit value to be JSON with `run_mode` `DRY_RUN`, and no new Delta version on the target or `ctrl_*` tables. A dry run takes no lock and writes no control row.
  2. A normal run when the raw table has no new version. Expect exit status `NO_DATA`, a `ctrl_log_run` row with the same `exec_id` and status, and a run that finishes without error. Make sure no DEV pipeline run of the same source is active, or the run ends `SKIPPED_CONCURRENT` and raises.

## Keep this skill current

This skill describes the code as of 2026-10-11. A task that changes behavior described here lists this skill in its scope. The skill is agent-system configuration, so the user decides how it is updated.
END_SKILL_FILE
````

````text
SKILL_FILE: .cursor/skills/vsvn-notebook-library/SKILL.md
---
name: vsvn-notebook-library
description: Add or change code in an NB_LIB_* %run library notebook (NB_LIB_EXTRACT_RAWDATA or NB_LIB_TRANSFORM_SLV_GLD) or create a new NB_LIB_* library. Use for shared helpers, retry, identifier quoting, schema-based ctrl appends, target table DDL, temp-view MERGE, parameter validation, and the lock and run-log lifecycle that business notebooks call. Do not use for source-specific extract cells, recompute node build logic, pipeline JSON, or ctrl-table DDL and seeds.
---

# VSVN notebook library

`NB_LIB_*` notebooks are loaded with `%run` and share one Spark session with the caller, so a mistake here reaches every caller at once.

`.cursor/rules/10-fabric-notebook.mdc` and `.cursor/rules/30-sql.mdc` still apply; this skill does not repeat them. If this skill conflicts with `AGENTS.md`, a rule, or the current library code, stop and report the conflict in the task.

## Before editing

1. Read the library's context file: `docs/context/NB_LIB_EXTRACT_RAWDATA.md` or `docs/context/NB_LIB_TRANSFORM_SLV_GLD.md`. Also read `docs/context/02_NAMING_CONVENTION.md` §8. For anything that touches `ctrl_*`, read `docs/context/CTRL_TABLES_CONTEXT.md`.
2. Find the callers by searching for `%run <LIB_NAME>` under `notebooks/`. As of 2026-10-11:
   - `NB_LIB_EXTRACT_RAWDATA` is loaded by `NB_EXTRACT_PARTNER_CDC_BRZ_TO_SLV`, `NB_EXTRACT_3RD_PARTY_CDC_BRZ_TO_SLV`, and `NB_SETUP_L1_TS_AUDIT`. The setup notebook uses `build_table_specs`, `table_has`, `PC_OPTIONAL_COLUMNS`, `TableSpec` and `ColumnSpec` fields, and the UTC helpers.
   - `NB_LIB_TRANSFORM_SLV_GLD` is loaded by `NB_00_ORCHES_SLV_TO_GLD` and, in future, by `NB_<UPPER(trg_tbl)>` node notebooks.
   In the task, record for each caller which library names it uses and whether the change keeps them working.
3. Do not remove or rename a public function, class, constant, or parameter that a caller uses. Add a new name and migrate the callers in the same task.

## Library contract

Both libraries follow these rules. Keep them.

- A library contains only imports, constants, classes, and functions. `%run` must not read or write a table, start a Spark job, or call `spark.conf.set`. Module-level code is limited to imports, constants, compiled regexes, `threading.Lock()`, read-only `spark.conf.get` (as `CAST_FN` does), and pure-Python tables such as `UNACCENT_SRC, UNACCENT_DST = _build_unaccent_map()`.
- A header markdown cell states the `%run` usage (the `%run` goes in its own cell, right after the caller's parameter cell), the conventions, and a numbered section table.
- Each section is a markdown cell `## N. <name>`, followed by a code cell that starts with the `# N. <name>` banner. Put a new function in the matching section. Add a section only at the end, and update both the header table and the context file's section table.
- Table names are always `lakehouse.schema.table`. Control tables use the `CTRL_SCHEMA` constants (`T_WATERMARK`, `T_LOG_RUN`, and so on). Never use the short form `ctrl.<table>`.
- `NB_LIB_EXTRACT_RAWDATA` stays source-agnostic. It has no partner or third-party names; source specifics come in through parameters, `TableSpec`, or ctrl rows.
- A library does not `%run` another library. `NB_LIB_TRANSFORM_SLV_GLD` keeps its own copies of the shared primitives on purpose. Changing that needs architecture.
- Every function has a Vietnamese docstring: a one-line purpose, `Input :`, `Output:`, and `Ví dụ :` with concrete values (`02_NAMING_CONVENTION.md` §8). Change markers are `[SỬA dd/mm]` or `[THÊM dd/mm]`, with the reason.
- Keep logic that needs no Spark in pure functions, and keep SQL text in separate builder functions (for example `build_table_specs`, `_validate_orch_params`, `sql_merge_target`, `sql_merge_edge_wm`), so it can be tested without Fabric.

## Shared primitives

`NB_LIB_TRANSFORM_SLV_GLD` carries copies marked `chép từ lib extract`. Their behavior must stay the same in both libraries:

| Primitive | Behavior to keep |
|---|---|
| `TRANSIENT_MARKERS`, `is_transient(e)` | Matches on class name plus message text, including Java errors that arrive through Py4J |
| `with_retry(fn, label, attempts=6, base_s=2.0)` | Retries transient errors only; waits `base_s * 2 ** (i - 1) + random.uniform(0, 1)`; re-raises the original error on the last attempt or on a non-transient error |
| `IDENT_RE`, `is_identifier`, `is_fq_name`, `quote_name` | `[A-Za-z][A-Za-z0-9_]*` per part, for external names (schema, table, column). A leading `_` is rejected on purpose: that prefix is reserved for internal columns and temp views. `quote_name` quotes only a name that already passed validation |
| `append_rows(table, rows)` | Builds the DataFrame from the table's current schema (missing keys become NULL) and appends inside `with_retry`. A retry can append the same rows twice; see "Retries and blind appends" |
| `utc_now`, `to_bool`, `split_csv`, `short_error` | UTC without tzinfo; `"1"`, `"true"`, `"yes"`, `"y"` are true; CSV items trimmed and empty ones dropped; `"<Type>: <message>"` cut to `limit` |
| `_lock_expired_sql`, lock acquire and release | See "Run lifecycle" |

Change both copies in the same task. Otherwise, record the deviation in `decision.md` before changing code. `log` is thread-safe in both libraries through `_LOG_LOCK`, but the signatures differ: `wave` and `table` in extract, `node` in transform. Keep each library's own signature.

Business notebooks never get a copy. A new library that needs these primitives copies them unchanged and marks the copy with its origin.

## SQL and writes inside a library

- An external name placed into SQL text must pass `is_identifier` or `is_fq_name` and is then wrapped with `quote_name`. Values go through `spark.sql(sql, args={...})`. The only other interpolations in the current code are integers passed through `int(...)`, a `src_tbl` checked by `is_identifier`, a timestamp string checked by `UTC_TS_RE`, and temp view names built by the rule below. A new interpolation needs the same kind of check right before it.
- For a MERGE from a DataFrame: `createOrReplaceTempView(<view>)`, run the statement, then `spark.catalog.dropTempView` in `finally`. Wave threads and node notebooks can share one Spark session, so the view name must be unique per run and target.
- Temp view names are internal names, not external identifiers. Never pass a view name to `is_identifier` or `quote_name`, and never relax `IDENT_RE` to accept a leading `_`. Build every view name only from:
  - a prefix from `02_NAMING_CONVENTION.md` §5.3 (`_v_`, `_v_wm_`) or the existing `_v_lock_`;
  - parts that already passed `is_identifier`, such as `trg_tbl`;
  - a hex tag cut from a uuid4, such as `exec_id[:8]`, `exec_id.replace("-", "")[:12]`, or `uuid.uuid4().hex[:8]`.
  The result matches `_v_[A-Za-z0-9_]+` and is used unquoted. Never build a part from a raw parameter, from config text that skipped `is_identifier`, or from a timestamp.
- A new helper that receives a view name from its caller checks `re.fullmatch(r"_v_[A-Za-z0-9_]+", view)` and raises `ConfigError` otherwise. `run_merge` does not check yet, so its callers must follow the construction rule.
- Wave threads write only their own target table. The main thread writes shared control tables after the wave. The exception is per-node `ctrl_log_table_run` rows, which are blind appends.

## Retries and blind appends

- Wrap each control-table write in `with_retry`. Do not add a third retry layer around `with_retry` or `process_with_retry`.
- A retry is safe only when the write is idempotent on its grain key. That means a MERGE on that key, such as `commit_state` by entity, `merge_rejects` by `event_hash`, the extract library's `write_run_log` by `exec_id`, or `merge_edge_wm` by edge. It also covers a conditional UPDATE, such as lock acquire and release or `update_run_log` by `exec_id`.
- A blind append is not idempotent under retry. Delta conflict errors (`Concurrent*Exception`, `MetadataChangedException`, `ProtocolChangedException`) mean nothing was committed. `Connection reset` and `TooManyRequestsForCapacity`, however, can arrive after the commit succeeded, and the retry then appends the rows again. Current blind appends are `ctrl_log_table_run` in both libraries and the `RUNNING` row of `ctrl_log_run` in `NB_LIB_TRANSFORM_SLV_GLD` (`write_run_log`). A duplicate row with the same grain key is therefore possible (open, review finding GATE-003, task `20261011-notebook-design-skills`, 2026-10-11).
- Until that gap is fixed under architecture:
  - Never use a blind append for state, watermark, reject, or lock data, or for any row whose duplicate changes behavior. Write those with a MERGE on the grain key.
  - Code that reads an append-only log reduces it to one row per grain key (`ctrl_log_table_run`: `exec_id`, `trg_schema`, `trg_tbl`, `attempt_no`), as `node_logs` keeps the latest row per node. It never counts log rows as attempts or runs.
  - Changing `append_rows`, whether to a MERGE on the grain key or to no retry on ambiguous errors, is a change to both library copies and needs architecture.

## Target table DDL

Both libraries create targets the same way. `target_ddl` emits `CREATE TABLE IF NOT EXISTS <quoted name> (...) USING DELTA TBLPROPERTIES ('delta.autoOptimize.optimizeWrite' = 'true', 'delta.autoOptimize.autoCompact' = 'true')`, with no `CLUSTER BY` (Runtime 1.3). `ensure_target`:

- creates the table when it is missing;
- raises `ConfigError` before any write when an existing column has a different type;
- adds missing columns with `ALTER TABLE ... ADD COLUMNS`;
- never drops, renames, or retypes a column.

Technical columns come after business columns and are taken from the library's own `TECH_COLUMNS` (plus `SNAPSHOT_TECH_COLUMNS` in the extract library). The two libraries' `TECH_COLUMNS` are different sets with the same name, so never import one into the other.

## Validation before writes

- Parse and check every parameter and config row first. Collect all messages and raise one `ConfigError` before taking a lock or writing, as `build_table_specs` and `_validate_orch_params` do.
- Range-check numeric parameters, as `_validate_orch_params` does. `NB_LIB_EXTRACT_RAWDATA` does not check `max_retries` yet. A negative value leaves tables `PENDING`, and the run can report `SUCCESS` (open finding E7 in `docs/context/99_PAIN_POINTS.md`). Do not copy that unchecked form.
- `ConfigError` is never retried. `CastNullError` and `QualityGateError` stop the write for that table or node.

## Run lifecycle

`run_controlled` (extract library), and `orchestrate` plus a manual `run_node` (transform library), implement the same lifecycle. Business notebooks call it and never rebuild it. Do not write a new lock, watermark, or run-log primitive. Extend the existing one under architecture, with `state-correctness-reviewer`.

1. Validate parameters and config. Nothing is written.
2. Acquire the lock:
   - Read the lock row. Refuse when it is held and not expired.
   - Otherwise run `UPDATE ... SET lock_exec_id = <exec_id>, lock_at = current_timestamp() WHERE lock_exec_id IS NULL OR <expired>`, then read the row again. Only the run whose `exec_id` is now stored owns the lock.
   - In `run_controlled` and `orchestrate`, a refused run writes one `SKIPPED_CONCURRENT` run-log row and returns.
   - RUNNING run-log rows past the timeout become `ABANDONED`. The extract library does this after acquiring the lock; the transform library does it before.
3. Open the run log as `RUNNING`.
4. Do the work.
5. Advance durable state (the source watermark or the edge watermarks) only for successful outcomes, and only forward. The extract library does this in `finally`, where a failed status writes `FAILED` and keeps the watermark. The transform library does it before `finally`.
6. In `finally`, close the run log, then release the lock with `WHERE lock_exec_id = <exec_id>`, then unpersist the DataFrames the library cached. A failure in one closing step does not skip the next.
7. Raise for a non-success status only after step 6.

Known gaps to keep in mind; do not copy them into new code:

- Lock expiry is `coalesce(lock_at < current_timestamp() - INTERVAL <n> MINUTES, true)` using the caller's timeout, not the holder's (open finding E8). A caller with a shorter timeout can take a lock that is still valid for its holder.
- Neither library checks lock ownership again just before the target MERGE (C1 in extract; `run_node` step 6 in transform). Safety depends on the activity timeout being shorter than the lock timeout.

## Deploy and check

- Deploy the library before any caller that uses the change (`02_NAMING_CONVENTION.md` §8).
- Run `python scripts/vv.py verify <task-id>`. Its pytest step reads `NB_LIB_EXTRACT_RAWDATA` as JSON and checks `utc_ts_text`. No test reads `NB_LIB_TRANSFORM_SLV_GLD`, and no test compiles code cells.
- Compile every Python code cell of the library and of each caller you changed. The command blanks `%` line magics such as `%run`, skips `%%` cells and non-Python cells, and does not execute anything. Run it from the repository root, in PowerShell or Bash:

  ```text
  python -c "import json,sys;[compile(''.join('\n' if l.startswith('%') else l for l in ''.join(c['source']).splitlines(True)),p+'#cell'+str(i),'exec') for p in sys.argv[1:] for i,c in enumerate(json.load(open(p,encoding='utf-8'))['cells']) if c['cell_type']=='code' and c.get('metadata',{}).get('microsoft',{}).get('language','python')=='python' and not ''.join(c['source']).startswith('%%')];print('compiled',len(sys.argv)-1,'notebooks')" notebooks/<LIBRARY>.ipynb
  ```

  It must print `compiled N notebooks`. A `SyntaxError` names the file and the cell index. `SyntaxWarning` lines are not failures.
- Search both libraries for every shared primitive you changed, and confirm the copies still match.
- Local checks cannot prove `%run` behavior. A library change needs runtime proof. Set `classification.runtime_required: true` and list in `runtime-runbook.md` one Fabric DEV run per caller, after the library is deployed, in a mode that writes nothing:
  - `dry_run = True` for each extract notebook;
  - `p_mode = "PLAN"` for `NB_00_ORCHES_SLV_TO_GLD`;
  - `p_apply = "false"` for `NB_SETUP_L1_TS_AUDIT`.
  Each `%run` must load and each notebook must finish with its normal output. A change to the lock, run log, watermark, or MERGE path also needs a run that exercises that path; its architecture names the run. The user executes the runbook (see `vsvn-task-workflow`).
- Runtime behavior (Delta versions, history, MERGE metrics, runMultiple) is proven only by a runtime runbook in Fabric DEV (`docs/context/99_PAIN_POINTS.md` §0, lesson 8).

## Keep this skill current

This skill describes the code as of 2026-10-11. A task that changes behavior described here lists this skill in its scope. The skill is agent-system configuration, so the user decides how it is updated.
END_SKILL_FILE
````
